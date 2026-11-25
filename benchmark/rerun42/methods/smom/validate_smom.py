"""Validation of smom.SMOM against numbers printed by Zhu, Lin and Liu (2017).

Run: python3 -I validate_smom.py [--runs 10] [--datasets vowel7,vowel5,vehicle]

Paper protocol (p. 335, Sec. 4.1): "The performance results on each data set are obtained from the
average of 10 independent runs with stratified 10-fold cross validation"; all classes oversampled
to the size of the largest one; standardized Euclidean distance; SMOM with k1 = 12, k2 = 8,
rTh = 5/8, nTh = 10, w1 = 0.2, w2 = 1/2, r1 = 1/3, r2 = 0.2; base classifiers built in Weka; "NB
employs supervised discretization". Measures: MG (geometric mean of the recalls of all classes),
MAUC (Hand and Till), recall and precision of the smallest class.

Classifier here: a re-implementation of Weka 3.8 NaiveBayes with useSupervisedDiscretization
(weka.filters.supervised.attribute.Discretize with its defaults, i.e. Fayyad and Irani's MDL
criterion with numCutPoints = N - 1, and DiscreteEstimator with Laplace counts for the class prior
and every discretized attribute). No Weka code is run.

Data sets (Table 1, p. 334), rebuilt from the local KEEL files (keel-ds 0.2.5):
  vowel5  990 x 10, classes '0'&'1' / '2' / '3'&'4'&'5'&'6' / '7'&'8'&'9' / '10' = 180/90/360/270/90
  vowel7  990 x 10, classes '0' / '1'&'2' / '3' / '4'&'5' / '6' / '7'&'8' / '9'&'10' = 90/180/90/180/90/180/180
  vehicle 846 x 18, van / saab&opel / bus = 199/429/218
The vowel features are F0..F9 (the KEEL columns TT, SpeakerNumber and Sex are dropped: Table 1
gives 10 features).

Methods: NONE (no oversampling), SMOTE (imbalanced-learn 0.14.2, k = 5, the paper's default for
SMOTE, on the training fold standardized like the paper's distance) and SMOM (this folder's
smom.py, paper defaults). SMOTE is a control: it separates the gap caused by the classifier and the
folds from the gap caused by SMOM.

Output: a table on stdout and validation_results.json in this folder.
"""

import argparse
import json
import os
import sys
import time

import numpy as np
from scipy.stats import rankdata
from sklearn.model_selection import StratifiedKFold

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from smom import SMOM  # noqa: E402

KEEL = "/home/claude/work/rerun42/src/kd/keel_ds/data/balanced/raw"

# Paper values, Supp. Table S4 (MG, Supp. p. 8), S6 (MAUC, Supp. p. 10), S8 (recall of the smallest
# class, Supp. p. 12), S10 (precision of the smallest class, Supp. p. 14). Block "A" is headed "NB"
# in S4-S10 but is the "MLP" block of the main paper's Table 2 (p. 335) and of Table S13; block "B"
# is headed "MLP" in S4-S10 and "NB" in Table 2 and Table S13 (see VALIDATION.md).
PAPER = {
    "vowel5": {"MG": {"A": {"NONE": 0.9512, "SMOTE": 0.9453, "SMOM": 0.9474},
                      "B": {"NONE": 0.7105, "SMOTE": 0.7736, "SMOM": 0.7783}},
               "MAUC": {"A": {"NONE": 0.9943, "SMOTE": 0.9881, "SMOM": 0.9894},
                        "B": {"NONE": 0.9544, "SMOTE": 0.9616, "SMOM": 0.9638}}},
    "vowel7": {"MG": {"A": {"NONE": 0.8343, "SMOTE": 0.8570, "SMOM": 0.8584},
                      "B": {"NONE": 0.6435, "SMOTE": 0.7170, "SMOM": 0.7188}},
               "MAUC": {"A": {"NONE": 0.9603, "SMOTE": 0.9688, "SMOM": 0.9719},
                        "B": {"NONE": 0.9547, "SMOTE": 0.9620, "SMOM": 0.9629}}},
    "vehicle": {"MG": {"A": {"NONE": 0.9719, "SMOTE": 0.9754, "SMOM": 0.9749},
                       "B": {"NONE": 0.7768, "SMOTE": 0.7832, "SMOM": 0.7849}},
                "MAUC": {"A": {"NONE": 0.9986, "SMOTE": 0.9986, "SMOM": 0.9983},
                         "B": {"NONE": 0.9255, "SMOTE": 0.9297, "SMOM": 0.9299}},
                "recall_smallest": {"A": {"NONE": 0.9659, "SMOTE": 0.9754, "SMOM": 0.9763},
                                    "B": {"NONE": 0.9607, "SMOTE": 0.9614, "SMOM": 0.9608}},
                "precision_smallest": {"A": {"NONE": 0.9547, "SMOTE": 0.9459, "SMOM": 0.9433},
                                       "B": {"NONE": 0.6267, "SMOTE": 0.6242, "SMOM": 0.6246}}},
}


# ============================================================================ data
def read_keel(name):
    rows = []
    with open(os.path.join(KEEL, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("@"):
                rows.append([t.strip() for t in line.split(",")])
    return rows


def load(name):
    if name in ("vowel5", "vowel7"):
        rows = read_keel("vowel.dat")
        X = np.array([[float(t) for t in r[3:13]] for r in rows])  # F0..F9
        lab = np.array([int(r[-1]) for r in rows])
        groups = ([[0, 1], [2], [3, 4, 5, 6], [7, 8, 9], [10]] if name == "vowel5" else
                  [[0], [1, 2], [3], [4, 5], [6], [7, 8], [9, 10]])
    elif name == "vehicle":
        rows = read_keel("vehicle.dat")
        X = np.array([[float(t) for t in r[:-1]] for r in rows])
        names = {"van": 0, "saab": 1, "opel": 1, "bus": 2}
        lab = np.array([names[r[-1]] for r in rows])
        groups = [[0], [1], [2]]
    else:
        raise ValueError(name)
    y = np.full(lab.size, -1)
    for k, g in enumerate(groups):
        y[np.isin(lab, g)] = k
    assert (y >= 0).all()
    return X, y


EXPECTED = {"vowel5": [180, 90, 360, 270, 90], "vowel7": [90, 180, 90, 180, 90, 180, 180],
            "vehicle": [199, 429, 218]}


# ============================================================================ Weka NaiveBayes -D
LOG2 = np.log(2.0)
# Weka's Discretize option useBetterEncoding (default false). Only for the side check
# "--mdl-encoding better"; the reported results use the default.
BETTER_ENCODING = False


def _xlnx(a):
    a = np.asarray(a, dtype=float)
    out = np.zeros_like(a)
    m = a > 0
    out[m] = a[m] * np.log(a[m])
    return out


def _entropy(counts):
    """weka.core.ContingencyTables.entropy (bits)."""
    s = float(np.sum(counts))
    if s <= 0:
        return 0.0
    return (-_xlnx(counts).sum() + _xlnx(s)) / (s * LOG2)


def _cond_entropy(L, R):
    """weka.core.ContingencyTables.entropyConditionedOnRows for the 2-row tables [L; R]."""
    sl, sr = L.sum(axis=1), R.sum(axis=1)
    rv = _xlnx(L).sum(axis=1) - _xlnx(sl) + _xlnx(R).sum(axis=1) - _xlnx(sr)
    return -rv / ((sl + sr) * LOG2)


def _cut_points(v, c, first, last, n_classes):
    """Discretize.cutPointsForSubset (Weka 3.8, supervised, useBetterEncoding = false,
    useKononenko = false) on values v sorted ascending with class indices c."""
    N = last - first
    if N < 2:
        return []
    onehot = np.zeros((N, n_classes))
    onehot[np.arange(N), c[first:last]] = 1.0
    prior = onehot.sum(axis=0)
    prior_entropy = _entropy(prior)
    vv = v[first:last]
    pos = np.flatnonzero(vv[:-1] < vv[1:])  # candidate boundaries between distinct values
    if pos.size == 0:
        return []
    L = np.cumsum(onehot, axis=0)[pos]
    R = prior - L
    ent = _cond_entropy(L, R)
    b = int(np.argmin(ent))  # first strict improvement, as Weka's loop with "<"
    if not ent[b] < prior_entropy:
        return []
    gain = prior_entropy - ent[b]
    if gain <= 0:
        return []
    # FayyadAndIranisMDL with numCutPoints = N - 1 (useBetterEncoding = false) or the number of
    # candidate boundaries (useBetterEncoding = true)
    num_cut_points = pos.size if BETTER_ENCODING else N - 1
    k = int((prior > 0).sum())
    kl = int((L[b] > 0).sum())
    kr = int((R[b] > 0).sum())
    delta = np.log2(3.0 ** k - 2) - (k * prior_entropy - kr * _entropy(R[b]) - kl * _entropy(L[b]))
    if not gain > (np.log2(num_cut_points) + delta) / N:
        return []
    split = first + int(pos[b])
    cut = (v[split] + v[split + 1]) / 2.0
    return (_cut_points(v, c, first, split + 1, n_classes) + [cut]
            + _cut_points(v, c, split + 1, last, n_classes))


class WekaNaiveBayesD:
    """weka.classifiers.bayes.NaiveBayes -D (Weka 3.8) for numeric attributes without missing
    values: supervised MDL discretization fitted on the training data, Laplace-corrected
    DiscreteEstimator for the class prior and for every attribute given the class."""

    def fit(self, X, y):
        self.classes_, yi = np.unique(y, return_inverse=True)
        C = self.classes_.size
        n, d = X.shape
        self.cuts_, self.logcond_ = [], []
        for f in range(d):
            order = np.argsort(X[:, f], kind="stable")
            cuts = np.asarray(_cut_points(X[order, f], yi[order], 0, n, C))
            bins = np.searchsorted(cuts, X[:, f], side="left")  # x <= cut -> lower bin
            nb = cuts.size + 1
            cnt = np.zeros((C, nb))
            np.add.at(cnt, (yi, bins), 1.0)
            self.cuts_.append(cuts)
            self.logcond_.append(np.log((cnt + 1.0) / (cnt.sum(axis=1, keepdims=True) + nb)))
        cc = np.bincount(yi, minlength=C).astype(float)
        self.logprior_ = np.log((cc + 1.0) / (n + C))
        return self

    def predict_proba(self, X):
        lp = np.tile(self.logprior_, (X.shape[0], 1))
        for f, (cuts, lc) in enumerate(zip(self.cuts_, self.logcond_)):
            lp += lc[:, np.searchsorted(cuts, X[:, f], side="left")].T
        lp -= lp.max(axis=1, keepdims=True)
        p = np.exp(lp)
        return p / p.sum(axis=1, keepdims=True)


# ============================================================================ measures
def mauc(y, proba, classes):
    """Hand and Till (2001) M: mean over class pairs of (A(i|j) + A(j|i)) / 2."""
    tot, pairs = 0.0, 0
    for a in range(classes.size):
        for b in range(a + 1, classes.size):
            vals = []
            for i, j in ((a, b), (b, a)):
                m = (y == classes[i]) | (y == classes[j])
                s = proba[m, i]
                pos = y[m] == classes[i]
                r = rankdata(s)
                n1, n0 = pos.sum(), (~pos).sum()
                vals.append((r[pos].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))
            tot += 0.5 * (vals[0] + vals[1])
            pairs += 1
    return tot / pairs


def measures(y, proba, classes, smallest):
    pred = classes[np.argmax(proba, axis=1)]
    rec = np.array([np.mean(pred[y == c] == c) for c in classes])
    out = {"MG": float(np.prod(rec) ** (1.0 / classes.size)), "MAUC": float(mauc(y, proba, classes))}
    if smallest is not None:
        tp = np.sum((pred == smallest) & (y == smallest))
        npred = np.sum(pred == smallest)
        out["recall_smallest"] = float(tp / np.sum(y == smallest))
        out["precision_smallest"] = float(tp / npred) if npred else float("nan")
    return out, pred


# ============================================================================ experiment
def resample(method, Xtr, ytr, seed, rule):
    if method == "NONE":
        return Xtr, ytr
    if method == "SMOTE":
        from imblearn.over_sampling import SMOTE
        mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0, ddof=1)
        sd[~(sd > 0)] = 1.0
        Xs, ys = SMOTE(k_neighbors=5, random_state=seed).fit_resample((Xtr - mu) / sd, ytr)
        return Xs * sd + mu, ys
    return SMOM(random_state=seed, soft_core_rule=rule).fit_resample(Xtr, ytr)


def run(name, methods, runs):
    X, y = load(name)
    classes, counts = np.unique(y, return_counts=True)
    assert counts.tolist() == EXPECTED[name], (name, counts)
    smallest = classes[np.argmin(counts)] if np.sum(counts == counts.min()) == 1 else None
    res = {}
    for method in methods:
        base, rule = (method.split(":") + ["proportion"])[:2]
        per_fold, pooled_mg, t0 = [], [], time.time()
        for r in range(1, runs + 1):
            skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=r)
            y_all, p_all = [], []
            for f, (tr, te) in enumerate(skf.split(X, y)):
                Xtr, ytr = resample(base, X[tr], y[tr], 1000 * r + f, rule)
                proba = WekaNaiveBayesD().fit(Xtr, ytr).predict_proba(X[te])
                m, pred = measures(y[te], proba, classes, smallest)
                per_fold.append(m)
                y_all.append(y[te])
                p_all.append(pred)
            yy, pp = np.concatenate(y_all), np.concatenate(p_all)
            rec = [np.mean(pp[yy == c] == c) for c in classes]
            pooled_mg.append(float(np.prod(rec) ** (1.0 / classes.size)))
        keys = per_fold[0].keys()
        summary = {k: float(np.nanmean([m[k] for m in per_fold])) for k in keys}
        summary["MG_pooled_per_run"] = float(np.mean(pooled_mg))
        run_means = [np.mean([m["MG"] for m in per_fold[10 * i:10 * i + 10]]) for i in range(runs)]
        summary["MG_sd_over_runs"] = float(np.std(run_means, ddof=1)) if runs > 1 else float("nan")
        summary["seconds"] = round(time.time() - t0, 1)
        res[method] = summary
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--datasets", default="vowel7,vowel5,vehicle")
    ap.add_argument("--methods", default="NONE,SMOTE,SMOM,SMOM:round")
    ap.add_argument("--mdl-encoding", choices=["default", "better"], default="default",
                    help="Weka Discretize useBetterEncoding false (default) or true (side check)")
    ap.add_argument("--out", default="validation_results.json", help="file in this folder, '-' for none")
    args = ap.parse_args()
    global BETTER_ENCODING
    BETTER_ENCODING = args.mdl_encoding == "better"
    methods = args.methods.split(",")
    allres = {}
    for name in args.datasets.split(","):
        allres[name] = run(name, methods, args.runs)
        print(f"\n{name} (NaiveBayes with supervised discretization, {args.runs} x stratified 10-fold CV)")
        print(f"{'method':12s} {'MG':>7s} {'MGpool':>7s} {'MAUC':>7s} {'rec_s':>7s} {'prec_s':>7s}"
              f"   paper MG A/B      paper MAUC A/B   seconds")
        for method, s in allres[name].items():
            base = method.split(":")[0]
            pm, pa = PAPER[name]["MG"], PAPER[name]["MAUC"]
            print(f"{method:12s} {s['MG']:7.4f} {s['MG_pooled_per_run']:7.4f} {s['MAUC']:7.4f} "
                  f"{s.get('recall_smallest', float('nan')):7.4f} {s.get('precision_smallest', float('nan')):7.4f}"
                  f"   {pm['A'][base]:.4f}/{pm['B'][base]:.4f}   {pa['A'][base]:.4f}/{pa['B'][base]:.4f}"
                  f"   {s['seconds']}")
    out = {"protocol": f"{args.runs} runs x StratifiedKFold(10, shuffle=True, random_state=run); resampling "
                       "on the training fold only; Weka-equivalent NaiveBayes -D (useBetterEncoding="
                       f"{BETTER_ENCODING}); MG, MAUC, recall and precision averaged over the test folds; "
                       "MG_pooled_per_run: MG of the pooled predictions of each run, averaged over runs",
           "results": allres, "paper": PAPER}
    if args.out != "-":
        with open(os.path.join(HERE, os.path.basename(args.out)), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
