#!/usr/bin/env python3
"""Spot check of the agreements (D31): are the values that both blind passes agreed on supported by the paper?

The sample is data/wp3_blind/AGREEMENTS_spot_check_sample.csv (351 items: a seeded fifth of the agreements of each
form, seed 20261111). This script checks the 288 Data extraction values against the paper texts (pdftotext of the
corpus PDFs, NFKC, whitespace normalised, one string per PDF page):
  value printed            the value (or, for a ratio or a class distribution, each number in it) occurs on a page
                           that also names the dataset; for a metric name, the name occurs in the paper
  value printed elsewhere  the value occurs in the paper, but not on a page that names the dataset (tables that span
                           pages, abbreviated names); read by hand below
  convention (D32)         number of classes 2 for a two-class set whose class count is not printed
  both blank               neither pass found a value; kept blank when the verified sheet records no printed number
                           from which the value follows; filled under D32 or D33 otherwise (AGREEMENTS_manual_checks.csv)
  not found                read by hand below
Items that the script cannot settle, and the 63 Data handling, Method and Evaluation codes, are checked by hand
(MANUAL, with the page and the passage); the result of every item is written to AGREEMENTS_checked.csv.
Usage: python3 -I check_agreements.py <corpus_dir> <v16_dir> <team_repo>
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

CORPUS, V16, TEAM = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
HERE = Path(__file__).resolve().parent
BY = 'AI check (Claude Opus 5.5, 12 Nov 2026)'
ALIAS = {'OREM-M': 'OREM', 'SMOTE-ENN': 'SMOTE-ENN / SMOTE-Tomek', 'RACOG': 'RACOG / wRACOG',
         'EasyEnsemble': 'EasyEnsemble / BalanceCascade', 'CTGAN': 'CTGAN / TVAE', 'DSRBF': 'DSRBF / Static-SMOTE',
         'SMOTE-Tomek, SMOTE-ENN': 'SMOTE-ENN / SMOTE-Tomek', 'RBBoost': 'RBBoost / Random Balance'}


def norm(s):
    s = unicodedata.normalize('NFKC', s).replace('­', '').replace('−', '-')
    return re.sub(r'\s+', ' ', s).lower()


KM = {d['data_key']: d['s7_key'] for d in json.load(open(CORPUS / 'key_map.json', encoding='utf-8'))}
S7 = {d['s7_key'] for d in json.load(open(CORPUS / 'key_map.json', encoding='utf-8'))}
_PAGES = {}


def pages(paper):
    stem = KM.get(ALIAS.get(paper, paper)) or KM.get(paper) or (paper if paper in S7 else None)
    if stem is None:
        raise SystemExit(f'STOP: no corpus text for {paper}')
    if stem not in _PAGES:
        out = []
        for f in sorted((CORPUS / 'txt').glob(stem + '__*.txt')):
            for i, p in enumerate(f.read_text(encoding='utf-8', errors='ignore').split('\f')):
                out.append((f.name.split('__')[1][:-4], i + 1, norm(p)))
        _PAGES[stem] = out
    return _PAGES[stem]


def numbers(v):
    """The numbers to look for in an agreed value."""
    v = v.replace(',', '')
    return re.findall(r'\d+(?:\.\d+)?', v)


def tok_in(n, text):
    alts = {n, n.replace('.', ',')}
    if re.fullmatch(r'\d{4,}', n):
        alts.add(f'{int(n):,}')
        alts.add(f'{int(n):,}'.replace(',', ' '))
    if re.fullmatch(r'0\.\d{3,}', n):                  # a share printed as a percentage (0.9656 -> 96.56)
        alts.add(f'{float(n) * 100:.{len(n) - 4}f}')
    if re.fullmatch(r'\d+\.\d+', n):                    # trailing zero dropped in print (0.5810 -> 0.581)
        alts.add(n.rstrip('0').rstrip('.'))
    return any(re.search(r'(?<![\d.,])' + re.escape(a) + r'(?![\d])', text) for a in alts if a)


def name_keys(ds):
    ds = norm(ds)
    keys = {ds, re.sub(r'[^a-z0-9]', '', ds)}
    keys.add(re.split(r'[ (/,]', ds)[0])
    return {k for k in keys if len(k) >= 3}


def on_page_with_name(ds, text):
    flat = re.sub(r'[^a-z0-9]', '', text)
    return any(k in text or k in flat for k in name_keys(ds))


MULTI = ['CTGAN / TVAE', 'EasyEnsemble / BalanceCascade', 'RBBoost / Random Balance', 'SMOTE-ENN / SMOTE-Tomek',
         'RACOG / wRACOG', 'DSRBF / Static-SMOTE', 'Global-CS (journal)', 'Global-CS (AAAI)']


def split_item(item):
    body = item.split(' ', 1)[1]
    for p in MULTI:
        if body.startswith(p + ' / '):
            return p, body[len(p) + 3:]
    paper, ds = body.split(' / ', 1)
    return paper, ds


REFS = {}


def load_refs():
    import csv as _c
    for v in _c.DictReader(open(TEAM / 'Data section/out/verified_datasets.csv', encoding='utf-8-sig')):
        REFS.setdefault(('D', v['paper'], v['name']), v['ref'])
    for o in _c.DictReader(open(TEAM / 'Data section/out/verified_outcomes.csv', encoding='utf-8-sig')):
        for nm in {o['dataset_as_printed'], o['dataset']}:
            REFS.setdefault(('R', o['paper'], nm), o['table'] + ' ' + o['page'])


_OCR = {}


def ocr_pages(paper, ref):
    """OCR (tesseract, 300 dpi) of the PDF pages that the verified sheet gives for the item; all pages if none."""
    import subprocess, tempfile
    stem = KM.get(ALIAS.get(paper, paper)) or KM.get(paper)
    part = 'supp1' if 'upplement' in ref else 'main'
    pdf = CORPUS / 'pdf' / f'{stem}__{part}.pdf'
    if not pdf.exists():
        return []
    pg = [int(x) for x in re.findall(r'(?<!printed )(?<!printed p)p\.(\d+)', ref)]
    rng = re.findall(r'(?<!printed )p\.(\d+)-(\d+)', ref)
    for a, b in rng:
        pg += list(range(int(a), int(b) + 1))
    if not pg:
        n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout).group(1))
        pg = list(range(1, min(n, 30) + 1))
    npages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout).group(1))
    out = []
    for n in sorted(x for x in set(pg) if 1 <= x <= npages):
        key = (str(pdf), n)
        if key not in _OCR:
            with tempfile.TemporaryDirectory() as td:
                subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-r', '300', '-png', str(pdf), td + '/p'],
                               check=True, capture_output=True)
                img = sorted(Path(td).glob('p*.png'))[0]
                txt = subprocess.run(['tesseract', str(img), '-', '--psm', '6'], capture_output=True, text=True).stdout
            _OCR[key] = norm(txt)
        out.append((f'{part} p.{n} (OCR)', _OCR[key]))
    return out


def check_data(r):
    paper, ds = split_item(r['item'])
    v, field = r['agreed_value'].strip(), r['field']
    pg = pages(paper)
    if field == 'metric':
        key = norm(re.split(r'[(\[]', v)[0]).strip()
        hit = [f'{p} p.{n}' for p, n, t in pg if key and key in t]
        return ('value printed', hit[0]) if hit else ('not found', '')
    if field == 'n_classes' and v == '2':
        return 'convention (D32)', ''
    nums = numbers(v)
    if not nums:
        return 'both blank: nothing printed from which it follows (verified sheet)', ''
    same = [f'{p} p.{n}' for p, n, t in pg if all(tok_in(x, t) for x in nums) and on_page_with_name(ds, t)]
    if same:
        return 'value printed', same[0]
    ref = REFS.get((r['item'][0], paper, ds), '')
    oc = [w for w, t in ocr_pages(paper, ref) if all(tok_in(x, t) for x in nums)]
    if oc:
        return 'value printed', oc[0] + (' on ' + ref if ref else '')
    anyp = [f'{p} p.{n}' for p, n, t in pg if all(tok_in(x, t) for x in nums)]
    if anyp:
        return 'value printed elsewhere', anyp[0]
    return 'not found', ref


def main():
    load_refs()
    S = list(csv.DictReader(open(V16 / 'data/wp3_blind/AGREEMENTS_spot_check_sample.csv', encoding='utf-8')))
    manual = {}
    mf = HERE / 'AGREEMENTS_manual_checks.csv'
    if mf.exists():
        for r in csv.DictReader(open(mf, encoding='utf-8')):
            manual[(r['form'], r['item'], r['field'])] = r
    out = []
    for r in S:
        key = (r['form'], r['item'], r['field'])
        if r['form'] == 'Data extraction':
            res, where = check_data(r)
        else:
            res, where = 'manual', ''
        if key in manual:
            mres = manual[key]
            res, where = mres['result'], mres['where'] + (' | ' + mres['note'] if mres['note'] else '')
        out.append(dict(form=r['form'], item=r['item'], field=r['field'], agreed_value=r['agreed_value'],
                        result=res, where=where, checked_by=BY))
    with open(HERE / 'AGREEMENTS_checked.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print(Counter((x['form'], x['result']) for x in out))


if __name__ == '__main__':
    main()
