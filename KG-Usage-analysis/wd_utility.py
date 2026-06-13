"""Utility demonstration (Tier-3 #11): does usage metadata have predictive value that KG
content statistics do not? Concrete downstream task = type autocomplete / query-suggestion.
Train a type-suggestion ranking on PAST organic logs (early 2017), then measure what fraction
of FUTURE class-position type demand (organic 2018, int7) the top-k suggestions capture.
Compare three rankings: (U) usage frequency in the training log, (S) KG supply = instances
per class (2017 dump), (R) random/popularity-free baseline. If U >> S, the usage metadata is
predictive where content volume is not -- operationalizing the content-demand inversion and
the paper's documentation/autocomplete motivation."""
import csv, gzip, os, json, subprocess, tempfile, urllib.parse, importlib.util
csv.field_size_limit(1<<30)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); PAW=os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD="data/logs/wikidata"
TRAIN=[f"{WD}/int1_2017_organic.tsv.gz", f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
       f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
TEST=[f"{WD}/int7_2018_organic.tsv.gz"]
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
def class_demand(files):
    """weighted class-position type references: {Qid: total occurrences}"""
    seen={}
    for path in files:
        with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
            r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
            for row in r:
                if len(row)>qi: k=wclean(row[qi]); seen[k]=seen.get(k,0)+1
    qs=list(seen); res=parallel([pv.add_prefixes(q,False) for q in qs])
    dem={}
    # DEDUPLICATED (intent-diversity) demand: each DISTINCT query counts once, so a single
    # hammered example/tool template cannot dominate (consistent with the paper's unique-query
    # counts and its example-query-contamination caveat).
    for q,rr in zip(qs,res):
        if not rr.get("v"): continue
        for t in set(rr["types"]): dem[t]=dem.get(t,0)+1
    return dem

print("parsing TRAIN (early 2017 organic)...",flush=True); train=class_demand(TRAIN)
print("parsing TEST (2018 organic int7)...",flush=True); test=class_demand(TEST)
supply={}
for r in csv.DictReader(open("generated-usage-metadata/wikidata-supply/instances_per_class_2017.csv")):
    try: supply[r["class"]]=int(r["instances"])
    except: pass
total_test=sum(test.values())
print(f"\nTRAIN distinct class-types: {len(train):,}  TEST distinct: {len(test):,}  TEST total references: {total_test:,}")

def rank_usage():  return [k for k,_ in sorted(train.items(),key=lambda x:-x[1])]
def rank_supply(): return [k for k,_ in sorted(supply.items(),key=lambda x:-x[1])]
def coverage(ranking,k):
    topk=set(ranking[:k]); return 100*sum(test[t] for t in test if t in topk)/max(1,total_test)

U=rank_usage(); S=rank_supply()
print("\n=== Future-demand coverage by top-k suggestions (TEST=organic 2018) ===")
print(f"{'k':>5} | {'usage-ranked':>13} | {'supply-ranked':>13}")
for k in [10,25,50,100,200,500,1000]:
    print(f"{k:>5} | {coverage(U,k):>12.1f}% | {coverage(S,k):>12.1f}%")

# how far down the supply list to match usage@50?
target=coverage(U,50)
need=0; topk=set()
for i,t in enumerate(S,1):
    topk.add(t)
    if 100*sum(test[x] for x in test if x in topk)/max(1,total_test)>=target: need=i; break
print(f"\nusage top-50 covers {target:.1f}% of future demand; supply needs top-{need or '>'+str(len(S))} to match.")

# coverage curve -> CSV + figure
import numpy as np
ks=[1,2,3,5,10,15,20,25,30,40,50,75,100,150,200,300,500,750,1000,1500,2000]
uc=[coverage(U,k) for k in ks]; sc=[coverage(S,k) for k in ks]
os.makedirs("out",exist_ok=True)
with open("out/wd_utility_curve.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["k","usage_coverage_pct","supply_coverage_pct"])
    for k,u,s in zip(ks,uc,sc): w.writerow([k,f"{u:.2f}",f"{s:.2f}"])
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(5.2,3.6))
    ax.plot(ks,uc,'-o',ms=3,color="#1f77b4",label="ranked by past usage frequency")
    ax.plot(ks,sc,'-s',ms=3,color="#d62728",label="ranked by KG supply (instances/class)")
    ax.set_xscale("log"); ax.set_xlabel("number of suggested types (top-$k$)")
    ax.set_ylabel("% of future (2018) type demand covered")
    ax.set_ylim(0,100); ax.axhline(coverage(U,50),ls=":",c="grey",lw=.8)
    ax.legend(fontsize=8,loc="center right"); ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig("manuscript/texsupport.iospress-sw-master/utility_autocomplete.png",dpi=200)
    print("wrote utility_autocomplete.png + out/wd_utility_curve.csv")
except Exception as e: print("plot skipped:",e)

LAB={"Q5":"human","Q515":"city","Q11424":"film","Q6256":"country","Q571":"book","Q33999":"actor",
 "Q486972":"human settlement","Q3305213":"painting","Q4830453":"business","Q1248784":"airport",
 "Q146":"cat","Q6581097":"male","Q6581072":"female","Q82955":"politician","Q5398426":"TV series",
 "Q13442814":"scholarly article","Q4167836":"Wikimedia category","Q16521":"taxon","Q7187":"gene",
 "Q8054":"protein","Q4167410":"disambiguation page","Q318":"galaxy","Q523":"star",
 "Q3624078":"sovereign state","Q3918":"university","Q8502":"mountain","Q11266439":"Wikimedia template",
 "Q13100073":"Chinese village","Q532":"village"}
def show(ranking,n=10): return [(t,LAB.get(t,'?'),) for t in ranking[:n]]
print("\nusage top-10:",show(U))
print("supply top-10:",show(S))
