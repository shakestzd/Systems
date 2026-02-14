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
| CS-1 | Transformer manufacturing and grid equipment | Draft complete |
| CS-2 | Power generation mix and asset lock-in | Not started |
| CS-3 | Grid interconnection and transmission | Not started |
| CS-4 | Material supply chains (GOES, copper, critical minerals) | Not started |
| CS-5 | Labor and workforce | Not started |

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
│   ├── dd001_learning_curves/   # CS-1: Transformer manufacturing
│   │   ├── 01_investigation.py
│   │   └── 02_feedback_architecture.py
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
```

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
