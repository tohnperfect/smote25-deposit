"""FW-SMOTE: feature-weighted SMOTE, re-implemented for the SMOTE25 rerun (WP6.8).

Reference
=========
S. Maldonado, C. Vairetti, A. Fernandez, F. Herrera. FW-SMOTE: A feature-weighted
oversampling approach for imbalanced classification. Pattern Recognition 124 (2022)
108511, doi:10.1016/j.patcog.2021.108511. "p.N" below is the journal page (1-13);
"Supp. p.N" is the supplementary Appendix A (pp.29-34).

What the method does (Algorithm 1 and Section 3.3, pp.5-6)
===========================================================
FW-SMOTE is SMOTE in which the k nearest minority neighbors of each minority example are
found with the IMOWAD distance (Definition 1, Eq. (5), p.4) instead of the Euclidean
distance. Everything else (seeds, N partners per seed, random point on the segment) is
SMOTE's. With equal weights, r = n and p = 2 it is SMOTE (p.6).

  Step 1  (p.5)  M* <- M (the minority examples are kept).
  Step 2  (p.5)  u <- FR({(x_i, y_i)}): one filter score per feature, computed on the
                 whole training set (both classes). Section 3.2 (p.5) lists four scores:
                 Fisher Score (Eq. 6), Mutual Information (Eq. 7), Correlation Score
                 (Eq. 8) and Eigenvector Centrality ([40], described in words only).
  Step 3  (p.5)  w <- RIM(u, alpha): a RIM quantifier Q gives rank position j = 1..n the
                 weight w_j = Q(j/n) - Q((j-1)/n) (Eqs. 9-12, p.5); the IOWA operator
                 (Eq. 3, p.4) gives w_j to the feature with the j-th largest u (Eq. 5).
  Step 4  (p.5)  S <- the r largest weights, or {j : w_j > epsilon}.
  Steps 5-8 (p.5) IMOWAD(x_i, x_i', w) = (sum_{j in S} w_j b_j^p)^(1/p),
                 b_j = |x_ij - x_i'j| (Eq. 5, p.4; step 7), for minority pairs i != i'.
  Step 9  (p.5)  T <- the k minority examples (other than i) with the smallest IMOWAD.
  Steps 10-15 (p.5; text p.6)  N times: draw x_k from T at random, add
                 x*_k = x_i + v (x_k - x_i) with v uniform in (0, 1) (Eq. 1, p.2; "a random
                 number v between 0 and 1", p.6), and remove x_k from T.
  Output (p.6)   M*: the original minority examples and N |M| synthetic ones. The
                 majority class is not touched. The synthetic examples have all n
                 features: S only shapes the neighborhood (pp.5-6, p.10).

Defaults
========
k = 5 (p.7). ranking = Fisher Score: the paper's recommended default (Section 5, p.11).
r = n/2, p = infinity, basic RIM, alpha = 0.4: the values that most often gave the best
AUC in the grid search (Table 4, p.9), which Section 4.3 (p.10) recommends ("Fisher Score
is the recommended feature selection strategy, while the basic RIM quantifier is the
suggested OWA approach ... the Chebyshev norm is preferred"). N: the paper tried N = 1
and N = 3 and kept the better one on test data (pp.7-8); the default here is N = 1
(CHOICE: C15, see below).

Choices the paper leaves open (each is marked CHOICE: in the code and listed in NOTES.md)
=======================================================================================
C1  Eqs. (10)-(12) do not sum to one as printed (Eq. (11) gives negative weights), while
    p.4 requires sum_j w_j = 1 and w_j in [0, 1]: every quantifier is divided by its sum,
    as the authors' code (OWAFunction.m) does.
C2  p = infinity is not defined by Eq. (5) (its limit drops the weights). Default:
    the weighted Chebyshev distance max_{j in S} w_j b_j, which is what the authors' code
    computes; chebyshev="limit" gives max_{j in S} b_j instead.
C3  S for a quantifier whose weights are not decreasing in rank (trigonometric, some
    quadratic, basic with alpha > 1): S is the r top-ranked features (largest u), as the
    authors' code does and the text implies ("subset S of relevant variables", p.5).
    For the defaults this equals "the r largest values of w" (Algorithm 1, step 4).
C4  r = n/2 or 3n/4 for odd n: r is given as a fraction and rounded half up
    (Matlab's round), within [1, n]; an integer r is a count.
C5  Ties in u: tied features share the mean of the weights of the positions they occupy
    (the usual IOWA tie rule, Yager and Filev 1999); S takes tied features in column
    order.
C6  Fisher Score: printed Eq. (6) (|mu_1 - mu_2| / (sigma_1^2 + sigma_2^2), no square
    root, although the prose says "joint standard deviation"), sample variances
    (ddof = 1, as Matlab's var in the authors' code); 0/0 -> 0 and c/0 -> +inf.
C7  Mutual Information: Eq. (7) after equal-width binning (p.5 says numerical variables
    are binned, not how); bins as in FSLib's muteinf, which the authors' code calls:
    20 bins if m/10 > 20, else max(floor(m/10), 10).
C8  Eigenvector Centrality has no formula in the paper; it follows Roffo and Melzi [40]
    as implemented in the authors' code (case 3 of SMOTEMODWOWA.m).
C9  Correlation Score Eq. (8): j' != j; correlations with a constant feature are
    ignored, and a feature with no defined correlation scores 0.
C10 epsilon rule: if no weight exceeds epsilon, S keeps the top-ranked feature.
C11 Distance ties in step 9 are broken by row order of the minority examples.
C12 If N exceeds the number of available neighbors, T is refilled once emptied, so each
    seed still gets N synthetic examples (the paper assumes N < k, p.6).
C13 Minority class: the class with fewer examples; with equal counts, the smaller label.
C14 The two-class method (p.5: "Assuming a two-class problem") raises an error for other
    numbers of classes.
C15 N, the amount of oversampling, has no default in the paper (it keeps the better of
    N = 1 and N = 3 on test data, pp.7-8): N = 1, the first value listed.

variant="smoteiowa2019" (reproduction aid, not the default)
===========================================================
The paper links its code to github.com/cvairetti (p.8). The only matching repository
there, cvairetti/SMOTEIOWA (commit 9d2f306, 23 April 2019, files SMOTEMODWOWA.m and
OWAFunction.m), differs from the paper's text in five ways, which this variant mimics
(re-written here, the Matlab code was read, not run):
  (a) the RIM weights are computed over the r selected positions (n replaced by r);
  (b) the distance is the plain Minkowski distance of the weighted features w_j x_j,
      i.e. (sum w_j^p b_j^p)^(1/p) instead of Eq. (5) (same for p = 1);
  (c) the N partners are drawn with replacement (randi);
  (d) the gap is fixed, v = 0.3 ("u=0.3; %non-random version");
  (e) the MI ranking is FSLib's muteinf (normalized MI, 2 I / (H(X) + H(Y)), clipped at 0).

Weights and solvers
===================
The paper defines no optimization problem for the weights: they are closed-form
(filter score -> rank -> quantifier increments, Algorithm 1 steps 2-3). The arg min of
step 9 is solved exactly by sorting distances (the objective is a sum over T, so the best
k-subset is the k smallest distances), as the authors' code does with Matlab's sort.
Eigenvector Centrality uses the leading eigenvector of a symmetric non-negative matrix:
numpy.linalg.eigh (dense LAPACK) here, Matlab eigs(A, 1, 'lm') (ARPACK) in the authors'
code; both give the Perron vector up to its sign, which abs() removes.
"""

import numbers

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator
from sklearn.utils import check_random_state

__all__ = [
    "FWSMOTE",
    "fisher_score",
    "mutual_information_score",
    "correlation_score",
    "eigenvector_centrality_score",
    "rim_weights",
    "iowa_feature_weights",
]

RANKINGS = ("fisher", "mi", "ec", "cfs")
QUANTIFIERS = ("basic", "quadratic", "exponential", "trigonometric")
VARIANTS = ("paper", "smoteiowa2019")


# ==================================================================================
# Step 2: feature ranking methods (Section 3.2, p.5)
# ==================================================================================
def _var(A):
    """Column variances with ddof = 1 (Matlab's var); a single row gives 0, as in Matlab."""
    if A.shape[0] < 2:
        return np.zeros(A.shape[1])
    return A.var(axis=0, ddof=1)


def fisher_score(X, y, positive):
    """Fisher Score, Eq. (6), p.5: FS(j) = |mu_j1 - mu_j2| / (sigma_j1^2 + sigma_j2^2).

    CHOICE: (C6) the printed equation (no square root; the authors' code computes the same
    ratio with Matlab's var, ddof = 1). A feature constant in both classes with equal means
    (0/0) scores 0; one constant within each class with different means (c/0) scores +inf.
    """
    X = np.asarray(X, dtype=float)
    pos = np.asarray(y) == positive
    num = np.abs(X[pos].mean(axis=0) - X[~pos].mean(axis=0))
    den = _var(X[pos]) + _var(X[~pos])
    with np.errstate(divide="ignore", invalid="ignore"):
        fs = num / den
    fs[(den == 0) & (num == 0)] = 0.0
    fs[(den == 0) & (num > 0)] = np.inf
    return fs


def _n_bins(m):
    """CHOICE: (C7) number of equal-width bins of FSLib's muteinf (called by the authors'
    code): 20 if m/10 > 20, else max(floor(m/10), 10)."""
    return 20 if m / 10.0 > 20 else max(m // 10, 10)


def _bin(x, nbins):
    """Equal-width bins on [min x, max x]; the last bin is closed (as in muteinf)."""
    lo, hi = float(np.min(x)), float(np.max(x))
    if not hi > lo:
        return np.zeros(x.shape[0], dtype=np.intp)
    edges = np.linspace(lo, hi, nbins + 1)
    idx = np.searchsorted(edges, x, side="right") - 1
    return np.clip(idx, 0, nbins - 1)


def mutual_information_score(X, y):
    """Mutual Information, Eq. (7), p.5: MI(j) = sum_y sum_x p(x, y) log(p(x, y) / (p(x) p(y))).

    p.5: the covariates are taken as nominal, "can be used with numerical variables after
    binning them". CHOICE: (C7) equal-width binning with FSLib's bin count, plug-in
    probabilities, natural logarithm, 0 log 0 = 0.
    """
    X = np.asarray(X, dtype=float)
    m, n = X.shape
    nb = _n_bins(m)
    _, yi = np.unique(np.asarray(y), return_inverse=True)
    ncls = int(yi.max()) + 1
    py = np.bincount(yi, minlength=ncls) / m
    mi = np.zeros(n)
    for j in range(n):
        b = _bin(X[:, j], nb)
        joint = np.zeros((nb, ncls))
        np.add.at(joint, (b, yi), 1.0)
        pxy = joint / m
        px = pxy.sum(axis=1)
        nz = pxy > 0
        mi[j] = float(np.sum(pxy[nz] * np.log(pxy[nz] / np.outer(px, py)[nz])))
    return np.maximum(mi, 0.0)


def _muteinf(x, y_pm):
    """FSLib's muteinf as called by the authors' code (EC and variant (e) only).

    Normalized MI 2 I / (H(X) + H(Y)) with 1e-5 in empty cells, labels in {-1, +1}.
    CHOICE: (C8) a constant feature scores 0 (muteinf's hist and interval counts disagree
    for it and give a spurious large value).
    """
    m = x.shape[0]
    if not np.max(x) > np.min(x):
        return 0.0
    nb = _n_bins(m)
    b = _bin(x, nb)
    pA = np.bincount(b, minlength=nb) / m
    pA[pA == 0] = 1e-5
    pY = np.array([np.sum(y_pm == 1), np.sum(y_pm == -1)], dtype=float) / m
    cnt = np.zeros((2, nb))
    np.add.at(cnt, (np.where(y_pm == 1, 0, 1), b), 1.0)
    cnt[cnt == 0] = 1e-5
    p = cnt / m
    hx = -np.sum(pA * np.log(pA))
    hy = -np.sum(pY * np.log(pY))
    info = np.sum(p * np.log(p / (pA[None, :] * pY[:, None])))
    return float(2.0 * info / (hx + hy))


def _minmax(A):
    """(A - min) / (max - min); a constant matrix gives zeros (Matlab would give NaN)."""
    lo, hi = np.min(A), np.max(A)
    if not hi > lo:
        return np.zeros_like(A)
    return (A - lo) / (hi - lo)


def eigenvector_centrality_score(X, y, positive, mix=0.5):
    """Eigenvector Centrality ([40], p.5): "combines the Fisher Score, the Mutual
    Information, and the covariates' standard deviation to construct an adjacency matrix
    A. Then, feature importance is assessed by computing the eigenvector related to the
    largest eigenvalue of A."

    CHOICE: (C8) the paper gives no formula; this follows Roffo and Melzi's ECFS as coded
    in the authors' SMOTEMODWOWA.m (case 3): sep_j = (mu_j+ - mu_j-)^2 / (s_j+^2 + s_j-^2)
    (a zero denominator replaced by 10000), mi_j = muteinf, v = |sep + mi| / 2,
    K = minmax(v v^T), Sigma_ij = minmax(max(s_i, s_j)) with s the overall standard
    deviations (ddof = 1), A = 0.5 K + 0.5 Sigma, score = |leading eigenvector of A|.
    Solver: numpy.linalg.eigh, largest eigenvalue (eigs(A, 1, 'lm') in the authors' code;
    the same vector for a non-negative A, up to sign).
    """
    X = np.asarray(X, dtype=float)
    y_pm = np.where(np.asarray(y) == positive, 1, -1)
    n = X.shape[1]
    mi = np.array([_muteinf(X[:, j], y_pm) for j in range(n)])
    Xp, Xn = X[y_pm == 1], X[y_pm == -1]
    sep = (Xp.mean(axis=0) - Xn.mean(axis=0)) ** 2
    st = _var(Xp) + _var(Xn)
    st[st == 0] = 10000.0
    sep = sep / st
    vec = np.abs(sep + mi) / 2.0
    K = _minmax(np.outer(vec, vec))
    sd = np.sqrt(_var(X))
    Sig = _minmax(np.maximum(sd[:, None], sd[None, :]))
    A = mix * K + (1.0 - mix) * Sig
    if not np.any(A):
        return np.zeros(n)
    evals, evecs = np.linalg.eigh(A)
    return np.abs(evecs[:, int(np.argmax(evals))])


def correlation_score(X):
    """Correlation Score, Eq. (8), p.5: CFS(j) = min_{j'} |rho_{j,j'}| (Pearson).

    CHOICE: (C9) the minimum is over j' != j; correlations involving a constant feature
    are undefined and ignored (Matlab's min skips NaN); a feature with no defined
    correlation scores 0. A high score ranks first (Remark 2, p.6: the score "weighs down
    attributes that are uncorrelated with others").
    """
    X = np.asarray(X, dtype=float)
    n = X.shape[1]
    if n == 1:
        return np.ones(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        R = np.abs(np.corrcoef(X, rowvar=False))
    R = np.atleast_2d(R)
    np.fill_diagonal(R, np.nan)
    out = np.zeros(n)
    for j in range(n):
        row = R[j][~np.isnan(R[j])]
        if row.size:
            out[j] = row.min()
    return out


# ==================================================================================
# Step 3: RIM quantifiers and the IOWA ordering (Eqs. 3, 5, 9-12, pp.4-5)
# ==================================================================================
def rim_weights(n, alpha, quantifier="basic"):
    """Position weights w_j = Q(j/n) - Q((j-1)/n), j = 1..n (Eqs. 9-12, p.5).

    basic          Q(x) = x^alpha                       Eq. (9)
    quadratic      Q(x) = 1 / (1 - alpha x^0.5)         Eq. (10)
    exponential    Q(x) = exp(-alpha x)                 Eq. (11)
    trigonometric  Q(x) = arcsin(alpha x)               Eq. (12)

    CHOICE: (C1) the weights are divided by their sum (p.4 requires sum_j w_j = 1 and
    w_j in [0, 1]; Eqs. 10-12 do not satisfy it as printed, Eq. 11 is negative), as the
    authors' OWAFunction.m does. For Eq. (9) the sum is already 1.
    """
    if quantifier not in QUANTIFIERS:
        raise ValueError(f"quantifier must be one of {QUANTIFIERS}, got {quantifier!r}")
    n = int(n)
    alpha = float(alpha)
    if n < 1:
        raise ValueError("n must be at least 1")
    if not alpha > 0:
        raise ValueError("alpha must be positive")
    if quantifier == "quadratic" and not alpha < 1:
        raise ValueError("the quadratic quantifier needs alpha < 1")
    if quantifier == "trigonometric" and alpha > 1:
        raise ValueError("the trigonometric quantifier needs alpha <= 1")
    t = np.arange(n + 1, dtype=float) / n
    if quantifier == "basic":
        Q = t ** alpha
    elif quantifier == "quadratic":
        Q = 1.0 / (1.0 - alpha * np.sqrt(t))
    elif quantifier == "exponential":
        Q = np.exp(-alpha * t)
    else:
        Q = np.arcsin(alpha * t)
    w = np.diff(Q)
    return w / w.sum()


def iowa_feature_weights(u, q):
    """Give position weight q[j] to the feature with the (j+1)-th largest u (IOWA, Eq. 3
    and Eq. 5, p.4: "b_j is the |x_ij - x_i'j| value of the 3-tuple with the jth largest
    of the u vector").

    CHOICE: (C5) tied u values share the mean of the weights of the positions they occupy
    (the IOWA tie rule); the order lists tied features by column index.
    Returns (w, order): w[f] is the weight of feature f, order[0] the top-ranked feature.
    """
    u = np.asarray(u, dtype=float)
    q = np.asarray(q, dtype=float)
    n = u.shape[0]
    order = np.argsort(-u, kind="stable")
    su = u[order]
    wq = q[:n].copy()
    start = 0
    for t in range(1, n + 1):
        if t == n or su[t] != su[start]:
            if t - start > 1:
                wq[start:t] = q[start:t].mean()
            start = t
    w = np.empty(n)
    w[order] = wq
    return w, order


def _k_smallest(D, k):
    """Column indices of the k smallest entries of each row of D, ordered by (value,
    column): the first k of a stable argsort, found with a partition (CHOICE: C11)."""
    kth = np.partition(D, k - 1, axis=1)[:, k - 1 : k]
    cand = D <= kth
    cnt = cand.sum(axis=1)
    out = np.empty((D.shape[0], k), dtype=np.intp)
    easy = cnt == k
    if np.any(easy):
        cols = np.nonzero(cand[easy])[1].reshape(-1, k)  # increasing column per row
        d = np.take_along_axis(D[easy], cols, axis=1)
        out[easy] = np.take_along_axis(cols, np.argsort(d, axis=1, kind="stable"), axis=1)
    for i in np.flatnonzero(~easy):  # ties at the k-th value
        idx = np.flatnonzero(cand[i])
        out[i] = idx[np.argsort(D[i, idx], kind="stable")][:k]
    return out


# ==================================================================================
# The sampler
# ==================================================================================
class FWSMOTE(BaseEstimator):
    """FW-SMOTE oversampler (Algorithm 1, p.5) with the interface of imbalanced-learn.

    Parameters (paper symbols in brackets)
    ==========
    N : int, default 1
        [N] synthetic examples per minority example (Algorithm 1 steps 10-15). The paper
        uses N in {1, 3} (100% and 300% oversampling, p.7) and keeps the better one on
        test data (p.8). CHOICE: (C15) default 1, the first value listed. N may exceed the
        number of neighbors (CHOICE: C12).
    k : int, default 5
        [k] nearest minority neighbors (p.7: "k = 5, as suggested in the original paper").
        Capped at |M| - 1.
    ranking : {"fisher", "mi", "ec", "cfs"} or callable, default "fisher"
        [FR] feature ranking of step 2: Fisher Score (Eq. 6), Mutual Information (Eq. 7),
        Eigenvector Centrality ([40]) or Correlation Score (Eq. 8). Fisher Score is the
        paper's recommended default (p.11). A callable f(X, y) -> u (one score per
        feature, larger = more relevant) is also accepted.
    quantifier : {"basic", "quadratic", "exponential", "trigonometric"}, default "basic"
        [RIM] quantifier of step 3 (Eqs. 9-12). Basic RIM is suggested (p.10).
    alpha : float, default 0.4
        [alpha] quantifier parameter; the paper explores {0.4, 0.6} (p.7) and 0.4 is best
        most often (Table 4, p.9).
    r : float in (0, 1] or int >= 1, default 0.5
        [r] number of features kept for the distance (step 4): a float is a fraction of n
        (rounded half up, CHOICE: C4), an int is a count. The paper explores
        {n/2, 3n/4, n} (p.7); n/2 is best most often (Table 4, p.9).
    epsilon : float or None, default None
        [epsilon] threshold alternative of step 4: S = {j : w_j > epsilon}. If given,
        r is ignored. CHOICE: (C10) an empty S keeps the top-ranked feature.
    p : float >= 1 or numpy.inf, default numpy.inf
        [p] Minkowski parameter of Eq. (5); the paper explores {1, 2, inf} (p.7) and
        prefers the Chebyshev norm (p = inf, Table 4 p.9, text p.10).
    chebyshev : {"weighted", "limit"}, default "weighted"
        CHOICE: (C2) meaning of p = inf. "weighted": max_{j in S} w_j b_j (the authors'
        code); "limit": max_{j in S} b_j, the limit of Eq. (5), where the weights drop out.
    variant : {"paper", "smoteiowa2019"}, default "paper"
        "paper" follows the paper's text. "smoteiowa2019" mimics the authors' 2019 Matlab
        code where it departs from the text (see the module docstring); it is meant for
        validation, not for the rerun.
    random_state : None, int or numpy.random.RandomState
        Seed of the partner draws and of the gaps.

    Attributes after fit_resample
    =============================
    minority_label_, minority_indices_ : the minority class and its rows in X.
    feature_scores_ : u (step 2). feature_weights_ : w per feature (step 3).
    feature_order_ : features by decreasing u. selected_features_ : S (step 4), in rank
    order. distance_weights_ : the weights of S as used in the distance.
    neighbors_ : (|M|, k) positions in minority_indices_ of each seed's neighbors T, by
    increasing IMOWAD (step 9). n_synthetic_ : N |M|.
    """

    def __init__(
        self,
        N=1,
        k=5,
        ranking="fisher",
        quantifier="basic",
        alpha=0.4,
        r=0.5,
        epsilon=None,
        p=np.inf,
        chebyshev="weighted",
        variant="paper",
        random_state=None,
    ):
        self.N = N
        self.k = k
        self.ranking = ranking
        self.quantifier = quantifier
        self.alpha = alpha
        self.r = r
        self.epsilon = epsilon
        self.p = p
        self.chebyshev = chebyshev
        self.variant = variant
        self.random_state = random_state

    # -- parameter checks ============================================================
    def _check_params(self):
        if not isinstance(self.N, (numbers.Integral, np.integer)) or self.N < 0:
            raise ValueError(f"N must be a non-negative integer, got {self.N!r}")
        if not isinstance(self.k, (numbers.Integral, np.integer)) or self.k < 1:
            raise ValueError(f"k must be a positive integer, got {self.k!r}")
        if not (callable(self.ranking) or self.ranking in RANKINGS):
            raise ValueError(f"ranking must be one of {RANKINGS} or a callable")
        if self.quantifier not in QUANTIFIERS:
            raise ValueError(f"quantifier must be one of {QUANTIFIERS}")
        p = float(self.p)
        if not p >= 1:
            raise ValueError("p must be >= 1 (p.4: 'for p >= 1')")
        if self.chebyshev not in ("weighted", "limit"):
            raise ValueError("chebyshev must be 'weighted' or 'limit'")
        if self.variant not in VARIANTS:
            raise ValueError(f"variant must be one of {VARIANTS}")
        rim_weights(1, self.alpha, self.quantifier)  # validates alpha for the quantifier
        return p

    def _resolve_r(self, n):
        """CHOICE: (C4) a float r is a fraction of n, rounded half up (Matlab's round),
        within [1, n]; an integer r is a count (at most n)."""
        r = self.r
        if isinstance(r, (bool, np.bool_)):
            raise ValueError("r must be a number")
        if isinstance(r, (numbers.Integral, np.integer)):
            if r < 1:
                raise ValueError("an integer r must be >= 1")
            return int(min(r, n))
        r = float(r)
        if not 0 < r <= 1:
            raise ValueError("a fractional r must lie in (0, 1]")
        return int(min(n, max(1, np.floor(r * n + 0.5))))

    # -- step 2 ======================================================================
    def _scores(self, X, y, positive):
        """Step 2 (p.5): u <- FR({(x_i, y_i)}) on the whole training set."""
        if callable(self.ranking):
            u = np.asarray(self.ranking(X, y), dtype=float).ravel()
            if u.shape[0] != X.shape[1] or np.any(np.isnan(u)):
                raise ValueError("the ranking callable must return one non-NaN score per feature")
            return u
        if self.ranking == "fisher":
            return fisher_score(X, y, positive)
        if self.ranking == "mi":
            if self.variant == "smoteiowa2019":  # variant (e): max(muteinf(x_j, Y), 0)
                y_pm = np.where(y == positive, 1, -1)
                return np.maximum([_muteinf(X[:, j], y_pm) for j in range(X.shape[1])], 0.0)
            return mutual_information_score(X, y)
        if self.ranking == "ec":
            return eigenvector_centrality_score(X, y, positive)
        return correlation_score(X)

    # -- steps 3-4 ===================================================================
    def _weights_and_subset(self, u):
        """Steps 3-4 (p.5). Returns (w for all features, order, S, weights of S used in
        the distance)."""
        n = u.shape[0]
        q = rim_weights(n, self.alpha, self.quantifier)  # Eqs. (9)-(12) over n positions
        w, order = iowa_feature_weights(u, q)  # Eq. (5): w_j goes to the j-th largest u
        if self.epsilon is None:
            # CHOICE: (C3) S = the r top-ranked features; equal to "the r largest values
            # of w" (step 4) whenever w decreases with rank, as for the defaults.
            S = order[: self._resolve_r(n)]
        else:
            S = order[w[order] > float(self.epsilon)]  # step 4, threshold form
            if S.size == 0:  # CHOICE: (C10)
                S = order[:1]
        if self.variant == "smoteiowa2019":
            # variant (a): OWAFunction(nvars, alpha, quantif) over the |S| kept positions
            wS, _ = iowa_feature_weights(u[S], rim_weights(S.size, self.alpha, self.quantifier))
        else:
            wS = w[S]  # step 7 sums w_j over j in S, with the weights of step 3
        return w, order, S, wS

    # -- steps 5-9 ===================================================================
    def _distance_block(self, A_rows, A_all, wS, p):
        """IMOWAD between minority examples on the features of S (Eq. 5, p.4; step 7)."""
        if self.variant == "smoteiowa2019":
            # variant (b): pdist(W .* Xsel, norm_type) = (sum (w_j b_j)^p)^(1/p)
            Za, Zb = A_rows * wS, A_all * wS
            if np.isinf(p):
                return cdist(Za, Zb, "chebyshev")
            return cdist(Za, Zb, "minkowski", p=p)
        if np.isinf(p):
            if self.chebyshev == "weighted":  # CHOICE: (C2) max_{j in S} w_j b_j
                return cdist(A_rows * wS, A_all * wS, "chebyshev")
            return cdist(A_rows, A_all, "chebyshev")  # limit of Eq. (5): max_{j in S} b_j
        # Eq. (5): (sum_{j in S} w_j b_j^p)^(1/p); scipy's weighted Minkowski is exactly this
        return cdist(A_rows, A_all, "minkowski", p=p, w=wS)

    def _neighbors(self, A, wS, p, k):
        """Steps 5-9 (p.5): for each minority example, the k others with the smallest
        IMOWAD. The arg min over subsets T of size k of sum_{i' in T} IMOWAD (step 9) is
        attained by the k smallest distances, so it is solved exactly by sorting.
        CHOICE: (C11) ties are broken by row order. Rows are processed in blocks to keep
        memory bounded."""
        m = A.shape[0]
        out = np.empty((m, k), dtype=np.intp)
        block = max(1, int(4_000_000 // max(m, 1)))
        for s in range(0, m, block):
            e = min(m, s + block)
            D = self._distance_block(A[s:e], A, wS, p)
            D[np.arange(e - s), np.arange(s, e)] = np.inf  # T is a subset of M \ {i}
            out[s:e] = _k_smallest(D, k)
        return out

    # -- main ========================================================================
    def fit_resample(self, X, y):
        """Run Algorithm 1 (p.5) and return (X_res, y_res): the original rows first, then
        the N |M| synthetic minority rows (seed by seed, in the order of step 5)."""
        p = self._check_params()
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if X.ndim != 2 or y.ndim != 1 or X.shape[0] != y.shape[0]:
            raise ValueError("X must be 2-D and y 1-D with as many rows as X")
        if not np.all(np.isfinite(X)):
            raise ValueError("X contains NaN or infinite values")
        classes, counts = np.unique(y, return_counts=True)
        if classes.size != 2:
            # CHOICE: (C14) the paper's method is two-class (p.5)
            raise ValueError(f"FW-SMOTE is a two-class method; y has {classes.size} classes")
        minority = classes[int(np.argmin(counts))]  # CHOICE: (C13) ties -> smaller label
        midx = np.flatnonzero(y == minority)
        M = X[midx]
        m_min, n = M.shape
        if m_min < 2:
            raise ValueError("FW-SMOTE needs at least 2 minority examples")

        # Step 1: M* <- M (the original rows are returned unchanged, first).
        # Step 2: feature ranking on the whole training set.
        u = self._scores(X, y, minority)
        # Steps 3-4: RIM weights through the IOWA order, and the subset S.
        w, order, S, wS = self._weights_and_subset(u)
        # Steps 5-9: neighborhood T of size k under IMOWAD restricted to S.
        k_eff = int(min(self.k, m_min - 1))
        nbrs = self._neighbors(M[:, S], wS, p, k_eff)

        # Steps 10-15: N partners per seed, drawn from T, and the random gap.
        rng = check_random_state(self.random_state)
        N = int(self.N)
        if self.variant == "smoteiowa2019":
            picks = rng.randint(0, k_eff, size=(m_min, N))  # variant (c): with replacement
            gaps = np.full((m_min, N), 0.3)  # variant (d): fixed gap
        else:
            # Step 11 draws x_k uniformly from T and step 14 removes it: the N partners are
            # the first N entries of a random permutation of T.
            # CHOICE: (C12) if N > |T|, T is refilled (another permutation) once emptied.
            n_pass = -(-N // k_eff) if N else 0
            keys = rng.random_sample((m_min, n_pass, k_eff))
            picks = np.argsort(keys, axis=2).reshape(m_min, n_pass * k_eff)[:, :N]
            gaps = rng.random_sample((m_min, N))  # step 12: v uniform in [0, 1)
        partners = np.take_along_axis(nbrs, picks, axis=1)
        seeds = np.repeat(np.arange(m_min), N)
        P = partners.reshape(-1)
        G = gaps.reshape(-1, 1)
        X_syn = M[seeds] + G * (M[P] - M[seeds])  # step 12: x*_k = x_i + v (x_k - x_i)

        # fitted attributes
        self.n_features_in_ = n
        self.minority_label_ = minority
        self.minority_indices_ = midx
        self.feature_scores_ = u
        self.feature_weights_ = w
        self.feature_order_ = order
        self.selected_features_ = S
        self.distance_weights_ = wS
        self.neighbors_ = nbrs
        self.n_synthetic_ = int(X_syn.shape[0])

        # Step 13 and the output: M* appended to the unchanged training set.
        X_res = np.vstack([X, X_syn])
        y_res = np.concatenate([y, np.full(X_syn.shape[0], minority, dtype=y.dtype)])
        return X_res, y_res
