# SMOTE25 check job: report of the AI check, version 3 (11 November 2026)

For the merge at the end. **Version 3 replaces the return files of versions 1 and 2** (reports
`claude/smote25-ai-check-report-2026-11-11.md` and `claude/smote25-ai-check-report-v2-2026-11-11.md`). It applies
the rulings the team lead gave the checker on 11 November (18:45 and 19:11, Bangkok). The manuscript, the codebooks
and `person_overrides.csv` were not touched.

This is still an **independent AI check** (checker `AI:Claude Fable 5.2`), not the authors' check. Nothing here has
been checked by a person. The rulings are not yet in any codebook: once the team adopts them, the codebooks and
Section 3 must state them, and the full screen (not only these lists) must be brought under the same rules.

## 1. The rulings as applied

| | Ruling | How it was applied | Rows it changed against the first check |
|---|---|---|---|
| A | A record that Zenodo has removed is excluded | `exclude`, `E-OTHER`, `ZENODO-WITHDRAWN` in `note` | 149 unsure, 1 sampled include |
| B | A chain of existing resampling methods counts as the paper's own only if the paper presents it as its contribution **and** compares it with at least one other way of resampling | Second pass over 1,245 records (version 2) | 160 unsure includes excluded; 7 sampled includes excluded |
| B2 | **New in version 3.** A standard generator used without a stated change (plain GAN, conditional GAN, WGAN-GP, CTGAN, VAE, diffusion or language model, KDE or GMM sampling, copula, standard augmentation) never counts as the paper's own, also when it is chained with other steps and compared | Recomputed from the stored facts; no record re-read | 50 more unsure includes excluded; 3 sampled includes excluded; the 6 sampled exclusions that version 2 moved to include stay excluded |
| C | Task scope: decided by the team lead at the merge | Included as if classification, `TASK-SCOPE: <task>` in `note` | 21 unsure includes tagged |
| D | Metric arithmetic is accepted as a basis for `before-split` and `test_balanced` | `BASIS:` in `note` | R00847, R10600, R01960 |

What still counts as an include: a generator, SMOTE variant or algorithm of the paper's own (including an
"improved" or newly named oversampler whose change the abstract does not describe, and a new or modified
generative model); and a chain made only of classical resampling steps (SMOTE-family oversamplers, undersamplers,
cleaners, clustering) that the paper presents as its contribution and compares with another resampler.

The four facts recorded for each re-read record (`scheme`, `presented`, `compared`, `task`), the flag
`stock_generator`, and the decision under ruling B alone and under B plus B2 are in
`method/second_pass_facts.csv`. Any other variant of the rule can be recomputed from that file.

## 2. Results

**2.1 `1_unsure` (1,222 rows)**

| Decision | Version 1 | Version 2 | Version 3 | Codes in version 3 |
|---|---|---|---|---|
| include | 821 | 660 | 609 | I1-hybrid 253, I1-new-variant 189, I1-other 80, I1-generative 76, I1-multiclass 11 |
| exclude | 351 | 511 | 562 | E1 284, E-OTHER 228 (149 withdrawn Zenodo), E-NOGEN 33, E-COMPARE 9, E2 6, E-LANG 2 |
| unsure | 50 | 51 | 51 | |

- Against the first check, 212 rows changed: 136 chains of existing parts presented but not compared; 24 single
  existing methods; 50 stock generators that were compared (ruling B2); R22396 (`E2`, the downstream model is an
  anomaly detector); R03096 (to unsure).
- Confidence outside the Zenodo series: include 55 high, 173 medium, 381 low; exclude 28 high, 163 medium, 222 low.
  128 includes are `scheme=unclear`: the abstract cannot say whether the method is the paper's own, and only the
  full text can settle them.

**2.2 The two samples (600 rows)**

The blind figures of version 1 stand and are the ones to quote for the screen as it was run: 579 of 596 agree
(97.1%, Cohen's kappa 0.943), 4 undecided.

Under the rulings, 11 sampled decisions change, all in `2_includes` (589 of 600 keep the AI decision, 98.2%):

| rec | AI code | Version 3 | Why |
|---|---|---|---|
| R21465 | I1-new-variant | exclude E-OTHER | Withdrawn Zenodo record (A) |
| R02455 | I1-generative | exclude E1 | CycleGAN, no stated change; only against no augmentation (B) |
| R15961 | I1-new-variant | exclude E1 | K-means partitioning then standard SMOTE; before and after only (B) |
| R18475 | I1-generative | exclude E1 | GPT-2 generation plus SMOTE; no sampler comparison (B) |
| R05963 | I1-hybrid | exclude E1 | SMOTE then an autoencoder cleaner; compared with classifiers only (B) |
| R19288 | I1-generative | exclude E1 | Diffusion model with standard fine-tuning; against real data only (B) |
| R02854 | I1-generative | exclude E1 | Augmentation search plus standard PGGAN; against the baseline only (B) |
| R18047 | I1-hybrid | exclude E1 | Existing GraphSMOTE inside a graph-construction framework, low confidence (B) |
| R01881 | I1-generative | exclude E1 | Plain VAE as the oversampler, compared with ROS and SMOTE (B2) |
| R01598 | I1-generative | exclude E1 | K-means plus standard WGAN-GP, compared with other samplers (B2) |
| R08682 | I1-generative | exclude E1 | Plain GAN over BERT embeddings, compared with traditional techniques (B2) |

No sampled exclusion changes. Nine differences stay flagged without a correction (`DIFF` in `note`), because the
abstract does not settle them or the second pass was not confident: R01320, R01514, R00270 (language), R02966,
R06444, R15103, R09604 in `2_includes`; R00678 and R05434 in `3_exclusions`.

**2.3 What the rulings would do to the full screen.** In the samples, 10 of 299 includes fail rulings B and B2
(3.3%, 95% interval 1.8% to 6.1%), and 0 of 300 exclusions pass them (upper limit 1.3%). At the v0.6 counts
(2,632 includes, 17,706 exclusions) that is about 90 includes to remove (50 to 160). The roughly 350 exclusions
that version 2 would have added are gone. A zero in 300 does not prove there are none: up to about 1.3% of the
exclusions could still qualify, so the exclusion sample is worth a person's eye for exactly this.

**2.4 Code checks.** Unchanged from version 1: six corrections (R00847, R10600, R01960, R06167 in sheet 5; R00002,
R18850 in sheet 4); 40 use-audit rows checked against the full text and 30 against the abstract only; 11 of 13
coverage rows checked. R00007 and R00277 remain unchecked (the Springer copies cannot be read from this session).

## 3. Where the rule is still soft

- **A stated change to a standard generator.** B2 turns on whether the abstract states a change. "Improved",
  "modified", "physics-constrained" or a new architecture was read as the paper's own (include); a plain model
  with a new name was read as stock. Borderline stock readings a person may reverse: R18859 (range-constrained
  CTGAN), R10081 (SNGAN with quality screening), R08290 (WGAN-GP with a sample filter), R17363 (tabular GANs with
  a kNN filter), R11481 (IDR_CTGAN), R13267 (GAMO with GMM grouping).
- **A new name over existing parts.** Read as an own method unless the abstract shows the parts are standard.
  Excluded on that reading: R07317, R04007, R10507, R09624. Included: R16698, R04831, R00593.
- **Comparators that are not named** ("traditional methods", "baselines") were read case by case: R02528, R17091
  (included); R12738, R01042, R14525 (excluded).
- **Tuning how much to sample.** Ratio search was read as an own way of applying SMOTE (R03063, R17713 included;
  R05434 flagged only); selection among samplers by AutoML was not (R03901).
- **Existing samplers in a learned space** (latent or PCA space) were read as a single existing method: R05675,
  R17646, R03327.
- **High-confidence includes of the first check that ruling B excludes:** R20624, R02472, R10264, R00680, R02070,
  R09711.
- **Abstract only.** A paper that compares resamplers in its tables but not in its abstract is excluded here, and
  a chain named only in a title falls to `E1` (for example R10054). The bias is against inclusion.

## 4. Rows a person should look at first

- The 149 `ZENODO-WITHDRAWN` rows and R21465: confirm ruling A once.
- The 51 unsure rows of `1_unsure`: R20873 R05899 R02526 R11429 R16703 R06096 R13814 R04412 R21939 R01054 R22230
  R00841 R01302 R06778 R16220 R14423 R05572 R13670 R16501 R17637 R10860 R03096 R12690 R16866 R01358 R10721 R12677
  R03611 R06403 R01649 R12178 R00208 R04707 R04690 R12162 R20211 R12938 R01956 R16375 R18767 R00148 R17629 R19031
  R07101 R21291 R17455 R05629 R03760 R05624 R01262 R15073
- The 21 `TASK-SCOPE` includes (ruling C, for the merge): segmentation R05002 R11013 R16396 R08293; regression
  recast as classes R10077 R13710 R10682 R16521 R06528 R16196; survival R01249 R02637; object detection R10277
  R11047; continual R00155 R21544; zero-shot R02137 R04326; ranking R01205; other R08316 R20688.
- The 11 sample corrections and the 9 `DIFF` rows in 2.2.
- What the rules removed from the unsure list: filter `note` on `RULE-B (` (160 rows) and `RULE-B2` (51 rows).
- Still without a rule: 24 theses and book chapters among the includes (`DOCTYPE`), the retracted article R07093,
  and includes in a probably non-English journal (`LANG?` in the samples; R01541, R00552, R18199, R00522, R19670,
  R07076, R15541 and others in `1_unsure`).
- Code sheets: the six corrections, R00847 and R10600 first.

## 5. How version 3 was made and checked

- Version 3 is a recomputation of version 2 from `second_pass_facts.csv`: a record is a stock-generator case when
  the second pass classed its scheme as `existing-parts` and coded the generator as generative (GAN, VAE,
  diffusion, language model) or other (KDE, GMM, copula, augmentation). I read the reasons of the 57 records coded
  that way; two more were added by hand because their generator is GMM sampling (R19601) and text augmentation
  (R14622) although they were coded as hybrids, which makes 59. No sub-session was run for version 3.
- Checks made: all non-yellow columns equal the workbook; the changes from version 2 are exactly 51 unsure rows
  to exclude, 3 sampled includes to exclude, and the 6 sampled exclusions back to no correction.
- Overall the check used 47 sub-sessions and about 7.7 million tokens (versions 1 and 2). Title and abstract only,
  apart from the Zenodo status lookup and the open copies for the code checks in version 1.
- I read 14 second-pass records against their abstracts in version 2; the other second-pass decisions were
  checked only for consistency between facts and decision.

## 6. Files returned (version 3)

| File | Content |
|---|---|
| `lists/SMOTE25_check_<list>_AI-Claude-Fable-5.2_2026-11-11_v3.csv` (5 files) | The five lists, same rows and columns as the workbook, only the yellow columns filled. Team use only (abstracts) |
| `RETURN_screen_decisions_AI-Claude-Fable-5.2_2026-11-11_v3.csv` | 1,366 rows: all 1,222 unsure rows and the 144 sample rows with a correction or a note. No abstracts |
| `RETURN_code_checks_AI-Claude-Fable-5.2_2026-11-11_v3.csv` | 81 rows (11 coverage, 70 use audit). No abstracts |
| `method/second_pass_facts.csv` | Facts, `stock_generator`, the decision under B alone and under B plus B2, confidence and reason for the 1,245 re-read records |
| `method/INSTRUCTIONS_pass2.md` | Ruling B as the sub-sessions received it (B2 was applied afterwards by script) |
| `method/` (other files) | Blind raw decisions, Zenodo status, first-check instructions, batch manifest, fetch log |

`note` prefixes: `ZENODO-WITHDRAWN`, `RULE-B`, `RULE-B2 stock generator`, `SECOND-PASS`, `DIFF`, `TASK-SCOPE`,
`CODE-DIFF`, `LOW-CONF`, `LANG?`, `BASIS`, `TITLE-ONLY`, `EVAL-NOT-STATED`, `THEORY-ONLY`, `PURPOSE:`, `DOCTYPE`,
`ABSTRACT-ONLY`. In lists 2 and 3 an empty `person_decision` means the check agrees with the AI decision.

## 7. Still open

- Ruling C (task scope), to be decided by the team lead at the merge.
- The authors' own check of the samples, and job 1 (217 PDFs, five review papers).
- The three codebooks, which the checker never received; coverage rows R00007 and R00277; the 30 abstract-only
  use-audit rows against full text.
- Adoption of rulings A, B, B2 and D in the codebooks, and their application to the records outside these lists.
