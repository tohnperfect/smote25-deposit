"""RSMOTE, re-implemented for the SMOTE25 rerun (WP6.8).

Paper: B. Chen, S. Xia, Z. Chen, B. Wang and G. Wang, "RSMOTE: A self-adaptive
robust SMOTE for imbalanced problems with label noise", Information Sciences
553 (2021) 397-428, doi:10.1016/j.ins.2020.10.013.  Pages below are the
journal's printed page numbers.

This is an independent implementation written from the paper.  The authors'
code (github.com/syxiaa/RSMOTE, RSMOTE_V8.py, last commit 26 Aug 2020) was read
as a reference only; NOTES.md lists every difference between it and the paper.

The method, step by step:

Input   D = P u Q (minority P, majority Q), the expected imbalance ratio IR and
        the number of nearest neighbors k (Algorithm 1, p. 403).
Line 2  N = |Q| / IR - |P| synthetic samples in total (Alg. 1 line 2, p. 403).
        |P| counts every minority sample, the ones Step 1 calls noise
        included, so D plus the synthetic set has the ratio IR (exactly for
        IR = 1; |Q| / IR is truncated otherwise).
Step 1  (p. 402; Alg. 1 lines 3-12)  For every x_i in P find its k nearest
        neighbors "from the entire set D" and count the majority ones, m_i
        (0 <= m_i <= k).  If m_i = k, x_i is a noisy sample [29] and "is not
        operated in the following steps"; otherwise x_i joins the seed set P'
        and gets its relative density, Eq. (2) of Definition 3 (p. 401):
            RD(p) = AbsoluteDensity(p, D+) / AbsoluteDensity(p, D-)
                  = sum_{o in HENk(p)} d(p, o) / sum_{q in HONk(p)} d(p, q),
        with the absolute density k / sum d(p, q) of Eq. (1) (Definition 1),
        HONk(p) the k nearest neighbors of p in its own class D+ and HENk(p)
        the k nearest in the other class D- (Definition 2, p. 401), and d the
        Euclidean distance (p. 412).
Step 2  (p. 402; Alg. 1 lines 13-14)  2-means on the one-dimensional vector
        RD(P') gives clusters C_A and C_B with centers c_A >= c_B; P'_A (larger
        RD: safe samples) and P'_B (smaller RD: borderline samples) are the
        matching seeds (p. 402, first paragraph).
Step 3  (p. 402; Alg. 1 lines 16-25)  For each cluster j in {A, B}:
            N_j  = |P'_j| / |P'| * N                       (line 17)
            w_i  = (k - m_i) / (k + 1)   for x_i in P'_j    (line 19)
            w~_i = w_i / sum_{x_l in P'_j} w_l              (line 20)
            N_i  = w~_i * N_j                               (line 21)
            Populate(N_i, i, nnarray)                       (line 22)
        Populate is SMOTE's routine [11]: every new sample is
        x_i + gap * (x_nn - x_i), with x_nn drawn at random from the k nearest
        neighbors of x_i and gap uniform on [0, 1].  New samples are generated
        "within each cluster" (p. 398; p. 402), so x_nn is taken from P'_j.
Output  Syn = Syn_A u Syn_B (Alg. 1 line 26).  fit_resample returns D followed
        by Syn.  The noisy samples stay in the training data: the
        oversamplers, RSMOTE included, "do not filter any noisy samples from
        the original data sets, which just aim at avoiding interpolating in the
        noisy area" (p. 412; again p. 416).
Classes (Sec. 4.3.3, p. 414)  With several classes, every class Y_t smaller
        than the largest class Y_s is oversampled "with respect to class Y_s"
        until it holds |Y_s| / IR samples (all classes equal when IR = 1).  Two
        classes are the special case with one smaller class.

Every choice the paper leaves open is marked CHOICE below and listed in
NOTES.md.  Uses NumPy and scikit-learn only.
"""

import warnings

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.neighbors import NearestNeighbors
from sklearn.utils import check_random_state

__all__ = ["RSMOTE", "two_means_1d"]


def _knn(fit_X, query_X, n_neighbors):
    """Exact Euclidean nearest neighbors: (distances, indices), nearest first.

    CHOICE: (C14, C5) a ball tree computes every distance from coordinate
    differences, so exact duplicates are at distance exactly 0 (the
    brute-force route of scikit-learn uses |a|^2 + |b|^2 - 2ab and can leave
    about 1e-8).  The
    zero-distance rules for RD below need exact zeros.  Ties are broken in the
    order the search returns them; Definition 1 (p. 401) would keep every
    neighbor tied with the k-th one, we keep exactly k.
    """
    nn = NearestNeighbors(n_neighbors=n_neighbors, algorithm="ball_tree")
    nn.fit(fit_X)
    return nn.kneighbors(query_X, return_distance=True)


def _drop_self(dist, ind, self_index):
    """Remove each query point from its own neighbor list.

    The search asked for one neighbor more than needed.  CHOICE: (C5) the query
    point is removed by its index, so an exact duplicate of it (another row
    at distance 0) still counts as a neighbor; if the point itself was not
    returned (more duplicates than neighbors asked for), the last one is
    dropped instead.
    """
    hit = ind == np.asarray(self_index)[:, None]
    hit[~hit.any(axis=1), -1] = True
    keep = ~hit
    n, width = ind.shape
    return dist[keep].reshape(n, width - 1), ind[keep].reshape(n, width - 1)


def _round_keep_sum(quota, total):
    """Integers close to the real `quota` that add up exactly to `total`.

    CHOICE: (C10) the paper's N_j and N_i (Alg. 1 lines 17 and 21) are real
    numbers and it does not say how they are rounded.  We use the largest
    remainder method (floor, then one more for the largest fractional parts,
    earlier position first on ties), so the totals are exactly N_j and N.
    """
    quota = np.asarray(quota, dtype=float)
    out = np.floor(quota).astype(int)
    rest = int(total) - int(out.sum())
    frac = quota - out
    if rest > 0:
        out[np.argsort(-frac, kind="stable")[:rest]] += 1
    elif rest < 0:  # only reachable through floating-point error
        for i in np.argsort(frac, kind="stable"):
            if rest == 0:
                break
            if out[i] > 0:
                out[i] -= 1
                rest += 1
    return out


def two_means_1d(values):
    """2-means of a one-dimensional vector (Step 2, p. 402; Alg. 1 line 13).

    Returns a boolean mask of the cluster with the larger center (C_A), or
    None when the values cannot be split (fewer than two distinct values).

    CHOICE: (C8) the paper names "2-means clustering" without an initialization
    or a number of restarts.  In one dimension the optimal 2-means clusters
    are two intervals of the sorted values, so we return the exact minimum
    of the within-cluster sum of squares over all splits between distinct
    values.  This is deterministic and is the solution Lloyd's algorithm
    with restarts (the authors' code calls scikit-learn's k_means) aims at.
    """
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return None
    order = np.argsort(v, kind="stable")
    s = v[order] - v.mean()
    n = s.size
    cs, cq = np.cumsum(s), np.cumsum(s * s)
    n_left = np.arange(1, n)
    n_right = n - n_left
    s_left, q_left = cs[:-1], cq[:-1]
    s_right, q_right = cs[-1] - s_left, cq[-1] - q_left
    sse = (q_left - s_left ** 2 / n_left) + (q_right - s_right ** 2 / n_right)
    valid = s[:-1] < s[1:]
    if not valid.any():
        return None
    sse[~valid] = np.inf
    cut = int(np.argmin(sse))
    high = np.zeros(n, dtype=bool)
    high[order[cut + 1:]] = True
    return high


class RSMOTE(BaseEstimator):
    """RSMOTE oversampler (Chen et al., Information Sciences 553, 2021).

    Parameters:

    k_neighbors : int, default=5
        k of Algorithm 1 (p. 403): the neighbors used for the noise test and
        the weights (Step 1, Step 3), for the relative density (Eq. 2) and
        for interpolation ("the same k-nearest neighbors", pp. 398 and 404).
        CHOICE: (C1) the paper tunes k over {3, 5, 20} (p. 409) and states no
        single default; 5 is the authors' code default.
    ir : float, default=1.0
        IR of Algorithm 1: the majority-to-minority ratio wanted after
        oversampling (N = |Q| / IR - |P|, line 2).  CHOICE: (C2) 1 (balance) is
        the authors' code default and what Sec. 4.3.3 (p. 414) does with
        several classes; the binary experiments do not state IR.
    random_state : None, int or numpy.random.RandomState, default=None
        Seed for the random neighbor and gap of every synthetic sample.

    Attributes:

    info_ : dict
        Set by fit_resample, keyed by every oversampled class label.  Each
        entry holds 'majority_label', 'k' (after any reduction), 'n_synthetic',
        'noise_index' (rows of X found noisy in Step 1; they stay in the
        output), 'seed_index' (rows of X in P'), and for those seeds 'm',
        'relative_density' (Eq. 2, inf where the homogeneous distances are
        all zero), 'cluster' (0 = C_A safe, 1 = C_B borderline), 'n_per_seed'
        (N_i), and 'split' (False when P' was kept as one cluster).
    """

    def __init__(self, k_neighbors=5, ir=1.0, random_state=None):
        self.k_neighbors = k_neighbors
        self.ir = ir
        self.random_state = random_state

    def fit_resample(self, X, y):
        """Return (X_res, y_res): the original rows in their order, then the
        synthetic rows.  CHOICE: (C15) synthetic rows are ordered by class
        label, then cluster A before B (Syn = Syn_A u Syn_B, Alg. 1 line 26),
        then seed."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if X.ndim != 2:
            raise ValueError("X must be a two-dimensional array")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("y must be one-dimensional with one label per row of X")
        if not np.all(np.isfinite(X)):
            raise ValueError("X contains NaN or infinite values")
        k = int(self.k_neighbors)
        if k < 1:
            raise ValueError("k_neighbors must be at least 1")
        ir = float(self.ir)
        if not ir > 0:
            raise ValueError("ir must be positive")
        rng = check_random_state(self.random_state)

        labels, counts = np.unique(y, return_counts=True)
        if labels.size < 2:
            raise ValueError("RSMOTE needs at least two classes in y")
        # Sec. 4.3.3 (p. 414): the largest class Y_s is the reference; every
        # smaller class Y_t is balanced "with respect to class Y_s".
        # CHOICE: (C13) with several classes, D for class Y_t is Y_t u Y_s only (the
        # authors' code does the same); one-against-the-rest is the other
        # reading.  Ties for the largest class: the first label in sorted
        # order is Y_s, and no class of that size is oversampled.
        s = int(np.argmax(counts))
        idx_q = np.flatnonzero(y == labels[s])

        X_parts, y_parts = [X], [y]
        self.info_ = {}
        for label, count in zip(labels, counts):
            if count >= counts[s]:
                continue
            idx_p = np.flatnonzero(y == label)
            syn, info = self._oversample_class(X[idx_p], X[idx_q], k, ir, rng)
            info["majority_label"] = labels[s]
            info["noise_index"] = idx_p[info.pop("noise_pos")]
            info["seed_index"] = idx_p[info.pop("seed_pos")]
            self.info_[label] = info
            X_parts.append(syn)
            y_parts.append(np.full(syn.shape[0], label, dtype=y.dtype))
        return np.vstack(X_parts), np.concatenate(y_parts)

    @staticmethod
    def _oversample_class(P, Q, k_param, ir, rng):
        """Algorithm 1 (p. 403) for one minority class P against Q.

        Returns the synthetic rows and a dict of diagnostics.
        """
        n_p, n_q, n_feat = P.shape[0], Q.shape[0], P.shape[1]
        empty = np.empty((0, n_feat))
        info = {"k": None, "n_synthetic": 0, "split": False,
                "noise_pos": np.empty(0, dtype=int), "seed_pos": np.empty(0, dtype=int),
                "m": np.empty(0, dtype=int), "relative_density": np.empty(0),
                "cluster": np.empty(0, dtype=int), "n_per_seed": np.empty(0, dtype=int)}

        # Alg. 1 line 2 (p. 403): N = |Q| / IR - |P|.
        # CHOICE: (C3) |Q| / IR is truncated to an integer (the paper does not
        # round; the authors' code truncates).
        n_syn = int(n_q / ir) - n_p
        if n_syn <= 0:
            return empty, info

        # CHOICE: (C4) a class with k or fewer members uses k = |P| - 1 throughout
        # (the authors' code does the same); the paper assumes |P| > k.
        k = min(k_param, n_p - 1)
        info["k"] = k
        if k < 1:
            warnings.warn("RSMOTE: a class with one member cannot be "
                          "oversampled; no synthetic rows for it", RuntimeWarning)
            return empty, info

        # Step 1 (p. 402; Alg. 1 lines 3-5): the k nearest neighbors of every
        # x_i in P "from the entire set D", and m_i, the majority ones.
        D = np.vstack([P, Q])
        is_majority = np.r_[np.zeros(n_p, dtype=bool), np.ones(n_q, dtype=bool)]
        dist, ind = _knn(D, P, k + 1)
        _, ind = _drop_self(dist, ind, np.arange(n_p))
        m_all = is_majority[ind].sum(axis=1)

        # Alg. 1 lines 6-9: m_i = k marks x_i as noise [29]; the others form
        # P'.  The noise is only kept out of the seeds (and of the
        # interpolation partners): it stays in the returned data (pp. 412, 416).
        noise = m_all == k
        seeds = np.flatnonzero(~noise)
        info["noise_pos"] = np.flatnonzero(noise)
        info["seed_pos"] = seeds
        m = m_all[seeds]
        info["m"] = m
        if seeds.size < 2:
            # CHOICE: (C12) interpolation needs two seeds; the paper does not cover
            # this case (the authors' code would raise an error).
            warnings.warn("RSMOTE: fewer than two non-noisy minority samples; "
                          "no synthetic rows for this class", RuntimeWarning)
            return empty, info

        # Alg. 1 line 10; Definitions 1-3 and Eq. (2), p. 401: relative density.
        # HONk(p): the k nearest neighbors of p in its own class D+, the
        # query point itself excluded.  CHOICE: (C6) D+ is the whole minority class
        # P of the training data, noisy samples included, as Definition 2
        # reads (the authors' code uses P' instead).
        d_hom, i_hom = _knn(P, P[seeds], k + 1)
        d_hom, _ = _drop_self(d_hom, i_hom, seeds)
        # HENk(p): the k nearest neighbors of p in the other class D- = Q.
        d_het, _ = _knn(Q, P[seeds], k)
        num, den = d_het.sum(axis=1), d_hom.sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            rd = num / den
        # CHOICE: (C7) Eq. (2) is undefined when all k homogeneous distances are 0
        # (k exact duplicates).  If the heterogeneous ones are not all 0, RD is
        # +inf (kept in info_) and enters the 2-means as the largest finite RD,
        # so these seeds join the safest cluster without moving its center;
        # if both sums are 0, RD is set to 1 (both densities infinite).  The
        # authors' code instead caps every RD at 100.
        rd[(den == 0) & (num == 0)] = 1.0
        info["relative_density"] = rd
        rd_for_clustering = rd.copy()
        infinite = np.isinf(rd_for_clustering)
        if infinite.any():
            finite = rd_for_clustering[~infinite]
            rd_for_clustering[infinite] = finite.max() if finite.size else 1.0

        # Step 2 (p. 402; Alg. 1 lines 13-14): 2-means on RD(P'); C_A is the
        # cluster with the larger center (safe), C_B the other (borderline).
        high = two_means_1d(rd_for_clustering)
        if high is None or high.sum() < 2 or (~high).sum() < 2:
            # CHOICE: (C9) a cluster with fewer than two seeds cannot interpolate
            # "within" itself; then P' is kept as one cluster (the authors'
            # code uses the same rule).  Also used when all RD are equal.
            groups = [np.arange(seeds.size)]
            info["cluster"] = np.zeros(seeds.size, dtype=int)
        else:
            groups = [np.flatnonzero(high), np.flatnonzero(~high)]
            info["cluster"] = np.where(high, 0, 1)
            info["split"] = True

        # Step 3 (p. 402; Alg. 1 lines 16-25).
        sizes = np.array([g.size for g in groups], dtype=float)
        n_cluster = _round_keep_sum(sizes / sizes.sum() * n_syn, n_syn)   # line 17
        n_per_seed = np.zeros(seeds.size, dtype=int)
        parts = []
        for g, n_j in zip(groups, n_cluster):
            w = (k - m[g]) / (k + 1.0)                                    # line 19
            w_bar = w / w.sum()                                           # line 20
            n_i = _round_keep_sum(w_bar * n_j, n_j)                       # line 21
            n_per_seed[g] = n_i
            # Line 22, Populate(N_i, i, nnarray) of SMOTE [11]: nnarray holds
            # the k nearest neighbors of x_i inside its own cluster P'_j.
            # CHOICE: (C11) a cluster with k or fewer seeds uses all its other seeds.
            Xg = P[seeds[g]]
            kk = min(k, g.size - 1)
            d_in, i_in = _knn(Xg, Xg, kk + 1)
            _, nnarray = _drop_self(d_in, i_in, np.arange(g.size))
            # CHOICE: (C16) one RandomState per call; per synthetic row a
            # uniform neighbor index and a uniform gap on [0, 1).
            base = np.repeat(np.arange(g.size), n_i)
            partner = nnarray[base, rng.randint(kk, size=base.size)]
            gap = rng.uniform(size=(base.size, 1))
            parts.append(Xg[base] + gap * (Xg[partner] - Xg[base]))
        info["n_per_seed"] = n_per_seed
        syn = np.vstack(parts) if parts else empty
        info["n_synthetic"] = syn.shape[0]
        return syn, info                                                  # line 26
