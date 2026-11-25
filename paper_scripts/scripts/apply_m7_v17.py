#!/usr/bin/env python3
"""Step 4 of the plan of 12 November (D39): the 12 claims of the M7 review that were left "for a person to check",
checked against their sources by a Claude session on 12 Nov 2026 (docs/M7-CLAIMS-CHECK-v0.17.md lists each claim, the
source read and the finding). This script applies the resulting edits to the sources of draft v0.17; each replacement
must match exactly once, so a second run stops. Usage: python3 -I scripts/apply_m7_v17.py <draft_dir>
"""
import sys
from pathlib import Path

D = Path(sys.argv[1])

EDITS = [
    # item 33: the 55 counts per-dataset results against any baseline; with SMOTE the Data count is 43 of 57 (Section 5.6)
    ('sec/06-evaluation.tex',
     r'\src{S}{}(55 of the 73 papers pair the proposed method with SMOTE dataset by dataset; Section~\ref{sec:wins}),',
     r'\src{S}{}(43 of the 57 papers that use SMOTE as a baseline pair it with the proposed method dataset by dataset; Section~\ref{sec:checkable}),'),
    ('sec/03-method.tex',
     r"Per-dataset results & 55 of 73 (47 full, 8 partial) & 58 of 71 & Decided: 55, tables that pair the proposal with SMOTE; the Evaluation's 58 counts any per-dataset table and is used only with that label \\",
     r"Per-dataset results & 55 of 73 (47 full, 8 partial) & 58 of 71 & Decided: 55, papers with per-dataset results against any baseline; with SMOTE, 43 of the 57 papers that use it as a baseline pair it with the proposal dataset by dataset (Section~\ref{sec:checkable}); the Evaluation's 58 counts any per-dataset table and is used only with that label \\"),
    # item 41: 29 papers convert classes; Section 5.2's 30 also counts a label-noise version and a set the authors labeled
    ('sec/03-method.tex',
     r'and papers with a modified entry that changes the class structure (29); name the question in each sentence \\',
     r'and papers with a modified entry that changes the class structure (29 that convert classes; 30 in Section~\ref{sec:modified}, which also counts a label-noise version and a set the authors labeled); name the question in each sentence \\'),
    # item 34: the class categories; GLOS's one two-class run only illustrates a parameter (decision A1, 10 Nov 2026)
    ('sec/03-method.tex',
     r'\emph{Multiclass only}: the generator creates synthetic data with three or more classes kept, and is never run on a two-class problem. \emph{Binary + Multiclass}:',
     r'\emph{Multiclass only}: the generator creates synthetic data with three or more classes kept, and is never run on a two-class problem \src{S}{}except to illustrate the choice of a parameter (the one two-class run of GLOS). \src{M}{3.4}\emph{Binary + Multiclass}:'),
    ('sec/04-family.tex',
     r'their rules would cover two classes as a special case, but their papers never show it. Eight are Binary + Multiclass.',
     r'their rules would cover two classes as a special case, \src{S}{}but their papers never evaluate it. \src{M}{7}Eight are Binary + Multiclass.'),
    # item 51: the source of the 39, Table 8 of the Evaluation draft, reported in Section 6.3
    ('sec/06-evaluation.tex',
     r'so a study that reports only composites cannot tell whether a resampler improved the classifier or merely moved its threshold.',
     r'so a study that reports only composites cannot tell whether a resampler improved the classifier or merely moved its threshold. \src{E}{Table 8}Seventy of the 71 studies say why they chose their measures, and a study can give several reasons: that the measures are standard in the literature (40 studies), that accuracy misleads under imbalance (39), a focus on the minority class (25), independence of the threshold (18), suitability for several classes (18) and the costs of an application (7).'),
    ('sec/08-society.tex',
     r'and 39 of the 71 studies of our corpus still give that argument for their choice of measures.',
     r'and 39 of the 71 studies of our corpus still give that argument for their choice of measures (Section~\ref{sec:measures}).'),
    # item 54: an unsourced claim about the software history, cut
    ('sec/08-society.tex',
     r'a free, simple and model-agnostic way to make a classifier pay attention to a rare class, at a time when the alternatives (costs, class weights, threshold tuning) were less accessible in common software.',
     r'a free, simple and model-agnostic way to make a classifier pay attention to a rare class.'),
    # item 55: the top-ten range is the paper's own Table 4; the gap to SMOTE is per learner (Table 3) and the author's words
    ('sec/07-evidence.tex',
     r'and their mean G-mean between 0.862 and 0.871 \citep{kovacs2019ranking}.',
     r'and their mean G-mean between 0.862 and 0.871 \citep[Table~4]{kovacs2019empirical}, as in the documentation of the package \citep{kovacs2019ranking}.'),
    ('sec/07-evidence.tex',
     r'Plain SMOTE itself is in none of the top lists: the best oversamplers lead it by about 0.01 in AUC.',
     r'Plain SMOTE itself is in none of the top lists: for each learner, the mean AUC of the best oversampler exceeds that of SMOTE by 0.003 to 0.009, a gain that the author puts at about one percent and finds smaller than expected \citep[Table~3 and p.~7]{kovacs2019empirical}.'),
    # item 56: the attacks' assumptions and results as the ICLR version states them
    ('sec/08-society.tex',
     r'\citet{ganev2026smote} give two attacks with minimal assumptions: one distinguishes real from synthetic records in an augmented dataset perfectly, and one reconstructs real minority records from a synthetic dataset with perfect precision and a recall that approaches one at realistic imbalance ratios.',
     r'\citet{ganev2026smote} give two attacks that need only the released dataset and the knowledge that SMOTE produced it: one distinguishes real from synthetic records in an augmented dataset with perfect precision and recall, and one reconstructs real minority records from a synthetic dataset with perfect precision and a recall of 0.85 on average, which reaches one at imbalance ratios of 20 or more.'),
    # item 57: Carriero et al. report discrimination; its effect depends on the learner, so "no consistent gain"
    ('sec/08-society.tex',
     r'and they find no gain in discrimination and a loss in calibration \citep{vandengoorbergh2022harm,carriero2025harms,andersen2026tipping};',
     r'and they find no consistent gain in discrimination and a loss in calibration \citep{vandengoorbergh2022harm,carriero2025harms,andersen2026tipping};'),
    # item 60 (consistency): the table repeats the wording that the M7 revision corrected in Section 8.2
    ('sec/08-society.tex',
     r'from 159 countries; default oversampler of common toolboxes & Strong (reach) \\',
     r'from 159 countries; implemented in common toolboxes & Strong (reach) \\'),
    # item 57 again: the row of Table 16 that repeats the claim
    ('sec/08-society.tex',
     r'no outcome-level study found; independent clinical studies find no gain & Weak, contested \\',
     r'no outcome-level study found; independent clinical studies find no consistent gain & Weak, contested \\'),
]


def main():
    for rel, old, new in EDITS:
        p = D / rel
        t = p.read_text(encoding='utf-8')
        n = t.count(old)
        if n != 1:
            sys.exit(f'STOP: {rel}: expected one match, found {n}: {old[:80]!r}')
        p.write_text(t.replace(old, new), encoding='utf-8')
    print(f'{len(EDITS)} edits applied')


if __name__ == '__main__':
    main()
