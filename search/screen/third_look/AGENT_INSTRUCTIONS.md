# Adjudication of disputed screening decisions: instructions for one batch

Two screeners have already screened every record of your batch on title and abstract, separately and blind to each
other, and they did not settle it: they disagree, or at least one of them said unsure. You are the third screener and
your decision settles the record for now (a person will check it later). Your batch number (three digits, for example
007) is in your task. Below, NNN stands for it and S for `/home/claude/work/screen_adjud`.

1. Read `S/SCREENING_CODEBOOK.md` in full. It is the only rule book. Do not look anything up online, and open no file
   other than the codebook, these instructions, the tools below and the files they name for your batch.
2. Show records with `python3 -I S/tools/show.py NNN FIRST LAST` (records are numbered from 1 in batch order; for
   example `1 25`). Each record shows the title, the abstract, the keywords and then the decisions, codes,
   confidences and reasons of screener A and screener B. Work through the batch in order, in chunks of 25.
3. Decide each record yourself from the title and abstract under the codebook. Use the two earlier reasons as
   arguments to weigh, not as votes: if one of them points to something in the abstract that settles the record,
   follow the abstract. Prefer a firm decision. Use `unsure` only when the record has no abstract and its title does
   not settle it, or when the abstract cannot tell whether the paper proposes a method of its own (code
   U-new-or-applied); an unsure record goes on to full-text assessment, so do not use it to avoid a hard call.
4. For each chunk, write your decisions with the Write tool to `S/work/batchNNN_chunk.json`: a JSON array with one
   object per record, in order, with the keys `rec`, `decision`, `reason_code`, `reason`, `quote`, `tags`,
   `confidence` as the codebook defines them (`reason` in one sentence that says what settles it; `tags` is a
   string, items separated by `;`, empty if none; `quote` is at most 25 words copied from the title or abstract that
   settle the decision, empty if there is no abstract). Then run
   `python3 -I S/tools/add_rows.py NNN S/work/batchNNN_chunk.json`. It checks the rows, appends them to
   `S/out/batchNNN_screened.csv` and prints the next record number to show. If it reports an error, fix the JSON
   and run it again; nothing is appended until the whole chunk passes.
5. If you lose track, run `python3 -I S/tools/add_rows.py NNN --status`.
6. When no records remain, write `S/out/batchNNN_DONE.txt`: the counts that `--status` prints, then in a few lines
   the records a person should look at first and any case the codebook does not settle.
7. Reply with one line only: `batch NNN: n=..., include=..., unsure=..., exclude=...`.
