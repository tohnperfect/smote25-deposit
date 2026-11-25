# Check of the search against the reference lists of recent reviews (v0.53, 21 November 2026)

Suggestion 6 of the comparison of 21 November 2026, at the team lead's request ("Edit the current version with
improvement suggestions 2, 3, 4, 5, 6, and 9."). Reported in Section 3.4, Appendix E and Table 3 of the paper as an AI
first pass. One AI session (Claude Fable 5.2) did all of it.

## What was done

1. `scripts/reflist_fetch.py` (network, run once on 21 November 2026 UTC): for the five reviews of Table 2 published
   in 2025 and 2026 (Udu et al. 2025, Idwan et al. 2025, Hayaeian Shirvan et al. 2025, Gao et al. 2026, Yousefimehr et
   al. 2026) the Crossref record with its reference list (`crossref/<doi>.json`), and for every reference that has a
   DOI the Crossref record of the cited work (`crossref_works/`: title, year and, where Crossref holds one, abstract).
   390 of the 392 DOIs answered.
2. `scripts/reflist_check.py` (no network; part of the build): matches every reference with the 22,426 records of the
   search, by DOI, else by title (letters and digits, the year within two), else by a close title (at least three
   quarters of the words shared, the year within two; one match, a title with a misprint). A matched reference takes
   the record's final decision of `screen_decisions.csv`. A reference that Crossref lists by its proceedings volume
   alone, without a DOI or a title, cannot be identified (2 of 695).
3. The session coded each of the 384 distinct references of 2002 or later that match no record, from the title and,
   for the few that have one, the Crossref abstract (`unmatched_coded.csv`):
   - `generator`: the paper proposes a way of creating new examples (or features, nodes or texts) for
     under-represented classes of a classification task; the task does not decide (ruling C);
   - `unclear`: the title leaves open whether the paper proposes such a method (a hybrid resampling, a framework, an
     application that names a generator);
   - `other`: reviews, general generative models and augmentation that are not aimed at under-represented classes,
     undersampling, cost-sensitive and loss-based methods, metric and contrastive learning, applications of existing
     resampling, regression, datasets and software.
   `dup_of` marks a work that two reviews cite without a DOI (10); it is counted once.
4. For every `generator` the script tests whether its title, with its abstract where there is one, holds a generation
   term and an imbalance term of the search string. None does.

## Files

| File | Content |
|---|---|
| `crossref/*.json` | The five reviews' Crossref records with their reference lists |
| `references.csv` | One row per review and reference: DOI, year, title, the matched record, its decision and code, whether the work is in the corpus |
| `unmatched_window.csv` | The references of 2002 or later that match no record |
| `unmatched_coded.csv` | The session's code for each of them (`code`) and, for the 61 works it coded `generator` or `unclear`, the authors' code of 21 November 2026 (`author_code`: generator, not a generator, cannot tell) |
| `reflist_numbers.json` | Every number the paper prints from this check |
| `crossref_works/` | Crossref's records of the cited works, with abstracts where it holds them; kept for the coding, not deposited |

## Limits

The session's codes rest on titles: Crossref holds an abstract for 5 of the 45 papers it coded `generator`. On 21
November 2026 the authors coded the 45 and the 16 `unclear` works: 40 generators (36 of the 45, 4 of the 16), 2 not, 19
left undecided. The paper counts with these codes (135 of 175; 135 of 194 with the undecided). The 313 works coded
`other` were coded by one session only. A reference matched with a record by title could be another paper of the
same title; the 52 title matches were not read one by one. The reviews' own reference lists are taken as Crossref
holds them.
