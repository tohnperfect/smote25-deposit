#!/usr/bin/env python3
"""Find and download open-access full texts for sampled records of the SMOTE25 search (WP4 coverage sample, WP5 use audit).

Only open routes meant for programmatic use, with an honest user agent and no attempt to get past a site that refuses:
  1. arXiv (records with an arXiv id): https://arxiv.org/pdf/<id>
  2. Europe PMC (by DOI): full-text XML of the open-access subset (REST API)
  3. Semantic Scholar Graph API (by DOI or arXiv id): the openAccessPdf link, fetched once; kept only if it is a PDF
  4. OpenAlex (local snapshot of the search): primary_location.pdf_url of records marked open access, fetched once
A site that answers 403, a login page or anything but a PDF/XML is recorded as not retrieved; nothing is retried with
another identity. Every text is checked against the record's title (share of title words found in the first pages).

Usage: python3 -I fulltext_fetch.py SAMPLE.csv OUTDIR [--limit-per-stratum N]
SAMPLE.csv: columns rec, stratum, order (random order within the stratum), doi, arxiv, openalex, title.
With --limit-per-stratum N the script stops a stratum once N records have a usable text (records are taken in order).
Writes OUTDIR/raw/<rec>.(pdf|xml), OUTDIR/text/<rec>.txt and OUTDIR/fetch_log.csv (one row per record tried).
"""
import csv
import gzip
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

UA = 'SMOTE25-systematic-review/1.0 (academic research; python-requests)'
S = requests.Session()
S.headers.update({'User-Agent': UA})
csv.field_size_limit(10**9)


def norm_words(s):
    return [w for w in re.findall(r'[a-z0-9]+', (s or '').lower()) if len(w) > 3]


def title_share(title, text):
    words = set(norm_words(title))
    if not words:
        return 0.0
    head = ' '.join(norm_words(text[:12000]))
    return sum(1 for w in words if w in head) / len(words)


def get(url, timeout=20, **kw):
    try:
        r = S.get(url, timeout=timeout, allow_redirects=True, **kw)
        return r
    except requests.RequestException as e:
        return e



def clean_text(t):
    """Join words split at line ends, drop page-break marks, collapse blank lines, and cut the reference list."""
    t = t.replace('\f', '\n')
    t = re.sub(r'(\w)-\n(\w)', r'\1\2', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n\n', t)
    m = None
    for m in re.finditer(r'\n\s*(References|REFERENCES|Bibliography|BIBLIOGRAPHY|Literature Cited)\s*\n', t):
        pass
    if m and m.start() > 0.5 * len(t):
        t = t[:m.start()] + '\n\n[reference list omitted]\n'
    return t.strip()

def pdf_to_text(pdf, txt):
    try:
        subprocess.run(['pdftotext', '-q', str(pdf), str(txt)], check=True, timeout=120)
        return clean_text(txt.read_text(encoding='utf-8', errors='replace'))
    except Exception:
        return ''


def xml_to_text(xml):
    x = re.sub(r'<(table-wrap|ref-list|fig)\b.*?</\1>', lambda m: '\n[' + m.group(1) + ' omitted]\n' if m.group(1) == 'ref-list' else m.group(0), xml, flags=re.S)
    x = re.sub(r'</(p|title|sec|caption|tr|abstract|article-title)>', '\n', x)
    x = re.sub(r'<td[^>]*>', ' | ', x)
    x = re.sub(r'<[^>]+>', ' ', x)
    x = html.unescape(x)
    return re.sub(r'[ \t]+', ' ', re.sub(r'\n\s*\n+', '\n\n', x)).strip()


def epmc_lookup(doi):
    r = get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
            params={'query': f'DOI:"{doi}"', 'format': 'json', 'resultType': 'lite', 'pageSize': 5})
    if isinstance(r, Exception) or r.status_code != 200:
        return None
    for h in r.json().get('resultList', {}).get('result', []):
        if (h.get('doi') or '').lower() == doi.lower() and h.get('pmcid') and h.get('isOpenAccess') == 'Y':
            return h['pmcid']
    return None


def s2_batch(ids):
    """ids: list of 'DOI:..' or 'ARXIV:..'; returns {id: openAccessPdf url or ''}."""
    out = {}
    for i in range(0, len(ids), 400):
        part = ids[i:i + 400]
        for attempt in range(6):
            try:
                r = S.post('https://api.semanticscholar.org/graph/v1/paper/batch', params={'fields': 'openAccessPdf,externalIds,title'},
                           json={'ids': part}, timeout=60)
            except requests.RequestException:
                time.sleep(5 * (attempt + 1)); continue
            if r.status_code == 429:
                time.sleep(10 * (attempt + 1)); continue
            break
        if not isinstance(r, requests.Response) or r.status_code != 200:
            for k in part:
                out[k] = {'pdf': '', 'arxiv': '', 'pmcid': ''}
            continue
        for k, p in zip(part, r.json()):
            p = p or {}
            ext = p.get('externalIds') or {}
            out[k] = {'pdf': (p.get('openAccessPdf') or {}).get('url') or '', 'arxiv': ext.get('ArXiv') or '',
                      'pmcid': ('PMC' + str(ext['PubMedCentral'])) if ext.get('PubMedCentral') else ''}
        time.sleep(1.5)
    return out


def openalex_pdf_urls(snapshot_dir):
    urls = {}
    for f in sorted(Path(snapshot_dir).glob('page_*.json')):
        for w in json.load(open(f, encoding='utf-8')).get('results', []):
            loc = w.get('primary_location') or {}
            if loc.get('is_oa') and loc.get('pdf_url'):
                urls[w['id'].rsplit('/', 1)[-1]] = loc['pdf_url']
    return urls


def main():
    sample, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    limit = int(sys.argv[sys.argv.index('--limit-per-stratum') + 1]) if '--limit-per-stratum' in sys.argv else None
    raw, txtd = outdir / 'raw', outdir / 'text'
    raw.mkdir(parents=True, exist_ok=True)
    txtd.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(sample, encoding='utf-8')))
    rows.sort(key=lambda r: (r['stratum'], int(r['order'])))
    logp = outdir / 'fetch_log.csv'
    done = {r['rec']: r for r in csv.DictReader(open(logp, encoding='utf-8'))} if logp.exists() else {}
    oa = openalex_pdf_urls('/home/claude/work/search/openalex/2026-11-11')
    ids = []
    for r in rows:
        if r['rec'] in done:
            continue
        if r['doi']:
            ids.append('DOI:' + r['doi'])
        elif r['arxiv']:
            ids.append('ARXIV:' + r['arxiv'])
    s2 = s2_batch(ids) if ids else {}
    cols = ['rec', 'stratum', 'order', 'route', 'url', 'status', 'chars', 'title_share', 'usable']
    new = not logp.exists()
    fh = open(logp, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(fh, cols)
    if new:
        w.writeheader()
    usable = {}
    for r in done.values():
        usable[r['stratum']] = usable.get(r['stratum'], 0) + (r['usable'] == 'yes')
    for r in rows:
        if r['rec'] in done:
            continue
        if limit is not None and usable.get(r['stratum'], 0) >= limit:
            continue
        rec, title = r['rec'], r['title']
        tried = []
        text, route, url, status = '', '', '', 'not found'
        cands = []
        key = 'DOI:' + r['doi'] if r['doi'] else ('ARXIV:' + r['arxiv'] if r['arxiv'] else '')
        info = s2.get(key) or {'pdf': '', 'arxiv': '', 'pmcid': ''}
        arx = r['arxiv'] or info['arxiv']
        if arx:
            cands.append(('arxiv', 'https://arxiv.org/pdf/' + arx))
        pmc = ''
        if r['doi']:
            pmc = epmc_lookup(r['doi'])
            time.sleep(0.3)
        if pmc:
            cands.append(('europepmc', f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'))
        elif info['pmcid']:
            cands.append(('europepmc', f"https://www.ebi.ac.uk/europepmc/webservices/rest/{info['pmcid']}/fullTextXML"))
        if info['pdf']:
            u = info['pdf']
            if 'arxiv.org/abs/' in u:
                u = u.replace('/abs/', '/pdf/')
            cands.append(('semanticscholar', u))
        if r['openalex'] in oa:
            cands.append(('openalex', oa[r['openalex']]))
        seen = set()
        for rt, u in cands:
            if u in seen:
                continue
            seen.add(u)
            resp = get(u)
            if isinstance(resp, Exception):
                tried.append(f'{rt}:error'); continue
            body = resp.content
            if resp.status_code != 200:
                tried.append(f'{rt}:{resp.status_code}'); continue
            if body[:5] == b'%PDF-':
                p = raw / f'{rec}.pdf'
                p.write_bytes(body)
                t = pdf_to_text(p, txtd / f'{rec}.tmp.txt')
                (txtd / f'{rec}.tmp.txt').unlink(missing_ok=True)
            elif rt == 'europepmc' and b'<article' in body[:4000]:
                p = raw / f'{rec}.xml'
                p.write_bytes(body)
                t = xml_to_text(body.decode('utf-8', errors='replace'))
            else:
                tried.append(f'{rt}:not-pdf'); continue
            share = title_share(title, t)
            if len(t) < 5000 or share < 0.6:
                tried.append(f'{rt}:mismatch({len(t)},{share:.2f})'); continue
            text, route, url, status = t, rt, u, 'ok'
            break
        if text:
            (txtd / f'{rec}.txt').write_text(text, encoding='utf-8')
        ok = 'yes' if text else 'no'
        usable[r['stratum']] = usable.get(r['stratum'], 0) + (ok == 'yes')
        w.writerow({'rec': rec, 'stratum': r['stratum'], 'order': r['order'], 'route': route, 'url': url,
                    'status': status if text else ('; '.join(tried) or 'no open route'), 'chars': len(text),
                    'title_share': f'{title_share(title, text):.2f}' if text else '', 'usable': ok})
        fh.flush()
        if 'arxiv' in route:
            time.sleep(3)
    fh.close()
    print('usable texts by stratum:', usable)


if __name__ == '__main__':
    main()
