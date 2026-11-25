#!/usr/bin/env python3
"""Apply the code corrections of the independent AI check (Claude Fable 5.2, report v3) to the codes of the coverage
sample and the use audit, as one recode batch per project (v0.13).

The check returned, for 81 coded rows (sheets 4 and 5 of the check job), whether it agrees with the AI codes, and for
those it does not, the corrections as `field=value; field=value`
(data/search/screening_full_2026-11-11/check/returns/RETURN_code_checks_*_v3.csv). For every row with
person_agrees = no, this script takes the record's current code (coded.csv of the draft), sets the corrected fields,
checks every value against the codebook's field rules (coding_tools/schema.py), and writes the rows as a new batch of
the coding project (out/batchNNN_coded.csv and out/batchNNN_DONE.txt), so that consolidate_codes.py, where the last
code of a record wins, merges them like any recode. It also writes check/returns/applied_code_corrections.csv (one row
per changed field, with the value before and after). It stops if a correction names an unknown field or value.
Usage: python3 -I scripts/apply_check_code_corrections.py DRAFT_DIR CODING_TOOLS_DIR
"""
import csv
import sys
from pathlib import Path

csv.field_size_limit(10**9)
draft, tools = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(tools))
from schema import ROOT, SCHEMA  # noqa: E402

S = draft / 'data/search/screening_full_2026-11-11'
ret = sorted((S / 'check/returns').glob('RETURN_code_checks_*_v3.csv'))
if len(ret) != 1:
    sys.exit(f'STOP: expected one RETURN_code_checks file, found {len(ret)}')
PROJ = {'4_coverage_codes': 'coverage', '5_useaudit_codes': 'useaudit'}


def check_value(proj, field, value):
    rule = SCHEMA[proj].get(field)
    if rule is None or field == 'rec':
        sys.exit(f'STOP: {proj}: unknown field {field}')
    if isinstance(rule, set) and value not in rule:
        sys.exit(f'STOP: {proj}: {field}={value} is not one of {sorted(rule)}')
    if isinstance(rule, tuple) and rule[0] == 'list':
        bad = [v for v in value.split(';') if v not in rule[1]]
        if bad:
            sys.exit(f'STOP: {proj}: {field} has values outside the codebook: {bad}')


log, by_proj = [], {'coverage': [], 'useaudit': []}
for r in csv.DictReader(open(ret[0], encoding='utf-8-sig')):
    if (r['person_agrees'] or '').strip().lower() != 'no':
        continue
    proj = PROJ[r['list'].strip()]
    coded = {x['rec']: x for x in csv.DictReader(open(S / proj / 'coded.csv', encoding='utf-8'))}
    rec = r['rec'].strip()
    if rec not in coded:
        sys.exit(f'STOP: {rec} has no code in {proj}/coded.csv')
    row = {k: v for k, v in coded[rec].items() if k != 'batch'}
    fields = []
    for part in [p.strip() for p in r['person_corrections'].split('; ') if p.strip()]:
        field, value = (s.strip() for s in part.split('=', 1))
        check_value(proj, field, value)
        log.append({'project': proj, 'rec': rec, 'field': field, 'before': row[field], 'after': value})
        row[field] = value
        fields.append(field)
    row['note'] = (f'Independent AI check (Claude Fable 5.2, v3) corrected {", ".join(fields)}; '
                   f'see check/returns/applied_code_corrections.csv.')
    by_proj[proj].append(row)

made = {}
for proj, rows in by_proj.items():
    if not rows:
        continue
    R = Path(ROOT[proj])
    for done in (R / 'out').glob('batch*_DONE.txt'):
        if 'corrections of the independent AI check' in done.read_text(encoding='utf-8'):
            sys.exit(f'STOP: {done} shows that the corrections were applied already')
    existing = sorted((R / 'batches').glob('batch*.csv')) + sorted((R / 'out').glob('batch*_coded.csv'))
    nnn = f'{max(int(p.name[5:8]) for p in existing) + 1:03d}'
    # the batch file too, so that make_coding_batches.py numbers the next batch after this one
    sample = {x['rec']: x for x in csv.DictReader(open(S / 'samples' / ('coverage_sample.csv' if proj == 'coverage' else 'useaudit_sample.csv'),
                                                         encoding='utf-8'))}
    bcols = ['rec', 'stratum', 'order', 'year', 'venue', 'doi', 'title', 'abstract']
    with open(R / f'batches/batch{nnn}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, bcols, extrasaction='ignore')
        w.writeheader()
        w.writerows(sample.get(r['rec'], {'rec': r['rec']}) for r in rows)
    cols = list(SCHEMA[proj])
    with open(R / f'out/batch{nnn}_coded.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    (R / f'out/batch{nnn}_DONE.txt').write_text(
        f'{proj} batch {nnn}: the corrections of the independent AI check (Claude Fable 5.2, report v3), applied by '
        f'scripts/apply_check_code_corrections.py to the current codes of {len(rows)} records '
        f'({", ".join(r["rec"] for r in rows)}); no session coded this batch.\n', encoding='utf-8')
    made[proj] = (nnn, len(rows))
with open(S / 'check/returns/applied_code_corrections.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, ['project', 'rec', 'field', 'before', 'after'])
    w.writeheader()
    w.writerows(log)
print('recode batches:', made, '; fields changed:', len(log))
for x in log:
    print(f"  {x['project']} {x['rec']} {x['field']}: {x['before']} -> {x['after']}")
