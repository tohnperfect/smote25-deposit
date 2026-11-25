"""Categorize Data blind-check disagreements after the outcome rows were recoded
with the written metric rule (G-mean > AUC > F-measure > accuracy).
usage: python3 -I blind_categorize_v2.py compare_rows.csv blind2_dir outrule_dir out.csv"""
import csv, sys, collections, re, glob
rows = list(csv.DictReader(open(sys.argv[1])))
notes = {}
for f in glob.glob(sys.argv[2] + '/batch*/*_filled.csv'):
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        notes[r['check_id']] = r
for f in glob.glob(sys.argv[3] + '/batch*_filled.csv'):          # outcome rows recoded under the rule
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        notes[r['check_id']] = r
def fam(m):
    """metric family of a printed label: G-mean, AUC, F-measure or accuracy (None if unclear)"""
    m = re.split(r'[,;]', str(m or '').lower())[0]   # the label itself, not the coder's remarks after it
    for k, pat in (('gmean', r'g[- ]?mean|\bg-?m\b|gmean'), ('auc', r'\bauc\b|roc'), ('f', r'f[_ -]?beta|\bf1\b|f-?measure|f-?value|f-?score'), ('acc', r'accuracy|\bacc\b')):
        if re.search(pat, m): return k
    return None
WORDS = {'one': '1', 'two': '2', 'three': '3', 'binary': '2', 'two-dimensional': '2'}
def nums(x):
    x = str(x).lower().replace(',', '')
    for w, n in WORDS.items(): x = re.sub(r'\b' + re.escape(w) + r'\b', n, x)
    return [float(v) for v in re.findall(r'\d+(?:\.\d+)?', x)]
def same_value(a, b):
    """the second pass copies the first value but adds or drops wording, units or a breakdown"""
    na, nb = nums(a), nums(b)
    if not na or not nb: return False
    return na[0] == nb[0] or set(na) <= set(nb) or set(nb) <= set(na)
by_check = collections.defaultdict(dict)
for r in rows: by_check[r['check_id']][r['field']] = r
out = []
for r in rows:
    if r['match'] != 'False': continue
    a, b, f = r['toon'].strip(), r['extracted'].strip(), r['field']
    if f == 'n_classes' and a.upper() == 'NR' and b == '2': cat = 'A convention: binary class count not printed (first coder recorded 2)'
    elif r['kind'] == 'outcome' and f == 'metric':
        cat = ('F same metric, label worded differently' if fam(a) and fam(a) == fam(b)
               else 'B different metric chosen under the same written rule')
    elif (r['kind'] == 'outcome' and f in ('proposed', 'smote') and a not in ('?', 'NR', '')
          and by_check[r['check_id']].get('metric', {}).get('match') == 'False'
          and fam(by_check[r['check_id']]['metric']['toon']) != fam(by_check[r['check_id']]['metric']['extracted'])):
        cat = 'B different metric chosen under the same written rule'
    elif a.upper() in ('NR', '') or a.startswith('?'): cat = 'C second coder found no printed value'
    elif b in ('', 'NR'): cat = 'D first extraction has no value, second found one'
    else:
        cat = ('E1 same value, written differently' if same_value(a, b) else 'E2 both found a value, values differ')
    n = notes.get(r['check_id'], {})
    note = n.get('note', '')
    step = n.get('metric_rule_step', '')
    out.append({'category': cat, 'check_id': r['check_id'], 'paper': r['paper'], 'item': r['item'], 'field': f,
                'first_extraction': b, 'second_pass': a, 'second_pass_note': note,
                'rule_step': step, 'adjudication': '', 'adjudication_note': ''})
out.sort(key=lambda x: (x['category'], x['paper'], x['check_id'], x['field']))
w = csv.DictWriter(open(sys.argv[4], 'w', newline=''), list(out[0].keys())); w.writeheader(); w.writerows(out)
c = collections.Counter(x['category'] for x in out)
for k, v in sorted(c.items()): print(v, k)
print('total', len(out))
