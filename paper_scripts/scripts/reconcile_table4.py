#!/usr/bin/env python3
"""WP1 steps 2 and 4: recompute every row of Table 4 (tab:denominators) from the
team's coding sheets under each draft's own definition, and list the papers that
make the two counts differ.

Reads (team repository, read only):
  Data section/out/full_summary.json         per-paper SMOTE baseline kind, result granularity
  Data section/out/verified_datasets.csv     per-entry how_obtained_final (value_status = verified)
  Data section/out/data_handling_summary.json reason for the choice of data (ai_draft values)
  Data section/out/modified_operations_summary.json
  Data section/out/section7_key_map.csv      Data key <-> Section 7 (Evaluation) key
  Data section/build/analyse_dataset_usage.py norm() for dataset names
  Evaluation section/section07-coded-data.json
Writes: reconcile/table4_reconciliation.md and reconcile/table4_rows.csv
Usage: python3 scripts/reconcile_table4.py <team-repo-root> [outdir]
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

repo = Path(sys.argv[1])
outdir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('reconcile')
outdir.mkdir(parents=True, exist_ok=True)
D = repo / 'Data section'
sys.path.insert(0, str(D / 'build'))
import analyse_dataset_usage as A  # noqa: E402  (the Data section's own norm())

full = json.loads((D / 'out/full_summary.json').read_text(encoding='utf-8'))['papers']
dkeys = {p['key'] for p in full}
ents = list(csv.DictReader(open(D / 'out/verified_datasets.csv', encoding='utf-8-sig')))
dh = json.loads((D / 'out/data_handling_summary.json').read_text(encoding='utf-8'))
mo = json.loads((D / 'out/modified_operations_summary.json').read_text(encoding='utf-8'))
kmap = list(csv.DictReader(open(D / 'out/section7_key_map.csv', encoding='utf-8-sig')))
ev = json.loads((repo / 'Evaluation section/section07-coded-data.json').read_text(encoding='utf-8'))
emp = [r for r in ev if r.get('empirical')]

d2e = {r['data_section_key']: r['section7_key'] for r in kmap}
e2d = {v: k for k, v in d2e.items()}
ekeys = {r['key'] for r in emp}


def as_e(keys):
    return {d2e.get(k, f'?{k}') for k in keys}


def diff(dset_dkeys, eset_ekeys):
    a, b = as_e(dset_dkeys), set(eset_ekeys)
    return sorted(a - b), sorted(b - a)


rows, md = [], []


def row(name, data_def, data_n, eval_def, eval_n, only_d, only_e, diagnosis, status):
    rows.append(dict(quantity=name, data_definition=data_def, data_count=data_n,
                     eval_definition=eval_def, eval_count=eval_n,
                     only_in_data='; '.join(only_d), only_in_eval='; '.join(only_e),
                     diagnosis=diagnosis, proposed_status=status))
    md.append(f'### {name}\n\n| | Definition | Count |\n|---|---|---|\n'
              f'| Data | {data_def} | {data_n} |\n| Evaluation | {eval_def} | {eval_n} |\n\n'
              f'Only in the Data set ({len(only_d)}): {", ".join(only_d) or "none"}\n\n'
              f'Only in the Evaluation set ({len(only_e)}): {", ".join(only_e) or "none"}\n\n'
              f'**Diagnosis.** {diagnosis}\n\n**Proposed status.** {status}\n')


# 1. papers with an evaluation
o_d, o_e = diff(dkeys, ekeys)
row('Papers with an evaluation', 'papers with an evaluation on data (full_summary.json)', len(dkeys),
    'empirical = true (section07-coded-data.json)', len(ekeys), o_d, o_e,
    'The two lists differ by exactly the papers named here; the Data draft keeps Tomek links and '
    'the critical review of Hassanat et al., the Evaluation draft does not.',
    'explained (no decision needed)')

# 2. SMOTE as a baseline
kind = {p['key']: p['smote_kind'] for p in full}
plain = {k for k, v in kind.items() if v == 'plain SMOTE'}
wrap = {k for k, v in kind.items() if v.startswith('SMOTE variant')}
e_smote = {r['key'] for r in emp if r.get('smote_baseline')}
o_d, o_e = diff(plain, e_smote)
o_d2, o_e2 = diff(plain | wrap, e_smote)
wrapped_in_eval = sorted(as_e(wrap) & e_smote)
row('SMOTE used as a baseline (plain)', 'smote_kind = plain SMOTE', len(plain),
    'smote_baseline = true', len(e_smote), o_d, o_e,
    f'Hypothesis of the plan (Evaluation counts wrapped SMOTE as plain): {len(wrapped_in_eval)} of the '
    f'{len(wrap)} papers the Data draft codes as wrapped SMOTE are counted as SMOTE baselines by the '
    f'Evaluation draft ({", ".join(wrapped_in_eval) or "none"}). Against plain + wrapped ({len(plain | wrap)}), '
    f'{len(o_d2)} papers are only in the Data set and {len(o_e2)} only in the Evaluation set '
    f'(only Data: {", ".join(o_d2) or "none"}; only Evaluation: {", ".join(o_e2) or "none"}).',
    'DECISION: one definition (plain only, or plain + wrapped stated as such), then recode the papers listed')

# 3. papers that modify data
mod_d = {e['paper'] for e in ents if e['how_obtained_final'] == 'modified'}
mod_e = {r['key'] for r in emp if r['r2'].get('mod_released') is not None}
rel_e = {r['key'] for r in emp if r['r2'].get('mod_released') is True}
o_d, o_e = diff(mod_d, mod_e)
row('Papers that modify data', 'papers with at least one entry whose how_obtained_final = modified '
    f'({sum(1 for e in ents if e["how_obtained_final"] == "modified")} entries)', len(mod_d),
    'r2.mod_released is true or false (null = data not modified)', len(mod_e), o_d, o_e,
    'Per-entry against per-study coding. The Evaluation reading counts a study as modifying when any data '
    f'are changed before use, including repository splits and generated sets in some cases; released: {len(rel_e)} '
    '(Evaluation) against 3 papers that publish modified files (Data). Read the papers listed against the two rules.',
    'DECISION: which definition the paper uses in each place; state both where both appear')

# 4. synthetic data
syn_d = {e['paper'] for e in ents if e['how_obtained_final'] == 'synthetic'}
syn_e = {r['key'] for r in emp if (r['datasets'].get('n_synthetic') or 0) > 0}
o_d, o_e = diff(syn_d, syn_e)
row('Papers with synthetic data', 'papers with at least one entry whose how_obtained_final = synthetic '
    f'({sum(1 for e in ents if e["how_obtained_final"] == "synthetic")} entries)', len(syn_d),
    'datasets.n_synthetic > 0 (the Evaluation table prints 30 from a hand-curated list)', len(syn_e), o_d, o_e,
    'The coded field gives 29 in both drafts; the 30 of the Evaluation table comes from a curated key list in '
    'make_tables_v41.py, not from the coded field.',
    'nearly explained: check the one extra study in the Evaluation list, then use 29 or state the rule')

# 5. reason given for the choice of data
ct = dh['crit_type']
given = ct.get('own reason', 0) + ct.get('cites prior work', 0) + ct.get('generic only', 0)
e_reason = {r['key'] for r in emp if r['r2'].get('data_stated')}
ng = set(dh['crit_not_stated_or_generic'])
reason_d = dkeys - (ng - set())  # 'generic only' papers are inside ng
o_d, o_e = diff(dkeys - ng, e_reason)
row('Reason given for the choice of data',
    f'crit_type in data_handling_summary.json (own reason {ct.get("own reason")}, cites prior work '
    f'{ct.get("cites prior work")}, generic only {ct.get("generic only")}, not stated {ct.get("not stated")}); '
    'all values ai_draft', f'{given} of 73 (specific reason: {len(dkeys - ng)})',
    'r2.data_stated = true', len(e_reason), o_d, o_e,
    'The Data figure rests on values still marked ai_draft (data_handling_matrix.csv); the standing rules do '
    'not allow citing them as final. The Evaluation count comes from the second, page-referenced reading. '
    'The diff compares the Data papers with a specific reason (not "not stated" or "generic only") with the '
    'Evaluation set.',
    'DECISION and verification: verify the Data codes (or drop the Data count) and use the Evaluation count')

# 6. per-dataset results
gran = {p['key']: p['results_granularity'] for p in full}
pd_d = {k for k, v in gran.items() if v in ('per-dataset', 'per-dataset partial')}
pd_e = {r['key'] for r in emp if 'per-dataset table' in (r.get('reporting') or [])}
o_d, o_e = diff(pd_d, pd_e)
row('Per-dataset results', 'results_granularity = per-dataset (47) or per-dataset partial (8): '
    'a per-dataset table that pairs the proposal with SMOTE', len(pd_d),
    "'per-dataset table' in reporting: any per-dataset results table", len(pd_e), o_d, o_e,
    'Different questions: the Data draft asks whether the proposal and SMOTE are paired per dataset, '
    'the Evaluation draft whether any per-dataset table is printed. Papers without SMOTE as a baseline '
    'can only be in the Evaluation set.',
    'explained once the two definitions are stated in the text (no recoding needed)')

# 7. dataset families
famrows = list(csv.DictReader(open(D / 'out/dataset_families.csv', encoding='utf-8-sig')))
name2fam = {r['normalized_name']: r['family'] for r in famrows}
fam_d = {}
unmapped = sum(1 for e in ents if A.norm(e['name']) not in name2fam)
for f in ('ecoli', 'yeast', 'glass'):
    fam_d[f] = {e['paper'] for e in ents if name2fam.get(A.norm(e['name'])) == f}
fam_e = {f: {r['key'] for r in emp if f in (r.get('ds_families') or [])} for f in ('ecoli', 'yeast', 'glass')}
for f in ('ecoli', 'yeast', 'glass'):
    o_d, o_e = diff(fam_d[f], fam_e[f])
    row(f'Dataset family {f}', 'papers with an entry assigned to the family in out/dataset_families.csv '
        f'(the Data draft\'s family rule; {unmapped} entries without a family row)', len(fam_d[f]), 'family in ds_families (hand-normalised family list)',
        len(fam_e[f]), o_d, o_e,
        'The Data family rule (dataset_families.csv) against the hand-normalised ds_families of the Evaluation '
        'coding; read the entries of the papers listed to see which rule misassigns them.', 'DECISION: one family rule; then regenerate both counts')

# 8. binarising papers (three counts inside the Data draft)
mrb = dh['minority_rule_among_binarised']
row('Papers that binarise or convert classes (inside the Data draft)',
    f'(a) minority_rule_among_binarised in data_handling_summary.json, ai_draft: {sum(mrb.values())} papers '
    f'({mrb}); (b) modified_operations_summary tag_papers CS (class structure): {mo["tag_papers"]["CS"]} papers; '
    f'(c) changes_task_papers: {mo["changes_task_papers"]} papers', '37 / 30 / 29 in the text', 'n/a', 'n/a', [], [],
    f'(a) counts papers whose data are binarised by anyone, including {mrb.get("repository-defined", 0)} that use '
    'repository-defined binary splits; (a) minus those = '
    f'{sum(mrb.values()) - mrb.get("repository-defined", 0)}. (b) counts papers with a modified entry tagged as a '
    'class-structure change. The three figures answer three questions; the 37 rests on ai_draft values.',
    'DECISION: name the question each count answers in the sentence, or keep one; verify (a) before citing it')

with open(outdir / 'table4_rows.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
head = ('# Table 4 reconciliation (WP1 steps 2 and 4)\n\nGenerated by `scripts/reconcile_table4.py` from the '
        'team repository (read only). Paper keys are the Evaluation draft\'s (Section 7) keys; Data keys are '
        'mapped with `Data section/out/section7_key_map.csv` (unmapped keys are prefixed with `?`).\n\n')
(outdir / 'table4_reconciliation.md').write_text(head + '\n'.join(md), encoding='utf-8')
for r in rows:
    print(f"{r['quantity'][:45]:<46} Data {str(r['data_count']):>22}  Eval {str(r['eval_count']):>4}  "
          f"onlyD {len(r['only_in_data'].split('; ')) if r['only_in_data'] else 0:>2}  "
          f"onlyE {len(r['only_in_eval'].split('; ')) if r['only_in_eval'] else 0:>2}")
