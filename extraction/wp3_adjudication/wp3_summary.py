#!/usr/bin/env python3
"""WP3 summary: agreement of the two blind passes, Cohen's kappa, and what the AI adjudication changed, per field.

Inputs (all in the v16 folder):
  data/wp3_blind/DATA_extraction_all_values_compared.csv   1,706 values of the Data extraction sample (match column)
  data/wp3_blind/DATA_handling_agreement.json               agreement and kappa of the data-handling codes (76 papers)
  data/wp3_blind/METHOD_EVALUATION_agreement.json           agreement and kappa of the Method and Evaluation codes
  wp3/adjudication/*_adjudicated.csv                       one row per disagreement, with the adjudicated value
  wp3/adjudication/AGREEMENTS_checked.csv                  the 351 agreements checked (a seeded fifth)
Definitions:
  agreement      share of items on which the two passes give the same code or value
  corrected      the adjudicated value differs from a value the first pass recorded (a wrong value)
  filled         the first pass left the item blank and the adjudication fills it (printed, derived under D33, or the
                 class count of a two-class set under D32)
  kept           the first-pass value stands (the second pass was wrong, or both are the same value written differently,
                 or own reason and prior work merge under D34)
  changed share  (corrected + filled) / number of items in the sample; the agreements checked add their own changes
Writes WP3_summary.json and WP3_summary.md next to this script.
Usage: python3 -I wp3_summary.py <v16_dir> <team_repo>
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

V16 = Path(sys.argv[1])
HERE = Path(__file__).resolve().parent
B = V16 / 'data/wp3_blind'


def rd(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


def blank(v):
    return v.strip() in ('', 'NR', '?', 'not printed', 'n/a')


def classify(first, adj, how):
    if how in ('both', 'first', 'agree'):
        return 'kept'
    if adj.strip() == first.strip():
        return 'kept'
    return 'filled' if blank(first) else 'corrected'


def main():
    out = {}
    # Data extraction: 283 entries x 5 fields, 97 outcome rows x 3 fields
    cmp = rd(B / 'DATA_extraction_all_values_compared.csv')
    n = Counter(r['field'] for r in cmp)
    agree = Counter(r['field'] for r in cmp if r['match'] == 'True')
    adj = rd(HERE / 'DATA_extraction_adjudicated.csv')
    ch = defaultdict(Counter)
    for r in adj:
        ch[r['field']][classify(r['first_extraction'], r['adjudicated_value'], r['adjudication'])] += 1
    agr = rd(HERE / 'AGREEMENTS_checked.csv')
    fills_agr = Counter(r['field'] for r in agr if r['form'] == 'Data extraction' and r['result'].startswith('fill'))
    chk_agr = Counter(r['field'] for r in agr if r['form'] == 'Data extraction')
    de = {}
    for f in ['n_instances', 'n_features', 'n_classes', 'n_minority', 'ir_as_printed', 'metric', 'proposed', 'smote']:
        de[f] = dict(n=n[f], agreement=round(agree[f] / n[f], 3), disagreements=n[f] - agree[f],
                     kept=ch[f]['kept'], corrected=ch[f]['corrected'], filled=ch[f]['filled'],
                     agreements_checked=chk_agr[f], agreements_filled=fills_agr[f],
                     changed_share=round((ch[f]['corrected'] + ch[f]['filled']) / n[f], 3))
    tot_n = sum(n.values())
    tot_c = sum(ch[f]['corrected'] for f in de)
    tot_f = sum(ch[f]['filled'] for f in de)
    out['data_extraction'] = dict(fields=de, values=tot_n, agreement=round(sum(agree.values()) / tot_n, 3),
                                  corrected=tot_c, filled=tot_f, changed_share=round((tot_c + tot_f) / tot_n, 3),
                                  note='kappa is not computed for printed numbers; agreement is the share of identical values')
    # Data handling: 76 papers (origin labels: 73 papers with an evaluation)
    dh = json.load(open(B / 'DATA_handling_agreement.json', encoding='utf-8'))
    adj = rd(HERE / 'DATA_handling_adjudicated.csv')
    ch = defaultdict(Counter)
    for r in adj:
        f = r['field']
        how = r['adjudication']
        if f == 'crit_type' and how == 'both':
            ch[f]['kept'] += 1                       # own reason / prior work merged under D34
            continue
        ch[f][classify(r['first_pass'], r['adjudicated_value'], how)] += 1
    dhs = {}
    for f in ('crit_type', 'minority_rule'):
        dhs[f] = dict(n=dh[f]['n'], agreement=dh[f]['agreement'], kappa=dh[f]['kappa'], **dict(ch[f]))
    for lab, v in dh['origin'].items():
        f = 'origin:' + lab
        dhs[f] = dict(n=73, agreement=v['agreement'], kappa=v['kappa'], **dict(ch[f]))
    out['data_handling'] = dhs
    # paper-level counts after the adjudication (the first pass is the team's data_handling_matrix.csv)
    team = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if team:
        mat = list(csv.DictReader(open(team / 'Data section/out/data_handling_matrix.csv', encoding='utf-8-sig')))
        A = {(r['paper'], r['field']): r['adjudicated_value'] for r in adj}
        crit = {}
        for r in mat:
            if r['crit_type'] == 'n.a.':
                continue
            crit[r['key']] = A.get((r['key'], 'crit_type'), r['crit_type'])
        given = sum(v in ('own reason', 'cites prior work', 'reason given') for v in crit.values())
        binar = 0
        for r in mat:
            if r['origin'] in ('n.a.', ''):
                continue
            v = A.get((r['key'], 'origin:Binarised'))
            binar += (v == 'yes') if v is not None else ('Binarised' in r['origin'])
        out['paper_level_after_adjudication'] = dict(
            papers_with_evaluation=len(crit), reason_given=given, no_reason=len(crit) - given,
            reason_rule='D34: own reason or cited work counts; generic only ("widely used") and not stated do not',
            binarised_by_anyone=binar)
    # Method and Evaluation
    me = json.load(open(B / 'METHOD_EVALUATION_agreement.json', encoding='utf-8'))
    for form, fn, key in (('method', 'METHOD_adjudicated.csv', 'field'), ('evaluation', 'EVALUATION_adjudicated.csv', 'field')):
        adj = rd(HERE / fn)
        ch = defaultdict(Counter)
        for r in adj:
            ch[r[key]][classify(r['first_pass'], r['adjudicated_value'], r['adjudication'])] += 1
        out[form] = {'fields': me[form], 'adjudication': {k: dict(v) for k, v in ch.items()},
                     'items': len(adj), 'corrected': sum(v['corrected'] for v in ch.values()),
                     'filled': sum(v['filled'] for v in ch.values())}
    out['method']['decision_points_by_letter'] = {k: v for k, v in out['method']['adjudication'].items() if len(k) == 1}
    # agreements checked
    out['agreements_checked'] = dict(total=len(agr), by_form=dict(Counter(r['form'] for r in agr)),
                                     results=dict(Counter(r['result'].split(':')[0] for r in agr)),
                                     wrong_values_found=0, seed='20261111 (a fifth of the agreements of each form)')
    out['decided_by'] = 'AI adjudication (Claude Opus 5.5, 12 Nov 2026) under D31 to D36; spot check by the team lead pending'
    (HERE / 'WP3_summary.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
    # markdown
    L = ['# WP3: agreement of the blind passes and the AI adjudication, per field', '',
         'Generated by `wp3_summary.py` (12 Nov 2026). Agreement = share of identical codes or values of the two blind passes; '
         'corrected = a first-pass value replaced; filled = a first-pass blank filled (printed, D33 derived, or D32).', '',
         '## Data extraction (sample of 283 dataset entries and 97 printed comparisons)', '',
         '| Field | n | Agreement | Disagreements | Kept | Corrected | Filled | Changed |', '|---|---|---|---|---|---|---|---|']
    for f, v in de.items():
        L.append(f"| {f} | {v['n']} | {100 * v['agreement']:.1f}% | {v['disagreements']} | {v['kept']} | {v['corrected']} | "
                 f"{v['filled']} | {100 * v['changed_share']:.1f}% |")
    d = out['data_extraction']
    L += [f"| all | {d['values']} | {100 * d['agreement']:.1f}% | {sum(v['disagreements'] for v in de.values())} | | "
          f"{d['corrected']} | {d['filled']} | {100 * d['changed_share']:.1f}% |", '',
          '## Data-handling codes (76 papers; origin labels on the 73 papers with an evaluation)', '',
          '| Field | Agreement | Kappa | Kept | Corrected | Filled |', '|---|---|---|---|---|---|']
    for f, v in dhs.items():
        L.append(f"| {f} | {v['agreement']} | {v['kappa']} | {v.get('kept', 0)} | {v.get('corrected', 0)} | {v.get('filled', 0)} |")
    for form in ('method', 'evaluation'):
        L += ['', f'## {form.capitalize()} form', '', '| Field | n | Agreement | Kappa | Kept | Corrected |', '|---|---|---|---|---|---|']
        for f, v in out[form]['fields'].items():
            a = {}
            for k, c in out[form]['adjudication'].items():
                if k == f or (form == 'method' and f == 'decision points' and len(k) == 1):
                    for kk, cc in c.items():
                        a[kk] = a.get(kk, 0) + cc
            L.append(f"| {f} | {v['n']} | {v['agreement']} | {v['kappa']} | {a.get('kept', 0)} | {a.get('corrected', 0)} |")
    a = out['agreements_checked']
    L += ['', '## Agreements checked (seeded fifth, 351 items)', '',
          f"By form: {a['by_form']}. Results: {a['results']}. No agreed value was wrong; 13 values that both passes left blank "
          'follow from the paper under D32 (class count 2 of a two-class set, 9) or D33 (a total or a printed share, 4).']
    (HERE / 'WP3_summary.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
