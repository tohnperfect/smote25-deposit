"""Rulings B and B2 of the team lead (11 Nov 2026; confirmed for the whole screen on 12 Nov 2026), as one function, so
that the screen (scripts/rule_b_decide.py) and the full-text stage of the coverage sample (scripts/analyze_samples.py)
apply them alike. Ruling C (task scope) excludes nothing. The facts are those of
data/search/screening_full_2026-11-11/rule_b/RULE_B_CODEBOOK.md."""
STOCK = {'deep-generative', 'statistical', 'augmentation'}


def decide(f):
    """(decision under B alone, decision under B and B2, ruling that excludes or '') for a dict of facts."""
    if f['scheme'] in ('own', 'unclear'):
        return 'include', 'include', ''
    kept_b = f['presented'] == 'yes' and f['compared'] == 'yes'
    dec_b = 'include' if kept_b else 'exclude'
    if f['generator'] in STOCK:
        return dec_b, 'exclude', 'B2'
    return dec_b, dec_b, '' if kept_b else 'B'
