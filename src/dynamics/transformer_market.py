"""
Python model 'transformer_market.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Delay, Integ
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 2020,
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
    name="Cumulative Production",
    units="Units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulative_production": 1},
    other_deps={
        "_integ_cumulative_production": {"initial": {}, "step": {"production_rate": 1}}
    },
)
def cumulative_production():
    """
    Total cumulative distribution transformers produced.
    """
    return _integ_cumulative_production()


_integ_cumulative_production = Integ(
    lambda: production_rate(), lambda: 10000, "_integ_cumulative_production"
)


@component.add(
    name="Order Backlog",
    units="Units",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_order_backlog": 1},
    other_deps={
        "_integ_order_backlog": {
            "initial": {},
            "step": {"new_orders": 1, "production_rate": 1},
        }
    },
)
def order_backlog():
    """
    Unfilled transformer orders in pipeline.
    """
    return _integ_order_backlog()


_integ_order_backlog = Integ(
    lambda: new_orders() - production_rate(), lambda: 2000, "_integ_order_backlog"
)


@component.add(
    name="Manufacturing Capacity",
    units="Units/Year",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_manufacturing_capacity": 1},
    other_deps={
        "_integ_manufacturing_capacity": {
            "initial": {},
            "step": {"capacity_expansion_rate": 1, "capacity_depreciation_rate": 1},
        }
    },
)
def manufacturing_capacity():
    """
    Annual transformer production capacity.
    """
    return _integ_manufacturing_capacity()


_integ_manufacturing_capacity = Integ(
    lambda: capacity_expansion_rate() - capacity_depreciation_rate(),
    lambda: 5000,
    "_integ_manufacturing_capacity",
)


@component.add(
    name="Standardization Fraction",
    units="Dimensionless",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_standardization_fraction": 1},
    other_deps={
        "_integ_standardization_fraction": {
            "initial": {},
            "step": {"standardization_change_rate": 1},
        }
    },
)
def standardization_fraction():
    """
    Fraction of production using standardized designs.
    """
    return _integ_standardization_fraction()


_integ_standardization_fraction = Integ(
    lambda: standardization_change_rate(),
    lambda: 0.15,
    "_integ_standardization_fraction",
)


@component.add(
    name="Regulatory Stringency",
    units="Dimensionless",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_regulatory_stringency": 1},
    other_deps={
        "_integ_regulatory_stringency": {
            "initial": {},
            "step": {"regulatory_tightening_rate": 1},
        }
    },
)
def regulatory_stringency():
    """
    Index of DOE efficiency standard tightness.
    """
    return _integ_regulatory_stringency()


_integ_regulatory_stringency = Integ(
    lambda: regulatory_tightening_rate(), lambda: 0.3, "_integ_regulatory_stringency"
)


@component.add(
    name="production rate",
    units="Units/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"manufacturing_capacity": 1, "order_backlog": 1, "target_lead_time": 1},
)
def production_rate():
    """
    Actual production constrained by capacity and backlog.
    """
    return float(
        np.minimum(manufacturing_capacity(), order_backlog() / target_lead_time())
    )


@component.add(
    name="new orders",
    units="Units/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "base_demand": 1,
        "ai_demand_growth_rate": 1,
        "price_elasticity_effect": 1,
    },
)
def new_orders():
    """
    Annual transformer orders driven by AI and grid demand.
    """
    return base_demand() * (1 + ai_demand_growth_rate()) * price_elasticity_effect()


@component.add(
    name="capacity expansion rate",
    units="Units/Year/Year",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_capacity_expansion_rate": 1},
    other_deps={
        "_delay_capacity_expansion_rate": {
            "initial": {"desired_capacity_expansion": 1, "capacity_expansion_delay": 1},
            "step": {"desired_capacity_expansion": 1, "capacity_expansion_delay": 1},
        }
    },
)
def capacity_expansion_rate():
    """
    New capacity coming online after construction delay.
    """
    return _delay_capacity_expansion_rate()


_delay_capacity_expansion_rate = Delay(
    lambda: desired_capacity_expansion(),
    lambda: capacity_expansion_delay(),
    lambda: desired_capacity_expansion(),
    lambda: 3,
    time_step,
    "_delay_capacity_expansion_rate",
)


@component.add(
    name="capacity depreciation rate",
    units="Units/Year/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"manufacturing_capacity": 1, "depreciation_fraction": 1},
)
def capacity_depreciation_rate():
    """
    Annual capacity retirement.
    """
    return manufacturing_capacity() * depreciation_fraction()


@component.add(
    name="standardization change rate",
    units="1/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "target_standardization": 1,
        "standardization_fraction": 1,
        "standardization_adjustment_time": 1,
    },
)
def standardization_change_rate():
    """
    Rate of convergence toward target standardization level.
    """
    return (
        target_standardization() - standardization_fraction()
    ) / standardization_adjustment_time()


@component.add(
    name="regulatory tightening rate",
    units="1/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "regulatory_step_size": 1, "regulatory_adjustment_time": 1},
)
def regulatory_tightening_rate():
    """
    DOE 2024 final rule takes effect April 2029.
    """
    return if_then_else(
        time() >= 2029,
        lambda: regulatory_step_size() / regulatory_adjustment_time(),
        lambda: 0,
    )


@component.add(
    name="base demand", units="Units/Year", comp_type="Constant", comp_subtype="Normal"
)
def base_demand():
    """
    Baseline annual distribution transformer demand.
    """
    return 3000


@component.add(
    name="AI demand growth rate",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ai_demand_growth_rate():
    """
    Annual growth rate of data center and grid modernization demand.
    """
    return 0.12


@component.add(
    name="price elasticity effect",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"price_elasticity": 1, "initial_unit_cost": 1, "unit_cost": 1},
)
def price_elasticity_effect():
    """
    Demand response to price changes.
    """
    return 1 - price_elasticity() * (unit_cost() / initial_unit_cost() - 1)


@component.add(
    name="price elasticity",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def price_elasticity():
    """
    Price elasticity of transformer demand.
    """
    return 0.3


@component.add(
    name="unit cost",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "manufacturing_cost": 1,
        "material_cost": 1,
        "regulatory_cost_premium": 1,
    },
)
def unit_cost():
    """
    Total unit cost composite.
    """
    return manufacturing_cost() + material_cost() + regulatory_cost_premium()


@component.add(
    name="manufacturing cost",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_manufacturing_cost": 1,
        "effective_learning_exponent": 1,
        "reference_production": 1,
        "cumulative_production": 1,
    },
)
def manufacturing_cost():
    """
    Wright Law cost curve conditional on standardization.
    """
    return initial_manufacturing_cost() * (
        cumulative_production() / reference_production()
    ) ** (0 - effective_learning_exponent())


@component.add(
    name="initial manufacturing cost",
    units="Dollars/Unit",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_manufacturing_cost():
    """
    Normalized initial manufacturing cost (40 percent of total).
    """
    return 40


@component.add(
    name="reference production",
    units="Units",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reference_production():
    """
    Reference cumulative production for normalization.
    """
    return 10000


@component.add(
    name="effective learning exponent",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"learning_exponent": 1, "standardization_effect": 1},
)
def effective_learning_exponent():
    """
    Learning activates proportionally to standardization level.
    """
    return learning_exponent() * standardization_effect()


@component.add(
    name="learning exponent",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def learning_exponent():
    """
    Wright Law exponent. 0.18 corresponds to 12 percent learning rate.
    """
    return 0.18


@component.add(
    name="standardization effect",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"standardization_fraction": 2, "standardization_threshold": 1},
)
def standardization_effect():
    """
    Multiplier on learning exponent.
    """
    return if_then_else(
        standardization_fraction() > standardization_threshold(),
        lambda: standardization_fraction(),
        lambda: 0.05,
    )


@component.add(
    name="standardization threshold",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def standardization_threshold():
    """
    Minimum standardization for meaningful learning curve effects.
    """
    return 0.4


@component.add(
    name="material cost",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"copper_cost_component": 1, "steel_cost_component": 1},
)
def material_cost():
    """
    Raw material cost 30 percent copper plus 30 percent GOES steel.
    """
    return copper_cost_component() + steel_cost_component()


@component.add(
    name="copper cost component",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"copper_price_index": 1},
)
def copper_cost_component():
    """
    Copper winding cost.
    """
    return 30 * copper_price_index()


@component.add(
    name="steel cost component",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"steel_price_index": 1},
)
def steel_cost_component():
    """
    GOES core cost.
    """
    return 30 * steel_price_index()


@component.add(
    name="copper price index",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def copper_price_index():
    """
    Simplified copper price trend.
    """
    return 1 + 0.02 * (time() - 2020)


@component.add(
    name="steel price index",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def steel_price_index():
    """
    Simplified GOES steel price trend.
    """
    return 1 + 0.015 * (time() - 2020)


@component.add(
    name="regulatory cost premium",
    units="Dollars/Unit",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "regulatory_stringency": 1,
        "regulatory_cost_multiplier": 1,
        "initial_unit_cost": 1,
    },
)
def regulatory_cost_premium():
    """
    Additional cost from DOE efficiency standards.
    """
    return regulatory_stringency() * regulatory_cost_multiplier() * initial_unit_cost()


@component.add(
    name="regulatory cost multiplier",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def regulatory_cost_multiplier():
    """
    Maximum regulatory cost as fraction of base unit cost.
    """
    return 0.15


@component.add(
    name="initial unit cost",
    units="Dollars/Unit",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_unit_cost():
    """
    Normalized starting unit cost.
    """
    return 100


@component.add(
    name="target lead time", units="Years", comp_type="Constant", comp_subtype="Normal"
)
def target_lead_time():
    """
    Target production lead time.
    """
    return 1.5


@component.add(
    name="desired capacity expansion",
    units="Units/Year/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "order_backlog": 1,
        "target_lead_time": 1,
        "manufacturing_capacity": 1,
        "expansion_aggressiveness": 1,
    },
)
def desired_capacity_expansion():
    """
    Desired new capacity based on gap between needed and existing.
    """
    return float(
        np.maximum(
            0,
            (order_backlog() / target_lead_time() - manufacturing_capacity())
            * expansion_aggressiveness(),
        )
    )


@component.add(
    name="expansion aggressiveness",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def expansion_aggressiveness():
    """
    Fraction of capacity gap addressed per year.
    """
    return 0.2


@component.add(
    name="capacity expansion delay",
    units="Years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def capacity_expansion_delay():
    """
    Time from investment decision to production ready capacity.
    """
    return 3


@component.add(
    name="depreciation fraction",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def depreciation_fraction():
    """
    Annual capacity depreciation rate.
    """
    return 0.03


@component.add(
    name="target standardization",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"base_standardization": 1, "hyperscaler_standardization_pull": 1},
)
def target_standardization():
    """
    Long run standardization target driven by hyperscaler procurement.
    """
    return float(
        np.minimum(1, base_standardization() + hyperscaler_standardization_pull())
    )


@component.add(
    name="base standardization",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def base_standardization():
    """
    Baseline standardization in absence of hyperscaler demand.
    """
    return 0.15


@component.add(
    name="hyperscaler standardization pull",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"hyperscaler_demand_fraction": 1, "hyperscaler_convergence_factor": 1},
)
def hyperscaler_standardization_pull():
    """
    Hyperscaler procurement drives standardization.
    """
    return hyperscaler_demand_fraction() * hyperscaler_convergence_factor()


@component.add(
    name="hyperscaler demand fraction",
    units="Dimensionless",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def hyperscaler_demand_fraction():
    """
    Fraction of total demand from hyperscalers.
    """
    return float(np.minimum(1, 0.1 + 0.03 * (time() - 2020)))


@component.add(
    name="hyperscaler convergence factor",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def hyperscaler_convergence_factor():
    """
    How much hyperscaler procurement drives design convergence.
    """
    return 0.8


@component.add(
    name="standardization adjustment time",
    units="Years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def standardization_adjustment_time():
    """
    Time for standardization fraction to converge toward target.
    """
    return 5


@component.add(
    name="regulatory step size",
    units="Dimensionless",
    comp_type="Constant",
    comp_subtype="Normal",
)
def regulatory_step_size():
    """
    Size of DOE 2029 efficiency standard increase.
    """
    return 0.25


@component.add(
    name="regulatory adjustment time",
    units="Years",
    comp_type="Constant",
    comp_subtype="Normal",
)
def regulatory_adjustment_time():
    """
    Time for industry to absorb new regulatory requirements.
    """
    return 2
