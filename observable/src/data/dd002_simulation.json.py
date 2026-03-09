#!/usr/bin/env python3
"""Data loader: Pre-computed PySD results for DD-002 feedback architecture.

Produces:
  - baseline: 4-panel time series (grid capacity, BTM, queue, renewable cost, spillover)
  - sensitivity: BTM cost x Regulatory favorability -> spillover heatmap
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import numpy as np
import pysd

# ── Load model ───────────────────────────────────────────────────────────
project_root = Path(__file__).parent.parent.parent.parent
model_path = project_root / "src" / "dynamics" / "grid_modernization.mdl"
model = pysd.read_vensim(str(model_path))

# ── Baseline run ─────────────────────────────────────────────────────────
baseline_df = model.run()

baseline = []
for idx, row in baseline_df.iterrows():
    baseline.append({
        "time": round(float(idx), 1),
        "grid_capacity": round(float(row["Grid Capacity"]), 1),
        "btm_capacity": round(float(row["Behind the Meter Capacity"]), 1),
        "queue_backlog": round(float(row["Queue Backlog"]), 1),
        "renewable_cost": round(float(row["Renewable Cost Index"]), 1),
        "spillover": round(float(row["grid spillover index"]), 3),
    })

# ── Sensitivity sweep ───────────────────────────────────────────────────
btm_range = np.arange(0.5, 2.1, 0.1).tolist()
reg_range = np.arange(0.1, 1.0, 0.05).tolist()
sensitivity = []

for reg in reg_range:
    row_data = []
    for btm in btm_range:
        result = model.run(params={
            "btm cost advantage": btm,
            "target regulatory favorability": reg,
        })
        idx_2035 = result.index.get_indexer([2035], method="nearest")[0]
        spillover = float(result["grid spillover index"].iloc[idx_2035])
        row_data.append(round(spillover, 3))
    sensitivity.append(row_data)

print(json.dumps({
    "baseline": baseline,
    "sensitivity": {
        "btm_range": [round(x, 1) for x in btm_range],
        "reg_range": [round(x, 2) for x in reg_range],
        "spillover": sensitivity,
    },
}))
