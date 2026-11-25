#!/usr/bin/env python3
"""Pull every OpenAlex count the paper uses on one date and archive the responses.

Writes, under data/openalex/<YYYY-MM-DD>/:
  urls.tsv                     one line per request: file, UTC time, URL
  smote_work.json              the SMOTE work record (W2148143831)
  citing_count.json            works?filter=cites:W2148143831 (meta.count)
  group_<field>.json           group_by results for the reach table and figure
  corpus_works.json            cited_by_count of the corpus papers (OpenAlex ids
                               from Evaluation section/section07-coded-data.json)
  extra_works.json             other works whose citation count the text quotes
Usage:
  python3 scripts/openalex_snapshot.py <team-repo-root> [outdir]
Network: api.openalex.org answers from the shell, but since November 2026 it needs
an API key beyond a small free budget shared per IP address. Set OPENALEX_API_KEY.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = 'https://api.openalex.org'
SMOTE = 'W2148143831'
GROUPS = ['publication_year', 'primary_topic.domain.id', 'primary_topic.field.id',
          'sustainable_development_goals.id', 'authorships.countries', 'type']
EXTRA_DOIS = {  # works whose citation count is quoted in the text
    'saito2015precision': '10.1371/journal.pone.0118432',
}


KEY = os.environ.get('OPENALEX_API_KEY', '')


def get(url, tries=4):
    if KEY:
        url += ('&' if '?' in url else '?') + 'api_key=' + urllib.parse.quote(KEY)
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:  # noqa: BLE001
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def main():
    repo = Path(sys.argv[1])
    day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('data/openalex') / day
    out.mkdir(parents=True, exist_ok=True)
    log = []

    def save(name, url):
        data = get(url)
        (out / name).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding='utf-8')
        log.append((name, datetime.now(timezone.utc).isoformat(timespec='seconds'), url))
        time.sleep(0.15)
        return data

    save('smote_work.json', f'{API}/works/{SMOTE}')
    save('citing_count.json', f'{API}/works?filter=cites:{SMOTE}&per-page=1&select=id')
    for g in GROUPS:
        save(f'group_{g.replace(".", "_")}.json',
             f'{API}/works?filter=cites:{SMOTE}&group_by={g}&per-page=200')
    # works with a primary topic (denominator of the field shares)
    save('citing_with_topic.json',
         f'{API}/works?filter=cites:{SMOTE},primary_topic.id:!null&per-page=1&select=id')

    recs = json.loads((repo / 'Evaluation section' / 'section07-coded-data.json').read_text(encoding='utf-8'))
    ids = sorted({r['openalex_id'] for r in recs if r.get('openalex_id')})
    works = []
    for i in range(0, len(ids), 50):
        chunk = '|'.join(ids[i:i + 50])
        url = (f'{API}/works?filter=openalex_id:{chunk}&per-page=50'
               '&select=id,doi,display_name,publication_year,cited_by_count')
        data = get(url)
        works += data['results']
        log.append((f'corpus_works.json[{i}]', datetime.now(timezone.utc).isoformat(timespec='seconds'), url))
        time.sleep(0.15)
    (out / 'corpus_works.json').write_text(json.dumps(works, indent=1, ensure_ascii=False), encoding='utf-8')

    extra = {}
    for key, doi in EXTRA_DOIS.items():
        url = f'{API}/works/https://doi.org/{doi}?select=id,doi,display_name,publication_year,cited_by_count'
        extra[key] = get(url)
        log.append((f'extra_works.json[{key}]', datetime.now(timezone.utc).isoformat(timespec='seconds'), url))
    (out / 'extra_works.json').write_text(json.dumps(extra, indent=1, ensure_ascii=False), encoding='utf-8')

    with open(out / 'urls.tsv', 'w', encoding='utf-8') as f:
        f.write('file\tutc_time\turl\n')
        for row in log:
            f.write('\t'.join(row) + '\n')
    print(f'archived {len(log)} responses in {out}; corpus works found: {len(works)} of {len(ids)} ids')


if __name__ == '__main__':
    main()
