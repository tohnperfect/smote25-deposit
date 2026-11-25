# WP6.8: the rerun behind Table 17 on the reference collection (11 November 2026)

Decisions of the team lead: recommend methods in Table 17 only from a rerun of its ten methods on the 42-task
reference collection of Appendix C, under the protocol of the independent benchmark (WP6.7); run RSMOTE and CGMOS as
faithful implementations with the failure to reproduce their papers stated (D22). Everything here is AI work (Claude
Opus 5.5 sessions); a person reads the validations and the results before submission.

## Steps and files

| Step | What | Files |
|---|---|---|
| 1 | Fetch the 42 tasks and check each against rows, features and minority count of the Data section's table: 41 pass, the Kaggle task (smoke detection) needs a sign-in | `scripts/tasks42.py`, `out/tasks42_check.csv`, `out/fetch_notes.md` |
| 2 | Implement CGMOS, SMOM, AB-SMOTE, RSMOTE and FW-SMOTE from their papers, one AI session each, with tests and a validation against a number the paper prints | `methods/` (README there) |
| 3 | Run the ten methods and the four baselines under the benchmark's protocol, then test against SMOTE on families of tasks | `scripts/run42.py`, `scripts/stats42.py`; statistics in `../results_summary/rerun42/` |

`run42.py` imports the benchmark's functions from `../run.py` (learners, samplers, measures, threshold tuning) rather
than copying them, loads each task with `tasks42.py`, drops rows with a missing value, one-hot encodes nominal
features and uses the minority label of the reference collection as the positive class. Five repetitions of
stratified 5-fold cross-validation (seed 20261110), six learners, 14 ways of handling imbalance: 2,100 cells per task,
one JSON line each, resumable. `--split-folds` makes one job per split for the large tasks.

`stats42.py` fixes the rule of criterion C1 in its docstring (written before any result was read): a method meets C1
when its median difference from SMOTE over families is no worse than -0.01 in ROC-AUC and PR-AUC with the random
forest and gradient boosting. The tests are those of `../stats.py`, imported. A task enters only when all its cells
have run.

## Where the runs are

* Cloud workspace (2 cores), 11 Nov 2026, 11:58 to 13:50 UTC: the 36 tasks of at most 2,308 rows, then
  mammography and ijcnn1 (one job per split); 38 tasks in all, every cell run. Per-fold results: `/home/claude/work/rerun42/results_cloud/` of the
  session's workspace (not in the package; they go into the deposit).
* MacBook (Apple M5 Pro, 15 cores, the machine of the core tier; 14 workers), 11 Nov 2026, 22:46 to 23:50 Bangkok
  time (15:46 to 16:50 UTC), started by the team lead with
  `bash ~/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run/run_benchmark_mac.sh`: phase `03_rerun42.sh` ran the five
  tasks of at least 4,000 rows (promotion, shoppers, mammography, musk, ijcnn1; 125 jobs, no errors, 46 minutes),
  phase `04_pack_rerun42.sh` packed them (`rerun42/results_mac.tgz`), and phase `05_rerun42_kaggle.sh` checked the
  Kaggle file with `rerun42/check_kaggle.py` and ran smoke detection (25 jobs, 18 minutes;
  `rerun42/results_mac_kaggle.tgz`). The two archives were copied into the session's workspace
  (`/home/claude/work/rerun42/mac_results_mac/`, `mac_results_mac_kaggle/`; not in the package, they go into the
  deposit). promotion took 17 to 18 minutes per split on the MacBook (7.4 CPU hours in all, against about 17 estimated
  for a cloud core), shoppers about 4 minutes, musk about 2.
* Mammography and ijcnn1 therefore ran on both machines. `stats42.py` keeps the first copy of a cell it reads, so it is
  given the cloud folder first and the tests use the cloud's copies. `scripts/cross_machine42.py` compares the copies
  (`results_summary/rerun42/cross_machine.json`): the two machines differ in processor and numerical libraries (numpy
  2.5.3 with OpenBLAS on x86 in the cloud, numpy 2.5.4 on Apple silicon; the same scikit-learn, imbalanced-learn,
  imbalanced-learn-extra and smote-variants), and 54% (mammography) and 35% (ijcnn1) of the cells differ in at least
  one of ROC-AUC, PR-AUC, G-mean and the Brier score, but no 25-fold mean differs by more than 0.005 and no
  difference from SMOTE with the random forest or gradient boosting by more than 0.003 (Appendix F).

## Regenerating the paper's numbers

```bash
python3 -I benchmark/rerun42/scripts/stats42.py benchmark "<team-repo>/Data section/difficulty/reference_collection.csv" \
    benchmark/results_summary/rerun42 <results_cloud> <results_mac> <results_mac_kaggle>
python3 -I benchmark/rerun42/scripts/cross_machine42.py --out benchmark/results_summary/rerun42/cross_machine.json \
    --cloud <results_cloud> --mac <results_mac> <results_mac_kaggle>
python3 -I scripts/search_numbers.py .          # rr_* keys
python3 -I scripts/render_search_text.py .      # Section 9.2 (h_rerun) and Appendix F (i_rerun_app)
python3 -I scripts/gen_recommend_table.py .     # Table 17 (gen/table_recommend.tex)
python3 -I scripts/make_supplement.py <team-repo> .   # online appendix S7
python3 -I benchmark/rerun42/scripts/check_claims42.py benchmark/results_summary/rerun42   # the numbers behind each claim
```

`check_claims42.py` prints the numbers behind every claim of Section 9.2 and Appendix F; read them after new tasks
are added and rewrite what no longer holds.

## The TabPFN arm (D43; v0.21 to v0.29)

TabPFN-3.5 without resampling and after SMOTE on the same folds, run on the MacBook on 14 Nov 2026
(`tabpfn_phase/README.md`, which also records the run and its result). Statistics: `scripts/stats42_tabpfn.py` (rule
fixed before any result) and `scripts/tabpfn_cells42.py` (cells by status, fold check, where the strong learners'
cells come from), written to `benchmark/results_summary/rerun42/tabpfn/`; reported in Section 7.5 and online appendix
S7 (Tables S15 and S16).
Under D56 (14 Nov 2026, v0.30) nothing produced by TabPFN-3.5 goes into the deposit: neither its per-fold results nor
the means of `benchmark/results_summary/rerun42/tabpfn/`; the scripts do (`scripts/build_deposit.py` enforces it).
