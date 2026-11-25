# SMOTE25 systematic search: title and abstract screening (full screen, codebook v1.1, 11 November 2026)

You screen records of a systematic search for a survey of SMOTE and the methods built on it. Each record has a title,
an abstract (sometimes missing), year, venue, document type, language and keywords. Decide from the title and abstract
only. Do not look anything up online, do not open any file other than those your instructions name, and never open a
file whose name contains PRIVATE, manifest, corpus, ledger, coded or matrix.

## Criteria (protocol, Section 3.2 of the survey)

A record is **included** when all three hold:
- **I1** It proposes a method that generates synthetic minority examples, or changes how SMOTE is applied, for
  classification. This covers new SMOTE variants (new seed selection, sample allocation, neighbor choice, placement,
  filtering), hybrids that change where or how synthetic examples are made (for example SMOTE inside boosting, SMOTE
  with a new cleaning step presented as a method), multiclass schemes for oversampling, and generative oversamplers
  (GAN, VAE, diffusion, language-model or other generators of synthetic minority examples).
- **I2** It evaluates the method on data (real or synthetic datasets, any metric).
- **I3** It is a journal or conference paper, or a preprint, in English.

A record is **excluded** when any of these holds:
- **E1** It applies existing resampling (SMOTE, ADASYN, random oversampling, an existing variant) to a domain problem
  without proposing a method: SMOTE is a preprocessing step in a pipeline for, say, fraud, disease or fault
  detection. Calling the pipeline a "framework" or "model" does not make it a new resampling method; it must change
  the generation of synthetic examples itself or how SMOTE is applied, and present that as its contribution.
- **E2** It addresses regression, clustering or anomaly detection only (no classification).
- **E-NOGEN** The method generates no synthetic examples and does not change how SMOTE is applied: undersampling
  only, cost-sensitive learning only, ensembles without oversampling, feature selection, loss functions.
- **E-REVIEW** A review, survey, tutorial, editorial or book front matter.
- **E-COMPARE** An empirical comparison of existing methods that proposes nothing new (tag it `comparison`, it may
  matter elsewhere in the survey).
- **E-LANG** Not in English.
(E3, no accessible full text, and E4, an earlier version of an included paper, are judged at the full-text stage,
not here.)

Mark **unsure** when the title and abstract do not let you decide between include and exclude, for example a
"novel framework" in a domain paper where you cannot tell whether the resampling itself is new, or a missing abstract
with a title that could go either way. Unsure records go to the full-text stage; do not use unsure to avoid a
decision you can make.

## Clarifications for the full screen (v1.1)

Added after the pilot from the coders' notes. Each sends a doubtful case to the person's check instead of deciding it:

1. A SMOTE extension or other generator of synthetic examples built for a purpose other than imbalanced
   classification (for example privacy-preserving data sharing): **unsure** (U-other); say the purpose in the reason.
2. A method that meets I1 but whose abstract names no evaluation on data: **unsure** (U-other), reason starting
   "I2 not stated in the abstract".
3. An existing generator combined with an existing cleaning or selection step and presented as a new method:
   **unsure** (U-new-or-applied), unless the abstract describes a change to the generation itself (then include,
   I1-hybrid).
4. Proceedings front matter, a book's table of contents or a "conference review" record that lists papers: **exclude**
   (E-REVIEW); if a listed title looks in scope, add the tag `front-matter-in-scope`.

## Output columns

One row per record, in the batch's order:

| Column | Content |
|---|---|
| rec | the record id, copied |
| decision | include, exclude or unsure |
| reason_code | for include: I1-new-variant, I1-hybrid, I1-generative, I1-multiclass, I1-other; for exclude: E1, E2, E-NOGEN, E-REVIEW, E-COMPARE, E-LANG; for unsure: U-new-or-applied, U-no-abstract, U-other |
| reason | one short sentence in your own words |
| quote | at most 25 words copied from the title or abstract that support the decision (empty if no abstract) |
| tags | any of: generative, comparison, multiclass, deep-learning, image, text, time-series, medical, no-abstract, front-matter-in-scope (separated by ;) |
| confidence | high, medium or low |
