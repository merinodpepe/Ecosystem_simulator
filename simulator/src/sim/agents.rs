use rand::Rng;

use super::energy::{
    critical_energy_threshold, get_energy_density_fruit, get_energy_density_invert,
    get_energy_density_meat, get_energy_density_plant, get_energy_density_seed,
    intake_per_tick, met_for_state, tick_energy, TICKS_PER_DAY as TICKS_F,
};

/// Maximum fat reserves as multiple of maintenance energy.
/// Fat yields ~9000 kcal/kg, but we cap at mass * 5000 for realism.
const MAX_FAT_RATIO: f64 = 5000.0;
use super::foodweb::{get_diet, get_prey_weighted};
use super::grid::TerrainGrid;
use super::pathfinding::a_star_path;

#[derive(Clone, Copy, PartialEq)]
pub enum AgentKind {
    Herbivore,
    Carnivore,
    Omnivore,
    Bird,
}

impl AgentKind {
    pub fn name(&self) -> &'static str {
        match self {
            AgentKind::Herbivore => "HERBIVORE",
            AgentKind::Carnivore => "CARNIVORE",
            AgentKind::Omnivore => "OMNIVORE",
            AgentKind::Bird => "BIRD",
        }
    }
}

#[derive(Clone, Copy, PartialEq)]
pub enum Gender {
    Male,
    Female,
}

#[derive(Clone, Copy, PartialEq)]
pub enum DeathCause {
    Starvation,
    OldAge,
    Predation,
}

#[derive(Clone, Copy, PartialEq)]
pub enum AgentFSMState {
    Idle,
    Travel,
    ForageSearch,
    ForageEat,
    HuntStalk,
    HuntChase,
    EatCarcass,
    Drink,
    Flee,
    Dead,
}

impl AgentFSMState {
    pub fn as_str(&self) -> &'static str {
        match self {
            AgentFSMState::Idle => "IDLE",
            AgentFSMState::Travel => "TRAVEL",
            AgentFSMState::ForageSearch => "FORAGE_SEARCH",
            AgentFSMState::ForageEat => "FORAGE_EAT",
            AgentFSMState::HuntStalk => "HUNT_STALK",
            AgentFSMState::HuntChase => "HUNT_CHASE",
            AgentFSMState::EatCarcass => "EAT_CARCASS",
            AgentFSMState::Drink => "DRINK",
            AgentFSMState::Flee => "FLEE",
            AgentFSMState::Dead => "DEAD",
        }
    }
}

#[derive(Clone, Copy, PartialEq)]
pub enum ActivityPattern {
    Diurnal,
    Nocturnal,
    Crepuscular,
    Cathemeral,
}

#[derive(Clone)]
pub struct AgentState {
    // Continuous position (metres within the grid)
    pub pos_x: f64,
    pub pos_y: f64,
    pub cell_x: i32,
    pub cell_y: i32,

    // FSM
    pub fsm_state: AgentFSMState,
    pub fsm_timer: i32,
    pub fsm_path: Vec<(i32, i32)>,
    pub fsm_path_index: usize,
    pub fsm_target_cell: (i32, i32),
    pub fsm_replan_counter: i32,

    // Energy (kcal)
    pub energy_kcal: f64,
    pub fat_reserve_kcal: f64,
    pub mass_kg: f64,
    pub age_ticks: i64,
    pub alive: bool,

    // Biology (daily-scale counters)
    pub gender: Gender,
    pub is_pregnant: bool,
    pub is_lactating: bool,
    pub gestation_ticks: i32,
    pub days_since_reproduction: i32,
    pub lactation_timer: i32,
    pub is_hibernating: bool,
    pub is_hyperphagia: bool,

    // Metrics
    pub calories_consumed_today: f64,
    pub calories_spent_today: f64,
    pub days_below_critical_energy: i32,
    pub death_cause: Option<DeathCause>,
}

#[derive(Clone)]
pub struct Agent {
    pub agent_id: u32,
    pub species_key: String,
    pub common_name: String,
    pub mass_kg: f64,
    pub adult_mass_kg: f64,
    pub kind: AgentKind,
    pub state: AgentState,

    // Movement (metres per second, real)
    pub speed_ms: f64,
    pub home_range_m: f64,

    // Reproduction
    pub gestation_ticks_total: i32,
    pub lactation_ticks_total: i32,
    pub litter_size_min: u32,
    pub litter_size_max: u32,
    pub reproductive_age_ticks: i64,
    pub lifespan_ticks: i64,

    // Personality
    pub boldness: f64,
    // Circadian rhythm
    pub activity_pattern: ActivityPattern,
}

#[derive(Clone, Default)]
pub struct TickOutcome {
    pub kill_agent_id: Option<u32>,
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

impl AgentState {
    pub fn new_continuous(pos_x: f64, pos_y: f64, cell_x: i32, cell_y: i32, mass_kg: f64, gender: Gender) -> Self {
        AgentState {
            pos_x, pos_y, cell_x, cell_y,
            fsm_state: AgentFSMState::Idle,
            fsm_timer: 0,
            fsm_path: Vec::new(),
            fsm_path_index: 0,
            fsm_target_cell: (cell_x, cell_y),
            fsm_replan_counter: 0,
            energy_kcal: mass_kg * super::energy::INITIAL_ENERGY_RATIO,
            fat_reserve_kcal: mass_kg * 1000.0,
            mass_kg,
            age_ticks: 0,
            alive: true,
            gender,
            is_pregnant: false,
            is_lactating: false,
            gestation_ticks: 0,
            days_since_reproduction: if gender == Gender::Male { i32::MAX / 2 } else { 1 },
            lactation_timer: 0,
            is_hibernating: false,
            is_hyperphagia: false,
            calories_consumed_today: 0.0,
            calories_spent_today: 0.0,
            days_below_critical_energy: 0,
            death_cause: None,
        }
    }
}

impl Agent {
    pub fn is_alive(&self) -> bool {
        self.state.alive
    }

    pub fn is_active_at_hour(&self, hour: f64) -> bool {
        match self.activity_pattern {
            ActivityPattern::Diurnal => hour >= 6.0 && hour < 20.0,
            ActivityPattern::Nocturnal => hour < 6.0 || hour >= 20.0,
            ActivityPattern::Crepuscular => {
                (hour >= 5.0 && hour < 9.0) || (hour >= 17.0 && hour < 21.0)
            }
            ActivityPattern::Cathemeral => true,
        }
    }

    /// Main tick: execute current FSM state, spend energy, check death.
    pub fn tick(&mut self, grid: &TerrainGrid, is_autumn: bool, is_winter: bool) -> TickOutcome {
        if !self.state.alive {
            return TickOutcome::default();
        }
        if self.state.is_hibernating {
            let cost = tick_energy(self.mass_kg, 0.0, 0.0, true);
            self.state.fat_reserve_kcal -= cost;
            self.state.age_ticks += 1;
            return TickOutcome::default();
        }

        let cell_temp = if grid.in_bounds(self.state.cell_x, self.state.cell_y) {
            grid.cell(self.state.cell_x as u32, self.state.cell_y as u32).temperature_c
        } else {
            5.0
        };

        let outcome = match self.state.fsm_state {
            AgentFSMState::Idle => self.tick_idle(),
            AgentFSMState::Travel => self.tick_travel(grid),
            AgentFSMState::ForageSearch => self.tick_forage_search(grid),
            AgentFSMState::ForageEat => self.tick_forage_eat(grid),
            AgentFSMState::HuntStalk => self.tick_hunt_stalk(grid),
            AgentFSMState::HuntChase => self.tick_hunt_chase(grid),
            AgentFSMState::EatCarcass => self.tick_eat_carcass(),
            AgentFSMState::Flee => self.tick_idle(),
            AgentFSMState::Drink => TickOutcome::default(),
            AgentFSMState::Dead => TickOutcome::default(),
        };

        let met = met_for_state(self.state.fsm_state.as_str());
        let cost = tick_energy(self.mass_kg, met, cell_temp, is_winter);
        self.state.energy_kcal -= cost;
        self.state.calories_spent_today += cost;

        // Update FSM timer
        if self.state.fsm_timer > 0 {
            self.state.fsm_timer -= 1;
        }
        if self.state.fsm_replan_counter > 0 {
            self.state.fsm_replan_counter -= 1;
        }

        // Advance age
        self.state.age_ticks += 1;

        // Advance gestation if pregnant
        if self.state.is_pregnant {
            self.state.gestation_ticks += 1;
        }

        // --- Seasonal fat reserve management ---
        // In autumn, lower the ceiling so more surplus goes to fat (hyperphagia)
        // In winter, also store aggressively if not hibernating
        let ceiling_mult = if is_autumn { 0.8 } else if is_winter { 1.0 } else { 1.5 };
        let energy_ceiling = self.mass_kg * super::energy::INITIAL_ENERGY_RATIO * ceiling_mult;
        if self.state.energy_kcal > energy_ceiling {
            let excess = self.state.energy_kcal - energy_ceiling;
            let room = (self.mass_kg * MAX_FAT_RATIO) - self.state.fat_reserve_kcal;
            let deposit = excess.min(room).max(0.0);
            self.state.fat_reserve_kcal += deposit;
            self.state.energy_kcal -= deposit;
        }

        // If energy is low, draw from fat reserves first
        let critical = critical_energy_threshold(self.mass_kg);
        if self.state.energy_kcal < critical && self.state.fat_reserve_kcal > 0.0 {
            let needed = critical - self.state.energy_kcal;
            let withdrawn = needed.min(self.state.fat_reserve_kcal);
            self.state.fat_reserve_kcal -= withdrawn;
            self.state.energy_kcal += withdrawn;
        }

        // Check starvation (total_energy below critical for 3+ days)
        let total_energy = self.state.energy_kcal + self.state.fat_reserve_kcal;
        if total_energy < critical {
            self.state.days_below_critical_energy += 1;
            if self.state.days_below_critical_energy >= 3 * TICKS_F as i32 {
                self.state.alive = false;
                self.state.fsm_state = AgentFSMState::Dead;
                self.state.death_cause = Some(DeathCause::Starvation);
            }
        } else {
            self.state.days_below_critical_energy = 0;
        }

        outcome
    }

    /// Re-route the agent: decide next action based on needs and environment.
    pub fn reroute(&mut self, grid: &TerrainGrid, tick_in_day: i32) {
        if !self.state.alive || self.state.is_hibernating {
            return;
        }
        let mut rng = rand::thread_rng();
        let hour = (tick_in_day as f64 / TICKS_F) * 24.0;

        // 1. Flee if predator detected (future: perception system)
        // 2. Diurnal/nocturnal cycle: rest if not active hours
        if !self.is_active_at_hour(hour) {
            self.state.fsm_state = AgentFSMState::Idle;
            self.state.fsm_timer = rng.gen_range(120..360);
            return;
        }

        let energy_ratio = self.state.energy_kcal / (self.mass_kg * super::energy::INITIAL_ENERGY_RATIO);
        // Seasonal hyperphagia: in autumn, agents eat more aggressively to build fat
        let is_pre_winter = self.state.is_hyperphagia;
        let hunger_threshold = if is_pre_winter { 0.5 } else { 0.3 };
        let is_hungry = energy_ratio < hunger_threshold;
        let is_very_hungry = energy_ratio < 0.1;
        let diet = get_diet(&self.species_key).unwrap_or_default();

        if is_very_hungry || (is_hungry && rng.gen::<f64>() < 0.4) {
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

        // If on carcass and diet includes carrion
        if diet.carrion_proportion > 0.0 {
            let cx = self.state.cell_x as u32;
            let cy = self.state.cell_y as u32;
            if grid.in_bounds(cx as i32, cy as i32) && grid.cell(cx, cy).carcass_biomass > 0.001 {
                self.state.fsm_state = AgentFSMState::EatCarcass;
                self.state.fsm_timer = rng.gen_range(30..120);
                return;
            }
        }

        // Random exploration
        if rng.gen::<f64>() < 0.1 * self.boldness {
            let target = self.wander_target(grid);
            self.start_travel(grid, target.0, target.1);
            return;
        }

        // Default: idle for a while
        self.state.fsm_state = AgentFSMState::Idle;
        self.state.fsm_timer = rng.gen_range(60..300);
    }

    // === FSM State Handlers ===

    fn tick_idle(&mut self) -> TickOutcome {
        TickOutcome::default()
    }

    fn tick_travel(&mut self, grid: &TerrainGrid) -> TickOutcome {
        if self.state.fsm_path.is_empty() || self.state.fsm_path_index >= self.state.fsm_path.len() {
            self.state.fsm_state = AgentFSMState::Idle;
            return TickOutcome::default();
        }

        let speed_mt = self.speed_ms * super::energy::SECONDS_PER_TICK;

        // Replan A* every 60 ticks if we still have a path
        if self.state.fsm_replan_counter == 0 && self.state.fsm_path.len() > 1 {
            let from = (self.state.cell_x, self.state.cell_y);
            let to = self.state.fsm_target_cell;
            if from != to {
                if let Some(new_path) = a_star_path(grid, from, to, 1000) {
                    self.state.fsm_path = new_path;
                    self.state.fsm_path_index = 0;
                }
            }
            self.state.fsm_replan_counter = 60;
        }

        let (tcx, tcy) = self.state.fsm_path[self.state.fsm_path_index];
        let target_cx = tcx as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;
        let target_cy = tcy as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;

        let dx = target_cx - self.state.pos_x;
        let dy = target_cy - self.state.pos_y;
        let dist = (dx * dx + dy * dy).sqrt();

        if dist <= speed_mt {
            self.state.pos_x = target_cx;
            self.state.pos_y = target_cy;
            self.state.cell_x = tcx;
            self.state.cell_y = tcy;
            self.state.fsm_path_index += 1;
        } else {
            let ratio = speed_mt / dist;
            self.state.pos_x += dx * ratio;
            self.state.pos_y += dy * ratio;
            let new_cx = (self.state.pos_x / grid.resolution_m as f64) as i32;
            let new_cy = (self.state.pos_y / grid.resolution_m as f64) as i32;
            if new_cx != self.state.cell_x || new_cy != self.state.cell_y {
                // Crossed into new cell — check bounds
                if grid.in_bounds(new_cx, new_cy) {
                    self.state.cell_x = new_cx;
                    self.state.cell_y = new_cy;
                } else {
                    // Clamp: out of bounds, stop movement
                    self.state.cell_x = self.state.cell_x.clamp(0, grid.width as i32 - 1);
                    self.state.cell_y = self.state.cell_y.clamp(0, grid.height as i32 - 1);
                    self.state.pos_x = self.state.cell_x as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;
                    self.state.pos_y = self.state.cell_y as f64 * grid.resolution_m as f64 + grid.resolution_m as f64 / 2.0;
                    self.state.fsm_path_index = self.state.fsm_path.len();
                }
            }
        }

        TickOutcome::default()
    }

    fn tick_forage_search(&mut self, _grid: &TerrainGrid) -> TickOutcome {
        // Transition to FORAGE_EAT after search time
        self.state.fsm_state = AgentFSMState::ForageEat;
        self.state.fsm_timer = 10;
        TickOutcome::default()
    }

    fn tick_forage_eat(&mut self, grid: &TerrainGrid) -> TickOutcome {
        let diet = get_diet(&self.species_key).unwrap_or_default();
        let edible = diet.plant_proportion + diet.invert_proportion;
        if edible <= 0.0 {
            return TickOutcome::default();
        }

        // Check available biomass in current cell and cap intake
        let cx = self.state.cell_x as u32;
        let cy = self.state.cell_y as u32;
        let cell = grid.cell(cx, cy);
        let avail_plant = cell.total_plant_biomass();
        let avail_invert = cell.total_invert_biomass();

        // 1.5x intake multiplier for foragers (plants are less energy-dense than meat)
        let desired = intake_per_tick(self.mass_kg) * 1.5;
        let plant_kg = (desired * diet.plant_proportion / edible).min(avail_plant);
        let invert_kg = (desired * diet.invert_proportion / edible).min(avail_invert);

        let plant_kcal = get_energy_density_plant() * 0.5
            + get_energy_density_seed() * 0.3
            + get_energy_density_fruit() * 0.2;
        let gain_plant = plant_kg * plant_kcal * 0.65;
        let gain_invert = invert_kg * get_energy_density_invert() * 0.65;

        self.state.energy_kcal += gain_plant + gain_invert;
        self.state.calories_consumed_today += gain_plant + gain_invert;

        // Keep eating if food remains, else switch to search
        let remaining = avail_plant + avail_invert - (plant_kg + invert_kg);
        self.state.fsm_timer = if remaining > 0.001 { 120 } else { 5 };

        TickOutcome {
            consume_plant_kg: plant_kg,
            consume_invert_kg: invert_kg,
            energy_gain_plant: gain_plant,
            energy_gain_invert: gain_invert,
            ..Default::default()
        }
    }

    fn tick_hunt_stalk(&mut self, grid: &TerrainGrid) -> TickOutcome {
        // Move toward detected prey at reduced speed (MET=2.0 vs TRAVEL MET=2.5)
        // For now, same as travel but with stalking behavior
        self.tick_travel(grid)
    }

    fn tick_hunt_chase(&mut self, _grid: &TerrainGrid) -> TickOutcome {
        // High-speed chase (MET=7.0). In a full implementation this
        // would close distance rapidly and trigger EatCarcass on contact.
        TickOutcome::default()
    }

    fn tick_eat_carcass(&mut self) -> TickOutcome {
        let intake = intake_per_tick(self.mass_kg);
        let energy = intake * get_energy_density_meat() * 0.8;
        self.state.energy_kcal += energy;
        self.state.calories_consumed_today += energy;
        self.state.fsm_timer = 60;
        TickOutcome {
            consume_carcass_kg: intake,
            energy_gain_meat: energy,
            ..Default::default()
        }
    }

    // === FSM State Starters ===

    fn start_travel(&mut self, grid: &TerrainGrid, tx: i32, ty: i32) {
        let from = (self.state.cell_x, self.state.cell_y);
        let to = (tx, ty);
        if from == to {
            self.state.fsm_state = AgentFSMState::Idle;
            return;
        }
        self.state.fsm_target_cell = to;
        if let Some(path) = a_star_path(grid, from, to, 5000) {
            self.state.fsm_path = path;
            self.state.fsm_path_index = 0;
            self.state.fsm_state = AgentFSMState::Travel;
            self.state.fsm_replan_counter = 60;
        } else {
            self.state.fsm_state = AgentFSMState::Idle;
        }
    }

    fn start_forage(&mut self, grid: &TerrainGrid) {
        let diet = get_diet(&self.species_key).unwrap_or_default();
        let cx = self.state.cell_x as u32;
        let cy = self.state.cell_y as u32;

        // If current cell has food, eat directly
        let cell = grid.cell(cx, cy);
        let available = cell.total_plant_biomass() * diet.plant_proportion
            + cell.total_invert_biomass() * diet.invert_proportion;
        if available > 0.001 {
            self.state.fsm_state = AgentFSMState::ForageEat;
            self.state.fsm_timer = 60;
            return;
        }

        // Look for best cell within radius
        let best = self.look_for_best_cell(grid, 8);
        if best != (self.state.cell_x, self.state.cell_y) {
            self.start_travel(grid, best.0, best.1);
        } else {
            self.state.fsm_state = AgentFSMState::ForageSearch;
            self.state.fsm_timer = 10;
        }
    }

    fn start_hunt(&mut self, grid: &TerrainGrid) {
        let cx = self.state.cell_x;
        let cy = self.state.cell_y;
        let radius = (self.home_range_m / grid.resolution_m as f64) as i32;
        let weighted_prey = get_prey_weighted(&self.species_key);
        if weighted_prey.is_empty() {
            // No prey in trophic matrix, go forage instead
            self.start_forage(grid);
            return;
        }

        // Check nearby cells for prey biomass (proxy)
        let prey_cells = self.detect_prey_cells(grid, radius.min(20));
        if !prey_cells.is_empty() {
            let mut rng = rand::thread_rng();
            let idx = rng.gen_range(0..prey_cells.len().min(5));
            let target = prey_cells[idx];
            if target != (cx, cy) {
                self.start_travel(grid, target.0, target.1);
                self.state.fsm_state = AgentFSMState::HuntStalk;
                return;
            }
        }

        // Wander
        let target = self.wander_target(grid);
        self.start_travel(grid, target.0, target.1);
    }

    // === Utility Methods ===

    fn look_for_best_cell(&self, grid: &TerrainGrid, radius: i32) -> (i32, i32) {
        let mut best_score = -1.0f64;
        let mut best_pos = (self.state.cell_x, self.state.cell_y);
        let (cx, cy) = (self.state.cell_x, self.state.cell_y);
        let diet = get_diet(&self.species_key).unwrap_or_default();
        for dy in -radius..=radius {
            for dx in -radius..=radius {
                let (nx, ny) = (cx + dx, cy + dy);
                if !grid.in_bounds(nx, ny) {
                    continue;
                }
                let cell = grid.cell(nx as u32, ny as u32);
                let score = (cell.total_plant_biomass() * diet.plant_proportion
                    + cell.total_invert_biomass() * diet.invert_proportion)
                    / cell.cost_a_star.max(0.1);
                if score > best_score {
                    best_score = score;
                    best_pos = (nx, ny);
                }
            }
        }
        best_pos
    }

    fn detect_prey_cells(&self, grid: &TerrainGrid, radius: i32) -> Vec<(i32, i32)> {
        let (cx, cy) = (self.state.cell_x, self.state.cell_y);
        let weighted_prey = get_prey_weighted(&self.species_key);
        if weighted_prey.is_empty() {
            return Vec::new();
        }
        let mut targets = Vec::new();
        for dy in -radius..=radius {
            for dx in -radius..=radius {
                let (nx, ny) = (cx + dx, cy + dy);
                if !grid.in_bounds(nx, ny) {
                    continue;
                }
                let cell = grid.cell(nx as u32, ny as u32);
                let score = cell.carcass_biomass * 5.0
                    + cell.total_invert_biomass() * 2.0
                    + cell.total_plant_biomass() * 0.2;
                if score > 0.05 {
                    targets.push((nx, ny));
                }
            }
        }
        targets.sort_by(|a, b| {
            let da = (a.0 - cx).abs() + (a.1 - cy).abs();
            let db = (b.0 - cx).abs() + (b.1 - cy).abs();
            da.cmp(&db)
        });
        targets
    }

    fn wander_target(&self, grid: &TerrainGrid) -> (i32, i32) {
        let mut rng = rand::thread_rng();
        let (cx, cy) = (self.state.cell_x, self.state.cell_y);
        let radius = (self.home_range_m / grid.resolution_m as f64 * rng.gen_range(0.3..1.0)) as i32;
        for _ in 0..20 {
            let nx = cx + rng.gen_range(-radius..=radius);
            let ny = cy + rng.gen_range(-radius..=radius);
            if grid.in_bounds(nx, ny) {
                return (nx, ny);
            }
        }
        (cx, cy)
    }

    pub fn should_reproduce(&self, density_factor: f64) -> bool {
        if self.state.gender != Gender::Female {
            return false;
        }
        let energy_threshold = match self.kind {
            AgentKind::Herbivore => self.mass_kg * 1500.0,
            AgentKind::Carnivore => self.mass_kg * 2000.0,
            AgentKind::Omnivore => self.mass_kg * 1800.0,
            AgentKind::Bird => self.mass_kg * 1500.0,
        };
        let total_energy = self.state.energy_kcal + self.state.fat_reserve_kcal;
        let mut rng = rand::thread_rng();
        // density_factor: 1.0 = at carrying capacity, 0.0 = empty
        // Reduces reproduction as population approaches carrying capacity
        // At twice capacity (density=2), reproduction drops to zero
        // At depletion (density near 0), chance doubles to aid recovery
        let density_mod = (2.0 - density_factor).max(0.0).min(2.0);
        let chance = rng.gen::<f64>() < 0.3 * density_mod;
        self.state.days_since_reproduction > 60
            && total_energy > energy_threshold
            && !self.state.is_pregnant
            && !self.state.is_lactating
            && chance
    }
}
