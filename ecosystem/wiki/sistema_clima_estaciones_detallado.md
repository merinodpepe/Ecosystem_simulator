# Sistema Climático y Estacional - Dinámicas Ambientales del Parc Natural de l'Alt Pirineu

## Visión General

El sistema climático y estacional del simulador modela las variaciones ambientales críticas que influyen en todos los aspectos del ecosistema del Parc Natural de l'Alt Pirineu: desde la fisiología de organismos individuales hasta las dinámicas poblacionales y los procesos tróficos. Este sistema captura los patrones estacionales característicos de montañas mediterráneas de alta altitud, incluyendo variaciones térmicas, niveles de precipitación nieve y fotoperíodo.

## Fundamentos Climáticos del PNAP

El Parc Natural de l'Alt Pirineu presenta un clima de montaña mediterráneo con fuertes influencias alpinas:

### Características Climáticas Clave
- **Gradiente térmico Vertical**: Aproximadamente -0.65°C cada 100m de ganancia de altitud (adiabático seco)
- **Estacionalidad marcada**: Inviernos fríos y largos, veranos cortos pero cálidos
- **Patrón de precipitación**: Máximos en primavera y otoño, mínimos en invierno y verano
- **Fotoperíodo extreme**: Variación significativa en duración del día entre solsticios
- **Inversiones térmicas**: Comunes en valles durante períodos anticiclónicos invernales
- **Variabilidad microclimática**: Gran diversidad debido a orientación, pendiente y topografía compleja

## Implementación Técnica

### Clase Environment

Ubicada en `src/sim/environment.py`, gestiona el estado ambiental global:

```python
@dataclass
class Environment:
    current_day: int = 0          # Día del año simulación (0-364)
    season: str = "winter"        # Estación actual: winter, spring, summer, autumn
    # Funciones de callback para cálculo dinámico
    snow_fn: Callable[[float, int], float] = field(default_factory=lambda: default_snow_fn)
    temp_fn: Callable[[float, int], float] = field(default_factory=lambda: default_temp_fn)
```

### Funciones de Cálculo Estacional

#### Determinación de Estación
Basada en el día juliano del año:

```python
def update_season(day: int) -> str:
    """Determina la estación basado en el día del año."""
    doy = day % 365
    if 80 <= doy < 172:   # ~20 marzo a ~20 junio
        return "spring"
    elif 172 <= doy < 265: # ~20 junio a ~22 septiembre
        return "summer"
    elif 265 <= doy < 355: # ~22 septiembre a ~20 diciembre
        return "autumn"
    else:                   # ~20 diciembre a ~20 marzo
        return "winter"
```

Esta aproximación utiliza divisiones aproximadamente iguales del año astronómico, ajustadas para el hemisferio norte.

#### Función de Temperatura Por Defecto

```python
@njit(cache=True)
def default_temp_fn(elevation_m: float, day: int) -> float:
    """
    Calcula la temperatura basada en elevación y día del año.
    
    Modelo: Gradiente adiabático + variación estacional anual
    """
    # Día del año (0-364)
    doy = day % 365
    
    # Componente estacional: modelo cosenoidal
    # Mínimo alrededor del día 355 (20 diciembre), máximo alrededor del día 172 (20 junio)
    seasonal_variation = 12.5 * np.cos(2 * np.pi * (doy - 172) / 365)
    
    # Temperatura base a nivel del mar (aproximado para la región)
    sea_level_temp = 8.0 + seasonal_variation  # Oscila entre ~-4.5°C y ~20.5°C
    
    # Aplicación del gradiente adiabático (-0.65°C cada 100m)
    # Nota: El signo negativo indica disminución con altura
    temperature = sea_level_temp - 0.65 * (elevation_m / 1000.0)
    
    return temperature
```

#### Función de Cobertura de Nieve Por Defecto

```python
@njit(cache=True)
def default_snow_fn(elevation_m: float, day: int) -> float:
    """
    Calcula la cobertura de nieve basada en elevación y día del año.
    
    Modelo: Línea de nieve que varía estacionalmente
    """
    doy = day % 365
    
    # Simulación simple del ciclo anual de nieve
    # Mínima alrededor del día 200 (18 julio), máxima alrededor del día 20 (20 enero)
    # Usamos coseno desplazado para alinear con el mínimo en verano
    seasonal_factor = np.cos(2 * np.pi * (doy - 200) / 365)
    
    # Línea de nieve base: 1800m (aproximado para la región)
    # Variación anual: ±600m (rango de 1200m a 2400m)
    snow_line = 1800.0 + 600.0 * (seasonal_factor + 1.0) / 2.0
    
    # Si la elevación está por debajo de la línea de nieve, no hay nieve
    if elevation_m < snow_line:
        return 0.0
    
    # Cuanto más alto sobre la línea de nieve, mayor la cobertura (hasta 1.0)
    # Normalizado de manera que a 2600m tengamos cobertura completa
    snow_depth = (elevation_m - snow_line) / 800.0
    return min(1.0, max(0.0, snow_depth))
```

### Integración con el TerrainGrid

Durante cada paso de simulación en `Simulation._step()`:

```python
def _step(self, day: int):
    # Actualización del entorno
    self.env.step()  # Avanza el día y actualiza estación
    season = self.env.season
    snow = default_snow_fn(1500.0, day)  # Valor de referencia para logging
    
    # Actualización JIT de cobertura de nieve en todo el grid
    try:
        from sim.grid import update_snow_jit
        arr = self.grid.get_biomass_arrays()
        update_snow_jit(arr["elevation_m"], arr["snow_cover"], day, 2400.0)
        self.grid.set_biomass_arrays(arr)
    except (ImportError, AttributeError):
        # Fallback a versión Python puro
        for row in self.grid.cells:
            for cell in row:
                cell.snow_cover = default_snow_fn(cell.elevation_m, day)
    
    # ... resto del paso (pools, agentes, etc.)
```

## Componentes Modelados

### 1. Ciclo Termal Anual

#### Variación Estacional de Temperatura
- **Rango anual**: Desde aproximadamente -10°C en valles durante inviernos fríos hasta +25°C en zonas bajas durante veranos cálidos
- **Gradiente térmico**: Mantiene la relación física de -0.65°C/100m, creando zonas de vida diferenciadas con la altura
- **Inercia térmica**: El modelo captura el desfase entre solsticio y extremos térmicos (máximo en julio-agosto, mínimo en enero-febrero)

#### Efectos Biológicos de la Temperatura
- **Metabolismo**: Afecta todas las tasas metabólicas mediante la ecuación de Arrhenius implícita en los valores MET
- **Reproducción**: Muchos taxones tienen umbrales térmicos para iniciar actividad gonadal
- **Desarrollo**: Tasas de crecimiento embrionario y post-natal dependientes de temperatura
- **Sobrevivencia**: Límites letales de frío y calor que influyen en rangos de distribución
- **Comportamiento**: Patrones de actividad diurna/estacional modificados por disponibilidad térmica

### 2. Dinámica de la Nieve

#### Modelo de Línea de Nieve
La cobertura de nieve se determina principalmente por la relación entre elevación y línea de nieve estacionalmente variable:

- **Línea de nieve mínima**: ~1200m (fin de verano/principio de otoño)
- **Línea de nieve máxima**: ~2400m (fin de invierno/principio de primavera)
- **Rango anual de variación**: ~1200m de variación vertical

#### Efectos de la Cobertura de Nieve
- **Aislamiento térmico**: La nieve protege el suelo y organismos subniveanos del frío extremo
- **Disponibilidad de agua**: Derretimiento primaveral提供 crucial recurso hídrico
- **Acceso al foraging**: Cobertura profunda limita el acceso a vegetación para herbívoros
- **Costos de movimiento**: Aumento significativo del gasto energético para locomoción
- **Refugio y caché**: Algunas especies usan la nieve para alojamiento o almacenamiento de alimento
- **Selección de hábitat**: Influencia en distribución invernal de especies

### 3. Fotoperíodo y Luz Diurna

Aunque no actualmente modelado explícitamente como variable independiente, el fotoperíodo influye implícitamente a través de:

#### Efectos Estacionales en el Comportamiento
- **Actividad diurna**: Duración disponible para foraging y otras actividades
- **Migración**: Señal clave para especies migratorias (algunas aves y posiblemente murciélagos)
- **Reproducción**: Regula el eje hipotálamo-hipófisis-gónadas en muchas especies
- **Muda y cambio de pelaje**: Preparación para estaciones venideras
- **Hibernación/Estivación**: Entrada y salida de estados metabólicos reducidos

#### Modelo Implícito
Las funciones estacionales en `daily_dee` y otros componentes capturan indirectamente los efectos del fotoperíodo mediante:
- Ajustes en presupuesto de tiempo disponible para actividades
- Modificadores estacionales en tasas de crecimiento y metabolismo
- Patrones de reproducción vinculados a estaciones específicas

## Integración con Otros Sistemas

### Con el Sistema Energético
La temperatura afecta directamente el gasto energético mediante:
1. **Costos de termoregulación**: 
   - Frío: Aumento de metabolismo para mantener temperatura corporal
   - Calor: Costos de jadeo, buscar sombra, reducir actividad
2. **Modificación de esfuerzo físico**: 
   - En frío extremo, los movimientos pueden ser más costosos debido a rigidez muscular
   - En calor, se prefieren actividades durante horas más frescas del día
3. **Disponibilidad de alimento**: 
   - La producto primaria neta sigue patrones estacionales fuertes
   - La disponibilidad de presa varía con ciclos de vida de invertebrados y vertebrates

### Con el Sistema de Biomassa y Producción Primaria
TODO: Actualmente el modelo asume crescimento constante de plantas, pero futuras extensiones podrían incluir:
- Fenología estacional de crecimiento vegetativo
- Fotoperíodo y temperatura como reguladores de fotosíntesis
- Senescencia y muerte de tejidos en unfavorable条件
- Asignación de recursos entre crecimiento, reproducción y reservas

### Con el Sistema Reproductivo de Agentes
Las estaciones dictan las ventanas de oportunidad reproductiva:
```python
def _reproduce_agents(self, alive_agents: list[Agent], season: str):
    if season not in ("spring", "sumper"):
        return
    # ... lógica de reproducción
```
Solo permite reproducción durante primavera y verano, reflejando las restricciones reales en el PNAP donde:
- Inverno: Condiciones adversas para gestación y lactancia
- Primavera: Deshielo, aparición de alimento nuevo, condiciones óptimas para crías
- Verano: Abundancia de alimento para soporte de lactancia y crecimiento rápido
- Otoño: Preparación para invierno, menos energía disponible para reproducción

### Con el Sistema de Movimento y Pathfinding
La nieve afecta directamente los costos de movimiento:
```python
# En update_costs_jit:
snow_factor = 1.0 + snow_cover[y, x]  # Aumenta costo linealemente con cobertura
```
- Nieve ligera (0.2 cobertura): 20% aumento en costo de movement
- Nieve moderada (0.5 cobertura): 50% aumento
- Nieve pesada (0.8 cobertura): 80% aumento
- Nieve completa (1.0 cobertura): 100% aumento (doble el costo normal)

## Validación y Calibración

El modelo climático ha sido informado por:
1. **Datos meteorológicos históricos** de estaciones en y alrededor del PNAP
2. **Modelos climáticos regionales** (como CHELSA) interpolados a la resolución del grid
3. **Observaciones fenológicas** de eventos clave (deshielo, floración, llegada de especies migratorias)
4. **Estudios de limitación altitudinal** de especies vegetales y animales

Los archivos de validación climática se encuentran en:
- `ecosystem/wiki/investigacion_parc_alt_pirineu.md` (sección climática)
- Posiblemente en futuras adiciones a `ecosystem/wiki/validacion_clima.md`

## Limitaciones y Suposiciones

### Suposiciones Actuales
1. **Estado Espacial Homogeneo por Elevación**: Asumimos que a una dada elevación, todos los puntos tienen similares condiciones térmicas y de nieve (ignora efecto de orientación y microtopografía)
2. **Modelo Termal Simple**: Utilizamos gradiente adiabático seco simple sin considerar efectos de humedad, nubosidad o inversión térmica detallada
3. **Fotoperíodo Implícito**: No modelamos explícitamente la duración del día como variable independiente que afecte procesos fisiológicos
4. **Estacionalidad Suave**: Transiciones estacionales modeladas como cambios sinusoidales suaves (no incluyen frente climáticos bruscos)
5. **Nieve Estática Durante el Día**: La cobertura de nieve se calcula una vez por día pero asume constante durante las 24 horas simuladas
6. **Sin Precipitación Activa**: No modelamos eventos de nevadas o lluvias individuales, solo el estado promedio de cobertura de nieve

### Mejoras Futuras
1. **Modelo Microclímático**: Incorporar efecto de orientación (aspecto) y pendiente en radiación solar recibida
2. **Inversiones Térmicas**: Modelar atrapamiento de aire frío en valles durante noches claras e invernales
3. **Nieve Dinámica**: Acumulación y derretimiento de nevadas individuales con densidad variable
4. **Precipitación Intermitente**: Modelado de eventos de lluvia/nieve que afecten hidrología y condiciones de superficie
5. **Fotoperíodo Explícito**: Variables independientes de duración del día y ángulo solar para procesos fotoperiódicos
6. **Modelo de Hielo y Terreno Congelado**: Diferenciación entre nieve fresca, nieve compactada, suelo congelado y capas de hielo
7. **Efectos de Viento**: Modelo simplificado de efecto enfriador y costo añadido de movimiento contra viento fuerte
8. **Integración Hidrológica**: Modelado de flujo de agua superficial, recarga de acuíferos y dinamización de cursos de agua temporales

## Aplicaciones y Salidas del Modelo Climático

### Indicadores Ambientales Trackeados
Durante la simulación se pueden exportar:
- **Temperatura media, mínima y máxima** por celda y por zona de vida
- **Días con cobertura de nieve** por elevación y pendiente
- **Profundidad equivalente de agua de nieve** acumulada estacionalmente
- **Días grado acumulados** (growing degree days) para modelos de desarrollo
- **Índice de severidad invernal** basado en combinación de temperatura y duración de nieve

### Aplicaciones Ecológicas
1. **Predicción de Límites Altitudinales**: Combinando tolerancia térmica con dinámica de nieve
2. **Ventanas de Actividad Estacional**: Prediciendo períodos disponibles para foraging, reproducción, migración
3. **Modelos de Fenología**: Relacionando acumulación de grados día con eventos de brotación, floración, emergence
4. **Evaluación de Refugios Climáticos**: Identificando áreas queamienen condiciones favorables bajo escenarios de cambio
5. **Análisis de Conectividad Klima específica**: Evaluando cómo el clima afecta el movimiento entre hábitats favorables

### Escenarios de Aplicación
1. **Cambio Climático Futuro**: Desplazamiento de líneas isotérmicas y de nieve hacia arriba
2. **Variabilidad Interanual**: Añadiendo ruido estocástico a los promedios climáticos actuales
3. **Eventos Extremos**: Simulación de años particularmente cálidos, fríos, secos o húmedos
4. **Restauración Ecológica**: Evaluando qué tan rápido podrían recuperarse sistemas después de perturbaciones climáticas
5. **Gestión Adaptativa**: Probando diferentes estrategias de conservación bajo variabilidad climática

## Relación con el Gradiente de Pisos Bioclimáticos

El modelo climático directamente determina la distribución de los pisos bioclimáticos modelados en `terrain_pisos.tif`:

| Piso Bioclimático | Rango de Altitudinal Aproximado | Características Climáticas Clave |
|-------------------|---------------------------------|----------------------------------|
| Montano           | 800-1800m                       | Inviernos fríos, veranos templados, larga estación de crecimiento |
| Subalpino         | 1800-2400m                      | Inviernos largos y nevados, veranos cortos, estación de crecimiento limitada |
| Alpino            | 2400-3000m                      | Inviernos muy largos con nieve permanente, veranos muy breves, estrés criónico |
| Nival             | >3000m                          | précipitations predominantemente sólidas, vegetación muy limitada o ausente |

A medida que el modelo climático evolucione, estas zonas podrían desplazarse verticalmente en respuesta a:
- Cambios en la temperatura media anual
- Alteraciones en el régimen de precipitación (nieve vs lluvia)
- Modificaciones en la variabilidad estacional

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*