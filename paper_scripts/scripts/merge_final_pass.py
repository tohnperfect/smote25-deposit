#!/usr/bin/env python3
"""Merge the corresponding author's decisions from the page "SMOTE25 Final Pass" into the draft (v0.18, 13 November 2026).

D16 as changed by D46: a session drafts, the corresponding author approves; a passage he approves changes its tag from
S or R to A, keeping the old tag as the reference (\\src{S}{} becomes \\src{A}{S}), so that the ledger can still tell
synthesis from research. An approved passage with another tag (the E sentence of the M7 check) keeps its tag and is
listed. A passage marked Revise is listed with his note for a session to redraft; the redraft keeps the tag S or R and
comes back on the rebuilt page.

Passages are found through the index that scripts/build_final_pass.py writes with the page it was decided on
(build_final_pass.py <draft> <out> <index.json>): each passage's file and LaTeX source. A paragraph or inline passage is
located by the first line of its source, which must occur once in its file; a table by its caption, and every S or R tag
inside that table changes. A passage whose LaTeX paragraph runs on past the end of the passage (the page cut it at a
comment line) is reported as partial and not applied: give the rest its own tag first.

v0.20: a figure's caption and its description for screen readers (kinds figure and description) are merged too: every
S or R tag inside the braced group changes, after a check that the group still reads as the page showed it.

Usage: python3 -I scripts/merge_final_pass.py <draft_dir> <index.json> [<index.json> ...] <export.csv> [<export.csv> ...]
                                             [--approver NAME] [--log FILE] [--apply]
Exports: the online page's CSV or the offline copy's; the latest decision per passage counts. Give the index of every page
the exports were made on (a passage that kept its text keeps its id from one page to the next).
"""
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

args = sys.argv[1:]
apply = '--apply' in args
approver = 'Thanapong Intharah'
log_path = None
rest = []
i = 0
while i < len(args):
    if args[i] == '--apply':
        i += 1
    elif args[i] == '--approver':
        approver, i = args[i + 1], i + 2
    elif args[i] == '--log':
        log_path, i = Path(args[i + 1]), i + 2
    else:
        rest.append(args[i])
        i += 1
D = Path(rest[0])
INDEXES = [Path(p) for p in rest[1:] if p.endswith('.json')]
CSVS = [Path(p) for p in rest[1:] if p.endswith('.csv')]
index = {}
for ip in INDEXES:
    index.update(json.loads(ip.read_text(encoding='utf-8')))
INDEX = ', '.join(str(p) for p in INDEXES)

latest, comments = {}, []
for p in CSVS:
    with p.open(newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['decision'] not in ('approve', 'revise'):
                continue
            if r['reviewer'] != approver:
                comments.append(dict(r, file=p.name))
                continue
            k = r['passage_id']
            if k not in latest or r['time'] > latest[k]['time']:
                latest[k] = dict(r, file=p.name)
unknown = sorted(set(latest) - set(index))
if unknown:
    sys.exit(f'STOP: decisions on passages the index does not know: {unknown}')

files = {}


def text_of(f):
    if f not in files:
        files[f] = (D / f).read_text(encoding='utf-8')
    return files[f]


def strip_full_comments(s):
    return '\n'.join(l for l in s.split('\n') if not l.lstrip().startswith('%'))


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


TAG = re.compile(r'\\src\{([A-Z])\}\{([^}]*)\}')
templates = {}
synced = []


def sync_template(f, t, p, tag):
    """v0.19: a passage inside a rendered block (%<<search:NAME ... %>>search:NAME) also changes its tag in the
    block's template, scripts/search_templates/NAME.tex, or the next render would put the old tag back. The k-th tag of
    the block is the k-th tag of the template."""
    b0 = t.rfind('%<<search:', 0, p)
    if b0 < 0 or t.rfind('%>>search:', 0, p) > b0:
        return
    name = re.match(r'%<<search:(\w+)', t[b0:]).group(1)
    k = len(TAG.findall(t[b0:p]))
    tp = D / 'scripts' / 'search_templates' / f'{name}.tex'
    tt = templates.get(tp) or tp.read_text(encoding='utf-8')
    ms = list(TAG.finditer(tt))
    m = ms[k]
    if m.group(1) == 'A':
        return
    assert m.group(1) == tag and not m.group(2), (name, k, m.group(0))
    templates[tp] = tt[:m.start()] + '\\src{A}{%s}' % tag + tt[m.end():]
    synced.append(dict(template=str(tp.relative_to(D)), tag_index=k, file=f))
applied, kept, partial, revise, already, missing = [], [], [], [], [], []
for pid, r in sorted(latest.items(), key=lambda kv: index[kv[0]]['n']):
    ix = index[pid]
    entry = dict(id=pid, n=ix['n'], where=ix['where'], file=ix['file'], kind=ix['kind'], tag=ix['tag'], time=r['time'])
    if r['decision'] == 'revise':
        revise.append(dict(entry, note=r['what_should_change'], wording=r['wording']))
        continue
    if ix['kind'] == 'removed':   # v0.19: a cut, confirmed or to be restored
        (kept if r['decision'] == 'approve' else revise).append(dict(entry, cut=True))
        continue
    if ix['tag'] not in 'SR':
        kept.append(entry)
        continue
    t = text_of(ix['file'])
    src = ix['src']
    if ix['kind'] in ('paragraph', 'inline', 'note'):
        anchor = src.split('\n')[0][:160]
        hits = [m.start() for m in re.finditer(re.escape(anchor), t)]
        if len(hits) != 1:
            # the passage may already be approved: look for its A form
            a_anchor = anchor.replace('\\src{%s}{}' % ix['tag'], '\\src{A}{%s}' % ix['tag'], 1)
            if len(re.findall(re.escape(a_anchor), t)) == 1:
                already.append(entry)
                sync_template(ix['file'], t, t.index(a_anchor), ix['tag'])
            else:
                missing.append(dict(entry, found=len(hits)))
            continue
        p = hits[0]
        assert t.startswith('\\src{%s}{}' % ix['tag'], p), (pid, t[p:p + 40])
        # the LaTeX paragraph from this tag to the next tag or a blank line, full comment lines dropped
        after = strip_full_comments(t[p:])
        # v0.19: the paragraph also ends at an environment or a heading (\\end{abstract} after the abstract's last part)
        m = re.search(r'\n\s*\n|\\src\{[A-Z]\}\{[^}]*\}|\\(?:begin|end)\{|\\(?:sub)*section\*?\{|\\paragraph\{', after[1:])
        extent = re.sub(r'\\label\{[^}]*\}', '', after[:m.start() + 1] if m else after)
        if ix['kind'] != 'note' and len(norm(extent)) > len(norm(src)) + 5:   # a table note ends at its closing brace
            partial.append(dict(entry, page_words=len(norm(src).split()), paragraph_words=len(norm(extent).split()),
                                rest_starts=norm(extent)[len(norm(src)):len(norm(src)) + 80]))
            continue
        old = '\\src{%s}{}' % ix['tag']
        files[ix['file']] = t[:p] + '\\src{A}{%s}' % ix['tag'] + t[p + len(old):]
        sync_template(ix['file'], files[ix['file']], p, ix['tag'])
        applied.append(dict(entry, line=t.count('\n', 0, p) + 1, changed=1))
    elif ix['kind'] == 'table':
        depth, end = 0, len(src)
        for j, ch in enumerate(src):   # the caption is the braced group that starts the source
            if ch == '{' and (j == 0 or src[j - 1] != '\\'):
                depth += 1
            elif ch == '}' and src[j - 1] != '\\':
                depth -= 1
                if depth == 0:
                    end = j
                    break
        cap_first = src[1:end].split('\n')[0][:160]
        hits = [m.start() for m in re.finditer(re.escape(cap_first), t)]
        if len(hits) != 1:
            a_first = cap_first.replace('\\src{%s}{}' % ix['tag'], '\\src{A}{%s}' % ix['tag'], 1)
            if len(re.findall(re.escape(a_first), t)) == 1:
                already.append(entry)
            else:
                missing.append(dict(entry, found=len(hits)))
            continue
        p = hits[0]
        b0 = t.rfind('\\begin{table', 0, p)
        b1 = t.find('\\end{table', p)
        assert b0 >= 0 and b1 > p, pid
        # change only what the page showed: the caption and the rows of the tabular (not a \\tabnote or a description)
        block = t[b0:b1]
        spans = []
        ci = block.find('\\caption{')
        if ci >= 0:
            depth = 0
            for j in range(ci + 8, len(block)):
                if block[j] == '{' and block[j - 1] != '\\':
                    depth += 1
                elif block[j] == '}' and block[j - 1] != '\\':
                    depth -= 1
                    if depth == 0:
                        spans.append((ci, j + 1))
                        break
        tb = re.search(r'\\begin\{tabular[x*]?\}.*?\\end\{tabular[x*]?\}', block, re.S)
        if tb:
            spans.append((tb.start(), tb.end()))
        out, k, last = [], 0, 0
        for m in re.finditer(r'\\src\{([SR])\}\{\}', block):
            if any(a <= m.start() < z for a, z in spans):
                out.append(block[last:m.start()] + '\\src{A}{%s}' % m.group(1))
                last, k = m.end(), k + 1
        out.append(block[last:])
        files[ix['file']] = t[:b0] + ''.join(out) + t[b1:]
        applied.append(dict(entry, line=t.count('\n', 0, p) + 1, changed=k))
    elif ix['kind'] in ('figure', 'description'):
        # v0.20: a figure's caption (\\caption{...}) or its description for screen readers (\\Description{...}). The page
        # showed the whole braced group, so every S or R tag inside it changes; the group must match the page's source.
        body = src[1:-1] if src.startswith('{') and src.endswith('}') else src
        anchor = body.split('\n')[0][:160]
        hits = [m.start() for m in re.finditer(re.escape(anchor), t)]
        if len(hits) != 1:
            a_anchor = anchor.replace('\\src{%s}{}' % ix['tag'], '\\src{A}{%s}' % ix['tag'], 1)
            if len(re.findall(re.escape(a_anchor), t)) == 1:
                already.append(entry)
            else:
                missing.append(dict(entry, found=len(hits)))
            continue
        p = hits[0]
        macro = '\\caption{' if ix['kind'] == 'figure' else '\\Description{'
        assert t[:p].endswith(macro), (pid, t[max(0, p - 30):p + 30])
        depth, q = 1, p
        while depth:
            if t[q] == '{' and t[q - 1] != '\\':
                depth += 1
            elif t[q] == '}' and t[q - 1] != '\\':
                depth -= 1
            q += 1
        group = t[p:q - 1]
        if norm(group) != norm(body):
            partial.append(dict(entry, page_words=len(norm(body).split()), paragraph_words=len(norm(group).split()),
                                rest_starts='the caption or description differs from the page'))
            continue
        tags = [m for m in re.finditer(r'\\src\{([SR])\}\{\}', group)]
        for m in reversed(tags):
            a, z = p + m.start(), p + m.end()
            t = t[:a] + '\\src{A}{%s}' % m.group(1) + t[z:]
        files[ix['file']] = t
        new_group_end = q - 1 + len(tags)
        for m in re.finditer(r'\\src\{A\}\{([SR])\}', t[p:new_group_end]):
            sync_template(ix['file'], t, p + m.start(), m.group(1))
        applied.append(dict(entry, line=t.count('\n', 0, p) + 1, changed=len(tags)))
    else:
        missing.append(dict(entry, found='kind not handled'))

if apply:
    for f, t in files.items():
        (D / f).write_text(t, encoding='utf-8')
    for tp, tt in templates.items():
        tp.write_text(tt, encoding='utf-8')
log = dict(merged_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), approver=approver, applied=apply,
           exports=[p.name for p in CSVS], index=str(INDEX), approved_to_A=applied, approved_tag_kept=kept,
           approved_already_A=already, templates_synced=synced, partial=partial, not_found=missing, revise=revise, comments_of_others=comments)
if log_path:
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({'approved_to_A': len(applied), 'tags_changed': sum(a['changed'] for a in applied),
                  'approved_tag_kept': len(kept), 'already_A': len(already), 'templates_synced': len(synced), 'partial': [(x['n'], x['where']) for x in partial],
                  'not_found': [(x['n'], x['where'], x['found']) for x in missing], 'revise': [(x['n'], x['where']) for x in revise],
                  'comments_of_others': len(comments), 'written': apply}, ensure_ascii=False))
if missing:
    sys.exit(1)
