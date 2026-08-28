"""
Size-controlled comparison of schema-element coverage in organic vs robotic logs.

Reviewer 2 argued that the higher schema coverage of robotic logs may simply be a
sampling-size artifact ("more queries cover more vocabulary"). To test this, we treat
each schema-element *occurrence* in the logs as an individual and use abundance-based
(individual-based) rarefaction (Hurlbert 1971) to estimate the expected number of
distinct schema elements a sample of the SAME size would recover. We also report Chao1
asymptotic richness (Chao 1984) as a size-independent estimate of total richness.

Input: per-element occurrence-count CSVs in ../generated-usage-metadata/
Output: console table + rarefaction-curve figure used in the revised manuscript.
"""
import os
import csv
import numpy as np
from math import lgamma
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = os.path.join(os.path.dirname(__file__), "..", "generated-usage-metadata")

# (label, organic_csv, robotic_csv, total_schema_elements_TSE)
PAIRS = [
    ("Bio2RDF 2019",
     "Bio2RDF organic log2019KG2024_combined_schema_elements.csv",
     "Bio2RDF robotic log2019_kg2024_combined_schema_elements.csv",
     541),   # conforming Bio2RDF schema: 350 types + 191 predicates (Section 3.2)
    ("Wikidata 2017",
     "Wikidata log2017kg2017_combined_schema_elements.csv",
     "Wikidata robotic log2017_kg2017_combined_schema_elements.csv",
     104314),
]


def load_counts(fname):
    counts = []
    with open(os.path.join(DATA, fname), newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)  # header
        for row in r:
            if len(row) < 2:
                continue
            try:
                c = int(float(row[1]))
            except ValueError:
                continue
            if c > 0:
                counts.append(c)
    return np.array(counts, dtype=np.int64)


def hurlbert_expected_richness(counts, n):
    """Expected number of distinct elements in a sub-sample of n occurrences
    drawn without replacement (Hurlbert 1971)."""
    N = int(counts.sum())
    if n >= N:
        return float((counts > 0).sum())
    lgN = lgamma(N + 1)
    lg_Nn = lgamma(N - n + 1)
    exp_absent = 0.0
    for Ni in counts:
        rem = N - Ni
        if rem < n:           # element certainly present in any n-subsample
            continue
        # P(absent) = C(N-Ni, n) / C(N, n)
        log_p = (lgamma(rem + 1) + lg_Nn) - (lgN + lgamma(rem - n + 1))
        exp_absent += np.exp(log_p)
    return float((counts > 0).sum()) - exp_absent


def chao1(counts):
    S_obs = int((counts > 0).sum())
    f1 = int((counts == 1).sum())
    f2 = int((counts == 2).sum())
    if f2 > 0:
        return S_obs + (f1 * f1) / (2.0 * f2)
    return S_obs + f1 * (f1 - 1) / 2.0  # bias-corrected when f2 == 0


def curve(counts, npts=40):
    N = int(counts.sum())
    xs = np.unique(np.linspace(1, N, npts).astype(int))
    ys = [hurlbert_expected_richness(counts, int(x)) for x in xs]
    return xs, np.array(ys)


print(f"{'Dataset':<22}{'Sobs':>8}{'N(uses)':>12}{'Chao1':>10}{'E[S] @organic-N':>18}{'Cov@equalN':>12}")
fig, axes = plt.subplots(1, len(PAIRS), figsize=(11, 4.2))
for ax, (label, org_f, rob_f, TSE) in zip(np.atleast_1d(axes), PAIRS):
    org = load_counts(org_f)
    rob = load_counts(rob_f)
    N_org = int(org.sum())
    N_rob = int(rob.sum())
    S_org = int((org > 0).sum())
    S_rob = int((rob > 0).sum())

    # Rarefy robotic DOWN to the number of occurrences seen in the organic log.
    rob_at_org = hurlbert_expected_richness(rob, N_org)

    for nm, cnt, N, S in [("organic", org, N_org, S_org), ("robotic", rob, N_rob, S_rob)]:
        cov_full = 100.0 * S / TSE
        print(f"{label+' '+nm:<22}{S:>8}{N:>12}{chao1(cnt):>10.0f}"
              f"{(rob_at_org if nm=='robotic' else S):>18.1f}"
              f"{(100.0*rob_at_org/TSE if nm=='robotic' else cov_full):>11.2f}%")

    print(f"  --> at equal effort (N={N_org:,} occurrences), robotic recovers "
          f"{rob_at_org:.0f} elements vs organic's {S_org} "
          f"(coverage {100.0*rob_at_org/TSE:.2f}% vs {100.0*S_org/TSE:.2f}%)\n")

    xo, yo = curve(org)
    xr, yr = curve(rob)
    ax.plot(xr, yr, "-", color="#c0392b", label="robotic")
    ax.plot(xo, yo, "-", color="#27ae60", label="organic")
    ax.axvline(N_org, ls=":", color="gray", lw=1)
    ax.set_title(label)
    ax.set_xlabel("schema-element occurrences sampled")
    ax.set_ylabel("expected distinct schema elements")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=9)

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "rarefaction_organic_vs_robotic.png")
plt.savefig(out, dpi=200)
print("figure ->", out)
