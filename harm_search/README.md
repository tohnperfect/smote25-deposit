# WP5 step 4: harm search, AI first pass (11 November 2026)

**Status: ai_draft.** Every decision, field and count here comes from AI screeners (Claude Opus 5.5 sessions, one
screener per record, no second reviewer) reading PubMed titles and abstracts under `HARM_SCREEN_CODEBOOK.md`. A person
checks it before anything enters the paper. The inclusion rule is the one proposed in `../README.md` (step 4) and is
itself for the team to confirm.

## Queries and records

The four harm queries of `../harm_search_log.json` (H1 calibration, H2 leakage, H3 privacy, H4 fairness), copied
verbatim, were rerun against PubMed with NCBI E-utilities on 11 November 2026 between 09:22 and 09:23 UTC
(`scripts/fetch_harm.py`; every request with its URL and UTC time in `raw/fetch_log.tsv`, raw XML in `raw/H1` to
`raw/H4`). No API key, tool name or email was sent. The counts equal those logged on 10 November: H1 297, H2 91,
H3 34, H4 46. Merged by PMID: **429 distinct records** (H1 only 260, H2 only 61, H3 only 29, H4 only 40; the rest
found by two queries), one without an abstract.

## Rule as applied

Include when (I1) a model is trained on data oversampled with SMOTE, a SMOTE variant or random oversampling, (I2) it
is compared with a model trained without resampling (class weights count as without resampling) or, for leakage only,
resampling before the split is compared with resampling of the training data only, and (I3) the comparison reports a
harm measure: calibration, leakage-inflated performance, privacy attack success, or a disparity between groups.

## Counts

| Decision | Records |
|---|---|
| include | 27 |
| unsure (full text needed) | 49 |
| exclude | 353 |

Excludes by reason: no comparison with a model trained without resampling 268, not resampling in the machine-learning
sense (instrument calibration, survey or signal oversampling, other senses of "bias") 57, a comparison without a harm
measure 22, not a study 6.

Includes by harm and finding:

| Harm | Includes | Harm found | No harm | Mixed |
|---|---|---|---|---|
| Calibration | 14 | 9 | 4 | 1 |
| Leakage | 8 | 8 | 0 | 0 |
| Fairness | 5 | 0 | 4 | 1 |
| Privacy | 0 | | | |

Comparison: with no resampling 19, before against after the split 7, both 1. Data: real 22, real and simulated 5.

A practice finding beside the rule: **176 excluded records report the calibration of a model trained on SMOTE or
oversampled data without any comparison with a model trained without resampling** (code X-no-comparison, `harms`
calibration), and several more apply SMOTE before the train-test split without measuring the leak.

## Choices the checker should confirm or change

1. A comparison with an existing clinical score, a human triage rule, a null model or another algorithm is not "a
   model trained without resampling" (X-no-comparison).
2. Oversampling that balances protected groups rather than classes (41701928, 41639760) counts as oversampling (I1).
3. A comment with its own re-analysis is a study (41590873); records that apply SMOTE before the split without a
   correct-resampling arm are X-no-comparison, though their estimates are probably leaky.
4. Where two calibration measures disagree (37266187: Brier score down, calibration distorted), the authors'
   conclusion decides the finding.
5. Where several exclusion codes hold, the first failing criterion in the order I1, I2, I3 is recorded.
6. No rule yet for calibration compared between oversampling and undersampling only (30342683: excluded).

The screening sessions worked in the v0.8 working folder (the paths in `AGENT_INSTRUCTIONS.md`); the folder was
moved into the v0.9 working copy afterwards, because v0.8 had been delivered. The screeners' notes on hard cases are in `work/decisions/batch_NN_DONE.txt`; the includes and unsure records with
their reasons are in `work/includes.md`; one row per record with every field is `harm_search_records.csv`.

## Files

| File | Content | Deposit |
|---|---|---|
| `raw/` | E-utilities responses (titles and abstracts) and the request log | log only (abstracts are publishers' text) |
| `work/records.json`, `work/batches/` | parsed records and the screening batches | no |
| `work/decisions/` | the screeners' decisions (JSON) and notes | without the `quote` field |
| `harm_search_records.csv` | the merged table | without the `quote` column |
| `work/summary.json` | the counts above | yes |
| `HARM_SCREEN_CODEBOOK.md`, `AGENT_INSTRUCTIONS.md`, `scripts/` | rules, instructions and tools | yes |

## Next

A person checks the 27 includes and the 49 unsure records (full text for the unsure), and a random sample of the
excludes; the team confirms the rule (and the choices above). Only then can Section 8.5 and Table 16 of the paper
(the balance of benefits and harms) use these counts, with the check reported. Rebuild with
`python3 -I scripts/build_results.py` after any correction of `work/decisions/`.
