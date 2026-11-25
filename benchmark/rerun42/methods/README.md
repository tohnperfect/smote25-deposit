# WP6.8 step 2: five re-implementations (11 November 2026)

Each method was implemented from its paper by one AI session (Claude Opus 5.5) under `IMPLEMENTATION_BRIEF.md`, as an
imbalanced-learn style sampler (`fit_resample`), with tests, a validation against a number printed in the paper, and
notes on every choice the paper leaves open (`CHOICE:` in the code, `NOTES.md` in each folder). The tests of all five
pass (rerun on 11 Nov: 10, 10, 11, 12 and 16 checks), and the SMOM validation was rerun by the coordinating session
with the same numbers. **These are AI work; a person reads each `VALIDATION.md` and `NOTES.md` before the rerun's
results are used.**

| Method | Validated against (paper's table) | Paper | This implementation | Verdict | Folder |
|---|---|---|---|---|---|
| SMOM (2017) | vehicle, MG with Weka Naive Bayes (supervised discretization), 10 x stratified 10-fold CV (Supp. Table S4; MAUC Supp. Table S6) | MG 0.7849, MAUC 0.9299 | MG 0.7848, MAUC 0.9299; vowel5 MG 0.7781 against 0.7783 | reproduced | `smom/` |
| AB-SMOTE (2020) | Abalone9-18, J48, 5-fold CV, recall and F-measure of the minority class, setting 4.1 (Table IV, p. 34) | recall 0.439, F 0.529 | recall 0.439, F 0.529 (exact Weka replay); rows 4.0, 4.2, 4.3 within the spread of the seeds | reproduced, under the reading that the paper's counts of generated points imply rather than its text's noise rule | `absmote/` |
| FW-SMOTE (2022) | yeast3, k-NN, AUC as (TPR + TNR) / 2 x 100, five runs of 10-fold CV (Supp. Table A.1) | 90.3 | 89.5 with its parameters tuned inside the training folds, as the paper states (range 88.8 to 90.5); 90.4 when the configuration is picked on the test folds | close; the paper's gain over SMOTE (1.9 points) is not reproduced (0.0 under in-fold tuning) | `fwsmote/` |
| RSMOTE (2021) | pima, AUC averaged over five classifiers and five repetitions, label noise c = 0 (Table 3, p. 410) | 0.886 | 0.781; the paper's NONE and SMOTE values are reproduced within 0.02 on the same protocol, and on all five data sets that could be rebuilt the paper's RSMOTE values exceed ours by 0.03 to 0.14 AUC | not reproduced | `rsmote/` |
| CGMOS (2016) | Haberman, AUC averaged over six base classifiers, 10 x 10-fold CV (Table 3, p. 1629) | 0.651 (SMOTE 0.600) | 0.688 (other readings 0.660 to 0.671); CGMOS equals SMOTE to within 0.003 in every reading | not reproduced: as printed, its seed probabilities are within 0.1% of SMOTE's uniform ones, so it cannot produce the paper's gain of 0.051 over SMOTE | `cgmos/` |

## Findings for the survey (for the team to read)

1. **RSMOTE keeps its "noise" in the training data.** The points it calls noise are removed from the seeds (and
   partners) only, from Algorithm 1 (p. 403) and the authors' code alike (`rsmote/NOTES.md`, section 1). This answers
   decision-sheet item A10: RSMOTE passes the "keeps all data" criterion of Table 17.
2. **Two of the five papers' own results are not reproduced** by a faithful implementation (RSMOTE, CGMOS), and a third
   (FW-SMOTE) matches its paper only when the configuration is chosen on the test folds. This bears on M1
   (recommendations resting on self-reported scores) and on Section 9 of the paper.
3. **FW-SMOTE's authors did publish code**: github.com/cvairetti/SMOTEIOWA (commit 9d2f306, April 2019, Matlab). It
   departs from the paper in five ways (fixed gap 0.3, partners with replacement, a Minkowski distance on weighted
   features, weights over the kept features, a normalized mutual-information score); `docs/RERUN-PLAN-table16.md` said
   no repository had been found.
4. **SMOM's supplement swaps two column headers**: in Supp. Tables S4, S6, S8 and S10 the blocks headed "NB" and "MLP"
   are the other way round, as the main paper's Table 2 and Supp. Table S13 show (`smom/VALIDATION.md`, section 1).
5. **AB-SMOTE's text and numbers disagree** on the noise rule; the counts of generated points in its tables fit the
   other reading (`absmote/NOTES.md`). The paper has two authors (Al Majzoub and Elgedawy), as `refs.bib` says.

## Decision needed

The rerun plan's rule says a re-implementation is used only after it reproduces a number printed in its paper.
SMOM and AB-SMOTE meet it and FW-SMOTE comes close. For RSMOTE and CGMOS the failure lies in the papers' own numbers as
far as the protocol can be read, not in an error found in the implementations. DECISION for the team lead: run them
in the rerun as faithful implementations with the non-reproduction stated, or leave them out of Table 17.

## Rerunning the validations

Each `validate_*.py` reads the KEEL files from `/home/claude/work/rerun42/src/kd/` (the keel-ds 0.2.5 wheel unzipped, see `../out/fetch_notes.md`): unzip the wheel there, or change the path at the top of the script. Run with `python3 -I`; imbalanced-learn 0.14.2 is needed for the SMOTE baselines.

## Not in the package

`*/ref/` (the authors' code that the sessions read: RSMOTE, SMOTEIOWA) and `*/scratch/`; `*/data/` except AB-SMOTE's copy of the UCI Haberman file in its original row order (from github.com/jbrownlee/Datasets).
