use std::collections::HashMap;
use std::path::Path;
use std::sync::OnceLock;

#[derive(Clone, Debug)]
pub struct Diet {
    pub plant_proportion: f64,
    pub invert_proportion: f64,
    pub vertebrate_proportion: f64,
    pub carrion_proportion: f64,
    pub fish_proportion: f64,
}

impl Diet {
    pub fn is_valid(&self) -> bool {
        let total = self.plant_proportion
            + self.invert_proportion
            + self.vertebrate_proportion
            + self.carrion_proportion
            + self.fish_proportion;
        (total - 1.0).abs() < 0.01
    }
}

impl Default for Diet {
    fn default() -> Self {
        Diet {
            plant_proportion: 0.0,
            invert_proportion: 0.0,
            vertebrate_proportion: 0.0,
            carrion_proportion: 0.0,
            fish_proportion: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct TrophicLinkData {
    pub consumer: String,
    pub resource: String,
    pub interaction_type: String,
    pub confidence: String,
}

static DIET_CACHE: OnceLock<HashMap<String, Diet>> = OnceLock::new();
static TROPHIC_CACHE: OnceLock<Vec<TrophicLinkData>> = OnceLock::new();
static SPECIES_ALIAS: OnceLock<HashMap<String, String>> = OnceLock::new();

fn species_key(scientific_name: &str) -> String {
    let cleaned = scientific_name.split('(').next().unwrap_or(scientific_name).trim();
    let parts: Vec<&str> = cleaned.split_whitespace().collect();
    if parts.len() >= 2 {
        format!("{}_{}", parts[0], parts[1])
    } else {
        cleaned.to_string()
    }
}

fn build_alias_map() -> HashMap<String, String> {
    let mut m = HashMap::new();
    m.insert("Rupicapra pyrenaica pyrenaica".to_string(), "Rupicapra_pyrenaica".to_string());
    m.insert("Cervus elaphus".to_string(), "Cervus_elaphus".to_string());
    m.insert("Capreolus capreolus".to_string(), "Capreolus_capreolus".to_string());
    m.insert("Sus scrofa".to_string(), "Sus_scrofa".to_string());
    m.insert("Ursus arctos arctos".to_string(), "Ursus_arctos".to_string());
    m.insert("Lutra lutra".to_string(), "Lutra_lutra".to_string());
    m.insert("Galemys pyrenaicus".to_string(), "Galemys_pyrenaicus".to_string());
    m.insert("Martes martes".to_string(), "Martes_martes".to_string());
    m.insert("Vulpes vulpes".to_string(), "Vulpes_vulpes".to_string());
    m.insert("Felis silvestris".to_string(), "Felis_silvestris".to_string());
    m.insert("Mustela nivalis".to_string(), "Mustela_nivalis".to_string());
    m.insert("Mustela erminea".to_string(), "Mustela_erminea".to_string());
    m.insert("Tetrao urogallus (subsp. pirenaica)".to_string(), "Tetrao_urogallus".to_string());
    m.insert("Lagopus muta".to_string(), "Lagopus_muta".to_string());
    m.insert("Gypaetus barbatus".to_string(), "Gypaetus_barbatus".to_string());
    m.insert("Aquila chrysaetos".to_string(), "Aquila_chrysaetos".to_string());
    m.insert("Corvus corax".to_string(), "Corvus_corax".to_string());
    m.insert("Iberolacerta aurelioi".to_string(), "Iberolacerta_aurelioi".to_string());
    m.insert("Podarcis muralis".to_string(), "Podarcis_muralis".to_string());
    m.insert("Zootoca vivipara".to_string(), "Zootoca_vivipara".to_string());
    m.insert("Calotriton asper".to_string(), "Calotriton_asper".to_string());
    m.insert("Rana temporaria".to_string(), "Rana_temporaria".to_string());
    m.insert("Bufo bufo".to_string(), "Bufo_bufo".to_string());
    m.insert("Salamandra salamandra".to_string(), "Salamandra_salamandra".to_string());
    m.insert("Salmo trutta".to_string(), "Salmo_trutta".to_string());
    m.insert("Phoxinus spp.".to_string(), "Phoxinus_spp".to_string());
    m.insert("Ovis aries musimon".to_string(), "Ovis_aries_musimon".to_string());
    m.insert("Dama dama".to_string(), "Dama_dama".to_string());
    m.insert("Marmota marmota".to_string(), "Marmota_marmota".to_string());
    m.insert("Oryctolagus cuniculus".to_string(), "Oryctolagus_cuniculus".to_string());
    m.insert("Meles meles".to_string(), "Meles_meles".to_string());
    m.insert("Sciurus vulgaris".to_string(), "Sciurus_vulgaris".to_string());
    m
}

fn resolve_key(scientific_name: &str) -> String {
    let alias = SPECIES_ALIAS.get()
        .and_then(|m| m.get(scientific_name));
    match alias {
        Some(k) => k.clone(),
        None => {
            let k = species_key(scientific_name);
            if k != scientific_name {
                k
            } else {
                scientific_name.to_string()
            }
        }
    }
}

pub fn load_diet_data(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let _ = SPECIES_ALIAS.set(build_alias_map());

    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(b'\t')
        .flexible(true)
        .from_path(path)?;

    let mut raw: Vec<(String, String, f64)> = Vec::new();

    for result in rdr.records() {
        let rec = match result {
            Ok(r) => r,
            Err(_) => continue,
        };
        if rec.len() < 4 {
            continue;
        }
        let field0 = rec.get(0).unwrap_or("").trim();
        let field1 = rec.get(1).unwrap_or("").trim();
        if field0.starts_with('#') || field1.starts_with('#') {
            continue;
        }

        // Handle inconsistent TSV: some rows have extra duplicate name column
        let category_idx = if rec.len() >= 5 && field1 == rec.get(2).unwrap_or("") {
            // Format: taxon	sci_name	sci_name(dup)	resource	proportion
            3
        } else {
            2
        };

        let category = rec.get(category_idx).unwrap_or("").trim();
        if category.is_empty() {
            continue;
        }

        let proportion: f64 = match rec.get(category_idx + 1).unwrap_or("0").parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        // Skip cluster-level entries (they define relationships between clusters, not individual diets)
        if field0 == "Planta" || field0 == "Invertebrado" || field1.starts_with("P1") || field1.starts_with("P2") || field1.starts_with("P3") || field1.starts_with("I1") || field1.starts_with("I2") || field1.starts_with("I3") {
            continue;
        }

        let combined_key = format!("{}__{}", field0, field1);

        let resource_type = if category == "Plantas" || category == "P1" || category == "P2" || category == "P3" {
            "plant"
        } else if category == "Invertebrados" {
            "invert"
        } else if category == "Vertebrados" {
            "vertebrate"
        } else {
            "other"
        };

        if resource_type != "other" {
            raw.push((combined_key, resource_type.to_string(), proportion));
        }
    }

    let mut diet_map: HashMap<String, Diet> = HashMap::new();

    for (combined_key, rtype, prop) in &raw {
        let entry = diet_map.entry(combined_key.clone()).or_insert(Diet::default());
        match rtype.as_str() {
            "plant" => entry.plant_proportion += prop,
            "invert" => entry.invert_proportion += prop,
            "vertebrate" => entry.vertebrate_proportion += prop,
            _ => {}
        }
    }

    let keyed_map: HashMap<String, Diet> = diet_map.into_iter().map(|(ck, diet)| {
        let parts: Vec<&str> = ck.split("__").collect();
        let sci_name = if parts.len() >= 2 { parts[1] } else { &ck };
        let key = resolve_key(sci_name);
        (key, diet)
    }).collect();

    DIET_CACHE.set(keyed_map).ok();
    Ok(())
}

pub fn load_trophic_data(path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(b'\t')
        .flexible(true)
        .from_path(path)?;

    let mut links = Vec::new();

    for result in rdr.records() {
        let rec = match result {
            Ok(r) => r,
            Err(_) => continue,
        };
        if rec.len() < 6 {
            continue;
        }
        let consumer_name = rec.get(1).unwrap_or("").trim().to_string();
        let resource_name = rec.get(3).unwrap_or("").trim().to_string();
        let interaction_type = rec.get(4).unwrap_or("").trim().to_string();
        let confidence = rec.get(5).unwrap_or("").trim().to_string();

        if consumer_name.starts_with('#') || resource_name == "Various" || resource_name.starts_with('#') {
            continue;
        }

        links.push(TrophicLinkData {
            consumer: resolve_key(&consumer_name),
            resource: resolve_key(&resource_name),
            interaction_type,
            confidence,
        });
    }

    TROPHIC_CACHE.set(links).ok();
    Ok(())
}

pub fn get_diet(species_key: &str) -> Option<Diet> {
    if let Some(cache) = DIET_CACHE.get() {
        if let Some(diet) = cache.get(species_key) {
            return Some(diet.clone());
        }
    }
    legacy_get_diet(species_key)
}

fn legacy_get_diet(species_key: &str) -> Option<Diet> {
    match species_key {
        "Rupicapra_pyrenaica" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Cervus_elaphus" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Capreolus_capreolus" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Marmota_marmota" => Some(Diet { plant_proportion: 0.95, invert_proportion: 0.05, ..Default::default() }),
        "Oryctolagus_cuniculus" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Sciurus_vulgaris" => Some(Diet { plant_proportion: 0.95, invert_proportion: 0.05, ..Default::default() }),
        "Ovis_aries_musimon" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Dama_dama" => Some(Diet { plant_proportion: 1.0, ..Default::default() }),
        "Lagopus_muta" => Some(Diet { plant_proportion: 0.8, invert_proportion: 0.2, ..Default::default() }),
        "Tetrao_urogallus" => Some(Diet { plant_proportion: 0.7, invert_proportion: 0.3, ..Default::default() }),
        "Aquila_chrysaetos" => Some(Diet { vertebrate_proportion: 0.9, carrion_proportion: 0.1, ..Default::default() }),
        "Lutra_lutra" => Some(Diet { fish_proportion: 0.8, invert_proportion: 0.1, vertebrate_proportion: 0.1, ..Default::default() }),
        "Martes_martes" => Some(Diet { vertebrate_proportion: 0.5, invert_proportion: 0.3, plant_proportion: 0.2, ..Default::default() }),
        "Mustela_erminea" => Some(Diet { vertebrate_proportion: 0.7, invert_proportion: 0.3, ..Default::default() }),
        "Mustela_nivalis" => Some(Diet { vertebrate_proportion: 0.7, invert_proportion: 0.3, ..Default::default() }),
        "Felis_silvestris" => Some(Diet { vertebrate_proportion: 0.8, invert_proportion: 0.2, ..Default::default() }),
        "Ursus_arctos" => Some(Diet { plant_proportion: 0.8, invert_proportion: 0.1, vertebrate_proportion: 0.05, carrion_proportion: 0.05, ..Default::default() }),
        "Sus_scrofa" => Some(Diet { plant_proportion: 0.7, invert_proportion: 0.2, vertebrate_proportion: 0.05, carrion_proportion: 0.05, ..Default::default() }),
        "Vulpes_vulpes" => Some(Diet { vertebrate_proportion: 0.4, invert_proportion: 0.3, plant_proportion: 0.2, carrion_proportion: 0.1, ..Default::default() }),
        "Meles_meles" => Some(Diet { invert_proportion: 0.5, plant_proportion: 0.3, vertebrate_proportion: 0.15, carrion_proportion: 0.05, ..Default::default() }),
        "Corvus_corax" => Some(Diet { carrion_proportion: 0.4, invert_proportion: 0.3, plant_proportion: 0.2, vertebrate_proportion: 0.1, ..Default::default() }),
        "Gypaetus_barbatus" => Some(Diet { carrion_proportion: 0.95, vertebrate_proportion: 0.05, ..Default::default() }),
        _ => None,
    }
}

pub fn get_prey_weighted(species_key: &str) -> Vec<(String, f64)> {
    if let Some(cache) = TROPHIC_CACHE.get() {
        let predation_links: Vec<&TrophicLinkData> = cache.iter()
            .filter(|l| l.consumer == species_key && l.interaction_type == "predation")
            .collect();

        if predation_links.is_empty() {
            return Vec::new();
        }

        let count = predation_links.len() as f64;
        return predation_links.iter()
            .map(|l| (l.resource.clone(), 1.0 / count))
            .collect();
    }
    legacy_get_prey_weighted(species_key)
}

pub fn get_prey(species_key: &str) -> Vec<String> {
    if let Some(cache) = TROPHIC_CACHE.get() {
        return cache.iter()
            .filter(|l| l.consumer == species_key && l.interaction_type == "predation")
            .map(|l| l.resource.clone())
            .collect();
    }
    legacy_get_prey(species_key).into_iter().map(|s| s.to_string()).collect()
}

pub fn get_scavenge_prey(species_key: &str) -> Vec<String> {
    if let Some(cache) = TROPHIC_CACHE.get() {
        return cache.iter()
            .filter(|l| l.consumer == species_key && l.interaction_type == "scavenging")
            .map(|l| l.resource.clone())
            .collect();
    }
    Vec::new()
}

pub fn get_predators(species_key: &str) -> Vec<String> {
    if let Some(cache) = TROPHIC_CACHE.get() {
        return cache.iter()
            .filter(|l| l.resource == species_key)
            .map(|l| l.consumer.clone())
            .collect();
    }
    legacy_get_predators(species_key).into_iter().map(|s| s.to_string()).collect()
}

pub fn get_all_trophic_links() -> &'static [TrophicLinkData] {
    if let Some(cache) = TROPHIC_CACHE.get() {
        return cache.as_slice();
    }
    &[]
}

pub fn is_data_loaded() -> bool {
    DIET_CACHE.get().is_some()
}

const TROPHIC_LINKS_LEGACY: &[TrophicLink] = &[
    TrophicLink { consumer: "Aquila_chrysaetos", resource: "Rupicapra_pyrenaica", proportion: 0.3 },
    TrophicLink { consumer: "Aquila_chrysaetos", resource: "Marmota_marmota", proportion: 0.5 },
    TrophicLink { consumer: "Aquila_chrysaetos", resource: "Lagopus_muta", proportion: 0.1 },
    TrophicLink { consumer: "Martes_martes", resource: "Tetrao_urogallus", proportion: 0.3 },
    TrophicLink { consumer: "Martes_martes", resource: "Sciurus_vulgaris", proportion: 0.3 },
    TrophicLink { consumer: "Vulpes_vulpes", resource: "Oryctolagus_cuniculus", proportion: 0.3 },
    TrophicLink { consumer: "Vulpes_vulpes", resource: "Tetrao_urogallus", proportion: 0.1 },
    TrophicLink { consumer: "Vulpes_vulpes", resource: "Lagopus_muta", proportion: 0.1 },
    TrophicLink { consumer: "Gypaetus_barbatus", resource: "Rupicapra_pyrenaica", proportion: 0.4 },
    TrophicLink { consumer: "Gypaetus_barbatus", resource: "Cervus_elaphus", proportion: 0.3 },
    TrophicLink { consumer: "Lutra_lutra", resource: "Salmo_trutta", proportion: 0.6 },
    TrophicLink { consumer: "Mustela_erminea", resource: "Lagopus_muta", proportion: 0.2 },
    TrophicLink { consumer: "Mustela_nivalis", resource: "Oryctolagus_cuniculus", proportion: 0.2 },
    TrophicLink { consumer: "Felis_silvestris", resource: "Oryctolagus_cuniculus", proportion: 0.3 },
    TrophicLink { consumer: "Felis_silvestris", resource: "Tetrao_urogallus", proportion: 0.1 },
];

struct TrophicLink {
    consumer: &'static str,
    resource: &'static str,
    proportion: f64,
}

fn legacy_get_prey_weighted(species_key: &str) -> Vec<(String, f64)> {
    TROPHIC_LINKS_LEGACY
        .iter()
        .filter(|l| l.consumer == species_key)
        .map(|l| (l.resource.to_string(), l.proportion))
        .collect()
}

fn legacy_get_prey(species_key: &str) -> Vec<&'static str> {
    TROPHIC_LINKS_LEGACY
        .iter()
        .filter(|l| l.consumer == species_key)
        .map(|l| l.resource)
        .collect()
}

fn legacy_get_predators(species_key: &str) -> Vec<&'static str> {
    TROPHIC_LINKS_LEGACY
        .iter()
        .filter(|l| l.resource == species_key)
        .map(|l| l.consumer)
        .collect()
}
