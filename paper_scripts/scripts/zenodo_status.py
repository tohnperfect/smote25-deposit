#!/usr/bin/env python3
"""Check every search record with a Zenodo DOI against the Zenodo API (v0.9, after the AI check of 11 Nov 2026).

The independent AI check (project doc claude/smote25-ai-check-report-2026-11-11.md) found 150 withdrawn Zenodo
deposits among the records it read and asked for a check of all records with a 10.5281/zenodo. DOI. For each such
record of data/search/2026-11-11/wp4_records_merged.csv.gz, this script asks https://zenodo.org/api/records/<id>
(one request per second, honest user agent, no token) and records the HTTP status and, for a removed record, the
removal date, reason and note of its tombstone. It changes no screening decision: the rule for withdrawn records is
for the team to decide.
Usage: python3 -I scripts/zenodo_status.py data/search/2026-11-11/wp4_records_merged.csv.gz \
           data/search/screening_full_2026-11-11/decisions/screen_decisions.csv data/search/zenodo_status_2026-11-11.csv
"""
import csv
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone

UA = {'User-Agent': 'SMOTE25-systematic-review/1.0 (academic research; python-urllib)', 'Accept': 'application/json'}


def ask(rid):
    url = f'https://zenodo.org/api/records/{rid}'
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.status, json.loads(r.read().decode('utf-8', 'replace'))
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode('utf-8', 'replace'))
            except Exception:  # noqa: BLE001
                body = {}
            if e.code in (429, 500, 502, 503, 504) and k < 2:
                time.sleep(10 * (k + 1))
                continue
            return e.code, body
        except Exception as e:  # noqa: BLE001
            if k == 2:
                return -1, {'error': str(e)[:200]}
            time.sleep(5)
    return -1, {}


def main():
    merged, decisions, out = sys.argv[1:4]
    with gzip.open(merged, 'rt', encoding='utf-8') as fh:
        recs = [r for r in csv.DictReader(fh) if '10.5281/zenodo.' in (r['doi'] or '').lower()]
    dec = {r['rec']: r for r in csv.DictReader(open(decisions, encoding='utf-8'))}
    rows = []
    for i, r in enumerate(recs):
        rid = re.search(r'10\.5281/zenodo\.(\d+)', r['doi'].lower()).group(1)
        code, body = ask(rid)
        tomb = body.get('tombstone') or {}
        rows.append(dict(rec=r['rec'], doi=r['doi'], zenodo_id=rid, year=r['year'], title=r['title'][:200],
                         decision=dec.get(r['rec'], {}).get('decision', ''), code=dec.get(r['rec'], {}).get('code', ''),
                         http=code, checked_utc=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                         removal_date=tomb.get('removal_date', ''),
                         removal_reason=(tomb.get('removal_reason') or {}).get('id', '') if isinstance(tomb.get('removal_reason'), dict) else str(tomb.get('removal_reason') or ''),
                         tombstone_note=(tomb.get('note') or '')[:120], status_field=str(body.get('status', ''))[:40]))
        if i % 50 == 0:
            print(i, code, flush=True)
        time.sleep(1)
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('records with a Zenodo DOI:', len(rows))
    print('HTTP status:', dict(Counter(r['http'] for r in rows)))
    print('removed (410) by decision:', dict(Counter(r['decision'] for r in rows if r['http'] == 410)))
    print('removal reasons:', dict(Counter(r['removal_reason'] for r in rows if r['http'] == 410)))
    print('removal dates:', dict(Counter(r['removal_date'][:10] for r in rows if r['http'] == 410)))


if __name__ == '__main__':
    main()
