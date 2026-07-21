"""
Figure 1 for the editorial
"Cheminformatics as a core driver of molecular discovery and design"
Martinez-Mayorga K. & Zdrazil B., Journal of Cheminformatics (2026)

Reproduces the topic-evolution bubble plot from a PubMed .nbib export of all
Journal of Cheminformatics articles published between 2015 and 2025.

PubMed query used to generate the export:
    "Journal of Cheminformatics"[Journal] AND 2015:2025[dp]
    -> Send to -> Citation manager -> .nbib

Dependencies:
    python >= 3.9
    numpy, scikit-learn, matplotlib

Usage:
    python figure1_topics.py path/to/pubmed_export.nbib
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.decomposition import NMF
from sklearn.feature_extraction import text as sktext
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

N_TOPICS = 9                     # number of NMF components
RANDOM_STATE = 42                # reproducibility
YEAR_RANGE = range(2015, 2026)   # 2015..2025 inclusive
NGRAM_RANGE = (1, 2)
MIN_DF = 8                       # minimum document frequency for vocabulary
MAX_DF = 0.5                     # maximum document frequency (drop boilerplate)
MAX_ITER = 600

# Hand-curated topic labels, derived after inspecting the top terms per NMF
# component (see print_top_terms() below). If you re-run with a different
# RANDOM_STATE or N_TOPICS these indices will need to be re-assigned.
TOPIC_LABELS = {
    0: "Drug discovery, QSAR & bioactivity",
    1: "Infrastructure, databases & mass spectrometry",
    2: "Protein–ligand binding & docking",
    3: "Generative models & molecular design",
    4: "Chemical text mining & entity recognition",
    5: "Reaction prediction & retrosynthesis",
    6: "Virtual screening & similarity",
    7: "Machine learning & property prediction",
    8: "Natural products",
}

# Row order (top -> bottom in the figure). Designed so the eye reads the
# AI-era clusters at the bottom-right, where the bubbles grow over time.
ROW_ORDER = [4, 6, 8, 1, 0, 2, 5, 3, 7]

# Colours grouped by topic family
TOPIC_COLORS = {
    4: "#8c9aa6", 6: "#8c9aa6", 8: "#5a8a8a",   # legacy / steady foundational
    1: "#3d6b7d", 0: "#2f5266",                  # core infra + bioactivity
    2: "#c98a3a", 5: "#d96e3f",                  # structure-based + reactions
    3: "#c0453b", 7: "#9b2d2d",                  # AI-era
}

# Domain stopwords stacked on top of sklearn's English stoplist
EXTRA_STOPWORDS = """
using used use based method methods approach approaches model models result results
study studies data dataset datasets paper present presented propose proposed novel new
provide provides provided show shows shown also however thus therefore well within
available open access article scientific contribution license author authors j cheminform
journal cheminformatics one two three high low large small set sets number different
including based via given respectively obtained compared comparison performance
http https github com org doi www figure table additional file material supplementary
""".split()


# ---------------------------------------------------------------------------
# 1. Parse the .nbib file
# ---------------------------------------------------------------------------

def parse_nbib(path: Path) -> list[dict]:
    """Parse a PubMed .nbib export into a list of records."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\r?\n\r?\n", raw)
    records = []

    for block in blocks:
        if "PMID-" not in block:
            continue

        # Tag-based fields; continuation lines start with 6 spaces.
        fields: dict[str, list[str]] = {}
        current_tag: str | None = None
        for line in block.split("\n"):
            line = line.rstrip("\r")
            m = re.match(r"^([A-Z]{2,4})\s*-\s?(.*)$", line)
            if m:
                current_tag = m.group(1)
                fields.setdefault(current_tag, []).append(m.group(2))
            elif line.startswith("      ") and current_tag is not None:
                fields[current_tag][-1] += " " + line.strip()

        title = " ".join(fields.get("TI", [])).strip()
        abstract = " ".join(fields.get("AB", [])).strip()
        if not abstract:
            continue  # skip records without an abstract

        year_match = re.match(r"(\d{4})", fields.get("DP", [""])[0])
        if not year_match:
            continue
        year = int(year_match.group(1))

        records.append({
            "pmid": fields.get("PMID", [""])[0].strip(),
            "year": year,
            "title": title,
            "abstract": abstract,
        })

    return records


# ---------------------------------------------------------------------------
# 2. Topic model
# ---------------------------------------------------------------------------

def fit_topic_model(records: list[dict]):
    """Fit an NMF topic model on title (weighted 2x) + abstract."""
    docs = [(r["title"] + " ") * 2 + r["abstract"] for r in records]

    stopwords = list(sktext.ENGLISH_STOP_WORDS.union(EXTRA_STOPWORDS))

    vectorizer = TfidfVectorizer(
        max_df=MAX_DF,
        min_df=MIN_DF,
        ngram_range=NGRAM_RANGE,
        stop_words=stopwords,
        token_pattern=r"[A-Za-z][A-Za-z\-]{2,}",
    )
    X = vectorizer.fit_transform(docs)

    nmf = NMF(
        n_components=N_TOPICS,
        init="nndsvd",
        random_state=RANDOM_STATE,
        max_iter=MAX_ITER,
    )
    W = nmf.fit_transform(X)     # docs x topics
    H = nmf.components_          # topics x terms
    vocab = np.array(vectorizer.get_feature_names_out())

    return W, H, vocab


def print_top_terms(H: np.ndarray, vocab: np.ndarray, n: int = 14) -> None:
    """Print top terms per topic — use this to assign or update TOPIC_LABELS."""
    print("\n=== Top terms per topic ===")
    for k in range(H.shape[0]):
        top_idx = np.argsort(H[k])[::-1][:n]
        print(f"Topic {k:>2}: " + ", ".join(vocab[top_idx]))


# ---------------------------------------------------------------------------
# 3. Plot
# ---------------------------------------------------------------------------

def build_year_topic_counts(
    records: list[dict],
    dominant_topic: np.ndarray,
) -> dict[int, Counter]:
    """For each topic k, return a Counter mapping year -> #papers."""
    counts: dict[int, Counter] = defaultdict(Counter)
    for rec, k in zip(records, dominant_topic):
        if rec["year"] in YEAR_RANGE:
            counts[int(k)][rec["year"]] += 1
    return counts


def plot_figure(counts: dict[int, Counter], output_path: Path) -> None:
    row_pos = {k: i for i, k in enumerate(ROW_ORDER)}
    scale = 13.0  # bubble area per paper

    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=200)

    for k in ROW_ORDER:
        xs, ys, sizes = [], [], []
        for yr in YEAR_RANGE:
            c = counts[k].get(yr, 0)
            if c > 0:
                xs.append(yr)
                ys.append(row_pos[k])
                sizes.append(c * scale)
        ax.scatter(xs, ys, s=sizes, color=TOPIC_COLORS[k], alpha=0.78,
                   edgecolor="white", linewidth=0.8, zorder=3)

    # Axes
    ax.set_yticks(range(len(ROW_ORDER)))
    ax.set_yticklabels([TOPIC_LABELS[k] for k in ROW_ORDER], fontsize=10.5)
    ax.set_ylim(-0.7, len(ROW_ORDER) - 0.3)
    ax.invert_yaxis()
    ax.set_xticks(list(YEAR_RANGE))
    ax.set_xticklabels(list(YEAR_RANGE), fontsize=10)
    ax.set_xlim(min(YEAR_RANGE) - 0.6, max(YEAR_RANGE) + 0.6)
    ax.set_xlabel("Year of publication", fontsize=11.5, labelpad=8)

    ax.set_title(
        "A decade of cheminformatics: topic evolution in the\n"
        "Journal of Cheminformatics, 2015–2025",
        fontsize=14.5, fontweight="bold", pad=16, loc="left",
    )

    # Cosmetics
    for y in range(len(ROW_ORDER)):
        ax.axhline(y, color="#e8e8e8", linewidth=0.8, zorder=0)
    ax.grid(axis="x", color="#f0f0f0", linewidth=0.8, zorder=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(length=0)

    # Size legend
    legend_counts = [5, 20, 50]
    handles = [
        Line2D(
            [0], [0], marker="o", linestyle="None",
            markersize=np.sqrt(c * scale) / np.sqrt(np.pi),
            markerfacecolor="#888", markeredgecolor="white",
            label=f"{c} papers",
        )
        for c in legend_counts
    ]
    ax.legend(
        handles=handles, title="Papers per year",
        loc="lower left", bbox_to_anchor=(1.005, 0.0),
        frameon=False, labelspacing=1.6, handletextpad=1.2,
        borderpad=1.0, fontsize=9.5, title_fontsize=10,
    )
    ax.text(
        1.005, 0.62,
        "Bubble area is\nproportional to the\nnumber of papers\n"
        "assigned to each\ntopic that year\n(NMF topic model).",
        transform=ax.transAxes, fontsize=8.6, color="#555", va="top",
    )

    plt.tight_layout()
    plt.subplots_adjust(right=0.80)
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    # also save a vector copy alongside the raster
    plt.savefig(output_path.with_suffix(".pdf"),
                bbox_inches="tight", facecolor="white")
    print(f"Wrote {output_path} and {output_path.with_suffix('.pdf')}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(nbib_path: Path, output_path: Path) -> None:
    records = parse_nbib(nbib_path)
    print(f"Parsed {len(records)} records with abstracts.")
    print("Year distribution:",
          dict(sorted(Counter(r["year"] for r in records).items())))

    W, H, vocab = fit_topic_model(records)
    print_top_terms(H, vocab)

    dominant_topic = W.argmax(axis=1)
    counts = build_year_topic_counts(records, dominant_topic)

    # Sanity: print the year x topic matrix
    print("\n=== Papers per topic per year ===")
    header = "Topic                                         | " + " ".join(
        f"{y:>4}" for y in YEAR_RANGE)
    print(header)
    for k in ROW_ORDER:
        row = " ".join(f"{counts[k].get(y, 0):>4}" for y in YEAR_RANGE)
        print(f"{TOPIC_LABELS[k][:44]:<45} | {row}")

    plot_figure(counts, output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python figure1_topics.py <pubmed_export.nbib> "
                 "[output.png]")
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("figure1.png")
    main(in_path, out_path)
