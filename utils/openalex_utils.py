"""
openalex_utils.py — OpenAlex API helpers for sota-agent

Extracted from prisma_analysis_report.ipynb Sections 6 and 7A.
"""

import json
import time
import requests
import networkx as nx
from pathlib import Path

DEFAULT_MAILTO = "ccruz.le2i@gmail.com"


def fetch_openalex(doi_or_id: str, cache: dict, cache_path: Path,
                   mailto: str = DEFAULT_MAILTO) -> dict | None:
    """Fetch a single paper from OpenAlex by DOI or arXiv ID. Uses and updates cache."""
    key = doi_or_id.strip()
    if key in cache:
        return cache[key]
    try:
        if key.startswith("10."):
            url = (f"https://api.openalex.org/works/doi:{key}"
                   f"?mailto={mailto}&select=id,title,referenced_works,cited_by_count")
        elif key.startswith("arxiv:") or "/" in key:
            arxiv_id = key.replace("arxiv:", "")
            url = (f"https://api.openalex.org/works/arxiv:{arxiv_id}"
                   f"?mailto={mailto}&select=id,title,referenced_works,cited_by_count")
        else:
            return None
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            cache[key] = data
            if cache_path:
                cache_path.write_text(json.dumps(cache, indent=2))
            return data
    except Exception:
        pass
    return None


def fetch_corpus_metadata(df_acc, cache_path: Path, mailto: str = DEFAULT_MAILTO,
                          max_papers: int = 400) -> tuple[dict, dict]:
    """
    Fetch OpenAlex metadata for all accepted papers with a DOI.
    Returns paper_refs: {paper_id → list of referenced OpenAlex work IDs}.
    Extends existing cache (never overwrites).
    """
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    paper_refs = {}

    sample = df_acc[df_acc["doi"].notna() & (df_acc["doi"].astype(str).str.strip() != "")]
    sample = sample.head(max_papers)
    print(f"Fetching OpenAlex metadata for {len(sample)} papers...")

    for idx, (_, row) in enumerate(sample.iterrows()):
        doi = str(row["doi"]).strip()
        if not doi or doi == "nan":
            continue
        data = fetch_openalex(doi, cache, cache_path, mailto)
        if data:
            paper_refs[str(row["id"])] = data.get("referenced_works", [])
        time.sleep(0.1)
        if (idx + 1) % 50 == 0:
            print(f"  {idx + 1}/{len(sample)} done")

    print(f"Fetched references for {len(paper_refs)}/{len(sample)} papers. Cache: {len(cache)} entries.")
    return paper_refs, cache


def build_bibliographic_coupling_graph(paper_refs: dict, min_shared: int = 2) -> nx.Graph:
    """
    Build a bibliographic coupling graph.
    Two papers share an edge if they reference ≥ min_shared common works.
    """
    G = nx.Graph()
    pids = list(paper_refs.keys())
    ref_sets = {pid: set(paper_refs[pid]) for pid in pids}
    for i in range(len(pids)):
        for j in range(i + 1, len(pids)):
            shared = len(ref_sets[pids[i]] & ref_sets[pids[j]])
            if shared >= min_shared:
                G.add_edge(pids[i], pids[j], weight=shared)
    print(f"Bib coupling graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_betweenness_bridge_papers(G_bib: nx.Graph, accepted_df, top_n: int = 5) -> list:
    """
    Compute betweenness centrality on the LCC of G_bib.
    Returns list of dicts: {id, cluster, bc_score, title}.
    """
    if G_bib.number_of_edges() == 0:
        return []
    comps = list(nx.connected_components(G_bib))
    lcc = max(comps, key=len)
    G_lcc = G_bib.subgraph(lcc)
    bc = nx.betweenness_centrality(G_lcc, normalized=True)
    top = sorted(bc.items(), key=lambda x: x[1], reverse=True)[:top_n]
    result = []
    for pid, score in top:
        row = accepted_df[accepted_df["id"].astype(str) == str(pid)]
        title = row.iloc[0]["title"][:70] if not row.empty else "?"
        cluster = row.iloc[0]["cluster"] if not row.empty else "?"
        result.append({"id": pid, "cluster": cluster, "bc_score": score, "title": title})
        print(f"  {pid} ({cluster}) BC={score:.4f}: {title}")
    return result
