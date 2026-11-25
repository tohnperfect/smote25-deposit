#!/usr/bin/env python3
"""Figure: PRISMA 2020 flow of the systematic search, the coverage sample and the use audit (WP4, WP5).

Reads data/search/screening_full_2026-11-11/decisions/search_numbers.json (scripts/search_numbers.py) and writes
figures/fig_prisma.pdf. Greyscale; every number comes from that file.
Usage: python3 -I scripts/make_fig_prisma.py DRAFT_DIR
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

R = Path(sys.argv[1])
N = json.load(open(R / 'data/search/screening_full_2026-11-11/decisions/search_numbers.json', encoding='utf-8'))
g = lambda k: N.get(k, '?')

plt.rcParams.update({'font.family': 'serif', 'font.size': 7})
fig, ax = plt.subplots(figsize=(6.6, 5.9))
ax.set_xlim(0, 100)
ax.set_ylim(10, 99)
ax.axis('off')


def box(x, y, w, h, text, fill='white', weight='normal'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4,rounding_size=1.2', fc=fill, ec='black', lw=0.6))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=6.6, fontweight=weight, linespacing=1.25)


def arrow(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='-|>', lw=0.6, color='black', shrinkA=0, shrinkB=0))


def band(y, h, label):
    ax.add_patch(FancyBboxPatch((0.5, y), 4.5, h, boxstyle='round,pad=0.2,rounding_size=1', fc='0.85', ec='none'))
    ax.text(2.75, y + h / 2, label, rotation=90, ha='center', va='center', fontsize=7, fontweight='bold')


L, W, RX, RW = 8, 44, 58, 41
band(84, 14, 'Identification')
band(56, 26, 'Screening')
band(11, 43, 'Full text and coding')

box(L, 86, W, 10, f"Records identified\nScopus (n = {g('id_scopus')}), OpenAlex (n = {g('id_openalex')}),\narXiv (n = {g('id_arxiv')}); together n = {g('id_total')}")
box(RX, 88, RW, 6, f"Duplicates removed (n = {g('id_duplicates')})")
arrow(L + W, 91, RX, 91)
FINAL = str(N.get('final_merge', 0)) == '1'   # v0.15: after the final merge (D28)
# v0.38: the authors decided not to check the screen record by record (Last Pass, 16 Nov 2026), so no step of theirs is
# added to the screen box; at the final merge the records left unsure are excluded (E-UNSURE)
sh = 8
arrow(L + W / 2, 86, L + W / 2, 72 + sh)

box(L, 72, W, sh, f"Records screened on title and abstract\n(n = {g('screened')}): AI sessions in three looks,\nan independent AI check, a rulings pass")
exc = [('E1', 'applies existing resampling (E1)'), ('E-COMPARE', 'compares existing methods'),
       ('E-NOGEN', 'creates no synthetic examples'), ('E-LANG', 'not in English'), ('E-REVIEW', 'review'),
       ('E2', 'not classification (E2)'), ('E-WITHDRAWN', 'removed by its repository'), ('E-OTHER', 'other reason (E-OTHER)'),
       ('E-UNSURE', 'left unsure (E-UNSURE)')]   # v0.15: D28, only at the final merge
lines = '\n'.join(f"{t}: {g('excluded_' + c)}" for c, t in exc if ('excluded_' + c) in N)
if N.get('ruleb_excluded', '0') != '0':   # v0.12: the E1 exclusions that the rulings pass added
    lines = lines.replace(f"(E1): {g('excluded_E1')}", f"(E1): {g('excluded_E1')}\n(of them by rulings B and B2: {g('ruleb_excluded')})", 1)
if lines.count('\n') >= 9:   # ten lines do not fit the box: two short ones share a line
    lines = lines.replace('\nreview: ', '; review: ', 1)
box(RX, 61, RW, 24.5, f"Records excluded (n = {g('excluded')})\n{lines}")
arrow(L + W, 76, RX, 76)
if g('unsure_to_fulltext') != '0':   # before the final merge (D28)
    passing = (f"included {g('included')}\nunsure, for the authors' check: {g('unsure_to_fulltext')}"
               + (f"\n(of them by rulings B and B2: {g('ruleb_unsure')})" if N.get('ruleb_unsure', '0') != '0' else ''))
else:
    passing = 'all included'
py, ph = (56.5, 10.5) if passing.count('\n') >= 2 else (58, 8)
arrow(L + W / 2, 72, L + W / 2, py + ph)
box(L, py, W, ph, f"Records passing the screen (n = {g('passed')})\n{passing}")
box(RX, 49.5, RW, 9.5, f"Use audit: {g('use_drawn')} records excluded under E1,\ndrawn at random by period, coded from title\nand abstract; {g('use_ft_target')} also from the full text\n(obtained: {g('use_ft_obtained')})")
arrow(RX + RW / 2, 61, RX + RW / 2, 59)
arrow(L + W / 2, py, L + W / 2, 51)

box(L, 44, W, 7, f"Coverage sample: {g('cov_drawn')} drawn at random,\n{g('cov_per_period')} per period of the evaluation audit")
box(RX, 40, RW, 6, f"Full text not obtained (n = {g('cov_not_retrieved')})")
arrow(L + W, 47.5, RX, 43)
arrow(L + W / 2, 44, L + W / 2, 37)

box(L, 30, W, 7, f"Full texts assessed for eligibility (n = {g('cov_assessed')})")
xl = '\n'.join(f'{k}: {v}' for k, v in N.get('cov_excluded_reasons', {}).items()) if isinstance(N.get('cov_excluded_reasons'), dict) else ''
box(RX, 22, RW, 13, f"Excluded at full text (n = {g('cov_excluded')})" + ('\n' + xl if xl else ''))
arrow(L + W, 33.5, RX, 28.5)
arrow(L + W / 2, 30, L + W / 2, 22)
box(L, 13, W, 9, f"Coded for the coverage test (n = {g('cov_eligible')})\nCore {g('cov_core')}, Partial {g('cov_partial')}, Not counted {g('cov_notcounted')}", weight='bold')

fig.savefig(R / 'figures/fig_prisma.pdf', bbox_inches='tight', pad_inches=0.02)
print('wrote figures/fig_prisma.pdf')
