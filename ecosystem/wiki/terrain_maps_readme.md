# Mapas de Terreno — Parc Natural de l'Alt Pirineu

## Grid de simulación

- **Resolución**: 25 m
- **Dimensiones**: 375 × 502 celdas (188.250 totales, 180.037 válidas)
- **Área**: ~9,4 × 12,6 km (subcuenca Vall de Cardós)
- **CRS**: EPSG:25831 (ETRS89 / UTM zone 31N)
- **Fuente DEM**: SRTM GL1 30m → reproyectado a 25 m

---

## Archivos ráster (`ecosystem/data/`)

### `terrain_dem_25m.tif`
**Modelo Digital de Elevaciones (DEM)**
- **Bandas**: 1 (float32)
- **Rango**: 977–2.722 m
- **Media**: 1.772 m
- **Descripción**: Altitud de cada celda del terreno. Capa base de la que derivan todas las demás. Se usó SRTM GL1 30m, recortado a la subcuenca de Vall de Cardós y reproyectado a 25 m con interpolación bilineal.
- **Visualización**: `terrain_dem.png`

### `terrain_slope.tif`
**Pendiente**
- **Bandas**: 1 (float32)
- **Rango**: 0,1–89,2°
- **Media**: 29,1°
- **Descripción**: Pendiente del terreno en grados. Calculada por diferencias finitas (método de Horn, ventana 3×3). Determina el coste energético de locomoción de los agentes (a mayor pendiente, mayor MET).
- **Visualización**: `terrain_slope.png`
- **Uso en simulación**: `costos_actividad.tsv` asigna MET según la pendiente (LOCO_WALK_MOD < 5°, LOCO_CLIMB > 15°).

### `terrain_aspect.tif`
**Orientación**
- **Bandas**: 1 (float32)
- **Rango**: 0–360° (-1 para terreno plano)
- **Descripción**: Orientación de la pendiente en grados desde el norte (0°=N, 90°=E, 180°=S, 270°=O). Influye en la insolación recibida: laderas sur son más cálidas y secas; laderas norte retienen más humedad y nieve.
- **Visualización**: `terrain_aspect.png` (cmap cíclico `twilight`)

### `terrain_tri.tif`
**Índice de Rugosidad del Terreno (TRI)**
- **Bandas**: 1 (float32)
- **Descripción**: Terrain Ruggedness Index — raíz del error cuadrático medio de las diferencias de elevación entre una celda y sus 8 vecinas. Valores altos indican terreno accidentado (roquedos, crestas), valores bajos indican superficies llanas (pastizales, llanos). Afecta al coste de paso en A* y a la idoneidad de hábitat.
- **Visualización**: `terrain_tri.png`

### `terrain_pisos.tif`
**Pisos Bioclimáticos**
- **Bandas**: 1 (int32)
- **Valores**: 1=Montano, 2=Subalpino, 3=Alpino, 4=Nival
- **Distribución**:
  - Montano (650–1.600 m): 66.806 celdas (37%)
  - Subalpino (1.600–2.300 m): 91.827 celdas (51%)
  - Alpino (2.300–2.700 m): 21.385 celdas (12%)
  - Nival (>2.700 m): 19 celdas (<1%)
- **Descripción**: Clasificación altitudinal en 4 pisos. Cada piso condiciona la vegetación dominante, las especies presentes y la fenología estacional. Se usa para filtrar hábitats y asignar preferencias de especies.
- **Visualización**: `terrain_pisos.png`

### `terrain_habitat.tif`
**Mapa de Hábitats Funcionales**
- **Bandas**: 1 (int32)
- **Valores**: 10 clases funcionales
  | Código | Hábitat | Celdas | % |
  |--------|---------|--------|---|
  | 1 | Bosc de coníferes | 58.434 | 31,0 |
  | 2 | Bosc caducifoli | 40.189 | 21,3 |
  | 3 | Matollar | 44.530 | 23,7 |
  | 4 | Pasturatge | 28.562 | 15,2 |
  | 5 | Zona humida | 251 | 0,1 |
  | 6 | Roca | 13.336 | 7,1 |
  | 7 | Aigua | 486 | 0,3 |
  | 8 | Ribera | 1.783 | 0,9 |
  | 9 | Neu | — | — |
  | 10 | Antròpic | 679 | 0,4 |
- **Descripción**: Clasificación derivada del MCSC (Mapa de Cobertes del Sòl de Catalunya, 44 clases → 10 funcionales). Descargado vía WFS del ICGC y rasterizado al grid de simulación. Cada celda tiene asignado un hábitat que determina la biomasa inicial y las preferencias de las especies.
- **Uso en simulación**: Preferencia de hábitat por especie (p. ej., isard → PASTIZAL/ROCA, gall fer → BOSQUE_CON/MATORRAL).
- **Visualización**: `terrain_habitat.png`

### `terrain_biomass.tif`
**Biomasa Inicial por Celda**
- **Bandas**: 9 (float32)
  | Banda | Variable | Descripción |
  |-------|----------|-------------|
  | 1 | `biomass_P1` | Plantas entomófilas (kg) |
  | 2 | `biomass_P2` | Plantas independientes (kg) |
  | 3 | `biomass_P3` | Pastos (kg) |
  | 4 | `biomass_I1` | Polinizadores (kg) |
  | 5 | `biomass_I2` | Fitófagos (kg) |
  | 6 | `biomass_I3` | Depredadores/parasitoides (kg) |
  | 7 | `P1_max` | Biomasa máxima P1 |
  | 8 | `P2_max` | Biomasa máxima P2 |
  | 9 | `P3_max` | Biomasa máxima P3 |
- **Descripción**: Valores iniciales de biomasa asignados según el tipo de hábitat de cada celda (ver `process_mcsc.py:309-376` para los valores por hábitat). Durante la simulación, la biomasa evoluciona con crecimiento logístico, consumo por herbívoros y estacionalidad.

---

## Archivo TSV (`ecosystem/data/`)

### `terrain_cells.tsv`
**Grid completo en formato tabular**
- **Filas**: 180.037 (una por celda válida)
- **Columnas**: `x`, `y`, `utm_x`, `utm_y`, `elevation_m`, `slope_deg`, `aspect_deg`, `tri`, `piso`
- **Descripción**: Exportación del grid de simulación en formato TSV. Es la fuente directa para los scripts de visualización (`visualize_terrain_tsv.py`). Generado por `process_terrain.py`.

---

## Mapas visuales generados (`output/maps/`)

| Archivo | Descripción |
|---------|-------------|
| `terrain_dem.png` | Elevación con hillshade |
| `terrain_slope.png` | Pendiente con hillshade |
| `terrain_aspect.png` | Orientación con cmap cíclico |
| `terrain_tri.png` | Rugosidad con hillshade |
| `terrain_pisos.png` | Pisos bioclimáticos |
| `terrain_habitat.png` | Hábitats funcionales |
| `terrain_biomass_P1.png` | Biomasa plantas entomófilas |
| `terrain_biomass_P3.png` | Biomasa pastos |
| `terrain_biomass_I1.png` | Biomasa polinizadores |
| `terrain_dashboard.png` | Panel combinado (3×3) |

### Cómo generar los mapas visuales

```bash
# Mapa básico (desde GeoTIFFs):
python3 src/visualize_terrain.py --output output/maps --dpi 200

# Mapas mejorados con escala y norte (desde TSV):
python3 src/visualize_terrain_tsv.py --output output/maps --dpi 300

# Capa específica:
python3 src/visualize_terrain.py --layer dem
python3 src/visualize_terrain_tsv.py --maps dem slope
```

---

## Pipeline de generación

```
SRTM GL1 30m (data/terrain/srtm_n42e001.tif)
  │
  └── process_terrain.py ──────────────────────────────────────────┐
      │ Recorte + reproyección EPSG:25831 25m                      │
      │ Pendiente, aspecto, TRI, pisos bioclimáticos               │
      ├── terrain_dem_25m.tif                                      │
      ├── terrain_slope.tif                                        │
      ├── terrain_aspect.tif                                       │
      ├── terrain_tri.tif                                          │
      ├── terrain_pisos.tif                                        │
      └── terrain_cells.tsv ──→ visualize_terrain_tsv.py ──→ mapas │
                                     │
MCSC 44 clases (ICGC WFS)           │
  │                                  │
  └── process_mcsc.py ───────────────┤
      ├── terrain_habitat.tif        │
      └── terrain_biomass.tif        │
                                     │
              visualize_terrain.py ──┘ (desde GeoTIFFs)
```

## Referencias

- `src/process_terrain.py` — pipeline de procesamiento del DEM
- `src/process_mcsc.py` — clasificación de hábitats y biomasa
- `src/visualize_terrain.py` — visualización básica desde GeoTIFFs
- `src/visualize_terrain_tsv.py` — visualización mejorada desde TSV
- `ecosystem/wiki/plan_terreno_simulacion.md` — plan detallado de procesamiento
