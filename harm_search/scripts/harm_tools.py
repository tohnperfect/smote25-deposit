#!/usr/bin/env python3
"""Tools for the AI screeners of the WP5 harm search (one batch each).

  python3 -I harm_tools.py show NN FIRST LAST        print records FIRST..LAST of batch NN (numbered from 1 in the batch)
  python3 -I harm_tools.py add NN CHUNK.json         check a chunk of decisions and append it to work/decisions/batch_NN.json
  python3 -I harm_tools.py status NN                 how many records of batch NN are decided, and the next one
  python3 -I harm_tools.py checkall                  check every decisions file against its batch (for the coordinator)

A chunk is a JSON array of objects with the keys of the codebook, in batch order, starting at the next undecided
record. Every value is a string. The quote must be a verbatim substring of the title or abstract (whitespace is
normalized), at most 25 words. Nothing is appended unless the whole chunk passes.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECS = os.path.join(HERE, 'work', 'records.json')
DEC = os.path.join(HERE, 'work', 'decisions')
SIZE = 75
KEYS = ['pmid', 'decision', 'code', 'harms', 'comparison', 'finding', 'data', 'domain', 'reason', 'quote', 'confidence']
CODES = {'include': {'H-calibration', 'H-leakage', 'H-privacy', 'H-fairness'},
         'exclude': {'X-not-resampling', 'X-no-comparison', 'X-no-harm-measure', 'X-not-study'},
         'unsure': {'U-abstract'}}
HARMS = {'calibration', 'leakage', 'privacy', 'fairness'}
COMP = {'no resampling', 'before vs after split', 'both', 'not stated'}
FIND = {'harm', 'no harm', 'mixed', 'not reported', 'n/a'}
DATA = {'real', 'simulated', 'both', 'not stated'}
CONF = {'high', 'medium', 'low'}


def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip().lower()


def batch(nn):
    recs = json.load(open(RECS, encoding='utf-8'))
    b = int(nn)
    return recs[(b - 1) * SIZE: b * SIZE]


def done(nn):
    p = os.path.join(DEC, f'batch_{int(nn):02d}.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []


def check_row(row, rec):
    err = []
    if list(row.keys()) != KEYS:
        return [f'keys must be exactly {KEYS}']
    if any(not isinstance(v, str) for v in row.values()):
        err.append('every value must be a string')
        return err
    if row['pmid'] != rec['pmid']:
        err.append(f'pmid {row["pmid"]} but the next record is {rec["pmid"]}')
    d = row['decision']
    if d not in CODES:
        err.append('decision must be include, exclude or unsure')
    elif row['code'] not in CODES[d]:
        err.append(f'code {row["code"]} not allowed for {d}')
    hs = [h.strip() for h in row['harms'].split(';') if h.strip()]
    if any(h not in HARMS for h in hs):
        err.append(f'harms must come from {sorted(HARMS)}')
    if d == 'include' and row['code'][2:] not in hs:
        err.append('an include lists its own harm in harms')
    if row['comparison'] not in COMP:
        err.append(f'comparison must be one of {sorted(COMP)}')
    if d == 'include' and row['comparison'] == 'not stated':
        err.append('an include needs a comparison')
    if d == 'include' and row['code'] != 'H-leakage' and row['comparison'] == 'before vs after split':
        err.append('only leakage includes may rest on a before-vs-after comparison alone')
    if row['finding'] not in FIND:
        err.append(f'finding must be one of {sorted(FIND)}')
    if d == 'exclude' and row['finding'] != 'n/a':
        err.append('an exclude has finding n/a')
    if d != 'exclude' and row['finding'] == 'n/a':
        err.append('an include or unsure has a finding other than n/a')
    if row['data'] not in DATA:
        err.append(f'data must be one of {sorted(DATA)}')
    if row['confidence'] not in CONF:
        err.append('confidence must be high, medium or low')
    if not row['reason'].strip():
        err.append('reason is empty')
    src = norm(rec['title'] + ' ' + rec['abstract'])
    q = norm(row['quote'])
    if rec['abstract'] and not q:
        err.append('quote is empty but the record has an abstract')
    if q and q not in src:
        err.append('quote is not a verbatim substring of the title or abstract')
    if len(row['quote'].split()) > 25:
        err.append('quote longer than 25 words')
    return err


def show(nn, first, last):
    for i, r in enumerate(batch(nn)[first - 1:last], first):
        print('=' * 20)
        print(f'#{i} PMID {r["pmid"]} | {r["year"]} | {r["journal"]} | {"; ".join(r["publication_types"])} | queries {"+".join(r["queries"])}')
        print('TI:', r['title'])
        print(r['abstract'] or '[no abstract]')


def add(nn, chunk_path):
    recs, have = batch(nn), done(nn)
    chunk = json.load(open(chunk_path, encoding='utf-8'))
    if not isinstance(chunk, list) or not chunk:
        sys.exit('ERROR: the chunk must be a non-empty JSON array')
    errs = []
    for k, row in enumerate(chunk):
        i = len(have) + k
        if i >= len(recs):
            errs.append(f'row {k + 1}: the batch has only {len(recs)} records')
            break
        errs += [f'row {k + 1} (record {i + 1}, PMID {recs[i]["pmid"]}): {e}' for e in check_row(row, recs[i])]
    if errs:
        sys.exit('ERROR, nothing appended:\n' + '\n'.join(errs))
    os.makedirs(DEC, exist_ok=True)
    json.dump(have + chunk, open(os.path.join(DEC, f'batch_{int(nn):02d}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    status(nn)


def status(nn):
    recs, have = batch(nn), done(nn)
    c = {}
    for r in have:
        c[r['decision']] = c.get(r['decision'], 0) + 1
    nxt = len(have) + 1
    print(f'batch {int(nn):02d}: {len(have)} of {len(recs)} decided {c}; ' +
          (f'next record {nxt}' if nxt <= len(recs) else 'all decided'))


def checkall():
    recs = json.load(open(RECS, encoding='utf-8'))
    nb = (len(recs) + SIZE - 1) // SIZE
    bad = 0
    for b in range(1, nb + 1):
        rs, have = batch(b), done(b)
        errs = [f'record {i + 1}: {e}' for i, (row, rec) in enumerate(zip(have, rs)) for e in check_row(row, rec)]
        print(f'batch {b:02d}: {len(have)} of {len(rs)} decided; {len(errs)} errors')
        bad += len(errs) + (len(rs) - len(have))
        for e in errs[:5]:
            print('  ', e)
    print('ALL OK' if bad == 0 else f'NOT COMPLETE: {bad} problems')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'show':
        show(a[1], int(a[2]), int(a[3]))
    elif a[0] == 'add':
        add(a[1], a[2])
    elif a[0] == 'status':
        status(a[1])
    elif a[0] == 'checkall':
        checkall()
    else:
        sys.exit(__doc__)
