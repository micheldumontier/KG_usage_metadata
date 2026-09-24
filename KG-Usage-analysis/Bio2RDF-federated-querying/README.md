# Bio2RDF federated-querying analysis (orphaned, kept — decided 2026-09-24)

**Not part of the current manuscript.** This analysis originally supported the "Pairwise Schema
Type Usage of Bio2RDF" subsection, which review round 4's comment #7 asked to remove: the
triple-pattern-only method couldn't distinguish genuine 2013 `SERVICE`-based cross-dataset
joins from the 2019 unified-endpoint architecture, so the reported "3 in 2013 → 22 in 2019"
comparison conflated a real usage question with an architectural artifact. The subsection, its
figure, and the matching Discussion paragraph were removed in commit `348be4a`; this analysis
has been uncited since.

**Decision: keep rather than remove**, for a concrete reason — despite the analysis itself being
retired, `2013KG-get_datasets_relationships_bio2rdf.ipynb` (cell 3, `allowed_vocabularies`) is
the *only surviving record* of the 17-dataset-name allowlist behind
`generated-usage-metadata/schema-Bio2RDF-17Subgraphs.csv` (the 2013-log-coverage TSE
denominator used throughout Table 3, §sec:bio2013, and §sec:rarefaction). See
`KG-Schema-extractors/build_bio2rdf_canonical_schema.py`'s docstring for the full derivation
this notebook made possible to reconstruct. Deleting this notebook would re-orphan that
derivation.

## Contents

- `2013KG-get_datasets_relationships_bio2rdf.ipynb`, `2019KG-get_datasets_relationships_bio2rdf.ipynb`
  — the original pairwise cross-subgraph-relationship extraction notebooks (2013 and 2019 logs
  respectively).
- `generated-usage-metadata/Bio2RDF-federated-querying-datasets/` — their outputs:
  `2013_17_subgraphs_DataSet_relationship_patterns.csv`,
  `2013_query_DataSet_relationship_patterns.csv`,
  `2019_26_subgraphs_DataSet_rel_patterns.csv`,
  `2019_query_DataSet_relationship_patterns26.csv`. Also uncited, kept alongside the notebooks
  that produced them for the same reason.
