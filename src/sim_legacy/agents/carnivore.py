from __future__ import annotations
import random

from sim.agents.base import Agent, AgentState
from sim.energy import EnergyBudget
from sim.grid import TerrainGrid
from sim.pathfinding import a_star
from sim.foodweb import CARNIVORE_DIETS


class CarnivoreAgent(Agent):
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
            trophic_level="CARNIVORE",
            state=AgentState(x=x, y=y, mass_kg=mass_kg),
            energy=EnergyBudget(mass_kg=mass_kg),
            **kwargs,
        )

    def _decide_actions(self, grid: TerrainGrid) -> list:
        actions = []
        target_prey = self._detect_prey(grid)
        if target_prey:
            actions.append(HuntAction(target_prey))
        else:
            wander_target = self._wander_target(grid)
            actions.append(MoveToAction(wander_target))
        if self._should_reproduce():
            actions.append(ReproduceAction())
        return actions

    def _detect_prey(self, grid: TerrainGrid) -> tuple[int, int] | None:
        cx, cy = self.state.x, self.state.y
        radius = 8
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if not grid.in_bounds(nx, ny):
                    continue
                cell = grid.cells[ny][nx]
                if cell.total_invert_biomass > 0.1:
                    return (nx, ny)
        return None

    def _wander_target(self, grid: TerrainGrid) -> tuple[int, int]:
        cx, cy = self.state.x, self.state.y
        for _ in range(20):
            nx = cx + random.randint(-5, 5)
            ny = cy + random.randint(-5, 5)
            if grid.in_bounds(nx, ny):
                return (nx, ny)
        return (cx, cy)

    def _should_reproduce(self) -> bool:
        return (
            self.state.days_since_reproduction > self.reproductive_age_days
            and self.state.energy_kcal > self.mass_kg * 3000.0
            and not self.state.is_pregnant
        )


class HuntAction:
    def __init__(self, prey_pos: tuple[int, int]):
        self.prey_pos = prey_pos

    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        start = (agent.state.x, agent.state.y)
        path = a_star(grid, start, self.prey_pos, max_steps=3000)
        if path and len(path) > 1:
            agent.state.x, agent.state.y = path[1]
            if path[-1] == self.prey_pos:
                cell = grid.cells[agent.state.y][agent.state.x]
                kill = cell.total_invert_biomass * 0.3
                agent.state.energy_kcal += kill * 2000.0 * 0.8


class MoveToAction:
    def __init__(self, target: tuple[int, int]):
        self.target = target

    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        start = (agent.state.x, agent.state.y)
        path = a_star(grid, start, self.target, max_steps=2000)
        if path and len(path) > 1:
            agent.state.x, agent.state.y = path[1]


class ReproduceAction:
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        if not agent.state.is_pregnant:
            agent.state.is_pregnant = True
            agent.state.gestation_days = 0
