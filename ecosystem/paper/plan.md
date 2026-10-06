# Plan de Trabajo: Paper del Simulador de Ecosistemas del Alt Pirineu

## Visión General

Este documento es el diario de a bordo para la elaboración de un artículo académico que describa el **Simulador Agent-Based del Ecosistema del Parc Natural de l'Alt Pirineu**. El artículo debe documentar tanto la construcción del modelo como los resultados ecológicos emergentes.

**Objetivo:** Publicar en una revista de ecología computacional o modelización ecológica (ej: *Ecological Modelling*, *Methods in Ecology and Evolution*, *PLOS Computational Biology*).

**Idioma:** Castellano (con título y abstract en inglés).

---

## Estructura Planificada del Paper

| Sección                     | Estado      | Notas |
|-----------------------------|-------------|-------|
| Título y autoría            | 🔲 Pendiente | Cambiar a español (actualmente en inglés); definir orden de autoría |
| Resumen / Abstract          | 🔲 Pendiente | Escribir al final |
| 1. Introducción             | ✅ Completado | Contexto ecológico, preguntas de investigación, estado del arte (actualizado con proyectos similares 2025-2026) |
| 2. Área de Estudio          | ✅ Completado | Parc Natural de l'Alt Pirineu, climas, orografía (actualizado con catálogo flora 2025) |
| 3. Materiales y Métodos     | ✅ Completado | Datos biológicos, red trófica, cálculos energéticos, arquitectura del simulador (3.8), mapas de terreno (3.9). 15 figuras, 52 ecuaciones. |
| 4. Resultados               | ✅ Completado | Simulaciones quick/medium/deep, tabla de resultados, limitaciones detectadas |
| 5. Discusión                | 🔲 Pendiente | Analizar mortalidad 90%, sesgo talla grande, comparación con literatura |
| 6. Conclusiones             | 🔲 Pendiente | Sintetizar hallazgos, hoja de ruta de mejoras |
| 7. Referencias              | ✅ Completado | 111 referencias (actualizado con censos 2025, PIPOL, MARL) |
| Material Suplementario      | ✅ Completado | Tablas TSV, JSON grafos, visualizador HTML, logs simulación |
| Anexo A                     | ✅ Completado | Fichas detalladas de 27 especies (movido de sección 3.4) |

---

## Pipeline Metodológico

```
[Datos de campo / Bases de datos]
       ↓
[Base de datos biológica maestra (328 especies)]
       ↓
[Datos estructurados TSV: vertebrados, plantas, invertebrados, matriz trófica]
       ↓
[Red trófica en grafos (JSON estándar + optimizado)]
       ↓
[Cálculos energéticos: DEE, costos de actividad, energía de los recursos]
       ↓
[VISUALIZADOR HTML interactivo] --- [SIMULADOR (Python + Numba JIT)]
                                               ↓
                                 [Hybrid Python-Rust (planeado)]
                                               ↓
                                      [Agentes, GOAP, A* pathfinding]
                                               ↓
                              [Mapas de terreno (DEM, pendiente, hábitat, biomasa)]
                                               ↓
                                      [Simulaciones ejecutadas (quick/medium/deep)]
                                               ↓
                                      [Análisis post-simulación]
```

---

## Progreso

### Fase 1: Datos y Estructuración ✅

- [x] Base de datos biológica maestra creada (328 líneas)
- [x] Tablas TSV: vertebrados (22 especies), plantas (3 clusters), invertebrados (3 clusters)
- [x] Matriz trófica (103+ interacciones documentadas)
- [x] Proporciones de dieta estimadas
- [x] Valores calóricos de los recursos
- [x] Gasto energético diario (DEE) estimado por especie
- [x] Costos metabólicos de actividad (19 comportamientos)
- [x] Grafos de red trófica (estándar + optimizado)
- [x] Visualizador HTML interactivo de la red trófica
- [x] Documentación completa en la Obsidian vault

### Fase 2: Cálculos Energéticos — Plan de Diagnóstico (7 etapas)

- [x] 2.1 Revisión bibliográfica del metabolismo
- [x] 2.2 Caracterización de la dieta
- [x] 2.3 Energía de los recursos
- [x] 2.4 Cálculo del DEE (Kleiber + FAct=2.0, primera aproximación)
- [x] 2.5 Cálculo de la Ingesta Energética Potencial (IEP)
- [x] 2.6 Validación de los valores energéticos (recalculado con parámetros taxon-específicos, comparado con Nagy 2005, IEP calculado, informe generado)
- [ ] 2.7 Integración al motor de simulación

### Fase 3: Simulador

- [x] Definir arquitectura: Python con Numba JIT + GOAP
- [x] Implementar sistema de movimiento (A* con coste de terreno + Numba JIT)
- [x] Implementar sistema de energía (Kleiber BMR + MET costs)
- [x] Implementar sistema de dieta (matriz trófica, proporciones)
- [x] Implementar sistema de reproducción (estacional, camadas)
- [x] Implementar sistema de clima (gradiente adiabático, nieve)
- [x] Implementar dinámica de vegetación (logístico P1/P2/P3, pastoreo)
- [x] Implementar motor GOAP (herbívoro, carnívoro, omnívoro, ave)
- [x] Pool de población (7 pools)
- [x] Carga de terreno real (SRTM 25m, 180K celdas)
- [x] Script de procesamiento MCSC completo (`src/process_mcsc.py`): 44 clases → 10 hábitats, descarga WFS, rasterización, biomasa inicial
- [x] Documentación completa del mapeo MCSC (44 clases → 10 tipos) en `ecosystem/wiki/terrain_habitat_explicacio.md`
- [x] **Mapas de terreno**: generados 15 mapas (DEM, pendiente, aspecto, TRI, pisos, hábitat, biomasa P1/P2/P3/I1/I2/I3, 3D, dashboard) en `output/maps/`
- [x] **Simulaciones ejecutadas**: quick (324 agentes, 20 días), medium (1.315 → 120 agentes, 360 días), deep (6.185 agentes, 10 días), validation (6.185 agentes)
- [ ] Conectar dieta real de `foodweb.py` al forrajeo de agentes (actualmente todos son omnívoros funcionales)
- [ ] Implementar depredación agente-a-agente (carnívoros no cazan actualmente)
- [ ] Conectar pools poblacionales (peces, herps, passerines, etc.) al consumo
- [ ] Implementar temperatura real en costos energéticos (is_cold hardcodeado)
- [ ] Optimizar rendimiento para 6.185 agentes completos
- [ ] Visualización en tiempo real (Plotly/Dash o animado)
- [ ] **Hybrid Python-Rust**: documentado en `HYBRID_APPROACH.md`, pendiente de implementar con PyO3 para offload de operaciones matemáticas batch (energía, forrajeo, búsqueda de vecinos)
- [ ] Análisis de sensibilidad: ejecutar 100+ réplicas para caracterizar varianza estocástica
- [ ] Validación con censos reales: oso pardo (108 ind., GSTOP 2025), quebrantahuesos (209 UT, VCF 2026), urogallo (declive 58%)
- [ ] Reestructurar a protocolo ODD (Overview, Design concepts, Details) para alineación con estándar ABM (Grimm et al. 2006, 2020)
- [ ] Añadir diagrama conceptual del modelo (flujo de datos, decisiones de agentes, interacciones)
- [ ] Consolidar 15 mapas de terreno en 1-2 figuras compuestas

### Fase 4: Paper

- [x] Redactar introducción
- [x] Redactar métodos (datos biológicos detallados por especie)
- [x] Redactar métodos (simulador) — arquitectura actualizada con implementación real
- [x] Insertar figuras de mapas de terreno (15 mapas: DEM, pendiente, aspecto, TRI, pisos, hábitat, biomasa, 3D)
- [x] Insertar resultados de simulación medium (360 días, 1.315→120 agentes)
- [ ] Redactar discusión — analizar mortalidad 90%, sesgo hacia individuos grandes, comparar con literatura
- [ ] Redactar conclusiones — sintetizar hallazgos, proponer hoja de ruta de mejoras
- [ ] Redactar resumen/abstract
- [ ] Cambiar título a español (actualmente en inglés)
- [ ] Eliminar mención a Rust del cuerpo del paper (no implementado, confunde al lector)
- [ ] Unificar referencias a formato consistente (APA)
- [ ] Unificar idioma: todo el paper en español (título, abstract, cuerpo)
- [ ] Añadir diagrama conceptual del modelo
- [ ] Consolidar 15 mapas en 1-2 figuras compuestas en lugar de 7+
- [ ] Enviar a revista

---

## Decisiones Técnicas y Metodológicas

### 2026-06-21 — Inicio del proyecto
- Se crea la base de datos maestra con 22 especies de vertebrados y clusters funcionales.
- Formato de datos: TSV para máxima compatibilidad y versionado.
- Red trófica representada como grafo dirigido (depredador → presa).
- DEE calculado con ley de Kleiber modificada por taxón, con FAct=2.0 para todos los vertebrados (primera aproximación, requiere refinamiento).
- Costos de actividad modelados con METs (Metabolic Equivalent of Task).

### 2026-06-22 — Plan de diagnóstico energético
- Se estructura el plan de 7 etapas para validar los cálculos energéticos antes de integrarlos al simulador.

### 2026-06-22 — Creación de la estructura del paper
- Se crean `plan.md` y `paper.md`.
- Decisión inicial de escribir en catalán → **cambiado a castellano** el 2026-06-22.
- Se plantea la simulación agent-based con GOAP/Behavior Trees sobre arquitectura ECS.

### 2026-06-22 — Redacción detallada de especies en el paper
- Se completa la sección de Materiales y Métodos con la descripción detallada de cada especie, incluyendo datos taxonómicos, tróficos, reproductivos, energéticos y estado de conservación.
- Se incorporan las 76 referencias de la base de datos maestra.
- El paper pasa a escribirse en castellano (decisión del autor).

### 2026-06-22 — Recopilación de info externa (informacion_unordered)
- Se crea la carpeta `informacion_unordered/` con 8 subcarpetas temáticas.
- Se realizan 3 rondas de búsqueda web (20+ consultas) sobre: parque, fauna, flora, clima, ecología, topografía, y proyectos similares.
- Información clave obtenida:
  - Censo oso pardo 2025: 108 individuos (GSTOP)
  - Quebrantahuesos 2025: 50 volantones en Pirineos, 209 unidades territoriales
  - Catálogo de flora vascular 2025: 1.765 especies
  - Población de urogallo: declive 58% en Pirineos centrales (2000-2017)
  - Desmán ibérico: contracción del 63.5% en áreas de Portugal
  - Proyectos similares: Multi-Agent RL (bioRxiv 2025), modelo ODE Pirineo (Nature Comms 2026), P-systems isard
- Se documenta toda la info con README explicativos y citaciones por subcarpeta.

### 2026-06-22 — Generación e inserción de imagen del grafo trófico
- Se crea `graph_analysis/visualize_graph.py` para generar una imagen publicable del grafo de red trófica.
- El script usa networkx (layout Kamada-Kawai), matplotlib (200 dpi, 32×24 pulgadas), colores por taxón, sin emojis.
- Se genera `ecosystem/paper/trophic_network_graph.png` (1.5MB, 75 nodos, 191 aristas).
- Se inserta la imagen en `paper.md` como Figura 1 en la sección 3.5 (Red Trófica), con caption explicativo.

### 2026-06-22 — Validación energética (Fase 2.6)
- Se crea `src/validate_energy.py` que recalcula DEE con parámetros alométricos específicos por taxón (no el Kleiber genérico de antes).
- Parámetros usados: Mammalia (a=70, b=0.75, FAct=2.5), Aves (a=129, b=0.67, FAct=2.8), Reptilia (a=0.16, b=0.88, FAct=3.0), Amphibia (a=0.20, b=0.80, FAct=2.5), Actinopterygii (a=0.13, b=0.80, FAct=2.0).
- Se compara con Nagy 2005 (FMR alométrico): mamíferos -29% desviación media, aves +27%, reptiles/amfibios ~-99% (ectotermos con masas muy pequeñas, BMR casi nulo en kcal/día → usar kJ).
- Se calcula IEP (Ingesta Energética Potencial) usando proporciones de dieta y densidades energéticas. La mayoría de especies muestran balance positivo o cercano a cero.
- Salidas: `ecosystem/wiki/validacion_energia.md` (informe), `ecosystem/data/validacion/validacion_energia.tsv` (datos), `ecosystem/data/validacion/validacion_energia.png` (gráficos).
- Se actualiza `ecosystem/data/dee_estimado.tsv` con los nuevos valores taxon-específicos.

### 2026-06-22 — Script de procesamiento MCSC completo
- Se crea `src/process_mcsc.py` que descarga datos MCSC vía WFS del ICGC, clasifica 44 clases → 10 hábitats funcionales, rasteriza a la cuadrícula de simulación, y genera capas de biomasa inicial.
- Se documenta el mapeo completo de 44 clases MCSC a 10 tipos de hábitat en `ecosystem/wiki/terrain_habitat_explicacio.md`.
- Pendiente: ejecutar para el PNAP completo (bbox: 0.95, 42.35, 1.50, 42.75) → ~180K celdas.

### 2026-06-22 — Generación de mapas de terreno
- Se crean `src/visualize_terrain.py` y `src/visualize_terrain_3d.py` para generar mapas publicables del terreno.
- Se generan 15 mapas en `output/maps/`: DEM, pendiente, aspecto, TRI, pisos bioclimáticos, hábitat (10 clases), biomasa de 3 clusters de plantas (P1/P2/P3) y 3 de invertebrados (I1/I2/I3), vista 3D, y dashboard compuesto 3×3.
- Los mapas se insertan en `paper.md` como Figuras 2-5.

### 2026-06-22 — Ejecución de simulaciones
- Se ejecutan 4 configuraciones de simulación sobre la subcuenca de Cardós (~2.500 celdas):
  - **quick**: 324 agentes, 20 días (3 réplicas)
  - **medium**: 1.315 agentes → 120 supervivientes, 360 días. Patrón: mortalidad temprana (días 40-260), estabilización ~120 agentes con biomasa creciente (126K → 263K kg) y energía decreciente (153K → 14K kcal).
  - **deep**: 6.185 agentes, 10 días
  - **validation**: 6.185 agentes, día 0
- Se detectan gaps críticos: la dieta de `foodweb.py` no se usa realmente (todos los agentes son funcionalmente omnívoros), no hay depredación agente-a-agente, los pools poblacionales están desconectados, y la temperatura está hardcodeada como `is_cold=False`.

### 2026-06-23 — Documentación del enfoque híbrido Python-Rust
- Se crea `HYBRID_APPROACH.md` que describe la estrategia para mejorar el rendimiento del simulador.
- Filosofía: **"Rust hace las matemáticas, Python controla los agentes"** — Rust (vía PyO3) procesa operaciones numéricas batch (energía, forrajeo, búsqueda de vecinos) mientras Python mantiene la flexibilidad para la lógica de decisión de agentes.
- Pendiente de implementar: el simulador actual usa Numba JIT para las operaciones matemáticas, y la migración a PyO3 está planificada pero no ejecutada.
- Se identifica que el enfoque híbrido no es crítico para el paper: el simulador Python+Numba JIT ya funciona y produce resultados. La optimización hybrida es un refinamiento técnico para escalar a más agentes.

### 2026-06-23 — Actualización mayor del paper: ecuaciones, mapas, resultados, anexos
- **Sección 3.8 (Arquitectura del Simulador)**: completamente reescrita con 12 subsecciones (3.8.1–3.8.12) y 52 ecuaciones matemáticas que formalizan todos los componentes del simulador: GOAP, balance energético, forrajeo, pathfinding A*, dinámica de vegetación, pools poblacionales, clima/nieve, reproducción.
- **Sección 3.9 (Mapas de Terreno)**: añadidas 15 figuras con captions explicativos (DEM, pendiente, aspecto, TRI, pisos, hábitat, 6 biomasas, 2 vistas 3D, dashboard).
- **Sección 4 (Resultados)**: datos de simulación medium (360 días, 1.315→120 agentes), tabla comparativa quick/medium/deep, análisis de patrón de mortalidad y limitaciones detectadas.
- **Anexo A**: movidas 22 fichas detalladas de especies desde sección 3.4; creada Tabla 1 compacta en cuerpo principal.
- **Referencias**: eliminado duplicado de encabezado; añadido nuevo material suplementario.
- **Gaps críticos identificados**: los 5 problemas (dieta no conectada, sin depredación A-A, pools desconectados, temperatura hardcodeada, reproducción bypass) significan que los resultados actuales pueden ser artefactos de simulación, no dinámicas ecológicas reales.
- **«Prioridad máxima:** corregir los 5 gaps del simulador antes de interpretar ecológicamente los resultados para el paper.»

### 2026-06-23 — Corrección de texto catalán en plan.md y adición de tareas de mejora
- Corregidas líneas en catalán a español (procesamiento MCSC, documentación, decision entries).
- Añadidas tareas de mejora a Fase 3: análisis de sensibilidad, validación con censos reales, protocolo ODD, diagrama conceptual, consolidación de mapas.
- Añadidas tareas a Fase 4: discusión, conclusiones, abstract, título español, eliminar Rust, formato referencias, diagrama conceptual, consolidar mapas.

---

## Preguntas Abiertas

- ~~¿Qué motor de simulación? Rust/Bevy vs Python/esper → **decidido: Python con Numba JIT**~~
- ~~Mapa de hábitats MCSC: pendiente de descargar para clasificar 44 clases → 10 tipos funcionales~~ ✅ **Completado**
- ¿Cómo validar el modelo? Comparar con datos de campo del parque. Datos disponibles: censo oso 2025 (108 ind.), quebrantahuesos 2025 (209 UT, 50 volantones), urogallo (declive 58%). ¿Hace falta colaboración con el PNAP?
- Factor de actividad (FAct): el valor 2.0 es genérico; hay que refinarlo por especie/estación. La validación energética mostró desviaciones de -29% (mamíferos) a +27% (aves) vs Nagy 2005.
- ¿Cómo modelar la competencia intraespecífica? ¿Exclusión competitiva implícita o explícita?
- Huevos de insectos: ¿hace falta incorporar especies de invertebrados individuales o mantener clusters funcionales?
- Visualización: ¿Plotly/Dash, Streamlit, o animación matplotlib con QGIS?
- **Prioridad máxima — 5 gaps críticos del simulador:**
  - **Dieta no conectada**: la dieta definida en `foodweb.py` no se usa en el forrajeo; todos los agentes son funcionalmente omnívoros.
  - **Sin depredación A-A**: carnívoros cazan pools de invertebrados, no agentes. Sin presión trófica real.
  - **Pools desconectados**: peces, herps, passerines, micromammals, bats crecen pero nunca son consumidos.
  - **Temperatura hardcodeada**: `is_cold=False` → no hay estrés invernal.
  - **Reproducción bypass**: `_should_reproduce()` nunca se llama; la reproducción depende solo del timer de lactancia.
- ¿La mortalidad del 90% en medium run es un artefacto de simulación o una dinámica ecológica real? Los 5 gaps sugieren que es mayoritariamente artefacto.
- ¿Reestructurar el paper a protocolo ODD? Añadiría claridad pero requiere cambiar la estructura actual.
- ¿Consolidar 15 mapas en 1-2 figuras compuestas para reducir el número de figuras en el paper?
- **Híbrido Python-Rust**: documentado pero no implementado. No es prioritario para el paper — el simulador Numba JIT funciona y produce resultados.

---

## Notas de Implementación del Paper

Cuando se complete una tarea del proyecto:
1. Documentar aquí qué se ha hecho y por qué.
2. Añadir o actualizar la sección correspondiente en `paper.md`.
3. Si la tarea afecta decisiones metodológicas, reflejarlo aquí.
