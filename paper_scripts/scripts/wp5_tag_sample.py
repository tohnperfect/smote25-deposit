#!/usr/bin/env python3
"""WP5 step 1 (M9): how far can the OpenAlex health tag (SDG 3) on works citing SMOTE be trusted,
and how many citing works use SMOTE rather than only cite it?

Draws, with a fixed seed, 100 citing works tagged SDG 3 and 50 citing works with no SDG tag, saves
the raw responses, rebuilds each abstract from OpenAlex's inverted index, and writes a coding sheet:
  health_application: yes / no / unclear      (from title and abstract)
  smote_use:          uses / only cites / unclear
First pass by a session (sheet 'first_pass'); a person codes a 20 percent subsample blind (sheet 'check').
Usage: OPENALEX_API_KEY=... python3 scripts/wp5_tag_sample.py data/openalex/<date> wp5/
"""
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

API, SMOTE, SEED = 'https://api.openalex.org', 'W2148143831', 20261110
KEY = os.environ.get('OPENALEX_API_KEY', '')
SEL = 'id,doi,title,publication_year,type,primary_topic,sustainable_development_goals,abstract_inverted_index'
snap, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)


def get(url):
    full = url + (('&' if '?' in url else '?') + 'api_key=' + urllib.parse.quote(KEY) if KEY else '')
    for k in range(4):
        try:
            with urllib.request.urlopen(full, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:  # noqa: BLE001
            time.sleep(2 * (k + 1))
    raise RuntimeError('request failed: ' + url)


def abstract(inv):
    if not inv:
        return ''
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return ' '.join(w for _, w in pos)


urls = {
    'sdg3': f'{API}/works?filter=cites:{SMOTE},sustainable_development_goals.id:https://metadata.un.org/sdg/3'
            f'&sample=100&seed={SEED}&per-page=100&select={SEL}',
    'all': f'{API}/works?filter=cites:{SMOTE}&sample=200&seed={SEED}&per-page=200&select={SEL}',
}
raw = {k: get(u) for k, u in urls.items()}
(snap / 'wp5_tag_sample_raw.json').write_text(json.dumps(dict(urls=urls, responses=raw), ensure_ascii=False), encoding='utf-8')
sdg3 = raw['sdg3']['results'][:100]
untagged = [w for w in raw['all']['results'] if not w.get('sustainable_development_goals')][:50]
rows = []
for grp, ws in (('SDG3', sdg3), ('no SDG tag', untagged)):
    for w in ws:
        pt = w.get('primary_topic') or {}
        rows.append([w['id'].rsplit('/', 1)[-1], grp, w.get('publication_year'), w.get('type'), (w.get('doi') or ''),
                     (pt.get('field') or {}).get('display_name', ''), w.get('title') or '', abstract(w.get('abstract_inverted_index'))])
rng = random.Random(SEED)
check = set(rng.sample(range(len(rows)), k=round(0.2 * len(rows))))
wb = openpyxl.Workbook()
info = wb.active; info.title = 'instructions'
for i, t in enumerate([
        'WP5 step 1: precision of the OpenAlex SDG 3 tag on works citing SMOTE (W2148143831), and share that use SMOTE.',
        f'Sample drawn {time.strftime("%Y-%m-%d")} with seed {SEED}: 100 citing works tagged SDG 3, 50 citing works with no SDG tag.',
        'health_application: yes if the work applies or studies a method on a health or medical problem (clinical, biomedical, public health); no if not; unclear if title and abstract do not say.',
        'smote_use: uses if title or abstract says SMOTE (or a SMOTE variant) is applied in the work; only cites if SMOTE is not mentioned or only discussed; unclear otherwise.',
        'Code from title and abstract only. The sheet "check" holds a 20 percent subsample for blind coding by a person.'], 1):
    info.cell(i, 1, t)
head = ['openalex_id', 'group', 'year', 'type', 'doi', 'primary field', 'title', 'abstract', 'health_application', 'smote_use', 'notes']
for name, sel in (('first_pass', range(len(rows))), ('check', sorted(check))):
    s = wb.create_sheet(name)
    for j, h in enumerate(head, 1):
        c = s.cell(1, j, h); c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDDDDD')
    for i, idx in enumerate(sel, 2):
        for j, v in enumerate(rows[idx], 1):
            s.cell(i, j, v)
    s.freeze_panes = 'C2'
wb.save(out / 'wp5_tag_precision_sheet.xlsx')
(out / 'wp5_tag_sample.json').write_text(json.dumps(dict(seed=SEED, rows=rows, check=sorted(check)), ensure_ascii=False), encoding='utf-8')
print(f'{len(sdg3)} SDG3 works, {len(untagged)} untagged works (from 200 sampled); {sum(1 for r in rows if r[7])} with an abstract')
