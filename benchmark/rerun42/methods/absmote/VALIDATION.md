# Validation of `absmote.ABSMOTE` (AB-SMOTE, Al Majzoub and Elgedawy 2020)

Script: `python3 -I validate_absmote.py 40` (about 3.5 minutes; writes `validation_results.json`; console log in `validation_output.txt`).
Helpers: `weka_replica.py` (validation only). Development probes: `exploration/`.

## Target

Table IV (p.34): Abalone9-18, J48, 5-fold cross-validation, recall and F-measure of the minority
(positive) class, AB-SMOTE settings 4.0-4.3 with (M, k) in {5, 8}^2, GAP 0-1, percentage 100
(Table III, p.34). Also the Gen columns (number of generated instances) of Tables IV, VI, IX and X
(pp.34-35). The printed 3-decimal values fix the integer confusion counts: for example, row 4.0
(recall 0.427, F 0.493, Gen 40) means TP = 35 of 82 positives and FP = 25.

## Data

| Paper dataset (source) | Copy used | Rows / minority |
|:--|:--|:--|
| Abalone9-18 (KEEL, ref. [13]) | KEEL `abalone9-18.dat` (keel-ds 0.2.5 raw) | 731 / 42 |
| Haberman (UCI, ref. [16]) | KEEL `haberman.dat`, and the UCI row order from github.com/jbrownlee/Datasets `haberman.csv` (saved as `data/haberman_uci_order.csv`, sha256 b4b7a32586a5668f9f4d6dc8be9d1bc8cd4822523affb1f6b5bfc350681ef3e2; same 306 rows) | 306 / 81 |
| Flare (KEEL, ref. [18]) | KEEL `flare-F.dat` | 1066 / 43 |
| Wine Quality (KEEL, ref. [4]) | KEEL `winequality-red-4.dat` | 1599 / 53 |

The four CrowdAnalytix and IBM sets (Tables V, VII, VIII, XI) were not used: their WEKA
preprocessing is not described, and the four sets above suffice.

## Protocol: stated, and reconstructed where unstated

Stated (Sec. IV, pp.33-34): WEKA, J48, 5-fold cross-validation, recall and F-measure of the
minority class, settings of Table III.

Not stated, reconstructed and checked (part A checks the reconstruction on rows without AB-SMOTE):

1. **Oversampling before cross-validation, on the whole dataset.** 43 of the 44 recalls in Tables
   IV, VI, IX and X are exact fractions over (original minority + Gen), e.g. row 4.3:
   0.494 = 40/81 = 40/(42 + 39). The synthetic rows sit in the test folds.
2. **Pooled confusion matrix** over the 5 folds (WEKA Explorer), not the per-fold average that
   Sec. IV describes.
3. **Seeds**: WEKA defaults, 1 for the filter and 1 for the cross-validation.
4. **J48 defaults** (-C 0.25 -M 2).
5. **Distances and generation as in WEKA's SMOTE filter**: unscaled numeric values plus VDM for
   nominal attributes (Sex), one gap per numeric attribute, nominal values of new rows by majority
   vote over the seed and its k neighbors; nominal values coded in order of first appearance
   (F, M, I), as WEKA's CSV loader does.
6. **Borderline rule as run** ("authors_code"): the instance counts as one of its own M neighbors
   and the bound is Java's integer M/2; see part B. This contradicts the text's noise rule.

How (no WEKA code was downloaded or run): `weka_replica.py` re-creates java.util.Random (checked
against OpenJDK 21: the first 19 draws of `new Random(1)` agree, `exploration/RandCheck.java`),
WEKA's `randomize`, `stratify` and `testCV`, J48 (C4.5 release 8: gain ratio with the average-gain
filter, MDL-corrected numeric thresholds, collapsing, pessimistic pruning with subtree raising),
and the SMOTE filter. `absmote.py` itself sees WEKA's distances through a VDM embedding: for two
classes VDM(u, v) = 2|p_u - p_v|, which a "staircase" of orthogonal steps reproduces exactly as a
squared Euclidean distance (`weka_replica.vdm_embedding`).

## A. Harness check: Table IV rows without AB-SMOTE (exact replay)

| Row (Table IV, p.34) | Paper TP / FP | Paper recall / F | Replay TP / FP | Replay recall / F |
|:--|:--|:--|:--|:--|
| 1.0 Original | 7 / 9 | 0.167 / 0.241 | 7 / 9 | 0.167 / 0.241 (exact) |
| 2.0 SMOTE k=5 | 32 / 19 | 0.381 / 0.474 | 32 / 19 | 0.381 / 0.474 (exact) |

The SMOTE row is exact only with one gap per attribute (one gap per instance gives 40 / 27) and Sex
coded F, M, I (M, F, I gives 32 / 20). Over filter seeds 1-150 the pair (32, 19) occurs once, at seed 1
(`exploration/check_chance.py`), so the match is not luck. J48, folds and SMOTE filter are re-created
correctly.

## B. Gen = |P'| at 100% (WEKA distances), M = 5 / M = 8

| Dataset | Paper | `text` (default) | `figure` | `authors_code` | authors_code + index quirk |
|:--|:--|:--|:--|:--|:--|
| Abalone9-18 (Table IV) | 40 / 39 | 18 / 22 | 18 / 22 | **40 / 39** | **40 / 39** |
| Haberman, KEEL order (Table VI) | 65 / 61 | 45 / 62 | 45 / 50 | 67 / **61** | 67 / **61** |
| Haberman, UCI order (Table VI) | 65 / 61 | 46 / 63 | 46 / 51 | 66 / **61** | **65 / 61** |
| Flare-F (Table IX) | 39 / 41 | 28 / 30 | 28 / 30 | **39 / 41** | **39 / 41** |
| Wine Quality red 4 (Table X) | 53 / 53 | 9 / 12 | 9 / 12 | **53 / 53** | **53 / 53** |

Columns 3-5 are `ABSMOTE(m_neighbors=M, borderline_rule=...)` on WEKA-distance features. The text's
rule (seed excluded, noise M' = M removed) finds far fewer seeds than the authors' runs did. The
`authors_code` reading reproduces 7 of 8 counts exactly; the eighth (Haberman, M = 5) needs the
UCI row order and a WEKA-style index quirk in the neighbor loop that skips the row whose index
equals the seed's position among the minority rows instead of the seed (column 6, replica only;
it matters only with ties). Readings tried (`exploration/gen_counts*.py`): raw, min-max or z-scored
features; VDM, 0/1 or one-hot distances for nominal attributes; seed excluded or included; real or
integer M/2; noise removed or kept. Only raw features with VDM, seed included and integer M/2 come
within 2 of all eight counts (summed absolute error 2); one-hot or 0/1 distances for the nominal
attributes give 4 and 5, and every reading that excludes the seed gives 10 or more.

## C. Exact replay of Table IV rows 3.0-4.3 (authors' pipeline, seeds 1)

| Row | Gen (paper) | Paper TP / FP, recall / F | Replay TP / FP, recall / F |
|:--|:--|:--|:--|
| 3.0 BSMOTE M=5 k=5 | 40 (40) | 34 / 18, 0.415 / 0.507 | 27 / 27, 0.329 / 0.397 |
| 3.1 BSMOTE M=5 k=8 | 40 (40) | 34 / 17, 0.415 / 0.511 | 34 / 17, 0.415 / 0.511 (exact) |
| 3.2 BSMOTE M=8 k=5 | 39 (39) | 38 / 26, 0.469 / 0.524 | 41 / 28, 0.506 / 0.547 |
| 3.3 BSMOTE M=8 k=8 | 39 (39) | 32 / 16, 0.395 / 0.496 | 32 / 16, 0.395 / 0.496 (exact) |
| 4.0 AB-SMOTE M=5 k=5 | 40 (40) | 35 / 25, 0.427 / 0.493 | 25 / 17, 0.305 / 0.403 |
| **4.1 AB-SMOTE M=5 k=8** | 40 (40) | 36 / 18, **0.439 / 0.529** | 36 / 18, **0.439 / 0.529 (exact)** |
| 4.2 AB-SMOTE M=8 k=5 | 39 (39) | 35 / 19, 0.432 / 0.519 | 31 / 17, 0.383 / 0.481 |
| 4.3 AB-SMOTE M=8 k=8 | 39 (39) | 40 / 22, 0.494 / 0.559 | 30 / 26, 0.370 / 0.438 |

The replay's AB-SMOTE uses exactly `absmote.py`'s selection: with `borderline_rule="authors_code"`,
`ABSMOTE` returns the same borderline sets (M = 5 and 8) and the same partner lists (k = 5 and 8) as
the replica (checked in the script). The replica differs only in drawing its random numbers from
java.util.Random in WEKA's order and in setting Sex by majority vote. The BSMOTE rows 3.1 and 3.3
are exact only if the partner search skips the minority row at the seed's position in the seed list
(WEKA's `if (i != j)` with mismatched indices), so the seed can be its own partner.

Chance level: over filter seeds 1-150, row 4.1's (36, 18) occurs for 3 seeds (2%). Three exact
rows (3.1, 3.3, 4.1) at their stated settings would be very unlikely by chance. Five rows are not
reproduced exactly. Tried without success (`exploration/variants.py`, `search_k.py`, `offset.py`):
other loop and exclusion structures, every (M, k) from (3..10, 1..10), offsets of 0-40 draws in
the random stream, and filter seeds 0-10 (a few other settings hit single rows, at the rate
expected by chance). These rows may come from runs that differed in a way the paper does not
record. The three AB-SMOTE rows among them lie within the seed spread of the same pipeline
(part D); the BSMOTE rows were not examined further.

## D. `absmote.py` over 40 random states (paper protocol, CV seed 1)

Mean +- standard deviation of recall / F-measure; in brackets, the share of runs at or below the
paper's value. The first column is the replica over java seeds 1-40 (the authors' pipeline);
the others are `ABSMOTE(borderline_rule=..., gap=...)` with random_state 0-39.

| Row (paper recall / F) | Replica, Gen 40/39 | authors_code, per_feature, Gen 40/39 | authors_code, scalar | text, per_feature, Gen 18/22 | text, scalar (default) |
|:--|:--|:--|:--|:--|:--|
| 4.0 (0.427 / 0.493) | 0.417 +- 0.048 / 0.493 +- 0.046 [0.60 / 0.53] | 0.430 +- 0.044 / 0.507 +- 0.035 [0.47 / 0.40] | 0.438 +- 0.050 / 0.508 +- 0.050 [0.53 / 0.42] | 0.409 +- 0.044 / 0.507 +- 0.038 [0.70 / 0.23] | 0.405 +- 0.053 / 0.503 +- 0.049 [0.65 / 0.38] |
| 4.1 (0.439 / 0.529) | 0.424 +- 0.045 / 0.502 +- 0.046 [0.72 / 0.75] | 0.412 +- 0.035 / 0.493 +- 0.029 [0.80 / 0.93] | 0.434 +- 0.041 / 0.511 +- 0.039 [0.57 / 0.62] | 0.396 +- 0.051 / 0.490 +- 0.049 [0.78 / 0.82] | 0.417 +- 0.050 / 0.511 +- 0.045 [0.78 / 0.72] |
| 4.2 (0.432 / 0.519) | 0.423 +- 0.032 / 0.494 +- 0.031 [0.68 / 0.80] | 0.427 +- 0.040 / 0.500 +- 0.038 [0.65 / 0.72] | 0.437 +- 0.041 / 0.509 +- 0.042 [0.40 / 0.55] | 0.431 +- 0.053 / 0.522 +- 0.044 [0.45 / 0.53] | 0.462 +- 0.040 / 0.552 +- 0.037 [0.15 / 0.17] |
| 4.3 (0.494 / 0.559) | 0.416 +- 0.054 / 0.497 +- 0.054 [0.95 / 0.85] | 0.424 +- 0.046 / 0.497 +- 0.037 [0.97 / 0.97] | 0.431 +- 0.052 / 0.510 +- 0.047 [0.93 / 0.85] | 0.436 +- 0.051 / 0.531 +- 0.044 [0.80 / 0.70] | 0.443 +- 0.048 / 0.532 +- 0.043 [0.82 / 0.78] |

* `absmote.py` with the authors' reading (`authors_code`, `per_feature`) matches the replica's
  distribution (differences of 0.000 to 0.014 in the means, at most 1.5 standard errors), as
  expected when only the random stream differs.
* The paper's values for 4.0-4.2 lie inside the spread of every reading (between the 15th and 93rd
  percentiles). Row 4.3, the table's bolded best, lies in the upper tail: 85th-97th percentile
  under the authors' reading, 70th-82nd under the text reading.
* Default setting 4.0: paper 0.427 / 0.493; `absmote.py` (authors_code, per_feature) 0.430 / 0.507,
  differences +0.003 / +0.014; `absmote.py` default (text, scalar) 0.405 / 0.503, differences
  -0.022 / +0.010.
* The text reading generates fewer rows (18/22 instead of 40/39) and still reaches similar recall
  and F here, because under this protocol fewer synthetic rows also means fewer synthetic positives
  in the test folds.

## Verdict

* **Reproduced exactly**: Table IV row 4.1 (AB-SMOTE M = 5, k = 8): recall 0.439 and F-measure
  0.529, difference 0.000, by the exact replay that uses `absmote.py`'s borderline sets and partner
  lists under the `authors_code` reading. The same holds for AB-SMOTE's Gen counts (40 and 39,
  Table IV, and 7 of 8 across Tables IV, VI, IX, X with `absmote.py` itself).
* **Close (within seed spread)**: rows 4.0, 4.2 and, in the tail, 4.3.
* **Reading used**: `authors_code` (seed counted as its own neighbor, integer M/2) with per-attribute
  gaps and WEKA distances. This is what the authors ran, not what the paper describes. With the
  paper's text rule (the default in `absmote.py`) the Gen counts are not reproduced (18/22 instead
  of 40/39 on Abalone9-18). Recall and F-measure are still within one standard deviation of the
  paper's values for 4.0, 4.1 and 4.2; for 4.3 the paper's recall is just over one standard
  deviation above the mean (0.494 against 0.443 +- 0.048).
* **Protocol caveat**: the paper's numbers include synthetic rows in the test folds, so they are
  optimistic and should not be compared with leak-free results.
