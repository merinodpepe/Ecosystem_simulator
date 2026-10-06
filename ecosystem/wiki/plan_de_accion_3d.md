# Pla d'Acció 3D — Visor interactiu per a l'Ecosistema d'Alt Pirineu

Objectiu: convertir el visor 3D d'Ursina d'un "screensaver" en una eina útil
per a la simulació. Ordre d'implementació: **1 → 3 → 2**.

---

## Fase 1 — Integració simulació real

Fusionar el bucle de simulació amb el visor: que `simulation.py` exporti
snapshots que el visor pugui carregar directament.

### 1.1 Corregir `ursina_sim_bridge.export_snapshot()`

**Fitxer**: `src/ursina_sim_bridge.py`

**Problema**: la funció accedeix a `a.species_nickname` i `a.guild`, que NO
existeixen en els agents reals de la simulació. Els agents tenen
`a.common_name` (ex: "Isard") i `a.trophic_level` (ex: "HERBIVORE").

**Canvi**: substituir els atributs incorrectes:

```python
agent_list.append({
    "id": a.agent_id,
    "species_key": a.species_key,
    "nick": getattr(a, "common_name", a.species_key),
    "guild": getattr(a, "trophic_level", "HERBIVORE"),
    "x": a.state.x,
    "y": a.state.y,
    "energy": a.state.energy_kcal,
    "alive": a.is_alive,
    "age": a.state.age_days,
})
```

**Test**: generar snapshots de test amb `generate_test_snapshots()` i
comprovar que els camps `nick` i `guild` són correctes.

### 1.2 Corregir `sim.io.export_snapshot_json()`

**Fitxer**: `src/sim/io.py` (línies 191-216)

**Problema**: l'exportador actual fa servir noms de camp incompatibles
amb el visor:
- `"species"` enlloc de `"species_key"`
- `"energy_kcal"` enlloc de `"energy"`
- `"age_days"` enlloc de `"age"`
- No exporta `"nick"` ni `"guild"`
- Filtra només agents vius (perd els morts)

**Canvi**: modificar perquè exporti camps compatibles amb el visor:

```python
def export_snapshot_json(agents, pools, day, path):
    data = {
        "day": day,
        "agents": [
            {
                "id": a.agent_id,
                "species_key": a.species_key,
                "nick": a.common_name,
                "guild": a.trophic_level,
                "x": a.state.x,
                "y": a.state.y,
                "energy": round(a.state.energy_kcal, 1),
                "alive": a.is_alive,
                "age": round(a.state.age_days, 1),
                "pregnant": a.state.is_pregnant,
            }
            for a in agents
        ],
        "pools": {k: round(v, 1) for k, v in pools.items()},
    }
    # escriure JSON
```

Així el visor pot carregar directament els snapshots del sim (accepta tant
`{"agents": [...]}` com `[...]` pla).

**Test**: executar simulació 1 dia, comprovar que el JSON generat té els
camps correctes i que el visor el pot carregar.

### 1.3 Canviar `simulation._snapshot()` al directori i nom correctes

**Fitxer**: `src/sim/simulation.py` (línia ~347)

**Problema**: escriu a `output/snap_0000.json` però el visor espera
`output/snapshots/agents_day_00000.json`.

**Canvi**: modificar `_snapshot()` perquè:
1. Creï directori `output/snapshots/` si no existeix
2. Escrigui amb nom `agents_day_{day:05d}.json`
3. Guardi també `snap_0000.json` antic per compatibilitat (opcional)

```python
def _snapshot(self, day, log_path):
    snap_dir = Path("output/snapshots")
    snap_dir.mkdir(parents=True, exist_ok=True)
    path = snap_dir / f"agents_day_{day:05d}.json"
    export_snapshot_json(
        agents=self.agents,
        pools=self.env.pools.resources if hasattr(self.env, 'pools') else {},
        day=day,
        path=path,
    )
```

### 1.4 Ajustar `simulation.run()` per a snapshot_every=1 en mode demo

**Fitxer**: `src/sim/simulation.py`

Per defecte `snapshot_every=100`, massa espaiat per al visor. En mode
demo (o si el visor està actiu), hauria de ser 1.

**Canvi opcional**: acceptar `snapshot_every` al constructor de Simulation
i que `run_simulation.py` el passi com a paràmetre.

### 1.5 Test d'integració complet

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from sim.simulation import Simulation
sim = Simulation(total_days=5, snapshot_every=1)
sim.run()
# Comprovar que output/snapshots/agents_day_*.json existeix
import json
from pathlib import Path
snaps = sorted(Path('output/snapshots').glob('agents_day_*.json'))
print(f'Generats {len(snaps)} snapshots')
# Comprovar que el visor els pot carregar
from ursina_viewer import TerrainViewer
viewer = TerrainViewer()
viewer.load_snapshot_sequence('output/snapshots')
viewer.load_snapshot(snaps[0])
print(f'Carregats {len(viewer.agent_entities)} agents')
"
```

---

## Fase 3 — Càmera segueix-agent (tecla F)

Permetre seguir un agent seleccionat amb la càmera.

### 3.1 Preparar `TerrainViewer` per a follow-mode

**Fitxer**: `src/ursina_viewer.py`, dins `__init__` de `TerrainViewer`

Afegir atributs d'estat:

```python
self.follow_target = None           # Agent3D a seguir
self.follow_mode = False            # toggle
self._f_key_held = False            # debounce
```

### 3.2 Detectar tecla F a `update()`

Afegir al final de `TerrainViewer.update()`:

```python
# Toggle follow-mode
if held_keys["f"] and not self._f_key_held:
    self._f_key_held = True
    if self.follow_mode:
        # Sortir de follow: restaurar EditorCamera
        self.follow_mode = False
        self.follow_target = None
        self.ecamera.enabled = True
    else:
        # Entrar a follow: agafar agent més proper o seleccionat
        target = self._get_follow_target()
        if target:
            self.follow_mode = True
            self.follow_target = target
            self.ecamera.enabled = False  # desactivar EditorCamera
if not held_keys["f"]:
    self._f_key_held = False

# Actualitzar càmera en mode follow
if self.follow_mode and self.follow_target:
    self._update_follow_camera()
```

### 3.3 Mètode `_get_follow_target()`

Seleccionar l'agent més proper al centre de la pantalla (o l'agent
seleccionat prèviament):

```python
def _get_follow_target(self):
    if self.selected_agent and self.selected_agent.enabled:
        return self.selected_agent
    # Cercar l'agent més proper a la càmera
    if not self.agent_entities:
        return None
    cam_pos = camera.position
    best = min(
        self.agent_entities.values(),
        key=lambda ae: (ae.position - cam_pos).length(),
        default=None,
    )
    return best if best and best.enabled else None
```

### 3.4 Mètode `_update_follow_camera()`

Lerp suau cap a la posició de l'agent:

```python
def _update_follow_camera(self):
    target_pos = self.follow_target.position
    # Posició desitjada: darrere i per sobre de l'agent
    desired = target_pos + Vec3(5, 8, 5)
    # Lerp suau
    camera.position += (desired - camera.position) * time.dt * 3
    camera.look_at(target_pos)
```

**Alternativa**: fer-ho relatiu a la direcció de moviment de l'agent,
però una posició fixa偏移 és suficient per a la primera versió.

### 3.5 HUD indicator

Afegir a `_setup_ui()`:

```python
self.follow_text = Text(
    text="",
    position=(0.65, 0.39),
    scale=1.0,
    color=color.lime,
    parent=ui_parent,
)
```

Actualitzar a `update()`:

```python
self.follow_text.text = f"Seguint: {self.follow_target.nick}" if self.follow_mode else ""
```

### 3.6 Test

```bash
# En una màquina amb display:
python src/ursina_viewer.py --snapshots output/snapshots_test
# Pitjar F per seguir l'agent més proper
# Pitjar F de nou per sortir de follow
```

---

## Fase 2 — Panell d'informació al clicar (Click Info)

En clicar un agent, mostrar una finestra amb les seves estadístiques.

### 2.1 Afegir `collider` i `on_click` a `Agent3D`

**Fitxer**: `src/ursina_models.py`, dins `Agent3D.__init__`

```python
def __init__(self, ..., **kwargs):
    super().__init__(
        ...,
        collider='box',          # Permet raycasting del ratolí
        on_click=self._on_click,
        **kwargs
    )
```

Implementar `_on_click`:

```python
def _on_click(self):
    if _viewer_instance:
        _viewer_instance.select_agent(self)
```

### 2.2 Mètode `select_agent(agent)` a `TerrainViewer`

**Fitxer**: `src/ursina_viewer.py`

```python
def select_agent(self, agent):
    self.selected_agent = agent
    self._show_agent_info(agent)

def _show_agent_info(self, agent):
    # Netejar info anterior
    self._clear_info_panel()

    # Dades a mostrar
    lines = [
        f"Agent: {agent.agent_id}",
        f"Especie: {agent.species_key}",
        f"Nom: {agent.nick}",
        f"Gremi: {agent.guild}",
        f"Posicio: ({agent.x:.0f}, {agent.y:.0f})",
    ]

    # Crear Text entities
    y_start = 0.2
    self._info_texts = []
    for i, line in enumerate(lines):
        t = Text(
            text=line,
            position=(-0.3, y_start - i * 0.04),
            scale=1.0,
            color=color.white,
            parent=camera.ui,
        )
        self._info_texts.append(t)

def _clear_info_panel(self):
    for t in getattr(self, '_info_texts', []):
        t.disable()
    self._info_texts = []
```

### 2.3 Tancar panell en clicar a fora

Detectar clic en espai buit a `update()`:

```python
if mouse.left and mouse.hovered_entity is None:
    self.deselect_agent()

def deselect_agent(self):
    self.selected_agent = None
    self._clear_info_panel()
```

### 2.4 Enriquir informació amb dades de la simulació

Si el snapshot inclou `energy` i `age`, mostrar-los:

```python
extra_lines = []
if "energy" in ad:
    extra_lines.append(f"Energia: {ad['energy']:.0f} kcal")
if "age" in ad:
    extra_lines.append(f"Edat: {ad['age']:.0f} dies")
```

Modificar `Agent3D` per emmagatzemar les dades extres:

```python
self.stats = {
    "energy": ad.get("energy", 0),
    "age": ad.get("age", 0),
    "alive": ad.get("alive", True),
}
```

### 2.5 Test

```bash
# En una màquina amb display:
python src/ursina_viewer.py --snapshots output/snapshots_test
# Clicar sobre un agent per veure info
# Clicar sobre fons per tancar
```

---

## Resum de fitxers a modificar

| Fitxer | Canvis |
|--------|--------|
| `src/ursina_sim_bridge.py` | Corregir `common_name`/`trophic_level` (línia ~45) |
| `src/sim/io.py` | Camps compatibles amb visor (línies ~191-216) |
| `src/sim/simulation.py` | Directori/nom snapshot correctes (línia ~347) |
| `src/ursina_models.py` | Afegir `collider='box'`, `on_click`, `stats` dict |
| `src/ursina_viewer.py` | Follow-camera (mode F), panell info, selecció |
| `src/ursina_launcher.py` | Argument `--snapshot-every` (opcional) |

## Tests de regressió

Després de cada fase:

```bash
# 1. Parseig de tots els fitxers
python -c "import py_compile; [py_compile.compile(f'src/{f}', doraise=True) for f in ['ursina_viewer.py','ursina_models.py','ursina_sim_bridge.py','ursina_launcher.py','sim/io.py','sim/simulation.py']]"

# 2. Test d'integració (headless)
python src/ursina_launcher.py --headless --test-snapshots --view

# 3. Test de simulació curta
python -c "
import sys; sys.path.insert(0,'src')
from sim.simulation import Simulation
sim = Simulation(total_days=3, snapshot_every=1)
sim.run()
print('OK')
"
```
