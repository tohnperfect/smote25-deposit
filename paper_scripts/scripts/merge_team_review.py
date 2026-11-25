#!/usr/bin/env python3
"""Turn the team's decisions from the review page (artifact "SMOTE25 Screen Check") into overrides of the screen.

Input: the page's CSV export (Summary and export > Download CSV), one row per record and reviewer:
  rec, title, year, queue, ai_decision, ai_code, ai_decided_by, reviewer, reviewer_id, mode, person_decision,
  person_code, note, decided_at, agrees_with_ai
A session can write the same file from the artifact's database instead: db_list "reviewers" (author per reviewer
id), then db_list "reviews/<id>/buckets" for each id; every bucket document maps a record to
{d: decision, c: code, n: note, t: time, m: "blind" or "open", q: queue}. Entries with an empty d were cleared.

Rule: a record whose reviewers all give the same decision, different from the screen's, becomes an override
(person_overrides.csv: rec, decision, code, note). Reviewers who disagree with each other send the record to the
team lead (conflicts.csv); nothing is written for it. Agreements with the screen change nothing but are counted.
Usage: python3 -I merge_team_review.py <export.csv> <screening_full dir> [--apply]
Writes check/team_review/{merge_summary.json, proposed_overrides.csv, conflicts.csv}; --apply also merges the
proposals into person_overrides.csv (a proposal replaces an earlier override of the same record).
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXPORT, SF = Path(sys.argv[1]), Path(sys.argv[2])
APPLY = '--apply' in sys.argv
OUT = SF / 'check' / 'team_review'
OUT.mkdir(parents=True, exist_ok=True)
VALID = {'include', 'exclude', 'unsure'}

with open(SF / 'decisions' / 'screen_decisions.csv', encoding='utf-8', newline='') as f:
    screen = {r['rec']: r for r in csv.DictReader(f)}
with open(EXPORT, encoding='utf-8-sig', newline='') as f:
    rows = [r for r in csv.DictReader(f) if r.get('person_decision')]

by_rec = defaultdict(dict)
for r in rows:
    if r['person_decision'] not in VALID:
        sys.exit(f"{r['rec']}: unknown decision {r['person_decision']!r}")
    if r['rec'] not in screen:
        sys.exit(f"{r['rec']}: not a record of the screen")
    prev = by_rec[r['rec']].get(r['reviewer_id'])
    if prev is None or r['decided_at'] > prev['decided_at']:
        by_rec[r['rec']][r['reviewer_id']] = r

proposals, conflicts, agree = [], [], 0
for rec, revs in sorted(by_rec.items()):
    ai = screen[rec]['decision']
    decs = {r['person_decision'] for r in revs.values()}
    if len(decs) > 1:
        conflicts.append({'rec': rec, 'ai_decision': ai, 'ai_code': screen[rec]['code'],
                          'reviewers': '; '.join(f"{r['reviewer']}: {r['person_decision']} {r['person_code']} {r['note']}".strip()
                                                 for r in revs.values())})
        continue
    d = decs.pop()
    if d == ai:
        agree += 1
        continue
    codes = Counter(r['person_code'] for r in revs.values())
    code = codes.most_common(1)[0][0]
    names = ', '.join(sorted(r['reviewer'] for r in revs.values()))
    notes = ' | '.join(r['note'] for r in revs.values() if r['note'])
    proposals.append({'rec': rec, 'decision': d, 'code': code,
                      'note': f'team check ({names})' + (f': {notes}' if notes else '')})


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == 'include' for a, _ in pairs) / n
    pb = sum(b == 'include' for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe >= 1 else round((po - pe) / (1 - pe), 3)


blind = defaultdict(list)
per_reviewer = Counter()
for rec, revs in by_rec.items():
    for r in revs.values():
        per_reviewer[r['reviewer']] += 1
        if r['mode'] == 'blind' and r['person_decision'] != 'unsure':
            blind[r['reviewer']].append((r['ai_decision'], r['person_decision']))
summary = {
    'export': EXPORT.name, 'records_decided': len(by_rec), 'decisions': sum(len(v) for v in by_rec.values()),
    'per_reviewer': dict(per_reviewer), 'same_as_screen': agree, 'proposed_overrides': len(proposals),
    'conflicts': len(conflicts),
    'proposed_by_decision': dict(Counter(p['decision'] for p in proposals)),
    'blind': {k: {'n': len(v), 'agree': sum(a == b for a, b in v), 'kappa': kappa(v)} for k, v in blind.items()},
}
(OUT / 'merge_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
for name, data, cols in (('proposed_overrides.csv', proposals, ['rec', 'decision', 'code', 'note']),
                         ('conflicts.csv', conflicts, ['rec', 'ai_decision', 'ai_code', 'reviewers'])):
    with open(OUT / name, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(data)
print(json.dumps(summary, indent=1))

if APPLY:
    po = SF / 'person_overrides.csv'
    with open(po, encoding='utf-8', newline='') as f:
        old = {r['rec']: r for r in csv.DictReader(f)}
    for p in proposals:
        old[p['rec']] = p
    with open(po, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['rec', 'decision', 'code', 'note'])
        w.writeheader()
        w.writerows(old[k] for k in sorted(old))
    print(f'person_overrides.csv: {len(old)} rows; next: the chain in the README of the screening folder')
