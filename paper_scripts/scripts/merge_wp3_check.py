#!/usr/bin/env python3
"""Merge the team lead's spot check of the WP3 AI adjudication (page "SMOTE25 WP3 Check", decision D31).

Input: the CSV the page exports (Summary and export: Download CSV or Copy CSV), one row per decision of every reviewer:
reviewer, group, form, paper, item, field, ai_adjudication, decision (agree or change), right_value, note, time, item_key.
Writes wp3/adjudication/WP3_spot_check_summary.json (per reviewer and group: items decided, agreed, changed; the
share of the drawn items, with the frames the draws came from) and wp3/adjudication/WP3_spot_check_changes.csv (every
change, for a session to apply to the *_adjudicated.csv files and rerun the scripts that depend on them).
The paper then reports, in Section 3.7, how many adjudications an author checked and how many were changed
(scripts/search_templates/k_wp3_spot.tex, v0.31).
Usage: python3 -I scripts/merge_wp3_check.py <export.csv> <v16_dir>
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXP, V = Path(sys.argv[1]), Path(sys.argv[2])
rec = json.load(open(V / 'wp3/check_page/records.json', encoding='utf-8'))
keys = {i['key']: i for i in rec['items']}
rows = list(csv.DictReader(open(EXP, encoding='utf-8-sig')))
bad = [r['item_key'] for r in rows if r['item_key'] not in keys]
assert not bad, f'STOP: rows for items the page does not hold: {bad[:5]}'
by = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    by[r['reviewer']][r['group']][r['decision']] += 1
# v0.31: also per group and form, the items the page holds and the decisions, so that the wording of Section 3.7
# (scripts/search_templates/k_wp3_spot.tex) can be checked against what was decided
items_gf = defaultdict(Counter)
for i in rec['items']:
    items_gf[i['group']][i['form']] += 1
dec_gf = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    dec_gf[r['group']][r['form']][r['decision']] += 1
summary = dict(items=len(keys), groups=rec['meta']['groups'], frames=rec['meta']['frames'], seeds=rec['meta']['seeds'],
               reviewers={rv: {g: dict(c) for g, c in gs.items()} for rv, gs in by.items()},
               totals={rv: dict(sum((c for c in gs.values()), Counter())) for rv, gs in by.items()},
               items_by_group_form={g: dict(c) for g, c in items_gf.items()},
               decided_by_group_form={g: {f: dict(c) for f, c in fs.items()} for g, fs in dec_gf.items()},
               changes=[r['item_key'] for r in rows if r['decision'] == 'change'],
               export=EXP.name)
out = V / 'wp3/adjudication'
(out / 'WP3_spot_check_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
ch = [r for r in rows if r['decision'] == 'change']
with open(out / 'WP3_spot_check_changes.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['item_key'])
    w.writeheader()
    w.writerows(ch)
print(json.dumps(summary['totals'], indent=1), f'\n{len(ch)} changes written to WP3_spot_check_changes.csv')
