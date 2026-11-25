#!/usr/bin/env python3
"""Merge the check of the page "SMOTE25 WP3 Count Check" (15 November 2026).

Input: the CSV the page exports (Summary and export: Download CSV or Copy CSV), one row per decision of every reviewer:
reviewer, group, form, paper, item, field, ai_adjudication, decision (agree or change), right_value, note, time, item_key;
and records.json rebuilt with scripts/build_wp3_count_check.py (the page's items; not kept in the draft because it
repeats the quotes).
Writes wp3/adjudication/WP3_count_check_summary.json (per reviewer and group: items decided, agreed, changed; the two
counts of Table 5 with the AI's values and with each reviewer's decisions; the requests to check, that is changes
without a value) and wp3/adjudication/WP3_count_check_changes.csv (every change). It changes no other file: a change
with a value is applied in wp3/adjudication/adjudicate_data_handling.py (the decision D of the paper and field, with
the note and "checked by an author, 15 Nov 2026" in decided_by), then wp3_summary.py, search_numbers.py,
render_search_text.py, the builds, check_numbers.py and build_ledger.py follow (wp3/count_check/README.md).
Usage: python3 -I scripts/merge_wp3_count_check.py <export.csv> <records.json> <draft_dir>
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXP, REC, V = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rec = json.load(open(REC, encoding='utf-8'))
items = {i['key']: i for i in rec['items']}
rows = list(csv.DictReader(open(EXP, encoding='utf-8-sig')))
bad = [r['item_key'] for r in rows if r['item_key'] not in items]
assert not bad, f'STOP: rows for items the page does not hold: {bad[:5]}'
wrong = [r['item_key'] for r in rows if r['ai_adjudication'] != items[r['item_key']]['adjudicated']]
assert not wrong, f'STOP: the export shows other AI values than records.json (rebuilt from other data?): {wrong[:5]}'
meta = rec['meta']
by = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    by[r['reviewer']][r['group']][r['decision']] += 1


def counts_for(decisions):
    """The two counts with the decisions of one reviewer (an undecided item, or a change without a value, keeps the AI's value)."""
    out = {}
    for g, c in meta['counts'].items():
        n = c['base_others']
        for i in rec['items']:
            if i['group'] != g:
                continue
            d = decisions.get(i['key'])
            v = d['right_value'] if d and d['decision'] == 'change' and d['right_value'] not in ('', 'see note') else i['adjudicated']
            n += v in meta['counts_as'][g]
        out[g] = dict(first_pass=c['first_pass'], after_adjudication=c['after'], with_decisions=n,
                      changes_the_paper=n != c['after'])
    return out


per = defaultdict(dict)
for r in rows:
    per[r['reviewer']][r['item_key']] = r
summary = dict(page='SMOTE25 WP3 Count Check', items=len(items), groups=meta['groups'], export=EXP.name,
               reviewers={rv: {g: dict(c) for g, c in gs.items()} for rv, gs in by.items()},
               undecided={rv: sorted(set(items) - set(d)) for rv, d in per.items()},
               counts={rv: counts_for(d) for rv, d in per.items()},
               changes=[r['item_key'] for r in rows if r['decision'] == 'change'],
               requests=[dict(item_key=r['item_key'], note=r['note']) for r in rows
                         if r['decision'] == 'change' and r['right_value'] in ('', 'see note')],
               flagged_on_the_page={i['key']: i['flag'] for i in rec['items'] if i.get('flag')})
out = V / 'wp3/adjudication'
(out / 'WP3_count_check_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
ch = [r for r in rows if r['decision'] == 'change']
with open(out / 'WP3_count_check_changes.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['item_key'])
    w.writeheader()
    w.writerows(ch)
print(json.dumps(dict(reviewers=summary['reviewers'], counts=summary['counts'], requests=summary['requests']), indent=1),
      f'\n{len(ch)} changes written to WP3_count_check_changes.csv')
