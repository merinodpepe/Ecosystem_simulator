# Plan de Simulación Agent-Based — PNAP en Python

## Escenario: Subcuenca/valle ~10.000 ha, 3.000–8.500 agentes, 25m grid

---

## 1. Arquitectura del Simulador

```
src/sim/
├── __init__.py               # Exporta Simulation
├── simulation.py             # Bucle principal, orquestación
├── grid.py                   # TerrainGrid (160K celdas) + Cell
├── environment.py            # Clima, estacionalidad, nieve
├── energy.py                 # BMR, DEE, costos MET (Numba JIT)
├── pathfinding.py            # A* con costos de terreno (Numba JIT)
├── foodweb.py                # Matriz trófica, dietas por especie
├── pools.py                  # Pools poblacionales (plantas, inverts, peces, etc.)
├── io.py                     # Carga DEM, exportación CSV/JSON
├── data/                     # Datos de entrada
│   └── __init__.py
└── agents/
    ├── __init__.py
    ├── base.py               # Agent base, AgentState, acciones
    ├── herbivore.py          # Herbívoro: isard, cérvol, marmota...
    ├── carnivore.py          # Carnívoro: marta, àguila, mostela...
    ├── omnivore.py           # Omnívoro: ós, senglar, guineu...
    └── bird.py               # Ave (extensión)
```

### Flujo del timestep (diario)

```
1. Environment.step()           → día++, mes, estación, nieve
2. PlantPool.step()             → crecimiento P1/P2/P3 por celda
3. InvertebratePool.step()      → crecimiento I1/I2/I3
4. FishPool.step()              → biomasa truita/barb roig
5. HerpPool.step()              → reptiles + anfibios
6. PasserinePool.step()         → pájaros insectívoros
7. MicromammalPool.step()       → micromamíferos
8. BatPool.step()               → quirópteros
9. Para cada agente vivo:
   a. Perceive → escanea radio 5-10 celdas
   b. Decide → GOAP simple (forrajear, moverse, reproducirse)
   c. Move → A* con cost_a_star si es necesario
   d. Forage → consume biomasa de celda
   e. Energy → DEE - intake, actualiza reservas
   f. Biology → edad, gestación, nacimiento
   g. Death check → energía ≤ 0 o edad > lifespan
10. Reproduce → nuevas crías en primavera/verano
11. Remove dead → limpia agentes muertos
12. Grid.update_costs() → recalcula A* costs
13. Log cada N días
```

---

## 2. Sistema de Energía (validado)

### Fórmulas clave

| Variable | Fórmula | Fuente |
|----------|---------|--------|
| BMR (kcal/día) | `70 × M^0.75` | Kleiber 1932 |
| BMR (kcal/h) | `BMR_day / 24` | |
| Costo actividad (kcal/h) | `MET × BMR_h` | `costos_actividad.tsv` |
| DEE diario | `Σ(MET_i × BMR_h × h_i)` para todas las actividades | Nagy 2005 |
| Reserva energética | `M × 5000 kcal` | ~tejido adiposo |

### Costos por pendiente (basado en `costos_actividad.tsv`)

| Pendiente | Actividad | MET |
|-----------|-----------|:---:|
| < 5° | LOCO_WALK_MOD | 2.5 |
| 5–15° | LOCO_WALK_FAST | 3.0 |
| 15–30° | LOCO_CLIMB | 5.0 |
| > 30° | LOCO_CLIMB+ | 6.0 |

### Ejemplo: Isard de 35 kg

| Componente | Horas | MET | kcal |
|------------|:-----:|:---:|:----:|
| BMR base (24h) | 24 | 1.0 | 1004 |
| Descanso | 12 | 1.0 | 502 |
| Forrajeo | 6 | 2.0 | 502 |
| Locomoción (5°) | 2 | 2.5 | 209 |
| Otras | 4 | 1.5 | 251 |
| **DEE total** | **24** | | **~1.464** |

Ingesta: 1,75 kg plantas × 800 kcal/kg × 60% eficiencia = **840 kcal**
Balance diario: 840 − 1.464 = **−624 kcal** (déficit asumible con reservas)

---

## 3. Grid de Terreno

### Especificación

- **Resolución**: 25 m
- **Área**: subcuenca/valle de ~10.000 ha (10×10 km)
- **Celdas**: 400 × 400 = 160.000
- **Sistema coordenadas**: EPSG:25831 (ETRS89 UTM 31N)
- **Formato almacenamiento**: GeoTIFF (capas separadas) + TSV por celda

### Campos por celda

```
elevation_m    → altitud (del DEM)
slope_deg      → pendiente (derivada)
aspect_deg     → orientación
tri            → ruggedness index
piso           → 1=Montano 2=Subalpino 3=Alpino 4=Nival
habitat_type   → 1=BOSQUE_CON 2=BOSQUE_CAD ... 10=ANTROPICO
snow_cover     → 0.0–1.0 (estacional)
is_water       → bool
is_riparian    → bool
cost_a_star    → costo locomoción (slope × nieve × terreno)
biomass_P1/P2/P3 → kg biomasa vegetal
biomass_I1/I2/I3 → kg biomasa invertebrados
```

### Costo A* por celda

```
cost = slope_factor(slope) × snow_factor(snow) × habitat_factor(habitat)
```

---

## 4. Poblaciones: 3.000–8.500 agentes

### Agentes individuales (~3.000–8.500)

| Especie | ~Población | Masa | Trófico | Ámbito |
|---------|:----------:|:----:|:-------:|:------:|
| Isard | 1.200 | 35 kg | HERB | alpino |
| Cérvol | 350 | 200 kg | HERB | montano |
| Cabirol | 500 | 20 kg | HERB | subalpino |
| Senglar | 350 | 100 kg | OMN | montano |
| Marmota | 400 | 4,5 kg | HERB | alpino |
| Conill | 1.200 | 1,2 kg | HERB | montano |
| Esquirol | 250 | 0,3 kg | HERB | bosque |
| Guineu | 120 | 6 kg | OMN | generalista |
| Teixó | 80 | 11 kg | OMN | forestal |
| Marta | 100 | 1,5 kg | CAR | forestal |
| Gat fer | 30 | 4 kg | CAR | forestal |
| Ermíni | 200 | 0,15 kg | CAR | alpino |
| Mostela | 300 | 0,08 kg | CAR | generalista |
| Gall fer | 20 | 4 kg | HERB | subalpino |
| Perdiu xerra | 40 | 0,5 kg | HERB | alpino |
| Corb | 120 | 1 kg | OMN | generalista |
| Trencalòs | 2 | 5,5 kg | OMN | rupícola |
| Àguila reial | 2 | 4 kg | CAR | rupícola |

### Pools poblacionales (biomasa, no agentes individuales)

| Pool | Modelo | Variables |
|------|--------|-----------|
| P1 (entomófilas) | Crecimiento logístico por celda | kg/celda |
| P2 (acuáticas/helechos) | Crecimiento logístico por celda | kg/celda |
| P3 (pastos) | Crecimiento rápido por celda | kg/celda |
| I1 (polinizadores) | Dependiente de P1 | kg |
| I2 (fitófagos) | Dependiente de P3 | kg |
| I3 (depredadores) | Dependiente de I1+I2 | kg |
| Peces (truita + barb) | Capacidad de carga por km río | kg |
| Reptiles + anfibios | Biomasa total valle | kg |
| Passeriformes | Biomasa total bosque | kg |
| Micromamífers | Biomasa total (alta repro) | kg |
| Ratpenats | Biomasa nocturna | kg |

---

## 5. Integración con Datos Reales

### Pipeline de datos (Fase 1–2 del plan terreno)

```
DEM ICGC 5m + MCSC
    │
    ▼
gdal_merge + gdalwarp (EPSG:25831, 25m)
    │
    ▼
gdaldem slope + aspect + TRI
    │
    ▼
Clasificar pisos bioclimáticos (650-1600-2300-2700m)
    │
    ▼
Simplificar MCSC (44 clases → 10 hábitats funcionales)
    │
    ▼
Cargar en TerrainGrid (rasterio → numpy → Cell[][])
    │
    ▼
Asignar biomasa inicial por hábitat
    │
    ▼
Calcular cost_a_star
    │
    ▼
Inicializar agentes + pools
```

### Dónde vive cada especie según hábitat

| Especie | Hábitat | Piso |
|---------|---------|------|
| Isard | PASTIZAL, ROCA | Alpino |
| Gall fer | BOSQUE_CON (pino negro), MATORRAL | Subalpino |
| Marmota | PASTIZAL | Alpino |
| Sargantana pallaresa | ROCA | Alpino (>2.100m) |
| Nutria | AGUA, RIBERA | Montano–Subalpino |
| Trucha | AGUA (ríos fríos) | Montano–Subalpino |
| Águila real | ROCA (nidificación), general | Todo |
| Trencalòs | ROCA (nidificación) | Montano–Alpino |
| Marta | BOSQUE_CON, BOSQUE_CAD | Montano–Subalpino |

---

## 6. Implementación Actual (ya creada)

### Archivos en `src/`

| Archivo | Estado | Líneas | Descripción |
|---------|--------|:------:|-------------|
| `run_simulation.py` | ✅ Funcional | 85 | CLI entry point con --demo, --grid, --days |
| `process_terrain.py` | ✅ Funcional | 160 | Pipeline SRTM → recorte → reproyección → slope/aspect/TRI/pisos |
| `validate_terrain.py` | ✅ | 85 | Validación: carga datos reales en grid + 1 paso |
| `sim/__init__.py` | ✅ | 2 | Exporta Simulation |
| `sim/simulation.py` | ✅ | 240 | Bucle principal con escalado por área |
| `sim/grid.py` | ✅ | 140 | TerrainGrid + Cell (20 campos), slope_cost_factor |
| `sim/environment.py` | ✅ | 79 | Clima, estacionalidad, nieve estacional |
| `sim/energy.py` | ✅ | 120 | BMR Kleiber, DEE, costos MET (Numba JIT). Bug corregido |
| `sim/pathfinding.py` | ✅ | 105 | A* con cost_a_star (Numba JIT compilado) |
| `sim/foodweb.py` | ✅ | 95 | Matriz trófica con 14 links |
| `sim/pools.py` | ✅ | 200 | 7 pools: P1/P2/P3 plantas, I1/I2/I3 inverts, fish, herps, birds, mammals, bats |
| `sim/io.py` | ✅ | 155 | Carga DEM, load_processed_terrain(), export CSV/JSON |
| `sim/agents/__init__.py` | ✅ | 6 | Exporta agentes |
| `sim/agents/base.py` | ✅ | 165 | Agent + AgentState + GOAP acciones |
| `sim/agents/herbivore.py` | ✅ | 80 | Foraging y movimiento |
| `sim/agents/carnivore.py` | ✅ | 105 | HuntAction, búsqueda de presas |
| `sim/agents/omnivore.py` | ✅ | 65 | Búsqueda mixta |
| `sim/agents/bird.py` | ✅ | 40 | Extensión para aves |

### Tests realizados

- ✅ **30-day demo**: 78 agentes, 2.500 celdas, 1.2×1.2 km. Todos sobreviven, balance energético estable
- ✅ **Pools**: invertebrados, peces, reptiles, passeriformes, micromamíferos, murciélagos funcionando
- ✅ **Numba JIT**: A* y funciones energéticas compiladas con caché
- ✅ **Escalado poblacional**: por área funcional (referencia 10.000 ha)
- ✅ **Carga de terreno real**: SRTM recortado a Vall de Cardós, reproyectado a 25m EPSG:25831
- ✅ **375×502 grid**: 180.037 celdas válidas con elevación, pendiente, aspecto, TRI, pisos
- ✅ **1 paso simulación**: 13 agentes de 3 especies en terreno real, todos vivos

### Archivos generados en `ecosystem/data/`

| Archivo | Tamaño | Contenido |
|---------|--------|-----------|
| `terrain_dem_25m.tif` | 752 KB | DEM 25m, EPSG:25831 |
| `terrain_slope.tif` | 782 KB | Pendiente en grados |
| `terrain_aspect.tif` | 791 KB | Orientación (0–360°) |
| `terrain_tri.tif` | 785 KB | Terrain Ruggedness Index |
| `terrain_pisos.tif` | 49 KB | Pisos: 37% Montano, 51% Subalpino, 12% Alpino |
| `terrain_cells.tsv` | 8,8 MB | Grid completo (180.037 filas) |

---

## 7. Pasos Siguientes

### Alta prioridad

1. **Descargar MCSC** — Mapa de coberturas del suelo para hábitats reales
   - Fuente: https://visors.icgc.cat/appdownloads/ → "Cobertes del sòl"
   - Simplificar 44 clases → 10 hábitats funcionales
   - Asignar biomasa inicial por hábitat
2. **Optimizar rendimiento** — 6.185 agentes con A* en 180K celdas es lento
   - Posibles soluciones: pathfinding caching, grid chunks, reducir agentes de pool
3. **Visualizar terreno** — Mapa de elevación/pisos con matplotlib

### Media prioridad

4. **Añadir hidrografía** — Red fluvial del Noguera Pallaresa
5. **Reproducción por hábitat** — Agentes spawn en hábitat preferido, no aleatorio
6. **Calibrar energía** — Ajustar balance con datos de campo
7. **Simulación multi-anual** — 3.650+ días con estacionalidad completa

### Baja prioridad

8. **Visualización tiempo real** — Plotly/Dash o matplotlib animado
9. **Validación contra monitoreo PNAP**
10. **Análisis de sensibilidad** y escenarios (cambio climático, depredación)

---

## 8. Cómo Usar

```bash
# Instalar dependencias
pip install numpy numba rasterio geopandas shapely pyproj matplotlib pandas pyyaml

# Demo rápida (30 días, grid 50×50)
python src/run_simulation.py --demo

# Simulación completa (1 año, grid 400×400 para 10.000 ha)
python src/run_simulation.py --grid 400 400 --days 365

# Con datos reales (cuando tengas el DEM procesado)
python src/run_simulation.py --grid 400 400 --days 3650 --dem data/terrain_dem_25m.tif
```
