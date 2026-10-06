use std::path::Path;

use super::grid::{habitat, TerrainGrid};

pub fn load_terrain_from_tsv(grid: &mut TerrainGrid, path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let mut rdr = csv::ReaderBuilder::new()
        .delimiter(b'\t')
        .flexible(true)
        .from_path(path)?;

    for result in rdr.records() {
        let rec = result?;
        if rec.len() < 9 {
            continue;
        }
        let x: u32 = match rec[0].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let y: u32 = match rec[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        if x >= grid.width || y >= grid.height {
            continue;
        }
        let cell = grid.cell_mut(x, y);
        cell.elevation_m = rec[4].parse().unwrap_or(0.0);
        cell.slope_deg = rec[5].parse().unwrap_or(0.0);
        cell.aspect_deg = rec[6].parse().unwrap_or(0.0);
        cell.tri = rec[7].parse().unwrap_or(0.0);
        cell.piso_bioclimatico = rec[8].parse().unwrap_or(1);
    }

    assign_habitat_from_piso(grid);
    assign_biomass_defaults(grid);

    Ok(())
}

#[cfg(feature = "geo")]
pub fn load_terrain_from_geotiff(grid: &mut TerrainGrid, data_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    use gdal::Dataset;

    let dem_path = data_dir.join("terrain_dem_25m.tif");
    let slope_path = data_dir.join("terrain_slope.tif");
    let aspect_path = data_dir.join("terrain_aspect.tif");
    let tri_path = data_dir.join("terrain_tri.tif");
    let pisos_path = data_dir.join("terrain_pisos.tif");
    let habitat_path = data_dir.join("terrain_habitat.tif");
    let biomass_path = data_dir.join("terrain_biomass.tif");

    if !dem_path.exists() {
        return Err(format!("DEM not found: {:?}", dem_path).into());
    }

    let dem_ds = Dataset::open(dem_path)?;
    let dem_band = dem_ds.rasterband(1)?;
    let dem_data: Vec<f64> = dem_band.read_as::<f64>(
        (0, 0),
        (grid.width as usize, grid.height as usize),
        (grid.width as usize, grid.height as usize),
        None,
    )?;

    let load_band = |path: &Path| -> Result<Vec<f64>, Box<dyn std::error::Error>> {
        if path.exists() {
            let ds = Dataset::open(path)?;
            let band = ds.rasterband(1)?;
            let data: Vec<f64> = band.read_as::<f64>(
                (0, 0),
                (grid.width as usize, grid.height as usize),
                (grid.width as usize, grid.height as usize),
                None,
            )?;
            Ok(data)
        } else {
            Err(format!("File not found: {:?}", path).into())
        }
    };

    let slope_data = load_band(&slope_path)?;
    let aspect_data = load_band(&aspect_path)?;
    let tri_data = load_band(&tri_path)?;
    let pisos_data = load_band(&pisos_path)?;

    for y in 0..grid.height {
        for x in 0..grid.width {
            let idx = (y * grid.width + x) as usize;
            let cell = grid.cell_mut(x, y);
            cell.elevation_m = dem_data[idx];
            cell.slope_deg = slope_data[idx];
            cell.aspect_deg = aspect_data[idx];
            cell.tri = tri_data[idx];
            cell.piso_bioclimatico = pisos_data[idx] as u8;
        }
    }

    if habitat_path.exists() {
        if let Ok(hab_data) = load_band(&habitat_path) {
            for y in 0..grid.height {
                for x in 0..grid.width {
                    let idx = (y * grid.width + x) as usize;
                    let cell = grid.cell_mut(x, y);
                    cell.habitat_type = hab_data[idx] as u8;
                }
            }
        }
    } else {
        assign_habitat_from_piso(grid);
    }

    if biomass_path.exists() {
        let bio_ds = Dataset::open(&biomass_path)?;
        let n_bands = bio_ds.raster_count() as usize;
        let mut band_data: Vec<Vec<f64>> = Vec::new();
        for b in 1..=n_bands.min(9) {
            if let Ok(band) = bio_ds.rasterband(b as i32) {
                if let Ok(data) = band.read_as::<f64>(
                    (0, 0),
                    (grid.width as usize, grid.height as usize),
                    (grid.width as usize, grid.height as usize),
                    None,
                ) {
                    band_data.push(data);
                }
            }
        }
        if band_data.len() >= 6 {
            for y in 0..grid.height {
                for x in 0..grid.width {
                    let idx = (y * grid.width + x) as usize;
                    let cell = grid.cell_mut(x, y);
                    cell.biomass_P1 = band_data[0][idx];
                    cell.biomass_P2 = band_data[1][idx];
                    cell.biomass_P3 = band_data[2][idx];
                    cell.biomass_I1 = band_data[3][idx];
                    cell.biomass_I2 = band_data[4][idx];
                    cell.biomass_I3 = band_data[5][idx];
                    if band_data.len() >= 9 {
                        cell.P1_max = band_data[6][idx];
                        cell.P2_max = band_data[7][idx];
                        cell.P3_max = band_data[8][idx];
                    }
                }
            }
        }
    } else {
        assign_biomass_defaults(grid);
    }

    Ok(())
}

#[cfg(not(feature = "geo"))]
pub fn load_terrain_from_geotiff(_grid: &mut TerrainGrid, _data_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
    Err("GeoTIFF loading requires the 'geo' feature: cargo run --features geo".into())
}

fn assign_habitat_from_piso(grid: &mut TerrainGrid) {
    for y in 0..grid.height {
        for x in 0..grid.width {
            let cell = grid.cell(x, y);
            let piso = cell.piso_bioclimatico;
            let elev = cell.elevation_m;

            let h = if piso == 3 {
                if elev > 2500.0 { habitat::ROCA }
                else { habitat::PASTIZAL }
            } else if piso == 4 {
                habitat::ROCA
            } else if piso == 2 {
                if elev < 1900.0 { habitat::BOSQUE_CON }
                else { habitat::MATORRAL }
            } else {
                if elev < 1200.0 { habitat::BOSQUE_CAD }
                else { habitat::BOSQUE_CON }
            };

            let cell = grid.cell_mut(x, y);
            cell.habitat_type = h;
        }
    }
}

fn assign_biomass_defaults(grid: &mut TerrainGrid) {
    for y in 0..grid.height {
        for x in 0..grid.width {
            let cell = grid.cell(x, y);
            let h = cell.habitat_type;
            let (p1, p2, p3, is_water) = match h {
                h if h == habitat::BOSQUE_CON => (3.0, 2.0, 2.0, false),
                h if h == habitat::BOSQUE_CAD => (4.0, 3.0, 3.0, false),
                h if h == habitat::MATORRAL => (3.0, 1.5, 4.0, false),
                h if h == habitat::PASTIZAL => (1.0, 0.5, 5.0, false),
                h if h == habitat::HUMEDAL => (2.0, 3.0, 3.0, false),
                h if h == habitat::ROCA => (0.5, 0.3, 1.5, false),
                h if h == habitat::AGUA => (0.1, 2.0, 0.0, true),
                h if h == habitat::RIBERA => (2.0, 2.0, 3.0, false),
                h if h == habitat::NIEVE => (0.0, 0.0, 0.0, false),
                h if h == habitat::ANTROPICO => (1.0, 0.5, 2.0, false),
                _ => (1.0, 0.5, 2.0, false),
            };

            let cell = grid.cell_mut(x, y);
            cell.P1_max = p1;
            cell.P2_max = p2;
            cell.P3_max = p3;
            cell.is_water = is_water;
            cell.biomass_P1 = p1 * 0.5;
            cell.biomass_P2 = p2 * 0.5;
            cell.biomass_P3 = p3 * 0.5;
            cell.biomass_I1 = p1 * 0.05;
            cell.biomass_I2 = p3 * 0.04;
            cell.biomass_I3 = 0.01;
        }
    }
}
