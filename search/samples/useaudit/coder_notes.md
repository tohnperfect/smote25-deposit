# Notes of the coding sessions (useaudit)

## batch001

useaudit batch 001: n=20, fulltext=7, application=20, inside_folds stated=1, before-split=3
Other counts: inside_folds nr=3, na=13 (abstract only); test_balanced yes=3, nr=4, na=13; vs_none yes=6, no=1; vs_weights yes=2, no=5; calibration assessed=0 of 7 full texts; validation internal=19, external=1; confidence high=5, medium=12, low=3.

Check first:
1. R00847 inside_folds=nr, test_balanced=nr: the text does not say where SMOTE ran, but Table 2 gives ACC = F = AUC = G-mean (.89), which on this imbalanced gene set requires about 50/50 test folds. Likely before-split / yes.
2. R01960 test_balanced=nr: the text is silent, but holdout accuracy vs macro F1 (subtask B: 81% acc, F1 .59; subtask C similar) cannot come from a balanced test set. Likely no (SMOTE on training data only; inside_folds would still be nr unless a checker reads it as stated).
3. R00727 before-split / test_balanced=yes rest partly on arithmetic: with SMOTE, CV Acc/MCC (.864/.728) fit balanced 217/217 folds, not the natural 87/217 (.860/.688). Validation coded external (independent 13/51 set from an earlier study, natural distribution).
4. R01239 inside_folds=stated (low confidence): resampling is described for the six training datasets, but train and test are built from the same 120 respondents with different labels, and Table 3 (50% accuracy at zero recall) hints at a balanced test set.
5. R01527 before-split / test_balanced=yes: the whole augmented set was oversampled with Borderline-SMOTE and test accuracy is reported "in BSIS"; the train/test split itself is never described.
6. Resampler coded other for three abstract-only records whose oversampling is unnamed (R01572, R01633, R01140); R01572 and R01633 may not use SMOTE or random oversampling at all, which bears on is_application.
7. Abstract-only records whose abstracts already state training-only oversampling (R00349 "in each training set", R02826 "a training set ... oversampled") have inside_folds=na per the codebook; with full text they would likely be stated. R02561's class counts (58 per class from 93 images) hint at before-split.
Procedure notes: add_codes.py requires a "rec" key not named in the codebook, and measures accepts na but not nr; na was used where an abstract names no measure (R01572, R02298, R01633). Rows already appended cannot be amended with the tool, so items 1-2 are flagged here rather than recoded.

## batch002

useaudit batch 002: done, 20 of 20 records coded (out/batch002_coded.csv)

Counts
n=20; source: fulltext=4, abstract=16
is_application: yes=17, no=3 (R01271, R02506, R00221)
inside_folds (full text only): stated=2 (R01570, R02484), nr=1 (R01707), before-split=0
test_balanced: no=2, nr=1; vs_none: yes=2, no=1; vs_weights yes=0; calibration yes=0
validation: internal=5, nr=12, na=3
confidence: high=2, medium=16, low=2

Check first
1. R02506 (full text) is_application=no: proposes its own GAN-based oversampler (G-IDS, GAN plus controller that accepts synthetic batches); no SMOTE or ROS. It may have been misfiled under E1. If counted as an application: security, tabular, deep-generative, neural-net.
2. R01271 is_application=no (low): compares ROS, RUS and SMOTE for clustering (FCM/PCM) image segmentation; the abstract names no application domain.
3. R01707 (full text) inside_folds=nr, test_balanced=nr: SMOTE and undersampling "balance the dataset", and the 25% test set is drawn "from the whole dataset". The order is not stated, so this may be before-split.
4. R01570 (full text) inside_folds=stated (medium): SMOTE was applied to the 9:1 training set and the test set was left untouched, but how this fits with the 10-fold CV is loosely described. The split is by clinical event (1524 events, 239 patients), and RF attribute reselection was run on the full data.
5. R02762 (low): the oversampling method is unnamed and the paraphrasing augmentation may be the authors' own (which could flip is_application). Domain coded education; social is possible.
6. Conventions used in abstract-only rows: resampler "other" = unnamed oversampling (R02350, R02762, R02261). learner "na" = classifier not named (R02350, R01782, R02576, R00861, R01285). measures "na" = no measure named (R01782, R02432, R00467).
7. Domain judgement calls: R02621 environment (earthquake hazard; could be other); R02884 and R00467 industry (could be transport); R02484 education (could be software). R02004 is_application=yes is borderline: cluster-then-SMOTE that the authors say they "adopt".

## batch003

useaudit batch 003: done, 20 of 20 records coded.

Counts: n=20; source fulltext=2, abstract=18 (R01439 has title only); application yes=19, no=1 (R00660);
inside_folds stated=0, before-split=2 (R00383, R02744), nr=0, na=18 (abstract only, or not an application);
test_balanced yes=1 (R02744), no=1 (R00383); validation internal=9, nr=10, na=1;
confidence high=3, medium=12, low=5.

Check first:
- R00383 inside_folds=before-split (medium): rests on "grid search was made over the entire balanced data of all
  samples" and five SMOTE-balanced copies of the data set (Dsmo1-5); where SMOTE sits inside the LOO loop is not
  stated, so nr is arguable. Modality coded tabular (55-band spectral vectors from multispectral images); image arguable.
- R01439: no abstract and no full text; is_application=yes rests on the E1 screening alone; resampler and measures na.
- R00660 is_application=no: generic imbalanced-data classifier (fuzzy C-means + Rotation Forest + existing SMOTE),
  no domain named; the codebook does not list this reason for "no".
- R02100 (GAN balancing) and R02214 (title "novel SMOTE algorithm", abstract "adopt SMOTE"): is_application=yes
  would become no if the resampler is the authors' own.
- Oversampling of unnamed type: R02502 resampler=na; R02631 coded random-oversampling;undersampling.
- Spatial hold-outs coded internal, not external: R01349 (test regions A/B), R02895 (held-out well).
- Domain calls: R02156 industry (transport plausible), R02895 energy, R02100 and R02309 other.

## batch004

useaudit batch 004: done, 20 of 20 records coded (out/batch004_coded.csv)

Counts
n=20; fulltext=0 (all 20 coded from title and abstract); application=20 (yes), 0 no
inside_folds: stated=0, before-split=0, nr=0, na=20 (no full texts, so all FT fields are na)
validation: internal=5, nr=15; confidence: medium=17, low=3

Check first
1. R02587: title only (no abstract, no full text). is_application=yes rests only on the E1 exclusion; modality, resampler, learner and measures are na. Needs the full text.
2. R02682: FN-SMOTE may be the authors' own SMOTE variant (book chapter). If the chapter presents it as new, is_application should be no.
3. R02274: the only resampling is image augmentation to oversample the minority class (no SMOTE). Coded yes with resampler=other; check that it is in scope.
4. R02898: vague abstract with unspecified oversampling and no named learner; it may be a generic demonstration rather than a domain application (low confidence).
5. Unspecified "oversampling" coded resampler=other: R01933, R02898, R02645 (and R02274, augmentation). Recode if the full texts name SMOTE or random oversampling.
6. The abstract wording suggests resampling before the split or CV (inside_folds left na, full text needed): R02114 (SMOTE, then CV), R01329 (RUS+SMOTE on the UCI data set first), R02730 (balancing "on the BCSC dataset before constructing" the models).
7. Domain borderlines: R01644 medicine/education, R02407 energy/industry, R01639 transport/environment, R02274 social/environment, R02645 medicine (public health)/finance.
8. learner=na because the abstract names no model: R02319, R02587, R02898, R02682. measures=na because none is named: R01718, R01639, R02682, R02587.

## batch005

useaudit batch 005: done (20 of 20 records coded, 11 November 2026)

Counts: n=20, fulltext=0 (none of the 20 had a text file; all coded from title and abstract), application=20,
inside_folds stated=0, before-split=0 (all 20 are na, because the codebook sets (FT) fields to na with the abstract only).
Domains: medicine 5, bio 4, finance 3, security 2, transport 2, software 2, social 1, other 1. Stakes individual 7.
Validation: internal 2, external 1, nr 17. Confidence: high 2, medium 16, low 2.

Check first:
1. R02000 and R01266: the abstracts themselves state when the resampling was done (R02000: SMOTE inside each CV
   training fold = stated; R01266: SMOTE on the whole data, then a 70/30 split = before-split with a balanced test set),
   but the rule makes inside_folds/test_balanced na. Getting these two full texts would change the inside_folds counts.
   R00652's abstract also says SMOTE was applied to the training set.
2. R01524: generic ResNet method shown only on MNIST; coded is_application yes, domain other (low confidence); "no" may fit better.
3. R01367: the abstract does not name the data type; modality time-series (EEG) is assumed (low confidence).
4. Resampler "other" stands for an unnamed "oversampling" in R02369, R01370, R00293, R01524, R01737 (SPIDER in R01367).
   Measures na where the abstract names none (R00874, R00652, R01719, R01968, R01228, R02429, R01737);
   learner na where no classifier is named (R02900, R01228).
5. Judgement calls: R02382 domain bio (fMRI memory task, no patient decision); R00874 domain security (image forensics);
   R02429 validation external (cross-project defect prediction); stakes individual for the fraud records R01864, R01737.
6. vs_none or vs_weights is probably yes in the full text (both are na here): R02369 (compares cost-sensitive learning),
   R02000, R02900, R01719, R01228, R01370, R01367.

## batch006

useaudit batch 006: done, 20 of 20 records coded (out/batch006_coded.csv)

Counts: n=20; source fulltext=5, abstract=15; is_application yes=20, no=0.
inside_folds: stated=2, before-split=2, nr=1, na=15. test_balanced: yes=2, no=3, na=15.
vs_none yes=3, no=2; vs_weights yes=1, no=4; confidence high=11, medium=9, low=0.

Check first:
- R04586 (card fraud, CNN-RNN): before-split and test_balanced=yes rest partly on arithmetic (accuracy equals the mean of sensitivity and specificity in every row of Tables I-II) plus garbled text; undersampling coded from a garbled passage in Sec. III.A.
- R06252 (Framingham RNN-GRU): before-split read from pipeline order (SMOTE at data collection, before modelling) and post-SMOTE total 7,328 > 4,240 original; the paper's per-class counts are inconsistent.
- R04241 (SemEval sarcasm): inside_folds=nr (SMOTE placement never described) but test_balanced=no, because results are official shared-task scores from submitted predictions.
- R02989 (driver stress): stated from Sec. 4.2 although Fig. 1 puts oversampling in data preparation; domain transport, stakes individual, modality mixed are judgment calls.
- R06494 and R03291: likely overlapping publications (same dataset, classifiers, 95.16%). R03291 shows Extra Trees was feature selection, so the forest in R06494's learner may be wrong.
- Conventions: modality coded by source data (image, signals, text), not the feature vectors SMOTE ran on (R03964, R04275, R02989, R03193); molecular fingerprints (R06703) coded tabular. Affective-state tasks R07289 and R02989 coded stakes individual, the facial-expression benchmark R03716 other.
- R03028 (abstract only): its precision, recall, G-mean and AUC are arithmetically consistent with a balanced test set; worth a full-text check.
- Process: to recode modality for R03964, R04275 and R02989, the coded CSV was cut back to records 1-5 and records 6-20 were appended again through add_codes.py; the pre-fix copy is work/batch006_coded_backup_before_fix.csv.

## batch007

useaudit batch 007: done (11 November 2026)

Counts: n=20; source fulltext=5, abstract=15; is_application yes=20, no=0.
Full-text records (5): inside_folds stated=1 (R06019), before-split=4 (R04593, R06088, R06167, R03269), nr=0;
test_balanced yes=4, no=1; vs_none yes=2, no=3; vs_weights yes=0; calibration yes=0.
Validation: internal=13, external=1 (R04991), nr=6. Stakes: individual=10, other=10. Confidence: high=4, medium=13, low=3.

Check first:
- R05299: the record title (perovskite solar cells, rGO buffer layer) does not match its abstract (credit card fraud with
  over/undersampling and class weights). Coded from the abstract, confidence low. Decide whether to drop or re-match the record
  (it may duplicate the real fraud paper). The resampler is incomplete because the oversampling method is unnamed.
- R05694: the abstract mentions no resampling at all. is_application=yes rests only on the E1 screening; resampler=na.
  Domain medicine (depression risk) vs social (social media forensics) is a judgment call.
- R03269: before-split inferred from "rebalance the dataset", then repeated training with 10-fold CV (Matlab Classification
  Learner), plus the limitations note that artificial samples weaken the metrics. Stakes coded other because the authors say
  the aim is to compare two SPECT cameras, not to build a clinical tool.
- R06167: SMOTE (then KNN augmentation to 1,254, coded other) was applied to the 90% portion before its 75/25 train/test
  split, so the headline test results are on balanced data (prevalence 50.47%). A 10% validation set was kept untouched.
- R05434: borderline is_application. It searches for the best SMOTE balance ratio jointly with L1-SVM feature selection.
- Abstract records with an unnamed resampler, coded na: R06678 (modality and learner also na) and R05027 ("oversampling of TxE
  samples"; it may also balance the test data).
- Conventions to confirm: validation=internal when an abstract names a single evaluation data set but no split (R04368, R03301,
  R06158, R04005, R04903). Modality=image for MRI radiomics (R04991) but tabular for clinical SPECT software scores (R03269).
  Fraud detection stakes=other (R03301, R05299).

## batch008

useaudit batch 008: n=20, fulltext=4, abstract=16, application=19 (no=1), inside_folds stated=2, before-split=1, nr=0; test_balanced yes=1, no=1, nr=1; validation internal=13, nr=6; confidence high=9, medium=9, low=2.

Check first:
- R03163 (before-split, test_balanced yes): the abstract says flipping and Borderline-SMOTE came before the split. Sect. 4.1-4.2 say the positives were flipped x4 before the split, but Borderline-SMOTE was applied only to the 48 training positives. Test set = 28 flipped positives + 38 random negatives; the best epoch was picked on test accuracy. Resampler includes other (flipping).
- R04381 (stated, test_balanced no): the text says ROS draws from the training set; Fig. 4 shows SAVEE undersampled 120 to 60 on the whole set, but the per-class test counts in Tables 2-4 are natural. Stakes coded other for speech emotion recognition (borderline).
- R05157 (stated, test_balanced nr): the only basis is "balance the train data" / "imbalanced handling of train data"; the test set is never described.
- Convention to confirm: an unnamed "oversampling" is coded resampler=other (R05566, R05157, R06207). SOUP is coded other (R06980). R07180 has a title only, with no mention of resampling: is_application=yes on the E1 premise, with resampler/modality/learner=na.
- R03578 is_application=no: software toolbox paper (imbens), no application.
- R06207 and R07180: no abstract, coded from the title only (low confidence).
- R05972 (abstract only): the abstract suggests the whole data set was oversampled before 5-fold CV; worth a full-text check.
- Domain calls: R05566 materials and R05972 robotics coded other; R04730 building fire and R06579 drinking water coded environment; R06108 exome-based cancer DSS coded medicine, not bio.

## batch009

useaudit batch 009: n=20, fulltext=0, application=20, inside_folds stated=0, before-split=0

All 20 records came without a full text, so source=abstract and every (FT) field (inside_folds, vs_none, vs_weights,
calibration, test_balanced, evidence) is na. validation: internal 10, nr 10. confidence: high 9, medium 8, low 3.

Check first:
- R03515 (low): the abstract equates "SMOTE" with rotating/scaling/translating training images (augmentation); resampler
  SMOTE may be wrong. Test on five public DR datasets coded validation nr; may be external if training used other data.
- R06560 and R04701 (low), R04066 (medium): the oversampling method is not named in the abstract and was coded `other`;
  the full text should give the real method(s).
- Possible before-split from the abstract wording (full text needed): R04257 (SMOTE "at the outset", before feature
  selection), R03509 (SMOTE listed before 10-fold CV), R04373 (k-fold CV on "imputed and resampled datasets").
- Abstract states training-set-only resampling (would be inside_folds=stated with the full text): R07187, R06988, R05592.
- Judgement calls: R03509 stakes=individual (fraud by traders) and modality=other (graph); R04373 stakes=other (firms);
  R05590 domain=industry (could be energy); R04066 domain=transport (data are tweets); R03215 modality=tabular assumed.
- measures=na (abstract names no result measure): R06495, R04257, R06988, R05646, R04373.

## batch010

useaudit batch 010: done (20 of 20 coded, 11 November 2026)
n=20, fulltext=0 (all coded from title and abstract; R06379 from title only), application=20, inside_folds stated=0, before-split=0 (all na: no full texts).
validation: nr 15, internal 3, external 2. confidence: high 4, medium 12, low 4.

Check first:
- R04086 (coupon acceptance): abstract names no resampling method; is_application=yes rests on its "imbalance handling" wording. Needs the full text.
- R03270 (card fraud): only random undersampling named, no SMOTE or oversampling; may fall outside the audit population.
- R06125 (CIDD-ADODNN stream framework on NSL-KDD/Spam/Chess) and R07106 (RN-Autoencoder around existing RN-SMOTE): is_application borderline.
- R04686 and R04703: validation=external read from vague abstract phrases ("different environment", "new dataset test case"). R04686 modality coded tabular but could be time-series (signal-derived features), as R04703 was coded.
- R06379: no abstract, title only; most fields na.
- resampler=na (method not named in abstract): R04086, R06327, R05773, R06379, R04077.
- Judgement calls: stakes=other for transaction-, parcel- and firm-level units (R03270, R04694, R03361); domain social for R04465 (bibliometrics) and R04694 (law enforcement); R07106 medicine vs bio; R05820 medicine vs business.
- vs_none is FT and set na, though the abstracts of R04465, R04879, R04694, R04703 and R03234 report runs without resampling.

## batch011

useaudit batch 011: done, 11 November 2026
n=20, fulltext=5, abstract=15, application=20 (no=0)
inside_folds (fulltext only): stated=4, before-split=1, nr=0
test_balanced: no=3, yes=1, nr=1; vs_none: yes=2, no=3; vs_weights: no=5; calibration: no=5
validation: internal=6, nr=14; confidence: high=8, medium=9, low=3

Check first:
1. R10600 (childhood anaemia, Lesotho): inside_folds=stated, test_balanced=nr. Methods say 80/20 split first and SMOTE on training only, but the results table says "all metrics obtained through 5-fold cross-validation", and the tuning CV ran on the SMOTE-oversampled training set. The reported numbers may come from leaky CV, not the test set.
2. R13197 (diabetes follow-up): inside_folds=stated is read from "fitted to the SMOTE training data", the post-SMOTE sizes listed per fold, and pooled confusion matrices that total the original class counts. The headline weighted precision of 0.93 hides an SVM that misclassifies 781 of 1,923 majority-class patients.
3. R10548 (GAN + cost-sensitive fraud, abstract only): coded as an application with resampler deep-generative. Its CTGAN-inspired generator could be read as the paper's own resampling method (is_application=no). No SMOTE is named.
4. R14882 (district heating pipes, abstract only): resampler and learner are coded "other" only because the abstract names neither; the full text would settle both.
5. Stakes for the four fraud records (R20299, R10548, R18816, R11193) is coded individual because the flags act on customers' or agents' transactions. This is borderline, and the rule should be the same in every batch.
6. Domain judgement calls: R14882 energy (or industry), R15036 burnout coded medicine (or business), R19306 security (or software).
7. R20299: vs_weights=no. Class weights and PR-curve threshold tuning were used together with SMOTE but never compared with it separately.

## batch012

useaudit batch 012: done, 20 of 20 records coded (out/batch012_coded.csv)

Counts
n=20; source: fulltext=4, abstract=16; is_application: yes=20, no=0
inside_folds (full text only): stated=3, before-split=1, nr=0, na=16
test_balanced: yes=1, no=3; vs_none: yes=1, no=3; vs_weights: no=4; calibration: yes=1, no=3
validation: internal=6, external=1, nr=13; confidence: high=8, medium=12

Check first
1. R12074 inside_folds=stated rests on the described step order (stratified split in IV.C, then the resampling-classifier pipeline in IV.D) and test metrics that fit a natural test set (recall 79/98); there is no explicit "training data only" sentence. A strict reading could give nr.
2. R12886 before-split and test_balanced=yes: SMOTE on the whole corpus, then Chi-Square, then the 60:40 to 90:10 splits; the 90:10 test confusion matrix has 949 near-balanced cases from 3078 tweets.
3. R21620: the reported accuracy, precision and recall imply a "positive" class with ~80-86% prevalence, so the precision/recall/F1 probably refer to the non-sarcopenia class. This is the only record with calibration=yes (plots, Brier) and net benefit.
4. resampler=other on five abstract-only records whose oversampling method is unnamed: R21056, R11123, R09949, R10444, R15731. Learner is na for R11123 (not named); measures is na for R21056, R09919, R10444 (none named).
5. Stakes calls: R12074 (transaction fraud) coded other, R12745 (bank account application fraud) coded individual.
6. R11291 validation=external rests on a temporal split (NHANES 2021-2023 cycle held out).
7. R20963 (abstract only) lists SMOTE-Tomek in preprocessing and then the 80:20 split, so it is likely before-split if the full text is obtained.
8. R09919 is a retracted paper (per its title). Domain calls to check: R09949 software vs security, R08675 social vs business.

## batch013

useaudit batch 013: n=20, fulltext=4, application=20, inside_folds stated=3, before-split=0
Other counts: inside_folds nr=1 (R20791), na=16 (abstract only); confidence high=1, medium=16, low=3.
Full texts: R13480, R08273, R20791, R15046. R15046 is the only one that assesses calibration (curves, Brier, Hosmer-Lemeshow, decision curves).

Check first:
1. R13484: coded application with deep-generative resampling (GAN, VAE-GAN); no SMOTE or random oversampling named. The VAE-GAN hybrid could count as its own resampling method, which would make it is_application=no.
2. R13480: inside_folds=stated (Sec 2.5 says SMOTE on training data only, within folds). But Table 1 gives whole-dataset counts after augmentation and SMOTE (288), which contradicts that. Test metrics imply 42 original test images.
3. R08273: inside_folds=stated rests on one sentence ("applied to the training dataset"). The split is never described.
4. R14986 and R13959: resampler=other because the method is not named ("oversampling techniques"; "adaptive oversampling strategy", possibly ADASYN).
5. R19386: resampling is CT-GAN only (deep-generative), with no SMOTE. Check that it belongs in the audit population.
6. Fraud records R11520 and R07344: stakes coded individual (transaction flags affect cardholders). Make this the same as other batches.
7. R07344: "Precision-Recall indicator" coded PR-AUC. R09194: measures=na because the abstract names no measure.
8. Validation coded internal for abstracts that report results on one dataset without describing a split: R13484, R21818, R09185, R07408.
9. R08089 (abstract only): the order of steps in the abstract suggests SMOTE was applied before the ten-fold CV. The full text would settle inside_folds.

## batch014

useaudit batch 014: done, 20 of 20 records coded (11 November 2026)

Counts: n=20; source fulltext=0, abstract=20; is_application yes=19, no=1; inside_folds stated=0, before-split=0, nr=0, na=20 (all abstract-only); validation internal=7, external=1, nr=11, na=1; resampler SMOTE=15, ADASYN=1, not named (na)=3 of the 19 applications; confidence high=8, medium=9, low=3.

Check first:
- R11369 (low): the abstract names no resampling at all, only class imbalance. It is coded as an application on the strength of the E1 screening, with resampler na. Recode is_application to no if the full text uses no resampling.
- R12347 (medium): coded is_application no, because it proposes its own sliding-window oversampling framework for CNN sleep staging. This is borderline: a checker may prefer yes with resampler other.
- R07566 (low) and R08816 (low): the methods are not named, so resampler is na, and learner is also na for R08816. R07566 may describe a new hybrid resampling scheme.
- R21259 (high): the best full-text target. The abstract reports no-SMOTE models, Brier score, calibration plots and decision curves, so vs_none and calibration are na only because the record is abstract-only.
- Validation rule used: internal when the abstract mentions any split, training set or cross-validation, even one used only for training or tuning (R20842, R17726, R15873, R16468), or says external validation is still lacking (R20009); nr otherwise. R19462 is coded external because of its China-to-Australia/Malaysia generalization.
- Possible leakage, to check in the full texts: R15873 (SMOTE "employed first", before feature selection), R12121 (labels are clusters of the same features, with F1 of 1.00), R20842 (accuracy and AUC both 97.46%), R16468 (every measure 99.95%).
- Stakes convention: card-transaction fraud (R07566, R11369) is coded other; electricity theft (R19462) is coded individual because it flags consumers.

## batch015

useaudit batch 015: done, 20 of 20 records coded (out/batch015_coded.csv)

Counts: n=20; source fulltext=0, abstract=20; is_application yes=20, no=0;
inside_folds stated=0, before-split=0, nr=0, na=20 (no full texts, so all FT fields are na);
validation internal=8, external=1, nr=11; stakes individual=9, other=11; confidence high=10, medium=10.
Resamplers: SMOTE 16, SMOTE-Tomek 2, random-oversampling 2, Borderline-SMOTE 1, ADASYN 1, SMOTE-ENN 1, undersampling 1.

Check first:
- R19710: abstract says SMOTE was applied only to the training partition; inside_folds would be "stated" if the full text is obtained (na for now under the abstract rule).
- R15366: abstract reports SMOTE turning 1,141 reviews into a 1,923-review "balanced dataset" (positives also rose), which hints at resampling before the split; candidate for before-split if the full text is obtained.
- R11486, R07927: stakes coded individual for fraud detection (judgment call). R07927: Isolation Forest/LOF coded learner other; AllKNN coded undersampling.
- R21750: "dynamic oversampling with continuous augmentation" (no SMOTE) coded random-oversampling; check that it belongs in the audit.
- R17069: "BSMOTE" (boundary-aware SMOTE) coded Borderline-SMOTE.
- R21688: validation internal only because the abstract mentions GridSearchCV; abstracts with no split or CV statement were coded nr (11 records).
- R12913: modality time-series (PMU) could be tabular (MSU-ORNL rows of features). R20806: construction risk coded industry, modality mixed.
- R17992: measures include calibration and net-benefit (abstract names calibration curves and DCA); the calibration field is na under the abstract rule.

## batch016

useaudit batch 016: n=3, fulltext=0, application=0, inside_folds stated=0, before-split=0
source: abstract=3, fulltext=0. is_application: yes=0, no=3 (all three code as "proposes own resampling method", so every other field is na).

Check first:
1. R01235 (rec 2), is_application=no, confidence low. Easy-SMT combines a SMOTE-based oversampling policy with EasyEnsemble and is called a new "imbalance learning algorithm". If it counts as a new ensemble classifier that applies existing SMOTE, recode it as yes (industry: wind turbine failure forecast challenge, PHM 2015 data).
2. R01361 (rec 1), is_application=no, confidence high. The abstract presents a DCGAN oversampler as the proposed method and compares it with other resampling algorithms. DCGAN is an existing architecture; if that counts as applying existing deep-generative resampling, recode it as yes (industry: rotating-machinery fault diagnosis).
3. R02901 (rec 3), is_application=no, confidence high. The abstract says explicitly that it proposes a VAE-based oversampling method (credit card fraud), with SMOTE and GAN oversamplers as baselines.
All three disagree with the E1 exclusion reason ("applies existing resampling"), so their screening decision may need another look.

## batch017

useaudit batch 017: n=5, fulltext=1, application=5, inside_folds stated=1, before-split=0, nr=0 (4 abstract-only records have na)

Check first:
1. R02506 (full text) inside_folds=stated. The GAN is fit on the training data after the split and the test data are not resampled. But the controller picks the weak classes (and accepts synthetic batches) from the reported test F1 (Table III), and the Table III supports mostly equal the full-data counts (Table II), not the test remainder. nr may be the safer code. is_application=yes under B2 (plain GAN plus a controller loop); the weak-class allocation could be read as a "new allocation".
2. R01235 is_application=yes, low confidence. Easy-SMT (SMOTE + EasyEnsemble) is presented as the contribution, but the abstract shows a comparison with baseline classifiers only. If the full text compares it with other resampling, rule B makes it the paper's own method (no). learner=boosting and modality=time-series are assumptions.
3. R12347 is_application=yes because sliding-window oversampling is standard data augmentation (B2). The abstract names no SMOTE or ROS, so resampler=other. Modality coded time-series (the CNN inputs are CWT spectrograms).
4. R01361: DCGAN treated as a standard generator (B2). The compared resamplers are not named, so resampler=deep-generative only; learner=na; modality assumed.
5. R02901 stakes=other (the model flags transactions, not people).

## batch018

useaudit batch 018: the corrections of the independent AI check (Claude Fable 5.2, report v3), applied by scripts/apply_check_code_corrections.py to the current codes of 4 records (R00847, R01960, R06167, R10600); no session coded this batch.

## batch019

useaudit batch 019: n=10, fulltext=0, application=7, inside_folds stated=0, before-split=0

All 10 records were coded from title and abstract (no full texts), so every FT field (inside_folds, vs_none, vs_weights, calibration, test_balanced, evidence) is na.
is_application yes: R00717, R01133, R01745, R06457, R02955, R05675, R05286. no: R00777, R00454, R00164 (generic imbalanced-classification methods with no domain problem).

Check first:
- R00717 (low), R02955 (low), R05675 (low), R01133 (medium): coded yes because the abstract states no comparison with another resampling method (rule B). Each presents its chain as its contribution (BDSK; PCA+MWMOTE; resampling in a VAE latent space; BSMOTE-Tomek/ENN), so if the full text compares it with another resampler, recode no.
- R05675: the abstract says the testing set is balanced, so test_balanced would be yes with the full text. R06457: train and test accuracies are reported "with a balanced dataset", so the oversampling may have come before the split.
- A field is na when the abstract does not name it (these fields have no nr value): learner for R00717, R01745, R02955, R05675; modality for R01745, R02955; resampler for R06457 (the oversampler is not named). R01745 domain is coded security but could be social (social-bot detection).

## batch020

useaudit batch 020 (round 2, library full texts), coded 16 November 2026
n=8, fulltext=8, abstract=0, application=7 (no=1: R00777)
inside_folds: stated=3, before-split=3, nr=1, na=1
test_balanced: yes=4, no=2, nr=1, na=1
vs_none yes=5; vs_weights yes=0; calibration yes=0; validation internal=7
confidence: high=4, medium=4

Check first:
1. R01735 is_application=yes: rule B borderline. A SMOTE+NCL chain is "adopted" in the IDS pipeline and compared with SMOTE alone and with no resampling (Table IV), but the stated proposal is the DBN-PNN model. If a checker reads the chain as the paper's presented contribution, this becomes no.
2. R02029 inside_folds=stated, test_balanced=no: the text conflicts. Sec. 4 says SMOTE was applied "on the training data only", but Sec. 2.1 says all 32 accidents were raised to 85,182 (the full non-accident count). Table 2 (ACC 99% with DR 48%) rules out a balanced test set.
3. R01361 is_application=yes under B2: the DCGAN is called "new"/"proposed", but no change to it is stated. test_balanced=yes because the test set is balanced by selection (100 per class), not resampled.
4. R01572: resampler=other (class-targeted flip augmentation of patches, not SMOTE). inside_folds and test_balanced are nr because the paper does not say whether the over-sampling touched only the training patches.
5. R02298 before-split / test_balanced=yes rest only on rule-D arithmetic. Fig. 7 implies a positive share of 0.500 in the evaluated folds with SMOTE versus 0.242 without (NB and SVM alike).
Clear-cut before-split cases: R02733 (authors state synthetic samples were in the holdout folds) and R02561 (the test confusion matrix holds 19 Tetraploid cases, but only 9 real ones exist).

## batch021

useaudit batch 021 (round 2, library full texts, 16 November 2026)

Counts: n=8; source fulltext=8, abstract=0; is_application yes=6, no=2;
inside_folds (applications) stated=2, before-split=1, nr=3; test_balanced yes=1, no=3, nr=2;
vs_none yes=4; vs_weights yes=0; calibration yes=0.

Check first:
1. R02621 is_application=no. Application-framed (seismic retrofit screening), but the full text calls CBS (k-means, mini clusters dropped, SMOTE per cluster) "a new strategy" it developed (Sec. 2.2, Conclusions) and compares it with SMOTE, COS, CUS: own under Rule B. The abstract alone did not show this.
2. R00717 is_application=no. BDSK (k-means undersampling plus SMOTE on the smaller minority cluster) is the paper's contribution and is compared with RUS+SMOTE, k-means SMOTE, k-means undersampling (Tables III-IV): own under Rule B.
3. R02483 inside_folds=before-split, test_balanced=yes. Rests on the described order (Sec. IV.A balances every class to 3500 in pre-processing; Sec. V then splits "the data set" 60/20/20). No explicit sentence and no arithmetic basis.
4. R02261 inside_folds=stated, test_balanced=no. Sec. II-B says oversampling applies after the split, but the Sec. II overview says the reverse. Table II recalls weighted by the natural test counts reproduce the accuracies (balanced would give ~54%, not 60.75%).
5. R02432 inside_folds=nr, test_balanced=nr. No split described. The conclusion speaks of balancing "the datasets" (training and testing), but the Sec. IV figures fit an unbalanced test set.
6. R01271 inside_folds=nr, validation=nr. Fuzzy-clustering segmentation scored on the same images (resubstitution); no split exists. Confusion-matrix row sums equal the original class counts, hence test_balanced=no.
7. R02884 inside_folds=nr. SMOTE on the 59,000/1,000 training set before a 5-fold tuning CV; which data the cost scores come from is not stated.
8. R01633 vs_none=yes rests on an ablation reported in words only (no numbers).

Conventions used: confusion matrices are not coded under measures; oversampling with augmented copies is coded random-oversampling plus other (R02483, R02261).

## batch022

useaudit batch 022: done (round 2, library full texts, 16 November 2026)
n=8, fulltext=8, abstract=0, application=7 (no=1)
inside_folds: stated=1, before-split=5, nr=1, na=1
test_balanced: yes=5, no=1, nr=1, na=1
vs_none yes=2, vs_weights yes=1, calibration yes=0, validation internal=7
before-split / test_balanced=yes on arithmetic (rule D, BASIS in evidence): R01835, R06350 (Table 2 class counts), R03028

Check first:
1. R03028: before-split and test_balanced=yes rest on arithmetic (precision 0.9976 impossible on a natural 20% test with ~122 events; Tables 6-8 imply test N:P ~1 vs natural 17.3) and contradict the stated order (80/20 split, then sampling "while training").
2. R01835: before-split and test_balanced=yes rest on arithmetic only (own metrics imply test N:P about half the natural ratio on all three datasets; competitors' rows fit the natural ratio). Modality coded other (protein-sequence windows).
3. R06494: before-split from the pipeline order alone (SMOTE to "data parity" on 216/87 in preprocessing, then feature selection, then 10-fold CV); no numbers to check; one sentence mentions "training data".
4. R00221: is_application=no (existing Random-SMOTE vs none with logit on five generic UCI sets, no domain problem); if recoded yes, it resampled before the 2/3 split.
5. R02316: inside_folds=nr, test_balanced=nr; validation=internal although the main text describes no split or CV; vs_none=no (no proposed-features-without-balancing row).
6. R01349: validation=internal for spatially separate test regions of the same image (arguably external).
7. R00467: domain industry (aero-engine wear fault diagnosis) rather than transport.

## batch023

useaudit batch 023 (round 2, library full texts, coded 16 November 2026)
n=8, fulltext=8, application=8, inside_folds stated=1, before-split=7, nr=0
test_balanced: yes=7, no=1, nr=0; vs_none yes=2; vs_weights yes=0; calibration yes=0
confidence: high=4, medium=3, low=1

Check first:
1. R06106 (low): the text says SMOTE was applied to the whole data (541 to 728) before the holdout/CV split, but the three headline accuracies are exactly 150, 147 and 115 of 163, and 163 = 30% of the original 541 (30% of 728 = 219). The reported test set may be unresampled. Coded before-split / test_balanced yes from the text; the result tables were not extracted.
2. R04275 (medium): split 70:30 first, then SMOTE-ENN applied to the training AND the test set (Table 5: test 214/26 to 168/198; the "after" metrics fit the resampled test set). No category fits exactly; coded before-split as the closest. vs_none = yes, but the "before" metrics are on the natural test set.
3. R03716 (medium): before-split / test_balanced yes rest on "In SMOTE, the entire dataset is used as the input"; the order of SMOTE and the 60/20/20 split is not explicit, and RAF-DB test counts are not reported.
4. R03964 (medium): no split or CV described; before-split and test_balanced yes come from "this data was used for analysis"; validation nr; stakes other (classifier used to find a key HRV predictor).
5. R03330 (high): domain coded business (bank telemarketing), not finance.

## batch024

useaudit batch 024 (round 2, library full texts), coded 16 November 2026
n=8, fulltext=8, application=8
inside_folds: stated=2 (R06678, R07043), before-split=0, nr=6
test_balanced: yes=1 (R07084), no=4, nr=3
vs_none yes=4, vs_weights yes=1 (R07043), calibration yes=0, validation internal=7, nr=1
confidence: high=1, medium=5, low=2

Check first:
1. R07084: no predictive model or split (K-means, then Borderline-SMOTE on the 5-user cluster, then TOPSIS). test_balanced=yes only because the reported category profiles use real plus synthetic curves; inside_folds and validation nr. Poor fit to the codebook.
2. R06049 and R04991: test_balanced=no rests on arithmetic only (rule D names arithmetic only for before-split and yes); inside_folds nr because not stated. R04991 validation coded internal although the abstract says "external" (same TCGA-LGG cohort).
3. R05027: the "full text" is the meeting abstract itself. Oversampling method unnamed (resampler other). "Equal proportion of TxE samples maintained across all datasets" may mean the test set was oversampled (coded nr).
4. R04368: Eq. 4 gives a non-standard SMOTE placement but the paper calls it plain SMOTE (coded SMOTE). vs_none=yes only through a bundled "without preprocessing" arm. Reported accuracy exceeds both sensitivity and specificity.
5. R07289: domain other (EEG emotion recognition; could be medicine), stakes individual. R06678: coded as an application although it compares three oversamplers and tunes the ratio (rule B "choice among samplers").

## batch025

useaudit batch 025, round 2 (library full texts), coded 16 November 2026
n=8, fulltext=8, abstract=0, application=6 (no=2: R05299, R05434)
inside_folds: stated=1, before-split=3, nr=2
test_balanced: yes=2, no=1, nr=3; vs_none yes=3; vs_weights yes=0; calibration yes=0
validation: internal=4, external=1, nr=1; confidence: medium=8

Check first:
1. R04903: before-split is stated in the text (III.D: "After applying the SMOTE technique on the whole data, the ten-fold CV results"), but the Table III hold-out test rows sum to 37,791 = 30% of 125,973 with natural counts (U2R 15); test_balanced coded nr because of this conflict.
2. R06158 and R04005: before-split and test_balanced=yes rest on rule D arithmetic only (BASIS in evidence). R06158: same-threshold accuracy/recall/F1 imply ~50% defective test data (natural 6.9-19.4%). R04005: whole-data counts after MLSMOTE, 778 = 508 + 270 synthetic, before 10-fold CV.
3. R05434: is_application=no under rule B (BBR-OFS is a search for how much to oversample, presented as the contribution and compared with weighted SVM); if upheld, the E1 exclusion of this record needs review.
4. R05299: metadata mismatch. Title, DOI and full text are a perovskite solar-cell paper without resampling (coded no); the record's abstract belongs to a credit-card fraud paper with over- and undersampling, which may need its own record.
5. R05566: vs_weights=no although cost-sensitive learning is used (always combined with an oversampler, never compared alone); validation=external rests on five alloys only (Table 2).
6. R04730: full text was in a shifted font encoding (decoded, digits lost) and reports no evaluation (measures na, validation nr). R05603: Borderline-SMOTE + Tomek links coded Borderline-SMOTE;undersampling, domain medicine (arguably bio).

## batch026

useaudit batch 026 (round 2, library full texts), coded 16 November 2026
n=8, fulltext=8, abstract=0, application=8
inside_folds: stated=4, before-split=4, nr=0
test_balanced: yes=4, no=4, nr=0
vs_none yes=7; vs_weights yes=0; calibration yes=0; validation internal=7, external=1
Rule D (BASIS) arithmetic used: R07062, R06579

Check first:
- R07062: before-split and test_balanced=yes rest on Rule D only (CM1 'Pure' accuracies are k/69 = 20% of 344, SMOTE columns k/128; KC3 40 vs 62). Denominators do not match a clean 1:1 SMOTE, and several SMOTE columns repeat across tables.
- R06980: before-split and test_balanced=yes read from 'First, we resampled the dataset' followed by a 70/30 per-class split; stakes=individual although the units are debtor corporations.
- R18088: validation=external rests on the zero-shot test of source-trained models on Cleveland (same UCI heart-disease family; the authors call it a related benchmark family).
- R14882: validation=internal although faults were split temporally; measures=other (FCLC-curve AUC, AUC10); vs_none=no (every run resamples); domain energy rather than industry.
- R09006: explicit before-split (SMOTE-Tomek, then 80/10/10); its confusion matrix (128/133 correct) does not match the reported 98.99% accuracy; log-loss taken from the 'Loss' column.
- R06579: domain=environment for drinking-water quality (public health is the alternative).

## batch027

useaudit batch 027 (round 2, library full texts), coded 16 November 2026
n=8, fulltext=8, application=8
inside_folds: stated=2, before-split=4, nr=2
test_balanced: yes=4, no=2, nr=2
vs_none: yes=4; vs_weights: yes=2; calibration: yes=0; validation: internal=8

Check first:
- R14731: before-split and test_balanced=yes rest on Rule D arithmetic (Table V metrics imply ~50% faulty in the evaluated data, natural 9.5-33%), against the paper's explicit statement that SMOTE was applied to the training portion only.
- R12857: before-split from the stated order (SMOTE on the datasets, then 3-fold CV); test_balanced=yes from aggregated summaries (SMOTE-arm F-measure ~ accuracy).
- R18816: vs_weights=yes only because "all models incorporated balanced class weights", so the imbalanced-data baseline appears class-weighted; inside_folds and test_balanced nr; reported metrics fit neither a natural nor a balanced test set.
- R10548: is_application=yes under B2 (plain MLP conditional GAN, "CTGAN-inspired", called "the proposed GAN model"); vs_weights=yes from the cost-vs-threshold curves (Fig. 6).
- R10548, R18816, R11193 (card fraud): stakes=individual, read as approve/decline decisions on customers' payments.
- R09665: inside_folds=nr; the data are "first split", but the text does not say which part SMOTE was applied to.

Process: listed U/work/ once to confirm it exists; this showed the file names of other batches' chunk files, none of which was opened.

## batch028

useaudit batch 028 (round 2, library full texts): done 16 November 2026
n=8, fulltext=8, application=8, inside_folds stated=4, before-split=4, nr=0
test_balanced yes=5, no=3; vs_none yes=2; vs_weights yes=2; validation internal=7, external=1; confidence high=2, medium=6

Check first:
1. R12745 (bank account fraud): inside_folds=stated (SMOTENC/NearMiss on the 75% training part; counts add up per class) but test_balanced=yes on rule D: the test set is exactly 10:1 against ~1% fraud in the paper's Table 3, which points to an undisclosed cut of the majority class before the split. Decide whether that makes it before-split. vs_weights=yes only because default and tuned thresholds are compared.
2. R18227 (T2DM screening): before-split and test_balanced=yes rest only on rule-D arithmetic (test confusion matrix 500/500); datasets not named.
3. R13388 (heart disease): before-split rests on the stated step order (SMOTE, then feature selection, then 75/25 split); reported metrics do not reconcile (Table V accuracies are k/101; XGBoost figures copy cited study [3]).
4. R11123 (precision marketing): before-split rests on "data preparation, oversampling, and splitting"; resampler=other because the oversampler is never named.
5. R22074 (XFEL vacuum pumps): validation=external, not deployed or prospective (model applied to 54 other pumps' later data, with no stated operational use).
6. R09949 (smart contracts): vs_none=yes only through training accuracy/loss curves; domain software vs security.

## batch029

useaudit batch 029 (round 2, library full texts), coded 16 November 2026
n=6, fulltext=6, abstract=0, application=6
inside_folds: stated=3, before-split=1, nr=2
test_balanced: yes=1, no=3, nr=2
vs_none yes=1; vs_weights yes=1; calibration yes=0
validation: internal=5, external=1; confidence: medium=5, low=1

Check first:
1. R11520 test_balanced=no (low confidence). The text says SMOTE was applied to the training data after the split, but Table 1 fits no 3.5%-fraud test set: ATAD-Net P/R/accuracy imply 22% fraud, CNN/RNN 7-9%, and a 50/50 test set would give 96.9%. I read this as incoherent numbers, not as a Rule D basis for yes. stakes=individual (card transactions) is a judgment call.
2. R10444 before-split / test_balanced=yes come from the stated order in Sec. III-B: oversampling first, then the "dataset was subsequently split" 60/20/20. resampler=SMOTE only: the framework's own "moderate oversampling" method is unnamed, and SMOTE is named only for the SMOTE-XGB comparator.
3. R15526 inside_folds=stated rests on one results sentence ("Balancing the training data with ADASYN"). The methods section is silent on the order, so nr is arguable.
4. R15731 resampler=undersampling;other: the oversampling method is unnamed (imblearn, per-class rates by incidence; not presented or compared as a method). validation=external rests on 38 MMA cases from another hospital, positives only.
5. R13484 is_application=yes under B2 (plain GAN; VAE-GAN with no stated change). validation=internal although the evaluation split is not described.
6. R14986 text contradicts its abstract (public symptom data, not environmental; "lung cancer" in Sec. IV). Only accuracy is reported.
