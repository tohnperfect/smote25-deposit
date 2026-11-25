# Notes of the coding sessions (coverage)

## batch001

coverage batch 001: n=6, fulltext_ok=6, eligible=3, Core=2, Partial=0, Not counted=1
Not eligible: E1=2 (R00007, R00308), NOT-GEN=1 (R00416).

Check first:
1. R00277 (Alejo 2012, modified back-propagation): eligibility is borderline. SMOTE itself is unchanged (it balances the training set once); the contribution is an MSE-driven rate that picks how many minority samples (original + synthetic) to feed in each epoch. Coded eligible, Core, A=yes, L=yes. L is the least certain call: the pool is redrawn every epoch, but SMOTE runs once. measures "other" = minority-sample counts.
2. R00007 (Akbani 2004, SDC): coded E1 (plain SMOTE + Veropoulos different error costs for SVM, generator unchanged). The abstract says "variant of SMOTE", but the full text uses SMOTE as is, without undersampling. The alternative reading is eligible, Core, no decision point changed.
3. R00308 (Jeatrakul 2012, OAA-DB): coded E1. SMOTE(1:1)+CMTNN cleaning comes from the authors' earlier papers [18,19]; it is applied per one-against-all subproblem with a codeword decision rule. The alternative reading is eligible, Core, F=yes (CMTNN removes misclassified points), class M.
4. R00002 (SMOTE 2002): inside_folds=stated rests only on Sec 4.2 (training-fold sizes in 10-fold CV, mammography experiment); Sec 5 is silent. vs_none=no: raw data appears only as the ROC-curve start point. n_datasets=9 counts Can (simulation output) and Adult (continuous features, Sec 6.1). tuning=test: only the best SMOTE curve is shown.
5. R01882 (ICVAE-DNN): n_datasets=2 (the paper counts KDDTest+ and KDDTest-21 as two datasets); FPR coded as specificity; tuning=validation applies to the proposed model only (competitor settings not reported).
6. R00416 (INNO): NOT-GEN. It pseudo-labels existing unlabeled points and creates no synthetic points. High confidence.

Codebook vs tool: the codebook sets sections 2-4 to na for ineligible records, but add_codes.py requires confidence to be high/medium/low. For ineligible records, confidence states confidence in the eligibility decision, and note is left na (reasons are given here).

## batch002

coverage batch 002: n=6, eligible=6, Core=1, Partial=0, Not counted=5
(excluded: 0; fulltext_ok=no: 0)

Check first:
1. R09141 (IQRBUwOGA, Core). Borderline E1: IQRBU + GenSMOTE [12] where the only change is the GA selection operator (selBest); I coded it eligible. A=yes and L=yes come from GA-optimised SMOTE oversampling rates (fitness = decision-tree F1). The paper never defines the rates R1..RN (per instance or per class), but A=yes holds either way. Table 2 values are missing from the extracted text. Protocol coded 'other' (95/5 split plus 3-fold CV).
2. R18850 (DIAO/DIAO-CP). Eligibility: semantic segmentation coded as pixel-level classification. Label: alpha-blended copy-paste of rare objects onto filtered tiles coded Not counted / generator 'other', not two-instance interpolation. n_datasets=5 counts 4 Chesapeake regions + OEM. stat_test=yes rests on 95% CI overlap only. vs_cost=yes because the baseline uses focal loss.
3. R07729 (AEMLO). Multi-label (14-374 labels) mapped to class M. vs_smote='wrapper' because MLSMOTE is the only SMOTE competitor. Modality coded tabular (feature-vector benchmarks from text/biology/music/image domains); 'mixed' is arguable.
4. R17554 (PCT-GAN). vs_cost=yes only because RF uses class_weight='balanced' in every run, including NoAug. code=no: a 'public repository' is claimed but the text gives no link.
5. R15093 (Quantum-SMOTEV2). inside_folds=before-split rests on 'applied to the entire dataset' (Sec. 4.1.2). Named SMOTE, but each new point is a rotation of one point, so Not counted / perturbation.
6. R04920 (latent-preserving GAN). inside_folds='stated' is read from the fixed train/test sets in Table I; there is no explicit sentence.

## batch003

coverage batch 003: done
n=1, fulltext_ok=1, eligible=0, Core=0, Partial=0, Not counted=0
exclusions: E2=1 (R22331)

Check first:
- R22331 (Wang et al., EPSR 2027, charging-station planning), eligible=no, E2. Borderline: the paper proposes its own
  route-based SMOTE, which interpolates between temporally adjacent observations of the same EV (Sec. 3, Eqs. 6-12).
  It fails I1 only on "for classification": the balanced data feed only an improved Mean Shift clustering for station
  siting (Sec. 4, Sec. 6). The classes are rule-defined (SOC thresholds and scheduling windows, Table 1) and no
  classifier is trained or evaluated. Possible alternative exclusion: OTHER (facility planning). If a checker reads I1
  more loosely, the generator would be Core (two-instance interpolation, evenly spaced lambda = s/(S+1)).
- Tool vs codebook: add_codes.py requires a "rec" key, which the codebook does not name. It also rejects
  confidence=na for ineligible records, although the codebook sets sections 2-4 to na for them. Here confidence=high
  refers to the eligibility call. The note is free text; every other section 2-4 field is na.

## batch004

coverage batch 004 (codebook v1.1): n=2, eligible=2, Core=2, Partial=0, Not counted=0

Check first:
1. R00007 (SDC, Akbani et al. 2004): eligible as "SMOTE inside a cost-sensitive learner" (plain SMOTE, then SVM with class-specific error costs). The change lies outside the generator, so S/A/N/P/F/L are all no (explained in note).
2. R00007 evaluation: tuning=test because the kernel was chosen "based on the best empirical results" on a single 70/30 split with no validation set. inside_folds=stated rests on parallel wording ("undersampled the training data ... For SMOTE we oversampled the data instead of undersampling it"), not on an explicit sentence about SMOTE/SDC.
3. R00308 (OAA-DB, Jeatrakul & Wong 2012): eligible as a multiclass decomposition scheme for oversampling with a cleaning step (one-against-all + SMOTE to 1:1 + CMTNN removal of misclassified patterns from both classes). Only F=yes. A=no (allocation unchanged inside each one-vs-all problem); L=no (generator runs once before the codeword-triggered retraining, no iterative loop). class=M (3, 6, 10 classes kept; binary sub-problems are internal to the method).
4. R00308 evaluation: measures add recall (per-class accuracy, Tables IV/VI/VIII) and balanced-accuracy (their "Average" row = mean of per-class accuracies, checked) to accuracy and macro-F1. protocol=repeated-holdout although the paper calls its ten random 80/20 splits "cross validation". n_datasets=3 counts Balance Scale, which the paper says "was generated to model a psychological experiment" (2 if generated UCI data count as synthetic). vs_smote=no: OAHO's balancing technique is not said to be SMOTE. inside_folds=stated from the method text ("each training set is applied by the data balancing technique"); tuning=nr (ANN, SMOTE k and CMTNN settings not reported).

## batch005

coverage batch 005: the corrections of the independent AI check (Claude Fable 5.2, report v3), applied by scripts/apply_check_code_corrections.py to the current codes of 2 records (R00002, R18850); no session coded this batch.

## batch006

coverage batch 006: n=6, eligible=5, Core=4, Partial=0, Not counted=1
fulltext_ok = no: 1 (R00144). Ineligible among readable texts: 0. Rulings B/B2: no record excluded.

Check first:
- R00144: the text is another paper by the same authors ("Visualizing the Yield Pattern for Multi Class
  Classification", AMS 2009, pp. 560-565, DOI 10.1109/AMS.2009.52), not "Visualizing the Pattern for Hard Disk
  Media Yield Prediction". It has no SMOTE experiments (SMOTE+SMaRT is only future work). Coded fulltext_ok = no,
  all else na. The right full text is needed.
- R00141: eligible, Not counted / other. The paper's own generator is taken to be Test 3: new minority texts made
  by appending paragraphs of minority-class texts to the original texts ("data reorganization"). Check (a) ruling B2:
  if a checker reads this as standard text augmentation, it becomes E1; (b) the label: text recombination, not
  interpolation. The text does not say clearly whose paragraphs are appended. Tuning = nr.
- R00004 (SMOTEBoost): S = yes rests on Sec. 3 ("new examples are constructed ... by sampling from Dt"; "focuses
  on the examples selected in the Dt"); Fig. 1 does not say how seeds are drawn. inside_folds = stated because SMOTE
  runs inside training by design (nothing said for the SMOTE baselines). tuning = test (full N grid, best in bold).
  protocol = cv, but KDDCup-99 was run on one holdout split.
- R00069: kRNN extreme-outlier removal before SMOTE coded S = yes (barred seeds), not F. The competitor is SMOTE +
  random undersampling, coded vs_smote = plain. Testing was "against entire dataset" with no split, so
  protocol = other and inside_folds = before-split; tuning = test.
- R00004 and R00069: the VDM distance for nominal/categorical features is not coded as N (treated as SMOTE's own
  nominal handling). Check that this matches how the team codes SMOTE-NC-style handling.
- R00022: the wrapper search for the SMOTE/undersampling amounts is coded A = yes, L = no (final sets are generated
  once per run). vs_smote = no (no fixed-amount SMOTE competitor, only the no-resampling baseline). FP-rate is coded
  as specificity; costs and cost curves as other. KDD-99 used its given train/test split.
- R00093: inside_folds = stated, read from "classifier applied to the original training set and to sets
  preprocessed by SMOTE" within 5x10-fold CV; the paper does not say it in so many words.

## batch007

coverage batch 007: n=6, eligible=6, Core=5, Partial=0, Not counted=1

Check first:
- R00015 (C-SMOTE): A=yes and L=yes for a multi-rate SMOTE ensemble are judgment calls. tuning=test because the vote weights come from F-measure on the test set. protocol=cv although satimage uses its given split. inside_folds=stated rests on Sec. III, while Sec. V says the competitors were "applied to the original data sets".
- R00101 (ADOMS): Core via the region clause (segment rotated onto the local first principal axis, equal to SMOTE at K=1); it could be read as Not counted/perturbation. n_datasets=12 counts five Letter variants separately (8 source sets).
- R00066 (SPSO, OCR text): generator=perturbation, where distribution (HMM profile) is the alternative. The main comparison is taken as the ROC one (measures=ROC-AUC, protocol=nr); accuracy/MCC from the "further evaluation" (2-fold and 5-fold CV) are left out. n_datasets=1 (GPCRDB).
- R00130 (MSMOTE): L=yes rests on MSMOTEBoost, described only as "similar with SMOTEBoost". F=no because majority noise is removed before generation.
- R00127 (ghost points): class=B+M assumes OSU Leaf kept its six classes (no collapse stated). n_datasets=14 includes six artificial sets that the text does not name. No other resampler was compared, but the method is the paper's own, so ruling B does not apply.
- R00074 (ADASYN): S=yes is coded alongside A=yes from the same difficulty weight; a checker may keep only A.
- None of the six texts was a journal-issue excerpt (pages 74 to 85). R00066 and R00015 look like the OCR texts. During the session the working directory was moved into d42 and v37 folders; nothing there was opened, listed or searched.

## batch008

coverage batch 008: n=6, eligible=5, Core=5, Partial=0, Not counted=0
Not eligible: R00112 (OTHER: master's thesis, fails I3). fulltext_ok = yes for all six; only R00077 reads as OCR (formulas garbled, readable); no text here is a journal-issue excerpt. Ruling B checked and passed for R00026 and R00006; no B/B2 exclusions.
Check first:
- R00112: excluded only on I3 (Maastricht master's thesis, 2009). If theses count, its Naive Bayes Sampling (features drawn independently from fitted marginals) would code Not counted, distribution.
- R00108 (BED): new point = centroid of seed and its minority neighbours among its k-NN; coded Core with P yes and N yes; majority removal treated as undersampling (F no).
- R00026 (EnSVM): ENN-type pre-filter before SMOTE coded S (not F); SMOTE runs once outside the SVM ensemble (L no); protocol repeated-holdout although a redraw of the split is not stated.
- R00018 (Borderline-SMOTE): N and P yes only through borderline-SMOTE2; tuning default although the text quotes best improvements over the amount sweep.
- R00006 (Smote+Tomek/ENN): n_datasets 13 UCI sources (15 binary tasks); N no although all k-NN use HVDM, shared with the SMOTE baseline.
- inside_folds: stated only where the protocol says the training sets were resampled (R00018, R00026); nr otherwise (R00006 "applied to the original data sets", R00108, R00077). tuning nr where an "optimal" setting was found "empirically" on unstated data (R00026, R00108); a checker may prefer test.
- R00077: vs_smote plain reads Sos+BSVM [13] as SMOTE plus Biased-SVM. ROC curves without AUC values (R00026, R00108) not coded as measures.

## batch009

coverage batch 009: n=6, eligible=6, Core=5, Partial=0, Not counted=1
fulltext_ok = yes for all 6; no exclusions (rulings B/B2 pass for all: each method is the paper's own or presented and compared).

Check first:
- R00711 (V-synth) label Not counted / perturbation: new point lies between the seed and a random point on a Voronoi facet bordering another class (not an instance), i.e. inside the seed's Voronoi cell. A checker may argue Core via the "region set by the chosen neighbour" clause; I found no way to shrink it to a seed-instance segment. vs_smote = no (only Borderline-SMOTE); FPR/FNR coded as specificity/recall.
- R00097 (SMMO / M-SMOTE) P = yes: partner is the mean of the 5 nearest positives; as printed (delta = m - A, eta = m + delta*U(0,1)) the point falls beyond the seed, away from the mean, while the prose follows SMOTE wording. Core kept either way. N = no despite an undefined "weighted distance".
- R00684 (SMOTE_mv) P = yes only because coordinates with missing values take the minority-class mean; N = yes (roulette weighted by non-missing attributes). tuning = test (SMOTE amount schedule picked from TP-rate experiments). n_datasets = 1 (Surgery data only).
- R00044 (BootOS) Hamamoto et al.'s bootstrap (mean of seed and k nearest neighbours; k = 1 in experiments, so the midpoint): Core with P; L = yes from the active-learning loop. n_datasets = 38 counts nouns of one corpus (OntoNotes). Recall is macro-averaged (equal to balanced accuracy) but coded recall.
- R00362 (NRSBoundary-SMOTE) A = no although Algorithm 1 has no amount input (one sample per neighbour per boundary seed) while the setup states 100% oversampling. tuning = test (w read off 10-fold CV F-value curves).
- R00382 (TSMOTE-AB) vs_none = yes rests on plain Bagging in Table 4, not KNN without resampling; tuning = nr (attribute-subset size j adjusted per dataset, data not stated); inside_folds = nr.

## batch010

coverage batch 010 (round 2, library full texts of 16 November 2026): done
Counts: n=6; fulltext_ok yes=5, no=1; eligible yes=3, no=2 (NOT-GEN=1, STUDY=1), na=1; Core=3, Partial=0, Not counted=0; no exclusion under ruling B or B2.
Check first:
- R00549 (del Rio 2014, MapReduce RF) coded STUDY: framed as a comparison of ROS/RUS/SMOTE/cost-sensitive RF ported to MapReduce, basic SMOTE run per mapper partition (Sec. 4.4). If that counts as a new way of applying SMOTE: eligible, Core, N=yes (ruling B would pass).
- R00184 (mix-ratio sampling) coded NOT-GEN: per-class ratio search over random over/under-sampling only, no SMOTE, no synthetic examples.
- R00252 (KSAMPLING): A=yes (IR-threshold amounts per cluster) and L=yes (resampled set per voting tree) are borderline; inside_folds=stated rests on the method being defined on the training set within 10-fold CV.
- R00339: fulltext_ok=no. The file is Xie et al. 2015 (Discrete Dyn. Nat. Soc. 562724), not Dong and Cai 2012 S-SMOTE (Computer Simulation 29(12)); the right text is needed.
- R00682 (SNOCC): three-point random convex combination coded Core with P=yes, N=yes; 3-fold CV x 100 runs coded repeated-cv.
Convention: for non-eligible and wrong-text records, evidence is na and the reason is in note.

## batch011

coverage batch 011: n=6, eligible=5, Core=2, Partial=0, Not counted=3
Not eligible: 1 (R00168, E1 under the base codebook, not a ruling). fulltext_ok=no: 0. Ruling exclusions (B/B2): 0.

Check first:
1. R00194 (KDEBS, Vajda & Fink 2010): B2 call. Kept eligible as own because the paper states a change to KDE sampling (diagonal covariance with K-means-estimated local variances instead of scalar bandwidth h; sampling in 80-PC PCA space). If that counts as a standard KDE setting, it becomes E1 with "ruling B2". Also: inside_folds=stated is read from the training-set counts and the official test sets; protocol=holdout (official split, 5 runs); tuning=test (PCs and topology "based on trial runs").
2. R00379 (COS-HMM): B2 not applied, because the generator is the paper's own (single-state HMM word model with document-frequency emissions, per-word Gaussian weights, length from a random class document). Generator coded distribution, not deep-generative/language model. n_datasets=3 (OHSUMED, TREC Allele, TREC GO); the paper says "two corpora".
3. R00361 (mutual kNN graph + MST + SMOTE): coded as own SMOTE variant (N=yes), so B not applied. Its only competitor is SVM without resampling, so it would fail B if read as existing parts. S=yes (isolated graph points cannot seed; seeds drawn via random MST edges); A=no though per-seed counts vary with MST degree. tuning=test (kernel chosen "after a lot of experiments"). Placement kept P=no: Alg. 1 draws lambda per attribute as in SMOTE's own pseudocode, but the text says "along the line segment".
4. R00495 (OUPS, two-page WSC paper): OUPS was first proposed in the authors' ICMLA 2014 paper (cited as accepted); this one extends its experiments. Check that it counts as proposing its own method (else STUDY). class=B and modality=tabular are read from the propensity-score setup; the four datasets and the classifiers are unnamed.
5. R00264 (SPO): vs_none=no; 1NN/1NN-DTW on unresampled data appear only in Table III, with learners other than SVM. tuning=validation (M chosen by 2-fold CV on training positives; SVM grid search per ref. [24]).
6. R00168 (SMRBF): the abstract suggests oversampling "using a memetic algorithm", but the full text has SMOTE run once in preprocessing (doubling GT) before the memetic RBF classifier. The note does not start with "ruling B" because base E1 already applies.

## batch012

coverage batch 012: n=6, eligible=2, Core=2, Partial=0, Not counted=0
fulltext_ok = yes for all 6 (each text is the paper the title names). Not eligible: R00374 NOT-GEN, R00640 E1 (ruling B), R02709 E1 (ruling B), R01695 NOT-GEN.

Check first:
1. R02354 (OSMOTE): Core with all six decision points "no". The only stated change is Orchard's fast nearest-neighbour search instead of k-NN (same nearest neighbours, same Minkowski distance), so N=no; the paper claims "better nearest neighbours", so N=yes is arguable. Also protocol = repeated-holdout (text says tenfold CV, but Tables 8-10 show ten random 70/30 runs, test n = 30% of original n) and inside_folds = before-split (text: "pre-processed rebalanced data was split"; test sets are near 50/50).
2. R02709 (parSMURF): E1 under ruling B. Plain SMOTE + undersampling inside the authors' existing hyperSMURF hyper-ensemble; new parts are parallelization and grid/Bayesian tuning of six hyper-parameters (fp, the SMOTE amount, among them). Compared only with untuned hyperSMURF. If tuning fp counts as "a search for how much to oversample", it becomes own and eligible.
3. R00374 (H-sampling bagging) and R01695 (SOTU): NOT-GEN because the minority is oversampled only by duplication (bootstrap copies / multiple copies), no synthetic points. The screen's rule-B codebook lists random oversampling under "classical"; confirm duplication-only methods are NOT-GEN at full text. Neither would fail ruling B for R00374 (presented and compared); R01695 has no experimental resampling comparison.
4. R02143 (CUSS): A=yes because the SMOTE total is set by the new minority-centroid distance rule (eqs. 1-3); its cluster-based undersampling of the majority is treated as outside the generator (F=no). "AUC" is single-point (1+TPR-FPR)/2 (eq. 9), coded ROC-AUC. tuning = nr (number of k-means clusters never reported).
5. R00640: E1 under ruling B. Unchanged Weka SMOTE per one-vs-all subset (MapReduce), compared only with OVA without resampling. Abstract names OVO too, but only OVA is run.

## batch013

coverage batch 013: n=6, eligible=4, Core=3, Partial=1, Not counted=0
Not eligible: 2, both E1 under ruling B2 (R01304, R02885). fulltext_ok = yes for all 6.

Check first:
- R00865 (banknotes, "modified SMOTE"): Partial / interpolation is a judgment call. The new image is the pixel-wise minimum of two
  minority images (a corner of the box the pair spans, not a point on the segment), plus flips and rotations. Not counted is
  arguable. N yes because every pair is used (no kNN). measures 'other' = PR curves. n_datasets 1: one image set binarised at
  three grade thresholds.
- R01304 (DOSS): excluded under B2 because the chain holds a standard cGAN (its configuration is taken unchanged from Douzas and
  Bacao). But that cGAN only makes majority samples; the minority gets plain SMOTE. Check whether the dual allocation should count
  as a new way of applying SMOTE.
- R02885 (two-attribute CNN): excluded under B2. The oversampler is standard mixup, the paper's contribution is the CNN, and the
  oversampler is never compared or ablated. The class-group pairing rule (D3-D3, D2-D3, D1 left out) could be read as an
  allocation of the paper's own.
- R01526 (SOM-SMOTE): the partner is the SOM subset centre. I coded both N and P yes (the centre combines several instances). I
  coded it eligible because Eq. 11 is a stated change; no other resampler is compared, so it would fail ruling B if read as
  "SOM clustering + SMOTE". measures 'other' = threshold-swept curve.
- R01801 (CBSMOTE): most of the text was in a font encoding shifted by 29 characters. I decoded it from the same file; numbers in
  those lines were lost. No classifier, split or settings found, so protocol, inside_folds and tuning are nr. The dataset comes
  from sensors on a simulated access-control testbed and is counted as one real dataset.
- R02083 (KMFOS): S is no even though a seed's chance of being picked varies with its cluster's size (coded under A). vs_none is
  yes from RQ1, where only the oversampling step is compared. inside_folds 'stated' rests on the training-set description under
  10x10 CV. tuning nr: parameter grids are given but not how values were picked.
- Tool requirements: add_codes.py needs a 'rec' key and a high/medium/low confidence on ineligible rows too. I gave both
  exclusions medium.

## batch014

coverage batch 014: n=6, eligible=5, Core=1, Partial=1, Not counted=3
Not eligible: R01069 (NOT-GEN). fulltext_ok = yes for all 6.

Check first:
1. R00736 (confidence low): eligibility and label are borderline. New minority examples are real reviews transferred from an auxiliary dataset (chosen by cosine similarity); SMOTE generates their N-gram features (Sec. 3.4, not detailed). Coded eligible, Partial, generator other (instance transfer), S=yes, P=yes. Alternatives: exclusion OTHER (transfer, not oversampling), or Core (SMOTE fills about 1385 of about 1406 feature dimensions). Also protocol=other (10-fold CV plus JD634 test set), inside_folds=before-split.
2. R01069: NOT-GEN. Boosting with weighted oversampling with replacement plus undersampling; Sec. 4 item (2) says it avoids generating non-existing samples. If replication were counted as generation it would be existing parts that pass ruling B (compared with SVM+SMOTE). The checker required a confidence value for this ineligible record; it rates the exclusion.
3. R01023 (FID): Not counted, generator=other (per-feature fuzzy-weighted means at evenly spaced points, features generated independently); could be read as distribution. tuning=default, but how one of three oversampling rates per competitor was reported is not stated.
4. Tuning: R02694 coded test (gamma and SVM parameters "searched for the best classification performance", no validation set); R02886 coded nr (K "selected from" {3,5,10,15}, criterion unstated; could be test).
5. inside_folds=nr for R02694 and R01571: both fit the sampler on "the training set/data" in the method section but never tie it to the CV folds.
6. R02886: vs_none=no; the Fig. 3 caption mentions "the original datasets", but the text says six methods and the tables have no no-resampling row.

## batch015

coverage batch 015 (round 2, library full texts of 16 November 2026; codebook v1.2 with rulings B, B2, C)
n=6, fulltext_ok=6, eligible=5, Core=4, Partial=0, Not counted=1, not eligible=1 (E1, ruling B)
R02528 Core | R00725 Core | R02035 Core | R01123 Core | R01804 Not counted | R01470 E1 (ruling B)

Check first:
1. R01470 (E1, ruling B): the abstract's "improved SMOTE" is the existing Safe-Level-SMOTE plus Tomek links, step 4 of an "improved KNN" text pipeline whose new part is NFS feature selection. I read "presented" as no. But the conclusion lists the SL-SMOTE+TL combination as its second contribution, and the pipeline is compared with SMOTE+KNN, so a checker could pass B (it would then be Core, 9-class Sogou text, 3 data sets). The tool requires a confidence value, so it is "medium"; evidence is "na".
2. R02528 (passes B, Core): a chain of existing samplers (SMOTE/Borderline-SMOTE/ADASYN/MWMOTE, then SSO-PSO majority undersampling), presented as own and compared with SSO-PSO, ADASYN and MWMOTE. Only F is coded yes (SSO-PSO removes majority points after oversampling); the S/A/N changes of the plug-in variants are not coded. n_datasets=5: the text says "six" UCI sets but names five. Hacide (980/20, 2-D) appears to be the simulated ROSE set (ROSE is in the reference list), so the count could be 4.
3. R02035 (Core): L=yes rests on the garbled Fig. 3 flowchart (resample, PSO rate update, retrain the SVM until no minority errors); the PSO fitness is not stated. Measures include majority-class recall and precision (coded specificity and other).
4. R01804 (Not counted, generator other): FF-SMOTE says it replaces interpolation with a firefly search inside bounds from randomly selected minority points; the pseudo-code is garbled. Its "AUC" is defined as (1+TPR-FPR)/2 (= balanced accuracy) but is coded ROC-AUC, as the paper names it.
5. R00725 (GASMOTE): A and L are yes. S is no because the bounds of the per-instance rates are not given (a zero lower bound would bar seeds). n_datasets=11 counts the VCR rockburst set (98 train/6 test) with the 10 KEEL sets. inside_folds and tuning are nr.
6. R01123 (SOMO): n_datasets=26 counts 13 UCI sets plus 13 versions with the minority undersampled (13 distinct sources). tuning=test: k, the intra/inter ratio and the grid size were picked to maximize the reported performance.
Only the codebook, these instructions, the two tools, the six full texts and the rulings file were opened.

## batch016

coverage batch 016: n=6, eligible=4, Core=2, Partial=0, Not counted=2
(excluded: R03490 E1 ruling B; R21735 E1. All 6 full texts were the papers named; fulltext_ok=yes for all.)

Check first:
- R03490 eligibility (ruling B): unchanged SMOTE after PCA/CAE feature extraction. Coded E1 because the stated contribution (Sec 1) is evaluating feature-extraction methods. But the abstract calls FE-before-SMOTE "our proposed method" and Table 1 compares it with SMOTE alone, so a "presented" reading would make it eligible.
- R14443 (MCSO) decision points: S=yes rests on the stated limitation that isolated points outside cliques cannot be oversampled. The formula is printed u + λ(u − v) (extrapolation as written) but the paper calls it SMOTE interpolation, so P=no. A=no even though seeds in several cliques get more points.
- R03697 (MECS-Ensemble): Core assumes centroid-member interpolation (O1/O3) counts as a convex combination. A=yes (size-proportional allocation, O_rate searched by the evolutionary algorithm) and L=yes (each individual generates data and trains a tree). n_datasets=39 counts binary splits of 15 UCI sources, as the paper counts them. The split protocol is not reported.
- R02145 (IQMOT): generator coded 'distribution' (new cases built from values drawn per quartile group of minority values); 'other' is defensible. tuning=validation rests on epoch selection by validation loss; the data used for the grid search is not stated. Balancing is done before the 80/10/10 split.
- R05572: generator coded 'other' (grid over feature ranges, labelled by a classifier, kept if predicted minority). Class B is inferred from binary metrics although the multiclass non-generative GDARMM2.0 appears in Table IV. n_datasets=2: the second dataset is identified only by the keywords and reference [12].
- R21735: software paper; the MASV-weighted SMOTE method comes from companion paper [9]. Coded E1; OTHER is the alternative.

## batch017

coverage batch 017: n=6, eligible=4, Core=2, Partial=0, Not counted=2
Not eligible: R21422 (NOT-GEN), R10073 (E1, ruling B2). All six texts are the papers named (fulltext_ok = yes); R03118 is an OCR text.

Check first:
1. R21422 (RRMP, rebalancing ratio): coded NOT-GEN. The method only sets the ratio; it is run with random sampling (Sec. 5.2.2, Table 2) or unnamed samplers and is never stated with SMOTE. The rulings count "a search for how much to oversample" as own, so a checker may prefer eligible with A = yes (the label would then need a decision).
2. R10912 (SS-EGAN): eligible, Not counted. Imbalance appears only in the abstract; the GAN makes images of both classes for data scarcity and the fakes enter only the critic loss (alternative: OTHER). Table bodies are missing from the text, so measures and vs_none rest on the prose.
3. R10073 (solar DDPM): E1, ruling B2. The model used in the classification experiments is a class-conditional DDPM with classifier-free guidance and no stated change. If the X-ray or ceVAE conditionings count as "new conditioning", it becomes eligible, Not counted.
4. R18541 (DualSS): Core rather than Partial. Latent-space interpolation is refined by diffusion denoising before decoding; N, P and F = yes. Check the label and P.
5. R03118 (MDGPDH-SMOTE, OCR): F = yes for the mean-test selection of the synthetic subset; read as the paper's own variant (not ruling B). If read as existing parts (refs [10][11]), it fails B: only SVM and RF are compared, no other resampling. protocol, inside_folds and tuning = nr.
6. R19707 (ICD-Balancer): protocol coded cv, but the text mixes an 80/20 split with three-fold CV. stat_test = no although Sec. 4.5 claims significance (no test shown). measures pooled over Fig. 8 and Tables 6-11.

## batch018

coverage batch 018: n=6, eligible=5, Core=1, Partial=0, Not counted=4
(not eligible: 1, E1; no record with fulltext_ok = no; no exclusion under ruling B or B2)

Check first:
1. R06105 (eligible = no, E1). ASYNO is the authors' own oversampler from an earlier paper (ref [11]). It is reused unchanged and not
   described here; the contribution is a DES (KNORA-U) stream classification framework. Coded E1 on the base criterion, not via
   ruling B (the framework is compared with six other oversamplers). The other reading is an own oversampler, which would leave the
   label uncodable from this text.
2. R21783 SMOMCCS (Not counted, perturbation). The "linear interpolation" is between two random points drawn uniformly in a ball
   around the minority centroid, not between instances. A checker reading only the formula may say Core. The paper's "AUC" is
   (1+TPR-FPR)/2, coded balanced-accuracy. Tuning = test (CF threshold c settled on CV test scores, Table 5). vs_cost = yes rests
   on the fuzzy-weighted twin SVMs (Sec. 5.6).
3. R08349 (Not counted). The M2M-style gradient translation of one majority seed is coded perturbation; `other` is arguable.
   Class M: three classes (N, S, V) are kept, but classified in two binary steps, so B is arguable. vs_smote = plain and
   vs_cost = yes come only from published results in Table V ([40] SMOTE, [12] batch-weighted loss).
4. R05755 AT-KSMOTE (Core, S/A/N = yes). N is taken from SMOTE applied per filtered cluster (not stated as a neighbour pool).
   F = no because noise removal precedes generation. Inside_folds = before-split: the whole datasets were balanced first.
   Tuning = test (k and ratio picked by the reported accuracy).
5. R14384 MTGP-SMOTE (Not counted, other): GP-evolved arithmetic expressions over minority instances. Tuning = test because a
   "Best of 30 runs" by test AUC is reported as a final result; the significance tests use the 30-run mean with fixed settings.
6. R19804 M-VAEGAN (Not counted, deep-generative; modified VAE-GAN, so it passes B2). The evaluation is coded for the brain-MRI
   classification only (n_datasets = 1); CIFAR-10, sketches and CelebA test generation quality only. vs_none = yes rests on the
   conclusion (72.6% without augmentation).

## batch019

coverage batch 019: n=4, eligible=4, Core=3, Partial=0, Not counted=1
(fulltext_ok = yes for all 4; no exclusions; no record failed ruling B or B2)

Check first:
- R08959 (HGDO): label Not counted / generator perturbation. Eq. 10 adds scaled Gaussian noise to one fixed point per seed (a Laplacian-row-weighted combination of its kNN, weights not convex); the paper says it replaces linear interpolation. "distribution" is the alternative generator code; Partial only if the Laplacian combination is read as interpolation. inside_folds nr: the only hint is "original training data" for NONE (Fig. 4 flowchart and Algorithm 1 are not in the text).
- R07370 (CBR/MCO): P = no. The text places samples between the seed and its sub-cluster centroid, but Alg. 2 line 13 prints x_p + s(x_p - mu), which extrapolates. The centroid partner is coded as N, not as a multi-instance combination under P. F = no because majority singleton outliers are removed before generation. inside_folds = stated, from a [Resampler, Standardizer, Classifier] pipeline evaluated by 5-fold CV with oversampling timed per fold.
- R06485 (hybrid SMOTE + bootstrap): passes ruling B (chain of SMOTE and bootstrap undersampling, presented as proposed, compared with SMOTE_OVA and Bootstrap alone). All six decision points are no; A is arguable (classes set to 40/50/60% of majority size, taken as a requested amount). vs_smote = plain although the competitor is named SMOTE_OVA (the OVA is the classifier decomposition). class = M. tuning = test (best of three sizes x four learners on one 70/30 split). before-split (whole-data counts).
- R10916 (AD-GSMOTE): Core, as a learned combination of tail node, nearest same-class node and adaptive class centre. Eq. 3 weights are unconstrained and the sign allows extrapolation. A = no (per-class total = gamma x mean class size). protocol = holdout: 5 training runs, re-splitting not stated, could be repeated-holdout. tuning = validation (grid search with a 20% validation split, the scoring set is not stated).

## batch020

coverage batch 020 (library full texts, round 2): DONE
n=4, fulltext_ok=4, eligible=4, Core=2, Partial=0, Not counted=2
Excluded: none. No record fails ruling B or B2: each proposes a generator of its own (avg-neighbor SMOTE, SDSMOTE, ICOTE, SMOTERandRep).

Check first:
- R00832 label Not counted/other: SMOTERandRep copies the seed and replaces log2(a) attribute values with values of random neighbors (box vertices, not the segment). A checker could argue Core with P=yes. The paper's other four "new" techniques (LRO, LRU, C-LROU, C-LRUO) only replicate or delete.
- R00655 label Not counted/other: ICOTE's synthetic points are aiNet memory antibodies evolved from random antibodies (clone, mutate eq.5, suppress eq.6), not interpolation between two instances. measures=ROC-AUC follows the paper's name; its eq.(9) is the one-point AUC (1+TPR-FPR)/2, i.e. balanced accuracy.
- R00042 N=yes: neighbors are found under a "weighted distance" that this two-page paper never defines; P=yes because the partner is the mean of the 5 nearest positives. No competitor of any kind (only oversampling rates 100-1000%).
- R00491 A=yes: seeds are drawn by support-degree probability and "the area near the sample should produce more samples"; step S6 does not say outright that counts differ per seed. inside_folds=before-split from "add the synthetic samples ... to participate in training and testing" (abstract, S7).
- R00832 inside_folds=before-split and n_datasets=1: the "nine data sets" are the one 13-class student dataset resampled whole, then stratified tenfold CV.

Texts: all four are the papers their titles name. None matches ROUND2_NOTE item 2 (no OCR text, no journal-issue excerpt pp. 74-85). R00491 (IEEE Xplore) and R00655 (Wiley) carry library download stamps dated 14 Nov 2026, not 16 Nov; R00042 (AAAI/FLAIRS) and R00832 (arXiv) carry no download stamp.

## batch021

coverage batch 021: n=4, eligible=4, Core=4, Partial=0, Not counted=0
Exclusions: none (no E1 under ruling B or B2). fulltext_ok = yes for all four: each text is the paper its title and DOI name.
Texts: ROUND2_NOTE says one text is an excerpt of a journal issue (pages 74 to 85). None of these four is. Their pages are 670-674, 25452-25459, 81370-81379 and 1813-1819. Formulas are garbled in R10647 and R03007.

Check first:
1. R11455 (TaA = Tomek links + ADASYN; four valve classes, class M). Eligible only under ruling B: it is a chain of existing parts, but the paper presents it as the authors' new algorithm and Table I compares it with SMOTE, ADASYN, Tomek links and TaS. S and A are both yes from ADASYN's difficulty-weighted allocation (A alone is defensible). F = no because the paper never says Tomek runs after ADASYN, and its wording reads as before. If a checker reads it as post-cleaning, F becomes yes. Modality is tabular, although the paper calls the data a multivariate time series. Table I reports the same CV scores that picked the SVM settings, and coded as tuning = validation. Only TaA vs no balancing was checked on a held-out test sample.
2. R03488 (FAWOS). It oversamples positive points of unprivileged sensitive groups (fairness imbalance), not a minority class as such. Kept eligible as a changed application of SMOTE. N = yes for the HEOM metric and same-class, same-group neighbours. tuning = test because alpha is reported at its best test AOD. The fairness measures ADI and AOD are coded as other.
3. R03007 (DP-SMOTE). Eq. (5) lost its operators. P = no rests on the stated "interpolation between cluster cores and other instances". "AUC" is defined as (1+TPR-FPR)/2, a single-point value equal to balanced accuracy, but it is coded ROC-AUC to follow the paper's label. inside_folds = nr: Algorithm 2 takes "the training set", but the experiment text suggests the data were resampled before CV.
4. R10647 (NR-Modified SMOTE). The KNN pre-filter is coded S (minority points barred as seeds), not F. N = yes for the Manhattan metric. inside_folds = before-split: the data were resampled, then 10-fold CV was run, and the confusion matrices count 500/500 and 225/225. In Table X the AUC column repeats the accuracy values for most rows.
