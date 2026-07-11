Overall, I think this is a strong Semantic Web Journal paper. It addresses a genuine gap in the SPARQL log literature: most previous work focuses on query syntax, shapes, optimization, or templates, whereas this paper asks a more fundamental question: *what parts of a knowledge graph are actually being used?* The notion of "usage metadata" derived from query logs is interesting, practically relevant, and potentially reusable across many KGs. 

That said, there are several areas where reviewers are likely to challenge the paper.

## Major strengths

### 1. Clear research contribution

The paper moves beyond query-structure analysis and introduces:

* schema coverage metrics,
* usage frequency distributions,
* organic vs robotic comparisons,
* rarefaction-based normalization,
* demand-vs-supply analysis,
* predictive use of usage metadata.

This is substantially more than an incremental extension of earlier Bio2RDF work. The rarefaction analysis is particularly important because it prevents obvious criticisms regarding unequal query volumes. 

### 2. Strong methodological rigor

The paper anticipates several methodological objections:

* query preprocessing is carefully described,
* schema extraction is formalized,
* explicit-reference vs closure-based usage is discussed,
* non-normality is tested before selecting Wilcoxon,
* ranking stability is assessed separately using Spearman.

This level of methodological transparency is often missing from SPARQL log papers.

### 3. Important conceptual finding

The most interesting result is arguably not the coverage numbers themselves, but the discovery that "schema coverage" means something fundamentally different in item-centric KGs such as Wikidata than in OWL-style KGs such as Bio2RDF. The distinction between:

* class-position usage
* value-position usage

is insightful and likely publishable in its own right. 

### 4. Practical relevance

The type-suggestion experiment demonstrates that usage metadata can support downstream applications rather than merely describing logs retrospectively.

That strengthens the paper considerably.

---

# Major concerns

## 1. The notion of "usage" remains too narrow

The paper explicitly defines usage as:

> schema elements explicitly written in queries

and excludes:

* inferred classes,
* transitive closures,
* returned entities,
* answer sets,
* execution statistics.

While the authors justify this choice, reviewers may argue that this is not truly measuring KG usage, but rather **query authoring behavior**. 

For example:

```sparql
?x wdt:P31/wdt:P279* wd:Q5
```

may traverse thousands of classes, yet only three schema elements are counted.

A reviewer may ask:

> Are we measuring what users write, or what parts of the KG are actually utilized during query evaluation?

I would recommend explicitly introducing two notions:

* **syntactic usage** (current work)
* **semantic usage** (future work)

and framing the paper as a study of syntactic usage.

---

## 2. Coverage may not be the most meaningful metric

Coverage implicitly assumes:

> more coverage = more usage

but this is debatable.

Suppose:

* 10 classes account for 95% of all queries
* 10,000 classes are never queried

The coverage metric treats every class equally.

A reviewer could argue that entropy-based or information-theoretic measures would be more informative.

I would suggest adding a discussion of alternative metrics:

* entropy
* Gini coefficient
* concentration indices
* Pareto analysis

especially since the paper already observes long-tail distributions.

---

## 3. Bio2RDF schema extraction is potentially problematic

This is where I expect the toughest reviewer comments.

The paper states that because historical Bio2RDF versions are unavailable:

> the current 2024 endpoint is used as the schema reference for 2013 and 2019 logs. 

This creates a temporal mismatch.

Potential issue:

* a class queried in 2013 may no longer exist in 2024,
* a class introduced after 2013 may inflate the denominator.

This threatens the validity of coverage calculations.

I would strongly recommend:

### Add a sensitivity analysis

For example:

* compute coverage using only elements observed in logs,
* compute coverage using 2024 schema,
* show conclusions remain stable.

Without this, a reviewer could question all Bio2RDF coverage results.

---

## 4. Organic vs robotic distinction is simplistic

The user-agent classification is inherited from previous work, but:

```text
browser => organic
everything else => robotic
```

is an imperfect proxy.

Today:

* notebooks
* APIs
* AI agents
* browser extensions

blur this distinction.

A reviewer may ask:

> Is "robotic" really measuring bots, or merely non-browser clients?

The paper should explicitly acknowledge classification uncertainty.

---

## 5. Limited generalization

Only three KGs appear:

* Bio2RDF
* Wikidata
* DBpedia

DBpedia seems mostly used as a sanity check rather than a full experimental subject.

A reviewer may ask whether findings generalize to:

* OpenAlex
* UniProt
* ChEMBL
* Europeana
* government KGs

The paper would benefit from explicitly positioning itself as an exploratory study across contrasting KG architectures rather than a universal characterization.

---

# Missing analyses that would significantly strengthen the paper

## 1. Query demand versus maintenance cost

You already show:

> content supply ≠ content demand.

A natural next step is:

> which schema elements are expensive to maintain but rarely queried?

This would create a direct bridge to KG governance.

---

## 2. Schema evolution versus query evolution

You compare log intervals and KG versions separately.

A stronger question is:

> Do newly introduced schema elements ever become popular?

This could reveal adoption dynamics.

---

## 3. Query-template linkage

You cite Asprino et al. but don't fully exploit template information.

Interesting analysis:

* which query templates drive schema coverage?
* are rare classes associated with specialized templates?

This would deepen the behavioral interpretation.

---

## 4. Execution-aware usage

Current usage is binary:

```text
referenced / not referenced
```

A useful extension:

```text
referenced
executed
successful
returned results
```

These are very different notions of usage.

---

# Writing and presentation improvements

### Reduce methodological detail in the main text

Sections 3.2–3.5 are extremely detailed.

SWJ reviewers are usually willing to accept technical details in appendices.

I would move:

* pseudocode,
* parser normalization details,
* Shapiro-Wilk equations,

to supplementary material.

The conceptual story would become much clearer.

### Strengthen the discussion section

The most novel ideas emerge late:

* item-based vs OWL-style schemas,
* demand-supply inversion,
* meaning of coverage.

These deserve a dedicated conceptual discussion section rather than appearing as interpretations of results.

---

# What I think SWJ reviewers will say

### Likely positive comments

* Novel perspective on SPARQL logs.
* Careful methodology.
* Valuable large-scale empirical study.
* Interesting findings regarding Wikidata modeling.
* Practical implications for KG maintenance and tooling.

### Likely critical comments

* Coverage metric may not reflect actual KG utilization.
* Historical Bio2RDF schema mismatch.
* Limited number of KGs.
* Overemphasis on coverage percentage.
* Organic/robotic classification may be weak.

---

# My overall assessment

**Novelty:** High
**Technical quality:** Good to very good
**Empirical validation:** Good
**Significance:** High for the SPARQL-log-analysis community
**SWJ fit:** Strong

If I were reviewing it for SWJ, I would likely recommend **minor revision to moderate revision**, with the biggest requested change being a stronger treatment of:

1. the historical Bio2RDF schema mismatch,
2. alternative notions of usage,
3. the conceptual distinction between syntactic and semantic usage.

Those additions would substantially increase the paper's impact and make it harder for reviewers to dismiss the coverage metric as merely a property of query text rather than KG use. 
