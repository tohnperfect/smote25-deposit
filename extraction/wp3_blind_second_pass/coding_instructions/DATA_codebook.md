# SMOTE25 blind second pass: Data extraction (codebook)

You are the second, independent coder of the Data extraction of the SMOTE25 survey. A first coder already coded these
papers. You must NOT see the first coder's values: work only from the paper texts and PDFs in this folder.

## Hard rules

1. Open only these files: `blind2/CODEBOOK.md`, your batch folder `blind2/batchNN/`, `blind2/papers/<key>.txt`
   and `blind2/pdf/<key>__*.pdf`. Never open anything under `/home/claude/team-repo`, `/home/claude/work/corpus`,
   any `*.csv`/`*.json`/`*.xlsx` outside your batch folder, or any file whose name contains `matrix`, `records`,
   `outcomes`, `atlas`, `explorer`, `coded`, `ledger`, `verified` or `ai-draft`. Do not search the web for the papers.
2. Copy printed values exactly as printed: no rounding, no conversion, no computing (e.g. `1,484`, `0.8363`, `1:28.1`, `12.5%`).
3. If the paper does not print a value at all, write `NR`. If you cannot find the row or it is ambiguous, write `?` and
   explain in `note`.
4. Every code other than "not stated" must be backed by evidence: the page (the number printed on the page if visible,
   else `pdf p.N`) and a verbatim quote of at most 40 words copied from the paper.
5. Never guess the authors' intention. If the paper does not say it, the code is "not stated".
6. The text files come from `pdftotext -layout`; tables can be garbled. When a table is unreadable in the text, look at
   the PDF page itself with the Read tool (`pages` parameter) before writing `?`.
7. Work paper by paper and write each paper's result file as soon as it is done (so nothing is lost if you stop).

## Part A: one JSON file per paper, `blind2/batchNN/out/<safe_key>.json`

```json
{
 "data_key": "<as given in papers.json>",
 "evaluates_on_data": "yes | no",
 "sources": ["subset of: UCI, KEEL, OpenML, UCR, LibSVM, imbalanced-learn, Kaggle, Image, Text, Private, Synthetic, Other"],
 "crit": "the selection rationale the paper gives for its datasets, close to its wording, or 'not stated in paper'",
 "crit_type": "own reason | cites prior work | generic only | not stated | n.a.",
 "basis": ["subset of: diversity, difficulty, method-target, application, prior-work, popularity, threshold rule, random draw, preregistered, replicability, analytic"],
 "benchmark_inherited_from": "the prior work whose dataset list was reused, as the paper itself says, or 'not stated in paper'",
 "origin": ["subset of: Natural, Binarised, Class-merged, Class-resized, Undersampled, Noise-injected, Induced profile, Generated"],
 "binarised_by": "authors | repository | both | n.a.",
 "minority_rule": "explicit target listed | smallest class vs rest | repository-defined | mean-size or IR threshold | induced by authors | not defined | not stated | n.a.",
 "modified_data_released": "yes | on request | no | n.a.",
 "evidence": [{"field": "crit_type", "page": "p.5", "quote": "..."}],
 "notes": "anything odd: typos, sums that do not add up, image tables, supplementary-only information"
}
```

Definitions.

- `evaluates_on_data`: the paper runs any evaluation on datasets (real or synthetic), including a single illustration
  on generated data. A survey or a theory paper without any experiment is `no`; then every other code is `n.a.`.
- `sources`: where the datasets come from, as the paper states it (count a source if at least one dataset comes from it).
  `Private` = the authors' or a partner's own data not in a public repository. `Synthetic` = generated data.
- `crit_type`, the reason given for choosing these datasets:
  - `own reason`: the paper gives a reason of its own (for example to cover a range of imbalance ratios, sizes, numbers
    of classes or domains; to test overlap, noise or another difficulty; because the data match the setting the method
    targets; because an application needs it; a written selection rule such as IR > 9).
  - `cites prior work`: the paper says it uses the datasets of, or selected as in, earlier work (it names or cites the
    source of the list) and gives no reason of its own.
  - `generic only`: the only justification is generic, such as "widely used", "commonly used", "well-known benchmark".
  - `not stated`: no reason at all.
  - `n.a.`: no evaluation on data.
  - Precedence when several apply: own reason > cites prior work > generic only > not stated. Record every applicable
    kind in `basis`.
- `basis` (all that apply): `diversity` (varied IR, size, dimension, classes or domains), `difficulty` (overlap, noise,
  borderline, small disjuncts, hardness), `method-target` (the data match what the method is for: multiclass,
  high-dimensional, time series, images, ...), `application` (a domain need), `prior-work` (follows earlier work),
  `popularity` (widely used), `threshold rule` (a written rule on IR, size or similar), `random draw`, `preregistered`,
  `replicability` (chosen because public or reproducible), `analytic` (chosen to control or demonstrate a property,
  e.g. synthetic data with a set overlap).
- `origin` (all that apply), how the data reached the experiment:
  - `Natural`: at least some datasets are used as distributed, with their native classes.
  - `Binarised`: a multiclass source was reduced to two classes, by the authors or by a repository (a two-class KEEL file
    such as `yeast-0-5-6-7-9_vs_4` counts). Also fill `binarised_by`.
  - `Class-merged`: classes were merged (other than one-vs-rest binarisation).
  - `Class-resized`: class sizes were changed in another way than removing minority examples (e.g. resampled to a set size).
  - `Undersampled`: minority examples were removed (at random or otherwise) to raise the imbalance ratio.
  - `Noise-injected`: label noise, attribute noise, outliers or missing values were added by the authors.
  - `Induced profile`: an imbalance profile was created from balanced data (typical for image datasets: step or long-tail).
  - `Generated`: synthetic data generated by the authors (or by a generator they describe).
- `binarised_by`: `authors` if the authors reduce the classes themselves, `repository` if they use ready-made two-class
  splits, `both`, or `n.a.` if nothing is binarised.
- `minority_rule`, whether and how the paper says which class is the minority:
  - `explicit target listed`: the minority class (or classes) is named per dataset, in the text or in a table.
  - `smallest class vs rest`: one written rule for all datasets: the smallest class is the minority, the rest the majority.
  - `repository-defined`: the split comes from the repository file name (e.g. KEEL `glass-0-1-6_vs_2`) and the paper adds no rule.
  - `mean-size or IR threshold`: (multiclass) classes below the mean class size, or above an IR threshold, count as minority.
  - `induced by authors`: the authors decide the minority while creating the imbalance (e.g. undersample class k).
  - `not defined`: (multiclass) the paper keeps the native class distribution and never defines a minority.
  - `not stated`: data were binarised or modified, but the paper does not say which class is the minority.
  - `n.a.`: all data are natively two-class, or there is no evaluation on data.
- `modified_data_released`: only for papers whose origin includes something the authors did themselves (Binarised by
  authors, Class-merged, Class-resized, Undersampled, Noise-injected, Induced profile): `yes` if the paper gives a
  link, repository or supplementary file holding the modified datasets themselves (not just the code or the original
  data); `on request` if it says they are available on request; `no` otherwise. `n.a.` if the authors modified nothing.

## Part B: fill the rows of your batch's two CSV files

`datasets_to_fill.csv`: for each row, find the dataset in the paper (use `where`, `pdf_page_hint`, `row_order_in_paper`
and `name_as_printed`) and copy `n_instances`, `n_features`, `n_classes`, `n_minority`, `ir_as_printed` exactly as
printed (the IR in the printed form, including `1:` or `%`). `NR` if the paper does not print that value; `?` plus a
note if you cannot find or cannot read the row.

`outcomes_to_fill.csv`: for each row, find the table (`table`, `page`, `pdf_page_hint`), the dataset row
(`dataset_as_printed`), the classifier (`classifier`) and the SMOTE column (`smote_column`), and copy the value of the
proposed method, the value of SMOTE and the metric name, exactly as printed.

Write the filled CSVs as `blind2/batchNN/datasets_filled.csv` and `blind2/batchNN/outcomes_filled.csv` (same columns,
same row order). Do not change the other columns.

## When you finish

Write `blind2/batchNN/DONE.txt` with one line per paper: key, minutes spent (estimate), and anything a human adjudicator
should look at first.
