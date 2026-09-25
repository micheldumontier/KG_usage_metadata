# Bio2RDF 2013-era organic queries

Recovers an organic/robotic split for the 2013 Bio2RDF log (the public LSQ release is
anonymized and can't be split by user agent), and computes its schema coverage against the
canonical 541-element schema. Supports Table 8 and the equal-effort comparison in §sec:rarefaction.

Run: `python3 KG-Usage-analysis/bio2rdf2013_log_compose.py` (extracts organic queries),
`python3 KG-Usage-analysis/bio2rdf2013_organic_coverage.py` (coverage)

Input: raw Bio2RDF server access log, May 2013–Sep 2015 (expected at
`~/data/bio2rdf.logs/bio2rdf.sparql.log.all/*.gz`; not committed here and its exact source isn't
otherwise documented in this repo), `generated-usage-metadata/bio2rdf-schema/`

Output: `organic_2013_queries.txt.gz` (decoded organic queries), `bio2rdf2013_organic_used.csv`
(used schema elements + occurrence counts).
