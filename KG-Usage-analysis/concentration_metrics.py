"""Concentration of schema-element usage (reviewer Concern #2: coverage treats
every element equally). For each manuscript dataset we read the per-element
usage-frequency vector (unique-query counts, the same basis as Tables 4-5) and
report, beside the breadth metric (coverage / N distinct elements):
  - Gini coefficient of the usage frequencies (0 = perfectly even, 1 = all mass on one element)
  - Pielou evenness J = H / ln(N)  (normalised Shannon entropy; 1 = even)
  - top-10 share  = fraction of all references captured by the 10 most-used elements
  - P80           = fraction of used elements needed to capture 80% of references
Outputs out/concentration_metrics.csv and prints LaTeX rows."""
import csv, sys, math, os
csv.field_size_limit(sys.maxsize)

# All vectors are the PUBLISHED *_combined_schema_elements.csv artifacts, i.e. the
# exact datasets behind Tables 4-5 (verified: implied coverage reproduces Table 5).
# TSE = total schema elements of the reference KG version, so we can also report
# concentration over the FULL schema universe (unused elements enter as zeros).
G = "generated-usage-metadata"
TSE_BIO_26, TSE_BIO_17 = 545, 399           # 2019/2013 Bio2RDF reference sets
TSE_WD_2017, TSE_WD_2018 = 104286, 98436    # types+preds per dump
DATASETS = [
    ("Bio2RDF All-2013",      f"{G}/Bio2RDF log2013kg2024_combined_schema_elements.csv",       TSE_BIO_17),
    ("Bio2RDF All-2019",      f"{G}/Bio2RDF log2019kg2024_combined_schema_elements.csv",        TSE_BIO_26),
    ("Bio2RDF robotic-2019",  f"{G}/Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv", TSE_BIO_26),
    ("Bio2RDF organic-2019",  f"{G}/Bio2RDF organic log2019KG2024_combined_schema_elements.csv", TSE_BIO_26),
    ("Wikidata robotic-2017", f"{G}/Wikidata robotic log2017_kg2017_combined_schema_elements.csv", TSE_WD_2017),
    ("Wikidata robotic-2018", f"{G}/Wikidata robotic log2018_kg2018_combined_schema_elements.csv", TSE_WD_2018),
    ("Wikidata organic-2017", f"{G}/Wikidata log2017kg2017_combined_schema_elements.csv",        TSE_WD_2017),
    ("Wikidata organic-2018", f"{G}/Wikidata log2017kg2018_combined_schema_elements.csv",        TSE_WD_2018),
]

def load_counts(path):
    with open(path, newline='') as f:
        r = csv.reader(f); h = next(r)
        # count column = the one named TotalCount / count, else last numeric col
        lower = [c.strip().lower() for c in h]
        ci = lower.index("totalcount") if "totalcount" in lower else (
             lower.index("count") if "count" in lower else len(h)-1)
        out = []
        for row in r:
            if len(row) <= ci or not row[ci].strip(): continue
            try: out.append(int(float(row[ci])))
            except ValueError: continue
        return [c for c in out if c > 0]

def gini(x):
    x = sorted(x); n = len(x); s = sum(x)
    if n == 0 or s == 0: return float('nan')
    cum = sum((i+1)*v for i, v in enumerate(x))
    return (2*cum - (n+1)*s) / (n*s)

def pielou(x):
    n = len(x); s = sum(x)
    if n <= 1 or s == 0: return float('nan')
    H = -sum((v/s)*math.log(v/s) for v in x if v > 0)
    return H / math.log(n)

def top_share(x, k=10):
    s = sum(x)
    return sum(sorted(x, reverse=True)[:k]) / s if s else float('nan')

def p80(x):
    s = sum(x); n = len(x)
    if s == 0: return float('nan')
    acc = 0
    for i, v in enumerate(sorted(x, reverse=True), 1):
        acc += v
        if acc >= 0.8*s: return i/n
    return 1.0

def main():
    rows = []
    for label, path, tse in DATASETS:
        if not os.path.exists(path):
            print(f"!! missing {path}", file=sys.stderr); continue
        x = load_counts(path)
        # full-universe vector: unused schema elements enter as zeros (TSE-N of them)
        xf = x + [0]*max(tse - len(x), 0)
        rows.append((label, len(x), tse, sum(x), gini(x), pielou(x), top_share(x, 10), p80(x),
                     gini(xf), pielou(xf)))
    os.makedirs("out", exist_ok=True)
    with open("out/concentration_metrics.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["dataset", "N_used", "TSE", "total_refs", "gini_used", "pielou_used",
                    "top10_share", "P80", "gini_fulluniverse", "pielou_fulluniverse"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], f"{r[4]:.3f}", f"{r[5]:.3f}", f"{r[6]:.3f}",
                        f"{r[7]:.4f}", f"{r[8]:.3f}", f"{r[9]:.3f}"])
    print(f"{'dataset':24} {'N_used':>7} {'TSE':>8} {'Gini':>6} {'J':>6} {'top10':>6} {'P80':>7} "
          f"{'Gini*':>6} {'J*':>6}   (* = full schema universe, incl. unused)")
    for label, n, tse, tot, g, j, t10, p, gf, jf in rows:
        print(f"{label:24} {n:>7,} {tse:>8,} {g:>6.3f} {j:>6.3f} {t10:>6.3f} {100*p:>6.2f}% "
              f"{gf:>6.3f} {jf:>6.3f}")
    print("\n% LaTeX rows: dataset & N & Gini & J & top10\\% & P80\\% & Gini(full)")
    for label, n, tse, tot, g, j, t10, p, gf, jf in rows:
        print(f"{label} & {n:,} & {g:.3f} & {j:.3f} & {100*t10:.1f}\\% & {100*p:.2f}\\% & {gf:.3f} \\\\")

if __name__ == "__main__": main()
