#!/usr/bin/env python3
"""Convert the Method section's generated table (make_tex.py output) into the
rows of Table 3 of the integrated draft (gen/table_methods_rows.tex).

The integrated draft must not be edited by hand where it is generated: change the
Method Map or the Method scripts, run them, then run this converter.
Usage:
  python3 scripts/gen_methods_rows.py "<team-repo>/Method section/manuscript/generated/smote-family-table.tex" gen/table_methods_rows.tex
Check: converting the table committed on 10 Nov 2026 (git ec78e2a) reproduces the
v0.1 rows byte for byte (see the v0.2 handoff).
"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding='utf-8').splitlines()
out = []
started = False
for line in src:
    s = line.strip()
    if not started:
        if s == r'\midrule':
            started = True
        continue
    if s == r'\end{tabular}':
        break
    if s == r'\addlinespace':
        out.append(r'\midrule')
        continue
    s = re.sub(r'~\\(?:pcite|parencite)\{([^}]+)\}', r' \\citep{\1}', s)
    s = s.replace(r'\fm', r'$\bullet$')
    s = re.sub(r'\$\+(\.\d+)\$', r'+\1', s)
    s = re.sub(r'\$-(\.\d+)\$', r'$-$\1', s)
    s = s.replace(r'$^{\dagger}$', r'$^\dagger$')
    out.append(s)
Path(sys.argv[2]).write_text('\n'.join(out) + '\n', encoding='utf-8')
print(f'wrote {sys.argv[2]} ({len(out)} lines)')
