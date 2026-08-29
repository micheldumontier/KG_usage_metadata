"""Query-template / coverage linkage (missing-analysis #3, reviewer's Asprino point).

We define a query's *template* as its predicate signature: the sorted set of
schema predicate IRIs it references (property-path member IRIs included). Two
queries with the same predicates instantiate the same template family. This is a
coarser, fully reproducible relative of the Asprino et al. templates, and it is
enough to answer the reviewer's two questions:
  (a) which templates drive schema coverage?  -> rank templates by unique-query
      frequency; contrast their share of query VOLUME with their share of the
      distinct schema elements (BREADTH) they introduce.
  (b) are rare classes reached through specialized templates?  -> for each
      class-position element, relate its query frequency to the popularity of the
      templates that reference it (Spearman), and measure how much breadth is
      contributed by singleton (used-once) templates.

Run: python3 KG-Usage-analysis/template_linkage.py [bio2rdf|wikidata|both]"""
import csv, gzip, sys, json, os, subprocess, tempfile, glob, urllib.parse, re, importlib.util
csv.field_size_limit(sys.maxsize)
spec = importlib.util.spec_from_file_location("pv", "Schema-coverage-method/sparql_log_preprocess.py")
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE = os.path.expanduser("~/.local/bin/node")
WORKER = os.path.expanduser("~/.local/sparqljs-worker/template_worker.js")

def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))

CONFIG = {
    "bio2rdf": {
        "base": "http://bio2rdf.org/",
        "typeprops": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type,"
                     "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "class_ok": lambda iri: "_vocabulary:" in iri,  # Bio2RDF schema types
        "pred_ok":  lambda iri: "_vocabulary:" in iri,  # Bio2RDF schema predicates
    },
    "wikidata": {
        "base": "http://www.wikidata.org/",
        "typeprops": "http://www.wikidata.org/prop/direct/P31,"
                     "http://www.wikidata.org/prop/direct/P279",
        "class_ok": lambda iri: "/entity/Q" in iri,
        "pred_ok":  lambda iri: "/prop/direct/P" in iri,  # wdt:Pxxx direct properties
    },
}

def load_queries(name):
    if name == "bio2rdf":
        out = []
        with open("out/bio2rdf2019_organic_unique_VALID.csv", newline='') as f:
            r = csv.reader(f); h = next(r); qi = h.index("query_cleaned"); ci = h.index("count")
            for row in r:
                if len(row) > qi: out.append((row[qi], int(row[ci]) if row[ci].isdigit() else 1))
        return out, "Bio2RDF organic-2019 (valid uniques)"
    else:
        counts = {}
        for path in sorted(glob.glob("data/logs/wikidata/*_organic.tsv.gz")):
            with gzip.open(path, 'rt', encoding='utf-8', errors='replace') as f:
                r = csv.reader(f, delimiter='\t'); h = next(r); qi = h.index('anonymizedQuery')
                for row in r:
                    if len(row) > qi:
                        k = wclean(row[qi]); counts[k] = counts.get(k, 0) + 1
        return list(counts.items()), "Wikidata organic (pooled 2017-2018 windows)"

def extract(queries, base, typeprops, nw=14):
    prepped = [pv.add_prefixes(q, False) for q in queries]
    chunks = [list(range(i, len(prepped), nw)) for i in range(nw)]
    procs = []
    env = dict(os.environ, BASEIRI=base, TYPEPROPS=typeprops)
    for idxs in chunks:
        ti = tempfile.NamedTemporaryFile('w', suffix='.nd', delete=False)
        for j in idxs: ti.write(json.dumps(prepped[j]) + "\n")
        ti.close(); to = ti.name + ".o"
        procs.append((subprocess.Popen([NODE, WORKER], stdin=open(ti.name), stdout=open(to, 'w'), env=env),
                      ti.name, to, idxs))
    results = [None]*len(prepped)
    for p, ti, to, idxs in procs:
        p.wait()
        for j, line in zip(idxs, open(to)): results[j] = json.loads(line)
        os.remove(ti); os.remove(to)
    return results

def analyze(name):
    import statistics
    cfg = CONFIG[name]
    queries, label = load_queries(name)
    print(f"\n=== {label} : {len(queries):,} unique queries ===", flush=True)
    res = extract([q for q, _ in queries], cfg["base"], cfg["typeprops"])
    tmpl_q = {}        # template -> #unique queries
    tmpl_classes = {}  # template -> set(classes)
    cls_q = {}         # class -> #unique queries referencing it
    cls_tmpls = {}     # class -> set(templates)
    nparsed = schemaless = 0
    typeonly = 0       # queries whose only schema footprint is class(es), no schema predicate
    for (q, _), r in zip(queries, res):
        if not r or not r.get("v"): continue
        nparsed += 1
        # restrict the query's footprint to SCHEMA elements only, then drop queries
        # that reference no schema element at all (endpoint default-sample / liveness /
        # Virtuoso-internal probes, and variable-only rdf:type introspection).
        spreds = tuple(sorted(p for p in r["preds"] if cfg["pred_ok"](p)))
        classes = [c for c in r["classes"] if cfg["class_ok"](c)]
        if not spreds and not classes:
            schemaless += 1; continue
        if not spreds: typeonly += 1
        t = spreds  # template = schema-predicate signature
        tmpl_q[t] = tmpl_q.get(t, 0) + 1
        tmpl_classes.setdefault(t, set()).update(classes)
        for c in set(classes):
            cls_q[c] = cls_q.get(c, 0) + 1
            cls_tmpls.setdefault(c, set()).add(t)
    nvalid = sum(tmpl_q.values())
    nt = len(tmpl_q)
    print(f"parsed valid: {nparsed:,}; schema-less (excluded): {schemaless:,} "
          f"({100*schemaless/max(nparsed,1):.1f}%); schema-bearing (used): {nvalid:,}")
    print(f"  of used, type-assertion only (no schema predicate): {typeonly:,} "
          f"({100*typeonly/max(nvalid,1):.1f}%)")
    print(f"distinct templates (schema-predicate signatures): {nt:,}")
    by_freq = sorted(tmpl_q.items(), key=lambda x: -x[1])
    cum = 0; t80 = 0
    for i, (_, c) in enumerate(by_freq, 1):
        cum += c
        if cum >= 0.8*nvalid: t80 = i; break
    print(f"templates covering 80% of schema-bearing queries: {t80} ({100*t80/max(nt,1):.2f}% of templates)")
    allcls = set().union(*tmpl_classes.values()) if tmpl_classes else set()
    top10 = by_freq[:10]
    vol10 = sum(c for _, c in top10)
    cls10 = set().union(*[tmpl_classes[t] for t, _ in top10]) if top10 else set()
    print(f"distinct class-position elements overall: {len(allcls):,}")
    print(f"top-10 templates: {100*vol10/nvalid:.1f}% of query volume, "
          f"but only {100*len(cls10)/max(len(allcls),1):.1f}% of distinct classes")
    singleton_t = {t for t, c in tmpl_q.items() if c == 1}
    cls_only_singleton = [c for c, ts in cls_tmpls.items() if ts <= singleton_t]
    print(f"singleton templates (used by exactly 1 query): {len(singleton_t):,} "
          f"({100*len(singleton_t)/max(nt,1):.1f}% of templates)")
    print(f"classes reachable ONLY via singleton templates: {len(cls_only_singleton):,} "
          f"({100*len(cls_only_singleton)/max(len(allcls),1):.1f}% of distinct classes)")
    # association class-frequency vs popularity of its most-popular template
    xs, ys = [], []
    for c, ts in cls_tmpls.items():
        xs.append(cls_q[c]); ys.append(max(tmpl_q[t] for t in ts))
    rho = spearman(xs, ys)
    print(f"Spearman(class query-frequency, max template popularity) = {rho:.3f} (n={len(xs):,})")
    paired = sorted(zip(xs, ys))
    k = max(len(paired)//10, 1)
    rare = [y for _, y in paired[:k]]; freq = [y for _, y in paired[-k:]]
    print(f"median max-template-popularity: bottom-decile classes={statistics.median(rare):.0f}, "
          f"top-decile classes={statistics.median(freq):.0f}")
    # M1 mechanical-coupling control: is max-template-popularity merely >= class freq,
    # or does the class ride templates popular for OTHER queries too?
    ratios = [y/x for x, y in zip(xs, ys) if x > 0]
    strictly_gt = sum(1 for x, y in zip(xs, ys) if y > x)
    print(f"  control: median(max-template-pop / class-freq) = {statistics.median(ratios):.1f}x; "
          f"class's top template strictly more popular than the class itself in "
          f"{100*strictly_gt/max(len(xs),1):.1f}% of classes")

def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0]*len(v); i = 0
        while i < len(v):
            j = i
            while j+1 < len(v) and v[order[j+1]] == v[order[i]]: j += 1
            avg = (i+j)/2 + 1
            for k in range(i, j+1): r[order[k]] = avg
            i = j+1
        return r
    rx, ry = rank(x), rank(y); n = len(x)
    mx = sum(rx)/n; my = sum(ry)/n
    num = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    den = (sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))**0.5
    return num/den if den else float('nan')

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    for name in (["bio2rdf", "wikidata"] if which == "both" else [which]):
        analyze(name)
