# Alt Pirineu Ecosystem Simulation Project

## 🎯 Project Vision
Advanced agent-based simulation of the Parc Natural de l'Alt Pirineu (PNAP) ecosystem, modeling complex trophic interactions, energy flows, and emergent ecological dynamics using real-world data.

## 📍 Study Area: Parc Natural de l'Alt Pirineu
- **Location**: Catalan Pyrenees, Spain
- **Size**: ~80,000 hectares
- **Elevation range**: 650m – 3,143m (Pica d'Estats)
- **Key features**: Alpine meadows, subalpine forests, glacial lakes, high biodiversity hotspot

## ⚙️ Technical Architecture

### Simulation Engine — Rust (`simulator/`)
- **21 species** (including *Ursus arctos*, *Lutra lutra*, *Galemys pyrenaicus*)
- **Tick-based**: 2880 ticks/day (30s per tick), FSM per agent
- **FSM states**: Idle, Travel, ForageSearch, ForageEat, HuntStalk, HuntChase, EatCarcass, Drink, Sleep, Dead
- **Energy**: Kleiber BMR + MET-based activity costs, carcass decomposition (95%/day)
- **Spatial**: Grid-based 25m resolution, A* pathfinding with BinaryHeap
- **Features**: hibernation, gender (male/female), carrion scavenging, personality (boldness), circadian rhythm, logistic plant growth, carcass pool
- **10 FSM states, 7 population pools** (plants, inverts, fish, herps, passerines, micromammals, bats)
- **Parallelised** with Rayon (`par_iter_mut()`)

### Terrain Data Pipeline — Python (`src/process_terrain.py`)
- SRTM → slope, aspect, TRI, pisos bioclimàtics, habitat, biomass
- Output: GeoTIFF rasters + `terrain_cells.tsv` (180K cells)

### 3D Visualisation — Python
- **Mesh export**: `src/export_terrain_mesh.py` → OBJ/MTL
- **Interactive viewer**: `src/ursina_viewer.py` (Ursina engine)
- **Launcher**: `src/ursina_launcher.py`
- **Orchestrator**: `src/pipeline.py` (mesh → simulation → viewer)

### Validation — Python
- `src/validate_energy.py`: DEE validation vs Nagy (2005)
- Matches `ecosystem/data/validacion/`

### Data (`ecosystem/data/`)
| Category | Files |
|----------|-------|
| Terrain (7 rasters) | DEM 25m, slope, aspect, TRI, pisos, habitat, biomass |
| Grid | `terrain_cells.tsv` (180K cells) |
| Species | `vertebrates.tsv` (38 species), `invertebrate_clusters.tsv`, `plant_clusters.tsv` |
| Trophic | `trophic_matrix.tsv` (221 interactions), `dieta_proporciones.tsv` |
| Energy | `energia_recursos.tsv`, `dee_estimado.tsv`, `costos_actividad.tsv` |
| Graphs | `ecosystem_graph_standard.json`, `ecosystem_graph_optimized.json` |

## 🗂️ Repository Structure
```
/
├── simulator/                  # Rust simulation engine
│   ├── src/sim/                # Simulation core (FSM, energy, grid, foodweb, pools, etc.)
│   ├── src/main.rs             # CLI entry point
│   ├── Cargo.toml              # Rust dependencies
│   ├── output_v5/              # Reference simulation (700 days)
│   ├── output_calibrated/      # Calibration run (365 days)
│   └── output_full_scale/      # Full-grid run (100 days)
├── src/
│   ├── pipeline.py             # Master pipeline: mesh → sim → viewer
│   ├── process_terrain.py      # Terrain processing (SRTM → TSV + rasters)
│   ├── export_terrain_mesh.py  # 3D mesh generator (OBJ)
│   ├── ursina_viewer.py        # Ursina 3D viewer
│   ├── ursina_launcher.py      # Unified viewer launcher
│   ├── visualize_simulation.py # Post-simulation plots
│   ├── validate_energy.py      # Energy validation
│   └── sim_legacy/             # Python simulation (legacy reference)
├── ecosystem/
│   ├── data/                   # All simulation data (terrain, species, energy)
│   └── wiki/                   # Documentation (català)
├── species_data/               # Species TSV files
├── biodata/                    # Source biological notes
├── data/terrain/               # Raw SRTM tile
├── run_simulation.sh           # Run simulation + figures
├── run.sh                      # Interactive runner
└── pyproject.toml              # Python dependencies (visualisation + terrain tools)
```

## 🚀 Quick Start
```bash
# Simulation (Rust)
./run_simulation.sh                    # test: 100×100, 365 days
./run_simulation.sh --full --days 365  # full: 375×502, 365 days
./run.sh                               # interactive mode

# Pipeline (mesh → sim → viewer)
python src/pipeline.py --full

# Just the viewer (with existing snapshots)
python src/ursina_launcher.py
```

## 📈 Status
- **Simulation engine**: Rust (~3,300 lines), active development
- **Terrain pipeline**: Complete (7 rasters + TSV)
- **3D viewer**: Working (Ursina)
- **Species data**: 38 vertebrates + 6 functional clusters
- **Energy validation**: DEE vs Nagy (2005) passing
- **Python sim** (`src/sim_legacy/`): Legacy reference, superseded by Rust
