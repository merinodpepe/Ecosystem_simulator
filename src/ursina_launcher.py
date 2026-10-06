#!/usr/bin/env python3
"""
Unified launcher for the 3D terrain viewer and related tools.

Usage:
    # Full pipeline: export mesh + launch viewer
    python src/ursina_launcher.py --run

    # Generate test snapshots + view them
    python src/ursina_launcher.py --test-snapshots --view

    # Just export mesh with custom settings
    python src/ursina_launcher.py --export-mesh --step 3

    # Just launch viewer
    python src/ursina_launcher.py --view

Commands:
    --export-mesh       Generate 3D mesh from terrain TSV
    --view              Launch interactive 3D viewer
    --test-snapshots    Generate synthetic agent trajectories
    --run               Full pipeline: export + launch (default)
    --step N            Subsampling factor (default: 2)
    --vertical-scale F  Vertical exaggeration (default: 0.03)
    --snapshots DIR     Load agent snapshots from directory
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_name, args=None):
    """Run a Python script with arguments, capturing output."""
    cmd = [sys.executable, str(Path("src") / script_name)]
    if args:
        cmd.extend(args)
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        for line in result.stdout.splitlines():
            if line.strip():
                print(f"    {line}")
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
    return result.returncode == 0


def main():
    p = argparse.ArgumentParser(
        description="Ecosystem Simulator — 3D Terrain Viewer Launcher"
    )
    p.add_argument("--export-mesh", action="store_true", help="Export 3D mesh from TSV")
    p.add_argument("--view", action="store_true", help="Launch interactive 3D viewer")
    p.add_argument(
        "--test-snapshots",
        action="store_true",
        help="Generate synthetic agent snapshots",
    )
    p.add_argument(
        "--run", action="store_true", default=False, help="Run full pipeline (default)"
    )
    p.add_argument("--step", type=int, default=2, help="Subsampling factor")
    p.add_argument(
        "--vertical-scale", type=float, default=0.03, help="Vertical exaggeration"
    )
    p.add_argument(
        "--snapshots",
        type=str,
        default=None,
        help="Load agent snapshots from directory",
    )
    p.add_argument(
        "--headless",
        action="store_true",
        help="Run viewer without a visible window (offscreen)",
    )
    args = p.parse_args()

    # Default: full pipeline when no specific action given
    has_cmd = args.export_mesh or args.view or args.test_snapshots or args.run
    if not has_cmd:
        args.run = True

    print("=" * 60)
    print("  3D TERRAIN VIEWER — Launcher")
    print("=" * 60)

    # Step 1: Export mesh
    if args.run or args.export_mesh:
        print("\n[1/3] Exporting terrain mesh...")
        ok = run_script(
            "export_terrain_mesh.py",
            [
                "--step",
                str(args.step),
                "--vertical-scale",
                str(args.vertical_scale),
            ],
        )
        if not ok:
            print("  Mesh export failed. Aborting.")
            return

    # Step 2: Generate test snapshots (optional)
    snap_dir = args.snapshots
    if args.run or args.test_snapshots:
        if not snap_dir:
            snap_dir = str(Path("output/snapshots_test"))
        print(f"\n[2/3] Generating test snapshots in {snap_dir}...")
        # Import and run
        sys.path.insert(0, "src")
        from ursina_sim_bridge import generate_test_snapshots

        generate_test_snapshots(output_dir=snap_dir, num_days=60, num_agents=30)
        print("  Done.")

    # Step 3: Launch viewer
    if args.run or args.view:
        print(f"\n[3/3] Launching 3D viewer...")
        viewer_args = [
            "--step",
            str(args.step),
            "--vertical-scale",
            str(args.vertical_scale),
        ]
        if snap_dir:
            viewer_args.extend(["--snapshots", snap_dir])
        if args.headless:
            viewer_args.append("--headless")
        ok = run_script("ursina_viewer.py", viewer_args)


if __name__ == "__main__":
    main()
