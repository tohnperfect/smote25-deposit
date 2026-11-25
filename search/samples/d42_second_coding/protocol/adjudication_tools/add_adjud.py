#!/usr/bin/env python3
"""Check adjudications and append them to out/adjNNN_decisions.csv.
Usage: python3 -I add_adjud.py NNN chunk.json     (a JSON array of objects: item, decision, value, reason, confidence)
       python3 -I add_adjud.py NNN --status
decision: A or B (the code the codebook supports) or other (then value must be a valid code for the field);
reason: at most 40 words, with where in the text; confidence: high, medium or low."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/claude/work/d42/tools')
from schema import SCHEMA  # noqa: E402

csv.field_size_limit(10**9)
A = Path('/home/claude/work/d42/adjudication')
nnn = sys.argv[1].zfill(3)
items = {r['item']: r for r in csv.DictReader(open(A / f'batches/adj{nnn}.csv', encoding='utf-8'))}
out = A / f'out/adj{nnn}_decisions.csv'
done = {r['item']: r for r in csv.DictReader(open(out, encoding='utf-8'))} if out.exists() else {}


def status():
    left = [k for k in items if k not in done]
    print(f'adjudication batch {nnn}: {len(done)} of {len(items)} items decided' +
          (f'; next: {left[0]} ({items[left[0]]["project"]} {items[left[0]]["rec"]} {items[left[0]]["field"]})' if left else '; none left'))


if sys.argv[2] == '--status':
    status(); sys.exit(0)
try:
    chunk = json.load(open(sys.argv[2], encoding='utf-8'))
except Exception as e:
    sys.exit(f'ERROR: not valid JSON ({e}); nothing appended')
chunk = [chunk] if isinstance(chunk, dict) else chunk
errors, rows = [], []
for o in chunk:
    if not isinstance(o, dict) or set(o) != {'item', 'decision', 'value', 'reason', 'confidence'}:
        errors.append(f'{o}: keys must be exactly item, decision, value, reason, confidence'); continue
    o = {k: ('' if v is None else str(v)).strip() for k, v in o.items()}
    it = items.get(o['item'])
    if not it:
        errors.append(f'{o["item"]}: no such item in batch {nnn}'); continue
    if o['item'] in done or any(r['item'] == o['item'] for r in rows):
        errors.append(f'{o["item"]}: already decided'); continue
    if o['decision'] not in ('A', 'B', 'other'):
        errors.append(f'{o["item"]}: decision must be A, B or other')
    if o['decision'] == 'other':
        rule = SCHEMA[it['project']].get(it['field'])
        v = o['value']
        ok = True
        if isinstance(rule, set):
            ok = v in rule
        elif isinstance(rule, tuple):
            xs = [x.strip() for x in v.split(';') if x.strip()]
            ok = v == 'na' or (xs and all(x in rule[1] for x in xs))
            o['value'] = v if v == 'na' else ';'.join(xs)
        elif rule == 'int_nr_na':
            ok = v.isdigit() or v in ('nr', 'na')
        if not ok:
            errors.append(f'{o["item"]}: value "{v}" is not a valid code for {it["field"]}')
    elif o['value'] not in ('', it['code_' + o['decision']]):
        errors.append(f'{o["item"]}: with decision {o["decision"]} leave value empty (or give code {o["decision"]} itself)')
    if len(o['reason'].split()) > 40 or not o['reason']:
        errors.append(f'{o["item"]}: reason must have 1 to 40 words')
    if o['confidence'] not in ('high', 'medium', 'low'):
        errors.append(f'{o["item"]}: confidence must be high, medium or low')
    rows.append(o)
if errors:
    print('ERROR: nothing appended. Fix these and rerun:'); print('\n'.join(errors[:40])); sys.exit(1)
new = not out.exists()
with open(out, 'a', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, ['item', 'decision', 'value', 'reason', 'confidence'])
    if new:
        w.writeheader()
    w.writerows(rows)
done.update({r['item']: r for r in rows})
print(f'appended {len(rows)}'); status()
