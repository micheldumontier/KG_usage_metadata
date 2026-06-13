# Cover letter — revised submission to the Semantic Web Journal

**Manuscript:** *Knowledge graph usage metadata: Insights from SPARQL log analysis*

Dear Editors,

Thank you for the opportunity to revise our manuscript, and for the two detailed and
constructive reviews. The revision is substantial: we have not only addressed every
specific comment but reframed the paper around the issue Reviewer 2 identified as
fundamental, and added five new analyses that turn the reviewers' main criticisms into
the paper's strongest results. We summarise the principal changes below; a complete,
point-by-point response is in the accompanying **Response to Reviewers**, and a
change-marked version of the manuscript (`main_changemarked.pdf`) shows every edit
relative to the reviewed version.

## What changed, and why

1. **Reframing around what "coverage" means on an item-based KG (Reviewer 2's central
   concern).** Reviewer 2 argued that summing heterogeneous Wikidata "classes" into one
   coverage number is not meaningful. We agree, and we now show *why*: we separate
   *class-position* from *value-position* references and find that ~30% of the items
   counted as queried "classes" in human queries are in fact used as property values. We
   compare query *demand* against KG *supply* and expose a structural content–demand
   inversion. This is now a central contribution rather than a buried assumption.

2. **Generality across modelling styles — a third KG (DBpedia).** To show the effect
   tracks the data model and not Wikidata's idiosyncrasies or scale, we added DBpedia
   (large and broad like Wikidata, OWL-style like Bio2RDF): only 6.5% of its queried
   classes are value-only, close to Bio2RDF and far below Wikidata's ~30%.

3. **Size-controlled organic-vs-robotic comparison.** Reviewer 2 correctly noted the raw
   coverage gap could be a sampling-size artifact. An individual-based rarefaction
   analysis (with a Monte-Carlo bootstrap CI) shows the gap is a genuine behavioural
   difference on the compact Bio2RDF (1.79×, 95% CI [1.62, 1.96]) but essentially a size
   artifact on Wikidata (1.03×, [1.02, 1.05]).

4. **When is an element "used"? — a closure bound.** Addressing the property-path concern,
   we built the P279 hierarchy from the dump and show that a naive closure-based notion
   would mark ~62% of all Wikidata classes as "used," driven by a handful of queries
   rooted at near-top classes — concrete evidence that explicit reference is the right
   primitive for an item-based KG.

5. **Robustness over equal-length intervals, and a demonstration of utility.** We verified
   the temporal results across seven consecutive equal-length windows, and added a
   forecasting experiment showing the usage metadata predicts the next year's query demand
   far better than KG content statistics (a query-level bootstrap confirms the advantage
   is well outside sampling noise).

We also directly addressed Reviewer 2's specific examples and Reviewer 1's detailed
points: we **measured** example-query contamination (it is bounded — ~1.4% of executions
— and does not affect the results) and corrected the *female*/*male* anecdote (the cited
"male", Q6581080, is in fact *Pirhasan*, a Turkish neighbourhood; the real male value
Q6581097 is queried, ~3:1, not absent); we **validated the class extraction** (querying
selects for instantiated, intentionally-modelled classes); we added a **domain-level
account** of the inversion; defined every key term with worked examples; renamed datasets;
fixed the units, figures, and factual issues; and report an independent reproducibility
audit that validated the inferential results and corrected a query-preprocessing defect in
the Bio2RDF-2019 validity counts.

All analysis code and generated usage-metadata datasets are available in the public
repository cited in the manuscript.

We believe the paper is now both clearer and substantially stronger, and we are grateful
to the reviewers for feedback that directly produced its best new results.

Sincerely,

The authors
