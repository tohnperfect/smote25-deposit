import sys, collections
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote")
import numpy as np
from weka_replica import weka_cv_confusion, recall_f, weka_smote_family
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote/exploration")
RAW = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/"
rows = [[c.strip() for c in ln.split(",")] for ln in open(RAW + "abalone9-18.dat") if ln.strip()]
order = []; labs = []
for r in rows:
    if r[0] not in order: order.append(r[0])
    if r[-1] not in labs: labs.append(r[-1])
X = np.array([[order.index(r[0])] + [float(v) for v in r[1:-1]] for r in rows])
y = np.array([labs.index(r[-1]) for r in rows]); pos = labs.index("positive")
nominal, nv = [True] + [False]*7, [3] + [0]*7
for meth, M, k, target in (("smote", 5, 5, (32, 19)), ("absmote", 5, 8, (36, 18)), ("absmote", 5, 5, (35, 25))):
    hits, tps, fps = 0, [], []
    for s in range(1, 151):
        Xr, yr, _ = weka_smote_family(X, y, nominal, nv, method=meth, k=k, M=M, seed=s)
        c = weka_cv_confusion(Xr, yr, nominal, nv, pos=pos)
        tps.append(c["tp"]); fps.append(c["fp"])
        hits += (c["tp"], c["fp"]) == target
    print(meth, M, k, "target", target, "hits", hits, "/150; TP mean %.1f sd %.1f; FP mean %.1f sd %.1f" %
          (np.mean(tps), np.std(tps), np.mean(fps), np.std(fps)),
          "P(TP=t)", np.mean(np.array(tps) == target[0]).round(3))
