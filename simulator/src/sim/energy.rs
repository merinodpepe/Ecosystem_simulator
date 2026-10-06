use std::collections::HashMap;
use std::path::Path;
use std::sync::OnceLock;

static ENERGY_DENSITY: OnceLock<HashMap<String, f64>> = OnceLock::new();
static ACTIVITY_COSTS: OnceLock<HashMap<String, (f64, f64)>> = OnceLock::new();

pub const TICKS_PER_DAY: f64 = 2880.0;
pub const SECONDS_PER_TICK: f64 = 30.0;
pub const TICKS_PER_HOUR: f64 = TICKS_PER_DAY / 24.0;
pub const INITIAL_ENERGY_RATIO: f64 = 2000.0; // kcal per kg of body mass
pub const INITIAL_FAT_RATIO: f64 = 1000.0; // kcal per kg of body mass
pub const CRITICAL_ENERGY_RATIO: f64 = 0.05;  // die below 5% of initial

/// Maximum sustained metabolisable energy intake as a multiple of BMR
/// (sustained metabolic scope 4-7×, Hammond & Diamond 1997).
pub const INTAKE_SCOPE: f64 = 5.0;
/// Hours per day an animal can spend feeding when food is available.
pub const FEEDING_HOURS_PER_DAY: f64 = 10.0;
/// Field metabolic rate as a multiple of BMR (≈ 2-3×, Nagy 2005).
pub const FMR_FACTOR: f64 = 2.5;
/// Fraction of BMR spent while hibernating, averaged over torpor bouts and
/// periodic arousals (Ruf & Geiser 2015: 10-30%).
pub const HIBERNATION_BMR_FRACTION: f64 = 0.15;

/// Assimilation efficiencies (fraction of gross energy retained).
pub const ASSIM_MEAT: f64 = 0.80;
pub const ASSIM_CARRION: f64 = 0.75;
pub const ASSIM_INVERT: f64 = 0.75;

/// Plant biomass is tracked in kg of dry matter (DM) per cluster
/// [P1 forbs/dwarf shrubs, P2 ferns/mosses/aquatic, P3 grasses].
/// Gross energy of forage DM is 4.0-4.6 kcal/g; energia_recursos.tsv only has
/// fresh-weight vegetable values, so DM values are set here.
pub const PLANT_GE_DM: [f64; 3] = [4500.0, 4000.0, 4200.0];
/// Apparent digestibility of plant DM per cluster.
pub const PLANT_DIGESTIBILITY: [f64; 3] = [0.50, 0.35, 0.60];

/// Invertebrate values in energia_recursos.tsv (4-5 kcal/g) are dry-mass values
/// despite the column name; above this threshold they are converted to fresh
/// mass assuming ~75% water.
const INVERT_DRY_THRESHOLD_KCAL_G: f64 = 3.0;
const INVERT_DRY_TO_WET: f64 = 0.25;

pub fn load_energy_data(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(b'\t')
        .flexible(true)
        .from_path(path)?;

    let mut map: HashMap<String, f64> = HashMap::new();

    for result in rdr.records() {
        let rec = match result {
            Ok(r) => r,
            Err(_) => continue,
        };
        if rec.len() < 3 || rec.get(0).unwrap_or("").trim().starts_with('#') {
            continue;
        }
        let resource_type = rec.get(0).unwrap_or("").trim().to_string();
        let subtype = rec.get(1).unwrap_or("").trim().to_string();
        let kcal_per_g: f64 = match rec.get(2).unwrap_or("0").parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        map.insert(format!("{}/{}", resource_type, subtype), kcal_per_g);
    }

    ENERGY_DENSITY.set(map).ok();
    Ok(())
}

pub fn load_activity_costs(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(b'\t')
        .flexible(true)
        .from_path(path)?;

    let mut map: HashMap<String, (f64, f64)> = HashMap::new();

    for result in rdr.records() {
        let rec = match result {
            Ok(r) => r,
            Err(_) => continue,
        };
        if rec.len() < 3 || rec.get(0).unwrap_or("").trim().starts_with('#') {
            continue;
        }
        let activity_id = rec.get(0).unwrap_or("").trim().to_string();
        let met: f64 = match rec.get(2).unwrap_or("0").parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let cost_per_km: f64 = rec.get(4).unwrap_or("0").parse().unwrap_or(0.0);

        map.insert(activity_id, (met, cost_per_km));
    }

    ACTIVITY_COSTS.set(map).ok();
    Ok(())
}

/// First TSV value (kcal/g) whose key is `resource_type/<subtype starting with prefix>`.
fn lookup_density(resource_type: &str, subtype_prefix: &str) -> Option<f64> {
    let cache = ENERGY_DENSITY.get()?;
    let prefix = format!("{}/{}", resource_type, subtype_prefix);
    let mut matches: Vec<(&String, &f64)> = cache.iter().filter(|(k, _)| k.starts_with(&prefix)).collect();
    matches.sort_by(|a, b| a.0.cmp(b.0));
    matches.first().map(|(_, &v)| v)
}

/// Energy per tick based on activity MET, body mass and reproductive state.
/// Cold penalty scales with how far below -3°C the cell is.
pub fn tick_energy(mass_kg: f64, met: f64, cell_temp_c: f64, is_pregnant: bool, is_lactating: bool) -> f64 {
    let bmr_tick = bmr_kcal_day(mass_kg) / TICKS_PER_DAY;
    let mut cost = bmr_tick * met;
    if cell_temp_c < -3.0 {
        let severity = ((-3.0 - cell_temp_c) / 10.0).min(1.0);
        cost += bmr_tick * get_activity_met("TERMO_SHIVERING") * severity * 0.5;
    }
    cost + bmr_tick * reproduction_extra_met(is_pregnant, is_lactating)
}

/// Extra metabolic cost of gestation / lactation above resting (MET - 1),
/// from costos_actividad.tsv.
pub fn reproduction_extra_met(is_pregnant: bool, is_lactating: bool) -> f64 {
    let mut extra = 0.0;
    if is_pregnant {
        extra += get_activity_met("REPRO_GESTATION") - 1.0;
    }
    if is_lactating {
        extra += get_activity_met("REPRO_LACTATION") - 1.0;
    }
    extra
}

/// Energy per tick while hibernating (paid from fat reserves).
pub fn hibernation_tick_energy(mass_kg: f64) -> f64 {
    bmr_kcal_day(mass_kg) * HIBERNATION_BMR_FRACTION / TICKS_PER_DAY
}

/// MET value for each FSM state. Used by tick_energy().
pub fn met_for_state(state: &str) -> f64 {
    match state {
        "IDLE" | "REST"     => 1.0,
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

/// Maximum metabolisable energy an animal can ingest per feeding tick.
pub fn max_intake_kcal_per_tick(mass_kg: f64) -> f64 {
    INTAKE_SCOPE * bmr_kcal_day(mass_kg) / (FEEDING_HOURS_PER_DAY * TICKS_PER_HOUR)
}

/// Maximum metabolisable energy an animal can ingest per day.
pub fn max_intake_kcal_per_day(mass_kg: f64) -> f64 {
    INTAKE_SCOPE * bmr_kcal_day(mass_kg)
}

/// Expected daily energy need (field metabolic rate plus reproduction).
pub fn daily_need_kcal(mass_kg: f64, is_pregnant: bool, is_lactating: bool) -> f64 {
    bmr_kcal_day(mass_kg) * (FMR_FACTOR + reproduction_extra_met(is_pregnant, is_lactating))
}

/// Critical energy threshold: die when energy drops below this.
pub fn critical_energy_threshold(mass_kg: f64) -> f64 {
    mass_kg * INITIAL_ENERGY_RATIO * CRITICAL_ENERGY_RATIO
}

/// Metabolisable energy (kcal) per kg DM of plant cluster 0..3 (P1, P2, P3).
pub fn plant_me_per_kg(cluster: usize) -> f64 {
    PLANT_GE_DM[cluster] * PLANT_DIGESTIBILITY[cluster]
}

/// Gross energy of fresh invertebrate biomass (kcal/kg): mean of the TSV rows.
pub fn energy_density_invert() -> f64 {
    if let Some(cache) = ENERGY_DENSITY.get() {
        let values: Vec<f64> = cache.iter()
            .filter(|(k, _)| k.starts_with("Invertebrados/"))
            .map(|(_, &v)| v)
            .collect();
        if !values.is_empty() {
            let mean = values.iter().sum::<f64>() / values.len() as f64;
            let wet = if mean > INVERT_DRY_THRESHOLD_KCAL_G { mean * INVERT_DRY_TO_WET } else { mean };
            return wet * 1000.0;
        }
    }
    1200.0
}

/// Gross energy of vertebrate carcass tissue (kcal/kg fresh): muscle with intramuscular fat.
pub fn energy_density_meat() -> f64 {
    lookup_density("Vertebrados", "Tejido muscular medio")
        .or_else(|| lookup_density("Vertebrados", "Músculo esquelético"))
        .map(|v| v * 1000.0)
        .unwrap_or(1600.0)
}

pub fn invert_me_per_kg() -> f64 {
    energy_density_invert() * ASSIM_INVERT
}

pub fn meat_me_per_kg() -> f64 {
    energy_density_meat() * ASSIM_MEAT
}

pub fn carrion_me_per_kg() -> f64 {
    energy_density_meat() * ASSIM_CARRION
}

pub fn get_activity_met(activity_id: &str) -> f64 {
    if let Some(cache) = ACTIVITY_COSTS.get() {
        if let Some(&(met, _)) = cache.get(activity_id) {
            return met;
        }
    }
    match activity_id {
        "RESTING" => 1.0,
        "FORAGE_SEARCH" => 3.0,
        "FORAGE_INTAKE" => 1.5,
        "LOCO_WALK_SLOW" => 2.0,
        "LOCO_WALK_MOD" => 2.5,
        "LOCO_WALK_FAST" => 3.0,
        "LOCO_TROT" => 4.5,
        "LOCO_GALLOP" => 7.0,
        "LOCO_CLIMB" => 5.0,
        "VIGILANCE" => 1.3,
        "TERMO_SHIVERING" => 2.0,
        "REPRO_GESTATION" => 1.3,
        "REPRO_LACTATION" => 3.0,
        _ => 1.5,
    }
}

pub fn bmr_kcal_day(mass_kg: f64) -> f64 {
    70.0 * mass_kg.powf(0.75)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bmr_follows_kleiber() {
        assert!((bmr_kcal_day(1.0) - 70.0).abs() < 1e-9);
        // 16× the mass → 8× the BMR
        assert!((bmr_kcal_day(16.0) / bmr_kcal_day(1.0) - 8.0).abs() < 1e-9);
    }

    #[test]
    fn daily_intake_cap_exceeds_daily_need() {
        for &m in &[0.08, 1.0, 35.0, 200.0] {
            assert!(max_intake_kcal_per_day(m) > daily_need_kcal(m, false, false));
            let per_tick_total = max_intake_kcal_per_tick(m) * FEEDING_HOURS_PER_DAY * TICKS_PER_HOUR;
            assert!((per_tick_total - max_intake_kcal_per_day(m)).abs() < 1e-6);
        }
    }

    #[test]
    fn reproduction_costs_energy() {
        let base = tick_energy(35.0, 1.0, 10.0, false, false);
        assert!(tick_energy(35.0, 1.0, 10.0, true, false) > base);
        assert!(tick_energy(35.0, 1.0, 10.0, false, true) > tick_energy(35.0, 1.0, 10.0, true, false));
    }

    #[test]
    fn cold_costs_energy() {
        assert!(tick_energy(4.0, 1.0, -13.0, false, false) > tick_energy(4.0, 1.0, 5.0, false, false));
    }

    #[test]
    fn hibernation_is_cheaper_than_rest() {
        assert!(hibernation_tick_energy(4.5) < tick_energy(4.5, 1.0, 10.0, false, false));
    }

    #[test]
    fn grass_energy_is_realistic() {
        // Metabolisable energy of grass DM ≈ 2-3 kcal/g
        let me = plant_me_per_kg(2);
        assert!(me > 2000.0 && me < 3000.0, "{}", me);
    }
}
