# RSMOTE validation (WP6.8)

**Verdict: not reproduced.** Headline number: pima, AUC, Table 3 (p. 410, label noise c = 0). The paper prints
**0.886** for RSMOTE; this implementation gives **0.781** under the stated protocol (difference -0.105). On the
same data and protocol, the paper's NONE and SMOTE rows are reproduced within 0.02 on all five measures (AUC
0.780 against 0.797, and 0.778 against 0.790), so the protocol matches on pima. No reading of the unstated
details brings RSMOTE above 0.796 (only the leak diagnostic, which breaks the stated protocol, reaches 0.847).
On all five data sets the paper's RSMOTE values exceed ours by
0.03 to 0.14 AUC, and the paper's RSMOTE gain over SMOTE (up to +0.16 AUC at c = 0) is about zero here.

Script: `validate_rsmote.py` (10,000 classifier runs, 18 min on two shared cores); every run is in
`validation_raw.csv`, every table in `validation_output.txt` (`python3 -I validate_rsmote.py --summarize-only`
reprints them). The noise-deletion diagnostic (Section 6) is in `validation_raw_dropnoise.csv` and
`validation_output_dropnoise.txt`.

## 1. What is compared

* Paper values: Table 3 (c = 0, p. 410) and Table 4 (c = 0.3, p. 411), the RSMT. column, all five measures
  (Precision, Recall, AUC, F1, G-mean of the minority class; Eqs. 3-6, p. 404). Each value is the average
  "across five classifiers" (p. 409) over five repetitions. The NON. and SMT. columns are compared too, as a
  check on the protocol.
* Data: the five Table 2 sets (p. 409) whose public copies match it exactly in size, class counts and
  dimension, from the local KEEL files: ecoli (KEEL ecoli2, pp against the rest: 336, 284, 52, 7), pima (768,
  500, 268, 8), heart (270, 150, 120, 13), vehicle (KEEL vehicle0, van against the rest: 846, 647, 199, 18),
  wine (class 2 against the rest: 178, 107, 71, 13). The other 22 sets cannot be matched: 18 were undersampled
  at random by the authors (p. 408); breast_tissue2 (88 rows, 9 features) is not among the local files and is
  smaller than the 106-row UCI Breast Tissue set, by a selection the paper does not describe; for iris, segment
  and libra the paper does not say which classes form the minority.

## 2. Protocol

Stated in the paper and followed (Sec. 4.3.2, pp. 408-409):

* random 75%/25% split with the classes divided separately (scikit-learn `train_test_split`, stratified,
  `random_state` = repetition 0 to 4);
* label noise on the training part only: c|P| minority labels flipped to majority, then as many majority labels
  flipped to minority (pp. 408-409; unstated: we round c|P| and draw the second flip from the original
  majority rows);
* the oversampler sees the training part only (Algorithm 1 takes the "Training set D", p. 403);
* classifiers AdaBoost, LR, DT, KNN, GBDT with default parameters (scikit-learn 1.9.1; `random_state` =
  repetition for AdaBoost, DT and GBDT);
* k of the oversamplers enumerated over {3, 5, 20} "to obtain the best result" (p. 409); IR = 1;
* five repetitions, measures averaged over the five classifiers and the five repetitions.

Not stated; readings tried (the headline uses the first of each):

| Detail | Readings | Evidence |
|--|--|--|
| Feature scaling | none; min-max fitted on the training part | not mentioned |
| Test fraction | 0.25 (stated); 0.20 | Table 3's recall values for ecoli, heart and iris are not multiples of 1/(25 n) for the 25% counts n = 13, 30, 13 but are for the 20% counts n = 11, 24, 10; wine, vehicle and pima fit both (checked for all eight oversampler columns) |
| AUC | from predicted probabilities; from hard labels | the label reading is excluded by the paper's own NONE row for ecoli: recall 0.509 caps a label-based AUC at (0.509 + 1)/2 = 0.755, but Table 3 prints 0.829 |
| Best k | per data set and measure; per data set, measure and classifier; k = 5 fixed | "enumerated to obtain the best result" (p. 409) |
| Pipeline (diagnostic) | oversample the whole set, then split ("leak") | NOT the paper's protocol; shown only to see whether it explains the gap |
| RSMOTE reading (diagnostic) | flagged rows also deleted from the training data | NOT the paper's reading (NOTES.md, Section 1) |

RSMOTE itself runs with the defaults and choices C1 to C16 of NOTES.md; SMOTE is imbalanced-learn 0.14.2.

## 3. Results at c = 0 (Table 3, p. 410)

Stated protocol: 75/25, no scaling, AUC from probabilities, best k per data set and measure. Values are P, R,
AUC, F1, G-mean.

| data | method | paper | ours | ours minus paper |
|--|--|--|--|--|
| ecoli | RSMOTE | 0.893, 1.000, 0.996, 0.942, 0.988 | 0.762, 0.889, 0.948, 0.817, 0.916 | -0.131, -0.111, -0.048, -0.125, -0.072 |
| ecoli | SMOTE | 0.505, 0.673, 0.834, 0.558, 0.751 | 0.767, 0.889, 0.947, 0.812, 0.915 | +0.262, +0.216, +0.113, +0.254, +0.164 |
| ecoli | NONE | 0.667, 0.509, 0.829, 0.543, 0.679 | 0.851, 0.748, 0.951, 0.745, 0.825 | +0.184, +0.239, +0.122, +0.202, +0.146 |
| pima | RSMOTE | 0.714, 0.837, 0.886, 0.770, 0.825 | 0.620, 0.684, 0.781, 0.643, 0.720 | -0.094, -0.153, -0.105, -0.127, -0.105 |
| pima | SMOTE | 0.595, 0.700, 0.790, 0.643, 0.721 | 0.602, 0.681, 0.778, 0.637, 0.716 | +0.007, -0.019, -0.012, -0.006, -0.005 |
| pima | NONE | 0.682, 0.578, 0.797, 0.623, 0.700 | 0.664, 0.562, 0.780, 0.607, 0.687 | -0.018, -0.016, -0.017, -0.016, -0.013 |
| heart | RSMOTE | 0.942, 0.950, 0.984, 0.946, 0.951 | 0.771, 0.755, 0.848, 0.757, 0.782 | -0.171, -0.195, -0.136, -0.189, -0.169 |
| heart | SMOTE | 0.672, 0.833, 0.820, 0.743, 0.748 | 0.760, 0.755, 0.843, 0.755, 0.780 | +0.088, -0.078, +0.023, +0.012, +0.032 |
| heart | NONE | 0.691, 0.833, 0.833, 0.754, 0.762 | 0.770, 0.720, 0.842, 0.742, 0.772 | +0.079, -0.113, +0.009, -0.012, +0.010 |
| vehicle | RSMOTE | 0.918, 1.000, 0.996, 0.956, 0.985 | 0.864, 0.923, 0.970, 0.890, 0.937 | -0.054, -0.077, -0.026, -0.066, -0.048 |
| vehicle | SMOTE | 0.824, 0.975, 0.981, 0.892, 0.954 | 0.860, 0.928, 0.971, 0.890, 0.939 | +0.036, -0.047, -0.010, -0.002, -0.015 |
| vehicle | NONE | 0.922, 0.880, 0.978, 0.898, 0.926 | 0.898, 0.897, 0.975, 0.896, 0.931 | -0.024, +0.017, -0.003, -0.002, +0.005 |
| wine | RSMOTE | 1.000, 1.000, 1.000, 1.000, 1.000 | 0.903, 0.900, 0.948, 0.895, 0.910 | -0.097, -0.100, -0.052, -0.105, -0.090 |
| wine | SMOTE | 0.949, 0.973, 0.982, 0.961, 0.968 | 0.893, 0.893, 0.947, 0.890, 0.905 | -0.056, -0.080, -0.035, -0.071, -0.063 |
| wine | NONE | 1.000, 0.933, 0.985, 0.965, 0.966 | 0.901, 0.869, 0.946, 0.883, 0.900 | -0.099, -0.064, -0.039, -0.082, -0.066 |

How well the protocol matches, judged by the baselines: pima within 0.02 on every measure, vehicle within 0.05,
heart within about 0.1, wine below the paper (no scaling hurts KNN and LR here; min-max raises our values, see
below), ecoli far above the paper. Only pima and vehicle therefore test RSMOTE cleanly, and on both RSMOTE
falls short while the baselines agree.

RSMOTE AUC (and F1) under every reading of the unstated details, best k per data set and measure:

| data | paper AUC | 75/25 none | 75/25 min-max | 80/20 none | 80/20 min-max | paper F1 | 75/25 none | 75/25 min-max | 80/20 none | 80/20 min-max |
|--|--|--|--|--|--|--|--|--|--|--|
| ecoli | 0.996 | 0.948 | 0.948 | 0.959 | 0.960 | 0.942 | 0.817 | 0.825 | 0.837 | 0.842 |
| pima | 0.886 | 0.781 | 0.792 | 0.791 | 0.790 | 0.770 | 0.643 | 0.650 | 0.653 | 0.654 |
| heart | 0.984 | 0.848 | 0.873 | 0.845 | 0.865 | 0.946 | 0.757 | 0.794 | 0.747 | 0.789 |
| vehicle | 0.996 | 0.970 | 0.971 | 0.969 | 0.972 | 0.956 | 0.890 | 0.886 | 0.879 | 0.887 |
| wine | 1.000 | 0.948 | 0.976 | 0.951 | 0.976 | 1.000 | 0.895 | 0.951 | 0.883 | 0.946 |

On pima, choosing the best k per classifier as well adds at most 0.005 AUC (0.782, 0.795, 0.796, 0.791 in the
order above), and k = 5 fixed loses at most 0.002. The pima baselines stay within 0.025 of the paper on every
measure under all four readings (AUC: NONE 0.780 to 0.788 against 0.797, SMOTE 0.778 to 0.794 against 0.790).

The paper's claim is a large gain of RSMOTE over SMOTE. RSMOTE minus SMOTE (best k each; stated protocol), P, R,
AUC, F1, G-mean:

| data | paper | ours |
|--|--|--|
| ecoli | +0.388, +0.327, +0.162, +0.384, +0.237 | -0.005, +0.000, +0.001, +0.004, +0.002 |
| pima | +0.119, +0.137, +0.096, +0.127, +0.104 | +0.018, +0.004, +0.003, +0.005, +0.004 |
| heart | +0.270, +0.117, +0.164, +0.203, +0.203 | +0.011, -0.000, +0.005, +0.002, +0.002 |
| vehicle | +0.094, +0.025, +0.015, +0.064, +0.031 | +0.004, -0.005, -0.001, -0.000, -0.002 |
| wine | +0.051, +0.027, +0.018, +0.039, +0.032 | +0.010, +0.007, +0.001, +0.005, +0.005 |

## 4. Results at c = 0.3 (Table 4, p. 411)

Stated protocol, P, R, AUC, F1, G-mean:

| data | paper RSMOTE | ours RSMOTE | paper SMOTE | ours SMOTE |
|--|--|--|--|--|
| ecoli | 0.376, 0.982, 0.913, 0.543, 0.819 | 0.698, 0.834, 0.912, 0.746, 0.871 | 0.238, 0.782, 0.699, 0.364, 0.630 | 0.538, 0.834, 0.896, 0.650, 0.845 |
| pima | 0.563, 0.715, 0.751, 0.629, 0.707 | 0.558, 0.633, 0.729, 0.586, 0.673 | 0.465, 0.652, 0.671, 0.542, 0.619 | 0.542, 0.643, 0.729, 0.586, 0.671 |
| heart | 0.682, 0.767, 0.807, 0.722, 0.739 | 0.639, 0.687, 0.720, 0.659, 0.682 | 0.575, 0.783, 0.742, 0.662, 0.645 | 0.625, 0.691, 0.719, 0.654, 0.676 |
| vehicle | 0.494, 0.850, 0.867, 0.624, 0.788 | 0.731, 0.842, 0.921, 0.778, 0.868 | 0.422, 0.805, 0.814, 0.553, 0.725 | 0.666, 0.821, 0.895, 0.726, 0.837 |
| wine | 0.777, 0.880, 0.903, 0.825, 0.853 | 0.751, 0.767, 0.834, 0.748, 0.785 | 0.585, 0.760, 0.780, 0.660, 0.694 | 0.736, 0.744, 0.832, 0.736, 0.775 |

Here the paper's baselines are not reproduced either (for example SMOTE AUC 0.671 against 0.729 on pima, 0.699
against 0.896 on ecoli), so single agreements such as the ecoli RSMOTE AUC (0.913 against 0.912) do not
validate anything. Qualitatively, our RSMOTE beats SMOTE under label noise on ecoli and vehicle (precision
+0.160 and +0.065, F1 +0.096 and +0.052, AUC +0.016 and +0.026), the two sets where its noise test flags the
largest share of the minority (26% and 19%, with 30% of labels flipped); on pima, heart and wine the gain is
at most +0.022 on any measure. The paper reports F1 gains of +0.06 to +0.18 on all five.

## 5. Diagnostic: oversampling before the split (not the paper's protocol)

No scaling, best k, c = 0, P, R, AUC, F1, G-mean:

| data | paper RSMOTE | ours RSMOTE (leak) | paper SMOTE | ours SMOTE (leak) |
|--|--|--|--|--|
| ecoli | 0.893, 1.000, 0.996, 0.942, 0.988 | 0.953, 0.977, 0.980, 0.964, 0.963 | 0.505, 0.673, 0.834, 0.558, 0.751 | 0.945, 0.970, 0.977, 0.956, 0.955 |
| pima | 0.714, 0.837, 0.886, 0.770, 0.825 | 0.790, 0.794, 0.847, 0.791, 0.789 | 0.595, 0.700, 0.790, 0.643, 0.721 | 0.765, 0.782, 0.830, 0.771, 0.766 |
| heart | 0.942, 0.950, 0.984, 0.946, 0.951 | 0.808, 0.825, 0.870, 0.815, 0.813 | 0.672, 0.833, 0.820, 0.743, 0.748 | 0.807, 0.820, 0.864, 0.807, 0.807 |
| vehicle | 0.918, 1.000, 0.996, 0.956, 0.985 | 0.951, 0.982, 0.985, 0.966, 0.965 | 0.824, 0.975, 0.981, 0.892, 0.954 | 0.953, 0.981, 0.985, 0.966, 0.965 |
| wine | 1.000, 1.000, 1.000, 1.000, 1.000 | 0.937, 0.895, 0.952, 0.913, 0.913 | 0.949, 0.973, 0.982, 0.961, 0.968 | 0.930, 0.899, 0.955, 0.912, 0.912 |

The leak lifts SMOTE as much as RSMOTE, far above the paper's SMOTE values, and still leaves RSMOTE below the
paper on pima, heart and wine. It does not explain the paper's pattern (RSMOTE high, baselines not inflated).

## 6. Diagnostic: deleting the flagged rows as well (not the paper's reading)

Stated protocol, best k, RSMOTE with the rows it flags as noise also removed from the training data:

| data | c = 0, flagged rows deleted (compare Section 3) | c = 0.3, flagged rows deleted (compare Section 4) |
|--|--|--|
| ecoli | 0.782, 0.898, 0.950, 0.831, 0.923 | 0.786, 0.818, 0.919, 0.779, 0.868 |
| pima | 0.638, 0.685, 0.785, 0.645, 0.722 | 0.596, 0.633, 0.739, 0.588, 0.675 |
| heart | 0.764, 0.752, 0.838, 0.750, 0.775 | 0.665, 0.668, 0.729, 0.643, 0.675 |
| vehicle | 0.868, 0.922, 0.970, 0.889, 0.935 | 0.764, 0.818, 0.918, 0.777, 0.857 |
| wine | 0.917, 0.900, 0.944, 0.895, 0.910 | 0.760, 0.747, 0.843, 0.743, 0.780 |

At c = 0 deletion moves every value by at most 0.02 (pima AUC 0.785 against 0.781). At c = 0.3 it raises
precision (ecoli 0.786 against 0.698), whereas the paper's Table 4 shows RSMOTE with low precision and high
recall (ecoli 0.376 and 0.982) and blames the low precision of all oversamplers on not filtering noise (p. 412).
The paper's own numbers thus fit the reading that the noise stays in the training data.

## 7. Why the gap is not ours to close, and what the paper does not state

* Under the stated protocol the baselines match on pima and vehicle while RSMOTE does not; none of the
  implementation choices (NOTES.md, C1 to C16) can move results by 0.1 AUC. Deleting the noise (Section 6) or
  choosing k per classifier moves them by about 0.02 or less.
* The authors' published file is not the code behind the tables: in all 50 training sets of the stated
  protocol (5 data sets, 5 repetitions, 2 noise levels; k = 5) our 2-means split P' into two clusters of at least two seeds each, the
  case in which RSMOTE_V8.py stops with ZeroDivisionError (NOTES.md, D10) unless its own capped relative density
  (D6) leaves a single-seed cluster; in that one-cluster case it returns all-zero synthetic rows whenever the
  imbalance ratio exceeds about 2.7 (D15). The experiment scripts are not published.
* Not stated in the paper: feature scaling; the IR used in the binary experiments; how the "best result" over k
  is chosen; library versions (AdaBoost's default algorithm changed from SAMME.R to SAMME since 2020) and seeds;
  whether all methods share the same five splits; how the noise flips are drawn and rounded. The stated 75/25
  split conflicts with Table 3's recall values, which fit a 20% test part (Section 2).
* What would settle it: the authors' experiment script, or RSMOTE outputs for one published split.
