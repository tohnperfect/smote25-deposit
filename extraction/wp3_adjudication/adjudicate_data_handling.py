#!/usr/bin/env python3
"""WP3, AI adjudication of the 109 data-handling disagreements (D31), with D34 (own reason and cites prior work merged
into "reason given", against none; "generic only" counts as none, as Section 5.2 counts it).

Sources: each pass's quote (data/wp3_blind/DATA_handling_disagreements_for_adjudication.csv), the paper's text
(corpus/txt) where the quotes do not settle it, and, for the origin labels, the verified entry-level sheet of the Data
extraction (team repository, Data section/out/full_datasets.csv and modified_operations_audit.csv): Generated follows
the papers' synthetic entries (the definition behind the decided count of Table 5), Undersampled and Noise-injected the
operations recorded per modified entry; Binarised counts repository-defined two-class splits (codebook). Each decision
below carries its reason. Writes wp3/adjudication/DATA_handling_adjudicated.csv.
Usage: python3 -I wp3/adjudication/adjudicate_data_handling.py DRAFT_DIR
"""
import csv
import sys
from collections import Counter
from pathlib import Path

R = Path(sys.argv[1])
SRC = R / 'data/wp3_blind/DATA_handling_disagreements_for_adjudication.csv'
OUT = R / 'wp3/adjudication/DATA_handling_adjudicated.csv'
BY = 'AI adjudication (Claude Opus 5.5, 12 Nov 2026)'
REASON = {'own reason', 'cites prior work'}

# (paper, field) -> (adjudication, value, note)
D = {
    # crit_type, where D34 does not settle it
    ('SMOTEBoost', 'crit_type'): ('second', 'not stated', 'p.112 introduces the four data sets with no reason for the choice; the satimage binarisation follows [24], which is not a reason for choosing the data'),
    ('EasyEnsemble / BalanceCascade', 'crit_type'): ('second', 'not stated', '"We tested the proposed methods on 16 UCI data sets [3]" with no reason (Sec. IV-B)'),
    ('Borderline-SMOTE', 'crit_type'): ('second', 'own reason', 'p.883: the simulated Circle set is chosen so that the methods "can be easily understood" (analytic)'),
    ('k-means SMOTE', 'crit_type'): ('second', 'own reason', 'p.13: data sets undersampled "to generate additional datasets with even higher imbalance ratios" (diversity)'),
    ('RSMOTE', 'crit_type'): ('second', 'own reason', 'p.408: 18 sets artificially imbalanced "to obtain higher imbalanced ratios" (diversity)'),
    ('GLOS', 'crit_type'): ('second', 'own reason', 'p.2083: Segment and Texture chosen and modified "to examine the robustness of GLOS in different imbalanced situations"'),
    ('GOIO', 'crit_type'): ('second', 'own reason', 'p.6456: synthetic sets generated for "precise control over dataset characteristics" (analytic)'),
    ('DGOT', 'crit_type'): ('second', 'own reason', 'p.994: four sets chosen to cover binary and multiclass, low and high IR (diversity)'),
    ('Loyalty-SMOTE', 'crit_type'): ('second', 'own reason', 'p.12: group 5 chosen to test large-scale and high-dimensional data (method target)'),
    # minority_rule
    ('SMOTEBoost', 'minority_rule'): ('second', 'explicit target listed', 'p.112 names the KDD minority classes U2R and R2L and, for satimage, the smallest class'),
    ('Cluster-SMOTE', 'minority_rule'): ('first', 'n.a.', 'both data sets are built as two-class problems (alert or not); codebook: n.a. when all data are two-class'),
    ('COG-OS', 'minority_rule'): ('second', 'induced by authors', 'p.818: the small class of each two-class set is sampled down to make it rare'),
    ('RUSBoost', 'minority_rule'): ('first', 'explicit target listed', 'Table I names the positive class in each data set name (for example SolarFlareF, Pendigits5, Glass3)'),
    ('SPIDER2', 'minority_rule'): ('second', 'induced by authors', 'p.161: the minority class shapes of the artificial data are set by the authors (low confidence: the UCI sets are not described)'),
    ('DSRBF / Static-SMOTE', 'minority_rule'): ('first', 'explicit target listed', 'Table 3 and p.1827 name the class pairs (CYTvsPOX, ME2vsOther)'),
    ('INOS', 'minority_rule'): ('second', 'induced by authors', 'p.2816: one class taken as positive and its training size set by the authors'),
    ('A-SUWO', 'minority_rule'): ('second', 'explicit target listed', 'Table 3.1 (p.35) names the minority class of each set'),
    ('AMDO', 'minority_rule'): ('both wrong', 'mean-size or IR threshold', 'p.3 and p.5: every class but the single majority is a minority, a relative rule; coded as the threshold rule, as for NROMM and SOS'),
    ('OBU', 'minority_rule'): ('second', 'repository-defined', 'two-class UCI and KEEL files, no rule of the paper\'s own'),
    ('CTGAN / TVAE', 'minority_rule'): ('second', 'not defined', 'multiclass sets (for example covertype) used with their native classes, no minority defined'),
    ('G-SMOTE', 'minority_rule'): ('second', 'repository-defined', 'the class splits are given by the data set names (for example PAGE BLOCKS 1 3)'),
    ('AB-SMOTE', 'minority_rule'): ('second', 'repository-defined', 'KEEL splits (Abalone9-18, Flare-F, winequality-red-4) and native two-class Haberman'),
    ('DLexiBoost', 'minority_rule'): ('second', 'repository-defined', 'supp. Table 1 uses KEEL splits (ecoli0vs1, shuttle-C2vsC4)'),
    ('NBU', 'minority_rule'): ('first', 'explicit target listed', 'Experiment III names the minority (MNIST digit 3, the positive breast cancer cases); the KEEL splits are repository-defined'),
    ('HDE', 'minority_rule'): ('second', 'repository-defined', 'Table 1 (p.166): KEEL splits such as yeast1289vs7'),
    ('CBHSID', 'minority_rule'): ('second', 'mean-size or IR threshold', 'p.118642: a class below a size threshold is a minority'),
    ('SOS', 'minority_rule'): ('second', 'mean-size or IR threshold', 'p.767: every class smaller than the largest is a minor class'),
    ('SVDD-WSMOTE', 'minority_rule'): ('second', 'explicit target listed', 'Table 2 (p.35) names the class kept against the others (for example v-good)'),
    ('GLOS', 'minority_rule'): ('second', 'mean-size or IR threshold', 'p.2074: a class with theta below the threshold DID is a minority'),
    ('NROMM', 'minority_rule'): ('second', 'mean-size or IR threshold', 'p.6: for multiclass data the largest class is the majority and the rest are minority classes'),
    ('MC-MBRC', 'minority_rule'): ('first', 'mean-size or IR threshold', 'p.6: classes sorted by size, each class treated as minority against the larger ones, a relative rule'),
    ('GDHS', 'minority_rule'): ('second', 'mean-size or IR threshold', 'p.3: a class smaller than the mean size m is a minority'),
    ('MLOS', 'minority_rule'): ('first', 'repository-defined', 'KEEL and PROMISE two-class files (Table, p.9); the second pass gives no evidence'),
    ('Loyalty-SMOTE', 'minority_rule'): ('second', 'smallest class vs rest', 'p.12: for multiclass sets the class with the fewest instances is the minority'),
    # origin labels (first pass / second pass yes or no)
    ('Cluster-SMOTE', 'origin:Natural'): ('second', 'no', 'verified sheet: both entries built by the authors (label construction); none used as distributed'),
    ('GAMO', 'origin:Natural'): ('second', 'yes', 'verified sheet: four entries used as distributed'),
    ('HDE', 'origin:Natural'): ('second', 'no', 'verified sheet: repository splits and undersampled entries only'),
    ('FW-SMOTE', 'origin:Natural'): ('second', 'no', 'verified sheet: repository-defined splits and entries whose origin is not stated'),
    ('Survey: Stop Oversampling', 'origin:Natural'): ('second', 'no', 'verified sheet: four KEEL splits (Yeast4 to Yeast6)'),
    ('Cluster-SMOTE', 'origin:Binarised'): ('second', 'yes', 'p.2: intrusion types reduced to a two-class problem'),
    ('DSRBF / Static-SMOTE', 'origin:Binarised'): ('second', 'yes', 'p.1827: CYTvsPOX and ME2vsOther built from Yeast'),
    ('GAMO', 'origin:Binarised'): ('first', 'no', 'class subsets stay multiclass; the second pass\'s quote is about imbalance created by sampling'),
    ('AB-SMOTE', 'origin:Binarised'): ('second', 'yes', 'KEEL split Abalone9-18 (repository-binarised, codebook)'),
    ('DLexiBoost', 'origin:Binarised'): ('second', 'yes', 'KEEL splits in supp. Table 1'),
    ('HDE', 'origin:Binarised'): ('second', 'yes', 'KEEL splits in Table 1'),
    ('CBHSID', 'origin:Binarised'): ('second', 'yes', 'KEEL splits (Yeast1, Glass6, Yeast6) in Table 1'),
    ('FW-SMOTE', 'origin:Binarised'): ('second', 'yes', 'KEEL splits (ecoli-0-1 vs 5, yeast-0-5-6-7-9 vs 4) in Table 1'),
    ('Survey: Stop Oversampling', 'origin:Binarised'): ('second', 'yes', 'KEEL splits Yeast4 to Yeast6'),
    ('OREM-M', 'origin:Binarised'): ('second', 'yes', 'verified sheet: two repository-defined split entries'),
    ('Loyalty-SMOTE', 'origin:Binarised'): ('second', 'yes', 'KEEL splits (ecoli-0-1-3-7_vs_2-6) in group 1'),
    ('SMOTE-ENN / SMOTE-Tomek', 'origin:Class-merged'): ('first', 'no', 'one-vs-rest binarisation (p.24), which the codebook counts as Binarised, not merging'),
    ('LS', 'origin:Class-merged'): ('second', 'yes', 'Letter: all vowels against the consonants (class grouping)'),
    ('RAMOBoost', 'origin:Class-merged'): ('first', 'no', 'Table II maps one class against the rest'),
    ('MWMOTE', 'origin:Class-merged'): ('second', 'yes', 'Table 5 (p.416) groups several original classes into the minority for some sets'),
    ('SMOTE-IPF', 'origin:Class-merged'): ('first', 'yes', 'p.191: "the joint of one or more classes as positive"'),
    ('DLexiBoost', 'origin:Class-merged'): ('first', 'no', 'repository splits such as wineQuality-red8vs67 count as Binarised (codebook)'),
    ('NROMM', 'origin:Class-merged'): ('second', 'no', 'multiclass sets used with their native classes; binary sets are KEEL splits'),
    ('OSS', 'origin:Class-resized'): ('first', 'no', 'verified sheet: one-vs-rest and minority undersampling only'),
    ('SHRINK', 'origin:Class-resized'): ('first', 'no', 'the quote is about the class structure of the oil-spill data, not class sizes'),
    ('SMOTEBoost', 'origin:Class-resized'): ('second', 'yes', 'p.112: KDD Cup-99 majority classes subsampled to reduce the size'),
    ('ROS (Buda)', 'origin:Class-resized'): ('second', 'yes', 'p.252: each class subsampled to at most 5,000 examples'),
    ('GDO', 'origin:Class-resized'): ('first', 'no', 'the quote is about binarisation (smallest class against the rest)'),
    ('SVDD-WSMOTE', 'origin:Class-resized'): ('second', 'yes', 'verified sheet: imbalance changed on 11 entries without removing minority examples'),
    ('SMOTEBoost', 'origin:Undersampled'): ('second', 'no', 'p.112: only majority classes were sampled; no minority examples removed'),
    ('ADASYN', 'origin:Undersampled'): ('second', 'no', 'verified sheet: class structure and feature changes only'),
    ('MBS', 'origin:Undersampled'): ('first', 'no', 'Table 2 lists native class sizes; no removal described'),
    ('NBU', 'origin:Undersampled'): ('second', 'yes', 'verified sheet: two entries with minority undersampling (Experiment III)'),
    ('KNNOR', 'origin:Undersampled'): ('first', 'no', 'the quote is about repository splits of multiclass sets'),
    ('SVDD-WSMOTE', 'origin:Undersampled'): ('first', 'no', 'verified sheet: no minority removal recorded'),
    ('Survey: Stop Oversampling', 'origin:Undersampled'): ('second', 'no', 'majority examples hidden for the evaluation; no minority removed'),
    ('RAMOBoost', 'origin:Noise-injected'): ('second', 'yes', 'verified sheet: label and attribute noise injected on two entries'),
    ('SPIDER2', 'origin:Noise-injected'): ('first', 'no', 'the borderline ratio is a property of the generated data (Generated), not noise added to data'),
    ('RSMOTE', 'origin:Noise-injected'): ('second', 'yes', 'label noise added to the training set (Sec. 4.3.2)'),
    ('KNNOR', 'origin:Noise-injected'): ('first', 'no', 'no noise injection described'),
    ('INOS', 'origin:Induced profile'): ('second', 'yes', 'p.2816: balanced UCR sets made imbalanced by the authors\' apportions'),
    ('GLOS', 'origin:Induced profile'): ('second', 'yes', 'p.2079 and p.2083: class sizes adjusted, Segment and Texture made imbalanced (not in the verified sheet as modified: see the report)'),
}
GENERATED_SHEET = {'COG-OS': 'yes', 'ADASYN': 'yes', 'RAMOBoost': 'no', 'INOS': 'no', 'RBBoost / Random Balance': 'yes',
                   'CGMOS': 'no', 'MDO': 'yes', 'GAMO': 'no', 'MBS': 'no', 'MC-CCR': 'no', 'RSMOTE': 'yes', 'GDO': 'yes',
                   'KNNOR': 'no', 'NROMM': 'yes', 'OREM-M': 'yes', 'GMMSampling': 'yes', 'CISO': 'no', 'MLOS': 'yes'}

rows = list(csv.DictReader(open(SRC, encoding='utf-8')))
out = []
for r in rows:
    key = (r['paper'], r['field'])
    if key in D:
        adj, val, note = D[key]
    elif r['field'] == 'crit_type':
        a, b = r['first_pass'] in REASON, r['second_pass'] in REASON
        if a != b:
            sys.exit(f'crit_type not settled by D34: {key}')
        adj, val, note = 'both', 'reason given' if a else 'none', 'D34: both passes find ' + ('a reason (own or cited)' if a else 'no reason')
    elif r['field'] == 'origin:Generated':
        val = GENERATED_SHEET[r['paper']]
        adj = 'first' if r['first_pass'] == val else 'second'
        note = 'verified sheet: ' + ('the paper has synthetic entries' if val == 'yes' else 'no synthetic entry') + ' (the definition of the Table 5 count)'
    else:
        sys.exit(f'no decision for {key}')
    out.append({**r, 'adjudication': adj, 'adjudicated_value': val, 'adjudication_note': note, 'decided_by': BY})
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print(len(out), dict(Counter(o['adjudication'] for o in out)), dict(Counter(o['field'].split(':')[0] for o in out)))
