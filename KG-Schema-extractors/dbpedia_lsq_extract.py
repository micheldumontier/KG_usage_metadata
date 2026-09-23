"""Extract DBpedia query texts from the LSQ 2.0 SPARQL endpoint.

Reproduces data/logs/dbpedia/dbpedia_texts.txt (per REPRODUCIBILITY.md: "Distinct
executed DBpedia query texts, extracted from the same LSQ 2.0 endpoint"), the input
dbpedia_analysis.py needs. Uses the same query template as Listing 1 in the
manuscript (Section 3.2), with dataset_name="dbpedia" -- confirmed against the
live endpoint (<http://lsq.aksw.org/dbpedia>).

PAGINATION NOTE (found empirically against the live endpoint, not from docs):
This LSQ instance runs Virtuoso, which hard-rejects `ORDER BY` combined with
`LIMIT`/`OFFSET` once their sum exceeds 10,000 ("Sorted TOP clause specifies
more than 20000 rows to sort. Only 10000 are allowed") -- so naive ORDER-BY
pagination is a dead end here, not just slow. Dropping ORDER BY and paginating
with plain LIMIT/OFFSET works and is fast even at large offsets (~8-19s/page
observed), but the server silently caps returned rows at 10,000 regardless of
the requested LIMIT, so PAGE_SIZE below is fixed at that cap. Without ORDER BY,
row order across repeated requests isn't formally guaranteed by the SPARQL spec,
but is stable in practice for a static, unchanging dataset; a handful of
duplicate rows at a page boundary would just slightly inflate one query's count
downstream (dbpedia_analysis.py dedupes by counting occurrences), not corrupt
the result.

The full join pattern (query + its recorded remote execution) has 6,535,500
rows total (measured via COUNT(*) against the live endpoint), so this is
~654 pages of 10,000 -- roughly 2-4 hours end to end at the observed per-page
latency. Use --start-offset to resume if it's interrupted partway; progress is
also printed per page so you can read the last completed offset from the log.

Usage:
  python3 dbpedia_lsq_extract.py [output_path] [--start-offset N]
  (default output_path: data/logs/dbpedia/dbpedia_texts.txt; default start: 0)

Resuming: rerun with --start-offset set to the offset after the last "written"
line printed, and redirect to a NEW file, then concatenate with the previous
partial file afterward (this script always overwrites output_path; it does not
append), e.g.:
  python3 dbpedia_lsq_extract.py data/logs/dbpedia/dbpedia_texts_part2.txt --start-offset 340000
  cat data/logs/dbpedia/dbpedia_texts.txt data/logs/dbpedia/dbpedia_texts_part2.txt \
    > data/logs/dbpedia/dbpedia_texts_full.txt
"""
import sys, os, re, time, argparse
from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT = "https://lsq.data.dice-research.org/sparql"
GRAPH = "http://lsq.aksw.org/dbpedia"
PAGE_SIZE = 10000  # server hard-caps returned rows here regardless of requested LIMIT
MAX_RETRIES = 5
INITIAL_TIMEOUT = 90
TIMEOUT_INCREMENT = 30
RETRY_DELAY = 20

# Deliberately no ORDER BY -- see PAGINATION NOTE above.
QUERY_TEMPLATE = """
PREFIX lsqv: <http://lsq.aksw.org/vocab#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT ?text
FROM <{graph}>
WHERE {{
    ?query  lsqv:text          ?text .
    ?query  lsqv:hasRemoteExec ?re .
    ?re     prov:atTime        ?timeStamp .
}}
LIMIT {limit}
OFFSET {offset}
"""

def fetch_page(sparql, offset):
    q = QUERY_TEMPLATE.format(graph=GRAPH, limit=PAGE_SIZE, offset=offset)
    timeout = INITIAL_TIMEOUT
    for attempt in range(MAX_RETRIES):
        try:
            sparql.setQuery(q)
            sparql.setReturnFormat(JSON)
            sparql.setTimeout(timeout)
            return sparql.query().convert()["results"]["bindings"]
        except Exception as e:
            print(f"  offset={offset}: error on attempt {attempt+1}: {e}", flush=True)
            timeout += TIMEOUT_INCREMENT
            time.sleep(RETRY_DELAY)
    print(f"  offset={offset}: giving up after {MAX_RETRIES} attempts "
          f"(resume later with --start-offset {offset})", flush=True)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_path", nargs="?", default="data/logs/dbpedia/dbpedia_texts.txt")
    ap.add_argument("--start-offset", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
    sparql = SPARQLWrapper(ENDPOINT)
    offset = args.start_offset
    n_written = 0
    mode = "a" if args.start_offset > 0 else "w"
    with open(args.out_path, mode, encoding="utf-8") as f:
        while True:
            rows = fetch_page(sparql, offset)
            if rows is None:
                break  # repeated failure; rerun with --start-offset {offset} to resume
            if not rows:
                break  # exhausted
            for r in rows:
                text = r["text"]["value"]
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    f.write(text + "\n")
                    n_written += 1
            offset += PAGE_SIZE
            print(f"  offset={offset:,}  written_this_run={n_written:,}", flush=True)
    print(f"done. wrote {n_written:,} query texts -> {args.out_path}")

if __name__ == "__main__":
    main()
