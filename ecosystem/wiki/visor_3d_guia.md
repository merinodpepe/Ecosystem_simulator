# Guía del Visor 3D Interactivo

## Descripción General

Visor tridimensional del terreno de Vall de Cardós (Parc Natural de l'Alt Pirineu) con controles de vuelo libre estilo videojuego. Permite visualizar el modelo digital de elevaciones en 3D, los pisos bioclimáticos y los agentes de la simulación ecológica moviéndose por el terreno.

```
terrain_cells.tsv → export_terrain_mesh.py → terrain.obj + texture
                                                    ↓
                                            ursina_viewer.py
                                            (Ursina Engine 3D)
                                           WASD + mouse flight
                                                    ↓
                                            Agent3D entities
                                         (esferas de colores)
                                                    ↑
                                        ursina_sim_bridge.py
                                    snapshots JSON / socket
                                                    ↑
                                            simulation.py
```

---

## Archivos del Sistema

| Archivo | Rol | Dependencias |
|---------|-----|-------------|
| `src/export_terrain_mesh.py` | Genera malla 3D desde TSV | numpy, pandas, Pillow, matplotlib |
| `src/ursina_viewer.py` | Visor 3D interactivo | Ursina, numpy, pandas |
| `src/ursina_models.py` | Modelos 3D de agentes | Ursina |
| `src/ursina_sim_bridge.py` | Puente simulación → visor | numpy |
| `src/ursina_launcher.py` | Lanzador unificado | (todos los anteriores) |

---

## Hito 1: Exportar Malla 3D

### `src/export_terrain_mesh.py`

**Función**: Lee `ecosystem/data/terrain_cells.tsv` y genera una malla 3D del terreno en formato OBJ con textura.

#### Algoritmo

```
1. Cargar TSV → DataFrame Pandas
2. Construir grid 2D de elevación (H×W)
3. Submuestrear con factor step (default: 2)
   - step=2 → 188×251 = 47K vértices
   - step=1 → 375×501 = 188K vértices
4. Para cada celda válida:
   - Crear vértice 3D: (x, elev * escala_vertical, -y)
   - Coordenada UV: (x/W, y/H)
5. Para cada quad 2×2 de celdas válidas:
   - Crear 2 triángulos
6. Calcular normales por vértice (promedio de normales de caras adyacentes)
7. Colorear vértices por elevación (colormap matplotlib "terrain")
8. Exportar:
   - terrain.obj (45K vértices, 89K triángulos)
   - terrain.mtl (material)
   - terrain_texture.png (textura horneada 1024×1024)
```

#### Parámetros

| Flag | Default | Descripción |
|------|---------|-------------|
| `--step` | 2 | Factor de submuestreo (1=resolución completa, 2=mitad, etc.) |
| `--vertical-scale` | 0.03 | Exageración vertical del relieve |
| `--color-by` | elevation | Coloración (actualmente solo elevation) |
| `--output` | output/terrain_mesh | Directorio de salida |

#### Salida

```
output/terrain_mesh/
├── terrain.obj              # Malla 3D (45K vértices, 89K triángulos)
├── terrain.mtl              # Material (referencia a textura)
├── terrain_texture.png      # Textura horneada 1024×1024
└── terrain_metadata.json    # Estadísticas de la malla
```

#### Matemáticas de la malla

```
Vértice V(x, y) = (x, elevation[y,x] * scale, -y)

Normal N(v) = average( Σ cross(v1 - v0, v2 - v0) para cada triángulo que contiene v )

Escala vertical: 0.03 → desnivel de 1745m se convierte en ~52 unidades 3D
```

---

## Hito 2: Visor 3D Interactivo

### `src/ursina_viewer.py`

**Función**: Renderiza la malla del terreno y permite al usuario navegar libremente con controles de cámara estilo videojuego.

#### Inicialización

```
Ursina() ─→ window (1280×720, sky blue)
    ├── EditorCamera (WASD + mouse)
    ├── DirectionalLight (sombras 2048×2048)
    ├── AmbientLight
    ├── Fog (densidad 0.002)
    ├── Terrain Entity (OBJ + textura)
    ├── Reference Grid (opcional)
    └── UI Overlay (FPS, posición, controles, leyenda)
```

#### Controles

| Entrada | Acción |
|---------|--------|
| WASD | Moverse adelante/atrás/izquierda/derecha |
| Shift + WASD | Movimiento rápido |
| Q / E | Subir / bajar cámara |
| Ratón (arrastrar) | Rotar vista orbital |
| Rueda ratón | Zoom in/out |
| R | Resetear posición de cámara |
| P | Pausar/reanudar reproducción |
| + / - | Acelerar / ralentizar reproducción |
| ESC | Salir |

#### Integración con Ursina

El visor usa el hook `update()` de Ursina. Se asigna una referencia global `_viewer_instance` para que Ursina encuentre la función:

```python
_viewer_instance = None

def update():
    """Ursina calls this every frame via reflection."""
    if _viewer_instance:
        _viewer_instance.update()
```

La clase `TerrainViewer` maneja toda la lógica: FPS, actualización de UI, carga de snapshots, control de reproducción.

#### Parámetros CLI

```bash
python src/ursina_viewer.py \
    --mesh output/terrain_mesh \
    --step 2 \
    --vertical-scale 0.03 \
    --snapshots output/snapshots_test \
    --no-grid
```

---

## Hito 3: Agentes 3D

### `src/ursina_models.py`

**Función**: Define la clase `Agent3D` que representa un agente de la simulación en el mundo 3D como un modelo construido con primitivas, sin assets externos.

#### Estructura del agente

```
Agent3D (Entity)
├── body (sphere o cube) — forma según gremio
│   ├── HERBIVORE → esfera verde (#4ade80)
│   ├── CARNIVORE → cubo rojo (#dc2626)
│   ├── OMNIVORE → esfera naranja (#f97316)
│   ├── BIRD → cono azul (#3b82f6)
│   └── FISH → esfera gris (#64748b)
├── head (cone) — orientado hacia adelante
├── shadow (circle) — sombra circular en el suelo
└── label (Text) — nombre en billboard (siempre visible)
```

#### Movimiento

```python
def move_to(self, x, y, terrain_height_fn):
    """Set target position for smooth interpolation."""
    h = terrain_height_fn(x, y)  # altura del terreno en esa celda
    z = -y                       # invertir eje Y del grid
    self.target_pos = Vec3(x, h, z)

def update(self):
    """Interpolar suavemente hacia target_pos cada frame."""
    diff = self.target_pos - self.position
    if dist > 0.05:
        self.position += diff * min(1, time.dt * move_speed)
    if dist > 0.3:
        self.look_at_2d(self.target_pos)
    # Bobbing: leve oscilación vertical al moverse
    self.y += sin(time.time() * 6) * 0.02 if dist > 0.1 else 0
```

#### Función de altura del terreno

```python
def terrain_height_fn(x, y):
    """Devuelve la elevación * escala en la celda (x,y) del grid."""
    ix, iy = int(round(x)), int(round(-y))
    h = elev_grid[iy, ix]
    return h * vertical_scale if not isnan(h) else 0
```

---

## Hito 4: Puente Simulación

### `src/ursina_sim_bridge.py`

**Función**: Conecta la simulación ecológica con el visor 3D mediante exportación de snapshots JSON.

#### Opción A: Snapshots (recomendada)

**Exportación** — llamar desde el bucle de simulación:

```python
from ursina_sim_bridge import export_snapshot

# En simulation.py, dentro del bucle principal:
if day % export_interval == 0:
    export_snapshot(
        agents=all_agents,
        day=day,
        output_dir="output/snapshots",
        prefix="agents_day",
    )
```

Cada snapshot contiene:

```json
[
    {
        "id": 1,
        "species_key": "Rupicapra_pyrenaica",
        "nick": "Isard",
        "guild": "HERBIVORE",
        "x": 152.3,
        "y": 287.1,
        "energy": 4500.0,
        "alive": true,
        "age": 120
    }
]
```

**Carga** — en el visor:

```python
viewer.load_snapshot_sequence("output/snapshots")
# Reproduce automáticamente día a día
```

**Datos de prueba** — generador sintético:

```python
generate_test_snapshots(
    output_dir="output/snapshots_test",
    num_days=60,       # 60 snapshots
    num_agents=30,     # 30 agentes con movimiento aleatorio
)
```

#### Opción B: Socket en tiempo real (futuro)

Arquitectura propuesta:

```
Simulación (servidor) ──socket TCP→ Visor 3D (cliente)
    Puerto 5555                 localhost
    JSON por línea              buffer + parse
```

La simulación inicia un hilo servidor que transmite el estado de los agentes en tiempo real. El visor recibe y actualiza posiciones cada frame.

---

## Hito 5: Lanzador Unificado

### `src/ursina_launcher.py`

**Función**: Punto de entrada único para todo el pipeline.

#### Modos de uso

```bash
# Pipeline completa: exportar malla + snapshots de prueba + visor
python src/ursina_launcher.py

# Solo exportar malla
python src/ursina_launcher.py --export-mesh --step 3

# Visor con snapshots de prueba
python src/ursina_launcher.py --test-snapshots --view

# Visor con datos reales de simulación
python src/ursina_launcher.py --view --snapshots output/snapshots

# Especificar exageración vertical
python src/ursina_launcher.py --view --vertical-scale 0.05
```

#### Pipeline interno

```
ursina_launcher.py
├── [1/3] export_terrain_mesh.py (subprocess)
├── [2/3] generate_test_snapshots() (in-process)
└── [3/3] ursina_viewer.py (subprocess, bloqueante)
```

---

## Glosario Técnico

### Submuestreo (step)

Factor que reduce la resolución del grid para la malla 3D:

| step | Grid | Vértices | Triángulos | Uso |
|------|------|----------|------------|-----|
| 1 | 375×501 | 188K | 375K | Resolución máxima |
| **2** | **188×251** | **45K** | **89K** | **Default (balance)** |
| 3 | 125×167 | 20K | 39K | Rendimiento |
| 4 | 94×125 | 11K | 22K | Máximo rendimiento |

### Escala vertical

El desnivel real es de 977–2722 m (rango 1745 m). Con escala 0.03, el relieve 3D tiene ~52 unidades de altura. La malla en planta mide 188×251 unidades (con step=2).

### Sistema de coordenadas

- Grid 2D: (x, y) → celdas del TSV
- Mundo 3D: (x, elev×scale, -y) → Ursina/Panda3D
- El eje Y del grid se invierte (z = -y) porque el grid tiene origen arriba-izquierda y Ursina usa coordenadas cartesianas estándar

### Formato OBJ

```
v 5.000 40.830 -0.000     # vértice (x, altura, -y)
vt 0.0266 0.0000           # coordenada de textura (u, v)
vn -0.770 -0.632 -0.083    # normal (nx, ny, nz)
f 1/1/1 14/14/14 2/2/2    # cara (v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3)
```

---

## Rendimiento Esperado

| Escenario | step | Agentes | FPS | Memoria |
|-----------|------|---------|-----|---------|
| Solo terreno | 2 | 0 | 60 | ~200 MB |
| Terreno + 100 agentes | 2 | 100 | 55-60 | ~250 MB |
| Terreno + 500 agentes | 2 | 500 | 40-50 | ~400 MB |
| Terreno + 1000 agentes | 2 | 1000 | 25-35 | ~600 MB |
| Solo terreno | 3 | 0 | 60 | ~100 MB |

### Optimizaciones si hay bajos FPS

1. Aumentar step (3 o 4) → menos triángulos
2. Ocultar labels de agentes lejanos (LOD por distancia)
3. Reducir resolución de sombras (1024→512)
4. Desactivar grid de referencia (`--no-grid`)

---

## Instalación y Dependencias

```bash
# Instalar Ursina (motor 3D)
pip install ursina

# Dependencias del mesh exporter
pip install numpy pandas pillow matplotlib

# En Linux, puede necesitar:
sudo apt install freeglut3-dev libgl1-mesa-dev

# Verificar instalación:
python3 -c "from ursina import *; print('Ursina OK')"
```

El visor requiere un servidor gráfico (X11/Wayland). En SSH usar `ssh -X` o `ssh -Y`. No funciona en terminales sin display.

---

## Integración Completa con la Simulación

Para usar snapshots reales desde `simulation.py`:

```python
# En simulation.py
from ursina_sim_bridge import export_snapshot

# Dentro del bucle de simulación:
for day in range(total_days):
    # ... lógica existente ...
    if day % 10 == 0:  # snapshot cada 10 días
        export_snapshot(self.agents, day, "output/snapshots")
```

Luego:

```bash
python src/ursina_launcher.py --view --snapshots output/snapshots
```

---

## Roadmap Futuro

- [ ] Socket en tiempo real (Opción B)
- [ ] Modelos 3D descargados (Poly Pizza, Sketchfab)
- [ ] Cámara que sigue a un agente específico (tecla F)
- [ ] Click en agente → mostrar panel de información
- [ ] Terreno coloreado por hábitat o pendiente
- [ ] Ciclo día/noche y estaciones
- [ ] Partículas (polvo al caminar, nieve)
