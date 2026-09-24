# `generated-usage-metadata/` — index

This directory holds every schema-extraction and usage-metadata output the manuscript's
Results section (§4) reads from. It grew by accretion across several review rounds and mixes
canonical, actively-read, and superseded material at the top level. This file is the map;
most subfolders also have their own README with analysis-specific detail
(`wd-classvalue/`, `wd-closure/`, `wd-utility/`, `wdqs-examples/`).

## The central "used schema elements" files (root-level `*_combined_schema_elements.csv` + `.ttl`)

These `KG log_KGversion_combined_schema_elements.csv` files (one row per referenced schema
element, columns `Schema Element,TotalCount`) are the single most load-bearing dataset in the
repo: they are read directly by `bio2rdf_recompute_conformant.py`, `concentration_metrics.py`,
`rarefaction_size_control.py`, `rarefaction_ci.py`, `regenerate_figures.py`, and
`adoption_dynamics.py` (all in `KG-Usage-analysis/`), which together produce Tables 4, 5, 6, 7,
8, 12 and Figures 5, 7, 8, 9. The matching `.ttl` files are an RDF serialization of the same
counts, produced from the CSVs by `csv-2-rdf.ipynb` — this is the paper's own "usage metadata"
deliverable (§4.10), not merely an intermediate.

**Known provenance caveat (already investigated, not an open question):** these committed CSVs
predate the current `Schema-coverage-method/sparql_log_preprocess.py` pipeline — they came from
an earlier notebook chain (`Schema_coverage_calculation_BIO2RDF.ipynb` /
`Schema_coverage_calculation_Wikidata.ipynb` / `usage_pattern_analysis.ipynb`), and nobody has
regenerated them end-to-end with the current script. This was raised in review round 2 and
answered there (`manuscript/RESPONSE_TO_REVIEW2.md`, section **V2**): the sparsest, most-exposed
log (Bio2RDF organic 2019) was re-derived from the corrected valid-query set directly and found
to change results negligibly (Spearman ρ = 0.954 between old and recomputed frequency vectors,
identical top-10, largest single-element count change 21; Wikidata and Bio2RDF-2013 were
unaffected by the correction in the first place). The manuscript states this basis and the
robustness check in a paragraph at the head of the usage-patterns results. Treat the files as
authoritative-by-verification, not as freshly reproducible from `sparql_log_preprocess.py` alone.

## Canonical per-KG schema totals (Table 3)

- `bio2rdf-schema/` — Bio2RDF, current (2024) endpoint, 26 subgraphs. Produced by
  `KG-Schema-extractors/schema_gnrator_Bio2RDF.py` (raw extraction) +
  `KG-Schema-extractors/build_bio2rdf_canonical_schema.py` (assembly into the canonical
  `types_26subgraphs.txt` / `predicates_26subgraphs.txt` / `schema_elements_26subgraphs.csv`
  triple). 350 types + 191 predicates = 541 total, `*_vocabulary:Resource` excluded.
- `bio2rdf-schema-release{2,3}/` — Bio2RDF Release 2/3 schemas, recovered from Bio2RDF's
  published per-dataset statistics files via `KG-Schema-extractors/bio2rdf_release_schema.py`.
- `wikidata-schema/` — Wikidata 2017/2018, native definition (types via `wdt:P31`/`wdt:P279`,
  predicates as the full `wdt:P` namespace). Produced by `KG-Schema-extractors/wd_schema_extract.py`.
  Also holds `p279_edges_2017.tsv` (read by `wd_class_validation.py`) and `qid_labels_en.tsv`
  (period-matched 2017 labels for Figure 8, produced by `KG-Schema-extractors/wd_qid_labels.py`).
- `schema-Bio2RDF-17Subgraphs.csv` (loose, root-level) — the 17-of-26 Bio2RDF subgraphs that
  have matching 2013 query-log data (270 types + 125 predicates = 395 total), used as the TSE
  denominator for 2013-log coverage. Derivation now documented in
  `build_bio2rdf_canonical_schema.py`'s docstring: a 17-dataset-name allowlist recovered from
  the orphaned `Bio2RDF-federated-querying/2013KG-get_datasets_relationships_bio2rdf.ipynb`
  notebook, filtered against the canonical 26-subgraph schema, with one understood exception
  (`ctd_vocabulary:Gene-Disease-Association`, present in the live 2024 ctd subgraph but not the
  2013-scoped file — most likely added to ctd after 2013).

## Superseded / legacy — kept for reference, not read by any current script

- **`schema-Bio2RDF-26Subgraphs.csv`** (loose, root-level, 98,756 raw rows) — this is *not* a
  duplicate of `bio2rdf-schema/schema_elements_26subgraphs.csv`. It's the raw, non-deduplicated
  `(Class1, Predicate, Class2)` pattern file (includes `*_vocabulary:Resource` entries), one
  step upstream of the canonical, deduplicated, Resource-excluded schema. It is referenced only
  as a stale example in `sparql_log_preprocess.py`'s usage docstring, which the script's own
  `load_schema()` code already flags in a comment as an approximation, not the canonical TSE.
  Do not use this file as `--schema`; use `bio2rdf-schema/schema_elements_26subgraphs.csv`.
- **`schema-wiki2017.csv`, `schema-wiki2018.csv`** — output of the superseded
  `schema_generator_wikidata.py` (the original Bio2RDF-style restricted class–predicate–class
  join). Referenced by zero current scripts; Wikidata now uses the native definition
  (`wikidata-schema/`, above). See `CLAUDE.md`'s "Wikidata schema definition" note.
- **`Bio2RDF-federated-querying-datasets/`** and the matching
  `KG-Usage-analysis/Bio2RDF-federated-querying/` notebooks — orphaned by comment #7's removal
  of the "Pairwise Schema Type Usage of Bio2RDF" subsection. **Decision: keep** (see
  `KG-Usage-analysis/Bio2RDF-federated-querying/README.md`) — one of the notebooks is the only
  surviving source of the 17-subgraph allowlist above.
- `csv-2-rdf.ipynb` — not itself superseded (see above), but has no equivalent script form; it's
  a notebook step in an otherwise-scripted pipeline.

## Other subfolders

- `rarefaction/` — size-controlled coverage comparison (Table 6, Figure 5). Covers both Bio2RDF
  and Wikidata; see its own README for the two scripts involved (one of them,
  `rarefaction_ci.py`, was renamed from `wd_rarefaction_ci.py` since it was never
  Wikidata-only despite the old prefix).
- `wikidata-supply/` — KG-content baselines (instances/class, triples/predicate) for the
  demand-vs-supply and utility-ranking analyses; see its own README.
- `wd-mismatch/` — Figure 6 and Table `tab:domains` (content-supply vs. query-demand). Organic
  side regenerated and verified this session; robotic side needs a log file not present
  locally — see its own README for the exact gap.
- `dbpedia-schema/` — DBpedia's schema + class-position analysis (Table 11); see its own
  README (not re-verified locally, query-text log unavailable here, but already verified on
  the server per comment #8).
- `bio2rdf-2013-organic/` — supports Table 8 (2013 log composition), from
  `KG-Usage-analysis/bio2rdf2013_log_compose.py`.
- `wd-classvalue/`, `wd-closure/`, `wd-utility/`, `wdqs-examples/` — each has its own README.

## Verified reproducible

- `rarefaction/` (Table 6, Figure 5) — both scripts re-run and confirmed to reproduce the
  published numbers exactly (mod a known numpy-version CI-bound effect, already documented).
  Documentation only, no code changes needed.
- `concentration/` (Tables 7, 12; Figures 7, 8) — re-run and confirmed exact reproduction after
  fixing a real stale-TSE-denominator bug in `concentration_metrics.py` (see its README).
  Figures 7/8 (`regenerate_figures.py`) reproduce byte-identical with no changes.

## Blocked locally — need additional raw log data (documented, not a correctness concern)

These four §4.9 analyses could not be regenerated or verified on this machine (only
`data/logs/wikidata/int1_2017_organic.tsv.gz` and the 2017 Wikidata dump are present locally;
no Bio2RDF log and no other Wikidata log interval). None of this is a data-quality problem —
their published numbers were produced on Maryam's server, where the full log collection lives —
this is purely a "what would it take to rerun this here" note.

- `KG-Usage-analysis/adoption_dynamics.py` (§sec:adoption, "Adoption of Newly Introduced
  Predicates") — needs `out/wd_{organic,robotic}2018_used.csv` (from `wd_coverage.py` against
  the 2018 Wikidata logs, not present) plus the already-committed `wikidata-schema/` and
  `bio2rdf-schema-release{2,3}/` files.
- `KG-Usage-analysis/wd_temporal.py` (§sec:equalintervals, Table 13) — needs all 7 equal-length
  (28-day) interval organic logs; only interval 1 is present locally.
- `KG-Usage-analysis/wd_decontaminate.py` (the "Example-query contamination" paragraph in
  §4.9, working with `wdqs-examples/`) — needs the same 7 organic interval logs as
  `wd_temporal.py`; only interval 1 present.
- `KG-Usage-analysis/template_linkage.py` (§sec:templates, "Which Queries Reach Rare Classes")
  — needs `out/bio2rdf2019_organic_unique_VALID.csv` (from the 1.6 GB Bio2RDF 2019 log, not
  present) and all organic Wikidata log intervals (same gap as above).

## Corrected assessment: `usage_pattern_analysis.ipynb` is not superseded

An earlier pass through this README speculated this notebook was likely superseded by
`wd_temporal.py`/`adoption_dynamics.py`/`regenerate_figures.py` and flagged it as needing a
keep/remove decision. On closer inspection (2026-09-24) that was wrong: this notebook computes
Spearman rank correlation and Wilcoxon signed-rank statistics between the 2013/2019 (Bio2RDF)
and 2017/2018 (Wikidata) frequency vectors — the exact ρ = 0.158/0.484/0.571 and Wilcoxon
statistics cited in §sec:concentration's "Changes in Used Schema Element Ranking" prose. None of
the current `.py` scripts compute this (they cover coverage, concentration, and temporal-window
trajectories, but not this specific pairwise rank-correlation comparison). This notebook is
therefore very likely still the authoritative source for those specific numbers — **not**
superseded, and should be kept as an active part of the pipeline, not archived. Not
independently re-verified number-by-number this session (would need re-running it, which its
`/opt/conda/...` paths suggest was last run in a different environment than this repo's). This
is also a real gap in `REPRODUCIBILITY.md`'s table/figure mapping, worth adding once confirmed.
- `manuscript/VALIDATION_SUMMARY.md` — a validation snapshot from an earlier review round,
  now stale (cites pre-Resource-exclusion Bio2RDF totals — 545/195 rather than the current
  541/191 — and the federated-querying comparison removed by comment #7). Flagged with a header
  note rather than deleted; superseded by the per-comment `RESPONSE_TO_REVIEWn.md` files and this
  session's `REPRODUCIBILITY.md`.
