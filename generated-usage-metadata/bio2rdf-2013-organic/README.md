# Bio2RDF 2013-era organic queries (browser user-agent)

Derived from the raw Bio2RDF server access log (`~/data/bio2rdf.logs`, May 2013–Sep 2015,
127.2M executed SPARQL requests; the upstream source of LSQ, not redistributed here).

- `organic_2013_queries.txt.gz` — 115,420 executed browser-UA SPARQL queries (decoded),
  extracted by `KG-Usage-analysis/bio2rdf2013_log_compose.py` (status 200, browser UA;
  Virtuoso-internal + LSQ-harvest infrastructure traffic excluded).
- `bio2rdf2013_organic_used.csv` — used schema elements + occurrence counts, from
  `KG-Usage-analysis/bio2rdf2013_organic_coverage.py`. Coverage 292/545 = 53.6%.
