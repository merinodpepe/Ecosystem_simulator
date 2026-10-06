use super::grid::TerrainGrid;

#[allow(non_snake_case)]
pub struct PlantPool {
    pub P1_growth_rate: f64,
    pub P2_growth_rate: f64,
    pub P3_growth_rate: f64,
    pub P1_max_per_cell: f64,
    pub P2_max_per_cell: f64,
    pub P3_max_per_cell: f64,
}

impl Default for PlantPool {
    fn default() -> Self {
        PlantPool {
            P1_growth_rate: 0.02,
            P2_growth_rate: 0.015,
            P3_growth_rate: 0.03,
            P1_max_per_cell: 2.0,
            P2_max_per_cell: 1.5,
            P3_max_per_cell: 5.0,
        }
    }
}

impl PlantPool {
    pub fn step(&mut self, grid: &mut TerrainGrid, growth_mod: f64) {
        grid.step_plants_logistic(growth_mod);
    }

    pub fn get_totals(&self, grid: &TerrainGrid) -> (f64, f64, f64) {
        let mut p1 = 0.0;
        let mut p2 = 0.0;
        let mut p3 = 0.0;
        for c in grid.cells() {
            p1 += c.biomass_P1;
            p2 += c.biomass_P2;
            p3 += c.biomass_P3;
        }
        (p1, p2, p3)
    }
}

#[allow(non_snake_case)]
pub struct InvertebratePool {
    pub I1_growth_rate: f64,
    pub I2_growth_rate: f64,
    pub I3_growth_rate: f64,
    pub I1_max_per_cell: f64,
    pub I2_max_per_cell: f64,
    pub I3_max_per_cell: f64,
}

impl Default for InvertebratePool {
    fn default() -> Self {
        InvertebratePool {
            I1_growth_rate: 0.01,
            I2_growth_rate: 0.015,
            I3_growth_rate: 0.008,
            I1_max_per_cell: 0.5,
            I2_max_per_cell: 0.8,
            I3_max_per_cell: 0.3,
        }
    }
}

impl InvertebratePool {
    pub fn step(&mut self, grid: &mut TerrainGrid, growth_mod: f64) {
        grid.step_inverts(growth_mod);
    }

    pub fn get_totals(&self, grid: &TerrainGrid) -> (f64, f64, f64) {
        let mut i1 = 0.0;
        let mut i2 = 0.0;
        let mut i3 = 0.0;
        for c in grid.cells() {
            i1 += c.biomass_I1;
            i2 += c.biomass_I2;
            i3 += c.biomass_I3;
        }
        (i1, i2, i3)
    }
}

pub struct FishPool {
    pub biomass_truita: f64,
    pub biomass_barb_roig: f64,
    pub growth_rate: f64,
    pub carrying_capacity_per_km: f64,
}

impl Default for FishPool {
    fn default() -> Self {
        FishPool {
            biomass_truita: 0.0,
            biomass_barb_roig: 0.0,
            growth_rate: 0.01,
            carrying_capacity_per_km: 200.0,
        }
    }
}

impl FishPool {
    pub fn step(&mut self, grid: &TerrainGrid) {
        let water_cells = grid.count_water_cells() as f64;
        let river_km = water_cells * grid.resolution_m as f64 / 1000.0;
        let max_fish = river_km * self.carrying_capacity_per_km;
        self.biomass_truita += self.growth_rate * self.biomass_truita;
        self.biomass_truita = self.biomass_truita.min(max_fish * 0.7).max(0.0);
        self.biomass_barb_roig += self.growth_rate * 1.5 * self.biomass_barb_roig;
        self.biomass_barb_roig = self.biomass_barb_roig.min(max_fish * 0.3).max(0.0);
    }

    pub fn consume(&mut self, max_kg: f64) -> f64 {
        let available = self.biomass_truita + self.biomass_barb_roig;
        let take = available.min(max_kg);
        if available > 0.0 {
            let truita_share = self.biomass_truita / available;
            self.biomass_truita -= take * truita_share;
            self.biomass_barb_roig -= take * (1.0 - truita_share);
        }
        take
    }

    pub fn total_biomass(&self) -> f64 {
        self.biomass_truita + self.biomass_barb_roig
    }
}

pub struct HerpPool {
    pub biomass_reptiles: f64,
    pub biomass_amphibians: f64,
    pub growth_rate: f64,
}

impl Default for HerpPool {
    fn default() -> Self {
        HerpPool {
            biomass_reptiles: 0.0,
            biomass_amphibians: 0.0,
            growth_rate: 0.008,
        }
    }
}

impl HerpPool {
    pub fn step(&mut self, growth_mod: f64, grid: &TerrainGrid) {
        let suitable_cells = grid.cells().iter().filter(|c| {
            !c.is_water && c.snow_cover <= 0.5
                && (c.habitat_type == super::grid::habitat::HUMEDAL
                    || c.habitat_type == super::grid::habitat::RIBERA
                    || c.habitat_type == super::grid::habitat::BOSQUE_CON
                    || c.habitat_type == super::grid::habitat::BOSQUE_CAD)
        }).count() as f64;
        let max_reptiles = suitable_cells * 0.15;
        let max_amphibians = suitable_cells * 0.25;
        self.biomass_reptiles += self.growth_rate * growth_mod * self.biomass_reptiles;
        self.biomass_amphibians += self.growth_rate * 1.2 * growth_mod * self.biomass_amphibians;
        self.biomass_reptiles = self.biomass_reptiles.clamp(0.0, max_reptiles);
        self.biomass_amphibians = self.biomass_amphibians.clamp(0.0, max_amphibians);
    }

    pub fn consume(&mut self, max_kg: f64) -> f64 {
        let available = self.biomass_reptiles + self.biomass_amphibians;
        let take = available.min(max_kg);
        if available > 0.0 {
            let rep_share = self.biomass_reptiles / available;
            self.biomass_reptiles -= take * rep_share;
            self.biomass_amphibians -= take * (1.0 - rep_share);
        }
        take
    }

    pub fn total_biomass(&self) -> f64 {
        self.biomass_reptiles + self.biomass_amphibians
    }
}

pub struct PasserinePool {
    pub biomass: f64,
    pub growth_rate: f64,
}

impl Default for PasserinePool {
    fn default() -> Self {
        PasserinePool {
            biomass: 0.0,
            growth_rate: 0.01,
        }
    }
}

impl PasserinePool {
    pub fn step(&mut self, growth_mod: f64, grid: &TerrainGrid) {
        let suitable_cells = grid.cells().iter().filter(|c| {
            !c.is_water && c.snow_cover <= 0.5
                && (c.habitat_type == super::grid::habitat::BOSQUE_CON
                    || c.habitat_type == super::grid::habitat::BOSQUE_CAD
                    || c.habitat_type == super::grid::habitat::MATORRAL)
        }).count() as f64;
        let max_biomass = suitable_cells * 0.4;
        self.biomass += self.growth_rate * growth_mod * self.biomass;
        self.biomass = self.biomass.clamp(0.0, max_biomass);
    }

    pub fn consume(&mut self, max_kg: f64) -> f64 {
        let take = self.biomass.min(max_kg);
        self.biomass -= take;
        take
    }
}

pub struct MicromammalPool {
    pub biomass: f64,
    pub growth_rate: f64,
}

impl Default for MicromammalPool {
    fn default() -> Self {
        MicromammalPool {
            biomass: 0.0,
            growth_rate: 0.02,
        }
    }
}

impl MicromammalPool {
    pub fn step(&mut self, growth_mod: f64, grid: &TerrainGrid) {
        let suitable_cells = grid.cells().iter().filter(|c| {
            !c.is_water && c.snow_cover <= 0.5
                && (c.habitat_type == super::grid::habitat::BOSQUE_CON
                    || c.habitat_type == super::grid::habitat::BOSQUE_CAD
                    || c.habitat_type == super::grid::habitat::MATORRAL
                    || c.habitat_type == super::grid::habitat::PASTIZAL)
        }).count() as f64;
        let max_biomass = suitable_cells * 0.5;
        self.biomass += self.growth_rate * growth_mod * self.biomass;
        self.biomass = self.biomass.clamp(0.0, max_biomass);
    }

    pub fn consume(&mut self, max_kg: f64) -> f64 {
        let take = self.biomass.min(max_kg);
        self.biomass -= take;
        take
    }
}

pub struct BatPool {
    pub biomass: f64,
    pub growth_rate: f64,
}

impl Default for BatPool {
    fn default() -> Self {
        BatPool {
            biomass: 0.0,
            growth_rate: 0.005,
        }
    }
}

impl BatPool {
    pub fn step(&mut self, growth_mod: f64, grid: &TerrainGrid) {
        let suitable_cells = grid.cells().iter().filter(|c| {
            !c.is_water && c.snow_cover <= 0.5
                && (c.habitat_type == super::grid::habitat::BOSQUE_CON
                    || c.habitat_type == super::grid::habitat::BOSQUE_CAD
                    || c.habitat_type == super::grid::habitat::ROCA)
        }).count() as f64;
        let max_biomass = suitable_cells * 0.08;
        self.biomass += self.growth_rate * growth_mod * self.biomass;
        self.biomass = self.biomass.clamp(0.0, max_biomass);
    }

    pub fn consume(&mut self, max_kg: f64) -> f64 {
        let take = self.biomass.min(max_kg);
        self.biomass -= take;
        take
    }
}

pub struct PoolManager {
    pub plants: PlantPool,
    pub invertebrates: InvertebratePool,
    pub fish: FishPool,
    pub herps: HerpPool,
    pub passerines: PasserinePool,
    pub micromammals: MicromammalPool,
    pub bats: BatPool,
}

impl Default for PoolManager {
    fn default() -> Self {
        PoolManager {
            plants: PlantPool::default(),
            invertebrates: InvertebratePool::default(),
            fish: FishPool::default(),
            herps: HerpPool::default(),
            passerines: PasserinePool::default(),
            micromammals: MicromammalPool::default(),
            bats: BatPool::default(),
        }
    }
}

impl PoolManager {
    pub fn step(&mut self, grid: &mut TerrainGrid, growth_mod: f64) {
        self.plants.step(grid, growth_mod);
        self.invertebrates.step(grid, growth_mod);
        self.fish.step(grid);
        self.herps.step(growth_mod, grid);
        self.passerines.step(growth_mod, grid);
        self.micromammals.step(growth_mod, grid);
        self.bats.step(growth_mod, grid);
    }

    pub fn total_biomass_kg(&self) -> (f64, f64, f64, f64, f64, f64, f64) {
        (
            0.0,
            0.0,
            self.fish.total_biomass(),
            self.herps.total_biomass(),
            self.passerines.biomass,
            self.micromammals.biomass,
            self.bats.biomass,
        )
    }
}
