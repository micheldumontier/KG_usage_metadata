# `analysis-results/` — index

Downstream analyses that consume the usage metadata and schema data in
`generated-usage-metadata/` to produce a specific manuscript table or figure. Each subfolder has
its own README with the script(s) to run, inputs, and outputs.

- `rarefaction/` — Table 6, Figure 5
- `concentration/` — Tables 7, 12
- `bio2rdf-2013-organic/` — Table 8, 2013-era Bio2RDF (see also
  `generated-usage-metadata/bio2rdf-schema-release2/` for the version-matched robustness check)
- `wikidata-classvalue/` — Table 9 (class-position vs. value-position)
- `wikidata-mismatch/` — Figure 6, domain content–demand table
- `dbpedia-schema/` — Table 11 (DBpedia generality comparison)
- `wikidata-closure/` — P279-closure bound (Discussion limitations)
- `wikidata-utility/` — Tables 14–16 (utility ranking)

## Not regenerable on every machine

`adoption_dynamics.py`, `wd_temporal.py`, `wd_decontaminate.py`, and `template_linkage.py` (all
in `KG-Usage-analysis/`, no dedicated result folder here) need Wikidata log intervals or the
Bio2RDF 2019 log beyond what's kept locally by default — see `REPRODUCIBILITY.md` for the full
input-data list and sources.
