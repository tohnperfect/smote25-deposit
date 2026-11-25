#!/usr/bin/env python3
"""Check one chunk of facts and append it to out/batchNNN_facts.csv.
Usage: python3 -I add_rows.py NNN chunk.json     (append a chunk)
       python3 -I add_rows.py NNN --status        (counts so far and the next record to show)
The chunk must continue the batch in order: its first record is the next one not yet in the output."""
import collections
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
S = Path('/home/claude/work/rule_b')
COLS = ['rec', 'scheme', 'generator', 'presented', 'compared', 'task', 'confidence', 'reason']
ALLOWED = {'scheme': {'own', 'existing-parts', 'unclear'},
           'generator': {'classical', 'deep-generative', 'statistical', 'augmentation', 'none'},
           'presented': {'yes', 'no'}, 'compared': {'yes', 'no'},
           'task': {'classification', 'segmentation', 'regression-as-classes', 'survival', 'detection', 'continual',
                    'zero-shot', 'ranking', 'other'},
           'confidence': {'high', 'medium', 'low'}}

nnn = sys.argv[1].zfill(3)
batch = [r['rec'] for r in csv.DictReader(open(S / f'batches/batch{nnn}.csv', encoding='utf-8'))]
out = S / f'out/batch{nnn}_facts.csv'
done = list(csv.DictReader(open(out, encoding='utf-8'))) if out.exists() else []


def status():
    c = collections.Counter(r['scheme'] for r in done)
    nxt = len(done) + 1
    print(f'batch {nnn}: {len(done)} of {len(batch)} records done; own {c["own"]}, existing-parts {c["existing-parts"]}, '
          f'unclear {c["unclear"]}')
    print('no records remain' if nxt > len(batch) else f'next record to show: {nxt} (rec {batch[nxt - 1]})')


if sys.argv[2] == '--status':
    status()
    sys.exit(0)
try:
    chunk = json.load(open(sys.argv[2], encoding='utf-8'))
except Exception as e:
    sys.exit(f'ERROR: the chunk is not valid JSON ({e}); nothing appended')
if not isinstance(chunk, list) or not chunk:
    sys.exit('ERROR: the chunk must be a non-empty JSON array; nothing appended')
errors, rows = [], []
start = len(done)
for k, o in enumerate(chunk):
    pos = start + k
    if not isinstance(o, dict):
        errors.append(f'item {k + 1}: not an object'); continue
    missing = [c for c in COLS if c not in o]
    if missing:
        errors.append(f'item {k + 1}: missing keys {missing}'); continue
    r = {c: ('' if o[c] is None else str(o[c])).strip() for c in COLS}
    if pos >= len(batch):
        errors.append(f'item {k + 1}: the batch has only {len(batch)} records'); continue
    if r['rec'] != batch[pos]:
        errors.append(f'item {k + 1}: rec {r["rec"]} but record {pos + 1} of the batch is {batch[pos]} (keep batch order)')
    for f, ok in ALLOWED.items():
        if r[f] not in ok:
            errors.append(f'item {k + 1} ({r["rec"]}): {f} must be one of {sorted(ok)}')
    if not r['reason']:
        errors.append(f'item {k + 1} ({r["rec"]}): reason is empty')
    rows.append(r)
if errors:
    print('ERROR: nothing appended. Fix these and rerun:')
    print('\n'.join(errors[:30]))
    sys.exit(1)
new = not out.exists()
with open(out, 'a', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, COLS)
    if new:
        w.writeheader()
    w.writerows(rows)
done += rows
print(f'appended {len(rows)} rows')
status()
