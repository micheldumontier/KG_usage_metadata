# Response to Maryam's fourth review (inline `\begin{comment}` blocks, `paper/main` 4a2e09a)

**Status: all 15 comments closed, including [1]/[5]'s repo-reorganization half.** This file was
originally written while comments [8] and [13] were still mid-flight, and [1]/[5]'s
per-analysis-README pass was deferred until they closed; all of that is now done. Sections below
were revised in place rather than left as stale in-progress notes — same treatment
`RESPONSE_TO_REVIEW3.md` got after its round finished. The repo-reorg work itself (READMEs
added, superseded scripts marked obsolete, several real bugs found and fixed along the way) is
logged in detail in `CLAUDE.md` and `generated-usage-metadata/README.md` rather than duplicated
here in full.

This round differs in character from the last one. Round 3 was mostly about finding defects
in the existing pipeline. This round is more about **reconciling code, data, and the
manuscript's own stated definitions** — a genuine Wikidata schema-definition choice, a
subsection removed because two architectures had been silently conflated as one comparison,
and a run of comments that looked blocked on unavailable co-author data but, once actually
traced through the code, turned out to need far less than assumed.

Comments are numbered in the order they appear in the source.

---

## Summary of what changed

| | before | after |
|---|---|---|
| Wikidata predicate definition | Bio2RDF-style restricted (class–predicate–class join) | **native** (`wdt:P` namespace directly) — author decision |
| Wikidata TSE 2017 (types/preds/total) | 103,380 / 934 / 104,314 | **103,355 / 931 / 104,286** |
| Wikidata TSE 2018 (types/preds/total) | 97,470 / 992 / 98,462 | **97,445 / 991 / 98,436** |
| Temporal-table TSE caption | 104,289 (mismatched Table 3) | **104,286** (now consistent) |
| Bio2RDF `*_vocabulary:Resource` | excluded in release extractor only, not in the live/2019 extractor's code | excluded in **both** (already Resource-free in committed data; code now matches) |
| Bio2RDF rarefaction denominator (`rarefaction_ci.py`) | 545 (stale) | **541** |
| Rarefaction Bio2RDF/Wikidata claim | "neither shows a robotic breadth advantage" | per-KG: Bio2RDF fully removed, **Wikidata retains a small real residual** |
| Rarefaction Wikidata curve (Fig. 5) shape | described as "organic richer at lower effort" | **crosses twice**: organic substantially richer across most of the range, robotic ahead only right at the common effort |
| Pairwise Schema Type Usage of Bio2RDF | "3→22, ~sevenfold increase" | **removed** — method couldn't separate a real usage question from the 2013→2019 architecture shift |
| Schema-usage-graph visualization (Fig. 6/11) | standalone paragraph, no positioning | moved into Utility subsection, **positioned against Bonifati et al.'s sunburst** |
| Adoption subsection | "...Newly Introduced Schema Elements" (predicates only) | retitled **"...Predicates"**, scope explained |
| Figure 6 (`fig:l6`) panel axes | independently auto-scaled | **shared within each KG** |
| DBpedia class-position | 675/47 (93.5%/6.5%) | **682/40 (94.5%/5.5%)** |
| Wikidata organic-2017 class-position | 8,968/3,805 (70.2%/29.8%) | **9,286/3,487 (72.7%/27.3%)** |
| Wikidata robotic-2017 class-position | 54,534/4,155 (92.9%/7.1%) | **55,698/2,991 (94.9%/5.1%)** |
| Predicate utility ranking (top-10 nDCG/cov) | 85.9%/58.6% usage, 43.3%/23.0% cov | **76.4%/62.5% usage, 35.8%/26.8% cov** |
| Predicate utility ranking MRR ratio | 1.3× | **1.1×** |
| `wd_closure_anchor_queries.tsv` | missing from the repo | **added**, verified exact match to published closure numbers |

---

## Point-by-point

### [1] Bio2RDF pipeline traceability — dev branch mixes old and new logic
**Resolved (2026-09-24), along with [5]'s repo-organization half.** The specific example you
gave — `bio2rdf2013_organic_coverage.py` printing a stale pre-correction comparison — was fixed
directly (updated to the current canonical 113/541=20.89%; 525/541=97.04%, from the previous
116/545; 529/545). More generally: every analysis in the manuscript's Results section now has a
README stating its authoritative script(s), inputs, intermediate files, and which table/figure
it produces (model: `generated-usage-metadata/wdqs-examples/README.md`, as you suggested).
Superseded scripts and files (`schema_generator_wikidata.py`,
`schema_gnrator_Bio2RDF_simpler_queries.py`, two stale data files, and one outdated validation
summary) are moved to a single top-level `archive/`, per your "make clear which is current" ask,
rather than left scattered through the live tree or discarded. Full detail in `CLAUDE.md`'s
repo-reconstruction section and `generated-usage-metadata/README.md`.

Doing this pass thoroughly (actually re-running scripts rather than just reading them) also
surfaced several real, previously-unknown bugs, all now fixed: a stale pre-Resource-exclusion
TSE denominator hardcoded in `concentration_metrics.py` (caused small errors in Table 12's
full-universe Gini/evenness columns), and two separate Windows-only portability bugs
(`csv.field_size_limit` overflow and a missing UTF-8 encoding on worker-output reads) that
between them affected 15 scripts — none had ever been run on Windows before, since they'd
always been run on your server.

### [2] Predicate definition drift — newer Wikidata extractor doesn't match the class–predicate–class pseudocode
**This was correct, and traced to its root: two independent extraction pipelines exist.**
Your original `schema_generator_wikidata.py` (used for the paper's original submission)
implements the restricted join exactly as the pseudocode describes. `wd_schema_extract.py`
(added later, for the class-vs-value/supply-demand reframing) takes every `wdt:P`-namespace
predicate directly, with no join restriction — confirmed by reading its code, not inferred.

**Resolved as an author decision, not a bug fix: Wikidata now uses its native definition.**
Every current Wikidata analysis script already read from the newer, unrestricted extractor's
output before this decision was even made, so the downstream pipeline didn't need to change
— only the manuscript's methodology text and Table 3's counts needed to catch up to what the
code was already doing. Bio2RDF keeps the restricted join (needed there specifically to
exclude foreign W3C vocabulary that would otherwise enter via meta-statements, per round 3's
D1). The methods section (§1 terminology, the Listing 2 pseudocode intro, and a new
paragraph after the Bio2RDF/Wikidata properties paragraph) now states this asymmetry
explicitly, and explains why it's principled rather than arbitrary: Wikidata's P-namespace
is already disjoint from its item space the way Bio2RDF's vocabulary isn't, so the join
Bio2RDF needs to stay in-vocabulary is unnecessary for Wikidata.

### [3] Which script actually produced Table 2's Wikidata counts?
**Resolved together with [2].** Table 3 now reports 103,355/931/104,286 (2017) and
97,445/991/98,436 (2018) — the newer extractor's actual output, matching what every
downstream analysis already used.

### [4] Rarefaction: interpretation, figure/table caption, denominator consistency, sampling density
**All four parts addressed, one of them uncovering more than expected.**

*Wording.* "Neither shows a robotic breadth advantage at equal effort" contradicted the same
paragraph's own numbers two sentences later (Wikidata's 1.03× has a 95% CI of [1.02, 1.05],
which excludes 1). Reworded to state the real asymmetry: Bio2RDF's advantage is fully
removed, Wikidata's is substantially reduced but leaves a small, real residual.

*Denominator.* Confirmed real: `rarefaction_ci.py` hardcoded Bio2RDF's TSE as 545;
`rarefaction_size_control.py` already had 541 correct. Fixed both scripts (and updated
Wikidata's denominator in both from the pre-fix 104,314 to 104,286 while there). The
published ratios/CIs don't depend on this constant at all — it only affects displayed
percentages — and rerunning confirmed the corrected constant reproduces the already-published
Bio2RDF percentages exactly (18.4%, 20.9%).

*A reproducibility finding surfaced while verifying that fix, not a data or code bug:*
rerunning `rarefaction_ci.py` with identical script, data, and seed reproduced Bio2RDF's
ratio and conclusion but not its exact CI bounds (`[0.73, 1.03]` here vs. the published
`[0.75, 1.02]`) — traced to `numpy.random.Generator.choice(replace=False)`'s sampling
algorithm differing across numpy versions despite a fixed seed. Documented in
`REPRODUCIBILITY.md`'s environment section; the manuscript's originally-published CI is left
as-is, since neither figure is wrong and the conclusion is identical either way.

*Figure caption vs. table.* The caption claimed one direction ("organic queries showing
slightly greater richness... at the common effort") for both KGs; the table shows Bio2RDF
organic ahead but Wikidata robotic (very slightly) ahead at that point. Rewritten per-KG.

*Sampling density — and what it revealed.* The rarefaction curves were evaluated at 40
**linearly**-spaced points but plotted on a log axis, so the low-effort region — exactly
where the text makes claims — was represented by almost no points. Switched to
`np.geomspace`. This didn't just improve the plot: it revealed that Wikidata's organic and
robotic curves actually **cross twice** — robotic negligibly ahead only at the very lowest
effort, organic substantially ahead (up to +3,400 elements) across nearly the entire
middle-to-upper range, then robotic overtakes again only in the final approach to the common
effort. The previous "organic richer at lower effort" text understated both the magnitude
and the extent; both the caption and the Discussion sentence are corrected to describe the
double crossover.

*Repo-organization ask in the same comment block* — folded into the deferred [1]/[5] pass.

### [5] `KG-Schema-extractors/` reorg + Bio2RDF `Resource`-class exclusion inconsistency
**The specific consistency issue is resolved; the general reorg ask is deferred.**

Confirmed from code: `bio2rdf_release_schema.py` excludes `*_vocabulary:Resource` types;
`schema_gnrator_Bio2RDF.py` (the live/2019-era extractor) did not. But the
**already-committed canonical schema files were already Resource-free** — verified by
direct grep, zero `:Resource` entries in either the 17- or 26-subgraph type lists — so no
manuscript number needed to change. Fixed `schema_gnrator_Bio2RDF.py`'s filter to match the
release extractor explicitly, so the code's logic now matches what its output already was.

While tracing this, found something not previously visible: **the assembly step that turns
`schema_gnrator_Bio2RDF.py`'s raw output into the canonical
`generated-usage-metadata/bio2rdf-schema/` files didn't exist anywhere in the repo.** Added
`KG-Schema-extractors/build_bio2rdf_canonical_schema.py` to reconstruct and document it, with
a full explanation of why object-position types (`Class2` in the raw relationship file) don't
need separately unioning in — they're provably already a subset of what the subject-position
collection captures, given how the extractor's two queries are structured. The 17-subgraph
subset file's exact derivation rule remains unconfirmed (a prefix-based hypothesis matches
predicates exactly but types off by one) and is explicitly flagged as unresolved rather than
guessed at.

The general repo-organization ask (dedicated READMEs, removing obsolete scripts) is deferred
with [1].

### [6] Figure placement — the schema-usage-graph visualization feels abrupt where it sits
**Accepted and moved, with an honest novelty check first.** Before moving it, checked whether
this is actually a novel contribution worth promoting into the Utility subsection at all —
it isn't, on its own: Bonifati et al. (already cited elsewhere in this paper) built an
"interactive property sunburst" for Wikidata predicates using the same underlying idea
(visualize schema elements sized by query-usage frequency). Moved the figure into the
retitled "Utility: Downstream Applications of Usage Metadata" subsection as a second,
qualitative example alongside the quantitative ranking demonstration, with a sentence
positioning it honestly against Bonifati et al. rather than implying novelty: this extends
their predicates-only, Wikidata-only, sunburst approach to a joint type+predicate view on a
different (OWL-style) KG, not a new technique.

### [7] Pairwise Schema Type Usage of Bio2RDF — 2013 vs. 2019 may not be comparable
**Accepted, and confirmed with direct evidence before deciding — removed rather than
revised.** You were right that the 2013 architecture (separate per-dataset endpoints) could
mean federation happened via `SERVICE`, invisible to a method that only detects ordinary
cross-subgraph joins in a single query's triple patterns. Checked directly against the
organic-2013 log already in the repo: **4,496 of 116,385 organic queries contain a `SERVICE`
clause**, and the overwhelming majority target Bio2RDF subgraph-specific endpoints
(`cu.gene.bio2rdf.org`, `cu.pharmgkb.bio2rdf.org`, `cu.drugbank.bio2rdf.org`, and dozens
more) — not external services. This confirms the "3 in 2013 → 22 in 2019, ~sevenfold
increase" comparison conflated a real usage question with the 2013→2019 architectural shift
(separate endpoints → unified endpoint), which the triple-pattern-only method structurally
cannot see.

Decision: remove rather than revise. A correct revision would need a new
`SERVICE`-endpoint-to-subgraph mapping analysis over the *full* (not just organic) 2013 log,
which isn't available locally, and the underlying "did cross-dataset federation increase"
question is peripheral to the paper's main contributions. Removed the subsection, its figure,
and a second, independent echo of the same claim in the Discussion section (a paragraph
drawing the identical "unified endpoint" causal narrative). `REPRODUCIBILITY.md`'s figure
table renumbered accordingly (1–11, was 1–12) — this also caught that it was already stale
from [6]'s figure move, independently of this removal. The now-orphaned
`Bio2RDF-federated-querying/` notebooks and their outputs are left in place, flagged for the
deferred [1]/[5] pass rather than removed now.

### [8] Class-position definition incomplete — subject of P279/`rdfs:subClassOf` should count too
**Resolved. DBpedia and Wikidata (organic + robotic) halves done, verified, and reflected in the manuscript.**

The fix itself needed no KG dump or ontology data — it's a property of how an entity appears
*within the query text*, not an external lookup. `P279`/`rdfs:subClassOf` relate two classes
(unlike `P31`/`rdf:type`, whose subject is an instance), so the subject of a subclass triple
is definitionally a class too. Fixed both parsing workers (`classvalue_worker.js` for
Wikidata, `classvalue_worker_dbo.js` for DBpedia) to also count subject-of-subclass as
class-position, and verified the fix does *not* pick up `P31`/`rdf:type` subjects (those
stayed correctly excluded).

**DBpedia** (run via a new LSQ 2.0 extraction script, `dbpedia_lsq_extract.py`, since the
existing extraction relied on an ORDER-BY-based pagination approach that turned out to be a
hard dead end on this Virtuoso instance — it caps sorted `LIMIT`/`OFFSET` at 10,000 rows
combined, found empirically): 722 `dbo:` classes referenced (unchanged, same universe);
class-position 675→**682** (93.5%→**94.5%**), value-only 47→**40** (6.5%→**5.5%**). Exactly
7 classes shifted, both ways consistent. Doesn't change the manuscript's qualitative claim —
if anything reinforces it, since the corrected value-only fraction is even closer to Bio2RDF's
near-zero.

**Wikidata organic-2017**: used types 12,773 (unchanged); class-position 8,968→**9,286**
(70.2%→**72.7%**), value-only 3,805→**3,487** (29.8%→**27.3%**) — a larger shift (318 types,
+2.5 points) than DBpedia's, consistent with Wikidata organic queries doing substantially
more subclass-hierarchy navigation (the closure analysis for [14] independently found 1,276
distinct `P279*`-anchored organic-2017 queries). Demand-weighted (KG-schema types only):
90.7%→**90.9%** — barely moves, as expected, since a handful of very-high-volume elements
dominate that view.

**Wikidata robotic-2017: re-downloaded and rerun successfully.** The original attempt at the
2.7 GB `int1_2017_all.tsv.gz` was truncated (`EOFError: Compressed file ended before the
end-of-stream marker`) — a data-integrity issue, not a code problem; the clean re-download
reproduced the same query counts already published in Table 2 (8,234,089 unique queries),
confirming it's the same dataset. Used types 58,689 (unchanged, same universe); class-position
54,534→**55,698** (92.9%→**94.9%**), value-only 4,155→**2,991** (7.1%→**5.1%**) — 1,164 types
shifted, both ways consistent. A smaller shift than organic's (+2.0 points vs organic's +2.5),
consistent with organic queries doing more subclass-hierarchy navigation. Demand-weighted (KG-
schema types only): 61.3%→**61.5%** — barely moves, same as organic's +0.2-point shift, for the
same reason (a handful of very-high-volume elements dominate that view either way).

The set-level contrast the manuscript draws (robotic more class-oriented by count, organic more
class-oriented by volume) survives unchanged in direction and magnitude: set-level gap 22.7→22.2
points, volume-weighted inversion ~29 points either way. Only the specific percentages needed
correcting, not the argument. Manuscript updated: Table 9 (`tab:classvalue`), Table
`tab:generality`, and the §sec:classvalue prose (both rows' percentages, the demand-weighted
reference counts, and the two derived shares — organic/robotic value-only-by-elements and
value-position-by-volume).

### [9] Figure 9 (now Figure 7 after [7]'s removal) — shared axis scales within each KG
**Accepted and implemented as specified.** `regenerate_figures.py` now computes shared x/y
limits per KG (Bio2RDF: panels A–D; Wikidata: E,F,G,H,L,M — kept separate from each other, as
you asked) before saving. Verified visually: log-scaled axes keep each panel's own curve
shape visible even when its data occupies a small fraction of the shared range, so sharing
the axes makes the magnitude gap between e.g. organic and robotic panels immediately visible
rather than something a reader has to read off tick labels. Caption updated to say so
explicitly. Also found and fixed a second, independent stale pair of Wikidata TSE numbers
(104,314/98,462 → 104,286/98,436) in the paragraph introducing this figure — missed during
[2]/[3]'s fix, caught while reviewing this one.

### [10] Adoption subsection title implies both types and predicates; only predicates are analyzed
**Accepted, and explained rather than extended.** Retitled to "Adoption of Newly Introduced
Predicates." Added a sentence explaining *why* the scope is predicate-only: the recency proxy
relies on Wikidata's sequential, property-only identifier namespace (`P`-numbers); item
identifiers (`Q`-numbers) are shared by all Wikidata entities, not only those used as types,
so a type's absence from the 2017 extraction can't be distinguished from an existing item
simply not yet used as a type — there's no type-side equivalent of the `P`-number recency
check. Extending the analysis to types would produce a number that looks parallel to the
predicate one but means something structurally weaker, so it wasn't attempted.

### [11] TSE mismatch — temporal-table caption says 104,289, Table 2 says 104,314
**Resolved as a consequence of [2]/[3].** Both were stale relative to the corrected Wikidata
schema. The temporal-table caption now reads 104,286, consistent with Table 3 and with the
concentration table (which, it turned out, already had the correct 104,286 independently —
confirming the caption was the outlier, not Table 3).

### [12] Temporal analysis — "consecutive" windows have a gap; intersection-only basis; overstated coverage claim
**All three addressed.** Confirmed the gap is real: window 3 ends 2017-09-03, window 4
begins 2017-12-03. "Consecutive" → "successive" everywhere it described the seven analyzed
windows (four locations: the methods intro, the table caption, and — found while checking —
two more echoes in the Discussion and Conclusion). Confirmed from `wd_temporal.py`'s code
(`set(a)&set(b)` for both the Spearman and Wilcoxon computations) that both statistics are
computed over the intersection of types common to each compared window pair, not the full
fixed 2017 universe the subsection's opening sentence implies; made this explicit at the
point each statistic is introduced rather than leaving it to the "paired types" phrasing
later in the paragraph. Softened "more queries in a window do not expand coverage" to your
suggested descriptive wording.

### [13] Candidate-universe mismatch in the type/predicate ranking experiments
**Resolved — code fixed and rerun with real data; manuscript updated.** Confirmed the concern precisely: the
usage ranking is built only from elements observed in the 2017 training logs, while the
supply ranking is built from whatever the supply CSV lists — and for predicates specifically,
that CSV (`triples_per_pred_2017.csv`, 3,668 entries) is actually **larger** than the
930-predicate schema itself, since it isn't restricted to the `wdt:P`-direct namespace the
schema definition uses. So the mismatch runs in both directions for predicates, not just the
one direction the comment described.

Fix implemented in both `wd_utility_ranking.py` and `wd_utility_predicates.py`: both rankings
are now aligned to the actual 2017 schema universe (`types_2017.txt`/`preds_2017.txt`) —
usage is extended with zero-usage entries for schema elements never observed in training,
and supply is restricted to schema elements only (dropping predicates outside the `wdt:P`
namespace). Chose this direction (extend usage, restrict supply) rather than the comment's
alternative (restrict supply to observed-only) because the supply/content baseline is
explicitly framed in the manuscript as computed "without using query-log information" —
restricting it to observed-in-logs elements would quietly contradict that. Also addressed the
companion point (top-1000 for a 934-predicate — now 930-predicate — schema is redundant past
saturation): the predicate table's reported k-values now end at the actual schema size
instead of a fixed 1000.

**Rerun on the server (2026-09-24), using the same organic TRAIN/TEST files as [8]'s Wikidata
half.** The two experiments were affected very differently by the fix, which itself confirms
the diagnosis above.

**Types** (`wd_utility_ranking.py`): candidate universe (103,355 types) is far larger than any
evaluated $k$ (max 1,000), so the fix barely moved anything — only usage-side coverage/nDCG at
$k$=100/500/1000 shifted by 0.1–0.3 points (e.g. top-1000 coverage 79.9%→**80.2%**, nDCG@1000
92.5%→**92.6%**); supply-side and $k$=10/50 are bit-for-bit unchanged. MRR: 0.338/0.117/2.9×
→ 0.3384/0.1172/2.9× — unchanged. No argument in the manuscript needed to change here, only
cosmetic table/prose touch-ups.

**Predicates** (`wd_utility_predicates.py`): a much bigger shift, because the pre-fix supply
side used the unrestricted `triples_per_pred_2017.csv` (3,668 entries) rather than the
931-predicate schema. Coverage at top-10: 43.3%/23.0% → **35.8%/26.8%**; nDCG@10: 85.9%/58.6%
→ **76.4%/62.5%**; MRR: 0.258/0.202/1.3× → **0.227/0.200/1.1×**. The table's max-$k$ row is
now 931 (schema size, computed dynamically) instead of a fixed 1000, and at that row usage and
supply coverage are now **exactly equal (51.3% = 51.3%)** — precisely the check you proposed
(a top-$k$ cutoff that already includes every candidate must give identical coverage), which
the pre-fix numbers (94.8% vs 93.3% at $k$=1000) never actually satisfied. That equality is a
mechanical consequence of both rankings including the full schema at $k$=931, not itself
evidence about ranking quality — the manuscript's revised prose says so explicitly.

More substantively, coverage now saturates at only ~51%, not ~94%, once the full schema is
included, because roughly half of predicate references in the query logs use something other
than the `wdt:P`-namespace predicates that define the schema (the Method section's predicate-
identification paragraph) — statement/qualifier predicates, general RDF vocabulary, etc. —
which are structurally uncoverable by a schema-restricted ranking regardless of method. This is
the predicate-side counterpart of the class/value-position issue from comment [8]'s section.
The manuscript's "predicate suggestion" paragraph and its explanatory paragraph were both
rewritten to reflect this — the
old explanation ("a content-ranked predicate list runs out of room to be wrong... reaches most
of the demand within a few hundred suggestions") was itself an artifact of the unrestricted,
buggy supply candidate set and is no longer accurate.

The qualitative conclusion survives — usage-based ranking still wins, especially at low $k$,
with a narrower margin than for types — but every quantitative claim in that paragraph and
Table `tab:predranking` needed correcting, not just small rounding. Run logs saved to
`analysis-results/wikidata-utility/`.

### [14] Missing `wd_closure_anchor_queries.tsv` artifact
**Resolved — regenerated locally, not obtained from the co-author, and cheaper than the
initial assessment suggested.** Tracing the two scripts involved found the actual data
footprint was much smaller than "the full raw logs + the full dump": `wd_p279_edges.py`
needs only the **2017** Wikidata dump (not 2018), and `wd_closure_queries.py` needs only
**one** log file (`int1_2017_organic.tsv.gz`), not the full log collection — provided it's
run at the correct default scope, not the `"pooled"` option (which reproduces the exact
scope bug round 3 already fixed).

Downloaded the 2017 dump (21 GB) and that one log file, ran both scripts. `wd_p279_edges.py`
took about 7 hours (scanning 4,011,697,996 decompressed lines — the dump's gzip compression
ratio was much higher than the compressed size alone suggested). Output verified against the
published closure numbers, all matching exactly: 1,276 distinct anchors, `Q35120` → 12
queries (not 13 — the pre-round-3-fix count), 62,410 additional classes credited by the
closure, 62.8%/62.2% closure share against the class universe/TSE. Both requested files
committed to `analysis-results/wikidata-closure/`.

### [15] Confirm the D2 `parallel()` ordering fix propagated across all three KGs
**Resolved, with one precision the blanket "yes, fixed everywhere" framing would have
missed.** Audited every `parallel()`-style worker function by finding all *definitions*
(not just call sites, so a copy-pasted variant with the old bug wouldn't be missed) across
14 scripts spanning Bio2RDF, Wikidata, and DBpedia, plus the older
`Bio2RDF-federated-querying/` notebooks (2013/2019). 11 scripts use the corrected
index-based reassembly; 1 (`template_linkage.py`) uses a different but equally correct
explicit-index approach; 2 (`wd_coverage.py`, `bio2rdf_coverage_vs_schema.py`) still
concatenate without reordering — but tracing what each does with its output confirmed
neither ever re-pairs a result with its originating query by position or occurrence count,
so they were never exposed to the bug in the first place (pure set-based tallying, the
category round 3's own D2 write-up already identified as unaffected). The two federated-
querying notebooks have no parallelism at all — sequential pandas/dict processing — so the
question doesn't apply to them by construction, not because of any fix.

---

## Also corrected while working through the above

- **A real Windows portability bug**, unrelated to any single comment: `csv.field_size_limit(sys.maxsize)`
  in the shared `sparql_log_preprocess.py` overflows Windows' 32-bit C `long`, crashing on
  import before any pipeline logic runs — found while setting up a Windows environment from
  scratch to reproduce [14] locally. Affects every script that imports this module, not just
  the one being run at the time. Fixed with `min(sys.maxsize, 2**31-1)`.
- **A Virtuoso pagination limit**, found building the DBpedia extraction script for [8]:
  the LSQ 2.0 endpoint hard-rejects `ORDER BY` combined with `LIMIT`/`OFFSET` past 10,000 rows
  combined ("Sorted TOP clause... Only 10000 are allowed"), undocumented anywhere. Worked
  around with plain unsorted pagination instead.

---

## Everything closed — minor loose ends only

All 15 comments are resolved, including [1]/[5]'s repo-organization half (per-analysis READMEs
added throughout `generated-usage-metadata/`, superseded scripts marked obsolete in place, the
17-subgraph canonical schema file's derivation recovered and documented — see
`KG-Schema-extractors/build_bio2rdf_canonical_schema.py`'s docstring for that one specifically).

Two small things remain, neither blocking anything:
1. `KG-Usage-analysis/usage_pattern_analysis.ipynb` (the likely source of the Spearman/Wilcoxon
   rank-correlation numbers in §sec:concentration's prose) hasn't been independently re-run to
   confirm those exact figures this session — flagged, not verified.
2. `REPRODUCIBILITY.md`'s table/figure mapping doesn't yet credit that notebook for those
   specific prose statistics, a gap worth closing once (1) is confirmed.
