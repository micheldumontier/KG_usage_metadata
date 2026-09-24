# Wikidata class-position/value-position run logs (Section 4.5 / Table 9, comment #8)

**Status: resolved (2026-09-24).** Raw stdout logs from `KG-Usage-analysis/wd_classvalue.py`
(run on Maryam's server, post-fix — subject-of-`P279`/`rdfs:subClassOf` now also counts as
class-position), for both 2017 Wikidata query classes. Pasted into this session rather than
uploaded as files, then committed here so the numbers behind Table 9 and `tab:generality` are
traceable without rerunning the pipeline.

- `wd_classvalue_organic2017.log` — organic-2017 run. Used types 12,773; class-position
  9,286 (72.7%); value-only 3,487 (27.3%).
- `wd_classvalue_robotic2017.log` — robotic-2017 run. Used types 58,689; class-position
  55,698 (94.9%); value-only 2,991 (5.1%). This run followed a first attempt that failed on
  a truncated `int1_2017_all.tsv.gz` download (`EOFError`); the unique-query count here
  (8,234,089) matches Table 2's existing robotic-2017 row exactly, confirming the
  re-download was the same dataset, not a different slice.

Both logs' "used types" totals match the pre-fix manuscript values exactly (12,773 and
58,689) — the fix changes only how each referenced type is classified, not the underlying
universe. See `manuscript/RESPONSE_TO_REVIEW4.md` (comment #8) and `CLAUDE.md` for the
full before/after comparison and how these numbers were applied to `main.tex`.

Not included here: the DBpedia half (682/40, 94.5%/5.5%) and its `dbpedia_lsq_extract.py`
run, which weren't captured as a log — see `RESPONSE_TO_REVIEW4.md` for those figures.
