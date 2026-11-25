import csv, json, re, sys, glob, collections
W = sys.argv[1]
def kappa(pairs):
    n = len(pairs)
    if not n: return None, None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return round(po, 3), (round((po - pe) / (1 - pe), 3) if pe < 1 else None)
def lead(s):
    # first token of a coded answer; map whole tokens (a substring replace once turned 'not said' into 'nt said')
    m = re.match(r'\s*(y|n|yes|no|not said|not stated|B\+M|B|M|Core|Partial|Not counted)\b', str(s or ''), re.I)
    if not m: return ''
    t = m.group(1).lower()
    return {'yes': 'y', 'no': 'n', 'not stated': 'not said'}.get(t, t)
# ---------------- Method: first pass from Table 6 rows
first = {}
for line in open(f'{W}/v04/gen/table_methods_rows.tex'):
    if '\\citep' not in line: continue
    c = [x.strip() for x in line.split('&')]
    name = re.sub(r'\s*\\citep\{[^}]*\}', '', c[0]).strip()
    first[name] = {'class': c[2].replace('*', ''), 'link': c[3], **{k: ('y' if 'bullet' in v else 'n') for k, v in zip('SANPFL', c[4:10])}}
alias = {'SMOTE-Tomek / SMOTE-ENN': 'SMOTE-Tomek, SMOTE-ENN', 'OREM': 'OREM, OREM-M'}
cols = {'class': 'class_category (B / M / B+M)', 'link': 'link (Core / Partial / Not counted)', 'S': 'seed selection changed? (y/n, page)',
        'A': 'sample allocation changed? (y/n, page)', 'N': 'neighbour choice changed? (y/n, page)', 'P': 'placement rule changed? (y/n, page)',
        'F': 'post-filtering changed? (y/n, page)', 'L': 'inside a pipeline? (y/n, page)'}
mrows, mpairs = [], collections.defaultdict(list)
for f in sorted(glob.glob(f'{W}/blind3/method/batch*_filled.csv')) + [f'{W}/blind3/smom/smom_filled.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        k = alias.get(r['paper key'], r['paper key']); fp = first.get(k)
        if not fp: print('no first pass for', k); continue
        for fld, col in cols.items():
            sec = lead(r.get(col)); sec = {'b+m': 'B+M', 'b': 'B', 'm': 'M', 'core': 'Core', 'partial': 'Partial', 'not counted': 'Not counted'}.get(sec, sec)
            a = fp[fld]; mpairs[fld if fld in ('class', 'link') else 'decision points'].append((a, sec))
            mrows.append({'paper': k, 'field': fld, 'first_pass': a, 'second_pass': sec, 'agree': a == sec, 'second_pass_evidence': (r.get(col) or '')[:300],
                          'C3_second_pass': (r.get('removes or moves original examples? (C3, y/n, page)') or '')[:160] if fld == 'class' else '',
                          'adaptive_k_second_pass': (r.get('adaptive choice of k? (y/n, page)') or '')[:120] if fld == 'class' else '', 'adjudication': ''})
msum = {k: dict(zip(('agreement', 'kappa'), kappa(v)), n=len(v)) for k, v in mpairs.items()}
# ---------------- Evaluation: first pass from section07-coded-data.json
E = {e['key']: e for e in json.load(open(f'{W}/../team-repo/Evaluation section/section07-coded-data.json'))}
tun = {'Fixed / default settings': 'fixed', 'Nested / held-out tuning': 'tuned inside training', 'Selected on evaluation data': 'on evaluation data', 'Unclear': 'not said', 'N/A': 'n/a'}
def sec_tuning(s):
    s = str(s or '').lower()
    for k in ('on evaluation data', 'tuned inside training', 'fixed', 'not said'):
        if s.startswith(k): return k
    return s[:20]
efields = [
    ('plain SMOTE baseline', 'plain SMOTE as baseline? (y/n)', lambda e: 'y' if e['smote_baseline'] else 'n', lead),
    ('no-resampling baseline', 'no-resampling baseline? (y/n)', lambda e: 'y' if e['no_resampling_baseline'] else 'n', lead),
    ('resampling inside folds stated', 'resampling inside the training folds stated? (y/n/not said)', lambda e: {True: 'y', False: 'n', None: 'not said'}[e['resampling_inside_cv']], lead),
    ('how settings were chosen', 'how settings were chosen (fixed / tuned inside training / on evaluation data / not said)', lambda e: tun.get(e['tuning_class'], e['tuning_class']), sec_tuning),
    ('code released', 'code released? (y/n, link)', lambda e: 'y' if e['has_code'] else 'n', lead),
    ('any statistical test', 'statistical tests (as printed)', lambda e: 'n' if e['test_class'] == 'None' else 'y', lambda s: 'n' if re.match(r'\s*(none|no |n\b|not )', str(s or ''), re.I) else 'y'),
    ('a measure defined wrongly', 'any measure defined wrongly? (y/n, which)', lambda e: 'n' if e['metric_issue'] in (None, 'None') else 'y', lead),
    ('calibration measure reported', 'calibration measure reported? (y/n)', lambda e: 'n', lead),
    ('real datasets (n)', 'real datasets (n)', lambda e: str((e.get('datasets') or {}).get('n_real', e['n_datasets'])), lambda s: (re.match(r'\s*(\d+)', str(s or '')) or [None, ''])[1]),  # first pass: n_real (n_datasets also counts synthetic sets)
]
erows, epairs = [], collections.defaultdict(list)
for f in sorted(glob.glob(f'{W}/blind3/eval/batch*_filled.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        e = E.get(r['paper key'])
        if not e: print('no first pass for', r['paper key']); continue
        for name, col, fa, fs in efields:
            a, b = fa(e), fs(r.get(col)); epairs[name].append((a, b))
            erows.append({'study': r['paper key'], 'field': name, 'first_pass': a, 'second_pass': b, 'agree': a == b, 'second_pass_evidence': (r.get(col) or '')[:300], 'adjudication': ''})
esum = {k: dict(zip(('agreement', 'kappa'), kappa(v)), n=len(v)) for k, v in epairs.items()}
for path, rows in ((f'{W}/blind3/WP3_method_comparison.csv', mrows), (f'{W}/blind3/WP3_evaluation_comparison.csv', erows)):
    w = csv.DictWriter(open(path, 'w', newline=''), list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump({'method': msum, 'evaluation': esum}, open(f'{W}/blind3/WP3_agreement_summary.json', 'w'), indent=1)
print(json.dumps({'method': msum, 'evaluation': esum}, indent=1))
