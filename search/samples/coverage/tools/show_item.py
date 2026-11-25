#!/usr/bin/env python3
"""Show the record K (1-based) of batch NNN of a coding project, with the path of its text file if there is one.
Usage: python3 -I show_item.py PROJECT NNN K      (PROJECT: coverage or useaudit)"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import ROOT

csv.field_size_limit(10**9)
proj, nnn, k = sys.argv[1], sys.argv[2].zfill(3), int(sys.argv[3])
R = Path(ROOT[proj])
rows = list(csv.DictReader(open(R / f'batches/batch{nnn}.csv', encoding='utf-8')))
r = rows[k - 1]
clean = lambda s: re.sub(r'\s+', ' ', s or '').strip()
print(f'=== record {k} of {len(rows)} in batch {nnn}: {r["rec"]} | {r["year"]} | {clean(r["venue"])[:100]} | DOI {r["doi"] or "-"}')
print('TITLE: ' + clean(r['title']))
print('ABSTRACT: ' + (clean(r['abstract']) or '[no abstract]'))
t = R / 'text' / f'{r["rec"]}.txt'
if t.exists():
    n = sum(1 for _ in open(t, encoding='utf-8'))
    print(f'FULL TEXT: {t} ({n} lines, {t.stat().st_size} bytes). Read it with the Read tool, in parts if it is long.')
else:
    print('FULL TEXT: none (code from the title and abstract)')
