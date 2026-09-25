# Knowledge graph usage metadata: Insights from SPARQL log analysis



## Datasets

### RDF Knowledge Graphs (KGs)

- **Wikidata 2017**: [Internet Archive](https://archive.org/download/wikibase-wikidatawiki-20170821)  
- **Wikidata 2018**: [Internet Archive](https://archive.org/download/wikibase-wikidatawiki-20180205)  

Both versions were hosted on Blazegraph on a local server to analyze SPARQL schema coverage changes over time.

- **Bio2RDF SPARQL Endpoint**: [https://Bio2RDF.org/sparql/](https://Bio2RDF.org/sparql/)  

### SPARQL Query Logs

The query logs were retrieved from multiple sources:

- **Linked SPARQL Queries Dataset (LSQ) 2.0**:  
  - **SPARQL Endpoint**: [https://lsq.data.dice-research.org/sparql](https://lsq.data.dice-research.org/sparql)  
  - This dataset contains queries from 24 datasets, including 23 Bio2RDF datasets and one Wikidata dataset.

- **Bio2RDF Query Logs**:  
  - **Dumontier Lab Repository**: [https://download.dumontierlab.com/Bio2RDF/logs/](https://download.dumontierlab.com/Bio2RDF/logs/)  

- **Wikidata Query Logs**:  
  - **International Center for Computational Logic (ICCL)**: [https://iccl.inf.tu-dresden.de/web/Wikidata_SPARQL_Logs/en](https://iccl.inf.tu-dresden.de/web/Wikidata_SPARQL_Logs/en)  
  - This dataset includes all queries and organic queries for **Interval 1** and **Interval 7**.

## Calculating Schema Coverage and Usage Analysis

**SPARQL Schema Coverage (SC)** is:  
\[
SC (\%) = \left( \frac{USE}{TSE} \right) \times 100
\]
where **TSE** (Total Schema Elements) is all distinct types and predicates in the KG, and
**USE** (Used Schema Elements) is the subset found in user SPARQL queries.

1. **Extract all schema elements** — run the code in **`KG-Schema-extractors`** (both KGs).
2. **Extract used schema elements and compute coverage**:
   - **Bio2RDF** — `Schema-coverage-method/sparql_log_preprocess.py`.
   - **Wikidata** — `KG-Usage-analysis/wd_coverage.py` (`Schema-coverage-method/sparql_log_preprocess.py`
     is still used as a shared library here for query cleanup/normalization, but the Wikidata
     entry point itself lives in `KG-Usage-analysis`, not `Schema-coverage-method`).

To perform the **usage pattern analysis** as proposed in the paper, run the rest of the code in
**`KG-Usage-analysis`**. See `REPRODUCIBILITY.md` for exact commands, inputs, and which script
produced each published number.


The **generated usage metadata** for **Bio2RDF** and **Wikidata** KGs can be found in the **`generated-usage-metadata`** folder. Downstream analyses computed from that metadata (rarefaction,
concentration, utility ranking, etc.) live in **`analysis-results`**, one folder per analysis. Superseded scripts and files are kept, not deleted, in **`archive`**.


## Reproducing the analyses

`REPRODUCIBILITY.md` lists where every input dataset comes from (the ~60 GB under `data/`
is git-ignored), which script produced each figure and table, and the environment quirks
worth knowing about before running anything.

## Manuscript (Overleaf sync)

The LaTeX manuscript lives in `manuscript/texsupport.iospress-sw-master/`, which is a
**git subtree** of the Overleaf-synced repository
[`MaastrichtU-IDS/KG-usage-manuscript`](https://github.com/MaastrichtU-IDS/KG-usage-manuscript)
(the `paper` remote). Overleaf pushes to that repo via its GitHub integration, so it is
the exchange point between Overleaf and this repository.

One-time remote setup, if your clone lacks it:

```sh
git remote add paper https://github.com/MaastrichtU-IDS/KG-usage-manuscript.git
```

**Pull Overleaf edits into this repo:**

```sh
git subtree pull --prefix=manuscript/texsupport.iospress-sw-master paper main --squash
```

**Push manuscript edits from this repo back to Overleaf:**

```sh
git subtree push --prefix=manuscript/texsupport.iospress-sw-master paper main
```

Two things to keep in mind:

- **Always pass `--squash` when pulling.** The subtree was established with `--squash`, and
  mixing squashed and unsquashed history on the same prefix causes spurious conflicts.
- **A push lands directly in the live Overleaf project**, where co-authors may be editing.
  Coordinate before pushing, and pull first.

Review comments belong **in this repository** (as plain text files under `manuscript/`, e.g.
`manuscript/reviews.txt`, `manuscript/review2.txt`) rather than in Overleaf's commenting
sidebar. Overleaf comments are not part
of the document source and therefore never reach git, so they are invisible to anyone
working from a clone.

### Building the manuscript

There is no need for a full TeX Live install; TinyTeX is sufficient:

```sh
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
cd manuscript/texsupport.iospress-sw-master
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

To produce a change-marked PDF against another revision (e.g. the last state synced from
Overleaf), note that `latexdiff` needs `tabular` blocks treated atomically or the markup it
inserts around `\hline` breaks the tables:

```sh
git show paper/main:main.tex > /tmp/baseline.tex
latexdiff --type=UNDERLINE \
  --config="PICTUREENV=(?:picture|DIFnomarkup|tabular)[\w\d*@]*" \
  /tmp/baseline.tex main.tex > main_diff.tex
pdflatex main_diff && bibtex main_diff && pdflatex main_diff && pdflatex main_diff
```
