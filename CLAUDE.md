# CLAUDE.md - Where AI Capital Lands

**Last updated:** 2026-02-14
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

See `research-framework.md` for the full framework, case study plans, and references.

## Current Phase

**Phase 1:** Tightening CS-1 (transformer case study) and establishing the analytical
framework for publication.
- Sprint 1 of the shakestzd life strategy system (Feb 9 - May 3, 2026)

## Case Studies

| ID | Focus | Status |
| :--- | :--- | :--- |
| DD-002 | Grid modernization: what's getting built, who benefits, feedback loops | Active — 3 notebooks complete |
| CS-1 | Transformer manufacturing and grid equipment | Archived (not rigorous enough) |
| CS-next | Hyperscaler labor/capital substitution — layoffs funding AI capex | Scoping |
| CS-4 | Material supply chains (GOES, copper, critical minerals) | Not started |

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
- Verify dates with `date` command before writing timestamps
- Do not auto-commit unless explicitly asked

### Code Style
- Use `ruff` for linting and formatting
- Use `mypy` for type checking
- Follow existing patterns in `src/`
- Tests go in `tests/` using `pytest`

---

## Project Structure

```
Systems/
├── CLAUDE.md                    # This file
├── pyproject.toml               # Project config and dependencies (uv managed)
├── README.md                    # Project overview
├── research-framework.md        # Analytical framework, case studies, references
├── data-sources.md              # Catalog of data sources
│
├── src/                         # Python source code
│   ├── __init__.py
│   ├── notebook.py              # Shared notebook setup (style, paths, save_fig)
│   ├── plotting.py              # Reusable plotting functions
│   ├── dynamics/                # Systems dynamics models (PySD / Vensim .mdl)
│   └── data/                    # Data pipelines and loaders
│
├── notebooks/                   # Marimo notebooks (.py files)
│   ├── dd002_grid_modernization/# Active: AI capital and grid modernization
│   │   ├── 01_whats_getting_built.py
│   │   ├── 02_who_benefits.py
│   │   └── 03_feedback_architecture.py
│   ├── _archive/                # Archived notebooks (not publication-ready)
│   │   └── dd001_learning_curves/
│   ├── images/                  # Generated figures (embedded in prose via mo.image)
│   └── shakes.mplstyle          # Custom matplotlib style
│
├── research/                    # Research tracking
│   └── deep_dives.csv           # Case study pipeline
│
├── data/                        # Not committed to git
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── tests/                       # pytest tests
│
└── .claude/                     # Claude Code config
    └── agents/                  # Specialized sub-agents
        ├── researcher.md
        ├── critic.md
        ├── writer.md
        └── fact-checker.md
```

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

The agents are designed to run in sequence, each building on the previous:

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

### How to Delegate

**Research a topic:**
> "Use the researcher agent to find primary data on U.S. transformer imports and
> domestic manufacturing capacity."

**Review a draft:**
> "Use the critic agent to review notebook 02 for logical gaps and missing evidence."

**Polish prose:**
> "Use the writer agent to improve the narrative structure and chart titles in the
> generation mix analysis."

**Pre-publication check:**
> "Use the fact-checker agent to verify all claims in CS-1 before publishing."

**Parallel delegation** works when agents don't depend on each other's output:
- researcher + critic can run simultaneously on different content
- writer and fact-checker should run sequentially (writer first, then fact-checker)

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

## Key Dependencies

- **PySD** -- Systems dynamics simulation in Python
- **Marimo** -- Reactive notebooks (replaces Jupyter)
- **fredapi** -- FRED economic data API
- **yfinance** -- Financial data
- **pandas / matplotlib / numpy** -- Data analysis and visualization

---

## Constraints

- Zero budget -- all tools and data sources must be freely accessible
- Learning project -- building analytical capability alongside the analysis
- Publication-oriented -- every case study should be writable as a standalone piece
- Aligned with Sprint 1 goals in shakestzd life strategy system
