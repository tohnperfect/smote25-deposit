# SMOM (Zhu, Lin and Liu, 2017, Pattern Recognition 72, 327-340): extra notes from the blind coder

Source used: journal PDF only (`/home/claude/work/blind2/pdf/SMOM__journal.pdf`) and its text. Page numbers are the printed numbers (327-340). The supplement was not opened.

## (1) How the SMOM generator relates to the SMOTE rule x_new = x_i + lambda (x_j - x_i)

SMOM keeps SMOTE interpolation as its only generator: step 8.2 of Algorithm 1 creates si = xi + (xj - xi).*gamma with Eq. (1), the rule the paper gives for SMOTE itself (p. 328; Alg. 1, p. 330). **Seed selection is not changed**, because every instance of the class being oversampled is a seed (Alg. 1 step 8, p. 330). **Sample allocation is not changed**: the number zeta needed for the class, set so that every class reaches the size of the largest class (Sec. 4.1, p. 335), is spread over all its members as evenly as possible (Alg. 1 step 7, p. 330; Sec. 3.3, p. 334). **Neighbour choice is the decision point SMOM changes**: the partner is still one of the k1 nearest same-class neighbours (k1 = 12 rather than 5, standardized Euclidean distance; Sec. 4.1, p. 335), but for "trapped" instances, those outside the NBDOS clusters of "outstanding" instances (Sec. 3.1, Algs. 1-2, pp. 330-331), it is drawn with probabilities proportional to selection weights from Eq. (2). Those weights fall when a direction's PN hypersphere (centred at the midpoint of xi and xj, radius half their distance) holds instances of other classes, especially other minority classes, and rise where class c is hard to learn (Sec. 3.2, pp. 332-334), while outstanding instances draw their partner uniformly, as in SMOTE (Alg. 1 step 8.1, p. 330). If none of a trapped instance's PN neighbourhoods contains only class c, the instance itself is added as a candidate partner with the highest possible weight, 1 + w1/e, so some "synthetic" points are exact copies of the seed (Alg. 1 step 6.1, p. 330; Sec. 3.2.2, pp. 333-334). **The placement rule is not changed by SMOM, but it is flagged**: the paper's Eq. (1) uses a random vector gamma with element-wise multiplication (p. 328), which puts points anywhere in the axis-aligned box spanned by xi and xj (the paper's "hyperrectangle", p. 332) rather than on the segment of our reference rule, and I coded n only because the paper states SMOTE itself this way. **Post-filtering is not changed**: Algorithm 1 returns the synthetic set with no cleaning step, and over-generalization is handled before generation through the weights (Alg. 1, p. 330; Sec. 3.2, p. 332). **SMOM is not inside a pipeline**: it runs once as preprocessing before the four weka classifiers are trained, and AdaBoost.M1(C4.5) is just one of those classifiers, trained on the oversampled data (Sec. 4.1, p. 335).

**Decision points changed: Neighbour choice only** (Placement rule flagged as above). Link: Core.

## (2) Per-dataset scores for SMOM and plain SMOTE in the same table?

**No.** The journal article does not print a per-dataset score for any method.

- **Table 2 (p. 335):** mean +/- SD over all 27 data sets, plus mean ranks, for MG, MAUC, recall and precision (recall and precision on the smallest class only, p. 335). It covers NONE, ROS, SMOTE (default k = 5), ADASYN, SL-SMOTE, MWMOTE, MDO and SMOM, each under C4.5, AdaBoost.M1(C4.5), MLP and NB.
- **Table 4 (p. 337):** the same summaries for SMOTE, ADASYN and SL-SMOTE with k = 12, compared with SMOM.
- **Tables 3 and 5 (pp. 336, 338):** Wilcoxon R+, R- and T only.
- **Table 6 (p. 338):** averages, mean ranks and Wilcoxon results for recall_majs, recall_mins, MAUC_majs, MAUC_maj-min and MAUC_mins. It compares SMOM with SMOTE (k = 12) under C4.5 only.
- **Where the per-dataset results are:** the paper points to supplementary Tables S3-S10 for the complete Exp. 1 results (p. 335) and S13-S16 for the detailed Exp. 2 results (p. 337). S18-S20 hold the Exp. 3 results for the other three classifiers (p. 337). None of these are part of the article, and none were opened.

**Count: 0 data sets. Pairs compared: none**, because no per-dataset SMOM/SMOTE pair is printed. The Wilcoxon rank sums cannot be turned into win counts.

The table below is for context only. It shows the first metric of Tables 2 and 4 (Avg-MG), averaged over the 27 data sets, not per data set.

| Table | Classifier | SMOM | SMOTE |
|---|---|---|---|
| 2 (p. 335) | C4.5 | 0.525 | 0.512 |
| 2 | AdaBoost(C4.5) | 0.542 | 0.526 |
| 2 | MLP | 0.550 | 0.537 |
| 2 | NB | 0.435 | 0.437 |
| 4 (p. 337) | C4.5 | 0.525 | 0.450 (k = 12) |
| 4 | AdaBoost(C4.5) | 0.542 | 0.527 (k = 12) |
| 4 | MLP | 0.550 | 0.543 (k = 12) |
| 4 | NB | 0.435 | 0.404 (k = 12) |

- **Average MG:** SMOM's is higher than SMOTE's (k = 5) for 3 of 4 classifiers and lower for NB. It is higher than SMOTE (k = 12) for all 4.
- **Wilcoxon on MG, SMOM vs SMOTE (Table 3, p. 336):** R+/R- = 316/62 (C4.5), 334.5/43.5 (AdaBoost), 349/29 (MLP) and 233/145 (NB). In each case R+ + R- = 378 = 27*28/2, which is consistent with 27 data sets.

## (3) Does SMOM remove or move any original example?

**No (C3 = n).**

- Algorithm 1 outputs only the new set SI (p. 330). No step deletes, shifts or relabels an original training example.
- NBDOS post-processing "drops" small clusters only by resetting their cluster labels to 0. This marks those instances as trapped for the weighting step and does not remove them (Alg. 2 lines 21-25, p. 331).
- Trapped instances that may be outliers or noise are kept (p. 333). At most they are paired with themselves and get copies (Alg. 1 step 6.1, p. 330; pp. 333-334).

## Flags for the adjudicator

- **Placement rule:** coded n although Eq. (1) draws gamma per feature, which gives a box rather than the segment (pp. 328, 332). Under the strict scalar-lambda reference it would be y.
- **Table 1 inconsistencies (p. 334):** the class-label lists do not match L for page-blocks and wine-red (5 labels, L = 4) or for housing10 (9 labels, L = 10). Every set still has L >= 3, so category M is unaffected.
- **k for small classes:** the reset of k to class size minus 1 for classes with fewer than 12 instances is stated in Exp. 2 "for all compared algorithms" (p. 337). This is a cap, not an adaptive k.
- **Protocol:** the paper does not say whether oversampling was applied only inside the training folds of the 10 x stratified 10-fold CV (p. 335).
