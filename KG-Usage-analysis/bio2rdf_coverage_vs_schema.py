"""Coverage of a Bio2RDF query set against a given (version-matched) schema.
Usage: python3 bio2rdf_coverage_vs_schema.py <queries.txt> <types.txt> <preds.txt> <label>"""
import csv, sys, json, os, subprocess, tempfile, importlib.util, re
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/sparql_log_preprocess.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); EXW=os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
QF,TF,PF,LABEL=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
TYPES=set(l.strip() for l in open(TF) if l.strip()); PREDS=set(l.strip() for l in open(PF) if l.strip())
TSE=TYPES|PREDS
VOC=re.compile(r'^http://bio2rdf\.org/([A-Za-z0-9_.\-]+)_vocabulary:(.+)$')
def par(prepped,nw=14):
    ch=[prepped[i::nw] for i in range(nw)];P=[]
    for c in ch:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in c: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"; P.append((subprocess.Popen([NODE,EXW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
    o=[]
    for p,ti,to in P: p.wait(); o+=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    return o
seen={}
for line in open(QF,encoding="utf-8",errors="replace"):
    k=pv.normalize_ws(line.rstrip("\n"))
    if k: seen[k]=seen.get(k,0)+1
qs=list(seen); occ=sum(seen.values()); res=par([pv.add_prefixes(q,True) for q in qs])
valid=sum(1 for r in res if r.get("v"))
ref=set(); ut=set(); up=set()
for r in res:
    if not r.get("v"): continue
    for iri in r.get("iris",[])+r.get("preds",[]):
        m=VOC.match(iri)
        if m and m.group(2)!='Resource': ref.add(iri)
        if iri in TYPES: ut.add(iri)
        if iri in PREDS: up.add(iri)
USE=len(ut)+len(up)
inref=len(ref & TSE)
print(f"[{LABEL}] occ={occ:,} unique={len(qs):,} valid={valid:,}  |schema TSE|={len(TSE)} ({len(TYPES)}T+{len(PREDS)}P)")
print(f"  referenced vocab IRIs={len(ref):,}; in this schema={inref:,} ({100*inref/max(1,len(ref)):.1f}%)")
print(f"  COVERAGE: used {USE}/{len(TSE)} = {100*USE/len(TSE):.1f}%  (types {len(ut)}/{len(TYPES)}, preds {len(up)}/{len(PREDS)})")
