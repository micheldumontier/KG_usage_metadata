"""Example-query decontamination (R2-2iii). Match logged organic Wikidata queries against
the WDQS example-query templates (2017-06-30 revision) via a variable-invariant fingerprint,
and quantify how much 'organic' traffic is demonstration/example-driven. Recompute the
'used types' top-list and coverage with example-template traffic removed.
Conservative (lower-bound): matches only verbatim example runs (modulo variable names,
literals, and label-service boilerplate); 329/348 example templates fingerprint."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, importlib.util
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/sparql_log_preprocess.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node")
FPW=os.path.expanduser("~/.local/sparqljs-worker/fingerprint_worker.js")
CVW=os.path.expanduser("~/.local/sparqljs-worker/classvalue_worker.js")
WD="data/logs/wikidata"
ORGANIC=[f"{WD}/int1_2017_organic.tsv.gz",f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
 f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz",f"{WD}/2017-12-03_2017-12-30_organic.tsv.gz",
 f"{WD}/2018-01-01_2018-01-28_organic.tsv.gz",f"{WD}/2018-01-29_2018-02-25_organic.tsv.gz",
 f"{WD}/int7_2018_organic.tsv.gz"]
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))
def run(worker, items, nw=14):
    chunks=[items[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,worker],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
    res=[]
    for p,ti,to in procs: p.wait(); res+=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    return res

# example fingerprints
_EXFP=("generated-usage-metadata/wdqs-examples/examples_2017_fp.ndjson"
       if os.path.exists("generated-usage-metadata/wdqs-examples/examples_2017_fp.ndjson")
       else "data/wdqs_examples/examples_2017_fp.ndjson")
exfp=set(json.loads(l)["fp"] for l in open(_EXFP) if json.loads(l)["fp"])
print(f"distinct example fingerprints: {len(exfp)}",flush=True)

# load organic log (unique cleaned queries + occurrence counts)
seen={}
for path in ORGANIC:
    with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
        for row in r:
            if len(row)>qi: k=wclean(row[qi]); seen[k]=seen.get(k,0)+1
qs=list(seen); occ=[seen[q] for q in qs]; TOT=sum(occ)
print(f"organic: {len(qs):,} unique queries, {TOT:,} occurrences",flush=True)

# fingerprint + class/value extraction over the SAME unique-query list (aligned by index)
fps=run(FPW,[pv.add_prefixes(q,False) for q in qs])
cvs=run(CVW,[pv.add_prefixes(q,False) for q in qs])

types=set(open("generated-usage-metadata/wikidata-schema/types_2017.txt").read().split())
preds=set(open("generated-usage-metadata/wikidata-schema/preds_2017.txt").read().split())
TSE=len(types)+len(preds)

matched=[i for i,r in enumerate(fps) if r.get("fp") and r["fp"] in exfp]
mset=set(matched)
mocc=sum(occ[i] for i in matched)
print(f"\n=== EXAMPLE-TEMPLATE CONTAMINATION (lower bound) ===")
print(f"unique queries matching an example template: {len(matched):,} ({100*len(matched)/len(qs):.2f}% of unique)")
print(f"occurrences from example templates:          {mocc:,} ({100*mocc/TOT:.2f}% of all organic occurrences)")

def toptypes(exclude):
    dem={}
    for i,(q,r) in enumerate(zip(qs,cvs)):
        if exclude and i in mset: continue
        if not r.get("v"): continue
        c=occ[i]
        for e in r["ents"]:
            if e in types: dem[e]=dem.get(e,0)+c
    return dem
def cov(exclude):
    ut=set(); up=set()
    for i,r in enumerate(cvs):
        if exclude and i in mset: continue
        if not r.get("v"): continue
        for e in r["ents"]:
            if e in types: ut.add(e)
        # preds via classvalue? classvalue gives no preds; coverage here is types-only proxy
    return ut

LAB={"Q5":"human","Q515":"city","Q11424":"film","Q6256":"country","Q571":"book","Q33999":"actor",
 "Q486972":"settlement","Q3305213":"painting","Q4830453":"business","Q1248784":"airport","Q146":"cat",
 "Q6581097":"male(gender)","Q6581072":"female(gender)","Q82955":"politician","Q5398426":"TV series",
 "Q13442814":"scholarly article","Q16521":"taxon","Q3624078":"sovereign state","Q901":"scientist",
 "Q11424":"film","Q43229":"organization","Q47461344":"written work","Q7725634":"literary work"}
before=toptypes(False); after=toptypes(True)
def show(dem,n=12):
    return [(LAB.get(e,e),dem[e]) for e in sorted(dem,key=lambda x:-dem[x])[:n]]
print(f"\nTop-12 'used types' BEFORE decontamination:\n  {show(before)}")
print(f"\nTop-12 'used types' AFTER  decontamination:\n  {show(after)}")
# the female/male asymmetry R2 raised: report BOTH unique-query and occurrence counts
def counts(qid):
    uq=sum(1 for i,r in enumerate(cvs) if r.get("v") and qid in r["ents"])
    oc=sum(occ[i] for i,r in enumerate(cvs) if r.get("v") and qid in r["ents"])
    return uq,oc
for q in ("Q6581072","Q6581097","Q6581080"):
    uq,oc=counts(q)
    print(f"  {LAB.get(q,q):16s} {q}: unique-queries={uq:,}  occurrences={oc:,}")
ub,ua=cov(False),cov(True)
print(f"\ntype 'used' set: before {len(ub):,} ({100*len(ub)/len(types):.2f}% of types) -> after {len(ua):,} ({100*len(ua)/len(types):.2f}%)")
