"""
Python model 'grid_modernization.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.statefuls import Integ, Delay
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 2024,
    "final_time": lambda: 2040,
    "time_step": lambda: 0.25,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="INITIAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    return __data["time"].initial_time()


@component.add(
    name="FINAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    return __data["time"].final_time()


@component.add(
    name="TIME STEP", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def time_step():
    return __data["time"].time_step()


@component.add(
    name="SAVEPER",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    return __data["time"].saveper()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Grid Capacity",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_grid_capacity": 1},
    other_deps={
        "_integ_grid_capacity": {
            "initial": {},
            "step": {"grid_additions": 1, "grid_retirements": 1},
        }
    },
)
def grid_capacity():
    """
    Total grid-connected generation capacity serving data center corridors.
    """
    return _integ_grid_capacity()


_integ_grid_capacity = Integ(
    lambda: grid_additions() - grid_retirements(), lambda: 50, "_integ_grid_capacity"
)


@component.add(
    name="Behind the Meter Capacity",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_behind_the_meter_capacity": 1},
    other_deps={
        "_integ_behind_the_meter_capacity": {
            "initial": {},
            "step": {"btm_additions": 1},
        }
    },
)
def behind_the_meter_capacity():
    """
    Data center on-site generation (gas, solar, batteries) bypassing the grid.
    """
    return _integ_behind_the_meter_capacity()


_integ_behind_the_meter_capacity = Integ(
    lambda: btm_additions(), lambda: 5, "_integ_behind_the_meter_capacity"
)


@component.add(
    name="Queue Backlog",
    units="GW",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_queue_backlog": 1},
    other_deps={
        "_integ_queue_backlog": {
            "initial": {},
            "step": {
                "queue_entries": 1,
                "queue_completions": 1,
                "queue_withdrawals": 1,
            },
        }
    },
)
def queue_backlog():
    """
    Interconnection queue: projects waiting for grid connection.
    """
    return _integ_queue_backlog()


_integ_queue_backlog = Integ(
    lambda: queue_entries() - queue_completions() - queue_withdrawals(),
    lambda: 200,
    "_integ_queue_backlog",
)


@component.add(
    name="Renewable Cost Index",
    units="Dollars/MWh",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_renewable_cost_index": 1},
    other_deps={
        "_integ_renewable_cost_index": {
            "initial": {},
            "step": {"renewable_learning": 1},
        }
    },
)
def renewable_cost_index():
    """
    Levelized cost of utility-scale solar plus storage.
    """
    return _integ_renewable_cost_index()


_integ_renewable_cost_index = Integ(
    lambda: -renewable_learning(), lambda: 40, "_integ_renewable_cost_index"
)


@component.add(
    name="Regulatory Favorability",
    units="Dimensionless",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_regulatory_favorability": 1},
    other_deps={
        "_integ_regulatory_favorability": {
            "initial": {},
            "step": {"regulatory_change": 1},
        }
    },
)
def regulatory_favorability():
    """
    Index (0-1) of regulatory support for grid-connected data centers.
    """
    return _integ_regulatory_favorability()


_integ_regulatory_favorability = Integ(
    lambda: regulatory_change(), lambda: 0.6, "_integ_regulatory_favorability"
)


@component.add(
    name="grid additions",
    units="GW/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_grid_additions": 1},
    other_deps={
        "_delay_grid_additions": {
            "initial": {"desired_grid_expansion": 1, "permitting_delay": 1},
            "step": {"desired_grid_expansion": 1, "permitting_delay": 1},
        }
    },
)
def grid_additions():
    """
    New grid-connected generation coming online after permitting delay.
    """
    return _delay_grid_additions()


_delay_grid_additions = Delay(
    lambda: desired_grid_expansion(),
    lambda: permitting_delay(),
    lambda: desired_grid_expansion(),
    lambda: 3,
    time_step,
    "_delay_grid_additions",
)


@component.add(
    name="grid retirements",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grid_capacity": 1, "retirement_fraction": 1},
)
def grid_retirements():
    """
    Annual grid capacity retirement.
    """
    return grid_capacity() * retirement_fraction()


@component.add(
    name="btm additions",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ai_demand_growth": 1, "btm_fraction": 1},
)
def btm_additions():
    """
    New behind-the-meter capacity added by data center operators.
    """
    return ai_demand_growth() * btm_fraction()


@component.add(
    name="queue entries",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ai_demand_growth": 1, "non_ai_generation_proposals": 1},
)
def queue_entries():
    """
    New projects entering the interconnection queue.
    """
    return ai_demand_growth() + non_ai_generation_proposals()


@component.add(
    name="queue completions",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"queue_backlog": 1, "queue_processing_time": 1},
)
def queue_completions():
    """
    Projects completing the interconnection process.
    """
    return queue_backlog() / queue_processing_time()


@component.add(
    name="queue withdrawals",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"queue_backlog": 1, "withdrawal_fraction": 1},
)
def queue_withdrawals():
    """
    Projects withdrawn from the queue (never built).
    """
    return queue_backlog() * withdrawal_fraction()


@component.add(
    name="renewable learning",
    units="Dollars/MWh/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "learning_rate": 1,
        "renewable_production_growth": 1,
        "renewable_cost_index": 1,
    },
)
def renewable_learning():
    """
    Wright Law cost reduction in renewables.
    """
    return learning_rate() * renewable_production_growth() * renewable_cost_index()


@component.add(
    name="regulatory change",
    units="1/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "target_regulatory_favorability": 1,
        "regulatory_favorability": 1,
        "regulatory_adjustment_time": 1,
    },
)
def regulatory_change():
    """
    Convergence toward target regulatory environment.
    """
    return (
        target_regulatory_favorability() - regulatory_favorability()
    ) / regulatory_adjustment_time()


@component.add(
    name="AI demand growth",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"base_ai_demand": 1, "ai_growth_rate": 1, "time": 1},
)
def ai_demand_growth():
    """
    Annual new data center power demand driven by AI buildout.
    """
    return base_ai_demand() * (1 + ai_growth_rate()) ** (time() - 2024)


@component.add(
    name="base AI demand", units="GW/Year", comp_type="Constant", comp_subtype="Normal"
)
def base_ai_demand():
    """
    Baseline annual AI-driven power demand growth (2024 level).
    """
    return 5


@component.add(
    name="AI growth rate", units="1/Year", comp_type="Constant", comp_subtype="Normal"
)
def ai_growth_rate():
    """
    Annual growth rate of AI power demand.
    """
    return 0.15


@component.add(
    name="non AI generation proposals",
    units="GW/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def non_ai_generation_proposals():
    """
    Non-AI generation projects entering the queue (renewables, replacements).
    """
    return 15


@component.add(
    name="btm fraction",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"btm_attractiveness": 2, "grid_attractiveness": 1},
)
def btm_fraction():
    """
    Share of new AI demand going behind-the-meter.
    """
    return btm_attractiveness() / (btm_attractiveness() + grid_attractiveness())


@component.add(
    name="btm attractiveness",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"regulatory_favorability": 1, "btm_cost_advantage": 1},
)
def btm_attractiveness():
    """
    Attractiveness of bypassing the grid. Increases when regulatory environment is hostile.
    """
    return (1 - regulatory_favorability()) * btm_cost_advantage()


@component.add(
    name="btm cost advantage",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def btm_cost_advantage():
    """
    Cost advantage of behind-the-meter relative to grid (>1 means BTM is cheaper).
    """
    return 1.2


@component.add(
    name="grid attractiveness",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "regulatory_favorability": 1,
        "queue_wait_time": 1,
        "reference_queue_time": 1,
        "grid_reliability_premium": 1,
    },
)
def grid_attractiveness():
    """
    Attractiveness of grid connection. Higher when regulatory environment is favorable and queue is short.
    """
    return (
        regulatory_favorability()
        * (reference_queue_time() / queue_wait_time())
        * grid_reliability_premium()
    )


@component.add(
    name="grid reliability premium",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def grid_reliability_premium():
    """
    Premium for grid reliability vs behind-the-meter risk.
    """
    return 1.5


@component.add(
    name="queue wait time",
    units="Years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"queue_backlog": 1, "queue_processing_rate": 1},
)
def queue_wait_time():
    """
    Average time to get through the interconnection queue.
    """
    return float(np.maximum(1, queue_backlog() / queue_processing_rate()))


@component.add(
    name="queue processing rate",
    units="GW/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def queue_processing_rate():
    """
    Queue throughput capacity (projects processed per year).
    """
    return 40


@component.add(
    name="queue processing time",
    units="Years",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"queue_backlog": 1, "queue_processing_rate": 1},
)
def queue_processing_time():
    """
    Time for average project to clear the queue.
    """
    return float(np.maximum(1, queue_backlog() / queue_processing_rate()))


@component.add(
    name="reference queue time",
    units="Years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reference_queue_time():
    """
    Reference queue wait time for attractiveness normalization.
    """
    return 3


@component.add(
    name="desired grid expansion",
    units="GW/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ai_demand_growth": 1,
        "btm_fraction": 1,
        "queue_completions": 1,
        "expansion_capture_fraction": 1,
        "grid_retirements": 1,
        "expansion_aggressiveness": 1,
    },
)
def desired_grid_expansion():
    """
    Desired new grid capacity based on demand and queue throughput.
    """
    return float(
        np.maximum(
            0,
            (
                ai_demand_growth() * (1 - btm_fraction())
                + queue_completions() * expansion_capture_fraction()
                - grid_retirements()
            )
            * expansion_aggressiveness(),
        )
    )


@component.add(
    name="expansion capture fraction",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def expansion_capture_fraction():
    """
    Fraction of queue completions that actually become operational capacity.
    """
    return 0.6


@component.add(
    name="expansion aggressiveness",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def expansion_aggressiveness():
    """
    Responsiveness of grid investment to perceived need.
    """
    return 0.3


@component.add(
    name="permitting delay", units="Years", comp_type="Constant", comp_subtype="Normal"
)
def permitting_delay():
    """
    Time from investment decision to operational capacity.
    """
    return 3


@component.add(
    name="retirement fraction",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def retirement_fraction():
    """
    Annual grid capacity retirement rate.
    """
    return 0.02


@component.add(
    name="withdrawal fraction",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def withdrawal_fraction():
    """
    Annual fraction of queued projects that withdraw.
    """
    return 0.15


@component.add(
    name="learning rate",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def learning_rate():
    """
    Wright Law learning rate for renewables (20 percent cost reduction per doubling of cumulative production).
    """
    return 0.2


@component.add(
    name="renewable production growth",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def renewable_production_growth():
    """
    Annual growth rate of renewable energy production.
    """
    return 0.08


@component.add(
    name="target regulatory favorability",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def target_regulatory_favorability():
    """
    Long-run regulatory favorability target.
    """
    return 0.5


@component.add(
    name="regulatory adjustment time",
    units="Years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def regulatory_adjustment_time():
    """
    Time for regulatory environment to shift.
    """
    return 5


@component.add(
    name="grid spillover index",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grid_capacity": 2, "behind_the_meter_capacity": 1},
)
def grid_spillover_index():
    """
    Share of total capacity that is grid-connected. Higher = more spillover.
    """
    return grid_capacity() / (grid_capacity() + behind_the_meter_capacity())


@component.add(
    name="cost allocation to ratepayers",
    units="Dollars/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"regulatory_favorability": 1, "grid_additions": 1, "cost_per_gw": 1},
)
def cost_allocation_to_ratepayers():
    """
    Grid investment costs socialized to non-data-center ratepayers.
    """
    return (1 - regulatory_favorability()) * grid_additions() * cost_per_gw()


@component.add(
    name="cost per GW", units="Dollars", comp_type="Constant", comp_subtype="Normal"
)
def cost_per_gw():
    """
    Cost of grid infrastructure per GW (in $B, normalized).
    """
    return 2


@component.add(
    name="total grid investment",
    units="Dollars/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"grid_additions": 1, "cost_per_gw": 1},
)
def total_grid_investment():
    """
    Total annual grid investment.
    """
    return grid_additions() * cost_per_gw()
