# Hoja de ruta — Simulador realista del Alt Pirineu

> Documento de referencia (creado el 2026-09-27) a partir de la revisión de un consejo de tres modelos: arquitectura (Opus), viabilidad y tests (Sonnet) y crítica en contra (Fable).
> **Objetivo elegido:** un simulador *ecológicamente realista*. El paper es secundario.
> Este es el documento vivo del estado del proyecto. Sustituye a `docs/archive/ESTADO_ACTUAL.md` y a las partes obsoletas de `PENDIENTE.md`.

---

## 1. De qué va el proyecto

Es un **modelo basado en agentes (ABM)** del Parc Natural de l'Alt Pirineu. Consta de:

| Componente | Dónde | Estado |
|---|---|---|
| Motor de simulación (Rust) | `simulator/src/sim/` | Activo. Es el único motor real |
| Pipeline de terreno (Python) | `src/process_terrain.py`, `src/process_mcsc.py` | Funciona. Genera `ecosystem/data/terrain_*` |
| Visor 3D (Ursina) | `src/ursina_*.py` | Funciona con snapshots |
| Gráficos | `src/visualize_simulation.py` | Funciona |
| Validación energética | `src/validate_energy.py` | Funciona (Nagy 2005) |
| Datos | `ecosystem/data/*.tsv` | **Fuente única de verdad** |
| Documentación / vault | `ecosystem/wiki/` | Parcialmente desfasada |
| Paper | `ecosystem/paper/` | Borrador. Describe un motor Python que ya no existe |
| Motor Python antiguo | `src/sim_legacy/` | Obsoleto. Solo lo usa `validate_terrain.py` |

**Área real simulada:** la malla `terrain_cells.tsv` mide 375×502 celdas de 25 m, unas 9,4 × 12,5 km, es decir **≈ 11.700 ha**. No son las 80.000 ha del parque. Hay que declararlo así en cualquier documento.

---

## 2. Diagnóstico: qué estaba mal (septiembre 2026)

Todas las salidas que existían eran **anteriores** al código actual (código del 06/07 y salidas del 23/06), y colapsaban (173 → 8 agentes con la comida creciendo) o explotaban (conejo ×2, comadreja ×4 en 30 días).

### 2.1 Errores que por sí solos invalidan los resultados
| # | Problema | Dónde | Efecto |
|---|---|---|---|
| E1 | **Nieve invertida**: cota a 3000 m en enero y a 2400 m en julio, sin bajar nunca de 2400 m | `grid.rs::step_snow`, `environment.rs::default_snow_fn` | Más nieve en verano que en invierno. Montano y subalpino nunca tienen nieve |
| E2 | **La depredación crea biomasa**: éxito del 100 %, el depredador gana el 80 % de la presa entera y además queda un 70 % como carroña | `simulation.rs::predation_tick` | Energía de la nada. Un águila de 4 kg se "come" un isard de 35 kg |
| E3 | **Carroñeros sin carroña**: el cargador de dietas nunca rellena `carrion_proportion` ni `fish_proportion`, y los enlaces con recurso `Various` (todos los de carroñeo) se descartan | `foodweb.rs::load_diet_data`, `load_trophic_data` | Trencalòs y corb mueren de hambre. La llúdriga no come peces |
| E4 | **Comer carroña sin carroña**: `tick_eat_carcass` da energía aunque la celda esté vacía | `agents.rs` | Energía de la nada |
| E5 | **Doble cobro de comida**: varios agentes en paralelo en la misma celda reciben la energía completa y luego el recurso se recorta a ≥ 0 | `simulation.rs::tick` | Energía de la nada |
| E6 | **Densidades energéticas mal enlazadas**: las claves no coinciden con el TSV (`"Plantas/Fruto seco"` frente a `"Fruto seco (nuez, avellana)"`). La mezcla vegetal obtiene el 84 % de su energía del valor de la nuez (5,5 kcal/g) | `energy.rs` | Energía vegetal ×4 |
| E7 | **Invertebrados en peso seco etiquetado como húmedo** (insectos 4,2-5 kcal/g, lombriz 3,8 kcal/g) | `energia_recursos.tsv` | Energía de invertebrados ×3-5 |
| E8 | **La hibernación no comprueba la inanición**: la grasa puede quedar negativa | `agents.rs::tick` | Marmotas inmortales en invierno |
| E9 | **Las crías nacen gratis** (3000 kcal/kg sin coste para la madre), no hay coste de gestación ni lactancia (`daily_dee` no se usa) | `simulation.rs::reproduce_step` | Explosiones de pequeños mamíferos |
| E10 | **La inanición no deja cadáver**; no existe muerte por vejez | `agents.rs`, `simulation.rs` | Poca carroña; individuos inmortales |

### 2.2 Problemas de diseño que impiden el realismo
- **Capacidad de carga impuesta:** el factor de densidad es la población actual dividida por el conteo inicial de `DEFAULT_POPULATIONS`, así que el equilibrio está fijado de antemano y no emerge.
- **Escalas irreales:** plantas unas 20-50 veces por debajo (≈ 60 kg/ha frente a 1000-3000 kg MS/ha en pastos alpinos). Pools unas 100-1000 veces por debajo (micromamíferos ≈ 0,004 kg/ha frente a 0,5-3 kg/ha).
- **Pools no espaciales y sin hambre:** cada carnívoro recibe cada día el 10 % de su masa de un pool global, esté donde esté y tenga hambre o no.
- **Demografía:** no se comprueba la edad reproductiva, no hace falta macho, las crías no crecen y la fenología es incorrecta (celo y partos solo en primavera/verano, sin relación con la gestación real).
- **Decisión:** solo se decide cada 600 ticks (5 h); se come solo si `energy_ratio < 0.3` y con una probabilidad del 40 %.
- **Parámetros escritos en el código** (21 especies en `simulation.rs`) en lugar de leerse de los TSV.
- **Resolución temporal excesiva:** 2880 ticks/día no se pueden validar y hacen inviables décadas de simulación y réplicas.
- **Faltan procesos clave del sistema real:** ganado y transhumancia (principal herbívoro estival y principal fuente de carroña), caza, oso.

### 2.3 Infraestructura de confianza inexistente
- Sin control de versiones (se ha hecho `git init` el 2026-09-27).
- Cero tests (`#[test]`) y `tests/` vacío.
- Sin semilla aleatoria (`thread_rng()`): no hay reproducibilidad.
- Datos duplicados byte a byte (`species_data/` = `ecosystem/data/`).
- Documentación que exagera el avance (`HYBRID_APPROACH.md` describe un motor que no existe; `PENDIENTE.md` da por hechas tareas que no lo están).

---

## 3. Plan por fases

Leyenda: ✅ hecho · 🔄 en curso · ⬜ pendiente

### Fase 0 — Base de confianza
| Tarea | Estado |
|---|---|
| `git init` | ✅ (sin commits: los hace el usuario) |
| Una sola fuente de datos (`ecosystem/data/`) | ⬜ Ver §4, requiere borrar `species_data/` |
| Añadir `--seed` a la CLI y generadores de números aleatorios sembrados (reproducibilidad, también en paralelo) | ver Fase 1 |
| Escribir el ODD "Purpose & Patterns" (1-2 preguntas y 3-5 patrones observables) | ⬜ **Decisión del usuario** |

Patrones candidatos para el ODD:
1. Persistencia de todas las especies a 10 años, sin colapsos por debajo del 10 % ni explosiones de más de 10×.
2. Estacionalidad de la nieve: cobertura máxima en enero-febrero y cota de nieve en torno a 1500 m en invierno.
3. Orden relativo de densidades entre especies (`vertebrates.tsv`).
4. Balance energético frente a `validacion_energia.tsv` (DEE dentro de ±30 % de Nagy 2005).
5. Densidad de isard comparable a censos del parque (si se consiguen datos por unidad de caza).

### Fase 1 — Reproducibilidad y tests de invariantes
- Añadir `--seed <u64>`. Cada agente lleva su propio `StdRng`, derivado de la semilla y de su id, para que el resultado sea determinista aunque se use Rayon en paralelo.
- Tests `#[cfg(test)]`:
  - conservación de masa y energía en forrajeo, carroña y depredación;
  - las dietas cargadas suman 1;
  - la nieve cubre más en invierno que en verano;
  - misma semilla → misma trayectoria;
  - carroña vacía → 0 energía;
  - las crías cuestan energía a la madre.

### Fase 2 — Corregir los errores E1-E10
- **E1** Nieve con fase correcta (cota ≈ 1500 m el 15 de enero y ≈ 3000 m en julio), en una sola función.
- **E2** Depredación: el depredador come hasta su capacidad y el resto pasa a carroña. Probabilidad de éxito por encuentro. Las presas mucho mayores que el depredador solo son vulnerables si son crías o están debilitadas. Saciedad. Índice espacial por celda en lugar de O(n²).
- **E3** Nuevas categorías de dieta `Carroña` y `Peces` en `dieta_proporciones.tsv` para las especies con enlaces de carroñeo o piscívoras. Los enlaces `Various` se conservan pero no cuentan como presas concretas.
- **E4 / E5** Los agentes *solicitan* comida. La simulación la reparte proporcionalmente entre los que piden en la misma celda y solo se paga la energía de lo realmente consumido.
- **E6** Búsqueda de densidades por prefijo de subtipo. Energía vegetal por clúster en materia seca.
- **E7** Corregir el TSV de invertebrados a peso húmedo.
- **E8** Muerte por agotamiento de grasa también durante la hibernación.
- **E9** Coste de gestación y lactancia (MET de `costos_actividad.tsv`). La energía de las crías sale de la madre.
- **E10** Toda muerte genera carroña. Muerte por vejez.

### Fase 3 — Escalas y demografía
- Biomasa vegetal en **kg de materia seca por hectárea** según hábitat, escalada al tamaño de celda. Senescencia invernal. La comida bajo la nieve es inaccesible.
- Invertebrados con capacidad por hectárea y crecimiento logístico.
- Pools (peces, anfibios/reptiles, paseriformes, micromamíferos, murciélagos) con densidades por hectárea de hábitat adecuado, crecimiento logístico y **consumo Holling tipo II** restringido a agentes que estén en hábitat adecuado y tengan hambre.
- **Capacidad de carga emergente:** se elimina el factor de densidad basado en el conteo inicial.
- Parámetros de especie en un TSV (`ecosystem/data/species_params.tsv`) en lugar de escritos en el código.
- Demografía: edad reproductiva, necesidad de macho, fenología derivada de la gestación (concepción ≈ fecha de parto objetivo − gestación), crías pequeñas que crecen, mortalidad por edad.
- Decisión basada en el déficit energético, replanificación cada hora y sin interrumpir desplazamientos en curso.

### Fase 4 — Resolución temporal y rendimiento
- Pasar de 2880 a 24-48 pasos/día (1 h o 30 min).
- A* con buffers reutilizados; detección de presas reales mediante índice espacial.

### Fase 5 — Ecología que falta
- Hibernación correcta de marmota y oso (entrada y salida por temperatura o fecha).
- Añadir el oso.
- **Ganado y transhumancia** como forzamiento externo (carga de pastos entre junio y octubre y carroña doméstica).
- Caza como mortalidad anual.
- Cargar los GeoTIFF (`--features geo`) para usar hábitat, agua y biomasa reales.

### Fase 6 — Calibración y validación
- Screening de Morris sobre unos 15-20 parámetros en malla de 100×100 o 200×200, con réplicas en paralelo.
- Validación orientada a patrones (POM) frente a los patrones del ODD.
- Decidir si se mantiene el IBM para todas las especies o se pasan a cohortes las no focales (propuesta del crítico: IBM solo para oso, trencalòs, gall fer e isard).

### Paralelo — Documentación
- Actualizar `PROJECT_OVERVIEW.md`, `PENDIENTE.md` y el paper para que reflejen el motor Rust real y el área real.

---

## 4. Limpieza del proyecto (pendiente de confirmación del usuario)

El modo automático no permite borrar archivos. Lista revisada de lo que es seguro eliminar:

| Ruta | Motivo |
|---|---|
| `ursina` (12 MB) | Es un **PostScript** (captura accidental de `import ursina` ejecutado en bash). No es la librería |
| `species_data/` | Copia idéntica byte a byte de 5 TSV de `ecosystem/data/`. Riesgo de editar la copia equivocada |
| `informacion_unordered/` (raíz) | Copia idéntica de `ecosystem/informacion_unordered/` |
| `topological_data/`, `models_compressed/` | Carpetas vacías |
| `ecosystem/ecosystem/` | Contiene solo un `.md` vacío |
| `ecosystem/Otra explicación relacionada.md` | Archivo vacío |
| `scripts/sim_*.sh` | Llaman a `src/run_simulation.py`, que no existe |
| `.ruff_cache/`, `ecosystem/.ruff_cache/`, `src/__pycache__/` | Cachés |
| `output/quick_*`, `output/deep_*`, `output/validation/`, `output/simulation_log.csv`, `output/snap_0000.json` | Salidas del motor Python antiguo |
| `simulator/output*/`, `simulator/run_script_test/` | Salidas generadas con código anterior; no se corresponden con el motor actual |

Hay que **conservar** `output/maps/` (figuras del paper), `output/terrain_mesh/`, `output/snapshots*/` (visor) y `output/medium_20260622_202003/` (citado en `paper.md`).

A archivar (mover a `docs/archive/`): `HYBRID_APPROACH.md`, `docs/ESTADO_ACTUAL.md`, `src/PLAN_SIMULACION.md`. Renombrar `execucio.md` → `docs/VISOR_3D.md` (su contenido es la guía del visor, distinta de `EXECUCIO.md`).

Comandos (ejecútalos tú con `!` si estás de acuerdo):
```bash
rm -rf ursina species_data informacion_unordered topological_data models_compressed \
       ecosystem/ecosystem "ecosystem/Otra explicación relacionada.md" scripts \
       .ruff_cache ecosystem/.ruff_cache src/__pycache__ \
       output/quick_2026* output/deep_2026* output/validation output/simulation_log.csv output/snap_0000.json \
       simulator/output simulator/output_calibrated simulator/output_v5 simulator/output_full_scale simulator/run_script_test
mkdir -p docs/archive && mv HYBRID_APPROACH.md docs/ESTADO_ACTUAL.md src/PLAN_SIMULACION.md docs/archive/
mv execucio.md docs/VISOR_3D.md
```

---

## 5. Registro de cambios de las fases 1-3

Ver la sección 6, que se actualiza al terminar cada fase.

## 6. Estado tras la ejecución automática

**Ejecución automática detenida (2026-09-27).** El clasificador del modo automático bloquea modificar o borrar archivos existentes que no tienen historial git ("Irreversible Local Destruction"). También bloqueó el commit inicial.

Hecho:
- `git init` (repositorio vacío, sin commits).
- Este documento.
- `ecosystem/data/species_params.tsv` (nuevo): parámetros de las 21 especies sacados de `simulation.rs`, más fenología (`birth_doy`, `breeding_window_days`), masa neonatal y reparto carroña/peces de la fracción de vertebrados. Cambios respecto al código antiguo: edad reproductiva de isard y marmota 365 → 730 días, guineu 365 → 300 y corb 365 → 730.
- `simulator/src/sim/energy.rs` reescrito para las fases 2-3: densidades por prefijo (E6), invertebrados convertidos a peso húmedo (E7), energía vegetal en materia seca por clúster, límite de ingesta por alcance metabólico, coste de gestación y lactancia (E9) y tests. **El resto del motor todavía usa la API antigua, así que ahora mismo `cargo build` falla.** Copia del código original: `/tmp/claude-1000/-home-pepe-proyectos-ecosystem-simulator/47618bda-1c11-48e2-8b6b-7d1cadf1f9f1/scratchpad/simulator_src_backup/`.

Pendiente de permiso: fases 1-3 en `environment.rs`, `grid.rs`, `io.rs`, `pools.rs`, `foodweb.rs`, `agents.rs`, `simulation.rs` y `main.rs`; la limpieza de §4; y el reparto de carroña/peces directamente en `dieta_proporciones.tsv`.
