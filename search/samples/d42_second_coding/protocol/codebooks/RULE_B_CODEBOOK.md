# SMOTE25 screen: rulings B, B2 and C on the included records (codebook addendum v1, 12 November 2026)

The team lead's rulings of 11 November 2026, confirmed for the whole screen on 12 November, narrow criterion I1 of the
screening codebook. Every record you see was included by the screen. You do not decide include or exclude: you record
six facts about each record from its title and abstract, and a script applies the rulings to them. Decide from the
title and abstract only. Do not look anything up online.

## The rulings

- **B.** A chain of existing resampling methods counts as the paper's own method only if the paper presents it as its
  contribution **and** compares it with at least one other way of resampling.
- **B2.** A standard generator used without a stated change (plain GAN, conditional GAN, WGAN-GP, CTGAN, VAE,
  diffusion model, language model, KDE or GMM sampling, copula, standard data augmentation) never counts as the paper's
  own, also when it is chained with other steps and compared.
- **C.** The task does not decide scope: segmentation, regression recast as classes, survival analysis, object
  detection, continual learning, zero-shot learning and ranking are in scope like classification. Record the task.

What still counts as the paper's own: a generator, SMOTE variant or algorithm of the paper's own, including an
"improved" or newly named oversampler whose change the abstract does not describe; a new or modified generative model;
a multiclass oversampling scheme of its own; and a new way of applying SMOTE (for example a search for how much to
oversample, or a new allocation of synthetic examples).

## The facts (one row per record)

| Field | Values and meaning |
|---|---|
| scheme | `own`: the abstract presents a resampling method of the paper's own: a new or changed SMOTE variant or oversampler (also when it is only named or called improved, without the change described), a new or modified generative model (a stated change to architecture, loss, training, conditioning or sampling, such as "improved", "modified", "constrained" or a new architecture), a multiclass oversampling scheme of its own, or a new way of applying SMOTE. `existing-parts`: the method is put together from existing parts without a stated change: a chain of existing resampling steps (SMOTE-family oversamplers, undersamplers, cleaners, clustering), a standard generator used as is (the list of B2), an existing sampler applied in a learned space (latent space, PCA), or a choice among existing samplers (for example by AutoML). A new name over parts that the abstract shows to be standard is `existing-parts`. `unclear`: the abstract does not let you tell (for example "a novel oversampling framework" with no detail and no named parts, or no abstract and a title that could go either way). |
| generator | The kind of step that makes the synthetic examples. `classical`: SMOTE or a SMOTE-family method, random oversampling or another interpolation, also when combined with undersampling, cleaning or clustering. `deep-generative`: GAN, VAE, diffusion model, language model, normalizing flow or another neural generator. `statistical`: KDE, GMM sampling, copula or another fitted distribution. `augmentation`: standard data augmentation (image transforms, text augmentation, mixup). `none`: no synthetic examples (the method changes how SMOTE is applied without generating) or the abstract names no generator. If a chain holds both a classical step and a standard generator of the B2 list, code the generator's kind. |
| presented | `yes` when the abstract presents the resampling method (or the chain) as the paper's contribution; `no` when resampling is a step of a pipeline whose contribution lies elsewhere (a domain model, a classifier, a feature method, an application). |
| compared | `yes` when the abstract says that the method is compared with at least one other way of resampling: another oversampler or undersampler, SMOTE, random oversampling, another generator or augmentation method, or unnamed methods that the abstract calls resampling, oversampling, augmentation or balancing methods ("traditional oversampling techniques", "other data balancing methods"). `no` when the comparison is only with classifiers, with no resampling or no augmentation, with real data only, before against after, with unnamed "baselines", "state-of-the-art methods" or "existing methods" that the abstract does not say are resampling methods, or when the abstract names no comparison. Judge only what the abstract says. |
| task | `classification`, `segmentation`, `regression-as-classes`, `survival`, `detection`, `continual`, `zero-shot`, `ranking` or `other`. |
| confidence | `high`, `medium` or `low`, for the facts as a whole. |
| reason | One short sentence in your own words: what the method is and why you coded the scheme as you did. |

## How the script applies the rulings (for your information)

`own` or `unclear`: the record stays included. `existing-parts`: excluded under E1 when the generator is
`deep-generative`, `statistical` or `augmentation` (B2); otherwise it stays included only when presented is `yes` and
compared is `yes` (B), and is excluded under E1 when not.

## Cases the independent check met (be consistent with them)

- An "improved" or newly named oversampler whose change the abstract does not describe: `own`.
- A plain standard model under a new name (for example a renamed CTGAN): `existing-parts`, `deep-generative`.
- Range-constrained or physics-constrained generation, a new loss, a new architecture, a new conditioning: `own`.
- A standard generator followed by a separate filter or quality screening of its output: `existing-parts` (the
  generator itself is unchanged).
- K-means partitioning then standard SMOTE; SMOTE then an existing cleaner (Tomek links, ENN, an autoencoder used as a
  cleaner); SMOTE inside an existing ensemble: `existing-parts`, `classical`.
- A search for how much to oversample, or a new allocation of synthetic examples per region: `own`.
- Choosing among existing samplers by AutoML or by validation: `existing-parts`.
- An existing sampler applied in a latent or PCA space: `existing-parts`.
- A method named only in the title, with no abstract: `unclear` when the title suggests a new method,
  `existing-parts` when it names only standard parts.
