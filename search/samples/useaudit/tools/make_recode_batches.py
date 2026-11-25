#!/usr/bin/env python3
"""Build use-audit batches that recode, from the full text, the full-text targets first coded from title and abstract
(the library PDFs of 16 Nov 2026). make_coding_batches.py skips records already coded, so the recode needs its own
batches; consolidate_codes.py keeps the last code of a record, so the recode replaces the abstract code.

Only targets (sample column `target` = fulltext) whose text is usable in FETCH_LOG.csv and whose current code is from
the abstract are batched. Texts are copied into PROJECT/text/.
Usage: python3 -I make_recode_batches.py SAMPLE.csv FETCH_LOG.csv TEXT_DIR SIZE"""
import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import ROOT

csv.field_size_limit(10**9)
sample, logp, textdir, size = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
R = Path(ROOT['useaudit'])
log = {r['rec']: r for r in csv.DictReader(open(logp, encoding='utf-8'))}
last = {}
for f in sorted((R / 'out').glob('batch*_coded.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        last[r['rec']] = r
todo = []
for r in csv.DictReader(open(sample, encoding='utf-8')):
    if r['target'] != 'fulltext' or log.get(r['rec'], {}).get('usable') != 'yes':
        continue
    if not (textdir / f"{r['rec']}.txt").exists() or last.get(r['rec'], {}).get('source') == 'fulltext':
        continue
    shutil.copy2(textdir / f"{r['rec']}.txt", R / 'text' / f"{r['rec']}.txt")
    todo.append(r)
start = len(sorted((R / 'batches').glob('batch*.csv'))) + 1
cols = ['rec', 'stratum', 'order', 'year', 'venue', 'doi', 'title', 'abstract']
made = []
for i in range(0, len(todo), size):
    nnn = f'{start + i // size:03d}'
    with open(R / f'batches/batch{nnn}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(todo[i:i + size])
    made.append(nnn)
print(f'useaudit recode: {len(todo)} records in {len(made)} new batches {made[:1]}..{made[-1:]}; texts: {len(list((R / "text").glob("*.txt")))}')
