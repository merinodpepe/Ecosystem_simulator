# Ecosystem Simulator — Parc Natural de l'Alt Pirineu

Benvingut/da al dipòsit de dades i models de l'ecosistema del Parc Natural de l'Alt Pirineu (PNAP).

## 📁 Estructura del vault

```
📂 data/            — Dades font, ràsters, TSVs, grafos, validació
📂 wiki/            — Documentació, explicacions, visualitzador HTML
📂 paper/           — Article acadèmic en elaboració
📄 Bienvenido.md    — Aquest fitxer (punt d'entrada)
```

## 📊 Dades disponibles (`data/`)

### Terreny (7 ràsters GeoTIFF + 1 TSV)
| Fitxer | Descripció |
|--------|------------|
| `terrain_dem_25m.tif` | DEM a 25m (Vall de Cardós, 375×502 cel·les) |
| `terrain_slope.tif` | Pendent en graus |
| `terrain_aspect.tif` | Orientació (0–360°) |
| `terrain_tri.tif` | Terrain Ruggedness Index |
| `terrain_pisos.tif` | Pisos bioclimàtics (Montà/Subalpí/Alpí/Nival) |
| `terrain_habitat.tif` | Mapa d'hàbitats (10 classes funcionals) |
| `terrain_biomass.tif` | Biomassa inicial per cel·la (9 bandes: P1/P2/P3, I1/I2/I3) |
| `terrain_cells.tsv` | Grid complet (180.037 cel·les) |

### Espècies i xarxa tròfica
| Fitxer | Descripció |
|--------|------------|
| `vertebrates.tsv` | 38 espècies/clústers de vertebrats |
| `invertebrate_clusters.tsv` | 3 clústers funcionals d'invertebrats (I1, I2, I3) |
| `plant_clusters.tsv` | 3 clústers funcionals de plantes (P1, P2, P3) |
| `trophic_matrix.tsv` | 221 interaccions tròfiques documentades |
| `dieta_proporciones.tsv` | Proporcions dietètiques per espècie/clúster |
| `ecosystem_graph_standard.json` | Graf tròfic complet (75 nodes, 220 arestes) |
| `ecosystem_graph_optimized.json` | Graf en format compacte per IA |

### Energia
| Fitxer | Descripció |
|--------|------------|
| `energia_recursos.tsv` | Densitat energètica dels recursos (kcal/g) |
| `dee_estimado.tsv` | Despesa energètica diària estimada per espècie |
| `costos_actividad.tsv` | Costos metabòlics per activitat (19 comportaments, MET) |
| `validacion/validacion_energia.tsv` | Validació energètica completa |
| `validacion/validacion_energia.png` | Gràfics de validació |

### Altres
| Fitxer | Descripció |
|--------|------------|
| `referencias/` | PDFs de referència (Nagy 2005, PanTHERIA, etc.) |

## 🌐 Visualitzador interactiu

Obre `wiki/ecosystem_graph_visualizer.html` al navegador per explorar la xarxa tròfica.

## 🔬 Investigació

- `wiki/investigacion_parc_alt_pirineu.md` — Informació detallada del PNAP (espècies, poblacions, terreny)
- `wiki/graph_analysis_explicación.md` — Anàlisi de xarxa tròfica (centralitat, comunitats, cadenes)
- `wiki/validacion_energia.md` — Validació energètica: DEE, IEP, comparació Nagy 2005

## ⚙️ Simulació

- `wiki/simulacion_arquitectura.md` — Arquitectura del motor Python
- `wiki/simulacion_agentes.md` — Sistema d'agents GOAP
- `wiki/simulacion_ejecucion.md` — Com executar simulacions
- `wiki/rust_simulador.md` — Port del simulador en Rust

## 📝 Paper acadèmic

- `paper/paper.md` — Article en elaboració (~800 línies, 4 seccions completes)
- `paper/plan.md` — Progrés i tasques del paper
