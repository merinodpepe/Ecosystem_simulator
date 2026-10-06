# Graph Report - ecosystem_simulator  (2026-10-06)

## Corpus Check
- Large corpus: 261 files · ~1,360,348 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 1339 nodes · 2342 edges · 88 communities (66 shown, 22 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 305 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- numpy (c0)
- pipeline.py (c1)
- Agent (c2)
- validacion_energia.md (c3)
- process_mcsc.py (c4)
- analyze_graph.py (c5)
- energy.rs (c6)
- PoolManager (c7)
- TerrainGrid (c8)
- Simulation (c9)
- Base d'espècies i interaccions tròfiques (c10)
- foodweb.rs (c11)
- Arquitectura del simulador (Python + Num (c12)
- Siete etapas del diagnóstico (2.1-2.7) (c13)
- simulation.rs (c14)
- ecosystem_graph_standard explicación (c15)
- Agent3D (c16)
- grid.py (c17)
- energy.py (c18)
- grid.rs (c19)
- Parc Natural de l'Alt Pirineu (c20)
- Agent (c21)
- Parc Natural de l'Alt Pirineu (79.317 ha (c22)
- OmnivoreAgent (c23)
- Anexo A: fichas de especies (c24)
- EnergyBudget (c25)
- Simulación agent-based: modelo matemátic (c26)
- TerrainGrid (c27)
- TerrainMesh (c28)
- CarnivoreAgent (c29)
- Simulation (c30)
- Ingesta Energética Potencial (IEP) (c31)
- TerrainViewer (c32)
- Ecosystem Simulation Overview figure (c33)
- Mancances ecològiques i pla d'acció (c34)
- Proyectos similares de simulación (doc) (c35)
- Errors E1-E10 invalidating results (c36)
- validate_energy.py (c37)
- Plan de Simulacion Agent-Based PNAP en P (c38)
- Pla d'Implementació: Sistema de Ticks (3 (c39)
- Flora y vegetación (doc) (c40)
- Paper: ABM trophic dynamics Alt Pirineu (c41)
- pathfinding.py (c42)
- Proyectos similares de simulacion de eco (c43)
- Season (c44)
- ursina_viewer.py (c45)
- Cell (c46)
- Terrain Cartography Dashboard (Alt Pirin (c47)
- Phased plan (Fases 0-6) (c48)
- Base de datos biológica maestra (c49)
- Fuentes de Informacion (master source in (c50)
- Energy validation figure (DEE vs Nagy 20 (c51)
- Vall de Cardos subcuenca grid (375x502,  (c52)
- Food web (foodweb.rs: diets, trophic lin (c53)
- Agent behaviors (herbivore, carnivore, o (c54)
- Base d'especies i interaccions trofiques (c55)
- Nagy (2005) Field metabolic rate and bod (c56)
- Ecosystem Simulator vault welcome (Bienv (c57)
- Topografía y terreno (doc) (c58)
- Visualizador de Red Trófica (HTML) (c59)
- PyO3 Rust extension module (c60)
- main.rs (c61)
- io.rs (c62)
- .initialize() (c63)
- Environment (c64)
- ecosystem/data (simulation data) (c67)
- Alt Pirineu Ecosystem Simulation Project (c68)
- Trophic network of Alt Pirineu Natural P (c69)
- Clústers vertebrados V-* (c70)
- Vall de Cardos terrain (500x375 grid, UT (c71)
- Per-species terrain biomass raster layer (c72)
- Pendent del Terreny (slope map, 0-60 deg (c73)
- sim_deep.sh (c75)
- sim_medium.sh (c76)
- sim_quick.sh (c77)
- run.sh (c78)
- PopulationConfig (species-specific param (c79)
- run_deep.sh (c80)
- run_medium.sh (c81)
- run_quick.sh (c82)
- Visualización interactiva vis-network (c83)
- alt-pirineu-sim (c84)
- ecosystem_simulator_rs (c85)

## God Nodes (most connected - your core abstractions)
1. `TerrainGrid` - 78 edges
2. `Agent` - 30 edges
3. `TerrainGrid` - 25 edges
4. `TerrainViewer` - 24 edges
5. `Agent` - 22 edges
6. `Simulation` - 22 edges
7. `Simulation` - 18 edges
8. `EnergyBudget` - 17 edges
9. `main()` - 17 edges
10. `Paper: ABM trophic dynamics Alt Pirineu` - 15 edges

## Surprising Connections (you probably didn't know these)
- `FMR allometric scaling (FMR = a·M^b)` --semantically_similar_to--> `Kleiber's law (BMR = 70 × M^0.75)`  [INFERRED] [semantically similar]
  ecosystem/data/referencias/Nagy_2005_FieldMetabolicRate.pdf → docs/2025-06-23_TICK_SYSTEM_FIXES.md
- `Agent FSM states (Idle, Travel, ForageSearch, HuntChase, ...)` --semantically_similar_to--> `AgentFSMState finite state machine`  [INFERRED] [semantically similar]
  PROJECT_OVERVIEW.md → docs/TICK_SYSTEM_REFACTOR_PLAN.md
- `Pisos bioclimaticos de vegetacion` --semantically_similar_to--> `Pisos bioclimaticos (Montano, Subalpino, Alpino, Nival)`  [INFERRED] [semantically similar]
  informacion_unordered/flora/vegetacion.md → ecosystem/wiki/terrain_procesamiento.md
- `Species template columns (taxon, diet, predators, reproduction)` --semantically_similar_to--> `vertebrates.tsv (38 entradas)`  [INFERRED] [semantically similar]
  graphify-out/converted/alt_pirineu_species_template_5c8d3a16.md → ecosystem/wiki/vertebrates_explicación.md
- `Clusters vertebrats V-*` --semantically_similar_to--> `Clusteres funcionales (V-, P, I) para modelar especies`  [INFERRED] [semantically similar]
  graph_analysis/graph_analysis_report.md → ecosystem/wiki/vertebrates_explicación.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Tick-based FSM engine core** — docs_tick_system_refactor_plan_agent_fsm, docs_tick_system_refactor_plan_tick_energy, docs_tick_system_refactor_plan_simulation_tick_loop, docs_tick_system_refactor_plan_tick_outcome, docs_tick_system_refactor_plan_circadian_cycle [EXTRACTED 1.00]
- **Mesh → simulation → 3D viewer pipeline** — pipeline_step_export_mesh, pipeline_step_simulation_snapshots, pipeline_step_viewer, execucio_pipeline_py [EXTRACTED 1.00]
- **Functional clusters P1-P3 / I1-I3 trophic scheme** — biodata_base_especies_plant_cluster_p1, biodata_base_especies_plant_cluster_p2, biodata_base_especies_plant_cluster_p3, biodata_base_especies_invert_cluster_i1, biodata_base_especies_invert_cluster_i2, biodata_base_especies_invert_cluster_i3 [EXTRACTED 1.00]
- **Pipeline de diagnóstico energético (dieta, DEE, locomoción, IEP)** — ecosystem_wiki_dieta_proporciones_doc, ecosystem_wiki_dee_calculo_doc, ecosystem_wiki_costo_locomocion_doc, ecosystem_wiki_2026_06_22_plan_diagnostico_energia_doc [EXTRACTED 0.85]
- **Subsistemas centrales del simulador** — ecosystem_paper_paper_goap, ecosystem_paper_paper_balance_energetico, ecosystem_paper_paper_forrajeo, ecosystem_paper_paper_astar, ecosystem_paper_paper_dinamica_vegetacion, ecosystem_paper_paper_reproduccion_mortalidad [EXTRACTED 0.95]
- **Clusters funcionales de plantas e invertebrados** — ecosystem_paper_paper_cluster_p1, ecosystem_paper_paper_cluster_p2, ecosystem_paper_paper_cluster_p3, ecosystem_paper_paper_cluster_i1, ecosystem_paper_paper_cluster_i2, ecosystem_paper_paper_cluster_i3 [EXTRACTED 0.95]
- **Subsistemas del motor de simulación** — ecosystem_wiki_simulacion_detallada_arquitectura_simulation_class, ecosystem_wiki_sistema_clima_estaciones_detallado_environment_class, ecosystem_wiki_sistema_energetico_detallado_energy_budget, ecosystem_wiki_sistema_pathfinding_detallado_a_star, ecosystem_wiki_sistema_pools_detallado_pool_manager, ecosystem_wiki_simulacion_agentes_detallado_goap_agents [INFERRED 0.85]
- **Flujo de balance energético (BMR, DEE, IEP)** — ecosystem_wiki_metabolismo_revision_bmr_allometric, ecosystem_wiki_metabolismo_revision_dee, ecosystem_wiki_iep_calculo_iep_formula, ecosystem_wiki_energia_recursos_energy_density, ecosystem_wiki_iep_calculo_iep_dee_balance [EXTRACTED 1.00]
- **Pipeline de terreno (SRTM, MCSC, biomasa)** — ecosystem_wiki_terrain_dem_explicacion_srtm_dem, ecosystem_wiki_terrain_dem_explicacion_pisos_bioclimaticos, ecosystem_wiki_terrain_habitat_explicacio_mcsc_landcover, ecosystem_wiki_terrain_habitat_explicacio_habitat_classes, ecosystem_wiki_terrain_habitat_explicacio_biomass_assignment, ecosystem_wiki_terrain_dem_explicacion_terrain_grid [EXTRACTED 1.00]
- **Terrain processing pipeline (SRTM/MCSC to rasters and maps)** — ecosystem_wiki_terrain_maps_readme_srtm_gl1, src_process_terrain, src_process_mcsc, ecosystem_wiki_terrain_maps_readme_terrain_dem_25m, ecosystem_wiki_terrain_maps_readme_terrain_habitat, ecosystem_wiki_terrain_maps_readme_terrain_biomass, ecosystem_wiki_terrain_maps_readme_terrain_cells_tsv, src_visualize_terrain_tsv [EXTRACTED 1.00]
- **Ursina 3D viewer pipeline** — src_export_terrain_mesh, ecosystem_wiki_visor_3d_guia_ursina_viewer_py, ecosystem_wiki_visor_3d_guia_ursina_models_py, src_ursina_sim_bridge, src_ursina_launcher [EXTRACTED 1.00]
- **Energy validation (BMR, FAct, DEE, IEP vs Nagy)** — ecosystem_wiki_validacion_energia_bmr, ecosystem_wiki_validacion_energia_fact, ecosystem_wiki_validacion_energia_dee, ecosystem_wiki_validacion_energia_iep, ecosystem_wiki_validacion_energia_nagy_2005 [EXTRACTED 1.00]
- **Trophic integration (diet foraging, predation, scavenging, pool consumption)** — simulator_readme_rust_forage, simulator_readme_rust_predation_step, simulator_readme_rust_scavenging, simulator_readme_rust_pool_consumption_step, simulator_readme_rust_foodweb [EXTRACTED 1.00]
- **Species data TSV files from biodata source** — species_data_readme_vertebrates_tsv, species_data_readme_plant_clusters_tsv, species_data_readme_invertebrate_clusters_tsv, species_data_readme_trophic_matrix_tsv [EXTRACTED 1.00]
- **Related ecosystem simulation projects** — informacion_unordered_proyectos_similares_simulaciones_ecosistemas_marl_alpine, informacion_unordered_proyectos_similares_simulaciones_ecosistemas_pyrenean_ses_model, informacion_unordered_proyectos_similares_simulaciones_ecosistemas_p_systems_isard, informacion_unordered_proyectos_similares_simulaciones_ecosistemas_netlogo_wolf_sheep, informacion_unordered_proyectos_similares_simulaciones_ecosistemas_comses_evolve [EXTRACTED 1.00]
- **Alt Pirineu trophic network visualizations** — ecosystem_paper_trophic_network_graph, ecosystem_paper_xarxa_trofica_alt_pirineu, ecosystem_paper_trophic_network_graph_recursos_vegetals [INFERRED 0.85]
- **Simulation result figures** — figures_overview, figures_species_populations, figures_species_stacked [INFERRED 0.85]
- **Terrain biomass maps (I3, P1, P2, P3)** — output_maps_terrain_biomass_i3, output_maps_terrain_biomass_p1, output_maps_terrain_biomass_p2, output_maps_terrain_biomass_p3 [EXTRACTED 1.00]
- **Terrain dashboard panels (DEM, slope, aspect, TRI, bioclimatic belts, habitats)** — output_maps_terrain_dem, output_maps_terrain_dashboard_slope, output_maps_terrain_dashboard_aspect, output_maps_terrain_dashboard_tri, output_maps_terrain_pisos, output_maps_terrain_habitat [EXTRACTED 1.00]
- **Terrain rasters derived from the DEM** — output_maps_terrain_slope, output_maps_terrain_tri, output_terrain_mesh_terrain_texture [INFERRED 0.85]

## Communities (88 total, 22 thin omitted)

### Community 0 - "numpy (c0)"
Cohesion: 0.05
Nodes (50): Grid de simulacion 375x502 a 25 m (EPSG:25831), terrain_cells.tsv, load_elevation_grid(), main(), load_terrain(), main(), render_frame(), export_grid_to_csv() (+42 more)

### Community 1 - "pipeline.py (c1)"
Cohesion: 0.05
Nodes (44): render_gif.py animated GIF renderer, Pla d'Acció 3D, Panel de info al clicar agente, Cámara follow-mode (tecla F), Integración simulación real con visor, Plan Visor 3D Interactivo, Agent3D, Snapshots JSON de la simulación (+36 more)

### Community 2 - "Agent (c2)"
Cohesion: 0.06
Nodes (32): Agent, AgentFSMState, Dead, Drink, EatCarcass, Flee, ForageEat, ForageSearch (+24 more)

### Community 3 - "validacion_energia.md (c3)"
Cohesion: 0.05
Nodes (39): trophic_matrix.tsv, Uso: red trofica inicial y probabilidades de interaccion, BMR alometrico por taxon (Kleiber, Aschoff & Pohl, ...), Gasto Energetico Diario (DEE = BMR x FAct), Balance energetico IEP - DEE, Factor de actividad (FAct) por taxon, Ingesta Energetica Potencial (IEP), Nagy 2005 allometric FMR equations (+31 more)

### Community 4 - "process_mcsc.py (c4)"
Cohesion: 0.07
Nodes (33): costos_actividad.tsv (MET por pendiente), MCSC (Mapa de Cobertes del Sol de Catalunya, 44 clases), SRTM GL1 30m DEM source, terrain_aspect.tif, terrain_biomass.tif (9 bandas biomasa inicial), terrain_dem_25m.tif (DEM), terrain_habitat.tif (10 habitats funcionales), terrain_pisos.tif (pisos bioclimaticos) (+25 more)

### Community 5 - "analyze_graph.py (c5)"
Cohesion: 0.08
Nodes (26): centrality_analysis(), cluster_subgraph_report(), community_detection(), load_graph(), main(), strip_clustermember_edges(), subgraph_around(), summary_statistics() (+18 more)

### Community 6 - "energy.rs (c6)"
Cohesion: 0.06
Nodes (39): ACTIVITY_COSTS, ASSIM_CARRION, ASSIM_INVERT, ASSIM_MEAT, bmr_kcal_day(), carrion_me_per_kg(), CRITICAL_ENERGY_RATIO, critical_energy_threshold() (+31 more)

### Community 7 - "PoolManager (c7)"
Cohesion: 0.08
Nodes (8): BatPool, FishPool, HerpPool, InvertebratePool, MicromammalPool, PasserinePool, PlantPool, PoolManager

### Community 8 - "TerrainGrid (c8)"
Cohesion: 0.11
Nodes (9): TerrainGrid, BatPool, FishPool, HerpPool, InvertebratePool, MicromammalPool, PasserinePool, PlantPool (+1 more)

### Community 9 - "Simulation (c9)"
Cohesion: 0.10
Nodes (5): default_snow_fn(), default_temp_fn(), Environment, PoolManager, Simulation

### Community 10 - "Base d'espècies i interaccions tròfiques (c10)"
Cohesion: 0.08
Nodes (28): Amphibians (Calotriton asper, Rana temporaria), Aquila chrysaetos (Àguila reial), Base d'espècies i interaccions tròfiques (PNAP), Galemys pyrenaicus (Almesquera), Gypaetus barbatus (Trencalòs), Iberolacerta aurelioi (Sargantana pallaresa), Cluster I1: pollinators (Boloria, Parnassius, Bombus), Cluster I2: phytophagous insects (+20 more)

### Community 11 - "foodweb.rs (c11)"
Cohesion: 0.12
Nodes (20): build_alias_map(), Diet, DIET_CACHE, get_all_trophic_links(), get_predators(), get_prey(), get_prey_weighted(), legacy_get_diet() (+12 more)

### Community 12 - "Arquitectura del simulador (Python + Num (c12)"
Cohesion: 0.14
Nodes (22): Agentes (Herbivore, Carnivore, Omnivore, Bird), Pathfinding A*, Balance energético del agente, Modelo de clima y nieve, Dinámica de vegetación e invertebrados, Forrajeo y consumo, GOAP: planificación de metas, Enfoque híbrido Python-Rust (planeado) (+14 more)

### Community 13 - "Siete etapas del diagnóstico (2.1-2.7) (c13)"
Cohesion: 0.12
Nodes (21): Costos de actividad MET (19 comportamientos), DEE alométrico (Kleiber por taxón), Fase 2: Cálculos energéticos (7 etapas), Validación energética (Nagy 2005), Gasto Energético Diario (DEE), Plan diagnóstico energético 2026-06-22, Siete etapas del diagnóstico (2.1-2.7), Fuentes: PanTHERIA, EltonTraits, Nagy 2005, USDA (+13 more)

### Community 14 - "simulation.rs (c14)"
Cohesion: 0.12
Nodes (13): ActivityPattern, Cathemeral, Crepuscular, Diurnal, Nocturnal, create_agent(), DEFAULT_POPULATIONS, HabitatPref (+5 more)

### Community 15 - "ecosystem_graph_standard explicación (c15)"
Cohesion: 0.15
Nodes (19): ecosystem_graph_standard explicación, Aristas clustermember, Clústers funcionales (P, I, V), trophic_matrix.tsv, Red trófica (75 nodos, 220 aristas), Recursos generales 'Various', Anàlisi de Xarxa Tròfica, Betweenness y especies clave (keystone) (+11 more)

### Community 16 - "Agent3D (c16)"
Cohesion: 0.13
Nodes (3): Agent3D, AgentDebug, darken()

### Community 17 - "grid.py (c17)"
Cohesion: 0.12
Nodes (6): Cell, slope_cost_factor(), step_inverts_jit(), step_plants_jit(), update_costs_jit(), update_snow_jit()

### Community 18 - "energy.py (c18)"
Cohesion: 0.17
Nodes (9): activity_kcal_h(), ActivityCost, bmr_kcal_day(), bmr_kcal_h(), daily_dee(), loco_cost_hours(), Diet, get_diet() (+1 more)

### Community 19 - "grid.rs (c19)"
Cohesion: 0.11
Nodes (16): AGUA, ALPINO, ANTROPICO, BOSQUE_CAD, BOSQUE_CON, HUMEDAL, MATORRAL, MONTANO (+8 more)

### Community 20 - "Parc Natural de l'Alt Pirineu (c20)"
Cohesion: 0.12
Nodes (19): AELCLIC-Pathfinder, Cambio climático en el PNAP (+1.2 °C desde 2003), Clima de montaña continental del PNAP, Contraste solells vs obacs, Clima del PNAP (doc), Menjaneu (viento foehn local), Cascadas tróficas, Ecología y redes tróficas (doc) (+11 more)

### Community 21 - "Agent (c21)"
Cohesion: 0.16
Nodes (3): Agent, AgentAction, ReproduceAction

### Community 22 - "Parc Natural de l'Alt Pirineu (79.317 ha (c22)"
Cohesion: 0.19
Nodes (18): Investigación del Parc Natural de l'Alt Pirineu, Fuentes DEM (ICGC, OpenTopography, EU-DEM), Especies emblemáticas y críticas, Parc Natural de l'Alt Pirineu (79.317 ha), Plan de Simulación del Terreno, Modelo de nieve estacional, Plan de terreno por fases, TRI como refugio de depredadores (+10 more)

### Community 23 - "OmnivoreAgent (c23)"
Cohesion: 0.19
Nodes (4): BirdAgent, ForageAction, MoveAction, OmnivoreAgent

### Community 24 - "Anexo A: fichas de especies (c24)"
Cohesion: 0.13
Nodes (17): Especies clave (keystone), Gall fer / urogallo, Relación mesodepredadores - gall fer, Oso pardo (Ursus arctos), Quebrantahuesos, Sargantana pallaresa, P-systems de isards (MeCoSim), Águila real (Aquila chrysaetos) (+9 more)

### Community 25 - "EnergyBudget (c25)"
Cohesion: 0.16
Nodes (3): AgentState, HerbivoreAgent, EnergyBudget

### Community 26 - "Simulación agent-based: modelo matemátic (c26)"
Cohesion: 0.20
Nodes (16): Sistema de Agentes GOAP detallado, AgentState / Agent base, Agentes GOAP simplificado, Arquitectura detallada del motor de simulación, Optimización Numba JIT, Simulation (bucle principal), TerrainGrid/Cell (grid.py), Simulación agent-based: modelo matemático y estado (+8 more)

### Community 29 - "CarnivoreAgent (c29)"
Cohesion: 0.19
Nodes (4): CarnivoreAgent, HuntAction, MoveToAction, ReproduceAction

### Community 30 - "Simulation (c30)"
Cohesion: 0.25
Nodes (3): log_line(), log_species_line(), Simulation

### Community 31 - "Ingesta Energética Potencial (IEP) (c31)"
Cohesion: 0.22
Nodes (13): Contenido energético de recursos (kcal/g), Densidad energética kcal/g húmedo, USDA FoodData Central, Cálculo de la IEP, Balance IEP vs DEE (validación), Ingesta Energética Potencial (IEP), Revisión bibliográfica de metabolismo, Factor de actividad FAct (+5 more)

### Community 33 - "Ecosystem Simulation Overview figure (c33)"
Cohesion: 0.18
Nodes (12): Parc Natural de l'Alt Pirineu (study area), Ecosystem Simulation Overview figure, Agent Population (alive jumps ~3300 to 5200 at day 90-100, peak 6100 day 250), Average Agent Energy (declines over year), Average Temperature (seasonal sinusoid, -10 to 10 C), Ecosystem Biomass (plants, invertebrates, carcass), Species Populations by Trophic Group figure, Carnivores panel (Mostela, Ermini, Marta, Gat fer, Aguila reial) (+4 more)

### Community 34 - "Mancances ecològiques i pla d'acció (c34)"
Cohesion: 0.19
Nodes (13): Daily simulation loop (decide/execute phases), Estat Actual (simulator state, Catalan), Current limitations (no hibernation, no migration, ...), Reproduction model (seasonal, females only), 18 modelled species table, Project cleanup list (duplicate data, legacy outputs), Three-model council review (Opus, Sonnet, Fable), Hoja de ruta — Simulador realista del Alt Pirineu (+5 more)

### Community 35 - "Proyectos similares de simulación (doc) (c35)"
Cohesion: 0.22
Nodes (13): Alt Pirineu Ecosystem Simulator, NetLogo Bug Hunt Predator-Prey, CoMSES test-bed ecological model, Proyectos similares de simulación (doc), Multi-Agent RL ecosistemas alpinos (bioRxiv 2025), NetLogo Wolf-Sheep Predation, Modelo socioecológico Pirineo catalán (ODE, 2026), 10 búsquedas web (2026-06-22) (+5 more)

### Community 36 - "Errors E1-E10 invalidating results (c36)"
Cohesion: 0.17
Nodes (12): Tick System — Fixes & Full-Scale Results, Hibernation when cold fix, Predator extinction bottleneck, E1: Inverted snow line, E2: Predation creates biomass, E3: Scavengers without carrion in diet loader, E5: Double food charge in parallel cells, E9: Offspring born free of energy cost (+4 more)

### Community 37 - "validate_energy.py (c37)"
Cohesion: 0.29
Nodes (9): main(), midpoint(), plot_validation(), read_diet_proportions(), read_vertebrates(), update_dee_tsv(), validate_species(), write_validation_report() (+1 more)

### Community 38 - "Plan de Simulacion Agent-Based PNAP en P (c38)"
Cohesion: 0.23
Nodes (12): Ecosystem Simulator Rust Port doc, Biological references (Kleiber, West, Nagy, Hoyt), Kleiber's law BMR = 70*M^0.75, Python to Rust port status, Plan de Simulacion Agent-Based PNAP en Python, Simulator architecture (src/sim modules), Daily timestep flow, Real data pipeline (DEM ICGC + MCSC to grid) (+4 more)

### Community 39 - "Pla d'Implementació: Sistema de Ticks (3 (c39)"
Cohesion: 0.27
Nodes (10): Activity costs from costos_actividad.tsv (MET), AgentFSMState finite state machine, Circadian activity patterns, decay_carcasses_tick() grid decay, Pla d'Implementació: Sistema de Ticks (30s) amb FSM i GIF, Simulation::tick() 2880 ticks/day loop, tick_energy() per-tick energy function, TickOutcome struct (+2 more)

### Community 40 - "Flora y vegetación (doc) (c40)"
Cohesion: 0.20
Nodes (11): Flora y vegetación (doc), Especies emblemáticas y protegidas, Flora vascular del PNAP (1.465-1.765 sp.), Hábitats de interés comunitario, Leontopodium alpinum (edelweiss), Pino negro (Pinus uncinata), Pisos bioclimáticos, Grid SRTM Vall de Cardós 25 m (375x502) (+3 more)

### Community 41 - "Paper: ABM trophic dynamics Alt Pirineu (c41)"
Cohesion: 0.25
Nodes (11): Paper: ABM trophic dynamics Alt Pirineu, Energía de los recursos (kcal/g), Matriz trófica (103+ interacciones), Proporciones de dieta, Grafo de red trófica, Visualizador interactivo de la red trófica, Clasificación de recursos (plantas, invertebrados, vertebrados), Proporciones de dieta (+3 more)

### Community 42 - "pathfinding.py (c42)"
Cohesion: 0.31
Nodes (6): a_star(), _a_star_numba(), astar_batch(), compute_path_cost(), _heuristic(), _neighbors_numba()

### Community 43 - "Proyectos similares de simulacion de eco (c43)"
Cohesion: 0.24
Nodes (10): proyectos_similares README, Proyectos similares de simulacion de ecosistemas, Alt Pirineu Ecosystem Simulator (this project), NetLogo Bug Hunt Predator-Prey, CoMSES test-bed ecological model (evolve.nlogo), Multi-Agent RL alpine ecosystems (bioRxiv 2025), NetLogo Wolf-Sheep Predation, P-systems isard model (Univ. Sevilla, MeCoSim) (+2 more)

### Community 44 - "Season (c44)"
Cohesion: 0.18
Nodes (6): default_temp_fn(), Season, Autumn, Spring, Summer, Winter

### Community 45 - "ursina_viewer.py (c45)"
Cohesion: 0.20
Nodes (5): _init_display(), input(), load_elevation_grid(), main(), update()

### Community 47 - "Terrain Cartography Dashboard (Alt Pirin (c47)"
Cohesion: 0.31
Nodes (9): Parc Natural de l'Alt Pirineu - Vall de Cardos study area (UTM 356000-365000 E, 4712000-4724000 N), Habitat classes (coniferous forest, deciduous forest, scrub, pasture, wetland, rock, water, riparian, snow, anthropic), Terrain Cartography Dashboard (Alt Pirineu, Vall de Cardós, 25 m), Aspect map (Orientacio, 0-360 deg), Slope map (Pendent, 0-60 deg), Terrain Ruggedness Index (TRI) map, Digital Elevation Model map (DEM, ~1000-2700 m), Habitat map (Mapa d'Habitats) (+1 more)

### Community 48 - "Phased plan (Fases 0-6) (c48)"
Cohesion: 0.25
Nodes (9): Emergent carrying capacity (remove imposed density factor), Holling type II functional response, Morris screening calibration, ODD Purpose & Patterns (pattern-oriented modelling), Phased plan (Fases 0-6), --seed reproducibility with per-agent StdRng, species_params.tsv, Holling functional response for predation (+1 more)

### Community 49 - "Base de datos biológica maestra (c49)"
Cohesion: 0.28
Nodes (9): Clústeres funcionales P1/P2/P3 para simulación, Base de datos biológica maestra, Cluster I1 polinizadores, Cluster I2 fitófagos, Cluster I3 depredadores/parasitoides, Cluster P1 plantas entomófilas, Cluster P2 productores independientes, Cluster P3 pastizales (+1 more)

### Community 50 - "Fuentes de Informacion (master source in (c50)"
Cohesion: 0.22
Nodes (9): ECOSYSTEM_VAULT_GUIDE.md, Fuentes de Informacion (master source index), 10 web searches of 2026-06-22, referencias README, topografia README, Topografia y Terreno del PNAP, Geology of PNAP (Alpine orogeny, Cambro-Ordovician), Glacial landforms (U valleys, Certascan lake) (+1 more)

### Community 51 - "Energy validation figure (DEE vs Nagy 20 (c51)"
Cohesion: 0.29
Nodes (8): Energy validation figure (DEE vs Nagy 2005, IEP balance, allometry), Allometric scaling mass vs DEE, Old DEE (Kleiber + factor 2), Taxon-specific DEE (daily energy expenditure) model, IEP (max intake) vs DEE energy balance, Nagy 2005 field metabolic rate (FMR) reference, Agent energy reserves over time (360-day curve), Average energy falls from 1.4e6 to 0.4e6 kJ with drop near day 90

### Community 52 - "Vall de Cardos subcuenca grid (375x502,  (c52)"
Cohesion: 0.32
Nodes (8): Pyrenean socioecological ODE model (Jolivet et al. 2026), Pisos bioclimaticos (Montano, Subalpino, Alpino, Nival), Vall de Cardos subcuenca grid (375x502, 25m, SRTM), Rust CLI (clap) and outputs, Data loading (TSV terrain, GeoTIFF, flat fallback), Grid and Cell (25m, row-major), 10 functional habitats, Terrain grid spec (25m, EPSG:25831)

### Community 53 - "Food web (foodweb.rs: diets, trophic lin (c53)"
Cohesion: 0.25
Nodes (8): Hydrography (Noguera Pallaresa, wetlands), Energy intake and assimilation efficiency, Food web (foodweb.rs: diets, trophic links), Diet-based foraging (do_forage), pool_consumption_step, Population pools (fish, herps, passerines, micromammals, bats), predation_step (agent-to-agent predation), scavenging_step / consume_carcass

### Community 54 - "Agent behaviors (herbivore, carnivore, o (c54)"
Cohesion: 0.25
Nodes (8): Agent behaviors (herbivore, carnivore, omnivore, bird), A* movement cost (slope x snow x terrain), Individual variation and stochastic behavior, MET activity costs and DEE, A* pathfinding (pathfinding.rs), Rayon parallelization (decision/execution), Seasonal snow cover model, Temperature model (adiabatic lapse rate)

### Community 55 - "Base d'especies i interaccions trofiques (c55)"
Cohesion: 0.43
Nodes (8): Invertebrate pools I1/I2/I3 (vertical trophic chain), Plant pools P1/P2/P3 (logistic growth), species_data README, Base d'especies i interaccions trofiques (biodata source document), invertebrate_clusters.tsv, plant_clusters.tsv, trophic_matrix.tsv, vertebrates.tsv

### Community 56 - "Nagy (2005) Field metabolic rate and bod (c56)"
Cohesion: 0.29
Nodes (7): Intake linear-with-mass scaling bug, Kleiber-based energy metabolism (BMR, MET, DEE), Doubly labeled water method, FMR allometric scaling (FMR = a·M^b), Nagy (2005) Field metabolic rate and body size, update_agent_energies_batch, Kleiber's law (BMR = 70 × M^0.75)

### Community 57 - "Ecosystem Simulator vault welcome (Bienv (c57)"
Cohesion: 0.29
Nodes (7): Energy density from energia_recursos.tsv, Ecosystem Simulator vault welcome (Bienvenido), Energy data files (energia_recursos, dee_estimado, costos_actividad), Interactive trophic graph visualizer (HTML), Academic paper draft (paper/), Terrain GeoTIFF rasters (DEM, slope, aspect, TRI, pisos, habitat, biomass), PanTHERIA overview (mammal trait database; PDF unreadable)

### Community 58 - "Topografía y terreno (doc) (c58)"
Cohesion: 0.38
Nodes (7): Geología del parque, Topografía y terreno (doc), Geología cambro-ordovícica y alpina, Hidrografía (Noguera Pallaresa), Fenómenos kársticos (Cigalera de Valeran), Modelado glaciar, Orografía (Pica d'Estats 3.143 m)

### Community 59 - "Visualizador de Red Trófica (HTML) (c59)"
Cohesion: 0.38
Nodes (7): Visualizador de Red Trófica (HTML), applyFilters, buildNetworkFromData, downloadPNG, fitToScreen, loadGraphFromFile, updateStatistics

### Community 60 - "PyO3 Rust extension module (c60)"
Cohesion: 0.33
Nodes (6): process_foraging_batch, find_best_cells_batch, Python-Rust Hybrid Approach, PyO3 Rust extension module, Python simulator (src/sim, Numba), Python legacy simulation (src/sim_legacy)

### Community 62 - "io.rs (c62)"
Cohesion: 0.62
Nodes (4): assign_biomass_defaults(), assign_habitat_from_piso(), load_terrain_from_geotiff(), load_terrain_from_tsv()

### Community 63 - ".initialize() (c63)"
Cohesion: 0.29
Nodes (4): load_activity_costs(), load_energy_data(), find_spawn_cells(), scale_to_area()

### Community 67 - "ecosystem/data (simulation data) (c67)"
Cohesion: 0.40
Nodes (6): Functional cluster mapping for agent-based model, Load full trophic_matrix.tsv instead of 15 hardcoded links, Species and trophic network data files, ecosystem/data (simulation data), Terrain data pipeline (SRTM → rasters + terrain_cells.tsv), trophic_matrix.tsv (221 interactions)

### Community 68 - "Alt Pirineu Ecosystem Simulation Project (c68)"
Cohesion: 0.40
Nodes (5): Actual simulated area (~11,700 ha, not 80,000 ha), Obsidian vault 'ecosystem', Guía para Agentes de IA - Vault Ecosystem, Parc Natural de l'Alt Pirineu (PNAP), Alt Pirineu Ecosystem Simulation Project (overview)

### Community 69 - "Trophic network of Alt Pirineu Natural P (c69)"
Cohesion: 0.33
Nodes (6): Trophic network of Alt Pirineu Natural Park (node-link plot), Recursos Vegetals hub node, Taxonomic groups legend (mammals 18, plants 11, birds 5, amphibians 4), Colored trophic network with typed interaction edges (Alt Pirineu), Predation edges dominate (red) toward vertebrate predators, Recursos Vegetals central producer node

### Community 70 - "Clústers vertebrados V-* (c70)"
Cohesion: 0.50
Nodes (5): Clústers vertebrados V-*, V-MicromamífersPetits, V-Passeriformes, V-RapinyairesNocturnesGrans, V-Ratpenats

### Community 71 - "Vall de Cardos terrain (500x375 grid, UT (c71)"
Cohesion: 0.50
Nodes (5): Vall de Cardos 3D low perspective terrain plot, Terrain aspect (orientation) map, Biomass I1 map (0-0.035 kg), Biomass I2 map (0-0.16 kg), Vall de Cardos terrain (500x375 grid, UTM)

### Community 72 - "Per-species terrain biomass raster layer (c72)"
Cohesion: 0.60
Nodes (5): Biomass map I3 (0.01-0.09 kg, 500x375 grid), Biomass map P1 (0-2.4 kg, 500x375 grid), Biomass map P2 (riparian/river-linked, 0.05-1.1 kg), Biomass map P3 (patchy high-biomass clusters, 0-4.8 kg), Per-species terrain biomass raster layers (Greens colormap, kg)

### Community 73 - "Pendent del Terreny (slope map, 0-60 deg (c73)"
Cohesion: 0.60
Nodes (5): Pendent del Terreny (slope map, 0-60 deg), Index de Rugositat TRI map, UTM study area (356000-365000E, 4712000-4724000N, ~9x12 km), Valley/drainage network (low slope, low TRI corridors), Terrain elevation colormap texture

## Ambiguous Edges - Review These
- `Alt Pirineu Ecosystem Simulation Project (overview)` → `Actual simulated area (~11,700 ha, not 80,000 ha)`  [AMBIGUOUS]
  docs/HOJA_DE_RUTA.md · relation: conceptually_related_to
- `Oso pardo (Ursus arctos)` → `P-systems de isards (MeCoSim)`  [AMBIGUOUS]
  ecosystem/informacion_unordered/proyectos_similares/simulaciones_ecosistemas.md · relation: conceptually_related_to

## Knowledge Gaps
- **192 isolated node(s):** `alt-pirineu-sim`, `run.sh script`, `run_simulation.sh script`, `sim_deep.sh script`, `LC_NUMERIC` (+187 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 404 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Alt Pirineu Ecosystem Simulation Project (overview)` and `Actual simulated area (~11,700 ha, not 80,000 ha)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `TerrainGrid` connect `TerrainGrid (c8)` to `numpy (c0)`, `Simulation (c9)`, `pathfinding.py (c42)`, `grid.py (c17)`, `Agent (c21)`, `OmnivoreAgent (c23)`, `EnergyBudget (c25)`, `CarnivoreAgent (c29)`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `TerrainGrid` (e.g. with `Agent` and `AgentAction`) actually correct?**
  _`TerrainGrid` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `alt-pirineu-sim`, `run.sh script`, `run_simulation.sh script` to the rest of the system?**
  _192 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `numpy (c0)` be split into smaller, more focused modules?**
  _Cohesion score 0.050693069306930696 - nodes in this community are weakly interconnected._
- **What is the exact relationship between `Oso pardo (Ursus arctos)` and `P-systems de isards (MeCoSim)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Estat Actual (simulator state, Catalan)` connect `Mancances ecològiques i pla d'acció (c34)` to `Nagy (2005) Field metabolic rate and bod (c56)`, `numpy (c0)`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._