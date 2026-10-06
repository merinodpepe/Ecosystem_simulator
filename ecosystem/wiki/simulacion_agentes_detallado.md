# Sistema de Agentes GOAP - Implementación Detallada

## Visión General del Comportamiento de Agentes

Los agentes en el simulador del Parc Natural de l'Alt Pirineu implementan una versión simplificada pero efectiva de GOAP (Goal-Oriented Action Planning). Este enfoque permite que los agentes tomen decisiones autónomas basado en su estado interno y las condiciones ambientales, sin necesidad de máquinas de estado finitas complejas.

## Arquitectura de la Clase Agent Base

### AgentState - Estado Internal del Agente

Cada agente mantiene un `AgentState` que contiene todas las variables dinámicas que cambian durante la simulación:

```python
@dataclass
class AgentState:
    x: int                                    # Posición X en el grid
    y: int                                    # Posición Y en el grid
    mass_kg: float = 50.0                     # Masa corporal (kg)
    energy_kcal: float = 0.0                  # Energía disponible (kcal)
    age_days: int = 0                         # Edad en días
    alive: bool = True                        # Estado de vida
    is_pregnant: bool = False                 # Estado de gestación
    is_lactating: bool = False                # Estado de lactancia
    gestation_days: int = 0                   # Días de gestación transcurridos
    days_since_reproduction: int = 0          # Días desde último parto
    calories_consumed_today: float = 0.0      # Calorías consumidas hoy
    calories_spent_today: float = 0.0         # Calorías gastadas hoy
```

### Agent - Clase Base

La classe `Agent` define la interfaz común para todos los tipos de agentes:

- **Propiedades identificadoras**: `agent_id`, `species_key`, `common_name`, `mass_kg`, `trophic_level`
- **Referencia al estado**: `state: AgentState`
- **Sistema energético**: `energy: EnergyBudget`
- **Parámetros específicos de especie**:
  - `home_range_radius_cells`: Radio del área de actividad
  - `daily_distance_cells`: Distancia diaria típica de movimiento
  - `speed_kmh`: Velocidad promedio
  - `gestation_days_total`: Duración total de gestación
  - `litter_size_min/max`: Tamaño de la camada
  - `reproductive_age_days`: Edad de madurez sexual
  - `lifespan_days`: Esperanza de vida máxima

## Implementación Específica por Tipo Trófico

### HerbivoreAgent

Los herbívoros implementan un comportamiento de forrajeo simple pero efectivo:

#### Toma de Decisiones (`_decide_actions`)
1. **Evaluación de necesidades de forrajeo**: Si la biomassa vegetal en la celda actual es menor al 5% de la masa corporal necesaria, buscar una celda mejor
2. **Búsqueda de destino**: Usar `look_for_best_cell()` para encontrar la celda vecina (radio=5) con mayor ratio (biomassa / costo de movimiento)
3. **Selección de acciones**:
   - Si se encontró un mejor destino: `MoveAction` hacia esa celda
   - Siempre: `ForageAction` para consumir biomassa local
   - Si las condiciones de reproducción se cumplen: `ReproduceAction`

#### Metodos Clave
- `forage_on_cell()`: Consumir biomassa de la celda actual y convertirla en energía
- `look_for_best_cell()`: Evaluar celdas vecinas usando una función de puntuación que considera biomassa y costos de movimiento
- `_should_reproduce()`: Verificar condiciones para iniciar reproducción

### CarnivoreAgent

Los carnívoros siguen un patrón similar pero adaptado para la caza:

- En lugar de forrajeo vegetal, buscan presas basándose en densidad de animales herbívoros
- Implementan comportamientos de persecución cuando detectan presas cercanas
- Su energía proviene exclusivamente del consumo de carne

### OmnivoreAgent

Los omnívores combinan ambos comportamientos:
- Pueden forrajear en vegetación cuando esté disponible
- Cazan pequeños vertebrados o consumen carroña cuando opportunity se presenta
- Tienen una dieta más flexible que les permite adaptarse mejor a variaciones estacionales

## Sistema de Acciones

Las acciones son clases ligeras que encapsulan un comportamiento específico:

### MoveAction
```python
class MoveAction:
    def __init__(self, target: tuple[int, int]):
        self.target = target
    
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        start = (agent.state.x, agent.state.y)
        path = a_star(grid, start, self.target, max_steps=500)
        if path and len(path) > 1:
            next_pos = path[1]
            agent.state.x, agent.state.y = next_pos
```
Utiliza el algoritmo A* para encontrar el caminho óptimo considerando los costos de movimiento basados en terreno, pendiente y cobertura de nieve.

### ForageAction
```python
class ForageAction:
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        intake = agent.forage_on_cell(grid)
        calory_intake = intake * 800.0  # Conversión biomassa a energía
        agent.state.calories_consumed_today += calory_intake
        agent.state.energy_kcal += calory_intake * 0.6  # Eficiencia de digestión
```
Extrae biomassa de la celda actual, la convierte en energía y la réserves al agente, considerando una eficiencia de digestión del 60%.

### ReproduceAction
```python
class ReproduceAction:
    def execute(self, agent: Agent, grid: TerrainGrid) -> None:
        if not agent.state.is_pregnant:
            agent.state.is_pregnant = True
            agent.state.gestation_days = 0
```
Simplemente inicia el proceso de gestación estableciendo las banderas apropiadas.

## Algoritmo de Pathfinding A*

La función `a_star` en `src/sim/pathfinding.py` implementa el algoritmo A* estándar con:

- **Función de costo**: Combina el costo real recorrido (g-score) con la heurística de distancia Manhattan (h-score)
- **Costos de movimiento**: Obtenidos de `cell.cost_a_star` que considera:
  - Factor base por pendiente (1.0-3.5x)
  - Factor de nieve (1.0 + cobertura de nieve)
  - Factor de tipo de hábitat (1.0-3.0x dependiendo del tipo)
- **Optimización**: Límite de pasos (max_steps=500) para evitar bucles infinitos en mapas grandes

## Funciones de Utilidad Espacial

### look_for_best_cell
Evalúa las celdas vecinas dentro de un radio especificado (por defecto 5 celdas) usando la función de puntuación:
```
puntuación = (biomassa_vegetal + 2.0 * biomassa_invertebrado) / costo_a_star
```
El factor 2.0 para invertebrados refleja su mayor valor energético relativo por unidad de masa.

### find_spawn_cells
Utilizada durante la inicialización para encontrar posiciones adecuadas para aparecer agentes basado en:
- Preferencias de hábitat específicas por especie
- Preferencias de pisos bioclimáticos específicos por especie
- Exclusión de cuerpos de agua

## Flujo de Toma de Decisiones en Detalle

Durante cada `_step()` del agente (que representa 24 horas de tiempo simulado):

1. **Verificación de vida**: Si no está vivo, retornar lista vacía de acciones
2. **Evaluación de acciones**: Llamar a `_decide_actions()` para determinar qué hacer
3. **Ejecutar acciones**: Cada acción modificará el estado del agente o el ambiente
4. **Actualización de energía**: Restar gastos metabolicos basado en actividades realizadas
5. **Actualización biológica**: Incrementar edad, días de gestación, etc.
6. **Revisión de muerte**: Verificar si la energía cayó a cero o se excedió la esperanza de vida
7. **Retornar acciones ejecutadas**: Para propósitos de registro y depuración

## Específicos por Especie

Aunque comparten la misma arquitectura, cada especie tiene parámetros únicos que afectan su comportamiento:

| Especie | Masa (kg) | Radio Hogar (celdas) | Distancia Diaria | Gestación (días) | Tamaño Camada |
|---------|-----------|---------------------|------------------|------------------|---------------|
| Isard (Rupicapra pyrenaica) | 35.0 | 8 | 5 | 150 | 1 |
| Cérvol (Cervus elaphus) | 200.0 | 15 | 5 | 240 | 1 |
| Cabirol (Capreolus capreolus) | 20.0 | 10 | 5 | 150 | 2 |
| Senglar (Sus scrofa) | 100.0 | 12 | 5 | 115 | 3-8 |
| ... | ... | ... | ... | ... | ... |

Estos parámetros se definen en `DEFAULT_POPULATIONS` en `src/sim/simulation.py`.

## Limitaciones y Simplificaciones

La implementación actual hace ciertas simplificaciones por motivos de claridad y rendimiento:

1. **GOAP Simplificado**: No implementa un planificador completo de acciones, sino reglas de decisión directas
2. **Memoria Limitada**: Los agentes no recuerdan ubicaciones de recursos pasadas (excepto attraverso la exploración local)
3. **Interacciones Sociales Simplificadas**: No se modelan jerarquías de dominio, territorios complejos o comportamientos de manada detallados
4. **Percepción Local**: Los agentes solo consideran su celda actual y vecinas inmediatas para toma de decisiones

## Extensiones Futuras para el Sistema de Agentes

1. **Memoria Espacial**: Implementar un sistema de recordatorio de ubicaciones productivas visitadas recientemente
2. **Comportamiento Social**: Jerarquías de dominio, comportamiento de manada, comunicación entre agentes
3. **Aprendizaje**: Adaptación de comportamiento basado en experiencias pasadas (refuerzo positivo/negativo)
4. **Percepción Mejorada**: Rango de detección de recursos y amenazas basado en sentidos específicos de cada especie
5. **Estados de Ánimo**: Factores de estrés, hambre, miedo que modulan la toma de decisiones
6. **Comportamientos Estacionales Específicos**: Migración, almacenamiento de food, comportamientos de celo más elaborados

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*