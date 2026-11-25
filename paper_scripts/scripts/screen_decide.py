#!/usr/bin/env python3
"""Combine the three AI looks of the title-and-abstract screen (WP4) and the team's corrections into one decision per record.

Inputs (all under data/search/screening_full_2026-11-11/):
  final/screen_final.csv            first pass and second look per record, with the status of reconcile.py
  adjudication/out/batch*_screened.csv   the third look at the 2,088 disputed records
  check/returns/RETURN_screen_decisions_*_v3.csv (optional)  the independent AI check (another model, Claude Fable
                                    5.2; report v3): its decision for every unsure record and its corrections of the
                                    two samples; check/csv/ lists the records it covered
  rule_b/rule_b_decisions.csv (optional)  rulings B and B2 applied by an AI pass to the included records
                                    (scripts/rule_b_decide.py)
  withdrawn_records.csv (optional)  records removed by their repository (scripts/withdrawn_rule.py)
  person_overrides.csv (optional)   the team's corrections: rec, decision (include, exclude), code, note
  FINAL_MERGE (optional, an empty file)  set at the final merge, when the authors have checked the screen: every record
                                    still unsure is then excluded under E-UNSURE (decision D28 of the team lead, 12 Nov 2026)
Rules: a high-confidence first decision stands; a decision both passes share stands (code of the second look); a
disputed record takes the third look's decision and code (unsure goes on to full-text assessment); the independent AI
check's decision replaces these for every record it decided or corrected (team lead, 12 Nov 2026); an included record
outside the check's lists that the AI pass finds to fail rulings B or B2 is excluded under E1 when the pass was
confident and is otherwise unsure (U-rule-B), for the authors' check or the full text (team lead, 12 Nov 2026); a record removed by its repository is excluded under E-WITHDRAWN whatever the looks decided (rule of the team
lead, 11 Nov 2026); a correction of the team replaces any of these; at the final merge a record still unsure is excluded under E-UNSURE (D28). Output: decisions/screen_decisions.csv and decisions/screen_decisions_summary.json.
The columns ai_screen_decision, ai_screen_code and ai_screen_by keep the decision of the AI screen (the looks, the
check, the rulings pass and the rule for removed records) before the authors' corrections and D28 (v0.15): the counts
that describe those AI steps in Section 3.4 are taken from them, so that a later correction or the final merge does not
change what the text says each step did; the summary reports the corrections and D28 separately (team, final_merge_unsure_excluded).
Usage: python3 -I scripts/screen_decide.py DRAFT_DIR
"""
import collections
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
D = Path(sys.argv[1]) / 'data/search/screening_full_2026-11-11'
PERIODS = [('P1', 1997, 2009), ('P2', 2010, 2015), ('P3', 2016, 2020), ('P4', 2021, 2027)]  # P4 holds the forthcoming records dated 2027


def period(y):
    y = int(y) if str(y).isdigit() else 0
    for p, a, b in PERIODS:
        if a <= y <= b:
            return p
    return 'P?'


fin = list(csv.DictReader(open(D / 'final/screen_final.csv', encoding='utf-8')))
third = {}
for f in sorted((D / 'adjudication/out').glob('batch*_screened.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        third[r['rec']] = r
wd = {}
wp = D / 'withdrawn_records.csv'
if wp.exists():
    for r in csv.DictReader(open(wp, encoding='utf-8')):
        wd[r['rec'].strip()] = r
ck, ck_lists = {}, set()
returns = sorted((D / 'check/returns').glob('RETURN_screen_decisions_*_v3.csv')) if (D / 'check/returns').exists() else []
for f in returns:
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        if r.get('rec') and (r.get('person_decision') or '').strip():
            ck[r['rec'].strip()] = r
if returns:   # the records the check read: its three screening lists
    for name in ('1_unsure', '2_includes', '3_exclusions'):
        ck_lists |= {r['rec'] for r in csv.DictReader(open(D / f'check/csv/{name}.csv', encoding='utf-8-sig'))}
rb = {}
rbp = D / 'rule_b/rule_b_decisions.csv'
if rbp.exists():
    for r in csv.DictReader(open(rbp, encoding='utf-8')):
        rb[r['rec']] = r
FINAL = (D / 'FINAL_MERGE').exists()  # D28: switched on only at the final merge
over = {}
op = D / 'person_overrides.csv'
if op.exists():
    for r in csv.DictReader(open(op, encoding='utf-8')):
        if r.get('rec'):
            over[r['rec'].strip()] = r

out, missing, rb_applied = [], [], []
for r in fin:
    st = r['status']
    t = third.get(r['rec'])
    row = {'rec': r['rec'], 'year': r['year'], 'period': period(r['year']),
           'first_decision': r['first_decision'], 'first_code': r['first_code'], 'first_confidence': r['first_confidence'],
           'second_decision': r['second_decision'], 'second_code': r['second_code'],
           'third_decision': t['decision'] if t else '', 'third_code': t['reason_code'] if t else '',
           'third_confidence': t['confidence'] if t else '', 'looks_decision': '', 'looks_code': '',
           'check_decision': '', 'check_code': '', 'rule_b': '', 'person_decision': '', 'person_note': ''}
    if st in ('include_single_high', 'exclude_single_high'):
        dec, code, by = r['first_decision'], r['first_code'], 'first pass, high confidence'
    elif st in ('include_agreed', 'exclude_agreed'):
        dec, code, by = r['second_decision'], r['second_code'], 'first pass and second look agree'
    elif st == 'to_check':
        if not t:
            missing.append(r['rec'])
            dec, code, by = 'pending', '', 'third look missing'
        else:
            dec, code, by = t['decision'], t['reason_code'], 'third look (adjudication)'
    else:
        raise SystemExit(f'unknown status {st} for {r["rec"]}')
    row['looks_decision'], row['looks_code'] = dec, code
    if r['rec'] in ck:
        c = ck[r['rec']]
        row['check_decision'], row['check_code'] = c['person_decision'].strip(), (c.get('person_code') or '').strip()
        dec, code, by = row['check_decision'], row['check_code'] or code, 'independent AI check'
    elif dec == 'include' and r['rec'] in rb and r['rec'] not in ck_lists:
        rb_applied.append(r['rec'])
        row['rule_b'] = rb[r['rec']]['rule'] or 'kept'
        if rb[r['rec']]['final'] == 'exclude':
            dec, code, by = 'exclude', 'E1', 'rulings B and B2 (AI pass)'
        elif rb[r['rec']]['final'] == 'unsure':
            dec, code, by = 'unsure', 'U-rule-B', 'rulings B and B2 (AI pass), not settled'
    if r['rec'] in wd:
        dec, code, by = 'exclude', wd[r['rec']]['code'], 'rule: removed by its repository'
    row['ai_screen_decision'], row['ai_screen_code'], row['ai_screen_by'] = dec, code, by   # before the authors and D28
    if r['rec'] in over:
        o = over[r['rec']]
        row['person_decision'], row['person_note'] = o['decision'].strip(), (o.get('note') or '').strip()
        dec, code, by = o['decision'].strip(), (o.get('code') or '').strip() or code, 'team correction'
    if FINAL and dec == 'unsure':
        dec, code, by = 'exclude', 'E-UNSURE', 'rule: unsure after the authors\' check (D28)'
    row.update({'decision': dec, 'code': code, 'decided_by': by})
    out.append(row)

cols = ['rec', 'year', 'period', 'decision', 'code', 'decided_by', 'first_decision', 'first_code', 'first_confidence',
        'second_decision', 'second_code', 'third_decision', 'third_code', 'third_confidence', 'looks_decision', 'looks_code',
        'check_decision', 'check_code', 'rule_b', 'person_decision', 'person_note', 'ai_screen_decision', 'ai_screen_code', 'ai_screen_by']
(D / 'decisions').mkdir(exist_ok=True)
with open(D / 'decisions/screen_decisions.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    w.writerows(out)

dec = collections.Counter(r['decision'] for r in out)
by = collections.Counter(r['decided_by'] for r in out)
codes = {d: dict(collections.Counter(r['code'] for r in out if r['decision'] == d).most_common()) for d in dec}
per = {d: dict(sorted(collections.Counter(r['period'] for r in out if r['decision'] == d).items())) for d in dec}
inc_kind_period = collections.defaultdict(dict)
for r in out:
    if r['decision'] == 'include':
        inc_kind_period[r['code']][r['period']] = inc_kind_period[r['code']].get(r['period'], 0) + 1
tl = [r for r in out if r['third_decision']]   # every record the third look settled, whatever a later rule or correction did
adj = {'n': len(tl), 'decision': dict(collections.Counter(r['third_decision'] for r in tl)),
       'sided_with_first': sum(1 for r in tl if r['third_decision'] == r['first_decision']),
       'sided_with_second': sum(1 for r in tl if r['third_decision'] == r['second_decision']),
       'confidence': dict(collections.Counter(r['third_confidence'] for r in tl))}
summary = {'records': len(out), 'decision': dict(dec), 'decided_by': dict(by), 'codes': codes, 'by_period': per,
           'include_kind_by_period': {k: dict(sorted(v.items())) for k, v in sorted(inc_kind_period.items())},
           'adjudication': adj, 'team_corrections': len(over), 'third_look_missing': len(missing),
           'final_merge': FINAL,
           'final_merge_unsure_excluded': sum(1 for r in out if r['code'] == 'E-UNSURE'),
           'ai_screen': {'decision': dict(collections.Counter(r['ai_screen_decision'] for r in out)),
                         'codes': {d: dict(collections.Counter(r['ai_screen_code'] for r in out if r['ai_screen_decision'] == d).most_common())
                                   for d in sorted({r['ai_screen_decision'] for r in out})}},
           'team': {'rows': len(over), 'records': sum(1 for r in out if r['person_decision']),
                    'changes': dict(collections.Counter(f"{r['ai_screen_decision']}->{r['person_decision']}" for r in out if r['person_decision']))},
           'ai_check': {'files': [f.name for f in returns], 'rows_with_a_decision': len(ck), 'records_in_lists': len(ck_lists),
                        'final': dict(collections.Counter(r['ai_screen_decision'] for r in out if r['ai_screen_by'] == 'independent AI check')),
                        'looks_to_check': dict(collections.Counter(f"{r['looks_decision']}->{r['check_decision']}"
                                                                   for r in out if r['check_decision'])),
                        # the same, leaving out the records that the rule for removed records excludes in any case
                        'looks_to_check_not_withdrawn': dict(collections.Counter(
                            f"{r['looks_decision']}->{r['check_decision']}" for r in out
                            if r['check_decision'] and r['ai_screen_by'] != 'rule: removed by its repository'))},
           'rule_b': {'read': len(rb), 'applied_to': len(rb_applied),
                      'excluded': dict(collections.Counter(r['rule_b'] for r in out if r['ai_screen_by'] == 'rulings B and B2 (AI pass)')),
                      'unsure': dict(collections.Counter(r['rule_b'] for r in out if r['ai_screen_by'] == 'rulings B and B2 (AI pass), not settled'))},
           'withdrawn': {'n': sum(1 for r in out if r['ai_screen_by'] == 'rule: removed by its repository'),
                         'looks_decision': dict(collections.Counter(r['looks_decision'] for r in out
                                                                    if r['ai_screen_by'] == 'rule: removed by its repository')),
                         'listed': len(wd)},
           'periods': {p: f'{a}-{b}' for p, a, b in PERIODS},
           'rules': __doc__.split('Rules: ')[1].split(' Output:')[0]}
json.dump(summary, open(D / 'decisions/screen_decisions_summary.json', 'w', encoding='utf-8'), indent=1)
print(json.dumps({k: summary[k] for k in ('records', 'decision', 'decided_by', 'adjudication', 'team_corrections', 'third_look_missing')}, indent=1))
