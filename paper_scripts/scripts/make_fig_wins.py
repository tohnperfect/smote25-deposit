#!/usr/bin/env python3
"""Figure: comparisons of the proposed method with plain SMOTE by metric (Section 5.5), drawn from the rows of the
table of the Data extraction (label supp:winsmetric) as the online appendix prints them. Greyscale.
Writes figures/fig_wins_metric.pdf. Usage: python3 -I scripts/make_fig_wins.py DRAFT_DIR"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

R = Path(sys.argv[1])
sys.path.insert(0, str(R / 'scripts'))
from table_rows import num, table_rows  # noqa: E402

rows = table_rows(R, 'supp:winsmetric')
data = [(r[0], *[int(num(x)) for x in r[1:7]]) for r in rows]   # metric, papers, rows, wins, ties, losses, n.c.
for m, p, n, w, t, l, nc in data:
    assert w + t + l + nc == n, m
allrow = [d for d in data if d[0].startswith('All')][0]
assert sum(d[2] for d in data if d is not allrow) == allrow[2]

plt.rcParams.update({'font.family': 'serif', 'font.size': 7})
fig, ax = plt.subplots(figsize=(6.6, 2.55))
y = 0
ticks, labels = [], []
for d in data:
    m, p, n, w, t, l, nc = d
    if d is allrow:
        y -= 0.5
    left = 0
    for v, kw in ((w, dict(fc='0.25', ec='black')), (t, dict(fc='0.65', ec='black')), (l, dict(fc='white', ec='black')),
                  (nc, dict(fc='white', ec='black', hatch='////'))):
        if v:
            ax.barh(y, 100 * v / n, left=left, height=0.62, lw=0.5, **kw)
        left += 100 * v / n
    share = 100 * w / (w + l) if (w + l) else float('nan')
    ax.text(102, y, f'{n:,} in {p} paper{"s" if p != 1 else ""}', ha='left', va='center')
    ax.text(134, y, f'{share:.0f}%', ha='left', va='center')
    if m == 'AUC':   # v0.63: the caption of the figure gives this row as its example
        cap = (R / 'sec/05-data.tex').read_text(encoding='utf-8')
        assert f'on AUC, {w} wins against {l} for SMOTE, which is {share:.0f}\\%' in cap, 'caption of Figure 6'
    ticks.append(y)
    labels.append(m)
    y -= 1
ax.text(102, 0.85, 'Number of\ncomparisons', ha='left', va='bottom', fontsize=6.4, linespacing=1.05)
ax.text(134, 0.85, 'Won by the proposed\nmethod, ties left out', ha='left', va='bottom', fontsize=6.4, linespacing=1.05)
ax.set_yticks(ticks)
ax.set_yticklabels(labels)
ax.set_xlim(0, 160)
ax.set_ylim(y + 0.35, 0.6)
ax.set_xticks(range(0, 101, 20))
ax.set_xlabel('Share of the comparisons on the metric (%)', x=0.35)
for sp_ in ('top', 'right', 'left'):
    ax.spines[sp_].set_visible(False)
ax.spines['bottom'].set_bounds(0, 100)
ax.tick_params(axis='y', length=0)
from matplotlib.patches import Patch  # noqa: E402
hs = [Patch(fc='0.25', ec='black', lw=0.5, label='Proposed method wins'), Patch(fc='0.65', ec='black', lw=0.5, label='Tie'),
      Patch(fc='white', ec='black', lw=0.5, label='SMOTE wins'), Patch(fc='white', ec='black', lw=0.5, hatch='////', label='Value not printed as a number')]
ax.legend(handles=hs, loc='upper center', bbox_to_anchor=(0.36, -0.24), ncol=4, frameon=False, fontsize=6.6, columnspacing=1.2, handlelength=1.4)
fig.tight_layout()
fig.savefig(R / 'figures/fig_wins_metric.pdf')
print('wrote figures/fig_wins_metric.pdf')
