#!/usr/bin/env python3
"""Draw the reach figure (Figure 5 of v0.2, figures/fig_reach.pdf) from an archived OpenAlex snapshot.

Reads group_publication_year.json / group_primary_topic_field_id.json when the
snapshot has raw JSON (scripts/openalex_snapshot.py with an API key), otherwise
citing_by_year.csv / citing_by_field.csv (the 10 Nov 2026 folder keeps those
in superseded_webfetch/). Greyscale by design: one ink, the
incomplete year hatched, direct labels on the field bars.
Usage: python3 scripts/make_fig_reach.py data/openalex/2026-11-10 [figures/fig_reach.pdf]
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
THOUSANDS = FuncFormatter(lambda v, _: f'{int(v):,}')

snap = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('figures/fig_reach.pdf')
INCOMPLETE = 2026
FIRST = 2002   # works dated before the SMOTE paper cannot cite it: dating or matching errors

if (snap / 'group_publication_year.json').exists():
    g = json.loads((snap / 'group_publication_year.json').read_text())['group_by']
    years = {int(x['key']): x['count'] for x in g}
else:
    years = {int(r['year']): int(r['citing_works']) for r in csv.DictReader(open(snap / 'citing_by_year.csv'))}
if (snap / 'group_primary_topic_field_id.json').exists():
    g = json.loads((snap / 'group_primary_topic_field_id.json').read_text())['group_by']
    g = sorted(g, key=lambda x: -x['count'])
    fields = [(x['key_display_name'], x['count']) for x in g[:6]]
    fields.append((f'{len(g) - 6} further fields', sum(x['count'] for x in g[6:])))
else:
    fields = [(r['field'], int(r['citing_works'])) for r in csv.DictReader(open(snap / 'citing_by_field.csv'))]

INK, MUTED, GRID = '#222222', '#666666', '#d9d9d9'
plt.rcParams.update({'font.family': 'serif', 'font.size': 8.5, 'axes.edgecolor': MUTED,
                     'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'hatch.linewidth': 0.6, 'pdf.fonttype': 42})
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={'width_ratios': [1.25, 1]})

ys = [y for y in sorted(years) if y >= FIRST]
for y in ys:
    hatch = '////' if y == INCOMPLETE else None
    a.bar(y, years[y], width=0.72, color='white' if hatch else '#4d4d4d',
          edgecolor='#4d4d4d', hatch=hatch, linewidth=0.6)
a.set_xlim(FIRST - 0.8, max(ys) + 0.8)
a.set_xticks([2002, 2006, 2010, 2014, 2018, 2022, 2026])
a.set_ylabel('Citing works per year')
a.yaxis.set_major_formatter(THOUSANDS)
a.yaxis.grid(True, color=GRID, linewidth=0.5)
a.set_axisbelow(True)
for s in ('top', 'right'):
    a.spines[s].set_visible(False)
a.annotate('2018: year of the\n15-year review', xy=(2018, years[2018]), xytext=(2008.2, 3600),
           fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.6))
a.set_title('(a) By year of publication', loc='left', fontsize=9, color=INK)

names = [n for n, _ in fields][::-1]
vals = [v for _, v in fields][::-1]
tot = sum(vals)
b.barh(range(len(vals)), vals, height=0.62, color='#4d4d4d', edgecolor='#4d4d4d', linewidth=0.6)
b.set_yticks(range(len(vals)))
b.set_yticklabels([n.replace('Biochemistry, Genetics and Molecular Biology', 'Biochem., Genetics, Mol. Biol.')
                   .replace('Business, Management and Accounting', 'Business, Mgmt., Accounting') for n in names],
                  fontsize=7.5, color=INK)
for i, v in enumerate(vals):
    b.text(v + tot * 0.01, i, f'{v:,}', va='center', fontsize=7, color=INK)
b.set_xlim(0, max(vals) * 1.22)
b.set_xlabel('Citing works')
b.xaxis.set_major_formatter(THOUSANDS)
b.xaxis.grid(True, color=GRID, linewidth=0.5)
b.set_axisbelow(True)
for s in ('top', 'right'):
    b.spines[s].set_visible(False)
b.set_title('(b) By field of primary topic', loc='left', fontsize=9, color=INK)

fig.tight_layout(w_pad=1.5)
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out)
fig.savefig(out.with_suffix('.png'), dpi=200)
print(f'wrote {out}; years {ys[0]}-{ys[-1]} sum {sum(years[y] for y in ys):,}; fields sum {tot:,}')
