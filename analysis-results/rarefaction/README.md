# Rarefaction / size-controlled coverage (Table 6, Figure 5)

Controls for sample size when comparing organic vs. robotic schema coverage, via rarefaction
(Hurlbert 1971) and Chao1 asymptotic richness (Chao 1984), then bootstraps a CI on the
size-controlled robotic/organic ratio. Covers both Bio2RDF and Wikidata.

Run: `python3 KG-Usage-analysis/rarefaction_size_control.py` (Table 6 + figure),
`python3 KG-Usage-analysis/rarefaction_ci.py` (bootstrap CIs)

Input: `generated-usage-metadata/*_combined_schema_elements.csv` (no raw logs or KG dump needed)

Output: `rarefaction_size_control.py` writes `rarefaction_organic_vs_robotic.png` next to itself
in `KG-Usage-analysis/` — copy to `manuscript/texsupport.iospress-sw-master/rarefaction.png` for
the LaTeX build (Figure 5). This folder holds the console output of both scripts:
`table6_point_estimates.txt`, `bootstrap_ci.txt`.

Note: the bootstrap CI depends on `numpy.random.Generator.choice`'s sampling algorithm, which has
changed across numpy versions — a rerun may reproduce the same ratio/conclusion without matching
the exact CI bounds bit-for-bit.
