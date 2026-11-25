import openpyxl, csv, sys, re, json, collections
sheet, W = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(sheet, read_only=True); it = wb['outcomes'].iter_rows(values_only=True); hdr = list(next(it))
rows = [dict(zip(hdr, r)) for r in it if r and r[0]]
km = {m['data_key']: m for m in json.load(open(f'{W}/corpus/key_map.json'))}
safe = lambda k: re.sub(r'[^A-Za-z0-9.-]+', '_', k).strip('_')
papers = sorted({r['paper'] for r in rows}); half = [papers[0::2], papers[1::2]]
cols = ['check_id', 'paper', 'safe', 'table', 'page', 'pdf_page_hint', 'dataset_as_printed', 'classifier', 'smote_column', 'metric_selected', 'metric_rule_step', 'proposed_method_value', 'smote_value', 'note']
for i, ps in enumerate(half, 1):
    with open(f'{W}/blind3/outrule/batch{i}_to_fill.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, cols); w.writeheader()
        for r in rows:
            if r['paper'] in ps:
                w.writerow({c: (r.get(c) or '') for c in cols if c in hdr} | {'safe': safe(r['paper'])})
    print(i, len(ps), 'papers', sum(r['paper'] in ps for r in rows), 'rows')
