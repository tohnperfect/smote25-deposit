#!/usr/bin/env python3
"""Apply rulings B and B2 of the team lead (11 Nov 2026; confirmed for the whole screen on 12 Nov) to the facts that the
AI pass over the included records recorded (data/search/screening_full_2026-11-11/rule_b/out/batch*_facts.csv).

Rule (as the independent AI check applied it, report v3): a record whose scheme is `own` or `unclear` stays included.
A record whose scheme is `existing-parts` is excluded under E1 when its generator is a standard generator
(`deep-generative`, `statistical` or `augmentation`; ruling B2); otherwise it stays included only when the paper
presents the chain as its contribution and compares it with another way of resampling (ruling B). Ruling C (task
scope) excludes nothing: every task is in scope. The pass reads more strictly than the independent check (on the
check's sample of 299 includes it excludes 44 where the check excluded 10, all 10 among them), so the team lead decided
(12 Nov 2026) that a record failing B or B2 is excluded only when the pass recorded its facts with high confidence; at
medium or low confidence it becomes unsure (U-rule-B) and goes to the authors' check or the full text.

Writes rule_b/rule_b_decisions.csv (one row per record read: the facts, the decision under B alone, the decision
under B and B2, the ruling that excluded it) and rule_b/rule_b_summary.json. When the check's facts
(check/returns/second_pass_facts.csv) are present, the summary also gives the agreement of this pass with the check
on the records both read; on the check's random sample of includes it compares with the check's corrections (its
return file in check/returns/, or until then the corrections its report lists, check/from_report/).
Usage: python3 -I scripts/rule_b_decide.py DRAFT_DIR
"""
import collections
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rulings import decide  # noqa: E402  (the rule itself, shared with scripts/analyze_samples.py)

D = Path(sys.argv[1]) / 'data/search/screening_full_2026-11-11'


rows = []
for p in sorted((D / 'rule_b/out').glob('batch*_facts.csv')):
    for f in csv.DictReader(open(p, encoding='utf-8')):
        b, bb2, rule = decide(f)
        final = bb2 if bb2 == 'include' or f['confidence'] == 'high' else 'unsure'
        f.update(batch=p.name[5:8], decision_B=b, decision=bb2, rule=rule, final=final,
                 code={'exclude': 'E1', 'unsure': 'U-rule-B'}.get(final, ''))
        rows.append(f)
recs = [r['rec'] for r in rows]
if len(recs) != len(set(recs)):
    sys.exit('STOP: a record appears twice in the facts')
cols = ['rec', 'batch', 'scheme', 'generator', 'presented', 'compared', 'task', 'confidence', 'reason', 'decision_B',
        'decision', 'rule', 'final', 'code']
with open(D / 'rule_b/rule_b_decisions.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, cols, extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)

summ = {'read': len(rows), 'scheme': dict(collections.Counter(r['scheme'] for r in rows)),
        'generator': dict(collections.Counter(r['generator'] for r in rows)),
        'task': dict(collections.Counter(r['task'] for r in rows)),
        'confidence': dict(collections.Counter(r['confidence'] for r in rows)),
        'decision_B': dict(collections.Counter(r['decision_B'] for r in rows)),
        'decision': dict(collections.Counter(r['decision'] for r in rows)),
        'excluded_by_rule': dict(collections.Counter(r['rule'] for r in rows if r['decision'] == 'exclude')),
        'final': dict(collections.Counter(r['final'] for r in rows)),
        'final_by_rule': {k: dict(collections.Counter(r['rule'] for r in rows if r['final'] == k)) for k in ('exclude', 'unsure')},
        'failing_by_confidence': dict(collections.Counter(r['confidence'] for r in rows if r['decision'] == 'exclude')),
        'rule': __doc__.split('Rule (')[1].split('Writes')[0].strip()}

# agreement with the independent check on the records both read (its facts, report v3, method/second_pass_facts.csv)
sp = D / 'check/returns/second_pass_facts.csv'
if sp.exists():
    ck = {r['rec']: r for r in csv.DictReader(open(sp, encoding='utf-8-sig'))}
    both = [r for r in rows if r['rec'] in ck]
    summ['check_facts_file'] = sp.name
    summ['check_read'] = len(ck)
    summ['both_read'] = len(both)
    if both:
        # the check's file (v3) has decision_rule_B (ruling B alone) and decision (rulings B and B2)
        keyd = next((k for k in ('decision_B_B2', 'decision_b_b2', 'decision_BB2', 'decision_rule_B_B2', 'decision')
                     if k in next(iter(ck.values()))), None)
        summ['check_decision_column'] = keyd
        if keyd:
            agree = sum(1 for r in both if ck[r['rec']][keyd].strip().lower().startswith(r['decision'][:3]))
            summ['agree_decision'] = agree
            summ['disagree'] = [{'rec': r['rec'], 'this_pass': r['decision'], 'check': ck[r['rec']][keyd]} for r in both
                                if not ck[r['rec']][keyd].strip().lower().startswith(r['decision'][:3])]
            summ['both_read_by_list'] = dict(collections.Counter(ck[r['rec']].get('list', '') for r in both))
            summ['check_excluded_both'] = sum(1 for r in both if ck[r['rec']][keyd].strip().lower().startswith('exc'))
            summ['pass_excluded_both'] = sum(1 for r in both if r['decision'] == 'exclude')
            summ['pass_final_excluded_both'] = sum(1 for r in both if r['final'] == 'exclude')
# agreement with the independent check on its random sample of includes (its corrections in the v3 return file)
ret = sorted((D / 'check/returns').glob('RETURN_screen_decisions_*_v3.csv')) if (D / 'check/returns').exists() else []
# until the return files are in check/returns/, the 11 sample corrections as the check's report lists them (v0.12)
if not ret and (D / 'check/from_report/sample_corrections_v3_from_report.csv').exists():
    ret = [D / 'check/from_report/sample_corrections_v3_from_report.csv']
if ret:
    summ['sample_source'] = [f.relative_to(D).as_posix() for f in ret]
    s2 = {r['rec'] for r in csv.DictReader(open(D / 'check/csv/2_includes.csv', encoding='utf-8-sig'))}
    corr = {}
    for f in ret:
        for r in csv.DictReader(open(f, encoding='utf-8-sig')):
            if (r.get('list') or '').strip().startswith('2') and (r.get('person_decision') or '').strip():
                corr[r['rec'].strip()] = r['person_decision'].strip()
    mine = {r['rec']: r['decision'] for r in rows if r['rec'] in s2}
    fin = {r['rec']: r['final'] for r in rows if r['rec'] in s2}
    summ['sample_final_excluded'] = sum(1 for k, v in fin.items() if v == 'exclude')
    summ['sample_final_both_excluded'] = sum(1 for k, v in fin.items() if v == 'exclude' and corr.get(k) == 'exclude')
    summ['sample_final_unsure'] = sum(1 for k, v in fin.items() if v == 'unsure')
    _c = {k for k in fin if corr.get(k) == 'exclude'}
    _f = {k for k, v in fin.items() if v == 'exclude'}
    _n = len(fin)
    if _n:
        _a = sum(1 for k in fin if (k in _c) == (k in _f))
        _pe = (len(_c) / _n) * (len(_f) / _n) + (1 - len(_c) / _n) * (1 - len(_f) / _n)
        summ['sample_final_agree'] = _a   # excluded by the pass (high confidence) against excluded by the check
        summ['sample_final_kappa'] = round((_a / _n - _pe) / (1 - _pe), 3) if _pe < 1 else None
    chk_ex = {k for k in mine if corr.get(k) == 'exclude'}
    my_ex = {k for k, v in mine.items() if v == 'exclude'}
    n_ = len(mine)
    agree = sum(1 for k in mine if (k in chk_ex) == (k in my_ex))
    pe = ((len(chk_ex) / n_) * (len(my_ex) / n_) + (1 - len(chk_ex) / n_) * (1 - len(my_ex) / n_)) if n_ else 0
    summ.update(sample_includes_both=n_, sample_check_excluded=len(chk_ex), sample_pass_excluded=len(my_ex),
                sample_both_excluded=len(chk_ex & my_ex), sample_agree=agree,
                sample_kappa=round((agree / n_ - pe) / (1 - pe), 3) if n_ and pe < 1 else None,
                sample_disagree=[{'rec': k, 'this_pass': mine[k], 'check': corr.get(k, 'include (no correction)')}
                                 for k in sorted(mine) if (k in chk_ex) != (k in my_ex)])
json.dump(summ, open(D / 'rule_b/rule_b_summary.json', 'w', encoding='utf-8'), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k not in ('rule', 'disagree', 'sample_disagree')}, indent=1))
