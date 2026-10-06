from __future__ import annotations
import random

from sim.agents.base import Agent, AgentState
from sim.agents.herbivore import ForageAction, MoveAction, ReproduceAction
from sim.agents.carnivore import HuntAction, MoveToAction
from sim.energy import EnergyBudget
from sim.grid import TerrainGrid
from sim.pathfinding import a_star
from sim.foodweb import OMNIVORE_DIETS


class OmnivoreAgent(Agent):
    def __init__(
        self,
        agent_id: int,
        species_key: str,
        common_name: str,
        mass_kg: float,
        x: int,
        y: int,
        **kwargs,
    ):
        super().__init__(
            agent_id=agent_id,
            species_key=species_key,
            common_name=common_name,
            mass_kg=mass_kg,
            trophic_level="OMNIVORE",
            state=AgentState(x=x, y=y, mass_kg=mass_kg),
            energy=EnergyBudget(mass_kg=mass_kg),
            **kwargs,
        )

    def _decide_actions(self, grid: TerrainGrid) -> list:
        actions = []
        cell = grid.cells[self.state.y][self.state.x]
        if cell.total_plant_biomass > 0.1 or cell.total_invert_biomass > 0.01:
            actions.append(ForageAction())
        else:
            target = self._search_food(grid)
            actions.append(MoveAction(target))
        if self._should_reproduce():
            actions.append(ReproduceAction())
        return actions

    def _search_food(self, grid: TerrainGrid) -> tuple[int, int]:
        cx, cy = self.state.x, self.state.y
        best = (cx, cy)
        best_score = 0.0
        for dy in range(-10, 11):
            for dx in range(-10, 11):
                nx, ny = cx + dx, cy + dy
                if not grid.in_bounds(nx, ny):
                    continue
                cell = grid.cells[ny][nx]
                score = cell.total_plant_biomass + cell.total_invert_biomass * 2.0
                if score > best_score:
                    best_score = score
                    best = (nx, ny)
        return best

    def _should_reproduce(self) -> bool:
        return (
            self.state.days_since_reproduction > self.reproductive_age_days
            and self.state.energy_kcal > self.mass_kg * 2500.0
            and not self.state.is_pregnant
        )
