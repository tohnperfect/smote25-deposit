#!/usr/bin/env python3
"""Figure: SMOTE against no resampling, by measure, in the core tier of the independent benchmark (WP6).

Reads benchmark/results_summary/core/per_dataset_means.csv (fold results averaged per dataset, method and learner)
and writes figures/fig_smote_vs_none.pdf plus benchmark/results_summary/core/smote_vs_none.csv with the counts it
draws. A pair is one dataset and one learner where both SMOTE and no resampling ran; a tie is a difference below
1e-9; for the Brier score lower is better.
Usage: python3 -I scripts/make_fig_smote_vs_none.py <draft root>
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(sys.argv[1])
SRC = ROOT / 'benchmark/results_summary/core/per_dataset_means.csv'
MEASURES = [('gmean', 'G-mean', False), ('f1', 'F1', False), ('roc_auc', 'ROC-AUC', False),
            ('pr_auc', 'PR-AUC', False), ('brier', 'Brier score', True)]

d = pd.read_csv(SRC)
rows = []
for col, label, lower in MEASURES:
    w = d.pivot_table(index=['dataset', 'learner'], columns='method', values=col)[['SMOTE', 'none']].dropna()
    diff = w['SMOTE'] - w['none']
    better = diff < -1e-9 if lower else diff > 1e-9
    worse = diff > 1e-9 if lower else diff < -1e-9
    rows.append(dict(measure=label, pairs=len(w), datasets=w.index.get_level_values(0).nunique(),
                     smote_better=int(better.sum()), tie=int((~better & ~worse).sum()), none_better=int(worse.sum()),
                     pct_smote_better=round(100 * better.mean(), 1), median_diff=round(float(diff.median()), 4)))
out_csv = ROOT / 'benchmark/results_summary/core/smote_vs_none.csv'
with out_csv.open('w', newline='') as fh:
    wr = csv.DictWriter(fh, list(rows[0])); wr.writeheader(); wr.writerows(rows)

plt.rcParams.update({'font.family': 'serif', 'font.size': 8})
fig, ax = plt.subplots(figsize=(6.6, 2.1))
blue, light, dark = '#3b7dd8', '#d0d4da', '#868b93'
y = np.arange(len(rows))[::-1]
for yi, r in zip(y, rows):
    segs = [(r['smote_better'], blue, 'white'), (r['tie'], light, 'black'), (r['none_better'], dark, 'white')]
    left = 0
    for n, c, tc in segs:
        ax.barh(yi, n, left=left, color=c, height=0.62, edgecolor='white', linewidth=0.5)
        if n >= 40:
            ax.text(left + n / 2, yi, str(n), ha='center', va='center', color=tc, fontsize=7, fontweight='bold')
        left += n
    v = r['median_diff']
    dtxt = '0.000' if abs(v) < 0.0005 else f"{v:+.3f}".replace('-', '\u2212')   # true minus sign; no sign on zero
    note = f"{r['pct_smote_better']:.0f}% SMOTE better, median $\\Delta$ {dtxt}"
    ax.text(r['pairs'] * 1.01, yi, note, va='center', fontsize=7)
ax.set_yticks(y)
ax.set_yticklabels([r['measure'] + (' (lower is better)' if m[2] else '') for r, m in zip(rows, MEASURES)])
ax.set_xlim(0, rows[0]['pairs'])
ax.set_xlabel(f"dataset $\\times$ learner pairs ({rows[0]['datasets']} datasets $\\times$ 6 learners)")
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (blue, light, dark)]
ax.legend(handles, ['SMOTE better', 'tie', 'no resampling better'], ncol=3, frameon=False, fontsize=7,
          loc='lower center', bbox_to_anchor=(0.5, 1.0))
fig.savefig(ROOT / 'figures/fig_smote_vs_none.pdf', bbox_inches='tight')
for r in rows:
    print(r)
