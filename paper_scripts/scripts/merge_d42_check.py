#!/usr/bin/env python3
"""Merge the team lead's spot check of the D42 adjudication (page "SMOTE25 Samples Check", decision D42).

Input: the CSV the page exports (Summary and export: Download CSV or Copy CSV), one row per decision of every reviewer:
reviewer, group, form, paper, item, field, ai_adjudication, decision (agree or change), right_value, note, time, item_key;
and the page's records.json (rebuilt with scripts/build_d42_check.py; not kept in the package, as it quotes the records).
Writes data/search/screening_full_2026-11-11/d42/spot_check_summary.json (per reviewer and group: items decided,
agreed, changed, with the frames and seeds of the draws) and d42/spot_check_changes.csv (every change: project, record,
field, the AI value and the right value). A session then applies the changes: it adds each, once checked, to
d42/spot_check_overrides.csv (project, rec, field, value, note) and reruns d42_compile.py, which lets an override
take precedence over the adjudication, then the chain from analyze_samples.py on. The paper reports,
in Sections 3.4 and 8.3 and the declarations, how many adjudications the team lead checked and how many he changed.
v0.37: `--round2` for the check of round 2 (page "SMOTE25 Samples Check, round 2", records.json built with
build_d42_check.py --round2): the two files go into d42/round2/, and its overrides into d42/round2/spot_check_overrides.csv.
v0.38: `--round3` likewise for round 3 (d42/round3/).
Usage: python3 -I scripts/merge_d42_check.py <export.csv> <records.json> <draft_dir> [--round2 | --round3]
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROUND2 = '--round2' in sys.argv[1:]
ROUND3 = '--round3' in sys.argv[1:]   # v0.38
EXP, REC, V = (Path(a) for a in sys.argv[1:] if a not in ('--round2', '--round3'))
rec = json.load(open(REC, encoding='utf-8'))
keys = {i['key']: i for i in rec['items']}
rows = list(csv.DictReader(open(EXP, encoding='utf-8-sig')))
bad = [r['item_key'] for r in rows if r['item_key'] not in keys]
assert not bad, f'STOP: rows for items the page does not hold: {bad[:5]}'
by = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    by[r['reviewer']][r['group']][r['decision']] += 1
# v0.27: per sample (form) as well, and the page's items per sample and group, for Sections 3.4 and 8.3
by_form = defaultdict(lambda: defaultdict(Counter))
for r in rows:
    by_form[keys[r['item_key']]['form']][r['group']][r['decision']] += 1
items_by_form = defaultdict(Counter)
for i in rec['items']:
    items_by_form[i['form']][i['group']] += 1
summary = dict(items=len(keys), groups=rec['meta']['groups'], frames=rec['meta']['frames'], seeds=rec['meta']['seeds'],
               reviewers={rv: {g: dict(c) for g, c in gs.items()} for rv, gs in by.items()},
               totals={rv: dict(sum((c for c in gs.values()), Counter())) for rv, gs in by.items()},
               items_by_form={f: dict(c) for f, c in items_by_form.items()},
               decided_by_form={f: {g: dict(c) for g, c in gs.items()} for f, gs in by_form.items()},
               records_md5=__import__('hashlib').md5(REC.read_bytes()).hexdigest())
out = V / 'data/search/screening_full_2026-11-11/d42' / ('round2' if ROUND2 else 'round3' if ROUND3 else '')
assert ROUND2 == all(k.startswith('r2_') for k in keys), 'STOP: the records are not those of this round'
assert ROUND3 == all(k.startswith('r3_') for k in keys), 'STOP: the records are not those of this round'
(out / 'spot_check_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
ch = []
for r in rows:
    if r['decision'] != 'change':
        continue
    it = keys[r['item_key']]
    proj = 'useaudit' if it['form'] == 'Use audit' else 'coverage'
    ch.append(dict(reviewer=r['reviewer'], group=r['group'], project=proj, rec=it['item'], field=it['field'],
                   ai_value=it['adjudicated'], right_value=r['right_value'], note=r['note'], item_key=r['item_key']))
with open(out / 'spot_check_changes.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['reviewer', 'group', 'project', 'rec', 'field', 'ai_value', 'right_value', 'note',
                                       'item_key'])
    w.writeheader()
    w.writerows(ch)
print(json.dumps(summary['totals'], indent=1), f'\n{len(ch)} changes written to spot_check_changes.csv')
