#!/usr/bin/env python3
"""D42: compile the AI adjudication of the blind second coding into adjudicated codes.

For every disagreement the adjudicator chose code A, code B (which of the two coders each letter was is in the key) or
another value. The adjudicated value replaces the first code in a copy of each project's coded.csv
(`<out>/<project>_coded_adjudicated.csv`, the same columns, so that analyze_samples.py can read it in place of
coded.csv); `<out>/adjudication_log.csv` keeps every item with both codes, the decision, the reason and the
confidence (short quotes: team use only, never deposited; `<out>/adjudication_decisions.csv` is the same without
the reasons, for the deposit); `<out>/adjudication_summary.json` counts them.
Second round (v0.37): with `--round2 <dir>`, the items of round 2 (<dir>/disagreements.csv, <dir>/adjudication_raw/,
<dir>/adjudication_key.json) are compiled the same way into <dir>, and the adjudicated codes in <out> rest on both
rounds. A record coded again in round 2 (listed in <dir>/second_codes_<project>.csv) takes the corrections of round 2
only, since both of its round-1 codes were replaced; every other record takes those of round 1, whose first codes must
be unchanged. The spot-check overrides of each round (<out>/spot_check_overrides.csv, <dir>/spot_check_overrides.csv)
apply in the same way. <dir>/adjudication_summary.json also counts, under `in_force`, the items of both rounds that the
adjudicated codes rest on.
Third round (v0.38): with `--round3 <dir>` as well, the items of round 3 (the coverage papers that joined the sample
at the final merge, D28) are compiled the same way into <dir> and the adjudicated codes rest on all three rounds;
<dir>/adjudication_summary.json counts under `in_force` the items that the codes of the samples as they now stand rest
on (`samples/coverage_sample.csv`, `samples/useaudit_sample.csv`): the items of papers that left the coverage sample at
the final merge no longer count (`left_sample_items`).
Usage: python3 -I scripts/d42_compile.py <draft_dir> <disagreements.csv> <decisions dir> <key.json> <out_dir>
       [--round2 <dir> [--round3 <dir>]]
"""
import collections
import csv
import json
import sys
from pathlib import Path

ARGS = sys.argv[1:]
R2 = R3 = None
if '--round2' in ARGS:
    _i = ARGS.index('--round2')
    R2 = Path(ARGS[_i + 1])
    del ARGS[_i:_i + 2]
if '--round3' in ARGS:
    _i = ARGS.index('--round3')
    R3 = Path(ARGS[_i + 1])
    del ARGS[_i:_i + 2]
    assert R2, 'STOP: --round3 needs --round2'
V, DIS, DEC, KEY, OUT = (Path(a) for a in ARGS)
S = V / 'data/search/screening_full_2026-11-11'
sys.path.insert(0, str(V / 'scripts'))
from rulings import decide  # noqa: E402

csv.field_size_limit(10**9)
LISTS = {'resampler', 'learner', 'measures'}


def rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


def norm(field, v):
    v = (v or '').strip()
    if field in LISTS:
        return ';'.join(sorted(x.strip() for x in v.replace(',', ';').split(';') if x.strip()))
    return v


def compile_round(dis, dec_dir, key_path, out):
    """The log of one round's items, written with its decisions file into `out`."""
    key = json.load(open(key_path))['first_is']
    dec = {}
    for f in sorted(dec_dir.glob('adj*_decisions.csv')):
        for r in rows(f):
            assert r['item'] not in dec, ('STOP: decided twice', r['item'])
            dec[r['item']] = r
    log, missing = [], []
    for d in rows(dis):
        item = f'{d["project"]}:{d["rec"]}:{d["field"]}'
        if item not in dec:
            missing.append(item); continue
        r = dec[item]
        if r['decision'] == 'other':
            chosen, value = 'other', r['value']
        else:
            chosen = 'first' if r['decision'] == key[item] else 'second'
            value = d['first'] if chosen == 'first' else d['second']
        log.append(dict(item=item, project=d['project'], rec=d['rec'], field=d['field'], source=d['source'],
                        first=d['first'], second=d['second'], adjudicated=value, chosen=chosen,
                        how='kept' if chosen == 'first' or value.strip() == d['first'].strip() else 'corrected',
                        reason=r['reason'], confidence=r['confidence']))
    if missing:
        raise SystemExit(f'STOP: {len(missing)} items not adjudicated, e.g. {missing[:5]}')
    out.mkdir(parents=True, exist_ok=True)
    with open(out / 'adjudication_log.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, list(log[0]))
        w.writeheader()
        w.writerows(log)
    # v0.25: the same items without the reasons (which may quote a paper), for the deposit
    with open(out / 'adjudication_decisions.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, [k for k in log[0] if k != 'reason'])
        w.writeheader()
        w.writerows({k: v for k, v in x.items() if k != 'reason'} for x in log)
    return log


def summarize(log, proj, n_overrides):
    lp = [x for x in log if x['project'] == proj]
    return dict(items=len(lp), kept=sum(x['how'] == 'kept' for x in lp),
                corrected=sum(x['how'] == 'corrected' for x in lp),
                chosen=dict(collections.Counter(x['chosen'] for x in lp)),
                records_corrected=len({x['rec'] for x in lp if x['how'] == 'corrected'}),
                by_field={f: dict(collections.Counter(x['how'] for x in lp if x['field'] == f))
                          for f in sorted({x['field'] for x in lp})},
                low_confidence=sum(x['confidence'] == 'low' for x in lp),
                spot_check_overrides=n_overrides)


first_codes = {p: {r['rec']: r for r in rows(S / f'{p}/coded.csv')} for p in ('useaudit', 'coverage')}
log1 = compile_round(DIS, DEC, KEY, OUT)
# v0.25: the team lead's spot check (page "SMOTE25 Samples Check", scripts/merge_d42_check.py): a checked change in
# <out>/spot_check_overrides.csv (project, rec, field, value, note) takes precedence over the adjudication
OVR = OUT / 'spot_check_overrides.csv'
overrides1 = rows(OVR) if OVR.exists() else []
log2, overrides2, again = [], [], set()
if R2:
    log2 = compile_round(R2 / 'disagreements.csv', R2 / 'adjudication_raw', R2 / 'adjudication_key.json', R2)
    again = {(p, r['rec']) for p in ('useaudit', 'coverage') for r in rows(R2 / f'second_codes_{p}.csv')}
    OVR2 = R2 / 'spot_check_overrides.csv'
    overrides2 = rows(OVR2) if OVR2.exists() else []
    # the first codes that round 1 compared must be unchanged for the records that kept their round-1 codes
    current = {p: dict(c) for p, c in first_codes.items()}
    for f in rows(S / 'coverage/rulings_fulltext_facts.csv'):
        k = f['rec']
        if k in current['coverage'] and current['coverage'][k]['eligible'] == 'yes' and decide(f)[1] == 'exclude':
            current['coverage'][k] = dict(current['coverage'][k], eligible='no', exclusion='E1')
    changed = [x['item'] for x in log1 if (x['project'], x['rec']) not in again
               and norm(x['field'], current[x['project']][x['rec']].get(x['field'], '')) != norm(x['field'], x['first'])]
    assert not changed, ('STOP: a first code of round 1 changed without a round-2 coding', changed[:5])
log3, overrides3 = [], []
if R3:
    log3 = compile_round(R3 / 'disagreements.csv', R3 / 'adjudication_raw', R3 / 'adjudication_key.json', R3)
    _new = {(x['project'], x['rec']) for x in log3}
    _old = {(x['project'], x['rec']) for x in log1 + log2}
    assert not (_new & _old), ('STOP: a record of round 3 was adjudicated in an earlier round', sorted(_new & _old)[:5])
    OVR3 = R3 / 'spot_check_overrides.csv'
    overrides3 = rows(OVR3) if OVR3.exists() else []
in_force = [x for x in log1 if (x['project'], x['rec']) not in again] + log2 + log3
fix = collections.defaultdict(dict)
for x in in_force:
    if x['how'] == 'corrected':
        fix[(x['project'], x['rec'])][x['field']] = x['adjudicated']
for o in [o for o in overrides1 if (o['project'], o['rec']) not in again] + overrides2 + overrides3:
    assert o['rec'] in first_codes[o['project']], ('STOP: override for a record not coded', o)
    if o['value'].strip() == first_codes[o['project']][o['rec']].get(o['field'], '').strip():
        fix[(o['project'], o['rec'])].pop(o['field'], None)
    else:
        fix[(o['project'], o['rec'])][o['field']] = o['value']
summary = {}
for proj in ('useaudit', 'coverage'):
    first = rows(S / f'{proj}/coded.csv')
    out_rows = [dict(r, **fix.get((proj, r['rec']), {})) for r in first]
    with open(OUT / f'{proj}_coded_adjudicated.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, list(first[0]))
        w.writeheader()
        w.writerows(out_rows)
    summary[proj] = summarize(log1, proj, sum(o['project'] == proj for o in overrides1))
(OUT / 'adjudication_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
print(json.dumps({p: {k: v for k, v in s.items() if k != 'by_field'} for p, s in summary.items()}))
if R2:
    s2 = {p: summarize(log2, p, sum(o['project'] == p for o in overrides2)) for p in ('useaudit', 'coverage')}
    s2['in_force'] = {}
    ov_in_force = [o for o in overrides1 if (o['project'], o['rec']) not in again] + overrides2
    for p in ('useaudit', 'coverage'):
        gone = [x for x in log1 if x['project'] == p and (p, x['rec']) in again]
        s2['in_force'][p] = dict(summarize([x for x in in_force if x not in log3], p,
                                           sum(o['project'] == p for o in ov_in_force)),
                                 round1_items_replaced=len(gone),
                                 round1_records_replaced=len({x['rec'] for x in gone}),
                                 round1_corrections_replaced=sum(x['how'] == 'corrected' for x in gone))
    (R2 / 'adjudication_summary.json').write_text(json.dumps(s2, indent=1), encoding='utf-8')
    print('round 2:', json.dumps({p: {k: v for k, v in s.items() if k != 'by_field'} for p, s in s2.items()
                                  if p != 'in_force'}))
    print('in force:', json.dumps({p: {k: v for k, v in s.items() if k != 'by_field'} for p, s in s2['in_force'].items()}))
if R3:
    # v0.38: the items that the codes of the samples as they now stand rest on (D28: papers that left the coverage
    # sample keep their codes but no longer count)
    sample = {p: {r['rec'] for r in rows(S / f'samples/{p}_sample.csv')} for p in ('useaudit', 'coverage')}
    ov_in_force = [o for o in overrides1 if (o['project'], o['rec']) not in again] + overrides2 + overrides3
    s3 = {p: summarize(log3, p, sum(o['project'] == p for o in overrides3)) for p in ('useaudit', 'coverage')}
    s3['in_force'] = {}
    for p in ('useaudit', 'coverage'):
        inside = [x for x in in_force if x['project'] == p and x['rec'] in sample[p]]
        outside = [x for x in in_force if x['project'] == p and x['rec'] not in sample[p]]
        gone = [x for x in log1 if x['project'] == p and (p, x['rec']) in again]
        s3['in_force'][p] = dict(summarize(inside, p, sum(o['project'] == p and o['rec'] in sample[p]
                                                          for o in ov_in_force)),
                                 from_round={str(rd): sum(1 for x in inside if x in lg)
                                             for rd, lg in ((1, log1), (2, log2), (3, log3))},
                                 round1_items_replaced=len(gone),
                                 round1_records_replaced=len({x['rec'] for x in gone}),
                                 left_sample_items=len(outside),
                                 left_sample_records=sorted({x['rec'] for x in outside}))
    (R3 / 'adjudication_summary.json').write_text(json.dumps(s3, indent=1), encoding='utf-8')
    print('round 3:', json.dumps({p: {k: v for k, v in s.items() if k != 'by_field'} for p, s in s3.items()
                                  if p != 'in_force'}))
    print('in force (samples as they stand):', json.dumps({p: {k: v for k, v in s.items() if k != 'by_field'}
                                                           for p, s in s3['in_force'].items()}))
