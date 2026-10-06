#!/usr/bin/env python3
"""
Ecosystem Simulator — Parc Natural de l'Alt Pirineu
Run script for the agent-based simulation.

Usage:
    python run_simulation.py                     # default run
    python run_simulation.py --days 365          # 1 year
    python run_simulation.py --grid 200 200      # smaller grid for testing
    python run_simulation.py --demo              # 30-day demo
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sim import Simulation
from sim.grid import TerrainGrid


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Alt Pirineu Ecosystem Simulator")
    p.add_argument("--grid", type=int, nargs=2, default=(400, 400), metavar=("W", "H"))
    p.add_argument("--days", type=int, default=365, help="total days to simulate")
    p.add_argument("--res", type=int, default=25, help="grid resolution in meters")
    p.add_argument("--output", type=str, default="output", help="output directory")
    p.add_argument("--demo", action="store_true", help="30-day quick demo")
    p.add_argument("--profile", action="store_true", help="enable basic profiling")
    return p


def main():
    args = build_parser().parse_args()

    if args.demo:
        args.days = 30
        args.grid = (50, 50)

    width, height = args.grid
    total_cells = width * height

    print(f"{'=' * 60}")
    print(f"  Alt Pirineu Ecosystem Simulator")
    print(f"{'=' * 60}")
    print(f"  Grid:       {width}×{height} = {total_cells:,} cells @ {args.res}m")
    print(
        f"  Area:       {width * args.res / 1000:.1f}×{height * args.res / 1000:.1f} km"
    )
    print(f"  Days:       {args.days}")
    print(f"  Output:     {args.output}")
    print(f"{'=' * 60}")

    grid = TerrainGrid(width, height, args.res)

    sim = Simulation(
        grid=grid,
        total_days=args.days,
        output_dir=Path(args.output),
        log_every=1 if args.demo else 10,
        snapshot_every=10 if args.demo else 100,
    )

    sim.initialize()
    pre = sim.get_stats()
    print(
        f"\n  Initial state: {pre['agents_alive']} agents, "
        f"{pre['plant_biomass_kg']:.0f} kg plant biomass"
    )
    print()

    sim.run()

    post = sim.get_stats()
    print(f"\n  Final state ({args.days} days):")
    print(f"  Agents alive:  {post['agents_alive']}")
    print(f"  Plant biomass: {post['plant_biomass_kg']:.0f} kg")
    print(f"  Invert biomass: {post['invert_biomass_kg']:.0f} kg")
    print(f"  Species:       {len(post['species_counts'])}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
