#!/usr/bin/env python3
"""Fetch from Crossref the records the reference-list check needs (v0.53): for each of the five reviews its own record
with its reference list, and for every reference that has a DOI the work's title, year and, where Crossref holds one,
abstract. Cached under data/reflists/crossref/ and data/reflists/crossref_works/ (one JSON per DOI; the abstracts are
kept for the coding and are not deposited). Polite: one request at a time, a pause between requests, no retries of a
refusal. Usage: python3 -I scripts/reflist_fetch.py <draft dir>"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

V = Path(sys.argv[1])
OUT = V / 'data/reflists'
(OUT / 'crossref_works').mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'SMOTE25-survey-refcheck/0.53'}


def get(doi):
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['message']


n_new = n_fail = 0
for f in sorted((OUT / 'crossref').glob('*.json')):
    refs = json.load(open(f, encoding='utf-8'))['message'].get('reference', [])
    for ref in refs:
        doi = (ref.get('DOI') or '').lower().strip()
        if not doi:
            continue
        p = OUT / 'crossref_works' / (re.sub(r'[^a-z0-9._-]+', '_', doi) + '.json')
        if p.exists():
            continue
        try:
            m = get(doi)
            rec = {'doi': doi, 'title': (m.get('title') or [''])[0], 'container': (m.get('container-title') or [''])[0],
                   'year': (m.get('issued', {}).get('date-parts') or [[None]])[0][0], 'type': m.get('type'),
                   'abstract': re.sub(r'<[^>]+>', ' ', m.get('abstract') or '')}
            n_new += 1
        except Exception as e:  # recorded, not retried
            rec = {'doi': doi, 'error': str(e)[:200]}
            n_fail += 1
        json.dump(rec, open(p, 'w', encoding='utf-8'))
        time.sleep(0.15)
print('fetched', n_new, 'failed', n_fail, 'cached', len(list((OUT / 'crossref_works').glob('*.json'))))
