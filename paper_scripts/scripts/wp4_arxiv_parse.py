import sys, pathlib, csv, xml.etree.ElementTree as ET
d = pathlib.Path(sys.argv[1]); ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
rows = {}
for f in sorted(d.glob('page_*.xml')):
    root = ET.parse(f).getroot()
    for e in root.findall('a:entry', ns):
        aid = e.find('a:id', ns).text.rsplit('/abs/', 1)[-1]
        base = aid.rsplit('v', 1)[0] if 'v' in aid.split('/')[-1] else aid
        g = lambda tag: (e.find(tag, ns).text or '').strip() if e.find(tag, ns) is not None else ''
        rows[base] = {'arxiv_id': base, 'version_id': aid, 'title': ' '.join(g('a:title').split()), 'abstract': ' '.join(g('a:summary').split()),
                      'published': g('a:published')[:10], 'updated': g('a:updated')[:10],
                      'authors': '; '.join(a.find('a:name', ns).text for a in e.findall('a:author', ns)),
                      'primary_category': (e.find('arxiv:primary_category', ns).attrib.get('term') if e.find('arxiv:primary_category', ns) is not None else ''),
                      'categories': ' '.join(c.attrib.get('term') for c in e.findall('a:category', ns)),
                      'doi': g('arxiv:doi'), 'journal_ref': g('arxiv:journal_ref')}
w = csv.DictWriter(open(sys.argv[2], 'w', newline=''), list(next(iter(rows.values())).keys())); w.writeheader(); w.writerows(rows.values())
print(len(rows), 'unique arXiv records;', sum(1 for r in rows.values() if r['doi']), 'with a DOI')
