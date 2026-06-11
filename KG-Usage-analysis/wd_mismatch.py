"""Content supply-vs-demand mismatch for Wikidata (Tier-1 #1).
Supply  = instances/class (P31) and triples/predicate, from the KG dump scan.
Demand  = query frequency per schema element, from the used-element CSVs (wd_coverage.py).
Output  = quadrant classification + named enrichment/deprecation candidates + scatter PNG.
Run after wd_supply.py has produced generated-usage-metadata/wikidata-supply/*.csv."""
import csv, os, sys, json, urllib.parse, urllib.request
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUP = "generated-usage-metadata/wikidata-supply"
year = sys.argv[1] if len(sys.argv) > 1 else "2017"
demand_file = sys.argv[2] if len(sys.argv) > 2 else "out/wd_allorganic2017_used.csv"

def load(path, kcol, vcol):
    d = {}
    for r in csv.DictReader(open(path)):
        try: d[r[kcol]] = int(r[vcol])
        except: pass
    return d

inst = load(f"{SUP}/instances_per_class_{year}.csv", "class", "instances")   # Q -> #instances
# demand: element -> query count; split wd:Q (types) vs wdt:P (preds)
dem_type = {}; dem_pred = {}
for r in csv.DictReader(open(demand_file)):
    e, c = r["element"], int(r["count"])
    if e.startswith("wd:Q"): dem_type[e[3:]] = c
    elif e.startswith("wdt:P"): dem_pred[e[4:]] = c

# ---- classes: supply (instances) vs demand (query freq) ----
classes = set(inst) | set(dem_type)
import statistics as st
sup_vals = [inst.get(q,0) for q in classes]
hi_sup = st.quantiles([v for v in sup_vals if v>0], n=4)[2]   # top quartile of supply
dem_vals = [dem_type.get(q,0) for q in classes]
hi_dem = st.quantiles([v for v in dem_vals if v>0], n=4)[2] if any(dem_vals) else 1

def quad(q):
    s, d = inst.get(q,0), dem_type.get(q,0)
    return ("HIdem_LOsup" if d>=hi_dem and s<hi_sup else
            "LOdem_HIsup" if d< max(1,hi_dem*0.1) and s>=hi_sup else
            "HIdem_HIsup" if d>=hi_dem and s>=hi_sup else "tail")
from collections import Counter
qc = Counter(quad(q) for q in classes)
print(f"=== Wikidata {year} classes: supply×demand quadrants (hi_sup={hi_sup:,.0f}, hi_dem={hi_dem:,.0f}) ===")
for k,v in qc.most_common(): print(f"  {k}: {v:,}")

def labels(qids):
    out={}
    for i in range(0,len(qids),50):
        batch=qids[i:i+50]
        q="SELECT ?x ?xLabel WHERE { VALUES ?x {%s} SERVICE wikibase:label {bd:serviceParam wikibase:language 'en'.}}"%" ".join(f"wd:{x}" for x in batch)
        try:
            req=urllib.request.Request("https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":q,"format":"json"}),headers={"User-Agent":"kg-usage-audit/1.0"})
            for b in json.load(urllib.request.urlopen(req,timeout=60))["results"]["bindings"]:
                out[b["x"]["value"].split("/")[-1]]=b.get("xLabel",{}).get("value","")
        except Exception as e: pass
    return out

# enrichment candidates: high demand, low supply (users want it, KG thin)
enr=sorted([q for q in classes if quad(q)=="HIdem_LOsup"], key=lambda q:-dem_type.get(q,0))[:15]
# rich-but-ignored: high supply, ~no demand (deprecation/doc-deprioritize candidates)
ign=sorted([q for q in classes if quad(q)=="LOdem_HIsup"], key=lambda q:-inst.get(q,0))[:15]
lab=labels(enr+ign)
print("\nENRICHMENT candidates (high query demand, low instance supply):")
for q in enr: print(f"  Q{q:<10} demand={dem_type.get(q,0):>7,} instances={inst.get(q,0):>9,}  {lab.get(q,'')}")
print("\nRICH-BUT-IGNORED (high instance supply, ~zero query demand):")
for q in ign: print(f"  Q{q:<10} demand={dem_type.get(q,0):>7,} instances={inst.get(q,0):>9,}  {lab.get(q,'')}")

# ---- scatter ----
xs=[inst.get(q,0)+1 for q in classes]; ys=[dem_type.get(q,0)+1 for q in classes]
plt.figure(figsize=(7,6)); plt.scatter(xs,ys,s=4,alpha=0.25,color="#2c63b8")
plt.xscale("log"); plt.yscale("log")
plt.axvline(hi_sup,ls=":",c="gray"); plt.axhline(max(1,hi_dem),ls=":",c="gray")
plt.xlabel("supply: instances per class (+1, log)"); plt.ylabel("demand: query frequency (+1, log)")
plt.title(f"Wikidata {year}: schema-element supply vs. query demand")
plt.tight_layout(); plt.savefig(f"out/wd_mismatch_{year}.png",dpi=200)
print(f"\nscatter -> out/wd_mismatch_{year}.png")
print(f"predicates: {len(dem_pred)} queried of {len(load(f'{SUP}/triples_per_pred_{year}.csv','pred','triples'))} with triples")
