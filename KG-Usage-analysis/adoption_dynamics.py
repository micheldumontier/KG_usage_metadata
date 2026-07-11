"""Adoption dynamics (missing-analysis #2): do newly introduced schema elements
become popular? We use the predicate as the clean signal of schema growth.

Wikidata: predicates present in the 2018 dump but absent from the 2017 dump are
"newly introduced between the logs." We ask, in the 2018 logs, (a) what fraction
of new predicates get queried at all, (b) where they rank among all queried
predicates, and (c) how many members of the most-popular core are new.

Bio2RDF: Release 3 (mid-2014) added datasets/vocabulary over Release 2. We ask
how much of the Release-3-added predicate vocabulary is queried, and its rank,
in the 2019 log."""
import csv, sys, os, re
csv.field_size_limit(sys.maxsize)
WDS = "generated-usage-metadata/wikidata-schema"
PID = re.compile(r'^wdt:(P\d+)$')

def load_set(path): return set(open(path).read().split())

def load_pred_counts(path):
    """element,count CSV -> {Pxxx: count} for wdt: predicates."""
    d = {}
    with open(path, newline='') as f:
        r = csv.reader(f); next(r)
        for row in r:
            m = PID.match(row[0].strip())
            if m: d[m.group(1)] = d.get(m.group(1), 0) + int(row[1])
    return d

def rank_report(label, used_counts, new_set):
    """Rank all queried predicates by frequency; report where new ones land."""
    ranked = sorted(used_counts.items(), key=lambda x: -x[1])
    n = len(ranked)
    rank_of = {p: i+1 for i, (p, _) in enumerate(ranked)}
    new_queried = [p for p in new_set if p in used_counts]
    print(f"\n[{label}] {n:,} distinct predicates queried")
    print(f"  new predicates (introduced 2017->2018): {len(new_set):,}")
    print(f"  ... of which queried at all in 2018: {len(new_queried):,} "
          f"({100*len(new_queried)/len(new_set):.1f}%)")
    for k in (10, 50, 100):
        top = {p for p, _ in ranked[:k]}
        nnew = len(top & new_set)
        print(f"  new predicates in top-{k} most-queried: {nnew}")
    if new_queried:
        ranks = sorted(rank_of[p] for p in new_queried)
        pct = [100*rank_of[p]/n for p in new_queried]
        med = sorted(pct)[len(pct)//2]
        best_p, best_c = ranked[min(rank_of[p] for p in new_queried)-1]
        print(f"  best-ranked new predicate: {best_p} at rank {min(ranks)}/{n} "
              f"(count {best_c:,})")
        print(f"  median rank-percentile of queried new predicates: {med:.1f}% "
              f"(100% = least queried)")

def wikidata():
    p17, p18 = load_set(f"{WDS}/preds_2017.txt"), load_set(f"{WDS}/preds_2018.txt")
    new = p18 - p17
    print(f"=== Wikidata predicate adoption ===")
    print(f"predicates: 2017={len(p17):,}  2018={len(p18):,}  newly introduced={len(new):,}")
    for lab, path in [("robotic-2018", "out/wd_robotic2018_used.csv"),
                      ("organic-2018", "out/wd_organic2018_used.csv")]:
        if os.path.exists(path):
            rank_report(lab, load_pred_counts(path), new)

def bio2rdf():
    print(f"\n=== Bio2RDF Release-3 vocabulary adoption (2019 log) ===")
    r2 = load_set("generated-usage-metadata/bio2rdf-schema-release2/r2_predicates.txt")
    r3 = load_set("generated-usage-metadata/bio2rdf-schema-release3/r3_predicates.txt")
    new = r3 - r2
    print(f"predicates: R2={len(r2):,}  R3={len(r3):,}  added in R3={len(new):,}")
    # 2019 used predicates with frequency
    path = "generated-usage-metadata/Bio2RDF log2019kg2024_combined_schema_elements.csv"
    counts = {}
    with open(path, newline='') as f:
        r = csv.reader(f); next(r)
        for row in r:
            counts[row[0].strip()] = int(row[1])
    # normalise the R2/R3 vocab IRIs and used IRIs to a comparable local form
    def local(iri): return iri.rsplit("/", 1)[-1].lower()
    new_local = {local(x) for x in new}
    used_local = {local(k): v for k, v in counts.items()}
    queried_new = {k: v for k, v in used_local.items() if k in new_local}
    print(f"  R3-added predicates queried in 2019: {len(queried_new)} "
          f"of {len(new_local)} ({100*len(queried_new)/max(len(new_local),1):.1f}%)")
    if queried_new:
        ranked = sorted(used_local.items(), key=lambda x: -x[1])
        rank_of = {k: i+1 for i, (k, _) in enumerate(ranked)}
        rr = sorted(rank_of[k] for k in queried_new)
        print(f"  best rank of an R3-added predicate: {rr[0]}/{len(ranked)}")
        top = [k for k, _ in ranked[:20]]
        print(f"  R3-added predicates in top-20 used: {len([k for k in top if k in new_local])}")

if __name__ == "__main__":
    wikidata(); bio2rdf()
