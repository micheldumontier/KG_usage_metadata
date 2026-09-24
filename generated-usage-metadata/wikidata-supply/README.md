# Wikidata KG-content supply baselines

Content-only baselines (computed "without using query-log information", as the manuscript's
utility-ranking framing requires) for two analyses: the supply-vs-demand mismatch (Figure 6,
`wd-mismatch/`) and the utility-ranking KG-supply comparator (Tables 14-16, `wd-utility/`).

- `instances_per_class_2017.csv` — instances per class (object of `wdt:P31`), from a single
  streaming pass over the 2017 Wikidata dump.
- `triples_per_pred_2017.csv` — triples per predicate (occurrences of each `wdt:P` predicate),
  from the same pass. **Not restricted to the schema universe** (3,668 entries vs. the
  931-predicate schema) — this asymmetry was exactly the bug review round 4's comment #13
  found and fixed in the *consumer* scripts (`wd_utility_ranking.py`/`wd_utility_predicates.py`
  now restrict to schema-only elements themselves rather than assuming this file already is).

Produced by `KG-Usage-analysis/wd_supply.py <year>`, reading the decompressed 2017 Wikidata
dump from stdin (`data/kg/wikidata-20170821-all-BETA.ttl.gz`, not committed — 21 GB, see
`REPRODUCIBILITY.md`).
