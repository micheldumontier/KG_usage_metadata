# Bio2RDF Release 2/3 historical schemas (§sec:bio2013, "Schema-version robustness")

Supports the robustness check that re-aligns the 2013-era organic log to the Bio2RDF release
it actually queried, rather than the current (2024) endpoint schema — see
`generated-usage-metadata/bio2rdf-2013-organic/README.md` for the main 2013-organic analysis
this feeds into.

Produced by `KG-Schema-extractors/bio2rdf_release_schema.py`, which recovers each release's
schema from Bio2RDF's published per-dataset `*-statistics.nt.gz` files (no live endpoint exists
for these releases any more). Unlike the current 2024 endpoint extraction, these statistics
files enumerate all predicates and only instantiated types, not the class–predicate–class-join
restricted definition of Section 3.2 — so these historical denominators are on a broader basis
than the 2024 one and are not directly comparable to it or to each other (the manuscript makes
this explicit rather than presenting the version-matched percentages as equivalent to the
headline Table 4/5 figures).

- `r2_types.txt` (157 types), `r2_predicates.txt` (628 predicates) — Release 2 (2012–2013 data),
  queried by the pre-mid-2014 portion of the organic-2013 log.
- Sibling folder `bio2rdf-schema-release3/`: `r3_types.txt` (351 types), `r3_predicates.txt`
  (1,744 predicates) — Release 3 (deployed mid-2014, grew the corpus from 25 to 35 datasets,
  e.g. adding *chembl*, *sider*, *reactome*), queried by the post-mid-2014 portion.

(`wc -l` on these files undercounts by one: the last line has no trailing newline. Verified
2026-09-24 that the true counts — 157/628 and 351/1,744 — match the manuscript exactly.)

The organic log itself is split at the Release 2/3 boundary by
`KG-Usage-analysis/bio2rdf_split_organic_by_release.py` (mid-2014, hardcoded from Release 3's
known build dates), writing `organic_r2period.txt` / `organic_r3period.txt` — not committed
here (derived from the same non-redistributed raw access log as
`bio2rdf-2013-organic/organic_2013_queries.txt.gz`).
