# Pla d'Implementació: Sistema de Ticks (30s) amb FSM i GIF

> **Objectiu**: Convertir el simulador de passos diaris discrets a un sistema de **ticks cada 30 segons** on cada agent té una **màquina d'estats** (FSM) que processa una acció per tick. A més, generar un **GIF animat** sobre el mapa de terreny amb les posicions dels agents.

---

## ⚠️ Correccions biològiques abans de començar

Basat en l'anàlisi de la simulació 50×50 on moltes espècies no variaven (Cervus 3→3, Martes 1→1, Aquila 1→1, etc.):

### 1. Energia inicial → `mass_kg × 2000` (abans ×10000)

| Espècie | Abans (kcal) | Ara (kcal) | Dies d'autonomia | Realisme |
|---------|-------------|------------|-------------------|----------|
| Isard (35kg) | 350.000 | 70.000 | ~28 dies | ✅ Real (15% greix ≈ 31.500) |
| Mostela (0.08kg) | 800 | 160 | ~5 dies | ✅ |
| Cérvol (200kg) | 2.000.000 | 400.000 | ~80 dies | ✅ Acceptable (greix estacional) |
| Trencalòs (5.5kg) | 55.000 | 11.000 | ~15 dies | ✅ |

Raó biològica: els animals emmagatzemen ~10-20% del seu pes en greix (9000 kcal/kg).  
`mass_kg × 2000` ≈ 22% de greix — valor superior mitjà, raonable.

### 2. Reproducció per simulacions petites → augmentar agents mínims

Per `scale_to_area()`, quan `count × area / reference_ha < 1`, s'arrodoneix a 1.  
Això deixa espècies amb 1 sol individu que mai es reprodueix.

**Fix**: Garantir mínim de 3-5 individus per espècie en mode demo.  
Per simulació completa (375×502), `scale_to_area` funciona correctament perquè l'àrea és ~11.765 ha.

```rust
// Nova versió per demo / àrees petites
fn scale_to_area(count: u32, area_ha: f64, reference_ha: f64) -> u32 {
    let scaled = (count as f64 * area_ha / reference_ha).max(1.0) as u32;
    if area_ha < 1000.0 {
        scaled.max(3)  // mínim 3 per àrees petites
    } else {
        scaled
    }
}
```

### 3. Predació al tick system → detecció per radi REAL

Al nou sistema FSM, els carnívors:
- Detecten preses dins d'un radi (en metres, no cel·les) cada N ticks
- Transicionen a `HUNT_STALK` (sigil) o `HUNT_CHASE` (persecució)
- La mort es produeix en arribar a la cel·la de la presa

Això substitueix `predation_step()` que només matava a la mateixa cel·la.

### 4. Inanició → `critical_energy_ratio = 0.05`

Un agent mor quan `energy_kcal < mass_kg × 2000 × 0.05` durant ≥3 dies consecutius  
(equival a ~1-2 dies sense menjar).

---

## Resum de l'arquitectura final

```
Cada dia (2880 ticks de 30s):
├── Matí     (ticks 0-720,   06:00-12:00)
├── Tarda    (ticks 720-1440,12:00-18:00)
├── Vespre   (ticks 1440-2160,18:00-00:00)
└── Nit      (ticks 2160-2880,00:00-06:00)

Per tick:
  1. Cada agent executa 1 pas del seu FSM (O(1) en ~99% dels casos)
  2. Si cal re-planificar (cada 60-300 ticks), A* només llavors
  3. Creixement plantes/inverts escalat a 1/2880
  4. Decadència carronya escalada
  5. Mort per inanició si energia ≤ 0

Cada dia (1 cop cada 2880 ticks):
  1. Avança estació/temperatura/neu
  2. Reproducció
  3. Log estats globals
```

---

## FASE 0: Preparació (1 fitxer, sense trenjar res)

### 0.1 — `Cargo.toml` + dependències

**Arxiu**: `Cargo.toml`

**Canvis**:
```toml
[dependencies]
image = "0.25"        # <-- NOU: per renderitzar frames de GIF
```

Raó: `image` + `imageproc` permetran dibuixar el terreny i agents a PNG des de Rust (opcional), però principalment usarem Python per al GIF. No cal afegir-ho ara.

✅ **Fet**: Ja tenim totes les dependències necessàries (clap, rand, serde, csv, rayon). La generació del GIF es farà des de Python, no calen canvis a Cargo.toml.

---

## FASE 1: Refactor energètic — funcions per tick (1 fitxer)

> **Objectiu**: En lloc de `daily_dee()` que calcula kcal/dia, crear `tick_energy()` que calcula kcal/tick segons l'estat actual de l'agent.

### 1.1 — `energy.rs`

**Arxiu**: `src/sim/energy.rs`

**Constants a afegir**:
```rust
pub const TICKS_PER_DAY: f64 = 2880.0;
pub const SECONDS_PER_TICK: f64 = 30.0;
```

**Noves funcions**:

```rust
/// Gasta energia per 1 tick en un estat concret.
/// `met` = Multiple of BMR per l'activitat (ex: 1.0 resting, 3.0 foraging, 2.5 walking)
pub fn tick_energy(mass_kg: f64, met: f64, is_cold: bool, is_hibernating: bool) -> f64 {
    if is_hibernating {
        let bmr_day = bmr_kcal_day(mass_kg);
        return bmr_day * 0.05 / TICKS_PER_DAY;
    }
    let bmr_tick = bmr_kcal_day(mass_kg) / TICKS_PER_DAY;
    let mut cost = bmr_tick * met;
    if is_cold {
        cost += bmr_tick * get_activity_met("TERMO_SHIVERING") * 0.5;
    }
    cost
}

/// Retorna el MET associat a un estat del FSM
pub fn met_for_state(state: &str) -> f64 {
    match state {
        "REST" | "IDLE"     => 1.0,
        "FORAGE_EAT"        => get_activity_met("FORAGE_INTAKE"),  // 1.5
        "FORAGE_SEARCH"     => get_activity_met("FORAGE_SEARCH"),  // 3.0
        "TRAVEL"            => get_activity_met("LOCO_WALK_MOD"),  // 2.5
        "HUNT_STALK"        => get_activity_met("LOCO_WALK_SLOW"), // 2.0
        "HUNT_CHASE"        => get_activity_met("LOCO_GALLOP"),    // 7.0
        "FLEE"              => get_activity_met("LOCO_GALLOP"),    // 7.0
        "EAT_CARCASS"       => 1.2,
        "DRINK"             => 1.0,
        "VIGILANCE"         => get_activity_met("VIGILANCE"),      // 1.3
        _                   => 1.5,
    }
}

pub fn intake_per_tick(mass_kg: f64, max_daily_intake_ratio: f64) -> f64 {
    mass_kg * max_daily_intake_ratio / TICKS_PER_DAY
}
```

✅ **Tests de coherència**:
- Un isard (35kg) en REST: BMR = 70 × 35^0.75 ≈ 1008 kcal/dia → 0.35 kcal/tick
- Un isard en TRAVEL (MET 2.5): 0.35 × 2.5 = 0.875 kcal/tick
- En un dia sencer REST: 0.35 × 2880 = 1008 kcal ✅ (correcte)
- En un dia sencer TRAVEL: 0.875 × 2880 = 2520 kcal ≈ 2.5× BMR ✅

**Funció a ELIMINAR** (o marcar com a deprecated):
- `daily_dee()` — ja no cal, substituït per `tick_energy()` cridat 2880 cops/dia

**Funció a MODIFICAR**:
- `loco_cost_hours()` → mantenir-lo com a utilitat però ja no s'usarà al loop principal

---

## FASE 2: Agent amb FSM i coordenades contínues (1 fitxer)

> **Objectiu**: Cada agent té una màquina d'estats que determina què fa cada tick. Posició en `f64` (metres UTM) per moviment suau. El FSM es processa 1 pas per tick.

### 2.1 — `agents.rs`

**Arxiu**: `src/sim/agents.rs`

#### 2.1.1 — AgentState: coordenades contínues + FSM

```rust
#[derive(Clone)]
pub struct AgentState {
    // --- Posició contínua (metres UTM) ---
    pub pos_x: f64,         // Coordenada UTM x (metres)
    pub pos_y: f64,         // Coordenada UTM y (metres)
    pub cell_x: i32,        // Cel·la actual (derivat de pos_x/pos_y, cache)
    pub cell_y: i32,

    // --- FSM ---
    pub fsm_state: AgentFSMState,
    pub fsm_timer: i32,          // Ticks restants a l'estat actual
    pub fsm_target_x: f64,       // Destí en metres UTM
    pub fsm_target_y: f64,
    pub fsm_path: Vec<(i32, i32)>,  // Camí A* (cache de cel·les)
    pub fsm_path_index: usize,      // Posició al llarg del camí
    pub fsm_goal_cell: (i32, i32),  // Cel·la objectiu actual

    // --- Energia (per tick) ---
    pub energy_kcal: f64,
    pub mass_kg: f64,
    pub age_ticks: i64,          // Edat en ticks (abans age_days)
    pub alive: bool,

    // --- Biologia (escala diària) ---
    pub gender: Gender,
    pub is_pregnant: bool,
    pub is_lactating: bool,
    pub gestation_ticks: i64,        // Ticks d'embaràs (abans gestation_days)
    pub days_since_reproduction: i32,
    pub lactation_timer: i32,
    pub is_hibernating: bool,

    // --- Metriques tick ---
    pub calories_consumed_today: f64,
    pub calories_spent_today: f64,
    pub death_cause: Option<DeathCause>,
}
```

#### 2.1.2 — FSM States

```rust
#[derive(Clone, Copy, PartialEq)]
pub enum AgentFSMState {
    Idle,           // Descansant, gastant BMR
    Travel,         // Seguint camí A* cap a un destí
    ForageSearch,   // Buscant menjar a la cel·la actual
    ForageEat,      // Menjant (durada variable)
    HuntStalk,      // Aproximació sigilosa a presa
    HuntChase,      // Persecució d'alta velocitat
    EatCarcass,     // Menjant carronya/presa
    Drink,          // Al punt d'aigua
    Flee,           // Fugint d'un depredador
    Dead,           // Mort (per neteja)
}
```

#### 2.1.3 — Agent struct (camps nous)

```rust
#[derive(Clone)]
pub struct Agent {
    pub agent_id: u32,
    pub species_key: String,
    pub common_name: String,
    pub mass_kg: f64,
    pub adult_mass_kg: f64,
    pub kind: AgentKind,
    pub state: AgentState,

    // --- Metes per espècie ---
    pub speed_ms: f64,                   // Velocitat base en m/s (abans speed_kmh)
    pub home_range_m: f64,               // Radi de la llar en metres
    pub daily_distance_m: f64,           // Distància diària típica en metres

    // --- Reproducció ---
    pub gestation_ticks_total: i64,      // Ticks totals d'embaràs (abans gestation_days_total)
    pub litter_size_min: u32,
    pub litter_size_max: u32,
    pub reproductive_age_ticks: i64,     // Edat reproductiva en ticks
    pub lifespan_ticks: i64,             // Vida màxima en ticks

    // --- Personalitat ---
    pub boldness: f64,                   // 0.0 (poruc) - 1.0 (arriscat)
    
    // --- Cicle circadià ---
    pub is_diurnal: bool,                // Actiu de dia
    pub is_nocturnal: bool,              // Actiu de nit
    pub is_crepuscular: bool,            // Actiu alba/ocàs
}
```

#### 2.1.4 — Mètode `tick()` (substitueix `decide()` + `execute()`)

```rust
impl Agent {
    /// Processa 1 tick de 30s. Retorna accions que el Simulation loop ha d'aplicar
    /// (ex: consumir cel·la, carronya, pools).
    pub fn tick(&mut self, grid: &TerrainGrid, env: &Environment, is_cold: bool) -> TickOutcome {
        if !self.state.alive || self.state.is_hibernating {
            return TickOutcome::empty();
        }
        
        // 1. Executar l'estat actual
        let outcome = match self.state.fsm_state {
            AgentFSMState::Idle => self.tick_idle(grid),
            AgentFSMState::Travel => self.tick_travel(grid),
            AgentFSMState::ForageSearch => self.tick_forage_search(grid),
            AgentFSMState::ForageEat => self.tick_forage_eat(grid),
            AgentFSMState::HuntStalk => self.tick_hunt_stalk(grid),
            AgentFSMState::HuntChase => self.tick_hunt_chase(grid),
            AgentFSMState::EatCarcass => self.tick_eat_carcass(grid),
            AgentFSMState::Flee => self.tick_flee(grid),
            AgentFSMState::Drink => self.tick_drink(grid),
            AgentFSMState::Dead => TickOutcome::empty(),
        };
        
        // 2. Gastar energia segons l'estat
        let met = met_for_state(self.state.fsm_state.as_str());
        let cost = tick_energy(self.mass_kg, met, is_cold, false);
        self.state.energy_kcal -= cost;
        self.state.calories_spent_today += cost * TICKS_PER_DAY as f64; // escalat a kcal/dia per log
        
        // 3. Actualitzar timer FSM
        if self.state.fsm_timer > 0 {
            self.state.fsm_timer -= 1;
            if self.state.fsm_timer == 0 {
                self.transition_fsm(grid, env);
            }
        }
        
        // 4. Check death (inanició)
        if self.state.energy_kcal <= 0.0 {
            self.state.alive = false;
            self.state.fsm_state = AgentFSMState::Dead;
            self.state.death_cause = Some(DeathCause::Starvation);
        }
        
        outcome
    }
}
```

#### 2.1.5 — Implementació de cada estat

**`tick_travel()`** — Moure 1 pas pel camí:
```rust
fn tick_travel(&mut self, grid: &TerrainGrid) -> TickOutcome {
    if self.state.fsm_path.is_empty() || self.state.fsm_path_index >= self.state.fsm_path.len() {
        // Hem arribat al destí
        self.state.fsm_state = AgentFSMState::Idle;
        return TickOutcome::empty();
    }
    
    // Calcular quant de temps necessitem per arribar a la següent cel·la
    let (next_cell_x, next_cell_y) = self.state.fsm_path[self.state.fsm_path_index];
    let cell_center_x = next_cell_x as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;
    let cell_center_y = next_cell_y as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;
    
    // Distància a la següent cel·la
    let dx = cell_center_x - self.state.pos_x;
    let dy = cell_center_y - self.state.pos_y;
    let dist = (dx * dx + dy * dy).sqrt();
    
    // Velocitat en metres per tick (30s)
    let speed_m_per_tick = self.speed_ms * SECONDS_PER_TICK; // ex: 3 km/h = 0.833 m/s * 30 = 25m/tick
    
    if dist <= speed_m_per_tick {
        // Arribem a la cel·la aquest tick
        self.state.pos_x = cell_center_x;
        self.state.pos_y = cell_center_y;
        self.state.cell_x = next_cell_x;
        self.state.cell_y = next_cell_y;
        self.state.fsm_path_index += 1;
    } else {
        // Avancem parcialment
        let ratio = speed_m_per_tick / dist;
        self.state.pos_x += dx * ratio;
        self.state.pos_y += dy * ratio;
        // Actualitzar cell_x/cell_y si creuem frontera
        let new_cell_x = (self.state.pos_x / grid.resolution_m as f64) as i32;
        let new_cell_y = (self.state.pos_y / grid.resolution_m as f64) as i32;
        if new_cell_x != self.state.cell_x || new_cell_y != self.state.cell_y {
            self.state.cell_x = new_cell_x;
            self.state.cell_y = new_cell_y;
        }
    }
    
    TickOutcome::empty()
}
```

**`tick_forage_eat()`** — Consumir biomassa:
```rust
fn tick_forage_eat(&mut self, grid: &TerrainGrid) -> TickOutcome {
    let diet = get_diet(&self.species_key).unwrap_or_default();
    let intake = intake_per_tick(self.mass_kg, 0.10); // 10% del pes/dia
    
    let plant_kg = intake * diet.plant_proportion;
    let invert_kg = intake * diet.invert_proportion;
    
    TickOutcome {
        consume_plant_kg: plant_kg,
        consume_invert_kg: invert_kg,
        energy_gain_plant: plant_kg * get_energy_density_plant() * 0.6,
        energy_gain_invert: invert_kg * get_energy_density_invert() * 0.6,
        ..Default::default()
    }
}
```

**`tick_hunt_stalk()`** — Moure's cap a presa:
```rust
fn tick_hunt_stalk(&mut self, _grid: &TerrainGrid) -> TickOutcome {
    // Similar a travel però amb sigil (menys velocitat, menys detecció)
    // La presa té probabilitat de detectar-lo i passar a FLEE
    TickOutcome { ..Default::default() } // Placeholder
}
```

**`tick_flee()`** — Fugir:
```rust
fn tick_flee(&mut self, grid: &TerrainGrid) -> TickOutcome {
    // Allunyar-se del depredador a màxima velocitat
    // Ignorar cost de terreny
    TickOutcome { ..Default::default() } // Placeholder
}
```

#### 2.1.6 — Màquina de transició d'estats

```rust
/// Es crida quan fsm_timer == 0. Decideix el proper estat.
fn transition_fsm(&mut self, grid: &TerrainGrid, env: &Environment) {
    // Factors prioritaris (per ordre):
    // 1. Depredador proper? → Flee
    // 2. Energia baixa? → Forage/Hunt
    // 3. Cicle circadià? → Rest si és de nit i soc diürn
    // 4. Set? → Drink si prop d'aigua
    // 5. Atzar / exploració
    
    let hour = env.current_hour(); // 0-23
    let is_active_hours = self.is_active_at_hour(hour);
    
    if !is_active_hours {
        // Descansar
        self.state.fsm_state = AgentFSMState::Idle;
        self.state.fsm_timer = rng.gen_range(120..360); // 1-3 hores
        return;
    }
    
    let diet = get_diet(&self.species_key).unwrap_or_default();
    let energy_ratio = self.state.energy_kcal / (self.mass_kg * 10000.0);
    let is_hungry = energy_ratio < 0.3;
    let is_very_hungry = energy_ratio < 0.1;
    
    if is_very_hungry || (is_hungry && rng.gen::<f64>() < 0.3) {
        match self.kind {
            AgentKind::Herbivore => self.start_forage(grid),
            AgentKind::Carnivore => self.start_hunt(grid),
            AgentKind::Omnivore => {
                if diet.plant_proportion > 0.5 && rng.gen::<f64>() < 0.6 {
                    self.start_forage(grid);
                } else {
                    self.start_hunt(grid);
                }
            }
            AgentKind::Bird => self.start_forage(grid),
        }
        return;
    }
    
    // Explorar / moure's aleatòriament
    if rng.gen::<f64>() < 0.1 * self.boldness {
        let target = self.pick_wander_target(grid);
        self.start_travel(grid, target.0, target.1);
        return;
    }
    
    // Per defecte: descansar
    self.state.fsm_state = AgentFSMState::Idle;
    self.state.fsm_timer = rng.gen_range(60..300); // 30 min - 2.5 h
}
```

#### 2.1.7 — TickOutcome (per comunicar al Simulation loop)

```rust
#[derive(Default)]
pub struct TickOutcome {
    pub kill_agent_id: Option<u32>,    // Si l'agent mata a un altre
    pub consume_plant_kg: f64,
    pub consume_invert_kg: f64,
    pub consume_carcass_kg: f64,
    pub consume_fish_kg: f64,
    pub consume_micromammal_kg: f64,
    pub consume_passerine_kg: f64,
    pub consume_herp_kg: f64,
    pub consume_bat_kg: f64,
    pub energy_gain_plant: f64,
    pub energy_gain_invert: f64,
    pub energy_gain_meat: f64,
}
```

---

## FASE 3: Simulation loop amb ticks (1 fitxer)

> **Objectiu**: El `Simulation::step()` processa 2880 ticks per dia en lloc d'1 pas.

### 3.1 — `simulation.rs`

**Arxiu**: `src/sim/simulation.rs`

**Constants**:
```rust
pub const TICKS_PER_DAY: i32 = 2880;
pub const SNAPSHOT_EVERY_TICKS: i32 = 120;  // Cada 60 minuts (1 frame/hora)
pub const LOG_EVERY_TICKS: i32 = 2880;      // Cada dia
```

#### 3.1.1 — Simulation struct (camps nous)

```rust
pub struct Simulation {
    // ... camps existents ...
    pub current_tick: i64,
    pub total_ticks: i64,   // total_days * TICKS_PER_DAY
    pub snapshot_every_ticks: i32,
    pub log_every_ticks: i32,
}
```

#### 3.1.2 — `run()` loop

```rust
pub fn run(&mut self) {
    // ... crear arxius de log ...
    
    for tick in 0..self.total_ticks {
        self.tick(tick);
        
        let day = tick / TICKS_PER_DAY as i64;
        if tick % self.snapshot_every_ticks as i64 == 0 {
            self.snapshot(tick);
        }
        if tick % self.log_every_ticks as i64 == 0 {
            self.log_state(day as i32);
        }
    }
}
```

#### 3.1.3 — `tick()` (nou — substitueix `step()`)

```rust
fn tick(&mut self, tick: i64) {
    let day = tick / TICKS_PER_DAY as i64;
    let tick_in_day = (tick % TICKS_PER_DAY as i64) as i32;
    let is_last_tick_of_day = tick_in_day == TICKS_PER_DAY - 1;
    
    let env = &self.env;
    let grid = &self.grid;
    
    // --- Processar ticks dels agents ---
    let outcomes: Vec<TickOutcome> = self.agents
        .par_iter_mut()
        .map(|agent| {
            let is_cold = self.compute_is_cold();
            agent.tick(grid, env, is_cold)
        })
        .collect();
    
    // --- Aplicar outcomes al grid/pools ---
    self.apply_outcomes(&outcomes);
    
    // --- Predació entre agents ---
    self.predation_tick();
    
    // --- Ecologia (escalat) ---
    let scale = 1.0 / TICKS_PER_DAY as f64;
    let growth_mod = seasonal_growth_modifier(self.env.season().name());
    self.grid.step_plants_logistic(growth_mod * scale);
    self.grid.step_inverts(growth_mod * scale);
    self.grid.decay_carcasses_tick(scale);
    
    // --- 1 cop al dia ---
    if is_last_tick_of_day {
        self.env.step();
        self.grid.step_snow(day as i32);
        self.grid.step_temperature(day as i32);
        self.reproduce_step();
        self.remove_dead();
        self.grid.update_costs();
        
        // Reset counters diaris
        for agent in &mut self.agents {
            agent.state.calories_consumed_today = 0.0;
            agent.state.calories_spent_today = 0.0;
        }
    }
}
```

#### 3.1.4 — `snapshot()` amb tick

```rust
fn snapshot(&self, tick: i64) {
    let snap = serde_json::json!({
        "tick": tick,
        "day": tick / TICKS_PER_DAY as i64,
        "tick_in_day": tick % TICKS_PER_DAY as i64,
        "season": self.env.season().name(),
        "avg_temp_c": ...,
        "snow_cells": ...,
        "agents": self.agents.iter().filter(|a| a.is_alive()).map(|a| {
            serde_json::json!({
                "id": a.agent_id,
                "species": a.species_key,
                "kind": a.kind.name(),
                "gender": ...,
                "mass_kg": ...,
                "x": a.state.pos_x,           // f64 continu
                "y": a.state.pos_y,
                "cell_x": a.state.cell_x,     // cel·la actual
                "cell_y": a.state.cell_y,
                "fsm_state": format!("{:?}", a.state.fsm_state),
                "energy_kcal": ...,
                ...
            })
        }).collect::<Vec<_>>(),
        ...
    });
    let path = self.output_dir.join(format!("snap_{:06}.json", tick));
    std::fs::write(&path, ...);
}
```

#### 3.1.5 — `predation_tick()` (simplificat respecte predation_step)

```rust
fn predation_tick(&mut self) {
    // Versió simplificada: cada tick els carnívors HUNT_CHASE que 
    // comparteixen cel·la amb presa maten.
    // La detecció i persecució es gestiona via FSM individual.
    
    let n = self.agents.len();
    let mut to_kill = vec![false; n];
    
    for i in 0..n {
        if !self.agents[i].is_alive() { continue; }
        if self.agents[i].state.fsm_state != AgentFSMState::HuntChase 
           && self.agents[i].state.fsm_state != AgentFSMState::ForageEat {
            continue;
        }
        
        let prey_list = get_prey(&self.agents[i].species_key);
        let px = self.agents[i].state.cell_x;
        let py = self.agents[i].state.cell_y;
        
        for j in 0..n {
            if i == j || !self.agents[j].is_alive() || to_kill[j] { continue; }
            if self.agents[j].state.cell_x != px || self.agents[j].state.cell_y != py { continue; }
            
            if prey_list.contains(&self.agents[j].species_key) {
                let prey_mass = self.agents[j].mass_kg;
                self.agents[i].state.energy_kcal += prey_mass * get_energy_density_meat() * 0.8;
                to_kill[j] = true;
                break;
            }
        }
    }
    
    // Aplicar morts
    for (j, &kill) in to_kill.iter().enumerate() {
        if kill {
            // Convertir en carronya
            let cell_idx = self.grid.pos_to_idx(self.agents[j].state.cell_x, self.agents[j].state.cell_y);
            self.grid.cell_at_idx_mut(cell_idx).carcass_biomass += self.agents[j].mass_kg * 0.7;
            self.agents[j].state.alive = false;
            self.agents[j].state.fsm_state = AgentFSMState::Dead;
            self.agents[j].state.death_cause = Some(DeathCause::Predation);
        }
    }
}
```

---

## FASE 4: Grid — decay escalable (1 fitxer)

> **Objectiu**: Permetre que `decay_carcasses` accepti un factor d'escala temporal.

### 4.1 — `grid.rs`

**Arxiu**: `src/sim/grid.rs`

**Funció nova**:
```rust
pub fn decay_carcasses_tick(&mut self, scale: f64) {
    // Per tick: carcass *= 0.95^(1/2880) ≈ carcass *= (1 - 0.0000179)
    let decay_per_tick = 0.95f64.powf(scale); // scale = 1/TICKS_PER_DAY
    for cell in &mut self.cells {
        cell.carcass_biomass *= decay_per_tick;
        if cell.carcass_biomass < 0.001 {
            cell.carcass_biomass = 0.0;
        }
    }
}
```

✅ Mantenir `decay_carcasses()` original per compatibilitat (ja no s'usa però no trenca res).

---

## FASE 5: Cicle circadià (1 fitxer)

> **Objectiu**: Cada espècie té un patró d'activitat diària que determina si està activa a cada hora del dia.

### 5.1 — `environment.rs` o nou `circadian.rs`

**Arxiu**: `src/sim/environment.rs`

**Nou mètode a Environment**:
```rust
impl Environment {
    /// Hora actual basada en el tick dins del dia (0-23)
    pub fn current_hour(&self, tick_in_day: i32) -> f64 {
        (tick_in_day as f64 / TICKS_PER_DAY as f64) * 24.0
    }
    
    /// Fracció del dia: 0.0 = mitjanit, 0.25 = 06:00, 0.5 = 12:00, etc.
    pub fn day_fraction(&self, tick_in_day: i32) -> f64 {
        tick_in_day as f64 / TICKS_PER_DAY as f64
    }
}
```

**Perfil d'activitat per espècie** (afegir a la definició d'espècie):
```rust
pub enum ActivityPattern {
    Diurnal,        // 06:00-20:00 (14h actiu)
    Nocturnal,      // 20:00-06:00 (10h actiu)
    Crepuscular,    // 05:00-09:00 + 17:00-21:00 (8h actiu)
    Cathemeral,     // Irregular, actiu quan cal
}
```

**Implementació**:
```rust
impl Agent {
    fn is_active_at_hour(&self, hour: f64) -> bool {
        match self.activity_pattern {
            ActivityPattern::Diurnal => hour >= 6.0 && hour < 20.0,
            ActivityPattern::Nocturnal => hour < 6.0 || hour >= 20.0,
            ActivityPattern::Crepuscular => {
                (hour >= 5.0 && hour < 9.0) || (hour >= 17.0 && hour < 21.0)
            }
            ActivityPattern::Cathemeral => true,
        }
    }
}
```

**Perfils per espècie**:
| Espècie | Patró |
|---------|-------|
| Rupicapra_pyrenaica (isard) | Diürn |
| Cervus_elaphus (cérvol) | Crepuscular |
| Sus_scrofa (senglar) | Crepuscular/Nocturn |
| Vulpes_vulpes (guineu) | Nocturn |
| Martes_martes (marta) | Nocturn |
| Mustela_erminea (ermini) | Diürn |
| Lutra_lutra (llúdriga) | Crepuscular/Nocturn |
| Gypaetus_barbatus (trencalòs) | Diürn |
| Aquila_chrysaetos (àguila) | Diürn |
| Marmota_marmota (marmota) | Diürn |
| Oryctolagus_cuniculus (conill) | Crepuscular/Nocturn |
| Tetrao_urogallus (gall fer) | Diürn |
| Corvus_corax (corb) | Diürn |
| Meles_meles (teixó) | Nocturn |
| Felis_silvestris (gat fer) | Nocturn/Crepuscular |

---

## FASE 6: Generació de GIF (Python)

> **Objectiu**: Script Python que llegeix els snapshots + terrain i genera un GIF animat.

### 6.1 — `src/render_gif.py` (NOU)

**Arxiu**: `src/render_gif.py` (al directori arrel `src/`)

**Requisits**:
```
pip install matplotlib numpy imageio pandas
```

**Funcionament**:
```python
#!/usr/bin/env python3
"""
Renderiza un GIF animado del ecosistema a partir de snapshots.
Uso:
  python render_gif.py --dir output_mig --fps 10 --output animation.gif
"""

def load_terrain(tsv_path):
    """Carga terrain_cells.tsv y devuelve array 2D de elevación y habitat."""
    df = pd.read_csv(tsv_path, sep='\t')
    width = df['x'].max() + 1
    height = df['y'].max() + 1
    elevation = np.zeros((height, width))
    habitat = np.zeros((height, width), dtype=np.uint8)
    for _, row in df.iterrows():
        elevation[int(row['y']), int(row['x'])] = row['elevation_m']
        habitat[int(row['y']), int(row['x'])] = row.get('habitat_type', 0)
    return elevation, habitat

def render_frame(ax, elevation, habitat, agents, day, tick, season, temp):
    """Renderiza un frame del GIF."""
    ax.clear()
    
    # Fondo: elevación en escala de grises o habitat en color
    if habitat.max() > 0:
        # Mapa de hábitat (colores)
        habitat_cmap = {
            0: '#888888', 1: '#1a5e1a', 2: '#3a9e3a', 3: '#8ab87a',
            4: '#c4d68a', 5: '#6ab0c4', 6: '#a0a0a0', 7: '#3070b0',
            8: '#60a060', 9: '#ffffff', 10: '#c06060',
        }
        habitat_rgb = np.zeros((*habitat.shape, 3))
        for h, color in habitat_cmap.items():
            mask = habitat == h
            rgb = tuple(int(color[i:i+2], 16)/255 for i in (1, 3, 5))
            for c in range(3):
                habitat_rgb[mask, c] = rgb[c]
        ax.imshow(habitat_rgb, origin='lower')
    else:
        ax.imshow(elevation, cmap='terrain', origin='lower')
    
    # Superponer agentes
    colors = plt.cm.tab20(np.linspace(0, 1, 21))
    species_list = list(set(a['species'] for a in agents))
    species_color = {s: colors[i % 20] for i, s in enumerate(species_list)}
    
    for a in agents:
        color = species_color.get(a['species'], 'white')
        marker = {'HERBIVORE': 'o', 'CARNIVORE': '^', 'OMNIVORE': 's', 'BIRD': 'D'}.get(a['kind'], 'o')
        size = max(10, a['mass_kg'] * 2)
        ax.plot(a['cell_x'], a['cell_y'], marker, color=color, 
                markersize=size/5, markeredgecolor='black', markeredgewidth=0.3)
    
    ax.set_title(f'Dia {day} Tick {tick} | {season} | {temp}°C')
    ax.set_xlabel('X (cel·les)')
    ax.set_ylabel('Y (cel·les)')
    ax.set_aspect('equal')

def generate_gif(snapshots_dir, terrain_path, output_path, fps=10, max_frames=None):
    """Genera GIF a partir de snapshots JSON."""
    import imageio
    import glob, json
    
    snap_files = sorted(glob.glob(f'{snapshots_dir}/snap_*.json'))
    if max_frames:
        snap_files = snap_files[:max_frames]
    
    elevation, habitat = load_terrain(terrain_path)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    frames = []
    
    for i, snap_file in enumerate(snap_files):
        with open(snap_file) as f:
            data = json.load(f)
        
        render_frame(ax, elevation, habitat, data['agents'],
                    data['day'], data.get('tick_in_day', 0),
                    data['season'], data['avg_temp_c'])
        
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)
        
        if (i+1) % 10 == 0:
            print(f'  Frame {i+1}/{len(snap_files)}')
    
    imageio.mimsave(output_path, frames, fps=fps, loop=0)
    print(f'GIF guardado: {output_path} ({len(frames)} frames, {fps}fps)')
```

---

## FASE 7: Migració de dades i constants d'espècie

> **Objectiu**: Convertir les poblacions de `PopulationConfig` al nou format amb velocitat en m/s i activity_pattern.

### 7.1 — `simulation.rs` — `DEFAULT_POPULATIONS` actualitzat

```rust
pub const DEFAULT_POPULATIONS: &[PopulationConfig] = &[
    PopulationConfig {
        species_key: "Rupicapra_pyrenaica",
        common_name: "Isard",
        count: 600,
        mass_kg: 35.0,
        kind: AgentKind::Herbivore,
        speed_ms: 3.0 / 3.6,           // 3 km/h → 0.833 m/s
        home_range_m: 200.0,            // ~8 cel·les × 25m
        gestation_ticks: 165 * TICKS_PER_DAY as i64,
        litter_size_min: 1,
        litter_size_max: 1,
        reproductive_age_ticks: 365 * TICKS_PER_DAY as i64,
        lifespan_ticks: 5840 * TICKS_PER_DAY as i64,
        activity_pattern: ActivityPattern::Diurnal,
    },
    // ... etc
];
```

**Conversió de velocitats**:
| Espècie | speed_kmh | speed_ms | metres/tick (30s) |
|---------|-----------|----------|-------------------|
| Isard | 3.0 | 0.833 | 25.0 (1 cel·la) |
| Cérvol | 4.0 | 1.111 | 33.3 |
| Senglar | 3.5 | 0.972 | 29.2 |
| Guineu | 3.0 | 0.833 | 25.0 |
| Àguila | 5.0 | 1.389 | 41.7 |
| Marmota | 1.5 | 0.417 | 12.5 |
| Conill | 2.5 | 0.694 | 20.8 |
| Mostela | 1.5 | 0.417 | 12.5 |

---

## Ordre d'implementació (FASES)

| Fase | Fitxers | Esforç | Risc | Prioritat |
|------|---------|--------|------|-----------|
| **1** Energy tick | `energy.rs` | 1 hora | Baix | 1a |
| **2** FSM Agent | `agents.rs` | 3-4 hores | Alt | 2a |
| **3** Simulation loop | `simulation.rs` | 2-3 hores | Alt | 3a |
| **4** Grid decay | `grid.rs` | 15 min | Molt baix | 4a |
| **5** Circadià | `environment.rs` | 30 min | Baix | 5a |
| **6** GIF Python | `src/render_gif.py` | 1-2 hores | Baix | Paral·lel |
| **7** Migració dades | `simulation.rs` | 1 hora | Mitjà | 6a |

**Recomanació**: Fer una **branch** i implementar Fase 1 + 2 junts, compilar, després Fase 3, compilar, i testejar amb `--demo` abans de continuar.

---

## Verificació

Després de cada fase, compilar i executar:
```bash
cd ecosystem_simulator_rs
cargo build --release
cargo run --release -- --width 30 --height 30 --days 10 --output test_tick
```

**Comprovacions**:
- [ ] Els agents es mouen ≥1 cel·la per dia (mínim 8 amb 8 hores de viatge)
- [ ] Energia decreix a ritme realista
- [ ] Animals diürns es mouen de dia, nocturns de nit
- [ ] Carronya decau correctament
- [ ] Plantes creixen a ritme escalat
- [ ] Snapshots es generen i el GIF es veu fluid
- [ ] Poblacions estables a 365 dies

---

## Possibles colls d'ampolla i solucions

| Problema | Solució |
|----------|---------|
| A* a cada tick | Cachejar el camí i recalcul·lar cada 60-300 ticks |
| 3000 agents × 2880 ticks × 365 dies = 3.15B ticks | Rust ho maneja (cada tick és O(1) o O(alguns A*)), però es pot reduir a 1440/dia |
| Snapshot JSON massa gran | Comprimir, o només guardar posicions + energia (no tot l'estat) |
| GIF de 8760 frames | Mostrar 1 frame cada 60 minuts = 8760 frames → a 10fps = 15m; usar `--max-frames 365` per defecte |
| Coordenades f64 fora del grid | Clamping a `simulation.rs` |

---

## Resum

**Abans**: 1 acció/dia, moviment 1 cel·la/dia, sense cicle dia/nit, sense caça realista.

**Després**: 30s/tick, moviment continu en metres, FSM amb caça/persecució, cicle circadià, GIF animat sobre mapa de terreny.
