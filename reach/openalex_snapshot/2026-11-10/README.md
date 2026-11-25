# OpenAlex snapshot, 10 November 2026 (15:52 to 15:53 UTC)

Every OpenAlex number in the v0.2 draft (Sections 1, 3, 6.9 and 8, Table 14,
Figure 5, Appendix G) comes from the raw JSON responses in this folder. The
request URL and UTC time of each response are in `urls.tsv` (the WP5 sample
keeps its URLs inside its own file). The ledger (`ledger.csv`) points each
number to `derived.json` or to the raw file.

The requests were made by `scripts/openalex_snapshot.py` with an OpenAlex API
key passed as the environment variable `OPENALEX_API_KEY`. The key is not in
any file here: the scripts strip it from the logged URLs. To repeat the
snapshot, a person gets a free key at
https://help.openalex.org/api/authentication/ and runs the commands below.

## Files

| File | Content |
|---|---|
| `smote_work.json` | Full work record of the SMOTE paper, W2148143831 (DOI 10.1613/jair.953): `cited_by_count` 34,938, `counts_by_year`, record `updated_date` 2026-11-10T11:39 |
| `citing_count.json` | `filter=cites:W2148143831`: `meta.count` 34,416 citing works |
| `citing_with_topic.json` | The same filter restricted to works with a primary topic: 34,366 |
| `group_publication_year.json` | Citing works by year of publication: groups sum to 34,408 (six dated before 2002; 34,402 from 2002 to 2026) |
| `group_primary_topic_domain_id.json` | By domain of the primary topic |
| `group_primary_topic_field_id.json` | By field of the primary topic (26 fields; groups sum to 34,367) |
| `group_sustainable_development_goals_id.json` | By Sustainable Development Goal (a work can carry more than one) |
| `group_authorships_countries.json` | By country of the authors' institutions (159 countries and territories; a work can count for more than one) |
| `group_type.json` | By document type |
| `corpus_works.json` | Records of the 75 corpus papers that have an OpenAlex id (ids from the Evaluation coding, two requests of up to 50 ids on the list endpoint); the list endpoint gives `cited_by_count` 34,720 for the SMOTE paper |
| `extra_works.json` | Saito and Rehmsmeier (2015), resolved from its DOI (6,338 citations), and the second OpenAlex record of the one-sided selection paper (OSS-1997, W2979832949, 329 citations) |
| `oss_candidates.json` | Title search that found that second OSS-1997 record |
| `wp5_tag_sample_raw.json` | WP5 step 1 sample: 100 citing works tagged with SDG 3 and 200 citing works without the tag filter (`sample` with `seed=20261110`; titles, primary topics, goals and abstract inverted indexes); `urls` holds the two request URLs |
| `derived.json` | Every number the paper prints, computed from the files above by `scripts/after_snapshot.py` (shares, top fields, top 25 countries, top ten most cited corpus studies) |
| `urls.tsv` | File, UTC time and request URL of each response (key removed) |
| `superseded_webfetch/` | Two tables transcribed by the fetch tool at about 12:55 UTC the same day, before an API key was available (34,297 citing works). They are kept for the record only; no number in the paper comes from them |

## Three counts of the same paper

At the same minute the API gives three counts for the SMOTE paper: 34,938 on
the work record, 34,720 for the same work on the list endpoint, and 34,416
works returned by the `cites` filter. The paper reports 34,416, because every
grouped count (year, field, goal, country, type) is computed on that set, and
mentions the other two in Section 8.1 and Appendix G.

## Commands

    OPENALEX_API_KEY=... python3 scripts/openalex_snapshot.py <team-repo> data/openalex/<date>
    python3 scripts/after_snapshot.py data/openalex/<date> <team-repo>
    python3 scripts/make_fig_reach.py data/openalex/<date> figures/fig_reach.pdf
    OPENALEX_API_KEY=... python3 scripts/wp5_tag_sample.py data/openalex/<date> wp5

Then rebuild the ledger (`python3 scripts/build_ledger.py . ledger.csv`) and
check the rows of Sections 1, 3, 6.9 and 8.
