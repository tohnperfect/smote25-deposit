#!/usr/bin/env python3
"""v0.48 (item 3 of the re-evaluation of v0.46, approved by the team lead on 19 Nov 2026): 95% intervals with the paper
as the unit for two shares pooled over papers, since entries of one paper are not independent.
- wins: decided printed comparisons with plain SMOTE that the proposed method wins (Section 5, 79.0%), from
  data/d35/out/winloss_allmetric_rows.csv (in_analysis True, comparator_group "plain SMOTE", result win or loss);
- no_row: listed dataset entries with no row in the table that compares the proposed method with SMOTE (Section 5.6,
  19.4%), from the Data section's out/h3_entries.csv in the team repository (in_comparison False).
Cluster bootstrap: draw the papers with replacement, pool, 10,000 draws, seed 20261119, 2.5 and 97.5 percentiles.
Writes data/d35/out/cluster_ci.json and data/d35/out/cluster_ci_papers.csv (paper keys and counts only).
Usage: python3 -I scripts/cluster_ci.py <draft dir> <team repo>"""
import csv
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

D, T = Path(sys.argv[1]), Path(sys.argv[2])
B, SEED = 10000, 20261119


def boot(per):  # per: {paper: (num, den)}
    keys = sorted(per)
    rng = random.Random(SEED)
    vals = []
    for _ in range(B):
        s = [per[keys[rng.randrange(len(keys))]] for _ in keys]
        vals.append(100 * sum(a for a, _ in s) / sum(b for _, b in s))
    vals.sort()
    num, den = sum(a for a, _ in per.values()), sum(b for _, b in per.values())
    rates = [100 * a / b for a, b in per.values()]
    return {'papers': len(keys), 'num': num, 'den': den, 'share': round(100 * num / den, 1),
            'lo': round(vals[int(0.025 * B)], 1), 'hi': round(vals[int(0.975 * B) - 1], 1),
            'per_paper_min': round(min(rates), 1), 'per_paper_median': round(statistics.median(rates), 1),
            'per_paper_max': round(max(rates), 1), 'draws': B, 'seed': SEED}


wins = defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(D / 'data/d35/out/winloss_allmetric_rows.csv', encoding='utf-8-sig')):
    if r['in_analysis'] == 'True' and r['comparator_group'] == 'plain SMOTE' and r['result'] in ('win', 'loss'):
        wins[r['paper']][1] += 1
        wins[r['paper']][0] += r['result'] == 'win'
norow = defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(T / 'Data section/out/h3_entries.csv', encoding='utf-8-sig')):
    norow[r['paper_key']][1] += 1
    norow[r['paper_key']][0] += r['in_comparison'] == 'False'

out = {'wins': boot({k: tuple(v) for k, v in wins.items()}), 'no_row': boot({k: tuple(v) for k, v in norow.items()})}
_m = sorted((v[0] for v in norow.values()), reverse=True)
out['no_row'].update({'papers_with_any': sum(1 for x in _m if x > 0), 'top3_papers_sum': sum(_m[:3])})
assert (out['wins']['num'], out['wins']['den'], out['wins']['papers']) == (1102, 1395, 29), out['wins']
assert (out['no_row']['num'], out['no_row']['den'], out['no_row']['papers']) == (201, 1034, 43), out['no_row']
(D / 'data/d35/out/cluster_ci.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
with open(D / 'data/d35/out/cluster_ci_papers.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['measure', 'paper', 'num', 'den'])
    for name, per in (('wins', wins), ('no_row', norow)):
        for k in sorted(per):
            w.writerow([name, k, per[k][0], per[k][1]])
print(json.dumps(out))
