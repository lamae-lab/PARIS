# Research Run — [TOPIC]

**Date:** YYYY-MM-DD  
**Primary Research Goal:** [One sentence]  
**Domain:** [e.g., quant-ph, cs.AI, cs.CL]  
**Date range:** YYYY–YYYY  
**Target databases:** OpenAlex, Semantic Scholar, arXiv, CrossRef, IEEE Xplore, ScienceDirect/Elsevier, Google Scholar  
**Language:** English + [other languages if known]  
**Elsevier API key available:** YES / NO  
**IEEE API key available:** YES / NO  
**Semantic Scholar API key available:** YES / NO  
**Unpaywall email configured:** YES / NO  
**OpenAlex polite-pool email:** (enter email or leave blank)

### Environment — set before running strategist_agent and pdf_retriever_agent

```bash
export ELSEVIER_API_KEY="..."        # required for ScienceDirect (step 2)
export ELSEVIER_INST_TOKEN="..."     # required for ScienceDirect full text (step 2.5)
export IEEE_API_KEY="..."            # required for IEEE Xplore (step 2)
export S2_API_KEY="..."              # optional but strongly recommended (100M req/day vs ~10)
export UNPAYWALL_EMAIL="..."         # required for Unpaywall PDF download (step 2.5)
# OpenAlex polite pool: add &mailto=<email> to API requests, no env var needed
```  

---

## Run Parameters

- **Max papers to retrieve:** ~200
- **Acceptance threshold (relevance score):** ≥ 4
- **Cluster balance soft cap:** auto (ceil(accepted / n_concepts × 1.5))

---

## Step Tracker

| Step | Agent | Status | Output file(s) | Notes |
|------|-------|--------|----------------|-------|
| 1 | scoper_agent | ⬜ TODO | `scoper_output.md` | |
| 2 | strategist_agent | ⬜ TODO | `strategist_output.md`, `raw_extraction_list.md` | |
| 2.5 | pdf_retriever_agent | ⬜ TODO | `pdf_retrieval_report.md`, `pdfs/` | Skip if no OA sources available |
| 3 | translator_agent | ⬜ TODO | `translation_report.md` | Skip if all papers English |
| 4a | curator_agent | ⬜ TODO | `borderline_review.md` | ⚠️ HUMAN CHECKPOINT |
| 4b | curator_agent | ⬜ TODO | `curation_report.md` | After human decisions |
| 5 | agent_analyst | ⬜ TODO | `master_research_data.csv`, `prisma_analysis_report.ipynb` (Sections 1–5) | |
| 5b | bibtex_agent | ⬜ TODO | `references.bib` | CrossRef + arXiv fallback |
| 5.5 | pdf_analyzer_agent | ⬜ TODO | `pdf_analysis_report.md` | Skip if pdfs/ empty |
| 6 | quality_agent | ⬜ TODO | `quality_report.md`, `openalex_cache.json`, notebook Section 7 | ⚠️ CONDUCTOR CHECKPOINT (QualityScore) |
| 7 | gap_finder_agent | ⬜ TODO | `gap_analysis.md` | |
| 7.5 | limits_agent | ⬜ TODO | `limits_report.md` | Works on abstracts if no PDFs |
| 8 | figure_agent | ⬜ TODO | 5 figures + `figures_manifest.md`, notebook Section 8 | |
| 9a | synthesizer_agent | ⬜ TODO | `synthesis_outline.md` | ⚠️ CONDUCTOR CHECKPOINT |
| 9b | synthesizer_agent | ⬜ TODO | `paper_draft.md` | After outline approval |
| 10 | reviewer_agent | ⬜ TODO | `review_report.md` | |
| 11 | export_agent | ⬜ TODO | `paper_draft.docx`, `slides_presentation.pptx`, `gen_slides.js` | Auto-runs after ACCEPT or MINOR verdict |

Status: ⬜ TODO / 🔄 IN PROGRESS / ✅ DONE / ❌ FAILED / ⚠️ NEEDS REVIEW / 👤 AWAITING HUMAN

---

## Human Checkpoint A — Borderline Papers
*Fill in after curator_agent phase 1 completes.*

| Paper ID | Title | My decision (INCLUDE/EXCLUDE) |
|----------|-------|-------------------------------|

---

## Conductor Checkpoint B — Synthesis Outline
*Fill in after synthesizer_agent phase 1 completes.*

- [ ] Clusters approved
- [ ] Paper structure approved
- [ ] Revisions requested: [describe or leave blank]

---

## Conductor Log

```
[YYYY-MM-DD HH:MM] Run started.
```

---

## Conductor Notes
