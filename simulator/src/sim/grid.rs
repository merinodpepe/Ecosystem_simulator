pub mod habitat {
    pub const BOSQUE_CON: u8 = 1;
    pub const BOSQUE_CAD: u8 = 2;
    pub const MATORRAL: u8 = 3;
    pub const PASTIZAL: u8 = 4;
    pub const HUMEDAL: u8 = 5;
    pub const ROCA: u8 = 6;
    pub const AGUA: u8 = 7;
    pub const RIBERA: u8 = 8;
    pub const NIEVE: u8 = 9;
    pub const ANTROPICO: u8 = 10;
}

pub mod piso {
    pub const MONTANO: u8 = 1;
    pub const SUBALPINO: u8 = 2;
    pub const ALPINO: u8 = 3;
    pub const NIVAL: u8 = 4;
}

use super::environment::default_temp_fn;

#[derive(Clone)]
#[allow(non_snake_case)]
pub struct Cell {
    pub x: u32,
    pub y: u32,
    pub elevation_m: f64,
    pub slope_deg: f64,
    pub aspect_deg: f64,
    pub tri: f64,
    pub piso_bioclimatico: u8,
    pub habitat_type: u8,
    pub snow_cover: f64,
    pub is_water: bool,
    pub is_riparian: bool,
    pub cost_a_star: f64,
    pub biomass_P1: f64,
    pub biomass_P2: f64,
    pub biomass_P3: f64,
    pub biomass_I1: f64,
    pub biomass_I2: f64,
    pub biomass_I3: f64,
    pub P1_max: f64,
    pub P2_max: f64,
    pub P3_max: f64,
    pub carcass_biomass: f64,
    pub temperature_c: f64,
}

impl Cell {
    pub fn new(x: u32, y: u32) -> Self {
        Cell {
            x,
            y,
            elevation_m: 0.0,
            slope_deg: 0.0,
            aspect_deg: 0.0,
            tri: 0.0,
            piso_bioclimatico: piso::MONTANO,
            habitat_type: habitat::PASTIZAL,
            snow_cover: 0.0,
            is_water: false,
            is_riparian: false,
            cost_a_star: 1.0,
            biomass_P1: 0.0,
            biomass_P2: 0.0,
            biomass_P3: 0.0,
            biomass_I1: 0.0,
            biomass_I2: 0.0,
            biomass_I3: 0.0,
            P1_max: 2.0,
            P2_max: 1.5,
            P3_max: 5.0,
            carcass_biomass: 0.0,
            temperature_c: 5.0,
        }
    }

    pub fn total_plant_biomass(&self) -> f64 {
        self.biomass_P1 + self.biomass_P2 + self.biomass_P3
    }

    pub fn total_invert_biomass(&self) -> f64 {
        self.biomass_I1 + self.biomass_I2 + self.biomass_I3
    }
}

pub struct TerrainGrid {
    pub width: u32,
    pub height: u32,
    pub resolution_m: u32,
    cells: Vec<Cell>,
}

impl TerrainGrid {
    pub fn new(width: u32, height: u32, resolution_m: u32) -> Self {
        let total = (width * height) as usize;
        let mut cells = Vec::with_capacity(total);
        for y in 0..height {
            for x in 0..width {
                cells.push(Cell::new(x, y));
            }
        }
        TerrainGrid {
            width,
            height,
            resolution_m,
            cells,
        }
    }

    fn idx(&self, x: u32, y: u32) -> usize {
        (y * self.width + x) as usize
    }

    pub fn cell(&self, x: u32, y: u32) -> &Cell {
        &self.cells[self.idx(x, y)]
    }

    pub fn cell_mut(&mut self, x: u32, y: u32) -> &mut Cell {
        let i = self.idx(x, y);
        &mut self.cells[i]
    }

    pub fn cells(&self) -> &[Cell] {
        &self.cells
    }

    pub fn cells_mut(&mut self) -> &mut [Cell] {
        &mut self.cells
    }

    pub fn cell_at_idx_mut(&mut self, idx: usize) -> &mut Cell {
        &mut self.cells[idx]
    }

    pub fn in_bounds(&self, x: i32, y: i32) -> bool {
        x >= 0 && (x as u32) < self.width && y >= 0 && (y as u32) < self.height
    }

    pub fn pos_to_idx(&self, x: i32, y: i32) -> usize {
        (y as u32 * self.width + x as u32) as usize
    }

    pub fn neighbors(&self, x: i32, y: i32, diagonal: bool) -> Vec<(i32, i32)> {
        let mut result = Vec::with_capacity(if diagonal { 8 } else { 4 });
        for (dx, dy) in &[(-1, 0), (1, 0), (0, -1), (0, 1)] {
            let (nx, ny) = (x + dx, y + dy);
            if self.in_bounds(nx, ny) {
                result.push((nx, ny));
            }
        }
        if diagonal {
            for (dx, dy) in &[(-1, -1), (-1, 1), (1, -1), (1, 1)] {
                let (nx, ny) = (x + dx, y + dy);
                if self.in_bounds(nx, ny) {
                    result.push((nx, ny));
                }
            }
        }
        result
    }

    pub fn update_costs(&mut self) {
        for cell in &mut self.cells {
            let base = slope_cost_factor(cell.slope_deg);
            let snow_factor = 1.0 + cell.snow_cover;
            let terrain_factor = match cell.habitat_type {
                habitat::BOSQUE_CON | habitat::BOSQUE_CAD => 1.3,
                habitat::ROCA => 1.6,
                habitat::AGUA => 3.0,
                habitat::ANTROPICO => 1.2,
                _ => 1.0,
            };
            cell.cost_a_star = base * snow_factor * terrain_factor;
        }
    }

    pub fn total_plant_biomass(&self) -> f64 {
        self.cells.iter().map(|c| c.total_plant_biomass()).sum()
    }

    pub fn total_invert_biomass(&self) -> f64 {
        self.cells.iter().map(|c| c.total_invert_biomass()).sum()
    }

    pub fn total_carcass_biomass(&self) -> f64 {
        self.cells.iter().map(|c| c.carcass_biomass).sum()
    }

    pub fn count_water_cells(&self) -> u32 {
        self.cells.iter().filter(|c| c.is_water).count() as u32
    }

    pub fn step_snow(&mut self, day: i32) {
        let doy = day % 365;
        let season_amplitude =
            (2.0 * std::f64::consts::PI * (doy as f64 - 15.0) / 365.0).cos();
        let snow_line = 2400.0 + 600.0 * (season_amplitude + 1.0) / 2.0;
        for cell in &mut self.cells {
            if cell.elevation_m < snow_line {
                cell.snow_cover = 0.0;
            } else {
                cell.snow_cover = ((cell.elevation_m - snow_line) / 800.0).min(1.0);
            }
        }
    }

    pub fn step_temperature(&mut self, day: i32) {
        for cell in &mut self.cells {
            cell.temperature_c = default_temp_fn(cell.elevation_m, day);
        }
    }

    pub fn step_plants_logistic(&mut self, growth_mod: f64) {
        for cell in &mut self.cells {
            if cell.is_water || cell.snow_cover > 0.5 {
                continue;
            }
            if cell.habitat_type == habitat::ROCA || cell.habitat_type == habitat::NIEVE {
                continue;
            }
            if cell.biomass_P1 > 0.0 {
                let r = 0.02 * growth_mod;
                let k = cell.P1_max;
                cell.biomass_P1 += r * cell.biomass_P1 * (1.0 - cell.biomass_P1 / k);
            }
            if cell.biomass_P2 > 0.0 {
                let r = 0.015 * growth_mod;
                let k = cell.P2_max;
                cell.biomass_P2 += r * cell.biomass_P2 * (1.0 - cell.biomass_P2 / k);
            }
            if cell.biomass_P3 > 0.0 {
                let r = 0.03 * growth_mod;
                let k = cell.P3_max;
                cell.biomass_P3 += r * cell.biomass_P3 * (1.0 - cell.biomass_P3 / k);
            }
            cell.biomass_P1 = cell.biomass_P1.clamp(0.0, cell.P1_max);
            cell.biomass_P2 = cell.biomass_P2.clamp(0.0, cell.P2_max);
            cell.biomass_P3 = cell.biomass_P3.clamp(0.0, cell.P3_max);
        }
    }

    pub fn step_inverts(&mut self, growth_mod: f64) {
        for cell in &mut self.cells {
            if cell.is_water || cell.snow_cover > 0.5 {
                continue;
            }
            cell.biomass_I1 =
                (cell.biomass_I1 + 0.01 * growth_mod * cell.biomass_P1 * 0.1).clamp(0.0, 0.5);
            cell.biomass_I2 = (cell.biomass_I2 + 0.015 * growth_mod * cell.biomass_P3 * 0.08)
                .clamp(0.0, 0.8);
            cell.biomass_I3 =
                (cell.biomass_I3 + 0.008 * growth_mod * cell.biomass_I2 * 0.2).clamp(0.0, 0.3);
        }
    }

    pub fn decay_carcasses(&mut self) {
        for cell in &mut self.cells {
            cell.carcass_biomass *= 0.95;
            if cell.carcass_biomass < 0.001 {
                cell.carcass_biomass = 0.0;
            }
        }
    }

    pub fn cost_array(&self) -> Vec<f64> {
        self.cells.iter().map(|c| c.cost_a_star).collect()
    }

    pub fn get_biomass_arrays(&self) -> Vec<f64> {
        let mut out = Vec::with_capacity(self.cells.len() * 6);
        for c in &self.cells {
            out.push(c.biomass_P1);
            out.push(c.biomass_P2);
            out.push(c.biomass_P3);
            out.push(c.biomass_I1);
            out.push(c.biomass_I2);
            out.push(c.biomass_I3);
        }
        out
    }

    pub fn set_biomass_arrays(&mut self, arr: &[f64]) {
        for (i, c) in self.cells.iter_mut().enumerate() {
            let base = i * 6;
            c.biomass_P1 = arr[base];
            c.biomass_P2 = arr[base + 1];
            c.biomass_P3 = arr[base + 2];
            c.biomass_I1 = arr[base + 3];
            c.biomass_I2 = arr[base + 4];
            c.biomass_I3 = arr[base + 5];
        }
    }
}

pub fn slope_cost_factor(slope_deg: f64) -> f64 {
    if slope_deg < 5.0 {
        1.0
    } else if slope_deg < 15.0 {
        1.5
    } else if slope_deg < 30.0 {
        2.5
    } else {
        3.5
    }
}

pub fn seasonal_growth_modifier(season: &str) -> f64 {
    match season {
        "summer" => 1.5,
        "spring" => 0.8,
        "autumn" => 0.5,
        _ => 0.1,
    }
}
