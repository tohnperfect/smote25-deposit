#!/usr/bin/env python3
"""D42: compare the blind AI second coding of both samples with the first coding, field by field.

First codes: `useaudit/coded.csv` and `coverage/coded.csv` of the screening folder; for the coverage sample the rulings
B and B2 at full text are applied to the first codes as `analyze_samples.py` applies them (a paper coded eligible whose
facts in `coverage/rulings_fulltext_facts.csv` fail a ruling is not eligible, E1). Second codes: the batches of the
blind second coders in <d42 dir>/<project>/out/, in two rounds (v0.37). Round 1 (14 Nov 2026): batches 201 to 209 (use
audit) and 201 to 202 (coverage), every record coded until then. Round 2 (16 Nov 2026): batches 211 and above, the
records whose full texts came through the library, that is the use-audit records recoded from their full texts (a first
and a blind second coding that replace both codes of round 1 for these records) and the coverage papers coded for the
first time. A record may be second-coded in both rounds only in the use audit. A coverage paper whose file turned out
to be another paper (`coverage/fetch_log.csv`: not usable; both coders coded fulltext_ok = no) is not compared, and
is listed under `not_the_paper`.
Agreement per field: share of records with the same value (lists compared as sets) and Cohen's kappa for single-value
fields. Fields compared: every coded field but `task`, `evidence`, `note` and `confidence` (free text or the coder's
own confidence). Writes into <out_dir>: second_codes_<project>.csv (the second codes of the round, as coded),
agreement.json, disagreements.csv (one row per record and field that differ, with both values and the source). With
`--round 2`, agreement.json also holds `all`: the agreement of the codes as they stand, each record with the two codes
of its last round. Round 1's files (d42/) were made from the first codes before the library round (coded.csv of
v0.36); `--round 1` reproduces them from those first codes only. The second codes' `evidence` and `note` columns are
short quotes and notes from the papers: team use only, never deposited.
Third round (v0.38): batches 231 and above, the coverage papers that joined the sample at the final merge (D28) and
whose full texts came through the library. With `--round 3`, `all` covers only the records of the samples as they
now stand (`samples/coverage_sample.csv`, `samples/useaudit_sample.csv`): a paper that left the coverage sample at the
final merge keeps its codes but no longer counts; `left_sample` lists such papers.
Usage: python3 -I scripts/d42_compare.py <draft_dir> <d42 dir> <out_dir> [--round 2|3]
"""
import collections
import csv
import json
import sys
from pathlib import Path

ARGS = sys.argv[1:]
ROUND = 1
if '--round' in ARGS:
    _i = ARGS.index('--round')
    ROUND = int(ARGS[_i + 1])
    del ARGS[_i:_i + 2]
assert ROUND in (1, 2, 3), 'STOP: --round is 1, 2 or 3'
V, D, OUT = (Path(a) for a in ARGS)
S = V / 'data/search/screening_full_2026-11-11'
sys.path.insert(0, str(V / 'scripts'))
from rulings import decide  # noqa: E402

csv.field_size_limit(10**9)
SKIP = {'rec', 'task', 'evidence', 'note', 'confidence', 'batch'}
LISTS = {'resampler', 'learner', 'measures'}
ROUND2_FROM = 211   # the first batch number of round 2
ROUND3_FROM = 231   # v0.38: the first batch number of round 3 (the papers that joined at the final merge, D28)


def round_of(batch):
    return 1 if int(batch) < ROUND2_FROM else 2 if int(batch) < ROUND3_FROM else 3


def rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


def norm(field, v):
    v = (v or '').strip()
    if field in LISTS:
        return ';'.join(sorted(x.strip() for x in v.replace(',', ';').split(';') if x.strip()))
    return v


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe >= 1 else round((po - pe) / (1 - pe), 3)


def block(pairs, fld):
    agree = sum(a == b for a, b in pairs)
    return dict(n=len(pairs), agree=agree, pct=round(100 * agree / len(pairs), 1) if pairs else None,
                kappa=None if fld in LISTS else kappa(pairs))


def field_stats(proj, fields, first, second, keys, ft_counted):
    """Agreement per field over `keys`; for the use audit also over the records coded from a full text and over the
    full texts that the paper counts."""
    per = {}
    for fld in fields:
        def pairs(sel):
            return [(norm(fld, first[k].get(fld, '')), norm(fld, second[k].get(fld, ''))) for k in keys if sel(k)]
        per[fld] = block(pairs(lambda k: True), fld)
        if proj == 'useaudit':
            # the records coded from a full text (the fields read in full texts are na otherwise)
            per[fld]['fulltext'] = block(pairs(lambda k: first[k].get('source') == 'fulltext'), fld)
            # v0.25: the full texts that the paper counts (Section 8.3: the targets of the full-text reading whose text
            # was obtained); two more records were coded from a full text when an earlier draw put them among the
            # first 50, and the paper uses their codes at abstract level only
            per[fld]['fulltext_counted'] = block(pairs(lambda k: first[k].get('source') == 'fulltext'
                                                       and k in ft_counted), fld)
    return per


def all_agree(fields, first, second, keys):
    return sum(all(norm(f, first[k].get(f, '')) == norm(f, second[k].get(f, '')) for f in fields) for k in keys)


OUT.mkdir(parents=True, exist_ok=True)
manifest_all = json.load(open(D / 'manifest.json'))
result, disagreements, every = {}, [], {}
for proj in ('useaudit', 'coverage'):
    first = {r['rec']: r for r in rows(S / f'{proj}/coded.csv')}
    if proj == 'coverage':
        for f in rows(S / 'coverage/rulings_fulltext_facts.csv'):
            k = f['rec']
            if k in first and first[k]['eligible'] == 'yes' and decide(f)[1] == 'exclude':
                first[k] = dict(first[k], eligible='no', exclusion='E1', note=f'ruling {decide(f)[2]} (facts recheck)')
    FT_COUNTED, USABLE = set(), None
    if proj == 'coverage':
        USABLE = {r['rec'] for r in rows(S / 'coverage/fetch_log.csv') if r['usable'] == 'yes'}
    if proj == 'useaudit':
        _fl = {r['rec']: r for r in rows(S / 'useaudit/fetch_log.csv')}
        FT_COUNTED = {r['rec'] for r in rows(S / 'samples/useaudit_sample.csv')
                      if r['target'] == 'fulltext' and _fl.get(r['rec'], {}).get('usable') == 'yes'}
    # second codes by round; a record second-coded twice within a round is an error
    by_round, batches_by_round = {1: {}, 2: {}, 3: {}}, {1: [], 2: [], 3: []}
    for b in sorted((D / proj / 'out').glob('batch2*_coded.csv')):
        rd = round_of(b.name[5:8])
        batches_by_round[rd].append(b)
        for r in rows(b):
            assert r['rec'] not in by_round[rd], ('STOP: coded twice in one round', r['rec'])
            by_round[rd][r['rec']] = dict(r, batch=b.name[5:8])
    want_by_round = {1: [], 2: [], 3: []}
    for nnn, recs in manifest_all[proj].items():
        for r in recs:
            if r not in want_by_round[round_of(nnn)]:
                want_by_round[round_of(nnn)].append(r)
    again = set(want_by_round[1]) & set(want_by_round[2])
    assert proj == 'useaudit' or not again, ('STOP: a coverage paper second-coded in both rounds', sorted(again)[:5])
    assert not (set(want_by_round[3]) & (set(want_by_round[1]) | set(want_by_round[2]))), \
        'STOP: a record of round 3 was second-coded in an earlier round'
    second, batches, want = by_round[ROUND], batches_by_round[ROUND], want_by_round[ROUND]
    missing = [r for r in want if r not in second]
    fields = [c for c in next(iter(first.values())).keys() if c not in SKIP]
    with open(OUT / f'second_codes_{proj}.csv', 'w', newline='', encoding='utf-8') as fh:
        cols = ['batch', 'rec'] + [c for c in (list(next(iter(second.values())).keys()) if second else []) if c not in ('batch', 'rec')]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for k in want:
            if k in second:
                w.writerow({c: second[k].get(c, '') for c in cols})
    keys = [k for k in want if k in second and (USABLE is None or k in USABLE)]
    not_paper = [k for k in want if k in second and k not in keys]
    per = field_stats(proj, fields, first, second, keys, FT_COUNTED)
    for fld in fields:
        for k in keys:
            if norm(fld, first[k].get(fld, '')) != norm(fld, second[k].get(fld, '')):
                disagreements.append(dict(project=proj, rec=k, batch=second[k]['batch'], field=fld,
                                          first=first[k].get(fld, ''), second=second[k].get(fld, ''),
                                          source=second[k].get('source', 'fulltext'),
                                          first_confidence=first[k].get('confidence', ''),
                                          second_confidence=second[k].get('confidence', '')))
    result[proj] = dict(records=len(want), coded=len(keys), missing=missing, batches=[b.name for b in batches],
                        records_all_fields_agree=all_agree(fields, first, second, keys), fields=per)
    if not_paper:
        result[proj]['not_the_paper'] = not_paper
    if ROUND == 2:
        # the codes as they stand: each record with the second code of its last round (round 2 replaces round 1)
        last = dict(by_round[1])
        last.update(by_round[2])
        want_all = want_by_round[1] + [r for r in want_by_round[2] if r not in want_by_round[1]]
        keys_all = [k for k in want_all if k in last and (USABLE is None or k in USABLE)]
        every[proj] = dict(records=len(want_all), coded=len(keys_all),
                           from_round={str(rd): sum(1 for k in keys_all if (k in by_round[2]) == (rd == 2))
                                       for rd in (1, 2)},
                           second_coded_again=len(again),
                           records_all_fields_agree=all_agree(fields, first, last, keys_all),
                           fields=field_stats(proj, fields, first, last, keys_all, FT_COUNTED))
    if ROUND == 3:
        # v0.38: the codes as they stand after the final merge: each record of the current sample with the second
        # code of its last round; papers that left the coverage sample under D28 no longer count
        sample = {r['rec'] for r in rows(S / f'samples/{"coverage" if proj == "coverage" else "useaudit"}_sample.csv')}
        last = dict(by_round[1])
        last.update(by_round[2])
        last.update(by_round[3])
        want_all = []
        for rd in (1, 2, 3):
            want_all += [r for r in want_by_round[rd] if r not in want_all]
        left = [k for k in want_all if k not in sample]
        keys_all = [k for k in want_all if k in last and k in sample and (USABLE is None or k in USABLE)]
        every[proj] = dict(records=len(want_all) - len(left), coded=len(keys_all),
                           from_round={str(rd): sum(1 for k in keys_all
                                                    if max(r for r in (1, 2, 3) if k in by_round[r]) == rd)
                                       for rd in (1, 2, 3)},
                           second_coded_again=len(again), left_sample=left,
                           records_all_fields_agree=all_agree(fields, first, last, keys_all),
                           fields=field_stats(proj, fields, first, last, keys_all, FT_COUNTED))
with open(OUT / 'disagreements.csv', 'w', newline='', encoding='utf-8') as fh:
    cols = ['project', 'rec', 'batch', 'field', 'first', 'second', 'source', 'first_confidence', 'second_confidence']
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(disagreements)
result['disagreements'] = dict(collections.Counter(d['project'] for d in disagreements))
if ROUND in (2, 3):
    result['round'] = ROUND
    result['all'] = every
(OUT / 'agreement.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
for proj in ('useaudit', 'coverage'):
    for label, r in ((f'round {ROUND}', result[proj]),) + ((('as they stand', every[proj]),) if ROUND in (2, 3) else ()):
        print(proj, label, f"coded {r['coded']}/{r['records']}, all fields agree on {r['records_all_fields_agree']} records")
        for f, v in r['fields'].items():
            ft = v.get('fulltext')
            print(f'  {f:15s} {v["agree"]:4d}/{v["n"]:<4d} {v["pct"]}%  kappa {v["kappa"]}'
                  + (f'   full texts {ft["agree"]}/{ft["n"]} {ft["pct"]}% kappa {ft["kappa"]}' if ft else ''))
print('disagreements:', result['disagreements'])
