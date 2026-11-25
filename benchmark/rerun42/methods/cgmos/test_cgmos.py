"""Quick checks for cgmos.CGMOS (run: python3 -I test_cgmos.py, or python3 -I -m pytest test_cgmos.py)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:  # python3 -I does not put the script's folder on sys.path
    sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

from cgmos import CGMOS, cgmos_weights, kde_bandwidths  # noqa: E402

HABERMAN = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/haberman.dat"


def _toy(n_maj=60, n_min=7, m=4, seed=0, labels=(0, 1)):
    rng = np.random.RandomState(seed)
    X = np.vstack([rng.normal(0.0, 1.0, (n_maj, m)), rng.normal(1.5, 1.0, (n_min, m))])
    y = np.r_[np.full(n_maj, labels[0]), np.full(n_min, labels[1])].astype(int)
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def test_original_rows_and_labels_unchanged():
    X, y = _toy()
    Xr, yr = CGMOS(random_state=0).fit_resample(X, y)
    n = len(y)
    assert np.array_equal(Xr[:n], X) and np.array_equal(yr[:n], y)
    assert np.all(yr[n:] == 1)
    assert set(np.unique(yr)) == {0, 1}


def test_number_of_synthetic_rows_follows_k_delta():
    # Sec. 4.5 (p. 1627): k * delta new samples, delta = n_mjr - n_mnr; default k = 1 (balance).
    X, y = _toy(n_maj=60, n_min=7)
    delta = 60 - 7
    for k_delta, expected in [(1.0, delta), (0.5, int(round(0.5 * delta))), (2.0, 2 * delta), (0.0, 0)]:
        Xr, yr = CGMOS(k_delta=k_delta, random_state=1).fit_resample(X, y)
        assert Xr.shape[0] - X.shape[0] == expected, (k_delta, Xr.shape[0] - X.shape[0])
        assert yr.shape[0] == Xr.shape[0]
    _, yr = CGMOS(random_state=1).fit_resample(X, y)
    assert np.sum(yr == 1) == np.sum(yr == 0)  # balanced by default


def test_same_random_state_same_output():
    X, y = _toy(seed=3)
    a = CGMOS(random_state=42).fit_resample(X, y)
    b = CGMOS(random_state=42).fit_resample(X, y)
    c = CGMOS(random_state=43).fit_resample(X, y)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])


def test_no_nan_and_seven_minority_examples():
    X, y = _toy(n_maj=90, n_min=7, m=6, seed=5)
    for kw in ({}, {"normalize_kernel": True}, {"bandwidth_neighbors": "all"}):
        s = CGMOS(random_state=0, **kw)
        Xr, yr = s.fit_resample(X, y)
        assert np.all(np.isfinite(Xr))
        assert Xr.shape == (180, 6) and np.sum(yr == 1) == 90
        assert np.all(s.weights_ > 0) and abs(s.seed_proba_.sum() - 1) < 1e-12  # W > 0 (p. 1625)


def test_tiny_minority_clips_neighbors():
    X, y = _toy(n_maj=30, n_min=3, seed=7)  # k and q clipped to 2
    Xr, yr = CGMOS(random_state=0).fit_resample(X, y)
    assert np.all(np.isfinite(Xr)) and np.sum(yr == 1) == 30


def test_synthetic_rows_lie_on_segments_to_minority_neighbors():
    X, y = _toy(n_maj=80, n_min=12, seed=11)
    s = CGMOS(random_state=0)
    Xr, _ = s.fit_resample(X, y)
    new = Xr[len(y):]
    a, b = X[s.seed_indices_], X[s.partner_indices_]
    assert np.all(y[s.seed_indices_] == 1) and np.all(y[s.partner_indices_] == 1)
    t = np.einsum("ij,ij->i", new - a, b - a) / np.einsum("ij,ij->i", b - a, b - a)
    assert np.all((t >= -1e-12) & (t <= 1 + 1e-12))
    assert np.allclose(a + t[:, None] * (b - a), new)
    # partner is one of the seed's 5 nearest minority neighbors
    Xm = X[y == 1]
    idx_min = np.flatnonzero(y == 1)
    for sd, pt in zip(s.seed_indices_[:20], s.partner_indices_[:20]):
        d = np.linalg.norm(Xm - X[sd], axis=1)
        d[idx_min == sd] = np.inf
        assert pt in idx_min[np.argsort(d)[:5]]


def _brute_weights(X, y, h, normalize):
    """Eqs. 3, 5, 6 recomputed literally: append a copy of x_i and rerun Bayes' rule."""
    n, m = X.shape

    def post(Xc, yc, hc, x):
        K = np.exp(-((Xc - x) ** 2).sum(1) / (2 * hc**2))
        if normalize:
            K = K * hc ** (-m)
        num = np.array([K[yc == l].sum() / np.sum(yc == l) * np.mean(yc == l) for l in (0, 1)])
        return num / num.sum()

    C = np.array([post(X, y, h, X[j])[y[j]] for j in range(n)])
    W = []
    for i in np.flatnonzero(y == 1):
        X2, y2, h2 = np.vstack([X, X[i]]), np.append(y, 1), np.append(h, h[i])
        C2 = np.array([post(X2, y2, h2, X[j])[y[j]] for j in range(n)])
        W.append(1 + np.mean((C2 - C) / C))
    return np.array(W), C


def test_weights_match_literal_recomputation():
    X, y = _toy(n_maj=35, n_min=8, m=3, seed=2)
    for normalize in (False, True):
        for nb in ("class", "all"):
            h = kde_bandwidths(X, y, q=4, sigma=0.9, neighbors=nb)
            W, C = cgmos_weights(X, y == 1, h, normalize_kernel=normalize)
            Wb, Cb = _brute_weights(X, y, h, normalize)
            assert np.allclose(W, Wb, rtol=0, atol=1e-12) and np.allclose(C, Cb, atol=1e-12)


def test_other_label_values_and_duplicates():
    X, y = _toy(n_maj=50, n_min=9, seed=4, labels=(8, 3))
    X = np.vstack([X, np.repeat(X[y == 3][:1], 7, axis=0)])  # exact duplicates -> zero q-NN distance
    y = np.r_[y, np.full(7, 3)]
    s = CGMOS(random_state=0)
    Xr, yr = s.fit_resample(X, y)
    assert s.minority_label_ == 3 and np.all(yr[len(y):] == 3)
    assert np.all(np.isfinite(Xr)) and np.all(s.bandwidths_ > 0)
    assert yr.dtype == y.dtype


def test_multiclass_and_balanced_inputs():
    X, y = _toy()
    y3 = y.copy()
    y3[:5] = 2
    try:
        CGMOS().fit_resample(X, y3)
        raise AssertionError("three classes should raise")
    except ValueError:
        pass
    Xb = np.vstack([X[y == 1], X[y == 0][:7]])
    yb = np.r_[np.ones(7, int), np.zeros(7, int)]
    Xr, yr = CGMOS(random_state=0).fit_resample(Xb, yb)
    assert np.array_equal(Xr, Xb) and np.array_equal(yr, yb)


def test_haberman_runs():
    if not os.path.exists(HABERMAN):
        return
    rows = [r.split(",") for r in open(HABERMAN).read().split("\n") if r.strip() and not r.startswith("@")]
    X = np.array([[float(v) for v in r[:-1]] for r in rows])
    y = np.array([r[-1].strip() == "positive" for r in rows], dtype=int)
    X = (X - X.mean(0)) / X.std(0)
    Xr, yr = CGMOS(random_state=0).fit_resample(X, y)
    assert Xr.shape == (450, 3) and np.sum(yr == 1) == 225 and np.all(np.isfinite(Xr))


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} tests passed")
