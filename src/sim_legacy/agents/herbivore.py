from __future__ import annotations
import random

from sim.agents.base import Agent, AgentState
from sim.energy import EnergyBudget
from sim.grid import TerrainGrid
from sim.pathfinding import a_star
from sim.foodweb import HERBIVORE_DIETS


class HerbivoreAgent(Agent):
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
        diet = HERBIVORE_DIETS.get(species_key)
        super().__init__(
            agent_id=agent_id,
            species_key=species_key,
            common_name=common_name,
            mass_kg=mass_kg,
            trophic_level="HERBIVORE",
            state=AgentState(x=x, y=y, mass_kg=mass_kg),
            energy=EnergyBudget(mass_kg=mass_kg),
            **kwargs,
        )

    def _decide_actions(self, grid: TerrainGrid) -> list:
        actions = []
        cell = grid.cells[self.state.y][self.state.x]
        if cell.total_plant_biomass < 0.05 * self.mass_kg:
            target = self.look_for_best_cell(grid, radius=5)
            if target != (self.state.x, self.state.y):
                actions.append(MoveAction(target))
        actions.append(ForageAction())
        if self._should_reproduce():
            actions.append(ReproduceAction())
        return actions

    def _should_reproduce(self) -> bool:
        return (
            self.state.days_since_reproduction > self.reproductive_age_days
            and self.state.energy_kcal > self.mass_kg * 2000.0
            and not self.state.is_pregnant
        )


class MoveAction:
    def __init__(self, target: tuple[int, int]):
        self.target = target

    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        start = (agent.state.x, agent.state.y)
        path = a_star(grid, start, self.target, max_steps=500)
        if path and len(path) > 1:
            next_pos = path[1]
            agent.state.x, agent.state.y = next_pos


class ForageAction:
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        intake = agent.forage_on_cell(grid)
        calory_intake = intake * 800.0
        agent.state.calories_consumed_today += calory_intake
        agent.state.energy_kcal += calory_intake * 0.6


class ReproduceAction:
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        if not agent.state.is_pregnant:
            agent.state.is_pregnant = True
            agent.state.gestation_days = 0
