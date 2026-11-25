#!/usr/bin/env python3
"""WP3, AI adjudication of the 4 Method and 11 Evaluation differences (D31), from both passes' evidence and the paper's
text (corpus/txt). Writes wp3/adjudication/METHOD_adjudicated.csv and EVALUATION_adjudicated.csv (every compared
row; agreements are marked "agree"). Usage: python3 -I wp3/adjudication/adjudicate_method_evaluation.py DRAFT_DIR
"""
import csv
import sys
from pathlib import Path

R = Path(sys.argv[1])
BY = 'AI adjudication (Claude Opus 5.5, 12 Nov 2026)'
M = {
    ('Loyalty-SMOTE', 'class'): ('first', 'B', 'the team\'s decision of 10 Nov on Loyalty-SMOTE (class B) stands; its multiclass experiments apply the binary method pairwise'),
    ('Loyalty-SMOTE', 'N'): ('first', 'y', 'the partners come from a restricted pool (the boundary set), as the second pass itself reads it; low confidence, for the spot check'),
    ('NROMM', 'S'): ('second', 'n', 'supp. Alg. 3 step 9: every minority sample is a seed; the type changes the generator (placement), not the seeds'),
    ('RSMOTE', 'N'): ('second', 'y', 'p.402 Step 3: partners are drawn within the seed\'s own cluster, so the neighbor choice changes'),
}
E = {
    ('AMDO-2018', 'resampling inside folds stated'): ('second', 'not said', 'Sec. 4.1 says five-fold cross-validation with 10 runs and nothing on where the resampling is applied'),
    ('GMMSampling-2024', 'how settings were chosen'): ('first', 'tuned inside training', 'Sec. 3: the number of GMM components is chosen on a train/development split of the training minority class'),
    ('MKC-SMOTE-2024', 'how settings were chosen'): ('second', 'fixed', 'the main results use R defaults and k = 5 (Table 2, Algorithm 1); the comparison of k = 3, 5, 7 (Table 6) is a later sensitivity check'),
    ('MKC-SMOTE-2024', 'a measure defined wrongly'): ('second', 'y', 'Eq. 4 (p.196934) prints the G-mean with TP/(TN+FP) as its second factor'),
    ('RBBoost-2015', 'how settings were chosen'): ('second', 'fixed', 'Sec. 6 (p.101) states the settings (ensemble size 100, J48 options, SMOTE amounts)'),
    ('CISO-2025', 'how settings were chosen'): ('second', 'fixed', 'pp.16-17: chosen once on five tuning-only data sets, then frozen for the 45 evaluation sets'),
    ('CISO-2025', 'real datasets (n)'): ('second', '45', 'Table 1 (p.16): 37 KEEL and 8 UCI sets are evaluated; the 5 KEEL sets of Table 2 serve tuning only'),
    ('FW-SMOTE-2022', 'resampling inside folds stated'): ('first', 'y', 'p.8: "the test set remains unseen until the final performance assessment for all models", which covers the oversampling; moderate confidence'),
    ('Global-CS-2006', 'how settings were chosen'): ('first', 'fixed', 'the method\'s own setting is stated (epsilon = 1/n_i) and nothing is tuned'),
    ('OSS-1997', 'how settings were chosen'): ('second', 'not said', 'no parameter of the method; the settings of 1-NN and C4.5 are not reported'),
    ('SOUP-2019', 'a measure defined wrongly'): ('second', 'y', 'p.775: the G-mean is printed over the minority classes only (n = number of minority classes), not the G-mean the paper reports'),
}
for name, dec, idcol in (('METHOD', M, 'paper'), ('EVALUATION', E, 'study')):
    rows = list(csv.DictReader(open(R / f'data/wp3_blind/{name}_comparison_for_adjudication.csv', encoding='utf-8')))
    out, used = [], set()
    for r in rows:
        key = (r[idcol], r['field'])
        if r['agree'] == 'True':
            adj, val, note = 'agree', r['first_pass'], ''
        elif key in dec:
            adj, val, note = dec[key]
            used.add(key)
        else:
            sys.exit(f'no decision for {name} {key}')
        r = {k: v for k, v in r.items() if k != 'adjudication'}
        out.append({**r, 'adjudication': adj, 'adjudicated_value': val, 'adjudication_note': note, 'decided_by': BY if adj != 'agree' else ''})
    if set(dec) - used:
        sys.exit(f'unused decisions {set(dec) - used}')
    with open(R / f'wp3/adjudication/{name}_adjudicated.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(name, len(out), 'rows,', len(used), 'adjudicated')
