# PARIS utility modules
# api_clients     : PDF retrieval via OA APIs
# pdf_utils       : full-text extraction with pymupdf
# csv_utils       : master_research_data.csv read/update helpers
# openalex_utils  : OpenAlex API fetch, bibliographic coupling, bridge papers
# quality_utils   : QualityScore v0.5 sub-score functions (S_network, S_bib, S_semantic, S_process)
# figures_utils   : 5 PRISMA figure generators (taxonomy, timeline, heatmap, network, radar)

from .openalex_utils import (
    fetch_openalex,
    fetch_corpus_metadata,
    build_bibliographic_coupling_graph,
    compute_betweenness_bridge_papers,
)
from .quality_utils import (
    compute_s_network,
    compute_s_bibliometric,
    compute_s_semantic,
    compute_s_process,
    compute_quality_score,
)
from .figures_utils import (
    plot_cluster_taxonomy,
    plot_publication_timeline,
    plot_platform_heatmap,
    plot_concept_network,
    plot_gap_radar,
)
