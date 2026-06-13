"""Domain-level grouping of the content-demand inversion (R2-2: 'natural groups of schema
elements'). Assign each Wikidata class to a top-level domain via its P279 ancestors, then
compare KG SUPPLY (instances) against organic/robotic query DEMAND per domain. Shows the
inversion is a domain phenomenon: bulk-imported scientific/bibliographic/geographic-feature
domains hold most of the content but attract little human demand; person/creative-work/
settlement domains attract most demand from a small content base."""
import csv, os
from collections import deque, defaultdict
csv.field_size_limit(1<<30)
B="generated-usage-metadata"
# parent map (child -> [parents]) from P279 edges
parents=defaultdict(list)
for line in open(f"{B}/wikidata-schema/p279_edges_2017.tsv"):
    c,p=line.rstrip("\n").split("\t"); parents[c].append(p)
inst={}
for r in csv.DictReader(open(f"{B}/wikidata-supply/instances_per_class_2017.csv")):
    try: inst[r["class"]]=int(r["instances"])
    except: pass

# top-level domain anchors (priority order: specific scientific domains first)
DOMAINS=[
 ("Taxon / species",      {"Q16521","Q713623","Q427626"}),
 ("Gene / protein / biomedical", {"Q7187","Q8054","Q11173","Q12136","Q12140","Q417841","Q897314"}),
 ("Astronomical object",  {"Q6999","Q3242597"}),
 ("Scholarly / publication", {"Q591041","Q13442814","Q732577","Q11032","Q571","Q732577"}),
 ("Person (human/occupation)", {"Q5","Q215627","Q28640","Q12737077"}),
 ("Creative work",        {"Q17537576","Q386724","Q2188189","Q11424","Q7889","Q482994","Q3305213"}),
 ("Organization / company", {"Q43229","Q4830453","Q783794","Q3918","Q43229"}),
 ("Structure / building", {"Q811979","Q41176","Q811430","Q83620"}),
 ("Event",                {"Q1656682","Q1190554","Q1656682"}),
 ("Geographic feature",   {"Q27096213","Q2221906","Q618123","Q271669","Q486972","Q56061"}),
 ("Wikimedia maintenance",{"Q17442446","Q4167836","Q4167410","Q11266439","Q15184295"}),
]
ANCHOR2DOM={}
for name,qs in DOMAINS:
    for q in qs: ANCHOR2DOM[q]=name
ANCHORS=set(ANCHOR2DOM)
DOMORD=[d[0] for d in DOMAINS]+["Other / unclassified"]

def domain_of(c):
    """walk up P279 from c; return the highest-priority anchor domain reached."""
    seen={c}; dq=deque([c]); hit=set()
    while dq:
        x=dq.popleft()
        if x in ANCHORS: hit.add(ANCHOR2DOM[x])
        for p in parents.get(x,()):
            if p not in seen: seen.add(p); dq.append(p)
    for name in DOMORD[:-1]:
        if name in hit: return name
    return "Other / unclassified"

# precompute domain for all classes we care about: universe ∩ (supply ∪ queried)
def used(path):
    d={}
    if os.path.exists(path):
        for r in csv.reader(open(path)):
            if r and r[0].startswith("wd:"):
                try: d[r[0][3:]]=int(r[1])
                except: pass
    return d
org=used("out/wd_allorganic2017_used.csv") or used("out/wd_organic2017_used.csv")
rob=used("out/wd_robotic2017_used.csv")
classes=set(inst)|set(org)|set(rob)
print(f"classifying {len(classes):,} classes (with instances or queried) into domains...",flush=True)
dom={c:domain_of(c) for c in classes}

agg=defaultdict(lambda:[0,0,0,0])  # domain -> [#classes, supply(sum instances), organic demand, robotic demand]
for c in classes:
    d=dom[c]; a=agg[d]
    a[0]+=1; a[1]+=inst.get(c,0); a[2]+=org.get(c,0); a[3]+=rob.get(c,0)
SUP=sum(a[1] for a in agg.values()); OD=sum(a[2] for a in agg.values()); RD=sum(a[3] for a in agg.values())
print(f"\n{'domain':30s} {'#cls':>7} {'supply':>13} {'supply%':>8} {'org.dem':>9} {'org%':>7} {'rob.dem':>9} {'rob%':>7}")
for d in DOMORD:
    if d not in agg: continue
    n,s,o,r=agg[d]
    print(f"{d:30s} {n:>7,} {s:>13,} {100*s/max(1,SUP):>7.1f}% {o:>9,} {100*o/max(1,OD):>6.1f}% {r:>9,} {100*r/max(1,RD):>6.1f}%")
print(f"{'TOTAL':30s} {sum(a[0] for a in agg.values()):>7,} {SUP:>13,} {'100%':>8} {OD:>9,} {'100%':>7} {RD:>9,} {'100%':>7}")
