# Execució — Simulador d'Ecosistema de l'Alt Pirineu

## Requisits previs

```bash
# Rust toolchain (simulació)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python + dependències (visualització, pipeline, processament)
pip install numpy pandas matplotlib ursina Pillow
```

## 1. Simulació (Rust)

### Test ràpid (50×50, 30 dies)
```bash
./run_simulation.sh            # mode test per defecte: 100×100, 365 dies
./run.sh                       # mode interactiu (tria 1=ràpid, 2=mig, 3=complet)
```

### Execució directa amb cargo
```bash
cd simulator
cargo run --release -- --width 50 --height 50 --days 30 --output output_demo
```

### Paràmetres disponibles
| Flag | Per defecte | Descripció |
|------|-------------|------------|
| `--width` | 100 | Amplada del grid (cel·les) |
| `--height` | 100 | Alçada del grid (cel·les) |
| `--days` | 365 | Dies de simulació |
| `--output` | `output` | Directori de sortida |
| `--data-dir` | `../ecosystem/data` | Directori de dades |
| `--res` | 25 | Resolució (m/cel·la) |

### Full-scale (375×502, grid complet)
```bash
./run_simulation.sh --full --days 365
# o directament:
cd simulator && cargo run --release -- --width 375 --height 502 --days 365 --output output_full
```

## 2. Visualització dels resultats

### Gràfics 2D (poblacions, energia)
```bash
# Generats automàticament per run_simulation.sh
# o manualment:
python src/visualize_simulation.py --dir simulator/output_demo --save figures
```

### Visor 3D interactiu (Ursina)
```bash
# Amb snapshots de test (no cal simulació)
python src/ursina_launcher.py --test-snapshots --view

# Amb snapshots d'una simulació real
python src/ursina_launcher.py --view --snapshots simulator/output_demo
```

**Controls del visor:** `WASD` moure, `Q/E` pujar/baixar, `R` reset càmera, `P` pausa, `+`/`-` velocitat, `F` seguir agent, clicar agent per veure info, `ESC` sortir.

### Exportar mesh 3D del terreny
```bash
python src/export_terrain_mesh.py --step 2
# Genera output/terrain_mesh/terrain.obj + .mtl + textura
```

## 3. Pipeline complet (mesh → simulació → visor)

```bash
# Automàtic (tot seguit)
python src/pipeline.py --full

# Interactiu (pregunta cada pas)
python src/pipeline.py

# Demo ràpida
python src/pipeline.py --demo --headless
```

## 4. Processament de terreny (un sol cop)

```bash
# Genera terrain_cells.tsv + ràsters a ecosystem/data/
python src/process_terrain.py
```

## 5. Validació energètica

```bash
python src/validate_energy.py
# Compara DEE estimat vs Nagy 2005, genera validacion_energia.tsv
```

## 6. Outputs de la simulació

El Rust genera tres fitxers per execució dins `simulator/output_*/`:

| Fitxer | Format | Contingut |
|--------|--------|-----------|
| `simulation_log.csv` | CSV | `day,n_alive,n_dead,total_plant_kg,total_invert_kg,total_carcass_kg,avg_energy,season,temp_avg` |
| `species_population.csv` | CSV | `day,sp1,sp2,...` (comptes per espècie cada dia) |
| `snap_NNNN.json` | JSON | Snapshot complet: agents, pools, season, temperatura |

## 7. Scripts disponibles

| Script | Funció |
|--------|--------|
| `run_simulation.sh` | Executa Rust + genera figures |
| `run.sh` | Mode interactiu (tria ràpid/mig/complet) |
| `simulator/run_quick.sh` | Test ràpid 50×50, 30 dies |
| `simulator/run_medium.sh` | Test mig 200×200, 100 dies |
| `simulator/run_deep.sh` | Test profund 400×400, 365 dies |
