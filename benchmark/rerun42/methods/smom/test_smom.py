"""Quick checks of smom.SMOM. Run: python3 -I test_smom.py (or python3 -I -m pytest test_smom.py)."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smom import SMOM, _k_smallest  # noqa: E402


def two_class(n_maj=300, n_min=40, d=4, shift=1.5, seed=0):
    rng = np.random.default_rng(seed)
    X = np.vstack([rng.normal(0.0, 1.0, (n_maj, d)), rng.normal(shift, 1.0, (n_min, d))])
    y = np.r_[np.zeros(n_maj, dtype=int), np.ones(n_min, dtype=int)]
    perm = rng.permutation(y.size)  # minority rows not contiguous
    return X[perm], y[perm]


def test_two_class_rows_labels_and_count():
    X, y = two_class()
    Xr, yr = SMOM(random_state=0).fit_resample(X, y)
    n = y.size
    assert np.array_equal(Xr[:n], X) and np.array_equal(yr[:n], y)  # originals first, unchanged
    # Paper's rule (p. 335): oversample to the size of the largest class.
    assert Xr.shape == (2 * 300, X.shape[1]) and yr.shape == (600,)
    assert np.all(yr[n:] == 1) and np.bincount(yr).tolist() == [300, 300]
    assert np.all(np.isfinite(Xr))


def test_same_random_state_same_output():
    X, y = two_class(seed=3)
    a = SMOM(random_state=7).fit_resample(X, y)
    b = SMOM(random_state=7).fit_resample(X, y)
    c = SMOM(random_state=8).fit_resample(X, y)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])


def test_seven_minority_examples():
    X, y = two_class(n_maj=150, n_min=7, d=5, shift=1.0, seed=1)
    s = SMOM(random_state=0)
    Xr, yr = s.fit_resample(X, y)
    assert Xr.shape[0] == 300 and np.sum(yr == 1) == 150 and np.all(np.isfinite(Xr))
    info = s.class_info_[1]
    assert info["k1"] == 6  # k1 reset to |S^c| - 1 (p. 337)
    assert info["n_trapped"] == 7  # no cluster can reach nTh = 10


def test_multiclass_counts():
    rng = np.random.default_rng(2)
    X = np.vstack([rng.normal(0, 1, (150, 3)), rng.normal(2, 1, (60, 3)), rng.normal([0, 3, 0], 1, (30, 3))])
    y = np.r_[np.zeros(150, int), np.ones(60, int), np.full(30, 2)]
    s = SMOM(random_state=0)
    Xr, yr = s.fit_resample(X, y)
    assert np.bincount(yr).tolist() == [150, 150, 150]
    assert s.sampling_strategy_ == {1: 90, 2: 120}
    assert np.array_equal(Xr[:240], X) and np.all(np.isfinite(Xr))


def test_eq2_values():
    s = SMOM()
    e = np.e
    # columns: class 0 (c), class 1 (majority), classes 2, 3, 4 (minority)
    counts = np.array([[2, 0, 0, 0, 0],    # clean neighborhood
                       [2, 2, 0, 0, 0],    # c and one majority class (the two-class case)
                       [3, 0, 1, 1, 1],    # three minority classes, even
                       [3, 0, 3, 0, 0]], dtype=float)
    sw, clean = s._eq2(counts, 0, [2, 3, 4], [1])
    assert np.allclose(sw[0], 1 + 0.2 / e) and clean.tolist() == [True, False, False, False]
    assert np.allclose(sw[1], np.exp(-0.5 * (1 / 3) * 1.0) + 0.2 * np.exp(-0.5))
    assert np.allclose(sw[2], np.exp(-((1 / 3) * 1.0 + 0.2 * 1.0)) + 0.2 * np.exp(-0.5))  # E_mi = 1
    assert np.allclose(sw[3], np.exp(-((1 / 3) * 1.0 + 0.0)) + 0.2 * np.exp(-0.5))  # E_mi = 0
    assert sw[2] < sw[3]  # observation 3 (p. 333): even minority mix is penalised more


def test_synthetic_rows_on_neighbor_rectangles():
    """Each synthetic row lies in the box spanned by a seed and one of its k1 same-class
    neighbors (or the seed itself), Eq. (1) and Step 8."""
    X, y = two_class(n_maj=120, n_min=25, d=3, seed=4)
    Xr, yr = SMOM(random_state=0).fit_resample(X, y)
    Xc = X[y == 1]
    D = np.linalg.norm(Xc[:, None] - Xc[None], axis=2)
    np.fill_diagonal(D, np.inf)
    nn = _k_smallest(D, 12)
    lo = np.minimum(Xc[:, None, :], Xc[nn])
    hi = np.maximum(Xc[:, None, :], Xc[nn])
    for srow in Xr[y.size:]:
        inside = np.all((lo <= srow + 1e-12) & (srow - 1e-12 <= hi), axis=2)
        same = np.all(np.abs(Xc - srow) < 1e-12, axis=1)
        assert inside.any() or same.any()


def test_outstanding_and_trapped():
    """NBDOS: a dense cluster of 15 is outstanding; a dense cluster of 5 (< nTh = 10) and
    minority points scattered in the majority cloud are trapped (Alg. 2, Step 4)."""
    rng = np.random.default_rng(5)
    maj = rng.normal(0, 1, (300, 2))
    big = rng.normal([10, 10], 0.2, (15, 2))
    small = rng.normal([-10, 10], 0.2, (5, 2))
    lost = rng.normal(0, 1, (10, 2))
    X = np.vstack([maj, big, small, lost])
    y = np.r_[np.zeros(300, int), np.ones(30, int)]
    s = SMOM(random_state=0)
    s.fit_resample(X, y)
    out = s.outstanding_[1]
    assert out[:15].all() and not out[15:].any()


def test_self_direction_replicates():
    """Minority points spread inside the majority cloud: no PN neighborhood is clean, so every
    minority instance gets its own direction (Step 6.1) and some synthetic rows are copies."""
    rng = np.random.default_rng(6)
    maj = rng.uniform(-1, 1, (2000, 2))
    mnr = rng.uniform(-0.8, 0.8, (12, 2))
    X = np.vstack([maj, mnr])
    y = np.r_[np.zeros(2000, int), np.ones(12, int)]
    s = SMOM(random_state=0)
    Xr, yr = s.fit_resample(X, y)
    assert s.class_info_[1]["n_self_direction"] == 12
    syn = Xr[y.size:]
    copies = (np.abs(syn[:, None, :] - mnr[None]).max(axis=2) == 0).any(axis=1)
    assert 0 < copies.sum() < syn.shape[0]


def test_dict_strategy_and_string_labels():
    X, y = two_class(seed=7)
    labels = np.where(y == 1, "pos", "neg")
    Xr, yr = SMOM(sampling_strategy={"pos": 100}, random_state=0).fit_resample(X, labels)
    assert Xr.shape[0] == y.size + 60 and np.all(yr[y.size:] == "pos")


def test_metric_choice_irrelevant_after_zscore():
    X, y = two_class(seed=8)
    Xz = (X - X.mean(0)) / X.std(0)
    a = SMOM(metric="seuclidean", random_state=0).fit_resample(Xz, y)[0]
    b = SMOM(metric="euclidean", random_state=0).fit_resample(Xz, y)[0]
    assert np.allclose(a, b)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} tests passed")
