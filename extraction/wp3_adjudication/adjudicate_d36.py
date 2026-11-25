#!/usr/bin/env python3
"""D36 adjudication: which papers that modify data publish the modified files themselves (12 Nov 2026).

Decision D36 of the team lead (11 Nov 2026): "modified data released" means that the modified files themselves are
public. Code that regenerates them, data "on request", the original data or a public repository of the unmodified
sets do not count. The candidates are every paper that one of the three readings named:
  Data first pass      3   out/modification_purpose_by_paper.csv, publishes_modified_data = yes
  Evaluation first pass 10  section07-coded-data.json, r2.mod_released = true
  blind second pass    8   data/wp3_blind/DATA_handling_agreement.json, modified_data_released_second
plus every paper among the 44 that modify data (the 43 of the Data section and GLOS, which glos_recount.py adds) whose
text has a release sentence: SCAN below is run on the corpus texts (the reference list of the main text cut off), and
every paper with a match must have a decision or be listed in CROSSREF (matches that are only cross-references). Each
decision quotes the paper; every quote is checked against the text (pdftotext, NFKC, whitespace and case normalised)
and the PDF page is taken from the page breaks. The script stops if a quote is not found or a match is left undecided.

SPOT (v0.31) holds what the spot check (D31) asked to recheck and what the recheck found (RBO: project page checked,
the decision stands).
Usage: python3 -I adjudicate_d36.py <corpus_txt_dir> <team_repo> <v16_dir>
Writes MODIFIED_RELEASED_adjudicated.csv and MODIFIED_RELEASED_summary.json next to this script.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

TXT, REPO, V16 = (Path(a) for a in sys.argv[1:4])
HERE = Path(__file__).resolve().parent
BY = 'AI adjudication (Claude Opus 5.5, 12 Nov 2026)'


def norm(s):
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    return re.sub(r'\s+', ' ', s).strip().lower()


def pages(stem):
    out = []
    for f in sorted(TXT.glob(stem + '__*.txt')):
        part = f.name.split('__')[1][:-4]
        for i, p in enumerate(f.read_text(encoding='utf-8', errors='ignore').split('\f')):
            out.append((part, i + 1, norm(p)))
    return out


def locate(stem, frags):
    """All fragments must occur, in order, on one page of one file; returns 'main p.N' or 'supp1 p.N'."""
    for part, pg, text in pages(stem):
        k, ok = 0, True
        for fr in frags:
            j = text.find(norm(fr), k)
            if j < 0:
                ok = False
                break
            k = j + len(norm(fr))
        if ok:
            return f'{part} p.{pg}'
    raise SystemExit(f'STOP: quote not found in {stem}: {frags}')


# paper key (Data) -> corpus stem, decision, confidence, quote fragments, note
D = [
    ('INOS', 'INOS-2013', 'yes', 'high',
     ['we have shared our 48 apportioned', 'data sets online (http://sites.google.com/site/sstarcao/)'],
     'the 48 imbalanced apportions made from balanced UCR sets are the modified files; missed by the Data keyword list'),
    ('SMOTE-IPF', 'SMOTE-IPF-2015', 'yes', 'moderate',
     ['This web-page also includes the basic information of this paper, the datasets used and the parameter setup'],
     'the datasets used include the noisy versions built from the KEEL sets (Section 4.2); the page is named, the files are not listed one by one'),
    ('k-means SMOTE', 'KMeansSMOTE-2018', 'yes', 'high',
     ['All modified and simulated datasets used in the study are made available at'], ''),
    ('G-SMOTE', 'G-SMOTE-2019', 'yes', 'high',
     ['Table 1 shows a summary of the final 69 data sets that can be found at'],
     'the final 69 sets include those undersampled by the authors to raise the imbalance ratio'),
    ('CTGAN / TVAE', 'CTGAN-2019', 'yes', 'moderate',
     ['All in all there are 8 real datasets in our benchmarking suite'],
     'MNIST12 and MNIST28 (resized and binarized by the authors) are among the 8 real sets of the benchmark, which the paper '
     'releases (footnote 2: "Our benchmark can be found at https://github.com/DAI-Lab/SDGym")'),
    ('GAMO', 'GAMO-2019', 'yes', 'moderate',
     ['Codes & data at: https://github.com/SankhaSubhra/'],
     'the supplement repeats it ("Codes and datasets can also be downloaded from https://github.com/SankhaSubhra/GAMO") '
     'but also gives a script that outputs "a class-imbalanced version similar to ours": a judgment call for the spot check'),
    ('HDE', 'HDE-2021', 'yes', 'high',
     ['All the 42 datasets adopted in our experiments have been uploaded to GitHub'],
     'the 14 sets made highly imbalanced by the authors are among the 42'),
    ('DSRBF / Static-SMOTE', 'DSRBF-2011', 'yes', 'high',
     ['All the datasets and', 'the corresponding partitions have been included in a public'], ''),
    ('OVO-SMOTE', 'OVO-SMOTE-2013', 'yes', 'moderate',
     ['point out that the data-set partitions employed in this paper are',
      'available for download at the KEEL data-set repository'],
     'the modified entries are KEEL multiclass files with the instances that have missing values removed; the paper says '
     'the partitions it used are in KEEL'),
    ('MC-MBRC', 'MC-MBRC-2024', 'no', 'high',
     ['Data will be made available on request'], 'on request is not public (D36)'),
    ('RBO', 'RBO-2019', 'no', 'moderate',
     ['Together with the', 'code, we provided the partitioning of the datasets into the cross'],
     'the code adds the label and feature noise; the noisy files themselves are not said to be released'),
    ('MC-CCR', 'MC-CCR-2020', 'no', 'high', ['https://github.com/michalkoziarski/MC-CCR'], 'code only'),
    ('NBU', 'NBU-2020', 'no', 'high', ['Source code available at https://github.com/fonkafon/NB-undersampling'],
     'code and results only'),
    ('SPE', 'SPE-2020', 'no', 'high', ['github.com/ZhiningLiu1998/self-paced-ensemble'], 'code and further results only'),
    ('MC-NCLWO', 'MC-NCLWO-2025', 'no', 'high', ['https://github.com/taoliangliang/MC-NCLWO/result'], 'result tables only'),
    ('SVDD-WSMOTE', 'SVDDWSMOTE-2022', 'no', 'high', ['can be found in https://github.com/Zheng7777/simulated-datasets'],
     'the four simulated sets are synthetic, not modified; the sets made more imbalanced are not said to be released'),
    ('GMMSampling', 'GMMSampling-2024', 'no', 'high',
     ['the artificial datasets can be found in the repository of multi-imbalance'],
     'synthetic sets only; the real sets are the public UCI files'),
]
# added on 12 Nov 2026 after SCAN: release sentences about code or about unmodified data only
D += [
    ('DGOT', 'DGOT-2026', 'no', 'high', ['Our code has been made', 'publicly available at https://github.com/MLneuers/DGOT'],
     'code only'),
    ('GOIO', 'GOIO-2025', 'no', 'high', ['The source code of GOIO is available', 'at https://github.com/MLneuers/GOIO'],
     'code only'),
    ('DLexiBoost', 'DLexiBoost-2020', 'no', 'high',
     ['Our implementation of LexiBoost can be', 'found at https://github.com/Shounak-D/LexiBoost'], 'code only'),
    ('RSMOTE', 'RSMOTE-2021', 'no', 'high',
     ['The implementation of the proposed RSMOTE in programming language Python is available at'], 'code only'),
    ('SMOTE', 'SMOTE-2002', 'no', 'high', ['The data is available from the USF Intelligent Systems Lab'],
     'the footnote is about Mammography, which the paper uses unmodified; its modified entries (Adult, Satimage, '
     'Forest Cover, Can) are not said to be released'),
    ('RUSBoost', 'RUSBoost-2010', 'no', 'high', ['PC1 and CM1 can be downloaded from the'],
     'unmodified NASA sets; the binarized UCI sets are not said to be released'),
    ('SMOM', 'SMOM-2017', 'no', 'high', ['The others are available from UCI'],
     'unmodified UCI sets; the supplementary material holds algorithms and parameter settings, not data files'),
    ('ROS (Buda)', 'ROS-Buda-2018', 'no', 'moderate', ['Supplementary material related to this article can be found'],
     'the supplementary data (Appendix A) hold results ("results are available in Appendix A"); the subsampled MNIST, '
     'CIFAR-10 and ImageNet sets are not said to be released'),
]
# the paper that the GLOS recount adds to the papers that modify data (glos_recount.py, Table 5 rule)
RECODED = [
    ('GLOS', 'GLOS-2023', 'no', 'high',
     ['21 multi-class data sets from the UCI repository and KEEL', 'repository [38] are selected to evaluate the effectiveness of'],
     'no release or availability sentence in the paper (SCAN finds no match); the Segment and Texture sets it made '
     'imbalanced (PDF p.13) are not released'),
]
# the spot check (D31; page "SMOTE25 WP3 Check", merged in v0.31 by scripts/merge_wp3_check.py): items marked for
# change and what checking them found. paper -> (decision, confidence, note, decided_by); the quote is unchanged.
SPOT = {
    'RBO': ('no', 'high',
            'the spot check asked for the project page to be checked ("Try to access"); checked on 15 Nov 2026: '
            'github.com/michalkoziarski/RBO (one branch, last commit 93528e7 of 12 Mar 2018) holds the code, the KEEL '
            'download links, the 5x2 cross-validation partitions as row-index files (folds/*.folds.pickle: integer index '
            'arrays only) and per-fold results; datasets.py adds the label and feature noise at run time, with no fixed '
            'seed, so the noisy files themselves are not released',
            BY + '; project page checked in the WP3 spot check (15 Nov 2026)'),
}
# papers whose SCAN matches are only cross-references to their own sections, tables or cited works
CROSSREF =['A-SUWO', 'AMDO', 'COG-OS', 'EasyEnsemble / BalanceCascade', 'MWMOTE', 'RAMOBoost', 'SOUP']
SCAN = re.compile(r'(github\.com|gitlab|made (publicly |freely )?available|(is|are) (publicly |freely )?available '
                  r'(at|from|online|for download|in)|can be (found|downloaded|obtained) (at|from|in)|uploaded to|available for '
                  r'download|data availability|code availability|supplementary (material|data|file)|figshare|zenodo|'
                  r'our (web ?page|website)|on request)', re.I)


def scan(stem):
    """Release-type matches in the paper's texts; the reference list of the main text is cut off."""
    hits = 0
    for f in sorted(TXT.glob(stem + '__*.txt')):
        s = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', f.read_text(encoding='utf-8', errors='ignore')).replace('\u00ad', ''))
        if f.name.endswith('__main.txt'):
            m = re.search(r'\bReferences\b(?!.*\bReferences\b)', s, re.S)
            s = s[:m.start()] if m else s
        hits += len(SCAN.findall(s))
    return hits


# outside the 43 (no entry coded as modified in the Data definition): recorded, not counted
OUTSIDE = [
    ('KNNOR', 'KNNOR-2022', 'n.a.', 'high', ['The code (and data) in this article has been certified as Reproducible by'],
     'the Evaluation counts KNNOR as releasing modified data; in the Data definition KNNOR modifies no data (adjudicated '
     'data-handling codes: no undersampling, no noise), so it is outside this count'),
]


def main():
    m43 = [r['paper_key'] for r in csv.DictReader(open(REPO / 'Data section/out/modification_purpose_by_paper.csv', encoding='utf-8'))]
    data3 = {r['paper_key'] for r in csv.DictReader(open(REPO / 'Data section/out/modification_purpose_by_paper.csv', encoding='utf-8'))
             if r['publishes_modified_data'] == 'yes'}
    ev = json.load(open(REPO / 'Evaluation section/section07-coded-data.json', encoding='utf-8'))
    ev10 = {s['key'] for s in ev if (s.get('r2') or {}).get('mod_released') is True}
    second = json.load(open(V16 / 'data/wp3_blind/DATA_handling_agreement.json', encoding='utf-8'))['modified_data_released_second']
    km = {d['data_key']: d['s7_key'] for d in json.load(open(TXT.parent / 'key_map.json', encoding='utf-8'))}
    glos = json.load(open(HERE / 'GLOS_recount.json', encoding='utf-8'))
    assert glos['changed']['modified_papers'] == [43, 44], 'STOP: the GLOS recount does not add one paper'
    recoded = [r[0] for r in RECODED]
    assert not set(recoded) & set(m43), 'STOP: a recoded paper is already among the 43'
    m44 = m43 + recoded
    rows = []
    assert set(SPOT) <= {r[0] for r in D + RECODED + OUTSIDE}, 'STOP: a spot-check item names a paper without a decision'
    for key, stem, dec, conf, frags, note in D + RECODED + OUTSIDE:
        by = BY
        if key in SPOT:
            dec, conf, note, by = SPOT[key]
        assert (key in m44) == (dec != 'n.a.'), f'STOP: {key} membership of the 44 does not match its decision'
        where = locate(stem, frags)
        rows.append(dict(paper=key, in_43=('yes' if key in m43 else ('recoded (GLOS recount)' if key in recoded else 'no')),
                         data_first_pass=('yes' if key in data3 else ''),
                         evaluation_first_pass=('yes' if km.get(key, stem) in ev10 or stem in ev10 else ''),
                         second_pass=second.get(key, ''), adjudicated=dec, confidence=conf,
                         quote=' ... '.join(frags), where=where, note=note, decided_by=by))
    named = data3 | {k for k, v in km.items() if v in ev10} | set(second)
    missing = sorted(p for p in named if p not in {r['paper'] for r in rows})
    assert not missing, f'STOP: candidates without a decision: {missing}'
    stems = {r[0]: r[1] for r in D + RECODED}
    matched = {k: scan(stems.get(k) or km.get(k, k)) for k in m44}
    undecided = sorted(k for k, n in matched.items() if n and k not in stems and k not in CROSSREF)
    assert not undecided, f'STOP: release-type matches without a decision: {undecided}'
    out = HERE / 'MODIFIED_RELEASED_adjudicated.csv'
    with out.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    yes = sorted(r['paper'] for r in rows if r['adjudicated'] == 'yes')
    summ = dict(definition='D36: the modified files themselves are public (code, on request, or unmodified data do not count)',
                papers_that_modify_data=len(m44), recoded_by_glos_recount=recoded, publish_modified_files=len(yes), papers=yes,
                scan=dict(papers_with_matches=sum(1 for n in matched.values() if n),
                          decided=sorted(k for k, n in matched.items() if n and k in stems),
                          cross_references_only=sorted(k for k, n in matched.items() if n and k in CROSSREF),
                          decided_without_match=sorted(k for k in stems if k in m44 and not matched.get(k))),
                data_first_pass=sorted(data3), evaluation_first_pass=sorted(k for k, v in km.items() if v in ev10),
                second_pass={k: v for k, v in second.items()},
                agreement_with_adjudication={
                    'data_first_pass': f'{len(data3 & set(yes))} of {len(yes)} found, 0 wrong' if data3 <= set(yes) else 'see csv',
                    'evaluation_first_pass': 'all 9 found; its tenth (KNNOR) modifies no data in the Data definition',
                    'second_pass': '7 of 9 found (not CTGAN, OVO-SMOTE); MC-MBRC "on request" not counted'},
                decided_by=BY,
                spot_check=dict(merged='v0.31, 15 Nov 2026', marked_for_change=sorted(SPOT),
                                decision_changed=sorted(k for k, v in SPOT.items()
                                                        if v[0] != next(r[2] for r in D + RECODED + OUTSIDE if r[0] == k))))
    (HERE / 'MODIFIED_RELEASED_summary.json').write_text(json.dumps(summ, indent=1), encoding='utf-8')
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
