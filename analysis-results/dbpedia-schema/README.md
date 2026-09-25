# DBpedia schema + class-position analysis (Table 11)

DBpedia serves as a third KG (OWL-style schema like Bio2RDF, but broad like Wikidata), used to
test whether Wikidata's value-position inflation (§sec:classvalue) is item-based-KG-specific or
more general.

Run: `python3 KG-Schema-extractors/dbpedia_lsq_extract.py` (schema extraction),
`python3 KG-Usage-analysis/dbpedia_analysis.py` (coverage + class-position analysis)

Input: LSQ 2.0 endpoint (`lsq.data.dice-research.org`) for schema extraction;
`data/logs/dbpedia/dbpedia_texts.txt` (distinct executed DBpedia query texts) for the analysis.

Output: `classes.txt`, `predicates.txt`, `instances_per_class.csv` (DBpedia `dbo:` schema and
instance counts). `dbpedia_analysis.py` prints coverage/class-position results to console, no
committed intermediate beyond the schema files.
