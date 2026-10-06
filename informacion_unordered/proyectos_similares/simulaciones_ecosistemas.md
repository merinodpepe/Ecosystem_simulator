# Proyectos Similares de Simulación de Ecosistemas

## 1. Multi-Agent Reinforcement Learning para ecosistemas alpinos (bioRxiv 2025)
- **Autores**: Varios (artículo bioRxiv 10.1101/2025.06.07.658424)
- **Enfoque**: Agent-Based Model (ABM) con Reinforcement Learning —sin reglas escritas a mano— para simular comportamiento animal
- **Validación**: 10 ecosistemas alpinos (Alpes Réticos, Italia) con lobos, rebecos y vegetación
- **Método**: Entrenamiento de modelos conductuales con RL en modelos sintéticos generados por Perlin noise
- **Agentes**: Individuales (chamois, wolves) sobre grid 100×100
- **Resultados**: Reproducen poblaciones realistas, historia de vida, patrones de caza
- **Relevancia**: Similar al proyecto del Alt Pirineu (ABM con agentes individuales en grid espacial)

## 2. Modelo socioecológico de Pirineo Catalán (Nature Communications Sustainability 2026)
- **Autores**: Jolivet, Lurgi, Claramunt-López (CREAF-UAB)
- **Enfoque**: Dinámica de sistemas acoplados (ODE network model) de 30 elementos
- **Elementos**: Socioeconómicos (13), usos del suelo (4), biodiversidad (4), hidrología (4), clima (2), teledetección (4)
- **Escenario**: Alto Segre, Pirineo catalán
- **Objetivo**: Identificar factores clave para la sostenibilidad bajo diferentes escenarios
- **Método**: 100.000 simulaciones numéricas → árbol de clasificación
- **Resultado**: Factores socioeconómicos y de uso del suelo son determinantes; limitar expansión forestal y equilibrar turismo/agricultura es clave

## 3. Modelo P-systems de Isards en Pirineos Catalanes (Universidad de Sevilla, MCoMS)
- **Enfoque**: Membrane Computing (P-systems) para modelar dinámica poblacional de *Rupicapra pyrenaica*
- **Variables**: Clima (nieve), reproducción, densidad, alimento, mortalidad natural, caza, enfermedades
- **Herramienta**: MeCoSim (Membrane Computing Simulator)
- **Módulos**: Clima, reproducción, regulación densidad, alimento, mortalidad (natural + caza + enfermedad)
- **Multientorno**: Grado 4, 11 membranas
- **Relevancia**: Modelo específico de Pirineos con isard como especie focal

## 4. NetLogo: Wolf-Sheep Predation (modelo clásico)
- El modelo depredador-presa más clásico en NetLogo
- Base de múltiples simulaciones educativas y de investigación
- Usado como punto de partida para simular depredación en ecosistemas

## 5. NetLogo: Bug Hunt Predator-Prey (ModelSim)
- **Modelo**: Consumidor-productor con disturbios ambientales
- **Entorno**: 2 regiones, pasto que regenera, bugs que se desplazan
- **Extensiones**: Depredadores (pájaros), especies invasoras, fuego, enfermedades
- **Relevancia**: Marco para entender dinámicas de estabilidad de ecosistemas ante perturbaciones

## 6. CoMSES Net — Test-bed ecological model (evolve.nlogo)
- **Creador**: Comunidad CoMSES.net
- **Características**: Economía energética, cadena trófica dinámica, espacio explícito, mutación y migración de especies
- **Autoorganización**: Especies y composición emergen sin predeterminación
- **Resultados**: Redes tróficas plausibles, shocks endógenos (nuevas especies), alta adaptabilidad

## 7. Proyectos específicos del Pirineo
- **LIFE RESQUE ALPYR**: Restauración de estanys de alta montaña eliminando peces introducidos. Francia-España-Andorra
- **AELCLIC-Pathfinder**: Adaptación de paisajes europeos al cambio climático (PNAP como piloto)
- **Seguimiento transfronterizo del oso (GSTOP)**: Monitorización genética y poblacional del oso pardo
- **Catalan Butterfly Monitoring Scheme (CBMS)**: Indicadores de polinizadores para el PNAP

## 8. Alt Pirineu Ecosystem Simulator (este proyecto)
- **Lenguaje**: Python + Numba JIT
- **Resolución**: 25m grid, 375×502 celdas
- **Agentes**: Individuales con GOAP (Goal-Oriented Action Planning)
- **Especies**: 277 vertebrados + clusters funcionales de plantas e invertebrados
- **Sistemas implementados**: Movimiento (A*), energía (Kleiber BMR + MET), dieta, reproducción, clima, vegetación
- **Datos reales**: SRTM DEM 30m, pisos bioclimáticos, costes MET

Fuentes: bioRxiv 2025, Nature Communications Sustainability 2026, DDD UAB, IDUS.us.es, CoMSES.net, ccl.netlogo.org, GitHub (ANR-MIMICO, Cizr)
