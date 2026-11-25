#!/usr/bin/env python3
"""Build records.json of the review page "SMOTE25 WP3 Count Check" (15 November 2026).

The spot check of the WP3 AI adjudication (page "SMOTE25 WP3 Check", merged in v0.31) drew data-handling changes by a
random sample, so two counts of Table 5 rest partly on adjudications no person has looked at:
  reason   the papers that give a reason for their choice of data (D34): 62 of 73 with the first-pass codes, 67 after
           the adjudication; 9 papers change status, and none of the 9 was drawn
  binar    the papers whose data are binarized by anyone: 37 with the first-pass codes, 47 after; 10 papers change,
           3 were drawn and agreed (AB-SMOTE, CBHSID, Loyalty-SMOTE), 7 were not
This page puts the 9 and the 7 before an author. Each card shows both passes, the AI's value and reason, what the
value does to the count, and context from the paper that the session building the page added (CONTEXT below, every
quote checked against the paper's text layer when --corpus is given).

The items are found from the data, not listed by hand: the first-pass codes are the team's data_handling_matrix.csv
(team repository, Data section/out/), the adjudicated values wp3/adjudication/DATA_handling_adjudicated.csv, and the
items already checked come from the export of the first spot check (wp3/check_page/exports/). The script stops if the
counts differ from wp3/adjudication/WP3_summary.json or if CONTEXT does not cover exactly the items found.

Usage: python3 -I scripts/build_wp3_count_check.py <draft_dir> <team_repo> <out_dir> [--corpus <corpus_txt_dir>]
Writes out_dir/records.json (short quotes from the papers: team use only, never deposited; this script rebuilds it,
and its output does not depend on --corpus, which only adds the check of the quotes).
"""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
V, REPO, OUT = (Path(a) for a in ARGS[:3])
CORPUS = Path(sys.argv[sys.argv.index('--corpus') + 1]) if '--corpus' in sys.argv else None
A = V / 'wp3/adjudication'
REASON = ('own reason', 'cites prior work', 'reason given')

# Per item: corpus stem, the PDF (the team's folder name where known, else the paper), where to look, the context that
# the session added on 15 Nov 2026 and, where that context questions the AI's stated basis, a flag shown on the card;
# each quote in 'quotes' is (pdf_page, text) and must be found on that page; a double-quoted passage of the context must
# be part of a checked quote.
CONTEXT = {
    ('SMOTEBoost', 'crit_type'): dict(
        flag="the AI's reason does not mention the sentence of p.117",
        stem='SMOTEBoost-2003', pdf='paper/Both/SMOTEBoost - Improving Prediction of the Minority Class in Boosting (PKDD 2003).pdf',
        where='printed p.112 (PDF p.6), Section 4; printed p.117 (PDF p.11), Conclusions',
        context='The data paragraph (p.112) introduces the four sets without a reason, as the AI says. The conclusion (p.117) '
                'adds: "Data sets used in our experiments contained different degrees of imbalance and different sizes, thus '
                'providing a diverse test bed." The AI\'s reason cites p.112 only; the first pass\'s \'own reason (diversity)\' '
                'matches the sentence of p.117.',
        quotes=[(11, 'Data sets used in our experiments contained different degrees of imbalance and different sizes, thus providing a diverse test bed.'),
                (6, 'Our experiments were performed on the four data sets summarized in Table 2.')]),
    ('Borderline-SMOTE', 'crit_type'): dict(
        stem='Borderline-SMOTE-2005', pdf='paper/Both/Borderline-SMOTE - A New Over-Sampling Method in Imbalanced Data Sets Learning (ICIC 2005).pdf',
        where='printed p.883 (PDF p.6), Section 4',
        context='The reason covers the simulated Circle set (to make the methods easy to understand); the UCI sets come without '
                'one: "Among the four data sets, Circle is our simulated data set depicted in Fig. 1, and the others are from UCI". '
                'Under the codebook\'s precedence (own reason, then cites prior work, then generic only, then not stated) an own '
                'reason for part of the data makes the paper \'own reason\'.',
        quotes=[(6, 'Our methods can be easily understood with the following simulated data set, Circle, which has two classes.'),
                (6, 'Among the four data sets, Circle is our simulated data set depicted in Fig. 1, and the others are from UCI')]),
    ('EasyEnsemble / BalanceCascade', 'crit_type'): dict(
        stem='EasyEnsemble-BalanceCascade-2009', pdf='Liu, Wu and Zhou, "Exploratory Undersampling for Class-Imbalance Learning", IEEE TSMC-B 39(2), 2009',
        where='printed p.542 (PDF p.4), Section IV-B and Table II',
        context='Section IV-B: "We tested the proposed methods on 16 UCI data sets [3]"; Table II names the minority class of '
                'each set. The easy and hard groups of Tables IV and V (AdaBoost\'s AUC above or below 0.95) sort the '
                'results after the run. The first pass\'s \'various sizes and imbalance levels\' is its own description; a '
                'search of the text layer for such wording (various, different sizes, degree of imbalance, chosen, selected) '
                'found none that gives a reason for the choice.',
        quotes=[(4, 'We tested the proposed methods on 16 UCI data sets [3].')]),
    ('k-means SMOTE', 'crit_type'): dict(
        stem='KMeansSMOTE-2018', pdf='Douzas, Bacao and Last, "Improving Imbalanced Learning Through a Heuristic Oversampling Method Based on K-Means and SMOTE", Information Sciences, 2018 (the corpus PDF is the accepted manuscript)',
        where='accepted manuscript p.13 (PDF p.14), Section 4.4',
        context='Section 4.4: the UCI sets were undersampled "to generate additional datasets with even higher imbalance '
                'ratios", a reason for the undersampled versions (a range of imbalance ratios). The first pass coded '
                '\'generic only\'; a search of the text layer found no \'widely used\' or \'commonly used\' for the data. The '
                'corpus PDF is the accepted manuscript, so its pages differ from the journal\'s.',
        quotes=[(14, 'In order to generate additional datasets with even higher imbalance ratios, each of the aforementioned datasets was randomly undersampled')]),
    ('RSMOTE', 'crit_type'): dict(
        stem='RSMOTE-2021', pdf='paper/Binary/RSMOTE A self-adaptive robust SMOTE for imbalanced problems with label noise.pdf',
        where='printed p.408 (PDF p.12), Section 4.3.2',
        context='Section 4.3.2: of the 27 UCI sets, 9 are intrinsically imbalanced and "the other 18 data sets are '
                'artificially imbalanced to obtain higher imbalanced ratios", a reason for the modified versions (a range of '
                'imbalance ratios). The sets themselves are introduced "to verify the effectiveness of the proposed RSMOTE".',
        quotes=[(12, 'the other 18 data sets are artificially imbalanced to obtain higher imbalanced ratios'),
                (12, 'To verify the effectiveness of the proposed RSMOTE, 27 real data sets from the UCI machine-learning repository')]),
    ('GLOS', 'crit_type'): dict(
        stem='GLOS-2023', pdf='paper/Multiclass/2023_GLOS_Global-local information based oversampling for multi-class imbalanced data.pdf',
        where='printed p.2079 (PDF p.9), Section 4.1 and Table 1; printed p.2083 (PDF p.13)',
        context='p.2083: Segment and Texture were chosen and modified "to examine the robustness of GLOS in different '
                'imbalanced situations", a reason for those two sets in an experiment of their own. The 21 sets of the main '
                'experiment are introduced on p.2079 ("21 multi-class data sets from the UCI repository and KEEL repository [38] '
                'are selected"); a search of the text layer found no \'widely used\' or \'commonly used\' for the data.',
        quotes=[(13, 'In order to examine the robustness of GLOS in different imbalanced situations, we selected Segment and Texture data sets and modified them to different imbalanced cases.'),
                (9, '21 multi-class data sets from the UCI repository and KEEL repository [38] are selected')]),
    ('GOIO', 'crit_type'): dict(
        stem='GOIO-2025', pdf='paper/Both/GOIO - Generative Oversampling Approach to Class Imbalance and Overlap of Tabular Data (IEEE TKDE 2025).pdf',
        where='printed p.6455 (PDF p.6), Section IV-A; printed p.6456 (PDF p.7)',
        context='p.6456: the five synthetic sets were generated "enabling precise control over dataset characteristics for '
                'clearer result interpretation", a reason for the synthetic sets (to control a property). The 18 real sets '
                '(Section IV-A, p.6455) are introduced as publicly available, without a reason.',
        quotes=[(7, 'We generated five synthetic datasets based on two multivariate Gaussian distributions following [50], enabling precise control over dataset characteristics for clearer result interpretation.'),
                (6, 'we employed 18 real-world tabular datasets and five artificial datasets to evaluate the performance of our model. All the real-world datasets used in our experiments are publicly available')]),
    ('DGOT', 'crit_type'): dict(
        flag="the AI's sentence comes from the ablation study, not the main experiment",
        stem='DGOT-2026', pdf='paper/Both/DGOT - Diffusion GAN-Based Oversampling for Imbalanced Tabular Data (IEEE TKDE 2026).pdf',
        where='printed p.989 (PDF p.7), Section IV-A "Dataset Selection"; printed p.994 (PDF p.12), ablation study',
        context='The sentence the AI relies on (p.994) belongs to the ablation study: the "four representative datasets" are '
                'those of Table IX, where DGOT is compared with its own variants. The 22 sets of the main experiment (Section '
                'IV-A, \'Dataset Selection\', p.989) are introduced as publicly available, without a reason, which is what the '
                'first pass coded.',
        quotes=[(12, 'We conducted experiments on four representative datasets, comprising two binary classification datasets and two multi-classification datasets, covering both low and high IR cases.'),
                (7, 'In our experiments, we employed 22 real-world tabular datasets to evaluate the performance of our model.')]),
    ('Loyalty-SMOTE', 'crit_type'): dict(
        stem='Loyalty-SMOTE-2026', pdf='paper/Both/Loyalty-SMOTE - Data Synthesis Algorithm for Effective Imbalanced Data Classification (Neural Networks 2026).pdf',
        where='p.7, Section 4.1 and Table 1; p.12, Section 4.4.5',
        context='Section 4.1: "this paper uses four groups of commonly used imbalanced datasets" (generic only). Table 1 describes '
                'group 5 as high-dimensional and large-scale sets, and Section 4.4.5 uses it "to evaluate the performance of '
                'the Loyalty-SMOTE algorithm on large-scale and high-dimensional datasets" (data that match what the method is '
                'for). Under the codebook\'s precedence an own reason for part of the data outranks \'generic only\'.',
        quotes=[(7, 'this paper uses four groups of commonly used imbalanced datasets'),
                (12, 'To evaluate the performance of the Loyalty-SMOTE algorithm on large-scale and high-dimensional datasets')]),
    ('Cluster-SMOTE', 'origin:Binarised'): dict(
        stem='Cluster-SMOTE-2006', pdf='paper/Binary/2006 Cluster-SMOTE - Cieslak, Chawla, Striegel.pdf',
        where='p.2 (PDF p.2)',
        context='The authors label each packet only as intrusive or not, instead of by its type of intrusion: "Rather than '
                'associating the type of intrusion with the packet, we merely label whether a packet was intrusive." A '
                'multiclass source becomes two classes, by the authors. The verified sheet records both entries as modified.',
        quotes=[(2, 'Rather than associating the type of intrusion with the packet, we merely label whether a packet was intrusive.')]),
    ('DSRBF / Static-SMOTE', 'origin:Binarised'): dict(
        stem='DSRBF-2011', pdf='Fernandez-Navarro, Hervas-Martinez and Gutierrez, "A dynamic over-sampling procedure based on sensitivity for multi-class problems", Pattern Recognition 44, 2011',
        where='printed p.1827 (PDF p.7); Table 3, printed p.1828 (PDF p.8)',
        context='CYTvsPOX keeps only the CYT and POX classes of the ten-class Yeast set, and ME2vsOther sets ME2 against all '
                'the other classes: two-class sets made by the authors. The verified sheet records both as modified.',
        quotes=[(7, 'The CYTvsPOX dataset is the Yeast dataset considering only patterns from CYT and POX classes, and the ME2vsOther is the Yeast dataset considering ME2 patterns vs the remaining patterns.')]),
    ('DLexiBoost', 'origin:Binarised'): dict(
        stem='DLexiBoost-2020', pdf='paper/Both/DLexiBoost - Boosting with Lexicographic Programming Addressing Class Imbalance without Cost Tuning (IEEE TKDE 2020).pdf',
        where='supplementary material p.4, Table 1',
        context='The 15 two-class sets of supplementary Table 1 are KEEL files such as ecoli0vs1, shuttle-C2vsC4, '
                'wineQuality-red8vs67 and poker8vs6; the verified sheet records them as repository-defined. Codebook: a '
                'two-class KEEL file counts as binarized (by the repository).',
        quotes=[(4, 'ecoli0vs1'), (4, 'shuttle-C2vsC4'), (4, 'wineQuality-red8vs67'), (4, 'poker8vs6')]),
    ('HDE', 'origin:Binarised'): dict(
        stem='HDE-2021', pdf='paper/Both/HDE - A Hybrid Data-Level Ensemble to Enable Learning from Highly Imbalanced Dataset (Information Sciences 2021).pdf',
        where='printed p.165 (PDF p.9), Section 4.1; Table 1, printed p.166 (PDF p.10)',
        context='28 of the 42 sets are KEEL two-class files (Table 1: for example glass016vs2, yeast2vs4, krvsk3vs11); the '
                'verified sheet records them as repository-defined. The other 14 (LibSVM) were undersampled by the authors.',
        quotes=[(10, 'glass016vs2'), (10, 'yeast2vs4'), (10, 'krvsk3vs11')]),
    ('FW-SMOTE', 'origin:Binarised'): dict(
        stem='FW-SMOTE-2022', pdf='paper/Both/FW-SMOTE - A Feature-Weighted Oversampling Approach for Imbalanced Classification (Pattern Recognition 2022).pdf',
        where='p.7, Table 1',
        context='27 of the 30 low-dimensional sets carry KEEL two-class names in Table 1 (for example ecoli-0-1 vs 5, '
                'yeast-0-5-6-7-9 vs 4). The paper says only that the 30 come from UCI and KEEL; the verified sheet marks the '
                '27 repository-defined by their names.',
        quotes=[(7, 'ecoli-0-1 vs 5'), (7, 'yeast-0-5-6-7-9 vs 4')]),
    ('Survey: Stop Oversampling', 'origin:Binarised'): dict(
        stem='StopOversampling-2022', pdf='Hassanat, Tarawneh, Altarawneh and Almuhaimeed, "Stop Oversampling for Class Imbalance Learning: A Critical Review", 2022',
        where='p.9, Table 2',
        context='Table 2 lists Yeast4, Yeast5 and Yeast6 with two classes each; the names are those of KEEL\'s two-class '
                'Yeast files, though the paper cites only where the data are available. The verified sheet marks them '
                'repository-defined by their names.',
        quotes=[(9, 'Yeast4 10 2 51 1433'), (9, 'Yeast5 10 2 44 1440'), (9, 'Yeast6 10 2 35 1449')]),
    ('OREM-M', 'origin:Binarised'): dict(
        flag='the two entries the AI relies on have 5 and 4 classes',
        stem='OREM-2023', pdf='paper/Multiclass/2023_OREM-M_Oversampling With Reliably Expanding Minority Class Regions for Imbalanced Data Learning.pdf',
        where='Table 2, printed p.6174 (PDF p.8); Table 6, printed p.6177 (PDF p.11)',
        context='The AI\'s reason is the verified sheet\'s two \'repository-defined\' entries, Vowel5 and Vowel4, but Table 6 '
                'gives them 5 and 4 classes (180/90/360/270/90 and 360/90/90/450, which add up to 990 in multiples of 90, as '
                'merged classes of the 11-class Vowel set would), so they are not two-class splits; the sheet\'s label came '
                'from a file-name rule. The paper does binarize in its two-class experiment (Table 2, for example Vehicle '
                'with its class van against the other classes), and the second pass\'s evidence is from that table, but the Data entries '
                'of OREM-M are the multiclass sets of Table 6 and a simulated set. Whether the count takes the whole paper '
                'or the OREM-M record decides the value.',
        quotes=[(11, 'Vowel5 180/90/360/270/90 5'), (11, 'Vowel4 360/90/90/450 4'), (8, "Vehicle 'van' other classes")]),
}
EFFECT_WORDS = {'reason': ('gives a reason for its choice of data', 'giving a reason'),
                'binar': ('has data binarized by anyone', 'binarized by anyone')}


def rd(p):
    return list(csv.DictReader(open(p, encoding='utf-8-sig')))


def norm_words(s):
    s = unicodedata.normalize('NFKC', s).replace('­', '')
    s = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', s)
    return re.findall(r'[a-z0-9]+', s.lower())


def lcs(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return prev[-1]


def check_quote(stem, pdf_page, text):
    """Share of the quote's words found in order on the PDF page (main text, or supp1 when the main has no such page)."""
    q = norm_words(text)
    best = 0.0
    for f in sorted(CORPUS.glob(stem + '__*.txt')):
        pages = f.read_text(encoding='utf-8', errors='ignore').split('\f')
        if pdf_page <= len(pages):
            best = max(best, lcs(q, norm_words(pages[pdf_page - 1])) / len(q))
    return best


def main():
    mat = rd(REPO / 'Data section/out/data_handling_matrix.csv')
    adj = rd(A / 'DATA_handling_adjudicated.csv')
    adj_by = {(r['paper'], r['field']): r for r in adj}
    summ = json.load(open(A / 'WP3_summary.json', encoding='utf-8'))['paper_level_after_adjudication']
    prior = rd(V / 'wp3/check_page/exports/smote25_wp3_check_2026-11-15.csv')
    checked = {(r['paper'], r['field']) for r in prior if r['form'] == 'Data handling'}

    # the two counts, from the first-pass codes and after the adjudication
    reason_rows = [r for r in mat if r['crit_type'] != 'n.a.']
    first_reason = {r['key']: r['crit_type'] in ('own reason', 'cites prior work') for r in reason_rows}
    after_reason = {r['key']: (adj_by[(r['key'], 'crit_type')]['adjudicated_value'] if (r['key'], 'crit_type') in adj_by
                               else r['crit_type']) in REASON for r in reason_rows}
    binar_rows = [r for r in mat if r['origin'] not in ('n.a.', '')]
    first_binar = {r['key']: 'Binarised' in r['origin'] for r in binar_rows}
    after_binar = {r['key']: (adj_by[(r['key'], 'origin:Binarised')]['adjudicated_value'] == 'yes'
                              if (r['key'], 'origin:Binarised') in adj_by else 'Binarised' in r['origin']) for r in binar_rows}
    assert sum(after_reason.values()) == summ['reason_given'] and len(reason_rows) == summ['papers_with_evaluation'], 'STOP: reason count'
    assert sum(after_binar.values()) == summ['binarised_by_anyone'], 'STOP: binarized count'
    flips = [(k, 'crit_type', 'reason') for k in first_reason if first_reason[k] != after_reason[k]]
    flips += [(k, 'origin:Binarised', 'binar') for k in first_binar if first_binar[k] != after_binar[k]]
    todo = [f for f in flips if (f[0], f[1]) not in checked]
    already = sorted(f'{k} ({fld})' for k, fld, g in flips if (k, fld) in checked)
    assert {(k, f) for k, f, g in todo} == set(CONTEXT), f'STOP: CONTEXT does not match the items found: {sorted(todo)}'

    mrow = {r['key']: r for r in mat}
    items = []
    for key, field, group in todo:
        a = adj_by[(key, field)]
        c = CONTEXT[(key, field)]
        m = mrow[key]
        if group == 'reason':
            first = f"{a['first_pass']}" + (f" (basis: {m['basis']})" if m['basis'] else '')
            first_note = m['crit_text']
            first_quote = a['first_pass_quote']
        else:
            first = 'no' + f" (the first pass's origin codes: {m['origin'].replace(';', ', ')})"
            first_note, first_quote = '', ''
        short = EFFECT_WORDS[group][1]
        counted = (after_reason if group == 'reason' else after_binar)[key]
        n_after = sum((after_reason if group == 'reason' else after_binar).values())
        if counted:
            effect = (f"With the AI's value the paper counts as {short}; with the first pass's value it would not, and the "
                      f"count would be {n_after - 1}")
        else:
            effect = (f"With the AI's value the paper does not count as {short}; with the first pass's value it would, and "
                      f"the count would be {n_after + 1}")
        items.append(dict(
            key=f'cnt_{group}_{key}'.replace(' ', '_'), group=group, form='Data handling', paper=key,
            item='the paper', field=field, pdf=c['pdf'], where=c['where'],
            question=('Reason given for the choice of data (D34)' if group == 'reason' else 'Data binarized by anyone (origin code Binarised)'),
            first=first, first_note=first_note, first_quote=first_quote,
            second=a['second_pass'], second_evidence=a['second_pass_evidence'],
            adjudicated=a['adjudicated_value'], note=a['adjudication_note'], decided_by=a['decided_by'],
            effect=effect + ' (count after the adjudication: ' + str(n_after) + ').', context=c['context'],
            flag=c.get('flag', '')))
    for i in items:
        i['id'] = 'c' + hashlib.sha256(i['key'].encode()).hexdigest()[:10]
    assert len({i['id'] for i in items}) == len(items), 'STOP: duplicate ids'

    if CORPUS:
        bad = []
        for (key, field), c in CONTEXT.items():
            for pg, q in c['quotes']:
                s = check_quote(c['stem'], pg, q)
                print(f'  quote check {key}: PDF p.{pg} {s:.2f}  {q[:60]}')
                if s < 0.9:
                    bad.append((key, pg, round(s, 2), q[:50]))
            for q in re.findall(r'"([^"]{15,})"', c['context']):
                if not any(q.lower() in qq.lower() for _, qq in c['quotes']):
                    bad.append((key, 'context quote not among the checked quotes', q[:50]))
        assert not bad, f'STOP: quotes not found: {bad}'

    n_reason = sum(i['group'] == 'reason' for i in items)
    n_binar = sum(i['group'] == 'binar' for i in items)
    meta = dict(
        title='SMOTE25 WP3 Count Check', built='2026-11-15', n=len(items),
        groups=dict(reason=n_reason, binar=n_binar),
        counts=dict(
            reason=dict(label='papers that give a reason for their choice of data', denominator=len(reason_rows),
                        first_pass=sum(first_reason.values()), after=sum(after_reason.values()),
                        base_others=sum(v for k, v in after_reason.items() if not any(k == i['paper'] and i['group'] == 'reason' for i in items)),
                        where='Table 5, row "Reason given for the choice of data"; Section 5.2 ("Six papers give no reason")'),
            binar=dict(label='papers whose data are binarized by anyone', denominator=len(binar_rows),
                       first_pass=sum(first_binar.values()), after=sum(after_binar.values()),
                       base_others=sum(v for k, v in after_binar.items() if not any(k == i['paper'] and i['group'] == 'binar' for i in items)),
                       checked_before=already, where='Table 5, row "Papers that binarize or convert classes"')),
        values=dict(reason=['own reason', 'cites prior work', 'generic only', 'not stated'], binar=['yes', 'no']),
        counts_as=dict(reason=['own reason', 'cites prior work', 'reason given'], binar=['yes']),
        sources=dict(first_pass='team repository, Data section/out/data_handling_matrix.csv',
                     adjudication='wp3/adjudication/DATA_handling_adjudicated.csv',
                     already_checked='wp3/check_page/exports/smote25_wp3_check_2026-11-15.csv'))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'records.json').write_text(json.dumps(dict(meta=meta, items=items), ensure_ascii=False, indent=0), encoding='utf-8')
    print(json.dumps(dict(n=meta['n'], groups=meta['groups'], counts=meta['counts']), indent=1))


if __name__ == '__main__':
    main()
