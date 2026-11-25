# Notes of the screening sessions, by batch

## batch001

batch 001: 200 of 200 records done; include 30, unsure 14, exclude 156
no records remain

Look at first (record position / rec id):
1. Cases the codebook does not settle:
   - 154 R09530: a PhD thesis with five new SMOTE extensions. It meets I1 and I2, but it is unclear whether a thesis passes I3. Marked unsure (U-other).
   - 102 R15688: oversampling used to make synthetic time series for forecasting. I coded it E2 (regression only). Clarification 1 (a generator built for another purpose goes to unsure) could also be read to cover it.
   - 84 R09534: a 3D point-cloud detector that resamples objects to balance easy and hard ones, not classes. Unsure (U-other) per clarification 1; probably an exclude.
   - Excluded only for language, though the content looks in scope: 13 R06497 (K-means-SMOTE, Chinese), 94 R06630 (SMOTE+WGAN "OSW", Chinese), 153 R09284 (improved SMOTE, Chinese).
2. Borderline calls under clarification 3 (an existing generator plus a cleaning or clustering step); please check these for consistency:
   - 8 R10825 SMOTE-PCA-HDBSCAN: unsure. 103 R04277 Kalman-SMOTE: include, medium. I treated the Kalman filter as a new cleaning step and HDBSCAN as close to existing DBSCAN filtering.
   - Cluster-then-SMOTE: 173 R03354 unsure; 183 R10934 ADBSCSL include, medium; 43 R07175 E1, medium (PyCaret K-means + "clustering-guided SMOTE"; arguably unsure).
   - Excluded as E1 at medium confidence: 19 R21605 (RUS + SMOTE-ENN called "proposed"), 134 R10049 (SMOTE + cost-sensitive LightGBM), 200 R18049 (SMOTE with a dynamically adjusted ratio), 182 R06736 ("proposed" over+under sampling).
   - Fusion over unchanged resampling, coded E-NOGEN at medium: 143 R04677 (ECC), 180 R00663 (IBEP).
3. Includes at medium confidence: 42 R06231 (Eigen-Entropy-guided oversampling; unclear whether it generates synthetic samples), 79 R05582 (fairness-oriented oversampling), 111 R01642 (AE/GAN oversampling for sequence anomaly data), 131 R22206 (multi-label feature interpolation), 198 R16945 (improved SMOTE inside a feature-selection method).
4. Existing generative models used inside domain pipelines, coded E1 at medium: 26 R22040 (TimeGAN+SMOTE, mostly forecasting), 137 R18885 (plain GAN), 161 R10436 (CGAN).
5. Low-confidence unsure: 5 R07239, 17 R00326, 128 R17054, 158 R20531, 171 R02803. No abstract: 41 R15206 and 82 R13814 (unsure), 187 R12582 (E1, low), 104 R20006 (E-COMPARE), 149 R19261 (E-REVIEW).
6. 93 R19984: proceedings front matter that lists an in-scope title ("FCM-RF-SMOTE framework"); tagged front-matter-in-scope.

## batch002

batch 002: 200 of 200 records done; include 25, unsure 18, exclude 157
no records remain

Records a person should look at first:
- Cases the codebook does not settle: R22258 (theory paper on when synthetic minority augmentation helps; coded E-COMPARE for lack of a theory code, may matter elsewhere in the survey); R03478 (long-tailed detection that over-samples stored instance features, coded E-NOGEN); R12989 (evaluation of GPT-4 few-shot minority text generation, coded E-COMPARE).
- Borderline includes (medium confidence): R15468 (SMOTEHashBoost: SMOTE inside boosting vs clarification 3, evaluation only vaguely stated); R07445 (existing D2GAN plus adaptive neighbourhood cleaning, may fall under clarification 3); R03551 (novelty mainly in ACO undersampling); R09879 (relabeling augmentation that reuses majority-class readings); R03011 and R15170 (new oversamplers described in a single line); R19804 (generator built for general diversity, then used for class balancing); R13306 (GAN augmentation of sequences, possibly an existing GAN applied).
- Borderline excludes (medium confidence): R16524 (Borderline-SMOTE + ENN inside a domain pipeline, E1 rather than clarification 3); R19418 (benchmarks six existing generative oversamplers in a domain); R03940 (plain SMOTE used to build Wi-Fi fingerprint maps); R07723 and R07508 (no abstract, domain titles).
- Unsure, clarification 3 (existing generator + existing step presented as new): R00164, R15662, R08002, R06083.
- Unsure, resampler of unclear novelty in a domain paper: R04609, R10553, R13128, R13899, R08942, R02662, R10911, R03722, R19416, R02345, R05845.
- Unsure, other: R19256 (FI-SMOTE, I2 not stated in the abstract); R06884 and R02237 (no abstract, titles name new oversamplers).
- Language note: R04918 and R14474 have Indonesian titles but language field en; both excluded E1 regardless.

## batch003

batch 003: 200 of 200 records done; include 33, unsure 20, exclude 147
no records remain

Look at first (no low-confidence calls; 42 medium):
- Codebook does not settle: R01872 (MASI relabels majority samples as minority, no new points; unsure), R01652 (hybrid resampler whose oversampling copies boundary minority samples; unsure), R22008 (edge-based image augmentation for minority classes; included as I1-other), R12138 (Gaussian-sampling augmentation for small, imbalanced spectra; unsure).
- Clarification 1, purpose is fairness: R09229 (PC-SMOTE, PC-ADASYN on protected subgroups), R22151 (diffusion augmentation for underrepresented groups); both unsure.
- Clarification 3 borderlines: R00968 (NN/DBSCAN filter + SMOTE/RUS orderings; coded E-COMPARE because it is framed as an empirical study, could be unsure), R00793 (TRkNN + SMOTE on UCI; unsure, likely include), R20467 and R16280 (SMOTE + KNN filtering, Tomek + SMOTE, called proposed; unsure, likely E1).
- Claimed new oversampler in a domain paper, no detail: R04151 (KCV-SMOTE), R04643, R06457, R15421 (SMADASYN), R04255 (G-SMOTE), R07372 (SMOTE + FCM), R01951 (MuDIOT), R13183 (negation generation); all unsure. R04267 (WCP-SMOTE used inside an ensemble) was excluded E1 but may be the authors' own variant.
- Feature-space SMOTE: R19246 (presented as a contribution; unsure) and R18252 (two standard ways compared; E1). Check that these two are treated consistently.
- Medium-confidence includes where the abstract does not say how samples are made: R01564 (IOSDS), R05522 (HPACID), R19530 (Q-SYNTH). Others to check: R00182 (local PCA generation), R17210 (simulation-based SIM-GEN), R02395 (cWGAN-GP for XSS).
- I2 not stated: R02210 (unsure). No abstract, excluded E1 from the title: R13030, R17183, R17231, R04176. Front matter with an in-scope title: R04897.
- Language: E-LANG only where the language field is not English (7 records). R17692 (Chinese, IWGAN-GP oversampler) would otherwise be an include. Records tagged English with Indonesian titles were coded on content.

## batch004

batch 004: 200 of 200 records done; include 29, unsure 19, exclude 152
no records remain

Look at these first:
- Low confidence (all unsure): R12654 (GloVe "semantically-aware oversampling" for text, new or existing?), R05322 (sports-culture paper that claims to "optimize SMOTE"; vague), R17228 ("modified ADYVASAN-SMOTE" in a GWO-SVM pipeline), R17120 (unexplained "Ch-SMOTE" in a brain tumour framework).
- Clarification 3 sent to unsure (existing generator plus existing cleaning step, presented as new): R00315 HYBS (Borderline-SMOTE + Tomek), R10675 (SMOTE + CLNI/ENN), R08312 (DBSCAN + SMOTE), R08977 HSS, R15778 two-stage sampling.
- Borderline excludes: R05745 (SmoteENN + RF on CTG called "novel"; I coded E1 because SMOTE-ENN is an existing variant, not clarification 3), R17439 (ADASYN + OSS as a preprocessing step in a DL IDS), R03360 (HMM + "modified DBSCAN" + SMOTE), R06236 (ASMOTE-CFR, ASMOTE assumed existing), R07598 (SMOTified ELM), R07838 (ROS + RUS hybrid, coded E-NOGEN).
- Borderline includes (medium): R01189 and R18766 (SMOTE plus a new post-generation cleaning step, coded I1-hybrid, not clarification 3), R11634 (SMOTE inside each member of an NN ensemble), R13446 and R18096 (VAE / GAN minority generation inside a pipeline paper), R19711 ("novel cluster-based oversampling" inside an IDS), R08928 (SMOTE seeded on confident pseudo-labels in domain adaptation), R00032 (venue may publish in Chinese, so E-LANG may apply at full text).
- Not settled by the codebook: R15932 (software paper packaging existing oversamplers, no evaluation; coded E-REVIEW for lack of a better code), R08817 (FAWOS fairness oversampler, unsure U-other under clarification 1; may also be a re-publication of earlier FAWOS work), R00825 and R00679 (new ensemble/hybrid schemes, abstract does not say whether SMOTE or synthetic generation is inside), R22317 and R04531 (excluded E2 as regression; R04531 has no abstract).
- Four Zenodo preprints of similar style propose SMOTE variants but name no evaluation (clarification 2, unsure): R17974 CBS-SMOTE, R17399 ARG-SMOTE, R21439 R-SMOTE, R17100 Hard-sample SMOTE.

## batch005

batch 005: 200 of 200 records done; include 24, unsure 16, exclude 160

Look at first:
- Low confidence: R13753 (unsure; book chapter, cDCGAN for kidney images), R05912 (unsure; garbled abstract, "text-based sampling" for sentiment).
- Not settled by the codebook, book chapters: R00351 (SMOTE guided by reliability estimates, IGI compilation volume, likely a reprint) and R13753. Both are unsure because no exclude code exists for failing I3 on document type.
- Not settled, existing GAN/diffusion generators applied as the oversampler in a domain paper: R13211, R07218, R02415, R13753 are unsure. R03320 (cGAN as one pipeline step) is E1 at medium confidence. One rule would make these consistent.
- Clarification 3 borderline: R02225 (methods paper integrating SMOTE-ENN and SMOTE-Tomek using noise and overlap measures; may count as a "new cleaning step", I1-hybrid). R13496 (food-safety LOF-KNN-CSENN).
- Classification or regression: R16490 (spatiotemporal Bayesian oversampler for traffic prediction, unsure). R20486 (load forecasting with an "improved K-means-SMOTE", E2 at medium; if the improvement is the authors' own, clarification 1 makes it unsure).
- Medium-confidence includes: R03055 and R16555 (intrusion detection framed as anomaly detection or one-class, so E2 is possible), R00691 (BAOUS, evaluation only loosely stated), R00722 (sparse abstract), R01292 (D-Self-SMOTE), R02737 (kernel SMOTE hybrid), R08801 (MCMC-guided GAN).
- Medium-confidence excludes worth a glance: R01376 (ImWeights, example weighting, keyword "over-sampling"), R11136 (claims to optimize how SMOTE is applied), R17668 ("controlled SMOTE-based oversampling"), R18123.
- Coding convention: non-English records with an English abstract are coded by content (E1: R14282, R09831, R03886) with the language named in the reason. R06896 (abstract only in Indonesian) is E-LANG. R07576 is typed "Review" but is a computational comparison, coded E-COMPARE.

## batch006

batch 006: 200 of 200 records done; include 25, unsure 15, exclude 160

Records to look at first:
- Low confidence: R02314 (exclude E1; incoherent abstract on stress/crop yield that restates the SMOTEBoost abstract as "a new approach"); R22257 (unsure; SMOTE/CTGAN ordering ablation: is minority-only CTGAN->SMOTE a proposed hybrid or only a compared setting?); R06444 (unsure; HardVis, interactive visual-analytics choice of which instances to over/undersample; the codebook does not cover interactive tools).
- Meet I1, but I2 is not stated in the abstract (clarification 2): R06130 (DeepSMOTE), R18008 (Contrastive SMOTE). Both are likely includes at full text.
- Where to draw the line between a proposed generative oversampler and an existing generator applied in a domain paper. Please check these are consistent: included R02705 (PacketCGAN) and R18107 (CTGAN-MVL, a CTGAN per feature view inside an ensemble); unsure R08290 (WGAN-GP + CTST quality control); excluded R07648 (ACGAN "employed") and R19911 (diffusion augmentation in a diabetes pipeline).
- Clarification-3 unsures (existing generator plus an existing cleaning, selection or cost step, or a modification the abstract does not describe): R04007 (HOK-SMOTE), R07839, R02827 (SMOTEFRIS-INFFC), R06082 (CSK), R07622 (RO-SMOTE), R13665 (MMSOT, modification not described), R13691 (spectrogram augmentation vs other approaches).
- Other borderline calls: R00327 (included; the journal Jisuanji yingyong yanjiu likely publishes in Chinese although the metadata says en); R18828 (included; wavelet interclass-fusion ECG augmentation, which also augments the test set); R02835 (included; its Mahalanobis oversampling may be the existing MDO); R21591 (included; kernel-SMOTE inside a fuzzy LSTSVM/AdaBoost); R00990 (unsure; the abstract does not say whether the oversampling makes synthetic points); R05281 (unsure; virtual sample generator for small data, clarification 1); R20215, R16291, R19399 (excluded E1, medium; oversampling tweaks inside domain training pipelines).
- No abstract: R00841 (unsure); R21247 (excluded as a domain prediction study on the title alone).

## batch007

batch 007: 200 of 200 records done; include 20, unsure 20, exclude 160
no records remain

Records to look at first:
- Low confidence (all unsure): R04514 (stream fraud: replays stored fraud data, plus a clustering oversampler), R03440 (ensemble CNN with random oversampling and feature-subspace "data enhancement", multiclass HSI), R20587 (ADASYN parameters tuned by a metaheuristic; the codebook does not say whether tuning an existing oversampler counts as changing how it is applied).
- Existing GAN used as the oversampler (codebook does not settle this). Where the GAN oversampler is the paper's contribution I coded unsure: R05382 (Unrolled GAN), R02067 (GAN, defect data, I2 not stated), R06565 (WGAN, botnet). Where a GAN is one step of a domain pipeline I coded E1 at medium confidence: R07123 (SeqGAN in SCGRU), R06674 (GAN + AdaBoost), R17777 (GAN in a landslide pipeline). Please check where I drew this line.
- Borderline includes (medium confidence): R03229 (new MLP undersampling + existing MWMOTE, included as "SMOTE with a new cleaning step"), R10282 (GraphSMOTE-like node synthesis with a new edge-generator loss), R06473 (SMOTE + Gaussian-noise hybrid), R01424 (abstention samples as SMOTE seeds), R00478 (pattern-based oversampler, secondary to a tree ensemble).
- Possibly an existing variant applied in a domain: R05054 (Radius-SMOTE, which may predate this paper), R16802 (DTW-SMOTE), R14044 ("refined application of SMOTE"), R20035 (SMOTE in sentence-transformer embedding space), R03018 (Resample + SMOTE framework); R19506 (Dirichlet ExtSMOTE) was excluded E1 at medium confidence.
- Non-synthetic stream oversampling by reusing stored past minority samples, which the codebook does not cover: R03406 coded E-NOGEN (medium); R04514 sent to unsure because it also uses a clustering oversampler.
- I2 not stated in the abstract: R09418 (Weighted-SMOTE), R01001 (book chapter where experiments are only "suggested"; the codebook has no exclusion code for a book chapter failing I3).
- Other unsure: R13265 (generative augmentation in federated learning that also targets privacy and non-iid data), R05462 (comparison paper that includes the authors' own synthetic-lesion generator), R21447 (latent-space sampling in an FDIA framework), R12621 (FOLU/FULO orderings of over- and undersampling).
- No abstract: R02142, R21617, R12097 (the IOSMOTE title looks in scope).
- In scope but not in English, so E-LANG: R13127 (CTGAN + cascade reject sampling), R00178 (boosting that injects synthetic samples), R12103 (SMOTE + contrastive enhancement). Records that are both out of scope and not in English were coded on substance, with the language noted in the reason (R02816, R12376, R13326, R05135).
- R04551 is a retracted article (excluded E1).

## batch008

batch 008: 200 of 200 records done; include 28, unsure 20, exclude 152

Records to look at first:
- Low confidence (all unsure): R11860 (JAAD balancing/augmentation schemes: new methods or a comparison?), R06483 (HSCL: does minority oversampling create synthetic nodes?), R05947 (Centroid-based PF-SMOTE: new or applied?), R06863 (Borderline-SMOTE inside contrastive sleep staging: new use or preprocessing?), R19015 (few-shot LLM time-series generation: proposed generator or evaluation?), R15491 (STAS: over- or undersampling?).
- Borderline includes (medium): R05548 (score-based selective SMOTE inside F-LLR), R00246 (distribution-sampling balancer, coded I1-generative), R08902 (conversational sample generation, coded I1-other), R16702 (ARS-sampling inside an IoT framework), R12708 (improved Borderline-SMOTE, no details), R13167 (FG-SMOTE, fairness aim), R16721 (safety filter: new or existing?), R22333 (cluster/geometry-constrained SMOTE: proposed or only studied?), R05881 (SSMOTE), R02540 (oversampling inside boosting, vague), R08040, R12144, R19290, R07639.
- Borderline excludes (medium, E1: existing generator in a domain pipeline): R11708 (unnamed generator), R16072 (CVAE), R12013 (CGAN), R11135 (GPT-2), R11051 (QGAN for data scarcity), R01149 (SMOTE + RBM pre-training), R21953 (local SMOTE in federated learning), R07806 (SMOTE in a stream semi-supervised ensemble), R17369, R11756.
- Cases the codebook does not settle: language field says en but text is Korean (R07941) or Indonesian (R06914), both coded E1; Chinese papers with possibly in-scope methods excluded E-LANG (R05689 GAN+FID oversampling, R06484 overlap-region hybrid sampling); book chapter that could otherwise qualify (R00267, unsure); Zenodo code/data records (R17884, R16086, excluded E1); clarification 1 (R03519 privacy face synthesis, R05868 small-sample synthesis); clarification 2, no data evaluation (R07091, R20522); no abstract (R19031); front matter with in-scope titles (R00895 radial-based oversampling, R00559 improved SMOTE by support degree).

## batch009

batch 009: 200 of 200 records done; include 21, unsure 17, exclude 162
no records remain

Records to look at first:
- Low confidence: R02173 (exclude E-NOGEN: PROSRUS, a new partial random over/undersampling allocation scheme; it duplicates rather than synthesizes, and the codebook does not say whether new random-oversampling schemes count); R06253 (unsure: title promises an "Enhanced SMOTE Strategy" but the abstract describes only a survey).
- Cases the codebook does not settle: R11235 (RSmote, a SMOTE extension for PINN collocation sampling; unsure per clarification 1); R01094 (OSTSC, an R package/tutorial for multiclass time-series oversampling; may only implement an existing method); R09632 (multi-label hybrid oversampler MLSOL+UCLSO, included and tagged multiclass because there is no multi-label tag).
- Borderline includes (medium): R06824 NKB-SMOTE; R00308 OAA-DB (balancing technique named only in keywords); R08605 (Kalman-filter SMOTE inside a multi-topic preprint, evaluation vague); R13293 and R03535 (domain papers whose GAN / Gaussian-process generators are part of the contribution); R02964 (K-means CTGAN); R02341 (CIR, generation mechanism not stated).
- Borderline excludes (medium): R06173 (graph SMOTE applied to blockchain "for the first time"); R11155 ("dual-phase SMOTE strategy" inside an IDS pipeline); R21689 (ChatGPT-generated minority data applied for balancing); R05237 (SMOTE in a regression task, coded E2); no-abstract domain titles R20356, R12318, R05456.
- Unsure under clarification 3 (existing generator plus cleaning, clustering or boosting, presented as new): R03328, R16917, R11062, R05920, R09270, R05501.
- Language metadata conflict: R11365 coded E-LANG (Indonesian title and primary abstract, language field "en"); R13935 (Indonesian title, English-only abstract) coded on substance as E-COMPARE.

## batch010

batch 010: 200 of 200 records done; include 32, unsure 15, exclude 153
no records remain

Look at these first (no record was coded low confidence; these are the borderline calls and cases the codebook does not settle):
- Rule 3 edge cases: R20175 (ADASYN+ENN named as the pipeline's "hybrid oversampling") is coded unsure. R06299 (RUS+SMOTE "is proposed") and R07479 (SMOTE+Tomek inside a "proposed model") are coded E1 because their contribution is the detector, but rule 3 could send them to unsure.
- Applying an existing generator within clusters, counted as changing where synthetic examples are made: R16142 (fuzzy k-prototypes + SMOTE-NC) and R02544 (clustering + oversampling + RF), both include I1-hybrid, medium. A new selection step applied to an existing generator: R20703 (DiVuse) is include I1-hybrid; R16750 (Stable Diffusion + CLIP filter) is unsure.
- Generators whose scope or novelty is unclear, all include at medium: R10770 (class-balanced Mixup for long-tailed images); R22069 (Jacobian data augmentation for imbalanced, adversarial fraud detection); R19310 (FireFly metaheuristic used as an oversampler); R00583 (bag-level MIL oversampling; synthetic generation is not stated).
- Domain papers with a "proposed" generator coded differently; please align them: R02906 is include, R18820 is unsure. Plain GAN oversampling in a domain pipeline: R10297 and R06413 are E1. GAN/VAE oversampler comparisons: R02155 and R02902 are E-COMPARE (R02902 calls WGAN-GP and WcGAN-GP "new methods").
- Other calls at medium confidence: R10547 (existing GDHS sampler paired with GBDT, E1); R04204 (titled a survey, describes a SMOTE-IPF-like method, E1); R00618 (big-data analysis of oversampling ratio, E-COMPARE); R01546 (include, but a book chapter, so I3 needs checking); R18313 (include, but the abstract is garbled and names no datasets); R19901 (unsure, I2 not stated in the abstract).
- No abstract: R04212 (exclude) and R06925 (exclude, E-COMPARE). R19234 is excluded under E-LANG (Chinese) but proposes a new GAN oversampler (GPSC-GAN); otherwise it would be in scope.

## batch011

batch 011: 200 of 200 records done; include 19, unsure 16, exclude 165
no records remain

Look at first:
- Low confidence, unsure but leaning exclude: R14272 (MixGAN: pretrained CTGAN inside a new semi-supervised DDoS detector), R07761 (overlap-removal undersampling with SMOTE listed; may be E-NOGEN), R16944 (precipitation: "physics-informed augmentation" vs SMOTE/GAN, mostly an evaluation), R20143 (Bernoulli perturbation augmentation vs balancing controls), R19123 and R17703 (no abstract; titles name imbalance-aware IDS/ECG networks).
- Includes to verify: R20222 (LSD-SMOTE; I2 only implied by "enhances the classification performance on imbalanced datasets", so clarification 2 may apply), R10073 (DDPM for solar flare images: new generator or applied DDPM?), R10030 (smart data augmentation for multiclass imbalance; unclear if it synthesizes examples), R05043 (improved ADASYN, improvement not described), R11266 (CTGAN plus new boundary-aware majority pruning).
- Excludes near the line: R12383 (existing TabDDPM as oversampler), R17095 (class-wise TVAE), R19645 (AC-GAN), R17156 (KMADASYN "applied"), R09054 (image-pair concatenation, E-NOGEN), R08095 (class flipping relabels, E-NOGEN), R17964 (comparison with a vague "refining" claim), R22011 (SMOTE evaluation framework: review or empirical?).
- Codebook does not settle: R13271 (GAN minority augmentation for object detection, not plain classification); R01605 and R00005 (oversampling may be duplication: I1 vs E-NOGEN); R02633 (deep generative oversampler benchmark "including our own": new method or E-COMPARE?); R21526 (clarification 2, I2 not stated).
- Conventions: non-English records coded E-LANG even where E1 also applies (R10218, R20769, R14462, R18403). Records with Indonesian titles, English abstracts and language "en" were coded on substance (R12319, R03793, R11330, R09663, R09068).

## batch012

batch 012: 200 of 200 records done; include 20, unsure 20, exclude 160
no records remain

Look at first:
- Low confidence (all unsure): R07454 (ALHS: "oversampling" labels real unlabeled instances by label propagation, so is that synthetic generation?); R10149 and R15103 (LLM or text augmentation against imbalance: a method or applied?); R11534 (on-the-fly image augmentation "ADT" for DR grading; title in Indonesian although the language field says en).
- Not settled by the codebook: domain papers that generate minority samples with an off-the-shelf LLM (R10149, R20205), and R03756 (conditional GAN/VAE oversamplers studied empirically: I1-generative or E-COMPARE?).
- Consistency check: R20048 (E1, medium; IDS using Borderline-SMOTE-OSS and ADASYN/SMOTE-ENN) is close to R15746 (unsure under clarification 3; named TB-SMOTE component). One of them may need to change.
- Medium-confidence excludes where the abstract says SMOTE is "proposed" or "innovative" but describes no change: R08327, R05779, R15006, R12658 (unknown "MOSD" oversampler). Also R00255 (standard SMOTE plus a new PSO-RBF classifier).
- Includes from thin abstracts: R02244 (Improved SMOTE, no details given); R00184 (mix-ratio multiclass sampling, base oversampler not stated, may be duplication); R09873 (RN-SMOTE extended to multiclass, may be only an application); R01615 (SMOTE inside gcForest); R10913 (ADASYN+GAN ensemble); R06322 (two-stage CGAN, use in classification implied); R00298 (no venue, check language).
- No abstract (unsure): R01054 (instance types and SMOTE, LIDTA 2017), R05898 (bank failure, SSRN).
- Non-English records coded by content as E1, with E-LANG noted in the reason: R11462, R01472, R03586, R20939, R20103, R21810.

## batch013

batch 013: 200 of 200 records done; include 26, unsure 21, exclude 153

Look at first:
- Codebook does not settle: R11388 (theoretical analysis of SMOTE's sampling distribution; no code for theory papers, coded E-COMPARE + comparison, low); R00940 (book chapter, included) and R00110 (dissertation, unsure) against I3; R00732 (included, reads like a thesis summary); R17099 (regression with a new knowledge-graph GAN generator: E2 vs clarification 1, coded E2).
- Low-confidence unsure: R17793 (per-mechanism WGAN-GP, framed as an evaluation), R14833, R13341, R00141, R08482 (oversampling layer for treatment-effect estimation), R10971 (ESMOTE), R07787 (CC-SMOTE), R00261, R21240 (generator for stress-testing a fuzzy system), R03178 (BSS-GAN), R21939 (no abstract).
- Borderline includes (medium): R01304 (minority side is plain SMOTE), R20134 (latent diffusion applied to IoT data), R04315 (back translation, I2 only implied), R07287, R06765 (graph oversampling as one model component), R16277, R08775, R05840, R08770.
- Borderline excludes (medium): R16092 and R11234 (existing TVAE/CTGAN applied, E1), R16185, R03863, R06462, R16095 (SMOTE plus DeepSMOTE), R03560.
- Language: R03971 (Chinese, E-LANG) would otherwise be a candidate (iForest-SMOTE hybrid); R14714, R20742, R19767 (Indonesian titles) and R01919 (Korean abstract) carry language "en" and were coded E1.

## batch014

batch 014: 200 of 200 records done; include 18, unsure 19, exclude 163

Records to look at first:
- Low-confidence unsure: R21540 (existing GAN used for cross-FOV synthesis of rare aurora images, detection task), R05404 (WGAN + meta-learning, bearing faults), R20710 ("Improved SMOTE" in the title, novelty unclear), R22117 ("improved MWMOTE", improvement not described), R01369 (oversampling + SVM parameter optimization, oversampler unnamed), R12982 (Bayesian optimization of sampling ratios with hyperparameters), R02398 (domain-adapted electrogram augmentations), R11841 (dynamic oversampling + temporal augmentation, video challenge), R04981 (oversampling for missing-data imputation; possibly E2), R00575 (LN-SMOTE modifications; I2 not stated; may be an overview), R11154 (no abstract, XGBoost + Borderline-SMOTE).
- Unsure by codebook rule (medium): clarification 3, an existing generator plus a selection or cleaning step claimed as new: R16368, R07978, R09960, R22115. Clarification 2, I2 not stated: R19516 (HA-SMOTE), R00620 (AdaBoost.Balance). Clarification 1, purpose other than classification: R08506 (outlier generation). No abstract, but the title names a new generator: R02055 (SMate, likely include).
- Borderline includes (medium): R16698 and R13474 (GAN+SMOTE hybrid generators inside domain pipelines), R09238 (per-class augmentation, generator unspecified), R01853 (SOM/GA resampling; the oversampling may be replication), R03530 (KSMOTE).
- Borderline excludes (medium): R00318 (random subspace + SMOTE, coded E-COMPARE), R00672 (SMOTE+LLE in a hospital study), R00852 (ordinal oversampling used alongside an evolutionary ANN), R12771 and R09894 (plain VAE/GAN augmentation in domain papers), R10853, R21303, R20112 (pipelines whose resampling step is not claimed as new), R17770 (SMOTE in CLIP feature space), R07210 (SVM on correlated covariates), R11620 (negative-sample oversampling for drug repositioning).
- Cases the codebook does not settle: R22325 (BaggFold oversamples the majority, not the minority; coded E-NOGEN). R11829 (off-topic book chapter with no abstract; there is no off-topic code, so coded E-REVIEW). R06877 (Chinese-language GAN oversampler that is in scope on content; coded E-LANG).
- Rules I applied consistently: clarification 3 was used only when the resampling combination itself is claimed as new. When only the overall framework is claimed as new, the record is coded E1. Domain papers that apply an unmodified GAN or VAE are coded E1 unless the abstract describes a change to the generator.

## batch015

batch 015: 200 of 200 records done; include 19, unsure 13, exclude 168

Records to look at first:
- Codebook gap, oversamplers that duplicate rather than synthesise: R06796 (multi-label, clones borderline samples at a risk-based rate) and R00169 (random oversampling restricted to SVM boundary examples) were excluded as E-NOGEN (medium confidence) because nothing synthetic is generated. Confirm the survey leaves such methods out.
- Unsure where existing tools are combined or novelty is only claimed (clarification 3 and similar): R12243 (SMOTE-ENN + GAN), R05286 (VAE + ADASYN), R07169 (SMOTE-RUS), R13498 (NearMiss-1 + SMOTE), R05913 (SMOTECU, 16 benchmark datasets), R09315 (K-means SMOTE + WCGAN + KNN screening), R06091 (claims "a unique SMOTE algorithm" without describing it), R00801 ("newly proposed hybrid approach"), R16129 (natural-neighbour adaptive oversampler for multiclass fault data, unclear if new).
- Unsure because the multiclass scheme is borderline: R10725 (existing oversamplers applied per node of a multiclass decomposition tree) and R01362 (block-wise over/undersampling in networked multi-label active learning).
- Clarifications 1 and 2: R03488 FAWOS (oversampler built for fairness, U-other) and R21519 P-SMOTE (only theoretical analysis, I2 not stated). R20091 KIR-SMOTE was included because the abstract reports "Synthetic results"; check that I2 is met.
- Medium-confidence includes: R02203 (Cluster+Boost) and R12037 (CHRE) do not say whether the new examples are synthetic or duplicated; R19316 (modified AC-GAN), R20885 (PCA-CSSF synthetic sample filter) and R16715 (APOEA subview oversampling) are domain or ensemble papers where the oversampling is one part of the method; R04990 is typed as a book chapter in a Springer lecture-notes proceedings series (check I3).
- No abstract, so decided from the title alone: R21820 (E1, low), R19194 (E-NOGEN), R14332 (E2, physics field prediction).
- Exclusions near the boundary: R09904 (standard GAN oversampling in a finance model, E1), R13701 (existing diffusion and pix2pix for dental segmentation, E1), R06287 (evolutionary tuning of the sampling ratio, E1), R06388 (feature selection + SMOTE named "FS-SMOTE", E1).
- Methods that would be in scope but are excluded only for language (Chinese, E-LANG): R05754 (CGAN trained on SMOTEENN output), R01248 (SMOTE inside bagging with an adjustable rate), R15587 (density-peak boundary oversampler).

## batch016

batch 016: 200 of 200 records done; include 31, unsure 11, exclude 158
no records remain

Look at these first:
- Low-confidence unsure: R17638 (jittering with classifier-guided selection, sarcopenia), R02565 (overlap-based undersampling that also oversamples the borderline; unclear if any synthetic examples are kept), R04968 (matrix-sketching rebalancing; unclear if minority examples are synthesized or the majority is only compressed), R00986 (dynamic oversampling during NN training; synthetic or replication?).
- Other unsure: R21316 (no abstract, but the title names a new multiclass oversampler, PROSTENN; probably include if it is evaluated), R07430 (two-stream hybrid generator), R06372 (FedBIP segmentation-based oversampling), R02820 (SMOTE-CSELM; is SMOTE applied in ELM feature space?), R20088 (KFCGAN-OVO: Kalman filter + CGAN + OVO), R20194 (Turkish LLaMA-3 augmentation case study), R15157 (U-other: latent-diffusion generator for semantic segmentation, not classification).
- Low-confidence excludes, no abstract: R17529 (bearing diagnosis; title names features + adaptive ensemble), R09119 (crash severity; title names ensembles + sampling techniques).
- Borderline includes (medium): R00154 (ensemble that synthesizes from hard examples; minority unclear), R06275 (OT image mixing for long-tailed classes), R00864 (VFSG face oversampling inside a dataset paper; abstract garbled), R02073 (balancing rules for allocating samples), R02424 (batch-wise SMOTE+ENN), R00530 (MIL target-concept oversampling), R02023 (pulsar-specific augmentation), R05740, R15616, R16983, R02204.
- Codebook does not settle: R02059 (smote-variants software package; coded E-COMPARE + comparison as a survey resource), R22302 (BL-SMOTE + PSO-tuned fuzzy SVM, a general method not a domain one; coded E1), R16053 (review that presents an "Adaptive SMOTE Tomek"), R02924 (front matter; tagged front-matter-in-scope for the multilabel-oversampling and sarcasm-imbalance titles).
- Off-the-shelf GAN/CTGAN uses coded E1 at medium: R19494, R05966, R11608, R12980. Indonesian titles with language "en" (paper language may not be English; excluded on E1/E-COMPARE anyway): R20094, R11361, R18962.

## batch017

batch 017: 200 of 200 records done; include 20, unsure 17, exclude 163
no records remain

Look at first:
- Low confidence: R13431 (unsure; BioMedBERT super-ensemble over models trained on over/under/hybrid-balanced data; does ensembling resampling strategies count as changing how oversampling is applied?).
- Excludes that could hide a method: R11758 ("novel LightGBM hybrid" with an oversampling module; could be SMOTE inside boosting), R22133 (TriMa pseudo-label augmentation pitched as a SMOTE alternative; coded E-NOGEN), R07406 (IRF imbalance-ratio formula vs SMOTE/ADASYN; weighting or sampling unclear), R01145 (comparison that also "proposes" a way to choose the balancing level), R00633 (ensemble of ensembles, Neurocomputing 2015), R19879 (keywords mention a ChatGPT prompt; balancing may be LLM-generated), R05528 (CGAN "employed" inside a transfer-learning method), R03506 (title features most-distant undersampling + Safe-Level-SMOTE; clarification 3 may apply).
- Consistency on ratio/allocation tuning: R16414 (Auto Balance, a standalone ratio-search algorithm) sent to unsure, while R02834, R19536, R14489 (SMOTE with tuned or per-class targets) were excluded as configuration. Please confirm the line.
- Medium-confidence generative includes from domain papers: R18083 CropGAN, R10123 SynDroid, R04517 Dazzle (BO-tuned cWGAN-GP), R16434 GeNSDP, R01598 K-means improved WGAN, R05702 VAE-WGAN-GP.
- Not settled by the codebook: generators built for segmentation sent to U-other (R17698 MoG-LISA, R03351 fusion over-sampling); three SMOTE variants with theoretical analysis only and no data evaluation (R21483, R16916, R17096; Zenodo 2026 preprints in a similar style; U-other per clarification 2).
- E-LANG records that propose new oversamplers (may matter elsewhere): R07286 SMOTE-NND, R01076 improved SMOTE, R05665 VBoGMM adaptive sampler (all Chinese).
- Data issues: R15880 title field holds an unrelated Indonesian abstract; R03191 is an off-topic ADC circuit paper coded E-NOGEN for lack of an off-topic code; R11034 is regression (RMSE) with SMOTE-NC, coded E1.
- No abstract: R19481 unsure (generic chapter title); R03483, R04955, R07824, R01519 excluded E1 (medium) on domain titles.

## batch018

batch 018: 200 of 200 records done; include 19, unsure 26, exclude 155

Look at first:
- Low confidence (all unsure, each probably exclude): R00867 (SMOTE with DECORATE for multiclass microarray, may be plain preprocessing, E1), R17572 (replay-sample generator for lifelong person re-ID; clarification 1 applied literally, almost surely out of scope), R16073 (Telugu NLP "targeted minority oversampling" plus de-duplication, probably E1).
- Codebook gap, book chapters or theses with in-scope methods (I3 unmet, but no exclusion code for these document types): R00965 (CBROSE, CRC Press), R01341 (AEMNOST, CRC Press), R00737 (thesis abstract, HMM used for class balancing). All coded unsure U-other.
- Codebook gap, new cluster-based oversamplers whose abstracts do not say whether they make synthetic examples or duplicate: R00813, R02993 (and swarm rebalancing R00738). Coded unsure U-other.
- Codebook gap, mixup-style long-tail augmentation (does mixup count as synthetic minority generation?): R15300.
- Clarification 1 (generator built for another purpose): R19805 (vision-language model images for data scarcity), R10682 (ISCOTE for tool-life regression), R17572. Clarification 2 (I2 not stated): R13311.
- Borderline consistency calls on existing GANs in domain pipelines: E1 for R12110 and R21984 (CTGAN), R12069 (WGAN) and R11023 (GAN as one component); unsure for R12276 (title stresses GAN design) and R10081 (SNGAN plus screening of generated samples).
- Medium-confidence includes worth a second look: R01000, R15204, R08825, R07808 (framed as anomaly detection but classifier-based), R22067, R01407, R02926, R12014 (could re-implement an existing CWGAN-GP oversampler).
- Excluded only for language although the method is in scope: R06802 and R00462 (both Chinese). Front matter with an in-scope title: R09211.

## batch019

batch 019: 200 of 200 records done; include 21, unsure 19, exclude 160

Look at first:
- Low confidence (no abstract, excluded E1 on title only): R16787 (SSRN credit-scoring preprint), R20479 (book chapter, badminton).
- Medium-confidence includes (scope edge): R08479 (EdgeCutMix image augmentation for minority classes), R01708 (conformational oversampling of molecules), R01388 (seq2seq kNN used as an oversampler), R16369 (ADASYN-FLS-SMOTEBoost inside an IDS framework), R19822 (Borderline-SMOTE + Giza Pyramids metaheuristic), R13633 (domain-aware SMOTE-ENN with physiological constraints).
- Borderline excludes: R03115 (SMOTE+Tomek called a "proposed hybrid" in an IDS paper; I treated SMOTE-Tomek as an existing variant, E1, rather than clarification 3), R00592 (BSMAIRS: Borderline-SMOTE + AIRS classifier on 8 UCI sets, E1), R17892 and R17547 (comparisons that include a SMOTE-NC-CTGAN hybrid / GP-Aug and TP-Aug generators that may be the authors' own, E-COMPARE), R19047 (applies unfamiliar "TPH-SMOTE" and "KHOI-SMOTE", E1), R18467 (Stable Diffusion + LoRA for an object-detection dataset, E1), R00180 (SPIDER2 study, E-COMPARE).
- Codebook does not settle: R18677 is a CRC book chapter proposing cGAN oversampling (I3 names only journal/conference/preprint and there is no exclusion code for book chapters), so I marked it unsure. R05776 (MCGSA multiclass sample synthesis) and R03879 (security-level-guided SMOTE) look in scope but are in Chinese, so I excluded them as E-LANG. R18023 (erratum) is coded E-REVIEW and R01522 (delta-sigma ADC, off-topic) is coded E-NOGEN because no closer code exists.
- Unsure, same pattern: domain papers whose main contribution is an existing GAN used for minority augmentation (R20524 cWGAN-GP ECG, R18187 CycleGAN faults, R22343 DCGAN-IDS, R07539 CTGAN crashes); clarification 3 cases (R02797 Tomek+SMOTE, R13938 k-means SMOTE+IPF, R10222 BLSmote-ENN, R11048 ADASYN+GMM, R06624 ACGAN+K-means); federated client-side SMOTE (R10495, R19269); oversampling type not stated (R00606, R04158); I2 not stated (R10198 fair oversampling, R22242 DP-SMOTE).
- Front matter with an in-scope listed title: R07356 (BELIEF 2024 proceedings).

## batch020

batch 020: 200 of 200 records done; include 20, unsure 16, exclude 164
no records remain

Look at these first:
1. Gaps in the codebook: R00839 is a PhD dissertation that proposes the MeMO oversampler. I3 fails, but no exclusion code covers theses, so I marked it unsure. R00330 oversamples by moving real samples in from an auxiliary domain rather than generating them (unsure). R16695 is a generator for imbalanced regression, where clarification 1 and E2 conflict (I chose unsure). R07538 is a class-invariant augmenter not aimed at imbalance (unsure).
2. Unclear whether synthetic examples are generated (unsure): R16942 (Borderline Shifting, compared with SMOTE variants on 30 datasets) and R00136 (directed oversampling).
3. GAN, VAE or autoencoder generators used inside domain papers. These are hard to code consistently, so please check them as a set. Unsure: R02270, R07534, R15242, R16788. Excluded as E1 at medium confidence: R05172, R01620, R07805, R09239, R06057. Included at medium confidence: R13291 (claims novel post-processing), R04818, R10136, R21936, R01600 (zero-shot fault generation is borderline).
4. Clarification 3 (an existing generator plus a cleaning step): R03543 and R06018 are unsure because each claims its combination is new. R14644 (ADASYN plus Tomek, picked after a comparison) is excluded as E1 at medium confidence; check it against the other two.
5. Language: R00173 is included, but its venue (Jisuanji gongcheng) may be a Chinese-language journal, so I3 needs checking. R02302 (Chinese) and R15930 (Ukrainian) are E-LANG, but their methods are in scope and their abstracts are in English.
6. I2 not stated (Zenodo preprints with theory only, unsure): R21666, R21320, R21606.
7. Includes at medium confidence: R00412 (SMOTE inside Learn++.NSE; the paper's second method drops SMOTE), R02886 (titled as undersampling but uses graph-based RWO oversampling), R04095 (oversampler proposed inside a domain paper).
Conventions I used: a comparison of existing resamplers within one application domain is E1 with the tag comparison, and a general methodological comparison is E-COMPARE. Records whose language field is not English are E-LANG even when E1 also applies.

## batch021

batch 021: 200 of 200 records done; include 18, unsure 15, exclude 167
no records remain

Records to look at first:
- Low confidence: R18128 (BERT+GAN, GAN novelty unclear), R11965 (TabDDPM-SMOTE may only chain imputation and SMOTE), R17637 (no abstract, "graduated imbalance training"), R01695 (new "split by over-sampling" preprocessing, undescribed), R12730 and R01413 (excluded E1 from title or a vague abstract).
- Clarification 3 borderline (existing parts combined, sent to unsure): R15295 (Tomek-SMOTE-GA, 24 datasets, closest to include), R12738 (K-means SMOTE + centroid undersampling), R06476 (metaheuristic-tuned LSH-SMOTE), R07327 (successive four-step SMOTE).
- Includes resting on a short abstract (medium): R04096 (improved ADASYN, change not described), R21025 (CS-SMOTE inside a crash-severity model), R04002 (BMCD multiclass SMOTE), R04154 (Tomek-CASUWO), R10912 (semi-supervised elastic GAN), R06195 (GPT-3 style-based oversampling, shared-task paper). Also R12337 (excluded E1): check whether DPB-SMOTE is introduced in this paper.
- Codebook does not settle: R10952 (TransCTGAN balances gender subgroups, not classes), R21544 (interpolation oversampling for continual learning), R09642 (partial random over/undersampling for multilabel: are partial copies synthetic?), R00875 (SPY: abstract does not say whether it generates examples), R02652 (segmentation oversampling scheme, coded E-NOGEN).
- In-scope content excluded on E-LANG: R02379 (CMOTE), R02706 (SMB-SMOTE), R08079 (CD-BSMOTE), all Chinese; R00188 (Indonesian). Non-English records whose content is plain E1 were coded E1, the first criterion in list order, with the language noted in the reason; the codebook sets no precedence.
- E1 vs E-COMPARE: domain studies whose main aim is to compare existing resampling methods were coded E-COMPARE (tag comparison); R10244 was coded E1 with the comparison tag. R00560 (proceedings front matter) is tagged front-matter-in-scope for a listed paper on oversampling with bagging and boosting.

## batch022

batch 022: 200 of 200 records done; include 31, unsure 18, exclude 151
no records remain

Look at first:
- Low confidence: R12162 (exclude E1, no abstract; "data-efficient" federated CNN for blade icing might hide a new oversampler); unsure low: R14370, R00741, R20443, R18315, R19539, R07778, R05288, R03552, R11481, R10200.
- Existing generator used as the oversampler and presented as the contribution (not settled by the codebook): R02115 (vanilla GAN for fraud) coded include medium, but R05171 (SeqGAN) and R11481 (CTGAN) coded unsure. Please decide these three together.
- R00441 (Blagus & Lusa, SMOTE for high-dimensional data): theoretical/empirical analysis of SMOTE, excluded E-COMPARE (tag comparison); relevant to the survey's theory discussion.
- R18022: erratum to an in-scope article ("Imbalanced data oversampling through subspace optimization with Bayesian reinforcement", AI Review 2025); excluded E-REVIEW, tagged front-matter-in-scope. Check that the original article is in the corpus.
- New oversamplers for imbalanced regression excluded E2: R08230 (COVERT) and R21834 (SPECTRA). Clarification 1 (other purpose -> unsure) could be read to cover them.
- Non-synthetic oversampling methods excluded E-NOGEN: R06597 (ROS+RUS ensemble) and R00214 (bootstrapping ratio search).
- SMOTE + cleaning rule I applied: a named existing hybrid (SMOTE-ENN, SMOTE-Tomek) in a domain pipeline is E1 (e.g. R01065). SMOTE plus some other existing cleaning step presented as a new framework is unsure under clarification 3 (R03552).
- Other includes worth a check: R14638 (SMOTE hyperparameter tuning only, I1-other) and R13742 (diffusion/flow generator motivated by both fault scarcity and privacy). R17240 (Mirror-Space SMOTE) is unsure because I2 is not stated in the abstract.
- Code convention: I1-generative for learned deep generators; I1-other for other generators (R00724 ontology, R19796 DMD, R21824 DiCE counterfactuals) and for SMOTE tuning. Non-English applied papers are coded E1 with the language noted in the reason; E-LANG is used only for R02054 (Turkish), whose content was otherwise unclear.

## batch023

batch 023: 200 of 200 records done; include 19, unsure 20, exclude 161
no records remain

Look at first:
- Low confidence: R16781 (unsure; "conditional upgraded SMOTE" in a meme-embedding space), R19333 (unsure; rotation-transformed image SMOTE in an osteoporosis model), R07460 (unsure; "D-H-SMOTE Tree"), R01614 (exclude E1; LSH-SMOTE used as preprocessing in a GWO-BRNN framework, may be the authors' own variant).
- Borderline includes: R18269 (SMOTE applied in a contrastive IndoBERT latent space, presented as the contribution; could be read as E1), R09430 (space partitioning + SMOTE + bagging), R02167 (existing ANS-SMOTE inside a recursive stream ensemble), R19583 (SVM-weights SMOTE "SVWS" inside an IDS framework), R04182 (probability-based multiclass oversampling; may be replication rather than synthesis).
- Borderline excludes: R08821 (INNOS oversampler in transformer fault diagnosis, not presented as new), R00341 (oversampling + AdaBoost + GA reweighting), R02205 (SMOTE once before a DES pool), R02462 (EHSO: evolutionary undersampling + tuned random replication, deliberately no synthesis, E-NOGEN).
- Codebook does not settle domain papers that apply an existing generative oversampler: I excluded as E1 those that "adopt/employ/utilize" CGAN, CopulaGAN, CTGAN or DCGAN (R06364, R06048, R12626, R11698) but marked R11083 (VAE oversampling named in the proposed framework and title) unsure; please check this line is drawn consistently.
- E-LANG records that are otherwise in scope: R02805 (Korean abstract; GMM-based oversampler vs SMOTE/ADASYN; check whether the full text is English) and R00186 (Chinese; improved adaptive-neighbor SMOTE + NCL hybrid).
- Unsure by clarification 3 (existing generator + cleaning/selection or existing parts combined and called new): R06809, R07754, R20024, R02519, R05778, R07085, R00745, R06952. I2 not stated: R21470 (Causal SMOTE), R04411 (CIGAN package). Other purpose: R17976 (diffusion augmentation for under-represented subpopulations). In-scope titles without abstract: R22253 (WG-SMOTE), R16440.

## batch024

batch 024: 200 of 200 records done; include 25, unsure 24, exclude 151
no records remain

Look at these first:
- R02547 include (low): garbled, apparently paraphrased abstract claiming a kernel-space oversampler and a multiclass scheme; the record is typed Review (Journal of Critical Reviews). Check that it is a real method paper.
- Includes that depend on a judgment call (medium): R17253 (SMOTE-MRS in an anaemia paper; new or not?); R11233 (existing CWGAN-GP plus a new sample-screening index); R01361 (plain DCGAN proposed as an oversampler); R00447 (picks the target class ratio for SMOTE and other resamplers, coded I1-other); R17060 (SMOTE-ENC plus a new density filter; clarification 3 read as a new cleaning step); R08986 (imputation-based oversampling in data streams); R18528 (digital-twin generator in a federated IDS; Springer proceedings-series chapter); R02668 and R04150 (outlier or anomaly detection framed as supervised classification; E2 borderline).
- Low-confidence unsures: R01358, R19873, R00983, R15272, R07798, R18865, R02397, R13907, R02609, R00999, R04389, R02629, R05091.
- Not settled by the codebook:
  - Software paper R01046 (imbalanced-learn): coded E-REVIEW because no code fits better. The survey will probably cite it as software.
  - Key prior review R01478 (SMOTE 15-year anniversary, JAIR): E-REVIEW.
  - Book chapters (I3 does not name them): excluded on content (R11504, R05905, R09030, R08876, R10233, R18185); R02609 marked unsure; R18528 included.
  - New samplers that create no synthetic examples, coded E-NOGEN: R16898 (ALO), R18649 (balanced epoch sampler), R13491 (UDDA).
- E-LANG records that would otherwise qualify: R07285 (Chinese improved SMOTE) and R02402 (Chinese CWGAN-GP).
- Non-English papers that only apply SMOTE: coded E1, with the language noted in the reason.
- I2 not stated (clarification 2): R19899 (IB-SMOTE) and R21005 (Physics-field SMOTE). Both are Zenodo preprints with theory only.
- No abstract, in-scope title: R14280 (MMWO, SSRN).

## batch025

batch 025: 200 of 200 records done; include 28, unsure 10, exclude 162
no records remain

Look at first:
- Low-confidence excludes: R03524 (a "novel grid-oversampling" for IHC cell detection that the abstract never defines; coded E-NOGEN on the guess that it resamples real patches); R12205 ("an advanced version of SMOTE (ISMOTE) is used": may be the authors' own variant); four no-abstract domain titles coded E1 from the title alone: R02207, R14054, R18894 (title mentions "class imbalance handling"), R16159.
- Borderline includes (medium): R05784 (says "we propose a novel M-SMOTE" but does not describe it; the name matches the existing MSMOTE); R17684 (CHKDE-SMOTE, title only, no abstract); R04195 and R03251 (resampling inside a stacking ensemble / slow-start allocation; not stated whether the oversampling is synthetic); R02648 (Clustering-SMOTE "embedded into" random forest: inside the ensemble or just preprocessing?); R02081 (SMOTE applied in stages, a minimal change); R02538 and R09047 (graph oversamplers; the abstracts do not say how new nodes or graphs are made); R06220, R19722 and R18463 (generative oversamplers built from standard VAE, GAN and diffusion parts with a described generation design).
- Unsure (10): R10502, R05499, R01915, R15581, R01586 and R21368 (existing generator plus cleaning, selection or ensemble, or ISMOTE of unclear origin; clarification 3); R13519 (GPT-4 generates synthetic minority samples in a domain paper); R20211 and R16703 (no abstract; both titles could go either way); R09450 (U-other: LLM self-improvement that rebalances generated solutions; not classification).
- Cases the codebook does not settle: (a) E1 vs E-COMPARE for comparisons of resampling within one domain. I used E-COMPARE when the stated aim was the comparison and E1 with the comparison tag when the comparison sat inside a domain model. This was applied unevenly; all of these are excluded either way. (b) Existing generators used unchanged in domain pipelines (CTGAN in R19537, medGAN in R06137, SMOTE-GAN in R16869) were coded E1 (medium). (c) R22093 is excluded E-LANG (Chinese) but would otherwise meet I1 (adaptive SMOTE-ENN). (d) R19005 is a book chapter; there is no exclusion code for document type, so I coded E1. (e) R10387 is coded E-COMPARE with the required comparison tag, although SMOTE is only mentioned as future work.

## batch026

batch 026: 200 of 200 records done; include 33, unsure 13, exclude 154

Look at first:
- Low-confidence unsure (abstract does not show whether the resampling is new or synthetic): R05921, R05220, R00171, R01191, R08334, R12487, R11146.
- Other unsure: R18035 (CP-SMOTE, I2 not stated), R22053 (TME, only "visualization performance" evaluated, purpose unclear), R00778 (SMOTE + feature ranker framework), R05685 (GAN balancing, novelty unclear), R16804 (SMOTEImputeScaler), R12625 (existing BEGAN applied in IDS; leans E1, compare R18834, existing CTGAN, coded E1).
- Borderline includes (medium): R05296 (SVD-CLAHE image-transform augmentation counted as oversampling), R20132 and R22281 (domain papers whose contribution is a VAE/GAN minority generator), R12092 (counterfactual augmentation module), R16332 (DI-SDG perturbation generator), R19433 (main contribution is the Ghost Rate diagnostic; ContraSMOTE is exploratory), R09319 (new oversampler named but not described), R04908 (KNNOR software paper, possibly an earlier version elsewhere), R07381 (CSSF under a "comparative analysis" title), R05653 (D-SMOTE framed as anomaly detection but evaluated as supervised CNN classification), R08607 (TriEnhance, generator not specified).
- Language check: R00340 is labeled English but is from Jisuanji kexue yu tansuo, the journal of R02477, which is labeled Chinese.
- Codebook gaps: R03240 and R15279 propose new classifiers trained on unchanged SMOTE or oversampled data (coded E1 although not domain papers); R19323 (cluster centroids + SMOTE "CCSM" inside a domain model) coded E1 but is close to clarification 3, like R11146 which was coded unsure.
- In scope on method but excluded for language only (E-LANG): R02477, R07589, R01607, R14347.

## batch027

batch 027: 200 of 200 records done; include 24, unsure 22, exclude 154
no records remain

Check first:
- Codebook does not settle E2 vs clarification 1. These new generators target a task other than classification, so I coded them U-other, not E2: R05837 (anomaly detection), R02928 (FCM-SMOTE for load clustering), R19617 and R01989 (imbalanced regression). R01249 (survival forest, low) is a similar task-scope doubt.
- I3 document type: R08563 proposes an improved ADASYN but is a chapter in an edited book. There is no exclusion code for document type at this stage, so it is unsure.
- Low confidence: R07066 (raking/sampling resampler for one-class classification; unclear whether it makes synthetic examples) and R01249.
- Borderline includes (medium): R05930 (CCR + GSVM-RU, close to clarification 3), R19280 (LLM-guided GAN inside an IDS framework), R15604 (TarDiff; aims at both scarcity and imbalance), R12638 (oversampling CutMix/Mixup for tail classes), R14314 (CGAN in ISOMAP space), R02445 (graph oversampling), R06871 (saliency oversampling), R06352 (adaptive-k SMOTE in a domain paper).
- Borderline excludes (medium): R04704 and R04355 (existing GANs applied in a domain), R01603 (local vs global SMOTE for big data, framed as analysis), R22030 (no abstract; "SMOTE paradox" meta-research), R19896 ("adapted" SMOTE), R11492 and R02999 (cluster + SMOTE pipelines).
- In-scope methods excluded only for language (Chinese full text, English abstract): R10921 (boundary-adaptive SMOTE) and R06869 (GAN oversampler).
- Front matter tagged front-matter-in-scope: R19986 (lists "MC-SMOTE" for software fault prediction).

## batch028

batch 028: 200 of 200 records done; include 28, unsure 16, exclude 156
no records remain

Look at first:
- Low confidence: R18539 (unsure; "structure-preserving graph oversampler" inside a paratope framework, novelty not stated), R18745 (unsure; undescribed "two-tier oversampling strategy" for MBTI text).
- Scope the codebook does not settle: R07164 SMOTE-CD (included, medium; compositional data, evaluated with regressors but reports class imbalance, accuracy and F1; E2 if not counted as classification); R04144 (unsure; multi-label oversampling for segmentation, unclear whether it synthesizes or replicates); R20214 (unsure; long-tailed point-cloud dataset distillation, purpose is compression); R21919 (unsure; single-cell generator for scarcity, imbalance and privacy, judged on fidelity); R17454 (unsure; boundary oversampling for fault localization, a ranking task).
- I2 not stated in the abstract: R17107 SDC-SMOTE, R17113 MI-SMOTE, R21923 FN-SMOTE (three 2026 Zenodo preprints with the same template; check for experiments and for a common source).
- Clarification 3 unsures (existing generator plus an existing step): R07332, R02543, R03403, R05693, R14796, R12859.
- Medium-confidence includes that lean on generators applied to one domain or on hybrids: R03056, R01826, R04404, R11070, R01502, R10021, R07549, R04983, R21622.
- Medium-confidence excludes a second coder may flip to unsure: R15277, R22136, R19140, R15048, R13948 (generators or hybrids used inside domain pipelines), R09970 (tool that compares existing generators).
- E-LANG decided from the language field only (English abstracts present): R16656, R03869, R00111, R00147, R21433, R13705, R21937.

## batch029

batch 029: 200 of 200 records done; include 29, unsure 7, exclude 164
no records remain

Records to look at first:
- The codebook does not settle these. R02080: extends SMOTE to imbalanced regression (function approximation). Excluded as E2, but clarification 1 (SMOTE extensions built for another purpose) could make it unsure. R15611: the abstract is in Korean although the metadata says English. Excluded as E-LANG. If the full text is in English, it adapts T-SMOTE with zero-padding for short series and could be included.
- Low confidence. R05057 (unsure): a HAR paper's "oversampling technique-based data augmentation algorithm" may be new or existing. R04299 (unsure): a grouped binary-decomposition IDS; SMOTE appears only in the keywords, so it may be a multiclass oversampling scheme. R16253 (unsure, no abstract): a physics-informed conditional tabular GAN for building energy; the task is unclear.
- Borderline includes (medium). R00775: CWOS-Ord treats ordinal regression as ordered multiclass, so E2 could be argued. R00348: SVBO may replicate support vectors rather than synthesize new ones. R00994: an imputation-based oversampler whose evaluation is only implied. R17523: an "Enhanced SMOTE-RUS" scheme inside a smart-grid paper. R13305: GAN-SMOTE integration. R19361: semantic oversampling for NER. R04941: MIL bag simulation. R05770: SMOTE plus weighted SLFN. R10486: VAST-KD-SMOTE inside an IDS.
- Borderline excludes (medium). R16676: ADASYN "incorporated into the model" is listed as a contribution. R19278: a per-client SMOTE ablation in federated learning. R05001: "optimized SMOTE", read as tuned rather than changed. R22052: a named ROS+NCL combination in a domain paper. R08491: pairings of 14 SMOTE variants with boosting, called "new methods".
- Unsure records going to full text (medium): R18346 (whether FSDR-SMOTE is the authors' own), R00352 (IFSMOTE), R06295 (SMOTE then PSO sampling, clarification 3), R17455 (no abstract; counterfactual-SMOTE hybrid for crop growth).

## batch030

batch 030: 200 of 200 records done; include 27, unsure 20, exclude 153

Records to look at first:
- Low confidence (all unsure): R03609, R11516, R05552 (no abstract, titles could go either way); R02497 (SMOTE-bootstrapping in a water quality study); R04628 (Caps-Triple GAN, unclear whether it generates minority data); R20244 (title says fake news but abstract is loan default; synthetic-borrower simulator plus standard SMOTE/ADASYN).
- Borderline includes (medium): R02612 (GAN with contrastive/triplet auxiliary loss; title reads like a limitations study); R13304 (VAE/AE/GAN/AE-GAN oversamplers, may be mostly a comparison); R02615 (existing SeqGAN used as oversampler for supervised log anomaly detection); R05847 (KM-SMOTE, title says "Application" and resembles K-means SMOTE); R00849 (SMOTE improvement, evaluation only "tested"); R04679 (GA search of per-class SMOTE ratios, could be read as tuning); R18943 (ensemble of GAN, SMOTE and ADASYN); R00821 (SMOTE inside rotation forest); R06080 (CutMix-style minority synthesis).
- Borderline excludes (medium): R14328 (SMOTE+Tomek+stacking called "the proposed method"; clarification 3 may apply); R18016 (off-the-shelf GAN augmentation in a bankruptcy pipeline); R06217 (SMOTE+CNN on KEEL); R10043 (critique of SMOTE that proposes an evaluation method, useful for the evaluation section); R19419 (GA-tuned ratio for random oversampling).
- Codebook does not settle: oversamplers whose abstract never says whether examples are synthetic (R01028, R00529, R05572, R09321, all unsure U-other); off-the-shelf generators applied in domain papers (R02615 included, R18016 excluded); Mixup-type synthesis (R06080).
- Also: R02768 (E-LANG, Chinese) describes an ELM-guided SMOTE hybrid that would otherwise look in scope; R01520 is proceedings front matter tagged front-matter-in-scope (local vs global SMOTE for big data).

## batch031

batch 031: 200 of 200 records done; include 24, unsure 18, exclude 158
no records remain

Check first:
- The codebook does not settle these: R04756 is a book chapter that otherwise meets I1 and I2 (conditional WGAN-GP), but I3 does not list book chapters and no exclusion code covers them, so it is unsure. R09023 is an AutoML tool, and the codebook does not say whether automated choice or configuration of existing resamplers counts (unsure). R01762 (DCIA) generates prototypes for every class in multiclass imbalanced data, so it is unclear whether it counts as oversampling (unsure). R06552 uses generative subtype balancing for segmentation, not classification (unsure under clarification 1). R01933 is a PhD thesis, excluded as E1.
- Low confidence: R12381 (diffusion oversampling on Zenodo; reads partly as a review, I2 vague), R04221 (ADASYN adapted to multi-label), R09553 (theory only, no data), R09524 (Tomek+SMOTE+WGAN in an IDS). R08042 and R11096 have no abstract and were excluded from the title only.
- Borderline includes: R00191 (new cluster-based undersampling with unchanged SMOTE, coded I1-hybrid by analogy with "SMOTE with a new cleaning step"), R03740 (existing WGAN, but the generation is the paper's contribution), R05763 (I2 only implied), R19789 (Kmeans-SVMSMOTE-ENN, at the boundary of clarification 3), R01526, R12833.
- Borderline excludes: R14846, R19403 and R20532 (existing GAN or CTGAN used as a step in a domain pipeline, E1). R13009 (existing EBGAN evaluated). R10924 and R15319 (SMOTE described as "class-preserving" or "tailored" with no change shown). R00459, R01162 and R03294 (E-NOGEN; the resampling looks random or bootstrap-only, and R03294 lists SMOTE among its keywords).
- Unsure because I cannot tell new from applied: R03625, R18988, R06579, R19369, R00208, R18558, R01986, R11000. R19671 meets I1, but I2 is not stated. R12565 is a general-purpose generator.
- Notes for the full-text stage: R05307 may be an extended version of GraphSMOTE (E4). R19732's metadata says English, but its venue (CIMS) often publishes in Chinese.

## batch032

batch 032: 200 of 200 records done; include 30, unsure 15, exclude 155
no records remain

Look at first:
1. Off-the-shelf generator applied in a domain paper; the codebook does not say whether this is E1. Coded E1 when a named existing model is used: R11832 (rec 14, "so-called GANs", code smells; closest call, could be unsure), R03984 (DCGAN, SAR ships), R19386 (CT-GAN), R16442 (existing kNN mega-trend diffusion with grid search), R20218 (Stable Diffusion + LoRA, object detection rather than classification). Coded unsure when a "VAE-based method" or "CVAE framework" is the stated contribution: R07631, R21576.
2. Includes based on inference or thin abstracts (all medium confidence): R00605 (MultiBoost; SMOTE appears only in keywords, oversampling inferred from "expanding the concept space"), R00804 (EMOTE; how it generates is unclear), R00092 (polynomial-fitting oversampling; results mentioned but no datasets named), R07518 (association rule + GAN hybrid), R01015 (SMOTE + new swarm-guided undersampling; generation unchanged), R09287 (SMOTE-GAN-VAE).
3. Clarification 3 edge cases. Unsure: R10264 (SMOTE+GMM+ENN), R03950 (SMOTE+ENN), R17139 (SMOTE+Tomek), R11642 (Bi-SMOTE). New selection step + SMOTE: R00925 (active learning) and R00903 (hierarchical multi-label negative selection) unsure, R01015 included.
4. Other unsure: R03732 and R01563 (oversampling proposed, but not clear whether it synthesizes or replicates), R22331 (SMOTE for EV station planning, clarification 1), R20219 and R03356 (I2 not stated), R21817 (COSTE applied or new?), R20608 (SMOTE per temporal subgraph).
5. Medium-confidence excludes: R09411 (SMOTE-ENN in a VAE latent space), R04722 (Honeybee-SMOTE feature selection), R20177 (grid-searched SMOTE), R12043, R00934 and R04301 (E-NOGEN).
6. Notes: R13597 is Chinese-language (E-LANG) but proposes an in-scope VAE generator. R21321 has an Indonesian title although its metadata says en. R03999 repeats R02191's abstract. No-abstract records excluded from the title as E1 (medium): R13476, R13783, R08359, R08268, R10259.

## batch033

batch 033: 200 of 200 records done; include 15, unsure 16, exclude 169
no records remain

Look at these first (record number in batch order, rec id):
- Low confidence: 21 R11272 (GAN-LSTM makes synthetic attack samples, but it is framed as anomaly detection), 61 R18599 (SMOTE-DBC inside a diabetes framework; is the variant new?), 66 R05748 ("designed" RandomSample-SMOTE for intrusion detection), 126 R00514 (EN-CS-HN-SMOTE; is SMOTE applied inside the ensemble?).
- Possibly inconsistent calls: 56 R10673 SMOTE-NRSEL is excluded E1 (medium), but 126 R00514 has the same pattern and is marked unsure. 108 R18881 is included I1-hybrid (SMOTE-ENN run in a decision-tree-leaf feature space), but 134 R02955 (PCA+MWMOTE) is unsure and 127 R04948 (PCA-SMOTE, domain paper) is excluded E1. Clarification 3 does not cover a feature transform placed before an existing generator.
- Medium-confidence includes whose abstract does not describe the generation step: 31 R01332 (arXiv "novel minority over sampling technique"), 96 R07122 SCALA and 154 R05032 IDBMORate (multiclass allocation schemes), 105 R03762 (SA-PSO tuning of SMOTE N and k; is this a method or just tuning?), 64 R18026 (diffusion integration and partial-balancing policy), 71 R06821 (conditional GAN capsule network).
- U-other, built for another purpose: 9 R07337 (zero-shot learning GAN), 55 R12102 (diffusion model for detection and segmentation), 72 R07819 (SMA for covariate bias and fairness), 176 R20525 (EFD-SMOTE; I2 is not stated, only theoretical analyses are cited).
- Not in English but possibly in scope: 59 R10870 (Chinese; SMOTE applied to Deep Forest output probabilities) and 146 R04490 (Chinese; keywords name "adaptive comprehensive oversampling"). Language metadata disagrees with the text: 33 R14721, 139 R14236, 150 R00783.
- Front matter tagged front-matter-in-scope: 116 R15064 (clustering-based oversampling for mixed data) and 147 R05148 (LIDTA 2022, adversarial oversampling for multi-class data).

## batch034

batch 034: 200 of 200 records done; include 27, unsure 23, exclude 150

Look at first:
- Low confidence: R20579 (include I1-other: minority-stage time-frequency augmentation module inside a sleep-staging network; is a domain augmentation module in scope?), R02041 (SMOTE applied to images as a "novel scheme", only SMOTE vs no SMOTE tested), R03101 (title says hybrid, abstract describes only simulated-annealing undersampling, keywords list oversampling), R08269 ("novel two-phase resampling" inside a comparative churn study), R22104 (part tutorial; transformer+VAE generator of minority data), R07300 (anomaly-model data generation for energy theft), R19505 (SMOTE plus class-specific autoencoder reconstructions), R10501 (no abstract).
- Regression is not settled by the codebook: new SMOTE extensions or generators for regression were sent to unsure under clarification 1 (R10295 WSMOTER; R10318 improved CTGAN for trajectory prediction), while R08677 (existing SMOGN with TPE tuning) was excluded E2. Please confirm whether clarification 1 or E2 governs.
- Clarification 2 (I2 not stated): three similar 2026 Zenodo preprints with theory-only abstracts: R16056 Ca-SMOTE, R17249 FRS-SMOTE, R21661 Self-organizing SMOTE.
- SMOTE plus a new undersampling or cleaning step included as I1-hybrid by analogy with "SMOTE with a new cleaning step": R01178 (SOS-BUS; the novelty is the undersampling), R19191 (SMOTE plus novel trimming in a skin-lesion framework). R02267 (SGM: SMOTE plus GMM undersampling) and R20624 (DiToS: Stable Diffusion, Tomek links, SMOTE) left unsure under clarification 3.
- Medium-confidence includes where the oversampling novelty is thinly described: R04289 (GSDC), R12193 (modified SMOTE-ENC), R02541 ("improved" sampling inside an ensemble), R09793 (GAN with new GFE loss), R05755, R16485, R01491.
- E-LANG records that would otherwise meet I1 (English versions may exist): R00278 (PCBoost), R00166 (clustering ensembles with improved SMOTE), R15786 (GraphSMOTE extension).
- Front matter in scope: R22377 (ICPR 2026 workshops; lists "Enhancing Foundation Models for Imbalanced SAR Ship Classification via Targeted Oversampling").
- No abstract, unsure: R04835, R01827, R18210, R10501.

## batch035

batch 035: 200 of 200 records done; include 27, unsure 13, exclude 160
no records remain

Look at first:
- Low confidence: R02637 (include I1-generative: ModGraProDep graphical-model synthetic data for small imbalanced subsets, also does imputation; downstream may be survival analysis rather than classification); R16220 (unsure, no abstract: "GAN-augmented gradient boosting ... continuous prediction under severe class imbalance", may be regression); R17584 and R20783 (excluded E1 with no abstract; titles show a biomarker tool and an IDS classifier paper, nothing suggests a new oversampler).
- Where a generator is used in a domain pipeline: R03299 included (VAE crash-data augmentation presented as the technique, compared with SMOTE/ADASYN/GAN). Excluded E1 at medium confidence because an existing generator is only "employed" or "adapted": R07813 (VAE), R09426 (WGAN-GP), R11256, R04746, R18594, R09803 (GAN), R19413 (CTGAN). Please check that line.
- Clarification 3 (existing generator + existing cleaning, presented as new) sent to unsure: R09206 (ADASYN+RENN), R04226 (ADASYN-LOF), R07317 (USMOTE = RUS+SMOTE). Similar unsure: R01073 (rough set + max-distance SMOTE), R05128 (SMOTE + proposed EnSVM majority selection), R04774 (HBSBoost hybrid sampling + boosting).
- Included because the cleaning step or module seemed new (medium confidence where unclear): R07222 SMOTE-CDNN, R15462 SMOTE-OSBNR, R02829 SMOTEMultiBoost (abstract does not say SMOTE runs inside boosting; compare R02574, excluded E1), R13251 FRF-ACS (functional SMOTE within the forest's bootstrapping).
- Other-generator includes to confirm: R09451 (mixup-style head/tail blending for long-tailed images), R08636 (Gaussian-noise perturbation oversampling), R21839 (embedding oversampling module in a graph fraud model), R07523 (MPMU, abstract does not say whether the minority upsampling is synthetic).
- Exclusions the codebook does not settle: R01428 E2 (one-class anomaly detection with sub-concept oversampling); R12139 E2 (CTABGAN for process parameter prediction, assumed to be regression). R15183 (VAE-GAN+SMOTE) and R05887 (1D GAN) are E-LANG (Chinese) but otherwise near scope.
- How I split E-COMPARE from E1: E-COMPARE (tagged comparison) only when resampling methods, or results with and without resampling, are among the things compared. Classifier comparisons with a fixed SMOTE step were coded E1.

## batch036

batch 036: 200 of 200 records done; include 25, unsure 16, exclude 159

Look at first:
- Low confidence (all unsure): R11231 ("improved SMOTE", unclear whose), R15081 (unspecified "imbalance-aware" DL method, may be loss-based only), R08131 (BLSMOTE + K-means presented as new algorithm), R01037 (SMOTE + OSS hybrid in a student-performance study).
- Codebook does not settle: R00234 is a dissertation that would meet I1 and I2, but fails I3 and no exclusion code covers theses (marked unsure U-other).
- Generative borderline (existing generator inside a domain method?): included R01810 (SeqGAN, text), R08354 (DDGAN), R19439 (Gaussian-multinomial DDPM), R02704 (GAN, bitcoin), all medium; marked unsure R18095 and R13288 (GAN as side component), R06626 (SMOTE-ENN + WGAN), R10249 (CTGAN with bound relaxing and silhouette filtering); excluded R11615 and R15424 (CTGAN applied, E1).
- I2 not stated in the abstract (clarification 2): R19452 (Graph Diffusion SMOTE), R16492 (PBE-SMOTE). Weak I2 but included: R07625 ("numerical experiments" only), R00927 (vague sampling details).
- Purpose other than imbalanced classification (clarification 1): R21791 (SMOTE for sufficient dimension reduction).
- Language: R15727 excluded E-LANG (Chinese) but its content is an in-scope GAN generator. R07883 and R11366 (Indonesian titles, English abstracts) and R18612 (language tr, English abstract) were coded E1, not E-LANG.
- Excluded on title alone (no abstract, medium): R17563, R12580, R09915, R14366, R09899, R12837, R21224.

## batch037

batch 037: 200 of 200 records done; include 33, unsure 11, exclude 156
no records remain

Look at these first:
- Low confidence, no abstract (decided from the title alone): R16705, R19552, R17387 (E1); R19409 (E-COMPARE, GANs vs diffusion models for knee radiographs).
- Unsure (11): R16808 (no abstract, GAN-augmented boosting); R08908, R03169, R11250, R05380, R01102, R03718 (cannot tell whether the resampling is new or applied); R06558, R17076 (existing ADASYN plus Tomek/ENN presented as new, clarification 3); R00374, R04620 (oversampling type or rate method unclear).
- Codebook does not settle off-the-shelf generators used as the oversampler in domain papers. My rule: a named existing generator used unchanged = E1 (R15695 CTGAN); a generator design presented as the contribution = include (R04097, R06210, R13510 medium); in between = unsure (R08908). R13119 (GAN on BERT embeddings) was included at medium confidence although minority targeting is not stated.
- Abstract does not say whether the oversampling is synthetic: R00374 (unsure), R02408 and R14467 (include, medium). These three should be decided together.
- Other borderline includes: R06420 (role of the deep GMM unclear), R19311 (multi-label graph oversampler inside a GNN paper), R06523 (noise-removal module, novelty of the cleaning step), R12106 (evaluation stated only in general terms), R00403 (thin abstract).
- R01672: excluded as E-LANG (Chinese), but the method (SVM_HS, iterative SMOTE near the SVM hyperplane) would otherwise meet I1.
- R10688: E1 at medium confidence; it presents SMOTE-ENN inside cross-validation folds as a novel approach.
- R12100: E-NOGEN at medium confidence; it oversamples the minority with real examples from related datasets, a case the codebook does not cover.
- R06943: the title (power grid control) does not match the abstract (cost-sensitive neural networks); likely a metadata error. Excluded on both.
- R20764: the language field is Indonesian but the abstract is English; coded E1 on content.

## batch038

batch 038: 200 of 200 records done; include 26, unsure 11, exclude 163
no records remain

Records to look at first
- Low confidence: R10138 (rec 92, unsure U-other): entropy-based over-, under- and hybrid sampling for a product-expiry app. No evaluation is named, and the abstract does not say whether synthetic examples are generated.
- Close calls among the includes:
  - R08507 (rec 99, SMOTENN, I1-hybrid): SMOTE plus "intelligent undersampling" in one MapReduce pass. Under clarification 3 it could be unsure.
  - R00484 (rec 20, BBO, I1-multiclass): binarization with boosting and oversampling. It is unclear whether the oversampling itself is new.
  - R08682 (rec 51, GAN on BERT embeddings for spam), R01446 (rec 130, text-GAN URLs) and R11191 (rec 94, Deep-CTGAN with target handling): I1-generative, medium confidence. These are domain papers whose GAN may be a standard model.
- GAN cases the codebook does not settle. I used one line:
  - Paper says it proposes the GAN oversampling: include or unsure. R08342 (rec 74) is unsure.
  - Paper only uses an existing GAN: E1. This covers R08336 (rec 17, CWGAN-GP), R03324 (rec 141, DCGAN) and R16419 (rec 71, CTGAN).
  Please confirm that line.
- Close calls among the excludes:
  - R00107 (rec 6, E-COMPARE): complexity-based rules for when to apply oversampling.
  - R02818 (rec 7, E-NOGEN): noise-robust boosting that is only paired with oversampling in experiments.
  - R09862 (rec 134, E1): RCSMOTE is named in the title of the proposed method but is only "used" in the abstract.
  - R06950 (rec 104, E1): CU-SMOTE may or may not be the authors' own.
  - R14343 (rec 5, E2): audio source separation.
  - R09704 (rec 49, E-NOGEN): sliding-window image representation.
- Unsure under clarification 3 (existing generator plus existing step): R05252 (SMOTE-LOF), R06556 (SMOTE-RBU), R17676 (hybrid SMOTE/Tomek/ADASYN), R18919 (SMOTE-Tomek inside bagging).
- Codebook gaps:
  - Indonesian titles with English abstracts and language field "en" were coded on content (E1): R01671, R09070, R13925, R05800. R08377 has language field "ar" and an English abstract; also coded E1.
  - R09813 is a thesis and R04947 is retracted; both excluded on content.
  - Off-topic records R15877 and R03461 were coded E-NOGEN because no code fits exactly.
  - R01160 (front matter) is tagged front-matter-in-scope for a listed paper that is a comparison.

## batch039

batch 039: 200 of 200 records done; include 21, unsure 19, exclude 160
no records remain

Look at first:
- Low-confidence unsure: R00871 (SMOTE-DGC: SMOTE paired with a classifier in a method paper, 44 datasets; codebook does not settle this), R00309 (SVM "exciting support vectors"; synthetic or not?), R01366 (online multiclass oversampling bagging; synthetic or copies?), R00222 (coevolution condensed-set resampling with an oversampling version), R04065 (CBCM bone-marrow images; method not described), R14580 (MADASYN in an IDS paper; new or existing?), R01302 (no abstract, multi-minority medical).
- Cases the codebook does not settle: R06411 (GOLIATH, a kernel-density generalization of SMOTE usable for classification but evaluated on regression only); R00098 (selective local oversampling plus majority filtering; copies or synthetic?); R08068 (generative balancing of protected groups for fairness) and R05680 (adSMOTE as general audio augmentation), both U-other under clarification 1; R16068 (CCI-SMOTE, no evaluation in abstract, clarification 2).
- Borderline includes (medium): R06797 (MLH) and R12801 (MetaBoost) combine existing oversamplers in layers or by weighted averaging (I1-hybrid, at the edge of clarification 3); R00519 (pattern-guided oversampling in a bootstrap ensemble; copies or synthetic?); R11538 (CFA-SMOTE; check classification vs regression); R06301 (KD-SMOTE inside a domain paper); R07692, R06028 and R18295 (generators described briefly). R14590 (genetic algorithm) and R11164 (cellular automata) are coded I1-generative as "other generators".
- Borderline excludes (medium): R17124 and R05650 apply existing WGAN-GP (E1), compared with R14656 and R15870 (unsure; the generator may be new). Also R10226 (Fuzzy C-Means SMOTE used without a novelty claim), R01126 (SMOTE-LSSVM; compare R00871), R02502, R07753 and R01637 (existing oversampling inside a pipeline), R20715 (label propagation, E-NOGEN), R00245 (duplication, E-NOGEN) and R21915 (no abstract; title names a ViT architecture).
- E-LANG (Chinese) with in-scope content: R02039 (improved SMOTE), R15572 (parabola-constrained oversampler), R11578 (improved ADASYN), R09943 (hash-optimized Borderline-SMOTE+Tomek).

## batch040

batch 040: 200 of 200 records done; include 27, unsure 14, exclude 159
no records remain

Look at first:
- Low confidence: R04707 (no abstract; collaborative-filtering fault diagnosis, book chapter), R18767 (no abstract; undefined CASE/C-BAFT image techniques), R08323 (title claims BCPA-based data balancing, abstract lists GAN + SMOTE), R04797 (customized mini-batch oversampling, may be replication only).
- Existing generator presented as the oversampling contribution, coded differently: R01973 include (SeqGAN generates minority log text) vs R04495 unsure (CTTGAN, abstract says it uses CTGAN as is) and R04664 unsure (cGAN, framed as an evaluation). Please harmonise.
- Borderline includes: R19720 (SMOTE-guided CGAN, two existing generators combined), R16678 (AceNet, feature-level SMOTE for classifier refinement), R04566 (clustered SMOTE for discrete features inside a domain paper).
- Borderline excludes: R16453 ("Improved SMOTE is employed", unspecified), R03114 (SMOTE + CNN ensemble, unclear if per member), R17625 and R21512 (SMOTE on embeddings, not presented as new), R22018 (covariate-shift theory; only a keyword mentions oversampling), R14234 (title says Generative AI, abstract shows only class-aware oversampling).
- Codebook gap: feature selection + existing resampling presented as a proposed method (R00434, R01172, R09041) coded E1; I read clarification 3 as covering sample cleaning or selection, not feature selection.
- Codebook gap: E-LANG records with English abstracts that propose oversamplers: R07339 (Thai, HIDPO improved random oversampling), R03484 (Chinese, MOLAD oversampling); also R08303 (Turkish, SMOTE vs GPT-generated data).
- Clarifications applied: R17023 EC-SMOTE (U-other, I2 not stated; strong candidate if the full text has experiments), R16625 and R21578 (U-other; generators for data scarcity and for causal inference), R01346 (front matter, tagged front-matter-in-scope for an improved random forest for imbalanced lung nodules), R05239 (hybrid sampling for defect-number regression, E2).
- Coding conventions: domain studies whose stated aim is the effect of resampling (R09060, R17326, R07236, R10133, R05111) coded E-COMPARE with tag comparison, other domain pipelines E1; book chapters R04707 and R16475 have no document-type exclusion code at this stage.

## batch041

batch 041: 200 of 200 records done; include 20, unsure 19, exclude 161
no records remain

Look at first:
- Low confidence: R18972 (no abstract; title "Evaluating Diffusion-Based Synthetic Data Augmentation for Driver Inattention Detection", could be an application or a new generator).
- E-LANG exclusions whose method looks in scope (language taken from metadata and non-English title; codebook does not say whether to seek an English version): R22205 (Spanish, Ledoit-Wolf Gaussian minority generator, emotion detection), R09844 (Chinese, prospect-theory oversampling POS), R03242 (Chinese, C4.5-guided iterative hybrid sampling ensemble).
- Borderline includes under clarification 3: R14643 (parallel/serial ensembles of existing oversamplers with selection near minority centers), R13364 (NR-Clustering SMOTE, close to K-means SMOTE), R04121 (HABC, density-based oversampling inside bagging; not clear the oversampling is synthetic).
- Clarification 2 (I2 not stated): R00175 (hierarchical SMOTE, multi-label), R00703 (distance-threshold SMOTE), R21979 (TCR-SMOTE, trajectories), R18471 (Dr-SMOTE, diffusion). Clarification 1 (other purpose): R19838 (limited-data GAN), R05715 (structured-data GAN, privacy and augmentation), R15345 (zero-shot feature generation).
- Borderline excludes: R01199 (dynamic selection combined with SMOTE-type preprocessing, coded E-COMPARE but could be read as an ensemble hybrid), R12838 (LLM-generated minority samples used as a step), R10652 ("dynamic sampling" with SMOTE plus RUS in a DL intrusion model).
- Domain papers naming a sampler whose novelty is unclear (U-new-or-applied): R20737 (SSOT, resembles SVM-SMOTE), R11313 (LCGBO), R05358 (TBSSVM), R07072 (BSGM), R16271 (SMOTE-GAN hybrids), R08362 (GAN oversampling on KEEL), R10977 (GAN for PV images), R02278 (unnamed oversampler), R10165 (undescribed two-sided sampler).
- No-abstract unsure with in-scope titles: R16381 (potential-field oversampling), R19425 (GeoBorrow-SMOTE).
- Front matter: R22292 (IUKM 2026 proceedings) lists "A Hybrid PSO-SMOTE Approach for Enhancing AFW-CIL in Imbalanced Data Classification" (tagged front-matter-in-scope).

## batch042

batch 042: 200 of 200 records done; include 25, unsure 20, exclude 155

Records to look at first:
- Low confidence (all unsure): R05509 (MASI relabels majority samples as minority; does relabelling count as generation?), R17593 (multi-discriminator GAN for zero-day detection; the generator may not act as an oversampler), R10126 (SMOTE on CNN features, then a cost-sensitive GAN classifier), R11522 (SMOTE-ENC in an "enhanced" imbalance step), R13180 (PCA before SMOTE presented as an improved SMOTE).
- Existing generator applied, or new? Excluded as E1: R05218 (CTGAN) and R03912 (vanilla/conditional GAN). Marked unsure: R02455 (CycleGAN with purpose-designed G/D) and R18530 (dual-purpose CVAE). Check that the same line is drawn in other batches.
- Included at medium confidence, but the abstract does not say whether examples are synthesized or replicated: R03052 (criteria-based seed selection) and R00323 (oversampling guided by fault counts). By contrast, R20732 (stream ensemble with random over/undersampling) was excluded as E-NOGEN.
- Included at medium confidence from domain papers with a named, modified resampler: R19441 (optimizer-chosen SMOTE neighbours), R02426 (fuzzy oversampling), R11474 (attention-modified GAMO), R04403 (information-weighted synthesis plus ENN).
- Cases the codebook does not settle: R00949 (GA tuning of an existing SMOTE hybrid, coded I1-other), R08722 (Ensemble-SMOTE merging SMOTE-variant outputs, coded I1-other), R10077 (Spatial-SMOTE framed for regression but scored with classifiers and F-score), R00231 (oversampling inside a boosting-style ensemble, not for imbalance).
- Generators whose purpose or evaluation is not imbalanced classification (clarification 1): R17981 and R22396 (WGAN-GP evaluated through anomaly detectors), R11542 (diffusion augmentation for perception), R03286 (GZSL feature generation). Latent-space resampling, new or applied: R05675 (BiVAE), R17423 (GATv2 + Graph-SMOTE).
- Clarification 2 (I2 not stated): R21474 Spectral SMOTE and R18087 Cross-class SMOTE (Zenodo preprints, theory only). Clarification 3: R13516 D-ENN and R00829 SMOTE+undersampling. No abstract: R00061 (title suggests a distance-based oversampler).
- Excluded as E-LANG although the methods are in scope: R05709 (adaptive kernel SMOTE-SVM) and R17789 (K-means improved SMOTE), both in Chinese. R14748 is listed as Turkish but has an English abstract; it was excluded as E-COMPARE regardless.

## batch043

batch 043: 200 of 200 records done; include 23, unsure 22, exclude 155
no records remain

Look at first:
- Low-confidence unsure: R06847 (SMOTE-SVM + GWO, lung disease; is the resampling new?), R16375 (no abstract, crash severity), R01658 (CD2A drift method for imbalanced streams; imbalance handling not described), R10186 (node oversampling on forum graphs; new or existing?), R07854 (SMOTE + silhouette cleaning inside a 6G digital-twin paper), R06436 (oversampling algorithm for a CNN on Spark).
- Clarification 2 (I2 not stated): R18688 Energy Landscape SMOTE, R20501 Meta-learned SMOTE, R18203 DTG-SMOTE. These are three 2026 Zenodo preprints with the same template and no reported experiments. All of them otherwise meet I1.
- Tuning an existing generator (the codebook does not settle this; decide consistently): R01385 SMOTUNED was included (I1-other). R00802 (SMOTE parameters tuned by several optimisers, framed as a comparison) and R05044 OOG (Optuna-tuned GAN) are unsure.
- Combinations of existing resamplers (clarification 3), all unsure: R11145 (blends GAN and B-SMOTE learners), R20368 (SMOTE then cWGAN), R08540 (IRC cascade), R08992 (SMOTE-ENN + Tomek). R21669 (label-propagation pseudo-positives before SMOTE-ENN, tested on KEEL) is the closest to an include.
- Unclear whether the new samples are synthetic: R00497 (support-vector sampling, unsure), R05577 (ROBC, unsure), R03469 (affinity-propagation oversampling in an ensemble; included at medium confidence).
- Built for another purpose (clarification 1): R13165 (GAN faces for few-shot recognition), R13287 (Gen-n-Val for long-tailed detection and segmentation).
- R06667 has no abstract, but its title is clearly in scope (label revision for SMOTE samples in multi-label learning), so it is likely an include. R00206 was included but has no venue, so I3 needs checking.
- Excluded, but they may matter elsewhere in the survey: R01535 (theoretical analysis of SMOTE) and R12015 (maths of SMOTE vs Borderline-SMOTE), both coded E-COMPARE; R20691 (NO-IGS) and R18823, oversamplers for imbalanced regression coded E2; R07509 (NNHOS), excluded for language only.
- Theses fail I3, but the codebook has no E-code for that, so I coded them by content: R13895 (E1), R20491 (E-COMPARE).

## batch044

batch 044: 200 of 200 records done; include 25, unsure 10, exclude 165
no records remain

Look at these first:
- Low confidence: R21508 (DERSMOTE, unsure). It is named as a SMOTE variant but moves and reweights existing samples without adding any ("zero sample increment"). The codebook does not say whether this meets I1 or is E-NOGEN.
- Codebook does not settle: R15971 (unsure; its novelty is tuning SMOTE's k with a metaheuristic inside a stroke pipeline). Is parameter tuning a change to how SMOTE is applied? Compare R00862 and R03759, which I excluded under E1 because they only searched for a best class ratio.
- Other unsure records: R04014 (grouped SMOTE), R13568 (SMOTE + GA feature selection), R02170 ("improved SMOTE"), R07825 (Dual-GAN), R01299 (spatiotemporal synthetic oversampling) and R08316 (oversampling + propensity matching for uplift). In all six the abstract does not say whether the generator is new.
- More unsure records: R15251 (U-other; RL-made synthetic data to fine-tune a vision-language model, not imbalanced classification) and R01842 (IDP-SMOTE, no abstract; the venue normally publishes in Chinese, so check the language).
- Borderline includes: R02256 is a GAN oversampler, but the record is typed "Book chapter" in a Lecture Notes series, so check I3. R01949 (PSOSMOTE) implies an evaluation through its metrics but names no datasets (I2). R15612, R19350 and R14305: the generator is half of a framework, so check how new it is. R10053 (SMOTE-MRS) is close to the existing K-means SMOTE.
- Borderline E1 excludes: these use an existing GAN, WGAN or GMM generator as-is in a domain pipeline: R19736, R13860, R18006, R22284, R19335. Also R12194 (MOSD, possibly the authors' own method) and R05394 (TW-SMOTE, applied to genetic association analysis rather than classification).
- Borderline E-NOGEN: R03600 (iteratively duplicates failing test cases, so nothing synthetic) and R04098 ("oversampling" lifted to the ensemble level).
- Excluded on title alone (no abstract): R01439, R16739.
- E-LANG records that describe in-scope methods, for the record: R02795 (an improved SMOTE, in Chinese) and R10866 (natural-neighbour oversampling NNOA, in Chinese).

## batch045

batch 045: 200 of 200 records done; include 19, unsure 29, exclude 152

Look at first:
- Low-confidence unsure: R02100 (GAN class-balancing, novelty and evaluation not stated), R22256 (no abstract, augmentation analysis in IDS), R12894 (oversampling + back-translation hybrid), R09561 ("Improved SMOTE-ENC"), R18320 ("timing-aware oversampling" for video), R19512 ("adaptive Borderline-SMOTE").
- Possible inconsistency: R07093 (retracted; "Improved Random-SMOTE") was coded E1/medium, but R09561 was coded unsure for the same pattern ("Improved" variant, novelty unclear). R07093 probably should be U-new-or-applied. add_rows cannot amend rows, so it is left as E1.
- Clarification 3 unsures (existing generator + existing cleaning/selection) that may deserve include: R05200 (RN-SMOTE: SMOTE, DBSCAN, SMOTE again), R01133 (BSMOTE-Tomek/ENN), R12749 (CP-SMOTE+RUS), R00974 (COSDF), R04930 (LeakGAN+PU labelling), R17091, R19798.
- Borderline includes (medium): R19238 (HCAB-SMOTE-LOF; included because the abstract says LOF constrains where synthesis happens), R07134 (ADASYN within majority-partitioned ensemble), R18465 (differentially private upsampler; privacy purpose and "anomaly detection" title), R05183 ("improved CGAN" not described), R01240 (CycleGAN used as oversampler), R07762 (neural filter for synthetic samples; evaluation vague), R07208 (modified SMOTE in a domain ECG paper).
- Borderline excludes (medium): R00200 and R05739 (unchanged SMOTE before a new classifier or DES ensemble for general imbalanced learning; E1 wording targets domain pipelines), R10868 (existing REaLTabFormer as oversampler), R16747 (existing CGAN applied).
- Not settled by the codebook: R11228 (CRC Press book chapter proposing an extended SMOTE; I3 venue type unclear, coded U-other); R02137 (zero-shot question generator, clarification 1 boundary); retracted records R07093 and R09918; R09213 (typed Review but an original study); R11866 (title and abstract do not match).
- Method papers excluded only on language (E-LANG): R05155 (MCDC-MF-SMOTE) and R02838 (SCF-ADASYN), both in Chinese.
- Clarification 2 (I2 not stated): R18945 and R20496 are 2026 Zenodo preprints with the same style; their full texts may contain experiments.

## batch046

batch 046: 200 of 200 records done; include 24, unsure 10, exclude 166
no records remain

Look at first (record number in batch order, rec id):
- Unsure, codebook clarification 3 (existing generator plus existing cleaning or selection step): 144 R10696 (CTGAN-ENN for intrusion detection), 169 R13396 (HiBBKA, RBU-SMOTE).
- Unsure, cannot tell whether the generator is new: 29 R19307 (Firefly-guided SMOTE), 139 R12777 (GAN augmentation for MQTT intrusion detection), 66 R02065 (bagging and boosting with and without a noise filter, called "our approach"), 153 R21327 (stated contribution is adding standard SMOTE to PU learning).
- Unsure, purpose or task is not plain imbalanced classification: 21 R08433 (differential privacy versions of SMOTE, oversampling and synthetic data), 106 R15592 (diffusion plus class-aware sampling for ultrasound object detection).
- Unsure, no abstract: 148 R15073 (PSGCL, progressive sampling for imbalanced node classification), low confidence.
- Medium-confidence includes to confirm at full text: 9 R18147 (physics-inspired latent diffusion model inside a PV defect framework), 53 R10025 (SIRSYN; I read SIR as changing where samples land, but it could fall under clarification 3), 89 R03503 (FOFO, outlier-targeted two-step SMOTE), 116 R08271 (Borderline-SMOTE inside bagging with cluster undersampling), 115 R01336 (K-means-improved SMOTE in a coal NIR paper; may simply be existing K-means SMOTE), 170 R03405 (swarm rebalancing hybrids; the abstract does not say how examples are generated), 149 R21952 (T-SMmOTE; aimed mainly at data scarcity, see clarification 1), 37 R15438 (graph mixup augmentation of minority graphs).
- Cases the codebook does not settle:
  (a) Resampling in a learned latent or embedding space: 69 R07321 marked unsure (VAE latent space is the paper's core idea), but 39 R19534 excluded E1 (SMOTE on IndicBERT embeddings as one part of an ensemble). These two should be decided the same way.
  (b) New oversampler for a non-classification task: 192 R03960 (real-time over-sampling in spline adaptive filters for system identification) excluded E2, although clarification 1 could send it to unsure.
  (c) Existing deep generators applied in domain pipelines were excluded E1 and tagged generative: 113 R06530 (CTGAN), 155 R09728 (GAN), 126 R22287 (EEG-GANs).
  (d) Multi-label oversampling: 3 R06608 (UCLSO) was included as I1-new-variant without the multiclass tag, because no multi-label tag exists.
- Low or medium-confidence excludes: 55 R09773 (no abstract, generic CHEST title, low), 81 R04392 (Bangla text augmentation by text and embedding generation, described as applying strategies), 109 R00142 (outlier filter plus random oversampling with replacement, coded E-NOGEN), 11 R02911 (uses LSH-SMOTE, possibly the authors' own earlier variant), 13 R09507 (MCS-SMOTE with OVO), 166 R00598 (MWMOTE used for crime clustering, E2).
- For other parts of the survey: 200 R05285 ("Stop Oversampling", evaluates more than 70 oversamplers, tagged comparison); 15 R01834 (front matter that lists a modified ADASYN/SMOTE paper, front-matter-in-scope).
- Language: records with an Indonesian title but an English abstract and language "en" (2 R09253, 87 R07895, 114 R03785, 164 R12954) were coded on content (E1). 110 R21498 has an English abstract but language "zh" and was coded E-LANG.

## batch047

batch 047: 200 of 200 records done; include 20, unsure 12, exclude 168
no records remain

Look at these first:
- Low confidence (unsure): R08385 (MANET IDS "adaptive synthetic auto-encoder": ADASYN applied, or a new generator?); R00284 (2012 rule for choosing the sampling strategy plus a new metric; neither I1 nor I2 is clear).
- Codebook does not settle: R00507 (include; two SMOTE improvements, but the record is typed as a book chapter, so I3 needs a check); R09916 (unsure; theory of under/oversampling with no named method) vs R21925 (include, I1-other; theory plus the VTSS rule for how many synthetic samples to add). These two should be judged the same way.
- Resampling inside an ensemble: R00229 (include, I1-hybrid; integrated over/under-sampling with SVM ensembles) and R21324 (unsure; RF pruning plus resampling). The abstracts do not say whether the oversampling is synthetic. Decide both together.
- Clarification 3 edge cases coded exclude: R04785 (calls SMOTE-Tomek "proposed novel"; coded E1 as an existing variant); R10821 (BHHO feature selection plus unchanged SMOTE presented as a new model; coded E-NOGEN); R03605 (existing K-means SMOTE applied to land cover but called "the proposed method"; coded E1).
- Other borderline includes: R09227 (guided oversampling by NaN insertion, alloy domain); R07146 (kernel-space SMOTE, close to SVM-SMOTE); R19417 (diffusion augmentor inside a quantum classifier framework).
- Borderline excludes: R13299 (GAN/VAE augmentation study, E-COMPARE); R18145 (TimeGAN applied, E1); R16157 (hierarchical RF with "selective SMOTE", E1); R06562 (trajectory regression with GMM plus SMOTE, E2).
- E-LANG records that are otherwise in scope: R04004 (CSbADASYN), R11109 (DDPM), R01206 (instance transfer), all in Chinese. Coded on content despite a non-English language field (title and abstract in English): R17358 (id), R09690 (ar).
- No abstract, excluded from the title only (medium confidence): R09503, R12386, R10260, R11839, R19354, R12509.

## batch048

batch 048: 200 of 200 records done; include 24, unsure 19, exclude 157

Look at these first:
- Low confidence: R02779 (excluded E1; garbled abstract, SMOTE plus an unspecified clustering step), R19672, R10273, R04092, R00176 (all unsure; too little detail to tell whether the oversampling step is new or in scope).
- Clarification 3 (existing generator plus a cleaning or selection step): R12404 DOFCM-SMOTE, R07991 AFS-O, R19907 SMOTE-IH were sent to unsure. R04190 iF-ADASYN was included as I1-hybrid because its abstract presents a new anomaly index. Check that these four are handled the same way.
- I2 not stated in the abstract (new SMOTE variants, no experiments named): R21358 RA-SMOTE, R17106 LSG-SMOTE. Other purpose (privacy synthesizer, oversampling only a by-product): R15569.
- Augmentation used as minority oversampling, which the codebook does not settle: R21584 (included I1-other, targeted ECG augmentation with adaptive synthetic counts); R05174, R04357, R12902, R07107, R18703 (unsure).
- Included at medium confidence because the generator may be existing: R21623 SC-GAN, R00865 modified SMOTE, R12767, R04536, R01235.
- Excluded on language only, otherwise in scope: R02348 (Turkish, GAN plus edited KNN oversampler), R02493 (Chinese, CNN feature-space oversampling).
- Pointers to other papers: R03397 is a reuse note; the TSE 2021 Yedida and Menzies paper it documents may be in scope. Front matter tagged front-matter-in-scope: R04052, R01515, R07348.

## batch049

batch 049: 200 of 200 records done; include 20, unsure 15, exclude 165

Records to look at first:
- Low confidence (all unsure): R12481 (neighbor over-sampling inside early anomaly prediction; synthetic or not, classification or anomaly detection), R22083 (masked-token substitution plus controlled oversampling for Sorani stance detection), R05986 (SMOTE plus neighbourhood cleaning rule, clarification 3), R05624 (Balanced SOINN; abstract does not say whether its resampling synthesizes examples), R18896 (simple hybrid under/oversampling with augmentation for Thai food images, clarification 3).
- I2 not stated in the abstract (clarification 2): R20611 MRC-SMOTE and R22155 U-MSMOTE, both 2026 Zenodo preprints supported only by theory.
- Borderline excludes that could be includes: R04009 (conditional WGAN-GP oversampler inside an electricity theft pipeline, E1), R02682 (IET book chapter, FN-SMOTE with cost-sensitive learning; FN-SMOTE may be the authors' own, E1), R02550 (K-means SMOTE with KELM plus a boosting ELM, E1), R02554 (per-task oversampling before a multi-task DNN, E1), R20609 (has a hybrid balancing step but is scored by MAPE, so E2), R13561 (evolutionary SMOTE for fuzzy c-means clustering, E2), R00563 (recursive ensemble for streams, E-NOGEN), R03781 (parameter study of the existing DEBOHID oversampler, E-COMPARE).
- Medium-confidence includes: R04293 (CIRKNN; synthetic generation implied, not stated), R03104 (no abstract, included on title; reason code arguably I1-other, not I1-new-variant), R02998, R16911, R00627, R07766.
- Not settled by the codebook: R08293 (generative augmentation for defect segmentation, sent as unsure U-other); R02042 (multi-label oversampling, included as I1-new-variant; no multi-label tag exists); book chapters outside proceedings (R02682, R15257, R06112) were coded on substance because I3 has no exclusion code.
- Excluded only for language but methodologically in scope: R01080 (ADASYN-N/ADASYN-KNN, Indonesian), R02800 (OABSC, Chinese), R00162 (AVG_Sampling, Chinese). Front matter with an in-scope title: R05429.

## batch050

batch 050: 200 of 200 records done; include 19, unsure 19, exclude 162
no records remain

Look at these first:
- Codebook gap, automatic tuning of SMOTE amount or parameters (all marked unsure, U-new-or-applied): R00022 (wrapper search over SMOTE and undersampling amounts; likely in scope), R01761 (Bat/PSO tune Random-SMOTE plus feature selection), R05050 (squirrel search sets SMOTE rate and k inside a domain model), R16910 (GA picks the SMOTE/RUS ratio). By contrast, R00015 (C-SMOTE, an ensemble over SMOTE rates) is included as I1-hybrid. One rule for all five is needed.
- Low confidence: R02553 (no abstract; title "SMOTE algorithm based on deep learning" could be an application or a deep variant), R11086 and R16043 (book chapters with an undescribed "hybrid" approach; I3 also doubtful), R00083 (Medicaid "non-random sampling" approaches; cannot tell if the resampling is new).
- Three 2026 Zenodo preprints propose SMOTE variants with no stated experiments (unsure under clarification 2): R21518 (noise-filtered SMOTE), R21520 (RBI-SMOTE), R18193 (DC-SMOTE). They read like one templated series; check whether the full texts have any evaluation.
- Replication rather than synthesis (the codebook does not say whether this counts): R00044 BootOS (unsure, the abstract does not say if it synthesises) and R00601 minority cloning (excluded E-NOGEN, medium confidence).
- Clarification 3 (existing generator plus existing cleaning or selection, presented as new): R17628 BSS-ENN, R00396 SelectSMOTEBoost, R11040 AE-TabNet, R03541 HOUSEN, R07115 rough sets plus SMOTE. Also unsure: R16396 (undescribed modified SMOTE for segmentation) and R13160 (privacy-preserving federated prototypes plus SMOTE, clarification 1).
- Borderline calls at medium confidence. Includes: R00113 (Isomap space SMOTE), R12778 (autoencoder plus K-means oversampling), R00890 (GA text oversampler, vague evaluation), R16550 (diffusion rebalancer inside a larger framework). Excludes: R21863 (plain SMOTE on windowed time series), R13276 and R13623 (off-the-shelf CTGAN or GAN applied to fraud), R08262 (SMOTE plus contrastive augmentation), R04753 (synthetic majority samples used only to make test data harder).
- Language: R00387 (CB-SMOTE) and R04886 (MCA) are in-scope methods excluded only for being in Chinese (E-LANG). Several records whose language field says English have Indonesian titles (R19908, R09069, R20936, R15037, R17301) or an Arabic abstract (R07667); all are excluded on content anyway.
- Other: R02922 is proceedings front matter tagged front-matter-in-scope for a listed EEG-plus-SMOTE paper (probably an application). R03517 is coded E2 as the nearest fit; it is off-topic survey sampling design, not classification.

## batch051

batch 051: 200 of 200 records done; include 24, unsure 11, exclude 165
no records remain

Check first:
- Low confidence: R03031 (unsure; very vague abstract: "suggested algorithms" with "unique" over/undersampling, unclear whether new or synthetic).
- Domain papers using a GAN/VAE/autoencoder oversampler. Five are excluded E1 because no generator design is described: R02508, R12718, R09293, R17443, R15736. Two are included because the design is described: R10951 (cGAN/cVAE with extra conditioning) and R02901 (VAE oversampler for fraud). The codebook does not set where this line falls.
- New oversamplers that copy or retrieve real points instead of synthesizing them, excluded E-NOGEN: R06451 (heterogeneity-weighted bootstrap) and R16561 (multi-label text, adds similar unlabeled instances). The codebook does not settle these.
- Includes whose language is doubtful: R00321 (B-ISMOTE) and R00280 (ImSMOTE-RSTR*) are in Chinese-language journals (Jisuanji Gongcheng; Microelectronics & Computer) but are recorded as en. R20510 is in a Ukrainian venue, recorded as en. Check the language at full text.
- Borderline E-COMPARE calls:
  - R00010: Prati/Batista/Monard 2004 analysis of SMOTE+Tomek and SMOTE+ENN. The abstract's "we have proposed" might be read as proposing them here.
  - R07049: replication study of OPeN (pure-noise oversampling). The codebook does not cover replications.
  - R02516: SMOTE-N/ADASYN-N comparison. "was developed" is ambiguous about authorship.
- Unsure under clarification 3 (existing generator plus an existing step, presented as new): R07450 (GASMOTEPSO_ENN), R02980, R08651, R12622, R07520, R01420, R00026. The same pattern without clarification 3 is R00132 (directed oversampling, may only replicate). R16149 reuses GASMOTEPSO_ENN unchanged (excluded E1), so it depends on the R07450 call.
- Unsure under clarification 2 (I2 not stated in the abstract): R21798 (SNE-SMOTE, theory only) and R10215.
- Excluded only on language but in-scope in content (E-LANG): R03365 (VAE boundary oversampler), R05373 (DBGS oversampler) and R01456 (improved ODR-BSMOTE-SVM).
- R00768: CEUR front matter tagged front-matter-in-scope. It lists "a study of synthetic oversampling for Twitter imbalanced sentiment analysis".
- R11956: language recorded as pt but the abstract is English. Coded E1 on content.
- R18944 and R14052 are book chapters, excluded E1 on content. The codebook has no code for a non-journal/conference type.

## batch052

batch 052: 200 of 200 records done; include 26, unsure 19, exclude 155
no records remain

Look at first:
- Low confidence (all unsure): R22230, R05629, R06384 (no abstract; titles could go either way); R00301 (clustering over-sampling step inside a gene-function SVM, unclear whether synthetic); R07429 (SMOTE/GAN for federated weather classification: new scheme or comparison?); R04025 (neighbourhood cleaning + random oversampling, sent to unsure under clarification 3 although random oversampling only duplicates).
- Includes that rest on an unexplained "improved/enhanced" claim: R05344 (enhanced DeepSMOTE), R06518 and R02982 (improved SMOTE), R08578 (Select-SMOTE may predate the paper).
- Includes where oversampling is only one part of a larger method: R12428 (existing OREMG inside a dynamic ensemble, coded I1-hybrid), R18110 (MLLM augmentation for rare relations), R22187 (CTGAN with relaxed feature bounds and silhouette filtering, taken as a change to generation under clarification 3).
- Excludes that could flip: R10660 (SMOTE-ENN called "improved", no change described), R19037 (plain cGAN augmentation for rare-disease images; compare R08436 DiGAN, sent to unsure), R11798 (k-medoids-SMOTE used as preprocessing), R14613 (Bag Over-Sampling in multi-instance data), R13536 and R18318 (no abstract, excluded on title).
- Not settled by the codebook: R01477 SMOTE-BD, an exact distributed (Spark) SMOTE, included as I1-other; does a scalability-only reimplementation count as changing how SMOTE is applied?
- E-LANG records that are otherwise in-scope oversamplers (Chinese): R13944, R03769, R06238. R05143 is a special-issue preface tagged front-matter-in-scope (Kim et al., oversampling-based augmentation for activity recognition).
- Seven records with "en" metadata but Indonesian or Spanish titles were coded E1, not E-LANG (R20746, R20907, R13923, R17287, R17274, R11335, R21031); they are excluded either way.

## batch053

batch 053: 200 of 200 records done; include 25, unsure 11, exclude 164
no records remain

Look at these first (no record was marked low confidence; these are the borderline calls and codebook gaps):
- Unsure, codebook clarification 3 (existing generator + existing cleaning/selection step presented as new): R08976 (CTGAN + DBSCAN + KNN undersampling), R05610 (RBO + RBU), R05515 (Leader + SMOTE with a chosen ratio).
- Unsure, cannot tell new vs applied: R03631 ("the improved SMOTE" in train delay paper), R09971 ("optimized SMOTE" in SgO-SCNN), R00914 (modified SVM ensemble with over/undersampling), R03321 (book chapter; "synthetic sampling" vs SMOTE), R11672 (no abstract; boundary-focused oversampling, also called a comparative study).
- Unsure, other: R20135 (LT-SMOTE, I2 not stated in the abstract), R11047 (diffusion generator for imbalanced defect object detection, not plain classification), R00112 (2009 thesis proposing Naive Bayes Sampling; I3 doubtful since a thesis is not a journal/conference paper/preprint).
- Borderline exclusions: R16358 (modified WGAN for drug response regression; coded E2, but clarification 1 could send it to unsure); R18041 (E-NOGEN) and R03883 (E1): proposed sampling built on random oversampling, so I treated it as duplication, not synthetic generation (the codebook does not cover this case); R17804 (SMOTE on transformer embeddings, coded E1); R02594 (two SMOTE workflows, coded E1).
- Borderline includes (medium confidence): R12417 (dual-attention WGAN inside a fuel-cell fault diagnosis framework), R06835 (oversampler named but not described), R20695 (noise-aware QSMOTE built for robustness assessment), R21437 (RL-controlled ensemble sampling, vague abstract).
- E-LANG records that are otherwise in scope: R06493 (Chinese, GAN oversampler tested on 36 UCI datasets), R04402 (Chinese, category-prior Mixup), R15190 (Chinese, EdgeTailor). Front matter with an in-scope title: R10306 (CARI 2024, "SMOTE in Stages for a Rice Dataset").
- Document type does not match content: R19702 and R03279 are labelled Review but are primary studies, so I coded them on their content (E1).

## batch054

batch 054: 200 of 200 records done; include 20, unsure 20, exclude 160
no records remain

Records a person should look at first:
- Low confidence: R16196 (Rolling SMOTE augmentation may be new, but RMSE evaluation suggests regression), R12101, R04023, R11044, R03250, R13225 (oversampling is one part of a larger method and the abstract does not show what is new), R11151 (no abstract, multi-fidelity GP classifier).
- GAN used inside a domain pipeline, check that these calls agree: R06345, R19272, R21493 (unsure) vs R17604 (exclude E1, existing BGAN used for intrusion-detection augmentation).
- Existing generator plus existing cleaning or selection step: R03510 (SMOTE+Tomek+cost-sensitive SVM, unsure) vs R02060 (SMOTETomek+PSO feature selection, exclude E1) are near-identical patterns; also R08087, R01179, R19935, R03973 (unsure).
- Medium-confidence includes: R00577 (SelectSMOTEBoost, SMOTE in boosting with feature selection), R05529 (new majority reduction step + plain SMOTE), R15628 (redesigned DeepSMOTE, change not described), R12265 (template-based defect image synthesis; check that the task is classification), R09627 (OsImp).
- Not settled by the codebook: R20864 (G-CTGAN is in scope, but the abstract is in Korean while metadata says en); R18686 and R21557 (Zenodo SMOTE-variant preprints with theoretical analysis only, I2 not stated; similar to R20500, included because it reports experiments); R18682 (GAN augmentation for non-IID federated learning).
- In scope but excluded only for language (E-LANG): R04280 (Chinese, WGAN minority generator), R00187 (Chinese, negative-immune oversampler).
- Borderline excludes and no-abstract records: R06780 (FCM+SMOTE+SVM wildfire), R04104 (dual evolutionary bagging); R21962 (TAD-SMOTE, no abstract, unsure, likely include); R00016 and R20240 (no abstract, excluded on title).

## batch055

batch 055: 200 of 200 records done; include 30, unsure 13, exclude 157
no records remain

Look at these first:
- Low-confidence excludes with no abstract: R03893 (retracted DL intrusion detection paper), R15347 (diabetes deep ensemble). Only the titles were available; neither points to a new resampler.
- Low-confidence unsure (domain papers with a vaguely new resampling step): R11150 (two-stage SMOTEENN then SMOTETomek), R17118 (oversampling inside per-attack binary models), R04844 ('novel' GAN/TVAE sample-size augmentation), R21454 (feature-level SMOTE plus focal loss), R19543 (GPT used as an oversampler for Arabic text), R15320 (named 'MOSD' oversampler).
- I2 not stated (clarification 2): R21497 (Od-SMOTE, theory only), R09143 (SMOTE in a feature-selected subspace for text).
- Borderline includes (medium): R15961 (DBO K-means constrained SMOTE in a lithology paper), R10737 (QENS noise injection on SMOTEENN), R00717 and R01187 (SMOTE with their own undersampling, counted as 'new cleaning step' hybrids), R03285 (contingency-based synthetic data for power systems; may be simulation, not an oversampler), R00144 (K* distance inside SMOTE plus a SMOTE/SMaRT combination; 2009, no venue), R13473 (existing Stable Diffusion plus feature-level SMOTE), R02355 (CWOS-Ord; ordinal classes treated as classification, not E2).
- Not settled by the codebook: R07081 is excluded E-LANG (Chinese) but proposes safe-borderline-SMOTE and would otherwise qualify. R00987 is a book chapter (no document-type code), coded E-NOGEN. R18694's 'range-controlled' oversampler looks like the existing RCSMOTE, so it was coded E1. R03515's two-stage training changes where SMOTE is used but not how samples are made, so it was coded E1.

## batch056

batch 056: 200 of 200 records done; include 24, unsure 14, exclude 162
no records remain

Look at these first:
- Low-confidence calls: R12616 (include: "improved GAN" IDS, the improvement is not described and the name matches an earlier IGAN-IDS), R01632, R05549, R01905, R08365 (unsure: cannot tell whether the oversampler is new), R09617 (unsure: its "novel LORAS" may be the existing LoRAS oversampler).
- Borderline includes: R02117 (SOUP: abstract does not say whether it synthesizes or replicates examples), R00525 (SMOTE inside bagging, close to existing SMOTEBagging), R01044 (CMTFSVM before SMOTE: is the cleaning step new?), R00297 (QMSVM: venue mostly publishes in Chinese, so check the language), R01895 (DSMOTE, but the record is a book chapter, so I3 is unclear), R11583 (CVAE plus ADASYN, two existing generators combined), R03105 (LR-SMOTE plus CCR variant).
- Consistency check: R16744 (prompt-based GPT-2, include) versus R04006 (GPT-2/LSTM plus grammar check, unsure under clarification 3).
- GAN papers excluded as E1 because a named generator is used unchanged: R04755, R12312, R06095, R03770. R13039 is unsure because the abstract does not say which GAN design it uses.
- Borderline excludes: R00515 (plain SMOTE before a new ensemble, benchmarked against SMOTEBagging/SMOTEBoost), R20075 (joint tuning of SMOTE k), R10579 (SMOTE-ENN "hybridized"), R16259, R20814.
- Not settled by the codebook: R21390 (reproduction study of OPeN pure-noise oversampling, coded E-COMPARE), R07124 (retracted), R03594 (Chinese, method otherwise in scope, coded E-LANG). R08218, R18131 and R17972 are U-other: their purposes are data sharing, augmentation of scarce data, and detection/segmentation. R14210, R14471 and R09256 have non-English titles but language=en; all three are excluded as E1 anyway.

## batch057

batch 057: 200 of 200 records done; include 21, unsure 11, exclude 168
no records remain

Look at these first:
- Low confidence: R00103 (VOTCL, unsure). It is an ensemble on subsets balanced by under- plus oversampling; the oversampler is not named, and the contribution may be only the threshold voting.
- Unsure, no SMOTE change or synthetic generation stated: R01431 (OOLASVM, oversampling of support vectors, maybe by replication), R06133 (density clustering with random under/oversampling, multiclass), R01405 (MASI, says "moving" samples, unclear whether it generates any). The codebook does not say whether new methods built on random oversampling or on moving samples meet I1.
- Unsure under clarification 3 or "novel framework": R05644 (TVAE+SMOTE+Boruta), R16978 (ENN-CTGAN), R16269 (SMOTE+CTGAN IDS), R04164 (Borderline-SMOTE+Tomek), R15894 (GAN oversampling, not named), R04108 (deep imbalance algorithm, unclear whether it generates). R19684 (ICUBO) has no abstract; its title names a new oversampler.
- Includes at medium confidence:
  - R06750 (MaMiPot): repositions samples, also run as a SMOTE preprocessor.
  - R00196 and R06407: existing generator run within GMM or genetic k-means clusters. I counted the clustering as a change to the generation, because clarification 3 covers only cleaning and selection steps.
  - R12409: sliding-window SMOTE inside a domain paper.
  - R04055: 1D-DCGAN in CNN feature space.
- Borderline excludes:
  - R03471 (ESMOTE): new evolutionary SMOTE, but used for warfarin dose regression (E2).
  - E1 at medium confidence: R21506 (clustering-based SMOTE "introduced"), R08277 ("Enhanced SMOTE", keyword SMOTE-ENC), R20022 (multimodal SMOTENC plus image augmentation), R16118 and R19867 (existing CTGAN or cGAN), R16729 (synthetic oversampling not specified), R00696 (MapReduce random oversampling).
- New in-scope oversamplers excluded only under E-LANG (Chinese): R10331, R05575, R03721.

## batch058

batch 058: 200 of 200 records done; include 29, unsure 19, exclude 152
no records remain

Records to look at first:
- Low-confidence unsure (abstract too vague to tell whether synthetic generation is new, or whether there is any): R00036, R04924, R00242, R06773, R20571, R13177, R02474, R12230, R01995, R16992 (clarification 1: CTGAN/LLM transaction generator built to create a dataset, not for minority oversampling; probably exclude).
- Clarification 3 calls (existing generator + clustering/selection step presented as new, so unsure): R02569 (DBSCAN + WGAN-div), R09785 (Borderline-SMOTE + entropy-scored undersampling), R05319 (FCM + SMOTE), R13222 (cluster-guided ROS/SMOTE), R13835, R09597, R09786. Domain pipelines that only apply ADASYN+ENN or outlier removal + SMOTE were coded E1, not unsure: R12604, R02405 (medium).
- Borderline includes (medium): R00714 (SMOTE applied in a compositional word-embedding space), R05372 and R03002 and R13398 (oversampler type not stated), R09544 (extends the authors' own NI-MWMOTE; check E4 at full text), R07827 (generates minority rules, not examples), R21002 (AC-GAN built from existing components), R16409, R06280, R09333.
- Borderline excludes (medium): R20537 (off-the-shelf Stable Diffusion + validation filter, not claimed as a method), R02696, R00334 (SVM relabelling, E-NOGEN), R19138 (no abstract, domain title). Generative/new oversampling used only for regression, coded E2: R13242, R13334, R14800.
- Not settled by the codebook: R07870 proposes an in-scope SMOTE variant (COW-SMOTE) but is in Chinese (E-LANG); R00713 is a theory note on rebalancing and AUC with no method (coded E-COMPARE as the nearest code); R01673 claims novelty but reads like SMOTEBoost (unsure); R22294 is front matter with an in-scope listed title (ICDG). Language may not be English despite the metadata for R00242 and R00316 (Chinese journals), and for R15042, R09659, R20921, R14723 (Indonesian titles).

## batch059

batch 059: 200 of 200 records done; include 29, unsure 16, exclude 155
no records remain

Records to look at first:
- Low confidence: R05002 (copy-paste minority augmentation, but the task is instance segmentation/detection, not classification); R15353 ("Enhanced SMOTE" appears only in the keywords, not the abstract); R06207 (no abstract, improved SVM + oversampling); R15270 ("enhanced hybrid ADASYN-SMOTE" in an IDS; check together with R16724, excluded E1 at medium confidence, which is a similar ADASYN + SMOTE-ENN hybrid).
- Cases the codebook does not settle: R05311 (in-scope Heinz-mean oversampler, but the Turkish title suggests a non-English full text although metadata says en); R03571 (arXiv PhD thesis summarizing 12 resampling papers, so document type and E4 overlap need checking); R16486 (included FL-SMOTE: privacy/federated setting, but the purpose is imbalanced fraud classification, so clarification 1 was not applied).
- Borderline includes (medium): R03455 and R06672 (new hybrid sampling ensembles whose oversampler is not named, so it may be random duplication); R01885 (active learning + oversampling); R04042 (SMOTE + GA); R05564 (improved SCUT, where the change may only be in undersampling); R20684 (existing LLM generator + new filtering, a clarification 3 boundary); R21003, R16437, R04410 (generators embedded in larger frameworks).
- Unsure, existing generator + other step (clarification 3): R02413, R08453, R05312, R00179, R15760, R00124, R07103. Unsure for other reasons: R12764 (I2 not stated); R10884 and R21970 (no abstract, titles suggest generative oversamplers).
- Exclusions worth a glance: R21546 (unfamiliar "LSMOST" oversampler used, but not presented as the contribution); R20026 and R02038 (E-LANG, Chinese records that also only apply SMOTE).

## batch060

batch 060: 200 of 200 records done; include 27, unsure 11, exclude 162
no records remain

Records to check first (record number in batch / rec id):
- Low-confidence includes: 34/R05320 (repeated SMOTE for multiclass, novelty doubtful, may be E1); 53/R02308 (MASI relabels majority samples as minority: does relabeling count as generation?); 153/R02354 (SMOTE "enhanced using Orchard's algorithm", may be a speed-up only).
- Borderline medium includes: 6/R00299 (kNN oversampling for streams); 40/R16542 (pattern-based oversampling module inside GraphSAGE+); 107/R06321 (PSO/GA-based oversampling, mechanism unclear); 112/R00393 (SMOTE inside cost-sensitive hypernetwork ensembles); 117/R19845 (class restructuring before SMOTE); 144/R22374 (K-Shape regions + DTW-SMOTE); 146/R06485 (SMOTE + bootstrap one-vs-all); 157/R16635 (SMOTE-CF + weighted ENN); 162/R04278 (extended study of the authors' C-SMOTE, possible E4 at full text).
- Unsure, I2 not stated (theory only, same Zenodo series): 74/R21983 Temporal SMOTE, 84/R20584 Multi-agent SMOTE, 128/R20597 Multi-hop SMOTE.
- Unsure, other: 102/R18753 (DCGAN pseudo-sample generation for membership inference attacks, purpose not imbalance); 180/R19411 (LLM-generated minority reviews vs SMOTE, Indonesian title, language doubtful); 191/R16036 (Time Series ROS, duplication or synthesis unclear); 25/R16239, 48/R08772, 55/R13703 (generator may or may not be new); 88/R01394 and 189/R12690 (no abstract).
- Language calls the codebook does not settle from metadata: 200/R03876 (E-LANG on Korean abstract although metadata says English; in-scope method otherwise); 179/R10217 (Chinese, improved CP-SMOTE, in scope otherwise); 129/R06612 (Chinese); 68/R05842 (Thai, coded E1); 77/R14273 (Korean abstract, coded E1).
- No code fits: 198/R01528 is the smotefamily R package (software, not a paper), coded E-REVIEW.
- Medium-confidence E1 calls on existing generators: 71/R04219 (LMOTE applied), 78/R15578 (CTGAN + cost-sensitive distillation), 118/R12172 (DCGAN balancing), 126/R01097 (tuning of the authors' earlier hyperSMURF, a SMOTE hybrid), 81/R00869, 176/R11544, 193/R10444; plus no-abstract excludes 21/R18928, 47/R11224, 192/R16636 (E2), 169/R19550 (E2, regression).

## batch061

batch 061: 200 of 200 records done; include 22, unsure 11, exclude 167
no records remain

Look at first:
- Lowest confidence: R18897 (unsure, low). It calls retrieval-augmented embedding enrichment a "dynamic oversampling strategy", but it seems to enrich features rather than generate minority examples.
- Includes that only change how much existing oversamplers resample (I1-other): R03063 (GA-chosen sampling ratios) and R09784 (classification-intensity resampling; SMOTE is named only in the keywords). Please confirm that ratio-setting counts as "changes how SMOTE is applied".
- Medium-confidence includes that need a full-text check:
  - R14650: weighted oversampling; synthetic or duplicated?
  - R00324: SwarmBoost; type of oversampling not stated.
  - R00049 (2007): a "novel oversampling algorithm", not described.
  - R07224 Synthetic-MixUp: the abstract's results mention only ROS and SMOTE.
  - R10902 AdaCluCSL: close to k-means SMOTE.
  - R19267 Fed-DiTTab: DiTTab may be prior work.
  - R12089 SC-CTGAN, R08285 AWSMOTE-NN, R00094 ABUSVM (TRECVID notebook), R01006 (SMOTE plus a new noise filter).
- Unsure, new or applied (clarification 3 and similar):
  - R12937: ADASYN then CTGAN.
  - R15562: RENN then SMOTE as "our proposed method".
  - R17691: SMOTE plus Gaussian noise.
  - R01363: bagging plus SMOTE; new scheme or existing SMOTEBagging?
  - R02257: AP-SMOTE; whose method?
  - R19693: Latin-hypercube/NN oversampler; benchmarked here, maybe proposed elsewhere.
- Unsure, no abstract but in-scope titles: R01848 (adversarial minority over-sampling), R04223 (adaptive kernel SMOTE-SVM), R15541 (CSA-optimized SMOTE).
- Not settled by the codebook: R21995 is a thesis (I3 names only journal, conference and preprint, and there is no exclusion code for document type), so it is unsure U-other. It designs a new semi-AI minority synthesis method.
- Borderline E1 excludes worth a glance: R10804 and R15235 (no abstract, domain titles), R03565 ("SMOTE with SVM" called the proposed technique), R05780, R07472, R06743, R20046, R07863, R14412, R02929.
- Front matter tagged front-matter-in-scope: R05424 lists an adaptive heterogeneous oversampling ensemble; R01465 (ICSE 2018) lists MAHAKIL.
- Language: R03272 is Korean (E-LANG). R14700 (Indonesian title), R07344 (Ukrainian title) and R02138 (Thai title) have English abstracts and were excluded on content, but their full texts are likely not in English.

## batch062

batch 062: 200 of 200 records done; include 27, unsure 12, exclude 161

Look at first:
- Low confidence: R01396 (unsure; book chapter on neighbourhood-based minority example types, "generalizations of over-sampling" may or may not be a new generator).
- Existing generative model used as the oversampler in a domain paper and presented as the method; included at medium confidence, but the codebook does not settle whether this is I1-generative or E1: R12267 (DDIM, IDS), R05652 (improved CWGAN-GP, wind turbine), R01745 (GAN, social bots), R02848 (GAN, bank churn), R21954 (TabDDPM-Med). Similar but framed as evaluation, so excluded: R21154 (VAE-GAN, E-COMPARE), R22060 (CGAN, E1).
- Tuning SMOTE parameters or ratios counted as "changes how SMOTE is applied" (I1-other, medium): R01134, R15298. Contrast R06151, an empirical ratio study with no method (E-COMPARE).
- Replication-type or unspecified oversampling, which the codebook does not settle: R10031 and R17401 excluded E-NOGEN (random or distribution resampling, no synthetic data); R07777 and R08771 unsure (nature of the oversampling not stated).
- Other medium-confidence includes: R17673 (cluster purity-guided resampling in a bioinformatics tool), R00378 (IFSMOTE, unclear abstract), R04767 (sparse abstract), R13645 (Gaussian-noise augmentation), R18850 (object-level synthesis for segmentation), R04446 (SMOTE plus OVA).
- Purpose other than classification: R00840 unsure U-other (SMOTE plus KS test for pump life estimation); R13812 excluded E2 (SMOTE-GN-Bootstrap augmentation for SVR), which could arguably be U-other under clarification 1.
- Remaining unsure: R03288, R16659 (I2 not stated), R10753 (no abstract), R15615, R04629, R04647, R20848, R07801.
- Notes: R03562 (Spark big-data oversampling taxonomy and library, E-COMPARE) is relevant to the survey; R07027 is AISTATS 2023 front matter tagged front-matter-in-scope (majority-guided VAE oversampling). No-abstract excludes: R19836, R03822, R12316, R02457. Coded E-LANG: R20902, R08126. Coded E1 despite non-English metadata or title: R21245, R16538, R15669, R14698. R08058 is a retracted record and R15707 is a thesis.

## batch063

batch 063: 200 of 200 records done; include 26, unsure 18, exclude 156

Records to look at first:
- Low confidence: R09920 (include; Scopus type "Retracted", the codebook is silent on retractions; new three-way-decision boundary oversampler inside an attribute-reduction method), R04266 (include; different oversamplers used to diversify an ensemble of belief-rule bases, main novelty is the rule base), R20989 (exclude; latent-space oversampling is one part of a diet-prediction pipeline), R03818, R02872, R15921 (unsure; R02872 has a garbled abstract and is indexed as a Review; R15921 has a Ukrainian title although the language field says en).
- Borderline under clarification 3: R02177 and R19786 included (M-SMOTE rate set by Random Forest errors; SMOTE+NCR+RUS inside each bag of a bagging ensemble). R08265, R00789, R14525, R13368 and R16915 marked unsure. R19844 (existing CTGAN plus a feature-refining DAE) excluded.
- Generators for other purposes, or existing generators applied: R19882 unsure (LLM text generation, clarification 1). R07216 (existing GAN and SMOTE used to synthesize tax data for privacy) and R02008 (existing CGAN used as oversampler for drug-target data, 2018) excluded with medium confidence. R17457 unsure (autoencoder makes pseudo-normal samples; unclear whether this is classification or anomaly detection).
- Likely includes waiting on the full text: R09280 (LD-CSMOTE, no abstract), R05280 (no abstract), R21451 (RE-SMOTE, I2 not stated in the abstract).
- Other: R08963 included for a side contribution (Soft-SMOTE) although its Scopus type is "Short survey". R06399 excluded only on language (a Chinese article proposing a new oversampler). Front matter tagged front-matter-in-scope: R04051 (oversampling taxonomy paper) and R06491 (GBSMOTE).

## batch064

batch 064: 200 of 200 records done; include 32, unsure 17, exclude 151

Look at first:
- Low confidence (unsure): R11269 ("Randomized Weighted SMOTE", abstract too thin to say if new), R14120 (GPON "vetted synthetic samples", generator not described), R02333 (point cloud hybrid sampling inside a new training framework).
- R06099 (include, medium): SMOTIFIED-GAN is presented as proposed, but the name matches an earlier SMOTified-GAN method, so this may be an application to gearbox faults (E1).
- GAN fault-diagnosis papers split on whether the generator is changed: R19236 and R10489 included (improved or PSO-tuned WGAN-GP), R14797 excluded E1 (standard CWGAN-GP). Unsure because the generator design is unclear: R16423, R20068, R18748.
- Clarification 2 (I2 not stated in the abstract): R10796 (triangular-region oversampler inside boosting), R02133 (multiple trials/feedback technique for SMOTE).
- Not settled by the codebook: R05435 (exclude E-NOGEN; enlarges the minority class with pseudo-labelled unlabelled data, not synthetic samples), R22329 (include, medium; tail-class perturbation augmentation inside a framework whose headline is a regularizer), R04970 (unsure; new multiclass label-noise filters with SMOTE folded in).
- Borderline calls: R08489 (E-COMPARE; noise filters before oversamplers, framed as an assessment), R00535 (include, medium; mainly analysis, but changes the SMOTE-related oversampling ratio), R06588 (include, medium; unclear whether the propensity-score oversampling is synthetic), R12678 (include, medium; LLM prompt oversampling barely described), R02070 and R04435 (unsure under clarification 3).
- No abstract: R06100 and R09757 excluded E1 (application titles), R08023 excluded E-REVIEW (generic textbook chapter). Language: R09660 (title in Indonesian, abstract in English) coded E1, R15923 (title in Ukrainian, a review) coded E-REVIEW.

## batch065

batch 065: 200 of 200 records done; include 19, unsure 16, exclude 165
no records remain

Look at first (no record was coded low confidence; these are the medium-confidence borderline calls and the cases the codebook does not settle):
- Borderline includes: R00343 SMOTE-FRST (SMOTE + fuzzy-rough editing; included as I1-hybrid because the editing step reads as the authors' own; if it is an existing editor, clarification 3 makes it unsure); R05177 raking/relabeling sampler (mechanism vague, title says one-class, abstract says binary); R01273 CBOUS (unclear whether its oversampling is synthetic or duplication); R16498 A-REACT (active learning + adaptive resampling, change to generation implied but not described); R15089 QCL-MixNet (kNN-guided mixup is one part of a deep framework); R18093 G-TOD (distribution-calibrated generative oversampling inside a graph transfer framework); R11294 CWGAN-GP oversampler for IDS (known architecture, included because it is presented as the contribution).
- Borderline excludes: R09324 (ADASYN+ENN+RF picked from 18 lithology workflows and called "a new process"; coded E1, though clarification 3 could send it to unsure); R15575 (synthetic counterfactual labels for conformal intervals, E2 rather than clarification 1); R19428 (diagnostic score for SMOTE under distribution shift, not a generator; tagged comparison, may be useful as discussion); R12541, R20633, R21760, R11549 (domain pipelines whose resampling step may be slightly modified: CTGAN+SMOTE, "tailored" SMOTE, clustered SMOTE-ENN, oversampling with noise injection).
- Title-only decisions: R18689 (E1) and R21322 (E-NOGEN) have no abstract; R16866 (no abstract) is unsure.
- Unsure records driven by clarifications 1 and 2: R21491 CS-SMOTE and R19265 Feature-token SMOTE (Zenodo preprints, theory-only abstracts, I2 not stated); R04984 CA-GAN (generates data for underrepresented ethnic groups to reduce bias); R20706 improved WGAN (generates data for scarcity under grid topology changes). R20706 also has a bilingual Chinese title in a Chinese journal, so the full text may not be in English.
- Not settled by the codebook: (a) R05937 (improved K-means SMOTE) and R06101 (improved ACGAN) are in-scope methods excluded only by E-LANG (Chinese); (b) multi-label oversamplers have no code or tag, so R10710 MLCIO (include) and R02401 DAI (unsure) carry the multiclass tag; (c) R00001 is off-topic (mineralogy) and coded E-NOGEN because there is no off-topic code; (d) R07303, R19764, R14725 and R17308 have Indonesian titles but English abstracts and language "en", and were excluded on other grounds; (e) for domain studies that compare existing resamplers, I used E1 + comparison tag when the domain model was the focus and E-COMPARE when comparing balancing methods was the stated aim.

## batch066

batch 066: 200 of 200 records done; include 25, unsure 22, exclude 153

Look at these first:
- Cases the codebook does not settle: R12009 (NeurIPS theory of SMOTE risk bounds with tuning guidelines; no category for theory papers, likely relevant), R00006 (Batista et al. 2004, original SMOTE+Tomek / SMOTE+ENN proposal; unsure only because of rule 3, probably an include), R00416 (semi-supervised "oversampling" that pseudo-labels real unlabeled samples; are these synthetic?), R01824 (semi-supervised GAN "complementary" samples for hard attributes).
- Rule 3 (existing generator + existing cleaning/selection, presented as new): R00006, R11265 (ROSE+Tomek), R17126 (WGAN-GP+ENN), R05576 (ROSE + k-means undersampling). R00746 (SMOTE + denoising autoencoder) is similar.
- Rule 2 (I2 not stated in abstract): R20083 (KC-SMOTE), R20627 (Multi-view SMOTE), R18001 (context-aware generative augmentation, general purpose).
- Rule 1 (generator built for another purpose): R15812 (image translation for source-free domain adaptation in segmentation).
- Low-confidence include: R06454 (minority mixup augmentation inside a compositional zero-shot model). Medium includes resting on a single abstract sentence: R03118, R02461, R05115, R01353 (Spark/LSH SMOTE), R06879, R08892, R01392, R08139 (simulation-generated instances), R21425 (mutation-generated defects), R03162 and R10512 (generative, existing generator types adapted).
- Borderline excludes: R17980 (existing CTGAN for balancing, E1; compare with R10512 included), R16270 (ensemble of SMOTE and non-SMOTE models, E1), R13419 (SMOTE+ENN pipeline called novel, E1), R01254 (SMOTEBoost-SVM applied, E1), R16416 (re-weighting + Mixup, E-NOGEN).
- Other unsure records: R10721 (no abstract, data augmentation diagnosis framework), R01262, R05899, R01186, R21472, R20641, R19515, R09095, R12628, R20650 (cannot tell whether the resampling is new).
- Possibly useful elsewhere: R03767 (oversampling-before-split flaw, E-COMPARE); R04056 front matter tagged front-matter-in-scope (listed paper on oversampling for fraud detection).

## batch067

batch 067: 200 of 200 records done; include 25, unsure 19, exclude 156
no records remain

Check first (low confidence or borderline):
- Language unclear: R21881 was excluded E-LANG because the language field says zh, but the title and abstract are English and the method (a generative oversampler) is in scope. R00063 was included (MCMO-Boost), but its venue, Jisuanji gongcheng, is a Chinese journal; check the full-text language. R01192 was excluded E-LANG (Chinese) but would otherwise be in scope.
- Cases the codebook does not settle: R20721 (theory of generative augmentation, no new generator) was coded E-COMPARE. R05203 (DIRECT trains on a smoothed minority distribution and generates no samples) was coded E-NOGEN.
- Includes resting on thin abstracts: R06274 (novel oversampler, evaluation only implied), R16677 (CN-SMOTE inside a skin lesion framework), R13943 (TVAE plus quality-diversity post-selection).
- Low-confidence unsure: R15697 (group-conditional oversampling for fairness in federated learning), R10277 (adaptive oversampling for object detection), R04366 (I2 not stated; graduate review), R01514 (deep over-sampling extension), R09732 (multilabel graph oversampling compared with MLSMOTE), R16316 (GAN plus SMOTE-Tomek), R12627 (SMOTE plus targeted undersampling), R01551 (SMOTE with one-vs-one in a multiclass ensemble).
- Clarification 3 unsures (existing generator plus a cleaning or other step): R10565, R02970, R18762, R05963, R07106, R02036. Also unsure: R15955 (Bit-level SMOTE, I2 not stated), R07609 (lexicon augmentation), R20160 (ChatGPT augmentation), R08001, R10557.
- Front matter in scope: R01157 (lists a VAE oversampling paper, CLOUD 2018) and R15934 (lists SVM-guided GraphSMOTE, PReMI 2025).
- Low-confidence exclude: R02587 (no abstract). R12538 has a garbled abstract (two abstracts merged).

## batch068

batch 068: 200 of 200 records done; include 21, unsure 19, exclude 160
no records remain

Records to look at first:
- Low confidence: R19448 (unsure; GNN paper that synthesises sensor-failure false positives), R10302 (unsure; Greek-titled thesis, language unclear, and the codebook has no exclusion code for theses), R14367 (unsure; GAN text augmentation inside a T5-CapsNet model).
- Two similar cases got different calls. Each proposes a plain generator as its main contribution: R21126 (VAE, unsure) and R13275 (class-conditional GAN, include). Check them together; R21126 may deserve include.
- Clarification 3 (existing generator plus a selection or cleaning step), all unsure: R03914, R10546, R00363, R02978, R03309, R17718. R03914 filters seeds by outlier detection, which is arguably new seed selection and could be an include. R05753 was included only because the abstract says "improved SMOTE"; the change is not described.
- I2 doubtful: R01335 (G-SMOTE) and R20694 (NIS-SMOTE) are unsure because their abstracts name no evaluation. R20859 (OverNaN) was included, but its only evaluation is a demonstration on examples bundled with the software.
- The codebook does not say whether non-synthetic (replication) oversamplers count. Three such methods were excluded as E-NOGEN: R14566 (RO-R), R02817 (clustering-based ROS ensemble), R06770 (stratified k-means sampling).
- Two similar fusion methods got different calls: R03558 (ERC, fuses classifiers trained on under-, over- and hybrid-sampled data; unsure) and R09485 (MOEF, a multi-oversampling strategy with evidence fusion; include).
- In-scope methods excluded only on language (E-LANG): R09100 (IProWSyn) and R01425 (ANBSC-SMOTE), both Chinese. R20705 is listed as zh but has an English abstract.
- Other borderline includes: R16452 (MOOST, framed as anomaly detection but trained as a supervised classifier), R12049 (multi-label seed selection; the abstract does not say whether samples are synthetic or replicated), R01585 (3D spatial interpolation oversampler built for one domain, coded I1-other).

## batch069

batch 069: 200 of 200 records done; include 23, unsure 15, exclude 162
no records remain

Look at these first:
- Low-confidence unsure: R08609 (mosaic augmentation with soft labels for tongue lesions: does mixing augmentation count as minority generation?), R01071 (SHWeL hashing "tackles imbalance directly" vs SMOTE: synthetic samples or not?), R01313 (bag-level oversampling in multi-instance DR grading: synthetic bags?), R20646 (no abstract; class imbalance in the title), R13066 ("improved SMOTE" not described, no data named).
- Cases the codebook does not settle: R03618 improves MWMOTE (meets I1 and I2) but the title is Indonesian while metadata says English, so I3 needs a full-text check. R05146 is a privacy-preserving (homomorphic encryption) SMOTE / Borderline-SMOTE protocol; coded U-other under clarification 1, although its purpose is still imbalanced classification.
- Clarification 2 (I2 not stated): R18537 Dual-space SMOTE and R18954 Equivariant SMOTE are 2026 Zenodo preprints with only a "theoretical" evaluation and near-identical wording (possibly the same source). R10877 (SSRN, no abstract, geometry-aware SMOTE variants) is likely an include if the full text has experiments.
- Clarification 3 unsure (existing generator plus existing step): R00360 (ISMOTE + DUS), R04729 (FinGAN: existing GANs + OCSVM), R22301 (SMOTE/Borderline/CTGAN + clustering), R15691 (TLBS = Borderline-SMOTE + Tomek), R14788 (PMOTE probabilistic oversampling on embeddings).
- Medium-confidence includes: R10196 (LLM prompting to generate minority samples), R00995 (EHSBoost; oversampling type not stated), R12261 (Borderline-SMOTE inside DeepSMOTE), R17984 (SMOTE + plausibility filtering), R22246, R13807, R07063 (new oversamplers in domain papers).
- Medium-confidence excludes: R04606 (stream ensemble replays stored real minority samples, E-NOGEN); R08697 and R07670 (existing SMOTE-Tomek / SMOTE + undersampling called novel, coded E1); R06622 (no abstract, excluded on title); R04692 ("manual augmentation" plus SMOTE variants).

## batch070

batch 070: 200 of 200 records done; include 24, unsure 14, exclude 162
no records remain

Look at first (no low-confidence rows; these are the borderline calls and cases the codebook does not settle):
- Codebook does not settle: R01790 (new ESMOTE built for regression, warfarin dose: clarification 1 versus E2, sent to unsure); R04124 (in-scope SMOTE + CycleGAN hybrid, but the abstract is Korean while the metadata says en, so the paper's language is unclear); R00317 (oversampling inside boosting that copies minority samples, not synthetic ones; does replication count under I1?); R03179 (BSS-GAN, not clear whether it generates minority examples); R09853 (book chapter, which leaves I3 in doubt, plus an unclear "Federated SMOTE").
- Includes at medium confidence (novelty of the resampler needs the full text): R04837, R22251, R12689, R15787, R00287, R00355, R13524, R01618, R18761, R13297.
- Excludes at medium confidence: R22407 (off-the-shelf diffusion/Gemini minority augmentation, coded E1), R02545, R19661, R17442, R08562, R01775, R12884, R01820, R09722 (no abstract).
- I2 not stated in the abstract (clarification 2): R21494 (Encoding-shift SMOTE) and R18476 (DF-SMOTE), both 2026 Zenodo preprints that claim only theoretical results; R05356 (Fair Oversampling).
- Excluded under E-LANG although the content is in scope: R09634, R15586, R09895 (all Chinese). R04019 is a Zenodo "Trial" deposit carrying the SMOTE 15-year review abstract (E-REVIEW). R14563 is retracted (E1 anyway).

## batch071

batch 071: 200 of 200 records done; include 29, unsure 18, exclude 153
no records remain

Look at first:
- Low confidence: R03573 (included, but the abstract is garbled and looks machine-paraphrased; it seems to propose a PSO Border-Kernel-SMOTE and may copy another paper); R09804 (unsure: education study with two-stage classification plus SMOTE; does a decomposition like this count as a "multiclass scheme for oversampling"?); R02881 (unsure: virtual-big-data cross-concatenation balances classes "without over-sampling" and names no evaluation); R19396 (unsure: label-aware loose pairing of fundus and OCT images to expand minority classes); R19818 (unsure: SMOTE plus outlier removal offered as the paper's imbalance solution).
- Cases the codebook does not settle:
  R00693 is SMOTER, SMOTE adapted to imbalanced regression. I excluded it under E2, but clarification 1 (a SMOTE extension built for another purpose goes to unsure) could also apply.
  R18199 (DEB-ADA) chains two existing generators, ADASYN then DEBOHID, and is tested on 44 KEEL datasets. Clarification 3 covers a generator plus a cleaning or selection step, not two generators, so I marked it unsure by analogy. Its language metadata says Turkish.
  Clarification 3 inside domain frameworks: I marked R12286, R19818 and R08282 unsure because SMOTE plus a cleaning or selection step is offered as part of the paper's own solution. Existing named hybrids (SMOTE-ENN, SMOTE-Tomek) used as plain preprocessing I excluded as E1.
  Applying an existing generator versus proposing one: I excluded R19912 (a standard GAN inside an IoT security framework) and R07599 (existing SMOTified-GAN with bagging ELM), marked R16861 (autoencoder latent interpolation) unsure, and included R12141 (a conditional DDPM that is the core of the method).
  Tuning SMOTE: I included R05335 (an improved, faster SMOTUNED; I1-other, tagged comparison) and excluded R05173 (SMOTE tuned by Bayesian optimization inside a semi-supervised pipeline, E1).
  R00645 (GMBoost): the title says "with over-sampling", but the abstract does not say whether the oversampling sits inside boosting.
  R02192 (GA-improved GAN oversampler): only "illustrated by a case study" and framed as anomaly detection.
  R01825 (cosine-similarity sampling): included on the assumption that it generates synthetic examples, which the abstract does not state.
- Language: I used E-LANG for R13602, R01869, R14671, R04432, R19686 and R05731. R14185, R02590, R20910, R19362 and R18199 have English abstracts but Indonesian or Turkish titles or metadata, so I judged them on content; the full texts may not be in English.

## batch072

batch 072: 200 of 200 records done; include 28, unsure 18, exclude 154
no records remain

Records to look at first:
- Low confidence: R08137 (include; ECG paper says it proposes new oversampling methods, mechanism not described); unsure R08120, R00256, R09594, R17616, R13876, R13757.
- I2 not stated in the abstract (clarification 2, unsure): R15954 (BFC-SMOTE, gains credited to "theoretical derivation"), R13900 (DBST), R21574 (ASMOTE-TDC module).
- Clarification 3, existing generator + existing cleaning/selection presented as new (unsure): R12108 (ADASYN+Tomek), R15543 (SMOTE+RUS), R15015 (SMOTE+Tomek), R10437 (CTGAN then SMOTEENN), R15184 ("improved SMOTE" + ENN).
- Not settled by the codebook: R17646 (unchanged SMOTE on autoencoder latent vectors, claimed as the contribution; unsure); R08120 (TNNLS ensemble running an unspecified oversampler on an optimized feature view; neither E1 nor E-NOGEN fits; unsure). Sampling-ratio optimisation: R02171 include (GA sets the SMOTE/GAN mix), R00233 unsure (DOE per-class proportions, synthetic or not unstated), R03901 E1 (AutoML picks an existing sampler in a case study).
- Where I drew the line on generators in domain papers: named off-the-shelf CTGAN applied = E1 (R08073, R08637); own generator presented as the contribution = include (R18039 CVAE, R13241 SMOTE-FraudGAN); undescribed "enhanced GAN" = unsure (R12617).
- Borderline includes (medium): R19750 (improved SMOTE-ENN inside a structural-engineering paper), R00069 (kRNN minority-outlier removal before SMOTE), R07137 (ADASYN per majority partition + ensemble), R03311 (SMOTE + clustering-improved undersampling to build a dynamic-ensemble pool), R05691 and R04457 (combinations of existing oversamplers), R10541 (t-SNE latent space + Gaussian noise), R00401 (bootstrap boundary synthesis; may synthesize for both classes).
- Language: E-LANG records with otherwise in-scope methods: R09040 (Chinese, VTO oversampler), R05025 (Chinese, CWGAN-GP). Full-text language worth confirming: R10846 (include, Korean society journal), R15015.
- No abstract: R00148 unsure (Comput Biol Med 2010, "A learning method for the class imbalance problem with medical data sets"); R01296 excluded E-REVIEW (Springer book chapter "Data Level Preprocessing Methods").
- Note: after a verbatim check of all quotes, the quote for R03311 was corrected in place in out/batch072_screened.csv (decision unchanged); all 200 quotes now match title/abstract text.

## batch073

batch 073: 200 of 200 records done; include 23, unsure 15, exclude 162
no records remain

Look at first (record number in batch order, rec id):
- Low confidence: #101 R01070 (unsure; spectrum-sharing under/oversampling scheme, not clear it makes synthetic examples) and #134 R14176 (unsure; "Majority Oversampling Technique" in a fraud paper, mechanism and novelty unclear).
- Codebook does not settle: #8 R12382 and #94 R21466 were included as a diffusion generator / new SMOTE variant (DAK-SMOTE) for supervised, labelled *anomaly detection* (E2 vs I1). #106 R09148 and #195 R00277 are unsure because the abstracts do not say whether the oversampling is synthetic or only replication/reweighting. #174 R10587 was excluded E-LANG (Chinese) although it proposes an in-scope SMOTE variant (RESMOTE). #20 R00228 (C-SMOTE) was included, but its venue looks like a Chinese-language journal (the language field says en).
- Clarification 1, purpose other than imbalanced classification (all unsure U-other): #41 R12716 PP-SMOTE (privacy, membership inference), #103 R09842 ProSOM (uplift/causal modelling), #114 R03601 (fairness de-biasing).
- Borderline includes (medium): #22 R01374 (new noise filters + SMOTE, education data), #131 R16801 (AE-CTGAN), #152 R06526 ("enhanced GAN", generator novelty thin), #194 R12434 (dynamic SMOTE+GAN sampling rates inside a fraud framework).
- Borderline excludes (medium): #1 R02498 (naive oversamplers devised only as baselines), #7 R06380 (LLM oversampling comparison; generative, text), #77 R21831 (existing CTGAN then SMOTE in a GNN paper), #175 R19368 (comparison workflow of existing generators), #189 R01312 (five image generators tested; novelty not stated).
- Other unsure (domain papers whose resampling may or may not be new): #38 R11035 BBOT, #55 R20894 Selective SMOTE, #123 R00889 K-Means+SMOTE, #154 R11781 GraphSMOTE in a stream ensemble, #180 R03065 I-SMOTE, #184 R05919 RoBERTa minority augmentation, #185 R17352 ANS-REA. #84 R05253 has no abstract (title "SMOTE, practical improvements").
- Front matter: #87 R05417 tagged front-matter-in-scope (lists "a Novel Oversampling Technique for Imbalanced Credit Scoring Datasets").

## batch074

batch 074: 200 of 200 records done; include 28, unsure 13, exclude 159
no records remain

Look at first:
- Low confidence: R21006 (no abstract; physics-informed casting defect model; unsure), R19324 (no abstract; LSTM Kp-index forecasting; excluded E1), R09614 (ECG: SMOTE plus a "novel waveform scaling augmentation"; is that an oversampler in scope?), R07802 (AdaBoost fraud paper using "Heron-Centroid SMOTE"; new or existing variant unknown), R00567 (PCA-based sampling; no evaluation named, unclear if it generates examples).
- Standard generator inside a domain pipeline, no novelty claimed, excluded E1: R09052 (VAE, rock burst), R22272 (CGAN, IoT intrusion). Settle whether vanilla VAE/GAN oversampling in domain papers is E1.
- Includes where an improved SMOTE is one component of a domain paper: R07820, R10718, R15196, R00596, R00998 ("SMOTE ASMO"), R01675 (EKSMOTE in stacking; may not be new here). Also R04546 (deep oversampling, generator type not stated), R02494 (one-point crossover generator), R08513 (graph GAN generating minority nodes), R02430 (DNOS: new denoising before ADASYN, read as "SMOTE with a new cleaning step").
- No multi-label code in the codebook: R07527 (ML-RUSMOTE) and R00830 (ML-SMOTE) coded I1-other.
- Clarification 1 (purpose other than imbalanced classification): R05838 (SMOTE for privacy-preserving anchor data), R09482 (MTGAN synthetic EHR, also targets uncommon diseases).
- Excluded on language only, otherwise in scope: R05659 (ACGAN oversampler), R00065 (ASMOTE), R07727 (BAEGAN), all Chinese. Indonesian titles with language "en" (R20096, R09658, R14285) were excluded E1 on substance.
- R02250 (ASSOM oversampler) extends the authors' earlier paper: E4 check at full text. R09289 has a garbled full-text abstract with no resampling content (E-NOGEN).

## batch075

batch 075: 200 of 200 records done; include 26, unsure 16, exclude 158

Look at first:
- Low confidence (unsure): R00125 (standard SMOTE + conformally modified-kernel SVM; generation unchanged, codebook does not settle classifier-level hybrids); R04786 (ROS inside bagging, OverBagging-like; ROS duplicates rather than synthesizes).
- Borderline excludes (medium): R22404 (existing conditional WGAN-GP applied to rare traffic classes; augmentation is the paper's focus, generator unchanged); R01797 (oversampling by retrieving real face images via action units, not synthetic); R17756 (intra-cluster SMOTE only combined in experiments); R01357, R12774, R09513 (existing resampling inside a named pipeline; check that NATE's "non-parametric oversampling" is not new).
- Borderline includes (medium): R05476 (icross-validation picks the oversampling amount; a wrapper, not a generator); R04710 (minor SMOTE allocation change); R14652 (boundary oversampling, generation not described); R20197 (LLM text augmentation; venue is a repository, check I3); R22267 (record says English but the journal, Power System Protection and Control, mostly publishes in Chinese; check E-LANG).
- Unsure, new or applied: R02891, R16634, R02821, R12540, R12701, R04426, R20758. Unsure, other: R20526 and R17211 (I2 not stated in the abstract), R17801 (privacy-preserving collaborative diffusion), R02807 (SMOTE interpolation for scRNA-seq imputation), R06755 (Bayesian-network generation for missing/small data), R12385 (diffusion generation for hyperspectral data, minority targeting unclear). No abstract: R09957 (title announces a novel SMOTE variant).
- Language: R04288 and R07283 excluded E-LANG (Chinese) although the content would meet I1. R01169 has a Korean abstract with record language en (excluded E1 anyway).

## batch076

batch 076: 200 of 200 records done; include 31, unsure 15, exclude 154

Look at first:
- Low confidence include: R19616 (IIoT intrusion model says it proposes an "improved SMOTE" but does not describe the change).
- Optimizer-tuned SMOTE in domain papers, marked unsure (the codebook does not say whether metaheuristic tuning of SMOTE parameters counts as changing how SMOTE is applied): R07593, R15478, R10748.
- Existing generator as the core of a domain paper, marked unsure: R18048 (DDPM, fraud), R03520 (GAN, aging bugs), R16680 (CycleGAN, medical image and tabular). Similar generators used only as one pipeline step were excluded E1 at medium confidence: R19098, R11103, R19284 (DP-GAN in federated learning, also privacy-motivated).
- Clarification 1 calls: R17982 unsure U-other (RF-Diffusion thesis, label scarcity, no classification). R22178 excluded E1 because it applies an existing WGAN-GP to unlabeled sleep EEG; it could also be read as U-other.
- Clarification 2: R20941 (PA-SMOTE preprint, only theoretical analysis named).
- Clarification 3: R05677 and R02194 unsure (existing generator plus Tomek links or ReliefF, presented as new). R08364 excluded E1 because ADASYN+RENN is a step, not the claimed contribution.
- Other unsure: R00888, R16077, R15748, R18488, R18515.
- Medium-confidence includes embedded in domain papers: R13822, R15289, R00826 (DySMOTE may be an earlier method), R19225, R20533, R11275, R07114 (weak evaluation statement), R06768, R18489.
- In scope but not in English (E-LANG): R01721 (Korean, CycleGAN tabular oversampler) and R04605 (Chinese, dynamic SMOTE with rotation forest).
- Document type: the codebook's I3 does not mention theses or book chapters (R22178, R17982, R15515, R17644, R20775, R09274). All were decided on other grounds, and none is an include.

## batch077

batch 077: 200 of 200 records done; include 32, unsure 17, exclude 151

Look at first:
- Cases the codebook does not settle: R07621 (theoretical analysis of the SMOTE sample distribution; no code fits, coded E-COMPARE + comparison, likely wanted elsewhere in the survey); R22380 (FERS, new entropy-guided duplication oversampler with no synthetic examples, coded E-NOGEN); R11598 (RL agent that picks among existing samplers, unsure U-other).
- Clarification 3 calls (existing generator + existing cleaning/selection): unsure R15465, R13406 (presented as novel but looks like plain SMOTE-ENN), R11499, R15201, R15834, R03327 (PCA-SMOTE); included because the abstract describes a change to generation: R10888, R05093, R07193.
- Clarification 2 (I2 not stated in the abstract): R20133 (LA-SMOTE, theory only), R05511 (also unclear novelty).
- GAN/diffusion borderlines: unsure R07329, R14647, R21724 (generator presented as the contribution, novelty unclear); excluded E1 at medium R04709, R17452, R22184 (existing GAN only applied); excluded E-NOGEN at medium R17561 (diffusion feature perturbation for contrastive learning). Medium-confidence includes: R08812, R04750, R18194, R13862 (DART, mechanism not described).
- Other low-confidence unsure: R06261, R14539, R07547, R04224; R06778 (no abstract, DDPM solar images).
- Latent-space oversampling inside domain frameworks, included at medium: R14678, R13560; also R04235 (improved ADASYN secondary to feature selection), R07530 (ROI perturbation oversampling).
- Excluded E-LANG but otherwise in scope: R14326 (Chinese, multi-discriminator WGAN oversampler).

## batch078

batch 078: 200 of 200 records done; include 23, unsure 17, exclude 160

Check first:
- Low confidence: R13330 (unsure). The title says it enhances GraphSMOTE, but the abstract describes only a new loss (ECC) replacing cross-entropy.
- Language conflict: R18985 (include, I1-generative). The language field is tr, but the title and abstract are English-only. Check the language of the full text.
- Codebook unclear on task or mechanism: R07661 (unsure; augmentation for aspect sentiment quad prediction, a structured task rather than classification), R03312 (unsure; Cross-Concatenation pairs instances instead of resampling), R11406 (include; Mixup-based minority augmentation for supervised anomaly classification, near the E2 line).
- Borderline includes, all medium: R04187 (KSMOTE fixes cross-validation after oversampling and may only be SMOTE inside folds), R15808 (oversampling ratio optimized with PSO/WOA/Optuna), R05497 (dynamic resampling with an attenuation rate; unclear whether it uses SMOTE), R05578 (HOUBC hybrid), R03918 (improved SMOTE with boundary cleaning).
- Two existing generators combined, coded as I1-hybrid, not as clarification 3: R19613 (GAN+SMOTE), R20483 (GPT-2+SMOTE), R11080 (SMOTE+CTGAN/TabDDPM).
- Clarification 3 sent to unsure: R00787 (DBSM), R07496 (USMOTE(r)), R09141 (IQRBU plus genetic oversampling), R12803 (ADASYN with bagging/boosting/stacking).
- Domain GAN oversampling, unclear if adapted: R06126 (CGAN IDS) and R16957 (edge IDS generator). Other unsure: R11176 (K-clusters SMOTE, maybe K-means SMOTE renamed), R01847 (SMOTE with noise), R02709 (parSMURF), R03000 and R08602 (abstract does not say whether synthetic examples are generated).
- No evaluation named in the abstract (clarification 2): R21496 (PE-SMOTE) and R17111 (SRA-SMOTE), both Zenodo preprints.
- No abstract: R14653 (unsure; title is a metaheuristic multiclass oversampler). R12001 and R05369 were excluded from the title alone (medium).
- Borderline excludes, medium: R12112 (existing simulated ECG mixed in by curriculum), R16754 (order of imputation and SMOTE), R19402 (GAN augmentation strategy benchmark).
- Front matter tagged front-matter-in-scope: R01516, R02917, R03856.

## batch079

batch 079: 200 of 200 records done; include 32, unsure 20, exclude 148
no records remain

Look at first:
- Low confidence: R00100 (exclude E-COMPARE, no abstract, title only); R05954, R00483, R00279, R09448, R05878 (unsure).
- Codebook does not settle: R09448 (SMOTE-Tomek sampling rate tuned by sparrow search: does tuning the amount count as changing how SMOTE is applied?); R05878 (SMOTE-Tomek-style generation used to test generalization, not to balance training); R05625 (excluded E-NOGEN: SSHR "oversamples" by pseudo-labeling unlabeled data, not synthesis); R08923 (dissertation abstract, I3 doubtful; HOVER graph oversampling).
- Borderline includes (medium): R21964 (saliency-guided mixup for tail-class images: augmentation or oversampling?), R16720 (tiered class-dependent SMOTE amounts, simple heuristic), R03641 (log-ratio oversampling, synthetic generation not confirmed), R10190 and R12206 (domain papers with an "improved" ACGAN / SMOTE, improvement barely described), R00224 (SMOTE in bagging, close to SMOTEBagging), R16464 (dynamic SMOTE in federated learning), R21784 (SMOTE plus adversarial-autoencoder filter), R02458 (k-means cluster-based over/undersampling), R02707 (MOKCCAS, garbled abstract, may duplicate MOKAS: E4 check).
- Borderline excludes (medium): R19895, R15174 (off-the-shelf WGAN / CGAN plus SMOTE in domain pipelines), R03742 (NNI plus SMOTE, task may be regression), R14586 (unspecified "modified SMOTE", record language Arabic), R01566 and R01931 (analyses of SMOTE / oversampling, coded E-COMPARE; useful background).
- R01861: abstract "proposes" Geometric-SMOTE but frames it as a tool for remote sensing; check whether G-SMOTE is introduced here (E4).
- E-LANG records that would otherwise be in scope (Chinese full text): R10478 (DPAS), R02265 (improved MSMOTE), R04237 (improved Borderline-SMOTE), R00104 (kernel SMOTE).

## batch080

batch 080: 200 of 200 records done; include 35, unsure 20, exclude 145
no records remain

Look at these first:
- Codebook does not settle: R05190 is marked RETRACTED but otherwise meets I1-I3 (SMOTE-PSOEV). Included with low confidence.
- Low-confidence unsure: R19405 (class-conditional DCGAN for crop images; new or applied, and aimed at data scarcity more than imbalance); R20631 (two-stage NTL detector, SMOTE only in stage 2 to cut synthetic data: a multiclass scheme or plain use?); R02291 (ADASYN for multi-label AMP types; labelling of synthetic multi-label instances is raised but not explained); R00815 (online ELM with under/over-sampling options); R00552 (oversampling ensembles, synthetic not stated, Korean-language venue); R13355 (grey wolf optimisation of samples after sampling); R21967 (ChatGPT minority reviews in a shared task); R19111 ("novel Dual-Balanced SMOTE" for class and gender).
- Abstract says nothing on whether oversampling is synthetic: R04153 WOOLASVM is unsure, but R19453 GDDSAD (oversampling inside AdaBoost) and R06514 (bidirectional sampling) are included with medium confidence. Check that these are treated alike.
- Borderline excludes (medium): R15341 (ADASYN rates tuned by SSA, treated as tuning); R14247 ("Stratified SMOTE" incorporated in an IDS framework); R17361 (KNN imputation + CBLOF + SVMSMOTE pipeline); R09508 (existing sparse autoencoder used for augmentation); R20982 (compares distance metrics inside SMOTE, coded E-COMPARE); R05686 (adversarial cost-sensitive classifier, E-NOGEN).
- Borderline includes (medium): R00084 (SMOTE on Biased-SVM support vectors), R00292 (SMOTE plus random subspace), R00640 (OVA/OVO + SMOTE on MapReduce), R04824 (improved SMOTE inside a credit-risk model), R09953 (oversampling of noise-purified time series), R19226 (LLM feature-guided text augmentation), R02854 (search-based augmentation feeding PGGAN), R18469 (diffusion samples used unlabeled for pretraining).
- Possible non-English full text although the record says en: R00084 (likely Chinese journal), R10048 (Korean J. Applied Statistics), R00552 (Korean venue).
- Rule-based unsure: R17110 CSM-SMOTE and R18111 CR-SMOTE (I2 not stated); R21537 (diffusion augmentation for covariate shift) and R11523 (generator for survival calibration and privacy) are U-other because they serve another purpose.
- Front matter tagged in scope: R22293 (hybrid VAE-Transformer multiclass oversampling), R04053 (deep oversampling for acne), R00451 (SMOTE with ensemble filtering).

## batch081

batch 081: 200 of 200 records done; include 28, unsure 17, exclude 155

Look at first:
- Low confidence: R13285 (unsure; graph contrastive learning that "expands" minority representations, SMOTE only in keywords, unclear whether any samples are synthesized).
- Borderline includes: R15849 (VAE oversampler with modified loss inside a supervised "anomaly detection" classifier; E2 vs include), R17700 (class-conditional TabDDPM in a domain paper; may be largely standard TabDDPM), R16439 and R08794 (hybrid resampling frameworks; oversampler not named), R02326 (SMOTE inside online SAM-kNN; main novelty is the downsampling method), R00219 (E-SMOTE, two-sentence abstract), R15192 (GAN + SMOTE chained), R09151 (K-means + VCIR; clarification 3 vs change to generation).
- Borderline excludes, existing generator applied in a domain (E1, medium): R04781, R08903, R17806, R19336, R04010, R13270. Other medium E1/E-NOGEN calls: R00677 (replication-based oversampling in bagging, E-NOGEN), R13743 (EbSmoT), R12746 (ASV-SMOTE), R17580 (Partial SMOTE ratios), R02666 (OSS+SMOTE in an IDS), R15138, R03042, R14077 ("proprietary" SMOTE step). No-abstract records excluded on their titles: R13403, R14783.
- Not settled by the codebook: Indonesian titles with English abstracts (language field en) were coded on content (R11339, R20747, R17306, R20098, R09260, R03788), and only R18646 (Indonesian abstract) was coded E-LANG. R04328 is excluded E-LANG but proposes an improved MDSMOTE (Chinese). R05434 (SMOTE ratio searched jointly with feature selection) is unsure. R00217 is front matter whose imbalance titles do not generate synthetic examples, so it has no front-matter-in-scope tag.

## batch082

batch 082: 200 of 200 records done; include 26, unsure 19, exclude 155

Look at first:
- Only low-confidence exclude: R16125 (no abstract; title names an attention random forest for small-sample wind turbine fault diagnosis, coded E-NOGEN). Low-confidence unsure: R16145, R02228, R18163, R13404, R03116, R01738, R16163, R09338, R11093.
- Not settled by the codebook: does tuning SMOTE's oversampling amount or k count as "changing how SMOTE is applied"? R02465 (TH-SMOTE picks the rate by G-mean) and R03116 (swarm optimizer tunes rate and k) are both marked unsure.
- New hybrid over/undersampling methods whose abstracts never say the oversampling is synthetic: R00980 (DBCS), R00466 (Neurocomputing 2014), R20717 (OHSEC). All unsure.
- Oversamplers built for detection or segmentation rather than classification (clarification 1): R02563 (aerial vehicle detection), R04499 (medical image segmentation), R01738 (point cloud segmentation). All unsure.
- I2 in doubt: R18033 CC-SMOTE gives only theory (unsure per clarification 2). R19249 FC-SMOTE was included because its abstract claims gains on constrained datasets, but it names none.
- Borderline includes: R01125 SMOTE-GPU (I1-other; a GPU implementation, not a change to generation), R21854 (LLM counterfactual minority generation inside a stance-detection study), R07055 (LR-SMOTE is part of the method but may come from earlier work), R16462 (SUPERAUG noise injection plus SMOTE), R03457 (envelope network; synthetic generation is implied, not stated).
- Language: R00152 was excluded only for E-LANG (Chinese) but is otherwise in scope (improved SMOTE neighbor selection plus NCR). R08260 (Chinese) and R15926 (Thai) were coded E1 because E1 also applies. R03946 (GBL-SMOTE, included) is in a Korean journal, so check the full-text language.
- Metadata: R05299 has a title about perovskite solar cells but an abstract about credit card fraud; it is excluded either way. R14005 and R11148 are marked retracted (both E1).

## batch083

batch 083: 200 of 200 records done; include 30, unsure 16, exclude 154
no records remain

Look at these first:
- Low confidence: R18153 (unsure). A CNN intrusion system "addresses unbalanced datasets" and is compared with systems that use SMOTE, ADASYN, ROS and GAN, but the abstract never says how it balances the data.
- Retractions (the codebook does not cover them): R21539 is a 2026 retraction notice for a 2022 PSO/Egyptian-vulture SMOTE article; I excluded it as E-REVIEW (editorial) with the tag front-matter-in-scope. If the original article is in the corpus, it needs a retraction flag. R05192 is itself a retracted article (GA+kNN oversampler). It meets I1-I3, so I included it as I1-other.
- E2 or clarification 1: R04138 (NNI+SMOTE augmentation for a rubber tensile-stress model) and R22154 (cWGAN-GP augmentation for snow-depth estimation) are regression-only, so I excluded them as E2. Clarification 1 (a generator built for a purpose other than imbalanced classification goes to unsure) could be read to cover them.
- In scope except for language (E-LANG, Chinese): R13328 (GLRD-GAN graph oversampler) and R02157 (WGAN oversampler for electricity theft).
- Borderline includes (medium): R19227 (LLM prompt augmentation in a fake-news paper), R02786 (DCGAN oversampler for crash data), R01182 (safe-screening undersampling plus an unnamed oversampler), R09549 (fuses the outputs of several SMOTE variants, then SMOTEBagging), R17592 (enhanced-PSO oversampler inside a stream ensemble; the oversampler may come from earlier work), R00023 (SPSO may have been introduced in an earlier paper), R00571 (spatiotemporal oversampling for background subtraction).
- Borderline excludes (E1, medium): R03550, R02004, R05388, R02416, R07524, R07367. Each applies existing resampling in a domain pipeline, but wording such as "proposed", "adopts" or "novel approach" could hide a change to the generation step.
- Unsure because I2 is not stated: R21458, R16552, R18484 and R20121 are 2026 Zenodo preprints of SMOTE variants that report theory only. All four abstracts are written in the same style, so they may be one series.

## batch084

batch 084: 200 of 200 records done; include 30, unsure 16, exclude 154

Look at these first:
- Low-confidence unsure (the codebook does not settle these): R15882 (new KNN classifier + existing R-SMOTE; does the weighted distance change the oversampling?), R20622 (multi-teacher distillation over existing resamplers), R07656 (AdaFNDFS, "differential sampling rate", unclear if it generates), R02478 (Augagging: oversampling learner inside bagging), R03516 (theory only: oversampling as weighted classification, bound for the re-balancing amount), R04379 (fuzzy-clustering SMOTE for protected-attribute bias, purpose is fairness), R04172 (I2 not stated; the "novel" oversampler reads like ADASYN), R11290 (no abstract; SMOTE-RF "guided by hydrogeochemical constraints"), R05525 (ROS+NCL hybrid; ROS duplicates, so I1 is doubtful), R01316 (churn model using EMOTE; EMOTE is proposed in R00930, possible E4 or E1).
- Medium-confidence unsure: R08932 (SMOTE+NearMiss on stroke, clarification 3), R14007 ("improved hybrid sampling" in a civil-engineering paper), R13697 ("tailored" CTGAN), R17671 (CE-SMOTE, I2 not stated), R05100 (existing oversamplers applied only to the short-ORF subgroup), R00168 (SMRBF: SMOTE inside a memetic algorithm, new or applied?).
- Borderline includes (medium): R03537 HCBST and R10052 SMOTE-kTLNN (clarification 3 edge cases; I read the oversampler or filter as new), R21742 and R21359 (graph embedding-space oversampling; "anomaly detection" here is supervised node classification, so not E2), R03745 (P2PK-SMOTE, peer-to-peer), R16696 (adaptive LM/dictionary text augmentation), R20204 (LLR-SMOTE Zenodo preprint, evaluation stated only vaguely), R00930 (EMOTE, mechanism not described), R20712 (CAS-NR in a domain paper), R08457 (stream multiclass oversampler), R07533 (per-class cluster oversampling in a DDoS paper), R04752 (K-CGAN), R08028 (BES-optimized SMOTE with a privacy framing; I read the purpose as imbalanced classification).
- Borderline excludes (medium): R04129 (re-proposes SMOTE-ENN; read literally, clarification 3 would make it unsure), R08080 (ADASYN inside a drift ensemble for streams), R05055, R05403 and R15520 (existing CTGAN, WGAN or GAN applied as is), R02084 ("Ensemble SMOTE" is a SMOTE-then-bagging pipeline), R06747, R02248 (ISPL selects samples and generates none), R02362, and the no-abstract records R10771, R20378, R11128 and R08205.
- Language: R04967 and R03828 are excluded as E-LANG (Chinese). R20750, R21262, R20938, R11364 and R09267 (Indonesian titles) and R18656 (Chinese journal) are listed as English and were coded on content; their full text may not be English.
- R07357 is proceedings front matter that lists an oversampling paper (tag front-matter-in-scope). R07682 is typed "Review" but is a research article (E1).

## batch085

batch 085: 200 of 200 records done; include 27, unsure 19, exclude 154

Records to look at first:
- Low confidence (all unsure): R16422 (clonal selection: classifier or generator of minority samples?), R07696 (CNN pretrained on SMOTE data then fine-tuned on real data: does staged use count as changing how SMOTE is applied?), R22102 (existing SMOTE-Tomek/SMOTE-ENN on ResNet features presented as the contribution), R05221 (zero-shot feature generation, clarification 1), R02386 (conformational oversampling of molecules; authors say "without artificial samples"), R03637 (unspecified image-based oversampling in an IDS CNN), R01509 (case study that "introduces an over-sampling approach"), R09449 (own method not described in the abstract).
- Borderline includes (medium): R01755 (SMOTEBagging with only the base learners changed), R05551 (SMOTE inside AdaBoost plus APSO tuning), R15906 (K-CGAN called "proposed novel" in a comparison-style paper; possible earlier version), R13793 (ABC-based sampler "utilized"; may be existing), R11644 (bias correction for training on synthetic data, not a new generator), R01438 (ordinal oversampling as a side contribution of a melanoma paper), R16757 (VAE oversampling in a tractography paper).
- Cases the codebook does not settle: clarification 3 unsures R09587, R01927, R02972, R03534, R09473; R13433 claims a "novel" resampler that resembles existing SVM-SMOTE; I2 not stated R05793, R21495 (DD-SMOTE); privacy purpose R09835.
- Medium-confidence excludes worth a glance: feature selection or weighting plus unchanged SMOTE coded E1 (R07466, R00438, R06591); R19450 (new outlier filter before SMOTE-ENN, coded E-NOGEN, tagged comparison for its leakage findings); R09394 (no abstract, application title).
- Format notes: R15931 (Greek title, thesis) and R13914 (Indonesian title) have language "en", so they were excluded on content (E1), not E-LANG; R20871 is a thesis; front matter with in-scope titles: R07355 (ACTIVE SMOTE), R01896 (modified radial-based oversampling).

## batch086

batch 086: 200 of 200 records done; include 17, unsure 16, exclude 167
no records remain

Records to look at first:
- Unsure, I2 not stated (new SMOTE variants with theoretical analysis only, all Zenodo preprints): R17975 CB-SMOTE, R21522 ME-SMOTE, R20469 Manifold-aware SMOTE.
- Unsure, low confidence (unclear whether the proposed balancing generates synthetic examples or is new): R01649 cluster-heads sampling, R01351 soft/hardsampling, R00656 oversampling to target IR, R04890 ROS-DBSCAN, R01588 cell-based oversampling, R09604 PSO data balancer, R15296 adaptive sampler selection, R13815 "modified SMOTE" in energy forecasting (also regression vs classification unclear). No abstract: R02526, R21291.
- Unsure, new-or-applied (clarification 3 and similar): R11008 filtering+ADASYN+ENN, R05834 CLUBS anomaly removal + ADO oversampling, R20658 MWMOTE-MLLM (modified or plain MWMOTE?).
- Medium-confidence includes where the oversampler sits inside a domain paper: R17986 Borderline-PC SMOTE bounded to process limits, R15069 DepAug speech decoder, R19707 cGAN-SMOTE ICD-Balancer (survival-analysis context), R20615 JSO oversampler, R01053 improved SMOTE + K-means, R02131 WSMOTE inside bagging, R10275 Argo error-sample oversampler.
- Borderline excludes: R02626 K-means+SMOTE (E1), R17657 SVM-SMOTE+NCL module (E1, clarification 3 arguable), R12549 K-SMOTE/K-ADASYN (E1), R16221 GAN built from earlier methods (E1), R18511 cluster-wise minority injection without synthesis (E-NOGEN), R14346 MSDL mechanism not stated (E-NOGEN), R14444 "Novel Sampling Methods" title but abstract is a comparison (E-COMPARE), R09625 climate parameterization (E2).
- Not settled by the codebook: R15141 is a Chinese-language paper proposing a covariance-based "global cost SMOTE" (coded E-LANG, otherwise in scope). Records with non-English language metadata but English titles/abstracts (R02486, R06576, R15464, R00131, R01851) were coded on content (all excluded on content, language noted in the reason); records with Indonesian titles were coded E-LANG.

## batch087

batch 087: 200 of 200 records done; include 20, unsure 18, exclude 162
no records remain

Look at first (no low-confidence rows; 29 medium):
- Likely includes held back by the codebook rules: R00702 SMOTE-IPF (well-known SMOTE + IPF filter; clarification 3 sends it to unsure because the filter is an existing step, although I1 names "SMOTE with a new cleaning step"); R21023 (no abstract, title names a new adaptive neighbor oversampler); R21602 RVR-SMOTE (new variant, but the abstract names no evaluation, so clarification 2 applies).
- Generator in a domain paper, new or just applied? Marked unsure: R21822 (self-attention GAN), R19470 (GAN, ECG emotion), R18712 (cGAN, IoT IDS), R22071 (LoRA diffusion; also a detection task). Included at medium: R02400 (DAITD GAN) and R18879 (Pulsar-WRecon WGAN-GP). Please check this line is drawn consistently.
- Existing generator plus an existing step (clarification 3) or a vague change to generation: R00350, R02992, R02034 (multilabel), R00252 (multi-class), R18047 (graph SMOTE), R18948, R11037, R04529 (only keywords name the oversampler), R12677.
- Purpose or task outside imbalanced classification (U-other): R06343 (GAN for scarce HAR data), R19302 (diffusion fine-tuning, judged on image fidelity only).
- Medium-confidence includes: R22367 (graph oversampling module), R00905 (multi-kernel over-sampling), R02887 (graph-based RWO-Sampling), R04814 (oversampling in a deep embedding), R05210 (SASMOTE; it treats CSI localization as classification).
- Other: R11625 and R09626 would meet I1-generative but are in Chinese (E-LANG). R06052 is an erratum tagged front-matter-in-scope; check that the original oversampling article (MTAP 2022, semiconductor lines) is in the corpus. R20808 and R21084 were excluded from their titles alone (no abstract).
- Coding note: domain studies whose stated aim is to compare existing balancing methods are E-COMPARE (tagged comparison); those that only use a resampler as one step are E1.

## batch088

batch 088: 200 of 200 records done; include 28, unsure 15, exclude 157
no records remain

Look at these first:
- Low confidence: R07023 (unsure; SMOTE + k-means cleaning on Pima, sold as originality: E1 or clarification 3?), R12213 (unsure; SMOTE then roughly balanced bagging of LSTMs for IDS), R04839 and R02334 (unsure; domain papers whose "proposed" oversampling step is not described), R03925 (unsure; SGBBA not described, keywords hint undersampling-bagging), R09848 (include; "enhanced SMOTE-Tomek" in PSC-Net, the change is not described, could be U-new-or-applied instead).
- Codebook does not settle: R07987 is a theory-only paper on SMOTE asymptotics (excluded as E-NOGEN for want of a better code; may matter for a theory section). R11185 is a book chapter in an edited volume (I3 fails but no exclusion code exists for document type; coded E1). Other book chapters (R20254, R20782, R17226, R12957) were excluded on E1 anyway.
- Borderline includes (medium): R01545 (GMM undersampling + SMOTE with sampling-factor allocation), R05774 (NMOTe, generation not described), R19244 (adversarial generator as one module of a federated RL fraud system), R02086 (existing Markov/LSTM text generators used as oversamplers; compare R12147, coded unsure), R08983 (SPCAGAN, partly a confidentiality/data-scarcity generator, framed as anomaly detection).
- Language: R00712 (Journal of Computer Applications) and R13442 (Korean Society for Quality Management) are metadata "en" but the venues may publish in Chinese/Korean. R00265 (excluded E-LANG, Chinese) proposes ODR undersampling + Borderline-SMOTE.
- Clarification-rule unsures: R17105 and R21743 (Feature-drop SMOTE and SI-SMOTE, Zenodo preprints, theory only, rule 2); R13147 (privacy-preserving federated DP-WGAN, rule 1); R11455, R03253, R08985 (existing generator + existing cleaning/selection, rule 3); R07125 (DA-SMOTE, new or existing?), R06403 (FuzzyCSampling, oversampling or not?), R17243 (no abstract; "oversampling framework for mitigating representation bias", possibly fairness).
- Exclusions worth a glance: R10750 ("SMOTE-based ensemble boosting", abstract reads as SMOTE preprocessing then boosting), R05154 (MSMM + BAG-SMOTE), R01295 (SMOTE + OSS on EDM, compare R07023). R01517 is front matter tagged front-matter-in-scope ("feature space oversampling technique for imbalanced classification").

## batch089

batch 089: 200 of 200 records done; include 22, unsure 12, exclude 166
no records remain

Look at first:
- Low confidence (unsure): R00981 (proposes "class specific scaling" next to a benchmark of SMOTE/ADASYN/CNN/OSS; abstract never says whether it generates examples), R02649 (video foreground "temporal and spatial oversampling", may not be synthetic generation), R04073 (RL + CGAN oversampling for intrusion detection, titled a comparative analysis; is the CGAN generation new?).
- Borderline includes (medium): R20170 (LLM + ConceptNet augmentation stated as a key contribution of a sexism-detection paper), R09954 (rumour detection, selective contextual augmentation with non-random seed choice), R19243 (FDCTGAN: unchanged CTGAN trained client-locally in federated learning), R11039 (AE-Multi-WGAN; GAN clearly generates samples but its use as oversampler is implied, not stated), R14299 (modified/weighted SMOTE, few details), R00475 (MapReduce-parallel NRSBoundary-SMOTE).
- Borderline excludes (medium): R17405 (existing TGAN + XGBoost "framework" on two domains), R07192 (STB "novel" SMOTE Tree Boosting reads as SMOTE then boosting), R01022 and R02032 (vague "synthetic samples"/"oversampling techniques" inside domain frameworks), R18733 and R06926 (no abstract, excluded E1 from title).
- Unsure by clarification 2 (I2 not stated): R20861 (Hash-space SMOTE), R16549 (selective class resampling). By clarification 3 or unclear novelty: R15210, R04645, R01611, R06892, R07771, R18284, R22039.
- Not settled by the codebook: whether parallelizing an existing variant counts as I1 (R00475); whether a learner that limits the influence of oversampled examples "changes how SMOTE is applied" (R22039); local oversampling inside federated learning (R19243 included where it is the contribution, R10768 excluded where it is a minor step). Domain papers comparing several existing resamplers were coded E1 with tag comparison rather than E-COMPARE; Indonesian-titled papers with English abstracts (R07888, R09266) were coded on content, Korean R04976 as E-LANG.

## batch090

batch 090: 200 of 200 records done; include 19, unsure 22, exclude 159
no records remain

Look at first:
- Policy question (codebook does not settle): domain papers whose proposed approach is a standard deep generator used as the minority oversampler, with no change to the generator described. Marked unsure U-new-or-applied: R12766 (CWGAN-GP malware), R01854 (GAN bearing faults), R13272 (GAN railway faults), R02903 (VAE social bots), R05395 (MCMC/GAN IDS). Excluded E1 because the generator is only a pipeline step or the paper is framed as an evaluation: R18996 (Stable Diffusion + LoRA), R08711, R06268, R07420. One rule for this group would settle all of them.
- I2 not stated in the abstract (clarification 2, theory-only Zenodo preprints of new SMOTE variants): R21500 PI-SMOTE, R17094 FCS-SMOTE, R16060 CBP-SMOTE.
- Low-confidence unsure: R00823 (HSDD; does it generate synthetic examples at all?), R04783 (existing RSMOTE inside a hybrid approach; language listed as id), R12938 (no abstract), R17213 (AMOP in skin cancer network), R12494 (hummingbird-optimized SMOTE), R13533 ("improved K-Means + SMOTE").
- I3 doubt: R00122 is a new clustering + genetic-crossover oversampler, but the venue (Jisuanji Gongcheng) is a Chinese journal; full text may not be in English.
- Clarification 1 (generator built for another purpose): R12011 (conditional ECG VAE for scarcity, privacy and imbalance), R04326 (WGAN feature generator for generalized zero-shot learning).
- Medium-confidence includes to verify: R09547 (MSMOTE is called novel; check that it is not an existing method), R14227 (MCOG-CCR is framed as anomaly detection but evaluated with multiclass MAUC), R11592 (new undersampling + SMOTE in a multi-label ensemble, coded I1-hybrid), R06692 (augmentation-based tail oversampling for long-tailed images), R01756 (distributed SMOTE; no datasets named), R16710, R04926, R11119.
- Metadata issues: R05401 has a title that does not match its abstract; R11351 is in Indonesian (coded E1, E-LANG also applies).

## batch091

batch 091: 200 of 200 records done; include 23, unsure 21, exclude 156
no records remain

Look at these first (record numbers are batch positions):
1. Not settled by the codebook: an existing generative model is used as the oversampler inside a domain pipeline, with no stated change to the generator. I marked all of these unsure so they can be decided together: R22240 (45, WCGAN-GP fraud), R16664 (69, AC-WGAN-GP transcriptomics), R04502 (167, ACGAN features, brain tumor), R15195 (198, DCGAN intrusion detection), R08904 (12, GPT text, also a book chapter).
2. Language doubt: new SMOTE variants that meet I1 and I2, and the language field says English, but the venue or a Chinese title suggests a Chinese full text: R00339 (121, S-SMOTE), R00247 (148, ISMOTE), R10651 (131, MC-LDWO). Also R13097 (2, excluded E1) has a bilingual Chinese abstract.
3. I3 doubt about document type: R01596 (156, PhD thesis proposing HSBagging hybrid-sampling bagging), R08904 (12, book chapter).
4. Clarification 1, generator built for fairness: R06679 (10, Fair-GAN), R13301 (35, CA-GAN, representation bias). Clarification 2, I2 not stated (Zenodo preprints with theory only): R18543 (86, DD-SMOTE), R17103 (89, AI-SMOTE).
5. Distributed SMOTE implementations, which may or may not count as changing how SMOTE is applied: R00549 (11, MapReduce, framed as an analysis), R01544 (66, Spark).
6. Borderline excludes: R21566 (22, UCAS-SMOTE) and R21531 (81, CASB) have named resampling steps inside domain frameworks but are not presented as the contribution (E1). By contrast, R15752 (169, CK-means-CNN) was marked unsure because its resampling is part of the model name. R21754 (197, SGGA) replicates support vectors instead of synthesizing and is benchmarked against SMOTE and MWMOTE (E-NOGEN). R14420 (190, authors re-apply their own NCLWO to defect prediction, E1). R10105 (116, no abstract, low confidence E1).
7. Borderline includes (oversampling placed inside ensembles, or a less detailed variant): R02412 (25, SMOTE on the DES-KNN DSEL set), R02598 (15, KA-Ensemble), R06156 (157), R02236 (140, multiclass hybrid oversampling), R15198 (107, Gaussian G-SMOTE), R04148 (42, random-walk text generation).
8. Front matter: R19985 (56) lists "GANified-SMOTE with Latent Factor", tagged front-matter-in-scope.

## batch092

batch 092: 200 of 200 records done; include 16, unsure 19, exclude 165

Records to look at first:
- Low confidence: R19475 (no abstract; SMOTE in epidemiological studies, could be a tutorial, an application or advice on applying SMOTE); R03096 (imbalanced deep forest; abstract does not say whether its units oversample).
- Clarification 3 borderline, excluded as E1 because the combination is a preprocessing step in a domain pipeline: R09571 (SMOTE+RUS "combinatorial balancing algorithm", diabetes), R21832 (phased downsampling+cleaning+oversampling, intrusion detection), R03948 (SMOTE-ENN with improved META-DES), R11199 (SMOTE-ELNGDI), R03533 (SMOTEXGBoost); in each case SMOTE may sit inside the ensemble, which would make it I1-hybrid.
- Includes at medium confidence: R21844 (RBStack, random-balance SVM-SMOTE in stacking), R09761 (modified SMOTE for binary variables in a domain study), R16718 (trust-stratified augmentation in semi-supervised RF), R06455 (ASMOTE-ENN; "adaptive SMOTE" may already exist, which would make it clarification 3 unsure).
- Unsure because I cannot tell new from applied: R11589, R04904, R03799, R19554, R13710, R01692, plus R05514 (SMOTEOSS, clarification 3).
- Not settled by the codebook: language (R13563 has a Korean abstract but English metadata; R01541 is from a Korean venue; R08053 and R10219 are excluded E-LANG but would otherwise be in scope); book chapters and I3 (R19388, R03945, both unsure because I2 is not stated); R14782 (PhyloMix, general augmentation, clarification 1); R21899 (SB-SMOTE, theoretical analysis only); R00893 (excluded E-COMPARE, but the abstract calls DyS-MLP "proposed").
- No abstract, but the title names a new oversampler: R06831 (NSOT), R11258 (functional-data oversampling), R19381 (G-ADASYN), R11429 (multi-task GAN), R01541.

## batch093

batch 093: 200 of 200 records done; include 21, unsure 18, exclude 161
no records remain

Records to look at first:
- Low confidence: R04831 (book chapter proposing VDB-SLSMOTE, evaluated on gearbox data; meets I1 and I2 but not I3, and no exclusion code covers document type, so unsure); R05184, R06402, R16521 (unsure; cannot tell whether the resampling is new).
- Cases the codebook does not settle: R00455 and R00777 (existing resampling plus a new twin SVM presented as one method, sent to unsure); compare R09906 and R00824 (SMOTE unchanged before a tuned or new classifier, excluded E1). R00161 (2010 book chapter, tutorial-style, coded E-REVIEW for lack of a document-type code).
- Oversampling that may not synthesize: R04003 (random oversampling schemes for hierarchical classification, E-NOGEN); R02158 and R05076 (new multilabel and multiclass balancing methods, unsure); R06426 (GraphSR pseudo-labels real unlabelled nodes instead of synthesizing, E-NOGEN). The includes R05163 and R00227 do not state whether their oversampling is synthetic.
- Possibly new resampler inside a domain paper, excluded E1 at medium confidence: R08343 (WSMOTE), R04200 (weakly supervised oversampling), R12251 and R03518 (off-the-shelf WGAN variants).
- Clarification 3 unsures that could be I1-hybrid: R04160 (SMOTE-RUS-NC embedded in a balanced random forest), R01858, R13444.
- Other: R04166 COSMOTE (I2 not stated in the abstract); R05283 (no abstract; title is a critique of oversampling, excluded E-REVIEW); R02921 (proceedings front matter, tagged front-matter-in-scope).

## batch094

batch 094: 200 of 200 records done; include 25, unsure 14, exclude 161
no records remain

Look at these first:
- Low-confidence unsure. The abstract does not say whether the oversampling creates synthetic examples or only copies them: R19859 (neighbourhood oversampling online bagging), R06508 (CRD; also framed as anomaly detection), R00928 (OSIDL), R00477 (boundary-ratio resampling). New or merely applied: R05500 (SeqGAN/AC-GAN for security logs), R08245 (a "combined resampling technique" called new). No abstract but the title centres on class imbalance: R05866, R13217, R06379.
- Four 2026 Zenodo preprints that name only theoretical support (clarification 2, unsure): R19455 Graph SMOTE (its text may be a repost of GraphSMOTE, WSDM 2021; check E4 at full text), R21499 CD-SMOTE, R21452 RF-SMOTE, R21638 SD-SMOTE.
- Borderline includes (medium confidence). A SMOTE variant inside a domain model: R05506 SMOTE-TS, R05648 Weighted SMOTE, R16740 per-class adaptive SMOTE allocation. Thin method detail: R07432 "dominant SMOTE". Graph/embedding generation close to GraphSMOTE: R08925 GraphSmin. Hybrids: R10733 KSMOTE (Kalman filter treated as a new cleaning step), R18622 and R02500 (SMOTE inside ensembles), R20089 KG-CTGAN (clusters steer CTGAN), R07267 (three-stage time-series sampler), R00820 (MWMOTE with BIRCH). Other generators: R02438 (image compositing), R06196 (GPT-3 prompts), R10505 GPEA (garbled metrics, obscure venue).
- Borderline excludes. R04188 uses SMOTE-P for count regression; coded E2, though clarification 1 (purpose other than classification) could make it unsure. R16647 SMOTified-GAN "tailored" to Alzheimer data; R18544 two-level NN-interpolation+ADASYN in a federated IDS; R01567 SMOTE before AdaBoost; R08351 SMOTE+VAE inside DeepPull. All coded E1.
- Cases the codebook does not settle. There is no code for off-topic records: R01590 (health insurance, no abstract) was coded E1, and R21609 (no abstract, new network) E-NOGEN. Theses: R02411 (coded E1) and R00263 (E-COMPARE). Indonesian- or Korean-language papers listed as English were coded on content, not E-LANG: R21266, R20926, R14481, R14696, R01087. Front matter with in-scope titles: R04795 (SDDSMOTE) and R07353 (GM4OS).

## batch095

batch 095: 200 of 200 records done; include 27, unsure 13, exclude 160
no records remain

Look at first:
- Low-confidence unsures (existing generator or step presented as a method, clarification 3): R05524 FHR-KNN hybrid resampling; R13353 SMOTE+ADASYN+ROS "combined" method; R14622 synonym replacement + oversampling; R05289 ENN then SMOTE then SVC; R15788 unspecified "improved SMOTE"; R12012 cluster-wise CGAN; R11823 C3GNN (Mixup in every subclass after splitting majority classes, not minority-specific).
- I2 not stated in the abstract (unsure U-other): R17123 IR-SMOTE, R21011 PF-SMOTE, R02383 COSM. R10871 has no abstract (ADASYN + SVM undersampling, two-stage).
- Medium-confidence includes to confirm: R06503 CSMOTE (is it new compared with existing cluster-SMOTE?); R09322 local resampling for LWNB; R10487 AEKS K-Means SMOTE in a stream ensemble; R22312 kernel thinning with SMOTE variants; R12883 CycleGAN-M for disease detection (the task is object detection); R08532 PEGASUS/back-translation minority text; R21449 REPEAT autoencoder oversampling; R09557 Gaussian pseudo-feature oversampling in continual learning; R00239 one-class-SVM + SMOTE SVM ensemble; R00873 ISBA swarm-tuned SMOTE; R21567 log-interpolated SMOTE targets (I1-multiclass).
- Cases the codebook does not settle: R08048 (ROS replaces RUS inside ensembles) and R21450 RSFR (a new oversampler that explicitly generates no synthetic examples), both excluded E-NOGEN. R07071 NaN-Bicluster SMOTE is a new variant excluded only as E-LANG (Chinese). R04548 is off-topic (signal oversampling ratio), coded E-NOGEN for lack of an off-topic code.
- Medium-confidence excludes: R16609 noise-based sampler in a solar-flare evaluation; R22134 density-aware Cluster-SMOTE+ENN inside an IDS; R18905 ChatGPT-generated images; R09134 AugOS-CNN; R17621 SMOTE-variant + GAN augmentation in a credit pipeline; R01510 SMOTE before stacking.
- Front matter with in-scope titles: R00452 (ANNPR 2014), R00716 (PAISI 2016), R07354 (NCTCS 2023, Region-SMOTE).

## batch096

batch 096: 200 of 200 records done; include 30, unsure 18, exclude 152

Records to look at first:
- Low confidence. Excludes with no abstract, decided as E1 from the title only: R08662, R16803, R13848. Unsure: R01956 (NILM appliance method compared with SMOTE; unclear whether it generates samples), R04211 (wTLCL-O has an unnamed oversampling strategy), R09245 (no abstract; iterative stacking for imbalance).
- Medium-confidence includes that could be challenged: R07130 (PSMOTE is one component of a domain framework), R05494 (layer oversampling may duplicate samples rather than synthesize them), R02523 (HIBoost puts SMOTE inside boosting, but the novelty is the hubness weighting), R03200 (16 DE strategies; could be read as a comparison), R08617 (Thai text oversampling by keyword removal and synonym replacement), R18448 (latent node interpolation inside a GCN).
- Medium-confidence excludes: R00468 (standard SMOTE plus cost-sensitive SVM), R03184 (standard SMOTE on BERT embeddings for PoS tagging), R13660 and R06412 (existing GANs applied), R06004 (one ensemble per oversampled copy, framed as a comparison), R04008, R16458, R11559, R22002.
- Cases the codebook does not settle:
  - R18367 is a book chapter. I3 names only journal papers, conference papers and preprints, and no exclusion code covers book chapters, so it is marked unsure.
  - R03489 and R07874 are multi-label oversamplers, coded I1-other because the codebook names multiclass schemes only.
  - Generators not based on SMOTE coded I1-other: R06673 (adversarial samples with triplet loss), R19382 (GA crossover and mutation), R00066 (synthetic protein sequences).
  - R17937 has language "ar" but an English title and abstract. It is coded E-LANG, and E1 would also apply.
  - R14482 and R20931 have Indonesian titles and language "en". Both are coded E1.
- Unsure under clarification 2 (no evaluation named in the abstract; all Zenodo preprints): R18949, R17112, R19293.
- Unsure under clarification 3 (existing generators combined, change to generation not shown): R06575, R05406, R00388, R09155, R16356, R18367.
- Unsure because a named variant in a domain paper may be new or existing: R17193 (DC-SMOTE), R12094 (enhanced SMOTE), R08179 (SMOTE-based multiclass balancing), R16160 (no abstract; AE-WGAN-HCBOU).
- Unsure because the abstract does not say whether synthetic examples are generated: R11476 (ART), R06297 (EPS).

## batch097

batch 097: 200 of 200 records done; include 19, unsure 18, exclude 163
no records remain

Look at these first:
- Cases the codebook does not settle: R01064 (SmoteND/SmoteNDBoost, SMOTE extended to imbalanced regression: clarification 1 says unsure, E2 says exclude); R00075 (2008 multiclass scheme using random over/undersampling only: I1 lists multiclass oversampling schemes, but nothing synthetic is generated; low); R06131 (AFCM-SMOTENC for association-rule mining, not classification; low).
- Language: R00240 (included, AdaBoost-SVM-OBMS, 2011) has English metadata but the abstract looks like the Chinese journal Computer Engineering and Applications; check the language at full text. R13574 was excluded under E-LANG (Chinese) but would otherwise be a generative include (SDCGAN).
- Methods that meet I1 but whose abstract names no evaluation (clarification 2): R17444 (Attention-route SMOTE, preprint), R06482 (FFSMOTE for streams).
- Borderline includes (medium): R10720 (proposed PSOS, not described), R04417 (SMOTE rate set by OOB error), R09907 (SMOTE variant inside incremental learning), R01942 (SMOR; ordinal regression treated as classification, E2 could be argued).
- Borderline excludes (medium): R19816 (GAN balancing step in a fraud framework, E1), R07996 (GAN makes majority data for an anomaly detector, E2), R08678, R04616, R01770, R04654 (no abstract).
- Existing generator plus an existing cleaning or selection step (clarification 3, unsure): R07698, R09946, R01228, R08980.
- Front matter: R00081 (ITAB 2008 abstract book) lists "the generation mechanism of synthetic minority class examples", tagged front-matter-in-scope.

## batch098

batch 098: 200 of 200 records done; include 23, unsure 15, exclude 162
no records remain

Look at first:
- Low confidence: R00539 (exclude E1) - one-paragraph abstract on malware detection that "employs" an unnamed oversampling method; no novelty or evaluation stated.
- Calls on SMOTE parameter tuning, which the codebook does not settle: R21583 (exclude E1) - ASMOTE parameters tuned by a metaheuristic as one pipeline step in a diabetes BiLSTM paper. R14408 (include I1-other) - SMOTE hyperparameters tuned by validating the synthetic data, presented as the paper's own new algorithm.
- Where SMOTE is applied (meta-level or feature space): R19538 (exclude E1) - SMOTE applied to stacking meta-features in a student-dropout pipeline. R08093 (include I1-hybrid) - SMOTE-RSB applied in a contrastive feature space as a general method for imbalanced images.
- Includes that may be existing parts recombined (clarification 3): R03951 (k-means SMOTE in safe areas plus instance-hardness undersampling), R05300 (synonym-based text generation), R05159 (raking and relabeling). Excluded on the same question: R04251 (SMOTE plus iterative-partitioning filter as one phase of a CVD ensemble).
- Task or language doubts: R05789 (include) - SMOTE variant framed as "anomaly detection" but trained as a supervised classifier. R20697 (include) - KB-SMOTE in a Chinese journal with a bilingual title, although the record says English. R13105 (exclude E2) - relevance-based SMOTE/GAN for extreme-value forecasting; E2 here sits close to clarification 1. R11418 (exclude E-LANG) - Chinese article with a new progressive-sampling CGAN oversampler, in scope apart from language.
- Unsure U-other: R17104 and R22233 - SMOTE variants without stated experiments; W-SMOTE says it abandons empirical validation. R20185 - selecting synthetic samples in self-consuming diffusion training. R21659 - SMOTE built into selection-bias correction for survey samples.
- Front matter with an in-scope title: R01158 (HAIS 2018, multiclass oversampling paper) and R04353 (ASSIC 2022, adaptive synthetic sampling with ensemble filters).

## batch099

batch 099: 200 of 200 records done; include 20, unsure 19, exclude 161
no records remain

Look at these first:
- Low confidence (unsure): R16562 (BIRCH oversampling in a sensor-network IDS; the Chinese journal may publish in Chinese although metadata says English); R18977 (HVAC faults simulated from physics models of similar equipment for transfer learning; it is unclear whether simulation counts as a generator of synthetic minority examples).
- Cases the codebook does not settle: R17549 (mixup-style feature-space mixing with class-balanced sampling, unsure); R00607 (multilabel random oversampling that clones instances, excluded E-NOGEN); R17639 (LLM-generated synthetic samples for an imbalanced task that is regression, excluded E2); R19285 (local vs centralised SMOTE in federated learning, excluded E1); R01963 (relation between misclassification cost and oversampling ratio, no algorithm, excluded E-COMPARE); R22405 (subgroup-targeted resampling study, excluded E-COMPARE).
- Medium-confidence includes: R07060 (BROOD adds labelled out-of-distribution points, not strictly minority examples); R08999 and R03490 (existing parts combined, but cluster-guided or feature-space generation counted as a change); R02399 (1-D DCGAN, new or adapted); R10135 (mostly theory of LLM oversampling); R00085 (2008, no venue given, check I3).
- I2 not stated in the abstract: R20853 (OT-SMOTE), R21486 (FP-SMOTE), R21624 (SC-SMOTE). All three are Zenodo preprints that look like one series and cite only theoretical analysis.
- Excluded only for language but otherwise in scope: R03319 (WD-RBO, Chinese), R03333 (DB-SMOTE, Chinese), R07194 (clustered SMOTE-ENN scheme, Indonesian), R16895 (probabilistic SMOTE variants, Spanish).
- No abstract, excluded on title alone (medium): R16457, R13791, R04798, R10293.

## batch100

batch 100: 200 of 200 records done; include 28, unsure 20, exclude 152
no records remain

Records to look at first:
- Low confidence: R09361, R11535 (no abstract, titles could go either way); R08567 (defect prediction, clustering-based oversampling not described); R19466 (adaptive oversampling intensity; record language is tr but title and abstract are English).
- Codebook does not settle whether choosing the oversampling amount or ratio counts as "changing how SMOTE is applied": R21422 and R19466 (both unsure).
- Unclear whether the method synthesizes examples or only reuses existing ones: R00120, R09005, R05348 (unsure). R00876 was excluded as E-NOGEN (stratified over-sampling bagging appears to resample existing instances), medium confidence.
- Generative oversamplers where it is unclear whether the generator is new: R02952, R10299, R13971, R17977 (unsure). Generative includes at medium confidence: R05517, R16114, R14521.
- Existing components combined (clarification 3): R06061, R04658, R08969 (unsure). R00520 was included as I1-hybrid because the abstract describes a new rule for how much to generate.
- I2 not stated in the abstract: R22056, R17576, R00674 (evaluation only announced).
- Scope or document type: R05531 (SMOTE used for fault localization, a ranking task rather than classification); R04848 (book chapter; MSMOTE may be an existing variant).
- Other medium-confidence includes: R03606 (generator not named), R19376 (FSDR-SMOTE in a domain paper), R01086 (thin abstract), R05879 (the SMOTE variant is a secondary contribution).
- No-abstract records excluded on the title alone (medium confidence): R06279, R07180, R20287, R02312.
- Language metadata conflicts: R00846 was excluded as E-LANG (field says en, abstract is Korean). R16894 and R17303 were kept as E1 (Indonesian titles, field says en).

## batch101

batch 101: 200 of 200 records done; include 24, unsure 15, exclude 161
no records remain

Look at first:
- Low-confidence unsure: R08456 (boundary sampling; may not generate examples), R00660 (rotation forest + SMOTE; SMOTE may only be preprocessing), R11679 (bias-aware SMOTE-Tomek/ADASYN mix), R20019 and R07830 (no abstract; R07830 is PINN collocation sampling, likely not classification).
- Not settled by the codebook: R08901 GOLIATH is a SMOTE generalization evaluated only on regression. I sent it to unsure under clarification 1, but I coded the regression-only generator R21384 (CopulaCalib) E2; please align the two. R15469 SMOTExT (SMOTE for text via LLM decoding) has only a qualitative and privacy evaluation.
- Medium-confidence includes that could go to unsure: R19904 (cluster-aware oversampling in a fraud framework), R01409 (ADASYN seeded by abstained samples), R13148 (federated K-means SMOTE; compare R10677, which is unsure), R17419 (oversampler for recommender data), R04996 (back-translation augmentation), R18864 (GAN image augmentation), R10191 (density-based WGAN), R22285 (extrapolated synthetic minority points inside an estimator).
- I2 not stated in the abstract: R02793 (TMDSMOTE), R17780 (Cluster-stable SMOTE).
- Excluded only for language, though the methods are in scope: R01416 (SMOTE-SGA, Indonesian) and R20598 (multi-label oversampler, Chinese). R02923 is front matter tagged front-matter-in-scope.
- Medium-confidence excludes: R01654, R04820, R00917, R03012, R14270, R19282, R00673, R02773, R04615 and R16289 (both no abstract).

## batch102

batch 102: 200 of 200 records done; include 25, unsure 11, exclude 164
no records remain

Check first:
- Low-confidence unsure, all leaning exclude: R05589 (#25), a retracted CHD paper that uses an "optimized SMOTE"; R02340 (#70), a decomposition-based identity-management algorithm with a privacy angle; R21615 (#95), a "Borderline-SMOTE-based" balancing method whose description matches plain Borderline-SMOTE; R13739 (#101), an oversampling-based data-structuring step for gait data; R13362 (#175), SVM classifier chains with "adaptive SMOTE".
- Borderline excludes the codebook does not settle:
  - R05355 (#8), TOUS (Tomek links with random under- and oversampling). Coded E-NOGEN on the reading that random duplication is not synthetic generation.
  - R19209 (#2), ExtenSO, which oversamples output values in GP semantic vectors. Coded E2 (regression-style); it could instead be clarification 1 (U-other).
  - R00283 (#50), SwarmBoost. The language field says French, but the title and abstract are English and the content is in scope, so the language needs checking.
  - R19889 (#60), LLaMA generation with dedup filtering, and R03248 (#71), Isolation Forest with SMOTE. Both coded E1 as domain pipelines; clarification 3 could make them unsure.
- Medium-confidence includes:
  - R00851 (#83), BAT/PSO tuning of SMOTE's amount and k. Unclear whether parameter optimisation counts as "changing how SMOTE is applied".
  - R05757 (#35), IGAN. The abstract does not say how it differs from a standard GAN.
  - R00404 (#48), SMOTE inside random subspaces. The venue is the Journal of Foshan University, so check the language.
  - R14454 (#88), a data-equalisation model. The record says English but has a Ukrainian abstract.
  - R09858 (#51), Gaussian noise upsampling in a single-dataset clinical paper.
  - R16443 (#158), EVOS, and R16366 (#199), stream ensembles with adaptive oversampling.
  - R00157 (#134), SMOTE inside Learn++.NSE, reported with only preliminary results.
- Other notes:
  - R19247 (#115), FC-SMOTE, is unsure under clarification 2 because the abstract reports only theoretical analysis.
  - R01983 (#152) has no abstract; excluded E-COMPARE from its title alone.
  - The codebook says nothing about retracted records: R04139 is excluded E1 and R05589 is unsure.
  - The front-matter record R22291 lists R22338 (#178), which is in this batch and excluded E-COMPARE.

## batch103

batch 103: 200 of 200 records done; include 26, unsure 16, exclude 158
no records remain

Look at first:
- Low confidence: R22322 (include; federated BiGAN minority generator for intrusion detection, framed as anomaly detection, abstract partly boilerplate); R17662 (exclude; no abstract, cascade CAD model "under class imbalance"); R00874 (unsure; SMOTE inside AdaBoost-SVM ensemble with multiclass decomposition).
- Not settled by the codebook: R07232 (new equally-weighted random over/undersampling across classes; duplicates rather than synthesizes; does a ROS-based multiclass scheme meet I1?); R20472 (dataset distillation that synthesizes prototypes; sent to U-other under clarification 1).
- Pipelines of existing generators, check together for consistency: R11601 (STDA+DAGAN stacked with optimizer tuning, included because the abstract describes changes to how the generators are tuned) vs R10697 (AraBART+AraGPT2+Borderline-SMOTE, unsure) and R21894 (SMOTE+CTGAN combined, unsure).
- Borderline includes (medium): R03244 and R03339 (new resampling, but the abstract does not say the samples are synthetic); R17436 (domain-specific generative augmentation for rare transients); R05315 (text-augmentation oversampling, no details); R04046 (WSMOTE inside a liver disease pipeline, no details); R00270 (Journal of Xiamen University; the record says English but the full text may be Chinese).
- Possibly useful elsewhere: R06828 (correction note on a published theoretical analysis of SMOTE, excluded E-REVIEW); R21955 (ablation finding SMOTE counter-productive with class weighting, E-COMPARE).
- In-scope methods excluded only for language (E-LANG): R02806 (SSCMIO multi-class oversampler), R05792 (bootstrap/maximum-entropy oversampler).

## batch104

batch 104: 200 of 200 records done; include 24, unsure 21, exclude 155
no records remain

Check first:
- Low confidence (5): R01610 (SPIDER3: a new oversampler, but the abstract suggests it copies existing examples rather than making synthetic ones), R13295 (GAN-made transactions for fraud anomaly detection; unclear if they are minority oversamples), R04931 ("one-sided gradient oversampling" inside an IDS), R07946 (no abstract: outlier analysis plus oversampling for landslides), R05874 (compensated over-sampling in continual learning).
- In scope but excluded only for language (E-LANG); check whether English versions exist: R13643, R03903, R09898, R13530 (Chinese), R07340 (Thai, GANs2T).
- Language coding: E-LANG was used where the record shows a non-English title or the content would otherwise be included. Where only the language field is non-English and the content is clearly out, I used the content code and noted the language in the reason: R22164 (tr), R11609 (ru), R00501 (ko), R02552 (zh). Bilingual Chinese titles tagged English, coded E1: R11531, R22149. R00073 (included, journal "Systems Engineering" 2008) may be in Chinese; check at full text.
- Includes that are weak on novelty or detail (medium): R00073 (SMOTEBoostSVM, close to SMOTEBoost), R10099 (MRF-SMOTE, mechanism not described), R03062 (an "improved SMOTE" inside AutoML credit scoring), R01128 ("hybrid probabilistic oversampling", not described), R20512 (synthetic-data generation plus fidelity-index selection; the generator may be existing), R09262 (KNN-SMOTE; book chapter, so check I3).
- Rule I applied for GANs used in domain papers: unsure when GAN oversampling is the headline contribution (R13274); E1 when the GAN is an off-the-shelf part of a pipeline (R22220, R22149). Same idea for KDE sampling (R22146, E1).
- Clarification 2 (I2 not stated in the abstract): R21346 (QJ-SMOTE, theory only), R15574 (conditional WGAN for ALS EEG, only qualitative checks). Clarification 1 (purpose other than imbalanced classification): R16630 (GAN augmentation for crack segmentation).
- R03810 is a case study that applies C-SMOTE (coded E1); check that the original C-SMOTE paper is in the corpus.

## batch105

batch 105: 200 of 200 records done; include 22, unsure 13, exclude 165

Look at first:
- Low confidence: R21672 and R05481 (excluded E1, no abstract, generic titles: a book-brief results chapter and an SSRN quality-control case study); R02862 (unsure; building-damage paper whose MLOS/DAC/DAM resampling strategies may or may not be new generators).
- Borderline includes (medium): R09865 RUEO (stream ensemble with built-in, unspecified oversampling); R12392 KODS (DGA knowledge-filtered oversampling plus stacking); R21965 TailedDiffAD (diffusion minority generator, but framed as anomaly detection, so E2 is arguable); R07500 (improved random balance sampling, multiclass, generator unspecified); R03334 DB2SM (DBSCAN cleaning plus SMOTE; under clarification 3 this could be unsure); R13132 (k-means adaptive hybrid sampling plus BiLSTM); R01862 (discourse-marker text augmentation).
- Borderline excludes (medium): R11019 (HHOA tunes the SMOTE rate inside an IDS model; could count as changing how SMOTE is applied); R15885 (existing WGAN as oversampler in a "novel framework"); R22348 (unspecified generative AI used before model distillation).
- The codebook does not settle these: R15442 (privacy attacks on SMOTE; excluded E-NOGEN but likely worth citing in a privacy discussion); R01496 GRE (stream oversampling that reuses past real minority examples, so no synthesis; excluded E-NOGEN); R01505 Cimap (partial-label oversampling, unsure U-other); R13325 GraphSMOTER (a SMOTE-style method for imbalanced regression, excluded E2).
- Excluded E-LANG although they propose oversamplers: R05279, R01237, R05063 (Chinese full text). R00522 (unsure) may also have Chinese full text.
- Metadata problems: R19680 has an LLM error message in its title field (the abstract is fine; excluded E1). R04057 is proceedings front matter tagged front-matter-in-scope (it lists a paper on sensitivity analysis of oversampling for bank credit data).

## batch106

batch 106: 200 of 200 records done; include 24, unsure 19, exclude 157
no records remain

Look at first:
- Low-confidence unsure: R00368 (active-learning resampling, synthetic or replication?), R07566 (vague "efficient resampling" fraud framework), R11050 (statistical balancing with geometric-transform oversampling), R05974 (centroid-based oversampling, garbled abstract), R20825 (SMOTE applied per region for fairness), R04520 (PERL rule ensemble with a sampling phase).
- Codebook conflict, clarification 1 vs E2: R21744 (spatially constrained SMOTE built for clustering) and R22303 (two-stage improved SMOTE for makespan prediction, apparently regression). Coded unsure U-other; E2 would exclude both.
- Include vs E1 boundary, off-the-shelf generator as the paper's oversampler: R03773 (VAE/CVAE), R05676 (GAN), R09056 (Synthetic Data Vault), included at medium. GAN used as one part of a domain framework went to unsure instead: R13801, R16132, R19358.
- R19744 (GraphBalance, 2026): abstract is almost word for word the GraphSMOTE abstract (Zhao et al. 2021) with the name changed. Included as I1-new-variant; check originality and E4 at full text.
- Language: R00294 (BOS) record says English, but the venue (Journal of Sichuan University) may publish in Chinese. Excluded E-LANG although in scope: R13257 (FBS-RE), R10064 (GDOS), R03088 (GSMOTEBoost).
- Clarification 3 (existing generator plus existing step): R01768, R04800, R00454; also R00680 (SMOTE plus Rotation Forest: inside the ensemble or applied once before it?).
- Medium-confidence includes to confirm: R04128 (oversampling by multiple imputation), R12058 (post-oversampling critical-sample filter), R22366 (instance-hardness oversampling may be replication), R02885 (mixup oversampling inside a CNN paper), R17675 (federated CGAN).
- Other unsure: R15456 (automatic per-class SMOTE ratio), R08499 (claims a novel nominal generator but compares SMOTE-N and ADASYN-N), R17241 (SS-SMOTE, I2 not stated, clarification 2), R16940 (no abstract).

## batch107

batch 107: 200 of 200 records done; include 18, unsure 15, exclude 167
no records remain

Check first:
- Low confidence: R12347 (sliding-window "oversampling" of sleep stages; are re-cut real windows synthetic examples?), R13670 (no abstract, vague title).
- Non-English but otherwise in scope, excluded E-LANG on the language field only (abstracts are English): R01096 (SD-ISMOTE, zh), R01957 (boosting to clean noise after SMOTE, Turkish). Verify the full-text language.
- Generative oversampler in a domain paper, "proposed generator" vs "existing generator applied" (codebook does not settle): included R03572 (deep WGAN-GP, fault), R13277 (DC-GAN, peptides), R13749 (new filters on GAN output); unsure R18464 (conditional DDPM + domain adaptation), R06374 (GAN-SMOTE, federated); excluded E1 R11078 and R16484 (CTGAN), R10548 (CTGAN-inspired + cost-sensitive), R18282 (GAN in HAR pipeline), R17052.
- Clarification 1 applied where E2 or "no classification" could also apply: R04099 (VAE for zero-inflated crash counts, regression), R01205 (SMOTE-PENN for learning to rank), R17978 (3D bone diffusion, no classification; probably exclude), R05574 (oversampling for fair classification).
- Same method twice: R00495 and R00551 (OUPS); R00495 has no venue (possibly a thesis). Decide E4 at full text.
- Borderline excludes: R00621 (multilabel ML-BFO duplicates samples, so E-NOGEN), R01954 (F-race chooses among existing balancers), R00389 (PCA then SMOTE).
- Out of scope but useful elsewhere in the survey: R18510 (threshold moving reproduces SMOTE's gain across 79 datasets), R17813 (commentary on SMOTE-ENN leakage before the split).

## batch108

batch 108: 200 of 200 records done; include 34, unsure 16, exclude 150
no records remain

Look at these first:
- Low-confidence includes and unsures: R13896 (include; 'Dynamic Seasonal SMOTE' is named as new in a water-quality system but never described), R03093 (unsure; adaptive DE replaces PSO, unclear whether it tunes SMOTE or the network), R01114 (unsure; t-SNE segmentation plus synthetic sampling for radar HRRP, unclear whether the sampling is new).
- Low-confidence excludes, all with no abstract and domain-application titles (E1): R19828, R18217, R09819, R07271. No-abstract unsure: R03611, R06442 (titles about handling imbalance, could be applied or new).
- Probably includes held back by the codebook: unsure U-other because I2 is not stated in the abstract: R09036 (improved G-SMOTE, multiclass), R17605 (BP-SMOTE), R17022 (ES-SMOTE). Unsure U-no-abstract with method-like titles: R05910 (boundary-distance/local-density oversampling), R11753 (class-balanced diffusion model).
- Language checks: R02632 excluded E-LANG because the record says zh, but the English abstract describes an in-scope GA sample generator for NER. R13569 was included (DBSCAN+CGAN oversampler); the record says English, but the title has a Chinese parallel title and the venue is a Chinese journal.
- Cases the codebook does not settle: R03230 (include I1-other; converts binary features to numerical ones before SMOTE, a change of representation rather than of generation), R08320 (exclude E-NOGEN; BALANCER recommends which augmentation method to use, plus a 720-dataset comparison), R10842 (include I1-other; conditioned mixup-style embedding augmentation compared with ROS), R03650 (include; seq2seq kNN that also works as an oversampler), R00765 (include I1-multiclass; BBO, oversampling type not stated, possibly random oversampling), R14217 (include; BS-GAN hybrid of a GAN and Borderline-SMOTE, an edge of clarification 3), R06880 (exclude E1; a standard VAE used as an oversampler on one medical dataset).
- Clarification 3 unsures (existing generator combined with a step, presented as new): R10932, R20565, R07449, R03909, R19715, R16266, R09591.
- Front matter: R15943 excluded E-REVIEW and tagged front-matter-in-scope (it lists 'BGDSO: A New Synthetic Oversampling Method...').

## batch109

batch 109: 200 of 200 records done; include 23, unsure 20, exclude 157
no records remain

Look at first:
- Borderline includes (medium): R05561 (GA-SVM tuning of SMOTE k and ratios; counted as "changes how SMOTE is applied"), R03664 (kernel-space SVM ensemble oversampling; "densifies majority class boundaries", so unclear it makes minority examples), R06664 (K-means++-SMOTE trained end to end with CNN-BiLSTM), R14198 (enhanced SMOTE is one of three innovations in an IDS framework), R06359 (improved DCGAN inside a fault-diagnosis pipeline), R09982 (SEDAC: CVAE on distilBERT vectors; new method or applied generator?), R02512 (WGAN then SMOTE as a two-stage generator).
- Not settled by the codebook: R22032 (theory of SMOTE convergence) and R03956 (SOUL software library), both excluded as E-COMPARE with no exact code and may matter elsewhere in the survey; R08432 (Chinese-language article proposing an improved SMOTE, E-LANG but otherwise meets I1/I2).
- Borderline excludes (medium): R06047 ("the improved SMOTE" plus cleaning in a CNN DGA paper), R02214 (title "Novel SMOTE Algorithm", abstract says it adopts SMOTE), R17811 (existing SMOTE-LOF plus feature selection in two orders), R08962 (deepfake "advanced data balancing strategy"), R07615 (unspecified synthetic augmentation, GAN keyword), R07414 (claims a "novel ensembled approach" but compares oversamplers).
- Unsure, I2 not stated in the abstract (clarification 2): R18112, R17968, R18157, three Zenodo SMOTE-variant preprints that mention only theoretical analysis.
- Unsure, existing generator plus cleaning (clarification 3): R13499, R00970, R02268, R15269, R13673, R10749. Unsure for another purpose (clarification 1): R14037 (long-tailed diffusion image synthesis), R10019 (sex-ratio matching in neuroimaging).
- Other unsure: R03577, R05205, R06629, R10206, R22113, R08272 (cannot tell whether the resampling is new); R01320, R05664 (new resampling, but unclear whether it is synthetic); R22095 (no abstract, TrafficLDM).

## batch110

batch 110: 200 of 200 records done; include 27, unsure 19, exclude 154

Look at these first:
- Low confidence (all unsure): R13484 (IDS paper with GAN and VAE-GAN augmentation, new or applied?), R13244 (LLM MBTI framework fine-tuned with "synthetic minority oversampling"), R03487 ("integrated" Borderline-SMOTE in AdaBoost: SMOTEBoost-like hybrid or plain preprocessing?), R01716 (denoising autoencoder that oversamples "through misclassification cost"), R19517 (custom "extrema oversampling" in stock trading; synthetic or duplication?).
- Zenodo preprint series of SMOTE variants: R21391 RE-SMOTE, R18956 EC-SMOTE, R16709 AK-SMOTE are unsure under clarification 2 (only theoretical claims, I2 not stated). R21517 BS-SMOTE from the same series was included because its abstract names evaluation metrics (F1, G-mean, AUC), but no datasets. Check these four together for consistency.
- Codebook does not settle whether setting the oversampling amount counts as I1: R03071 (complexity-based oversampling size, included as I1-other), R02122 (optimal target proportion plus resampling at random, unsure), R06801 (ISMOTE = SMOTE with metaheuristic-tuned sampling rate, unsure).
- Clarification 3 boundary: R00344 SMOTE-RSB* was included as I1-hybrid because the rough-set editing step looks new. Unsure because the step looks existing: R19848 (SMOTERN noise filter + SMOTE; also typed as book chapter, so I3 is in question), R01849 (ADASYN-NCL), R00819 (CMTFSVM + SMOTE), R15185 (oversamplers + NN denoising), R18859 (ADASYN + range-constrained CTGAN).
- Medium-confidence includes: R16146 (LLM oversampler CGGReaT framed as "anomaly detection" but uses supervised classifiers), R07551 (SMOTE+CGAN two-phase oversampler inside a fraud paper), R08305 (MOKCCAS, garbled abstract), R00499 (C-MIEN multiclass scheme; oversampler type not stated).
- R09621 was excluded only as E-LANG (Chinese full text); otherwise it would be an include (WKMeans-SMOTE).

## batch111

batch 111: 200 of 200 records done; include 29, unsure 14, exclude 157
no records remain

Look at first:
- R17422 (low): no abstract; title "Assessing Fidelity, Utility, and Privacy of Synthetic CGM Signals Generated by Deep Models". Coded E-COMPARE as an assessment study. If it actually proposes a generator for privacy-preserving sharing, clarification 1 makes it U-other.
- Cases the codebook does not settle:
  - R21941 (arXiv): de-biased validity test for synthetic minority data that audits 91 oversamplers. Coded E-COMPARE + comparison because it evaluates generators rather than proposing one. Probably important for the survey's evaluation discussion.
  - R01352: software paper for the R "imbalance" package. Coded E-REVIEW because there is no software code. May be wanted for a tools section.
  - R00440: safe level graph that picks which SMOTE variant to apply. Included as I1-other because it changes how SMOTE is applied, though it generates nothing new.
- Includes that may not hold up:
  - R00275: guided oversampling. Unclear whether it makes synthetic examples or duplicates.
  - R13505: HSMOTE is described only as plain interpolation.
  - R08723: ensemble SMOTE on pixel-pair features (HSI).
  - R15775: modified Gaussian oversampler inside a power-plant method.
  - R12539: dual-channel SMOTE extensions in a CNN.
  - R17713: a metaheuristic sets the SMOTE rates.
  - R08572: fuses several oversampled datasets.
  - R21663: semantic-filtered SMOTE-PSO.
- Excludes that may not hold up:
  - R01624: margin-based "random oversampling" in AdaBoost. Coded E-NOGEN on the assumption that it duplicates examples.
  - R00384: cluster-selection strategy. Coded E-NOGEN on the assumption that it undersamples.
  - R07977, R15044, R15972, R19934, R12705: CTGAN, diffusion, SeqGAN or a GAN applied as a pipeline step. Coded E1.
- E-LANG records whose methods would otherwise be candidates (Chinese): R02044 (Screening_SMOTE), R12268 (DCHO), R05005 (online transfer oversampling), R10642 (SMOTE+GAN). Non-English papers that were plainly E1 were coded E1 (R11363, R20184, R07035).
- R02414 (DBCSMOTE): a SMOTE variant built for regression (warfarin dose). Coded E2 with high confidence; noted in case regression variants matter elsewhere.
- Unsure (14): 13 are U-new-or-applied, in two groups.
  - A domain paper's GAN or other generator whose novelty is unclear: R05721, R19742, R06361, R19389, R11397, R13303, R15744.
  - An existing generator plus an existing cleaning or selection step, presented as new (clarification 3): R20756, R10438, R07272, R10457, R20602, R03407.
  - The 14th is R01930 (U-other): margin-based RF "with data sampling"; the abstract does not say whether it oversamples.

## batch112

batch 112: 200 of 200 records done; include 19, unsure 21, exclude 160
no records remain

Records to check first:
- Low confidence (unsure): R11723 (existing SMOTE-Tomek, but synthetic samples are fed only into broad-learning input generation, not training) and R15479 (class-separable ELM autoencoder, then oversampling in the encoded space). In both, it is unclear whether the way SMOTE is applied is the claimed contribution.
- Four Zenodo 2026 preprints in the same style were marked unsure under clarification 2 (only theoretical analysis, no experiments named): R17116 Index-space SMOTE, R17987 CVM-SMOTE, R17601 BA-SMOTE, R21601 Rule-chain SMOTE. Check whether the full texts contain any experiments.
- R00540 (SMOTE extended with the IPF noise filter, compared with SMOTE generalisations) is unsure only because clarification 3 treats an existing generator plus an existing filter as unsure. It reads like a substantive SMOTE extension.
- The codebook does not settle these: R13796 (excluded E1; whale optimisation tunes SMOTE's hyperparameters in a domain pipeline). Does tuning count as "changing how SMOTE is applied"? Compare R00718 (unsure: PSO sets separate rates for boundary and safe samples) and R13932 (unsure: unclear whether MVO tunes SMOTE or only KNN). R02209 (excluded E1): SMOTE plus PSO feature selection plus MetaCost, presented as a novel method. I applied clarification 3 to sample cleaning or selection only, not to feature selection.
- Generative borderline calls: R04759 (GAN oversamplers for software fault prediction), R02132 (WGAN oversampling for lung nodules) and R04858 (taming-transformer cervical cell generator) were included at medium confidence, because each presents the generator as the method. R11237 (conditional WGAN with gradient penalty plus MPSO feature selection), R04161 (RUS plus mixed-type CWGAN) and R18340 (SMOTE-GAN plus CRF undersampling) were left unsure, because the abstracts do not say whether the generator itself is new. R18495 was excluded as E2: a GAN anomaly detector whose generated fraud samples train the discriminator rather than oversample.
- Includes resting on inference: R10080 (DSSO) and R13528 (IA-KNNR) are multi-label resamplers where synthetic generation is implied but not stated. R19292 (FIS-CSP-OM) is evaluated mainly on rule quality, and synthetic instance production is described as a capability.
- No code fits: R03578 (IMBENS software toolbox; coded E-NOGEN) and R17725 (theory of oversampling as transfer learning, SMOTE against bootstrapping; coded E-COMPARE with tag comparison; possibly useful as a background citation). R05788 is a book chapter (I3 unclear) and was also marked unsure under clarification 2.
- Language and order of exclusion codes: where several reasons applied, I used the codebook's order. So R00429 (language id), R07594 (ar) and R03635 (Chinese; also regression) are coded E1, and R03293 (Chinese, content otherwise in scope) is coded E-LANG. R16621 has no abstract and was excluded E1 on its title alone (medium).

## batch113

batch 113: 26 of 26 records done; include 5, unsure 4, exclude 17
no records remain

Look at these first:
- R08186 (unsure, low): new k-prototypes cluster-based undersampling followed by existing ADASYN/SMOTETomek/NearMiss-2 on crash data, framed as a comparison. The codebook counts "SMOTE with a new cleaning step presented as a method" as I1-hybrid, but the novelty may be undersampling only (E-NOGEN) or a comparison (E-COMPARE).
- R21968 (include, medium): diffusion generator of minority defect images plus filtering, framed as "anomaly detection and localization". E2 judged not to apply because a supervised classification-segmentation detector is trained (image-level AP). Check scope.
- R17791 (include, medium): CoCo-GAN, a software defect prediction framework whose conditional GAN generates minority samples. The abstract does not say whether the CGAN itself is new, so this could be U-new-or-applied.
- R14267 (include, medium): class-conditional 3D latent diffusion MRI generator, framed mainly as data scarcity (imbalance also named). Classifiers are trained on synthetic images, so this may be synthetic-data replacement rather than minority oversampling.
- R07585 (unsure, medium): 3D rendering plus CycleGAN defect-image synthesis for object detection. I2 is not stated, and the codebook does not say whether object detection counts as classification (the same question applies to R21968).
- R00831 (unsure, medium): OS-YATSI, oversampling inside a semi-supervised learner. Would be I1-hybrid if the full text shows it changes how oversampling is applied.
- R16558 (unsure, medium): no abstract, but the title proposes a new MOPSO-based oversampling strategy. Likely an include once I2 is checked. Coded U-no-abstract, not include, following clarification 2.
- R06733 (exclude, medium): no abstract; the title reads as a domain application (bad-loan prediction).

