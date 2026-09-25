# Wikidata class-position vs. value-position (Table 9)

Classifies each Wikidata "used type" as class-position (object of `wdt:P31`/`wdt:P279`, or
subject of `wdt:P279`) or value-only, for organic and robotic 2017 query logs.

Run: `python3 KG-Usage-analysis/wd_classvalue.py organic2017` (and `robotic2017`)

Input: `data/logs/wikidata/int1_2017_organic.tsv.gz` / `int1_2017_all.tsv.gz`, the 2017 Wikidata
schema (`generated-usage-metadata/wikidata-schema/`)

Output (this folder): `wd_classvalue_organic2017.log`, `wd_classvalue_robotic2017.log` — run logs
with used-type counts and the class/value split.
