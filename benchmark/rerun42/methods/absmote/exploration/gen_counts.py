"""Scratch: which reading of the borderline rule reproduces the paper's Gen counts?

Gen = number of synthetic rows at percentage 100 = |P'| (one per borderline seed).
Paper: Table IV (abalone9-18) Gen 40 (M=5), 39 (M=8); Table VI (haberman) 65 / 61;
Table IX (flare) 39 / 41; Table X (wine quality red 4) 53 / 53.
"""
import numpy as np

RAW = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/"
PAPER = {"abalone9-18": (40, 39), "haberman": (65, 61), "flare-F": (39, 41),
         "winequality-red-4": (53, 53)}


def load(name):
    rows = [ln.strip().split(",") for ln in open(RAW + name + ".dat") if ln.strip()]
    rows = [[c.strip() for c in r] for r in rows]
    y = np.array([1 if r[-1] == "positive" else 0 for r in rows])
    cols = list(zip(*[r[:-1] for r in rows]))
    num, nom = [], []
    for c in cols:
        try:
            num.append(np.array([float(v) for v in c]))
        except ValueError:
            nom.append(np.array(c))
    Xn = np.column_stack(num) if num else np.zeros((len(y), 0))
    return Xn, nom, y


def vdm_matrix(col, y):
    vals = sorted(set(col))
    idx = np.array([vals.index(v) for v in col])
    P = np.zeros((len(vals), 2))
    for v in range(len(vals)):
        m = idx == v
        P[v] = [np.mean(y[m] == 0), np.mean(y[m] == 1)]
    D = np.abs(P[:, None, :] - P[None, :, :]).sum(-1)
    return idx, D


def dist_matrix(Xn, nom, y, scale, nominal):
    X = Xn.copy()
    if scale == "minmax":
        rng = X.max(0) - X.min(0)
        rng[rng == 0] = 1
        X = (X - X.min(0)) / rng
    elif scale == "z":
        sd = X.std(0)
        sd[sd == 0] = 1
        X = (X - X.mean(0)) / sd
    D2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
    for col in nom:
        if nominal == "vdm":          # WEKA SMOTE filter: VDM added unsquared
            idx, V = vdm_matrix(col, y)
            D2 = D2 + V[idx][:, idx]
        elif nominal == "overlap":    # WEKA EuclideanDistance: 0/1 mismatch
            D2 = D2 + (col[:, None] != col[None, :]).astype(float)
        elif nominal == "onehot":     # one-hot columns, squared diff = 2 per mismatch
            D2 = D2 + 2.0 * (col[:, None] != col[None, :]).astype(float)
    return np.sqrt(D2)


def danger_count(D, y, M, rule, self_in):
    n = len(y)
    cnt = 0
    for i in np.where(y == 1)[0]:
        d = D[i].copy()
        if not self_in:
            d[i] = np.inf
        # stable sort: ties broken by row order (as Java's Collections.sort)
        order = np.argsort(d, kind="stable")
        if self_in:
            # put self first among zero-distance points
            order = np.concatenate([[i], order[order != i]])
        nn = order[:M]
        Mp = int(np.sum(y[nn] == 0))
        if rule == "text":      # M/2 <= M' < M  (Han et al.; text p.33)
            ok = (Mp >= M / 2) and (Mp < M)
        elif rule == "figure":  # M/2 < M' < M   (Figs. 4 and 6)
            ok = (Mp > M / 2) and (Mp < M)
        elif rule == "nonoise_text":  # M/2 <= M' <= M
            ok = Mp >= M / 2
        cnt += ok
    return cnt


if __name__ == "__main__":
  for name, (g5, g8) in PAPER.items():
    Xn, nom, y = load(name)
    print(f"== {name}: n={len(y)} minority={y.sum()} numeric={Xn.shape[1]} nominal={len(nom)}  paper Gen M=5:{g5} M=8:{g8}")
    for scale in ("raw", "minmax", "z"):
        for nominal in (("vdm", "overlap", "onehot") if nom else ("none",)):
            D = dist_matrix(Xn, nom, y, scale, nominal)
            out = []
            for self_in in (False, True):
                for rule in ("text", "figure"):
                    c5 = danger_count(D, y, 5, rule, self_in)
                    c8 = danger_count(D, y, 8, rule, self_in)
                    out.append(f"self={int(self_in)},{rule[:3]}: {c5:3d}/{c8:3d}")
            print(f"  {scale:6s} {nominal:7s} | " + " | ".join(out))
