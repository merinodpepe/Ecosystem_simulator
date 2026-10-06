# Pipeline Master — Visor 3D Alt Pirineu

Orquestra tot el pipeline en un sol comandament:

**dades del terreny** → **mesh 3D** → **simulació** → **visor interactiu**

## Visió general

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  terrain_cells   │────▶│  export_mesh.py  │────▶│  terrain.obj     │
│  .tsv            │     │  (step 1)        │     │  (45K vèrtexs)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                          │
                                                          ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  simulación      │────▶│  snapshots       │────▶│  ursina_viewer   │
│  run_simulation  │     │  agents_day_*.   │     │  .py             │
│  .py             │     │  json            │     │  (3D interactiu) │
│  (step 2)        │     │  (step 2)        │     │  (step 3)        │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                                                            
        ▼ (alternativa)                                               
┌──────────────────┐                                                 
│  test snapshots  │────▶ (saltar-se la simulació real)               
│  sintètics       │                                                 
└──────────────────┘                                                 
```

## Ús ràpid

### Demo completa (tot automàtic)

```bash
python src/pipeline.py --full
```

Preguntarà confirmació a cada pas. Per a entorns no interactius:

```bash
python src/pipeline.py --full --headless
```

### Demo ràpida (30 dies, sense finestra)

```bash
python src/pipeline.py --demo --headless
```

### Provar el visor amb dades sintètiques

```bash
python src/pipeline.py --test-only --headless
```

### Només el visor (si ja teniu snapshots)

```bash
python src/pipeline.py --full --skip-mesh --skip-sim --headless
```

## Arguments complets

| Argument | Per defecte | Descripció |
|----------|-------------|------------|
| `--full` | — | Mode automàtic: executa tot sense preguntar |
| `--demo` | — | Demo ràpida (30 dies, 50×50) |
| `--headless` | — | Visor sense finestra (rendering offscreen) |
| `--skip-mesh` | — | Omet exportació del mesh 3D |
| `--skip-sim` | — | Omet simulació/snapshots |
| `--test-only` | — | Usa snapshots sintètics (no simulació real) |
| `--step` | 2 | Factor de submostreig del mesh |
| `--vertical-scale` | 0.03 | Exageració vertical del relleu |
| `--sim-days` | 365 | Dies de la simulació |
| `--snapshot-every` | 10 | Cada quants dies es guarda snapshot |
| `--test-days` | 60 | Nombre de snapshots sintètics |
| `--test-agents` | 30 | Nombre d'agents sintètics |

## Què fa cada pas

### Pas 1: Exportar mesh

Llegeix `ecosystem/data/terrain_cells.tsv` i genera:

- `output/terrain_mesh/terrain.obj` — malla 3D (45.001 vèrtexs, 89.126 triangles)
- `output/terrain_mesh/terrain.mtl` — material
- `output/terrain_mesh/terrain_texture.png` — textura per elevació
- `output/terrain_mesh/terrain_metadata.json` — metadades

### Pas 2: Simulació o snapshots

**Opció A — Simulació real** (`run_simulation.py`):
- Carrega dades reals del terreny (DEM, habitats, biomassa)
- Inicialitza poblacions de 18 espècies
- Executa `N` dies amb ecologia (neu, plantes, agents, reproducció)
- Exporta snapshots a `output/snapshots/agents_day_XXXXX.json`

**Opció B — Snapshots sintètics** (`generate_test_snapshots`):
- No requereix simulació
- Genera `N` agents amb moviment aleatori
- Útil per provar el visor sense esperar la simulació
- Exporta a `output/snapshots_test/agents_day_XXXXX.json`

### Pas 3: Visor 3D

Llança `ursina_viewer.py` amb els snapshots generats:

| Tecla | Acció |
|-------|-------|
| `WASD` | Moure càmera |
| `Q` / `E` | Pujar / baixar |
| `R` | Reset càmera |
| `P` | Pausar / reprendre |
| `+` / `-` | Velocitat de reproducció |
| `F` | Seguir agent més proper |
| Clic agent | Info (espècie, gremi, energia, edat) |
| Clic buit | Tancar info |
| `ESC` | Sortir |

## Exemples d'ús

```bash
# Desenvolupament: tot sense finestra
python src/pipeline.py --full --headless

# Presentació: finestra interactiva
python src/pipeline.py --full

# Servidor: només processar, sense visor
python src/pipeline.py --full --skip-view

# Tests ràpids: snapshots sintètics + visor headless
python src/pipeline.py --test-only --test-days 10 --test-agents 50 --headless

# Simulació llarga + visor
python src/pipeline.py --full --sim-days 3650 --snapshot-every 100

# Només regenerar mesh
python src/pipeline.py --full --skip-sim --headless

# Amb valors personalitzats
python src/pipeline.py --full --step 1 --vertical-scale 0.05 --sim-days 30 --headless
```

## Fitxer

`src/pipeline.py` — script únic, sense dependències addicionals.
