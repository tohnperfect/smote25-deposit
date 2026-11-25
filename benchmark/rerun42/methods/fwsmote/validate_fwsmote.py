"""Validate fwsmote.FWSMOTE against numbers the paper prints (WP6.8 brief, item 3).

Target: yeast3 (ldd28 in Table 1, p.7), whose FW-SMOTE results are in the supplementary
Appendix A: AUC x100 = 90.3 (k-NN, Table A.1, Supp. p.29), 89.1 (linear SVM, Table A.2,
p.30), 89.0 (LR, Table A.3, p.31); G-mean x100 = 90.3 / 88.7 / 88.5 (Tables A.4-A.6,
pp.32-34). SMOTE on the same dataset: AUC 88.4 / 88.6 / 88.2, G-mean 88.6 / 88.9 / 88.2.

Protocol as the paper states it (Section 4.1, pp.7-8):
  * ten-fold cross-validation; AUC and G-mean averaged over the folds (x100);
  * classifiers: k-NN with k = 5, linear SVM with C = 1, logistic regression (no settings);
  * FW-SMOTE with k = 5 and N in {1, 3}; the better N on average test performance is kept;
  * FW-SMOTE's other parameters tuned "within the training set" by grid search over
    ranking {Fisher, MI, EC, CFS} x r {n/2, 3n/4, n} x p {inf, 1, 2} x quantifier {basic,
    quadratic, exponential, trigonometric} x alpha {0.4, 0.6} = 288 configurations
    (pp.7, 9-10); ties go to the first configuration in the order of Table 4 (p.10).

Unstated details and the readings tried (all reported):
  * folds: stratified, shuffled with seeds 0..S-1 (one 10-fold run per seed);
  * tuning "within the training set": (A) inner stratified 5-fold CV on each outer
    training set; (B) the configuration with the best mean test AUC over the ten folds
    (the optimistic reading of "the best parameter configuration ... for each dataset",
    Supp. p.29 and p.10);
  * AUC: "crisp" = (TPR + TNR) / 2 from predicted labels (the reading the supplement's
    exact 50.0 values with G-mean 0.0 suggest), "score" = ROC AUC of the classifier's
    scores (k-NN neighbor fraction, LR probability, SVM decision value);
  * no feature scaling (yeast3's features are already in [0, 1]); --scale minmax fits a
    min-max scaling on each outer training fold instead;
  * implementation readings: the paper's text with the weighted Chebyshev distance (the
    default), the paper's text with the limit Chebyshev distance, and the authors' 2019
    Matlab code (variant="smoteiowa2019": fixed gap 0.3, partners with replacement, ...).
SMOTE baseline: FWSMOTE with equal weights, r = n, p = 2 (the reduction the paper states,
p.6), N in {1, 3}, better N kept: it checks the protocol against the paper's SMOTE column.

k-NN is evaluated exactly but fast: the distances from the test rows to the original
training rows are computed once per training set, and only the synthetic rows are new
for each configuration (the check against KNeighborsClassifier is printed).

Run (one invocation at a time: each rewrites validation_results.json, merging by key):
      python3 -I validate_fwsmote.py --seeds 0 1 2 3 4 --classifiers knn
      python3 -I validate_fwsmote.py --seeds 0 1 2 3 4 --classifiers knn --no-inner --readings paper-weighted --scale minmax
      python3 -I validate_fwsmote.py --seeds 0 --classifiers lr svm --no-inner --readings paper-weighted
Writes validation_results.json next to this file.
"""

import argparse
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from scipy.spatial.distance import cdist  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402
from sklearn.svm import SVC  # noqa: E402

from fwsmote import (  # noqa: E402
    FWSMOTE,
    _muteinf,
    correlation_score,
    eigenvector_centrality_score,
    fisher_score,
    mutual_information_score,
)

KEEL = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw"
DATASET = "yeast3"
PAPER = {  # yeast3 = ldd28; Tables A.1-A.6 (Supp. pp.29-34), x100
    "knn": {"FW-SMOTE": {"auc": 90.3, "gmean": 90.3}, "SMOTE": {"auc": 88.4, "gmean": 88.6}},
    "svm": {"FW-SMOTE": {"auc": 89.1, "gmean": 88.7}, "SMOTE": {"auc": 88.6, "gmean": 88.9}},
    "lr": {"FW-SMOTE": {"auc": 89.0, "gmean": 88.5}, "SMOTE": {"auc": 88.2, "gmean": 88.2}},
}
# Grid in the order of Table 4 (p.9), so that ties go to the first configuration (p.10).
GRID = [
    dict(ranking=rk, r=r, p=p, quantifier=q, alpha=a)
    for rk, r, p, q, a in itertools.product(
        ("fisher", "mi", "ec", "cfs"),
        (0.5, 0.75, 1.0),
        (np.inf, 1.0, 2.0),
        ("basic", "quadratic", "exponential", "trigonometric"),
        (0.4, 0.6),
    )
]
DEFAULT = dict(ranking="fisher", r=0.5, p=np.inf, quantifier="basic", alpha=0.4)
READINGS = {
    "paper-weighted": dict(variant="paper", chebyshev="weighted"),
    "paper-limit": dict(variant="paper", chebyshev="limit"),
    "smoteiowa2019": dict(variant="smoteiowa2019", chebyshev="weighted"),
}
KEYS = ("auc_crisp", "auc_score", "gmean")
MEASURES = ("auc_crisp", "auc_score")
NS = (1, 3)


def load_keel(name):
    """KEEL .dat (keel-ds 0.2.5): comma-separated, last column the class, no header."""
    X, y = [], []
    with open(os.path.join(KEEL, name + ".dat")) as fh:
        for line in fh:
            parts = [t.strip() for t in line.strip().split(",")]
            if len(parts) < 2:
                continue
            X.append([float(t) for t in parts[:-1]])
            y.append(1 if parts[-1] == "positive" else 0)
    return np.array(X), np.array(y)


def make_clf(name):
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=5)
    if name == "svm":
        return SVC(kernel="linear", C=1.0)
    if name == "lr":
        return LogisticRegression(C=np.inf, max_iter=10000)  # no penalty (p.7: no settings)
    raise ValueError(name)


def rank_auc(pos, score):
    """ROC AUC as the Mann-Whitney statistic with average ranks for ties (equal to
    sklearn's roc_auc_score, checked in main(), without its per-call validation cost)."""
    _, inv, cnt = np.unique(score, return_inverse=True, return_counts=True)
    avg = np.cumsum(cnt) - (cnt - 1) / 2.0  # average 1-based rank of each distinct score
    r = avg[inv.ravel()]
    n1 = int(pos.sum())
    n0 = pos.size - n1
    return float((r[pos].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def fold_metrics(y_true, pred, score):
    pos = y_true == 1
    tpr = float(np.mean(pred[pos] == 1))
    tnr = float(np.mean(pred[~pos] == 0))
    return (
        (tpr + tnr) / 2.0,  # auc_crisp
        rank_auc(pos, score),  # auc_score
        float(np.sqrt(tpr * tnr)),  # gmean
    )


class FastKNN:
    """5-NN (Euclidean, uniform votes) on the original training rows plus synthetic
    minority rows. The 5 nearest original rows of each test row are computed once; for a
    new configuration only the test-to-synthetic distances are added. Same result as
    KNeighborsClassifier(5) up to the order of equidistant neighbors."""

    def __init__(self, Xtr, ytr, Xte, k=5):
        D = cdist(Xte, Xtr)
        idx = np.argpartition(D, k - 1, axis=1)[:, :k]
        self.d0 = np.take_along_axis(D, idx, axis=1)
        self.l0 = ytr[idx].astype(float)
        self.Xte = Xte
        self.k = k

    def score(self, X_syn):
        if X_syn.shape[0] == 0:
            d, lab = self.d0, self.l0
        else:
            Ds = cdist(self.Xte, X_syn)
            d = np.hstack([self.d0, Ds])
            lab = np.hstack([self.l0, np.ones_like(Ds)])  # synthetic rows are minority
        idx = np.argpartition(d, self.k - 1, axis=1)[:, : self.k]
        return np.take_along_axis(lab, idx, axis=1).mean(axis=1)


def rankings_for(X, y, variant):
    """Step 2 scores of the four ranking methods, computed once per training set."""
    out = {
        "fisher": fisher_score(X, y, 1),
        "ec": eigenvector_centrality_score(X, y, 1),
        "cfs": correlation_score(X),
    }
    if variant == "smoteiowa2019":  # the 2019 code ranks by max(muteinf, 0)
        y_pm = np.where(y == 1, 1, -1)
        out["mi"] = np.maximum([_muteinf(X[:, j], y_pm) for j in range(X.shape[1])], 0.0)
    else:
        out["mi"] = mutual_information_score(X, y)
    return out


class Split:
    """One training/test split with its classifier evaluation."""

    def __init__(self, clf_name, Xtr, ytr, Xte, yte):
        self.clf_name, self.Xtr, self.ytr, self.Xte, self.yte = clf_name, Xtr, ytr, Xte, yte
        self.knn = FastKNN(Xtr, ytr, Xte) if clf_name == "knn" else None
        self.ranks = {}

    def ranks_for(self, variant):
        if variant not in self.ranks:
            self.ranks[variant] = rankings_for(self.Xtr, self.ytr, variant)
        return self.ranks[variant]

    def evaluate(self, sampler=None):
        if sampler is None:
            Xr, yr = self.Xtr, self.ytr
        else:
            Xr, yr = sampler.fit_resample(self.Xtr, self.ytr)
        if self.knn is not None:
            s = self.knn.score(Xr[self.Xtr.shape[0]:])
            return fold_metrics(self.yte, (s > 0.5).astype(int), s)
        clf = make_clf(self.clf_name).fit(Xr, yr)
        s = clf.decision_function(self.Xte)
        return fold_metrics(self.yte, (s > 0).astype(int), s)


def sampler_for(cfg, reading, split, N, rs):
    params = dict(cfg)
    params.update(READINGS[reading])
    u = split.ranks_for(params["variant"])[cfg["ranking"]]
    params["ranking"] = lambda X, y, u=u: u  # precomputed step-2 scores of this split
    return FWSMOTE(N=N, k=5, random_state=rs, **params)


def grid_on_split(split, readings, N, rs):
    """Metrics (len(GRID), 3) for each reading. 'paper-limit' differs from
    'paper-weighted' only when p = inf; elsewhere the results are equal and are copied."""
    out = {rd: np.zeros((len(GRID), 3)) for rd in readings}
    for c, cfg in enumerate(GRID):
        for rd in readings:
            if rd == "paper-limit" and not np.isinf(cfg["p"]) and "paper-weighted" in readings:
                out[rd][c] = out["paper-weighted"][c]
                continue
            out[rd][c] = split.evaluate(sampler_for(cfg, rd, split, N, rs))
    return out


def scale_split(Xtr, Xte, how):
    """Unstated in the paper: no scaling (default) or min-max scaling fitted on the
    training fold."""
    if how == "none":
        return Xtr, Xte
    lo, hi = Xtr.min(axis=0), Xtr.max(axis=0)
    rng = np.where(hi > lo, hi - lo, 1.0)
    return (Xtr - lo) / rng, (Xte - lo) / rng


def run_seed(job):
    """One ten-fold run (one CV seed) for one classifier."""
    seed, clf_name, readings, inner, scale = job
    t0 = time.time()
    X, y = load_keel(DATASET)
    outer = StratifiedKFold(10, shuffle=True, random_state=seed)
    B = {rd: np.zeros((len(NS), len(GRID), 10, 3)) for rd in readings}
    choice = {rd: {ms: np.zeros((len(NS), 10), dtype=int) for ms in MEASURES} for rd in readings}
    smote = np.zeros((len(NS), 10, 3))
    none = np.zeros((10, 3))
    knn_check = []
    dflt = GRID.index(DEFAULT)
    for f, (tr, te) in enumerate(outer.split(X, y)):
        Xtr_f, Xte_f = scale_split(X[tr], X[te], scale)
        sp = Split(clf_name, Xtr_f, y[tr], Xte_f, y[te])
        none[f] = sp.evaluate(None)
        inner_splits = []
        if inner:
            isp = StratifiedKFold(5, shuffle=True, random_state=1000 + seed)
            for a_, b_ in isp.split(sp.Xtr, sp.ytr):
                inner_splits.append(Split(clf_name, sp.Xtr[a_], sp.ytr[a_], sp.Xtr[b_], sp.ytr[b_]))
        for a, N in enumerate(NS):
            rs = 10000 * seed + 100 * f + N
            sm = FWSMOTE(N=N, k=5, ranking=lambda X_, y_: np.zeros(X_.shape[1]), r=1.0, p=2.0, random_state=rs)
            smote[a, f] = sp.evaluate(sm)
            g = grid_on_split(sp, readings, N, rs)
            for rd in readings:
                B[rd][a, :, f] = g[rd]
            if inner:
                acc = {rd: np.zeros((len(GRID), 3)) for rd in readings}
                for i, isplit in enumerate(inner_splits):
                    gi = grid_on_split(isplit, readings, N, rs + 10 * (i + 1))
                    for rd in readings:
                        acc[rd] += gi[rd] / len(inner_splits)
                for rd in readings:
                    for m_i, ms in enumerate(MEASURES):  # argmax keeps the first maximum
                        choice[rd][ms][a, f] = int(np.argmax(acc[rd][:, m_i]))
            if clf_name == "knn" and a == 0 and "paper-weighted" in readings:
                s = sampler_for(GRID[dflt], "paper-weighted", sp, N, rs)
                Xr, yr = s.fit_resample(sp.Xtr, sp.ytr)
                ref = KNeighborsClassifier(5).fit(Xr, yr).predict_proba(sp.Xte)[:, 1]
                knn_check.append(float(np.mean(np.isclose(ref, sp.knn.score(Xr[len(sp.Xtr):])))))
    return dict(seed=seed, clf=clf_name, readings=readings, inner=inner, B=B, choice=choice,
                smote=smote, none=none, knn_check=knn_check, seconds=round(time.time() - t0, 1))


def summarize(r):
    """Means over the ten folds (x100); the better N is kept, as on pp.7-8."""
    out = {"seconds": r["seconds"], "knn_agreement_with_sklearn": r["knn_check"]}
    out["no_oversampling"] = {k: 100 * r["none"][:, j].mean() for j, k in enumerate(KEYS)}
    out["SMOTE"] = {}
    for m_i, ms in enumerate(MEASURES):
        means = r["smote"][:, :, m_i].mean(axis=1)
        a = int(np.argmax(means))
        out["SMOTE"][ms] = {"value": 100 * means[a], "N": NS[a], "gmean": 100 * r["smote"][a, :, 2].mean()}
    dflt = GRID.index(DEFAULT)
    out["FW-SMOTE"] = {}
    for rd in r["readings"]:
        B = r["B"][rd]
        e_rd = {}
        for m_i, ms in enumerate(MEASURES):
            means = B[:, :, :, m_i].mean(axis=2)  # (N, configuration)
            a, c = np.unravel_index(int(np.argmax(means)), means.shape)
            cfg = {k: ("inf" if (isinstance(v, float) and np.isinf(v)) else v) for k, v in GRID[c].items()}
            e = {"B_best_on_test": {"value": 100 * means[a, c], "N": NS[a], "config": cfg,
                                    "gmean": 100 * B[a, c, :, 2].mean()}}
            ad = int(np.argmax(means[:, dflt]))
            e["default_config"] = {"value": 100 * means[ad, dflt], "N": NS[ad], "gmean": 100 * B[ad, dflt, :, 2].mean()}
            if r["inner"]:
                ch = r["choice"][rd][ms]
                vals = np.array([[B[a_, ch[a_, f], f, m_i] for f in range(10)] for a_ in range(len(NS))])
                gms = np.array([[B[a_, ch[a_, f], f, 2] for f in range(10)] for a_ in range(len(NS))])
                aa = int(np.argmax(vals.mean(axis=1)))
                picked = [GRID[i] for i in ch[aa]]
                e["A_tuned_in_training"] = {
                    "value": 100 * vals[aa].mean(), "N": NS[aa], "gmean": 100 * gms[aa].mean(),
                    "ranking": {k: sum(g["ranking"] == k for g in picked) for k in ("fisher", "mi", "ec", "cfs")},
                    "p": {("inf" if np.isinf(k) else str(k)): sum(g["p"] == k for g in picked) for k in (np.inf, 1.0, 2.0)},
                    "r": {str(k): sum(g["r"] == k for g in picked) for k in (0.5, 0.75, 1.0)},
                    "quantifier": {k: sum(g["quantifier"] == k for g in picked) for k in ("basic", "quadratic", "exponential", "trigonometric")},
                }
            e_rd[ms] = e
        gm = B[:, :, :, 2].mean(axis=2)
        e_rd["best_gmean_on_test"] = 100 * float(gm.max())
        out["FW-SMOTE"][rd] = e_rd
    return out


def aggregate(per_seed):
    """Mean, min and max over CV seeds of every numeric 'value' and 'gmean' field."""
    def walk(nodes):
        first = nodes[0]
        if isinstance(first, dict):
            return {k: walk([n[k] for n in nodes]) for k in first if all(k in n for n in nodes)}
        if isinstance(first, (int, float)) and not isinstance(first, bool):
            v = np.array(nodes, dtype=float)
            return {"mean": float(v.mean()), "min": float(v.min()), "max": float(v.max())}
        return None
    return walk(per_seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--classifiers", nargs="+", default=["knn"])
    ap.add_argument("--readings", nargs="+", default=list(READINGS))
    ap.add_argument("--no-inner", action="store_true", help="skip protocol A (inner CV)")
    ap.add_argument("--scale", choices=("none", "minmax"), default="none")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(HERE, "validation_results.json"))
    args = ap.parse_args()
    X, y = load_keel(DATASET)
    print(f"{DATASET}: {X.shape[0]} rows, {X.shape[1]} features, {int(np.sum(y == 1))} minority", flush=True)
    rng = np.random.RandomState(0)  # rank_auc agrees with sklearn, ties included
    for _ in range(50):
        pos = rng.rand(60) < 0.3
        sc = rng.randint(0, 6, 60) / 5.0
        assert abs(rank_auc(pos, sc) - roc_auc_score(pos, sc)) < 1e-12
    store = {}
    if os.path.exists(args.out):
        with open(args.out) as fh:
            store = json.load(fh)
    for clf_name in args.classifiers:
        jobs = [(s, clf_name, list(args.readings), not args.no_inner, args.scale) for s in args.seeds]
        tag = f"{clf_name}{'' if not args.no_inner else '-noinner'}{'' if args.scale == 'none' else '-' + args.scale}"
        entry = store.setdefault(tag, {"dataset": DATASET, "paper": PAPER[clf_name], "per_seed": {}})
        entry["readings"] = list(args.readings)
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futures = [ex.submit(run_seed, j) for j in jobs]
            for fut in as_completed(futures):  # save each seed as soon as it is done
                r = fut.result()
                s = summarize(r)
                entry["per_seed"][f"seed{r['seed']}"] = s
                entry["over_seeds"] = aggregate(list(entry["per_seed"].values()))
                entry["seeds"] = sorted(int(k[4:]) for k in entry["per_seed"])
                with open(args.out, "w") as fh:
                    json.dump(store, fh, indent=1, default=float)
                print(f"\n== {clf_name}, CV seed {r['seed']} ({s['seconds']} s); k-NN check {s['knn_agreement_with_sklearn']}")
                print(f"   no oversampling: crisp {s['no_oversampling']['auc_crisp']:.1f}, score {s['no_oversampling']['auc_score']:.1f}")
                for ms in MEASURES:
                    print(f"   [{ms}] SMOTE {s['SMOTE'][ms]['value']:.1f} (N={s['SMOTE'][ms]['N']})")
                    for rd in args.readings:
                        e = s["FW-SMOTE"][rd][ms]
                        line = f"   [{ms}] FW-SMOTE {rd:15s} default {e['default_config']['value']:.1f}"
                        if "A_tuned_in_training" in e:
                            line += f" | A {e['A_tuned_in_training']['value']:.1f} (N={e['A_tuned_in_training']['N']})"
                        b = e["B_best_on_test"]
                        line += f" | B {b['value']:.1f} (N={b['N']}, {b['config']})"
                        print(line, flush=True)
        agg = entry["over_seeds"]
        print(f"\n== {clf_name}: mean [min, max] over seeds {entry['seeds']}; paper FW-SMOTE AUC "
              f"{PAPER[clf_name]['FW-SMOTE']['auc']}, SMOTE {PAPER[clf_name]['SMOTE']['auc']}")
        for ms in MEASURES:
            v = agg["SMOTE"][ms]["value"]
            print(f"   [{ms}] SMOTE {v['mean']:.1f} [{v['min']:.1f}, {v['max']:.1f}]")
            for rd in args.readings:
                e = agg["FW-SMOTE"][rd][ms]
                parts = []
                for proto in ("default_config", "A_tuned_in_training", "B_best_on_test"):
                    if proto in e:
                        v = e[proto]["value"]
                        parts.append(f"{proto.split('_')[0]} {v['mean']:.1f} [{v['min']:.1f}, {v['max']:.1f}]")
                print(f"   [{ms}] FW-SMOTE {rd:15s} " + " | ".join(parts))


if __name__ == "__main__":
    main()
