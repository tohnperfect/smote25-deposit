"""Validation of cgmos.CGMOS against Zhang et al., CGMOS (CIKM 2016).

Part A (number reproduction). Table 3 (p. 1629) prints, for Haberman, the AUC averaged over the
six base classifiers of Sec. 4.3 (p. 1626): CGMOS 0.651, Original 0.623, SMOTE 0.600. The
protocol stated by the paper: 10 rounds of 10-fold cross-validation (Sec. 4.5, p. 1627); six
classifiers, b-kde (the Bayes classifier of Sec. 2), knn, RBF svm, a one-hidden-layer neural
network, a random forest of C4.5 trees and AdaBoost.M1, "All hyper-parameters ... determined
by cross validation" (p. 1626); AUC (Sec. 4.4, p. 1627). Haberman: 306 samples, 3 features,
ratio 0.36 (Table 1, p. 1627), identical to the KEEL copy used here (81 positive, 225 negative).

What the paper does not state, and the reading used here (see VALIDATION.md):
  * scaling: z-score fitted on each training fold (--scaling minmax or none for other readings);
  * oversampling: applied to the training fold only (and inside the inner tuning folds);
  * tuning: inner stratified 3-fold CV on the training fold, AUC, over the small grids below;
  * classifiers: scikit-learn models (entropy-split random forest for "C4.5"; SAMME AdaBoost,
    which is AdaBoost.M1 for two classes); b-kde as in Sec. 2 with its own sigma and q tuned;
  * AUC: computed per test fold and averaged over the 100 folds (alternative: one AUC per
    round on the pooled test scores, also reported);
  * CGMOS settings: the defaults of cgmos.CGMOS (sigma = 1, q = 5, k = 5, balance).

Protocol "tuned" is the main reading; protocol "fixed" (one default setting per classifier, no
tuning) is a cheap second reading used to compare the CGMOS readings of NOTES.md.

Part B (qualitative). Figure 1 (p. 1625) plots W(x) - 1 (scale 1e-4) for a minority example
moved along the center line of two Gaussian classes (2000 majority, 400 minority). The Gaussian
parameters are not given; they are estimated here from the figure, so only the scale and the
shape are compared, for the default reading and a sweep of readings.

Part C (structural check). How far CGMOS's seed distribution W(x_i) / z is from SMOTE's uniform
one (total-variation distance), on five KEEL data sets and five readings.

Run: python3 -I validate_cgmos.py [--parts ABC] [--protocol tuned|fixed|both] [--scaling zscore|minmax|none]
                                   [--rounds 10] [--jobs 2] [--samplers name,name]
Writes results/haberman_<protocol>.json, results/fig1_curve.json and results/seed_uniformity.json,
and prints a summary.
"""

import argparse
import json
import os
import sys
import time
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:  # python3 -I does not put the script's folder on sys.path
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from scipy.special import expit, logsumexp  # noqa: E402
from sklearn.base import BaseEstimator, ClassifierMixin, clone  # noqa: E402
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier  # noqa: E402
from sklearn.exceptions import ConvergenceWarning  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import ParameterGrid, StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors  # noqa: E402
from sklearn.neural_network import MLPClassifier  # noqa: E402
from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, StandardScaler  # noqa: E402
from sklearn.svm import SVC  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402
from threadpoolctl import threadpool_limits  # noqa: E402

from cgmos import CGMOS, _sq_dists, cgmos_weights, kde_bandwidths, log_kernel_block  # noqa: E402

HABERMAN = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/haberman.dat"
RESULTS = os.path.join(HERE, "results")
PAPER_TABLE3_HABERMAN = {"CGMOS": 0.651, "Original": 0.623, "Dup": 0.577, "SMOTE": 0.600,
                         "B-SMOTE": 0.593, "MWMOTE": 0.594, "ADASYN": 0.587, "RAMOboost": 0.586}


# ==============================================================================================
# b-kde: the Bayesian classifier of Sec. 2 (Eq. 3 likelihoods, priors n_l / n, Bayes' rule).
# ==============================================================================================
class KDEBayesClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, sigma=1.0, q=5, bandwidth_neighbors="class", normalize_kernel=False):
        self.sigma = sigma
        self.q = q
        self.bandwidth_neighbors = bandwidth_neighbors
        self.normalize_kernel = normalize_kernel

    def fit(self, X, y):
        self.classes_, yi = np.unique(y, return_inverse=True)
        self.X_, self.yi_ = np.asarray(X, float), yi
        self.h_ = kde_bandwidths(self.X_, yi, self.q, self.sigma, self.bandwidth_neighbors)
        return self

    def decision_function(self, X):
        """log P(l_1 | x) - log P(l_0 | x); with priors n_l / n the class counts cancel."""
        X = np.asarray(X, float)
        L = log_kernel_block(_sq_dists(X, self.X_), self.h_, self.normalize_kernel, X.shape[1])
        return logsumexp(L[:, self.yi_ == 1], axis=1) - logsumexp(L[:, self.yi_ == 0], axis=1)

    def predict_proba(self, X):
        p1 = expit(self.decision_function(X))
        return np.c_[1 - p1, p1]

    def predict(self, X):
        return self.classes_[(self.decision_function(X) > 0).astype(int)]


class UniformSeedCGMOS(CGMOS):
    """Ablation: CGMOS with W(x_i) = 1 for every seed, i.e. SMOTE drawn from CGMOS's random stream."""

    def _seed_weights(self, X, y, is_min):
        self.bandwidths_ = self.certainty_ = None
        return np.ones(int(is_min.sum()))


# name -> (estimator, grid for "tuned", parameters for "fixed")
CLASSIFIERS = {
    "b-kde": (KDEBayesClassifier(), {"sigma": [0.5, 1.0, 2.0], "q": [5, 15]},
              {"sigma": 1.0, "q": 5}),
    "knn": (KNeighborsClassifier(), {"n_neighbors": [5, 11, 21, 31]}, {"n_neighbors": 5}),
    "svm": (SVC(kernel="rbf"), {"C": [0.1, 1.0, 10.0], "gamma": [0.1, 0.3, 1.0]},
            {"C": 1.0, "gamma": "scale"}),
    "nn": (MLPClassifier(solver="lbfgs", max_iter=500),
           {"hidden_layer_sizes": [(5,), (20,)], "alpha": [0.01, 1.0]},
           {"hidden_layer_sizes": (10,), "alpha": 1e-4}),
    "rf": (RandomForestClassifier(n_estimators=50, criterion="entropy"),
           {"min_samples_leaf": [1, 5, 10]}, {"min_samples_leaf": 1}),
    "Adaboost.M1": (AdaBoostClassifier(estimator=DecisionTreeClassifier(max_depth=1), n_estimators=50),
                    {"estimator__max_depth": [1, 3], "learning_rate": [0.5, 1.0]},
                    {"estimator__max_depth": 1, "learning_rate": 1.0}),
}

SAMPLERS = {
    "Original": None,
    "SMOTE": "imblearn",
    "CGMOS": {},
    "CGMOS-uniform-seeds": "uniform",
    "CGMOS[normalize_kernel]": {"normalize_kernel": True},
    "CGMOS[bandwidth_neighbors=all]": {"bandwidth_neighbors": "all"},
    "CGMOS[sigma=0.5]": {"sigma": 0.5},
    "CGMOS[sigma=2]": {"sigma": 2.0},
    "CGMOS[q=10]": {"q": 10},
}


def load_haberman():
    rows = [r.split(",") for r in open(HABERMAN).read().split("\n") if r.strip() and not r.startswith("@")]
    X = np.array([[float(v) for v in r[:-1]] for r in rows])
    y = np.array([r[-1].strip() == "positive" for r in rows], dtype=int)  # minority = positive
    return X, y


def make_sampler(name, seed):
    spec = SAMPLERS[name]
    if spec is None:
        return None
    if spec == "imblearn":
        from imblearn.over_sampling import SMOTE
        return SMOTE(k_neighbors=5, random_state=seed)
    if spec == "uniform":
        return UniformSeedCGMOS(random_state=seed)
    return CGMOS(random_state=seed, **spec)


def resample(name, X, y, seed):
    s = make_sampler(name, seed)
    return (X, y) if s is None else s.fit_resample(X, y)


def make_clf(est, params, seed):
    clf = clone(est).set_params(**params)
    if "random_state" in clf.get_params():
        clf.set_params(random_state=seed)
    return clf


def score(clf, X):
    if hasattr(clf, "decision_function"):
        return clf.decision_function(X)
    return clf.predict_proba(X)[:, 1]


def tune(est, grid, X, y, sampler, seed):
    cands = list(ParameterGrid(grid))
    auc = np.zeros(len(cands))
    for a, b in StratifiedKFold(3, shuffle=True, random_state=seed).split(X, y):
        Xa, ya = resample(sampler, X[a], y[a], seed)
        for c, params in enumerate(cands):
            clf = make_clf(est, params, seed).fit(Xa, ya)
            auc[c] += roc_auc_score(y[b], score(clf, X[b]))
    return cands[int(np.argmax(auc))]


SCALERS = {"zscore": StandardScaler, "minmax": MinMaxScaler, "none": FunctionTransformer}


def run_fold(X, y, train, test, sampler, protocol, seed, scaling="zscore"):
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    with threadpool_limits(1):
        sc = SCALERS[scaling]().fit(X[train])
        Xtr, Xte, ytr, yte = sc.transform(X[train]), sc.transform(X[test]), y[train], y[test]
        s = make_sampler(sampler, seed)
        Xr, yr = (Xtr, ytr) if s is None else s.fit_resample(Xtr, ytr)
        out = {"scores": {}, "params": {}, "diag": {}}
        if isinstance(s, CGMOS) and not isinstance(s, UniformSeedCGMOS):
            p = s.seed_proba_
            u = UniformSeedCGMOS(random_state=seed)
            Xu, _ = u.fit_resample(Xtr, ytr)
            n = len(ytr)
            same = np.all(np.isclose(Xr[n:], Xu[n:]), axis=1)
            out["diag"] = {"W_min": float(s.weights_.min()), "W_max": float(s.weights_.max()),
                           "tv_to_uniform": float(0.5 * np.abs(p - 1 / p.size).sum()),
                           "max_rel_dev": float(np.abs(p * p.size - 1).max()),
                           "share_rows_identical_to_uniform_seed_run": float(same.mean())}
        for cname, (est, grid, fixed) in CLASSIFIERS.items():
            params = tune(est, grid, Xtr, ytr, sampler, seed) if protocol == "tuned" else fixed
            clf = make_clf(est, params, seed).fit(Xr, yr)
            out["scores"][cname] = score(clf, Xte).tolist()
            out["params"][cname] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in params.items()}
        out["test"] = test.tolist()
        return out


def evaluate(X, y, sampler, protocol, rounds, folds, jobs, scaling="zscore"):
    splits = []
    for r in range(rounds):
        for f, (tr, te) in enumerate(StratifiedKFold(folds, shuffle=True, random_state=r).split(X, y)):
            splits.append((r, f, tr, te))
    # forked workers inherit sys.path (python3 -I keeps this folder off it in fresh interpreters)
    res = Parallel(n_jobs=jobs, backend="multiprocessing")(
        delayed(run_fold)(X, y, tr, te, sampler, protocol, 1000 * r + f, scaling) for r, f, tr, te in splits)
    per_fold = {c: [] for c in CLASSIFIERS}
    pooled = {c: [] for c in CLASSIFIERS}
    for r in range(rounds):
        idx = [i for i, s in enumerate(splits) if s[0] == r]
        for c in CLASSIFIERS:
            yt = np.concatenate([y[res[i]["test"]] for i in idx])
            st = np.concatenate([res[i]["scores"][c] for i in idx])
            pooled[c].append(float(roc_auc_score(yt, st)))
            per_fold[c] += [float(roc_auc_score(y[res[i]["test"]], res[i]["scores"][c])) for i in idx]
    summary = {
        "per_classifier_fold_mean": {c: float(np.mean(v)) for c, v in per_fold.items()},
        "per_classifier_pooled_mean": {c: float(np.mean(v)) for c, v in pooled.items()},
    }
    summary["avg6_fold_mean"] = float(np.mean(list(summary["per_classifier_fold_mean"].values())))
    summary["avg6_pooled_mean"] = float(np.mean(list(summary["per_classifier_pooled_mean"].values())))
    # standard error of the six-classifier average over the 100 folds
    fold_avg = np.mean(np.array([per_fold[c] for c in CLASSIFIERS]), axis=0)
    summary["avg6_fold_se"] = float(fold_avg.std(ddof=1) / np.sqrt(fold_avg.size))
    summary["fold_avg6"] = fold_avg.tolist()
    diags = [r["diag"] for r in res if r["diag"]]
    if diags:
        summary["diag"] = {k: [float(np.min([d[k] for d in diags])), float(np.mean([d[k] for d in diags])),
                               float(np.max([d[k] for d in diags]))] for k in diags[0]}
    summary["chosen_params"] = [r["params"] for r in res[:3]]
    return summary


# ==============================================================================================
# Part B: Figure 1 (p. 1625), W(x) - 1 for a minority example moved along the center line.
# ==============================================================================================
FIG1_READ_OFF = {-2.0: 2.4, -1.0: 1.5, 0.0: 1.4, 1.0: 1.2, 2.0: 2.8, 2.75: 3.2, 3.25: 4.4,
                 3.75: 5.2, 4.0: 3.9, 4.25: "< 0"}  # values x 1e-4, read off panel 3 by eye


def fig1_data(seed=1):
    """Two Gaussian classes as in Fig. 1. The parameters are estimated from the figure (not stated):
    minority centered near (1, 5), majority near (7.3, 5), the majority narrower in x."""
    rng = np.random.RandomState(seed)
    X = np.vstack([np.c_[rng.normal(7.3, 0.7, 2000), rng.normal(5.0, 1.0, 2000)],
                   np.c_[rng.normal(1.0, 1.3, 400), rng.normal(5.0, 1.2, 400)]])
    y = np.r_[np.zeros(2000, int), np.ones(400, int)]
    return X, y


def fig1_curve(X, y, xs, sigma=1.0, q=5, normalize_kernel=False, neighbors="class"):
    """W(x) - 1 (Eqs. 5-6) for one minority example added at (x, 5); its bandwidth follows Eq. 4."""
    is_min = y == 1
    m = X.shape[1]
    P = np.c_[xs, np.full(xs.size, 5.0)]
    h = kde_bandwidths(X, y, q, sigma, neighbors)
    ref = X[is_min] if neighbors == "class" else X
    d, _ = NearestNeighbors(n_neighbors=q).fit(ref).kneighbors(P)
    hp = sigma * d.mean(axis=1)
    K = np.exp(log_kernel_block(_sq_dists(X, X), h, normalize_kernel, m))
    s_min, s_maj = K[:, is_min].sum(1), K[:, ~is_min].sum(1)
    own, other = np.where(is_min, s_min, s_maj), np.where(is_min, s_maj, s_min)
    Kc = np.exp(log_kernel_block(_sq_dists(X, P), hp, normalize_kernel, m))
    R = Kc / ((s_min + s_maj)[:, None] + Kc) * np.where(is_min, other / own, -1.0)[:, None]
    return R.mean(axis=0)


def part_b():
    X, y = fig1_data()
    xs = np.round(np.arange(-2.0, 10.001, 0.25), 2)
    out = {"paper_read_off_x1e4": {str(k): v for k, v in FIG1_READ_OFF.items()}, "sweep": []}
    read = np.array(sorted(FIG1_READ_OFF))
    for norm in (False, True):
        for nb in ("class", "all"):
            for sigma in (0.5, 1.0, 2.0, 5.0, 10.0):
                for q in (5, 20):
                    c = fig1_curve(X, y, xs, sigma, q, norm, nb) * 1e4
                    left = xs <= 4.25
                    i = int(np.argmax(np.where(left, c, -np.inf)))
                    neg = xs[(xs > xs[i]) & (c < 0)]
                    row = {"normalize_kernel": norm, "bandwidth_neighbors": nb, "sigma": sigma, "q": q,
                           "at_x1_x1e4": float(c[xs == 1.0][0]), "peak_x": float(xs[i]),
                           "peak_x1e4": float(c[i]), "first_negative_x": float(neg[0]) if neg.size else None}
                    if not norm and nb == "class" and sigma == 1.0 and q == 5:
                        out["default_curve_x1e4"] = {str(x): float(v) for x, v in zip(xs, c) if x in read or x in (5.0, 6.0, 8.0)}
                    out["sweep"].append(row)
    W, _ = cgmos_weights(X, y == 1, kde_bandwidths(X, y, 5, 1.0, "class"))
    p = W / W.sum()
    out["default_data_W_range"] = [float(W.min()), float(W.max())]
    out["default_tv_to_uniform"] = float(0.5 * np.abs(p - 1 / p.size).sum())
    print("[Fig. 1] paper, read off panel 3 (x1e-4):", FIG1_READ_OFF)
    print("[Fig. 1] default reading (x1e-4):", {k: round(v, 3) for k, v in out["default_curve_x1e4"].items()})
    print(f"[Fig. 1] weights of the 400 minority points (default): [{W.min():.6f}, {W.max():.6f}], "
          f"TV(seed distribution, uniform) = {out['default_tv_to_uniform']:.6f}")
    print("[Fig. 1] sweep (paper: 1.2 at x = 1, peak 5.2 at x = 3.75, negative from about x = 4.2):")
    for r in out["sweep"]:
        print(f"    normalize_kernel={int(r['normalize_kernel'])} neighbors={r['bandwidth_neighbors']:5s} "
              f"sigma={r['sigma']:4.1f} q={r['q']:2d}: at x=1 {r['at_x1_x1e4']:7.3f}, peak {r['peak_x1e4']:7.3f} "
              f"at x={r['peak_x']:5.2f}, first negative x={r['first_negative_x']}")
    json.dump(out, open(os.path.join(RESULTS, "fig1_curve.json"), "w"), indent=1)


# ==============================================================================================
# Part C: distance of CGMOS's seed distribution W(x_i) / z from SMOTE's uniform one.
# ==============================================================================================
KEEL = "/home/claude/work/rerun42/src/kd/keel_ds/data"
UNIFORMITY_SETS = {
    "haberman": (KEEL + "/imbalanced/raw/haberman.dat", "positive"),
    "tae (class 1 vs rest)": (KEEL + "/balanced/raw/tae.dat", "1"),
    "contraceptive (class 2 vs rest)": (KEEL + "/balanced/raw/contraceptive.dat", "2"),
    "movement_libras (class 1 vs rest)": (KEEL + "/balanced/raw/movement_libras.dat", "1"),
    "yeast4": (KEEL + "/imbalanced/raw/yeast4.dat", "positive"),
}
READINGS = {"default": {}, "normalize_kernel": {"normalize_kernel": True},
            "bandwidth_neighbors=all": {"bandwidth_neighbors": "all"}, "sigma=3": {"sigma": 3.0}}


def load_keel(path, positive):
    rows = [r.split(",") for r in open(path).read().split("\n") if r.strip() and not r.startswith("@")]
    X = np.array([[float(v) for v in r[:-1]] for r in rows])
    y = np.array([r[-1].strip() == positive for r in rows], dtype=int)
    sd = X.std(0)
    return (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), y


def loo_weights(X, y, sigma=1.0, q=5):
    """Leave-one-out reading of Eq. 3 (x_j's own kernel left out of its density); not the printed one."""
    is_min = y == 1
    h = kde_bandwidths(X, y, q, sigma, "class")
    K = np.exp(log_kernel_block(_sq_dists(X, X), h))
    np.fill_diagonal(K, 0.0)
    s_min, s_maj = K[:, is_min].sum(1), K[:, ~is_min].sum(1)
    own, other = np.where(is_min, s_min, s_maj), np.where(is_min, s_maj, s_min)
    cand = np.flatnonzero(is_min)
    Kc = K[:, cand].copy()
    Kc[cand, np.arange(cand.size)] = 1.0  # the copy added at x_i does count at x_i
    with np.errstate(divide="ignore", invalid="ignore"):
        R = Kc / ((s_min + s_maj)[:, None] + Kc) * np.where(is_min, other / own, -1.0)[:, None]
    return 1.0 + np.nansum(R, axis=0) / len(y)


def part_c():
    out = {}
    for name, (path, pos) in UNIFORMITY_SETS.items():
        X, y = load_keel(path, pos)
        for rname, kw in list(READINGS.items()) + [("leave-one-out (not printed)", None)]:
            if kw is None:
                W = loo_weights(X, y)
            else:
                s = CGMOS(random_state=0, **kw)
                s.fit_resample(X, y)
                W = s.weights_
            p = W / W.sum()
            out[f"{name} | {rname}"] = r = {
                "n": int(len(y)), "m": int(X.shape[1]), "n_min": int(y.sum()),
                "W_min": float(W.min()), "W_max": float(W.max()),
                "tv_to_uniform": float(0.5 * np.abs(p - 1 / p.size).sum()),
                "max_rel_dev": float(np.abs(p * p.size - 1).max())}
            print(f"[seeds] {name + ' | ' + rname:62s} n={r['n']:5d} m={r['m']:3d} n_min={r['n_min']:4d} "
                  f"W in [{r['W_min']:.4f}, {r['W_max']:.4f}] TV={r['tv_to_uniform']:.4f} "
                  f"max|n_min p - 1|={r['max_rel_dev']:.4f}")
    print(f"[seeds] largest TV distance: {max(v['tv_to_uniform'] for v in out.values()):.4f}")
    json.dump(out, open(os.path.join(RESULTS, "seed_uniformity.json"), "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", default="both", choices=["tuned", "fixed", "both"])
    ap.add_argument("--rounds", type=int, default=10)
    ap.add_argument("--folds", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--samplers", default="")
    ap.add_argument("--parts", default="ABC")
    ap.add_argument("--scaling", default="zscore", choices=list(SCALERS))
    args = ap.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    X, y = load_haberman()
    assert X.shape == (306, 3) and y.sum() == 81
    protocols = ["tuned", "fixed"] if args.protocol == "both" else [args.protocol]
    default_samplers = {"tuned": ["Original", "SMOTE", "CGMOS"],
                        "fixed": list(SAMPLERS)}
    for protocol in (protocols if "A" in args.parts else []):
        names = args.samplers.split(",") if args.samplers else default_samplers[protocol]
        tag = "" if args.scaling == "zscore" else f"_{args.scaling}"
        path = os.path.join(RESULTS, f"haberman_{protocol}{tag}.json")
        allres = json.load(open(path)) if os.path.exists(path) else {}
        for name in names:
            t0 = time.time()
            allres[name] = evaluate(X, y, name, protocol, args.rounds, args.folds, args.jobs, args.scaling)
            allres[name]["seconds"] = round(time.time() - t0, 1)
            allres[name]["rounds"], allres[name]["folds"] = args.rounds, args.folds
            s = allres[name]
            print(f"[{protocol}{tag}] {name:32s} avg6 AUC fold-mean {s['avg6_fold_mean']:.3f} "
                  f"(se {s['avg6_fold_se']:.3f}), pooled {s['avg6_pooled_mean']:.3f}  "
                  + " ".join(f"{c}={v:.3f}" for c, v in s["per_classifier_fold_mean"].items())
                  + f"  [{s['seconds']}s]", flush=True)
            if "diag" in s:
                print("    seed diagnostics [min, mean, max over folds]: "
                      + "; ".join(f"{k}={[round(v, 5) for v in vals]}" for k, vals in s["diag"].items()),
                      flush=True)
            json.dump(allres, open(path, "w"), indent=1)
    if "B" in args.parts:
        part_b()
    if "C" in args.parts:
        part_c()

if __name__ == "__main__":
    main()
