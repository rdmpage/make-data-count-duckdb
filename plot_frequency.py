# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib", "numpy"]
# ///
"""Log-log plot of dataset citation frequency (from dataset_citation_frequency.csv)."""
import csv

import matplotlib.pyplot as plt
import numpy as np

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
SERIES = {"accession": "#2a78d6", "doi": "#eb6834"}
LABELS = {"accession": "Accession", "doi": "DOI"}

with open("dataset_citation_frequency.csv") as f:
    rows = list(csv.DictReader(f))
k = np.array([int(r["times_cited"]) for r in rows])


def mle_alpha(k, n):
    """Discrete power-law exponent (Clauset et al. approximation, xmin = 1)."""
    keep = n > 0
    return 1 + n[keep].sum() / (n[keep] * np.log(k[keep] / 0.5)).sum()


fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150, facecolor=SURFACE)
ax.set_facecolor(SURFACE)

for key in ("accession", "doi"):
    n = np.array([int(r[key]) for r in rows])
    keep = n > 0
    alpha = mle_alpha(k, n)
    ax.scatter(k[keep], n[keep], s=14, color=SERIES[key], alpha=0.75,
               edgecolors=SURFACE, linewidths=0.6,
               label=f"{LABELS[key]} ({n.sum():,} datasets, α ≈ {alpha:.2f})")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Times cited (distinct citing publications)", color=TEXT_2)
ax.set_ylabel("Number of datasets", color=TEXT_2)
ax.set_title("How often are datasets cited? Make Data Count, release 202610",
             color=TEXT, loc="left", fontsize=12)
ax.grid(True, which="major", color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(GRID)
ax.tick_params(colors=TEXT_2, which="both")
ax.legend(frameon=False, labelcolor=TEXT)

fig.tight_layout()
fig.savefig("dataset_citation_frequency.png", facecolor=SURFACE)
print("wrote dataset_citation_frequency.png")
