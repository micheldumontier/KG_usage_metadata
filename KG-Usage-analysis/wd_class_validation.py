"""Class-extraction validation (R2-1.1): quantify the data-glitch / uninstantiated-class
risk in the Wikidata 'class' universe, and show the QUERIED classes (which drive coverage)
are well-supported. 'Support' of a class = #times it is the object of P31 or P279 in the KG
(= #instances + #subclasses); support==1 is R2's glitch-prone 'used as a class only once'.
Inputs: types_2017.txt (universe), instances_per_class_2017.csv (P31), p279_edges_2017.tsv (P279)."""
import csv, os, sys, json
csv.field_size_limit(1<<30)
B="generated-usage-metadata"
types=set(open(f"{B}/wikidata-schema/types_2017.txt").read().split())
inst={}
for r in csv.DictReader(open(f"{B}/wikidata-supply/instances_per_class_2017.csv")):
    try: inst[r["class"]]=int(r["instances"])
    except: pass
children={}; haschild=set(); haspar=set()
for line in open(f"{B}/wikidata-schema/p279_edges_2017.tsv"):
    c,p=line.rstrip("\n").split("\t")
    children[p]=children.get(p,0)+1; haschild.add(p); haspar.add(c)
def support(q): return inst.get(q,0)+children.get(q,0)   # P31-obj + P279-obj count

def profile(label, S):
    S=[q for q in S if q in types]
    n=len(S)
    instd=sum(1 for q in S if inst.get(q,0)>0)
    subp =sum(1 for q in S if children.get(q,0)>0)
    hier =sum(1 for q in S if q in haschild or q in haspar)   # embedded in subclass hierarchy
    sing =sum(1 for q in S if support(q)==1)                  # used as a class exactly once
    sups=sorted(support(q) for q in S)
    med=sups[n//2] if n else 0
    print(f"\n[{label}]  n={n:,}")
    print(f"  instantiated (>=1 instance):            {instd:,} ({100*instd/n:.1f}%)")
    print(f"  has >=1 subclass:                       {subp:,} ({100*subp/n:.1f}%)")
    print(f"  embedded in subclass hierarchy (P279):  {hier:,} ({100*hier/n:.1f}%)")
    print(f"  SINGLETON (support==1, glitch-prone):   {sing:,} ({100*sing/n:.1f}%)")
    print(f"  median support (instances+subclasses):  {med}")
    return S

print("=== full extracted class universe ===")
profile("universe 2017", types)
# queried classes: union of used-type sets
def used(path):
    s=set()
    if os.path.exists(path):
        for r in csv.reader(open(path)):
            e=r[0]
            if e.startswith("wd:"): s.add(e[3:])
    return s
org=used("out/wd_allorganic2017_used.csv") or used("out/wd_organic2017_used.csv")
rob=used("out/wd_robotic2017_used.csv")
profile("queried: organic 2017", org)
profile("queried: robotic 2017", rob)

# write singleton sample for API label-check (random, seed-free: take a deterministic stride)
allsing=[q for q in sorted(types) if support(q)==1]
qsing=[q for q in sorted(org|rob) if support(q)==1]
print(f"\nuniverse singletons: {len(allsing):,};  queried singletons: {len(qsing):,}")
import math
def sample(lst,k):
    if len(lst)<=k: return lst
    step=len(lst)/k; return [lst[int(i*step)] for i in range(k)]
json.dump({"universe_singletons":sample(allsing,100),
           "queried_classes":sample(sorted(org|rob),100),
           "queried_singletons":qsing[:100]},
          open("out/wd_class_sample.json","w"))
print("wrote out/wd_class_sample.json (samples for API label-check)")
