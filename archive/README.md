# Archive

Superseded scripts and data files, not used by any current analysis. Kept for historical
reference rather than deleted.

- `schema_generator_wikidata.py` — original Bio2RDF-style restricted Wikidata schema extractor.
  Superseded by `KG-Schema-extractors/wd_schema_extract.py` (native `wdt:P`-namespace definition).
- `schema_gnrator_Bio2RDF_simpler_queries.py` — exploratory scratch script for spot-checking
  specific class/predicate relationships.
- `schema-wiki2017.csv`, `schema-wiki2018.csv` — output of the superseded Wikidata extractor
  above.
- `schema-Bio2RDF-26Subgraphs.RAW.csv` — raw, non-deduplicated Bio2RDF class/predicate pattern
  dump (includes `*_vocabulary:Resource` entries). Superseded by the canonical, deduplicated
  `generated-usage-metadata/bio2rdf-schema/schema_elements_26subgraphs.csv`.
- `Schema_coverage_calculation_BIO2RDF.ipynb`, `Schema_coverage_calculation_Wikidata.ipynb` —
  the original notebook-based coverage pipeline. Superseded by
  `Schema-coverage-method/sparql_log_preprocess.py` (Bio2RDF) and
  `KG-Usage-analysis/wd_coverage.py` (Wikidata) for any *new* run. Not needed to reproduce the
  currently-published numbers: Bio2RDF's committed usage-metadata files were confirmed current
  by a forced full recomputation (review round 3), and Wikidata's were independently
  cross-checked from scratch (see `VALIDATION_SUMMARY.md` below) — neither depends on rerunning
  these notebooks.
- `VALIDATION_SUMMARY.md` — a reproducibility audit from an earlier review round. Its Bio2RDF
  numbers predate later corrections (Resource-exclusion, predicate-definition changes) and no
  longer match the current manuscript; for those, see `REPRODUCIBILITY.md` and the per-round
  `manuscript/RESPONSE_TO_REVIEWn.md` files instead. Its Wikidata "mine vs. paper" cross-check
  (Tables 4–5) is still the standing evidence that the committed Wikidata usage-metadata files
  are independently reproducible — that specific finding was never superseded.
