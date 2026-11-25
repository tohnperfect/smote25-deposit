# Rulings B, B2 and C: the pass over the included records (12 November 2026)

During the independent AI check of the screen (Claude Fable 5.2, report v3 of 11 November 2026, project doc
`claude/smote25-ai-check-report-v3-2026-11-11.md`) the team lead settled the questions it raised by rulings: A (records that
their repository removed are excluded, E-WITHDRAWN; `../withdrawn_records.csv`, `scripts/withdrawn_rule.py`), B and B2
(what counts as a method of the paper's own), C (the task does not decide scope) and D (a basis for two codes of the
use audit). On 12 November he confirmed B, B2 and D for the whole screen (D24), kept every task in scope (D25) and
decided that a record failing B or B2 is excluded only when the pass below recorded its facts with high confidence;
otherwise it is unsure (U-rule-B) and goes to the authors' check or to full text (D26).

## What was done, and by whom

* `RULE_B_CODEBOOK.md` states the rulings and the six facts to record; `AGENT_INSTRUCTIONS.md` is what each session
  received.
* `tools/make_batches.py` put the 2,933 records that the screen then included in a random order (SHA-256 of seed
  20261118 and the record id) and cut 15 batches (14 of 196, one of 189); `rule_b_manifest_PRIVATE.json` lists them.
  The batch files hold abstracts and are not kept; the tool rebuilds them byte for byte from the draft folder.
* Fifteen AI sessions (Claude Opus 5.5 subagents, one per batch, none seeing another's output) recorded the facts of
  every record from its title and abstract with `tools/show.py` and `tools/add_rows.py`, which checks every value
  (`out/batchNNN_facts.csv`, `out/batchNNN_DONE.txt` with the records a person should look at first). The session of
  batch 004 changed one row by hand after appending it (R00878, own to unclear, to match R00298) and says so in its
  note; the record is kept either way.
* `scripts/rule_b_decide.py` applies the rulings (the rule itself is `scripts/rulings.py`, shared with the full-text
  stage of the coverage sample) and writes `rule_b_decisions.csv` and `rule_b_summary.json`;
  `scripts/screen_decide.py` takes the result into the decisions.

## Result

| | Records |
|---|---|
| Read | 2,933 (scheme own 2,258, existing parts 593, unclear 82) |
| Fail B or B2 | 484 (B 177, B2 307); 115 with high confidence, 369 with medium or low |
| Task other than plain classification (kept in scope by C) | 46 |
| Decided by the rulings since v0.13 (the 2,634 includes outside the independent check's lists) | 108 excluded under E1 (B 26, B2 82); 332 unsure, U-rule-B (B 133, B2 199) |

In v0.12, before the independent check was merged, the rulings decided all 2,933 (115 excluded, 369 unsure). Since
v0.13 the check's decision is final for the 299 records of its sample of includes, so the pass decides the other 2,634.

The pass reads more strictly than the independent check. On the check's random sample of 300 includes (299 read by
both; R21465 is a removed deposit) it fails 44, among them all 10 that the check excluded under B or B2 (agreement 265
of 299, Cohen's kappa 0.33); with only the high-confidence failures excluded it would exclude 7, 5 of them among the
check's 10, and send 37 to unsure (agreement 292 of 299, kappa 0.58). The comparison uses the check's return file
(`../check/returns/`); in v0.12, before the file arrived, it used the 11 corrections the check's report lists
(`../check/from_report/`), with the same result. The check's second pass (`../check/returns/second_pass_facts.csv`)
excludes 14 of the 299: the 10 it corrected under B or B2, and 4 for other reasons (language, purpose, no synthetic
examples) that it flagged as differences in its return file without correcting them.

## Files

| Path | Content |
|---|---|
| `RULE_B_CODEBOOK.md`, `AGENT_INSTRUCTIONS.md` | Rules and instructions of the pass |
| `tools/` | Batch builder, record viewer, row checker |
| `out/` | The facts of each batch and the notes of each session |
| `rule_b_manifest_PRIVATE.json` | Seed and the records of each batch |
| `rule_b_decisions.csv`, `rule_b_summary.json` | One decision per record read; counts and the comparison with the check |

The facts hold no text copied from the records (the `reason` column is written by the sessions), so they can be
deposited.
