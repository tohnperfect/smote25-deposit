# Systematic search (WP4): screen, coverage sample and use audit, 11 and 12 November 2026

Title-and-abstract screening of the 22,426 distinct records of `../2026-11-11/wp4_records_merged.csv.gz` by AI
sessions in three looks, with the rulings of the team lead on criterion I1 applied by a further AI pass (12 November,
`rule_b/`); a stratified random sample of the records that pass the screen, coded in full text (coverage
of the corpus, Section 4.4); and a stratified random sample of the applications the screen excluded under E1 (use
audit, Section 8.3). **The authors' check of the screen runs in parallel** (D14; the team lead's decision of 11 November
2026 was to proceed as if the screen were checked and to merge the team's corrections into the final version). An
**independent AI check** by another model (Claude Fable 5.2; report v3, project doc
`claude/smote25-ai-check-report-v3-2026-11-11.md`) is merged since v0.13 (`check/returns/`, `check/README.md`). Every
count in Section 3.4, Figure 2, Section 4.4, Section 7.5, Section 8.3 and the abstract is generated from the files here.

## How a correction of the team enters the paper

1. Add one row per corrected record to `person_overrides.csv`: `rec` (for example R01234), `decision` (`include` or
   `exclude`; `unsure` leaves it for the authors' check, and at the final merge excludes it, D28), `code` (optional; for an exclusion E1, E2, E-NOGEN, E-REVIEW,
   E-COMPARE, E-LANG or E-OTHER, for an include I1-new-variant, I1-generative, I1-hybrid, I1-multiclass or I1-other),
   `note`. The decisions of `check/SMOTE25_rulings_check_2026-11-12.xlsx` (the records the rulings moved) and of the
   workbook of 11 November come back this way. Since v0.14 the team can also decide on the review page (artifact
   "SMOTE25 Screen Check"); `scripts/merge_team_review.py` turns its export into these rows
   (`check/team_review/README.md`).
2. From the draft folder run, in order:
   `python3 -I scripts/rule_b_decide.py .` (only if the facts of the rulings pass changed) ;
   `python3 -I scripts/screen_decide.py .` (one decision per record) ;
   `python3 -I scripts/make_samples.py . data/search/screening_full_2026-11-11/samples` (the samples; ranks come from a
   hash of the record id, so a correction removes or adds a record without moving any other) ;
   code any record that newly enters a sample (tools below) and merge the codes with `consolidate_codes.py` ;
   `python3 -I scripts/analyze_samples.py .` ; `python3 -I scripts/search_numbers.py .` ;
   `python3 -I scripts/render_search_text.py .` (rewrites the marked paragraphs from `scripts/search_templates/`) ;
   `python3 -I scripts/gen_coverage_table.py .` ; `python3 -I scripts/make_fig_prisma.py .` ;
   `python3 -I scripts/pdf_request_list.py .` ; then rebuild, `check_numbers.py` and `build_ledger.py`.
   `search_numbers.py` stops with WORDING CHECK FAILED when a count no longer bears out a sentence of Section 4.4; revise
   `scripts/search_templates/c_beyond.tex` by hand then.
3. A full text supplied by the team (saved as `R#####.pdf`) is converted with `pdftotext`, put in the project's
   `text/` folder and coded (coverage: a new batch; use audit: a recode from the full text, which replaces the code
   from the abstract).

## What was done, and by whom

1. **First pass.** Separate AI sessions (Claude Opus 5.5 subagents, one session per batch, none seeing another's
   output) screened every record under `SCREENING_CODEBOOK.md` v1.1 (the pilot's codebook v1 with four written
   clarifications) as `AGENT_INSTRUCTIONS.md` says. 113 batches (112 of 200 records, one of 26; seed 20261112;
   `first_pass/screen_manifest_PRIVATE.json`). Each record got a decision, a code, a confidence, a one-sentence reason,
   a short quote from the abstract and optional tags. Notes in `result/coder_notes.md`.
2. **Second look.** Other sessions screened again, blind to the first decision, every record the first pass marked
   unsure or decided with low or medium confidence: 4,358 records in 22 batches (seed 20261113;
   `second_look/second_manifest_PRIVATE.json`). Combined by `tools/reconcile.py` into `final/`.
3. **Third look (adjudication).** Other sessions settled the 2,088 records on which the first two looks differed or
   either said unsure, seeing both earlier decisions and reasons (`adjudication/`: instructions, tools, manifest with
   seed 20261115, outputs). The codebook's clarifications send doubtful kinds of record (an existing generator plus an
   existing cleaning step presented as new; a generator built for another purpose; no evaluation named in the
   abstract) to unsure, so 1,222 of the 2,088 stay unsure and go on to full-text assessment, as PRISMA 2020 provides.
4. **Decisions** (`decisions/`, `scripts/screen_decide.py`). A high-confidence first decision stands; a decision both
   looks share stands; a disputed record takes the third look's decision; a record that its repository removed is
   excluded under E-WITHDRAWN (ruling A, 11 November; `withdrawn_records.csv`); an included record that fails rulings B
   or B2 is excluded under E1 when the rulings pass was confident and is otherwise unsure (U-rule-B), unless the
   independent AI check read it; the decision of the independent AI check is final for every record of its three
   lists (v0.13); a row of `person_overrides.csv` replaces any of these. At the final merge, when the authors have
   finished the review page, an empty file `FINAL_MERGE` in this folder switches on decision D28 (team lead,
   12 November): every record still unsure is excluded under E-UNSURE, a line of its own in Figure 2. The columns
   `ai_screen_decision`, `ai_screen_code` and `ai_screen_by` keep the AI screen's decision before the authors'
   corrections and D28 (v0.15); the counts that describe the AI steps come from them, so later corrections do not change
   what the text says those steps did, and the corrections and D28 are counted on their own (`team`,
   `final_merge_unsure_excluded` in the summary).
4a. **Rulings pass** (`rule_b/`, 12 November). The team lead's rulings B (a chain of existing resampling steps counts as
   the paper's own method only if presented as the contribution and compared with another way of resampling), B2 (a
   standard generator used without a stated change never counts) and C (the task does not decide scope): 15 AI sessions
   recorded the facts of the 2,933 records the looks included and `scripts/rule_b_decide.py` applied the rulings; for
   the 2,634 of them outside the independent check's lists, the failures recorded with high confidence are excluded
   and the others are unsure (team lead, 12 November). See `rule_b/README.md`.
4b. **Independent AI check** (`check/`, merged 12 November, v0.13). Another model (Claude Fable 5.2), run by the team
   lead on the check job of 11 November: blind decisions on a random 300 includes and 300 exclusions, decisions on the
   1,222 records the looks left unsure, a second pass under rulings A, B and B2, and a check of the codes of both
   samples. Its decisions are final for its lists; its code corrections enter as recode batches
   (`scripts/apply_check_code_corrections.py`). See `check/README.md`.
5. **Samples** (`samples/`, `scripts/make_samples.py`). Coverage: 30 records at random from each of the four periods of
   the evaluation audit among the records that pass the screen (seed 20261116; P4 includes the forthcoming records
   dated 2027). Use audit: 100 records at random from each of three periods among the exclusions under E1 (seed 20261117),
   the first 50 of each also for full text. The rulings pass (12 November) removed R02697, R02901 and R19720 from the
   coverage sample (R02145, R01762 and R05514 entered) and brought R01361, R01235 and R02901 into the use audit in place
   of R02429, R01155 and R01737; the rule for removed records had replaced R17106 by R21783 (11 November). The merge of
   the independent check (v0.13) changed both again: 8 records left the coverage sample (R00083, R01762, R07978,
   R13673, R17572, R03543, R22331, R19448) and 8 entered (R00097, R02697, R06255, R05755, R06485, R10916, R07370,
   R08959); 10 left the use audit (R01719, R01968, R02900, R01524, R01228, R02000, R05820, R07106, R02956, R04077) and
   10 entered (R00777, R00717, R00454, R01133, R01745, R00164, R06457, R02955, R05675, R05286).
6. **Full texts** (`fulltext_tools/fulltext_fetch.py`). Open routes only: arXiv, Europe PMC full text of the
   open-access subset, and the open-access PDF links of Semantic Scholar and OpenAlex, fetched once with an honest user
   agent and kept only if they are the paper (title check). 13 of the 120 coverage papers and 40 of the 150 use-audit
   full-text targets had one at first (none of the records that entered on 11 and 12 November). In v0.13 one of the 13
   (R22331) left the coverage sample, and two of the use audit's 40 (R02744, R03578) moved beyond the first 50 of their
   period, which leaves 12 and 38; `samples/pdf_requests.xlsx` lists the other 220 (108 and 112) for the team to
   download through the library, in rank order (any first part of each stratum is itself a random sample).
   `samples/reserves.csv` (v0.15) adds 21 coverage and 3 use-audit reserves, listed last in `pdf_requests.xlsx`: the
   papers that join the samples if the 13 coverage records still unsure leave the screen under D28 (two more per
   period for the authors' corrections) and the next use-audit record of each period after its full-text part. Under
   D28 the coverage frame becomes the firm includes, so the 13 unsure records leave and the next in rank order join.
   **Library round (16 Nov 2026, v0.37).** The team saved 179 PDFs through the library on a shared Drive folder.
   `samples/library_pdfs_2026-11-16.csv` has one row per requested paper (243): whether a file is on the Drive, whether
   it is the paper, how its text was made (`pdftotext` as `fulltext_fetch.py` does, OCR for two scans, one excerpt of
   pages 74 to 85 of a book) and the team's note on any paper not obtained. 172 files give a usable text: 80 coverage
   papers, 78 use-audit targets and 14 reserves (12 and 2). Of the other seven, four are other papers (R00094 and
   R01369, found when converted; R00144 and R00339, found by both coders of the library round), two are previews
   (R00128, and the reserve R00110) and one was not requested (R05775). The fetch logs record the route (`library`) and
   the outcome of every request. With the library, 92 of the 120 coverage papers and 116 of the 150 use-audit targets
   have a full text; `samples/pdf_requests.xlsx` now lists the 71 still missing, reserves included. The reserves
   obtained are not coded: they join the samples only under D28 at the final merge.
7. **Coding** (`coverage/`, `useaudit/`): codebooks, instructions, tools, `coded.csv`, notes. AI sessions coded each
   coverage paper from its full text (label, decisions changed, class category, evaluation items, as the corpus was
   coded) and each use-audit record from its title and abstract, and from the full text where one was obtained.
   After the rulings (codebook addenda of 12 November: coverage v1.2, use audit v1.1), a separate session recorded the
   facts of the rulings from the full text of the 11 coverage papers coded eligible until then
   (`coverage/rulings_fulltext_facts.csv`, instructions `coverage/RULINGS_FULLTEXT_INSTRUCTIONS.md`);
   `scripts/analyze_samples.py` treats a paper whose method fails B or B2 as excluded at full text (R00308, ruling B).
   Another session coded again the 5 use-audit records that the first coding took to propose a
   method of their own (`useaudit/rulings_recode.csv`); under the rulings all 5 are applications. The code corrections
   of the independent check (6 records) are recode batches coverage 005 and use audit 018.
   Library round (v0.37): separate AI sessions coded the 82 new coverage texts (batches 006 to 019,
   `coverage/tools/make_coding_batches.py`) and coded the 78 use-audit targets again from their full texts (batches
   020 to 029, `useaudit/tools/make_recode_batches.py`; the last code of a record wins, so these replace the codes from
   title and abstract), under the same codebooks and instructions with the notes `coverage/ROUND2_NOTE.md` and
   `useaudit/ROUND2_NOTE.md`. The blind second coding of these records and its adjudication are round 2 of
   `d42/README.md`.
8. **Final merge (16 to 17 Nov 2026, v0.38).** In the Last Pass (16 Nov 2026) the team lead decided that the authors do
   not check the screen record by record and that no more papers will be obtained. The empty file `FINAL_MERGE` then
   switched on D28: the 383 records still unsure are excluded (E-UNSURE), so 3,096 records pass the screen and the
   coverage frame is the firm includes (47, 204, 524 and 2,321 by period). `make_samples.py` redrew the coverage
   sample from that frame: the 13 records of the sample that were unsure left it (R00004, R00084, R00308, R00379,
   R00640, R01304, R01526, R02709, R02885, R03697, R05572, R06485, R10073; 12 of them had a full text and codes,
   which stay in `coverage/coded.csv` but no longer count) and the next 13 in rank order joined (R00023, R00042,
   R00491, R00655, R00691, R00825, R00832, R01762, R02204, R03007, R03488, R10647, R11455). Five of the newcomers
   have no full text and count as not obtained; the other eight came through the library on 16 Nov and were coded by
   separate AI sessions (batches 020 and 021, with `coverage/ROUND2_NOTE.md`), coded again blind and adjudicated
   (round 3 of `d42/README.md`). The use audit is unchanged. Coverage: 88 of 120 papers obtained, 76 eligible.

## Results (v0.38, after the final merge; `decisions/search_numbers.json` holds every number the paper prints)

* Screen: 22,426 records; 3,096 pass (all included); 19,330 excluded, among them 14,738 under E1 (108 of them by the
  rulings pass) and 383 left unsure (E-UNSURE, D28). Includes by period: 47 / 204 / 524 / 2,321.
* Coverage sample: 88 of 120 with a full text, all assessed; 76 eligible (49 Core, 1 Partial, 26 Not counted). Against
  the corpus (Table 8): the same shape, fewer decisions changed (2.0 against 2.8 on average), more generators other
  than interpolation (34% against 21%), and lighter evaluations. D42 for these 88: 94.8% agreement of the coded
  values; 101 differences in force, 47 of them changed a first code; an author checked 55 settled codes, every change
  among them, and none needed correcting.
* Use audit: as below (unchanged by the final merge); an author checked 86 of its settled codes, none needed
  correcting.

## Results (v0.37, before the final merge)

* Screen: 22,426 records; 3,475 pass (3,092 include, 383 unsure: 332 under the rulings, 51 left by the
  independent check); 18,951 excluded (E1 14,738, of them 108 by the rulings pass; E-COMPARE 1,661, E-NOGEN 1,017,
  E-LANG 658, E-REVIEW 413, E2 218, E-WITHDRAWN 167, E-OTHER 79). Second look agreement 81.9% (kappa
  0.72) on the hard cases; first pass against the pilot 95.8% (kappa 0.859); independent check, blind, 579 of 596 (97.1%,
  kappa 0.94). (The paper's counts, after the authors' corrections, are those of `search_numbers.json`: 3,479 pass.)
* Includes by period against the corpus: 47 / 204 / 524 / 2,321 against 8 / 7 / 7 / 15 corpus methods;
  generative oversamplers 4% / 4% / 10% / 21% of the includes.
* Coverage sample: 92 of 120 with a full text, all assessed; 74 eligible (47 Core, 1 Partial, 26 Not counted). Against
  the corpus (Table 8, Section 4.4): the same shape (Core, two classes, training folds stated), fewer decisions changed
  (2.0 against 2.8 on average), more generators other than interpolation (35% against 21%), and lighter evaluations.
* Use audit: 289 of 300 are applications; medicine 106, finance 27, social 24, security 22, software 17; a decision
  about a person in 137. Full texts (116 obtained among the 150 targets, 110 of them applications): resampling fitted
  on the training data only stated in 41, before the split in 46 (37.0% with the periods weighted, 95% interval 25.6 to
  48.4; no trend across the periods), not said in 23; test data resampled in 46; a no-resampling comparator in 55;
  calibration assessed in 2; external validation in 6.

## Files

| Path | Content |
|---|---|
| `SCREENING_CODEBOOK.md`, `AGENT_INSTRUCTIONS.md` | Rules of the first two looks |
| `first_pass/`, `second_look/`, `adjudication/` | Outputs, manifests and notes of the three looks |
| `result/`, `final/` | First pass combined; first two looks combined, with the workbook for the authors' check |
| `decisions/` | One decision per record, its summary, and `search_numbers.json` |
| `rule_b/` | The rulings pass: codebook, instructions, tools, facts per batch, decisions, summary (`rule_b/README.md`) |
| `check/` | The check job of 11 November (lists, codebooks, workbook), the rulings workbook of 12 November, the independent AI check's corrections as its report lists them (`from_report/`) and, once supplied, its return files (`returns/`) |
| `person_overrides.csv` | The team's corrections (8 rows since v0.15: decision D30 of 12 November) |
| `FINAL_MERGE` (absent until the final merge) | Switches on D28: records still unsure are excluded (E-UNSURE) |
| `samples/` | The drawn samples, their reserves, their summary and the list of PDFs to download |
| `coverage/`, `useaudit/` | Codebooks, instructions, coding tools, codes, notes, fetch logs |
| `tools/`, `fulltext_tools/` | Screening tools and batch rebuilders; the open-access fetcher |

The batch files of the three looks hold abstracts and are not kept; `tools/make_batches.py` and
`adjudication/tools/make_adjud_batches.py` rebuild them byte for byte. Paths inside the tools are those of the
session's working folder; edit them to rerun.

## Team use only

The `quote` column of the screened files and `result/screen_all.csv`, the `abstract` column of `samples/*.csv` and of
`check/csv/*.csv`, the workbooks in `final/` and `check/`, and any full text are licensed or copyrighted material: strip
or leave them out before anything from this folder is deposited.

Cost, roughly: 146 screening batches at 300,000 to 500,000 tokens each and 18 coding batches at 120,000 to 280,000
tokens (from the session's usage reports), up to 20 sessions at a time; on 12 November the 15 sessions of the rulings
pass, and one recheck and two coding sessions of 100,000 to 310,000 tokens each.
