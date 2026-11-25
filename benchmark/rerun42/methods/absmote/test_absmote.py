"""Quick checks for absmote.ABSMOTE. Run: python3 -I test_absmote.py (or pytest)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from absmote import ABSMOTE  # noqa: E402

ABALONE = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/abalone9-18.dat"


def _toy(n_maj=200, n_min=30, seed=0, d=4):
    """Overlapping two-class data: plenty of safe, borderline and noise minority points."""
    r = np.random.RandomState(seed)
    X = np.vstack([r.normal(0, 1, (n_maj, d)), r.normal(1.0, 1, (n_min, d))])
    y = np.array([0] * n_maj + [1] * n_min)
    return X, y


def _brute_border(X, y, M, rule):
    """Independent M' computation by a full stable sort per minority row."""
    mino = np.flatnonzero(y == 1)
    out = []
    for i in mino:
        d = ((X - X[i]) ** 2).sum(1)
        if rule != "authors_code":
            d[i] = np.inf
        nn = np.argsort(d, kind="stable")[:M]
        mp = int(np.sum(y[nn] == 0))
        if rule == "text":
            ok = M / 2 <= mp < M
        elif rule == "figure":
            ok = M / 2 < mp < M
        else:
            ok = M // 2 <= mp < M
        if ok:
            out.append(i)
    return np.array(out, dtype=int)


def test_original_rows_and_labels_unchanged():
    X, y = _toy()
    Xr, yr = ABSMOTE(random_state=0).fit_resample(X, y)
    assert np.array_equal(Xr[:len(X)], X)
    assert np.array_equal(yr[:len(y)], y)
    assert set(np.unique(yr[len(y):])) <= {1}
    assert yr.dtype == y.dtype and Xr.dtype == np.float64


def test_borderline_set_matches_bruteforce():
    X, y = _toy()
    for rule in ("text", "figure", "authors_code"):
        for M in (5, 8):
            s = ABSMOTE(m_neighbors=M, borderline_rule=rule, random_state=0)
            s.fit_resample(X, y)
            assert np.array_equal(s.borderline_indices_, _brute_border(X, y, M, rule)), (rule, M)


def test_number_of_synthetic_rows():
    X, y = _toy()
    s = ABSMOTE(random_state=1)
    Xr, yr = s.fit_resample(X, y)
    nb = len(s.borderline_indices_)
    assert nb >= 2
    assert len(Xr) - len(X) == nb == s.n_synthetic_          # 100%: one per borderline seed
    for pct, expect in ((0, 0), (200, 2 * nb), (250, 2 * nb + int(0.5 * nb)), (50, int(0.5 * nb))):
        s = ABSMOTE(percentage=pct, random_state=1)
        Xr, yr = s.fit_resample(X, y)
        assert len(Xr) - len(X) == expect, (pct, expect, len(Xr) - len(X))


def test_partners_are_borderline_neighbors_and_points_on_segments():
    X, y = _toy()
    s = ABSMOTE(k_neighbors=5, random_state=2)
    Xr, _ = s.fit_resample(X, y)
    new = Xr[len(X):]
    border = set(s.borderline_indices_.tolist())
    pos = {r: i for i, r in enumerate(s.borderline_indices_)}
    for x, a, b, g in zip(new, s.seed_indices_, s.partner_indices_, s.gaps_):
        assert a in border and b in border and a != b
        assert b in s.borderline_neighbors_[pos[a]]
        assert 0.0 <= g[0] < 1.0
        assert np.allclose(x, X[a] + g[0] * (X[b] - X[a]))
    # neighbors are the k nearest borderline points (not all minority points)
    B = s.borderline_indices_
    for i, r in enumerate(B):
        d = ((X[B] - X[r]) ** 2).sum(1)
        d[i] = np.inf
        assert np.array_equal(s.borderline_neighbors_[i], B[np.argsort(d, kind="stable")[:s.k_eff_]])
    # per-feature gaps: inside the box spanned by seed and partner
    s = ABSMOTE(gap="per_feature", random_state=2)
    Xr, _ = s.fit_resample(X, y)
    for x, a, b in zip(Xr[len(X):], s.seed_indices_, s.partner_indices_):
        lo, hi = np.minimum(X[a], X[b]), np.maximum(X[a], X[b])
        assert np.all(x >= lo - 1e-12) and np.all(x <= hi + 1e-12)


def test_same_random_state_same_output():
    X, y = _toy()
    a = ABSMOTE(random_state=7).fit_resample(X, y)
    b = ABSMOTE(random_state=7).fit_resample(X, y)
    c = ABSMOTE(random_state=8).fit_resample(X, y)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])


def test_no_nan():
    X, y = _toy(seed=3)
    for rule in ("text", "figure", "authors_code"):
        for gap in ("scalar", "per_feature"):
            Xr, yr = ABSMOTE(borderline_rule=rule, gap=gap, random_state=0).fit_resample(X, y)
            assert np.all(np.isfinite(Xr))


def test_seven_minority_examples():
    X, y = _toy(n_maj=60, n_min=7, seed=4)
    for M, k in ((5, 5), (5, 8), (8, 5), (8, 8)):
        s = ABSMOTE(m_neighbors=M, k_neighbors=k, random_state=0)
        Xr, yr = s.fit_resample(X, y)
        nb = len(s.borderline_indices_)
        assert len(Xr) - len(X) == (nb if nb >= 2 else 0)
        assert s.k_eff_ == (min(k, nb - 1) if nb >= 2 else 0)
        assert np.all(np.isfinite(Xr)) and np.array_equal(Xr[:len(X)], X)


def test_no_or_one_borderline_point_gives_no_new_rows():
    r = np.random.RandomState(5)
    X = np.vstack([r.normal(0, 0.1, (50, 2)), r.normal(10, 0.1, (7, 2))])   # separated
    y = np.array([0] * 50 + [1] * 7)
    s = ABSMOTE(random_state=0)
    Xr, yr = s.fit_resample(X, y)
    assert len(s.borderline_indices_) == 0 and len(Xr) == len(X)
    # 1-D: a safe minority cluster A near 7.2 and one minority point q at 6.0 whose five
    # nearest rows are three majority rows (4.9, 4.95, 4.97) and two rows of A: M' = 3.
    maj = np.concatenate([np.linspace(0.0, 4.8, 40), [4.9, 4.95, 4.97]])
    A = 7.2 + 0.01 * np.arange(6)
    X1 = np.concatenate([maj, A, [6.0]])[:, None]
    y1 = np.array([0] * len(maj) + [1] * len(A) + [1])
    s = ABSMOTE(random_state=0)
    Xr, _ = s.fit_resample(X1, y1)
    assert s.borderline_indices_.tolist() == [len(X1) - 1]
    assert s.n_synthetic_ == 0 and len(Xr) == len(X1)


def test_text_and_figure_rules_differ_only_at_half():
    # minority point with exactly M/2 = 4 majority among its 8 neighbors
    X = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [-0.1], [-0.2], [-0.3], [-0.4], [5.0], [5.1], [5.2]])
    y = np.array([1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0])
    t = ABSMOTE(m_neighbors=8, borderline_rule="text", random_state=0)
    f = ABSMOTE(m_neighbors=8, borderline_rule="figure", random_state=0)
    t.fit_resample(X, y)
    f.fit_resample(X, y)
    m = dict(zip(t.minority_indices_.tolist(), t.m_prime_.tolist()))
    assert m[0] == 4
    assert 0 in t.borderline_indices_ and 0 not in f.borderline_indices_


def test_two_classes_required():
    X, y = _toy()
    y3 = y.copy()
    y3[:10] = 2
    try:
        ABSMOTE().fit_resample(X, y3)
    except ValueError:
        pass
    else:
        raise AssertionError("three classes should raise")


def test_authors_code_rule_reproduces_paper_gen_counts():
    """Table IV (p.34): Gen 40 for M=5 and 39 for M=8 on Abalone9-18 (WEKA distance)."""
    if not os.path.exists(ABALONE):
        print("  (skipped: KEEL abalone9-18 not found)")
        return
    from weka_replica import vdm_embedding
    rows = [[c.strip() for c in ln.split(",")] for ln in open(ABALONE) if ln.strip()]
    sexes = list(dict.fromkeys(r[0] for r in rows))
    codes = np.array([sexes.index(r[0]) for r in rows])
    y = np.array([1 if r[-1] == "positive" else 0 for r in rows])
    num = np.array([[float(v) for v in r[1:-1]] for r in rows])
    X = np.hstack([vdm_embedding(codes, y, len(sexes)), num])
    for M, gen in ((5, 40), (8, 39)):
        s = ABSMOTE(m_neighbors=M, borderline_rule="authors_code", random_state=0)
        Xr, _ = s.fit_resample(X, y)
        assert len(Xr) - len(X) == gen, (M, len(Xr) - len(X))


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("ok  ", t.__name__)
    print(f"{len(tests)} tests passed")
