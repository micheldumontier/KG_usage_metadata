# Reproducing the analyses

This file answers two questions raised in review: **where does each input dataset come
from**, and **which script produced each figure**. It complements `README.md`, which
describes the method, and `generated-usage-metadata/README.md`, which indexes every
committed output file (canonical vs. superseded/legacy) in more detail than the tables below.

## 1. Input data

The datasets are too large to version (about 60 GB in total), so `data/` is git-ignored.
`data/download_all.sh` fetches the largest of them; the table below is the complete list,
including the inputs that script does not yet cover.

| Path under `data/` | Size | Source |
|---|---|---|
| `kg/wikidata-20170821.ttl.gz` | 21 GB | Internet Archive, <https://archive.org/download/wikibase-wikidatawiki-20170821/wikidata-20170821-all-BETA.ttl.gz> |
| `kg/wikidata-20180205.ttl.gz` | 28 GB | Internet Archive, <https://archive.org/download/wikibase-wikidatawiki-20180205/wikidata-20180205-all-BETA.ttl.gz> |
| `logs/bio2rdf_2019-2021.csv` | 1.6 GB | <https://download.dumontierlab.com/Bio2RDF/logs/bio2rdf_sparql_logs_processed_01-2019_to_07-2021.csv> |
| `logs/wikidata/*_organic.tsv.gz`, `*_all.tsv.gz` | 4.5 GB | Wikimedia one-off SPARQL query logs, <https://analytics.wikimedia.org/datasets/one-off/wikidata/sparql_query_logs/> — one directory per 28-day interval; we use intervals 1 and 7 plus the five intermediate windows |
| `logs/lsq2013/`, `logs/lsq2013_exec/` | 2.7 GB | Extracted from the LSQ 2.0 SPARQL endpoint, <https://lsq.data.dice-research.org/sparql>, with the query in Listing 1 of the paper (one file per Bio2RDF subgraph). `lsq2013_exec/` is the subset with a recorded remote execution. |
| `logs/dbpedia/dbpedia_texts.txt` | 1.7 GB | Distinct executed DBpedia query texts, extracted from the same LSQ 2.0 endpoint via `KG-Schema-extractors/dbpedia_lsq_extract.py` (dataset name `dbpedia`, confirmed against the live endpoint; paginated, since this Virtuoso instance caps `ORDER BY`+`LIMIT`/`OFFSET` at 10,000 rows combined) |
| `wdqs_examples/` | small | WDQS example set, revision 509986548 — <https://www.wikidata.org/w/index.php?title=Wikidata:SPARQL_query_service/queries/examples&oldid=509986548>. See `generated-usage-metadata/wdqs-examples/README.md`. |
| Bio2RDF 2024 schema | — | Queried live from <https://bio2rdf.org/sparql>. Because a live endpoint drifts, the extracted schema is frozen in `generated-usage-metadata/bio2rdf-schema/` and *that*, not the endpoint, is the reproducible reference. |
| Bio2RDF Release 2 / 3 schemas | small | Recovered from Bio2RDF's published per-dataset statistics files; frozen in `generated-usage-metadata/bio2rdf-schema-release{2,3}/`. |
| `wd_closure_anchor_queries.tsv`, `wd_closure_bound_summary.txt` | small | Outputs of `KG-Usage-analysis/wd_closure_queries.py` (review round 4, comment #14), regenerated locally from the 2017 Wikidata dump and the interval-1 2017 organic log; verified against the published closure numbers. See `analysis-results/wikidata-closure/README.md`. |

## 2. Which script produced which figure

Figure numbers are those of the current `main.pdf`.

| Figure | Image file | Produced by |
|---|---|---|
| 1 | `image14.png` | hand-drawn (workflow diagram) |
| 2 | `image17.png` | hand-drawn (variable standardization) |
| 3, 4 | `image9.png`, `image8.png` | hand-drawn Venn diagrams |
| 5 | `rarefaction.png` | `KG-Usage-analysis/rarefaction_size_control.py` |
| 6 | `wd_mismatch.png` | `KG-Usage-analysis/wd_mismatch.py` |
| 7 | `image10.png` | `KG-Usage-analysis/regenerate_figures.py` |
| 8 | `image7.png` | `KG-Usage-analysis/regenerate_figures.py` |
| 9 | `image16.png` | hand-drawn (usage-metadata model) |
| 10 | `utility_autocomplete.png` | `KG-Usage-analysis/wd_utility.py` |
| 11 | `image21.png` | external, <https://marmhm.github.io/Schema-usage-graph/> |

The old Figure 6 (`image24.png`, the Bio2RDF 2013-vs-2019 pairwise-subgraph heatmap
from `KG-Usage-analysis/Bio2RDF-federated-querying/`) was removed along with the
"Pairwise Schema Type Usage of Bio2RDF" subsection (comment #7, review round 4):
the method couldn't distinguish genuine 2013 `SERVICE`-based cross-dataset joins
from the 2019 unified-endpoint architecture, so the reported "3 vs 22" comparison
conflated a real usage question with an architectural artifact. `image21.png` also
moved position (comment #6): it now illustrates a usage-aware exploration
interface in the Utility subsection rather than sitting in the Bio2RDF results,
which is why it is Figure 11, not Figure 6, despite being one of the
earlier-produced images. The `Bio2RDF-federated-querying/` notebooks and their
`generated-usage-metadata/Bio2RDF-federated-querying-datasets/` outputs are no
longer cited by the manuscript. Decision (2026-09-24, comment #5's repo-reorg pass):
**keep** rather than remove — one of the notebooks turned out to be the only
surviving source of the 17-subgraph schema allowlist (see
`KG-Schema-extractors/build_bio2rdf_canonical_schema.py`'s docstring). See
`KG-Usage-analysis/Bio2RDF-federated-querying/README.md`.

**Figures 5, 7 and 8 read the per-element count files in `generated-usage-metadata/`.**
Any change to the schema definition or to those counts requires re-running the
corresponding script; both have silently gone stale after a numeric correction before.

**Figure 5 needs a manual copy step.** `rarefaction_size_control.py` writes its figure next to
itself, as `KG-Usage-analysis/rarefaction_organic_vs_robotic.png`, which must be manually copied
to `manuscript/texsupport.iospress-sw-master/rarefaction.png` — confirmed byte-identical as of
2026-09-24, so this had already been done correctly, just undocumented. See
`analysis-results/rarefaction/README.md`.

## 3. Which script produced which table

| Table | Produced by |
|---|---|
| 2, 3 (schema totals) | `KG-Schema-extractors/schema_gnrator_Bio2RDF.py`, `wd_schema_extract.py` |
| 4, 5 (used elements, coverage) | `Schema-coverage-method/sparql_log_preprocess.py`; Bio2RDF cross-check in `KG-Usage-analysis/bio2rdf_recompute_conformant.py` |
| 6 (rarefaction) | `KG-Usage-analysis/rarefaction_size_control.py` |
| 7 (singletons), 12 (concentration) | `KG-Usage-analysis/concentration_metrics.py`, `bio2rdf_recompute_conformant.py` |
| 8 (2013 log composition) | `KG-Usage-analysis/bio2rdf2013_log_compose.py` |
| 9 (class vs value) | `KG-Usage-analysis/wd_classvalue.py` |
| 10 (domains) | `KG-Usage-analysis/wd_domains.py` |
| 11 (generality / DBpedia) | `KG-Usage-analysis/dbpedia_analysis.py` |
| 13 (temporal windows) | `KG-Usage-analysis/wd_temporal.py` |
| 14, 15 (utility, ranking) | `KG-Usage-analysis/wd_utility.py`, `wd_utility_ranking.py` |
| 16 (predicate ranking) | `KG-Usage-analysis/wd_utility_predicates.py` |

The utility subsection's bootstrap-CI robustness check (2,000 query-level resamples confirming
the usage-minus-supply coverage difference stays positive at every evaluated *k*; not its own
numbered table) is produced by `KG-Usage-analysis/wd_utility_ci.py`.

## 4. Environment

- **Python**: the analysis scripts need `pandas`, `numpy` and `matplotlib`. On macOS with
  both a Homebrew and a CommandLineTools interpreter installed, `python3` may resolve to
  the one *without* them; invoke `/usr/bin/python3` explicitly if imports fail.
- **Node**: the SPARQL parsing workers under `~/.local/sparqljs-worker/` need Node and
  `sparqljs`. `Schema-coverage-method/sparqljs-worker/` holds the worker sources.
- **LaTeX**: TinyTeX suffices. `main.tex` uses `comment.sty`, which a default TinyTeX
  install lacks: `tlmgr install comment`.
- **numpy version affects Monte-Carlo reproducibility despite a fixed seed.**
  `rarefaction_ci.py`'s bootstrap uses `numpy.random.Generator.choice(...,
  replace=False)`, whose internal sampling algorithm has changed across numpy
  releases; the same script, data, and seed (`20260612`) can therefore give
  slightly different CIs on different numpy versions (verified: numpy 2.2.1
  reproduces Bio2RDF's ratio and conclusion exactly but not its exact CI bounds
  — 95% CI [0.73, 1.03] here vs. the published [0.75, 1.02] — while Wikidata's
  much larger sample size happens to reproduce exactly). Neither CI is wrong;
  a fixed seed alone does not guarantee bit-identical Monte-Carlo output across
  environments for this method.

## 5. Note on the parallel workers

`parallel()` in the `KG-Usage-analysis` scripts partitions work with a stride
(`prepped[i::nw]`). Results **must** be reassembled by original index, which they now are.
Concatenating the per-worker outputs instead silently misaligns `zip(queries, results)`,
which corrupts every count-weighted result while leaving set-based results untouched — a
failure mode that produced several wrong published numbers before it was found. If you add
a worker-based script, copy the reassembly loop rather than the concatenation.
