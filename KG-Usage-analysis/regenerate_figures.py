"""Regenerate Fig 6 (frequency distribution) and Fig 8 (top frequent types) with native
log-scaled axes (addresses reviewer comment R2-3g: label log axes rather than plotting the
value of the logarithm on a linear axis). Inputs: committed per-element count CSVs."""
import os, re, csv
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "generated-usage-metadata"
OUT = "manuscript/texsupport.iospress-sw-master"
# (panel, file, duration_months, color, title)
GREEN, RED, BLUE = "#27ae60", "#c0392b", "#2c63b8"
PANELS = [
 ("A", "Bio2RDF log2013kg2024_combined_schema_elements.csv",            16.79, BLUE,  "Bio2RDF all 2013"),
 ("B", "Bio2RDF log2019kg2024_combined_schema_elements.csv",            29.93, BLUE,  "Bio2RDF all 2019"),
 ("C", "Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv",   29.93, RED,   "Bio2RDF robotic 2019"),
 ("D", "Bio2RDF organic log2019KG2024_combined_schema_elements.csv",    29.93, GREEN, "Bio2RDF organic 2019"),
 ("E", "Wikidata log2017kg2017_combined_schema_elements.csv",            9.43, GREEN, "Wikidata organic 2017 (KG2017)"),
 ("F", "Wikidata log2017kg2018_combined_schema_elements.csv",            9.43, GREEN, "Wikidata organic 2017 (KG2018)"),
 ("G", "Wikidata robotic log2017_kg2017_combined_schema_elements.csv",   0.88, RED,   "Wikidata robotic 2017"),
 ("H", "Wikidata organic-int1 log2018_kg2018_combined_schema_elements.csv",0.88,GREEN,"Wikidata organic 2017 (int1)"),
 ("L", "Wikidata robotic log2018_kg2018_combined_schema_elements.csv",   0.88, RED,   "Wikidata robotic 2018"),
 ("M", "Wikidata organic-int7 log2018_kg2018_combined_schema_elements.csv",0.88,GREEN,"Wikidata organic 2018 (int7)"),
]
VOC = re.compile(r'_vocabulary:(.+)$'); QID = re.compile(r'/entity/(Q\d+)$')
def is_type(e):
    m = VOC.search(e)
    if m: return m.group(1)[:1].isupper() and not e.endswith(":Resource")
    return bool(QID.search(e))   # Wikidata entity = type
def short(e):
    m = VOC.search(e)
    if m: return e.split("/")[-1]
    m = QID.search(e)
    return m.group(1) if m else e.split("/")[-1]

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
for ax, (p, f, dur, col, title) in zip(axes, PANELS):
    df = load(f); df = df[df["element"].map(is_type)].nlargest(10, "count")[::-1]
    labels = [short(e) for e in df["element"]]
    ax.barh(range(len(df)), df["count"], color=col)
    ax.set_yticks(range(len(df))); ax.set_yticklabels(labels, fontsize=6)
    ax.set_xscale("log"); ax.set_xlabel("total count", fontsize=8)
    ax.set_title(f"{p}) {title}", fontsize=9); ax.tick_params(axis="x", labelsize=7)
fig.suptitle("Top-10 most frequent schema types per dataset (log-scaled count axis)", fontsize=12)
fig.tight_layout(rect=[0,0,1,0.97]); fig.savefig(os.path.join(OUT,"image7.png"), dpi=200); plt.close(fig)
print("wrote Fig 8 -> image7.png")
