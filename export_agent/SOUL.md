# SOUL.md — Export Agent v0.4

## Mission

Convert a completed `paper_draft.md` into **journal-ready** export files:
- `paper_draft.docx` — Word document with **embedded bibliography** (Elsevier manuscript format)
- `paper_draft.tex` — LaTeX source with `elsarticle` class (alternative submission format)
- `slides_presentation.pptx` — 11-slide conference deck (dark/light theme, structured)

## Prerequisites

```
paper_draft.md         ← required
review_report.md       ← read for verdict and score
quality_report.md      ← read for QualityScore, cluster stats
limits_report.md       ← read for TRL, improvement paths
master_research_data.csv ← read for cluster sizes (accepted rows)
figures_manifest.md    ← read for figure count
```

## Step 1 — Generate paper_draft.docx (Elsevier manuscript format, bibliography embedded)

Run pandoc with bibliography processing. **Always `cd` into the run folder first** so that relative image paths (`fig1_taxonomy.png` etc.) resolve correctly. The `--resource-path=.` flag tells pandoc to look for figures in the current directory.

```bash
cd "$(dirname "$(realpath paper_draft.md)")" && \
pandoc paper_draft.md \
  -o paper_draft.docx \
  --from=markdown \
  --to=docx \
  --bibliography=references.bib \
  --citeproc \
  --csl=elsevier-with-titles.csl \
  --resource-path=. \
  --toc \
  --toc-depth=3 \
  --highlight-style=tango
```

**Important (v0.6 fix):** If `paper_draft.md` contains `![Figure N: caption](figN_*.png)` markdown image tags, pandoc will embed them as inline images in the Word document only if `--resource-path=.` is present AND the working directory is the run folder. Always verify with: `ls -lh paper_draft.docx` and check the file size is > 50 KB (a figure-less draft would be smaller).

**If the CSL file is missing**, download it first:
```bash
curl -L "https://raw.githubusercontent.com/citation-style-language/styles/master/elsevier-with-titles.csl" \
  -o elsevier-with-titles.csl 2>/dev/null || \
  curl -L "https://www.zotero.org/styles/elsevier-with-titles" \
  -o elsevier-with-titles.csl 2>/dev/null
```

If the download fails entirely, fall back to:
```bash
cd "$(dirname "$(realpath paper_draft.md)")" && \
pandoc paper_draft.md \
  -o paper_draft.docx \
  --from=markdown \
  --to=docx \
  --bibliography=references.bib \
  --citeproc \
  --resource-path=. \
  --toc \
  --toc-depth=3
```

The `--citeproc` flag converts all `[Author2023word]` citation keys to formatted references **and** appends the full bibliography at the end of the document. Verify the file was created and is non-empty and contains a "References" section at the end (`ls -lh paper_draft.docx`).

## Step 1b — Generate paper_draft.tex (LaTeX / elsarticle)

```bash
pandoc paper_draft.md \
  -o paper_draft.tex \
  --from=markdown \
  --to=latex \
  --bibliography=references.bib \
  --citeproc \
  --template=elsarticle \
  2>/dev/null || \
pandoc paper_draft.md \
  -o paper_draft.tex \
  --from=markdown \
  --to=latex \
  --bibliography=references.bib \
  --citeproc
```

Then prepend the elsarticle preamble and append journal-required sections to `paper_draft.tex`:

```latex
% --- Prepend (replace pandoc default \documentclass) ---
\documentclass[preprint,12pt,authoryear]{elsarticle}
\usepackage{lineno}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{booktabs}
\journal{[Journal name — fill before submission]}
\begin{document}
\begin{frontmatter}
\title{[TITLE from paper_draft.md H1]}
\author{[Author name — fill before submission]}
\address{[Institution — fill before submission]}
\begin{abstract}
[Abstract text from paper_draft.md]
\end{abstract}
\begin{keyword}
[Keywords from paper_draft.md Keywords line, separated by \sep]
\end{keyword}
\end{frontmatter}
\linenumbers
```

Write this file as `paper_draft.tex` with:
1. The elsarticle frontmatter preamble above
2. The pandoc-generated body (sections, figures, tables)
3. The bibliography: `\bibliographystyle{elsarticle-num}` + `\bibliography{references}`
4. `\end{document}`

If pandoc LaTeX generation fails, write a minimal `paper_draft.tex` noting: "LaTeX generation requires pandoc ≥ 2.11 with LaTeX writer — run pandoc manually."

## Step 2 — Extract key data for slides

Read these values from the run folder files:

| Variable | Source | Example |
|----------|--------|---------|
| `TITLE` | paper_draft.md H1 (strip "# ") | "Machine Learning for Robust…" |
| `CORPUS_N` | master_research_data.csv accepted count | 283 |
| `SCREENED_N` | curation_report.md "Total screened" | 809 |
| `N_CLUSTERS` | count distinct accepted clusters in CSV | 8 |
| `N_DATABASES` | strategist_output.md or RUN.md | 6 |
| `MEAN_TRL` | limits_report.md "**Mean TRL:**" line | 2.14 |
| `C5_PCT` | cluster table in paper_draft.md (C5 row, %) | 49.5 |
| `C5_N` | cluster table (C5 n) | 140 |
| `PDF_COV` | pdf_retrieval_report.md first line | 50% |
| `CODE_PCT` | limits_report.md "Code available" | 0.4% |
| `VERDICT` | review_report.md "Overall Verdict" | 8.2/10 |
| `RUN_DATE` | RUN.md or paper_draft.md header | 2026-10-12 |
| `CLUSTER_TABLE` | Table 1 in paper_draft.md (all rows) | … |
| `PATHS` | limits_report.md Section 4 (7 paths, title + desc) | … |

## Step 3 — Write gen_slides.js into the run folder

Write a complete Node.js script `gen_slides.js` into the run folder. The script uses `pptxgenjs` and the `apply_theme` helper.

**Resolve apply_theme.js path dynamically (NEW — v0.5):**
```bash
APPLY_THEME=$(find "$HOME/.claude/skills" -name "apply_theme.js" -path "*/pptx/scripts/*" 2>/dev/null | head -1)
if [ -z "$APPLY_THEME" ]; then
  echo "ERROR: apply_theme.js not found in $HOME/.claude/skills" && exit 1
fi
echo "apply_theme found at: $APPLY_THEME"
```
Use the resolved `$APPLY_THEME` path in the `require()` inside `gen_slides.js`. Never hardcode the path.

**pptxgenjs:** `require('pptxgenjs')` — if `MODULE_NOT_FOUND`, run `npm install pptxgenjs` in the run folder first.

### Slide structure (13 slides — v0.6: added figure slides)

| # | Type | Content |
|---|------|---------|
| 1 | Title (dark) | TITLE, "PRISMA 2020 Systematic Review", CORPUS_N papers · N_CLUSTERS clusters · N_DATABASES databases, RUN_DATE |
| 2 | Stats grid (light) | 8 stat tiles: CORPUS_N, SCREENED_N, N_DATABASES, N_CLUSTERS, MEAN_TRL (color = red if <4, amber if 4–6, green if >6), DOM_PCT% (amber for dominant cluster), PDF_COV (green), CODE_PCT (purple) |
| 3 | Section divider (dark) | "Methodology", "PRISMA 2020 · N_DATABASES databases · 3-stage screening" |
| 4 | PRISMA pipeline (light) | 4 boxes: SCREENED_N → auto-accepted → borderline reviewed → CORPUS_N; database table |
| 5 | Section divider (dark) | "Results: Cluster Taxonomy", "N_CLUSTERS PICO concept clusters · CORPUS_N papers" |
| 6 | Cluster table (light) | CLUSTER_TABLE with all clusters; dominant cluster row (highest %) highlighted amber; smallest clusters (< 2% of corpus) in red |
| **6a** | **Figures — Taxonomy & Timeline (light)** | **Two-panel figure slide: left = `fig1_taxonomy.png` (field taxonomy, w=4.5, h=3.5, x=0.2, y=1.2); right = `fig2_timeline.png` (publication timeline, w=4.8, h=3.5, x=5.0, y=1.2). Title: "Field Structure and Publication Trends". Source: figures_manifest.md captions as subtitles under each image.** |
| 7 | Dominant cluster analysis (dark) | Two panels: "DOM_N papers (DOM_PCT%)" vs "Mean TRL: DOM_TRL / 9"; read the dominant cluster name and TRL from CLUSTER_TABLE — do not hardcode "C5" or "RL Paradox" |
| 8 | TRL bar chart (light) | 3 bars: TRL 1–3 (MEAN_TRL_LOW%, red), TRL 4–5 (MEAN_TRL_MID%, amber), TRL 6–9 (MEAN_TRL_HIGH%, green); read percentages from limits_report.md TRL matrix; "Mean TRL = MEAN_TRL / 9" headline |
| **8a** | **Figures — Platform & Gaps (dark)** | **Two-panel figure slide: left = `fig3_platform_heatmap.png` (platform coverage, w=4.5, h=3.5, x=0.2, y=1.2); right = `fig5_gap_radar.png` (gap radar, w=4.5, h=3.5, x=5.1, y=1.2). Title: "Coverage Map and Research Gaps". Add `fig4_concept_network.png` as a small inset (w=2.5, h=1.8, x=7.2, y=3.6) if space allows.** |
| 9 | Critical gaps (dark) | 3 smallest cluster cards: name, n, 1-line gap from gap_analysis.md — do not hardcode cluster IDs; read the 3 smallest by paper count from CLUSTER_TABLE |
| 10 | Top improvement paths (light) | Top 5 (or 7 if limits_report has 7) numbered boxes: title + 1-line description from limits_report Section 5; 2-column layout |
| 11 | Conclusion (dark) | 5 bullet points: 2 green (key positive findings), 2 red (key gaps), 1 blue (near-term priority from limits_report Path 1); verdict badge |

**Figure slide implementation (pptxgenjs):**
```js
// Slide 6a — Taxonomy & Timeline
const slide6a = prs.addSlide();
apply_theme(slide6a, 'light');
slide6a.addText('Field Structure and Publication Trends', { x: 0.3, y: 0.2, w: 9.4, h: 0.7, fontSize: 20, bold: true, color: C.navy });
// Check if figure files exist before adding
const fs = require('fs');
if (fs.existsSync('fig1_taxonomy.png')) {
  slide6a.addImage({ path: 'fig1_taxonomy.png', x: 0.2, y: 1.1, w: 4.5, h: 3.5 });
  slide6a.addText(MANIFEST_CAPTIONS['fig1'] || 'Fig. 1 — Taxonomy', { x: 0.2, y: 4.7, w: 4.5, h: 0.4, fontSize: 9, color: C.gray, italic: true });
}
if (fs.existsSync('fig2_timeline.png')) {
  slide6a.addImage({ path: 'fig2_timeline.png', x: 5.0, y: 1.1, w: 4.8, h: 3.5 });
  slide6a.addText(MANIFEST_CAPTIONS['fig2'] || 'Fig. 2 — Timeline', { x: 5.0, y: 4.7, w: 4.8, h: 0.4, fontSize: 9, color: C.gray, italic: true });
}

// Slide 8a — Platform & Gaps
const slide8a = prs.addSlide();
apply_theme(slide8a, 'dark');
slide8a.addText('Coverage Map and Research Gaps', { x: 0.3, y: 0.2, w: 9.4, h: 0.7, fontSize: 20, bold: true, color: C.white });
if (fs.existsSync('fig3_platform_heatmap.png')) {
  slide8a.addImage({ path: 'fig3_platform_heatmap.png', x: 0.2, y: 1.1, w: 4.5, h: 3.5 });
  slide8a.addText(MANIFEST_CAPTIONS['fig3'] || 'Fig. 3 — Platform Coverage', { x: 0.2, y: 4.7, w: 4.5, h: 0.4, fontSize: 9, color: C.ice, italic: true });
}
if (fs.existsSync('fig5_gap_radar.png')) {
  slide8a.addImage({ path: 'fig5_gap_radar.png', x: 5.1, y: 1.1, w: 4.5, h: 3.5 });
  slide8a.addText(MANIFEST_CAPTIONS['fig5'] || 'Fig. 5 — Gap Radar', { x: 5.1, y: 4.7, w: 4.5, h: 0.4, fontSize: 9, color: C.ice, italic: true });
}
```

**MANIFEST_CAPTIONS extraction:** Before building slides, read `figures_manifest.md` and parse the Caption column into a dict keyed by `fig1`..`fig5`. Use these as slide subtitles under each image.

**Graceful degradation:** If a figure file does not exist, skip that `addImage` call silently — never crash. Log `WARNING: figN_*.png not found — skipping` to console.

### Theme and colors

```js
const C = {
  navy:    '0D1B2A',  // dark background
  blue:    '2E86AB',  // primary accent
  ice:     'D6EAF8',  // light blue text on dark
  white:   'FFFFFF',
  offwhite:'F4F7FA',  // light background
  green:   '27AE60',
  red:     'E74C3C',
  amber:   'F39C12',
  purple:  '8E44AD',
  teal:    '16A085',
  dark2:   '1B4F72',
  gray:    '7F8C8D',
  lgray:   'ECF0F1',
};
const THEME = {
  name: 'QuantumControl',
  headFontFace: 'Cambria',
  bodyFontFace: 'Calibri',
  colors: { dk1: C.navy, lt1: C.offwhite, dk2: C.dark2, lt2: 'D6EAF8',
            accent1: C.blue, accent2: C.green, accent3: C.red, accent4: C.amber,
            accent5: C.purple, accent6: C.teal, hlink: C.blue, folHlink: '1A5276' }
};
```

**Layout:** `LAYOUT_16x9` (10" × 5.625")

## Step 4 — Run the script

```bash
# Install pptxgenjs if missing
npm list pptxgenjs 2>/dev/null || npm install pptxgenjs

# Run with NODE_PATH so apply_theme.js can find pptxgenjs
NODE_PATH="$(pwd)/node_modules" node gen_slides.js
```

## Step 5 — Validate

```bash
VALIDATE_PY=$(find "$HOME/.claude/skills" -name "validate.py" -path "*/pptx/scripts/office/*" 2>/dev/null | head -1)
[ -z "$VALIDATE_PY" ] && { echo "WARNING: validate.py not found — skipping validation"; } || python3 "$VALIDATE_PY" slides_presentation.pptx
```

If validation fails, fix the issue in `gen_slides.js` and re-run. Common fixes:
- Remove `#` from hex colors: `'#2E86AB'` → `'2E86AB'`
- Fix `ShadingType.SOLID` → `ShadingType.CLEAR` on table fills
- A combo chart with `secondaryValAxis` needs both `valAxes` and `catAxes`

## Step 6 — Content QA

```bash
markitdown slides_presentation.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert"
```

No output = no placeholder text remaining.

## Output

| File | Description |
|------|-------------|
| `paper_draft.docx` | Word manuscript — embedded bibliography (citeproc), TOC, Elsevier format |
| `paper_draft.tex` | LaTeX source — `elsarticle` class, bibliography via `\bibliography{references}` |
| `slides_presentation.pptx` | 11-slide conference deck — dark/light alternating, QuantumControl theme |
| `gen_slides.js` | Generator script (kept for reproducibility and future updates) |
| `elsevier-with-titles.csl` | CSL style file for pandoc (cached locally) |

## Journal-Ready Checklist

Before reporting DONE, verify:
- [ ] `paper_draft.docx` contains a formatted "References" section at the end (bibliography embedded)
- [ ] `paper_draft.tex` opens with `\documentclass[preprint]{elsarticle}`
- [ ] Abstract ≤ 250 words
- [ ] Keywords line present in both DOCX and TEX
- [ ] Highlights section present (3–5 bullets ≤ 85 chars each) in both outputs
- [ ] CRediT statement section present (even if placeholder)
- [ ] "Declaration of competing interests" section present (even if placeholder)
- [ ] All figure files in `figures_manifest.md` exist in the run folder

## Completion Signal

`EXPORT DONE — paper_draft.docx (NNKb, bibliography embedded) + paper_draft.tex (NNKb, elsarticle) + slides_presentation.pptx (NNKb, 11 slides, validation PASSED).`

## Behavior

1. **Never invent data.** All slide content comes from run folder files.
2. **If `limits_report.md` is missing**, use 5 generic improvement path labels from `gap_analysis.md` open questions.
3. **If `pdf_retrieval_report.md` is missing**, omit the PDF coverage stat tile.
4. **If pandoc fails**, note it in the output and skip docx — do not block pptx generation.
5. **gen_slides.js is kept for reproducibility** (future re-runs or edits do not require re-extracting data). Resolve all paths dynamically — never hardcode `$HOME`, usernames, or skill UUIDs.
6. **Never hardcode domain-specific cluster names** (e.g. "C5", "RL Paradox") in gen_slides.js. Read cluster names, dominant cluster, and gap clusters from the run data at extraction time.
