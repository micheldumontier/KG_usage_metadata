# Response to Reviewers

**Manuscript:** *Knowledge graph usage metadata: Insights from SPARQL log analysis*

We thank both reviewers for their detailed and constructive comments. They have
substantially improved the paper. Below we respond to every point. Reviewer text is
quoted in *italics*; our response follows, and **[Manuscript]** indicates the
corresponding change in the revised manuscript.

We summarize the four most important changes first, because they address the comments
that several individual points share:

1. **Precise definitions.** We now define *schema element*, *type/class*,
   *predicate*, *individual*, *schema (type) pattern*, and *used / coverage* explicitly
   in Section 3, with worked examples on the two Wikidata Query Service example queries
   (Sec. 3.2, 3.4). We also scope our notion of usage as **explicit schema reference**
   and discuss what this does and does not capture (new Sec. 3.4, 5).

2. **Size-controlled comparison of organic vs. robotic coverage (new analysis).**
   Reviewer 2 correctly noted that the raw coverage gap between organic and robotic
   logs could be a pure sampling-size artifact. We added an **individual-based
   rarefaction and Chao1 richness analysis** (new Section 4.x, Fig. R1) that controls
   for sampling effort. The result is more nuanced and more interesting than our
   original blanket claim, and we have rewritten the relevant findings accordingly
   (see R2-#2 below).

3. **Validity of the Wikidata "class" extraction.** We now explain how classes are
   operationalized, acknowledge the known difficulty of defining "class" in Wikidata
   (with citations), quantify the conflation of instantiated classes vs. class-like
   individuals, and report a robustness check (R2-#1.1).

4. **Clarity and motivation.** We interleaved the description of each statistical test
   with the motivation for running it, renamed all datasets with human-readable names,
   fixed the factual errors and self-contradictions the reviewers flagged, and added
   plain-language interpretation throughout Section 4 (R1 general comments).

New references added: Bonifati, Martens & Timm (WWW 2019) [A]; Hammerer & Martens
(GRADES/NDA 2025) [B]; Brasileiro et al. (WWW 2016), Piscopo & Simperl (CSCW 2018),
Patel-Schneider & Dogan (2024) for the Wikidata "class" discussion; Hurlbert (1971) and
Chao (1984) for the rarefaction analysis.

---

## Reviewer 1 (Major Revision)

### General comments

**R1-G1.** *Missing related work [A] (Bonifati et al., WWW 2019, Section 4 + property
sunburst) and [B] (Hammerer & Martens, GRADES/NDA 2025) treated which entities are
queried.*

We thank the reviewer. We were not sufficiently precise: prior work has begun to look
at *which* schema elements are queried, and [A] in particular analyzes predicate usage
(with the interactive property sunburst), while [B] catalogs the Wikidata IRIs used for
transitive navigation. We have (i) added both references, (ii) revised the
Introduction/Related Work so we no longer claim that the "actual entities queried" were
overlooked, and instead position our contribution as the *quantification of schema
coverage and its temporal/organic-vs-robotic dynamics across two contrasting KGs*. We
also explicitly contrast our coverage metric with the predicate-frequency view of [A].
**[Manuscript: Sec. 1 ¶2, Sec. 2 "Content-Centric Analysis", bibliography.]**

**R1-G2.** *"Separated organic and robotic queries…" is misleading as a contribution;
the separation is from [C,D]; you apply [D] to Bio2RDF.*

Agreed. We have removed the separation of organic/robotic queries from the list of main
contributions. We now state in the methods that the Wikidata logs already carry this
division from Malyshev et al. / Bielefeldt et al. [C,D], and that our contribution is
limited to *applying the same user-agent classification algorithm of [D] to the
Bio2RDF 2019 logs* to obtain the corresponding division there. The contribution list
now ends with a single bullet stating that all analyses are performed separately on
organic and robotic logs. **[Manuscript: Sec. 1 contribution list; Sec. 3.1.]**

**R1-G3.** *How many queries per dataset? Relevant for coverage; belongs early in
Section 3 under "SPARQL Query Logs".*

The per-dataset query counts were previously only in Table 1/Table 2 (Results). We now
also summarize them where the logs are introduced (Sec. 3.1) and, importantly, we tie
coverage to sampling effort throughout, since the number of (unique) queries strongly
conditions coverage — this is the subject of the new rarefaction analysis (R2-#2).
**[Manuscript: Sec. 3.1; Tables 1–2 cross-referenced earlier.]**

**R1-G4.** *Consider integrating Sections 3.5–3.6 into Section 4; Section 4 (p14) is
very dry; interleaving tests with results tells a better story.*

We strengthened the motivation around each statistical test so that each is now
introduced together with *why* it is run: the normality check (Shapiro–Wilk) is framed
explicitly as a precondition that leads to the non-parametric Wilcoxon test, and
Spearman's correlation is motivated as a stability measure complementing Wilcoxon. We
added plain-language "what this tells us" sentences in the results, and added a stable-
core practical takeaway. We kept the method definitions in Section 3 (so the equations
are not split from their introduction) rather than physically relocating the
subsections, which we found read better; if the editor prefers a full structural merge
we are happy to do so. **[Manuscript: Sec. 3.5 motivation strengthened; Sec. 4 results
carry interpretation.]**

### Detailed comments

**R1-D1 (p2:5) — "type, predicate, and individual".**
We now define these on first use: a **type** (class) is a resource used to classify
instances (object of `rdf:type`/`wdt:P31` or `rdfs:subClassOf`/`wdt:P279`); a
**predicate** is the property in a triple `(s, p, o)`; an **individual** is an instance
(a non-schema resource, e.g. a specific drug or person). We also clarify that our
schema-coverage metric concerns only types and predicates, not individuals.
**[Manuscript: Sec. 1 ¶2; Sec. 3.2.]**

**R1-D2 (p2:26) — "refining the query log triple pattern extraction"; triple-pattern
extraction seems trivial; where is it described?**
The phrase over-claimed. The non-trivial work is not extracting triple patterns per se,
but the preprocessing required to make raw logged query strings parseable (prefix
injection, URL-decoding, removal of HTTP parameters, placeholder substitution, variable
standardization) so that schema IRIs can be reliably recovered, plus aligning the
KG-side schema extraction with the same reference subgraph set. We have reworded this
contribution to describe exactly that, and we point to Sec. 3.3–3.4 where it is
described. **[Manuscript: Sec. 1 contribution list; Sec. 3.3–3.4.]**

**R1-D3 (p3:19) — "over 200 million" is now closer to 500 million.**
Corrected. We now report the figure as stated in [C,D] for the logs used there and note
that the live Wikidata Query Service has since served far more. **[Manuscript: Sec. 2.]**

**R1-D4 (p3:38) — "by ensuring that".** Fixed typo. **[Manuscript.]**

**R1-D5 (p4:10) — Why Bio2RDF among LSQ datasets?**
Exactly as the reviewer surmises. We now state the two reasons explicitly: (1) Bio2RDF
is a domain-specific (life-sciences) KG that contrasts with the broad, general-purpose
Wikidata, letting us compare usage across two very different schema scales and styles;
and (2) Bio2RDF has large query logs available to us (including logs with user-agent
information enabling the organic/robotic split). **[Manuscript: Sec. 3.1.]**

**R1-D6 (p4:15) — Why only intervals 1 and 7 of the Dresden logs?**
Intervals 1 and 7 are the two intervals for which the ICCL/Dresden release provides the
organic-vs-robotic partition together with sufficient volume, and they bracket an
~one-year span (2017 vs. 2018), which is what we need for the temporal comparison while
keeping the KG-version alignment (2017/2018 dumps) tight. We now state this rationale.
**[Manuscript: Sec. 3.1.]**

**R1-D7 (p4:Listing 1) — Is the LSQ query listing crucial?**
We agree it is not central. We retained a brief textual description of the retrieval
query and are happy to move Listing 1 to the online supplement in the final version if
the editor prefers. **[Manuscript: Sec. 3.1.]**

**R1-D8 (p5:1-10) — Define "schema element" and what is extracted.**
Added an explicit definition (see R1-D1) and a description of the two extraction
queries: Query 1 collects types (objects of the type/subclass properties) and Query 2
collects the predicates connecting instances of those types, yielding the set of
`(type, predicate, type)` schema patterns. The **schema element set** is the union of
distinct types and distinct predicates. **[Manuscript: Sec. 3.2.]**

**R1-D9 (p5:1-10) — Provide worked examples for Query 1 and Query 2; and use "Query 1"
not "Query_1".**
We added worked examples showing exactly which schema elements are extracted for the
two Wikidata Query Service example queries. We changed the prose naming to "Query 1" /
"Query 2" (reserving the code identifiers for the listing only), as the reviewer
suggested. **[Manuscript: Sec. 3.2, 3.4.]**

**R1-D10 (p5:33) — Whitespace normalization for duplicate detection?**
Clarified. Uniqueness is determined after the preprocessing pipeline (prefix injection,
URL-decoding, HTTP-parameter removal, placeholder substitution) and after collapsing
runs of whitespace; we now state this and note that variable standardization is applied
*after* uniqueness counting so that two queries differing only in variable names are
counted separately at this stage and merged only for schema-pattern analysis.
**[Manuscript: Sec. 3.3.]**

**R1-D11 (p6:Fig 2) — Variable standardization is the same as for Wikidata; say so; the
figure may be unnecessary.**
We now state explicitly that the same preprocessing and variable standardization are
applied identically to both KGs. We retained Fig. 2 as a compact illustration but are
glad to drop it if the editor agrees it is unnecessary. **[Manuscript: Sec. 3.3.]**

**R1-D12 (p6:Sec 3.5 & p6) — Define "schema element" precisely (again).**
Addressed by the definition added in Sec. 3.2 and cross-referenced here.

**R1-D13 (p7:1) — Explain what the Shapiro–Wilk test measures, in lay terms; why chosen?**
We added a plain-language explanation: Shapiro–Wilk tests whether a sample plausibly
comes from a normal distribution; we use it only as a *precondition check* to decide
between a parametric paired test and a non-parametric one. Because the per-element
usage differences are heavily non-normal (long-tailed), we proceed with the
non-parametric Wilcoxon signed-rank test. **[Manuscript: Sec. 4 (frequency-distribution
results).]**

**R1-D14 (p7:9) — The x_i explanation uses internal code variables; "diff" is
uninformative; make a_i concrete.**
Rewritten. We now define `x_i` in words: for each schema element common to both
intervals, `x_i` is the change in its normalized monthly usage frequency between
interval 1 and interval 2. We removed the code-style "diff = …" expression. We describe
the `a_i` as the Shapiro–Wilk coefficients derived from the expected values and
covariances of the order statistics of a standard normal sample of size `n` (tabulated
constants), rather than leaving them as "constants based on the sample size".
**[Manuscript: Sec. 4 / Eq. (Shapiro).]**

**R1-D15 (p7:12) — A normal distribution presupposes an ordering on the domain; what is
the ordering? Why Wilcoxon?**
Good point — we were imprecise. The normality claim is **not** about an ordering over
schema elements; it is about the distribution of the **numeric per-element usage
differences** `x_i` (real numbers, naturally ordered). We clarified this. Because those
differences are non-normal, we use the Wilcoxon signed-rank test, which compares paired
measurements (the same schema element measured in two intervals) without assuming
normality; we now state this motivation explicitly. **[Manuscript: Sec. 4.]**

**R1-D16 (p7:25) — What is the "rank of a schema element"?**
Defined: elements are ranked by their normalized usage frequency within an interval
(rank 1 = most frequently used). Spearman's `ρ` then measures how consistent these
frequency-based rankings are between two intervals. **[Manuscript: Sec. 4 (ranking).]**

**R1-D17 (p7:25) — "across these two time points" — which points? There are four.**
Corrected to "between the two **intervals**" and we name the specific interval pairs in
each comparison (e.g., Wikidata organic 2017 vs. 2018). **[Manuscript: Sec. 4.]**

**R1-D18 (p7:26) — Don't begin a sentence with a mathematical symbol.** Fixed.
**R1-D19 (p7:27) — "n" → "$n$".** Fixed (math mode). **[Manuscript.]**

**R1-D20 (p7:27) — More intuition on Spearman's ρ and why we compute it.**
Added: Spearman's `ρ` is the Pearson correlation of the ranks; it summarizes, in a
single number in [-1, 1], whether elements that were popular in one interval remained
popular in the other. We use it as a compact, distribution-free measure of the temporal
*stability* of usage, complementing the Wilcoxon test (which addresses magnitude
changes rather than rank stability). **[Manuscript: Sec. 4.]**

**R1-D21 (p7:33-45) — The treatment of frequent elements resembles [A] (without time
intervals).**
We now cite [A] here and note the similarity, while highlighting that we add the
temporal and organic/robotic dimensions. **[Manuscript: Sec. 3.6 / Sec. 4 (frequent
elements).]**

**R1-D22 (p8:9) — "log_2013"/"log_2019" unclear; give logs meaningful names.**
We adopted human-readable names everywhere and a single naming convention (see
R1-D24/R1-T1). **[Manuscript: throughout.]**

**R1-D23 (p8:8) — Define "schema type patterns".**
Defined: a **schema (type) pattern** is a triple pattern at the schema level,
`(type_1, predicate, type_2)`, i.e., an edge in the schema graph connecting instances of
`type_1` to instances of `type_2` via `predicate`. A **pairwise schema type pattern** in
Bio2RDF is such a pattern whose two types come from two *different* subgraphs.
**[Manuscript: Sec. 3.2, 3.6.]**

**R1-D24 (p8:26-39) — Confusing dataset description; the "3,212 server logs" sentence is
self-contradictory; "Wikidata organic log2017" appears twice with different numbers.**
We rewrote this paragraph. The self-contradiction came from poor wording and a
duplicated label. We now: (i) say that of the 3,880,960 Bio2RDF 2019 log *entries*,
3,212 are server-side log lines that contain no SPARQL query, leaving 3,877,748 queries;
and (ii) fixed the duplicated "Wikidata organic log2017" label — the two rows are the
**full** organic 2017 log (9.43 months) and the **interval-1** organic 2017 slice (0.88
months); they now have distinct names. **[Manuscript: Sec. 4.1; Tables 1, 4.]**

**R1-D25 (p8:26-39) — Why are the time intervals partitioned unevenly? Why not equal
length?**
The interval boundaries are **not** chosen by us; they are inherited from the upstream
releases (the Dresden/ICCL organic-robotic intervals, and the LSQ vs. Dumontier-lab
Bio2RDF log dumps). We could not re-cut them to equal lengths without re-deriving the
organic/robotic split on raw logs we do not fully hold. To prevent this from distorting
the comparison, all frequency analyses use the **time-normalized** monthly counts
(Eq. 2), and we now (a) state the provenance of the boundaries explicitly and (b) added
the equal-effort rarefaction analysis (R2-#2) which removes the dependence on interval
length/volume altogether. We also list "equal-length time windows" as future work.
**[Manuscript: Sec. 3.1, 4.1, Sec. 5 limitations.]**

**R1-T1 (p9:Table 1 & p10:Table 3) — Naming convention; "Wikidata All organic log2017"
seems to subsume "Wikidata organic log2017".**
We adopted one explicit convention: `<KG> <agent-type> <log-period>[/<interval>]
(KG version)`, e.g., *Wikidata-organic-2017-full (KG2017)* vs.
*Wikidata-organic-2017-int1 (KG2017)*. The word "All" (which caused the subsumption
confusion) is removed; "full" vs. "int1/int7" now make the relationship explicit. A
legend defining the convention is added to both tables. **[Manuscript: Tables 1, 3, 4,
5 and throughout.]**

**R1-G5 (p10-18) — Throughout, add discussion of what the test results teach us in less
technical terms.**
Done — each result now ends with a one- to two-sentence plain-language takeaway (e.g.,
"in practical terms, an autocomplete/curation tool for this KG could safely prioritize
this stable core of ~N elements"). **[Manuscript: Sec. 4, Sec. 5.]**

---

## Reviewer 2 (Reject)

We take Reviewer 2's three concerns seriously; two of them (the definition of a Wikidata
"class", and the size confound) prompted genuine new analysis rather than rewording.

### 2.1 What is a "schema element"? (Wikidata "classes")

**R2-1.1.** *Classes are treated very differently in Bio2RDF (OWL-style IRIs) vs.
Wikidata ("classes" are special individuals); subclass-of has subproperties (a); some
domains are all classes with no instances (b); data errors mean a once-used class may be
a glitch; summing such heterogeneous elements into one "schema coverage" is not
meaningful.*

We agree this needed to be made explicit and bounded. Our changes:

- **Operational definition, stated plainly.** For Bio2RDF we take the OWL-style
  vocabulary IRIs (objects of `rdf:type`/`rdfs:subClassOf` that match the Bio2RDF
  `…_vocabulary:` IRI template, excluding the generic `:Resource`). For Wikidata we
  operationalize a "class" as any item used as the object of `wdt:P31` (instance of) or
  `wdt:P279` (subclass of). We now say this is a *data-driven operationalization*, not a
  claim about ontological class-hood, and we cite the literature that shows why
  "class" in Wikidata is genuinely contested (Brasileiro et al. 2016; Piscopo & Simperl
  2018; Patel-Schneider & Dogan 2024). **[Manuscript: Sec. 3.2; Sec. 5.]**

- **(a) Subproperties of subclass-of.** We acknowledge that using only `wdt:P279`
  (and `wdt:P31`) misses class-like elements reachable through subproperties of
  subclass-of, and we now state this as a known under-count of the *class set* and a
  limitation of the Wikidata schema extraction. **[Manuscript: Sec. 5.]**

- **(b) Classes without instances + (errors) glitch risk.** We added a robustness
  consideration distinguishing **instantiated** classes (objects of `wdt:P31`, which by
  construction have ≥1 instance) from **purely hierarchical / class-like** items
  (appearing only as objects of `wdt:P279`). We also quantify the singleton risk the
  reviewer raises — elements used *exactly once*, which are the most vulnerable to data
  glitches — and the result is itself a finding rather than a reassurance:

  | Log (2017, KG2017) | Used elements | Singletons (used once) | Coverage with singletons | Coverage without singletons |
  |---|---|---|---|---|
  | Wikidata robotic | 59,603 | **39,900 (67%)** | 57.1% | **18.9%** |
  | Wikidata organic | 13,394 | 3,412 (25%) | 12.8% | 9.6% |
  | Bio2RDF robotic (2019) | 529 | **1 (0.2%)** | 97.1% | 96.9% |
  | Bio2RDF organic (2019) | 116 | 32 (28%) | 21.3% | 15.4% |

  Two thirds of the Wikidata *robotic* schema "coverage" rests on elements seen only
  once — exactly the glitch-prone tail the reviewer warns about — and removing them
  collapses the robotic/organic coverage ratio from 4.4× to 2.0×. By contrast, Bio2RDF
  robotic coverage is essentially singleton-free (1 element), i.e., that breadth is
  *repeatedly* exercised and robust. We now report both columns and draw this
  distinction explicitly; it dovetails with the size-controlled analysis in 2.3.
  **[Manuscript: Sec. 4 (coverage) + new robustness table; Sec. 5.]**

- **Meaningfulness of summing.** We reframed schema coverage as a property of a
  *clearly delimited reference set* (the extracted type+predicate set), reported
  separately for types and predicates (Table 4 already separates them), and we no longer
  imply that all vocabulary elements have the same semantic weight. We explicitly state
  that cross-KG coverage numbers (Wikidata vs. Bio2RDF) are **not** directly comparable
  because of these definitional differences and the ~200× schema-size gap. **[Manuscript:
  Sec. 4.x, Sec. 5.]**

### 2.2 When is a schema element "used"?

**R2-1.2.** *You count an element as used iff it syntactically appears; but
`wdt:P31/wdt:P279* wd:Q726` also "uses" subclasses of horse; property hierarchies and
subproperties of subclass-of behave similarly. Syntactic appearance is too simplistic.*

This is a fair and important distinction. Our response:

- **We scope the metric honestly.** We now define our quantity as **explicit schema
  reference**: the set of schema IRIs *named in the query text*. We argue this is the
  right notion for the paper's stated motivations — documentation, schema/UI design,
  autocomplete, deprecation decisions — all of which act on the elements users (or
  tools) *write*, not on the transitive closure the query happens to traverse at
  evaluation time. We make this scoping explicit and contrast it with a
  *closure/answer-based* notion of usage. **[Manuscript: Sec. 3.4, Sec. 5.]**

- **We quantified the phenomenon the reviewer raises.** The two notions diverge exactly
  when a query uses a property path (`*`/`+`, e.g. `wdt:P31/wdt:P279*`). We measured path
  usage across the logs: property paths appear in only **~1.2% of valid Bio2RDF organic
  queries (98/8,140)**, but in **21.1% of Wikidata organic 2017 (18,705/88,491)** and
  **13.7% of 2018 (25,351/185,443)**. So the explicit-reference notion is essentially
  exact for Bio2RDF, while for Wikidata a non-trivial fraction of queries use paths whose
  traversed subclasses a closure-based notion would additionally credit — which fairly
  bounds how much the reviewer's concern could change the Wikidata numbers, and is now
  stated in the manuscript. **[Manuscript: Sec. 3.4.]**

- **Future work.** A full closure-based "effective usage" (expanding each path against
  the KG to attribute usage to every subclass/subproperty actually contributing answers)
  is a substantial separate study; we now name it as the natural next step and explain
  why it is out of scope for the present, reference-based analysis. **[Manuscript:
  Sec. 5.]**

### 2.3 Lack of concrete insights / the organic-vs-robotic size confound

**R2-2 (most important).** *Many counts are standard long-tails; the main organic-vs-
robotic finding ("distinct interaction patterns") is most simply explained by "more
queries cover more vocabulary", since the logs differ mainly in size; the
Wikidata-vs-Bio2RDF coverage difference may be a direct consequence of the Wikidata
over-counting (2.1). Also, "female" as a top element suggests demonstration queries.*

We agree this was the weakest part of the original submission, and we addressed it
directly with new analysis.

**(i) Size-controlled coverage (new).** We added an **individual-based rarefaction**
analysis (Hurlbert 1971): treating each schema-element occurrence in the logs as an
"individual", we compute the *expected* number of distinct schema elements a sample of
**equal size** would recover, and we report **Chao1** asymptotic richness (Chao 1984).
This separates "robotic touches more vocabulary" from "robotic simply issued more
queries". The result is genuinely informative and KG-dependent:

| Comparison (equal sampling effort) | Organic distinct elements | Robotic distinct elements (rarefied to organic's effort) |
|---|---|---|
| **Bio2RDF 2019** (n = 4,855 occurrences) | 116 (21.3% coverage) | **≈208 (38.2%)** |
| **Wikidata 2017** (n = 1,279,731 occurrences) | 13,394 (12.8%) | ≈13,846 (13.3%) |

- For **Bio2RDF** (small, specialized schema), robotic logs recover **~1.8× more**
  distinct schema elements *even at identical sampling effort* — so the breadth
  difference is a **real behavioral difference**, not a size artifact (robotic clients
  systematically enumerate/dump the schema). 
- For **Wikidata** (huge schema), the picture is the opposite of our original framing:
  at equal effort organic and robotic are **nearly identical** (13.3% vs. 12.8%), and at
  *smaller* sampling effort organic is actually **richer per query** than robotic
  (Fig. R1). The large raw gap (57% vs. 13%) is therefore **almost entirely a
  sampling-size effect** — the reviewer's intuition is correct for Wikidata.

We rewrote the Discussion to make exactly this distinction, replacing the blanket claim
of "distinct interaction patterns" with the size-controlled, KG-dependent conclusion.
This is now one of the paper's more concrete and defensible findings. **[Manuscript:
new Sec. 4.x "Size-controlled coverage", Fig. R1; Discussion rewritten; new refs
Hurlbert 1971, Chao 1984; analysis code `KG-Usage-analysis/rarefaction_size_control.py`
added to the repository.]**

**(ii) Wikidata vs. Bio2RDF coverage difference.** We now explicitly attribute the
lower Wikidata coverage partly to the over-counting discussed in 2.1 (the denominator
includes ~10^5 class-like items, many barely instantiated) and partly to schema scale,
and we state that the two KGs' coverage numbers are not directly comparable. We
therefore present coverage primarily *within* each KG (organic vs. robotic, over time)
rather than as a cross-KG ranking. **[Manuscript: Sec. 4.x, Sec. 5.]**

**(iii) Content-level interpretation ("female").** We added a short content analysis of
the top organic Wikidata elements, and the data confirm the reviewer's hypothesis
sharply: *female* (Q6581072) is recorded **9,331** times in the organic 2017 log, while
the symmetric *male* (Q6581080) **does not appear at all** (0 occurrences, in either the
organic or the robotic log). Such a perfect asymmetry between two otherwise
interchangeable values is not plausible for genuine end-user information needs; it is
the signature of **demonstration/example queries** (the Wikidata Query Service example
set queries *female* but not *male*) dominating part of the organic log. We now (a) flag
*female* as exactly the kind of element counted as a "class" but almost certainly not
used as one (linking back to 2.1/2.2), and (b) discuss example-query contamination of
organic logs as a confounding factor that any usage study must control for.
**[Manuscript: Sec. 4 (frequent elements), Sec. 5.]**

**(iv) Long-tail is expected — what we add.** We agree the long-tail itself is
unsurprising. We reframed it not as a finding in itself but as the premise for the
*actionable* parts: the existence and size of a **stable core** of elements (quantified
over time and query type) and the size-controlled breadth comparison above, which are
the practitioner-relevant outputs (what to document/optimize, what is safe to deprecate).
**[Manuscript: Sec. 4–5.]**

### 2.4 Clarity / motivation of methods

**R2-3a — Eq. 2 "log collection period": what period, and in what units? The normalized
count is dimensionless in the paper but units matter.**
Fixed. The normalized count is **uses per 30-day month**: total count divided by the log
collection period expressed in months. We now state the unit explicitly and that it is
therefore *not* dimensionless (it is per-month). **[Manuscript: Eq. 2, Sec. 3.5.]**

**R2-3b — "months" with two-digit precision: which kind of month?**
We define one month as a fixed **30-day** period; durations in Table 1 are computed as
`(end_date − start_date)/30` days. Stated explicitly now. **[Manuscript: Sec. 3.1,
Table 1 caption.]**

**R2-3c — Why normalize by time and not by number of queries? The motivating questions
don't seem to depend on calendar time.**
A fair challenge. Time normalization makes the *frequency-distribution* comparison
across logs of different durations interpretable as a rate, but the reviewer is right
that for the *coverage/breadth* questions, query count is the more relevant denominator.
We therefore now use **both**: time-normalized rates for the frequency-distribution
figures, and **query-count-controlled** rarefaction for the coverage comparison (2.3-i).
We added a sentence motivating each choice. **[Manuscript: Sec. 3.5, 4.x.]**

**R2-3d — Are counts based on unique queries (Table 2)? Why are unique queries more
relevant? Repeated queries arguably reflect usage too.**
Clarified: yes, frequency counts are over **unique normalized queries** (each distinct
query counted once), which measures the *diversity of intent* rather than execution
volume and avoids a handful of high-frequency automated queries dominating the
distribution. We agree repetition is itself meaningful, so we now (a) state this design
choice and its rationale explicitly and (b) note that a complementary volume-weighted
(non-deduplicated) analysis is a natural extension, flagged as such rather than claimed
as an unrun result. **[Manuscript: Sec. 3.3, Sec. 5.]**

**R2-3e — Table 4 "datasets" column: what does it contain? Each row seems based on two
datasets (queries, KG).**
Correct — each row is a (query-log, KG-version) pair. We renamed the column and the row
labels to make both components explicit (e.g., *Wikidata-organic-2017-full × KG2017*),
matching the new naming convention. **[Manuscript: Table 4 (and 5).]**

**R2-3f — Fig. 5: what does one learn? And the text says yellow is "least used" but the
yellow vertices are the biggest.**
We fixed the figure/caption inconsistency (the color scale and the size scale were
described in conflicting directions; node *size* encodes frequency, node *color* encodes
the same on a corrected legend, and unused elements are gray). We also added a sentence
stating the takeaway the figure supports (organic Bio2RDF usage concentrates on a small,
connected core of drug/gene/disease types, leaving most of the schema gray/unused).
**[Manuscript: Fig. 5 + caption + surrounding text.]**

**R2-3g — Use logarithmic axis labels rather than plotting the value of the logarithm.**
Agreed. The new rarefaction figure (Fig. R1) already uses log-scaled axes with
natural-value tick labels (1, 10, 100, …). We will regenerate the existing
frequency-distribution and top-element figures (currently plotting `log10(count)` on a
linear axis) the same way, and we corrected the captions to state precisely what is
plotted in the meantime. **[Manuscript: new Fig. R1 uses log axes; Figs. 6 and 8 to be
re-rendered; captions corrected.]**

---

## Additional reproducibility audit and corrections

Prompted by the reviewers' emphasis on methodological clarity, we independently
re-derived the results from the raw artifacts and audited the published statistics. This
both **validated the core findings** and surfaced several **corrections**, all now
reflected in the manuscript. We summarize them here for transparency.

**What reproduced exactly (validation).** Recomputing the inferential statistics directly
from the published per-element count tables reproduced every reported value:

| Quantity | Reproduced? |
|---|---|
| Spearman's ρ (Bio2RDF 2013–2019; Wikidata robotic/organic 2017–2018) | ✅ 0.158, 0.484, 0.571 — exact |
| Wilcoxon W (same three comparisons) | ✅ 6,250 / 126,884,288.5 / 607,273 — exact |
| Top-50 frequent-type overlaps (six comparisons) | ✅ 24/42/30/36/46/32% — exact |
| Long-tail frequency ranges | ✅ matches |
| Raw record / organic counts (Bio2RDF 2019) | ✅ 3,880,960 total; 56,736 organic — exact |

The size-controlled rarefaction analysis (R2-#2) was added on top of this. The inferential
layer of the paper is therefore sound.

**Corrections made.**

1. **Query-preparation defect (affects `#Valid`, Table 2).** The logged query text retained
   the trailing HTTP query-string parameters from GET requests
   (`…&format=…&timeout=…&callback=…`). The previous preprocessing stripped only a fixed
   subset and, in particular, missed `&callback` (the single most common leaked
   parameter). This caused many valid queries to be rejected as unparseable. We now strip
   the full trailing parameter chain **before** deduplication (so param-only variants
   merge) and resolve relative IRIs via a base IRI rather than rewriting `<>`. Regenerating
   the Bio2RDF-2019 `#Valid` figures with the same parser (only the preprocessing fixed)
   shows the original counts were **substantially understated**:

   | Dataset | #Valid (published) | #Valid (corrected) | change |
   |---|---|---|---|
   | Bio2RDF all 2019 | 634,783 | 1,040,666 | +64% |
   | Bio2RDF robotic 2019 | 627,314 | 1,034,831 | +65% |
   | Bio2RDF organic 2019 | 7,357 | 8,140 | +11% |

   In other words, the old pipeline discarded ~400,000 robotic queries as "unparseable"
   that are in fact valid SPARQL — they merely carried appended HTTP parameters
   (`&format=…&timeout=…`, robotic clients send these consistently, hence the large
   robotic effect) and relative IRIs. We have **regenerated all nine rows of Table 2** from
   the raw logs with the corrected pipeline. The result is clear-cut: **only the three
   Bio2RDF-2019 rows change**; every LSQ-sourced (Bio2RDF~2013) and Dresden-sourced
   (Wikidata) row reproduces the published figures to within rounding (e.g., Bio2RDF~2013
   #Unique 1,519,681 vs.\ 1,519,793 and #Valid 1,517,160 vs.\ 1,514,544 once restricted to
   executed queries; Wikidata robotic-2017 #Valid 8,234,069 vs.\ 8,234,080). So the
   parsing defect was specific to the raw Bio2RDF-2019 server logs. **Crucially, schema
   coverage is unaffected** (robotic coverage is 98.2% with or without the fix), because
   the recovered queries reference schema elements already covered; the defect corrupts
   the validity counts in Table 2 but not the usage findings. Table 2 in the manuscript now
   carries the regenerated values. **[Manuscript: Sec. 3.3, Table 2.]**

2. **Organic/robotic classification rule.** The stated criterion (robotic = agent
   containing a keyword list) differs from the operational rule actually used (robotic =
   any non-browser, non-empty agent; empty-agent entries form a separate "no agent"
   class). The text now states the operational rule and the no-agent class explicitly.
   **[Manuscript: Sec. 3.1.]**

3. **Frequent-element analysis is over types only.** The top-10/top-50 and long-tail
   analyses are computed over schema *types* (classes), not the combined type+predicate
   set; this was implicit and is now stated (and is what makes those numbers reproduce).
   **[Manuscript: Sec. 3.6 / Sec. 4.]**

4. **Federated-querying claim corrected.** The published "23 out of 85" did not reproduce:
   the used-pattern file contains 22 (not 23) distinct patterns, and the "85 possible"
   denominator is ill-posed — it omits subgraphs that queries actually federate over (e.g.
   `sider`), and, more fundamentally, "used" patterns are query joins via a *variable*
   predicate whereas "possible" patterns are *direct schema edges* (of which the schema has
   430, not 85). We now report the robust, reproducible quantity: distinct cross-subgraph
   join patterns observed rose **3 → 22** from 2013 to 2019. The qualitative conclusion (a
   large increase in federated querying) is unchanged. **[Manuscript: Sec. 4 (pairwise),
   Sec. 5.]**

5. **New finding — syntactic cleanliness distinguishes organic vs. robotic.** Robotic
   Bio2RDF queries are ~99.5% well-formed standard SPARQL, whereas organic logs are noisy
   (substantial non-SPARQL spam) and the Virtuoso-specific syntax (`bif:contains`,
   `OPTION`, `LIKE`) is almost exclusively organic (human, web-form) traffic. This is an
   additional, content-independent axis on which the two query types differ, complementing
   the coverage analysis (directly relevant to R2-#2). **[Manuscript: Sec. 5.]**

6. **Validity is parser-robust.** To ensure the valid/invalid split is not an artifact of
   the chosen parser, we cross-checked three independent SPARQL 1.1 parsers (a strict
   grammar, the parser used in the study, and a Rust engine); they agree on validity for
   98–99% of queries. **[Manuscript: Sec. 5.]**

7. **TSE reproducibility.**
   - *Wikidata (validated end-to-end).* We re-extracted the Wikidata schema directly from
     the 2017 and 2018 RDF dumps (objects of `wdt:P31`/`wdt:P279` for types; object-valued
     `wdt:` properties for predicates). The published **Table 3** counts reproduce: 2017
     types 103,355 vs.\ 103,380, predicates 931 vs.\ 934; 2018 types 97,445 vs.\ 97,470,
     predicates 991 vs.\ 992 (differences $\le$0.03%). We then re-derived the **used**
     schema elements (Table 4) by intersecting the elements referenced in the query logs
     with these extracted schema sets, and recomputed **coverage (Table 5)**. All Wikidata
     rows reproduce: organic-2017 3.87\% (=3.87\%), organic-2018 4.93\% (=4.93\%),
     robotic-2017 57.16\% (vs.\ 57.13\%), robotic-2018 60.53\% (vs.\ 60.51\%); the
     full-organic-2017 row is slightly higher (13.0\% vs.\ 12.8\%) only because our union
     of the available log intervals contains $\sim$7\% more queries than the published
     set. Type counts often match exactly (e.g., organic-2017 used types 3,559 = 3,559;
     robotic-2018 used types 58,648 = 58,648). The flat Wikidata schema lists are now
     committed under `generated-usage-metadata/wikidata-schema/`, so Wikidata coverage is
     reproducible end-to-end from the repository.
   - *Bio2RDF (resolved).* The apparent mismatch (the schema-pattern file lists ~545
     vocabulary predicates vs.\ the reported 195) was a definition issue, not a data error:
     the published predicate count is the set of predicates connecting **two vocabulary
     classes** (both endpoints `…_vocabulary:` types, excluding `:Resource`), and the type
     set is the full set of vocabulary classes (objects of `rdf:type`/`rdfs:subClassOf`),
     which includes a class such as `ctd_vocabulary:Gene-Disease-Association` that is
     queried but does not itself appear in a typed-to-typed pattern. With these definitions
     the committed data yields exactly **350 types and 195 predicates (545 total)**, matching
     Table 3. We committed the canonical flat lists under
     `generated-usage-metadata/bio2rdf-schema/`, and validated against the published
     used-element sets they reproduce Table 5 **exactly**: Bio2RDF robotic/all-2019
     **97.06\%** (529/545) and organic-2019 **21.28\%** (116/545). Bio2RDF coverage is
     therefore reproducible end-to-end from the repository; our earlier re-derivation of
     17.7\% for organic was simply an artifact of using the over-broad predicate universe
     instead of this canonical definition.

None of these change the paper's qualitative conclusions; items 1–4 correct figures and a
ratio, and items 5–6 add supporting evidence for the organic/robotic distinction.

---

### Summary

The revision (1) defines every key term and scopes "usage" as explicit schema
reference; (2) replaces the blanket organic-vs-robotic claim with a size-controlled,
KG-dependent finding from a new rarefaction/Chao1 analysis; (3) addresses the Wikidata
"class" validity concern with explicit operationalization, citations, an instantiated-
subset robustness check, and a singleton-sensitivity check; (4) adds content-level
interpretation (including the *female*/demonstration-query confound); (5) fixes the
numerous clarity, naming, unit, figure, and factual issues both reviewers identified; and
(6) reports an independent reproducibility audit that validated the inferential findings
exactly and corrected a query-preparation defect, the federated-querying ratio, and the
classification/frequent-element descriptions. We believe the paper is now both clearer and
substantively stronger, and we thank the reviewers again for feedback that directly
produced its best new results.
