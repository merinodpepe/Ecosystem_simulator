# Sistema Energético Detallado - Ley de Kleiber y Costos MET

## Fundamentos Teóricos

El sistema energético del simulador se basa en principios ecológicos bien establecidos:

### Ley de Kleiber para Metabolismo Basal

La tasa metabólica basal (BMR) se calcula usando la ecuación de Kleiber:
```
BMR = 70.0 × masa_kg^0.75 kcal/día
```

Esta relación alométrica describe cómo el metabolismo basal escala con la masa corporal entre especies, desde pequeños mamíferos hasta grandes ungulados. El exponente 0.75 refleja la eficiencia de los sistemas de distribución de nutrientes en organismos multicelulares.

### Equivalentes Metabólicos (MET)

Las actividades específicas se expresan como múltiplos del BMR usando MET (Metabolic Equivalent of Task):
- 1 MET = tasa de consumo de energía en reposo
- Un actividad de 3 MET consume 3 veces la energía que en reposo
- Los valores MET provienen de la literatura de fisiología del ejercicio aplicada a mamíferos salvajes

## Implementación en el Código

### Clase EnergyBudget

```python
@dataclass
class EnergyBudget:
    mass_kg: float
    bmr_kcal_day: float = 0.0      # Metabolismo basal diario
    dee_kcal_day: float = 0.0      # Gasto energético diario estimado
    intake_kcal_day: float = 0.0   # Energía ingerida diariamente
    energy_reserve_kcal: float = 0.0 # Reserva de energía (grasa corporal)
    energy_deficit_kcal: float = 0.0 # Déficit energético acumulado

    def __post_init__(self):
        self.bmr_kcal_day = bmr_kcal_day(self.mass_kg)
        self.dee_kcal_day = self.bmr_kcal_day * 2.5  # Valor típico para mamíferos activos
        self.energy_reserve_kcal = self.mass_kg * 5000.0  # ~5000 kcal/kg de grasa
```

### Funciones de Cálculo Energético (Numba JIT)

Todas las funciones críticas están decoradas con `@njit(cache=True)` para compilación Just-In-Time:

```python
@njit(cache=True)
def bmr_kcal_day(mass_kg: float) -> float:
    """Basal Metabolic Rate in kcal/day (Kleiber's law)."""
    return 70.0 * (mass_kg**0.75)

@njit(cache=True)
def activity_kcal_h(mass_kg: float, met: float) -> float:
    """Energy cost of an activity in kcal/hour (MET × BMR_hourly)."""
    return met * bmr_kcal_h(mass_kg)
```

### Cálculo de Gasto Energético Diario (DEE)

La función `daily_dee` computes elgasto energético total basado en el presupuesto de tiempo:

```python
@njit(cache=True)
def daily_dee(
    mass_kg: float,
    hours_foraging: float = 6.0,
    hours_locomotion: float = 2.0,
    hours_resting: float = 12.0,
    hours_other: float = 4.0,
    slope_avg: float = 0.0,
    is_cold: bool = False,
    is_lactating: bool = False,
) -> float:
    bmr_h = bmr_kcal_h(mass_kg)
    total = 0.0
    total += loco_cost_hours(mass_kg, slope_avg, hours_locomotion)
    total += activity_kcal_h(mass_kg, 2.0) * hours_foraging
    total += activity_kcal_h(mass_kg, 1.0) * hours_resting
    total += activity_kcal_h(mass_kg, 1.5) * hours_other
    if is_cold:
        total += activity_kcal_h(mass_kg, 2.0) * 2.0
    if is_lactating:
        total *= 1.4
    return total
```

### Desglose de Actividades y sus Costos MET

Definidas en `ACTIVITY_COSTS` en `src/sim/energy.py`:

| Actividad | MET | Descripción |
|-----------|-----|-------------|
| FORAGE_SEARCH | 3.0 | Búsqueda activa de alimento |
| FORAGE_INTAKE | 1.5 | Ingesta de alimento (masticación, deglución) |
| LOCO_WALK_SLOW | 2.0 | Caminata lenta |
| LOCO_WALK_MOD | 2.5 | Caminata moderada |
| LOCO_WALK_FAST | 3.0 | Caminata rápida |
| LOCO_TROT | 4.5 | Trotar (exponente de masa 0.70) |
| LOCO_GALLOP | 7.0 | Galope (exponente de masa 0.70) |
| LOCO_SWIM | 6.0 | Natación (exponente de masa 0.80) |
| LOCO_CLIMB | 5.0 | Escalada |
| VIGILANCE | 1.3 | Estado de alerta |
| REPRO_COURTSHIP | 2.5 | Comportamiento de cortejo |
| REPRO_GESTATION | 1.3 | Gestación |
| REPRO_LACTATION | 3.0 | Lactancia |
| TERMO_SHIVERING | 2.0 | Termoregulación por temblor |
| TERMO_PANTING | 1.5 | Termoregulación por jadeo |
| RESTING | 1.0 | Reposo |
| GROOMING | 1.5 | Acicalamiento |
| SOCIAL_INTERACTION | 1.8 | Interacción social |

## Integración con el Comportamiento de los Agentes

### Actualización de Energía en Agent.step()

En `src/sim/agents/base.py`, el método `_update_energy` calcula el gasto energético diario:

```python
def _update_energy(self, grid: TerrainGrid, dt_hours: float) -> None:
    cell = grid.cells[self.state.y][self.state.x]
    slope = cell.slope_deg

    # Presupuesto de tiempo típico (horas)
    hours_loco = 2.0
    hours_forage = 6.0
    hours_rest = 12.0
    hours_other = 4.0

    # Gasto energético diario usando la función JIT
    expended = daily_dee(
        self.mass_kg,
        hours_forage,
        hours_loco,
        hours_rest,
        hours_other,
        slope,
        is_cold=False,
        is_lactating=self.state.is_lactating,
    )
    self.state.calories_spent_today = expended
    self.state.energy_kcal -= expended * (dt_hours / 24.0)  # Proporcional al fracción de día
```

### Adquisición de Energía mediante Forrajeo

Los agentes obtienen energía através del método `forage_on_cell`:

```python
def forage_on_cell(self, grid: TerrainGrid) -> float:
    cell = grid.cells[self.state.y][self.state.x]
    available = cell.total_plant_biomass + cell.total_invert_biomass
    intake = min(available, self.mass_kg * 0.05)  # Máximo 5% de masa corporal
    
    # Distribución proporcional de consumo
    plant_share = cell.total_plant_biomass / max(available, 1e-6)
    invert_share = 1.0 - plant_share
    
    # Reducción de biomassa en la celda
    cell.biomass_P1 -= intake * plant_share * 0.5
    cell.biomass_P2 -= intake * plant_share * 0.2
    cell.biomass_P3 -= intake * plant_share * 0.3
    cell.biomass_I1 -= intake * invert_share * 0.3
    cell.biomass_I2 -= intake * invert_share * 0.5
    cell.biomass_I3 -= intake * invert_share * 0.2
    
    return intake
```

La biomassa consumida se convierte en energía usando factores de conversión específicos:
- Plantas: 800 kcal/kg
- Carne: 1500 kcal/kg
- Invertebrados: 2000 kcal/kg (mayor densidad energética)

## Factores Modificadores del Gasto Energético

### Efecto de la Pendiente

La función `loco_cost_hours` ajusta el costo de locomoción basado en la pendiente:

```python
@njit(cache=True)
def loco_cost_hours(mass_kg: float, slope_deg: float, hours: float) -> float:
    if slope_deg < 5.0:
        met = 2.5  # Terreno llano
    elif slope_deg < 15.0:
        met = 3.0  - Pendiente suave
    elif slope_deg < 30.0:
        met = 5.0  - Pendiente moderada
    else:
        met = 6.0  - Pendiente empinada
    return activity_kcal_h(mass_kg, met) * hours
```

### Efecto de la Temperatura y Lactancia

- **Condiciones de frío**: Añade costo adicional equivalente a 2 horas de termoregulación por temblor
- **Lactancia**: Multiplica el gasto energético total por 1.4 (40% de aumento)

## Reservas y Déficits Energéticos

El modelo trackea dos componentes críticos del balance energético:

### Reserva de Energía (`energy_reserve_kcal`)
- Representa las reservas de grasa corporal
- Inicializada como masa_kg × 5000 kcal/kg (aprox. 0.5 kg de grasa por kg de masa corporal)
- Aumenta con el superávit energético (ingesta - gasto)
- Disminuye con el déficit energético
- Cuando llega a cero, el agente comienza a usar tejido muscular (no modelado explícitamente)
- Si llega a negativo significativo, conduce a la muerte

### Déficit Energético Acumulado (`energy_deficit_kcal`)
- Trackea la magnitud del déficit cuando las reservas están agotadas
- Se utiliza para modelos más sofisticados de pérdida de condición física
- En la implementación actual, principalmente sirve para diagnóstico

## Validación y Calibración

El sistema energético ha sido validado contra:

1. **Estudios de Nagy (2005)**: Comparación de DEE predicho vs medido en mamíferos salvajes
2. **Datos de PANTHERIA**: Escalado alométrico entre especies
3. **Mediciones de campo específicas del PNAP**: Cuando están disponibles

Los archivos de validación se encuentran en:
- `ecosystem/data/validacion/validacion_energia.tsv`
- `ecosystem/data/validacion/validacion_energia.png`
- `ecosystem/wiki/validacion_energia.md`

## Aplicaciones Prácticas en la Simulación

El sistema energético afecta múltiples aspectos del comportamiento agente:

### Supervivencia
- Agentes mueren cuando `energy_kcal <= 0.0`
- Umbral de hambre que puede modificar comportamiento de riesgo

### Reproducción
- Requiere energía mínima para iniciar gestación (`mass_kg * 2000.0 kcal`)
- La lactancia aumenta significativamente el gasto energético
- Condición corporal afecta éxito reproductivo y supervivencia de crías

### Movimiento y Selección de Hábitat
- Los costos de movement influyen en las decisiones de pathfinding
- Agentes prefieren rutas que minimicen gasto energético por unidad de biomassa ganada
- Selección de hábitat basada en ratio biomassa-disponible/costo-de-acceso

### Respuesta Estacional
- Variaciones en disponibilidad de biomassa afectan el balance energético
- Costos adicionales de termoregulación en invierno
- Aumento de requerimientos durante lactancia (primavera/verano)

## Limitaciones y Suposiciones

### Suposiciones Actuales
1. **Eficiencia de Digestión Constante**: 60% para todos los tipos de alimento
2. **Densidad Energética Fija**: Valores promedio por tipo de tejido (no específico por especie)
3. **Presupuesto de Tiempo Estático**: Asignación fija de horas a actividades (no dinámica según condiciones)
4. **Adaptación Térmica Simplificada**: Efectos de frío/calor modelados como modificadores binarios
5. **No hay Adaptación Metabólica**: El BMR no cambia con la condición corporal o acclimatación a largo plazo

### Mejoras Futuras
1. **Modelo de Condición Corporal**: Seguimiento explícito de reservas de grasa vs proteína
2. **Digestión Específica por Tipo de Alimento**: Diferentes eficiencias para plantas, carne, invertebrados
3. **Presupuesto de Tiempo Dinámico**: Adjuste asignación de horas basado en factores ambientales y estado interno
4. **Acclimatación Térmica**: Adaptación estacional a temperaturas extremas
5. **Costos de Caza**: Modelo más detallado del gasto energético en perseguición y captura de presas
6. **Energía de Crecimiento**: Asignación explícita de energía para crecimiento tisular en jóvenes

## Relación con Otros Sistemas

### Interacción con el Sistema de Terreno
- La pendiente afecta directamente los costos de locomoción
- La cobertura de nieve aumenta el costo de movement (factor `1.0 + snow_cover`)
- El tipo de hábitat modifica la dificultad de movimiento (bosque = 1.3x, roca = 1.6x, agua = 3.0x)

### Interacción con el Sistema de Biomassa
- La disponibilidad de biomassa local determina el potencial de ingesta energética
- Los agentes modifican el paysage consumiendo biomassa de las celdas
- El crecimiento de biomassa depende de factores ambientales (no actualmente modelado en detalle)

### Interacción con el Sistema Reproductivo
- La gestación y lactancia son estados que modifican significativamente el gasto energético
- La energía disponible determina la capacidad para invertir en reproducción vs mantenimiento

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*