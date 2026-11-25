# RBO: project page checked for the spot check (15 November 2026)

The spot check of the WP3 adjudication (D31; page "SMOTE25 WP3 Check", export of 15 November 2026) agreed with 79 of
its 80 items and marked one for change: RBO, field "modified files themselves public" (D36), AI adjudication "no",
with the request "Check the project page" and the note "Try to access". This file records the check.

## The page the paper names

Koziarski, Krawczyk and Woźniak, Neurocomputing 343 (2019), Section 4.1 ("Implementation and reproducibility", PDF
p.7) points in footnote 1 to `https://github.com/michalkoziarski/RBO` for its code, and says the fold partitions and
the full results are there too.

## What the page holds (accessed 15 November 2026)

The repository is public. A session read the GitHub page and cloned it (`git clone --depth 1`; one branch, `master`,
last commit `93528e765e14e7447eefcacc5c06085482f4e70e` of 12 March 2018; 68 files, 23 MB). Nothing in it was run.

| Path | Files | What they are |
|---|---|---|
| `algorithms.py`, `datasets.py`, `run.py`, `databases.py`, `slurm.sh`, `spawn_n.sh`, `README.md`, `.gitignore` | 8 | code and instructions |
| `data_urls/final.txt`, `data_urls/preliminary.txt` | 2 | 34 download links (24 final, 10 preliminary), all to the KEEL imbalanced repository (the original files) |
| `experiments/schedule_final.py`, `experiments/schedule_preliminary.py` | 2 | the experiment grid: noise type none, class (0.05 to 0.20) or attribute (0.1 to 0.5) |
| `folds/*.folds.pickle` | 34 | the 5x2 cross-validation partitions, one file per dataset |
| `results/final.csv`, `results/preliminary.csv` | 2 | per-fold precision, recall, F-measure, AUC and G-mean |
| `results/preliminary - visualizations/` | 20 | figures of the preliminary analysis |

The fold files were read with Python's `pickletools` (which lists a pickle's operations without loading it): each
holds nested lists of NumPy integer arrays (dtype `i8`; for `pima`, arrays of 384 row numbers), the train and test row
indices that `partition()` in `datasets.py` draws. They hold no feature values and no labels.

`datasets.py` downloads the KEEL files, reads the folds, scales the features, and only then adds the noise to the
training part of each fold (`make_folds()`): class noise relabels majority objects as minority with probability equal
to the noise level, and attribute noise adds Gaussian noise with a spread set by the noise level. The noise is drawn with
`np.random` and no seed is set anywhere in the code.

## Result

The noisy training sets, the files the paper modified, are not on the page: the code makes them at run time and, with no
fixed seed, could not remake them exactly. Under D36 (the modified files themselves must be public; code that regenerates
them does not count) the adjudication stays **no**, now with high confidence. `adjudicate_d36.py` records this in `SPOT`;
its outputs change only in RBO's confidence, note and `decided_by`, and in a `spot_check` entry of
`MODIFIED_RELEASED_summary.json`. No number of the paper changes: 9 of the 44 papers that modify data publish the modified
files (Table 5).
