"""CGMOS: Certainty Guided Minority OverSampling (re-implementation for the SMOTE25 rerun, WP6.8).

Paper (the authority for every step below):
    X. Zhang, D. Ma, L. Gan, S. Jiang and G. Agam. CGMOS: Certainty Guided Minority
    OverSampling. Proceedings of CIKM 2016, pages 1623-1631. doi:10.1145/2983323.2983789
Page numbers are the proceedings pages printed on the PDF (p. 1623 is the first page).

This file was written from the paper alone; no author code was found (none is linked from
the paper, arXiv 1607.06525 or Papers with Code). Every point the paper leaves open is marked
"CHOICE:" in the code and listed in NOTES.md.

Algorithm (two classes; the paper treats "the binary classification problem", Sec. 2, p. 1624)
================================================================================================
Notation: D = {(x_j, y_j)}, j = 1..n, labels l_mnr (minority) and l_mjr (majority).

Step 0  Labels and amount. l_mnr is the class with fewer samples. The number of synthetic
        samples is k_delta * delta with delta = n_mjr - n_mnr (Sec. 4.5, p. 1627: "we
        synthesized k delta new samples ... k gradually increased from 0.5 to 5"); the default
        k_delta = 1 balances the classes, as SMOTE does ("To balance the dataset", p. 1624).
Step 1  Bandwidths, Eq. 4 (p. 1624): h_k = sigma * (1/q) * sum_{x in N(x_k)} ||x - x_k||, the
        scaled average Euclidean distance from x_k to its q nearest neighbors.
Step 2  Class-conditional kernel density, Eq. 3 (p. 1624):
            P(x_j | l) = sum_k K((x_j - x_k) / h_k) I(y_k = l) / sum_k I(y_k = l).
        K is a Gaussian kernel, K(u) = exp(-||u||^2 / 2) (its constant cancels below).
Step 3  Bayes posterior (p. 1624, P(l | x_j) = P(x_j | l) P(l) / P(x_j)) and certainty,
        Definition 1, Eqs. 1-2 (p. 1624): C(y_j | x_j) = P(y_j | x_j). With the class priors
        P(l) = n_l / n the counts cancel and, writing S_l(j) = sum_{k: y_k = l} K_jk,
        K_jk = K((x_j - x_k) / h_k) and S(j) = S_mnr(j) + S_mjr(j):
            C(y_j | x_j) = S_{y_j}(j) / S(j).
Step 4  Relative certainty change, Definition 2, Eq. 5 (p. 1625), of adding one minority
        example at the location x_i (Sec. 2.3, p. 1625: "we suppose that a new sample will be
        added to the same location as x_i"): R_{+i}(y_j | x_j) = (C_{+i} - C) / C. The added
        copy carries x_i's kernel, so its contribution at x_j is K_ji (column i of the kernel
        matrix) and the minority count grows by one (priors recomputed). This gives
            minority j:  R_{+i} = K_ji S_mjr(j) / (S_mnr(j) (S(j) + K_ji))   (>= 0)
            majority j:  R_{+i} = -K_ji / (S(j) + K_ji)                       (in (-1, 0])
Step 5  Weight, Eq. 6 (p. 1625): W(x_i) = 1 + (1/n) sum_{j=1..n} R_{+i}(y_j | x_j), the
        average over all n samples of both classes; W(x_i) > 0 (p. 1625).
Step 6  Seed selection (p. 1625): z = sum_i W(x_i); seeds are drawn at random with probability
        W(x_i) / z. The weights are computed once, on the original data (CGMOS "can achieve
        data oversampling in a single step", Sec. 1.2, p. 1624).
Step 7  Interpolation (p. 1625: "The interpolation phase of CGMOS is the same as SMOTE[4]";
        p. 1624: "a linear interpolation between the seed sample and one of its neighbors"):
        x_new = x_seed + gap * (x_nn - x_seed), x_nn one of the seed's k nearest minority
        neighbors chosen uniformly, gap ~ U(0, 1).
Step 8  Output: the original rows first, then the synthetic rows labeled l_mnr.

The paper's Theorem 1 (p. 1626) is a property of Steps 5-6 and needs no code.

Note for users: because of the "1 +" and the 1/n in Eq. 6, W(x_i) - 1 is of order 1/n, so the
seed probabilities W(x_i) / z are within a fraction of a percent of SMOTE's uniform ones on
typical data (Haberman: total-variation distance 0.0007). See NOTES.md, section 1.
"""

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.neighbors import NearestNeighbors
from sklearn.utils import check_random_state

__all__ = ["CGMOS", "kde_bandwidths", "log_kernel_block", "cgmos_weights"]

# Entries (rows x n) of one kernel block; 4e6 float64 entries are about 32 MB per array.
_BLOCK_ENTRIES = 4_000_000


def _sq_dists(A, B, A_sq=None, B_sq=None):
    """Squared Euclidean distances between the rows of A and the rows of B (clipped at 0)."""
    if A_sq is None:
        A_sq = np.einsum("ij,ij->i", A, A)
    if B_sq is None:
        B_sq = np.einsum("ij,ij->i", B, B)
    D2 = A_sq[:, None] + B_sq[None, :] - 2.0 * (A @ B.T)
    np.maximum(D2, 0.0, out=D2)
    return D2


def kde_bandwidths(X, y, q=5, sigma=1.0, neighbors="class"):
    """Per-sample bandwidths of Eq. 4 (p. 1624): h_k = sigma * mean distance to q nearest neighbors.

    neighbors="class": N(x_k) is taken among the samples of x_k's own class.
    neighbors="all":   N(x_k) is taken among all samples of D.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n = X.shape[0]
    h = np.full(n, np.nan)
    # CHOICE: the paper does not say from which set the q nearest neighbors of Eq. 4 come.
    # Default "class": each kernel belongs to the density of its own class (Eq. 3), so its
    # width follows the spacing of that class (adaptive class-conditional KDE).
    if neighbors == "class":
        groups = [np.flatnonzero(y == c) for c in np.unique(y)]
    elif neighbors == "all":
        groups = [np.arange(n)]
    else:
        raise ValueError("neighbors must be 'class' or 'all'")
    for idx in groups:
        if idx.size < 2:
            continue  # filled below
        # CHOICE: q is clipped to (group size - 1) for very small classes.
        qq = min(int(q), idx.size - 1)
        nn = NearestNeighbors(n_neighbors=qq).fit(X[idx])
        dist, _ = nn.kneighbors()  # without X: a point is not its own neighbor
        hg = sigma * dist.mean(axis=1)
        pos = hg > 0
        # CHOICE: a zero bandwidth (q or more exact duplicates of x_k) would make the kernel a
        # point mass; it is replaced by the smallest positive bandwidth of the same group.
        if pos.any() and not pos.all():
            hg[~pos] = hg[pos].min()
        h[idx] = hg
    ok = np.isfinite(h) & (h > 0)
    if not ok.all():
        # CHOICE: a class with a single sample (or only duplicates) gets the median positive
        # bandwidth of all other samples (sigma if there is none).
        h[~ok] = np.median(h[ok]) if ok.any() else float(sigma)
    return h


def log_kernel_block(D2, h, normalize_kernel=False, m=None):
    """log K((x_j - x_k) / h_k) for squared distances D2 (rows j, columns k), Gaussian K.

    With normalize_kernel=True each kernel is divided by h_k^m (a standard KDE); the paper's
    Eq. 3 prints K((x_j - x_k) / h_k) without that factor, which is the default here.
    """
    # CHOICE: the paper names no kernel ("zero mean and integrates to one", p. 1624); a Gaussian
    # with h_k as its standard deviation is used. Its constant (2 pi)^(-m/2) cancels in every ratio.
    # CHOICE: Eq. 3 is followed as printed (no 1/h_k^m) unless normalize_kernel=True.
    L = D2 * (-0.5 / h**2)[None, :]
    if normalize_kernel:
        L += (-float(m) * np.log(h))[None, :]
    return L


def cgmos_weights(X, is_min, h, normalize_kernel=False, candidates=None):
    """Certainties (Eqs. 1-3) and weights W(x_i) (Eqs. 5-6) for the candidate seeds.

    Parameters
    ==========
    X : (n, m) float array.
    is_min : (n,) bool array, True for the minority class.
    h : (n,) bandwidths from Eq. 4.
    candidates : indices i for which W(x_i) is computed (default: the minority samples).

    Returns
    =======
    W : (len(candidates),) array, W(x_i) = 1 + (1/n) sum_j R_{+i}(y_j | x_j)   (Eq. 6).
    certainty : (n,) array, C(y_j | x_j) before any addition                    (Eqs. 1-2).
    """
    X = np.asarray(X, dtype=float)
    is_min = np.asarray(is_min, dtype=bool)
    n, m = X.shape
    if candidates is None:
        candidates = np.flatnonzero(is_min)
    candidates = np.asarray(candidates)
    sq = np.einsum("ij,ij->i", X, X)
    rows_per_block = max(1, _BLOCK_ENTRIES // max(n, 1))
    R_sum = np.zeros(candidates.size)
    certainty = np.empty(n)
    tiny = np.finfo(float).tiny
    for start in range(0, n, rows_per_block):
        r = np.arange(start, min(n, start + rows_per_block))
        D2 = _sq_dists(X[r], X, sq[r], sq)
        D2[np.arange(r.size), r] = 0.0  # exact zero self-distance
        L = log_kernel_block(D2, h, normalize_kernel, m)
        if normalize_kernel:
            # Rescaling a row by a constant leaves every ratio below unchanged and avoids
            # overflow of h^-m in high dimension.
            L -= L.max(axis=1, keepdims=True)
        K = np.exp(L)
        # CHOICE: Eq. 3 as printed sums over all k = 1..n, so x_j's own kernel is part of its
        # density (a leave-one-out reading is possible; it keeps the weights as uniform, NOTES.md).
        s_min = K[:, is_min].sum(axis=1)
        s_maj = K[:, ~is_min].sum(axis=1)
        s_all = s_min + s_maj
        row_min = is_min[r]
        own = np.maximum(np.where(row_min, s_min, s_maj), tiny)
        other = np.where(row_min, s_maj, s_min)
        # Eqs. 1-2 with Bayes' rule (p. 1624).
        # CHOICE: priors P(l) = n_l / n (not stated), so P(x_j | l) P(l) = S_l(j) / n.
        certainty[r] = own / s_all
        # Eq. 5 for a minority copy added at x_i (Step 4 of the module docstring).
        # CHOICE: the copy carries x_i's bandwidth h_i (its kernel at x_j is K_ji, column i), the
        # other bandwidths are not recomputed, and the priors are recomputed with n_mnr + 1, n + 1.
        Kc = K[:, candidates]
        R = Kc / (s_all[:, None] + Kc)
        R *= np.where(row_min, other / own, -1.0)[:, None]
        R_sum += R.sum(axis=0)
    # Eq. 6: average over all n samples of D (both classes).
    W = 1.0 + R_sum / n
    return W, certainty


class CGMOS(BaseEstimator):
    """Certainty Guided Minority OverSampling (Zhang et al., CIKM 2016, pp. 1623-1631).

    Seeds are minority samples drawn with probability W(x_i) / z, where W(x_i) (Eq. 6, p. 1625)
    is one plus the average relative change (Eq. 5, p. 1625) in the kernel-density Bayes
    posterior certainty (Eqs. 1-4, p. 1624) of all n training samples when one minority example
    is added at x_i; synthetic samples are then made by SMOTE interpolation (p. 1625). See the
    module docstring for the step-by-step mapping to the paper.

    Parameters
    ==========
    sigma : float, default=1.0
        Scale factor sigma > 0 of the bandwidth, Eq. 4 (p. 1624).
        CHOICE: the paper gives no value (arXiv 1607.06525 promises one "in Section 4" but
        does not give it); 1.0 makes h_k the plain mean distance to the q nearest neighbors.
    q : int, default=5
        Number of nearest neighbors in the bandwidth, Eq. 4 (p. 1624).
        CHOICE: no value in the paper; 5 matches SMOTE's neighborhood size.
    k_neighbors : int, default=5
        Nearest minority neighbors used for interpolation (SMOTE, p. 1625).
        CHOICE: the paper says the interpolation is "the same as SMOTE[4]" and gives no k;
        k = 5 is the value of the SMOTE paper.
    k_delta : float, default=1.0
        Number of synthetic samples = round(k_delta * (n_mjr - n_mnr)), the "k delta" of
        Sec. 4.5 (p. 1627). CHOICE: the main experiments' amount is not stated; 1.0 balances.
    bandwidth_neighbors : {"class", "all"}, default="class"
        Set from which the q neighbors of Eq. 4 are taken. CHOICE (see kde_bandwidths).
    normalize_kernel : bool, default=False
        False follows Eq. 3 as printed (K((x_j - x_k)/h_k), no 1/h_k^m factor);
        True uses the standard KDE normalization 1/h_k^m. CHOICE (see NOTES.md).
    random_state : None, int or numpy.random.RandomState, default=None
        Controls seed draws, neighbor choice and interpolation gaps.

    Attributes (after fit_resample)
    ===============================
    minority_label_, majority_label_ : the two class labels.
    n_synthetic_ : number of synthetic rows appended.
    bandwidths_ : (n,) bandwidths h_k (Eq. 4).
    certainty_ : (n,) certainties C(y_j | x_j) before oversampling (Eqs. 1-2).
    minority_indices_ : indices (into X) of the minority samples, i.e. the candidate seeds.
    weights_ : W(x_i) for the minority samples, same order as minority_indices_ (Eq. 6).
    seed_proba_ : W(x_i) / z (p. 1625).
    seed_indices_, partner_indices_ : indices (into X) of the seed and of the interpolation
        partner of every synthetic row.
    """

    def __init__(
        self,
        sigma=1.0,
        q=5,
        k_neighbors=5,
        k_delta=1.0,
        bandwidth_neighbors="class",
        normalize_kernel=False,
        random_state=None,
    ):
        self.sigma = sigma
        self.q = q
        self.k_neighbors = k_neighbors
        self.k_delta = k_delta
        self.bandwidth_neighbors = bandwidth_neighbors
        self.normalize_kernel = normalize_kernel
        self.random_state = random_state

    def _seed_weights(self, X, y, is_min):
        """Steps 1-5: W(x_i) of Eq. 6 for the minority samples (in the order of minority_indices_).

        Sets bandwidths_ and certainty_. (validate_cgmos.py overrides this method to build a
        uniform-seed ablation, i.e. SMOTE drawn from the same random stream.)
        """
        h = kde_bandwidths(X, y, self.q, self.sigma, self.bandwidth_neighbors)
        # CHOICE: the candidate seeds are the minority samples. The paper assigns a weight to
        # "each sample (x_i, y_i) in D" (p. 1625), but its interpolation is SMOTE's, which
        # interpolates between a minority seed and its minority neighbors.
        W, certainty = cgmos_weights(
            X, is_min, h, self.normalize_kernel, candidates=np.flatnonzero(is_min)
        )
        self.bandwidths_, self.certainty_ = h, certainty
        return W

    def fit_resample(self, X, y):
        """Return (X_res, y_res): the original rows first, then the synthetic minority rows."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if X.ndim != 2 or y.ndim != 1 or X.shape[0] != y.shape[0]:
            raise ValueError("X must be 2-D and y 1-D with the same number of rows")
        if not np.all(np.isfinite(X)):
            raise ValueError("X contains NaN or infinite values")
        if not self.sigma > 0:
            raise ValueError("sigma must be > 0 (Eq. 4)")
        if int(self.q) < 1 or int(self.k_neighbors) < 1:
            raise ValueError("q and k_neighbors must be >= 1")
        if self.k_delta < 0:
            raise ValueError("k_delta must be >= 0")

        classes, counts = np.unique(y, return_counts=True)
        if classes.size != 2:
            # CHOICE: the paper is binary only (Sec. 2, p. 1624) and binarizes multiclass data
            # sets before oversampling (Sec. 4.1, p. 1626); that is the caller's job here.
            raise ValueError(f"CGMOS handles two classes; got {classes.size}")
        i_min = int(np.argmin(counts))  # CHOICE: on a tie the first label is "minority"
        minority, majority = classes[i_min], classes[1 - i_min]
        n_min, n_maj = int(counts[i_min]), int(counts[1 - i_min])
        is_min = y == minority
        self.minority_label_, self.majority_label_ = minority, majority
        self.minority_indices_ = np.flatnonzero(is_min)

        # Step 0: amount k_delta * delta (Sec. 4.5, p. 1627).
        n_new = int(round(self.k_delta * (n_maj - n_min)))
        self.n_synthetic_ = n_new
        if n_new == 0:
            self.bandwidths_ = self.certainty_ = None
            self.weights_ = self.seed_proba_ = None
            self.seed_indices_ = self.partner_indices_ = np.empty(0, dtype=int)
            return X.copy(), y.copy()
        if n_min < 2:
            raise ValueError("SMOTE interpolation needs at least 2 minority samples")

        # Steps 1-5: bandwidths (Eq. 4), certainties (Eqs. 1-3), weights (Eqs. 5-6).
        # CHOICE: computed once, on the original data ("a single step", Sec. 1.2, p. 1624), not
        # updated as synthetic samples are added.
        W = self._seed_weights(X, y, is_min)
        # Step 6: seed probabilities W(x_i) / z, z = sum_i W(x_i) (p. 1625).
        p = W / W.sum()
        self.weights_, self.seed_proba_ = W, p

        # Step 7: SMOTE interpolation (p. 1625; Chawla et al. 2002).
        rng = check_random_state(self.random_state)
        X_min = X[is_min]
        # CHOICE: k is clipped to n_min - 1 when the minority class is very small.
        k = min(int(self.k_neighbors), n_min - 1)
        nbrs = NearestNeighbors(n_neighbors=k).fit(X_min).kneighbors(return_distance=False)
        # Seeds drawn independently, with replacement, with probability W(x_i) / z.
        seeds = rng.choice(n_min, size=n_new, replace=True, p=p)
        partners = nbrs[seeds, rng.randint(0, k, size=n_new)]
        # CHOICE: one gap per synthetic sample (a point on the segment, as SMOTE's text and
        # imbalanced-learn do), not one gap per attribute as in SMOTE's pseudo-code.
        gaps = rng.uniform(0.0, 1.0, size=n_new)
        X_new = X_min[seeds] + gaps[:, None] * (X_min[partners] - X_min[seeds])
        self.seed_indices_ = self.minority_indices_[seeds]
        self.partner_indices_ = self.minority_indices_[partners]

        # Step 8: original rows first, then synthetic rows.
        X_res = np.vstack([X, X_new])
        y_res = np.concatenate([y, np.full(n_new, minority, dtype=y.dtype)])
        return X_res, y_res
