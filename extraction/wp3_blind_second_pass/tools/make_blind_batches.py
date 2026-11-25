import json, csv, sys, re, shutil, openpyxl
from pathlib import Path
W = Path(sys.argv[1]); corpus = Path(sys.argv[2]); sheet = sys.argv[3]; nb = int(sys.argv[4])
km = json.load(open(corpus / 'key_map.json'))
B = W / 'blind2'; (B / 'papers').mkdir(parents=True, exist_ok=True); (B / 'pdf').mkdir(exist_ok=True)
safe = lambda k: re.sub(r'[^A-Za-z0-9.-]+', '_', k).strip('_')
wb = openpyxl.load_workbook(sheet, read_only=True)
def rows(name):
    it = wb[name].iter_rows(values_only=True); hdr = list(next(it)); return [dict(zip(hdr, r)) for r in it if r and r[0]]
D, O = rows('datasets'), rows('outcomes')
papers = []
for m in km:
    k, s7 = m['data_key'], m['s7_key']; sk = safe(k)
    parts = sorted(corpus.glob(f'txt/{s7}__*.txt'), key=lambda p: (p.stem.split('__')[1] != 'main', p.stem))
    txt = []
    for p in parts:
        tag = p.stem.split('__')[1]
        txt.append(f'\n\n===== {"MAIN PAPER" if tag == "main" else "SUPPLEMENTARY FILE " + tag[4:]} ({p.stem}.pdf) =====\n\n' + p.read_text(errors='replace'))
        shutil.copy(corpus / 'pdf' / f'{p.stem}.pdf', B / 'pdf' / f'{sk}__{tag}.pdf')
    (B / 'papers' / f'{sk}.txt').write_text(''.join(txt))
    papers.append({'data_key': k, 'safe': sk, 'chars': sum(len(t) for t in txt), 'pdfs': [f'pdf/{sk}__{p.stem.split("__")[1]}.pdf' for p in parts],
                   'n_ds': sum(1 for r in D if r['paper'] == k), 'n_out': sum(1 for r in O if r['paper'] == k)})
unk = sorted({r['paper'] for r in D + O} - {p['data_key'] for p in papers})
print('sheet papers not in key map:', unk)
# greedy balance by chars + 15k per sampled row
papers.sort(key=lambda p: -(p['chars'] + 15000 * (p['n_ds'] + p['n_out'])))
bins = [[] for _ in range(nb)]; load = [0] * nb
for p in papers:
    i = load.index(min(load)); bins[i].append(p); load[i] += p['chars'] + 15000 * (p['n_ds'] + p['n_out'])
for i, b in enumerate(bins, 1):
    d = B / f'batch{i:02d}'; (d / 'out').mkdir(parents=True, exist_ok=True)
    keys = {p['data_key'] for p in b}
    json.dump(sorted(b, key=lambda p: p['data_key'].lower()), open(d / 'papers.json', 'w'), indent=1)
    dcols = ['check_id', 'paper', 'paper_title', 'where', 'pdf_page_hint', 'row_order_in_paper', 'name_as_printed', 'n_instances', 'n_features', 'n_classes', 'n_minority', 'ir_as_printed', 'note']
    ocols = ['check_id', 'paper', 'table', 'page', 'pdf_page_hint', 'dataset_as_printed', 'classifier', 'smote_column', 'proposed_method_value', 'smote_value', 'metric', 'note']
    with open(d / 'datasets_to_fill.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, dcols); w.writeheader()
        for r in D:
            if r['paper'] in keys: w.writerow({c: ('' if c in ('n_instances','n_features','n_classes','n_minority','ir_as_printed','note') else r.get(c, '')) for c in dcols})
    with open(d / 'outcomes_to_fill.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, ocols); w.writeheader()
        for r in O:
            if r['paper'] in keys: w.writerow({c: ('' if c in ('proposed_method_value','smote_value','metric','note') else r.get(c, '')) for c in ocols})
    print(f'batch{i:02d}: {len(b)} papers, {sum(p["n_ds"] for p in b)} ds rows, {sum(p["n_out"] for p in b)} outcome rows, {load[i-1]//1000}k load')
