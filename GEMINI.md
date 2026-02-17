# Gemini Project Context: Systems Dynamics Research

This `GEMINI.md` file provides context and instructions for AI agents working on the "Systems" project.

## Project Overview

**Purpose:** This research project models the durable commodity and infrastructure impacts of AI capital flows. It aims to separate AI hype from structural shifts in demand for energy, water, minerals, and physical infrastructure.

**Core Research Question:** Which commodity markets and infrastructure systems being catalyzed by AI investment will sustain demand growth independent of AI's commercial success?

**Methodology:**
The project employs a hybrid quantitative approach:
1.  **Systems Dynamics Modeling (PySD):** Maps causal feedback loops between AI CapEx and commodity/infrastructure demand.
2.  **Bayesian Inference (PyMC):** Quantifies uncertainty in model parameters (e.g., AI-specific data center growth).
3.  **Markov Regime Switching (statsmodels):** Models different AI adoption scenarios (Boom, Plateau, Bust) and their transitions.

## Tech Stack

*   **Language:** Python (>=3.11)
*   **Dependency Management:** `uv`
*   **Notebooks:** `marimo` (Pure Python `.py` files, **NOT** Jupyter `.ipynb`)
*   **Linting & Formatting:** `ruff`
*   **Type Checking:** `mypy`
*   **Testing:** `pytest`
*   **Key Libraries:** `pysd`, `pymc`, `arviz`, `statsmodels`, `fredapi`, `yfinance`, `pandas`, `numpy`, `scipy`.

## Project Structure

```
Systems/
├── src/                         # Core Python source code
│   ├── dynamics/                # Systems dynamics models (PySD)
│   ├── bayesian/                # Bayesian inference logic (PyMC)
│   ├── regime/                  # Markov regime switching logic
│   └── data/                    # Data pipelines and loaders
├── notebooks/                   # Marimo notebooks (pure .py files)
│   └── (exploration, analysis)
├── tests/                       # Unit and integration tests (pytest)
├── data/                        # Data storage (git-ignored)
│   ├── raw/                     # Original downloads
│   ├── processed/               # Cleaned data
│   └── external/                # Third-party datasets
├── CLAUDE.md                    # User's project guide (reference this!)
├── research-framework.md        # Detailed methodology documentation
├── pyproject.toml               # Configuration and dependencies
└── uv.lock                      # Dependency lock file
```

## Development Workflow & Conventions

### 1. Dependency Management
*   **Always use `uv`** for all Python operations.
*   **Install:** `uv sync` (installs dependencies from `uv.lock`)
*   **Add Package:** `uv add <package>`
*   **Run Script:** `uv run python script.py`

### 2. Notebooks
*   **Strictly use Marimo.** Do not create `.ipynb` files.
*   **Create/Edit:** `uv run marimo edit notebooks/my_analysis.py`
*   **Run:** `uv run marimo run notebooks/my_analysis.py`
*   Marimo notebooks are stored as standard Python scripts, making them git-friendly.

### 3. Code Quality
*   **Linting:** `uv run ruff check .`
*   **Formatting:** `uv run ruff format .`
*   **Type Checking:** `uv run mypy .`
*   **Testing:** `uv run pytest`

### 4. Data Handling
*   Data files in `data/` are **not committed**.
*   Use absolute paths or robust relative path handling in code to locate data.
*   Refer to `data-sources.md` for data origin information.

## Key Commands Cheat Sheet

| Task | Command |
|---|---|
| **Install Dependencies** | `uv sync` |
| **Run Tests** | `uv run pytest` |
| **Start Marimo Editor** | `uv run marimo edit notebooks/<name>.py` |
| **Run Python Script** | `uv run python src/<script>.py` |
| **Lint Code** | `uv run ruff check .` |
| **Format Code** | `uv run ruff format .` |
| **Type Check** | `uv run mypy .` |

## Important Rules for AI Agents

1.  **Check `CLAUDE.md`:** This file contains the user's latest specific instructions and context. It is the source of truth for current sprint goals.
2.  **No Jupyter:** If asked to create a notebook, create a Marimo script (`.py`) in `notebooks/`.
3.  **Use `uv`:** Never suggest `pip install` or `python script.py`. Always prefix with `uv run` or use `uv` commands.
4.  **Read First:** Before editing code, read the relevant files in `src/` and `notebooks/` to understand existing patterns.
