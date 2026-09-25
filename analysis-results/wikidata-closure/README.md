# Wikidata P279-closure bound (§3.4 / Discussion limitations)

For each organic-2017 query anchored at a near-root class via `wdt:P279*`/`wdt:P31/wdt:P279*`,
computes how many additional classes its closure credits beyond the literal query text — the
data behind the "explicit vs. semantic usage" limitation in the Discussion.

Run: `python3 KG-Usage-analysis/wd_p279_edges.py` then `python3 KG-Usage-analysis/wd_closure_queries.py`

Input: the 2017 Wikidata dump (`data/kg/wikidata-20170821-all-BETA.ttl.gz`), the interval-1 2017
organic log

Output (this folder; script's own default is `out/`, copied here):
`wd_closure_anchor_queries.tsv` (one row per anchored query), `wd_closure_bound_summary.txt`
(aggregate closure-bound summary).
