# Response to the external review (`GPT_REVIEW.md`)

This note maps each point in the external review to the current manuscript: either to
text that already addresses it, or to a change made in response. Section/label
references are to `main.tex`. Three new analyses were added (concentration, adoption
dynamics, template→coverage linkage); their scripts are in `KG-Usage-analysis/` and
their captured outputs in `out/`.

---

## Major concern 1 — "Usage" is too narrow (syntactic vs. semantic)

**Agreed, and adopted the reviewer's framing.** The paper already drew the
explicit-reference vs. closure distinction conceptually and bounded its size
(the closure of near-root anchors would mark ~62% of Wikidata classes "used" off a
handful of queries; Section~\ref{sec:used}, Discussion). We have now adopted the
reviewer's exact terminology and framed the paper as a study of **syntactic usage**:

- New definition in the Introduction terminology paragraph (Section~\ref{s1}): syntactic
  usage = IRI explicitly written; *semantic (effective) usage* = additionally crediting
  elements reached only at evaluation time. We state we adopt syntactic usage throughout.
- The "What we mean by used" paragraph (Section~\ref{sec:used}) and the Discussion
  limitation (now titled *"Syntactic vs. semantic (effective) usage"*) use the same terms.
- The closure bound is retained as positive evidence that semantic usage is *ill-behaved*
  on an item-based KG, so syntactic usage is the right primitive — not merely the easy one.

## Major concern 2 — Coverage may not be the most meaningful metric (entropy/Gini/Pareto)

**Agreed; added a concentration analysis (new).** Coverage is a breadth metric; we now
quantify how *unevenly* that breadth is exercised.

- New Section~\ref{sec:concentration} + Table~\ref{tab:concentration}: per-dataset Gini,
  Pielou evenness *J*, top-10 share, and *P₈₀* (fraction of used elements carrying 80% of
  references). Script: `KG-Usage-analysis/concentration_metrics.py`.
- Finding: usage is extremely concentrated everywhere (**Gini 0.90–0.99**); **0.02–4.3%**
  of used elements account for 80% of references; the top-10 Bio2RDF elements carry 83–93%.
  So a high coverage number means "almost everything is touched once," *not* "demand is
  even" — the reviewer's exact worry, now stated explicitly in the abstract and Discussion.
- We frame coverage and concentration as **complementary** ("how much is reached" vs. "how
  unequally"), and note when each (or entropy/Gini) is the right summary.

## Major concern 3 — Bio2RDF schema extraction / 2024-vs-historical mismatch (their "toughest")

**Already addressed, and we go beyond the reviewer's suggested sensitivity analysis.**

- Consistent-reference-set design (Section~\ref{s3}.4, Section 4.1): numerator and
  denominator come from the same subgraphs; Venn diagrams show the log/KG overlap.
- **Schema-version robustness** (Section~\ref{sec:bio2013}): we recovered the actual
  Release-2 and Release-3 schemas from Bio2RDF's published per-dataset statistics, split the
  2013 organic log at the mid-2014 release boundary, and recomputed coverage version-matched.
  Result: the 2024 schema *under*-recognizes historical vocabulary (referenced-vocabulary
  presence rises 17.5% → 48%/62% once release-matched), so the 2024-based 2013 figure is a
  **conservative** estimate — aligning the schema *raises* it. The recovered schemas ship
  with the artifacts.
- The reviewer suggested (i) log-only coverage and (ii) 2024-schema coverage as two legs of a
  sensitivity check; we provide the stronger release-matched recomputation, which subsumes
  the concern. The 2019 log is already version-matched (same Release 4 the 2024 endpoint serves).

## Major concern 4 — Organic/robotic distinction is simplistic

**Agreed; added an explicit classification-uncertainty caveat.** New Discussion limitation
(*"Organic vs. robotic is a user-agent proxy, not a ground truth"*): the user-agent scheme of
Malyshev/Bielefeldt labels non-browser clients "robotic," but notebooks, API clients,
extensions, and LLM agents blur this and UA strings can be spoofed — so "robotic" reads as
"non-browser," not "non-human." We note our two mitigations (within-class reporting;
size-controlled rarefaction before reading a gap as behavioral) and the independent syntactic
corroboration that the classes differ in kind (vendor full-text/`OPTION` syntax concentrates in
organic traffic). Content/session-based classification is flagged as future work.

## Major concern 5 — Limited generalization (3 KGs; DBpedia as sanity check)

**Partly already addressed (DBpedia is a full third subject, isolating modeling style from
size; Section~\ref{sec:classvalue}, generality table), now with explicit scoping.** New
Discussion limitation (*"Scope: an exploratory study across contrasting modeling styles"*)
positions the work as exploratory across deliberately contrasting architectures and names
UniProt, ChEMBL, OpenAlex, Europeana, and government portals as future targets (gated on log
access).

---

## Missing analyses

1. **Demand vs. maintenance cost** — added to the new future-work Discussion paragraph
   (*"Toward demand-aware governance…"*): pair the existing supply–demand inversion with a
   maintenance-cost signal to target curation/deprecation. (Conceptual; no cost data in logs.)
2. **Schema evolution vs. query evolution (do new elements become popular?)** — **added as a
   new analysis.** New "Adoption of newly introduced schema elements" paragraph (temporal
   results). Script: `adoption_dynamics.py`. Finding: of 68 predicates new in the 2018 Wikidata
   dump, 71%/31% (robotic/organic) are queried but **none reach the top-100**; of 1,357
   predicates added in Bio2RDF Release 3, only 9% are ever queried and 2 reach the top-20. New
   elements are *tried* but rarely displace the core within a year.
3. **Query-template linkage (Asprino)** — **added as a new analysis.** New
   Section~\ref{sec:templates}. Script: `template_linkage.py`. Template = predicate signature.
   Finding: query *volume* is driven by very few templates (2 cover 80% of Bio2RDF organic
   queries; 3,179 for Wikidata) while schema *breadth* comes from a long tail of specialised,
   often single-use templates; rare classes are reached only through low-popularity templates
   (Spearman ρ = 0.23/0.34; bottom- vs. top-decile median template popularity 1/3,525 and
   22/17,472). The few-vs-many template contrast is itself a modeling-style signature.
4. **Execution-aware usage (referenced/executed/successful/returned)** — added to the
   future-work paragraph; the LSQ-derived logs lack result/success data, so this needs
   instrumented endpoints.

## Writing/presentation

- *Move methodological detail to supplementary* — noted; this is an SWJ-tolerant judgment call
  and the pipeline detail is load-bearing for the acceptance-hardening reviewers asked for. Not
  changed for now; can be relocated if the editor prefers.
- *Strengthen/consolidate the conceptual discussion* — the modeling-style and demand–supply
  arguments already anchor the Discussion; the new concentration and template results reinforce
  them. We did not add a separate conceptual section to avoid duplicating the Discussion.

---

### Summary of changes
- New: Section~\ref{sec:concentration} + Table~\ref{tab:concentration} (concentration).
- New: adoption-dynamics paragraph (temporal results).
- New: Section~\ref{sec:templates} (template→coverage linkage).
- Reframed: syntactic vs. semantic usage (Intro, Section~\ref{sec:used}, Discussion).
- New Discussion limitations: UA-classification caveat; exploratory-scope statement;
  demand-aware-governance + execution-aware-usage future work.
- Abstract and contributions updated to reflect the above.
- Scripts: `concentration_metrics.py`, `adoption_dynamics.py`, `template_linkage.py`,
  `template_worker.js`; outputs captured under `out/`.
