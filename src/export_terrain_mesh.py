#!/usr/bin/env python3
"""
Export terrain DEM as 3D mesh (OBJ + texture) for Ursina viewer.

Usage:
    python src/export_terrain_mesh.py
        --step 2
        --vertical-scale 0.03
        --color-by elevation
        --output output/terrain_mesh
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
import matplotlib

DATA_DIR = Path("ecosystem/data")
TSV_PATH = DATA_DIR / "terrain_cells.tsv"


def load_elevation_grid(tsv_path, step=1):
    """Load TSV and return 2D elevation array (subsampled by step)."""
    df = pd.read_csv(tsv_path, sep="\t")
    W, H = df["x"].max() + 1, df["y"].max() + 1
    elev = np.full((H, W), np.nan)
    elev[df["y"].values, df["x"].values] = df["elevation_m"].values
    if step > 1:
        elev = elev[::step, ::step]
    return elev


class TerrainMesh:
    """Generates a 3D mesh from a 2D elevation grid."""

    def __init__(self, elev, vertical_scale=0.03, step=1):
        self.elev = elev
        self.scale = vertical_scale
        self.step = step
        self.H, self.W = elev.shape
        self.vertices = []
        self.uvs = []
        self.triangles = []
        self.normals = []
        self.vertex_colors = []
        self.valid_mask = None
        self._build()

    def _vert_index(self, row, col):
        return row * self.W + col

    def _is_valid(self, row, col):
        return not np.isnan(self.elev[row, col])

    def _build(self):
        """Build vertices, triangles, UVs, normals, and colors."""
        # 1. Build vertex list and valid mask
        self.vertices = np.zeros((self.H * self.W, 3), dtype=np.float32)
        self.uvs = np.zeros((self.H * self.W, 2), dtype=np.float32)
        self.valid_mask = np.zeros(self.H * self.W, dtype=bool)
        self.vertex_colors = np.zeros((self.H * self.W, 3), dtype=np.float32)

        for y in range(self.H):
            for x in range(self.W):
                idx = self._vert_index(y, x)
                ev = self.elev[y, x]
                if np.isnan(ev):
                    continue
                self.valid_mask[idx] = True
                # Vértice: (x, elev * scale, -y)
                self.vertices[idx] = [float(x), float(ev) * self.scale, -float(y)]
                # UV
                self.uvs[idx] = [x / self.W, y / self.H]

        # 2. Build triangle list
        valid_verts = self.valid_mask.reshape(self.H, self.W)
        for y in range(self.H - 1):
            for x in range(self.W - 1):
                if (
                    valid_verts[y, x]
                    and valid_verts[y + 1, x]
                    and valid_verts[y, x + 1]
                    and valid_verts[y + 1, x + 1]
                ):
                    i00 = self._vert_index(y, x)
                    i10 = self._vert_index(y + 1, x)
                    i01 = self._vert_index(y, x + 1)
                    i11 = self._vert_index(y + 1, x + 1)
                    self.triangles.append((i00, i10, i01))
                    self.triangles.append((i10, i11, i01))

        self.triangles = np.array(self.triangles, dtype=np.int32)

        # 3. Compute normals
        self._compute_normals()

        # 4. Compute vertex colors by elevation
        self._compute_colors()

    def _compute_normals(self):
        """Compute vertex normals as average of face normals."""
        face_normals = np.zeros((len(self.triangles), 3), dtype=np.float32)
        for i, (i0, i1, i2) in enumerate(self.triangles):
            v0, v1, v2 = self.vertices[i0], self.vertices[i1], self.vertices[i2]
            face_normals[i] = np.cross(v1 - v0, v2 - v0)
            norm = np.linalg.norm(face_normals[i])
            if norm > 0:
                face_normals[i] /= norm

        self.normals = np.zeros_like(self.vertices)
        count = np.zeros(len(self.vertices), dtype=np.int32)
        for i, (i0, i1, i2) in enumerate(self.triangles):
            self.normals[i0] += face_normals[i]
            self.normals[i1] += face_normals[i]
            self.normals[i2] += face_normals[i]
            count[i0] += 1
            count[i1] += 1
            count[i2] += 1

        valid_norm = count > 0
        self.normals[valid_norm] /= count[valid_norm, np.newaxis]
        norms = np.linalg.norm(self.normals[valid_norm], axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.normals[valid_norm] /= norms

    def _compute_colors(self, colormap="terrain"):
        """Color vertices by elevation using a matplotlib colormap."""
        valid_vals = self.elev[~np.isnan(self.elev)]
        vmin, vmax = valid_vals.min(), valid_vals.max()
        cmap = matplotlib.colormaps[colormap]
        for y in range(self.H):
            for x in range(self.W):
                idx = self._vert_index(y, x)
                if not self.valid_mask[idx]:
                    continue
                ev = self.elev[y, x]
                t = (ev - vmin) / (vmax - vmin) if vmax > vmin else 0.5
                r, g, b, _ = cmap(t)
                self.vertex_colors[idx] = [r, g, b]

    def export_obj(self, path):
        """Export mesh as Wavefront OBJ + MTL."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        obj_path = path.with_suffix(".obj")
        mtl_path = path.with_suffix(".mtl")
        tex_path = path.parent / f"{path.stem}_texture.png"

        valid_idx = np.where(self.valid_mask)[0]
        old_to_new = {old: new for new, old in enumerate(valid_idx)}

        with open(obj_path, "w") as f:
            f.write(f"# Terrain mesh - step={self.step} scale={self.scale}\n")
            f.write(f"# Vertices: {len(valid_idx)}, Triangles: {len(self.triangles)}\n")
            f.write(f"mtllib {mtl_path.name}\n\n")

            for old in valid_idx:
                v = self.vertices[old]
                f.write(f"v {v[0]:.3f} {v[1]:.3f} {v[2]:.3f}\n")
            f.write("\n")

            for old in valid_idx:
                uv = self.uvs[old]
                f.write(f"vt {uv[0]:.6f} {uv[1]:.6f}\n")
            f.write("\n")

            for old in valid_idx:
                n = self.normals[old]
                f.write(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")
            f.write("\n")

            f.write("usemtl terrain_material\n")
            for tri in self.triangles:
                i0, i1, i2 = (
                    old_to_new[int(tri[0])] + 1,
                    old_to_new[int(tri[1])] + 1,
                    old_to_new[int(tri[2])] + 1,
                )
                f.write(f"f {i0}/{i0}/{i0} {i1}/{i1}/{i1} {i2}/{i2}/{i2}\n")

        # MTL
        tex_rel = tex_path.name
        with open(mtl_path, "w") as f:
            f.write("newmtl terrain_material\n")
            f.write(f"map_Kd {tex_rel}\n")
            f.write("Kd 0.9 0.9 0.9\n")
            f.write("Ka 0.2 0.2 0.2\n")
            f.write("Ks 0.1 0.1 0.1\n")
            f.write("Ns 10.0\n")
            f.write("illum 2\n")

        # Texture
        self._export_texture(tex_path)

        return obj_path, mtl_path, tex_path

    def _export_texture(self, path, tex_size=1024):
        """Bake vertex colors to a PNG texture."""
        img = Image.new("RGB", (tex_size, tex_size))
        pixels = img.load()
        for py in range(tex_size):
            for px in range(tex_size):
                gx = px * self.W / tex_size
                gy = py * self.H / tex_size
                ix, iy = int(gx), int(gy)
                ix = min(ix, self.W - 1)
                iy = min(iy, self.H - 1)
                idx = self._vert_index(iy, ix)
                if self.valid_mask[idx]:
                    r, g, b = (int(c * 255) for c in self.vertex_colors[idx])
                else:
                    r, g, b = 200, 200, 200
                pixels[px, tex_size - 1 - py] = (r, g, b)
        img.save(path)

    def summary(self):
        n_valid = int(self.valid_mask.sum())
        n_tri = len(self.triangles)
        valid_vals = self.elev[~np.isnan(self.elev)]
        return {
            "grid": f"{self.W}x{self.H}",
            "step": self.step,
            "scale": self.scale,
            "vertices": n_valid,
            "triangles": n_tri,
            "elevation_min": float(valid_vals.min()),
            "elevation_max": float(valid_vals.max()),
            "elevation_mean": float(valid_vals.mean()),
        }


def main():
    p = argparse.ArgumentParser(description="Export terrain DEM as 3D mesh")
    p.add_argument("--step", type=int, default=2, help="Subsampling factor (1=full)")
    p.add_argument(
        "--vertical-scale",
        type=float,
        default=0.03,
        help="Vertical exaggeration for 3D mesh",
    )
    p.add_argument("--color-by", choices=["elevation"], default="elevation")
    p.add_argument(
        "--output",
        "-o",
        type=str,
        default="output/terrain_mesh",
        help="Output directory",
    )
    args = p.parse_args()

    out_dir = Path(args.output)

    print("=" * 60)
    print("  TERRAIN MESH EXPORTER")
    print("=" * 60)

    print(f"\nLoading elevation (step={args.step})...")
    elev = load_elevation_grid(TSV_PATH, step=args.step)
    print(f"  Grid: {elev.shape[1]}x{elev.shape[0]}")
    print(f"  Elevation: {np.nanmin(elev):.0f}-{np.nanmax(elev):.0f} m")

    print(f"\nBuilding mesh (scale={args.vertical_scale})...")
    mesh = TerrainMesh(elev, vertical_scale=args.vertical_scale, step=args.step)
    s = mesh.summary()
    print(f"  Vertices: {s['vertices']:,}")
    print(f"  Triangles: {s['triangles']:,}")

    print(f"\nExporting to {out_dir}...")
    obj_path, mtl_path, tex_path = mesh.export_obj(out_dir / "terrain.obj")
    print(f"  OBJ: {obj_path}")
    print(f"  MTL: {mtl_path}")
    print(f"  Texture: {tex_path}")

    meta_path = out_dir / "terrain_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(s, f, indent=2)
    print(f"  Metadata: {meta_path}")

    print(f"\n{'=' * 60}")
    print(f"  DONE — {s['vertices']:,} vertices, {s['triangles']:,} triangles")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
