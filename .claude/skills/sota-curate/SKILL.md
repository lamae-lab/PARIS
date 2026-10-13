---
name: sota-curate
description: Resolve the borderline-papers checkpoint of a PARIS run, finalize the curation report, run the Analyst (notebook Sections 1–6), then run PDF Analyzer if PDFs are available (step 5.5).
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).

## Locate the run
Use the skill argument if it is a run folder path (runs may live outside the framework, e.g. `openclaw/runs/...`). Otherwise take the ACTIVE run from `runs/index.md`; if several, ask.

## Steps

1. **Read the borderlines** from `borderline_review.md` (or the borderline section of `curation_report.md`). If curation hasn't run, run `curator_agent` first.
2. **Present** them: `# | id | title | score | curator recommendation`. Accept per-id INCLUDE/EXCLUDE or "include all"/"exclude all".
3. **Record decisions** in a "Conductor Decision" section of `curation_report.md`.
4. **Compute the final corpus from the decision log**, not from the curator's summary line: count ACCEPT rows + included borderlines. If the summary disagrees, write the corrected counts in the report and RUN.md.
5. **Run `agent_analyst`** (fork, SOUL.md `agent_analyst/SOUL.md`). It must produce:
   - `master_research_data.csv` — all screened papers, `accepted` True/False, columns per the SOUL.md
   - `prisma_analysis_report.ipynb` Sections 1–6: flowchart, descriptive stats, co-authorship network **with Louvain communities + modularity**, keywords (TF-IDF, K-Means, WordCloud), temporal growth, **citation network (co-citation, bibliographic coupling, PageRank, bridge papers via OpenAlex)**
   - `bridge_papers.json`
6. **Validate**: CSV accepted count == final corpus count from step 4; notebook has 6 sections. Update RUN.md.
7. **Run `pdf_analyzer_agent`** (step 5.5, optional) if `pdfs/` exists and contains at least one file. Fork `pdf_analyzer_agent/SOUL.md` → `pdf_analysis_report.md` + CSV columns update (`full_text_available`, `sections_detected`, `limitations_extracted`, `future_work_extracted`, `methods_extracted`, `open_code`, `open_data`). Uses `utils/pdf_utils.py`. Skip silently if `pdfs/` is empty or absent. Report coverage % in RUN.md.
8. Tell the user the next step is `/sota-quality`.
