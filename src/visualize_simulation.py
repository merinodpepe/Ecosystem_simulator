#!/usr/bin/env python3
"""
Post-simulation visualization for Rust ecosystem simulator outputs.
Reads simulation_log.csv and species_population.csv from the output directory.

Usage:
    python visualize_simulation.py                          # uses output/simulation_log.csv
    python visualize_simulation.py --dir path/to/output     # custom output dir
    python visualize_simulation.py --save figures/          # save figures to directory
"""

import argparse
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

HABITAT_NAMES = {
    1: "Bosc coníferes",
    2: "Bosc caducifoli",
    3: "Matollar",
    4: "Pasturatge",
    5: "Aiguamoll",
    6: "Roca",
    7: "Aigua",
    8: "Ribera",
    9: "Neu",
    10: "Antròpic",
}

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
}


def load_data(output_dir: Path):
    log_path = output_dir / "simulation_log.csv"
    species_path = output_dir / "species_population.csv"

    if not log_path.exists():
        print(f"ERROR: {log_path} not found. Run Rust simulation first.")
        sys.exit(1)

    log_df = pd.read_csv(log_path)
    species_df = pd.read_csv(species_path) if species_path.exists() else None
    return log_df, species_df


def plot_population_over_time(log_df, species_df, save_dir: Path | None):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Ecosystem Simulation — Overview", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(log_df["day"], log_df["n_alive"], label="Alive", linewidth=2)
    ax.plot(log_df["day"], log_df["n_dead"], label="Dead", linewidth=2, linestyle="--")
    ax.set_xlabel("Day")
    ax.set_ylabel("Count")
    ax.set_title("Agent Population")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.plot(log_df["day"], log_df["total_plant_kg"], label="Plants", linewidth=2)
    ax.plot(
        log_df["day"], log_df["total_invert_kg"], label="Invertebrates", linewidth=2
    )
    if "total_carcass_kg" in log_df.columns:
        ax.plot(
            log_df["day"],
            log_df["total_carcass_kg"],
            label="Carcass",
            linewidth=2,
            linestyle=":",
        )
    ax.set_xlabel("Day")
    ax.set_ylabel("Biomass (kg)")
    ax.set_title("Ecosystem Biomass")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    ax.plot(log_df["day"], log_df["avg_energy"], linewidth=2, color="orange")
    ax.set_xlabel("Day")
    ax.set_ylabel("Energy (kcal)")
    ax.set_title("Average Agent Energy")
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    ax.plot(log_df["day"], log_df["temp_avg"], linewidth=2, color="steelblue")
    ax.axhline(y=0, color="red", linestyle="--", alpha=0.5, label="Freezing")
    ax.set_xlabel("Day")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("Average Temperature")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / "overview.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {path}")

    plt.close()


def plot_species_populations(species_df, save_dir: Path | None):
    if species_df is None or len(species_df.columns) <= 1:
        return

    species_cols = [c for c in species_df.columns if c != "day"]
    herbivores = [
        "Rupicapra_pyrenaica",
        "Cervus_elaphus",
        "Capreolus_capreolus",
        "Marmota_marmota",
        "Oryctolagus_cuniculus",
        "Sciurus_vulgaris",
        "Tetrao_urogallus",
        "Lagopus_muta",
    ]
    carnivores = [
        "Martes_martes",
        "Felis_silvestris",
        "Mustela_erminea",
        "Mustela_nivalis",
        "Aquila_chrysaetos",
    ]
    omnivores = [
        "Sus_scrofa",
        "Vulpes_vulpes",
        "Meles_meles",
        "Corvus_corax",
        "Gypaetus_barbatus",
    ]
    scavengers = ["Corvus_corax", "Gypaetus_barbatus"]

    groups = [
        ("Herbívors", [c for c in herbivores if c in species_cols], "forestgreen"),
        ("Carnívors", [c for c in carnivores if c in species_cols], "firebrick"),
        ("Omnívors", [c for c in omnivores if c in species_cols], "darkgoldenrod"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Species Populations by Trophic Group", fontsize=14, fontweight="bold")

    for idx, (title, species, color) in enumerate(groups):
        ax = axes[idx // 2, idx % 2]
        for sp in species:
            label = SPECIES_LABELS.get(sp, sp)
            ax.plot(species_df["day"], species_df[sp], label=label, linewidth=2)
        ax.set_xlabel("Day")
        ax.set_ylabel("Population")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    for sp in species_cols:
        label = SPECIES_LABELS.get(sp, sp)
        ax.plot(species_df["day"], species_df[sp], label=label, linewidth=1.5)
    ax.set_xlabel("Day")
    ax.set_ylabel("Population")
    ax.set_title("All Species")
    ax.legend(fontsize=6, loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / "species_populations.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {path}")

    plt.close()


def plot_stacked_species(species_df, save_dir: Path | None):
    if species_df is None or len(species_df.columns) <= 1:
        return

    species_cols = [c for c in species_df.columns if c != "day"]
    labels = [SPECIES_LABELS.get(c, c) for c in species_cols]

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.stackplot(
        species_df["day"],
        [species_df[c] for c in species_cols],
        labels=labels,
        alpha=0.8,
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Population")
    ax.set_title("Species Composition Over Time (Stacked)")
    ax.legend(loc="upper left", fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / "species_stacked.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {path}")

    plt.close()


def plot_energy_balance(log_df, save_dir: Path | None):
    fig, ax = plt.subplots(figsize=(10, 6))

    energy_kj = log_df["avg_energy"] * 4.184
    ax.plot(log_df["day"], energy_kj, linewidth=2, color="darkviolet")
    ax.set_xlabel("Day")
    ax.set_ylabel("Average Energy (kJ)")
    ax.set_title("Agent Energy Reserves Over Time")
    ax.grid(True, alpha=0.3)

    if "season" in log_df.columns:
        for _, row in log_df.iterrows():
            if row["season"] == "winter":
                ax.axvspan(row["day"] - 5, row["day"] + 5, alpha=0.08, color="blue")

    plt.tight_layout()

    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / "energy_balance.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {path}")

    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Visualize Rust simulation outputs")
    parser.add_argument("--dir", default="output", help="Simulation output directory")
    parser.add_argument("--save", default="figures", help="Directory to save figures")
    args = parser.parse_args()

    output_dir = Path(__file__).resolve().parent.parent / "simulator" / args.dir
    save_dir = Path(args.save) if args.save else None

    print(f"Loading data from: {output_dir}")
    log_df, species_df = load_data(output_dir)

    print(f"  Simulation log: {len(log_df)} rows")
    if species_df is not None:
        print(
            f"  Species log: {len(species_df)} rows, {len(species_df.columns) - 1} species"
        )
    print()

    print("Generating overview plot...")
    plot_population_over_time(log_df, species_df, save_dir)

    print("Generating species population plots...")
    plot_species_populations(species_df, save_dir)
    plot_stacked_species(species_df, save_dir)

    print("Generating energy balance plot...")
    plot_energy_balance(log_df, save_dir)

    print("\nDone! All visualizations generated.")


if __name__ == "__main__":
    main()
