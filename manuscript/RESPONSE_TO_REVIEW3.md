# Response to Maryam's second review (inline `\begin{comment}` blocks, `paper/main` b36ddc9)

Thank you. Delivering the comments inline in `main.tex` worked far better than the sidebar
did last round, and it is worth saying why beyond convenience: **three of the nine comments
led to four defects that were not visible from the text at all, and three of them had
silently changed published numbers.** Two headline results reversed as a result. The details are below;
the short version is that the paper is now more defensible and slightly less dramatic.

Comments are numbered in the order they appear in the source.

---

## Summary of what changed

| | before | after |
|---|---|---|
| Bio2RDF TSE (26 subgraphs) | 545 | **541** |
| Bio2RDF TSE (17 subgraphs) | 399 | **395** |
| Bio2RDF equal-effort ratio | 1.80×, CI [1.64, 1.97] | **0.88×, CI [0.75, 1.02]** |
| organic-2019 coverage | 21.28% | 20.89% |
| robotic / all-2019 coverage | 97.06% | 97.04% |
| all-2013 coverage | 79.44% | 79.24% |
| Bio2RDF-organic-2019 Gini | 0.901 | **0.662** |
| 2013-era organic coverage | 53.6% | 53.4% |
| 2013 vs 2019 equal-effort | 1.58× | 1.28× |
| Bio2RDF adoption claim | "growth outruns adoption" | **withdrawn** (retirement artifact) |
| DBpedia class-demand core | …, Company, … | Place, **Airport**, Person, … |
| consecutive-window Spearman | ρ = 0.47–0.51 | **0.52–0.59** (endpoint 0.44 → 0.43) |
| Wilcoxon, adjacent windows | "not significant for most" | **5 of 6 significant**; claim withdrawn |
| persistent top-50 core | 14 types | **15**, membership changed |
| volume-weighted class position | "~27–29%" | **organic 90.7%, robotic 61.3%** |

The build is clean throughout: 37 pages, no errors, no undefined references or citations.

---

## The four defects

### D1. `rdf:type` in the Bio2RDF schema (your comment [3])

You asked whether `rdf:type` should count as a Bio2RDF schema element, given the template
defined in §3.2. It should not, and the problem is broader than that one term.

**Root cause.** `schema_gnrator_Bio2RDF.py` applies the template filter to types (line 102,
`if "_vocabulary" in stype`) but writes the predicate out unchecked (line 122). Types were
350/350 conforming; predicates only 191/195. The extraction pattern
`?s rdf:type <stype> . ?s ?p ?o . ?o rdf:type ?otype` binds `?p` to `rdf:type` whenever a
resource carries two types, and the relationship file holds **1,559** such rows, e.g.
`sgd_vocabulary:Resource , rdf:type , owl:Class`. Those are statements *about* the
vocabulary. Four W3C terms entered this way: `rdf:type`, `rdfs:subClassOf`, `owl:sameAs`,
`owl:sourceIndividual`.

**Why we removed them rather than redefining the schema.** Three reasons, in order of
weight. Bio2RDF was the only one of the three KGs carrying foreign vocabulary — Wikidata's
930 predicates are all P-numbers and DBpedia's 3,024 are all DBpedia terms — so the cross-KG
comparison that the paper is built on was not on a common footing. They are also not
elements Bio2RDF's maintainers can document, redesign or deprecate, which are precisely the
decisions this measurement exists to inform. (Wikidata's `P31`/`P279` stay, and that is the
same rule applied consistently: those are Wikidata's own properties.) And `rdf:type` is the
worst possible member of an abundance vector for rarefaction, being near-universal and
hugely abundant while adding almost nothing to richness.

**Consequence.** Coverage barely moves. The rarefaction result does not: `rdf:type` was
**74.2%** of the organic log's occurrences against **29.3%** of the robotic log's, inflating
organic sampling effort roughly fourfold (4,855 → 1,220) while adding one element to
richness. The Bio2RDF equal-effort ratio falls from **1.80×** to **0.88×, 95% CI
[0.75, 1.02]** — an interval containing 1.

**This improves the paper.** Previously it had to report a "KG-dependent" outcome: a genuine
robotic advantage on Bio2RDF, none on Wikidata. Now neither KG shows one (0.88× and 1.03×),
and the finding collapses into a single well-supported statement: *the raw organic/robotic
coverage gap chiefly reflects query volume; control for effort before reading it as
behavioural.* That also retires the n=2 generalisation you objected to in the first round.

You suggested deleting the caveat built around the `rdf:type` counts. We agree it had to go,
but deleting it alone would have left the underlying inclusion in place; the caveat was a
symptom. It is gone because the element is.

*One consequence worth flagging.* Concentration moved sharply for the sparsest log:
Bio2RDF-organic-2019 Gini **0.901 → 0.662**, P80 **4.31% → 27.43%**. That breaks the former
"Gini above 0.90 in every dataset" claim. Rather than widen the range quietly, §4.9.2 now
treats it as an instructive exception: with only 113 of 541 elements touched, a low
used-element Gini signals a *narrow log*, not even demand — and the full-universe Gini\*
returns to 0.930 once untouched elements enter as zeros.

### D2. Result misordering in the parallel workers (your comment [9.5])

You suggested testing whether worker output order matches query order in
`dbpedia_analysis.py`. It does not.

`chunks = [prepped[i::nw] for i in range(nw)]` partitions with a stride, but results are
concatenated in chunk order, so element *k* of the output is not element *k* of the input.
In a 40-item reproduction, **39 of 40 positions are misaligned**. Every later
`zip(queries, results)` therefore pairs the wrong query with the wrong parse.

Five scripts dereference `q` inside that loop and were affected: `dbpedia_analysis`,
`bio2rdf2013_organic_coverage`, `wd_classvalue`, `wd_temporal`, and our own
`wd_closure_queries`. In each, `c = seen[q]` attached an execution count to another query's
schema elements. Set-based results are unaffected; only count-weighted ones. Note that
`wd_coverage.py` already carried a comment observing the striding and judging it harmless
*there*, which was correct but never propagated to the callers where alignment matters.

`parallel()` now reassembles by original index in all ten scripts. The re-run gives a clean
confirmation of the predicted signature: DBpedia's set-based figures reproduce **exactly**
(722 `dbo:` classes referenced, 675 / 93.5% in class position, 47 / 6.5% value-only, same
rich-but-unqueried list) while the count-weighted class-demand ranking **changed**. The
manuscript's DBpedia core is corrected to *Place, Airport, Person, MusicalArtist,
PopulatedPlace, Film*: **Company** does not survive correction and **Airport**, second by
demand, had been missing. The same signature appeared in the closure artifact — anchor
counts identical, query texts different.

### D3. The adoption result was a retirement artifact (surfaced by your comment [6])

You asked why the adoption analysis covers only predicates. It can cover types, so we ran
it — and the answer disqualifies the Bio2RDF comparison rather than extending it. See [6].

---

### D4. The volume-weighted class/value contrast was inverted (found while re-running for D2)

Re-running `wd_classvalue` to check D2 confirmed that **Table 9 reproduces exactly on both
rows** — organic 12,773 / 8,968 (70.2%) / 3,805 (29.8%), robotic 58,689 / 54,534 (92.9%) /
4,155 (7.1%). The set-based result was never exposed.

The volume-weighted sentence in the same paragraph was wrong in magnitude and in direction.
It read: *"Weighted by reference volume the contrast narrows (both query types are dominated
by value references, since queries fetch values): only ~27–29% of all type-item references
are in class position."* Recomputed, **90.7% of organic type-item references are in class
position and 61.3% of robotic ones**. No denominator produces 27–29%; over all referenced
entities the shares are 72.1% and 23.6%. The published figure looks like a value share
reported as a class share.

The correction is more interesting than the sentence it replaces, because volume weighting
does not narrow the contrast — **it inverts it**. Counting elements, robotic queries are the
more class-oriented (92.9% vs 70.2%); counting references, organic queries are (90.7% vs
61.3%). Both are true and they measure different things: human value-position usage is a long
tail of one-off mentions (29.8% of distinct type-items, 9.3% of references), while robotic
value-position usage concentrates on few items referenced in enormous volume (7.1% of items,
38.7% of references).

The paper now also states which view bears on the metric. Coverage is a breadth measure, so
it is the set-level figure that governs how inflated a coverage percentage is, and that
inflation remains worst for human queries. The volume figures do not correct coverage; they
show the two query types reach their schema usage by different routes.

*A note on our own reasoning here.* We predicted from the set-level figures that the robotic
volume-weighted share would also be around 90%. It is 61.3%. The prediction was wrong and the
measurement stands; we mention it because it is exactly the kind of plausible inference that
the set-level numbers invite and that the paper should not encourage.

## Point-by-point

### [1] "Raw schema coverage" is used in the abstract before being defined
**Accepted.** Defined at first use, close to your suggested wording: "the proportion of a
KG's schema elements that queries explicitly reference in a given period."

### [2] Where are the 13 near-root anchor queries?
**Accepted; they are now published.** You were right that no file contained them. New script
`KG-Usage-analysis/wd_closure_queries.py` writes `out/wd_closure_anchor_queries.tsv`.

Run at the scope of the claim in §3.4 (the 2017 organic log), it reproduces the manuscript's
two closure figures **exactly** — **1,276** distinct anchors and **62,410** additional classes
credited by the closure — which is a strong check that the artifact and the claim are
measuring the same thing. It also corrects an off-by-one: `Q35120` (*entity*) is the anchor of
**12** queries, not 13. The manuscript is updated.

Two process notes. The first version of this artifact was generated before D2 was fixed and
had to be quarantined and regenerated: the anchor *counts* were right but the query *texts*
were misattributed, which is exactly the signature of that bug. And our first run pooled three
early-2017 windows rather than the single interval the claim is about, which inflated the
anchor count to 2,752; the script now defaults to the correct scope.

### [3] `rdf:type` as a Bio2RDF schema element
**Accepted in full.** See **D1**.

### [4] The supply–demand analysis is introduced abruptly; why Wikidata and not Bio2RDF?
**Accepted; the motivation is now stated, and so is the reason for the choice of KG.** The
position analysis establishes that Wikidata's coverage figure over-counts, but it says
nothing about whether the parts of the schema that *are* reached are the parts the KG is
built around. If the heavily populated regions were also the heavily queried ones, a low
coverage figure would simply mean users query a small but well-chosen core. Supply versus
demand settles that, and the two together are what make the coverage number interpretable.

On why not Bio2RDF: an inversion can only exist where a substantial part of the schema goes
unqueried, and Bio2RDF has essentially none. The union of 2019 queries reaches 97% of the
schema, leaving 16 elements of 541 untouched, so the comparison would have nothing to find.
Wikidata's organic queries reach about 4% of the class universe, which makes *which* content
goes unqueried a substantive question. This is now said in the text before Table 10.

### [5] Do not keep the pre-correction counts; the paper should be internally consistent
**Resolved, though not in the way either of us expected.** Your objection was
that reporting earlier counts because the differences are small is unsatisfying when the
corrected pipeline is the one the paper presents as accurate. Agreed in principle. The
schema correction has now forced a recomputation of every Bio2RDF figure from a single
consistently-defined element set, so the inconsistency you objected to is gone at its source.
What remains of the original paragraph is the narrower and still-useful statement that the
corrected preprocessing does not materially change the frequency vectors, which is a
robustness check rather than a justification for using older numbers. Its figures are
re-derived on the conforming basis: ρ = 0.954 over the 109 shared elements, an identical set
of ten most-used elements, a largest single-element difference of 21 references, and coverage
differing by 0.2 points. The reviewer-response framing you objected to is gone.

### [6] Why is adoption bounded only for predicates?
**Accepted, and it changed the section.** Types can be analysed, and doing so exposed a
confound.

Naively: **9%** of the 1,357 predicates Release 3 added are queried in the 2019 log, against
**85%** of the 264 added types. That invites a story about predicates going unadopted. The
gap is almost entirely **retirement**: **91.5%** of the added predicates no longer exist in
the 2024 schema the log is scored against, versus 16.5% of the added types. They are not
unadopted; they are absent from the denominator. Restricting to vocabulary surviving into
2024 erases the contrast — all 213 surviving types and all 115 surviving predicates are
queried — and that is not a finding either, since the robotic 2019 log already touches 525
of 541 elements, so any subset scores near 100% by construction.

The analysis measures retirement at one end and the coverage ceiling at the other. The
subsection now says so and **draws no adoption conclusion from Bio2RDF**, which withdraws
the previous claim that "schema growth vastly outruns query adoption." We kept the negative
result in, briefly, because the naive version is an easy mistake on a KG whose schema was
substantially rewritten between the queried release and the reference release. You suggested
in the first round that this paragraph might be better omitted if a clear connection could
not be established; this is the concrete reason you were right to doubt it.

### [7] Why should predicates appearing only in the later dump not be read as newly created?
**Accepted, and now answered with evidence rather than a caveat.** Mostly they *are* newly
created, and this is checkable because Wikidata allocates property identifiers sequentially.
The highest identifier in the 2017 extraction is **P4151**; **56 of the 68** candidates lie
above it and were therefore minted after the 2017 dump, while the remaining 12 are older
properties that simply had no qualifying triple in 2017. The results are insensitive to the
distinction: 66% of all 68 are queried by robotic clients (64% of the unambiguous 56) and 28%
by organic users (27%). The proxy is sound enough to use with its contamination stated.

Wikidata now carries the adoption claim alone, narrowed to what it supports: new properties
are adopted in *presence* but not in *prominence*, none reaching the top 100 within the year
(best rank 216/934 robotic, 161/549 organic). Recomputing from the released counts shifts the
previously reported 71%/31% to **66%/28%**.

### [8] Connect the utility experiment to existing SPARQL-autocomplete work; evaluate predicates too
**Accepted on both counts.**

*Positioning.* Bast et al. (CIKM 2022) and de la Parra & Hogan (ICSC 2021) are added to the
bibliography and discussed. The manuscript now states plainly what the experiment is not:
both systems rank from KG-side signals, ours isolates what a *usage*-derived signal adds, so
the measured gap is a lower bound on what a usage-aware ranker could contribute to such a
system — not a claim to outperform one. Integrating usage priors into a full autocompletion
system under its latency constraints is named as the follow-up.

*Predicates.* Run, and reported as new **Table 16**. Usage wins again but by much less than
for types, and the advantage narrows as the list grows:

| top-k | nDCG usage | nDCG supply | cov usage | cov supply |
|---|---|---|---|---|
| 10 | 85.9% | 58.6% | 43.3% | 23.0% |
| 100 | 90.9% | 72.6% | 81.4% | 72.5% |
| 1000 | 91.6% | 76.1% | 94.8% | 93.3% |

Demand-weighted MRR is 0.258 vs 0.202 (**1.3×**, against 2.9× for types). We report the
asymmetry rather than only the flattering class-side result, and explain it: Wikidata has
~1k predicates against ~100k classes, so a content-ranked predicate list has little room to
be wrong, and the content–demand inversion is a class-side pathology with no predicate
counterpart. Usage metadata helps most exactly where the content signal is weakest.

### [9] Repository comments

**[9.1] Data provenance and a figure→script map.** **Done.** New `REPRODUCIBILITY.md` gives
the source of every input dataset, including the four you could not locate and that
`data/download_all.sh` does not cover (the LSQ-derived Bio2RDF 2013 logs, `dbpedia_texts.txt`,
the five intermediate Wikidata windows, and the WDQS example set), plus a figure→script and
table→script map. Every path in that map was checked to exist. Linked from `README.md`.

**[9.2] `parse_validate_bio2rdf2019.py` is misleadingly named.** **Done.** Renamed to
`sparql_log_preprocess.py`, with all 18 referencing files updated and the module verified to
still load. The docstring was the substance of the point and is fixed too: it also described
the file as Bio2RDF-specific, and now states that only the CSV-streaming entry point is,
while the preprocessing helpers are shared across all three KGs.

**[9.3] The closure percentage should use the class universe, not TSE.** **Accepted, and it
turns out not to matter.** `wd_closure_queries.py` now reports both: the closure spans
**62.8%** of the class universe and **62.2%** of TSE. The difference is negligible because
predicates are only 931 of 104,286, so the manuscript's ~62% stands under either reading —
but it is now unambiguous which is meant.

**[9.4] Add the retrieval permalink for the WDQS example set.** **Done.**

**[9.5] Verify parallel result ordering.** **Accepted; it was a real bug.** See **D2**.

---

## Also corrected while working through the above

- **Figure 8 regenerated.** The schema fix changed the per-element count files it reads.
  Figure 9 is byte-identical, as expected, since `rdf:type` is a predicate and the top-types
  panels already excluded it.
- **Panel peak values were wrong**, including before this round. Measured: panel C peaks at
  2,522 uses/month and panel D at 5.3 — nearly three orders of magnitude apart, where the
  text said "approaching 10⁴" and "around 10²".
- **`\label{sec}`** at "Which Queries Reach Rare Classes" had lost its `:templates` suffix in
  the Overleaf revision, leaving two `\ref` calls undefined. Restored.
- **Variable standardization quantified** (raised last round): it merges 0.01–1.33% of
  queries across five logs, so variable naming is almost never the only difference between
  two logged queries. Standardization matters for correct parse-tree extraction, not for
  deduplication.

---

## Re-runs prompted by D2

Both Wikidata scripts that D2 affected have been re-run. The prediction held in both cases:
everything set-based reproduced, everything count-weighted had to be corrected.

**`wd_classvalue`** — Table 9 reproduces exactly on both rows; the volume-weighted claim was
inverted (see **D4**).

**`wd_temporal`** — Table 13 reproduces exactly, all four columns across all seven windows.
The frequency-derived statistics in §4.9.4 did not, and all three were wrong:

- The consecutive-window Spearman band was reported as ρ = 0.47–0.51 with an endpoint value
  of 0.44. It is **0.52–0.59** with endpoint **0.43** — slightly higher and just as narrow, so
  the stability argument is unchanged and marginally stronger.
- The persistent top-50 core is **fifteen** types, not fourteen, with *actor* and *airport*
  out and *year*, *television film* and *scientific article* in. A downstream sentence citing
  *actor* as a value-position core member is corrected accordingly.
- **The Wilcoxon claim inverted.** The paper reported the test as not significant for most
  adjacent windows and concluded that usage magnitude is "largely stationary month-to-month".
  Five of six adjacent windows are in fact significant; only December–January is not
  (p = 0.23). That conclusion is withdrawn. The stability finding now rests where the paper's
  own argument about large-N p-values says it should: with 1,500–1,900 paired types the test
  detects arbitrarily small differences, whereas coverage varying by under a percentage point
  and a narrow rank-correlation band are the informative measures, and both still hold.

Together with the DBpedia demand ranking, four independent analyses now show the same
signature: sets survive the misordering, counts do not.

## Still open

Nothing from your review. All nine comments are addressed and no `\begin{comment}` blocks
remain in the source.

Two items of our own housekeeping remain, neither affecting the manuscript:

1. `RESPONSE_TO_REVIEW2.md` is superseded wherever it quotes the Bio2RDF rarefaction, since
   it still reports 1.80×. It is left as the record of the previous round.
2. The robotic arm of `wd_classvalue` takes about 40 minutes on 8.2M queries. The script now
   persists its per-entity demand vectors to `out/`, so follow-up questions about these
   numbers no longer require a re-parse.

## A note on local builds

`\usepackage{comment}` needs `comment.sty`, which a default TinyTeX install lacks
(`tlmgr install comment`); Overleaf's full TeX Live has it. Separately, `python3` on this
machine resolves inconsistently between Homebrew and CommandLineTools, only one of which has
pandas/numpy — the analysis scripts want `/usr/bin/python3`. Worth pinning in the README.
