#!/usr/bin/env python3
"""v0.21 (D43): statistics of the TabPFN arm of the rerun on the reference collection (Section 7.5, online appendix S7).

Rule fixed on 14 November 2026, before any result of the arm existed (the TabPFN weights had not been downloaded):
* Cells: TabPFN with its defaults, without resampling ("none") and after SMOTE ("SMOTE", imbalanced-learn defaults),
  on the same folds as the rerun (five repetitions of stratified 5-fold cross-validation, seed 20261110), scaling and
  SMOTE fitted on the training part only. No threshold tuning and no class weights for TabPFN.
* Unit and grouping as in stats42.py: fold results averaged per (task, method, learner), tasks of one family of
  reference_collection.csv averaged, so one family counts once.
* A task enters only when TabPFN ran in every one of its cells. A task that TabPFN refuses (beyond its pretraining
  limits) or that fails is listed in summary.json and left out of every comparison below, the strong learners' ones
  included, so that all comparisons use the same families. Nothing is subsampled.
* Comparisons, each over the families where both sides ran: (1) TabPFN after SMOTE against TabPFN without
  resampling; (2) TabPFN without resampling against the random forest and gradient boosting, each without resampling
  and after SMOTE (four comparisons). Measures: ROC-AUC, PR-AUC and the Brier score. For each: the median difference
  over families (signed so that a positive value favours the first side; for the Brier score lower is better), the
  Wilcoxon signed-rank test with Holm's correction over the five comparisons of a measure, and the Bayesian
  signed-rank test (baycomp, seeded 20261110) with a region of practical equivalence of 0.01, as the benchmark does.
* Reading: two sides are on par for a measure when the median difference lies within 0.01 of zero; the text reports
  the medians, the probabilities and the number of families, and says that the arm ran with one configuration.
Usage: python3 -I stats42_tabpfn.py <reference_collection.csv> <out dir> <tabpfn results dir> <rerun results dir>...
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

KEY = ['roc_auc', 'pr_auc', 'brier']
LOWER_IS_BETTER = {'brier'}
ROPE = 0.01
SEED = 20261110
COMPARISONS = [  # (label, first side, second side): sides are (learner, method)
    ('TabPFN: SMOTE vs none', ('TabPFN', 'SMOTE'), ('TabPFN', 'none')),
    ('TabPFN vs RF, both none', ('TabPFN', 'none'), ('RF', 'none')),
    ('TabPFN vs GB, both none', ('TabPFN', 'none'), ('GB', 'none')),
    ('TabPFN none vs RF after SMOTE', ('TabPFN', 'none'), ('RF', 'SMOTE')),
    ('TabPFN none vs GB after SMOTE', ('TabPFN', 'none'), ('GB', 'SMOTE')),
]


def holm(ps):
    ps = np.asarray(ps, dtype=float)
    order = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (len(ps) - i) * ps[j])
        adj[j] = min(1.0, run)
    return adj


def read(dirs, learners, methods):
    rows, seen = [], set()
    for src in dirs:
        for f in sorted(Path(src).glob('*.jsonl')):
            for line in f.open():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r['learner'] not in learners or r['method'] not in methods:
                    continue
                k = (r['dataset'], r['repeat'], r['fold'], r['method'], r['learner'])
                if k not in seen:
                    seen.add(k)
                    rows.append(r)
    return pd.DataFrame(rows)


def main():
    refc, out, tab = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    rerun = [Path(p) for p in sys.argv[4:]]
    out.mkdir(parents=True, exist_ok=True)
    fam = {r['task']: r['family_t1'] for r in pd.read_csv(refc, dtype=str).fillna('').to_dict('records')}
    t = read([tab], {'TabPFN'}, {'none', 'SMOTE'})
    s = read(rerun, {'RF', 'GB'}, {'none', 'SMOTE'})
    if t.empty:
        sys.exit('STOP: no TabPFN cells')
    cells = t.groupby('dataset').size()
    expected = 2 * 25
    ok_status = t.assign(ok=t['status'] == 'ok').groupby('dataset')['ok'].all()
    complete = sorted(d for d in cells.index if cells[d] == expected and ok_status[d])
    left_out = {d: dict(cells=int(cells[d]), all_ok=bool(ok_status[d]),
                        error=str(t.loc[(t['dataset'] == d) & (t['status'] != 'ok'), 'error'].dropna().head(1).tolist()[:1]))
                for d in cells.index if d not in complete}
    df = pd.concat([t[t['dataset'].isin(complete)], s[s['dataset'].isin(complete)]], ignore_index=True)
    df = df[df['status'] == 'ok'].copy()
    unknown = sorted(set(df['dataset']) - set(fam))
    if unknown:
        sys.exit(f'STOP: tasks without a family: {unknown}')
    df['family'] = df['dataset'].map(fam)
    per_task = df.groupby(['family', 'dataset', 'learner', 'method'])[KEY].mean().reset_index()
    per_fam = per_task.groupby(['family', 'learner', 'method'])[KEY].mean().reset_index()
    per_task.to_csv(out / 'per_task_means.csv', index=False)
    per_fam.to_csv(out / 'per_family_means.csv', index=False)
    res = []
    for m in KEY:
        part = []
        for label, a, b in COMPARISONS:
            xa = per_fam[(per_fam['learner'] == a[0]) & (per_fam['method'] == a[1])].set_index('family')[m]
            xb = per_fam[(per_fam['learner'] == b[0]) & (per_fam['method'] == b[1])].set_index('family')[m]
            pair = pd.concat([xa.rename('a'), xb.rename('b')], axis=1).dropna()
            d = pair['a'] - pair['b']
            if m in LOWER_IS_BETTER:
                d = -d
            p = stats.wilcoxon(d).pvalue if len(d) and np.any(d != 0) else 1.0
            try:
                import baycomp
                np.random.seed(SEED)
                left, rope, right = baycomp.SignedRankTest.probs(pair['b'].values, pair['a'].values, rope=ROPE)
                if m in LOWER_IS_BETTER:
                    left, right = right, left
            except Exception:  # noqa: BLE001
                left = rope = right = np.nan
            part.append(dict(measure=m, comparison=label, n_families=int(len(pair)),
                             median_diff=float(np.median(d)) if len(d) else np.nan, wilcoxon_p=p,
                             p_first_better=right, p_rope=rope, p_second_better=left,
                             on_par=bool(len(d)) and abs(float(np.median(d))) <= ROPE))
        for row, a in zip(part, holm([r['wilcoxon_p'] for r in part])):
            row['holm_p'] = float(a)
        res.extend(part)
    pd.DataFrame(res).to_csv(out / 'tabpfn_comparisons.csv', index=False)
    summary = dict(tabpfn_dir=str(tab), rerun_dirs=[str(p) for p in rerun], tasks_complete=len(complete),
                   families=int(df['family'].nunique()), tasks_left_out=left_out,
                   rule=dict(rope=ROPE, measures=KEY, comparisons=[c[0] for c in COMPARISONS], seed=SEED))
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(f"{len(complete)} tasks complete ({summary['families']} families), {len(left_out)} left out; "
          f"{len(res)} comparisons written to {out}")


if __name__ == '__main__':
    main()
