"""
Validación del terreno procesado: carga, estadísticas, integración en simulación.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sim_legacy.grid import TerrainGrid
from sim_legacy.io import load_processed_terrain
from sim_legacy.simulation import Simulation, PopulationConfig

DATA_DIR = Path("ecosystem/data")
GRID_W, GRID_H = 375, 502


def main():
    grid = TerrainGrid(GRID_W, GRID_H, resolution_m=25)

    print("Cargando datos procesados...")
    grid = load_processed_terrain(
        grid,
        DATA_DIR / "terrain_dem_25m.tif",
        DATA_DIR / "terrain_slope.tif",
        DATA_DIR / "terrain_aspect.tif",
        DATA_DIR / "terrain_tri.tif",
        DATA_DIR / "terrain_pisos.tif",
    )

    elevations = []
    slopes = []
    piso_counts = {}
    valid = 0
    for row in grid.cells:
        for c in row:
            if c.elevation_m > 0:
                valid += 1
                elevations.append(c.elevation_m)
                slopes.append(c.slope_deg)
                piso_counts[c.piso_bioclimatico] = (
                    piso_counts.get(c.piso_bioclimatico, 0) + 1
                )

    piso_names = {1: "Montano", 2: "Subalpino", 3: "Alpino", 4: "Nival"}

    print(f"\n{'=' * 60}")
    print(f"TERRENO CARGADO — Vall de Cardós")
    print(f"{'=' * 60}")
    print(f"  Grid: {grid.width} x {grid.height} = {grid.width * grid.height} celdas")
    print(f"  Válidas: {valid} ({100 * valid / (grid.width * grid.height):.0f}%)")
    print(
        f"  Elevación: {np.min(elevations):.0f} - {np.max(elevations):.0f} m (media {np.mean(elevations):.0f})"
    )
    print(
        f"  Pendiente: {np.min(slopes):.1f} - {np.max(slopes):.1f}° (media {np.mean(slopes):.1f})"
    )
    for pcode, pname in piso_names.items():
        cnt = piso_counts.get(pcode, 0)
        print(f"  {pname}: {cnt} ({100 * cnt / valid:.0f}%)")
    print(f"{'=' * 60}")

    print("\nInicializando simulación con 5 especies...")
    sim = Simulation(
        grid=grid,
        total_days=1,
        log_every=1,
        output_dir=Path("output/validation"),
        populations=[
            PopulationConfig("Rupicapra_pyrenaica", "Isard", 5, 35.0, "HERBIVORE", 8),
            PopulationConfig("Marmota_marmota", "Marmota", 5, 4.5, "HERBIVORE", 5),
            PopulationConfig("Vulpes_vulpes", "Guineu", 3, 6.0, "OMNIVORE", 10),
        ],
    )
    sim.initialize()
    print(f"  Agentes: {len(sim.agents)}")
    print(f"  Biomasa plantas: {grid.total_plant_biomass():.0f} kg")
    print(f"  Biomasa inverts: {grid.total_invert_biomass():.0f} kg")

    print("\nEjecutando 1 paso...")
    sim._step(0)

    alive = sum(1 for a in sim.agents if a.is_alive)
    print(f"  Vivos tras paso 1: {alive}/{len(sim.agents)}")
    print("\nValidación completada.")


if __name__ == "__main__":
    main()
