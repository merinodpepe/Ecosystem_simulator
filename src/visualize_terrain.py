#!/usr/bin/env python3
"""
Terrain Visualization — Alt Pirineu Ecosystem Simulator
Generates maps of terrain layers: DEM, slope, aspect, TRI, pisos, habitat, biomass.

Usage:
    python visualize_terrain.py                          # default: show all maps
    python visualize_terrain.py --output maps/           # save to directory
    python visualize_terrain.py --layer habitat          # single layer only
"""

import argparse
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import rasterio

matplotlib.use("Agg")  # non-interactive backend for file output

DATA_DIR = Path(__file__).resolve().parent.parent / "ecosystem" / "data"

HABITAT_NAMES = {
    0: "Sense dades",
    1: "Bosc de coníferes",
    2: "Bosc caducifoli",
    3: "Matollar",
    4: "Pasturatge",
    5: "Zona humida",
    6: "Roca",
    7: "Aigua",
    8: "Ribera",
    9: "Neu",
    10: "Antròpic",
}

HABITAT_COLORS = {
    0: "#cccccc",
    1: "#1a5e1a",  # BOSQUE_CON - dark green
    2: "#5e9e3a",  # BOSQUE_CAD - medium green
    3: "#b8d45a",  # MATORRAL - yellow-green
    4: "#f0e68c",  # PASTIZAL - khaki
    5: "#6ba3c7",  # HUMEDAL - light blue
    6: "#8b7355",  # ROCA - brown
    7: "#3182bd",  # AGUA - blue
    8: "#7ec8a4",  # RIBERA - teal
    9: "#ffffff",  # NIEVE - white
    10: "#de2d26",  # ANTROPICO - red
}

PISO_NAMES = {1: "Montà", 2: "Subalpí", 3: "Alpí", 4: "Nival"}
PISO_COLORS = {1: "#2e8b57", 2: "#9370db", 3: "#daa520", 4: "#e0e0e0"}


def load_raster(path: Path, band: int = 1) -> np.ndarray:
    with rasterio.open(path) as src:
        return src.read(band)


def create_dem_map(ax, dem: np.ndarray, title: str = "Elevació (m)"):
    im = ax.imshow(dem, cmap="terrain", aspect="auto")
    plt.colorbar(im, ax=ax, label="m", shrink=0.6)
    ax.set_title(title)
    ax.set_xlabel("Columna (cel·la)")
    ax.set_ylabel("Fila (cel·la)")


def create_slope_map(ax, slope: np.ndarray, title: str = "Pendent (°)"):
    im = ax.imshow(slope, cmap="YlOrRd", aspect="auto", vmin=0, vmax=60)
    plt.colorbar(im, ax=ax, label="°", shrink=0.6)
    ax.set_title(title)
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def create_aspect_map(ax, aspect: np.ndarray, title: str = "Orientació"):
    cmap = plt.cm.twilight
    cmap.set_bad("white")
    masked = np.ma.MaskedArray(aspect, aspect < 0)
    im = ax.imshow(masked, cmap=cmap, aspect="auto", vmin=0, vmax=360)
    plt.colorbar(im, ax=ax, label="°", shrink=0.6, ticks=[0, 90, 180, 270, 360])
    ax.set_title(title)
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def create_tri_map(ax, tri: np.ndarray, title: str = "Índex de Rugositat (TRI)"):
    im = ax.imshow(tri, cmap="Greys", aspect="auto")
    plt.colorbar(im, ax=ax, label="TRI", shrink=0.6)
    ax.set_title(title)
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def create_pisos_map(ax, piso: np.ndarray, title: str = "Pisos Bioclimàtics"):
    from matplotlib.colors import ListedColormap, BoundaryNorm

    vals = sorted(PISO_COLORS.keys())
    colors = [PISO_COLORS[v] for v in vals]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)
    im = ax.imshow(piso, cmap=cmap, norm=norm, aspect="auto")
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, ticks=[1, 2, 3, 4])
    cbar.ax.set_yticklabels([PISO_NAMES[i] for i in [1, 2, 3, 4]])
    ax.set_title(title)
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def create_habitat_map(ax, habitat: np.ndarray, title: str = "Hàbitats"):
    from matplotlib.colors import ListedColormap, BoundaryNorm

    vals = sorted([k for k in HABITAT_COLORS.keys() if k > 0])
    colors = [HABITAT_COLORS[k] for k in vals]
    # Add nodata color
    cmap = ListedColormap(["#cccccc"] + colors)
    all_vals = [0] + vals
    boundaries = [v - 0.5 for v in all_vals] + [max(all_vals) + 0.5]
    norm = BoundaryNorm(boundaries, cmap.N)
    im = ax.imshow(habitat, cmap=cmap, norm=norm, aspect="auto")
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, ticks=all_vals)
    cbar.ax.set_yticklabels([HABITAT_NAMES.get(v, "?") for v in all_vals])
    cbar.ax.tick_params(labelsize=7)
    ax.set_title(title)
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def create_biomass_map(ax, biomass: np.ndarray, band_name: str, title: str = None):
    im = ax.imshow(biomass, cmap="Greens", aspect="auto")
    plt.colorbar(im, ax=ax, label="kg", shrink=0.6)
    ax.set_title(title or f"Biomassa {band_name}")
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")


def main():
    p = argparse.ArgumentParser(description="Terrain visualization")
    p.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(DATA_DIR.parent.parent / "output" / "maps"),
        help="Output directory for map images",
    )
    p.add_argument("--layer", "-l", type=str, default="all",
                    choices=["all", "dem", "slope", "aspect", "tri", "pisos", "habitat", "biomass"])
    p.add_argument("--dpi", type=int, default=150, help="Image DPI")
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Terrain Visualization — Alt Pirineu")
    print("=" * 60)

    layers = {}

    if args.layer in ("all", "dem", "slope", "aspect", "tri", "pisos"):
        layers["dem"] = ("Elevació", load_raster(DATA_DIR / "terrain_dem_25m.tif"))
        layers["slope"] = (
            "Pendent",
            load_raster(DATA_DIR / "terrain_slope.tif"),
        )
        layers["aspect"] = (
            "Orientació",
            load_raster(DATA_DIR / "terrain_aspect.tif"),
        )
        layers["tri"] = ("TRI", load_raster(DATA_DIR / "terrain_tri.tif"))
        layers["pisos"] = (
            "Pisos",
            load_raster(DATA_DIR / "terrain_pisos.tif").astype(np.int32),
        )

    if args.layer in ("all", "habitat"):
        layers["habitat"] = (
            "Hàbitats",
            load_raster(DATA_DIR / "terrain_habitat.tif").astype(np.int32),
        )

    if args.layer in ("all", "biomass"):
        with rasterio.open(DATA_DIR / "terrain_biomass.tif") as src:
            bands = {
                "biomass_P1": src.read(1),
                "biomass_P2": src.read(2),
                "biomass_P3": src.read(3),
                "biomass_I1": src.read(4),
                "biomass_I2": src.read(5),
                "biomass_I3": src.read(6),
            }
            layers.update({k: (k, v) for k, v in bands.items()})

    if args.layer == "all":
        # Full dashboard: 3x3 grid
        fig, axes = plt.subplots(3, 3, figsize=(18, 16))
        fig.suptitle(
            "Parc Natural de l'Alt Pirineu — Vall de Cardós\nCartografia del Terreny",
            fontsize=16,
            fontweight="bold",
        )

        create_dem_map(axes[0, 0], layers["dem"][1])
        create_slope_map(axes[0, 1], layers["slope"][1])
        create_aspect_map(axes[0, 2], layers["aspect"][1])
        create_tri_map(axes[1, 0], layers["tri"][1])
        create_pisos_map(axes[1, 1], layers["pisos"][1])
        create_habitat_map(axes[1, 2], layers["habitat"][1])
        create_biomass_map(axes[2, 0], layers["biomass_P1"][1], "P1 (entomòfiles)")
        create_biomass_map(axes[2, 1], layers["biomass_P3"][1], "P3 (pastures)")
        create_biomass_map(axes[2, 2], layers["biomass_I1"][1], "I1 (pol·linitzadors)")

        plt.tight_layout()
        out_path = out_dir / "terrain_dashboard.png"
        plt.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
        print(f"  Saved: {out_path}")
        plt.close()

        # Also save individual maps
        for name, (title, data) in layers.items():
            fig, ax = plt.subplots(figsize=(8, 6))
            if name == "dem":
                create_dem_map(ax, data)
            elif name == "slope":
                create_slope_map(ax, data)
            elif name == "aspect":
                create_aspect_map(ax, data)
            elif name == "tri":
                create_tri_map(ax, data)
            elif name == "pisos":
                create_pisos_map(ax, data)
            elif name == "habitat":
                create_habitat_map(ax, data)
            elif name.startswith("biomass"):
                create_biomass_map(ax, data, name)
            plt.tight_layout()
            out_path = out_dir / f"terrain_{name}.png"
            plt.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
            print(f"  Saved: {out_path}")
            plt.close()

    else:
        # Single layer
        fig, ax = plt.subplots(figsize=(10, 8))
        name, data = list(layers.values())[0]
        if args.layer == "dem":
            create_dem_map(ax, data)
        elif args.layer == "slope":
            create_slope_map(ax, data)
        elif args.layer == "aspect":
            create_aspect_map(ax, data)
        elif args.layer == "tri":
            create_tri_map(ax, data)
        elif args.layer == "pisos":
            create_pisos_map(ax, data)
        elif args.layer == "habitat":
            create_habitat_map(ax, data)
        elif args.layer == "biomass":
            create_biomass_map(ax, data, "Total")
        plt.tight_layout()
        out_path = out_dir / f"terrain_{args.layer}.png"
        plt.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
        print(f"  Saved: {out_path}")
        plt.close()

    # Print summary statistics
    print(f"\n  Output directory: {out_dir}")
    print(f"  Grid: {data.shape[1]}x{data.shape[0]} celdas")
    print(f"  Resolución: 25 m")
    if "dem" in layers:
        dem = layers["dem"][1]
        valid = dem[dem > 0]
        print(f"  Elevación: {valid.min():.0f}-{valid.max():.0f} m (media {valid.mean():.0f} m)")
    if "habitat" in layers:
        hab = layers["habitat"][1]
        total = np.sum(hab > 0)
        for code in sorted([c for c in np.unique(hab) if c > 0]):
            count = np.sum(hab == code)
            print(f"    {HABITAT_NAMES.get(code, '?')}: {count:,} celdas ({100*count/total:.1f}%)")
    print("  Done!")


if __name__ == "__main__":
    main()
