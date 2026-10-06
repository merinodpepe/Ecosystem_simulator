use std::path::{Path, PathBuf};

use rand::Rng;
use rayon::prelude::*;

use super::agents::{
    Agent, AgentKind, AgentFSMState, ActivityPattern, AgentState, DeathCause, Gender, TickOutcome,
};
use super::energy::{
    get_energy_density_meat, load_activity_costs, load_energy_data, TICKS_PER_DAY as TICKS_F,
};
use super::environment::{Environment, Season};
use super::foodweb::{
    get_all_trophic_links, get_diet, get_prey, is_data_loaded, load_diet_data, load_trophic_data,
};
use super::grid::{habitat, piso, seasonal_growth_modifier, TerrainGrid};
use super::io;
use super::pools::PoolManager;

const TICKS_PER_DAY: i32 = TICKS_F as i32;
const REROUTE_EVERY_TICKS: i32 = 600;

struct HabitatPref {
    habitats: &'static [u8],
    pisos: &'static [u8],
}

const SPECIES_HABITAT: &[(&str, HabitatPref)] = &[
    ("Rupicapra_pyrenaica", HabitatPref { habitats: &[habitat::PASTIZAL, habitat::ROCA], pisos: &[piso::ALPINO] }),
    ("Cervus_elaphus", HabitatPref { habitats: &[habitat::BOSQUE_CAD, habitat::PASTIZAL], pisos: &[piso::MONTANO] }),
    ("Capreolus_capreolus", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::BOSQUE_CAD, habitat::MATORRAL], pisos: &[piso::SUBALPINO] }),
    ("Sus_scrofa", HabitatPref { habitats: &[habitat::BOSQUE_CAD, habitat::BOSQUE_CON], pisos: &[piso::MONTANO] }),
    ("Marmota_marmota", HabitatPref { habitats: &[habitat::PASTIZAL], pisos: &[piso::ALPINO] }),
    ("Oryctolagus_cuniculus", HabitatPref { habitats: &[habitat::PASTIZAL, habitat::MATORRAL], pisos: &[piso::MONTANO] }),
    ("Sciurus_vulgaris", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::BOSQUE_CAD], pisos: &[piso::MONTANO, piso::SUBALPINO] }),
    ("Vulpes_vulpes", HabitatPref { habitats: &[], pisos: &[] }),
    ("Meles_meles", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::BOSQUE_CAD], pisos: &[piso::MONTANO, piso::SUBALPINO] }),
    ("Martes_martes", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::BOSQUE_CAD], pisos: &[piso::MONTANO, piso::SUBALPINO] }),
    ("Felis_silvestris", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::BOSQUE_CAD], pisos: &[piso::MONTANO, piso::SUBALPINO] }),
    ("Mustela_erminea", HabitatPref { habitats: &[habitat::PASTIZAL, habitat::ROCA], pisos: &[piso::ALPINO] }),
    ("Mustela_nivalis", HabitatPref { habitats: &[], pisos: &[] }),
    ("Tetrao_urogallus", HabitatPref { habitats: &[habitat::BOSQUE_CON, habitat::MATORRAL], pisos: &[piso::SUBALPINO] }),
    ("Lagopus_muta", HabitatPref { habitats: &[habitat::PASTIZAL, habitat::ROCA], pisos: &[piso::ALPINO] }),
    ("Corvus_corax", HabitatPref { habitats: &[], pisos: &[] }),
    ("Gypaetus_barbatus", HabitatPref { habitats: &[habitat::ROCA], pisos: &[piso::MONTANO, piso::SUBALPINO, piso::ALPINO] }),
    ("Aquila_chrysaetos", HabitatPref { habitats: &[habitat::ROCA], pisos: &[] }),
    ("Lutra_lutra", HabitatPref { habitats: &[habitat::AGUA, habitat::RIBERA], pisos: &[] }),
    ("Ovis_aries_musimon", HabitatPref { habitats: &[habitat::PASTIZAL, habitat::ROCA], pisos: &[piso::ALPINO] }),
    ("Dama_dama", HabitatPref { habitats: &[habitat::BOSQUE_CAD, habitat::PASTIZAL], pisos: &[piso::MONTANO] }),
];

pub struct PopulationConfig {
    pub species_key: &'static str,
    pub common_name: &'static str,
    pub count: u32,
    pub mass_kg: f64,
    pub kind: AgentKind,
    pub home_range_m: f64,
    pub gestation_days: i32,
    pub lactation_days: i32,
    pub litter_size_min: u32,
    pub litter_size_max: u32,
    pub reproductive_age_days: i32,
    pub lifespan_days: i32,
    pub speed_kmh: f64,
    pub activity_pattern: &'static str,
}

pub const DEFAULT_POPULATIONS: &[PopulationConfig] = &[
    PopulationConfig { species_key: "Rupicapra_pyrenaica", common_name: "Isard", count: 600, mass_kg: 35.0, kind: AgentKind::Herbivore, home_range_m: 200.0, gestation_days: 165, lactation_days: 90, litter_size_min: 1, litter_size_max: 1, reproductive_age_days: 365, lifespan_days: 5840, speed_kmh: 3.0, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Cervus_elaphus", common_name: "Cérvol", count: 200, mass_kg: 200.0, kind: AgentKind::Herbivore, home_range_m: 375.0, gestation_days: 235, lactation_days: 180, litter_size_min: 1, litter_size_max: 1, reproductive_age_days: 730, lifespan_days: 7300, speed_kmh: 4.0, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Capreolus_capreolus", common_name: "Cabirol", count: 300, mass_kg: 20.0, kind: AgentKind::Herbivore, home_range_m: 250.0, gestation_days: 280, lactation_days: 120, litter_size_min: 1, litter_size_max: 2, reproductive_age_days: 365, lifespan_days: 5840, speed_kmh: 3.5, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Sus_scrofa", common_name: "Senglar", count: 200, mass_kg: 100.0, kind: AgentKind::Omnivore, home_range_m: 300.0, gestation_days: 115, lactation_days: 90, litter_size_min: 4, litter_size_max: 8, reproductive_age_days: 365, lifespan_days: 4380, speed_kmh: 3.5, activity_pattern: "nocturnal" },
    PopulationConfig { species_key: "Marmota_marmota", common_name: "Marmota", count: 200, mass_kg: 4.5, kind: AgentKind::Herbivore, home_range_m: 125.0, gestation_days: 34, lactation_days: 40, litter_size_min: 2, litter_size_max: 6, reproductive_age_days: 365, lifespan_days: 5475, speed_kmh: 1.5, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Oryctolagus_cuniculus", common_name: "Conill", count: 600, mass_kg: 1.2, kind: AgentKind::Herbivore, home_range_m: 125.0, gestation_days: 30, lactation_days: 28, litter_size_min: 3, litter_size_max: 8, reproductive_age_days: 120, lifespan_days: 1460, speed_kmh: 2.5, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Sciurus_vulgaris", common_name: "Esquirol", count: 150, mass_kg: 0.3, kind: AgentKind::Herbivore, home_range_m: 75.0, gestation_days: 38, lactation_days: 60, litter_size_min: 2, litter_size_max: 5, reproductive_age_days: 365, lifespan_days: 2190, speed_kmh: 2.0, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Vulpes_vulpes", common_name: "Guineu", count: 80, mass_kg: 6.0, kind: AgentKind::Omnivore, home_range_m: 250.0, gestation_days: 53, lactation_days: 56, litter_size_min: 3, litter_size_max: 6, reproductive_age_days: 365, lifespan_days: 2920, speed_kmh: 3.0, activity_pattern: "nocturnal" },
    PopulationConfig { species_key: "Meles_meles", common_name: "Teixó", count: 60, mass_kg: 11.0, kind: AgentKind::Omnivore, home_range_m: 200.0, gestation_days: 60, lactation_days: 90, litter_size_min: 2, litter_size_max: 4, reproductive_age_days: 365, lifespan_days: 4380, speed_kmh: 2.0, activity_pattern: "nocturnal" },
    PopulationConfig { species_key: "Martes_martes", common_name: "Marta", count: 60, mass_kg: 1.5, kind: AgentKind::Carnivore, home_range_m: 200.0, gestation_days: 30, lactation_days: 60, litter_size_min: 2, litter_size_max: 4, reproductive_age_days: 365, lifespan_days: 3650, speed_kmh: 2.5, activity_pattern: "nocturnal" },
    PopulationConfig { species_key: "Felis_silvestris", common_name: "Gat fer", count: 20, mass_kg: 4.0, kind: AgentKind::Carnivore, home_range_m: 250.0, gestation_days: 65, lactation_days: 60, litter_size_min: 2, litter_size_max: 4, reproductive_age_days: 365, lifespan_days: 4380, speed_kmh: 3.0, activity_pattern: "nocturnal" },
    PopulationConfig { species_key: "Mustela_erminea", common_name: "Ermíni", count: 100, mass_kg: 0.15, kind: AgentKind::Carnivore, home_range_m: 75.0, gestation_days: 42, lactation_days: 42, litter_size_min: 4, litter_size_max: 8, reproductive_age_days: 365, lifespan_days: 2190, speed_kmh: 1.5, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Mustela_nivalis", common_name: "Mostela", count: 150, mass_kg: 0.08, kind: AgentKind::Carnivore, home_range_m: 75.0, gestation_days: 35, lactation_days: 35, litter_size_min: 4, litter_size_max: 8, reproductive_age_days: 120, lifespan_days: 1460, speed_kmh: 1.5, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Tetrao_urogallus", common_name: "Gall fer", count: 15, mass_kg: 4.0, kind: AgentKind::Herbivore, home_range_m: 125.0, gestation_days: 26, lactation_days: 35, litter_size_min: 6, litter_size_max: 12, reproductive_age_days: 365, lifespan_days: 2555, speed_kmh: 1.5, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Lagopus_muta", common_name: "Perdiu xerra", count: 30, mass_kg: 0.5, kind: AgentKind::Herbivore, home_range_m: 100.0, gestation_days: 23, lactation_days: 28, litter_size_min: 5, litter_size_max: 10, reproductive_age_days: 365, lifespan_days: 1460, speed_kmh: 1.5, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Corvus_corax", common_name: "Corb", count: 80, mass_kg: 1.0, kind: AgentKind::Omnivore, home_range_m: 250.0, gestation_days: 21, lactation_days: 45, litter_size_min: 3, litter_size_max: 7, reproductive_age_days: 365, lifespan_days: 7300, speed_kmh: 3.5, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Gypaetus_barbatus", common_name: "Trencalòs", count: 2, mass_kg: 5.5, kind: AgentKind::Omnivore, home_range_m: 500.0, gestation_days: 55, lactation_days: 120, litter_size_min: 1, litter_size_max: 2, reproductive_age_days: 1825, lifespan_days: 10950, speed_kmh: 5.0, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Aquila_chrysaetos", common_name: "Àguila reial", count: 2, mass_kg: 4.0, kind: AgentKind::Carnivore, home_range_m: 625.0, gestation_days: 45, lactation_days: 90, litter_size_min: 1, litter_size_max: 3, reproductive_age_days: 1460, lifespan_days: 9125, speed_kmh: 5.0, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Lutra_lutra", common_name: "Llúdriga", count: 5, mass_kg: 9.5, kind: AgentKind::Carnivore, home_range_m: 375.0, gestation_days: 62, lactation_days: 120, litter_size_min: 1, litter_size_max: 3, reproductive_age_days: 730, lifespan_days: 5475, speed_kmh: 2.5, activity_pattern: "crepuscular" },
    PopulationConfig { species_key: "Ovis_aries_musimon", common_name: "Mufló", count: 80, mass_kg: 37.5, kind: AgentKind::Herbivore, home_range_m: 300.0, gestation_days: 155, lactation_days: 120, litter_size_min: 1, litter_size_max: 2, reproductive_age_days: 730, lifespan_days: 7300, speed_kmh: 3.5, activity_pattern: "diurnal" },
    PopulationConfig { species_key: "Dama_dama", common_name: "Daina", count: 60, mass_kg: 57.5, kind: AgentKind::Herbivore, home_range_m: 300.0, gestation_days: 240, lactation_days: 150, litter_size_min: 1, litter_size_max: 1, reproductive_age_days: 730, lifespan_days: 7300, speed_kmh: 3.5, activity_pattern: "diurnal" },
];

pub struct Simulation {
    pub grid: TerrainGrid,
    pub env: Environment,
    pub pools: PoolManager,
    pub agents: Vec<Agent>,
    pub total_days: i32,
    pub log_every: i32,
    pub snapshot_every: i32,
    pub output_dir: PathBuf,
    pub data_dir: PathBuf,
    pub agent_id_counter: u32,
}

impl Simulation {
    pub fn new(
        width: u32,
        height: u32,
        resolution_m: u32,
        total_days: i32,
        output_dir: &str,
        data_dir: &str,
    ) -> Self {
        let grid = TerrainGrid::new(width, height, resolution_m);
        Simulation {
            grid,
            env: Environment::new(),
            pools: PoolManager::default(),
            agents: Vec::new(),
            total_days,
            log_every: 10,
            snapshot_every: 100,
            output_dir: PathBuf::from(output_dir),
            data_dir: PathBuf::from(data_dir),
            agent_id_counter: 0,
        }
    }

    pub fn initialize(&mut self) {
        let data_dir = &self.data_dir;
        let tsv_path = data_dir.join("terrain_cells.tsv");

        let diet_path = data_dir.join("dieta_proporciones.tsv");
        if diet_path.exists() {
            println!("  Loading diet data from TSV...");
            match load_diet_data(&diet_path) {
                Ok(_) => println!("  Diet data loaded: {}", if is_data_loaded() { "OK" } else { "failed" }),
                Err(e) => println!("  Warning: diet load error: {}", e),
            }
        }

        let trophic_path = data_dir.join("trophic_matrix.tsv");
        if trophic_path.exists() {
            println!("  Loading trophic matrix from TSV...");
            match load_trophic_data(&trophic_path) {
                Ok(_) => println!("  Trophic matrix loaded"),
                Err(e) => println!("  Warning: trophic matrix load error: {}", e),
            }
        }

        let energy_path = data_dir.join("energia_recursos.tsv");
        if energy_path.exists() {
            println!("  Loading energy density data from TSV...");
            if let Err(e) = load_energy_data(&energy_path) {
                println!("  Warning: energy data load error: {}", e);
            }
        }

        let activity_path = data_dir.join("costos_actividad.tsv");
        if activity_path.exists() {
            println!("  Loading activity cost data from TSV...");
            if let Err(e) = load_activity_costs(&activity_path) {
                println!("  Warning: activity cost load error: {}", e);
            }
        }

        if tsv_path.exists() {
            println!("  Loading terrain data from TSV...");
            io::load_terrain_from_tsv(&mut self.grid, &tsv_path).ok();
            println!("  Done: {} cells loaded", self.grid.width * self.grid.height);
        } else {
            println!("  No terrain TSV found, using flat defaults");
            self.assign_default_habitat();
        }

        self.grid.update_costs();

        let area_ha = (self.grid.width as f64 * self.grid.resolution_m as f64
            * self.grid.height as f64 * self.grid.resolution_m as f64)
            / 10000.0;
        let area_factor = area_ha / 1000.0;
        self.pools.fish.biomass_truita = 5.0 * area_factor;
        self.pools.fish.biomass_barb_roig = 2.0 * area_factor;
        self.pools.herps.biomass_reptiles = 0.5 * area_factor;
        self.pools.herps.biomass_amphibians = 0.8 * area_factor;
        self.pools.passerines.biomass = 3.0 * area_factor;
        self.pools.micromammals.biomass = 4.0 * area_factor;
        self.pools.bats.biomass = 0.3 * area_factor;

        let res = self.grid.resolution_m as f64;
        let mut rng = rand::thread_rng();
        for pop in DEFAULT_POPULATIONS {
            let scaled = scale_to_area(pop.count, area_ha, 10000.0);
            let candidates = find_spawn_cells(&self.grid, pop.species_key);

            for _ in 0..scaled {
                let (cx, cy) = if candidates.is_empty() {
                    (rng.gen_range(0..self.grid.width) as i32,
                     rng.gen_range(0..self.grid.height) as i32)
                } else {
                    let idx = rng.gen_range(0..candidates.len());
                    candidates[idx]
                };

                let pos_x = cx as f64 * res + res / 2.0;
                let pos_y = cy as f64 * res + res / 2.0;

                let agent = create_agent(&mut rng, self.agent_id_counter, pop, pos_x, pos_y, cx, cy, res);
                self.agent_id_counter += 1;
                self.agents.push(agent);
            }
        }

        println!(
            "  Initialized {} agents across {} species",
            self.agents.len(),
            DEFAULT_POPULATIONS.len()
        );
    }

    fn assign_default_habitat(&mut self) {
        for y in 0..self.grid.height {
            for x in 0..self.grid.width {
                let cell = self.grid.cell_mut(x, y);
                cell.piso_bioclimatico = piso::MONTANO;
                cell.habitat_type = habitat::PASTIZAL;
                cell.P1_max = 2.0;
                cell.P2_max = 1.5;
                cell.P3_max = 5.0;
                cell.biomass_P1 = 1.0;
                cell.biomass_P2 = 0.5;
                cell.biomass_P3 = 1.5;
                cell.biomass_I1 = 0.1;
                cell.biomass_I2 = 0.2;
                cell.biomass_I3 = 0.05;
            }
        }
    }

    pub fn run(&mut self) {
        std::fs::create_dir_all(&self.output_dir).ok();

        let log_path = self.output_dir.join("simulation_log.csv");
        let species_log_path = self.output_dir.join("species_population.csv");

        let mut log_file = std::fs::File::create(&log_path).ok();
        if let Some(ref mut f) = log_file {
            use std::io::Write;
            writeln!(f, "day,n_alive,n_dead,n_total,total_plant_kg,total_invert_kg,total_carcass_kg,avg_energy,season,temp_avg").ok();
        }

        let mut species_file = std::fs::File::create(&species_log_path).ok();
        if let Some(ref mut f) = species_file {
            use std::io::Write;
            let headers: Vec<&str> = DEFAULT_POPULATIONS.iter().map(|p| p.species_key).collect();
            writeln!(f, "day,{}", headers.join(",")).ok();
        }

        let total_ticks = self.total_days as i64 * TICKS_PER_DAY as i64;

        for tick in 0..total_ticks {
            let tick_in_day = (tick % TICKS_PER_DAY as i64) as i32;
            self.tick(tick, tick_in_day);

            if tick_in_day == TICKS_PER_DAY - 1 {
                let day = (tick / TICKS_PER_DAY as i64) as i32;
                if day % self.log_every == 0 {
                    self.log_state(day, &log_path, &species_log_path);
                }
                if day % self.snapshot_every == 0 {
                    self.snapshot(day);
                }
            }
        }
    }

    fn tick(&mut self, tick: i64, tick_in_day: i32) {
        let day = (tick / TICKS_PER_DAY as i64) as i32;
        let is_midnight = tick_in_day == 0;

        // --- Daily operations (at tick 0 of each day) ---
        if is_midnight {
            self.env.step();
            let season = self.env.season();
            let growth_mod = seasonal_growth_modifier(season.name());
            let is_winter = season == Season::Winter;

            self.grid.step_snow(day);
            self.grid.step_temperature(day);
            self.pools.step(&mut self.grid, growth_mod);
            self.grid.decay_carcasses();

            // Set hibernation for marmots in winter
            for agent in &mut self.agents {
                if !agent.is_alive() {
                    continue;
                }
                agent.state.is_hibernating = is_winter
                    && (agent.species_key == "Marmota_marmota");
                agent.state.is_hyperphagia = season == Season::Autumn;
            }

            // Advance daily counters
            for agent in &mut self.agents {
                if agent.is_alive() {
                    agent.state.calories_consumed_today = 0.0;
                    agent.state.calories_spent_today = 0.0;
                    agent.state.days_since_reproduction = agent.state.days_since_reproduction.saturating_add(1);
                    if agent.state.is_lactating {
                        agent.state.lactation_timer += 1;
                        if agent.state.lactation_timer > agent.lactation_ticks_total {
                            agent.state.is_lactating = false;
                            agent.state.lactation_timer = 0;
                        }
                    }
                }
            }
        }

        // --- Agent ticks (parallel, scoped to release borrows before grid mutation) ---
        let season = self.env.season();
        let is_autumn = season == Season::Autumn;
        let is_winter = season == Season::Winter;
        let tick_data: Vec<(i32, i32, TickOutcome)> = {
            let grid = &self.grid;
            self.agents
                .par_iter_mut()
                .map(|a| {
                    let outcome = a.tick(grid, is_autumn, is_winter);
                    (a.state.cell_x, a.state.cell_y, outcome)
                })
                .collect()
        };

        for (cx, cy, outcome) in &tick_data {
            if !self.grid.in_bounds(*cx, *cy) {
                continue;
            }
            let cell = self.grid.cell_mut(*cx as u32, *cy as u32);
            cell.biomass_P1 = (cell.biomass_P1 - outcome.consume_plant_kg * 0.4).max(0.0);
            cell.biomass_P2 = (cell.biomass_P2 - outcome.consume_plant_kg * 0.2).max(0.0);
            cell.biomass_P3 = (cell.biomass_P3 - outcome.consume_plant_kg * 0.4).max(0.0);
            cell.biomass_I1 = (cell.biomass_I1 - outcome.consume_invert_kg * 0.5).max(0.0);
            cell.biomass_I2 = (cell.biomass_I2 - outcome.consume_invert_kg * 0.3).max(0.0);
            cell.biomass_I3 = (cell.biomass_I3 - outcome.consume_invert_kg * 0.2).max(0.0);
            cell.carcass_biomass = (cell.carcass_biomass - outcome.consume_carcass_kg).max(0.0);
        }

        // --- Predation (every tick) ---
        self.predation_tick();

        // --- Reroute agents periodically ---
        if tick_in_day % REROUTE_EVERY_TICKS == 0 {
            self.reroute_agents(tick_in_day);
        }

        // --- Daily end-of-day operations (at tick 0 of each day) ---
        if is_midnight {
            self.pool_consumption_step();
            self.reproduce_step();
            self.remove_dead();
            self.grid.update_costs();
        }
    }

    fn reroute_agents(&mut self, tick_in_day: i32) {
        let grid = &self.grid;
        for agent in &mut self.agents {
            if agent.is_alive() {
                agent.reroute(grid, tick_in_day);
            }
        }
    }

    fn predation_tick(&mut self) {
        let n = self.agents.len();
        let mut to_kill = vec![false; n];

        for i in 0..n {
            if !self.agents[i].is_alive() || to_kill[i] {
                continue;
            }
            // Only predators in hunting FSM states can kill
            let state = self.agents[i].state.fsm_state;
            if state != AgentFSMState::HuntChase && state != AgentFSMState::HuntStalk {
                continue;
            }

            let all_prey = get_prey(&self.agents[i].species_key);
            let prey_list: Vec<&String> = all_prey.iter()
                .filter(|p| !p.starts_with("V-"))
                .collect();
            if prey_list.is_empty() {
                continue;
            }

            let px = self.agents[i].state.cell_x;
            let py = self.agents[i].state.cell_y;

            for j in 0..n {
                if i == j || !self.agents[j].is_alive() || to_kill[j] {
                    continue;
                }
                if self.agents[j].state.cell_x != px || self.agents[j].state.cell_y != py {
                    continue;
                }
                if prey_list.iter().any(|p| ***p == self.agents[j].species_key) {
                    let prey_mass = self.agents[j].mass_kg;
                    let energy_gain = prey_mass * get_energy_density_meat() * 0.8;
                    self.agents[i].state.energy_kcal += energy_gain;
                    self.agents[i].state.calories_consumed_today += energy_gain;
                    to_kill[j] = true;
                    break;
                }
            }
        }

        for (j, &kill) in to_kill.iter().enumerate() {
            if kill {
                let cell_idx = self.grid.pos_to_idx(self.agents[j].state.cell_x, self.agents[j].state.cell_y);
                let carcass_add = self.agents[j].mass_kg * 0.7;
                self.grid.cell_at_idx_mut(cell_idx).carcass_biomass += carcass_add;
                self.agents[j].state.alive = false;
                self.agents[j].state.fsm_state = AgentFSMState::Dead;
                self.agents[j].state.death_cause = Some(DeathCause::Predation);
            }
        }
    }

    fn pool_consumption_step(&mut self) {
        for agent in &mut self.agents {
            if !agent.is_alive() {
                continue;
            }
            let diet = get_diet(&agent.species_key).unwrap_or_default();
            let max_intake = agent.mass_kg * 0.10;
            let mut total_meat_kg = 0.0;

            let trophic_links = get_all_trophic_links();
            let mut pool_fish = 0.0;
            let mut pool_micromammals = 0.0;
            let mut pool_passerines = 0.0;
            let mut pool_herps = 0.0;
            let mut pool_bats = 0.0;

            for link in trophic_links {
                if link.consumer != agent.species_key {
                    continue;
                }
                match link.resource.as_str() {
                    "Salmo_trutta" | "Phoxinus_spp" => pool_fish += 0.3,
                    "V-MicromamífersPetits" => pool_micromammals += 0.3,
                    "V-Passeriformes" => pool_passerines += 0.3,
                    "V-RapinyairesNocturnesGrans" | "V-RapinyairesNocturnesPetites" => pool_passerines += 0.2,
                    "V-Ratpenats" => pool_bats += 0.2,
                    "V-InsectívorsMitjans" | "Calotriton_asper" | "Rana_temporaria" | "Bufo_bufo" | "Salamandra_salamandra" | "Podarcis_muralis" | "Zootoca_vivipara" | "Iberolacerta_aurelioi" => pool_herps += 0.3,
                    _ => {}
                }
            }

            if pool_fish == 0.0 && pool_micromammals == 0.0 && pool_passerines == 0.0
                && pool_herps == 0.0 && pool_bats == 0.0
            {
                if diet.fish_proportion > 0.0 {
                    let desired = max_intake * diet.fish_proportion;
                    let taken = self.pools.fish.consume(desired);
                    total_meat_kg += taken;
                }
                if diet.vertebrate_proportion > 0.0 {
                    let desired = max_intake * diet.vertebrate_proportion * 0.33;
                    total_meat_kg += self.pools.micromammals.consume(desired);
                    let desired = max_intake * diet.vertebrate_proportion * 0.33;
                    total_meat_kg += self.pools.passerines.consume(desired);
                    let desired = max_intake * diet.vertebrate_proportion * 0.34;
                    total_meat_kg += self.pools.herps.consume(desired);
                }
            } else {
                let total_weight = pool_fish + pool_micromammals + pool_passerines + pool_herps + pool_bats;
                if total_weight > 0.0 {
                    if pool_fish > 0.0 {
                        let share = pool_fish / total_weight;
                        total_meat_kg += self.pools.fish.consume(max_intake * share);
                    }
                    if pool_micromammals > 0.0 {
                        let share = pool_micromammals / total_weight;
                        total_meat_kg += self.pools.micromammals.consume(max_intake * share);
                    }
                    if pool_passerines > 0.0 {
                        let share = pool_passerines / total_weight;
                        total_meat_kg += self.pools.passerines.consume(max_intake * share);
                    }
                    if pool_herps > 0.0 {
                        let share = pool_herps / total_weight;
                        total_meat_kg += self.pools.herps.consume(max_intake * share);
                    }
                    if pool_bats > 0.0 {
                        let share = pool_bats / total_weight;
                        total_meat_kg += self.pools.bats.consume(max_intake * share);
                    }
                }
            }

            if total_meat_kg > 0.0 {
                let energy_gain = total_meat_kg * get_energy_density_meat() * 0.8;
                agent.state.calories_consumed_today += energy_gain;
                agent.state.energy_kcal += energy_gain;
            }
        }
    }

    fn reproduce_step(&mut self) {
        let season = self.env.season();
        if season != Season::Spring && season != Season::Summer {
            return;
        }

        let mut new_agents = Vec::new();
        let mut rng = rand::thread_rng();
        let res = self.grid.resolution_m as f64;

        // Count alive agents per species for density-dependent reproduction
        let mut species_counts: std::collections::HashMap<&str, u32> = std::collections::HashMap::new();
        for a in &self.agents {
            if a.is_alive() {
                *species_counts.entry(&a.species_key).or_insert(0) += 1;
            }
        }
        // Build reference population lookup
        let ref_counts: std::collections::HashMap<&str, u32> = DEFAULT_POPULATIONS.iter()
            .map(|p| {
                let area_ha = (self.grid.width as f64 * self.grid.resolution_m as f64
                    * self.grid.height as f64 * self.grid.resolution_m as f64) / 10000.0;
                (p.species_key, scale_to_area(p.count, area_ha, 10000.0))
            })
            .collect();

        let n = self.agents.len();
        let mut start_pregnancy = vec![false; n];
        let mut give_birth = Vec::new();

        for i in 0..n {
            if !self.agents[i].is_alive() {
                continue;
            }

            if self.agents[i].state.is_pregnant
                && self.agents[i].state.gestation_ticks >= self.agents[i].gestation_ticks_total
            {
                give_birth.push(i);
            }

            // Density factor: current / reference, capped at 0..2
            let current = *species_counts.get(self.agents[i].species_key.as_str()).unwrap_or(&0) as f64;
            let ref_count = *ref_counts.get(self.agents[i].species_key.as_str()).unwrap_or(&1) as f64;
            let density_factor = (current / ref_count).min(2.0);

            if self.agents[i].should_reproduce(density_factor) {
                start_pregnancy[i] = true;
            }
        }

        for &i in &give_birth {
            let agent = &self.agents[i];
            let n_births = rng.gen_range(agent.litter_size_min..=agent.litter_size_max);
            for _ in 0..n_births {
                let child_cx = agent.state.cell_x + rng.gen_range(-2..=2);
                let child_cy = agent.state.cell_y + rng.gen_range(-2..=2);
                if !self.grid.in_bounds(child_cx, child_cy) {
                    continue;
                }
                let aid = self.agent_id_counter;
                self.agent_id_counter += 1;
                let mass = agent.mass_kg * rng.gen_range(0.5..0.8);
                let child_gender = if rng.gen::<bool>() { Gender::Male } else { Gender::Female };
                let child_boldness = rng.gen::<f64>();
                let child_pos_x = child_cx as f64 * res + res / 2.0;
                let child_pos_y = child_cy as f64 * res + res / 2.0;

                let child = Agent {
                    agent_id: aid,
                    species_key: agent.species_key.clone(),
                    common_name: agent.common_name.clone(),
                    mass_kg: mass,
                    adult_mass_kg: agent.adult_mass_kg,
                    kind: agent.kind,
                    state: AgentState::new_continuous(child_pos_x, child_pos_y, child_cx, child_cy, mass, child_gender),
                    speed_ms: agent.speed_ms,
                    home_range_m: agent.home_range_m,
                    gestation_ticks_total: agent.gestation_ticks_total,
                    lactation_ticks_total: agent.lactation_ticks_total,
                    litter_size_min: agent.litter_size_min,
                    litter_size_max: agent.litter_size_max,
                    reproductive_age_ticks: agent.reproductive_age_ticks,
                    lifespan_ticks: agent.lifespan_ticks,
                    boldness: child_boldness,
                    activity_pattern: agent.activity_pattern,
                };
                new_agents.push(child);
            }
            self.agents[i].state.is_pregnant = false;
            self.agents[i].state.is_lactating = true;
            self.agents[i].state.lactation_timer = 0;
            self.agents[i].state.gestation_ticks = 0;
            self.agents[i].state.days_since_reproduction = 0;
        }

        for (i, &start) in start_pregnancy.iter().enumerate() {
            if start {
                self.agents[i].state.is_pregnant = true;
                self.agents[i].state.gestation_ticks = 0;
            }
        }

        self.agents.extend(new_agents);
    }

    fn remove_dead(&mut self) {
        self.agents.retain(|a| a.is_alive());
    }

    fn log_state(&self, day: i32, log_path: &Path, species_log_path: &Path) {
        let n_alive = self.agents.iter().filter(|a| a.is_alive()).count();
        let n_dead = self.agents.iter().filter(|a| !a.is_alive()).count();
        let total_plant = self.grid.total_plant_biomass();
        let total_invert = self.grid.total_invert_biomass();
        let total_carcass = self.grid.total_carcass_biomass();
        let avg_energy = self
            .agents
            .iter()
            .filter(|a| a.is_alive())
            .map(|a| a.state.energy_kcal)
            .sum::<f64>()
            / n_alive.max(1) as f64;
        let season = self.env.season().name();
        let avg_temp: f64 = self.grid.cells().iter().map(|c| c.temperature_c).sum::<f64>()
            / self.grid.cells().len().max(1) as f64;

        log_line(
            day,
            n_alive as u32,
            n_dead as u32,
            (n_alive + n_dead) as u32,
            total_plant,
            total_invert,
            total_carcass,
            avg_energy,
            season,
            avg_temp,
            log_path,
        );

        let species_counts: Vec<u32> = DEFAULT_POPULATIONS
            .iter()
            .map(|p| {
                self.agents
                    .iter()
                    .filter(|a| a.is_alive() && a.species_key == p.species_key)
                    .count() as u32
            })
            .collect();

        log_species_line(day, &species_counts, species_log_path);

        print!(
            "Day {}: alive={} dead={} plant={:.0}kg invert={:.0}kg carcass={:.1}kg energy_avg={:.0} {} {:.1}C",
            day, n_alive, n_dead, total_plant, total_invert, total_carcass, avg_energy, season, avg_temp
        );
        let predator_count = self.agents.iter().filter(|a| a.is_alive() && a.kind == AgentKind::Carnivore).count();
        if predator_count > 0 {
            print!(" pred={}", predator_count);
        }
        println!();
    }

    fn snapshot(&self, day: i32) {
        let pools = self.pools.total_biomass_kg();
        let avg_temp: f64 = self.grid.cells().iter().map(|c| c.temperature_c).sum::<f64>()
            / self.grid.cells().len().max(1) as f64;
        let snow_cells = self.grid.cells().iter().filter(|c| c.snow_cover > 0.5).count();

        let snap = serde_json::json!({
            "day": day,
            "season": self.env.season().name(),
            "avg_temp_c": (avg_temp * 10.0).round() / 10.0,
            "snow_cells": snow_cells,
            "agents": self.agents.iter().filter(|a| a.is_alive()).map(|a| {
                serde_json::json!({
                    "id": a.agent_id,
                    "species": a.species_key,
                    "kind": a.kind.name(),
                    "gender": if a.state.gender == Gender::Male { "M" } else { "F" },
                    "mass_kg": (a.state.mass_kg * 10.0).round() / 10.0,
                    "adult_mass_kg": (a.adult_mass_kg * 10.0).round() / 10.0,
                    "boldness": (a.boldness * 100.0).round() / 100.0,
                    "pos_x": (a.state.pos_x * 10.0).round() / 10.0,
                    "pos_y": (a.state.pos_y * 10.0).round() / 10.0,
                    "cell_x": a.state.cell_x,
                    "cell_y": a.state.cell_y,
                    "fsm_state": a.state.fsm_state.as_str(),
                    "alive": a.state.alive,
                    "energy_kcal": (a.state.energy_kcal * 10.0).round() / 10.0,
                    "age_days": (a.state.age_ticks as f64 / TICKS_F * 10.0).round() / 10.0,
                    "pregnant": a.state.is_pregnant,
                    "lactating": a.state.is_lactating,
                })
            }).collect::<Vec<_>>(),
            "pools": {
                "plants": (self.grid.total_plant_biomass() * 10.0).round() / 10.0,
                "inverts": (self.grid.total_invert_biomass() * 10.0).round() / 10.0,
                "carcass": (self.grid.total_carcass_biomass() * 10.0).round() / 10.0,
                "fish": (pools.2 * 10.0).round() / 10.0,
                "herps": (pools.3 * 10.0).round() / 10.0,
                "passerines": (pools.4 * 10.0).round() / 10.0,
                "micromammals": (pools.5 * 10.0).round() / 10.0,
                "bats": (pools.6 * 10.0).round() / 10.0,
            },
        });
        let path = self.output_dir.join(format!("snap_{:04}.json", day));
        std::fs::write(&path, serde_json::to_string_pretty(&snap).unwrap()).ok();
    }

    pub fn get_stats(&self) -> serde_json::Value {
        let n_alive = self.agents.iter().filter(|a| a.is_alive()).count();
        let mut species_counts = serde_json::Map::new();
        for a in &self.agents {
            if a.is_alive() {
                let count = species_counts
                    .entry(a.species_key.clone())
                    .or_insert(serde_json::Value::Number(0.into()));
                if let Some(n) = count.as_u64() {
                    *count = serde_json::Value::Number((n + 1).into());
                }
            }
        }
        serde_json::json!({
            "day": self.env.current_day,
            "agents_alive": n_alive,
            "agents_total": self.agents.len(),
            "species_counts": species_counts,
            "plant_biomass_kg": (self.grid.total_plant_biomass() * 10.0).round() / 10.0,
            "invert_biomass_kg": (self.grid.total_invert_biomass() * 10.0).round() / 10.0,
            "carcass_biomass_kg": (self.grid.total_carcass_biomass() * 10.0).round() / 10.0,
        })
    }
}

fn scale_to_area(count: u32, area_ha: f64, reference_ha: f64) -> u32 {
    let scaled = (count as f64) * area_ha / reference_ha;
    let min = if area_ha < 200.0 {
        1
    } else if area_ha < 500.0 {
        2
    } else if area_ha < 1500.0 {
        3
    } else {
        1
    };
    (scaled.ceil().max(min as f64)).min(count as f64) as u32
}

fn parse_activity_pattern(s: &str) -> ActivityPattern {
    match s {
        "nocturnal" => ActivityPattern::Nocturnal,
        "crepuscular" => ActivityPattern::Crepuscular,
        "cathemeral" => ActivityPattern::Cathemeral,
        _ => ActivityPattern::Diurnal,
    }
}

fn create_agent(
    rng: &mut impl rand::Rng,
    id: u32,
    pop: &PopulationConfig,
    pos_x: f64,
    pos_y: f64,
    cell_x: i32,
    cell_y: i32,
    _resolution_m: f64,
) -> Agent {
    let weight_offset = 0.8 + rng.gen::<f64>() * 0.4;
    let mass = pop.mass_kg * weight_offset;
    let gender = if rng.gen::<bool>() { Gender::Male } else { Gender::Female };
    let max_start_age_ticks = (pop.lifespan_days as f64 * 0.25) as i64 * TICKS_PER_DAY as i64;
    let start_age_ticks = rng.gen_range(0..=max_start_age_ticks.max(0));
    let boldness = rng.gen::<f64>();

    let mut agent = Agent {
        agent_id: id,
        species_key: pop.species_key.to_string(),
        common_name: pop.common_name.to_string(),
        mass_kg: mass,
        adult_mass_kg: pop.mass_kg,
        kind: pop.kind,
        state: AgentState::new_continuous(pos_x, pos_y, cell_x, cell_y, mass, gender),
        speed_ms: pop.speed_kmh / 3.6,
        home_range_m: pop.home_range_m,
        gestation_ticks_total: pop.gestation_days * TICKS_PER_DAY,
        lactation_ticks_total: pop.lactation_days * TICKS_PER_DAY,
        litter_size_min: pop.litter_size_min,
        litter_size_max: pop.litter_size_max,
        reproductive_age_ticks: pop.reproductive_age_days as i64 * TICKS_PER_DAY as i64,
        lifespan_ticks: pop.lifespan_days as i64 * TICKS_PER_DAY as i64,
        boldness,
        activity_pattern: parse_activity_pattern(pop.activity_pattern),
    };
    agent.state.age_ticks = start_age_ticks;
    agent
}

fn find_spawn_cells(grid: &TerrainGrid, species_key: &str) -> Vec<(i32, i32)> {
    let prefs = SPECIES_HABITAT.iter().find(|(k, _)| *k == species_key).map(|(_, p)| p);
    let prefs = match prefs {
        Some(p) => p,
        None => return Vec::new(),
    };

    let mut cells = Vec::new();
    for c in grid.cells() {
        if c.is_water {
            continue;
        }
        let habitat_ok = prefs.habitats.is_empty() || prefs.habitats.contains(&c.habitat_type);
        let piso_ok = prefs.pisos.is_empty() || prefs.pisos.contains(&c.piso_bioclimatico);
        if habitat_ok && piso_ok {
            cells.push((c.x as i32, c.y as i32));
        }
    }
    cells
}

fn log_line(
    day: i32,
    n_alive: u32,
    n_dead: u32,
    n_total: u32,
    total_plant: f64,
    total_invert: f64,
    total_carcass: f64,
    avg_energy: f64,
    season: &str,
    avg_temp: f64,
    path: &Path,
) {
    use std::io::Write;
    if let Ok(mut f) = std::fs::OpenOptions::new().append(true).create(true).open(path) {
        writeln!(
            f,
            "{},{},{},{},{:.1},{:.1},{:.1},{:.1},{},{:.1}",
            day, n_alive, n_dead, n_total, total_plant, total_invert, total_carcass, avg_energy, season, avg_temp
        )
        .ok();
    }
}

fn log_species_line(day: i32, counts: &[u32], path: &Path) {
    use std::io::Write;
    if let Ok(mut f) = std::fs::OpenOptions::new().append(true).create(true).open(path) {
        let counts_str: Vec<String> = counts.iter().map(|c| c.to_string()).collect();
        writeln!(f, "{},{}", day, counts_str.join(",")).ok();
    }
}
