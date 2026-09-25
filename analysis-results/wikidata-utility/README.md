# Wikidata utility ranking (Tables 14–16)

Ranks Wikidata types/predicates by 2017 query usage vs. by KG content (instances/triples), and
evaluates each ranking against 2018 query demand (nDCG@k, coverage@k, demand-weighted MRR).

Run: `python3 KG-Usage-analysis/wd_utility_ranking.py` (types),
`python3 KG-Usage-analysis/wd_utility_predicates.py` (predicates)

Input: 2017 organic TRAIN logs + 2018 organic TEST log
(`data/logs/wikidata/int1_2017_organic.tsv.gz` etc.), `generated-usage-metadata/wikidata-schema/`,
`generated-usage-metadata/wikidata-supply/`

Output (this folder): `wd_utility_ranking.log`, `wd_utility_predicates.log` — run logs with the
nDCG/coverage/MRR tables.
