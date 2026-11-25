"""SMOM: k-NN-based synthetic minority oversampling for multiclass imbalance problems.

Re-implementation for the SMOTE25 rerun (WP6.8) of

    T. Zhu, Y. Lin, Y. Liu, "Synthetic minority oversampling technique for multiclass
    imbalance problems", Pattern Recognition 72 (2017) 327-340, doi:10.1016/j.patcog.2017.07.024,

and of its supplementary material ("Supp."). "p. NNN" cites the journal page, "Supp. p. N" the
page of the 26-page supplementary PDF. Written from the paper only: the WP6.8 brief lists SMOM
among the methods without a usable public implementation, and no author code was consulted.

What SMOM does (Sec. 3, pp. 329-334; Algorithm 1, p. 330)
==========================================================
Every class c with fewer instances than the largest class is oversampled, one class at a time,
against the whole data set D. A synthetic point of c is generated SMOTE-style from a seed x^i of c
and one of its k1 nearest neighbors x^j of c; because the random gap is drawn per feature (Eq. 1,
p. 328), it falls in the axis-parallel box spanned by x^i and x^j, not only on the segment.
SMOM changes how the neighbor (the "neighbor direction" x^i x^j) is chosen:

* Step 1 (p. 330): split D into S^c (class c) and S^~c (all other classes).
* Step 2 (p. 330): for each x^i in S^c find its k1 nearest neighbors in S^c (N^c_k1) and the
  distance r_k1 to the k1-th of them; the instances of other classes within r_k1 (set T); the
  first-filtration set Fs = T u N^c_k1 (Sec. 3.2.1, p. 333, Fig. 4a); and the k2 nearest
  neighbors N_k2 of x^i in the whole data (Step 2.3).
* Step 3 (p. 330) and Algorithm 2 NBDOS (p. 331, Definitions 1-2 and Lemma 1, pp. 330-331): a
  DBSCAN-like clustering of S^c. x^i is a "soft core" instance if at least a proportion rTh of its
  k2 nearest neighbors belong to c (Definition 1). Clusters are grown through the
  G^c_k-neighborhood H(x^i) = {x^i} u {class-c members of N_k2(x^i)} u {soft cores among the
  reverse k2-NN of x^i} (Definition 2); clusters with fewer than nTh members are dropped
  (Alg. 2, lines 21-25).
* Step 4 (p. 330): instances in a kept cluster are "outstanding" (Oi^c), the rest "trapped" (Ti^c).
* Step 5 (p. 330): for each trapped x^i and each neighbor x^j in N^c_k1(x^i), a selection weight
  sw(x^j):
    5.1  if x^j is outstanding and x^i is in N^c_k1(x^j): sw = 1 + w1/e (a "clean" direction);
    5.2  if x^i is in N^c_k1(x^j) and x^j.sw(x^i) has been computed: copy it;
    5.3  otherwise collect the instances in the PN neighborhood (the ball centered at the midpoint
         of x^i and x^j with radius d(x^i, x^j)/2, Fig. 2b, p. 332) by the second filtration
         Ss(x^j) = {x in Fs : d(x^i, x) <= d(x^i, x^j)} (p. 333, Fig. 4b) and dPN (Supp.
         Algorithm S1, Supp. p. 3), and apply Eq. (2), p. 332:

             sw = 1 / exp( r1*g_mi/g_c + r2*E_mi + w2*(r1*g_ma/g_c + r2*E_ma) )
                  + w1 * exp( -g_c / (g_ma + g_mi + g_c) )

         g_c, g_mi, g_ma: numbers of instances of class c, of the minority classes and of the
         majority classes (both without c) in the PN neighborhood; E_mi (E_ma): Shannon entropy of
         the minority (majority) class distribution in it divided by log|miC| (log|maC|), so that
         it lies in [0, 1] (p. 332). Minority (majority) classes are the classes smaller (larger)
         than the mean class size M/L (p. 334).
* Step 6 (p. 330; Sec. 3.2.2, pp. 333-334): if none of the k1 PN neighborhoods of a trapped x^i
  holds class-c instances only, x^i itself is added as a direction with weight 1 + w1/e (drawing it
  replicates x^i); the weights are normalized to a probability distribution.
* Step 7 (p. 330; Sec. 3.3, p. 334): the number zeta of synthetic instances of class c is spread
  over the members of S^c as evenly as possible.
* Step 8 (p. 330): for each x^i, x^i.g times: draw x^j (by the probabilities of Step 6 if x^i is
  trapped, uniformly from N^c_k1 if it is outstanding) and add x^i + (x^j - x^i) .* gamma, where
  gamma has one U[0, 1] number per feature (Eq. 1, p. 328).

Paper settings used as defaults
===============================
k1 = 12, k2 = 8, rTh = 5/8, nTh = 10, w1 = 0.2, w2 = 1/2, r1 = 1/3, r2 = 0.2 (p. 335; Supp. Sec. 3,
Supp. p. 3); "All classes are oversampled until they contain as many instances as the largest
one" (p. 335); "The standardized Euclidean distance is applied" (p. 335); when a class has fewer
than k1 + 1 instances, k is reset to its size minus one (p. 337).

Two-class data (the rerun's tasks)
==================================
The multiclass logic is kept. With two classes the larger class is the only majority class and
the smaller one the only minority class (p. 334), so in Eq. (2) g_mi = 0, E_mi = 0 (no minority
class other than c) and E_ma = 0 (one majority class: log|maC| = 0, see CHOICE below); the weight
becomes exp(-w2*r1*g_ma/g_c) + w1*exp(-g_c/(g_ma + g_c)).

Every point the paper leaves open is marked "CHOICE:" below and listed in NOTES.md.
"""

from collections import deque
import numbers

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator

__all__ = ["SMOM"]

# Largest distance block (rows x columns) computed at once; keeps memory near 32 MB.
_BLOCK = 4_000_000
# CHOICE: numerical guard of the ball test in dPN (Supp. Alg. S1, line 6, "dis_lm <= dis_ij/2").
# Points exactly on the sphere (e.g. duplicates of x^i of another class) belong to the ball; the
# tolerance keeps them there despite rounding of the midpoint.
_RTOL = 1e-9
_ATOL = 1e-12


def _k_smallest(D, k):
    """Column indices of the k smallest entries of each row of D, ordered by (distance, index).

    CHOICE: ties in distance are broken by the lower index, so the result does not depend on the
    order in which numpy's partition returns tied entries.
    """
    m, n = D.shape
    if k <= 0:
        return np.empty((m, 0), dtype=np.intp)
    if k >= n:
        return np.argsort(D, axis=1, kind="stable")[:, :k]
    part = np.argpartition(D, k - 1, axis=1)[:, :k]
    pd = np.take_along_axis(D, part, axis=1)
    kth = pd.max(axis=1)
    order = np.lexsort((part, pd), axis=-1)
    out = np.take_along_axis(part, order, axis=1)
    n_le = (D <= kth[:, None]).sum(axis=1)
    for r in np.flatnonzero(n_le > k):  # a tie at the k-th distance: rebuild this row exactly
        sel = np.flatnonzero(D[r] <= kth[r])
        out[r] = sel[np.lexsort((sel, D[r, sel]))][:k]
    return out


def _normalized_entropy(C):
    """Rows of class counts -> Shannon entropy / log(number of classes) (p. 332).

    CHOICE: the paper prints E_mi = (sum p log p) / Z_mi without a minus sign; as printed the value
    would lie in [-1, 0], while the text says E_mi ranges from 0 to 1 and grows with the number and
    the evenness of the minority classes (pp. 332-333, observations 2-3). The usual entropy
    -sum p log p is used.
    CHOICE: a group with fewer than two classes (Z = log 1 = 0) or without any instance in the
    neighborhood has entropy 0.
    """
    q, m = C.shape
    if m <= 1:
        return np.zeros(q)
    tot = C.sum(axis=1, keepdims=True)
    p = np.divide(C, tot, out=np.zeros_like(C, dtype=float), where=tot > 0)
    plogp = np.zeros_like(p)
    np.log(p, out=plogp, where=p > 0)
    plogp *= p
    return -plogp.sum(axis=1) / np.log(m)


class SMOM(BaseEstimator):
    """SMOM oversampler (Zhu, Lin and Liu, Pattern Recognition 72 (2017) 327-340).

    Parameters (defaults: p. 335 and Supp. Sec. 3, Supp. p. 3)
    ==========
    k1 : int, default 12
        Number of nearest same-class neighbors used to generate synthetic instances (Alg. 1).
    k2 : int, default 8
        Number of nearest neighbors (all classes) used by NBDOS (Alg. 1 Step 2.3, Alg. 2).
    rTh : float, default 5/8
        Minimal proportion of class-c instances among the k2 neighbors of a soft core instance
        (Definition 1, p. 330).
    nTh : int, default 10
        Minimal size of a cluster of outstanding instances (Alg. 2, lines 21-25).
    w1, w2, r1, r2 : float, defaults 0.2, 1/2, 1/3, 0.2
        Weights of Eq. (2), p. 332.
    sampling_strategy : "auto" or dict, default "auto"
        "auto": every class smaller than the largest class is oversampled to the size of the
        largest class (p. 335). A dict maps class labels to the wanted number of instances after
        resampling (an imbalanced-learn convention, not in the paper).
    metric : "seuclidean" or "euclidean", default "seuclidean"
        "seuclidean": the standardized Euclidean distance of the paper (p. 335), i.e. Euclidean
        distance after dividing every feature by its standard deviation over the X passed to
        fit_resample. "euclidean": plain Euclidean distance on X as given. Synthetic points are
        always built in the original feature space (Eq. 1 commutes with per-feature scaling).
    soft_core_rule : "proportion" or "round", default "proportion"
        "proportion": Definition 1 (p. 330), soft core if |Tem|/k2 >= rTh. "round": the literal
        line 5 of Algorithm 2 (p. 331), round(|Tem|/k2) >= rTh with round half up; kept only to
        test that reading (see NOTES.md).
    random_state : None, int or numpy Generator
        Seed of the random draws (extra allocation in Step 7, directions and gaps in Step 8).

    Attributes after fit_resample
    =============================
    sampling_strategy_ : dict, class label -> number of synthetic rows generated.
    class_info_ : dict, class label -> diagnostics (k1 and k2 used, numbers of outstanding and
        trapped instances, clusters, trapped instances that received their own direction).
    outstanding_ : dict, class label -> boolean mask over that class's rows (in input order).
    """

    def __init__(self, k1=12, k2=8, rTh=5 / 8, nTh=10, w1=0.2, w2=0.5, r1=1 / 3, r2=0.2,
                 sampling_strategy="auto", metric="seuclidean", soft_core_rule="proportion",
                 random_state=None):
        self.k1 = k1
        self.k2 = k2
        self.rTh = rTh
        self.nTh = nTh
        self.w1 = w1
        self.w2 = w2
        self.r1 = r1
        self.r2 = r2
        self.sampling_strategy = sampling_strategy
        self.metric = metric
        self.soft_core_rule = soft_core_rule
        self.random_state = random_state

    # ================================================================== public API
    def fit_resample(self, X, y):
        """Return (X_res, y_res): the original rows first, then the synthetic rows of each
        oversampled class (classes in ascending label order)."""
        X, y = self._check_input(X, y)
        self._check_params()
        rng = self._rng()
        n, d = X.shape
        classes, counts = np.unique(y, return_counts=True)
        zeta = self._n_synthetic(classes, counts)

        # Minority / majority classes (p. 334): "we simply classify the classes whose instances
        # size greater (/smaller) than M/L as the majority (/minority) classes".
        # CHOICE: a class whose size equals M/L exactly is counted as a majority class.
        mean_size = n / classes.size
        is_minority = counts < mean_size

        Z = self._metric_space(X)
        y_idx = np.searchsorted(classes, y)  # class column of every row

        self.sampling_strategy_ = {}
        self.class_info_ = {}
        self.outstanding_ = {}
        X_parts, y_parts = [X], [y]
        # CHOICE: every class is oversampled from the original data D (synthetic instances of
        # other classes are not added to D), so the result does not depend on the class order.
        for ci, c in enumerate(classes):
            z = int(zeta.get(c, 0))
            if z <= 0:
                continue
            S = self._oversample_class(X, Z, y_idx, ci, z, is_minority, rng, c)
            X_parts.append(S)
            y_parts.append(np.full(S.shape[0], c, dtype=y.dtype))
            self.sampling_strategy_[c] = int(S.shape[0])
        return np.vstack(X_parts), np.concatenate(y_parts)

    # ================================================================== checks
    @staticmethod
    def _check_input(X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if X.ndim != 2:
            raise ValueError("X must be a 2-D array")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError("y must be 1-D with one label per row of X")
        if not np.all(np.isfinite(X)):
            raise ValueError("X contains NaN or infinite values")
        return X, y

    def _check_params(self):
        for name in ("k1", "k2", "nTh"):
            v = getattr(self, name)
            if not isinstance(v, numbers.Integral) or v < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.metric not in ("seuclidean", "euclidean"):
            raise ValueError("metric must be 'seuclidean' or 'euclidean'")
        if self.soft_core_rule not in ("proportion", "round"):
            raise ValueError("soft_core_rule must be 'proportion' or 'round'")

    def _rng(self):
        rs = self.random_state
        if isinstance(rs, np.random.Generator):
            return rs
        if isinstance(rs, np.random.RandomState):
            return np.random.default_rng(rs.randint(np.iinfo(np.int32).max))
        return np.random.default_rng(rs)

    def _n_synthetic(self, classes, counts):
        """zeta per class. 'auto': up to the size of the largest class (p. 335)."""
        if isinstance(self.sampling_strategy, str):
            if self.sampling_strategy != "auto":
                raise ValueError("sampling_strategy must be 'auto' or a dict")
            top = counts.max()
            return {c: int(top - m) for c, m in zip(classes, counts) if m < top}
        if isinstance(self.sampling_strategy, dict):
            size = dict(zip(classes.tolist(), counts.tolist()))
            out = {}
            for c, target in self.sampling_strategy.items():
                if c not in size:
                    raise ValueError(f"class {c!r} of sampling_strategy is not in y")
                if target < size[c]:
                    raise ValueError(f"target {target} of class {c!r} is below its size")
                out[classes[classes.tolist().index(c)]] = int(target - size[c])
            return out
        raise ValueError("sampling_strategy must be 'auto' or a dict")

    def _metric_space(self, X):
        """Coordinates in which Euclidean distance is the paper's standardized Euclidean distance
        (p. 335). CHOICE: standard deviations with ddof=1 over all rows of X (the training data);
        a constant feature keeps scale 1."""
        if self.metric == "euclidean" or X.shape[0] < 2:
            return X
        s = X.std(axis=0, ddof=1)
        s[~(s > 0)] = 1.0
        return X / s

    # ================================================================== Algorithm 1
    def _oversample_class(self, X, Z, y_idx, ci, zeta, is_minority, rng, label):
        n, d = X.shape
        idx_c = np.flatnonzero(y_idx == ci)  # Step 1: S^c
        n_c = idx_c.size
        info = {"n": int(n_c), "n_synthetic": int(zeta)}
        if n_c == 1:
            # CHOICE: a class with one instance has no neighbor direction; its only possible
            # direction is itself (Step 6.1), so it is replicated.
            info.update(k1=0, k2=0, n_outstanding=0, n_trapped=1, n_clusters=0, n_self_direction=1)
            self.class_info_[label] = info
            self.outstanding_[label] = np.zeros(1, dtype=bool)
            return np.repeat(X[idx_c], zeta, axis=0)

        # "If the considered class has less than 12 instances, k is reset to the number of
        # instances of this class minus one" (p. 337).
        # CHOICE: the paper states this rule in Experiment 2 "for all compared algorithms"; it is
        # applied in every run here. k2 is likewise capped at n - 1 for tiny data sets.
        k1 = min(self.k1, n_c - 1)
        k2 = min(self.k2, n - 1)

        # Step 2: neighbor search.
        nn1, nn1_d, nn2 = self._neighbors(Z, idx_c, k1, k2)
        r_k1 = nn1_d[:, -1]  # Step 2.1: distance to the k1-th nearest instance of class c

        # Steps 3-4: NBDOS, outstanding (cl != 0) and trapped (cl == 0) instances.
        cl, n_clusters = self._nbdos(y_idx, idx_c, nn2, ci, k2)
        outstanding = cl != 0

        # Steps 5-6: selection probabilities of the neighbor directions of trapped instances.
        cand, prob, n_self = self._direction_probabilities(
            Z, y_idx, idx_c, nn1, r_k1, outstanding, ci, is_minority)

        # Step 7: allocate zeta to the members of S^c "as evenly as possible".
        g = np.full(n_c, zeta // n_c, dtype=np.intp)
        rem = zeta % n_c
        if rem:
            # CHOICE: the zeta mod |S^c| extra instances go to a random subset of S^c.
            g[rng.choice(n_c, size=rem, replace=False)] += 1

        # Step 8: draw the assistant reference instance x^j and interpolate (Eq. 1).
        # CHOICE: "repeat 1) and 2) x^i.g times" is read as x^i.g independent draws, i.e. with
        # replacement (the same direction can be drawn several times).
        owners = np.repeat(idx_c, g)
        partners = np.empty(owners.size, dtype=np.intp)
        start = 0
        for i in np.flatnonzero(g):
            stop = start + g[i]
            if outstanding[i]:
                # Step 8.1, outstanding: x^j drawn uniformly from N^c_k1 (with replacement).
                partners[start:stop] = idx_c[nn1[i, rng.integers(0, k1, size=g[i])]]
            else:
                # Step 8.1, trapped: weighted draw by x^i.P (with replacement).
                partners[start:stop] = rng.choice(cand[i], size=g[i], p=prob[i])
            start = stop
        gamma = rng.random((owners.size, d))  # Eq. (1): one U[0, 1] number per feature
        S = X[owners] + (X[partners] - X[owners]) * gamma

        info.update(k1=int(k1), k2=int(k2), n_outstanding=int(outstanding.sum()),
                    n_trapped=int((~outstanding).sum()), n_clusters=int(n_clusters),
                    n_self_direction=int(n_self))
        self.class_info_[label] = info
        self.outstanding_[label] = outstanding
        return S

    # ================================================================== Step 2
    @staticmethod
    def _neighbors(Z, idx_c, k1, k2):
        """Step 2 (p. 330). Returns
        nn1   (n_c, k1): positions in idx_c of the k1 nearest class-c instances (Step 2.1),
        nn1_d (n_c, k1): their distances,
        nn2   (n_c, k2): row indices of the k2 nearest instances of the whole data (Step 2.3).

        N_k2 is searched over all of D; this equals the paper's search in the union of the k3
        nearest class-c and the k3 nearest other-class instances because k3 = max(k1, k2) >= k2.
        CHOICE: a point is not its own neighbor (excluded by index); duplicates of it are.
        """
        n = Z.shape[0]
        n_c = idx_c.size
        nn1 = np.empty((n_c, k1), dtype=np.intp)
        nn1_d = np.empty((n_c, k1))
        nn2 = np.empty((n_c, k2), dtype=np.intp)
        step = max(1, _BLOCK // max(n, 1))
        for s in range(0, n_c, step):
            rows = np.arange(s, min(s + step, n_c))
            D = cdist(Z[idx_c[rows]], Z)
            D[np.arange(rows.size), idx_c[rows]] = np.inf
            nn2[rows] = _k_smallest(D, k2)
            Dc = D[:, idx_c]
            loc = _k_smallest(Dc, k1)
            nn1[rows] = loc
            nn1_d[rows] = np.take_along_axis(Dc, loc, axis=1)
        return nn1, nn1_d, nn2

    # ================================================================== Algorithm 2
    def _nbdos(self, y_idx, idx_c, nn2, ci, k):
        """NBDOS (Algorithm 2, p. 331). Returns cluster labels over S^c (0 = trapped) and the
        number of clusters kept."""
        n_c = idx_c.size
        pos = np.full(y_idx.size, -1, dtype=np.intp)
        pos[idx_c] = np.arange(n_c)
        same = y_idx[nn2] == ci
        tem = [pos[nn2[i, same[i]]] for i in range(n_c)]  # line 4: class-c members of N_k
        frac = same.sum(axis=1) / k
        # CHOICE: Definition 1 (p. 330) says "proportion ... not less than rTh"; Alg. 2 line 5 prints
        # round(|Tem|/k) >= rTh, which with rounding to an integer would make every rTh in (0, 1/2]
        # and in (1/2, 1] act alike and contradict the role of rTh in Supp. Sec. 3 (Supp. p. 5).
        # Default: Definition 1 (with a 1e-12 guard for the float comparison); "round" is kept
        # as an option to test the literal reading.
        if self.soft_core_rule == "proportion":
            soft = frac >= self.rTh - 1e-12
        else:
            soft = np.floor(frac + 0.5) >= self.rTh  # literal Alg. 2 line 5, round half up
        H = [set(tem[i].tolist()) if soft[i] else None for i in range(n_c)]  # line 7
        for m in np.flatnonzero(soft):  # lines 10-13: soft cores among the reverse k-NN
            for i in tem[m]:
                if soft[i]:
                    H[i].add(int(m))
        cl = np.zeros(n_c, dtype=np.intp)
        cur = 0
        # CHOICE: soft cores are visited in input order and expandCluster draws from sfC first in,
        # first out; the order only decides which cluster claims a non-core instance two
        # clusters reach.
        for i in np.flatnonzero(soft):  # lines 14-20
            if cl[i]:
                continue
            cur += 1
            cl[i] = cur  # line 28
            queue = deque([int(i)])
            while queue:  # lines 29-39 (expandCluster)
                j = queue.popleft()
                for l in sorted(H[j]):
                    if cl[l] == 0:
                        cl[l] = cur
                        if soft[l]:
                            queue.append(l)
        kept = 0
        for cid in range(1, cur + 1):  # lines 21-25: drop clusters smaller than nTh
            members = cl == cid
            if members.sum() < self.nTh:
                cl[members] = 0
            else:
                kept += 1
        return cl, kept

    # ================================================================== Steps 5-6
    def _direction_probabilities(self, Z, y_idx, idx_c, nn1, r_k1, outstanding, ci, is_minority):
        """Steps 5-6 (p. 330; Secs. 3.2.1-3.2.2, pp. 332-334) for the trapped instances.

        Returns cand[i] (row indices of the directions of trapped x^i, possibly x^i itself),
        prob[i] (their selection probabilities) and the number of trapped instances that got their
        own direction (Step 6.1).
        CHOICE: trapped instances are processed in input order. The order only decides whether
        Step 5.2 copies a weight or Step 5.3 computes it; both give the same PN neighborhood (the
        ball lies within distance d(x^i, x^j) <= r_k1 of both points), except when ties at
        exactly r_k1 leave a duplicate point out of a k1 list.
        """
        n_c, k1 = nn1.shape
        n_classes = int(y_idx.max()) + 1
        mi_cols = [j for j in range(n_classes) if j != ci and is_minority[j]]
        ma_cols = [j for j in range(n_classes) if j != ci and not is_minority[j]]
        w_clean = 1.0 + self.w1 / np.e  # Eq. (2) for a PN neighborhood holding class c only
        nn1_sets = [set(row.tolist()) for row in nn1]
        other = y_idx != ci
        computed = {}  # (i, j) -> (x^i.sw(x^j), clean flag), positions in idx_c
        cand, prob = {}, {}
        n_self = 0
        trapped = np.flatnonzero(~outstanding)
        step = max(1, _BLOCK // max(Z.shape[0], 1))
        for s in range(0, trapped.size, step):
            rows = trapped[s:s + step]
            D = cdist(Z[idx_c[rows]], Z)
            for r, i in enumerate(rows):
                sw = np.empty(k1)
                clean = np.zeros(k1, dtype=bool)
                todo = []
                for t, j in enumerate(nn1[i]):
                    i_in_j = i in nn1_sets[j]
                    if outstanding[j] and i_in_j:  # Step 5.1
                        sw[t], clean[t] = w_clean, True
                    elif i_in_j and (j, i) in computed:  # Step 5.2
                        sw[t], clean[t] = computed[(j, i)]
                    else:  # Step 5.3
                        todo.append(t)
                if todo:
                    todo = np.asarray(todo)
                    v, f = self._pn_weights(Z, y_idx, D[r], idx_c[i], idx_c[nn1[i, todo]],
                                            r_k1[i], idx_c[nn1[i]], other, ci, mi_cols,
                                            ma_cols, n_classes)
                    sw[todo], clean[todo] = v, f
                for t, j in enumerate(nn1[i]):
                    computed[(int(i), int(j))] = (sw[t], clean[t])
                dirs = idx_c[nn1[i]]
                if not clean.any():  # Step 6.1: no clean PN neighborhood -> add x^i itself
                    dirs = np.append(dirs, idx_c[i])
                    sw = np.append(sw, w_clean)
                    n_self += 1
                cand[i] = dirs
                prob[i] = sw / sw.sum()  # Step 6.2
        return cand, prob, n_self

    def _pn_weights(self, Z, y_idx, d_row, gi, gj, r_k1_i, nn1_rows, other, ci, mi_cols, ma_cols,
                    n_classes):
        """Step 5.3 for the directions x^i -> gj (row indices): two-round filtration (p. 333),
        dPN (Supp. Alg. S1, Supp. p. 3) and Eq. (2) (p. 332). d_row: distances from x^i to all
        rows. Returns the selection weights and the "clean" flags (no instance of another class
        in the PN neighborhood)."""
        # First filtration (Steps 2.1-2.2): Fs = T u N^c_k1.
        # CHOICE: T holds every other-class instance within r_k1, not only those among the k3
        # nearest other-class instances: Step 2.2 says T is chosen "during this process" of the k3
        # search, but Sec. 3.2.1 (p. 333, Fig. 4a) says the first filtration keeps all instances
        # within r_k1 and only excludes instances that cannot lie in a PN neighborhood.
        T = np.flatnonzero(other & (d_row <= r_k1_i))
        Fs = np.concatenate([T, nn1_rows])
        dF = d_row[Fs]
        dJ = d_row[gj]
        # Second filtration (Step 5.3): Ss(x^j) = {x in Fs : d(x^i, x) <= d(x^i, x^j)}.
        in_ss = dF[None, :] <= dJ[:, None]
        # dPN: N_PN = {x^i, x^j} u {x in Ss(x^j) : d(x, mid_ij) <= dis_ij / 2}.
        mid = 0.5 * (Z[gi][None, :] + Z[gj])
        dm = cdist(mid, Z[Fs])
        in_pn = in_ss & (dm <= 0.5 * dJ[:, None] * (1.0 + _RTOL) + _ATOL)
        in_pn &= Fs[None, :] != gj[:, None]  # x^j is already in the initial set {x^i, x^j}
        onehot = np.zeros((Fs.size, n_classes))
        onehot[np.arange(Fs.size), y_idx[Fs]] = 1.0
        counts = in_pn.astype(float) @ onehot
        counts[:, ci] += 2.0  # x^i and x^j (Supp. Alg. S1, line 1)
        return self._eq2(counts, ci, mi_cols, ma_cols)

    def _eq2(self, counts, ci, mi_cols, ma_cols):
        """Selection weight of Eq. (2), p. 332, from the class counts of PN neighborhoods
        (one row per neighborhood, one column per class)."""
        g_c = counts[:, ci]
        g_mi = counts[:, mi_cols].sum(axis=1) if mi_cols else np.zeros(counts.shape[0])
        g_ma = counts[:, ma_cols].sum(axis=1) if ma_cols else np.zeros(counts.shape[0])
        E_mi = _normalized_entropy(counts[:, mi_cols]) if mi_cols else np.zeros(counts.shape[0])
        E_ma = _normalized_entropy(counts[:, ma_cols]) if ma_cols else np.zeros(counts.shape[0])
        over = self.r1 * g_mi / g_c + self.r2 * E_mi + self.w2 * (self.r1 * g_ma / g_c + self.r2 * E_ma)
        sw = np.exp(-over) + self.w1 * np.exp(-g_c / (g_ma + g_mi + g_c))
        return sw, (g_mi + g_ma) == 0
