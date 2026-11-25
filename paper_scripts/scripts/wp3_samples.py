#!/usr/bin/env python3
"""WP3 steps 1 and 2: seeded stratified samples and blank coding forms for the human
verification of the Method and Evaluation extractions. The Data extraction already
has its own blind sample (Data section/blind/, 15 percent of rows, seed 20261028),
which WP3 uses as it is.

Forms show only where to look, never the existing codes (blind coding). Two authors
fill them independently; scripts compare them with the assisted coding afterwards.
Usage: python3 scripts/wp3_samples.py <team-repo-root> wp3/
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

SEED = 20261110
repo, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

# ---- Method extraction: 10 of the 37 SMOTE-family papers, by class category x (<=2 vs >=3 decisions)
recs = {}
for f in (repo / 'Method section/pdf-check').glob('*.json'):
    d = json.loads(f.read_text(encoding='utf-8'))
    for it in (d if isinstance(d, list) else d.get('papers', [d])):
        if isinstance(it, dict) and it.get('acronym'):
            recs[it['acronym']] = it
strata = defaultdict(list)
for a, it in sorted(recs.items()):
    strata[(it.get('category'), 'few' if len(it.get('decision_points') or []) <= 2 else 'many')].append(a)
rng = random.Random(SEED)
quota = {k: max(1, round(10 * len(v) / len(recs))) for k, v in strata.items()}
while sum(quota.values()) > 10:
    k = max(quota, key=lambda s: quota[s] - 10 * len(strata[s]) / len(recs)); quota[k] -= 1
while sum(quota.values()) < 10:
    k = max(quota, key=lambda s: 10 * len(strata[s]) / len(recs) - quota[s]); quota[k] += 1
m_sample = sorted(a for k, v in strata.items() for a in rng.sample(v, quota[k]))

# ---- Evaluation extraction: 15 of the 71 empirical studies, by period
ev = [r for r in json.loads((repo / 'Evaluation section/section07-coded-data.json').read_text(encoding='utf-8')) if r.get('empirical')]
by_era = defaultdict(list)
for r in ev:
    by_era[r['era']].append(r['key'])
rng = random.Random(SEED + 1)
equota = {e: round(15 * len(v) / len(ev)) for e, v in by_era.items()}
while sum(equota.values()) != 15:
    e = max(equota, key=lambda s: 15 * len(by_era[s]) / len(ev) - equota[s]) if sum(equota.values()) < 15 else \
        max(equota, key=lambda s: equota[s] - 15 * len(by_era[s]) / len(ev))
    equota[e] += 1 if sum(equota.values()) < 15 else -1
e_sample = sorted(k for e, v in by_era.items() for k in rng.sample(sorted(v), equota[e]))
evd = {r['key']: r for r in ev}

M_FIELDS = ['class_category (B / M / B+M)', 'evidence for the category (page, table)', 'multiclass data reduced to two classes? (yes/no, page)',
            'link (Core / Partial / Not counted)', 'seed selection changed? (y/n, page)', 'sample allocation changed? (y/n, page)',
            'neighbour choice changed? (y/n, page)', 'placement rule changed? (y/n, page)', 'post-filtering changed? (y/n, page)',
            'inside a pipeline? (y/n, page)', 'removes or moves original examples? (C3, y/n, page)', 'adaptive choice of k? (y/n, page)']
E_FIELDS = ['real datasets (n)', 'synthetic datasets (n)', 'sources (UCI/KEEL/other)', 'learner families', 'plain SMOTE as baseline? (y/n)',
            'no-resampling baseline? (y/n)', 'class weighting or cost-sensitive baseline? (y/n)', 'threshold moving baseline? (y/n)',
            'measures (as printed)', 'any measure defined wrongly? (y/n, which)', 'calibration measure reported? (y/n)',
            'validation protocol (CV type, repeats)', 'resampling inside the training folds stated? (y/n/not said)',
            'how settings were chosen (fixed / tuned inside training / on evaluation data / not said)', 'statistical tests (as printed)',
            'per-dataset results table? (y/n)', 'standard deviations reported? (y/n)', 'code released? (y/n, link)',
            'data modified before use? (y/n)', 'modified data released? (y/n)', 'reason given for the data? (y/n, quote)']


def form(path, title, rows, fields, intro):
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = 'instructions'
    for i, line in enumerate(intro, 1):
        ws.cell(i, 1, line)
    for coder in ('coder_A', 'coder_B'):
        s = wb.create_sheet(coder)
        head = ['check_id', 'paper key', 'title', 'year'] + fields + ['notes']
        for j, h in enumerate(head, 1):
            c = s.cell(1, j, h); c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDDDDD')
        for i, r in enumerate(rows, 2):
            for j, v in enumerate(r, 1):
                s.cell(i, j, v)
        s.freeze_panes = 'E2'
    wb.save(path)


intro_common = ['Blind coding form (WP3). Seed and strata in wp3/sample_manifest.json.',
                'Code from the PDF and its supplement only. Do not open the coding sheets, the Method Map, the Atlas or the draft.',
                'Give a page, section, table or equation for every code. Write "not stated" when the paper does not say.',
                'Two authors fill sheets coder_A and coder_B independently; at least one is not the first coder of that section.',
                'Then run the comparison (kappa per field, percentage agreement for rare categories) and adjudicate.']
form(out / 'wp3_method_form.xlsx', 'Method', [[f'M{i:02d}', a, '', ''] for i, a in enumerate(m_sample, 1)], M_FIELDS,
     intro_common + ['Rules: Method section/pdf-check/coding_rules.md (class categories, decision points, SMOTE-family definition).'])
form(out / 'wp3_evaluation_form.xlsx', 'Evaluation',
     [[f'E{i:02d}', k, evd[k]['title'], evd[k]['year']] for i, k in enumerate(e_sample, 1)], E_FIELDS,
     intro_common + ['Rules: the coding scheme of Section 7 (Evaluation section/latex/sections/07-empirical-comparisons.tex, Section 7.1).'])
manifest = dict(seed=SEED, method=dict(n=len(m_sample), of=len(recs), strata={f'{k[0]}|{k[1]}': dict(n=len(v), drawn=quota[k]) for k, v in strata.items()}, papers=m_sample),
                evaluation=dict(n=len(e_sample), of=len(ev), strata={e: dict(n=len(v), drawn=equota[e]) for e, v in by_era.items()}, papers=e_sample),
                data='use Data section/blind/ (seed 20261028; 15 percent of dataset entries and of plain-SMOTE outcome rows)')
(out / 'sample_manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
print('method sample:', m_sample); print('evaluation sample:', e_sample)
