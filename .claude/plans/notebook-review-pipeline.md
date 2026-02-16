# Plan: Run Notebook Review Pipeline on All Notebooks

## Context

We built and tested a repeatable notebook review workflow on DD-001. The workflow
is now codified as:
- A new `notebook-qa` agent (`.claude/agents/notebook-qa.md`)
- An updated publication pipeline in `CLAUDE.md`
- A 6-step revision checklist

DD-001 has been fully reviewed and fixed. The remaining notebooks need the same treatment.

## What Was Done on DD-001 (completed)

1. Ran critic agent → found 10 priority issues (numerical errors, missing citations,
   logical gaps, structural omissions)
2. Ran data verification queries against DuckDB → confirmed exact correct values
3. Created a `stats` cell that computes all key summary values from data
4. Replaced all hardcoded data-derived values in `mo.md()` cells with f-string
   interpolation from `stats` — captions now auto-update when data changes
5. Fixed reference line bug (0.30 → 0.234, now computed from stats)
6. Fixed caption errors ($147B → $158B, $9.5T → $9.7T, 30x → 41x, 9% → 7%)
7. Added methodology caveats (fiscal year misalignment, capex definition scope,
   global-vs-US denominator, decomposition estimate uncertainty)
8. Added source citations (LBNL "Queued Up" 2024, BEA NIPA Table 5.3.5)
9. Nuanced unsupported claims (prisoner's dilemma + Meta counterexample)
10. Fixed prose inconsistencies ("red dashed line" → "red line")
11. Validated: ruff check passes, marimo export html succeeds, charts render correctly

## What Needs to Be Done

### Step 1: Review DD-002 notebooks (3 notebooks)

Run critic + notebook-qa agents **in parallel** on each:

```
notebooks/dd002_grid_modernization/01_whats_getting_built.py
notebooks/dd002_grid_modernization/02_who_benefits.py
notebooks/dd002_grid_modernization/03_feedback_architecture.py
```

For each notebook:
1. Launch critic agent: "Review [notebook path] for logical gaps and evidence quality"
2. Launch notebook-qa agent: "Run data QA on [notebook path]"
3. Merge both reports into a task list
4. Execute the 6-step revision checklist:
   a. Fix numerical errors
   b. Data-ground all values (create/update stats cell, replace hardcoded numbers)
   c. Add missing citations
   d. Add methodology caveats
   e. Address logical gaps
   f. Validate (ruff + marimo export + visual check)

### Step 2: Apply SWD fixes from the earlier audit

The SWD audit (from a previous session) identified these critical DD-002 chart redesigns:

| Priority | Chart | Issue | Fix |
|:---------|:------|:------|:----|
| Critical | dd002_energy_prices | Dual y-axis | Single axis or small multiples |
| Critical | dd002_capacity_factor | Grouped bars | Cleveland dot plot |
| Critical | dd002_queue_funnel | Chart junk | Replace with data-driven version |
| Critical | dd002_plant_map | Data dump | Find one story or cut |
| High | dd002_generation_mix | No gray+accent | Apply SWD pattern |
| High | dd002_queue_composition | No gray+accent | Apply SWD pattern |
| High | dd002_asset_timeline | No gray+accent | Apply SWD pattern |
| High | dd002_baseline_simulation | No gray+accent | Apply SWD pattern |
| Pervasive | All DD-002 charts | No chart_title() | Add insight titles |

### Step 3: Add chart_title() to all DD-002 charts

18 of 21 DD-002 charts have no title in the PNG. Apply `chart_title()` to each,
following the pattern established in DD-001.

### Step 4: Final validation

```bash
bash scripts/test_notebooks.sh
```

All 4 notebooks must pass headless export.

## Sequencing

The most efficient approach is to process one notebook at a time, completing all
review + fixes before moving to the next:

1. `01_whats_getting_built.py` — largest notebook, most charts
2. `02_who_benefits.py` — moderate size
3. `03_feedback_architecture.py` — smallest, most analytical

For each notebook, the critic and notebook-qa agents should run in parallel.
SWD fixes and chart_title() additions happen during the revision step.

## Key Patterns Established in DD-001

### Stats cell pattern
```python
@app.cell
def _(capex_annual, guidance_2025, mkt_cap):
    stats = {
        "capex_2024": annual[annual["year"] == 2024]["capex_bn"].sum(),
        "guidance_2025": guidance["capex_bn"].sum(),
        "mkt_gain_t": mkt_cap["gain_t"].sum(),
    }
    stats["ratio_vs_2024"] = stats["mkt_gain_t"] / (stats["capex_2024"] / 1000)
    return (stats,)
```

### Data-driven caption pattern
```python
@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "chart.png").read_bytes(), width=850)
    mo.md(f"""
    # Heading with data: ${stats['value']:.0f}B

    {_chart}

    *Caption using ${stats['value']:.0f}B instead of hardcoded numbers.*
    """)
    return
```

### Dollar signs in matplotlib vs marimo
- `mo.md(f"...")`: `$234B` works fine (no escaping needed)
- `ax.text(f"...")`: use `\\$` for literal dollar sign (matplotlib TeX)
- `chart_title(fig, f"...")`: same as ax.text, use `\\$`
- `chart_title(fig, r"...")`: use `\$` for literal dollar sign

### Data verification query pattern
```bash
uv run python -c "
from src.data.db import query
import pandas as pd
df = query('SELECT ... FROM energy_data.table_name')
print(df)
"
```

## Files Modified in DD-001 Review

- `notebooks/dd001_capital_reality/01_capex_vs_reality.py` — all prose and chart fixes
- `src/plotting.py` — chart_title() helper (added in earlier session)
- `.claude/agents/notebook-qa.md` — NEW agent
- `CLAUDE.md` — updated pipeline documentation
