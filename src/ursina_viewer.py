#!/usr/bin/env python3
"""
Interactive 3D terrain viewer using Ursina Engine.
WASD + mouse to fly through the Vall de Cardós terrain.

Usage:
    python src/ursina_viewer.py
    python src/ursina_viewer.py --snapshots output/snapshots_test
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ursina import (
    Ursina,
    color,
    window,
    scene,
    camera,
    mouse,
    DirectionalLight,
    AmbientLight,
    Entity,
    Text,
    Grid,
    Vec3,
    held_keys,
    time,
)

DATA_DIR = Path("ecosystem/data")
TSV_PATH = DATA_DIR / "terrain_cells.tsv"

# Module-level reference so Ursina can find update()
_viewer_instance = None


def input(key):
    """Called by Ursina on key/button/mouse events."""
    if _viewer_instance:
        _viewer_instance._handle_input(key)


def update():
    """Called every frame by Ursina's game loop."""
    if _viewer_instance:
        _viewer_instance.update()


def load_elevation_grid(tsv_path, step=1):
    """Load TSV and return 2D elevation array (subsampled)."""
    df = pd.read_csv(tsv_path, sep="\t")
    W, H = df["x"].max() + 1, df["y"].max() + 1
    elev = np.full((H, W), np.nan)
    elev[df["y"].values, df["x"].values] = df["elevation_m"].values
    if step > 1:
        elev = elev[::step, ::step]
    return elev


class TerrainViewer:
    """Interactive 3D viewer for the Alt Pirineu terrain."""

    def __init__(
        self,
        mesh_dir="output/terrain_mesh",
        vertical_scale=0.03,
        step=2,
        show_grid=True,
    ):
        self.mesh_dir = Path(mesh_dir)
        self.vertical_scale = vertical_scale
        self.step = step
        self.show_grid = show_grid
        self.play_speed = 1.0
        self.is_paused = False
        self.current_day = 0
        self.snapshots = []
        self.agent_entities = {}
        self._p_key_held = False
        self._f_key_held = False
        self._frame_count = 0
        self.follow_target = None
        self.follow_mode = False
        self.selected_agent = None
        self._scroll = 0

        self.elev = load_elevation_grid(TSV_PATH, step=step)

        self._setup_scene()
        self._setup_camera()
        self._setup_lights()
        self._setup_terrain()
        self._setup_ui()

        if self.show_grid:
            self._setup_reference_grid()

    def _setup_scene(self):
        window.title = "Ecosystem Simulator — Alt Pirineu 3D"
        window.size = (1280, 720)
        window.color = color.rgb(180, 200, 230)

    def _setup_camera(self):
        W = self.elev.shape[1]
        H = self.elev.shape[0]
        h = float(np.nanmedian(self.elev)) * self.vertical_scale
        camera.position = Vec3(W // 2, h * 2.5, -H * 0.7)
        camera.rotation = (25, 0, 0)

    def _orbit_camera(self):
        speed = 30 * time.dt
        fwd = camera.forward
        fwd.y = 0
        fwd = fwd.normalized() if fwd.length() > 0 else Vec3(0, 0, 1)
        right = camera.right
        right.y = 0
        right = right.normalized() if right.length() > 0 else Vec3(1, 0, 0)

        move_dir = Vec3(
            (held_keys["d"] - held_keys["a"]),
            (held_keys["e"] - held_keys["q"]),
            (held_keys["s"] - held_keys["w"]),
        )
        if move_dir.length() > 0:
            move_dir = move_dir.normalized() * speed
            camera.position += (
                right * move_dir.x + Vec3(0, 1, 0) * move_dir.y + (-fwd) * move_dir.z
            )

        if mouse.right:
            camera.rotation_y += mouse.velocity.x * 40
            camera.rotation_x = max(
                -89, min(89, camera.rotation_x - mouse.velocity.y * 40)
            )

        if self._scroll:
            camera.position += camera.forward * self._scroll * speed * 3
            self._scroll = 0

    def _setup_lights(self):
        AmbientLight(color=color.rgb(0.3, 0.3, 0.35))
        sun = DirectionalLight(shadow_map_resolution=(2048, 2048))
        sun.look_at(Vec3(-1, -1, -1))
        scene.fog_color = window.color
        scene.fog_density = 0.002

    def _setup_terrain(self):
        obj_path = self.mesh_dir / "terrain.obj"
        tex_path = self.mesh_dir / "terrain_texture.png"

        if obj_path.exists():
            self.terrain = Entity(
                model=str(obj_path),
                texture=str(tex_path) if tex_path.exists() else None,
                scale=(1, 1, 1),
                unlit=False,
            )
        else:
            print(f"  Mesh not found at {obj_path}")
            print(f"  Creating fallback flat terrain plane")
            W = self.elev.shape[1]
            H = self.elev.shape[0]
            h = float(np.nanmedian(self.elev)) * self.vertical_scale
            self.terrain = Entity(
                model="plane",
                scale=(W, 1, H),
                position=(W / 2, h - 0.5, -H / 2),
                color=color.rgba(80, 140, 80, 200),
                unlit=True,
            )

    def _setup_reference_grid(self):
        W = self.elev.shape[1]
        H = self.elev.shape[0]
        Entity(
            model=Grid(W // 10, H // 10),
            scale=(W, 1, H),
            position=(W / 2, -0.1, -H / 2),
            color=color.rgba(255, 255, 255, 30),
            unlit=True,
        )

    def _setup_ui(self):
        ui_parent = camera.ui
        self.fps_text = Text(
            text="FPS: --",
            position=(-0.85, 0.47),
            scale=1.2,
            color=color.white,
            parent=ui_parent,
        )
        self.pos_text = Text(
            text="Pos: (0, 0, 0)",
            position=(-0.85, 0.43),
            scale=1.0,
            color=color.white,
            parent=ui_parent,
        )
        self.day_text = Text(
            text="Day: 0",
            position=(-0.85, 0.39),
            scale=1.0,
            color=color.white,
            parent=ui_parent,
        )
        self.agents_text = Text(
            text="Agents: 0",
            position=(-0.85, 0.35),
            scale=1.0,
            color=color.white,
            parent=ui_parent,
        )
        self.speed_text = Text(
            text="Speed: 1.0x",
            position=(0.65, 0.47),
            scale=1.2,
            color=color.yellow,
            parent=ui_parent,
        )
        self.pause_text = Text(
            text="",
            position=(0.65, 0.43),
            scale=1.5,
            color=color.orange,
            parent=ui_parent,
        )

        self.follow_text = Text(
            text="",
            position=(0.65, 0.35),
            scale=1.0,
            color=color.lime,
            parent=ui_parent,
        )

        legend_y = -0.42
        Text(
            text="o Herbivor   o Carnivor   o Omnivor   o Ocell",
            position=(-0.85, legend_y),
            scale=0.9,
            color=color.white,
            parent=ui_parent,
        )
        Text(
            text="WASD: moure  Q/E:altura  R:reset  ESC:eixir  P:pausa  [+] [-] :vel",
            position=(-0.85, legend_y - 0.04),
            scale=0.7,
            color=color.gray,
            parent=ui_parent,
        )

    def select_agent(self, agent):
        """Select an agent and show its info panel."""
        self.selected_agent = agent
        self._show_agent_info(agent)

    def _handle_input(self, key):
        if key == "scroll up":
            self._scroll = 1
        elif key == "scroll down":
            self._scroll = -1

    def deselect_agent(self):
        """Deselect agent and hide info panel."""
        self.selected_agent = None
        self._clear_info_panel()

    def _show_agent_info(self, agent):
        """Display agent stats panel on screen."""
        self._clear_info_panel()
        lines = [
            f"Agent: {agent.agent_id}",
            f"Especie: {agent.species_key}",
            f"Nom: {agent.nick}",
            f"Gremi: {agent.guild}",
        ]
        if agent.stats.get("energy"):
            lines.append(f"Energia: {agent.stats['energy']:.0f} kcal")
        if agent.stats.get("age"):
            lines.append(f"Edat: {agent.stats['age']:.0f} dies")
        y_start = 0.2
        self._info_texts = []
        for i, line in enumerate(lines):
            t = Text(
                text=line,
                position=(-0.3, y_start - i * 0.04),
                scale=1.0,
                color=color.white,
                parent=camera.ui,
            )
            self._info_texts.append(t)

    def _clear_info_panel(self):
        for t in getattr(self, "_info_texts", []):
            t.disable()
        self._info_texts = []

    def _terrain_height(self, x, y):
        """Get terrain height at grid position (x, y) for agent placement."""
        ix, iy = int(round(x)), int(round(-y))
        if 0 <= ix < self.elev.shape[1] and 0 <= iy < self.elev.shape[0]:
            h = self.elev[iy, ix]
            if not np.isnan(h):
                return float(h) * self.vertical_scale
        return 0.0

    def _get_follow_target(self):
        """Find the best agent to follow: selected agent, or nearest to camera."""
        if self.selected_agent and self.selected_agent.enabled:
            return self.selected_agent
        if not self.agent_entities:
            return None
        cam_pos = camera.position
        best = min(
            self.agent_entities.values(),
            key=lambda ae: (
                (ae.position - cam_pos).length() if ae.enabled else float("inf")
            ),
            default=None,
        )
        return best if best and best.enabled else None

    def _update_follow_camera(self):
        """Lerp camera toward follow target position."""
        target_pos = self.follow_target.position
        desired = target_pos + Vec3(8, 12, 8)
        camera.position += (desired - camera.position) * time.dt * 3
        camera.look_at(target_pos)

    def load_snapshot(self, path):
        """Load agents from a snapshot JSON file."""
        with open(path) as f:
            data = json.load(f)

        if isinstance(data, dict) and "agents" in data:
            agent_list = data["agents"]
        elif isinstance(data, list):
            agent_list = data
        else:
            print(f"  Unknown snapshot format in {path}")
            return

        alive_ids = {a["id"] for a in agent_list if a.get("alive", True)}
        to_remove = [eid for eid in self.agent_entities if eid not in alive_ids]
        for eid in to_remove:
            self.agent_entities[eid].disable()
            del self.agent_entities[eid]

        for ad in agent_list:
            if not ad.get("alive", True):
                continue
            aid = ad["id"]
            if aid in self.agent_entities:
                ae = self.agent_entities[aid]
                pos_x = ad.get("x", ad.get("pos_x", 0))
                pos_y = ad.get("y", ad.get("pos_y", 0))
                ae.move_to(pos_x, pos_y, self._terrain_height)
            else:
                from ursina_models import Agent3D

                species_key = ad.get("species_key", ad.get("species", "unknown"))
                guild = ad.get("guild", ad.get("kind", "HERBIVORE"))
                nick = ad.get("nick", ad.get("common_name", str(aid)))
                pos_x = ad.get("x", ad.get("pos_x", 0))
                pos_y = ad.get("y", ad.get("pos_y", 0))
                energy = ad.get("energy", ad.get("energy_kcal", 0))
                age = ad.get("age", ad.get("age_days", 0))

                ae = Agent3D(
                    agent_id=aid,
                    species_key=species_key,
                    nick=nick,
                    guild=guild,
                    x=pos_x,
                    y=pos_y,
                    terrain_height_fn=self._terrain_height,
                    scale=1.0,
                )
                ae.stats["energy"] = energy
                ae.stats["age"] = age
                self.agent_entities[aid] = ae

        self.agents_text.text = f"Agents: {len(self.agent_entities)}"

    def load_snapshot_sequence(self, snap_dir):
        """Load all snapshots from a directory (sorted by day)."""
        snap_dir = Path(snap_dir)
        paths = sorted(snap_dir.glob("snap_*.json"))
        if not paths:
            paths = sorted(snap_dir.glob("agents_day_*.json"))
        self.snapshots = paths
        if paths:
            self.current_day = 0
            self.day_text.text = f"Day: {self.current_day}"
            print(f"  Loaded {len(paths)} snapshots")

    def update(self):
        """Called every frame by Ursina (via _viewer_instance)."""
        self.fps_text.text = f"FPS: {round(1 / time.dt) if time.dt > 0 else '--'}"

        p = camera.position
        self.pos_text.text = f"Pos: ({p.x:.0f}, {p.y:.0f}, {p.z:.0f})"

        if held_keys["p"] and not self._p_key_held:
            self.is_paused = not self.is_paused
            self.pause_text.text = "|| PAUSED" if self.is_paused else ""
            self._p_key_held = True
        if not held_keys["p"]:
            self._p_key_held = False

        if held_keys["+"] or held_keys["="]:
            self.play_speed = min(10.0, self.play_speed + 0.1)
            self.speed_text.text = f"Speed: {self.play_speed:.1f}x"
        if held_keys["-"]:
            self.play_speed = max(0.1, self.play_speed - 0.1)
            self.speed_text.text = f"Speed: {self.play_speed:.1f}x"

        if not self.is_paused and self.snapshots:
            step_every = max(1, int(10 / self.play_speed))
            self._frame_count += 1
            if self._frame_count >= step_every:
                self._frame_count = 0
                self._advance_day()

        # Camera orbit controls (only when not following)
        if not self.follow_mode:
            self._orbit_camera()

        # F key: toggle follow-camera mode
        if held_keys["f"] and not self._f_key_held:
            self._f_key_held = True
            if self.follow_mode:
                self.follow_mode = False
                self.follow_target = None
            else:
                target = self._get_follow_target()
                if target:
                    self.follow_mode = True
                    self.follow_target = target
                    self.follow_text.text = f"Seguint: {target.nick}"
        if not held_keys["f"]:
            self._f_key_held = False

        # Click on empty space to deselect
        if mouse.left and mouse.hovered_entity is None and self.selected_agent:
            self.deselect_agent()

        # Follow-camera update
        if self.follow_mode and self.follow_target:
            self._update_follow_camera()
            self.follow_text.text = f"Seguint: {self.follow_target.nick}"
        else:
            self.follow_text.text = ""

    def _advance_day(self):
        """Advance to the next snapshot day (loops when reaching the end)."""
        if not self.snapshots:
            return
        snap_path = self.snapshots[self.current_day]
        self.load_snapshot(snap_path)
        self.day_text.text = f"Day: {self.current_day}"
        self.current_day += 1
        if self.current_day >= len(self.snapshots):
            self.current_day = 0


def _init_display(headless=False):
    """Configure Panda3D display backend before Ursina() is created.

    - Non-headless: let Panda3D auto-detect (GPU/OpenGL when available).
    - Headless (server/CI): force p3tinydisplay software renderer + offscreen.
    """
    try:
        from panda3d.core import loadPrcFileData

        if headless:
            loadPrcFileData("", "load-display p3tinydisplay")
            loadPrcFileData("", "window-type offscreen")
    except ImportError:
        pass


def main():
    p = argparse.ArgumentParser(description="Interactive 3D terrain viewer")
    p.add_argument(
        "--mesh",
        type=str,
        default="output/terrain_mesh",
        help="Directory with terrain.obj",
    )
    p.add_argument(
        "--step", type=int, default=2, help="Subsampling step (match mesh export)"
    )
    p.add_argument(
        "--vertical-scale",
        type=float,
        default=0.03,
        help="Vertical exaggeration (match mesh export)",
    )
    p.add_argument(
        "--snapshots", type=str, default=None, help="Directory with agent snapshots"
    )
    p.add_argument("--no-grid", action="store_true", help="Hide reference grid")
    p.add_argument(
        "--headless",
        action="store_true",
        help="Run without a visible window (offscreen rendering)",
    )
    args = p.parse_args()

    global _viewer_instance
    _viewer_instance = None

    _init_display(headless=args.headless)
    ursina_app = Ursina()

    print("=" * 60)
    print("  3D TERRAIN VIEWER — Alt Pirineu")
    print("=" * 60)

    viewer = TerrainViewer(
        mesh_dir=args.mesh,
        vertical_scale=args.vertical_scale,
        step=args.step,
        show_grid=not args.no_grid,
    )
    _viewer_instance = viewer

    import ursina_models

    ursina_models.on_click_callback = viewer.select_agent

    if args.snapshots:
        print(f"Loading snapshots from {args.snapshots}...")
        viewer.load_snapshot_sequence(args.snapshots)

    print("\nControls: WASD=move Q/E=height R=reset P=pause +/-=speed")
    print("Running...")
    ursina_app.run()


if __name__ == "__main__":
    main()
