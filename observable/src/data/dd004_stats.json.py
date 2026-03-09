#!/usr/bin/env python3
"""Data loader: Combined stats dict for DD-004 prose interpolation.

Mirrors the stats cells in notebooks/dd004_utility_regulation/ notebooks
so the Observable page prose can reference the same numbers.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

# ── Source citations ──────────────────────────────────────────────────────
cite_raw = query("SELECT key, value FROM energy_data.source_citations")
cmap = dict(zip(cite_raw["key"], cite_raw["value"]))

# ── PJM demand data ──────────────────────────────────────────────────────
pjm = query("""
    SELECT zone, year, requested_mw
    FROM energy_data.dd004_pjm_zone_demand
    WHERE request_type = 'demand' AND year BETWEEN 2026 AND 2035
    ORDER BY zone, year
""")

aep = pjm[pjm["zone"] == "AEP"]
aep_2026 = float(aep[aep["year"] == 2026]["requested_mw"].iloc[0])
aep_2030 = float(aep[aep["year"] == 2030]["requested_mw"].iloc[0])

rto = pjm[pjm["zone"] == "PJM RTO"]
rto_2026 = float(rto[rto["year"] == 2026]["requested_mw"].iloc[0])
rto_2030 = float(rto[rto["year"] == 2030]["requested_mw"].iloc[0])

dom = pjm[pjm["zone"] == "DOM"]
dom_2026 = float(dom[dom["year"] == 2026]["requested_mw"].iloc[0])
dom_2030 = float(dom[dom["year"] == 2030]["requested_mw"].iloc[0])

# ── IURC cases ───────────────────────────────────────────────────────────
iurc = query("""
    SELECT cause_number, key_metric, key_metric_value
    FROM energy_data.dd004_iurc_cases
""")
egr = iurc[iurc["cause_number"] == "46301"].set_index("key_metric")
tariff = iurc[iurc["cause_number"] == "46097"].set_index("key_metric")

total_icap_mw = float(egr.loc["total_icap_need_mw", "key_metric_value"])
gas_ct_mw = float(egr.loc["new_gas_ct_mw", "key_metric_value"])
clean_energy_mw = float(egr.loc["clean_energy_ceiling_mw", "key_metric_value"])
tier1_mw = float(tariff.loc["tier1_threshold_mw", "key_metric_value"])
tier2_mw = float(tariff.loc["tier2_threshold_mw", "key_metric_value"])

stats = {
    # Virginia (JLARC)
    "va_tax_savings_m": int(cmap["jlarc_va_sales_tax_savings_fy23_m"]),
    "va_global_share_pct": int(cmap["jlarc_nova_global_share_pct"]),
    "va_americas_share_pct": int(cmap["jlarc_nova_americas_share_pct"]),
    "va_dc_gdp_bn": float(cmap["jlarc_va_dc_gdp_bn"]),
    "va_dc_jobs": int(cmap["jlarc_va_dc_jobs"]),
    "va_dc_labor_income_bn": float(cmap["jlarc_va_dc_labor_income_bn"]),
    "va_local_rev_max_pct": int(cmap["jlarc_va_dc_local_rev_max_pct"]),

    # Indiana
    "indiana_amazon_bn": int(cmap["iurc_amazon_indiana_investment_bn"]),
    "indiana_msft_bn": int(cmap["iurc_msft_indiana_investment_bn"]),
    "indiana_total_bn": round(float(cmap["iurc_hyperscaler_indiana_total_bn"]), 1),
    "indiana_peak_2024_gw": round(float(cmap["iurc_imp_peak_2024_gw"]), 1),
    "indiana_peak_2030_gw": int(cmap["iurc_imp_peak_2030_gw"]),
    "indiana_load_growth_gw": round(float(cmap["iurc_imp_load_growth_gw"]), 1),
    "indiana_signed_mw": int(cmap["iurc_imp_large_load_signed_mw"]),

    # IURC case metrics
    "total_icap_mw": int(total_icap_mw),
    "gas_ct_mw": int(gas_ct_mw),
    "clean_energy_mw": int(clean_energy_mw),
    "tier1_mw": int(tier1_mw),
    "tier2_mw": int(tier2_mw),
    "stranded_cost_1gw_bn": float(cmap["iurc_imp_ll_stranded_cost_1gw_bn"]),
    "collateral_m": int(cmap["iurc_imp_ll_collateral_m"]),
    "demand_charge_kw": float(cmap["iurc_imp_ll_demand_charge_kw"]),
    "capacity_deficit_mw": int(cmap.get("iurc_egr_capacity_deficit_2030_mw", 4034)),
    "oregon_mw": int(cmap["iurc_oregon_ccgt_mw"]),
    "oregon_eol": int(cmap["iurc_oregon_eol_year"]),
    "transmission_cost_m": int(cmap["iurc_imp_ll_transmission_cost_annual_m"]),

    # PJM demand
    "aep_2026_mw": int(aep_2026),
    "aep_2030_mw": int(aep_2030),
    "aep_growth_mw": int(aep_2030 - aep_2026),
    "aep_growth_pct": round((aep_2030 - aep_2026) / aep_2026 * 100),
    "dom_2026_mw": int(dom_2026),
    "dom_2030_mw": int(dom_2030),
    "rto_2026_mw": int(rto_2026),
    "rto_2030_mw": int(rto_2030),

    # Derived
    "gas_ct_pct_of_icap": round(gas_ct_mw / total_icap_mw * 100),
    "peak_growth_pct": round((float(cmap["iurc_imp_peak_2030_gw"]) - float(cmap["iurc_imp_peak_2024_gw"])) / float(cmap["iurc_imp_peak_2024_gw"]) * 100),
}

print(json.dumps(stats))
