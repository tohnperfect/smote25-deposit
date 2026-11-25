# SMOM validation (WP6.8)

**Verdict: reproduced.** With the paper's Naive Bayes classifier (Weka NaiveBayes with supervised
discretization), this implementation gives an MG of **0.7848 on vehicle against the paper's 0.7849**
(Supp. Table S4, Supp. p. 8) and an MAUC of 0.9299 against 0.9299 (Supp. Table S6, Supp. p. 10). On
vowel5 the MG is 0.7781 against 0.7783. On vowel7 it is 0.7419 against 0.7188 (+0.023), but the
same protocol without any oversampling (NONE) is +0.046 above the paper there, so that gap lies in
the data or the classifier, not in SMOM (details below).

Reproduce: `python3 -I validate_smom.py` (about 2 minutes; writes `validation_results.json`; the
numbers are fixed by the seeds).

## 1. What was compared

The paper prints per-data-set scores of SMOM only in the supplement (Supp. Tables S3 to S20). Of its
27 data sets, three can be rebuilt exactly from files already on disk (keel-ds 0.2.5,
`src/kd/keel_ds/data/balanced/raw/`), with the class sizes of Table 1 (p. 334):

| Data set | Rows x features | Classes (Table 1) | Built from |
|:--|:--|:--|:--|
| vehicle | 846 x 18 | 199 / 429 / 218 | `vehicle.dat`: van / saab and opel / bus |
| vowel5 | 990 x 10 | 180 / 90 / 360 / 270 / 90 | `vowel.dat`, F0..F9: '0'&'1' / '2' / '3'&'4'&'5'&'6' / '7'&'8'&'9' / '10' |
| vowel7 | 990 x 10 | 90 / 180 / 90 / 180 / 90 / 180 / 180 | `vowel.dat`, F0..F9: '0' / '1'&'2' / '3' / '4'&'5' / '6' / '7'&'8' / '9'&'10' |

Of the paper's four classifiers (C4.5, AdaBoost.M1 of C4.5, MLP, NB, all in Weka, p. 335), only NB
with supervised discretization is a fully specified algorithm that can be re-implemented exactly
without running Weka. `validate_smom.py` re-implements Weka 3.8 `NaiveBayes -D`: Fayyad and Irani's
MDL discretization as in `weka.filters.supervised.attribute.Discretize` with its default options,
fitted on each training fold, and Laplace-corrected counts for the class prior and every attribute.
Check: on iris it returns Weka's well-known cut points (5.55, 6.15; 2.95, 3.35; 2.45, 4.75; 0.8, 1.75).

### Which supplement column is NB

Supp. Tables S4, S6, S8 and S10 (Supp. pp. 8, 10, 12, 14) head their two column blocks "NB" (left,
block A) and "MLP" (right, block B). The main paper's Table 2 (p. 335) and Supp. Table S13 (Supp.
p. 17) print the same numbers under the opposite labels: the averages of block A (SMOM Avg-MG 0.5496,
NONE 0.4052) are the "MLP" column of Table 2 (0.550, 0.405) and of S13, those of block B (0.4351,
0.372) the "NB" column. The NB baseline here settles it: without oversampling it gives MG 0.7802 on
vehicle (block A 0.9719, block B 0.7768), 0.6958 on vowel5 (0.9512 against 0.7105) and 0.6897 on vowel7
(0.8343 against 0.6435). **Block B is NB**; the headers of S4, S6, S8 and S10 are swapped. All paper
values below are block B.

## 2. Protocol

| Item | Paper (page) | Here |
|:--|:--|:--|
| Folds | "average of 10 independent runs with stratified 10-fold cross validation" (p. 335) | 10 runs of scikit-learn `StratifiedKFold(10, shuffle=True, random_state=run)`, runs 1 to 10 |
| Oversampling target | "All classes are oversampled until they contain as many instances as the largest one" (p. 335) | same (`sampling_strategy="auto"`) |
| SMOM settings | k1 = 12, k2 = 8, rTh = 5/8, nTh = 10, w1 = 0.2, w2 = 1/2, r1 = 1/3, r2 = 0.2 (p. 335) | defaults of `smom.SMOM` |
| Distance | standardized Euclidean (p. 335) | SMOM `metric="seuclidean"` (standard deviations of the training fold) |
| Classifier | Weka NB, "NB employs supervised discretization" (p. 335) | Weka 3.8 `NaiveBayes -D` re-implemented, default options |
| Measures | MG, MAUC (Hand and Till), recall and precision of the smallest class (pp. 334-335) | same, on each test fold, averaged over the 100 folds |
| Controls | NONE and SMOTE (k = 5) are in the same tables | NONE; SMOTE of imbalanced-learn 0.14.2 (k = 5) on the standardized training fold |

Not stated by the paper, and the reading used:

1. Fold assignment and seeds (Weka's own stratification): scikit-learn folds, seeds 1 to 10.
2. Whether MG is averaged over the test folds or computed from the pooled predictions of a run:
   averaged over folds (main reading); the pooled reading is also reported (`MG_pooled_per_run`).
3. That resampling touches the training folds only: assumed.
4. NB options beyond "supervised discretization": Weka defaults (Fayyad and Irani MDL,
   `useBetterEncoding` false). Side check with `useBetterEncoding` true below.
5. Weka version: not given; Weka 3.8 behavior reproduced.
6. vowel features: Table 1 gives 10 features, so KEEL's F0..F9 (TT, SpeakerNumber and Sex dropped).
7. vehicle classes: Table 1 names them 'DH'/'SL'/'NO', which are not vehicle classes; the sizes
   199/429/218 fit van / saab and opel / bus, which is what was used.
8. Standard deviations of the standardized distance: training fold, ddof = 1 (inside SMOM).
9. Recall and precision of "the smallest minority class": defined only for vehicle (van, 199); in
   vowel5 two classes and in vowel7 three classes tie for smallest, so these are not compared there.

## 3. Results (NB, block B)

SMOM, the number to reproduce:

| Data set | Measure | Paper (table, page) | Here | Difference |
|:--|:--|--:|--:|--:|
| vehicle | MG | 0.7849 (S4, Supp. p. 8) | 0.7848 | -0.0001 |
| vehicle | MAUC | 0.9299 (S6, Supp. p. 10) | 0.9299 | 0.0000 |
| vehicle | recall of van | 0.9608 (S8, Supp. p. 12) | 0.9594 | -0.0014 |
| vehicle | precision of van | 0.6246 (S10, Supp. p. 14) | 0.6254 | +0.0008 |
| vowel5 | MG | 0.7783 (S4, Supp. p. 8) | 0.7781 | -0.0002 |
| vowel5 | MAUC | 0.9638 (S6, Supp. p. 10) | 0.9630 | -0.0008 |
| vowel7 | MG | 0.7188 (S4, Supp. p. 8) | 0.7419 | +0.0231 |
| vowel7 | MAUC | 0.9629 (S6, Supp. p. 10) | 0.9612 | -0.0017 |

Controls under the same protocol (MG; same tables):

| Data set | NONE paper / here / diff | SMOTE paper / here / diff |
|:--|:--|:--|
| vehicle | 0.7768 / 0.7802 / +0.0034 | 0.7832 / 0.7882 / +0.0050 |
| vowel5 | 0.7105 / 0.6958 / -0.0147 | 0.7736 / 0.7833 / +0.0097 |
| vowel7 | 0.6435 / 0.6897 / +0.0462 | 0.7170 / 0.7402 / +0.0232 |

Noise level: the standard deviation over the 10 runs of a run's MG is 0.005 (vehicle), 0.012
(vowel5) and 0.010 (vowel7) for SMOM, so a 10-run average carries about 0.002 to 0.004 of chance
variation, the paper's as well as this one.

Other readings tried (all in `validation_results.json` or reproducible with the command given):

| Reading | vehicle MG | vowel5 MG | vowel7 MG |
|:--|--:|--:|--:|
| Paper (S4, block B) | 0.7849 | 0.7783 | 0.7188 |
| Used: MG per test fold, soft core by Definition 1 | 0.7848 | 0.7781 | 0.7419 |
| MG from the pooled predictions of each run | 0.7868 | 0.7848 | 0.7504 |
| Soft core by the literal Alg. 2 line 5, `soft_core_rule="round"` | 0.7851 | 0.7840 | 0.7446 |
| NONE with Weka `useBetterEncoding` true (`--methods NONE --mdl-encoding better --out -`) | 0.7826 (NONE) | 0.6966 (NONE) | 0.6899 (NONE) |

The per-fold reading and Definition 1 match the printed values best (vowel5: 0.7781 against 0.7840
for the "round" reading). The encoding switch does not move the vowel7 baseline.

## 4. What this shows and what it does not

* On vehicle and vowel5 the implementation lands on the paper's SMOM values to within 0.001 in MG
  and MAUC, well inside the run-to-run noise, under a protocol whose baseline (NONE) and control
  (SMOTE) also land within 0.015 of the paper.
* On vowel7 every method is above the paper (NONE +0.046, SMOTE +0.023, SMOM +0.023), with no
  oversampling involved in the NONE case; the cause is in the data or the classifier and is not
  found. Table 1's vowel7 row is itself inconsistent: Eq. (3) gives IR 12.00 for the printed sizes
  90/180/90/180/90/180/180, not the printed 15.00, and no grouping of the eleven 90-instance vowel
  classes into seven groups gives 15 (the possible values are 12, 17, 20, 21 and 24), while the
  printed IR of vowel5 (13.83) and vehicle (2.22) match their sizes. So the paper's vowel7 may not be
  the data set rebuilt here. Weka's encoding switch was ruled out.
* The comparison does not separate SMOM from SMOTE: in the paper SMOM beats SMOTE by 0.0017,
  0.0047 and 0.0018 MG on vehicle, vowel5 and vowel7; here the differences are -0.0034, -0.0053 and
  +0.0017, all within the noise. So the validation shows that this SMOM performs where the
  authors' SMOM performs on these data, not that each internal step matches the authors' code. The
  steps themselves are checked against the paper's text by `test_smom.py` (Eq. 2 values, NBDOS
  outstanding and trapped sets, Step 6.1 self direction, box-shaped placement of Eq. 1).
* Not attempted: C4.5, AdaBoost.M1 and MLP (Weka's J48 and MultilayerPerceptron cannot be matched
  exactly without running Weka; scikit-learn's CART is a different algorithm). The paper has no
  two-class experiment, so nothing here validates SMOM on the rerun's two-class tasks beyond the
  unit tests.
