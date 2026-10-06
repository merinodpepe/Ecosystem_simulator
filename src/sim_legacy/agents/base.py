from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Protocol

from sim.energy import EnergyBudget, daily_dee
from sim.grid import TerrainGrid


class AgentAction(Protocol):
    def execute(self, agent: Agent, grid: TerrainGrid) -> None: ...


@dataclass
class AgentState:
    x: int
    y: int
    mass_kg: float = 50.0
    energy_kcal: float = 0.0
    age_days: int = 0
    alive: bool = True
    is_pregnant: bool = False
    is_lactating: bool = False
    gestation_days: int = 0
    days_since_reproduction: int = 0
    calories_consumed_today: float = 0.0
    calories_spent_today: float = 0.0

    def __post_init__(self):
        if self.energy_kcal == 0.0:
            self.energy_kcal = self.mass_kg * 5000.0


@dataclass
class Agent:
    agent_id: int
    species_key: str
    common_name: str
    mass_kg: float
    trophic_level: str  # "HERBIVORE", "CARNIVORE", "OMNIVORE"
    state: AgentState
    energy: EnergyBudget

    home_range_radius_cells: int = 10
    daily_distance_cells: int = 5
    speed_kmh: float = 2.0
    gestation_days_total: int = 150
    litter_size_min: int = 1
    litter_size_max: int = 2
    reproductive_age_days: int = 365
    lifespan_days: int = 3650

    def __post_init__(self):
        self.energy = EnergyBudget(mass_kg=self.mass_kg)

    @property
    def is_alive(self) -> bool:
        return self.state.alive

    def step(
        self,
        grid: TerrainGrid,
        dt_hours: float = 24.0,
    ) -> list[AgentAction]:
        if not self.state.alive:
            return []

        actions = self._decide_actions(grid)
        self._execute_actions(actions, grid, dt_hours)
        self._update_energy(grid, dt_hours)
        self._update_biology(dt_hours)
        self._check_death(grid)
        return actions

    def _decide_actions(self, grid: TerrainGrid) -> list[AgentAction]:
        return []

    def _execute_actions(
        self,
        actions: list[AgentAction],
        grid: TerrainGrid,
        dt_hours: float,
    ) -> None:
        for action in actions:
            action.execute(self, grid)

    def _update_energy(self, grid: TerrainGrid, dt_hours: float) -> None:
        cell = grid.cells[self.state.y][self.state.x]
        slope = cell.slope_deg

        hours_loco = 2.0
        hours_forage = 6.0
        hours_rest = 12.0
        hours_other = 4.0

        expended = daily_dee(
            self.mass_kg,
            hours_forage,
            hours_loco,
            hours_rest,
            hours_other,
            slope,
            is_cold=False,
            is_lactating=self.state.is_lactating,
        )
        self.state.calories_spent_today = expended
        self.state.energy_kcal -= expended * (dt_hours / 24.0)

    def _update_biology(self, dt_hours: float) -> None:
        self.state.age_days += dt_hours / 24.0
        self.state.days_since_reproduction += dt_hours / 24.0
        if self.state.is_pregnant:
            self.state.gestation_days += dt_hours / 24.0
            if self.state.gestation_days >= self.gestation_days_total:
                self._give_birth()

    def _give_birth(self) -> None:
        self.state.is_pregnant = False
        self.state.gestation_days = 0
        self.state.days_since_reproduction = 0
        self.state.is_lactating = True

    def _check_death(self, grid: TerrainGrid) -> None:
        if self.state.energy_kcal <= 0.0:
            self.state.alive = False
        if self.state.age_days >= self.lifespan_days:
            self.state.alive = False

    def forage_on_cell(self, grid: TerrainGrid) -> float:
        cell = grid.cells[self.state.y][self.state.x]
        available = cell.total_plant_biomass + cell.total_invert_biomass
        intake = min(available, self.mass_kg * 0.05)
        plant_share = cell.total_plant_biomass / max(available, 1e-6)
        invert_share = 1.0 - plant_share
        cell.biomass_P1 -= intake * plant_share * 0.5
        cell.biomass_P2 -= intake * plant_share * 0.2
        cell.biomass_P3 -= intake * plant_share * 0.3
        cell.biomass_I1 -= intake * invert_share * 0.3
        cell.biomass_I2 -= intake * invert_share * 0.5
        cell.biomass_I3 -= intake * invert_share * 0.2
        return intake

    def look_for_best_cell(
        self,
        grid: TerrainGrid,
        radius: int = 5,
    ) -> tuple[int, int]:
        best_score = -1.0
        best_pos = (self.state.x, self.state.y)
        cx, cy = self.state.x, self.state.y
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if not grid.in_bounds(nx, ny):
                    continue
                cell = grid.cells[ny][nx]
                score = cell.total_plant_biomass + cell.total_invert_biomass * 2.0
                score /= max(cell.cost_a_star, 0.1)
                if score > best_score:
                    best_score = score
                    best_pos = (nx, ny)
        return best_pos
