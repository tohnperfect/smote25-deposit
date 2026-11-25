#!/usr/bin/env python3
"""Merge the authors' decisions from the page "SMOTE25 Section 8 Check" (decision D41) into the WP5 folders.

Input: the page's CSV export (Summary and export > Download CSV), one row per decision. When several authors decided
the same record, a record on which they agree is merged; one on which they disagree goes to
wp5/section8_conflicts.csv for the team lead and is not merged.
  harm  every record where the authors' decision, code or finding differs from the AI's becomes a row of
        wp5/harm_search/proposed_overrides.csv (pmid, decision, code, harms, comparison, finding, note; empty fields keep
        the AI's value, as scripts/build_results.py there reads them). --apply merges them into person_overrides.csv
        (a row for the same PMID is replaced). Then: cd wp5/harm_search && python3 -I scripts/build_results.py, and the
        search chain (search_numbers.py, render_search_text.py) regenerates Section 8.5 and S6.
  case  likewise wp5/case_search/proposed_overrides.csv and person_overrides.csv (pmid, decision, group,
        compares_no_resampling, exclusion_reason, note). The case search is not yet in the paper's text (Section 8.4).
  tags  with --apply the codes go into the columns health_application, smote_use and notes of the sheet "check" of
        wp5/wp5_tag_check_blind.xlsx; then python3 scripts/wp5_first_pass.py data/openalex/2026-11-10 wp5/ --agreement.
Always writes wp5/section8_check_summary.json: per check and reviewer, the records decided, the agreement and Cohen's
kappa with the AI, and for the two searches the decision agreement weighted to the full set of records (the exclusions
were sampled: each stratum of the AI's decisions is weighted by its size in the search over its size in the check).
Usage: python3 -I scripts/merge_section8_review.py EXPORT.csv DRAFT_DIR [--apply]
"""
import collections
import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(10**9)
EXPORT, R = Path(sys.argv[1]), Path(sys.argv[2])
APPLY = '--apply' in sys.argv
W = R / 'wp5'
FRAME = {'harm': {'include': 27, 'unsure': 49, 'exclude': 353}, 'case': {'include': 141, 'unsure': 23, 'exclude': 187}}

rows = [r for r in csv.DictReader(open(EXPORT, encoding='utf-8-sig')) if r.get('check')]
by_rec = collections.defaultdict(list)
for r in rows:
    by_rec[(r['check'], r['id'])].append(r)


def sig(r):
    if r['check'] == 'tags':
        return (r['person_health'], r['person_use'])
    if r['check'] == 'harm':
        return (r['person_decision'], r['person_code'], r['person_finding'])
    return (r['person_decision'], r['person_group'], r['person_compares'], r['person_exclusion_reason'])


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return {'n': n, 'agree': sum(a == b for a, b in pairs), 'agreement': round(po, 4),
            'kappa': round((po - pe) / (1 - pe), 4) if pe < 1 else None}


# ---------- agreement per reviewer ----------
summary = {'export': EXPORT.name, 'rows': len(rows), 'reviewers': sorted({r['reviewer'] for r in rows}), 'checks': {}}
for check in ('harm', 'case', 'tags'):
    out = {}
    for rev in sorted({r['reviewer'] for r in rows if r['check'] == check}):
        rr = [r for r in rows if r['check'] == check and r['reviewer'] == rev]
        m = {'decided': len(rr)}
        if check == 'tags':
            m['health_application'] = kappa([(r['ai_health'], r['person_health']) for r in rr])
            m['smote_use'] = kappa([(r['ai_use'], r['person_use']) for r in rr])
        else:
            m['decision'] = kappa([(r['ai_decision'], r['person_decision']) for r in rr])
            both = [r for r in rr if r['ai_decision'] == 'include' and r['person_decision'] == 'include']
            if check == 'harm':
                m['code_both_include'] = kappa([(r['ai_code'], r['person_code']) for r in both])
                m['finding_both_include'] = kappa([(r['ai_finding'], r['person_finding']) for r in both])
            else:
                m['group_both_include'] = kappa([(r['ai_group'], r['person_group']) for r in both])
                m['compares_both_include'] = kappa([(r['ai_compares'], r['person_compares']) for r in both])
            strata, num, den = {}, 0.0, 0
            for s, size in FRAME[check].items():
                ss = [r for r in rr if r['ai_decision'] == s]
                if ss:
                    rate = sum(r['person_decision'] == s for r in ss) / len(ss)
                    strata[s] = {'checked': len(ss), 'kept': sum(r['person_decision'] == s for r in ss),
                                 'changed_to': dict(collections.Counter(r['person_decision'] for r in ss if r['person_decision'] != s))}
                    num += size * rate
                    den += size
            m['by_ai_decision'] = strata
            m['decision_agreement_weighted_to_search'] = round(num / den, 4) if den else None
        out[rev] = m
    summary['checks'][check] = out

# ---------- consensus per record ----------
conflicts, agreed = [], {}
for key, rs in by_rec.items():
    if len({sig(r) for r in rs}) > 1:
        conflicts.extend(rs)
    else:
        agreed[key] = rs[0]
summary['conflicts'] = len({(r['check'], r['id']) for r in conflicts})
if conflicts:
    with open(W / 'section8_conflicts.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, list(conflicts[0].keys()))
        w.writeheader()
        w.writerows(conflicts)


def note(r):
    return f"author check (D41), {r['reviewer']}" + (f": {r['note']}" if r['note'] else '')


def write(path, cols, new):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(new)


def merge_into(path, cols, new):
    old = list(csv.DictReader(open(path, encoding='utf-8'))) if path.exists() else []
    ids = {n['pmid'] for n in new}
    write(path, cols, [o for o in old if o.get('pmid') not in ids] + new)


harm_cols = ['pmid', 'decision', 'code', 'harms', 'comparison', 'finding', 'note']
harm_new = []
for (check, pid), r in sorted(agreed.items()):
    if check != 'harm':
        continue
    if (r['person_decision'], r['person_code'], r['person_finding'] or r['ai_finding']) == (r['ai_decision'], r['ai_code'], r['ai_finding']):
        continue
    harm_new.append({'pmid': pid, 'decision': r['person_decision'], 'code': r['person_code'], 'harms': '', 'comparison': '',
                     'finding': r['person_finding'] if r['person_decision'] != 'exclude' else 'n/a', 'note': note(r)})
write(W / 'harm_search/proposed_overrides.csv', harm_cols, harm_new)

case_cols = ['pmid', 'decision', 'group', 'compares_no_resampling', 'exclusion_reason', 'note']
case_new = []
for (check, pid), r in sorted(agreed.items()):
    if check != 'case':
        continue
    same = r['person_decision'] == r['ai_decision'] and (r['person_decision'] != 'include' or
                                                          (r['person_group'], r['person_compares']) == (r['ai_group'], r['ai_compares']))
    if same:   # the AI's exclusions carry no reason code, so a kept exclusion needs no row
        continue
    case_new.append({'pmid': pid, 'decision': r['person_decision'], 'group': r['person_group'],
                     'compares_no_resampling': r['person_compares'], 'exclusion_reason': r['person_exclusion_reason'], 'note': note(r)})
write(W / 'case_search/proposed_overrides.csv', case_cols, case_new)

tags = {pid: r for (check, pid), r in agreed.items() if check == 'tags'}
summary['proposed'] = {'harm': len(harm_new), 'case': len(case_new), 'tags_coded': len(tags)}
if APPLY:
    merge_into(W / 'harm_search/person_overrides.csv', harm_cols, harm_new)
    merge_into(W / 'case_search/person_overrides.csv', case_cols, case_new)
    if tags:
        import openpyxl
        wb = openpyxl.load_workbook(W / 'wp5_tag_check_blind.xlsx')
        ws = wb['check']
        head = [c.value for c in ws[1]]
        ci = {k: head.index(k) + 1 for k in ('health_application', 'smote_use', 'notes')}
        for row in range(2, ws.max_row + 1):
            oid = ws.cell(row, 1).value
            if oid in tags:
                ws.cell(row, ci['health_application']).value = tags[oid]['person_health']
                ws.cell(row, ci['smote_use']).value = tags[oid]['person_use']
                ws.cell(row, ci['notes']).value = note(tags[oid])
        wb.save(W / 'wp5_tag_check_blind.xlsx')
    summary['applied'] = True
(W / 'section8_check_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
print(json.dumps({k: summary[k] for k in ('rows', 'reviewers', 'conflicts', 'proposed')}, indent=1))
