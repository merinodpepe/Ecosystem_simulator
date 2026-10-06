# Sistema de Pathfinding A* Detallado - Movimiento Inteligente en Terreno Complejo

## Visión General

El sistema de pathfinding en el simulador del Parc Natural de l'Alt Pirineu implementa el algoritmo A* (A-estreno) optimizado para encontrar caminos de movimiento eficientes considerando la dificultad del terreno, pendiente, cobertura de nieve y tipo de hábitat. Este sistema permite que los agentes naveguen de manera realista hacia ubicaciones con mejores recursos mientras minimizan el gasto energético asociado al movimiento.

## Fundamentos del Algoritmo A*

El algoritmo A* combina las ventajas de Dijkstra's algorithm (garantía de camino óptimo) y la búsqueda voraz primera mejor (eficiencia mediante heurística). Utiliza la función de evaluación:
```
f(n) = g(n) + h(n)
```

Donde:
- **g(n)**: Costo real desde el nodo inicial hasta el nodo n
- **h(n)**: Heurística que estima el costo desde el nodo n hasta el objetivo (admisible y consistente)
- **f(n)**: Estimación total del costo del camino que pasa por n

En nuestra implementación:
- g(n) se acumula como la suma de los `cost_a_star` de las celdastravesadas
- h(n) usa la distancia de Manhattan (o euclidiana al cuadrado) como heurística admisible
- El algoritmo termina cuando encuentra el objetivo o explora todas las opciones alcanzables

## Implementación en el Código

### Función Principal A*

Ubicada en `src/sim/pathfinding.py`:

```python
def a_star(grid: TerrainGrid, start: tuple[int, int], goal: tuple[int, int], max_steps: int = 500) -> list[tuple[int, int]]:
    """
    Algoritmo A* para encontrar el camino de menor costo entre dos puntos.
    
    Args:
        grid: TerrainGrid containing the navigation map
        start: Coordenadas (x, y) de inicio
        goal: Coordenadas (x, y) objetivo
        max_steps: Número máximo de nodos a explorar (previene bucles infinitos)
        
    Returns:
        Lista de coordenadas [(x1,y1), (x2,y2), ...] que representan el camino,
        o lista vacía si no se encuentra camino
    """
    # Implementación estándar de A* con heap de prioridad
    # ...
```

### Cálculo de Costos de Movimiento

La clave del realismo está en cómo se calcula `cell.cost_a_star` para cada celda, que representa el costo relativo de atravesar esa celda.

#### Factores que Influencian en el costo_a_star

1. **Factor de Pendiente** (basado en grados):
   - 0-5°: factor = 1.0 (terreno llano)
   - 5-15°: factor = 1.5 (pendiente suave)
   - 15-30°: factor = 2.5 (pendiente moderada)
   - >30°: factor = 3.5 (pendiente empinada)

2. **Factor de Cobertura de Nieve**:
   - factor = 1.0 + snow_cover (donde snow_cover está en rango [0,1])
   - Sin nieve: factor = 1.0
   - Nieve completa: factor = 2.0 (el doble de costo)

3. **Factor de Tipo de Hábitat**:
   - Bosque de coníferas (BOSQUE_CON): factor = 1.3
   - Bosque caducifolio (BOSQUE_CAD): factor = 1.3
   - Matorral (MATORRAL): factor = 1.0 (base)
   - Pastizales (PASTIZAL): factor = 1.0 (base)
   - Humedales (HUMEDAL): factor = 1.0
   - Roca (ROCA): factor = 1.6
   - Agua (AGUA): factor = 3.0 (muy difícil de atravesar)
   - Ribera (RIBERA): factor = 1.0
   - Nieve (NIEVE): factor = 1.0 (asumimos tráfico sobre nieve compactada)
   - Antropogénico (ANTROPICO): factor = 1.2

#### Fórmula Final
```
cost_a_star = factor_pendiente × (1.0 + snow_cover) × factor_habitat
```

### Integración con el TerrainGrid

El `TerrainGrid` mantiene los costos actualizados mediante dos métodos:

1. `update_costs()`: Versión en Python puro que itera sobre todas las celdas
2. `update_costs_jit()`: Versión Numba JIT para máximo rendimiento

Ambas calculan el mismo resultado pero la versión JIT es aproximadamente 10-100x más rápida para grids grandes.

### Uso en el Movimiento de Agentes

Cuando un agente decide moverse:

1. Calcula un objetivo basado en búsqueda local de mejor ratio biomassa/costo
2. Llama a `a_star(grid, start_position, target_position, max_steps=500)`
3. Si encuentra un camino, se mueve al primer paso del camino (evita recalcular constantemente)
4. Si no encuentra camino, permanece en su posición o intenta un objetivo más cercano

## Heurística Utilizada

Nuestra implementación usa la distancia de Manhattan como heurística:
```
h(n) = |x_n - x_goal| + |y_n - y_goal|
```

Esta heurística es:
- **Admisible**: Nunca sobreestima el costo real alcanzable (optimalidad garantizada)
- **Consistente**: Satisface la condición del triángulo (eficiencia en replanificación)
- **Adecuada para grids**: Funciona bien con movimiento en 4 o 8 direcciones

Alternativamente, Podemos usar distancia euclidiana al cuadrado para mejor rendimiento en algunos casos, aunque Manhattan es suficiente para nuestros propósitos.

## Optimizaciones de Rendimiento

### Almacenamiento de Costos Precalculados
En lugar de recalcular el costo de movement cada vez que se evalúa un vecino, almacenamos `cost_a_star` en cada celda y lo actualizamos periódicamente cuando cambian las condiciones ambientales (nieve, principalmente).

### Actualización JIT de Costos
La función `update_costs_jit` en `src/sim/grid.py` utiliza Numba para paralelizar efectivamente el cálculo:
```python
@njit(cache=True)
def update_costs_jit(
    cost_a_star,
    slope_deg,
    snow_cover,
    habitat_type,
    width: int,
    height: int,
):
    """Numba JIT: update pathfinding costs for all cells."""
    for y in range(height):
        for x in range(width):
            # Cálculo idéntico a la versión Python pero compilado a máquina
            # ...
```

### Límite de Exploración
El parámetro `max_steps=500` en la llamada a A* previene que el algoritmo consuma excesivo tiempo en grids muy grandes o cuando el objetivo es inalcanzable. Este valor equilibra calidad de camino con rendimiento.

## Integración con la Toma de Decisiones de Agentes

### Función look_for_best_cell

Los agentes no se mueven hacia ubicaciones aleatorias, sino que evalúan opciones locales usando:

```python
def look_for_best_cell(self, grid: TerrainGrid, radius: int = 5) -> tuple[int, int]:
    best_score = -1.0
    best_pos = (self.state.x, self.state.y)
    cx, cy = self.state.x, self.state.y
    
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx, ny = cx + dx, cy + dy
            if not grid.in_bounds(nx, ny):
                continue
                
            cell = grid.cells[ny][nx]
            # Función de puntuación: valor de recurso dividido por costo de acceso
            score = (cell.total_plant_biomass + cell.total_invert_biomass * 2.0) / max(cell.cost_a_star, 0.1)
            
            if score > best_score:
                best_score = score
                best_pos = (nx, ny)
                
    return best_pos
```

### Lógica detrás de la Función de Puntuación
- **Numerador**: `(biomassa_vegetal + 2.0 * biomassa_invertebrado)`
  - Las plantas contribuyen directamente al valor
  - Los invertebrados tienen peso doble debido a su mayor densidad energética y proteína
- **Denominador**: `max(cell.cost_a_star, 0.1)`
  - Normaliza por el costo de acceso (evita división por cero)
  - Valores altos de cost_a_star reducen la puntuación (menos atractivo)
- El agente se mueve hacia la celda con la máxima puntuación dentro del radio especificado

## Manejo de Casos Especiales

### Objetivos Inalcanzables
Cuando A* no encuentra un camino (devuelve lista vacía):
- El agente permanece en su posición actual
- En el próximo ciclo, intentará una nueva evaluación local
- Esto puede ocurrir cuando el objetivo está completamente rodeado de agua u otros obstáculos infranqueables

### Movimiento Diagonal
El algoritmo soporta movimiento en 8 direcciones (incluyendo diagonales) cuando se encuentra disponible:
- Esto proporciona movimientos más naturales y eficientes en terrenos abiertos
- El costo de movimiento diagonal se calcula correctamente considerando los factores de la celda destino

### Límite de Pasos y Eficiencia
Para distancias muy largas, el agente podría necesitar múltiples turnos de simulación para llegar al destino:
- En cada paso, recalcula el objetivo local basado en condiciones actuales
- Este enfoque "greedy" con re-planificación frecuente se adapta mejor a ambientes dinámicos
- Evita compromisos con caminos que puedan volverse subóptimos debido a cambios en nieve o vegetación

## Validación y Características de Rendimiento

### Complejidad Computacional
- **Caso peor**: O(branching_factor^depth) pero típicamente mucho mejor gracias a la heurística
- **Práctico**: Para grids de hasta 1000x1000 con heurística admisible, generalmente explora una fracción mínima del espacio de búsqueda
- **Con JIT**: Capable de procesar miles de llamadas A* por segundo en hardware moderno

### Calidad de Caminos Encontrados
- **Optimalidad**: Garantizado cuando la heurística es admisible (como en nuestro caso)
- **Suavidad**: Los caminos tienden a seguir líneas de menor resistencia natural
- **Adaptación al Terreno**: Evitan naturalmente áreas de alta pendiente, nieve profunda y cuerpos de agua cuando existen alternativas

### Escalabilidad
El sistema escala bien con:
- Número de agentes (cada agente ejecuta A* independientemente)
- Tamaño del grid (gracias a la heurística y límite de pasos)
- Frecuencia de re-planificación (ajustable según necesidades de realismo vs rendimiento)

## Integración con Factores Ambientales Dinámicos

### Efecto de la Nieve
La cobertura de nieve se actualiza daily mediante `update_snow_jit` basada en:
- Elevación de la celda
- Línea de nieve que varía estacionalmente (modelo cosenoidal)
- Esto causa que los costos de pathfinding cambien naturalmente con las estaciones:
  - Verano: Línea de nieve alta, solo afecta zonas alpinas superiores
  - Invierno: Línea de nieve baja, aumenta costos en montañia y subalanía

### Cambios Estacionales de Vegetación
Aunque no actualmente modelado en el costo de movement, futuras extensiones podrían considerar:
- Mayor dificultad de movimiento en vegetación densa (primavera/verano)
- Cambios en accesibilidad debido a crecimiento estacional de plantas

## Limitaciones y Suposiciones

### Suposiciones Actuales
1. **Terreno Estático**: Asumimos que las propiedades básicas del terreno (pendiente, hábitat) no cambian durante la simulación
2. **Costos Homogéneos por Celda**: No modelamos variabilidad subcelular en dificultad de movimiento
3. **Transito Uniforme**: Asumimos que todos los agentes tienen la misma capacidad de movimiento relativa (no diferenciamos por tipo de locomoción)
4. **Planeación Instantánea**: Asumimos cálculo y ejecución inmediata del camino (no hay retraso cognitivo)
5. **Memoria de Camino Nula**: No recordamos caminos previamente calculados (re-calculamos cada vez que es necesario)

### Mejoras Futuras
1. **Costos Específicos por Especie**: Diferentes habilidades de movimiento según morfología (ungulados vs carnívoros vs aves)
2. **Memoria Espacial de Rutas**: Almacenamiento de caminos frecuentemente usados para reducir recomputation
3. **Consideración de Predicción de Riesgo**: Evitar áreas con alta densidad de depredadores conocida
4. **Integración con Sistemas Sociales**: Seguimiento de miembros de manada, comportamiento de línea
5. **Modelo de Fatiga**: Acumulación de costo de movimiento que afecta capacidad futura
6. **Terreno Dinámico**: Erosión, acumulación de sedimentos, cambios de vegetation que afecten movimiento

## Ejemplo Práctico de Uso

Consideremos un Isard (Rupicapra pyrenaica) en una celda con poca biomassa que quiere moverse a un área de mejor pasto:

1. **Evaluación Local**: `look_for_best_cell()` examina las celdas vecinas (radio=5)
2. **Selección de Objetivo**: Elige la celda con mejor ratio (biomassa / costo de acceso)
3. **Cálculo de Camino**: Llama a `a_star(current_pos, selected_goal, max_steps=500)`
4. **Ejecución de Movimiento**: Se mueve al primer paso del camino retornado
5. **Repetición**: En el próximo ciclo horario, vuelve a evaluar basado en condiciones actualizadas

Este proceso resulta en movimientos que parecen seguir valles naturales, evitar pendientes innecesariamente empinadas, y aprovechar pasos de montaña cuando están disponibles, todo mientras busca optimizar la ingesta neta de energía (beneficio de forageo menos costo de movimiento).

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*