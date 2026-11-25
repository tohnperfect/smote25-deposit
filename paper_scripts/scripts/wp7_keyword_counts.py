#!/usr/bin/env python3
"""WP7 step 1 (Section 7.5): keyword counts on the unscreened WP4 records (title and abstract), by period.
Usage: python3 scripts/wp7_keyword_counts.py data/search/2026-11-11/wp4_records_merged.csv.gz data/search/2026-11-11/wp7_keyword_counts.json"""
import collections, csv, gzip, json, re, sys
csv.field_size_limit(10 ** 8)
PAT = {'GAN': r'\bgenerative adversarial|\bGANs?\b|\bCTGAN\b|\bWGAN', 'VAE': r'variational auto-?encoder|\bVAEs?\b',
       'diffusion': r'\bdiffusion model|\bdenoising diffusion|\bDDPM\b|\bTabDDPM\b', 'LLM': r'large language model|\bLLMs?\b|\bGPT',
       'long-tail': r'long-tail|long tail', 'foundation': r'foundation model|\bTabPFN\b'}
period = lambda y: '2002-2017' if y <= 2017 else ('2018-2022' if y <= 2022 else '2023-2026')
rows = list(csv.DictReader(gzip.open(sys.argv[1], 'rt', encoding='utf-8')))
res = {'records': len(rows), 'by_period': collections.Counter(), 'terms': {k: collections.Counter() for k in PAT}, 'any_deep_generative': collections.Counter()}
for r in rows:
    if not r['year']:
        continue
    p = period(int(r['year'])); t = r['title'] + ' ' + r['abstract']; res['by_period'][p] += 1
    gen = False
    for k, pat in PAT.items():
        if re.search(pat, t, re.I):
            res['terms'][k][p] += 1; gen = gen or k in ('GAN', 'VAE', 'diffusion', 'LLM')
    if gen:
        res['any_deep_generative'][p] += 1
res['any_deep_generative_total'] = sum(res['any_deep_generative'].values())
res['note'] = 'keyword match on title and abstract of unscreened records; GAN, VAE, diffusion or LLM counted once per record'
json.dump(res, open(sys.argv[2], 'w'), indent=1, default=dict); print(json.dumps(res, default=dict)[:400])
