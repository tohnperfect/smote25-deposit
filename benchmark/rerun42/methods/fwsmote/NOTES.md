# FW-SMOTE (slug `fwsmote`): notes for the SMOTE25 rerun (WP6.8)

Paper: S. Maldonado, C. Vairetti, A. Fernandez, F. Herrera, "FW-SMOTE: A feature-weighted
oversampling approach for imbalanced classification", Pattern Recognition 124 (2022) 108511,
doi:10.1016/j.patcog.2021.108511. Page numbers are the journal's (pp.1-13); "Supp." is the
supplementary Appendix A (pp.29-34).

Files in this folder:

| File | What it is |
|:--|:--|
| `fwsmote.py` | class `FWSMOTE` (imbalanced-learn interface) and the ranking and weighting functions |
| `test_fwsmote.py` | 16 quick checks; `python3 -I test_fwsmote.py` (or with pytest) |
| `validate_fwsmote.py`, `validation_results.json`, `VALIDATION.md` | reproduction of the paper's yeast3 numbers |
| `ref/` | code read as a reference, never run (see "Sources") |
| `NOTES.md` | this file |

## 1. Sources read

* The paper text in full and the supplement text in full. Eqs. (2)-(12) and Algorithm 1 are
  garbled in the text file, so PDF pages 4 and 5 were checked as images (page 5 at 220 dpi).
* The survey's account (`\item[FW-SMOTE (2022)]` in `v08/supplement/gen/accounts.tex`). It
  agrees with the paper. One refinement: Algorithm 1 removes each partner from T after use
  (step 14), so the N partners of a seed are distinct, while Chawla's SMOTE pseudo-code draws
  the neighbor with replacement. "The random partner ... as in SMOTE" is right otherwise.
* **The authors' code exists.** The paper points to github.com/cvairetti (p.8). That account
  holds `cvairetti/SMOTEIOWA` ("SMOTE" with the IOWA operator, the method's working name):
  commit 9d2f306cd0c836b38149c694a1b47d1f82ae5012, 23 April 2019, two Matlab files,
  `SMOTEMODWOWA.m` (the sampler) and `OWAFunction.m` (the quantifiers). It was found with a
  GitHub repository search (`user:cvairetti`) on 11 November 2026 and cloned to
  `ref/smoteiowa/`; it was read, not run. It predates the paper's submission (September 2020)
  by more than a year, has no experiment scripts and calls `muteinf` (FSLib) without
  including it, so whether it produced the paper's tables is not known. Its differences from
  the paper are listed in section 5.
* `muteinf` (FSLib, by G. Roffo), which the authors' code calls: read in two ports,
  `ref/ZixiaoShen_ECFS-Feature-Selection-via-Eigenvector-Centrality/Mutual_Information.m`
  (commit 9da1c4b) and `ref/OhadVolk_ECFS/ec_feature_selection/_ecfs_functions.py`
  (commit fd0edcf). Roffo's own repository `ref/roffo-infFS` (commit ebaa33e) calls
  `muteinf` but does not contain it.
* Not read: `kostasb30/Fw-SMOTE` (a third-party repository of June 2026, not the authors').

## 2. The weights: there is no optimization problem in the paper

The task description said that the feature weights come from an optimization the paper
defines. The paper defines none. The weights are closed-form (Algorithm 1 steps 2-3, p.5):

1. a filter score u_j per feature (Fisher Score Eq. 6, Mutual Information Eq. 7, Correlation
   Score Eq. 8, or Eigenvector Centrality [40]);
2. a RIM quantifier gives rank position j the weight w_j = Q(j/n) - Q((j-1)/n) (Eqs. 9-12);
3. the IOWA operator gives w_j to the feature with the j-th largest u (Eqs. 3 and 5, p.4).

The steps that use a solver, and how mine relates to the authors':

| Step | Paper | Authors' code (2019) | This implementation |
|:--|:--|:--|:--|
| Step 9, T = arg min over k-subsets of sum of IMOWAD | stated as an arg min (p.5) | Matlab `sort` of the distance row | exact: the objective is a sum over T, so the k smallest distances are optimal; `np.partition` plus a stable sort, ties by row order |
| Eigenvector Centrality | "the eigenvector related to the largest eigenvalue of A" (p.5) | `eigs(A, 1, 'lm')` (ARPACK) | `numpy.linalg.eigh` (dense LAPACK), largest eigenvalue; A is symmetric and non-negative, so both give the Perron vector up to sign, removed by `abs` |
| Parameter grid (288 configurations) | "grid search ... within the training set" (p.7) | not in the repository | only in `validate_fwsmote.py` (it is model selection for the experiments, not part of the sampler) |

The only true optimization in the authors' code is `OWAFunction.m` option 5 (O'Hagan's
maximum-entropy OWA weights, solved with CVX). The paper does not use it: it lists only the
four RIM quantifiers (Eqs. 9-12, p.5; Table 4, p.9). It is not implemented here.

## 3. What is implemented (paper reading, `variant="paper"`, the default)

| Algorithm 1 (p.5) | Implementation |
|:--|:--|
| Step 1, M* = M | original rows returned first, unchanged |
| Step 2, u = FR(all training data) | `fisher_score`, `mutual_information_score`, `eigenvector_centrality_score`, `correlation_score`, or a callable; computed on both classes |
| Step 3, w = RIM(u, alpha) | `rim_weights(n, alpha, quantifier)` over all n positions, then `iowa_feature_weights` |
| Step 4, S | the r top-ranked features (or the epsilon rule) |
| Steps 5-8, IMOWAD | Eq. (5) restricted to S: `(sum_{j in S} w_j b_j^p)^(1/p)` (SciPy's weighted Minkowski is exactly this; checked in the tests) |
| Step 9, T | k nearest other minority examples (k capped at \|M\| - 1) |
| Steps 10-15 | N distinct partners per seed (without replacement), gap v ~ U[0, 1) per synthetic row, x* = x_i + v (x_k - x_i) on all n features |

Defaults: `N=1, k=5, ranking="fisher", quantifier="basic", alpha=0.4, r=0.5, p=inf,
chebyshev="weighted"`. k = 5 is stated (p.7). Fisher Score is the recommended default (p.11).
r = n/2, p = inf, basic RIM and alpha = 0.4 are the values that most often gave the best AUC
(Table 4, p.9), recommended in Section 4.3 (p.10). **N has no default in the paper**: it
tried N = 1 and N = 3 (100% and 300%, p.7) and kept the better one on test data (p.8).
N = 1 (the first value listed) is a CHOICE (C15). The paper's rule gives N |M| synthetic rows; it
does not balance the classes.

## 4. Choices the paper leaves open (marked `CHOICE:` in `fwsmote.py`)

| # | Open point (paper location) | Choice | Authors' code |
|:--|:--|:--|:--|
| C1 | Eqs. (10)-(12) do not sum to 1 as printed (Eq. 11 is negative), against "sum w_j = 1, w_j in [0, 1]" (p.4) | divide each quantifier by its sum | same (`w = re/reT`) |
| C2 | p = inf (p.7, Table 4) is not defined by Eq. (5); its limit is max_{j in S} b_j, where the weights drop out | default `chebyshev="weighted"`: max_{j in S} w_j b_j; `"limit"` available | weighted (`pdist(W.*X, 'chebychev')`) |
| C3 | Step 4 "the r largest values of w" vs. "subset S of relevant variables" (p.5): they differ when w is not decreasing in rank (Eq. 12 always; Eq. 10 with alpha = 0.6; Eq. 9 with alpha > 1) | S = the r top-ranked features (same as step 4 for the defaults) | same (top `nvars` by score) |
| C4 | r = n/2, 3n/4 for odd n (p.7) | fraction rounded half up (Matlab's `round`), within [1, n] (n = 7 gives 4 and 5) | takes an integer `nvars` |
| C5 | ties in u (Eq. 5 "the jth largest") | tied features share the mean of their positions' weights (Yager and Filev's IOWA tie rule); S takes tied features in column order | Matlab `sort` (column order, no averaging) |
| C6 | Eq. (6) is printed as \|mu_1 - mu_2\| / (sigma_1^2 + sigma_2^2), the prose says "normalized with a joint standard deviation" (p.5) | the printed formula, sample variances (ddof = 1); 0/0 gives 0, c/0 gives +inf | the printed formula with `var` (ddof = 1); 0/0 gives NaN, which Matlab's descending sort ranks first |
| C7 | Eq. (7) needs binning for numerical features; how is not stated (p.5) | equal-width bins, FSLib's count (20 if m/10 > 20, else max(floor(m/10), 10)), plug-in probabilities, natural log | `muteinf` with the same bins, but normalized (2 I / (H(X) + H(Y))) and with 1e-5 in empty cells |
| C8 | Eigenvector Centrality has no formula (p.5) | Roffo and Melzi's ECFS exactly as in the authors' code (case 3): squared mean difference over the sum of class variances (0 replaced by 10000), `muteinf`, v = \|sep + mi\| / 2, K = minmax(v v^T), Sigma = minmax(max(s_i, s_j)), A = 0.5 K + 0.5 Sigma, score = \|leading eigenvector\| | same; constant features get MI 0 here (`muteinf` gives them a spurious large value) |
| C9 | Eq. (8): j' = j allowed? constant features? | j' != j; undefined correlations ignored; no defined correlation gives 0 | `min(abs(corr(X)), [], 2)` (diagonal included, NaN skipped) |
| C10 | epsilon rule with no weight above epsilon | keep the top-ranked feature | no epsilon rule |
| C11 | ties in the distances of step 9 | row order of the minority examples | Matlab `sort` (row order) |
| C12 | N larger than \|T\| (the paper assumes N < k, p.6) | T is refilled once emptied | draws with replacement anyway |
| C13 | which class is the minority with equal counts | the smaller label | class -1 |
| C14 | more than two classes | `ValueError` (the paper's method is two-class, p.5) | two classes {-1, +1} only |
| C15 | N has no default (pp.7-8: the better of N = 1 and N = 3 on test data) | N = 1, the first value listed | `over_param` argument, no default |

Also open but outside the sampler (they matter for the rerun and the validation): feature
scaling (none stated; Eq. 6 as printed is not scale-invariant, so the Fisher ranking depends
on the caller's scaling), the CV seed and stratification, the inner tuning scheme, and how the
AUC is computed (see `VALIDATION.md`).

## 5. Where the authors' 2019 code departs from the paper's text

`variant="smoteiowa2019"` re-creates these five departures (written from the Matlab, not run):

| | Paper's text | `SMOTEMODWOWA.m` / `OWAFunction.m` |
|:--|:--|:--|
| (a) | RIM weights over the n positions, then restricted to S (steps 3, 4, 7) | `OWAFunction(nvars, ...)`: weights over the r kept positions |
| (b) | IMOWAD = (sum w_j b_j^p)^(1/p) (Eq. 5) | `pdist(W .* Xsel, norm_type)` = (sum w_j^p b_j^p)^(1/p); the same only for p = 1 |
| (c) | partners without replacement (step 14) | `randi([1 k], 1, over_param)`: with replacement |
| (d) | gap v random in (0, 1) (step 12, p.6) | `u=0.3; %non-random version` (the random line is commented out) |
| (e) | MI by Eq. (7) | `max(muteinf(x, Y), 0)`, the normalized MI |

Smaller ones: the code skips the seed by drawing from sorted positions 2 to k + 1, so if the
seed has a duplicate with a lower row index, the seed itself can be drawn as its own partner;
it returns the minority rows first; and its Fisher score ranks 0/0 features first (NaN in a
descending sort).

## 6. Things a person should check against the PDF

1. **Eq. (6), p.5**: no square root in the denominator, while the prose says "joint standard
   deviation". Only the order of the scores matters, and the two readings order features
   differently in general. The implementation follows the printed formula, as the authors'
   code does; the prose reading can be passed as a callable `ranking=f` with
   f(X, y) = |mu_1 - mu_2| / sqrt(sigma_1^2 + sigma_2^2).
2. **Eqs. (10)-(12), p.5**: as printed, they do not sum to 1 and Eq. (11) is negative.
3. **Eq. (12)** gives weights that increase with rank (the least relevant feature weighs
   most), and **Eq. (10)** with alpha = 0.6 is not monotone. With "the r largest values of
   w" (step 4) these quantifiers would keep low-ranked features. Is that intended?
4. **p = inf** in Eq. (5): see C2. With the limit reading and the paper's preferred p = inf,
   the weights play no role and FW-SMOTE is SMOTE with the Chebyshev distance on the top-r
   features. Table 4's tie rule (p.10: a tie goes to the first-listed value) would then credit
   every p = inf tie across quantifiers and alpha to "Basic RIM" and "alpha = 0.4", which is
   one way to read their large shares in Table 4.
5. **Table 4, p.9**: the percentages are multiples of 1/90 (64.4% = 58/90, 7.8% = 7/90,
   83.3% = 75/90), while there are 42 datasets (30 + 12). What the 90 cases per classifier
   are is not stated.
6. **Tuning, pp.7-8**: "performed within the training set" (inner scheme not stated), but the
   supplement reports "the best parameter configuration obtained for each oversampling
   method" (Supp. p.29) and Table 4 one configuration per dataset (p.10). N is chosen on test
   performance (p.8). FW-SMOTE is tuned over 288 configurations while each baseline has only N
   tuned. On yeast3 the paper's FW-SMOTE values for all three classifiers are matched within
   0.2 AUC points when the configuration is picked on the test folds, and the k-NN value is
   0.8 points lower when it is tuned inside the training folds (`VALIDATION.md`): one dataset,
   so suggestive only, but the survey may want to say how the paper tuned.
7. **AUC, p.7**: not said whether it is computed from scores or from predicted labels. The
   supplement favors labels, AUC = (TPR + TNR)/2 per fold: SVM on ldd15 (Table A.2, Supp.
   p.30) gives exactly 50.0 for FW-SMOTE, SMOTE, BL-S., SL-S., RBO and PCA-S. and 49.4 to
   49.7 for three others, all with G-mean 0.0 (Table A.5, p.33): what (TPR + TNR)/2 gives
   when no minority example is predicted, and values a score-based AUC of a linear SVM would
   hardly hit. SVM on ldd25 gives AUC 51.7 with G-mean 5.8, which is what one fold with
   TPR = 1/3 and nine folds with TPR = 0 (TNR = 1 throughout) give. The validation supports
   this reading (`VALIDATION.md`).
8. **ldd17 (glass-0-6 vs 5)**: Table 1 (p.7) lists its classes as (91.7, 8.3), reversed. In
   Table A.4 (Supp. p.32) the four Matlab implementations (FW-SMOTE, SMOTE, BL-S., SL-S.)
   have G-mean 0.0 while their AUC (Table A.1) is 79.5 to 89.0; for LR (Tables A.3 and A.6)
   every method but PCA-S. has AUC 90.0 and G-mean 97.0. Neither fits AUC = (TPR + TNR)/2 on the same
   predictions; with 9 minority examples, one of the ten test folds has none, and how such a
   fold was scored is not stated. Avoid ldd17 for any comparison.
9. **Datasets**: "ecoli" (ldd2) is KEEL's ecoli3 (35 of 336, IR 8.6); "image1" (ldd19) is
   close to KEEL's segment0 (2,308 rows instead of 2,310); "abalone7" and "solar" (ldd1,
   ldd22) have no exact KEEL file.

## 7. Notes for the rerun

* Use `variant="paper"` (the default). `variant="smoteiowa2019"` exists for the validation.
* The paper's amount of oversampling is N per minority example, not balancing. The paper's
  choice of N on test data (p.8) should not be copied; the rerun's protocol should fix N.
  In the validation (yeast3, IR 8.1) N = 3 beat N = 1 in every run. Near-balance would need
  N close to IR - 1, which breaks the paper's N < k = 5 for IR > 6; the sampler then refills
  T (C12) rather than failing.
* With the defaults and p = inf, the sampler uses only r = n/2 features (rounded half up)
  for the neighborhood and all n features for the synthetic rows.
* Two-class only (raises otherwise); at least 2 minority examples; k is capped at |M| - 1.
* Cost: O(|M|^2 |S|) distance work, done in row blocks (about 32 MB at a time), so large
  minority classes (for example the Kaggle smoke task) fit in memory. Ranking: MI and EC loop
  over features (fast for d <= 200).
* Tests: `python3 -I test_fwsmote.py` (16 checks, about 3 s).
