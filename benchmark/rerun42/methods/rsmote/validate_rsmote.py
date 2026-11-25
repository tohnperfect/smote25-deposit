"""Validation of rsmote.RSMOTE against Table 3 (and Table 4) of Chen et al. (2021).

Paper protocol (Sec. 4.3.2, pp. 408-409), followed where stated:
  * every data set is split at random into 75% training and 25% test, the
    majority and the minority class separately (a stratified split);
  * label noise at rate c is added to the training part only: c|P| minority
    labels flipped to majority, then as many majority labels flipped to
    minority (pp. 408-409); c = 0 is Table 3 (p. 410), c = 0.3 Table 4 (p. 411);
  * the oversampler sees the training part only (Algorithm 1 input: "Training
    set D", p. 403);
  * five classifiers with default parameters: AdaBoost, LR, DT, KNN, GBDT;
  * oversampler parameter knn enumerated over {3, 5, 20} "to obtain the best
    result" (p. 409);
  * five repetitions, scores averaged; Tables 3 and 4 report the average
    "across five classifiers" (p. 409) of Precision, Recall, AUC, F1 and
    G-mean (Eqs. 3-6, p. 404) of the minority class.
Not stated, so several readings are run (see VALIDATION.md):
  * test fraction: 0.25 as stated, and 0.20, because the paper's own recall
    values for ecoli, heart and iris only fit 20% of the minority class in
    each test part (11, 24 and 10 samples, not 13, 30 and 13);
  * feature scaling: none, or min-max fitted on the training part;
  * AUC from predicted probabilities or from the hard predictions;
  * how the best k is chosen: per data set and measure, or per data set,
    measure and classifier; fixed k = 5 is shown too;
  * diagnostic only, NOT the paper's protocol: oversampling the whole data
    set before the split ("leak");
  * diagnostic only, NOT the paper's reading of RSMOTE: also deleting the rows
    RSMOTE flags as noise from the training data ("dropnoise"; run with
    --pipelines dropnoise --raw validation_raw_dropnoise.csv).
Data: the KEEL copies of the five Table 2 sets whose size and class counts
match exactly: ecoli (KEEL ecoli2: pp vs rest), pima, heart, vehicle (KEEL
vehicle0: van vs rest), wine (class 2 vs rest).

Run: python3 -I validate_rsmote.py [--noise 0 0.3] [--datasets ecoli pima ...]
Writes validation_raw.csv next to this file and prints the tables.
python3 -I validate_rsmote.py --summarize-only reprints them from that file.
"""

import argparse
import os
import sys
import time
import warnings

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rsmote import RSMOTE  # noqa: E402

from imblearn.over_sampling import SMOTE  # noqa: E402  (baseline only)
from joblib import Parallel, delayed  # noqa: E402
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import confusion_matrix, roc_auc_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402
from sklearn.preprocessing import MinMaxScaler  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

KEEL = "/home/claude/work/rerun42/src/kd/keel_ds/data"
DATASETS = {  # name: (file, minority class value)
    "ecoli": (f"{KEEL}/imbalanced/raw/ecoli2.dat", "positive"),
    "pima": (f"{KEEL}/balanced/raw/pima.dat", "tested_positive"),
    "heart": (f"{KEEL}/balanced/raw/heart.dat", "2"),
    "vehicle": (f"{KEEL}/imbalanced/raw/vehicle0.dat", "positive"),
    "wine": (f"{KEEL}/balanced/raw/wine.dat", "2"),
}
TABLE2 = {"ecoli": (336, 284, 52, 7), "pima": (768, 500, 268, 8), "heart": (270, 150, 120, 13),
          "vehicle": (846, 647, 199, 18), "wine": (178, 107, 71, 13)}
# Paper values for RSMOTE ("RSMT.") and SMOTE ("SMT."), order P, R, AUC, F1, G.
PAPER = {
    0.0: {  # Table 3, p. 410
        "ecoli": {"RSMOTE": (0.893, 1.000, 0.996, 0.942, 0.988), "SMOTE": (0.505, 0.673, 0.834, 0.558, 0.751),
                  "NONE": (0.667, 0.509, 0.829, 0.543, 0.679)},
        "heart": {"RSMOTE": (0.942, 0.950, 0.984, 0.946, 0.951), "SMOTE": (0.672, 0.833, 0.820, 0.743, 0.748),
                  "NONE": (0.691, 0.833, 0.833, 0.754, 0.762)},
        "pima": {"RSMOTE": (0.714, 0.837, 0.886, 0.770, 0.825), "SMOTE": (0.595, 0.700, 0.790, 0.643, 0.721),
                 "NONE": (0.682, 0.578, 0.797, 0.623, 0.700)},
        "vehicle": {"RSMOTE": (0.918, 1.000, 0.996, 0.956, 0.985), "SMOTE": (0.824, 0.975, 0.981, 0.892, 0.954),
                    "NONE": (0.922, 0.880, 0.978, 0.898, 0.926)},
        "wine": {"RSMOTE": (1.000, 1.000, 1.000, 1.000, 1.000), "SMOTE": (0.949, 0.973, 0.982, 0.961, 0.968),
                 "NONE": (1.000, 0.933, 0.985, 0.965, 0.966)},
    },
    0.3: {  # Table 4, p. 411
        "ecoli": {"RSMOTE": (0.376, 0.982, 0.913, 0.543, 0.819), "SMOTE": (0.238, 0.782, 0.699, 0.364, 0.630),
                  "NONE": (0.216, 0.509, 0.722, 0.301, 0.517)},
        "heart": {"RSMOTE": (0.682, 0.767, 0.807, 0.722, 0.739), "SMOTE": (0.575, 0.783, 0.742, 0.662, 0.645),
                  "NONE": (0.605, 0.758, 0.744, 0.672, 0.674)},
        "pima": {"RSMOTE": (0.563, 0.715, 0.751, 0.629, 0.707), "SMOTE": (0.465, 0.652, 0.671, 0.542, 0.619),
                 "NONE": (0.511, 0.604, 0.683, 0.549, 0.632)},
        "vehicle": {"RSMOTE": (0.494, 0.850, 0.867, 0.624, 0.788), "SMOTE": (0.422, 0.805, 0.814, 0.553, 0.725),
                    "NONE": (0.620, 0.755, 0.866, 0.669, 0.792)},
        "wine": {"RSMOTE": (0.777, 0.880, 0.903, 0.825, 0.853), "SMOTE": (0.585, 0.760, 0.780, 0.660, 0.694),
                 "NONE": (0.789, 0.800, 0.845, 0.791, 0.820)},
    },
}
MEASURES = ("precision", "recall", "auc", "f1", "gmean")
KS = (3, 5, 20)
REPS = 5
CLASSIFIERS = ("Adaboost", "LR", "DT", "KNN", "GBDT")


def load(name):
    path, minority = DATASETS[name]
    rows = [ln.strip() for ln in open(path) if ln.strip() and not ln.startswith("@")]
    cells = [[c.strip() for c in r.split(",")] for r in rows]
    X = np.array([[float(v) for v in c[:-1]] for c in cells])
    y = np.array([1 if c[-1] == minority else 0 for c in cells])
    return X, y


def make_classifier(name, seed):
    return {"Adaboost": lambda: AdaBoostClassifier(random_state=seed),
            "LR": lambda: LogisticRegression(),
            "DT": lambda: DecisionTreeClassifier(random_state=seed),
            "KNN": lambda: KNeighborsClassifier(),
            "GBDT": lambda: GradientBoostingClassifier(random_state=seed)}[name]()


def add_label_noise(y, c, rng):
    """Pp. 408-409: flip c|P| minority labels to majority, then as many
    majority labels to minority.  CHOICE (unstated): the count is rounded,
    and the second flip draws from the original majority samples."""
    y = y.copy()
    n_flip = int(round(c * np.sum(y == 1)))
    if n_flip == 0:
        return y
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    to_neg = rng.choice(pos, n_flip, replace=False)
    to_pos = rng.choice(neg, n_flip, replace=False)
    y[to_neg], y[to_pos] = 0, 1
    return y


def scores(y_true, y_pred, y_score):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "gmean": np.sqrt(rec * spec),
            "auc": roc_auc_score(y_true, y_score), "auc_label": roc_auc_score(y_true, y_pred)}


def resample(sampler, k, X, y, seed, drop_noise=False):
    if sampler == "NONE":
        return X, y
    if sampler == "SMOTE":
        return SMOTE(k_neighbors=k, random_state=seed).fit_resample(X, y)
    rs = RSMOTE(k_neighbors=k, random_state=seed)
    X_res, y_res = rs.fit_resample(X, y)
    if drop_noise:  # diagnostic: delete the flagged rows too (not the paper's reading)
        keep = np.ones(len(y_res), dtype=bool)
        for info in rs.info_.values():
            keep[info["noise_index"]] = False
        X_res, y_res = X_res[keep], y_res[keep]
    return X_res, y_res


def one_cell(name, rep, scaling, pipeline, noise, test_size):
    """All samplers x k x classifiers for one data set, repetition, reading."""
    warnings.simplefilter("ignore")
    X, y = load(name)
    out = []
    configs = [("NONE", 0)] + [(s, k) for s in ("SMOTE", "RSMOTE") for k in KS]
    if pipeline == "leak":
        configs = configs[1:]
    if pipeline == "dropnoise":
        configs = [("RSMOTE", k) for k in KS]
    for sampler, k in configs:
        rng = np.random.RandomState(1000 + rep)
        if pipeline in ("paper", "dropnoise"):
            X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, stratify=y, random_state=rep)
            y_tr = add_label_noise(y_tr, noise, rng)
            if scaling == "minmax":
                sc = MinMaxScaler().fit(X_tr)
                X_tr, X_te = sc.transform(X_tr), sc.transform(X_te)
            X_fit, y_fit = resample(sampler, k, X_tr, y_tr, rep, drop_noise=(pipeline == "dropnoise"))
        else:  # diagnostic: oversample everything, then split the result
            X_all = MinMaxScaler().fit_transform(X) if scaling == "minmax" else X
            y_all = add_label_noise(y, noise, rng)
            X_os, y_os = resample(sampler, k, X_all, y_all, rep)
            X_fit, X_te, y_fit, y_te = train_test_split(X_os, y_os, test_size=test_size, stratify=y_os,
                                                        random_state=rep)
        for clf_name in CLASSIFIERS:
            clf = make_classifier(clf_name, rep).fit(X_fit, y_fit)
            proba = clf.predict_proba(X_te)[:, 1]
            sc_ = scores(y_te, clf.predict(X_te), proba)
            out.append(dict(dataset=name, noise=noise, test_size=test_size, rep=rep, scaling=scaling,
                            pipeline=pipeline, sampler=sampler, k=k, clf=clf_name, **sc_))
    return out


def summarize(rows, name, noise, scaling, pipeline, auc_key, test_size):
    """Table value per sampler: mean over classifiers and repetitions; for the
    oversamplers also the best-k readings."""
    sel = [r for r in rows if r["dataset"] == name and r["noise"] == noise and r["scaling"] == scaling
           and r["pipeline"] == pipeline and r["test_size"] == test_size]
    keys = ["precision", "recall", auc_key, "f1", "gmean"]

    def mean_of(sampler, k, clf=None):
        rr = [r for r in sel if r["sampler"] == sampler and r["k"] == k and (clf is None or r["clf"] == clf)]
        return np.array([np.mean([r[m] for r in rr]) for m in keys]) if rr else None

    res = {}
    if pipeline == "paper":
        res[("NONE", "-")] = mean_of("NONE", 0)
    for s in ("SMOTE", "RSMOTE"):
        if not any(r["sampler"] == s for r in sel):
            continue
        per_k = np.array([mean_of(s, k) for k in KS])
        res[(s, "k=5")] = per_k[KS.index(5)]
        res[(s, "best k")] = per_k.max(axis=0)
        per_clf = np.array([[mean_of(s, k, c) for k in KS] for c in CLASSIFIERS])   # clf x k x measure
        res[(s, "best k per clf")] = per_clf.max(axis=1).mean(axis=0)
    return res


def compact(rows, args):
    """Short tables used in VALIDATION.md."""
    names = [n for n in args.datasets if n in PAPER[0.0]]
    labels = ("P", "R", "AUC", "F1", "G")

    def fmt(v):
        return ", ".join(f"{x:.3f}" for x in v)

    if "dropnoise" in args.pipelines:
        for c in args.noise:
            print(f"\n## Compact, c = {c}: diagnostic, RSMOTE with the flagged rows also deleted (NOT the paper's "
                  "reading), 75/25, no scaling, best k")
            print("| data | paper RSMOTE P, R, AUC, F1, G | ours, flagged rows deleted |")
            print("|--|--|--|")
            for name in names:
                summ = summarize(rows, name, c, "none", "dropnoise", "auc", args.test_sizes[0])
                print(f"| {name} | {fmt(PAPER[c][name]['RSMOTE'])} | {fmt(summ[('RSMOTE', 'best k')])} |")
    if "paper" not in args.pipelines:
        return
    for c in args.noise:
        print(f"\n## Compact, c = {c}: stated protocol (75/25, no scaling, AUC from probabilities)")
        print("RSMOTE, best k per data set and measure, against the paper; then the same for SMOTE and NONE.")
        print("| data | method | paper P, R, AUC, F1, G | ours | ours minus paper |")
        print("|--|--|--|--|--|")
        for name in names:
            summ = summarize(rows, name, c, "none", "paper", "auc", 0.25)
            for samp, key in (("RSMOTE", "best k"), ("SMOTE", "best k"), ("NONE", "-")):
                paper = np.array(PAPER[c][name][samp])
                ours = summ[(samp, key)]
                print(f"| {name} | {samp} | {fmt(paper)} | {fmt(ours)} | "
                      + ", ".join(f"{x:+.3f}" for x in ours - paper) + " |")
        print(f"\n## Compact, c = {c}: RSMOTE AUC and F1 under every reading (best k per data set and measure)")
        print("| data | paper AUC | 75/25 none | 75/25 minmax | 80/20 none | 80/20 minmax | paper F1 | "
              "75/25 none | 75/25 minmax | 80/20 none | 80/20 minmax |")
        print("|--|--|--|--|--|--|--|--|--|--|--|")
        for name in names:
            cells_auc, cells_f1 = [], []
            for t in args.test_sizes:
                for s in args.scalings:
                    v = summarize(rows, name, c, s, "paper", "auc", t)[("RSMOTE", "best k")]
                    cells_auc.append(v[2])
                    cells_f1.append(v[3])
            print(f"| {name} | {PAPER[c][name]['RSMOTE'][2]:.3f} | " + " | ".join(f"{x:.3f}" for x in cells_auc)
                  + f" | {PAPER[c][name]['RSMOTE'][3]:.3f} | " + " | ".join(f"{x:.3f}" for x in cells_f1) + " |")
        print(f"\n## Compact, c = {c}: RSMOTE minus SMOTE (best k each), paper against ours "
              "(75/25, no scaling)")
        print("| data | paper: " + ", ".join(labels) + " | ours: " + ", ".join(labels) + " |")
        print("|--|--|--|")
        for name in names:
            summ = summarize(rows, name, c, "none", "paper", "auc", 0.25)
            d_paper = np.array(PAPER[c][name]["RSMOTE"]) - np.array(PAPER[c][name]["SMOTE"])
            d_ours = summ[("RSMOTE", "best k")] - summ[("SMOTE", "best k")]
            print(f"| {name} | " + ", ".join(f"{x:+.3f}" for x in d_paper) + " | "
                  + ", ".join(f"{x:+.3f}" for x in d_ours) + " |")
        if "leak" in args.pipelines:
            print(f"\n## Compact, c = {c}: diagnostic, oversampling before the split (NOT the paper's protocol), "
                  "no scaling, best k")
            print("| data | paper RSMOTE | ours RSMOTE (leak) | paper SMOTE | ours SMOTE (leak) |")
            print("|--|--|--|--|--|")
            for name in names:
                summ = summarize(rows, name, c, "none", "leak", "auc", args.test_sizes[0])
                print(f"| {name} | {fmt(PAPER[c][name]['RSMOTE'])} | {fmt(summ[('RSMOTE', 'best k')])} | "
                      f"{fmt(PAPER[c][name]['SMOTE'])} | {fmt(summ[('SMOTE', 'best k')])} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="*", default=list(DATASETS))
    ap.add_argument("--noise", nargs="*", type=float, default=[0.0, 0.3])
    ap.add_argument("--scalings", nargs="*", default=["none", "minmax"])
    ap.add_argument("--pipelines", nargs="*", default=["paper", "leak"])
    ap.add_argument("--test-sizes", nargs="*", type=float, default=[0.25, 0.2])
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--summarize-only", action="store_true",
                    help="read the raw file instead of running the experiment")
    ap.add_argument("--raw", default="validation_raw.csv", help="raw results file in this folder")
    args = ap.parse_args()
    raw_path = os.path.join(HERE, args.raw)

    for name in args.datasets:
        X, y = load(name)
        print(f"{name}: n={len(y)} majority={np.sum(y == 0)} minority={np.sum(y == 1)} d={X.shape[1]}"
              f"  (Table 2: {TABLE2[name]})")
    import csv
    if args.summarize_only:
        with open(raw_path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            for key in ("noise", "test_size") + MEASURES + ("auc_label",):
                r[key] = float(r[key])
            for key in ("rep", "k"):
                r[key] = int(r[key])
        print(f"{len(rows)} classifier runs read from {args.raw}")
    else:
        t0 = time.time()
        # the leak diagnostic is run with the first (stated) test fraction only
        jobs = [(n, r, s, p, c, t) for n in args.datasets for c in args.noise for s in args.scalings
                for p in args.pipelines for t in (args.test_sizes if p in ("paper", "dropnoise")
                                                  else args.test_sizes[:1])
                for r in range(REPS)]
        chunks = Parallel(n_jobs=args.jobs)(delayed(one_cell)(*j) for j in jobs)
        rows = [r for ch in chunks for r in ch]
        print(f"{len(rows)} classifier runs in {time.time() - t0:.0f} s")
        with open(raw_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    compact(rows, args)

    for c in args.noise:
        for p in args.pipelines:
            for t in (args.test_sizes if p in ("paper", "dropnoise") else args.test_sizes[:1]):
                for s in args.scalings:
                    for auc_key in ("auc", "auc_label"):
                        print(f"\n### c = {c}, pipeline = {p}, test fraction = {t}, scaling = {s}, AUC from "
                              f"{'probabilities' if auc_key == 'auc' else 'hard labels'}")
                        print("| data | sampler | reading | Precision | Recall | AUC | F1 | G-mean |")
                        print("|--|--|--|--|--|--|--|--|")
                        for name in args.datasets:
                            paper = PAPER.get(c, {}).get(name, {})
                            for samp in ("NONE", "SMOTE", "RSMOTE"):
                                if samp in paper and p == "paper":
                                    print(f"| {name} | {samp} | paper | "
                                          + " | ".join(f"{v:.3f}" for v in paper[samp]) + " |")
                            for (samp, reading), v in summarize(rows, name, c, s, p, auc_key, t).items():
                                print(f"| {name} | {samp} | {reading} | " + " | ".join(f"{x:.3f}" for x in v) + " |")


if __name__ == "__main__":
    main()
