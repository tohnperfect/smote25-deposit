#!/usr/bin/env python3
"""After scripts/openalex_snapshot.py: print the numbers of the reach table (Table 14) and recompute
the citation statistics of Section 6.9 from one snapshot, so that the draft can quote one date.

Usage: python3 scripts/after_snapshot.py data/openalex/<date> <team-repo-root>
Writes data/openalex/<date>/derived.json.
"""
import json
import statistics
import sys
from pathlib import Path

snap, repo = Path(sys.argv[1]), Path(sys.argv[2])
J = lambda n: json.loads((snap / n).read_text(encoding='utf-8'))  # noqa: E731
out = {}
total = J('citing_count.json')['meta']['count']
out['smote_cited_by_count'] = J('smote_work.json')['cited_by_count']
out['citing_works'] = total
out['citing_with_topic'] = J('citing_with_topic.json')['meta']['count']


def groups(name):
    return sorted(J(name)['group_by'], key=lambda g: -g['count'])


yrs = {int(g['key']): g['count'] for g in J('group_publication_year.json')['group_by'] if str(g['key']).isdigit()}
out['by_year'] = dict(sorted(yrs.items()))
out['up_to_2017'] = sum(c for y, c in yrs.items() if y <= 2017)
out['from_2018'] = sum(c for y, c in yrs.items() if y >= 2018)
out['domains'] = [(g['key_display_name'], g['count']) for g in groups('group_primary_topic_domain_id.json')]
f = groups('group_primary_topic_field_id.json')
out['fields_top6'] = [(g['key_display_name'], g['count']) for g in f[:6]]
out['fields_rest'] = (len(f) - 6, sum(g['count'] for g in f[6:]))
out['sdg'] = [(g['key_display_name'], g['count']) for g in groups('group_sustainable_development_goals_id.json')]
c = groups('group_authorships_countries.json')
out['countries_n'] = len([g for g in c if g['key'] not in (None, 'unknown', '')])
out['countries_top25'] = [(g['key_display_name'], g['count']) for g in c[:25]]
out['types'] = [(g['key_display_name'], g['count']) for g in groups('group_type.json')]

# Section 6.9: citation statistics of the empirical studies, with the counts of this snapshot
ev = json.loads((repo / 'Evaluation section/section07-coded-data.json').read_text(encoding='utf-8'))
new = {w['id'].rsplit('/', 1)[-1]: w['cited_by_count'] for w in J('corpus_works.json')}
extra = J('extra_works.json')
second = {k: v for k, v in extra.items() if k.startswith('second:')}  # second OpenAlex records of split papers
emp = []
for r in ev:
    if not r.get('empirical'):
        continue
    cnt = new.get(r.get('openalex_id') or '')
    for k, v in second.items():
        if k == 'second:' + r['key']:
            cnt = (cnt or 0) + v['cited_by_count']
    emp.append(dict(key=r['key'], year=r['year'], old=r.get('cites'), new=cnt, n_real=r['datasets'].get('n_real'),
                    test=r.get('test_class')))
top = sorted([e for e in emp if e['new'] is not None], key=lambda e: -e['new'])[:10]
out['top10'] = [(e['key'], e['year'], e['old'], e['new']) for e in top]
out['top10_median_real_datasets'] = statistics.median([e['n_real'] for e in top])
out['top10_with_test'] = sum(1 for e in top if e['test'] not in (None, 'None'))
out['top10_before_2010'] = sum(1 for e in top if e['year'] < 2010)
out['top10_same_as_18oct'] = [e['key'] for e in top] == [e['key'] for e in sorted([e for e in emp if e['old'] is not None], key=lambda e: -e['old'])[:10]]
out['saito2015'] = extra.get('saito2015precision', {}).get('cited_by_count')
(snap / 'derived.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
for k, v in out.items():
    if k not in ('by_year', 'countries_top25'):
        print(f'{k}: {v}')
print('countries_top25:', ', '.join(f'{n} {c}' for n, c in out['countries_top25']))
