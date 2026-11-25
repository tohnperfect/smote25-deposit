# Use audit: instructions for one batch

You code one batch of papers for the SMOTE25 survey. Your batch number (three digits) is in your task; below NNN
stands for it, U for `/home/claude/work/useaudit` and T for `/home/claude/work/coding_tools`.

1. Read `U/USE_AUDIT_CODEBOOK.md` in full. It is the only rule book. Do not use the web. Open no files other than the
   codebook, these instructions, the tools below and the text files they point to.
2. For record K of the batch (K = 1, 2, ...), run `python3 -I T/show_item.py useaudit NNN K`. It prints the title,
   the abstract and, where there is one, the path of the full text. With a full text, read it with the Read tool (in
   parts of about 600 lines if it is long), above all the data, methods and validation sections; look for where and
   when the resampling was applied relative to the train/test split or the cross-validation, and on which data the
   reported results were computed. Without a full text, code from the title and abstract (`source` = abstract).
3. Code the record under the codebook, then write it with the Write tool to `U/work/batchNNN_chunk.json` (a JSON
   array with one object, or a few objects for consecutive records, keys exactly as the codebook names them, all
   values as strings) and run `python3 -I T/add_codes.py useaudit NNN U/work/batchNNN_chunk.json`. It checks the
   values and appends the rows; fix any error it reports and run it again. Keep batch order.
4. `python3 -I T/add_codes.py useaudit NNN --status` tells you how far you are.
5. When no records remain, write `U/out/batchNNN_DONE.txt` with the counts and, in a few lines, the codes a person
   should check first.
6. Reply with one line only: `useaudit batch NNN: n=..., fulltext=..., application=..., inside_folds stated=..., before-split=...`.
