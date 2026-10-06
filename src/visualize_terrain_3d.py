#!/usr/bin/env python3
"""
3D terrain visualization from DEM data.
Generates a 3D surface plot of the Vall de Cardós terrain.

Usage:
    python src/visualize_terrain_3d.py [--output output/maps] [--dpi 300]
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

DATA_DIR = Path("ecosystem/data")
TSV_PATH = DATA_DIR / "terrain_cells.tsv"


def load_dem_grid(path):
    """Load elevation data and build 2D grid."""
    df = pd.read_csv(path, sep="\t")
    W, H = df["x"].max() + 1, df["y"].max() + 1
    elev = np.full((H, W), np.nan)
    elev[df["y"].values, df["x"].values] = df["elevation_m"].values
    return elev, W, H


def main():
    p = argparse.ArgumentParser(description="Generate 3D terrain map")
    p.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(Path("output/maps")),
        help="Output directory",
    )
    p.add_argument("--dpi", type=int, default=250, help="Image DPI")
    p.add_argument("--azim", type=float, default=315, help="Azimuth viewing angle")
    p.add_argument("--elev", type=float, default=25, help="Elevation viewing angle")
    p.add_argument(
        "--z-exaggeration", type=float, default=2.0, help="Vertical exaggeration"
    )
    p.add_argument(
        "--wireframe", action="store_true", help="Wireframe instead of surface"
    )
    args = p.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading DEM...")
    elev, W, H = load_dem_grid(TSV_PATH)
    elev_filled = np.where(np.isnan(elev), 0, elev)
    print(f"  Grid: {W} x {H}, range: {np.nanmin(elev):.0f}-{np.nanmax(elev):.0f} m")

    # Subsample for performance (max ~400x400 for 3D)
    step = max(1, max(W, H) // 400)
    if step > 1:
        print(f"  Subsampling {step}x for 3D rendering")
        elev_filled = elev_filled[::step, ::step]
        W_sub, H_sub = elev_filled.shape[1], elev_filled.shape[0]
    else:
        W_sub, H_sub = W, H

    X, Y = np.meshgrid(range(W_sub), range(H_sub))

    # Mask nodata for display
    valid = elev[::step, ::step] if step > 1 else elev
    mask = np.isnan(valid)
    elev_plot = elev_filled.copy()
    if mask.any():
        elev_plot = np.ma.MaskedArray(elev_filled, mask)

    z_range = elev_plot.max() - elev_plot.min()
    z_scale = args.z_exaggeration

    print("Rendering 3D surface...")
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    ax.view_init(elev=args.elev, azim=args.azim)

    if args.wireframe:
        stride = max(1, W_sub // 50)
        ax.plot_wireframe(
            X,
            Y,
            elev_plot,
            rstride=stride,
            cstride=stride,
            color="darkslategray",
            linewidth=0.3,
            alpha=0.7,
        )
    else:
        norm = plt.Normalize(elev_plot.min(), elev_plot.max())
        colors = cm.terrain(norm(elev_plot))
        colors[..., 3] = np.where(mask, 0, 0.95) if mask.any() else 0.95
        surf = ax.plot_surface(
            X, Y, elev_plot, facecolors=colors, rstride=1, cstride=1, antialiased=False
        )

    # Labels
    elev_min, elev_max = np.nanmin(elev), np.nanmax(elev)
    ax.set_zlim(0, elev_max * z_scale * 0.15)
    ax.set_xlabel("Columna (cel·la)", fontsize=10, labelpad=8)
    ax.set_ylabel("Fila (cel·la)", fontsize=10, labelpad=8)
    z_label = f"Elevació (m)"
    ax.set_zlabel(z_label, fontsize=10, labelpad=8)
    ax.set_title(
        f"Parc Natural de l'Alt Pirineu — Vall de Cardós\n"
        f"Terreny 3D | {W}x{H} cel·les a 25 m | {elev_min:.0f}–{elev_max:.0f} m",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )

    # Colorbar
    mappable = cm.ScalarMappable(norm=norm, cmap="terrain")
    mappable.set_array(elev_plot)
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.5, pad=0.08)
    cbar.set_label("Elevació (m)", fontsize=11)

    # Ticks
    ticks = np.linspace(0, H_sub - 1, 5, dtype=int)
    ax.set_xticks(np.linspace(0, W_sub - 1, 5))
    ax.set_yticks(ticks)
    ax.set_xticklabels(
        [f"{int(W * t / (W_sub - 1))}" for t in np.linspace(0, W_sub - 1, 5)]
    )
    ax.set_yticklabels(
        [f"{int(H * t / (H_sub - 1))}" for t in np.linspace(0, H_sub - 1, 5)]
    )

    ax.xaxis.pane.set_edgecolor("0.8")
    ax.yaxis.pane.set_edgecolor("0.8")
    ax.zaxis.pane.set_edgecolor("0.8")
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(True, alpha=0.3)

    out_path = out_dir / "terrain_3d.png"
    fig.savefig(out_path, dpi=args.dpi, bbox_inches="tight")
    print(f"  Saved: {out_path}")
    plt.close(fig)

    # Second view: low-angle perspective
    fig2 = plt.figure(figsize=(16, 10))
    ax2 = fig2.add_subplot(111, projection="3d", computed_zorder=False)
    ax2.view_init(elev=10, azim=225)
    norm2 = plt.Normalize(elev_plot.min(), elev_plot.max())
    colors2 = cm.terrain(norm2(elev_plot))
    colors2[..., 3] = np.where(mask, 0, 0.95) if mask.any() else 0.95
    ax2.plot_surface(
        X, Y, elev_plot, facecolors=colors2, rstride=1, cstride=1, antialiased=False
    )
    ax2.set_zlim(0, elev_max * z_scale * 0.15)
    ax2.set_xlabel("Columna", fontsize=10, labelpad=8)
    ax2.set_ylabel("Fila", fontsize=10, labelpad=8)
    ax2.set_zlabel(z_label, fontsize=10, labelpad=8)
    ax2.set_title(
        "Vall de Cardós — Perspectiva baixa", fontsize=14, fontweight="bold", pad=12
    )
    ax2.xaxis.pane.fill = False
    ax2.yaxis.pane.fill = False
    ax2.zaxis.pane.fill = False
    ax2.grid(True, alpha=0.3)

    out_path2 = out_dir / "terrain_3d_low.png"
    fig2.savefig(out_path2, dpi=args.dpi, bbox_inches="tight")
    print(f"  Saved: {out_path2}")
    plt.close(fig2)

    print("  Done!")


if __name__ == "__main__":
    main()
