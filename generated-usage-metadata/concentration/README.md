# Concentration of usage + singleton sensitivity (Tables 7 and 12)

**Status: verified reproducible (2026-09-24), one real bug found and fixed.**

## Table 12 (`tab:concentration`) — Gini / Pielou evenness / top-10% / P80

`KG-Usage-analysis/concentration_metrics.py`, reading the central
`generated-usage-metadata/*_combined_schema_elements.csv` files (see the parent README).

**Bug found and fixed**: this script hardcoded `TSE_BIO_26, TSE_BIO_17 = 545, 399` — the
pre-Resource-exclusion Bio2RDF totals, superseded by the canonical 541/395 everywhere else in
the repo (Table 3, `rarefaction_size_control.py`, `bio2rdf_recompute_conformant.py`, ...). This
script alone was never updated. Effect: the full-schema-universe columns (Gini*/J*, which zero-
pad by the *unused* element count = TSE − N) were off by ~0.001 from the published values — e.g.
Bio2RDF-All-2013's Gini* printed as 0.932 instead of the published 0.931. Fixed the constants to
541/395; rerunning now reproduces Table 12 **exactly**, row for row, all eight columns
(`table12_concentration.txt`, committed here).

## Table 7 (`tab:singletons`) — physically sits in §sec:rarefaction, not §4.9

Despite the manuscript placing this table right after the rarefaction discussion (so it is
really part of §4.6, not §4.9 — a placement quirk worth knowing if searching for it), it's
grouped with Table 12 here because both are produced by an overlapping set of scripts and
concepts (used-element frequency vectors, TSE-relative statistics).

- **Bio2RDF rows** (robotic-2019, organic-2019): `KG-Usage-analysis/bio2rdf_recompute_conformant.py`,
  which already used the correct canonical 541/395 TSE (no fix needed) and reproduces every
  number exactly — verified this session, both "published" and "conforming" columns identical,
  confirming Bio2RDF's coverage/singleton/concentration/rarefaction numbers are all already
  internally consistent. This script also double-checks against a second, "conforming"
  definition (§3.2's strict predicate/type template) and finds no difference — a useful
  standing sanity check, not just a one-off computation.
- **Wikidata rows** (robotic, organic-full): no dedicated script — these are a simple derived
  statistic (count of central-file rows with `TotalCount == 1`) directly on
  `Wikidata robotic log2017_kg2017_combined_schema_elements.csv` and
  `Wikidata log2017kg2017_combined_schema_elements.csv`. Not verified independently this
  session, but trivial enough (one `pandas`/`csv` pass) that a dedicated script would be
  overkill; noting this so a future reader doesn't go looking for one.

Note: `wd_class_validation.py` and `template_linkage.py` also use the word "singleton" but for
unrelated concepts (class *support*-in-the-KG singletons for §4.8's validity paragraph, and
singleton *query templates* for §sec:templates respectively) — not this table.
