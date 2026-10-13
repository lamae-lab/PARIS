---
name: sota-review
description: Adversarial review of a PARIS manuscript (citation integrity, PRISMA counts, quality-chain use, gap + limits coverage, figures) and revision loop until the verdict is ACCEPT or MINOR, then auto-runs export_agent to generate .docx and .pptx.
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).

## Locate the run
Skill argument (run folder path) or ACTIVE run in `runs/index.md`. Requires `paper_draft.md`.

## Steps

1. **Fork `reviewer_agent`** (`reviewer_agent/SOUL.md`) → `review_report.md`. It runs the mandatory verification checklist (every citation in CSV and `references.bib`, PRISMA counts consistent with the curation decision log, QualityScore in Methodology, bridge papers cited, Future Directions traced to `gap_analysis.md` or `limits_report.md` Top 5 paths, figure count matches manifest, if `limits_report.md` exists: verify Top 5 improvement paths are covered in Future Directions) before scoring the 10 dimensions.
2. **Present**: verdict, scorecard, critical issues, minor issues.
3. **If MAJOR REVISION or REJECT**, or any critical issue: propose the fix plan, and with user agreement fork `synthesizer_agent` to revise `paper_draft.md` (keep the previous version as `paper_draft_v<N>.md`), then re-run the reviewer. Max 3 iterations before handing back to the user.
4. **On ACCEPT / MINOR**: apply minor fixes if the user wants, then mark the run COMPLETED in `runs/index.md` (topic, date, final corpus, QualityScore, verdict) and in RUN.md.
5. **Fork `export_agent`** (`export_agent/SOUL.md`) → `paper_draft.docx` + `slides_presentation.pptx`. Report file sizes and PPTX validation result. Update Step 11 in RUN.md.
