# Wikidata content-supply vs. query-demand mismatch (Figure 6, Table `tab:domains`)

Supports §4.8's "Query Demand and KG Supply" subsection: whether the classes Wikidata *contains*
the most of are the classes users actually *query* as classes.

## Scripts

- `KG-Usage-analysis/wd_mismatch.py` — Figure 6 (`wd_mismatch.png`): supply×demand quadrant
  scatter (enrichment candidates / rich-but-ignored classes). Writes to
  `out/wd_mismatch_{year}.png` (gitignored); needs manual copying to
  `manuscript/texsupport.iospress-sw-master/wd_mismatch.png`, same undocumented-copy pattern as
  Figure 5 (see `generated-usage-metadata/rarefaction/README.md`).
- `KG-Usage-analysis/wd_domains.py` — Table `tab:domains` (content--demand inversion by
  top-level domain). Console output only, no committed file.

## Inputs

- Supply: `generated-usage-metadata/wikidata-supply/instances_per_class_2017.csv` (from
  `wd_supply.py`, already committed).
- Domain hierarchy: `generated-usage-metadata/wikidata-schema/p279_edges_2017.tsv` (already
  committed).
- Demand: `out/wd_{organic2017,robotic2017}_used.csv`, produced by `wd_coverage.py` from the
  raw Wikidata query logs (`data/logs/wikidata/int1_2017_*.tsv.gz`). Not committed by default
  (an `out/` intermediate) — **the organic-2017 copy now is**, at
  `wd_organic2017_used.csv` in this folder (regenerated and verified 2026-09-24: 4,038 elements,
  3,559 types / 479 predicates — matches the manuscript's used-element counts for Wikidata
  organic 2017 exactly, mod a known ±3 predicate variance already documented in
  `VALIDATION_SUMMARY.md`).

**Robotic-2017 demand not regenerated here** — needs `int1_2017_all.tsv.gz` (2.7 GB), which
isn't present on this machine (only on Maryam's server, where comment #8's Wikidata
robotic-2017 classvalue rerun used it). Without it, `wd_domains.py`'s robotic column would
silently compute as all-zero rather than fail loudly, so it was not run here to avoid producing
a misleadingly empty result — the organic side alone was verified instead. Table `tab:domains`
and Figure 6 as published were presumably generated with both halves present (likely on the
server); this is a reproducibility gap for the robotic half specifically, not a correctness
concern for the published numbers.

## Verified this session (organic half only)

Running `wd_mismatch.py 2017 out/wd_organic2017_used.csv` reproduces the manuscript's named
examples exactly: `Q6581072` (*female*) is the top enrichment candidate (high query demand,
essentially zero instance supply) — matching the class/value-position discussion in
§sec:classvalue and the mismatch figure's caption examples.

Bonus find while running this: `wd_coverage.py`'s (and 13 other scripts') worker-output reader
(`open(to)`, reading the Node/sparqljs worker's JSON-lines temp file) had no explicit encoding,
so Python fell back to Windows' default `cp1252`, which crashes (`UnicodeDecodeError`) on
non-Latin-1 bytes in query text or labels. Fixed across all 14 by opening with
`encoding='utf-8', errors='replace'` — same class of Windows-only latent bug as the
`csv.field_size_limit` issue (see `bio2rdf-2013-organic/README.md`), never previously visible
because these scripts had only ever been run on Maryam's Linux server.
