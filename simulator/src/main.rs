use clap::Parser;

use ecosystem_simulator_rs::sim::Simulation;

#[derive(Parser)]
#[command(name = "ecosystem-sim", about = "Alt Pirineu Ecosystem Simulator (Rust)")]
struct Args {
    #[arg(long, default_value_t = 400)]
    width: u32,

    #[arg(long, default_value_t = 400)]
    height: u32,

    #[arg(long, default_value_t = 365)]
    days: i32,

    #[arg(long, default_value_t = 25)]
    res: u32,

    #[arg(long, default_value = "output")]
    output: String,

    #[arg(long)]
    demo: bool,

    #[arg(long, default_value = "../ecosystem/data")]
    data_dir: String,

    #[arg(long, default_value_t = 100)]
    snapshot_every: i32,
}

fn main() {
    let args = Args::parse();

    let (width, height) = if args.demo {
        (50u32, 50u32)
    } else {
        (args.width, args.height)
    };

    let days = if args.demo { 30 } else { args.days };

    let total_cells = width * height;
    let area_km_w = width as f64 * args.res as f64 / 1000.0;
    let area_km_h = height as f64 * args.res as f64 / 1000.0;

    println!("{}", "=".repeat(60));
    println!("  Alt Pirineu Ecosystem Simulator (Rust v0.2)");
    println!("{}", "=".repeat(60));
    println!("  Grid:       {}×{} = {} cells @ {}m", width, height, total_cells, args.res);
    println!("  Area:       {:.1}×{:.1} km", area_km_w, area_km_h);
    println!("  Days:       {}", days);
    println!("  Output:     {}", args.output);
    println!("  Data dir:   {}", args.data_dir);
    println!("{}", "=".repeat(60));

    let mut sim = Simulation::new(width, height, args.res, days, &args.output, &args.data_dir);
    sim.snapshot_every = args.snapshot_every;

    sim.initialize();

    let pre = sim.get_stats();
    println!(
        "\n  Initial state: {} agents, {:.0} kg plant biomass\n",
        pre["agents_alive"].as_u64().unwrap_or(0),
        pre["plant_biomass_kg"].as_f64().unwrap_or(0.0),
    );

    sim.run();

    let post = sim.get_stats();
    println!("\n  Final state ({} days):", days);
    println!("  Agents alive:  {}", post["agents_alive"].as_u64().unwrap_or(0));
    println!("  Plant biomass: {:.0} kg", post["plant_biomass_kg"].as_f64().unwrap_or(0.0));
    println!("  Invert biomass: {:.0} kg", post["invert_biomass_kg"].as_f64().unwrap_or(0.0));
    println!("  Carcass biomass: {:.0} kg", post["carcass_biomass_kg"].as_f64().unwrap_or(0.0));
    println!("  Species:       {}", post["species_counts"].as_object().map(|m| m.len()).unwrap_or(0));
    println!("{}", "=".repeat(60));
}
