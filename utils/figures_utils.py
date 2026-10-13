"""
figures_utils.py — 5 PRISMA figure functions for sota-agent

Extracted from prisma_analysis_report.ipynb Section 8 (cells 23-27).
Each function writes one figure to run_dir and returns the output path.
"""

import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes as _MplAxes
from pathlib import Path
from collections import defaultdict
from typing import cast

DEFAULT_CLUSTER_NAMES = {
    "C1": "ML for Control", "C2": "Robust Protocol", "C3": "Quantum Sensing",
    "C4": "Quantum Opt. Control", "C5": "RL for Quantum", "C6": "Control Landscape",
    "C7": "Noise/Decoherence", "C8": "Physical Platform",
}
DEFAULT_PALETTE = ["#4477AA", "#EE6677", "#228833", "#CCBB44",
                   "#66CCEE", "#AA3377", "#BBBBBB", "#AA4499"]


def plot_cluster_taxonomy(accepted: pd.DataFrame, run_dir: str | Path,
                          cluster_names: dict | None = None, palette: list | None = None) -> Path:
    """
    Fig 1 — Thematic cluster taxonomy tree.
    Saves fig1_taxonomy.svg and fig1_taxonomy.png.
    """
    run_dir = Path(run_dir)
    cluster_names = cluster_names or DEFAULT_CLUSTER_NAMES
    palette = palette or DEFAULT_PALETTE
    counts = accepted["cluster"].value_counts().sort_index()
    clusters = sorted(counts.index.tolist())

    fig, ax = plt.subplots(figsize=(14, 8))
    ax = cast(_MplAxes, ax)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    ax.text(1.2, 5, "ML for\nQuantum\nControl", ha="center", va="center",
            fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#1a1a2e",
                      edgecolor="#4477AA", linewidth=2), color="white")

    ys = np.linspace(0.8, 9.2, len(clusters))
    for i, (cl, y) in enumerate(zip(clusters, ys)):
        n = counts.get(cl, 0)
        name = cluster_names.get(cl, cl)
        color = palette[i % len(palette)]
        ax.plot([1.7, 3.2], [5, y], color="#aaaaaa", linewidth=1.2, zorder=0)
        ax.text(4.5, y, f"{cl}: {name}\n(n={n})", ha="center", va="center",
                fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.35", facecolor=color, edgecolor="none", alpha=0.85),
                color="white" if i not in [3, 6] else "#111111")

    n_total = len(accepted)
    ax.set_title(f"Thematic Cluster Taxonomy\n(n={n_total})",
                 fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    out_svg = run_dir / "fig1_taxonomy.svg"
    out_png = run_dir / "fig1_taxonomy.png"
    plt.savefig(out_svg, format="svg", bbox_inches="tight")
    plt.savefig(out_png, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    print(f"fig1_taxonomy saved → {out_svg}")
    return out_png


def plot_publication_timeline(accepted: pd.DataFrame, run_dir: str | Path,
                               cluster_names: dict | None = None, palette: list | None = None) -> Path:
    """Fig 2 — Stacked bar publication timeline by cluster. Saves fig2_timeline.png."""
    run_dir = Path(run_dir)
    cluster_names = cluster_names or DEFAULT_CLUSTER_NAMES
    palette = palette or DEFAULT_PALETTE

    acc = accepted.copy()
    acc["year"] = pd.to_numeric(acc["year"], errors="coerce")
    acc = acc.dropna(subset=["year"])
    acc["year"] = acc["year"].astype(int)
    clusters = sorted(acc["cluster"].unique())
    years = list(range(int(acc["year"].min()), int(acc["year"].max()) + 1))

    pivot = acc.groupby(["year", "cluster"]).size().unstack(fill_value=0)
    pivot = pivot.reindex(years, fill_value=0)
    for c in clusters:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[clusters]

    fig, ax = plt.subplots(figsize=(13, 6))
    ax = cast(_MplAxes, ax)
    bottom = np.zeros(len(years))
    for i, cl in enumerate(clusters):
        vals = pivot[cl].values
        ax.bar(years, vals, bottom=bottom, color=palette[i % len(palette)],
               label=f"{cl} {cluster_names.get(cl, '')}", alpha=0.9, edgecolor="white", linewidth=0.4)
        bottom += vals

    ax.set_xlabel("Year", fontsize=11); ax.set_ylabel("Papers accepted", fontsize=11)
    ax.set_title(f"Publication Timeline by Cluster (n={len(accepted)})", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, ncol=2, framealpha=0.85)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45, ha="right", fontsize=9)
    ax.grid(axis="y", alpha=0.3); ax.set_axisbelow(True)
    plt.tight_layout()
    out = run_dir / "fig2_timeline.png"
    plt.savefig(out, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"fig2_timeline saved → {out}")
    return out


def plot_platform_heatmap(accepted: pd.DataFrame, run_dir: str | Path,
                          cluster_names: dict | None = None) -> Path:
    """Fig 3 — Platform × cluster coverage heatmap. Saves fig3_platform_heatmap.png."""
    run_dir = Path(run_dir)
    cluster_names = cluster_names or DEFAULT_CLUSTER_NAMES

    PLATFORMS = {
        "superconducting": r"superconducting|transmon|qubit|josephson|microwave",
        "trapped ion": r"trapped.?ion|ion.?trap|calcium.?ion|ytterbium",
        "photonic": r"photon|optical|beam.?splitter|interferometer|waveguide",
        "neutral atoms": r"neutral.?atom|rydberg|cold.?atom|bose.?einstein",
        "NV center": r"nv.?cent|nitrogen.?vacanc|diamond",
        "NMR/spin": r"\bnmr\b|nuclear.?spin|magnetic.?resonance",
        "simulation only": r"simul|hamiltonian|model|synthetic",
    }

    def detect_platform(abstract):
        if not isinstance(abstract, str):
            return "simulation only"
        text = abstract.lower()
        for plat, pattern in PLATFORMS.items():
            if re.search(pattern, text):
                return plat
        return "simulation only"

    acc = accepted.copy()
    acc["platform"] = acc["abstract"].apply(detect_platform)
    clusters = sorted(acc["cluster"].unique())

    heat = pd.crosstab(acc["platform"], acc["cluster"])
    for c in clusters:
        if c not in heat.columns:
            heat[c] = 0
    heat = heat[clusters]
    heat.index = [p.title() for p in heat.index]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax = cast(_MplAxes, ax)
    im = ax.imshow(heat.values, cmap=plt.cm.YlOrRd, aspect="auto")
    plt.colorbar(im, ax=ax, label="Paper count")
    ax.set_xticks(range(len(clusters)))
    ax.set_xticklabels([f"{c}\n{cluster_names.get(c,'')[:12]}" for c in clusters], fontsize=8)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=9)

    for i in range(len(heat.index)):
        for j in range(len(clusters)):
            val = heat.values[i, j]
            if val > 0:
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=8, color="black" if val < heat.values.max() * 0.6 else "white")

    ax.set_title("Platform Coverage Heatmap by Cluster", fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = run_dir / "fig3_platform_heatmap.png"
    plt.savefig(out, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"fig3_platform_heatmap saved → {out}")
    return out


def plot_concept_network(accepted: pd.DataFrame, run_dir: str | Path,
                         keywords: list | None = None) -> Path:
    """Fig 4 — Keyword co-occurrence network. Saves fig4_concept_network.png."""
    import networkx as nx
    run_dir = Path(run_dir)

    if keywords is None:
        keywords = [
            "reinforcement learning", "optimal control", "neural network", "quantum gate",
            "robust control", "noise", "decoherence", "fidelity", "GRAPE", "DRAG",
            "deep learning", "quantum sensing", "Fisher information", "metrology",
            "superconducting", "trapped ion", "qubit", "Hamiltonian", "pulse",
            "policy gradient", "Q-learning", "actor-critic", "Bayesian", "Gaussian process",
            "control landscape", "trap-free", "CRAB", "Krotov", "variational", "transfer learning",
        ]

    palette = DEFAULT_PALETTE
    abstracts = accepted["abstract"].fillna("").str.lower().tolist()

    freq = {kw: sum(1 for a in abstracts if re.search(re.escape(kw.lower()), a))
            for kw in keywords}
    cooccur: dict = defaultdict(int)
    for abstract in abstracts:
        present = [kw for kw in keywords if re.search(re.escape(kw.lower()), abstract)]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                cooccur[tuple(sorted([present[i], present[j]]))] += 1

    top_kws = [k for k, v in sorted(freq.items(), key=lambda x: -x[1])[:30] if v > 0]
    G = nx.Graph()
    for kw in top_kws:
        G.add_node(kw, weight=freq[kw])
    for (a, b), w in cooccur.items():
        if a in top_kws and b in top_kws and w >= 3:
            G.add_edge(a, b, weight=w)

    node_sizes = [max(100, G.nodes[n]["weight"] * 25) for n in G.nodes()]
    degrees = dict(G.degree())
    node_colors = [palette[min(int(degrees[n] / 5), len(palette) - 1)] for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(14, 10))
    ax = cast(_MplAxes, ax)
    pos = nx.spring_layout(G, k=2.5, seed=42)
    edge_weights = [G[u][v]["weight"] * 0.3 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.4, edge_color="#999999", ax=ax)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.85, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=7.5, font_weight="bold", ax=ax)
    ax.set_title("Concept Co-occurrence Network (top 30 keywords, edge ≥ 3 co-occurrences)",
                 fontsize=12, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    out = run_dir / "fig4_concept_network.png"
    plt.savefig(out, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"fig4_concept_network saved → {out}")
    return out


def plot_gap_radar(accepted: pd.DataFrame, run_dir: str | Path,
                  cluster_names: dict = None) -> Path:
    """Fig 5 — Cluster coverage radar chart. Saves fig5_gap_radar.png."""
    run_dir = Path(run_dir)
    cluster_names = cluster_names or DEFAULT_CLUSTER_NAMES
    clusters = sorted(accepted["cluster"].unique())

    def cluster_coverage(df, cl):
        sub = df[df["cluster"] == cl]
        n = len(sub)
        if n == 0:
            return 0.0, 0.0, 0.0
        size_score = min(np.log1p(n) / np.log1p(140), 1.0)
        years_present = sub["year"].dropna().nunique()
        temporal_score = min(years_present / 11, 1.0)
        cit = sub["citation_count"].fillna(0)
        citation_score = float((cit > 0).mean())
        return size_score, temporal_score, citation_score

    labels, values = [], []
    for cl in clusters:
        s, t, cit = cluster_coverage(accepted, cl)
        score = np.mean([s, t, cit])
        labels.append(f"{cl}\n{cluster_names.get(cl,'')[:14]}")
        values.append(score)

    N_c = len(clusters)
    angles = np.linspace(0, 2 * np.pi, N_c, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    ax.plot(angles_plot, values_plot, "o-", color="#4477AA", linewidth=2)
    ax.fill(angles_plot, values_plot, alpha=0.2, color="#4477AA")
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], size=7)
    ax.grid(True, alpha=0.4)
    ax.set_title("Coverage Score per Cluster\n(size × temporal × citation health)",
                 size=13, fontweight="bold", y=1.08)
    plt.tight_layout()
    out = run_dir / "fig5_gap_radar.png"
    plt.savefig(out, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"fig5_gap_radar saved → {out}")
    return out
