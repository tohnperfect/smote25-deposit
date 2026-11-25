#!/usr/bin/env python3
"""GLOS: six dataset entries recoded as modified by the authors (WP3 adjudication, 12 Nov 2026), and the Section 5
counts that change.

Finding. The blind second pass coded GLOS (Han et al. 2023) as inducing an imbalance profile; the adjudication
confirmed it from the paper: "In order to examine the robustness of GLOS in different imbalanced situations, we
selected Segment and Texture data sets and modified them to different imbalanced cases" (PDF p.13, printed p.2083;
the three cases are multi-minority, multi-majority and both). The verified sheet of the Data extraction had coded the
six Segment and Texture entries by its name rules (Toon, 18 Oct): Segment, Texture, Texture_s and Texture_l
"original" (multiclass common name, no modification stated), Segment_2 and Segment_6 "repository-defined" (KEEL
file-name pattern). Its own note says the sets were modified. The originals are balanced (UCI Segment 330 per class;
KEEL Texture 500 per class) while GLOS prints IR 9.9 and 10 for all six, so all six are the authors' versions.

Table 5 of the paper says the papers outside the Data count of modifying papers "are not counted unless the second
pass finds one"; the second pass found GLOS. This script recodes the six entries in the audit vocabulary of
build/modified_operations.py (ops IM: the imbalance is changed on purpose; how the class sizes were changed is not
described, so no US/CS tag; missing information: minority class not stated, because the paper does not say which
classes were reduced), and recounts the numbers that Section 5 prints. It first recomputes every number from the
team's files WITHOUT the recode and stops unless they equal the numbers printed now, so the recount uses the same
definitions as the Data section. Nothing in the team repository is changed.

Usage: python3 -I glos_recount.py <team_repo> <corpus_dir>
Writes GLOS_recount.json and GLOS_entries_recoded.csv next to this script.
"""
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO, CORPUS = Path(sys.argv[1]), Path(sys.argv[2])
DS = REPO / 'Data section'
HERE = Path(__file__).resolve().parent
GLOS = {'P063-D016': 'Segment', 'P063-D017': 'Segment_2', 'P063-D018': 'Segment_6',
        'P063-D019': 'Texture', 'P063-D020': 'Texture_s', 'P063-D021': 'Texture_l'}
QUOTE = ['In order to examine the robustness of GLOS in differ', 'ent imbalanced situations, we selected Segment and Texture',
         'data sets and modified them to different imbalanced cases']


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s)).lower()


def rd(p):
    return list(csv.DictReader(open(p, encoding='utf-8-sig')))


def quote_page():
    for i, p in enumerate((CORPUS / 'txt/GLOS-2023__main.txt').read_text(encoding='utf-8', errors='ignore').split('\f')):
        t, k = norm(p), 0
        for fr in QUOTE:
            j = t.find(norm(fr), k)
            if j < 0:
                break
            k = j + len(fr)
        else:
            return i + 1
    raise SystemExit('STOP: the GLOS quote is not in the text')


def band(y):
    y = int(y)
    for hi, lab in ((2004, 'up to 2004'), (2009, '2005-2009'), (2014, '2010-2014'), (2019, '2015-2019'), (2024, '2020-2024')):
        if y <= hi:
            return lab
    return '2025-2026'


def counts(rec, aud, purpose_papers, several, verif):
    c = Counter(r['category'] for r in rec)
    per = {}
    for b in ('2015-2019', '2020-2024', '2025-2026'):
        rs = [r for r in rec if band(r['year']) == b]
        per[b] = dict(modified_pct=round(100 * sum(r['category'] == 'modified' for r in rs) / len(rs)),
                      repository_pct=round(100 * sum(r['category'] == 'repository-defined' for r in rs) / len(rs)))
    im = [a for a in aud if 'IM' in a['ops'].split(';')]
    miss = [a for a in aud if a['missing_information'].strip()]
    mi = Counter()
    for a in aud:
        for m in [x.strip() for x in a['missing_information'].split(';') if x.strip()]:
            mi[m] += 1
    V = [v for v in verif if v['verif'].startswith('V-')]
    return dict(entries=len(rec), original=c['original'], repository_defined=c['repository-defined'],
                modified=c['modified'], synthetic=c['synthetic'], not_stated=c['not stated'],
                modified_papers=len({a['paper_key'] for a in aud}), by_period=per,
                im_entries=len(im), im_papers=len({a['paper_key'] for a in im}),
                purpose_stated_papers=len(purpose_papers), entries_missing_information=len(miss),
                characteristics_not_printed=mi['characteristics not printed'], target_ir_not_stated=mi['target IR not stated'],
                minority_class_not_stated=mi['minority class not stated'], several_levels_papers=len(several),
                verifiable_entries=len(V), verifiable_papers=len({v['paper'] for v in V}),
                verifiable_files=len({v['file'] for v in V}))


def main():
    page = quote_page()
    rec = rd(DS / 'out/dataset_records.csv')
    aud = rd(DS / 'out/modified_operations_audit.csv')
    pur = rd(DS / 'out/modification_purpose_by_paper.csv')
    verif = rd(DS / 'difficulty/verifiability_entries.csv')
    purpose = {p['paper_key'] for p in pur if p['stated_purpose'] != 'not stated'}
    several = {p['paper_key'] for p in pur if p['several_levels'] == 'yes'}
    old = counts(rec, aud, purpose, several, verif)
    printed = dict(entries=1756, original=537, repository_defined=470, modified=341, synthetic=213, not_stated=195,
                   modified_papers=43, im_entries=147, im_papers=9, purpose_stated_papers=24, entries_missing_information=103,
                   characteristics_not_printed=65, target_ir_not_stated=18, minority_class_not_stated=15,
                   several_levels_papers=12, verifiable_entries=991, verifiable_papers=65, verifiable_files=261)
    bad = {k: (old[k], v) for k, v in printed.items() if old[k] != v}
    assert not bad, f'STOP: recount without the recode differs from the printed numbers: {bad}'
    assert old['by_period']['2020-2024'] == dict(modified_pct=12, repository_pct=28), old['by_period']
    # the recode
    rec2 = [dict(r) for r in rec]
    recoded = []
    for r in rec2:
        if r['record_id'] in GLOS:
            assert r['paper_key'] == 'GLOS'
            recoded.append(dict(record_id=r['record_id'], name_as_reported=r['name_as_reported'],
                                category_before=r['category'], category_after='modified', ops='IM', ops_conditional='',
                                changes_imbalance_level='deliberately changed', purpose_stated_by_authors='robustness test',
                                missing_information='minority class not stated', confidence='explicitly reported',
                                evidence_ref=f'PDF p.{page} (printed p.2083): "' + ' '.join(QUOTE).replace('differ ent', 'different') + '"; Table 1, PDF p.9',
                                decided_by='AI adjudication (Claude Opus 5.5, 12 Nov 2026), D31'))
            r['category'] = 'modified'
    assert len(recoded) == 6
    aud2 = aud + [dict(paper_key='GLOS', record_id=x['record_id'], normalized_name=x['name_as_reported'].lower(),
                       ops='IM', missing_information='minority class not stated') for x in recoded]
    new = counts(rec2, aud2, purpose | {'GLOS'}, several | {'GLOS'},
                 [dict(v, verif=('U-modified_not_published' if v['record_id'] in GLOS and v['verif'].startswith('V-') else v['verif']))
                  for v in verif])
    out = dict(source='Data section/out/dataset_records.csv, modified_operations_audit.csv, modification_purpose_by_paper.csv; '
                      'Data section/difficulty/verifiability_entries.csv (team repository, unchanged)',
               rule='the six Segment and Texture entries of GLOS are modified (WP3 adjudication; Table 5 rule)',
               quote_page=page, before=old, after=new,
               changed={k: [old[k], new[k]] for k in new if old[k] != new[k] and k != 'by_period'},
               changed_period={b: [old['by_period'][b], new['by_period'][b]] for b in new['by_period']
                               if old['by_period'][b] != new['by_period'][b]},
               decided_by='AI adjudication (Claude Opus 5.5, 12 Nov 2026), spot-checked by the team lead (D31)')
    (HERE / 'GLOS_recount.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
    with open(HERE / 'GLOS_entries_recoded.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(recoded[0]))
        w.writeheader()
        w.writerows(recoded)
    print(json.dumps(out['changed'], indent=1), json.dumps(out['changed_period'], indent=1))


if __name__ == '__main__':
    main()
