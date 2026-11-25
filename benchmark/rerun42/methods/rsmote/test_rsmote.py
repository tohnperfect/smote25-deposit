"""Quick checks for rsmote.RSMOTE.  Run: python3 -I test_rsmote.py (or pytest)."""

import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsmote import RSMOTE, two_means_1d, _round_keep_sum  # noqa: E402


def make_data(n_maj=120, n_min=30, n_noise=3, seed=0, dim=2):
    """Two overlapping Gaussian classes plus isolated minority points placed
    deep in the majority class (label noise), minority label 1.  The noisy
    points are far apart, so none is among another's k nearest neighbors."""
    r = np.random.RandomState(seed)
    X_maj = r.normal(0.0, 1.0, size=(n_maj, dim))
    X_min = r.normal(2.0, 0.8, size=(n_min, dim))
    spots = np.array([[-1.2, -0.8], [0.3, -1.3], [-1.4, 0.7], [-0.4, -0.3]])
    X_noise = np.zeros((n_noise, dim))
    X_noise[:, :2] = spots[:n_noise]
    X = np.vstack([X_maj, X_min, X_noise])
    y = np.r_[np.zeros(n_maj, int), np.ones(n_min + n_noise, int)]
    perm = r.permutation(len(y))
    return X[perm], y[perm]


def test_original_rows_and_labels_unchanged():
    X, y = make_data()
    X_res, y_res = RSMOTE(random_state=1).fit_resample(X, y)
    n = len(y)
    assert isinstance(X_res, np.ndarray) and isinstance(y_res, np.ndarray)
    assert np.array_equal(X_res[:n], X)
    assert np.array_equal(y_res[:n], y)
    assert y_res.dtype == y.dtype
    assert np.all(y_res[n:] == 1)


def test_number_of_synthetic_rows_follows_algorithm_1_line_2():
    X, y = make_data()                       # |Q| = 120, |P| = 33 (3 noisy)
    n_q, n_p = np.sum(y == 0), np.sum(y == 1)
    for ir, expected in [(1.0, n_q - n_p), (2.0, int(n_q / 2.0) - n_p), (3.5, int(n_q / 3.5) - n_p)]:
        sampler = RSMOTE(ir=ir, random_state=0)
        X_res, y_res = sampler.fit_resample(X, y)
        assert len(y_res) - len(y) == expected, (ir, len(y_res) - len(y), expected)
        assert sampler.info_[1]["n_synthetic"] == expected
        assert sampler.info_[1]["n_per_seed"].sum() == expected
    # IR = 1: balanced output although noisy points are not seeds (|P| counts them).
    X_res, y_res = RSMOTE(random_state=0).fit_resample(X, y)
    assert np.sum(y_res == 1) == np.sum(y_res == 0)
    # Already at or beyond the requested ratio: nothing to add.
    X_res, y_res = RSMOTE(ir=n_q / n_p + 1, random_state=0).fit_resample(X, y)
    assert len(y_res) == len(y)


def test_same_random_state_same_output():
    X, y = make_data()
    a = RSMOTE(random_state=7).fit_resample(X, y)
    b = RSMOTE(random_state=7).fit_resample(X, y)
    c = RSMOTE(random_state=8).fit_resample(X, y)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])
    r1, r2 = np.random.RandomState(3), np.random.RandomState(3)
    assert np.array_equal(RSMOTE(random_state=r1).fit_resample(X, y)[0],
                          RSMOTE(random_state=r2).fit_resample(X, y)[0])


def test_no_nan_with_duplicates():
    X, y = make_data()
    # exact duplicates of minority rows (zero homogeneous distances)
    dup = np.repeat(X[y == 1][:2], 6, axis=0)
    X2, y2 = np.vstack([X, dup]), np.r_[y, np.ones(len(dup), int)]
    X_res, y_res = RSMOTE(random_state=0).fit_resample(X2, y2)
    assert np.all(np.isfinite(X_res))
    assert np.sum(y_res == 1) == np.sum(y_res == 0)


def test_seven_minority_examples():
    r = np.random.RandomState(5)
    X = np.vstack([r.normal(0, 1, size=(200, 3)), r.normal(2.5, 0.5, size=(7, 3))])
    y = np.r_[np.zeros(200, int), np.ones(7, int)]
    X_res, y_res = RSMOTE(random_state=0).fit_resample(X, y)
    assert len(y_res) == 400 and np.sum(y_res == 1) == 200
    assert np.all(np.isfinite(X_res))
    # Seven scattered minority points that are all noise: no crash, no rows.
    X = np.vstack([r.normal(0, 1, size=(200, 3)), r.normal(0, 1, size=(7, 3))])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sampler = RSMOTE(k_neighbors=5, random_state=0)
        X_res, y_res = sampler.fit_resample(X, y)
    assert np.array_equal(X_res[:207], X)
    if len(sampler.info_[1]["seed_index"]) < 2:
        assert len(y_res) == 207 and any("fewer than two" in str(w.message) for w in caught)
    # Smaller than k: k shrinks to |P| - 1.
    X = np.vstack([r.normal(0, 1, size=(50, 2)), r.normal(3, 0.3, size=(3, 2))])
    y = np.r_[np.zeros(50, int), np.ones(3, int)]
    sampler = RSMOTE(k_neighbors=5, random_state=0)
    X_res, y_res = sampler.fit_resample(X, y)
    assert sampler.info_[1]["k"] == 2 and np.sum(y_res == 1) == 50


def _on_segment(s, a, b, tol=1e-9):
    ab = b - a
    t = np.dot(s - a, ab) / max(np.dot(ab, ab), 1e-300)
    return -tol <= t <= 1 + tol and np.linalg.norm(a + t * ab - s) <= tol * (1 + np.linalg.norm(ab))


def test_noise_kept_in_data_but_never_used_for_interpolation():
    X, y = make_data(n_noise=3)
    sampler = RSMOTE(random_state=0)
    X_res, y_res = sampler.fit_resample(X, y)
    info = sampler.info_[1]
    noise = info["noise_index"]
    assert len(noise) >= 3                       # the planted points at (-1, -1)
    assert np.array_equal(X_res[noise], X[noise]) and np.all(y_res[noise] == 1)
    seeds = info["seed_index"]
    assert np.intersect1d(noise, seeds).size == 0
    # every synthetic row lies on a segment between two seeds of one cluster
    syn = X_res[len(y):]
    for s in syn:
        found = False
        for c in np.unique(info["cluster"]):
            S = X[seeds[info["cluster"] == c]]
            for i in range(len(S)):
                for j in range(len(S)):
                    if i != j and _on_segment(s, S[i], S[j]):
                        found = True
                        break
                if found:
                    break
            if found:
                break
        assert found


def test_relative_density_is_eq2():
    X, y = make_data()
    k = 5
    sampler = RSMOTE(k_neighbors=k, random_state=0)
    sampler.fit_resample(X, y)
    info = sampler.info_[1]
    P_idx, Q = np.flatnonzero(y == 1), X[y == 0]
    for row, rd in zip(info["seed_index"], info["relative_density"]):
        d_own = np.sort(np.linalg.norm(X[P_idx[P_idx != row]] - X[row], axis=1))[:k]
        d_other = np.sort(np.linalg.norm(Q - X[row], axis=1))[:k]
        assert np.isclose(rd, d_other.sum() / d_own.sum())
        # m: majority points among the k nearest in the whole D
        d_all = np.linalg.norm(X - X[row], axis=1)
        d_all[row] = np.inf
        nearest = np.argsort(d_all, kind="stable")[:k]
        m = np.sum(y[nearest] == 0)
        assert m == info["m"][list(info["seed_index"]).index(row)]
    for row in info["noise_index"]:
        d_all = np.linalg.norm(X - X[row], axis=1)
        d_all[row] = np.inf
        assert np.all(y[np.argsort(d_all, kind="stable")[:k]] == 0)


def test_counts_follow_step_3():
    X, y = make_data(n_maj=200, n_min=40)
    k = 5
    sampler = RSMOTE(k_neighbors=k, random_state=0)
    X_res, _ = sampler.fit_resample(X, y)
    info = sampler.info_[1]
    N = info["n_synthetic"]
    cl, m, n_i = info["cluster"], info["m"], info["n_per_seed"]
    assert info["split"]
    # safe cluster A has the larger mean relative density
    rd = info["relative_density"]
    assert rd[cl == 0].mean() > rd[cl == 1].mean()
    sizes = np.array([np.sum(cl == 0), np.sum(cl == 1)])
    n_j = np.array([n_i[cl == 0].sum(), n_i[cl == 1].sum()])
    assert n_j.sum() == N
    assert np.all(np.abs(n_j - sizes / sizes.sum() * N) < 1)            # line 17
    for j in (0, 1):
        w = (k - m[cl == j]) / (k + 1.0)                                  # line 19
        quota = w / w.sum() * n_j[j]                                      # lines 20-21
        assert np.all(np.abs(n_i[cl == j] - quota) < 1)


def test_two_means_is_optimal():
    from sklearn.cluster import KMeans
    r = np.random.RandomState(0)

    def sse(v, mask):
        return sum(((v[g] - v[g].mean()) ** 2).sum() for g in (mask, ~mask) if g.any())

    for trial in range(30):
        v = np.r_[r.gamma(2.0, 1.0, size=r.randint(5, 40)), r.gamma(9.0, 1.0, size=r.randint(2, 30))]
        mask = two_means_1d(v)
        km = KMeans(n_clusters=2, n_init=10, random_state=trial).fit(v.reshape(-1, 1))
        km_mask = km.labels_ == np.argmax(km.cluster_centers_.ravel())
        assert sse(v, mask) <= sse(v, km_mask) + 1e-9
        assert v[mask].min() > v[~mask].max()
    assert two_means_1d(np.ones(5)) is None and two_means_1d(np.array([3.0])) is None


def test_round_keep_sum():
    assert list(_round_keep_sum([1.5, 1.5, 1.0], 4)) == [2, 1, 1]
    q = np.array([0.2, 3.7, 2.1, 9.0])
    out = _round_keep_sum(q, 15)
    assert out.sum() == 15 and np.all(np.abs(out - q) < 1)


def test_multiclass_balances_every_smaller_class():
    r = np.random.RandomState(2)
    X = np.vstack([r.normal(0, 1, (100, 2)), r.normal(3, 1, (40, 2)), r.normal([0, 4], 1, (15, 2))])
    y = np.r_[np.full(100, 2), np.full(40, 0), np.full(15, 1)]
    X_res, y_res = RSMOTE(random_state=0).fit_resample(X, y)
    assert np.array_equal(X_res[:155], X) and np.array_equal(y_res[:155], y)
    assert all(np.sum(y_res == c) == 100 for c in (0, 1, 2))


def test_estimator_interface():
    s = RSMOTE(k_neighbors=3, ir=1.0, random_state=0)
    assert s.get_params() == {"k_neighbors": 3, "ir": 1.0, "random_state": 0}
    from sklearn.base import clone
    assert clone(s).get_params() == s.get_params()


if __name__ == "__main__":
    names = [n for n in sorted(globals()) if n.startswith("test_")]
    for n in names:
        globals()[n]()
        print("ok", n)
    print(f"{len(names)} tests passed")
