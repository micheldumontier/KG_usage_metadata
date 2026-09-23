# Wikidata closure-bound artifacts (Section 3.4 / Section 5 limitations, comment #14)

**Status: pending.** This folder is a placeholder for two files requested in review
round 4, comment #14 — they exist on the co-author's machine but are not yet
committed here, since regenerating them locally requires data this repo doesn't
have (the raw Wikidata organic query logs and `p279_edges_2017.tsv`, itself
derived from the full Wikidata dump — see `REPRODUCIBILITY.md`).

- `wd_closure_anchor_queries.tsv` — every organic query anchored at a near-root
  class via `wdt:P279*`/`wdt:P31/wdt:P279*`, i.e. the raw data behind the
  "explicit vs. semantic usage" limitation in the Discussion (Section 5).
- `wd_closure_bound_summary.txt` — the closure-bound summary against the class
  universe and TSE denominators (companion output from the same script run).

Produced by `KG-Usage-analysis/wd_closure_queries.py` and
`KG-Usage-analysis/wd_closure_bound.py`, which by default write to `out/`, not
here — they were copied into this folder from a run whose logic matches the
numbers currently in the manuscript.

**Before dropping the real files in, verify they match the published numbers**
(the manuscript's closure discussion was corrected once already for a scope bug
and an off-by-one — see `RESPONSE_TO_REVIEW3.md`):
- 1,276 distinct anchor classes
- 62,410 additional classes credited by the closure
- `Q35120` (*entity*) anchors **12** queries (not 13 — that was the pre-fix count)
- `Q151885` (*concept*) anchors 49,828 classes
- closure share: 62.8% of the class universe, 62.2% of TSE

If a candidate file disagrees with these, it's most likely from before that
correction and shouldn't be committed as-is.
