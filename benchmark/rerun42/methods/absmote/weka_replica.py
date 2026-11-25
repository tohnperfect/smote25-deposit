"""Python re-creations of the WEKA pieces the AB-SMOTE paper ran (validation only).

The paper evaluated with WEKA (Sec. IV, p.33, ref. [11]): the oversampler was applied to
the whole dataset, then J48 was cross-validated with 5 folds and WEKA's pooled confusion
matrix gave recall and F-measure of the minority class (Sec. IV, p.34). The recall values
in Tables IV-X are exact fractions over (original minority + Gen), which shows that the
synthetic rows were part of the test folds. This module re-creates, from the published
WEKA algorithms and written from scratch here (no WEKA code is downloaded or run):

* ``JavaRandom``: java.util.Random (48-bit LCG), used by WEKA for every random step.
* ``weka_cv_folds``: Instances.randomize(Random(seed)), Instances.stratify(folds),
  Instances.testCV(folds, i), as in the Explorer's cross-validation.
* ``J48``: WEKA's C4.5 release 8 tree with its defaults (-C 0.25 -M 2): gain ratio with
  the average-gain filter, MDL-corrected thresholds for numeric attributes, multiway
  splits for nominal attributes, collapsing, pessimistic pruning with subtree raising.
* ``weka_smote_family``: WEKA's SMOTE filter (raw numeric distances plus VDM for nominal
  attributes, nominal values by majority vote, java.util.Random streams), with the
  borderline subset and the borderline-only partner pool that the AB-SMOTE authors
  added to it, as inferred from the paper's Gen counts (see VALIDATION.md).

None of this is used by absmote.py, which depends on NumPy, SciPy and scikit-learn only.
"""
import math

import numpy as np
from scipy.special import ndtri

SMALL = 1e-6          # weka.core.Utils.SMALL
LN2 = math.log(2.0)


# == RNG ==
class JavaRandom:
    """java.util.Random: seed scramble, next(bits), nextInt(bound), nextDouble()."""

    _MULT = 0x5DEECE66D
    _ADD = 0xB
    _MASK = (1 << 48) - 1

    def __init__(self, seed):
        self._seed = (int(seed) ^ self._MULT) & self._MASK

    def _next(self, bits):
        self._seed = (self._seed * self._MULT + self._ADD) & self._MASK
        return self._seed >> (48 - bits)

    def next_int(self, bound):
        r = self._next(31)
        m = bound - 1
        if (bound & m) == 0:                      # power of two
            return (bound * r) >> 31
        u = r
        while True:
            r = u % bound
            if u - r + m < (1 << 31):             # no 32-bit overflow in Java
                return r
            u = self._next(31)

    def next_double(self):
        return ((self._next(26) << 27) + self._next(27)) * (1.0 / (1 << 53))


# == cross-validation ==
def weka_cv_folds(y, n_folds=5, seed=1):
    """Test-fold row indices exactly as WEKA's Explorer builds them.

    randomize: for j = n-1..1 swap(j, rand.nextInt(j+1)); stratify: group rows of the
    same class in order of first appearance, then take every n_folds-th row (stratStep);
    testCV: contiguous blocks, the first (n mod n_folds) folds one row longer.
    """
    n = len(y)
    order = list(range(n))
    rand = JavaRandom(seed)
    for j in range(n - 1, 0, -1):
        k = rand.next_int(j + 1)
        order[j], order[k] = order[k], order[j]
    # Instances.stratify (nominal class)
    index = 1
    while index < n:
        c1 = y[order[index - 1]]
        for j in range(index, n):
            if y[order[j]] == c1:
                order[index], order[j] = order[j], order[index]
                index += 1
        index += 1
    # stratStep
    new = []
    start = 0
    while len(new) < n:
        j = start
        while j < n:
            new.append(order[j])
            j += n_folds
        start += 1
    order = new
    folds = []
    for f in range(n_folds):
        num = n // n_folds
        if f < n % n_folds:
            num += 1
            offset = f
        else:
            offset = n % n_folds
        first = f * (n // n_folds) + offset
        folds.append(np.array(order[first:first + num], dtype=int))
    return folds


# == J48 ==
def _lnf(x):
    """x * ln(x) with WEKA's cut-off (0 below 1e-6), vectorized."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    m = x >= 1e-6
    out[m] = x[m] * np.log(x[m])
    return out


def _old_ent(per_class):
    per_class = np.asarray(per_class, dtype=float)
    return float((_lnf(per_class.sum()) - _lnf(per_class).sum()) / LN2)


def _new_ent(bags):
    bags = np.asarray(bags, dtype=float)
    s = _lnf(bags).sum() - _lnf(bags.sum(1)).sum()
    return float(-s / LN2)


def _split_ent(bags, total):
    per_bag = np.asarray(bags, dtype=float).sum(1)
    if not per_bag.sum() > SMALL:
        return 0.0
    s = -_lnf(per_bag).sum() - float(_lnf(total - per_bag.sum())) + float(_lnf(total))
    return float(s / LN2)


def _eq(a, b):
    return a == b or (a - b < SMALL and b - a < SMALL)


def _gain_ratio(bags, total, info_gain):
    den = _split_ent(bags, total)
    if _eq(den, 0.0):
        return 0.0
    return info_gain / (den / total)


def _max_class(per_class):
    best, idx = 0.0, 0
    for i, c in enumerate(per_class):
        if c - best > SMALL:
            best, idx = c, i
    return idx


def _num_incorrect(dist):
    pc = np.asarray(dist, dtype=float).reshape(-1, dist.shape[-1]).sum(0)
    return float(pc.sum() - pc[_max_class(pc)])


def _add_errs(N, e, CF=0.25):
    """weka.classifiers.trees.j48.Stats.addErrs."""
    if e < 1:
        base = N * (1 - CF ** (1.0 / N))
        if e == 0:
            return base
        return base + e * (_add_errs(N, 1, CF) - base)
    if e + 0.5 >= N:
        return max(N - e, 0.0)
    z = float(ndtri(1 - CF))
    f = (e + 0.5) / N
    r = (f + z * z / (2 * N) + z * math.sqrt(f / N - f * f / N + z * z / (4 * N * N))) / (1 + z * z / N)
    return r * N - e


def _est_errors(dist, CF):
    dist = np.asarray(dist, dtype=float)
    tot = float(dist.sum())
    if _eq(tot, 0.0):
        return 0.0
    e = _num_incorrect(dist)
    return e + _add_errs(tot, e, CF)


class _Node:
    __slots__ = ("train", "is_leaf", "is_empty", "attr", "split_point", "dist", "sons")


class J48:
    """WEKA J48 (C4.5 release 8) with default options -C 0.25 -M 2.

    ``nominal[a]`` marks nominal attributes (integer codes 0..n_values[a]-1 in X);
    ``y`` holds class indices 0..n_classes-1 in the order of the ARFF declaration.
    """

    def __init__(self, nominal, n_values, n_classes=2, cf=0.25, min_obj=2,
                 subtree_raising=True, collapse=True, prune=True):
        self.nominal = list(nominal)
        self.n_values = list(n_values)
        self.C = n_classes
        self.cf = cf
        self.min_obj = min_obj
        self.subtree_raising = subtree_raising
        self.collapse_tree = collapse
        self.prune_tree = prune

    # -- split search (C45Split / C45ModelSelection)
    def _numeric(self, idx, a, N):
        v_all = self.X[idx, a]
        o = np.argsort(v_all, kind="stable")
        v = v_all[o]
        yy = self.y[idx][o]
        C = self.C
        min_split = 0.1 * N / C
        if min_split - self.min_obj < SMALL:
            min_split = float(self.min_obj)
        elif min_split - 25 > SMALL:
            min_split = 25.0
        if 2 * min_split - N > SMALL:
            return None
        onehot = np.zeros((N, C))
        onehot[np.arange(N), yy] = 1.0
        cum = np.vstack([np.zeros(C), np.cumsum(onehot, 0)])
        total = cum[-1]
        default_ent = _old_ent(total)
        nxt = np.where(v[:-1] + 1e-5 < v[1:])[0] + 1
        if len(nxt) == 0:
            return None
        left = cum[nxt]
        right = total - left
        nl, nr = left.sum(1), right.sum(1)
        ok = ((min_split - nl < SMALL) | (nl >= min_split)) & ((min_split - nr < SMALL) | (nr >= min_split))
        m_index = int(ok.sum())
        if m_index == 0:
            return None
        # newEnt for every candidate, vectorized
        new_ent = -(_lnf(left).sum(1) - _lnf(nl) + _lnf(right).sum(1) - _lnf(nr)) / LN2
        num = default_ent - new_ent
        gains = np.where((np.abs(num) < SMALL) | (num == 0), 0.0, num / N)
        best, split_index = 0.0, -1
        for g, p, k in zip(gains, nxt, ok):
            if k and g - best > SMALL:
                best, split_index = float(g), int(p) - 1
        info_gain = best - math.log2(m_index) / N
        if info_gain - 0.0 < SMALL:
            return None
        sp = (v[split_index + 1] + v[split_index]) / 2.0
        if sp == v[split_index + 1]:
            sp = v[split_index]
        bags = np.vstack([cum[split_index + 1], total - cum[split_index + 1]])
        return info_gain, _gain_ratio(bags, N, info_gain), sp, bags

    def _nominal(self, idx, a, N):
        codes = self.X[idx, a].astype(int)
        bags = np.zeros((self.n_values[a], self.C))
        np.add.at(bags, (codes, self.y[idx]), 1.0)
        per_bag = bags.sum(1)
        if int(np.sum((self.min_obj - per_bag < SMALL) | (per_bag >= self.min_obj))) <= 1:
            return None
        num = _old_ent(bags.sum(0)) - _new_ent(bags)
        info_gain = 0.0 if _eq(num, 0.0) else num / N
        return info_gain, _gain_ratio(bags, N, info_gain), None, bags

    def _select(self, idx):
        N = len(idx)
        counts = np.bincount(self.y[idx], minlength=self.C).astype(float)
        if 2 * self.min_obj - N > SMALL or _eq(N, counts.max() if N else 0.0):
            return None
        n_all = self.X.shape[0]
        multi_val = True
        for a in range(self.d):
            if (not self.nominal[a]) or (0.3 * n_all - self.n_values[a] > SMALL):
                multi_val = False
                break
        models, avg, valid = [], 0.0, 0
        for a in range(self.d):
            m = self._nominal(idx, a, N) if self.nominal[a] else self._numeric(idx, a, N)
            models.append(m)
            if m is not None:
                if (not self.nominal[a]) or multi_val or (0.3 * n_all - self.n_values[a] > SMALL):
                    avg += m[0]
                    valid += 1
        if valid == 0:
            return None
        avg /= valid
        best, min_result = None, 0.0
        for a, m in enumerate(models):
            if m is not None and m[0] >= avg - 1e-3 and m[1] - min_result > SMALL:
                best, min_result = (a, m), m[1]
        if best is None or _eq(min_result, 0.0):
            return None
        a, (ig, gr, sp, bags) = best
        if not self.nominal[a]:
            # C45Split.setSplitPoint: largest training value not above the midpoint
            col = self.X[:, a]
            cand = col[col - sp < SMALL]
            new_sp = -np.finfo(float).max
            for t in cand:
                if t - new_sp > SMALL:
                    new_sp = t
            sp = float(new_sp)
        return a, sp, bags

    def _subsets(self, node, idx):
        a = node.attr
        if self.nominal[a]:
            codes = self.X[idx, a].astype(int)
            return [idx[codes == v] for v in range(self.n_values[a])]
        left = self.X[idx, a] - node.split_point < SMALL
        return [idx[left], idx[~left]]

    def _dist_for(self, node, idx):
        if node.is_leaf:
            return np.bincount(self.y[idx], minlength=self.C).astype(float)[None, :]
        return np.vstack([np.bincount(self.y[s], minlength=self.C).astype(float)
                          for s in self._subsets(node, idx)])

    def _build(self, idx):
        node = _Node()
        node.train = idx
        node.is_empty = False
        node.sons = None
        sel = self._select(idx)
        if sel is None:
            node.is_leaf = True
            node.attr = None
            node.split_point = None
            node.dist = np.bincount(self.y[idx], minlength=self.C).astype(float)[None, :]
            node.is_empty = len(idx) == 0
            return node
        node.is_leaf = False
        node.attr, node.split_point, node.dist = sel
        node.sons = [self._build(s) for s in self._subsets(node, idx)]
        return node

    # -- collapse and prune (C45PruneableClassifierTree)
    def _training_errors(self, node):
        if node.is_leaf:
            return _num_incorrect(node.dist)
        return sum(self._training_errors(s) for s in node.sons)

    def _collapse(self, node):
        if node.is_leaf:
            return
        if self._training_errors(node) >= _num_incorrect(node.dist) - 1e-3:
            node.sons = None
            node.is_leaf = True
        else:
            for s in node.sons:
                self._collapse(s)

    def _estimated_errors(self, node):
        if node.is_leaf:
            return _est_errors(node.dist, self.cf)
        return sum(self._estimated_errors(s) for s in node.sons)

    def _estimated_errors_for_branch(self, node, idx):
        if node.is_leaf:
            return _est_errors(np.bincount(self.y[idx], minlength=self.C).astype(float), self.cf)
        return sum(self._estimated_errors_for_branch(s, sub)
                   for s, sub in zip(node.sons, self._subsets(node, idx)))

    def _new_distribution(self, node, idx):
        node.dist = self._dist_for(node, idx)
        node.train = idx
        if not node.is_leaf:
            for s, sub in zip(node.sons, self._subsets(node, idx)):
                self._new_distribution(s, sub)
        elif len(idx) > 0:
            node.is_empty = False

    def _prune(self, node):
        if node.is_leaf:
            return
        for s in node.sons:
            self._prune(s)
        per_bag = node.dist.sum(1)
        i_large, mx = -1, 0.0
        for i, b in enumerate(per_bag):             # Distribution.maxBag: last max
            if (mx - b < SMALL) or b >= mx:
                mx, i_large = b, i
        if self.subtree_raising:
            e_branch = self._estimated_errors_for_branch(node.sons[i_large], node.train)
        else:
            e_branch = np.finfo(float).max
        e_leaf = _est_errors(node.dist, self.cf)
        e_tree = self._estimated_errors(node)
        if e_leaf - (e_tree + 0.1) < SMALL and e_leaf - (e_branch + 0.1) < SMALL:
            node.sons = None
            node.is_leaf = True
            return
        if e_branch - (e_tree + 0.1) < SMALL:
            big = node.sons[i_large]
            node.sons = big.sons
            node.attr = big.attr
            node.split_point = big.split_point
            node.is_leaf = big.is_leaf
            self._new_distribution(node, node.train)
            self._prune(node)

    # -- public API
    def fit(self, X, y):
        self.X = np.asarray(X, dtype=float)
        self.y = np.asarray(y, dtype=int)
        self.d = self.X.shape[1]
        self.root = self._build(np.arange(len(self.y)))
        if self.collapse_tree:
            self._collapse(self.root)
        if self.prune_tree:
            self._prune(self.root)
        return self

    def _probs(self, x):
        node = self.root
        while not node.is_leaf:
            a = node.attr
            if self.nominal[a]:
                sub = int(x[a])
            else:
                sub = 0 if x[a] - node.split_point < SMALL else 1
            son = node.sons[sub]
            if son.is_empty:
                bag = node.dist[sub]
                if bag.sum() > SMALL:
                    return bag / bag.sum()
                pc = node.dist.sum(0)
                return pc / pc.sum() if pc.sum() > 0 else np.zeros(self.C)
            node = son
        pc = node.dist.sum(0)
        return pc / pc.sum() if not _eq(pc.sum(), 0.0) else np.zeros(self.C)

    def predict(self, X):
        """Class index per row (first maximum, as Utils.maxIndex); -1 if unclassified."""
        out = []
        for x in np.asarray(X, dtype=float):
            p = self._probs(x)
            k = int(np.argmax(p))                    # first maximum
            out.append(k if p[k] > 0 else -1)
        return np.array(out, dtype=int)

    def n_leaves(self, node=None):
        node = self.root if node is None else node
        return 1 if node.is_leaf else sum(self.n_leaves(s) for s in node.sons)


def weka_cv_confusion(X, y, nominal, n_values, pos=0, n_folds=5, seed=1, n_classes=2):
    """Pooled confusion counts of J48 under WEKA's Explorer cross-validation."""
    folds = weka_cv_folds(y, n_folds, seed)
    n = len(y)
    tp = fp = fn = tn = unc = 0
    for test in folds:
        mask = np.ones(n, dtype=bool)
        mask[test] = False
        tree = J48(nominal, n_values, n_classes).fit(X[mask], y[mask])
        pred = tree.predict(X[test])
        yt = y[test]
        unc += int(np.sum(pred < 0))
        ok = pred >= 0
        tp += int(np.sum(ok & (pred == pos) & (yt == pos)))
        fp += int(np.sum(ok & (pred == pos) & (yt != pos)))
        fn += int(np.sum(ok & (pred != pos) & (yt == pos)))
        tn += int(np.sum(ok & (pred != pos) & (yt != pos)))
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, unclassified=unc)


def recall_f(c):
    rec = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0
    prec = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0
    f = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return rec, f


# == WEKA SMOTE-family filter ==
def vdm_embedding(codes, y, n_values):
    """Columns whose squared Euclidean distances equal WEKA's VDM for one nominal attribute.

    WEKA's SMOTE filter adds VDM(u, v) = sum_c |P(c|u) - P(c|v)| (unsquared) to the sum of
    squared numeric differences. With two classes VDM(u, v) = 2 |p_u - p_v|, p = P(class 0
    | value): sorting the values by p and stepping along orthogonal axes by
    sqrt(2 (p_next - p)) gives points whose squared distances are exactly the VDM values.
    """
    codes = np.asarray(codes, dtype=int)
    y = np.asarray(y, dtype=int)
    labels = np.unique(y)
    if len(labels) != 2:
        raise ValueError("the staircase embedding is exact for two classes only")
    p = np.zeros(n_values)
    for v in range(n_values):
        m = codes == v
        p[v] = np.mean(y[m] == labels[0]) if m.any() else 0.0
    order = np.argsort(p, kind="stable")
    steps = np.sqrt(2.0 * np.diff(p[order]))
    E = np.zeros((n_values, max(n_values - 1, 1)))
    for rank, v in enumerate(order):
        E[v, :rank] = steps[:rank]
    return E[codes]


def _vdm_tables(X, y, nominal, n_values, n_classes):
    tabs = {}
    for a, nom in enumerate(nominal):
        if not nom:
            continue
        V = n_values[a]
        codes = X[:, a].astype(int)
        cnt = np.bincount(codes, minlength=V).astype(float)
        by = np.zeros((n_classes, V))
        np.add.at(by, (y, codes), 1.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            P = by / cnt                              # P(class | value), NaN for unused values
        tabs[a] = np.abs(P[:, :, None] - P[:, None, :]).sum(0)
    return tabs


def _weka_dist(xi, Xj, nominal, vdm):
    d2 = np.zeros(len(Xj))
    for a, nom in enumerate(nominal):
        if nom:
            d2 += vdm[a][int(xi[a]), Xj[:, a].astype(int)]
        else:
            d2 += (Xj[:, a] - xi[a]) ** 2
    return np.sqrt(d2)


def weka_borderline(X, y, minority, M, nominal, vdm, rule="authors_code", skip_quirk=True):
    """Minority rows whose M-nearest-neighbor count of majority rows M' marks them as danger.

    rule="authors_code": the seed is one of its own M neighbors (distance 0, ties by row
    order) and the bound is Java's integer M/2, i.e. M/2 <= M' < M with M/2 = floor(M/2).
    With skip_quirk, the data row whose index equals the seed's position among the
    minority rows is skipped instead of the seed (a WEKA-style "if (i != j)" test with i
    indexing the minority rows and j the whole data); this only matters with ties and is
    needed for Haberman's Gen = 65 (Table VI) in UCI row order.
    rule="text": the seed is excluded and M/2 <= M' < M with real M/2 (Sec. II.B, III).
    """
    out = []
    for i_s, i in enumerate(np.where(y == minority)[0]):
        d = _weka_dist(X[i], X, nominal, vdm)
        if rule == "text":
            d[i] = np.inf
        elif skip_quirk:
            d[i_s] = np.inf
        o = np.argsort(d, kind="stable")[:M]
        mp = int(np.sum(y[o] != minority))
        if rule == "text":
            ok = (mp >= M / 2.0) and (mp < M)
        else:
            ok = (mp >= M // 2) and (mp < M)
        if ok:
            out.append(i)
    return np.array(out, dtype=int)


def weka_smote_family(X, y, nominal, n_values, method="smote", k=5, M=5, percentage=100.0,
                      seed=1, gap_per_attribute=True, rule="authors_code", n_classes=2,
                      index_exclusion=True, skip_quirk=True):
    """WEKA SMOTE filter and the authors' BSMOTE / AB-SMOTE variants of it.

    method: "smote" (seeds and partners: all minority rows), "bsmote" (seeds: borderline
    rows, partners: all minority rows), "absmote" (seeds and partners: borderline rows).
    index_exclusion: the partner search skips the pool row at the seed's position in the
    seed list (WEKA's "if (i != j)"), which is the seed itself for SMOTE and AB-SMOTE but
    an unrelated minority row for BSMOTE; this reproduces Table IV rows 3.1 and 3.3.
    Returns (X_res, y_res, seeds) with the original rows first, as the filter outputs them.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    counts = np.bincount(y, minlength=n_classes)
    minority = int(np.argmin(np.where(counts > 0, counts, np.iinfo(int).max)))
    vdm = _vdm_tables(X, y, nominal, n_values, n_classes)
    mino = np.where(y == minority)[0]
    if method == "smote":
        seeds, pool = mino, mino
    else:
        seeds = weka_borderline(X, y, minority, M, nominal, vdm, rule, skip_quirk)
        pool = mino if method == "bsmote" else seeds
    if len(pool) <= k:
        k_eff = len(pool) - 1
    else:
        k_eff = k
    if k_eff < 1 or len(seeds) == 0:
        return X.copy(), y.copy(), seeds
    rand = JavaRandom(seed)
    frac = percentage / 100.0 - math.floor(percentage / 100.0)
    n_extra = int(frac * len(seeds))
    extra = list(range(len(seeds))) if n_extra >= 1 else []
    for i in range(len(extra), 1, -1):                # Collections.shuffle(list, rand)
        j = rand.next_int(i)
        extra[i - 1], extra[j] = extra[j], extra[i - 1]
    extra = set(extra[:n_extra])
    synth = []
    for si, i in enumerate(seeds):
        if index_exclusion:
            cand = np.delete(pool, si) if si < len(pool) else pool.copy()
        else:
            cand = pool[pool != i]
        d = _weka_dist(X[i], X[cand], nominal, vdm)
        nn = cand[np.argsort(d, kind="stable")[:k_eff]]
        n = int(math.floor(percentage / 100.0))
        while n > 0 or (si in extra):
            if n <= 0:
                extra.discard(si)
            new = np.zeros(X.shape[1])
            pick = nn[rand.next_int(k_eff)]
            g = None if gap_per_attribute else rand.next_double()
            for a, nom in enumerate(nominal):
                if nom:
                    vc = np.zeros(n_values[a], dtype=int)
                    vc[int(X[i, a])] += 1
                    for r in nn:
                        vc[int(X[r, a])] += 1
                    new[a] = int(np.argmax(vc))     # first maximum
                else:
                    gap = rand.next_double() if gap_per_attribute else g
                    new[a] = X[i, a] + gap * (X[pick, a] - X[i, a])
            synth.append(new)
            n -= 1
    Xs = np.array(synth).reshape(-1, X.shape[1])
    return (np.vstack([X, Xs]), np.concatenate([y, np.full(len(Xs), minority)]), seeds)
