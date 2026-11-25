"""Validate absmote.ABSMOTE against Al Majzoub and Elgedawy (2020).

Target: Table IV (p.34), Abalone9-18, J48, 5-fold cross-validation, recall and F-measure
of the minority class, AB-SMOTE settings 4.0-4.3 (M, k) in {5, 8}^2, GAP 0-1, 100%
(Table III, p.34); and the Gen columns of Tables IV, VI, IX and X (pp.34-35).

Protocol as the paper ran it (Sec. IV, pp.33-34, reconstructed where unstated; the
reconstruction is checked on Table IV rows that do not involve AB-SMOTE, part A):
the oversampler is applied once to the whole dataset (Gen rows appended after the
original rows); WEKA's Explorer then cross-validates J48 (-C 0.25 -M 2) with 5 stratified
folds and random seed 1 and pools one confusion matrix over the folds. Distances are
WEKA's SMOTE distances (raw numeric values, VDM for nominal attributes); nominal values
are coded in order of first appearance (WEKA's CSV loader).

Run: python3 -I validate_absmote.py [n_random_states]   (about 4 minutes with 40)
Writes validation_results.json next to this file.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from absmote import ABSMOTE  # noqa: E402
from weka_replica import (_vdm_tables, _weka_dist, recall_f, vdm_embedding,  # noqa: E402
                          weka_borderline, weka_cv_confusion, weka_smote_family)

RAW = "/home/claude/work/rerun42/src/kd/keel_ds/data/imbalanced/raw/"
UCI_HABERMAN = os.path.join(HERE, "data", "haberman_uci_order.csv")

# Table IV (p.34): Gen, recall, F-measure; TP and FP are implied (recall = TP/(42 + Gen)).
TABLE_IV = {
    "1.0 Original":         dict(gen=0,  recall=0.167, f=0.241),
    "2.0 SMOTE k=5":        dict(gen=42, recall=0.381, f=0.474),
    "3.0 BSMOTE M=5 k=5":   dict(gen=40, recall=0.415, f=0.507, method="bsmote", M=5, k=5),
    "3.1 BSMOTE M=5 k=8":   dict(gen=40, recall=0.415, f=0.511, method="bsmote", M=5, k=8),
    "3.2 BSMOTE M=8 k=5":   dict(gen=39, recall=0.469, f=0.524, method="bsmote", M=8, k=5),
    "3.3 BSMOTE M=8 k=8":   dict(gen=39, recall=0.395, f=0.496, method="bsmote", M=8, k=8),
    "4.0 AB-SMOTE M=5 k=5": dict(gen=40, recall=0.427, f=0.493, method="absmote", M=5, k=5),
    "4.1 AB-SMOTE M=5 k=8": dict(gen=40, recall=0.439, f=0.529, method="absmote", M=5, k=8),
    "4.2 AB-SMOTE M=8 k=5": dict(gen=39, recall=0.432, f=0.519, method="absmote", M=8, k=5),
    "4.3 AB-SMOTE M=8 k=8": dict(gen=39, recall=0.494, f=0.559, method="absmote", M=8, k=8),
}
# Gen of AB-SMOTE (= |P'|) for M = 5 and M = 8: Tables IV, VI, IX, X (pp.34-35).
GEN = {"abalone9-18": (40, 39), "haberman": (65, 61), "flare-F": (39, 41),
       "winequality-red-4": (53, 53)}


def implied_tp_fp(n_pos, recall, f):
    """Integer TP and FP consistent with the printed 3-decimal recall and F-measure."""
    tp = int(round(recall * n_pos))
    best = None
    for fp in range(0, 2000):
        val = 2 * tp / (2 * tp + fp + (n_pos - tp)) if tp else 0.0
        if abs(val - f) < 0.0005 and best is None:
            best = fp
    return tp, best


def encode(rows, minority_label):
    """WEKA CSV typing: numeric if every value parses, else nominal coded by first appearance."""
    cols = list(zip(*[r[:-1] for r in rows]))
    nominal, n_values, data = [], [], []
    for c in cols:
        try:
            data.append([float(v) for v in c])
            nominal.append(False)
            n_values.append(0)
        except ValueError:
            vals = list(dict.fromkeys(c))
            data.append([vals.index(v) for v in c])
            nominal.append(True)
            n_values.append(len(vals))
    X = np.array(data, dtype=float).T
    labs = list(dict.fromkeys(r[-1] for r in rows))
    y = np.array([labs.index(r[-1]) for r in rows])
    return X, y, labs.index(minority_label), nominal, n_values


def load(name):
    if name == "haberman-uci":
        rows = [ln.strip().split(",") for ln in open(UCI_HABERMAN) if ln.strip()]
        return encode(rows, "2")
    rows = [[c.strip() for c in ln.split(",")] for ln in open(RAW + name + ".dat") if ln.strip()]
    return encode(rows, "positive")


def weka_features(X, y, nominal, n_values):
    """Euclidean features whose squared distances equal WEKA's SMOTE distances."""
    blocks = []
    for a, nom in enumerate(nominal):
        blocks.append(vdm_embedding(X[:, a], y, n_values[a]) if nom else X[:, [a]])
    return np.hstack(blocks)


def absmote_to_weka(X, y, nominal, n_values, s, Xr):
    """Map ABSMOTE output back to WEKA attributes: numeric columns as generated, nominal
    columns of new rows by WEKA SMOTE's majority vote over seed and its k neighbors."""
    n = len(y)
    pos_in_border = {r: i for i, r in enumerate(s.borderline_indices_)}
    out = np.zeros((len(Xr), X.shape[1]))
    out[:n] = X
    col = 0
    for a, nom in enumerate(nominal):
        width = max(n_values[a] - 1, 1) if nom else 1
        if nom:
            for j, seed in enumerate(s.seed_indices_):
                group = [seed] + list(s.borderline_neighbors_[pos_in_border[seed]])
                counts = np.bincount(X[group, a].astype(int), minlength=n_values[a])
                out[n + j, a] = int(np.argmax(counts))
        else:
            out[n:, a] = Xr[n:, col]
        col += width
    return out


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    t0 = time.time()
    res = {"n_random_states": R}

    X, y, pos, nominal, nv = load("abalone9-18")
    n_pos = int(np.sum(y == pos))
    print(f"Abalone9-18 (KEEL): n={len(y)}, minority={n_pos}; nominal codes {nominal}")

    # == A: harness check ==
    print("\nA. Harness check on Table IV rows without AB-SMOTE (exact replay, seeds 1)")
    harness = {}
    for row, (Xa, ya) in (("1.0 Original", (X, y)),
                          ("2.0 SMOTE k=5", weka_smote_family(X, y, nominal, nv, "smote", k=5)[:2])):
        c = weka_cv_confusion(Xa, ya, nominal, nv, pos=pos)
        r, f = recall_f(c)
        p = TABLE_IV[row]
        tp, fp = implied_tp_fp(n_pos + p["gen"], p["recall"], p["f"])
        harness[row] = dict(paper_recall=p["recall"], paper_f=p["f"], paper_tp=tp, paper_fp=fp,
                            tp=c["tp"], fp=c["fp"], recall=round(r, 3), f=round(f, 3),
                            exact=(c["tp"], c["fp"]) == (tp, fp))
        print(f"  {row:22s} paper TP={tp} FP={fp} recall {p['recall']:.3f} F {p['f']:.3f} | "
              f"replay TP={c['tp']} FP={c['fp']} recall {r:.3f} F {f:.3f} "
              f"{'EXACT' if harness[row]['exact'] else 'differs'}")
    res["A_harness"] = harness

    # == B: Gen counts ==
    print("\nB. Gen = |P'| at 100% (WEKA distances), M = 5 / M = 8")
    gen_out = {}
    for name, label in (("abalone9-18", "abalone9-18"), ("haberman", "haberman (KEEL order)"),
                        ("haberman-uci", "haberman (UCI order)"), ("flare-F", "flare-F"),
                        ("winequality-red-4", "winequality-red-4")):
        if name == "haberman-uci" and not os.path.exists(UCI_HABERMAN):
            continue
        Xd, yd, pd, nomd, nvd = load(name)
        paper = GEN["haberman" if name.startswith("haberman") else name]
        F = weka_features(Xd, yd, nomd, nvd)
        row = {"paper": list(paper)}
        for rule in ("text", "figure", "authors_code"):
            row[rule] = [int(ABSMOTE(m_neighbors=M, borderline_rule=rule).fit(F, yd).n_synthetic_)
                         for M in (5, 8)]
        vdm = _vdm_tables(Xd, yd, nomd, nvd, 2)
        row["authors_code+index_quirk"] = [
            len(weka_borderline(Xd, yd, pd, M, nomd, vdm, "authors_code", skip_quirk=True)) for M in (5, 8)]
        gen_out[label] = row
        print(f"  {label:24s} paper {paper[0]}/{paper[1]} | text {row['text'][0]}/{row['text'][1]}"
              f" | figure {row['figure'][0]}/{row['figure'][1]}"
              f" | authors_code {row['authors_code'][0]}/{row['authors_code'][1]}"
              f" | +index quirk {row['authors_code+index_quirk'][0]}/{row['authors_code+index_quirk'][1]}")
    res["B_gen"] = gen_out

    # == C: exact replay of rows 3.x, 4.x ==
    print("\nC. Exact replay of the authors' WEKA pipeline (seeds 1), Table IV")
    F = weka_features(X, y, nominal, nv)
    vdm = _vdm_tables(X, y, nominal, nv, 2)
    replay = {}
    for row, p in TABLE_IV.items():
        if "method" not in p:
            continue
        Xa, ya, seeds = weka_smote_family(X, y, nominal, nv, p["method"], k=p["k"], M=p["M"])
        c = weka_cv_confusion(Xa, ya, nominal, nv, pos=pos)
        r, f = recall_f(c)
        tp, fp = implied_tp_fp(n_pos + p["gen"], p["recall"], p["f"])
        replay[row] = dict(gen=len(ya) - len(y), paper_gen=p["gen"], paper_tp=tp, paper_fp=fp,
                           paper_recall=p["recall"], paper_f=p["f"], tp=c["tp"], fp=c["fp"],
                           recall=round(r, 3), f=round(f, 3),
                           exact=(len(ya) - len(y), c["tp"], c["fp"]) == (p["gen"], tp, fp))
        print(f"  {row:22s} Gen {len(ya)-len(y)} (paper {p['gen']}) | paper TP={tp} FP={fp} "
              f"{p['recall']:.3f}/{p['f']:.3f} | replay TP={c['tp']} FP={c['fp']} {r:.3f}/{f:.3f} "
              f"{'EXACT' if replay[row]['exact'] else ''}")
    res["C_replay"] = replay

    # same borderline sets and partner lists in absmote.py (authors_code) and the replica
    agree = {}
    for M in (5, 8):
        s = ABSMOTE(m_neighbors=M, k_neighbors=8, borderline_rule="authors_code").fit(F, y)
        rep = weka_borderline(X, y, pos, M, nominal, vdm, "authors_code", skip_quirk=False)
        same_set = np.array_equal(np.sort(rep), s.borderline_indices_)
        same_nn = True
        for k in (5, 8):
            sk = ABSMOTE(m_neighbors=M, k_neighbors=k, borderline_rule="authors_code").fit(F, y)
            for i, r_ in enumerate(sk.borderline_indices_):
                cand = sk.borderline_indices_[sk.borderline_indices_ != r_]
                d = _weka_dist(X[r_], X[cand], nominal, vdm)
                same_nn &= np.array_equal(cand[np.argsort(d, kind="stable")[:k]],
                                          sk.borderline_neighbors_[i])
        agree[f"M={M}"] = dict(same_borderline_set=bool(same_set), same_neighbor_lists=bool(same_nn))
    res["C_agreement"] = agree
    print("  absmote.py (authors_code) vs replica: " +
          "; ".join(f"{m}: set {v['same_borderline_set']}, neighbors {v['same_neighbor_lists']}"
                    for m, v in agree.items()))

    # == D: absmote.py over random states ==
    print(f"\nD. absmote.ABSMOTE over {R} random states (paper protocol, CV seed 1);"
          f" first line: the replica over Java seeds 1..{R}")
    readings = [("replica", "per_feature"), ("authors_code", "per_feature"),
                ("authors_code", "scalar"), ("text", "per_feature"), ("text", "scalar")]
    dist = {}
    for rule, gap in readings:
        for row, p in TABLE_IV.items():
            if p.get("method") != "absmote":
                continue
            recs, fs, gens = [], [], []
            for rs in range(R):
                if rule == "replica":
                    Xw, yr, sd = weka_smote_family(X, y, nominal, nv, "absmote", k=p["k"],
                                                   M=p["M"], seed=rs + 1)
                    n_new = len(yr) - len(y)
                else:
                    s = ABSMOTE(m_neighbors=p["M"], k_neighbors=p["k"], borderline_rule=rule,
                                gap=gap, random_state=rs)
                    Xr, yr = s.fit_resample(F, y)
                    Xw = absmote_to_weka(X, y, nominal, nv, s, Xr)
                    n_new = s.n_synthetic_
                c = weka_cv_confusion(Xw, yr, nominal, nv, pos=pos)
                r, f = recall_f(c)
                recs.append(r)
                fs.append(f)
                gens.append(n_new)
            recs, fs = np.array(recs), np.array(fs)
            key = f"{row} | {rule}, gap={gap}"
            dist[key] = dict(gen=int(gens[0]), paper_recall=p["recall"], paper_f=p["f"],
                             recall_mean=round(float(recs.mean()), 3), recall_sd=round(float(recs.std(ddof=1)), 3),
                             f_mean=round(float(fs.mean()), 3), f_sd=round(float(fs.std(ddof=1)), 3),
                             share_recall_at_most_paper=round(float(np.mean(recs <= p["recall"] + 5e-4)), 3),
                             share_f_at_most_paper=round(float(np.mean(fs <= p["f"] + 5e-4)), 3))
            d_ = dist[key]
            print(f"  {row:22s} {rule:12s} {gap:11s} Gen {d_['gen']:2d} | recall {d_['recall_mean']:.3f}"
                  f" +- {d_['recall_sd']:.3f} (paper {p['recall']:.3f}, {d_['share_recall_at_most_paper']:.2f}"
                  f" of runs <= paper) | F {d_['f_mean']:.3f} +- {d_['f_sd']:.3f} (paper {p['f']:.3f},"
                  f" {d_['share_f_at_most_paper']:.2f})", flush=True)
    res["D_random_states"] = dist
    res["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "validation_results.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"\nwrote validation_results.json ({res['seconds']} s)")


if __name__ == "__main__":
    main()
