#!/usr/bin/env python3
"""Figure: the seven-point minimum standard by period (Section 6.9), drawn from the rows of the table of the
Evaluation extraction (label supp:standard) as the online appendix prints them. Greyscale.
Writes figures/fig_standard.pdf. Usage: python3 -I scripts/make_fig_standard.py DRAFT_DIR"""
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

R = Path(sys.argv[1])
sys.path.insert(0, str(R / 'scripts'))
from table_rows import num, table_rows  # noqa: E402

rows = table_rows(R, 'supp:standard')
points = [(r[0], int(num(r[1])), [num(x) for x in r[2:6]]) for r in rows if not r[0].startswith('Median')]
median = [r for r in rows if r[0].startswith('Median')][0]
assert len(points) == 7
PER = ['to\n2009', '2010\nto 15', '2016\nto 20', '2021\nto 26']

plt.rcParams.update({'font.family': 'serif', 'font.size': 7})
fig, axes = plt.subplots(2, 4, figsize=(6.6, 2.85))
axes = axes.ravel()
for k, (ax, (name, n, v)) in enumerate(zip(axes, points)):
    ax.plot(range(4), v, '-o', color='black', lw=0.9, ms=3.2, clip_on=False)
    for i, x in enumerate(v):
        ax.text(i, x + 6, f'{x:.0f}', ha='center', va='bottom', fontsize=6.4)
    ax.set_title('\n'.join(textwrap.wrap(name, 24)) + f'\n({n} of 71 studies)', fontsize=6.8, linespacing=1.1)
    ax.set_xticks(range(4))
    ax.set_xticklabels(PER, fontsize=6.2)
    ax.set_ylim(0, 108)
    ax.set_xlim(-0.4, 3.4)
    ax.set_yticks([0, 50, 100])
    if k % 4:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel('Studies of the period (%)')
    ax.yaxis.grid(True, color='0.9', lw=0.5)
    ax.set_axisbelow(True)
    for sp_ in ('top', 'right'):
        ax.spines[sp_].set_visible(False)
ax = axes[7]
mv = [num(x) for x in median[2:6]]
ax.plot(range(4), mv, '-s', color='0.4', lw=0.9, ms=3.2)
for i, x in enumerate(mv):
    ax.text(i, x + 0.4, f'{x:g}', ha='center', va='bottom', fontsize=6.4)
ax.set_title('Median number of\npoints met\n(of seven)', fontsize=6.8, linespacing=1.1)
ax.set_xticks(range(4))
ax.set_xticklabels(PER, fontsize=6.2)
ax.set_ylim(0, 7.56)
ax.set_xlim(-0.4, 3.4)
ax.set_yticks([0, 3.5, 7])
ax.set_yticklabels(['0', '3.5', '7'])
ax.yaxis.tick_right()
ax.yaxis.grid(True, color='0.9', lw=0.5)
ax.set_axisbelow(True)
for sp_ in ('top', 'left'):
    ax.spines[sp_].set_visible(False)
fig.tight_layout(h_pad=1.2, w_pad=0.6)
fig.savefig(R / 'figures/fig_standard.pdf')
print('wrote figures/fig_standard.pdf')
