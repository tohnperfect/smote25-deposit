#!/usr/bin/env python3
"""Check of the reference lists of the newest reviews of Table 2 against the systematic search (v0.53, 21 Nov 2026).

For each review (the five of 2025 and 2026 in Table 2) the reference list is the one Crossref holds for its DOI
(data/reflists/crossref/<doi>.json, fetched from api.crossref.org on 21 November 2026 UTC). Every reference is matched
to the 22,426 records of the search, by DOI and, where the reference has no DOI or the DOI finds no record, by its
title (letters and digits, lower case) with the year within one. A matched reference takes the record's final screening
decision. References are also matched to the corpus (data/openalex/2026-11-10/corpus_works.json, by DOI or title).

Writes data/reflists/references.csv (one row per review and reference), data/reflists/unmatched_window.csv (the
distinct references of the search window, 2002 on, that match no record, for the coding of step 2) and
data/reflists/reflist_numbers.json. When data/reflists/unmatched_coded.csv exists (step 2: an AI session's code for
each unmatched reference, from its title and, where Crossref gives one, its abstract) its counts are added.

Usage: python3 -I scripts/reflist_check.py <draft dir>"""
import csv
import gzip
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

csv.field_size_limit(10 ** 9)
V = Path(sys.argv[1])
OUT = V / 'data/reflists'
REVIEWS = OrderedDict([
    ('10.1109/access.2025.3584532', 'Udu et al. (2025)'),
    ('10.1007/s41060-025-00878-w', 'Idwan et al. (2025)'),
    ('10.1016/j.asoc.2024.112677', 'Hayaeian Shirvan et al. (2025)'),
    ('10.1007/s11704-025-50274-7', 'Gao et al. (2026)'),
    ('10.3390/make8070211', 'Yousefimehr et al. (2026)'),
])


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())


def ndoi(s):
    s = (s or '').strip().lower()
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', s)


# the records of the search and their final decisions
recs = list(csv.DictReader(gzip.open(V / 'data/search/2026-11-11/wp4_records_merged.csv.gz', 'rt', encoding='utf-8')))
dec = {r['rec']: r for r in csv.DictReader(open(V / 'data/search/screening_full_2026-11-11/decisions/screen_decisions.csv', encoding='utf-8'))}
assert len(recs) == 22426 and len(dec) == 22426
by_doi, by_title = {}, {}
for r in recs:
    d = ndoi(r['doi'])
    if d:
        by_doi.setdefault(d, r)
    t = norm(r['title'])
    if len(t) >= 25:
        by_title.setdefault(t, []).append(r)
title_keys = sorted(by_title, key=len, reverse=True)
STOP = set('a an the of for in on with and to by via using based from is are as at'.split())


def toks(s):
    return {w for w in re.findall(r'[a-z0-9]+', (s or '').lower()) if w not in STOP and len(w) > 2}


rec_toks = [(toks(r['title']), r) for r in recs]
GEN_TERMS = ['smote', 'oversampling', 'over-sampling', 'synthetic minority', 'adaptive synthetic', 'synthetic samples', 'synthetic instances']
IMB_TERMS = ['imbalanced', 'imbalance', 'minority class', 'minority classes']


def string_matches(text):
    """Whether a text holds a generation term and an imbalance term of the search string (Section 3.4)."""
    s = (text or '').lower()
    return any(g in s for g in GEN_TERMS) and any(i in s for i in IMB_TERMS)

# what Crossref holds for the references that have a DOI (scripts/reflist_fetch.py)
works = {}
for _f in (OUT / 'crossref_works').glob('*.json'):
    _w = json.load(open(_f, encoding='utf-8'))
    if 'error' not in _w:
        works[_w['doi']] = _w

# the corpus
corpus = json.load(open(V / 'data/openalex/2026-11-10/corpus_works.json', encoding='utf-8'))
corpus_doi = {ndoi(w.get('doi')) for w in corpus if w.get('doi')}
corpus_title = {norm(w['display_name']) for w in corpus if len(norm(w['display_name'])) >= 20}


def year_of(ref):
    _w = works.get(ndoi(ref.get('DOI')))
    if _w and _w.get('year'):
        return int(_w['year'])
    y = ref.get('year') or ''
    m = re.search(r'(19|20)\d\d', y)
    if m:
        return int(m.group(0))
    m = re.findall(r'\b((?:19|20)\d\d)\b', ref.get('unstructured') or '')
    return int(m[-1]) if m else None


def title_of(ref):
    """The reference's own title: Crossref's record of its DOI, else the title its review gave. A reference that Crossref
    lists by its proceedings volume alone has none."""
    _w = works.get(ndoi(ref.get('DOI')))
    return (_w or {}).get('title') or ref.get('article-title') or ''


def identified(ref):
    return bool(ndoi(ref.get('DOI')) or ref.get('article-title') or ref.get('unstructured'))


def match_record(ref):
    d = ndoi(ref.get('DOI'))
    if d and d in by_doi:
        return by_doi[d], 'doi'
    y = year_of(ref)
    t = norm(title_of(ref))
    cands = []
    if len(t) >= 25 and t in by_title:
        cands = by_title[t]
    elif not t:
        u = norm(ref.get('unstructured') or '')
        if len(u) >= 40:
            for k in title_keys:
                if len(k) >= 30 and k in u:
                    cands = by_title[k]
                    break
    for c in cands:
        try:
            cy = int(c['year'])
        except ValueError:
            cy = None
        if y is None or cy is None or abs(cy - y) <= 2:
            return c, 'title'
    # a close title: at least three quarters of the words of the two titles shared, the year within two
    a = toks(title_of(ref))
    if len(a) >= 4:
        best, bj = None, 0.0
        for b, c in rec_toks:
            if len(a & b) * 4 < len(a) * 3:
                continue
            j = len(a & b) / len(a | b)
            if j > bj:
                best, bj = c, j
        if best is not None and bj >= 0.75:
            try:
                cy = int(best['year'])
            except ValueError:
                cy = None
            if y is None or cy is None or abs(cy - y) <= 2:
                return best, 'close title'
    return None, ''


def in_corpus(ref):
    d = ndoi(ref.get('DOI'))
    if d and d in corpus_doi:
        return True
    t = norm(title_of(ref))
    if len(t) >= 20 and t in corpus_title:
        return True
    u = norm(ref.get('unstructured') or '')
    return bool(u) and any(len(c) >= 30 and c in u for c in corpus_title)


rows = []
for doi, name in REVIEWS.items():
    m = json.load(open(OUT / 'crossref' / (doi.replace('/', '_').replace('access', 'ACCESS') + '.json'), encoding='utf-8'))['message']
    assert ndoi(m['DOI']) == doi, (m['DOI'], doi)
    refs = m.get('reference', [])
    assert len(refs) == m.get('reference-count'), name
    for i, ref in enumerate(refs, 1):
        rec, how = match_record(ref)
        y = year_of(ref)
        title = title_of(ref) or ref.get('unstructured') or ref.get('volume-title') or ''
        rows.append(OrderedDict(review=name, n=i, identified='yes' if identified(ref) else 'no', doi=ndoi(ref.get('DOI')), year=y or '', title=' '.join(title.split()),
                                rec=rec['rec'] if rec else '', matched_by=how,
                                decision=dec[rec['rec']]['decision'] if rec else '', code=dec[rec['rec']]['code'] if rec else '',
                                in_corpus='yes' if in_corpus(ref) else 'no'))

with open(OUT / 'references.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)


def key(r):
    return r['rec'] or r['doi'] or norm(r['title'])[:80]


N = OrderedDict()
N['reviews'] = len(REVIEWS)
N['references_listed'] = len(rows)
per = OrderedDict()
for name in REVIEWS.values():
    rr = [r for r in rows if r['review'] == name]
    per[name] = OrderedDict(listed=len(rr), identified=sum(1 for r in rr if r['identified'] == 'yes'), in_records=sum(1 for r in rr if r['rec']),
                            pass_screen=sum(1 for r in rr if r['decision'] == 'include'),
                            in_corpus=sum(1 for r in rr if r['in_corpus'] == 'yes'))
N['by_review'] = per
N['references_identified'] = sum(1 for r in rows if r['identified'] == 'yes')
N['references_volume_only'] = len(rows) - N['references_identified']
dist = OrderedDict()
for r in rows:
    if r['identified'] == 'yes':
        dist.setdefault(key(r), r)
N['references_distinct'] = len(dist)
win = [r for r in dist.values() if r['year'] and int(r['year']) >= 2002]
N['distinct_2002_on'] = len(win)
N['distinct_before_2002_or_undated'] = len(dist) - len(win)
matched = [r for r in win if r['rec']]
N['in_records'] = len(matched)
N['in_records_include'] = sum(1 for r in matched if r['decision'] == 'include')
N['in_records_exclude'] = sum(1 for r in matched if r['decision'] == 'exclude')
N['in_records_exclude_by_code'] = dict(Counter(r['code'] for r in matched if r['decision'] == 'exclude').most_common())
N['not_in_records'] = len(win) - len(matched)
N['corpus_papers_cited'] = len({norm(r['title'])[:60] for r in dist.values() if r['in_corpus'] == 'yes'})
N['include_also_in_corpus'] = sum(1 for r in matched if r['decision'] == 'include' and r['in_corpus'] == 'yes')
assert N['in_records_include'] + N['in_records_exclude'] == N['in_records']

un = [r for r in win if not r['rec']]
with open(OUT / 'unmatched_window.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['key', 'review', 'n', 'doi', 'year', 'title', 'in_corpus'])
    for r in un:
        w.writerow([key(r), r['review'], r['n'], r['doi'], r['year'], r['title'], r['in_corpus']])

coded = OUT / 'unmatched_coded.csv'
if coded.exists():
    cr = list(csv.DictReader(open(coded, encoding='utf-8')))
    keys = {key(r) for r in un}
    assert {c['key'] for c in cr} == keys, 'unmatched_coded.csv does not hold exactly the unmatched references'
    assert all(c['code'] in ('generator', 'unclear', 'other') for c in cr)
    assert all(c['dup_of'] in keys for c in cr if c['dup_of'])
    one = [c for c in cr if not c['dup_of']]  # a work cited by two reviews without a DOI is counted once
    N['unmatched_duplicates'] = len(cr) - len(one)
    N['not_in_records_distinct'] = len(one)
    c = Counter(x['code'] for x in one)
    N['unmatched_generator'] = c.get('generator', 0)
    N['unmatched_unclear'] = c.get('unclear', 0)
    N['unmatched_other'] = c.get('other', 0)
    title_of_key = {key(r): r['title'] for r in un}
    doi_of_key = {key(r): r['doi'] for r in un}
    g = [x for x in one if x['code'] == 'generator']
    hit = 0
    for x in g:
        w = works.get(doi_of_key[x['key']]) or {}
        if string_matches(title_of_key[x['key']] + ' ' + (w.get('abstract') or '')):
            hit += 1
    N['unmatched_generator_string_in_title_or_abstract'] = hit
    N['unmatched_generator_string_absent'] = len(g) - hit
    N['unmatched_generator_with_abstract'] = sum(1 for x in g if (works.get(doi_of_key[x['key']]) or {}).get('abstract'))
    N['distinct_2002_on_after_duplicates'] = N['distinct_2002_on'] - N['unmatched_duplicates']
    elig = N['in_records_include'] + N['unmatched_generator']
    N['method_papers_total'] = elig
    N['method_papers_found_share_pct'] = round(100 * N['in_records_include'] / elig, 1) if elig else None
    # v0.56 (21 Nov 2026): an author's check of the works coded generator or unclear (column author_code, written by
    # team/reflist_check/apply_check_sheet.py). Where it exists, the counts of the paper use his codes.
    if any(x.get('author_code') for x in one):
        AC = ('generator', 'not a generator', 'cannot tell')
        chk = [x for x in one if x.get('author_code')]
        assert all(x['author_code'] in AC for x in chk)
        assert {x['key'] for x in chk} == {x['key'] for x in one if x['code'] in ('generator', 'unclear')}
        N['author_checked'] = len(chk)
        for a in AC:
            N['author_' + a.replace(' ', '_')] = sum(x['author_code'] == a for x in chk)
        for ai in ('generator', 'unclear'):
            for a in AC:
                N['ai_%s_author_%s' % (ai, a.replace(' ', '_'))] = sum(x['code'] == ai and x['author_code'] == a for x in chk)
        ga = [x for x in chk if x['author_code'] == 'generator']
        hit = [x for x in ga if string_matches(title_of_key[x['key']] + ' ' + ((works.get(doi_of_key[x['key']]) or {}).get('abstract') or ''))]
        hit_title = [x for x in ga if string_matches(title_of_key[x['key']])]
        N['author_generator_string_in_title'] = len(hit_title)
        N['author_generator_string_in_title_or_abstract'] = len(hit)
        N['author_generator_string_keys'] = sorted(x['key'] for x in hit)
        N['author_generator_with_abstract'] = sum(1 for x in ga if (works.get(doi_of_key[x['key']]) or {}).get('abstract'))
        lo = N['in_records_include'] + len(ga)
        hi = lo + N['author_cannot_tell']
        N['method_papers_total_author'] = lo
        N['method_papers_found_share_author_pct'] = round(100 * N['in_records_include'] / lo, 1)
        N['method_papers_total_author_with_cannot_tell'] = hi
        N['method_papers_found_share_author_with_cannot_tell_pct'] = round(100 * N['in_records_include'] / hi, 1)

json.dump(N, open(OUT / 'reflist_numbers.json', 'w', encoding='utf-8'), indent=1)
print(json.dumps(N, indent=1))
