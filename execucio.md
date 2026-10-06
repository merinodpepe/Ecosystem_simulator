# Execució del Visor 3D — Alt Pirineu

## Requisits

```bash
pip install ursina pandas numpy
```

## Visor amb dades de test (recomanat)

```bash
# Generar snapshots sintètics + llançar visor
python src/ursina_launcher.py --test-snapshots --view
```

Controls: `WASD` moure, `Q/E` altura, `R` reset càmera, `P` pausa,
`+`/`-` velocitat, `F` seguir agent, clicar agent per veure info,
`ESC` sortir.

## Visor amb simulació real

```bash
# 1. Exportar mesh (un sol cop)
python src/ursina_launcher.py --export-mesh

# 2. Executar simulació (genera snapshots a output/snapshots/)
python -c "
import sys; sys.path.insert(0, 'src')
from sim.simulation import Simulation
sim = Simulation(total_days=365, snapshot_every=10)
sim.initialize()
sim.run()
"

# 3. Llançar visor amb els snapshots
python src/ursina_launcher.py --view --snapshots output/snapshots
```

## Tot en un (mesh + test + visor)

```bash
python src/ursina_launcher.py --run
```

## Sense pantalla (servidor / SSH)

```bash
# --headless fa rendering offscreen (no cal display)
python src/ursina_launcher.py --headless --test-snapshots --view
```

## Només exportar mesh

```bash
python src/ursina_launcher.py --export-mesh --step 2
```

## Fitxers rellevants

| Fitxer | Què fa |
|--------|--------|
| `src/ursina_viewer.py` | Visor 3D interactiu |
| `src/ursina_models.py` | Models 3D dels agents |
| `src/ursina_sim_bridge.py` | Exporta snapshots des de la simulació |
| `src/ursina_launcher.py` | Llançador unificat |
| `src/sim/simulation.py` | Motor de simulació |
| `src/export_terrain_mesh.py` | Genera mesh OBJ des del TSV |
| `ecosystem/wiki/plan_de_accion_3d.md` | Pla d'implementació detallat |
| `ecosystem/wiki/visor_3d_guia.md` | Guia d'usuari completa |
