---
tags:
  - terrain
  - pipeline
  - srtm
  - mcsc
  - processing
  - gis
date: 2026-06-22
---
# Pipeline de Procesamiento del Terreno

**Resolución:** 25 m · **Proyección:** EPSG:25831 · **Grid:** 375 × 502 celdas (180.037 válidas) · **Área:** Vall de Cardós, ~11.800 ha

---

## Diagrama del Pipeline

```
SRTM GL1 30m (N42E001)
       │
       ▼
  Recorte (WGS84 bbox: 1.2443–1.3554°E, 42.5446–42.6557°N)
       │
       ▼
  Reproyección EPSG:25831 + resampling bilinear a 25m
       │
       ├──► terrain_dem_25m.tif        (DEM recortado y reproyectado)
       │
       ├──► Pendiente (slope)          Diferencia central, Zevenbergen & Thorne
       │       └── terrain_slope.tif
       │
       ├──► Orientación (aspect)       arctan2(dz/dy, -dz/dx)
       │       └── terrain_aspect.tif
       │
       ├──► Rugosidad (TRI)            RMS diferencias con 8 vecinos
       │       └── terrain_tri.tif
       │
       ├──► Pisos bioclimáticos        Clasificación por altitud
       │       └── terrain_pisos.tif   (1=Montano 2=Subalpino 3=Alpino 4=Nival)
       │
       └──► Exportación TSV            Grid completo por celda
               └── terrain_cells.tsv   (x, y, utm_x, utm_y, elevation_m,
                                        slope_deg, aspect_deg, tri, piso)
```

El mapa de hábitats se genera por separado via `process_mcsc.py`:

```
MCSC ICGC WFS (inspire:LC.LandCoverSurfaces)
       │
       ▼
  Descarga GeoJSON (44 clases de cobertura del suelo)
       │
       ▼
  Clasificación → 10 hábitats funcionales
       │
       ▼
  Rasterización a grid 25m (rasterio.features.rasterize)
       │
       ├──► terrain_habitat.tif        (códigos 1–10)
       │
       └──► terrain_biomass.tif        (6 bandas: P1_max, P2_max, P3_max, I1, I2, I3)
```

---

## 1. Procesamiento del DEM (`process_terrain.py`)

### 1.1 Fuente original
- **Tile SRTM GL1:** `srtm_n42e001.tif` — 30 m resolución, EPSG:4326
- **Cobertura original:** 1.0°E–2.0°E, 42.0°N–43.0°N (348–3.109 m)

### 1.2 Recorte y reproyección
```python
# Bounding box de la Vall de Cardós (EPSG:4326)
LON_MIN, LON_MAX = 1.244306, 1.355417
LAT_MIN, LAT_MAX = 42.544583, 42.655694

# Parámetros destino
TARGET_RES = 25.0        # resolución en metros
TARGET_CRS = "EPSG:25831"  # ETRS89 / UTM zone 31N
NODATA_F32 = -32768.0

# Resampling bilinear para el DEM
# Valores < 500 m se marcan como NODATA (eliminar bordes del tile)
```

### 1.3 Pendiente (`compute_slope`)
```python
# Diferencia central en ventana 3×3
dzdx = (padded[1:-1, 2:] - padded[1:-1, :-2]) / (2 * res)
dzdy = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / (2 * res)
slope = degrees(arctan(sqrt(dzdx² + dzdy²)))
# Clip a [0, 90] grados
```

### 1.4 Orientación (`compute_aspect`)
```python
dzdx = (padded[1:-1, 2:] - padded[1:-1, :-2]) / 2
dzdy = (padded[2:, 1:-1] - padded[:-2, 1:-1]) / 2
aspect = degrees(arctan2(dzdy, -dzdx))
# Ángulo 0–360°, -1 para terreno plano
```

### 1.5 TRI — Terrain Ruggedness Index (`compute_tri`)
```python
# RMS de diferencias entre celda y sus 8 vecinas
neighbors = [8 direcciones]
diff_sq = (neighbors - cell)²
tri = sqrt(mean(diff_sq))
```

### 1.6 Pisos bioclimáticos (`classify_pisos`)
| Piso | Rango (m) | Código | Celdas | % | Especies indicadoras |
|------|-----------|--------|--------|---|---------------------|
| Montano | 650–1.600 | 1 | 66.806 | 37% | *Cervus elaphus*, *Sus scrofa* |
| Subalpino | 1.600–2.300 | 2 | 91.827 | 51% | *Tetrao urogallus*, *Capreolus capreolus* |
| Alpino | 2.300–2.700 | 3 | 21.385 | 12% | *Rupicapra pyrenaica*, *Marmota marmota* |
| Nival | >2.700 | 4 | 19 | 0% | *Iberolacerta aurelioi* |

### 1.7 Exportación TSV (`export_tsv`)
Cada celda válida se exporta con: `x`, `y`, `utm_x`, `utm_y`, `elevation_m`, `slope_deg`, `aspect_deg`, `tri`, `piso`.

---

## 2. Procesamiento del Mapa de Hábitats (`process_mcsc.py`)

### 2.1 Descarga WFS
```
URL: https://geoserveis.icgc.cat/geoserver/wfs
TypeName: inspire:LC.LandCoverSurfaces
Formato: application/json (GeoJSON)
Bbox por defecto: 0.95, 42.35, 1.50, 42.75 (~80.000 ha, PNAP completo)
```

### 2.2 Clasificación 44 → 10 hábitats funcionales

| Código | Hábitat | Descripción | MCSC sources |
|--------|---------|-------------|--------------|
| 1 | BOSQUE_CON | Bosque de coníferas | 311, 312, 501, 502, 503 |
| 2 | BOSQUE_CAD | Bosque caducifolio | 313, 314, 504, 505 |
| 3 | MATORRAL | Matorral | 321, 322, 323, 324, 506, 507 |
| 4 | PASTIZAL | Pastizal alpino/subalpino | 211–243, 325 |
| 5 | HUMEDAL | Humedal / turbera | 411, 412, 421, 334 |
| 6 | ROCA | Roca / tartera | 331, 332 |
| 7 | AGUA | Agua | 511, 512, 521, 523 |
| 8 | RIBERA | Bosque de ribera | 522 |
| 9 | NIEVE | Nieve permanente | 333 |
| 10 | ANTROPICO | Antrópico | 111–142 |

### 2.3 Asignación de biomasa inicial

| Hábitat | P1_max | P2_max | P3_max | I1 | I2 | I3 |
|---------|--------|--------|--------|----|----|----|
| BOSQUE_CON | 1.5 | 0.3 | 0.5 | 0.02 | 0.15 | 0.08 |
| BOSQUE_CAD | 1.0 | 0.3 | 0.5 | 0.015 | 0.08 | 0.05 |
| MATORRAL | 2.0 | 0.2 | 1.5 | 0.03 | 0.08 | 0.05 |
| PASTIZAL | 1.0 | 0.1 | 4.0 | 0.03 | 0.15 | 0.06 |
| HUMEDAL | 2.0 | 1.0 | 0.5 | 0.025 | 0.06 | 0.04 |
| ROCA | 0.2 | 0.15 | 0.0 | 0.005 | 0.01 | 0.01 |
| AGUA | 0.0 | 1.0 | 0.0 | 0.0 | 0.02 | 0.01 |
| RIBERA | 1.0 | 0.8 | 1.5 | 0.02 | 0.08 | 0.05 |
| NIEVE | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ANTROPICO | 0.1 | 0.05 | 0.2 | 0.005 | 0.005 | 0.005 |

**Biomasa total inicial:** ~529.392 kg plantas, ~35.074 kg invertebrados

---

## 3. Visualización (`visualize_terrain.py`)

Genera mapas con matplotlib (backend `Agg`):

| Comando | Salida |
|---------|--------|
| `python visualize_terrain.py` | Dashboard 3×3 + mapas individuales en `output/maps/` |
| `python visualize_terrain.py --layer habitat` | Solo mapa de hábitats |
| `python visualize_terrain.py --output maps/ --dpi 200` | Personalizar directorio y resolución |

Capas del dashboard (3×3):
1. DEM (colormap `terrain`)
2. Pendiente (colormap `YlOrRd`, vmin=0, vmax=60)
3. Orientación (colormap `twilight`, 0–360°)
4. TRI (colormap `Greys`)
5. Pisos bioclimáticos (BoundaryNorm, 4 colores)
6. Hábitats (BoundaryNorm, 10 colores)
7. Biomasa P1 (entomófilas)
8. Biomasa P3 (pastos)
9. Biomasa I1 (polinizadores)

---

## 4. Validación (`validate_terrain.py`)

Carga datos reales en `TerrainGrid(375, 502, 25)` y ejecuta 1 paso de simulación:

```python
grid = load_processed_terrain(grid, dem, slope, aspect, tri, pisos)
sim = Simulation(grid=grid, populations=[...])
sim.initialize()
sim._step(0)
# Verifica: celdas válidas, elevación media, agentes vivos tras paso 1
```

Estadísticas de validación:
- **Grid:** 375 × 502 = 188.250 celdas
- **Válidas:** 180.037 (96%)
- **Elevación:** 977 – 2.722 m (media 1.772 m)
- **Pendiente media:** 29.1°

---

## 5. Dependencias

| Herramienta | Uso |
|------------|-----|
| `rasterio` | Lectura/escritura GeoTIFF, reproyección |
| `numpy` | Cálculos vectoriales (slope, aspect, TRI) |
| `GDAL` (gdalwarp, gdaldem) | Pipeline alternativo vía CLI |
| `shapely` | Geometrías vectoriales (MCSC) |
| `requests` | Descarga WFS desde ICGC |
| `matplotlib` | Visualización de mapas |

---

## 6. Archivos generados

| Archivo | Tamaño | Ubicación |
|---------|--------|-----------|
| `terrain_dem_25m.tif` | 752 KB | `ecosystem/data/` |
| `terrain_slope.tif` | 782 KB | `ecosystem/data/` |
| `terrain_aspect.tif` | 791 KB | `ecosystem/data/` |
| `terrain_tri.tif` | 785 KB | `ecosystem/data/` |
| `terrain_pisos.tif` | 49 KB | `ecosystem/data/` |
| `terrain_habitat.tif` | 83 KB | `ecosystem/data/` |
| `terrain_biomass.tif` | 5.2 MB | `ecosystem/data/` |
| `terrain_cells.tsv` | 8.8 MB | `ecosystem/data/` |

---

## Enlaces

- [[terrain_dem_explicacion]] — Detalles del DEM SRTM procesado
- [[terrain_habitat_explicacio]] — Clasificación MCSC y asignación de biomasa
- [[plan_terreno_simulacion]] — Plan original del pipeline de terreno
- [[../data/terrain_cells.tsv]] — Grid completo exportado
