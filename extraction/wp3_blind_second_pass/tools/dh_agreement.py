import csv, json, glob, sys, collections, math
dm = {r['key']: r for r in csv.DictReader(open(sys.argv[1], encoding='utf-8-sig'))}
blind = {}
for f in glob.glob(sys.argv[2] + '/batch*/out/*.json'):
    try: d = json.load(open(f))
    except Exception as e: print('BAD JSON', f, e); continue
    blind[d['data_key']] = d
print('blind papers:', len(blind), 'matrix papers:', len(dm), 'missing:', sorted(set(dm) - set(blind)))
def kappa(pairs):
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan')
res, rows = {}, []
norm = lambda s: (s or '').strip().lower()
for field in ('crit_type', 'minority_rule'):
    pairs = [(norm(dm[k][field]), norm(blind[k].get(field))) for k in dm if k in blind]
    po, k = kappa(pairs); res[field] = {'n': len(pairs), 'agreement': round(po, 3), 'kappa': round(k, 3)}
    for key in dm:
        if key in blind and norm(dm[key][field]) != norm(blind[key].get(field)):
            ev = [e for e in blind[key].get('evidence', []) if e.get('field') == field][:2]
            rows.append({'paper': key, 'field': field, 'first_pass': dm[key][field], 'second_pass': blind[key].get(field), 'second_pass_evidence': ' | '.join(f"{e.get('page')}: {e.get('quote')}" for e in ev), 'first_pass_quote': dm[key].get('quote', '')[:300]})
for field, vocab in (('origin', ['Natural', 'Binarised', 'Class-merged', 'Class-resized', 'Undersampled', 'Noise-injected', 'Induced profile', 'Generated']),):
    per = {}
    for lab in vocab:
        pairs = [((lab in dm[k][field].split(';')), (lab in (blind[k].get(field) or []))) for k in dm if k in blind and dm[k]['empirical'] == 'yes']
        po, kk = kappa(pairs); per[lab] = {'first': sum(a for a, _ in pairs), 'second': sum(b for _, b in pairs), 'agreement': round(po, 3), 'kappa': round(kk, 3) if kk == kk else None}
        for k in dm:
            if k in blind and dm[k]['empirical'] == 'yes' and (lab in dm[k][field].split(';')) != (lab in (blind[k].get(field) or [])):
                ev = [e for e in blind[k].get('evidence', []) if e.get('field') in ('origin', 'binarised_by')][:2]
                rows.append({'paper': k, 'field': f'origin:{lab}', 'first_pass': 'yes' if lab in dm[k][field].split(';') else 'no', 'second_pass': 'yes' if lab in (blind[k].get(field) or []) else 'no', 'second_pass_evidence': ' | '.join(f"{e.get('page')}: {e.get('quote')}" for e in ev), 'first_pass_quote': dm[k].get('prep_text', '')[:300]})
    res['origin'] = per
# Table 5 row 17: reason given = crit_type not in (not stated, generic only, n.a.)
emp = [k for k in dm if dm[k]['empirical'] == 'yes']
res['reason_given_first'] = sum(dm[k]['crit_type'] in ('own reason', 'cites prior work') for k in emp)
res['reason_given_second'] = sum(norm(blind.get(k, {}).get('crit_type')) in ('own reason', 'cites prior work') for k in emp)
res['crit_type_second_counts'] = dict(collections.Counter(norm(blind.get(k, {}).get('crit_type')) for k in emp))
res['crit_type_first_counts'] = dict(collections.Counter(dm[k]['crit_type'] for k in emp))
res['modified_data_released_second'] = {k: v.get('modified_data_released') for k, v in blind.items() if v.get('modified_data_released') in ('yes', 'on request')}
res['empirical_disagreements'] = [k for k in dm if k in blind and (dm[k]['empirical'] == 'yes') != (norm(blind[k].get('evaluates_on_data')) == 'yes')]
json.dump(res, open(sys.argv[3] + '.json', 'w'), indent=1)
w = csv.DictWriter(open(sys.argv[3] + '_disagreements.csv', 'w', newline=''), list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(json.dumps({k: v for k, v in res.items() if k != 'origin'}, indent=1)); print(json.dumps(res['origin'], indent=0)[:1200]); print(len(rows), 'disagreement rows')
