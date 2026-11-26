#!/usr/bin/env python3
"""WP1 step 1: number ledger. One row for every number in the text of the draft.

Columns: id, value_in_text, where (file:line and section), tag (provenance), source_file,
source_field_or_query, status (ok, conflict, open, stale), note, context.
Rules (applied in order):
  * numbers inside [Team: ...] notes, citations, labels and cross-references are skipped;
  * rows of Table 4 (tab:denominators) are 'conflict' while their status cell says Open (v0.4: decided rows are ok);
  * values listed in OVERRIDES carry the source and status given there (numbers recomputed or
    re-pulled in this session, and numbers changed on purpose);
  * D, M, E blocks: 'ok' when the number occurs in the attributed section PDF, else 'conflict';
  * S blocks: 'ok' when the number occurs in one of the three section PDFs (synthesis of them), else 'open';
  * R blocks: 'open' unless an override gives the external source.
Usage: python3 scripts/build_ledger.py . ledger.csv
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_numbers import NUM, STRIP, TAG, found, norm_pdf  # noqa: E402

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
PDF = {'D': 'data-section-jair.pdf', 'M': 'method-section-draft-preview.pdf', 'E': 'SMOTE25_Evaluation_Section.pdf'}
TXT = {k: norm_pdf((ROOT / 'src' / f).read_text(encoding='utf-8', errors='ignore'))
       for k, f in {'D': 'data.txt', 'M': 'method.txt', 'E': 'eval.txt'}.items()}
OA = 'data/openalex/2026-11-10/'
# value -> (source_file, field_or_query, status, note); applies to S and R blocks and to the listed changes
OVERRIDES = {
    # v0.4: WP4 identification (10 Nov 2026, UTC; v0.8 corrected the dates)
    '16414': ('data/search/2026-11-11/scopus_search_log.json', 'documents_found', 'ok', 'Scopus, 10 Nov 2026 16:44 UTC'),
    '1546': ('data/search/2026-11-11/scopus_search_log.json', 'preprints_tab', 'ok', 'Scopus preprint index, not exportable'),
    '14448': ('data/search/2026-11-11/openalex_search_log.json', 'count', 'ok', 'OpenAlex meta.count, run of 10 Nov 2026 17:08 UTC'),
    '14445': ('data/search/2026-11-11/openalex_search_log.json', 'sum of pages[].n', 'ok', 'records retrieved'),
    '693': ('data/search/2026-11-11/arxiv_search_log.json', 'total_results', 'ok', 'arXiv API, run of 10 Nov 2026 17:03 UTC'),
    '22426': ('data/search/2026-11-11/wp4_records_merged_summary.json', 'unique_after_dedup', 'ok', 'scripts/wp4_merge_records.py'),
    '31552': ('data/search/2026-11-11/wp4_records_merged_summary.json', 'records_total', 'ok', ''),
    # v0.4: Section 7.5 keyword counts on unscreened records
    '1727': ('data/search/2026-11-11/wp7_keyword_counts.json', 'any_deep_generative_total', 'ok', 'scripts/wp7_keyword_counts.py'),
    '262': ('data/search/2026-11-11/wp7_keyword_counts.json', 'any_deep_generative.2018-2022', 'ok', ''),
    '1463': ('data/search/2026-11-11/wp7_keyword_counts.json', 'any_deep_generative.2023-2026', 'ok', ''),
    # v0.4: M5, Kovacs (2019) Table 3, journal PDF read 11 Nov 2026 (checks/kovacs2019_M5_notes.md)
    '0.857': ('kovacs2019empirical, Table 3', 'AUC, SVM, no sampling .8568', 'ok', 'rounded to three decimals'),
    '0.900': ('kovacs2019empirical, Table 3', 'AUC, SVM, SMOTE .8999', 'ok', 'rounded to three decimals'),
    '0.812': ('kovacs2019empirical, Table 3', 'AUC, DT, no sampling .8124', 'ok', 'rounded to three decimals'),
    '0.881': ('kovacs2019empirical, Table 3', 'AUC, DT, SMOTE .8809', 'ok', 'rounded to three decimals'),
    '0.01': ('kovacs2019empirical, Table 3', 'AUC, SVM: best .9089 against SMOTE .8999', 'ok', 'about 0.01'),
    '10000': ('hollmann2025tabpfn, abstract (Crossref record)', 'datasets with up to 10,000 samples', 'ok', ''),
    '5.7': ('wp5/pypistats_imbalanced_learn.json', 'data.last_month = 5,708,559', 'ok', '10 Nov 2026'),
    '7.1': ('wp5/README.md', 'GitHub stars shown on the repository page', 'ok', '10 Nov 2026, web fetch'),
    '0.901': ('kovacs2019ranking (docs/ranking.rst)', 'mean AUC of the top ten', 'ok', ''),
    '0.904': ('kovacs2019ranking (docs/ranking.rst)', 'mean AUC of the top ten', 'ok', ''),
    '0.862': ('kovacs2019ranking (docs/ranking.rst)', 'mean G-mean of the top ten', 'ok', ''),
    '0.871': ('kovacs2019ranking (docs/ranking.rst)', 'mean G-mean of the top ten', 'ok', ''),
    '558': ('data-section-jair.pdf', 'comparisons inside a wrapper', 'ok', ''),
    '1755': ('data-section-jair.pdf', 'named entries', 'ok', ''),
    '524': ('data-section-jair.pdf', 'datasets in the comparisons', 'ok', ''),
    '0.14.2': ('pip show imbalanced-learn', 'version', 'ok', ''),
}
# counts of the archived OpenAlex snapshot of 10 Nov 2026, 15:52 UTC (scripts/after_snapshot.py writes derived.json)
import json as _json
_der = ROOT / 'data/openalex/2026-11-10/derived.json'
if _der.exists():
    _d = _json.loads(_der.read_text())
    _snap = 'data/openalex/2026-11-10/derived.json'
    _note = '10 Nov 2026 15:52 UTC, raw JSON archived'
    def _put(v, field):
        OVERRIDES[str(v)] = (_snap, field, 'ok', _note)
    for _y, _c in _d['by_year'].items():
        if _c >= 100:
            _put(_c, f'citing works published in {_y}')
    _put(sum(_d['by_year'].values()), 'sum of the year groups (group_publication_year.json)')
    _put(sum(c for y, c in _d['by_year'].items() if int(y) >= 2002), 'sum of the year groups 2002-2026')
    _put(_d['up_to_2017'], 'year groups up to 2017'); _put(_d['from_2018'], 'year groups 2018-2026')
    for _lab in ('domains', 'fields_top6', 'sdg', 'countries_top25', 'types'):
        for _name, _c in _d[_lab]:
            if _c >= 100:
                _put(_c, f'{_lab}: {_name}')
    _put(_d['fields_rest'][1], f"{_d['fields_rest'][0]} further fields")
    _put(sum(c for _, c in _d['fields_top6']) + _d['fields_rest'][1], 'sum of the field groups')
    _put(_d['countries_n'], 'number of countries (authorships.countries groups)')
    for _row in _d['top10']:
        _put(_row[2], f'{_row[0]}: cited_by_count at 18 Oct 2026 (Evaluation coding)')
        _put(_row[3], f'{_row[0]}: cited_by_count at 10 Nov 2026 (corpus_works.json)')
    _put(_d['saito2015'], 'saito2015precision cited_by_count (extra_works.json)')
    OVERRIDES['5000'] = (_snap, 'citing works per year: 2025 = 5,059; 2026 = 5,195 (more than 5,000)', 'ok', _note)
    OVERRIDES['34000'] = ('data/openalex/2026-11-10/citing_count.json', 'meta.count = 34,416 (more than 34,000)', 'ok', _note)
    for _k, (_f, _fld) in {'34938': ('smote_work.json', 'cited_by_count (work entity endpoint)'),
                           '34720': ('corpus_works.json', 'cited_by_count of W2148143831 (list endpoint)'),
                           '34416': ('citing_count.json', 'meta.count, filter=cites:W2148143831'),
                           '34366': ('citing_with_topic.json', 'meta.count, citing works with a primary topic'),
                           '11.6': ('derived.json', '3,994 / 34,416'), '88.4': ('derived.json', '30,414 / 34,416'),
                           '49.3': ('derived.json', '16,927 / 34,366'), '50.7': ('derived.json', '1 - 16,927 / 34,366')}.items():
        OVERRIDES[_k] = ('data/openalex/2026-11-10/' + _f, _fld, 'ok', _note)

CHANGED = {  # (file, value) changed on purpose in v0.2; the section PDF still prints the old value
    ('09-guidance.tex', '23'): ('gen/table_methods_rows.tex', 'rows with a value in the last column', 'ok',
                               'Method PDF prints 26 (WP1 step 6: 24); v0.64: 23, KNNOR marked avg. (scripts/apply_method_decisions.py)'),
    ('09-guidance.tex', '17'): ('gen/table_methods_rows.tex', '|value| <= 0.03 in the last column', 'ok',
                               'Method PDF prints 19 (WP1 step 6: 18); v0.64: 17, KNNOR marked avg.'),
}
# v0.5: numbers of the independent benchmark (WP6). An entry applies to S blocks only, and only on a line that holds its
# marker, so the same value elsewhere in a file keeps its own source. Sources are in benchmark/ (results_summary/ holds the
# result summaries copied from the MacBook run of 10 and 11 Nov 2026; scripts/bench_derived.py writes the derived files).
_RS = 'benchmark/results_summary/'
_C, _T, _N = _RS + 'core/smote_vs_none.csv', _RS + 'core/tests_vs_smote.csv', _RS + 'nested/tests_vs_smote.csv'
_S, _K, _E = _RS + 'core/cell_status.csv', _RS + 'core/config.json', _RS + 'environment.txt'
_H, _P, _F = _RS + 'highdim/smote_vs_none.csv', _RS + 'nested/pool.json', _RS + 'families.json'
_HS, _KN = _RS + 'highdim/highdim_selection.json', _RS + 'nested/config.json'
_note = 'benchmark run on the MacBook, 10 and 11 Nov 2026'
BENCH = {}
for _f, _marker, _vals, _src, _fld in (
        ('03-method.tex', 'Its core tier compares', ('110',), _K, 'datasets (count)'),
        ('03-method.tex', 'Its core tier compares', ('36',), _F, 'core.families'),
        ('03-method.tex', 'Its core tier compares', ('5',), _K, 'folds = 5, repeats = 5'),
        ('06-evaluation.tex', 'SMOTE against no resampling, by measure', ('106', '636'), _C, 'datasets, pairs'),
        ('06-evaluation.tex', 'Stacked horizontal bars', ('636',), _C, 'pairs'),
        ('06-evaluation.tex', 'Stacked horizontal bars', ('84', '62', '50', '34', '23'), _C, 'pct_smote_better, rounded'),
        ('06-evaluation.tex', 'Our benchmark shows the size of the effect',
         ('531', '636', '83.5', '0.056', '61.8', '49.7', '0.000', '34.3', '470'), _C, 'smote_better, pairs, pct_smote_better, median_diff, none_better'),
        ('07-evidence.tex', 'Our own benchmark points the same way', ('83.5', '49.7', '34.3'), _C, 'pct_smote_better'),
        ('07-evidence.tex', 'Our own benchmark points the same way', ('34',), _T, 'n_families, RF and GB against SMOTE'),
        ('07-evidence.tex', 'Our own benchmark points the same way', ('0.006',), _T, 'median_diff_vs_smote, none, PR-AUC, RF'),
        ('07-evidence.tex', 'Our own benchmark points the same way', ('0.039', '0.040'), _T, 'median_diff_vs_smote, threshold, G-mean, RF and GB'),
        ('07-evidence.tex', 'Oversampling raises recall and G-mean', ('83.5',), _C, 'pct_smote_better, G-mean'),
        ('07-evidence.tex', 'It improves ranking', ('49.7', '34.3'), _C, 'pct_smote_better, ROC-AUC and PR-AUC'),
        ('07-evidence.tex', 'It yields usable probabilities', ('470', '636'), _C, 'none_better and pairs, Brier score'),
        ('07-evidence.tex', 'High dimension is the setting', ('24', '30', '9'), _H, 'smote_better (G-mean, PR-AUC), pairs'),
        ('07-evidence.tex', 'It works in high dimension', ('24', '30', '9'), _H, 'smote_better (G-mean, PR-AUC), pairs'),
        ('10-closing.tex', 'The benchmark has limits of its own', ('110',), _K, 'datasets (count)'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('110',), _K, 'datasets (count)'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('36',), _F, 'core.families'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('14',), _K + ' and ' + _E, 'methods (14); jobs: 14'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('3',), 'benchmark/run.py', 'inner 3-fold cross-validation of the threshold'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('5',), 'benchmark/run.py and ' + _K, 'k-NN n_neighbors = 5; folds = 5, repeats = 5'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('200',), 'benchmark/run.py', 'random forest n_estimators = 200'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('20261110',), _K, 'seed'),
        ('11-appendix.tex', 'The benchmark follows the protocol of Section', ('0.14', '1.0', '26.5', '3.13', '1.9', '15', '24', '2', '1'), _E,
         'machine and package versions (imbalanced-learn 0.14.2, smote-variants 1.0.1, macOS 26.5.2, Python 3.13, scikit-learn 1.9.1)'),
        ('11-appendix.tex', 'Fold results are averaged per dataset', ('0.01',), 'benchmark/stats.py', 'rope=0.01 of the Bayesian signed-rank test'),
        ('11-appendix.tex', 'Fold results are averaged per dataset', ('10', '25'), _RS + 'core/per_dataset_means.csv', 'n_folds of SMOTE on ecoli_0_1_3_7_vs_2_6 (15 of 25)'),
        ('11-appendix.tex', 'Fold results are averaged per dataset', ('34',), _F, 'core.families_with_smote'),
        ('11-appendix.tex', 'Fold results are averaged per dataset', ('231000', '225112', '3138', '660', '1152', '6', '2750'), _S, 'cells by method and status'),
        ('11-appendix.tex', 'Core tier of the benchmark: median difference', ('34',), _T, 'n_families'),
        ('11-appendix.tex', 'Core tier of the benchmark: median difference', ('0.05',), 'benchmark/stats.py', 'Holm-adjusted p below 0.05 marked'),
        ('11-appendix.tex', 'Core tier of the benchmark: median difference', ('0.000',), _T, 'median_diff_vs_smote of ADASYN and Safe-Level-SMOTE, ROC-AUC, RF'),
        ('11-appendix.tex', 'In the high-dimensional tier, the same protocol', ('100', '0.20', '20000'), _HS, 'rule'),
        ('11-appendix.tex', 'In the high-dimensional tier, the same protocol', ('24', '30', '18', '9', '20'), _H, 'smote_better (G-mean, ROC-AUC, PR-AUC), pairs, none_better (Brier score)'),
        ('11-appendix.tex', 'In the nested tier, to test whether', ('30', '59', '20261111'), _P, 'drawn_size, pool_size, seed; rule: at least 30 minority examples'),
        ('11-appendix.tex', 'In the nested tier, to test whether', ('21',), _F, 'nested.families'),
        ('11-appendix.tex', 'In the nested tier, to test whether', ('25200', '24578'), _RS + 'nested/cell_status.csv', 'cells, all and ok'),
        ('11-appendix.tex', 'In the high-dimensional tier, the same protocol', ('10500', '10351'), _RS + 'highdim/cell_status.csv', 'cells, all and ok'),
        ('11-appendix.tex', 'In the nested tier, to test whether', ('3', '5'), _KN + ' and benchmark/run_ext.py', 'inner 3-fold; folds = 5, repeats = 3'),
        ('11-appendix.tex', 'In the nested tier, to test whether', ('0.012', '0.009'), _N, 'median_diff_vs_smote, PR-AUC, RF: none and G-SMOTE'),
        ('11-appendix.tex', 'Nested tier of the benchmark: median difference', ('20', '21'), _N, 'n_families, RF and GB'),
        ('12-checklist.tex', 'Experiments, item 10.', ('5',), _K + ' and ' + _KN, 'folds = 5, repeats = 5 (3 nested)'),
        ('12-checklist.tex', 'Experiments, item 14.', ('3',), _KN + ' and benchmark/run_ext.py', 'grid of three values; inner 3-fold')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld))


# v0.6: other S numbers with a source of their own (an entry may carry its own note)
for _f, _marker, _vals, _src, _fld, _nt in (
        ('12-checklist.tex', 'CC BY 4.0 license', ('4.0',), 'claude/smote25-fix-plan-handoff.md', 'license decided 11 Nov 2026 (D20)', 'decision of the team lead'),
        ('main.tex', 'Integrated draft v0.', ('19', '13', '2026'), 'main.tex', 'draft version and date', 'title note'),
        ('main.tex', 'ORCID 0000-0003-0965-680X', ('0000', '0003', '0965'), 'the team lead, 11 Nov 2026 (ORCID in his dblp record; checksum valid)', 'corresponding author ORCID', 'author details')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))


# v0.8: run times of the identification stage (search logs, UTC) and the competitor counts of Section 6.4
_SL = 'data/search/2026-11-11/'
_DS = 'Data section/out/'
for _f, _marker, _vals, _src, _fld, _nt in (
        ('03-method.tex', 'The identification stage was run on', ('10', '2026'),
         _SL + 'scopus_search_log.json, openalex_search_log.json, arxiv_search_log.json', 'searched_utc, run_utc: 2026-11-10', 'run date of the three searches (UTC)'),
        ('03-method.tex', 'The identification stage was run on', ('2002',), _SL + 'scopus_search_log.json', 'query: PUBYEAR > 2001', 'publication years searched'),
        ('03-method.tex', 'The identification stage was run on', ('16', '44'), _SL + 'scopus_search_log.json', 'searched_utc 2026-11-10T16:44:00Z', 'Scopus search time'),
        ('03-method.tex', 'The identification stage was run on', ('17',), _SL + 'openalex_search_log.json, arxiv_search_log.json', 'run_utc 17:08:47 (OpenAlex), 17:03:14 (arXiv)', 'search times'),
        ('03-method.tex', 'The identification stage was run on', ('08',), _SL + 'openalex_search_log.json', 'run_utc 2026-11-10T17:08:47', 'OpenAlex run time'),
        ('03-method.tex', 'The identification stage was run on', ('03',), _SL + 'arxiv_search_log.json', 'run_utc 2026-11-10T17:03:14Z', 'arXiv run time'),
        ('06-evaluation.tex', 'It is a competitor in', ('7', '23'), _DS + 'baseline_provenance_papers.csv', 'papers (57) by year: before 2010, 2021 on', 'SMOTE as a competitor'),
        ('06-evaluation.tex', 'It is a competitor in', ('15', '25'), _DS + 'dataset_records.csv', 'distinct paper_id (73) by year: before 2010, 2021 on', 'papers with an evaluation on data'),
        ('06-evaluation.tex', 'It is a competitor in', ('2010', '2021'), _DS + 'baseline_provenance_papers.csv', 'year bands of the evaluation audit', 'period limits'),
        ('11-appendix.tex', 'Section~S1 of the online appendix gives', ('37',), 'gen/table_methods_rows.tex', 'rows (37 methods)', 'online appendix S1'),
        ('11-appendix.tex', 'Section~S1 of the online appendix gives', ('10', '2026'), 'scripts/apply_method_decisions.py and docs/smote25-decision-sheet-v0.3.md', 'decisions of 10 Nov 2026 (A1 to A4)', 'decision date'),
        ('11-appendix.tex', 'Section~S1 of the online appendix gives', ('11',), 'docs/CHANGES-v0.4.md', 'SMOM: journal version recoded blind (A7)', 'date of the SMOM check')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.10: the harm search (Section 8.5, Table 16) and corpus counts that Section 8 repeats from the Evaluation section
_HSUM = 'wp5/harm_search/work/summary.json'
_EV = 'SMOTE25_Evaluation_Section.pdf (text in src/eval.txt)'
for _f, _marker, _vals, _src, _fld, _nt in (
        ('08-society.tex', 'Four harms are documented. To find', ('10', '2026'), 'wp5/harm_search_log.json', 'date_utc 2026-11-10T13:26:39+00:00 (H1 to H4)', 'harm search date'),
        ('08-society.tex', 'Harm: overestimated risk', ('9', '14'), _HSUM, 'includes_by_finding.H-calibration.harm = 9; includes_by_harm.H-calibration = 14', 'harm search, AI first pass'),
        ('08-society.tex', 'Harm: inflated published results through leakage', ('8',), _HSUM, 'includes_by_harm.H-leakage = 8, all with finding harm', 'harm search, AI first pass'),
        ('08-society.tex', 'direct checks in 6 of 71 studies', ('6', '71'), _EV, 'Section 7.7: Only 6 of the 71 studies (8%) examine the resampled data directly', 'corpus count (E 7.7), as Section 6 prints'),
        ('08-society.tex', 'only 6 of 71 studies use one', ('6', '71'), _EV, 'Section 7.7: Only 6 of the 71 studies (8%) examine the resampled data directly', 'corpus count (E 7.7), as Section 6 prints'),
        ('08-society.tex', '39 of the 71 studies of our corpus', ('39', '71'), _EV, 'reasons for the choice of measures: accuracy misleads under imbalance (39) of 71', 'corpus count (E), as Section 6 prints'),
        ('08-society.tex', '39 of 71 studies cite its failure', ('39', '71'), _EV, 'reasons for the choice of measures: accuracy misleads under imbalance (39) of 71', 'corpus count (E), as Section 6 prints'),
        ('09-guidance.tex', 'The rerun on the reference collection of Appendix', ('0.0025',), 'benchmark/rerun42/methods/cgmos/NOTES.md', 'section 1: total-variation distance at most 0.0025 (five data sets, four readings)', 'CGMOS validation')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.10: dates, years and counts of the reach paragraphs (Sections 1 and 8), checked against the OpenAlex snapshot
# data/openalex/2026-11-10 (README.md: requests 10 Nov 2026, 15:52 to 15:53 UTC) or against the reference the sentence cites
_OA = 'data/openalex/2026-11-10/'
for _f, _marker, _vals, _src, _fld, _nt in (
        ('01-intro.tex', 'Since the 15-year review, the scale of SMOTE', ('15',), 'refs.bib: fernandez2018smote', 'title: Marking the 15-Year Anniversary', 'the 15-year review'),
        ('01-intro.tex', 'Since the 15-year review, the scale of SMOTE', ('10', '2026'), _OA + 'README.md', 'snapshot of 10 Nov 2026', 'snapshot date'),
        ('01-intro.tex', 'Since the 15-year review, the scale of SMOTE', ('2025',), _OA + 'group_publication_year.json', 'key 2025: count 5,059', 'citing works in 2025'),
        ('01-intro.tex', 'Since the 15-year review, the scale of SMOTE', ('2018',), 'refs.bib: fernandez2018smote', 'year 2018', 'year of the 15-year review'),
        ('01-intro.tex', 'Since the 15-year review, the scale of SMOTE', ('85', '104'), 'refs.bib: kovacs2019empirical', '85 oversamplers on 104 datasets (the cited benchmark)', 'cited benchmark'),
        ('01-intro.tex', 'published since 2018 on whether and when', ('2018',), 'refs.bib: fernandez2018smote', 'year 2018', 'year of the 15-year review'),
        ('08-society.tex', 'Scholarly reach of SMOTE in OpenAlex', ('10', '2026', '11'), _OA + 'README.md', 'snapshot of 10 Nov 2026 (folder 2026-11-10)', 'snapshot date'),
        ('08-society.tex', 'Scholarly reach of SMOTE in OpenAlex', ('2002',), 'refs.bib: chawla2002smote; ' + _OA + 'group_publication_year.json', 'year 2002; 6 citing works dated before 2002', 'year of the SMOTE paper'),
        ('08-society.tex', 'Scholarly reach of SMOTE in OpenAlex', ('20',), _OA + 'group_primary_topic_field_id.json', '26 fields: the six largest and 20 others', 'fields'),
        ('08-society.tex', 'Works citing the SMOTE paper in OpenAlex (queried', ('10', '2026'), _OA + 'README.md', 'snapshot of 10 Nov 2026', 'snapshot date'),
        ('08-society.tex', 'Year of publication & up to 2017', ('2017', '2018', '2025', '2026'), _OA + 'group_publication_year.json', 'to 2017: 3,994; 2018 to 2026: 30,414; 2025: 5,059; 2026: 5,195', 'year bands'),
        ('08-society.tex', 'Field of primary topic & Computer Science', ('20',), _OA + 'group_primary_topic_field_id.json', '26 fields: six named and 20 further', 'fields'),
        ('08-society.tex', 'The reach of SMOTE is wide and still growing', ('2002',), 'refs.bib: chawla2002smote', 'year 2002', 'year of the SMOTE paper'),
        ('08-society.tex', 'The reach of SMOTE is wide and still growing', ('10', '2026'), _OA + 'README.md', 'snapshot of 10 Nov 2026', 'snapshot date'),
        ('08-society.tex', 'The reach of SMOTE is wide and still growing', ('2018', '15'), 'refs.bib: fernandez2018smote; ' + _OA + 'group_publication_year.json', '15-year review of 2018; 2018 to 2026: 30,414', 'year band'),
        ('08-society.tex', 'The reach of SMOTE is wide and still growing', ('25',), _OA + 'group_authorships_countries.json', '159 countries; the 25 with the most citing works', 'country ranking'),
        ('08-society.tex', 'Part of this reach coincides with the availability', ('30', '9', '2026', '10'), 'pypistats.org, as the sentence cites it (accessed 10 Nov 2026)', 'downloads in the 30 days to 9 Nov 2026', 'external source named in the text'),
        ('08-society.tex', 'Part of this reach coincides with the availability', ('85',), 'refs.bib: kovacs2019smotevariants', 'title: A Python Implementation of 85 Minority Oversampling Techniques', 'cited software paper'),
        ('08-society.tex', 'The honest summary is that the benefit', ('2002',), 'refs.bib: chawla2002smote', 'year 2002', 'year of the SMOTE paper'),
        ('08-society.tex', 'item 13 of TRIPOD+AI', ('13',), 'refs.bib: collins2024tripodai', 'TRIPOD+AI checklist item 13, Class imbalance (checked against copies of the checklist, 11 Nov 2026)', 'cited guideline'),
        ('08-society.tex', 'YL{2.3cm}', ('2',), 'sec/08-society.tex', 'LaTeX column width 2.3cm', 'not a number of the text')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.20: the data-availability statement (Declarations): the DOI reserved on the Zenodo draft on 14 Nov 2026
# (deposit/zenodo_draft_checked_2026-11-14.json, read back from Zenodo), the license decided on 11 Nov 2026, and the
# number of the online appendix's section on the deposit (supplement/supplement.aux, label supp:deposit)
for _f, _marker, _vals, _src, _fld, _nt in (
        ('10-closing.tex', 'Data and code availability.} The data and code', ('10.5281', '24212321'), 'deposit/zenodo_draft_checked_2026-11-14.json', 'metadata.prereserve_doi: 10.5281/zenodo.24212321 (draft record 24212321)', 'reserved Zenodo DOI'),
        ('10-closing.tex', 'Data and code availability.} The data and code', ('4.0',), 'claude/smote25-decisions-2026-11-10.md', 'license decided 11 Nov 2026: CC BY 4.0 for data, MIT for code', 'license version'),
        ('10-closing.tex', 'Data and code availability.} The data and code', ('4', '4.4'), 'supplement/supplement.aux', 'newlabel supp:deposit: S4.4', 'section number of the online appendix')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.20: the model names of the AI sessions (Claude Opus 5.5, Claude Fable 5.2), sourced from the records of the work
# they did, not from a chance match in a section PDF
_SCR = 'data/search/screening_full_2026-11-11/README.md'
for _f, _marker, _vals, _src, _fld, _nt in (
        ('03-method.tex', 'Claude Opus 5.5', ('5.5',), _SCR, 'line 40: Separate AI sessions (Claude Opus 5.5 subagents ...); wp3/adjudication/README.md line 4', 'model of the AI sessions'),
        ('03-method.tex', 'Claude Fable 5.2', ('5.2',), _SCR, 'line 9: independent AI check by another model (Claude Fable 5.2; report v3)', 'model of the independent check'),
        ('10-closing.tex', 'Claude Opus 5.5', ('5.5',), _SCR, 'line 40: Separate AI sessions (Claude Opus 5.5 subagents ...)', 'model of the AI sessions'),
        ('10-closing.tex', 'Claude Fable 5.2', ('5.2',), _SCR, 'line 9: independent AI check by another model (Claude Fable 5.2; report v3)', 'model of the independent check')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.21 (M4): the numbers of the new sentences of Sections 7.1 and 7.5, from the sources checked on 14 Nov 2026
for _f, _marker, _vals, _src, _fld, _nt in (
        ('07-evidence.tex', 'A benchmark posted as a preprint in 2026', ('2026', '40', '57'), 'refcheck/m4_v021_sources.json', 'liu2026tilbench: arXiv:2605.14915 (posted 14 May 2026; abstract: more than 40 methods, 57 tabular datasets)', 'TILBench'),
        ('07-evidence.tex', 'TabPFN-2.5', ('2.5',), 'refcheck/m4_v021_sources.json', 'mcdowell2026correcting: arXiv:2605.21742, Section I (TabPFN-2.5)', 'model version')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.10: the OpenAlex appendix and Section 3.5 (snapshot README, urls.tsv, smote_work.json), the survey's own counts
# in Table 2, and numbers that are not numbers of the text (file names, column widths)
_DMEP = 'data-section-jair.pdf (1,756 entries, 76 papers), method-section-draft-preview.pdf (37 methods), SMOTE25_Evaluation_Section.pdf (71 studies)'
for _f, _marker, _vals, _src, _fld, _nt in (
        ('11-appendix.tex', 'come from the public OpenAlex API', ('10', '2026', '15', '52', '53'), _OA + 'README.md and urls.tsv', 'requests 2026-11-10 15:52:35 to 15:52:44 UTC (README: 15:52 to 15:53)', 'snapshot date and time'),
        ('11-appendix.tex', 'come from the public OpenAlex API', ('10.1613', '953'), _OA + 'smote_work.json', 'doi https://doi.org/10.1613/jair.953', 'DOI of the SMOTE paper'),
        ('11-appendix.tex', 'come from the public OpenAlex API', ('2002',), _OA + 'group_publication_year.json', '6 citing works dated before 2002', 'year of the SMOTE paper'),
        ('03-method.tex', 'we queried the OpenAlex API on 10 November 2026', ('10', '2026'), _OA + 'README.md', 'snapshot of 10 Nov 2026', 'snapshot date'),
        ('11-appendix.tex', '\\input{sec/12-checklist}', ('12',), 'main file layout', 'file name sec/12-checklist.tex', 'not a number of the text'),
        ('main.tex', '\\input{sec/09-guidance}', ('09',), 'main file layout', 'file name sec/09-guidance.tex', 'not a number of the text'),
        ('02-background.tex', 'YL{3.4cm}', ('2', '3'), 'sec/02-background.tex', 'LaTeX column widths 2.6cm and 3.4cm', 'not a number of the text'),
        ('02-background.tex', 'This survey & 76 papers, 37 SMOTE-family methods', ('76', '37', '1756', '71'), _DMEP, 'corpus counts, as the three section drafts print them', "the survey's own counts")):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.17: the M7 claims checked against their sources (D39; docs/M7-CLAIMS-CHECK-v0.17.md)
for _f, _marker, _vals, _src, _fld, _nt in (
        ('07-evidence.tex', 'the mean AUC of the best oversampler exceeds that of SMOTE', ('0.003', '0.009'),
         'refs.bib: kovacs2019empirical, Table 3 (journal PDF, p. 8)',
         'best oversampler minus SMOTE in mean AUC: MLP .9182-.9156, kNN .9153-.9082, DT .8885-.8809, SVM .9089-.8999',
         'cited benchmark'),
        ('08-society.tex', 'give two attacks that need only the released dataset', ('0.85', '20'),
         'refs.bib: ganev2026smote (arXiv:2510.15083v3, the ICLR 2026 version, read 12 Nov 2026)',
         'ReconSMOTE: average recall 0.85, reaching 1 for imbalance ratios of 20 or higher', 'cited study')):
    for _v in _vals:
        BENCH.setdefault((_f, _v), []).append((_marker, _src, _fld, _nt))

# v0.7: numbers of the screen, the coverage sample and the use audit, rendered from templates by
# scripts/render_search_text.py, which lists each with its paragraph marker and source key in scripts/search_bench.json
_SB = ROOT / 'scripts/search_bench.json'
if _SB.exists():
    for _e in _json.load(open(_SB, encoding="utf-8")):
        BENCH.setdefault((_e['file'], _e['value']), []).append(
            (_e['marker'], _e['source'], 'key ' + _e['key'], 'rendered from scripts/search_templates by scripts/render_search_text.py'))


def bench_source(fname, tok, line):
    for entry in BENCH.get((fname, tok), []):
        marker, src, fld = entry[:3]
        if marker in line:
            return src, fld, 'ok', (entry[3] if len(entry) > 3 else _note)
    return None
# v0.16: numbers changed on purpose by the WP3 adjudication and decisions D34 to D36 (D35 recomputation, GLOS recode);
# one entry per paragraph or table row, matched by a marker on the same line, whatever the tag of the block
ADJ = {}
for _e in _json.load(open(ROOT / 'scripts/adjudicated_numbers.json', encoding='utf-8')):
    for _v in _e['values']:
        ADJ.setdefault((_e['file'], _v), []).append(_e)


def adj_source(fname, tok, line):
    for e in ADJ.get((fname, tok), []):
        if e['marker'] in line:
            return e['source'], e['field'], 'ok', e['note']
    return None


STALE = set()  # Section 6.9: the same ten studies lead in the 10 Nov 2026 snapshot (derived.json)


def section_at(lines, i):
    for j in range(i, -1, -1):
        m = re.match(r'\\(sub)?section\*?\{([^}]*)\}', lines[j])
        if m:
            return m.group(2)
    return ''


def main():
    rows, n = [], 0
    files = [ROOT / 'main.tex'] + sorted((ROOT / 'sec').glob('*.tex'))
    for f in files:
        lines = f.read_text(encoding='utf-8').splitlines()
        tag, ref, in_denoms = 'S', '', False
        for i, line in enumerate(lines):
            if line.lstrip().startswith('%'):
                continue
            gen = re.search(r'\\input\{(gen/[^}]+)\}', line)
            if gen:
                gl = (ROOT / (gen.group(1) + '.tex')).read_text(encoding='utf-8').splitlines()
                for k, g in enumerate(gl):
                    if g.startswith('%'):
                        continue
                    for tok in re.findall(r'(?<![A-Za-z0-9_])[-+]?\.?\d[\d,]*(?:\.\d+)?', re.sub(r'\\cite[pt]?\{[^}]*\}', ' ', g)):
                        n += 1
                        rows.append(dict(id=f'L{n:04d}', value_in_text=tok, where=f'{gen.group(1)}.tex:{k + 1} ({section_at(lines, i)})',
                                         tag='generated', source_file=f'{gen.group(1)} (generated by script)', source_field_or_query='see header of the generated file',
                                         status='ok', note='regenerate, do not edit', context=g[:90]))
                continue
            if '\\label{tab:denominators}' in line:
                in_denoms = True
            if in_denoms and '\\end{table}' in line:
                in_denoms = False
            parts = TAG.split(line)
            segs = [(tag, ref, parts[0])]
            for k in range(1, len(parts), 3):
                segs.append((parts[k], parts[k + 1], parts[k + 2]))
            for t, r, text in segs:
                tag, ref = t, r
                shown = t
                if t == 'A':   # v0.18: approved in the final pass; the reference holds the earlier tag (S or R)
                    t, r, shown = (r if r in ('S', 'R') else 'S'), '', 'A/' + (r if r in ('S', 'R') else 'S')
                clean = text
                for pat, rep in STRIP:
                    clean = pat.sub(rep, clean)
                clean = clean.replace('\\%', '%').replace('$-$', '-')
                for m in NUM.finditer(clean):
                    raw = m.group(0)
                    if not re.search(r'\d', raw):
                        continue
                    tok = raw.lstrip('+-').replace(',', '')
                    if t in ('D', 'M', 'E') or True:
                        n += 1
                        src, fld, st, note = '', '', 'open', ''
                        key = (f.name, tok)
                        if adj_source(f.name, tok, line):   # v0.16: adjudicated or recomputed on purpose
                            src, fld, st, note = adj_source(f.name, tok, line)
                        elif in_denoms and not (tok in OVERRIDES and t in ('S', 'R')):   # v0.6: OpenAlex counts in Table 4
                            # v0.4: rows decided on 10 Nov 2026 (decision form items 13 to 22) or explained by definitions are ok;
                            # a row whose status cell says Open stays a conflict until it is decided
                            if '& Open:' in line:
                                src, fld, st, note = 'Table 4', 'reconcile/table4_reconciliation.md', 'conflict', 'open row (WP1 step 3)'
                            else:
                                src, fld, st, note = 'Table 4', 'claude/smote25-decisions-2026-11-10.md', 'ok', 'row decided or explained (decision form, 10 Nov 2026)'
                        elif t in ('S', 'R') and bench_source(f.name, tok, line):   # v0.10: R numbers with a registered source
                            src, fld, st, note = bench_source(f.name, tok, line)
                        elif key in CHANGED:
                            src, fld, st, note = CHANGED[key]
                        elif tok in OVERRIDES and t in ('S', 'R'):
                            src, fld, st, note = OVERRIDES[tok]
                        elif t in PDF:
                            ok = found(tok, TXT[t])
                            src, st = PDF[t], ('ok' if ok else 'conflict')
                            fld = f'section {r}' if r else ''
                            note = '' if ok else 'not found in the attributed PDF; read the sentence'
                            if (f.name, tok) in STALE and 'OpenAlex' in line:
                                st, note = 'stale', 'OpenAlex 18 Oct 2026; re-pull on one date'
                        elif t == 'S':
                            hit = [k for k in ('D', 'M', 'E') if found(tok, TXT[k])]
                            src, st = (', '.join(PDF[k] for k in hit), 'ok') if hit else ('', 'open')
                            note = 'synthesis; number occurs in the section PDF(s) named' if hit else 'synthesis; no source found by script'
                        elif t in ('R', 'P'):
                            st, note = 'open', 'external or project source; give the citation or the file'
                        rows.append(dict(id=f'L{n:04d}', value_in_text=raw, where=f'{f.name}:{i + 1} ({section_at(lines, i)[:40]})',
                                         tag=shown, source_file=src, source_field_or_query=fld, status=st, note=note,
                                         context=re.sub(r'\s+', ' ', clean[max(0, m.start() - 45):m.end() + 45]).strip()))
    with OUT.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    c = Counter(r['status'] for r in rows)
    print(f'{len(rows)} numbers; ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items())))
    print('by tag:', dict(Counter((r['tag'], r['status']) for r in rows)))


if __name__ == '__main__':
    main()
