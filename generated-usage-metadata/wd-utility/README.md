# Wikidata utility-ranking run logs (Section 4.7 / Tables 10-12, comment #13)

**Status: resolved (2026-09-24).** Raw stdout logs from `KG-Usage-analysis/wd_utility_ranking.py`
(types) and `KG-Usage-analysis/wd_utility_predicates.py` (predicates), run on Maryam's server
after the candidate-universe fix (both rankings aligned to the actual schema universe —
`types_2017.txt`/`preds_2017.txt` — usage extended with zero-usage padding for unobserved
schema elements, supply restricted to schema-only elements). Pasted into this session rather
than uploaded as files, then committed here so the numbers behind Tables 10-12 are traceable
without rerunning the pipeline.

- `wd_utility_ranking.log` — type-suggestion ranking. TRAIN distinct=7,572, TEST distinct=3,523.
  Candidate universe (103,355 types) is far larger than any evaluated `k` (max 1,000), so the
  fix barely moved these numbers: only the usage-side coverage/nDCG at k=100/500/1000 shifted by
  0.1-0.3 points; supply-side and all of k=10/50 are bit-for-bit unchanged from the pre-fix
  published values.
- `wd_utility_predicates.log` — predicate-suggestion ranking. TRAIN distinct preds=2,688, TEST
  distinct=2,103, evaluated up to k=931 (the actual 2017 predicate-schema size, computed
  dynamically as `len(SCHEMA)` rather than a fixed 1000 as before). Here the fix changed the
  numbers substantially, because the pre-fix supply ranking was built from
  `triples_per_pred_2017.csv` (3,668 entries, unrestricted to the `wdt:P` namespace) rather than
  the 931-predicate schema — exactly the asymmetric mismatch traced in `CLAUDE.md`/comment #13.
  At k=931 (=schema size), usage and supply coverage are now **exactly equal (51.3% = 51.3%)**,
  which is precisely the check the reviewer proposed (a top-k cutoff that already includes every
  candidate must give identical coverage) and which the pre-fix numbers (94.8% vs 93.3% at
  k=1000) never actually satisfied.

See `manuscript/RESPONSE_TO_REVIEW4.md` (comment #13) and `CLAUDE.md` for the full before/after
comparison and how these numbers were applied to `main.tex` (Tables `tab:utility`, `tab:ranking`,
and `tab:predranking`, plus the surrounding prose).
