# Wikidata KG-content supply baselines

Content-only baselines (instances/class, triples/predicate) used by the supply-vs-demand
mismatch (Figure 6, `analysis-results/wikidata-mismatch/`) and the utility-ranking KG-supply
comparator (Tables 14–16, `analysis-results/wikidata-utility/`).

Run: `python3 KG-Usage-analysis/wd_supply.py <year>` (reads the Wikidata dump from stdin)

Input: `data/kg/wikidata-20170821-all-BETA.ttl.gz` (2017 Wikidata dump), streamed via
`zcat | wd_supply.py 2017`

Output: `instances_per_class_2017.csv` (class, instance count), `triples_per_pred_2017.csv`
(predicate, triple count — not restricted to the schema universe; consumers restrict it
themselves).
