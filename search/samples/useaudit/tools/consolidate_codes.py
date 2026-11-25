#!/usr/bin/env python3
"""Merge the coded batches of a project into one coded.csv in the draft's data folder (last code of a record wins,
so a recode from a full text supplied later replaces the abstract-only code).
Usage: python3 -I consolidate_codes.py PROJECT DRAFT_DIR"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import ROOT, SCHEMA

csv.field_size_limit(10**9)
proj, draft = sys.argv[1], Path(sys.argv[2])
R = Path(ROOT[proj])
rows = {}
for f in sorted((R / 'out').glob('batch*_coded.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        r['batch'] = f.name[5:8]
        rows[r['rec']] = r
D = draft / 'data/search/screening_full_2026-11-11' / proj
D.mkdir(parents=True, exist_ok=True)
cols = list(SCHEMA[proj]) + ['batch']
with open(D / 'coded.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    for r in rows.values():
        w.writerow({c: r.get(c, '') for c in cols})
notes = [f'# Notes of the coding sessions ({proj})\n']
for f in sorted((R / 'out').glob('batch*_DONE.txt')):
    notes.append(f'\n## {f.name[:8]}\n\n' + f.read_text(encoding='utf-8').strip() + '\n')
(D / 'coder_notes.md').write_text(''.join(notes), encoding='utf-8')
print(proj, len(rows), 'coded rows')
