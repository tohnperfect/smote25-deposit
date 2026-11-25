#!/usr/bin/env python3
"""Build records.json of the page "SMOTE25 C1-C3 Workbench" (12 November 2026): the papers the team gets through the
library (the two samples' PDF request list with its reserves, and the five related-work papers of D44), with the
metadata a person needs to find each one. No abstracts: titles, years, venues and DOIs only.

Usage: python3 -I scripts/build_workbench.py <draft_dir> <out_dir>
Reads  data/search/screening_full_2026-11-11/samples/pdf_requests.csv (243 rows, in request order)
       data/related_work/requests_d44.csv (5 rows)
Writes <out_dir>/records.json
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

D, OUT = Path(sys.argv[1]), Path(sys.argv[2])
REQ = D / 'data/search/screening_full_2026-11-11/samples/pdf_requests.csv'
RW = D / 'data/related_work/requests_d44.csv'

GROUP = {'coverage (WP4)': ('coverage', 'Coverage sample (C1)'),
         'use audit (WP5)': ('use', 'Use audit (C2)'),
         'coverage, reserve (WP4)': ('reserve', 'Reserve, coverage'),
         'use audit, reserve (WP5)': ('reserve', 'Reserve, use audit')}


def scholar(title):
    return 'https://scholar.google.com/scholar?q=' + quote('"' + title.strip() + '"')


def main():
    rows = list(csv.DictReader(open(REQ, encoding='utf-8')))
    assert len(rows) == 243, f'STOP: {len(rows)} request rows, expected 243'
    years = defaultdict(list)
    for r in rows:
        if r['year'].strip().isdigit():
            years[r['stratum']].append(int(r['year']))
    span = {s: f'{min(v)} to {max(v)}' for s, v in years.items()}
    items = []
    for n, r in enumerate(rows, 1):
        group, label = GROUP[r['sample']]
        doi = r['doi'].strip()
        items.append(dict(k=r['rec'], rec=r['rec'], order=n, group=group, sample=label, stratum=r['stratum'],
                          years=span.get(r['stratum'], ''), rank=int(r['rank']), title=r['title'].strip(),
                          year=r['year'].strip(), venue=r['venue'].strip(), doi=doi,
                          link=('https://doi.org/' + doi) if doi else (r['url'].strip() or scholar(r['title'])),
                          linkkind='DOI' if doi else ('link' if r['url'].strip() else 'Scholar search'),
                          save=r['save_as'].strip()))
    keys = {i['k'] for i in items}
    assert len(keys) == len(items), 'STOP: a record appears twice'
    for n, r in enumerate(csv.DictReader(open(RW, encoding='utf-8')), len(items) + 1):
        doi = r['doi'].strip()
        k = 'RW-' + r['key']
        assert k not in keys
        items.append(dict(k=k, rec=r['key'], order=n, group='related', sample='Related work, Table 2 (D44)', stratum='',
                          years='', rank=0, title=r['title'].strip(), year=r['year'].strip(),
                          venue=r['venue'].strip() + ' (' + r['authors'].strip() + ')', doi=doi,
                          link='https://doi.org/' + doi, linkkind='DOI',
                          save=r['key'] + '.pdf', access=r['access'].strip()))
    counts = defaultdict(int)
    for i in items:
        counts[i['group']] += 1
    out = dict(title='SMOTE25 C1-C3 Workbench', built='2026-11-12', n=len(items), counts=counts,
               sources=[str(REQ.relative_to(D)), str(RW.relative_to(D))], items=items)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'records.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(json.dumps(dict(n=len(items), counts=counts, strata=span), indent=1))


if __name__ == '__main__':
    main()
