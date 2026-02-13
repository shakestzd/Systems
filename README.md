# Beyond the Hype Cycle: Modeling the Durable Commodity and Infrastructure Impacts of AI Capital Flows

## Core Research Question

Which commodity markets and infrastructure systems being catalyzed by AI investment will sustain demand growth independent of AI's commercial success?

## Motivation

AI capital expenditure is driving massive investment into energy, water, minerals, and physical infrastructure. But much of the analysis conflates AI hype with durable structural shifts. This project aims to separate signal from noise by modeling the feedback loops between AI spending and commodity demand, then testing which demand effects persist across different AI adoption scenarios (boom, plateau, bust).

## Methodology

A hybrid quantitative approach combining three techniques:

1. **Systems dynamics modeling** -- Map causal feedback loops between AI CapEx, energy demand, water usage, semiconductor supply chains, and grid infrastructure
2. **Bayesian inference** -- Estimate uncertain model parameters (e.g., what fraction of data center growth is AI-specific vs. general cloud)
3. **Markov regime switching** -- Model scenario transitions (AI boom / plateau / bust) and their effects on commodity demand

## Key Sectors

- Electricity generation and grid capacity
- Water consumption and cooling infrastructure
- Critical minerals (copper, lithium, rare earths, silicon)
- Fiber optic and network backbone
- Real estate and construction (data center specific)

## Project Status

**Phase:** Initial framework and research design

## Repository Contents

- `research-framework.md` -- Detailed methodology, sector analysis approach, and phased learning plan
- `data-sources.md` -- Catalog of data sources with descriptions and access information
- `src/` -- Python source code for models and data pipelines
- `notebooks/` -- Jupyter notebooks for exploration and analysis
- `data/` -- Raw and processed datasets (not committed to git)
- `tests/` -- Unit and integration tests

## Tools and Skills Being Developed

- Systems dynamics modeling (Vensim/Stella or Python with PySD)
- Bayesian statistics and parameter estimation
- Markov regime switching models
- Financial/commodity data analysis

## Getting Started

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## License

MIT
