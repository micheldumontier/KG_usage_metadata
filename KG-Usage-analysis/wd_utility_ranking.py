"""Ranking-sensitive evaluation of the type-suggestion task (review2: "Since the proposed
application is autocomplete, a ranking-sensitive evaluation or an explanation of why coverage
alone is sufficient would strengthen the analysis").

Top-k coverage (Table 12) measures how much future demand a suggestion LIST captures, but is
insensitive to the ORDER within that list -- which is exactly what an autocomplete dropdown
exposes. Here we add order-sensitive measures over the same train/test split:
  * nDCG@k with graded relevance = the type's deduplicated 2018 demand
  * demand-weighted MRR = sum_t (d_t / rank_t) / sum_t d_t
Rankings compared: (U) 2017 usage frequency, (S) KG supply (instances/class).
Caches the parsed demand vectors so the expensive log parse runs once."""
import csv, gzip, os, json, subprocess, tempfile, urllib.parse, importlib.util, math
csv.field_size_limit(1<<30)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); PAW=os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD="data/logs/wikidata"
TRAIN=[f"{WD}/int1_2017_organic.tsv.gz", f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
       f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
TEST=[f"{WD}/int7_2018_organic.tsv.gz"]
CACHE="out/wd_utility_demand_cache.json"

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
def class_demand(files):
    seen={}
    for path in files:
        with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
            r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
            for row in r:
                if len(row)>qi: k=wclean(row[qi]); seen[k]=seen.get(k,0)+1
    qs=list(seen); res=parallel([pv.add_prefixes(q,False) for q in qs])
    dem={}
    for q,rr in zip(qs,res):
        if not rr.get("v"): continue
        for t in set(rr["types"]): dem[t]=dem.get(t,0)+1
    return dem

if os.path.exists(CACHE):
    c=json.load(open(CACHE)); train,test=c["train"],c["test"]; print("loaded cached demand vectors")
else:
    print("parsing TRAIN (early 2017 organic)...",flush=True); train=class_demand(TRAIN)
    print("parsing TEST (2018 organic int7)...",flush=True);   test=class_demand(TEST)
    os.makedirs("out",exist_ok=True); json.dump({"train":train,"test":test},open(CACHE,"w"))

supply={}
for r in csv.DictReader(open("generated-usage-metadata/wikidata-supply/instances_per_class_2017.csv")):
    try: supply[r["class"]]=int(r["instances"])
    except: pass

U=[k for k,_ in sorted(train.items(),key=lambda x:-x[1])]
S=[k for k,_ in sorted(supply.items(),key=lambda x:-x[1])]
total=sum(test.values())
print(f"TRAIN distinct={len(train):,}  TEST distinct={len(test):,}  TEST total refs={total:,}")

def dcg(ranking,k):
    return sum(test.get(t,0)/math.log2(i+2) for i,t in enumerate(ranking[:k]))
def idcg(k):
    ideal=sorted(test.values(),reverse=True)[:k]
    return sum(r/math.log2(i+2) for i,r in enumerate(ideal))
def ndcg(ranking,k):
    z=idcg(k); return 100*dcg(ranking,k)/z if z else 0.0
def cov(ranking,k):
    s=set(ranking[:k]); return 100*sum(test[t] for t in test if t in s)/max(1,total)
def wmrr(ranking):
    pos={t:i+1 for i,t in enumerate(ranking)}
    num=sum(d/pos[t] for t,d in test.items() if t in pos)
    return num/total

print(f"\n{'k':>6} | {'nDCG@k usage':>13} | {'nDCG@k supply':>14} | {'cov usage':>10} | {'cov supply':>11}")
rows=[]
for k in [10,50,100,500,1000]:
    nu,ns,cu,cs=ndcg(U,k),ndcg(S,k),cov(U,k),cov(S,k)
    rows.append((k,nu,ns,cu,cs))
    print(f"{k:>6} | {nu:>12.1f}% | {ns:>13.1f}% | {cu:>9.1f}% | {cs:>10.1f}%")
mu,ms=wmrr(U),wmrr(S)
print(f"\ndemand-weighted MRR:  usage={mu:.4f}   supply={ms:.4f}   ratio={mu/ms if ms else float('inf'):.1f}x")
with open("out/wd_utility_ranking.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["k","ndcg_usage_pct","ndcg_supply_pct","cov_usage_pct","cov_supply_pct"])
    for k,nu,ns,cu,cs in rows: w.writerow([k,f"{nu:.2f}",f"{ns:.2f}",f"{cu:.2f}",f"{cs:.2f}"])
    w.writerow([]); w.writerow(["weighted_MRR_usage","weighted_MRR_supply"]); w.writerow([f"{mu:.4f}",f"{ms:.4f}"])
print("wrote out/wd_utility_ranking.csv")
