#!/usr/bin/env python3
"""WP6.8 step 1: load the 42 tasks of the reference collection and check them against the Data section's table.

The task list, the source and the minority label of every task come from the team repository,
`Data section/difficulty/reference_collection.csv`. The files were fetched on 11 Nov 2026 into `src/` (untrusted data;
see `out/fetch_notes.md`): the keel-ds 0.2.5 wheel from PyPI (20 KEEL tasks) and single files from the GitHub mirrors
and author repositories that `Data section/difficulty/fetch_mirrors_ext.sh` names, at the commits it pins. The parsers
copy the logic of `Data section/difficulty/measure.py`, `mirrors_ext.py` and `official_sources.py` (read, not imported).
A task passes when its rows, features and minority count equal N, d and n_min of the Data section's table; nothing is
run on a task that does not pass. The 8 tasks of the k-means SMOTE release come from the release tarball, which the
cloud proxy refuses; it was downloaded on the team lead's machine on 11 Nov 2026 (sha256 as the Data section pins it)
and its 8 CSV files were staged into src/files/author-kmeans/. The Kaggle task needs a Kaggle sign-in and is missing.
Usage: python3 -I scripts/tasks42.py <team-repo> src out
"""
import csv
import glob
import gzip
import hashlib
import io
import os
import re
import sys

import numpy as np
import pandas as pd


def arff_any(path, class_attr=None):
    """dense or sparse ARFF or KEEL file with a header (official_sources.arff_any)."""
    names, nom, rows, data = [], set(), [], False
    for ln in open(path, errors='ignore'):
        l = ln.strip()
        if not l or l.startswith('%'):
            continue
        if data:
            if l.startswith('{'):
                r = ['0'] * len(names)
                for kv in l.strip('{}').split(','):
                    kv = kv.strip()
                    if kv:
                        i, v = kv.split(None, 1)
                        r[int(i)] = v.strip()
                rows.append(r)
            else:
                rows.append([x.strip() for x in next(csv.reader([l], skipinitialspace=True))])
        elif l.lower().startswith('@attribute'):
            m = re.match(r"@attribute\s+('([^']*)'|\"([^\"]*)\"|(\S+))\s*(.*)", l, re.I)
            nm = m.group(2) or m.group(3) or m.group(4)
            names.append(nm)
            if m.group(5).strip().startswith('{'):
                nom.add(nm)
        elif l.lower().startswith('@data'):
            data = True
    rows = [r for r in rows if len(r) == len(names)]
    d = pd.DataFrame(rows, columns=names)
    cls = class_attr if class_attr in names else ([n for n in names if n.strip().lower() in ('class', 'label', 'target')] or [names[-1]])[0]
    y = d.pop(cls).astype(str).str.strip().str.strip("'\"")
    nom.discard(cls)
    d = d.apply(lambda s: s.astype(str).str.strip().str.strip("'\""))
    return d.assign(**{c: d[c].astype('category') for c in nom if c in d}), y


def load(src_dir, source, fname, minority=None):
    if source == 'KEEL(keel_ds)':
        ps = sorted(glob.glob(os.path.join(src_dir, 'kd', 'keel_ds', 'data', '*', 'raw', fname + '.dat')))
        if not ps:
            raise FileNotFoundError(fname)
        for p in ps:                       # pima is in both folders: take the file whose labels hold the minority label
            d = pd.read_csv(p, header=None, dtype=str, skipinitialspace=True)
            y = d.pop(d.columns[-1]).astype(str).str.strip()
            d.columns = [f'a{i}' for i in range(d.shape[1])]
            if minority in set(y):
                return d, y, p
        raise FileNotFoundError(f'{fname}: no file with label {minority}')
    sub = {'KEEL-std(F)': ('KEEL-std-F', '.dat'), 'UCI++': ('UCIpp', '.arff'), 'Weka-UCI': ('Weka-UCI', '.arff'),
           'author-HDE': ('author-HDE', '.arff')}
    if source in sub:
        p = os.path.join(src_dir, 'files', sub[source][0], fname + sub[source][1])
        d, y = arff_any(p)
        return d, y, p
    if source == 'PMLB':
        p = os.path.join(src_dir, 'files', 'PMLB', fname + '.tsv.gz')
        d = pd.read_csv(p, sep='\t')
        y = d.pop('target').astype(str)
        return d.astype(str), y, p
    if source == 'jbrownlee-UCI':
        p = os.path.join(src_dir, 'files', 'jbrownlee-UCI', fname + '.csv')
        d = pd.read_csv(p, header=None, dtype=str, skipinitialspace=True)
        y = d.pop(d.columns[-1]).str.strip().str.strip("'\"")
        d.columns = [f'a{i}' for i in range(d.shape[1])]
        return d, y, p
    if source == 'author-SOS':
        p = os.path.join(src_dir, 'files', 'author-SOS', fname + '.npz')
        z = np.load(p, allow_pickle=False)                    # never unpickle downloaded files
        a = np.vstack([z['train'], z['test']])
        return pd.DataFrame(a[:, :-1]).astype(str), pd.Series(a[:, -1]).astype(str), p
    if source == 'author-MBS':
        p = os.path.join(src_dir, 'files', 'author-MBS', 'Promotion_data.csv')
        d = pd.read_csv(p, dtype=str, skipinitialspace=True)
        y = d.pop('Label').astype(str).str.strip()
        return d, y, p
    if source == 'author-kmeans':            # official_sources: table(label=-1, encoding='latin-1'), header in the file
        p = os.path.join(src_dir, 'files', 'author-kmeans', fname + '.csv')
        d = pd.read_csv(p, dtype=str, skipinitialspace=True, encoding='latin-1')
        y = d.pop(d.columns[-1]).astype(str).str.strip().str.strip("'\"")
        d = d.apply(lambda c: c.astype(str).str.strip().str.strip("'\""))
        return d, y, p
    if source == 'Kaggle':                   # official_sources: table(label='Fire Alarm', drop=('Unnamed: 0',))
        p = os.path.join(src_dir, 'files', 'Kaggle', 'smoke_detection_iot.csv')
        if not os.path.exists(p):
            raise LookupError('Kaggle: smoke_detection_iot.csv not yet supplied (needs a Kaggle sign-in)')
        d = pd.read_csv(p, dtype=str, skipinitialspace=True)
        d = d.drop(columns=[c for c in ('Unnamed: 0',) if c in d.columns])
        y = d.pop('Fire Alarm').astype(str).str.strip()
        return d, y, p
    raise LookupError(f'{source}: not obtainable in the cloud workspace')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    repo, src_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
    ref = list(csv.DictReader(open(os.path.join(repo, 'Data section', 'difficulty', 'reference_collection.csv'), encoding='utf-8')))
    if len(ref) != 42:
        sys.exit(f'STOP: {len(ref)} tasks in reference_collection.csv')
    rows = []
    for r in ref:
        row = dict(task=r['task'], source=r['source'], file=r['file'], minority_label=r['minority_label'],
                   origin=r['origin'], N_ref=int(r['N']), nmin_ref=int(r['n_min']), d_ref=int(r['d']))
        try:
            d, y, path = load(src_dir, r['source'], r['file'], r['minority_label'])
        except (LookupError, FileNotFoundError) as e:
            row.update(status='missing', note=str(e))
            rows.append(row)
            continue
        # rows with a missing value are dropped, as measure.py does before it counts (typed(): '?' and '<null>' are missing,
        # a column with no value at all is dropped first)
        dd = d.replace('?', np.nan).replace('<null>', np.nan).replace('', np.nan)
        dd = dd.loc[:, dd.notna().any(axis=0)]
        keep = dd.notna().all(axis=1)
        ymin = (y[keep] == r['minority_label'])
        row.update(N_raw=len(y), N=int(keep.sum()), nmin=int(ymin.sum()), d=dd.shape[1], n_classes=y.nunique(),
                   rows_with_missing=int((~keep).sum()), path=os.path.relpath(path, src_dir), sha256=sha256(path))
        # the Data section's N counts the rows after dropping missing values for some files (promotion, breast.cancer)
        # and all rows for others (cleveland-0_vs_4): a task passes when either count matches
        raw_ok = (row['N_raw'], int((y == r['minority_label']).sum()), d.shape[1]) == (row['N_ref'], row['nmin_ref'], row['d_ref'])
        drop_ok = (row['N'], row['nmin'], row['d']) == (row['N_ref'], row['nmin_ref'], row['d_ref'])
        ok = raw_ok or drop_ok
        row.update(status='ok' if ok else 'MISMATCH',
                   note=('matches after dropping rows with missing values' if drop_ok and row['rows_with_missing'] else
                         'matches with all rows (rows with missing values kept)' if raw_ok and row['rows_with_missing'] else '')
                   if ok else f"N {row['N']} vs {row['N_ref']}, n_min {row['nmin']} vs {row['nmin_ref']}, d {row['d']} vs {row['d_ref']}")
        rows.append(row)
    os.makedirs(out, exist_ok=True)
    cols = ['task', 'source', 'file', 'minority_label', 'origin', 'status', 'N_raw', 'N', 'N_ref', 'nmin', 'nmin_ref', 'd', 'd_ref',
            'n_classes', 'rows_with_missing', 'path', 'sha256', 'note']
    with open(os.path.join(out, 'tasks42_check.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    st = pd.Series([r['status'] for r in rows]).value_counts().to_dict()
    print('status:', st)
    for r in rows:
        if r['status'] != 'ok':
            print(f"  {r['status']:8s} {r['task'][:45]:45s} {r['source']:15s} {r.get('note', '')}")


if __name__ == '__main__':
    main()
