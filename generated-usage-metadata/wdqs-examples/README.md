# WDQS example-query set (for example-query decontamination, R2-2iii)

Source: Wikidata:SPARQL_query_service/queries/examples, revision **509986548**
(permalink: <https://www.wikidata.org/w/index.php?title=Wikidata:SPARQL_query_service/queries/examples&oldid=509986548>)
(timestamp **2017-06-30T00:32:28Z**), the latest revision before the organic log period.

- `examples_2017_queries.ndjson` — 348 unique example query templates extracted from the
  page wikitext (one JSON-encoded query per line).
- `examples_2017_fp.ndjson` — per-query fingerprint `{v,fp,nt}` from
  `sparqljs-worker/fingerprint_worker.js` (variable-/literal-invariant canonical form,
  label-service plumbing excluded); 329 parse, 313 distinct content fingerprints.

Reproduce: `KG-Usage-analysis/wd_decontaminate.py` matches the organic log against `fp`.
