#!/usr/bin/env python3
"""WP6.8 step 3: statistics of the rerun on the reference collection (Table 17, Section 9.2).

Rule fixed on 11 November 2026, before any result of the rerun was read (only run times and cell statuses of three
timing probes had been seen):
* Unit and grouping: fold results are averaged per (task, method, learner); tasks of the same family of the Data
  section (column family_t1 of reference_collection.csv: four yeast splits, three pima versions, two each of ecoli,
  glass, haberman, cleveland, heart and iris) are averaged, so that one family counts once, as Appendix C asks.
* A task enters only when every one of its cells has run (splits, methods, learners); tasks still running elsewhere
  are listed in summary.json and left out until they finish.
* Tests: those of the independent benchmark, imported from benchmark/stats.py unchanged (per learner and measure:
  Friedman with Iman-Davenport; Wilcoxon signed-rank of every method against SMOTE with Holm; Bayesian signed-rank
  with a region of practical equivalence of 0.01, seeded; median difference over families). As in the benchmark, a
  method that failed in every fold of a family has no mean there, and elsewhere its mean is over the folds where it
  ran; a method present in fewer than 80 percent of the families is left out of that test. (Wording corrected on
  11 Nov 2026, after the run, to match the benchmark's rule that the code imports; until then this sentence read "a
  method that cannot run in every fold of a family has no mean there". The code did not change.)
* Criterion C1 from the rerun (replaces the papers' own scores in Table 17): a method is on par with SMOTE when its
  median difference from SMOTE over families is at least -0.01 (the region of practical equivalence) for ROC-AUC and
  for PR-AUC, with the random forest and with gradient boosting (the strong learners of Section 7); "not testable"
  when it is left out of any of these four tests.
* Reported beside it: the same median differences, the Bayesian probabilities, the Brier score difference, the
  baselines (no resampling, class weights, tuned threshold, random oversampling) against SMOTE, and the cells where a
  sampler could not run.
Usage: python3 -I stats42.py <bench dir> <reference_collection.csv> <out dir> <results dir> [<results dir> ...]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

STRONG = ['RF', 'GB']
KEY = ['roc_auc', 'pr_auc']
ROPE = 0.01


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    bench, refc, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    srcs = [Path(p) for p in sys.argv[4:]]
    out.mkdir(parents=True, exist_ok=True)
    st = module(bench / 'stats.py', 'smote25_stats')
    fam = {r['task']: r['family_t1'] for r in pd.read_csv(refc, dtype=str).fillna('').to_dict('records')}
    rows, seen, dup = [], set(), 0
    for src in srcs:
        for f in sorted(src.glob('*.jsonl')):
            for line in f.open():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:   # a line cut short when a run was stopped
                    continue
                k = (r['dataset'], r['repeat'], r['fold'], r['method'], r['learner'])
                if k in seen:
                    dup += 1
                    continue
                seen.add(k)
                rows.append(r)
    df = pd.DataFrame(rows)
    # a task enters the analysis only when every cell has run (all splits, methods and learners); a task still running
    # elsewhere, or stopped, is listed in summary.json and left out
    cells = df.groupby('dataset').size()
    expected = int(cells.max())
    incomplete = sorted(d for d, c in cells.items() if c < expected)
    df = df[~df['dataset'].isin(incomplete)].copy()
    unknown = sorted(set(df['dataset']) - set(fam))
    if unknown:
        sys.exit(f'STOP: tasks without a family: {unknown}')
    df['family'] = df['dataset'].map(fam)
    status = (df.assign(sampler_error=df.get('error', pd.Series('', index=df.index)).fillna('').str.startswith('RuntimeError: sampler'))
              .groupby(['method', 'status']).size().unstack(fill_value=0))
    status.to_csv(out / 'cell_status.csv')
    ok = df[df['status'] == 'ok'].copy()
    per_task = ok.groupby(['family', 'dataset', 'method', 'learner'])[st.MEASURES].mean().reset_index()
    per_task['n_folds'] = ok.groupby(['family', 'dataset', 'method', 'learner']).size().values
    per_task.to_csv(out / 'per_task_means.csv', index=False)
    per_fam = per_task.groupby(['family', 'method', 'learner'])[st.MEASURES].mean().reset_index()
    per_fam.to_csv(out / 'per_family_means.csv', index=False)
    res = pd.DataFrame(st.tests(per_fam))
    res.to_csv(out / 'tests_vs_smote.csv', index=False)
    # tasks on which a method has no result in some fold (sampler could not run)
    fails = {}
    for m in sorted(df['method'].unique()):
        g = df[(df['method'] == m)]
        bad = sorted({d for d, s in zip(g['dataset'], g['status']) if s == 'error'})
        fails[m] = bad
    methods = [m for m in sorted(df['method'].unique()) if m != 'SMOTE']
    c1 = []
    for m in methods:
        row = {'method': m}
        worse = missing = False
        for ln in STRONG:
            for ms in KEY:
                hit = res[(res['method'] == m) & (res['learner'] == ln) & (res['measure'] == ms)]
                if hit.empty:
                    row[f'{ms}_{ln}'] = None
                    missing = True
                    continue
                d = float(hit['median_diff_vs_smote'].iloc[0])
                row[f'{ms}_{ln}'] = d
                worse = worse or d < -ROPE
        verdict = 'no' if worse else ('not testable' if missing else 'yes')
        for ln in STRONG:
            hit = res[(res['method'] == m) & (res['learner'] == ln) & (res['measure'] == 'brier')]
            row[f'brier_{ln}'] = float(hit['median_diff_vs_smote'].iloc[0]) if not hit.empty else None
        row['c1_rerun'] = verdict
        row['tasks_with_sampler_errors'] = len(fails.get(m, []))
        c1.append(row)
    pd.DataFrame(c1).to_csv(out / 'c1_rerun.csv', index=False)
    summary = dict(results_dirs=[str(s) for s in srcs], fold_results=len(df), ok=int(len(ok)), duplicates_skipped=dup,
                   tasks=int(df['dataset'].nunique()), families=int(df['family'].nunique()),
                   tasks_by_family={f: sorted(set(df.loc[df['family'] == f, 'dataset'])) for f in sorted(df['family'].unique())},
                   cells_by_status=df['status'].value_counts().to_dict(), sampler_error_tasks=fails,
                   cells_per_task=expected, tasks_incomplete_left_out={d: int(cells[d]) for d in incomplete},
                   rule={'rope': ROPE, 'learners': STRONG, 'measures': KEY})
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(f"{len(df)} cells ({len(ok)} ok, {dup} duplicates skipped); {summary['tasks']} tasks in {summary['families']} families; "
          f"{len(res)} comparisons with SMOTE; written to {out}")


if __name__ == '__main__':
    main()
