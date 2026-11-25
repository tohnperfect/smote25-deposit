#!/usr/bin/env python3
"""Derived counts of the independent benchmark (WP6) that the text uses and no result file holds yet.

Writes
  benchmark/results_summary/highdim/smote_vs_none.csv  SMOTE against no resampling per measure, over dataset-learner
                                                        pairs of the high-dimensional tier (same rule as the core tier
                                                        file written by make_fig_smote_vs_none.py)
  benchmark/results_summary/nested/pool.json            the datasets of the core tier with at least 30 minority examples
                                                        and the 30 drawn from them with the seed 20261111 (the draw of
                                                        run_ext.py, recomputed and checked against nested/config.json)
  benchmark/results_summary/families.json               distinct source families per tier and per comparison with SMOTE
Usage: python3 -I scripts/bench_derived.py <draft root>   (needs the benchmark environment: imbalanced-databases)
"""
import ast
import csv
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1])
RS = ROOT / 'benchmark/results_summary'

# 1. high-dimensional tier: SMOTE against no resampling
MEASURES = [('gmean', 'G-mean', False), ('f1', 'F1', False), ('roc_auc', 'ROC-AUC', False),
            ('pr_auc', 'PR-AUC', False), ('brier', 'Brier score', True)]
d = pd.read_csv(RS / 'highdim/per_dataset_means.csv')
rows = []
for col, label, lower in MEASURES:
    w = d.pivot_table(index=['dataset', 'learner'], columns='method', values=col)[['SMOTE', 'none']].dropna()
    diff = w['SMOTE'] - w['none']
    better = diff < -1e-9 if lower else diff > 1e-9
    worse = diff > 1e-9 if lower else diff < -1e-9
    rows.append(dict(measure=label, pairs=len(w), datasets=w.index.get_level_values(0).nunique(),
                     smote_better=int(better.sum()), tie=int((~better & ~worse).sum()), none_better=int(worse.sum()),
                     pct_smote_better=round(100 * float(better.mean()), 1), median_diff=round(float(diff.median()), 4)))
with (RS / 'highdim/smote_vs_none.csv').open('w', newline='') as fh:
    wr = csv.DictWriter(fh, list(rows[0])); wr.writeheader(); wr.writerows(rows)
for r in rows:
    print('highdim', r)

# 2. nested tier: the pool and the draw
sys.path.insert(0, str(ROOT / 'benchmark'))
import run as R  # noqa: E402  (the loader of the benchmark)
import imbalanced_databases as imbd  # noqa: E402

pool, errors = [], []
for f in sorted(x[5:] for x in dir(imbd) if x.startswith('load_') and x != 'load_all'):
    try:
        X, y = R.load(f)
    except Exception as e:  # recorded, not hidden
        errors.append([f, type(e).__name__])
        continue
    if int(y.sum()) >= 30:
        pool.append(f)
cfg = json.loads((RS / 'nested/config.json').read_text())
seed = cfg['seed_ext']
drawn = sorted(random.Random(seed).sample(pool, min(30, len(pool))))
listed = cfg['datasets'] if isinstance(cfg['datasets'], list) else ast.literal_eval(cfg['datasets'])
assert drawn == sorted(listed), 'the recomputed draw differs from nested/config.json'
(RS / 'nested/pool.json').write_text(json.dumps(dict(
    rule='core-tier datasets with at least 30 minority examples; 30 drawn with random.Random(seed).sample, as in run_ext.py',
    seed=seed, pool_size=len(pool), drawn_size=len(drawn), pool=pool, drawn=drawn, load_errors=errors), indent=1))
print('nested pool', len(pool), 'drawn', len(drawn), 'load errors', len(errors))

# 3. source families
fam = {}
for tier in ('core', 'highdim', 'nested'):
    p = pd.read_csv(RS / f'{tier}/per_family_means.csv')
    fam[tier] = dict(families=int(p.family.nunique()),
                     families_with_smote=int(p[p.method == 'SMOTE'].family.nunique()))
(RS / 'families.json').write_text(json.dumps(fam, indent=1))
print('families', fam)
