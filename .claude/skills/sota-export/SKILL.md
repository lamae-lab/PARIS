---
name: sota-export
description: Export a completed PARIS paper_draft.md to Word (.docx) and PowerPoint (.pptx) using the export_agent.
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).

## Locate the run
Skill argument (run folder path) or ACTIVE run in `runs/index.md`. Requires `paper_draft.md`. Also reads `review_report.md`, `quality_report.md`, `limits_report.md`, `master_research_data.csv`.

## Steps

1. **Verify prerequisites** — confirm `paper_draft.md` exists and is non-empty. If `review_report.md` exists, read the verdict; warn if verdict is MAJOR or REJECT (export is still possible but the draft may not be final).

2. **Fork `export_agent`** (`export_agent/SOUL.md`) passing the run folder path. The agent:
   - Generates `paper_draft.docx` via pandoc
   - Reads key stats from run folder files
   - Writes `gen_slides.js` and runs it (requires `npm install pptxgenjs` if needed, `NODE_PATH` set to run folder's `node_modules`)
   - Validates `slides_presentation.pptx` with the pptx skill's `validate.py`

3. **Verify outputs** — confirm both files exist:
   ```bash
   ls -lh <run_folder>/paper_draft.docx <run_folder>/slides_presentation.pptx
   ```

4. **Report** — list both files with their sizes and the PPTX validation result.

5. **Update RUN.md** — mark Step 11 (export_agent) as ✅ DONE with output file names.
