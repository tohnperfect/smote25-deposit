#!/usr/bin/env python3
"""Step 8 (D53): build the deposit bundle, one folder for both Zenodo and the GitHub repository tohnperfect/smote25-deposit.

What goes in follows Section S4.4 of the online appendix and item 10 of the handoff (answered on 12 Nov 2026); what
never goes in: any abstract (the Scopus export is licensed), full texts, the passages quoted from papers (`quote`,
`evidence` and similar columns), the screening and check workbooks and lists, the PubMed abstracts, the batch files
of the looks, the data files of the 42 tasks and the Kaggle file, the review pages' data, and anything marked PRIVATE.
Since v0.30 (D56, 14 Nov 2026) also nothing produced by TabPFN-3.5: neither the model nor the results of the TabPFN arm
of the rerun, per fold or averaged (its license lets the outputs be used for non-commercial purposes, while the data
here carry CC BY 4.0); the arm's scripts are deposited. The build stops if a --rerun-results folder holds TabPFN cells,
and the scan reports any file that holds them.

The script copies, never moves; CSV and JSON files are rewritten without the banned columns or keys, and every
dropped column is listed in BUILD_REPORT.json. It then scans the whole bundle and stops (exit 1) on: a banned column
or key left, a spreadsheet, a file over 100 MB (GitHub's limit; such a file is split into numbered parts with a
`join` note, or the build stops if --no-split), an access token (the Zenodo token is read from the environment
variable ZENODO_TOKEN only to search for it; the OpenAlex key likewise from OPENALEX_API_KEY), an `api_key=` with a
value, or a gmail address (every e-mail address but the authors' printed ones is replaced first). It writes README.md, CITATION.cff, the two licenses and MANIFEST.tsv (path, bytes, sha256).

Usage:
  python3 -I scripts/build_deposit.py <draft dir> <team-repo dir> <out dir> [--rerun-results DIR ...]
      [--benchmark-results DIR] [--arxiv ID] [--journal-doi DOI] [--no-split]
v0.38 (Last Pass, 16 Nov 2026): in the records of the authors' checks (the spot-check summaries and changes of WP3 and
D42, the count check, and the log of the library PDFs) every author's name is replaced by "an author"; the scan stops if
one is left there. Round 3 of D42 is deposited like round 2 (without the adjudicator's reasons and the check page).
Nothing is pushed or uploaded; a session does that at submission with the team lead's approval.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

BANNED = {'abstract', 'abstracts', 'quote', 'quotes', 'evidence', 'snippet', 'excerpt', 'passage', 'full_text',
          'fulltext', 'text_excerpt'}
TEXT_COLUMNS = {'crit_text', 'prep_text', 'src_text'}   # verbatim criteria, preprocessing and source text from papers


def banned(name):
    """A column or key that may hold text from a paper: an abstract, a quotation, or the evidence quoted for a code
    (a page or table reference, *_ref, stays)."""
    c = str(name).strip().lower()
    return (c in BANNED or c in TEXT_COLUMNS or any(k in c for k in ('abstract', 'quote', 'excerpt', 'snippet'))
            or ('evidence' in c and not c.endswith('_ref')))


SKIP_SUFFIX = {'.xlsx', '.xls', '.pdf', '.zip', '.html', '.pyc', '.aux', '.log', '.gz', '.tgz'}
SKIP_NAME = re.compile(r'(_PRIVATE\.|^\.DS_Store$|^__pycache__$)')
LIMIT = 100 * 1024 * 1024
# the authors' addresses that the paper prints; any other e-mail address in a deposited text is replaced
ALLOWED_EMAILS = {'thanin@kku.ac.th', 'pharamut@kkumail.com', 'kanvara.t@kkumail.com', 'supawit.c@kkumail.com'}
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
TEXT_SUFFIX = {'.md', '.txt', '.py', '.tex', '.sh', '.bib', '.r', '.yml', '.yaml', '.cfg', '.toml', '.ini', '.log'}
REDACTED = [0]
# v0.38 (Last Pass, D51): the records of the authors' checks name no author; each name becomes "an author"
CHECK_RECORD = re.compile(r'(spot_check_|count_check_|library_pdfs_)')
NAMES = ['Thanapong Intharah', 'Pharamut Makjaroen', 'Kanvara Thawarorit', 'Supawit Chaingam', 'Thanapong', 'Intharah',
         'Pharamut', 'Makjaroen', 'Kanvara', 'Thawarorit', 'Supawit', 'Chaingam']
NAME_RE = re.compile(r'\b(' + '|'.join(re.escape(n) for n in NAMES) + r')\b')
ANON = [0]


def anonymize(x):
    if isinstance(x, str):
        y, k = NAME_RE.subn('an author', x)
        ANON[0] += k
        return y
    if isinstance(x, dict):
        return {anonymize(k): anonymize(v) for k, v in x.items()}
    if isinstance(x, list):
        return [anonymize(v) for v in x]
    return x


def redact(t):
    def one(m):
        e = m.group(0).lower()
        if any(a == e or a.endswith(e) for a in ALLOWED_EMAILS):
            return m.group(0)
        REDACTED[0] += 1
        return '[e-mail removed]'
    return EMAIL.sub(one, t)
HOME_PATH = re.compile(rb'(/Users/)([A-Za-z0-9._-]+)')


def redact_home(O, report):
    """25 Nov 2026, before the first upload: the error traces of failed cells in the per-fold results hold the path of
    the folder they ran in, with the account name of the MacBook. Every /Users/<name> becomes /Users/USER, and so
    does <name>/ where a cut trace left the name without its prefix."""
    files, names = [], set()
    for p in sorted(O.rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.jsonl', '.json', '.csv', '.txt', '.md', '.tsv'):
            b = p.read_bytes()
            found = {m.group(2) for m in HOME_PATH.finditer(b)} - {b'USER', b'Shared'}
            if found:
                names |= found
            files.append(p)
    names = {n for n in names if len(n) >= 4}
    n_files = 0
    for p in files:
        b = p.read_bytes()
        c = HOME_PATH.sub(lambda m: m.group(1) + b'USER', b)
        for n in names:
            c = re.sub(rb'(?<![A-Za-z0-9._-])' + re.escape(n) + rb'(?=/)', b'USER', c)
        if c != b:
            p.write_bytes(c)
            n_files += 1
    report['home_paths_redacted'] = dict(files=n_files, names=len(names))
    return [n.decode('utf-8', 'replace') for n in names]


DOI = '10.5281/zenodo.24212321'
REPO = 'https://github.com/tohnperfect/smote25-deposit'
TITLE = 'SMOTE 25 Years of Magic: What Has Been Done, What the Evidence Shows, and Whom It Reached'
AUTHORS = [('Intharah', 'Thanapong', '0000-0003-0965-680X'), ('Makjaroen', 'Pharamut', ''),
           ('Thawarorit', 'Kanvara', ''), ('Chaingam', 'Supawit', '')]
AFFIL = 'Khon Kaen University'

# (source root key, relative glob, destination folder); roots: D = draft, T = team repo
SPEC = [
    ('D', 'scripts/**/*', 'paper_scripts/scripts'),
    ('D', 'gen/*', 'paper_scripts/gen'),
    ('D', 'supplement/gen/*', 'paper_scripts/supplement_gen'),
    ('D', 'ledger.csv', 'paper_scripts'),
    ('D', 'figures/*', 'paper_scripts/figures'),
    ('D', 'data/search/2026-11-11/arxiv_records.csv', 'search/identification'),
    ('D', 'data/search/2026-11-11/*_search_log.json', 'search/identification'),
    ('D', 'data/search/2026-11-11/wp4_records_merged_summary.json', 'search/identification'),
    ('D', 'data/search/2026-11-11/corpus_papers.json', 'search/identification'),   # v0.58: the corpus against the records
    ('D', 'data/search/2026-11-11/corpus_in_records.*', 'search/identification'),
    ('D', 'data/search/2026-11-11/wp7_keyword_counts.json', 'search/identification'),
    ('D', 'data/search/zenodo_status_2026-11-11.csv', 'search/identification'),
    ('D', 'data/search/ZENODO_WITHDRAWN.md', 'search/identification'),
    ('D', 'data/search/screening_full_2026-11-11/*.md', 'search/screen'),
    ('D', 'data/search/screening_full_2026-11-11/person_overrides.csv', 'search/screen'),
    ('D', 'data/search/screening_full_2026-11-11/withdrawn_records.csv', 'search/screen'),
    ('D', 'data/search/screening_full_2026-11-11/decisions/*', 'search/screen/decisions'),
    ('D', 'data/search/screening_full_2026-11-11/final/*', 'search/screen/final'),
    ('D', 'data/search/screening_full_2026-11-11/result/*', 'search/screen/first_pass_result'),
    ('D', 'data/search/screening_full_2026-11-11/first_pass/out/*', 'search/screen/first_pass'),
    ('D', 'data/search/screening_full_2026-11-11/second_look/out/*', 'search/screen/second_look'),
    ('D', 'data/search/screening_full_2026-11-11/second_look/*.md', 'search/screen/second_look'),
    ('D', 'data/search/screening_full_2026-11-11/adjudication/out/*', 'search/screen/third_look'),
    ('D', 'data/search/screening_full_2026-11-11/adjudication/*.md', 'search/screen/third_look'),
    ('D', 'data/search/screening_full_2026-11-11/rule_b/**/*', 'search/screen/rulings_pass'),
    ('D', 'data/search/screening_full_2026-11-11/check/returns/**/*', 'search/screen/independent_check'),
    ('D', 'data/search/screening_full_2026-11-11/check/from_report/*', 'search/screen/independent_check'),
    ('D', 'data/search/screening_full_2026-11-11/check/README.md', 'search/screen/independent_check'),
    ('D', 'data/search/screening_full_2026-11-11/check/codebooks/*', 'search/screen/independent_check/codebooks'),
    ('D', 'data/search/screening_full_2026-11-11/samples/coverage_sample.csv', 'search/samples'),
    ('D', 'data/search/screening_full_2026-11-11/samples/useaudit_sample.csv', 'search/samples'),
    ('D', 'data/search/screening_full_2026-11-11/samples/reserves.csv', 'search/samples'),
    ('D', 'data/search/screening_full_2026-11-11/samples/coverage_late_corrections.csv', 'search/samples'),   # v0.61
    ('D', 'data/search/screening_full_2026-11-11/samples/samples_summary.json', 'search/samples'),
    ('D', 'data/search/screening_full_2026-11-11/samples/library_pdfs_2026-11-16.csv', 'search/samples'),   # v0.38
    ('D', 'data/search/screening_full_2026-11-11/coverage/**/*', 'search/samples/coverage'),
    ('D', 'data/search/screening_full_2026-11-11/useaudit/**/*', 'search/samples/useaudit'),
    ('D', 'data/search/screening_full_2026-11-11/d42/**/*', 'search/samples/d42_second_coding'),   # v0.25 (D42)
    ('D', 'data/search/screening_full_2026-11-11/tools/*', 'search/screen/tools'),
    ('D', 'data/search/screening_full_2026-11-11/fulltext_tools/*', 'search/samples/fulltext_tools'),
    ('D', 'data/reflists/*', 'search/reference_lists'),   # v0.53: the check against the reference lists of five reviews
    ('D', 'data/reflists/crossref/*', 'search/reference_lists/crossref'),
    ('D', 'data/openalex/**/*', 'reach/openalex_snapshot'),
    ('D', 'wp5/harm_search/raw/fetch_log.tsv', 'harm_search'),
    ('D', 'wp5/harm_search/work/decisions/*', 'harm_search/decisions'),
    ('D', 'wp5/harm_search/work/summary.json', 'harm_search'),
    ('D', 'wp5/harm_search/harm_search_records.csv', 'harm_search'),
    ('D', 'wp5/harm_search/person_overrides.csv', 'harm_search'),
    ('D', 'wp5/harm_search/*.md', 'harm_search'),
    ('D', 'wp5/harm_search/scripts/*', 'harm_search/scripts'),
    ('D', 'wp3/adjudication/**/*', 'extraction/wp3_adjudication'),
    ('D', 'data/wp3_blind/**/*', 'extraction/wp3_blind_second_pass'),
    ('D', 'data/d35/**/*', 'extraction/d35_recomputation'),
    ('D', 'benchmark/*.py', 'benchmark'),
    ('D', 'benchmark/*.md', 'benchmark'),
    ('D', 'benchmark/rerun42/**/*', 'benchmark/rerun42'),
    ('D', 'benchmark/results_summary/**/*', 'benchmark/results_summary'),
    ('T', 'Method section/**/*', 'extraction/team_repository/Method section'),
    ('T', 'Data section/**/*', 'extraction/team_repository/Data section'),
    ('T', 'Evaluation section/**/*', 'extraction/team_repository/Evaluation section'),
]
TABPFN_CELL = b'"learner": "' + 'TabPFN'.encode() + b'"'   # v0.30 (D56); built so this file does not match it
EXCLUDE = [re.compile(p) for p in (
    r'^data/search/2026-11-11/wp4_records_merged\.csv\.gz$',   # merged records with the Scopus abstracts
    r'/check/(csv|team_review)/', r'/batches?/', r'^wp5/harm_search/(raw/H\d|work/batches|work/records\.json)',
    r'^benchmark/rerun42/tabpfn_phase/venv/', r'/out/team_pages/', r'^scripts/__pycache__/',
    r'/d42/(round[23]/)?(adjudication_log\.csv|adjudication_raw/|check_page/)',   # v0.25: the adjudicator's reasons may quote papers (v0.37: and round 2's; v0.38: round 3's)
    r'^benchmark/results_summary/rerun42/tabpfn/',   # v0.30 (D56): nothing produced by TabPFN-3.5 is deposited
    r'^data/reflists/crossref_works/',   # v0.53: Crossref's records of the cited works, with abstracts; kept for the coding only
)]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def drop_keys(x, dropped):
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if banned(k):
                dropped.add(str(k))
                continue
            out[k] = drop_keys(v, dropped)
        return out
    if isinstance(x, list):
        return [drop_keys(v, dropped) for v in x]
    if isinstance(x, str):
        return redact(x)
    return x


def copy_clean(src, dst, report):
    dst.parent.mkdir(parents=True, exist_ok=True)
    suf = src.suffix.lower()
    _copy_clean(src, dst, report, suf)
    if CHECK_RECORD.search(dst.name):   # v0.38: the authors' check records name no author
        if suf == '.json':
            dst.write_text(json.dumps(anonymize(json.loads(dst.read_text(encoding='utf-8'))), ensure_ascii=False, indent=1),
                           encoding='utf-8')
        elif suf in ('.csv', '.tsv'):
            with open(dst, newline='', encoding='utf-8') as f:
                rows = list(csv.reader(f, delimiter='\t' if suf == '.tsv' else ','))
            with open(dst, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter='\t' if suf == '.tsv' else ',', lineterminator='\n').writerows(anonymize(rows))
        elif suf in TEXT_SUFFIX:
            dst.write_text(anonymize(dst.read_text(encoding='utf-8')), encoding='utf-8')
        report.setdefault('anonymized', []).append(str(dst.name))


def _copy_clean(src, dst, report, suf):
    if suf in ('.csv', '.tsv'):
        csv.field_size_limit(sys.maxsize)
        with open(src, newline='', encoding='utf-8', errors='replace') as f:
            rows = list(csv.reader(f, delimiter='\t' if suf == '.tsv' else ','))
        if rows:
            keep = [i for i, c in enumerate(rows[0]) if not banned(c)]
            gone = [c for i, c in enumerate(rows[0]) if i not in keep]
            if gone:
                report['dropped_columns'][str(dst)] = gone
                rows = [[r[i] for i in keep if i < len(r)] for r in rows]
            rows = [[redact(c) for c in r] for r in rows]
        with open(dst, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter='\t' if suf == '.tsv' else ',', lineterminator='\n').writerows(rows)
    elif suf == '.json':
        try:
            data = json.loads(src.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            dst.write_text(redact(src.read_text(encoding='utf-8', errors='replace')), encoding='utf-8')
            return
        dropped = set()
        data = drop_keys(data, dropped)
        if dropped:
            report['dropped_keys'][str(dst)] = sorted(dropped)
        dst.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    elif suf == '.jsonl':
        dropped, lines = set(), []
        for line in src.read_text(encoding='utf-8').splitlines():
            try:
                lines.append(json.dumps(drop_keys(json.loads(line), dropped), ensure_ascii=False))
            except json.JSONDecodeError:
                continue   # a line cut short when a run was stopped
        if dropped:
            report['dropped_keys'][str(dst)] = sorted(dropped)
        dst.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    elif suf in TEXT_SUFFIX:
        dst.write_text(redact(src.read_text(encoding='utf-8', errors='replace')), encoding='utf-8')
    else:
        shutil.copy2(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('draft')
    ap.add_argument('team')
    ap.add_argument('out')
    ap.add_argument('--rerun-results', nargs='*', default=[])
    ap.add_argument('--benchmark-results', default='')
    ap.add_argument('--arxiv', default='')
    ap.add_argument('--journal-doi', default='')
    ap.add_argument('--no-split', action='store_true')
    a = ap.parse_args()
    D, T, O = Path(a.draft).resolve(), Path(a.team).resolve(), Path(a.out).resolve()
    if O.exists():
        sys.exit(f'STOP: {O} exists; give a new folder')
    O.mkdir(parents=True)
    report = dict(copied=0, skipped=[], dropped_columns={}, dropped_keys={}, missing=[], split=[], problems=[])
    roots = {'D': D, 'T': T}
    for key, pattern, dest in SPEC:
        base = roots[key]
        hits = [p for p in base.glob(pattern) if p.is_file()]
        if not hits:
            report['missing'].append(f'{key}:{pattern}')
        stem = pattern.split('*')[0].rsplit('/', 1)[0] if '*' in pattern else str(Path(pattern).parent)
        for p in sorted(hits):
            rel = p.relative_to(base).as_posix()
            if any(x.search(rel) for x in EXCLUDE) or any(SKIP_NAME.search(part) for part in p.parts):
                report['skipped'].append(rel + ' (excluded)')
                continue
            if p.suffix.lower() in SKIP_SUFFIX:
                report['skipped'].append(rel + f' ({p.suffix} not deposited)')
                continue
            sub = p.relative_to(base / stem) if stem not in ('', '.') else p.relative_to(base)
            copy_clean(p, O / dest / sub, report)
            report['copied'] += 1
    for d in a.rerun_results:   # v0.30 (D56): the outputs of TabPFN-3.5 stay out of the deposit
        if any(TABPFN_CELL in p.read_bytes() for p in Path(d).glob('**/*.jsonl')):
            sys.exit(f'STOP: {d} holds cells of TabPFN-3.5, whose outputs are not deposited (D56); give the rerun\'s own '
                     'result folders only')
    for i, d in enumerate(a.rerun_results):
        for p in sorted(Path(d).glob('**/*')):
            if p.is_file() and p.suffix.lower() in ('.jsonl', '.json', '.csv', '.log', '.md'):
                if p.suffix.lower() == '.log':
                    dst = O / 'benchmark' / 'rerun42_per_fold' / Path(d).name / p.relative_to(d).with_suffix('.log.txt')
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(redact(p.read_text(encoding='utf-8', errors='replace')), encoding='utf-8')
                else:
                    copy_clean(p, O / 'benchmark' / 'rerun42_per_fold' / Path(d).name / p.relative_to(d), report)
                report['copied'] += 1
    if a.benchmark_results:
        for p in sorted(Path(a.benchmark_results).glob('**/*')):
            if p.is_file() and p.suffix.lower() in ('.jsonl', '.json', '.csv'):
                copy_clean(p, O / 'benchmark' / 'per_fold' / p.relative_to(a.benchmark_results), report)
                report['copied'] += 1
    else:
        report['missing'].append('per-fold results of the benchmark of Appendix F (on the MacBook): --benchmark-results')
    if not a.rerun_results:
        report['missing'].append('per-fold results of the rerun (cloud and MacBook archives): --rerun-results')
    write_texts(O, a)
    home_names = redact_home(O, report)
    scan(O, report, a.no_split, home_names)
    manifest(O)
    report['emails_redacted'] = REDACTED[0]
    report['names_replaced'] = ANON[0]   # v0.38
    (O / 'BUILD_REPORT.json').write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding='utf-8')
    size = sum(p.stat().st_size for p in O.rglob('*') if p.is_file())
    print(f"copied {report['copied']} files ({size / 1e6:.1f} MB); dropped columns in {len(report['dropped_columns'])} files, "
          f"keys in {len(report['dropped_keys'])}; skipped {len(report['skipped'])}; missing {len(report['missing'])}; "
          f"split {len(report['split'])}; problems {len(report['problems'])}")
    if report['problems']:
        print('STOP: problems found:', *report['problems'][:20], sep='\n  ')
        sys.exit(1)


def write_texts(O, a):
    cite_paper = (f'arXiv:{a.arxiv}' if a.arxiv else 'arXiv preprint (identifier to be added when it is posted)')
    journal = f'https://doi.org/{a.journal_doi}' if a.journal_doi else 'to be added when the paper is published'
    names = ', '.join(f'{g} {f}' for f, g, _ in AUTHORS)
    (O / 'README.md').write_text(f"""# SMOTE25: data and code for "{TITLE}"

{names} (Department of Statistics, Faculty of Science, {AFFIL}).

This deposit holds the data and code behind the survey: the coding sheets of the three extractions (with the second
pass and its adjudication), the scripts that build every table and figure of the paper and of its online appendix
and the number ledger, the search strings, run times, counts and request logs, the identifiers of every record of the
systematic search with each screening decision and code, the OpenAlex snapshot of the reach analysis, the codebooks
and instructions, the codes of the two samples of the systematic search (the coverage sample and the use audit) with
their blind second coding and its adjudication, the PubMed identifiers of the harm search with their decisions and
codes, and the code and per-fold results of the benchmark and of the rerun on the reference collection, with the five
re-implementations and their validations. In the records of the authors' checks (the spot checks of the adjudications
and the log of the papers obtained through the library), each author's name is replaced by "an author".
`MANIFEST.tsv` lists every file with its size and SHA-256.

**Not included.** The abstracts of the records (the Scopus export is licensed content), the full texts of the papers,
the passages quoted from them (the `quote`, `evidence` and similar columns were removed, and the adjudicators' reasons
are left out; `BUILD_REPORT.json` lists every removed column), the data files of the benchmark tasks (each comes from the source its notes give), the
screening and check workbooks, and the model TabPFN-3.5 with its outputs: the results of the TabPFN arm of the rerun,
per fold or averaged, are not included, as the authors decided, because the model's license lets its outputs be used
for non-commercial purposes only, while the data of this deposit carry CC BY 4.0. The scripts of the arm are included.

## How to cite

Please cite the paper: {names}. {TITLE}. {cite_paper}. Journal version: {journal}.
To cite these files: {names}. SMOTE25: data and code for "{TITLE}". Zenodo, https://doi.org/{DOI}. The same
files are in the GitHub repository {REPO}.

## Licenses

Data: CC BY 4.0 (`LICENSE-DATA.md`). Code: MIT (`LICENSE-CODE`).
""", encoding='utf-8')
    cff = ['cff-version: 1.2.0', 'message: "Please cite the paper, and these files with their DOI."',
           f'title: "SMOTE25: data and code for \\"{TITLE}\\""', 'type: dataset', f'doi: {DOI}',
           f'repository-code: "{REPO}"', 'license: CC-BY-4.0', 'authors:']
    for f, g, orcid in AUTHORS:
        cff += [f'  - family-names: "{f}"', f'    given-names: "{g}"', f'    affiliation: "{AFFIL}"']
        if orcid:
            cff.append(f'    orcid: "https://orcid.org/{orcid}"')
    cff += ['preferred-citation:', '  type: article', f'  title: "{TITLE}"', '  authors:']
    for f, g, orcid in AUTHORS:
        cff += [f'    - family-names: "{f}"', f'      given-names: "{g}"']
    if a.journal_doi:
        cff.append(f'  doi: "{a.journal_doi}"')
    elif a.arxiv:
        cff += ['  identifiers:', '    - type: other', f'      value: "arXiv:{a.arxiv}"']
    (O / 'CITATION.cff').write_text('\n'.join(cff) + '\n', encoding='utf-8')
    (O / 'LICENSE-DATA.md').write_text(
        'The data of this deposit are licensed under the Creative Commons Attribution 4.0 International license '
        '(CC BY 4.0): https://creativecommons.org/licenses/by/4.0/legalcode\n', encoding='utf-8')
    (O / 'LICENSE-CODE').write_text(f"""MIT License

Copyright (c) 2026 {names}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""", encoding='utf-8')


def scan(O, report, no_split, home_names=()):
    secrets = [s for s in (os.environ.get('ZENODO_TOKEN', ''), os.environ.get('OPENALEX_API_KEY', ''),
                           os.environ.get('TABPFN_TOKEN', '')) if len(s) >= 16]
    pat = re.compile(rb'(api_key=[A-Za-z0-9]{8,}|[A-Za-z0-9._%+-]+@gmail\.com)')
    for p in sorted(O.rglob('*')):
        if not p.is_file():
            continue
        rel = p.relative_to(O).as_posix()
        if p.suffix.lower() in ('.xlsx', '.xls'):
            report['problems'].append(f'{rel}: spreadsheet')
        b = p.read_bytes()
        for s in secrets:
            if s.encode() in b:
                report['problems'].append(f'{rel}: holds an access token')
        m = pat.search(b)
        if m:
            report['problems'].append(f'{rel}: {m.group(0)[:40]!r}')
        if rel != 'paper_scripts/scripts/build_deposit.py' and any(
                h.group(2) not in (b'USER', b'Shared') for h in HOME_PATH.finditer(b)) or any(n.encode() in b for n in home_names):
            report['problems'].append(f'{rel}: holds the path or the account name of a machine')
        if TABPFN_CELL in b:   # v0.30 (D56): no cell of TabPFN-3.5 in the deposit
            report['problems'].append(f'{rel}: holds cells of TabPFN-3.5 (D56)')
        if CHECK_RECORD.search(p.name) and NAME_RE.search(b.decode('utf-8', 'replace')):   # v0.38
            report['problems'].append(f'{rel}: a check record names an author')
        if p.suffix.lower() in ('.csv', '.tsv'):
            head = b.split(b'\n', 1)[0].decode('utf-8', 'replace').lower()
            with open(p, newline='', encoding='utf-8', errors='replace') as fh:
                rd = csv.reader(fh, delimiter='\t' if p.suffix.lower() == '.tsv' else ',')
                cols = next(rd, [])
                if 'learner' in cols:   # v0.30 (D56): no result of TabPFN-3.5, per fold or averaged
                    j = cols.index('learner')
                    if any(len(r) > j and r[j] == 'TabPFN' for r in rd):
                        report['problems'].append(f'{rel}: holds results of TabPFN-3.5 (D56)')
            left = [c for c in cols if banned(c)]
            if left:
                report['problems'].append(f'{rel}: banned column left {left}')
        if len(b) > LIMIT:
            if no_split:
                report['problems'].append(f'{rel}: over 100 MB')
            else:
                n = 0
                for i in range(0, len(b), LIMIT - (1 << 20)):
                    n += 1
                    (p.parent / f'{p.name}.part{n:02d}').write_bytes(b[i:i + LIMIT - (1 << 20)])
                (p.parent / f'{p.name}.JOIN.txt').write_text(f'cat {p.name}.part* > {p.name}\n', encoding='utf-8')
                p.unlink()
                report['split'].append(f'{rel}: {n} parts')


def manifest(O):
    rows = [('path', 'bytes', 'sha256')]
    for p in sorted(O.rglob('*')):
        if p.is_file() and p.name not in ('MANIFEST.tsv', 'BUILD_REPORT.json'):
            rows.append((p.relative_to(O).as_posix(), str(p.stat().st_size), sha(p)))
    with open(O / 'MANIFEST.tsv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f, delimiter='\t', lineterminator='\n').writerows(rows)


if __name__ == '__main__':
    main()
