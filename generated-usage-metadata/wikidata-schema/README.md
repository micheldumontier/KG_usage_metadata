# Wikidata schema (2017/2018) — Table 3

The canonical Wikidata schema for both KG versions: types via `wdt:P31`/`wdt:P279`, predicates
as the full `wdt:P` namespace (the native definition, not the Bio2RDF-style restricted join).

Run: `python3 KG-Schema-extractors/wd_schema_extract.py <year>` (schema),
`python3 KG-Schema-extractors/wd_p279_edges.py` (subclass edges),
`python3 KG-Schema-extractors/wd_qid_labels.py` (labels)

Input: the Wikidata dump for the given year (`data/kg/wikidata-20170821-all-BETA.ttl.gz` etc.)

Output: `types_2017.txt`, `preds_2017.txt` (and `_2018` equivalents), `p279_edges_2017.tsv`
(subclass parent edges), `qid_labels_en.tsv` (period-matched English labels for Figure 8).
