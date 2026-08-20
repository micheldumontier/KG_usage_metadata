"""Regenerate Fig 6 (frequency distribution) and Fig 8 (top frequent types) with native
log-scaled axes (addresses reviewer comment R2-3g: label log axes rather than plotting the
value of the logarithm on a linear axis). Inputs: committed per-element count CSVs."""
import os, re, csv
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

D = "generated-usage-metadata"
OUT = "manuscript/texsupport.iospress-sw-master"
# (panel, file, duration_months, color, title)
GREEN, RED, BLUE = "#27ae60", "#c0392b", "#2c63b8"
PANELS = [
 ("A", "Bio2RDF log2013kg2024_combined_schema_elements.csv",            16.79, BLUE,  "Bio2RDF all 2013"),
 ("B", "Bio2RDF log2019kg2024_combined_schema_elements.csv",            29.93, BLUE,  "Bio2RDF all 2019"),
 ("C", "Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv",   29.93, RED,   "Bio2RDF robotic 2019"),
 ("D", "Bio2RDF organic log2019KG2024_combined_schema_elements.csv",    29.93, GREEN, "Bio2RDF organic 2019"),
 ("E", "Wikidata log2017kg2017_combined_schema_elements.csv",            9.43, GREEN, "WD organic 2017 (KG2017)"),
 ("F", "Wikidata log2017kg2018_combined_schema_elements.csv",            9.43, GREEN, "WD organic 2017 (KG2018)"),
 ("G", "Wikidata robotic log2017_kg2017_combined_schema_elements.csv",   0.88, RED,   "WD robotic 2017"),
 ("H", "Wikidata organic-int1 log2018_kg2018_combined_schema_elements.csv",0.88,GREEN,"WD organic 2017 (int1)"),
 ("L", "Wikidata robotic log2018_kg2018_combined_schema_elements.csv",   0.88, RED,   "WD robotic 2018"),
 ("M", "Wikidata organic-int7 log2018_kg2018_combined_schema_elements.csv",0.88,GREEN,"WD organic 2018 (int7)"),
]
VOC = re.compile(r'_vocabulary:(.+)$'); QID = re.compile(r'/entity/(Q\d+)$')

# Bio2RDF type/predicate membership is read from the RELEASED schema file rather than guessed
# from capitalization. The old rule (uppercase char after "_vocabulary:") misclassified 28 of
# the 350 released types whose local names begin lowercase (ctd_vocabulary:clv,
# pharmgkb_vocabulary:disease-gene-Association, ...), which wrongly dropped
# ctd_vocabulary:Gene-Disease-Association -- the 4th-largest type -- from panel D.
_SCHEMA_KIND = {}
with open(os.path.join(D, "bio2rdf-schema", "schema_elements_26subgraphs.csv")) as _f:
    _r = csv.reader(_f); next(_r)
    for _row in _r:
        if len(_row) > 1: _SCHEMA_KIND[_row[0].strip()] = _row[1].strip()

# Wikidata QID -> English label, extracted from the 2017 dump (see scripts/wd_labels.tsv).
# Restores the natural-language names the earlier version of this figure displayed.
WD_LABEL = {}
_lab = os.path.join("generated-usage-metadata", "wikidata-schema", "qid_labels_en.tsv")
if os.path.exists(_lab):
    for _line in open(_lab):
        if "\t" in _line:
            _q, _l = _line.rstrip("\n").split("\t", 1); WD_LABEL[_q] = _l

def is_type(e):
    if VOC.search(e): return _SCHEMA_KIND.get(e) == "type"
    return bool(QID.search(e))   # Wikidata entity = type
def short(e):
    m = VOC.search(e)
    if m: return e.split("/")[-1]
    m = QID.search(e)
    if m:
        q = m.group(1)
        return "%s (%s)" % (WD_LABEL[q], q) if q in WD_LABEL else q
    return e.split("/")[-1]

def load(f):
    df = pd.read_csv(os.path.join(D, f))
    df.rename(columns={df.columns[0]: "element", df.columns[1]: "count"}, inplace=True)
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    return df.dropna()

# ---------- Fig 6: frequency distribution (rank vs normalized monthly count, log y) ----------
fig, axes = plt.subplots(2, 5, figsize=(18, 7)); axes = axes.ravel()
for ax, (p, f, dur, col, title) in zip(axes, PANELS):
    df = load(f); y = sorted(df["count"]/dur, reverse=True); x = range(1, len(y)+1)
    ax.plot(x, y, color=col, lw=1.2)
    ax.set_yscale("log"); ax.set_xscale("log")
    ax.set_title(f"{p}) {title}", fontsize=9)
    ax.set_xlabel("schema element rank", fontsize=8)
    ax.set_ylabel("uses / month", fontsize=8)
    ax.tick_params(labelsize=7)
fig.suptitle("Frequency distribution of schema-element usage (log-scaled axes)", fontsize=12)
fig.tight_layout(rect=[0,0,1,0.97]); fig.savefig(os.path.join(OUT,"image10.png"), dpi=200); plt.close(fig)
print("wrote Fig 6 -> image10.png")

# ---------- Fig 8: top-10 frequent schema TYPES (horizontal bars, log x) ----------
fig, axes = plt.subplots(2, 5, figsize=(20, 8)); axes = axes.ravel()
# top-10 type set per panel, so we can bold the elements shared by each compared pair
TOP = {}
for p, f, dur, col, title in PANELS:
    _d = load(f); TOP[p] = set(_d[_d["element"].map(is_type)].nlargest(10, "count")["element"])
PAIRS = [("A","B"), ("C","D"), ("E","F"), ("G","H"), ("L","M")]
SHARED = {}
for a, b in PAIRS:
    common = TOP[a] & TOP[b]
    SHARED[a] = common; SHARED[b] = common

for ax, (p, f, dur, col, title) in zip(axes, PANELS):
    df = load(f); df = df[df["element"].map(is_type)].nlargest(10, "count")[::-1]
    labels = [short(e) for e in df["element"]]
    ax.barh(range(len(df)), df["count"], color=col)
    ax.set_yticks(range(len(df))); ax.set_yticklabels(labels, fontsize=6)
    for tick, e in zip(ax.get_yticklabels(), df["element"]):
        if e in SHARED.get(p, ()): tick.set_fontweight("bold")
    ax.set_xscale("log"); ax.set_xlabel("total count", fontsize=8)
    # On panels whose counts span less than a decade, matplotlib labels the minor ticks too and
    # the labels collide into an unreadable smear. Keep decade labels only.
    ax.xaxis.set_major_locator(mticker.LogLocator(base=10.0))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_title(f"{p}) {title}", fontsize=8); ax.tick_params(axis="x", labelsize=7)
fig.suptitle("Top-10 most frequent schema types per dataset (log-scaled count axis)", fontsize=12)
fig.tight_layout(rect=[0,0,1,0.97]); fig.savefig(os.path.join(OUT,"image7.png"), dpi=200); plt.close(fig)
print("wrote Fig 8 -> image7.png")
