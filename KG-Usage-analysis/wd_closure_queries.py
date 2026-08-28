"""Publish the queries behind the closure-bound claim, and report the bound against the
class universe rather than TSE.

Addresses two reproducibility gaps raised in review:

  (a) The manuscript says a "handful of queries" anchored at near-root classes would, under a
      closure-based notion of usage, mark most of the ontology as used. Neither
      wd_closure_bound.py nor wd_closure_anchors.py emitted the actual query texts, so the
      claim could not be checked. This script writes them out.

  (b) The manuscript states the closure would mark ~62% of Wikidata *classes* as used, but
      wd_closure_bound.py reported the closure-derived additions as a percentage of TSE,
      whose denominator mixes classes and predicates. This script reports both denominators
      explicitly so the quoted figure is unambiguous.

Outputs:
  out/wd_closure_anchor_queries.tsv   every organic query anchored at a near-root class
  out/wd_closure_bound_summary.txt    the bound against class-universe and TSE denominators
"""
import csv, gzip, os, urllib.parse, json, subprocess, tempfile, importlib.util
from collections import deque
csv.field_size_limit(1 << 30)
spec = importlib.util.spec_from_file_location("pv", "Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE = os.path.expanduser("~/.local/bin/node")
PAW  = os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD = "data/logs/wikidata"
# Default scope is the 2017 organic log (interval 1), which is the scope of the closure-bound
# claim in Section 3.4. Pass "pooled" as argv[1] to use the three early-2017 windows instead.
import sys
FILES = ([f"{WD}/int1_2017_organic.tsv.gz",
          f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
          f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
         if len(sys.argv) > 1 and sys.argv[1] == "pooled"
         else [f"{WD}/int1_2017_organic.tsv.gz"])

# Near-root anchors: classes so general that crediting their whole subclass closure would
# mark most of the ontology as "used". These are the ones the manuscript's argument rests on.
NEAR_ROOT = {"Q35120": "entity", "Q151885": "concept", "Q488383": "object",
             "Q99527517": "collective entity", "Q23958852": "variable-order class",
             "Q4406616": "concrete object", "Q7184903": "abstract object",
             "Q16686022": "natural object", "Q223557": "physical object"}

def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))

def parallel(prepped, nw=14):
    chunks = [prepped[i::nw] for i in range(nw)]; procs = []
    for ch in chunks:
        ti = tempfile.NamedTemporaryFile('w', suffix='.nd', delete=False)
        for x in ch: ti.write(json.dumps(x) + "\n")
        ti.close(); to = ti.name + ".o"
        procs.append((subprocess.Popen([NODE, PAW], stdin=open(ti.name), stdout=open(to, 'w')), ti.name, to))
    # Results must be returned in the SAME order as `prepped`. Chunks are strided
    # (prepped[i::nw]), so chunk i holds original positions i, i+nw, i+2nw, ...; concatenating
    # the chunks would scramble the mapping and silently misalign any later zip(queries, results).
    out=[None]*len(prepped)
    for i,(p,ti,to) in enumerate(procs):
        p.wait()
        rs=[json.loads(l) for l in open(to)]
        for j,r in enumerate(rs): out[i+j*nw]=r
        os.remove(ti); os.remove(to)
    return out

seen = set()
for path in FILES:
    with gzip.open(path, 'rt', encoding='utf-8', errors='replace') as f:
        r = csv.reader(f, delimiter='\t'); h = next(r); qi = h.index('anonymizedQuery')
        for row in r:
            if len(row) > qi: seen.add(wclean(row[qi]))
qs = list(seen)
print("unique organic queries: %d" % len(qs), flush=True)
res = parallel([pv.add_prefixes(q, False) for q in qs])

# --- (a) emit the queries anchored at each near-root class -------------------------------
rows = []
for q, r in zip(qs, res):
    if not r.get("v"): continue
    hits = [a for a in r.get("anchors", []) if a in NEAR_ROOT]
    for a in hits:
        rows.append((a, NEAR_ROOT[a], q))
os.makedirs("out", exist_ok=True)
with open("out/wd_closure_anchor_queries.tsv", "w", newline='', encoding="utf-8") as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(["anchor_qid", "anchor_label", "query_text"])
    for a, lab, q in sorted(rows): w.writerow([a, lab, q])
per = {}
for a, lab, q in rows: per.setdefault(a, []).append(q)
print("\n=== queries anchored at near-root classes ===")
for a in sorted(per, key=lambda x: -len(per[x])):
    print("  %-12s %-24s %d queries" % (a, NEAR_ROOT[a], len(per[a])))
print("  wrote out/wd_closure_anchor_queries.tsv (%d rows)" % len(rows))

# --- (b) the bound, against both denominators --------------------------------------------
children = {}
for line in open("generated-usage-metadata/wikidata-schema/p279_edges_2017.tsv"):
    c, p = line.rstrip("\n").split("\t"); children.setdefault(p, []).append(c)
types_universe = set(open("generated-usage-metadata/wikidata-schema/types_2017.txt").read().split())
preds_universe = set(open("generated-usage-metadata/wikidata-schema/preds_2017.txt").read().split())
TSE = len(types_universe) + len(preds_universe)

anchors_all = set()
for r in res:
    if r.get("v"): anchors_all.update(r.get("anchors", []))
closure = set()
dq = deque(anchors_all); closure |= anchors_all
while dq:
    x = dq.popleft()
    for c in children.get(x, ()):
        if c not in closure: closure.add(c); dq.append(c)
closure_types = closure & types_universe
explicit = set()
for r in res:
    if r.get("v"): explicit.update(r.get("types", []))
extra = closure_types - explicit

lines = [
 "Closure-based ('effective usage') bound, Wikidata organic 2017",
 "",
 "  distinct P279*/P31-P279* anchors in queries : %d" % len(anchors_all),
 "  subclass closure of those anchors (classes) : %d" % len(closure_types),
 "  explicitly-referenced classes               : %d" % len(explicit),
 "  additional classes credited by closure      : %d" % len(extra),
 "",
 "  class universe (types_2017)                 : %d" % len(types_universe),
 "  predicate universe (preds_2017)             : %d" % len(preds_universe),
 "  TSE (classes + predicates)                  : %d" % TSE,
 "",
 "  closure as %% of CLASS universe              : %.1f%%   <- the figure the manuscript quotes" % (100*len(closure_types)/len(types_universe)),
 "  closure as %% of TSE                         : %.1f%%" % (100*len(closure_types)/TSE),
 "",
 "The manuscript's ~62%% refers to the class universe. Reporting it against TSE would give",
 "the smaller second figure, because TSE's denominator also contains the ~1k predicates.",
]
txt = "\n".join(lines)
open("out/wd_closure_bound_summary.txt", "w").write(txt + "\n")
print("\n" + txt)
