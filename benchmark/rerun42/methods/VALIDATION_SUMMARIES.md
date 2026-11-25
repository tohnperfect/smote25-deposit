---
title: "SMOTE25: the five re-implementations of the rerun, one page each"
subtitle: "For the team lead's reading (decision D40, 12 November 2026). Prepared by a Claude session from VALIDATION.md and NOTES.md of each method; nothing here is new evidence."
---

# How to read these pages

Each page gives the number the method's paper prints, the number our implementation gives under the paper's
protocol, the verdict fixed before the comparison, the choices our implementation had to make, what the rerun
behind Table 17 used, and two or three things to look at in the paper's PDF. The details are in
`benchmark/rerun42/methods/<method>/VALIDATION.md` and `NOTES.md`. All five implementations are AI work (one Claude
Opus 5.5 session each, 11 November 2026); their tests pass. The rerun's results are the medians of Tables S13
and S14 of the online appendix (Section S7; Table S11 lists the validations): difference from SMOTE over 30 families of tasks, random forest (RF)
and gradient boosting (GB); for the Brier score a positive value means lower, that is better.

When you have read a page, tick it and add any question; M1 moves to fixed once all five are ticked (D40).

\newpage

# SMOM (Zhu, Lin and Liu, 2017, Pattern Recognition 72)

**What it does.** A multiclass oversampler: each minority class is oversampled from its own instances, with a
selection weight per neighbor direction that lowers the chance of generating into other classes (clusters found
by NBDOS, weights from Eq. 2).

| | Paper | Ours | Difference |
|:----------------------------|-----------:|-----------:|----------:|
| vehicle, MG, Weka NB with supervised discretization, 10 x 10-fold CV (Supp. Table S4) | 0.7849 | 0.7848 | -0.0001 |
| vehicle, MAUC (Supp. Table S6) | 0.9299 | 0.9299 | 0.0000 |
| vowel5, MG (Supp. Table S4) | 0.7783 | 0.7781 | -0.0002 |
| vowel7, MG (Supp. Table S4) | 0.7188 | 0.7419 | +0.0231 |

**Verdict: reproduced** on vehicle and vowel5, within the run-to-run noise (0.002 to 0.004). On vowel7 every
method is above the paper, NONE by 0.046 with no oversampling at all, so the gap lies in the data or the classifier;
the paper's own vowel7 row is inconsistent (its printed imbalance ratio does not fit its class sizes).

**Choices our implementation made** (15, each marked `CHOICE:` in `smom.py`): the entropy of Eq. 2 is read with
the minus sign the paper omits; Definition 1 is used for soft cores (the Alg. 2 line 5 reading with `round` gives
0.7851 on vehicle); the remainder of Step 7 goes to a random subset of the class.

**In the rerun:** defaults (k1 = 12, k2 = 8 and the other settings of p. 335), every class balanced. RF: ROC-AUC
.000, PR-AUC .000, G-mean +.001, Brier -.001 (higher). GB: .000, .000, +.002, .000. Meets C1. The rerun is two-class,
so it does not test SMOM's multiclass behavior.

**Look at in the PDF:** Eq. 2 and the missing minus sign (p. 332); the swapped "NB" and "MLP" headers of Supp.
Tables S4, S6, S8 and S10 (block B is NB, as the main paper's Table 2 shows); Table 1's class descriptions.

Read: [ ]  Questions:

\newpage

# AB-SMOTE (Al Majzoub and Elgedawy, 2020, IJMLC 10(1))

**What it does.** A Borderline-SMOTE variant: it generates one synthetic point per borderline minority instance,
with the partner chosen among the borderline instances only.

| | Paper | Ours | Difference |
|:----------------------------|-----------:|-----------:|----------:|
| Abalone9-18, J48, 5-fold CV, setting 4.1 (Table IV, p. 34): recall / F of the minority | 0.439 / 0.529 | 0.439 / 0.529 | 0.000 (exact replay) |
| Same, settings 4.0, 4.2, 4.3 | 0.427 / 0.493; 0.432 / 0.519; 0.494 / 0.559 | within the spread of 40 seeds (4.3 in the upper tail) | |
| Generated rows on four data sets (Tables IV, VI, IX, X) | 8 counts | 7 of 8 exact | |

**Verdict: reproduced**, but under the reading that the authors' runs imply (the instance counts as one of its own
neighbors, integer M/2), not the noise rule the text states: with the text's rule the paper's counts of generated
rows are not reproduced (18 and 22 instead of 40 and 39 on Abalone9-18). The paper's numbers also put synthetic rows
in the test folds (oversampling before the cross-validation), so they are optimistic.

**Choices our implementation made:** the text's borderline rule is the default (`borderline_rule="text"`), the
authors' reading is an option; one gap per new point (`gap="scalar"`); Euclidean distance on the features as given
(the authors used Weka's distances with VDM for nominal attributes).

**In the rerun:** defaults (M = 5, k = 5, 100%, the text's rule), so it adds one point per borderline minority
instance, fewer than SMOTE's balancing. RF: ROC-AUC .000, PR-AUC .000, G-mean -.040, Brier +.005 (lower). GB: .000,
.000, -.026, +.003; Bayesian probability 0.26 that it is worse than SMOTE in PR-AUC by more than 0.01. Meets C1.

**Look at in the PDF:** the noise rule in the text against Fig. 4 and Fig. 6 (p. 33); Table IV (p. 34), rows
4.0 to 4.3 and the Gen counts; whether the paper says where the oversampling happens relative to the folds.

Read: [ ]  Questions:

\newpage

# FW-SMOTE (Maldonado, Vairetti, Fernández and Herrera, 2022, Pattern Recognition 124)

**What it does.** SMOTE with a feature-weighted distance: features are ranked (Fisher score, mutual information,
eigenvector centrality or correlation), weighted by an OWA quantifier, and neighbors are found with a weighted
Minkowski distance on the r most relevant features.

| | Paper | Ours | Difference |
|:----------------------------|-----------:|-----------:|----------:|
| yeast3, k-NN, AUC = (TPR + TNR)/2 x 100, 10-fold CV (Supp. Table A.1, p. 29), tuned inside the training folds as stated | 90.3 | 89.5 (five runs: 88.8 to 90.5) | -0.8 |
| Same, configuration picked on the test folds | 90.3 | 90.4 | +0.1 |
| SMOTE on the same protocol | 88.4 | 89.5 | +1.1 |

**Verdict: close** (within 2 points, the scale fixed before the comparison). The paper's gain over SMOTE (1.9
points) is not reproduced under the stated protocol (0.0); it reappears in part (0.9) only when the configuration is
chosen on the test folds, which matches the paper's numbers for all three classifiers to within 0.2.

**Choices our implementation made** (15, in `NOTES.md`, section 4): the weights of Eqs. 10 to 12 are normalized to
sum to 1 (as printed they do not, and Eq. 11 is negative); p = infinity is read as the weighted maximum; Eq. 6 is
used as printed (no square root); N = 1 is the default amount (the paper picks N on test data). The authors' 2019
Matlab code departs from the paper in five ways; it changes results by less than one point.

**In the rerun:** defaults (Fisher ranking, r = n/2, p = infinity, alpha = 0.4, N = 1), so it adds fewer points
than SMOTE. RF: ROC-AUC .000, PR-AUC .000, G-mean -.021, Brier +.005 (lower). GB: .000, .000, -.020, +.002. Meets C1.

**Look at in the PDF:** Eq. 6 and Eqs. 10 to 12 (p. 5); how "tuned within the training set" and the choice of N
on test data are described (pp. 7 and 8); whether AUC is computed from scores or labels (p. 7).

Read: [ ]  Questions:

\newpage

# RSMOTE (Chen, Xia, Chen, Wang and Wang, 2021, Information Sciences 553)

**What it does.** A SMOTE variant for label noise: minority points whose neighbors are all majority are treated as
noise and left out of the seeds; the remaining seeds are split by relative density into two clusters, and points
are generated within each cluster in proportion to its density.

| | Paper | Ours | Difference |
|:----------------------------|-----------:|-----------:|----------:|
| pima, AUC averaged over five classifiers and five repetitions, c = 0 (Table 3, p. 410) | 0.886 | 0.781 | -0.105 |
| pima, SMOTE on the same protocol | 0.790 | 0.778 | -0.012 |
| pima, no resampling on the same protocol | 0.797 | 0.780 | -0.017 |
| RSMOTE minus SMOTE, AUC, on the five data sets that could be rebuilt | +0.015 to +0.164 | -0.001 to +0.005 | |

**Verdict: not reproduced.** The baselines match the paper on pima (within 0.02 on all five measures), so the
protocol fits; RSMOTE does not, under any reading of the unstated details (best 0.796). Leaking the test data into
the oversampling lifts SMOTE as much as RSMOTE and does not explain the gap. The authors' published file stops with
an error or returns all-zero rows in the settings of the paper's experiments, so it is not the code behind the tables.

**Choices our implementation made** (16, in `NOTES.md`, section 2): the "noise" points are left out of the seeds
but stay in the training data (as Algorithm 1 and the authors' file do; this answers decision-sheet item A10:
RSMOTE keeps all data); 2-means is the exact one-dimensional optimum; k = 5 by default (the paper tunes k).

**In the rerun:** defaults (k = 5, classes balanced). RF: ROC-AUC .000, PR-AUC .000, G-mean -.008, Brier +.001
(lower). GB: .000, .000, -.003, .000. Meets C1; Table 17 states that it does not reproduce its paper (D22).

**Look at in the PDF:** the weight (k - m)/(k + 1) in Step 3 and Alg. 1 line 19 (pp. 402 and 403); the 75/25 split
stated on p. 408 against Table 3's recall values, which fit a 20% test part; Table 3 itself (p. 410).

Read: [ ]  Questions:

\newpage

# CGMOS (Zhang, Ma, Gan, Jiang and Agam, 2016, CIKM)

**What it does.** SMOTE with seeds chosen by "certainty": a seed's probability is the relative gain in the
certainty of a kernel-density Bayes classifier that adding it brings (Eq. 6).

| | Paper | Ours | Difference |
|:----------------------------|-----------:|-----------:|----------:|
| Haberman, AUC averaged over six classifiers, 10 x 10-fold CV, tuned (Table 3, p. 1629) | 0.651 | 0.688 | +0.037 |
| Four other readings of the unstated details | 0.651 | 0.660 to 0.671 | +0.009 to +0.020 |
| CGMOS minus SMOTE, paired over the same folds | +0.051 | -0.003 to +0.001 | |

**Verdict: not reproduced.** The CGMOS value itself is near the paper's in some readings, but so are SMOTE and the
original data, which the paper has lower; no reading reproduces the paper's ordering. The cause is structural: with
Eq. 6 as printed, the seed probabilities differ from SMOTE's uniform ones by less than 0.1% (total variation; at most
0.0025 on five data sets), and 99.6% of the synthetic rows equal those of a uniform-seed run. No protocol can make
the two differ by 0.05 AUC.

**Choices our implementation made** (in `NOTES.md`, section 2): Eq. 3 without a 1/h^m factor (as printed); the
bandwidths of Eq. 4 from the q nearest neighbors in the same class; sigma = 1, q = 5, k = 5 by default.

**In the rerun:** defaults, classes balanced. RF and GB: .000 in ROC-AUC, PR-AUC, G-mean and Brier. It is SMOTE in
practice. Meets C1; Table 17 states that it does not reproduce its paper (D22).

**Look at in the PDF:** Eq. 6 and the sentence on z (p. 1625), which make the weights near 1; Eq. 3 (p. 1624);
Table 3, row Haberman (p. 1629).

Read: [ ]  Questions:
