# Where AI Capital Lands

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
| **CS-1** | Transformer manufacturing and grid equipment | Draft complete |
| **CS-2** | Power generation mix and asset lock-in | Not started |
| **CS-3** | Grid interconnection and transmission | Not started |
| **CS-4** | Material supply chains (GOES, copper, critical minerals) | Not started |
| **CS-5** | Labor and workforce | Not started |

## Project Status

**Phase 1:** Tightening CS-1 (transformer case study) and establishing the
analytical framework for publication.

## Repository Contents

- `research-framework.md` — Analytical framework, case study plans, reference list
- `data-sources.md` — Catalog of data sources with access information
- `src/` — Python source code for models and data pipelines
- `notebooks/` — Marimo notebooks for analysis (.py files, not Jupyter)
- `data/` — Raw and processed datasets (not committed to git)
- `tests/` — Unit and integration tests

## Getting Started

```bash
# Install dependencies (uses uv)
uv sync

# Open a notebook
uv run marimo edit notebooks/dd001_learning_curves/01_investigation.py

# Run tests
uv run pytest
```

## License

MIT
