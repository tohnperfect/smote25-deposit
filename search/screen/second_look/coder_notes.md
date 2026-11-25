# Notes of the second-look sessions, by batch

## batch001

batch 001: 200 of 200 records done; include 35, unsure 82, exclude 83
no records remain

Look at these first:
1. Low-confidence excludes (they will not reach full text otherwise): R01854 (plain GAN on FFT spectra for bearing faults, compared with ROS/SMOTE/PCO), R20368 (SMOTE then cWGAN chain), R12493 (SMOTE tuned by a hummingbird optimizer), R18180 (SMOTE in autoencoder latent space), R15006, R11620, R01632, R13353, R13225, R02629.
2. Low-confidence includes: R19244 (new adversarial generation module inside a federated-RL fraud model), R02648 (clustering-SMOTE embedded in a random forest, domain paper).
3. Cases the codebook does not settle (marked unsure unless stated):
   - Book chapters with a new oversampler; I3 lists only journal, conference and preprint: R01341 (AEMNOST), R00741 (OUPS), R04756 (modified WGAN-GP).
   - Theory of SMOTE, no method and no exclusion code fits: R07987, R22032 (probably related papers on SMOTE convergence).
   - Multiclass scheme that duplicates rather than synthesizes: R00075. Minority enlarged with pseudo-labelled real data, excluded E-NOGEN: R05435.
   - Full text may not be in English: R03618 (Indonesian title, improves MWMOTE), R01842 (IDP-SMOTE, Chinese journal, no abstract).
   - Purpose other than imbalanced classification (clarification 1): R08817 (fairness, FAWOS), R15569, R20708, R08218, R19882, R07661, R17454, R09534; R22396 (anomaly detection) and R11523 (survival analysis) may be E2.
4. Clarification 2 (I2 not stated): seven 2026 Zenodo SMOTE-variant preprints share one template with only "theoretical analysis" (R18543, R21486, R21495, R20496, R19265, R16060, R17103), possibly from one source; R18543 and R21495 both use the name DD-SMOTE. Also R13900, R03926, R12764, R11581.
5. Consistency checks:
   - R10025 (SIRSYN, 60 KEEL datasets, 13 baselines) and R07622 (RO-SMOTE) are unsure only through clarification 3; SIRSYN is a strong include candidate.
   - R15320 (unsure) uses MOSD, which R12658 (E1) also treats as an existing technique, so R15320 is probably E1.
   - R20205 (local-LLM augmentation, unsure) follows the same pattern as R19389, R21984 and R16092 (off-the-shelf GAN, CTGAN or TVAE, all E1); align them at the check.
   - SMOTE+ENN or NearMiss+SMOTE claimed as novel went to unsure (R08259, R10660, R03543, R10696, R13498); unclaimed uses were E1 (R05289, R19188).
   - R06099 (SMOTified-GAN, include) and R08817 (FAWOS) reuse names of published methods; check whether they are applications or republications.

## batch002

batch 002: 200 of 200 records done; include 47, unsure 78, exclude 75
no records remain

Look at first:
1. Low-confidence include/exclude: R12193 (include; "modified SMOTE-ENC" not described), R08605 (include; Kalman-filter SMOTE inside a multi-topic preprint, vague evaluation), R13217 (exclude; no abstract, fraud title), R19409 (exclude E-COMPARE; no abstract, GAN vs diffusion for knee radiographs).
2. Language: R21881 excluded E-LANG only because the record language is zh. The abstract is in English and the method, a generative oversampler, is in scope. R13569 (included) and R16562 (unsure) have bilingual Chinese/English titles but English metadata. Check the full-text language of all three.
3. Excluded but relevant elsewhere (E-COMPARE): R01566 (theoretical analysis of SMOTE density), R03756 (conditional GAN/VAE as oversamplers), R08489 (noise filters before oversamplers), R18988 (ASTRA-SMOTE / SMOTE-RADIANT; check these are not the authors' own new variants).
4. Codebook does not settle whether non-synthetic oversampling meets I1: duplication or random-oversampling variants (R09642, R01162, R03731, R00184, R00813, R08602, R00222); relabelling or pseudo-labelling as minority (R01872, R09879, R00416). All are marked unsure U-other.
5. Scope edges marked unsure U-other: segmentation or detection rather than classification (R17972, R08293); supervised anomaly detection with federated P2P SMOTE (R03745); mixed-purpose generators (R13265 FL/privacy, R02637 imputation/survival); a SMOTE-variant selection tool (R00440); semi-supervised GAN (R03178); deep over-sampling extension (R01514); raking resampling for one-class (R07066). Borderline includes as I1-other: R11644 (loss-level bias correction for SMOTE data), R15089 (kNN-guided mixup), and the big-data SMOTE implementations R01125 (GPU) and R05756 (MapReduce). By contrast, R01990 (Spark SMOTE inside a domain study) is unsure.
6. "I2 not stated in the abstract" (clarification 2): R21491, R05356, R17096, R21983, R18686, R20525, R17987, R21601, R04172. Seven are 2026 Zenodo SMOTE-variant preprints supported only by "theoretical analysis", which looks like a series. R04172's "novel" method reads like ADASYN.
7. Clarification 3 (existing generator plus existing cleaning step, or combinations of existing generators): R00540 (the known SMOTE-IPF), R14388, R13396, R00363, R13516, R10932, R03706, R06797, R09632, R15421, R11499, R22301, R20624, R04161, R20684. The person should decide whether well-known ones such as SMOTE-IPF go straight to include.
8. Generative methods in domain papers need a consistency check. Include where the abstract presents the generator as the contribution or describes a change to it (e.g. R12267, R03535, R07631, R04404, R07218). E1 where an off-the-shelf GAN, CTGAN, WGAN or LLM is one pipeline step (e.g. R06413, R12626, R13660, R19889, R15520). Unsure where unclear (R19439, R20194, R08539, R06671).
9. No abstract, but the title names a new oversampler (unsure U-no-abstract): R20568 (MoRO), R09280 (LD_CSMOTE). R12043 and R18153 have near-identical intrusion detection plus data-balancing abstracts, so they may be duplicates.

## batch003

batch 003: 200 of 200 records done; include 56, unsure 57, exclude 87
no records remain

Look at these first:
- Low confidence: R11155 ("dual-phase SMOTE") and R13177 ("composite minority oversampling"), both unsure; either could just as well be E1.
- Coded E1 because each paper names an undescribed variant but does not present it as a contribution: R18599 (SMOTE-DBC), R17156 (KMADASYN), R14247 (SSMOTE). By contrast, "Improved/tailored SMOTE" papers went to unsure: R09561, R16987, R10553, R09937.
- Existing generators used as oversamplers. Included where the paper frames the generator as its resampling contribution: R01810, R02086, R10196. Excluded as E1 where it is a pipeline step: R19934, R19543, R05919, R19336, R18464, R01905.
- The codebook does not settle oversamplers that create no synthetic examples. Excluded as E-NOGEN: R00601 (cloning), R18041 (ROS-based), R05509 (relabelling), R04606 (reuse of past minority samples). R01624 kept as unsure. R01564 (IOSDS) and R02117 (SOUP) included, although their abstracts do not say the new examples are synthetic.
- Domain-specific augmentation counted as I1-other: R17436, R18131, R09451, R12265, R01196. Augmentation for detection or segmentation sent to unsure: R05002, R02563, R04499.
- Metaheuristic- or joint-tuned SMOTE in domain papers sent to unsure (does tuning count as changing how SMOTE is applied?): R21583, R06759, R08478, R19307.
- Zenodo 2026 series of SMOTE variants with no evaluation (clarification 2, unsure): R17116, R21499, R19247, R20611, R22155, R21602, R21496. R21517 from the same series was included because it names metrics, though no datasets.
- Language: R20894 unsure (Indonesian title, but the language field says en). R02632 is E-LANG (zh), but its content looks in scope.
- Other: R08963 is indexed as a "Short survey" but reports original work (included). R01535 (SMOTE theory, E-COMPARE) and R15932 (package paper, E-REVIEW, no closer code) may matter elsewhere in the survey. R17982 is unsure only because of clarification 1 (likely exclude). R12382 was included despite its anomaly-detection framing.

## batch004

batch 004: 200 of 200 records done; include 31, unsure 68, exclude 101

Records to look at first:
- Low-confidence EXCLUDES that could be in scope: R03399 (domain adaptation for a rare class augmented with simulated samples; E-NOGEN), R03487 ("integrated" Borderline-SMOTE in AdaBoost, possibly inside the boosting rounds), R02398 / R06773 / R17619 (domain-specific augmentation or "deterministic" oversampling, read as E1), and no-abstract domain titles R21006, R18972, R01394, R13536, R05898.
- Low-confidence INCLUDE: R15298 (grid search over RUS and SMOTE ratios). It belongs with the other parameter- and ratio-tuning includes R00851, R03116 and R15808, but R03901 (AutoML over sampler, ratio, loss and calibration) and R09560 ("optimized SMOTE", not described) are unsure. These need one rule on whether tuning SMOTE parameters or ratios counts as changing how SMOTE is applied.
- Cases the codebook does not settle: retracted paper R05192; language conflicts R18199 (field says Turkish, abstract in English), R00283 (field says French, abstract in English), R02805 (field says en, abstract in Korean) and R09844 (Chinese, excluded E-LANG although its POS oversampler is in scope); document type with no exclusion code: R18677 (book chapter), R21995 (thesis), R22053 (poster evaluated only on visualization).
- Regression generators excluded under E2 rather than sent to unsure under clarification 1: R17099, R04981, R04099, R10295 (WSMOTER), R04138. R00775 (CWOS-Ord, ordinal "regression") is included because it is classification of ordered classes.
- Domain papers that name an "improved" or "modified" oversampler without describing it were split: R22117 (improved MWMOTE) is included; R07855, R13665, R05753, R21566, R16704 and R09560 are unsure. These should be decided the same way.
- Generative calls: domain papers whose generator is modified were included (R19236, R19290, R20089, R03299, R06220, R07808); existing GANs that are only applied were excluded E1. The closest of those to the line is R12766 ("proposes" a CWGAN-GP-based augmentation).
- Latent-space SMOTE: R17646 and R07321 are unsure, while R04536 (embedding-space oversampling inside a general method) is included.
- R00098 (selective pre-processing with local over-sampling) is unsure because the over-sampling may be replication. Similar new hybrids that also do not name their oversampler were included (R01182, R00941, R05372).
- I2 not stated (U-other): 11 near-identical 2026 Zenodo SMOTE-variant preprints that make only theoretical claims (R21391, R17576, R18954, R18111, R21923, R21500, R17444, R16659, R19256, R19444, R17104), plus R00703.

## batch005

batch 005: 200 of 200 records done; include 43, unsure 80, exclude 77
no records remain

Look at these first:
1. Exclusions most likely to be wrong: R13563 (E-LANG; abstract is in Korean but metadata says English; VAE-GAN with semi-hard example mining would otherwise be an include). Also R06339 (E-COMPARE; include if the OSSA seed-spread generator is new in this paper). No-abstract titles excluded at medium confidence: R19194, R19552, R06065, R05866, R04462, R12318, R07180, R17177, R01439, R16705, R18160.
2. Low-confidence includes: R01336, R04042, R13151, R05189, R09761, R05177.
3. Where I drew the line under clarification 3, please confirm. Removing minority seeds before generation counted as a change to generation (include: R04190 iF-ADASYN, R19848 SMOTERN). Cleaning after generation or cleaning the majority class went to unsure: R05200 RN-SMOTE, R02267 SGM, R06556 SMOTE-RBU, R02530, R01927, R12738, R02545. R00789 (ADASYN with MCA pruning) and R20462 (MAGA, which its authors call procedural) are included because the filtering they use is new.
4. Existing generators combined with no stated mechanism went to unsure: R16269, R10913, R19634, R09315, R06363, R11583. The exception is R19935 (SHDO, five oversamplers applied in sequence), which I included. Please check it alongside that group.
5. Cases the codebook does not settle:
   - R07093 is a retracted record.
   - Full text may not be in English although metadata says English: R00552, R00242, R00327, R00084, R20697.
   - Four Zenodo 2026 SMOTE variants mention only theoretical analysis (unsure, "I2 not stated"), probably from the same source: R17671, R16916, R17780, R18945.
   - Unclear whether the oversampling synthesizes examples or duplicates them: R01652, R00005, R08001, R00323, R03023, R14664, R07821.
   - Built for something other than imbalanced classification (unsure under clarification 1): R04876 (imputation), R01249 (survival), R03519 (privacy), R07337 (zero-shot), R13287 (detection/segmentation), R06755 (missing data).
   - R14227 is framed as anomaly detection but evaluated as multiclass classification, so it is included.

## batch006

batch 006: 200 of 200 records done; include 46, unsure 62, exclude 92
no records remain

Look at these first:
- Cases the codebook does not settle (all marked unsure, U-other). Retracted papers that propose an oversampler: R09920, R05190. Book chapters with an in-scope SMOTE variant: R00351, R01895. A Turkish title with "en" metadata: R05311. Related: R01957 is excluded as E-LANG (metadata says Turkish), but its content (SMOTE plus boosting for noise) is in scope. R18048 has "English" metadata but comes from a Chinese journal.
- Six similar 2026 Zenodo preprints proposing SMOTE variants with no evaluation in the abstract (unsure, "I2 not stated", clarification 2): R21520, R17241, R21497, R21522, R17111, R21638. They may share one source. The same rule was applied to R09418, R16549 and R10198.
- Generators built for another purpose (clarification 1, unsure). Fairness: R03488 (FAWOS), R10198 (FOS), R15697 (FedIDA). Privacy: R09835. Generation quality only: R19302, R14037.
- Probable duplicate pair, both included: R20197 (repository copy) and R19226 (journal version) of the same LLM text-augmentation paper.
- Low-confidence includes: R19845, R01951, R08329, R13558, R06672.
- Borderline excludes. Existing generator applied as an oversampler (E1): R18048 (DDPM), R04495 (CTTGAN). The previously proposed NCLWO applied to software defect data: R14420. The authors' earlier SSOMaj-SMOTE-SSOMin reused with a new transform: R01907. Grid-search-tuned SMOTE: R20177 (compare R15478, which is unsure). Generative-oversampler benchmark that mentions "our own" models: R02633. Batista et al. study of SMOTE+Tomek and SMOTE+ENN: R00010. SMOTE extended to regression (E2): R01064.
- Unsure records that may be includes under the I1 example "SMOTE with a new cleaning step": R05564 (improved SCUT, multiclass), R07085 (LOF with Borderline-SMOTE), R15465 (SMOTE-PCADBSCAN).

## batch007

batch 007: 200 of 200 records done; include 33, unsure 61, exclude 106
no records remain

Look at first:
- Low-confidence excludes: R02132 (WGAN-based minority oversampling for lung CT, coded E1), R06770 (stratified k-means sampling, E-NOGEN).
- Low-confidence includes: R16443 (EVOS, generator only vaguely described), R00136 (statistically directed oversampling), R22069 (Jacobian data augmentation replacing SMOTE in fraud, partly adversarial purpose).
- Likely includes held as unsure only by the rules: R06130 DeepSMOTE (abstract names no evaluation, clarification 2) and R00702 SMOTE-IPF (existing IPF filter after SMOTE, clarification 3). R00344 SMOTE-RSB* was included on the assumption that its rough-set editing is new; under a strict reading of clarification 3 it would be unsure.
- Theory-only Zenodo preprints with new SMOTE variants, unsure per clarification 2: R21005, R19293, R20597, R21516, R15955, R18484, R21519, R18537.
- Domain frameworks naming an undescribed SMOTE variant were sent to unsure (low): R17120, R16781, R19670, R17213, R16248, R17193. R13815 (energy forecasting with a "modified SMOTE") was coded E1 medium before this pattern was settled; please recheck it for consistency.
- GAN papers built for one domain (codebook does not settle): include when a new generator design is described (R02399, R06821, R10912, R18864, R01824); unsure when a named GAN framework claims unspecified improvements (R05652, R18879, R08682, R11000); E1 when an existing GAN is applied (R02132, R16664 and others).
- Replication-only oversampling coded E-NOGEN because no synthetic examples are made (codebook silent on ROS-type methods): R03406, R10031, R05355, R03600, R04820. R06588 (US-PONR, included) may also be replication-based.
- Metadata says English but the venue usually publishes in Chinese or Korean (E-LANG risk at full text): R00294, R00270, R10048 (included), R00483, R00032 (unsure).
- Other: R18367 is a book chapter (I3 doubtful); R01352 (R package of oversamplers) coded E-REVIEW but may matter for a software discussion; R04326 (zero-shot feature generator) and R17457 (pseudo-normal generator) unsure per clarification 1; R02386 (conformational oversampling, include) and R00733 (SDSA sample selection, exclude) are borderline.

## batch008

batch 008: 200 of 200 records done; include 61, unsure 68, exclude 71

Look at these first:
1. Excludes with low confidence (nothing else sends them on): R01413 (flight delays; the method is unclear, keywords suggest plain SMOTE), R17593 (multi-discriminator GAN zero-day detector; excluded as E2), R14586 (language field is ar but the title and abstract are English; the modified SMOTE is not described).
2. Borderline excludes: R07696 (SMOTE data used only for CNN pretraining), R01496 (stream method that reuses past real minority examples; R05664 is the same kind but marked unsure), R14566 (fairness-driven random oversampling, no synthesis), R19428 (diagnostic of SMOTE under distribution shift; may matter for the discussion), R20046, R09728, R00947, R15695 (existing GANs used in domain pipelines).
3. Not settled by the codebook: an existing generator used unchanged but presented as the paper's own oversampler. Unsure: R05055, R02008, R03740, R13519. Included: R02615 (SeqGAN), R03162 (GPT-2). One rule should cover the whole group.
4. Not settled by the codebook: a new ensemble or classifier wrapped around unchanged SMOTE. Is it an I1 hybrid? R01755, R21324, R00393, R00871, R13446 (all unsure).
5. Not settled by the codebook: I3 for book chapters. R18315, R03321, R04707 (unsure). Also R00240 (included; the venue may publish its full texts in Chinese).
6. Scope: generators for segmentation or detection (R18850, R12102); patch- or cell-level oversampling that may not be synthetic (R03524, R01588); tasks that may be regression (R22303 unsure, R14521 included).
7. Includes with low confidence: R15222, R17697, R06676, R07327, R14521, R05974.

## batch009

batch 009: 200 of 200 records done; include 48, unsure 75, exclude 77
no records remain

Look at these first:
- Low-confidence includes and excludes: R07684 (E1; claims a "novel" oversampling approach for stroke but describes none), R15491 (E-NOGEN; STAS might create data, keywords say undersampling), R00179 (include; SMOTE plus class-weighted Bagging, venue may be a Chinese-language journal), R00388 (include; SVM ensembles with k-means and resampling, SMOTE only in keywords).
- Language: R15921 is coded E-LANG because its title is Ukrainian, although the metadata says en (content: SMOTENC vs a signature-preserving adaptive balancer). R10651 is included, but its journal (JEIT) may publish in Chinese. R04783 has Indonesian language metadata.
- The codebook does not settle metaheuristic tuning of an oversampler's parameters. R09448 and R20587 are E1 (tuning inside a domain pipeline), R13953 and R09878 are unsure, and R06476 is included (balancing is its main contribution). Please make these consistent.
- The codebook does not settle a standard GAN/VAE/CTGAN/SeqGAN presented as a "novel" oversampler in a domain paper. I sent these to unsure: R20524, R19272, R02705, R11481, R16437, R07361, R01973, R15590, R06526, R19405, R21009. I used E1 where the generator was only a pipeline step.
- Clarification 2 cluster: seven 2026 Zenodo SMOTE variants report theoretical analysis only (R18476, R19241, R17123, R22242, R18101, R20941, R17974); also R21574 and R00155. All are coded U-other.
- Clarification 1 (purpose is not class balancing), all U-other: R10952 balances gender, R02807 and R05710 impute missing values, R08482 estimates treatment effects, R05531 localises faults, R20218 does object detection.
- Other gaps: book chapters R01396 (unsure) and R00161 (E-REVIEW). The software paper R01046 (imbalanced-learn) is coded E-REVIEW for lack of a better code. R00094 is included but is a TRECVID notebook paper. R10794 and R02192 are included but framed as anomaly detection, so check E2.
- Excluded but possibly useful elsewhere in the survey: R21941 and R22263 (E-COMPARE; critical audits of synthetic minority data), R03781 (DEBOHID parameter study), R00607 (E-NOGEN; multilabel random over- and undersampling), R12100 (E-NOGEN; oversampling with real data from related datasets).

## batch010

batch 010: 200 of 200 records done; include 38, unsure 67, exclude 95
no records remain

Look at these first:
- Low confidence: R00083, R01695, R05729, R22322, R05184 (unsure); R01913 (excluded E-NOGEN; GAN segmentation, oversampling unclear); R17638 (excluded E-COMPARE; its jittering with classifier-guided acceptance may be a new generator).
- R19744 (include): the abstract almost matches GraphSMOTE (WSDM 2021) word for word, with the method renamed GraphBalance. Check originality.
- Ten 2026 Zenodo SMOTE-variant preprints are unsure only because their abstracts cite theory and no data (clarification 2): R20222, R15954, R17105, R16552, R21624, R19671, R19516, R21606, R21439, R20861. They share one abstract template, so they may come from one source. R00042 (FLAIRS 2007) is unsure for the same reason.
- The codebook does not settle these: R00839 is a dissertation (I3) proposing MeMO, coded unsure. R07621 is a theory paper on the distribution of SMOTE samples; it is excluded as E-NOGEN for lack of a code but is likely useful as background. R00280 and R00340 are included, but their venues may publish in Chinese; check the language.
- Borderline includes: R13167 FG-SMOTE (fairness purpose, clarification 1?); R21968 (diffusion defects framed as anomaly detection, E2?); R21964 and R08479 (mixup/cutmix-style minority image synthesis); R00714 (plain SMOTE in a sentence-embedding space); R02081 (staged SMOTE in a case study).
- Rule I applied for generators: when a standard VAE or GAN is paired with a classifier in a domain pipeline, I excluded it as E1 (e.g. R21576, R07534, R16757). When generative oversampling is the paper's main contribution but the abstract does not say the generator was changed, I coded it unsure (R06345, R11070). Cluster-restricted SMOTE was split on whether a new mechanism is claimed: R16142 unsure, R20535 include.

## batch011

batch 011: 200 of 200 records done; include 25, unsure 71, exclude 104
no records remain

Look at first (low-confidence excludes are final, so these come first):
1. Low-confidence excludes: R02100 (GANs to balance comfort data, E1), R20732 (stream ensemble with inverse random under/oversampling, E-NOGEN), R09148 (online bagging with neighbourhood oversampling, E-NOGEN).
2. Consistency check: R05382 (Unrolled-GAN oversampling for fraud) was coded unsure. Later records with an existing GAN/WGAN/VAE used as an oversampler on a domain dataset were coded E1: R09894, R02848, R03770, R06880, R02100. Please apply one rule to all of them.
3. Low-confidence includes: R00747 (cost-driven oversampling + denoising AE; synthetic?), R03606 (SAC per-class generation; generator unnamed), R00804 (EMOTE applied to churn; EMOTE itself is R00930), R16677 (CN-SMOTE inside a skin-lesion framework), R17713 (metaheuristic-set SMOTE rates).
4. Cases the codebook does not settle:
   - Metaheuristic tuning of SMOTE rate/k as "changing how SMOTE is applied": included R05335, R04679, R17713; unsure R05050, R09971, R15541 (no abstract).
   - New ensembles whose oversampling may only replicate examples: unsure R01028, R03455, R00927, R05406; E-NOGEN R20732, R09148, R02539.
   - "Oversampling" that adds real instances (retrieval, unlabeled pool, instance transfer), coded E-NOGEN: R16561, R01797, R01260.
   - Generators for segmentation or other purposes (clarification 1, unsure): R15157, R19720, R20472 (dataset distillation), R04984 (fairness), R13147 (privacy), R21919 (privacy), R22325 (majority-class oversampling).
   - Language: R00173 and R00339 are from Chinese-language journals but the metadata says en. Included on substance; check the full-text language (E-LANG).
   - Book chapters (I3 fails, no dedicated code): R13753, R21672, R19836 coded E1; R19261 coded E-REVIEW.
   - SMOTE with a filter before generation, judged as a change to the seed pool: R19907 SMOTE-IH and R07267 included (clarification 3 could instead give unsure).
5. Clarification 2 (I2 not stated), mostly 2026 Zenodo theory-only SMOTE variants, all unsure: R21518, R17094, R20121, R21505, R21451, R21979, R20135, R20584, R18087, R09036.

## batch012

batch 012: 200 of 200 records done; include 28, unsure 66, exclude 106

Look at first:
- Possible inconsistencies in my own rows (appended before I noticed; not edited): R16230 (Enhanced SMOTE in an IoT IDS framework) was excluded E1, but the similar cases R11646, R03065 and R19554 (Improved/I-/boundary-midpoint SMOTE named in domain frameworks) went to unsure U-new-or-applied, so R16230 probably belongs there too. R03960 (real-time oversampling inside spline adaptive filters for system identification) was excluded E2 (high), but under clarification 1 it may belong with the unsure U-other "generator built for another purpose" group below.
- Low-confidence includes: R03118 (SMOTE with Gaussian density, Alzheimer's), R01053 (K-means plus improved SMOTE, IPTV), R04128 (oversampling via multiple imputation), R06454 (mixup minority augmentation, a minor part of a zero-shot vision model), R00073 (SMOTEBoostSVM, a small step from SMOTEBoost).
- Borderline includes: R19015 (few-shot LLM generation for HAR, framed as an evaluation), R04759 (GAN oversamplers for software faults; the GANs may be existing ones), R21839 and R02906 (new oversampling or augmentation components inside larger models), and R08572, R14643 and R05691 (fusing several oversamplers' outputs). I included these three as new ways of applying SMOTE rather than as clarification-3 unsure cases.
- Not settled by the codebook:
  (a) Theory papers, sent to unsure U-other: R12009 (SMOTE risk bounds, NeurIPS) and R09916 (under/oversampling theory, PMLR).
  (b) Non-synthetic oversampling by replication or reweighting, excluded E-NOGEN: R00621 (ML-BFO, multilabel), R00677 and R19859 (neighbourhood bagging).
  (c) Not a journal paper, conference paper or preprint (I3 has no exclusion code), sent to unsure U-other: theses R00110 and R00737; book chapters R08563 (improved ADASYN) and R02682 (FN-SMOTE).
  (d) Language metadata: R10870 (zh; SMOTE on Deep Forest output probabilities) and R18985 (tr; LSHADE-tuned WGAN-GP text generator) were excluded E-LANG, but both have English abstracts and in-scope content. R00073, R11531 and R10846 are recorded as English but appear in Chinese- or Korean-language venues.
  (e) Retracted: R05589, excluded E1.
- Generators built for purposes other than imbalanced classification (clarification 1, unsure U-other): R21920 (privacy), R21744 (clustering), R16490 (traffic forecasting), R04188 (count regression), R16630 (segmentation), R01205 (learning to rank), R21965 (supervised anomaly detection).
- Six Zenodo preprints of SMOTE variants with no evaluation stated (clarification 2, unsure U-other): R17238, R17239, R20694, R18949, R18112, R21798. They look like one series.
- Low-confidence unsure and exclude: R00233, R12994, R01369, R13710, R11199, R06297, R22108, R09614, R06096, R11151, R00567, R09773 (excluded E-REVIEW, no abstract), R20019 (excluded E2, no abstract).
- Possibly useful elsewhere in the survey: R19450 (leakage-free benchmark showing that resampling before splitting inflates F1) and R15649 (ADASYN breaks down under extreme imbalance).

## batch013

batch 013: 200 of 200 records done; include 41, unsure 76, exclude 83
no records remain

Look at these first:
- Cases the codebook does not settle: R00234 (dissertation, I3 has no exclusion code; unsure), R04831 (CRC book chapter proposing VDB-SLSMOTE; unsure), R03573 (garbled, machine-paraphrased abstract of a kernel SMOTE method, possibly a spun copy of an earlier paper; include, low), R22258 (theory-only paper on when synthetic augmentation helps; coded E-COMPARE for lack of a better code), R08901 (GOLIATH, a KDE generalization of SMOTE evaluated on regression only; E2, may matter for the theory section), R13097 (coded E-LANG although language field says en: Chinese abstract first).
- Replication-based or unclear oversamplers (codebook only covers synthetic generation): R06451 HSBoot (E-NOGEN), R00986, R03440, R00120, R12101 (unsure, low).
- Low-confidence includes: R13524 (HyperSMOTE-MC), R01372 (hierarchical SMOTE), R21622 (SB-CPO), R13331 (GraphIAM), R03573.
- Low-confidence excludes: R00801 (employability, undescribed "newly proposed hybrid"), R18694 (range-controlled oversampling in a lending model).
- Borderline includes: R21422 and R00447 (choosing the oversampling ratio or class distribution, coded I1-other); R01642 and R16452 (framed as anomaly detection but trained as supervised imbalanced classification, check E2).
- Clarification 2 (I2 not stated), a run of similar 2026 Zenodo SMOTE-variant preprints: R17113, R21358, R17107, R21320, R20083, R17211, R21666.
- No abstract, title looks in scope: R10636, R16558, R11753, R00148.
- Clarification 1 (generator for another purpose or task): R20214 (dataset distillation), R15251 (VLM fine-tuning), R11047 and R04357 (detection or segmentation), R07538, R20143, R19805 (general augmentation).
- Duplicate pair: R14370 (conference) and R12656 (arXiv preprint) are the same smart-contract paper; both unsure.
- Most of the other unsures are clarification 3 combinations (existing generator plus an existing cleaning or selection step presented as new) or domain papers built on WGAN, CTGAN, DDPM or VAE-GAN where it is unclear whether the generator is new.

## batch014

batch 014: 200 of 200 records done; include 46, unsure 56, exclude 98
no records remain

Look at these first:
1. Low confidence (12): R21291, R16755, R04520, R04412, R16992, R04924, R16866, R06018, R02881, R13499, R21240 (all unsure) and R17473 (exclude E1, no abstract, "under data imbalance" in title).
2. Codebook conflicts:
   - R15688 (SMOTE-style synthetic series for forecasting) and R09450 (LLM self-improvement sampling) are recorded E2 (no classification). Clarification 1 (generator built for another purpose -> unsure) could also apply.
   - R09530 is a PhD thesis with several new SMOTE extensions. It meets I1 and I2 but fails I3, and no exclusion code covers theses. Recorded unsure U-other.
   - R21605 ("proposes a hybrid sampling strategy", RUS + SMOTE-ENN, in an IDS paper) and R07023 (SMOTE + k-means cleaning, Pima dataset) are recorded E1. Under clarification 3 both may belong in unsure. Other records were split by the same rule: combos claimed as a new method -> unsure (R09494, R13499, R05178); combos only "used/incorporated" -> E1 (R15691, R19323).
3. Questions the codebook does not settle:
   - Does moving existing samples count as generating them? R06750 MaMiPot was included (it is also used as a SMOTE preprocessor); R21508 DERSMOTE is unsure.
   - Does applying SMOTE in a learned embedding or latent space count as a change? R05210 SASMOTE was included; R20035 STESO and R19246 are unsure; R12533 is E1.
   - Existing GAN/VAE models used as oversamplers in a domain were excluded E1 (R19867, R18885, R04355, R03773, R17124, R05364, R15885). R01446 (text-GAN data-space oversampling of URLs) was included as a new technique.
4. Zenodo 2026 preprints in near-identical form, sent to unsure by clarification 2 (theory only): R18157, R17023, R17106, R17601, R21483, R19455. Check that they are genuine. R19455 "Graph SMOTE" shares its name with an earlier published method. R20204 (included) and R21508 do claim results on data.
5. Possible language or duplicate problems at full text:
   - Language field says en, but the venue may publish in Chinese: R00228 (included) and R07076 (unsure).
   - R04908 is a KNNOR software paper and may be E4 against the main KNNOR article.
   - R05757 (IGAN) may re-implement an earlier IGAN.

## batch015

batch 015: 200 of 200 records done; include 45, unsure 72, exclude 83
no records remain

Look at first:
- Possible inconsistencies: R16801 (include, high) applies an existing CTGAN in an autoencoder latent space, the same structure as R07106 (unsure); recheck R16801. R01600 (include, generates unseen fault classes) vs R03286 (unsure U-other, zero-shot feature generation).
- Codebook gaps: R03471 (new evolutionary SMOTE built for dose regression; excluded E2, but clarification 1 could apply); R00330 (oversampling by transferring real auxiliary-domain samples; excluded E-NOGEN, low); R01762 (prototype generation for multiclass imbalance; unsure); R02059 (smote-variants software package; excluded E-COMPARE, likely worth citing); R04620 (oversampling-rate sweep called a method; excluded E-COMPARE, low); R16036 (new time-series random oversampling, replication only; excluded E-NOGEN); R17419 (GMM oversampler for recommendation data; included).
- Include resting partly on keywords: R00605 (MultiBoost adaptation; SMOTE named only in keywords).
- I2 not stated (clarification 2): R20501, R22056, R18033 (2026 Zenodo SMOTE variants with theory-only abstracts); R03945, R02210, R10796 (Applied Soft Computing; experiments likely in the full text).
- Generators built for other purposes (clarification 1): R22356 (data-free quantization), R03286 (zero-shot learning), R13165 (few-shot face recognition), R06679 (fairness), R05281 (small-data virtual samples).
- Language: R19466 (listed Turkish, unsure); R03944 (Indonesian title), R08377 (Arabic), R11609 (Russian) excluded on content.
- Low-confidence excludes: R22039, R00999, R18474, R07784, R09899.
- Most method-like of the clarification-3 unsures (existing generator plus existing cleaning or selection): R05252 (SMOTE-LOF), R05514 (SMOTEOSS, 11 datasets), R20565 (k-means plus ADASYN, 9 datasets). R01006 and R01374 (both included) share one noise-filter method, possible E4.
- Included on title alone (no abstract): R03104, R21970.

## batch016

batch 016: 200 of 200 records done; include 54, unsure 67, exclude 79
no records remain

Look at these first (record number in batch order, then rec id):
- Low-confidence excludes, decided from the title only (no abstract): 41 R17387, 113 R22241, 124 R06442.
- Low-confidence include: 54 R02424 (batch-wise SMOTE+ENN inside LSTM training in a factory-quality paper; it could also be read as E1).
- Language: 50 R01096 excluded E-LANG (record language zh), but its SD-ISMOTE method is in scope. 121 R00321 included (B-ISMOTE); the metadata says en, but the venue is a Chinese journal, so check the full-text language. The no-abstract records 35 R01541 and 81 R03760 are in Korean venues.
- Document types the codebook does not settle: 141 R01596 is a doctoral thesis proposing HSBagging, marked unsure because I3 lists only journal, conference and preprint and no exclusion code fits. The book chapters 88 R16043 and 147 R03347 were excluded as E1 on content.
- Clarification 1 (purpose other than imbalanced classification), all marked unsure: fairness 29 R03601, 32 R05574, 169 R08068, 179 R04379; EV charging planning with a SMOTE extension 182 R22331; segmentation domain adaptation 164 R15812; general augmentation 75 R12565, 148 R12138. Related case: 105 R18465 (differentially private upsampling) was included as I1-other but could be read as a privacy purpose.
- Clarification 2 (I2 not stated), mostly new SMOTE variants that would be includes once evaluation is confirmed: 4 R04170, 53 R16068, 48 R17240, 60 R20219, 64 R17399, 178 R19899, 129 R01335, 19 R00175, 154 R02133.
- Borderline E1 calls on existing generators applied in a domain: 59 R04502 (ACGAN feature generation, "we apply this idea"), 68 R05403, 79 R05650, 23 R18859 (CTGAN with a range constraint).
- Possible consistency issue: 62 R20825 (SMOTE applied per region) was marked unsure, while the cluster-wise SMOTE in 117 R09155 and 65 R02544 was included.
- 133 R02709 (parSMURF) was included, but it is a parallel version of an earlier sequential tool, so check E4 at full text. 7 R00983 (deep boosting): unclear whether SMOTE is part of the method.

## batch017

batch 017: 200 of 200 records done; include 55, unsure 64, exclude 81

Look at first:
1. Excludes that may belong under clarification 3 or the unsure rule (decided before I fixed my rule; similar later records went to unsure): R02970 (NCR+SVMSMOTE presented as the proposed approach), R06736 ("proposed combined over/undersampling"), R06950 (CU-SMOTE) and R12205 (ISMOTE, low); compare R09946, R04129, R09007, R12094 (all unsure).
2. Same pattern, different calls: new over/under-sampling methods where the abstract does not say whether examples are synthetic or replicated: R00750 (include), R04700 (include, low), R00261 (unsure). New replication-only oversamplers were excluded E-NOGEN (R21450 RSFR, R00169, R05525 ROS+NCL); the codebook does not name random-oversampling variants.
3. Low-confidence includes, mostly a standard GAN or SMOTE applied with little stated novelty: R05685, R03912, R19280, R21540, R02455, R20650, R15581, R09127, R10109; R01361 is medium but the same type.
4. Not settled by the codebook: frameworks that tune how far to oversample (R05476 include high, R12982 include low, R09023 Imba excluded); software packages coded E-COMPARE (R03956 SOUL, R01528 smotefamily); a reproduction study (R21390); a SMOTE privacy-attack paper (R15442, E-NOGEN, relevant to the survey's discussion); theses (R20491, R10302 excluded; R00732 included, may be a dissertation); generators for object detection (R15592 unsure, R07726 excluded).
5. Unsure under clarification 1 (purpose other than imbalanced classification): R00693 SMOTER (regression), R11235 RSmote (PINNs), R07164 SMOTE-CD (compositional targets), R15272 (correlation), R08506 (outlier generation), R12716 and R08433 (privacy), R21544 (continual learning), R16625 (data scarcity).
6. Language doubts (field says English): Chinese journals R00298, R00712, R00122, R22267 (all included) and R20706 (unsure, Chinese title); R10302 (Greek title) and R03651 (Indonesian title) were excluded on other grounds; R15611 was excluded E-LANG (Korean abstract).
7. No abstract but the title clearly proposes a new oversampler (unsure, likely includes if evaluated): R14280, R11258, R01848, R02237, R21023, R05253.
8. Possible earlier/later versions (E4 at full text): R02445 (BGOA) and R02538 (GOT), the same graph-oversampling line for identifying lonely students.

## batch018

batch 018: 200 of 200 records done; include 53, unsure 55, exclude 92

Look at first:
- Possible inconsistency: R22240 (WCGAN-GA-RF) was excluded E1, but similar frameworks that use an existing GAN as their balancing component (R16266, R13276, R05528) were marked unsure. Suggest moving R22240 to unsure.
- Low-confidence includes: R19616 (improved SMOTE claimed, change not described), R05174 (augmentation-based balancing module), R14454 (bilingual Ukrainian/English abstract; check the paper's language). R00247 (ISMOTE) may be published in Chinese.
- Low-confidence excludes: R03910 (balancing unlabeled imagery, no synthesis described), R19873 (targeted minority augmentation in a deepfake detector).
- Codebook does not settle SMOTE parameter or ratio tuning: R14638 (OpTunedSMOTE) included I1-other, R16910 (GA-tuned ratio) unsure, R13757 (manual SMOTE ratios) E1, R01145 (empirical balancing level) E-COMPARE.
- New oversamplers that only duplicate examples were excluded E-NOGEN because I1 requires synthetic examples: R22380 (FERS), R01610 (SPIDER3), R08048 (ROS in ensembles), R02817.
- Theory papers: R11388 (analytical distribution of SMOTE) was excluded E-NOGEN for lack of a better code, though it may matter for background. R03516 (generalization bound that sets the resampling amount) is unsure.
- Oversamplers built for regression (clarification 1), marked U-other: R10682, R10077, R14800. R20185 (self-consuming diffusion study) is also U-other.
- Oversampling of unknown type (unclear whether it synthesizes or replicates), marked U-other: R18320, R02677, R07777, R00227, R00275, R00132, R02019, R03251, R01563.
- Possible later version (E4 at full text): R04278 (extended C-SMOTE study). Book chapters (I3 lists only journal, conference or preprint): R05552, R00267, R16673. R02202 is typed Review but is a research paper.

## batch019

batch 019: 200 of 200 records done; include 42, unsure 71, exclude 87
no records remain

Look at these first:
1. Low confidence: R09553, R08263, R02314 (title and abstract do not match; the abstract repeats SMOTEBoost text), R02497, R16220, R07761, R00256, R02609, R06402, R03101, R12677, R07771, R01302, R05624, R04366 (all unsure); R06384 (exclude E-NOGEN, no abstract).
2. Codebook does not settle: standard SMOTE as preprocessing for a new classifier, with SMOTE part of the method's name or design (R07839, R02820, R00200, R03240, R00679; also R01675). All marked unsure. Where SMOTE is only a generic step in a larger framework I excluded as E-NOGEN (R02911, R21529).
3. Codebook does not settle: document types that I3 does not list. Book chapters R11228, R00507 (venue name and wording suggest a journal), R02609, R01001, and thesis R00112 are all unsure (U-other).
4. Metaheuristic or AutoML tuning of oversamplers, please check these as a group. Included where the record presents a new SMOTE variant (R08028, R17203, R17394). Excluded where it tunes existing samplers for a domain (R06287) or where the contribution is the optimizer (R16600). Unsure: R07450, R07771, R00718.
5. Oversampling by replication or cloning, with no synthetic examples, excluded as E-NOGEN: R06597, R06796, R00317, R02467, R00357. Please confirm that this is out of scope.
6. Included although the abstract does not say the oversampling is synthetic: R00519, R01273, R06514.
7. Inconsistency to check: R06485 (SMOTE plus bootstrap in a one-versus-all scheme) is included as I1-hybrid, but R02497 (SMOTE plus bootstrapping) is unsure.
8. Nine theoretical-only Zenodo 2026 SMOTE variants, unsure under clarification 2: R20522, R19901, R17975, R21906, R21458, R18471, R19030, R18035, R17022.
9. Language: the metadata says English for R00317 and R00297, but both are in Chinese journals, so the full text may be in Chinese. R03242 was excluded E-LANG; apart from language it would be in scope.
10. R21539 is a retraction notice (E-REVIEW) for an in-scope paper: the PSO and Egyptian Vulture optimized SMOTE (Information, 2022). The survey should not cite that paper as sound.

## batch020

batch 020: 200 of 200 records done; include 33, unsure 71, exclude 96
no records remain

Look at these first:
- Calls the codebook does not settle: R08230 (COVERT, a classless oversampler for regression or process modelling) and R13295 (a GAN inside a transaction anomaly detector) were coded E2, but clarification 1 may send them to unsure. Oversampling that makes no synthetic examples was coded E-NOGEN: R02462 (EHSO, random replication), R07454 (ALHS, minority picked from unlabeled data by label propagation), R00146, R03883. Tools that pick among existing oversamplers: R08320 (BALANCER, E-NOGEN) and R05747 (E-COMPARE).
- Language and document type: R03876 and R04124 were coded E-LANG because their abstracts are in Korean, though the metadata says en, and both propose in-scope oversamplers. R00279 and R00063 (include) and R00522 (unsure) are from Chinese-language journals with English abstracts, so check the full-text language. R00965 (CBROSE, a CRC Press book chapter) is unsure on I3. R04926 (Pattern_Syn, a chapter in the LNDECT proceedings series) is included.
- Low-confidence includes: R05032, R04121, R05315, R01761, R21567, R14652, R01949. Doubtful excludes: R04692 (manual augmentation plus SMOTE), R16077 (SMOTE plus KNN called "proposed"), R01861 (applies G-SMOTE, but the abstract calls it novel), R15206 (no abstract).
- Why there are so many unsure: 15 follow clarification 2 (no evaluation named). Eleven of those are 2026 Zenodo preprints of named SMOTE variants that follow the same abstract pattern and mention no experiments. 6 follow clarification 1 (generator built for another purpose). 12 follow clarification 3 (existing SMOTE plus a cleaning or selection step presented as new). 8 have no abstract. The other 30 are papers whose resampling is named or called improved but not described, or where it is unclear whether new examples are synthesized. The weakest of these (low confidence) are R05286, R18488, R08120, R10277, R09177, R09848, R10126, R14220, R16196, R11965.

## batch021

batch 021: 200 of 200 records done; include 43, unsure 84, exclude 73
no records remain

Look at these first:
- Low-confidence includes: R00980 (DBCS), R01008 (big-data oversampling), R22329 (TimeLT tail augmentation), R00350 (RUS + boundary SMOTE), R00751 (improved SMOTE, not described), R12434 (dynamic SMOTE/GAN oversampling), R00144 (K* distance in SMOTE, SMOTE-SMaRT).
- Low-confidence excludes: R19475 and R00100 (no abstract), R19517 (custom extrema oversampling in a trading model), R19539 (optimizer-tuned MSYN in an IDS).
- Clarification 3 sends the seminal Batista et al. 2004 SMOTE+Tomek / SMOTE+ENN paper (R00006) to unsure; it is likely in scope. Same rule applied to R00970, R01127, R00405, R17628, R10546, R05951, R16978.
- Language: R20864 (G-CTGAN) has a Korean abstract but record language "en"; in scope if the paper is English. R22205 excluded E-LANG (Spanish) although its generator would otherwise qualify.
- Not settled by the codebook: pseudo-label or relabel "oversampling" (R05625 and R22133 excluded E-NOGEN; R02308 unsure; R12037 included); replication-only oversampling schemes (R04003, R04144, R01366, R02122, R06508, R10273); mixup-type feature mixing (R17549, R10770).
- Clarification 2 (I2 not stated): eight theory-only SMOTE-variant preprints on Zenodo with no experiments named: R21011, R20997, R22233, R20627, R21661, R17968, R17108, R16928.
- Purpose other than imbalanced classification (clarification 1): R09229 (fairness PC-SMOTE), R05146 (homomorphic-encryption SMOTE), R09482 (EHR GAN), R05868, R10019, R06343. Regression: R06411 GOLIATH unsure (regression-only evaluation); R10318 excluded E2.
- Consistency check for domain papers with GAN oversamplers: R02256 and R02115 included, but the similar R12689, R13277, R06361 and R02983 were marked unsure. Clustering-based SMOTE variants: R04289 and R04068 included, but R03530 (KSMOTE) and R00717 unsure.

## batch022

batch 022: 158 of 158 records done; include 22, unsure 46, exclude 90
no records remain

Look at these first
1. Low-confidence excludes: R21182 (AFCM-SMOTE step in a pile-capacity pipeline; target looks like regression, unclear whether AFCM-SMOTE is the authors' own), R10105 (no abstract, SRF-KELM domain model), R04204 (titled a survey, but the abstract describes ensemble SVM with a SMOTE-IPF-like extension and names no evaluation), R17703 (no abstract, imbalance-aware ECG network).
2. Low-confidence unsures, mostly domain papers whose resampling step is unnamed or only vaguely new: R03360, R18558, R14489, R12494, R07854, R04839, R08830, R08567, R13739, R06585. Also R12162 (no abstract), R11598 (RL agent picks among existing samplers) and R11272 (GAN-LSTM CPS detector, possibly anomaly detection only, E2).
3. Borderline calls made one way or the other:
   - Includes: R02786 (DCGAN oversampling of crash data reshaped to 2-D matrices; the plain GAN/AAE applications R03984, R12147, R03520 and R14797 were excluded E1), R00949 (GA auto-tuning of DBSM), R08722 (Ensemble-SMOTE aggregates SMOTE variants), R04438 (GEP-NB), R03011 (semi-supervised oversampling, unclear if synthetic), R09706 (feature-level oversampling inside a PolSAR model).
   - Excludes: R17892 (comparison paper that includes a SMOTE-NC-CTGAN hybrid), R08186 (new cluster undersampling, then existing ADASYN/SMOTETomek), R01603 (local vs global distributed SMOTE analysis), R02857 (SMOTE tuned by grid search).
4. Cases the codebook does not settle:
   - Parameter tuning of SMOTE (GA, metaheuristic, grid or threshold search): R00949 include; R12494 and R02465 unsure; R02857 and R02283 E1. A rule would make these consistent.
   - Informed replication with no synthetic data: R21754 (SVM slack-guided replication) excluded E-NOGEN; R01853 and R08830 unsure because the abstract does not say whether the oversampling is synthetic.
   - Theses: R08923 (HOVER graph oversampling, typed as a journal article) and R03571 (arXiv thesis summarising 12 resampling papers) marked unsure; I3 has no thesis category.
   - Erratum and comment: R18022 (erratum to an oversampling article, tagged front-matter-in-scope so the original can be checked) and R06828 (comment correcting a SMOTE theory paper) coded E-REVIEW for want of a better code.
   - Clarification 1 taken literally for R17978 (3D bone diffusion model for virtual trials): unsure, but probably out of scope.
   - Clarification 3 applied to combinations that are already named methods: R13406 (SMOTE plus ENN, i.e. SMOTE-ENN) and R01343 (A-SUWO plus NCL): unsure.
5. Zenodo preprint series: seven new SMOTE variants reporting only theoretical analysis (R22038, R18193, R16056, R16709, R18203, R20853, R21494), all unsure U-other ("I2 not stated"). They share one abstract template and may come from one source.
