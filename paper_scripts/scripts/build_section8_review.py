#!/usr/bin/env python3
"""Build records.json of the review page for the authors' checks of Section 8 (decision D41 of 12 November 2026).

Three AI first passes of WP5, each checked blind by an author on the page "SMOTE25 Section 8 Check":
  harm  the harm search (wp5/harm_search/): all 27 includes and 49 unsure records, and 50 of the 353 exclusions
        drawn at random (seed 20261118); Section 8.5, Table 16 and online appendix S6.
  case  the case search on query O1 (wp5/case_search/): all 141 includes and 23 unsure records, and 40 of the 187
        exclusions drawn at random (seed 20261119); for Section 8.4.
  tags  the 30 works of the blind subsample of the reach tags (wp5/wp5_tag_check_blind.xlsx); Section 8.1.
Within each check the records come in one random order (seed 20261120), so the queue gives away no AI decision; the
page shows the AI's coding of a record only after the author has decided it.
Every draw ranks records by a hash of (seed, id), as the samples of the screen are drawn. Keys: h<PMID> (harm),
c<PMID> (case) and the OpenAlex id (tags); a PMID found by both searches is checked once in each.
Usage: python3 -I scripts/build_section8_review.py DRAFT_DIR OUTDIR [draft label]
Writes OUTDIR/records.json. It holds PubMed abstracts (publishers' text): team use only, never deposited; the page is
shared by name only. The script rebuilds it byte for byte.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

import openpyxl

csv.field_size_limit(10**9)
R, OUT = Path(sys.argv[1]), Path(sys.argv[2])
LABEL = sys.argv[3] if len(sys.argv) > 3 else 'v0.16'
SEED_HARM, SEED_CASE, SEED_ORDER = 20261118, 20261119, 20261120
N_HARM_EXC, N_CASE_EXC = 50, 40


def rank(seed, key):
    return hashlib.sha256(f'{seed}:{key}'.encode()).hexdigest()


def clean(s):
    return ' '.join(str(s or '').split())


records, checks = {}, {}

# ---------- harm search ----------
H = R / 'wp5/harm_search'
hrows = list(csv.DictReader(open(H / 'harm_search_records.csv', encoding='utf-8')))
habs = {r['pmid']: r for r in json.load(open(H / 'work/records.json', encoding='utf-8'))}
frame = {d: [r for r in hrows if r['decision'] == d] for d in ('include', 'unsure', 'exclude')}
drawn = frame['include'] + frame['unsure'] + sorted(frame['exclude'], key=lambda r: rank(SEED_HARM, r['pmid']))[:N_HARM_EXC]
for r in drawn:
    a = habs[r['pmid']]
    records['h' + r['pmid']] = {
        'k': 'harm', 'id': r['pmid'], 't': clean(r['title']), 'v': clean(r['journal']), 'y': r['year'], 'doi': r['doi'],
        'pt': clean(r['publication_types']), 'q': clean(r['queries']), 'a': clean(a.get('abstract', '')),
        'ai': {'d': r['decision'], 'code': r['code'], 'harms': r['harms'], 'comparison': r['comparison'],
               'finding': r['finding'], 'data': r['data'], 'reason': clean(r['reason']), 'quote': clean(r['quote']),
               'conf': r['confidence']}}
checks['harm'] = {'n': len(drawn), 'order': sorted(('h' + r['pmid'] for r in drawn), key=lambda k: rank(SEED_ORDER, 'harm' + k[1:])),
                  'frame': {d: len(v) for d, v in frame.items()},
                  'drawn': {'include': len(frame['include']), 'unsure': len(frame['unsure']), 'exclude': N_HARM_EXC},
                  'seed_sample': SEED_HARM}

# ---------- case search ----------
C = R / 'wp5/case_search'
crows = list(csv.DictReader(open(C / 'case_search_records.csv', encoding='utf-8')))
cparsed = {r['pmid']: r for r in json.load(open(C / 'work/records_parsed.json', encoding='utf-8'))['records']}
beyond_words = ('external', 'prospective validation', 'prospective external validation', 'temporal', 'deploy')
dca_words = ('decision curve', 'net benefit', 'net-benefit', 'clinical impact', 'clinical utility')


def group(r):   # as scripts/build_records_csv.py of the case search assigns them
    if r['decision'] != 'include':
        return ''
    e = r['evaluation_type'].lower()
    if any(w in e for w in beyond_words):
        return 'A'
    if any(w in e for w in dca_words):
        return 'B'
    raise SystemExit(f'include {r["pmid"]} without a recognized evaluation')


def abstract(p):
    secs = p.get('abstract_sections') or []
    if isinstance(secs, list) and secs:
        return clean(' '.join((f"{s.get('label')}: " if s.get('label') else '') + s.get('text', '') for s in secs))
    return clean(p.get('abstract', ''))


frame = {d: [r for r in crows if r['decision'] == d] for d in ('include', 'unsure', 'exclude')}
drawn = frame['include'] + frame['unsure'] + sorted(frame['exclude'], key=lambda r: rank(SEED_CASE, r['pmid']))[:N_CASE_EXC]
for r in drawn:
    p = cparsed[r['pmid']]
    records['c' + r['pmid']] = {
        'k': 'case', 'id': r['pmid'], 't': clean(r['title']), 'v': clean(r['journal']), 'y': r['year'],
        'doi': clean(p.get('doi', '')), 'pt': clean(p.get('publication_types', '')), 'a': abstract(p),
        'ai': {'d': r['decision'], 'group': group(r), 'cmp': r['compares_no_resampling'], 'resampling': clean(r['resampling']),
               'evaluation': clean(r['evaluation_type']), 'outcome': clean(r['outcome_reported']),
               'reason': clean(r['reason']), 'quote': clean(r['quote'])}}
assert sum(1 for k, v in records.items() if v['k'] == 'case') == len(drawn), 'a case PMID drawn twice'
checks['case'] = {'n': len(drawn), 'order': sorted(('c' + r['pmid'] for r in drawn), key=lambda k: rank(SEED_ORDER, 'case' + k[1:])),
                  'frame': {d: len(v) for d, v in frame.items()},
                  'drawn': {'include': len(frame['include']), 'unsure': len(frame['unsure']), 'exclude': N_CASE_EXC},
                  'seed_sample': SEED_CASE}

# ---------- reach tags ----------
wb = openpyxl.load_workbook(R / 'wp5/wp5_tag_check_blind.xlsx')
ws = wb['check']
head = [c.value for c in ws[1]]
blind = [dict(zip(head, row)) for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]
first = {c['openalex_id']: c for c in csv.DictReader(open(R / 'wp5/wp5_first_pass_codes.csv', encoding='utf-8'))}
for b in blind:
    f = first[b['openalex_id']]
    records[b['openalex_id']] = {
        'k': 'tags', 'id': b['openalex_id'], 't': clean(b['title']), 'v': clean(b.get('type')), 'y': str(b['year']),
        'doi': clean(b['doi']).replace('https://doi.org/', ''), 'a': clean(b['abstract']),
        'ai': {'health': f['health_application'], 'use': f['smote_use'], 'notes': clean(f['notes']), 'group': f['group']}}
assert len(records) == checks['harm']['n'] + checks['case']['n'] + len(blind), 'records overwritten'
checks['tags'] = {'n': len(blind), 'order': [b['openalex_id'] for b in blind], 'frame': {'blind subsample': len(blind)},
                  'drawn': {'blind subsample': len(blind)}, 'seed_sample': 20261110}

data = {'built': '2026-11-12', 'draft': LABEL, 'checks': checks, 'records': records}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'records.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print({k: (v['n'], v['drawn']) for k, v in checks.items()}, 'records', len(records),
      'size MB', round((OUT / 'records.json').stat().st_size / 1e6, 2),
      'no abstract', sum(1 for v in records.values() if not v['a'] or v['a'].startswith('(no abstract')))
