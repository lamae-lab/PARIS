# PARIS — PRISMA Agentic Research Intelligence System

**Version:** 0.5 (2026-10-13) — evolved from sota-agent-0.4  
**v0.5 fixes:** Deduplication in curator_agent (arXiv ID priority); arXiv ID + rate-limiting in strategist_agent; dynamic path resolution in export_agent; main/SOUL.md resync (13 steps); QualityScore normalization + grade letter; env vars in RUN.md template; bibtex_agent (new, step 5b); limits_agent now reads curation_report.md  
**v0.5 additions (in-place):** dedup arXiv ID, rate-limiting, dynamic path resolution, QualityScore normalization, bibtex_agent, journal-ready output (Highlights/CRediT/elsarticle), code consolidation into utils/ (openalex_utils, quality_utils, figures_utils), strategist C6 domain contamination guard  
**v0.4 addition:** export_agent — generates `paper_draft.docx` (Word) and `slides_presentation.pptx` (11-slide conference deck)  
**v0.3 additions:** PDF retrieval (OA sources), full-text PDF analysis, limits agent (TRL matrix + improvement paths), synthesizer enriched with limits_report  
**v0.2 additions:** API-based retrieval, translator agent, gap finder, figure agent, updater agent, BibTeX export, cluster balance enforcement, human checkpoints

---

## Directory Structure

```
sota-agent-0.4/
├── CLAUDE.md                    ← start here every session
├── main/
│   ├── SOUL.md                  ← Conductor identity, pipeline v0.4
│   └── AGENTS.md                ← workspace rules + 14-agent registry
├── scoper_agent/SOUL.md
├── strategist_agent/SOUL.md
├── translator_agent/SOUL.md
├── curator_agent/SOUL.md
├── agent_analyst/SOUL.md
├── gap_finder_agent/SOUL.md
├── limits_agent/SOUL.md         ← v0.3: TRL matrix, limitations, improvement paths
├── figure_agent/SOUL.md
├── synthesizer_agent/SOUL.md
├── reviewer_agent/SOUL.md
├── updater_agent/SOUL.md
├── pdf_retriever_agent/SOUL.md  ← v0.3: OA PDF download
├── pdf_analyzer_agent/SOUL.md   ← v0.3: full-text extraction
├── export_agent/SOUL.md         ← NEW v0.4: DOCX + PPTX export
├── utils/
│   ├── __init__.py              ← exports all utils functions
│   ├── api_clients.py           ← PDF retrieval via OA APIs
│   ├── pdf_utils.py             ← pymupdf text extraction
│   ├── csv_utils.py             ← CSV load/save/update helpers
│   ├── openalex_utils.py        ← OpenAlex fetch, bib coupling, bridge papers (NEW v0.5)
│   ├── quality_utils.py         ← QualityScore v0.5 sub-score functions (NEW v0.5)
│   ├── figures_utils.py         ← 5 PRISMA figure generators (NEW v0.5)
│   └── README.md                ← usage examples for all modules
└── runs/
    ├── index.md                 ← global runs index
    ├── template/RUN.md          ← copy to start a new run
    └── YYYY-MM-DD-topic/
        ├── RUN.md
        ├── scoper_output.md
        ├── strategist_output.md
        ├── raw_extraction_list.md
        ├── translation_report.md
        ├── borderline_review.md      ← human checkpoint
        ├── curation_report.md
        ├── master_research_data.csv
        ├── prisma_analysis_report.ipynb
        ├── pdfs/                     ← v0.3: downloaded PDFs
        ├── pdf_retrieval_report.md   ← v0.3
        ├── pdf_analysis_report.md    ← v0.3
        ├── gap_analysis.md
        ├── limits_report.md          ← v0.3
        ├── figures_manifest.md
        ├── fig1_taxonomy.svg
        ├── fig2_timeline.png
        ├── fig3_platform_heatmap.png
        ├── fig4_concept_network.png
        ├── fig5_gap_radar.png
        ├── synthesis_outline.md
        ├── paper_draft.md
        ├── paper_draft_v*.md         ← revision backups
        ├── references.bib
        ├── review_report.md
        ├── paper_draft.docx          ← NEW v0.4
        ├── slides_presentation.pptx  ← NEW v0.4
        └── gen_slides.js             ← NEW v0.4: PPTX generator script
```

---

## How to Start a New Review

```bash
cp -r runs/template runs/YYYY-MM-DD-your-topic
# Edit RUN.md, then in Claude Code:
```

> *"Act as the PRISMA Conductor v0.4. Read `main/SOUL.md` and `main/AGENTS.md`, then start a new run from `runs/YYYY-MM-DD-your-topic/RUN.md`."*

---

## How to Export an Existing Draft

> *"/sota-export"* — on the active run, or pass the run folder path as argument.

Or manually:
> *"Act as the PRISMA Conductor v0.4. Run the export_agent on `runs/YYYY-MM-DD-topic/`."*

---

## What's New vs openclaw

| Feature | openclaw | sota-agent-0.2 | sota-agent-0.3 | sota-agent-0.4 |
|---------|---------|----------------|----------------|----------------|
| Paper retrieval | Web scraping | OpenAlex / S2 / CrossRef APIs | — | — |
| Non-English papers | Excluded | translator_agent | — | — |
| Cluster balance | None | Quota enforcement | — | — |
| Human checkpoints | Informal | 2 formal checkpoints | — | — |
| Gap analysis | None | gap_finder_agent | Enrichi texte complet | — |
| Figures | Notebook only | 5 standalone figures | — | — |
| BibTeX | None | Auto-generated from DOI | — | — |
| Full-text PDF | None | None | pdf_retriever_agent | — |
| PDF analysis | None | None | pdf_analyzer_agent | — |
| Limitations/TRL | None | None | limits_agent | — |
| Word export | None | None | None | **export_agent (.docx)** |
| Slide deck | None | None | None | **export_agent (.pptx, 11 slides)** |
| Deduplication | None | DOI + title | DOI + title | **arXiv ID + DOI + title (curator)** |
| BibTeX agent | None | ad-hoc | ad-hoc | **bibtex_agent (step 5b)** |
| API pre-flight | None | None | None | **strategist_agent pre-flight** |

---

## Pipeline at a Glance

```
Scope → Strategy → PDF Retrieve (2.5) → Translate → [Curator + HUMAN CHECKPOINT]
      → Analyze → PDF Analyze (5.5) → Quality → Gap Finder → Limits (7.5)
      → Figures → [Synthesize outline + CONDUCTOR CHECKPOINT]
      → Write draft → Review → Export (11) → DONE

Step 11 (export_agent) runs automatically after reviewer verdict ACCEPT or MINOR REVISION.
Can also be run standalone via /sota-export.
```
