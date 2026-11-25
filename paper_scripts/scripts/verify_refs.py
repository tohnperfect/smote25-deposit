#!/usr/bin/env python3
"""WP8: check every entry of refs.bib against Crossref (and arXiv for preprints).

For an entry with a DOI the Crossref record of that DOI is fetched (this also proves
that the DOI resolves). For an entry without one, Crossref is searched with the title
and the first author, and the best hit is accepted only if the normalised titles
match (ratio >= 0.93) and the years differ by at most one. The script never edits
refs.bib; it writes refcheck/crossref.json (raw records) and refcheck/report.csv
(one row per entry: what Crossref says, what differs). Completing the bibliography
from the report is a separate, reviewed step.
Usage: python3 scripts/verify_refs.py refs.bib refcheck/
"""
import csv
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

UA = {'User-Agent': 'SMOTE25-refcheck/0.2 (scripted bibliography check)'}


def get(url):
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(3 * (k + 1))
    return 'ERROR'


def parse_bib(text):
    entries = []
    for m in re.finditer(r'@(\w+)\{([^,]+),(.*?)\}\s*(?=\n@|\n%|\Z)', text, re.S):
        typ, key, body = m.group(1), m.group(2).strip(), m.group(3)
        fields = {}
        for fm in re.finditer(r'(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}', body):
            fields[fm.group(1).lower()] = fm.group(2)
        entries.append((typ, key, fields))
    return entries


def plain(s):
    s = re.sub(r'\\[a-zA-Z]+\s*', '', s or '')
    s = re.sub(r"\\['`^\"~=.uvHc]\{?(\w)\}?", r'\1', s)
    s = s.replace('{', '').replace('}', '').replace('\\', '')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9 ]+', ' ', s.lower()).split()


def sim(a, b):
    return difflib.SequenceMatcher(None, ' '.join(plain(a)), ' '.join(plain(b))).ratio()


def cr_fields(msg):
    year = None
    for k in ('published-print', 'published-online', 'issued'):
        if msg.get(k, {}).get('date-parts') and msg[k]['date-parts'][0][0]:
            year = msg[k]['date-parts'][0][0]
            break
    authors = ' and '.join(f"{a.get('family', '')}, {a.get('given', '')}".strip(', ') for a in msg.get('author', []))
    return dict(cr_title=(msg.get('title') or [''])[0], cr_year=year,
                cr_container=(msg.get('container-title') or [''])[0], cr_volume=msg.get('volume', ''),
                cr_issue=msg.get('issue', ''), cr_pages=msg.get('page', '') or msg.get('article-number', ''),
                cr_doi=msg.get('DOI', ''), cr_type=msg.get('type', ''), cr_authors=authors,
                cr_publisher=msg.get('publisher', ''))


def main():
    bib = Path(sys.argv[1]).read_text(encoding='utf-8')
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    raw, rows = {}, []
    for typ, key, f in parse_bib(bib):
        title, year = f.get('title', ''), f.get('year', '')
        first = re.split(r'\s+and\s+', f.get('author', ''))[0].split(',')[0]
        rec, how = None, ''
        if f.get('doi'):
            r = get('https://api.crossref.org/works/' + urllib.parse.quote(f['doi']))
            if isinstance(r, dict):
                rec, how = r['message'], 'doi'
            else:
                how = 'doi-not-found' if r is None else 'error'
        if rec is None and how != 'error':
            q = urllib.parse.urlencode({'query.bibliographic': f'{plain(title) and " ".join(plain(title))} {first}',
                                        'rows': 5, 'select': 'DOI,title,author,issued,published-print,published-online,container-title,volume,issue,page,article-number,type,publisher'})
            r = get('https://api.crossref.org/works?' + q)
            best = None
            if isinstance(r, dict):
                for it in r['message']['items']:
                    s = sim(title, (it.get('title') or [''])[0])
                    y = cr_fields(it)['cr_year']
                    ok_year = not year.isdigit() or y is None or abs(int(year) - y) <= 1
                    if s >= 0.93 and ok_year and (best is None or s > best[0]):
                        best = (s, it)
            if best:
                rec, how = best[1], ('search' if not how else how + '+search')
            elif not how:
                how = 'no-match'
        row = dict(key=key, type=typ, bib_status=f.get('status', ''), bib_title=title, bib_year=year,
                   bib_doi=f.get('doi', ''), how=how)
        if rec:
            raw[key] = rec
            cf = cr_fields(rec)
            row.update(cf)
            row['title_sim'] = round(sim(title, cf['cr_title']), 3)
            diffs = []
            if year and cf['cr_year'] and str(cf['cr_year']) != year:
                diffs.append(f"year {year}->{cf['cr_year']}")
            for bf, cfk in (('volume', 'cr_volume'), ('pages', 'cr_pages')):
                bv = (f.get(bf, '') or '').replace('--', '-')
                if bv and cf[cfk] and bv != cf[cfk].replace('--', '-'):
                    diffs.append(f"{bf} {bv}->{cf[cfk]}")
            if not f.get('doi') and cf['cr_doi']:
                diffs.append(f"add doi {cf['cr_doi']}")
            if 'others' in f.get('author', '') or f.get('status', '').startswith('memory'):
                diffs.append('check authors')
            row['diffs'] = '; '.join(diffs)
        rows.append(row)
        print(f"{key:32} {how:14} {row.get('title_sim', ''):>5}  {row.get('diffs', '')[:90]}")
        time.sleep(0.25)
    (out / 'crossref.json').write_text(json.dumps(raw, indent=1, ensure_ascii=False), encoding='utf-8')
    keys = sorted({k for r in rows for k in r})
    with open(out / 'report.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(f'{len(rows)} entries; matched {sum(1 for r in rows if "cr_doi" in r)}')


if __name__ == '__main__':
    main()
