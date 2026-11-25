#!/usr/bin/env python3
"""Check coded rows and append them to out/batchNNN_coded.csv of a coding project.
Usage: python3 -I add_codes.py PROJECT NNN chunk.json     (append; the rows must continue the batch in order)
       python3 -I add_codes.py PROJECT NNN --status       (rows done and the next record)"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import ROOT, SCHEMA

csv.field_size_limit(10**9)
proj, nnn = sys.argv[1], sys.argv[2].zfill(3)
R, SC = Path(ROOT[proj]), SCHEMA[proj]
cols = list(SC)
batch = [r['rec'] for r in csv.DictReader(open(R / f'batches/batch{nnn}.csv', encoding='utf-8'))]
out = R / f'out/batch{nnn}_coded.csv'
done = list(csv.DictReader(open(out, encoding='utf-8'))) if out.exists() else []


def status():
    nxt = len(done) + 1
    print(f'{proj} batch {nnn}: {len(done)} of {len(batch)} records coded')
    print('no records remain' if nxt > len(batch) else f'next record: {nxt} (rec {batch[nxt - 1]})')


if sys.argv[3] == '--status':
    status(); sys.exit(0)
try:
    chunk = json.load(open(sys.argv[3], encoding='utf-8'))
except Exception as e:
    sys.exit(f'ERROR: not valid JSON ({e}); nothing appended')
if isinstance(chunk, dict):
    chunk = [chunk]
errors, rows = [], []
for k, o in enumerate(chunk):
    pos = len(done) + k
    if not isinstance(o, dict):
        errors.append(f'item {k + 1}: not an object'); continue
    miss = [c for c in cols if c not in o]
    extra = [c for c in o if c not in SC]
    if miss or extra:
        errors.append(f'item {k + 1}: missing {miss} unknown {extra}'); continue
    r = {c: ('' if o[c] is None else str(o[c])).strip() for c in cols}
    if pos >= len(batch):
        errors.append(f'item {k + 1}: the batch has only {len(batch)} records'); continue
    if r['rec'] != batch[pos]:
        errors.append(f'item {k + 1}: rec {r["rec"]}, but record {pos + 1} of the batch is {batch[pos]}')
    for c, rule in SC.items():
        v = r[c]
        if rule is None:
            continue
        if isinstance(rule, set):
            if v not in rule:
                errors.append(f'{r["rec"]} {c}: "{v}" not in {sorted(rule)}')
        elif isinstance(rule, tuple):
            items = [x.strip() for x in v.split(';') if x.strip()]
            if v != 'na' and (not items or any(x not in rule[1] for x in items)):
                errors.append(f'{r["rec"]} {c}: "{v}" must be na or items from {sorted(rule[1])} separated by ;')
            r[c] = v if v == 'na' else ';'.join(items)
        elif rule == 'int_nr_na':
            if not (v.isdigit() or v in ('nr', 'na')):
                errors.append(f'{r["rec"]} {c}: "{v}" must be an integer, nr or na')
        elif rule.startswith('text'):
            lim = int(rule[4:])
            if len(v.split()) > lim:
                errors.append(f'{r["rec"]} {c}: more than {lim} words')
    rows.append(r)
if errors:
    print('ERROR: nothing appended. Fix these and rerun:'); print('\n'.join(errors[:40])); sys.exit(1)
new = not out.exists()
with open(out, 'a', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    if new:
        w.writeheader()
    w.writerows(rows)
done += rows
print(f'appended {len(rows)} rows'); status()
