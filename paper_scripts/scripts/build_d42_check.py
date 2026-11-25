#!/usr/bin/env python3
"""Build records.json of the page "SMOTE25 Samples Check": the authors' spot check of the AI adjudication of the blind
second coding of the two samples (D42).

Each card shows one code of one record: the first coder's value, the blind second coder's value, the AI adjudication
and its reason, the evidence each coder quoted, and whether the record was coded from the full text. Items (seeded
draws rank by a hash of seed and key):
  must    every correction of a first code that can change a count of the paper: in the use audit is_application,
          domain, stakes, inside_folds, test_balanced, vs_none, vs_weights, calibration and validation, and the
          corrections of modality, resampler, learner and measures that change what the paper counts (tabular data,
          plain SMOTE, a deep network; accuracy, ROC-AUC and PR-AUC in the full texts it counts); in the coverage
          sample eligible, exclusion and label, and any correction of an eligible paper (v0.25)
  changed the other corrections, up to 15 (seed 20261125)
  kept    10 adjudications that kept the first code (seed 20261126)
  fill    10 codes on which both coders agreed, in the fields of `must`, not na, and a safeguard only where the
          record was coded from a full text (seed 20261127)
Round 2 (v0.37, `--round2`): the adjudication of round 2 (d42/round2/: its second codes and adjudication log), the
same groups with seeds 20261128 (changed), 20261129 (kept) and 20261130 (agreed, among the records of round 2), and
keys prefixed `r2_`, so that its item ids differ from those of round 1 on the same page.
Round 3 (v0.38, `--round3`): the adjudication of round 3 (d42/round3/: the coverage papers that joined the sample at
the final merge, D28), the same groups with seeds 20261133 (changed), 20261134 (kept) and 20261135 (agreed, among the
records of round 3), keys prefixed `r3_`.
Usage: python3 -I scripts/build_d42_check.py <draft_dir> <d42 work dir> <out_dir> [--round2 | --round3]
Writes out_dir/records.json (titles and short quotes from the records: team use only, never deposited).
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ARGS = sys.argv[1:]
ROUND2 = '--round2' in ARGS
ROUND3 = '--round3' in ARGS
assert not (ROUND2 and ROUND3), 'STOP: one round at a time'
ARGS = [a for a in ARGS if a not in ('--round2', '--round3')]
V, D, OUT = (Path(a) for a in ARGS)
S = V / 'data/search/screening_full_2026-11-11'
K = S / 'd42'
KR = K / 'round2' if ROUND2 else K / 'round3' if ROUND3 else K   # the round's second codes and adjudication log
PFX = 'r2_' if ROUND2 else 'r3_' if ROUND3 else ''
SEED_CH, SEED_KEPT, SEED_AGR = ((20261128, 20261129, 20261130) if ROUND2 else (20261133, 20261134, 20261135) if ROUND3
                                else (20261125, 20261126, 20261127))
csv.field_size_limit(10**9)
MUST = {'useaudit': {'is_application', 'domain', 'stakes', 'inside_folds', 'test_balanced', 'vs_none', 'vs_weights',
                     'calibration', 'validation'},
        'coverage': {'eligible', 'exclusion', 'label'}}
LABEL = {'is_application': 'application of existing resampling', 'domain': 'domain', 'stakes': 'a decision about a person',
         'modality': 'type of data', 'resampler': 'resampler', 'learner': 'learner',
         'inside_folds': 'resampling fitted on the training data only', 'vs_none': 'compared with no resampling',
         'vs_weights': 'compared with class weights or a threshold', 'measures': 'measures', 'calibration': 'calibration assessed',
         'validation': 'validation', 'test_balanced': 'test data resampled', 'source': 'source of the codes',
         'fulltext_ok': 'full text usable', 'eligible': 'eligible', 'exclusion': 'exclusion', 'label': 'label',
         'generator': 'kind of generator', 'S': 'decision changed: seed selection', 'A': 'decision changed: sample allocation',
         'N': 'decision changed: neighbor choice', 'P': 'decision changed: placement rule', 'F': 'decision changed: post-filtering',
         'L': 'decision changed: inside a pipeline', 'class': 'class category', 'n_datasets': 'number of data sets',
         'vs_smote': 'compared with SMOTE', 'vs_cost': 'compared with cost-sensitive learning', 'protocol': 'evaluation protocol',
         'tuning': 'tuning', 'stat_test': 'statistical test', 'code': 'code released'}
FORM = {'useaudit': 'Use audit', 'coverage': 'Coverage sample'}


def rank(seed, key):
    return hashlib.sha256(f'{seed}:{key}'.encode()).hexdigest()


def rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


titles = {}
for proj in ('useaudit', 'coverage'):   # v0.25: from the samples (in the package); the work dir's batches only fill gaps
    for r in rows(S / f'samples/{proj}_sample.csv'):
        titles[(proj, r['rec'])] = ' '.join(r['title'].split())
    for b in sorted((D / proj / 'batches').glob('batch*.csv')):
        for r in rows(b):
            titles.setdefault((proj, r['rec']), ' '.join(r['title'].split()))
    # v0.38: a paper that left the coverage sample at the final merge (D28) keeps its title from the screen's records
    for r in rows(S / 'final/screen_final.csv'):
        titles.setdefault((proj, r['rec']), ' '.join(r['title'].split()))
first = {p: {r['rec']: r for r in rows(S / f'{p}/coded.csv')} for p in ('useaudit', 'coverage')}
second = {p: {r['rec']: r for r in rows(KR / f'second_codes_{p}.csv')} for p in ('useaudit', 'coverage')}
log = rows(KR / 'adjudication_log.csv')


def base(proj, rec, field):
    t = titles.get((proj, rec), '')
    ev1, ev2 = first[proj][rec].get('evidence', ''), second[proj].get(rec, {}).get('evidence', '')
    src = second[proj].get(rec, {}).get('source', 'fulltext' if proj == 'coverage' else '')
    return dict(form=FORM[proj], topic=LABEL.get(field, field), paper=f'{rec}: {t[:90]}' + ('...' if len(t) > 90 else ''),
                item=rec, field=field, evidence=f'first coder: {ev1 or "-"} | second coder: {ev2 or "-"}',
                extra='coded from the full text' if src == 'fulltext' else 'coded from the title and abstract')


sys.path.insert(0, str(Path(__file__).resolve().parent))
from rulings import decide  # noqa: E402
_rf = {r['rec']: r for r in rows(S / 'coverage/rulings_fulltext_facts.csv')}
_cov_adj = {r['rec']: r for r in rows(K / 'coverage_coded_adjudicated.csv')}
_fl = {r['rec']: r for r in rows(S / 'useaudit/fetch_log.csv')}
FT_COUNTED = {r['rec'] for r in rows(S / 'samples/useaudit_sample.csv')
              if r['target'] == 'fulltext' and _fl.get(r['rec'], {}).get('usable') == 'yes'}


def cov_eligible(rec_id):
    c = _cov_adj.get(rec_id, {})
    return c.get('eligible') == 'yes' and not (rec_id in _rf and decide(_rf[rec_id])[1] == 'exclude')


def must(x):
    """v0.25: a correction that can change a count that the paper prints."""
    f, a, b = x['field'], x['first'], x['adjudicated']
    if x['project'] == 'coverage':
        return f in MUST['coverage'] or cov_eligible(x['rec'])
    if f in MUST['useaudit']:
        return True
    A, B = set(a.split(';')), set(b.split(';'))
    if f == 'modality':
        return (a == 'tabular') != (b == 'tabular')
    if f == 'resampler':
        return ('SMOTE' in A) != ('SMOTE' in B)
    if f == 'learner':
        return ('deep-net' in A) != ('deep-net' in B)
    if f == 'measures':
        return x['rec'] in FT_COUNTED and x['source'] == 'fulltext' and any((m in A) != (m in B) for m in ('accuracy', 'ROC-AUC', 'PR-AUC'))
    return False


FT_ONLY = {'inside_folds', 'test_balanced', 'vs_none', 'vs_weights', 'calibration'}
items, pool_ch, pool_kept = [], [], []
for x in log:
    rec = dict(base(x['project'], x['rec'], x['field']), key=f'{PFX}adj_{x["project"]}_{x["rec"]}_{x["field"]}',
               first=x['first'], second=x['second'], adjudicated=x['adjudicated'],
               how='kept' if x['how'] == 'kept' else ('corrected to the second code' if x['chosen'] == 'second' else 'corrected'),
               note=f'{x["reason"]} (confidence {x["confidence"]})')
    if x['how'] == 'corrected' and must(x):
        items.append(dict(rec, group='must'))
    elif x['how'] == 'corrected':
        pool_ch.append(rec)
    else:
        pool_kept.append(rec)
for rec in sorted(pool_ch, key=lambda r: rank(SEED_CH, r['key']))[:15]:
    items.append(dict(rec, group='changed'))
for rec in sorted(pool_kept, key=lambda r: rank(SEED_KEPT, r['key']))[:10]:
    items.append(dict(rec, group='kept'))
disagree = {(x['project'], x['rec'], x['field']) for x in log}
agreed = []
for proj in ('useaudit', 'coverage'):
    for rec_id, s in second[proj].items():
        for f in sorted(MUST[proj]):
            if (proj, rec_id, f) not in disagree and rec_id in first[proj]:
                v = first[proj][rec_id].get(f, '')
                # v0.25: informative codes only (not na; a safeguard only where the record was coded from a full text)
                if v.strip() in ('', 'na') or (proj == 'useaudit' and f in FT_ONLY and first[proj][rec_id].get('source') != 'fulltext'):
                    continue
                agreed.append(dict(base(proj, rec_id, f), key=f'{PFX}agr_{proj}_{rec_id}_{f}', first=v, second=s.get(f, ''),
                                   adjudicated=v, how='agreed', note='both coders gave this code'))
for rec in sorted(agreed, key=lambda r: rank(SEED_AGR, r['key']))[:10]:
    items.append(dict(rec, group='fill'))
for i in items:
    i['id'] = 'i' + hashlib.sha256(i['key'].encode()).hexdigest()[:10]
ids = [i['id'] for i in items]
assert len(ids) == len(set(ids)), 'STOP: duplicate keys'
meta = dict(title='SMOTE25 Samples Check' + (', round 2' if ROUND2 else ', round 3' if ROUND3 else ''),
            built='2026-11-16' if ROUND2 else '2026-11-17' if ROUND3 else '2026-11-14',
            n=len(items),
            groups={g: sum(i['group'] == g for i in items) for g in ('must', 'changed', 'kept', 'fill')},
            seeds=dict(changed=SEED_CH, kept=SEED_KEPT, agreed=SEED_AGR),
            frames=dict(changed=len(pool_ch), kept=len(pool_kept), agreed=len(agreed)))
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'records.json').write_text(json.dumps(dict(meta=meta, items=items), ensure_ascii=False, indent=0), encoding='utf-8')
print(json.dumps(meta))
