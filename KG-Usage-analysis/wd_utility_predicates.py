"""Predicate-suggestion counterpart to the type-suggestion experiment.

Review comment: "It is also unclear why only type/class suggestions are evaluated, while the
generated usage metadata also covers predicates and predicate suggestion is equally relevant
to SPARQL autocomplete."

Same design as wd_utility_ranking.py, but over PREDICATES instead of classes:
  train  = early-2017 organic Wikidata logs
  test   = 2018 organic log (int7)
  usage ranking  = predicate frequency in train (deduplicated queries)
  content ranking = triples per predicate in the 2017 dump (the content-side analogue of
                    instances-per-class, and again the only ranking a maintainer can compute
                    without log access)
Reports top-k demand coverage, nDCG@k with graded relevance, and demand-weighted MRR.
"""
import csv, gzip, os, json, subprocess, tempfile, urllib.parse, importlib.util, math
csv.field_size_limit(1 << 30)
spec = importlib.util.spec_from_file_location("pv", "Schema-coverage-method/sparql_log_preprocess.py")
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
NODE = os.path.expanduser("~/.local/bin/node")
EXW  = os.path.expanduser("~/.local/sparqljs-worker/extract_worker.js")
WD = "data/logs/wikidata"
TRAIN = [f"{WD}/int1_2017_organic.tsv.gz", f"{WD}/2017-07-10_2017-08-06_organic.tsv.gz",
         f"{WD}/2017-08-07_2017-09-03_organic.tsv.gz"]
TEST  = [f"{WD}/int7_2018_organic.tsv.gz"]
CACHE = "out/wd_utility_pred_cache.json"

def wclean(q): return pv.normalize_ws(pv.HTTP_TAIL.sub('', urllib.parse.unquote_plus(q)))

def parallel(prepped, nw=14):
    chunks = [prepped[i::nw] for i in range(nw)]; procs = []
    for ch in chunks:
        ti = tempfile.NamedTemporaryFile('w', suffix='.nd', delete=False)
        for x in ch: ti.write(json.dumps(x) + "\n")
        ti.close(); to = ti.name + ".o"
        procs.append((subprocess.Popen([NODE, EXW], stdin=open(ti.name), stdout=open(to, 'w')), ti.name, to))
    out = [None] * len(prepped)
    for i, (p, ti, to) in enumerate(procs):
        p.wait()
        rs = [json.loads(l) for l in open(to)]
        for j, r in enumerate(rs): out[i + j * nw] = r
        os.remove(ti); os.remove(to)
    return out

PROP = "http://www.wikidata.org/prop/direct/"
def pred_demand(files):
    seen = set()
    for path in files:
        with gzip.open(path, 'rt', encoding='utf-8', errors='replace') as f:
            r = csv.reader(f, delimiter='\t'); h = next(r); qi = h.index('anonymizedQuery')
            for row in r:
                if len(row) > qi: seen.add(wclean(row[qi]))
    qs = list(seen); res = parallel([pv.add_prefixes(q, False) for q in qs])
    dem = {}
    for rr in res:                      # deduplicated: each distinct query counts once
        if not rr.get("v"): continue
        for p in set(rr.get("preds", [])):
            if p.startswith(PROP):
                pid = p[len(PROP):]
                dem[pid] = dem.get(pid, 0) + 1
    return dem

if os.path.exists(CACHE):
    c = json.load(open(CACHE)); train, test = c["train"], c["test"]; print("loaded cache")
else:
    print("parsing TRAIN...", flush=True); train = pred_demand(TRAIN)
    print("parsing TEST...", flush=True);  test  = pred_demand(TEST)
    os.makedirs("out", exist_ok=True); json.dump({"train": train, "test": test}, open(CACHE, "w"))

supply = {}
for r in csv.DictReader(open("generated-usage-metadata/wikidata-supply/triples_per_pred_2017.csv")):
    try: supply[r["pred"]] = int(r["triples"])
    except Exception: pass

# Common candidate universe (review round 4, comment #13): usage and supply previously
# drew from different candidate sets -- usage only from predicates observed in TRAIN,
# supply from whatever triples_per_pred_2017.csv happens to list (3,668 predicates --
# MORE than the 930-predicate schema universe, since that file isn't restricted to the
# wdt:P-direct namespace the schema definition uses). Align both to the actual 2017
# predicate schema instead: this both restricts supply's over-inclusive candidate set
# and extends usage's under-inclusive one, so a coverage/nDCG difference reflects
# ranking quality, not which candidate set happened to be larger.
SCHEMA = [l.strip() for l in open("generated-usage-metadata/wikidata-schema/preds_2017.txt") if l.strip()]
U = sorted(SCHEMA, key=lambda k: (-train.get(k, 0), k))
S = sorted(SCHEMA, key=lambda k: (-supply.get(k, 0), k))
total = sum(test.values())
print("TRAIN distinct preds=%d  TEST distinct=%d  TEST refs=%d" % (len(train), len(test), total))

def cov(rank, k):
    s = set(rank[:k]); return 100 * sum(test[t] for t in test if t in s) / max(1, total)
def idcg(k):
    ideal = sorted(test.values(), reverse=True)[:k]
    return sum(r / math.log2(i + 2) for i, r in enumerate(ideal))
def ndcg(rank, k):
    z = idcg(k)
    return 100 * sum(test.get(t, 0) / math.log2(i + 2) for i, t in enumerate(rank[:k])) / z if z else 0.0
def wmrr(rank):
    pos = {t: i + 1 for i, t in enumerate(rank)}
    return sum(d / pos[t] for t, d in test.items() if t in pos) / total

print("\n%6s | %14s %15s | %11s %12s" % ("k", "nDCG usage", "nDCG supply", "cov usage", "cov supply"))
rows = []
# Comment #13 also flagged reporting a top-1000 cutoff against a 930-predicate schema
# (the old, pre-Wikidata-native-definition figure was 934; the predicate universe is
# now 930): past k=len(SCHEMA), coverage trivially saturates for both rankings by
# construction, so the last reported k is the schema size itself, not a fixed 1000.
K_VALUES = sorted(set([10, 50, 100, 500] + [len(SCHEMA)]))
for k in K_VALUES:
    r = (k, ndcg(U, k), ndcg(S, k), cov(U, k), cov(S, k)); rows.append(r)
    print("%6d | %13.1f%% %14.1f%% | %10.1f%% %11.1f%%" % r)
mu, ms = wmrr(U), wmrr(S)
print("\ndemand-weighted MRR: usage=%.4f  supply=%.4f  ratio=%.1fx" % (mu, ms, mu / ms if ms else float('inf')))
with open("out/wd_utility_predicates.csv", "w", newline='') as f:
    w = csv.writer(f); w.writerow(["k", "ndcg_usage", "ndcg_supply", "cov_usage", "cov_supply"])
    for r in rows: w.writerow(["%d" % r[0]] + ["%.2f" % x for x in r[1:]])
    w.writerow([]); w.writerow(["MRRw_usage", "MRRw_supply"]); w.writerow(["%.4f" % mu, "%.4f" % ms])
print("wrote out/wd_utility_predicates.csv")
