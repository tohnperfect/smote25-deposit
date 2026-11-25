#!/usr/bin/env python3
"""Citation counts of the corpus papers for Section 3.1 (v0.53), from the OpenAlex snapshot of 10 November 2026
(data/openalex/2026-11-10/corpus_works.json: the 75 corpus papers with an OpenAlex record, cited_by_count and
publication_year as OpenAlex gives them). Writes data/openalex/2026-11-10/corpus_citations.json.
Usage: python3 -I scripts/corpus_citations.py <draft dir>"""
import json
import statistics
import sys
from pathlib import Path

D = Path(sys.argv[1]) / 'data/openalex/2026-11-10'
w = json.load(open(D / 'corpus_works.json', encoding='utf-8'))
c = [x['cited_by_count'] for x in w]
early = [x['cited_by_count'] for x in w if x['publication_year'] <= 2009]
late = [x['cited_by_count'] for x in w if x['publication_year'] >= 2021]
out = {'papers': len(w), 'median': statistics.median(c), 'at_least_100': sum(1 for v in c if v >= 100),
       'to_2009': {'papers': len(early), 'median': statistics.median(early)},
       'from_2021': {'papers': len(late), 'median': statistics.median(late)}}
json.dump(out, open(D / 'corpus_citations.json', 'w', encoding='utf-8'), indent=1)
print(out)
