# Revision plan — from "correctable" to "a paper with a point"

Goal: lift the paper above its current ceiling (descriptive coverage metric + mostly-
expected findings) by (a) connecting the metric to a decision, (b) adding content-level
interpretation, and (c) demonstrating generality. Tiered by effort × payoff. "Local" =
data/tooling already on disk from the audit.

---

## Tier 0 — DONE (rigor + corrections, already committed)
Definitions; explicit-reference scoping + property-path quantification; size-controlled
rarefaction; Table 2 `#Valid` correction; federated 3→22 fix; types-only note;
robotic-classification fix; parser-robustness; Figs 6/8 on log axes; canonical TSE lists;
full reproducibility audit (Tables 2–5 reproduce from source). These answer the reviewers'
*surface* critiques. They do not, by themselves, add a thesis.

---

## Tier 1 — cheap, high-impact, all data LOCAL (do first)

| # | Analysis | Strengthens | Data | Effort |
|---|---|---|---|---|
| 1 | **Content supply-vs-demand mismatch** (the headline new analysis) | C1, C3, C5 → turns descriptive stats into actionable insight | Wikidata: instances/class from dumps (P31 tally); Bio2RDF: COUNT/class from endpoint. Demand = used-element CSVs (local) | M |
| 2 | **Example-query contamination filter** (WDQS example set) | C2, C5 (organic = human intent) | WDQS example queries (public) matched against organic logs (local) | S |
| 3 | **Stable-core utility curve** (cumulative query-volume coverage; Gini/Lorenz) | C5 (make "core" concrete + useful) | used-element CSVs (local) | S |
| 4 | **Power-law / distribution fit** (exponents per KG×type) | C3 (quantify, not "sharp decline") | used-element CSVs (local) | S |
| 5 | **Instantiated vs class-like split** (P31-object vs P279-only) | R2-1.1 (Wikidata "class" validity) | one dump re-scan (local) | M |

**Analysis #1 in detail (most important).** For each KG, place every schema element on
two axes: *demand* (normalized query frequency) vs *supply* (instances per class /
triples per predicate). Four quadrants → the actionable output:
- **high demand / low supply** = enrichment priorities (users want it, KG is thin);
- **high supply / low demand** = deprioritize-for-docs / deprecation candidates;
- **high/high** = the genuine core;
- **low/low** = the long tail.
This is the "where KG content and query demand mismatch" story that would make the paper
citable, and it directly cashes the abstract's promise ("highlights underused elements …
guidance for documentation, schema design").

---

## Tier 2 — medium effort, NEW data (raises generality + temporal claims)

| # | Analysis | Strengthens | New data | Effort |
|---|---|---|---|---|
| 6 | **Add a 3rd KG (DBpedia)** via LSQ logs | external validity (currently n=2 KGs) | LSQ 2.0 endpoint (we already use it) + DBpedia schema | M–L |
| 7 | **Equal-length time windows + ≥3 intervals** (Wikidata) | C4 (disentangle interval-length from KG; real trend) | more Wikidata Dresden intervals (downloadable; we have the URLs) | M |
| 8 | **Closure-based "effective usage"** for path queries | R2-1.2 (the `P279*` concern) | Wikidata dumps (local) — expand P31/P279* and property paths | M |
| 9 | **Volume-weighted coverage** (non-deduplicated) alongside unique | R2-3d | raw logs (local) | S |

Note on #6: a third KG of *intermediate* scale/domain (DBpedia) tests whether the
KG-dependent breadth result (C2) and the coverage metric behave as the two-KG story
predicts, instead of being a Bio2RDF-vs-Wikidata artifact. This is the strongest single
move for generalizability.

---

## Tier 3 — expensive / reframe (the "point" of the paper)

| # | Action | Why |
|---|---|---|
| 10 | **Reframe the narrative** (see below) | the current coverage-metric framing buries the novel results |
| 11 | **Utility demonstration** | the only way to fully cash C1/C5: build + evaluate a documentation/autocomplete prioritization driven by the core, report the win |

### Proposed reframed narrative
Move from "we propose a coverage metric and describe distributions" to a thesis-driven arc:

> **Thesis:** *Query logs reveal a large, structured gap between what a KG contains and
> what users actually query — and this gap differs systematically between human and
> machine usage and between KGs of different scale.*

1. **Setup:** usage metadata from logs; explicit-reference coverage as the instrument.
2. **Finding 1 (behavioral):** organic vs robotic differ not just in volume but in
   *kind* — size-controlled breadth (rarefaction, KG-dependent) **and** syntactic
   cleanliness / Virtuoso-extension use (C2 + C7). *This is the lead result.*
3. **Finding 2 (content):** supply-vs-demand mismatch (Tier-1 #1) — concrete enrichment
   and deprecation candidates per KG.
4. **Finding 3 (temporal/structural):** stable core + federation growth, properly
   controlled (C4, C5, C6).
5. **Utility:** the core/coverage drives a documentation-prioritization recommendation,
   evaluated (Tier-3 #11).

Coverage % becomes supporting evidence, not the hero.

---

## Recommended sequence
1. **Tier-1 #1 (supply-vs-demand)** — prototype on Wikidata first (dumps local) to see if
   it yields a real story before investing further. *Highest leverage.*
2. **Tier-1 #2, #3, #4** — quick wins that harden C2/C3/C5 (a day's work, all local).
3. **Decide on reframe (Tier-3 #10)** once #1 confirms there's a content story.
4. **Tier-2 #6 (DBpedia)** if generality is the gating reviewer concern.
5. **Tier-1 #5, Tier-2 #8** to fully close R2-1.1 / R2-1.2.
6. **Tier-3 #11 (utility)** last — biggest effort, biggest payoff for the "so what."

## Decision points (need author input)
- Venue/ambition: aim to satisfy *Semantic Web* journal (needs Tier 1–3), or settle for a
  strong major-revision resubmission (Tier 1 + reframe)?
- Appetite for a 3rd KG (DBpedia) — meaningful new data work but the best generality lever.
- Whether a utility/evaluation (Tier-3 #11) is in scope or deferred to future work.
