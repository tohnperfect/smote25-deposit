#!/usr/bin/env python3
"""D42: cut the disagreements of the blind second coding into adjudication batches.

Every disagreement (one record, one field) becomes an item. Which coder's code is shown as A and which as B is drawn
per item by a hash of seed 20261124 and the item, so that the adjudicator cannot favor the first coding; the key is
written outside the adjudicators' folder (<private dir>/d42_adjudication_key.json). Items are grouped by record, and
records are cut into batches: use audit records coded from the abstract 40 per batch, records coded from a full text
(both projects) 8 per batch. Usage: python3 -I scripts/d42_adjud_batches.py <disagreements.csv> <adjudication dir>
<private dir> [--first-batch N --seed S]  (batches 301, 302, ... with seed 20261124 by default; refuses to overwrite).
Round 2 (v0.37): the differences of round 2 (d42/round2/disagreements.csv) with --first-batch 311 --seed 20261125; the
manifest of the adjudication dir gains the new batches.
"""
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

ARGS = sys.argv[1:]
OPT = {'--first-batch': 301, '--seed': 20261124}
for o in list(OPT):
    if o in ARGS:
        _i = ARGS.index(o)
        OPT[o] = int(ARGS[_i + 1])
        del ARGS[_i:_i + 2]
DIS, A, PRIV = (Path(a) for a in ARGS)
SEED = OPT['--seed']
rows = list(csv.DictReader(open(DIS, encoding='utf-8')))
if any(int(p.stem[3:6]) >= OPT['--first-batch'] for p in (A / 'batches').glob('adj*.csv')):
    raise SystemExit('adjudication batches with these numbers exist; remove them by hand first')
by_rec = collections.OrderedDict()
for r in rows:
    by_rec.setdefault((r['project'], r['rec']), []).append(r)
groups = {'abstract': [k for k, v in by_rec.items() if v[0]['source'] == 'abstract'],
          'fulltext': [k for k, v in by_rec.items() if v[0]['source'] != 'abstract']}
key, n_batch = {}, OPT['--first-batch']
manifest = json.load(open(A / 'manifest.json')) if (A / 'manifest.json').exists() else {}
for g, size in (('abstract', 40), ('fulltext', 8)):
    recs = sorted(groups[g], key=lambda k: (k[0], k[1]))
    for i in range(0, len(recs), size):
        nnn = f'{n_batch:03d}'
        n_batch += 1
        items = []
        for proj, rec in recs[i:i + size]:
            for r in by_rec[(proj, rec)]:
                item = f'{proj}:{rec}:{r["field"]}'
                first_is_a = int(hashlib.sha256(f'{SEED}:{item}'.encode()).hexdigest(), 16) % 2 == 0
                key[item] = 'A' if first_is_a else 'B'
                a, b = (r['first'], r['second']) if first_is_a else (r['second'], r['first'])
                items.append(dict(item=item, project=proj, rec=rec, field=r['field'], code_A=a, code_B=b))
        with open(A / f'batches/adj{nnn}.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, ['item', 'project', 'rec', 'field', 'code_A', 'code_B'])
            w.writeheader()
            w.writerows(items)
        manifest[nnn] = dict(group=g, records=len(recs[i:i + size]), items=len(items))
PRIV.mkdir(parents=True, exist_ok=True)
(PRIV / 'd42_adjudication_key.json').write_text(json.dumps(dict(seed=SEED, first_is=key), indent=0), encoding='utf-8')
(A / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
print(json.dumps(manifest))
