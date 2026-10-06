# Plan de Simulación del Terreno — Parc Natural de l'Alt Pirineu

**Fecha:** 2026-06-22
**Resolución del grid:** 25 m
**Área:** Subcuenca y valle representativos
**Motor de simulación:** *Pendiente de decidir*

---

## Resumen Ejecutivo

Este plan detalla la adquisición, procesamiento e integración del terreno en el simulador agent-based del PNAP. El objetivo es generar un grid de 25 m de resolución para un área de subcuenca/valle (~10.000–20.000 ha), derivando capas de elevación, pendiente, hábitat y costo de locomoción, y vinculándolo con los agentes y sus metabolismos.

---

## Tabla de Contenidos

1. [Fase 1: Adquisición de Fuentes de Datos](#fase-1-adquisición-de-fuentes-de-datos)
2. [Fase 2: Procesamiento del DEM → Capas Derivadas](#fase-2-procesamiento-del-dem--capas-derivadas)
3. [Fase 3: Grid de Simulación (Estructura y Formato)](#fase-3-grid-de-simulación-estructura-y-formato)
4. [Fase 4: Mapa de Hábitats desde Cobertura del Suelo](#fase-4-mapa-de-hábitats-desde-cobertura-del-suelo)
5. [Fase 5: Integración con Agentes](#fase-5-integración-con-agentes)
6. [Fase 6: Estacionalidad del Terreno](#fase-6-estacionalidad-del-terreno)
7. [Referencias](#fase-7-referencias)

---

## Fase 1: Adquisición de Fuentes de Datos

### 1.1 Modelo Digital de Elevaciones (DEM)

#### Opción A (Recomendada): ICGC MDT 5m + Downsampling a 25m

| Atributo | Valor |
|----------|-------|
| **Nombre** | Model d'Elevacions del Terreny Topogràfic de Catalunya 5m (2009–2018) |
| **Resolución original** | 5 m |
| **Formato** | ASCII Grid (ASC) / GeoTIFF |
| **Licencia** | CC BY 4.0 |
| **Precisión vertical** | RMSE < 2 m |
| **Descarga** | https://visors.icgc.cat/appdownloads/ |
| **Partición** | Hojas 1×1 km coincidentes con BT-5M v2.0 |

**Procedimiento:**
1. Navegar al visor de descargas del ICGC → sección "Elevacions"
2. Seleccionar "Model d'Elevacions del Terreny Topogràfic Catalunya 5m 2009-2018"
3. Dibujar el área de la subcuenca/valle sobre el mapa
4. Descargar el ZIP con todos los tiles
5. Unir tiles con `gdal_merge.py`
6. Downsampling a 25 m con `gdalwarp -tr 25 25 -r average`

**Ventaja:** Mayor precisión al ser fotogramétrico desde BT-5M (no LiDAR con ruido vegetal).
**Desventaja:** ~18× más tiles que usando directamente 25 m.

#### Opción B: ICGC LiDAR 50cm + Downsampling a 25m

| Atributo | Valor |
|----------|-------|
| **Nombre** | Model d'Elevacions del Terreny LiDAR 50cm (2021–2023) |
| **Resolución original** | 0.5 m |
| **Precisión vertical** | RMSE < 0.5 m |
| **Descarga** | https://visors.icgc.cat/appdownloads/ (sección "Elevacions" o "Lidar") |

**Ventaja:** Precisión máxima, datos recientes (2021–2023), incluye clasificación ground/vegetation/ buildings.
**Desventaja:** Archivos enormes, requiere más procesamiento.

#### Opción C: EU-DEM v1.1 (25m directo)

| Atributo | Valor |
|----------|-------|
| **Nombre** | EU-DEM v1.1 — Copernicus Land Monitoring Service |
| **Resolución** | 25 m (1 arcsec) |
| **Formato** | GeoTIFF 32-bit |
| **Precisión vertical** | RMSE ±7 m |
| **Licencia** | Copernicus full, open and free |
| **Descarga** | https://files.gpxz.io/eudem_buffered.zip (23 GB, todo Europa) |
| **Tile para Alt Pirineu** | `eu_dem_v11_E00N40.tif` (~1.33°E, 42.65°N → tile E00N40) |

**Ventaja:** Resolución 25m directa, sin downsampling. Un solo tile para toda el área.
**Desventaja:** Menor precisión vertical (±7 m vs <2 m del ICGC).

#### Opción D: Copernicus GLO-30 (30m)

| Atributo | Valor |
|----------|-------|
| **Nombre** | Copernicus Global DSM (GLO-30) |
| **Resolución** | 30 m |
| **Descarga** | https://portal.opentopography.org/datasets?group=global |
| **Nota** | Reemplazo moderno del EU-DEM; mayor calidad |

#### Opción E: SRTM GL1 (30m) / ALOS AW3D30 (30m)

Ambas gratuitas desde OpenTopography. SRTM es de 2000, ALOS de 2006–2011.
Precisión inferior a ICGC pero suficientes para simulación ecológica a 25–30 m.

### 1.2 Cobertura del Suelo / Vegetación

| Fuente | Descripción | Resolución | Enlace |
|--------|-------------|------------|--------|
| **MCSC** (Mapa de Cobertes del Sòl de Catalunya) | 44 clases de cobertura (bosques, cultivos, urbanizado, etc.). Ideal para simulación. | 1:5.000 vectorial / raster 5m | https://visors.icgc.cat/appdownloads/ → "Cobertes del sòl" |
| **CORINE Land Cover 2018** | Pan-Europe, 44 clases armonizadas | 100 m mínimo | https://land.copernicus.eu/en/products/corine-land-cover |
| **Mapa d'Hàbitats de Catalunya** | Hábitats CORINE clasificados por vegetación | 1:50.000 | ICGC / Generalitat |

**Recomendación:** MCSC 2023 en format vectorial (Geopackage, ~1.6 GB toda Catalunya),
descargable por área de interés desde el visor ICGC.

### 1.3 Hidrografía (Ríos, Lagos, Humedales)

| Fuente | Descripción | Enlace |
|--------|-------------|--------|
| **ICGC Xarxa Hidrogràfica** | Red fluvial completa de Catalunya | https://visors.icgc.cat/appdownloads/ |
| **EU-Hydro** | Pan-European hydrography (compatible con EU-DEM) | Copernicus Land |
| **OpenStreetMap** | Waterways del Alt Pirineu (overpass-api) | https://overpass-api.de |

**Relevancia:** Crucial para especies acuáticas: *Salmo trutta* (truita), *Lutra lutra* (llúdriga),
*Calotriton asper* (tritó pirinenc), *Galemys pyrenaicus* (almesquera).

### 1.4 Nieve Estacional (Opcional)

| Fuente | Descripción |
|--------|-------------|
| **MODIS Snow Cover (MOD10A1)** | Cobertura de nieve diaria 500m, desde 2000 |
| **Sentinel-2** | 10–20m, útil para validar modelo de nieve local |
| **CHELSA climate data** | Temperatura y precipitación para modelar acumulación/fusión |

---

## Fase 2: Procesamiento del DEM → Capas Derivadas

### 2.1 Pipeline de procesamiento

```
DEM crudo (5m o 25m)
│
├── 2.1.1 Mosaico y reproyección
│   └── gdal_merge.py + gdalwarp a EPSG:25831 (ETRS89 / UTM zone 31N)
│
├── 2.1.2 Downsampling (solo si origen es 5m → 25m)
│   └── gdalwarp -tr 25 25 -r average
│
├── 2.1.3 Recorte al área de estudio
│   └── gdalwarp -te <xmin> <ymin> <xmax> <ymax>
│
├── 2.1.4 Slope (pendiente en grados)
│   └── gdaldem slope -p (en percent) o gdaldem slope (en degrees)
│
├── 2.1.5 Aspect (orientación)
│   └── gdaldem aspect
│
├── 2.1.6 Ruggedness (TRI — Terrain Ruggedness Index)
│   └── gdaldem TRI o cálculo numpy: sqrt(Σ(celda - vecina)²)
│
├── 2.1.7 Pisos bioclimáticos (classification)
│   ├── Montano   (650–1.600 m)
│   ├── Subalpino (1.600–2.300 m)
│   ├── Alpino    (2.300–2.700 m)
│   └── Nival     (>2.700 m)
│
└── 2.1.8 Clasificación de hábitats (ver Fase 4)
```

### 2.2 Cálculos específicos

#### Slope (Pendiente)

```python
# Convertir pendiente en grados a factor de costo de locomoción
# Basado en: LOCO_CLIMB = MET 5.0 (terreno rocoso, ver costos_actividad.tsv)
# Ecuación propuesta:
def slope_cost_factor(slope_degrees):
    if slope_degrees < 5:
        return 1.0     # LOCO_WALK_MOD (MET 2.5)
    elif slope_degrees < 15:
        return 1.5     # transición
    elif slope_degrees < 30:
        return 2.5     # LOCO_CLIMB (MET 5.0)
    else:
        return 3.5     # escalada extrema
```

#### TRI (Terrain Ruggedness Index)

```python
# TRI = RMSE de diferencias entre celda y sus 8 vecinas
# Alto TRI → refugio para depredadores, madrigueras, microhábitats
# Bajo TRI → pastizales abiertos, fácil desplazamiento
```

#### Pisos Bioclimáticos

Referencia directa de `paper.md`:34-39 y `investigacion_parc_alt_pirineu.md`:7-16.
Cada piso condiciona:

| Piso | Altitud | Vegetación dominante | Especies clave |
|------|---------|---------------------|----------------|
| Montano | 650–1.600 m | Roble, pino silvestre, abeto, haya | *Cervus elaphus*, *Sus scrofa*, *Martes martes* |
| Subalpino | 1.600–2.300 m | Pino negro (*Pinus uncinata*), rododendro, *Vaccinium* | *Tetrao urogallus*, *Capreolus capreolus* |
| Alpino | 2.300–2.700 m | Prados alpinos, canchales | *Rupicapra pyrenaica*, *Marmota marmota*, *Lagopus muta* |
| Nival | >2.700 m | Roca desnuda, nieve permanente | *Iberolacerta aurelioi* (hábitat rupícola) |

### 2.3 Herramientas necesarias

| Herramienta | Uso |
|------------|-----|
| **GDAL** (gdal_merge.py, gdalwarp, gdaldem, gdal_calc.py) | Todo el procesamiento raster |
| **Python + numpy/rasterio** | Cálculos personalizados (TRI, costos, clasificación) |
| **QGIS** (opcional) | Visualización y validación manual |
| **GRASS GIS / WhiteboxTools** (opcional) | Análisis hidrológicos avanzados |

---

## Fase 3: Grid de Simulación (Estructura y Formato)

### 3.1 Dimensiones esperadas

Para una **subcuenca representativa** de ~10.000 ha (10×10 km):

| Resolución | Celdas totales | Celdas con datos |
|------------|----------------|------------------|
| **25 m** | 400 × 400 = **160.000 celdas** | Manejable en memoria |
| 5 m (sin downsampling) | 2.000 × 2.000 = 4.000.000 celdas | Posible pero más pesado |

Para un **valle completo** de ~20.000 ha (~14×14 km):

| Resolución | Celdas totales |
|------------|----------------|
| **25 m** | 560 × 560 = **~314.000 celdas** |
| 5 m | 2.800 × 2.800 = 7.840.000 celdas |

**Conclusión:** 25 m × 10.000–20.000 ha = 160K–314K celdas → completamente viable incluso en Python.

### 3.2 Estructura de datos para el grid

Cada celda del grid debe contener:

```
Celda(x, y):
├── elevation_m: float           # altitud en metros
├── slope_deg: float              # pendiente en grados
├── aspect_deg: float             # orientación (0-360)
├── tri: float                    # ruggedness index
├── piso_bioclimatico: int        # 1=Montano, 2=Subalpino, 3=Alpino, 4=Nival
├── habitat_type: int             # código MCSC o clase simplificada
├── habitat_clase: str            # "bosque_conifera", "pradera_alpina", etc.
├── biomasa_P1: float             # kg biomasa plantas entomófilas
├── biomasa_P2: float             # kg biomasa plantas independientes
├── biomasa_P3: float             # kg biomasa pastos
├── biomasa_I1: float             # biomasa polinizadores
├── biomasa_I2: float             # biomasa herbívoros fitófagos
├── biomasa_I3: float             # biomasa depredadores/parasitoides
├── snow_cover: float             # 0.0–1.0 fracción de nieve
├── is_water: bool                # lago/río permanente
├── is_riparian: bool             # zona de ribera
├── cost_locomotion: float        # multiplicador de costo energético (ver Fase 2.2)
└── cost_a_star: float            # costo de paso para pathfinding (A*)
```

### 3.3 Formatos de almacenamiento

| Formato | Uso | Ventaja |
|---------|-----|---------|
| **GeoTIFF multicapa** (1 archivo por variable) | Almacenamiento y análisis GIS | Estándar, GDAL nativo |
| **TSV/CSV** (1 fila por celda) | Intercambio con scripts Python/R | Legible, fácil de procesar |
| **NumPy .npz / Zarr** | Carga en memoria para simulación | Rápido, comprimido |
| **Parquet** | Grandes volúmenes, consultas eficientes | Ideal para análisis post-simulación |

**Recomendación:**
- Almacenamiento base: GeoTIFFs (uno por capa: elevación, pendiente, hábitat, etc.)
- Carga a simulación: exportar a NumPy `.npz` o TSV comprimido
- Post-procesamiento: Parquet

### 3.4 Sistema de coordenadas

```
EPSG:25831 — ETRS89 / UTM zone 31N
```
- Cubre toda Catalunya
- Unidades en metros → resolución de celda directamente 25×25 m
- Compatible con todos los datos del ICGC

---

## Fase 4: Mapa de Hábitats desde Cobertura del Suelo

### 4.1 Simplificación de clases MCSC a categorías de simulación

El MCSC tiene 44 clases. Para la simulación, se simplifican a ~10 clases funcionales:

| Clase MCSC | Clase simulación | Abreviación | Relevancia para agentes |
|------------|------------------|-------------|------------------------|
| Bosques de coníferas (*Pinus uncinata*, *P. sylvestris*, *Abies alba*) | Bosque subalpino / montano | BOSQUE_CON | Hábitat gall fer, marta, esquirol |
| Bosques caducifolios (*Fagus*, *Quercus*, *Betula*) | Bosque caducifolio | BOSQUE_CAD | Hábitat ciervo, corzo, jabalí |
| Matorral (*Rhododendron*, *Vaccinium*, *Calluna*) | Matorral subalpino | MATORRAL | Alimentación gall fer, cobijo |
| Praderas alpinas (*Nardus*, *Festuca*) | Pastizal alpino/subalpino | PASTIZAL | Pastoreo isard, marmota, perdiz nival |
| Prados húmedos / molleres | Humedal / turbera | HUMEDAL | Hábitat *Boloria eunomia*, anfibios |
| Roquedos / canchales / gleras | Roca | ROCA | Hábitat *Iberolacerta aurelioi*, marmota |
| Lagos, embalses, ríos | Agua | AGUA | Hábitat truita, tritó, nutria, almesquera |
| Zonas de ribera | Ribera | RIBERA | Conectividad, hábitat *Galemys*, *Rana temporaria* |
| Nieves perpetuas / glaciares | Nieve/ Hielo | NIEVE | Hábitat perdiz nival (invierno) |
| Áreas humanizadas (pistas, refugios, núcleos) | Antrópico | ANTROPICO | Zona de exclusión/perturbación |

### 4.2 Vinculación hábitat → biomasa de recursos

Cada clase de hábitat tiene una asignación inicial de biomasa de los clusters P1/P2/P3 e I1/I2/I3:

| Hábitat | P1 | P2 | P3 | I1 | I2 | I3 |
|---------|----|----|----|----|----|----|
| BOSQUE_CON | Alta (*Vaccinium*) | Baja (briófitos) | Baja | Media | Alta (*Thaumetopoea*) | Alta (hormigas) |
| BOSQUE_CAD | Media | Baja | Baja | Media | Media | Media |
| MATORRAL | Alta | Baja | Media | Alta | Media | Media |
| PASTIZAL | Media | Baja | Alta | Alta (Bombus) | Alta (ortópteros) | Media (arañas) |
| HUMEDAL | Alta (*Bistorta*) | Alta (briófitos) | Baja | Alta (*Boloria*) | Media | Media |
| ROCA | Baja | Baja (líquenes) | Nula | Baja | Baja | Baja |
| AGUA | Nula | Alta (*Hippuris*) | Nula | Nula | Nula | Nula |
| RIBERA | Media | Media (helechos) | Media | Media | Media | Media |

Estos valores iniciales serán dinámicos durante la simulación (crecimiento, pastoreo, estacionalidad).

---

## Fase 5: Integración con Agentes

### 5.1 Movimiento: A* con coste de terreno

El algoritmo A* usará el `cost_a_star` de cada celda, derivado de:

```
cost_a_star = base_cost × slope_factor(slope_deg) × habitat_factor(habitat_type) × snow_factor(snow_cover)
```

Donde:
- `base_cost = 1.0` (caminar 25 m en llano, terreno abierto, sin nieve)
- `slope_factor(slope)` basado en tabla de `costos_actividad.tsv` (LOCO_WALK_MOD, LOCO_CLIMB)
- `habitat_factor`: bosque denso > pradera abierta > roca
- `snow_factor`: nieve profunda = 2.0–3.0

### 5.2 Gasto energético de locomoción por terreno

Sistema de energía del agente (referencia: `costos_actividad.tsv`):

```python
costo_base = met_actividad * bmr  # kcal/h (ver DEE cálculo)
```

Cuando un agente se mueve, se selecciona la actividad según pendiente:
- `pendiente < 5°` → LOCO_WALK_MOD (MET 2.5)
- `pendiente 5–15°` → LOCO_WALK_FAST o LOCO_TROT (MET 3.0–4.5)
- `pendiente 15–30°` → LOCO_CLIMB (MET 5.0)
- `pendiente > 30°` → LOCO_CLIMB + factor extra (MET 5.0+)

### 5.3 Preferencias de hábitat por especie

Cada especie tiene afinidad por ciertos hábitats (basado en `paper.md` sección 3.4
y `vertebrates.tsv`):

| Especie | Hábitat preferido | Rango altitudinal |
|---------|-------------------|-------------------|
| *Rupicapra pyrenaica* (Isard) | PASTIZAL, ROCA | Alpino–Subalpino |
| *Tetrao urogallus* (Gall fer) | BOSQUE_CON (pino negro), MATORRAL (*Vaccinium*) | Subalpino |
| *Marmota marmota* (Marmota) | PASTIZAL, ROCA | Alpino |
| *Iberolacerta aurelioi* (Sargantana pallaresa) | ROCA (canchales) | Alpino (>2.100 m) |
| *Lutra lutra* (Llúdriga) | AGUA, RIBERA | Montano–Subalpino (ríos) |
| *Salmo trutta* (Truita) | AGUA | Montano–Subalpino (ríos fríos) |

### 5.4 Preferencia estacional

| Especie | Verano | Invierno |
|---------|--------|----------|
| Isard | PASTIZAL alpino | BOSQUE_CON, MATORRAL (cota baja) |
| Ciervo | PASTIZAL, BOSQUE_CAD | BOSQUE_CON (menor altitud) |
| Oso | TODOS (forrajeo intensivo) | Hibernación en ROCA/BOSQUE_CON |
| Gall fer | MATORRAL (*Vaccinium*), BOSQUE_CON | BOSQUE_CON (acículas de pino) |

---

## Fase 6: Estacionalidad del Terreno

### 6.1 Modelo de nieve

La nieve afecta:
1. **Costo de locomoción** (factor 1.5–3.0 sobre terreno sin nieve)
2. **Accesibilidad de celdas** (pisos alpinos inaccesibles en invierno para muchas especies)
3. **Disponibilidad de recursos** (P1/P3 cubiertos por nieve → biomasa = 0)
4. **Camuflaje** (*Lagopus muta*, *Mustela erminea* → plumaje/pelaje blanco)

Propuesta de modelo simple:
```python
# Nieve según altitud y mes (calibrable con datos MODIS/CHELSA)
def snow_cover(elevation_m, month):
    if month in [6, 7, 8, 9]:  # verano
        return 0.0
    snow_line = get_snow_line(month)  # ej: 2700m en mayo, 1800m en enero
    if elevation_m < snow_line:
        return 0.0
    return min(1.0, (elevation_m - snow_line) / 500.0)
```

### 6.2 Fenología de plantas (P1, P2, P3)

Basado en `plant_clusters.tsv` y `paper.md`:53–85:

| Cluster | Primavera | Verano | Otoño | Invierno |
|---------|-----------|--------|-------|----------|
| **P1** (entomófilas) | Brotación, floración | Fructificación | Senescencia | Dormancia |
| **P2** (independientes) | Crecimiento | Fotosíntesis alta | Esporulación | Dormancia |
| **P3** (pastos) | Crecimiento rápido | Máxima biomasa | Senescencia | Dormancia/baja |

### 6.3 Fenología de invertebrados (I1, I2, I3)

Basado en `invertebrate_clusters.tsv` y `paper.md`:87–109:

| Cluster | Primavera | Verano | Otoño | Invierno |
|---------|-----------|--------|-------|----------|
| **I1** (polinizadores) | Emergencia adultos | Vuelo/reproducción | Nuevas reinas (Bombus) | Huevos/reinas hibernantes |
| **I2** (fitófagos) | Larvas activas | Adultos/generaciones | Pupas/huevos | Diapausa (huevos/pupas) |
| **I3** (depredadores) | Actividad creciente | Máxima actividad | Preparación invierno | Hibernación/reducción |

### 6.4 Hibernación y migración altitudinal

| Especie | Comportamiento invernal | Dependencia del terreno |
|---------|------------------------|------------------------|
| *Ursus arctos* | Hibernación (cuevas, ROCA) | Necesita celdas ROCA con cobertura |
| *Marmota marmota* | Hibernación (madrigueras, PASTIZAL) | Suelo profundo en PASTIZAL/ROCA |
| *Rupicapra pyrenaica* | Migración altitudinal descendente | PASTIZAL alpino → BOSQUE_CON |
| *Cervus elaphus* | Migración altitudinal descendente | BOSQUE_CAD → BOSQUE_CON (menor cota) |
| *Tetrao urogallus* | Permanece, dieta cambia a acículas | BOSQUE_CON subalpino (refugio) |
| *Vulpes vulpes* | Activo todo el año | Cualquier hábitat |
| *Sus scrofa* | Activo, reduce actividad en nieve | BOSQUE_CAD, BOSQUE_CON |

---

## Fase 7: Referencias

### Fuentes de datos

| Fuente | Enlace |
|--------|--------|
| ICGC — Descarga de cartografía | https://visors.icgc.cat/appdownloads/ |
| ICGC — OpenICGC recursos abiertos | https://openicgc.github.io/ |
| ICGC — MDT 5m (2009–2018) | https://catalegs.ide.cat/geonetwork/srv/api/records/model-elevacions-terreny-topografic-catalunya-5m-2009-2018 |
| ICGC — LiDAR 50cm (2021–2023) | https://catalegs.ide.cat/geonetwork/rcc/api/records/lidar-territorial-v3r1-2021-2023 |
| ICGC — Mapa de Cobertes del Sòl (MCSC) | https://catalegs.ide.cat/geonetwork/rcc/api/records/cobertes-sol-v1r0-2024 |
| EU-DEM v1.1 (25m) | https://files.gpxz.io/eudem_buffered.zip |
| Copernicus DEM GLO-30 | https://portal.opentopography.org/ |
| OpenTopography (SRTM, ALOS, COP30) | https://portal.opentopography.org/datasets?group=global |
| CORINE Land Cover 2018 | https://land.copernicus.eu/en/products/corine-land-cover |

### Documentos del proyecto (vault)

| Documento | Contenido relevante |
|-----------|---------------------|
| `wiki/investigacion_parc_alt_pirineu.md` | Pisos bioclimáticos, especies, código Python DEM (líneas 80–154) |
| `wiki/costo_locomocion.md` | Costos MET por actividad, fórmula de gasto energético |
| `data/costos_actividad.tsv` | 19 actividades con MET y exponentes |
| `data/plant_clusters.tsv` | Fenología y biomasa por cluster |
| `data/invertebrate_clusters.tsv` | Fenología de I1, I2, I3 |
| `data/vertebrates.tsv` | Especies, masa corporal, dieta |
| `paper/paper.md` | Descripción detallada de especies y hábitats (sección 3.4) |
| `paper/plan.md` | Arquitectura del simulador (A* con coste de terreno) |

### Referencias científicas

1. Kleiber, M. (1932). Body size and metabolism. *Hilgardia*, 6, 315–353.
2. Nagy, K.A. (2005). Field metabolic rate and body size. *Journal of Experimental Biology*, 208, 1621–1625.
3. Pontzer, H. (2017). The energy cost of walking and running in animals. *Journal of Experimental Biology*, 220, 174–182.
4. Shipley, B. (1999). *Foraging ecology: energy costs of search and intake*.
5. Grimm, V., et al. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, 198, 115–126.
6. Railsback, S.F., & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling: A Practical Introduction*. Princeton University Press.

---

## Productos a generar en el vault

| Archivo | Contenido | Ubicación |
|---------|-----------|-----------|
| `terrain_dem_25m.tif` | DEM recortado a subcuenca | `ecosystem/data/` |
| `terrain_slope.tif` | Pendiente en grados | `ecosystem/data/` |
| `terrain_aspect.tif` | Orientación | `ecosystem/data/` |
| `terrain_tri.tif` | Ruggedness index | `ecosystem/data/` |
| `terrain_pisos.tif` | Pisos bioclimáticos clasificados | `ecosystem/data/` |
| `terrain_habitat.tif` | Mapa de hábitats simplificado | `ecosystem/data/` |
| `terrain_cells.tsv` | Grid completo (1 fila por celda) | `ecosystem/data/` |
| `terrain_costs.tsv` | Costos de locomoción por celda | `ecosystem/data/` |
| `river_network.tsv` | Red fluvial en el área | `ecosystem/data/` |
| `wiki/terrain_dem_explicacion.md` | Explicación del DEM procesado | `ecosystem/wiki/` |
| `wiki/terrain_habitat_explicacion.md` | Explicación del mapa de hábitats | `ecosystem/wiki/` |
| `wiki/terrain_costs_explicacion.md` | Explicación de costos de terreno | `ecosystem/wiki/` |
| `wiki/snow_model_explicacion.md` | Modelo de nieve estacional | `ecosystem/wiki/` |
| `wiki/hidrografia_explicacion.md` | Red fluvial y masas de agua | `ecosystem/wiki/` |
