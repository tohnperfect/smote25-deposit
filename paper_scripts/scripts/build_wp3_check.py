#!/usr/bin/env python3
"""Build records.json of the review page "SMOTE25 WP3 Check": the team lead's spot check of the AI adjudication (D31).

The page shows each AI adjudication with both passes and the reason, and the reviewer agrees or gives the right value.
It is not blind: a spot check judges a decision that has been made. Items (seeded draws rank by a hash of seed and key):
  must    every adjudication that changes a number of the paper: every paper read for "modified data released" (D36),
          the six GLOS entries recoded as modified (one item), the variant taken in four papers (D35)
  changed adjudications that replaced or filled a first-pass value: 15 of the Data extraction values, 10 of the
          data-handling codes (seed 20261121), and all Method and Evaluation corrections
  kept    8 adjudications that kept the first pass (seed 20261122)
  fill    5 of the 13 blanks of the agreements check filled under D32 or D33 (seed 20261123)
Usage: python3 -I scripts/build_wp3_check.py <v16_dir> <out_dir>
Writes out_dir/records.json (short quotes from the papers: team use only, never deposited; the script rebuilds it).
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

V, OUT = Path(sys.argv[1]), Path(sys.argv[2])
A = V / 'wp3/adjudication'
SEED_CH, SEED_KEPT, SEED_FILL = 20261121, 20261122, 20261123


def rank(seed, key):
    return hashlib.sha256(f'{seed}:{key}'.encode()).hexdigest()


def rd(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


def blank(v):
    return v.strip() in ('', 'NR', '?', 'not printed', 'n/a')


def how(first, adj, h):
    if h in ('both', 'first', 'agree') or adj.strip() == first.strip():
        return 'kept'
    return 'filled' if blank(first) else 'corrected'


MOD = {'yes': 'modifies data (one of the 43 of the Data section)', 'recoded (GLOS recount)': 'modifies data (added by the GLOS recount)',
       'no': 'modifies no data in the Data definition (outside the count)'}
items = []
# ---- must: D36
for r in rd(A / 'MODIFIED_RELEASED_adjudicated.csv'):
    items.append(dict(key='rel_' + r['paper'], group='must', form='Data handling', topic='Modified data released (D36)',
                      paper=r['paper'], item='the paper', field='modified files themselves public',
                      first=('Data: yes' if r['data_first_pass'] else 'Data: not listed') + '; ' +
                      ('Evaluation: yes' if r['evaluation_first_pass'] else 'Evaluation: no'),
                      second=r['second_pass'] or 'not coded', adjudicated=r['adjudicated'],
                      how='decision', note=r['note'], evidence=f"{r['where']}: \"{r['quote']}\"",
                      extra=MOD[r['in_43']] + f"; confidence {r['confidence']}"))
# ---- must: GLOS
g = json.load(open(A / 'GLOS_recount.json', encoding='utf-8'))
ge = rd(A / 'GLOS_entries_recoded.csv')
items.append(dict(key='glos', group='must', form='Data extraction', topic='GLOS entries recoded as modified',
                  paper='GLOS', item=', '.join(e['name_as_reported'] for e in ge), field='how the data were obtained',
                  first='verified sheet: ' + ', '.join(f"{e['name_as_reported']} {e['category_before']}" for e in ge),
                  second='second pass: the paper induces an imbalance profile (origin label)', adjudicated='modified (all six)',
                  how='corrected', note='The originals are balanced (UCI Segment 330 per class, KEEL Texture 500 per class); '
                  'GLOS prints IR 9.9 and 10. Counted, 44 papers modify data (347 entries).',
                  evidence=ge[0]['evidence_ref'], extra='changes: ' + json.dumps(g['changed'])))
# ---- must: D35
d35 = rd(V / 'data/d35/d35_changes.csv')
VAR = {'NBU': ('NB-Comm', 'NB-Basic', 'abstract: "Four methods based on neighbourhood searching ... are proposed" (none named); '
               'the paper names NB-Basic first'),
       'RACOG': ('wRACOG', 'RACOG', 'abstract: "We introduce two probabilistic oversampling approaches, namely RACOG and wRACOG"'),
       'SMOTE-ENN': ('Smote+ENN', 'Smote+Tomek', 'abstract, p.1: "Two of our proposed methods, Smote + Tomek and Smote + ENN, presented very good results"'),
       'SOS': ('Sub-VP', 'VE', 'abstract names no variant; Section 2: "variance exploding (VE), ii) variance preserving (VP), and '
               'ii) sub-variance preserving (Sub-VP)"')}
for p, (old, new, ev) in VAR.items():
    rows = [r for r in d35 if r['paper'] == p]
    ch = [r for r in rows if r['changed'] == 'yes']
    items.append(dict(key='d35_' + p, group='must', form='Data extraction', topic='Proposed variant (D35)', paper=p,
                      item=f'{len(rows)} printed comparisons', field='which variant is "the proposed method"',
                      first=f'extraction: {old}', second='second pass, sampled rows: ' + ('the first-named variant' if p != 'SOS' else 'VE'),
                      adjudicated=new, how='corrected', note=f'{len(ch)} of {len(rows)} comparisons change result: ' +
                      '; '.join(f"{r['dataset']} {r['metric'][:14]} {r['old_result']}->{r['new_result']}" for r in ch[:8]) +
                      (' ...' if len(ch) > 8 else ''), evidence=ev,
                      extra='all 29 papers: 79.5% of decided comparisons before, 79.0% after (data/d35/)'))
# ---- changed and kept adjudications
pool_ch, pool_kept = {}, []
for fn, form, fk, ik in (('DATA_extraction_adjudicated.csv', 'Data extraction', 'first_extraction', None),
                         ('DATA_handling_adjudicated.csv', 'Data handling', 'first_pass', None),
                         ('METHOD_adjudicated.csv', 'Method', 'first_pass', None),
                         ('EVALUATION_adjudicated.csv', 'Evaluation', 'first_pass', None)):
    for i, r in enumerate(rd(A / fn)):
        if r.get('adjudication') == 'agree':
            continue
        paper = r.get('paper') or r.get('study')
        it = r.get('item') or ''
        k = f"{form[:4]}_{r.get('check_id') or paper}_{it}_{r['field']}".replace(' ', '_')
        h = how(r[fk], r['adjudicated_value'], r['adjudication'])
        rec = dict(key=k, form=form, topic=r['field'], paper=paper, item=it or 'the paper', field=r['field'],
                   first=r[fk], second=r['second_pass'], adjudicated=r['adjudicated_value'], how=h,
                   note=r.get('adjudication_note', ''), evidence=(r.get('second_pass_note') or r.get('second_pass_evidence') or ''),
                   extra=(('first-pass quote: ' + r['first_pass_quote']) if r.get('first_pass_quote') else (r.get('category') or '')))
        if h == 'kept':
            pool_kept.append(rec)
        else:
            pool_ch.setdefault(form, []).append(rec)
for form, n in (('Data extraction', 15), ('Data handling', 10), ('Method', 99), ('Evaluation', 99)):
    for rec in sorted(pool_ch.get(form, []), key=lambda r: rank(SEED_CH, r['key']))[:n]:
        items.append(dict(rec, group='changed'))
for rec in sorted(pool_kept, key=lambda r: rank(SEED_KEPT, r['key']))[:8]:
    items.append(dict(rec, group='kept'))
# ---- fills of the agreements check
for r in sorted([r for r in rd(A / 'AGREEMENTS_checked.csv') if r['result'].startswith('fill')],
                key=lambda r: rank(SEED_FILL, r['item'] + r['field']))[:5]:
    items.append(dict(key='agr_' + (r['item'] + '_' + r['field']).replace(' ', '_'), group='fill', form=r['form'],
                      topic='blank in both passes', paper=r['item'].split(' ', 1)[1].split(' / ')[0], item=r['item'],
                      field=r['field'], first='(blank)', second='(blank)', adjudicated=r['result'].split(': ', 1)[1],
                      how='filled', note=r['where'], evidence='', extra='agreements check'))
for i in items:
    i['id'] = 'i' + hashlib.sha256(i['key'].encode()).hexdigest()[:10]
keys = [i['id'] for i in items]
assert len(keys) == len(set(keys)), 'STOP: duplicate keys'
meta = dict(title='SMOTE25 WP3 Check', built='2026-11-12', n=len(items),
            groups={g: sum(i['group'] == g for i in items) for g in ('must', 'changed', 'kept', 'fill')},
            seeds=dict(changed=SEED_CH, kept=SEED_KEPT, fill=SEED_FILL),
            frames=dict(changed={k: len(v) for k, v in pool_ch.items()}, kept=len(pool_kept)))
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'records.json').write_text(json.dumps(dict(meta=meta, items=items), ensure_ascii=False, indent=0), encoding='utf-8')
print(json.dumps(meta))
