#!/usr/bin/env python3
"""Build the arXiv source package of the paper from its JAIR build (v0.38, 17 Nov 2026; Last Pass decision d_arxiv:
a preprint on arXiv at submission, posted by an author).

The preprint is the JAIR manuscript without the review options and without the template's journal footer and running
head, whose volume, article number and date are placeholders that JAIR sets on acceptance: the document class becomes
[manuscript, screen, nonacm] and every page carries only its number. Nothing else changes. arXiv does not run biber, so
the package holds the main.bbl that biber made here (TeX Live 2023, biblatex bbl format 3.2); if arXiv rejects it as the
wrong format version, rebuild main.bbl with arXiv's TeX Live version. The online appendix goes in as an ancillary file
(anc/). The script compiles the package from scratch with pdflatex alone, as arXiv does, and stops if that fails.

Usage: python3 -I scripts/make_arxiv.py <jair build dir> <online appendix pdf> <out dir>
Writes <out dir>/SMOTE25_arXiv_source.tar.gz, <out dir>/SMOTE25_arXiv_preview.pdf and <out dir>/README.md.
"""
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

J, SUPP, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
CLASS_OLD = '\\documentclass[manuscript, screen, review]{jair}'
CLASS_NEW = '\\documentclass[manuscript, screen, nonacm]{jair}'
STYLE = ('% arXiv preprint: no line numbers, and no journal footer or running head of the JAIR template, whose\n'
         '% volume, article number and date are placeholders set by JAIR; page numbers only.\n'
         '\\AtBeginDocument{%\n'
         '  \\fancypagestyle{standardpagestyle}{\\fancyhf{}\\fancyfoot[C]{\\footnotesize\\thepage}\\renewcommand\\headrulewidth{0pt}}%\n'
         '  \\fancypagestyle{firstpagestyle}{\\fancyhf{}\\fancyfoot[C]{\\footnotesize\\thepage}\\renewcommand\\headrulewidth{0pt}}%\n'
         '  \\pagestyle{standardpagestyle}}\n')


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


with tempfile.TemporaryDirectory() as tmp:
    B = Path(tmp) / 'build'
    B.mkdir()
    for n in ('main.tex', 'references.bib', 'jair.cls', 'acmart.cls', 'acmauthoryear.bbx', 'acmauthoryear.cbx',
              'acmdatamodel.dbx'):
        shutil.copy2(J / n, B / n)
    for d in ('sec', 'gen', 'figures'):
        shutil.copytree(J / d, B / d)
    tex = (B / 'main.tex').read_text(encoding='utf-8')
    lines = tex.split('\n')
    hits = [i for i, l in enumerate(lines) if l.strip() == CLASS_OLD]   # the class line itself, not the header comment
    assert len(hits) == 1 and tex.count('\\begin{document}') == 1, 'STOP: the JAIR main.tex is not as expected'
    lines[hits[0]] = CLASS_NEW
    tex = '\n'.join(lines).replace('\\begin{document}', STYLE + '\\begin{document}')
    (B / 'main.tex').write_text(tex, encoding='utf-8')
    r = run(['latexmk', '-pdf', '-interaction=nonstopmode', 'main.tex'], B)
    if not (B / 'main.pdf').exists() or 'undefined' in (B / 'main.log').read_text(errors='replace').lower().replace('undefined control', ''):
        sys.exit('STOP: the preprint build failed or left undefined references:\n' + r.stdout[-2000:])
    # the files the build read, from its .fls
    used = sorted({line[6:].strip()[2:] if line[6:].strip().startswith('./') else line[6:].strip()
                   for line in (B / 'main.fls').read_text().splitlines()
                   if line.startswith('INPUT ') and not line[6:].strip().startswith('/')})
    used = [u for u in used if not re.search(r'\.(aux|out|bcf|run\.xml|toc|fls|log)$', u)]
    P = Path(tmp) / 'pkg'
    for u in used + ['main.tex', 'main.bbl']:
        (P / u).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(B / u, P / u)
    (P / 'anc').mkdir(exist_ok=True)
    shutil.copy2(SUPP, P / 'anc' / 'SMOTE25_online_appendix.pdf')
    # compile the package as arXiv does: pdflatex only, with the shipped .bbl
    T = Path(tmp) / 'test'
    shutil.copytree(P, T)
    for _ in range(3):
        r = run(['pdflatex', '-interaction=nonstopmode', 'main'], T)
    log = (T / 'main.log').read_text(errors='replace')
    if not (T / 'main.pdf').exists() or re.search(r'(Citation|Reference) .* undefined', log):
        sys.exit('STOP: the package does not compile from scratch with pdflatex:\n' + r.stdout[-2000:])
    OUT.mkdir(parents=True, exist_ok=True)
    with tarfile.open(OUT / 'SMOTE25_arXiv_source.tar.gz', 'w:gz') as tf:
        for p in sorted(P.rglob('*')):
            if p.is_file():
                tf.add(p, arcname=p.relative_to(P).as_posix())
    shutil.copy2(T / 'main.pdf', OUT / 'SMOTE25_arXiv_preview.pdf')
    n_files = sum(1 for p in P.rglob('*') if p.is_file())
# v0.49: the abstract as plain text for arXiv's form (docs/ABSTRACT.txt, written by scripts/abstract_plain.py)
_abs = Path(__file__).resolve().parent.parent / 'docs' / 'ABSTRACT.txt'
_abstract = ''
if _abs.exists():
    _a = _abs.read_text(encoding='utf-8').strip()
    _abstract = (f"\n## Abstract for the arXiv form ({len(_a):,} characters; arXiv takes 1,920)\n\n"
                 f"Paste it as it is; the same text is in `docs/ABSTRACT.txt` and `docs/SUBMISSION_FORM.md`.\n\n{_a}\n")
(OUT / 'README.md').write_text(f"""# arXiv preprint: source package

`SMOTE25_arXiv_source.tar.gz` ({n_files} files) is the paper's source for arXiv, built by `scripts/make_arxiv.py` from
the JAIR build. It is the JAIR manuscript without line numbers and without the template's journal footer and running
head (their volume, article number and date are placeholders); nothing else differs. `SMOTE25_arXiv_preview.pdf` is
what arXiv should produce: the package was compiled from scratch with pdflatex alone, as arXiv does.

How to post (an author, at submission to JAIR): on arxiv.org choose Submit, upload the .tar.gz as is, choose the
category (suggested: cs.LG, cross-list stat.ML), license CC BY 4.0 (as the paper's own), and in Comments write the
page count and, if wanted, "Submitted to the Journal of Artificial Intelligence Research". The online appendix is in
`anc/` and arXiv lists it as an ancillary file. arXiv does not run biber; the package carries `main.bbl` made with
TeX Live 2023 (biblatex bbl format 3.2). If arXiv reports that main.bbl has the wrong format version, a session
rebuilds it for arXiv's TeX Live. When the identifier is known, a session adds it to the deposit
(`scripts/build_deposit.py --arxiv ID`: README and CITATION.cff).
""" + _abstract, encoding='utf-8')
print(f'wrote {OUT}/SMOTE25_arXiv_source.tar.gz ({n_files} files) and the preview')
