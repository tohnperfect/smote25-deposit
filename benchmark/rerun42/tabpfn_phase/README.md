# The TabPFN arm of the rerun (D43), prepared 14 Nov 2026, revised for v0.24 and v0.25

TabPFN (a tabular foundation model) with its defaults, without resampling and after SMOTE, on the 42 tasks of the
reference collection, with the same folds as the rerun of Table 17. The statistics are fixed in `stats42_tabpfn.py`
before any result exists: TabPFN after SMOTE against TabPFN alone, and TabPFN alone against the random forest and
gradient boosting with and without SMOTE, by ROC-AUC, PR-AUC and the Brier score, over families of tasks.

**Model and license.** The TabPFN package 10.0.0 (pinned) uses TabPFN-3.5 by default (`ModelVersion.V3_5`); `run42.py`
records the package, the model and the device in `config.json`. Its weights download only for an account that has
accepted the TabPFN-3.5 license at Prior Labs. The team lead accepted it on 14 Nov 2026 (https://platform.priorlabs.ai,
Licenses) and created an API key named "SMOTE25 TabPFN rerun", which expires after 30 days. The license allows
non-commercial research, academic benchmarking included; it bars commercial and production use, surveillance and
biometric processing, and distributing the weights without its notice. The weights stay out of every package and the
deposit. The license calls predictions "Outputs" and lets them be used for non-commercial purposes; since the
deposit's data carry CC BY 4.0, the authors decided on 14 Nov 2026 (D56, v0.30) that nothing produced by TabPFN-3.5
goes into the deposit: neither the results per fold nor the means of `benchmark/results_summary/rerun42/tabpfn/`.
The arm's scripts are deposited, and `build_deposit.py` stops on any TabPFN cell.

**The key.** Passed only as `TABPFN_TOKEN` in the environment of a run, never written down. TabPFN 10.0.0 copies a
valid key to `~/.cache/tabpfn/auth_token`; `run42.py` switches that copy off (since v0.24), and `TABPFN_NO_BROWSER=1`
stops the package from opening a browser login.

**Where it runs (v0.24): all 42 tasks on the MacBook.** Measured on 14 Nov: in the cloud workspace (two CPU cores) one
fit and prediction took 24.5 s at 1,280 training rows, about seven hours for the 36 small tasks alone, so the plan of
v0.21 (36 tasks in the cloud, six on the MacBook) was dropped. In Terminal on the MacBook:
`bash ~/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run/tabpfn_phase/run_tabpfn_mac.sh` (this folder copied to
`~/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run/tabpfn_phase/`). It makes its own Python environment in the
folder, asks for the key, runs the 36 tasks of at most 2,308 rows and then the six of at least 4,000 rows (one job per
split) on the Apple GPU, and packs `results_tabpfn_mac.tgz`. It reads `tasks42_check_kaggle.csv`, which marks all 42
tasks available. Rerunning it resumes: finished cells are kept. A task beyond TabPFN's limits fails in every cell and
is reported, not subsampled.

**Fixed in v0.25, after the first start on the MacBook (14 Nov, 16:15 to about 16:40 local time; nothing of it is a result).** (1) The Python environment lacked numpy after an interrupted install: the script now installs the packages whenever one of them fails to import. (2) The data files of the 36 small tasks existed only in the cloud workspace, so every small task failed with `FileNotFoundError`: the 36 files were copied to the MacBook's `rerun42/src` (hashes checked). (3) The splits of smoke detection ran out of Apple GPU memory when predicting 12,526 test rows at once: `run42.py` now predicts in batches of 500 rows. TabPFN's test rows attend to the training rows only, not to each other, so batching does not change the predictions. (4) Rerunning drops the cells that ended in an error, and any half-written line, before it starts, so they run again; finished cells are kept. The fixes need a fresh start of the script (Ctrl+C, then the command above).

Corrected in v0.24: the script of v0.21 ran its second command on `tasks42_check_kaggle.csv` without a size limit,
which would have run the 36 small tasks on the MacBook as well; it never ran.

**Then** (a session): `python3 -I stats42_tabpfn.py "<team-repo>/Data section/difficulty/reference_collection.csv"
<out> <TabPFN results dir> <rerun results dirs...>` (the TabPFN cells from the first directory, the random forest
and gradient boosting cells from the rerun's directories). The TabPFN cells come from the MacBook and the rerun's
random forest and gradient boosting cells of the 36 small tasks from the cloud, so each comparison across learners
mixes the two machines; the folds are the same (one seed), and for the two tasks the rerun ran on both machines the
25-fold means of each learner agreed within 0.005 (Appendix D). Section 7.5 and online appendix S7 report the arm.

**The run (14 Nov 2026).** The first start (about 16:15 local time) ran with the code of v0.24 and gave the cells of
promotion, shoppers and mammography, of musk after SMOTE and of ijcnn1 without resampling; the team lead started the
fixed script again at 18:27 local time, and it finished at 21:02:58 (`run_mac.log`: 150 jobs of the large tasks, none reported as failed). It packed
`results_tabpfn_mac.tgz` (1,850,847 bytes, MD5 5e5f37cccf951e70dd1b67360f39fef3), which a session copied to the cloud
workspace the same evening; the archive stays on the MacBook and does not go into the deposit (D56, above). `config.json`: package 10.0.0, `ModelVersion.V3_5`, device `mps`. Of the 2,100 cells, 1,990 gave a result:
75 ran out of the Apple GPU's memory even in batches of 500 test rows (musk without resampling, 25 cells, at 5,278
training rows and 167 features; smoke detection with and without SMOTE, 50 cells, at 50,104 training rows) and 35 are
SMOTE runs on training folds with too few minority examples for five neighbors (ijcnn1, all 25; ecoli-0-1-3-7_vs_2-6,
10 of 25), as in the rerun. The fold files are the rerun's (all 42 identical). The cells that gave a result took 2.09
hours.

**Result (v0.29).** `stats42_tabpfn.py` and `tabpfn_cells42.py` (both in `benchmark/rerun42/scripts/`) wrote
`benchmark/results_summary/rerun42/tabpfn/`: under the rule fixed before the results, a task enters only when all its
50 cells gave a result, so the comparisons use 38 tasks in 28 families. TabPFN after SMOTE against TabPFN alone: median
difference over families -0.017 in ROC-AUC, -0.032 in PR-AUC, and a Brier score higher by 0.012 (Holm-adjusted
Wilcoxon p 0.016, 0.006 and below 0.001; Bayesian probability that TabPFN alone is better 0.98, 1.00 and 0.82).
TabPFN alone against the random forest and gradient boosting, without resampling and after SMOTE: higher ROC-AUC by
0.014 to 0.028 and PR-AUC by 0.024 to 0.046 (Holm-adjusted p below 0.03), a lower Brier score by 0.013 to 0.027
except against the random forest without resampling (0.006, on par within 0.01). The random forest and gradient
boosting cells come from the rerun: 36 of the 38 tasks from the cloud workspace, promotion and shoppers from the
MacBook. Written into Section 7.5 (rendered from `scripts/search_templates/j_tabpfn.tex`, whose wording
`search_numbers.py` checks) and online appendix S7 (Tables S15 and S16, generated by `make_supplement.py`). A rerun of
the failed cells of musk and smoke detection would need more GPU memory than the MacBook has, or its CPU
(`SMOTE25_TABPFN_DEVICE=cpu`), which was not tried.

Tests: the plumbing ran on 14 Nov with a stand-in model (`SMOTE25_TABPFN_STANDIN=1`) on three small tasks, and with
the real model in the cloud on four tasks of at most 120 rows, one split each (about 1 to 2 s per fit; no key file was
written). Neither run is a result, and neither was kept.
