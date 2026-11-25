#!/usr/bin/env python3
"""Apply the Method decisions of 10 Nov 2026 (decision form items 24 and 25; decision sheet A1, A2) to the generated
rows of Table 6 until the Method Map itself is updated: the class categories of GLOS (Multiclass only) and
Loyalty-SMOTE (Binary only) are no longer provisional, so their asterisks go.
v0.64 (the team lead, 23 Nov 2026, "make them consistent"): KNNOR prints its scores and those of SMOTE only as means
over its datasets, like G-SMOTE, CISO and QC-SMOTE, so its cell is "avg." like theirs and carries no value (the
Method section's build/delta_vs_smote.py still writes "+.013 (mean)").
Usage (after gen_methods_rows.py): python3 scripts/apply_method_decisions.py gen/table_methods_rows.tex
"""
import sys
from pathlib import Path
p = Path(sys.argv[1]); s = p.read_text(encoding='utf-8')
DECIDED = {r'GLOS \citep{han2023glos} & 2023 & M* &': r'GLOS \citep{han2023glos} & 2023 & M &',
           r'Loyalty-SMOTE \citep{hu2026loyalty} & 2026 & B* &': r'Loyalty-SMOTE \citep{hu2026loyalty} & 2026 & B &',
           r'$\bullet$ & $\bullet$ & $\bullet$ &  & +.013 (mean) \\': r'$\bullet$ & $\bullet$ & $\bullet$ &  & avg. \\'}
for old, new in DECIDED.items():
    if old in s:
        s = s.replace(old, new)
    elif new not in s:
        sys.exit(f'STOP: row not found: {old}')
if '*' in s.replace('$^\\dagger$', ''):
    print('note: another asterisk remains in', p)
p.write_text(s, encoding='utf-8'); print('applied', len(DECIDED), 'decisions to', p)
