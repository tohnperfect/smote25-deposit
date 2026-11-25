# WP6.8 step 1: the 42 reference tasks (11 November 2026, 09:20 to 09:30 UTC)

Task list, sources and minority labels: team repository, `Data section/difficulty/reference_collection.csv`.
Checked by `scripts/tasks42.py` against the rows, features and minority count of that table; the result, with the
path and sha256 of every file, is `out/tasks42_check.csv`.

**All 42 tasks pass the check (v0.11).** 41 were fetched in the cloud workspace; the Kaggle task (smoke detection) was downloaded by the team lead with his Kaggle sign-in on 11 Nov 2026 and passed the same check on the MacBook (phase 05 of the runner, `check_kaggle.py`) and in the cloud (`tasks42.py`, byte-identical output).

| Source | Tasks | How fetched (cloud) | Commit or version |
|---|---|---|---|
| KEEL (keel-ds) | 20 | `pip download --no-deps keel-ds==0.2.5` from PyPI, wheel unzipped (`src/kd/`) | 0.2.5, wheel sha256 79faf1bd2f3ac2082d16eb9c8c49b2b1a60a5182e94464c5d32c7c642ea9650e |
| UCI++ (lpfgarcia/ucipp) | 6 | partial git clone, single files from `uci/` | 7a6f2986d7f759c92f6643cbee7c0ffa97768fe7 |
| KEEL standard (Fuminides/keel_datasets) | 1 (balance) | partial git clone, `balance/balance.dat` | 6d4d6fd19a88b60e85e0012cc13848e9b0079f03 |
| Weka UCI (renatopp/arff-datasets) | 1 (breast.cancer) | partial git clone, `classification/breast.cancer.arff` | c59f172882592bb58982cc54d2d3c8a2b57e9b73 |
| HD-Ensemble authors (smallcube/HD-Ensemble) | 1 (ijcnn1) | partial git clone, `datasets/ijcnn1.arff` | ae78b37243391f42475ce485bcbc90c124dfdd3d (the commit the Data section pins) |
| SOS authors (JayoungKim408/SOS) | 1 (shoppers) | partial git clone, `tabular_datasets/shoppers.npz` (read with `allow_pickle=False`) | f1b450cf199d5e0013b401e380008446ef8757f7 (pinned) |
| MBS authors (b10071007/Model-Based-Synthetic-Sampling) | 1 (promotion) | partial git clone, `data/promotion/Promotion_data.csv` | 90020a6a12cf88079942ab4988ba046e1941facd (pinned) |
| PMLB (EpistasisLab/pmlb) | 1 (hepatitis) | `media.githubusercontent.com/.../hepatitis.tsv.gz` | master on 11 Nov 2026 |
| jbrownlee/Datasets | 1 (mammography) | `raw.githubusercontent.com/jbrownlee/Datasets/master/mammography.csv` | master on 11 Nov 2026 |
| k-means SMOTE release (felix-last/evaluate-kmeans-smote v0.0.1) | 8 (pima2, heart6, breast_tissue4, haberman2, iris4, iris6, liver_disorders6, pima6) | the cloud proxy refuses GitHub's release download, so the tarball was downloaded in the Linux VM of the team lead's MacBook (09:31 UTC; sha256 bc0aff0adc079ab01a51d286c070334ca23a393393488a6fee441cf3cd0225cf, the value the Data section pins); only the 8 CSV files were extracted (no `._` files), saved to `~/Downloads/SMOTE25/benchmark/reference42_kmeans/` with a README and their sha256, and staged into `src/files/author-kmeans/` | v0.0.1 |
| Kaggle | 1 (smoke detection) | downloaded by the team lead with his Kaggle sign-in on 11 Nov 2026, about 22:50 Bangkok time (deepcontractor/smoke-detection-dataset, `smoke_detection_iot.csv`, as the Data section did), saved to `~/Downloads/SMOTE25/benchmark/reference42_kaggle/` and staged into `src/files/Kaggle/`; sha256 7bbf5deaab4c94746b344cee7bfec493f69b7d624ea63f35fabcd3c4a4e6eb7d. It is the largest task (62,630 rows) | |

Two counting conventions in the Data section's table: for promotion (1,185 rows with missing values) and
breast.cancer (9) its N and n_min count the rows left after dropping rows with missing values; for cleveland-0_vs_4
(4 such rows) they count all rows. Every other task has no missing value. How the rerun treats those rows (drop them before the split, as the
Data section's measures do, or impute inside each training fold) is to be fixed in its protocol and stated in the
paper.

pima exists twice in keel-ds (`balanced/raw/pima.dat` with labels tested_positive/tested_negative and
`imbalanced/raw/pima.dat` with positive/negative); the loader takes the file whose labels hold the minority label of
the table (`positive`), as the Data section's counts imply.

The downloads in `src/` are untrusted data: they are read only by `scripts/tasks42.py` with `python3 -I`, and the
SOS file is read without unpickling.

## Next (from `docs/RERUN-PLAN-table16.md`)

1. Done (11 Nov 2026): the Kaggle CSV from the team lead (`~/Downloads/SMOTE25/benchmark/reference42_kaggle/smoke_detection_iot.csv`),
   then `scripts/tasks42.py` again (42 of 42 ok).
2. Done (v0.9): CGMOS, SMOM, AB-SMOTE, RSMOTE and FW-SMOTE implemented, each validated against a number printed in its
   paper (`benchmark/rerun42/methods/README.md`).
3. Done (v0.10 and v0.11): the ten methods and the baselines run under the protocol of the independent benchmark on all
   42 tasks (`benchmark/rerun42/README.md`).
