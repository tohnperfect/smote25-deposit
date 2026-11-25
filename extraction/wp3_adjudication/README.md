# WP3: AI adjudication of the blind second pass (12 November 2026)

Decision D31 of the team lead (12 Nov 2026): an AI session adjudicates every disagreement of the blind second pass, and
he spot-checks the result. Decisions D32 to D36 set the conventions. The adjudication was made by Claude Opus 5.5 in the
v0.16 session; the spot check is on the page "SMOTE25 WP3 Check" (`wp3/check_page/`).

## Conventions (decisions of the team lead, 12 Nov 2026)

| Decision | Question | Rule |
|---|---|---|
| D32 | Class count of a two-class set that the paper does not print | record 2, flagged `inferred` |
| D33 | A value that follows exactly from printed numbers (a minority size read off a class distribution, a total as the sum of printed class sizes) | counts as printed, flagged `derived`; a value that needs a rounded ratio or percentage (size and IR) is not derived |
| D34 | "Own reason" against "cites prior work" for the choice of data | merged into "reason given"; a remark that the sets are widely used counts as no reason |
| D35 | Which variant is "the proposed method" when a paper proposes several | the variant the abstract names as the contribution; if several, the first named; if none, the first the paper names |
| D36 | "Modified data released" | the modified files themselves are public; code that regenerates them, data on request or the unmodified sets do not count |

## What was done

1. Every disagreement adjudicated from the paper text (pdftotext of the corpus PDFs; tables without a text layer read on
   the rendered page): `adjudicate_data_extraction.py` (269 values), `adjudicate_data_handling.py` (109 codes),
   `adjudicate_method_evaluation.py` (4 Method and 11 Evaluation codes). Each row keeps both passes, the adjudicated
   value, a flag (`printed`, `derived`, `inferred`) where it applies, the reason and the page.
2. D36 read in 27 papers: the 11 that any of the three readings named, the 15 others among the 44 papers that modify
   data (the 43 of the Data section and GLOS) whose text has a release-type sentence (a keyword scan with the reference
   list cut off; 7 papers match only through cross-references and are listed as such), and GLOS, which has none. The
   first run read 18 of them; the scan, written into the script afterwards, added 8 whose sentences are about code or
   unmodified data. `adjudicate_d36.py` runs the scan, checks every quote against the text and stops if a quote is
   missing or a match is left undecided. Result: 9 of the 44 papers that modify data publish the modified files (CTGAN/TVAE, DSRBF/Static-SMOTE, GAMO, G-SMOTE, HDE, INOS, k-means SMOTE,
   OVO-SMOTE, SMOTE-IPF). The Data list (3) kept only explicit sentences; the Evaluation list (10) adds KNNOR, which
   modifies no data in the Data definition; the second pass found 7 and coded MC-MBRC "on request" (not public).
3. GLOS: the second pass coded an induced imbalance profile; the paper says it modified Segment and Texture into
   imbalanced cases (PDF p.13), while the verified sheet coded the six entries original or repository-defined by its name
   rules. `glos_recount.py` reproduces every printed number of Section 5 from the team's files first (it stops otherwise),
   then recodes the six entries: 44 papers and 347 entries modify data; Table 9 and the paragraphs of Section 5.2 change;
   990 verifiable entries (GLOS's Segment no longer counts as a public file).
4. D35 applied to the whole wins analysis: see `data/d35/README.md` (four papers; 79.5% becomes 79.0%; the models of
   Section 5.5 move in the same direction).
5. The 351 sampled agreements (a seeded fifth of each form) checked against the papers: `check_agreements.py` (text
   layer, then OCR of the cited page, then the rendered page by eye; `AGREEMENTS_manual_checks.csv` for the 63 codes and
   the values read by hand). No agreed value was wrong; 13 values that both passes left blank follow from the paper
   under D32 (9) or D33 (4); 52 blanks stay blank because the verified sheet records nothing printed from which they
   follow.
6. `wp3_summary.py` writes the agreement, kappa and changes per field (`WP3_summary.md`, `WP3_summary.json`), which
   Section 3.7 reports.

## Results (`WP3_summary.md`)

- Data extraction, 1,706 values: the passes agree on 84.2%. The adjudication corrected 13 values (0.8%) and filled 112
  blanks (6.6%), mostly minority sizes and feature counts that follow from printed numbers (D33); 116 class counts keep
  the first pass's 2 (D32).
- Data-handling codes, 736 codes: agreement 0.67 to 0.97, kappa 0.29 to 0.75; 65 codes changed (8.8%). After it, 67 of
  73 papers give a reason for their data (D34) and 47 have data binarized by anyone (37 in the first pass).
- Method form, 88 codes of 11 papers: agreement 0.91 to 1.00, kappa 0.84 to 1.00; 2 decision points corrected (NROMM
  seed selection, RSMOTE neighbor choice).
- Evaluation form, 135 codes of 15 studies: agreement 0.60 to 1.00, kappa 0.43 to 1.00; 8 corrected, 4 of them on how
  the settings were chosen.

## What the paper uses

The counts of the survey rest on the verified sheets. The sample corrections are recorded here and are not
extrapolated, except where a correction or a convention applies to a whole count: the papers that modify or release
data and the papers that give a reason (Table 5, Section 5.2), and the variant taken in four papers (Section 5.5). The
numbers that changed are registered in `scripts/adjudicated_numbers.json`, which `scripts/check_numbers.py` and
`scripts/build_ledger.py` read.

## The spot check (D31; merged in v0.31, 15 November 2026)

The spot check on the page "SMOTE25 WP3 Check" (`wp3/check_page/`) decided all 80 items: 79 agree, 1 change.
`scripts/merge_wp3_check.py` turned the export (`wp3/check_page/exports/smote25_wp3_check_2026-11-15.csv`) into
`WP3_spot_check_summary.json` (per group and per form, items and decisions) and `WP3_spot_check_changes.csv`.

The one change was a request, not a new value: RBO, "modified files themselves public" (D36), AI value "no", with
"Check the project page" and the note "Try to access". A session checked the page the paper names
(`RBO_project_page_check_2026-11-15.md`): the repository holds code, KEEL download links, the 5x2 fold partitions as
row-index files and per-fold results; the noise is added at run time with no fixed seed, so the noisy files are not
public. The decision stays "no", with high confidence; `adjudicate_d36.py` records the check in `SPOT`, and its rerun
changes only RBO's confidence, note and `decided_by` and adds a `spot_check` entry to `MODIFIED_RELEASED_summary.json`.
`wp3_summary.py` reran unchanged. No number of the paper changes (9 of the 44 papers that modify data publish the
modified files).

Section 3.7 reports the check in a paragraph rendered from `scripts/search_templates/k_wp3_spot.tex` with keys of
`scripts/search_numbers.py` (wording checks: the groups named add up to the 80, every Method and Evaluation correction
was checked, the samples are proper samples of their frames, and the one change is RBO's and changed no value).

What the check did not cover in full: the "Must check" tab held every D36, GLOS and D35 decision, but two counts of
Table 5 also move through data-handling adjudications that were checked only by sample. The papers that give a reason
for their data are 62 of 73 with the first-pass codes under D34 and 67 after the adjudication: 9 papers change status
(Borderline-SMOTE, DGOT, GLOS, GOIO, k-means SMOTE, Loyalty-SMOTE and RSMOTE gain a reason; SMOTEBoost and
EasyEnsemble / BalanceCascade lose it), and none of the 9 was among the 10 data-handling changes drawn for the check.
The papers whose data are binarized by anyone are 37 with the first pass and 47 after it (a count Table 5 prints but no
sentence uses); 3 of those changes (AB-SMOTE, CBHSID, Loyalty-SMOTE) were checked.

Since 15 November (after v0.33) the 9 reason changes and the 7 binarization changes not drawn are on the page "SMOTE25
WP3 Count Check" for an author's check (`../count_check/README.md`). Building it, the session read the passages again
and marked three cards to look at first: SMOTEBoost (the conclusion, printed p.117, describes the data sets as "a diverse
test bed", which the AI's reason does not mention), DGOT (the AI's sentence is from the ablation study) and OREM-M (the
two entries the AI relies on, Vowel5 and Vowel4, have 5 and 4 classes in Table 6). The merge writes
`WP3_count_check_summary.json` and `WP3_count_check_changes.csv` here.
Merged in v0.34 (15 November): the author agreed with all 16, the three marked cards among them, so no value changed
and the counts stand (67 of 73 give a reason; 47 binarized by anyone). With this check, the gap described above is
closed: every data-handling adjudication that moves a count of Table 5 has been checked by a person.
