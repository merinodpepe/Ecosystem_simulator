import numpy as np
from numba import njit
from dataclasses import dataclass, field
from typing import Optional

HABITAT_CODES = {
    "BOSQUE_CON": 1,
    "BOSQUE_CAD": 2,
    "MATORRAL": 3,
    "PASTIZAL": 4,
    "HUMEDAL": 5,
    "ROCA": 6,
    "AGUA": 7,
    "RIBERA": 8,
    "NIEVE": 9,
    "ANTROPICO": 10,
}

HABITAT_NAMES = {v: k for k, v in HABITAT_CODES.items()}

PISO_CODES = {"Montano": 1, "Subalpino": 2, "Alpino": 3, "Nival": 4}


@dataclass
class Cell:
    x: int
    y: int
    elevation_m: float = 0.0
    slope_deg: float = 0.0
    aspect_deg: float = 0.0
    tri: float = 0.0
    piso_bioclimatico: int = 1
    habitat_type: int = 0
    snow_cover: float = 0.0
    is_water: bool = False
    is_riparian: bool = False
    cost_a_star: float = 1.0
    biomass_P1: float = 0.0
    biomass_P2: float = 0.0
    biomass_P3: float = 0.0
    biomass_I1: float = 0.0
    biomass_I2: float = 0.0
    biomass_I3: float = 0.0
    P1_max: float = 2.0
    P2_max: float = 1.5
    P3_max: float = 5.0

    @property
    def total_plant_biomass(self) -> float:
        return self.biomass_P1 + self.biomass_P2 + self.biomass_P3

    @property
    def total_invert_biomass(self) -> float:
        return self.biomass_I1 + self.biomass_I2 + self.biomass_I3


@njit(cache=True)
def slope_cost_factor(slope_deg: float) -> float:
    if slope_deg < 5.0:
        return 1.0
    elif slope_deg < 15.0:
        return 1.5
    elif slope_deg < 30.0:
        return 2.5
    else:
        return 3.5


class TerrainGrid:
    def __init__(self, width: int, height: int, resolution_m: int = 25):
        self.width = width
        self.height = height
        self.resolution_m = resolution_m
        self.cells: list[list[Cell]] = [
            [Cell(x=x, y=y) for x in range(width)] for y in range(height)
        ]

    def _cell(self, x: int, y: int) -> Cell:
        return self.cells[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbors(self, x: int, y: int, diagonal: bool = True) -> list[tuple[int, int]]:
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonal:
            offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [
            (x + dx, y + dy) for dx, dy in offsets if self.in_bounds(x + dx, y + dy)
        ]

    def update_costs(self):
        for row in self.cells:
            for c in row:
                base = slope_cost_factor(c.slope_deg)
                snow_factor = 1.0 + c.snow_cover
                terrain_factor = 1.0
                habitat = c.habitat_type
                if habitat in (
                    HABITAT_CODES["BOSQUE_CON"],
                    HABITAT_CODES["BOSQUE_CAD"],
                ):
                    terrain_factor = 1.3
                elif habitat == HABITAT_CODES["ROCA"]:
                    terrain_factor = 1.6
                elif habitat == HABITAT_CODES["AGUA"]:
                    terrain_factor = 3.0
                elif habitat == HABITAT_CODES["ANTROPICO"]:
                    terrain_factor = 1.2
                c.cost_a_star = base * snow_factor * terrain_factor

    def get_cost_array(self) -> np.ndarray:
        arr = np.zeros((self.height, self.width), dtype=np.float32)
        for y in range(self.height):
            for x in range(self.width):
                arr[y, x] = self.cells[y][x].cost_a_star
        return arr

    def get_elevation_array(self) -> np.ndarray:
        arr = np.zeros((self.height, self.width), dtype=np.float32)
        for y in range(self.height):
            for x in range(self.width):
                arr[y, x] = self.cells[y][x].elevation_m
        return arr

    def get_habitat_array(self) -> np.ndarray:
        arr = np.zeros((self.height, self.width), dtype=np.int32)
        for y in range(self.height):
            for x in range(self.width):
                arr[y, x] = self.cells[y][x].habitat_type
        return arr

    def find_spawn_cells(
        self, habitats: list[int] | None = None, pisos: list[int] | None = None
    ) -> list[tuple[int, int]]:
        cells: list[tuple[int, int]] = []
        for row in self.cells:
            for c in row:
                if c.is_water:
                    continue
                habitat_ok = habitats is None or c.habitat_type in habitats
                piso_ok = pisos is None or c.piso_bioclimatico in pisos
                if habitat_ok and piso_ok:
                    cells.append((c.x, c.y))
        return cells

    def total_plant_biomass(self) -> float:
        return sum(c.total_plant_biomass for row in self.cells for c in row)

    def total_invert_biomass(self) -> float:
        return sum(c.total_invert_biomass for row in self.cells for c in row)

    def count_water_cells(self) -> int:
        return sum(1 for row in self.cells for c in row if c.is_water)

    # ---- Numpy array extractors for JIT-accelerated operations ----

    def get_biomass_arrays(self) -> dict:
        """Extract all biomass arrays as numpy 2D arrays."""
        h, w = self.height, self.width
        out = {
            "biomass_P1": np.zeros((h, w), dtype=np.float32),
            "biomass_P2": np.zeros((h, w), dtype=np.float32),
            "biomass_P3": np.zeros((h, w), dtype=np.float32),
            "biomass_I1": np.zeros((h, w), dtype=np.float32),
            "biomass_I2": np.zeros((h, w), dtype=np.float32),
            "biomass_I3": np.zeros((h, w), dtype=np.float32),
            "P1_max": np.zeros((h, w), dtype=np.float32),
            "P2_max": np.zeros((h, w), dtype=np.float32),
            "P3_max": np.zeros((h, w), dtype=np.float32),
            "elevation_m": np.zeros((h, w), dtype=np.float32),
            "slope_deg": np.zeros((h, w), dtype=np.float32),
            "habitat_type": np.zeros((h, w), dtype=np.int32),
            "snow_cover": np.zeros((h, w), dtype=np.float32),
            "is_water": np.zeros((h, w), dtype=np.int32),
            "cost_a_star": np.zeros((h, w), dtype=np.float32),
        }
        for y in range(h):
            for x in range(w):
                c = self.cells[y][x]
                out["biomass_P1"][y, x] = c.biomass_P1
                out["biomass_P2"][y, x] = c.biomass_P2
                out["biomass_P3"][y, x] = c.biomass_P3
                out["biomass_I1"][y, x] = c.biomass_I1
                out["biomass_I2"][y, x] = c.biomass_I2
                out["biomass_I3"][y, x] = c.biomass_I3
                out["P1_max"][y, x] = c.P1_max
                out["P2_max"][y, x] = c.P2_max
                out["P3_max"][y, x] = c.P3_max
                out["elevation_m"][y, x] = c.elevation_m
                out["slope_deg"][y, x] = c.slope_deg
                out["habitat_type"][y, x] = c.habitat_type
                out["snow_cover"][y, x] = c.snow_cover
                out["is_water"][y, x] = int(c.is_water)
                out["cost_a_star"][y, x] = c.cost_a_star
        return out

    def set_biomass_arrays(self, arr: dict):
        """Write back numpy arrays to Cell objects."""
        h, w = self.height, self.width
        for y in range(h):
            for x in range(w):
                c = self.cells[y][x]
                c.biomass_P1 = float(arr["biomass_P1"][y, x])
                c.biomass_P2 = float(arr["biomass_P2"][y, x])
                c.biomass_P3 = float(arr["biomass_P3"][y, x])
                c.biomass_I1 = float(arr["biomass_I1"][y, x])
                c.biomass_I2 = float(arr["biomass_I2"][y, x])
                c.biomass_I3 = float(arr["biomass_I3"][y, x])
                c.snow_cover = float(arr["snow_cover"][y, x])
                c.cost_a_star = float(arr["cost_a_star"][y, x])


@njit(cache=True)
def step_plants_jit(
    biomass_P1,
    biomass_P2,
    biomass_P3,
    P1_max,
    P2_max,
    P3_max,
    habitat_type,
    snow_cover,
    is_water,
    P1_growth_rate,
    P2_growth_rate,
    P3_growth_rate,
    growth_mod: float,
):
    """Numba JIT: update plant biomass for all cells."""
    h, w = biomass_P1.shape
    for y in range(h):
        for x in range(w):
            if is_water[y, x] or snow_cover[y, x] > 0.5:
                continue
            if habitat_type[y, x] == 6:  # ROCA
                continue
            biomass_P1[y, x] += P1_growth_rate * growth_mod * P1_max[y, x]
            biomass_P2[y, x] += P2_growth_rate * growth_mod * P2_max[y, x]
            biomass_P3[y, x] += P3_growth_rate * growth_mod * P3_max[y, x]
            # Clamp
            if biomass_P1[y, x] > P1_max[y, x]:
                biomass_P1[y, x] = P1_max[y, x]
            if biomass_P2[y, x] > P2_max[y, x]:
                biomass_P2[y, x] = P2_max[y, x]
            if biomass_P3[y, x] > P3_max[y, x]:
                biomass_P3[y, x] = P3_max[y, x]
            if biomass_P1[y, x] < 0.0:
                biomass_P1[y, x] = 0.0
            if biomass_P2[y, x] < 0.0:
                biomass_P2[y, x] = 0.0
            if biomass_P3[y, x] < 0.0:
                biomass_P3[y, x] = 0.0


@njit(cache=True)
def step_inverts_jit(
    biomass_I1,
    biomass_I2,
    biomass_I3,
    biomass_P1,
    biomass_P3,
    snow_cover,
    is_water,
    I1_growth_rate,
    I2_growth_rate,
    I3_growth_rate,
    I1_max,
    I2_max,
    I3_max,
    growth_mod: float,
):
    """Numba JIT: update invertebrate biomass for all cells."""
    h, w = biomass_I1.shape
    for y in range(h):
        for x in range(w):
            if is_water[y, x] or snow_cover[y, x] > 0.5:
                continue
            biomass_I1[y, x] += I1_growth_rate * growth_mod * biomass_P1[y, x] * 0.1
            biomass_I2[y, x] += I2_growth_rate * growth_mod * biomass_P3[y, x] * 0.08
            biomass_I3[y, x] += I3_growth_rate * growth_mod * biomass_I2[y, x] * 0.2
            # Clamp
            if biomass_I1[y, x] > I1_max:
                biomass_I1[y, x] = I1_max
            if biomass_I2[y, x] > I2_max:
                biomass_I2[y, x] = I2_max
            if biomass_I3[y, x] > I3_max:
                biomass_I3[y, x] = I3_max
            if biomass_I1[y, x] < 0.0:
                biomass_I1[y, x] = 0.0
            if biomass_I2[y, x] < 0.0:
                biomass_I2[y, x] = 0.0
            if biomass_I3[y, x] < 0.0:
                biomass_I3[y, x] = 0.0


@njit(cache=True)
def update_snow_jit(
    elevation_m,
    snow_cover,
    day: int,
    snow_line_base: float,
):
    """Numba JIT: update snow cover for all cells."""
    doy = day % 365
    # Simple cosine model
    season_amplitude = np.cos(2 * np.pi * (doy - 15) / 365)
    snow_line = snow_line_base + 600 * (season_amplitude + 1) / 2
    h, w = elevation_m.shape
    for y in range(h):
        for x in range(w):
            if elevation_m[y, x] < snow_line:
                snow_cover[y, x] = 0.0
            else:
                snow_cover[y, x] = min(1.0, (elevation_m[y, x] - snow_line) / 800.0)


@njit(cache=True)
def update_costs_jit(
    cost_a_star,
    slope_deg,
    snow_cover,
    habitat_type,
    width: int,
    height: int,
):
    """Numba JIT: update pathfinding costs for all cells."""
    for y in range(height):
        for x in range(width):
            s = slope_deg[y, x]
            if s < 5.0:
                base = 1.0
            elif s < 15.0:
                base = 1.5
            elif s < 30.0:
                base = 2.5
            else:
                base = 3.5
            snow_factor = 1.0 + snow_cover[y, x]
            htype = habitat_type[y, x]
            if htype == 1 or htype == 2:  # BOSQUE_CON, BOSQUE_CAD
                terrain_factor = 1.3
            elif htype == 6:  # ROCA
                terrain_factor = 1.6
            elif htype == 7:  # AGUA
                terrain_factor = 3.0
            elif htype == 10:  # ANTROPICO
                terrain_factor = 1.2
            else:
                terrain_factor = 1.0
            cost_a_star[y, x] = base * snow_factor * terrain_factor
