#!/usr/bin/env python3
"""Collect every number the paper prints about the systematic search into one flat file (WP4, WP5).

Sources: data/search/2026-11-11/wp4_records_merged_summary.json (identification),
data/search/screening_full_2026-11-11/decisions/screen_decisions_summary.json (screen),
data/search/screening_full_2026-11-11/samples/samples_summary.json (coverage sample and use audit),
data/search/screening_full_2026-11-11/final/screen_final_summary.json and result/screen_summary.json (agreement).
Writes data/search/screening_full_2026-11-11/decisions/search_numbers.json: key -> value as printed (with a
thousands separator). scripts/render_search_text.py writes the paragraphs from it and registers each number for the ledger, so a correction
of the team that changes a count shows up as a mismatch.
Usage: python3 -I scripts/search_numbers.py DRAFT_DIR
"""
import json
import sys
from pathlib import Path

R = Path(sys.argv[1])
S = R / 'data/search/screening_full_2026-11-11'
ident = json.load(open(R / 'data/search/2026-11-11/wp4_records_merged_summary.json'))
dec = json.load(open(S / 'decisions/screen_decisions_summary.json'))
fin = json.load(open(S / 'final/screen_final_summary.json'))
first = json.load(open(S / 'result/screen_summary.json'))
smp = json.load(open(S / 'samples/samples_summary.json')) if (S / 'samples/samples_summary.json').exists() else {}


def f(x):
    if isinstance(x, float):
        return f'{x:.1f}'
    return f'{x:,}' if isinstance(x, int) else str(x)


N = {}
N['id_scopus'] = ident['records_by_source']['scopus']
N['id_openalex'] = ident['records_by_source']['openalex']
N['id_arxiv'] = ident['records_by_source']['arxiv']
N['id_total'] = ident['records_total']
N['id_duplicates'] = ident['duplicates_removed']
N['screened'] = ident['unique_after_dedup']
N['no_abstract'] = ident['unique_without_abstract']
d = dec['decision']
N['included'] = d.get('include', 0)
N['unsure_to_fulltext'] = d.get('unsure', 0)
N['passed'] = N['included'] + N['unsure_to_fulltext']
N['excluded'] = d.get('exclude', 0)
for code, v in dec['codes'].get('exclude', {}).items():
    N['excluded_' + code] = v
for code, v in dec['codes'].get('include', {}).items():
    N['included_' + code] = v
for code, v in dec['codes'].get('unsure', {}).items():
    N['unsure_' + code] = v
for p, v in dec['by_period'].get('include', {}).items():
    N['included_' + p] = v
gen = dec['include_kind_by_period'].get('I1-generative', {})
for p, v in gen.items():
    N['generative_' + p] = v
N['generative_total'] = sum(gen.values())
by = dec['decided_by']
N['decided_first_high'] = by.get('first pass, high confidence', 0)
N['decided_agree'] = by.get('first pass and second look agree', 0)
N['decided_third'] = dec['adjudication']['n']   # records the third look settled (a later rule or correction may replace its decision)
N['decided_third_final'] = by.get('third look (adjudication)', 0)
N['decided_team'] = by.get('team correction', 0)
wdr = dec.get('withdrawn', {})
N['excluded_withdrawn'] = dec['codes'].get('exclude', {}).get('E-WITHDRAWN', 0)
N['withdrawn_were_include'] = wdr.get('looks_decision', {}).get('include', 0)
N['withdrawn_were_unsure'] = wdr.get('looks_decision', {}).get('unsure', 0)
N['withdrawn_were_exclude'] = wdr.get('looks_decision', {}).get('exclude', 0)
_zs = R / 'data/search/zenodo_status_2026-11-11.csv'
if _zs.exists():
    import csv as _csv
    _z = list(_csv.DictReader(open(_zs, encoding='utf-8')))
    N['zenodo_checked'] = len(_z)
    N['withdrawn_spam'] = sum(1 for r in _z if r['http'] == '410' and r['removal_reason'] == 'spam')
    N['withdrawn_spam_7sep'] = sum(1 for r in _z if r['http'] == '410' and r['removal_reason'] == 'spam' and r['removal_date'].startswith('2026-09-07'))
# v0.12: the independent AI check (another model) and the pass that applies rulings B and B2 to the whole screen
_ac = dec.get('ai_check', {})
_lt = _ac.get('looks_to_check_not_withdrawn', {})
N['check_unsure_n'] = sum(v for k, v in _lt.items() if k.startswith('unsure->'))
N['check_unsure_include'] = _lt.get('unsure->include', 0)
N['check_unsure_exclude'] = _lt.get('unsure->exclude', 0)
N['check_unsure_unsure'] = _lt.get('unsure->unsure', 0)
N['check_include_to_exclude'] = _lt.get('include->exclude', 0)
N['check_exclude_to_include'] = _lt.get('exclude->include', 0)
N['decided_check'] = by.get('independent AI check', 0)
# v0.13: the check merged; all records of its lists, the removed deposits included, and its blind decisions and code checks
_la = _ac.get('looks_to_check', {})
N['check_unsure_all'] = sum(v for k, v in _la.items() if k.startswith('unsure->'))
N['check_unsure_include_all'] = _la.get('unsure->include', 0)
N['check_unsure_exclude_all'] = _la.get('unsure->exclude', 0)
N['check_unsure_unsure_all'] = _la.get('unsure->unsure', 0)
N['check_sample_corrections'] = _la.get('include->exclude', 0) + _la.get('exclude->include', 0)
_ret = S / 'check/returns'
_blind = _ret / 'method/blind_check_raw_2_includes_3_exclusions.csv'
if _blind.exists():
    import csv as _csv2
    _b = list(_csv2.DictReader(open(_blind, encoding='utf-8-sig')))
    _d = [x for x in _b if x['blind_decision'] in ('include', 'exclude')]
    _ag = sum(1 for x in _d if x['blind_decision'] == x['ai_decision'])
    _pa = sum(1 for x in _d if x['ai_decision'] == 'include') / len(_d)
    _pb = sum(1 for x in _d if x['blind_decision'] == 'include') / len(_d)
    _pe = _pa * _pb + (1 - _pa) * (1 - _pb)
    N['check_blind_n'] = len(_b)
    N['check_blind_inc_n'] = sum(1 for x in _b if x['list'] == '2_includes')
    N['check_blind_exc_n'] = sum(1 for x in _b if x['list'] == '3_exclusions')
    N['check_blind_decided'] = len(_d)
    N['check_blind_undecided'] = len(_b) - len(_d)
    N['check_blind_agree'] = _ag
    N['check_blind_pct'] = round(100 * _ag / len(_d), 1)
    N['check_blind_kappa'] = f"{(_ag / len(_d) - _pe) / (1 - _pe):.2f}"
_cc = sorted(_ret.glob('RETURN_code_checks_*_v3.csv')) if _ret.exists() else []
if _cc:
    import csv as _csv3
    _c = list(_csv3.DictReader(open(_cc[0], encoding='utf-8-sig')))
    N['check_codes_rows'] = len(_c)
    N['check_codes_cov_rows'] = sum(1 for x in _c if x['list'].startswith('4'))
    N['check_codes_use_rows'] = sum(1 for x in _c if x['list'].startswith('5'))
    N['check_codes_corrected'] = sum(1 for x in _c if x['person_agrees'].strip().lower() == 'no')
_rb = dec.get('rule_b', {})
N['ruleb_read'] = _rb.get('read', 0)
N['ruleb_applied'] = _rb.get('applied_to', 0)
N['ruleb_excluded_B'] = _rb.get('excluded', {}).get('B', 0)
N['ruleb_excluded_B2'] = _rb.get('excluded', {}).get('B2', 0)
N['ruleb_excluded'] = N['ruleb_excluded_B'] + N['ruleb_excluded_B2']
N['excluded_other'] = dec['codes'].get('exclude', {}).get('E-OTHER', 0)
_rbs = S / 'rule_b/rule_b_summary.json'
if _rbs.exists():
    _r = json.load(open(_rbs, encoding='utf-8'))
    N['ruleb_unclear'] = _r['scheme'].get('unclear', 0)
    N['ruleb_existing'] = _r['scheme'].get('existing-parts', 0)
    for _k in ('both_read', 'agree_decision', 'sample_includes_both', 'sample_agree', 'sample_check_excluded',
               'sample_pass_excluded', 'sample_both_excluded', 'sample_final_excluded', 'sample_final_both_excluded',
               'sample_final_unsure', 'sample_final_agree'):
        if _k in _r:
            N['ruleb_' + _k] = _r[_k]
    # v0.12: the records that fail ruling B or B2 under the pass's facts, and what became of them (D26: only those
    # recorded with high confidence are excluded; the others go to unsure, U-rule-B)
    N['ruleb_own'] = _r['scheme'].get('own', 0)
    if _r.get('sample_kappa') is not None:
        N['ruleb_sample_kappa'] = f"{_r['sample_kappa']:.2f}"
        N['ruleb_sample_final_kappa'] = f"{_r['sample_final_kappa']:.2f}"
    N['ruleb_failing_B'] = _r['excluded_by_rule'].get('B', 0)
    N['ruleb_failing_B2'] = _r['excluded_by_rule'].get('B2', 0)
    N['ruleb_failing'] = N['ruleb_failing_B'] + N['ruleb_failing_B2']
    N['ruleb_task_other'] = _r['read'] - _r['task'].get('classification', 0)
    _m = json.load(open(S / 'rule_b/rule_b_manifest_PRIVATE.json', encoding='utf-8'))
    N['ruleb_batches'] = len(_m['batches'])
    N['ruleb_batch_max'] = max(len(v) if isinstance(v, list) else len(v.get('recs', v.get('records', []))) for v in _m['batches'].values())
N['ruleb_unsure_B'] = _rb.get('unsure', {}).get('B', 0)
N['ruleb_unsure_B2'] = _rb.get('unsure', {}).get('B2', 0)
N['ruleb_unsure'] = N['ruleb_unsure_B'] + N['ruleb_unsure_B2']
N['unsure_ruleb'] = dec['codes'].get('unsure', {}).get('U-rule-B', 0)   # alias without hyphens for the templates
N['ruleb_failing_applied'] = N['ruleb_excluded'] + N['ruleb_unsure']   # among the includes the check did not read
N['ruleb_failing_applied_B'] = N['ruleb_excluded_B'] + N['ruleb_unsure_B']
N['ruleb_failing_applied_B2'] = N['ruleb_excluded_B2'] + N['ruleb_unsure_B2']

N['third_include'] = dec['adjudication']['decision'].get('include', 0)
N['third_exclude'] = dec['adjudication']['decision'].get('exclude', 0)
N['third_unsure'] = dec['adjudication']['decision'].get('unsure', 0)
N['first_include'] = first['decisions']['include']
N['first_unsure'] = first['decisions']['unsure']
N['first_exclude'] = first['decisions']['exclude']
N['first_E1'] = first['codes']['E1']
pil = first['pilot_random_400']
N['pilot_n'] = pil.get('n', 400)
N['pilot_agreement_pct'] = round(100 * pil['agreement'], 1)
N['pilot_kappa'] = f"{pil['kappa']:.3f}"
N['pilot_differences'] = sum(pil['differences'].values())
kn = first['known_smote_family_35']
N['known_n'] = kn['n']
N['known_include'] = kn['included']
N['known_unsure'] = kn['unsure']
N['known_excluded'] = len(kn['excluded'])
N['second_n'] = fin['second_look']
N['second_agreement_pct'] = round(100 * fin['doubtful_agreement'], 1)
N['second_kappa'] = f"{fin['doubtful_kappa']:.2f}"
N['second_include_high'] = fin['status']['include_single_high']
N['second_to_check'] = fin['to_check']
# bands of Section 7.5 for generative oversamplers among the records that pass the screen
import csv
csv.field_size_limit(10**9)
dec_rows = list(csv.DictReader(open(S / 'decisions/screen_decisions.csv', encoding='utf-8')))
# v0.12: the unsure records by where their decision came from (the three looks, the rulings pass, the check)
# v0.15: from the AI screen's own decision (ai_screen_*), so that the authors' corrections and D28 leave these counts of
# the AI steps as they were; the corrections and D28 have keys of their own (team_*, excluded_unsure_final)
N['unsure_looks'] = sum(1 for r in dec_rows if r['ai_screen_decision'] == 'unsure' and r['ai_screen_by'] in
                        ('first pass, high confidence', 'first pass and second look agree', 'third look (adjudication)'))
N['unsure_check'] = sum(1 for r in dec_rows if r['ai_screen_decision'] == 'unsure' and r['ai_screen_by'] == 'independent AI check')
_ai = dec.get('ai_screen', {}).get('decision', {})
N['ai_included'], N['ai_unsure'], N['ai_excluded'] = _ai.get('include', 0), _ai.get('unsure', 0), _ai.get('exclude', 0)
N['ai_passed'] = N['ai_included'] + N['ai_unsure']
N['final_merge'] = 1 if dec.get('final_merge') else 0
N['excluded_unsure_final'] = dec.get('final_merge_unsure_excluded', 0)
_tc = dec.get('team', {}).get('changes', {})
N['team_records'] = dec.get('team', {}).get('records', 0)
N['team_changed'] = sum(v for k, v in _tc.items() if k.split('->')[0] != k.split('->')[1])
for _a, _b, _k in (('exclude', 'include', 'team_exc_to_inc'), ('include', 'exclude', 'team_inc_to_exc'),
                   ('unsure', 'include', 'team_uns_to_inc'), ('unsure', 'exclude', 'team_uns_to_exc'),
                   ('include', 'unsure', 'team_inc_to_uns'), ('exclude', 'unsure', 'team_exc_to_uns'),
                   ('exclude', 'exclude', 'team_exc_recoded'), ('include', 'include', 'team_inc_recoded')):
    N[_k] = _tc.get(f'{_a}->{_b}', 0)
band = lambda y: '2002_2017' if (int(y) if y.isdigit() else 0) <= 2017 else ('2018_2022' if int(y) <= 2022 else '2023_2026')
for b in ('2002_2017', '2018_2022', '2023_2026'):
    N['generative_' + b] = sum(1 for r in dec_rows if r['decision'] == 'include' and r['code'] == 'I1-generative' and band(r['year']) == b)
    N['passed_' + b] = sum(1 for r in dec_rows if r['decision'] in ('include', 'unsure') and band(r['year']) == b)
DICTS = {}
if smp:
    c, p = smp['coverage'], smp['coverage']['pooled']
    N['cov_per_period'] = smp.get('cov_per_period', 30)
    N['cov_drawn'] = p['drawn']
    N['cov_retrieved'] = p['retrieved']
    N['cov_not_retrieved'] = p['drawn'] - p['retrieved']
    N['cov_assessed'] = p['assessed']
    N['cov_eligible'] = p['eligible']
    _rf = c.get('rulings_fulltext', {})
    N['cov_rulings_rechecked'] = _rf.get('rechecked_in_sample', 0)
    N['cov_rulings_failed'] = len(_rf.get('not_eligible', {}))
    N['cov_excluded'] = p['assessed'] - p['eligible']
    DICTS['cov_excluded_reasons'] = p['excluded']
    for k, lab in (('Core', 'core'), ('Partial', 'partial'), ('Not counted', 'notcounted')):
        N['cov_' + lab] = p['label'][k]['k']
    N['cov_corepartial'] = N['cov_core'] + N['cov_partial']
    for s, v in c['strata'].items():
        N[f'cov_{s}_drawn'], N[f'cov_{s}_retrieved'], N[f'cov_{s}_eligible'] = v['drawn'], v['retrieved'], v['eligible']
    # v0.37 (the library round): Section 4.4 set against Table 8 (the corpus counts and the sample's rows of
    # scripts/gen_coverage_table.py); the wording checks of c_beyond.tex below use the same rows
    sys.path.insert(0, str(R / 'scripts'))
    from gen_coverage_table import CORPUS as _CORPUS, rows_for as _rows_for
    _covrows = {key: d for _, key, d in _rows_for(p) if key}
    N['cov_dec_mean'] = f"{p['mean_decisions']:.1f}"
    N['corpus_dec_mean'] = f"{sum(_CORPUS[k][0] for k in 'SANPFL') / _CORPUS['S'][1]:.1f}"
    N['cov_notcounted_pct'] = round(p['label']['Not counted']['pct'])
    N['corpus_notcounted_pct'] = round(100 * _CORPUS['notcounted'][0] / _CORPUS['notcounted'][1])
    N['cov_notcounted_since2016'] = sum(c['strata'][s]['label'].get('Not counted', 0) for s in ('P3', 'P4'))
    u = smp['useaudit']
    N['use_drawn'] = sum(v['drawn'] for v in u['strata'].values())
    N['use_ft_target'] = sum(v['fulltext_target'] for v in u['strata'].values())
    N['use_ft_coded'] = u['pooled']['fulltext']
    N['use_ft_obtained'] = u['pooled'].get('fulltext_obtained', 0)
    N['use_application'] = u['pooled']['application']
    N['use_coded'] = u['pooled']['coded']
    N['use_rulings_recoded'] = u.get('rulings_recode', {}).get('in_sample', 0)
    N['use_rulings_now_app'] = u.get('rulings_recode', {}).get('now_application', 0)
    for s, v in u['strata'].items():
        N[f'use_{s}_drawn'], N[f'use_{s}_frame'] = v['drawn'], u['frame'].get(s, 0)
# v0.25 (D42): the blind AI second coding of both samples and its AI adjudication (d42/, scripts/d42_compare.py and
# scripts/d42_compile.py). Agreement over the values coded for every record (300 records) and over the safeguards
# read in full texts (the 38 full texts that Section 8.3 counts; fulltext_counted in agreement.json); kappa per
# single-value field.
_D42 = S / 'd42'
if (_D42 / 'agreement.json').exists():
    _ag = json.load(open(_D42 / 'agreement.json', encoding='utf-8'))
    _adj = json.load(open(_D42 / 'adjudication_summary.json', encoding='utf-8')) if (_D42 / 'adjudication_summary.json').exists() else {}
    # v0.37: after the second round (the library full texts, d42/round2/), the agreement of the codes as they stand
    # (`all` of round2/agreement.json: each record with the two codes of its last round) and the adjudications that the
    # codes rest on (`in_force` of round2/adjudication_summary.json: round 1's items of the records coded again are out)
    # v0.38: after the third round (d42/round3/: the coverage papers that joined the sample at the final merge, D28),
    # round3/ holds the same for the samples as they now stand (papers that left the coverage sample no longer count)
    _R2 = _D42 / 'round2'
    _R3 = _D42 / 'round3'
    _r2 = (_R2 / 'agreement.json').exists() and (_R2 / 'adjudication_summary.json').exists()
    _r3 = (_R3 / 'agreement.json').exists() and (_R3 / 'adjudication_summary.json').exists()
    if _r2:
        _ag2 = json.load(open(_R2 / 'agreement.json', encoding='utf-8'))
        _s2 = json.load(open(_R2 / 'adjudication_summary.json', encoding='utf-8'))
        _ag = dict(_ag2['all'], disagreements={p: _s2['in_force'][p]['items'] for p in ('useaudit', 'coverage')})
        _adj = _s2['in_force']
        N['d42_r2_use_n'] = _ag2['useaudit']['coded']
        N['d42_r2_cov_n'] = _ag2['coverage']['coded']
    if _r3:
        _ag3 = json.load(open(_R3 / 'agreement.json', encoding='utf-8'))
        _s3 = json.load(open(_R3 / 'adjudication_summary.json', encoding='utf-8'))
        _ag = dict(_ag3['all'], disagreements={p: _s3['in_force'][p]['items'] for p in ('useaudit', 'coverage')})
        _adj = _s3['in_force']
        N['d42_r3_cov_n'] = _ag3['coverage']['coded']
    _ua = _ag['useaudit']['fields']
    _AB = ['is_application', 'domain', 'stakes', 'modality', 'resampler', 'learner', 'measures', 'validation']
    _FT = ['inside_folds', 'vs_none', 'vs_weights', 'calibration', 'test_balanced']
    N['d42_use_n'] = _ag['useaudit']['coded']
    N['d42_use_ab_pct'] = round(100 * sum(_ua[k]['agree'] for k in _AB) / sum(_ua[k]['n'] for k in _AB), 1)
    _ks = [_ua[k]['kappa'] for k in _AB if _ua[k]['kappa'] is not None]
    N['d42_use_ab_kappa_lo'], N['d42_use_ab_kappa_hi'] = f'{min(_ks):.2f}', f'{max(_ks):.2f}'
    N['d42_use_validation_pct'] = _ua['validation']['pct']
    N['d42_use_ft_n'] = _ua['inside_folds']['fulltext_counted']['n']
    N['d42_use_ft_pct'] = round(100 * sum(_ua[k]['fulltext_counted']['agree'] for k in _FT)
                                / sum(_ua[k]['fulltext_counted']['n'] for k in _FT), 1)
    # wording of e_use.tex: the full texts are those counted as obtained, and kappa is lowest for the kind of validation
    _kmin = min((k for k in _AB if _ua[k]['kappa'] is not None), key=lambda k: _ua[k]['kappa'])
    if _kmin != 'validation' or N['d42_use_ft_n'] != u['pooled'].get('fulltext_obtained'):
        sys.exit(f'WORDING CHECK FAILED (revise e_use.tex): lowest kappa for {_kmin}; full texts compared '
                 f"{N['d42_use_ft_n']}, obtained {u['pooled'].get('fulltext_obtained')}")
    N['d42_use_items'] = _ag['disagreements'].get('useaudit', 0)
    _cv = _ag['coverage']['fields']
    _CF = [k for k in _cv if k != 'fulltext_ok']
    N['d42_cov_n'] = _ag['coverage']['coded']
    N['d42_cov_pct'] = round(100 * sum(_cv[k]['agree'] for k in _CF) / sum(_cv[k]['n'] for k in _CF), 1)
    N['d42_cov_items'] = _ag['disagreements'].get('coverage', 0)
    if _r3 and N['d42_cov_n'] != c.get('pooled', {}).get('retrieved', N['d42_cov_n']):
        sys.exit(f"WORDING CHECK FAILED (revise b_coverage_design.tex): {N['d42_cov_n']} papers coded twice, "
                 f"{c.get('pooled', {}).get('retrieved')} obtained")
    if _adj:
        N['d42_use_corrected'] = _adj['useaudit']['corrected']
        N['d42_use_records_corrected'] = _adj['useaudit']['records_corrected']
        N['d42_cov_corrected'] = _adj['coverage']['corrected']
        N['d42_items'] = N['d42_use_items'] + N['d42_cov_items']
        N['d42_corrected'] = N['d42_use_corrected'] + N['d42_cov_corrected']
    # v0.27: the team lead's spot check of the adjudication (page SMOTE25 Samples Check, scripts/merge_d42_check.py).
    # v0.38: the checks of all rounds, counted over the items that the codes of the samples as they now stand rest on: a
    # use-audit record coded again in round 2 keeps only round 2's checked items, and a paper that left the coverage
    # sample at the final merge (D28) no longer counts. Wording of b_coverage_design.tex: every coverage code that the
    # adjudication changed (in force) was checked, among other settled codes; of e_use.tex: every use-audit correction
    # that can change a count was checked (each round's page held all of them), with random samples of the other
    # changes, of the codes the adjudication kept and of the codes both coders gave. Round 3 (9 items, every one kept the
    # first code) changed no code, so it has no check page; were a later change left unchecked, the check below stops.
    def _d42rows(p):
        return list(csv.DictReader(open(p, encoding='utf-8-sig')))
    _cov_sample = {r['rec'] for r in _d42rows(S / 'samples/coverage_sample.csv')}
    _use_sample = {r['rec'] for r in _d42rows(S / 'samples/useaudit_sample.csv')}
    _again = {r['rec'] for r in _d42rows(_R2 / 'second_codes_useaudit.csv')} if _r2 else set()
    _rounds = [(1, _D42, _D42 / 'check_page/exports'), (2, _R2, _R2 / 'check_page/exports'),
               (3, _R3, _R3 / 'check_page/exports')]
    N['d42_r2_check_pending'] = int(_r2 and not (_R2 / 'spot_check_summary.json').exists())
    _checked, _bad = [], []
    for _rd, _dir, _exp in _rounds:
        if _rd == 2 and not _r2 or _rd == 3 and not _r3:
            continue
        if (_dir / 'spot_check_summary.json').exists():
            _sc = json.load(open(_dir / 'spot_check_summary.json', encoding='utf-8'))
            _ex = [r for f in sorted(_exp.glob('*.csv')) for r in _d42rows(f)]
            _latest = {}
            for _r in _ex:   # the latest decision per item counts
                if _r['item_key'] not in _latest or _r['time'] >= _latest[_r['item_key']]['time']:
                    _latest[_r['item_key']] = _r
            _its = [dict(group=r['group'], form=r['form'], rec=r['item'], field=r['field'], decision=r['decision'])
                    for r in _latest.values()]
            if len(_its) != _sc['items']:
                _bad.append(f'round {_rd}: the exports decide {len(_its)} of {_sc["items"]} items')
            for _frm in ('Use audit', 'Coverage sample'):
                if sum(_sc['decided_by_form'].get(_frm, {}).get('must', {}).values()) != _sc['items_by_form'].get(_frm, {}).get('must', 0):
                    _bad.append(f'round {_rd}: not every count-changing correction of the {_frm} was checked')
        else:
            _its = []
            if _rd == 2:
                N['d42_chk_use_n'] = N['d42_chk_use_changed'] = N['d42_chk_cov_n'] = N['d42_chk_cov_changed'] = 0
        for _it in _its:
            _proj = 'useaudit' if _it['form'] == 'Use audit' else 'coverage'
            if _proj == 'useaudit' and (_it['rec'] not in _use_sample or _rd == 1 and _it['rec'] in _again):
                continue
            if _proj == 'coverage' and _it['rec'] not in _cov_sample:
                continue
            _checked.append(dict(_it, project=_proj, round=_rd))
    if _checked and not N['d42_r2_check_pending']:
        _chk_u = [i for i in _checked if i['project'] == 'useaudit']
        _chk_c = [i for i in _checked if i['project'] == 'coverage']
        N['d42_chk_use_n'], N['d42_chk_use_changed'] = len(_chk_u), sum(i['decision'] == 'change' for i in _chk_u)
        N['d42_chk_cov_n'], N['d42_chk_cov_changed'] = len(_chk_c), sum(i['decision'] == 'change' for i in _chk_c)
        if not all(any(i['group'] == g for i in _chk_u) for g in ('changed', 'kept', 'fill')):
            _bad.append('a random sample of the use audit was not checked')
        # every coverage correction in force (the adjudication logs of the rounds, papers of the sample) was checked
        _logs = [(1, _D42 / 'adjudication_log.csv'), (2, _R2 / 'adjudication_log.csv'), (3, _R3 / 'adjudication_log.csv')]
        _corr = {(x['rec'], x['field']) for rd, lp in _logs if lp.exists() for x in _d42rows(lp)
                 if x['project'] == 'coverage' and x['how'] == 'corrected' and x['rec'] in _cov_sample}
        _seen = {(i['rec'], i['field']) for i in _chk_c}
        if not _corr <= _seen or len(_corr) != N.get('d42_cov_corrected'):
            _bad.append(f'the coverage corrections in force ({len(_corr)}, summary {N.get("d42_cov_corrected")}) '
                        f'are not all among the checked items ({len(_corr - _seen)} missing)')
        if N['d42_chk_cov_n'] <= len(_corr):
            _bad.append('the coverage items checked are only the changes; say so')
    if _bad:
        sys.exit('WORDING CHECK FAILED (revise b_coverage_design.tex or e_use.tex): ' + '; '.join(_bad))
# includes by kind and period (codes of the screen, from titles and abstracts) and the corpus by period
import re
for per in ('P1', 'P2', 'P3', 'P4'):
    inc = [r for r in dec_rows if r['decision'] == 'include' and r['period'] == per]
    N['inc_' + per] = len(inc)
    N['pass_' + per] = sum(1 for r in dec_rows if r['decision'] in ('include', 'unsure') and r['period'] == per)
    for code, lab in (('I1-generative', 'gen'), ('I1-new-variant', 'newvar'), ('I1-hybrid', 'hybrid'), ('I1-multiclass', 'multi'), ('I1-other', 'other')):
        k = sum(1 for r in inc if r['code'] == code)
        N[f'{lab}_{per}'] = k
        N[f'{lab}_{per}_pct'] = round(100 * k / len(inc)) if inc else 0
cy = []
for line in open(R / 'gen/table_methods_rows.tex', encoding='utf-8'):
    if line.count('&') >= 5:
        m = re.search(r'\b(19\d\d|20\d\d)\b', line.split('&')[1])
        if m:
            cy.append(int(m.group(1)))
for per, a, b in (('P1', 0, 2009), ('P2', 2010, 2015), ('P3', 2016, 2020), ('P4', 2021, 2027)):
    N['corpus_' + per] = sum(1 for y in cy if a <= y <= b)
    N['corpus_' + per + '_pct'] = f"{100 * N['corpus_' + per] / N['inc_' + per]:.1f}" if N['inc_' + per] else '0'
N['corpus_methods'] = len(cy)
N['ratio_P4'] = round(N['inc_P4'] / N['corpus_P4']) if N['corpus_P4'] else 0
inc_all = [r for r in dec_rows if r['decision'] == 'include']
for code, lab in (('I1-generative', 'gen'), ('I1-new-variant', 'newvar'), ('I1-hybrid', 'hybrid'), ('I1-multiclass', 'multi'), ('I1-other', 'other')):
    N[f'{lab}_all'] = sum(1 for r in inc_all if r['code'] == code)
    N[f'{lab}_all_pct'] = round(100 * N[f'{lab}_all'] / len(inc_all))
N['year2027'] = sum(1 for r in dec_rows if r['decision'] in ('include', 'unsure') and r['year'] == '2027')
N['year_future'] = str(max(int(r['year']) for r in dec_rows if r['decision'] in ('include', 'unsure') and r['year'].isdigit()))
if smp:
    q, wt = smp['useaudit']['pooled'], smp['useaudit']['weighted']
    N['use_notapp'] = q['coded'] - q['application']
    N['use_app_pct'] = round(100 * q['application'] / q['coded'], 1)
    for dom in ('medicine', 'finance', 'security', 'social', 'software', 'environment', 'industry', 'energy', 'bio', 'transport', 'business', 'education', 'other'):
        d = q['domain'].get(dom, {'k': 0, 'pct': 0.0})
        N['use_dom_' + dom] = d['k']
        N['use_dom_' + dom + '_pct'] = round(d['pct']) if d['pct'] is not None else 0
    N['use_med_w'] = wt['medicine']['pct']
    N['use_med_w_lo'], N['use_med_w_hi'] = wt['medicine']['ci95']
    N['use_ind'] = q['stakes_individual']['k']
    N['use_ind_pct'] = round(q['stakes_individual']['pct'])
    N['use_ind_w'] = wt['stakes_individual']['pct']
    N['use_smote'] = q['smote_named']['k']
    N['use_smote_pct'] = round(q['smote_named']['pct'])
    N['use_deep'] = q['deep_net']['k']
    N['use_deep_pct'] = round(q['deep_net']['pct'])
    N['use_tab'] = q['modality'].get('tabular', 0)
    N['use_ext_abs'] = q['validation_abstract_level'].get('external', 0)
    N['use_ft'] = q['fulltext']
    for k in ('stated', 'before-split', 'nr'):
        N['use_ft_' + k.replace('-', '_')] = q['ft_inside_folds'][k]['k']
    N['use_ft_before_pct'] = round(q['ft_inside_folds']['before-split']['pct']) if q['fulltext'] else 0
    N['use_ft_stated_pct'] = round(q['ft_inside_folds']['stated']['pct']) if q['fulltext'] else 0
    N['use_ft_none'] = q['ft_vs_none']['k']
    N['use_ft_weights'] = q['ft_vs_weights']['k']
    N['use_ft_calib'] = q['ft_calibration']['k']
    N['use_ft_testbal'] = q['ft_test_balanced']['yes']['k']
    N['use_ft_testnat'] = q['ft_test_balanced']['no']['k']
    N['use_ft_external'] = q['ft_validation']['external']['k']
    N['use_ft_beyond'] = sum(q['ft_validation'][k]['k'] for k in ('external', 'prospective', 'deployed'))
    N['use_ft_prosp'] = q['ft_validation']['prospective']['k']
    N['use_ft_deployed'] = q['ft_validation']['deployed']['k']
    N['use_ft_acc'] = q['ft_accuracy']['k']
    N['use_ft_roc'] = q['ft_roc_auc']['k']
    N['use_ft_pr'] = q['ft_pr_auc']['k']
    for s, v in smp['useaudit']['strata'].items():
        N[f'use_{s}_ft'] = v['fulltext_coded']
        N[f'use_{s}_before'] = v['inside_folds'].get('before-split', 0)
        N[f'use_{s}_stated'] = v['inside_folds'].get('stated', 0)
    # v0.37 (the library round): the final full-text shares of Section 8.3, the leak's share with the periods weighted
    # by their size, and its change across the periods (chi-square test of the 3 x 2 table: with two degrees of freedom
    # p = exp(-chi2 / 2)); the wording checks of e_use.tex below use them
    N['use_ft_missing'] = N['use_ft_target'] - N['use_ft_obtained']
    N['use_ft_before_w'] = wt['before_split']['pct']
    N['use_ft_before_w_lo'], N['use_ft_before_w_hi'] = wt['before_split']['ci95']
    N['use_ft_before_w_r'] = int(wt['before_split']['pct'] + 0.5)
    N['use_ft_before_w_lo_r'], N['use_ft_before_w_hi_r'] = (int(x + 0.5) for x in wt['before_split']['ci95'])

    def _chi2_p(kn):
        import math
        K, T = sum(k for k, _ in kn), sum(n for _, n in kn)
        P = K / T
        x2 = sum((k - n * P) ** 2 / (n * P) + ((n - k) - n * (1 - P)) ** 2 / (n * (1 - P)) for k, n in kn)
        return math.exp(-x2 / 2)
    _per = ('U1', 'U2', 'U3')
    N['use_ft_before_trend_p'] = f"{_chi2_p([(N[f'use_{s}_before'], N[f'use_{s}_ft']) for s in _per]):.2f}"
    N['use_ft_stated_trend_p'] = f"{_chi2_p([(N[f'use_{s}_stated'], N[f'use_{s}_ft']) for s in _per]):.2f}"
# v0.10: the harm search of Section 8.5 (WP5 step 4, AI first pass; wp5/harm_search/)
_HS = R / 'wp5/harm_search/work/summary.json'
if _HS.exists():
    import csv as _csv
    hs = json.load(open(_HS, encoding='utf-8'))
    hr = list(_csv.DictReader(open(R / 'wp5/harm_search/harm_search_records.csv', encoding='utf-8')))
    hq = json.load(open(R / 'wp5/harm_search_log.json', encoding='utf-8'))
    fnd = hs['includes_by_finding']
    N['harm_records'] = hs['records']
    N['harm_include'] = hs['decision'].get('include', 0)
    N['harm_unsure'] = hs['decision'].get('unsure', 0)
    N['harm_exclude'] = hs['decision'].get('exclude', 0)
    N['harm_calib'] = hs['includes_by_harm'].get('H-calibration', 0)
    N['harm_calib_harm'] = fnd.get('H-calibration', {}).get('harm', 0)
    N['harm_calib_noharm'] = fnd.get('H-calibration', {}).get('no harm', 0)
    N['harm_calib_mixed'] = fnd.get('H-calibration', {}).get('mixed', 0)
    N['harm_leak'] = hs['includes_by_harm'].get('H-leakage', 0)
    N['harm_leak_harm'] = fnd.get('H-leakage', {}).get('harm', 0)
    N['harm_fair'] = hs['includes_by_harm'].get('H-fairness', 0)
    N['harm_fair_noharm'] = fnd.get('H-fairness', {}).get('no harm', 0)
    N['harm_fair_mixed'] = fnd.get('H-fairness', {}).get('mixed', 0)
    N['harm_priv'] = hs['includes_by_harm'].get('H-privacy', 0)
    N['harm_calib_nocomp'] = hs['harm_measure_reported_without_comparison'].get('calibration', 0)
    for q in hq:
        if q['query'][:2] in ('H1', 'H2', 'H3', 'H4'):
            N['harm_q' + q['query'][1]] = q['count']
    N['harm_priv_unsure'] = sum(1 for r in hr if 'H3' in r['queries'].split('+') and r['decision'] == 'unsure')
    N['harm_priv_records'] = sum(1 for r in hr if 'H3' in r['queries'].split('+'))
# v0.10: the rerun on the reference collection (Section 9.2, Table 17, Appendix F; benchmark/rerun42/)
_RR = R / 'benchmark/results_summary/rerun42'
if (_RR / 'summary.json').exists():
    import csv as _csv
    rr = json.load(open(_RR / 'summary.json', encoding='utf-8'))
    N['rr_tasks'] = rr['tasks']
    N['rr_families'] = rr['families']
    N['rr_cells'] = rr['fold_results']
    N['rr_ok'] = rr['ok']
    N['rr_error'] = rr['cells_by_status'].get('error', 0)
    N['rr_na'] = rr['cells_by_status'].get('not applicable', 0)
    c1 = list(_csv.DictReader(open(_RR / 'c1_rerun.csv', encoding='utf-8')))
    var = [r for r in c1 if r['method'] not in ('none', 'class_weight', 'threshold', 'ROS')]
    for v in ('yes', 'no', 'not testable'):
        N['rr_c1_' + v.replace(' ', '_')] = sum(1 for r in var if r['c1_rerun'] == v)
    tv = {(r['learner'], r['measure'], r['method']): r for r in _csv.DictReader(open(_RR / 'tests_vs_smote.csv', encoding='utf-8'))}

    def _d(x):
        return f"{float(x):+.3f}".replace('+', '+').replace('-', '$-$')
    for m in ('none', 'class_weight', 'threshold', 'ROS', 'Cluster-SMOTE', 'ADASYN', 'Safe-Level-SMOTE', 'CGMOS', 'SMOM', 'G-SMOTE',
              'AB-SMOTE', 'RSMOTE', 'FW-SMOTE'):
        k = m.replace('-', '').replace('_', '').lower()
        for ln in ('RF', 'GB'):
            for ms in ('roc_auc', 'pr_auc', 'gmean', 'brier'):
                r = tv.get((ln, ms, m))
                if r:
                    N[f'rr_{k}_{ms.replace("_", "")}_{ln.lower()}'] = _d(r['median_diff_vs_smote'])
                    N[f'rr_{k}_{ms.replace("_", "")}_{ln.lower()}_fam'] = int(r['n_families'])
                    N[f'rr_{k}_{ms.replace("_", "")}_{ln.lower()}_abs'] = f"{abs(float(r['median_diff_vs_smote'])):.3f}"
    N['rr_rope'] = f"{rr['rule']['rope']:.2f}"
    N['rr_collection'] = sum(1 for _ in _csv.DictReader(open(R / 'benchmark/rerun42/out/tasks42_check.csv', encoding='utf-8')))
    N['rr_test_families'] = max(int(r['n_families']) for r in tv.values() if r['learner'] in ('RF', 'GB') and r['measure'] in ('roc_auc', 'pr_auc'))
    _var = ('Cluster-SMOTE', 'ADASYN', 'Safe-Level-SMOTE', 'CGMOS', 'SMOM', 'G-SMOTE', 'AB-SMOTE', 'RSMOTE', 'FW-SMOTE')
    _vr = [r for r in tv.values() if r['method'] in _var and r['learner'] in ('RF', 'GB') and r['measure'] in ('roc_auc', 'pr_auc')]
    N['rr_var_maxabs'] = f"{max(abs(float(r['median_diff_vs_smote'])) for r in _vr):.3f}"
    N['rr_var_holm_sig'] = sum(1 for r in _vr if float(r['holm_p']) < 0.05)
    N['rr_var_tests'] = len(_vr)
    for _m, _k in (('none', 'none'), ('threshold', 'threshold'), ('class_weight', 'classweight')):
        _r = tv.get(('GB', 'pr_auc', _m))
        if _r:
            N[f'rr_{_k}_prauc_gb_psmote'] = f"{float(_r['p_smote_better']):.2f}"
    N['rr_incomplete'] = len(rr.get('tasks_incomplete_left_out', {}))
    import pandas as _pd
    _pf = _pd.read_csv(_RR / 'per_family_means.csv')
    _ten = ['SMOTE'] + list(_var)
    for _ln in ('RF', 'GB'):
        for _ms in ('roc_auc', 'pr_auc'):
            _w = _pf[(_pf.learner == _ln) & _pf.method.isin(_ten)].pivot(index='family', columns='method', values=_ms)
            _w = _w[_w['SMOTE'].notna()]
            _rg = _w.max(axis=1) - _w.min(axis=1)
            N[f'rr_range_{_ms.replace("_", "")}_{_ln.lower()}'] = f"{_rg.median():.3f}"
            N[f'rr_range_{_ms.replace("_", "")}_{_ln.lower()}_n01'] = int((_rg > 0.01).sum())
            _sm = _w['SMOTE']
            N[f'rr_smote_{_ms.replace("_", "")}_{_ln.lower()}_median'] = f"{_sm.median():.2f}"
    # v0.63 (note 23 of the read-through of 23 Nov 2026): the spread over families behind the Bayesian probability
    # for no resampling against SMOTE, PR-AUC with gradient boosting (Section 9.2)
    _w = _pf[(_pf.learner == 'GB') & _pf.method.isin(['SMOTE', 'none'])].pivot(index='family', columns='method', values='pr_auc').dropna()
    _dn = _w['none'] - _w['SMOTE']
    if len(_dn) != N['rr_test_families'] or abs(float(_dn.median())) >= 0.0005:
        sys.exit('STOP: the families or the median of no resampling against SMOTE (PR-AUC, GB) changed; revise h_rerun.tex')
    N['rr_none_prauc_gb_nworse'] = int((_dn < -float(rr['rule']['rope'])).sum())
    N['rr_none_prauc_gb_nbetter'] = int((_dn > float(rr['rule']['rope'])).sum())
    # v0.11: where the tasks ran, and how far the two machines agree on the tasks that ran on both (cross_machine42.py)
    if (_RR / 'cross_machine.json').exists():
        xm = json.load(open(_RR / 'cross_machine.json', encoding='utf-8'))
        N['rr_tasks_cloud'] = xm['tasks_used_from_cloud']
        N['rr_tasks_mac'] = xm['tasks_used_from_mac']
        for _t, _v in xm['per_task'].items():
            N['rr_xm_pct_' + _t.lower().replace(' ', '').replace('-', '').replace('_', '')] = int(round(_v['pct_value_differ']))
        N['rr_xm_mean_max'] = f"{xm['max_abs_diff_of_means']:.3f}"
        N['rr_xm_vs_smote_max'] = f"{xm['max_change_of_diff_vs_smote_rf_gb']:.3f}"
# v0.29 (D43): the TabPFN arm of the rerun (stats42_tabpfn.py and tabpfn_cells42.py, both in benchmark/rerun42/scripts),
# for the paragraph of Section 7.5 (search_templates/j_tabpfn.tex); its wording is checked at the end of this script
_TP = R / 'benchmark/results_summary/rerun42/tabpfn'
_tbad = []
if (_TP / 'summary.json').exists():
    import csv as _csv4
    import math as _math
    _ts = json.load(open(_TP / 'summary.json', encoding='utf-8'))
    _tc = json.load(open(_TP / 'cells.json', encoding='utf-8'))
    _cmp = {(r['comparison'], r['measure']): r for r in _csv4.DictReader(open(_TP / 'tabpfn_comparisons.csv', encoding='utf-8'))}

    def _below2(x):  # a strict upper bound with two decimals ("p below"), never equal to the value
        return f'{(_math.floor(float(x) * 100 + 1e-9) + 1) / 100:.2f}'

    def _floor2(x):  # a lower bound printed with two decimals ("at least")
        return f'{_math.floor(float(x) * 100 + 1e-9) / 100:.2f}'
    _SM = 'TabPFN: SMOTE vs none'
    _VS = ['TabPFN vs RF, both none', 'TabPFN vs GB, both none', 'TabPFN none vs RF after SMOTE', 'TabPFN none vs GB after SMOTE']
    _M3 = ('roc_auc', 'pr_auc', 'brier')
    N['tp_package'] = _tc['config']['package']
    N['tp_model'] = _tc['config']['model'].rsplit('.V', 1)[-1].replace('_', '.')   # ModelVersion.V3_5 -> 3.5
    N['tp_tasks'] = _ts['tasks_complete']
    N['tp_families'] = _ts['families']
    N['tp_left'] = len(_ts['tasks_left_out'])
    N['tp_cells'] = _tc['cells']
    N['tp_ok'] = _tc['ok']
    N['tp_rf_cloud'] = _tc['rf_gb_tasks_from_first_dir']
    for _ms, _k in zip(_M3, ('roc', 'pr', 'brier')):
        N[f'tp_sm_{_k}'] = f"{abs(float(_cmp[(_SM, _ms)]['median_diff'])):.3f}"
        N[f'tp_sm_bay_{_k}'] = f"{float(_cmp[(_SM, _ms)]['p_second_better']):.2f}"
    N['tp_sm_holm_below'] = _below2(max(float(_cmp[(_SM, m)]['holm_p']) for m in _M3))
    for _ms, _k in (('roc_auc', 'roc'), ('pr_auc', 'pr')):
        _v = [float(_cmp[(c, _ms)]['median_diff']) for c in _VS]
        N[f'tp_vs_{_k}_min'] = f'{min(_v):.3f}'
        N[f'tp_vs_{_k}_max'] = f'{max(_v):.3f}'
    N['tp_vs_holm_below'] = _below2(max(float(_cmp[(c, m)]['holm_p']) for c in _VS for m in ('roc_auc', 'pr_auc')))
    N['tp_vs_bay_min'] = _floor2(min(float(_cmp[(c, m)]['p_first_better']) for c in _VS for m in ('roc_auc', 'pr_auc')))
    _bv = [float(_cmp[(c, 'brier')]['median_diff']) for c in _VS[1:]]
    N['tp_vs_brier_min'] = f'{min(_bv):.3f}'
    N['tp_vs_brier_max'] = f'{max(_bv):.3f}'
    # what the paragraph says, tested against the result (a later run that changes any of it stops the chain)
    _rope = float(_ts['rule']['rope'])
    if (sorted(_tc['tasks_by_kind'].get('out of memory', [])) != ['musk', 'smoke detection']
            or sorted(_tc['tasks_by_kind'].get('sampler', [])) != ['ecoli-0-1-3-7_vs_2-6', 'ijcnn1'] or N['tp_left'] != 4):
        _tbad.append('the tasks left out are not musk and smoke detection (memory) and ijcnn1 and one ecoli task (sampler)')
    if not all(float(_cmp[(_SM, m)]['median_diff']) < -_rope and float(_cmp[(_SM, m)]['holm_p']) < 0.05 for m in _M3):
        _tbad.append('SMOTE does not make TabPFN worse, beyond the margin and with Holm p < 0.05, on all three measures')
    if not all(float(_cmp[(c, m)]['median_diff']) > _rope and float(_cmp[(c, m)]['holm_p']) < 0.05
               for c in _VS for m in ('roc_auc', 'pr_auc')):
        _tbad.append('TabPFN alone does not rank better than both strong learners, with and without SMOTE')
    if not (abs(float(_cmp[(_VS[0], 'brier')]['median_diff'])) <= _rope and all(v > _rope for v in _bv)):
        _tbad.append('the Brier scores are not: on par with the random forest alone, lower than the other three')
    if _tc['folds_same_as_rerun'] != _tc['folds_compared'] or N['tp_rf_cloud'] >= N['tp_tasks']:
        _tbad.append('the folds differ from the rerun, or no strong-learner cell comes from the MacBook')
# v0.31: the spot check of the WP3 adjudication (D31; page "SMOTE25 WP3 Check", scripts/merge_wp3_check.py), reported
# in Section 3.7 by scripts/search_templates/k_wp3_spot.tex. The wording names what the 80 items were and says that the
# one item marked for change (RBO, D36) was settled by checking the project page and changed no value; _wbad stops the
# chain if the merged check no longer bears that out.
_W = R / 'wp3/adjudication'
_wbad = []
N['wp3_chk_n'] = 0
if (_W / 'WP3_spot_check_summary.json').exists():
    import csv as _csv
    _ws = json.load(open(_W / 'WP3_spot_check_summary.json', encoding='utf-8'))
    _wrows = list(_csv.DictReader(open(R / 'wp3/check_page/exports' / _ws['export'], encoding='utf-8-sig')))
    _wkeys = [r['item_key'] for r in _wrows]
    _wit, _wdec, _wfr = _ws['items_by_group_form'], _ws['decided_by_group_form'], _ws['frames']
    _wtot = sum(sum(c.values()) for c in _ws['totals'].values())
    _wagree = sum(c.get('agree', 0) for c in _ws['totals'].values())
    _mr = list(_csv.DictReader(open(_W / 'MODIFIED_RELEASED_adjudicated.csv', encoding='utf-8')))
    _mrs = json.load(open(_W / 'MODIFIED_RELEASED_summary.json', encoding='utf-8'))
    _wsum = json.load(open(_W / 'WP3_summary.json', encoding='utf-8'))
    N['wp3_chk_n'] = _wtot
    N['wp3_chk_agree'] = _wagree
    N['wp3_chk_d36'] = sum(k.startswith('rel_') for k in _wkeys)
    N['wp3_chk_d35'] = sum(k.startswith('d35_') for k in _wkeys)
    N['wp3_chk_me'] = _wit['changed'].get('Method', 0) + _wit['changed'].get('Evaluation', 0)
    N['wp3_chk_other_n'] = _wit['changed'].get('Data extraction', 0) + _wit['changed'].get('Data handling', 0)
    N['wp3_chk_other_frame'] = _wfr['changed']['Data extraction'] + _wfr['changed']['Data handling']
    N['wp3_chk_kept_n'] = sum(_wit['kept'].values())
    N['wp3_chk_kept_frame'] = _wfr['kept']
    N['wp3_chk_fill_n'] = sum(_wit['fill'].values())
    N['wp3_chk_fill_frame'] = _wsum['agreements_checked']['results']['fill']
    if len(_ws['totals']) != 1 or _wtot != _ws['items'] or len(set(_wkeys)) != _wtot:
        _wbad.append('not one reviewer deciding every item of the page once')
    if N['wp3_chk_d36'] != len(_mr) or 'glos' not in _wkeys or N['wp3_chk_d35'] != 4:
        _wbad.append('the must-check items are not the papers read for D36, GLOS and the four D35 variants')
    if (N['wp3_chk_d36'] + 1 + N['wp3_chk_d35'] + N['wp3_chk_me'] + N['wp3_chk_other_n'] + N['wp3_chk_kept_n']
            + N['wp3_chk_fill_n']) != _wtot:
        _wbad.append('the groups named do not add up to the items checked')
    if N['wp3_chk_me'] != _wfr['changed']['Method'] + _wfr['changed']['Evaluation']:
        _wbad.append('not every method and evaluation correction was checked')
    if not (0 < N['wp3_chk_other_n'] < N['wp3_chk_other_frame'] and 0 < N['wp3_chk_kept_n'] < N['wp3_chk_kept_frame']
            and 0 < N['wp3_chk_fill_n'] < N['wp3_chk_fill_frame']):
        _wbad.append('the other groups are not proper samples of their frames')
    _rbo = [r for r in _mr if r['paper'] == 'RBO']
    if not (_ws['changes'] == ['rel_RBO'] and _wagree == _wtot - 1
            and _mrs.get('spot_check', {}).get('marked_for_change') == ['RBO']
            and _mrs['spot_check'].get('decision_changed') == [] and _rbo and _rbo[0]['adjudicated'] == 'no'
            and 'project page' in _rbo[0]['note'] and 'not released' in _rbo[0]['note']):
        _wbad.append('the one change is not RBO (D36), or its project-page check changed a value')
# v0.34: the check of the 16 adjudications behind two counts of Table 5 that the random samples of the spot check left
# out (page "SMOTE25 WP3 Count Check", scripts/merge_wp3_count_check.py), reported in Section 3.7 by
# scripts/search_templates/k_wp3_count.tex. The items are recounted here from the adjudication: every data-handling
# adjudication that changes whether a paper counts as giving a reason (D34) or as having data binarized by anyone.
# v0.35 (the author's Final Pass note of 15 Nov: an overview, not the number of each step): the wording gives no
# numbers; it says that the author checked, on a second page, the remaining adjudications that move a count of Table 5
# (those the first page did not hold) and agreed with all of them, so that no count changed. The checks below still
# hold the page to those items; a seventh fails if the adjudication's paper-level counts gain one other than the two the
# page covered (the counts of modified and released data rest on the first page's GLOS and D36 items, which the checks
# of k_wp3_spot.tex hold); _cbad stops the chain otherwise.
_cbad = []
N['wp3_cnt_n'] = 0
if (_W / 'WP3_count_check_summary.json').exists():
    import csv as _csv
    _cs = json.load(open(_W / 'WP3_count_check_summary.json', encoding='utf-8'))
    _crows = list(_csv.DictReader(open(R / 'wp3/count_check/exports' / _cs['export'], encoding='utf-8-sig')))
    _dh = list(_csv.DictReader(open(_W / 'DATA_handling_adjudicated.csv', encoding='utf-8')))
    _REASON = ('own reason', 'cites prior work', 'reason given')
    _flip_r = {r['paper'] for r in _dh if r['field'] == 'crit_type'
               and (r['first_pass'] in _REASON) != (r['adjudicated_value'] in _REASON)}
    _flip_b = {r['paper'] for r in _dh if r['field'] == 'origin:Binarised' and r['first_pass'] != r['adjudicated_value']}
    _first = {(r['paper'], r['field']): r['decision'] for r in csv.DictReader(open(
        R / 'wp3/check_page/exports' / json.load(open(_W / 'WP3_spot_check_summary.json', encoding='utf-8'))['export'],
        encoding='utf-8-sig')) if r['form'] == 'Data handling'} if (_W / 'WP3_spot_check_summary.json').exists() else {}
    _before_r = {p for p in _flip_r if (p, 'crit_type') in _first}
    _before_b = {p for p in _flip_b if (p, 'origin:Binarised') in _first}
    _page_r = {r['paper'] for r in _crows if r['group'] == 'reason'}
    _page_b = {r['paper'] for r in _crows if r['group'] == 'binar'}
    N['wp3_cnt_reason'] = len(_flip_r)
    N['wp3_cnt_binar_all'] = len(_flip_b)
    N['wp3_cnt_binar_before'] = len(_before_b)
    N['wp3_cnt_binar'] = len(_page_b)
    N['wp3_cnt_n'] = len(_crows)
    N['wp3_cnt_agree'] = sum(r['decision'] == 'agree' for r in _crows)
    _after = _wsum['paper_level_after_adjudication'] if (_W / 'WP3_spot_check_summary.json').exists() else {}
    if len({r['reviewer'] for r in _crows}) != 1 or len({r['item_key'] for r in _crows}) != len(_crows) \
            or len(_crows) != _cs['items'] or any(_cs['undecided'].values()):
        _cbad.append('not one reviewer deciding every item of the page once')
    if _before_r or _page_r != _flip_r:
        _cbad.append('the reason items are not all the reason changes, or some were among the first page\'s items')
    if _page_b != _flip_b - _before_b or any(_first[(p, 'origin:Binarised')] != 'agree' for p in _before_b):
        _cbad.append('the binarization items are not the changes the first page left out, or one it held was not agreed')
    if N['wp3_cnt_n'] != len(_page_r) + len(_page_b):
        _cbad.append('the two groups named do not add up to the items checked')
    if N['wp3_cnt_agree'] != N['wp3_cnt_n'] or _cs['changes'] or _cs['requests']:
        _cbad.append('the author did not agree with all of them')
    _cc = list(_cs['counts'].values())[0] if _cs['counts'] else {}
    if not _cc or any(v['changes_the_paper'] or v['with_decisions'] != v['after_adjudication'] for v in _cc.values()) \
            or _cc['reason']['after_adjudication'] != _after.get('reason_given') \
            or _cc['binar']['after_adjudication'] != _after.get('binarised_by_anyone'):
        _cbad.append('a count changed, or the page\'s counts are not those of WP3_summary.json')
    _extra = sorted(k for k, v in _after.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
                    and k not in ('papers_with_evaluation', 'reason_given', 'no_reason', 'binarised_by_anyone'))
    if _extra:
        _cbad.append('the adjudication moves a paper-level count that the page did not cover: ' + ', '.join(_extra))
json.dump({k: f(v) for k, v in N.items()} | DICTS | {'_raw': N}, open(S / 'decisions/search_numbers.json', 'w', encoding='utf-8'), indent=1)
print(json.dumps({k: f(v) for k, v in N.items()}, indent=0)[:2500])
# v0.12: the words of Section 4.4 (scripts/search_templates/c_beyond.tex) that the counts must bear out; a correction or
# merge that breaks one stops the chain here (the numbers are written) so that the wording is revised by hand
_P = ('P1', 'P2', 'P3', 'P4')
_claims = {
    'new variants are the largest kind of include in every period':
        all(N[f'newvar_{p}'] >= max(N[f'{k}_{p}'] for k in ('gen', 'hybrid', 'multi', 'other')) for p in _P),
    'the share of hybrids falls from period to period': all(N[f'hybrid_{a}_pct'] >= N[f'hybrid_{b}_pct'] for a, b in zip(_P, _P[1:])),
    'generative oversamplers rise in the last two periods':
        N['gen_P3_pct'] > max(N['gen_P1_pct'], N['gen_P2_pct']) and N['gen_P4_pct'] > N['gen_P3_pct'],
    'the corpus covers the early literature more closely than the recent': N['inc_P1'] / N['corpus_P1'] < N['inc_P4'] / N['corpus_P4'],
}
# v0.37: the comparison with the corpus in Section 4.4 (third paragraph) and the abstract (f_abstract_results.tex)
if smp:
    def _share(key):
        return 100 * _CORPUS[key][0] / _CORPUS[key][1]

    def _inside(key):
        return _covrows[key]['ci95'][0] <= _share(key) <= _covrows[key]['ci95'][1]

    def _above(key):
        return _share(key) > _covrows[key]['ci95'][1]
    _gap = sorted('SANPFL', key=lambda k: _share(k) - _covrows[k]['pct'], reverse=True)
    _claims.update({
        'the sample reproduces the shape of the family (most Core, most binary only, about half state the folds; the '
        'corpus inside the intervals)': _covrows['core']['pct'] > 50 and _inside('core') and _covrows['B']['pct'] > 50
        and _inside('B') and 40 <= _covrows['inside']['pct'] <= 60 and _inside('inside'),
        'the sample\'s variants change fewer decisions, seed selection and sample allocation above all':
            float(N['cov_dec_mean']) < float(N['corpus_dec_mean']) and set(_gap[:2]) == {'S', 'A'}
            and _above('S') and _above('A'),
        'more of the sample\'s methods generate in another way, most of them since 2016':
            _share('notcounted') < _covrows['notcounted']['ci95'][0] and 2 * N['cov_notcounted_since2016'] > N['cov_notcounted'],
        'the sample\'s evaluations are lighter (fewer repeat partitions, test significance, release code or choose '
        'settings on test scores)': all(_above(k) for k in ('repeated', 'stat_test', 'code', 'tuning_test')),
    })
_broken = [c for c, ok in _claims.items() if not ok]
if _broken:
    sys.exit('WORDING CHECK FAILED (revise c_beyond.tex and f_abstract_results.tex): ' + '; '.join(_broken))
# v0.37: the change of the leak across the periods in Section 8.3 (e_use.tex) and the abstract
if smp:
    _ub = []
    if float(N['use_ft_before_trend_p']) < 0.05:
        _ub.append('the share that resampled before the split changes across the periods (the text says no trend)')
    _st = {s: N[f'use_{s}_stated'] / N[f'use_{s}_ft'] for s in ('U1', 'U2', 'U3')}
    if not (_st['U3'] > max(_st['U1'], _st['U2']) and float(N['use_ft_stated_trend_p']) < 0.05):
        _ub.append('more papers since 2024 state the training-only fit: not borne out')
    if _ub:
        sys.exit('WORDING CHECK FAILED (revise e_use.tex): ' + '; '.join(_ub))
    print('wording checks of e_use.tex (periods) hold: 2')
print('wording checks of c_beyond.tex hold:', len(_claims))
# v0.29: the wording checks of j_tabpfn.tex (Section 7.5), computed above with its keys
if _tbad:
    sys.exit('WORDING CHECK FAILED (revise j_tabpfn.tex): ' + '; '.join(_tbad))
# v0.31: the wording checks of k_wp3_spot.tex (Section 3.7)
if _wbad:
    sys.exit('WORDING CHECK FAILED (revise k_wp3_spot.tex): ' + '; '.join(_wbad))
if N['wp3_chk_n']:
    print('wording checks of k_wp3_spot.tex hold: 6')
# v0.34: the wording checks of k_wp3_count.tex (Section 3.7)
if _cbad:
    sys.exit('WORDING CHECK FAILED (revise k_wp3_count.tex): ' + '; '.join(_cbad))
if N['wp3_cnt_n']:
    print('wording checks of k_wp3_count.tex hold: 7')
if (_TP / 'summary.json').exists():
    print('wording checks of j_tabpfn.tex hold: 5')
# v0.39: the final-pass rule of 17 Nov 2026 (say what the authors and the AI did, not what they did not do) replaced
# phrases that named an absence ("excluding none", "none needed correcting", "that the check did not read"); the
# positive wording holds only while the numbers bear it out, so these checks stop the chain otherwise.
def _i(v):
    return int(str(v).replace(',', ''))
_pbad = []
if _i(N['known_include']) + _i(N['known_unsure']) != _i(N['known_n']):
    _pbad.append('a_screen.tex: the known SMOTE-family papers are not all included or unsure (the screen excluded one)')
if _i(N['ruleb_applied']) + _i(N['ruleb_sample_includes_both']) != _i(N['ruleb_read']):
    _pbad.append('a_screen.tex: "the other included records" are not the included records outside the shared sample')
if _i(N.get('d42_chk_cov_n', 0)) and _i(N['d42_chk_cov_changed']):
    _pbad.append('b_coverage_design.tex: the author corrected a code ("found all of them correct" no longer holds)')
if _i(N.get('d42_chk_use_n', 0)) and _i(N['d42_chk_use_changed']):
    _pbad.append('e_use.tex: the author corrected a code ("found all of them correct" no longer holds)')
if 'tp_tasks' in N and _i(N['rr_tasks']) - _i(N['tp_tasks']) != 4:
    _pbad.append('j_tabpfn.tex: "the other tasks" are not the rerun\'s tasks less the four named')
if _pbad:
    sys.exit('WORDING CHECK FAILED (v0.39 rule): ' + '; '.join(_pbad))
print('wording checks of the v0.39 rule hold: 5')
