"""Substantiate WHY the closure bound saturates: which general classes are used as
P279*-anchors, and how large is each one's individual subclass closure."""
import csv, gzip, os, urllib.parse, json, subprocess, tempfile, importlib.util
from collections import deque
csv.field_size_limit(1<<30)
spec=importlib.util.spec_from_file_location("pv","Schema-coverage-method/sparql_log_preprocess.py")
pv=importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE=os.path.expanduser("~/.local/bin/node"); PAW=os.path.expanduser("~/.local/sparqljs-worker/pathanchor_worker.js")
WD="data/logs/wikidata"
FILES=[f"{WD}/int1_2017_organic.tsv.gz", f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
       f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
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
seen=set()
for path in FILES:
    with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); qi=h.index('anonymizedQuery')
        for row in r:
            if len(row)>qi: seen.add(wclean(row[qi]))
qs=list(seen)
res=parallel([pv.add_prefixes(q,False) for q in qs])
anchor_freq={}
for r in res:
    if r.get("v"):
        for a in r["anchors"]: anchor_freq[a]=anchor_freq.get(a,0)+1
children={}
for line in open("generated-usage-metadata/wikidata-schema/p279_edges_2017.tsv"):
    c,p=line.rstrip("\n").split("\t"); children.setdefault(p,[]).append(c)
types_universe=set(open("generated-usage-metadata/wikidata-schema/types_2017.txt").read().split())
def closure_size(root):
    seen={root}; dq=deque([root])
    while dq:
        x=dq.popleft()
        for c in children.get(x,()):
            if c not in seen: seen.add(c); dq.append(c)
    return len(seen & types_universe)
LABELS={"Q35120":"entity","Q488383":"object","Q99527517":"collective entity",
 "Q23958852":"variable-order class","Q16686022":"natural object","Q4406616":"concrete object",
 "Q151885":"concept","Q386724":"work","Q43229":"organization","Q5":"human","Q726":"horse",
 "Q1190554":"occurrence","Q488383":"object","Q7184903":"abstract object","Q223557":"physical object"}
# most-frequently-used anchors
top=sorted(anchor_freq.items(),key=lambda x:-x[1])[:15]
print("=== most-frequent P279*-anchors (anchor, #queries, |subclass closure in type universe|) ===")
for a,f in top:
    print(f"  {a} {LABELS.get(a,'?'):24s} queries={f:>6}  closure={closure_size(a):,}")
print("\n=== canonical general classes: present as anchor? + closure size ===")
for q,lab in [("Q35120","entity"),("Q488383","object"),("Q99527517","collective entity"),
              ("Q16686022","natural object"),("Q4406616","concrete object"),("Q151885","concept"),
              ("Q43229","organization"),("Q386724","work")]:
    inq = q in anchor_freq
    print(f"  {q} {lab:20s} anchor={'YES('+str(anchor_freq[q])+')' if inq else 'no':10s} closure={closure_size(q):,}")
