---
name: sota-quality
description: Measure corpus quality (QualityScore 0–100), hold the quality checkpoint, then run Gap Finder → Limits agent (TRL + improvement paths) → Figure agents.
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).

## Locate the run
Skill argument (run folder path) or ACTIVE run in `runs/index.md`.

## Prerequisites
`master_research_data.csv` and `prisma_analysis_report.ipynb` exist. Otherwise point the user to `/sota-curate`.

## Steps

1. **Enrich citations first.** If most `citation_count` values are 0 or empty, fetch them from OpenAlex (`https://api.openalex.org/works/doi:<doi>` or title search, with `mailto=` param), also pulling `referenced_works` for the network metrics. Cache everything in `openalex_cache.json`. Without this step the bibliometric and network scores are artificially low.
2. **Run `quality_agent`** (fork, `quality_agent/SOUL.md`) → `quality_report.md` + notebook Section 7. It reuses `bridge_papers.json` from the Analyst when present.
3. **Present the dashboard**:
   ```
   QualityScore XX/100 — [level]
   Network XX (30%) | Bibliometric XX (25%) | Semantic XX (20%) | Process XX (25%)
   Bridge papers: ...
   Top recommendations: ...
   ```
   Say explicitly which metric families were unavailable and how weights were redistributed.
4. **Checkpoint B** — if QualityScore < 65, recommend IMPROVE; ask the user PROCEED or IMPROVE.
   - IMPROVE → act on the chosen recommendations (targeted Strategist delta query, re-curation), re-run Analyst if the corpus changed, then re-run this skill.
   - PROCEED → continue.
5. **Run `gap_finder_agent`** → `gap_analysis.md` (intersection matrix, temporal/platform/methodological gaps, open questions quoted from authors). If `pdf_analysis_report.md` exists, instruct the agent to also extract open questions from conclusion sections (not just abstracts).
6. **Run `limits_agent`** (step 7.5) → `limits_report.md`. Fork `limits_agent/SOUL.md`. It reads `master_research_data.csv` + `gap_analysis.md` + `scoper_output.md` and, if available, `pdf_analysis_report.md`. Produces: limitations per cluster, TRL matrix, reproducibility map, cross-cluster complementarities, Top 5 improvement paths. Always run — it works on abstracts alone if no PDFs are available. Present the Top 5 paths to the user.
7. **Run `figure_agent`** → write the plotting code into notebook Section 8 **and execute it** so the 5 files exist (`fig1_taxonomy.svg`, `fig2_timeline.png`, `fig3_platform_heatmap.png`, `fig4_concept_network.png`, `fig5_gap_radar.png`, 300 DPI), plus `figures_manifest.md`. If execution fails, report it — never list a figure as done when the file doesn't exist.
8. Update RUN.md and tell the user the next step is `/sota-write`.
