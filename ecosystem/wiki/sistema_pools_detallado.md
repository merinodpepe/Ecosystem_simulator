# Sistema de Pools de Biomassa - Modelado de Organismos No-Agentizados

## Visión General

El sistema de pools en el simulador del Parc Natural de l'Alt Pirineu representa grupos de organismos que, debido a su pequeño tamaño, alta abundancia o características específicas, no se modelan como agentes individuales. En su lugar, se agrupan en "pools" que trackean su biomassa total como un recurso escalar continuo. Este enfoque permite incluir importantes componentes tróficos del ecosistema sin el costo computacional de modelar miles o millones de individuos separados.

## Filosofía de Diseño

La decisión de qué organismos modelar como agentes individuales vs. pools se basa en:

1. **Escala Espacial y Temporal**: Organismos pequeños con ciclos de vida cortos relativo al paso de simulación (1 día)
2. **Abundancia**: Especies que ocurrirían en densidades demasiado altas para modelado individual (ej. miles por hectárea)
3. **Movilidad**: Organismos con movimento muy limitado o pasivo que no requieren toma de decisiones compleja
4. **Importancia Trófica**: Su papel como recurso energético para consumidores superiores
5. **Complejidad Conductual**: Organismos cuyo comportamiento puede adequately representarse mediante reglas simples de crecimiento y consumo

## Pools Implementados

El simulador actualmente implementa seis pools distintos, cada uno representando un grupo ecológico funcional:

### 1. Peces (Fish)
- **Especies representativas**: Truita común (*Salmo trutta*), Barbo rosco (*Barbus haasi*)
- **Hábitat**: Ríos y corrientes del Noguera Pallaresa y tributarios
- **Importancia trófica**: 
  - Consumidores secundarios (invertebrados acuáticos, algunos terrestres)
  - Presa para aves piscívoras (martín pescador, garzas, águilas)
  - Indicadores de calidad de agua
- **Dinámica**: 
  - Crecimiento basado en disponibilidad de invertebrados acuáticos
  - Consumo por aves y mamíferos piscívoros
  - Movilidad limitada principalmente al corredor ripario

### 2. Herpetofauna (Herps - Reptiles y Anfibios)
- **Especies representativas**: 
  - Anfibios: Sapito de espuelas (*Pelobates cultripes*), Rana común (*Rana temporaria*)
  - Reptiles: Lagarto verdinegro (*Lacerta schreiberi*), Víbora de Seo (*Vipera seoanei*)
- **Hábitat**: Variado, desde zonas húmedas hasta áreas rocosas y boscosas
- **Importancia trófica**:
  - Consumidores de invertebrados y pequeños vertebrados
  - Presa para aves de paso, mamíferos carnívoros y otras herps
  - Indicadores de salud de ecosistemas de transición
- **Dinámica**: 
  - Estacionalidad fuerte (hibernación/actividad)
  - Crecimiento basado en presas disponibles (invertebrados, pequeños vertebrados)
  - Consumo por aves rapaces, mamíferos y otras herps

### 3. Aves Passeriformes (Passerines)
- **Especies representativas**: 
  - Insectívoros: Mosquitero común (*Phylloscopus collybita*), Carbonero común (*Parus major*)
  - Granívoros: Pinzón vulgar (*Fringilla coelebs*), Escribano soteador (*Emberiza cia*)
- **Hábitat**: Bosques, matos, pastizales, zonas de transición
- **Importancia trófica**:
  - Consumidores primarios y secundarios (semillas, invertebrados, frutos)
  - Vectores importante de semillas (dispersión)
  - Presa para rapaces nocturnas y diurnas, mamíferos carnívoros
- **Dinámica**: 
  - Migratoria parcial/escalar dependiendo de la especie
  - Crecimiento estacional asociado a abundancia de alimento
  - Alta rotación poblacional (múltiples generaciones por año en algunas especies)

### 4. Micromamíferos (Micromammals)
- **Especies representativas**: 
  - Roedores: Topillo campesino (*Microtus arvalis*), Ratón de campo (*Apodemus sylvaticus*)
  - Insectívoros: Musaraña común (*Sorex araneus*), Topo europeo (*Talpa europaea*)
- **Hábitat**: Variado, desde bosques hasta pastizales y zonas rocosas
- **Importancia trófica**:
  - Consumidores primarios y secundarios (semillas, raíces, invertebrados)
  - Ingenieros del suelo (aeración, mezcla de nutrientes)
  - Presa crítica para una amplia gama de depredadores (aves, mamíferos, reptiles)
- **Dinámica**: 
  - Alta fecundidad y crecimiento poblacional rápido
  - Fluctuaciones poblacionales fuertes asociadas a alimento y predación
  - Ciclos de auge y caída naturales en ausencia de control depredador

### 5. Murciélagos (Bats)
- **Especies representativas**: 
  - Insectívoros: Murciélago de herradura grande (*Rhinolophus ferrumequinum*), Murciélago común (*Pipistrellus pipistrellus*)
  - Frugívoros: (menos comunes en el PNAP pero presentes en zonas de transición)
- **Hábitat**: Refugios en cuevas, edificaciones, árboles Huecos; áreas de caza abierta
- **Importancia trófica**:
  - Principales depredadores nocturnos de insectos voladores
  - Polinizadores y dispersores de semillas (especies frugívoras)
  - Indicadores de calidad de hábitats nocturnos y de cuevas
- **Dinámica**: 
  - Estacionalidad marcada (hibernación en invierno)
  - Crecimiento asociado a abundancia de insectos nocturnos
  - Baja tasa reproductiva (generalmente un hijo por año)
  - Alta longevidad relativa a su tamaño

## Implementación Técnica

### Clase PoolManager

Ubicada en `src/sim/pools.py`, gestiona todos los pools como una colección:

```python
@dataclass
class PoolManager:
    fish: FishPool = field(default_factory=FishPool)
    herps: HerpsPool = field(default_factory=HerpsPool)
    passerines: PasserinesPool = field(default_factory=PasserinesPool)
    micromammals: MicromammalsPool = field(default_factory=MicromammalsPool)
    bats: BatsPool = field(default_factory=BatsPool)
    
    def step(self, grid: TerrainGrid, season: str, snow: float) -> None:
        """Actualiza todos los pools por un día de simulación."""
        self.fish.step(grid, season, snow)
        self.herps.step(grid, season, snow)
        self.passerines.step(grid, season, snow)
        self.micromammals.step(grid, season, snow)
        self.bats.step(grid, season, snow)
```

### Clase Base de Pool

Cada pool específico hereda de una clase base común que define la interfaz:

```python
@dataclass
class BasePool:
    biomass: float = 0.0  # Biomassa total en kg
    
    def step(self, grid: TerrainGrid, season: str, snow: float) -> None:
        """Actualiza el pool por un día de simulación."""
        # Implementación específica por tipo de pool
        pass
        
    def consume(self, amount: float) -> float:
        """Consumir biomassa del pool, retornando la cantidad realmente consumida."""
        consumed = min(self.biomass, amount)
        self.biomass -= consumed
        return consumed
```

### Implementación Específica por Pool

#### FishPool
```python
def step(self, grid: TerrainGrid, season: str, snow: float) -> None:
    # Crecimiento basado en invertebrados acuáticos disponibilidad
    # Simplificado: proporcional a biomass_I3 (invertebrados depredadores/parasitoides como proxy)
    growth_rate = 0.1  # 10% crecimiento diario máximo bajo condiciones ideales
    available_prey = grid.total_invert_biomass * 0.3  # Porcion acuática estimada
    growth = growth_rate * self.biomass * min(available_prey / (self.biomass + 1e-6), 1.0)
    
    # Pérdida basal (metabolismo)
    maintenance = self.biomass * 0.03  # 3% diario
    
    # Actualización
    self.biomass += growth - maintenance
    self.biomass = max(0.0, self.biomass)  # No negativo
```

#### HerpsPool, PasserinesPool, etc.
Cada pool tiene su propia lógica de crecimiento basada en:
- Disponibilidad de presas apropiadas (invertebrados, vegetación, etc.)
- Factores estacionales (reproducción, hibernación, migración)
- Tasa metabólica específica del grupo
- Capacidad de carga ambiental implícita

## Integración con el Resto de la Simulación

### Consumo por Agentes

Los agentes consumen biomassa de los pools através de métodos especializados en sus clases:

#### En CarnivoreAgent y OmnivoreAgent
```python
def consume_from_pools(self, pools: PoolManager) -> float:
    """Obtener energía de pools apropiados según dieta."""
    total_energy = 0.0
    
    # Según la dieta del agente, consumir de pools específicos
    diet = ALL_DIETS.get(self.species_key)
    if not diet:
        return 0.0
        
    # Consumo de pescado
    if diet.fish_proportion > 0:
        fish_needed = self.mass_kg * 0.02 * diet.fish_proportion  # Ejemplo de requerimiento
        fish_consumed = pools.fish.consume(fish_needed)
        total_energy += fish_consumed * 1500.0  # kcal/kg de pescado
    
    # Consumo de herps
    if diet.vertebrate_proportion > 0:
        herps_needed = self.mass_kg * 0.015 * diet.vertebrate_proportion
        herps_consumed = pools.herps.consume(herps_needed)
        total_energy += herps_consumed * 1200.0  # kcal/kg de herps
    
    # ... similar para otros pools
    
    return total_energy
```

#### Producción y Consumo en el Paso de Pools
Durante `Simulation._step()`, los pools son actualizados:
```python
def _step(self, day: int):
    # ... actualización de entorno y nieve
    
    self.pools.step(self.grid, season, snow)  # Actualiza todos los pools
    
    # ... acciones de agentes (que pueden consumir de pools)
    
    # ... resto del paso
```

### Producción de Biomassa

Los pools generan biomassa através de procesos específicos:
- **Peces**: Crecimiento basado en invertebrados acuáticos disponible
- **Herps**: Crecimiento basado en invertebrados y pequeños vertebrados
- **Passerines**: Crecimiento basado en semillas e invertebrados estacionalmente disponibles
- **Micromamíferos**: Crecimiento rápido basado en vegetación y invertebrados
- **Murciélagos**: Crecimiento basado en insectos nocturnos disponibles

## Factores Estacionales y Ambientales

Cada pool responde differently a las condiciones estacionales:

### Estación y Fenología
- **Primavera**: Aumento de actividad reproductive y crecimiento para la mayoría
- **Verano**: Pico de actividad y crecimiento para many taxa
- **Otoño**: Preparación para invierno, acumulación de reservas
- **Invierno**: Reducción drástica de actividad (hibernación, migración, letargo)

### Factores Específicos
- **Temperatura**: Afecta tasas metabólicas y rates de crecimiento
- **Disponibilidad de Agua**: crítica para especies acuáticas y semiaquáticas
- **Cobertura de Nieve**: Afecta acceso a sitios de hibernación y foraging
- **Fotoperíodo**: Regula ciclos reproductivos y de muda

## Integración con la Red Trófica

Los pools ocupan posiciones específicas en la red trófica del ecosistema:

### Consumidores Primarios
- Algunos micromamíferos (herbívoros/granívoros)
- Algunas aves passeriformes (granívoros/frugívoros)

### Consumidores Secundarios
- La mayoría de los pools son consumidores secundarios:
  - Insectívoros (peces, herps, passerines, micromamíferos, bats)
  - Omnívoros que consumen tanto planta como animal

### Presa para Niveles Superiores
- Todos los pools son presa potencial para:
  - Agentes carnívoros y omnívoros
  - Otras pools de nivel trófico superior (ej. aves rapaces consumiendo passerines)

### Enlaces Específicos Documentados
Aunque no actualmente modelado en detalle en los pools, la red trófica completa incluye conexiones como:
- Truita → Martín pescador, Águila pescadora
- Invertebrados acuáticos → Truita, Martín pescador
- Micromamíferos → Águila real, Zorro, Gina, Martinete
- Passerines → Águila real, Búho reale, Águila culebrera
- Murciélagos → Búho reale, Gineta (ocasionalmente)

## Ventajas del Enfoque de Pools

### Eficiencia Computacional
En lugar de modelar potencialmente cientos de miles de individuos individuales, trackeamos:
- 6 variables escalares (biomassa de cada pool)
- Operaciones simples de crecimiento y consumo por paso de simulación
- Reducción de órdenes de magnitud en complejidad computacional

### Representación Adecuada de Escalas
- **Agentes individuales**: Adecuado para vertebrados grandes y medianos con territorios y comportamiento complejo
- **Pools**: Adecuado para organismos pequeños, abundantes o con comportamiento menos complejo individualmente

### Flexibilidad para Detalles Futuro
Cada pool puede ser refinado independientemente:
- Añadir estructura de edad o tamaño dentro del pool
- Modelar etapas de vida específicas (larvas, juveniles, adultos)
- Incorporar respuestas específicas a factores ambientales
- Añadir comportamiento espacial limitado (migración estacional, movimientos de refugio)

## Limitaciones y Suposiciones

### Suposiciones Actuales
1. **Homogeneidad Internal**: Asumimos que todos los individuos en un pool tienen las mismas características promedio
2. **Consumo Instantáneo**: No modelamos tiempos de búsqueda, manejo o procesamiento de alimento
3. **Respuesta Lineal al Recurso**: Crecimiento proporcional simple a disponibilidad de alimento (no funcional de respuesta tipo II o III)
4. **Sin Estructura Espacial**: Los pools se tratan como recursos globales sin distribución espacial específica
5. **Interacciones Simplificadas**: No modelamos competencia dentro del pool ni interacciones complejas entre pools
6. **Estacionalidad Promedio**: Usamos modificadores estacionales generales en lugar de respuestas específicas por especie

### Mejoras Futuras
1. **Estructura de Tamaño/Edad**: Dividir pools en clases de tamaño para mejor representar depredación selectiva
2. **Respuestas Funcionales**: Implementar curvas de respuesta tipo II o III para consumo y crecimiento
3. **Distribución Espacial**: Asignar pools a celdas específicas basado en preferencias de hábitat
4. **Modelo de Estadios de Vida**: Separar larvas, juveniles, adultos donde ecológicamente relevante
5. **Interacciones Específicas**: Modelar relaciones depredador-presa específicas entre pools y agentes
6. **Adaptación Evolutiva Simple**: Permitir cambios lentos en parámetros basado en presión selectiva (muy a largo plazo)

## Integración con el Balance Energético Global

Los pools contribuyen significativamente al flujo de energía en el ecosistema:

### Ruta Energética típica
Plantas (P1/P2/P3) → Herbívoro pools (micromamíferos, passarines) → 
Carnívoro pools (herps, bats) o Agentes carnívoros omnivoros

### Contribución al Metabolismo de la Comunidad
Aunque no directamente trackeado, los pools representan:
- Porción significativa de la respiración comunitaria total
- Importante flujo de energía hacia niveles tróficos superiores
- Componentes clave en el ciclado de nutrientes (especialmente micromamíferos en suelo)

### Indicadores de Salud del Ecosistema
Cambios en la biomassa de pools pueden indicar:
- **Declive de micromamíferos**: Posible sobrepesadeo por depredadores o pérdida de hábitat de suelo
- **Aumento repentino de passerines**: Buen año reproductivo o disminución de predación
- **Fluctuaciones de murciélagos**: Cambios en poblaciones de insectos nocturnos o calidad de refugios
- **Tendencias en peces**: Indicadores de calidad de agua y conectividad riparia

## Estadísticos y Métricas de Salida

Durante la simulación, se trackean y pueden ser exportados:
- Biomassa total de cada pool por paso de tiempo
- Flujos de consumo entre pools y agentes
- Producción neta primaria asignada a cada pathway trófico
- Eficiencia de transferencia trófica entre niveles

Estos datos son valiosos para:
- Validación contra estimaciones de campo de abundancia biomass
- Análisis de eficiencia trófica y canales de energía
- Identificación de factores limitantes en diferentes pathways
- Evaluación de impacto de cambios en especies clave (ej. introducción/eliminación de depredadores)

---
*Actualizado: 2026-06-22 basado en la revisión del código fuente*