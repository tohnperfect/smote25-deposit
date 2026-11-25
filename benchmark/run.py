#!/usr/bin/env python3
"""WP6 independent benchmark, core tier (SMOTE25 fix plan v4; loader fixes and per-dataset error capture v0.4).

One command runs everything and can be resumed:
    python3 benchmark/run.py --out benchmark/results            # all 110 KEEL two-class sets
    python3 benchmark/run.py --out benchmark/pilot --datasets ecoli1,glass1,pima,yeast3 --repeats 1 \
        --methods none,class_weight,threshold,ROS,SMOTE,ADASYN --learners CART,LR,RF
Every (dataset, repeat, fold, method, learner) result is one JSON line in <out>/<dataset>.jsonl; cells
already present are skipped, so a run can be split across machines by dataset and merged by copying files.

Protocol (plan WP6 steps 2 to 5): stratified 5-fold cross-validation repeated five times with fixed seeds,
the same folds for every method (saved in <out>/folds/), every learned step (scaling, resampling, threshold)
fitted on the training folds only, the authors' default settings for every sampler, identical learner
settings for every sampler. Measures from scores: ROC-AUC, PR-AUC; at the default threshold: G-mean, F1,
MCC, balanced accuracy; calibration: Brier score, expected calibration error (10 equal-width bins),
calibration intercept and slope; resampling time relative to SMOTE is computed in stats.py.
Data: the 110 two-class KEEL sets bundled in the imbalanced-databases package (the sets of the illustrative
runs of v0.1). The 42-task reference collection of the Data section is added with --extra (not yet wired).
"""
import argparse
import json
import time
import traceback
import warnings
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score, brier_score_loss, f1_score,
                             matthews_corrcoef, recall_score, roc_auc_score)
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_predict
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings('ignore')
SEED = 20261110


def learners():
    return {
        'CART': DecisionTreeClassifier(random_state=SEED),
        'kNN': KNeighborsClassifier(n_neighbors=5),
        'LR': LogisticRegression(max_iter=2000),
        'SVM': SVC(kernel='rbf', probability=True, random_state=SEED),
        'RF': RandomForestClassifier(n_estimators=200, random_state=SEED, n_jobs=1),
        'GB': HistGradientBoostingClassifier(random_state=SEED),
    }


def samplers():
    """name -> (factory, source). Factories return a fresh sampler with the authors' defaults."""
    from imblearn.over_sampling import ADASYN, SMOTE, BorderlineSMOTE, RandomOverSampler
    s = {
        'ROS': (lambda: RandomOverSampler(random_state=SEED), 'imbalanced-learn'),
        'SMOTE': (lambda: SMOTE(random_state=SEED), 'imbalanced-learn'),
        'ADASYN': (lambda: ADASYN(random_state=SEED), 'imbalanced-learn'),
        'Borderline-SMOTE': (lambda: BorderlineSMOTE(random_state=SEED), 'imbalanced-learn'),
    }
    try:
        from imblearn_extra.gsmote import GeometricSMOTE
        s['G-SMOTE'] = (lambda: GeometricSMOTE(random_state=SEED), 'imbalanced-learn-extra (Douzas and Bacao)')
    except Exception:  # noqa: BLE001
        pass
    try:
        import logging
        import smote_variants as sv
        logging.getLogger('smote_variants').setLevel(logging.ERROR)
        for name, cls in (('Safe-Level-SMOTE', 'Safe_Level_SMOTE'), ('Cluster-SMOTE', 'cluster_SMOTE'),
                          ('k-means SMOTE', 'kmeans_SMOTE'), ('MWMOTE', 'MWMOTE'), ('SMOTE-IPF', 'SMOTE_IPF'),
                          ('A-SUWO', 'A_SUWO')):
            s[name] = ((lambda c=getattr(sv, cls): SVWrap(c(random_state=SEED))), 'smote-variants 1.0.1')
    except Exception:  # noqa: BLE001
        pass
    return s


NOT_AVAILABLE = ['CGMOS', 'SMOM', 'RSMOTE', 'FW-SMOTE', 'AB-SMOTE']  # no implementation in imbalanced-learn or smote-variants


class SVWrap:
    """Give smote-variants samplers the fit_resample interface."""
    def __init__(self, s):
        self.s = s

    def fit_resample(self, X, y):
        return self.s.sample(X, y)


def calib(y, p):
    eps = 1e-6
    p = np.clip(p, eps, 1 - eps)
    bins = np.minimum((p * 10).astype(int), 9)
    ece = sum(abs(y[bins == b].mean() - p[bins == b].mean()) * (bins == b).mean() for b in range(10) if (bins == b).any())
    logit = np.log(p / (1 - p)).reshape(-1, 1)
    try:
        m = LogisticRegression(C=1e6, max_iter=1000).fit(logit, y)
        slope, intercept = float(m.coef_[0][0]), float(m.intercept_[0])
    except Exception:  # noqa: BLE001
        slope = intercept = float('nan')
    return dict(brier=float(brier_score_loss(y, p)), ece=float(ece), cal_slope=slope, cal_intercept=intercept)


def scores(y, p, thr=0.5):
    yhat = (p >= thr).astype(int)
    tpr = recall_score(y, yhat, zero_division=0)
    tnr = recall_score(1 - y, 1 - yhat, zero_division=0)
    out = dict(roc_auc=float(roc_auc_score(y, p)), pr_auc=float(average_precision_score(y, p)),
               gmean=float(np.sqrt(tpr * tnr)), f1=float(f1_score(y, yhat, zero_division=0)),
               mcc=float(matthews_corrcoef(y, yhat)), bacc=float(balanced_accuracy_score(y, yhat)))
    out.update(calib(y, p))
    return out


def best_threshold(model, X, y):
    """Threshold that maximises G-mean on 3-fold out-of-fold probabilities of the training part."""
    k = min(3, int(min(np.bincount(y))))
    if k < 2:
        return 0.5
    p = cross_val_predict(model, X, y, cv=StratifiedKFold(k, shuffle=True, random_state=SEED), method='predict_proba')[:, 1]
    grid = np.unique(np.quantile(p, np.linspace(0, 1, 101)))
    g = [np.sqrt(((p >= t) & (y == 1)).sum() / max(1, (y == 1).sum()) * ((p < t) & (y == 0)).sum() / max(1, (y == 0).sum())) for t in grid]
    return float(grid[int(np.argmax(g))])


def load(name):
    import imbalanced_databases as imbd
    from imbalanced_databases import _imbalanced_databases as _imb
    from sklearn.preprocessing import OneHotEncoder as _OHE

    # the package passes sparse=..., renamed sparse_output in scikit-learn 1.2
    _imb.OneHotEncoder = lambda sparse=False, **kw: _OHE(sparse_output=sparse, **kw)
    # pandas 3 infers a strict string dtype that breaks the package's encoders (hepatitis, hypothyroid)
    import pandas as _pd
    try:
        _pd.set_option('future.infer_string', False)
    except Exception:  # noqa: BLE001
        pass
    # abalone19.dat declares its class values with a leading space; newer scipy rejects them
    if not getattr(_imb, '_smote25_arff_patch', False):
        import io as _io, pkgutil as _pk, re as _re
        from scipy.io import arff as _arff
        def _read_arff_data(filename, sep=',', usecols=None):
            txt = _pk.get_data('imbalanced_databases', filename).decode('unicode_escape')
            txt = _re.sub(r'\{\s*([^}]*)\}', lambda m: '{' + ','.join(v.strip() for v in m.group(1).split(',')) + '}', txt)
            lines, body = [], False
            for ln in txt.splitlines():
                if body and ln.strip() and not ln.lstrip().startswith('%'):
                    ln = ','.join(v.strip() for v in ln.split(','))
                if ln.strip().lower().startswith('@data'):
                    body = True
                lines.append(ln)
            return _arff.loadarff(_io.StringIO('\n'.join(lines)))
        _imb.read_arff_data = _read_arff_data
        _imb._smote25_arff_patch = True
    d = getattr(imbd, 'load_' + name)()
    X = np.asarray(d['data'], dtype=float)
    y = np.asarray(d['target']).astype(int)
    if (y == 1).sum() > (y == 0).sum():
        y = 1 - y
    return X, y


def run_dataset(name, out, methods, lrn_names, folds, repeats):
    path = out / f'{name}.jsonl'
    done = set()
    if path.exists():
        for line in path.open():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:   # a line cut short when the run was stopped: rerun that cell
                continue
            done.add((r['repeat'], r['fold'], r['method'], r['learner']))
    X, y = load(name)
    cv = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=SEED)
    splits = list(cv.split(X, y))
    (out / 'folds').mkdir(exist_ok=True)
    (out / 'folds' / f'{name}.json').write_text(json.dumps([s[1].tolist() for s in splits]))
    S = samplers()
    L = learners()
    with path.open('a') as fh:
        for i, (tr, te) in enumerate(splits):
            rep, fold = divmod(i, folds)
            sc = StandardScaler().fit(X[tr])
            Xtr, Xte, ytr, yte = sc.transform(X[tr]), sc.transform(X[te]), y[tr], y[te]
            cache = {}
            for m in methods:
                for ln in lrn_names:
                    if (rep, fold, m, ln) in done:
                        continue
                    rec = dict(dataset=name, repeat=rep, fold=fold, method=m, learner=ln, n_train=int(len(tr)),
                               n_min_train=int(ytr.sum()))
                    try:
                        model = clone(L[ln])
                        thr, t0 = 0.5, time.perf_counter()
                        Xs, ys = Xtr, ytr
                        if m == 'class_weight':
                            if 'class_weight' not in model.get_params():
                                rec.update(status='not applicable'); fh.write(json.dumps(rec) + '\n'); continue
                            model.set_params(class_weight='balanced')
                        elif m == 'threshold':
                            thr = best_threshold(clone(L[ln]), Xtr, ytr)
                        elif m != 'none':
                            if m not in cache:
                                t1 = time.perf_counter()
                                cache[m] = (*S[m][0]().fit_resample(Xtr, ytr), time.perf_counter() - t1)
                            Xs, ys, rec['resample_seconds'] = cache[m]
                            rec['n_synthetic'] = int(len(ys) - len(ytr))
                        model.fit(Xs, ys)
                        p = model.predict_proba(Xte)[:, 1]
                        rec.update(scores(yte, p, thr), threshold=thr, status='ok', seconds=time.perf_counter() - t0)
                    except Exception as e:  # noqa: BLE001
                        rec.update(status='error', error=f'{type(e).__name__}: {e}'[:300], trace=traceback.format_exc(limit=1)[-300:])
                    fh.write(json.dumps(rec) + '\n')
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='benchmark/results')
    ap.add_argument('--datasets', default='all')
    ap.add_argument('--methods', default='all')
    ap.add_argument('--learners', default='all')
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--repeats', type=int, default=5)
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    import imbalanced_databases as imbd
    names = sorted(f[5:] for f in dir(imbd) if f.startswith('load_') and f != 'load_all') if a.datasets == 'all' else a.datasets.split(',')
    methods = ['none', 'class_weight', 'threshold'] + list(samplers()) if a.methods == 'all' else a.methods.split(',')
    lrn = list(learners()) if a.learners == 'all' else a.learners.split(',')
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'config.json').write_text(json.dumps(dict(seed=SEED, folds=a.folds, repeats=a.repeats, datasets=names, methods=methods,
                                                     learners=lrn, sampler_sources={k: v[1] for k, v in samplers().items()},
                                                     not_available=NOT_AVAILABLE), indent=1))
    if a.jobs > 1:
        from joblib import Parallel, delayed
        Parallel(n_jobs=a.jobs, verbose=5)(delayed(safe_run)(n, out, methods, lrn, a.folds, a.repeats) for n in names)
    else:
        for n in names:
            safe_run(n, out, methods, lrn, a.folds, a.repeats)
    errs = sorted(p.stem for p in out.glob('*.error'))
    print(f'finished: {len(names)} datasets, {len(errs)} with errors {errs}', flush=True)


def safe_run(n, out, methods, lrn, folds, repeats):
    """One dataset; an exception is written to <out>/<dataset>.error and the run goes on (v0.4)."""
    t = time.perf_counter()
    try:
        run_dataset(n, out, methods, lrn, folds, repeats)
        (out / f'{n}.error').unlink(missing_ok=True)
        print(f'{n}: {time.perf_counter() - t:.1f}s', flush=True)
    except Exception:  # noqa: BLE001
        (out / f'{n}.error').write_text(traceback.format_exc())
        print(f'{n}: ERROR after {time.perf_counter() - t:.1f}s', flush=True)


if __name__ == '__main__':
    main()
