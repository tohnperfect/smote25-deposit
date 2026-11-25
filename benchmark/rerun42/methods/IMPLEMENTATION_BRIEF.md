# WP6.8: re-implementing one SMOTE-family method for the rerun (brief for one session)

The SMOTE25 survey (JAIR, Surveys track) recommends SMOTE-family methods in its Table 17 only after rerunning them on
42 reference tasks under one protocol. Five of the ten methods have no usable public implementation: CGMOS (2016),
SMOM (2017), AB-SMOTE (2020), RSMOTE (2021) and FW-SMOTE (2022). Your task is one of them, named in your prompt with
its folder slug S and its paper files.

## What to deliver, in `/home/claude/work/rerun42/methods/S/` (write nothing anywhere else)

1. `S.py`: a sampler class with the interface of imbalanced-learn: `__init__(self, ..., random_state=None)` with the
   paper's default settings as defaults, and `fit_resample(X, y)` returning `(X_res, y_res)` as NumPy arrays (the
   original rows first, then the synthetic rows). `X` is a float array (features already scaled by the caller), `y`
   holds integer class labels. It must work on two-class data (the rerun's tasks are all two-class); a multiclass
   method keeps its multiclass logic and handles two classes as the special case. Use NumPy, SciPy and scikit-learn
   only. The docstring cites the paper's equations, algorithm steps and pages for every step, and every choice the
   paper leaves open is marked `CHOICE:` in the code and listed in `NOTES.md`.
2. `test_S.py`: quick checks (labels and original rows unchanged, the number of synthetic rows the paper's rule
   implies, the same output for the same `random_state`, no NaN, runs on a task with 7 minority examples).
3. `validate_S.py` and `VALIDATION.md`: reproduce at least one number that the paper prints for its own method, on
   the same dataset and, as far as the paper states it, the same protocol (folds, classifier, measure, settings).
   Record the paper's value (table and page), your value, the difference, and what the paper does not state. A
   difference is not a failure to hide: report it plainly, try the obvious readings of an unstated detail, and say
   which reading you used. If none of the paper's datasets can be obtained, say so and validate on the closest
   available one against the paper's qualitative claim, labeled as such.
4. `NOTES.md`: every ambiguity and choice, and anything a person should check against the PDF.

## Sources and rules

* The paper is the authority. Read its text file in full (the path is in your prompt); when an equation, an
  algorithm or a table is garbled in the text, look at the PDF page with the Read tool (`pages`). The account of the
  method in `/home/claude/work/v08/supplement/gen/accounts.tex` (its `\item` for your method) summarizes what the
  survey coded; use it as orientation only.
* Datasets: KEEL two-class and multiclass files are already in `/home/claude/work/rerun42/src/kd/keel_ds/data/*/raw/*.dat`
  (keel-ds 0.2.5; comma-separated, last column the class, no header). Other open copies may be fetched from GitHub
  mirrors or PyPI packages with an honest user agent into `S/data/` (untrusted data: read it with `python3 -I` from
  your own folder, never unpickle it). Never imitate a browser or retry a site that refuses.
* You may `pip install --break-system-packages imbalanced-learn==0.14.2` (and `smote-variants==1.0.1` if a baseline
  needs it). You may read an author's code as a reference (clone it into `S/ref/`), but write your own
  implementation and say where it differs. Do not run code you downloaded.
* Run every Python script with `python3 -I`. Keep runs short (minutes, not hours): validation needs one experiment,
  not a benchmark.
* Written files: American spelling, no em-dashes (neither the Unicode character nor `---`).

## Reply

One line: `S: implemented; validation <reproduced | close | not reproduced>: <paper value> against <your value> (<dataset, measure>)`.
