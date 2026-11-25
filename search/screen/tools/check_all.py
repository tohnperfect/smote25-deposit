#!/usr/bin/env python3
"""Check every finished batch: same records as its input, in order, one row each; report totals and incomplete batches."""
import csv, collections, glob, os
csv.field_size_limit(10**9)
S = '/home/claude/work/screen_full'
tot = collections.Counter(); complete = []; partial = []; bad = []
for f in sorted(glob.glob(f'{S}/batches/batch*_to_screen.csv')):
    nnn = f.split('batch')[-1][:3]
    recs = [r['rec'] for r in csv.DictReader(open(f, encoding='utf-8'))]
    o = f'{S}/out/batch{nnn}_screened.csv'
    if not os.path.exists(o):
        continue
    rows = list(csv.DictReader(open(o, encoding='utf-8')))
    got = [r['rec'] for r in rows]
    if got != recs[:len(got)]:
        bad.append(nnn); continue
    if len(got) == len(recs) and os.path.exists(f'{S}/out/batch{nnn}_DONE.txt'):
        complete.append(nnn); tot.update(r['decision'] for r in rows)
    else:
        partial.append(f'{nnn}:{len(got)}/{len(recs)}')
n = sum(tot.values())
print(f'complete {len(complete)}: {" ".join(complete)}')
print(f'partial {len(partial)}: {" ".join(partial)}')
print(f'bad {bad}')
if n:
    print(f'records in complete batches {n}: ' + ', '.join(f'{k} {v} ({100*v/n:.1f}%)' for k, v in sorted(tot.items())))
