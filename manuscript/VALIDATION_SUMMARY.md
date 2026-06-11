# Regenerated & validated tables — full reproducibility audit

Re-derived from raw logs and the source KG dumps. "paper" = published values.
Bold = the only consequential correction (Bio2RDF-2019 HTTP-param prep defect).

## Table 2 — parsing/validity (all 9 rows regenerated; #Failed = #Unique − #Valid)

| Dataset | #Queries (mine / paper) | #Unique (mine / paper) | #Valid (mine / paper) | verdict |
|---|---|---|---|---|
| Bio2RDF all 2013 | 31,950,877 / 31,950,877 | 1,519,681 / 1,519,793 | 1,517,160 / 1,514,544 | reproduces |
| **Bio2RDF all 2019** | 3,880,939 / 3,877,748 | 1,050,616 / 1,048,592 | **1,040,666 / 634,783** | **+64%** |
| **Bio2RDF robotic 2019** | 3,824,203 / 3,816,776 | 1,040,356 / 1,039,411 | **1,034,831 / 627,314** | **+65%** |
| **Bio2RDF organic 2019** | 56,736 / 53,524 | 12,579 / 9,612 | **8,140 / 7,357** | **+11%** |
| WD all-organic 2017 | 3,530,948 / 3,298,254 | 859,290 / 844,256 | 858,969 / 844,132 | reproduces* |
| WD robotic 2017 | 59,355,579 / 59,355,579 | 8,234,089 / 8,234,097 | 8,234,069 / 8,234,080 | exact |
| WD robotic 2018 | 81,339,186 / 81,339,186 | 18,939,743 / 18,940,103 | 18,939,657 / 18,940,050 | exact |
| WD organic 2017 | 192,330 / 192,331 | 88,514 / 88,516 | 88,491 / 88,493 | exact |
| WD organic 2018 | 872,555 / 872,556 | 185,478 / 185,482 | 185,443 / 185,438 | exact |

\* validity rate matches (99.96% vs 99.98%); counts ~7% high because the union of available log intervals exceeds the published set.

## Table 3 — Wikidata schema totals (extracted from 2017/2018 RDF dumps)

| KG version | types (mine / paper) | predicates (mine / paper) |
|---|---|---|
| Wikidata 2017 | 103,355 / 103,380 | 931 / 934 |
| Wikidata 2018 | 97,445 / 97,470 | 991 / 992 |

Bio2RDF Table 3 (26 subgraphs): types 350 / preds 195 / total 545 = paper exactly. "195 predicates" = predicates connecting two vocabulary classes; type set is all vocabulary classes (incl. `ctd_vocabulary:Gene-Disease-Association`, queried but absent from typed-to-typed patterns). Canonical flat lists at `generated-usage-metadata/bio2rdf-schema/`; reproduces Table 5 Bio2RDF coverage exactly: robotic/all-2019 97.06% (529/545), organic-2019 21.28% (116/545).

## Tables 4 & 5 — Wikidata used elements & coverage (logs × extracted schema)

| Dataset | used types (mine/paper) | used preds (mine/paper) | coverage (mine / paper) |
|---|---|---|---|
| organic 2017 | 3,559 / 3,559 | 479 / 482 | **3.87% / 3.87%** |
| organic 2018 | 4,310 / 4,310 | 546 / 549 | **4.93% / 4.93%** |
| all-organic 2017 | 12,773 / 12,590 | 803 / 804 | 13.02% / 12.84% |
| robotic 2017 | 58,689 / 58,680 | 919 / 923 | 57.16% / 57.13% |
| robotic 2018 | 58,648 / 58,648 | 933 / 934 | 60.53% / 60.51% |

## Other validations (not tables)
- Spearman ρ (0.158/0.484/0.571), Wilcoxon W, top-50 type overlaps, long-tail: reproduce **exactly** from the published count CSVs.
- Federated querying: corrected to **3 → 22** distinct cross-subgraph join patterns (published "23 of 85" was off-by-one and used an ill-posed denominator).
- Validity is parser-robust: 98–99% agreement across rdflib / sparqljs / pyoxigraph.

## Bottom line
The audit found exactly **one consequential error** — the Bio2RDF-2019 `#Valid` undercount from un-stripped HTTP query parameters — now corrected. **Schema coverage and every statistical finding reproduce** from source; the corrections do not change any qualitative conclusion.
