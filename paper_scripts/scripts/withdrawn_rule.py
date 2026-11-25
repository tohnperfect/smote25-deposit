#!/usr/bin/env python3
"""Rule for records removed by their repository (decision of the team lead, 11 November 2026).

A search record whose deposit its repository has removed is excluded under a code of its own, E-WITHDRAWN, whatever
the three looks of the screen decided, and the number is reported in the PRISMA flow (Figure 2). The records are the
ones for which the Zenodo API answered HTTP 410 on 11 November 2026 (data/search/zenodo_status_2026-11-11.csv,
written by scripts/zenodo_status.py; Zenodo is the only repository in the search results found to have removed
deposits). This script writes data/search/screening_full_2026-11-11/withdrawn_records.csv; scripts/screen_decide.py
applies it after the three looks and before the team's corrections, so a person can still override a record.
Usage: python3 -I scripts/withdrawn_rule.py DRAFT_DIR
"""
import collections
import csv
import sys
from pathlib import Path

R = Path(sys.argv[1])
rows = list(csv.DictReader(open(R / 'data/search/zenodo_status_2026-11-11.csv', encoding='utf-8')))
gone = [r for r in rows if r['http'] == '410']
out = R / 'data/search/screening_full_2026-11-11/withdrawn_records.csv'
cols = ['rec', 'repository', 'doi', 'http', 'checked_utc', 'removal_date', 'removal_reason', 'code', 'rule']
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    for r in sorted(gone, key=lambda r: r['rec']):
        w.writerow({'rec': r['rec'], 'repository': 'Zenodo', 'doi': r['doi'], 'http': r['http'],
                    'checked_utc': r['checked_utc'], 'removal_date': r['removal_date'][:10],
                    'removal_reason': r['removal_reason'] or 'not given', 'code': 'E-WITHDRAWN',
                    'rule': 'removed by its repository; excluded under its own code (team lead, 11 Nov 2026)'})
print(f'{len(gone)} of {len(rows)} Zenodo records removed;', dict(collections.Counter(r["removal_reason"] or "not given" for r in gone)))
print('wrote', out.relative_to(R))
