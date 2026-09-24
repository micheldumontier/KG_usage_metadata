# DBpedia schema + class-position analysis (Table 11 `tab:generality`, "DBpedia as an Additional Case Study")

DBpedia serves as the manuscript's third KG: an OWL-style schema (like Bio2RDF) but broad and
general-purpose (like Wikidata), used to test whether Wikidata's value-position inflation
(§sec:classvalue) is item-based-KG-specific or more general.

- `classes.txt` (790 `dbo:` classes), `predicates.txt` (3,024 predicates),
  `instances_per_class.csv` — the full current DBpedia ontology schema and instance counts,
  extracted via `KG-Schema-extractors/dbpedia_lsq_extract.py` from the LSQ 2.0 endpoint
  (`lsq.data.dice-research.org`). See that script's own notes (and `CLAUDE.md`) for a real
  undocumented Virtuoso limit found building it: `ORDER BY` combined with `LIMIT`/`OFFSET` past
  10,000 rows combined is rejected outright, worked around with plain unsorted pagination.
- Analysis script: `KG-Usage-analysis/dbpedia_analysis.py`, reading
  `data/logs/dbpedia/dbpedia_texts.txt` (1.7 GB, distinct executed DBpedia query texts, not
  committed — see `REPRODUCIBILITY.md`) plus the schema files above. Console output only, no
  committed intermediate beyond the schema itself.

**Not re-verified locally this session** — the 1.7 GB query-text log isn't present on this
machine. The published numbers (722 classes referenced; class-position 675→**682**
(93.5%→**94.5%**), value-only 47→**40** (6.5%→**5.5%**), after review round 4's comment #8
class-position fix) were produced and verified on Maryam's server — see `CLAUDE.md`'s comment
#8 section and `manuscript/RESPONSE_TO_REVIEW4.md` for that verification's detail. Nothing here
contradicts or needs correcting; this is purely a documentation gap (no README existed for this
folder before), not a data-quality one.
