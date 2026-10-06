#[derive(Clone, Copy, PartialEq)]
pub enum Season {
    Winter,
    Spring,
    Summer,
    Autumn,
}

impl Season {
    pub fn name(&self) -> &'static str {
        match self {
            Season::Winter => "winter",
            Season::Spring => "spring",
            Season::Summer => "summer",
            Season::Autumn => "autumn",
        }
    }
}

pub struct Environment {
    pub total_days: i32,
    pub current_day: i32,
    pub year: i32,
    pub snow_line_base: f64,
    pub temperature_base_c: f64,
    pub precipitation_mm: f64,
}

impl Environment {
    pub fn new() -> Self {
        Environment {
            total_days: 365,
            current_day: 0,
            year: 0,
            snow_line_base: 2700.0,
            temperature_base_c: 5.0,
            precipitation_mm: 0.0,
        }
    }

    pub fn month(&self) -> i32 {
        (self.current_day % 365) / 30
    }

    pub fn season(&self) -> Season {
        let d = self.current_day % 365;
        if (60..152).contains(&d) {
            Season::Spring
        } else if (152..244).contains(&d) {
            Season::Summer
        } else if (244..335).contains(&d) {
            Season::Autumn
        } else {
            Season::Winter
        }
    }

    pub fn day_of_year(&self) -> i32 {
        self.current_day % 365
    }

    pub fn current_hour(&self, tick_in_day: i32, ticks_per_day: i32) -> f64 {
        (tick_in_day as f64 / ticks_per_day as f64) * 24.0
    }

    pub fn step(&mut self) {
        self.current_day += 1;
        if self.current_day % 365 == 0 {
            self.year += 1;
        }
    }
}

impl Default for Environment {
    fn default() -> Self {
        Self::new()
    }
}

pub fn default_snow_fn(elevation_m: f64, day: i32) -> f64 {
    let doy = day % 365;
    let season_amplitude =
        (2.0 * std::f64::consts::PI * (doy as f64 - 15.0) / 365.0).cos();
    let snow_line = 2400.0 + 600.0 * (season_amplitude + 1.0) / 2.0;
    if elevation_m < snow_line {
        0.0
    } else {
        ((elevation_m - snow_line) / 800.0).min(1.0)
    }
}

pub fn default_temp_fn(elevation_m: f64, day: i32) -> f64 {
    let doy = day % 365;
    let base_temp = 5.0 + 10.0 * (2.0 * std::f64::consts::PI * (doy as f64 - 182.0) / 365.0).cos();
    let lapse_rate = -0.0065;
    base_temp + lapse_rate * (elevation_m - 1000.0).max(0.0)
}
