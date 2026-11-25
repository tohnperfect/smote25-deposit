# Full title-and-abstract screen: instructions for one batch

You screen one batch of about 200 records of the systematic search of the SMOTE25 survey. Your batch number (three
digits, for example 007) is in your task. Below, NNN stands for it and S for `/home/claude/work/screen_full`.

1. Read `S/SCREENING_CODEBOOK.md` in full. It is the only rule book. Do not look anything up online, and open no file
   other than the codebook, these instructions, the tools below and the files they name for your batch.
2. Show records with `python3 -I S/tools/show.py NNN FIRST LAST` (records are numbered from 1 in batch order; for
   example `1 25`). Work through the batch in order, in chunks of 25.
3. For each chunk, write your decisions with the Write tool to `S/work/batchNNN_chunk.json`: a JSON array with one
   object per record, in order, with the keys `rec`, `decision`, `reason_code`, `reason`, `quote`, `tags`,
   `confidence` as the codebook defines them (`tags` is a string, items separated by `;`, empty if none; `quote` is
   at most 25 words copied from the title or abstract, empty if there is no abstract). Then run
   `python3 -I S/tools/add_rows.py NNN S/work/batchNNN_chunk.json`. It checks the rows, appends them to
   `S/out/batchNNN_screened.csv` and prints the next record number to show. If it reports an error, fix the JSON
   and run it again; nothing is appended until the whole chunk passes.
4. If you lose track (for example after a long pause), run `python3 -I S/tools/add_rows.py NNN --status`: it prints
   how many records are done and the next one to show.
5. When no records remain, write `S/out/batchNNN_DONE.txt`: the counts that `--status` prints, then in a few lines
   the records a person should look at first (low confidence, borderline calls, cases the codebook does not settle).
6. Reply with one line only: `batch NNN: n=..., include=..., unsure=..., exclude=...`.

Decide each record on its own merits; do not let the share of includes so far shape later decisions. Read every
title and abstract; keywords alone are not enough.
