# CLAUDE.md - Where AI Capital Lands

**Owner:** Thandolwethu Zwelakhe Dlamini (Shakes)

---

## What This Project Is

An investigative research project analyzing how technology capital flows land in the
physical economy — covering AI infrastructure, energy transition, climate finance, and
their intersections — and what path dependencies they create for workers, communities,
ratepayers, and the physical systems they depend on.

**Core questions:**
1. Where does capital convert from financial commitment to physical asset?
2. How durable is that infrastructure, and what does it lock in?
3. Who benefits and who bears the costs?
4. How do public policy decisions amplify or distort these outcomes?
5. Where are the feedback loops and leverage points?

The analytical framework combines:
1. **Capital flow mapping** — Trace where technology capital converts to physical assets
2. **Durability taxonomy** — Classify investments as structural, policy-dependent,
   or demand-thesis-dependent
3. **Regulatory interaction analysis** — How trade, energy, utility, and industrial
   policy shapes where capital lands
4. **People and distribution** — Workers, communities, ratepayers, decision-makers
5. **Systems dynamics modeling** (PySD) — Map feedback architecture and leverage points

See `research-framework.md` for the full framework and references.

## Publication Architecture

See `FRAMING.md` for the full editorial architecture. Short version:

**Scope:** Technology capital in the physical economy — AI infrastructure, energy
transition, climate finance, materials. The analytical arc is COMMIT → CONVERT → LAND → DISTRIBUTE.
Current focus: AI (DD-001–004). Framework portable to future case studies.

**Position:** Starts where Politano ends. Politano shows the scale; we show what
the capital actually buys, what it locks in, and who ends up paying.

Before writing any new section: confirm the content answers the governing question
for that deep dive (see `FRAMING.md`). Before titling a piece: follow the title
conventions in `FRAMING.md`.

## Project Status (auto-generated)

@PROJECT_STATUS.md

Case studies, active notebooks, source modules, dependencies, and project structure
are all generated from the filesystem and `research/deep_dives.csv` by running:
```
uv run python scripts/sync_project_status.py
```

**To add a new case study:** Add a row to `research/deep_dives.csv`, create the
notebook directory, then run the sync script. Do NOT edit PROJECT_STATUS.md by hand.

---

## Code Principles

### DRY / Single Source of Truth
- **Every configuration, constant, and shared value must have exactly one canonical location.**
  If a value appears in more than one place, extract it to a shared module.
- `src/plotting.py` — compatibility shim; re-exports everything from the `flowmpl` package
  - Canonical source is `flowmpl` (PyPI: `pip install flowmpl`, GitHub: Shakes-tzd/flowmpl)
  - `COLORS` (semantic roles), `FUEL_COLORS`, `COMPANY_COLORS`, `CATEGORICAL` (palettes)
  - `CONTEXT` (SWD gray for non-focus elements), `FONTS`, `FIGSIZE`, `BAR_DEFAULTS`
  - `focus_colors()` (SWD gray+accent pattern), `legend_below()`, `annotate_point()`
  - Company colors are redistributed across hue bands for chart legibility (not raw brand blues)
  - To change or extend plotting behavior, edit `flowmpl` — not `src/plotting.py`
- `src/notebook.py:setup()` — single entry point for notebook configuration
- `research/deep_dives.csv` — single source for case study metadata
- `scripts/sync_project_status.py` — generates PROJECT_STATUS.md from the above
- When adding new shared configuration, put it in `src/` and import it — never
  hardcode values in notebook cells

### Separation of Concerns
- **Data pipelines** (`src/data/`) — fetch, clean, store data; no visualization
- **Plotting** (`src/plotting.py`) — shim to `flowmpl`; do not add logic here directly
- **Notebook setup** (`src/notebook.py`) — style, paths, save_fig; no data logic
- **Dynamics models** (`src/dynamics/`) — PySD model wrappers; no visualization
- **Notebooks** (`notebooks/`) — analysis narrative, call src/ functions, display results

### Reuse and Parameterization
- Extract repeated patterns into `src/` functions with clear parameters
- Use consistent color palettes across related charts (define once, import everywhere)
- Prefer function parameters over hardcoded values
- If you copy-paste code between cells, it belongs in `src/`

---

## Post-Work Hygiene (Mandatory)

After any major work session — new feature, notebook changes, Observable article,
bug fix, refactor — **always**:

1. **Commit all relevant changes** — stage by area, write a clear commit message
2. **Push to remote** — don't leave work only local
3. **Clean the project directory** — delete debug artifacts, move stray files to
   their correct locations, verify `.gitignore` covers all build outputs and temp files
4. **Verify with `git status`** — no untracked files that should be committed or ignored

Common cleanup targets:
- `debug_*.png` — delete (already gitignored; still clean up)
- `_site/` — gitignored build output; never commit
- `observable/dist/` — gitignored build output; never commit
- Stray `.py` scripts at project root — move to `scripts/` or delete if experimental
- Research extracts and CSVs — move to `research/` not project root

---

## Development Rules

### Python
- **ALWAYS use `uv`** for all Python operations
  - `uv run python script.py` (not `python script.py`)
  - `uv run pytest` (not `pytest`)
  - `uv pip install package` (not `pip install`)
  - `uv run marimo edit notebook.py` (not `marimo edit`)
- Project uses `pyproject.toml` for dependency management

### Notebooks: Marimo, NOT Jupyter
- **Use Marimo for all notebooks** -- reactive, git-friendly, pure Python
- Notebook files are `.py` files in `notebooks/`, not `.ipynb`
- Create notebooks with: `uv run marimo edit notebooks/name.py`
- Run notebooks with: `uv run marimo run notebooks/name.py`
- Marimo notebooks are valid Python scripts -- they diff cleanly in git
- **Do NOT create .ipynb files.** If you see Jupyter references, migrate to Marimo.

### General
- Read files before editing them
- Use absolute paths
- Do not auto-commit unless explicitly asked

### Policy Currency

Technology, energy, and climate policy are in active flux. A claim accurate in 2023
may be wrong by mid-2025. **Before writing any policy claim, use the `tzd-labs:researcher` agent
to verify current status.**

Rules:
- Cite specific statutory provisions by section number (e.g., §45Y, §45X), not just
  program names — names change, section numbers are stable
- Date every policy reference: "as of [month year]"
- Note when a policy is under legal challenge or pending rulemaking
- Flag when a policy reference is more than 6 months old and may need re-verification

**Reliable primary sources (zero-budget, publicly accessible):**
- [Congress.gov](https://congress.gov) — statutory text and bill status
- [FERC.gov](https://www.ferc.gov) — orders, dockets, interconnection queue
- [EIA.gov](https://www.eia.gov) — energy data, generation capacity, fuel mix
- [NERC.org](https://www.nerc.com) — reliability assessments, demand forecasts
- [LBNL Electricity Markets & Policy](https://emp.lbl.gov) — grid and clean energy research
- State PUC websites — utility rate cases and IRP filings
- [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar) — company 10-K/10-Q filings

**Known policy state as of February 2026 (verify before citing):**
- One Big Beautiful Act (H.R.1, signed July 4, 2025): eliminated 30D consumer EV
  credits; terminated 25C/25D residential credits by 12/31/2025; set 12/31/2031
  sunset for 45Y/48E (utility-scale wind/solar); preserved 45X (battery manufacturing),
  48C (advanced manufacturing), 45Q (carbon capture), 45V (hydrogen), 45Z (clean fuels)
- US Paris Agreement withdrawal: initiated January 20, 2025; effective January 2026
- FERC Order 2023 (interconnection reform): in effect, ISOs/RTOs compliant
- FERC Order 1920 (transmission planning): vacated by Fifth Circuit, late 2024

### Code Style
- Use `ruff` for linting and formatting
- Use `mypy` for type checking
- Follow existing patterns in `src/`
- Tests go in `tests/` using `pytest`

### Notebook Theme

All notebooks share a consistent typography that matches the published site. The theme
files live in `src/notebook_theme/` and must be wired into every new notebook via
`marimo.App()`.

**Required `marimo.App()` pattern for every notebook:**

```python
import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",                                        # omit if not needed
    app_title="DD-XXX Notebook Title",                    # human-readable title
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)
```

**Critical rules:**
- Paths MUST be string literals — marimo parses `App()` kwargs from the AST and does
  NOT execute Python expressions at parse time. `css_file=str(Path(...))` will NOT work.
- The relative path `../../src/notebook_theme/` is correct for any notebook at depth
  `notebooks/ddXXX/notebook.py`. Do not use absolute paths.
- Both files are required: `custom.css` sets the three stable CSS variables
  (`--marimo-text-font`, `--marimo-monospace-font`, `--marimo-heading-font`);
  `head.html` injects the Google Fonts `<link>` tags.

**What the theme sets:**
- `--marimo-text-font` → DM Sans (body text)
- `--marimo-monospace-font` → DM Mono (code, IDs)
- `--marimo-heading-font` → Cormorant Garamond (headings)

**Verification after adding theme to a notebook:**
```bash
bash scripts/test_notebooks.sh notebooks/ddXXX/notebook.py
# Then grep for font fingerprint in exported HTML:
grep -c "Cormorant\|DM Mono\|marimo-text-font" _site/ddXXX/notebook.html
# Should return > 0
```

**Do NOT modify `src/notebook_theme/` files** to change fonts for a single notebook.
Those files are shared across all notebooks. Typographic changes belong in a project-wide
update that touches both theme files and `build.py` simultaneously.

### Notebook Testing
- **Always validate notebooks after changes** to `src/` or notebook files
- Test all active notebooks headlessly:
  ```
  bash scripts/test_notebooks.sh
  ```
- Test a single notebook:
  ```
  bash scripts/test_notebooks.sh notebooks/dd001_capital_reality/01_markets_and_money.py
  ```
- Structural check (fast, no execution): `uv run marimo check notebooks/**/*.py`
- Lint check: `uv run ruff check src/ notebooks/`
- The test script uses `marimo export html` which executes every cell and exits
  non-zero on failure. Add new notebooks to the `NOTEBOOKS` array in the script.
- **Run `bash scripts/test_notebooks.sh` before committing notebook or `src/` changes.**

### Event Annotations

Use `mark_events()` from `src.data.events` for structural inflection points on any
time-series chart where policy or market context matters:

```python
from src.data.events import mark_events
mark_events(ax, categories=["policy", "announcement"])
```

- Event catalog: `src/data/events.py` — add new events there, not in notebook cells
- Categories: `"policy"`, `"market"`, `"announcement"`, `"regulatory"`, `"energy"`
- Call **after** setting axis limits so only events within the visible range are drawn
- Do NOT hardcode event dates or labels inside notebook cells

### Chart Review (Storytelling with Data)

Every chart must pass this checklist before committing. Based on Cole Nussbaumer
Knaflic's *Storytelling with Data* methodology.

**Before creating a chart — answer these:**
1. What is the ONE insight this chart communicates?
2. What action should the reader take after seeing it?
3. Can you state the insight as a sentence? (That sentence is your H1 title.)

**Color strategy (gray + accent):**
- Start with everything in `CONTEXT` gray
- Add color ONLY to the element that carries the story
- Use `focus_colors()` to apply this pattern to any color mapping
- Never use color decoratively — every color must encode meaning
- Company charts: use `COMPANY_COLORS` (redistributed across hue bands)
- Semantic meaning: use `COLORS["positive"]` / `COLORS["negative"]` ONLY for
  genuinely good/bad values — NOT for arbitrary categories

**Declutter checklist:**
- [ ] No gridlines (or very light, opt-in via `ax.grid(True, ...)`)
- [ ] No chart title (use marimo markdown H1 above the chart instead)
- [ ] Direct labels on data where feasible (reduce legend dependency)
- [ ] No 3D effects, ever
- [ ] Sorted meaningfully (by value, not alphabetically)
- [ ] White background, no borders

**Post-creation validation:**
- [ ] `add_source(fig, "Source: ...")` on every published chart
- [ ] `add_brand_mark(fig, logo_path=...)` applied (requires `src/assets/tzdlabs_mark.png`)
- [ ] `add_rule(ax)` on time-series charts
- [ ] `mark_events(ax, categories=[...])` where temporal context matters
- [ ] Can someone understand the main point in 5 seconds?
- [ ] Is there anything you can remove without losing meaning?
- [ ] Does every visual element serve the story?
- [ ] Are colors distinguishable? (check for adjacent similar hues)
- [ ] Does the insight title match what the chart actually shows?

> **MANDATORY — READ THE IMAGE AFTER EVERY CHART GENERATION.**
> After every `save_fig(...)` call and successful notebook test, use the `Read` tool to
> open the saved `.png` and visually inspect it before reporting success to the user.
> Check specifically: text overflow, label clipping, overlapping elements, legend
> placement, and axis limits. Do NOT report a chart as complete until you have read
> and verified the image. This is non-negotiable — the test suite only checks that
> cells execute without error; it does not check visual correctness.

**Visual review workflow (Marimo notebooks):**
1. Regenerate charts: `bash scripts/test_notebooks.sh`
2. **Read every saved image** using the `Read` tool — verify text fits, nothing clips
3. Open all images for side-by-side review: `open notebooks/images/dd00*.png`
4. Check for: color consistency, font sizing, visual family across charts
5. Verify no hex colors in notebook code: `rg '#[0-9a-fA-F]{6}' notebooks/`

**Observable article cross-viewport review (MANDATORY after any chart JS change):**

After every change to `observable/src/js/charts/*.js` or `observable/src/js/animate.js`,
run the Playwright review script and read all output screenshots before committing:

```bash
# Dev server must be running: cd observable && npm run dev
node scripts/review_charts.cjs http://localhost:3000/dd001 /tmp/chart_review

# Then read every screenshot with the Read tool:
# /tmp/chart_review/mobile_chart_0.png  (and tablet_, desktop_ variants)
```

Viewports checked: mobile (390×844), tablet (768×1024), desktop (1200×800).

Common mobile issues to check:
- X-axis label collision (labels too close at narrow widths — use `isMobile` guard to reduce ticks)
- SVG text overflow past viewBox edge (shorten labels or use mobile-specific text)
- Callout position: overlay callouts auto-promote to "above" on mobile (width < 500px) when
  `callout !== "none"` — verify prose callout appears above chart, not clipped inside it

### Writing Style

This project is investigative, not academic. The voice is a curious person working through
a question in public. Write as if explaining to a smart colleague who is not a specialist.

**What AI-generated prose sounds like (avoid all of these):**

*Structural tells:*
- Em-dashes used to splice clauses mid-sentence: "The data shows X — which means Y"
- Three-item lists when prose flows better: "X, Y, and Z" repeated throughout
- Overly parallel sentence structure across an entire section
- Bullet points for things that should just be sentences
- Topic sentences that announce themselves: "This section will cover X, Y, and Z"

*Lexical tells — these words flag AI authorship:*
- "delve into", "dive into"
- "it is worth noting", "notably", "importantly" (as throat-clearing openers)
- "moreover", "furthermore", "additionally" (as sentence starters)
- "leverage" as a verb (in non-financial contexts)
- "robust", "comprehensive", "holistic" (vague intensifiers)
- "landscape", "ecosystem", "paradigm" (overused abstractions)
- "cutting-edge", "state-of-the-art"
- "in conclusion", "to summarize"
- "this demonstrates", "this shows", "this indicates" (as repeated openers)

*Voice tells:*
- Hedging everything: "somewhat", "fairly", "quite", "rather"
- Passive voice as the default construction
- Over-explaining what is already obvious from context

**What to do instead:**
- Use em-dashes sparingly, only as genuine parenthetical asides (one per paragraph max)
- Prefer short sentences when making a key point
- State numbers and claims directly without pre-signposting them
- Let data speak; do not over-narrate the chart before the reader sees it
- Use active constructions: "AI capex converted into..." not "was converted by..."
- When in doubt, cut the sentence. Most prose is 20% longer than it needs to be.

**Check before committing prose:**
- [ ] Search for ` — ` (space-dash-dash-space): flag any sentence with more than one
- [ ] Search for "worth noting", "notably", "moreover", "furthermore", "delve"
- [ ] Read one paragraph aloud. If it sounds like a presentation, rewrite it.

---

## Agent Workflow

Five specialized agents handle distinct phases of the research-to-publication pipeline.
Delegate to them using the Task tool with `subagent_type`.

**Plugin location:** All agents and skills are defined in the `tzd-labs` Claude Code
plugin at `/Users/shakes/DevProjects/tzd-labs`. Agent files live in
`/Users/shakes/DevProjects/tzd-labs/agents/`. Skills live in
`/Users/shakes/DevProjects/tzd-labs/skills/`. The plugin manifest is at
`/Users/shakes/DevProjects/tzd-labs/.claude-plugin/plugin.json`.

**CRITICAL: All project agents require the `tzd-labs:` namespace prefix.**
Always use the full `subagent_type` — never the bare name:

| Correct | Wrong |
| :--- | :--- |
| `tzd-labs:researcher` | `researcher` |
| `tzd-labs:critic` | `critic` |
| `tzd-labs:notebook-qa` | `notebook-qa` |
| `tzd-labs:writer` | `writer` |
| `tzd-labs:fact-checker` | `fact-checker` |

### Agents

| subagent_type | Color | Purpose |
| :--- | :--- | :--- |
| **tzd-labs:researcher** | cyan | Finds and validates primary data sources (government databases, academic repos, company filings). Actively searches for contradictory evidence. Zero-budget aware. |
| **tzd-labs:critic** | red | Rigorous intellectual review. Evaluates logical structure, evidence quality, structural omissions, and reference strength. Does not soften criticism. |
| **tzd-labs:notebook-qa** | blue | Data integrity auditor. Verifies every number in prose against the database, identifies hardcoded values that should be data-driven, checks internal consistency between chart code and captions. |
| **tzd-labs:writer** | green | Transforms draft analysis into accessible, rigorous narrative. Applies storytelling principles (inverted pyramid, insight-driven chart titles, Tufte, Knaflic). |
| **tzd-labs:fact-checker** | yellow | Final gate before publication. Verifies every number, citation, date, and entity. Flags unsourced claims and stale data. |
| **tzd-labs:observable-converter** | blue | Converts Marimo charts to Observable Framework interactive articles. Researches D3 visualization patterns, proposes novel chart types, handles geographic maps. See `observable/CONVERSION_GUIDE.md`. |

### Publication Pipeline

```
1. RESEARCH    (tzd-labs:researcher)    Find primary data, validate existing references
       ↓
2. DRAFT       (you)                    Write the analysis in a Marimo notebook
       ↓
3. REVIEW      (tzd-labs:critic ∥ tzd-labs:notebook-qa)   Run IN PARALLEL
       ↓
4. REVISE      (you)                    Address findings from both reviews
       ↓
5. POLISH      (tzd-labs:writer)        Rewrite prose for clarity, structure
       ↓
6. VERIFY      (tzd-labs:fact-checker)  Check every claim against its source
       ↓
7. CONVERT     (tzd-labs:observable-converter)  Port charts to Observable interactive article
       ↓
8. DEPLOY      bash scripts/deploy.sh           Build + push to GitHub Pages
```

Steps 3-6 may iterate. The critic and fact-checker may surface issues that require
returning to the researcher for additional data.

### Notebook Review Process (Step 3 Detail)

When reviewing a notebook, **always launch both agents in parallel**:

```
Task(tzd-labs:critic):      "Review notebooks/ddXXX/.../notebook.py for logical gaps and evidence quality"
Task(tzd-labs:notebook-qa): "Run data QA on notebooks/ddXXX/.../notebook.py"
```

The **critic** produces: logical gaps, missing evidence, structural omissions, weak
references, section ratings, priority fixes.

The **notebook-qa** agent produces: numerical verification table, hardcoded value
inventory, internal consistency checks, missing caveats, data-grounding recommendations.

**After receiving both reports, the revision checklist is:**

1. **Fix numerical errors** — Correct any values that don't match the database
2. **Data-ground all values** — Create/update a `stats` cell that computes all key
   summary values from data. Replace hardcoded numbers in `mo.md()` cells with
   f-string interpolation from `stats`. Pattern:
   ```python
   @app.cell
   def _(capex_annual, guidance_2025, mkt_cap):
       stats = {
           "capex_2024": annual[annual["year"] == 2024]["capex_bn"].sum(),
           # ... all data-derived values used in prose ...
       }
       return (stats,)
   ```
3. **Add missing citations** — Replace vague references with specific sources
   (report name, year, table/page number)
4. **Add methodology caveats** — Disclose fiscal year misalignment, definition
   scope, geographic scope, estimate uncertainty
5. **Address logical gaps** — Fix reasoning issues identified by the critic
6. **Validate** — `uv run ruff check` + `bash scripts/test_notebooks.sh` +
   visual inspection of regenerated charts

### How to Delegate

**Full notebook review (most common):**
> "Run the `tzd-labs:critic` and `tzd-labs:notebook-qa` agents in parallel on notebooks/dd001.../01_capex.py"

**Data-only check (after data refresh):**
> "Use the `tzd-labs:notebook-qa` agent to verify all prose claims in DD-001 against the updated data"

**Research a topic:**
> "Use the `tzd-labs:researcher` agent to find primary data on U.S. transformer imports"

**Polish prose:**
> "Use the `tzd-labs:writer` agent to improve the narrative structure in the generation mix analysis"

**Pre-publication check:**
> "Use the `tzd-labs:fact-checker` agent to verify all claims in CS-1 before publishing"

**Parallel delegation** works when agents don't depend on each other's output:
- `tzd-labs:critic` + `tzd-labs:notebook-qa` should run simultaneously (they review different dimensions)
- `tzd-labs:researcher` + `tzd-labs:critic` can run simultaneously on different content
- `tzd-labs:writer` and `tzd-labs:fact-checker` should run sequentially (writer first, then fact-checker)

### Agent Design Principles

- Each agent has a single, clear responsibility — no overlap
- Agents read project context (`CLAUDE.md`, `research-framework.md`, notebooks) before acting
- The critic does not hedge or soften — it identifies what does not hold up
- The notebook-qa agent verifies data, not arguments — it queries the database
- The writer preserves analytical substance while improving prose
- The fact-checker does not evaluate arguments — only verifiable facts
- All agents respect the zero-budget constraint (flag paywalls, suggest free alternatives)

---

## Key Resources

| Resource | Purpose |
|----------|---------|
| [MIT 15.871](https://ocw.mit.edu/courses/15-871-introduction-to-system-dynamics-fall-2013/) | Systems dynamics foundations |
| [MIT 15.872](https://ocw.mit.edu/courses/15-872-system-dynamics-ii-fall-2013/) | Advanced SD (boom-bust cycles) |
| [PySD docs](https://pysd.readthedocs.io/) | Python systems dynamics library |
| [Vensim PLE](https://vensim.com/free-downloads/) | GUI-based SD modeling (free) |
| Sterman's *Business Dynamics* | SD reference text |
| Meadows' *Thinking in Systems* | Conceptual SD primer |

---

## Constraints

- Zero budget -- all tools and data sources must be freely accessible
- Learning project -- building analytical capability alongside the analysis
- Publication-oriented -- every case study should be writable as a standalone piece
- Aligned with Sprint 1 goals in shakestzd life strategy system
