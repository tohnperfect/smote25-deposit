#!/usr/bin/env python3
"""v0.29 (D43): count the cells of the TabPFN arm of the rerun by task, method and status, and record where they ran.

Reads the TabPFN results directory (results_tabpfn_mac/ of the MacBook run, from results_tabpfn_mac.tgz), the rerun's
results directories in the order stats42_tabpfn.py reads them (the cloud's first), and stats42_tabpfn.py's summary.json.
Writes <out>/cells.json:
* cells, ok and errors of the arm, the errors by kind (out of memory of the graphics processor, or a sampler that could
  not run on a training fold) and the tasks of each kind;
* the model, package and device that run42.py recorded in config.json, and the run time of the cells that gave a result;
* whether the fold files of the arm are the rerun's (same splits), task by task;
* for the tasks in the comparisons (summary.json), which machine the random forest and gradient boosting cells come from
  (the first directory that holds a cell wins, as in stats42_tabpfn.py).
Usage: python3 -I tabpfn_cells42.py <tabpfn results dir> <stats out dir (with summary.json)> <rerun results dir>...
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

tab, out = Path(sys.argv[1]), Path(sys.argv[2])
rerun = [Path(p) for p in sys.argv[3:]]
summ = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
left_out = set(summ['tasks_left_out'])


def kind(err):
    e = str(err)
    if 'OutOfMemory' in e or 'out of memory' in e:
        return 'out of memory'
    if 'sampler:' in e:
        return 'sampler'
    return 'other'


cells, by_task, kinds, secs = 0, collections.defaultdict(collections.Counter), collections.Counter(), 0.0
tasks_by_kind = collections.defaultdict(set)
for f in sorted(tab.glob('*.jsonl')):
    for line in f.open(encoding='utf-8'):
        if not line.strip():
            continue
        r = json.loads(line)
        if r['learner'] != 'TabPFN':
            continue
        cells += 1
        by_task[r['dataset']][(r['method'], r['status'])] += 1
        if r['status'] == 'ok':
            secs += float(r.get('seconds') or 0)
        else:
            k = kind(r.get('error'))
            kinds[k] += 1
            tasks_by_kind[k].add(r['dataset'])
if kinds.get('other'):
    sys.exit(f"STOP: {kinds['other']} cells failed for a reason that is neither memory nor the sampler")
cfg = json.loads((tab / 'config.json').read_text(encoding='utf-8'))
folds = {}
for f in sorted((tab / 'folds').glob('*.json')):
    h = hashlib.md5(f.read_bytes()).hexdigest()
    other = next((d / 'folds' / f.name for d in rerun if (d / 'folds' / f.name).exists()), None)
    folds[f.stem] = bool(other) and hashlib.md5(other.read_bytes()).hexdigest() == h
if not all(folds.values()):
    sys.exit(f'STOP: fold files differ from the rerun for {[k for k, v in folds.items() if not v]}')
complete = sorted(set(by_task) - left_out)
src, seen = collections.defaultdict(set), set()
for d in rerun:
    for f in sorted(d.glob('*.jsonl')):
        for line in f.open(encoding='utf-8'):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r['learner'] not in ('RF', 'GB') or r['method'] not in ('none', 'SMOTE') or r['dataset'] not in complete:
                continue
            k = (r['dataset'], r['repeat'], r['fold'], r['method'], r['learner'])
            if k not in seen:
                seen.add(k)
                src[str(d)].add(r['dataset'])
res = dict(
    cells=cells, ok=sum(c[(m, 'ok')] for c in by_task.values() for m in ('none', 'SMOTE')), error=sum(kinds.values()),
    errors_by_kind=dict(kinds), tasks_by_kind={k: sorted(v) for k, v in tasks_by_kind.items()},
    errors_by_task={t: {f'{m} {s}': n for (m, s), n in sorted(c.items())} for t, c in sorted(by_task.items())
                    if any(s != 'ok' for (_, s) in c)},
    tasks=len(by_task), tasks_complete=len(complete), tasks_left_out=sorted(left_out),
    hours_of_cells_with_result=round(secs / 3600, 2), config=cfg.get('tabpfn', {}),
    folds_same_as_rerun=sum(folds.values()), folds_compared=len(folds),
    rf_gb_cells_from={d: sorted(v) for d, v in src.items()},
    rf_gb_tasks_from_first_dir=len(src.get(str(rerun[0]), ())))
(out / 'cells.json').write_text(json.dumps(res, indent=1), encoding='utf-8')
print(json.dumps({k: v for k, v in res.items() if k not in ('errors_by_task', 'rf_gb_cells_from')}, indent=1))
