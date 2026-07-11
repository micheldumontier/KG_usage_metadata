# Adversarial review — SPARQL-log KG usage-metadata manuscript

Written as a hostile SWJ reviewer, deliberately probing for holes rather than
crediting strengths. Findings are severity-ordered. `[VERIFIED]` = checked against
the actual data/scripts in this repo; `[ANALYTICAL]` = argued from the text/method.
Line numbers refer to `manuscript/texsupport.iospress-sw-master/main.tex`.

Note: the three most recently added analyses (concentration, adoption, template
linkage) receive the harshest scrutiny here precisely because they are new and
unreviewed. The first finding invalidates one of them as written.

---

## CRITICAL

### C1. The template-linkage result for Bio2RDF is an artifact of degenerate queries `[VERIFIED]`
**Where:** §"Which Query Templates Drive Coverage" (`main.tex:826–830`), claim
"just **2** of 438 templates account for 80% of organic queries … the ten most
frequent templates carry 90% of query volume yet introduce only 75% of the distinct
queried classes."

**Attack:** A "template" is defined as the *predicate signature* (set of schema
predicates). I recomputed the Bio2RDF organic-2019 signatures directly:

| template | share of valid unique queries |
|---|---|
| `{rdf:type}` only | 43.3% (3,525) |
| **`{}` — no schema predicate at all** | **43.2% (3,516)** |
| everything else | 13.5% |

The "2 templates covering 80%" are the **empty signature** and **`rdf:type`-only**.
The empty-signature bucket is not a template in any meaningful sense — it is every
query that references *no schema predicate*: endpoint default-sample queries
(`select * where {[] a ?Concept} LIMIT 100`), liveness probes
(`select ?s where {?s ?p ?o} limit 1`), and Virtuoso-internal `OPTION(RVR)` /
`OPTION(BREAKUP)` test queries against `no-such-g-qazxswedc` IRIs. The `rdf:type`
bucket is largely the *introspection* query above, whose type is a **variable**, so
it references no specific class either. So the headline "2 templates drive 80% of
volume, but breadth comes from the tail" is manufactured by two degenerate buckets
that contribute (almost) no classes — not by a real finding about how humans query.
"the ten most frequent templates … introduce only 75% of classes" is driven by the
same empty/introspection buckets carrying volume but no schema.

**Wikidata is *not* similarly degenerate `[VERIFIED]`:** I ran the same check on the
858,969 Wikidata organic valid uniques — the empty-signature bucket is only **2.5%**,
and the top template is 9.0% (a Blazegraph `gas:` graph-service example), i.e. a
genuinely flat, diverse distribution. So the manuscript's marquee cross-KG contrast —
"**two templates** driving most Bio2RDF volume **versus thousands** for Wikidata … is
itself a signature of modeling style" (`:829`) — is **not valid**: the "2" is a
degeneracy artifact (empty + introspection buckets), while the "thousands" is real.
The two sides of the contrast are measured on incomparable footing, so the
modeling-style punchline collapses once Bio2RDF is cleaned. (One minor Wikidata
aside: the top template being a `gas:` example query is itself mild
example-contamination, consistent with §example-contamination.)

**Fix:** Exclude queries with an empty predicate signature (and variable-only
`rdf:type` introspection) *before* the template analysis, re-run **both** KGs, and
report the excluded fraction. Re-examine whether the Bio2RDF story survives on
genuine schema-bearing queries at all (far fewer than 8,140), and drop or re-derive
the "2 vs thousands = modeling style" claim. Also stop calling the predicate
signature a template "in the spirit of Asprino" (see M4).

### C2. "Bio2RDF organic-2019" is heavily automated/non-informative traffic, undisclosed `[VERIFIED]`
**Where:** Dataset framing throughout (`:143`, `:198` "organic queries reflect
end-user behavior … typically representative of human users"); all Bio2RDF
organic-2019 numbers (coverage 21.3%, Table 5; concentration Gini 0.90, Table 12;
rarefaction 116 elements, Table 8).

**Attack:** ~43% of the *valid* organic-2019 unique queries reference no schema at
all — they are default-sample/probe/Virtuoso-internal queries (see C1). The paper
carefully documents infrastructure contamination for the **2013** raw log (Table 11:
Virtuoso-internal 24%, LSQ-harvest 22%) and example-query contamination for
**Wikidata** (§example-contamination), but says **nothing** about the same problem
in the 2019 organic log it treats as human. Calling this set "human/end-user
behavior" is not supported.

**Scope (in fairness):** this does *not* mechanically inflate coverage/concentration
— probe queries contribute zero used elements, so the 21.3% and the Gini are
computed off the schema-bearing minority. The damage is interpretive: every
sentence describing Bio2RDF organic-2019 as "human" behavior, and every
organic/robotic behavioral contrast on Bio2RDF-2019, is undermined.

**Fix:** Disclose the composition of the 2019 organic log (as done for 2013), filter
the non-informative queries, and re-state how many genuine human queries remain.

---

## MAJOR

### M1. The class↔template correlation is partly mechanical `[ANALYTICAL]`
**Where:** `:829`, "Spearman correlation between a class's query frequency and the
popularity of the most popular template referencing it is positive in both KGs
(ρ = 0.23 / 0.34) … median bottom-decile class reached via a template used once /
22 times vs. top-decile 3,525 / 17,472."

**Attack:** These two quantities are not independent by construction. A class used
in *k* queries can only appear in templates whose popularity is ≥ the number of
those *k* queries sharing its signature; a class queried once *cannot* have a
max-template-popularity below 1 and is very likely reached only through a rare
template. So ρ>0 and the decile gap are substantially guaranteed by the definitions,
not discovered. No null model is offered.

**Fix:** Report a permutation/null baseline (shuffle class→template membership
preserving marginals) and show the observed ρ exceeds it, or drop the causal reading
("rare classes *are reached through* specialised templates").

### M2. "Adoption dynamics" rests on a proxy and a near-tautology `[ANALYTICAL]`
**Where:** §adoption paragraph (`:723`), "68 predicates present in the 2018 dump but
absent from the 2017 dump … none reaches the top 100."

**Attack:** (a) "newly introduced" is operationalised as *newly appearing in the
extracted predicate set* (931→991), which conflates a genuinely new Wikidata
property with one that merely first appeared in a triple between the two dumps — the
extraction is data-driven, not Wikidata's property-creation log. (b) *n*=68 is tiny.
(c) "brand-new predicates don't crack the top-100 within a year" is close to a
tautology given a heavy-tailed popularity distribution — of course items introduced
at *t* are not yet the most-queried at *t*+1. The finding risks being unfalsifiable.

**Fix:** Anchor "introduced" to Wikidata property-creation timestamps (available via
the property's creation revision), and frame the result as an *upper bound on
adoption speed* rather than a discovery. The Bio2RDF Release-2→3 version (1,357 added,
9% ever queried) is stronger and should lead.

### M3. Cross-dataset Gini/evenness comparison is confounded by N `[ANALYTICAL]`
**Where:** Table 12 + text (`:709–730`), comparing Gini 0.90 (Bio2RDF organic,
N=116) to 0.99 (Wikidata robotic, N=59,603) as if commensurable, and computing all
metrics over *used-only* elements.

**Attack:** (a) Gini and Pielou J are sensitive to N and to the number of
singletons; comparing an N=116 distribution to an N=60,000 one and reporting a single
"Gini 0.90–0.99 everywhere" range invites a spurious cross-KG reading. (b) Computing
concentration over *used* elements only excludes the vast unused mass — but coverage
(the thing this is meant to complement) is precisely about that unused mass.
Concentration over the full schema universe (with zeros) would be far higher and
arguably the more honest denominator; at minimum both should be reported.

**Fix:** State that Gini is compared *within* a KG (as coverage already is), add a
note on N-sensitivity, and report concentration over the full schema universe
alongside the used-only version.

### M4. Predicate-signature "template" discards all query structure; "spirit of Asprino" overclaims `[ANALYTICAL]`
**Where:** `:826`, "a coarser but fully reproducible relative of the Asprino
templates."

**Attack:** A predicate signature ignores join shape, variable structure, filters,
aggregation, and ordering — exactly what Asprino et al.'s templates capture. Two
structurally unrelated queries with the same predicates are one "template," and (per
C1) all schema-less queries collapse to a single bucket. This is a *predicate co-use*
analysis, not a template analysis; the Asprino framing invites a comparison the
method cannot support.

**Fix:** Rename to "predicate co-occurrence signatures," drop the Asprino lineage
claim (or actually adopt a structural template notion), and scope the conclusions
accordingly.

### M5. Wilcoxon significance at N=13k–60k is uninformative `[ANALYTICAL]`
**Where:** `:735–741`, "statistic 126,884,288.5 (p-value = 0.000)" etc.

**Attack:** With tens of thousands of paired elements, any non-zero systematic
difference yields p≈0; the test confirms sample size, not a meaningful effect. The
paper itself concedes this logic for the rarefaction residual ("with n=1.28M the
tiny residual is statistically distinguishable from 1.0 … negligible") but still
presents Wilcoxon p=0.000 as if informative. Reporting "p = 0.000" is also
statistically improper phrasing.

**Fix:** Lead with an effect size (e.g., median per-element change, or a
standardized effect), report p<10⁻³ rather than 0.000, and de-emphasise significance
at these N.

---

## MODERATE

### Mo1. Coverage denominator for Wikidata is a modeling artifact `[ANALYTICAL]`
Wikidata TSE ≈ 103,355 "classes" = every item ever an object of P31/P279, so the
coverage percentage is largely definitional and the "14%" is an artifact of how the
denominator is drawn. The paper defends this well (class/value split §classvalue;
singleton-validity check `:590`), and concedes cross-KG %s aren't comparable — but a
reviewer will still argue the headline coverage number is not a KG-intrinsic
quantity. Consider leading with the class-position/instantiated-class coverage rather
than the raw figure.

### Mo2. Rarefaction assumes independent element occurrences `[ANALYTICAL]`
Individual-based rarefaction (`:547`) treats each schema-element occurrence as an
independent draw. Query traffic is bursty and correlated (the same client repeats
similar queries), violating the independence Hurlbert's estimator assumes, which can
bias the expected-richness curve. The dedup-to-unique-queries step mitigates but does
not remove this. Add a caveat; the 1.79× Bio2RDF effect is large enough to survive,
but the Wikidata 1.03× is close enough that the assumption matters.

### Mo3. Live 2024 endpoint as schema reference is non-reproducible `[ANALYTICAL]`
The Bio2RDF schema is extracted from the live endpoint (`:164`), which drifts, so the
exact TSE/coverage numbers are not reproducible from the paper alone. Mitigated by
shipping the extracted schema CSVs — but state explicitly that the frozen artifacts,
not the live endpoint, are the reproducible reference.

### Mo4. Utility experiment: weak baseline and expected autocorrelation `[ANALYTICAL]`
"Past usage predicts future usage" (§utility) is expected given the demonstrated
stable core; the informative comparison is beating KG-supply, which it does. But the
only baseline is supply; add a random baseline and ideally a recency/frequency hybrid,
and acknowledge that deduplicated demand may not be what a real autocomplete
optimises (which is volume-weighted).

### Mo5. DBpedia carries a strong generalization claim on thin evidence `[ANALYTICAL]`
The "modeling style, not size" conclusion (abstract, `:940`, generality table) leans
heavily on a single DBpedia snapshot and one number (6.5% value-only). Now framed as
exploratory (good), but the third-KG evidence is a table, not an analysis of
comparable depth to Bio2RDF/Wikidata.

---

## MINOR

- **Mi1. Abstract/conclusion inconsistency `[VERIFIED]`:** abstract says organic
  coverage "13--21%" (`:91`), conclusion says "14--21%" (`:940`); the actual table-5
  low end is **12.84%** (Wikidata organic-2017), so both ranges misstate it. Pick one
  and match the table.
- **Mi2. Multiple comparisons uncorrected `[ANALYTICAL]`:** many tests (Shapiro,
  Wilcoxon, Spearman across pairs, several bootstraps) with no family-wise correction
  mentioned.
- **Mi3. Concentration "about six elements" cherry-picks `[VERIFIED]`:** `:721` cites
  ~1% ≈ 6 elements, which is the 2019 figure (P80=1.13%×529≈6); the 2013 figure is
  2.84%×317≈9. Say "6–9" or cite per-row.
- **Mi4. "9.4% of classes reachable only via singleton templates" (Bio2RDF)** is
  computed on the same contaminated query set as C1 and should be recomputed after
  filtering.

---

## Bottom line
The core contributions — coverage metric, rarefaction size-control, the
class-vs-value / content–demand-inversion insight, and the utility forecast — are
solid and well-defended, and the class-value work is genuinely strong. The
**vulnerable surface is the three newest analyses**: the template-linkage result
(C1/M1/M4) is the weakest and, for Bio2RDF, currently invalid as written; the
adoption result (M2) is a proxy-based near-tautology; the concentration result (M3)
is fine but needs N-caveats and a full-universe variant. C2 (undisclosed 2019 organic
contamination) is the most consequential validity issue for the paper as a whole and
is independent of the new analyses. None of these is fatal to the paper, but C1, C2,
and M1 should be fixed before resubmission because a careful reviewer *will* find them.

---

## Resolution log (fixes applied)

- **C1 — FIXED.** Template analysis now excludes schema-less queries and restricts to a
  schema-predicate signature. Corrected numbers: Bio2RDF 86.9% of "organic" queries are
  schema-less (excluded), leaving 1,065; **25** signatures (not 2) cover 80%. Wikidata
  23.1% excluded, leaving 660,672; **1,078** (not 3,179) cover 80%. Section retitled
  "Which Queries Reach Rare Classes"; the bogus "2 vs thousands = modeling style" claim
  is removed; the diversity contrast (31,495 vs 174 distinct signatures) is kept.
- **C2 — FIXED.** New paragraph "What the Bio2RDF organic-2019 log actually contains"
  (§4.5) discloses the 86.9% schema-less composition and scopes the "human" reading;
  notes it does not inflate coverage/concentration (probes contribute zero elements).
- **M1 — FIXED.** Added a mechanical-coupling control: max-signature-popularity is
  strictly greater than the class's own frequency for 84% (Bio2RDF) / 99% (Wikidata) of
  classes, median ratio 109× / 5,407×, so the ρ (0.14 / 0.40) is not the arithmetic floor.
- **M2 — FIXED.** Adoption reframed as an upper bound; leads with the documented Bio2RDF
  R2→R3 result; the Wikidata dump-diff is flagged as a proxy (appearance ≠ creation), n=68
  noted, precise creation-timestamp study deferred.
- **M3 — FIXED.** Table 12 now also reports full-universe Gini*/J* (unused elements as
  zeros; 0.95–0.996); text adds an explicit within-KG / N-sensitivity caveat.
- **M4 — FIXED.** Renamed to "predicate co-occurrence signature"; dropped the Asprino-
  template equivalence claim; explicitly lists what the notion discards.
- **M5 — FIXED.** Wilcoxon "p = 0.000" → "p < 10⁻³"; added a paragraph that significance
  at N=13k–60k is uninformative and points to effect-oriented analyses.
- **Mo2 — FIXED.** Added the rarefaction independence-assumption caveat.
- **Mo3 — FIXED.** Stated the frozen extracted schema (not the live endpoint) is the
  reproducible reference.
- **Mo4 — FIXED.** Utility section now states the random baseline (≈k/N, <3% at top-1000),
  acknowledges usage autocorrelation, and notes the volume-weighted variant.
- **Mi1 — FIXED.** Conclusion "14–21%" → "13–21%", matching the abstract.
- **Mi3 — FIXED.** "about six" → "six to nine (1–3%)".
- **Mi4 — FIXED.** Recomputed on the filtered set (7.3%); folded into the rewritten section.
- **Mo1, Mo5 — not changed.** Judged already adequately defended (class/value split;
  exploratory-scope framing added previously); left for co-author discretion.

Rebuilt clean: main.pdf, 33 pages, no undefined refs. Scripts updated:
`template_linkage.py` (filter + control), `concentration_metrics.py` (full-universe);
outputs in `out/template_linkage_*_filtered.txt`, `out/concentration_metrics.csv`.
