"""Quick checks for fwsmote.FWSMOTE (WP6.8 brief, item 2).

Run:  python3 -I test_fwsmote.py      (or: python3 -I -m pytest -q test_fwsmote.py)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.neighbors import NearestNeighbors  # noqa: E402

from fwsmote import (  # noqa: E402
    FWSMOTE,
    correlation_score,
    fisher_score,
    iowa_feature_weights,
    rim_weights,
)

KEEL = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw"


def load_keel(name):
    """KEEL .dat from keel-ds 0.2.5: comma-separated, last column the class, no header."""
    X, y = [], []
    with open(os.path.join(KEEL, name + ".dat")) as fh:
        for line in fh:
            parts = [t.strip() for t in line.strip().split(",")]
            if len(parts) < 2:
                continue
            X.append([float(t) for t in parts[:-1]])
            y.append(1 if parts[-1] == "positive" else 0)
    return np.array(X), np.array(y)


def toy(n_maj=60, n_min=12, n_feat=6, seed=0):
    rng = np.random.RandomState(seed)
    X = np.vstack([rng.normal(0, 1, (n_maj, n_feat)), rng.normal(1, 1, (n_min, n_feat))])
    y = np.array([0] * n_maj + [1] * n_min)
    return X, y


def segment_partner(s, xi, M, cand):
    """Return (partner row in M, v, residual) for synthetic s = xi + v (M[j] - xi), j in cand."""
    best = None
    for j in cand:
        d = M[j] - xi
        v = float(np.dot(s - xi, d) / np.dot(d, d))
        res = float(np.linalg.norm(s - xi - v * d))
        if best is None or res < best[2]:
            best = (j, v, res)
    return best


def test_original_rows_and_labels_unchanged():
    X, y = toy()
    Xr, yr = FWSMOTE(N=3, random_state=0).fit_resample(X, y)
    assert np.array_equal(Xr[: len(X)], X)
    assert np.array_equal(yr[: len(y)], y)
    assert np.all(yr[len(y):] == 1)
    assert yr.dtype == y.dtype and Xr.dtype == np.float64


def test_number_of_synthetic_rows():
    # Algorithm 1 steps 5 and 10: N synthetic examples per minority example.
    X, y = toy()
    for N in (0, 1, 3, 5, 7):  # 7 > k = 5: T is refilled (CHOICE C12)
        s = FWSMOTE(N=N, random_state=1)
        Xr, yr = s.fit_resample(X, y)
        assert Xr.shape[0] == len(X) + N * 12 == len(yr)
        assert s.n_synthetic_ == N * 12
        assert np.sum(yr == 0) == 60  # majority untouched


def test_same_seed_same_output():
    X, y = toy()
    a = FWSMOTE(N=3, random_state=42).fit_resample(X, y)
    b = FWSMOTE(N=3, random_state=42).fit_resample(X, y)
    c = FWSMOTE(N=3, random_state=43).fit_resample(X, y)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])
    rs = np.random.RandomState(7)
    d = FWSMOTE(N=3, random_state=rs).fit_resample(X, y)
    assert np.all(np.isfinite(d[0]))


def test_no_nan_on_degenerate_data():
    X, y = toy()
    X = np.column_stack([X, np.full(len(X), 3.0)])  # constant feature
    X[61] = X[60]  # duplicate minority row
    X[:60, 2] = 0.5  # feature constant within the majority class
    for rk in ("fisher", "mi", "ec", "cfs"):
        for q in ("basic", "quadratic", "exponential", "trigonometric"):
            for p in (1, 2, np.inf):
                s = FWSMOTE(N=3, ranking=rk, quantifier=q, p=p, random_state=0)
                Xr, yr = s.fit_resample(X, y)
                assert np.all(np.isfinite(Xr)), (rk, q, p)
                assert np.all(np.isfinite(s.feature_weights_))
                assert abs(s.feature_weights_.sum() - 1) < 1e-9


def test_seven_minority_task():
    # ecoli-0-1-3-7_vs_2-6: 281 rows, 7 minority (the smallest minority among the rerun's
    # KEEL tasks), and a 5-fold training subset with 5 or 6 minority examples.
    X, y = load_keel("ecoli-0-1-3-7_vs_2-6")
    assert np.sum(y == 1) == 7
    for rk in ("fisher", "mi", "ec", "cfs"):
        for N in (1, 3):
            Xr, yr = FWSMOTE(N=N, ranking=rk, random_state=0).fit_resample(X, y)
            assert Xr.shape[0] == len(X) + 7 * N and np.all(np.isfinite(Xr))
    keep = np.r_[np.flatnonzero(y == 0), np.flatnonzero(y == 1)[:5]]
    s = FWSMOTE(N=3, random_state=0)
    Xr, yr = s.fit_resample(X[keep], y[keep])
    assert s.neighbors_.shape == (5, 4)  # k capped at |M| - 1
    assert Xr.shape[0] == len(keep) + 15
    s = FWSMOTE(N=3, variant="smoteiowa2019", random_state=0)
    assert s.fit_resample(X, y)[0].shape[0] == len(X) + 21


def test_synthetic_rows_on_segments_to_distinct_neighbors():
    X, y = toy(n_min=15, seed=3)
    s = FWSMOTE(N=3, k=5, random_state=0)
    Xr, _ = s.fit_resample(X, y)
    M = X[s.minority_indices_]
    syn = Xr[len(X):].reshape(len(M), 3, -1)  # seed by seed (step 5 order)
    for i in range(len(M)):
        partners = []
        for t in range(3):
            j, v, res = segment_partner(syn[i, t], M[i], M, s.neighbors_[i])
            assert res < 1e-9 and 0.0 <= v < 1.0
            partners.append(j)
        assert len(set(partners)) == 3  # step 14: drawn without replacement


def test_imowad_neighbors_match_eq5():
    X, y = toy(n_min=20, seed=5)
    for p in (1, 2, 3.0, np.inf):
        for cheb in ("weighted", "limit"):
            s = FWSMOTE(N=1, k=4, p=p, chebyshev=cheb, r=0.75, random_state=0)
            s.fit_resample(X, y)
            M = X[s.minority_indices_][:, s.selected_features_]
            w = s.distance_weights_
            B = np.abs(M[:, None, :] - M[None, :, :])
            if np.isinf(p):
                D = (B * w).max(-1) if cheb == "weighted" else B.max(-1)
            else:
                D = ((B ** p) * w).sum(-1) ** (1.0 / p)
            np.fill_diagonal(D, np.inf)
            ref = np.argsort(D, axis=1, kind="stable")[:, :4]
            assert np.array_equal(ref, s.neighbors_), (p, cheb)


def test_k_smallest_equals_stable_sort_with_ties():
    from fwsmote import _k_smallest

    rng = np.random.RandomState(0)
    for _ in range(100):
        D = rng.randint(0, 5, size=(25, 30)).astype(float)
        for k in (1, 4, 5, 12):
            assert np.array_equal(_k_smallest(D, k), np.argsort(D, axis=1, kind="stable")[:, :k])


def test_reduces_to_smote():
    # p.6: equal weights, r = n and p = 2 give SMOTE's Euclidean neighborhood.
    X, y = toy(n_min=25, seed=9)
    s = FWSMOTE(N=1, k=5, ranking=lambda X, y: np.zeros(X.shape[1]), r=1.0, p=2, random_state=0)
    s.fit_resample(X, y)
    assert np.allclose(s.distance_weights_, 1.0 / X.shape[1])
    M = X[s.minority_indices_]
    nn = NearestNeighbors(n_neighbors=6).fit(M)
    _, ind = nn.kneighbors(M)
    assert np.array_equal(np.sort(ind[:, 1:], axis=1), np.sort(s.neighbors_, axis=1))


def test_rim_weights():
    w = rim_weights(4, 0.4, "basic")  # Eq. (9)
    ref = np.array([0.25 ** 0.4, 0.5 ** 0.4 - 0.25 ** 0.4, 0.75 ** 0.4 - 0.5 ** 0.4, 1 - 0.75 ** 0.4])
    assert np.allclose(w, ref) and abs(w.sum() - 1) < 1e-12
    assert np.all(np.diff(w) < 0)  # alpha < 1: the top-ranked feature weighs most
    for q in ("quadratic", "exponential", "trigonometric"):
        for a in (0.4, 0.6):
            v = rim_weights(7, a, q)
            assert abs(v.sum() - 1) < 1e-12 and np.all(v > 0) and np.all(v < 1)
    e = rim_weights(5, 0.4, "exponential")  # Eq. (11) normalized: decreasing
    assert np.all(np.diff(e) < 0)
    t = rim_weights(5, 0.6, "trigonometric")  # Eq. (12) as printed: increasing
    assert np.all(np.diff(t) > 0)


def test_fisher_matches_eq6():
    X = np.array([[1.0, 0.0], [3.0, 2.0], [5.0, 4.0], [10.0, 1.0], [14.0, 3.0]])
    y = np.array([0, 0, 0, 1, 1])
    fs = fisher_score(X, y, positive=1)
    # feature 0: |3 - 12| / (4 + 8) = 0.75; feature 1: |2 - 2| / (4 + 2) = 0
    assert np.allclose(fs, [0.75, 0.0])
    Xc = np.array([[1.0], [1.0], [2.0], [2.0]])
    assert np.isinf(fisher_score(Xc, np.array([0, 0, 1, 1]), 1)[0])


def test_cfs_and_ties():
    rng = np.random.RandomState(0)
    a = rng.rand(50)
    X = np.column_stack([a, a + 0.01 * rng.rand(50), rng.rand(50)])
    c = correlation_score(X)
    R = np.abs(np.corrcoef(X, rowvar=False))
    assert np.isclose(c[0], min(R[0, 1], R[0, 2]))
    w, order = iowa_feature_weights(np.array([2.0, 5.0, 2.0, 1.0]), np.array([0.4, 0.3, 0.2, 0.1]))
    assert np.array_equal(order, [1, 0, 2, 3])
    assert np.allclose(w, [0.25, 0.4, 0.25, 0.1])  # tied features share positions 2-3


def test_r_rounding_and_threshold():
    X, y = load_keel("ecoli-0-1-3-7_vs_2-6")  # n = 7
    for r, size in ((0.5, 4), (0.75, 5), (1.0, 7), (3, 3), (10, 7)):
        s = FWSMOTE(r=r, random_state=0)
        s.fit_resample(X, y)
        assert s.selected_features_.size == size, (r, size)
    s = FWSMOTE(epsilon=0.12, random_state=0)
    s.fit_resample(X, y)
    assert np.all(s.feature_weights_[s.selected_features_] > 0.12)
    s = FWSMOTE(epsilon=0.99, random_state=0)
    s.fit_resample(X, y)
    assert s.selected_features_.size == 1  # CHOICE C10


def test_two_class_only_and_minimum_minority():
    X, y = toy()
    y3 = y.copy()
    y3[:10] = 2
    for bad_y in (y3, np.zeros_like(y)):
        try:
            FWSMOTE().fit_resample(X, bad_y)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
    y1 = np.zeros(len(y), dtype=int)
    y1[0] = 1
    try:
        FWSMOTE().fit_resample(X, y1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for one minority example")


def test_variant_smoteiowa2019():
    X, y = toy(n_min=15, seed=4)
    s = FWSMOTE(N=3, variant="smoteiowa2019", random_state=0)
    Xr, _ = s.fit_resample(X, y)
    M = X[s.minority_indices_]
    syn = Xr[len(X):].reshape(len(M), 3, -1)
    for i in range(len(M)):
        for t in range(3):
            j, v, res = segment_partner(syn[i, t], M[i], M, s.neighbors_[i])
            assert res < 1e-9 and abs(v - 0.3) < 1e-12  # fixed gap
    assert abs(s.distance_weights_.sum() - 1) < 1e-12  # RIM over the |S| kept positions


def test_sklearn_clone_and_params():
    s = FWSMOTE(N=3, ranking="mi", p=2, random_state=5)
    c = clone(s)
    assert c.get_params() == s.get_params()
    X, y = toy()
    assert np.array_equal(s.fit_resample(X, y)[0], c.fit_resample(X, y)[0])


if __name__ == "__main__":
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for name, fn in tests:
        fn()
        print("ok  ", name)
    print(f"{len(tests)} tests passed")
