"""WP4: merge Scopus, OpenAlex and arXiv records; deduplicate by DOI, then by normalised title + year (+-1)."""
import csv, json, glob, re, sys, unicodedata, collections
csv.field_size_limit(10**8)
scopus_csv, oa_dir, arx_csv, out = sys.argv[1:5]
def nt(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()
def ndoi(d):
    d = (d or '').strip().lower(); d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d); return d or None
recs = []
for r in csv.DictReader(open(scopus_csv, encoding='utf-8-sig')):
    recs.append({'source': 'scopus', 'id': r['EID'], 'doi': ndoi(r['DOI']), 'title': r['Title'], 'year': r['Year'], 'abstract': r['Abstract'],
                 'venue': r['Source title'], 'doctype': r['Document Type'], 'language': r.get('Language of Original Document', ''), 'authors': r['Authors'], 'keywords': r.get('Author Keywords', '')})
def inv(ix):
    if not ix: return ''
    pos = {}
    for w, ps in ix.items():
        for p in ps: pos[p] = w
    return ' '.join(pos[k] for k in sorted(pos))
for f in sorted(glob.glob(oa_dir + '/page_*.json')):
    for w in json.load(open(f))['results']:
        src = ((w.get('primary_location') or {}).get('source') or {}) or {}
        recs.append({'source': 'openalex', 'id': w['id'].rsplit('/', 1)[-1], 'doi': ndoi(w.get('doi')), 'title': w.get('display_name') or '', 'year': str(w.get('publication_year') or ''),
                     'abstract': inv(w.get('abstract_inverted_index')), 'venue': src.get('display_name') or '', 'doctype': w.get('type') or '', 'language': w.get('language') or '',
                     'authors': '; '.join(a['author']['display_name'] for a in (w.get('authorships') or [])[:6]), 'keywords': ''})
for r in csv.DictReader(open(arx_csv)):
    recs.append({'source': 'arxiv', 'id': r['arxiv_id'], 'doi': ndoi(r['doi']), 'title': r['title'], 'year': r['published'][:4], 'abstract': r['abstract'],
                 'venue': r['journal_ref'] or 'arXiv', 'doctype': 'preprint', 'language': 'en', 'authors': r['authors'], 'keywords': r['categories']})
counts = collections.Counter(r['source'] for r in recs)
# union-find over records: same DOI, or same normalised title and |year diff| <= 1
parent = list(range(len(recs)))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
def union(a, b): parent[find(a)] = find(b)
by_doi, by_title = {}, collections.defaultdict(list)
for i, r in enumerate(recs):
    if r['doi']:
        if r['doi'] in by_doi: union(i, by_doi[r['doi']])
        else: by_doi[r['doi']] = i
    t = nt(r['title'])
    if len(t) >= 25:
        for j in by_title[t]:
            try:
                if abs(int(recs[j]['year'] or 0) - int(r['year'] or 0)) <= 1: union(i, j)
            except ValueError: pass
        by_title[t].append(i)
groups = collections.defaultdict(list)
for i in range(len(recs)): groups[find(i)].append(i)
pri = {'scopus': 0, 'openalex': 1, 'arxiv': 2}
rows = []
for g in groups.values():
    srcs = sorted({recs[i]['source'] for i in g}, key=pri.get)
    best = min(g, key=lambda i: (pri[recs[i]['source']], -len(recs[i]['abstract'] or '')))
    r = dict(recs[best]); r['sources'] = '+'.join(srcs); r['n_records'] = len(g)
    if not r['abstract']:
        alt = [recs[i]['abstract'] for i in g if recs[i]['abstract']]; r['abstract'] = max(alt, key=len) if alt else ''
    r['record_ids'] = ';'.join(f"{recs[i]['source']}:{recs[i]['id']}" for i in g)
    rows.append(r)
rows.sort(key=lambda r: (r['year'], nt(r['title'])))
for k, r in enumerate(rows, 1): r['rec'] = f'R{k:05d}'
cols = ['rec', 'sources', 'n_records', 'year', 'title', 'abstract', 'doi', 'venue', 'doctype', 'language', 'authors', 'keywords', 'record_ids']
w = csv.DictWriter(open(out, 'w', newline=''), cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
combo = collections.Counter(r['sources'] for r in rows)
summary = {'records_by_source': dict(counts), 'records_total': len(recs), 'unique_after_dedup': len(rows), 'duplicates_removed': len(recs) - len(rows),
           'unique_by_source_combination': dict(combo), 'unique_without_abstract': sum(1 for r in rows if not r['abstract'])}
json.dump(summary, open(out.replace('.csv', '_summary.json'), 'w'), indent=1); print(json.dumps(summary, indent=1))
