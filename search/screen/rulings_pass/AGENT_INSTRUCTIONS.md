# Rulings B, B2 and C on the included records: instructions for one batch

You record facts about one batch of about 200 records that the SMOTE25 screen included. Your batch number (three
digits, for example 007) is in your task. Below, NNN stands for it and S for `/home/claude/work/rule_b`.

1. Read `S/RULE_B_CODEBOOK.md` in full. It is the only rule book. Do not look anything up online, and open no file
   other than the codebook, these instructions, the tools below and the files they name for your batch.
2. Show records with `python3 -I S/tools/show.py NNN FIRST LAST` (records are numbered from 1 in batch order; for
   example `1 25`). Work through the batch in order, in chunks of 25.
3. For each chunk, write your facts with the Write tool to `S/work/batchNNN_chunk.json`: a JSON array with one object
   per record, in order, with the keys `rec`, `scheme`, `generator`, `presented`, `compared`, `task`, `confidence`,
   `reason`, using the values of the codebook. Then run `python3 -I S/tools/add_rows.py NNN S/work/batchNNN_chunk.json`.
   It checks the rows, appends them to `S/out/batchNNN_facts.csv` and prints the next record number to show. If it
   reports an error, fix the JSON and run it again; nothing is appended until the whole chunk passes.
4. If you lose track, run `python3 -I S/tools/add_rows.py NNN --status`: it prints how many records are done and the
   next one to show.
5. When no records remain, write `S/out/batchNNN_DONE.txt`: the counts that `--status` prints, then in a few lines the
   records a person should look at first (low confidence, borderline calls, cases the codebook does not settle).
6. Reply with one line only: `batch NNN: n=..., own=..., existing-parts=..., unclear=...`.

Judge each record on its own merits; do not let the counts so far shape later records. Read every title and
abstract; keywords alone are not enough.
