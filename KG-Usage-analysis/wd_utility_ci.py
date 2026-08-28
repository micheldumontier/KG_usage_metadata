"""Bootstrap confidence intervals for the utility forecast (Sec. 4.9). The training ranking
(2017 usage) and the supply ranking are fixed 'models'; uncertainty lives in the TEST demand
sample (2018 distinct queries). We resample the distinct test queries with replacement (B=2000)
and recompute coverage@k for each ranking, reporting 2.5/50/97.5 percentiles and the gap CI.
Coverage@k = (reference-weighted) fraction of test class-type references whose type is in top-k."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, importlib.util, bisect
import numpy as np
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); PAW=os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD="data/logs/wikidata"
TRAIN=[f"{WD}/int1_2017_organic.tsv.gz",f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
       f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
TEST=[f"{WD}/int7_2018_organic.tsv.gz"]
KS=[10,25,50,100,200,500,1000]; B=2000
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))
def parallel(prepped,nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,PAW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
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
def typesets(files):
    """dedup queries -> list of class-position type-sets (one per distinct query)."""
    seen={}
    for path in files:
        with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
            r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
            for row in r:
                if len(row)>qi: seen[wclean(row[qi])]=1
    qs=list(seen); res=parallel([pv.add_prefixes(q,False) for q in qs])
    return [set(r["types"]) for r in res if r.get("v")]

# training usage demand -> ranking
trainsets=typesets(TRAIN)
train={}
for ts in trainsets:
    for t in ts: train[t]=train.get(t,0)+1
usage_rank={t:i for i,(t,_) in enumerate(sorted(train.items(),key=lambda x:-x[1]))}
supply={}
for r in csv.DictReader(open("generated-usage-metadata/wikidata-supply/instances_per_class_2017.csv")):
    try: supply[r["class"]]=int(r["instances"])
    except: pass
supply_rank={t:i for i,(t,_) in enumerate(sorted(supply.items(),key=lambda x:-x[1]))}

testsets=typesets(TEST)
print(f"test distinct queries with >=1 type: {len(testsets):,}",flush=True)
# per-query: tot_i, and coverage contribution c_i(k) for each ranking and k
INF=10**9
def contrib(sets, rank):
    tot=np.zeros(len(sets)); C=np.zeros((len(sets),len(KS)))
    for i,ts in enumerate(sets):
        ranks=sorted(rank.get(t,INF) for t in ts)
        tot[i]=len(ts)
        for j,k in enumerate(KS): C[i,j]=bisect.bisect_left(ranks,k)
    return tot,C
tot,Cu=contrib(testsets,usage_rank)
_,Cs=contrib(testsets,supply_rank)
N=len(testsets); rng=np.random.default_rng(20260612)
def boot(C):
    out=np.zeros((B,len(KS)))
    for b in range(B):
        idx=rng.integers(0,N,N); d=tot[idx].sum()
        out[b]=100*C[idx].sum(0)/d
    return out
Bu,Bs=boot(Cu),boot(Cs)
def pct(a,j): return np.percentile(a[:,j],[2.5,50,97.5])
print(f"\n{'k':>5} | {'usage  (95% CI)':>26} | {'supply (95% CI)':>26} | {'gap (95% CI)':>20}")
for j,k in enumerate(KS):
    u=pct(Bu,j); s=pct(Bs,j); g=np.percentile(Bu[:,j]-Bs[:,j],[2.5,50,97.5])
    print(f"{k:>5} | {u[1]:6.1f} [{u[0]:5.1f},{u[2]:5.1f}] | {s[1]:6.1f} [{s[0]:5.1f},{s[2]:5.1f}] | {g[1]:5.1f} [{g[0]:4.1f},{g[2]:4.1f}]")
os.makedirs("out",exist_ok=True)
with open("out/wd_utility_ci.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["k","usage_med","usage_lo","usage_hi","supply_med","supply_lo","supply_hi","gap_med","gap_lo","gap_hi"])
    for j,k in enumerate(KS):
        u=pct(Bu,j);s=pct(Bs,j);g=np.percentile(Bu[:,j]-Bs[:,j],[2.5,50,97.5])
        w.writerow([k,*[f"{x:.2f}" for x in (u[1],u[0],u[2],s[1],s[0],s[2],g[1],g[0],g[2])]])
print("\nwrote out/wd_utility_ci.csv")
