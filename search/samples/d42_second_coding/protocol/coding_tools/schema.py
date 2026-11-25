"""Field rules for the coverage sample and the use audit (WP4, WP5), 11 November 2026."""
ROOT = {'coverage': '/home/claude/work/d42/coverage', 'useaudit': '/home/claude/work/d42/useaudit'}

YN = {'yes', 'no'}
NA = {'na'}
COV_MEASURES = {'accuracy', 'recall', 'precision', 'specificity', 'F-measure', 'G-mean', 'ROC-AUC', 'PR-AUC', 'MCC',
                'balanced-accuracy', 'kappa', 'Brier', 'log-loss', 'calibration', 'other'}
USE_MEASURES = COV_MEASURES | {'net-benefit'}

COVERAGE = {
    'rec': None,
    'fulltext_ok': YN,
    'eligible': YN | NA,
    'exclusion': {'none', 'E1', 'E2', 'NOT-GEN', 'NO-EVAL', 'STUDY', 'OTHER'} | NA,
    'label': {'Core', 'Partial', 'Not counted'} | NA,
    'generator': {'interpolation', 'deep-generative', 'distribution', 'perturbation', 'other'} | NA,
    'S': YN | NA, 'A': YN | NA, 'N': YN | NA, 'P': YN | NA, 'F': YN | NA, 'L': YN | NA,
    'class': {'B', 'M', 'B+M'} | NA,
    'modality': {'tabular', 'image', 'text', 'time-series', 'graph', 'mixed', 'other'} | NA,
    'n_datasets': 'int_nr_na',
    'vs_smote': {'plain', 'wrapper', 'no'} | NA,
    'vs_none': YN | NA,
    'vs_cost': YN | NA,
    'measures': ('list', COV_MEASURES),
    'protocol': {'cv', 'repeated-cv', 'holdout', 'repeated-holdout', 'other', 'nr'} | NA,
    'inside_folds': {'stated', 'before-split', 'nr'} | NA,
    'tuning': {'default', 'validation', 'test', 'nr'} | NA,
    'stat_test': YN | NA,
    'code': YN | NA,
    'evidence': 'text40',
    'note': 'text40',
    'confidence': {'high', 'medium', 'low'},
}

USEAUDIT = {
    'rec': None,
    'source': {'fulltext', 'abstract'},
    'is_application': YN,
    'domain': {'medicine', 'bio', 'finance', 'security', 'industry', 'energy', 'software', 'transport', 'environment',
               'education', 'business', 'social', 'other'} | NA,
    'task': 'text15',
    'stakes': {'individual', 'other'} | NA,
    'modality': {'tabular', 'image', 'text', 'time-series', 'mixed', 'other'} | NA,
    'resampler': ('list', {'SMOTE', 'Borderline-SMOTE', 'ADASYN', 'SVM-SMOTE', 'SMOTE-ENN', 'SMOTE-Tomek', 'SMOTE-NC',
                           'KMeans-SMOTE', 'other-SMOTE-variant', 'random-oversampling', 'undersampling',
                           'deep-generative', 'other'}),
    'learner': ('list', {'logistic', 'tree', 'forest', 'boosting', 'svm', 'knn', 'naive-bayes', 'neural-net',
                         'deep-net', 'other'}),
    'inside_folds': {'stated', 'before-split', 'nr'} | NA,
    'vs_none': YN | NA,
    'vs_weights': YN | NA,
    'measures': ('list', USE_MEASURES),
    'calibration': YN | NA,
    'validation': {'internal', 'external', 'prospective', 'deployed', 'nr'} | NA,
    'test_balanced': {'yes', 'no', 'nr'} | NA,
    'evidence': 'text30',
    'note': 'text40',
    'confidence': {'high', 'medium', 'low'},
}

SCHEMA = {'coverage': COVERAGE, 'useaudit': USEAUDIT}
