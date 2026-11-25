# Checks of the screen and of the sample codes

Team use only: the lists and workbooks here hold licensed abstracts.

## The check job of 11 November 2026

`CHECK_JOB_HANDOFF.md`, `csv/1_unsure.csv` to `csv/5_useaudit_codes.csv`, `codebooks/` and
`SMOTE25_team_check_2026-11-11.xlsx` are the job given to the authors and to any independent AI checker: the 1,222
records the three looks left unsure, a random 300 of the includes and of the exclusions, and the AI codes of the two
samples. `RETURN_screen_decisions.csv` and `RETURN_code_checks.csv` are the empty return templates. The codebooks in
`codebooks/` are the versions the checkers received (before the rulings).

## The rulings workbook of 12 November 2026

`SMOTE25_rulings_check_2026-11-12_v2.xlsx` (`scripts/make_rulings_check.py`; the same rows in
`csv/7_rulings_unsure.csv`, `csv/8_rulings_excluded.csv` and `csv/9_check_task_exclusions.csv`) lists the records that
the rulings pass made unsure (332) or excluded (108) outside the independent check's lists, and 8 exclusions of the
independent check whose notes tie the decision at least partly to a task that ruling C keeps in scope. Its README
states the rulings, which also apply to the authors' check of the earlier workbook. Version 1 (369 and 115 records, no
sheet 9) went out with v0.12, before the check was merged; version 2 replaces it. The authors' decisions come back
through `../person_overrides.csv`.

## The independent AI check (Claude Fable 5.2), merged in v0.13

The team lead supplied its return files on 12 November (`SMOTE25_AI_check_returns_v3_2026-11-11.zip` in
`~/Downloads/SMOTE25/`). `returns/` holds what the merge uses and what documents it:

* `RETURN_screen_decisions_AI-Claude-Fable-5.2_2026-11-11_v3.csv` (1,366 rows: all 1,222 records of list 1, and the
  rows of lists 2 and 3 with a correction or a note), read by `scripts/screen_decide.py`: the check's decision is final
  for every record of its three screening lists (an empty decision in lists 2 and 3 means it agrees);
* `RETURN_code_checks_AI-Claude-Fable-5.2_2026-11-11_v3.csv` (81 rows), applied by
  `scripts/apply_check_code_corrections.py` as a recode batch of each sample (coverage 005, use audit 018);
  `applied_code_corrections.csv` lists the 8 fields changed in 6 records, before and after;
* `second_pass_facts.csv`, the facts of its pass under rulings B and B2, which `scripts/rule_b_decide.py` compares
  with the rulings pass;
* `SMOTE25_AI_check_report_v3_2026-11-11.md`, its report (also in the project), and `method/`: its session
  instructions, the blind decisions on the two samples (from which `scripts/search_numbers.py` computes the agreement
  that Section 3.4 prints), the Zenodo status it fetched, the fetch log of its open copies and its batch manifest.

Its lists with abstracts (`lists/` in the zip) are not copied here: they repeat the return files with the licensed
abstracts. `from_report/` holds the 11 sample corrections as its report lists them, which v0.12 used before the files
arrived; it is no longer read when `returns/` is present.
