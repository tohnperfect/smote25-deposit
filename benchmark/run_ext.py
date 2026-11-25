#!/usr/bin/env python3
"""WP6 extension tier (v0.4, decision D18 of 10 Nov 2026): high-dimensional sets and nested tuning with an equal budget.
It reuses the protocol, methods, learners and measures of run.py.

  python3 benchmark/run_ext.py highdim --out benchmark/results_highdim --jobs 14
      Same protocol as the core tier (5 x 5 CV, 14 methods, 6 learners) on high-dimensional binary sets from OpenML.
      Selection rule, fixed before the run: every candidate below that loads, is binary, has at least 100 features,
      a minority share of at most 20 percent and at most 20,000 rows, and is not already in the core tier (the
      active OpenML version is used; its id is recorded). The OVA targets share their examples, so one of those that
      pass is drawn at random (seed 20261111). The candidates, the sets used and the reason for every set left out
      are written to <out>/highdim_selection.json.
  python3 benchmark/run_ext.py nested --out benchmark/results_nested --jobs 14
      Nested tuning with an equal budget: for every method and learner, three settings of the learner's main
      hyperparameter (GRID) are compared by 3-fold cross-validation inside the training part of each outer fold,
      with resampling, class weighting or threshold tuning applied inside each inner fold; the setting with the best
      mean PR-AUC (declared in advance) is refitted on the whole training part and scored on the outer test fold.
      Data: 30 of the 110 KEEL sets with at least 30 minority examples, drawn with seed 20261111; 3 x 5 outer CV;
      learners LR, kNN, RF and GB; all 14 methods with their authors' default settings.
Results: one JSON line per cell in <out>/<dataset>.jsonl, resumable as in run.py; benchmark/stats.py reads them.
"""
import argparse
import json
import random
import sys
import time
import traceback
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as R  # noqa: E402

warnings.filterwarnings('ignore')
SEED_EXT = 20261111
HIGHDIM_CANDIDATES = ['hiva_agnostic', 'sylva_agnostic', 'scene', 'Speech', 'musk', 'Internet-Advertisements',
                      'OVA_Endometrium', 'OVA_Prostate', 'OVA_Omentum', 'OVA_Lung', 'OVA_Uterus', 'OVA_Ovary', 'OVA_Colon',
                      'OVA_Kidney', 'OVA_Breast']
IN_CORE_TIER = {'hiva_agnostic': 'hiva', 'sylva_agnostic': 'sylva'}   # same data as core-tier sets: left out
# Attributes that are not features of the example, fixed before the run: musk's molecule name identifies the molecule,
# which carries the label; scene's five other columns are the other labels of the multilabel original.
DROP_COLUMNS = {'musk': ['molecule_name'], 'scene': ['Beach', 'Sunset', 'FallFoliage', 'Field', 'Mountain']}
GRID = {'LR': ('C', [0.1, 1.0, 10.0]), 'kNN': ('n_neighbors', [3, 5, 11]), 'RF': ('min_samples_leaf', [1, 5, 20]),
        'GB': ('learning_rate', [0.03, 0.1, 0.3]), 'SVM': ('C', [0.3, 1.0, 3.0]), 'CART': ('max_depth', [None, 8, 4])}


# ------------------------------------------------------------------ high-dimensional sets from OpenML
def _fetch_openml(name, cache):
    """The active OpenML version of a dataset (row-id and ignore attributes are dropped by scikit-learn).
    The pandas ARFF parser fails on integer-coded nominal values under pandas 3; then the liac-arff parser is used."""
    from sklearn.datasets import fetch_openml
    kw = dict(name=name, version='active', as_frame=True, data_home=str(cache))
    try:
        return fetch_openml(parser='auto', **kw)
    except TypeError:
        return fetch_openml(parser='liac-arff', **kw)


def _load_openml(name, cache, details=None):
    import pandas as pd
    b = _fetch_openml(name, cache)
    if details is not None:
        details.update(openml_id=int(b.details.get('id')), openml_version=int(b.details.get('version')),
                       target=b.details.get('default_target_attribute'))
    X = b.data.drop(columns=[c for c in DROP_COLUMNS.get(name, []) if c in b.data.columns]).copy()
    if details is not None:
        details.update(dropped_columns=[c for c in DROP_COLUMNS.get(name, []) if c in b.data.columns])
    cat = [c for c in X.columns if str(X[c].dtype) in ('category', 'object', 'bool')]
    two = [c for c in cat if X[c].nunique(dropna=True) <= 2]          # binary nominal -> one 0/1 column
    for c in two:
        X[c] = X[c].astype('category').cat.codes.replace(-1, np.nan)
    rest = [c for c in cat if c not in two]
    if rest:
        X = pd.get_dummies(X, columns=rest, dummy_na=False)
    X = X.apply(pd.to_numeric, errors='coerce')
    X = X.fillna(X.median(numeric_only=True)).fillna(0.0).to_numpy(dtype=float)
    yv = b.target.astype(str).to_numpy()
    labels, counts = np.unique(yv, return_counts=True)
    if len(labels) != 2:
        raise ValueError(f'{len(labels)} classes')
    y = (yv == labels[np.argmin(counts)]).astype(int)
    return X, y


_ORIG_LOAD = R.load
CACHE = Path.home() / '.cache' / 'smote25_openml'


def _patched_load(name):
    if name.startswith('oml_'):
        return _load_openml(name[4:], CACHE)
    return _ORIG_LOAD(name)


R.load = _patched_load  # module level, so every joblib worker that imports this file gets it


def select_highdim(out):
    used, left = [], {}
    for n in HIGHDIM_CANDIDATES:
        if n in IN_CORE_TIER:
            left[n] = f'same data as the core-tier set {IN_CORE_TIER[n]}'
            continue
        try:
            info = {}
            X, y = _load_openml(n, CACHE, info)
            n_rows, d, share = len(y), X.shape[1], float(y.mean())
            if d < 100:
                left[n] = f'{d} features'
            elif share > 0.20:
                left[n] = f'minority share {share:.3f}'
            elif n_rows > 20000:
                left[n] = f'{n_rows} rows'
            else:
                used.append(dict(name=n, rows=n_rows, features=d, minority=int(y.sum()), minority_share=round(share, 4), **info))
        except Exception as e:  # noqa: BLE001
            left[n] = f'not loaded: {type(e).__name__}: {str(e)[:120]}'
    # The OVA targets share the same 1,545 examples and form one family in the analysis; each costs about ten core-hours,
    # so one of those that pass the rule is drawn at random (fixed before the run).
    ova = [u for u in used if u['name'].startswith('OVA_')]
    group = None
    if len(ova) > 1:
        keep = random.Random(SEED_EXT).choice(sorted(u['name'] for u in ova))
        for u in ova:
            if u['name'] != keep:
                left[u['name']] = f'OVA target passing the rule, not drawn (one OVA target is used; drawn: {keep})'
        used = [u for u in used if not u['name'].startswith('OVA_') or u['name'] == keep]
        group = dict(passed=sorted(u['name'] for u in ova), drawn=keep, seed=SEED_EXT)
    (out / 'highdim_selection.json').write_text(json.dumps(dict(rule='binary, >= 100 features, minority share <= 0.20, <= 20,000 rows, '
                                                                    'not already in the core tier; active OpenML version; '
                                                                    'one OVA target drawn at random (seed 20261111)',
                                                               candidates=HIGHDIM_CANDIDATES, used=used, left_out=left,
                                                               ova_group=group), indent=1))
    return ['oml_' + u['name'] for u in used]


def _done_cells(path):
    """Cells already written to a results file; a line cut short by a stopped run is skipped (and rerun)."""
    done = set()
    if path.exists():
        for line in path.open():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((r['repeat'], r['fold'], r['method'], r['learner']))
    return done


def run_dataset_rep(name, out, methods, lrn_names, folds, repeats, rep_only):
    """run.run_dataset restricted to one repeat: the same folds and the same cells, so that the repeats of one large
    dataset can run on several workers. Writes <out>/by_repeat/r<rep>/<name>.jsonl; merge() joins them."""
    from sklearn.base import clone
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.preprocessing import StandardScaler
    sub = out / 'by_repeat' / f'r{rep_only}'
    sub.mkdir(parents=True, exist_ok=True)
    path = sub / f'{name}.jsonl'
    done = _done_cells(path)
    X, y = _patched_load(name)   # direct call: a joblib worker does not run this module's top level, so R.load is unpatched there
    splits = list(RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=R.SEED).split(X, y))
    if rep_only == 0:
        (out / 'folds').mkdir(exist_ok=True)
        (out / 'folds' / f'{name}.json').write_text(json.dumps([sp[1].tolist() for sp in splits]))
    S, L = R.samplers(), R.learners()
    with path.open('a') as fh:
        for i, (tr, te) in enumerate(splits):
            rep, fold = divmod(i, folds)
            if rep != rep_only:
                continue
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
                                rec.update(status='not applicable'); fh.write(json.dumps(rec) + '\n'); fh.flush(); continue
                            model.set_params(class_weight='balanced')
                        elif m == 'threshold':
                            thr = R.best_threshold(clone(L[ln]), Xtr, ytr)
                        elif m != 'none':
                            if m not in cache:
                                t1 = time.perf_counter()
                                cache[m] = (*S[m][0]().fit_resample(Xtr, ytr), time.perf_counter() - t1)
                            Xs, ys, rec['resample_seconds'] = cache[m]
                            rec['n_synthetic'] = int(len(ys) - len(ytr))
                        model.fit(Xs, ys)
                        p = model.predict_proba(Xte)[:, 1]
                        rec.update(R.scores(yte, p, thr), threshold=thr, status='ok', seconds=time.perf_counter() - t0)
                    except Exception as e:  # noqa: BLE001
                        rec.update(status='error', error=f'{type(e).__name__}: {e}'[:300], trace=traceback.format_exc(limit=1)[-300:])
                    fh.write(json.dumps(rec) + '\n'); fh.flush()
    return name


def merge(out, names):
    """Join the per-repeat files into <out>/<name>.jsonl (rewritten each time; stats.py reads these)."""
    for n in names:
        rows = []
        for f in sorted((out / 'by_repeat').glob(f'r*/{n}.jsonl')):
            for line in f.open():
                try:
                    json.loads(line)
                except json.JSONDecodeError:
                    continue
                rows.append(line if line.endswith('\n') else line + '\n')
        (out / f'{n}.jsonl').write_text(''.join(rows))


def safe_rep(n, out, methods, lrn, folds, reps, r):
    t = time.perf_counter()
    err = out / f'{n}.r{r}.error'
    try:
        run_dataset_rep(n, out, methods, lrn, folds, reps, r)
        err.unlink(missing_ok=True)
        print(f'{n} repeat {r}: {time.perf_counter() - t:.1f}s', flush=True)
    except Exception:  # noqa: BLE001
        err.write_text(traceback.format_exc())
        print(f'{n} repeat {r}: ERROR', flush=True)


# ------------------------------------------------------------------ nested tuning with an equal budget
def _apply(m, model, Xtr, ytr, S, L, ln):
    """Return the fitted model and threshold for method m on (Xtr, ytr)."""
    from sklearn.base import clone
    thr, Xs, ys = 0.5, Xtr, ytr
    if m == 'class_weight':
        if 'class_weight' not in model.get_params():
            return None, None
        model.set_params(class_weight='balanced')
    elif m == 'threshold':
        thr = R.best_threshold(clone(model), Xtr, ytr)
    elif m != 'none':
        Xs, ys = S[m][0]().fit_resample(Xtr, ytr)
    model.fit(Xs, ys)
    return model, thr


def nested_dataset(name, out, methods, lrn_names, folds, repeats):
    from sklearn.base import clone
    from sklearn.metrics import average_precision_score
    from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    path = out / f'{name}.jsonl'
    done = _done_cells(path)
    X, y = R.load(name)
    splits = list(RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=R.SEED).split(X, y))
    (out / 'folds').mkdir(exist_ok=True)
    (out / 'folds' / f'{name}.json').write_text(json.dumps([s[1].tolist() for s in splits]))
    S, L = R.samplers(), R.learners()
    with path.open('a') as fh:
        for i, (tr, te) in enumerate(splits):
            rep, fold = divmod(i, folds)
            inner = list(StratifiedKFold(3, shuffle=True, random_state=SEED_EXT).split(X[tr], y[tr]))
            for m in methods:
                for ln in lrn_names:
                    if (rep, fold, m, ln) in done:
                        continue
                    rec = dict(dataset=name, repeat=rep, fold=fold, method=m, learner=ln, n_train=int(len(tr)),
                               n_min_train=int(y[tr].sum()), tuning='nested 3-fold, PR-AUC, equal budget')
                    try:
                        par, values = GRID[ln]
                        t0, inner_scores = time.perf_counter(), []
                        for v in values:
                            sc_v = []
                            for itr, iva in inner:
                                a, b = tr[itr], tr[iva]
                                sc = StandardScaler().fit(X[a])
                                mdl, thr = _apply(m, clone(L[ln]).set_params(**{par: v}), sc.transform(X[a]), y[a], S, L, ln)
                                if mdl is None:
                                    break
                                sc_v.append(average_precision_score(y[b], mdl.predict_proba(sc.transform(X[b]))[:, 1]))
                            if not sc_v:
                                break
                            inner_scores.append(float(np.mean(sc_v)))
                        if not inner_scores:
                            rec.update(status='not applicable'); fh.write(json.dumps(rec) + '\n'); continue
                        best = values[int(np.argmax(inner_scores))]
                        sc = StandardScaler().fit(X[tr])
                        mdl, thr = _apply(m, clone(L[ln]).set_params(**{par: best}), sc.transform(X[tr]), y[tr], S, L, ln)
                        p = mdl.predict_proba(sc.transform(X[te]))[:, 1]
                        rec.update(R.scores(y[te], p, thr), threshold=thr, tuned_param=par, tuned_value=best,
                                   inner_pr_auc=inner_scores, status='ok', seconds=time.perf_counter() - t0)
                    except Exception as e:  # noqa: BLE001
                        rec.update(status='error', error=f'{type(e).__name__}: {e}'[:300], trace=traceback.format_exc(limit=1)[-300:])
                    fh.write(json.dumps(rec) + '\n')
    return name


def safe(fn, n, out, *a):
    t = time.perf_counter()
    try:
        fn(n, out, *a)
        (out / f'{n}.error').unlink(missing_ok=True)
        print(f'{n}: {time.perf_counter() - t:.1f}s', flush=True)
    except Exception:  # noqa: BLE001
        (out / f'{n}.error').write_text(traceback.format_exc())
        print(f'{n}: ERROR', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tier', choices=['highdim', 'nested'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--jobs', type=int, default=1)
    ap.add_argument('--datasets', default='auto')
    ap.add_argument('--methods', default='all')
    ap.add_argument('--learners', default='auto')
    ap.add_argument('--repeats', type=int, default=None)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    methods = ['none', 'class_weight', 'threshold'] + list(R.samplers()) if a.methods == 'all' else a.methods.split(',')
    if a.tier == 'highdim':
        names = select_highdim(out) if a.datasets == 'auto' else a.datasets.split(',')
        lrn = list(R.learners()) if a.learners == 'auto' else a.learners.split(',')
        fn, reps = R.run_dataset, a.repeats or 5
        size = {}
        sel = out / 'highdim_selection.json'
        if sel.exists():
            size = {'oml_' + u['name']: u['rows'] * u['features'] for u in json.loads(sel.read_text())['used']}
        jobs = sorted(((n, r) for n in names for r in range(reps)), key=lambda j: (-size.get(j[0], 0), j[1], j[0]))
        (out / 'config.json').write_text(json.dumps(dict(tier=a.tier, seed=R.SEED, folds=5, repeats=reps, datasets=names,
                                                         methods=methods, learners=lrn, split='one job per dataset and repeat'), indent=1))
        from joblib import Parallel, delayed
        Parallel(n_jobs=a.jobs, verbose=5)(delayed(safe_rep)(n, out, methods, lrn, 5, reps, r) for n, r in jobs)
        merge(out, names)
        errs = sorted(p.name for p in out.glob('*.error'))
        print(f'finished {a.tier}: {len(names)} datasets, {len(errs)} jobs with errors {errs}', flush=True)
        return
    else:
        if a.datasets == 'auto':
            import imbalanced_databases as imbd
            pool = []
            for f in sorted(x[5:] for x in dir(imbd) if x.startswith('load_') and x != 'load_all'):
                try:
                    if int(R.load(f)[1].sum()) >= 30:
                        pool.append(f)
                except Exception:  # noqa: BLE001
                    pass
            names = sorted(random.Random(SEED_EXT).sample(pool, min(30, len(pool))))
        else:
            names = a.datasets.split(',')
        lrn = ['LR', 'kNN', 'RF', 'GB'] if a.learners == 'auto' else a.learners.split(',')
        fn, reps = nested_dataset, a.repeats or 3
    (out / 'config.json').write_text(json.dumps(dict(tier=a.tier, seed=R.SEED, seed_ext=SEED_EXT, folds=5, repeats=reps, datasets=names,
                                                     methods=methods, learners=lrn, grid=GRID if a.tier == 'nested' else None), indent=1))
    from joblib import Parallel, delayed
    Parallel(n_jobs=a.jobs, verbose=5)(delayed(safe)(fn, n, out, methods, lrn, 5, reps) for n in names)
    errs = sorted(p.stem for p in out.glob('*.error'))
    print(f'finished {a.tier}: {len(names)} datasets, {len(errs)} with errors {errs}', flush=True)


if __name__ == '__main__':
    main()
