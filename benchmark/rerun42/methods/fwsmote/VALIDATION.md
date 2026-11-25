# FW-SMOTE validation: yeast3

**Result: close.** The paper prints AUC 90.3 for FW-SMOTE with k-NN on yeast3 (Table A.1,
Supp. p.29). Under the protocol the paper states (FW-SMOTE's parameters tuned inside the
training folds), `fwsmote.FWSMOTE` gives **89.5** (mean of five ten-fold CV runs, range 88.8
to 90.5): a difference of **-0.8** points. Picking the configuration on the test folds instead
gives **90.4** (+0.1), and that reading also matches the paper's FW-SMOTE values for LR
(88.8 against 89.0) and linear SVM (89.2 against 89.1).

Verdict scale, fixed before the comparison: reproduced if the mean is within 0.5 points of
the paper's value, close if within 2 points, not reproduced otherwise. All values are x100.

## 1. Target

* **Dataset**: yeast3 = ldd28 (Table 1, p.7: 1,484 rows, 8 attributes, IR 8.1, 11.0%
  minority). File: keel-ds 0.2.5 `imbalanced/raw/yeast3.dat` (1,484 rows, 163 positive),
  the same KEEL dataset. Chosen because it is one of the rerun's 42 tasks, has an exact
  KEEL file, has 163 minority examples (less fold noise than the ecoli and glass tasks) and
  has features already in [0, 1] (so the unstated scaling matters little).
* **Paper's values on yeast3** (Supplementary Appendix A):

| Classifier | FW-SMOTE AUC | FW-SMOTE G-mean | SMOTE AUC | SMOTE G-mean | Tables (Supp. pages) |
|:--|:--|:--|:--|:--|:--|
| k-NN (k = 5) | **90.3** | 90.3 | 88.4 | 88.6 | A.1 (p.29), A.4 (p.32) |
| linear SVM (C = 1) | 89.1 | 88.7 | 88.6 | 88.9 | A.2 (p.30), A.5 (p.33) |
| logistic regression | 89.0 | 88.5 | 88.2 | 88.2 | A.3 (p.31), A.6 (p.34) |

## 2. Protocol: what the paper states and what was assumed

| Item | Paper (Section 4.1, pp.7-8) | Used here |
|:--|:--|:--|
| Validation | ten-fold cross-validation | stratified, shuffled; **five runs with seeds 0-4** (the paper reports one run, seed unknown) |
| Measures | AUC and G-mean, averaged x100 | per-fold means; AUC read two ways (below) |
| Classifiers | k-NN k = 5, linear SVM C = 1, LR "no parameter setting" | `KNeighborsClassifier(5)` (Euclidean, uniform votes; computed exactly by a fast path, see section 5), `SVC(kernel="linear", C=1)`, `LogisticRegression(C=inf)` (no penalty) |
| FW-SMOTE k, N | k = 5; N in {1, 3}, the better on average **test** performance | the same (N = 3 was better in every run) |
| FW-SMOTE grid | ranking x r x p x quantifier x alpha = 4 x 3 x 3 x 4 x 2 = 288 (pp.7, 9-10) | the same 288, in the order of Table 4 |
| Tuning | "performed within the training set" (p.7); scheme not stated | **(A)** inner stratified 5-fold CV on each outer training set, ties to the first configuration in Table 4's order (p.10); **(B)** the configuration with the best mean test AUC over the ten folds, the reading of "the best parameter configuration ... for each method" (Supp. p.29) and of Table 4 (one configuration per dataset, p.10) |
| AUC | "AUC (Area Under the Curve)"; computation not stated | **crisp**: (TPR + TNR)/2 from predicted labels (what the supplement's exact 50.0 values with G-mean 0.0 indicate, NOTES.md section 6.7); **score**: ROC AUC of the classifier's scores |
| Scaling | not stated | none (main); min-max fitted on each training fold (check) |
| SMOTE baseline | Nekooeimehr's Matlab SMOTE (p.8) | `FWSMOTE` with equal weights, r = n, p = 2 (the reduction stated on p.6), N in {1, 3} |
| FW-SMOTE code | Matlab, "github.com/cvairetti" (p.8) | three readings: **paper-weighted** (the default of `fwsmote.py`), **paper-limit** (p = inf as max of b_j), **smoteiowa2019** (the 2019 code's departures: gap 0.3, partners with replacement, Minkowski on w-scaled features, RIM over r positions, normalized MI) |

## 3. Results

### 3.1 k-NN, the main experiment (five CV runs, all readings, both tuning protocols)

Crisp AUC, mean over the five runs [min, max]; difference = mean minus the paper's value.

| Method | Paper | This implementation | Difference |
|:--|:--|:--|:--|
| no oversampling | | 83.1 [82.5, 83.7] | |
| SMOTE (N = 3 kept) | 88.4 | 89.5 [89.0, 90.1] | +1.1 |
| FW-SMOTE, default configuration (Fisher, r = n/2, p = inf, basic RIM, alpha = 0.4), untuned | | 89.5 [89.0, 89.9] | |
| **FW-SMOTE, (A) tuned inside the training folds** (the stated protocol) | **90.3** | **89.5 [88.8, 90.5]** | **-0.8** |
| FW-SMOTE, (B) best configuration on the test folds | 90.3 | 90.4 [89.7, 90.9] | +0.1 |

G-mean of the same pipelines: SMOTE 89.3 (paper 88.6, +0.7); FW-SMOTE (A) 89.3 (paper 90.3,
-1.0); FW-SMOTE (B) 90.2 (paper 90.3, -0.1).

The other implementation readings (crisp AUC, mean [min, max]):

| Reading | Default config | (A) tuned in training | (B) best on test |
|:--|:--|:--|:--|
| paper-weighted (the default) | 89.5 [89.0, 89.9] | 89.5 [88.8, 90.5] | 90.4 [89.7, 90.9] |
| paper-limit | 88.9 [88.2, 89.5] | 89.1 [88.8, 89.6] | 90.4 [89.7, 90.9] |
| smoteiowa2019 (authors' 2019 code) | 89.2 [88.2, 90.5] | 88.8 [87.6, 89.5] | 90.8 [90.6, 91.4] |

Score-based AUC (the other reading of "AUC"): no oversampling 92.8, SMOTE 93.6 (paper 88.4),
FW-SMOTE 93.6 to 94.6 in every reading and protocol (paper 90.3): 3 to 5 points above the
paper's values, and above every AUC the paper prints for yeast3 (87.1 to 90.3 across the
eleven methods of Table A.1). The paper's AUC is not the score-based one; the crisp reading
fits.

### 3.2 Checks

* **Min-max scaling** (k-NN, paper-weighted, five runs, no inner CV): SMOTE 89.1
  [88.5, 89.8], FW-SMOTE default 89.6 [88.7, 90.3], (B) 90.6 [90.2, 91.0]. Scaling moves
  the numbers by less than 0.5 points.
* **LR and linear SVM** (paper-weighted, two runs, (B) and the default only; the inner CV
  was not run for them because of the cost of 288 x 2 x 60 fits):

| Classifier | SMOTE: paper / here | FW-SMOTE default config | FW-SMOTE (B): paper / here | G-mean (B): paper / here |
|:--|:--|:--|:--|:--|
| LR | 88.2 / 88.5 | 88.4 | 89.0 / 88.8 | 88.5 / 88.5 |
| linear SVM | 88.6 / 88.9 | 89.1 | 89.1 / 89.2 | 88.7 / 89.0 |

  Score-based AUC is again far from the paper (96.8 to 96.9 for both classifiers).

## 4. Reading the results

1. **The implementation reproduces the paper's FW-SMOTE numbers when the configuration is
   chosen on the test folds**: AUC within 0.2 points for all three classifiers (90.4, 88.8,
   89.2 against 90.3, 89.0, 89.1) and G-mean within 0.3 (90.2, 88.5, 89.0 against 90.3, 88.5,
   88.7). Under the protocol the paper states (tuning inside the training folds), the k-NN
   value is 0.8 points lower; the paper's 90.3 lies inside the range of the five CV runs
   (88.8 to 90.5), so a single CV run could produce it.
2. **The paper's gain over SMOTE is not reproduced under the stated protocol.** With k-NN the
   paper has FW-SMOTE 1.9 points above SMOTE (90.3 against 88.4); here the gain is 0.0 under
   (A) and 0.9 under (B). With LR and SVM the paper's gains (0.8 and 0.5) shrink to 0.3 and
   0.4 under (B), and to -0.1 and +0.2 for the untuned default configuration. Part of the
   gap is the SMOTE baseline, which is 0.3 to 1.1 points
   higher here than in the paper (a different SMOTE implementation; the paper's is
   Nekooeimehr's Matlab code).
3. **Tuning does not help on yeast3**: the tuned FW-SMOTE (A) equals its untuned default
   (89.5). The inner CV picks noisy winners (over the 50 outer folds of the paper-weighted
   reading: Correlation Score 26 times, Fisher 11, MI 7, EC 6; p = inf 22, p = 1 18, p = 2 10;
   r = n/2 28 times). Choosing among 576 configurations on the test folds (B) adds about
   one point, which is about the size of the paper's advantage over SMOTE.
4. **The readings of the open points matter little on yeast3**: the weighted Chebyshev
   distance beats the limit reading by 0.6 points on average in the default configuration
   (0.3 to 0.8 per run) and ties it under (B); the 2019 code's departures (fixed gap 0.3 and
   the rest) change results by less than one point.
5. N = 3 (300% oversampling) was the better amount in every run, for every method, with the
   crisp AUC.

## 5. What the paper does not state (and what was used)

* the folds (stratified? seed? one run?): stratified, shuffled, seeds 0-4, one run each;
* the tuning scheme "within the training set": (A) inner stratified 5-fold CV, (B) best on
  the test folds; ties to the first configuration in Table 4's order (p.10);
* how AUC is computed: both readings reported; the crisp one fits the paper;
* scaling: none (and min-max as a check);
* the classifier implementations (Matlab): scikit-learn equivalents as listed in section 2;
* the random seeds of the oversampling: one seed per outer fold and N, shared by all
  configurations (common random numbers);
* which code produced the tables: three implementation readings reported;
* how the paper's SMOTE baseline differs from Algorithm 1 with equal weights: unknown.

The fast k-NN path (distances from the test rows to the original training rows computed once
per training set, synthetic rows added per configuration) was checked against
`KNeighborsClassifier(5)` on the default configuration of every outer fold: identical
predicted probabilities for all test rows in 48 of 50 folds, and for all but one row in the
other 2 (the fast path is exact except for the order of equidistant neighbors, so the fifth
neighbor was a tie or a floating-point near-tie there). The rank-based AUC was checked against
`sklearn.metrics.roc_auc_score`.

## 6. How to reproduce

From this folder, one invocation at a time (each merges its results into
`validation_results.json`):

```
python3 -I validate_fwsmote.py --seeds 0 1 2 3 4 --classifiers knn
python3 -I validate_fwsmote.py --seeds 0 1 2 3 4 --classifiers knn --no-inner --readings paper-weighted --scale minmax
python3 -I validate_fwsmote.py --seeds 0 1 --classifiers lr svm --no-inner --readings paper-weighted
```

Run times on the shared 2-core machine of 11 November 2026: 2.5 to 6 minutes per CV run
for the first command (two runs in parallel, about 17 minutes in all), 34 seconds for the
second, 6 minutes for the third. `validation_results.json` holds every per-run summary (keys `knn`,
`knn-noinner-minmax`, `lr-noinner`, `svm-noinner`), including the configurations chosen.
