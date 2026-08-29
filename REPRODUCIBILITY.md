# Reproducing the analyses

This file answers two questions raised in review: **where does each input dataset come
from**, and **which script produced each figure**. It complements `README.md`, which
describes the method.

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
| `logs/dbpedia/dbpedia_texts.txt` | 1.7 GB | Distinct executed DBpedia query texts, extracted from the same LSQ 2.0 endpoint |
| `wdqs_examples/` | small | WDQS example set, revision 509986548 — <https://www.wikidata.org/w/index.php?title=Wikidata:SPARQL_query_service/queries/examples&oldid=509986548>. See `generated-usage-metadata/wdqs-examples/README.md`. |
| Bio2RDF 2024 schema | — | Queried live from <https://bio2rdf.org/sparql>. Because a live endpoint drifts, the extracted schema is frozen in `generated-usage-metadata/bio2rdf-schema/` and *that*, not the endpoint, is the reproducible reference. |
| Bio2RDF Release 2 / 3 schemas | small | Recovered from Bio2RDF's published per-dataset statistics files; frozen in `generated-usage-metadata/bio2rdf-schema-release{2,3}/`. |

## 2. Which script produced which figure

Figure numbers are those of the current `main.pdf`.

| Figure | Image file | Produced by |
|---|---|---|
| 1 | `image14.png` | hand-drawn (workflow diagram) |
| 2 | `image17.png` | hand-drawn (variable standardization) |
| 3, 4 | `image9.png`, `image8.png` | hand-drawn Venn diagrams |
| 5 | `rarefaction.png` | `KG-Usage-analysis/rarefaction_size_control.py` |
| 6 | `image21.png` | external, <https://marmhm.github.io/Schema-usage-graph/> |
| 7 | `image24.png` | `KG-Usage-analysis/Bio2RDF-federated-querying/` |
| 8 | `wd_mismatch.png` | `KG-Usage-analysis/wd_mismatch.py` |
| 9 | `image10.png` | `KG-Usage-analysis/regenerate_figures.py` |
| 10 | `image7.png` | `KG-Usage-analysis/regenerate_figures.py` |
| 11 | `image16.png` | hand-drawn (usage-metadata model) |
| 12 | `utility_autocomplete.png` | `KG-Usage-analysis/wd_utility.py` |

**Figures 5, 9 and 10 read the per-element count files in `generated-usage-metadata/`.**
Any change to the schema definition or to those counts requires re-running the
corresponding script; both have silently gone stale after a numeric correction before.

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

## 4. Environment

- **Python**: the analysis scripts need `pandas`, `numpy` and `matplotlib`. On macOS with
  both a Homebrew and a CommandLineTools interpreter installed, `python3` may resolve to
  the one *without* them; invoke `/usr/bin/python3` explicitly if imports fail.
- **Node**: the SPARQL parsing workers under `~/.local/sparqljs-worker/` need Node and
  `sparqljs`. `Schema-coverage-method/sparqljs-worker/` holds the worker sources.
- **LaTeX**: TinyTeX suffices. `main.tex` uses `comment.sty`, which a default TinyTeX
  install lacks: `tlmgr install comment`.

## 5. Note on the parallel workers

`parallel()` in the `KG-Usage-analysis` scripts partitions work with a stride
(`prepped[i::nw]`). Results **must** be reassembled by original index, which they now are.
Concatenating the per-worker outputs instead silently misaligns `zip(queries, results)`,
which corrupts every count-weighted result while leaving set-based results untouched — a
failure mode that produced several wrong published numbers before it was found. If you add
a worker-based script, copy the reassembly loop rather than the concatenation.
