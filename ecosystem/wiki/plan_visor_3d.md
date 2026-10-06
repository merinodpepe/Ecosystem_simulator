# Plan de Implementación: Visor 3D Interactivo

## Objetivo

Construir un visor tridimensional del terreno de Vall de Cardós (Parc Natural de l'Alt Pirineu) donde el usuario pueda moverse libremente estilo videojuego (WASD + ratón), y donde los agentes de la simulación ecológica sean visibles en 3D moviéndose por el terreno.

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    Ursina Engine (Panda3D)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Terreno 3D   │  │ Agentes 3D   │  │ UI / Controles    │  │
│  │ (malla OBJ)  │  │ (dummy/low)  │  │ (info, FPS, ley.) │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────────┘  │
│         │                 │                                  │
└─────────┼─────────────────┼──────────────────────────────────┘
          │                 │
          ▼                 ▼
   output/terrain_mesh/   output/snapshots/  (o socket en vivo)
          ▲                 ▲
          │                 │
   src/export_terrain_    src/sim/simulation.py
   mesh.py                (exporta snapshots JSON)
```

---

## Fase 1: Exportar Malla 3D del Terreno

### Archivo

**`src/export_terrain_mesh.py`** (~200 líneas)

### Entrada

- `ecosystem/data/terrain_cells.tsv` (180.037 filas, columnas: x, y, utm_x, utm_y, elevation_m, slope_deg, aspect_deg, tri, piso)

### Salida

```
output/terrain_mesh/
├── terrain.obj           # Malla 3D (formato Wavefront)
├── terrain.mtl           # Materiales (colores, textura)
├── terrain_texture.png   # Textura horneada (opcional)
└── terrain_metadata.json # Stats de la malla generada
```

### Algoritmo de Generación de Malla

#### Submuestreo

Para rendimiento en Ursina, la malla se submuestrea con un factor `step`.

| step | Vértices | Triángulos | Calidad visual | Rendimiento |
|------|----------|------------|----------------|-------------|
| 1 | ~188K | ~375K | Original | Puede ir justo |
| 2 | ~47K | ~94K | Buena | Bueno |
| 3 | ~21K | ~42K | Aceptable | Muy bueno |
| 4 | ~12K | ~24K | Baja | Excelente |

**Valor por defecto: step=2** (balance calidad/rendimiento).

#### Cálculo de vértices

```
Para cada celda (x, y) en el grid:
  Si elevation_m no es NaN:
    Crear vértice V = (x, elevacion * escala_vertical, -y)

Donde:
  - escala_vertical = 0.03 (ajustable)
  - El signo negativo en Z invierte el eje Y del grid
    para que Ursina lo muestre con la orientación correcta
  - Las celdas NaN (nodata) no generan vértices
```

#### Cálculo de triángulos

```
Para cada quad (i,j) con 4 vértices válidos:
  Triángulo 1: (i, j) → (i+step, j) → (i, j+step)
  Triángulo 2: (i+step, j) → (i+step, j+step) → (i, j+step)

Donde i, j recorren el grid con paso = step
```

#### Cálculo de coordenadas de textura (UV)

```
u = x / W   (0 a 1)
v = y / H   (0 a 1, invertido)
```

#### Cálculo de normales

```
Para cada vértice, la normal es el promedio de las normales
de todos los triángulos que lo comparten.

Normal de un triángulo = producto vectorial de (v1-v0) × (v2-v0)
```

#### Coloración de vértices por elevación

```
Mapear elevation_m → color usando matplotlib colormap "terrain":
  - 977 m  (mín) → verde oscuro (valle)
  - 1800 m (medio) → marrón/verde claro (ladera)
  - 2722 m (máx) → blanco/gris (cumbres)

Exportar como:
  a) Vértices con color por-vertex en OBJ
  b) Textura PNG horneada de 1024×1024 px
```

### Formato OBJ

```obj
# Exportado por ecosystem_simulator - terrain mesh
# step=2, vertices=47012, triangles=92344
# Escala vertical: 0.030

mtllib terrain.mtl

# Vértices (x, elev*escala, -y)
v 0.0 29.31 -0.0
v 2.0 29.28 -0.0
...

# Coordenadas de textura
vt 0.0000 0.0000
vt 0.0053 0.0000
...

# Normales
vn 0.12 0.98 -0.15
...

# Caras
usemtl terrain_material
f 1/1/1 2/2/2 3/3/3
f 2/2/2 4/4/4 3/3/3
...
```

### Archivo MTL

```mtl
newmtl terrain_material
map_Kd terrain_texture.png
Kd 0.8 0.8 0.8
Ka 0.2 0.2 0.2
Ks 0.1 0.1 0.1
Ns 10.0
illum 2
```

### Generación de textura horneada

Alternativa a color por-vertex: generar una textura PNG de 1024×1024 donde cada píxel corresponde al color de elevación de esa celda del grid. Esto permite texturizar la malla con mayor detalle.

---

## Fase 2: Visor 3D Interactivo

### Archivo

**`src/ursina_viewer.py`** (~300 líneas)

### Dependencias

```
ursina>=6.0.0
numpy>=1.24
Pillow>=9.0
```

### Clase Principal: `TerrainViewer`

```python
class TerrainViewer:
    """Controlador principal del visor 3D."""

    def __init__(self, mesh_dir="output/terrain_mesh"):
        # Inicializar escena
        # Cargar malla del terreno
        # Configurar cámara, luces, UI
        # Preparar contenedores de agentes

    def setup_terrain(self):
        """Cargar terrain.obj como Entity estática."""

    def setup_camera(self):
        """Configurar EditorCamera con parámetros ajustados."""

    def setup_lights(self):
        """Añadir sol direccional + ambiental + fog."""

    def setup_ui(self):
        """Overlay con FPS, posición, leyenda de colores."""

    def setup_agents(self, agent_data_list):
        """Crear entidades 3D para cada agente."""

    def update(self):
        """Loop por frame: animar agentes, actualizar UI."""

    def run(self):
        """Iniciar app.run() de Ursina."""
```

### Controles de Cámara

| Entrada | Acción |
|---------|--------|
| WASD | Movimiento horizontal (adelante/atrás/izquierda/derecha) |
| Shift + WASD | Movimiento rápido (×3) |
| Q / E | Subir / bajar cámara (eje Y) |
| Ratón (botón derecho arrastrar) | Rotar vista |
| Scroll | Zoom |
| Tecla R | Resetear cámara a posición inicial |
| Tecla F | Seguir agente seleccionado (toggle) |
| Tecla 1-5 | Cambiar velocidad de reproducción (0.5×, 1×, 2×, 5×, 10×) |
| Tecla H | Ocultar/mostrar UI |
| Tecla ESC | Salir |

### Configuración de Escena

```python
app = Ursina()
window.title = "Ecosystem Simulator — Alt Pirineu 3D"
window.size = (1280, 720)
window.color = color.rgb(135, 206, 235)  # azul cielo

# Terreno
terrain = Entity(
    model="output/terrain_mesh/terrain.obj",
    texture="output/terrain_mesh/terrain_texture.png",
    scale=(1, 1, 1),
)

# Cámara
camera = EditorCamera(
    rotation_smoothing=6,
    zoom_speed=2,
)
camera.position = Vec3(W//2, altura_media*escala*1.5, -H*0.6)
camera.rotation = Vec3(30, 0, 0)

# Luces
scene.fog_color = color.rgb(200, 220, 240)
scene.fog_density = 0.003
DirectionalLight(shadow_map_resolution=(2048, 2048))

# Grid de referencia (opcional)
grid_entity = Entity(model=Grid(N, N), scale=1, position=(W/2, 0, -H/2))

app.run()
```

### UI Overlay

```python
# Ejemplo de overlay usando Ursina Text
fps_counter = Text(text="FPS: 60", position=(-0.85, 0.47), scale=1.5,
                  color=color.white, parent=camera.ui)
pos_display = Text(text="Pos: (0, 0, 0)", position=(-0.85, 0.43),
                   scale=1.2, color=color.white, parent=camera.ui)
speed_display = Text(text="Speed: 1.0×", position=(0.7, 0.47),
                     scale=1.2, color=color.yellow, parent=camera.ui)
legend = Text(text="● Herbívoro  ● Carnívoro  ● Omnívoro",
              position=(-0.85, -0.45), scale=1, color=color.white,
              parent=camera.ui)
help_text = Text(text="WASD: mover  Q/E: altura  R: reset  ESC: salir",
                 position=(-0.85, -0.40), scale=0.8, color=color.gray,
                 parent=camera.ui)
```

---

## Fase 3: Agentes 3D

### Archivo

**`src/ursina_models.py`** (~150 líneas)

### Clase: `Agent3D` (dummy, sin assets externos)

```python
class Agent3D(Entity):
    """Representación 3D de un agente de la simulación."""

    COLORS = {
        "HERBIVORE": color.hex("#4ade80"),  # verde
        "CARNIVORE": color.hex("#dc2626"),  # rojo
        "OMNIVORE":  color.hex("#f97316"),  # naranja
        "BIRD":      color.hex("#3b82f6"),  # azul
        "FISH":      color.hex("#64748b"),  # gris
    }

    def __init__(self, agent_id, species_key, nick, guild,
                 x, y, terrain_height_fn, **kwargs):
        super().__init__(**kwargs)

        self.agent_id = agent_id
        self.species_key = species_key
        self.guild = guild
        self.color_3d = self.COLORS.get(guild, color.white)

        # Construir modelo compuesto de primitivas
        self.body = Entity(
            parent=self,
            model="sphere",
            scale=(0.6, 0.4, 0.4),
            color=self.color_3d,
        )
        self.head = Entity(
            parent=self,
            model="cone",
            scale=(0.25, 0.2, 0.2),
            position=(0.4, 0.1, 0),
            rotation=(0, 0, -90),
            color=self._darken(self.color_3d, 0.8),
        )
        self.shadow = Entity(
            parent=self,
            model="circle",
            scale=(0.7, 1, 0.7),
            color=color.rgba(0, 0, 0, 80),
            y=-0.15,
        )
        self.label = Text(
            text=nick,
            parent=self,
            scale=1.5,
            billboard=True,
            position=(0, 1.2, 0),
            color=color.white,
            outline=color.black,
        )

        # Estado de movimiento
        self.current_pos = Vec3(0, 0, 0)
        self.target_pos = Vec3(0, 0, 0)
        self.move_speed = 2.0
        self.is_alive = True

        # Colocar en posición inicial
        self.teleport_to(x, y, terrain_height_fn)

    def teleport_to(self, x, y, height_fn):
        """Teletransportar a (x, y) del grid con altura del terreno."""
        z = -y  # invertir eje Y del grid
        h = height_fn(x, y)  # altura del terreno en ese punto
        self.position = Vec3(x, h, z)
        self.current_pos = self.position
        self.target_pos = self.position

    def move_towards(self, x, y, height_fn, dt):
        """Interpolar movimiento suave hacia (x, y)."""
        z = -y
        h = height_fn(x, y)
        self.target_pos = Vec3(x, h, z)

        # Interpolación lineal suave
        self.position = lerp(self.current_pos, self.target_pos,
                             min(1, dt * self.move_speed))
        self.current_pos = self.position

        # Orientar en dirección del movimiento
        direction = self.target_pos - self.current_pos
        if direction.length() > 0.1:
            self.look_at_2d(self.target_pos)

    def _darken(self, col, factor=0.7):
        return color.rgb(col.r * factor, col.g * factor, col.b * factor)
```

### Variante por gremio

Cada gremio puede tener una forma diferente para distinguirse visualmente sin necesidad de modelos externos:

| Gremio | Forma | Color |
|--------|-------|-------|
| HERBIVORE | Esfera achatada | Verde (#4ade80) |
| CARNIVORE | Cápsula alargada | Rojo (#dc2626) |
| OMNIVORE | Esfera + cono | Naranja (#f97316) |
| BIRD | Disco (dos triángulos) | Azul (#3b82f6) |
| MICROMAMMAL | Esfera pequeña | Marrón (#a16207) |

### Función de altura del terreno

```python
def terrain_height_fn(x, y):
    """Devuelve la altura del terreno en (x, y) con interpolación."""

    def __init__(self, grid_data):
        # grid_data: array 2D (H, W) con elevation_m
        self.elev = grid_data
        self.scale = 0.03  # misma escala que la malla

    def __call__(self, x, y):
        ix, iy = int(x), int(-y)  # -y porque z = -y en la malla
        if 0 <= ix < self.elev.shape[1] and 0 <= iy < self.elev.shape[0]:
            return self.elev[iy, ix] * self.scale
        return 0
```

---

## Fase 4: Puente Simulación → Visor

### Archivo

**`src/ursina_sim_bridge.py`** (~100 líneas)

### Opción A: Snapshots (modo offline)

#### Exportación desde la simulación

En `src/sim/simulation.py`, añadir exportación periódica:

```python
def _step(self, day):
    # ... lógica existente ...
    if day % self.export_interval == 0:
        self.export_agents_3d(self.output_dir / "snapshots")

def export_agents_3d(self, snap_dir):
    snap_dir.mkdir(parents=True, exist_ok=True)
    agents_3d = []
    for a in self.agents:
        if a.is_alive:
            agents_3d.append({
                "id": a.agent_id,
                "species_key": a.species_key,
                "nick": a.species_nickname,
                "guild": a.guild,
                "x": a.state.x,
                "y": a.state.y,
                "energy": a.state.energy_kcal,
                "alive": a.state.alive,
                "age": a.state.age_days,
            })
    path = snap_dir / f"agents_day_{day:05d}.json"
    with open(path, "w") as f:
        json.dump(agents_3d, f, indent=2)
```

#### Carga en el visor

```python
def load_snapshot(self, path):
    with open(path) as f:
        return json.load(f)

def play_simulation(self):
    for day in range(0, self.max_day + 1, self.snapshot_interval):
        agents_data = load_snapshot(
            self.snap_dir / f"agents_day_{day:05d}.json"
        )
        for ad in agents_data:
            agent_3d = self.agent_entities.get(ad["id"])
            if agent_3d:
                agent_3d.move_towards(ad["x"], ad["y"],
                                      self.height_fn, self.dt)
        self.day = day
        yield  # un frame por step
```

### Opción B: Socket en tiempo real (modo live)

#### Servidor (en `simulation.py`, hilo separado)

```python
import socket, json, threading

class SimServer:
    def __init__(self, port=5555):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", port))
        self.server.listen(1)
        self.clients = []

    def broadcast(self, data):
        msg = json.dumps(data).encode() + b"\n"
        for c in self.clients[:]:
            try:
                c.send(msg)
            except:
                self.clients.remove(c)

    def accept_loop(self):
        while True:
            conn, addr = self.server.accept()
            self.clients.append(conn)
```

#### Cliente (en `ursina_viewer.py`)

```python
import socket, json, threading

class SimClient:
    def __init__(self, host="localhost", port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.buffer = b""
        self.latest_snapshot = []
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while True:
            data = self.sock.recv(65536)
            self.buffer += data
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                self.latest_snapshot = json.loads(line)
```

### Recomendación

**Empezar con Opción A (snapshots)** por simplicidad. Es más fácil de depurar, no requiere sincronización, y los snapshots sirven como registro reproducible de la simulación.

La Opción B (socket) se añade después cuando el visor básico funcione.

---

## Hoja de Ruta (Roadmap)

### Hito 1: Malla 3D básica

- [ ] Crear `src/export_terrain_mesh.py`
- [ ] Leer TSV y construir grid 2D de elevación
- [ ] Implementar submuestreo (step configurable, default=2)
- [ ] Generar vértices con escala vertical ajustable
- [ ] Generar triángulos (2 por quad)
- [ ] Calcular normales por vértice
- [ ] Colorear por elevación (cmap "terrain")
- [ ] Exportar OBJ + MTL + textura PNG
- [ ] Verificar malla en Blender o similar
- [ ] Probar con step=1,2,3,4 y medir tiempos

### Hito 2: Visor Ursina básico

- [ ] Instalar Ursina (`pip install ursina`)
- [ ] Verificar dependencias (OpenGL, freeglut3 en Linux)
- [ ] Crear `src/ursina_viewer.py`
- [ ] Cargar terrain.obj como Entity
- [ ] Configurar EditorCamera con controles WASD
- [ ] Añadir luz direccional + ambiental
- [ ] Añadir niebla atmosférica
- [ ] Añadir cuadrícula de referencia (opcional)
- [ ] Overlay UI: FPS, posición, ayuda

### Hito 3: Agentes dummy

- [ ] Crear `src/ursina_models.py`
- [ ] Implementar `Agent3D` con primitivas (esfera + cono)
- [ ] Colorear por gremio
- [ ] Añadir sombra circular
- [ ] Añadir label billboard con nombre
- [ ] Implementar `terrain_height_fn` para colocar agentes sobre el terreno
- [ ] Probar con 10, 100, 1000 agentes y medir FPS

### Hito 4: Animación de agentes

- [ ] Implementar interpolación de movimiento (lerp)
- [ ] Orientar agente hacia la dirección del movimiento
- [ ] Sistema de reproducción (play/pause/velocidad)
- [ ] Cargar snapshots desde archivo
- [ ] Avanzar día a día por los snapshots
- [ ] Controles de velocidad (0.5×, 1×, 2×, 5×, 10×)

### Hito 5: Mejoras visuales (post-MVP)

- [ ] Modelos 3D descargados (Poly Pizza, Sketchfab)
- [ ] Terreno coloreado por hábitat en lugar de elevación
- [ ] Efectos: sombras dinámicas, partículas de polvo
- [ ] Cámara que sigue a un agente específico (tecla F)
- [ ] Click en agente → mostrar info (especie, energía, edad)
- [ ] Socket en tiempo real (Opción B)
- [ ] Día/noche, estaciones, nieve

---

## Modelos 3D Descargables (para Hito 5)

Fuentes recomendadas para modelos low-poly gratuitos:

| Fuente | URL | Licencia |
|--------|-----|----------|
| Poly Pizza | https://poly.pizza/ | CC0 (mayoría) |
| Sketchfab | https://sketchfab.com/ | CC-BY / CC0 |
| Quaternius | https://quaternius.com/ | CC0 (todos) |
| OpenGameArt | https://opengameart.org/ | Varias |

Modelos específicos para este proyecto:

| Especie | Búsqueda sugerida |
|---------|-------------------|
| Oso pardo | "bear low poly" |
| Ciervo | "deer low poly" |
| Jabalí | "wild boar low poly" |
| Águila/Quebrantahuesos | "eagle low poly" / "bird low poly" |
| Lobo/Zorro | "fox low poly" |
| Marmota | "marmot low poly" |
| Perdiz nival | "ptarmigan low poly" |
| Árbol (pino negro) | "pine tree low poly" |
| Árbol (haya) | "tree low poly" |
| Roca | "rock low poly" |

Formato preferido: **glTF** (.glb) — Ursina lo carga con `Entity(model="modelo.glb")`.

Los modelos se almacenan en `output/terrain_mesh/models/`.

---

## Configuración Exportable

```yaml
# config/visor_3d.yaml (o argumentos CLI)
terrain:
  tsv_path: ecosystem/data/terrain_cells.tsv
  output_dir: output/terrain_mesh
  step: 2                    # submuestreo
  vertical_scale: 0.03       # exageración vertical
  color_by: elevation        # elevation | slope | piso | habitat
  colormap: terrain          # matplotlib colormap name

viewer:
  window_width: 1280
  window_height: 720
  fullscreen: false
  fog_density: 0.003
  camera_height_factor: 1.5  # altura relativa al terreno

agents:
  mode: snapshot             # snapshot | socket | none
  snapshots_dir: output/snapshots
  socket_port: 5555
  default_speed: 1.0
  show_labels: true
  show_shadows: true
  max_agents: 500
```

---

## Métricas de Rendimiento Esperadas

| Escenario | step | Agentes | FPS esperado | Memoria |
|-----------|------|---------|-------------|---------|
| Solo terreno | 2 | 0 | 60 | ~200 MB |
| Terreno + 100 agentes | 2 | 100 | 55-60 | ~250 MB |
| Terreno + 500 agentes | 2 | 500 | 40-50 | ~400 MB |
| Terreno + 1000 agentes | 2 | 1.000 | 25-35 | ~600 MB |
| Solo terreno | 3 | 0 | 60 | ~100 MB |
| Terreno + 500 agentes | 3 | 500 | 55-60 | ~300 MB |

Si el rendimiento es insuficiente:
1. Reducir step (3 o 4)
2. Ocultar labels de agentes lejanos (LOD)
3. Usar instancing para agentes del mismo gremio
4. Reducir resolución de sombras

---

## Estructura Final de Archivos

```
src/
├── export_terrain_mesh.py    # Fase 1: Generar malla 3D desde TSV
├── ursina_viewer.py          # Fase 2: Visor 3D interactivo
├── ursina_models.py          # Fase 3: Clases de agentes 3D
├── ursina_sim_bridge.py      # Fase 4: Puente simulación → visor
├── ursina_launcher.py        # Punto de entrada: CLI con argparse

output/
├── terrain_mesh/
│   ├── terrain.obj
│   ├── terrain.mtl
│   ├── terrain_texture.png
│   ├── terrain_metadata.json
│   └── models/               # Modelos 3D descargados
└── snapshots/                 # Snapshots de la simulación (Opción A)
    ├── agents_day_00000.json
    ├── agents_day_00010.json
    └── ...

ecosystem/
└── wiki/
    └── plan_visor_3d.md       # Este documento
```

---

## Notas Técnicas

### Instalación de Ursina en Linux

```bash
pip install ursina

# Si hay errores de OpenGL:
sudo apt install freeglut3-dev libgl1-mesa-dev libgles2-mesa-dev

# Para sombras:
sudo apt install pkg-config
```

### Ursina no tiene un `app.run()` bloqueante en modo headless

El visor requiere un servidor gráfico (X11/Wayland) o se puede usar `virtualgl` en entornos sin pantalla. No se puede ejecutar en una terminal SSH sin X forwarding.

### La malla completa tiene ~188K celdas válidas

Con step=2, se reduce a ~47K vértices y ~94K triángulos. Esto es perfectamente manejable para Ursina/Panda3D en cualquier GPU moderna integrada.

### Escala vertical

El Valle de Cardós tiene 977-2722 m de desnivel (~1745 m de rango). Con escala_vertical=0.03, el relieve en 3D ocupará ~52 unidades de altura. La malla en planta mide 375×501 celdas. La exageración 0.03×1745=52.35 hace que el relieve sea visible sin distorsionar demasiado la geografía.

---

## Glosario

| Término | Definición |
|---------|------------|
| **Step** | Factor de submuestreo. step=2 significa tomar 1 de cada 2 celdas en cada eje |
| **Vértice** | Punto 3D (x, y, z) que forma parte de la malla |
| **Triángulo** | Unidad básica de renderizado 3D (3 vértices conectados) |
| **OBJ** | Formato de malla 3D estándar (Wavefront) |
| **MTL** | Archivo de materiales asociado al OBJ |
| **glTF** | Formato moderno de modelos 3D (.glb binario, .gltf texto) |
| **Ursina** | Motor de juegos 3D en Python (basado en Panda3D) |
| **EditorCamera** | Control de cámara de Ursina con WASD + ratón |
| **Billboard** | Objeto 2D que siempre mira hacia la cámara (para etiquetas) |
| **Lerp** | Interpolación lineal entre dos puntos |
| **Snapshot** | Captura del estado de la simulación en un instante dado |
| **LOD** | Level of Detail: reducir calidad de objetos lejanos |
| **Instancing** | Renderizar múltiples copias de un mismo modelo en un solo draw call |
