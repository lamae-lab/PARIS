# AGENTS.md — PARIS Workspace

## Every Session

Before doing anything else:
1. Read `CLAUDE.md` — workspace map and how to start a run
2. Read `main/SOUL.md` — pipeline protocol and checkpoints
3. Read `runs/index.md` — list of all completed and active runs
4. Read `runs/ACTIVE_RUN/RUN.md` if a run is in progress

## Memory

- **Run logs:** `runs/YYYY-MM-DD-topic/RUN.md` — per-run tracker and conductor log
- **Global index:** `runs/index.md` — all runs summary

## Safety

- `trash` > `rm` — never permanently delete run outputs
- Never skip a mandatory human checkpoint
- Never modify original files in an update run — append only

## Sub-Agent Registry (v0.5 — 15 agents)

| # | Agent | Role | New in |
|---|-------|------|--------|
| 1 | **scoper_agent** | Concept extraction and keyword mapping | v0.1 |
| 2 | **strategist_agent** | API-based retrieval (OpenAlex, S2, arXiv, CrossRef, Elsevier, IEEE); API pre-flight + rate-limiting | v0.2 *(updated v0.5)* |
| 2.5 | **pdf_retriever_agent** | Full-text PDF download via OA sources (OpenAlex, arXiv, Elsevier, Unpaywall, S2) | v0.3 |
| 3 | **translator_agent** | Non-English abstract detection and translation | v0.2 |
| 4 | **curator_agent** | Pre-deduplication (arXiv ID / DOI / title), relevance scoring, cluster balance, borderline human review | v0.2 *(updated v0.5)* |
| 5 | **agent_analyst** | CSV consolidation + PRISMA Jupyter notebook (Sections 1–5) | v0.1 |
| 5b | **bibtex_agent** | CrossRef BibTeX export + arXiv fallback; generates `references.bib` | **v0.5 NEW** |
| 5.5 | **pdf_analyzer_agent** | Full-text extraction: sections, limitations, future work, methods, reproducibility indicators | v0.3 |
| 6 | **quality_agent** | QualityScore 0–100 with grade letter (A/B/C/D); normalized sub-scores; OA coverage flag | v0.2 *(updated v0.5)* |
| 7 | **gap_finder_agent** | Research gap analysis: intersections, temporal, platform, methodological, open questions | v0.2 |
| 7.5 | **limits_agent** | TRL matrix, methodological limitations, reproducibility map, Top 5 improvement paths | v0.3 *(updated v0.5)* |
| 8 | **figure_agent** | 5 visual assets: taxonomy, timeline, heatmap, concept network, gap radar | v0.2 |
| 9 | **synthesizer_agent** | Thematic clustering, outline validation, full manuscript draft | v0.2 (updated v0.3) |
| 10 | **reviewer_agent** | Adversarial peer review, citation integrity check, final verdict | v0.2 |
| 11 | **export_agent** | DOCX (pandoc) + PPTX (pptxgenjs, 11 slides); dynamic path resolution | v0.4 *(updated v0.5)* |
| 12 | **updater_agent** | Delta retrieval for existing runs (refreshes corpus without full re-run) | v0.2 |

## Execution Protocol

### New Run
1. `scoper_agent` → validate `scoper_output.md`
2. `strategist_agent` → validate `raw_extraction_list.md`
2.5. `pdf_retriever_agent` → validate `pdf_retrieval_report.md` + `pdfs/` folder (run only if OA coverage > 0%)
3. `translator_agent` → validate `translation_report.md`
4. `curator_agent` phase 1 → present `borderline_review.md` → **await human decisions**
5. `curator_agent` phase 2 → validate `curation_report.md`
6. `agent_analyst` → validate CSV + notebook (Sections 1–5)
5.5. `pdf_analyzer_agent` → validate `pdf_analysis_report.md` + CSV update (run only if pdfs/ has files)
7. `quality_agent` → validate `quality_report.md` + notebook Section 7 — review QualityScore with user
8. `gap_finder_agent` → validate `gap_analysis.md`
7.5. `limits_agent` → validate `limits_report.md`
9. `figure_agent` → validate `figures_manifest.md`
10. `synthesizer_agent` phase 1 → present `synthesis_outline.md` → **await conductor approval**
11. `synthesizer_agent` phase 2 → validate `paper_draft.md`
12. `reviewer_agent` → deliver verdict
13. **If verdict ACCEPT or MINOR REVISION:** `export_agent` → validate `paper_draft.docx` + `slides_presentation.pptx`

### Delta Run (corpus refresh)
1. `updater_agent` → validate `update_log.md` + `delta_report.md`
2. Per recommendation: re-run `agent_analyst` and/or `synthesizer_agent`

## BibTeX Export (Step 5b)

Fork `bibtex_agent` (`bibtex_agent/SOUL.md`) after step 5 (agent_analyst). It queries CrossRef for DOI-based entries and constructs arXiv-format fallbacks. Output: `references.bib` in the run folder.

## Heartbeats

Default heartbeat: check active run folder for any output file that exists but hasn't been validated yet. Report status to user.
