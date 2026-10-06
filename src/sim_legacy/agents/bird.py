from __future__ import annotations

from sim.agents.base import Agent, AgentState
from sim.energy import EnergyBudget
from sim.grid import TerrainGrid


class BirdAgent(Agent):
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
            trophic_level="BIRD",
            state=AgentState(x=x, y=y, mass_kg=mass_kg),
            energy=EnergyBudget(mass_kg=mass_kg),
            **kwargs,
        )
        self.home_range_radius_cells = 20
        self.daily_distance_cells = 15
        self.speed_kmh = 3.0

    def _decide_actions(self, grid: TerrainGrid) -> list:
        actions = []
        cell = grid.cells[self.state.y][self.state.x]
        if cell.total_plant_biomass + cell.total_invert_biomass < 0.001:
            target = self.look_for_best_cell(grid, radius=15)
            if target != (self.state.x, self.state.y):
                from sim.agents.herbivore import MoveAction

                actions.append(MoveAction(target))
        from sim.agents.herbivore import ForageAction

        actions.append(ForageAction())
        return actions
