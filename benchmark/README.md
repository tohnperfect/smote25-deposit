# Independent benchmark (WP6, core tier): harness and pilot

Built 10 November 2026. Code only; the full run needs team compute.

## One command

```bash
pip install imbalanced-learn smote-variants imbalanced-learn-extra baycomp joblib
pip install --no-deps imbalanced-databases        # its old 'sklearn' dependency breaks pip
python3 benchmark/run.py --out benchmark/results --jobs 8      # resumable; one .jsonl per dataset
python3 benchmark/stats.py benchmark/results benchmark/results/stats
```

## What it does (plan WP6 steps 1 to 6)

* Data: the 110 two-class KEEL sets bundled in `imbalanced-databases` (the 110 sets of the v0.1
  illustrative runs). Datasets of one source family are averaged before testing. The 42-task
  reference collection of the Data section is not wired in yet.
* Methods: no resampling; class weighting (`class_weight='balanced'`; kNN has none, recorded as not
  applicable); threshold tuned to G-mean on 3-fold out-of-fold probabilities of the training part;
  random oversampling; SMOTE; ADASYN; Borderline-SMOTE (imbalanced-learn 0.14.2); G-SMOTE of Douzas
  and Bacao (imbalanced-learn-extra 0.2.10); Safe-Level-SMOTE, Cluster-SMOTE, k-means SMOTE, MWMOTE,
  SMOTE-IPF and A-SUWO (smote-variants 1.0.1). No public implementation was found for CGMOS, SMOM,
  FW-SMOTE and AB-SMOTE (simple candidates of the recommendation table); the code the RSMOTE authors published
  (github.com/syxiaa/RSMOTE, last commit 26 Aug 2020) imports two modules that are not in the repository
  (checked 11 Nov 2026), so RSMOTE was not run either. CISO and QC-SMOTE
  are left out until a re-implementation reproduces a number from their papers.
* Learners: CART, kNN (k = 5), logistic regression, RBF-SVM (Platt probabilities), random forest
  (200 trees), histogram gradient boosting; one configuration for every method.
* Protocol: stratified 5-fold cross-validation repeated 5 times, seed 20261110, the same folds for
  every method (saved under `folds/`); scaling, resampling and threshold fitted on the training part.
* Measures: ROC-AUC and PR-AUC; G-mean, F1, MCC and balanced accuracy at the default threshold
  (or the tuned one); Brier score, expected calibration error, calibration slope and intercept;
  resampling time.
* Statistics: Friedman with Iman-Davenport; Wilcoxon against SMOTE with Holm; Bayesian signed-rank
  against SMOTE with a region of practical equivalence of 0.01; median difference.

## Pilot (10 Nov 2026, not reportable)

`benchmark/pilot/`: 4 datasets (ecoli1, glass1, pima, yeast3), one repeat of 5 folds, 9 methods,
4 learners, 720 cells, all ran. It shows the harness works end to end; four datasets support no
conclusion. Timing: about 30 s for 180 cells on yeast3 (1,484 rows) on one core.

Estimate for the full core tier: 110 datasets x 25 folds x 15 methods x 6 learners, about 250,000
fits; roughly 10 to 20 CPU hours, dominated by the SVM with probabilities and the larger sets.

## Still to do (extension tier and checks)

1. Wire in the 42-task reference collection (Data section difficulty files).
2. Recalibration (Platt and isotonic) before the calibration measures, as a second condition.
3. Four to six multiclass sets kept multiclass; a nested-tuning run with an equal budget.
4. Check the run against the paper's own 15-item checklist (Table 15) before reporting.

## The run on the team lead's MacBook (v0.4, 10 and 11 November 2026)

Machine and versions: `mac_runner/environment.txt` (Apple M5 Pro, 15 cores, 24 GB; Python 3.13, scikit-learn 1.9.1,
imbalanced-learn 0.14.2, smote-variants 1.0.1; 14 workers). The runner `mac_runner/run_benchmark_mac.sh` sets up a
virtual environment, keeps the Mac awake and runs the phase scripts in `phases/` in order; finished cells are skipped
on resume. Results stay on the Mac in `~/Downloads/SMOTE25_benchmark_run/SMOTE25_Draft_v03/benchmark/results*/`.

* Phase 1 (`01_core.sh`): the core tier, 110 sets x 25 folds x 14 methods x 6 learners (2,100 cells per set). The
  first attempt stopped on three bundled files with spaces inside nominal values (abalone19, hepatitis,
  hypothyroid); `load()` now strips those spaces (the other sets load unchanged) and a failing set writes
  `<set>.error` instead of stopping the run. Note for the write-up: the 110 sets are the two-class sets bundled in
  `imbalanced-databases`; names such as ada, hiva, sylva, cm1, kc1 and pc1 suggest sets from collections other than
  KEEL, so check the source of each before the paper calls all 110 KEEL sets.
* Phase 2 (`02_extras.sh`, decision D18): the two extension tiers of `run_ext.py`, run at the same time.
  High-dimensional tier: OpenML candidates filtered by a rule fixed before the run (binary, at least 100 features,
  minority share at most 0.20, at most 20,000 rows, not already in the core tier; active OpenML version, id
  recorded); musk's molecule name and scene's five other label columns are dropped; the eight OVA gene-expression
  targets that pass share their 1,545 examples, so one is drawn at random (seed 20261111; a test draw gave
  OVA_Uterus), which leaves scene, Speech, musk, Internet-Advertisements and one OVA target; one job per dataset
  and repeat (tested to give the same cells as one job per dataset). A timing probe on a cloud CPU took up to about
  100 s per cell for an OVA set (gradient boosting, SVM, A-SUWO), hence the single OVA target. Nested tier: 30 of the 59 sets with at least 30 minority
  examples (seed 20261111), 3 x 5 outer folds, one hyperparameter per learner tuned on 3 inner folds by PR-AUC.
  `run_extras_now.sh` can start this phase from a second Terminal window while phase 1 runs; a lock prevents a
  double run. When both tiers finish, the phase writes `phases/STOP` so that the runner ends.
* Fixes made before phase 2 started (11 Nov): the OpenML loader failed under pandas 3 for integer-coded nominal
  values (now falls back to the liac-arff parser) and, inside joblib workers, was not used at all (the high-dimensional
  jobs now call it directly); `stats.py` would have put every OpenML set in one family "oml"; resume and statistics now
  skip a results line cut short by a stop.
* Not wired yet: the 42-task reference collection of the Data section (needs the repository mirrors).

## Results and write-up (v0.5, 11 November 2026)

The run finished on 11 November 2026 (07:34 on the MacBook). Cells by tier (dataset, fold, method and learner):

| Tier | Cells | Gave a result | Sampler stopped with an error | Not applicable (k-NN with class weights) |
|---|---|---|---|---|
| Core | 231,000 | 225,112 | 3,138 (SMOTE, Borderline-SMOTE, G-SMOTE 660 each; ADASYN 1,152; A-SUWO 6) | 2,750 |
| High-dimensional | 10,500 | 10,351 | 24 (A-SUWO) | 125 |
| Nested | 25,200 | 24,578 | 172 (ADASYN) | 450 |

* Statistics: `stats.py` was fixed before any result was read (see its docstring): SMOTE has no result in two
  source families (lymphography, zoo), and the old rule removed a method from every test after one failed family,
  which left the core tier without a single comparison. The Bayesian test is now seeded (20261110), so reruns give
  the same probabilities; the high-dimensional tier reproduces exactly with the fixed code. The tests were rerun
  from the family means with `stats.py --from-means`.
* `results_summary/` holds what the paper uses, copied from the Mac (per tier: `config.json`, `cell_status.csv`,
  `per_dataset_means.csv`, `per_family_means.csv`, `tests_vs_smote.csv`; `environment.txt`). Derived files:
  `core/smote_vs_none.csv` (written by `scripts/make_fig_smote_vs_none.py`, which also draws Figure 3),
  `highdim/smote_vs_none.csv`, `nested/pool.json` and `families.json` (written by `scripts/bench_derived.py`),
  `headline.json` (written by `scripts/gen_benchmark_tables.py`, which also writes Tables 20 and 21).
* High-dimensional selection (`results_summary/highdim/highdim_selection.json`): five of the nine OVA targets could
  not be downloaded on the Mac (IncompleteRead: OVA_Lung, OVA_Uterus, OVA_Ovary, OVA_Colon, OVA_Breast), so
  OVA_Prostate was drawn (seed 20261111) from the four that loaded and passed the rule (OVA_Endometrium,
  OVA_Kidney, OVA_Omentum, OVA_Prostate); the test draw named above (OVA_Uterus) was made while testing in the
  cloud. hiva_agnostic and sylva_agnostic were left out as the same data as core-tier sets. Appendix F says the
  OVA target was drawn among those that loaded.
* The per-fold result files (about 230 MB) stay on the MacBook in
  `~/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run/`; they go into the deposit (WP2 step 6).
* Still not run: the 42-task reference collection, the recalibration condition and the multiclass sets (items 1 to
  3 of "Still to do" above). Section 11 of the paper states the limits of the benchmark.

## The reference-collection tier (v0.10, 11 November 2026)

The rerun behind Table 17 (`rerun42/README.md`): the ten simple methods of the recommendation table, five of them
re-implemented from their papers (`rerun42/methods/`), and the four baselines, on the 42-task reference collection of
Appendix C, under this protocol (`rerun42/scripts/run42.py` imports `run.py`); statistics by `rerun42/scripts/stats42.py`
(imports `stats.py`) in `results_summary/rerun42/`. Run in the cloud on the tasks it could run; the three largest
tasks wait for phase 03 of the MacBook runner, the Kaggle task for a sign-in.

