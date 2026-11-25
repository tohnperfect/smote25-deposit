# Coverage sample: instructions for one batch

You code one batch of papers for the SMOTE25 survey. Your batch number (three digits) is in your task; below NNN
stands for it, C for `/home/claude/work/coverage` and T for `/home/claude/work/coding_tools`.

1. Read `C/COVERAGE_CODEBOOK.md` in full. It is the only rule book. Do not use the web. Open no files other than the
   codebook, these instructions, the tools below and the text files they point to.
2. For record K of the batch (K = 1, 2, ...), run `python3 -I T/show_item.py coverage NNN K`. It prints the title,
   the abstract and the path of the full text. Read the full text with the Read tool (in parts of about 600 lines if
   it is long): the method section, the experimental setup and the results tables. Text extracted from a PDF can
   be out of order around tables and figures; read around them.
3. Code the record under the codebook, then write it with the Write tool to `C/work/batchNNN_chunk.json` (a JSON
   array with one object, or a few objects for consecutive records, keys exactly as the codebook names them, all
   values as strings) and run `python3 -I T/add_codes.py coverage NNN C/work/batchNNN_chunk.json`. It checks the
   values and appends the rows; fix any error it reports and run it again. Code one record at a time, in order.
4. `python3 -I T/add_codes.py coverage NNN --status` tells you how far you are.
5. When no records remain, write `C/out/batchNNN_DONE.txt` with the counts and, in a few lines, the codes a person
   should check first (borderline labels, decision points you were unsure of).
6. Reply with one line only: `coverage batch NNN: n=..., eligible=..., Core=..., Partial=..., Not counted=...`.
