# SMOM implementation notes (WP6.8)

Method: SMOM, Zhu, Lin and Liu, "Synthetic minority oversampling technique for multiclass imbalance
problems", Pattern Recognition 72 (2017) 327-340, doi 10.1016/j.patcog.2017.07.024.

Files in this folder:

| File | Content |
|:--|:--|
| `smom.py` | `SMOM` sampler, `fit_resample(X, y)`; docstring maps every step to the paper |
| `test_smom.py` | 10 quick checks (`python3 -I test_smom.py`, about 1 s) |
| `validate_smom.py` | validation experiment (`python3 -I validate_smom.py`, about 2 minutes) |
| `VALIDATION.md`, `validation_results.json` | validation report and its numbers |

Page references: "p. NNN" is the journal page; "Supp. p. N" is the page of the 26-page supplementary
PDF (`SMOM-2017__supp1.pdf`).

## Sources read

* Main text `SMOM-2017__main.txt`, read in full. The main PDF `SMOM-2017__main.pdf` was checked on
  11 November 2026: its title page is the SMOM paper (Pattern Recognition 72, 327-340), not the INOS
  paper of the earlier copy. Algorithm 1 (p. 330), Algorithm 2 (p. 331), Eq. (2) with the entropies
  (p. 332) and Table 2 (p. 335) were read from the rendered PDF pages because the text file garbles
  them.
* Supplement text `SMOM-2017__supp1.txt`, read in full, and its PDF for page numbers and tables
  (Algorithm S1 on Supp. p. 3; Tables S3 to S10 on Supp. pp. 7 to 14, one table per page; S13 on
  Supp. p. 17).
* The survey's account (`v08/supplement/gen/accounts.tex`, item SMOM (2017)), as orientation only.
* No author code: the brief lists SMOM among the methods without a usable public implementation.

## Paper step to code

| Paper | Code (`smom.py`) |
|:--|:--|
| Classes to oversample and zeta: "All classes are oversampled until they contain as many instances as the largest one" (p. 335) | `_n_synthetic` |
| Minority and majority classes by the mean class size M/L (p. 334) | `fit_resample` (`is_minority`) |
| Standardized Euclidean distance (p. 335) | `_metric_space` |
| k reset to class size minus one for small classes (p. 337) | `_oversample_class` |
| Alg. 1 Step 1 and Step 2 (p. 330) | `_oversample_class`, `_neighbors` |
| Alg. 1 Step 3, Alg. 2 NBDOS, Definitions 1-2 (pp. 330-331) | `_nbdos` |
| Alg. 1 Step 4 | `outstanding = cl != 0` |
| Alg. 1 Step 5.1, 5.2, 5.3; two-round filtration (Sec. 3.2.1, p. 333); dPN (Supp. Alg. S1, Supp. p. 3) | `_direction_probabilities`, `_pn_weights` |
| Eq. (2) and the entropies E_mi, E_ma (p. 332) | `_eq2`, `_normalized_entropy` |
| Alg. 1 Step 6 (Sec. 3.2.2, pp. 333-334) | `_direction_probabilities` |
| Alg. 1 Step 7 (Sec. 3.3, p. 334) | `_oversample_class` |
| Alg. 1 Step 8 and Eq. (1) (p. 328) | `_oversample_class` |

## Choices (each marked `CHOICE:` in `smom.py`)

1. **Entropy sign.** The paper prints E_mi = (sum p log p)/Z_mi with no minus sign (p. 332), which
   lies in [-1, 0]; the text says E_mi ranges from 0 to 1 and grows with the number and evenness of
   the minority classes (pp. 332-333). The usual entropy -sum p log p, divided by log|miC|, is used.
2. **Entropy of a group with fewer than two classes, or with no instance in the ball:** 0 (the
   normalizer log 1 = 0 is undefined). This is the two-class case: E_mi = E_ma = 0.
3. **A class whose size equals M/L exactly** counts as a majority class (the paper names only
   "greater" and "smaller" than M/L, p. 334). Irrelevant for two unequal classes.
4. **Several classes:** each class is oversampled from the original data D; synthetic instances of
   one class are not added to D before the next class. Classes run in ascending label order with one
   random generator. The paper does not say (Alg. 1 takes "the whole multiclass imbalanced data" D).
5. **Standardized distance:** standard deviations with ddof = 1 over all rows passed to
   `fit_resample`; a constant feature keeps scale 1.
6. **A class with one instance** has no neighbor; it is replicated (its only direction is itself,
   as Step 6.1 would give).
7. **k reset** (k1 = min(12, n_c - 1)): the paper states it in Experiment 2 "for all compared
   algorithms" (p. 337); applied always. k2 is capped at n - 1 for tiny data.
8. **Step 7 remainder:** the zeta mod n_c extra instances go to a random subset of the class.
9. **Step 8 draws** are independent, with replacement ("repeat 1) and 2) x^i.g times").
10. **Self and ties in neighbor search:** a point is excluded from its own neighbor lists by index
    (exact duplicates of it remain neighbors); ties in distance are broken by the lower row index.
11. **Soft core rule.** Definition 1 (p. 330): soft core if |Tem|/k2 >= rTh. Alg. 2 line 5 (p. 331)
    prints round(|Tem|/k) >= rTh, which, with rounding to an integer, makes rTh irrelevant
    (|Tem| >= k/2 for any rTh in (0, 1]) and contradicts Supp. Sec. 3 (Supp. p. 5: "The higher rTh
    will tougher the condition"). Definition 1 is the default; `soft_core_rule="round"` gives the
    literal reading. With k2 = 8 and rTh = 5/8 the two readings need 5 and 4 class-c neighbors. The
    validation favors Definition 1 slightly (vowel5 MG 0.7781 against 0.7840; paper 0.7783).
12. **NBDOS visiting order:** soft cores in input order, `expandCluster` first in, first out. Order
    only decides which cluster claims a non-core instance reached by two clusters.
13. **Order of trapped instances** (input order) decides only whether Step 5.2 copies a weight or
    Step 5.3 computes it; the PN ball is the same seen from both ends, so the value is the same except
    for distance ties at exactly r_k1.
14. **Scope of T in Step 2.2.** "Find the nearest k3 instances from x^i in S^~c; during this process,
    choose out those instances, T, ... no larger than x^i.r_k1" could limit T to the k3 nearest
    other-class instances. Sec. 3.2.1 (p. 333, Fig. 4a) says the first filtration keeps all instances
    within r_k1 and only drops instances that cannot lie in a PN neighborhood, so T holds every
    other-class instance within r_k1. The k3-limited reading would cap the count of other-class
    instances near a minority point at 12 and make dense regions look cleaner.
15. **Ball test tolerance:** dPN keeps a point when its distance to the midpoint is at most
    d/2 (1 + 1e-9) + 1e-12, so that points exactly on the sphere (for example, an other-class duplicate
    of x^i) are kept despite rounding.

Not choices but easy to miss when reading the paper quickly:

* **Placement (Eq. 1, p. 328):** gamma is a vector of independent U[0, 1] numbers, one per feature,
  so a synthetic point falls in the axis-parallel box spanned by x^i and x^j, not on the segment
  (imbalanced-learn's SMOTE uses one gap per point). Figs. 1a and 2a draw these boxes as the
  "generalization regions". The paper writes SMOTE itself the same way.
* **Replication (Step 6.1):** a trapped instance none of whose PN neighborhoods holds class c only
  gets its own direction with weight 1 + w1/e, the largest possible weight; drawing it returns x^i
  exactly. Expect exact copies of minority rows among the synthetic rows on overlapping data.
* **Step 5.1 assumes, does not check:** if x^j is outstanding and x^i is in x^j's k1 list, the
  direction gets the clean weight 1 + w1/e without looking at the ball.
* **gamma_c in Eq. (2)** counts x^i and x^j themselves (dPN starts from N_PN = {x^i, x^j}), so it is
  at least 2.

## Two-class behavior (the rerun's tasks)

* Synthetic rows: n_majority - n_minority, all of the minority label, after the original rows.
* Weight of a direction with g_ma majority and g_c class-c instances in its ball:
  exp(-w2 r1 g_ma / g_c) + w1 exp(-g_c / (g_ma + g_c)); clean ball: 1 + 0.2/e = 1.0736; it falls to
  about 0.2 as g_ma grows.
* With nTh = 10, a minority class of fewer than 10 training rows has no outstanding instance: all
  its rows are trapped and use weighted directions. With 7 minority rows k1 = 6.
* **Metric, for the rerun protocol to decide.** Default `metric="seuclidean"` follows the paper.
  If the caller z-scores the features on the same training data, this equals plain Euclidean
  distance up to one common factor, which does not change SMOM's output (tested). If the caller
  min-max scales, the two differ; pass `metric="euclidean"` to give SMOM the same geometry as the
  other methods.
* Run time: about 12 s for 56,000 rows x 12 features with 16,000 minority rows; memory is bounded by
  distance blocks of 4 million entries.

## To check against the PDF

1. Eq. (2), p. 332, as read from the rendered page:
   sw = 1/exp(r1 g_mi/g_c + r2 E_mi + w2 (r1 g_ma/g_c + r2 E_ma)) + w1 exp(-g_c/(g_ma + g_mi + g_c)).
2. The missing minus sign in E_mi and E_ma (p. 332, right column).
3. Alg. 2 line 5 `round(|Tem|/k) >= rTh` (p. 331) against Definition 1 (p. 330).
4. Alg. 1 Step 5.1 (p. 330): "If x^j in Oi^c and x^i in x^j.N^c_k1, then x^i.sw(x^j) <- 1 + w1/e".
5. **Supp. Tables S4, S6, S8 and S10 (Supp. pp. 8, 10, 12, 14) have their "NB" and "MLP" headers
   swapped** relative to the main paper's Table 2 (p. 335) and Supp. Table S13 (Supp. p. 17); a
   Weka-equivalent NB baseline confirms that the block headed "MLP" there is NB (VALIDATION.md).
   Anyone citing per-data-set NB or MLP values from S4 to S10 should use the opposite block.
6. Table 1 (p. 334) class descriptions are unreliable: vehicle is described as 'DH'/'SL'/'NO' (not
   vehicle classes; sizes 199/429/218 fit van / saab and opel / bus); ecoli lists M = 327 but its
   class sizes sum to 307 (and IR 7.86 fits the four sizes); housing10 lists 10 sizes but 9 labels,
   pendigits 5 sizes but 4 labels, wine-red 4 sizes but 5 labels; vowel7's printed IR 15.00 does not
   fit its sizes (Eq. (3) gives 12.00) nor any grouping of the eleven vowel classes into seven.

## For the survey's account (accounts.tex, item SMOM (2017))

* The account says the main PDF in Drive held the INOS paper and that it was read from the
  supplement; the corpus PDF is now the SMOM paper (title page checked), and Eq. (2), the weight,
  is in the main paper (p. 332). The account cites "Algorithm S1; Supp. Sec. 3" for the weight:
  Algorithm S1 only collects the instances in the ball, and Supp. Sec. 3 explains the parameters.
* The account does not mention Step 6.1 (trapped instances without a clean direction replicate
  themselves) or the per-feature gap (box placement); both affect what SMOM generates.
* "neighbors are searched over all classes": true of the k2 neighbors (NBDOS) and the PN balls; the
  k1 directions are same-class neighbors.
* "oversampled until all classes have the same size" is also stated in the main text (p. 335), not
  only in Supp. Sec. 7.
