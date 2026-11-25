#!/usr/bin/env python3
"""Build records.json for the team's review page (approve or drop) from the v0.13 screen.

Queues:
  unsure    records the screen leaves unsure (rulings pass not settled, or left unsure by the independent check)
  rulings   records the rulings pass excluded with high confidence, plus the check's exclusions tied to a task
            (ruling C keeps every task in scope)
  coverage  the coverage sample of Section 4.4 (120 records that pass the screen)
  blind     the check job's two samples (300 includes, 300 exclusions); the page hides the AI decision until the
            reviewer has decided, so the authors' agreement with the screen can be reported
  included  every record the screen includes, in a seeded random order (any first part is a random sample)

Team use only: the output carries the licensed Scopus abstracts. Never deposit it.
Usage: python3 -I build_team_review.py <screening_full dir> <merged records csv.gz> <out dir> [draft label, e.g. v0.15]
"""
import csv
import glob
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

SF = Path(sys.argv[1])
MERGED = Path(sys.argv[2])
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
SEED = '20261112'


def rows(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def short(s, n=300):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def hrank(rec):
    return hashlib.sha256(f'{SEED}:{rec}'.encode()).hexdigest()


def period(y):
    try:
        y = int(y)
    except ValueError:
        return ''
    return 'to 2020' if y <= 2020 else ('2021 to 2023' if y <= 2023 else 'from 2024')


dec = {r['rec']: r for r in rows(SF / 'decisions' / 'screen_decisions.csv')}

# reasons of the three looks
first = {r['rec']: r for r in rows(SF / 'result' / 'screen_all.csv')}
final = {r['rec']: r for r in rows(SF / 'final' / 'screen_final.csv')}
third = {}
for p in sorted(glob.glob(str(SF / 'adjudication' / 'out' / '*.csv'))):
    for r in rows(p):
        third[r['rec']] = r
# the independent check (v3) and the rulings pass
check = {}
for p in sorted(glob.glob(str(SF / 'check' / 'returns' / 'RETURN_screen_decisions_*_v3.csv'))):
    for r in rows(p):
        check[r['rec']] = r
facts = {}
for p in sorted(glob.glob(str(SF / 'rule_b' / 'out' / 'batch*_facts.csv'))):
    for r in rows(p):
        facts[r['rec']] = r

cov = rows(SF / 'samples' / 'coverage_sample.csv')
blind = rows(SF / 'check' / 'csv' / '2_includes.csv') + rows(SF / 'check' / 'csv' / '3_exclusions.csv')
rb_ex = rows(SF / 'check' / 'csv' / '8_rulings_excluded.csv')
task_ex = rows(SF / 'check' / 'csv' / '9_check_task_exclusions.csv')

queues = {
    'unsure': sorted((r for r in dec if dec[r]['decision'] == 'unsure'), key=hrank),
    'rulings': [r['rec'] for r in rb_ex] + [r['rec'] for r in task_ex],
    'coverage': [r['rec'] for r in sorted(cov, key=lambda r: (r['stratum'], int(r['order'])))],
    'blind': sorted((r['rec'] for r in blind), key=hrank),  # shuffled: the two lists must not show as blocks
    'included': sorted((r for r in dec if dec[r]['decision'] == 'include'), key=hrank),
}
for q, recs in queues.items():
    assert len(recs) == len(set(recs)), q
need = set().union(*queues.values())

meta = {}
with gzip.open(MERGED, 'rt', encoding='utf-8', newline='') as f:
    for r in csv.DictReader(f):
        if r['rec'] in need:
            meta[r['rec']] = r
missing = need - set(meta)
assert not missing, sorted(missing)[:5]


def link(m):
    if m.get('doi'):
        return 'https://doi.org/' + m['doi']
    for part in (m.get('record_ids') or '').split(';'):
        k, _, v = part.partition(':')
        if k == 'arxiv' and v:
            return 'https://arxiv.org/abs/' + v
        if k == 'openalex' and v:
            return 'https://openalex.org/' + v
    return ''


def why(rec):
    d = dec[rec]
    by = d['decided_by']
    out = []
    if by.startswith('independent AI check') and rec in check:
        c = check[rec]
        out.append(('Independent AI check', short(f"{c['person_decision'] or 'agrees'} {c['person_code']}. {c['note']}")))
    if by.startswith('rulings') and rec in facts:
        f = facts[rec]
        out.append(('Rulings pass', short(
            f"scheme {f['scheme']}, generator {f['generator']}, presented {f['presented']}, compared {f['compared']}, "
            f"confidence {f['confidence']}. {f['reason']}")))
    if rec in third and third[rec].get('reason'):
        t = third[rec]
        out.append(('Third look', short(f"{t['decision']} {t['reason_code']}. {t['reason']}")))
    if rec in final and final[rec].get('second_reason'):
        s = final[rec]
        out.append(('Second look', short(f"{s['second_decision']} {s['second_code']}. {s['second_reason']}")))
    if rec in first and first[rec].get('reason'):
        p = first[rec]
        out.append(('First pass', short(f"{p['decision']} {p['reason_code']}. {p['reason']}")))
    if not by.startswith('rulings') and rec in facts and d['decision'] != 'exclude':
        f = facts[rec]
        out.append(('Rulings pass', short(
            f"scheme {f['scheme']}, generator {f['generator']}, presented {f['presented']}, compared {f['compared']}, "
            f"confidence {f['confidence']}. {f['reason']}", 300)))
    return out[:3]


qof = {}
for q, recs in queues.items():
    for i, r in enumerate(recs):
        qof.setdefault(r, {})[q] = i + 1

recs_out = []
for rec in sorted(need):
    d, m = dec[rec], meta[rec]
    recs_out.append({
        'r': rec, 'y': d['year'], 'p': period(d['year']), 't': m['title'], 'v': m['venue'], 'u': link(m),
        'a': m['abstract'], 'd': d['decision'], 'c': d['code'], 'lc': d['looks_code'], 'by': d['decided_by'],
        'w': why(rec), 'q': qof[rec],
    })

data = {
    'built': '2026-11-12', 'draft': sys.argv[4] if len(sys.argv) > 4 else 'v0.13',
    'queues': {q: {'n': len(v), 'order': v} for q, v in queues.items()},
    'records': recs_out,
}
(OUT / 'records.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('records', len(recs_out), {q: len(v) for q, v in queues.items()})
print('decisions in queues:', {q: dict(Counter(dec[r]['decision'] for r in v)) for q, v in queues.items()})
print('size MB', round((OUT / 'records.json').stat().st_size / 1e6, 2))
print('no abstract:', sum(1 for r in recs_out if not r['a']))
