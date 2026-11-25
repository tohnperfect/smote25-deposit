# RSMOTE (Chen, Xia, Chen, Wang and Wang, 2021): implementation notes

Paper: Information Sciences 553 (2021) 397-428, doi 10.1016/j.ins.2020.10.013. Pages are the journal's
printed pages (PDF page = printed page minus 396).

Files in this folder:

* `rsmote.py`: class `RSMOTE(k_neighbors=5, ir=1.0, random_state=None)` with `fit_resample(X, y)`, plus the
  helper `two_means_1d`. NumPy and scikit-learn only. After `fit_resample`, `info_` holds per class the noisy
  rows, the seeds, their m, relative density, cluster and number of synthetic rows.
* `test_rsmote.py`: 12 quick checks (`python3 -I test_rsmote.py`, about 2 s).
* `validate_rsmote.py`, `VALIDATION.md`, `validation_output.txt` (printed tables), `validation_raw.csv`
  (every classifier run); `validation_output_dropnoise.txt` and `validation_raw_dropnoise.csv` hold the
  diagnostic run that also deletes the flagged rows.
* `ref/RSMOTE/`: the authors' repository (github.com/syxiaa/RSMOTE, commits of 26 Aug 2020, head 2b55f2e),
  cloned for reading only. Nothing in it was run.

## 1. Open question: does RSMOTE delete its "noise" from the training data?

**No. The points RSMOTE calls noise are removed from the seeds only (and so from the interpolation
partners); they stay in the training data that the classifier sees.** `rsmote.py` returns them unchanged
among the original rows.

From the paper:

1. Algorithm 1 (p. 403) has "Output: Syn" and ends with "return generated samples Syn = Syn_A u Syn_B"
   (line 26). "Filter x_i from P" (line 7) and "is not operated in the following steps" (Step 1, p. 402)
   describe the algorithm's own working set: x_i does not enter P', the set that is clustered and
   oversampled.
2. Line 2 sets N = |Q|/IR - |P| with the full |P|, before any filtering. D plus Syn reaches the requested
   ratio IR only if the noisy points remain in D; if they were deleted, the result would fall short of
   balance by the number of noisy points.
3. The paper says so twice in its discussion of the label-noise results: "The oversampling methods,
   including the variants of SMOTE, do not filter any noisy samples from the original data sets, which just
   aim at avoiding interpolating in the noisy area" and "we believe that any cleaning procedure can be applied
   with RSMOTE" (p. 412); "none of the oversampling methods filter any noisy samples from the original data,
   they just try to avoid generating noise samples. Thus, any filtering or noise-cleaning method will
   contribute to improving the performance of the oversampling methods" (p. 416). The conclusion (p. 417)
   lists "post-processing approaches to address the noise samples" as future work.
4. Two sentences can be misread as deletion: "RSMOTE tries to maintain as many minority samples as
   possible, except for the noisy ones surrounded by the majority samples" (p. 402) and "except for the
   noisy samples surrounded by the majority samples, RSMOTE will not filter any other sample" (p. 408). Both
   contrast RSMOTE's seed selection with other pre-processing variants (which samples are used to generate);
   points 1 to 3 settle the question.

From the authors' code (`ref/RSMOTE/RSMOTE_V8.py`): `_div_data` builds `self.train` from all rows before
the filter; the filter (lines 77-85) only replaces `self.train_less`, the seed set; the result is
`np.vstack((self.train, synthetic))` (lines 194, 199). The noisy rows are returned unchanged. The code also
keeps them out of the relative-density neighbors (see difference D5 below).

Empirically (VALIDATION.md, Section 6): deleting the flagged rows as well moves RSMOTE's results by at most
0.02 at c = 0 and raises its precision at c = 0.3, whereas the paper's Table 4 (p. 411) shows RSMOTE with low
precision and high recall under noise and blames the low precision on not filtering (p. 412). The published
numbers fit the reading that the noise stays in the data.

Suggested wording for the survey's account: "Minority points whose k neighbors are all majority are
excluded from the seeds as noise (they stay in the training data, pp. 412, 416)" instead of "are dropped as
noise".

## 2. Choices the paper leaves open (each marked `CHOICE` in rsmote.py)

| ID | Choice in rsmote.py | Basis | Authors' code |
|--|--|--|--|
| C1 | Default `k_neighbors=5`. | The paper tunes k over {3, 5, 20} (p. 409) and names no default. | default k=5 |
| C2 | Default `ir=1` (balance). | IR is an input of Alg. 1; the binary experiments do not state it; Sec. 4.3.3 (p. 414) balances to the largest class. | default ir=1 |
| C3 | N = int(\|Q\|/IR) - \|P\| (truncation). | Alg. 1 line 2 gives a real number for IR other than 1. | truncates |
| C4 | A class with k or fewer members uses k = \|P\| - 1 everywhere; a class with one member gets no synthetic rows (warning). | The paper assumes \|P\| > k. | same reduction |
| C5 | Exactly k neighbors; ties in the order the search returns them; the query point is removed by index, so an exact duplicate of it counts as a neighbor at distance 0. | Def. 1 (p. 401) keeps every point tied with the k-th distance. | drops the first column, which is a duplicate rather than the point itself when duplicates exist |
| C6 | HONk(p) (relative density) is searched in the whole minority class P of the training data, noisy points included. | Def. 2 (p. 401) uses D+, the class; Step 1 does not say the noisy points leave D+ (and they stay in D, Section 1). | searches in P' (noise removed) |
| C7 | If all k homogeneous distances are 0, RD = +inf (kept in `info_`) and enters the 2-means as the largest finite RD; if both sums are 0, RD = 1. | Eq. (2) is undefined there. | caps every RD at 100 (both cases become 100) |
| C8 | 2-means is the exact optimum of the 1-D within-cluster sum of squares (best split of the sorted values), deterministic. | The paper names "2-means" without initialization or restarts. | `sklearn.cluster.k_means` (k-means++, unseeded) |
| C9 | If a 2-means cluster has fewer than 2 seeds (or all RD are equal, or there are fewer than 2 seeds), P' is kept as one cluster. | A single seed cannot interpolate "within" its cluster; the paper does not cover it. | same rule |
| C10 | N_j and N_i are rounded by the largest remainder method, so they add up to N exactly. | Lines 17 and 21 give real numbers. | floors, then an inexact remainder rule (D14) |
| C11 | Populate's nnarray: the k nearest seeds of x_i inside its own cluster P'_j (all other members if the cluster has k or fewer); partner uniform among them; gap uniform on [0, 1). | "generate new samples within each cluster" (p. 402, also p. 398); Populate of SMOTE [11]. | same |
| C12 | Fewer than 2 non-noisy minority points: no synthetic rows for that class (warning). | Not covered; interpolation needs two seeds. | would raise an error |
| C13 | Several classes: each class smaller than the largest is oversampled against the largest class only (D = Y_t u Y_s), from the original data each time, to \|Y_s\|/IR rows; ties for the largest class: the first label in sorted order is Y_s and classes of that size are not oversampled. | "call RSMOTE to balance the class Y_t with respect to class Y_s" (p. 414). One-against-the-rest is the other reading. | same pairing (but ignores k and ir, D17) |
| C14 | Exact Euclidean distances from a ball tree, so duplicates are at distance exactly 0. | Euclidean distance (p. 412). | scikit-learn default search |
| C15 | Output order: original rows in their order, then synthetic rows by class label, cluster A before B, seed order. | Interface of the brief. | majority rows first, then minority, then synthetic |
| C16 | One `RandomState` for the whole call: a uniform neighbor index and a uniform gap per synthetic row. | Populate draws both at random. | reseeds Python's `random` at every seed (D16) |

## 3. Differences between the paper and the authors' code (RSMOTE_V8.py)

Read statically; the code was not run. Line numbers refer to `ref/RSMOTE/RSMOTE_V8.py`.

* D0. Imports. The file imports `base_sampler` and `多分类相对密度调用版` ("multi-class relative density,
  calling version"), which are not in the repository, and `sklearn.utils.safe_indexing`, which scikit-learn
  removed in 0.24 (it fails on the installed 1.9.1). A parse of the file (no execution) shows that no name it
  uses comes from the two missing modules: their `import *` lines are dead, so nothing had to be completed
  from them; every step is written here from the paper.
* D1. m (noise test and weights) is counted among a fixed 5 nearest neighbors (`n_neighbors=6` minus the
  point itself, line 23) whatever k is. Paper: the same k (Step 1).
* D2. Noise test `num_maj < self.k` keeps a point (line 82), with m from 5 neighbors: for k = 5 this is the
  paper's rule; for k = 3 it removes points with at least 3 majority points among 5 neighbors; for k = 20 it
  removes nothing (and see D11).
* D3. Self-exclusion by position (drop the first returned neighbor, lines 24 and 185): with exact duplicates
  the point itself can stay in its own list.
* D4. HENk uses k + 1 majority neighbors (line 86); paper: k.
* D5. HONk is searched in P' (noise removed, lines 88-89); paper: D+ (C6).
* D6. RD capped at 100 (line 97); zero homogeneous sums give 100 (Python `min(100, nan)` is 100, so 0/0 also
  gives 100). Not in the paper.
* D7. 2-means by `k_means(..., n_clusters=2)` without `random_state` (line 116): not reproducible run to run
  in principle (in 1-D it nearly always gives the same split); the clusters are read off the RD-sorted list
  at the first label change (lines 117-125), and all-equal RD values would raise IndexError there.
* D8. If a cluster has fewer than 2 points, no split (lines 128-134); the paper does not say (C9 adopts it).
* D9. Weight normalizer: `sum_0 += (5 - m) / self.k + 1` (lines 138-141), that is (5 - m)/k + 1 by operator
  precedence, summed over both clusters; paper: the sum of (k - m)/(k + 1) over the cluster (line 20).
* D10. `sum_1` is never accumulated (both loops add to `sum_0`), so `ratio[1] = 0`, and for the second
  cluster `x / ratio[i]` (line 176) divides a Python float by 0: ZeroDivisionError whenever both clusters
  have at least 2 points, which is the method's normal case. The published file therefore cannot have
  produced the paper's results in that case.
* D11. Weights are the hard-coded list `[5/6, 4/6, 3/6, 2/6, 1/6]` indexed by m (line 146), that is
  (k - m)/(k + 1) for k = 5 only; with k = 20 a seed with m = 5 would index past the list (IndexError).
* D12. One-cluster case: N = int(|Q|/IR - |P'|) (line 167) counts P' rather than P, so the output exceeds
  the ratio IR by the number of noisy points; paper: |P| (Alg. 1 line 2).
* D13. Two-cluster case: N = |Q| - |P| (line 148) ignores IR; N_A = int(|P'_A|/|P'| N), N_B the rest
  (lines 170-173), which matches line 17 of Alg. 1 for IR = 1.
* D14. Per-seed counts are `int(w(m) / ratio * N_j)` (line 176) with the normalizer of D9, so they do not
  add up to N_j; the shortfall `reminder` is computed from the five per-m values, not from the seeds
  (line 177), gives one extra row to the first `reminder` seeds in descending RD order, and generation stops
  at N_j rows (line 211).
* D15. The synthetic array is preallocated with zeros (line 183). When the counts of D14 add up to fewer than
  N_j, the unfilled rows stay all-zero and are returned as minority samples. With k = 5 the counts give at
  most 5/12 of N_j plus one row per seed, so zero rows remain whenever N_j exceeds about 12/7 |P'|, that is
  for imbalance ratios above about 2.7 at IR = 1 (for example |P'| = 50 seeds with m = 0 and N_j = 200 give
  100 real rows and 100 zero rows). Since the two-cluster case stops at D10, the published file either
  stops with an error or, for such ratios, returns zero rows.
* D16. `_populate` calls `random.seed(self.random_state)` for every seed (line 205): with a fixed seed every
  seed draws the same sequence of neighbor positions and gaps. `np.random.seed` (line 188) has no effect on
  the generation, which uses Python's `random`.
* D17. `RSmoteKClasses` (multiclass) builds `RSmote(data_train, random_state=...)` without passing its own
  `ir` and `k` (line 248), so they are always 1 and 5; it pairs each smaller class with the largest class,
  as C13 does.
* D18. Interface: labels in column 0 of one array; the output puts the majority rows first, then the
  minority rows, then the synthetic rows, so the original row order is lost.

What the code confirms about the paper: N from |Q| and the full |P| (two-cluster case), the noise test for
k = 5, RD as the heterogeneous over the homogeneous distance sum (Eq. 2), 2-means on RD with the safe cluster
taken as the one with larger RD, cluster shares proportional to cluster sizes, weights (k - m)/(k + 1) for
k = 5, interpolation inside each cluster with SMOTE's Populate, and noisy rows kept in the output.

## 4. Points a person should check against the PDF

* Step 3 and Alg. 1 line 19 (pp. 402-403): the weight is (k - m)/(k + 1); the text file loses the fraction,
  the PDF at 220 dpi shows it clearly. Alg. 1 line 6 prints "if m <- k" for m = k (a typo; Step 1 says
  "If m = k").
* Alg. 1 line 2 (p. 403): N <- |Q|/|IR| - |P| (bars around IR are harmless).
* Definition 2 (p. 401): HONk(p) is defined over D+, the class; nothing restricts it to P' (C6).
* Sec. 4.3.2 (p. 408) states a 75%/25% split, but the recall values of Table 3 (p. 410) for ecoli, heart and
  iris cannot be averages over 25 runs with 13, 30 and 13 test minority samples (25% of 52, 120 and 50); they
  fit 11, 24 and 10 (20%). Wine, vehicle and pima fit both. See VALIDATION.md.
* Table 3 (p. 410): RSMOTE is far above every other method on several small sets (for example ecoli AUC
  0.996 against at most 0.885, heart 0.984 against at most 0.840, pima 0.886 against at most 0.799, wine 1.000
  on all five measures). VALIDATION.md compares these with the rerun of the stated protocol.

## 5. Notes on the survey's account (`accounts.tex`, item "RSMOTE (2021)")

* "dropped as noise": see Section 1 (excluded from the seeds; kept in the training data).
* "Defs. 1-3, pp.401-402": Definitions 1-3 are all on p. 401; Steps 1-3 are on p. 402.
* "Sec. 4.3.3, p.413" (and "pp.413-414" in `\classev`): Sec. 4.3.3 starts on p. 414 and runs to p. 416; the
  multiclass procedure is on p. 414.
* "Each group gets a share matching its size, and within a group each seed gets a weight (k-m)/(k+1)": agrees
  with Alg. 1 lines 17-21.
* "Points are made with SMOTE's own routine, uniform on the segment, once before training": agrees (Populate,
  line 22; within the seed's own cluster).

## 6. Notes for the rerun

* With `k_neighbors=5`, a minority class whose points all have 5 majority nearest neighbors (or that has
  fewer than two other points) gets no synthetic rows: RSMOTE then returns the input unchanged and warns (C4,
  C12). This can happen on tasks with very few, scattered minority examples; the test with 7 scattered
  minority points shows it.
* The paper's grid for k is {3, 5, 20} (p. 409); the default here is 5 (C1).
* Cost: three k-nearest-neighbor searches over the training set for the minority points plus one per
  cluster, and a sort of |P'| values; no iterative fitting. Measured on one core: 2.6 s for KEEL magic
  (19,020 rows), 0.1 s for page-blocks0 (5,472 rows), 1.9 s for letter with all 26 classes balanced.
