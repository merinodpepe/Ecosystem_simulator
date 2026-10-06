#!/usr/bin/env python3
"""
Bridge between the ecosystem simulation and the 3D Ursina viewer.
Exports agent snapshots during simulation, loads them in the viewer.

Usage:
    # From simulation (add to simulation.py loop):
    from ursina_sim_bridge import export_snapshot
    export_snapshot(agents, day, output_dir)

    # From viewer (already integrated in ursina_viewer.py):
    viewer.load_snapshot_sequence("output/snapshots")
"""

import json
from pathlib import Path


def export_snapshot(agents, day, output_dir="output/snapshots", prefix="agents_day"):
    """Export current agent states as a JSON snapshot file.

    Call this from the simulation loop every N steps.

    Args:
        agents: list of agent objects (must have .agent_id, .species_key,
                .common_name, .trophic_level, .state.x, .state.y,
                .state.energy_kcal, .state.age_days)
        day: current simulation day
        output_dir: directory to save snapshots
        prefix: filename prefix
    """
    snap_dir = Path(output_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    agent_list = []
    for a in agents:
        alive = (
            a.is_alive if hasattr(a, "is_alive") else getattr(a.state, "alive", True)
        )

        agent_list.append(
            {
                "id": a.agent_id,
                "species_key": a.species_key,
                "nick": getattr(a, "common_name", a.species_key),
                "guild": getattr(a, "trophic_level", "HERBIVORE"),
                "x": getattr(a.state, "x", 0)
                if hasattr(a, "state")
                else getattr(a, "x", 0),
                "y": getattr(a.state, "y", 0)
                if hasattr(a, "state")
                else getattr(a, "y", 0),
                "energy": getattr(a.state, "energy_kcal", 0)
                if hasattr(a, "state")
                else 0,
                "alive": alive,
                "age": getattr(a.state, "age_days", 0) if hasattr(a, "state") else 0,
            }
        )

    path = snap_dir / f"{prefix}_{day:05d}.json"
    with open(path, "w") as f:
        json.dump(agent_list, f, indent=2)

    return path


def generate_test_snapshots(
    output_dir="output/snapshots_test", num_days=50, num_agents=20
):
    """Generate synthetic agent trajectories for testing the viewer."""
    import numpy as np

    snap_dir = Path(output_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    # Species palette
    species = [
        {"key": "Rupicapra_pyrenaica", "nick": "Isard", "guild": "HERBIVORE"},
        {"key": "Vulpes_vulpes", "nick": "Guineu", "guild": "OMNIVORE"},
        {"key": "Marmota_marmota", "nick": "Marmota", "guild": "HERBIVORE"},
        {"key": "Gypaetus_barbatus", "nick": "Trencalòs", "guild": "BIRD"},
    ]

    # Random walk parameters per agent
    np.random.seed(42)
    agents = []
    for i in range(num_agents):
        sp = species[i % len(species)]
        agents.append(
            {
                "id": i + 1,
                "species_key": sp["key"],
                "nick": f"{sp['nick']}_{i + 1}",
                "guild": sp["guild"],
                "x": float(np.random.randint(10, 350)),
                "y": float(np.random.randint(10, 480)),
                "vx": float(np.random.uniform(-2, 2)),
                "vy": float(np.random.uniform(-2, 2)),
            }
        )

    print(f"Generating {num_days} test snapshots ({num_agents} agents)...")
    for day in range(num_days):
        for a in agents:
            # Random walk with occasional direction changes
            if np.random.random() < 0.1:
                a["vx"] = float(np.random.uniform(-3, 3))
                a["vy"] = float(np.random.uniform(-3, 3))
            a["x"] = max(1, min(373, a["x"] + a["vx"]))
            a["y"] = max(1, min(499, a["y"] + a["vy"]))

        # Build snapshot
        snapshot = []
        for a in agents:
            alive = not (day > 30 and np.random.random() < 0.002)
            snapshot.append(
                {
                    "id": a["id"],
                    "species_key": a["species_key"],
                    "nick": a["nick"],
                    "guild": a["guild"],
                    "x": a["x"],
                    "y": a["y"],
                    "energy": float(np.random.uniform(2000, 8000)),
                    "alive": alive,
                    "age": day,
                }
            )

        path = snap_dir / f"agents_day_{day:05d}.json"
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)

    print(f"  Generated {num_days} snapshots in {snap_dir}")
    return snap_dir
