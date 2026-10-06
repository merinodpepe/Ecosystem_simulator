# An Agent-Based Model of Trophic Dynamics in the Alt Pirineu Natural Park: From Empirical Data to Emergent Ecosystem Behavior

## Resumen

> *Pendiente de redacción — se completará al final del proceso.*

---

## 1. Introducción

### 1.1 Contexto

Los ecosistemas de montaña son particularmente sensibles a los cambios ambientales y a las perturbaciones antrópicas. Comprender las dinámicas tróficas que sustentan la biodiversidad en estos sistemas es esencial para su gestión y conservación. Los modelos basados en agentes (Agent-Based Models, ABM) ofrecen una aproximación metodológica potente para explorar las interacciones locales que dan lugar a patrones ecológicos emergentes a escala de ecosistema (Grimm et al., 2006; Railsback & Grimm, 2019).

El presente trabajo describe la construcción de la base de datos biológica y el diseño de un simulador agent-based del ecosistema del **Parc Natural de l'Alt Pirineu (PNAP)**, el parque natural más extenso de Cataluña (~80.000 ha), situado en el corazón de los Pirineos. El modelo integra datos empíricos sobre especies, interacciones tróficas, requerimientos energéticos y dinámicas estacionales para explorar preguntas fundamentales sobre el funcionamiento del ecosistema.

### 1.2 Preguntas de Investigación

1. **Cascadas tróficas:** ¿Cómo operan las cascadas tróficas en un ecosistema de montaña mediterráneo donde los grandes depredadores (oso, lobo) tienen densidades bajas o están ausentes?
2. **Dinámicas poblacionales emergentes:** ¿Qué patrones poblacionales surgen de la interacción entre depredación, competencia y disponibilidad estacional de recursos?
3. **Restricciones estacionales:** ¿Cómo afectan las restricciones estacionales (nieve invernal, sequía estival) al flujo de energía y a las interacciones entre especies?
4. **Especies clave:** ¿Qué papel juegan las especies clave (quebrantahuesos, urogallo, oso pardo) en el mantenimiento de la estabilidad del ecosistema?

### 1.3 Estado del Arte

La modelización ecológica basada en agentes ha experimentado un crecimiento significativo en las últimas décadas. Trabajos fundamentales como el modelo de reintroducción del lobo en Yellowstone (Smith et al., 2003) han demostrado el poder de los ABM para explorar efectos tróficos en cascada. Sin embargo, pocos modelos integran datos empíricos detallados sobre gasto energético, composición de la dieta e interacciones tróficas a nivel de especie individual en un ecosistema de montaña mediterráneo.

Proyectos recientes en entornos alpinos han explorado enfoques complementarios:
- **Multi-Agent Reinforcement Learning** para ecosistemas alpinos (lobo-rebeco-vegetación) sobre grid 100×100 en los Alpes Réticos, demostrando que agentes entrenados con RL reproducen dinámicas poblacionales realistas sin reglas escritas a mano (bioRxiv 2025).
- **Modelo socioecológico del Pirineo catalán** basado en ODEs con 30 elementos (socioeconomía, usos del suelo, biodiversidad, hidrología, clima) que identificó factores clave para la sostenibilidad mediante 100.000 simulaciones (Jolivet et al., 2026, *Nature Communications Sustainability*).
- **Modelo P-systems de isards en Pirineos** utilizando Membrane Computing (MeCoSim) para simular dinámica poblacional con módulos de clima, reproducción, densidad, alimento y mortalidad (Universidad de Sevilla).

Este proyecto se inspira en la tradición de los modelos individual-based (IBM) y de agentes (ABM) aplicados a sistemas ecológicos, siguiendo los principios ODD (Overview, Design concepts, Details) propuestos por Grimm et al. (2006, 2020). La integración de datos empíricos detallados, terreno real (SRTM 25m), y comportamiento autónomo con GOAP (Goal-Oriented Action Planning) lo diferencia de aproximaciones anteriores.

---

## 2. Área de Estudio

El Parc Natural de l'Alt Pirineu se encuentra en el noroeste de Cataluña, en la comarca del Pallars Sobirà, y se extiende por una superficie de aproximadamente 80.000 hectáreas (79.317 ha desde su creación el 1 de agosto de 2003 mediante el Decreto 194/2003). El rango altitudinal va desde los 650 m hasta los 3.143 m (pico de la Pica d'Estats), lo que genera una notable diversidad de climas y hábitats [1][2]:

- **Piso montano** (650-1.600 m): bosques de roble, pino silvestre, abeto, haya.
- **Piso subalpino** (1.600-2.300 m): bosque de pino negro, matorrales de rododendro.
- **Piso alpino** (2.300-2.700 m): prados alpinos, canchales.
- **Piso nival** (>2.700 m): roca desnuda y nieve permanente.

El parque alberga una biodiversidad excepcional: ~277 especies de vertebrados (7 peces, 8 anfibios, 17 reptiles, 184 aves y 61 mamíferos), entre 1.465 y 1.765 especies de plantas vasculares (catálogo 2025; ~47% de la flora autóctona de Catalunya) y 900+ especies de lepidópteros (168 especies de mariposas diurnas, ~82% de toda Cataluña) [1][3][4][5][104]. Es el parque natural más extenso de Cataluña y su complejidad orográfica y amplitud altitudinal generan la mayor diversidad de ecosistemas del territorio.

---

## 3. Materiales y Métodos

### 3.1 Base de Datos Biológicos

Se elaboró una base de datos maestra que documenta 22 especies de vertebrados representativas de los principales niveles tróficos del ecosistema, complementadas con clusters funcionales de plantas (3) e invertebrados (3) [6]. Para cada especie se recopilaron datos taxonómicos, tróficos, reproductivos y morfométricos, utilizando fuentes como PanTHERIA [7], EltonTraits [8], FishBase, AmphibiaWeb, USDA FoodData Central [9] y literatura especializada.

El parque tiene ~277 especies de vertebrados documentadas [1], pero para la simulación se seleccionaron las especies más emblemáticas y/o clave para la dinámica trófica, siguiendo un enfoque de grupos funcionales que permite reducir la complejidad computacional manteniendo la representatividad ecológica [6].

### 3.2 Clusters Funcionales de Plantas

Dado que el PNAP alberga entre 1.500 y 1.590 especies de flora vascular [2][5], se definieron tres clusters funcionales que capturan los principales roles ecológicos [6]:

#### 3.2.1 Cluster P1: Plantas Entomófilas de Sotobosque y Prados Floridos

Plantas dependientes de polinizadores externos (insectos), con alta conexión con la comunidad de polinizadores. Incluye especies representativas como:

- ***Vaccinium myrtillus*** (Nabiu/Arándano): Produce frutos carnosos de alto valor energético (~0.80 kcal/g) [9]. Dispersada por aves y mamíferos [10][11][12]. Fenología: brotación primavera, floración finales de primavera a inicio de verano, fructificación verano-otoño [6][10][11].
- ***Leontopodium alpinum*** (Flor de neu/Edelweiss): Planta alpina de prados y roquedos calcáreos. Floración corta en verano (julio-agosto) ligada al deshielo [6][13][14].
- ***Astragalus penduliflorus*** (Astràgal pèndul/Astrágalo péndulo): Fabácea entomófila, fijadora de nitrógeno. Floración a finales de primavera e inicio de verano. Especie amenazada en el PNAP [6][13][15].
- ***Gentiana acaulis*** (Genciana de flor gran/Genciana de flor grande): Planta de prados alpinos acidófilos. Floración muy concentrada en primavera-inicio de verano [16][17][14].
- ***Trifolium alpinum*** (Regalèssia de muntanya/Regaliz de montaña): Fabácea entomófila de alto valor forrajero, fijadora de nitrógeno, polinizada por abejas [17][6][16].

Las plantas P1 presentan polinización por insectos (abejas, mariposas) y dispersión de frutos por aves y mamíferos. Su fenología está marcada por la estacionalidad alpina, con brotación primaveral y fructificación estival [6][10][11][13].

#### 3.2.2 Cluster P2: Productores Independientes (Acuáticos y Esporófitos)

Plantas con baja o nula dependencia de polinizadores animales. Incluye:

- ***Hippuris vulgaris*** (Cua de cavall aquàtica/Cola de caballo acuática): Planta acuática emergente, reproducción vegetativa por rizomas, polinización hidrogama y anemófila [6][13][18].
- **Pteridófitos** (helechos como *Athyrium filix-femina*, *Dryopteris filix-mas*): Reproducción por esporas, sin polinizadores. Ocupan el estrato herbáceo de bosques húmedos de ribera, hayedo y abetal [2][5][19].
- **Briófitos** (musgos de torrentes y turberas): Reproducción por esporas y propagación vegetativa. Importantes para la retención de agua y creación de microhábitats para invertebrados [6][20].

#### 3.2.3 Cluster P3: Pastizales y Praderas de Crecimiento Rápido (Recurso Base)

Recurso base de energía para grandes herbívoros. Incluye:

- ***Nardus stricta*** (Pèl caní/Cervuno): Gramínea dominante en prados acidófilos de alta montaña. Forma césped denso muy resistente al pastoreo. Polinización anemófila, gran producción de semillas [6][16][17].
- ***Festuca eskia***, ***F. airoides*** (Festuques alpines/Festucas alpinas): Gramíneas formadoras de macollas en prados alpinos acidófilos. Crecimiento rápido en temporada de buen tiempo, base de la dieta de isard y ganado durante el verano [6][16][21].
- **Mezcla de leguminosas** (*Trifolium repens*, *T. pratense*, *Lotus corniculatus*): Fijadoras de nitrógeno, alto valor forrajero, polinizadas por abejas y abejorros [6][22][17].

En el modelo, este cluster representa un "pool" de biomasa herbácea rápidamente renovable que sostiene la dieta de isards, ciervos, corzos, muflones, gamos y jabalíes [6][23][24][25].

### 3.3 Clusters Funcionales de Invertebrados

El PNAP es un hot-spot europeo de lepidópteros (~910 especies censadas, ~61% de las catalogadas en Cataluña) [4][5][26]. Se definieron tres clusters funcionales [6]:

#### 3.3.1 Cluster I1: Polinizadores Mutualistas

- ***Boloria eunomia*** (Donzella de la bistorta/Mariposa de la Bistorta): **En peligro de extinción** [27]. Larvas se alimentan de hojas de *Bistorta officinalis*; adultos de néctar de flores de Bistorta y otras compuestas [28][29][30]. Univoltina, vuelo primavera tardía-inicio de verano [29][30].
- ***Parnassius mnemosyne*** (Mnemòsine): Especie protegida. Larvas se alimentan de *Corydalis* spp.; adultos de néctar de flores de prado (Ranunculus, Trifolium) [31][32][33][34]. Univoltina, vuelo finales de primavera y principios de verano [31][33][35].
- ***Bombus spp.*** (Borinots/Abejorros): Polinizadores clave del ecosistema alpino. Adultos nectarívoros y polinívoros; larvas alimentadas con polen y néctar por obreras [36][17][37]. Ciclo anual con reinas fecundadas invernantes [37][38].

#### 3.3.2 Cluster I2: Herbívoros / Fitófagos

- **Orugas defoliadoras de coníferas** (*Thaumetopoea pityocampa* y otros geométridos): Fitófagas de hojas de *Pinus* spp. Ciclo anual o bienal, pupación en suelo [6][11][39].
- **Hemípteros fitófagos** (pulgones en *Vaccinium*, *Nardus*, *Festuca*): Se alimentan de savia, secretan melaza aprovechada por hormigas mutualistas. Reproducción rápida con generaciones partenogenéticas [6][40][39].
- **Ortópteros** (saltamontes de prados alpinos): Fitófagos generalistas de hojas de gramíneas. Ciclo anual, huevos depositados en el suelo [6][16][41].

#### 3.3.3 Cluster I3: Depredadores / Parasitoides

- **Hormigas** (Formicidae, ej. *Formica* spp.): Omnívoras, consumen melaza de pulgones, pequeños artrópodos, carroña y semillas. Colonia perenne con reinas longevas [6][41][4].
- **Himenópteros parasitoides** (Ichneumonidae, Braconidae): Parasitan larvas de lepidópteros, dípteros y otros órdenes. Control denso-dependiente sobre mariposas y otros fitófagos [4][5][26].
- **Arañas de prados y matorrales** (Araneae): Depredadoras generalistas de insectos en prados y matorrales [6][40][4].

El cluster I3 funciona como un "compartimento regulador" que reduce la eficiencia de conversión de biomasa de fitófagos en presas para vertebrados [6].

### 3.4 Especies de Vertebrados

Se incluyeron 22 especies/taxones de vertebrados en el modelo, seleccionadas por su representatividad de los principales niveles tróficos y su relevancia ecológica en el PNAP. Para cada especie se recopilaron datos taxonómicos, tróficos, reproductivos, morfométricos, energéticos y de conservación, detallados en el **Anexo A** (Fichas de Especies). La Tabla 1 resume los atributos clave de entrada al modelo:

| Especie | Taxón | Masa (kg) | Dieta (P/I/V %) | DEE (kcal/día) | Nivel trófico |
|---------|-------|-----------|-----------------|----------------|---------------|
| *Rupicapra pyrenaica* | Mammalia | 32.5 | 92/5/3 | 1,905.6 | Herbívoro |
| *Cervus elaphus* | Mammalia | 200.0 | 95/3/2 | 7,445.6 | Herbívoro |
| *Capreolus capreolus* | Mammalia | 20.0 | 96/3/1 | 1,324.0 | Herbívoro |
| *Sus scrofa* | Mammalia | 100.0 | 60/20/20 | 4,427.2 | Omnívoro |
| *Ursus arctos* | Mammalia | 150.0 | 40/30/30 | 6,000.6 | Omnívoro |
| *Lutra lutra* | Mammalia | 9.5 | 0/10/90 | 757.6 | Carnívoro |
| *Galemys pyrenaicus* | Mammalia | 0.015 | 0/100/0 | 6.0 | Insectívoro |
| *Martes martes* | Mammalia | 1.5 | 0/20/80 | 189.8 | Carnívoro |
| *Vulpes vulpes* | Mammalia | 6.0 | 10/30/60 | 536.7 | Omnívoro |
| *Felis silvestris* | Mammalia | 4.0 | 5/15/80 | 396.0 | Carnívoro |
| *Mustela nivalis* | Mammalia | 0.08 | 0/20/80 | 21.1 | Carnívoro |
| *Mustela erminea* | Mammalia | 0.15 | 0/20/80 | 33.7 | Carnívoro |
| *Marmota marmota* | Mammalia | 4.55 | 95/5/0 | 396.0 | Herbívoro |
| *Oryctolagus cuniculus* | Mammalia | 1.2 | 95/5/0 | 189.8 | Herbívoro |
| *Meles meles* | Mammalia | 11.0 | 30/40/30 | 757.6 | Omnívoro |
| *Sciurus vulgaris* | Mammalia | 0.3 | 80/20/0 | 33.7 | Herbívoro |
| *Ovis aries musimon* | Mammalia | 37.5 | 98/2/0 | 1,905.6 | Herbívoro |
| *Dama dama* | Mammalia | 57.5 | 98/2/0 | 4,427.2 | Herbívoro |
| *Tetrao urogallus* | Aves | 4.25 | 40/40/20 | 414.4 | Omnívoro |
| *Lagopus muta* | Aves | 0.5 | 80/20/0 | 83.2 | Herbívoro |
| *Gypaetus barbatus* | Aves | 5.5 | 0/0/100 | 502.8 | Carroñero |
| *Aquila chrysaetos* | Aves | 4.0 | 0/10/90 | 396.0 | Carnívoro |
| *Iberolacerta aurelioi* | Reptilia | 0.015 | 0/100/0 | 6.0 | Insectívoro |
| *Calotriton asper* | Amphibia | 0.0075 | 0/100/0 | 3.6 | Carnívoro |
| *Rana temporaria* | Amphibia | 0.025 | 0/100/0 | 8.8 | Insectívoro |
| *Salmo trutta* | Actinopterygii | 1.25 | 0/40/60 | 165.5 | Carnívoro |
| *Phoxinus spp.* | Actinopterygii | 0.03 | 0/80/20 | 10.1 | Omnívoro |

**Tabla 1:** Resumen de especies de vertebrados incluidas en el modelo. P/I/V = porcentaje de plantas, invertebrados y vertebrados en la dieta. DEE = Gasto Energético Diario estimado. Fuentes detalladas en Anexo A.

### 3.5 Red Trófica

Se construyó una **matriz trófica** con 103+ interacciones documentadas [78], clasificando cada relación por tipo (depredación, herbivoría, frugivoría, carroñero, entomofagia, parasitoidismo, mutualismo, canibalismo, detritivoría) y por nivel de confianza (alto/medio/bajo) [78].

A partir de esta matriz, se generó un **grafo dirigido** representando toda la red trófica [79]:
- **66 nodos** (50 especies, 6 clusters funcionales, 10 nodos de recurso generales)
- **121 aristas** (43 especie-a-especie, 60 especie-a-recurso-general, 18 pertenencias a cluster)
- **13 tipos de interacción** diferentes

El grafo es completamente conexo (un solo componente), lo que indica una red trófica integrada sin subredes aisladas [79]. El grafo se exportó en dos formatos: JSON estándar para análisis [79] y JSON optimizado para procesamiento eficiente [80].

![Xarxa Tròfica del Parc Natural de l'Alt Pirineu](trophic_network_graph.png)

**Figura 1:** Grafo dirigido de la red trófica del PNAP (75 nodos, 191 aristas). Los nodos se colorean por grupo taxonómico y el tamaño refleja su nivel de agregación (clusters funcionales mayores, especies individuales menores). El layout responde al algoritmo Kamada-Kawai, minimizando el cruce de aristas. La red constituye un único componente conexo, evidenciando la integración trófica del ecosistema.

### 3.6 Cálculos Energéticos

#### 3.6.1 Gasto Energético Diario (DEE)

El DEE se estimó para cada especie utilizando la ley de Kleiber modificada por taxón [81][82]:

$$ \text{BMR} = a \cdot M^b $$

donde \(M\) es la masa corporal en kg, y \(a, b\) son parámetros taxonómicos específicos [83]:

| Grupo taxonómico | a (kcal·día⁻¹·kg⁻ᵇ) | b | Fuente |
|-----------------|---------------------|----|--------|
| Mamíferos | 70 | 0.75 | Kleiber 1932 [81]; PanTHERIA [7] |
| Aves | 129 | 0.67 | Aschoff & Pohl 1970; EltonTraits [8] |
| Reptiles | 0.16 | 0.88 | Huey & Kingsolver 1989 [84] |
| Anfibios | 0.20 | 0.80 | Lillywhite et al. 1973 [85] |
| Peces (Actinopterygii) | 0.13 | 0.80 | Jobling 1994 [86] |

El DEE se calculó como:

$$ \text{DEE} = \text{BMR} \times \text{FAct} $$

con un factor de actividad (FAct) inicial de **2.0** para todas las especies (forrajeo moderado), basado en Nagy (2005) [87]. Este valor es una primera aproximación que deberá refinarse por especie y estación [50].

El cálculo se realizó mediante un script en Python que procesa el archivo `vertebrates.tsv`, tomando el punto medio del rango de masa corporal y aplicando los parámetros alométricos correspondientes [50].

#### 3.6.2 Costos de Actividad

Se modelizaron 19 comportamientos con sus costos metabólicos específicos, utilizando valores MET (Metabolic Equivalent of Task) y exponentes de masa [88]:

| ID Actividad | Descripción | MET | Exponente | Fuente |
|-------------|-------------|-----|-----------|--------|
| FORAGE_SEARCH | Búsqueda de alimento | 3.0 | 0.75 | Shipley 1999 [89] |
| FORAGE_INTAKE | Ingestión de alimento | 1.5 | 0.75 | Shipley 1999 [89] |
| LOCO_WALK_SLOW | Caminar lento (~1 km/h) | 2.0 | 0.75 | Pontzer 2017 [90] |
| LOCO_WALK_MOD | Caminar moderado (~2 km/h) | 2.5 | 0.75 | Pontzer 2017 [90] |
| LOCO_WALK_FAST | Caminar rápido (~3.5 km/h) | 3.0 | 0.75 | Pontzer 2017 [90] |
| LOCO_TROT | Trote | 4.5 | 0.70 | Hoyt & Williams 1983 [91] |
| LOCO_GALLOP | Galope / carrera | 7.0 | 0.70 | Roberts et al. 2010 [92] |
| LOCO_SWIM | Natación | 6.0 | 0.80 | Jobling 1994 [86] |
| LOCO_CLIMB | Escalada | 5.0 | 0.75 | Kiddo et al. 2015 |
| VIGILANCE | Vigilancia | 1.3 | 0.75 | Elgar 1989 [93] |
| REPRO_COURTSHIP | Cortejo y apareamiento | 2.5 | 0.75 | Speakman 2008 [94] |
| REPRO_GESTATION | Gestación | 1.3 | 0.75 | Blanc et al. 2015 |
| REPRO_LACTATION | Lactancia | 3.0 | 0.75 | Oftedal 2000 [95] |
| TERMO_SHIVERING | Termorregulación (frío) | 2.0 | 0.75 | Angilletta 2009 [96] |
| TERMO_PANTING | Jadeo (calor) | 1.5 | 0.75 | Angilletta 2009 [96] |
| RESTING | Reposo | 1.0 | 0.75 | Kleiber 1932 [81] |
| GROOMING | Acicalado | 1.5 | 0.75 | Moore et al. 2005 |
| SOCIAL_INTERACTION | Interacciones sociales | 1.8 | 0.75 | Barash 2003 |

#### 3.6.3 Energía de los Recursos

Se recopilaron valores calóricos (kcal/g de peso húmedo) para diferentes tipos de recursos tróficos [97], utilizando principalmente la base USDA FoodData Central [9]:

| Tipo de recurso | Subtipo | kcal/g húmedo | Rango | Fuente |
|----------------|---------|--------------|-------|--------|
| Plantas | Hoja tierna | 0.30 | 0.20-0.40 | USDA [9] |
| Plantas | Hoja madura fibrosa | 0.20 | 0.10-0.30 | USDA [9] |
| Plantas | Fruto carnoso (bayas) | 0.80 | 0.60-1.00 | USDA [9] |
| Plantas | Fruto seco (nuez) | 5.50 | 4.50-6.50 | USDA [9] |
| Plantas | Raíz/tubérculo | 0.40 | 0.30-0.50 | USDA [9] |
| Invertebrados | Lepidoptera larva | 5.00 | 4.50-5.50 | Sloan et al. 2019 [98] |
| Invertebrados | Coleoptera adulto | 4.80 | 4.20-5.20 | Sloan et al. 2019 [98] |
| Invertebrados | Araneae | 4.50 | 4.00-5.00 | Greenstone & Bennett 1980 [99] |
| Invertebrados | Formicidae obrera | 4.20 | 3.80-4.60 | Lighton & Wehner 1993 [100] |
| Invertebrados | Oligochaeta (lombriz) | 3.80 | 3.50-4.20 | Bouché 1977 [101] |
| Vertebrados | Músculo magro | 1.20 | 1.00-1.40 | USDA [9] |
| Vertebrados | Grasa subcutánea/visceral | 9.30 | 8.50-10.00 | USDA [9] |
| Vertebrados | Hígado | 1.60 | 1.40-1.80 | USDA [9] |

#### 3.6.4 Proporciones de Dieta

Para cada especie y cluster funcional, se estimaron las proporciones de la dieta en términos de porcentaje de planta/invertebrado/vertebrado [51]. El procedimiento combinó:

1. **Clasificación de recursos** a partir de la columna `main_diet` de `vertebrates.tsv` [44] y la matriz trófica [78]
2. **Ponderación por confianza** de cada interacción (alta=1.0, media=0.5, baja=0.25)
3. **Normalización** a 1 (100%) para obtener la proporción de cada recurso en la dieta

Las proporciones detalladas para cada especie se incluyen en las tablas de la Sección 3.4.

### 3.7 Visualizador Interactivo

Se desarrolló un **visualizador interactivo de la red trófica** en HTML/CSS/JavaScript autónomo [102], que utiliza un layout de fuerzas (force-directed graph) para representar la topología de la red. El visualizador permite:
- Filtrar por tipo de interacción (13 tipos)
- Seleccionar nodos con panel de información detallada
- Visualizar estadísticas en tiempo real (nodos, aristas, densidad)
- Explorar la red con zoom y arrastre

### 3.8 Arquitectura del Simulador

El simulador se implementó en **Python 3.12** con **Numba JIT** para aceleración de operaciones matemáticas, siguiendo una arquitectura orientada a agentes con planificación GOAP (Goal-Oriented Action Planning). El código fuente comprende aproximadamente 1.700 líneas distribuidas en los siguientes módulos:

#### 3.8.1 Terreno y Espacio

Se utiliza un modelo digital de elevación (DEM) SRTM de 30 m remuestreado a 25 m (EPSG:25831), procesado mediante `src/process_terrain.py` para derivar capas de pendiente (Slope), aspecto (Aspect), índice de rugosidad (TRI), y pisos bioclimáticos (montano, subalpino, alpino, nival). La clasificación de hábitats se realiza mediante el script `src/process_mcsc.py`, que descarga datos MCSC (Mapa de Cubiertas del Suelo de Cataluña) vía WFS del ICGC y traduce 44 clases originales a **10 tipos funcionales** (bosque denso coníferas, bosque denso frondosas, bosque mixto, matorral, prado, roquedo, suelo desnudo, agua, nieve, zona urbana). Cada celda de 25 m contiene valores de elevación, pendiente, aspecto, TRI, piso bioclimático, tipo de hábitat y biomasa inicial para los clusters de plantas e invertebrados.

La zona de simulación actual es la **subcuenca de Vall de Cardós**, con aproximadamente 2.500 celdas (~1.560 ha). El objetivo es escalar al PNAP completo (~80.000 ha, ~180.000 celdas).

#### 3.8.2 Agentes

Se definen 4 clases de agente que heredan de una clase base `Agent`:

- **HerbivoreAgent**: pastoreo, movimiento hacia parches de alta biomasa vegetal, umbral de energía para reproducción.
- **CarnivoreAgent**: caza en celdas con alta biomasa de invertebrados, mayor rango de movimiento.
- **OmnivoreAgent**: combina estrategias de herbívoro y carnívoro según disponibilidad.
- **BirdAgent**: versión simplificada con mayor movilidad y menor coste energético.

Cada agente contiene:

| Componente | Descripción |
|-----------|-------------|
| `AgentState` | Energía (kcal), edad (días), alive, is_lactating, last_reproduced |
| `AgentGenetics` | Masa corporal (kg), tasa metabólica, eficiencia de conversión |
| `AgentPosition` | Coordenadas (x, y) en la cuadrícula |
| `goap_memory` | Plan de acciones GOAP (cola de acciones a ejecutar) |

#### 3.8.3 GOAP y Toma de Decisiones

Cada agente implementa un planificador GOAP (Goal-Oriented Action Planning) que evalúa su estado interno y el entorno para seleccionar un plan de acciones. La decisión sigue umbrales energéticos específicos por nivel trófico:

**Evaluación de metas:**
$$
\text{meta} = \begin{cases}
\text{findEnergy()} & \text{si } E < E_{\text{umbral}} \\
\text{findFood()} & \text{si } \text{recursos}_{celda} < \text{consumo}_{\text{máx}} \\
\text{reproduce()} & \text{si } E > E_{\text{repro}} \text{ y época reproductiva} \\
\text{explore()} & \text{en caso contrario}
\end{cases}
$$

**Umbrales de reproducción** (energía mínima para reproducirse):
$$
E_{\text{repro}} = \begin{cases}
2000 \cdot M & \text{herbívoros} \\
2500 \cdot M & \text{omnívoros} \\
3000 \cdot M & \text{carnívoros}
\end{cases}
\quad [\text{kcal}]
$$

Además, la reproducción requiere que hayan transcurrido al menos 365 días desde la última reproducción y que la hembra no esté gestante.

**Selección de celda de forrajeo** (función de puntuación maximizada):
$$
S(x,y) = \frac{B_{\text{plant}}(x,y) + 2 \cdot B_{\text{invert}}(x,y)}{\max(C_{\text{path}}(x,y),\; 0.1)}
$$

donde \(B_{\text{plant}}\) e \(B_{\text{invert}}\) son las biomasas disponibles, y \(C_{\text{path}}\) es el coste de desplazamiento A*. El radio de búsqueda es de 5 celdas para herbívoros y omnívoros, 8 para carnívoros y 15 para aves.

#### 3.8.4 Balance Energético

**Gasto Basal (Kleiber):**
$$
\text{BMR} = a \cdot M^{b} \quad [\text{kcal/día}]
$$

con parámetros taxonómicos \(a, b\) especificados en la Sección 3.6.1.

**Costo de actividad por MET:**
$$
C_a = \text{MET}_a \cdot \text{BMR}_{\text{hora}} \cdot t_a
$$

donde \(\text{BMR}_{\text{hora}} = \text{BMR} / 24\) y \(t_a\) son las horas dedicadas a la actividad \(a\). Para locomoción, el MET depende de la pendiente:

$$
\text{MET}_{\text{loco}}(s) = \begin{cases}
2.5 & s < 5^\circ \\
3.0 & 5^\circ \leq s < 15^\circ \\
5.0 & 15^\circ \leq s < 30^\circ \\
6.0 & s \geq 30^\circ
\end{cases}
$$

**Gasto Energético Diario total (DEE):**
$$
\text{DEE} = \text{BMR}_{\text{hora}} \left[ \text{MET}_{\text{loco}} \cdot t_{\text{loco}} + 2.0 \cdot t_{\text{forrajeo}} + 1.0 \cdot t_{\text{reposo}} + 1.5 \cdot t_{\text{otro}} \right]
$$

con presupuestos temporales por defecto: \(t_{\text{loco}} = 2\text{h}\), \(t_{\text{forrajeo}} = 6\text{h}\), \(t_{\text{reposo}} = 12\text{h}\), \(t_{\text{otro}} = 4\text{h}\). Si hay lactancia, el DEE se multiplica por 1.4. Si hay estrés por frío, se añaden 2 horas a MET 2.0.

Sustituyendo los valores por defecto (terreno llano, sin lactancia, sin frío):
$$
\text{DEE}_{\text{default}} = 102.08 \cdot M^{0.75} \quad [\text{kcal/día}]
$$

**Actualización de energía por paso temporal:**
$$
E_{t+1} = E_t + \eta \cdot I - \text{DEE} \cdot \frac{\Delta t}{24}
$$

donde \(\eta\) es la eficiencia de asimilación (0.6 para herbívoros, 0.8 para carnívoros), \(I\) la ingesta calórica total (kcal), y \(\Delta t\) el intervalo de tiempo en horas (24 h por defecto).

**Muerte por inanición:** si \(E_t \leq 0\), el agente muere.

**Muerte por senescencia:** si \(\text{edad}_{\text{días}} \geq 3650\) (10 años), el agente muere.

**Energía inicial:** \(E_0 = 5000 \cdot M\) kcal.

#### 3.8.5 Forrajeo y Consumo

Cuando un agente forrajea en una celda, consume biomasa de los pools disponibles:

$$
I_{\text{kg}} = \min\left( B_{\text{disp}},\; 0.05 \cdot M \right)
$$

donde \(B_{\text{disp}} = \sum_{i=1}^{3} P_i + \sum_{j=1}^{3} I_j\) es la biomasa total disponible en la celda.

La biomasa consumida se reparte proporcionalmente entre los pools:

$$
f_{\text{plant}} = \frac{\sum P_i}{B_{\text{disp}}}, \quad f_{\text{invert}} = 1 - f_{\text{plant}}
$$

Con extracción específica de cada sub-pool según fracciones fijas: las plantas se extraen en proporción (P1: 50\%, P2: 20\%, P3: 30\%) y los invertebrados en proporción (I1: 30\%, I2: 50\%, I3: 20\%).

**Conversión calórica** (valores por kg consumido):
- Plantas: 800 kcal/kg (eficiencia asimilación 60\% → 480 kcal/kg netas)
- Invertebrados: 2000 kcal/kg (eficiencia asimilación 80\% → 1600 kcal/kg netas)
- Vertebrados: 1500 kcal/kg (eficiencia asimilación 80\% → 1200 kcal/kg netas)

#### 3.8.6 Movimiento y Pathfinding (A*)

El movimiento utiliza el algoritmo A* con una función heurística de distancia euclidiana:

$$
h(a,b) = \sqrt{(a_x - b_x)^2 + (a_y - b_y)^2}
$$

El coste de movimiento a una celda vecina es:

$$
C_{\text{move}}(n) = C_{\text{base}}(s_n) \cdot f_{\text{nieve}}(n) \cdot f_{\text{terreno}}(n) \cdot d_{\text{diag}}
$$

donde:
- \(C_{\text{base}}(s)\) depende de la pendiente \(s\) de la celda destino:
  $$
  C_{\text{base}}(s) = \begin{cases}
  1.0 & s < 5^\circ \\
  1.5 & 5^\circ \leq s < 15^\circ \\
  2.5 & 15^\circ \leq s < 30^\circ \\
  3.5 & s \geq 30^\circ
  \end{cases}
  $$
- \(f_{\text{nieve}} = 1 + \text{snow\_cover}\) (rango [1.0, 2.0])
- \(f_{\text{terreno}}\) varía por hábitat: bosque=1.3, matorral=1.0, pastizal=1.0, roca=1.6, agua=3.0
- \(d_{\text{diag}} = \sqrt{2} \approx 1.414\) para movimientos diagonales (1.0 para ortogonales)

La función de puntuación A* es:
$$
f(n) = g(n) + h(n, \text{objetivo})
$$

donde \(g(n)\) es el coste acumulado desde el inicio y \(h\) la heurística al objetivo. El algoritmo converge en máximo 5000 iteraciones.

#### 3.8.7 Dinámica de Vegetación e Invertebrados

**Crecimiento vegetal** (modelo logístico por celda):

$$
\Delta P_i = r_i \cdot g(s) \cdot P_i^{\text{máx}} \quad \text{para } i = 1,2,3
$$

con la restricción \(0 \leq P_i \leq P_i^{\text{máx}}\). No hay crecimiento en celdas de agua, nieve o roca.

| Pool | \(r_i\) (tasa crecimiento) | \(P_i^{\text{máx}}\) (kg/celda) |
|------|---------------------------|-------------------------------|
| P1 (entomófilas) | 0.02 | 2.0 |
| P2 (independientes) | 0.015 | 1.5 |
| P3 (pastizales) | 0.03 | 5.0 |

**Dinámica de invertebrados** (acoplada a biomasa vegetal):

$$
\begin{aligned}
\Delta I_1 &= r_{I1} \cdot g(s) \cdot P_1 \cdot 0.1 \\
\Delta I_2 &= r_{I2} \cdot g(s) \cdot P_3 \cdot 0.08 \\
\Delta I_3 &= r_{I3} \cdot g(s) \cdot I_2 \cdot 0.2
\end{aligned}
$$

| Pool | \(r_{Ij}\) | \(I_j^{\text{máx}}\) (kg/celda) |
|------|-----------|-------------------------------|
| I1 (polinizadores) | 0.01 | 0.5 |
| I2 (fitófagos) | 0.015 | 0.8 |
| I3 (depredadores) | 0.008 | 0.3 |

**Factor estacional \(g(s)\):**

$$ g(s) = \begin{cases}
1.0 & \text{verano} \\
0.8 & \text{primavera} \\
0.5 & \text{otoño} \\
0.1 & \text{invierno}
\end{cases} $$

**Consumo por pastoreo:** Cuando los agentes forrajean, reducen los pools según lo descrito en 3.8.5.

#### 3.8.8 Dinámica de Pools Poblacionales

Siete pools representan la biomasa agregada de grupos no modelados como agentes individuales. Crecen según:

$$
\frac{dB}{dt} = r_{\text{pool}} \cdot g(s) \cdot B
$$

| Pool | \(r_{\text{pool}}\) | Notas |
|------|-------------------|-------|
| Trucha (*Salmo trutta*) | 0.01 | Capacidad de carga: 200 kg/km de río |
| Piscardo (*Phoxinus spp.*) | 0.015 | Capacidad: 30\% del máximo de peces |
| Reptiles + Anfibios | 0.008 | Anfibios crecen 1.2× más rápido |
| Passeriformes | 0.01 | — |
| Micromamíferos | 0.02 | La tasa más alta |
| Murciélagos | 0.005 | La tasa más baja |

La capacidad de carga piscícola se calcula como:

$$
K_{\text{fish}} = L_{\text{río}} \cdot 200 \text{ kg/km}
$$

donde \(L_{\text{río}} = N_{\text{celdas-agua}} \times 25 \text{ m} / 1000\).

#### 3.8.9 Clima y Nieve

**Temperatura** (gradiente adiabático + onda estacional):

$$
T(z, d) = 5.0 + 10.0 \cdot \cos\left(\frac{2\pi(d - 182)}{365}\right) - 0.0065 \cdot \max(0, z - 1000)
$$

donde \(z\) es la elevación en metros y \(d\) el día del año (0–364). La temperatura base es 5°C, con amplitud estacional de ±10°C y gradiente adiabático de −6.5°C/km por encima de 1000 m.

**Nieve:**

$$
\text{snow\_line}(d) = 2400 + 300 \left[ 1 + \cos\left(\frac{2\pi(d - 15)}{365}\right) \right] \quad [\text{m}]
$$

$$
\text{snow\_cover}(z, d) = \begin{cases}
0 & z < \text{snow\_line} \\
\min\left(1.0,\; \dfrac{z - \text{snow\_line}}{800}\right) & z \geq \text{snow\_line}
\end{cases}
$$

La línea de nieve oscila entre 2400 m (verano) y 3000 m (invierno). El factor 800 m es la banda de transición: a 800 m por encima de la línea, la cobertura es 1.0.

#### 3.8.10 Reproducción y Mortalidad

**Eventos de nacimiento:** Solo ocurren en primavera y verano. Una hembra lactante pare cuando han transcurrido menos de 60 días desde el último parto:

$$
\text{camada} = \mathcal{U}\{1, 2\} \quad (\text{uniforme discreta entre 1 y 2})
$$

La cría aparece en una celda adyacente (\(\pm 2\) celdas en x, y) con masa inicial:

$$
M_{\text{cría}} = M_{\text{progenitor}} \cdot \mathcal{U}(0.05, 0.15)
$$

**Gestación:** Dura 150 días. Al completarse, se reinician los contadores y se activa el estado de lactancia.

**Crecimiento:** La edad avanza fraccionalmente: \(edad += \Delta t / 24\).

#### 3.8.11 Implementación y Rendimiento

El simulador se ejecuta en pasos de tiempo diarios, con los siguientes hitos de rendimiento:

| Configuración | Agentes | Días | Tiempo | Supervivientes |
|--------------|---------|------|--------|---------------|
| Quick | 324 | 20 | ~1 min | 324 (100\%) |
| Medium | 1.315 | 360 | ~30 min | 120 (9.1\%) |
| Deep | 6.185 | 10 | ~15 min | 6.185 (100\%) |

El cuello de botella principal es el bucle de decisión GOAP y el acceso a la cuadrícula por agente. Se ha documentado una estrategia híbrida **Python-Rust** (PyO3) en `HYBRID_APPROACH.md` para migrar operaciones matemáticas batch (energía, forrajeo, búsqueda de vecinos) a Rust, manteniendo la lógica de decisión en Python. Esta optimización está planificada pero no es crítica para los resultados actuales.

#### 3.8.12 Limitaciones Actuales

El análisis post-simulación reveló varios gaps entre el diseño y la implementación:

1. **Dietas no conectadas**: las proporciones de dieta definidas en `foodweb.py` no se utilizan en el forrajeo. Todos los agentes consumen biomasa vegetal e invertebrada proporcionalmente a su disponibilidad en la celda, resultando funcionalmente omnívoros.
2. **Sin depredación agente-a-agente**: los carnívoros cazan `cell.total_invert_biomass` (pools de invertebrados), no otros objetos `Agent`. Los depredadores superiores (águila, marta, zorro) no ejercen presión trófica real sobre herbívoros.
3. **Pools desconectados**: los pools de peces, herps, passeriformes, micromamíferos y murciélagos crecen estacionalmente pero ningún agente los consume.
4. **Temperatura hardcodeada**: el parámetro `is_cold=False` elimina el estrés energético invernal.
5. **Reproducción incompleta**: el método `_should_reproduce()` nunca se llama; los nacimientos dependen exclusivamente del timer de lactancia.

Estas limitaciones constituyen la hoja de ruta prioritaria para la siguiente fase del desarrollo.

### 3.9 Mapas de Terreno

Se generaron 15 mapas del área de estudio a partir del DEM SRTM 30 m remuestreado a 25 m, utilizando `src/visualize_terrain.py` y `src/visualize_terrain_3d.py`:

![Mapa de elevación (DEM)](../../output/maps/terrain_dem.png)
**Figura 2a:** Modelo digital de elevación (DEM) de la subcuenca de Vall de Cardós. Rango altitudinal: ~1.200–2.800 m. Escala de color "terrain" de matplotlib.

![Mapa de pendiente](../../output/maps/terrain_slope.png)
**Figura 2b:** Pendiente en grados. Escala YlOrRd, recortada a 0–60°. Las zonas más escarpadas corresponden a los circos glaciares y barrancos.

![Mapa de aspecto](../../output/maps/terrain_aspect.png)
**Figura 2c:** Orientación de las laderas (0–360°). Escala cíclica "twilight". La orientación determina la insolación recibida y, por tanto, la distribución de hábitats y la fenología.

![Índice de rugosidad del terreno](../../output/maps/terrain_tri.png)
**Figura 2d:** Terrain Ruggedness Index (TRI). Escala "Greys". Mide la heterogeneidad topográfica, relevante para la diversidad de microhábitats.

![Pisos bioclimáticos](../../output/maps/terrain_pisos.png)
**Figura 3a:** Pisos bioclimáticos clasificados por altitud: Montano (verde), Subalpino (azul), Alpino (naranja), Nival (rojo). Cada piso alberga comunidades ecológicas distintas.

![Hábitats funcionales](../../output/maps/terrain_habitat.png)
**Figura 3b:** Mapa de hábitats funcionales (10 clases derivadas del MCSC). Los bosques de coníferas dominan las laderas medias, mientras que los prados alpinos ocupan las cotas superiores.

![Biomasa de plantas entomófilas (P1)](../../output/maps/terrain_biomass_P1.png)
**Figura 4a:** Biomasa inicial del cluster P1 (plantas entomófilas de sotobosque y prados floridos). Las zonas de mayor biomasa se concentran en los bosques de media montaña.

![Biomasa de plantas independientes (P2)](../../output/maps/terrain_biomass_P2.png)
**Figura 4b:** Biomasa inicial del cluster P2 (productores independientes acuáticos y esporófitos). Asociada a cursos de agua y zonas húmedas.

![Biomasa de pastizales (P3)](../../output/maps/terrain_biomass_P3.png)
**Figura 4c:** Biomasa inicial del cluster P3 (pastizales y praderas). Máxima en los prados alpinos y subalpinos, base de la dieta de grandes herbívoros.

![Biomasa de invertebrados polinizadores (I1)](../../output/maps/terrain_biomass_I1.png)
**Figura 4d:** Biomasa inicial del cluster I1 (polinizadores mutualistas). Correlacionada con la densidad de plantas entomófilas (P1).

![Biomasa de invertebrados fitófagos (I2)](../../output/maps/terrain_biomass_I2.png)
**Figura 4e:** Biomasa inicial del cluster I2 (herbívoros/fitófagos). Máxima en zonas de alta productividad vegetal.

![Biomasa de invertebrados depredadores (I3)](../../output/maps/terrain_biomass_I3.png)
**Figura 4f:** Biomasa inicial del cluster I3 (depredadores/parasitoides). Sigue la distribución de sus presas (I2).

![Vista 3D del terreno](../../output/maps/terrain_3d.png)
**Figura 5a:** Vista 3D del terreno (azimut 315°, elevación 25°, exageración vertical 2×). La coloración sigue la elevación (cmap="terrain").

![Vista 3D baja](../../output/maps/terrain_3d_low.png)
**Figura 5b:** Vista 3D alternativa (azimut 225°, elevación 10°), ofreciendo una perspectiva más raseera del relieve.

![Dashboard de terreno](../../output/maps/terrain_dashboard.png)
**Figura 5c:** Panel compuesto 3×3 con DEM, pendiente, aspecto, TRI, pisos bioclimáticos, hábitat, biomasa P1, biomasa P3 y biomasa I1. Proporciona una visión sinóptica de las variables del terreno.

---

## 4. Resultados

### 4.1 Simulaciones Exploratorias

Se ejecutaron simulaciones sobre la subcuenca de Vall de Cardós (~2.500 celdas) con tres configuraciones de agente y duración:

| Configuración | Agentes iniciales | Duración (días) | Supervivientes | Biomasa inicial (kg) | Biomasa final (kg) |
|--------------|------------------|----------------|---------------|--------------------|-------------------|
| Quick | 324 | 20 | 324 (100%) | 25.085 | 23.903 |
| Medium | 1.315 | 360 | 120 (9.1%) | 126.866 | 263.077 |
| Deep | 6.185 | 10 | 6.185 (100%) | 561.733 | 556.371 |

La simulación **medium** (1.315 agentes, 360 días) muestra la dinámica más interesante (Tabla 1 y datos completos en Material Suplementario S6).

La mortalidad se concentra entre los días 40 y 260, con una estabilización en ~120 agentes a partir del día 320. La biomasa total aumenta de 126.866 kg a 263.077 kg, indicando que los agentes supervivientes son los de mayor masa corporal (selección de individuos grandes con más reservas). La energía media disminuye de 153.091 kcal a 13.944 kcal, reflejando que incluso los supervivientes operan cerca de su límite energético.

La simulación **deep** (6.185 agentes) solo alcanzó 10 días debido al coste computacional del bucle GOAP por agente.

### 4.2 Limitaciones Detectadas

El análisis de los logs de simulación reveló que los patrones observados no reflejan fielmente la ecología del sistema debido a las limitaciones documentadas en 3.8.7. En particular:

1. Todos los agentes compiten por los mismos recursos (plantas + invertebrados), independientemente de su nicho trófico real.
2. Los carnívoros no ejercen presión de depredación sobre herbívoros, eliminando las cascadas tróficas.
3. La ausencia de estrés invernal suaviza la mortalidad estacional.
4. La reproducción no responde a umbrales ecológicos sino a temporizadores.

Estos resultados constituyen una **línea base** que deberá refinarse conectando la dieta real, implementando depredación agente-a-agente, activando la temperatura estacional y completando el ciclo reproductivo.

---

## 5. Discusión

> *Pendiente — se completará cuando haya resultados para discutir.*

---

## 6. Conclusiones

> *Pendiente — se completará al final del proceso.*

---

## 7. Referencias

### Referencias del área de estudio y parque

1. [El Parc de l'Alt Pirineu comptabilitza 277 espècies diferents de...](https://www.radioseu.cat/noticies/el-parc-de-lalt-pirineu-comptabilitza-277-espacies)
2. [Vint anys de la creació del Parc Natural de l'Alt Pirineu](https://www.comarquesdeponent.com/articulo/documentals/parc-natural-lalt-pirineu/20230817083202070469.html)
3. [Parc Natural de l'Alt Pirineu - Gencat](https://parcsnaturals.gencat.cat/ca/xarxa-de-parcs/alt-pirineu/)
4. [El Parc de l'Alt Pirineu, entre les zones amb més diversitat de papallones d'Europa](https://www.radioseu.cat/noticies/el-parc-de-lalt-pirineu-entre-les-zones-amb-mes-diversitat-de-papallones-deuropa)
5. [L'Alt Pirineu és una de les zones amb més diversitat de papallones d'Europa](https://www.descobrir.cat/noticies/l-alt-pirineu-es-una-de-les-zones-amb-mes-diversitat-de-papallones-d-europa-3598_303598_102.html)

### Referencias de la base de datos biológica maestra

6. Base d'espècies i interaccions tròfiques per a una simulació agent-based al Parc Natural de l'Alt Pirineu (documento maestro, 328 líneas, 76 referencias)

### Referencias de bases de datos globales

7. Jones, K.E., et al. (2009). PanTHERIA: a species-level database of life history, ecology, and geography of extant and recently extinct mammals. *Ecology*, 90(9), 2648.
8. Wilman, H., et al. (2014). EltonTraits 1.0: Species-level foraging attributes of the world's birds and mammals. *Ecology*, 95(8), 2027-2036.
9. USDA FoodData Central. https://fdc.nal.usda.gov/

### Referencias de plantas y vegetación

10. Anàlisi de la interacció entre la gestió forestal i el gall fer (Tetrao urogallus). TFG UAB, 2017. [PDF]
11. Gall fer - Documentació Cerdanya. [PDF]
12. Gall fer comú - Viquipèdia. https://ca.wikipedia.org/wiki/Gall_fer_com%C3%BA
13. Orsis 24_2. [PDF] - Plantas alpinas y fenología. https://www.raco.cat/index.php/Orsis/article/download/181222/233873
14. Prats Alpins dels Nivells Culminals - Natura al Berguedà. http://www.naturabergueda.com/Flora/Paisatges_vegetals/Prats_Alpins_dels_Nivells_Culminals-76.htm
15. Astragalus penduliflorus - Referencias del PNAP.
16. Els prats alpins als Pirineus catalans. *Atzavara*. https://www.raco.cat/index.php/Atzavara/article/download/436841/531254
17. 36c Prats de pèl caní (Nardus stricta). Gencat. http://www.gencat.cat/mediamb/habitats/fitxespdf/mill36c.pdf
18. Bestiari fòssil - ICP. https://bestiarifossil.icp.cat/
19. Reptes per preservar els boscos madurs a Catalunya. IEC. https://ichn2.iec.cat/pdf/Boscos_madurs_Catalunya.pdf
20. Resum d'actuacions i activitats - PNAP. Gencat. https://mediambient.repositori.gencat.cat/bitstream/handle/20.500.14343/241/2024_MB_PNAltPirineu.pdf
21. La alimentación del sarrio en el Pirineo central. CSIC. https://digital.csic.es/handle/10261/36788
22. La vegetació de la nostra comarca - Prats i pastures. https://sites.google.com/site/vegetaciodelsolsones/sabeu-que/els-ecosistemes/prats-i-pastures
23. Parc Natural de l'Alt Pirineu - CampingsCat. https://campingscat.com/ca/que-fer-catalunya/parcs-naturals/parc-natural-alt-pirineu/
24. Els ungulats de la Reserva - La brama del cérvol. https://www.bramaaltpallars.cat/ungulats-reserva/
25. Flora i fauna - Vall de Cardós. http://valldecardos.cat/mobile/la-vall-de-cardos/flora-i-fauna/

### Referencias de invertebrados

26. Presentem la Guia i Pòster de les Voliaines i Plantes de prats de pastura de l'Alt Pirineu. https://www.catalanbms.org/ca/noticies/presentem-la-guia-i-poster-de-les-voliaines-i-plantes-de-prats-de-pastura-de-l-alt-pirineu/
27. Descobertes a l'alt Pirineu dues espècies de papallones mai vistes a Catalunya. https://www.3cat.cat/3catinfo/descobertes-a-lalt-pirineu-dues-especies-de-papallones-mai-vistes-a-catalunya/noticia/2990022/
28. Bistorta - Viquipèdia. https://ca.wikipedia.org/wiki/Polygonum_bistorta
29. Lepidoptera Mundi. https://lepidoptera.eu/species/38
30. European Lepidoptera: Boloria eunomia. http://www.pyrgus.de/Boloria_eunomia_en.html
31. Parnassius mnemosyne - Butterflies of Europe. Naturalis.
32. Parnassius mnemosyne – Niepylak mnemozyna. https://insektarium.net/
33. Parnassius mnemosyne. http://www.pyrgus.de/Parnassius_mnemosyne_en.html
34. Presentem la Guia i Pòster de les Voliaines. English version. https://www.catalanbms.org/en/noticies/presentem-la-guia-i-poster-de-les-voliaines-i-plantes-de-prats-de-pastura-de-l-alt-pirineu/
35. Lepidòpters - Museu de Ciències Naturals de Granollers. https://mcng.cat/blog/categoria/lepidopters
36. Prats alpins - Catalan BMS. https://www.catalanbms.org/ca/habitats/23/
37. PIPOL - Pla Intersectorial de conservació dels Pol·linitzadors Silvestres de Catalunya. Gencat. https://mediambient.repositori.gencat.cat/
38. PIPOL - Scribd. https://www.scribd.com/document/877587339/
39. Les papallones com a bioindicadores dels hàbitats a Catalunya. IEC. https://publicacions.iec.cat/repository/pdf/00000039/00000085.pdf
40. Informe sobre l'estat i les tendències del medi natural a Catalunya. ICHN. https://defensapatrimoninatural.wordpress.com/
41. La sargantana pallaresa - Enciclopèdia. https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/la-sargantana-pallaresa

### Referencias de vertebrados

42. Rupicapra pyrenaica Bonaparte, 1845. MITECO. https://www.miteco.gob.es/
43. Isard - Enciclopèdia. https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/isard
44. vertebrates.tsv - Base de datos de vertebrados del proyecto (22 especies, datos taxonómicos, tróficos, reproductivos, masa corporal)
45. Isard pirinenc - Viquipèdia. https://ca.wikipedia.org/wiki/Isard_pirinenc
46. Isard - Enciclopèdia Catalana.
47. La alimentación del sarrio en el Pirineo central. CSIC.
48. Os bru - Enciclopèdia. https://www.enciclopedia.cat/historia-natural-dels-paisos-catalans/os-bru
49. Fauna salvatge dels Pirineus. https://www.turismefgc.cat/blog/la-fauna-salvatge-del-pirineu/
50. dee_estimado.tsv - Cálculos de DEE del proyecto (basado en Kleiber, FAct=2.0)
51. dieta_proporciones.tsv - Proporciones de dieta del proyecto
52. Intensifiquen les accions per frenar la davallada de població de gall fer. https://lesvegueries.cat/
53. ATACS D'ÓS BRU (URSUS ARCTOS) A CATALUNYA. ADLO Pirineo. https://www.adlopirineo.org/docuteca/atacosbru.pdf
54. 10 Qüestions sobre l'ós bru - Depana. https://depana.org/
55. Troben una truita gegant de 7 quilos a la Noguera Pallaresa. https://www.3cat.cat/324/
56. L'os bru als Pirineus: passat, present i futur. Gencat. https://accioclimatica.bibliotecadigital.gencat.cat/
57. Quines accions es duen a terme per protegir hàbitats i espècies dels Pirineus i els Alps? CEAB. https://www.ceab.csic.es/
58. Com s'eliminen els peixos introduïts en estanys d'alta muntanya? https://www.prisma-tic.cat/
59. La truita de riu del Pirineu, el peix que no enveja la costa. https://vadegust.cat/
60. El tritó pirinenc - XTEC. https://blocs.xtec.cat/faunaiflora/2010/10/04/el-trito-pirinenc/
61. El Parc de l'Alt Pirineu acull la primera monitorització en directe d'un niu de gall fer. https://www.radioseu.cat/
62. Capercaillie Nest Loss and Attendance at Abernethy Forest, Scotland. *Wildlife Biology*. https://onlinelibrary.wiley.com/doi/10.2981/08-036
63. OBJECTES - Gall fer - Paisatges Vius. https://paisatgesvius.org/ca/objectes/3945
64. Western capercaillie - Wikipedia. https://en.wikipedia.org/wiki/Tetrao_urogallus
65. AnAge entry for Tetrao urogallus. https://genomics.senescence.info/species/entry.php?species=Tetrao_urogallus
66. Why the capercaillie population in mountain... [PDF]. https://ife.sk/
67. Gall fer (Tetrao urogallus) - Muntanyes Vives. https://muntanyesvives.org/gall-fer/
68. Observació de la fauna i flora Parc Natural de l'Alt Pirineu. https://patoupallars.com/
69. El trencalòs augmenta la seva població al PNAP. https://www.3cat.cat/324/
70. Sargantana pallaresa - Viquipèdia. https://ca.wikipedia.org/wiki/Sargantana_pallaresa
71. La calor pot matar l'Aureli(oi) - Diari d'Andorra. https://www.diariandorra.ad/
72. Tritó pirinenc - Viquipèdia. https://ca.wikipedia.org/wiki/Trit%C3%B3_pirinenc
73. Experiments evolutius als llacs d'alta muntanya. MCNG. https://mcng.cat/
74. Espècies introduïdes als estanys - Life Resque AlPyr. https://liferesquealpyr.eu/ca/especies-introduides-als-estanys/
75. Espècies objectiu - Life Resque AlPyr. https://liferesquealpyr.eu/ca/especies-objectiu/
76. Les grans truites tornen a la capçalera del riu Noguera Pallaresa. https://www.segre.com/
77. Inici de la temporada de pesca als rius de Lleida. https://aralleida.cat/

### Referencias de red trófica y visualización

78. trophic_matrix.tsv - Matriz de interacciones tróficas del proyecto (103+ interacciones)
79. ecosystem_graph_standard.json - Grafo de red trófica en formato JSON estándar (66 nodos, 121 aristas)
80. ecosystem_graph_optimized.json - Grafo de red trófica en formato JSON optimizado
81. Kleiber, M. (1932). Body size and metabolism. *Hilgardia*, 6(11), 315-353.
82. Nagy, K.A. (2005). Field metabolic rate and body size. *Journal of Experimental Biology*, 208, 1621-1625.
83. metabolismo_revision.md - Revisión bibliográfica de ecuaciones alométricas por taxón
84. Huey, R.B., & Kingsolver, J.G. (1989). Evolution of thermal heterogeneity in ectotherms. *American Naturalist*, 134, 1-13.
85. Lillywhite, H.B., et al. (1973). The energetics of amphibian movements. *Copeia*, 1973(2), 241-247.
86. Jobling, M. (1994). *Fish Bioenergetics*. Chapman & Hall.
87. Nagy, K.A. (2005). Field metabolic rate and body size. *Journal of Experimental Biology*, 208, 1621-1625.
88. costos_actividad.tsv - Costos de actividad metabólica del proyecto (19 comportamientos)
89. Shipley, B. (1999). *The allometry of foraging behavior*. Princeton University Press.
90. Pontzer, H. (2017). Energy expenditure in humans and other primates: A new synthesis. *Annual Review of Nutrition*, 37, 387-410.
91. Hoyt, D.F., & Williams, K.H. (1983). *Journal of Experimental Biology*.
92. Roberts, T.J., et al. (2010). *Journal of Experimental Biology*.
93. Elgar, M.A. (1989). *Animal Behaviour*.
94. Speakman, J.R. (2008). *Journal of Experimental Biology*.
95. Oftedal, O.T. (2000). *Journal of Mammalogy*.
96. Angilletta, M.J. (2009). *Thermal Adaptation*. Oxford University Press.
97. energia_recursos.tsv - Densidad energética de recursos del proyecto
98. Sloan, et al. (2019). Energy content of Lepidoptera larvae.
99. Greenstone & Bennett (1980). *Journal of Arachnology*.
100. Lighton, J.R.B., & Wehner, R. (1993). *Journal of Experimental Biology*.
101. Bouché, M.B. (1977). *Revue d'Écologie et de Biologie du Sol*.
102. ecosystem_graph_visualizer.html - Visualizador interactivo HTML de la red trófica
103. ICGC - Institut Cartogràfic i Geològic de Catalunya. Modelos digitales del terreno (MDT) LiDAR 5m. https://www.icgc.cat

### Referencias de modelización ABM

Grimm, V., Berger, U., Bastiansen, F., et al. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, 198(1-2), 115-126.

Grimm, V., Railsback, S. F., Vincenot, C. E., et al. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation*, 23(2), 7.

Railsback, S. F., & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling: A Practical Introduction* (2nd ed.). Princeton University Press.

Smith, D. W., Peterson, R. O., & Houston, D. B. (2003). Yellowstone after wolves. *BioScience*, 53(4), 330-340.

Jolivet, A., Lurgi, M., Claramunt-López, B. (2026). Socioeconomic and land-use factors shape sustainable management in the Catalan Pyrenees. *Communications Sustainability*, 1, 13.

### Nuevas referencias añadidas 2026-06-22

104. Catálogo de flora vascular del Parc Natural de l'Alt Pirineu (Aymerich, Seuba, Altarriba, 2025). Generalitat de Catalunya.
105. Esnaola, A., et al. (2021). It is the ambience, not the menu. Prey availability does not drive habitat selection by the endangered Pyrenean desman. *Aquatic Conservation*, 31(8).
106. Vulture Conservation Foundation (2026). Bearded Vulture in the Pyrenees: 2025 Breeding results and conservation actions.
107. MDPI Animals (2024). Survival Estimation Using Multistate Cormack–Jolly–Seber Models — The Case of the Bearded Vulture Gypaetus barbatus in Spain. *Animals*, 14(3), 403.
108. GSTOP (2026). 108 Brown Bears Detected in Pyrenees in 2025.
109. OFB (2025). Bilan des population d'ours brun dans les Pyrénées en 2024.
110. Burgos, T., et al. (2024). Apex predators can structure ecosystems through trophic cascades. *Functional Ecology*, 38, 1407-1420.
111. bioRxiv (2025). Predicting Ecosystem Resilience Using Multi-Agent Reinforcement Learning. 10.1101/2025.06.07.658424

---

## Material Suplementario

- **Tabla S1:** Especies de vertebrados incluidas en el modelo (masa, dieta, DEE) → `data/vertebrates.tsv`, `data/dee_estimado.tsv`
- **Tabla S2:** Clusters funcionales de plantas e invertebrados → `data/plant_clusters.tsv`, `data/invertebrate_clusters.tsv`
- **Tabla S3:** Matriz trófica completa (103+ interacciones) → `data/trophic_matrix.tsv`
- **Tabla S4:** Costos de actividad (19 comportamientos) → `data/costos_actividad.tsv`
- **Tabla S5:** Densidad energética de recursos → `data/energia_recursos.tsv`
- **Figura S1:** Visualización interactiva de la red trófica → `wiki/ecosystem_graph_visualizer.html`
- **Figura S2:** Grafo de red trófica (formato estándar) → `data/ecosystem_graph_standard.json`
- **Figuras S3–S5:** Mapas de terreno (15 mapas: DEM, pendiente, aspecto, TRI, pisos, hábitat, biomasas, 3D) → `output/maps/`
- **Figura S6:** Log de simulación medium (360 días, 1.315→120 agentes) → `output/medium_20260622_202003/simulation_log.csv`

---

## Anexo A: Fichas Detalladas de Especies de Vertebrados

A continuación se presenta la información biológica completa recopilada para cada una de las 22 especies/taxones de vertebrados incluidas en el modelo, con sus referencias asociadas. Los datos provienen de la base de datos maestra [6], las tablas de datos estructurados, la documentación del vault y las fuentes bibliográficas referenciadas.

### A.1 Mamíferos

##### *Rupicapra pyrenaica pyrenaica* — Isard pirinenc (Rebeco pirenaico)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Bovidae | [42][43] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Gramíneas y hierbas dicotiledóneas de prados alpinos y subalpinos (*Nardus stricta*, *Festuca* spp.); en invierno, vegetación leñosa (pino, arándanos, arbustos) | [45][46][47][16] |
| **Depredadores** | Águila real (principalmente jóvenes), zorro (menos frecuente), oso pardo (ocasionalmente individuos débiles) | [45][46][48][49] |
| **Reproducción** | Zelos en octubre-noviembre; gestación ~5 meses (23-25 semanas); parto de 1 cabrito único a finales de mayo-principios de junio; madurez sexual a los 2-3 años; tasa de natalidad efectiva: 0.8-1 cría/hembra/año | [45][46][47] |
| **Masa corporal** | 25-40 kg (media: 32.5 kg) | [44] |
| **Estado de conservación** | Población estable; subespecie endémica de los Pirineos | [2][43] |
| **DEE estimado** | 1,905.6 kcal/día | [50] |
| **Proporción dieta** | 92% plantas, 5% invertebrados, 3% vertebrados | [51] |

##### *Cervus elaphus* — Cérvol (Ciervo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Cervidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Gramíneas, hierbas y brotes de arbustos y árboles; prados de alta montaña y claros forestales | [24][23][52] |
| **Depredadores** | Oso pardo (crías o individuos debilitados); zorro y grandes rapaces (cervatos); en ausencia de lobo, depredación natural sobre adultos baja | [53][48][52] |
| **Reproducción** | Berrea y celo en septiembre-octubre; gestación ~8 meses; parto en mayo-junio con 1 cría por hembra (raramente 2); madurez sexual a los ~2 años (hembras) | [24][53] |
| **Masa corporal** | 150-250 kg (media: 200 kg) | [44] |
| **Estado de conservación** | Población en expansión en el PNAP | [2] |
| **DEE estimado** | 7,445.6 kcal/día | [50] |
| **Proporción dieta** | 95% plantas, 3% invertebrados, 2% vertebrados | [51] |

##### *Capreolus capreolus* — Cabirol (Corzo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Cervidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Brotes tiernos, hojas y hierbas de claros, prados y sotobosque | [24][1] |
| **Depredadores** | Oso y lobo (potencial); crías por zorro y grandes rapaces | [48][49] |
| **Reproducción** | Celo en verano (julio-agosto); implantación embrionaria diferida; gestación efectiva ~5 meses; parto en mayo-junio con 2 crías por hembra | [24][48] |
| **Masa corporal** | 15-25 kg (media: 20 kg) | [44] |
| **Estado de conservación** | Población moderada en el PNAP | [2] |
| **DEE estimado** | 1,324.0 kcal/día | [50] |
| **Proporción dieta** | 96% plantas, 3% invertebrados, 1% vertebrados | [51] |

##### *Sus scrofa* — Porc senglar (Jabalí)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Suidae | [44] |
| **Nivel trófico** | Omnívoro | [44] |
| **Dieta principal** | Raíces, tubérculos, frutos forestales (hayas, bellotas), invertebrados del suelo; ocasionalmente huevos o pollos de aves nidificantes en tierra | [24][52] |
| **Depredadores** | Oso pardo (adultos); zorros y águilas (jabalíes jóvenes); regulación principal antrópica (caza) fuera del parque | [53][52] |
| **Reproducción** | Alta capacidad reproductiva; celos principalmente otoñales; gestación ~4 meses; camadas de 3-8 jabatos; hembras se reproducen anualmente o más a menudo | [24][53] |
| **Masa corporal** | 50-150 kg (media: 100 kg) | [44] |
| **Estado de conservación** | Población abundante, clave en la dinámica del sotobosque | [2] |
| **DEE estimado** | 4,427.2 kcal/día | [50] |
| **Proporción dieta** | 60% plantas, 20% invertebrados, 20% vertebrados (huevos) | [51] |

##### *Ursus arctos arctos* — Ós bru (Oso pardo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Ursidae | [44] |
| **Nivel trófico** | Omnívoro | [44] |
| **Dieta principal** | 75-85% vegetal (hierbas, brotes, frutos carnosos y secos: arándanos, frambuesas, manzanas, castañas, hayas); carroña, insectos (hormigas), miel, aves y huevos, ungulados domésticos o salvajes, truchas | [53][54][48][55] |
| **Depredadores** | Adulto sin depredadores naturales en el PNAP; mortalidad por causas humanas (caza ilegal, colisiones, conflictos) o accidentes naturales | [53][56] |
| **Reproducción** | Madurez sexual: 3.5-5 años (hembras); celos mayo-julio; implantación embrionaria diferida; gestación efectiva 8-10 semanas; 1-3 crías en enero durante hibernación; crías con la madre 18-22 meses; hembras se aparean cada 2-3 años; tasa de natalidad baja (~1 cría/hembra cada 2-3 años) | [53][48][56] |
| **Masa corporal** | 100-200 kg (media: 150 kg) | [44] |
| **Estado de conservación** | **En peligro crítico** en Pirineos; población pirenaica mínima de 108 individuos en 2025 (GSTOP 2025: 59 adultos, 42 subadultos, 8 crías); crecimiento anual ~11% desde 2006; origen esloveno (reintroducciones 1996-2018); presencia regular en los valles más septentrionales del parque; problemas de endogamia (85% descendientes de un solo macho, "Pyros") | [2][53][56][108][109] |
| **DEE estimado** | 6,000.6 kcal/día | [50] |
| **Proporción dieta** | 40% plantas, 30% invertebrados, 30% vertebrados | [51] |

##### *Lutra lutra* — Llúdriga (Nutria)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Mustelidae | [44] |
| **Nivel trófico** | Carnívoro (piscívoro) | [44] |
| **Dieta principal** | Principalmente peces (trucha *Salmo trutta* y ciprínidos como madrilla y piscardo); cangrejos de río, anfibios y pequeños mamíferos acuáticos (desmán) | [57][58][59] |
| **Depredadores** | Sin depredadores naturales significativos como adulto; crías vulnerables a grandes rapaces o cánidos | [57][56] |
| **Reproducción** | Reproducción en cualquier época con picos a finales de invierno-primavera; gestación ~60-64 días; 1-3 crías/camada; madurez sexual a los 2-3 años | [57][48] |
| **Masa corporal** | 7-12 kg (media: 9.5 kg) | [44] |
| **Estado de conservación** | Población recuperándose; indicador de calidad de aguas fluviales | [2] |
| **DEE estimado** | 757.6 kcal/día | [50] |

##### *Galemys pyrenaicus* — Almesquera / Desmàn ibèric (Desmán ibérico)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Talpidae | [44] |
| **Nivel trófico** | Insectívoro (semiacuático) | [44] |
| **Dieta principal** | Invertebrados acuáticos (larvas de insectos, gusanos, moluscos); ocasionalmente pequeños crustáceos | [18][57] |
| **Depredadores** | Peces grandes (truchas), nutrias, garzas reales y otras aves piscívoras; carnívoros terrestres en tramos de río estrechos | [18][57][60] |
| **Reproducción** | Especie con ciclo ligado a cursos de agua fríos; reproducción generalmente en primavera con 2-5 crías/camada; 1-2 camadas anuales | [18][57] |
| **Masa corporal** | 0.01-0.02 kg (media: 0.015 kg) | [44] |
| **Estado de conservación** | **Vulnerable** (IUCN); endemismo del norte ibérico; especie relicta ibero-pirenaica; contracción del 63.5% en rangos históricos de Portugal (1993-96 vs 2014-15); muy sensible a contaminación, alteración hidrológica y cambio climático; prefiere rápidos por restricciones mecánicas de caza, no por disponibilidad de presas | [2][6][104][105] |
| **DEE estimado** | 6.0 kcal/día | [50] |

##### *Martes martes* — Marta (Marta)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Mustelidae | [44] |
| **Nivel trófico** | Carnívoro (forestal) | [44] |
| **Dieta principal** | Dieta muy oportunista: pequeños mamíferos (micromamíferos, ardillas), aves y sus huevos, anfibios, invertebrados y frutos; depredador clave de nidos de urogallo | [60][61][62] |
| **Depredadores** | Adulto sin depredadores naturales significativos; ocasionalmente presa de grandes rapaces | [2][60] |
| **Reproducción** | Implantación embrionaria diferida; apareamiento en verano (julio-agosto) y parto a finales de invierno-inicios de primavera; 2-5 crías | [61][19] |
| **Masa corporal** | 1-2 kg (media: 1.5 kg) | [44] |
| **Estado de conservación** | Población moderada en bosques maduros; depredador clave de nidos de urogallo | [2][60] |
| **DEE estimado** | 189.8 kcal/día | [50] |

##### *Vulpes vulpes* — Guineu (Zorro)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Canidae | [44] |
| **Nivel trófico** | Omnívoro | [44] |
| **Dieta principal** | Micromamíferos, aves, invertebrados, frutos, carroña; oportunista | [44] |
| **Depredadores** | Sin depredadores naturales significativos como adulto | [44] |
| **Reproducción** | Reproducción en invierno-primavera; gestación ~52 días; 4-6 crías/camada; madurez sexual ~1 año | [44] |
| **Masa corporal** | 4-8 kg (media: 6 kg) | [44] |
| **Estado de conservación** | Población abundante, oportunista; afecta a nidos de aves | [2] |
| **DEE estimado** | 536.7 kcal/día | [50] |

##### *Felis silvestris* — Gat fer (Gato montés)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Felidae | [44] |
| **Nivel trófico** | Carnívoro | [44] |
| **Dieta principal** | Micromamíferos, aves, huevos, invertebrados, frutos; oportunista | [44] |
| **Depredadores** | Sin depredadores naturales significativos como adulto | [44] |
| **Reproducción** | Reproducción en cualquier época; gestación ~65 días; 2-5 crías/camada; madurez sexual ~1 año | [44] |
| **Masa corporal** | 3-5 kg (media: 4 kg) | [44] |
| **Estado de conservación** | Población moderada; nicho trófico similar al zorro | [2] |
| **DEE estimado** | 396.0 kcal/día | [50] |

##### *Mustela nivalis* — Mostela (Comadreja)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Mustelidae | [44] |
| **Nivel trófico** | Carnívoro | [44] |
| **Dieta principal** | Micromamíferos, aves, invertebrados; oportunista | [44] |
| **Depredadores** | Rapaces, gato montés, zorro; ocasionalmente martas y tejones | [44] |
| **Reproducción** | Reproducción primavera-verano; gestación ~30 días; 4-8 crías/camada; madurez sexual a los 3-4 meses | [44] |
| **Masa corporal** | 0.06-0.1 kg (media: 0.08 kg) | [44] |
| **Estado de conservación** | Población moderada; consume ~50% de su peso corporal al día | [2] |
| **DEE estimado** | 21.1 kcal/día | [50] |

##### *Mustela erminea* — Ermíni (Armiño)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Mustelidae | [44] |
| **Nivel trófico** | Carnívoro | [44] |
| **Dieta principal** | Micromamíferos, aves, invertebrados; oportunista | [44] |
| **Depredadores** | Rapaces, gato montés, zorro, martas | [44] |
| **Reproducción** | Reproducción en verano; gestación ~30 días con implantación diferida; 4-9 crías/camada; madurez sexual ~1 año | [44] |
| **Masa corporal** | 0.1-0.2 kg (media: 0.15 kg) | [44] |
| **Estado de conservación** | Población moderada; pelaje blanco en invierno (camuflaje nival) | [2] |
| **DEE estimado** | 33.7 kcal/día | [50] |

##### *Marmota marmota* — Marmota alpina (Marmota alpina)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Sciuridae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Predominantemente dicotiledóneas, hierbas, tallos, flores, hojas, semillas, brotes y raíces; ocasionalmente pequeños invertebrados | [44] |
| **Depredadores** | Águila real (principal depredador, hasta el 50% de su dieta en época reproductora), zorro, perros pastores, quebrantahuesos (carroña) | [44] |
| **Reproducción** | Celo en mayo; gestación ~33-34 días; parto en junio con 2-4 crías (hasta 7); peso al nacer 30-40 g; hibernación de octubre a abril; madurez sexual a los 2 años; una camada anual | [44] |
| **Masa corporal** | 3.4-5.7 kg (media: 4.55 kg) | [44] |
| **Estado de conservación** | Población estable en zonas rocosas alpinas; clave en la aireación del suelo alpino; presa del águila real | [2] |
| **DEE estimado** | 396.0 (estimado por similitud con *Aquila chrysaetos*) | [50] |

##### *Oryctolagus cuniculus* — Conill (Conejo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Leporidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Gramíneas y hierba fresca con alto contenido en proteínas; brotes tiernos, frutos | [44] |
| **Depredadores** | Águila real, zorro, marta, gato montés, comadreja, armiño, rapaces nocturnas | [44] |
| **Reproducción** | Reproducción oportunista (receptivas todo el año); gestación ~30 días; 3-7 crías/parto; varias camadas anuales (3-6); destete a las 3-4 semanas; madurez sexual a los 4-8 meses | [44] |
| **Masa corporal** | 0.9-1.5 kg (media: 1.2 kg) | [44] |
| **Estado de conservación** | Población variable | [2] |
| **DEE estimado** | 189.8 (estimado por similitud con *Martes martes*) | [50] |

##### *Meles meles* — Teixó (Tejón)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Mustelidae | [44] |
| **Nivel trófico** | Omnívoro | [44] |
| **Dieta principal** | Lombrices de tierra (base de la dieta), frutos, raíces, tubérculos, insectos (coleópteros) y larvas, micromamíferos, conejos, anfibios, reptiles, miel | [44] |
| **Depredadores** | Adulto sin depredadores naturales en el PNAP; crías potencialmente por águila real, oso pardo | [44] |
| **Reproducción** | Implantación embrionaria diferida; apareamiento de febrero a mayo; gestación efectiva ~2 meses; partos en enero-marzo de 2-4 crías; destete a los 3 meses; una camada anual; semi-hibernación invernal | [44] |
| **Masa corporal** | 7-15 kg (media: 11 kg) | [44] |
| **Estado de conservación** | Población estable | [2] |
| **DEE estimado** | 757.6 (estimado por similitud con *Lutra lutra*) | [50] |

##### *Sciurus vulgaris* — Esquirol (Ardilla roja)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Sciuridae | [44] |
| **Nivel trófico** | Herbívoro (granívoro) | [44] |
| **Dieta principal** | Piñones, frutos secos (avellanas, hayas, bellotas), semillas y hongos; ocasionalmente larvas de insectos, caracoles, huevos y pollos de aves | [44] |
| **Depredadores** | Marta, azor, zorro, gato montés, rapaces diurnas y nocturnas | [44] |
| **Reproducción** | Dos épocas reproductoras al año (enero-abril y mayo-agosto); gestación ~38 días; 3-6 crías/camada; destete a las 8-10 semanas; madurez sexual al año; longevidad 3-7 años en libertad | [44] |
| **Masa corporal** | 0.2-0.4 kg (media: 0.3 kg) | [44] |
| **Estado de conservación** | Población estable en bosques de coníferas | [2] |
| **DEE estimado** | 33.7 (estimado por similitud con *Mustela erminea*) | [50] |

##### *Ovis aries musimon* — Mufló (Muflón)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Bovidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Gramíneas, hierbas, brotes tiernos, hojas, corteza, setas, musgos y líquenes; prefiere espacios abiertos de montaña | [44] |
| **Depredadores** | Oso pardo (crías ocasionalmente), águila real (crías), zorro (crías) | [44] |
| **Reproducción** | Celo en septiembre-octubre; gestación ~5 meses (150-160 días); 1-2 crías/parto en marzo-abril; madurez sexual a los 2-3 años; tasa de natalidad efectiva 0.8-1 cría/hembra/año | [44] |
| **Masa corporal** | 25-50 kg (media: 37.5 kg) | [44] |
| **Estado de conservación** | Ungulado introducido, puede competir con fauna autóctona | [2] |
| **DEE estimado** | 1,905.6 (estimado por similitud con *Rupicapra*) | [50] |

##### *Dama dama* — Daina (Gamo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Mammalia, Cervidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Vegetación herbácea, hojas de árboles y arbustos, hierbas de prados y claros forestales | [44] |
| **Depredadores** | Oso pardo (crías), zorro (crías), águila real (crías) | [44] |
| **Reproducción** | Celo en octubre (ronca); gestación ~8 meses; parto en mayo-junio con 1 cría (raramente 2) por hembra; madurez sexual a los 2 años; tasa de natalidad efectiva: 1 cría/hembra/año | [44] |
| **Masa corporal** | 30-85 kg (media: 57.5 kg) | [44] |
| **Estado de conservación** | Ungulado introducido, puede competir con fauna autóctona | [2] |
| **DEE estimado** | 4,427.2 (estimado por similitud con *Sus scrofa*) | [50] |

### A.2 Aves

##### *Tetrao urogallus* (subsp. pirenaica) — Gall fer (Urogallo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Aves, Phasianidae | [44] |
| **Nivel trófico** | Omnívoro (estacional) | [44] |
| **Dieta principal** | Invierno: acículas de pino negro (*Pinus uncinata*), abeto blanco, enebro; primavera-verano: brotes y frutos de sotobosque (arándano, gayuba, rododendro, gramíneas); pollos: invertebrados (larvas de lepidópteros, hormigas, coleópteros) para proteína de alta calidad | [10][11][12][63] |
| **Depredadores** | Marta (*Martes martes*) como principal depredador de nidos y pollos; zorro (nidos, especialmente en zonas perturbadas); jabalí (nidos en tierra) | [60][52][11] |
| **Reproducción** | Celo y actividad de cantaderos en primavera (marzo-mayo); puesta de 6-8 huevos/nido (típico 7); incubación ~26-28 días; supervivencia de nido limitada (pérdidas por depredación >40-60%); hembras se reproducen anualmente pero éxito reproductor bajo (≤2 pollos volanderos/hembra) | [64][65][66][67] |
| **Masa corporal** | 3.5-5 kg (media: 4.25 kg) | [44] |
| **Estado de conservación** | **Vulnerable**; mayor población ibérica de urogallo (casi la única que no está en regresión); especie paraguas del bosque subalpino maduro | [2][6] |
| **DEE estimado** | 414.4 kcal/día | [50] |

##### *Lagopus muta* — Perdiu xerra (Perdiz nival)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Aves, Phasianidae | [44] |
| **Nivel trófico** | Herbívoro | [44] |
| **Dieta principal** | Vegetación alpina (brotes, hojas, yemas); invertebrados para los pollos | [1][2] |
| **Depredadores** | Similares a otras gallináceas: mustélidos, zorros, rapaces | [44] |
| **Reproducción** | Puesta en primavera; incubación ~24 días; 6-10 huevos/nido; madurez sexual al año siguiente; una camada anual | [44] |
| **Masa corporal** | 0.4-0.6 kg (media: 0.5 kg) | [44] |
| **Estado de conservación** | **Especie ártico-alpina**; en el límite sur de su distribución europea; plumaje blanco en invierno | [2][6] |
| **DEE estimado** | 83.2 kcal/día | [50] |

##### *Gypaetus barbatus* — Trencalòs (Quebrantahuesos)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Aves, Accipitridae | [44] |
| **Nivel trófico** | Carroñero (osteófago) | [44] |
| **Dieta principal** | Principalmente huesos de ungulados domésticos y salvajes (isard, ciervo, corzo, ovejas, cabras); ocasionalmente tejidos ricos en médula y presas pequeñas vivas | [68][2][69] |
| **Depredadores** | Sin depredadores naturales; riesgos antrópicos (venenos, colisiones, molestias) | [69][2] |
| **Reproducción** | Especie de vida larga con madurez tardía (~7-8 años); parejas territoriales estables; puesta en invierno (diciembre-febrero) de 1-2 huevos; incubación ~53-60 días; generalmente solo un pollo vuela; tasa de reproducción baja (1 cría cada 1-2 años por pareja) | [69][2] |
| **Masa corporal** | 4-7 kg (media: 5.5 kg) | [44] |
| **Estado de conservación** | **Vulnerable**; especie en peligro; única ave especializada en alimentarse de huesos (90% de su dieta); Plan de Recuperación activo; población estable en el PNAP. En 2025: 50 volantones en todo el Pirineo, 209 unidades territoriales. Francia adoptó Plan de Acción Nacional 2026-2035 para +42% de parejas territoriales. Supervivencia adulta en Pirineos: 0.92, juvenil: 0.90 | [2][69][106][107] |
| **DEE estimado** | 502.8 kcal/día | [50] |

##### *Aquila chrysaetos* — Àguila reial (Águila real)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Aves, Accipitridae | [44] |
| **Nivel trófico** | Carnívoro (depredador apical) | [44] |
| **Dieta principal** | Principalmente mamíferos medianos (isards jóvenes, corzos, marmotas, conejos); también aves (gallináceas, córvidos) y ocasionalmente carroña | [68][45][46][49] |
| **Depredadores** | Sin depredadores naturales significativos como adulto; pollos vulnerables a competidores o humanos | [69][48] |
| **Reproducción** | Parejas territoriales; puesta 1-3 huevos a finales de invierno-primavera; incubación ~40-45 días; a menudo solo un pollo sobrevive por competencia fraterna; 1 cría/año en parejas en buen estado | [69][48] |
| **Masa corporal** | 3-5 kg (media: 4 kg) | [44] |
| **Estado de conservación** | Varias parejas territoriales estables en el PNAP; superdepredador apical; territorios extensos (~100 km²) | [2] |
| **DEE estimado** | 396.0 kcal/día | [50] |

### A.3 Reptiles

##### *Iberolacerta aurelioi* — Sargantana pallaresa (Lagartija pallaresa)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Reptilia, Lacertidae | [44] |
| **Nivel trófico** | Insectívoro | [44] |
| **Dieta principal** | Exclusivamente entomófaga; dieta variada de artrópodos de 14 órdenes diferentes (preferencia por hormigas, coleópteros, heterópteros y dípteros); ocasionalmente canibalismo | [41][70] |
| **Depredadores** | Rapaces diurnas insectívoras/omnívoras; carnívoros pequeños; pero el riesgo principal es la alteración del hábitat | [41][70] |
| **Reproducción** | Especie de alta montaña (2.100-2.900 m) con período de actividad anual de ~4 meses; cópulas a mediados de mayo-principios de junio; puesta única anual de 1-4 huevos un mes después del deshielo; incubación ~1 mes; juveniles visibles de finales de agosto al otoño; madurez sexual a los 4 años (machos) y 5 años (hembras); longevidad hasta 17 años | [41][70][71] |
| **Masa corporal** | 0.01-0.02 kg (media: 0.015 kg) | [44] |
| **Estado de conservación** | **En peligro de extinción**; especie endémica descubierta en la década de 1990; la mayor parte de su población mundial está dentro del parque (macizo del Mont-roig y oeste de Andorra); catalogada como **En Peligro** en el Catálogo de Fauna Amenazada de Cataluña | [2][6][70] |
| **DEE estimado** | 6.0 kcal/día | [50] |

### A.4 Anfibios

##### *Calotriton asper* — Tritó pirinenc (Tritón pirenaico)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Amphibia, Salamandridae | [44] |
| **Nivel trófico** | Carnívoro (acuático) | [44] |
| **Dieta principal** | Pequeños moluscos, crustáceos y larvas de insectos acuáticos (efemerópteros, plecópteros, tricópteros); depredador importante de invertebrados en torrentes y balsas frías de montaña | [60][72][73] |
| **Depredadores** | Trucha (*Salmo trutta*); otros peces introducidos; aves acuáticas | [60][73][74] |
| **Reproducción** | Cría a finales de primavera y principios de verano en aguas frías y bien oxigenadas; hembra coloca huevos bajo piedras o en sustrato sumergido; larvas nacen al cabo de un mes; metamorfosis en 1-2 años; alta fidelidad a masas de agua concretas | [72][73][75] |
| **Masa corporal** | 0.005-0.01 kg (media: 0.0075 kg) | [44] |
| **Estado de conservación** | **Endemismo pirenaico**; uno de los pocos urodelos que vive exclusivamente en medios acuáticos fríos y oxigenados; indicador de calidad de aguas | [2] |
| **DEE estimado** | 3.6 kcal/día | [50] |

##### *Rana temporaria* — Granota roja (Rana bermeja)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Amphibia, Ranidae | [44] |
| **Nivel trófico** | Insectívoro | [44] |
| **Dieta principal** | Invertebrados acuáticos y terrestres; larvas de mosquitos, gusanos y otros pequeños invertebrados | [75] |
| **Depredadores** | Truchas, otros peces, aves piscívoras, carnívoros de ribera; renacuajos consumidos por invertebrados acuáticos y peces | [60][73] |
| **Reproducción** | Puesta masiva en primavera en balsas y charcas; decenas a centenares de huevos/puesta; desarrollo larvario variable según temperatura; importante fuente de biomasa para depredadores acuáticos | [75][60] |
| **Masa corporal** | 0.02-0.03 kg (media: 0.025 kg) | [44] |
| **Estado de conservación** | Población abundante; clave en la transferencia de energía de invertebrados a vertebrados acuáticos | [2] |
| **DEE estimado** | 8.8 kcal/día | [50] |

### A.5 Peces

##### *Salmo trutta* — Truita de riu autòctona (Trucha común)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Actinopterygii, Salmonidae | [44] |
| **Nivel trófico** | Carnívoro (acuático) | [44] |
| **Dieta principal** | Invertebrados acuáticos (larvas de efemerópteros, plecópteros, tricópteros), crustáceos; peces pequeños y anfibios (tritón pirenaico); ocasionalmente renacuajos y ranas | [60][74][58][59] |
| **Depredadores** | Nutria, garzas reales, otras aves piscívoras; potencialmente el oso cuando pesca en ríos | [57][60][59] |
| **Reproducción** | Remonta los cursos para frezar en tramos cabdalosos y bien oxigenados de cabecera; freza a finales de otoño-invierno; huevos en gravas; eclosión en primavera; longevidad alta en ríos fríos (hasta 10-11 años documentados en la Noguera Pallaresa) | [55][76][77] |
| **Masa corporal** | 0.5-2 kg (media: 1.25 kg) | [44] |
| **Estado de conservación** | Poblaciones autóctonas en los tramos fluviales superiores; especie clave en ecosistemas fluviales del parque; depredador tope en ríos de montaña | [2] |
| **DEE estimado** | 165.5 kcal/día | [50] |

##### *Phoxinus spp.* — Barb roig / Veró (Piscardo)

| Atributo | Descripción | Referencia |
|----------|-------------|------------|
| **Taxonomía** | Actinopterygii, Cyprinidae | [44] |
| **Nivel trófico** | Omnívoro | [44] |
| **Dieta principal** | Pequeños invertebrados, algas y materia orgánica | [74][58] |
| **Depredadores** | Truchas y nutrias; también aves piscívoras en aguas someras | [74][58] |
| **Reproducción** | Reproducción en primavera-verano en aguas someras; puesta sobre sustratos de grava o vegetación acuática; varias puestas por temporada; altas densidades en lagos de montaña con impactos sobre redes tróficas | [74][58] |
| **Masa corporal** | 0.01-0.05 kg (media: 0.03 kg) | [44] |
| **Estado de conservación** | Especie introducida en algunos lagos de alta montaña; puede impactar negativamente sobre anfibios e invertebrados autóctonos | [2] |
| **DEE estimado** | 10.1 kcal/día | [50] |

---

*Documento generado el 23 de junio de 2026. Pendiente de actualización con simulaciones corregidas (conectar dieta, depredación, temperatura).*
