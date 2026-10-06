from __future__ import annotations
import random
import time
from pathlib import Path
from dataclasses import dataclass, field

from sim.grid import TerrainGrid, HABITAT_CODES, PISO_CODES
from sim.environment import Environment, default_snow_fn, default_temp_fn
from sim.agents import Agent, HerbivoreAgent, CarnivoreAgent, OmnivoreAgent
from sim.pools import PoolManager
from sim.pathfinding import a_star
from sim.io import log_line, export_snapshot_json, export_grid_to_csv


@dataclass
class PopulationConfig:
    species_key: str
    common_name: str
    count: int
    mass_kg: float
    trophic: str
    home_radius: int = 10


# Species habitat/piso preferences matching the Rust port
SPECIES_HABITAT: dict[str, tuple[list[int], list[int]]] = {
    "Rupicapra_pyrenaica": (
        [HABITAT_CODES["PASTIZAL"], HABITAT_CODES["ROCA"]],
        [PISO_CODES["Alpino"]],
    ),
    "Cervus_elaphus": (
        [HABITAT_CODES["BOSQUE_CAD"], HABITAT_CODES["PASTIZAL"]],
        [PISO_CODES["Montano"]],
    ),
    "Capreolus_capreolus": (
        [
            HABITAT_CODES["BOSQUE_CON"],
            HABITAT_CODES["BOSQUE_CAD"],
            HABITAT_CODES["MATORRAL"],
        ],
        [PISO_CODES["Subalpino"]],
    ),
    "Sus_scrofa": (
        [HABITAT_CODES["BOSQUE_CAD"], HABITAT_CODES["BOSQUE_CON"]],
        [PISO_CODES["Montano"]],
    ),
    "Marmota_marmota": ([HABITAT_CODES["PASTIZAL"]], [PISO_CODES["Alpino"]]),
    "Oryctolagus_cuniculus": (
        [HABITAT_CODES["PASTIZAL"], HABITAT_CODES["MATORRAL"]],
        [PISO_CODES["Montano"]],
    ),
    "Sciurus_vulgaris": (
        [HABITAT_CODES["BOSQUE_CON"], HABITAT_CODES["BOSQUE_CAD"]],
        [PISO_CODES["Montano"], PISO_CODES["Subalpino"]],
    ),
    "Vulpes_vulpes": ([], []),
    "Meles_meles": (
        [HABITAT_CODES["BOSQUE_CON"], HABITAT_CODES["BOSQUE_CAD"]],
        [PISO_CODES["Montano"], PISO_CODES["Subalpino"]],
    ),
    "Martes_martes": (
        [HABITAT_CODES["BOSQUE_CON"], HABITAT_CODES["BOSQUE_CAD"]],
        [PISO_CODES["Montano"], PISO_CODES["Subalpino"]],
    ),
    "Felis_silvestris": (
        [HABITAT_CODES["BOSQUE_CON"], HABITAT_CODES["BOSQUE_CAD"]],
        [PISO_CODES["Montano"], PISO_CODES["Subalpino"]],
    ),
    "Mustela_erminea": (
        [HABITAT_CODES["PASTIZAL"], HABITAT_CODES["ROCA"]],
        [PISO_CODES["Alpino"]],
    ),
    "Mustela_nivalis": ([], []),
    "Tetrao_urogallus": (
        [HABITAT_CODES["BOSQUE_CON"], HABITAT_CODES["MATORRAL"]],
        [PISO_CODES["Subalpino"]],
    ),
    "Lagopus_muta": (
        [HABITAT_CODES["PASTIZAL"], HABITAT_CODES["ROCA"]],
        [PISO_CODES["Alpino"]],
    ),
    "Corvus_corax": ([], []),
    "Gypaetus_barbatus": (
        [HABITAT_CODES["ROCA"]],
        [PISO_CODES["Montano"], PISO_CODES["Subalpino"], PISO_CODES["Alpino"]],
    ),
    "Aquila_chrysaetos": ([HABITAT_CODES["ROCA"]], []),
}

DEFAULT_POPULATIONS: list[PopulationConfig] = [
    PopulationConfig("Rupicapra_pyrenaica", "Isard", 1200, 35.0, "HERBIVORE", 8),
    PopulationConfig("Cervus_elaphus", "Cérvol", 350, 200.0, "HERBIVORE", 15),
    PopulationConfig("Capreolus_capreolus", "Cabirol", 500, 20.0, "HERBIVORE", 10),
    PopulationConfig("Sus_scrofa", "Senglar", 350, 100.0, "OMNIVORE", 12),
    PopulationConfig("Marmota_marmota", "Marmota", 400, 4.5, "HERBIVORE", 5),
    PopulationConfig("Oryctolagus_cuniculus", "Conill", 1200, 1.2, "HERBIVORE", 5),
    PopulationConfig("Sciurus_vulgaris", "Esquirol", 250, 0.3, "HERBIVORE", 3),
    PopulationConfig("Vulpes_vulpes", "Guineu", 120, 6.0, "OMNIVORE", 10),
    PopulationConfig("Meles_meles", "Teixó", 80, 11.0, "OMNIVORE", 8),
    PopulationConfig("Martes_martes", "Marta", 100, 1.5, "CARNIVORE", 8),
    PopulationConfig("Felis_silvestris", "Gat fer", 30, 4.0, "CARNIVORE", 10),
    PopulationConfig("Mustela_erminea", "Ermíni", 200, 0.15, "CARNIVORE", 3),
    PopulationConfig("Mustela_nivalis", "Mostela", 300, 0.08, "CARNIVORE", 3),
    PopulationConfig("Tetrao_urogallus", "Gall fer", 20, 4.0, "HERBIVORE", 5),
    PopulationConfig("Lagopus_muta", "Perdiu xerra", 40, 0.5, "HERBIVORE", 4),
    PopulationConfig("Corvus_corax", "Corb", 120, 1.0, "OMNIVORE", 10),
    PopulationConfig("Gypaetus_barbatus", "Trencalòs", 2, 5.5, "OMNIVORE", 20),
    PopulationConfig("Aquila_chrysaetos", "Àguila reial", 2, 4.0, "CARNIVORE", 25),
]


@dataclass
class Simulation:
    grid: TerrainGrid = field(default_factory=lambda: TerrainGrid(400, 400, 25))
    env: Environment = field(default_factory=Environment)
    pools: PoolManager = field(default_factory=PoolManager)
    agents: list[Agent] = field(default_factory=list)
    populations: list[PopulationConfig] = field(
        default_factory=lambda: DEFAULT_POPULATIONS
    )
    total_days: int = 3650
    log_every: int = 10
    snapshot_every: int = 100
    output_dir: Path = Path("output")
    agent_id_counter: int = 0

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.env.snow_fn = default_snow_fn
        self.env.temp_fn = default_temp_fn

    def initialize(self):
        self._init_terrain()
        self._init_pools()
        area_ha = (
            self.grid.width
            * self.grid.resolution_m
            * self.grid.height
            * self.grid.resolution_m
            / 10000
        )
        self._init_agents(area_ha=area_ha)

    @staticmethod
    def _scale_to_area(count: int, area_ha: float, reference_ha: float = 10000) -> int:
        return max(1, int(count * area_ha / reference_ha))

    def _init_terrain(self):
        from sim.io import (
            load_processed_terrain,
            load_habitat_to_grid,
            load_biomass_to_grid,
        )

        data_dir = Path(__file__).resolve().parent.parent.parent / "ecosystem" / "data"

        # Check if processed terrain data exists
        dem_path = data_dir / "terrain_dem_25m.tif"
        if dem_path.exists():
            print("  Loading processed terrain (DEM, slope, aspect, TRI, pisos)...")
            load_processed_terrain(
                self.grid,
                dem_path,
                data_dir / "terrain_slope.tif",
                data_dir / "terrain_aspect.tif",
                data_dir / "terrain_tri.tif",
                data_dir / "terrain_pisos.tif",
            )
        else:
            print("  No terrain data found, using flat defaults")
            for row in self.grid.cells:
                for cell in row:
                    cell.piso_bioclimatico = PISO_CODES["Montano"]

        # Load real habitat from MCSC if available
        habitat_path = data_dir / "terrain_habitat.tif"
        if habitat_path.exists():
            print("  Loading habitat map from MCSC data...")
            load_habitat_to_grid(self.grid, habitat_path)
        else:
            print("  No habitat map found, defaulting to PASTIZAL")
            for row in self.grid.cells:
                for cell in row:
                    cell.habitat_type = HABITAT_CODES["PASTIZAL"]

        # Load biomass data if available
        biomass_path = data_dir / "terrain_biomass.tif"
        if biomass_path.exists():
            print("  Loading biomass data from habitat-based assignment...")
            load_biomass_to_grid(self.grid, biomass_path)
        else:
            print("  No biomass data found, using random fallback")
            for row in self.grid.cells:
                for cell in row:
                    cell.biomass_P1 = random.uniform(0.3, 1.0)
                    cell.biomass_P2 = random.uniform(0.1, 0.5)
                    cell.biomass_P3 = random.uniform(0.5, 2.0)

        self.grid.update_costs()

    def _init_pools(self):
        self.pools = PoolManager()

    def _init_agents(self, area_ha: float = 10000):
        for pop in self.populations:
            scaled_count = self._scale_to_area(pop.count, area_ha)
            habitats, pisos = SPECIES_HABITAT.get(pop.species_key, ([], []))
            candidates = self.grid.find_spawn_cells(
                habitats=habitats if habitats else None,
                pisos=pisos if pisos else None,
            )
            for _ in range(scaled_count):
                if candidates:
                    x, y = random.choice(candidates)
                else:
                    x = random.randint(0, self.grid.width - 1)
                    y = random.randint(0, self.grid.height - 1)
                agent = self._create_agent(pop, x, y)
                if agent:
                    self.agents.append(agent)

    def _create_agent(self, pop: PopulationConfig, x: int, y: int) -> Agent | None:
        aid = self.agent_id_counter
        self.agent_id_counter += 1
        if pop.trophic == "HERBIVORE":
            return HerbivoreAgent(
                aid, pop.species_key, pop.common_name, pop.mass_kg, x, y
            )
        elif pop.trophic == "CARNIVORE":
            return CarnivoreAgent(
                aid, pop.species_key, pop.common_name, pop.mass_kg, x, y
            )
        elif pop.trophic == "OMNIVORE":
            return OmnivoreAgent(
                aid, pop.species_key, pop.common_name, pop.mass_kg, x, y
            )
        return None

    def run(self):
        log_header = "day,n_alive,n_dead,total_biomass,avg_energy"
        log_path = self.output_dir / "simulation_log.csv"
        with open(log_path, "w") as f:
            f.write(log_header + "\n")

        for day in range(self.total_days):
            self._step(day)
            if day % self.log_every == 0:
                self._log_state(day, log_path)
            if day % self.snapshot_every == 0:
                self._snapshot(day)

    def _step(self, day: int):
        self.env.step()
        season = self.env.season
        snow = default_snow_fn(1500.0, day)

        # JIT-accelerated snow update
        try:
            from sim.grid import update_snow_jit

            arr = self.grid.get_biomass_arrays()
            update_snow_jit(arr["elevation_m"], arr["snow_cover"], day, 2400.0)
            self.grid.set_biomass_arrays(arr)
        except (ImportError, AttributeError):
            for row in self.grid.cells:
                for cell in row:
                    cell.snow_cover = default_snow_fn(cell.elevation_m, day)

        self.pools.step(self.grid, season, snow)

        alive_agents = [a for a in self.agents if a.is_alive]
        for agent in alive_agents:
            agent.step(self.grid, dt_hours=24.0)

        self._reproduce_agents(alive_agents, season)
        self._remove_dead()

        # JIT-accelerated cost update
        try:
            from sim.grid import update_costs_jit

            arr = self.grid.get_biomass_arrays()
            update_costs_jit(
                arr["cost_a_star"],
                arr["slope_deg"],
                arr["snow_cover"],
                arr["habitat_type"],
                self.grid.width,
                self.grid.height,
            )
            self.grid.set_biomass_arrays(arr)
        except (ImportError, AttributeError):
            self.grid.update_costs()

    def _reproduce_agents(self, alive_agents: list[Agent], season: str):
        if season not in ("spring", "summer"):
            return
        new_agents = []
        for agent in alive_agents:
            if agent.state.is_lactating and agent.state.days_since_reproduction < 60:
                n_births = random.randint(
                    agent.litter_size_min, agent.litter_size_max + 1
                )
                for _ in range(n_births):
                    child = self._create_offspring(agent)
                    if child:
                        new_agents.append(child)
                agent.state.is_lactating = False
        self.agents.extend(new_agents)

    def _create_offspring(self, parent: Agent) -> Agent | None:
        x = parent.state.x + random.randint(-2, 2)
        y = parent.state.y + random.randint(-2, 2)
        if not self.grid.in_bounds(x, y):
            return None
        aid = self.agent_id_counter
        self.agent_id_counter += 1
        mass = parent.mass_kg * random.uniform(0.05, 0.15)
        if parent.trophic_level == "HERBIVORE":
            return HerbivoreAgent(
                aid, parent.species_key, parent.common_name, mass, x, y
            )
        elif parent.trophic_level == "CARNIVORE":
            return CarnivoreAgent(
                aid, parent.species_key, parent.common_name, mass, x, y
            )
        else:
            return OmnivoreAgent(
                aid, parent.species_key, parent.common_name, mass, x, y
            )

    def _remove_dead(self):
        self.agents = [a for a in self.agents if a.is_alive]

    def _log_state(self, day: int, log_path: Path):
        n_alive = sum(1 for a in self.agents if a.is_alive)
        n_dead = len(self.agents) - n_alive
        total_bio = self.grid.total_plant_biomass() + self.grid.total_invert_biomass()
        avg_energy = sum(a.state.energy_kcal for a in self.agents if a.is_alive) / max(
            n_alive, 1
        )
        log_line(day, n_alive, n_dead, total_bio, avg_energy, log_path)
        print(
            f"Day {day}: alive={n_alive} dead={n_dead} biomass={total_bio:.0f}kg energy_avg={avg_energy:.0f}"
        )

    def _snapshot(self, day: int):
        snap_dir = self.output_dir / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap = {
            "plants": self.grid.total_plant_biomass(),
            "inverts": self.grid.total_invert_biomass(),
            "fish": self.pools.fish.biomass_truita + self.pools.fish.biomass_barb_roig,
            "herps": self.pools.herps.biomass_reptiles
            + self.pools.herps.biomass_amphibians,
            "passerines": self.pools.passerines.biomass,
            "micromammals": self.pools.micromammals.biomass,
            "bats": self.pools.bats.biomass,
        }
        export_snapshot_json(
            self.agents, snap, day, snap_dir / f"agents_day_{day:05d}.json"
        )

    def get_stats(self) -> dict:
        n_alive = sum(1 for a in self.agents if a.is_alive)
        species_counts = {}
        for a in self.agents:
            if a.is_alive:
                species_counts[a.species_key] = species_counts.get(a.species_key, 0) + 1
        return {
            "day": self.env.current_day,
            "agents_alive": n_alive,
            "agents_total": len(self.agents),
            "species_counts": species_counts,
            "plant_biomass_kg": round(self.grid.total_plant_biomass(), 1),
            "invert_biomass_kg": round(self.grid.total_invert_biomass(), 1),
        }
