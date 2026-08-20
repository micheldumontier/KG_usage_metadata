# Response to Maryam's review (`review2.txt`)

Thank you for this review. It is unusually specific and several comments caught real
problems rather than wording preferences. Three in particular changed the paper's
substance and not just its prose:

1. **The figure/data provenance question was right, and we chased it down.** You noticed
   that `regenerate_figures.py` reads the committed `*_combined_schema_elements.csv`
   files. It does, and those files predate the corrected preprocessing. We have now
   quantified the consequence instead of arguing about it (see **V2** below): the effect
   on every frequency, concentration and ranking result is negligible
   (Spearman $\rho = 0.954$, identical top-10, largest single-element count change 21),
   and the paper now says so explicitly with the numbers.
2. **The parser question exposed a genuine ambiguity in the repository**, not just in the
   text (**V1**).
3. **The `Q6581080` claim was unsupported and is now removed** (**V3**).

We accepted the large majority of the comments as written. Where we pushed back, it is
flagged **[partially accepted]** or **[not accepted]** with the reason. Two things you
asked for required new computation, which we ran: the ranking-sensitive evaluation of the
autocomplete experiment (new Table 15) and the robotic-demand-to-supply column (Table 10).

A note on one global request: **all 97 occurrences of `---` have been removed** from the
paper, replaced by commas, colons or sentence breaks according to context. En-dashes in
numeric ranges (`2013--2015`, `1$--$3\%`) are retained, since those are correct LaTeX for
ranges rather than punctuation.

---

## Verification items (the three comments that needed code investigation)

### V1. "which parser is used, `rdflib` or `sparqljs`?"

**You were right that the repository is ambiguous.** `parse_validate_bio2rdf2019.py`
exposes `--parser {rdflib,pyoxigraph,sparqljs}` and **defaults to `rdflib`**, which is
almost certainly what you found. The reported numbers, however, all come from the
`sparqljs` path (`Schema-coverage-method/sparqljs-worker/extract_worker.js`). The other
two back-ends exist only for the cross-parser agreement check (98--99%) that we cite in
response to the earlier referee round; they contribute no reported value.

**Changed:** the Method section now states this explicitly rather than leaving it to be
inferred, naming `sparqljs` as the source of every validity and used-element count and
`rdflib`/`pyoxigraph` as validation-only. We also recommend changing the CLI default to
`sparqljs` so the repository cannot mislead a reader the same way twice.

### V2. Figure 9 (top frequent schema types) and the data-provenance concern

You raised three sub-points. All three are correct, and one of them is a real error in the
published figure.

**(a) The x-axis change is intentional.** The earlier version plotted $\log_{10}(\text{count})$
on a linear axis; the current one plots the count on a log-scaled axis with natural-value
tick labels. That was a deliberate response to a referee in the previous round who asked
for labelled log axes. This also explains your observation that bar lengths differ
slightly: a bar drawn from the left edge of a log axis has different geometry from a bar
whose length is the value of a logarithm on a linear axis. **No underlying data changed.**

**(b) The label and bolding regression is a real defect, now fixed.** You are right that
the earlier figure showed natural-language names alongside QIDs and used bold to mark
classes common to paired panels, and that the regenerated figure lost both. Worse, the
**caption still promised the bold marking**, so the caption was factually wrong. We have
restored both features and verified the caption against the regenerated figure.

The labels are now regenerated from the **period-matched 2017 dump** rather than from live
Wikidata or a hard-coded table, via a new committed script,
`KG-Schema-extractors/wd_qid_labels.py`. This matters for correctness, not just provenance:
labels drift, and `Q1004` is *comic* in the 2017 dump but *comics* on Wikidata today, so a
figure describing 2017 logs should carry 2017 names. The script auto-discovers the QIDs it
needs (the top-10 types of each Wikidata panel, 29 items) from the committed count files, so
it stays correct if the panels change. All 29 labels are now recovered and the regenerated
figure carries them; the label table is committed at
`generated-usage-metadata/wikidata-schema/qid_labels_en.tsv`.

A side benefit worth noting: with names on the bars, the class-vs-value point of
Section 4.8.1 becomes visible directly in the figure. The organic panels are topped by
*female (Q6581072)*, *actor (Q33999)* and *France (Q142)*, which the text identifies as
value-position items rather than classes, so a reader can now see the inflation we quantify
instead of taking it on trust. Panel H also shows *human (Q5)* and *Homo sapiens
(Q15978631)* as separate high-demand items, which is itself an illustration of the
item-based modeling issue.

While at it, we also fixed two legibility problems the regeneration had introduced but that
nobody had flagged: on panels whose counts span less than a decade, matplotlib was labelling
the minor ticks as well and the labels collided into an unreadable smear (now decade labels
only), and the panel E title was clipped (titles shortened).

**(c) The provenance concern is correct, and we have now bounded it.** The frequency
analyses do read the pre-correction per-element counts. Rather than assert this is
harmless, we re-derived the per-element usage vector for *Bio2RDF-organic-2019*, the log
most exposed because it is the sparsest, directly from the corrected valid-query set:

| quantity | released | recomputed from corrected set |
|---|---|---|
| Spearman $\rho$ between the two frequency vectors | — | **0.954** (111 shared elements) |
| top-10 most-used elements | — | **identical**, near-identical order |
| largest single-element count difference | — | **21** |
| used elements / coverage | 116 / 21.3% | 115 / 21.1% |

The used-element sets differ by seven elements in total (four only in the released set,
three only in the recomputed one, each referenced by one to four queries), a net change of
one. The reason a large change in *valid-query* count does not propagate is that the
correction adds only 11% to valid organic queries (7,357 → 8,140), and 86.9% of valid
organic queries reference no Bio2RDF schema element at all. The Wikidata and Bio2RDF-2013
logs were unaffected by the correction in the first place, so their counts are unchanged
by construction.

**Changed:** a new paragraph at the head of the usage-patterns results states the basis of
the frequency analyses and reports this robustness check with the numbers above.

**One thing you should know, because it is what likely triggered your concern.** The
`out/` directory contains exploratory runs that *appear* to contradict the paper:

| run | USE | TSE | coverage |
|---|---|---|---|
| paper (Table 5) | 116 | 545 | **21.28%** |
| `bio2rdf_organic_canonical` | 110 | 544 | 20.22% |
| `bio2rdf2019_organic_sparqljs_fixed` | 161 | 910 | 17.69% |

These use different and looser schema denominators (544 and 910 against the released 545),
and we traced the `canonical` under-count to an extractor that misses seven
`*-Association` types. We confirmed those seven are genuinely referenced in full-IRI
`rdf:type` object position in the valid organic queries, so **116 is correct and 110 is an
under-count**. `VALIDATION_SUMMARY.md` says Bio2RDF coverage "reproduces exactly," but that
check recomputed 116/545 from the committed CSV rather than end-to-end; the wording
overstates what was verified. **We recommend deleting or clearly labelling these
exploratory outputs**, since they invite exactly the inference you drew.

**A second, smaller defect found while checking this.** `is_type()` in
`regenerate_figures.py` classifies a Bio2RDF element as a type by testing whether the
character after `_vocabulary:` is uppercase. That misclassifies **28 of the 350 released
types** whose local names begin lowercase (`ctd_vocabulary:clv`,
`pharmgkb_vocabulary:gene-disease-Association`, …). The visible consequence is confined to
one panel, but it is a real error in the published figure: panel D (*Bio2RDF-organic-2019*)
omits `pharmgkb_vocabulary:gene-disease-Association`, which with 42 references is the
**fourth-largest type in that log**, and promotes `sgd_vocabulary:Location` (32) into tenth
place in its stead. Panels A, B and C are unaffected. Fixed by classifying against the
released schema file instead of by capitalization.

### V3. Provenance of the `Q6581080` claim

**Accepted; the claim is removed.** We traced the *origin of the anecdote* to the previous
referee round (`reviews.txt:136`), where a reviewer argued that the prominence of *female*
in Fig. 7 indicated example-query domination "otherwise it seems hard to explain why the
symmetric concept 'male' is so much less used." That much we can cite. But we could **not**
establish any source for the specific assertion that the comparison was made against
`Q6581080`/*Pirhasan*; it survives only as a third lookup in
`KG-Usage-analysis/wd_decontaminate.py:97`. You are right that it appears abruptly and
unsupported.

**Changed:** the *Pirhasan* digression is deleted. The paragraph now (i) states the
observation explicitly first (*female* ranks high, *male* does not, which invites the
example-contamination inference), (ii) answers it with the measurement (9,753 vs 2,931
unique queries, roughly 3:1, not the near-absence the inference requires), (iii) attributes
the residual skew to two factors we explicitly cannot separate, and (iv) closes on the
methodological point rather than the anecdote, as you suggested in your sub-point 4.

### V4. Two further defects we found while checking your comments (you did not raise these)

**(a) The frequency-distribution text described the old plotting convention.** See item 40.

**(b) The rarefaction "sampling effort" was never defined, and one predicate dominates it.**
The paper quotes an effort of $n = 4{,}855$ occurrences for *Bio2RDF-organic-2019* without
saying what an occurrence is. We reconstructed it: one occurrence is one reference to one
schema element by one unique query, with the SPARQL `a` keyword counted as `rdf:type`
(an independent recount reproduces 5,129 against the released 4,855, the residual being
regex-versus-parse-tree matching). The definition is now stated in the text.

Reconstructing it also surfaced something worth stating: **3,603 of those 4,855 occurrences
(74%) are the single predicate `rdf:type`**, which every type-assertion query names. It is a
legitimate member of the 545-element universe, so this is not an error, but it means the
nominal effort figure is dominated by one generic predicate and overstates how much
*distinguishing* evidence the sub-sample carries. Since the robotic log is rarefied to the
same total and `rdf:type` is similarly ubiquitous there, the effect pushes both sides the
same way and does not overturn the 1.79$\times$ Bio2RDF result. The rarefaction subsection now
carries this as a second explicit caveat alongside the exchangeability one.

**(c) "The two KGs behave oppositely"** was an instance of exactly the over-generalization you
flagged elsewhere; softened to "behave differently, in opposite directions."

---

## Introduction

| # | Your comment | Response |
|---|---|---|
| 1 | Add the "These insights constitute usage metadata…" sentence to the end of ¶1 | **Accepted**, added verbatim. |
| 2 | Move "We refer to the set of distinct types and predicates…" before the definition of *individual* | **Accepted**, moved. |
| 3 | Replace "syntactic usage" with "explicit usage" to avoid confusion with query grammar | **Accepted.** Renamed throughout, including the Method and Discussion where the term recurs. The point is well taken: the paper elsewhere discusses genuine *syntax* (parse validity, vendor extensions), so the collision was real. |
| 4 | Remove all `---` throughout | **Accepted**, all 97 removed. |
| 5 | "relations" → "predicates" for consistency | **Accepted**, both occurrences. |
| 6 | Remove "The output of this analysis can be termed 'usage metadata'" as now redundant | **Accepted**, removed. |
| 7 | The preprocessing contribution overlaps the workshop paper; state only the improvement | **Accepted.** Rewritten to credit \cite{mohammadi2024analyzing} with prefix injection, URL-decoding, placeholder substitution and variable standardization, and to claim only what is new: stripping *any* terminal run of `&key=value` segments anchored to the end of the string rather than matching a fixed keyword list, and normalizing *before* deduplication. |
| 8 | Contributions should describe methodological/conceptual contributions, not empirical findings | **Accepted.** The usage-patterns bullet now states the measures and procedures introduced rather than what they found. |
| 9 | Clarify "size" and "equal sampling effort"; rarefaction equalizes occurrences, not queries; "disentangling genuine behavioral differences" is too strong | **Accepted in full, and this was the most useful comment of the set.** The bullet now defines sampling effort as *the number of observed schema-element occurrences, not the number of queries*, and claims only that the analysis "tests whether a coverage difference persists once the number of observed occurrences is held equal," separating the size-attributable part from the rest. We propagated the same correction to every other place the paper made the stronger claim (see Results and Discussion below). |

## Method

| # | Your comment | Response |
|---|---|---|
| 10 | Remove the redundant ", and we relate coverage to this sampling effort explicitly in Section 4" | **Accepted**, removed. |
| 11 | "a measurement issue specific to item-based KGs" is too strong and uncited; "item-based" is used abruptly and undefined | **Accepted.** We now define both styles before using either: an *OWL-style* KG has classes as dedicated vocabulary IRIs disjoint from instance data and not legitimate property values (Bio2RDF, DBpedia); an *item-based* KG has no formal class/instance separation, so the same resource may act as a class in one triple and a value in another (Wikidata). The unsupported universal claim is replaced by "In the logs we analyse, the *same* item is far more often referenced as a value than as a class," which is what we measured. |
| 12 | Remove "which earlier processing overlooked" | **Accepted**, removed. |
| 13 | `sparqljs` vs `rdflib` | See **V1**. |
| 14 | "In the 2017 organic queries" lacks the KG name | **Accepted**, now "of Wikidata". |
| 15 | "earlier pipeline" is vague: cite the workshop paper, and use *Bio2RDF all log2019* rather than the robotic row, since that is the dataset used there | **Accepted on both counts.** Now cites \cite{mohammadi2024analyzing} and quotes the comparable dataset: 1,040,666 vs 634,783 for *Bio2RDF-all-2019*. |
| 16 | The parsing-defect sentence is a reviewer response and does not belong in the paper; remove it | **Accepted**, removed. |
| 17 | Trim the same material from the Table 3 caption | **Accepted.** The caption now defines the columns and notes the 2013 executed-query basis, without the reviewer-response narrative. |

## Results: coverage and the equal-effort comparison

| # | Your comment | Response |
|---|---|---|
| 18 | Use "coverage gap" rather than "gap" | **Accepted** throughout the subsection. |
| 19 | Replace "To separate a genuine behavioral difference" with a precise statement | **Accepted**, using your suggested wording. |
| 20 | The Chao1 sentence is awkwardly constructed | **Accepted**, rewritten to your suggested form. |
| 21 | The large-vs-compact KG generalization is unsupported; results concern Wikidata and Bio2RDF specifically, and size is not established as the explanation | **Accepted.** The claim is now scoped to "the two logs analysed here," and we add explicitly that with two KGs we cannot separate schema size from differences in data, user communities and workloads. |
| 22 | The singleton-validity conclusion is overly compressed; and "taxa" mixes taxa with non-taxonomic concepts (*ghat* is geographic) | **Accepted on both.** Replaced with your suggested sentence, and the examples are now split into biological taxa (*Quercus velutina*, *Pinales*) and specialised non-taxonomic concepts, with *ghat* glossed as a South Asian riverside step structure. |
| 23 | "genuine, not a size artifact" overstates what rarefaction establishes | **Accepted**, now "persists after controlling for sampling effort." |
| 24 | "The most plausible explanation is…" should be more cautious | **Accepted**, now "One possible explanation," and we add that the endpoint architecture and the six-year gap change together, so the two cannot be separated. |
| 25 | The closing sentence combines too many contributions and conclusions; split it, and soften | **Accepted.** Split into a numbered pair of contributions (the 2013 organic/robotic split; the temporal organic comparison) followed by your suggested sentence, plus an explicit statement that equalizing effort controls for sample size only. |
| 26 | "under-recognizes" → "underestimates" | **Accepted.** |
| 27 | Drop "for cross-period consistency" as unconvincing | **Accepted**, removed. |
| 28 | Why are different schema definitions used for historical releases and 2024? The same definition should ideally be applied across releases | **Accepted as a fair criticism, and we now answer it rather than noting it.** This is a data-availability constraint, not a choice: the 2024 denominator comes from a live endpoint, which permits the restrictive definition; Releases 2 and 3 are no longer served anywhere, so their only surviving record is Bio2RDF's per-dataset statistics files, which enumerate all predicates and only instantiated types. We cannot re-derive the restrictive definition from those files. We now state this, and add that the bias direction is known: a broader denominator can only *lower* the version-matched percentages, so it cannot manufacture the increase we report. |

### The ordering of Section 4

**Accepted, and reorganized as you suggested.** Your diagnosis was exact: the jumps came
from two paragraphs sitting in the wrong subsections, not from the subsection order itself.
*What the Bio2RDF organic-2019 log actually contains* sat at the end of the general
coverage subsection, and *Validity of the extracted classes* sat at the end of the general
size-controlled subsection. Both are now moved, and the results progress as:

```
4.5 Calculating SPARQL Schema Coverage          (general)
4.6 Size-Controlled Coverage                    (general)
4.7 Bio2RDF-specific Analyses                   <- new grouping
      what the organic-2019 log contains
      organic vs robotic in the 2013-era log
      schema-version robustness
4.8 Wikidata-specific Analyses                  <- new grouping
      validity of the extracted classes
      class- vs value-position usage
      generality across modeling styles: DBpedia
4.9 Knowledge Graph Usage Patterns
4.10 Usage Metadata
```

Both new groupings open with a sentence saying what is grouped and why. The move was verified
by building the paper: no undefined references and no undefined citations, so every
cross-reference survived the reorganization (see **Build status** below).

## Results: what Wikidata coverage measures

| # | Your comment | Response |
|---|---|---|
| 29 | The opening sentence is awkward | **Accepted**, rewritten using your second suggested framing (Bio2RDF classes are only referenced as classes; Wikidata items appear as both). |
| 30 | "Two readings follow" → "These results have two implications" | **Accepted.** |
| 31 | The class/value split as a "behavioral signal" is too strong | **Accepted.** Now reported as a systematic difference *between the analysed logs*, with an explicit statement that generalizing to querying behavior would need further evidence. |
| 32 | "holds across natural domains" is stronger than Table 10 supports | **Accepted**, now "a similar pattern is observed across the analyzed domains." |
| 33 | Clarify that "Supply (% instances)" is the share of *items*, not of classes; and make the instance-supply vs class-demand rationale explicit before the table | **Accepted, both.** A new two-point paragraph precedes Table 10: it states that supply is a share of instances and gives the *taxon* example (7.6% of classified items, not 7.6% of classes), then states that the comparison is deliberately instance-level supply against class-level demand and what question that answers, warning against expecting an instance-to-instance reading. |
| 34 | Table 10 reports the organic/supply ratio but not the robotic one | **Accepted, and computed.** A `Rob/supply` column is added. It strengthens the contrast rather than merely balancing the table: bots over-query *scholarly publication* relative to content (0.75 vs 0.13 organic) and *geographic features* (1.37 vs 0.69), and geographic features is the one domain bots over-query while humans under-query it. The prose now cites both ratios. No ratio is given for the unclassified residual, whose supply share is not a meaningful denominator; the caption says so. |
| 35 | "A natural objection…" is unconvincing framing | **Accepted**, replaced with your suggested "An alternative explanation is…". |
| 36 | "tracks the *data model*, not KG size" is too strong | **Accepted**, now "These results suggest that the value-only fraction is more closely associated with the data model than with KG size," scoped to the three KGs analysed. |
| 37 | "The phenomena we report are therefore not Wikidata-specific" | **Accepted**, replaced with your wording. |
| 38 | The closing paragraph conflates two distinct conclusions; "A faithful figure" is overly definitive | **Accepted.** Split into the two findings and hedged to "a more faithful estimate," close to your suggested replacement text. |

## Results: usage patterns

| # | Your comment | Response |
|---|---|---|
| 39 | Dataset names do not match the template defined in the dataset-retrieval section | **Accepted, resolved by extending the convention rather than renaming everything.** The tables and figure panels consistently use a paired form (`log<period>_kg<version>`) that the stated convention did not cover, which is the actual inconsistency. Section 4.1 now defines both forms and says which is used where. We chose this over a global rename because renaming across nine tables, ten figure panels and the prose is a high-risk edit for a purely notational gain; if you prefer the full rename, it is a mechanical follow-up. |
| 40 | You quoted the Plot A/C/D sentence without stating the defect | **We think we found what you were pointing at, and it is a real error.** The duplication in your quote looks like a copy/paste artifact (the paragraph reads once through Plots A--D in the source). But the quoted sentence contains a genuine inconsistency: it says Plot C reaches "a log count approaching 4" and Plot D "around 2", and later that Plots G/L exceed "a log count of 6" while H/M "peak around 5". Those numbers describe the *old* convention, where the axis showed the value of the logarithm. Figure 6 now plots natural values on log-scaled axes, as its own caption two paragraphs earlier states, so the text and the figure contradicted each other. Corrected to "approaching $10^{4}$ uses per month", "around $10^{2}$", "exceeding $10^{6}$", "around $10^{5}$". We also fixed a missing space ("6.In contrast"). If you meant something else, please say and we will revisit. |
| 41 | The adoption-of-new-elements paragraph is abruptly motivated; strengthen the transition, move it, or omit it | **Accepted, promoted to its own subsection with a real motivation.** It is now Section 4.9.3 with a transition explaining why it follows: the preceding analyses hold the schema fixed within an interval and describe how *existing* elements shift in popularity, saying nothing about elements that did not yet exist; and this matters directly for the practical recommendation we make, because a maintainer who prioritizes by observed usage needs to know whether new vocabulary is systematically missed. |
| 42 | "A natural worry" is informal; open with the validity threat and method | **Accepted**, replaced with your suggested opening. |
| 43 | The female/male paragraph shifts abruptly, the anecdote is not stated, `Q6581080` is unsupported, and the closing methodological point should be introduced | See **V3**. All four sub-points accepted. |
| 44 | The pairwise-usage results arrive before the concept and motivation; and it is unclear how 3 → 22 comes from Figure 10 | **Accepted, both.** Promoted to a subsection that first explains Bio2RDF's subgraph organization, why cross-subgraph joins are the thing worth measuring, and why the analysis cannot be run on Wikidata; then defines the pairwise pattern; then reports the result. We now state explicitly that 3 and 22 are the counts of **non-zero cells** in the two heatmap panels. |
| 45 | The motivation for the coarser signature representation vs Asprino's templates is not explained | **Accepted.** We now justify the simplification: the research question concerns which *combinations of schema elements* classes are reached through, not how complete query structures are composed, so the representation discards structural features while preserving exactly the schema interactions under study, and it is computable from the extracted elements we already have. |
| 46 | "the pooled Wikidata organic windows" does not say which windows | **Accepted**, now named: all seven 28-day windows of the equal-interval analysis, 2017-06-12 to 2018-03-25. |
| 47 | The cross-KG comparison of signature counts is not supported and the "encyclopedic vs biomedical" reading is speculative | **Accepted, removed.** We now state that the absolute counts (31,495 vs 174) are not on a common footing and draw no conclusion from their ratio, pointing instead to the within-log concentration as the comparable quantity. |
| 48 | The rare-classes paragraph is hard to follow: the "mechanically lower-bounds" argument is unexplained, and result and artifact-check are interleaved | **Accepted, restructured into four steps** as you suggested: (i) the finding in one sentence; (ii) definitions of *class frequency* and *signature popularity*, which were previously assumed; (iii) the evidence (correlation, then decile extremes); (iv) the artifact check, now opened with the intuition in plain terms ("if a class is referenced by $n$ queries, any signature containing it is issued at least $n$ times, so a positive correlation is guaranteed") before the supporting statistics. |

## Results: utility experiment

| # | Your comment | Response |
|---|---|---|
| 49 | Add a "Usage metadata" subsection with the utility study nested under it | **Accepted.** Section 4.10 *Usage Metadata* now opens by stating what the metadata comprises, with the utility study as 4.10.1 and the released artifact following. |
| 50 | The KG-supply baseline needs stronger justification; it is odd to expect class prevalence to predict demand, and it sits oddly with the paper's own inversion finding | **Accepted, and this is the comment we found most clarifying.** You are right that supply is not a plausible predictor, and our own Section 4.8.1 predicts it should fail. That is exactly why we chose it, and the paper never said so. It now does: supply is the only ranking a maintainer can compute *without log access*, from the KG alone, so it is the default fallback when usage data is unavailable. The comparison is not a test of a plausible rival; it quantifies the cost of using the readily available content signal instead of usage metadata, turning the inversion from an observation into a measurable penalty. |
| 51 | The claim is based on one KG and one temporal split, so it cannot support a general forecasting claim | **Accepted.** The subsection title is now "usage metadata predicts demand better than KG content **in this setting**," and a new closing paragraph states plainly that the experiment covers one KG, one query type and one split; that it does not establish general forecasting; and that the supportable claim is the narrower one about beating the content-based default. Additional KGs and periods are named as future work. |
| 52 | Since the application is autocomplete, a ranking-sensitive evaluation is needed, or an explanation of why coverage suffices | **Accepted, and we ran it.** New Table 15 reports nDCG@$k$ with graded relevance equal to each type's deduplicated 2018 demand, plus a demand-weighted MRR. The ordering result is *sharper* than the coverage result: nDCG@10 is **94.9%** for the usage ranking against **44.5%** for supply, staying above 92% out to $k = 1000$, while supply never exceeds 50%. Demand-weighted MRR is 0.338 vs 0.117 (2.9×). So the usage ranking not only contains the right types but places them near the ideal order, whereas supply both omits types and mis-orders those it has, which is what matters for a list read top-down. Implemented in `KG-Usage-analysis/wd_utility_ranking.py`; it reproduces Table 14's coverage column exactly, which is an independent check on the original experiment. |

## Discussion and Conclusion

| # | Your comment | Response |
|---|---|---|
| 53 | The "To quantify the overall usage" paragraph generalizes two case studies into a rule about KG scale | **Accepted.** Rewritten to tie the interpretation to the analysed datasets, in the form you suggested, and to draw the *methodological* lesson (a raw coverage gap cannot be read as behavioral without an equal-effort comparison) rather than a structural one. We add that with two KGs we cannot attribute the differing outcomes to scale, since the systems differ in domain, community and workload. |
| 54 | The syntactic-difference paragraph is out of place in the Discussion; move it to preprocessing/results, restructure it, and keep it specific to the Bio2RDF logs | **Accepted in full.** Moved to the preprocessing results (Section 4.3) and split into three labelled observations: what the invalid queries actually are (web-form spam, `/sparql` fragments); the concentration of Virtuoso extensions in organic traffic, now explicitly attributed to the web-form access path rather than to human querying as such; and the parser-independence of the validity rate. The Discussion's user-agent-proxy limitation now cross-references the new location and carries the same caveat. |
| 55 | "enhanced emphasis" is poor phrasing | **Accepted**, rewritten to state what was observed and name the endpoint unification as a likely contributing factor. |
| 56 | Replace "In conclusion" with "Together…" and give a concise summary of findings | **Accepted.** Now opens "Together," and summarizes the four concrete findings rather than asserting that the work is valuable. |
| 57 | "two-endpoint result" is confusing; say two intervals | **Accepted**, now states that the original analysis compared the 2017 and 2018 intervals. |
| 58 | "isolates the cause" should be "isolates the size effect"; and the modeling-style conclusion is too broad for two or three KGs | **Accepted, both.** "Cause" is gone. The conclusion is now scoped to the three KGs examined, with an explicit statement that three KGs cannot establish a general association and that a KG with different conventions could behave otherwise. |
| 59 | Conclusion: soften "reflects a genuine behavioral difference only for the compact Bio2RDF schema" | **Accepted**, now "persists after controlling for sampling effort only for Bio2RDF." |
| 60 | Conclusion: the DBpedia claim is too broad; we report observations and what we think they suggest, not proofs | **Accepted.** "Confirms … tracks" becomes "indicates … is associated with," followed by "With three KGs these are reported observations rather than established regularities." |

## Two remaining items

| # | Your comment | Response |
|---|---|---|
| 61 | Table 4: why is the number of unique valid **normalized** queries not reported? | **Accepted; you are right that the paper describes variable standardization and then never reports its effect.** We report it in the prose of the preprocessing results rather than as a table column, because we could measure only four of the nine rows in the time available and a half-empty column would be worse than none. The measured effect is small and consistent: standardization reduces *Bio2RDF-organic-2019* from 8,208 valid queries to 8,099 distinct shapes (1.3%), *Bio2RDF-robotic-2019* from 1,034,833 to 1,034,754 (0.01%), *Wikidata-organic-2017-int1* from 88,514 to 88,116 (0.45%), *Wikidata-organic-2018-int7* from 185,478 to 184,934 (0.29%), and the multi-million-query *Wikidata-all-2017-int1* from 8,317,396 to 8,316,939 (0.01%). The useful conclusion is one the paper had not drawn: variable naming is almost never the *only* difference between two logged queries, so standardization matters for correctly extracting schema elements from the parse tree, not for deduplication. Note that the last figure is for the *all* log, not the robotic one: the Dresden release ships *all* and *organic* per interval, and robotic is their difference (measured all − organic = 8,228,882 against the paper's robotic 8,234,089, agreeing to 99.94%). The remaining rows (*Wikidata-robotic-2018*, *Bio2RDF-all-2013*, *Bio2RDF-all-2019*) are the remainder **if you want the full table column.** |
| 62 | "larger samples mechanically touch more vocabulary" contradicts "more queries in a window do not expand coverage" | **Accepted, and this is a genuine inconsistency in the wording rather than in the results.** The two statements were about different comparisons. Monotonicity holds for *sub-samples drawn from one log*: a larger sub-sample cannot recover fewer distinct elements. The equal-interval observation is *across different windows*, where organic coverage has already saturated, so a 4.7× volume range moves it barely at all. The rarefaction section now states the monotonicity as a property of within-log sub-sampling, says explicitly that it does not imply a larger log must show higher coverage than a different smaller one, and forward-references the saturation result. The two claims are now visibly consistent. |

---

## Build status

**The paper compiles clean.** Built with TinyTeX (TeX Live 2026) via the full
`pdflatex` / `bibtex` / `pdflatex` / `pdflatex` cycle:

- **37 pages**, exit status 0 on every pass
- **zero errors**
- **zero undefined references and zero undefined citations**, so the section
  reorganization did not break any cross-reference
- **zero overfull or underfull boxes**, so the widened Table 10 and the new Table 15 both fit
  the column without manual adjustment

Numbering after the reorganization, for reference when comparing against your comments:
the results run 4.5 coverage, 4.6 size-controlled coverage, 4.7 Bio2RDF-specific (4.7.1 the
2013-era log), 4.8 Wikidata-specific (4.8.1 class- vs value-position), 4.9 usage patterns,
4.10 usage metadata (4.10.1 utility, 4.10.2 released artifact). Your "Figure 9" and
"Figure 10" and "Table 10" all still carry those numbers; the utility table is Table 14 and
the new ranking table is Table 15.
- **The `#Normalized` column is incomplete** (item 61).
- **No end-to-end regeneration of every frequency figure from the corrected logs.** We
  bounded the effect instead (V2) and judged the measured impact too small to justify a
  full re-run of the Wikidata pipeline over the 20 GB and 32 GB dumps. If you would rather
  have the full re-run for the record, the inputs are all present locally and we can do it.
- **The exploratory `out/` runs are still in the repository.** We recommend removing or
  labelling them, but have not deleted anyone else's outputs.

## A performance note for whoever reruns the label extraction

Our first attempt used `gzip -dc dump.ttl.gz | grep -F -A 25 -f patterns`. On macOS this is
unusable: BSD `grep` with a pattern file *plus* context lines burned **61 minutes of CPU to
the decompressor's 20 seconds** and had recovered only 5 of 29 labels. Replacing it with a
chunked binary scan in Python, locating the fixed byte string `" a wikibase:Item ;"` with
`bytes.find` and testing only the resulting entity headers against a set, runs at **~950 MB/s**
and completes the pass in minutes, roughly a 200x improvement. The committed script uses the
fast path and says so in a comment, so the mistake is not repeated.
