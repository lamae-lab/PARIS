# PARIS — PRISMA Agentic Research Intelligence System

```
██████╗  █████╗ ██████╗ ██╗███████╗
██╔══██╗██╔══██╗██╔══██╗██║██╔════╝
██████╔╝███████║██████╔╝██║███████╗
██╔═══╝ ██╔══██║██╔══██╗██║╚════██║
██║     ██║  ██║██║  ██║██║███████║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
  PRISMA Agentic Research Intelligence System
```

![PRISMA 2020](https://img.shields.io/badge/PRISMA-2020%20Compliant-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skills%20v0.5-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Agents](https://img.shields.io/badge/Agents-15-purple)
![website]([https://img.shields.io/badge/website](https://lamae-lab.github.io/PARIS-site/))

> **From research question to journal-ready manuscript in one pipeline.**  
> PARIS is a multi-agent systematic literature review system built for [Claude Code](https://claude.ai/code). It automates every PRISMA 2020 stage — from database retrieval to Elsevier-formatted export — while keeping humans in the loop at critical decision points.

---

## What is PARIS?

PARIS automates the full lifecycle of a **PRISMA 2020 systematic literature review**:

1. **Retrieval** across six academic databases (OpenAlex, Semantic Scholar, arXiv, CrossRef, IEEE Xplore, ScienceDirect/Elsevier)
2. **Screening** with relevance scoring, cluster-balanced curation, and 3-level deduplication (arXiv ID → DOI → title)
3. **Full-text analysis** of open-access PDFs via OA APIs
4. **Quality assessment** with a normalized 4-dimension score (0–100, Grade A–D)
5. **Gap and limitations analysis** including TRL matrix and reproducibility map
6. **Manuscript synthesis** with a PRISMA-compliant structure, figures, and BibTeX bibliography
7. **Journal-ready export**: DOCX (Elsevier CSL), LaTeX (elsarticle), and 11-slide PPTX

### How PARIS differs from other tools

| Tool | Screening | Synthesis | Draft | Journal-ready |
|------|-----------|-----------|-------|---------------|
| **Rayyan** | ✅ AI-assisted | ❌ | ❌ | ❌ |
| **Covidence** | ✅ Manual | ❌ | ❌ | ❌ |
| **ASReview** | ✅ Active learning | ❌ | ❌ | ❌ |
| **Elicit** | ✅ LLM extraction | ⚠️ Tables only | ❌ | ❌ |
| **Research Rabbit** | ❌ Discovery only | ❌ | ❌ | ❌ |
| **PARIS** | ✅ LLM scoring + dedup | ✅ Full thematic | ✅ ~8,000 words | ✅ DOCX + TEX + PPTX |

PARIS is the only open-source tool that produces a complete, peer-review-ready manuscript from a research question. It is built entirely on Claude Code skills and Python utilities — no cloud subscription, no vendor lock-in.

---

## Architecture

### 15-Agent Pipeline

| Step | Agent | Role | Outputs |
|------|-------|------|---------|
| 1 | **scoper_agent** | Concept extraction, keyword mapping, 8-cluster taxonomy | `scoper_output.md` |
| 2 | **strategist_agent** | API retrieval (6 DBs), rate-limiting, deduplication | `raw_extraction_list.md` |
| 2.5 | **pdf_retriever_agent** | Full-text PDF download (OA sources) | `pdf_retrieval_report.md`, `pdfs/` |
| 3 | **translator_agent** | Non-English abstract detection and translation | `translation_report.md` |
| 4 | **curator_agent** | Relevance scoring, cluster balancing, 3-level dedup, borderline review | `curation_report.md` |
| 5 | **agent_analyst** | CSV consolidation, PRISMA Jupyter notebook (Sections 1–5) | `master_research_data.csv`, `.ipynb` |
| 5b | **bibtex_agent** | CrossRef BibTeX export + arXiv fallback | `references.bib` |
| 5.5 | **pdf_analyzer_agent** | Full-text extraction: methods, limitations, reproducibility | `pdf_analysis_report.md` |
| 6 | **quality_agent** | QualityScore 0–100, Grade A–D, OA coverage enrichment | `quality_report.md` |
| 7 | **gap_finder_agent** | Cross-cluster gaps, temporal, platform, methodological | `gap_analysis.md` |
| 7.5 | **limits_agent** | TRL matrix, Top 5 improvement paths, reproducibility map | `limits_report.md` |
| 8 | **figure_agent** | 5 figures: taxonomy, timeline, heatmap, concept network, radar | `fig1–5.{svg,png}` |
| 9 | **synthesizer_agent** | Outline checkpoint + full manuscript draft | `paper_draft.md` |
| 10 | **reviewer_agent** | Adversarial peer review, citation integrity, verdict 0–10 | `review_report.md` |
| 11 | **export_agent** | DOCX (pandoc + Elsevier CSL), LaTeX (elsarticle), PPTX (11 slides) | `paper_draft.{docx,tex}`, `slides.pptx` |

### Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  RESEARCH QUESTION                                                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
         ┌─────────────────────▼──────────────────────┐
         │  (1) SCOPE  →  (2) STRATEGY               │
         │      ↓               ↓                      │
         │  scoper         strategist                  │
         │  8 concepts     6 databases                 │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (2.5) PDF RETRIEVE  →  (3) TRANSLATE       │
         │  OA APIs: OpenAlex, arXiv, Elsevier         │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (4) CURATE  ← ⚠️ HUMAN CHECKPOINT A       │
         │  Score + dedup + cluster balance            │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (5) ANALYZE  →  (5b) BIBTEX  →  (5.5) PDF │
         │  CSV + Notebook                             │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (6) QUALITY  →  (7) GAPS  →  (7.5) LIMITS │
         │  QS 0–100 Grade A–D │ TRL matrix            │
         │  ⚠️ CHECKPOINT B: QS < 65 → IMPROVE?        │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (8) FIGURES  →  (9) SYNTHESIZE             │
         │  5 figures     ⚠️ CHECKPOINT C: outline     │
         └────────────────────┬───────────────────────┘
                              │
         ┌────────────────────▼───────────────────────┐
         │  (10) REVIEW  →  (11) EXPORT               │
         │  Peer review     DOCX + TEX + PPTX          │
         └────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
pip install -r requirements_v03.txt

# Node.js 18+ (for PPTX generation)
npm install -g pptxgenjs

# pandoc (for DOCX export)
# Ubuntu/Debian:
sudo apt-get install pandoc
# macOS:
brew install pandoc

# Claude Code CLI
npm install -g @anthropic-ai/claude-code
```

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/PARIS.git
cd PARIS
pip install -r requirements_v03.txt
```

### First Run (3 commands)

```bash
# 1. Open Claude Code in the PARIS directory
claude

# 2. Start a new systematic review
/sota-new "Your research topic here"

# 3. Follow the prompts — the pipeline runs autonomously
# Human checkpoints appear at A (borderline papers) and C (synthesis outline)
```

---

## Skills Reference

PARIS provides 6 Claude Code slash commands. Each skill delegates work to the 15-agent pipeline.

| Skill | Command | Entry point | Output |
|-------|---------|-------------|--------|
| **New run** | `/sota-new "<topic>"` | scoper → curator phase 1 | `borderline_review.md` |
| **Curate** | `/sota-curate` | curator phase 2 → analyst | `curation_report.md`, `.ipynb` |
| **Quality** | `/sota-quality` | quality → gaps → limits → figures | `quality_report.md`, 5 figures |
| **Write** | `/sota-write` | synthesizer outline → draft | `paper_draft.md` |
| **Review** | `/sota-review` | reviewer → export | `review_report.md`, `.docx`, `.pptx` |
| **Export** | `/sota-export` | export only | `paper_draft.docx`, `.tex`, `slides.pptx` |

### Skill details

#### `/sota-new "<topic>"`

Launches the first 4 pipeline steps (scoper, strategist, pdf_retriever, translator, curator phase 1). Stops at **Human Checkpoint A** with the borderline papers table.

```
Prerequisites: none
Outputs: scoper_output.md, raw_extraction_list.md, borderline_review.md
Next: review borderline papers, then /sota-curate
```

#### `/sota-curate`

Finalises curation with your borderline decisions, runs agent_analyst, bibtex_agent, and pdf_analyzer (if PDFs available).

```
Prerequisites: borderline_review.md with your decisions filled in
Outputs: curation_report.md, master_research_data.csv, prisma_analysis_report.ipynb, references.bib
Next: /sota-quality
```

#### `/sota-quality`

Runs quality assessment (with OpenAlex citation enrichment), gap finder, limits agent, and figure generation. Presents **Checkpoint B**: if QualityScore < 65, recommends a delta run to improve the corpus.

```
Prerequisites: master_research_data.csv, prisma_analysis_report.ipynb
Outputs: quality_report.md, gap_analysis.md, limits_report.md, fig1–5
Next: /sota-write (or improve corpus if Grade D)
```

#### `/sota-write`

Runs synthesizer in two phases: outline (Checkpoint C, awaits approval) then full draft.

```
Prerequisites: quality_report.md, gap_analysis.md, figures_manifest.md
Outputs: synthesis_outline.md, paper_draft.md (~7,000–9,000 words)
Next: /sota-review
```

#### `/sota-review`

Runs adversarial peer review, applies fixes for critical issues (up to 3 iterations), then auto-exports on verdict ACCEPT/MINOR.

```
Prerequisites: paper_draft.md
Outputs: review_report.md, paper_draft.docx (Elsevier CSL), paper_draft.tex (elsarticle), slides_presentation.pptx
```

#### `/sota-export`

Export only, for an existing `paper_draft.md`.

```
Prerequisites: paper_draft.md, references.bib
Outputs: paper_draft.docx, paper_draft.tex, slides_presentation.pptx
```

---

## Configuration

Set these environment variables before running. Export them in your shell profile or in a `.env` file.

| Variable | Required | Description | Where to obtain |
|----------|----------|-------------|-----------------|
| `ELSEVIER_API_KEY` | Optional | ScienceDirect full-text access | [dev.elsevier.com](https://dev.elsevier.com) |
| `ELSEVIER_INST_TOKEN` | Optional | Institutional token (required with API key) | Your library IT |
| `IEEE_API_KEY` | Optional | IEEE Xplore API key | [developer.ieee.org](https://developer.ieee.org) |
| `S2_API_KEY` | Optional | Semantic Scholar API key (10M req/day vs ~10 without) | [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api) |
| `UNPAYWALL_EMAIL` | Optional | Unpaywall polite pool | [unpaywall.org/products/api](https://unpaywall.org/products/api) |
| `OPENALEX_EMAIL` | Recommended | OpenAlex polite pool (10 req/s vs ~1) | Any valid email |

```bash
export ELSEVIER_API_KEY="your_key_here"
export ELSEVIER_INST_TOKEN="your_token_here"
export IEEE_API_KEY="your_key_here"
export S2_API_KEY="your_key_here"
export UNPAYWALL_EMAIL="you@institution.edu"
export OPENALEX_EMAIL="you@institution.edu"
```

> **Note:** Elsevier requires both the API key AND the institutional token to access full-text PDFs. The key alone gives metadata only.

---

## QualityScore v0.5

PARIS computes a normalized quality score for every corpus using 4 independent dimensions.

### Formula

```
QS = 100 × [0.30 × S_network + 0.25 × S_bibliometric + 0.20 × S_semantic + 0.25 × S_process]
```

### Dimensions

| Dimension | Weight | What it measures | Key metrics |
|-----------|--------|-----------------|-------------|
| **S_network** | 30% | Bibliographic coupling quality | Louvain modularity (bib coupling graph), betweenness centrality of bridge papers |
| **S_bibliometric** | 25% | Citation health and Gini balance | Mean citation count, H-index distribution, Gini coefficient ≤ 0.7 |
| **S_semantic** | 20% | Field specialization and diversity | Inter-cluster cosine similarity, scoper keyword coverage, TF-IDF redundancy |
| **S_process** | 25% | PRISMA process compliance | Inclusion/exclusion ratio, OA PDF coverage, cluster balance, dedup rate |

All sub-scores are normalized to [0, 1] before weighting.

### Grades

| Grade | Score | Interpretation |
|-------|-------|----------------|
| **A** | ≥ 80 | High-quality corpus, ready for synthesis |
| **B** | 65–79 | Good quality, minor gaps acceptable |
| **C** | 50–64 | Adequate, consider delta enrichment for under-represented clusters |
| **D** | < 50 | Insufficient — run delta queries before synthesis |

> **Checkpoint B**: At QualityScore < 65, PARIS recommends targeted delta queries for under-represented clusters before synthesis. The user decides IMPROVE or PROCEED.

### OpenAlex Coverage Flag

If OpenAlex metadata is available for fewer than 40% of accepted papers, the network sub-score is flagged as `⚠️ unreliable` and the quality report notes the caveat. Target coverage is ≥ 80%.

---

## Output Files

Each run produces the following files in `runs/YYYY-MM-DD-topic/`:

| File | Format | Description |
|------|--------|-------------|
| `scoper_output.md` | Markdown | Concept taxonomy, 8 clusters, keyword list |
| `strategist_output.md` | Markdown | Database query log, hit counts per source |
| `raw_extraction_list.md` | Markdown | All retrieved papers before screening |
| `translation_report.md` | Markdown | Non-English papers detected/translated |
| `borderline_review.md` | Markdown | Papers scored 4: human inclusion/exclusion decisions |
| `curation_report.md` | Markdown | Final accepted corpus with cluster assignments |
| `master_research_data.csv` | CSV | One row per paper: id, title, doi, year, cluster, citation_count, … |
| `prisma_analysis_report.ipynb` | Jupyter | 30-cell notebook: PRISMA stats, network graphs, QualityScore |
| `references.bib` | BibTeX | Auto-generated BibTeX for all accepted papers |
| `pdf_retrieval_report.md` | Markdown | PDF coverage by source (OA %, arXiv %) |
| `pdf_analysis_report.md` | Markdown | Extracted methods, limitations, reproducibility indicators |
| `quality_report.md` | Markdown | QualityScore dashboard, sub-scores, recommendations |
| `openalex_cache.json` | JSON | Cached OpenAlex metadata (referenced_works, citation counts) |
| `gap_analysis.md` | Markdown | 11 cross-cluster gaps, temporal/platform gaps, author-quoted open questions |
| `limits_report.md` | Markdown | TRL matrix, Top 5 improvement paths, reproducibility map |
| `fig1_taxonomy.svg/png` | SVG + PNG | Thematic cluster taxonomy tree |
| `fig2_timeline.png` | PNG 300dpi | Stacked bar: publication timeline by cluster |
| `fig3_platform_heatmap.png` | PNG 300dpi | Platform × cluster coverage heatmap |
| `fig4_concept_network.png` | PNG 300dpi | Keyword co-occurrence network (top 30) |
| `fig5_gap_radar.png` | PNG 300dpi | Cluster coverage radar (size × temporal × citation) |
| `figures_manifest.md` | Markdown | Caption and usage for each figure |
| `synthesis_outline.md` | Markdown | Section plan and cluster assignments (Checkpoint C) |
| `paper_draft.md` | Markdown | Full manuscript (~7,000–9,000 words) |
| `paper_draft.docx` | Word | Pandoc output with embedded bibliography (Elsevier CSL) |
| `paper_draft.tex` | LaTeX | elsarticle class, linenumbers, `\bibliography{references}` |
| `review_report.md` | Markdown | Peer review scorecard, critical/minor issues, verdict |
| `slides_presentation.pptx` | PowerPoint | 11-slide conference deck (dark QuantumControl theme) |

---

## Journal-Ready Output

PARIS targets **Elsevier journal submission** for its final exports.

### paper_draft.md structure

The manuscript must include (enforced by reviewer_agent checklist):

- **Highlights** — 3–5 bullets, ≤ 85 characters each, before the Abstract
- **Keywords** — 5–8 terms
- **Abstract** — ≤ 250 words
- **CRediT Author Contribution Statement** — per Elsevier guidelines
- **Declaration of Competing Interests**
- **Acknowledgments**

### paper_draft.docx

Generated via:
```bash
pandoc paper_draft.md \
  --bibliography=references.bib \
  --citeproc \
  --csl=elsevier-with-titles.csl \
  -o paper_draft.docx
```

### paper_draft.tex

Generated with `\documentclass[preprint,12pt,authoryear]{elsarticle}`:
```latex
\documentclass[preprint,12pt,authoryear]{elsarticle}
\usepackage{lineno,hyperref,graphicx,booktabs,amsmath}
\journal{[Journal name]}
\begin{document}
\begin{frontmatter}
...
\end{frontmatter}
\linenumbers
```

### slides_presentation.pptx

11-slide structure, QuantumControl theme (navy `#0D1B2A`, blue `#2E86AB`, ice `#D6EAF8`):
1. Title slide
2. Motivation & Research Questions
3. Methodology (PRISMA flowchart)
4. Cluster overview
5. Key findings (per cluster)
6. Dominant cluster deep-dive
7. Cross-cutting themes
8. TRL analysis
9. Research gaps (radar chart)
10. Future directions (Top 5 paths)
11. Conclusion

---

## Example Run

**Topic**: "ML for Robust or Sensitive Quantum Control Protocols" (2026-10-11)

```
[2026-10-11] Step 2 DONE — strategist_agent
             809 unique papers from 6 databases
             (arXiv 249, CrossRef 189, OpenAlex 173, IEEE 100, Scopus 58, S2 47)

[2026-10-11] Step 4b DONE — curator_agent
             396 accepted (8 clusters): C1=35, C2=42, C3=58, C4=44,
             C5=54, C6=29, C7=47, C8=21

[2026-10-13] Step 6 DONE — quality_agent v0.5
             QualityScore: 63.6/100 Grade C
             Network: 0.41 | Bibliometric: 0.62 | Semantic: 0.58 | Process: 0.74
             OpenAlex coverage: 350/396 (88.4%)

[2026-10-13] Step 7.5 DONE — limits_agent
             Mean TRL: 2.13 (95.8% simulation-only)
             Code availability: 0.5% (systemic reproducibility crisis)
             Top path: C7×C2 noise-aware robust control

[2026-10-13] Step 10 DONE — reviewer_agent
             Score: 8.3/10 — ACCEPT WITH MINOR REVISION
             Paper: ~8,100 words, 43 refs, 6 figures

[2026-10-13] Step 11 DONE — export_agent
             paper_draft.docx (37KB, bibliography embedded, Elsevier CSL)
             paper_draft.tex (66KB, 1416 lines, elsarticle)
             slides_presentation.pptx (44KB, 11 slides — PASS)
             Journal-ready checklist: 6/6 ✓
```

**Total pipeline time**: ~4 hours (including human checkpoint reviews)  
**Final corpus**: 396 papers, 2016–2026, 8 thematic clusters

---

## Python Utilities

The `utils/` library provides reusable functions for agents to import directly, avoiding code regeneration.

```python
from utils.openalex_utils import fetch_corpus_metadata, build_bibliographic_coupling_graph
from utils.quality_utils import compute_quality_score
from utils.figures_utils import plot_cluster_taxonomy, plot_gap_radar

# Fetch OpenAlex metadata for 396 papers
paper_refs, cache = fetch_corpus_metadata(df_accepted, Path("openalex_cache.json"),
                                           mailto="your@email.com")

# Compute QualityScore v0.5
qs, details = compute_quality_score(G_bib, df_accepted, scoper_text, curation_report_text)
print(f"QualityScore: {qs:.1f}/100")

# Generate figures
plot_cluster_taxonomy(df_accepted, run_dir)
plot_gap_radar(df_accepted, run_dir)
```

See `utils/README.md` for full API documentation.

---

## Citing PARIS

If you use PARIS in your research, please cite:

```bibtex
@software{paris2026,
  author  = {Cruz, C.},
  title   = {{PARIS}: {PRISMA} Agentic Research Intelligence System},
  year    = {2026},
  note    = {Software. Multi-agent systematic literature review pipeline for Claude Code.
             v0.5. PRISMA 2020 compliant.},
  url     = {https://github.com/YOUR_USERNAME/PARIS}
}
```

---

## Requirements

See `requirements_v03.txt` for the full Python dependency list. Key dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥2.31 | API calls (OpenAlex, CrossRef, S2) |
| `pandas` | ≥2.0 | CSV management |
| `networkx` | ≥3.1 | Bibliographic coupling graphs |
| `pymupdf` (fitz) | ≥1.23 | PDF text extraction |
| `matplotlib` | ≥3.7 | Figures |
| `scikit-learn` | ≥1.3 | TF-IDF, cosine similarity |
| `jupyter` | ≥1.0 | PRISMA analysis notebook |
| `nbconvert` | ≥7.0 | Notebook execution (`--execute --inplace`) |
| `python-louvain` | ≥0.16 | Louvain community detection (optional, fallback to networkx) |

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Contributing

PARIS is a research prototype. Issues and pull requests welcome.

- Report bugs via [GitHub Issues](../../issues)
- The `SOUL.md` files in each agent directory define agent behavior — they are the primary extension point
- New agents follow the naming convention `<role>_agent/SOUL.md`
