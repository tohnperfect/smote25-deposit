#!/usr/bin/env python3
"""WP3, AI adjudication of the 269 differences of the Data extraction (D31), under the team lead's conventions of
12 November 2026: D32 (a two-class set whose class count is not printed: 2, flagged inferred), D33 (a value that
follows exactly from printed numbers counts as printed, flagged derived), D35 (the proposed method is the variant the
abstract names as the contribution; if several, the first named).

Groups (column `category` of data/wp3_blind/DATA_extraction_disagreements_for_adjudication.csv):
  A   first pass 2, second NR: D32, the first pass stands (inferred).
  D   first pass blank, second found a value: D33, the second pass stands; flagged derived where the value is computed
      from printed numbers (the smallest class of a printed distribution, a sum), printed otherwise. A multiclass set
      without a minority the paper defines takes the smallest printed class as its minority size (derived).
  E1, F  the same value written differently: both stand.
  C, E2  decided one by one from the second pass's page and quote and the paper's text (corpus/txt): the decisions are
      in DECISIONS below, each with its reason.
Writes wp3/adjudication/DATA_extraction_adjudicated.csv: the input columns plus adjudication (first, second, both,
both wrong), adjudicated_value, flag (printed, inferred, derived) and adjudication_note; decided_by is "AI
adjudication (Claude Opus 5.5, 12 Nov 2026)". Usage: python3 -I wp3/adjudication/adjudicate_data_extraction.py DRAFT_DIR
"""
import csv
import re
import sys
from pathlib import Path

R = Path(sys.argv[1])
SRC = R / 'data/wp3_blind/DATA_extraction_disagreements_for_adjudication.csv'
OUT = R / 'wp3/adjudication/DATA_extraction_adjudicated.csv'
BY = 'AI adjudication (Claude Opus 5.5, 12 Nov 2026)'

# (check_id, field) -> (adjudication, value, flag, note); values checked against the second pass's quotes and the text
DECISIONS = {
    ('D034', 'n_instances'): ('both wrong', '125841', 'derived', 'p.5726: training 62,309 and testing 63,532 samples are printed; their sum is the size (D33)'),
    ('D034', 'n_minority'): ('both wrong', '28203', 'derived', 'p.5726: minority 14,602 in training and 13,601 in testing (D33)'),
    ('D072', 'n_classes'): ('first', '10', 'derived', 'Sec. 4.2 (p.1701) prints ten class sizes; class count follows (D33)'),
    ('D072', 'n_minority'): ('both wrong', '80', 'derived', 'multiclass without a defined minority: smallest printed class (80) (D33)'),
    ('D073', 'n_minority'): ('both wrong', '40', 'derived', 'multiclass without a defined minority: smallest printed class (40) (D33)'),
    ('D076', 'n_classes'): ('first', '6', 'derived', 'Table 1 (p.8) prints six class sizes 70/76/17/13/9/29 (D33)'),
    ('D128', 'n_minority'): ('both wrong', '13', 'derived', 'Table 1 (p.8) distribution 164/55/36/35/13: smallest class (D33)'),
    ('D129', 'n_minority'): ('both wrong', '166', 'derived', 'Table 1 (p.8) distribution 166/368/6666: smallest class (D33)'),
    ('D130', 'n_minority'): ('both wrong', '48', 'derived', 'Table 1 (p.8) distribution 59/71/48: smallest class (D33)'),
    ('R045', 'smote'): ('second', 'NR', 'printed', 'Tables 9-13 head no column SMOTE (the first column is headed MDO); not printed as SMOTE, as the wins analysis already treats MC-MBRC (excluded)'),
    ('R046', 'smote'): ('second', 'NR', 'printed', 'as R045'),
    ('R047', 'smote'): ('second', 'NR', 'printed', 'as R045'),
    ('R058', 'proposed'): ('first', '95.74', 'printed', 'D35: the abstract names no single variant; the first the paper names is NB-Basic, 95.74 (equal to NB-Comm)'),
    ('R059', 'proposed'): ('both wrong', '40', 'printed', 'D35: NB-Basic, the first variant the paper names; Table 4 prints 40'),
    ('R060', 'proposed'): ('both wrong', '57.9', 'printed', 'D35: NB-Basic, Table 4 prints 57.9'),
    ('R061', 'proposed'): ('first', '97.7', 'printed', 'D35: NB-Basic 97.7 (equal to NB-Comm)'),
    ('R066', 'proposed'): ('both wrong', '0.7919', 'printed', 'D35: RACOG, named first in the abstract; Table 5 G-mean 0.7919'),
    ('R067', 'proposed'): ('both wrong', '0.5586', 'printed', 'D35: RACOG; Table 5 G-mean 0.5586'),
    ('D220', 'n_minority'): ('both wrong', '5', 'derived', 'Table 1 distribution 244/429/463/44/51/163/35/30/20/5: smallest class (D33)'),
    ('D221', 'n_minority'): ('both wrong', '5', 'derived', 'Table 1 distribution 30/216/2138/2836/1079/193/5: smallest class (D33)'),
    ('D231', 'n_classes'): ('first', '2', 'derived', 'Table 2 (p.334) prints the two classes kept, majority 35,754 and minority 2,747 (D33)'),
    ('D231', 'n_instances'): ('both wrong', '38501', 'derived', 'Table 2 (p.334): 35,754 + 2,747 (D33)'),
    ('R086', 'proposed'): ('both wrong', '41.80', 'printed', 'D35: Smote + Tomek, named first in the abstract; Table 4, pruned, 41.80'),
    ('R087', 'proposed'): ('both wrong', '81.75', 'printed', 'D35: Smote + Tomek, Table 4, pruned, 81.75'),
    ('R088', 'proposed'): ('both wrong', '95.98', 'printed', 'D35: Smote + Tomek, Table 4, pruned, 95.98'),
    ('R091', 'proposed'): ('first', '77.37', 'printed', 'SMOTEBoost and SMOTE at the same amount N = 100 (Table 6, p.114), as the wins analysis pairs them'),
    ('R091', 'smote'): ('first', '68.89', 'printed', 'SMOTE at N = 100, matched to SMOTEBoost (Table 6, p.114)'),
    ('D110', 'n_classes'): ('first', '2', 'printed', 'each apportion used is two-class (Table 1, p.2815); 14 is the source set\'s class count (p.2816)'),
    ('R092', 'proposed'): ('second', '0.675', 'printed', 'D35: the abstract names no variant; VE is the first of the three the paper names, and the text gives 0.675 as "our method" on Shoppers; Table 2 prints 0.675 for VE'),
}
DERIVED = re.compile(r'smallest|sum|n=\d|n_min=|\+ #F|total not printed|no total|follows', re.I)

rows = list(csv.DictReader(open(SRC, encoding='utf-8')))
out = []
for r in rows:
    g = r['category'].split()[0]
    key = (r['check_id'], r['field'])
    if key in DECISIONS:
        adj, val, flag, note = DECISIONS[key]
    elif g == 'A':
        adj, val, flag, note = 'first', r['first_extraction'], 'inferred', 'D32: two-class set whose class count is not printed; recorded 2, flagged inferred'
    elif g == 'D':
        flag = 'derived' if DERIVED.search(r['second_pass_note']) else 'printed'
        adj, val, note = 'second', r['second_pass'], 'D33: the value is printed or follows exactly from printed numbers (second pass: ' + r['second_pass_note'][:160] + ')'
    elif g in ('E1', 'F'):
        adj, val, flag, note = 'both', r['first_extraction'], 'printed', 'the same value written differently'
    else:
        sys.exit(f'no decision for {key} ({g})')
    out.append({**r, 'adjudication': adj, 'adjudicated_value': val, 'flag': flag, 'adjudication_note': note, 'decided_by': BY})
cols = list(rows[0].keys()) + ['adjudicated_value', 'flag', 'decided_by']
cols = [c for c in cols if c not in ('adjudication', 'adjudication_note')] + ['adjudication', 'adjudication_note']
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols)
    w.writeheader()
    w.writerows(out)
from collections import Counter
print(len(out), dict(Counter(o['adjudication'] for o in out)), dict(Counter(o['flag'] for o in out)))
unused = set(DECISIONS) - {(r['check_id'], r['field']) for r in rows}
if unused:
    sys.exit(f'decisions for rows not in the file: {unused}')
