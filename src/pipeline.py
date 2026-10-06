#!/usr/bin/env python3
"""
Master pipeline: terrain mesh → simulation → 3D viewer.

Executa tot el pipeline pas a pas:
  1. Verifica dependències i dades
  2. Exporta mesh 3D del terreny
  3. Executa simulació (o genera snapshots de test)
  4. Llança el visor 3D interactiu

Ús:
  python src/pipeline.py                         # interactiu (pregunta cada pas)
  python src/pipeline.py --full                  # automàtic: tot seguit
  python src/pipeline.py --full --headless       # sense finestra (servidor)
  python src/pipeline.py --demo --headless       # demo ràpida + visor headless
  python src/pipeline.py --skip-mesh             # omet exportació mesh
  python src/pipeline.py --skip-sim              # omet simulació, usa snapshots de test
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent


def step_header(num, total, title):
    """Print a formatted step header."""
    print()
    print("=" * 64)
    print(f"  PAS {num}/{total} — {title}")
    print("=" * 64)
    print()


def run(cmd, desc, critical=True):
    """Run a command, print output, return success."""
    print(f"  $ {' '.join(cmd)}")
    print(f"  → {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.strip():
            print(f"    {line}")
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        if critical:
            print("  Pipeline ABORTED.")
            sys.exit(1)
        return False
    return True


def check_dependencies():
    """Verify Python packages and data files exist."""
    deps = {
        "numpy": "pip install numpy",
        "pandas": "pip install pandas",
        "PIL": "pip install Pillow",
        "ursina": "pip install ursina",
    }
    missing = []
    for mod, install_cmd in deps.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append((mod, install_cmd))
    if missing:
        print("  Paquets Python necessaris:")
        for mod, cmd in missing:
            print(f"    {mod} → {cmd}")
        return False
    print("  Totes les dependències Python estan instal·lades.")
    return True


def check_data():
    """Check that terrain TSV exists."""
    tsv = ROOT / "ecosystem" / "data" / "terrain_cells.tsv"
    if not tsv.exists():
        print(f"  Dades de terreny no trobades a {tsv}")
        print("  Executa 'src/process_terrain.py' primer o verifica el repositori.")
        return False
    print(f"  Dades de terreny trobades: {tsv.name}")
    return True


def step_export_mesh(args):
    """Step 1: Export 3D terrain mesh."""
    step_header(1, 4, "Exportar mesh 3D del terreny")
    cmd = [
        sys.executable,
        str(SRC_DIR / "export_terrain_mesh.py"),
        "--step",
        str(args.step),
        "--vertical-scale",
        str(args.vertical_scale),
    ]
    return run(cmd, "Genera OBJ + MTL + textura + metadades")


def step_run_simulation(args):
    """Step 2: Executar simulació real amb el motor Rust."""
    step_header(2, 4, "Executar simulació ecològica (Rust)")

    sim_script = ROOT / "run_simulation.sh"
    output_name = f"output_pipeline"

    if args.demo:
        print("  Mode DEMO: 30 dies, graella 50×50")
        cmd = [
            "bash",
            str(sim_script),
            "--days",
            "30",
            "--output",
            output_name,
        ]
    else:
        print(f"  Mode normal: {args.sim_days} dies")
        cmd = [
            "bash",
            str(sim_script),
            "--days",
            str(args.sim_days),
            "--output",
            output_name,
        ]

    ok = run(cmd, "Genera snapshots i figures via Rust")

    # Check snapshots were generated (Rust output)
    rust_out = ROOT / "simulator" / output_name
    if ok and rust_out.exists():
        n = len(list(rust_out.glob("snap_*.json")))
        print(f"  Snapshots generats al Rust: {n}")
        if n == 0:
            print("  ERROR: No s'han generat snapshots!")
            return False
    return ok, rust_out if ok else None


def step_test_snapshots(args):
    """Step 2b (fallback): Generate synthetic test snapshots."""
    step_header(2, 4, "Generar snapshots de test (fallback)")

    cmd = [
        sys.executable,
        "-c",
        f"""
import sys; sys.path.insert(0, '{SRC_DIR}')
from ursina_sim_bridge import generate_test_snapshots
generate_test_snapshots(output_dir='output/snapshots_test',
                        num_days={args.test_days},
                        num_agents={args.test_agents})
print('Fet.')
""",
    ]
    return run(cmd, f"Genera {args.test_days} snapshots sintètics")


def step_launch_viewer(args, snap_dir):
    """Step 3/4: Llançar visor 3D."""
    if args.demo or args.test_only:
        step = 3
        total = 3
    else:
        step = 4
        total = 4

    step_header(step, total, "Llançar visor 3D interactiu")

    if args.headless:
        print("  Mode HEADLESS: rendering offscreen (sense finestra)")

    cmd = [
        sys.executable,
        str(SRC_DIR / "ursina_viewer.py"),
        "--step",
        str(args.step),
        "--vertical-scale",
        str(args.vertical_scale),
    ]
    if snap_dir:
        cmd += ["--snapshots", str(snap_dir)]
    if args.headless:
        cmd.append("--headless")

    print(f"  Snapshots: {snap_dir or '(cap)'}")
    print(f"  Visor preparat. Executant...")
    return run(cmd, "Visor en marxa (tanqueu amb ESC)", critical=False)


def pipeline_interactive(args):
    """Run pipeline in interactive mode, asking user before each step."""
    print("=" * 64)
    print("  PIPELINE MASTER — Visor 3D Alt Pirineu")
    print("=" * 64)

    # --- Check ---
    print()
    print("Comprovant entorn...")
    deps_ok = check_dependencies()
    data_ok = check_data()
    if not deps_ok or not data_ok:
        print("  Corregiu els errors anteriors i torneu a executar.")
        return

    # --- Step 1: Mesh ---
    print()
    print("-" * 64)
    resp = input("  PAS 1: Exportar mesh 3D? (Y/n): ").strip().lower()
    if resp != "n":
        step_export_mesh(args)
    else:
        print("  Omes.")

    # --- Step 2: Sim ---
    print()
    print("-" * 64)
    resp = input("  PAS 2: Executar simulació real? (Y/n): ").strip().lower()
    snap_dir = None
    if resp != "n":
        ok, snap_dir = step_run_simulation(args)
    else:
        resp2 = input("  PAS 2b: O generar snapshots de test? (Y/n): ").strip().lower()
        if resp2 != "n":
            step_test_snapshots(args)
            snap_dir = ROOT / "output" / "snapshots_test"
        else:
            print("  Omes.")

    # --- Step 3/4: Viewer ---
    print()
    print("-" * 64)
    if args.headless:
        resp = "y"
        print("  PAS 3: Llançar visor (forçat per --headless)")
    else:
        resp = input("  PAS 3: Llançar visor 3D? (Y/n): ").strip().lower()
    if resp != "n":
        if not snap_dir:
            # Try to find any snapshots
            for d in [
                ROOT / "simulator" / "output_pipeline",
                ROOT / "output" / "snapshots_test",
            ]:
                if d.exists() and list(d.glob("*.json")):
                    snap_dir = d
                    break
        step_launch_viewer(args, snap_dir)
    else:
        print("  Omes.")

    print()
    print("=" * 64)
    print("  Pipeline completat!")
    print("=" * 64)


def pipeline_automatic(args):
    """Run pipeline in automatic mode: all steps in sequence."""
    print("=" * 64)
    print("  PIPELINE MASTER — Mode automàtic")
    print("=" * 64)

    check_dependencies()
    check_data()

    # Step 1: Mesh (unless skipped)
    if not args.skip_mesh:
        step_export_mesh(args)

    # Step 2: Simulation or test snapshots
    snap_dir = None
    if not args.skip_sim:
        if args.test_only:
            step_test_snapshots(args)
            snap_dir = ROOT / "output" / "snapshots_test"
        else:
            ok, snap_dir = step_run_simulation(args)
    else:
        print("\n  PAS 2 omès (--skip-sim). Buscant snapshots existents...")
        for d in [
            ROOT / "simulator" / "output_pipeline",
            ROOT / "simulator" / "output",
            ROOT / "output" / "snapshots_test",
        ]:
            if d.exists() and list(d.glob("snap_*.json")):
                snap_dir = d
                print(f"  Trobats: {d}")
                break
        if not snap_dir:
            print("  Cap snapshot trobat. Genereu snapshots primer.")

    # Step 3/4: Viewer
    step_launch_viewer(args, snap_dir)

    print()
    print("=" * 64)
    print("  Pipeline completat!")
    print("=" * 64)


def main():
    p = argparse.ArgumentParser(
        description="Master pipeline: mesh → simulació → visor 3D"
    )
    # Mode
    p.add_argument(
        "--full",
        action="store_true",
        help="Mode automàtic: executa tot sense preguntar",
    )
    p.add_argument(
        "--demo",
        action="store_true",
        help="Demo ràpida: 30 dies, graella petita",
    )
    p.add_argument(
        "--headless",
        action="store_true",
        help="Visor sense finestra (rendering offscreen)",
    )

    # Steps
    p.add_argument(
        "--skip-mesh",
        action="store_true",
        help="Omet exportació del mesh (usa l'existent)",
    )
    p.add_argument(
        "--skip-sim",
        action="store_true",
        help="Omet simulació/snapshots (usa els existents)",
    )
    p.add_argument(
        "--test-only",
        action="store_true",
        help="Usa snapshots de test (no simulació real)",
    )

    # Parameters
    p.add_argument("--step", type=int, default=2, help="Factor de submostreig")
    p.add_argument(
        "--vertical-scale", type=float, default=0.03, help="Exageració vertical"
    )
    p.add_argument("--sim-days", type=int, default=365, help="Dies de simulació")
    p.add_argument(
        "--snapshot-every", type=int, default=10, help="Freqüència snapshots (dies)"
    )
    p.add_argument("--test-days", type=int, default=60, help="Snapshots de test")
    p.add_argument("--test-agents", type=int, default=30, help="Agents de test")

    args = p.parse_args()

    if args.full or args.demo or args.test_only or args.headless:
        pipeline_automatic(args)
    else:
        pipeline_interactive(args)


if __name__ == "__main__":
    main()
