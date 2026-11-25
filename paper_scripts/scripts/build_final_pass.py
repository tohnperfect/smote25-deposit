#!/usr/bin/env python3
"""Build records.json of the page "SMOTE25 Final Pass" (12 November 2026): every passage of the paper tagged S
(synthesis by a session) or R (new research by a session), as readable text, for the corresponding author's approval
(D16 as changed by D46: a session drafts, he approves; an approved passage is tagged A). Passages that carry one of the
14 edits of the M7 check (D39, scripts/apply_m7_v17.py) are flagged, whatever their tag.

A passage is the text from one \\src tag to the next one or to the end of its paragraph; inline passages keep the
paragraph they sit in as context. Tables and figures whose caption (or figure description) is tagged S or R are one
passage each, with their rows. \\team notes are left out: they are removed before submission. Each passage has an id
from a hash of its tag and LaTeX source, so a decision stays with a passage until its text changes.

Usage: python3 -I scripts/build_final_pass.py <draft_dir> <out_dir>
Reads main.tex, sec/*.tex (in the order main.tex inputs them), main.aux (reference numbers), main.bbl (the citation
labels as printed, 2019a and 2019b included) and refs.bib (citations that main.bbl lacks). Build the preview first.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

D, OUT = Path(sys.argv[1]), Path(sys.argv[2])
INDEX = Path(sys.argv[3]) if len(sys.argv) > 3 else None   # v0.18: where each passage is, for merge_final_pass.py

M7 = ['43 of the 57 papers that use SMOTE as a baseline pair it with the proposed method',
      'with SMOTE, 43 of the 57 papers that use it as a baseline pair it with the proposal',
      '29 that convert classes; 30 in Section', 'except to illustrate the choice of a parameter',
      'but their papers never evaluate it', 'Seventy of the 71 studies say why they chose their measures',
      'still give that argument for their choice of measures (Section', 'to make a classifier pay attention to a rare class. It is associated',
      'as in the documentation of the package', 'the mean AUC of the best oversampler exceeds that of SMOTE',
      'give two attacks that need only the released dataset', 'they find no consistent gain in discrimination',
      'implemented in common toolboxes', 'independent clinical studies find no consistent gain']

# ---------------------------------------------------------------- references and citations
LABELS = {}
for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', (D / 'main.aux').read_text(encoding='utf-8', errors='ignore')):
    LABELS[m.group(1)] = m.group(2)

ACC = {"\\'a": 'á', "\\'e": 'é', "\\'i": 'í', "\\'o": 'ó', "\\'u": 'ú', '\\"o': 'ö', '\\"u': 'ü', '\\"a': 'ä', '\\o': 'ø',
       '\\v{s}': 'š', '\\c{c}': 'ç', '\\~n': 'ñ', '\\~a': 'ã', '\\`e': 'è', "\\'c": 'ć', '\\^i': 'î', '\\^{i}': 'î', '\\l': 'ł'}


def deaccent(s):
    for k, v in ACC.items():
        s = s.replace('{' + k + '}', v).replace(k, v)
    return re.sub(r'[{}]', '', s)


BIB = {}
for m in re.finditer(r'@\w+\{([^,\s]+),(.*?)(?=\n@|\Z)', (D / 'refs.bib').read_text(encoding='utf-8'), re.S):
    body = m.group(2)
    a = re.search(r'author\s*=\s*\{(.*?)\}\s*,\s*(?:title|year|journal|booktitle|howpublished)', body, re.S)
    y = re.search(r'year\s*=\s*\{?(\d{4})', body)
    names = []
    if a:
        for part in re.split(r'\s+and\s+', a.group(1)):
            part = deaccent(part.strip())
            names.append(part.split(',')[0].strip() if ',' in part else (part.split()[-1] if part.split() else part))
    BIB[m.group(1)] = (names, y.group(1) if y else '')


# the labels the bibliography prints (main.bbl, natbib): author part and year with its letter (2019a, 2019b, ...)
BBL = {}
for m in re.finditer(r'\\bibitem\[(.*?)\]\{([^}]+)\}', (D / 'main.bbl').read_text(encoding='utf-8', errors='ignore'), re.S):
    lab = re.sub(r'\s+', ' ', m.group(1))
    lm = re.match(r'^(.*?)\((\d{4})(?:\{\\natexlab\{([a-z])\}\})?\)', lab)
    if lm:
        BBL[m.group(2)] = (deaccent(lm.group(1).replace('~', ' ')).strip(), lm.group(2) + (lm.group(3) or ''))


def cite_text(key):
    if key in BBL:
        return BBL[key]
    names, year = BIB.get(key, ([key], ''))
    names = [n for n in names if n.lower() != 'others'] or [key]
    who = names[0] if len(names) == 1 else (names[0] + ' and ' + names[1] if len(names) == 2 else names[0] + ' et al.')
    if len(BIB.get(key, ([], ''))[0]) > 2 or 'others' in [n.lower() for n in BIB.get(key, ([], ''))[0]]:
        who = names[0] + ' et al.'
    return who, year


def cite(cmd, post, keys):
    parts = [cite_text(k.strip()) for k in keys.split(',') if k.strip()]
    if cmd == 'citet':
        s = '; '.join(f'{w} ({y})' for w, y in parts)
        return s + (f' ({post})' if post else '')
    s = '; '.join(f'{w}, {y}' for w, y in parts)
    return '(' + s + (', ' + post if post else '') + ')'


# ---------------------------------------------------------------- LaTeX to readable text
MATH = {r'\kappa': 'κ', r'\Delta': 'Δ', r'\pi': 'π', r'\le': '≤', r'\leq': '≤', r'\ge': '≥', r'\geq': '≥', r'\times': '×',
        r'\cdot': '·', r'\pm': '±', r'\approx': '≈', r'\sim': '~', r'\lambda': 'λ', r'\alpha': 'α', r'\beta': 'β',
        r'\omega': 'ω', r'\in': '∈', r'\cup': '∪', r'\mid': '|', r'\sum': 'Σ', r'\min': 'min', r'\quad': ' ', r'\qquad': ' ',
        r'\dagger': '†', r'\infty': '∞', r'\neq': '≠', r'\rightarrow': '→', r'\to': '→', r'\left': '', r'\right': ''}


def balanced(s, i):
    """s[i] == '{'; return the index after the matching '}'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{' and (j == 0 or s[j - 1] != '\\'):
            depth += 1
        elif s[j] == '}' and (j == 0 or s[j - 1] != '\\'):
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


def drop_cmd(s, name):
    """Remove \\name{...} with balanced braces."""
    out, i = [], 0
    pat = re.compile(r'\\' + name + r'\s*\{')
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            return ''.join(out)
        out.append(s[i:m.start()])
        i = balanced(s, m.end() - 1)


def math(m):
    t = m.group(1)
    t = re.sub(r'\\(?:mathrm|text|mathbf|mathcal|operatorname)\{([^{}]*)\}', r'\1', t)
    t = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1)/(\2)', t)
    t = re.sub(r'\\hat\{([^{}]*)\}', r'\1̂', t)
    for k in sorted(MATH, key=len, reverse=True):
        t = re.sub(re.escape(k) + r'(?![A-Za-z])', MATH[k], t)
    t = re.sub(r'\^\{([^{}]*)\}', r'^\1', t).replace('_{', '_').replace('{', '').replace('}', '')
    return t.replace('-', '−').replace('\\,', ' ').replace('\\', '')


def to_text(s):
    s = drop_cmd(s, 'team')
    s = drop_cmd(s, 'label')
    s = re.sub(r'\\src\{[A-Z]\}\{[^}]*\}', '', s)
    s = re.sub(r'\\(citet|citep)(?:\[([^\]]*)\])?\{([^}]*)\}', lambda m: cite(m.group(1), (m.group(2) or '').replace('~', ' '), m.group(3)), s)
    s = re.sub(r'\\citeauthor\{([^}]*)\}', lambda m: cite_text(m.group(1))[0], s)
    s = re.sub(r'\\citeyear\{([^}]*)\}', lambda m: cite_text(m.group(1))[1], s)
    s = re.sub(r'\\(?:ref|eqref|pageref)\*?\{([^}]*)\}', lambda m: LABELS.get(m.group(1), '?'), s)
    s = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\url\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\$([^$]*)\$', math, s)
    s = re.sub(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', lambda m: ' [equation: ' + math(re.match(r'(.*)', m.group(1), re.S)) + '] ', s, flags=re.S)
    for _ in range(3):
        s = re.sub(r'\\(?:emph|textbf|textit|texttt|textsc|mbox|textrm|textsf|underline|paragraph|noindent)\s*\{([^{}]*)\}', r'\1', s)
    s = s.replace('``', '“').replace("''", '”').replace('---', '–').replace('--', '–')
    s = s.replace('\\%', '%').replace('\\&', '&').replace('\\_', '_').replace('\\$', '$').replace('\\#', '#')
    s = s.replace('~', ' ').replace('\\,', ' ').replace('\\ ', ' ').replace('\\\\', '\n').replace('\\noindent', '')
    s = deaccent(s) if '\\' in s else s
    s = re.sub(r'\\(?:item)\b', '\n• ', s)
    s = re.sub(r'\\(?:begin|end)\{[^}]*\}(?:\{[^}]*\})?', ' ', s)
    s = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?', '', s)
    s = s.replace('{', '').replace('}', '')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    return s.strip()


# ---------------------------------------------------------------- reading the files
def strip_comments(t):
    # v0.18: a line that is only a comment is dropped, as LaTeX does; v0.17 left a blank line there, which cut the abstract
    # at the rendered block of its Methods part and left Methods, Results and Conclusions off the page
    return '\n'.join(re.sub(r'(?<!\\)%.*$', '', line) for line in t.splitlines() if not line.lstrip().startswith('%'))


def files():
    main = (D / 'main.tex').read_text(encoding='utf-8')
    a, b = main.index('\\begin{abstract}'), main.index('\\end{abstract}')
    yield 'main.tex', main[a:b]
    for m in re.finditer(r'\\input\{(sec/[^}]+)\}', main):
        t = (D / (m.group(1) + '.tex')).read_text(encoding='utf-8')
        yield m.group(1) + '.tex', t
        for n in re.finditer(r'\\input\{(sec/[^}]+)\}', t):
            yield n.group(1) + '.tex', (D / (n.group(1) + '.tex')).read_text(encoding='utf-8')


def main():
    items, sec, sub, para_title, appendix = [], [0], [0], '', False
    secname = 'Abstract'
    tabn = fign = 0
    for fname, raw in files():
        t = strip_comments(raw)
        if fname == 'sec/11-appendix.tex':
            appendix = True
        pos = 0
        # walk the file block by block: floats whole, other text by paragraph
        for m in re.finditer(r'\\begin\{(table\*?|figure\*?)\}(.*?)\\end\{\1\}|((?:(?!\\begin\{(?:table|figure)).)+?)(?=\\begin\{(?:table|figure)|\Z)', t, re.S):
            if m.group(1):
                body = m.group(2)
                kind = 'Table' if m.group(1).startswith('table') else 'Figure'
                if '\\caption' not in body:
                    continue
                if kind == 'Table':
                    tabn += 1
                    num = tabn
                else:
                    fign += 1
                    num = fign
                lab = re.search(r'\\label\{([^}]+)\}', body)
                num = LABELS.get(lab.group(1), num) if lab else num
                ci = body.index('\\caption')
                cap = body[ci + 8: balanced(body, body.index('{', ci))]
                tag = re.search(r'\\src\{([A-Z])\}\{([^}]*)\}', cap)
                parts = []
                rows = ''
                tb = re.search(r'\\begin\{tabular[x*]?\}(?:\{[^}]*\})*(.*?)\\end\{tabular[x*]?\}', body, re.S)
                if tb:
                    rows = re.sub(r'\\(?:toprule|midrule|bottomrule|hline|cmidrule(?:\([^)]*\))?\{[^}]*\})', '', tb.group(1))
                    rows = '\n'.join(' | '.join(to_text(c) for c in r.split('&')) for r in re.split(r'\\\\', rows) if r.strip())
                    rows = re.sub(r'\\input\{gen/[^}]+\}', '[generated rows]', rows)
                gen = re.search(r'\\input\{(gen/[^}]+)\}', body)
                if gen:
                    rows = (rows + '\n' if rows else '') + '[rows generated from data: ' + gen.group(1) + '.tex]'
                src_latex = cap + (tb.group(1) if tb else '')
                flag = any(x in src_latex for x in M7)
                if tag and tag.group(1) != 'A' and (tag.group(1) in 'SR' or flag):
                    items.append(dict(kind=kind.lower(), where=f'{kind} {num}', sec=secname, tag=tag.group(1), file=fname,
                                      text=to_text(cap[1:-1] if cap.startswith('{') else cap), rows=rows, m7=flag, src=src_latex))
                # v0.18: other tagged text of the float (a \\tabnote) is a passage of its own; v0.17 left it off the page
                spans = [(ci, ci + 8 + len(cap))]
                if tb:
                    spans.append((tb.start(), tb.end()))
                dd = re.search(r'\\Description\{', body)
                if dd:
                    spans.append((dd.start(), balanced(body, dd.end() - 1)))
                for tg in re.finditer(r'\\src\{([A-Z])\}\{([^}]*)\}', body):
                    if any(a <= tg.start() < z for a, z in spans):
                        continue
                    # v0.19: the passage ends at the next tag or at the close of the group that holds it (a second
                    # tag inside one \\tabnote ends the first passage there)
                    depth, j = 0, tg.end()
                    while j < len(body):
                        ch = body[j]
                        if ch == '{' and body[j - 1] != '\\':
                            depth += 1
                        elif ch == '}' and body[j - 1] != '\\':
                            if depth == 0:
                                break
                            depth -= 1
                        elif depth == 0 and body.startswith('\\src{', j):
                            break
                        j += 1
                    seg = body[tg.start(): j]
                    flag = any(x in seg for x in M7)
                    if tg.group(1) != 'A' and (tg.group(1) in 'SR' or flag):
                        items.append(dict(kind='note', where=f'{kind} {num}, note below the {kind.lower()}', sec=secname,
                                          tag=tg.group(1), file=fname, text=to_text(seg), rows='', m7=flag, src=seg))
                d = re.search(r'\\Description\{', body)
                if d:
                    dtext = body[d.end() - 1: balanced(body, d.end() - 1)]
                    dtag = re.search(r'\\src\{([A-Z])\}', dtext)
                    if dtag and dtag.group(1) in 'SR':
                        items.append(dict(kind='description', where=f'{kind} {num}, description for screen readers', sec=secname,
                                          tag=dtag.group(1), file=fname, text=to_text(dtext[1:-1]), rows='', m7=False, src=dtext))
                continue
            text = m.group(3) or ''
            for block in re.split(r'\n\s*\n', text):
                b = block.strip()
                if not b:
                    continue
                for h in re.finditer(r'\\(section|subsection|paragraph)(\*?)\{((?:[^{}]|\{[^{}]*\})*)\}', b):
                    title = to_text(h.group(3))
                    if h.group(1) == 'section':
                        if not h.group(2):
                            sec[0] += 1
                            sub[0] = 0
                        num = (chr(64 + sec[0] - 10) if appendix else str(sec[0])) if not h.group(2) else ''
                        secname = (num + ' ' if num else '') + title
                        para_title = ''
                    elif h.group(1) == 'subsection':
                        sub[0] += 1
                        base = chr(64 + sec[0] - 10) if appendix else str(sec[0])
                        secname = f'{base}.{sub[0]} {title}'
                        para_title = ''
                    else:
                        para_title = title
                body = re.sub(r'\\(section|subsection)\*?\{((?:[^{}]|\{[^{}]*\})*)\}', '', b)
                body = re.sub(r'\\label\{[^}]*\}', '', body).strip()
                tags = list(re.finditer(r'\\src\{([A-Z])\}\{([^}]*)\}', body))
                if not tags:
                    continue
                context = to_text(body)
                for n, tg in enumerate(tags):
                    end = tags[n + 1].start() if n + 1 < len(tags) else len(body)
                    seg = body[tg.start():end]
                    flag = any(x in seg for x in M7)
                    if tg.group(1) == 'A' or (tg.group(1) not in 'SR' and not flag):   # v0.18: A is approved
                        continue
                    txt = to_text(seg)
                    if not txt:
                        continue
                    if '\\team' in seg and len(txt.split()) < 8:
                        txt += ' [the rest of this passage is a team note, still to be written]'
                    inline = len(tags) > 1
                    ctx = context if inline else ''
                    if fname.endswith('12-checklist.tex') and '\\item' in body:
                        # v0.38: a checklist answer is shown with its own question, not with the next item's
                        q = body[body.rfind('\\item', 0, tg.start()) + len('\\item'):tg.start()]
                        txt = to_text(seg.split('\\item')[0])
                        ctx = 'Checklist question: ' + to_text(q)
                    items.append(dict(kind='inline' if inline else 'paragraph', where=secname + (' · ' + para_title if para_title else ''),
                                      sec=secname, tag=tg.group(1), file=fname, text=txt, rows='', m7=flag,
                                      context=ctx, src=seg))
    # v0.18: passages approved in the final pass that keep their tag (an E passage), and redrafts asked for there
    kept = set()
    for f in sorted(OUT.glob('merged_*.json')):
        kept |= {e['id'] for e in json.loads(f.read_text(encoding='utf-8')).get('approved_tag_kept', [])}
    redrafted = json.loads((OUT / 'redrafted.json').read_text(encoding='utf-8')) if (OUT / 'redrafted.json').exists() else []
    for it in items:
        for r in redrafted:
            if r.get('type', 'redraft') in ('redraft', 'answer') and r['marker'] in it['src']:
                it.update(request=r['request'], requested_by=r['by'], old_n=r.get('old_n'), answer=r.get('answer', ''))
                if r.get('type', 'redraft') == 'redraft':
                    it['revised'] = True
                else:
                    it['answered'] = True
    # v0.19: a passage cut at a request comes back as a card of its own, so that the cut is approved too
    for r in redrafted:
        if r.get('type') == 'removed' and not r.get('confirmed'):
            card = dict(kind='removed', where=r['where'] + ' (cut)', sec=r['sec'], tag=r['tag'], file=r['file'],
                        text=r['old_text'], rows='', m7=False, src='removed|' + r['old_id'], revised=True,
                        request=r['request'], requested_by=r['by'], old_n=r.get('old_n'), answer=r.get('answer', ''))
            same = [k for k, it in enumerate(items) if it['sec'] == r['sec']]   # in place: after its section's passages
            items.insert(same[-1] + 1 if same else len(items), card)
    for it in items:   # v0.19: a passage that ends just before the next list item no longer shows a stray bullet
        it['text'] = re.sub(r'(\s*\u2022)+\s*$', '', it['text']).rstrip()
    for it in items:
        it['id'] = 'p' + hashlib.sha1((it['tag'] + '|' + it['kind'] + '|' + re.sub(r'\s+', ' ', it['src'])).encode()).hexdigest()[:10]
    items = [it for it in items if it['id'] not in kept]
    # v0.18: every S or R tag of the inputs must be on the page (the v0.17 page missed three parts of the abstract and two table notes)
    shown = re.sub(r'\s+', ' ', ' '.join(i['text'] + ' ' + i['rows'] for i in items))
    missed = []
    for fname, raw in files():
        t = strip_comments(raw)
        for tg in re.finditer(r'\\src\{([SR])\}\{[^}]*\}', t):
            seg = t[tg.start(): tg.start() + 600]
            cut = re.search(r'\n\s*\n', seg)
            seg = seg[:cut.start()] if cut else seg
            nxt = re.search(r'\\src\{', seg[5:])               # v0.50: a passage ends at the next tag (a bold lead-in of under 40 characters)
            seg = seg[:5 + nxt.start()] if nxt else seg
            if fname.endswith('12-checklist.tex'):   # v0.38: an answer ends at the next item
                seg = seg.split('\\item')[0]
            head = re.sub(r'\s+', ' ', to_text(seg))[:40]
            head = re.sub(r'\s*•.*$', '', head).rstrip()   # v0.43: a passage that ends where a list begins (the contributions)
            if head and head not in shown:
                missed.append((fname, head))
    assert not missed, f'STOP: S or R text not on the page: {missed}'
    index = {}
    for n, it in enumerate(items, 1):
        it['n'] = n
        it['words'] = len(it['text'].split()) + len(it['rows'].split())
        index[it['id']] = dict(n=n, file=it['file'], kind=it['kind'], tag=it['tag'], where=it['where'], src=it.pop('src'))
    ids = [i['id'] for i in items]
    assert len(ids) == len(set(ids)), 'STOP: two passages share an id'
    m7 = [i for i in items if i['m7']]
    found = sum(1 for x in M7 if any(x in json.dumps(i, ensure_ascii=False) or True for i in m7))
    mtex = (D / 'main.tex').read_text(encoding='utf-8')
    ver = re.search(r'Integrated draft (v[0-9.]+), (\d{1,2} \w+ \d{4})', mtex)
    approved = sum(len(re.findall(r'\\src\{A\}', raw)) for _, raw in files())
    out = dict(title='SMOTE25 Final Pass', built=ver.group(2), draft=ver.group(1), approved_A=approved, approved_kept=len(kept),
               redrafted=sum(1 for i in items if i.get('revised')), n=len(items),
               by_tag={t: sum(1 for i in items if i['tag'] == t) for t in sorted({i['tag'] for i in items})},
               m7=len(m7), words=sum(i['words'] for i in items), items=items)
    OUT.mkdir(parents=True, exist_ok=True)
    if INDEX:
        INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=0), encoding='utf-8')
    (OUT / 'records.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(json.dumps({k: v for k, v in out.items() if k != 'items'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
