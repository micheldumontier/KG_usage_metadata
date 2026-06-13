"""Bootstrap (Monte-Carlo) CIs for the size-controlled coverage comparison (Sec. 4.6).
At EQUAL sampling effort (n = organic total occurrences), we subsample the robotic
occurrences R times without replacement and count distinct schema elements recovered,
giving a 95% CI on robotic-rarefied richness. We compare it to the organic observed
richness to test whether the robotic>organic breadth gap is real (Bio2RDF) or a
size artifact (Wikidata)."""
import os, csv, numpy as np
DATA="generated-usage-metadata"
PAIRS=[
 ("Bio2RDF 2019","Bio2RDF organic log2019KG2024_combined_schema_elements.csv",
  "Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv",545),
 ("Wikidata 2017","Wikidata log2017kg2017_combined_schema_elements.csv",
  "Wikidata robotic log2017_kg2017_combined_schema_elements.csv",104314),
]
def load(fname):
    cs=[]
    with open(os.path.join(DATA,fname),newline="",encoding="utf-8") as f:
        r=csv.reader(f); next(r)
        for row in r:
            if len(row)<2: continue
            try: c=int(float(row[1]))
            except ValueError: continue
            if c>0: cs.append(c)
    return np.array(cs,dtype=np.int64)
def mc_rarefy(counts,n,R=400,seed=20260612):
    """Monte-Carlo: distinct elements in n occurrences subsampled w/o replacement."""
    N=int(counts.sum())
    if n>=N: return np.full(R,float((counts>0).sum()))
    occ=np.repeat(np.arange(len(counts)),counts)   # element id per occurrence
    rng=np.random.default_rng(seed); out=np.empty(R)
    for b in range(R):
        idx=rng.choice(N,size=n,replace=False)
        out[b]=np.unique(occ[idx]).size
    return out
for label,oc,rc,TSE in PAIRS:
    org=load(oc); rob=load(rc)
    n=int(org.sum()); So=int((org>0).sum()); Sr_full=int((rob>0).sum())
    mc=mc_rarefy(rob,n)
    lo,med,hi=np.percentile(mc,[2.5,50,97.5])
    print(f"\n[{label}]  equal effort n={n:,} occurrences (= organic total)")
    print(f"  organic observed:        {So:,} distinct ({100*So/TSE:.1f}% of TSE)")
    print(f"  robotic (full sample):   {Sr_full:,} distinct ({100*Sr_full/TSE:.1f}%)")
    print(f"  robotic rarefied to n:   {med:.0f} distinct  95% CI [{lo:.0f}, {hi:.0f}]  "
          f"({100*med/TSE:.1f}% [{100*lo/TSE:.1f}, {100*hi/TSE:.1f}])")
    ratio_lo, ratio_hi = lo/So, hi/So
    sig = "SIGNIFICANT (CI excludes organic)" if lo>So else ("not significant" if hi>=So>=lo else "robotic<organic")
    print(f"  robotic/organic ratio at equal effort: {med/So:.2f}x  95% CI [{ratio_lo:.2f}, {ratio_hi:.2f}]  -> {sig}")
