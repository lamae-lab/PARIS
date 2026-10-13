# utils/ — Reusable Python Modules for sota-agent-0.4

Extracted from `prisma_analysis_report.ipynb` (ML for Quantum Control run, 2026-10-11).
Agents import from here instead of re-generating notebook code each run.

## Modules

### `openalex_utils.py`
OpenAlex REST API helpers used by `agent_analyst` (Section 6) and `quality_agent` (Section 7A).

| Function | Description |
|----------|-------------|
| `fetch_openalex(doi_or_id, cache, cache_path, mailto)` | Single-paper fetch with local JSON cache |
| `fetch_corpus_metadata(df_acc, cache_path, mailto, max_papers)` | Bulk fetch for accepted corpus; returns `(paper_refs, cache)` |
| `build_bibliographic_coupling_graph(paper_refs, min_shared=2)` | Returns `nx.Graph` (bib coupling) |
| `compute_betweenness_bridge_papers(G_bib, accepted_df, top_n=5)` | BC on LCC; returns list of `{id, cluster, bc_score, title}` |

### `quality_utils.py`
QualityScore v0.5 formula — used by `quality_agent` Section 7.

| Function | Weight | Description |
|----------|--------|-------------|
| `compute_s_network(G_bib, G_ca)` | 30% | Louvain modularity / 0.7 |
| `compute_s_bibliometric(accepted, N)` | 25% | H-index, temporal entropy, venue Gini, foundational rate |
| `compute_s_semantic(accepted, scoper_text)` | 20% | Inter-cluster cosine sim, scoper coverage, redundancy |
| `compute_s_process(accepted, n_raw)` | 25% | Inclusion rate, source Gini, mean relevance score |
| `compute_quality_score(s_net, s_bib, s_sem, s_proc)` | — | Returns `(score_0_100, grade_letter, grade_label)` |

**Formula:** `QS = 100 × (0.30×S_network + 0.25×S_bib + 0.20×S_semantic + 0.25×S_process)`  
**Grades:** A ≥ 80, B ≥ 65, C ≥ 50, D < 50

### `figures_utils.py`
5 standard PRISMA figures — used by `figure_agent` Section 8.

| Function | Output file | Description |
|----------|-------------|-------------|
| `plot_cluster_taxonomy(accepted, run_dir, ...)` | `fig1_taxonomy.svg/.png` | Radial tree of 8 clusters |
| `plot_publication_timeline(accepted, run_dir, ...)` | `fig2_timeline.png` | Stacked bar by cluster × year |
| `plot_platform_heatmap(accepted, run_dir, ...)` | `fig3_platform_heatmap.png` | Platform × cluster count heatmap |
| `plot_concept_network(accepted, run_dir, ...)` | `fig4_concept_network.png` | PICO keyword co-occurrence network |
| `plot_gap_radar(accepted, run_dir, ...)` | `fig5_gap_radar.png` | Cluster coverage radar chart |

## Usage example (in a notebook or agent script)

```python
import sys; sys.path.insert(0, '/mnt/e/lamae-sota-tool/sota-agent-0.4')
from utils import (
    fetch_corpus_metadata, build_bibliographic_coupling_graph,
    compute_betweenness_bridge_papers,
    compute_s_network, compute_s_bibliometric, compute_s_semantic,
    compute_s_process, compute_quality_score,
    plot_cluster_taxonomy, plot_publication_timeline,
    plot_platform_heatmap, plot_concept_network, plot_gap_radar,
)

# Quality score
paper_refs, cache = fetch_corpus_metadata(df_acc, cache_path, mailto='you@example.com')
G_bib = build_bibliographic_coupling_graph(paper_refs)
bridges = compute_betweenness_bridge_papers(G_bib, df_acc)

s_net = compute_s_network(G_bib)
s_bib = compute_s_bibliometric(df_acc, N=len(df_acc))
s_sem = compute_s_semantic(df_acc, scoper_text)
s_proc = compute_s_process(df_acc, n_raw=959)
qs, grade, label = compute_quality_score(s_net, s_bib, s_sem, s_proc)

# Figures
plot_cluster_taxonomy(df_acc, run_dir)
plot_publication_timeline(df_acc, run_dir)
```
