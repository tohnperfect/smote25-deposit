#!/usr/bin/env python3
"""D35 in the wins analysis: the proposed method is the variant the abstract names as the contribution; if it names
several, the first named; if it names none, the first the paper names (decision of the team lead, 12 Nov 2026).

Four of the 29 papers with per-dataset comparisons against plain SMOTE propose several variants, and the all-metric
extraction had taken another one as "the proposed method":
  NBU          NB-Comm  -> NB-Basic      the abstract names no variant ("Four methods ... are proposed"); NB-Basic is the
                                          first the paper names (Section 3); values: other_variants of the extraction
  RACOG/wRACOG wRACOG   -> RACOG         the abstract names "RACOG and wRACOG"; values: racog_alt of the extraction
  SMOTE-ENN    Smote+ENN -> Smote+Tomek  "Two of our proposed methods, Smote + Tomek and Smote + ENN" (abstract, p.1);
                                          values: Table 4, pruned trees (PDF page 7), read from the rendered page
                                          on 12 Nov 2026 (the table is an image)
  SOS          Sub-VP   -> VE            the abstract names no variant; the paper names VE, VP and Sub-VP in that
                                          order (Section 2); values: Table 2 (PDF page 7, text layer)
The other 25 papers propose one method, or their extraction already takes the first-named variant (checked against
each abstract on 12 Nov 2026).

Patches a COPY of the Data section (never the team repository):
  ai-draft/outcome/allmetric/{NBU,RACOG,SMOTE-ENN,SOS}.json   proposed (and proposed_std) per row; the replaced value
                                                               is kept per row under 'replaced_by_D35'
  out/verified_outcomes.csv                                    rule-A rows of the same papers: proposed, diff, raw_sign
Writes d35_changes.csv (one row per changed value) next to the copy.
Usage: python3 -I apply_d35.py "<copy>/Data section"
"""
import csv
import json
import sys
from pathlib import Path

D = Path(sys.argv[1])
AM = D / 'ai-draft/outcome/allmetric'
NOTE = 'D35 (12 Nov 2026): '
# Batista et al. (2004), Table 4, Smote+Tomek, pruning = yes (AUC %, mean (std))
TOMEK = {'Pima': ('84.46', '5.84'), 'German': ('81.75', '4.78'), 'Post-operative': ('41.80', '16.59'),
         'Haberman': ('75.73', '6.55'), 'Splice-ie': ('98.26', '0.51'), 'Splice-ei': ('98.87', '0.44'),
         'Vehicle': ('98.96', '0.98'), 'Letter-vowel': ('98.90', '0.20'), 'New-thyroid': ('98.91', '1.84'),
         'E.Coli': ('95.98', '4.21'), 'Satimage': ('95.43', '1.03'), 'Flag': ('79.30', '28.68'),
         'Glass': ('91.40', '8.24'), 'Letter-a': ('99.91', '0.12'), 'Nursery': ('99.27', '0.36')}
# Kim et al. (2022), Table 2, SOS VE (weighted F1, mean +- std)
VE = {'Default': ('0.571', '0.003'), 'Shoppers': ('0.675', '0.004'), 'Surgical': ('0.709', '0.003'),
      'WeatherAUS': ('0.672', '0.002'), 'Buddy': ('0.607', '0.007'), 'Satimage': ('0.854', '0.002')}
PAPERS = {  # allmetric key -> (verified_outcomes paper, old variant, new variant, column text)
    'NBU': ('NBU', 'NB-Comm', 'NB-Basic',
            'NB-Basic (D35: the abstract names none of the four NB variants; NB-Basic is the first the paper names; '
            'until 12 Nov 2026 NB-Comm, the variant the paper ranks best)'),
    'RACOG': ('RACOG / wRACOG', 'wRACOG', 'RACOG',
              'RACOG (D35: the abstract names "RACOG and wRACOG"; until 12 Nov 2026 wRACOG)'),
    'SMOTE-ENN': ('SMOTE-ENN / SMOTE-Tomek', 'Smote+ENN', 'Smote+Tomek',
                  'Smote+Tomek (D35: the paper names "Smote + Tomek and Smote + ENN" in that order; until 12 Nov 2026 Smote+ENN)'),
    'SOS': ('SOS', 'Sub-VP', 'VE',
            'SOS VE (D35: the abstract names no variant; the paper names VE, VP and Sub-VP in that order; until 12 Nov 2026 Sub-VP)'),
}


def new_value(key, r):
    """(value, std, source) of the D35 variant for one extracted row."""
    ds = r['dataset_as_printed']
    if key == 'NBU':
        return r['other_variants']['NB-Basic'], None, 'other_variants NB-Basic'
    if key == 'RACOG':
        return r['racog_alt'], r.get('racog_alt_std'), 'racog_alt'
    if key == 'SMOTE-ENN':
        v, s = TOMEK[ds]
        return v, s, 'Table 4, pruned, Smote+Tomek (rendered page 7)'
    v, s = VE[ds]
    return v, s, 'Table 2, VE'


def num(x):
    try:
        return float(str(x).replace('%', '').strip())
    except ValueError:
        return None


def res(p, s, hib):
    if p is None or s is None:
        return 'not comparable'
    if p == s:
        return 'tie'
    return 'win' if (p > s) == bool(hib) else 'loss'


def main():
    log = []
    rule_a = {}
    for key, (vkey, old, new, coltext) in PAPERS.items():
        f = AM / f'{key}.json'
        d = json.loads(f.read_text(encoding='utf-8'))
        assert old.lower().replace(' ', '') in d['proposed_column'].lower().replace(' ', '').replace('smt', 'smote') or \
            old in d['proposed_column'], f'STOP: {key} proposed column is not {old}: {d["proposed_column"][:80]}'
        for m in d['metrics']:
            for r in m['rows']:
                v, s, src = new_value(key, r)
                before = (r['proposed'], r.get('proposed_std'))
                r['replaced_by_D35'] = {'variant': old, 'proposed': before[0], 'proposed_std': before[1]}
                r['proposed'], r['proposed_std'] = v, s
                hib = m.get('higher_is_better')
                o1, o2 = res(num(before[0]), num(r['smote']), hib), res(num(v), num(r['smote']), hib)
                log.append(dict(paper=key, metric=m['metric'], is_rule_A_metric=bool(m.get('is_existing_chosen')),
                                dataset=r['dataset_as_printed'], smote=r['smote'], old_variant=old, old_value=before[0],
                                new_variant=new, new_value=v, source=src, old_result=o1, new_result=o2,
                                changed=('yes' if o1 != o2 else 'no')))
                if m.get('is_existing_chosen'):
                    rule_a[(vkey, r['dataset_as_printed'])] = v
        d['proposed_column'] = coltext
        d['notes'] = NOTE + f'proposed values replaced by {new} under D35 (the earlier {old} values are kept per row as ' \
            f'replaced_by_D35). ' + d.get('notes', '')
        f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    vo = D / 'out/verified_outcomes.csv'
    rows = list(csv.DictReader(open(vo, encoding='utf-8-sig')))
    fields = list(rows[0].keys())
    n = 0
    for r in rows:
        key = (r['paper'], r['dataset_as_printed'] or r['dataset'])
        if r['paper'] in {p[0] for p in PAPERS.values()}:
            v = rule_a.get(key) or rule_a.get((r['paper'], r['dataset']))
            assert v is not None, f'STOP: no D35 value for rule-A row {key}'
            p, s = num(v), num(r['smote'])
            r['proposed'] = v
            r['diff'] = repr(round(p - s, 6)).rstrip('0').rstrip('.') if p is not None and s is not None else r['diff']
            r['raw_sign'] = '+' if p > s else '-' if p < s else '='
            n += 1
    with open(vo, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    out = D.parent.parent / 'd35_changes.csv'
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(log[0]))
        w.writeheader()
        w.writerows(log)
    ch = [x for x in log if x['changed'] == 'yes']
    print(f'{len(log)} all-metric values replaced in 4 papers, {len(ch)} results change; {n} rule-A rows patched; log {out}')


if __name__ == '__main__':
    main()
