# Withdrawn Zenodo deposits among the search records (checked 11 November 2026, 10:46 to 10:58 UTC)

Trigger: the independent AI check of the screen (project doc `claude/smote25-ai-check-report-2026-11-11.md`, by
another model) found 150 Zenodo deposits among the records it read that Zenodo had removed as spam, and asked for a
check of every record with a `10.5281/zenodo.` DOI.

`scripts/zenodo_status.py` asked the Zenodo API (`https://zenodo.org/api/records/<id>`, one request per second, no
token) about all 367 such records of `data/search/2026-11-11/wp4_records_merged.csv.gz`; one row per record, with the
HTTP status and the tombstone's removal date, reason and note, is in `zenodo_status_2026-11-11.csv`.

| Result | Records |
|---|---|
| Available (HTTP 200) | 200 |
| Removed (HTTP 410) | 167: spam 164 (159 removed on 7 Sep 2026, tombstone note "User was blocked"), retracted 1, no reason given 2 |

The removed records by screen decision: include 11 (R04291, R16057, R19456, R19900, R20091, R20204, R20500, R21465,
R21517, R21521, R21741), unsure 149, exclude 7. One removed record is in the coverage sample (R17106, period P4,
rank 22; not yet coded, and on the PDF request list, where it can never be retrieved); none is in the use-audit sample.
All but six of the 167 are dated 2026 (all records with a Zenodo DOI: 314 of 367 dated 2026), and 359 of the 367
came from OpenAlex only.

Nothing was changed. DECISION for the team: a rule for removed records (for example: exclude a record whose only
version was removed by its repository, with a reason code of its own, and report the number in the PRISMA flow).
If the rule excludes them, the 11 includes and 149 unsure records go into `person_overrides.csv` with that code,
R17106 is replaced in the coverage sample by the next record of its stratum (the sampling rule keeps every other
record in place), and the chain of the README regenerates every count.
