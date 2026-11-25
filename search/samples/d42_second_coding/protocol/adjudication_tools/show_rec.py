#!/usr/bin/env python3
"""Show one record of the D42 samples: title, abstract and the path of its full text if the coders had one.
Usage: python3 -I show_rec.py PROJECT REC      (PROJECT: coverage or useaudit)"""
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)
D = Path('/home/claude/work/d42')
proj, rec = sys.argv[1], sys.argv[2]
for b in sorted((D / proj / 'batches').glob('batch*.csv')):
    for r in csv.DictReader(open(b, encoding='utf-8')):
        if r['rec'] == rec:
            clean = lambda s: re.sub(r'\s+', ' ', s or '').strip()
            print(f'=== {proj} {rec} | {r["year"]} | {clean(r["venue"])[:100]} | DOI {r["doi"] or "-"}')
            print('TITLE: ' + clean(r['title']))
            print('ABSTRACT: ' + (clean(r['abstract']) or '[no abstract]'))
            t = D / proj / 'text' / f'{rec}.txt'
            if t.exists():
                n = sum(1 for _ in open(t, encoding='utf-8'))
                print(f'FULL TEXT: {t} ({n} lines). Both coders read it; read it with the Read tool, in parts if long.')
            else:
                print('FULL TEXT: none (both coders coded from the title and abstract)')
            sys.exit(0)
sys.exit(f'no record {rec} in {proj}')
