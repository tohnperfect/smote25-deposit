# AB-SMOTE (slug `absmote`): notes, ambiguities and choices

Paper: H. Al Majzoub and I. Elgedawy, "AB-SMOTE: An Affinitive Borderline SMOTE Approach for
Imbalanced Data Binary Classification", International Journal of Machine Learning and Computing
10(1):31-37, 2020, doi 10.18178/ijmlc.2020.10.1.894. The PDF has 7 pages (journal pp.31-37).
Implementation: `absmote.py`, class `ABSMOTE`. Validation: `VALIDATION.md`.

## 0. Bibliographic check

The task prompt names five authors (Al Majzoub, Elgedawy, Akaydin, Kofman and Alkhurayji). The
paper's byline (p.31) and the survey's `refs.bib` entry `almajzoub2020absmote` list two: Hisham Al
Majzoub and Islam Elgedawy. The other three names do not appear anywhere in the paper. Wherever the
survey cites this paper, use the two-author form.

## 1. What the paper specifies

* Seeds: minority instances whose M nearest neighbors in the whole training set contain M'
  majority instances with M' "between M/2 and M" (Sec. II.B, p.32; Sec. III, p.33). M' < M/2 is
  safe, M' = M is noise (Sec. III, p.33).
* Partner: one of the k nearest neighbors searched within the borderline set P' only, chosen at
  random (Sec. III, p.33; Figs. 5-6, p.33). This is the only difference from Borderline-SMOTE.
* Placement: new = P'i + gap * (P'j - P'i), gap a random number between 0 and 1 (Sec. III, p.33;
  Sec. II.A, p.32, where "distance" is defined as the difference vector).
* Amount: percentage parameter, 100 in every AB-SMOTE setting (Table III, p.34). The Gen columns
  (Tables IV-XI, pp.34-35) equal |P'|, i.e. one new instance per borderline instance.
* Settings: (M, k) in {(5, 5), (5, 8), (8, 5), (8, 8)}, GAP 0-1, percentage 100 (Table III, p.34).
  Defaults in `ABSMOTE` are setting 4.0: M = 5, k = 5, percentage 100. SMOTE's default k = 5 and
  100% are also stated in Sec. II.A (p.32).
* Two-class only (title; Sec. I, p.31). No multiclass rule is given.

## 2. Choices (each marked `CHOICE:` in `absmote.py`)

1. **Borderline rule** (`borderline_rule`, default `"text"`). The text implies M/2 <= M' < M
   (only M' < M/2 is safe and only M' = M is noise; Sec. III, p.33), which is also Han et al.'s
   Borderline-SMOTE rule (the paper's ref. [9]). The flowcharts print "If M/2 < M' < M" (Fig. 4 and
   Fig. 6, p.33; checked on the rendered PDF). The two differ only when M' = M/2 (even M, e.g.
   M = 8, M' = 4). Option `"figure"` gives the flowchart reading. Option `"authors_code"` gives the
   reading that reproduces the paper's Gen counts (section 3 below): the instance counts as one of
   its own M neighbors and the bound is the integer floor(M/2), so noise is never excluded.
2. **Distance**: Euclidean on X as given (the caller scales the features). The paper names no
   metric. The authors' WEKA runs used unscaled numeric values plus VDM for nominal attributes
   (section 3). Squared distances are compared.
3. **Ties and duplicates**: neighbors are ordered by distance, ties by lower row index; the query
   row is excluded from its own neighbor list by index only, so exact duplicates count as
   neighbors (for `"text"` and `"figure"`); for `"authors_code"` the query itself takes part, at
   distance 0, in row order.
4. **Gap** (`gap`, default `"scalar"`): one uniform gap per new instance, so the point lies on
   the segment, as the prose says ("new instances falling in the line space between the selected
   instances", Sec. II.A, p.32; "Multiply by Gap", Fig. 6). Option `"per_feature"` draws one gap
   per feature, which is what WEKA's SMOTE filter does (following the pseudocode in Chawla et al.
   2002) and what the authors' runs did (confirmed by the exact replay of Table IV's SMOTE row,
   VALIDATION.md part A). Uniform on [0, 1) is assumed; the paper only says "between 0 and 1".
5. **Small borderline sets**: the partner pool is P' minus the seed, so k_eff = min(k, |P'| - 1)
   (WEKA's SMOTE caps k the same way for a small class). With |P'| < 2 there is no partner and no
   new instance is made; with |P'| = 0 the data are returned unchanged. WEKA would raise an error
   ("Cannot use 0 neighbors!"); the paper does not cover the case.
6. **Percentage not a multiple of 100**: floor(percentage/100) new instances per borderline seed,
   and one more for int(fraction * |P'|) seeds drawn without replacement (the WEKA SMOTE filter's
   rule, which the authors modified). The paper only uses 100.
7. **Minority class**: the smaller class; on a tie, the smaller label. More or fewer than two
   classes raise `ValueError` (the paper is two-class only).
8. **Tiny training sets**: if fewer than M other rows exist, all other rows form the
   neighborhood and the bounds use that size (M_eff = n - 1; n for `"authors_code"`).
9. **Partner choice**: uniform among the k_eff nearest borderline neighbors (the paper says
   "randomly chooses one of the Knn", p.33).
10. **Order of new rows**: grouped by seed, seeds in row order, after all original rows.
11. **Nominal attributes**: not handled (X is float). The authors' WEKA code used VDM distances
    and set nominal values of new instances by majority vote over the seed and its k neighbors.
12. **Random numbers**: `sklearn.utils.check_random_state`; draws in the order: extra seeds (only
    for fractional percentages), partner indices, gaps.

## 3. What the authors' runs did, as reconstructed from the printed numbers

Evidence and code are in `VALIDATION.md`, `validate_absmote.py` and `weka_replica.py`.

* **Seed counted as its own neighbor, integer M/2.** Under the text's rule the borderline sets are
  far smaller than the paper's Gen (Abalone9-18: 18 and 22 against 40 and 39; Wine Quality: 9 and 12
  against 53 and 53). Counting the instance itself among its M neighbors and using Java's integer
  M/2 (2 for M = 5) reproduces 7 of the 8 printed Gen counts exactly with `absmote.py`
  (`borderline_rule="authors_code"`, WEKA's distances), and all 8 when Haberman is in UCI row
  order and the neighbor loop skips the row whose index equals the seed's position among the
  minority rows (a WEKA-style `if (i != j)` with mismatched indices; it only matters with ties).
  Consequence: the authors never removed noise. Every minority instance with at least floor(M/2)
  majority rows among its M - 1 nearest others became a seed, so AB-SMOTE as run equals SMOTE on
  Wine Quality (all 53 minority rows are seeds, matching the paper's identical SMOTE, BSMOTE and
  AB-SMOTE rows in Table X).
* **Per-attribute gaps, raw values, VDM** (WEKA SMOTE filter); nominal values coded in order of
  first appearance (Sex as F, M, I), as WEKA's CSV loader does.
* **Oversampling before cross-validation.** 43 of the 44 recalls in Tables IV, VI, IX and X are
  exact fractions over (original minority + Gen), e.g. Table IV row 4.3: 0.494 = 40/81 =
  40/(42 + 39); 23 of them are not fractions over the original minority alone. The exception,
  Table VI row 3.1 (0.627), fits neither and is probably a typo. The synthetic rows were in the
  test folds, so the printed recall and F-measure are optimistic and not comparable with
  leak-free protocols such as the survey's rerun.
* **Pooled confusion matrix** over the folds (WEKA Explorer), not the per-fold average that
  Sec. IV (p.34) describes.
* **BSMOTE baseline**: the exact replays of Table IV rows 3.1 and 3.3 need an index mismatch in the
  partner search (the seed can be its own partner, producing copies), so the BSMOTE runs the paper
  compares against were not a clean Borderline-SMOTE either.

## 4. Errors and inconsistencies in the paper (please check against the PDF)

* Figs. 4 and 6 (p.33) print M/2 < M' < M; the text treats M' = M/2 as borderline (item 2.1).
* Fig. 6's "Generate new instance" box says "Calculate Difference between P'i & Pj" (copied from
  Fig. 4); for AB-SMOTE it should be P'j.
* Table I (p.34): Flare total 1109 and majority 1066; KEEL flare-F, which reproduces the paper's
  Gen and SMOTE recall (31/86 = 0.36), has 1066 rows and 1023 majority. Wine Quality total 1493,
  but 1546 + 53 = 1599 (KEEL winequality-red-4, which reproduces Gen 53). Table IX repeats
  "Majority = 1066".
* Table VII (p.35), row 3.1: F-measure 0.871 with recall 0.513 is impossible (F <= 2R/(1+R) = 0.678
  at precision 1). The text below Table VII and Table XII still count it as BSMOTE's best
  F-measure on Employee Attrition.
* Table VIII (p.35), row 4.3: Gen 1101, but rows 3.2, 3.3 and 4.2 (also M = 8) have 949.
* "Harberman" for Haberman (Tables VI, XII). "AB-SOMTE" in the abstract and conclusion.
* Table VI (p.35), row 3.1: recall 0.627 is not k/146 (Gen 65 + 81) or k/81; probably a typo.
* Table XII's tally of wins rests on single runs. In the replay, the seed-to-seed standard
  deviation of recall on Abalone9-18 is 0.03 to 0.05 (VALIDATION.md part D), larger than most
  differences between the BSMOTE and AB-SMOTE rows of Table IV.

## 5. For the rerun

* Use the defaults: `ABSMOTE()` = M 5, k 5, 100%, text rule, scalar gap. The number of new rows is
  |P'| (one per borderline minority instance), not a balancing amount, and it can be zero when no
  minority instance is borderline or only one is.
* The borderline set depends on the distance. The caller's scaled features differ from the
  authors' raw values and VDM, and the text rule differs from the authors' code: even with WEKA's
  distances, the text rule gives 0.17 to 1.02 times as many seeds as the authors' code did on the
  four reachable paper datasets (median 0.62; VALIDATION.md part B).
* To mimic the authors' runs: `ABSMOTE(borderline_rule="authors_code", gap="per_feature")`.

## 6. Points to check against the PDF

* Fig. 4 and Fig. 6 inequality boxes (p.33).
* Table III (p.34): settings 4.0-4.3.
* Table IV (p.34): Gen 40/40/39/39 and recall/F of rows 4.0-4.3 (used in validation).
* Table VII row 3.1 F-measure 0.871 and Table VIII row 4.3 Gen 1101 (p.35).
* Table I totals for Flare and Wine Quality (p.34).
