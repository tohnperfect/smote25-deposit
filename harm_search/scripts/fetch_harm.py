#!/usr/bin/env python3
"""WP5 step 4: rerun the four harm queries H1 to H4 against PubMed and write the screening batches.

The exact query strings are copied from ../harm_search_log.json (logged 10 Nov 2026, 13:26 UTC). For each query:
one esearch (retmax 1000, usehistory=y), then efetch in XML from the history server in pages of 200, with a pause of
about one second between requests. No API key, tool name or email is sent. Every request is logged with its UTC
time, URL, HTTP status and output file in raw/fetch_log.tsv; the raw responses are kept in raw/<query>/.
The records are parsed with the parser of the case search (pubmed_xml.py, unchanged copy of
case_search/scripts/parse_records.py), merged by PMID with the queries that found each, and written to
work/records.json; the screening batches (title and full abstract, plain text) go to work/batches/.
No screening decision is made here.
Usage: python3 -I scripts/fetch_harm.py ../harm_search_log.json raw work 75
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubmed_xml import full_abstract, parse_article, parse_book  # noqa: E402

BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
UA = {'User-Agent': 'SMOTE25-systematic-review/1.0 (academic research; python-urllib)'}
PAGE = 200


def request(log, step, url, out):
    t = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data, code = r.read(), r.status
            break
        except Exception as e:  # noqa: BLE001
            if k == 3:
                sys.exit(f'STOP: {step}: {e}')
            time.sleep(3 * (k + 1))
    with open(out, 'wb') as fh:
        fh.write(data)
    log.write(f'{t}\t{step}\t{code}\t{os.path.basename(out)}\t{len(data)}\t{url}\n')
    log.flush()
    return data


def main():
    log_path, raw, work, size = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    entries = [e for e in json.load(open(log_path, encoding='utf-8')) if e['query'][:2] in ('H1', 'H2', 'H3', 'H4')]
    if len(entries) != 4:
        sys.exit('STOP: expected the four queries H1 to H4')
    os.makedirs(raw, exist_ok=True)
    summary, recs = [], {}
    with open(os.path.join(raw, 'fetch_log.tsv'), 'w', encoding='utf-8') as log:
        log.write('utc_time\tstep\thttp_code\toutput_file\tbytes\turl\n')
        for e in entries:
            q = e['query'][:2]
            qdir = os.path.join(raw, q)
            os.makedirs(qdir, exist_ok=True)
            with open(os.path.join(qdir, 'query_term.txt'), 'w', encoding='utf-8') as fh:
                fh.write(e['term'])
            url = BASE + 'esearch.fcgi?' + urllib.parse.urlencode(
                {'db': 'pubmed', 'term': e['term'], 'retmax': 1000, 'usehistory': 'y'})
            root = ET.fromstring(request(log, f'{q} esearch', url, os.path.join(qdir, 'esearch.xml')))
            count, qkey, webenv = int(root.findtext('Count')), root.findtext('QueryKey'), root.findtext('WebEnv')
            ids = [i.text.strip() for i in root.findall('IdList/Id')]
            got = []
            for start in range(0, count, PAGE):
                time.sleep(1)
                url = BASE + 'efetch.fcgi?' + urllib.parse.urlencode(
                    {'db': 'pubmed', 'query_key': qkey, 'WebEnv': webenv, 'retstart': start, 'retmax': PAGE, 'retmode': 'xml'})
                page = ET.fromstring(request(log, f'{q} efetch {start}', url, os.path.join(qdir, f'efetch_retstart_{start:03d}.xml')))
                got += [parse_article(pa) for pa in page.findall('PubmedArticle')]
                got += [parse_book(pb) for pb in page.findall('PubmedBookArticle')]
            pm = [r['pmid'] for r in got]
            if sorted(pm) != sorted(ids) or len(set(pm)) != count:
                sys.exit(f'STOP: {q}: esearch {count} ids, efetch {len(pm)} records ({len(set(pm))} unique)')
            for r in got:
                recs.setdefault(r['pmid'], dict(r, queries=[]))['queries'].append(q)
            summary.append({'query': e['query'], 'term': e['term'], 'logged_count_2026_11_10': e['count'],
                            'count': count, 'run_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
            print(f'{q}: {count} records (logged {e["count"]} on 10 Nov)')
            time.sleep(1)
    os.makedirs(os.path.join(work, 'batches'), exist_ok=True)
    rows = sorted(recs.values(), key=lambda r: int(r['pmid']), reverse=True)
    for r in rows:
        r['abstract'] = full_abstract(r)
    json.dump(rows, open(os.path.join(work, 'records.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'queries': summary, 'distinct_records': len(rows),
               'without_abstract': sum(1 for r in rows if not r['abstract']),
               'by_queries': {k: sum(1 for r in rows if '+'.join(r['queries']) == k)
                              for k in sorted({'+'.join(r['queries']) for r in rows})}},
              open(os.path.join(work, 'fetch_summary.json'), 'w', encoding='utf-8'), indent=1)
    for b in range(0, len(rows), size):
        part = rows[b:b + size]
        with open(os.path.join(work, 'batches', f'batch_{b // size + 1:02d}.txt'), 'w', encoding='utf-8') as fh:
            for i, r in enumerate(part, b + 1):
                fh.write('=' * 20 + '\n')
                fh.write(f'#{i} PMID {r["pmid"]} | {r["year"]} | {r["journal"]} | {"; ".join(r["publication_types"])} | '
                         f'queries {"+".join(r["queries"])}\n')
                fh.write(f'TI: {r["title"]}\n')
                fh.write((r['abstract'] or '[no abstract]') + '\n')
    print(f'{len(rows)} distinct records; {sum(1 for r in rows if not r["abstract"])} without abstract; '
          f'{(len(rows) + size - 1) // size} batches of up to {size}')


if __name__ == '__main__':
    main()
