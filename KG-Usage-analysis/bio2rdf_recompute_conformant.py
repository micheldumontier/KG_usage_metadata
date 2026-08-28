"""Recompute every Bio2RDF figure against a schema that matches the paper's stated definition.

Section 3.2 states that the Bio2RDF schema consists of IRIs matching
http://Bio2RDF.org/DATASET_vocabulary:ELEMENT, and that non-conforming IRIs are excluded.
The released schema applied that filter to types (350/350 conform) but not to predicates
(191/195), because schema_gnrator_Bio2RDF.py filters `stype` and not `?p`. Four W3C terms
therefore entered the universe: rdf:type, rdfs:subClassOf, owl:sameAs, owl:sourceIndividual.

This matters beyond bookkeeping. rdf:type is 74% of the organic log's occurrences but 29% of
the robotic log's, so it inflates the organic "sampling effort" roughly fourfold while adding
a single element to richness, which is exactly the pathology individual-based rarefaction is
most sensitive to. It is also the only foreign vocabulary in any of the three KG universes:
Wikidata's 930 entries are all P-numbers and DBpedia's 3,024 are all DBpedia terms.

Recomputes: TSE, used elements, coverage, rarefaction (with bootstrap CI), singletons and
concentration, both as published and under the conforming definition.
"""
import csv, os, re, random
from math import lgamma, exp, log

G = "generated-usage-metadata"
TEMPL = re.compile(r'^http://[Bb]io2rdf\.org/\w+_vocabulary:')
NONCONF = ['http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
           'http://www.w3.org/2000/01/rdf-schema#subClassOf',
           'http://www.w3.org/2002/07/owl#sameAs',
           'http://www.w3.org/2002/07/owl#sourceIndividual']

kind = {}
for r in list(csv.reader(open(f"{G}/bio2rdf-schema/schema_elements_26subgraphs.csv")))[1:]:
    if r: kind[r[0].strip()] = r[1].strip()
TSE26_pub = len(kind)
TSE26_fix = sum(1 for e in kind if TEMPL.match(e))
s17 = [r[0].strip() for r in list(csv.reader(open(f"{G}/schema-Bio2RDF-17Subgraphs.csv")))[1:] if r]
TSE17_pub, TSE17_fix = len(s17), sum(1 for e in s17 if TEMPL.match(e))

LOGS = [("Bio2RDF All log2013_kg2024",  "Bio2RDF log2013kg2024_combined_schema_elements.csv",        TSE17_pub, TSE17_fix),
        ("Bio2RDF All log2019_kg2024",  "Bio2RDF log2019kg2024_combined_schema_elements.csv",        TSE26_pub, TSE26_fix),
        ("Bio2RDF robotic log2019",     "Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv", TSE26_pub, TSE26_fix),
        ("Bio2RDF organic log2019",     "Bio2RDF organic log2019KG2024_combined_schema_elements.csv",  TSE26_pub, TSE26_fix)]

def load(f, conform):
    d = {}
    for row in csv.reader(open(os.path.join(G, f))):
        if row and row[0] != "Schema Element":
            k = row[0].strip()
            if conform and not TEMPL.match(k): continue
            try:
                v = int(float(row[1]))
                if v > 0: d[k] = v
            except ValueError: pass
    return d

def gini(v):
    v = sorted(v); n = len(v); s = sum(v)
    if n == 0 or s == 0: return 0.0
    return (2*sum((i+1)*x for i, x in enumerate(v)))/(n*s) - (n+1)/n
def pielou(v):
    s = sum(v); n = len(v)
    if n <= 1 or s == 0: return 0.0
    H = -sum((x/s)*log(x/s) for x in v if x > 0)
    return H/log(n)
def hurlbert(counts, n):
    N = sum(counts)
    if n >= N: return float(len(counts))
    lc = lgamma(N+1)-lgamma(n+1)-lgamma(N-n+1); t = 0.0
    for Ni in counts:
        if N-Ni >= n: t += 1-exp(lgamma(N-Ni+1)-lgamma(n+1)-lgamma(N-Ni-n+1)-lc)
        else: t += 1.0
    return t

print("TSE  26 subgraphs: published %d  ->  conforming %d" % (TSE26_pub, TSE26_fix))
print("TSE  17 subgraphs: published %d  ->  conforming %d" % (TSE17_pub, TSE17_fix))
print("\n%-30s %-26s %-26s" % ("log", "AS PUBLISHED", "CONFORMING"))
print("%-30s %8s %7s %9s %8s %7s %9s" % ("", "USE", "occ", "cov", "USE", "occ", "cov"))
for nm, f, tp, tf in LOGS:
    a, b = load(f, False), load(f, True)
    print("%-30s %8d %7d %8.2f%% %8d %7d %8.2f%%" % (nm, len(a), sum(a.values()), 100*len(a)/tp,
                                                     len(b), sum(b.values()), 100*len(b)/tf))

print("\n--- singletons (2019) ---")
for nm, f, tp, tf in LOGS[2:]:
    for lbl, conform, tse in (("published", False, tp), ("conforming", True, tf)):
        d = load(f, conform); sg = sum(1 for v in d.values() if v == 1)
        nosg = {k: v for k, v in d.items() if v > 1}
        print("  %-26s %-11s used=%4d singletons=%3d (%.0f%%)  cov=%5.1f%%  cov w/o singletons=%5.1f%%"
              % (nm, lbl, len(d), sg, 100*sg/max(1, len(d)), 100*len(d)/tse, 100*len(nosg)/tse))

print("\n--- concentration ---")
for nm, f, tp, tf in LOGS:
    for lbl, conform, tse in (("published", False, tp), ("conforming", True, tf)):
        d = load(f, conform); v = sorted(d.values(), reverse=True); tot = sum(v)
        top10 = 100*sum(v[:10])/tot
        cum = 0; p80 = 0
        for i, x in enumerate(v, 1):
            cum += x
            if cum >= 0.8*tot: p80 = 100*i/len(v); break
        full = v + [0]*(tse-len(v))
        print("  %-26s %-11s N=%4d Gini=%.3f J=%.3f top10=%5.1f%% P80=%5.2f%%  Gini*=%.3f J*=%.3f"
              % (nm, lbl, len(v), gini(v), pielou(v), top10, p80, gini(full), pielou(full)))

print("\n--- rarefaction: organic vs robotic at equal effort (2019) ---")
random.seed(20260820)
for lbl, conform, tse in (("published", False, TSE26_pub), ("conforming", True, TSE26_fix)):
    org = load(LOGS[3][1], conform); rob = load(LOGS[2][1], conform)
    N = sum(org.values()); S = len(org)
    est = hurlbert(list(rob.values()), N)
    pool = [e for e, c in rob.items() for _ in range(c)]
    reps = []
    for _ in range(400):
        reps.append(len(set(random.sample(pool, N))))
    reps.sort(); lo, hi = reps[int(.025*len(reps))], reps[int(.975*len(reps))-1]
    print("  %-11s organic N=%-6d S=%-4d (%.1f%%) | robotic rarefied=%.0f (%.1f%%) "
          "| ratio=%.2fx  bootstrap 95%% CI [%.2f, %.2f]"
          % (lbl, N, S, 100*S/tse, est, 100*est/tse, est/S, lo/S, hi/S))
