#!/usr/bin/env python3
"""WP6 step 6: statistics for the independent benchmark.

The dataset is the unit, and one source family counts once: fold results are averaged per
(dataset, method, learner), then datasets of the same source family (ecoli1, ecoli-0-1_vs_5 -> ecoli)
are averaged. Per learner and measure: Friedman test with the Iman-Davenport correction; Wilcoxon
signed-rank tests of every method against SMOTE with Holm correction; Bayesian signed-rank test against
SMOTE with a region of practical equivalence of 0.01 (baycomp); median difference as effect size.
A method that failed in every fold of a family has no mean there (SMOTE with five neighbors cannot run when a
training fold holds five or fewer minority examples). Families without SMOTE are left out; a method present on fewer
than 80 percent of the remaining families is left out; each method is compared with SMOTE on the families where both
ran, and the Friedman test uses the families where every kept method ran. (Until 11 Nov 2026 a single failed family
removed the method from every test, which emptied the core-tier tests; fixed before any result was read.)
Usage: python3 benchmark/stats.py benchmark/results benchmark/results/stats
       python3 benchmark/stats.py --from-means <per_family_means.csv> <out_dir>   (tests only)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

MEASURES = ['roc_auc', 'pr_auc', 'gmean', 'f1', 'mcc', 'bacc', 'brier', 'ece']
LOWER_IS_BETTER = {'brier', 'ece'}


def family(name):
    name = re.sub(r'^oml_', '', name)          # OpenML sets of the high-dimensional tier: oml_OVA_Lung -> ova
    return re.split(r'[-_0-9]', name.lower(), maxsplit=1)[0] or name


def holm(ps):
    order = np.argsort(ps)
    adj, run = np.empty(len(ps)), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def main():
    if sys.argv[1] == '--from-means':
        per_fam, out = pd.read_csv(sys.argv[2]), Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        res = tests(per_fam)
        pd.DataFrame(res).to_csv(out / 'tests_vs_smote.csv', index=False)
        print(f'{per_fam.family.nunique()} families; {len(res)} method-vs-SMOTE comparisons written to {out}')
        return
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in src.glob('*.jsonl'):
        for line in f.open():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:   # a line cut short when the run was stopped
                pass
    df = pd.DataFrame([r for r in rows if r.get('status') == 'ok'])
    df['family'] = df['dataset'].map(family)
    per_ds = df.groupby(['family', 'dataset', 'method', 'learner'])[MEASURES].mean().reset_index()
    per_fam = per_ds.groupby(['family', 'method', 'learner'])[MEASURES].mean().reset_index()
    per_fam.to_csv(out / 'per_family_means.csv', index=False)
    res = tests(per_fam)
    pd.DataFrame(res).to_csv(out / 'tests_vs_smote.csv', index=False)
    print(f'{len(df)} fold results; {per_fam.family.nunique()} families; {len(res)} method-vs-SMOTE comparisons written to {out}')


def tests(per_fam):
    res = []
    for ln, g in per_fam.groupby('learner'):
        for m in MEASURES:
            wide = g.pivot(index='family', columns='method', values=m)
            if 'SMOTE' not in wide:
                continue
            wide = wide[wide['SMOTE'].notna()]
            wide = wide[[c for c in wide if wide[c].notna().mean() >= 0.8]]
            complete = wide.dropna()
            if 'SMOTE' not in wide or complete.shape[0] < 3 or complete.shape[1] < 3:
                continue
            k, n = complete.shape[1], complete.shape[0]
            chi2, p_f = stats.friedmanchisquare(*[complete[c] for c in complete])
            ff = (n - 1) * chi2 / (n * (k - 1) - chi2) if n * (k - 1) != chi2 else np.inf
            p_id = 1 - stats.f.cdf(ff, k - 1, (k - 1) * (n - 1))
            others = [c for c in wide if c != 'SMOTE']
            pw = []
            for c in others:
                pair = wide[['SMOTE', c]].dropna()
                d = pair[c] - pair['SMOTE']
                if m in LOWER_IS_BETTER:
                    d = -d
                p = stats.wilcoxon(d).pvalue if np.any(d != 0) else 1.0
                try:
                    import baycomp
                    np.random.seed(20261110)   # baycomp samples with numpy's global generator: fixed for reproducibility
                    left, rope, right = baycomp.SignedRankTest.probs(pair['SMOTE'].values, pair[c].values, rope=0.01)
                    if m in LOWER_IS_BETTER:
                        left, right = right, left
                except Exception:  # noqa: BLE001
                    left = rope = right = np.nan
                pw.append((c, float(np.median(d)), p, left, rope, right, len(pair)))
            adj = holm(np.array([x[2] for x in pw]))
            for (c, med, p, pl, pr, pg, npair), a in zip(pw, adj):
                res.append(dict(learner=ln, measure=m, method=c, n_families=npair, n_friedman=n, k_methods=k,
                                friedman_p=p_f, iman_davenport_p=p_id, median_diff_vs_smote=med, wilcoxon_p=p,
                                holm_p=a, p_smote_better=pl, p_rope=pr, p_method_better=pg))
    return res


if __name__ == '__main__':
    main()
