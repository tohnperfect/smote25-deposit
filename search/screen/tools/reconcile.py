#!/usr/bin/env python3
"""Combine the first pass of the full screen with the blind second look at doubtful records (WP4, 11 Nov 2026), and
write the workbook for the person's check (D14). Team use only: the workbook holds licensed Scopus abstracts.

Rule: a record the first pass decided with high confidence (include or exclude) keeps that decision. Every other
record (unsure, or low or medium confidence) was screened again, blind; where both passes agree on include or
exclude, that is the result; where they differ or either says unsure, the record goes to the person ("to check").
Writes into OUT: screen_final.csv, screen_final_summary.json, SMOTE25_screening_check_2026-11-11.xlsx
Usage: python3 -I reconcile.py OUT
"""
import collections
import csv
import gzip
import json
import random
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

csv.field_size_limit(10**9)
OUT = Path(sys.argv[1])
OUT.mkdir(exist_ok=True)
FIRST = Path('/home/claude/work/screen_full/result/screen_all.csv')
SECOND = Path('/home/claude/work/screen_second')
RECORDS = Path('/home/claude/work/v06/data/search/2026-11-11/wp4_records_merged.csv.gz')

first = {r['rec']: r for r in csv.DictReader(open(FIRST, encoding='utf-8'))}
recs = {r['rec']: r for r in csv.DictReader(gzip.open(RECORDS, 'rt', encoding='utf-8'))}
second, missing = {}, []
for f in sorted((SECOND / 'batches').glob('batch*_to_screen.csv')):
    nnn = f.name[5:8]
    order = [r['rec'] for r in csv.DictReader(open(f, encoding='utf-8'))]
    o = SECOND / f'out/batch{nnn}_screened.csv'
    got = list(csv.DictReader(open(o, encoding='utf-8'))) if o.exists() else []
    if [r['rec'] for r in got] != order:
        missing.append(nnn)
        continue
    for r in got:
        second[r['rec']] = r
assert not missing, f'second look incomplete: {missing}'

rows = []
for rid, a in first.items():
    b = second.get(rid)
    if b is None:
        status = f"{a['decision']}_single_high"
    elif a['decision'] == b['decision'] and a['decision'] in ('include', 'exclude'):
        status = f"{a['decision']}_agreed"
    else:
        status = 'to_check'
    m = recs[rid]
    rows.append(dict(rec=rid, status=status, year=m['year'], title=m['title'], doi=m['doi'], venue=m['venue'],
                     doctype=m['doctype'], language=m['language'],
                     first_decision=a['decision'], first_code=a['reason_code'], first_confidence=a['confidence'],
                     first_reason=a['reason'], first_tags=a['tags'],
                     second_decision=b['decision'] if b else '', second_code=b['reason_code'] if b else '',
                     second_confidence=b['confidence'] if b else '', second_reason=b['reason'] if b else '',
                     abstract=m['abstract']))
cols = [c for c in rows[0] if c != 'abstract']
with open(OUT / 'screen_final.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols, extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)

# agreement on the doubtful records (both passes, three classes)
pairs = [(first[r]['decision'], second[r]['decision']) for r in second]
n = len(pairs)
po = sum(a == b for a, b in pairs) / n
ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
cross = collections.Counter(f'{a}->{b}' for a, b in pairs)
status = collections.Counter(r['status'] for r in rows)
summary = dict(records=len(rows), second_look=n, status=dict(status),
               doubtful_agreement=round(po, 3), doubtful_kappa=round((po - pe) / (1 - pe), 3), first_to_second=dict(cross),
               include_total=status['include_single_high'] + status['include_agreed'],
               exclude_total=status['exclude_single_high'] + status['exclude_agreed'],
               to_check=status['to_check'], seed_samples=20261114)
json.dump(summary, open(OUT / 'screen_final_summary.json', 'w'), indent=1)

# workbook for the person's check
rnd = random.Random(20261114)
inc = [r for r in rows if r['status'] in ('include_single_high', 'include_agreed')]
exc = [r for r in rows if r['status'] in ('exclude_single_high', 'exclude_agreed')]
inc_sample = set(r['rec'] for r in rnd.sample(inc, min(300, len(inc))))
exc_sample = rnd.sample(exc, min(300, len(exc)))
wcols = ['rec', 'status', 'year', 'title', 'abstract', 'doi', 'venue', 'doctype', 'language',
         'first_decision', 'first_code', 'first_confidence', 'first_reason',
         'second_decision', 'second_code', 'second_confidence', 'second_reason', 'person_decision', 'person_note']
wb = Workbook()
ws = wb.active
ws.title = 'README'
for line in [
        'SMOTE25 systematic search: records for the person\'s check (decision D14), 11 November 2026. Team use only (Scopus abstracts are licensed).',
        'Pass 1: separate AI sessions screened all 22,426 records under SCREENING_CODEBOOK.md v1.1 (title and abstract only).',
        'Pass 2: separate AI sessions screened again, blind, every record that pass 1 marked unsure or decided with low or medium confidence.',
        'Sheet to_check: the passes disagree or one says unsure. Sheet includes: every include (column sample300 marks a seeded random 300, seed 20261114).',
        'Sheet exclusions_sample: a seeded random 300 of the exclusions. Write include, exclude or unsure in person_decision, with a note where useful.',
        'Codes: I1-new-variant, I1-hybrid, I1-generative, I1-multiclass, I1-other; E1 applies existing resampling; E2 not classification; E-NOGEN no synthetic examples;',
        'E-REVIEW review or front matter; E-COMPARE comparison of existing methods; E-LANG not English; U-new-or-applied, U-no-abstract, U-other.']:
    ws.append([line])
ws.column_dimensions['A'].width = 160


def sheet(name, data, extra=None):
    s = wb.create_sheet(name)
    hdr = wcols + ([extra] if extra else [])
    s.append(hdr)
    for c in s[1]:
        c.font = Font(bold=True)
    for r in data:
        s.append([r.get(c, '') for c in wcols] + ([('yes' if r['rec'] in inc_sample else '')] if extra else []))
    for col, wdt in zip('ABCDEFGHIJKLMNOPQRST', [9, 18, 6, 60, 90, 22, 30, 14, 10, 10, 16, 10, 50, 10, 16, 10, 50, 14, 30, 10]):
        s.column_dimensions[col].width = wdt
    for row in s.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=False, vertical='top')
    s.freeze_panes = 'B2'


sheet('to_check', [r for r in rows if r['status'] == 'to_check'])
sheet('includes', inc, extra='sample300')
sheet('exclusions_sample', exc_sample)
wb.save(OUT / 'SMOTE25_screening_check_2026-11-11.xlsx')
print(json.dumps(summary, indent=1))
