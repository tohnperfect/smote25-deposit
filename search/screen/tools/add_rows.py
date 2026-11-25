#!/usr/bin/env python3
"""Check one chunk of screening decisions and append it to out/batchNNN_screened.csv.
Usage: python3 -I add_rows.py NNN chunk.json     (append a chunk)
       python3 -I add_rows.py NNN --status        (counts so far and the next record to show)
The chunk must continue the batch in order: its first record is the next one not yet in the output."""
import collections
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
S = Path('/home/claude/work/screen_full')
COLS = ['rec', 'decision', 'reason_code', 'reason', 'quote', 'tags', 'confidence']
CODES = {'include': {'I1-new-variant', 'I1-hybrid', 'I1-generative', 'I1-multiclass', 'I1-other'},
         'exclude': {'E1', 'E2', 'E-NOGEN', 'E-REVIEW', 'E-COMPARE', 'E-LANG'},
         'unsure': {'U-new-or-applied', 'U-no-abstract', 'U-other'}}
TAGS = {'generative', 'comparison', 'multiclass', 'deep-learning', 'image', 'text', 'time-series', 'medical',
        'no-abstract', 'front-matter-in-scope'}

nnn = sys.argv[1].zfill(3)
batch = [r['rec'] for r in csv.DictReader(open(S / f'batches/batch{nnn}_to_screen.csv', encoding='utf-8'))]
out = S / f'out/batch{nnn}_screened.csv'
done = list(csv.DictReader(open(out, encoding='utf-8'))) if out.exists() else []


def status():
    c = collections.Counter(r['decision'] for r in done)
    nxt = len(done) + 1
    print(f'batch {nnn}: {len(done)} of {len(batch)} records done; include {c["include"]}, unsure {c["unsure"]}, '
          f'exclude {c["exclude"]}')
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
    if r['decision'] not in CODES:
        errors.append(f'item {k + 1} ({r["rec"]}): decision must be include, exclude or unsure')
    elif r['reason_code'] not in CODES[r['decision']]:
        errors.append(f'item {k + 1} ({r["rec"]}): reason_code {r["reason_code"]} is not valid for {r["decision"]}')
    if r['confidence'] not in ('high', 'medium', 'low'):
        errors.append(f'item {k + 1} ({r["rec"]}): confidence must be high, medium or low')
    tags = [t.strip() for t in r['tags'].split(';') if t.strip()]
    bad = [t for t in tags if t not in TAGS]
    if bad:
        errors.append(f'item {k + 1} ({r["rec"]}): unknown tags {bad}')
    r['tags'] = ';'.join(tags)
    if len(r['quote'].split()) > 25:
        errors.append(f'item {k + 1} ({r["rec"]}): quote has more than 25 words')
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
