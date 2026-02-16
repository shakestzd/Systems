# CLAUDE.md - Where AI Capital Lands

**Owner:** Thandolwethu Zwelakhe Dlamini (Shakes)

---

## What This Project Is

A research project analyzing how AI capital expenditure ($200B+/year) converts into
physical infrastructure and creates durable path dependencies in supply chains, labor
markets, trade patterns, and grid topology.

**Core question:** Where does AI capex land in the physical economy, what does it
lock in, and how do current regulatory decisions amplify or distort those outcomes?

The analytical framework combines:
1. **Capital flow mapping** — Trace where AI capex converts to physical assets
2. **Durability taxonomy** — Classify investments as structural, policy-dependent,
   or demand-thesis-dependent
3. **Regulatory interaction analysis** — How trade, energy, and utility policy shapes
   where capital lands
4. **Systems dynamics modeling** (PySD) — Map feedback architecture and leverage points

See `research-framework.md` for the full framework and references.

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
- `src/plotting.py` — dataviz design system (colors, fonts, sizing, chart helpers)
  - `COLORS` (semantic roles), `FUEL_COLORS`, `COMPANY_COLORS`, `CATEGORICAL` (palettes)
  - `FONTS` (text hierarchy), `FIGSIZE` (figure presets), `BAR_DEFAULTS`, `SCATTER_DEFAULTS`
  - `legend_below()`, `annotate_point()`, `reference_line()`, lookup helpers
- `src/notebook.py:setup()` — single entry point for notebook configuration
- `research/deep_dives.csv` — single source for case study metadata
- `scripts/sync_project_status.py` — generates PROJECT_STATUS.md from the above
- When adding new shared configuration, put it in `src/` and import it — never
  hardcode values in notebook cells

### Separation of Concerns
- **Data pipelines** (`src/data/`) — fetch, clean, store data; no visualization
- **Plotting** (`src/plotting.py`) — reusable chart functions; return Figure objects
- **Notebook setup** (`src/notebook.py`) — style, paths, save_fig; no data logic
- **Dynamics models** (`src/dynamics/`) — PySD model wrappers; no visualization
- **Notebooks** (`notebooks/`) — analysis narrative, call src/ functions, display results

### Reuse and Parameterization
- Extract repeated patterns into `src/` functions with clear parameters
- Use consistent color palettes across related charts (define once, import everywhere)
- Prefer function parameters over hardcoded values
- If you copy-paste code between cells, it belongs in `src/`

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

### Code Style
- Use `ruff` for linting and formatting
- Use `mypy` for type checking
- Follow existing patterns in `src/`
- Tests go in `tests/` using `pytest`

### Notebook Testing
- **Always validate notebooks after changes** to `src/` or notebook files
- Test all active notebooks headlessly:
  ```
  bash scripts/test_notebooks.sh
  ```
- Test a single notebook:
  ```
  bash scripts/test_notebooks.sh notebooks/dd001_capital_reality/01_capex_vs_reality.py
  ```
- Structural check (fast, no execution): `uv run marimo check notebooks/**/*.py`
- Lint check: `uv run ruff check src/ notebooks/`
- The test script uses `marimo export html` which executes every cell and exits
  non-zero on failure. Add new notebooks to the `NOTEBOOKS` array in the script.
- **Run `bash scripts/test_notebooks.sh` before committing notebook or `src/` changes.**

---

## Agent Workflow

Four specialized agents handle distinct phases of the research-to-publication pipeline.
Delegate to them using the Task tool with `subagent_type` matching the agent name.

### Agents

| Agent | Color | Purpose |
| :--- | :--- | :--- |
| **researcher** | cyan | Finds and validates primary data sources (government databases, academic repos, company filings). Actively searches for contradictory evidence. Zero-budget aware. |
| **critic** | red | Rigorous intellectual review. Evaluates logical structure, evidence quality, structural omissions, and reference strength. Does not soften criticism. |
| **writer** | green | Transforms draft analysis into accessible, rigorous narrative. Applies storytelling principles (inverted pyramid, insight-driven chart titles, Tufte, Knaflic). |
| **fact-checker** | yellow | Final gate before publication. Verifies every number, citation, date, and entity. Flags unsourced claims and stale data. |

### Publication Pipeline

```
1. RESEARCH    (researcher)  Find primary data, validate existing references
       ↓
2. DRAFT       (you)         Write the analysis in a Marimo notebook
       ↓
3. CRITIQUE    (critic)      Identify logical gaps, weak evidence, omissions
       ↓
4. REVISE      (you)         Address the critic's findings
       ↓
5. POLISH      (writer)      Rewrite prose for clarity, fix chart titles, structure
       ↓
6. VERIFY      (fact-checker) Check every claim against its source
       ↓
7. PUBLISH
```

Steps 3-6 may iterate. The critic and fact-checker may surface issues that require
returning to the researcher for additional data.

### Agent Design Principles

- Each agent has a single, clear responsibility — no overlap
- Agents read project context (`CLAUDE.md`, `research-framework.md`, notebooks) before acting
- The critic does not hedge or soften — it identifies what does not hold up
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
