"""Shared helpers: record metadata (DOI, arXiv id, OpenAlex id) from the merged records of the search."""
import csv
import gzip
import re

csv.field_size_limit(10**9)
MERGED = '/home/claude/work/v06/data/search/2026-11-11/wp4_records_merged.csv.gz'


def load_records():
    out = {}
    for r in csv.DictReader(gzip.open(MERGED, 'rt', encoding='utf-8')):
        ids = r['record_ids']
        ax = re.search(r'arxiv:([^;]+)', ids)
        oa = re.search(r'openalex:(W\d+)', ids)
        doi = (r['doi'] or '').strip().lower()
        arx = ax.group(1).strip() if ax else ''
        if not arx and doi.startswith('10.48550/arxiv.'):
            arx = doi.split('arxiv.', 1)[1]
        r['arxiv'] = re.sub(r'v\d+$', '', arx)
        r['openalex'] = oa.group(1) if oa else ''
        r['doi'] = doi
        out[r['rec']] = r
    return out
