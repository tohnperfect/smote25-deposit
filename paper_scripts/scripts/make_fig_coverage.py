#!/usr/bin/env python3
"""Figure: the corpus against the coverage sample of the systematic search (Section 4.4), from the rows of the table
that scripts/gen_coverage_table.py writes: the corpus counts printed in the paper and the sample counts of
data/search/screening_full_2026-11-11/samples/samples_summary.json, with the sample's Wilson 95% intervals.
Greyscale. Writes figures/fig_coverage.pdf. Usage: python3 -I scripts/make_fig_coverage.py DRAFT_DIR"""
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

R = Path(sys.argv[1])
sys.path.insert(0, str(R / 'scripts'))
from gen_coverage_table import CORPUS, rows_for  # noqa: E402

s = json.load(open(R / 'data/search/screening_full_2026-11-11/samples/samples_summary.json', encoding='utf-8'))['coverage']['pooled']
rows = [('Method (corpus: papers that generate synthetic minority examples)', None, None)] + rows_for(s)

plt.rcParams.update({'font.family': 'serif', 'font.size': 7})
fig, ax = plt.subplots(figsize=(6.6, 4.0))
y = 0
ticks, labels = [], []
for label, key, d in rows:
    if key is None:
        y -= 0.45
        head = re.sub(r'\\multicolumn\{3\}\{l\}\{\\emph\{(.*)\}\}', r'\1', label)
        ax.text(-1.5, y, head, ha='left', va='center', fontsize=7, style='italic')
        y -= 1
        continue
    ck, cn = CORPUS[key][:2]
    c = 100 * ck / cn
    sp = 100 * d['k'] / d['n']
    lo, hi = d['ci95']
    ax.plot([lo, hi], [y, y], color='0.45', lw=1.0, solid_capstyle='butt', zorder=1)
    ax.plot([c, sp], [y, y], color='0.8', lw=0.6, zorder=0)
    ax.plot(sp, y, 'o', ms=4.6, mfc='white', mec='black', mew=0.8, zorder=3)
    ax.plot(c, y, 'o', ms=3.6, mfc='black', mec='black', zorder=4)
    ticks.append(y)
    labels.append(label)
    y -= 1
ax.set_yticks(ticks)
ax.set_yticklabels(labels)
ax.set_xlim(-2, 100)
ax.set_ylim(y + 0.3, 0.6)
ax.set_xticks(range(0, 101, 20))
ax.set_xlabel('Share of papers (%)')
ax.xaxis.grid(True, color='0.9', lw=0.5)
ax.set_axisbelow(True)
for sp_ in ('top', 'right', 'left'):
    ax.spines[sp_].set_visible(False)
ax.tick_params(axis='y', length=0)
h1, = ax.plot([], [], 'o', ms=3.6, mfc='black', mec='black', label='Corpus')
h2, = ax.plot([], [], 'o', ms=4.6, mfc='white', mec='black', mew=0.8, label='Coverage sample, with its 95% interval')
ax.legend(handles=[h1, h2], loc='lower left', bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False, fontsize=7, handletextpad=0.3, columnspacing=2)
fig.tight_layout()
fig.savefig(R / 'figures/fig_coverage.pdf')
print('wrote figures/fig_coverage.pdf')
