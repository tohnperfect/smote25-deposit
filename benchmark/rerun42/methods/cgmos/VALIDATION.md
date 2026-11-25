# CGMOS validation (WP6.8)

**Verdict: not reproduced.** Paper: CGMOS AUC 0.651 on Haberman (Table 3, p. 1629, AUC averaged
over the six base classifiers). This implementation, main reading of the protocol: **0.688**
(difference +0.037; standard error of my estimate about 0.010). Four other readings of details the
paper leaves unstated give 0.660 to 0.671 (+0.009 to +0.020). In every reading CGMOS equals SMOTE
to within 0.003 (paired over the same folds), while the paper puts CGMOS 0.051 above SMOTE on
Haberman (0.651 against 0.600). As printed, the method cannot produce that gap: its seed
probabilities are within 0.1% (total variation) of SMOTE's uniform ones, and 99.6% of its
synthetic rows are identical to those of a uniform-seed run drawn from the same random stream
(NOTES.md, section 1).

Script: `validate_cgmos.py`. Raw output: `results/` (`haberman_*.json` per protocol reading,
`fig1_curve.json`, `seed_uniformity.json`, run logs).

## 1. The number and the data

* Paper value: Table 3 (p. 1629), row Haberman: CGMOS 0.651, Original 0.623, Dup 0.577, SMOTE
  0.600, B-SMOTE 0.593, MWMOTE 0.594, ADASYN 0.587, RAMOboost 0.586. The caption says the AUC "is
  averaged over all 6 base classifiers". Per-classifier values for Haberman are not printed, so
  only the six-classifier average can be compared.
* Data: KEEL `haberman.dat` (keel-ds 0.2.5, `src/kd/keel_ds/data/imbalanced/raw/`): 306 rows, 3
  features, 81 positive and 225 negative. Table 1 (p. 1627) lists Haberman with 306 samples, 3
  features and ratio 0.36 (= 81/225), so this is the same UCI data set. Minority = positive.

## 2. Protocol

Stated by the paper, and followed:

* 10 rounds of 10-fold cross-validation (Sec. 4.5, p. 1627). Here: stratified, shuffled folds,
  round r uses seed r (r = 0..9).
* Six base classifiers (Sec. 4.3, p. 1626): b-kde (the Bayes classifier of Sec. 2), knn, svm with
  RBF kernel, a neural network with one hidden layer, a random forest of C4.5 trees, Adaboost.M1.
* "All hyper-parameters of the classifiers tested were determined by cross validation to ensure
  the best performance of each method" (p. 1626).
* Measure: AUC (Sec. 4.4, p. 1627), averaged over the six classifiers (Table 3 caption).

Not stated, and the reading used (main reading first):

| Detail | Main reading | Other readings tried |
|:--|:--|:--|
| Feature scaling | z-score fitted on the training fold | none; min-max |
| Where oversampling happens | training fold only (and inside every inner tuning fold) | |
| Hyperparameters | inner stratified 3-fold CV on the training fold, AUC, over the grids below ("tuned") | one default setting per classifier ("fixed") |
| AUC averaging | AUC per test fold, mean over the 100 folds | one AUC per round on the pooled test scores (in parentheses below) |
| Classifier implementations | scikit-learn 1.9.1 (below) | |
| CGMOS settings | defaults of `cgmos.CGMOS`: sigma = 1, q = 5, k = 5, balanced classes | sigma 0.5 and 2, q = 10, normalized kernel, all-class bandwidth neighbors (fixed protocol) |
| SMOTE baseline | imbalanced-learn 0.14.2 `SMOTE(k_neighbors=5)`, balanced | |
| Random seeds | sampler and classifiers use 1000 * round + fold | |

Classifiers, tuning grids and the fixed setting:

| Classifier | Implementation and score used for AUC | Grid ("tuned") | Fixed setting |
|:--|:--|:--|:--|
| b-kde | Eq. 3 likelihoods with Eq. 4 bandwidths (as in `cgmos.py`), priors n_l / n; log posterior odds | sigma {0.5, 1, 2} x q {5, 15} | sigma 1, q 5 |
| knn | `KNeighborsClassifier`; class probability | k {5, 11, 21, 31} | k 5 |
| svm | `SVC(kernel="rbf")`; decision function | C {0.1, 1, 10} x gamma {0.1, 0.3, 1} | C 1, gamma "scale" |
| nn | `MLPClassifier(solver="lbfgs", max_iter=500)`, one hidden layer; class probability | units {5, 20} x alpha {0.01, 1} | 10 units, alpha 1e-4 |
| rf | `RandomForestClassifier(50 trees, criterion="entropy")` for "C4.5 trees"; class probability | min_samples_leaf {1, 5, 10} | 1 |
| Adaboost.M1 | `AdaBoostClassifier` (SAMME, which is AdaBoost.M1 for two classes), 50 rounds of trees; decision function | tree depth {1, 3} x learning rate {0.5, 1} | depth 1, rate 1 |

One reading can be ruled out from the paper itself: AUC computed from hard labels. For b-kde on
the original data Table 2 (p. 1628) prints minority recall 0.033 and majority recall 0.995, which
would give an AUC of (0.033 + 0.995) / 2 = 0.514, but the printed AUC is 0.797. The AUCs are
therefore computed from scores, as here.

## 3. Results

Six-classifier AUC, mean over 100 test folds (pooled per round in parentheses):

| Protocol reading | Original | SMOTE | CGMOS | CGMOS minus paper (0.651) | CGMOS minus SMOTE, paired over folds |
|:--|:--|:--|:--|:--|:--|
| tuned, z-score (main) | 0.694 (0.684) | 0.687 (0.674) | **0.688** (0.673) | **+0.037** (+0.022) | +0.0007 (se 0.0026) |
| tuned, no scaling | 0.682 (0.673) | 0.674 (0.661) | 0.671 (0.658) | +0.020 (+0.007) | -0.0027 (se 0.0032) |
| fixed, z-score | 0.658 (0.653) | 0.660 (0.655) | 0.661 (0.656) | +0.010 (+0.005) | +0.0005 (se 0.0030) |
| fixed, no scaling | 0.670 (0.663) | 0.662 (0.658) | 0.662 (0.658) | +0.011 (+0.007) | +0.0006 (se 0.0025) |
| fixed, min-max | 0.662 (0.657) | 0.659 (0.655) | 0.660 (0.656) | +0.009 (+0.005) | +0.0010 (se 0.0022) |
| **Paper, Table 3** | **0.623** | **0.600** | **0.651** | | **+0.051** |

Standard error of each six-classifier mean in the main reading: 0.010 (computed over the 100
folds, which are not independent within a round, so it is approximate).

Per classifier, main reading (the paper does not print these for Haberman):

| Classifier | Original | SMOTE | CGMOS |
|:--|:--|:--|:--|
| b-kde | 0.675 | 0.697 | 0.691 |
| knn | 0.681 | 0.662 | 0.657 |
| svm | 0.727 | 0.692 | 0.694 |
| nn | 0.694 | 0.680 | 0.680 |
| rf | 0.715 | 0.713 | 0.716 |
| Adaboost.M1 | 0.669 | 0.678 | 0.687 |

Readings of CGMOS's own settings, and a uniform-seed ablation (fixed protocol, z-score). The
ablation is `CGMOS` with every W(x_i) set to 1, i.e. SMOTE drawn from the same random stream:

| Sampler | Six-classifier AUC | Pooled | TV distance of the seed distribution from uniform (mean over folds) | Synthetic rows identical to the uniform-seed run (mean, minimum over folds) |
|:--|:--|:--|:--|:--|
| Original | 0.658 | 0.653 | | |
| SMOTE (imbalanced-learn) | 0.660 | 0.655 | | |
| CGMOS (defaults) | 0.661 | 0.656 | 0.00079 | 99.6%, 97.7% |
| CGMOS with uniform seeds (ablation) | 0.661 | 0.656 | 0 | 100% |
| CGMOS, normalized kernel | 0.660 | 0.655 | 0.00027 | 99.8%, 98.4% |
| CGMOS, all-class bandwidth neighbors | 0.661 | 0.656 | 0.00037 | 99.8%, 98.4% |
| CGMOS, sigma = 0.5 | 0.659 | 0.654 | 0.00102 | 99.4%, 96.2% |
| CGMOS, sigma = 2 | 0.661 | 0.656 | 0.00034 | 99.8%, 98.4% |
| CGMOS, q = 10 | 0.661 | 0.656 | 0.00054 | 99.8%, 97.7% |

CGMOS and the ablation give identical six-classifier AUCs in 60 of the 100 folds (identical
training data); over all folds the mean difference is -0.0008. In the main reading the weights
lie in [0.989, 1.0007] on every training fold.

## 4. Reading of the result

* The CGMOS number itself is within 0.01 of the paper's in the readings without tuning, but those
  readings also move Original and SMOTE to about 0.66, whereas the paper has them at 0.623 and
  0.600. Every reading shifts all methods together; none reproduces the paper's ordering
  (CGMOS ahead of Original by 0.028 and of SMOTE by 0.051).
* The main reading follows the paper's statement that hyperparameters were tuned by cross
  validation, and it gives 0.688. I label the validation "not reproduced" on that reading, which
  was fixed before the runs. The paper's lower values for all methods suggest a weaker or
  differently configured set of classifiers (for example Weka defaults), which the paper does not
  describe.
* The CGMOS-SMOTE difference is the part that matters for the survey, and it is structural, not
  a protocol effect: with Eq. 6 as printed, CGMOS changes SMOTE's seed probabilities by less than
  1% each, so no protocol can make the two differ by 0.05 AUC on this data.

## 5. Figure 1 (p. 1625), qualitative (Part B)

Figure 1 panel 3 plots, on a 1e-4 scale, the relative certainty change of all samples
(W(x) - 1) when one minority example is moved along the center line of two Gaussian classes
(2000 majority, 400 minority). The Gaussian parameters are not given; I estimated them from the
figure (minority centered near (1, 5), majority near (7.3, 5), narrower in x). Values read off
the figure (x 1e-4): 2.4 at x = -2, 1.2 to 1.5 for x in [-1, 1], 2.8 at x = 2, a peak of 5.2 at
x = 3.75, below zero from about x = 4.2.

* Default reading: W(x) - 1 is about 0 for x <= 3, rises to a peak of 0.088e-4 at x = 4.25 and is
  negative from x = 4.5. The rise on the minority side of the overlap followed by a plunge is
  reproduced, near the right place; the magnitude is about 60 times smaller and the plateau deep in
  the minority class is absent.
* A sweep of 40 readings (sigma 0.5 to 10, q 5 and 20, both kernel normalizations, both
  bandwidth neighbor sets) never gives both the plateau and the peak (`results/fig1_curve.json`).
  The likely cause is that my estimate of the figure's data is off, so this check is weak.
* What does hold: in the default reading the weights of the 400 simulated minority points lie in
  [0.9984, 1.00001] (total-variation distance from uniform 0.000006); across the sweep the
  positive values of W(x) - 1 never exceed 1.5e-4; and the figure itself plots positive values of
  at most 5.2e-4 (its axis cuts off values below zero). On the paper's own scale, then, the seed
  probabilities W / z differ from uniform by a fraction of a percent.

## 6. Seed-distribution check on other data sets (Part C)

On Haberman, TAE (class 1 against the rest), Contraceptive (class 2 against the rest),
movement_libras (class 1 against the rest, 90 features) and yeast4, each z-scored, with five
readings (default, normalized kernel, all-class bandwidth neighbors, sigma = 3, and a
leave-one-out version of Eq. 3), the largest total-variation distance between CGMOS's seed
distribution and the uniform one is 0.0025 (`results/seed_uniformity.json`).

## 7. Reproducing

```
cd /home/claude/work/rerun42/methods/cgmos
python3 -I validate_cgmos.py --parts A --protocol tuned                    # main reading
python3 -I validate_cgmos.py --parts A --protocol fixed                    # CGMOS readings, ablation
python3 -I validate_cgmos.py --parts A --protocol tuned --scaling none --samplers Original,SMOTE,CGMOS
python3 -I validate_cgmos.py --parts A --protocol fixed --scaling none --samplers Original,SMOTE,CGMOS
python3 -I validate_cgmos.py --parts A --protocol fixed --scaling minmax --samplers Original,SMOTE,CGMOS
python3 -I validate_cgmos.py --parts BC                                    # Figure 1, seed check
```

Times on the shared 2-CPU machine: the tuned protocol took 5 to 7 minutes per sampler while other
jobs were running and about 2.5 minutes per sampler when the machine was idle; the fixed protocol
takes 10 to 70 seconds per sampler; Parts B and C take about 20 seconds.
