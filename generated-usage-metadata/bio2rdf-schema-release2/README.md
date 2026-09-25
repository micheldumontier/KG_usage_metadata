# Bio2RDF Release 2/3 historical schemas

Historical schemas for Bio2RDF Release 2 and Release 3, used to re-align the 2013-era organic
log to the release it actually queried (rather than the current 2024 endpoint schema) — the
"Schema-version robustness" check alongside `analysis-results/bio2rdf-2013-organic/`.

Run: `python3 KG-Schema-extractors/bio2rdf_release_schema.py`

Input: Bio2RDF's published per-dataset `*-statistics.nt.gz` files (no live endpoint exists for
these releases any more); the split organic log from
`KG-Usage-analysis/bio2rdf_split_organic_by_release.py`

Output: `r2_types.txt`, `r2_predicates.txt` (Release 2, here); `r3_types.txt`, `r3_predicates.txt`
(Release 3, sibling folder `bio2rdf-schema-release3/`).
