#!/usr/bin/env python3
"""WP6.8 step 3: the rerun behind Table 17 on the reference collection of 42 tasks (Appendix C).

Decision of the team lead, 11 November 2026: run the ten methods of Table 17 on the reference collection under the
protocol of the independent benchmark before the table recommends anything; RSMOTE and CGMOS run as faithful
implementations, with the failure to reproduce their papers stated.

The protocol is `benchmark/run.py` unchanged (its functions are imported, not copied): five repetitions of
stratified 5-fold cross-validation with seed 20261110, the same folds for every method, scaling, resampling and
threshold fitted on the training part only, the six learners with one configuration each, every sampler with its
authors' defaults, the same measures. The tasks come from `tasks42.py` (checked against the Data section's table);
rows with a missing value are dropped (as the Data section's measure.py does), nominal features are one-hot encoded
with the categories of the whole task (no label is used), and the minority label of `reference_collection.csv` is
the positive class.

Methods: the baselines of Section 9.1 (no resampling, class weights, tuned threshold, random oversampling) and the
ten methods of Table 17: SMOTE, ADASYN (imbalanced-learn 0.14.2), G-SMOTE (imbalanced-learn-extra 0.2.10),
Cluster-SMOTE and Safe-Level-SMOTE (smote-variants 1.0.1), and the five re-implementations of
`benchmark/rerun42/methods/` (CGMOS, SMOM, AB-SMOTE, RSMOTE, FW-SMOTE), each with the defaults its folder documents.

Usage (resumable; one JSON line per cell in <out>/<task>.jsonl, as run.py writes):
    python3 -I run42.py --bench <benchmark dir> --src <src dir> --check <tasks42_check.csv> --out <out dir> [--jobs N]
        [--tasks a,b] [--max-n N | --min-n N] [--methods ...] [--learners ...] [--repeats 5] [--folds 5]
        [--split-repeats | --split-folds]   (one job per task and repeat, or per task and split, for the large tasks)
    The TabPFN arm (v0.21, D43): --methods none,SMOTE --learners TabPFN, with TABPFN_TOKEN set for the run.
"""
import argparse
import importlib.util
import json
import re
import sys
import time
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

BASELINES = ['none', 'class_weight', 'threshold', 'ROS']
TABLE17 = ['SMOTE', 'Cluster-SMOTE', 'ADASYN', 'Safe-Level-SMOTE', 'G-SMOTE', 'CGMOS', 'SMOM', 'AB-SMOTE', 'RSMOTE',
           'FW-SMOTE']
NEW = {'CGMOS': ('cgmos', 'CGMOS'), 'SMOM': ('smom', 'SMOM'), 'AB-SMOTE': ('absmote', 'ABSMOTE'),
       'RSMOTE': ('rsmote', 'RSMOTE'), 'FW-SMOTE': ('fwsmote', 'FWSMOTE')}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def tabpfn_learner(seed):
    """v0.21 (D43): the foundation-model arm. TabPFNClassifier with its defaults (n_estimators, model and preprocessing
    'auto'), on the device that SMOTE25_TABPFN_DEVICE names (default 'auto': a GPU, Apple's MPS, or the CPU). Its model
    weights download only after the team lead accepts Prior Labs' license; the key is passed only as TABPFN_TOKEN for a
    run, never written down. A task beyond TabPFN's pretraining limits fails in every cell and is reported as such (no
    subsampling). SMOTE25_TABPFN_STANDIN=1 swaps in a logistic regression to test the plumbing without the weights;
    such a run is never a result."""
    import os
    if os.environ.get('SMOTE25_TABPFN_STANDIN') == '1':
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(max_iter=2000)
    # v0.24 (14 Nov 2026): TabPFN 10.0.0 copies a valid TABPFN_TOKEN to ~/.cache/tabpfn/auth_token (save_token in
    # tabpfn.browser_auth). The key must stay in the environment of the run only, so that copy is switched off here.
    import tabpfn.browser_auth as _tabpfn_auth
    _tabpfn_auth.save_token = lambda token: None
    from tabpfn import TabPFNClassifier

    class TabPFNBatched(TabPFNClassifier):
        """v0.25: predict_proba in chunks of 500 test rows. TabPFN's test rows attend to the training rows only, so the
        predictions are those of one call; the chunks only bound the GPU memory (on the MacBook the 12,526 test rows
        of smoke detection ran out of memory in one call)."""
        def predict_proba(self, X):
            import numpy as _np
            n = X.shape[0]
            if n <= 500:
                return super().predict_proba(X)
            return _np.vstack([super(TabPFNBatched, self).predict_proba(X[i:i + 500]) for i in range(0, n, 500)])

    return TabPFNBatched(device=os.environ.get('SMOTE25_TABPFN_DEVICE', 'auto'), random_state=seed)


def slug(task):
    return re.sub(r'[^A-Za-z0-9._-]+', '_', task).strip('_')


def prepare(d, y, minority):
    """DataFrame of strings and labels -> numeric X, binary y (1 = minority); drop rows with a missing value."""
    dd = d.replace({'?': np.nan, '<null>': np.nan, '': np.nan, 'nan': np.nan, 'NaN': np.nan})
    dd = dd.loc[:, dd.notna().any(axis=0)]
    keep = dd.notna().all(axis=1).to_numpy()
    dd, yy = dd.loc[keep].reset_index(drop=True), y[keep].reset_index(drop=True)
    num, cat = {}, []
    for c in dd.columns:
        s = pd.to_numeric(dd[c].astype(str).str.strip(), errors='coerce')
        if s.notna().all():
            num[c] = s.astype(float)
        else:
            cat.append(c)
    parts = [pd.DataFrame(num)]
    if cat:
        parts.append(pd.get_dummies(dd[cat].astype(str), dtype=float))
    X = pd.concat(parts, axis=1).to_numpy(dtype=float)
    keep_cols = X.std(axis=0) > 0            # a constant column carries nothing and breaks some samplers
    X = X[:, keep_cols]
    yb = (yy.astype(str).str.strip() == str(minority)).astype(int).to_numpy()
    return X, yb, dict(rows_dropped=int((~keep).sum()), n_categorical=len(cat), d_used=int(X.shape[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bench', required=True)
    ap.add_argument('--src', required=True)
    ap.add_argument('--check', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--tasks', default='all')
    ap.add_argument('--max-n', type=int, default=0)
    ap.add_argument('--min-n', type=int, default=0)
    ap.add_argument('--methods', default='all')
    ap.add_argument('--learners', default='all')
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--repeats', type=int, default=5)
    ap.add_argument('--only-splits', default='', help='comma list of split indices to run (timing probes)')
    ap.add_argument('--split-repeats', action='store_true', help='one job per (task, repeat) instead of per task')
    ap.add_argument('--split-folds', action='store_true', help='one job per (task, split) instead of per task')
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    chk = pd.read_csv(a.check, dtype=str).fillna('')
    chk = chk[chk['status'] == 'ok']
    if a.tasks != 'all':
        want = set(a.tasks.split(','))
        chk = chk[chk['task'].isin(want) | chk['task'].map(slug).isin(want)]
    if a.max_n:
        chk = chk[chk['N'].astype(int) <= a.max_n]
    if a.min_n:
        chk = chk[chk['N'].astype(int) >= a.min_n]
    methods = BASELINES + TABLE17 if a.methods == 'all' else a.methods.split(',')
    bench = module(Path(a.bench) / 'run.py', 'smote25_run')
    lrn = list(bench.learners()) if a.learners == 'all' else a.learners.split(',')
    cfg = dict(seed=bench.SEED, folds=a.folds, repeats=a.repeats, methods=methods, learners=lrn,
               tasks=chk['task'].tolist(), protocol='benchmark/run.py (imported)', missing_rows='dropped',
               nominal='one-hot, categories of the whole task', positive='minority label of reference_collection.csv')
    if 'TabPFN' in lrn:   # v0.21: what ran, for the paper and the deposit
        import os
        if os.environ.get('SMOTE25_TABPFN_STANDIN') == '1':
            cfg['tabpfn'] = 'STAND-IN (logistic regression): a test of the plumbing, never a result'
        else:
            import tabpfn
            from tabpfn.settings import settings as _tabpfn_settings
            cfg['tabpfn'] = dict(package=tabpfn.__version__, model=str(_tabpfn_settings.tabpfn.model_version),
                                 device=os.environ.get('SMOTE25_TABPFN_DEVICE', 'auto'),
                                 settings='defaults (n_estimators, model_path auto), random_state = seed')
    (out / 'config.json').write_text(json.dumps(cfg, indent=1))
    jobs = []
    for _, r in chk.sort_values('N', key=lambda s: -s.astype(int)).iterrows():
        if a.split_folds:
            parts = [('s', i) for i in range(a.repeats * a.folds)]
        elif a.split_repeats:
            parts = [('r', i) for i in range(a.repeats)]
        else:
            parts = [None]
        for part in parts:
            jobs.append((r.to_dict(), part))
    only = [int(x) for x in a.only_splits.split(',') if x != '']
    args = (a.bench, a.src, str(out), methods, lrn, a.folds, a.repeats, only)
    if a.jobs > 1:
        from joblib import Parallel, delayed
        Parallel(n_jobs=a.jobs, verbose=0, batch_size=1)(delayed(safe_task)(r, rep, *args) for r, rep in jobs)
    else:
        for r, rep in jobs:
            safe_task(r, rep, *args)
    errs = sorted(p.name for p in out.glob('*.error'))
    print(f'finished: {len(jobs)} jobs, {len(errs)} with errors {errs}', flush=True)


def safe_task(r, rep, *args):
    name = slug(r['task']) + ('' if rep is None else f'.{rep[0]}{rep[1]}')
    out = Path(args[2])
    t = time.perf_counter()
    try:
        run_task(r, rep, *args)
        (out / f'{name}.error').unlink(missing_ok=True)
        print(f'{name}: {time.perf_counter() - t:.1f}s', flush=True)
    except Exception:  # noqa: BLE001
        (out / f'{name}.error').write_text(traceback.format_exc())
        print(f'{name}: ERROR after {time.perf_counter() - t:.1f}s', flush=True)


def run_task(r, rep_only, bench_dir, src, out, methods, lrn_names, folds, repeats, only):
    from sklearn.base import clone
    from sklearn.model_selection import RepeatedStratifiedKFold
    from sklearn.preprocessing import StandardScaler
    bench = module(Path(bench_dir) / 'run.py', 'smote25_run')
    tasks = module(Path(bench_dir) / 'rerun42' / 'scripts' / 'tasks42.py', 'smote25_tasks42')
    S = bench.samplers()
    for m, (folder, cls) in NEW.items():
        mod = module(Path(bench_dir) / 'rerun42' / 'methods' / folder / f'{folder}.py', f'smote25_{folder}')
        S[m] = ((lambda c=getattr(mod, cls): c(random_state=bench.SEED)), f'SMOTE25 re-implementation ({folder}/)')
    L = bench.learners()
    if 'TabPFN' in lrn_names:   # v0.21 (D43): only when a run names it; 'all' keeps the six learners
        L['TabPFN'] = tabpfn_learner(bench.SEED)
    out = Path(out)
    name = slug(r['task'])
    path = out / (f'{name}.jsonl' if rep_only is None else f'{name}.{rep_only[0]}{rep_only[1]}.jsonl')
    done = set()
    for p in out.glob(f'{name}.jsonl'), out.glob(f'{name}.[rs][0-9]*.jsonl'):
        for q in p:
            for line in q.open():
                try:
                    x = json.loads(line)
                except json.JSONDecodeError:
                    continue
                done.add((x['repeat'], x['fold'], x['method'], x['learner']))
    d, y, _ = tasks.load(src, r['source'], r['file'], r['minority_label'])
    X, yb, info = prepare(d, y, r['minority_label'])
    (out / 'tasks').mkdir(exist_ok=True)
    (out / 'tasks' / f'{name}.json').write_text(json.dumps(dict(task=r['task'], source=r['source'], n=int(len(yb)),
                                                              n_min=int(yb.sum()), **info)))
    cv = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=bench.SEED)
    splits = list(cv.split(X, yb))
    (out / 'folds').mkdir(exist_ok=True)
    fp = out / 'folds' / f'{name}.json'
    if not fp.exists():
        fp.write_text(json.dumps([s[1].tolist() for s in splits]))
    with path.open('a') as fh:
        for i, (tr, te) in enumerate(splits):
            rep, fold = divmod(i, folds)
            if rep_only is not None and ((rep_only[0] == 'r' and rep != rep_only[1]) or (rep_only[0] == 's' and i != rep_only[1])):
                continue
            if only and i not in only:
                continue
            sc = StandardScaler().fit(X[tr])
            Xtr, Xte, ytr, yte = sc.transform(X[tr]), sc.transform(X[te]), yb[tr], yb[te]
            cache = {}
            for m in methods:
                for ln in lrn_names:
                    if (rep, fold, m, ln) in done:
                        continue
                    rec = dict(dataset=r['task'], source=r['source'], repeat=rep, fold=fold, method=m, learner=ln,
                               n_train=int(len(tr)), n_min_train=int(ytr.sum()))
                    try:
                        model = clone(L[ln])
                        thr, t0 = 0.5, time.perf_counter()
                        Xs, ys = Xtr, ytr
                        if m == 'class_weight':
                            if 'class_weight' not in model.get_params():
                                rec.update(status='not applicable')
                                fh.write(json.dumps(rec) + '\n')
                                continue
                            model.set_params(class_weight='balanced')
                        elif m == 'threshold':
                            thr = bench.best_threshold(clone(L[ln]), Xtr, ytr)
                        elif m != 'none':
                            if m not in cache:
                                t1 = time.perf_counter()
                                try:
                                    res = S[m][0]().fit_resample(Xtr, ytr)
                                    cache[m] = (np.asarray(res[0], dtype=float), np.asarray(res[1]).astype(int),
                                                time.perf_counter() - t1, None)
                                except Exception as e:  # noqa: BLE001
                                    cache[m] = (None, None, time.perf_counter() - t1, f'{type(e).__name__}: {e}'[:300])
                            Xs, ys, rec['resample_seconds'], err = cache[m]
                            if err:
                                raise RuntimeError('sampler: ' + err)
                            rec['n_synthetic'] = int(len(ys) - len(ytr))
                        model.fit(Xs, ys)
                        p = model.predict_proba(Xte)[:, 1]
                        rec.update(bench.scores(yte, p, thr), threshold=thr, status='ok', seconds=time.perf_counter() - t0)
                    except Exception as e:  # noqa: BLE001
                        rec.update(status='error', error=f'{type(e).__name__}: {e}'[:300],
                                   trace=traceback.format_exc(limit=1)[-300:])
                    fh.write(json.dumps(rec) + '\n')
                    fh.flush()


if __name__ == '__main__':
    main()
