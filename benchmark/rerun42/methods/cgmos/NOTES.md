# CGMOS re-implementation: ambiguities, choices and points to check

Paper: X. Zhang, D. Ma, L. Gan, S. Jiang and G. Agam, "CGMOS: Certainty Guided Minority
OverSampling", CIKM 2016, pp. 1623-1631, doi:10.1145/2983323.2983789. Page numbers below are the
proceedings pages printed on the PDF. The arXiv version (1607.06525) prints the same Haberman row
of Table 3 and the same Table 1 entries; the differences I found are the sentence quoted in item 3
of section 2 and the phrases listed in section 6.

Files: `cgmos.py` (class `CGMOS`), `test_cgmos.py`, `validate_cgmos.py`, `VALIDATION.md`,
`results/` (raw validation output). No author code exists as far as I could find (nothing is
linked from the paper, from arXiv or from Papers with Code), so nothing was cloned into `ref/`.

## 1. Main finding: as printed, CGMOS is SMOTE up to a negligible change in seed probabilities

Eq. 6 (p. 1625) sets W(x_i) = 1 + (1/n) sum_j R_{+i}(y_j | x_j), and seeds are drawn with
probability W(x_i) / z (p. 1625). The relative change R_{+i} is nonzero only for samples within
reach of x_i's kernel, and it is bounded (with Eq. 3 as printed, every R lies in (-1, 1)), so
W(x_i) - 1 is of order (number of neighbors affected) / n. The seed distribution is therefore
within O(1/n) of SMOTE's uniform one:

* Haberman (n = 306): W in [0.992, 1.0004]; the total-variation distance between CGMOS's seed
  distribution and the uniform one is 0.0007; no seed's probability differs from 1/n_min by more
  than 0.6% of 1/n_min.
* Over Haberman, TAE, Contraceptive, Libras (90 features) and yeast4, and over four readings
  (default, normalized kernel, all-class bandwidth neighbors, sigma = 3), the total-variation
  distance is at most 0.0025. A leave-one-out reading of Eq. 3 (not the printed one) gives at
  most 0.002. (`validate_cgmos.py`, Part C.)
* The paper's own Figure 1 (p. 1625, panel 3) plots W - 1 on a 1e-4 scale for n = 2400, the
  same order of magnitude.
* Theorem 1 (p. 1626) is correct but its margin is tiny: E_p = sum_i W_i^2 / z = mean(W) +
  var(W) / mean(W) and E_s = mean(W), so the guaranteed gain over SMOTE is var(W) / mean(W),
  between 5e-7 and 3e-5 on these five data sets (Haberman 3e-6).
* In the validation on Haberman (VALIDATION.md), 99.6% of CGMOS's synthetic rows (at least 97.7%
  in every fold) are identical to those of a uniform-seed run drawn from the same random stream;
  the six-classifier AUC is identical in 60 of 100 folds; and CGMOS minus SMOTE is +0.0007
  (se 0.0026) in the main protocol and within 0.003 in every other reading. CGMOS and SMOTE
  therefore differ by no more than the noise between two SMOTE implementations.

Consequence: the paper's reported gains over SMOTE (Table 3, p. 1629: average AUC 0.864 against
0.844; Haberman 0.651 against 0.600) cannot come from the seed weighting as printed. The authors'
code may have used W differently (for example W - 1, which can be negative, or W - min W), or the
gains may come from other, unreported differences between their CGMOS and SMOTE runs. **A person should check p. 1625 (Eq. 6 and the sentence on z) and decide
how the survey describes this.** Note also that the survey's account (`accounts.tex`,
`\item[CGMOS (2016)]`) says seeds are drawn "in proportion to ... the average relative change";
Eq. 6 is *one plus* the average relative change, and the "one plus" is what makes the weights
nearly uniform.

## 2. Choices the paper leaves open (each is marked `CHOICE:` in `cgmos.py`)

| # | Point | Paper | Choice in `cgmos.py` |
|:--|:--|:--|:--|
| 1 | Two classes only | "the binary classification problem" (Sec. 2, p. 1624); multiclass data sets binarized by keeping the smallest class (Sec. 4.1, p. 1626) | More than two classes raises `ValueError`; binarizing is the caller's job. |
| 2 | Candidate seeds | "CGMOS assigns each sample (x_i, y_i) in D a weight W(x_i) which is used to determine the probabilities of x_i being chosen for interpolation" (p. 1625); z sums over all n; Fig. 1 panel 2 colors both classes | Minority samples only: the interpolation is SMOTE's (p. 1625), which needs a minority seed and minority neighbors, and the paper gives no rule for a majority seed. Theorem 1 holds for any candidate set (its n is then the number of candidates). |
| 3 | sigma and q of Eq. 4 | No values. arXiv 1607.06525 says "We will discuss selection of parameters sigma and q in Section 4", but Section 4 does not | `sigma = 1.0` (h_k is the plain mean distance), `q = 5` (SMOTE's neighborhood size). |
| 4 | Kernel K | "a kernel function which has zero mean and integrates to one" (p. 1624) | Gaussian, h_k as its standard deviation: K(u) = exp(-\|\|u\|\|^2 / 2). Its constant cancels in every ratio. |
| 5 | 1/h_k^m factor in Eq. 3 | Eq. 3 prints K((x_j - x_k)/h_k) with no 1/h_k^m, although K "integrates to one" | Eq. 3 as printed (`normalize_kernel=False`). `normalize_kernel=True` gives the standard KDE (computed in the log domain with each row rescaled, which leaves every ratio unchanged). With per-sample bandwidths the factor does not cancel. |
| 6 | Neighbor set of Eq. 4 | "its q nearest neighbors" | Same class (`bandwidth_neighbors="class"`), since each kernel belongs to its class density in Eq. 3; `"all"` uses all of D. |
| 7 | x_j in its own density | Eq. 3 sums over k = 1..n | Included, as printed. It keeps C(y_j \| x_j) >= K(0) / S(j) > 0, so Eq. 5's division is safe. |
| 8 | Class priors P(l) | Bayes' rule is written (p. 1624), P(l) not specified | P(l) = n_l / n, recomputed after the addition (n_mnr + 1, n + 1). Then the counts cancel and C(y_j \| x_j) = S_{y_j}(j) / S(j). Evidence: b-kde on the original data has minority recall 0.033 (Table 2, p. 1628), which fits a classifier with the majority-favoring empirical prior. Keeping the priors fixed at n_l / n after the addition gives nearly the same weights (total-variation distance from uniform at most 0.0016 on the five data sets of section 1). |
| 9 | The added copy | "a new sample will be added to the same location as x_i" (p. 1625) | It carries x_i's bandwidth h_i, so its kernel at x_j is K_ji (column i of the kernel matrix); the other bandwidths are not recomputed. |
| 10 | When weights are computed | "can achieve data oversampling in a single step" (Sec. 1.2, p. 1624) | Once, on the original data; seeds then drawn independently with replacement with probability W / z. |
| 11 | SMOTE's k | "The interpolation phase of CGMOS is the same as SMOTE[4]" (p. 1625); no k | k = 5 (SMOTE paper), neighbor chosen uniformly; k clipped to n_min - 1. |
| 12 | Gap | Same as SMOTE | One U(0, 1) gap per synthetic sample (a point on the segment, as SMOTE's text and imbalanced-learn do), not one per attribute as in SMOTE's pseudo-code. |
| 13 | Number of synthetic samples | Not stated for the main experiments; Sec. 4.5 (p. 1627) varies "k delta" with k from 0.5 to 5, delta = n_mjr - n_mnr | `k_delta = 1.0`, i.e. delta samples (balanced classes). |
| 14 | Degenerate inputs | Not discussed | q clipped to class size - 1; a zero bandwidth (q or more duplicates) is set to the smallest positive bandwidth of its class; a single-sample class gets the median bandwidth; n_min < 2 raises; equal class sizes return the data unchanged. |

## 3. Correctness checks done

* The closed forms used in `cgmos_weights` (module docstring, Step 4) match a literal
  recomputation of Eqs. 3, 5 and 6 (append a copy of x_i, recompute every posterior with Bayes'
  rule and class priors) to 1e-12, for both kernel readings and both neighbor sets
  (`test_weights_match_literal_recomputation`).
* Every synthetic row lies on the segment between its seed and one of the seed's 5 nearest
  minority neighbors (`test_synthetic_rows_lie_on_segments_to_minority_neighbors`).
* Runtime: O(n^2 m) for the weights, memory bounded by blocks of about 4e6 kernel entries.
  On one shared CPU thread: n = 2,000 (m = 20) 0.6 s, n = 5,000 1.6 s, n = 10,000 5.8 s.

## 4. Figure 1 (p. 1625)

* Panels 1 and 2 seem to use per-class color scales: under one posterior, minority samples at the
  boundary and majority samples at the boundary cannot both have low certainty, yet both are
  blue in panel 1. Panel 2 also colors majority samples, which is what suggests weights for all
  of D (item 2 above).
* Panel 3 (W - 1 for a minority example moved along the center line) could not be matched
  quantitatively. The Gaussian parameters are not given, so they were estimated from the figure.
  The shape near the boundary (a rise on the minority side, then a plunge below zero) is
  reproduced; the plateau of 1.2e-4 to 2.4e-4 deep in the minority class (region A) is not
  reproduced by any reading tried (sigma 0.5 to 10, q 5 to 20, both kernel normalizations, both
  neighbor sets). See `validate_cgmos.py` Part B and VALIDATION.md.

## 5. Experimental details the paper does not state (relevant to the validation)

Feature scaling; whether oversampling happens inside the cross-validation folds; the classifiers'
hyperparameter grids and the tuning procedure; the implementations (the "random forest
implementing the C4.5 decision tree" suggests Weka); how AUC is averaged over folds; random seeds;
the number of synthetic samples; the settings of the competing methods (SMOTE's k). The readings
used are listed in VALIDATION.md.

## 6. Other points for a person to check against the PDF

* The WP6.8 assignment for this method cites "Zhang and Chen"; the PDF lists five authors (Zhang,
  Ma, Gan, Jiang, Agam), and the survey's `refs.bib` entry `zhang2016cgmos` has them right.
* Eq. 3 (p. 1624): confirm that no 1/h_k^m factor is printed (item 5).
* Eq. 6 and the sentence on z (p. 1625): confirm the "1 +" (section 1).
* Table 1 (p. 1627) lists Haberman as 306 samples, 3 features, ratio 0.36, which matches the KEEL
  copy exactly. Some other rows do not follow the stated "smallest class" rule (for example Yeast
  with ratio 0.04, where the smallest class, ERL, would give 0.003).
* The arXiv version's Table 2 caption says "on the artificial datasets" and its Sec. 4.5 mentions
  "the experiments of the artificial dataset", which are not described; the CIKM version does not
  have these phrases.
