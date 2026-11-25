"""WP4 identification on OpenAlex: string S5 on title and abstract, 2002-2026, types as in the 29 Oct pilot.
The API key is read from OPENALEX_API_KEY and never written: every logged URL is stored without it."""
import os, sys, json, time, urllib.parse, urllib.request, pathlib, datetime
KEY = os.environ.get('OPENALEX_API_KEY', ''); assert KEY, 'set OPENALEX_API_KEY'
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
S5 = '(SMOTE OR oversampling OR "over-sampling" OR "synthetic minority" OR "adaptive synthetic" OR "synthetic samples" OR "synthetic instances") AND (imbalanced OR imbalance OR "minority class" OR "minority classes")'
FLT = f'title_and_abstract.search:{S5},publication_year:2002-2026,type:article|preprint|book-chapter|review'
SEL = 'id,doi,display_name,publication_year,publication_date,type,language,primary_location,authorships,cited_by_count,abstract_inverted_index,ids,primary_topic'
def get(params):
    q = urllib.parse.urlencode(params)
    url = 'https://api.openalex.org/works?' + q
    for t in range(5):
        try:
            with urllib.request.urlopen(url + '&api_key=' + urllib.parse.quote(KEY), timeout=120) as r:
                return json.load(r), url
        except Exception as e:
            err = str(e).replace(KEY, '***'); time.sleep(5 * (t + 1))
    raise SystemExit('failed: ' + err)
log = {'run_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'), 'filter': FLT, 'pages': []}
cursor, page = '*', 0
while cursor:
    d, url = get({'filter': FLT, 'per-page': 200, 'cursor': cursor, 'select': SEL})
    page += 1; (out / f'page_{page:03d}.json').write_text(json.dumps(d))
    log['pages'].append({'page': page, 'n': len(d['results']), 'url': url}); log['count'] = d['meta']['count']
    print(page, len(d['results']), d['meta']['count'], flush=True)
    cursor = d['meta'].get('next_cursor') if d['results'] else None
    time.sleep(0.3)
log['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
json.dump(log, open(out / 'search_log.json', 'w'), indent=1)
