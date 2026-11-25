#!/usr/bin/env python3
"""Build the coding batches of the coverage sample or the use audit from a drawn sample and the fetched full texts.

coverage: only records with a usable full text are coded (the rest wait for the team's PDFs); batches of SIZE.
useaudit: every drawn record is coded; records in the full-text target with a usable text get it, the others are coded
from title and abstract (and recoded from the full text when the team supplies it).
Texts are copied into PROJECT/text/; a record already coded is not batched again.
Usage: python3 -I make_coding_batches.py PROJECT SAMPLE.csv FETCH_LOG.csv TEXT_DIR SIZE
"""
import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schema import ROOT

csv.field_size_limit(10**9)
proj, sample, logp, textdir, size = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), int(sys.argv[5])
R = Path(ROOT[proj])
(R / 'batches').mkdir(parents=True, exist_ok=True)
(R / 'text').mkdir(parents=True, exist_ok=True)
log = {r['rec']: r for r in csv.DictReader(open(logp, encoding='utf-8'))}
coded = set()
for f in (R / 'out').glob('batch*_coded.csv'):
    coded |= {r['rec'] for r in csv.DictReader(open(f, encoding='utf-8'))}
todo = []
for r in csv.DictReader(open(sample, encoding='utf-8')):
    if r['rec'] in coded:
        continue
    has = log.get(r['rec'], {}).get('usable') == 'yes' and (textdir / f"{r['rec']}.txt").exists()
    if proj == 'coverage' and not has:
        continue
    if has and r['target'] == 'fulltext':
        shutil.copy2(textdir / f"{r['rec']}.txt", R / 'text' / f"{r['rec']}.txt")
    todo.append(r)
existing = sorted((R / 'batches').glob('batch*.csv'))
start = len(existing) + 1
cols = ['rec', 'stratum', 'order', 'year', 'venue', 'doi', 'title', 'abstract']
made = []
for i in range(0, len(todo), size):
    nnn = f'{start + i // size:03d}'
    with open(R / f'batches/batch{nnn}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(todo[i:i + size])
    made.append(nnn)
print(f'{proj}: {len(todo)} records in {len(made)} new batches {made[:1]}..{made[-1:]}; texts: {len(list((R / "text").glob("*.txt")))}')
