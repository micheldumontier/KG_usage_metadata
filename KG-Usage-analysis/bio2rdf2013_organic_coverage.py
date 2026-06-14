"""Bio2RDF-2013 ORGANIC coverage from the raw server log's browser-UA queries
(Option A: lift the 'cannot split 2013' limitation). Parse organic queries, extract
referenced bio2rdf vocabulary elements, intersect with the canonical 545-element TSE,
report coverage. Mirrors the 2019 organic method (extract_worker, TSE intersection)."""
import csv, sys, json, os, subprocess, tempfile, importlib.util, re
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); EXW=os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
ORG=os.path.expanduser("~/data/bio2rdf.logs/derived/organic_2013_queries.txt")
B="generated-usage-metadata/bio2rdf-schema"
TYPES=set(l.strip() for l in open(f"{B}/types_26subgraphs.txt") if l.strip())
PREDS=set(l.strip() for l in open(f"{B}/predicates_26subgraphs.txt") if l.strip())
TSE=len(TYPES)+len(PREDS)
def parallel(prepped,nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,EXW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
    out=[]
    for p,ti,to in procs: p.wait(); out+=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    return out
# already URL-decoded during extraction; just normalize whitespace + dedup
seen={}
for line in open(ORG,encoding="utf-8",errors="replace"):
    k=pv.normalize_ws(line.rstrip("\n"))
    if k: seen[k]=seen.get(k,0)+1
qs=list(seen); occ=sum(seen.values())
print(f"organic occurrences: {occ:,}   unique: {len(qs):,}",flush=True)
res=parallel([pv.add_prefixes(q,True) for q in qs])
valid=sum(1 for r in res if r.get("v"))
ut={}; up={}
for q,r in zip(qs,res):
    if not r.get("v"): continue
    c=seen[q]
    for iri in r.get("iris",[]):
        if iri in TYPES: ut[iri]=ut.get(iri,0)+c
    for p in r.get("preds",[]):
        if p in PREDS: up[p]=up.get(p,0)+c
USE=len(ut)+len(up)
print(f"valid: {valid:,} ({100*valid/len(qs):.1f}% of unique)")
print(f"used types: {len(ut)}/{len(TYPES)}   used preds: {len(up)}/{len(PREDS)}")
print(f"COVERAGE (organic 2013): {USE}/{TSE} = {100*USE/TSE:.2f}%")
print(f"  [compare: organic-2019 = 116/545 = 21.28%; robotic/all-2019 = 529/545 = 97.06%]")
os.makedirs("out",exist_ok=True)
with open("out/bio2rdf2013_organic_used.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["element","kind","count"])
    for e,c in sorted(ut.items(),key=lambda x:-x[1]): w.writerow([e,"type",c])
    for e,c in sorted(up.items(),key=lambda x:-x[1]): w.writerow([e,"predicate",c])
print("top used types:", [e.split('/')[-1] for e,_ in sorted(ut.items(),key=lambda x:-x[1])[:10]])
