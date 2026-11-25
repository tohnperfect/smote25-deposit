"""Scratch: systematic search over readings of the borderline rule vs the paper's Gen counts."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gen_counts import load, dist_matrix, PAPER


def counts_for(D, y, M, self_mode):
    """Return list of M' values (majority count among the M neighbors) per minority row."""
    out = []
    for i in np.where(y == 1)[0]:
        d = D[i].copy()
        if self_mode == "excl":
            d[i] = np.inf
            order = np.argsort(d, kind="stable")
        elif self_mode == "incl_first":
            d[i] = -1.0
            order = np.argsort(d, kind="stable")
        elif self_mode == "incl_stable":   # self at distance 0, ties by row index
            d[i] = 0.0
            order = np.argsort(d, kind="stable")
        nn = order[:M]
        out.append(int(np.sum(y[nn] == 0)))
    return np.array(out)


RULES = {
    "M/2<=M'<M":      lambda Mp, M: (Mp >= M / 2) & (Mp < M),
    "M/2<M'<M":       lambda Mp, M: (Mp > M / 2) & (Mp < M),
    "M//2<=M'<M":     lambda Mp, M: (Mp >= M // 2) & (Mp < M),
    "M/2<=M'<=M":     lambda Mp, M: (Mp >= M / 2),
    "M/2<M'<=M":      lambda Mp, M: (Mp > M / 2),
    "M//2<=M'<=M":    lambda Mp, M: (Mp >= M // 2),
}

results = {}
for name in PAPER:
    Xn, nom, y = load(name)
    for scale in ("raw", "minmax", "z"):
        for nominal in (("vdm", "overlap", "onehot") if nom else ("none",)):
            D = dist_matrix(Xn, nom, y, scale, nominal)
            for self_mode in ("excl", "incl_first", "incl_stable"):
                Mp5 = counts_for(D, y, 5, self_mode)
                Mp8 = counts_for(D, y, 8, self_mode)
                for rname, rf in RULES.items():
                    c5, c8 = int(rf(Mp5, 5).sum()), int(rf(Mp8, 8).sum())
                    nomkey = nominal if nom else "any"
                    results[(name, scale, nomkey, self_mode, rname)] = (c5, c8)

# score each reading across datasets (nominal handling only matters for abalone/flare)
print("reading (scale, self, rule, nominal) -> counts per dataset; total |error|")
rows = []
for scale in ("raw", "minmax", "z"):
    for self_mode in ("excl", "incl_first", "incl_stable"):
        for rname in RULES:
            for nominal in ("vdm", "overlap", "onehot"):
                tot, parts = 0, []
                for name, (g5, g8) in PAPER.items():
                    key = (name, scale, nominal if name in ("abalone9-18", "flare-F") else "any",
                           self_mode, rname)
                    c5, c8 = results[key]
                    tot += abs(c5 - g5) + abs(c8 - g8)
                    parts.append(f"{name[:5]} {c5}/{c8}")
                rows.append((tot, scale, self_mode, rname, nominal, parts))
rows.sort(key=lambda r: r[0])
for r in rows[:25]:
    print(f"err={r[0]:3d} {r[1]:6s} {r[2]:11s} {r[3]:12s} {r[4]:7s} | " + " | ".join(r[5]))
print("paper: abalo 40/39 | haber 65/61 | flare 39/41 | wineq 53/53")
