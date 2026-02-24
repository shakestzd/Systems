# Where AI Capital Lands

**Live site:** https://shakes-tzd.github.io/Systems/

## Core Question

AI companies are deploying over $200 billion per year in capital expenditure. That
capital converts into physical infrastructure — power plants, transmission lines,
transformer factories, data centers, semiconductor fabs. Unlike the capital itself,
which can be written down in a quarterly earnings report, the infrastructure is
durable. It reshapes supply chains, labor markets, trade patterns, and grid topology
for decades.

**Where does AI capex land in the physical economy, what does it lock in, and how
do current regulatory decisions amplify or distort those outcomes?**

## Approach

This project traces AI capital flows through the physical supply chain and analyzes
the infrastructure path dependencies they create. The analytical framework combines:

1. **Capital flow mapping** — Trace where AI capex converts from financial
   commitment to physical asset
2. **Durability taxonomy** — Classify investments as structural (persists regardless
   of AI outcome), policy-dependent (tied to a regulatory regime), or
   demand-thesis-dependent (requires continued AI growth)
3. **Regulatory interaction analysis** — How trade policy, energy policy, FERC
   regulation, and industrial policy shape where capital lands and what it locks in
4. **Systems dynamics modeling** — Map feedback architecture and identify leverage
   points in each supply chain node

## Case Studies

| ID | Focus | Status |
| :--- | :--- | :--- |
| **DD-001** | AI Valuations vs Physical Infrastructure Reality | Active |
| **DD-002** | AI Capital and Grid Modernization | Active |
| **DD-003** | AI Capital Flows and Labor Impact | Active |
| **DD-004** | AI Capital and Who Pays for the Grid | Scoping |

## Repository Contents

- `research-framework.md` — Analytical framework, case study plans, reference list
- `src/` — Python source code for data pipelines, plotting, and dynamics models
- `notebooks/` — Marimo notebooks for analysis (`.py` files, not Jupyter)
- `data/` — Raw and processed datasets (not committed to git)
- `tests/` — Unit and integration tests
- `.github/scripts/build.py` — Exports notebooks to static HTML for GitHub Pages
- `scripts/deploy.sh` — Builds the site and pushes to the `gh-pages` branch

## Getting Started

```bash
# Install dependencies (uses uv)
uv sync

# Open a notebook
uv run marimo edit notebooks/dd001_capital_reality/01_markets_and_money.py

# Run tests
uv run pytest

# Build the site locally
uv run python .github/scripts/build.py

# Deploy to GitHub Pages
bash scripts/deploy.sh
```

## License

MIT
