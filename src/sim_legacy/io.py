from __future__ import annotations
import csv
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from sim.grid import TerrainGrid, Cell


def load_dem_to_grid(
    grid: TerrainGrid,
    dem_path: str | Path,
    band: int = 1,
) -> TerrainGrid:
    import rasterio

    with rasterio.open(dem_path) as src:
        dem_data = src.read(band)
    for y in range(grid.height):
        for x in range(grid.width):
            if y < dem_data.shape[0] and x < dem_data.shape[1]:
                grid.cells[y][x].elevation_m = float(dem_data[y, x])
    return grid


def load_processed_terrain(
    grid: TerrainGrid,
    dem_path: str | Path,
    slope_path: str | Path,
    aspect_path: str | Path,
    tri_path: str | Path,
    piso_path: str | Path,
    nodata: float = -32768.0,
) -> TerrainGrid:
    import rasterio

    with rasterio.open(dem_path) as src:
        dem = src.read(1)
    with rasterio.open(slope_path) as src:
        slope = src.read(1)
    with rasterio.open(aspect_path) as src:
        aspect = src.read(1)
    with rasterio.open(tri_path) as src:
        tri = src.read(1)
    with rasterio.open(piso_path) as src:
        piso = src.read(1)

    for y in range(min(grid.height, dem.shape[0])):
        for x in range(min(grid.width, dem.shape[1])):
            ev = dem[y, x]
            if ev == nodata:
                continue
            c = grid.cells[y][x]
            c.elevation_m = float(ev)
            c.slope_deg = float(slope[y, x]) if slope[y, x] != nodata else 0.0
            c.aspect_deg = float(aspect[y, x]) if aspect[y, x] != nodata else 0.0
            c.tri = float(tri[y, x]) if tri[y, x] != nodata else 0.0
            c.piso_bioclimatico = int(piso[y, x]) if piso[y, x] != nodata else 1

    grid.update_costs()
    return grid


def load_habitat_to_grid(
    grid: TerrainGrid,
    habitat_path: str | Path,
    mapping: Optional[dict[int, int]] = None,
) -> TerrainGrid:
    import rasterio

    with rasterio.open(habitat_path) as src:
        hab_data = src.read(1)
    for y in range(grid.height):
        for x in range(grid.width):
            if y < hab_data.shape[0] and x < hab_data.shape[1]:
                val = int(hab_data[y, x])
                if mapping:
                    val = mapping.get(val, 0)
                grid.cells[y][x].habitat_type = val
    return grid


def load_biomass_to_grid(
    grid: TerrainGrid,
    biomass_path: str | Path,
    nodata: float = -9999.0,
) -> TerrainGrid:
    """
    Load biomass data from a 9-band GeoTIFF:
    Band 1: biomass_P1
    Band 2: biomass_P2
    Band 3: biomass_P3
    Band 4: biomass_I1
    Band 5: biomass_I2
    Band 6: biomass_I3
    Band 7: P1_max
    Band 8: P2_max
    Band 9: P3_max
    Also sets is_water for cells with habitat_type == AGUA (7).
    """
    import rasterio

    with rasterio.open(biomass_path) as src:
        p1 = src.read(1)
        p2 = src.read(2)
        p3 = src.read(3)
        i1 = src.read(4)
        i2 = src.read(5)
        i3 = src.read(6)
        p1m = src.read(7)
        p2m = src.read(8)
        p3m = src.read(9)

    for y in range(min(grid.height, p1.shape[0])):
        for x in range(min(grid.width, p1.shape[1])):
            if p1[y, x] == nodata:
                continue
            c = grid.cells[y][x]
            c.biomass_P1 = float(p1[y, x])
            c.biomass_P2 = float(p2[y, x])
            c.biomass_P3 = float(p3[y, x])
            c.biomass_I1 = float(i1[y, x])
            c.biomass_I2 = float(i2[y, x])
            c.biomass_I3 = float(i3[y, x])
            c.P1_max = float(p1m[y, x])
            c.P2_max = float(p2m[y, x])
            c.P3_max = float(p3m[y, x])
            if c.habitat_type == 7:  # AGUA
                c.is_water = True
    return grid


def export_grid_to_csv(grid: TerrainGrid, path: str | Path):
    fieldnames = [
        "x",
        "y",
        "elevation_m",
        "slope_deg",
        "aspect_deg",
        "tri",
        "piso",
        "habitat",
        "snow",
        "is_water",
        "cost_astar",
        "biomass_P1",
        "biomass_P2",
        "biomass_P3",
        "biomass_I1",
        "biomass_I2",
        "biomass_I3",
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in grid.cells:
            for c in row:
                w.writerow(
                    {
                        "x": c.x,
                        "y": c.y,
                        "elevation_m": c.elevation_m,
                        "slope_deg": c.slope_deg,
                        "aspect_deg": c.aspect_deg,
                        "tri": c.tri,
                        "piso": c.piso_bioclimatico,
                        "habitat": c.habitat_type,
                        "snow": c.snow_cover,
                        "is_water": int(c.is_water),
                        "cost_astar": c.cost_a_star,
                        "biomass_P1": c.biomass_P1,
                        "biomass_P2": c.biomass_P2,
                        "biomass_P3": c.biomass_P3,
                        "biomass_I1": c.biomass_I1,
                        "biomass_I2": c.biomass_I2,
                        "biomass_I3": c.biomass_I3,
                    }
                )


def load_vertebrates_tsv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def load_trophic_matrix(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def export_snapshot_json(
    agents: list,
    pools: dict,
    day: int,
    path: str | Path,
):
    data = {
        "day": day,
        "agents": [
            {
                "id": a.agent_id,
                "species_key": a.species_key,
                "nick": a.common_name,
                "guild": a.trophic_level,
                "x": a.state.x,
                "y": a.state.y,
                "alive": a.is_alive,
                "energy": round(a.state.energy_kcal, 1),
                "age": round(a.state.age_days, 1),
                "pregnant": a.state.is_pregnant,
            }
            for a in agents
        ],
        "pools": {k: round(v, 1) for k, v in pools.items()},
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log_line(
    day: int,
    n_alive: int,
    n_dead: int,
    total_biomass: float,
    avg_energy: float,
    path: str | Path,
):
    with open(path, "a") as f:
        f.write(f"{day},{n_alive},{n_dead},{total_biomass:.1f},{avg_energy:.1f}\n")
