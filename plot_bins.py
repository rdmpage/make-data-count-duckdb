# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib"]
# ///
"""Bar chart of how many times datasets are cited, in grouped bins
(from dataset_citation_frequency.csv)."""
import csv

import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
SERIES = "#2a78d6"

BINS = [(1, 1), (2, 2), (3, 3), (4, 5), (6, 10), (11, 20), (21, 50),
        (51, 100), (101, 1000), (1001, None)]

with open("dataset_citation_frequency.csv") as f:
    rows = [(int(r["times_cited"]), int(r["datasets"])) for r in csv.DictReader(f)]
total = sum(n for _, n in rows)

labels, counts = [], []
for lo, hi in BINS:
    labels.append(str(lo) if lo == hi else f"{lo:,}+" if hi is None else f"{lo}–{hi:,}")
    counts.append(sum(n for k, n in rows if k >= lo and (hi is None or k <= hi)))

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150, facecolor=SURFACE)
ax.set_facecolor(SURFACE)
bars = ax.bar(labels, counts, width=0.72, color=SERIES, edgecolor=SURFACE, linewidth=2)

for bar, n in zip(bars, counts):
    pct = 100 * n / total
    pct_text = f"{pct:.1f}%" if pct >= 0.1 else f"{pct:.2f}%" if pct >= 0.01 else f"{pct:.3f}%"
    ax.annotate(f"{n:,}\n{pct_text}", (bar.get_x() + bar.get_width() / 2, n),
                xytext=(0, 4), textcoords="offset points",
                ha="center", va="bottom", fontsize=8, color=TEXT_2)

ax.set_xlabel("Times cited (distinct citing publications)", color=TEXT_2)
ax.set_ylabel("Number of datasets (millions)", color=TEXT_2)
ax.yaxis.set_major_formatter(lambda y, _: f"{y / 1e6:g}")
ax.set_ylim(0, max(counts) * 1.12)
ax.set_title(f"Most datasets are cited once: {total:,} datasets, Make Data Count release 202610",
             color=TEXT, loc="left", fontsize=11)
ax.grid(True, axis="y", color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
for side in ("left", "bottom"):
    ax.spines[side].set_color(GRID)
ax.tick_params(colors=TEXT_2)

fig.tight_layout()
fig.savefig("dataset_citation_bins.png", facecolor=SURFACE)
print("wrote dataset_citation_bins.png")
