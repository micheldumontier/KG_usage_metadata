# Bio2RDF 2013-era organic queries (browser user-agent)

Supports §sec:bio2013 ("Organic vs. Robotic in the 2013-era Bio2RDF Log", Table 8 and the
version-matched-robustness paragraph) and the equal-effort comparison in §sec:rarefaction.

**Input provenance gap, needs filling in:** derived from the raw Bio2RDF server access log
(expected at `~/data/bio2rdf.logs/bio2rdf.sparql.log.all/*.gz`, May 2013–Sep 2015, 127.2M
executed SPARQL requests; the upstream source of LSQ before anonymization). This file is not
redistributed here and its exact origin (who provided it, from where) isn't recorded anywhere
in the repo — worth adding once confirmed, since it's the one raw input in the whole pipeline
with no documented source.

- `organic_2013_queries.txt.gz` — 115,420 executed browser-UA SPARQL queries (decoded, one
  line per occurrence; 61,628 unique), extracted by
  `KG-Usage-analysis/bio2rdf2013_log_compose.py` (status 200, browser UA; Virtuoso-internal +
  LSQ-harvest infrastructure traffic excluded — see Table `tab:bio2013comp`'s composition
  breakdown).
- `bio2rdf2013_organic_used.csv` — used schema elements + occurrence counts, from
  `KG-Usage-analysis/bio2rdf2013_organic_coverage.py`. **Regenerated 2026-09-24** against the
  canonical 541-element schema (`bio2rdf-schema/`): 289 elements (167 types + 122 predicates),
  coverage 289/541 = 53.42% — matches the manuscript's "53.4% (167/350 types, 122/191
  predicates)" exactly. Replaces a stale committed copy that had 292 elements against the old
  pre-Resource-exclusion 545-element denominator (53.6%).

Rerunning this script also surfaced and fixed two real bugs (2026-09-24), unrelated to the
number above but found while verifying it:
- The script's own `csv.field_size_limit(sys.maxsize)` call overflows Windows' 32-bit C `long`
  (the same bug class already fixed once in `sparql_log_preprocess.py` for comment #14, but
  this script calls the C function directly rather than going through that shared module, so
  it wasn't covered by that fix). Fixed the same way here, and audited every other script in
  the repo: 11 total had the same unguarded call (`concentration_metrics.py`,
  `bio2rdf_coverage_vs_schema.py`, `adoption_dynamics.py`, `template_linkage.py`,
  `dbpedia_analysis.py`, `wd_closure_bound.py`, `wd_coverage.py`, `wd_classvalue.py`,
  `wd_decontaminate.py`, `wd_temporal.py`, `wd_utility_ci.py`), all now fixed. None had been
  run on Windows before (previously always run on a Linux server), which is why this hadn't
  surfaced already.
- The script's own "[compare: organic-2019 = ...]" console line hardcoded stale
  pre-Resource-exclusion figures (116/545 = 21.28%; 529/545 = 97.06%) — this is exactly the
  example review round 4's comment #1 gave. Updated to the current canonical values
  (113/541 = 20.89%; 525/541 = 97.04%, matching Table 5 and `rarefaction/table6_point_estimates.txt`
  exactly). This print statement doesn't feed any file or figure, so no other correction was
  needed once it was updated.
