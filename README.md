# The Physical Economy of the Technology Transition

**Live site:** https://shakes-tzd.github.io/Systems/

The AI infrastructure buildout and the energy transition are not separate stories. When an AI company signs a 20-year power purchase agreement, it locks in generation capacity. When a utility cites data center load growth in a rate proceeding — as Dominion Virginia and Georgia Power have done in recent IRP filings — it shapes decisions about what generation gets built. When a semiconductor fab receives federal investment, it reshapes regional labor markets for a generation. These decisions are made in separate rooms by separate actors using separate analytical frameworks. But they are building the same physical world, and their interactions create feedback loops that no single discipline tracks.

The people in that world are ratepayers paying for grid upgrades they didn't ask for, workers whose job markets are being remade faster than retraining programs can follow, communities hosting data centers that draw power and water while offering few local jobs, state commissioners deciding who bears the cost of infrastructure that benefits distant shareholders, and executives making billion-dollar bets on physical assets that will outlast any quarterly report.

Understanding any one piece requires understanding how it connects to the rest. Federal clean energy incentives, now significantly modified by the One Big Beautiful Act (July 2025), shape which generation technologies get built. The US formally withdrew from the Paris Agreement in January 2026, shifting the international context for domestic clean energy investment. FERC interconnection reform determines how fast new generation can reach the grid. State utility regulation shapes who pays for what. These policy regimes interact with market forces in ways that create path dependencies lasting decades — and that can be extended or broken by decisions made in the next few years.

This project investigates where technology capital lands in the physical economy, what it locks in, and who bears the consequences.

## Core Questions

1. Where does capital convert from financial commitment to physical asset, and what infrastructure does it create?
2. How durable is that infrastructure — does it persist regardless of AI outcomes, or does it depend on continued growth or specific policy regimes?
3. Who benefits and who bears the costs? Which workers, communities, and ratepayers are most exposed?
4. How do public policy decisions — at the federal, state, and international level — amplify or distort these outcomes?
5. Where are the feedback loops and leverage points that could change the trajectory?

## Approach

The analytical framework combines:

1. **Capital flow mapping** — Trace where technology capital converts from financial commitment to physical asset
2. **Durability taxonomy** — Classify investments as structural (persists regardless of technology outcome), policy-dependent (tied to a regulatory regime), or demand-thesis-dependent (requires continued growth)
3. **Regulatory interaction analysis** — How trade policy, energy policy, FERC regulation, industrial policy, and state utility regulation shape where capital lands and what it locks in
4. **People and distribution** — Who works in these industries, who bears costs, who makes decisions, who is excluded
5. **Systems dynamics modeling** — Map feedback architecture and identify leverage points across interdependent supply chains and policy regimes

Policy references are dated and verified at time of writing. This is an active investigation in a rapidly shifting landscape.

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
