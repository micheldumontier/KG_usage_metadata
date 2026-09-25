# Concentration of usage + singleton sensitivity (Tables 7 and 12)

Table 12: Gini coefficient, Pielou evenness, top-10% share, and P80 of the used-element
usage-frequency vectors (both within-used-elements and over the full schema universe). Table 7:
what fraction of used elements are singletons (used exactly once), and coverage with/without
them. Note: Table 7 sits in §sec:rarefaction in the manuscript text, not §4.9, despite being
grouped here.

Run: `python3 KG-Usage-analysis/concentration_metrics.py` (Table 12),
`python3 KG-Usage-analysis/bio2rdf_recompute_conformant.py` (Table 7's Bio2RDF rows)

Input: `generated-usage-metadata/*_combined_schema_elements.csv`

Output: `table12_concentration.txt` (console output, reproduces Table 12),
`concentration_metrics.csv` (same data, machine-readable). Table 7's Wikidata rows have no
dedicated script — they're a direct count of `TotalCount == 1` rows in the central
combined_schema_elements files.
