#!/usr/bin/env python3
"""WP6.8 step 3 (v0.11): which tasks of the rerun ran on which machine, and how far the tasks that ran on both agree.

The cloud workspace (Linux, x86) ran 38 tasks; the team lead's MacBook (Apple M5 Pro, the machine of the core tier) ran
the five tasks of at least 4,000 rows and smoke detection. Mammography and ijcnn1 therefore ran on both. stats42.py
reads the cloud folder first and keeps the first copy of a cell, so the tests use the cloud's copies of those two.
This script compares the two copies cell by cell (ROC-AUC, PR-AUC, G-mean and the Brier score) and through the
25-fold means per method and learner, including the differences from SMOTE with the random forest and gradient
boosting, and writes the result as JSON for the paper's Appendix F (search_numbers.py reads it).

Usage: python3 -I cross_machine42.py --out benchmark/results_summary/rerun42/cross_machine.json \
          --cloud <results_cloud> --mac <results_mac> [<results_mac_kaggle> ...]
"""
import argparse
import glob
import json
import os

import pandas as pd

MEASURES = ['roc_auc', 'pr_auc', 'gmean', 'brier']
KEY = ['dataset', 'repeat', 'fold', 'method', 'learner']


def load(dirs):
    rows = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
            with open(f) as fh:
                for line in fh:
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rows.append({k: r.get(k) for k in KEY + ['status'] + MEASURES})
    df = pd.DataFrame(rows)
    return df.drop_duplicates(subset=KEY, keep='first')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cloud', nargs='+', required=True)
    ap.add_argument('--mac', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    c, m = load(a.cloud), load(a.mac)
    tc, tm = set(c.dataset), set(m.dataset)
    both = sorted(tc & tm)
    out = dict(cloud_dirs=a.cloud, mac_dirs=a.mac, tasks_cloud=sorted(tc), tasks_mac=sorted(tm), tasks_both=both,
               tasks_used_from_cloud=len(tc), tasks_used_from_mac=len(tm - tc),
               note='stats42.py reads the cloud folder first, so the tasks that ran on both enter the tests with the '
                    "cloud's copies", per_task={})
    mean_max, vs_smote_max = 0.0, 0.0
    for t in both:
        j = c[c.dataset == t].merge(m[m.dataset == t], on=KEY, suffixes=('_c', '_m'))
        status_differ = int((j.status_c != j.status_m).sum())
        ok = j[(j.status_c == 'ok') & (j.status_m == 'ok')]
        differ = (ok[[x + '_c' for x in MEASURES]].to_numpy() != ok[[x + '_m' for x in MEASURES]].to_numpy()).any(axis=1)
        gc = c[(c.dataset == t) & (c.status == 'ok')].groupby(['method', 'learner'])[MEASURES].mean()
        gm = m[(m.dataset == t) & (m.status == 'ok')].groupby(['method', 'learner'])[MEASURES].mean()
        d = (gc - gm).abs()
        ch = []
        for ln in ('RF', 'GB'):
            if ('SMOTE', ln) not in gc.index or ('SMOTE', ln) not in gm.index:
                continue
            for meth in sorted(set(gc.index.get_level_values('method'))):
                if meth == 'SMOTE' or (meth, ln) not in gc.index or (meth, ln) not in gm.index:
                    continue
                for x in ('roc_auc', 'pr_auc'):
                    ch.append(abs((gc.loc[(meth, ln), x] - gc.loc[('SMOTE', ln), x]) -
                                  (gm.loc[(meth, ln), x] - gm.loc[('SMOTE', ln), x])))
        out['per_task'][t] = dict(cells=int(len(j)), cells_status_differ=status_differ, cells_ok_both=int(len(ok)),
                                  cells_value_differ=int(differ.sum()), pct_value_differ=round(100 * float(differ.mean()), 1),
                                  max_abs_diff_of_means=d.max().round(6).to_dict(),
                                  max_change_of_diff_vs_smote_rf_gb=round(max(ch), 6) if ch else None)
        mean_max = max(mean_max, float(d.max().max()))
        if ch:
            vs_smote_max = max(vs_smote_max, max(ch))
    out['max_abs_diff_of_means'] = round(mean_max, 6)
    out['max_change_of_diff_vs_smote_rf_gb'] = round(vs_smote_max, 6)
    with open(a.out, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('tasks_cloud', 'tasks_mac')}, indent=1))


if __name__ == '__main__':
    main()
