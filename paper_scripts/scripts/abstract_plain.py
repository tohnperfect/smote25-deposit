#!/usr/bin/env python3
"""v0.49: the abstract as plain text, for the arXiv and JAIR forms. Reads main.tex, writes docs/ABSTRACT.txt and the
block between <!--abstract--> and <!--/abstract--> of docs/SUBMISSION_FORM.md, and stops if the text is longer than
arXiv's limit of 1,920 characters. scripts/make_arxiv.py copies docs/ABSTRACT.txt into arxiv/README.md.
Usage: python3 -I scripts/abstract_plain.py DRAFT_DIR"""
import re
import sys
from pathlib import Path

R = Path(sys.argv[1])
LIMIT = 1920
t = (R / 'main.tex').read_text(encoding='utf-8')
a = t[t.index('\\begin{abstract}') + len('\\begin{abstract}'):t.index('\\end{abstract}')]
a = re.sub(r'%[<>]{2}search:\w+\n', '', a)
a = re.sub(r'\\src\{[^}]*\}\{[^}]*\}', '', a).replace('\\noindent', '')
a = re.sub(r'\\textbf\{([^}]*)\}', r'\1', a).replace('\\%', '%')
a = ' '.join(a.split())
if '\\' in a or '{' in a or '$' in a:
    sys.exit('STOP: LaTeX left in the plain abstract: ' + a)
if len(a) > LIMIT:
    sys.exit(f'STOP: the abstract has {len(a)} characters; arXiv takes {LIMIT}')
(R / 'docs/ABSTRACT.txt').write_text(a + '\n', encoding='utf-8')
form = R / 'docs/SUBMISSION_FORM.md'
f = form.read_text(encoding='utf-8')
block = (f'<!--abstract-->\n## Abstract (plain text for the JAIR and arXiv forms: {len(a):,} characters, {len(a.split())} '
         f'words; arXiv takes {LIMIT:,} characters)\n\nWritten by `scripts/abstract_plain.py` from `main.tex`; the same text is in '
         f'`docs/ABSTRACT.txt` and `arxiv/README.md`.\n\n{a}\n<!--/abstract-->')
if '<!--abstract-->' in f:
    f = re.sub(r'<!--abstract-->.*?<!--/abstract-->', lambda m: block, f, flags=re.S)
else:
    f = f.replace('## Importance (', block + '\n\n## Importance (', 1)
form.write_text(f, encoding='utf-8')
print(f'abstract: {len(a)} characters, {len(a.split())} words')
