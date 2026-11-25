#!/usr/bin/env python3
"""Consolidate the full title-and-abstract screen (WP4, 11 Nov 2026).

Writes into OUT (default /home/claude/work/screen_full/result):
  screen_all.csv        one row per record: decision, codes, reason, quote, tags, confidence, batch, and the record's
                        year, title, DOI, venue, document type and language (no abstract: licensed Scopus text stays out)
  screen_summary.json   counts by decision and code, includes by kind, by year band; agreement with the pilot
  coder_notes.md        the DONE notes of every batch, in batch order
Usage: python3 -I consolidate.py [OUT]
"""
import collections
import csv
import gzip
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
S = Path('/home/claude/work/screen_full')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else S / 'result'
OUT.mkdir(exist_ok=True)
RECORDS = Path('/home/claude/work/v06/data/search/2026-11-11/wp4_records_merged.csv.gz')
PILOT = Path('/home/claude/work/v06/data/search/screening_pilot_2026-11-11')

recs = {r['rec']: r for r in csv.DictReader(gzip.open(RECORDS, 'rt', encoding='utf-8'))}
rows, missing_batches = [], []
for f in sorted((S / 'batches').glob('batch*_to_screen.csv')):
    nnn = f.name[5:8]
    order = [r['rec'] for r in csv.DictReader(open(f, encoding='utf-8'))]
    o = S / f'out/batch{nnn}_screened.csv'
    got = list(csv.DictReader(open(o, encoding='utf-8'))) if o.exists() else []
    if [r['rec'] for r in got] != order:
        missing_batches.append(nnn)
        continue
    for r in got:
        m = recs[r['rec']]
        rows.append(dict(r, batch=nnn, year=m['year'], title=m['title'], doi=m['doi'], venue=m['venue'],
                         doctype=m['doctype'], language=m['language'], sources=m['sources']))
cols = ['rec', 'decision', 'reason_code', 'reason', 'quote', 'tags', 'confidence', 'batch', 'year', 'title', 'doi',
        'venue', 'doctype', 'language', 'sources']
with open(OUT / 'screen_all.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    w.writerows(rows)

dec = collections.Counter(r['decision'] for r in rows)
code = collections.Counter(r['reason_code'] for r in rows)
conf = collections.Counter((r['decision'], r['confidence']) for r in rows)


def band(y):
    try:
        y = int(y)
    except ValueError:
        return 'unknown'
    return '2002-2017' if y < 2018 else '2018-2022' if y <= 2022 else '2023-2026'


by_year = collections.Counter((band(r['year']), r['decision']) for r in rows)

# agreement with the pilot (same records, separate sessions, codebook v1 against v1.1)
man = json.load(open(PILOT / 'pilot_manifest_PRIVATE.json'))
pilot = {}
for f in sorted(PILOT.glob('batch0*_screened_a.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        pilot[r['rec']] = r['decision']
full = {r['rec']: r['decision'] for r in rows}


def agreement(ids):
    pairs = [(pilot[i], full[i]) for i in ids if i in pilot and i in full]
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    cross = collections.Counter(f'{a}->{b}' for a, b in pairs if a != b)
    return dict(n=n, agreement=round(po, 3), kappa=round((po - pe) / (1 - pe), 3) if pe < 1 else None,
                differences=dict(cross))


known = man['known_includes_smote_family']
summary = dict(
    records_screened=len(rows), batches_missing=missing_batches,
    decisions=dict(dec), codes=dict(code), confidence={f'{a}/{b}': n for (a, b), n in sorted(conf.items())},
    by_year_band={f'{a}/{b}': n for (a, b), n in sorted(by_year.items())},
    pilot_random_400=agreement(man['random_sample']),
    known_smote_family_35=dict(n=len([i for i in known if i in full]),
                               included=sum(full.get(i) == 'include' for i in known),
                               unsure=sum(full.get(i) == 'unsure' for i in known),
                               excluded=[i for i in known if full.get(i) == 'exclude']),
    codebook='SCREENING_CODEBOOK.md v1.1 (the pilot used v1)', seed_batches=20261112)
json.dump(summary, open(OUT / 'screen_summary.json', 'w'), indent=1)

with open(OUT / 'coder_notes.md', 'w', encoding='utf-8') as fh:
    fh.write('# Notes of the screening sessions, by batch\n\n')
    for f in sorted((S / 'out').glob('batch*_DONE.txt')):
        fh.write(f'## {f.name[:8]}\n\n' + open(f, encoding='utf-8').read().strip() + '\n\n')
print(json.dumps({k: summary[k] for k in ('records_screened', 'batches_missing', 'decisions', 'pilot_random_400',
                                          'known_smote_family_35')}, indent=1))
