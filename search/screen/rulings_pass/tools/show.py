#!/usr/bin/env python3
"""Show records FIRST to LAST (1-based, batch order) of batch NNN. Usage: python3 -I show.py NNN FIRST LAST"""
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)
S = Path('/home/claude/work/rule_b')
nnn, first, last = sys.argv[1].zfill(3), int(sys.argv[2]), int(sys.argv[3])
rows = list(csv.DictReader(open(S / f'batches/batch{nnn}.csv', encoding='utf-8')))
last = min(last, len(rows))
clean = lambda s: re.sub(r'\s+', ' ', s or '').strip()
for i in range(first, last + 1):
    r = rows[i - 1]
    print(f'=== {i}/{len(rows)}  {r["rec"]}  | {r["year"]} | {clean(r["doctype"])} | language: {clean(r["language"]) or "?"} | {clean(r["venue"])[:90]}')
    print('TITLE: ' + clean(r['title']))
    print('ABSTRACT: ' + (clean(r['abstract']) or '[no abstract]'))
    if clean(r['keywords']):
        print('KEYWORDS: ' + clean(r['keywords'])[:400])
    print()
