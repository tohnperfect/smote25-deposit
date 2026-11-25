import sys
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote/exploration")
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote")
import numpy as np
import variants as V   # runs its own loop on import; guarded below
targets = {"bs55": (40, 34, 18), "bs58": (40, 34, 17), "bs85": (39, 38, 26), "bs88": (39, 32, 16),
           "ab55": (40, 35, 25), "ab58": (40, 36, 18), "ab85": (39, 35, 19), "ab88": (39, 40, 22)}
found = {t: [] for t in targets}
for meth in ("bsmote", "absmote"):
    for M in range(3, 11):
        for k in range(1, 11):
            Xr, yr = V.generate(meth, M, k, "self_in", "borderline", "index")
            c = V.weka_cv_confusion(Xr, yr, V.nominal, V.nv, pos=V.pos)
            key = (len(yr) - len(V.y), c["tp"], c["fp"])
            for t, v in targets.items():
                if key == v:
                    found[t].append((meth, M, k))
for t, v in found.items():
    print(t, targets[t], "->", v)
