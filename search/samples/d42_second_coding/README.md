# The blind AI second coding of the two samples and its adjudication (decision D42, 14 November 2026)

Decision D42 (12 Nov 2026): a blind AI second coder codes both samples again, an AI session adjudicates the
differences, and the team lead spot-checks the adjudication. On 14 Nov 2026 the team lead chose to start at once, on
the records coded so far (the 300 records of the use audit and the 12 papers of the coverage sample with an open full
text), and to run a second round when the library PDFs arrive. Draft v0.25 reports the first round (Sections 3.4 and
8.3) and uses the settled codes for every count of the samples.

## How it was done

1. **Second coding, blind.** Separate AI sessions (Claude Opus 5.5) coded every record again from the same texts as
   the first coding (title and abstract, or the full text where the first coding used one), under the same codebooks
   (`protocol/codebooks/`: use audit v1.1, coverage v1.2 with the rulings) and instructions that withhold the first
   codes (`protocol/AGENT_INSTRUCTIONS_*.md`; tools in `protocol/coding_tools/`, batches 201 to 209 for the use audit
   and 201 to 202 for the coverage sample, listed in `protocol/coding_manifest.json`). No session saw a first code.
2. **Comparison.** `python3 -I scripts/d42_compare.py . data/search/screening_full_2026-11-11/d42/work data/search/screening_full_2026-11-11/d42`
   (`work/` holds the coding manifest and the second coders' outputs, `work/<project>/out/batch2NN_coded.csv`, with
   their `evidence` columns; the batch files with the abstracts and the full texts stayed in the session's workspace)
   writes `second_codes_<project>.csv`, `agreement.json` (agreement and Cohen's kappa per field; for the use audit also
   over the 40 records coded from a full text and over the 38 full texts that Section 8.3 counts, `fulltext_counted`)
   and `disagreements.csv` (222 items: 216 of the use audit, 6 of the coverage sample). The coverage sample's first
   codes are compared as the paper uses them, after the rulings' facts recheck (`coverage/rulings_fulltext_facts.csv`).
   List fields (resampler, learner, measures) are compared as sets.
3. **Adjudication.** `scripts/d42_adjud_batches.py` put the 222 items in six batches (adj301 to adj306, seed 20261124)
   and showed each with its two codes as A and B in random order; `adjudication_key.json` (kept out of the adjudicators'
   reach until they finished) says which letter was the first coder. Separate AI sessions settled each item from the
   record (abstract or full text) under the codebook: A, B or another value, a reason of at most 40 words and a
   confidence (`protocol/ADJUDICATION_INSTRUCTIONS.md`, `protocol/adjudication_tools/`). Raw decisions:
   `adjudication_raw/`.
4. **Compilation.** `python3 -I scripts/d42_compile.py . data/search/screening_full_2026-11-11/d42/disagreements.csv
   data/search/screening_full_2026-11-11/d42/adjudication_raw data/search/screening_full_2026-11-11/d42/adjudication_key.json data/search/screening_full_2026-11-11/d42`
   writes `adjudication_log.csv` (every item with both codes, the decision, the reason and the confidence),
   `adjudication_decisions.csv` (the same without the reasons), `adjudication_summary.json`, and
   `<project>_coded_adjudicated.csv`: the first codes with the corrections, the same columns as `<project>/coded.csv`.
   `scripts/analyze_samples.py` reads the adjudicated files when they exist (`codes_used` in `samples_summary.json`).

## Result of the first round (14 Nov 2026)

| | Use audit | Coverage sample |
|---|---|---|
| Records coded twice | 300 | 12 |
| Agreement | 91.2% of the values coded for every record (kappa 0.39 to 0.96 by field, lowest for the kind of validation, 66.0%); 97.9% of the safeguards coded from the 38 full texts | 97.7% of the coded values |
| Differences adjudicated | 216 | 6 |
| First code kept / changed | 133 / 83 (in 58 records; one value other than both codes) | 4 / 2 |
| Low confidence | 28 | 2 |

What moved in the paper (Section 8.3): applications 293 to 290 (three records found not to be applications), the
model meant to inform a decision about a person 142 (48%) to 135 (47%) (weighted 55.7% to 51.6%; card-fraud models
decide about transactions), and smaller shifts in domains, modality, resampler, external validation (abstract level)
and the full-text count of resampled test data (19 to 21). The coverage sample's counts did not change (R00308 stays
excluded under ruling B: the adjudicator kept the first code). `CHANGES-v0.25.md` lists every number.

## The team lead's spot check

Page "SMOTE25 Samples Check" (see `check_page/README.md`): every adjudication that changes a count of the paper, a
seeded sample of the other changes, a sample of the kept codes, and a sample of the agreed codes. The page shows short
quotes and reasons from the papers: team use only, never a public link, never deposited.

**Done on 14 Nov 2026 (v0.27):** the team lead checked all 90 items and agreed with every one (`spot_check_summary.json`; `spot_check_changes.csv` is empty). Sections 3.4 and 8.3 report it: "An author checked the 2 changes against the papers; none needed correcting" and "An author checked 88 of the settled codes against the records ...; none needed correcting". The second round will need a check of its own.

## Deposit

Deposited (D53): this README, `agreement.json`, `disagreements.csv`, `second_codes_*.csv`, `work/` and
`*_coded_adjudicated.csv` without their `evidence` columns, `adjudication_decisions.csv`, `adjudication_summary.json`,
`adjudication_key.json`, `spot_check_summary.json`, `spot_check_changes.csv` and `protocol/`. Not deposited: `adjudication_log.csv` and `adjudication_raw/` (the reasons may
quote papers) and `check_page/` (`scripts/build_deposit.py` excludes them).

## Second round (16 Nov 2026, v0.37)

The library PDFs arrived on 16 Nov 2026 (`../samples/library_pdfs_2026-11-16.csv`). The first coders coded the 82 new
coverage texts and coded the 78 use-audit targets again from their full texts (`../README.md`, step 7); then the same
steps as in round 1, for these records only:

1. **Second coding, blind.** Batches 211 to 224 (coverage, 82 papers) and 211 to 220 (use audit, 78 records), in an
   order shuffled with seed 20261116 (`work/manifest.json`, the same as `protocol/coding_manifest.json`), by separate
   AI sessions under the instructions of round 1, from the same full texts as the first coders.
2. **Comparison.** `python3 -I scripts/d42_compare.py . data/search/screening_full_2026-11-11/d42/work data/search/screening_full_2026-11-11/d42/round2 --round 2`
   writes `round2/second_codes_<project>.csv`, `round2/agreement.json` and `round2/disagreements.csv` (133 items: 41 of
   the use audit, 92 of the coverage sample). Two coverage files turned out to be other papers (R00144, R00339: both
   coders coded `fulltext_ok` = no, and the fetch log no longer counts them as obtained); they are listed under
   `not_the_paper` and not compared. `round2/agreement.json` also holds `all`: the agreement of the codes as they
   stand, each record with the two codes of its last round (round 2 replaces round 1 for the 78 use-audit records).
3. **Adjudication.** `python3 -I scripts/d42_adjud_batches.py data/search/screening_full_2026-11-11/d42/round2/disagreements.csv <adjudication dir> <private dir> --first-batch 311 --seed 20261125`
   (batches adj311 to adj317, `protocol/adjudication_manifest.json`; the key, `round2/adjudication_key.json`, stayed out
   of the adjudicators' reach until they finished), under `protocol/ADJUDICATION_INSTRUCTIONS.md`; raw decisions in
   `round2/adjudication_raw/`.
4. **Compilation.** `python3 -I scripts/d42_compile.py . data/search/screening_full_2026-11-11/d42/disagreements.csv data/search/screening_full_2026-11-11/d42/adjudication_raw data/search/screening_full_2026-11-11/d42/adjudication_key.json data/search/screening_full_2026-11-11/d42 --round2 data/search/screening_full_2026-11-11/d42/round2`
   rewrites round 1's adjudication files unchanged, writes round 2's (`round2/adjudication_log.csv`,
   `round2/adjudication_decisions.csv`, `round2/adjudication_summary.json`) and builds `<project>_coded_adjudicated.csv`
   from both rounds: a use-audit record coded again in round 2 takes round 2's corrections only, since both of its
   round-1 codes were replaced, and every other record takes round 1's (the script stops if a first code that round 1
   compared has changed). `in_force` in `round2/adjudication_summary.json` counts the items that the codes rest on.

### Result of the second round (16 Nov 2026)

| | Use audit | Coverage sample |
|---|---|---|
| Records coded twice in round 2 | 78, from their full texts | 80 (82 less the two other papers) |
| Agreement in round 2 | 96.2% of the values coded for every record, 95.6% of the safeguards (kappa 0.86 to 0.98 by field) | 94.8% of the coded values (kappa 0.84 to 0.96) |
| Differences adjudicated | 41 | 92 |
| First code kept / changed | 25 / 16 (in 13 records; one value other than both codes) | 46 / 46 (in 15 records) |
| Low confidence | 5 | 6 |
| The codes as they stand (both rounds) | 300 records: 93.2% of the values coded for every record (kappa 0.54 to 0.97, lowest for the kind of validation), 96.4% of the safeguards coded from the 116 full texts; 185 differences in force, 67 changes (round 1's 72 items of the 46 records coded again are replaced) | 92 papers: 95.2% of the coded values; 98 differences, 48 changes |

What moved: the coverage counts of the library round rest on the settled codes (R01470 becomes eligible, Core, as the
second coder had it; R00865 goes from Partial to Not counted); in the use audit the 78 full texts replace the codes from
title and abstract, and the adjudication settles 16 of their codes (`round2/adjudication_log.csv`). `CHANGES-v0.37.md`
lists the numbers of the paper that moved.

### The author's check of round 2

Page "SMOTE25 Samples Check, round 2" (82 items; `records.json` built by
`python3 -I scripts/build_d42_check.py . data/search/screening_full_2026-11-11/d42/work <out_dir> --round2`, md5
`707931b96187087b4edc316d90aafb85`, not kept here as it quotes the records). Its items went onto the page "SMOTE25 Last
Pass" (16 Nov 2026), where the team lead agreed with all 82 (export `../../../../team/last_pass/exports/`, converted to
this page's format in `round2/check_page/exports/`); `merge_d42_check.py ... --round2` wrote
`round2/spot_check_summary.json` and an empty `round2/spot_check_changes.csv`, so no override and no code changed.

## Third round (16 to 17 Nov 2026, v0.38): the papers that joined at the final merge

At the final merge (D28; `../README.md`, step 8) eight coverage papers with a library full text joined the sample:
R00042, R00491, R00655, R00832, R03007, R03488, R10647 and R11455. Separate AI sessions coded them (first coding,
batches 020 and 021) and, blind to that, coded them again (batches 231 and 232, in an order shuffled with seed
20261131; `work/manifest.json` and `protocol/coding_manifest.json`, `seed_round3`), under the instructions of round 1.
`python3 -I scripts/d42_compare.py . data/search/screening_full_2026-11-11/d42/work data/search/screening_full_2026-11-11/d42/round3 --round 3`
found 9 differences in 2 papers (agreement 94.9% of the coded values); `d42_adjud_batches.py ... --first-batch 321
--seed 20261132` cut them into batch adj321, which an AI session adjudicated under `protocol/ADJUDICATION_INSTRUCTIONS.md`
(key `round3/adjudication_key.json`, kept from the adjudicator until it finished): every item kept the first code
(R00832 stays Not counted; R11455's tuning stays validation). Compilation of all three rounds:

`python3 -I scripts/d42_compile.py . data/search/screening_full_2026-11-11/d42/disagreements.csv data/search/screening_full_2026-11-11/d42/adjudication_raw data/search/screening_full_2026-11-11/d42/adjudication_key.json data/search/screening_full_2026-11-11/d42 --round2 data/search/screening_full_2026-11-11/d42/round2 --round3 data/search/screening_full_2026-11-11/d42/round3`

It leaves the files of rounds 1 and 2 byte for byte as they were and writes round 3's into `round3/`;
`round3/agreement.json` (`all`) and `round3/adjudication_summary.json` (`in_force`) count the codes as they now stand,
over the samples after the final merge: 88 coverage papers (94.8% of the coded values agree; 101 differences in force,
47 changes) and the 300 use-audit records (as after round 2). The 6 items of the three papers that left the sample with
codes of round 1 or 2 no longer count. Round 3 changed no code, so it has no check page of its own: an author's checks
of rounds 1 and 2 already hold every change in force (55 coverage items and 86 use-audit items in force, none changed;
`scripts/search_numbers.py` checks this).

### Reproducing round 1

Round 1's files (`agreement.json`, `disagreements.csv`, `second_codes_*.csv`, the adjudication files) were made from
the first codes before the library round. Checked on 16 Nov 2026: `d42_compare.py --round 1` run on v0.36 (the same
second codes, `work/`) reproduces round 1's four comparison files byte for byte, `d42_compile.py` reproduces its
adjudication files, `build_d42_check.py` its page records (md5 `9fb4b0b2334e9830e93f2c97373651eb`) and
`merge_d42_check.py` its check summary.

Checked on 14 Nov 2026: from the files of this folder alone, `d42_compare.py` reproduces `agreement.json`,
`disagreements.csv` and both `second_codes_*.csv`, `d42_compile.py` reproduces the adjudication files, and
`build_d42_check.py` (with `work/` as its work dir) reproduces the page's `records.json` byte for byte.
