---
name: sota-write
description: Write the complete état de l'art manuscript — thematic clusters, recent advances, integrated figures, gaps, limitations analysis and future directions (from limits_report.md when available), PRISMA methodology with QualityScore, BibTeX bibliography — with an outline approval checkpoint.
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).

## Locate the run
Skill argument (run folder path) or ACTIVE run in `runs/index.md`.

## Step 0 — Check the analysis chain
Required in the run folder: `master_research_data.csv`, `prisma_analysis_report.ipynb`, `curation_report.md`, `quality_report.md`, `gap_analysis.md`, `figures_manifest.md`. Missing → name the skill that produces it (`/sota-curate` or `/sota-quality`) and stop.
Optional but recommended: `limits_report.md` (from `limits_agent`, step 7.5 of `/sota-quality`). If present, the synthesizer must consume its Top 5 improvement paths for Future Directions and its per-cluster limitations for the Discussion/Limitations sections.

## Step 1 — Bibliography
Build `references.bib` for every accepted paper: DOI → `https://api.crossref.org/works/<doi>/transform/application/x-bibtex`; arXiv-only → `@misc` entry with eprint id. Key format `FirstAuthorYEARword`. Report entries that could not be resolved.

## Step 2 — Outline (Checkpoint C)
Fork `synthesizer_agent` (`synthesizer_agent/SOUL.md`) for phase 1 only → `synthesis_outline.md`. Present:
- clusters (name, N papers, 2-sentence description, bridge papers)
- section plan
- figure placement (the 5 figures of `figures_manifest.md` + PRISMA flowchart from the notebook)
- which gaps go to Discussion vs Future Directions
Wait for explicit approval or edits.

## Step 3 — Full draft
Fork `synthesizer_agent` phase 2 with the approved outline → `paper_draft.md`. Mandatory content:
- **Abstract** ≤ 250 words: context, method, corpus size, QualityScore, findings
- **Introduction** with RQ1–RQ4
- **Background**: key definitions per cluster
- **Methodology**: databases + queries, translator, curation criteria and final counts (from the decision log), QualityScore and its caveats, PRISMA flowchart
- **One section per cluster**: open with bridge papers, a **"Recent advances"** subsection for papers from the last 24 months, close with an intra-cluster synthesis
- **Discussion**: ≥ 3 cross-cutting themes, convergences/tensions, platform and intersection gaps, co-authorship communities
- **Future Directions**: ≥ 5 items — sourced from `limits_report.md` Top 5 improvement paths when available, otherwise from `gap_analysis.md` open questions. Never invented.
- **Limitations**, **Conclusion**
- **References** resolved against `references.bib` — every citation must exist in the CSV
- every figure referenced inline "(Fig. N)" with its manifest caption

## Step 4 — Hand-off
Report word count, sections, figures, references. Update RUN.md. Next: `/sota-review`.
