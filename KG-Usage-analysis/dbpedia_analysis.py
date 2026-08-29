"""DBpedia (OWL-style, 3rd KG): coverage + class-vs-value + supply/demand.
Tests whether the value-position inflation seen in Wikidata is item-based-KG-specific.
Inputs: data/logs/dbpedia/dbpedia_texts.txt (distinct executed query texts),
generated-usage-metadata/dbpedia-schema/{classes,predicates,instances_per_class}.txt/csv."""
import csv, sys, json, os, subprocess, tempfile, importlib.util
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/sparql_log_preprocess.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); CVW=os.path.expanduser("~/.local/sparqljs-worker/classvalue_worker_dbo.js")
DBO="http://dbpedia.org/ontology/"
B="generated-usage-metadata/dbpedia-schema"
classes={DBO+l.strip() for l in open(f"{B}/classes.txt") if l.strip()}
preds_set={DBO+l.strip() for l in open(f"{B}/predicates.txt") if l.strip()}
inst={}
if os.path.exists(f"{B}/instances_per_class.csv"):
    for r in csv.DictReader(open(f"{B}/instances_per_class.csv")):
        try: inst[DBO+r["class"]]=int(r["instances"])
        except: pass
TSE=len(classes)+len(preds_set)

def parallel(prepped,nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,CVW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
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

# dedup query texts (clean: LSQ texts are raw, not URL-encoded)
TEXTS=sys.argv[1] if len(sys.argv)>1 else "data/logs/dbpedia/dbpedia_texts.txt"
seen={}
for line in open(TEXTS,encoding="utf-8",errors="replace"):
    k=pv.clean(line.rstrip("\n")); seen[k]=seen.get(k,0)+1
qs=list(seen); print(f"DBpedia unique cleaned texts: {len(qs):,}; parsing...",flush=True)
res=parallel([pv.add_prefixes(q,False) for q in qs])

valid=sum(1 for r in res if r.get("v"))
used_cls=set(); ref_cls=set(); used_pred=set(); cls_dem={}
for q,r in zip(qs,res):
    if not r.get("v"): continue
    c=seen[q]
    for e in r["cls"]:
        if e in classes: used_cls.add(e); cls_dem[e]=cls_dem.get(e,0)+c
    for e in r["ents"]:
        if e in classes: ref_cls.add(e)
    for p in r["preds"]:
        if p in preds_set: used_pred.add(p)
value_only=ref_cls-used_cls
USE=len(used_cls)+len(used_pred)
print(f"valid={valid:,}  TSE={TSE} (classes {len(classes)}, preds {len(preds_set)})")
print(f"coverage: USE={USE} (used classes {len(used_cls)}, used preds {len(used_pred)}) = {100*USE/TSE:.2f}%")
print(f"--- class vs value (dbo classes referenced in queries) ---")
print(f"  dbo classes referenced anywhere:        {len(ref_cls)}")
print(f"  used in class position (rdf:type obj):  {len(used_cls)} ({100*len(used_cls)/max(1,len(ref_cls)):.1f}%)")
print(f"  value-only (never class position):      {len(value_only)} ({100*len(value_only)/max(1,len(ref_cls)):.1f}%)")
if inst:
    qd=sorted(used_cls,key=lambda e:-cls_dem.get(e,0))[:8]
    ign=sorted([c for c in classes if inst.get(c,0)>0 and c not in used_cls],key=lambda c:-inst.get(c,0))[:8]
    print("  top class-demand:", [(e.split('/')[-1],cls_dem.get(e,0),inst.get(e,0)) for e in qd])
    print("  rich-but-unqueried:", [(c.split('/')[-1],inst.get(c,0)) for c in ign])
