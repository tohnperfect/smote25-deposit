import sys
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote/exploration")
sys.path.insert(0, "/home/claude/work/rerun42/methods/absmote")
import numpy as np
import variants as V
from weka_replica import JavaRandom

orig_init = JavaRandom.__init__
def run(meth, M, k, offset, seed=1):
    def patched(self, s):
        orig_init(self, s)
        for _ in range(offset):
            self._next(32)
    JavaRandom.__init__ = patched
    V.JavaRandom = JavaRandom
    try:
        Xr, yr = V.generate(meth, M, k, "self_in", "borderline", "index", seed=seed)
    finally:
        JavaRandom.__init__ = orig_init
    c = V.weka_cv_confusion(Xr, yr, V.nominal, V.nv, pos=V.pos)
    return c["tp"], c["fp"]

targets = {("bsmote", 5, 5): (34, 18), ("absmote", 5, 5): (35, 25), ("absmote", 8, 5): (35, 19), ("bsmote", 8, 5): (38, 26),
           ("absmote", 8, 8): (40, 22)}
for off in range(0, 41):
    res = {t: run(*t, off) for t in targets}
    hits = [t for t in targets if res[t] == targets[t]]
    if hits:
        print("offset", off, "hits", hits, flush=True)
# other seeds for the filter (WEKA GUI seed field), offset 0
for s in range(0, 11):
    res = {t: run(*t, 0, seed=s) for t in targets}
    hits = [t for t in targets if res[t] == targets[t]]
    print("seed", s, "hits", hits, flush=True)
