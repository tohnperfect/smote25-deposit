#!/usr/bin/env python3
"""v0.8 online appendix: write supplement/supp_refs.bib, the 28 references that the coding of the 71 empirical
studies cites and refs.bib lacks.

Source of each entry, in this order:
1. the Crossref record that scripts/verify_refs.py matched to the entry of the Evaluation section's candidate list
   (team repo: Evaluation section/latex/notes/empirical-bib-candidates.bib) by title and first author
   (refcheck_supp/crossref.json; 25 entries, title similarity at least 0.97);
2. the Crossref record of a DOI found by hand where the title search failed (DOI_BY_HAND; the record is fetched
   and kept in refcheck_supp/crossref_extra.json);
3. for the two conference papers without a DOI, the fields in BY_HAND, with the sources checked on 11 Nov 2026.
Nothing else is typed in: the few corrections of Crossref fields are listed in FIX with their reason.
Usage: python3 scripts/make_supp_bib.py refcheck_supp/ supplement/supp_refs.bib
"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

D = '2026-11-11'
UA = {'User-Agent': 'SMOTE25-refcheck/0.2 (scripted bibliography check)'}
KEYS = ['abdi2016mdo', 'das2015racog', 'datta2020dlexiboost', 'janicka2019soup', 'kim2022sos', 'koziarski2020mcccr',
        'krawczyk2020mcrbo', 'kubat1997oss', 'kubat1998shrink', 'liu2009easyensemble', 'liu2020mbs',
        'naglik2024gmmsampling', 'napierala2010spider2', 'palli2022cbhsid', 'ren2025goio', 'ren2026dgot',
        'seiffert2010rusboost', 'sun2015splitbal', 'tao2025mcnclwo', 'vuttipittayamongkol2018obu',
        'vuttipittayamongkol2020nbu', 'wu2007cogos', 'xie2022gdo', 'yan2025mlos', 'yen2009sbc', 'zheng2022shsampler',
        'zhou2006globalcs', 'zhou2010globalcs']
# Crossref stores the KDD 2022 title as "SOS" with the rest as a subtitle, so the title search missed it.
DOI_BY_HAND = {'kim2022sos': '10.1145/3534678.3539454'}
BY_HAND = {
    'kubat1997oss': ('inproceedings', {
        'author': 'Kubat, Miroslav and Matwin, Stan',
        'title': 'Addressing the Curse of Imbalanced Training Sets: One-Sided Selection',
        'booktitle': 'Proceedings of the Fourteenth International Conference on Machine Learning ({ICML} 1997)',
        'editor': 'Fisher, Douglas H.', 'pages': '179--186', 'publisher': 'Morgan Kaufmann', 'year': '1997',
        'status': f'no DOI; dblp record conf/icml/KubatM97 (as shown by BibSonomy) and mlanthology.org, checked {D}'}),
    'zhou2006globalcs': ('inproceedings', {
        'author': 'Zhou, Zhi-Hua and Liu, Xu-Ying',
        'title': 'On Multi-Class Cost-Sensitive Learning',
        'booktitle': 'Proceedings of the Twenty-First National Conference on Artificial Intelligence ({AAAI} 2006)',
        'pages': '567--572', 'publisher': '{AAAI} Press', 'year': '2006',
        'status': f'no DOI; proceedings (AAAI 21, technical papers, machine learning track) from aaai.org, pages from '
                  f'the reference list of arXiv:1209.1800; checked {D}'}),
}
FIX = {  # key -> field -> value, with the reason
    'zhou2010globalcs': {'title': 'On Multi-Class Cost-Sensitive Learning'},          # Crossref title in capitals
    'krawczyk2020mcrbo': {'author': 'Krawczyk, Bartosz and Koziarski, Micha{\\l} and Wo{\\\'z}niak, Micha{\\l}'},
    # Crossref drops the diacritics that the same authors' record koziarski2020mcccr keeps
    'liu2009easyensemble': {'author': 'Liu, Xu-Ying and Wu, Jianxin and Zhou, Zhi-Hua'},
    # Crossref stores each full name as the family name
    'wu2007cogos': {'booktitle': 'Proceedings of the 13th {ACM} {SIGKDD} International Conference on Knowledge '
                                 'Discovery and Data Mining'},                         # Crossref in lower case
}
PROPER = {'Newton', 'Gaussian', 'Mahalanobis'}
ACCENT = {'́': "'", '̀': '`', '̂': '^', '̈': '"', '̃': '~', '̧': 'c', '̌': 'v',
          '̨': 'k', '̇': '.'}
SPECIAL = {'ł': '{\\l}', 'Ł': '{\\L}', 'ø': '{\\o}', 'Ø': '{\\O}', 'ß': '{\\ss}', 'æ': '{\\ae}', 'đ': '{\\dj}'}
PUNCT = {'‐': '-', '‑': '-', '–': '--', '—': '--', '’': "'", '‘': "'", ' ': ' '}


def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:  # noqa: BLE001
            time.sleep(3 * (k + 1))
    sys.exit(f'STOP: could not fetch {url}')


def tex(s):
    out = []
    for ch in s:
        if ch in PUNCT:
            out.append(PUNCT[ch])
        elif ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ord(ch) < 128:
            out.append(ch)
        else:
            base, *marks = unicodedata.normalize('NFD', ch)
            if len(marks) == 1 and marks[0] in ACCENT:
                cmd = ACCENT[marks[0]]
                out.append('{\\' + cmd + ('{' + base + '}' if cmd.isalpha() else base) + '}')
            else:
                sys.exit(f'STOP: no TeX form for {ch!r} in {s!r}')
    return ''.join(out).replace('&', '\\&')


def protect(title):
    def rep(m):
        w = m.group(0)
        return '{' + w + '}' if any(c.isupper() for c in w[1:]) or w in PROPER else w
    return re.sub(r'(?<![{\\])\b[A-Za-z][A-Za-z0-9]*\b', rep, title)


def year(m):
    for k in ('published-print', 'issued', 'published-online'):
        dp = (m.get(k) or {}).get('date-parts') or [[None]]
        if dp[0][0]:
            return str(dp[0][0])
    return ''


def from_crossref(key, m, how):
    title = ' '.join((m.get('title') or [''])[0].split())
    sub = ' '.join(((m.get('subtitle') or ['']) or [''])[0].split())
    if sub and sub.lower() not in title.lower():
        title = f'{title}: {sub}'
    f = {'author': ' and '.join(tex(f"{a['family'].strip()}, {a.get('given', '').strip()}".strip(', '))
                                for a in m.get('author', [])),
         'title': title}
    typ = m.get('type')
    cont = [c for c in (m.get('container-title') or []) if c]
    if typ == 'journal-article':
        etype = 'article'
        f['journal'] = cont[0]
        f['volume'] = m.get('volume', '')
        f['number'] = (m.get('issue') or '').replace('-', '--')
    elif typ == 'proceedings-article':
        etype = 'inproceedings'
        f['booktitle'] = cont[0]
        f['publisher'] = m.get('publisher', '')
    elif typ == 'book-chapter':
        etype = 'inproceedings'
        f['booktitle'] = cont[-1]
        if len(cont) > 1:
            f['series'] = cont[0]
        f['publisher'] = 'Springer' if 'Springer' in m.get('publisher', '') else m.get('publisher', '')
    else:
        sys.exit(f'STOP: Crossref type {typ} of {key} not handled')
    f['pages'] = (m.get('page') or m.get('article-number') or '').replace('-', '--')
    f['year'] = year(m)
    f['doi'] = m['DOI']
    f['status'] = f'Crossref record ({how}), checked {D}; key from the Evaluation coding'
    for k, v in FIX.get(key, {}).items():
        f[k] = v
        f['status'] += f'; {k} corrected (see make_supp_bib.py)'
    return etype, f


def fmt(key, etype, f):
    order = ['author', 'title', 'journal', 'booktitle', 'series', 'editor', 'volume', 'number', 'pages',
             'publisher', 'year', 'doi', 'status']
    parts = []
    for k in order:
        v = f.get(k)
        if not v:
            continue
        if k == 'title':
            v = protect(tex(v) if not v.isascii() else v)
        elif k in ('journal', 'booktitle', 'series', 'publisher'):
            v = tex(v) if not v.isascii() else v
        parts.append(f'{k}={{{v}}}')
    return f'@{etype}{{{key}, ' + ', '.join(parts) + '}'


def main():
    chk, out = Path(sys.argv[1]), Path(sys.argv[2])
    raw = json.loads((chk / 'crossref.json').read_text(encoding='utf-8'))
    extra_p = chk / 'crossref_extra.json'
    extra = json.loads(extra_p.read_text(encoding='utf-8')) if extra_p.exists() else {}
    for key, doi in DOI_BY_HAND.items():
        if key not in extra:
            extra[key] = get('https://api.crossref.org/works/' + urllib.parse.quote(doi))['message']
    extra_p.write_text(json.dumps(extra, indent=1, ensure_ascii=False), encoding='utf-8')
    lines = [f'% Generated by scripts/make_supp_bib.py on {D} from the Crossref records in refcheck_supp/ and two '
             'entries checked by hand; do not edit by hand.']
    for key in KEYS:
        if key in BY_HAND:
            etype, f = BY_HAND[key]
        elif key in raw:
            etype, f = from_crossref(key, raw[key], 'title search')
        elif key in extra:
            etype, f = from_crossref(key, extra[key], f'DOI {DOI_BY_HAND[key]} found by hand')
        else:
            sys.exit(f'STOP: no source for {key}')
        lines.append(fmt(key, etype, f))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'wrote {len(lines) - 1} entries to {out}')


if __name__ == '__main__':
    main()
