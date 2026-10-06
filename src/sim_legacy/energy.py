import numpy as np
from numba import njit
from dataclasses import dataclass


@dataclass(frozen=True)
class ActivityCost:
    met: float
    mass_exponent: float = 0.75


ACTIVITY_COSTS = {
    "FORAGE_SEARCH": ActivityCost(met=3.0),
    "FORAGE_INTAKE": ActivityCost(met=1.5),
    "LOCO_WALK_SLOW": ActivityCost(met=2.0),
    "LOCO_WALK_MOD": ActivityCost(met=2.5),
    "LOCO_WALK_FAST": ActivityCost(met=3.0),
    "LOCO_TROT": ActivityCost(met=4.5, mass_exponent=0.70),
    "LOCO_GALLOP": ActivityCost(met=7.0, mass_exponent=0.70),
    "LOCO_SWIM": ActivityCost(met=6.0, mass_exponent=0.80),
    "LOCO_CLIMB": ActivityCost(met=5.0),
    "VIGILANCE": ActivityCost(met=1.3),
    "REPRO_COURTSHIP": ActivityCost(met=2.5),
    "REPRO_GESTATION": ActivityCost(met=1.3),
    "REPRO_LACTATION": ActivityCost(met=3.0),
    "TERMO_SHIVERING": ActivityCost(met=2.0),
    "TERMO_PANTING": ActivityCost(met=1.5),
    "RESTING": ActivityCost(met=1.0),
    "GROOMING": ActivityCost(met=1.5),
    "SOCIAL_INTERACTION": ActivityCost(met=1.8),
}


@njit(cache=True)
def bmr_kcal_day(mass_kg: float) -> float:
    """Basal Metabolic Rate in kcal/day (Kleiber's law)."""
    return 70.0 * (mass_kg**0.75)


@njit(cache=True)
def bmr_kcal_h(mass_kg: float) -> float:
    """Basal Metabolic Rate in kcal/hour."""
    return bmr_kcal_day(mass_kg) / 24.0


@njit(cache=True)
def activity_kcal_h(mass_kg: float, met: float) -> float:
    """Energy cost of an activity in kcal/hour (MET × BMR_hourly)."""
    return met * bmr_kcal_h(mass_kg)


@njit(cache=True)
def loco_cost_hours(mass_kg: float, slope_deg: float, hours: float) -> float:
    if slope_deg < 5.0:
        met = 2.5
    elif slope_deg < 15.0:
        met = 3.0
    elif slope_deg < 30.0:
        met = 5.0
    else:
        met = 6.0
    return activity_kcal_h(mass_kg, met) * hours


@njit(cache=True)
def daily_dee(
    mass_kg: float,
    hours_foraging: float = 6.0,
    hours_locomotion: float = 2.0,
    hours_resting: float = 12.0,
    hours_other: float = 4.0,
    slope_avg: float = 0.0,
    is_cold: bool = False,
    is_lactating: bool = False,
) -> float:
    bmr_h = bmr_kcal_h(mass_kg)
    total = 0.0
    total += loco_cost_hours(mass_kg, slope_avg, hours_locomotion)
    total += activity_kcal_h(mass_kg, 2.0) * hours_foraging
    total += activity_kcal_h(mass_kg, 1.0) * hours_resting
    total += activity_kcal_h(mass_kg, 1.5) * hours_other
    if is_cold:
        total += activity_kcal_h(mass_kg, 2.0) * 2.0
    if is_lactating:
        total *= 1.4
    return total


@dataclass
class EnergyBudget:
    mass_kg: float
    bmr_kcal_day: float = 0.0
    dee_kcal_day: float = 0.0
    intake_kcal_day: float = 0.0
    energy_reserve_kcal: float = 0.0
    energy_deficit_kcal: float = 0.0

    def __post_init__(self):
        self.bmr_kcal_day = bmr_kcal_day(self.mass_kg)
        self.dee_kcal_day = self.bmr_kcal_day * 2.5
        self.energy_reserve_kcal = self.mass_kg * 5000.0

    def intake_from_plant(self, kg_eaten: float, kcal_per_kg: float = 800.0) -> float:
        return kg_eaten * kcal_per_kg

    def intake_from_meat(self, kg_eaten: float, kcal_per_kg: float = 1500.0) -> float:
        return kg_eaten * kcal_per_kg

    def intake_from_invert(self, kg_eaten: float, kcal_per_kg: float = 2000.0) -> float:
        return kg_eaten * kcal_per_kg

    def net_energy(self, intake: float, expenditure: float) -> float:
        return intake - expenditure

    def update_reserve(self, net: float):
        self.energy_reserve_kcal += net
        if self.energy_reserve_kcal < 0:
            self.energy_deficit_kcal = -self.energy_reserve_kcal
