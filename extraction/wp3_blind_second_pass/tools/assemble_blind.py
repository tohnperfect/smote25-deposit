import csv, sys, glob, openpyxl
src_sheet, batches, out_sheet = sys.argv[1], sys.argv[2], sys.argv[3]
fill = {}
for kind, fn in (('datasets', 'datasets_filled.csv'), ('outcomes', 'outcomes_filled.csv')):
    for f in sorted(glob.glob(f'{batches}/batch*/{fn}')):
        for r in csv.DictReader(open(f, encoding='utf-8-sig')):
            fill[(kind, r['check_id'])] = r
wb = openpyxl.load_workbook(src_sheet)
cols = {'datasets': ['n_instances', 'n_features', 'n_classes', 'n_minority', 'ir_as_printed', 'note'],
        'outcomes': ['proposed_method_value', 'smote_value', 'metric', 'note']}
miss = []
for kind in ('datasets', 'outcomes'):
    ws = wb[kind]; hdr = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        cid = row[0].value
        if not cid: continue
        r = fill.get((kind, cid))
        if r is None: miss.append(cid); continue
        for c in cols[kind]:
            row[hdr.index(c)].value = r.get(c, '')
wb.save(out_sheet)
print('filled from', len(fill), 'rows; missing:', miss[:20], len(miss))
