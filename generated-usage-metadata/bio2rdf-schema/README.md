# Bio2RDF schema (26 subgraphs, current endpoint) — Table 3

The canonical Bio2RDF schema (types + predicates) as currently served by the live 2024 endpoint,
across all 26 subgraphs. `*_vocabulary:Resource` excluded.

Run: `python3 KG-Schema-extractors/schema_gnrator_Bio2RDF.py` (raw extraction, needs a live
Bio2RDF SPARQL endpoint), then `python3 KG-Schema-extractors/build_bio2rdf_canonical_schema.py`
(assembly)

Input: `all_classes.csv`, `schema.csv` (raw output of `schema_gnrator_Bio2RDF.py`, not committed)

Output: `types_26subgraphs.txt` (350 types), `predicates_26subgraphs.txt` (191 predicates),
`schema_elements_26subgraphs.csv` (combined, 541 total).
