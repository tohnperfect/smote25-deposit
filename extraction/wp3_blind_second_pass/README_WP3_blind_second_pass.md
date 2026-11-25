# WP3: blind second pass of the extractions (report for the adjudicator)

Version 1, 11 November 2026. Prepared by the AI assistant (Claude) in the v0.4 session. Nothing in this folder has
been checked by a person yet; under D13 an author adjudicates every disagreement from the PDF and checks a random
fifth of the agreements. Section 3.7 of the draft describes the protocol and carries a team note to report the
agreement and kappa per field and the share of items the adjudicator corrected once that is done.

## What was done

Separate AI sessions (fresh contexts, one per batch) recoded seeded random samples of each extraction. Each session
received the written coding rules, the paper texts and PDFs, and a list of items to code; it was told not to open
the first-pass codes, the team repository or any matrix, ledger or coded-data file, and not to look the papers up
online. Every code carries a page and, for judgment calls, a quote of at most 40 words.

| Extraction | Sample | Source of the first pass | Second-pass instructions |
|---|---|---|---|
| Data: dataset entries | 283 entries, 5 fields each (team sample, seed 20261028, 15 percent) | `Data section/blind/blind_sheet.xlsx` (verified sheet) | `coding_instructions/DATA_codebook.md` |
| Data: printed comparisons with plain SMOTE | 97 outcome rows, 3 fields each (same team sample) | same sheet | first without, then with the written metric rule (G-mean, else AUC, else F-measure, else accuracy) |
| Data: data-handling codes | all 76 papers | `Data section/out/data_handling_matrix.csv` (rows still marked `ai_draft`) | `coding_instructions/DATA_codebook.md` |
| Method form | 10 of the 37 method papers (seed 20261110, stratified) plus SMOM | Table 6 rows of v0.4 (after the D-decisions on GLOS and Loyalty-SMOTE) | `coding_instructions/METHOD_coding_rules.md` |
| Evaluation form | 15 of the 71 empirical studies (seed 20261110, stratified by period) | `Evaluation section/section07-coded-data.json` | `coding_instructions/EVAL_coding_scheme_section7_1.tex` |

The comparison of the Data extraction uses the team's own script (`build/blind_check.py compare`); the other
comparisons use `tools/dh_agreement.py` and `tools/wp3_compare.py`. Disagreements are grouped by
`tools/blind_categorize_v2.py`. Agreement is the share of identical codes; kappa is Cohen's kappa.

## Results before adjudication

### Data extraction (1,706 values: 283 entries x 5 fields, 97 outcome rows x 3 fields)

| Field | n | Different | Rate |
|---|---|---|---|
| Number of instances | 283 | 14 | 4.9% |
| Number of features | 283 | 39 | 13.8% |
| Number of classes | 283 | 123 | 43.5% |
| Minority size | 283 | 51 | 18.0% |
| Imbalance ratio as printed | 283 | 21 | 7.4% |
| Metric (under the rule) | 97 | 6 | 6.2% |
| Value of the proposed method | 97 | 11 | 11.3% |
| Value of plain SMOTE | 97 | 4 | 4.1% |
| All values | 1,706 | 269 | 15.8% (95% CI 14.1 to 17.6) |

Without the written metric rule the second coders chose the metric themselves, and 330 of the 1,706 values differed
(19.3%; the outcome fields differed in 19, 31 and 32 of 97 rows). With the rule the outcome rows agree closely; the
rule should therefore be printed in the Data methods text.

The 269 differences fall into six groups (`DATA_extraction_disagreements_for_adjudication.csv`, column `category`):

| Group | Count | What it is | Suggested handling |
|---|---|---|---|
| A | 105 | Number of classes not printed for a two-class dataset; the first pass recorded 2, the second `NR` | Convention, not an error: decide once and apply to all |
| C | 27 | The second coder found no printed value, or marked the row ambiguous (`?`): 13 dataset values; 14 outcome values where the paper has several "proposed" variants or SMOTE amounts (NBU, RACOG/wRACOG, SMOTE-ENN/SMOTE-Tomek, SMOTEBoost, MC-MBRC) | Check the page; decide which variant counts as "the proposed method" |
| D | 104 | The first pass left the value blank and the second found or read one, mostly a minority size or feature count read off a printed class distribution or the text | Decide whether a value read off a distribution counts as printed; then fill or keep blank |
| E1 | 25 | Same value written differently (`two` and 2, `5(5/-)` and 5, an IR with or without the overall IR) | Confirm and close |
| E2 | 2 | Different values: INOS FaceAll, number of classes 2 against 14 (binarized from a 14-class set); SOS on Shoppers, 0.673 against 0.675 | Check against the PDF |
| F | 6 | Same metric, label written differently (A-SUWO, MC-MBRC) | Confirm and close |

So, under the metric rule, the two coders chose the same metric for all 97 outcome rows and copied the same values
wherever both found a single printed value, with one exception (SOS).

### Data-handling codes (76 papers; `DATA_handling_agreement.json`, `DATA_handling_disagreements_for_adjudication.csv`)

| Field | Agreement | Kappa |
|---|---|---|
| Type of reason for the choice of data (`crit_type`) | 0.684 | 0.292 |
| Minority rule | 0.671 | 0.614 |
| Origin labels (73 empirical papers, one yes/no per label) | 0.753 (Generated) to 0.973 (Induced profile) | 0.372 (Class-resized) to 0.748 (Noise-injected) |

Which papers evaluate on data: no disagreement. The low kappa of `crit_type` comes mainly from one boundary: the
first pass coded 14 papers "cites prior work" and 48 "own reason"; the second pass 2 and 65. Both passes find a
reason for most papers, so the Table 5 count barely moves (first pass 65 of 73 with a reason, counting the 3 "widely
used"; second pass 68 of 73: 65 own reason, 2 cite prior work, 1 generic only), but the split between "own reason"
and "cites prior work" is not stable and needs the adjudicator's reading of the definitions. For the open Table 5 row
"Modified data released", the second pass coded 7 papers "yes" (GAMO, HDE, SMOTE-IPF, INOS, DSRBF/Static-SMOTE,
G-SMOTE, k-means SMOTE) and MC-MBRC "on request", a third count beside the Data (3) and Evaluation (10) counts; the
row stays open until the team fixes the definition.

### Method form (11 papers; `METHOD_comparison_for_adjudication.csv`)

| Field | Agreement | Kappa |
|---|---|---|
| Class category (B / M / B+M) | 10 of 11 (0.909) | 0.841 |
| Link (Core / Partial / Not counted) | 11 of 11 | 1.0 |
| Six decision points, 66 codes | 63 of 66 (0.955) | 0.909 |

Differences: Loyalty-SMOTE class (first B, after the team's decision; second B+M) and neighbor choice (first y,
second n); NROMM seed selection (first y, second n); RSMOTE neighbor choice (first n, second y). The SMOM check of the
journal version confirms class M, link Core and a change in neighbor choice only (`smom_check/`).

### Evaluation form (15 studies; `EVALUATION_comparison_for_adjudication.csv`)

| Field | Agreement | Kappa |
|---|---|---|
| Plain SMOTE as a baseline | 15 of 15 | 1.0 |
| No-resampling baseline | 15 of 15 | 1.0 |
| Resampling inside the training folds stated | 13 of 15 (0.867) | 0.727 |
| How settings were chosen | 9 of 15 (0.600) | 0.427 |
| Code released | 15 of 15 | 1.0 |
| Any statistical test | 15 of 15 | 1.0 |
| A measure defined wrongly | 13 of 15 (0.867) | 0.667 |
| Calibration measure reported | 15 of 15 (none in either pass) | not defined |
| Number of real datasets | 14 of 15 (0.933) | 0.928 |

Items to look at first: the second pass found a wrongly printed G-mean in MKC-SMOTE-2024 (Eq. 4) and SOUP-2019
that the first pass did not record; "how settings were chosen" differs for six studies (GMMSampling-2024,
MKC-SMOTE-2024, RBBoost-2015, CISO-2025, Global-CS-2006, OSS-1997), mostly between "fixed" and "not said" or
"tuned"; the in-fold statement differs for AMDO-2018 and FW-SMOTE-2022 (first pass y, second pass "not said");
and CISO-2025 has 50 real datasets in the first pass and 45 in the second, which leaves out the 5 KEEL sets used only
for tuning. If the adjudicator confirms these, the counts that rest on them in Sections 6 and 7 must be regenerated.

Two faults of the comparison script were found and fixed before these figures were computed: the token mapping
turned "not said" into "nt said" (which made five agreements look like disagreements), and the dataset count of the
first pass included synthetic sets. The spot-check sample was drawn after the fixes.

## What the adjudicator does

1. In each `*_for_adjudication.csv`, fill `adjudication` (the correct value, or `first`, `second`, `both wrong`)
   and `adjudication_note` (page and short quote), working from the PDF.
2. Check the 351 agreements drawn in `AGREEMENTS_spot_check_sample.csv` (a seeded fifth of the agreements of each
   form, seed 20261111): 288 Data extraction values, 21 data-handling codes, 17 Method codes, 25 Evaluation codes.
   Fill `check_result` (correct / wrong) and `note`.
3. Decide the conventions once (group A and D of the Data extraction; "cites prior work" against "own reason";
   which variant counts as the proposed method) and record them in the coding rules.
4. Report per field: agreement, kappa, and the share of items corrected; then the team notes in Section 3.7 and
   Table 5 can be resolved and the counts regenerated from the corrected codes.

## Files

| File | Content |
|---|---|
| `DATA_extraction_all_values_compared.csv` | All 1,706 compared values (both passes, match flag) |
| `DATA_extraction_disagreements_for_adjudication.csv` | The 269 differences with group, second-pass note and rule step |
| `DATA_extraction_summary_first_run.json`, `DATA_extraction_summary_metric_rule.json` | Rates per field before and after the metric rule |
| `DATA_handling_agreement.json`, `DATA_handling_disagreements_for_adjudication.csv` | Data-handling codes |
| `METHOD_comparison_for_adjudication.csv`, `EVALUATION_comparison_for_adjudication.csv`, `METHOD_EVALUATION_agreement.json` | Method and Evaluation forms |
| `AGREEMENTS_spot_check_sample.csv` | The random fifth of agreements to check |
| `second_pass_raw/` | Every second-pass file as written by the coding sessions |
| `coding_instructions/` | The instructions the second-pass sessions received |
| `smom_check/` | SMOM journal-version check |
| `tools/` | Scripts that drew the batches, assembled and compared the codes and drew the spot-check sample |

The second-pass files quote the papers (at most 40 words per code). They are for the team; if the folder is
deposited, keep the quotes short or drop the quote columns.
