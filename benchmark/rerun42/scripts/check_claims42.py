#!/usr/bin/env python3
"""WP6.8 step 3: print the numbers behind each claim of Section 9.2 and Appendix F (v0.10) from a stats42.py output
folder, so that a person or a session can see whether the text still holds after new tasks are added: every variant
within the region of practical equivalence of SMOTE (C1), the Holm-corrected tests, AB-SMOTE and FW-SMOTE with a lower
G-mean and Brier score, Safe-Level-SMOTE with a higher Brier score (random forest), the baselines (no resampling: same
ROC-AUC and PR-AUC, lower Brier score; tuned threshold: higher G-mean), the spread within families and the sampler
errors. Differences are method minus SMOTE; for the Brier score the sign is flipped, so that positive is better.
Usage: python3 -I check_claims42.py benchmark/results_summary/rerun42
"""
import json
import sys
from pathlib import Path

import pandas as pd

S = Path(sys.argv[1])
t = pd.read_csv(S / 'tests_vs_smote.csv')
summ = json.load(open(S / 'summary.json'))
VAR = ['Borderline-SMOTE', 'ADASYN', 'Safe-Level-SMOTE', 'Cluster-SMOTE', 'G-SMOTE', 'SMOM', 'AB-SMOTE', 'FW-SMOTE',
       'RSMOTE', 'CGMOS']
VAR = [v for v in VAR if v in set(t['method'])]
print('methods in tests:', sorted(set(t['method'])))
print('tasks', summ['tasks'], 'families', summ['families'], 'cells', summ['fold_results'], summ['cells_by_status'])
print('incomplete left out:', summ['tasks_incomplete_left_out'])
print('sampler errors:')
for m, ts in sorted(summ['sampler_error_tasks'].items()):
    if ts:
        print('  ', m, ts)


def row(m, ln, me):
    h = t[(t.method == m) & (t.learner == ln) & (t.measure == me)]
    return None if h.empty else h.iloc[0]


print('\n1. variants vs SMOTE (ROC/PR x RF/GB): max |median diff| and Holm-significant count')
mx, sig, n = 0, 0, 0
for m in VAR:
    for ln in ['RF', 'GB']:
        for me in ['roc_auc', 'pr_auc']:
            r = row(m, ln, me)
            if r is None:
                print('   missing', m, ln, me)
                continue
            n += 1
            mx = max(mx, abs(r.median_diff_vs_smote))
            if r.holm_p < 0.05:
                sig += 1
                print('   SIG', m, ln, me, r.median_diff_vs_smote, r.holm_p)
            if r.median_diff_vs_smote < -0.01:
                print('   FAILS C1', m, ln, me, r.median_diff_vs_smote)
print(f'   max |diff| {mx:.4f}; significant {sig} of {n}; families per test', sorted(set(t[t.method.isin(VAR) & t.learner.isin(["RF","GB"]) & t.measure.isin(["roc_auc","pr_auc"])].n_families)))

print('\n2. G-mean and Brier for AB-SMOTE, FW-SMOTE, Safe-Level-SMOTE (diff = method minus SMOTE; Brier sign flipped so + = better)')
for m in ['AB-SMOTE', 'FW-SMOTE', 'Safe-Level-SMOTE']:
    for ln in ['RF', 'GB']:
        g = row(m, ln, 'gmean')
        b = row(m, ln, 'brier')
        print(f'   {m:18s} {ln}: gmean {g.median_diff_vs_smote:+.4f} (holm {g.holm_p:.3g})  brier(+better) {b.median_diff_vs_smote:+.4f} (holm {b.holm_p:.3g})')

print('\n3. baselines')
for m in ['none', 'class_weight', 'threshold', 'ROS']:
    for ln in ['RF', 'GB']:
        out = []
        for me in ['roc_auc', 'pr_auc', 'gmean', 'brier']:
            r = row(m, ln, me)
            if r is None:
                out.append(f'{me} -')
                continue
            out.append(f'{me} {r.median_diff_vs_smote:+.4f} (holm {r.holm_p:.3g}; P smote>{r.p_smote_better:.2f} rope {r.p_rope:.2f} m> {r.p_method_better:.2f})')
        print(f'   {m:12s} {ln}: ' + ' | '.join(out))

print('\n4. all Holm-significant comparisons with RF/GB on ROC/PR')
h = t[(t.holm_p < 0.05) & t.learner.isin(['RF', 'GB']) & t.measure.isin(['roc_auc', 'pr_auc'])]
print(h[['learner', 'measure', 'method', 'median_diff_vs_smote', 'holm_p']].to_string())

print('\n5. per-family spread of the ten methods (ROC-AUC, RF)')
pf = pd.read_csv(S / 'per_family_means.csv')
ten = ['SMOTE'] + VAR
x = pf[(pf.learner == 'RF') & pf.method.isin(ten)]
rng = x.groupby('family')['roc_auc'].agg(lambda s: s.max() - s.min())
fam_smote = set(x[x.method == 'SMOTE'].dropna(subset=['roc_auc']).family)
rng2 = rng[rng.index.isin(fam_smote)]
print(f'   median range {rng2.median():.4f}; >0.01 in {(rng2 > 0.01).sum()} of {len(rng2)} families (SMOTE ran)')
print('\n6. c1_rerun.csv')
print(pd.read_csv(S / 'c1_rerun.csv').to_string())
