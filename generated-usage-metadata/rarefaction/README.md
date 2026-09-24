# Rarefaction / size-controlled coverage (§sec:rarefaction, Table 6, Figure 5)

**Status: verified reproducible (2026-09-24).** Reviewer 2 (round 2) argued the higher schema
coverage of robotic logs might just be a sampling-size artifact ("more queries cover more
vocabulary"). This analysis controls for sample size via rarefaction (Hurlbert 1971) and reports
Chao1 asymptotic richness (Chao 1984), then bootstraps a CI on the size-controlled comparison.

## Scripts (both authoritative, both cover Bio2RDF *and* Wikidata)

- `KG-Usage-analysis/rarefaction_size_control.py` — point estimates (Table 6) and the
  rarefaction-curve figure. Despite living in `KG-Usage-analysis/`, its own output figure
  (`rarefaction_organic_vs_robotic.png`, written next to the script) is manually copied to
  `manuscript/texsupport.iospress-sw-master/rarefaction.png` for the LaTeX build (Figure 5) —
  confirmed byte-identical to the currently-committed manuscript copy, so this is not a stray
  duplicate, just an undocumented manual step. Re-run this script and re-copy if the input CSVs
  or the TSE constants ever change.
- `KG-Usage-analysis/rarefaction_ci.py` — bootstrap (Monte-Carlo) 95% CIs on the
  size-controlled robotic/organic ratio. Its `PAIRS` list covers both Bio2RDF and Wikidata, and
  both CIs feed the manuscript (the "0.88x, not significant" / "1.03x, significant" contrast in
  §sec:rarefaction). Renamed from `wd_rarefaction_ci.py` (2026-09-25) since the old `wd_` prefix
  was misleading given it was never Wikidata-only.

## Inputs

Both scripts read directly from the already-committed
`generated-usage-metadata/*_combined_schema_elements.csv` files (see the parent directory's
README for what those are and their provenance caveat) — no raw log or KG dump access needed to
reproduce this analysis. TSE constants are hardcoded in each script's `PAIRS` list (541 for
Bio2RDF, 104,286 for Wikidata 2017 — the current canonical values).

## Outputs (this folder)

- `table6_point_estimates.txt` — console output of `rarefaction_size_control.py`, reproduces
  Table 6 exactly.
- `bootstrap_ci.txt` — console output of `rarefaction_ci.py`. Reproduces the manuscript's
  ratios and conclusions exactly (Bio2RDF 0.88x not significant, Wikidata 1.03x significant) but
  not Bio2RDF's exact published CI bounds ([0.73,1.03] here vs. published [0.75,1.02]) — a known
  numpy-version effect on `Generator.choice(replace=False)`, already documented in
  `REPRODUCIBILITY.md`, not a new issue. The manuscript's originally-published CI was kept as-is
  since the conclusion is unaffected either way.

Neither script's actual figure/table output needed regenerating or moving — both were verified
to already reproduce the published numbers exactly (mod the documented numpy caveat), so nothing
about the analysis itself changed here, only its documentation.
