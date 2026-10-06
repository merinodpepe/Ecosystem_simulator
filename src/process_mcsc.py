#!/usr/bin/env python3
"""
MCSC Habitat Map Processor for the full Parc Natural de l'Alt Pirineu.
Downloads MCSC data via ICGC WFS, classifies 44 classes → 10 functional types,
rasterizes to simulation grid.

Usage:
  python process_mcsc.py [--bbox lon_min lat_min lon_max lat_max] [--resolution 25]

Default bbox covers the full PNAP (~80,000 ha).
"""

import os
import sys
import argparse
import json

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import shape
from shapely.ops import unary_union

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ecosystem", "data")
)

# ── Complete MCSC (44 classes) → 10 functional habitat types ──

FUNCTIONAL_HABITATS = {
    1: "BOSQUE_CON",
    2: "BOSQUE_CAD",
    3: "MATORRAL",
    4: "PASTIZAL",
    5: "HUMEDAL",
    6: "ROCA",
    7: "AGUA",
    8: "RIBERA",
    9: "NIEVE",
    10: "ANTROPICO",
}

HABITAT_CODES = {v: k for k, v in FUNCTIONAL_HABITATS.items()}

# MCSC Level-4 codes (full Catalan land cover classification, 44 classes)
# Source: https://www.icgc.cat/Descarregues/Cobertes-del-sol/Mapa-de-cobertes-del-sol-de-Catalunya-MCSC
# Mapping: MCSC code → (functional_habitat_code, functional_habitat_name, description)
MCSC_MAPPING = {
    # Urban / Artificial (1xx)
    111: (10, "ANTROPICO", "Teixit urbà continu"),
    112: (10, "ANTROPICO", "Teixit urbà discontinu"),
    121: (10, "ANTROPICO", "Zones industrials i comercials"),
    122: (10, "ANTROPICO", "Xarxes viàries i ferroviàries"),
    131: (10, "ANTROPICO", "Zones d'extracció minera"),
    132: (10, "ANTROPICO", "Abocadors"),
    133: (10, "ANTROPICO", "Zones en construcció"),
    141: (10, "ANTROPICO", "Zones verdes urbanes"),
    142: (10, "ANTROPICO", "Instal·lacions esportives i recreatives"),
    # Agricultural (2xx)
    211: (4, "PASTIZAL", "Cultius herbacis de secà"),
    212: (4, "PASTIZAL", "Cultius herbacis de regadiu"),
    221: (4, "PASTIZAL", "Vinyes"),
    222: (4, "PASTIZAL", "Fruiters"),
    223: (4, "PASTIZAL", "Oliveres"),
    231: (4, "PASTIZAL", "Pastures i prats naturals"),
    241: (4, "PASTIZAL", "Cultius anuals associats amb cultius permanents"),
    242: (4, "PASTIZAL", "Mosaic de cultius"),
    243: (4, "PASTIZAL", "Terrenys principalment agrícoles amb vegetació natural"),
    # Forest and semi-natural (3xx)
    311: (
        1,
        "BOSQUE_CON",
        "Boscos de coníferes (Pinus uncinata, P. sylvestris, Abies alba)",
    ),
    312: (
        1,
        "BOSQUE_CON",
        "Boscos de coníferes (Pinus nigra, P. halepensis, P. pinea)",
    ),
    313: (
        2,
        "BOSQUE_CAD",
        "Boscos de caducifolis (Fagus sylvatica, Quercus spp., Betula)",
    ),
    314: (2, "BOSQUE_CAD", "Boscos mixtos de coníferes i caducifolis"),
    321: (3, "MATORRAL", "Pastures i matollars"),
    322: (3, "MATORRAL", "Matollars (Rhododendron ferrugineum, Vaccinium, Calluna)"),
    323: (3, "MATORRAL", "Vegetació escleròfila (màquia, garriga)"),
    324: (3, "MATORRAL", "Matollars de transició i clarianes forestals"),
    325: (4, "PASTIZAL", "Prats i herbagens"),
    331: (6, "ROCA", "Roques nues, tarteres, canyars"),
    332: (6, "ROCA", "Roques nues (glacials, periglacials)"),
    333: (9, "NIEVE", "Neu permanent i glaceres"),
    334: (5, "HUMEDAL", "Zones cremades"),
    # Wetlands (4xx)
    411: (5, "HUMEDAL", "Molleres i aiguamolls d'alta muntanya"),
    412: (5, "HUMEDAL", "Torberes"),
    421: (5, "HUMEDAL", "Maresmes i salins"),
    # Water bodies (5xx)
    511: (7, "AGUA", "Llacs i estanys"),
    512: (7, "AGUA", "Embassaments"),
    521: (7, "AGUA", "Rius i rierols"),
    522: (8, "RIBERA", "Boscos de ribera"),
    523: (7, "AGUA", "Canals i basses artificials"),
    # Additional MCSC-specific classes (from detailed ICGC legend)
    # PNA = Pineda de pi negre (Pinus uncinata) - key in PNAP subalpine
    501: (1, "BOSQUE_CON", "Pineda de pi negre (Pinus uncinata)"),
    502: (1, "BOSQUE_CON", "Pineda de pi roig (Pinus sylvestris)"),
    503: (1, "BOSQUE_CON", "Avetosa (Abies alba)"),
    504: (2, "BOSQUE_CAD", "Fageda (Fagus sylvatica)"),
    505: (2, "BOSQUE_CAD", "Bedollar (Betula pubescens)"),
    506: (3, "MATORRAL", "Matollar de rododèndron (Rhododendron ferrugineum)"),
    507: (3, "MATORRAL", "Matollar de nabiu (Vaccinium myrtillus)"),
}

# Inverse mapping for the classes currently found in the Vall de Cardós
# (28 classes that were mapped in the original terrain_habitat_explicacio.md)
VALL_CARDOS_MCSC_CODES = [
    311,
    312,
    313,
    314,  # forests
    321,
    322,
    324,
    325,  # matorral/pasture
    411,
    421,  # wetlands
    511,
    512,
    521,
    522,  # water/riparian
    331,
    332,
    333,  # rock/snow
    111,
    112,
    121,
    131,  # anthropic
    211,
    231,
    242,
    243,  # agriculture/pasture
    501,
    502,
    503,
    504,  # detailed forest
]


def download_mcsc_wfs(bbox, output_gml):
    """Download MCSC polygons from ICGC WFS."""
    import requests

    lon_min, lat_min, lon_max, lat_max = bbox
    url = "https://geoserveis.icgc.cat/geoserver/wfs"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "inspire:LC.LandCoverSurfaces",
        "bbox": f"{lon_min},{lat_min},{lon_max},{lat_max},EPSG:4326",
        "outputFormat": "application/json",
        "count": "10000",
    }
    print(f"  Downloading MCSC data for bbox {bbox}...")
    resp = requests.get(url, params=params, timeout=300)
    resp.raise_for_status()
    with open(output_gml, "wb") as f:
        f.write(resp.content)
    print(f"  Downloaded {len(resp.content)} bytes to {output_gml}")


def parse_mcsc_geojson(geojson_path):
    """Parse MCSC GeoJSON features and map to functional habitat types."""
    with open(geojson_path) as f:
        data = json.load(f)

    features = []
    mapped = {}
    unmapped_codes = set()

    for feat in data.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry")

        # Try different MCSC code fields
        mcsc_code = (
            props.get("lc_code") or props.get("inspire:lc_code") or props.get("code")
        )
        if mcsc_code is None:
            # Try to extract from other fields
            for key in props:
                if "code" in key.lower() or "lc" in key.lower():
                    mcsc_code = props[key]
                    break

        if mcsc_code is None:
            continue

        try:
            mcsc_code = int(mcsc_code)
        except (ValueError, TypeError):
            continue

        # Map to functional habitat
        mapping = MCSC_MAPPING.get(mcsc_code)
        if mapping is None:
            unmapped_codes.add(mcsc_code)
            continue

        hab_code, hab_name, desc = mapping
        if hab_code not in mapped:
            mapped[hab_code] = {"name": hab_name, "count": 0, "mcsc_codes": set()}
        mapped[hab_code]["count"] += 1
        mapped[hab_code]["mcsc_codes"].add(mcsc_code)

        if geom and geom.get("type") in ("Polygon", "MultiPolygon"):
            features.append(
                {
                    "geometry": shape(geom),
                    "properties": {"habitat_code": hab_code, "habitat_name": hab_name},
                }
            )

    return features, mapped, unmapped_codes


def rasterize_habitats(features, bounds, resolution, width, height):
    """Rasterize habitat polygons to a grid."""
    transform = from_bounds(
        bounds[0],
        bounds[1],
        bounds[2],
        bounds[3],
        width,
        height,
    )
    shapes = [
        (feat["geometry"], feat["properties"]["habitat_code"]) for feat in features
    ]
    raster = rasterize(
        shapes,
        out_shape=(height, width),
        transform=transform,
        fill=0,
        dtype=np.int32,
    )
    return raster, transform


def estimate_grid_dimensions(bbox, resolution):
    """Estimate grid dimensions from bounding box and resolution (meters)."""
    from rasterio.warp import transform as warp_transform
    from rasterio.crs import CRS

    lon_min, lat_min, lon_max, lat_max = bbox
    # Central latitude for UTM zone
    src_crs = CRS.from_epsg(4326)
    dst_crs = CRS.from_epsg(25831)

    # Transform corners to target CRS
    xs = [lon_min, lon_max]
    ys = [lat_min, lat_max]
    x_trans, y_trans = warp_transform(src_crs, dst_crs, xs, ys)

    width = int(abs(x_trans[1] - x_trans[0]) / resolution)
    height = int(abs(y_trans[1] - y_trans[0]) / resolution)

    bounds_25831 = (min(x_trans), min(y_trans), max(x_trans), max(y_trans))
    return width, height, bounds_25831


def save_raster(raster, transform, crs, path):
    """Save raster to GeoTIFF."""
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=raster.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(raster, 1)
    print(f"  Saved: {path} ({raster.shape[1]}×{raster.shape[0]})")


def print_mapping_summary(mapped, unmapped_codes):
    """Print summary of MCSC → habitat mapping."""
    print("\n  MCSC → Habitat Mapping Summary:")
    print(f"  {'Habitat Code':<15} {'Name':<20} {'MCSC Classes':<15} {'Polygons':<10}")
    print(f"  {'-' * 60}")
    for code in sorted(mapped.keys()):
        info = mapped[code]
        print(
            f"  {code:<15} {info['name']:<20} {len(info['mcsc_codes']):<15} {info['count']:<10}"
        )

    if unmapped_codes:
        print(f"\n  ⚠ Unmapped MCSC codes: {sorted(unmapped_codes)}")


def generate_biomass_raster(habitat_raster, out_path):
    """Generate biomass initial values per cell based on habitat type."""
    biomass_config = {
        1: {
            "P1": 1.5,
            "P2": 0.3,
            "P3": 0.5,
            "I1": 0.02,
            "I2": 0.15,
            "I3": 0.08,
        },  # BOSQUE_CON
        2: {
            "P1": 1.0,
            "P2": 0.3,
            "P3": 0.5,
            "I1": 0.015,
            "I2": 0.08,
            "I3": 0.05,
        },  # BOSQUE_CAD
        3: {
            "P1": 2.0,
            "P2": 0.2,
            "P3": 1.5,
            "I1": 0.03,
            "I2": 0.08,
            "I3": 0.05,
        },  # MATORRAL
        4: {
            "P1": 1.0,
            "P2": 0.1,
            "P3": 4.0,
            "I1": 0.03,
            "I2": 0.15,
            "I3": 0.06,
        },  # PASTIZAL
        5: {
            "P1": 2.0,
            "P2": 1.0,
            "P3": 0.5,
            "I1": 0.025,
            "I2": 0.06,
            "I3": 0.04,
        },  # HUMEDAL
        6: {
            "P1": 0.2,
            "P2": 0.15,
            "P3": 0.0,
            "I1": 0.005,
            "I2": 0.01,
            "I3": 0.01,
        },  # ROCA
        7: {"P1": 0.0, "P2": 1.0, "P3": 0.0, "I1": 0.0, "I2": 0.02, "I3": 0.01},  # AGUA
        8: {
            "P1": 1.0,
            "P2": 0.8,
            "P3": 1.5,
            "I1": 0.02,
            "I2": 0.08,
            "I3": 0.05,
        },  # RIBERA
        9: {"P1": 0.0, "P2": 0.0, "P3": 0.0, "I1": 0.0, "I2": 0.0, "I3": 0.0},  # NIEVE
        10: {
            "P1": 0.1,
            "P2": 0.05,
            "P3": 0.2,
            "I1": 0.005,
            "I2": 0.005,
            "I3": 0.005,
        },  # ANTROPICO
    }
    biomass_names = ["P1_max", "P2_max", "P3_max", "I1", "I2", "I3"]
    bands = []
    for bname in biomass_names:
        band = np.zeros_like(habitat_raster, dtype=np.float32)
        for hab_code, config in biomass_config.items():
            mask = habitat_raster == hab_code
            if bname.startswith("P"):
                band[mask] = config[bname]
            else:
                band[mask] = config[bname]
        bands.append(band)
    biomass_stack = np.stack(bands, axis=0)

    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=habitat_raster.shape[0],
        width=habitat_raster.shape[1],
        count=len(bands),
        dtype=np.float32,
        crs="EPSG:25831",
    ) as dst:
        for i, band in enumerate(bands):
            dst.write(band, i + 1)
    print(f"  Saved biomass: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Process MCSC habitat data for PNAP")
    parser.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        default=[0.95, 42.35, 1.50, 42.75],
        help="Bounding box lon_min lat_min lon_max lat_max",
    )
    parser.add_argument(
        "--resolution", type=float, default=25.0, help="Target resolution in meters"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to existing MCSC GeoJSON (skip download)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  MCSC HABITAT MAP PROCESSOR — PNAP")
    print("=" * 60)

    bbox = tuple(args.bbox)
    print(f"\n  Bounding box: {bbox}")
    print(f"  Resolution: {args.resolution}m")

    # Estimate grid
    width, height, bounds_25831 = estimate_grid_dimensions(bbox, args.resolution)
    print(f"  Grid: {width}×{height} cells ({width * height / 1e6:.1f}M cells)")

    geojson_path = args.input or os.path.join(DATA_DIR, "mcsc_raw.geojson")

    if args.input is None and not os.path.exists(geojson_path):
        download_mcsc_wfs(bbox, geojson_path)
    else:
        print(f"  Using existing file: {geojson_path}")

    # Parse features
    print("\n[*] Parsing MCSC features...")
    features, mapped, unmapped_codes = parse_mcsc_geojson(geojson_path)
    print(f"  Parsed {len(features)} features from {len(mapped)} habitat classes")
    print_mapping_summary(mapped, unmapped_codes)

    # Rasterize
    print("\n[*] Rasterizing habitats...")
    hab_raster, transform = rasterize_habitats(
        features, bounds_25831, args.resolution, width, height
    )
    print(f"  Raster shape: {hab_raster.shape}")

    # Save habitat map
    hab_path = os.path.join(DATA_DIR, "terrain_habitat.tif")
    save_raster(hab_raster, transform, "EPSG:25831", hab_path)

    # Generate biomass
    print("\n[*] Generating biomass layers...")
    biomass_path = os.path.join(DATA_DIR, "terrain_biomass.tif")
    generate_biomass_raster(hab_raster, biomass_path)

    # Area breakdown
    print("\n[*] Area breakdown:")
    print(f"  {'Habitat':<20} {'Cells':<12} {'Area (ha)':<12} {'%':<8}")
    print(f"  {'-' * 52}")
    total_cells = hab_raster.size
    for code in sorted(FUNCTIONAL_HABITATS.keys()):
        count = int(np.sum(hab_raster == code))
        area_ha = count * args.resolution * args.resolution / 10000
        pct = count / total_cells * 100 if total_cells > 0 else 0
        print(
            f"  {FUNCTIONAL_HABITATS[code]:<20} {count:<12} {area_ha:<12.1f} {pct:<8.1f}"
        )

    print("\n" + "=" * 60)
    print("  MCSC PROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
