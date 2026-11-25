#!/usr/bin/env python3
"""Draw the coverage sample (WP4) and the use-audit sample (WP5) from the screening decisions, in a stable random order.

Every record gets a rank within its stratum from a hash of (seed, record id), so removing or adding a record (a
correction of the team) moves no other record: the sample is always the first records of each stratum in that order.
  Coverage sample: records that pass the title-and-abstract screen (include, or unsure for full-text assessment),
    strata = the four periods of the evaluation audit (P1 to 2009, P2 2010-2015, P3 2016-2020, P4 2021-2026);
    the first COV_N of each stratum are assessed in full text. Seed 20261116.
  Use audit: records excluded under E1, strata U1 (to 2020), U2 (2021-2023), U3 (2024-2026); the first USE_N of each
    stratum are coded from title and abstract and the first USE_FT of them from the full text. Seed 20261117.
  Reserves (v0.15): the records whose full texts the final merge may need. Coverage: the records that join the sample
    if every record of it still unsure leaves the screen (D28: unsure after the authors' check is excluded), and two
    more per stratum for the authors' corrections; use audit: the next record of each stratum after its full-text part.
  Late corrections (v0.61): a record listed in samples/coverage_late_corrections.csv was included by the authors after
    the coverage sample had been coded and stays out of its frame; the paper says so (Appendix E).
Usage: python3 -I scripts/make_samples.py DRAFT_DIR OUTDIR
Writes OUTDIR/coverage_sample.csv and OUTDIR/useaudit_sample.csv (records of the target only, in rank order) and
OUTDIR/reserves.csv (not part of either sample until a correction moves them in).
"""
import csv
import gzip
import hashlib
import re
import sys
from pathlib import Path

csv.field_size_limit(10**9)
COV_N, COV_SEED = 30, 20261116
USE_N, USE_FT, USE_SEED = 100, 50, 20261117
draft, outdir = Path(sys.argv[1]), Path(sys.argv[2])
dec = list(csv.DictReader(open(draft / 'data/search/screening_full_2026-11-11/decisions/screen_decisions.csv', encoding='utf-8')))
meta = {}
for r in csv.DictReader(gzip.open(draft / 'data/search/2026-11-11/wp4_records_merged.csv.gz', 'rt', encoding='utf-8')):
    ax = re.search(r'arxiv:([^;]+)', r['record_ids'])
    oa = re.search(r'openalex:(W\d+)', r['record_ids'])
    doi = (r['doi'] or '').strip().lower()
    arx = ax.group(1).strip() if ax else (doi.split('arxiv.', 1)[1] if doi.startswith('10.48550/arxiv.') else '')
    meta[r['rec']] = {'doi': doi, 'arxiv': re.sub(r'v\d+$', '', arx), 'openalex': oa.group(1) if oa else '',
                      'title': r['title'], 'year': r['year'], 'venue': r['venue'], 'abstract': r['abstract']}


def rank_key(seed, rec):
    return hashlib.sha256(f'{seed}:{rec}'.encode()).hexdigest()


def use_stratum(y):
    y = int(y) if y.isdigit() else 0
    return 'U1' if y <= 2020 else ('U2' if y <= 2023 else 'U3')


cols = ['rec', 'stratum', 'order', 'target', 'doi', 'arxiv', 'openalex', 'title', 'year', 'venue', 'abstract']
outdir.mkdir(parents=True, exist_ok=True)

# v0.61 (23 Nov 2026): a record that the authors included after the coverage sample had been coded stays out of its
# frame, so that the sample is kept as coded (samples/coverage_late_corrections.csv: rec, decided, note)
_late = draft / 'data/search/screening_full_2026-11-11/samples/coverage_late_corrections.csv'
LATE = {r['rec'] for r in csv.DictReader(open(_late, encoding='utf-8'))} if _late.exists() else set()
cov = [r for r in dec if r['decision'] in ('include', 'unsure') and r['rec'] not in LATE]
with open(outdir / 'coverage_sample.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    for s in ('P1', 'P2', 'P3', 'P4'):
        frame = sorted((r for r in cov if r['period'] == s), key=lambda r: rank_key(COV_SEED, r['rec']))
        for i, r in enumerate(frame[:COV_N], 1):
            w.writerow({'rec': r['rec'], 'stratum': s, 'order': i, 'target': 'fulltext', **meta[r['rec']]})
        print(f'coverage {s}: frame {len(frame)}, drawn {min(COV_N, len(frame))}')

use = [r for r in dec if r['decision'] == 'exclude' and r['code'] == 'E1']
with open(outdir / 'useaudit_sample.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    for s in ('U1', 'U2', 'U3'):
        frame = sorted((r for r in use if use_stratum(r['year']) == s), key=lambda r: rank_key(USE_SEED, r['rec']))
        for i, r in enumerate(frame[:USE_N], 1):
            w.writerow({'rec': r['rec'], 'stratum': s, 'order': i, 'target': 'fulltext' if i <= USE_FT else 'abstract', **meta[r['rec']]})
        print(f'use audit {s}: frame {len(frame)}, drawn {min(USE_N, len(frame))} ({min(USE_FT, len(frame))} for full text)')

inc = [r for r in dec if r['decision'] == 'include' and r['rec'] not in LATE]
with open(outdir / 'reserves.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    for s in ('P1', 'P2', 'P3', 'P4'):
        drawn = sorted((r for r in cov if r['period'] == s), key=lambda r: rank_key(COV_SEED, r['rec']))[:COV_N]
        ids, k = {r['rec'] for r in drawn}, sum(1 for r in drawn if r['decision'] == 'unsure') + 2
        nxt = [r for r in sorted((r for r in inc if r['period'] == s), key=lambda r: rank_key(COV_SEED, r['rec'])) if r['rec'] not in ids][:k]
        for j, r in enumerate(nxt, 1):
            w.writerow({'rec': r['rec'], 'stratum': s, 'order': COV_N + j, 'target': 'reserve-coverage', **meta[r['rec']]})
        print(f'coverage {s}: {len(nxt)} reserves ({k - 2} unsure in the sample)')
    for s in ('U1', 'U2', 'U3'):
        frame = sorted((r for r in use if use_stratum(r['year']) == s), key=lambda r: rank_key(USE_SEED, r['rec']))
        if len(frame) > USE_FT:
            r = frame[USE_FT]
            w.writerow({'rec': r['rec'], 'stratum': s, 'order': USE_FT + 1, 'target': 'reserve-useaudit', **meta[r['rec']]})
