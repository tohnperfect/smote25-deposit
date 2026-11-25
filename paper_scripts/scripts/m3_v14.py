#!/usr/bin/env python3
"""M3 (length), draft v0.14: move reference material from the paper's appendices to the online appendix.

Moves (the generated tables stay generated; the online appendix inputs the same files from ../gen/):
  Appendix D, candidate benchmarks, with its full-page table      -> online appendix S8
  Appendix E, model variants of the data analyses, with its table -> online appendix S9
  the table of the nested tier of the benchmark (Appendix F)      -> online appendix S10 (the text stays in F)
  Appendix G, the OpenAlex queries                                -> online appendix S4, a subsection
The references in the paper point to the online appendix by section number (S4, S8, S9, S10), as the paper's other
references to it do; the build checks the numbers (check_supp_sections in this script, run after the builds).
Usage: python3 -I m3_v14.py <draft dir>          (edits the sources once; refuses to run twice)
       python3 -I m3_v14.py <draft dir> --check  (after the builds: the online appendix numbers its sections as cited)
"""
import re
import sys
from pathlib import Path

D = Path(sys.argv[1])


def edit(rel, pairs):
    p = D / rel
    s = p.read_text(encoding='utf-8')
    for old, new in pairs:
        n = s.count(old)
        if n != 1:
            sys.exit(f'{rel}: expected one match, found {n}: {old[:80]!r}')
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')


def cut(rel, start, end, keep_end=True):
    """Remove the text from `start` up to `end` (end kept when keep_end)."""
    p = D / rel
    s = p.read_text(encoding='utf-8')
    i, j = s.find(start), s.find(end)
    if i < 0 or j < 0 or j < i or s.count(start) != 1:
        sys.exit(f'{rel}: block not found: {start[:60]!r}')
    removed = s[i:j]
    p.write_text(s[:i] + (s[j:] if keep_end else s[j + len(end):]), encoding='utf-8')
    return removed


if '--check' in sys.argv:
    aux = (D / 'supplement' / 'supplement.aux').read_text(encoding='utf-8')
    want = {'supp:search': 'S4', 'supp:candidates': 'S8', 'supp:models': 'S9', 'supp:nested': 'S10',
            'supp:consistency': 'S11'}   # v0.40: Table 5 and the detail of the second pass
    bad = []
    for lab, num in want.items():
        m = re.search(r'\\newlabel\{' + re.escape(lab) + r'\}\{\{([^}]*)\}', aux)
        if not m or m.group(1) != num:
            bad.append(f'{lab}: {m.group(1) if m else "missing"} (cited as {num})')
    if bad:
        sys.exit('online appendix numbers differ from the paper: ' + '; '.join(bad))
    print('online appendix sections as cited:', ', '.join(f'{k} {v}' for k, v in want.items()))
    sys.exit(0)

app = (D / 'sec' / '11-appendix.tex').read_text(encoding='utf-8')
if 'app:candidates' not in app:
    sys.exit('already applied (no Appendix D in sec/11-appendix.tex)')

# ---- the paper -------------------------------------------------------------------------------------------------
moved_dE = cut('sec/11-appendix.tex', '\\section{Candidate Benchmarks for a Cross-Family Comparison}',
               '\\section{Independent Benchmark}')
assert 'tab:candidates' in moved_dE and 'tab:modelvariants' in moved_dE
nested_start = '\\begin{table}[tp]\n\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\n\\caption{\\src{S}{}Nested tier'
moved_nested = cut('sec/11-appendix.tex', nested_start, '%<<search:i_rerun_app')
assert 'tab:benchnested' in moved_nested
moved_G = cut('sec/11-appendix.tex', '\\section{OpenAlex Queries}', '\\section{Reproducibility Checklist}')
assert 'W2148143831' in moved_G
edit('sec/11-appendix.tex', [
    ('Table~\\ref{tab:benchnested} gives the medians.', 'The online appendix (Section~S10) gives the medians.'),
])
edit('sec/03-method.tex', [
    ('Appendix~\\ref{app:openalex} lists the queries.', 'The online appendix (Section~S4) lists the queries.'),
])
edit('sec/05-data.tex', [
    ('Appendix~\\ref{app:candidates} lists every dataset that two written rules select',
     'The online appendix (Section~S8) lists every dataset that two written rules select'),
    ('Table~\\ref{tab:modelvariants} in Appendix~\\ref{app:models} lists every model variant.',
     'the online appendix (Section~S9) lists every model variant.'),
    ('within papers; Table~\\ref{tab:modelvariants})', 'within papers; online appendix, Section~S9)'),
])
edit('sec/12-checklist.tex', [
    ('use clustered models (Appendix~\\ref{app:models})', 'use clustered models (online appendix, Section~S9)'),
    ('Answers describe v0.13.', 'Answers describe v0.14.'),
])
edit('main.tex', [
    ('% Integrated draft v0.13 (12 Nov 2026)', '% Integrated draft v0.14 (12 Nov 2026)'),
    ('Integrated draft v0.13, 12 November 2026', 'Integrated draft v0.14, 12 November 2026'),
])
for rel in ('sec/11-appendix.tex', 'sec/03-method.tex', 'sec/05-data.tex', 'sec/12-checklist.tex'):
    s = (D / rel).read_text(encoding='utf-8')
    for lab in ('app:candidates', 'tab:candidates', 'app:models', 'tab:modelvariants', 'tab:benchnested', 'app:openalex'):
        if lab in s:
            sys.exit(f'{rel} still refers to {lab}')


# ---- the online appendix -----------------------------------------------------------------------------------------
def unsrc(s):
    return re.sub(r'\\src\{[A-Z]\}\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', s)


cand_text = re.search(r'\\label\{app:candidates\}\n\n(.*?)\n\n\\begin\{table\}', moved_dE, re.S).group(1)
cand_part = moved_dE[:moved_dE.index('\\label{app:models}')]
cand_caption = re.search(r'\\caption\{(.*?)\}\n\\label\{tab:candidates\}', cand_part, re.S).group(1)
assert '\\section' not in cand_caption
cand_tabular = re.search(r'(\\begin\{tabular\}\{llrrrrrl\}.*?\\end\{tabular\})', moved_dE, re.S).group(1)
mv_text = re.search(r'\\label\{app:models\}\n\n(.*?)\n\n\\begin\{table\}', moved_dE, re.S).group(1)
mv_part = moved_dE[moved_dE.index('\\label{app:models}'):]  # search the captions inside each part only
mv_caption = re.search(r'\\caption\{(.*?)\}\n\\label\{tab:modelvariants\}', mv_part, re.S).group(1)
mv_tabular = re.search(r'(\\begin\{tabular\}\{L\{3\.3cm\}.*?\\end\{tabular\})', mv_part, re.S).group(1)
assert '\\section' not in mv_caption and '\\label' not in mv_caption
ne_caption = re.search(r'\\caption\{(.*?)\}\n\\label\{tab:benchnested\}', moved_nested, re.S).group(1)
ne_tabular = re.search(r'(\\begin\{tabular\}\{lrrrrrrrr\}.*?\\end\{tabular\})', moved_nested, re.S).group(1)
oa_text = re.search(r'\\label\{app:openalex\}\n\n(.*?)\n\n', moved_G + '\n\n', re.S).group(1)


def to_supp(s):
    s = unsrc(s)
    s = s.replace('\\input{gen/', '\\input{../gen/')
    s = s.replace('Section~\\ref{sec:wins}', 'Section~\\ref*{P-sec:wins} of the paper')
    s = s.replace('Section~\\ref{sec:reach}', 'Section~\\ref*{P-sec:reach} of the paper')
    s = s.replace('Section~\\ref{sec:whychanged}', 'Section~\\ref*{P-sec:whychanged} of the paper')
    s = s.replace('Table~\\ref{tab:benchcore}', 'Table~\\ref*{P-tab:benchcore} of the paper')
    s = s.replace('Table~\\ref{tab:modelvariants}', 'Table~\\ref{supp:modelvariants}')
    s = s.replace('Section~S4 of the online appendix lists the files of the snapshot with the time and URL of every request.',
                  'Section~\\ref{supp:snapshot} lists the files of the snapshot with the time and URL of every request.')
    s = s.replace('Generated from \\texttt{Data section/out/benchmark\\_candidates.csv}.',
                  'Generated from \\texttt{Data section/out/benchmark\\_candidates.csv} by \\texttt{scripts/gen\\_benchmark\\_candidates.py}.')
    return s.strip()


for name, s in (('cand_text', cand_text), ('mv_text', mv_text), ('oa_text', oa_text)):
    if re.search(r'\\ref\{(sec|tab|app|fig|eq):', to_supp(s)):
        sys.exit(f'{name}: a reference to the paper is left unconverted')

oa_sub = ('\\subsection{The OpenAlex Queries of the Reach Analysis}\n\\label{supp:openalexq}\n\n' + to_supp(oa_text) + '\n')
new_sections = f"""\\section{{Candidate Benchmarks for a Cross-Family Comparison}}
\\label{{supp:candidates}}

{to_supp(cand_text)} Section~\\ref*{{P-sec:landscape}} of the paper refers to this list.

\\begin{{table}}[htbp]
\\centering\\footnotesize
\\caption{{{to_supp(cand_caption)}}}
\\label{{supp:candtab}}
{to_supp(cand_tabular)}
\\end{{table}}

\\section{{Model Variants of the Data Analyses}}
\\label{{supp:models}}

{to_supp(mv_text)}

\\begin{{table}}[htbp]
\\centering\\footnotesize\\setlength{{\\tabcolsep}}{{4pt}}
\\caption{{{to_supp(mv_caption)}}}
\\label{{supp:modelvariants}}
{to_supp(mv_tabular).replace('L{3.3cm}L{3.3cm}', 'L{3.1cm}L{3.1cm}')}  
\\end{{table}}

\\section{{The Nested Tier of the Independent Benchmark}}
\\label{{supp:nested}}

Appendix~\\ref*{{P-app:benchmark}} of the paper describes the nested tier of the independent benchmark, in which one setting of each of four learners is tuned by an inner cross-validation, and reports its result. Table~\\ref{{supp:benchnested}} gives the median differences from SMOTE for the tuned random forest and gradient boosting.

\\begin{{table}}[htbp]
\\centering\\footnotesize\\setlength{{\\tabcolsep}}{{4pt}}
\\caption{{{to_supp(ne_caption)}}}
\\label{{supp:benchnested}}
{to_supp(ne_tabular)}
\\end{{table}}

"""
edit('supplement/supplement.tex', [
    ('% Draft v0.13 (12 Nov 2026).', '% Draft v0.14 (12 Nov 2026).'),
    ('{\\small Draft v0.13, 12 November 2026}}', '{\\small Draft v0.14, 12 November 2026}}'),
    ('\\renewcommand{\\thetable}{S\\arabic{table}}',
     '\\renewcommand{\\thetable}{S\\arabic{table}}\n\\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}'),
    ('; and Section~\\ref{supp:rerun} the rerun of the methods of the paper\'s recommendation table on the reference collection.',
     '; Section~\\ref{supp:rerun} the rerun of the methods of the paper\'s recommendation table on the reference collection; '
     'Section~\\ref{supp:candidates} the candidate benchmarks for a comparison across method families; Section~\\ref{supp:models} '
     'the model variants of the data analyses; and Section~\\ref{supp:nested} the result of the nested tier of the independent benchmark.'),
    ('the OpenAlex snapshot and what is archived;', 'the OpenAlex queries and snapshot and what is archived;'),
    ('\\input{gen/search}\n\n\\input{gen/snapshot}', '\\input{gen/search}\n\n' + oa_sub + '\n\\input{gen/snapshot}'),
    ('\\input{gen/rerun42}\n\n\\bibliographystyle', '\\input{gen/rerun42}\n\n' + new_sections + '\\bibliographystyle'),
])
edit('scripts/make_supplement.py', [
    ("S.append(f'Every OpenAlex number of Section~\\\\ref*{{P-sec:reach}} and Appendix~\\\\ref*{{P-app:openalex}} of the paper '",
     "S.append(f'Every OpenAlex number of Section~\\\\ref*{{P-sec:reach}} of the paper and of Section~\\\\ref{{supp:openalexq}} '"),
])
edit('scripts/build_ledger.py', [
    ("('main.tex', 'Integrated draft v0.', ('13', '12', '2026')", "('main.tex', 'Integrated draft v0.', ('14', '12', '2026')"),
])
print('moved: Appendix D and E (with their tables), the nested-tier table, Appendix G; references updated')
