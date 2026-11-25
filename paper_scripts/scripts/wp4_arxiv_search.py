"""WP4: arXiv identification for the SMOTE25 systematic search (string S5, title and abstract).
Raw Atom responses are archived with their URLs; run once, then parse with --parse."""
import sys, time, json, urllib.parse, urllib.request, pathlib, datetime, re
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
G = ['smote', 'oversampling', '"over-sampling"', '"synthetic minority"', '"adaptive synthetic"', '"synthetic samples"', '"synthetic instances"']
I = ['imbalanced', 'imbalance', '"minority class"', '"minority classes"']
both = lambda terms: ' OR '.join(f'{f}:{t}' for t in terms for f in ('ti', 'abs'))
q = f'(({both(G)}) AND ({both(I)})) AND submittedDate:[200201010000 TO 202611112359]'
base = 'http://export.arxiv.org/api/query'
log = {'run_utc': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z', 'query': q, 'pages': []}
start, per, total = 0, 200, None
while True:
    url = base + '?' + urllib.parse.urlencode({'search_query': q, 'start': start, 'max_results': per, 'sortBy': 'submittedDate', 'sortOrder': 'ascending'})
    for attempt in range(4):
        try:
            body = urllib.request.urlopen(url, timeout=120).read().decode('utf-8'); break
        except Exception as e:
            time.sleep(10 * (attempt + 1)); body = None
    if body is None: log['error'] = f'failed at start={start}'; break
    (out / f'page_{start:05d}.xml').write_text(body)
    m = re.search(r'<opensearch:totalResults[^>]*>(\d+)<', body); total = int(m.group(1)) if m else total
    n = body.count('<entry>'); log['pages'].append({'start': start, 'entries': n, 'url': url})
    print(start, n, total, flush=True)
    start += per
    if n == 0 or (total is not None and start >= total): break
    time.sleep(3.5)
log['total_results'] = total
json.dump(log, open(out / 'search_log.json', 'w'), indent=1)
