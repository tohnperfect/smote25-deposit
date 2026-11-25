#!/usr/bin/env python3
"""Rebuild the batch files of the screening (WP4, 11 Nov 2026) from the merged records and a manifest.

The batch files hold licensed Scopus abstracts, so they are not kept in the draft package; this script writes them
again, record for record and in the same order, from data/search/2026-11-11/wp4_records_merged.csv.gz.
Manifests: first_pass/screen_manifest_PRIVATE.json (113 batches, seed 20261112) and
second_look/second_manifest_PRIVATE.json (22 batches, seed 20261113, the doubtful records of the first pass).
Usage: python3 -I make_batches.py RECORDS.csv.gz MANIFEST.json OUTDIR
"""
import csv
import gzip
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
COLS = ['rec', 'year', 'title', 'abstract', 'venue', 'doctype', 'language', 'keywords']
recs = {r['rec']: r for r in csv.DictReader(gzip.open(sys.argv[1], 'rt', encoding='utf-8'))}
man = json.load(open(sys.argv[2], encoding='utf-8'))
out = Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
for nnn, ids in sorted(man['batches'].items()):
    with open(out / f'batch{nnn}_to_screen.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, COLS, extrasaction='ignore')
        w.writeheader()
        for i in ids:
            w.writerow(recs[i])
print(len(man['batches']), 'batches,', sum(len(v) for v in man['batches'].values()), 'records')
