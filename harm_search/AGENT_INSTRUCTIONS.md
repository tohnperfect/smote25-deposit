# WP5 harm search: instructions for one batch

You screen one batch of PubMed records for the SMOTE25 survey. Your batch number (two digits, for example 03) is in
your task. Below, NN stands for it and H for `/home/claude/work/v08/wp5/harm_search`.

1. Read `H/HARM_SCREEN_CODEBOOK.md` in full. It is the only rule book. Do not look anything up online, and open no
   file other than the codebook, these instructions and what the tools below print.
2. Show records with `python3 -I H/scripts/harm_tools.py show NN FIRST LAST` (records are numbered from 1 in batch
   order). Work through the batch in order, in chunks of 25.
3. Decide each record yourself from its title and abstract under the codebook. Read every abstract; no keyword
   decides a record. Most records found by the calibration query concern prediction models that use SMOTE and report
   a calibration curve without any comparison with a model trained without resampling: those are excluded
   (X-no-comparison), with `harms` set to `calibration`.
4. For each chunk, write your decisions with the Write tool to `H/work/chunk_NN.json`: a JSON array with one object
   per record, in order, with exactly the keys `pmid`, `decision`, `code`, `harms`, `comparison`, `finding`, `data`,
   `domain`, `reason`, `quote`, `confidence`, every value a string, as the codebook defines them. Then run
   `python3 -I H/scripts/harm_tools.py add NN H/work/chunk_NN.json`. It checks the rows (allowed values; the quote is
   copied exactly from the title or abstract and has at most 25 words) and appends them. If it reports an error, fix
   the JSON and run it again; nothing is appended until the whole chunk passes.
5. `python3 -I H/scripts/harm_tools.py status NN` tells you how far you are.
6. When every record is decided, write `H/work/decisions/batch_NN_DONE.txt`: the counts that `status` prints, then in
   a few lines the includes and unsure records a person should read first and any case the codebook does not settle.
7. Reply with one line only: `harm batch NN: n=..., include=..., unsure=..., exclude=...`.
