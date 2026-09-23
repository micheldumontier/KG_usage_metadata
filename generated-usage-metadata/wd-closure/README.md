# Wikidata closure-bound artifacts (Section 3.4 / Section 5 limitations, comment #14)

**Status: resolved (2026-09-23).** Regenerated locally rather than obtained from
the co-author: downloaded the 2017 Wikidata dump (21 GB) and the interval-1 2017
organic log, ran `wd_p279_edges.py` then `wd_closure_queries.py` (default,
non-pooled scope — see `REPRODUCIBILITY.md`).

- `wd_closure_anchor_queries.tsv` — every organic query anchored at a near-root
  class via `wdt:P279*`/`wdt:P31/wdt:P279*` (14 rows), i.e. the raw data behind
  the "explicit vs. semantic usage" limitation in the Discussion (Section 5).
- `wd_closure_bound_summary.txt` — the closure-bound summary against the class
  universe and TSE denominators (companion output from the same script run).

Produced by `KG-Usage-analysis/wd_closure_queries.py`, which by default writes
to `out/`, not here — copied into this folder after verifying the run below.

**Verified against the published numbers** (the manuscript's closure discussion
was corrected once already for a scope bug and an off-by-one — see
`RESPONSE_TO_REVIEW3.md`) — all match exactly:
- 1,276 distinct anchor classes ✓
- 62,410 additional classes credited by the closure ✓
- `Q35120` (*entity*) anchors **12** queries (not 13 — that was the pre-fix count) ✓
- closure share: 62.8% of the class universe, 62.2% of TSE ✓

Note: the manuscript's per-anchor closure-size examples (e.g. *entity*'s own
closure of 64,356 classes, *concept*'s 49,828) are not reproduced by this
script's printed output, which only reports the aggregate closure across all
anchors combined (64,906 classes) — those specific per-anchor figures were not
independently re-verified here.
