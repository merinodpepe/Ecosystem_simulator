# Arquitectura Detallada del Motor de Simulación Python

## Visión General

El motor de simulación del Parc Natural de l'Alt Pirineu está implementado en Python con optimizaciones de Numba JIT para las operaciones críticas de rendimiento. Sigue una arquitectura modular basada en entidades-componentes-sistema (ECS) simplificada, donde:

- **TerrainGrid**: Manage el terreno y sus propiedades (elevación, pendiente, hábitat, pisos bioclimáticos, biomassa)
- **Simulation**: Orquesta el bucle principal, gestiona agentes y pools
- **Agents**: Entidades individuales con comportamiento GOAP (Goal-Oriented Action Planning)
- **Pools**: Agregados de biomassa para organismos no modelados como agentes individuales
- **Environment**: Gestiona ciclos climáticos y estacionales
- **Energy**: Sistema metabólico basado en la ley de Kleiber y costos MET
- **Foodweb**: Define las interacciones tróficas y dietas de las especies
- **Pathfinding**: Implementación de A* con costos basados en terreno

## Estructura de Directorios del Código

```
src/
├── run_simulation.py              # Punto de entrada CLI
├── process_terrain.py             # Procesamiento de DEM SRTM
├── validate_terrain.py            # Validación de datos de terreno
├── process_mcsc.py                # Procesamiento de mapas de hábitat MCSC
├── visualize_terrain.py           # Visualización de terrenos
└── sim/                           # Núcleo de la simulación
    ├── __init__.py
    ├── simulation.py              # Bucle principal y gestión de agentes
    ├── grid.py                    # TerrainGrid y Cell (con operaciones JIT)
    ├── environment.py             # Ciclos estacionales y clima
    ├── energy.py                  # Sistema metabólico (Kleiber + MET)
    ├── pathfinding.py             # A* con costos de terreno
    ├── foodweb.py                 # Matriz trófica y dietas
    ├── pools.py                   # Gestión de pools de biomassa
    ├── io.py                      # Funciones de entrada/salida
    └── agents/                    # Implementaciones de agentes
        ├── __init__.py
        ├── base.py                # Clase base de Agent y AgentState
        ├── herbivore.py           # Herbivoro con GOAP
        ├── carnivore.py           # Carnívoro con GOAP
        ├── omnivore.py            # Omnívoro con GOAP
        └── bird.py                # Extensión para aves
```

## Flujo Principal de la Simulación

1. **Inicialización**
   - Carga de datos de terreno procesado (DEM, pendiente, aspecto, TRI, pisos, hábitat, biomassa)
   - Escalado de poblaciones basado en el área del terreno simulado
   - Apareado de agentes en celdas apropiadas según preferencias de hábitat y piso
   - Inicialización de pools de biomassa

2. **Bucle Principal (por día)**
   - Actualización del entorno (estación, línea de nieve)
   - Actualización de cobertura de nieve (JIT)
   - Paso de los pools de biomassa
   - Ejecución del paso de cada agente vivo:
     - Toma de decisiones (GOAP simplificado)
     - Ejecución de acciones (movimiento, forrajeo, reproducción)
     - Actualización de energía (metabolismo basal + actividades)
     - Actualización biológica (edad, gestación, lactancia)
     - Verificación de muerte (energía ≤ 0 o edad máxima)
   - Reproducción (solo en primavera/verano)
   - Limpieza de agentes muertos
   - Actualización de costos de pathfinding (JIT)
   - Registro y snapshots periódico

## Componentes Clave

### TerrainGrid y Clase Cell

La clase `TerrainGrid` gestiona una matriz 2D de objetos `Cell`, cada una representando una celda de 25m×25m. Cada celda almacena:

- **Propiedades topográficas**: elevación_m, slope_deg, aspect_deg, tri
- **Clasificación ecológica**: piso_bioclimatico, habitat_type
- **Estado dinámico**: snow_cover, is_water, is_riparian, cost_a_star
- **Biomassa**: 
  - Plantas: biomass_P1 (entomófilas), biomass_P2 (independientes), biomass_P3 (pastos)
  - Invertebrados: biomass_I1 (polinizadores), biomass_I2 (herbívoro), biomass_I3 (depredadores/parasitoides)

### Sistema de Agentes GOAP

Los agentes implementan una versión simplificada de GOAP (Goal-Oriented Action Planning):

- **Estados internos**: energía, edad, estado reproductivo, posición
- **Objetivos**: mantener energía por encima del umbral de supervivencia, reproducirse
- **Acciones disponibles**:
  - `MoveAction`: Usa A* para navegar hacia celdas con mejor ratio biomassa/costo
  - `ForageAction`: Consumir biomassa local y convertirla en energía
  - `ReproduceAction`: Iniciar gestación cuando las condiciones sean favorables

El método `_decide_actions()` determina qué acciones tomar basado en el estado actual y las condiciones locales.

### Sistema Energético

Basado en la ley de Kleiber para el metabolismo basal y equivalentes metabólicos (MET) para las actividades:

- **BMR (Basal Metabolic Rate)**: 70.0 × masa_kg^0.75 kcal/día
- **DEE (Daily Energy Expenditure)**: BMR × factor de actividad + costos específicos
- **Costos de actividad**: Definidos en `ACTIVITY_COSTS` con valores MET
- **Modificadores**: 
  - Lactancia: ×1.4 al gasto energético total
  - Frío: + actividad de termoregulación
  - Pendiente: afecta costos de locomoción

### Sistema de Reproducción

- **Madurez sexual**: Específica por especie (definida en `reproductive_age_days`)
- **Estación**: Solo ocurre en primavera y verano
- **Condiciones**: Energía suficiente y no embarazada actualmente
- **Proceso**: 
  - Acción `ReproduceAction` establece `is_pregnant = True`
  - Gestación avanza con cada paso (basado en `gestation_days_total`)
  - Al completar gestación: nacen crías, se establece lactancia
  - Las crías heredan propiedades de la madre con masa aleatoria (5-15%)

### Pools de Biomassa

Para organismos que no se modelan como agentes individuales (demasiado numerosos o pequeños):

- **Peces**: Truita común y barbo rosco
- **Herps**: Reptiles y anfibios
- **Passerines**: Aves passeriformes
- **Micromamíferos**: Roedores pequeños y insectivoros
- **Murciélagos**: Quirópteros

Cada pool tiene biomassa que crece basado en la biomassa de plantas disponible y se consume según las necesidades de los depredadores.

### Optimizaciones de Rendimiento

Uso extensivo de Numba JIT para bucles críticos:

- `step_plants_jit`: Crecimiento de biomassa vegetal
- `step_inverts_jit`: Crecimiento de biomassa de invertebrados
- `update_snow_jit`: Actualización de cobertura de nieve basada en elevación y día del año
- `update_costs_jit`: Recalculo de costos de pathfinding considerando pendiente, nieve y tipo de hábitat
- Funciones de energía: `bmr_kcal_day`, `activity_kcal_h`, `loco_cost_hours`, `daily_dee`

Estas optimizaciones permiten simular aproximadamente 6,000 agentes en 180,000 celdas con rendimiento aceptable.

## Parámetros de Configuración

Los parámetros clave se pueden ajustar en `src/run_simulation.py`:

- `--grid W H`: Dimensiones del grid (por defecto: 400×400)
- `--res RESOLUTION`: Resolución en metros (por defecto: 25m)
- `--days DÍAS`: Número de días a simular (por defecto: 365)
- `--demo`: Ejecuta una demostración rápida (30 días, 50×50 grid)
- `--profile`: Habilita perfilado básico
- `--output DIR`: Directorio de salida (por defecto: "output")

## Archivos de Salida

Durante la ejecución, se generan en el directorio de salida:

- `simulation_log.csv`: Registro diario de métricas (poblados vivos/muertos, biomassa total, energía promedio)
- `snap_XXXX.json`: Instantáneas periódicas con estado detallado de la simulación
- Otros archivos de diagnóstico según se implementen

## Extensiones Futuras Planificadas

1. **Integración de datos MCSC**: Mapas de hábitat reales para asignación precisa de biomassa
2. **Red hidrográfica**: Ríos y lagos del Noguera Pallaresa
3. **Preferencias de hábitat para apareado**: En lugar de apareado aleatorio
4. **Calibración energética**: Con datos de campo
5. **Simulaciones multi-año**: Con dinámicas estacionales completas
6. **Visualización en tiempo real**: Con Plotly/Dash o matplotlib animado
7. **Escenarios de prueba**: Reintroducción de depredadores, cambio climático, fragmentación de hábitat
8. **Validación contra datos de monitoreo PNAP**

## Relación con el Proyecto Rust

Existe un port en desarrollo del simulador en Rust usando el framework Bevy ECS para mejor rendimiento y capacidades de 3D. La versión Python sirve como prototipo y plataforma de investigación, mientras que la versión Rust apuntará a producción y visualización avanzada.

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*