# Terreno Procesado — Vall de Cardós (PNAP)

**Fecha:** 2026-06-22
**Fuente:** SRTM GL1 30m (tile N42E001)
**Resolución final:** 25 m
**Proyección:** EPSG:25831 (ETRS89 / UTM zone 31N)
**Área total:** ~9.4 × 12.6 km (11.800 ha)

---

## Pipeline de procesamiento

### 1. Fuente original
- **Tile SRTM GL1:** `N42E001.tif` — 30 m resolución, EPSG:4326
- **Cobertura:** 1.0°E–2.0°E, 42.0°N–43.0°N (348–3.109 m)
- **Descargado de:** `https://opentopography.s3.sdsc.edu/raster/SRTM_GL1/SRTM_GL1_srtm/N42E001.tif`

### 2. Recorte
- **Bounding box:** 1,2443°E–1,3554°E, 42,5446°N–42,6557°N
- **Zona:** Vall de Cardós, subcuenca del Noguera Pallaresa
- **Criterio:** Cubrir todos los pisos bioclimáticos (montano → nival)

### 3. Reproyección
- De EPSG:4326 a EPSG:25831 (UTM 31N)
- Resampling bilinear a 25 m
- **Resultado:** 375 × 502 celdas = 188.250 celdas (180.037 válidas)

### 4. Capas derivadas
| Capa | Método | Archivo |
|------|--------|---------|
| Elevación | Reprojection bilineal | `terrain_dem_25m.tif` |
| Pendiente | Central difference (Zevenbergen & Thorne) | `terrain_slope.tif` |
| Aspecto | Arctan2(dz/dy, -dz/dx) | `terrain_aspect.tif` |
| TRI | RMS de diferencias con 8 vecinos | `terrain_tri.tif` |
| Pisos | Clasificación por altitud | `terrain_pisos.tif` |
| Grid completo | TSV con 180.037 filas | `terrain_cells.tsv` |

### 5. Pisos bioclimáticos

| Piso | Rango (m) | Celdas | % | Especies indicadoras |
|------|-----------|--------|---|---------------------|
| Montano | 650–1.600 | 66.806 | 37% | *Cervus elaphus*, *Sus scrofa*, *Martes martes* |
| Subalpino | 1.600–2.300 | 91.827 | 51% | *Tetrao urogallus*, *Capreolus capreolus* |
| Alpino | 2.300–2.700 | 21.385 | 12% | *Rupicapra pyrenaica*, *Marmota marmota* |
| Nival | >2.700 | 19 | 0% | *Iberolacerta aurelioi* |

### 6. Estadísticas del terreno
| Parámetro | Valor |
|-----------|-------|
| Elevación min | 977 m |
| Elevación max | 2.722 m |
| Elevación media | 1.772 m |
| Pendiente media | 29,1° |
| TRI medio | 21,8 |
| Celdas válidas | 180.037 (96%) |

---

## Archivos generados

| Archivo | Tamaño | Descripción |
|---------|--------|-------------|
| `ecosystem/data/terrain_dem_25m.tif` | 752 KB | DEM 25m recortado y reproyectado |
| `ecosystem/data/terrain_slope.tif` | 782 KB | Pendiente en grados |
| `ecosystem/data/terrain_aspect.tif` | 791 KB | Orientación (0–360°) |
| `ecosystem/data/terrain_tri.tif` | 785 KB | Terrain Ruggedness Index |
| `ecosystem/data/terrain_pisos.tif` | 49 KB | Pisos bioclimáticos (int32) |
| `ecosystem/data/terrain_cells.tsv` | 8,8 MB | Grid completo (180.037 filas) |

---

## Integración en simulación

El grid de 375×502 celdas se carga en `TerrainGrid` mediante `io.load_processed_terrain()`, que:

1. Lee los 5 GeoTIFFs (DEM, slope, aspect, TRI, piso)
2. Asigna valores a cada celda del grid
3. Calcula `cost_a_star` = slope_factor × snow_factor × habitat_factor
4. Biomass inicial se asigna aleatoriamente según piso

### Cobertura del suelo (pendiente)

Actualmente no hay mapa de hábitats real (MCSC). Todas las celdas se inicializan con hábitat PASTIZAL por defecto. La clasificación real de hábitats requiere descargar el MCSC.

---

## Pendiente

1. **MCSC**: Descargar cobertura del suelo para clasificar hábitats reales
2. **Hidrografía**: Añadir red fluvial del Noguera Pallaresa
3. **Validación visual**: Plotear mapa de elevación/pisos con matplotlib
4. **Optimización**: La simulación con ~6.000 agentes y pathfinding A* en 180K celdas es lenta — considerar optimizaciones (grid chunks, pathfinding caching)
