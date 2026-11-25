# D35 in the wins analysis (12 November 2026)

Decision D35 of the team lead (12 Nov 2026): when a paper proposes several variants, "the proposed method" is the
variant the abstract names as the contribution; if it names several, the first named. Applied to the sample of the blind
second pass, it settled the outcome values of group C. Applied to the whole all-metric extraction, it changes the
proposed column of four of the 29 papers with per-dataset comparisons against plain SMOTE:

| Paper | Taken before | Taken under D35 | Why | Values from |
|---|---|---|---|---|
| NBU | NB-Comm (ranked best by the paper) | NB-Basic | the abstract names none of the four NB variants; NB-Basic is the first the paper names | `other_variants` of the extraction |
| RACOG / wRACOG | wRACOG | RACOG | abstract: "two probabilistic oversampling approaches, namely RACOG and wRACOG" | `racog_alt` of the extraction |
| SMOTE-ENN / SMOTE-Tomek | Smote+ENN | Smote+Tomek | abstract (p.1): "Two of our proposed methods, Smote + Tomek and Smote + ENN" | Table 4, pruned trees, read on the rendered page 7 (an image) |
| SOS | Sub-VP (most bold cells) | VE | the abstract names no variant; Section 2 names VE, VP and Sub-VP in that order | Table 2, text layer |

The other 25 papers propose one method, or their extraction already takes the first-named variant (each proposed
column checked against its abstract on 12 Nov 2026; GDHS's first-named strategy is the self-inner cleaning, GDHS_LC,
which the extraction takes).

## How the numbers were recomputed

The Data section's own scripts were run, unchanged, on a copy of the Data section (the team repository is read only):

1. Copy `Data section/` to a scratch folder and rerun, from outside it with `python3 -I tools/run_team.py <script>`:
   `winloss_allmetric`, `allmetric_links`, `modification_analysis`, `hypotheses`, `difficulty_outcomes`,
   `reconcile_counts --overwrite`, `family_dependence`, `temporal_comparison`, `claim_evidence`. On the unchanged copy
   every output equals the repository's (JSON values compared key by key; CSV rows compared after line endings), with
   statsmodels 0.15.0, pandas 3.0.5, scipy 1.18.1.
2. `python3 -I tools/apply_d35.py "<copy>/Data section"` replaces the proposed values of the four papers in
   `ai-draft/outcome/allmetric/{NBU,RACOG,SMOTE-ENN,SOS}.json` (the replaced value is kept per row under
   `replaced_by_D35`) and the 55 rule-A rows of the same papers in `out/verified_outcomes.csv`; it writes
   `d35_changes.csv` (147 values, 32 results change).
3. Rerun the scripts of step 1 on the patched copy. The outputs that changed are in `out/` here; `allmetric/` holds the
   four patched extraction files.

`tools/run_team.py` appends the script's folder to the end of `sys.path`, so the team's helper modules import while the
standard library and installed packages resolve first (no module of `build/` shadows one).

## What changed in the paper

| Quantity | Before | Under D35 | Source here |
|---|---|---|---|
| Decided comparisons won by the proposal (29 papers) | 1,107 of 1,393 (79.5%, CI 77.3 to 81.5) | 1,102 of 1,395 (79.0%, CI 76.8 to 81.1) | `out/hypotheses.json` all_metric_plain.overall |
| Ties, losses | 102, 286 | 100, 293 | `out/winloss_allmetric_summary.json` plain_smote_only |
| Papers with at least one SMOTE win | 23 of 29 | 24 of 29 (SOS) | `out/winloss_allmetric_summary.json` per_paper |
| One result per dataset | 409 / 35 / 76 | 403 / 42 / 75 | `out/hypotheses.json` robust_R1_dataset_majority |
| Modified or synthetic vs original, GEE | 0.68 (0.43 to 1.08), p = 0.10 | 0.61 (0.37 to 1.00), p = 0.051 | H1 M1_gee |
| Same, conditional logistic | 0.62 (0.39 to 0.99), p = 0.04 | 0.53 (0.33 to 0.84), p = 0.007 | H1 M2_conditional |
| Same, Bayesian mixed model | 0.75 (0.58 to 0.98) | 0.64 (0.49 to 0.83) | H1 M3_bayes_mixed |
| Noise index per 0.1, GEE / within papers | 1.15 (p = 0.005) / 1.19 (p = 0.006) | 1.18 (p = 0.001) / 1.21 (p = 0.002) | `out/difficulty_outcomes.json` |
| Holm-adjusted p of the noise index | 0.025 / 0.031 | 0.006 / 0.009 | `gen/table_model_variants.tex` |
| Margin ranks of splits of one source, permutation p | 0.005 | 0.002 | `out/family_dependence.json` t1 |

Every direction is the same. The online appendix (S9) states the rule and the values before it.

## Rounding once

The Data scripts write odds ratios and their limits with three decimals, and the paper prints two, so a value can be
rounded twice. `tools/full_precision.py` copies a Data section, changes only the number of decimals of the round() calls
of `build/hypotheses.py` and `build/difficulty_outcomes.py`, reruns them and checks that each of the 376 values lies
within half a unit of the value the unchanged script wrote. Its outputs are in `out/full_precision/` (under D35) and
`before/full_precision/` (the variants first chosen); `scripts/gen_model_variants.py` reads them when they are present.
Under D35 one printed value moved: the within-paper odds ratio of the noise index is 1.2145 (1.0747 to 1.3725), printed
1.21 (1.07 to 1.37), where the three-decimal file gave 1.22 (1.08 to 1.37). Before D35, four values of the v0.15 table
had been rounded twice (0.69 for 0.68, the clustered odds ratio of modified or synthetic against original data; 0.41 for
0.42 and 0.97 for 0.98, two limits of the comparison with original or repository-defined data; 0.077 for 0.078, a
p value); only the first is still printed, as a value before D35 in S9, and it now reads 0.68.

    python3 -I tools/full_precision.py "<patched copy>/Data section" out
    python3 -I tools/full_precision.py "<unchanged copy>/Data section" before

For the team repository: to carry D35 into the Data section itself, run `tools/apply_d35.py` on the repository's
`Data section/` and rerun the scripts of step 1 there (the Data section's owner, Kanvara Thawarorit), then compare with `out/` here.
