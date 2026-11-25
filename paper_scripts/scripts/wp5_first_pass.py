#!/usr/bin/env python3
"""WP5 step 1 (M9), after the sample: apply the first-pass codes, summarise them, and prepare the blind check.

Inputs (written by scripts/wp5_tag_sample.py and by the coder):
  wp5/wp5_tag_sample.json                  the 150 sampled works (100 tagged SDG 3, 50 with no SDG tag) and the
                                           seeded 20 percent check subsample
  data/openalex/<date>/wp5_tag_sample_raw.json   raw responses (for the SDG strata of the random 200)
  wp5/wp5_first_pass_codes.csv             first-pass codes (status ai_draft: not citable until the check)
Outputs:
  wp5/wp5_tag_precision_sheet.xlsx         instructions + first_pass (codes filled in)
  wp5/wp5_tag_check_blind.xlsx             instructions + check: the 30 works without group, field or codes,
                                           for a person to code blind (drop-down lists)
  wp5/wp5_first_pass_summary.json          counts, shares and Wilson 95% intervals, by group
With --agreement, reads the filled blind file and writes wp5/wp5_check_agreement.json (percent agreement and
Cohen's kappa against the first pass).
Usage: python3 scripts/wp5_first_pass.py data/openalex/<date> wp5/ [--agreement]
"""
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

snap, out = Path(sys.argv[1]), Path(sys.argv[2])
AGREEMENT = '--agreement' in sys.argv
Z = 1.959964
HEALTH = ('yes', 'no', 'unclear')
USE = ('uses', 'only cites', 'unclear')
INSTRUCTIONS = [
    'WP5 step 1: precision of the OpenAlex SDG 3 tag on works citing SMOTE (W2148143831), and share that use SMOTE.',
    'Sample drawn 2026-11-10 (15:52 UTC) with seed 20261110: 100 citing works tagged SDG 3, 50 citing works with no SDG tag.',
    'health_application: yes if the work applies or studies a method on a health or medical problem (clinical, biomedical, '
    'public health); no if not; unclear if title and abstract do not say.',
    'smote_use: uses if title or abstract says SMOTE (or a SMOTE variant) is applied in the work; only cites if SMOTE is not '
    'mentioned or only discussed; unclear otherwise.',
    'Code from title and abstract only. Note "borderline: ..." when the work fits an SDG 3 target but is not clinical, '
    'biomedical or public-health research (for example road safety), and "no abstract" when OpenAlex has none.',
]


def wilson(x, n):
    if n == 0:
        return None
    p = x / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return dict(x=x, n=n, share=round(p, 4), ci95=[round(c - h, 4), round(c + h, 4)])


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return dict(n=n, agreement=round(po, 4), kappa=(round((po - pe) / (1 - pe), 4) if pe < 1 else None))


sample = json.loads((out / 'wp5_tag_sample.json').read_text(encoding='utf-8'))
rows, check = sample['rows'], sample['check']
codes = list(csv.DictReader(open(out / 'wp5_first_pass_codes.csv', encoding='utf-8')))
assert [c['openalex_id'] for c in codes] == [r[0] for r in rows], 'codes and sample are not in the same order'
for c in codes:
    assert c['health_application'] in HEALTH and c['smote_use'] in USE, c

if AGREEMENT:
    wb = openpyxl.load_workbook(out / 'wp5_tag_check_blind.xlsx')
    ws = wb['check']
    head = [c.value for c in ws[1]]
    person = {r[0]: dict(zip(head, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}
    first = {c['openalex_id']: c for c in codes}
    ids = [i for i in person if person[i].get('health_application') and person[i].get('smote_use')]
    res = dict(coded_by_person=len(ids), of=len(person))
    for var in ('health_application', 'smote_use'):
        res[var] = kappa([first[i][var] for i in ids], [str(person[i][var]).strip() for i in ids])
        res[var]['disagreements'] = [i for i in ids if first[i][var] != str(person[i][var]).strip()]
    (out / 'wp5_check_agreement.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
    print(json.dumps(res, indent=1))
    sys.exit(0)

# == workbook with the first pass
wb = openpyxl.Workbook()
info = wb.active
info.title = 'instructions'
lines = INSTRUCTIONS + ['first_pass: codes by a session (AI), 10 Nov 2026, status ai_draft; not citable until a person has '
                        'coded the 30 works of wp5_tag_check_blind.xlsx blind and the agreement is computed '
                        '(scripts/wp5_first_pass.py --agreement).']
for i, t in enumerate(lines, 1):
    info.cell(i, 1, t)
info.column_dimensions['A'].width = 160
head = ['openalex_id', 'group', 'year', 'type', 'doi', 'primary field', 'title', 'abstract', 'health_application', 'smote_use', 'notes']
ws = wb.create_sheet('first_pass')
for j, h in enumerate(head, 1):
    c = ws.cell(1, j, h); c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDDDDD')
for i, (r, c) in enumerate(zip(rows, codes), 2):
    for j, v in enumerate(list(r) + [c['health_application'], c['smote_use'], c['notes']], 1):
        ws.cell(i, j, v)
for col, w in zip('ABCDEFGHIJK', (14, 11, 6, 15, 30, 22, 60, 80, 12, 11, 50)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'C2'
wb.save(out / 'wp5_tag_precision_sheet.xlsx')

# == blind file for the person: no group, no field, no codes
wb = openpyxl.Workbook()
info = wb.active
info.title = 'instructions'
for i, t in enumerate(INSTRUCTIONS[2:] + [
        'Code the 30 works of the sheet "check" from title and abstract only (follow the DOI if you need the abstract), '
        'without looking at wp5_tag_precision_sheet.xlsx. Use the drop-down lists. Then run: '
        'python3 scripts/wp5_first_pass.py data/openalex/2026-11-10 wp5/ --agreement'], 1):
    info.cell(i, 1, t)
info.column_dimensions['A'].width = 160
bhead = ['openalex_id', 'year', 'type', 'doi', 'title', 'abstract', 'health_application', 'smote_use', 'notes']
ws = wb.create_sheet('check')
for j, h in enumerate(bhead, 1):
    c = ws.cell(1, j, h); c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDDDDD')
for i, idx in enumerate(check, 2):
    r = rows[idx]
    for j, v in enumerate([r[0], r[2], r[3], r[4], r[6], r[7] or '(no abstract in OpenAlex)'], 1):
        ws.cell(i, j, v).alignment = Alignment(wrap_text=(j in (5, 6)), vertical='top')
n = len(check) + 1
for col, opts in (('G', HEALTH), ('H', USE)):
    dv = DataValidation(type='list', formula1='"' + ','.join(opts) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'{col}2:{col}{n}')
for col, w in zip('ABCDEFGHI', (14, 6, 15, 30, 50, 90, 16, 12, 40)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = 'B2'
wb.save(out / 'wp5_tag_check_blind.xlsx')

# == summary
summ = dict(status='ai_draft: first pass by a session; not citable until the blind check (30 works) is done',
            sample='100 citing works tagged SDG 3 and 50 with no SDG tag, OpenAlex 10 Nov 2026, seed 20261110')
for grp in ('SDG3', 'no SDG tag'):
    g = [c for c in codes if c['group'] == grp]
    has_abs = {r[0]: bool(r[7]) for r in rows}
    h = Counter(c['health_application'] for c in g)
    u = Counter(c['smote_use'] for c in g)
    border = sum(1 for c in g if c['health_application'] == 'no' and c['notes'].startswith('borderline'))
    ga = [c for c in g if has_abs[c['openalex_id']]]
    summ[grp] = dict(
        n=len(g), with_abstract=len(ga),
        health=dict(h), health_no_borderline=border,
        health_yes_among_coded=wilson(h['yes'], h['yes'] + h['no']),
        health_yes_all=wilson(h['yes'], len(g)),
        health_yes_or_borderline_among_coded=wilson(h['yes'] + border, h['yes'] + h['no']),
        smote_use=dict(u),
        uses_all=wilson(u['uses'], len(g)),
        uses_with_abstract=wilson(sum(1 for c in ga if c['smote_use'] == 'uses'), len(ga)),
        unclear_with_abstract=sum(1 for c in ga if c['smote_use'] == 'unclear'),
    )
raw = json.loads((snap / 'wp5_tag_sample_raw.json').read_text(encoding='utf-8'))['responses']['all']['results']
none = sum(1 for w in raw if not w.get('sustainable_development_goals'))
s3 = sum(1 for w in raw if any(str(x.get('id', '')).endswith('/3') for x in (w.get('sustainable_development_goals') or [])))
summ['random_200'] = dict(n=len(raw), sdg3=wilson(s3, len(raw)), no_sdg=wilson(none, len(raw)), other_sdg_only=len(raw) - s3 - none,
                          note='the 50 untagged works are the first 50 works without an SDG tag in this random sample')
(out / 'wp5_first_pass_summary.json').write_text(json.dumps(summ, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps(summ, indent=1, ensure_ascii=False))
