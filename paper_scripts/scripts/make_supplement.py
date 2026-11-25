#!/usr/bin/env python3
"""v0.8: generate the parts of the online appendix (supplement/) from the team repository and the archived data.

Writes supplement/gen/: accounts.tex (S1), studies.tex (S2), reference_tasks.tex (S3), search.tex (S4),
codebooks.tex (S5) and numbers.tex (the counts the hand-written prose of supplement/supplement.tex prints).
Nothing is retyped. Each input is transformed by the rules below, and the script stops (STOP:) when a check fails.

S1 accounts, from Method section/manuscript/generated/smote-family-methods.tex (written by make_tex.py, 28 Oct 2026):
   \\parencite and \\pcite become \\citep; "Steps changed" becomes "Decisions changed"; British spellings become
   American (SPELL); the link (Core or Partial) of each method is added from the paper's Table 6
   (gen/table_methods_rows.tex); each provisional note (\\pnote) is replaced by the decision taken since
   (DECIDED). Checks: 37 accounts; class category, year and decisions changed equal those of Table 6.
S2 studies, from Evaluation section/latex/tables/empirical-studies.tex (version 4.1, 8 Nov 2026): \\parencite becomes
   \\citep; the legend's reference to the Evaluation draft's standard table points to the paper's Table
   (tab:standard). Checks: 71 rows; every key in refs.bib or supplement/supp_refs.bib; the summary of the Std.
   column printed in Section 6 of the paper (median 3; 3 before 2010, 4 since 2021; one study meets all seven;
   39 meet three or fewer).
S3 reference tasks, the table tab:data-reference of Data section/manuscript/data-section-final.tex (written by
   difficulty/reference_collection.py). Checks: 42 rows; the ranges that Appendix C of the paper prints.
S4 search, from data/search/2026-11-11/*_search_log.json, wp4_records_merged_summary.json and the OpenAlex
   snapshot data/openalex/2026-11-10/ (README.md table of files, urls.tsv).
S5 codebooks and session instructions, from data/search/screening_full_2026-11-11/ (Markdown, converted by pandoc).
S6 harm search (v0.10), from wp5/harm_search_log.json (queries), wp5/harm_search/work/summary.json (counts) and
   wp5/harm_search/harm_search_records.csv (the included studies: identifiers, harm, comparison, finding; never the
   abstracts, the quotes or the screeners' reasons). Checks: the counts of the table equal those of summary.json.
S7 rerun on the reference collection (v0.10), from benchmark/rerun42/methods/README.md (the validation table of the
   five re-implementations, parsed, not retyped) and benchmark/results_summary/rerun42/ (stats42.py: summary.json,
   cell_status.csv, tests_vs_smote.csv).
   v0.29: the TabPFN arm of the rerun (tabpfn.tex), from benchmark/results_summary/rerun42/tabpfn/ (stats42_tabpfn.py:
   summary.json, tabpfn_comparisons.csv; tabpfn_cells42.py: cells.json).
Final check on every generated file: no em-dash, no British spelling from WATCH.
Usage: python3 scripts/make_supplement.py <team-repo-root> <draft-dir>
"""
import csv
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

REPO, DRAFT = Path(sys.argv[1]), Path(sys.argv[2])
OUT = DRAFT / 'supplement' / 'gen'
NUMS = {}

SPELL = {'neighbours': 'neighbors', 'neighbour': 'neighbor', 'neighbourhood': 'neighborhood', 'centre': 'center',
         'relabelled': 'relabeled', 'labelled': 'labeled', 'regularised': 'regularized', 'penalises': 'penalizes',
         'optimised': 'optimized', 'favours': 'favors', 'favouring': 'favoring', 'binarised': 'binarized',
         'towards': 'toward'}
WATCH = ['neighbour', 'favour', 'behaviour', 'colour', 'centre', 'modelling', 'modelled', 'labelled', 'optimis',
         'normalis', 'regularis', 'binaris', 'randomis', 'generalis', 'summaris', 'minimis', 'maximis', 'organis',
         'recognis', 'utilis', 'characteris', 'prioritis', 'penalis', 'analyse', 'whilst', 'amongst', 'towards']
STEP = {'Seed selection': 'S', 'Sample allocation': 'A', 'Neighbour choice': 'N', 'Placement rule': 'P',
        'Post-filtering': 'F', 'Inside a pipeline': 'L'}
CAT = {'Binary only': 'B', 'Multiclass only': 'M', 'Binary + Multiclass': 'B+M'}
HEAD = {'Binary only': 'Binary Only', 'Multiclass only': 'Multiclass Only', 'Binary + Multiclass': 'Binary + Multiclass'}
# The provisional notes of the accounts and the decisions taken since (decision form of 10 Nov 2026, items 24 and 25,
# decision sheet v0.3 items A1 to A4; SMOM: blind recoding of the journal version, v0.4, see sec/11 of the paper).
DECIDED = {
    'Loyalty-SMOTE': 'Decided by the authors: Binary only, because only the smallest class is '
                     'ever oversampled and the results are scored with binary measures.',
    'SMOM': 'The journal version confirms the class category '
            '(Multiclass only), the link (Core) and the one decision changed, the partner (neighbor choice); its '
            'per-dataset scores are printed in the supplement only.',
    'GLOS': 'Decided by the authors: Multiclass only; the two-class Sonar run is a '
            'parameter-tuning run and is not counted.',
    'NROMM': 'Decided by the authors: Core, although the trapped seeds are placed without '
             'interpolation.',
    'OREM, OREM-M': 'Decided by the authors: one entry, Binary + Multiclass, for OREM, OREM-M '
                    'and OREMBoost.',
}


def stop(msg):
    sys.exit('STOP: ' + msg)


def american(s):
    def rep(m):
        w = m.group(0)
        a = SPELL[w.lower()]
        return a[0].upper() + a[1:] if w[0].isupper() else a
    return re.sub(r'\b(' + '|'.join(sorted(SPELL, key=len, reverse=True)) + r')\b', rep, s, flags=re.I)


def macro_args(s, name):
    """Yield (start, end, argument) for every \\name{...} with balanced braces."""
    for m in re.finditer(r'\\' + name + r'\{', s):
        depth, i = 1, m.end()
        while depth:
            if i >= len(s):
                stop(f'unbalanced \\{name}')
            depth += {'{': 1, '}': -1}.get(s[i], 0) if s[i - 1] != '\\' else 0
            i += 1
        yield m.start(), i, s[m.end():i - 1]


def table6():
    rows = {}
    for line in (DRAFT / 'gen' / 'table_methods_rows.tex').read_text(encoding='utf-8').splitlines():
        if '\\citep' not in line:
            continue
        c = [x.strip() for x in line.rstrip().rstrip('\\').split('&')]
        rows[c[0].split(' \\citep')[0]] = dict(year=c[1], cat=c[2], link=c[3],
                                              dec=''.join(sorted(l for l, x in zip('SANPFL', c[4:10]) if 'bullet' in x)))
    return rows


def accounts():
    src = (REPO / 'Method section/manuscript/generated/smote-family-methods.tex').read_text(encoding='utf-8')
    t6 = table6()
    body = '\n'.join(l for l in src.splitlines() if not l.startswith('%%'))
    out, cat, name, seen, notes = [], None, None, {}, 0
    for line in body.split('\n'):
        m = re.match(r'\\subsection\{(.*?) \((\d+) Methods\)\}', line)
        if m:
            cat = m.group(1)
            out.append(f'\\subsection{{{HEAD[cat]} ({m.group(2)} Methods)}}')
            NUMS['nAcc' + CAT[cat].replace('+', '')] = int(m.group(2))
            continue
        if line.startswith('\\label{sec:methods-'):
            out.append(line.replace('sec:methods-', 'supp:methods-'))
            continue
        m = re.match(r'\\item\[(.*) \((\d{4})\)\]', line)
        if m:
            name = m.group(1)
            seen[name] = dict(cat=CAT[cat], year=m.group(2))
        m2 = re.match(r'(\s*)\\textit\{Steps changed:\}\s*(.*)', line)
        if m2:
            t = m2.group(2).rstrip('.')
            seen[name]['dec'] = '' if t.startswith('none') else ''.join(sorted(STEP[x.strip()] for x in t.split(',')))
            line = f'{m2.group(1)}\\textit{{Decisions changed:}} {m2.group(2)} \\textit{{Link:}} {t6[name]["link"]}.'
        if '\\pnote{' in line:
            (a, b, _), = list(macro_args(line, 'pnote'))
            if name not in DECIDED:
                stop(f'provisional note of {name} has no decision')
            line = line[:a] + '\\par\\noindent\\textit{Coding decision:} ' + DECIDED[name] + '\\par' + line[b:]
            notes += 1
        out.append(line)
    if len(seen) != 37 or set(seen) != set(t6):
        stop(f'accounts {len(seen)} against Table 6 {len(t6)}: {set(seen) ^ set(t6)}')
    for n, a in seen.items():
        for k in ('cat', 'year', 'dec'):
            if a[k] != t6[n][k]:
                stop(f'{n}: {k} {a[k]} in the account, {t6[n][k]} in Table 6')
    if notes != len(DECIDED):
        stop(f'{notes} notes replaced, {len(DECIDED)} decisions listed')
    s = '\n'.join(out)
    s = re.sub(r'\\(?:parencite|pcite)\{', r'\\citep{', s)
    NUMS.update(nAccounts=len(seen), nNotes=notes,
                nCore=sum(1 for r in t6.values() if r['link'] == 'Core'),
                nPartial=sum(1 for r in t6.values() if r['link'] == 'Partial'))
    return american(s)


def bibkeys():
    keys = set()
    for f in (DRAFT / 'refs.bib', DRAFT / 'supplement' / 'supp_refs.bib'):
        keys |= set(re.findall(r'@\w+\{([^,\s]+),', f.read_text(encoding='utf-8')))
    return keys


def studies():
    src = (REPO / 'Evaluation section/latex/tables/empirical-studies.tex').read_text(encoding='utf-8')
    s = '\n'.join(l for l in src.splitlines() if not l.startswith('%%'))
    old = 'Std.: points met of the standard in Table~\\ref{tab:empirical-standard}.'
    if s.count(old) != 1:
        stop('legend of the studies table changed')
    s = s.replace(old, 'Std.: points met of the seven-point standard (Table~\\ref{supp:standard}).')
    s = s.replace('\\caption{Coding of the 71 Empirical Studies}\\label{tab:empirical-studies}',
                  '\\caption{Coding of the 71 Empirical Studies}\\label{supp:studies}')
    s = re.sub(r'\\parencite\{', r'\\citep{', s)
    rows = [l for l in s.splitlines() if '\\citep{' in l and l.rstrip().endswith('\\\\')]
    if len(rows) != 71:
        stop(f'{len(rows)} study rows')
    keys = set(k.strip() for r in rows for k in re.search(r'\\citep\{([^}]*)\}', r).group(1).split(','))
    missing = keys - bibkeys()
    if missing:
        stop(f'keys without a bibliography entry: {sorted(missing)}')
    std, yr, key = [], [], []
    for r in rows:
        c = [x.strip() for x in r.rstrip().rstrip('\\').split('&')]
        std.append(int(c[-1]))
        yr.append(int(re.search(r'\((\d{4})\)', c[0]).group(1)))
        key.append(re.search(r'\\citep\{([^}]*)\}', c[0]).group(1))
    got = dict(median=statistics.median(std), before2010=statistics.median([s_ for s_, y in zip(std, yr) if y < 2010]),
               since2021=statistics.median([s_ for s_, y in zip(std, yr) if y >= 2021]),
               seven=[k for s_, k in zip(std, key) if s_ == 7], le3=sum(1 for s_ in std if s_ <= 3))
    want = dict(median=3, before2010=3, since2021=4, seven=['koziarski2019rbo'], le3=39)
    if got != want:
        stop(f'Std. column {got} against Section 6 {want}')
    NUMS.update(nStudies=len(rows), nStudyKeysSupp=len(keys - set(re.findall(r'@\w+\{([^,\s]+),', (DRAFT / 'refs.bib').read_text(encoding='utf-8')))))
    return american(s)


def reference_tasks():
    src = (REPO / 'Data section/manuscript/data-section-final.tex').read_text(encoding='utf-8')
    a = src.index('% Table generated by difficulty/reference_collection.py')
    b = src.index('\\end{table}', a) + len('\\end{table}')
    s = src[a:b].replace('\\begin{table}[t]', '\\begin{table}[htbp]').replace(
        '\\label{tab:data-reference}', '\\label{supp:reference}')
    s = s.replace('% Table generated by difficulty/reference_collection.py (do not edit by hand); in data-section-draft.tex since 29 Oct 2026.',
                  '% Table generated by difficulty/reference_collection.py of the team repository (Data section); copied unchanged.')
    rows = [l for l in s.splitlines() if l.startswith('\\raggedright\\texttt')]
    if len(rows) != 42:
        stop(f'{len(rows)} reference tasks')
    num = lambda x: float(x.replace(',', ''))  # noqa: E731
    cells = [[x.strip() for x in r.rstrip().rstrip('\\').split('&')] for r in rows]
    n, ir, noise = [num(c[4]) for c in cells], [num(c[7]) for c in cells], [num(c[8]) for c in cells]
    got = (min(noise), max(noise), min(ir), max(ir), min(n), max(n))
    if got != (0.0, 1.0, 1.1, 970.6, 79.0, 62630.0):
        stop(f'ranges of the reference tasks {got}')
    NUMS['nTasks'] = len(rows)
    return s


def tt(s):
    return '\\texttt{' + s.replace('\\', '\\textbackslash{}').replace('_', '\\_').replace('&', '\\&').replace(
        '%', '\\%').replace('#', '\\#').replace('$', '\\$').replace('{', '\\{').replace('}', '\\}') + '}'


def ttb(s):
    """tt() with a break point after every underscore and dot, for file names in narrow columns."""
    return tt(s).replace('\\_', '\\_\\allowbreak{}').replace('.', '.\\allowbreak{}')


def fmt_int(x):
    return f'{x:,}'


def search():
    d = DRAFT / 'data/search/2026-11-11'
    sc = json.loads((d / 'scopus_search_log.json').read_text(encoding='utf-8'))
    oa = json.loads((d / 'openalex_search_log.json').read_text(encoding='utf-8'))
    ax = json.loads((d / 'arxiv_search_log.json').read_text(encoding='utf-8'))
    mg = json.loads((d / 'wp4_records_merged_summary.json').read_text(encoding='utf-8'))
    oa_got = sum(p['n'] for p in oa['pages'])
    ax_got = sum(p['entries'] for p in ax['pages'])
    if mg['records_by_source'] != {'scopus': sc['export']['records'], 'openalex': oa_got, 'arxiv': ax_got}:
        stop('merge summary does not match the search logs')
    hm = lambda t: t[11:16]  # noqa: E731
    pre = re.match(r'([\d,]+) preprints', sc['preprints_tab']).group(1)
    L = []
    L.append('\\begin{table}[htbp]\\centering\\footnotesize')
    L.append('\\caption{Identification stage of the systematic search, 10 November 2026 (times in UTC). Found: the '
             'count the source reported; retrieved: the records exported or downloaded. Generated from '
             '\\texttt{scopus\\_search\\_log.json}, \\texttt{openalex\\_search\\_log.json}, '
             '\\texttt{arxiv\\_search\\_log.json} and \\texttt{wp4\\_records\\_merged\\_summary.json} in '
             '\\texttt{data/search/2026-11-11/}.}\\label{supp:searchruns}')
    L.append('\\begin{tabular}{@{}lllrr@{}}\\toprule')
    L.append('Source & Run & Fields searched & Found & Retrieved \\\\ \\midrule')
    L.append(f'Scopus & {hm(sc["searched_utc"])} & title, abstract, author keywords & {fmt_int(sc["documents_found"])} & '
             f'{fmt_int(sc["export"]["records"])} \\\\')
    L.append(f'OpenAlex & {hm(oa["run_utc"])} to {hm(oa["finished_utc"])} & title and abstract & {fmt_int(oa["count"])} & '
             f'{fmt_int(oa_got)} \\\\')
    L.append(f'arXiv & {hm(ax["run_utc"])} & title and abstract & {fmt_int(ax["total_results"])} & {fmt_int(ax_got)} '
             f'\\\\ \\midrule')
    L.append(f'All sources & & & & {fmt_int(mg["records_total"])} \\\\')
    L.append(f'Distinct after matching & & & & {fmt_int(mg["unique_after_dedup"])} \\\\')
    L.append('\\bottomrule\\end{tabular}\\end{table}')
    L.append('')
    L.append(f'Scopus also lists {pre} preprints in a separate preprint index, which offers no export; they are not '
             f'among the records. The Scopus search was run by '
             f'an AI session in an author\'s signed-in browser; OpenAlex and arXiv were queried through their '
             f'public APIs, OpenAlex in {len(oa["pages"])} pages and arXiv in {len(ax["pages"])} pages, and every '
             f'request URL is kept in the log. The exact queries were:')
    for title, q in (('Scopus (advanced search)', sc['query']), ('OpenAlex (filter of the works endpoint)', oa['filter']),
                     ('arXiv (search query of the export API)', ax['query'])):
        L.append(f'\\par\\medskip\\noindent\\textbf{{{title}}}')
        L.append('\\begin{lstlisting}')
        L.append(q)
        L.append('\\end{lstlisting}')
    NUMS.update(nScopus=sc['documents_found'], nOpenAlexFound=oa['count'], nOpenAlexGot=oa_got, nArxiv=ax_got,
                nAllRecords=mg['records_total'], nDistinct=mg['unique_after_dedup'])

    # OpenAlex snapshot: README table of files and urls.tsv
    snap = DRAFT / 'data/openalex/2026-11-10'
    readme = (snap / 'README.md').read_text(encoding='utf-8')
    files = []
    for line in readme.splitlines():
        m = re.match(r'\| `([^`]+)` \| (.*) \|$', line)
        if m:
            files.append((m.group(1), m.group(2)))
    if len(files) < 12:
        stop(f'{len(files)} files in the snapshot README')
    with open(snap / 'urls.tsv', encoding='utf-8') as fh:
        reqs = list(csv.DictReader(fh, delimiter='\t'))

    def md(s):
        s = s.replace('\\', '\\textbackslash{}').replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
        s = re.sub(r'`([^`]+)`', lambda m: tt(m.group(1)), s)
        return s.replace('_', '\\_') if '\\texttt' not in s else re.sub(
            r'(\\texttt\{[^}]*\})|_', lambda m: m.group(1) or '\\_', s)
    S = ['\\subsection{The OpenAlex Snapshot of 10 November 2026}\\label{supp:snapshot}', '']
    S.append(f'Every OpenAlex number of Section~\\ref*{{P-sec:reach}} of the paper and of Section~\\ref{{supp:openalexq}} '
             f'comes from the raw JSON responses of one snapshot, taken by \\texttt{{scripts/openalex\\_snapshot.py}} on '
             f'10 November 2026 between {reqs[0]["utc_time"][11:19]} and {reqs[-1]["utc_time"][11:19]} UTC. '
             f'Table~\\ref{{supp:snapfiles}} lists its files and Table~\\ref{{supp:snapurls}} the time and URL of each '
             f'request. The API key used for the requests is not in any file.')
    S.append('\\begin{table}[htbp]\\centering\\footnotesize')
    S.append('\\caption{Files of the OpenAlex snapshot (folder \\texttt{data/openalex/2026-11-10/}), as described in its '
             'README.}\\label{supp:snapfiles}')
    S.append('\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.3\\linewidth}>{\\raggedright\\arraybackslash}p{0.65\\linewidth}@{}}'
             '\\toprule File & Content \\\\ \\midrule')
    for f, c in files:
        S.append(f'{ttb(f)} & {md(c)} \\\\')
    S.append('\\bottomrule\\end{tabular}\\end{table}')
    S.append('{\\footnotesize\\begin{longtable}{@{}>{\\raggedright\\arraybackslash}p{0.27\\linewidth}l'
             '>{\\raggedright\\arraybackslash}p{0.52\\linewidth}@{}}')
    S.append('\\caption{Requests of the OpenAlex snapshot (\\texttt{urls.tsv}; the WP5 sample keeps its two request '
             'URLs inside its own file).}\\label{supp:snapurls}\\\\ \\toprule File & UTC time & Request URL \\\\ \\midrule\\endfirsthead')
    S.append('\\toprule File & UTC time & Request URL \\\\ \\midrule\\endhead\\bottomrule\\endfoot')
    for r in reqs:
        S.append(f'{ttb(r["file"])} & {r["utc_time"][11:19]} & \\url{{{r["url"]}}} \\\\')
    S.append('\\end{longtable}}')
    NUMS.update(nSnapFiles=len(files), nSnapRequests=len(reqs))
    return '\n'.join(L), '\n'.join(S)


CODEBOOKS = [  # (file, subsection title)
    ('SCREENING_CODEBOOK.md', 'Screening on Title and Abstract: Codebook'),
    ('AGENT_INSTRUCTIONS.md', 'Screening: Instructions for the First Pass and the Second Look'),
    ('adjudication/AGENT_INSTRUCTIONS.md', 'Screening: Instructions for the Third Look'),
    ('rule_b/RULE_B_CODEBOOK.md', 'Screening: Rulings B, B2 and C, Codebook of the Rulings Pass'),
    ('rule_b/AGENT_INSTRUCTIONS.md', 'Screening: Instructions for the Rulings Pass'),
    ('coverage/COVERAGE_CODEBOOK.md', 'Coverage Sample: Codebook'),
    ('coverage/AGENT_INSTRUCTIONS.md', 'Coverage Sample: Instructions for Each Session'),
    ('coverage/RULINGS_FULLTEXT_INSTRUCTIONS.md', 'Coverage Sample: Instructions for the Recheck under Rulings B, B2 and C'),
    ('coverage/ROUND2_NOTE.md', 'Coverage Sample: Note for the Sessions of the Library Round'),   # v0.37
    ('useaudit/USE_AUDIT_CODEBOOK.md', 'Use Audit: Codebook'),
    ('useaudit/AGENT_INSTRUCTIONS.md', 'Use Audit: Instructions for Each Session'),
    ('useaudit/ROUND2_NOTE.md', 'Use Audit: Note for the Sessions of the Library Round'),   # v0.37
    # v0.25 (D42): the blind second coding of both samples and the adjudication of its differences
    ('d42/protocol/AGENT_INSTRUCTIONS_coverage.md', 'Coverage Sample: Instructions for the Blind Second Coding'),
    ('d42/protocol/AGENT_INSTRUCTIONS_useaudit.md', 'Use Audit: Instructions for the Blind Second Coding'),
    ('d42/protocol/ADJUDICATION_INSTRUCTIONS.md', 'Both Samples: Instructions for the Adjudication of the Second Coding'),
]


HARM = {'H-calibration': 'calibration', 'H-leakage': 'leakage', 'H-fairness': 'fairness', 'H-privacy': 'privacy'}
XCODE = {'X-no-comparison': 'no comparison with a model trained without resampling',
         'X-not-resampling': 'not resampling in the machine-learning sense',
         'X-no-harm-measure': 'a comparison without a measure of harm', 'X-not-study': 'not a study',
         'U-abstract': 'the abstract does not settle it (full text needed)'}


def esc(s):
    tr = {'\\': '\\textbackslash{}', '&': '\\&', '%': '\\%', '#': '\\#', '_': '\\_', '$': '\\$', '{': '\\{', '}': '\\}'}
    return re.sub(r'[\\&%#_${}]', lambda m: tr[m.group(0)], s)


def harm():
    base = DRAFT / 'wp5'
    log = json.loads((base / 'harm_search_log.json').read_text(encoding='utf-8'))
    summ = json.loads((base / 'harm_search/work/summary.json').read_text(encoding='utf-8'))
    rows = list(csv.DictReader(open(base / 'harm_search/harm_search_records.csv', encoding='utf-8')))
    if len(rows) != summ['records']:
        stop('harm search: records and summary differ')
    inc = [r for r in rows if r['decision'] == 'include']
    if len(inc) != summ['decision'].get('include', 0):
        stop('harm search: includes and summary differ')
    qs = [q for q in log if q['query'][:2] in ('H1', 'H2', 'H3', 'H4')]
    L = ['\\begin{table}[htbp]\\centering\\footnotesize',
         '\\caption{Queries of the harm search, PubMed, run on 10 November 2026 (rerun on 11 November with the same counts). '
         'Generated from \\texttt{wp5/harm\\_search\\_log.json}.}\\label{supp:harmqueries}',
         '\\begin{tabular}{@{}lp{10.2cm}r@{}}', '\\toprule', 'Query & PubMed search term & Records \\\\', '\\midrule']
    for q in qs:
        L.append(f"{esc(q['query'])} & \\texttt{{{esc(q['term'])}}} & {fmt_int(q['count'])} \\\\")
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']
    dec, code = summ['decision'], summ['code']
    fnd = summ['includes_by_finding']
    L += ['\\begin{table}[htbp]\\centering\\footnotesize',
          f"\\caption{{Result of the screen on title and abstract of the {fmt_int(summ['records'])} distinct records (AI sessions, "
          'a single screener per record). Generated from '
          '\\texttt{wp5/harm\\_search/work/summary.json}.}\\label{supp:harmcounts}',
          '\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{7.6cm}rrrr@{}}', '\\toprule',
          'Included, by harm & Studies & Harm found & No harm & Mixed \\\\', '\\midrule']
    for c in ('H-calibration', 'H-leakage', 'H-fairness', 'H-privacy'):
        f = fnd.get(c, {})
        L.append(f"{HARM[c].capitalize()} & {summ['includes_by_harm'].get(c, 0)} & {f.get('harm', 0)} & {f.get('no harm', 0)} & {f.get('mixed', 0)} \\\\")
    L.append(f"\\midrule\\multicolumn{{5}}{{@{{}}l}}{{Not included}} \\\\")
    L.append(f"\\quad Unsure: {XCODE['U-abstract']} & {dec.get('unsure', 0)} & & & \\\\")
    for c in ('X-no-comparison', 'X-not-resampling', 'X-no-harm-measure', 'X-not-study'):
        L.append(f"\\quad Excluded: {XCODE[c]} & {code.get(c, 0)} & & & \\\\")
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']
    NUMS['nHarmRecords'] = summ['records']
    NUMS['nHarmInclude'] = len(inc)
    NUMS['nHarmUnsure'] = dec.get('unsure', 0)
    NUMS['nHarmNoComparisonCalibration'] = summ['harm_measure_reported_without_comparison'].get('calibration', 0)
    order = {'H-calibration': 0, 'H-leakage': 1, 'H-fairness': 2}
    L += ['{\\footnotesize\\setlength{\\tabcolsep}{4pt}\\setlength{\\LTcapwidth}{\\linewidth}', '\\begin{longtable}{@{}p{1.35cm}p{0.75cm}>{\\raggedright\\arraybackslash}p{5.9cm}p{1.5cm}>{\\raggedright\\arraybackslash}p{2.9cm}p{1.3cm}@{}}',
          f"\\caption{{The {len(inc)} included studies of the harm search: PubMed identifier, year, journal, the harm measured, the "
          'comparison (with a model trained without resampling, or resampling before against after the split) and the finding '
          'as the screener coded it from the abstract. Generated from \\texttt{wp5/harm\\_search/harm\\_search\\_records.csv}.}'
          '\\label{supp:harmincludes}\\\\', '\\toprule',
          'PMID & Year & Journal & Harm & Comparison & Finding \\\\', '\\midrule', '\\endfirsthead', '\\toprule',
          'PMID & Year & Journal & Harm & Comparison & Finding \\\\', '\\midrule', '\\endhead', '\\bottomrule', '\\endlastfoot']
    for r in sorted(inc, key=lambda r: (order.get(r['code'], 9), -int(r['year'] or 0), r['pmid'])):
        j = r['journal'].split(' : ')[0]
        cmp_ = {'no resampling': 'without resampling', 'before vs after split': 'before vs.\\ after the split',
                'both': 'both'}.get(r['comparison'], r['comparison'])
        L.append(f"{r['pmid']} & {r['year']} & {esc(j)} & {HARM[r['code']]} & {cmp_} & {r['finding']} \\\\")
    L += ['\\end{longtable}}']
    return '\n'.join(L)


RR_NAMES = {'none': 'No resampling', 'class_weight': 'Class weights', 'threshold': 'Tuned threshold', 'ROS': 'Random oversampling'}
RR_ORDER = ['none', 'class_weight', 'threshold', 'ROS', 'Cluster-SMOTE', 'ADASYN', 'Safe-Level-SMOTE', 'CGMOS', 'SMOM',
            'G-SMOTE', 'AB-SMOTE', 'RSMOTE', 'FW-SMOTE']


def md_inline(s):
    s = esc(s.replace('**', ''))
    return re.sub(r'`([^`]*)`', lambda m: '\\texttt{' + m.group(1) + '}', s)


def rerun42():
    base = DRAFT / 'benchmark/results_summary/rerun42'
    if not (base / 'summary.json').exists():
        stop('rerun42: run benchmark/rerun42/scripts/stats42.py first')
    summ = json.loads((base / 'summary.json').read_text(encoding='utf-8'))
    tests = list(csv.DictReader(open(base / 'tests_vs_smote.csv', encoding='utf-8')))
    status = list(csv.DictReader(open(base / 'cell_status.csv', encoding='utf-8')))
    readme = (DRAFT / 'benchmark/rerun42/methods/README.md').read_text(encoding='utf-8')
    rows = [l for l in readme.splitlines() if l.startswith('| ') and not l.startswith('| Method') and not l.startswith('|---')]
    rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in rows][:5]
    if len(rows) != 5 or any(len(r) != 6 for r in rows):
        stop('rerun42: the validation table of methods/README.md has changed shape')
    NUMS['nRerunTasks'] = summ['tasks']
    NUMS['nRerunFamilies'] = summ['families']
    NUMS['nRerunCells'] = summ['fold_results']
    L = ['{\\footnotesize\\setlength{\\tabcolsep}{4pt}\\setlength{\\LTcapwidth}{\\linewidth}',
         '\\begin{longtable}{@{}>{\\raggedright\\arraybackslash}p{1.6cm}>{\\raggedright\\arraybackslash}p{4.6cm}'
         '>{\\raggedright\\arraybackslash}p{1.9cm}>{\\raggedright\\arraybackslash}p{3.6cm}>{\\raggedright\\arraybackslash}p{2.6cm}@{}}',
         '\\caption{Validation of the five re-implementations against a number their papers print. Parsed from '
         '\\texttt{benchmark/rerun42/methods/README.md}; the method folders hold each \\texttt{VALIDATION.md} and '
         '\\texttt{NOTES.md}.}\\label{supp:validation}\\\\', '\\toprule',
         'Method & Validated against & Paper & This implementation & Verdict \\\\', '\\midrule', '\\endfirsthead',
         '\\toprule', 'Method & Validated against & Paper & This implementation & Verdict \\\\', '\\midrule', '\\endhead',
         '\\bottomrule', '\\endlastfoot']
    for r in rows:
        L.append(' & '.join(md_inline(c) for c in r[:5]) + ' \\\\')
    L += ['\\end{longtable}}', '']
    st = {r['method']: r for r in status}
    cols = [c for c in ('ok', 'error', 'not applicable') if c in status[0]]
    L += ['\\begin{table}[htbp]\\centering\\footnotesize',
          f"\\caption{{Cells of the rerun by method and status ({fmt_int(summ['fold_results'])} cells: {summ['tasks']} tasks, "
          '5 x 5 folds, 6 learners). An error is a sampler that could not run on a training fold: SMOTE, G-SMOTE and ADASYN '
          'when the fold holds too few minority examples for five neighbors, and ADASYN also when no minority example has a '
          'majority neighbor or its rule generates no point. Generated from \\texttt{cell\\_status.csv}.}\\label{supp:rrstatus}',
          '\\begin{tabular}{@{}l' + 'r' * len(cols) + '@{}}', '\\toprule', 'Method & ' + ' & '.join(c.capitalize() for c in cols) + ' \\\\', '\\midrule']
    for m in ['SMOTE'] + RR_ORDER:
        if m in st:
            L.append(f"{RR_NAMES.get(m, m)} & " + ' & '.join(fmt_int(int(st[m].get(c, 0) or 0)) for c in cols) + ' \\\\')
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']
    T = {(r['learner'], r['measure'], r['method']): r for r in tests}

    def cell(ln, ms, m):
        r = T.get((ln, ms, m))
        if not r:
            return 'n/a', ''
        v = float(r['median_diff_vs_smote'])
        txt = ('$-$' if v < -0.0005 else '+' if v > 0.0005 else '') + (f'{abs(v):.3f}'.lstrip('0') if abs(v) >= 0.0005 else '.000')
        star = '*' if float(r['holm_p']) < 0.05 else ''
        return txt + star, r

    for ln, lname in (('RF', 'random forest'), ('GB', 'gradient boosting')):
        L += ['\\begin{table}[htbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}',
              f'\\caption{{Rerun, {lname}: median difference from SMOTE over families of tasks (positive: better than SMOTE; for the '
              'Brier score, positive: lower, that is better), with * where the Holm-adjusted Wilcoxon $p$ is below 0.05, and the '
              'Bayesian signed-rank probabilities for PR-AUC that the method is worse than SMOTE, practically equivalent '
              '(within 0.01) or better (w/e/b). Generated from \\texttt{tests\\_vs\\_smote.csv}.}'
              f'\\label{{supp:rr{ln.lower()}}}',
              '\\begin{tabular}{@{}lrrrrrl@{}}', '\\toprule',
              'Method & Families & ROC-AUC & PR-AUC & G-mean & Brier & PR-AUC: P(w/e/b) \\\\',
              '\\midrule']
        for m in RR_ORDER:
            vals = [cell(ln, ms, m) for ms in ('roc_auc', 'pr_auc', 'gmean', 'brier')]
            r = vals[1][1]
            if not r:
                L.append(f"{RR_NAMES.get(m, m)} & n/a & n/a & n/a & n/a & n/a & left out \\\\")
                continue
            pr = '/'.join(f'{float(r[k]):.2f}' if r[k] not in ('', 'nan') else 'n/a' for k in ('p_smote_better', 'p_rope', 'p_method_better'))
            L.append(f"{RR_NAMES.get(m, m)} & {r['n_families']} & " + ' & '.join(v[0] for v in vals) + f" & {pr} \\\\")
        L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']
    return '\n'.join(L)


TP_LABELS = {'TabPFN: SMOTE vs none': 'TabPFN after SMOTE vs TabPFN',
             'TabPFN vs RF, both none': 'TabPFN vs random forest',
             'TabPFN vs GB, both none': 'TabPFN vs gradient boosting',
             'TabPFN none vs RF after SMOTE': 'TabPFN vs random forest after SMOTE',
             'TabPFN none vs GB after SMOTE': 'TabPFN vs gradient boosting after SMOTE'}


def tabpfn():
    """v0.29 (D43): the TabPFN arm of the rerun, from benchmark/results_summary/rerun42/tabpfn/ (stats42_tabpfn.py:
    summary.json, tabpfn_comparisons.csv; tabpfn_cells42.py: cells.json)."""
    base = DRAFT / 'benchmark/results_summary/rerun42/tabpfn'
    if not (base / 'cells.json').exists():
        stop('tabpfn: run benchmark/rerun42/scripts/stats42_tabpfn.py and tabpfn_cells42.py first')
    summ = json.loads((base / 'summary.json').read_text(encoding='utf-8'))
    cells = json.loads((base / 'cells.json').read_text(encoding='utf-8'))
    comps = list(csv.DictReader(open(base / 'tabpfn_comparisons.csv', encoding='utf-8')))
    if len(comps) != 15 or {c['comparison'] for c in comps} != set(TP_LABELS):
        stop('tabpfn: tabpfn_comparisons.csv has changed shape')
    kinds = cells['errors_by_kind']
    if set(kinds) - {'out of memory', 'sampler'} or cells['ok'] + cells['error'] != cells['cells']:
        stop('tabpfn: cells.json has errors of another kind, or its counts do not add up')
    if cells['folds_same_as_rerun'] != cells['folds_compared']:
        stop('tabpfn: the fold files of the arm differ from the rerun')
    NUMS.update(nTabpfnCells=cells['cells'], nTabpfnOk=cells['ok'], nTabpfnOom=kinds.get('out of memory', 0),
                nTabpfnSampler=kinds.get('sampler', 0), nTabpfnTasks=summ['tasks_complete'], nTabpfnFamilies=summ['families'],
                nTabpfnCloudTasks=cells['rf_gb_tasks_from_first_dir'], nTabpfnFolds=cells['folds_compared'],
                nTabpfnHours=f"{cells['hours_of_cells_with_result']:.2f}", nTabpfnPackage=cells['config']['package'],
                nTabpfnModel=cells['config']['model'].rsplit('.V', 1)[-1].replace('_', '.'))
    reason = {}
    for k, ts in cells['tasks_by_kind'].items():
        for t in ts:
            reason[t] = 'out of the processor\'s memory' if k == 'out of memory' else 'too few minority examples for SMOTE'
    L = ['\\begin{table}[htbp]\\centering\\footnotesize',
         '\\caption{Tasks left out of the TabPFN arm: cells (of 25 folds) without a result, without resampling and after '
         'SMOTE. Generated from \\texttt{cells.json} (\\texttt{benchmark/rerun42/scripts/tabpfn\\_cells42.py}).}'
         '\\label{supp:tpleft}', '\\begin{tabular}{@{}lrrl@{}}', '\\toprule',
         'Task & Without resampling & After SMOTE & Reason \\\\', '\\midrule']
    for t in sorted(cells['tasks_left_out']):
        e = cells['errors_by_task'].get(t, {})
        L.append(f"{esc(t)} & {e.get('none error', 0)} & {e.get('SMOTE error', 0)} & {reason.get(t, 'n/a')} \\\\")
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']

    def diff(v):
        v = float(v)
        return ('$-$' if v < -0.0005 else '+' if v > 0.0005 else '') + (f'{abs(v):.3f}'.lstrip('0') if abs(v) >= 0.0005 else '.000')

    def pv(p):
        p = float(p)
        return '<.001' if p < 0.001 else f'{p:.3f}'.lstrip('0')
    L += ['\\begin{table}[htbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}',
          f"\\caption{{TabPFN arm of the rerun ({summ['tasks_complete']} tasks, {summ['families']} families): median difference "
          'over families of tasks (positive: the first side is better; for the Brier score, positive: the first side\'s score is '
          'lower), Holm-adjusted Wilcoxon $p$ over the five comparisons of a measure, and the Bayesian signed-rank probabilities '
          'that the first side is better, that the two are practically equivalent (within 0.01) or that the second side is '
          'better (b/e/w). TabPFN and the two strong learners without resampling unless stated. Generated from '
          '\\texttt{tabpfn\\_comparisons.csv} (\\texttt{stats42\\_tabpfn.py}).}\\label{supp:tabpfn}',
          '\\begin{tabular}{@{}llrrrl@{}}', '\\toprule',
          'Comparison & Measure & Families & Median diff. & Holm $p$ & P(b/e/w) \\\\', '\\midrule']
    names = {'roc_auc': 'ROC-AUC', 'pr_auc': 'PR-AUC', 'brier': 'Brier'}
    for lab in TP_LABELS:
        for m in ('roc_auc', 'pr_auc', 'brier'):
            r = next(c for c in comps if c['comparison'] == lab and c['measure'] == m)
            pr = '/'.join(f"{float(r[k]):.2f}" for k in ('p_first_better', 'p_rope', 'p_second_better'))
            first = TP_LABELS[lab] if m == 'roc_auc' else ''
            L.append(f"{first} & {names[m]} & {r['n_families']} & {diff(r['median_diff'])} & {pv(r['holm_p'])} & {pr} \\\\")
        if lab != list(TP_LABELS)[-1]:
            L.append('\\addlinespace')
    L += ['\\bottomrule', '\\end{tabular}', '\\end{table}', '']
    return '\n'.join(L)


def codebooks():
    base = DRAFT / 'data/search/screening_full_2026-11-11'
    parts = []
    for f, title in CODEBOOKS:
        md = (base / f).read_text(encoding='utf-8')
        first, rest = md.split('\n', 1)
        if not first.startswith('# '):
            stop(f'{f} does not start with a title')
        tex = subprocess.run(['pandoc', '-f', 'markdown+lists_without_preceding_blankline-auto_identifiers', '-t', 'latex', '--wrap=preserve',
                              '--shift-heading-level-by=1'], input=rest, capture_output=True, text=True, check=True).stdout
        parts.append(f'\\subsection{{{title}}}\n\\noindent\\textit{{File}} {tt(f)}\\textit{{; its title line reads:}} '
                     f'{first[2:]}\\par\\medskip\n{tex}')
    NUMS['nCodebookFiles'] = len(CODEBOOKS)
    # v0.12: let long paths and commands in typewriter type break after a slash or an underscore, and set the
    # codebooks sloppy, so that the instructions fit the measure (the text itself is unchanged)
    def _brk(m):
        return '\\texttt{' + m.group(1).replace('/', '/\\allowbreak{}').replace('\\_', '\\_\\allowbreak{}') + '}'
    body = re.sub(r'\\texttt\{((?:[^{}]|\{[^{}]*\})*)\}', _brk, '\n\n'.join(parts))
    # the two-column tables of the codebooks (a field and its meaning): a narrow first column instead of pandoc's halves
    half = '>{\\raggedright\\arraybackslash}p{(\\columnwidth - 2\\tabcolsep) * \\real{0.5000}}'
    body = body.replace(half + '\n  ' + half, half.replace('0.5000', '0.2000') + '\n  ' + half.replace('0.5000', '0.8000'))
    return '{\\sloppy\n' + body + '\n\\par}'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    srch, snap = search()
    out = {'accounts.tex': accounts(), 'studies.tex': studies(), 'reference_tasks.tex': reference_tasks(),
           'search.tex': srch, 'snapshot.tex': snap, 'codebooks.tex': codebooks(), 'harm.tex': harm(),
           'rerun42.tex': rerun42(), 'tabpfn.tex': tabpfn()}
    for f, s in out.items():
        if '---' in s or '\u2014' in s:
            stop(f'em-dash in {f}')
        low = s.lower().replace('optimistic', '').replace('organism', '')   # American words that contain a watched stem
        bad = [w for w in WATCH if w in low]
        if bad:
            stop(f'British spelling in {f}: {bad}')
        (OUT / f).write_text(f'% Generated by scripts/make_supplement.py; do not edit by hand.\n{s}\n', encoding='utf-8')
    (OUT / 'numbers.tex').write_text(
        '% Generated by scripts/make_supplement.py; do not edit by hand.\n' +
        ''.join(f'\\newcommand{{\\{k}}}{{{fmt_int(v) if isinstance(v, int) else v}}}\n' for k, v in sorted(NUMS.items())),
        encoding='utf-8')
    (OUT / 'numbers.json').write_text(json.dumps(NUMS, indent=1), encoding='utf-8')
    print('wrote', ', '.join(out), 'and numbers.tex:', json.dumps(NUMS))


if __name__ == '__main__':
    main()
