# Simulación Agent-Based del Parc Natural de l'Alt Pirineu

## Modelo Matemático Completo y Estado del Proyecto

---

## 1. Modelo Matemático

### 1.1 Procesamiento del Terreno

**Pipeline SRTM → Grid de Simulación:**

```
SRTM GL1 30m (EPSG:4326)
  → recorte ventana (lon: 1.2443-1.3554, lat: 42.5446-42.6557)
  → reproyección bilineal a EPSG:25831, resolución 25m
  → grid resultante: 375 × 502 celdas (188.250 total, ~180.000 válidas)
```

**Derivadas del terreno:**

**Pendiente** (Horn's algorithm, 3rd-order finite difference):
```
dzdx = (z[i-1][j+1] + 2·z[i][j+1] + z[i+1][j+1] - z[i-1][j-1] - 2·z[i][j-1] - z[i+1][j-1]) / (8·Δx)
dzdy = (z[i+1][j-1] + 2·z[i+1][j] + z[i+1][j+1] - z[i-1][j-1] - 2·z[i-1][j] - z[i-1][j+1]) / (8·Δy)
slope = arctan(√(dzdx² + dzdy²))
```

**Orientación (aspect):**
```
aspect = arctan2(dzdy, -dzdx)  → convertido a 0-360°
```

**TRI** (Terrain Ruggedness Index):
```
TRI = √( ⅛ · Σ(i=1..8) (z_i - z_central)² )
```

**Pisos Bioclimáticos:**
| Código | Piso | Elevación |
|--------|------|-----------|
| 1 | Montano | 650-1600 m |
| 2 | Subalpino | 1600-2300 m |
| 3 | Alpino | 2300-2700 m |
| 4 | Nival | >2700 m |

---

### 1.2 Clima

**Temperatura** (modelo sinusoidal anual + gradiente adiabático):
```
T_base(doy) = 5.0 + 10.0 · cos(2π · (doy - 182) / 365)
T(elev, doy) = T_base(doy) - 0.0065 · max(0, elev - 1000)
```
El lapse rate de -0.0065 °C/m es el gradiente adiabático seco estándar.

**Nieve** (modelo coseno estacional):
```
amplitude = cos(2π · (doy - 15) / 365)
snow_line = 2400 + 600 · (amplitude + 1) / 2
snow_cover(elev) = clamp((elev - snow_line) / 800, 0, 1)
```
El snow_line varía desde ~1800m (invierno) hasta ~2700m (verano).

**Estaciones:**
| Días | Estación |
|------|----------|
| 0-59 | Invierno |
| 60-151 | Primavera |
| 152-243 | Verano |
| 244-334 | Otoño |
| 335-364 | Invierno |

---

### 1.3 Sistema Energético

**Tasa Metabólica Basal** (Ley de Kleiber, 1932):
```
BMR (kcal/día) = 70 · M^0.75    (M = masa corporal en kg)
BMR (kcal/h) = BMR_día / 24
```

**Costo de Actividades** (método factorial MET):
```
Costo_actividad (kcal/h) = MET · BMR_h
```

**Valores MET por actividad:**
| Actividad | MET |
|-----------|:---:|
| Reposo termoneutral | 1.0 |
| Vigilancia | 1.3 |
| Ingestión de alimento | 1.5 |
| Acicalado | 1.5 |
| Interacciones sociales | 1.8 |
| Caminar lento (~1 km/h) | 2.0 |
| Termorregulación (frío) | 2.0 |
| Cortejo | 2.5 |
| Caminar moderado (~2 km/h) | 2.5 |
| Caminar rápido (~3.5 km/h) | 3.0 |
| Búsqueda de alimento | 3.0 |
| Lactancia | 3.0 |
| Trote | 4.5 |
| Escalada | 5.0 |
| Natación | 6.0 |
| Galope | 7.0 |

**Costo de locomoción ajustado por pendiente:**
```
MET_loco(slope) = 2.5   si  slope < 5°
                  3.0   si  5° ≤ slope < 15°
                  5.0   si 15° ≤ slope < 30°
                  6.0   si  slope ≥ 30°
```

**Gasto Energético Diario (DEE):**
```
DEE = Σ(MET_i · BMR_h · h_i) para todas las actividades i
```
Horas típicas: forrajeo=6h, locomoción=2h, reposo=12h, otras=4h.

**Ajustes:**
- Frío: `DEE += MET_termo · BMR_h · 2h` (MET_termo = 2.0)
- Lactancia: `DEE ×= 1.4`
- ⚠️ Gestación: **no implementada**. El MET `REPRO_GESTATION = 1.3` está definido en `ACTIVITY_COSTS` pero `daily_dee()` no lo aplica. Las preñaz gastan lo mismo que las no preñadas.

**Reserva energética:**
```
Reserva = masa · 5000 kcal/kg    (~tejido adiposo)
```

**Densidades energéticas de alimentos:**
| Tipo | kcal/kg |
|------|:-------:|
| Plantas | 800 |
| Carne | 1500 |
| Invertebrados | 2000 |

**Balance energético diario:**
```
Intake = kg_ingeridos · kcal_por_kg · η_asimilación
η_asimilación ≈ 0.6
ΔEnergía = Intake - DEE
```

---

### 1.4 Dinámica de Vegetación

Tres pools funcionales de plantas por celda:

| Pool | Tipo | Growth rate | Biomasa máxima típica |
|------|------|:-----------:|:---------------------:|
| P1 | Plantas entomófilas (dicotiledóneas) | 0.02/día | 2.0 kg/celda |
| P2 | Plantas acuáticas / helechos | 0.015/día | 1.5 kg/celda |
| P3 | Pastos (gramíneas) | 0.03/día | 5.0 kg/celda |

**Crecimiento logístico por celda:**
```
ΔP = growth_rate · growth_mod · P_max
P = clamp(P + ΔP - grazing, 0, P_max)
```

**Modificador estacional:**
```
growth_mod(season) = 1.0  (verano)
                     0.8  (primavera)
                     0.5  (otoño)
                     0.1  (invierno)
```

**Restricciones espaciales:**
- No crece en celdas con agua o nieve > 50%
- No crece en hábitat rocoso (ROCA)
- P_max depende del hábitat de la celda

---

### 1.5 Dinámica de Invertebrados

Tres pools tróficos de invertebrados:

| Pool | Tipo | Dependencia | Growth rate | Max |
|------|------|-------------|:-----------:|:---:|
| I1 | Polinizadores | Alimentación de P1 | 0.01/día | 0.5 kg |
| I2 | Fitófagos | Alimentación de P3 | 0.015/día | 0.8 kg |
| I3 | Depredadores | Alimentación de I2 | 0.008/día | 0.3 kg |

**Crecimiento:**
```
ΔI1 = 0.01 · growth_mod · P1 · 0.1
ΔI2 = 0.015 · growth_mod · P3 · 0.08
ΔI3 = 0.008 · growth_mod · I2 · 0.2
I = clamp(I + ΔI - predation, 0, I_max)
```

---

### 1.6 Pools Poblacionales Agregados

**Peces** (truita + barb roig):
```
river_km = n_water_cells · resolution_m / 1000
max_fish = river_km · 200 kg/km
truita = clamp(truita · (1 + 0.01), 0, max_fish · 0.7)
barb_roig = clamp(barb_roig · (1 + 0.015), 0, max_fish · 0.3)
```

**Reptiles + Anfibios:**
```
biomass += growth_rate · growth_mod · biomass
(growth_rate = 0.008, anfibios × 1.2)
```

**Passeriformes, Micromamíferos, Murciélagos:**
Crecimiento exponencial estacional simple (misma fórmula, distintas tasas).

---

### 1.7 Pathfinding (A* con costos de terreno)

**Función de costo de una celda:**
```
cost(celda) = slope_factor · snow_factor · terrain_factor
```

**Factor de pendiente:**
```
slope_factor(slope) = 1.0   si  slope < 5°
                      1.5   si  5° ≤ slope < 15°
                      2.5   si 15° ≤ slope < 30°
                      3.5   si  slope ≥ 30°
```

**Factor de nieve:**
```
snow_factor = 1.0 + snow_cover    (0-1 → 1.0-2.0)
```

**Factor de terreno:**
| Hábitat | Factor |
|---------|:------:|
| Bosque coníferas / caducifolio | 1.3 |
| Roca | 1.6 |
| Agua | 3.0 |
| Antrópico | 1.2 |
| Otros | 1.0 |

**Costo de movimiento diagonal:** `cost × √2 ≈ cost × 1.414`

**Algoritmo A***:
```
f(n) = g(n) + h(n)
g(n) = costo acumulado desde inicio
h(n) = distancia Euclidiana al objetivo
```
Implementado con Numba JIT para rendimiento.

---

### 1.8 Comportamiento de Agentes (GOAP simplificado)

**Ciclo diario de cada agente:**
```
1. Percibir entorno (radio 5-15 celdas)
2. Decidir acciones según estado y percepción
3. Ejecutar acciones (movimiento, forrajeo, reproducción)
4. Actualizar energía (DEE)
5. Actualizar biología (edad, gestación)
6. Verificar muerte (energía ≤ 0 o edad ≥ lifespan)
```

**Decisiones por tipo trófico:**

- **Herbívoro:** Si biomasa celda < 5% de su masa → moverse a mejor celda. Luego forrajear.
- **Carnívoro:** Detectar presas en radio 8. Si encuentra → cazar (A* + ataque). Si no → deambular.
- **Omnívoro:** Si hay comida → forrajear. Si no → buscar en radio 10.
- **Ave:** Similar al herbívoro pero con radio de detección mayor (15).

**Forrajeo:**
```
intake = min(available, M · 0.05)    (max 5% de masa corporal)
proporción_planta = P_total / (P_total + I_total)
P1 -= intake · prop_planta · 0.5
P2 -= intake · prop_planta · 0.2
P3 -= intake · prop_planta · 0.3
I1 -= intake · (1-prop_planta) · 0.3
I2 -= intake · (1-prop_planta) · 0.5
I3 -= intake · (1-prop_planta) · 0.2
```

**Búsqueda de mejor celda:**
```
score = (P_total + 2 · I_total) / max(cost_A*, 0.1)
```

---

### 1.9 Reproducción

**Condiciones:**
- Solo en primavera/verano
- Energía > umbral (herbívoro: M·2000, carnívoro: M·3000, omnívoro: M·2500 kcal)
- No gestando actualmente
- Días desde última reproducción > edad reproductiva

**Nacimiento:**
```
n_crías = random(litter_min, litter_max)
masa_cría = M_padre · random(0.05, 0.15)
posición = padre ± 2 celdas (aleatorio)
```

**Especies con parámetros:**
| Especie | Masa (kg) | Gestación (días) | Camada | Edad repro (días) | Lifespan (días) |
|---------|:---------:|:----------------:|:------:|:-----------------:|:---------------:|
| Isard | 35 | 150 | 1-2 | 365 | 3650 |
| Cérvol | 200 | 240 | 1 | 365 | 5475 |
| Cabirol | 20 | 150 | 2 | 730 | 3650 |
| Senglar | 100 | 120 | 3-8 | 365 | 5475 |
| Marmota | 4.5 | 33 | 2-4 | 730 | 3650 |
| Conill | 1.2 | 30 | 3-7 | 120 | 1825 |
| Esquirol | 0.3 | 38 | 3-6 | 365 | 2190 |
| Guineu | 6 | 52 | 4-6 | 365 | 3650 |
| Marta | 1.5 | 60 | 2-5 | 365 | 3650 |
| Mostela | 0.08 | 30 | 4-8 | 90 | 1095 |
| Gall fer | 4 | 28 | 6-8 | 365 | 2190 |

---

### 1.10 Clasificación de Hábitats (MCSC → 10 funcionales)

El MCSC (Mapa de Cobertes del Sòl de Catalunya) tiene 44 clases que se simplifican a 10 hábitats funcionales:

| Código | Hábitat | P1_max | P2_max | P3_max |
|:------:|---------|:------:|:------:|:------:|
| 1 | BOSQUE_CON (bosque coníferas) | 3.0 | 2.0 | 2.0 |
| 2 | BOSQUE_CAD (bosque caducifolio) | 4.0 | 3.0 | 3.0 |
| 3 | MATORRAL (matorral) | 3.0 | 1.5 | 4.0 |
| 4 | PASTIZAL (pastizal) | 1.0 | 0.5 | 5.0 |
| 5 | HUMEDAL (zona húmeda) | 2.0 | 3.0 | 3.0 |
| 6 | ROCA (roca) | 0.1 | 0.1 | 0.5 |
| 7 | AGUA (agua) | 0.1 | 2.0 | 0.0 |
| 8 | RIBERA (ribera) | 2.0 | 2.0 | 3.0 |
| 9 | NIEVE (nieve permanente) | 0.0 | 0.0 | 0.0 |
| 10 | ANTROPICO (antrópico) | 1.0 | 0.5 | 2.0 |

---

## 2. Estado del Proyecto

### 2.1 Completado ✅

| Componente | Archivo(s) | Detalle |
|-----------|------------|---------|
| Pipeline terreno SRTM | `process_terrain.py` | DEM 25m, slope, aspect, TRI, pisos (180K celdas) |
| Procesador MCSC | `process_mcsc.py` | Mapeo 44→10 hábitats, genera tif (485 líneas) |
| Grid de simulación | `sim/grid.py` | Celda con 20 campos, TerrainGrid, JIT costs |
| Clima | `sim/environment.py` | Temp modelo sinusoidal, nieve coseno estacional |
| Sistema energético | `sim/energy.py` | BMR Kleiber, MET factorial, DEE, Numba JIT |
| Pathfinding | `sim/pathfinding.py` | A* con costos de terreno, Numba JIT |
| Pools poblacionales | `sim/pools.py` | 7 pools (P1-3, I1-3, fish, herps, passerines, micromammals, bats) |
| Red trófica | `sim/foodweb.py` | 14 links tróficos, 5 proporciones de dieta |
| Agentes | `sim/agents/*.py` | Herbívoro, carnívoro, omnívoro, ave + GOAP |
| Orquestador | `sim/simulation.py` | Init, step, reproduce, logging, snapshots |
| Visualización | `visualize_terrain.py` | Mapas de DEM, pendiente, hábitat, biomasa |
| Puerto Rust | `ecosystem_simulator_rs/` | Grid, energy, environment, pathfinding, pools, agents, sim |
| Datos terreno | `ecosystem/data/*.tif` | 7 GeoTIFFs + TSV de 180K filas |

### 2.2 Pendiente (Alta Prioridad) ⬜

#### Funcionalidades Críticas

| # | Tarea | Impacto |
|:-:|-------|---------|
| 1 | **Depredación entre agentes** — Actualmente la depredación es implícita (pools). Los carnívoros individuales no cazan herbívoros individuales. | La dinámica trófica no emerge de interacciones agente-agente. |
| 2 | **Muerte por depredación** — Cuando un carnívoro ataca, no mata al agente presa. Solo consume biomasa del pool de invertebrados de la celda. | No hay cascada trófica real ni regulación poblacional por depredación. |
| 3 | **Pools globales no consumidos por agentes** — `HerpPool`, `PasserinePool`, `MicromammalPool`, `BatPool`, `FishPool` crecen exponencialmente sin que los agentes carnívoros los depreden. Solo la biomasa local de celda (`biomass_I1/I2/I3` y `biomass_P1/P2/P3`) se reduce por forrajeo directo. | La mayor parte de la red trófica (herpetofauna, aves, micromamíferos, murciélagos, peces) es un sumidero de carbono sin retroalimentación con los consumidores. La simulación no puede producir ciclos depredador-presa reales. |
| 4 | **Red fluvial explícita** — Noguera Pallaresa modelada como grafo de aristas en lugar de celdas AGUA inconexas. | Peces, nutrias y almesquera necesitan un hábitat lineal continuo con capacidad de carga por tramo de río. |
| 5 | **Spawning por hábitat** (completado en Rust, pendiente en Python) — Agentes aparecen aleatoriamente, ignorando preferencias de hábitat y piso bioclimático. | Isard aparece en bosque, gall fer en pastizal alpino. Sesgo inicial que distorsiona toda la simulación. |
| 6 | **Costo de gestación no aplicado** — `REPRO_GESTATION` (MET=1.3) está definido en `ACTIVITY_COSTS` y en `costos_actividad.tsv` pero `daily_dee()` no lo usa. Las hembras preñadas gastan la misma energía que las no preñadas. | Balance energético irreal durante la gestación. Subestima DEE en ~30% durante el embarazo. |
| 7 | **Carroña no modelada** — La fracción `carrion_proportion` existe en `Diet` y `get_diet()` la devuelve (p.ej. `Gypaetus_barbatus` 95% carroña, `Corvus_corax` 40%), pero ningún mecanismo genera carroña (agentes muertos no quedan como recurso). | Trencalòs y corb no tienen su fuente primaria de alimento. |

#### Rendimiento

| # | Tarea | Problema |
|:-:|-------|----------|
| 8 | **Caching de pathfinding** — Cada agente ejecuta A* cada día. Sin caché: 6000 agentes × 365 días = 2.2M llamadas A*. Cada A* recorre cientos de celdas en grid de 180K. | Simulación multi-año inviable en Python. La versión Rust ayuda pero el algoritmo O(n·log n) sigue siendo cuello de botella. |
| 9 | **Chunking del grid** — Dividir grid en regiones independientes (p.ej. 4 × 4 parches de ~100×125 celdas). | Facilitaría paralelización (cada chunk en su thread) y reduciría memoria de pathfinding. |

#### Datos

| # | Tarea | Estado |
|:-:|-------|--------|
| 10 | **MCSC vía WFS** — `process_mcsc.py` descarga datos del ICGC. El mapeo 44→10 clases está completo, pero la conexión WFS no se ha probado en esta máquina. | Script listo (485 líneas), depende de acceso a `geoserveis.icgc.cat`. |
| 11 | **Datos climáticos CHELSA** — Temperatura/precipitación mensual (1 km) para validar y calibrar `default_temp_fn` y `default_snow_fn`. | No descargados. |
| 12 | **Datos de GBIF/iNaturalist** — Presencia de especies para calibrar distribución espacial de agentes. | No integrados. |

#### Validación

| # | Tarea | Estado |
|:-:|-------|--------|
| 13 | **Calibración energética** — Comparar DEE simulada (Kleiber + MET) con valores empíricos (Nagy 2005, Speakman 2008, datos de campo PNAP). | Pendiente. |
| 14 | **Validación poblacional** — Densidades de agentes (individuos/km²) vs censos PNAP. | Sin datos de monitoreo. |

### 2.3 Pendiente (Media Prioridad)

| # | Tarea | Descripción |
|:-:|-------|-------------|
| 15 | **Dietas específicas no usadas en forrajeo** — `foodweb.py` define dietas detalladas por especie (p.ej. `Martes_martes`: 50% vertebrados, 30% invertebrados, 20% plantas), pero `forage_on_cell()` de `base.py` ignora la especie: todos los agentes comen la misma mezcla proporcional de `P_total` e `I_total`. | Todas las especies son funcionalmente idénticas. La diferenciación trófica no tiene efecto. |
| 16 | **Variabilidad interanual** — Clima, nieve y temperatura son idénticos cada año. | No permite estudiar respuesta a sequías, inviernos extremos, ni cambio climático. |
| 17 | **Hibernación / letargo invernal** — Marmota, murciélagos, erizo, etc. no reducen su metabolismo en invierno. | Su DEE sigue siendo el mismo, muriendo de inanición en invierno cuando la nieve cubre los pastos. |
| 18 | **Migración altitudinal** — Especies que bajan a cotas más bajas en invierno (isard, cérvol, quebrantahuesos). | Actualmente se quedan en su celda y mueren de hambre cuando la nieve cubre su hábitat. |
| 19 | **Banco de semillas** — P1/P2/P3 no tienen estado latente en el suelo. | Una celda pastoreada hasta 0 kg no puede regenerarse si la presión de pastoreo continúa — la biomasa debería persistir como semillas. |
| 20 | **Descomposición / ciclo de nutrientes** — No hay mineralización de materia orgánica. | Los nutrientes se eliminan del sistema cuando los agentes consumen biomasa. |
| 21 | **Competencia intraespecífica** — Agentes no compiten por recursos. Múltiples agentes pueden forrajear en la misma celda sin interferencia. | No hay límite de carga local ni exclusión competitiva. |
| 22 | **Dispersión juvenil** — Crías aparecen a ±2 celdas del progenitor, sin dispersión a larga distancia. | No hay colonización de nuevos hábitats ni flujo genético espacial. |
| 23 | **BirdAgent** — `bird.py` está definido pero nunca instanciado en `Simulation._create_agent()` porque ningún `PopulationConfig` usa `trophic="BIRD"`. | Las aves como `Tetrao_urogallus` se simulan como herbívoros genéricos. |
| 24 | **Eventos estocásticos** — No hay sequías, heladas tardías, inundaciones, ni aludes como perturbaciones. | El ecosistema es determinista: mismo input → misma salida. |

### 2.4 Pendiente (Baja Prioridad / Futuro)

| # | Tarea | Descripción |
|:-:|-------|-------------|
| 25 | **Sin distinción macho/hembra** — Cualquier agente puede quedarse preñado y lactar. | Reproducción poco realista, pero funcional para dinámica poblacional agregada. |
| 26 | **Modelo de fuego** — Incendios forestales como perturbación del paisaje. | Afectaría a bosques y matorral, creando mosaico sucesional. |
| 27 | **Presión humana** — Caza, senderismo, pastoreo, infraestructuras. | Relevante para ungulados y grandes carnívoros en el PNAP. |
| 28 | **Enfermedades infecciosas** — Sarna del isard (`Sarcoptes scabiei`), moquillo, etc. | Brotes epidémicos documentados en el Pirineo. |
| 29 | **Efecto Allee** — Problemas de encontrar pareja a baja densidad. | Umbral de extinción para especies con baja densidad (trencalòs, águila). |
| 30 | **Territorialidad** — Áreas de campeo con solapamiento limitado. | Actualmente todos los agentes pueden ocupar la misma celda. |
| 31 | **Carroña como dinámica** — Agentes muertos → biomasa disponible para carroñeros. | Conectar muerte de agente con recurso para `Corvus` y `Gypaetus`. |
| 32 | **Curvas de aprendizaje** — Eficiencia de forrajeo que mejora con la edad. | Relevante para especies longevas con transmisión cultural. |
| 33 | **Genética poblacional** — Deriva, endogamia, adaptación local. | Para estudios de viabilidad poblacional a largo plazo. |
| 34 | **Escenario cambio climático** — Aumento de temperatura + cambio fenológico. | Permitiría estudiar desplazamiento altitudinal de especies. |
| 35 | **Reintroducción de lobo** — `Canis lupus` como depredador apical ausente. | Cascada trófica: lobo → ungulados → vegetación. El escenario más impactante. |
| 36 | **Dashboard interactivo** — Plotly/Dash o Streamlit con visualización en tiempo real del grid, agentes y pools. | Facilitaría exploración y debugging. |
| 37 | **Mortalidad dependiente de edad** — Todos los agentes mueren exactamente al cumplir `lifespan_days`. No hay senescencia progresiva ni pico de mortalidad juvenil. | Simplificación aceptable para v1 pero elimina dinámicas de cohorte. |

---

## 3. Arquitectura del Código

```
src/
├── run_simulation.py        ← Entry point CLI
├── process_terrain.py       ← Pipeline SRTM → derivadas + TSV
├── process_mcsc.py          ← MCSC WFS → hábitats 10 clases
├── validate_terrain.py      ← Validación carga de datos
├── visualize_terrain.py     ← Mapas matplotlib
├── sim/
│   ├── __init__.py          ← Exporta Simulation
│   ├── simulation.py        ← Bucle principal + orquestación
│   ├── grid.py              ← TerrainGrid + Cell + JIT ops
│   ├── environment.py       ← Clima, nieve, temperatura
│   ├── energy.py            ← BMR, MET, DEE + Numba JIT
│   ├── pathfinding.py       ← A* con costos de terreno
│   ├── foodweb.py           ← Matriz trófica + dietas
│   ├── pools.py             ← 7 pools poblacionales
│   ├── io.py                ← Carga DEM, exportación datos
│   └── agents/
│       ├── __init__.py
│       ├── base.py          ← Agent base + AgentState + GOAP
│       ├── herbivore.py     ← Forrajeo + movimiento A*
│       ├── carnivore.py     ← Cacería + detección presas
│       ├── omnivore.py      ← Búsqueda mixta
│       └── bird.py          ← Ave (extensión, no usada)
├── scripts/
│   ├── sim_quick.sh         ← Test rápido (100×100, 30 días)
│   ├── sim_medium.sh        ← Test medio (200×200, 365 días)
│   └── sim_deep.sh          ← Test completo (375×502, 365 días)
└── output/                  ← Logs + snapshots generados
```

**Puerto Rust** (`ecosystem_simulator_rs/`):
- Misma arquitectura, módulos espejo
- Compila y ejecuta. Tiene spawning por hábitat implementado.
- IO lee de TSV (sin GDAL). Carga hábitats y biomasa por defecto según piso.

---

## 4. Cómo Contribuir / Próximos Pasos Recomendados

### Si tienes 1 hora:
1. Ejecuta `scripts/sim_quick.sh` (verifica que funciona)
2. Lee `sim/simulation.py` → `initialize()` → `_init_agents()` (spawning aleatorio)
3. Aplica el mismo patrón de hábitat-constrained spawning que ya está en Rust

### Si tienes 1 día:
4. Implementa depredación agente-a-agente en `sim/agents/carnivore.py`
5. Añade muerte por depredación en `sim/agents/base.py`

### Si tienes 1 semana:
6. Crea caché de A* (reduce llamadas de 2.2M a ~10K)
7. Descarga datos MCSC vía WFS para validar hábitats
8. Ejecuta `sim_deep.sh` y perfila cuellos de botella
