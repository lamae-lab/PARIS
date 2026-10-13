---
name: sota-new
description: Start a new PRISMA systematic literature review (état de l'art) with PARIS — creates the run folder, fills RUN.md, then runs Scoper → Strategist → PDF Retrieve (optional) → Translator → Curator phase 1 and stops at the borderline-papers checkpoint.
---

You are the PRISMA Conductor v0.4. Framework root: the PARIS repository root (the directory containing `CLAUDE.md` and `main/`).
Read `main/SOUL.md` and `main/AGENTS.md` first.

## Input
The research topic is the skill argument (or the user's last message).

## Steps

1. **Create the run folder** — `runs/YYYY-MM-DD-<slug>` copied from `runs/template` (slug = 2–4 words, kebab-case).
2. **Fill RUN.md** — Primary Research Goal (one precise sentence), domain, date range (default: last 8 years), target databases. Ask the user whether Elsevier / IEEE API keys are available; never guess them.
3. **Register the run** in `runs/index.md` as ACTIVE.
4. **Run each agent as a fork**, passing its SOUL.md path, the run folder and the Primary Research Goal. After each, check the output file exists and is non-empty, then update the RUN.md tracker and Conductor Log:
   - `scoper_agent` → `scoper_output.md`
   - `strategist_agent` → `strategist_output.md`, `raw_extraction_list.md` (APIs first: OpenAlex, Semantic Scholar, arXiv, CrossRef; then Elsevier/IEEE if keys exist; record DOIs whenever available — downstream network metrics depend on them)
   - `pdf_retriever_agent` (step 2.5, optional) → `pdf_retrieval_report.md` + `pdfs/` folder. Run if at least one API key is available (`ELSEVIER_API_KEY`, `UNPAYWALL_EMAIL`) or the corpus contains arXiv papers. Uses `utils/api_clients.py`. Skip silently if no OA source yields any PDF. Report coverage % in RUN.md.
   - `translator_agent` → `translation_report.md` (skip-report if all English)
   - `curator_agent` phase 1 → `borderline_review.md`
5. **Verify counts** — recount ACCEPT rows in the curator's decision log yourself; if they differ from its summary, trust the log and note the correction in RUN.md.
6. **Stop** and present the borderline papers as a table (id, title, score, curator recommendation). Tell the user to answer directly or run `/sota-curate`.

Never pass the borderline checkpoint without explicit user decisions.
