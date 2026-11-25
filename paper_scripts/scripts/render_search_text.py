#!/usr/bin/env python3
"""Write the paragraphs that report the screen, the coverage sample and the use audit from their templates (WP4, WP5).

Each template in scripts/search_templates/NAME.tex starts with a line
    % target: sec/FILE.tex
and holds LaTeX with placeholders <<key>> (or <<key|w>>, which prints 0 as "none") for values of data/search/screening_full_2026-11-11/decisions/search_numbers.json.
v0.15: <<?key>>TEXT<</key>> keeps TEXT only when the value of key is not 0, and <<!key>>TEXT<</key>> only when it is 0
(not nested); so a phrase about the unsure records drops out once the final merge (D28) has excluded them.
In the target file the rendered text replaces everything between the lines
    %<<search:NAME   and   %>>search:NAME
so a rerun after a correction of the team (person_overrides.csv) updates every number at once. The script also writes
scripts/search_bench.json: for every rendered number, the file, a marker (the first words of its paragraph), the
value and the key it came from; scripts/build_ledger.py registers these as sourced numbers.
v0.37: `--redraft NAME[,NAME...]` lets the named templates turn approved passages back to S on purpose (a session
redrafted them, for the team lead's final pass); without it, a rendering that would do so stops.
Usage: python3 -I scripts/render_search_text.py DRAFT_DIR [--redraft NAME[,NAME...]]
"""
import json
import re
import sys
from pathlib import Path

ARGS = sys.argv[1:]
REDRAFT = set()
if '--redraft' in ARGS:
    _i = ARGS.index('--redraft')
    REDRAFT = set(ARGS[_i + 1].split(','))
    del ARGS[_i:_i + 2]
R = Path(ARGS[0])
N = json.load(open(R / 'data/search/screening_full_2026-11-11/decisions/search_numbers.json', encoding='utf-8'))
SRC = 'data/search/screening_full_2026-11-11/decisions/search_numbers.json'
bench = []
missing = set()
COND = re.compile(r'<<([?!])([a-zA-Z0-9_]+)>>(.*?)<</\2>>', re.S)


def truthy(v):
    return str(v).replace(',', '').strip() not in ('0', '', 'False', 'false', 'None')


def resolve(text):
    def f(m):
        if m.group(2) not in N:
            missing.add(m.group(2))
            return m.group(3)
        return m.group(3) if truthy(N[m.group(2)]) == (m.group(1) == '?') else ''
    return COND.sub(f, text)


for tpl in sorted((R / 'scripts/search_templates').glob('*.tex')):
    name = tpl.stem
    lines = tpl.read_text(encoding='utf-8').splitlines()
    target = R / lines[0].split('target:', 1)[1].strip()
    body = resolve('\n'.join(lines[1:]).strip('\n'))
    if '<<?' in body or '<<!' in body or '<</' in body:
        sys.exit(f'{name}: a condition is not closed or is nested')

    def sub(m):
        k, mode = m.group(1), m.group(2)
        if k not in N:
            missing.add(k)
            return '??' + k
        v = str(N[k])
        return 'none' if (mode == '|w' and v == '0') else v

    text = re.sub(r'<<([a-zA-Z0-9_]+)(\|w)?>>', sub, body)
    src = target.read_text(encoding='utf-8')
    pat = re.compile(r'(%<<search:' + re.escape(name) + r'\n)(.*?)(%>>search:' + re.escape(name) + r')', re.S)
    if not pat.search(src):
        sys.exit(f'markers for {name} not found in {target}')
    # v0.25: an approved passage (tag A) must not lose its approval when the block is rendered again (the template of
    # Table 8's caption still carried S after the final pass had approved it, so a rerender reverted it)
    old_tags = re.findall(r'\\src\{([A-Z])\}', pat.search(src).group(2))
    new_tags = re.findall(r'\\src\{([A-Z])\}', text)
    lost = sum(1 for a in old_tags if a == 'A') - sum(1 for a in new_tags if a == 'A')
    if lost > 0 and name in REDRAFT:
        print(f'{name}: {lost} approved passage(s) of {target.name} redrafted (now S, for the final pass)')
    elif lost > 0 and len(new_tags) >= len(old_tags):
        sys.exit(f'STOP: rendering {name} would turn {lost} approved passage(s) of {target.name} back to S; '
                 f'copy the A tags into scripts/search_templates/{name}.tex first')
    src = pat.sub(lambda m: m.group(1) + text + '\n' + m.group(3), src)
    target.write_text(src, encoding='utf-8')
    # register numbers paragraph by paragraph
    for para in [p for p in re.split(r'\n\s*\n', body) if p.strip()]:
        keys = [k for k, mode in re.findall(r'<<([a-zA-Z0-9_]+)(\|w)?>>', para) if not (mode and str(N.get(k)) == '0')]
        if not keys:
            continue
        rendered = re.sub(r'<<([a-zA-Z0-9_]+)(\|w)?>>', lambda m: 'none' if (m.group(2) and str(N.get(m.group(1))) == '0') else str(N.get(m.group(1), '')), para)
        marker = re.sub(r'^\\src\{[^}]*\}\{[^}]*\}', '', rendered.strip())[:35]
        for k in keys:
            v = str(N.get(k, ''))
            # v0.10: a signed value (+0.012, $-$0.005) is registered without its sign, as the ledger reads the number
            bench.append({'file': target.name, 'marker': marker, 'value': re.sub(r'^(\$-\$|[+-])', '', v.replace(',', '')),
                          'printed': v, 'key': k, 'source': SRC})
json.dump(bench, open(R / 'scripts/search_bench.json', 'w', encoding='utf-8'), indent=1)
print(f'rendered {len(list((R / "scripts/search_templates").glob("*.tex")))} templates, {len(bench)} numbers registered')
if missing:
    sys.exit(f'missing keys: {sorted(missing)}')
