import numpy as np
from numba import njit
from dataclasses import dataclass, field

from sim.grid import TerrainGrid, HABITAT_CODES


@dataclass
class PlantPool:
    P1_growth_rate: float = 0.02
    P2_growth_rate: float = 0.015
    P3_growth_rate: float = 0.03
    P1_max_per_cell: float = 2.0
    P2_max_per_cell: float = 1.5
    P3_max_per_cell: float = 5.0

    def step(self, grid: TerrainGrid, snow_cover: float, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        try:
            # Use JIT-accelerated version
            from sim.grid import step_plants_jit
            arr = grid.get_biomass_arrays()
            step_plants_jit(
                arr['biomass_P1'], arr['biomass_P2'], arr['biomass_P3'],
                arr['P1_max'], arr['P2_max'], arr['P3_max'],
                arr['habitat_type'], arr['snow_cover'], arr['is_water'],
                self.P1_growth_rate, self.P2_growth_rate, self.P3_growth_rate,
                growth_mod,
            )
            grid.set_biomass_arrays(arr)
        except (ImportError, AttributeError):
            # Fallback to pure Python
            for row in grid.cells:
                for cell in row:
                    if cell.is_water or cell.snow_cover > 0.5:
                        continue
                    if cell.habitat_type == HABITAT_CODES["ROCA"]:
                        continue
                    cell.biomass_P1 += self.P1_growth_rate * growth_mod * cell.P1_max
                    cell.biomass_P2 += self.P2_growth_rate * growth_mod * cell.P2_max
                    cell.biomass_P3 += self.P3_growth_rate * growth_mod * cell.P3_max
                    cell.biomass_P1 = min(cell.biomass_P1, cell.P1_max)
                    cell.biomass_P2 = min(cell.biomass_P2, cell.P2_max)
                    cell.biomass_P3 = min(cell.biomass_P3, cell.P3_max)
                    cell.biomass_P1 = max(cell.biomass_P1, 0.0)
                    cell.biomass_P2 = max(cell.biomass_P2, 0.0)
                    cell.biomass_P3 = max(cell.biomass_P3, 0.0)

    def get_totals(self, grid: TerrainGrid) -> dict[str, float]:
        return {
            "P1": sum(c.biomass_P1 for row in grid.cells for c in row),
            "P2": sum(c.biomass_P2 for row in grid.cells for c in row),
            "P3": sum(c.biomass_P3 for row in grid.cells for c in row),
        }


@dataclass
class InvertebratePool:
    I1_growth_rate: float = 0.01
    I2_growth_rate: float = 0.015
    I3_growth_rate: float = 0.008
    I1_max_per_cell: float = 0.5
    I2_max_per_cell: float = 0.8
    I3_max_per_cell: float = 0.3

    def step(self, grid: TerrainGrid, snow_cover: float, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        try:
            from sim.grid import step_inverts_jit
            arr = grid.get_biomass_arrays()
            step_inverts_jit(
                arr['biomass_I1'], arr['biomass_I2'], arr['biomass_I3'],
                arr['biomass_P1'], arr['biomass_P3'],
                arr['snow_cover'], arr['is_water'],
                self.I1_growth_rate, self.I2_growth_rate, self.I3_growth_rate,
                self.I1_max_per_cell, self.I2_max_per_cell, self.I3_max_per_cell,
                growth_mod,
            )
            grid.set_biomass_arrays(arr)
        except (ImportError, AttributeError):
            for row in grid.cells:
                for cell in row:
                    if cell.is_water or cell.snow_cover > 0.5:
                        continue
                    cell.biomass_I1 += (
                        self.I1_growth_rate * growth_mod * cell.biomass_P1 * 0.1
                    )
                    cell.biomass_I2 += (
                        self.I2_growth_rate * growth_mod * cell.biomass_P3 * 0.08
                    )
                    cell.biomass_I3 += (
                        self.I3_growth_rate * growth_mod * cell.biomass_I2 * 0.2
                    )
                    cell.biomass_I1 = min(cell.biomass_I1, self.I1_max_per_cell)
                    cell.biomass_I2 = min(cell.biomass_I2, self.I2_max_per_cell)
                    cell.biomass_I3 = min(cell.biomass_I3, self.I3_max_per_cell)
                    cell.biomass_I1 = max(cell.biomass_I1, 0.0)
                    cell.biomass_I2 = max(cell.biomass_I2, 0.0)
                    cell.biomass_I3 = max(cell.biomass_I3, 0.0)

    def get_totals(self, grid: TerrainGrid) -> dict[str, float]:
        return {
            "I1": sum(c.biomass_I1 for row in grid.cells for c in row),
            "I2": sum(c.biomass_I2 for row in grid.cells for c in row),
            "I3": sum(c.biomass_I3 for row in grid.cells for c in row),
        }


@dataclass
class FishPool:
    biomass_truita: float = 0.0
    biomass_barb_roig: float = 0.0
    growth_rate: float = 0.01
    carrying_capacity_per_km: float = 200.0

    def step(self, grid: TerrainGrid) -> None:
        water_cells = grid.count_water_cells()
        river_km = water_cells * grid.resolution_m / 1000.0
        max_fish = river_km * self.carrying_capacity_per_km
        self.biomass_truita += self.growth_rate * self.biomass_truita
        self.biomass_truita = min(self.biomass_truita, max_fish * 0.7)
        self.biomass_barb_roig += self.growth_rate * 1.5 * self.biomass_barb_roig
        self.biomass_barb_roig = min(self.biomass_barb_roig, max_fish * 0.3)
        self.biomass_truita = max(self.biomass_truita, 0.0)
        self.biomass_barb_roig = max(self.biomass_barb_roig, 0.0)


@dataclass
class HerpPool:
    biomass_reptiles: float = 0.0
    biomass_amphibians: float = 0.0
    growth_rate: float = 0.008

    def step(self, grid: TerrainGrid, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        self.biomass_reptiles += self.growth_rate * growth_mod * self.biomass_reptiles
        self.biomass_amphibians += (
            self.growth_rate * 1.2 * growth_mod * self.biomass_amphibians
        )
        self.biomass_reptiles = max(self.biomass_reptiles, 0.0)
        self.biomass_amphibians = max(self.biomass_amphibians, 0.0)


@dataclass
class PasserinePool:
    biomass: float = 0.0
    growth_rate: float = 0.01

    def step(self, grid: TerrainGrid, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        self.biomass += self.growth_rate * growth_mod * self.biomass
        self.biomass = max(self.biomass, 0.0)


@dataclass
class MicromammalPool:
    biomass: float = 0.0
    growth_rate: float = 0.02

    def step(self, grid: TerrainGrid, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        self.biomass += self.growth_rate * growth_mod * self.biomass
        self.biomass = max(self.biomass, 0.0)


@dataclass
class BatPool:
    biomass: float = 0.0
    growth_rate: float = 0.005

    def step(self, grid: TerrainGrid, season: str) -> None:
        growth_mod = _seasonal_growth_modifier(season)
        self.biomass += self.growth_rate * growth_mod * self.biomass
        self.biomass = max(self.biomass, 0.0)


def _seasonal_growth_modifier(season: str) -> float:
    if season == "summer":
        return 1.0
    elif season == "spring":
        return 0.8
    elif season == "autumn":
        return 0.5
    else:
        return 0.1


@dataclass
class PoolManager:
    plants: PlantPool = field(default_factory=PlantPool)
    invertebrates: InvertebratePool = field(default_factory=InvertebratePool)
    fish: FishPool = field(default_factory=FishPool)
    herps: HerpPool = field(default_factory=HerpPool)
    passerines: PasserinePool = field(default_factory=PasserinePool)
    micromammals: MicromammalPool = field(default_factory=MicromammalPool)
    bats: BatPool = field(default_factory=BatPool)

    def step(self, grid: TerrainGrid, season: str, snow: float) -> None:
        self.plants.step(grid, snow, season)
        self.invertebrates.step(grid, snow, season)
        self.fish.step(grid)
        self.herps.step(grid, season)
        self.passerines.step(grid, season)
        self.micromammals.step(grid, season)
        self.bats.step(grid, season)

    def total_biomass_kg(self) -> dict[str, float]:
        return {
            "plants": 0.0,
            "invertebrates": 0.0,
            "fish": self.fish.biomass_truita + self.fish.biomass_barb_roig,
            "herps": self.herps.biomass_reptiles + self.herps.biomass_amphibians,
            "passerines": self.passerines.biomass,
            "micromammals": self.micromammals.biomass,
            "bats": self.bats.biomass,
        }
