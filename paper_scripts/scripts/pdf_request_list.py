#!/usr/bin/env python3
"""List the sampled papers that still need a full text, for the team to download through the library (WP4, WP5).

Reads samples/coverage_sample.csv and samples/useaudit_sample.csv (records with target fulltext) and the fetch logs
(coverage/fetch_log.csv, useaudit/fetch_log.csv); writes samples/pdf_requests.csv and samples/pdf_requests.xlsx with
one row per paper: where it belongs, its rank in its stratum (download in this order: any first part of each stratum
is itself a random sample), DOI, title, year, venue and the file name to save it under. v0.15: then the reserves of
samples/reserves.csv (make_samples.py), the papers the final merge may move into the samples, marked as such; and a
sheet of the five related-work papers of decision D44 (data/related_work/requests_d44.csv), saved by key in
~/Downloads/SMOTE25/papers/related_work/.
Usage: python3 -I scripts/pdf_request_list.py DRAFT_DIR
"""
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

csv.field_size_limit(10**9)
S = Path(sys.argv[1]) / 'data/search/screening_full_2026-11-11'


def rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8'))) if p.exists() else []


out = []
for proj, sample in (('coverage', 'coverage_sample.csv'), ('useaudit', 'useaudit_sample.csv')):
    log = {r['rec']: r for r in rows(S / proj / 'fetch_log.csv')}
    for r in rows(S / 'samples' / sample):
        if r['target'] != 'fulltext' or log.get(r['rec'], {}).get('usable') == 'yes':
            continue
        out.append({'sample': 'coverage (WP4)' if proj == 'coverage' else 'use audit (WP5)', 'stratum': r['stratum'],
                    'rank': int(r['order']), 'rec': r['rec'], 'doi': r['doi'], 'url': f'https://doi.org/{r["doi"]}' if r['doi'] else '',
                    'title': r['title'], 'year': r['year'], 'venue': r['venue'], 'save_as': f'{r["rec"]}.pdf',
                    'downloaded (yes/no/not available)': ''})
log = {**{r['rec']: r for r in rows(S / 'coverage/fetch_log.csv')}, **{r['rec']: r for r in rows(S / 'useaudit/fetch_log.csv')}}
for r in rows(S / 'samples/reserves.csv'):
    if log.get(r['rec'], {}).get('usable') == 'yes':
        continue
    out.append({'sample': 'coverage, reserve (WP4)' if r['target'] == 'reserve-coverage' else 'use audit, reserve (WP5)',
                'stratum': r['stratum'], 'rank': int(r['order']), 'rec': r['rec'], 'doi': r['doi'],
                'url': f'https://doi.org/{r["doi"]}' if r['doi'] else '', 'title': r['title'], 'year': r['year'],
                'venue': r['venue'], 'save_as': f'{r["rec"]}.pdf', 'downloaded (yes/no/not available)': ''})
out.sort(key=lambda r: ('reserve' in r['sample'], r['sample'], r['rank'], r['stratum']))
cols = list(out[0]) if out else ['sample']
with open(S / 'samples/pdf_requests.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    w.writerows(out)
wb = Workbook()
ws = wb.active
ws.title = 'pdf_requests'
ws.append(cols)
for c in ws[1]:
    c.font = Font(bold=True)
for r in out:
    ws.append([r[c] for c in cols])
for col, width in zip('ABCDEFGHIJK', (16, 8, 6, 9, 28, 34, 70, 6, 40, 12, 18)):
    ws.column_dimensions[col].width = width
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical='top')
ws.freeze_panes = 'A2'
info = wb.create_sheet('README', 0)
for line in ('SMOTE25: full texts needed for the coverage sample (WP4) and the use audit (WP5), 11 November 2026.',
             'Open-access copies were fetched automatically; these papers had none. Please download each through the library',
             'and save it under the name in column save_as (for example R01234.pdf) in ~/Downloads/SMOTE25/papers/sample_pdfs/.',
             'Work down the list by rank: the first papers of each stratum form a random sample on their own, so a partial',
             'download still gives an unbiased result. Mark each row yes, no or not available. Team use only (copyright).',
             'The rows marked reserve come last: papers that the final merge may move into a sample (an unsure record',
             'excluded under D28, or a correction of the authors). Download them after the others.'):
    info.append([line])
info.column_dimensions['A'].width = 120
rw = S.parents[1] / 'related_work/requests_d44.csv'   # v0.15: decision D44, Table 2
if rw.exists():
    ws2 = wb.create_sheet('related work (D44)')
    rcols = ['key', 'authors', 'year', 'title', 'venue', 'doi', 'url', 'access', 'save_as', 'why', 'downloaded (yes/no)']
    ws2.append(rcols)
    for c in ws2[1]:
        c.font = Font(bold=True)
    for r in rows(rw):
        ws2.append([r['key'], r['authors'], r['year'], r['title'], r['venue'], r['doi'], f'https://doi.org/{r["doi"]}',
                    r['access'], f'{r["key"]}.pdf', r['why'], ''])
    for col, width in zip('ABCDEFGHIJK', (24, 30, 6, 60, 40, 28, 40, 18, 28, 40, 12)):
        ws2.column_dimensions[col].width = width
    for row in ws2.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    info.append([''])
    info.append(['Sheet "related work (D44)": five papers for Table 2 (decision D44 of 12 November 2026). Save each under its'])
    info.append(['key (for example he2009learning.pdf) in ~/Downloads/SMOTE25/papers/related_work/. Team use only (copyright).'])
wb.save(S / 'samples/pdf_requests.xlsx')
print(len(out), 'papers to download:', {s: sum(1 for r in out if r['sample'] == s) for s in {r['sample'] for r in out}})
