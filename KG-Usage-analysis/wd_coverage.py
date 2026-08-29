"""Wikidata schema-coverage from real logs: parse queries, intersect referenced
entities/predicates with the TSE sets extracted from the KG dump. Validates Tables 4-5."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, re, glob, importlib.util
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/sparql_log_preprocess.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); EXW=os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
QID=re.compile(r'wikidata\.org/entity/(Q\d+)$'); PID=re.compile(r'wikidata\.org/prop/direct/(P\d+)$')
WD="data/logs/wikidata"
SRC={
 "organic2017":  ([f"{WD}/int1_2017_organic.tsv.gz"], None, "2017"),
 "organic2018":  ([f"{WD}/int7_2018_organic.tsv.gz"], None, "2018"),
 "allorganic2017":(sorted(glob.glob(f"{WD}/*organic*.tsv.gz")), None, "2017"),
 "robotic2017":  ([f"{WD}/int1_2017_all.tsv.gz"], "robotic", "2017"),
 "robotic2018":  ([f"{WD}/int7_2018_all.tsv.gz"], "robotic", "2018"),
}
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))
def parallel_extract(prepped, nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]; outs=[None]*nw
    for j,ch in enumerate(chunks):
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,EXW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to,j))
    res=[None]*nw
    for p,ti,to,j in procs:
        p.wait(); res[j]=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    # reinterleave to original order not needed (we only tally), just concat
    out=[]
    for j in range(nw): out.extend(res[j])
    return out  # NOTE order is round-robin-chunked; fine for tallying (we don't need counts alignment beyond per-query)

def main():
    src=sys.argv[1]
    files,filt,year=SRC[src]
    types=set(open(f"generated-usage-metadata/wikidata-schema/types_{year}.txt").read().split())
    preds=set(open(f"generated-usage-metadata/wikidata-schema/preds_{year}.txt").read().split())
    TSE=len(types)+len(preds)
    counts={}; nq=0
    for path in files:
        with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
            r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
            ci=h.index('sourceCategory') if filt else None
            for row in r:
                if len(row)<=qi: continue
                if filt and (len(row)<=ci or row[ci]!=filt): continue
                k=wclean(row[qi]); counts[k]=counts.get(k,0)+1; nq+=1
    qs=list(counts); print(f"[{src}] occ={nq:,} unique={len(qs):,}; extracting...",flush=True)
    results=parallel_extract([pv.add_prefixes(q,False) for q in qs])
    type_occ={}; pred_occ={}
    for r in results:
        if not r.get("v"): continue
        for iri in r["iris"]:
            m=QID.search(iri)
            if m and m.group(1) in types: type_occ[m.group(1)]=type_occ.get(m.group(1),0)+1
        for p in r["preds"]:
            m=PID.search(p)
            if m and m.group(1) in preds: pred_occ[m.group(1)]=pred_occ.get(m.group(1),0)+1
    USE=len(type_occ)+len(pred_occ)
    os.makedirs("out",exist_ok=True)
    with open(f"out/wd_{src}_used.csv","w",newline='') as f:
        w=csv.writer(f); w.writerow(["element","count"])
        for e,c in sorted(type_occ.items(),key=lambda x:-x[1]): w.writerow([f"wd:{e}",c])
        for e,c in sorted(pred_occ.items(),key=lambda x:-x[1]): w.writerow([f"wdt:{e}",c])
    print(f"[{src}] USE={USE} (types {len(type_occ)}, preds {len(pred_occ)}) TSE={TSE} "
          f"coverage={100*USE/TSE:.2f}%",flush=True)

if __name__=="__main__": main()
