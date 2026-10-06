"""
Pipeline de procesamiento del terreno:
SRTM 30m -> recorte a subcuenca Vall de Cardós -> reproyección EPSG:25831 25m
-> pendiente, aspecto, TRI, pisos bioclimáticos

Referencia: ecosistema/wiki/plan_terreno_simulacion.md
"""

import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.transform import from_bounds

# === CONFIGURACIÓN ===
SRTM_PATH = Path("data/terrain/srtm_n42e001.tif")
OUT_DIR = Path("ecosystem/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Bounding box (EPSG:4326) - Vall de Cardós subcuenca
LON_MIN, LON_MAX = 1.244306, 1.355417
LAT_MIN, LAT_MAX = 42.544583, 42.655694

TARGET_RES = 25.0
TARGET_CRS = "EPSG:25831"
NODATA_F32 = -32768.0


def crop_reproject_dem():
    """Read SRTM window in EPSG:4326, reproject to EPSG:25831 at 25m."""
    out_path = OUT_DIR / "terrain_dem_25m.tif"

    with rasterio.open(SRTM_PATH) as src:
        window = src.window(LON_MIN, LAT_MIN, LON_MAX, LAT_MAX)
        src_data = src.read(1, window=window)

        if src.nodata is not None:
            src_data = np.where(src_data == src.nodata, -32768, src_data)

        # Transform of the windowed read (EPSG:4326)
        w_transform = src.window_transform(window)

        # Destination transform & dimensions in EPSG:25831
        dst_transform, dst_width, dst_height = calculate_default_transform(
            src.crs,
            TARGET_CRS,
            src_data.shape[1],
            src_data.shape[0],
            LON_MIN,
            LAT_MIN,
            LON_MAX,
            LAT_MAX,
            resolution=TARGET_RES,
        )

        print(f"  Cuenca: {LON_MIN:.4f}E-{LON_MAX:.4f}E, {LAT_MIN:.4f}N-{LAT_MAX:.4f}N")
        print(f"  Grid: {dst_width}x{dst_height} celdas a {TARGET_RES}m")
        print(
            f"  Área: {dst_width * TARGET_RES / 1000:.1f} x {dst_height * TARGET_RES / 1000:.1f} km"
        )

        # Reproject
        dst_data = np.empty((dst_height, dst_width), dtype=np.float32)
        reproject(
            source=src_data.astype(np.float32),
            src_crs=src.crs,
            src_transform=w_transform,
            destination=dst_data,
            dst_crs=TARGET_CRS,
            dst_transform=dst_transform,
            dst_resolution=TARGET_RES,
            resampling=Resampling.bilinear,
        )

        # Clean border artifacts: set very low or negative values to nodata
        dst_data[dst_data < 500.0] = NODATA_F32
        dst_data = np.where(np.isnan(dst_data), NODATA_F32, dst_data)

        profile = {
            "driver": "GTiff",
            "height": dst_height,
            "width": dst_width,
            "count": 1,
            "dtype": "float32",
            "crs": TARGET_CRS,
            "transform": dst_transform,
            "nodata": NODATA_F32,
            "compress": "lzw",
        }
        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(dst_data, 1)

        print(f"  Guardado: {out_path}")
        return dst_data, dst_transform, TARGET_CRS, dst_width, dst_height


def compute_slope(dem, res):
    valid = np.where(dem == NODATA_F32, 0.0, dem)
    padded = np.pad(valid, 1, mode="edge")
    dzdx = (padded[1:-1, 2:] - padded[1:-1, :-2]) / (2 * res)
    dzdy = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / (2 * res)
    slope = np.degrees(np.arctan(np.sqrt(dzdx**2 + dzdy**2)))
    slope = np.clip(slope, 0, 90)
    slope[dem == NODATA_F32] = NODATA_F32
    return slope.astype(np.float32)


def compute_aspect(dem):
    valid = np.where(dem == NODATA_F32, 0.0, dem)
    padded = np.pad(valid, 1, mode="edge")
    dzdx = (padded[1:-1, 2:] - padded[1:-1, :-2]) / 2
    dzdy = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / 2
    aspect = np.degrees(np.arctan2(dzdy, -dzdx))
    aspect = np.where(aspect < 0, aspect + 360, aspect)
    aspect[(dzdx == 0) & (dzdy == 0)] = -1
    aspect[dem == NODATA_F32] = NODATA_F32
    return aspect.astype(np.float32)


def compute_tri(dem):
    valid = np.where(dem == NODATA_F32, 0.0, dem.astype(np.float64))
    padded = np.pad(valid, 1, mode="edge")
    neighbors = np.stack(
        [
            padded[:-2, :-2],
            padded[:-2, 1:-1],
            padded[:-2, 2:],
            padded[1:-1, :-2],
            padded[1:-1, 2:],
            padded[2:, :-2],
            padded[2:, 1:-1],
            padded[2:, 2:],
        ]
    )
    diff_sq = (neighbors - valid[np.newaxis, :, :]) ** 2
    tri = np.sqrt(np.mean(diff_sq, axis=0))
    tri[dem == NODATA_F32] = NODATA_F32
    return tri.astype(np.float32)


def classify_pisos(dem):
    piso = np.zeros_like(dem, dtype=np.int32)
    piso[(dem >= 650) & (dem < 1600)] = 1
    piso[(dem >= 1600) & (dem < 2300)] = 2
    piso[(dem >= 2300) & (dem < 2700)] = 3
    piso[dem >= 2700] = 4
    piso[dem == NODATA_F32] = -32768
    return piso


def save_raster(data, path, transform, crs, dtype="float32"):
    profile = {
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "nodata": NODATA_F32,
        "compress": "lzw",
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data, 1)
    print(f"  Guardado: {path}")


def export_tsv(dem, slope, aspect, tri, piso, transform, out_path):
    h, w = dem.shape
    rows = []
    for y in range(h):
        for x in range(w):
            v = dem[y, x]
            if v == NODATA_F32:
                continue
            ux = transform.c + x * transform.a + y * transform.b
            uy = transform.f + x * transform.d + y * transform.e
            rows.append(
                f"{x}\t{y}\t{ux:.1f}\t{uy:.1f}\t{v:.1f}\t{slope[y, x]:.1f}\t{aspect[y, x]:.1f}\t{tri[y, x]:.1f}\t{piso[y, x]}\n"
            )

    header = "x\ty\tutm_x\tutm_y\televation_m\tslope_deg\taspect_deg\ttri\tpiso\n"
    with open(out_path, "w") as f:
        f.write(header)
        f.writelines(rows)
    print(f"  Guardado TSV: {out_path}")


def main():
    print("=" * 60)
    print("PROCESAMIENTO DE TERRENO — PNAP Vall de Cardós")
    print("=" * 60)

    print("\n[1/5] Recorte y reproyección DEM...")
    dem, transform, crs, w, h = crop_reproject_dem()

    print("\n[2/5] Pendiente (slope)...")
    slope = compute_slope(dem, TARGET_RES)
    save_raster(slope, OUT_DIR / "terrain_slope.tif", transform, crs)

    print("\n[3/5] Orientación (aspect)...")
    aspect = compute_aspect(dem)
    save_raster(aspect, OUT_DIR / "terrain_aspect.tif", transform, crs)

    print("\n[4/5] Rugosidad (TRI)...")
    tri = compute_tri(dem)
    save_raster(tri, OUT_DIR / "terrain_tri.tif", transform, crs)

    print("\n[5/5] Pisos bioclimáticos...")
    piso = classify_pisos(dem)
    save_raster(piso, OUT_DIR / "terrain_pisos.tif", transform, crs, dtype="int32")

    print("\nExportando TSV...")
    export_tsv(dem, slope, aspect, tri, piso, transform, OUT_DIR / "terrain_cells.tsv")

    # Summary
    valid = dem[dem != NODATA_F32]
    vs = slope[dem != NODATA_F32]
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print(f"  Grid: {w} x {h} = {w * h} celdas")
    print(f"  Celdas válidas: {len(valid)} ({100 * len(valid) / (w * h):.0f}%)")
    print(
        f"  Elevación: {valid.min():.0f} - {valid.max():.0f} m (media {valid.mean():.0f} m)"
    )
    print(f"  Pendiente: {vs.min():.1f} - {vs.max():.1f}° (media {vs.mean():.1f}°)")
    for code, name in [(1, "Montano"), (2, "Subalpino"), (3, "Alpino"), (4, "Nival")]:
        count = np.sum(piso == code)
        pct = 100 * count / len(valid) if len(valid) else 0
        print(f"  {name}: {count} celdas ({pct:.0f}%)")
    print("\nProcesamiento completado.")


if __name__ == "__main__":
    sys.exit(main())
