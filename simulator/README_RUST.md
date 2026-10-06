# Ecosystem Simulator — Rust Port

## Visión general

Port a Rust del simulador de ecosistemas del Parc Natural de l'Alt Pirineu (PNAP).

**⚠️ NOTA: Este documento está parcialmente desactualizado.** El simulador ha implementado
la mayoría de las funcionalidades que aquí se marcan como pendientes. Los cambios principales
incluyen: forrajeo basado en dieta, depredación agente-a-agente, carroñeo, pools conectados,
temperatura conectada, crecimiento logístico, parámetros especie-específicos, paralelización
con Rayon, output enriquecido, variación individual (peso/género/edad), y comportamiento
estocástico. Ver secciones marcadas con **[ACTUALIZADO]**.

---

## 1. Grid y terreno

### Estructura

El grid es una matriz 2D plana almacenada en orden row-major (`Vec<Cell>` indexado como `y × width + x`).
Cada celda representa una parcela de **25 × 25 m = 625 m²** del terreno real.

| Campo | Tipo | Descripción | Default |
|-------|------|-------------|---------|
| `elevation_m` | `f64` | Elevación en metros sobre el nivel del mar | 0.0 |
| `slope_deg` | `f64` | Pendiente en grados (0–90) | 0.0 |
| `aspect_deg` | `f64` | Orientación de la ladera (0–360) | 0.0 |
| `tri` | `f64` | Terrain Ruggedness Index (RMS del desnivel con 8 vecinos) | 0.0 |
| `piso_bioclimatico` | `u8` | Piso bioclimático: 1=Montano, 2=Subalpino, 3=Alpino, 4=Nival | 1 |
| `habitat_type` | `u8` | Tipo de hábitat funcional (1–10) | 4 (PASTIZAL) |
| `snow_cover` | `f64` | Cobertura de nieve fraccional [0, 1] | 0.0 |
| `cost_a_star` | `f64` | Coste de atravesar la celda para pathfinding A* | 1.0 |
| `biomass_P1/P2/P3` | `f64` | Biomasa de plantas en kg/celda | 0.0 |
| `biomass_I1/I2/I3` | `f64` | Biomasa de invertebrados en kg/celda | 0.0 |
| `P1_max/P2_max/P3_max` | `f64` | Biomasa máxima (capacidad de carga) por pool vegetal | 2.0 / 1.5 / 5.0 |
| `is_water` | `bool` | La celda es agua | false |
| `is_riparian` | `bool` | La celda es ribera | false |

### 1.1 Los 10 hábitats funcionales

Los hábitats del MCSC catalán (44 clases originales) se simplifican a 10 tipos funcionales.
Cada tipo tiene propiedades diferentes de coste de movimiento, capacidad de biomasa, y régimen de crecimiento:

| Código | Nombre | Factor terreno (A*) | Descripción ecológica |
|--------|--------|---------------------|----------------------|
| 1 | BOSQUE_CON | 1.3 | Bosque de coníferas (pino negro, abeto). Dosel denso, poca luz en sotobosque. |
| 2 | BOSQUE_CAD | 1.3 | Bosque caducifolio (roble, haya, abedul). Alta productividad en primavera-verano. |
| 3 | MATORRAL | 1.0 | Matorral subalpino (rododendro, arándano, enebro). Transición bosque-pastizal. |
| 4 | PASTIZAL | 1.0 | Pastizales alpinos y subalpinos (festuca, nardus). Alta producción de P3. |
| 5 | HUMEDAL | 1.5 | Zonas húmedas (turberas, bordes de lago). Suelo saturado, vegetación hidrófila. |
| 6 | ROCA | 1.6 | Afloramientos rocosos, pedregales, canchales. Biomasa mínima. |
| 7 | AGUA | 3.0 | Lagos, tramos de río. Sin vegetación terrestre, hábitat para peces. |
| 8 | RIBERA | 1.2 | Bosque de ribera (aliso, sauce, chopo). Alta humedad, productividad alta. |
| 9 | NIEVE | 1.0 | Neveros permanentes. Sin biomasa. |
| 10 | ANTROPICO | 1.2 | Zonas humanizadas (pueblos, carreteras, pistas de esquí). |

### 1.2 Coste de movimiento (A*)

El coste de atravesar una celda para pathfinding combina tres factores:

```
cost_a_star = slope_factor × snow_factor × terrain_factor
```

**slope_factor** — la pendiente incrementa el coste energético de locomoción:
- Pendiente < 5° (llano-suave): factor 1.0 — marcha normal
- 5°–15° (moderado): factor 1.5 — esfuerzo notable
- 15°–30° (fuerte): factor 2.5 — esfuerzo alto, requiere energía significativa
- > 30° (muy fuerte): factor 3.5 — prácticamente escalada

**snow_factor** — la nieve dificulta el movimiento:
```
snow_factor = 1.0 + snow_cover
```
Lineal desde 1.0 (sin nieve) hasta 2.0 (nieve total).

**terrain_factor** — el tipo de terreno impone su propio coste (ver tabla hábitats).
Los valores están calibrados para reflejar la dificultad relativa: agua (3.0) es el más restrictivo,
mientras que pastizal y matorral (1.0) son los más fáciles.

### 1.3 Asignación de hábitat desde piso bioclimático (TSV)

Cuando se cargan datos reales, el hábitat se deduce del piso bioclimático y la elevación:

| Piso | Condición | Hábitat asignado | Justificación ecológica |
|------|-----------|------------------|------------------------|
| Alpino (3) | elevación > 2500 m | ROCA | Por encima del límite del suelo continuo |
| Alpino (3) | elevación ≤ 2500 m | PASTIZAL | Pastos alpinos y prados de alta montaña |
| Nival (4) | cualquier | ROCA | Rocas y nieve permanente |
| Subalpino (2) | elevación < 1900 m | BOSQUE_CON | Bosque de coníferas subalpino (pino negro) |
| Subalpino (2) | elevación ≥ 1900 m | MATORRAL | Transición a matorral subalpino (rododendro) |
| Montano (1) | elevación < 1200 m | BOSQUE_CAD | Robledales y hayedos de media montaña |
| Montano (1) | elevación ≥ 1200 m | BOSQUE_CON | Bosque mixto de coníferas montano |

---

## 2. Cobertura de nieve (modelo estacional)

Archivo: `grid.rs:178-190` (también definido pero no usado en `environment.rs:76-86`)

### Modelo matemático

La línea de nieve varía sinusoidalmente a lo largo del año, reflejando la acumulación invernal y el deshielo estival:

```math
doy = day % 365
amplitude = cos(2π × (doy - 15) / 365)
snow_line = 2400 + 600 × (amplitude + 1) / 2
```

**Parámetros:**
- **2400 m**: línea de nieve base en verano (mínimo estacional)
- **600 m**: amplitud de la oscilación estacional
- **day 15** (15 de enero): máximo de nieve (coseno en fase)
- **day 197** (16 de julio): mínimo de nieve

La línea de nieve oscila entre:
- **2400 m** en verano (julio): solo las cumbres más altas tienen nieve
- **3000 m** en invierno (enero): la nieve desciende hasta cotas subalpinas

Una vez calculada la línea de nieve, la cobertura fraccional es:

```
if elevation < snow_line:
    snow_cover = 0
else:
    snow_cover = min(1, (elevation - snow_line) / 800)
```

La rampa lineal de 800 m significa que desde la línea de nieve hasta 800 m por encima,
la cobertura pasa de 0 a 1. Esto modela la transición gradual desde nieve parcial
(manchas, neveros) hasta nieve continua.

### Consecuencias ecológicas

- **Nieve > 0.5**: suprime completamente el crecimiento de plantas e invertebrados
- **Nieve > 0**: incrementa el coste de movimiento linealmente hasta 2×
- El modelo captura correctamente el gradiente altitudinal: a 2700 m la nieve dura ~4 meses más que a 2000 m

---

## 3. Temperatura (gradiente adiabático)

Archivo: `environment.rs:88-93`. **Importante: este modelo está definido pero nunca se invoca en el bucle de simulación.** Es una funcionalidad pendiente de conectar.

### Modelo matemático

```math
base_temp = 5 + 10 × cos(2π × (doy - 182) / 365)
temp = base_temp + (-0.0065) × max(0, elevation - 1000)
```

**Parámetros:**
- **5°C**: temperatura media anual base
- **±10°C**: amplitud estacional (oscilación invierno-verano)
- **day 182** (1 de julio): pico de temperatura en verano
- **−0.0065 °C/m** (−6.5 °C/km): gradiente adiabático seco estándar (lapse rate)
- **1000 m**: altitud de referencia por debajo de la cual se ignora el lapse rate

### Perfiles térmicos por altitud:

| Altitud | Verano (day 182) | Invierno (day 0) |
|---------|-----------------|-------------------|
| 1000 m | 15.0 °C | −5.0 °C |
| 2000 m | 8.5 °C | −11.5 °C |
| 2700 m (Pica d'Estats) | 4.45 °C | −15.55 °C |

### Consecuencias ecológicas (pendiente de implementar)

Una vez conectado, este modelo debería modular:
- **Tasa de crecimiento vegetal**: la temperatura real (no solo la estación) debería afectar la fotosíntesis
- **Estrés por frío**: añadir horas de frío al DEE de agentes (actualmente `is_cold` siempre es `false`)
- **Hibernación**: activar letargo en especies que hibernan (marmota, oso) cuando la temperatura baja
- **Límite del bosque**: el gradiente térmico explica por qué el bosque alpino termina ~2300 m

---

## 4. Dinámica de plantas (P1, P2, P3)

Archivo: `grid.rs:192-207`, `pools.rs:1-42`

### Los tres pools funcionales

Basados en la clasificación de `plant_clusters.tsv`:

| Pool | Tipo funcional | Ejemplos | Crecimiento (base/día) | Max (default) | Rol ecológico |
|------|---------------|----------|----------------------|---------------|---------------|
| P1 | Arbustos entomófilos | Rododendro, arándano, brezo | 0.02 | 2.0 kg | Sotobosque, alimenta polinizadores |
| P2 | Productores independientes | Helechos, musgos, líquenes | 0.015 | 1.5 kg | Cobertura suelo, humedad |
| P3 | Gramíneas de crecimiento rápido | Festuca, nardus, poa | 0.03 | 5.0 kg | Pastos, biomasa dominante en prados |

### Modelo de crecimiento

Crecimiento aditivo por paso diario:

```
P1 += 0.02 × growth_mod × P1_max
P2 += 0.015 × growth_mod × P2_max
P3 += 0.03 × growth_mod × P3_max
```

Cada pool se clamp a `[0, P_max]` después del crecimiento.

**Nota sobre densidad-dependencia**: el modelo actual es puramente aditivo, no logístico.
No hay competencia intraespecífica: una celda con 0.01 kg de P1 crece igual que una con 1.9 kg de P1.
Una mejora futura sería usar crecimiento logístico: `dP/dt = r × P × (1 - P/K)`.

### Modulador estacional (`seasonal_growth_modifier`)

| Estación | Días | Modificador | Justificación biológica |
|----------|------|-------------|------------------------|
| Verano | 152–243 | 1.0 | Fotoperiodo máximo, temperaturas óptimas |
| Primavera | 60–151 | 0.8 | Desarrollo foliar, floración |
| Otoño | 244–334 | 0.5 | Senescencia, caída de hoja |
| Invierno | 335–59, 0–59 | 0.1 | Reposo vegetativo, fotosíntesis mínima |

### Restricciones de crecimiento

El crecimiento no ocurre si la celda cumple **cualquiera** de estas condiciones:
- `is_water == true` — las plantas terrestres no crecen en agua
- `snow_cover > 0.5` — la nieve espesa bloquea la fotosíntesis
- `habitat_type == ROCA` — sustrato rocoso sin suelo

### Biomasa inicial según hábitat (cuando se carga TSV real)

| Hábitat | P1_max | P2_max | P3_max | P1_init | P2_init | P3_init |
|---------|--------|--------|--------|---------|---------|---------|
| BOSQUE_CON | 3.0 | 2.0 | 2.0 | 1.5 | 1.0 | 0.6 |
| BOSQUE_CAD | 4.0 | 3.0 | 3.0 | 2.0 | 1.5 | 0.9 |
| MATORRAL | 3.0 | 1.5 | 4.0 | 1.5 | 0.75 | 1.2 |
| PASTIZAL | 1.0 | 0.5 | 5.0 | 0.5 | 0.25 | 1.5 |
| HUMEDAL | 2.0 | 3.0 | 3.0 | 1.0 | 1.5 | 0.9 |
| ROCA | 0.1 | 0.1 | 0.5 | 0.05 | 0.05 | 0.15 |
| AGUA | 0.1 | 2.0 | 0.0 | 0.05 | 1.0 | 0.0 |
| RIBERA | 2.0 | 2.0 | 3.0 | 1.0 | 1.0 | 0.9 |
| ANTROPICO | 1.0 | 0.5 | 2.0 | 0.5 | 0.25 | 0.6 |

**Nota**: P3_max = 5.0 en PASTIZAL refleja que los pastos son la vegetación dominante en prados alpinos.
P2_max = 2.0 en AGUA representa plantas acuáticas (fitoplancton, algas).

---

## 5. Dinámica de invertebrados (I1, I2, I3)

Archivo: `grid.rs:209-221`, `pools.rs:44-83`

Los invertebrados se organizan en tres pools funcionales que forman una
**cadena trófica vertical dentro de cada celda**:

| Pool | Tipo | Se alimenta de | Tasa conversión | Crecimiento base | Max (kg) |
|------|------|---------------|-----------------|-----------------|----------|
| I1 | Polinizadores, fitófagos | P1 | 10% | 0.01 × growth_mod × P1 × 0.1 | 0.5 |
| I2 | Herbívoros, folívoros | P3 | 8% | 0.015 × growth_mod × P3 × 0.08 | 0.8 |
| I3 | Depredadores, parasitoides | I2 | 20% | 0.008 × growth_mod × I2 × 0.2 | 0.3 |

### Ecuaciones completas del paso diario:

```
I1 += 0.01 × growth_mod × P1 × 0.1    → clamped a [0, 0.5]
I2 += 0.015 × growth_mod × P3 × 0.08  → clamped a [0, 0.8]
I3 += 0.008 × growth_mod × I2 × 0.2   → clamped a [0, 0.3]
```

### Interpretación ecológica

- **I1** (abejas, mariposas, escarabajos polinizadores): su biomasa está limitada por la disponibilidad
  de plantas entomófilas (P1). La tasa de conversión del 10% significa que por cada kg de P1,
  pueden sostener 0.1 kg de I1.
- **I2** (orugas, saltamontes, pulgones): se alimentan de biomasa vegetal generalista (P3).
  Tasa de conversión 8% — más baja que I1 porque P3 es menos nutritivo.
- **I3** (arañas, mantis, avispas parasitoides): depredadores de I2. Tasa de conversión 20%
  (más eficiente porque la proteína animal es más digerible).

### Mismas restricciones que plantas

El crecimiento se suprime en celdas con `is_water`, `snow_cover > 0.5`, o `habitat == ROCA`.

---

## 6. Pools poblacionales

Archivo: `pools.rs:85-201`

Además de los pools por celda (plantas e invertebrados), el simulador mantiene
**7 pools poblacionales globales** que representan grupos taxonómicos no modelados como agentes individuales.

### 6.1 Peces (FishPool)

Archivo: `pools.rs:85-113`. Dos especies de la cuenca de la Noguera Pallaresa:

```rust
// Capacidad de carga:
river_km = num_celdas_agua × resolution_m / 1000
max_fish = river_km × 200  // 200 kg de peces por km de río

// Crecimiento diario:
truita += 0.01 × truita     → capped a max_fish × 0.7
barb_roig += 0.015 × barb_roig → capped a max_fish × 0.3
```

| Especie | Nombre científico | Reparto de K | Tasa crecimiento | Rol trófico |
|---------|------------------|-------------|-----------------|-------------|
| Truita (trucha) | Salmo trutta | 70% | 0.01 | Depredador tope acuático |
| Barb roig (barbo) | Barbus haasi | 30% | 0.015 | Omnívoro bentónico |

**Nota**: actualmente estos pools **no son consumidos por ningún agente**.
La nutria (Lutra lutra) tiene dieta 80% pez en el foodweb (`foodweb.rs:31-32`)
pero no hay código que conecte la depredación de nutrias al pool de peces.

### 6.2 Reptiles y anfibios (HerpPool)

Archivo: `pools.rs:115-138`. Crecimiento exponencial con modulador estacional:

```
reptiles += 0.008 × growth_mod × reptiles
amphibians += 0.0096 × growth_mod × amphibians
```

La tasa de anfibios es ligeramente superior (0.0096 vs 0.008) porque muchas especies
tienen ciclos reproductivos más rápidos. Ambos pools son ectotermos — su metabolismo
depende fuertemente de la temperatura (aunque el modelo actual usa solo el modulador estacional).

### 6.3 Paseriformes (PasserinePool)

Archivo: `pools.rs:140-157`. Aves insectívoras y granívoras pequeñas:

```
biomass += 0.01 × growth_mod × biomass
```

### 6.4 Micromamíferos (MicromammalPool)

Archivo: `pools.rs:159-177`. Roedores, musarañas, topillos — presas base para carnívoros:

```
biomass += 0.02 × growth_mod × biomass
```

La tasa más alta (0.02) refleja su alta fecundidad y generaciones cortas.

### 6.5 Murciélagos (BatPool)

Archivo: `pools.rs:179-201`. Quirópteros insectívoros:

```
biomass += 0.005 × growth_mod × biomass
```

La tasa más baja (0.005) refleja su baja fecundidad (1-2 crías/año) y madurez tardía.

### Limitación actual de los pools

Todos estos pools **crecen exponencialmente sin límite de carga** (no hay K) y
**no interactúan con los agentes** (ningún agente los consume, ningún pool es depredado).
Esto significa que sus poblaciones no están conectadas al resto del ecosistema.
Son proyecciones independientes que reflejan el modulador estacional pero no la retroalimentación trófica.

---

## 7. Metabolismo energético (Ley de Kleiber)

Archivo: `energy.rs:1-48`

### 7.1 Basal Metabolic Rate (BMR)

La tasa metabólica basal sigue la ley de Kleiber (1932, 1961),
una de las leyes más universales de la biología:

```math
BMR = 70 × M^{0.75}
```

Donde:
- **BMR**: kcal/día
- **M**: masa corporal en kg
- **70**: constante de proporcionalidad (kcal × kg⁻⁰·⁷⁵ × día⁻¹)
- **0.75**: exponente alométrico — las ¾ partes de la masa

**Fundamento biológico**: el exponente 0.75 refleja que la tasa metabólica escala
con la superficie corporal (∝ M²/³) pero corregido por la geometría fractal
de los sistemas de transporte internos (West, Brown & Enquist 1997, Science).

**BMR horaria** para cómputos de actividad:

```rust
bmr_kcal_h = bmr_kcal_day / 24.0
```

### 7.2 Costes de actividad (MET)

El **MET (Metabolic Equivalent of Task)** expresa el coste de una actividad como
múltiplo del BMR. Un MET de 2.0 significa que la actividad cuesta el doble que estar en reposo.

```math
coste_actividad (kcal/h) = MET × BMR_h
```

#### Coste de locomoción según pendiente

| Pendiente | MET | Ejemplo real |
|-----------|-----|-------------|
| < 5° | 2.5 | Andar por terreno llano |
| 5–15° | 3.0 | Caminata moderada, desnivel suave |
| 15–30° | 5.0 | Ascenso pronunciado, esfuerzo alto |
| > 30° | 6.0 | Escalada, terreno muy escarpado |

Estos valores están calibrados de la literatura (Pontzer 2017, Hoyt & Williams 1983)
para locomoción bípeda y cuadrúpeda en gradientes.

#### Costes de otras actividades

| Actividad | MET | Horas/día (default) |
|-----------|-----|---------------------|
| Reposo | 1.0 | 12 |
| Forrajeo | 2.0 | 6 |
| Otras (social, aseo, alerta) | 1.5 | 4 |
| Total día base | — | 24 |

### 7.3 Daily Energy Expenditure (DEE)

```math
DEE = (loco_h × MET_loco) + (forage_h × MET_forage) + (rest_h × MET_rest) + (other_h × MET_other)
```

Valores por defecto: loco=2h, forage=6h, rest=12h, other=4h.

**Modificadores** (implementados pero no activados):

$$
DEE_{final} =
\begin{cases}
DEE + 2 \times 2.0 \times BMR_h & \text{si hace frío (} T < 0°C \text{)} \\
DEE \times 1.4 & \text{si está lactando}
\end{cases}
$$

El modificador de **frío** añade 2 horas de termorregulación (temblor, piloerección)
a MET 2.0 (el doble del reposo). Esto representa el coste de mantener la homeotermia
en condiciones adversas.

El modificador de **lactancia** multiplica el gasto por 1.4, reflejando el coste
energético de producción de leche (unas 1.3–1.5× el BMR en mamíferos).

### 7.4 Reserva energética **[ACTUALIZADO]**

```rust
energia_inicial = masa_kg × 10000  // kcal (antes 5000)
```

### 7.5 Ingesta y asimilación **[ACTUALIZADO]**

| Recurso | Densidad energética | Eficiencia de asimilación |
|---------|--------------------|--------------------------|
| Planta | 1200 kcal/kg | 60% |
| Carne (vertebrado) | 1500 kcal/kg | 80% |
| Invertebrado | 2500 kcal/kg | 60% |

**Energía realmente asimilada** = `kg_ingeridos × kcal_por_kg × eficiencia`.

Limite de ingesta: máximo 10% de la masa corporal por día.

---

## 8. Forrajeo y consumo

Archivo: `agents.rs:200-243`

### 8.1 Algoritmo de forrajeo

```rust
fn do_forage(agent, cell) {
    available = cell.total_plant_biomass() + cell.total_invert_biomass()
    intake_kg = min(available, agent.mass_kg × 0.05)
    cell.subtract_biomass(intake_kg)  // reparto proporcional entre pools
    energia_ganada = intake_kg × 800 × 0.6  // 60% asimilación
}
```

**Reparto proporcional**: la biomasa se descuenta de los pools según su disponibilidad
relativa. Por ejemplo, si una celda tiene 60% P1, 20% P2, 20% P3, el consumo se reparte
en esas proporciones.

### 8.2 Forrajeo basado en dieta **[ACTUALIZADO]**

Ahora `do_forage()` consulta `get_diet(species_key)` para determinar las proporciones
de planta/invertebrado que come cada especie. Las proporciones se respetan y el consumo
se reparte según la dieta, no según la biomasa disponible. Además, el forrajeo incluye
un factor estocástico (±40%) para evitar comportamiento determinista.

---

## 9. Comportamiento de agentes **[ACTUALIZADO]**

Archivo: `agents.rs:7-353`

### 9.0 Novedades: género, variación individual, estocasticidad

Cada agente tiene:
- **Género** (Male/Female) asignado aleatoriamente (50/50)
- **Peso individual**: ±20% del peso medio de la especie
- **Edad inicial**: hasta 25% de la esperanza de vida
- **Personalidad** (`boldness` 0-1): afecta la probabilidad de explorar vs quedarse
- **Comportamiento estocástico**:
  - 5% de probabilidad de estar inactivo (mayor si es tímido)
  - 8% de exploración aleatoria (mayor si es audaz)
  - Búsqueda de comida con umbral variable (±50%)
  - Forrajeo con éxito variable (60-100%)
  - Reproducción con probabilidad del 30% (aunque cumpla condiciones)

### 9.1 Tipos de agente

```rust
enum AgentKind {
    Herbivore,  // busca plantas
    Carnivore,  // caza invertebrados
    Omnivore,   // come de todo
    Bird,       // radio de búsqueda grande
}
```

### 9.2 Estado del agente

Cada agente mantiene:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `x, y` | `i32` | Posición en el grid |
| `mass_kg` | `f64` | Masa corporal (constante) |
| `energy_kcal` | `f64` | Energía disponible (inicial: mass × 5000) |
| `age_days` | `u64` | Edad en días |
| `is_pregnant` | `bool` | Gestación activa |
| `is_lactating` | `bool` | Lactancia/cuidado parental |
| `gestation_days` | `u64` | Días de gestación transcurridos |
| `days_since_reproduction` | `u64` | Días desde último evento reproductivo |
| `calories_consumed_today` | `f64` | Seguimiento diario de ingesta |
| `calories_spent_today` | `f64` | Seguimiento diario de gasto |

### 9.3 Herbívoro (step_herbivore)

```
1. Evaluar celda actual:
   if biomasa_vegetal < 5% del peso corporal:
       buscar mejor celda en radio 5
       mover con A* hacia ella
2. Forrajear en celda actual
3. Actualizar energía (DEE)
4. Actualizar biología (edad, gestación)
5. Comprobar muerte
```

**Criterio de búsqueda**: `score = biomasa_total / coste_a_star`
(prioriza celdas con mucha comida y fácil acceso).

### 9.4 Carnívoro (step_carnivore)

```
1. Detectar presa en radio 8:
   buscar celdas con biomasa de invertebrados > 0.1 kg
2. Si hay presa detectable:
       mover con A* hacia la celda con más invertebrados
       al llegar: kill = cell.invert_biomass × 0.3
         energía += kill × 2000 × 0.8  (carne, 80% asimilación)
   Si no:
       wander aleatorio (radio 5, 20 intentos)
3. Si no ha cazado, forrajear como omnívoro
4. Actualizar energía, biología, muerte
```

**Limitación**: el carnívoro "caza" biomasa de invertebrados (pool I1+I2+I3),
no agentes vertebrados. No hay depredación real de un agente sobre otro.
Un águila real "caza" saltamontes en lugar de rebecos o marmotas.

### 9.5 Omnívoro (step_omnivore)

```
1. Si celda tiene comida (planta > 0.1 o invert > 0.01):
       forrajear
   Si no:
       buscar comida en radio 10
       mover con A*
       forrajear
2. Actualizar energía, biología, muerte
```

### 9.6 Ave (step_bird)

```
1. Si celda tiene muy poca comida (< 0.001 kg):
       buscar mejor celda en radio 15
       mover con A*
2. Forrajear
3. Actualizar energía, biología, muerte
```

### 9.7 Muerte

Un agente muere si cumple **cualquiera** de:

```rust
energy_kcal <= 0          // inanición
age_days >= lifespan_days  // senescencia (10 años por defecto)
```

No hay muerte por depredación, enfermedad, accidente, o causas ambientales.

---

## 10. Reproducción

Archivo: `simulation.rs:222-259`, `agents.rs:342-353`

### Condiciones

La reproducción ocurre **solo en primavera o verano** (días 60–243 del año calendario).

El proceso se activa para madres lactantes con `days_since_reproduction < 60`.

### Parámetros

| Parámetro | Valor actual | Nota |
|-----------|-------------|------|
| Tamaño de camada | 1–2 (aleatorio) | Mismo para todas las especies |
| Masa de cría | 5–15% de la masa materna | Constante para todas |
| Edad reproductiva mínima | 365 días | Mismo para todas |
| Gestación total | 150 días | Mismo para todas |
| Lifespan | 3650 días (10 años) | Mismo para todas |

### Algoritmo

```
for each agent alive AND female AND lactating:
    if days_since_reproduction < 60 AND is spring/summer:
        n_births = random(litter_min, litter_max)
        for each birth:
            child_x = parent_x + random(-2, 2)
            child_y = parent_y + random(-2, 2)
            child_mass = parent_mass × random(0.05, 0.15)
            child_energy = child_mass × 5000
            push child to agents list
        parent.is_lactating = false
```

### Limitación: `should_reproduce()` no se usa

El método `Agent::should_reproduce()` en `agents.rs:342-353` comprueba si hay suficiente
energía (2000–3000 kcal/kg dependiendo del tipo) antes de permitir la reproducción,
pero **nunca es llamado** por el bucle de simulación. Solo el temporizador de lactancia
controla la reproducción, sin coste energético.

---

## 11. Pathfinding (A*)

Archivo: `pathfinding.rs:131`

### Algoritmo

Implementación estándar de A* con heurística euclídea y 8 vecinos:

```rust
fn a_star_path(grid, start, goal, max_steps) -> Option<Vec<(i32, i32)>>
```

### Componentes

**Heurística**: distancia euclídea (la más precisa para movimiento libre):

```math
h(a, b) = \sqrt{(a_x - b_x)^2 + (a_y - b_y)^2}
```

**Coste de movimiento** (8 direcciones):
- Cardinal: `cost_a_star[vecino]`
- Diagonal: `cost_a_star[vecino] × 1.414 (√2)`

**Estructura de datos**:
- `BinaryHeap<Reverse<OrderedFloat<f64>>>` como cola de prioridad (min-heap)
- `Vec<Option<usize>>` para `came_from`
- `Vec<f64>` para `g_score` y `f_score`

### Complejidad

- Peor caso: O(N log N) donde N = número de celdas exploradas
- Limitado por `max_steps` (configurable, default típico 5000)
- En grid real de 180K celdas, una búsqueda típica explora ~100–500 celdas

### Coste de celda

```rust
cost = slope_factor * (1.0 + snow_cover) * terrain_factor
```

---

## 12. Red trófica (sistema decorativo)

Archivo: `foodweb.rs:105`

### Dietas definidas (22 especies)

El archivo contiene dietas detalladas para 22 especies con proporciones en 5 categorías:

| Especie | Tipo | Planta | Invert | Vertebrado | Carroña | Pez |
|---------|------|--------|--------|------------|---------|-----|
| Rupicapra pyrenaica (rebeco) | Herbívoro | 1.0 | — | — | — | — |
| Cervus elaphus (ciervo) | Herbívoro | 1.0 | — | — | — | — |
| Capreolus capreolus (corzo) | Herbívoro | 1.0 | — | — | — | — |
| Oryctolagus cuniculus (conejo) | Herbívoro | 1.0 | — | — | — | — |
| Marmota marmota (marmota) | Herbívoro | 0.95 | 0.05 | — | — | — |
| Sciurus vulgaris (ardilla) | Herbívoro | 0.95 | 0.05 | — | — | — |
| Tetrao urogallus (urogallo) | Herbívoro | 0.70 | 0.30 | — | — | — |
| Lagopus muta (perdiz nival) | Herbívoro | 0.80 | 0.20 | — | — | — |
| Rupicapra pyrenaica (isard) | Herbívoro | 1.0 | — | — | — | — |
| Ovis musimon (muflón) | Herbívoro | 1.0 | — | — | — | — |
| Dama dama (gamo) | Herbívoro | 1.0 | — | — | — | — |
| Aquila chrysaetos (águila real) | Carnívoro | — | — | 0.90 | 0.10 | — |
| Lutra lutra (nutria) | Carnívoro | — | — | — | 0.20 | 0.80 |
| Martes martes (marta) | Carnívoro | 0.20 | 0.30 | 0.50 | — | — |
| Mustela erminea (armiño) | Carnívoro | — | 0.20 | 0.80 | — | — |
| Mustela nivalis (comadreja) | Carnívoro | — | 0.30 | 0.70 | — | — |
| Felis silvestris (gato montés) | Carnívoro | — | — | 0.90 | 0.10 | — |
| Ursus arctos (oso pardo) | Omnívoro | 0.80 | 0.10 | 0.05 | 0.05 | — |
| Sus scrofa (jabalí) | Omnívoro | 0.70 | 0.20 | 0.05 | 0.05 | — |
| Vulpes vulpes (zorro) | Omnívoro | 0.20 | 0.30 | 0.30 | 0.20 | — |
| Meles meles (tejón) | Omnívoro | 0.50 | 0.30 | 0.10 | 0.10 | — |
| Corvus corax (cuervo) | Omnívoro | 0.20 | 0.30 | 0.20 | 0.30 | — |
| Gypaetus barbatus (quebrantahuesos) | Carroñero | — | — | 0.05 | 0.95 | — |

### Enlaces tróficos (15 relaciones)

Ejemplos de relaciones depredador-presa definidas:

| Depredador | Presa | Proporción | Tipo |
|-----------|-------|-----------|------|
| Aquila chrysaetos | Rupicapra pyrenaica | 0.3 | Depredación |
| Aquila chrysaetos | Marmota marmota | 0.5 | Depredación |
| Aquila chrysaetos | Lagopus muta | 0.1 | Depredación |
| Martes martes | Tetrao urogallus | 0.3 | Depredación |
| Martes martes | Sciurus vulgaris | 0.3 | Depredación |
| Vulpes vulpes | Oryctolagus cuniculus | 0.3 | Depredación |
| Vulpes vulpes | Tetrao urogallus | 0.1 | Depredación |
| Vulpes vulpes | Lagopus muta | 0.1 | Depredación |
| Gypaetus barbatus | Rupicapra pyrenaica | 0.4 | Carroñeo |
| Gypaetus barbatus | Cervus elaphus | 0.3 | Carroñeo |
| Lutra lutra | Salmo trutta | 0.6 | Depredación |
| Mustela erminea | Lagopus muta | 0.2 | Depredación |
| Mustela nivalis | Oryctolagus cuniculus | 0.2 | Depredación |
| Felis silvestris | Oryctolagus cuniculus | 0.3 | Depredación |
| Felis silvestris | Tetrao urogallus | 0.1 | Depredación |

### Funcionalidad actual **[ACTUALIZADO]**

Ahora el sistema trófico está completamente integrado:

- **`get_diet()`**: usado en `do_forage()` para forrajeo basado en dieta especie-específica
- **`get_prey()`**: usado en `predation_step()` para depredación agente-a-agente
- **`get_prey_weighted()`**: usado en decisiones de carnívoros para seleccionar presas según proporciones
- **TROPHIC_LINKS**: usado para determinar qué especies depredan a cuáles y en qué proporción
- **Carroñeros**: `consume_carcass()` para especies con dieta carroña (quebrantahuesos 95%, cuervo 30%, etc.)
- **Pools conectados**: `pool_consumption_step()` consume peces, micromamíferos, paseriformes y herps según la dieta del agente

---

## 13. Modelo de datos y carga

Archivo: `io.rs:89`

### 13.1 Carga TSV (terreno real)

```rust
// Ruta esperada: ecosystem/data/terrain_cells.tsv
// Columnas (0-indexed):
//   0: x (columna del grid)
//   1: y (fila del grid)
//   2: utm_x (coordenada UTM, ignorada)
//   3: utm_y (coordenada UTM, ignorada)
//   4: elevation_m
//   5: slope_deg
//   6: aspect_deg
//   7: tri
//   8: piso_bioclimatico
```

El TSV tiene **180.037 filas** correspondientes a las celdas válidas del grid real
(375 × 502, recortado a la cuenca de Vall de Cardós).

### 13.2 Grid plano (fallback)

Si no se encuentra el TSV, se genera un grid plano con:
- Toda celda: piso=MONTANO, habitat=PASTIZAL
- P1_max=2.0, P2_max=1.5, P3_max=5.0
- Biomasa inicial: P1=1.0, P2=0.5, P3=1.5, I1=0.1, I2=0.2, I3=0.05

### 13.3 Inicialización de agentes

Cada especie tiene preferencias de hábitat y piso definidas en `simulation.rs:11-35`.
`find_spawn_cells()` busca celdas que cumplan ambos criterios. Si no hay celdas aptas,
spawn aleatorio. La población se escala al área del grid:

```rust
scaled = max(1, count × area_celdas / 10000_ha)
```

### 13.4 GeoTIFFs (pendiente)

Existen 7 archivos GeoTIFF en `ecosystem/data/`:
- `terrain_dem_25m.tif`, `terrain_slope.tif`, `terrain_aspect.tif`, `terrain_tri.tif`
- `terrain_pisos.tif`, `terrain_habitat.tif`
- `terrain_biomass.tif` (9 bandas: P1, P2, P3, I1, I2, I3, P1_max, P2_max, P3_max)

La versión Python los carga con `rasterio`. La versión Rust no tiene carga GeoTIFF
implementada — necesitaría el crate `gdal` con `--features geo`.

---

## 14. CLI y ejecución

Archivo: `main.rs:71`

```bash
cargo run -- --width 400 --height 400 --days 365 --res 25 --output output
cargo run -- --demo  # atajo: 50×50, 30 días
```

### Argumentos

| Flag | Default | Descripción |
|------|---------|-------------|
| `--width` | 400 | Ancho del grid en celdas |
| `--height` | 400 | Alto del grid en celdas |
| `--days` | 365 | Días de simulación |
| `--res` | 25 | Resolución en metros/celda |
| `--output` | "output" | Directorio de salida |
| `--demo` | false | Modo demo (50×50, 30 días) |

### Output

El programa imprime estadísticas en JSON al finalizar:
```json
{
  "days": 365,
  "agents_alive": 184,
  "agents_dead": 52,
  "grid": "400x400",
  "plant_biomass_kg": 12345.6,
  "invert_biomass_kg": 0.0,     // BUG: siempre 0, falta en get_stats()
  "species_counts": { ... }
}
```

Además genera:
- `output/simulation_log.csv`: registro día a día
- `output/snapshot_*.json`: estado completo cada 100 días

---

## 15. Resumen de discrepancias y bugs conocidos

### 15.1 Bugs corregidos **[ACTUALIZADO]**

| # | Bug | Estado |
|---|-----|--------|
| 1 | `invert_biomass_kg` en `get_stats()` | ✅ Corregido: `total_invert_biomass()` existe y se usa |
| 2 | `neighbors_numba()` | ✅ Eliminado (código Python, no Rust) |

### 15.2 Funcionalidad ahora implementada **[ACTUALIZADO]**

| # | Componente | Estado actual |
|---|-----------|-------------|
| 3 | `default_temp_fn()` | ✅ Conectado: `grid.step_temperature(day)` se llama en el bucle |
| 4 | `default_snow_fn()` | ✅ Inline en `grid.step_snow()` |
| 5 | `Environment.temperature_base_c` | Almacenado (no usado directamente) |
| 6 | `Environment.snow_line_base` | Almacenado (no usado directamente) |
| 7 | `get_diet()` | ✅ Usado en `do_forage()` y `pool_consumption_step()` |
| 8 | `get_predators()` | ✅ Usado en `predation_step()` |
| 9 | `get_prey()` | ✅ Usado en `predation_step()` |
| 10 | `TROPHIC_LINKS` | ✅ Usado vía `get_prey_weighted()` para decisiones de caza |
| 11 | `should_reproduce()` | ✅ Llamado en `reproduce_step()`, con estocasticidad |
| 12 | `home_radius_cells` | ✅ Almacenado, usado para wander radius |

### 15.3 Gaps ecológicos cerrados **[ACTUALIZADO]**

| # | Gap | Estado |
|---|-----|--------|
| 13 | Depredación agente-a-agente | ✅ Implementada en `predation_step()` |
| 14 | Sistema trófico | ✅ Integrado: dieta, depredación, carroñeo, pools |
| 15 | Parámetros especie-específicos | ✅ Implementados en `PopulationConfig` (18 especies) |
| 16 | Pools desacoplados | ✅ Conectados vía `pool_consumption_step()` |
| 17 | Crecimiento P3/P1 | ⚠️ Pendiente de revisión ecológica |
| 18 | Densidad-dependencia vegetal | ✅ Implementado: crecimiento logístico `r*P*(1-P/K)` |
| 19 | `is_cold` | ✅ Implementado: `compute_is_cold()` con umbral -3°C |
| 20 | Datos reales | ✅ TSV cargado automáticamente si existe |

---

## 16. Estado actual de implementación **[ACTUALIZADO]**

La mayoría de las fases del roadmap original están completadas:

### ✅ Fase 2 (Carga de datos reales)
- **Ruta TSV**: configurable vía `--data-dir`, default `../ecosystem/data`
- **Carga TSV**: automática si existe, con pisos, elevación, pendiente, aspecto, TRI
- **GeoTIFF**: implementado con `gdal` (feature gate `--features geo`)
- **Asignación hábitat**: desde piso + elevación, con defaults por tipo de hábitat

### ✅ Fase 3 (Sistema trófico real)
- **`get_diet()`**: usado en `do_forage()`, `pool_consumption_step()`, `scavenging_step()`
- **Depredación agente-a-agente**: en `predation_step()` con `get_prey()`
- **Muerte por depredación**: `DeathCause::Predation` y carcasa para carroñeros
- **Carroñeros**: `consume_carcass()` + `scavenging_step()` para especies con carroña
- **Pools como presa**: `pool_consumption_step()` conecta peces, micromamíferos, paseriformes, herps

### ✅ Fase 4 (Diferenciación de especies)
- **`PopulationConfig`**: 13 campos especie-específicos (gestación, camada, edad reproductiva, esperanza de vida, velocidad, distancia diaria)
- **`should_reproduce()`**: llamado con umbral energético y estocasticidad
- **`home_range_radius`**: usado para wander radius y detección

### ✅ Fase 5 (Correcciones y mejoras)
- **`invert_biomass_kg`**: incluido en `get_stats()`
- **Temperatura conectada**: `grid.step_temperature()` + `compute_is_cold()` en el bucle
- **Crecimiento logístico**: `step_plants_logistic()` con `r*P*(1-P/K)`
- **Forrajeo selectivo**: basado en proporciones de dieta

### ✅ Fase 6 (Paralelización)
- **Rayon 1.8.0**: bucle de agentes paralelizado con patrón decisión/ejecución

### ✅ Fase 7 (Output y visualización)
- **CSV por especie**: `species_population.csv` con todas las especies
- **Simulación log**: incluye temperatura, estación, biomasa
- **Snapshots JSON**: con detalles de agente (género, peso, energía, boldness)
- **Visualización Python**: `visualize_simulation.py` con 4 tipos de gráficos

### ⏳ Fase 8 (Tests) — No iniciada
- Pendiente de implementar tests unitarios y de integración

---

## 17. Conexión Python → Rust: estado del port

### Lo que el Rust YA tiene (herencia del Python)

| Componente | Python (líneas) | Rust (líneas) | Estado |
|-----------|----------------|---------------|--------|
| Grid/Cell | 316 | 272 | ✅ Completo |
| Environment | 79 | 93 | ✅ Parcial (nieve sí, temperatura no conectada) |
| Energy (BMR, MET, DEE) | 118 | 92 | ✅ Completo |
| Pathfinding (A*) | 129 | 131 | ✅ Completo |
| Pools (plantas, inverts, peces, herps, aves, micromamíferos, murciélagos) | 216 | 249 | ✅ Completo |
| Foodweb (dietas, enlaces) | 125 | 105 | ⚠️ Definido pero no integrado |
| Simulation loop | 292 | 405 | ✅ Completo |
| Agent herbivore | 78 | 353 (todos) | ✅ Completo |
| Agent carnivore | 105 | (incluido) | ✅ Completo |
| Agent omnivore | 68 | (incluido) | ✅ Completo |
| Agent bird | 45 | (incluido) | ✅ Completo |
| TSV loading | 228 | 89 | ✅ Básico |
| CLI | 85 | 71 | ✅ Completo |
| **Total** | **~1.764** | **1.873** | |

### Lo que el Python tiene y el Rust NO tiene

| Feature | Python | Rust | Prioridad |
|---------|--------|------|-----------|
| Carga GeoTIFF (7 archivos, 9 bandas) | `io.py:228` | ❌ No implementado | Alta |
| Procesador MCSC (44→10 hábitats) | `process_mcsc.py:485` | ❌ No implementado | Baja (offline) |
| Validación energética (38 spp, Nagy 2005) | `validate_energy.py:641` | ❌ No implementado | Baja (herramienta) |
| Visualización terreno (matplotlib, 3×3 dashboard) | `visualize_terrain.py:286` | ❌ No implementado | Baja (herramienta) |
| Dietas reales integradas en forrajeo | `foodweb.py:125` | ⚠️ Decorativo | **Alta** |
| Depredación agente-a-agente | `agents/carnivore.py:105` | ❌ No implementado | **Alta** |
| Agente Bird instanciable | `agents/bird.py:45` | ⚠️ Definido pero ninguna especie lo usa | Media |
| 18 actividades MET | `energy.py:118` | ⚠️ Solo 5 actividades | Media |
| Modificador frío en DEE | `energy.py` | ⚠️ Definido, `is_cold` siempre `false` | Media |
| Modificador lactancia en DEE | `energy.py` | ✅ Implementado | — |
| Numba JIT fallback (pure-Python) | Todo | ✅ No necesario (Rust compila) | — |

---

## 18. Dependencias

| Crate | Versión | Uso |
|-------|---------|-----|
| `clap` | 4.4.18 | CLI argumentos (`--width`, `--days`, `--demo`, etc.) |
| `rand` | 0.8 | Números aleatorios (spawn, reproducción, wander) |
| `serde` + `serde_json` | 1 | Snapshots JSON de estado |
| `ordered-float` | 4 | Implementar `Ord` para `f64` en BinaryHeap de A* |
| `csv` | 1.4 | Carga TSV de terreno |
| `gdal` | 0.17 (opcional, feature `geo`) | Carga GeoTIFF (pendiente de implementar) |
| `rayon` | (pendiente) | Paralelización del bucle de agentes (Fase 6) |

---

## 19. Referencias biológicas

| Concepto | Referencia |
|----------|-----------|
| Kleiber's law (BMR = 70×M^0.75) | Kleiber, M. (1932). "Body size and metabolism". *Hilgardia* 6:315–353. |
| Fractal scaling explanation | West, G.B., Brown, J.H. & Enquist, B.J. (1997). "A general model for the origin of allometric scaling laws in biology". *Science* 276:122–126. |
| MET costs for locomotion | Pontzer, H. (2017). "Locomotor ecology and evolution in chimpanzees and humans". *Am. J. Phys. Anthropol.* 162:72–83. |
| MET costs by slope | Hoyt, D.F. & Williams, E. (1983). "Energy expenditure of walking on a gradient". *J. Exp. Biol.* 107:89–97. |
| Standard adiabatic lapse rate | Wallace, J.M. & Hobbs, P.V. (2006). *Atmospheric Science: An Introductory Survey*. Academic Press. |
| Snow line model | Adapted from Hock, R. (2003). "Temperature index melt modelling in mountain areas". *J. Hydrol.* 282:104–115. |
| Mediterranean seasonal vegetation | Terradas, J. (2001). *Ecología de la vegetación*. Omega, Barcelona. |
| PNAP biodiversity | Generalitat de Catalunya (2003). *Pla Especial del Parc Natural de l'Alt Pirineu*. |
| Energy density of food resources | Nagy, K.A. (2005). "Field metabolic rate and body size". *J. Exp. Biol.* 208:1621–1625. |
| River carrying capacity for fish | Vannote, R.L. et al. (1980). "The river continuum concept". *Can. J. Fish. Aquat. Sci.* 37:130–137. |
| Invertebrate trophic chains in soil | Swift, M.J., Heal, O.W. & Anderson, J.M. (1979). *Decomposition in Terrestrial Ecosystems*. Blackwell. |
| Alpine plant phenology | Körner, C. (2003). *Alpine Plant Life*. Springer. |
