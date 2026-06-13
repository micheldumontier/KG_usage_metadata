"""Closure-based effective-usage bound (Tier-2 #8) for Wikidata organic 2017.
Answers reviewer R2-1.2: a closure/answer-based notion of "use" would additionally credit
the subclasses traversed by P279*-paths (e.g. wdt:P31/wdt:P279* wd:Q726 'uses' all subclasses
of horse). We bound exactly that: parse organic queries, find anchor classes reached via a
*/+ path over P279, take the transitive subclass closure (descendants) of each anchor in the
2017 KG, restrict to the type universe, subtract types already named explicitly -> the MAX
number of additional types a closure notion could credit, as an absolute count and % of TSE."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, re, importlib.util
from collections import deque
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); PAW=os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD="data/logs/wikidata"; YEAR="2017"
# int1 only, to match the §3.4 property-path figure (18,705 of 88,491 = 21.1%)
FILES=[f"{WD}/int1_2017_organic.tsv.gz"]
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))
def parallel(prepped,nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,PAW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
    out=[]
    for p,ti,to in procs: p.wait(); out+=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    return out

# 1) collect unique organic 2017 queries
seen={}
for path in FILES:
    with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
        for row in r:
            if len(row)>qi:
                k=wclean(row[qi]); seen[k]=seen.get(k,0)+1
qs=list(seen); print(f"unique organic-2017 queries: {len(qs):,}; parsing paths...",flush=True)
res=parallel([pv.add_prefixes(q,False) for q in qs])

valid=sum(1 for r in res if r.get("v"))
star=sum(1 for r in res if r.get("star"))
anchors=set(); explicit_types=set()
for r in res:
    if not r.get("v"): continue
    anchors.update(r["anchors"]); explicit_types.update(r["types"])
print(f"valid={valid:,}  star-path queries={star:,} ({100*star/max(1,valid):.1f}% of valid)")
print(f"distinct P279*-anchor classes named in queries: {len(anchors)}")
print(f"explicit class-position types named: {len(explicit_types)}")

# 2) load P279 edge list (child -> parents); build parent -> children for descendant BFS
EDGES=f"generated-usage-metadata/wikidata-schema/p279_edges_{YEAR}.tsv"
children={}
ne=0
for line in open(EDGES):
    c,p=line.rstrip("\n").split("\t"); children.setdefault(p,[]).append(c); ne+=1
print(f"P279 edges loaded: {ne:,}; classes with >=1 subclass: {len(children):,}")

types_universe=set(open(f"generated-usage-metadata/wikidata-schema/types_{YEAR}.txt").read().split())
TSE=len(types_universe)+len(open(f"generated-usage-metadata/wikidata-schema/preds_{YEAR}.txt").read().split())

# 3) transitive subclass closure (descendants) of all anchors
desc=set(); dq=deque(anchors)
while dq:
    x=dq.popleft()
    for c in children.get(x,()):
        if c not in desc:
            desc.add(c); dq.append(c)
# restrict to the type universe (only count things that are actually classes)
desc_types=desc & types_universe
added=desc_types - explicit_types
print(f"\n=== CLOSURE BOUND (organic 2017) ===")
print(f"subclasses reachable from anchors (transitive): {len(desc):,}")
print(f"  ... that are in the type universe:            {len(desc_types):,}")
print(f"  ... not already named explicitly (NET add):   {len(added):,}")
print(f"as fraction of TSE ({TSE:,}): max +{100*len(added)/TSE:.2f} percentage points of coverage")
# context vs explicit used types (first-window count was 3,559)
print(f"relative to ~3,559 explicitly used organic-2017 types: up to +{100*len(added)/3559:.0f}% more types")
