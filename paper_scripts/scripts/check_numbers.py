#!/usr/bin/env python3
"""Check that every number in a paragraph tagged D, M or E occurs in the PDF
it is attributed to (rebuilt in v0.2 because the v0.1 script was not in the
project; same purpose as scripts/check_numbers.py of the v0.1 zip).

A block runs from one \\src{X}{ref} tag to the next. Citations, labels,
cross-references and [Team: ...] notes are removed first, because they are
not text copied from a section PDF. Numbers are compared after removing
thousands separators. The check proves that a number occurs in the PDF, not
that it is used in the right sentence: read the sentence as well.

Usage: python3 scripts/check_numbers.py [root]   (root holds main.tex, sec/, gen/, src/)
Needs src/data.txt, src/method.txt, src/eval.txt made with pdftotext -layout.
Exit code 0 when every number is found; prints one line per miss.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
PDFTXT = {'D': 'data.txt', 'M': 'method.txt', 'E': 'eval.txt'}

STRIP = [
    (re.compile(r'\\team\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'), ' '),
    (re.compile(r'\\cite[pt]?\*?(\[[^\]]*\])*\{[^}]*\}'), ' '),
    (re.compile(r'\\(?:text|paren)?cite[a-z]*\*?(\[[^\]]*\])*\{[^}]*\}'), ' '),
    (re.compile(r'\\(?:label|ref|eqref|pageref|includegraphics)(\[[^\]]*\])?\{[^}]*\}'), ' '),
    (re.compile(r'\\(?:begin|end)\{[^}]*\}(\{[^}]*\})*'), ' '),
    (re.compile(r'\\(?:L|p)\{[^}]*\}'), ' '),
    (re.compile(r'\\hskip\s*[0-9.]+pt'), ' '),
    (re.compile(r'\\setlength\{[^}]*\}\{[^}]*\}'), ' '),
    (re.compile(r'\\multicolumn\{\d+\}\{[^}]*\}'), ' '),
    (re.compile(r'\\cmidrule(\([a-z]*\))?\{[^}]*\}'), ' '),   # v0.5: column ranges of a rule
    (re.compile(r'\{[lrcLY@{}\s0-9.ptX]*\}'), ' '),
]
NUM = re.compile(r'(?<![A-Za-z0-9_])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?![A-Za-z0-9_])')
TAG = re.compile(r'\\src\{([DMEPSRA])\}\{([^}]*)\}')   # v0.18: A = approved S or R (ref: the earlier tag)


def norm_pdf(text: str) -> str:
    text = re.sub(r'(?<=\d),(?=\d{3})', '', text)
    text = text.replace('\u2212', '-').replace('\u2013', '-').replace('\u2014', '-')
    return text


def numbers(block: str):
    for pat, rep in STRIP:
        block = pat.sub(rep, block)
    block = block.replace('\\%', '%').replace('$-$', '-')
    for m in NUM.finditer(block):
        tok = m.group(0)
        if not re.search(r'\d', tok):
            continue
        tok = tok.lstrip('+').replace(',', '')
        if tok.startswith('-'):
            tok = tok[1:]
        yield tok


def found(tok: str, pdf: str) -> bool:
    variants = {tok}
    if tok.startswith('0.'):
        variants.add(tok[1:])          # 0.29 printed as .29
    if tok.startswith('.'):
        variants.add('0' + tok)
    if re.fullmatch(r'\d+\.\d*0', tok):
        variants.add(tok.rstrip('0').rstrip('.'))
    for v in variants:
        if re.search(r'(?<![0-9])' + re.escape(v) + r'(?![0-9])', pdf):
            return True
    return False


def adjudicated():
    """v0.16: numbers changed on purpose by the WP3 adjudication and decisions D34 to D36 (scripts/adjudicated_numbers.json).
    A number of a D, M or E block that is not in the section PDF is accepted when an entry lists it and the entry's marker
    occurs in the same block; it is reported apart, with its source."""
    import json
    f = ROOT / 'scripts' / 'adjudicated_numbers.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else []


def main():
    texts = {k: norm_pdf((ROOT / 'src' / f).read_text(encoding='utf-8', errors='ignore'))
             for k, f in PDFTXT.items()}
    adj = adjudicated()
    changed = []
    files = [ROOT / 'main.tex'] + sorted((ROOT / 'sec').glob('*.tex'))
    full = ''
    for f in files:
        t = f.read_text(encoding='utf-8')
        # inline the generated rows at their \input so that they inherit the caption tag of their table
        t = re.sub(r'\\input\{(gen/[^}]+)\}',
                   lambda m: (ROOT / (m.group(1) + '.tex')).read_text(encoding='utf-8'), t)
        full += f'\n%%FILE {f.name}\n' + t
    full = re.sub(r'(?m)^%.*$', '', full)
    parts = TAG.split(full)
    checked = misses = 0
    report = []
    # parts: [pre, tag, ref, text, tag, ref, text, ...]
    for i in range(1, len(parts), 3):
        tag, ref, text = parts[i], parts[i + 1], parts[i + 2]
        if tag not in PDFTXT:
            continue
        for tok in numbers(text):
            checked += 1
            if not found(tok, texts[tag]):
                hit = [e for e in adj if tok in e['values'] and e['marker'] in text]
                if hit:
                    changed.append(f'{tag} {ref:<14} {tok:<10} | {hit[0]["source"]} ({hit[0]["note"]})')
                    continue
                misses += 1
                snippet = re.sub(r'\s+', ' ', text.strip())[:90]
                report.append(f'{tag} {ref:<14} {tok:<10} | {snippet}')
    print(f'numbers checked in D/M/E blocks: {checked}; not found in the attributed PDF: {misses}; '
          f'changed on purpose with a registered source (scripts/adjudicated_numbers.json): {len(changed)}')
    for line in changed:
        print('  changed: ' + line)
    for line in report:
        print('  ' + line)
    return 0 if misses == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
