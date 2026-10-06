#!/usr/bin/env python3
"""
Render simulation snapshots as an animated GIF over terrain maps.
Reads terrain_cells.tsv for the base map and snap_*.json for agent positions.

Usage:
    python render_gif.py --dir /path/to/output --data ../ecosystem/data --output sim.gif
    python render_gif.py --dir /path/to/output --width 400 --height 400 --res 25
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HABITAT_COLORS = {
    1: (0.2, 0.5, 0.2),
    2: (0.3, 0.7, 0.3),
    3: (0.6, 0.6, 0.2),
    4: (0.8, 0.8, 0.4),
    5: (0.4, 0.6, 0.6),
    6: (0.5, 0.4, 0.3),
    7: (0.2, 0.3, 0.8),
    8: (0.3, 0.6, 0.4),
    9: (0.9, 0.9, 0.9),
    10: (0.6, 0.3, 0.3),
}

SPECIES_COLORS = [
    "#E6194B",
    "#3CB44B",
    "#FFE119",
    "#4363D8",
    "#F58231",
    "#911EB4",
    "#46F0F0",
    "#F032E6",
    "#BCF60C",
    "#FABEBE",
    "#008080",
    "#E6BEFF",
    "#9A6324",
    "#FFFAC8",
    "#800000",
    "#AAFFC3",
    "#808000",
    "#FFD8B1",
    "#000075",
    "#808080",
    "#AFFFE0",
]

SPECIES_LABELS = {
    "Rupicapra_pyrenaica": "Isard",
    "Cervus_elaphus": "Cérvol",
    "Capreolus_capreolus": "Cabirol",
    "Sus_scrofa": "Senglar",
    "Marmota_marmota": "Marmota",
    "Oryctolagus_cuniculus": "Conill",
    "Sciurus_vulgaris": "Esquirol",
    "Vulpes_vulpes": "Guineu",
    "Meles_meles": "Teixó",
    "Martes_martes": "Marta",
    "Felis_silvestris": "Gat fer",
    "Mustela_erminea": "Ermíni",
    "Mustela_nivalis": "Mostela",
    "Tetrao_urogallus": "Gall fer",
    "Lagopus_muta": "Perdiu xerra",
    "Corvus_corax": "Corb",
    "Gypaetus_barbatus": "Trencalòs",
    "Aquila_chrysaetos": "Àguila reial",
    "Lutra_lutra": "Llúdriga",
    "Ovis_aries_musimon": "Mufló",
    "Dama_dama": "Daina",
}


def load_terrain(tsv_path, width, height):
    elev = np.full((height, width), np.nan)
    habitat = np.zeros((height, width), dtype=np.uint8)
    with open(tsv_path) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for row in reader:
            if len(row) < 9:
                continue
            x, y = int(row[0]), int(row[1])
            if x >= width or y >= height:
                continue
            elevation = float(row[4])
            piso = int(row[8])
            elev[y, x] = elevation
            if piso == 3:
                h = 6 if elevation > 2500 else 4
            elif piso == 4:
                h = 6
            elif piso == 2:
                h = 1 if elevation < 1900 else 3
            else:
                h = 2 if elevation < 1200 else 1
            habitat[y, x] = h
    return elev, habitat


def render_frame(
    fig,
    ax,
    elev,
    habitat,
    day,
    season,
    avg_temp,
    agents,
    color_map,
    width,
    height,
    resolution,
):
    ax.clear()
    hab_rgb = np.zeros((height, width, 3))
    for h_type, color in HABITAT_COLORS.items():
        mask = habitat == h_type
        hab_rgb[mask] = color
    ax.imshow(
        hab_rgb,
        extent=[0, width * resolution, 0, height * resolution],
        origin="lower",
        interpolation="nearest",
    )
    if not np.all(np.isnan(elev)):
        ax.contour(
            elev,
            levels=6,
            colors="white",
            alpha=0.12,
            linewidths=0.3,
            extent=[0, width * resolution, 0, height * resolution],
        )
    for a in agents:
        if not a["alive"]:
            continue
        sp = a["species"]
        ax.plot(
            a["pos_x"],
            a["pos_y"],
            "o",
            color=color_map.get(sp, "#FFF"),
            markersize=3,
            markeredgecolor="black",
            markeredgewidth=0.2,
        )
    alive = sum(1 for a in agents if a["alive"])
    ax.set_title(
        f"Day {day} | {season} | {avg_temp:.1f}°C | {alive} alive",
        fontsize=9,
        fontweight="bold",
        pad=6,
    )
    ax.set_xlabel("Metres", fontsize=7)
    ax.set_ylabel("Metres", fontsize=7)
    ax.tick_params(labelsize=6)
    unique = sorted(set(a["species"] for a in agents if a["alive"]))
    if len(unique) <= 12:
        patches = [
            mpatches.Patch(
                color=color_map.get(sp, "#FFF"), label=SPECIES_LABELS.get(sp, sp)
            )
            for sp in unique
        ]
        ax.legend(
            handles=patches,
            loc="upper right",
            fontsize=4.5,
            framealpha=0.7,
            ncol=2 if len(unique) > 6 else 1,
        )
    fig.canvas.draw()


def main():
    parser = argparse.ArgumentParser(description="Render simulation GIF")
    parser.add_argument("--dir", required=True)
    parser.add_argument("--data", default="../ecosystem/data")
    parser.add_argument("--output", default="simulation.gif")
    parser.add_argument("--width", type=int, default=400)
    parser.add_argument("--height", type=int, default=400)
    parser.add_argument("--res", type=int, default=25)
    parser.add_argument("--fps", type=int, default=2)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--dpi", type=int, default=120)
    args = parser.parse_args()

    output_dir = Path(args.dir)
    data_dir = Path(args.data)
    w, h, res = args.width, args.height, args.res

    tsv_path = data_dir / "terrain_cells.tsv"
    if not tsv_path.exists():
        print(f"ERROR: {tsv_path} not found")
        sys.exit(1)
    print(f"Loading terrain {w}x{h} from {tsv_path}...")
    elev, habitat = load_terrain(tsv_path, w, h)

    snap_paths = sorted(output_dir.glob("snap_*.json"))
    if not snap_paths:
        print(f"ERROR: No snap_*.json in {output_dir}")
        sys.exit(1)
    print(f"Found {len(snap_paths)} snapshots")
    if args.max_frames > 0:
        snap_paths = snap_paths[: args.max_frames]

    all_species = set()
    for sp in SPECIES_LABELS:
        all_species.add(sp)
    color_map = {}
    for i, sp in enumerate(sorted(all_species)):
        color_map[sp] = SPECIES_COLORS[i % len(SPECIES_COLORS)]

    fig_w = max(6, w * res / 800)
    fig_h = max(6, h * res / 800)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=args.dpi)

    frames = []
    for path in snap_paths:
        with open(path) as f:
            snap = json.load(f)
        render_frame(
            fig,
            ax,
            elev,
            habitat,
            snap.get("day", 0),
            snap.get("season", "unknown"),
            snap.get("avg_temp_c", 0.0),
            snap.get("agents", []),
            color_map,
            w,
            h,
            res,
        )
        buf = fig.canvas.buffer_rgba()
        ncols, nrows = fig.canvas.get_width_height()
        frame = (
            np.frombuffer(buf, dtype=np.uint8).reshape(nrows, ncols, 4)[:, :, :3].copy()
        )
        frames.append(frame)
        print(f"\r  Frame {len(frames)}/{len(snap_paths)} (day {snap['day']})", end="")
        sys.stdout.flush()

    print(f"\nCompiling GIF ({len(frames)} frames)...")
    pil_frames = [Image.fromarray(f) for f in frames]
    pil_frames[0].save(
        args.output,
        save_all=True,
        append_images=pil_frames[1:],
        duration=1000 // args.fps,
        loop=0,
    )
    print(f"Done! {args.output}")
    plt.close()


if __name__ == "__main__":
    from PIL import Image

    main()
