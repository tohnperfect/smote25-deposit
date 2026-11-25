#!/usr/bin/env python3
"""Summarize the coverage sample (WP4) and the use audit (WP5) from the AI sessions' codes.

Inputs under data/search/screening_full_2026-11-11/: decisions/screen_decisions.csv (frames), samples/*.csv (drawn
records), coverage/coded.csv and useaudit/coded.csv (codes), coverage/fetch_log.csv and useaudit/fetch_log.csv.
Shares are given per stratum and pooled; with a Wilson 95% interval for pooled counts and, where the strata were
sampled at different rates, a stratum-weighted estimate (weights = frame sizes) with a normal-approximation interval.
Usage: python3 -I scripts/analyze_samples.py DRAFT_DIR
Writes data/search/screening_full_2026-11-11/samples/samples_summary.json.
"""
import collections
import csv
import json
import math
import sys
from pathlib import Path

csv.field_size_limit(10**9)
D = Path(sys.argv[1]) / 'data/search/screening_full_2026-11-11'


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def share(k, n):
    return {'k': k, 'n': n, 'pct': round(100 * k / n, 1) if n else None, 'ci95': wilson(k, n)}


def weighted(by_stratum, weights):
    """by_stratum: {s: (k, n)}; weights: {s: N_s}. Stratum-weighted share and normal-approximation 95% interval."""
    tot = sum(weights[s] for s, (k, n) in by_stratum.items() if n)
    if not tot:
        return None
    est, var = 0.0, 0.0
    for s, (k, n) in by_stratum.items():
        if not n:
            continue
        w, p = weights[s] / tot, k / n
        est += w * p
        var += w * w * p * (1 - p) / n
    se = math.sqrt(var)
    return {'pct': round(100 * est, 1), 'ci95': [round(100 * max(0, est - 1.96 * se), 1), round(100 * min(1, est + 1.96 * se), 1)]}


def rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8'))) if p.exists() else []


dec = rows(D / 'decisions/screen_decisions.csv')
out = {}

# ---------- coverage sample ----------
cs = rows(D / 'samples/coverage_sample.csv')
# v0.25 (D42): where the blind AI second coding has been adjudicated, the adjudicated codes replace the first codes
# (d42/<project>_coded_adjudicated.csv, written by scripts/d42_compile.py; same columns as coded.csv).
CODED = {p: (D / 'd42' / f'{p}_coded_adjudicated.csv') if (D / 'd42' / f'{p}_coded_adjudicated.csv').exists()
         else (D / p / 'coded.csv') for p in ('coverage', 'useaudit')}
cc = {r['rec']: r for r in rows(CODED['coverage'])}
cf = {r['rec']: r for r in rows(D / 'coverage/fetch_log.csv')}
# v0.12: rulings B and B2 at the full-text stage (coverage codebook v1.2, Section 5). A separate session recorded the
# facts of the rulings from the full text of every paper coded eligible under v1.1 (coverage/rulings_fulltext_facts.csv);
# a paper whose method fails B or B2 by those facts is not eligible (E1), whatever its confidence, as the full text is
# the last stage. The coders' codes in coded.csv are left as they are.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rulings import decide  # noqa: E402
rf = {r['rec']: r for r in rows(D / 'coverage/rulings_fulltext_facts.csv')}
ruled = {}
for k, f in rf.items():
    if k in cc and cc[k]['eligible'] == 'yes' and decide(f)[1] == 'exclude':
        ruled[k] = decide(f)[2]
        cc[k] = dict(cc[k], eligible='no', exclusion=f'E1 (ruling {ruled[k]})')
frame = collections.Counter(r['period'] for r in dec if r['decision'] in ('include', 'unsure'))
strata = ['P1', 'P2', 'P3', 'P4']
cov = {'frame': dict(frame), 'strata': {}}
elig_all, cp_all = [], []
for s in strata:
    drawn = [r for r in cs if r['stratum'] == s]
    got = [r for r in drawn if cf.get(r['rec'], {}).get('usable') == 'yes']
    coded = [cc[r['rec']] for r in got if r['rec'] in cc]
    ok = [c for c in coded if c['fulltext_ok'] == 'yes']
    el = [c for c in ok if c['eligible'] == 'yes']
    cp = [c for c in el if c['label'] in ('Core', 'Partial')]
    elig_all += [(s, c) for c in el]
    cp_all += [(s, c) for c in cp]
    cov['strata'][s] = {'drawn': len(drawn), 'retrieved': len(got), 'coded': len(coded), 'assessed': len(ok),
                        'eligible': len(el), 'excluded': dict(collections.Counter(c['exclusion'] for c in ok if c['eligible'] == 'no')),
                        'label': dict(collections.Counter(c['label'] for c in el)),
                        'class': dict(collections.Counter(c['class'] for c in el))}
E = [c for s, c in elig_all]
CP = [c for s, c in cp_all]
cov['pooled'] = {
    'drawn': len(cs), 'retrieved': sum(v['retrieved'] for v in cov['strata'].values()),
    'assessed': sum(v['assessed'] for v in cov['strata'].values()), 'eligible': len(E),
    'excluded': dict(sum((collections.Counter(v['excluded']) for v in cov['strata'].values()), collections.Counter())),
    'label': {k: share(sum(c['label'] == k for c in E), len(E)) for k in ('Core', 'Partial', 'Not counted')},
    'generator': {k: share(sum(c['generator'] == k for c in E), len(E)) for k in ('interpolation', 'deep-generative', 'distribution', 'perturbation', 'other')},
    'decisions': {k: share(sum(c[k] == 'yes' for c in CP), len(CP)) for k in 'SANPFL'},
    'n_decisions': dict(sorted(collections.Counter(sum(c[k] == 'yes' for k in 'SANPFL') for c in CP).items())),
    'mean_decisions': round(sum(sum(c[k] == 'yes' for k in 'SANPFL') for c in CP) / len(CP), 2) if CP else None,
    'class': {k: share(sum(c['class'] == k for c in E), len(E)) for k in ('B', 'M', 'B+M')},
    'modality': dict(collections.Counter(c['modality'] for c in E)),
    'vs_smote_plain': share(sum(c['vs_smote'] == 'plain' for c in E), len(E)),
    'vs_smote_any': share(sum(c['vs_smote'] in ('plain', 'wrapper') for c in E), len(E)),
    'vs_none': share(sum(c['vs_none'] == 'yes' for c in E), len(E)),
    'vs_cost': share(sum(c['vs_cost'] == 'yes' for c in E), len(E)),
    'measures': {m: share(sum(m in c['measures'].split(';') for c in E), len(E)) for m in
                 ('accuracy', 'G-mean', 'F-measure', 'ROC-AUC', 'PR-AUC', 'MCC', 'Brier', 'calibration')},
    'protocol': dict(collections.Counter(c['protocol'] for c in E)),
    'repeated': share(sum(c['protocol'] in ('repeated-cv', 'repeated-holdout') for c in E), len(E)),
    'inside_folds': dict(collections.Counter(c['inside_folds'] for c in E)),
    'inside_stated': share(sum(c['inside_folds'] == 'stated' for c in E), len(E)),
    'tuning': dict(collections.Counter(c['tuning'] for c in E)),
    'tuning_test': share(sum(c['tuning'] == 'test' for c in E), len(E)),
    'stat_test': share(sum(c['stat_test'] == 'yes' for c in E), len(E)),
    'code': share(sum(c['code'] == 'yes' for c in E), len(E)),
    'datasets_median': (sorted(int(c['n_datasets']) for c in E if c['n_datasets'].isdigit())[len([c for c in E if c['n_datasets'].isdigit()]) // 2]
                        if any(c['n_datasets'].isdigit() for c in E) else None),
}
cov['weighted'] = {k: weighted({s: (sum(1 for t, c in elig_all if t == s and f(c)), sum(1 for t, c in elig_all if t == s)) for s in strata}, frame)
                   for k, f in {'core_or_partial': lambda c: c['label'] in ('Core', 'Partial'),
                                'not_counted': lambda c: c['label'] == 'Not counted',
                                'deep_generative': lambda c: c['generator'] == 'deep-generative',
                                'binary_only': lambda c: c['class'] == 'B',
                                'vs_none': lambda c: c['vs_none'] == 'yes',
                                'inside_stated': lambda c: c['inside_folds'] == 'stated'}.items()}
cov['rulings_fulltext'] = {'rechecked': len(rf), 'rechecked_in_sample': sum(1 for r in cs if r['rec'] in rf),
                           # v0.38: the papers of the sample as it now stands (D28 may move a ruled paper out)
                           'not_eligible': dict(sorted((k, v) for k, v in ruled.items() if k in {r['rec'] for r in cs})),
                           'facts_scheme': dict(collections.Counter(f['scheme'] for f in rf.values()))}
out['coverage'] = cov

# ---------- use audit ----------
us = rows(D / 'samples/useaudit_sample.csv')
uc = {r['rec']: r for r in rows(CODED['useaudit'])}
uf = {r['rec']: r for r in rows(D / 'useaudit/fetch_log.csv')}
uframe = collections.Counter(('U1' if (int(r['year']) if r['year'].isdigit() else 0) <= 2020 else 'U2' if int(r['year']) <= 2023 else 'U3')
                             for r in dec if r['decision'] == 'exclude' and r['code'] == 'E1')
ustr = ['U1', 'U2', 'U3']
use = {'frame': dict(uframe), 'strata': {}}
A_all, F_all = [], []
for s in ustr:
    drawn = [r for r in us if r['stratum'] == s]
    coded = [uc[r['rec']] for r in drawn if r['rec'] in uc]
    app = [c for c in coded if c['is_application'] == 'yes']
    ft_target = {r['rec'] for r in drawn if r['target'] == 'fulltext'}
    ft = [c for c in app if c['source'] == 'fulltext' and c['rec'] in ft_target]
    A_all += [(s, c) for c in app]
    F_all += [(s, c) for c in ft]
    use['strata'][s] = {'drawn': len(drawn), 'coded': len(coded), 'application': len(app), 'fulltext_target': len(ft_target),
                        'fulltext_coded': len(ft),
                        'not_application': dict(collections.Counter((c['note'] or '')[:40] for c in coded if c['is_application'] == 'no')),
                        'domain': dict(collections.Counter(c['domain'] for c in app)),
                        'inside_folds': dict(collections.Counter(c['inside_folds'] for c in ft))}
A = [c for s, c in A_all]
F = [c for s, c in F_all]
# v0.12: records that the first coding took to propose a resampling method of their own, coded again under the rulings
# of the screen (use-audit codebook v1.1); useaudit/rulings_recode.csv lists them with both codes of is_application
rr = rows(D / 'useaudit/rulings_recode.csv')
use['rulings_recode'] = {'recoded': len(rr), 'in_sample': sum(1 for r in rr if r['rec'] in {x['rec'] for x in us}),
                         'now_application': sum(1 for r in rr if uc.get(r['rec'], {}).get('is_application') == 'yes'),
                         'records': {r['rec']: f"{r['is_application_before']} -> {uc.get(r['rec'], {}).get('is_application', '?')}" for r in rr}}
use['pooled'] = {
    'coded': sum(v['coded'] for v in use['strata'].values()), 'application': len(A), 'fulltext': len(F),
    # v0.12: full texts obtained for the targets, applications or not (fulltext counts the applications among them)
    'fulltext_obtained': sum(1 for r in us if r['target'] == 'fulltext' and uf.get(r['rec'], {}).get('usable') == 'yes'),
    'domain': {k: share(sum(c['domain'] == k for c in A), len(A)) for k in sorted({c['domain'] for c in A})},
    'stakes_individual': share(sum(c['stakes'] == 'individual' for c in A), len(A)),
    'modality': dict(collections.Counter(c['modality'] for c in A)),
    'smote_named': share(sum('SMOTE' in c['resampler'].split(';') for c in A), len(A)),
    'resampler': dict(collections.Counter(x for c in A for x in c['resampler'].split(';'))),
    'deep_net': share(sum('deep-net' in c['learner'].split(';') for c in A), len(A)),
    'validation_abstract_level': dict(collections.Counter(c['validation'] for c in A)),
    'ft_inside_folds': {k: share(sum(c['inside_folds'] == k for c in F), len(F)) for k in ('stated', 'before-split', 'nr')},
    'ft_vs_none': share(sum(c['vs_none'] == 'yes' for c in F), len(F)),
    'ft_vs_weights': share(sum(c['vs_weights'] == 'yes' for c in F), len(F)),
    'ft_calibration': share(sum(c['calibration'] == 'yes' for c in F), len(F)),
    'ft_test_balanced': {k: share(sum(c['test_balanced'] == k for c in F), len(F)) for k in ('yes', 'no', 'nr')},
    'ft_validation': {k: share(sum(c['validation'] == k for c in F), len(F)) for k in ('internal', 'external', 'prospective', 'deployed', 'nr')},
    'ft_accuracy': share(sum('accuracy' in c['measures'].split(';') for c in F), len(F)),
    'ft_roc_auc': share(sum('ROC-AUC' in c['measures'].split(';') for c in F), len(F)),
    'ft_pr_auc': share(sum('PR-AUC' in c['measures'].split(';') for c in F), len(F)),
}
use['weighted'] = {k: weighted({s: (sum(1 for t, c in src if t == s and f(c)), sum(1 for t, c in src if t == s)) for s in ustr}, uframe)
                   for k, (src, f) in {'medicine': (A_all, lambda c: c['domain'] == 'medicine'),
                                       'stakes_individual': (A_all, lambda c: c['stakes'] == 'individual'),
                                       'inside_stated': (F_all, lambda c: c['inside_folds'] == 'stated'),
                                       'before_split': (F_all, lambda c: c['inside_folds'] == 'before-split'),
                                       'vs_none': (F_all, lambda c: c['vs_none'] == 'yes'),
                                       'calibration': (F_all, lambda c: c['calibration'] == 'yes'),
                                       'external_or_beyond': (F_all, lambda c: c['validation'] in ('external', 'prospective', 'deployed'))}.items()}
out['useaudit'] = use
out['codes_used'] = {p: str(CODED[p].relative_to(D)) for p in CODED}   # v0.25 (D42)
(D / 'samples').mkdir(exist_ok=True)
json.dump(out, open(D / 'samples/samples_summary.json', 'w', encoding='utf-8'), indent=1)
print(json.dumps({'coverage': cov['pooled'] | {'strata': cov['strata']}, 'useaudit': {k: use['pooled'][k] for k in ('coded', 'application', 'fulltext')}}, indent=1)[:3000])
