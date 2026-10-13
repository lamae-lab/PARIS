"""
quality_utils.py — QualityScore v0.5 sub-score functions for sota-agent

Extracted from prisma_analysis_report.ipynb Section 7 (cells 16-21).
Formula: QS = 100 × (0.30×S_network + 0.25×S_bib + 0.20×S_semantic + 0.25×S_process)
"""

import math
import re
import numpy as np
from collections import Counter
from typing import Any

TfidfVectorizer: Any = None
cosine_similarity: Any = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

import networkx as nx


def compute_s_network(G_bib: nx.Graph, G_ca: nx.Graph | None = None) -> float:
    """
    Network science sub-score (weight 30%).
    Based on Louvain modularity of the bibliographic coupling graph, capped at 0.7.
    G_ca is unused (kept for API compatibility — co-authorship LCC fraction is minor signal).
    """
    if G_bib.number_of_edges() == 0:
        return 0.0
    try:
        import community as community_louvain  # type: ignore[import]
        partition = community_louvain.best_partition(G_bib)
        modularity = community_louvain.modularity(partition, G_bib)
    except ImportError:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = list(greedy_modularity_communities(G_bib))
        modularity = nx.algorithms.community.modularity(G_bib, comms)
    s = min(modularity / 0.7, 1.0)
    print(f"S_network = min({modularity:.3f}/0.7, 1.0) = {s:.3f}")
    return float(s)


def compute_s_bibliometric(accepted, N: int) -> float:
    """
    Bibliometric sub-score (weight 25%).
    Components: h-index, temporal entropy, venue Gini (inverted), foundational rate.
    """
    citations = sorted(accepted["cit_enriched"].fillna(0).tolist(), reverse=True)
    h = sum(1 for i, c in enumerate(citations) if c >= i + 1)

    years = accepted["year"].dropna().astype(int).tolist()
    yr_counts = Counter(years)
    yr_probs = [v / len(years) for v in yr_counts.values()]
    t_ent = -sum(p * math.log(p) for p in yr_probs if p > 0)
    max_ent = math.log(len(yr_counts)) if len(yr_counts) > 1 else 1
    t_ent_norm = t_ent / max_ent

    venue_counts = Counter(accepted["venue"].fillna("Unknown").str[:50].tolist())
    vv = sorted(venue_counts.values(), reverse=True)
    n_v = len(vv)
    mean_v = float(np.mean(vv))
    if n_v > 1 and mean_v > 0:
        venue_gini = sum(abs(vv[i] - vv[j]) for i in range(n_v) for j in range(i + 1, n_v))
        venue_gini /= n_v ** 2 * mean_v
    else:
        venue_gini = 0

    foundational = sum(1 for c in citations if c > 50)
    found_rate = foundational / N if N > 0 else 0

    s = float(np.mean([min(h / 30, 1), t_ent_norm, 1 - venue_gini, min(found_rate / 0.15, 1)]))
    print(f"S_bibliometric = mean([{min(h/30,1):.3f}, {t_ent_norm:.3f}, {1-venue_gini:.3f}, "
          f"{min(found_rate/0.15,1):.3f}]) = {s:.3f}")
    return s


def compute_s_semantic(accepted, scoper_text: str) -> float:
    """
    Semantic diversity sub-score (weight 20%).
    Components: 1 - inter-cluster cosine similarity, scoper keyword coverage, 1 - redundancy.
    """
    if not HAS_SKLEARN:
        print("WARNING: scikit-learn not available — S_semantic defaulting to 0.5")
        return 0.5

    abstracts = accepted["abstract"].fillna("").tolist()
    clusters = accepted["cluster"].fillna("Unknown").tolist()
    N = len(abstracts)

    tfidf = TfidfVectorizer(max_features=1000, min_df=2, stop_words="english")
    X = tfidf.fit_transform(abstracts)

    cluster_ids = sorted(set(clusters))
    cvecs = []
    for cid in cluster_ids:
        mask = [i for i, c in enumerate(clusters) if c == cid]
        if mask:
            cvecs.append(np.asarray(X[np.array(mask)].mean(axis=0)).flatten())

    if len(cvecs) >= 2:
        sim_mat = cosine_similarity(np.vstack(cvecs))
        nc = len(cvecs)
        off_d = [sim_mat[i, j] for i in range(nc) for j in range(i + 1, nc)]
        inter_sim = float(np.mean(off_d))
    else:
        inter_sim = 0.0

    np.random.seed(42)
    sidx = np.random.choice(N, min(200, N), replace=False)
    pw = cosine_similarity(X[sidx])
    np.fill_diagonal(pw, 0)
    redundancy = float(pw.sum() / (len(sidx) * (len(sidx) - 1))) if len(sidx) > 1 else 0

    rows_kw = re.findall(r"\| C\d+ —[^|]+\|([^|]+)\|([^|]+)\|", scoper_text)
    kw_set = set()
    for primary, synonyms in rows_kw:
        for term in re.split(r"[,;]", primary + "," + synonyms):
            t = term.strip().lower()
            if len(t) > 3 and not t.startswith("[") and ":" not in t:
                kw_set.add(t)

    all_abs = " ".join(accepted["abstract"].fillna("").str.lower().tolist())
    found_kw = [k for k in kw_set if all_abs.count(k) >= 2]
    scoper_cov = len(found_kw) / len(kw_set) if kw_set else 0.5

    s = float(np.mean([1 - inter_sim, scoper_cov, 1 - redundancy]))
    print(f"S_semantic = mean([{1-inter_sim:.3f}, {scoper_cov:.3f}, {1-redundancy:.3f}]) = {s:.3f}")
    return s


def compute_s_process(accepted, n_raw: int) -> float:
    """
    Process quality sub-score (weight 25%).
    Components: inclusion rate (sweet spot 30-60%), source Gini (inverted), mean relevance score health.
    """
    N = len(accepted)
    inclusion_rate = N / n_raw if n_raw > 0 else 0

    if 0.30 <= inclusion_rate <= 0.60:
        i_score = 1.0
    elif inclusion_rate < 0.30:
        i_score = inclusion_rate / 0.30
    else:
        i_score = max(0, 1.0 - (inclusion_rate - 0.60) / 0.40)

    single_mask = ~accepted["source"].astype(str).str.contains(r"\+", na=False)
    src_counts = Counter(accepted[single_mask]["source"].fillna("unknown").tolist())
    sv = sorted(src_counts.values(), reverse=True)
    n_sv = sum(sv)
    if len(sv) > 1 and n_sv > 0:
        src_gini = sum(abs(sv[i] - sv[j]) for i in range(len(sv)) for j in range(i + 1, len(sv)))
        src_gini /= len(sv) ** 2 * float(np.mean(sv))
    else:
        src_gini = 0

    mean_score = float(accepted["relevance_score"].fillna(0).mean())
    score_health = min(mean_score / 8.0, 1.0)

    s = float(np.mean([i_score, 1 - src_gini, score_health]))
    print(f"S_process = mean([{i_score:.3f}, {1-src_gini:.3f}, {score_health:.3f}]) = {s:.3f}")
    return s


def compute_quality_score(s_network: float, s_bib: float,
                          s_semantic: float, s_process: float) -> tuple[float, str, str]:
    """
    Composite QualityScore v0.5.
    Returns (score_0_100, grade_letter, grade_label).
    """
    qs = 100 * (0.30 * s_network + 0.25 * s_bib + 0.20 * s_semantic + 0.25 * s_process)
    grade = "A" if qs >= 80 else ("B" if qs >= 65 else ("C" if qs >= 50 else "D"))
    labels = {"A": "Very Good", "B": "Good", "C": "Acceptable", "D": "Poor"}
    print(f"\nQualityScore v0.5: {qs:.1f}/100 — Grade {grade} ({labels[grade]})")
    print(f"  Network:      {s_network:.3f} → {0.30*s_network*100:.1f} pts")
    print(f"  Bibliometric: {s_bib:.3f} → {0.25*s_bib*100:.1f} pts")
    print(f"  Semantic:     {s_semantic:.3f} → {0.20*s_semantic*100:.1f} pts")
    print(f"  Process:      {s_process:.3f} → {0.25*s_process*100:.1f} pts")
    return qs, grade, labels[grade]
