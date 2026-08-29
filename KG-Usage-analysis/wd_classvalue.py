"""Quantify the class-position vs value-position split for Wikidata query logs.
Shows how much of the "used schema types" are genuinely used as classes (object of
P31/P279) vs merely referenced as property values. Evidence for the reframing /R2-1.1/."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, importlib.util, glob
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); CVW=os.path.expanduser("~/.local/sparqljs-worker/classvalue_worker.js")
SUP="generated-usage-metadata/wikidata-supply"
WD="data/logs/wikidata"
SRC={"organic2017":(sorted(glob.glob(f"{WD}/*organic*.tsv.gz")),None),
     "robotic2017":([f"{WD}/int1_2017_all.tsv.gz"],"robotic")}
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('',urllib.parse.unquote_plus(q)))
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

inst={r["class"]:int(r["instances"]) for r in csv.DictReader(open(f"{SUP}/instances_per_class_2017.csv"))}
src=sys.argv[1]; files,filt=SRC[src]
counts={}
for path in files:
    with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery'); ci=h.index('sourceCategory') if filt else None
        for row in r:
            if len(row)<=qi: continue
            if filt and (len(row)<=ci or row[ci]!=filt): continue
            counts[wclean(row[qi])]=counts.get(wclean(row[qi]),0)+1
qs=list(counts); print(f"[{src}] unique={len(qs):,}; parsing class/value positions...",flush=True)
res=parallel([pv.add_prefixes(q,False) for q in qs])

cls_ent=set(); all_ent=set(); cls_dem={}; val_dem={}
for q,r in zip(qs,res):
    if not r.get("v"): continue
    c=counts[q]
    for e in r["ents"]: all_ent.add(e)
    for e in r["cls"]:  cls_ent.add(e); cls_dem[e]=cls_dem.get(e,0)+c
    for e in set(r["ents"])-set(r["cls"]): val_dem[e]=val_dem.get(e,0)+c
value_only=all_ent-cls_ent
inst_classpos=[e for e in cls_ent if inst.get(e,0)>0]
# TSE-restricted: among entities the schema extraction counts as types (objects of P31/P279
# in the KG), how many are actually used as classes in queries vs only as values?
tse=set(l.strip() for l in open("generated-usage-metadata/wikidata-schema/types_2017.txt") if l.strip())
used_types=all_ent & tse            # = the paper's "used schema types"
class_used=cls_ent & tse
value_only_types=used_types-class_used
print(f"  --- restricted to KG-schema types (the paper's 'used types' metric) ---")
print(f"  used types (referenced & in KG type set): {len(used_types):,}")
print(f"    used as a class (class-position):        {len(class_used):,} ({100*len(class_used)/max(1,len(used_types)):.1f}%)")
print(f"    referenced ONLY as a value:              {len(value_only_types):,} ({100*len(value_only_types)/max(1,len(used_types)):.1f}%)")
print(f"  -------------------------------------------------------------")
print(f"  distinct entities referenced (any position): {len(all_ent):,}")
print(f"  ...ever used in CLASS position (object of P31/P279):        {len(cls_ent):,} ({100*len(cls_ent)/len(all_ent):.1f}%)")
print(f"  ...VALUE-only (never class position):                       {len(value_only):,} ({100*len(value_only)/len(all_ent):.1f}%)")
print(f"  class-position entities that are actually instantiated:     {len(inst_classpos):,}")
tot_cls=sum(cls_dem.values()); tot_val=sum(val_dem.values())
print(f"  demand-weighted (all referenced entities): class-position refs={tot_cls:,}  value-position refs={tot_val:,} "
      f"({100*tot_cls/(tot_cls+tot_val):.1f}% of references are class-position)")
# Same measure restricted to KG-schema types, which is the basis the manuscript's
# "type-item references" claim is stated on. Reported separately because the two
# denominators give very different shares.
t_cls=sum(v for e,v in cls_dem.items() if e in tse)
t_val=sum(v for e,v in val_dem.items() if e in tse)
print(f"  demand-weighted (KG-schema types only):    class-position refs={t_cls:,}  value-position refs={t_val:,} "
      f"({100*t_cls/max(1,t_cls+t_val):.1f}% of type-item references are class-position)")
# Persist the per-entity demand vectors so downstream questions about these numbers can be
# answered without re-parsing the logs, which takes tens of minutes.
import json as _json
_out = f"out/wd_classvalue_demand_{src}.json"
os.makedirs("out", exist_ok=True)
_json.dump({"cls_dem": cls_dem, "val_dem": val_dem,
            "used_types": sorted(used_types), "class_used": sorted(class_used)},
           open(_out, "w"))
print(f"  wrote {_out}")
print("  top class-position (genuine class demand):")
for e,c in sorted(cls_dem.items(),key=lambda x:-x[1])[:8]:
    print(f"     {e} demand={c:,} instances={inst.get(e,0):,}")
