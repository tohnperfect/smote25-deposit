"""AB-SMOTE: Affinitive Borderline SMOTE, re-implemented for the SMOTE25 rerun (WP6.8).

Paper: H. Al Majzoub and I. Elgedawy, "AB-SMOTE: An Affinitive Borderline SMOTE Approach
for Imbalanced Data Binary Classification", International Journal of Machine Learning and
Computing 10(1):31-37, 2020, doi:10.18178/ijmlc.2020.10.1.894. Page numbers below are the
journal's (31-37). The paper has no numbered equations; formulas are cited by section and
page, algorithm steps by the boxes of its flowchart (Fig. 6, p.33).

Method, step by step (the paper's notation in brackets):

1. Split the training set into minority instances P and majority instances N
   (Fig. 6, boxes "Define"; Sec. III, p.33: "AB-SMOTE defines the minority and majority
   class instances").
2. For every minority instance p_i find its M nearest neighbors [Mnn] in the whole
   training set and count the majority instances among them [M'] (Sec. II.B, p.32;
   Sec. III, p.33; Fig. 6, box "Check Mnn").
3. p_i is borderline ("danger") if M' lies between M/2 and M; it is safe if M' < M/2 and
   noise if M' = M (Sec. III, p.33). Borderline instances form the subset P'
   (Fig. 6, box "Create Borderline Subset"). CHOICE: see ``borderline_rule``.
4. For every borderline instance p'_i find its k nearest neighbors [Knn] within P' only,
   not within all of P; this is the only change from Borderline-SMOTE (Sec. III, p.33:
   "instead of checking Knn between the borderline instances and all minority
   instances, it only checks Knn within the borderline instances"; Fig. 6, box
   "Check Knn": "Borderline class instance P'j"; Fig. 5).
5. Generate: choose one of the k neighbors p'_j at random and set
   new = p'_i + gap * (p'_j - p'_i), gap a random number in [0, 1]
   (Sec. III, p.33, formula "New instance = P'i + gap * (distance (P'i, P'j))", where
   "distance" is the difference vector, Sec. II.A, p.32; Fig. 6, box "Generate new
   instance"; Table III, p.34, GAP 0-1).
6. The number of new instances follows the percentage parameter, 100 in every
   AB-SMOTE setting of Table III (p.34): 100% gives one new instance per borderline
   instance, so Gen = |P'| in Tables IV-XI (pp.34-35); SMOTE's 100% default doubles the
   class it is applied to (Sec. II.A, p.32).

Defaults are the paper's setting 4.0 (Table III, p.34): M = 5, k = 5, gap in [0, 1],
percentage 100. Table III also runs (M, k) = (5, 8), (8, 5), (8, 8).

Choices the paper leaves open are marked ``CHOICE:`` below and listed in NOTES.md.
Uses NumPy, SciPy and scikit-learn only.
"""
import math

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_X_y

_RULES = ("text", "figure", "authors_code")
_GAPS = ("scalar", "per_feature")


def _stable_knn(X, queries, pool, n_neighbors, exclude_self=True, chunk=512):
    """Row indices of the n_neighbors nearest rows of X[pool] for each row X[queries].

    CHOICE: Euclidean distance on X as given (the paper names no metric; the caller has
    already scaled the features; the authors' WEKA runs used unscaled values plus VDM for
    nominal attributes, see NOTES.md). Squared distances are compared (same order).
    CHOICE: ties are broken by the lower row index, and a query is excluded from its own
    neighbors by row index only, so exact duplicates of a query count as its neighbors.
    """
    queries = np.asarray(queries, dtype=int)
    pool = np.asarray(pool, dtype=int)                  # ascending row indices
    out = np.empty((len(queries), n_neighbors), dtype=int)
    if n_neighbors == 0 or len(queries) == 0:
        return out
    pos_in_pool = {r: p for p, r in enumerate(pool)}
    R = X[pool]
    for s in range(0, len(queries), chunk):
        q = queries[s:s + chunk]
        D = cdist(X[q], R, metric="sqeuclidean")
        if exclude_self:
            for row, r in enumerate(q):
                p = pos_in_pool.get(int(r))
                if p is not None:
                    D[row, p] = np.inf
        kth = np.partition(D, n_neighbors - 1, axis=1)[:, n_neighbors - 1]
        for row in range(len(q)):
            cand = np.flatnonzero(D[row] <= kth[row])   # ascending pool positions
            cand = cand[np.argsort(D[row, cand], kind="stable")][:n_neighbors]
            out[s + row] = pool[cand]
    return out


class ABSMOTE(BaseEstimator):
    """Affinitive Borderline SMOTE (Al Majzoub and Elgedawy, 2020), two-class data.

    Parameters
    ==========
    m_neighbors : int, default 5
        M, the neighborhood size in the whole training set used to find borderline
        minority instances (Mnn; Sec. II.B, p.32; Sec. III, p.33; Table III, p.34).
    k_neighbors : int, default 5
        k, the number of nearest borderline neighbors from which the partner is drawn
        (Knn; Sec. III, p.33; Table III, p.34).
    percentage : float, default 100
        Amount of oversampling in percent of |P'| (Table III, p.34; Sec. II.A, p.32).
        CHOICE: for values that are not multiples of 100, each borderline instance gets
        floor(percentage/100) new instances and int(fraction * |P'|) of them, drawn
        without replacement, get one more (the convention of WEKA's SMOTE filter, which
        the authors modified, Sec. IV, p.33-34).
    borderline_rule : {"text", "figure", "authors_code"}, default "text"
        CHOICE: how M' marks a minority instance as borderline.
        "text": the instance is not its own neighbor and M/2 <= M' < M, so M' < M/2 is
        safe and M' = M is noise, as the text says (Sec. II.B, p.32; Sec. III, p.33) and
        as in Borderline-SMOTE (Han et al. 2005, the paper's ref. [9]).
        "figure": M/2 < M' < M, as printed in the flowcharts (Fig. 4 and Fig. 6, p.33);
        differs from "text" only when M' = M/2 (even M).
        "authors_code": the instance counts as one of its own M neighbors (distance 0,
        ties by row order) and the bound is the integer M/2 = floor(M/2), so M' < M
        always and noise is never removed. Not what the paper says, but the only reading
        found that reproduces the paper's Gen counts (Tables IV, VI, IX, X); see
        VALIDATION.md.
    gap : {"scalar", "per_feature"}, default "scalar"
        CHOICE: "scalar" draws one gap per new instance, so it lies on the segment
        between p'_i and p'_j ("new instances falling in the line space between the
        selected instances", Sec. II.A, p.32; "Multiply by Gap: (0-1)", Fig. 6).
        "per_feature" draws one gap per feature, as WEKA's SMOTE filter does (and as the
        authors' runs evidently did; see VALIDATION.md); the point then lies in the box
        spanned by p'_i and p'_j.
    random_state : None, int or numpy.random.RandomState, default None
        Seed or generator for the partner choices and gaps.

    Attributes (after ``fit_resample``)
    ==========
    minority_class_ : label of the minority class.
    minority_indices_ : row indices of the minority instances (ascending).
    m_prime_ : M' of each minority instance, aligned with ``minority_indices_``.
    borderline_indices_ : row indices of P' (ascending).
    borderline_neighbors_ : (|P'|, k_eff) row indices of each borderline instance's
        nearest borderline neighbors, nearest first.
    k_eff_ : number of borderline neighbors actually used.
    seed_indices_, partner_indices_, gaps_ : per new instance, the row of p'_i, the row
        of p'_j and the gap(s) used.
    n_synthetic_ : number of new instances.
    """

    def __init__(self, m_neighbors=5, k_neighbors=5, percentage=100.0,
                 borderline_rule="text", gap="scalar", random_state=None):
        self.m_neighbors = m_neighbors
        self.k_neighbors = k_neighbors
        self.percentage = percentage
        self.borderline_rule = borderline_rule
        self.gap = gap
        self.random_state = random_state

    # == helpers ==
    def _check_params(self):
        if int(self.m_neighbors) != self.m_neighbors or self.m_neighbors < 1:
            raise ValueError("m_neighbors must be a positive integer")
        if int(self.k_neighbors) != self.k_neighbors or self.k_neighbors < 1:
            raise ValueError("k_neighbors must be a positive integer")
        if not np.isfinite(self.percentage) or self.percentage < 0:
            raise ValueError("percentage must be a non-negative number")
        if self.borderline_rule not in _RULES:
            raise ValueError(f"borderline_rule must be one of {_RULES}")
        if self.gap not in _GAPS:
            raise ValueError(f"gap must be one of {_GAPS}")

    def _borderline(self, X, y, minority):
        """Steps 2-3: M' for every minority instance and the borderline subset P'."""
        n = len(y)
        mino = np.flatnonzero(y == minority)
        M = int(self.m_neighbors)
        if self.borderline_rule == "authors_code":
            # CHOICE (authors_code): the instance itself is one of its M neighbors.
            M_eff = min(M, n)
            nn = _stable_knn(X, mino, np.arange(n), M_eff, exclude_self=False)
        else:
            # CHOICE: with fewer than M other rows, all other rows are the neighbors.
            M_eff = min(M, n - 1)
            nn = _stable_knn(X, mino, np.arange(n), M_eff, exclude_self=True)
        m_prime = np.sum(y[nn] != minority, axis=1)
        if self.borderline_rule == "text":
            # Sec. III, p.33: safe if M' < M/2, noise if M' = M, borderline otherwise.
            mask = (m_prime >= M_eff / 2.0) & (m_prime < M_eff)
        elif self.borderline_rule == "figure":
            # Figs. 4 and 6, p.33: "If M/2 < M' < M".
            mask = (m_prime > M_eff / 2.0) & (m_prime < M_eff)
        else:
            # Integer M/2 as in Java (floor); M' < M always holds here.
            mask = (m_prime >= M_eff // 2) & (m_prime < M_eff)
        return mino, m_prime, mino[mask]

    # == API ==
    def fit_resample(self, X, y):
        """Return (X_res, y_res): the original rows first, then the new minority rows."""
        self._check_params()
        X, y = check_X_y(X, y, dtype=np.float64)
        y = np.asarray(y)
        labels, counts = np.unique(y, return_counts=True)
        if len(labels) != 2:
            # CHOICE: the paper defines the method for two classes only (title; Sec. I,
            # p.31: "the datasets have two classes"); no multiclass rule is given.
            raise ValueError(f"ABSMOTE needs exactly two classes, got {len(labels)}")
        # CHOICE: the minority class is the smaller one; on a tie, the smaller label.
        minority = labels[int(np.argmin(counts))]
        rng = check_random_state(self.random_state)

        mino, m_prime, border = self._borderline(X, y, minority)
        self.minority_class_ = minority
        self.minority_indices_ = mino
        self.m_prime_ = m_prime
        self.borderline_indices_ = border

        # Step 4: k nearest neighbors within P' only. CHOICE: k_eff = min(k, |P'| - 1),
        # as WEKA's SMOTE caps k for a small class; |P'| < 2 leaves no partner, so no
        # new instances are made.
        k_eff = min(int(self.k_neighbors), len(border) - 1) if len(border) > 1 else 0
        self.k_eff_ = k_eff
        self.borderline_neighbors_ = _stable_knn(X, border, border, k_eff, exclude_self=True)

        # Step 6: how many new instances per borderline instance.
        n_b = len(border) if k_eff > 0 else 0
        per_seed = np.full(n_b, int(math.floor(self.percentage / 100.0)), dtype=int)
        frac = self.percentage / 100.0 - math.floor(self.percentage / 100.0)
        n_extra = int(frac * n_b)
        if n_extra > 0:
            per_seed[rng.choice(n_b, size=n_extra, replace=False)] += 1
        # CHOICE: new rows are grouped by seed, seeds in row order (the paper gives no order).
        seed_pos = np.repeat(np.arange(n_b), per_seed)
        n_new = len(seed_pos)

        # Step 5: partner uniformly among the k_eff nearest borderline neighbors
        # (Sec. III, p.33: "randomly chooses one of the Knn"). CHOICE: gap uniform on
        # [0, 1) (the paper says only "a random number having value between 0 and 1",
        # pp.32-33; Table III, p.34: GAP 0-1).
        d = X.shape[1]
        if n_new > 0:
            which = rng.randint(k_eff, size=n_new)
            partners = self.borderline_neighbors_[seed_pos, which]
            seeds = border[seed_pos]
            if self.gap == "scalar":
                gaps = rng.random_sample((n_new, 1))
            else:
                gaps = rng.random_sample((n_new, d))
            X_new = X[seeds] + gaps * (X[partners] - X[seeds])
        else:
            partners = np.empty(0, dtype=int)
            seeds = np.empty(0, dtype=int)
            gaps = np.empty((0, 1 if self.gap == "scalar" else d))
            X_new = np.empty((0, d))
        self.seed_indices_ = seeds
        self.partner_indices_ = partners
        self.gaps_ = gaps
        self.n_synthetic_ = n_new

        X_res = np.vstack([X, X_new])
        y_res = np.concatenate([y, np.full(n_new, minority, dtype=y.dtype)])
        return X_res, y_res

    def fit(self, X, y):
        """Run the method and keep the fitted attributes; returns self."""
        self.fit_resample(X, y)
        return self
