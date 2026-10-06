#!/usr/bin/env python3
"""
High-quality terrain maps from terrain_cells.tsv.
Generates publication-ready maps: DEM, slope, aspect, TRI, pisos, hillshade.

Usage:
    python src/visualize_terrain_tsv.py [--output output/maps] [--dpi 300]
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

DATA_DIR = Path("ecosystem/data")
TSV_PATH = DATA_DIR / "terrain_cells.tsv"
HABITAT_PATH = DATA_DIR / "terrain_habitat.tif"

PISO_NAMES = {
    1: "Montà\n(650-1600 m)",
    2: "Subalpí\n(1600-2300 m)",
    3: "Alpí\n(2300-2700 m)",
    4: "Nival\n(>2700 m)",
}
PISO_COLORS_HEX = ["#2e8b57", "#9370db", "#daa520", "#e0e0e0"]

HABITAT_NAMES = {
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
HABITAT_COLORS_HEX = [
    "#cccccc",
    "#1a5e1a",
    "#5e9e3a",
    "#b8d45a",
    "#f0e68c",
    "#6ba3c7",
    "#8b7355",
    "#3182bd",
    "#7ec8a4",
    "#ffffff",
    "#de2d26",
]


def load_tsv_grid(path):
    """Load TSV and pivot to 2D grids preserving original layout."""
    df = pd.read_csv(path, sep="\t")
    W = df["x"].max() + 1
    H = df["y"].max() + 1
    grids = {}
    for col in ["elevation_m", "slope_deg", "aspect_deg", "tri", "piso"]:
        arr = np.full((H, W), np.nan)
        arr[df["y"].values, df["x"].values] = df[col].values
        grids[col] = arr
    return grids, W, H


def hillshade(elevation, az=315, alt=30):
    """Compute hillshade from elevation array."""
    x, y = np.gradient(elevation)
    slope = np.pi / 2.0 - np.arctan(np.sqrt(x * x + y * y))
    aspect = np.arctan2(-x, y)
    azimuth = np.radians(az)
    altitude = np.radians(alt)
    shaded = np.sin(altitude) * np.sin(slope) + np.cos(altitude) * np.cos(
        slope
    ) * np.cos(azimuth - aspect)
    return np.clip(shaded, 0, 1)


def add_scale_bar(ax, utm_x, utm_y, length_m=1000):
    """Add a scale bar in UTM coordinates."""
    x_min, x_max = utm_x.min(), utm_x.max()
    y_min = utm_y.min()
    bar_x_start = x_min + (x_max - x_min) * 0.05
    bar_x_end = bar_x_start + length_m
    bar_y = y_min + (utm_y.max() - y_min) * 0.03
    ax.plot([bar_x_start, bar_x_end], [bar_y, bar_y], color="black", linewidth=3)
    ax.text(
        (bar_x_start + bar_x_end) / 2,
        bar_y - (utm_y.max() - y_min) * 0.02,
        f"{length_m // 1000} km",
        ha="center",
        va="top",
        fontsize=9,
        fontweight="bold",
    )


def add_north_arrow(ax, utm_x, utm_y, size_ratio=0.04):
    """Add a north arrow."""
    x_min, x_max = utm_x.min(), utm_x.max()
    y_min, y_max = utm_y.min(), utm_y.max()
    dx = x_max - x_min
    dy = y_max - y_min
    cx = x_max - dx * 0.08
    cy = y_max - dy * 0.07
    s = min(dx, dy) * size_ratio
    ax.arrow(
        cx,
        cy,
        0,
        s,
        width=s * 0.25,
        head_width=s * 0.6,
        head_length=s * 0.35,
        fc="black",
        ec="black",
    )
    ax.text(
        cx, cy - s * 0.3, "N", ha="center", va="top", fontsize=11, fontweight="bold"
    )


def make_dem_map(ax, elev, utm_x, utm_y, shade):
    """Elevation map with hillshade overlay."""
    vmin, vmax = np.nanmin(elev), np.nanmax(elev)
    ax.imshow(
        shade,
        cmap="gray",
        alpha=0.35,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
    )
    im = ax.imshow(
        elev,
        cmap="terrain",
        alpha=0.75,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
        vmin=vmin,
        vmax=vmax,
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.65, pad=0.02)
    cbar.set_label("Elevació (m)", fontsize=10)
    ax.set_title(
        "Model Digital d'Elevacions (DEM)", fontsize=12, fontweight="bold", pad=8
    )
    _format_map_axes(ax, utm_x, utm_y)
    return im


def make_slope_map(ax, slope, utm_x, utm_y, shade):
    """Slope map with hillshade."""
    ax.imshow(
        shade,
        cmap="gray",
        alpha=0.3,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
    )
    im = ax.imshow(
        slope,
        cmap="YlOrRd",
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
        vmin=0,
        vmax=60,
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.65, pad=0.02)
    cbar.set_label("Pendent (°)", fontsize=10)
    ax.set_title("Pendent del Terreny", fontsize=12, fontweight="bold", pad=8)
    _format_map_axes(ax, utm_x, utm_y)


def make_aspect_map(ax, aspect, utm_x, utm_y):
    """Aspect map with cyclic colormap."""
    masked = np.ma.MaskedArray(aspect, aspect < 0)
    im = ax.imshow(
        masked,
        cmap="twilight",
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
        vmin=0,
        vmax=360,
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.65, pad=0.02, ticks=[0, 90, 180, 270, 360])
    cbar.set_label("Orientació (°)", fontsize=10)
    ax.set_title("Orientació del Terreny", fontsize=12, fontweight="bold", pad=8)
    _format_map_axes(ax, utm_x, utm_y)


def make_tri_map(ax, tri, utm_x, utm_y, shade):
    """TRI map."""
    ax.imshow(
        shade,
        cmap="gray",
        alpha=0.25,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
    )
    vmax = np.nanpercentile(tri, 98)
    im = ax.imshow(
        tri,
        cmap="Greys",
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
        vmin=0,
        vmax=vmax,
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.65, pad=0.02)
    cbar.set_label("TRI", fontsize=10)
    ax.set_title("Índex de Rugositat (TRI)", fontsize=12, fontweight="bold", pad=8)
    _format_map_axes(ax, utm_x, utm_y)


def make_pisos_map(ax, piso, utm_x, utm_y, shade):
    """Bioclimatic belts map."""
    from matplotlib.colors import ListedColormap, BoundaryNorm

    cmap = ListedColormap(PISO_COLORS_HEX)
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)
    ax.imshow(
        shade,
        cmap="gray",
        alpha=0.25,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
    )
    im = ax.imshow(
        piso,
        cmap=cmap,
        norm=norm,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02, ticks=[1, 2, 3, 4])
    cbar.ax.set_yticklabels(["Montà", "Subalpí", "Alpí", "Nival"])
    cbar.set_label("Pis Bioclimàtic", fontsize=10)
    ax.set_title("Pisos Bioclimàtics", fontsize=12, fontweight="bold", pad=8)
    _format_map_axes(ax, utm_x, utm_y)


def make_habitat_map(ax, hab, utm_x, utm_y):
    """Habitat classification map."""
    from matplotlib.colors import ListedColormap, BoundaryNorm

    all_vals = sorted([k for k in HABITAT_NAMES.keys()])
    colors = [HABITAT_COLORS_HEX[k] for k in [0] + all_vals]
    cmap = ListedColormap(colors)
    boundaries = [v - 0.5 for v in [0] + all_vals] + [max(all_vals) + 0.5]
    norm = BoundaryNorm(boundaries, cmap.N)

    hab_disp = np.where(hab == 0, np.nan, hab)
    im = ax.imshow(
        hab_disp,
        cmap=cmap,
        norm=norm,
        aspect="auto",
        extent=[utm_x[0], utm_x[-1], utm_y[-1], utm_y[0]],
        interpolation="none",
    )
    cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02, ticks=all_vals)
    cbar.ax.set_yticklabels([HABITAT_NAMES[v] for v in all_vals])
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("Tipus d'Hàbitat", fontsize=10)
    ax.set_title("Mapa d'Hàbitats", fontsize=12, fontweight="bold", pad=8)
    _format_map_axes(ax, utm_x, utm_y)


def _format_map_axes(ax, utm_x, utm_y):
    ax.set_xlabel("UTM Easting (m)", fontsize=9)
    ax.set_ylabel("UTM Northing (m)", fontsize=9)
    ax.ticklabel_format(style="scientific", scilimits=(5, 5), axis="both")
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())


def compute_utm_coords(_df, W, H):
    """Build UTM coordinate arrays from TSV data."""
    utm_x = np.full(W, np.nan)
    utm_y = np.full(H, np.nan)
    for y in range(H):
        row = _df[_df["y"] == y]
        if len(row) > 0:
            utm_y[y] = row["utm_y"].iloc[0]
    for x in range(W):
        col = _df[_df["x"] == x]
        if len(col) > 0:
            utm_x[x] = col["utm_x"].iloc[0]
    xs = np.where(np.isnan(utm_x), np.nanmean(utm_x), utm_x)
    ys = np.where(np.isnan(utm_y), np.nanmean(utm_y), utm_y)
    return xs, ys[::-1]


def main():
    p = argparse.ArgumentParser(
        description="Generate high-quality terrain maps from TSV"
    )
    p.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(Path("output/maps")),
        help="Output directory",
    )
    p.add_argument("--dpi", type=int, default=250, help="Image DPI")
    p.add_argument(
        "--maps",
        "-m",
        type=str,
        nargs="+",
        choices=[
            "all",
            "dem",
            "slope",
            "aspect",
            "tri",
            "pisos",
            "habitat",
            "dashboard",
        ],
        default=["all"],
        help="Which maps to generate",
    )
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  TERRAIN TSV MAP GENERATOR")
    print("=" * 60)

    print("\nLoading TSV...")
    df = pd.read_csv(TSV_PATH, sep="\t")
    W, H = df["x"].max() + 1, df["y"].max() + 1
    print(f"  Grid: {W} x {H} = {W * H} cells, {len(df)} valid")

    print("Building grids...")
    grids, _, _ = load_tsv_grid(TSV_PATH)

    print("Computing hillshade...")
    elev_filled = np.where(
        np.isnan(grids["elevation_m"]),
        np.nanmean(grids["elevation_m"]),
        grids["elevation_m"],
    )
    shade = hillshade(elev_filled, az=315, alt=30)

    print("Computing UTM coordinates...")
    xs, ys = compute_utm_coords(df, W, H)
    extent = [xs[0], xs[-1], ys[-1], ys[0]]

    # Try loading habitat
    hab_data = None
    try:
        import rasterio

        with rasterio.open(HABITAT_PATH) as src:
            hab_data = src.read(1)
        print("  Habitat data loaded")
    except Exception:
        print("  No habitat data found, skipping habitat map")

    want = set(args.maps)

    # --- Individual maps ---
    def _save(name, fig):
        path = out_dir / f"terrain_{name}.png"
        fig.savefig(path, dpi=args.dpi, bbox_inches="tight")
        print(
            f"  Saved: {path} ({fig.get_size_inches()[0]:.0f}x{fig.get_size_inches()[1]:.0f} in)"
        )
        plt.close(fig)

    maps = {
        "dem": (
            "DEM",
            lambda ax: make_dem_map(ax, grids["elevation_m"], xs, ys, shade),
        ),
        "slope": (
            "Pendent",
            lambda ax: make_slope_map(ax, grids["slope_deg"], xs, ys, shade),
        ),
        "aspect": (
            "Orientació",
            lambda ax: make_aspect_map(ax, grids["aspect_deg"], xs, ys),
        ),
        "tri": ("TRI", lambda ax: make_tri_map(ax, grids["tri"], xs, ys, shade)),
        "pisos": ("Pisos", lambda ax: make_pisos_map(ax, grids["piso"], xs, ys, shade)),
    }
    if hab_data is not None:
        maps["habitat"] = (
            "Hàbitats",
            lambda ax: make_habitat_map(ax, hab_data, xs, ys),
        )

    for key, (name, draw_fn) in maps.items():
        if "all" not in want and key not in want:
            continue
        print(f"\n[{name}]")
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor("white")
        draw_fn(ax)
        add_scale_bar(ax, xs, ys, 1000)
        add_north_arrow(ax, xs, ys)
        _save(key, fig)

    # --- Dashboard ---
    if "all" in want or "dashboard" in want:
        print("\n[Dashboard]")
        keys = list(maps.keys())
        n = len(keys)
        if n <= 3:
            rows, cols = 1, n
        elif n <= 6:
            rows, cols = 2, 3
        else:
            rows, cols = 3, 3

        fig, axes = plt.subplots(
            rows, cols, figsize=(6 * cols, 5 * rows), constrained_layout=True
        )
        axes = axes.flatten() if rows * cols > 1 else [axes]

        fig.suptitle(
            "Parc Natural de l'Alt Pirineu — Vall de Cardós\nCartografia del Terreny (25 m)",
            fontsize=16,
            fontweight="bold",
            y=1.02,
        )

        for i, (key, (name, draw_fn)) in enumerate(maps.items()):
            if i < len(axes):
                draw_fn(axes[i])
                if i % cols != 0:
                    axes[i].set_ylabel("")
                if i < len(keys) - cols:
                    axes[i].set_xlabel("")

        for j in range(len(maps), len(axes)):
            axes[j].axis("off")

        _save("dashboard", fig)

    # --- Statistical summary ---
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    elev_valid = grids["elevation_m"][~np.isnan(grids["elevation_m"])]
    slope_valid = grids["slope_deg"][~np.isnan(grids["slope_deg"])]
    print(
        f"  Elevation: {elev_valid.min():.0f} - {elev_valid.max():.0f} m (mean {elev_valid.mean():.0f})"
    )
    print(
        f"  Slope: {slope_valid.min():.1f} - {slope_valid.max():.1f}° (mean {slope_valid.mean():.1f})"
    )
    for code, name in [(1, "Montano"), (2, "Subalpino"), (3, "Alpino"), (4, "Nival")]:
        count = int(np.sum(grids["piso"] == code))
        pct = 100 * count / len(elev_valid)
        print(f"  {name}: {count} cells ({pct:.0f}%)")
    print(f"\n  Maps saved to: {out_dir.resolve()}")
    print("  Done!")


if __name__ == "__main__":
    main()
