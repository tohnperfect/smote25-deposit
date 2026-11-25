import json, sys, openpyxl, re, csv
W = sys.argv[1]; km = json.load(open(f'{W}/corpus/key_map.json'))
safe = lambda k: re.sub(r'[^A-Za-z0-9.-]+', '_', k).strip('_')
by_data = {m['data_key']: m for m in km}; by_s7 = {m['s7_key']: m for m in km}
alias_m = {'SMOTE-Tomek / SMOTE-ENN': 'SMOTE-ENN / SMOTE-Tomek'}
def form_rows(path):
    wb = openpyxl.load_workbook(path, read_only=True); ws = wb['coder_A']; it = ws.iter_rows(values_only=True); hdr = list(next(it))
    return hdr, [dict(zip(hdr, r)) for r in it if r and r[0]]
for kind, path, nb in (('method', f'{W}/pkg03/SMOTE25_Draft_v03/wp3/wp3_method_form.xlsx', 2), ('eval', f'{W}/pkg03/SMOTE25_Draft_v03/wp3/wp3_evaluation_form.xlsx', 3)):
    hdr, rows = form_rows(path)
    for r in rows:
        k = r['paper key']
        m = by_data.get(alias_m.get(k, k)) if kind == 'method' else by_s7.get(k)
        r['_safe'] = safe(m['data_key']) if m else '??'
    for b in range(nb):
        part = rows[b::nb]
        with open(f'{W}/blind3/{kind}/batch{b+1}_to_fill.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, hdr + ['_safe']); w.writeheader(); w.writerows(part)
        print(kind, b + 1, [(r['paper key'], r['_safe']) for r in part])
