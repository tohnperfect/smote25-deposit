# SMOTE25 blind second pass, part 2 (WP3 Method and Evaluation forms; outcome rows with the metric rule)

You are an independent, blind second coder. A first coder already coded these papers; do NOT look for their codes.
Allowed files: this folder (`/home/claude/work/blind3/`), the paper texts `/home/claude/work/blind2/papers/<safe>.txt`
and PDFs `/home/claude/work/blind2/pdf/<safe>__*.pdf`. Never open `/home/claude/team-repo`, `/home/claude/work/pkg03`,
`/home/claude/work/corpus`, any other batch's outputs, or any file named like matrix, records, outcomes, atlas,
explorer, coded, ledger, verified, ai-draft, Method Map. Do not look the papers up online.

Every code needs a location: a page (printed number if visible, else `pdf p.N`), section, table or equation, and for
judgement calls a verbatim quote of at most 40 words in `notes`. Write `not stated` when the paper does not say.
The texts come from `pdftotext -layout`: grep -n for the passages you need and read those line ranges; do not read a
whole paper. When a table or algorithm is garbled, look at the PDF page with the Read tool (`pages` parameter).

## Method form (`method/batchN_to_fill.csv`; rules in `METHOD_coding_rules.md`)
Fill every column of each row as its header asks: class category B / M / B+M by what the paper shows its generator
doing (see the rules), the evidence, whether multiclass data were reduced to two classes, the link (Core / Partial /
Not counted), each of the six decision points changed relative to SMOTE (y/n with the page), whether the method removes
or moves original training examples (C3: y if the output training set lacks or alters any original example; dropping a
point from the seed set only is n), and whether k is chosen adaptively. Write `method/batchN_filled.csv`.

## Evaluation form (`eval/batchN_to_fill.csv`; scheme in `EVAL_coding_scheme_section7_1.tex`)
Fill every column as its header asks, from the paper's own experiments (counts of real and synthetic datasets, sources,
learner families, baselines, measures as printed, wrong or missing measure definitions, calibration measures, protocol,
whether resampling inside the training folds is stated, how settings were chosen: fixed / tuned inside training / on
evaluation data / not said, statistical tests, per-dataset results table, standard deviations, code release with link,
data modified before use, modified data released, reason given for the choice of data with a quote).
Write `eval/batchN_filled.csv`.

## Outcome rows with the metric rule (`outrule/batchN_to_fill.csv`)
Each row names a paper, a results table, a dataset row, a classifier and the SMOTE column. Choose the metric by this
fixed rule, then copy the two printed values exactly as printed:
1. G-mean if the table (or the set of tables for that classifier) reports it; else 2. AUC; else 3. F-measure (F1);
else 4. accuracy. Use the unperturbed condition (no added noise) and the classifier named in the row.
Fill `metric_selected` (as printed), `metric_rule_step` (1 to 4), `proposed_method_value`, `smote_value` and `note`;
`NR` if not printed; `?` plus a note if ambiguous. Write `outrule/batchN_filled.csv`.

## When done
Write `<kind>/batchN_DONE.txt` with anything the human adjudicator should look at first.
