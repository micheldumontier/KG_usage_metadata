"""Equal-length-interval temporal trajectory for Wikidata organic queries (Tier-2 #7).
Upgrades the paper's 2-point (int1 vs int7) Wilcoxon/Spearman comparison to >=3 equal-length
(28-day) intervals spanning 2017-06..2018-03. The schema universe (TSE) is held FIXED at the
2017 dump so coverage/rank changes reflect QUERY BEHAVIOR, not schema evolution.
Per interval: schema coverage, type-frequency vector. Across intervals: coverage trajectory,
consecutive- and endpoint Spearman rank correlation on type frequencies, Wilcoxon on per-type
frequency change, and the persistent top-50 'core'."""
import csv, gzip, sys, json, os, subprocess, tempfile, urllib.parse, re, importlib.util
csv.field_size_limit(sys.maxsize)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/parse_validate_bio2rdf2019.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
from scipy.stats import spearmanr, wilcoxon
NODE=os.path.expanduser("~/.local/bin/node"); EXW=os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
QID=re.compile(r'wikidata\.org/entity/(Q\d+)$'); PID=re.compile(r'wikidata\.org/prop/direct/(P\d+)$')
WD="data/logs/wikidata"
# chronological, equal-length 28-day organic intervals
INTERVALS=[
 ("2017-06-12..07-09", f"{WD}/int1_2017_organic.tsv.gz"),
 ("2017-07-10..08-06", f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz"),
 ("2017-08-07..09-03", f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"),
 ("2017-12-03..12-30", f"{WD}/2017-12-03_2017-12-30_organic.tsv.gz"),
 ("2018-01-01..01-28", f"{WD}/2018-01-01_2018-01-28_organic.tsv.gz"),
 ("2018-01-29..02-25", f"{WD}/2018-01-29_2018-02-25_organic.tsv.gz"),
 ("2018-02-26..03-25", f"{WD}/int7_2018_organic.tsv.gz"),
]
def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))
def parallel_extract(prepped, nw=14):
    chunks=[prepped[i::nw] for i in range(nw)]; procs=[]
    for ch in chunks:
        ti=tempfile.NamedTemporaryFile('w',suffix='.nd',delete=False)
        for x in ch: ti.write(json.dumps(x)+"\n")
        ti.close(); to=ti.name+".o"
        procs.append((subprocess.Popen([NODE,EXW],stdin=open(ti.name),stdout=open(to,'w')),ti.name,to))
    out=[]
    for p,ti,to in procs: p.wait(); out+=[json.loads(l) for l in open(to)]; os.remove(ti); os.remove(to)
    return out

YEAR="2017"
types=set(open(f"generated-usage-metadata/wikidata-schema/types_{YEAR}.txt").read().split())
preds=set(open(f"generated-usage-metadata/wikidata-schema/preds_{YEAR}.txt").read().split())
TSE=len(types)+len(preds)

def process(path):
    counts={}; nq=0
    with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
        for row in r:
            if len(row)<=qi: continue
            k=wclean(row[qi]); counts[k]=counts.get(k,0)+1; nq+=1
    qs=list(counts)
    results=parallel_extract([pv.add_prefixes(q,False) for q in qs])
    type_occ={}; pred_occ={}
    for q,r in zip(qs,results):
        if not r.get("v"): continue
        c=counts[q]
        for iri in r["iris"]:
            m=QID.search(iri)
            if m and m.group(1) in types: type_occ[m.group(1)]=type_occ.get(m.group(1),0)+c
        for p in r["preds"]:
            m=PID.search(p)
            if m and m.group(1) in preds: pred_occ[m.group(1)]=pred_occ.get(m.group(1),0)+c
    return nq, type_occ, pred_occ

# all intervals are equal-length (28 days) so raw counts are already time-normalized
per=[]
for label,path in INTERVALS:
    nq,t,p=process(path)
    cov=100*(len(t)+len(p))/TSE
    per.append((label,nq,t,p,cov))
    print(f"{label}  q={nq:>8,}  usedTypes={len(t):>5}  usedPreds={len(p):>4}  coverage={cov:5.2f}%",flush=True)

print("\n=== type-frequency rank stability (Spearman rho) ===")
def rho(a,b):
    common=sorted(set(a)&set(b))
    if len(common)<3: return float('nan'),len(common)
    va=[a[k] for k in common]; vb=[b[k] for k in common]
    return spearmanr(va,vb).correlation, len(common)
print("consecutive intervals:")
for i in range(len(per)-1):
    r,n=rho(per[i][2],per[i+1][2])
    print(f"  {per[i][0]} -> {per[i+1][0]}:  rho={r:.3f}  (n={n} common types)")
r,n=rho(per[0][2],per[-1][2])
print(f"endpoint {per[0][0]} -> {per[-1][0]}:  rho={r:.3f}  (n={n})")

print("\n=== Wilcoxon signed-rank on per-type frequency change (consecutive) ===")
for i in range(len(per)-1):
    common=sorted(set(per[i][2])&set(per[i+1][2]))
    if len(common)<10: print(f"  {per[i][0]}->{per[i+1][0]}: n<10"); continue
    d=[per[i+1][2][k]-per[i][2][k] for k in common]
    try:
        w=wilcoxon(d); print(f"  {per[i][0]}->{per[i+1][0]}: W={w.statistic:.0f} p={w.pvalue:.3g} (n={len(common)})")
    except Exception as e: print(f"  err {e}")

print("\n=== persistent top-50 'core' types (in top-50 of ALL intervals) ===")
top50=[set(sorted(t.items(),key=lambda x:-x[1])[:50]) for (_,_,t,_,_) in per]
top50=[{k for k,_ in s} for s in top50]
persistent=set.intersection(*top50)
print(f"  {len(persistent)} types in every interval's top-50:")
# order by mean rank in first interval
print("  ", sorted(persistent))
print("\n=== coverage trajectory CSV ===")
os.makedirs("out",exist_ok=True)
with open("out/wd_temporal_trajectory.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["interval","queries","used_types","used_preds","coverage_pct"])
    for label,nq,t,p,cov in per: w.writerow([label,nq,len(t),len(p),f"{cov:.2f}"])
print("  wrote out/wd_temporal_trajectory.csv")
