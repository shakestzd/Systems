---
description: Run notebook execution checks and evaluate communication quality (decision-first, concept tax, orange cones, why-chain, failure movie)
argument-hint: "[optional notebook path, directory, or glob]"
---

# Notebook Execution + Communication Audit

Run this command when I ask to "run and evaluate notebooks."

## Inputs

- Target: `$ARGUMENTS`
- If no target is provided:
  - Read `research/deep_dives.csv`
  - Select rows with `Status` in `Active` or `Scoping`
  - Resolve notebook paths from `Notebook Dir` under `notebooks/`
  - Include `*.py` notebooks except `99_methods_and_sources.py`

## Phase 1: Run Checks

1. Run lint gate:
   - `uv run ruff check src/ notebooks/`
2. Run Marimo structural check for target notebooks:
   - `uv run marimo check <resolved notebook paths>`
3. Run headless execution:
   - `bash scripts/test_notebooks.sh <resolved notebook paths>`
4. Capture failures with exact notebook path and key error line.

## Phase 2: Evaluate Communication Quality

Read every `mo.md(...)` and `mo.callout(...)` cell in the notebook. Review all
reader-facing prose — opening, chart captions, body sections, and closing. Do not
skip cells.

Score each dimension `0-2`:
- `Decision-First`: the key finding or implication appears before the mechanism detail
- `Concept Tax`: a reader with no specialist background can understand why it matters
- `Language`: plain language used throughout; technical terms defined on first use
- `Why Chain`: explicit consequence after each piece of evidence — not just "here is data" but "here is what it means"
- `Failure Movie`: at least one concrete consequence stated as a specific scenario, not as an abstract risk

### Scoring Guide
- `2` = strong and consistent across the notebook
- `1` = present but inconsistent, or weak in key sections
- `0` = missing or ineffective

### Language Review — do this for every prose cell

Read each sentence and flag:

**Unexplained jargon** — technical terms used without definition. Examples of terms
that need explanation when they first appear: "capex", "forward P/E", "OCF", "TTM",
"contracted backlog", "operating lease", "special purpose vehicle", "Jevons paradox",
"price elasticity", "VC cycles", "platform era", "neocloud", "rate recovery schedule".
The rule: if a smart person outside the field would not immediately understand the
term, either define it inline or rewrite the sentence without it.

**Abbreviations without expansion** — flag every abbreviation on first use (e.g.
"YoY" should be "year-on-year", "FY" should be "fiscal year", "SPV" should be
"special purpose vehicle"). Abbreviations are fine after they have been defined.

**Em-dash overuse** — flag any paragraph with more than one em-dash. Em-dashes used
to splice clauses instead of writing proper sentences are a structural tell.
("Revenue was high — costs were also high — so margins fell" should be two sentences.)

**Announcing labels** — flag any bold prefix that announces what the paragraph is
doing rather than doing it: "Decision implication:", "Failure movie:", "Takeaway:",
"Key signal:", "Caveat on X:", "Decision handoff:", "Plain-language takeaway:". The
writing should carry the meaning without labelling it.

**The technical/jargon distinction** — being technical is fine and expected. The goal
is not to simplify the analysis but to explain it. A sentence like "investors are
paying about 160 times Tesla's expected annual earnings, compared to about 6 times for
a typical auto company" is technical and clear. A sentence like "forward P/E is 160x
vs. the auto sector median of 6.2x" says the same thing to a narrower audience. Flag
the second kind; do not flag the first.

## Required Output

Return results in this structure:

1. `Execution Results`
- pass/fail for ruff, marimo check, test_notebooks
- failing notebook list with error summaries

2. `Language Findings (by severity)`
- prioritized findings first
- each finding includes:
  - severity: `High | Medium | Low`
  - category: Unexplained Jargon | Unexpanded Abbreviation | Em-dash Overuse | Announcing Label | Other
  - the exact quoted text that has the problem
  - file reference with line number
  - suggested rewrite

3. `Communication Findings (by severity)`
- each finding includes:
  - severity: `High | Medium | Low`
  - dimension (from rubric above)
  - brief impact statement
  - file reference with line number(s)

4. `Notebook Scorecard`
- one row per notebook with 5-dimension scores and total (`/10`)

5. `Top Fixes`
- top 5 fixes across all findings
- each fix written as a concrete edit instruction: quote the problem text, state
  what to change, and provide a rewritten version

## Constraints

- Do not edit files unless I explicitly ask for fixes.
- Quote the exact text that has the problem — do not paraphrase.
- Keep findings evidence-based; do not infer claims without citing notebook lines.
- If execution is blocked (missing data/network), report as blocked with the exact command and error.
