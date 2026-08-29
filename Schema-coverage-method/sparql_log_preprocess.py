#!/usr/bin/env python3
"""
Clean, reproducible pipeline: raw SPARQL query log  ->  used-schema-element usage.

Despite its origin as a Bio2RDF-2019 script (and its former name,
parse_validate_bio2rdf2019.py, which review correctly flagged as misleading), this is the
general preprocessing and validation path used for *all three* KGs in the paper. The
Wikidata and DBpedia analyses in KG-Usage-analysis/ import it for `normalize_ws`,
`add_prefixes`, `clean` and `HTTP_TAIL`; only the CSV-streaming entry point below is
Bio2RDF-log-specific.

It replaces the notebook chain (Schema_coverage_calculation_BIO2RDF.ipynb) with a
single, streaming, parameterized command. It addresses the issues found in that chain:

  * NUL-safe, quote/newline-safe CSV streaming (the raw log has embedded newlines,
    commas, '""'-escaped quotes, and a few stray NUL bytes that crash naive readers).
  * No semantically-corrupting string hacks. In particular we do NOT rewrite '<>' to
    '?class' (that turns a constant into a variable). Relative IRIs are handled by
    giving the parser a base IRI instead.
  * Full percent-decoding (urllib unquote), not just '%3A' -> ':'.
  * HTTP request parameters accidentally appended to the query text
    (e.g. '...&format=text/html&timeout=0&run=Run Query') are stripped.
  * Standard prefixes are added only when a prefix is *used but not declared*,
    so we never duplicate or shadow a query's own PREFIX declarations.
  * A real SPARQL 1.1 parser (rdflib) is used for validation, and schema elements are
    read from the *typed* algebra (URIRef / Variable / Literal / BNode / Path), so the
    fragile ', '-splitting and e_b/g_ blank-node heuristics are gone. Property paths
    (e.g. wdt:P279*) are walked to recover every predicate IRI inside them.

Agent classification follows the paper's *effective* rule (which differs from the
keyword list stated in the methods): organic = browser UA; none = empty UA;
robotic = everything else. Use --strict-robotic to require the stated keyword list.

Usage:
  python3 sparql_log_preprocess.py \
      --log   data/logs/bio2rdf_2019-2021.csv \
      --schema generated-usage-metadata/schema-Bio2RDF-26Subgraphs.csv \
      --agent organic --out out/bio2rdf2019_organic

Outputs (per run):
  <out>_used_schema_elements.csv   element,TotalCount   (unique-query occurrence counts)
  <out>_summary.json               record/unique/valid/coverage stats
"""
import argparse, csv, json, os, re, sys, urllib.parse
from collections import Counter
from multiprocessing import Pool

csv.field_size_limit(sys.maxsize)

# ----- agent classification ------------------------------------------------
BROWSER = re.compile(r'mozilla|chrome|safari|firefox|edge|opera', re.I)
ROBOT_KW = re.compile(r'apache|httpclient|crawler|sparqlwrapper|python|java|wget|curl|bot', re.I)

def classify_agent(agent, strict):
    a = (agent or "").strip()
    if not a:
        return "none"
    if BROWSER.search(a):
        return "organic"
    if strict:
        return "robotic" if ROBOT_KW.search(a) else "unknown"
    return "robotic"

# ----- preprocessing (safe) -------------------------------------------------
STD_PREFIXES = {
    "rdf":     "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":    "http://www.w3.org/2000/01/rdf-schema#",
    "owl":     "http://www.w3.org/2002/07/owl#",
    "xsd":     "http://www.w3.org/2001/XMLSchema#",
    "foaf":    "http://xmlns.com/foaf/0.1/",
    "dc":      "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "skos":    "http://www.w3.org/2004/02/skos/core#",
    "schema":  "http://schema.org/",
    "geo":     "http://www.w3.org/2003/01/geo/wgs84_pos#",
}
# Trailing HTTP query-string parameters leaked into the query text by the log capture
# (queries were submitted as GET /sparql?query=<SPARQL>&format=...&timeout=...&callback=...).
# We strip a *trailing chain* of one-or-more '&key=value' segments anchored to the end of
# the string. Anchoring to the end (rather than the first '&key=') avoids corrupting IRIs
# that legitimately contain '&...=' mid-query. The SPARQL logical-AND '&&' is never matched
# because a key must start with a letter immediately after a single '&'.
HTTP_TAIL = re.compile(r'(?:&[A-Za-z_][\w.\-]*=[^&]*)+\s*$', re.S)
PREFIX_DECL = re.compile(r'\bPREFIX\s+([A-Za-z][\w.\-]*)\s*:', re.I)
PNAME_USE   = re.compile(r'(?<![<\w])([A-Za-z][\w.\-]*):')  # prefixed-name usage

def normalize_ws(q):
    return re.sub(r'\s+', ' ', q).strip()

def clean(query):
    """STAGE 1 (run first, before deduplication): turn a raw logged query string into a
    canonical cleaned query -- full percent-decoding, removal of the trailing HTTP
    query-string parameter chain, and whitespace normalization. Because deduplication is
    performed on this cleaned form, queries that differ only in appended HTTP parameters
    (e.g. &format=, &timeout=, &callback=) collapse into a single unique query."""
    q = urllib.parse.unquote(query)          # full percent-decoding
    q = HTTP_TAIL.sub('', q)                 # drop appended HTTP query-string params
    return normalize_ws(q)                   # whitespace normalization

# Virtuoso (the Bio2RDF endpoint engine) namespaces for its built-in functions.
VIRTUOSO_PREFIXES = {
    "bif": "http://www.openlinksw.com/schemas/bif#",
    "sql": "http://www.openlinksw.com/schemas/sql#",
}
# Virtuoso syntax extensions that standard SPARQL parsers reject.
_V_DEFINE = re.compile(r'\bDEFINE\s+[\w:]+\s+(?:"[^"]*"|<[^>]*>|\S+)\s*', re.I)
_V_OPTION = re.compile(r'\bOPTION\s*\((?:[^()]|\([^()]*\))*\)', re.I)   # 1 level of nesting
_V_PARAM  = re.compile(r'\?:(?=\w)')                                    # ?:name  ->  ?name
# LIKE *operator* only: an operand (variable or ')') then LIKE then a quoted string.
# (Avoids matching the English word "like" in injected blog-spam log entries.)
_V_LIKE   = re.compile(r'(?i)((?:\?\w+|\))\s+)LIKE(\s+["\'])')          # operator -> '='

def virtuoso_normalize(q):
    """Rewrite Virtuoso-specific syntax into parseable SPARQL WITHOUT touching the triple
    patterns, so the schema-element references survive. We strip DEFINE pragmas and
    OPTION(...) clauses, map Virtuoso parameters ?:name to plain variables, and turn the
    LIKE operator into '=' (this only affects FILTER expressions, not the BGP). The bif:/
    sql: built-ins are handled by declaring their prefixes in add_prefixes()."""
    q = _V_DEFINE.sub(' ', q)
    q = _V_OPTION.sub(' ', q)
    q = _V_PARAM.sub('?', q)
    q = _V_LIKE.sub(r'\1=\2', q)
    return q

def add_prefixes(q, virtuoso=False):
    """STAGE 2 (parse-prep): optionally apply the Virtuoso-aware rewrite, then prepend
    standard (and, if virtuoso, bif:/sql:) PREFIX declarations the query uses but does not
    declare, so the parser can resolve them."""
    if virtuoso:
        q = virtuoso_normalize(q)
    avail = dict(STD_PREFIXES)
    if virtuoso:
        avail.update(VIRTUOSO_PREFIXES)
    declared = {m.lower() for m in PREFIX_DECL.findall(q)}
    used = {m.lower() for m in PNAME_USE.findall(q)}
    missing = [p for p in avail if p in used and p not in declared]
    header = "".join(f"PREFIX {p}: <{avail[p]}>\n" for p in missing)
    return header + q

def preprocess(query, virtuoso=False):
    """Convenience: full preprocessing of a raw query = clean + parse-prep."""
    return add_prefixes(clean(query), virtuoso)

# ----- parse + typed schema-element extraction ------------------------------
RDF_TYPE  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SUBCLASS  = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
BASE_IRI  = "http://bio2rdf.org/"

def _iris_in_path(path, out):
    """Recover every predicate IRI inside an rdflib property-path object."""
    from rdflib.term import URIRef
    if isinstance(path, URIRef):
        out.add(str(path)); return
    for attr in ("arg", "path"):                       # InvPath / MulPath / NegatedPath
        if hasattr(path, attr):
            _iris_in_path(getattr(path, attr), out)
    if hasattr(path, "args"):                          # SequencePath / AlternativePath
        for a in path.args:
            _iris_in_path(a, out)

def extract_rdflib(query):
    """Return (valid, iri_terms_set, predicates_set, uses_path) using rdflib (SPARQL 1.1,
    strict grammar). Extraction reads the typed algebra."""
    from rdflib.plugins.sparql.parser import parseQuery
    from rdflib.plugins.sparql.algebra import translateQuery
    from rdflib.plugins.sparql.sparql import CompValue
    from rdflib.term import URIRef
    from rdflib.paths import Path
    try:
        algebra = translateQuery(parseQuery(query), base=BASE_IRI).algebra
    except Exception:
        return (False, set(), set(), False)

    triples, uses_path = [], False
    def walk(n):
        nonlocal uses_path
        if isinstance(n, CompValue):
            if n.name == "BGP":
                triples.extend(n["triples"])
            for v in n.values():
                walk(v)
        elif isinstance(n, (list, tuple)):
            for x in n:
                walk(x)
    walk(algebra)
    # CONSTRUCT template triples live outside the WHERE BGP
    if algebra.name == "ConstructQuery" and "template" in algebra:
        tmpl = algebra["template"]
        if isinstance(tmpl, (list, tuple)):
            triples.extend(tmpl)

    iri_terms, predicates = set(), set()
    for t in triples:
        if not (isinstance(t, tuple) and len(t) == 3):
            continue                                   # skip any non-(s,p,o) artifact
        s, p, o = t
        if isinstance(s, URIRef): iri_terms.add(str(s))
        if isinstance(o, URIRef): iri_terms.add(str(o))
        if isinstance(p, URIRef):
            predicates.add(str(p))
        elif isinstance(p, Path):                      # property path (NOT a variable)
            uses_path = True
            _iris_in_path(p, predicates)
        # else: predicate is a Variable/BNode -> not a schema element, ignore
    return (True, iri_terms, predicates, uses_path)

# pyoxigraph: fast, standards-compliant SPARQL 1.1 (Rust). No public AST in Python, so
# this backend reports VALIDITY ONLY (no schema-element extraction). IMPORTANT: Oxigraph's
# only Python entry point is Store.query(), which *evaluates* the query. We therefore (a)
# never iterate the result (so SELECT bodies are not executed) and (b) skip queries that
# contain SERVICE, because evaluating them would trigger live federation/network calls.
# Such queries return validity = None ("not assessed"). This is a real limitation of using
# an execution engine as a validator on logs that contain federated queries.
_OX_STORE = None
_SERVICE_RE = re.compile(r'\bSERVICE\b', re.I)
def extract_pyoxigraph(query):
    global _OX_STORE
    if _SERVICE_RE.search(query):
        return (None, set(), set(), False)            # cannot validate without federating
    from pyoxigraph import Store
    if _OX_STORE is None:
        _OX_STORE = Store()
    try:
        _OX_STORE.query(query)                        # parse/plan only; do NOT iterate
        return (True, set(), set(), False)
    except Exception:
        return (False, set(), set(), False)

_PARSER_FN = None
_VIRTUOSO = False
def _init_pool(parser, virtuoso):
    global _PARSER_FN, _VIRTUOSO
    _PARSER_FN = {"rdflib": extract_rdflib, "pyoxigraph": extract_pyoxigraph}[parser]
    _VIRTUOSO = virtuoso

def _worker(item):
    qtext, count = item                                # qtext is already cleaned (STAGE 1)
    valid, iris, preds, path = _PARSER_FN(add_prefixes(qtext, _VIRTUOSO))
    return (valid, iris, preds, path, count)

def parse_batch_sparqljs(items, workdir, virtuoso=False):
    """Run all preprocessed queries through the Node/sparqljs worker (paper's parser)."""
    import subprocess, json as _json
    node = os.path.expanduser("~/.local/bin/node")
    worker = os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
    inp = "\n".join(_json.dumps(add_prefixes(q, virtuoso)) for q, _ in items) + "\n"  # q cleaned
    proc = subprocess.run([node, worker], input=inp, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"sparqljs worker failed: {proc.stderr[:500]}")
    out = [l for l in proc.stdout.splitlines() if l]
    results = []
    for (q, count), line in zip(items, out):
        r = _json.loads(line)
        results.append((bool(r["v"]), set(r["iris"]), set(r["preds"]), bool(r["path"]), count))
    return results

# ----- schema reference -----------------------------------------------------
VOCAB_IRI = re.compile(r'^http://[Bb]io2[Rr][Dd][Ff]\.org/\w+_vocabulary:')

def load_schema(path):
    """Build the reference (TSE) universe from the (Class1, Predicate, Class2)
    schema-pattern file:
       types      = distinct Bio2RDF '_vocabulary:' class IRIs, excluding ':Resource'
       predicates = distinct IRIs in the Predicate column (incl. rdf:type, subClassOf,
                    owl:sameAs, which the published used-set also contains)
    NOTE: this universe is derived from the committed pattern CSV. The paper's published
    TSE (350 types / 195 predicates) comes from the KG-Schema-extractors run against the
    live endpoint and is NOT byte-reproducible from this file (its predicate column lists
    ~545 distinct vocabulary predicates). Coverage is therefore reported against the
    universe actually provided here; pass a flat one-column element list as --schema to
    override with the canonical TSE when available.
    """
    classes, predicates = set(), set()
    with open(path, newline='') as f:
        head = f.readline()
        f.seek(0)
        if "," in head and ("Predicate" in head or "Class1" in head):
            r = csv.DictReader(f)
            for row in r:
                for c in (row.get("Class1"), row.get("Class2")):
                    if c and VOCAB_IRI.match(c) and not c.endswith(":Resource"):
                        classes.add(c)
                p = row.get("Predicate")
                if p:
                    predicates.add(p)
        else:                                          # flat one-column element list
            r = csv.reader(f); next(r, None)
            for row in r:
                if not row:
                    continue
                el = row[0]
                (classes if el.rstrip("/").split(":")[-1][:1].isupper() else predicates).add(el)
    return classes, predicates

# ----- main -----------------------------------------------------------------
def stream_unique(log_path, agent_filter, strict):
    """Yield (query_text, count) for unique whitespace-normalized queries that match
    the requested agent class. Also returns tallies via the closure dict `stats`."""
    counts = Counter()
    stats = Counter()
    with open(log_path, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader((line.replace('\x00', '') for line in f))
        header = next(reader)
        for row in reader:
            if len(row) != 4:
                stats["malformed"] += 1
                continue
            q, _domain, agent, _ts = row
            stats["records"] += 1
            cls = classify_agent(agent, strict)
            stats[f"agent_{cls}"] += 1
            if agent_filter != "all" and cls != agent_filter:
                continue
            counts[clean(q)] += 1                      # STAGE 1: clean BEFORE dedup
    return counts, stats

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--agent", default="all",
                    choices=["all", "organic", "robotic", "none", "unknown"])
    ap.add_argument("--strict-robotic", action="store_true",
                    help="use the stated keyword rule (else: non-browser, non-empty = robotic)")
    ap.add_argument("--parser", default="rdflib",
                    choices=["rdflib", "pyoxigraph", "sparqljs"],
                    help="rdflib=pure-Python strict + extraction; pyoxigraph=fast Rust, "
                         "VALIDATION ONLY; sparqljs=Node, paper's parser + extraction")
    ap.add_argument("--virtuoso", action="store_true",
                    help="Virtuoso-aware pass: rewrite bif:/sql:/OPTION/DEFINE/LIKE/?: so "
                         "Virtuoso-extension queries parse and contribute schema elements")
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=max(1, os.cpu_count() - 2))
    ap.add_argument("--limit", type=int, default=0, help="cap unique queries (debug)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    print(f"[1/4] streaming + dedup ({args.agent}) ...", flush=True)
    counts, stats = stream_unique(args.log, args.agent, args.strict_robotic)
    items = list(counts.items())
    if args.limit:
        items = items[:args.limit]
    print(f"      records={stats['records']:,} malformed={stats['malformed']:,} "
          f"unique({args.agent})={len(items):,}", flush=True)

    print(f"[2/4] parsing + extracting ({args.parser}) ...", flush=True)
    valid = invalid = path_q = 0
    type_occ, pred_occ = Counter(), Counter()      # unique-query occurrence counts
    classes, predicates = load_schema(args.schema)

    if args.parser == "sparqljs":
        results = parse_batch_sparqljs(items, os.path.dirname(args.out) or ".", args.virtuoso)
    else:
        with Pool(args.procs, initializer=_init_pool, initargs=(args.parser, args.virtuoso)) as pool:
            results = pool.imap_unordered(_worker, items, chunksize=200)
            results = list(results)

    skipped = 0
    for ok, iris, preds, uses_path, _c in results:
        if ok is None:                                 # pyoxigraph: SERVICE, not assessed
            skipped += 1; continue
        if not ok:
            invalid += 1; continue
        valid += 1
        if uses_path: path_q += 1
        for t in iris & classes:   type_occ[t] += 1
        for p in preds & predicates: pred_occ[p] += 1
    if args.parser == "pyoxigraph":
        print("      NOTE: pyoxigraph is validation-only; USE/coverage not extracted.", flush=True)

    print("[3/4] writing used-schema-element counts ...", flush=True)
    used = Counter(); used.update(type_occ); used.update(pred_occ)
    with open(f"{args.out}_used_schema_elements.csv", "w", newline='') as f:
        w = csv.writer(f); w.writerow(["Schema Element", "TotalCount"])
        for el, c in sorted(used.items(), key=lambda x: -x[1]):
            w.writerow([el, c])

    print("[4/4] summary", flush=True)
    TSE = len(classes) + len(predicates)
    USE = len(type_occ) + len(pred_occ)
    summary = {
        "parser": args.parser,
        "virtuoso_aware": args.virtuoso,
        "agent_filter": args.agent,
        "strict_robotic": args.strict_robotic,
        "records": stats["records"],
        "malformed_rows": stats["malformed"],
        "agent_breakdown": {k[6:]: v for k, v in stats.items() if k.startswith("agent_")},
        "unique_queries": len(items),
        "valid": valid, "invalid": invalid, "not_assessed_service": skipped,
        "queries_using_property_path": path_q,
        "used_types": len(type_occ), "used_predicates": len(pred_occ),
        "USE": USE, "TSE": TSE,
        "schema_coverage_pct": round(100.0 * USE / TSE, 2) if TSE else None,
    }
    with open(f"{args.out}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
