#!/usr/bin/env python3
"""Flatten main.tex (+ sec/*.tex, gen/*.tex) into one file for the project.

Every \\input{X} is replaced by its file, wrapped in
'% ---- begin X ----' / '% ---- end X ----' markers, the same layout as
claude/smote25-integrated-draft-v0.1.tex. Usage:
    python3 scripts/flatten.py main.tex out.tex
"""
import re
import sys
from pathlib import Path

INPUT = re.compile(r'^\\input\{([^}]+)\}\s*$')


def expand(path: Path, root: Path) -> str:
    out = []
    for line in path.read_text(encoding='utf-8').splitlines(keepends=True):
        m = INPUT.match(line.strip())
        if m:
            name = m.group(1)
            sub = root / (name if name.endswith('.tex') else name + '.tex')
            body = expand(sub, root)
            if not body.endswith('\n'):
                body += '\n'
            out.append(f'% ---- begin {name} ----\n{body}% ---- end {name} ----\n')
        else:
            out.append(line)
    return ''.join(out)


def main():
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2])
    dst.write_text(expand(src, src.parent), encoding='utf-8')
    print(f'wrote {dst} ({dst.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
