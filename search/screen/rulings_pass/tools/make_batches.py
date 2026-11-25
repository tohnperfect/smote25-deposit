#!/usr/bin/env python3
"""Batches of the records that the screen includes, for the pass that records the facts of rulings B, B2 and C.
Order: a SHA-256 hash of (seed, record id); 15 batches of near-equal size.
Usage: python3 -I make_batches.py <draft dir> <out dir> [seed]"""
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
draft, out = Path(sys.argv[1]), Path(sys.argv[2])
seed = sys.argv[3] if len(sys.argv) > 3 else '20261118'
dec = list(csv.DictReader(open(draft / 'data/search/screening_full_2026-11-11/decisions/screen_decisions.csv', encoding='utf-8')))
inc = [r['rec'] for r in dec if r['decision'] == 'include']
with gzip.open(draft / 'data/search/2026-11-11/wp4_records_merged.csv.gz', 'rt', encoding='utf-8') as fh:
    recs = {r['rec']: r for r in csv.DictReader(fh)}
order = sorted(inc, key=lambda r: hashlib.sha256(f'{seed}:{r}'.encode()).hexdigest())
n = 15
size = -(-len(order) // n)
cols = ['rec', 'year', 'doctype', 'language', 'venue', 'title', 'abstract', 'keywords']
manifest = {'seed': seed, 'records': len(order), 'batches': {}}
(out / 'batches').mkdir(parents=True, exist_ok=True)
for b in range(n):
    part = order[b * size:(b + 1) * size]
    nnn = f'{b + 1:03d}'
    with open(out / f'batches/batch{nnn}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(recs[r] for r in part)
    manifest['batches'][nnn] = part
json.dump(manifest, open(out / 'rule_b_manifest_PRIVATE.json', 'w'), indent=0)
print({k: len(v) for k, v in manifest['batches'].items()}, sum(len(v) for v in manifest['batches'].values()))
