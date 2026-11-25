# Notes of the recheck session (rulings B, B2 and C at full text, batch 101, 12 November 2026)

batch 101: 11 of 11 records done; own 9, existing-parts 2, unclear 0
no records remain

Look at these first:
1. R00308 (OAA-DB, Jeatrakul & Wong 2012): existing-parts + compared=no, so the script will now exclude it. Pivotal call: its only imbalance baseline, OAHO, is called a "balancing technique" by the paper, but in the text it is a class-ordering decomposition that does not resample. One could also argue OAA-DB is "a multiclass oversampling scheme of its own"; I read it as the authors' earlier SMOTE+CMTNN balancing applied unchanged per one-against-all subproblem plus a codeword rule. Medium confidence.
2. R09141 (IQRBU + genetic oversampling, 2024): coded own on thin changes: an inverse-quadratic kernel in RBU, and a GenSMOTE rate search with a different GA selection operator, both credited to earlier work. If a reviewer reads it as existing-parts, it is excluded, because results are only before vs after balancing. Medium confidence.
3. R00007 (SDC, Akbani et al. 2004): the abstract says "variant of SMOTE", but Sec. 5 uses standard SMOTE unchanged with Veropoulos's different-error-cost SVM, so existing-parts. It still stays included under B (presented, and compared with SMOTE and undersampling).
Lower priority: R15093 (own; compared only with its own ablation) and R00277 (own as an MSE-driven search for how much to oversample).
