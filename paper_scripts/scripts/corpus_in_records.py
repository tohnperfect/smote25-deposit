#!/usr/bin/env python3
"""Where the 76 papers of the SMOTE25 core corpus stand among the 22,426 records of the systematic search.

Each corpus paper (data/search/2026-11-11/corpus_papers.json, the list of the method extraction: key, title, year,
OpenAlex id, SMOTE-family or not; copied from the team repository on 23 November 2026) is matched to
the records by DOI, then by title, then by a close title (three quarters of the words shared, the year within two),
as scripts/reflist_check.py matches references. A match carries the record's final decision of the screen.
Writes data/search/2026-11-11/corpus_in_records.csv and corpus_in_records.json.
Usage: python3 -I scripts/corpus_in_records.py <draft dir>
"""
import csv, gzip, json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

V = Path(sys.argv[1])


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def ndoi(s):
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', (s or '').strip().lower())


STOP = set('a an the of for in on with and to by via using based from is are as at'.split())


def toks(s):
    return {w for w in re.findall(r'[a-z0-9]+', (s or '').lower()) if w not in STOP and len(w) > 2}


recs = list(csv.DictReader(gzip.open(V / 'data/search/2026-11-11/wp4_records_merged.csv.gz', 'rt', encoding='utf-8')))
dec = {r['rec']: r for r in csv.DictReader(open(V / 'data/search/screening_full_2026-11-11/decisions/screen_decisions.csv', encoding='utf-8'))}
assert len(recs) == 22426 and len(dec) == 22426
by_doi, by_title = {}, {}
for r in recs:
    if ndoi(r['doi']):
        by_doi.setdefault(ndoi(r['doi']), r)
    if len(norm(r['title'])) >= 25:
        by_title.setdefault(norm(r['title']), []).append(r)
rec_toks = [(toks(r['title']), r) for r in recs]

corpus = json.load(open(V / 'data/search/2026-11-11/corpus_papers.json', encoding='utf-8'))
works = {w['id'].rsplit('/', 1)[-1]: w for w in json.load(open(V / 'data/openalex/2026-11-10/corpus_works.json', encoding='utf-8'))}
assert len(corpus) == 76 and sum(1 for c in corpus if c['sf']) == 37


def match(c):
    w = works.get(c.get('oa') or '')
    d = ndoi((w or {}).get('doi'))
    if d and d in by_doi:
        return by_doi[d], 'doi'
    y = int(c['year'])
    for title in {c['title'], (w or {}).get('display_name') or c['title']}:
        for r in by_title.get(norm(title), []):
            if not r['year'].isdigit() or abs(int(r['year']) - y) <= 2:
                return r, 'title'
    a = toks(c['title'])
    best, bj = None, 0.0
    for b, r in rec_toks:
        if len(a & b) * 4 < len(a) * 3:
            continue
        j = len(a & b) / len(a | b)
        if j > bj:
            best, bj = r, j
    if best is not None and bj >= 0.75 and (not best['year'].isdigit() or abs(int(best['year']) - y) <= 2):
        return best, 'close title'
    return None, ''


rows = []
for c in corpus:
    r, how = match(c)
    d = dec[r['rec']] if r else {}
    rows.append({'key': c['key'], 'year': c['year'], 'smote_family': 'yes' if c['sf'] else 'no', 'title': c['title'],
                 'in_window': 'yes' if int(c['year']) >= 2002 else 'no', 'rec': r['rec'] if r else '',
                 'matched_by': how, 'record_title': r['title'] if r else '', 'decision': d.get('decision', ''),
                 'code': d.get('code', d.get('reason', ''))})
out = V / 'data/search/2026-11-11'
with open(out / 'corpus_in_records.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
N = {'corpus': len(rows), 'family': sum(r['smote_family'] == 'yes' for r in rows)}
for lab, sel in (('all', rows), ('family', [r for r in rows if r['smote_family'] == 'yes']),
                 ('other', [r for r in rows if r['smote_family'] == 'no'])):
    N[lab + '_before_2002'] = sum(r['in_window'] == 'no' for r in sel)
    N[lab + '_in_records'] = sum(bool(r['rec']) for r in sel)
    N[lab + '_include'] = sum(r['decision'] == 'include' for r in sel)
    N[lab + '_exclude'] = sum(r['decision'] == 'exclude' for r in sel)
    N[lab + '_exclude_codes'] = dict(Counter(r['code'] for r in sel if r['decision'] == 'exclude'))
    N[lab + '_not_in_records_in_window'] = sum(not r['rec'] and r['in_window'] == 'yes' for r in sel)
N['matched_by'] = dict(Counter(r['matched_by'] for r in rows if r['rec']))
(out / 'corpus_in_records.json').write_text(json.dumps(N, indent=1) + '\n', encoding='utf-8')
print({k: v for k, v in N.items() if k.startswith('all_')})
