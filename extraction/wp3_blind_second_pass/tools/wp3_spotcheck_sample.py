"""Draw the seeded random fifth of the agreements that the adjudicator checks (D13 protocol).
usage: python3 -I wp3_spotcheck_sample.py <work_dir> <team_repo> <out.csv>"""
import csv, json, glob, random, sys, math
W, T, OUT = sys.argv[1:4]
SEED = 20261111
rows = []
# Data extraction values (dataset entries and outcome rows, outcome rows recoded under the metric rule)
for r in csv.DictReader(open(f'{W}/scratch_data/ds2/blind/compare_rows.csv')):
    if r['match'] == 'True':
        rows.append({'form': 'Data extraction', 'item': f"{r['check_id']} {r['paper']} / {r['item']}", 'field': r['field'], 'agreed_value': r['extracted']})
# Data-handling codes (crit_type, minority_rule)
dm = {r['key']: r for r in csv.DictReader(open(f'{T}/Data section/out/data_handling_matrix.csv', encoding='utf-8-sig'))}
blind = {}
for f in glob.glob(f'{W}/blind2/batch*/out/*.json'):
    d = json.load(open(f)); blind[d['data_key']] = d
for k in sorted(dm):
    for fld in ('crit_type', 'minority_rule'):
        a, b = (dm[k][fld] or '').strip().lower(), (blind.get(k, {}).get(fld) or '').strip().lower()
        if k in blind and a == b:
            rows.append({'form': 'Data handling', 'item': k, 'field': fld, 'agreed_value': dm[k][fld]})
# Method and Evaluation forms
for path, form, key in ((f'{W}/blind3/WP3_method_comparison.csv', 'Method', 'paper'), (f'{W}/blind3/WP3_evaluation_comparison.csv', 'Evaluation', 'study')):
    for r in csv.DictReader(open(path)):
        if r['agree'] == 'True':
            rows.append({'form': form, 'item': r[key], 'field': r['field'], 'agreed_value': r['first_pass']})
rnd = random.Random(SEED)
out = []
for form in ('Data extraction', 'Data handling', 'Method', 'Evaluation'):
    pool = [r for r in rows if r['form'] == form]
    pick = rnd.sample(pool, math.ceil(len(pool) / 5))
    print(form, 'agreements', len(pool), 'drawn', len(pick))
    out += sorted(pick, key=lambda r: (r['item'], r['field']))
for r in out: r.update({'check_result': '', 'note': ''})
w = csv.DictWriter(open(OUT, 'w', newline=''), list(out[0].keys())); w.writeheader(); w.writerows(out)
print('seed', SEED, 'total drawn', len(out))
