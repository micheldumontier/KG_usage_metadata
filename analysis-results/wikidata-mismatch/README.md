# Wikidata content-supply vs. query-demand mismatch (Figure 6, Table `tab:domains`)

Checks whether the classes Wikidata contains the most instances of are the classes users
actually query as classes; groups classes into top-level domains and compares each domain's
share of KG content against its share of query demand.

Run: `python3 KG-Usage-analysis/wd_mismatch.py <year> <demand_file>` (Figure 6),
`python3 KG-Usage-analysis/wd_domains.py` (Table `tab:domains`)

Input: `generated-usage-metadata/wikidata-supply/instances_per_class_2017.csv`,
`generated-usage-metadata/wikidata-schema/p279_edges_2017.tsv`, and a demand file
(`wd_organic2017_used.csv` / `wd_robotic2017_used.csv`) produced by `wd_coverage.py` from the raw
Wikidata query logs.

Output: `wd_mismatch.py` writes `wd_mismatch_{year}.png` (copy to
`manuscript/texsupport.iospress-sw-master/wd_mismatch.png` for the LaTeX build); `wd_domains.py`
prints the domain table to console. This folder holds `wd_organic2017_used.csv`, the organic-2017
demand file.
