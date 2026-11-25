"""Scratch: structural variants of the authors' WEKA-SMOTE modification vs Table IV rows 3.0-3.3, 4.0-4.3."""
import sys, math, itertools
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote")
import numpy as np
from weka_replica import (JavaRandom, weka_cv_confusion, recall_f, _vdm_tables, _weka_dist)

RAW = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/"
rows = [[c.strip() for c in ln.split(",")] for ln in open(RAW + "abalone9-18.dat") if ln.strip()]
order, labs = [], []
for r in rows:
    if r[0] not in order: order.append(r[0])
    if r[-1] not in labs: labs.append(r[-1])
X = np.array([[order.index(r[0])] + [float(v) for v in r[1:-1]] for r in rows])
y = np.array([labs.index(r[-1]) for r in rows]); pos = labs.index("positive")
nominal, nv = [True] + [False] * 7, [3] + [0] * 7
vdm = _vdm_tables(X, y, nominal, nv, 2)
mino = np.where(y == pos)[0]
PAPER = {("bsmote", 5, 5): (40, 34, 18), ("bsmote", 5, 8): (40, 34, 17), ("bsmote", 8, 5): (39, 38, 26),
         ("bsmote", 8, 8): (39, 32, 16), ("absmote", 5, 5): (40, 35, 25), ("absmote", 5, 8): (40, 36, 18),
         ("absmote", 8, 5): (39, 35, 19), ("absmote", 8, 8): (39, 40, 22)}


def borderline(M, det):
    out = []
    for i_s, i in enumerate(mino):
        d = _weka_dist(X[i], X, nominal, vdm)
        if det == "self_in":
            pass
        elif det == "skip_is":            # i != j with i = minority-sample index, j = data index
            d[i_s] = np.inf
        o = np.argsort(d, kind="stable")[:M]
        mp = int(np.sum(y[o] != pos))
        if mp >= M // 2 and mp < M:
            out.append(i)
    return np.array(out)


def generate(method, M, k, det, loop, excl, seed=1):
    B = borderline(M, det)
    pool = mino if method == "bsmote" else B
    k_eff = k if len(pool) > k else len(pool) - 1
    rand = JavaRandom(seed)
    synth = []
    seeds = mino if loop == "sample" else B
    for i_loop, i in enumerate(seeds):
        if i not in set(B.tolist()):
            continue
        if excl == "identity":
            cand = pool[pool != i]
        elif excl == "index":            # skip pool[j] where j == i_loop
            cand = np.delete(pool, i_loop) if i_loop < len(pool) else pool.copy()
        elif excl == "none":
            cand = pool.copy()
        d = _weka_dist(X[i], X[cand], nominal, vdm)
        nn = cand[np.argsort(d, kind="stable")[:k_eff]]
        new = np.zeros(X.shape[1])
        pick = nn[rand.next_int(k_eff)]
        for a, nom in enumerate(nominal):
            if nom:
                vc = np.zeros(nv[a], dtype=int)
                vc[int(X[i, a])] += 1
                for r in nn:
                    vc[int(X[r, a])] += 1
                new[a] = int(np.argmax(vc))
            else:
                gap = rand.next_double()
                new[a] = X[i, a] + gap * (X[pick, a] - X[i, a])
        synth.append(new)
    Xs = np.array(synth)
    return np.vstack([X, Xs]), np.concatenate([y, np.full(len(Xs), pos)])


if __name__ == "__main__":
  results = []
  for det, loop, excl in itertools.product(("self_in", "skip_is"), ("borderline", "sample"),
                                           ("identity", "index", "none")):
      hits, cells = 0, []
      for (meth, M, k), (g, tp, fp) in PAPER.items():
          Xr, yr = generate(meth, M, k, det, loop, excl)
          c = weka_cv_confusion(Xr, yr, nominal, nv, pos=pos)
          ok = (len(yr) - len(y), c["tp"], c["fp"]) == (g, tp, fp)
          hits += ok
          cells.append(f"{meth[:2]}{M}{k}:{c['tp']}/{c['fp']}{'*' if ok else ''}")
      results.append((hits, det, loop, excl, cells))
      print(hits, det, loop, excl, " ".join(cells), flush=True)
  print("paper: bs55 34/18 bs58 34/17 bs85 38/26 bs88 32/16 ab55 35/25 ab58 36/18 ab85 35/19 ab88 40/22")
