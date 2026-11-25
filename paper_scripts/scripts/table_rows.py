#!/usr/bin/env python3
"""Read the rows of a table of the paper from its LaTeX source, by its label, so that a figure drawn from a table of
the authors' drafts plots exactly the numbers the table prints (v0.53)."""
import re
from pathlib import Path


def table_rows(draft, label):
    for f in sorted(Path(draft, 'sec').glob('*.tex')) + [Path(draft, 'supplement', 'supplement.tex')]:
        t = f.read_text(encoding='utf-8')
        i = t.find('\\label{' + label + '}')
        if i < 0:
            continue
        body = t[i:t.index('\\end{tabular', i)]
        body = body[body.index('\\midrule') + len('\\midrule'):]
        rows = []
        for line in body.split('\\\\'):
            line = re.sub(r'\\(midrule|bottomrule|toprule|addlinespace)', '', line).strip()
            if '&' in line:
                rows.append([c.strip() for c in line.split('&')])
        return rows
    raise SystemExit('no table with label ' + label)


def num(s):
    return float(s.replace(',', '').replace('\\%', '').strip())
