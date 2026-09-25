# Bio2RDF federated-querying notebooks (inactive, kept for one reason)

Not part of the current pipeline — supported a subsection removed from the manuscript because
the method couldn't distinguish genuine cross-dataset joins from an architecture change between
the 2013 and 2019 logs.

Kept rather than deleted: `2013KG-get_datasets_relationships_bio2rdf.ipynb` (cell 3,
`allowed_vocabularies`) is the only surviving record of the 17-dataset-name allowlist behind
`generated-usage-metadata/schema-Bio2RDF-17Subgraphs.csv` (used throughout Table 3 and
§sec:bio2013). See `KG-Schema-extractors/build_bio2rdf_canonical_schema.py`'s docstring.

Contents: `2013KG-get_datasets_relationships_bio2rdf.ipynb`,
`2019KG-get_datasets_relationships_bio2rdf.ipynb`, and their outputs in
`generated-usage-metadata/Bio2RDF-federated-querying-datasets/`.
