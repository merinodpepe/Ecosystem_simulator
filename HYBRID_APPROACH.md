# Python-Rust Hybrid Approach for Ecosystem Simulator

This document outlines a strategy to improve the performance of the Python-based ecosystem simulator by offloading compute-intensive mathematical operations to Rust while retaining Python's flexibility for agent behavior and simulation control.

## Current State

The project contains two implementations:
1. **Python** (`src/sim/`) - The main simulator with Numba JIT optimizations
2. **Rust** (`ecosystem_simulator_rs/`) - A standalone Rust version

While the Python version already uses Numba JIT for many mathematical operations (energy calculations, pathfinding, grid updates), profiling indicates that the primary performance bottlenecks remain in:
- Per-agent grid access in Python loops
- Agent iteration overhead
- Decision-making logic (though this is harder to optimize without losing flexibility)
- Object creation and attribute access overhead

## Hybrid Approach Philosophy

> "Rust does the math, Python controls the agents"

This means:
- **Rust**: Handles batch numerical operations on large arrays of agent/grid data
- **Python**: Manages agent decision logic, high-level simulation flow, and flexibility for experimentation

This approach gives us:
- Rust's performance for numerical computations (cache-friendly, vectorized, no GIL)
- Python's ease of modification for agent behaviors and simulation parameters
- Seamless data exchange via NumPy arrays (using PyO3)

## Implementation Plan

### 1. Create Rust Extension Module

Add PyO3 to `ecosystem_simulator_rs/Cargo.toml`:
```toml
[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
numpy = "0.17"  # For NumPy array interchange
# Keep existing dependencies...
```

Create a new Rust module (e.g., `src/ecosystem_math.rs`) for batch operations.

### 2. Identify Math Operations to Offload to Rust

Focus on **batch operations** that process many agents at once:

#### A. Batch Energy Updates
Instead of calling `daily_dee` per agent in Python, process all agents simultaneously:

```rust
// Pseudo-Rust interface for Python
#[pyfunction]
fn update_agent_energies_batch(
    agent_masses: &[f64],
    agent_energies: &mut [f64],
    agent_lactating: &[bool],
    grid_slopes: &[f64],  // Current slope for each agent
    hours_forage: f64,
    hours_loco: f64,
    hours_rest: f64,
    hours_other: f64,
    dt_hours: f64,
    is_cold: bool,
) {
    for i in 0..agent_masses.len() {
        let expended = daily_dee(
            agent_masses[i],
            hours_forage,
            hours_loco,
            hours_rest,
            hours_other,
            grid_slopes[i],
            is_cold,
            agent_lactating[i],
        );
        agent_energies[i] -= expended * (dt_hours / 24.0);
    }
}
```

#### B. Batch Foraging/Resource Consumption
Process all agents' feeding in one call:

```rust
#[pyfunction]
fn process_foraging_batch(
    agent_x: &[i32],
    agent_y: &[i32],
    agent_masses: &[f64],
    plant_biomass: &mut [f64],
    invert_biomass: &mut [f64],
    agent_energy_gain: &mut [f64],
    grid_width: i32,
    grid_height: i32,
) {
    for i in 0..agent_x.len() {
        let x = agent_x[i] as usize;
        let y = agent_y[i] as usize;
        if x < grid_width as usize && y < grid_height as usize {
            let idx = y * grid_width as usize + x;
            let available = plant_biomass[idx] + invert_biomass[idx];
            let intake = available.min(agent_masses[i] * 0.05);
            
            let plant_share = if available > 0.0 { 
                plant_biomass[idx] / available 
            } else { 0.0 };
            let invert_share = 1.0 - plant_share;
            
            // Update biomass pools (simplified)
            plant_biomass[idx] -= intake * plant_share * 0.5;
            plant_biomass[idx] -= intake * plant_share * 0.2;
            plant_biomass[idx] -= intake * plant_share * 0.3;
            invert_biomass[idx] -= intake * invert_share * 0.3;
            invert_biomass[idx] -= intake * invert_share * 0.5;
            invert_biomass[idx] -= intake * invert_share * 0.2;
            
            agent_energy_gain[i] = intake * 800.0 * 0.6;
        }
    }
}
```

#### C. Batch Neighborhood Searches
For movement decisions (e.g., herbivore's `look_for_best_cell`):

```rust
#[pyfunction]
fn find_best_cells_batch(
    agent_x: &[i32],
    agent_y: &[i32],
    agent_masses: &[f64],
    plant_biomass: &[f64],
    invert_biomass: &[f64],
    cost_a_star: &[f64],
    best_x: &mut [i32],
    best_y: &mut [i32],
    grid_width: i32,
    grid_height: i32,
    search_radius: i32,
) {
    for i in 0..agent_x.len() {
        let cx = agent_x[i];
        let cy = agent_y[i];
        let mut best_score = -1.0;
        let mut best_pos_x = cx;
        let mut best_pos_y = cy;
        
        for dy in -search_radius..=search_radius {
            for dx in -search_radius..=search_radius {
                let nx = cx + dx;
                let ny = cy + dy;
                if nx >= 0 && nx < grid_width && ny >= 0 && ny < grid_height {
                    let idx = (ny as usize) * grid_width as usize + nx as usize;
                    let score = plant_biomass[idx] + invert_biomass[idx] * 2.0;
                    let score = score / max(cost_a_star[idx], 0.1);
                    if score > best_score {
                        best_score = score;
                        best_pos_x = nx;
                        best_pos_y = ny;
                    }
                }
            }
        }
        best_x[i] = best_pos_x;
        best_y[i] = best_pos_y;
    }
}
```

### 3. Modify Python Agent Code

Update agents to collect data, call Rust batch functions, then apply results:

```python
# In src/sim/agents/base.py - Example modification
def step(
    self,
    grid: TerrainGrid,
    dt_hours: float = 24.0,
) -> list[AgentAction]:
    if not self.state.alive:
        return []

    # Decision-making stays in Python (flexibility preserved)
    actions = self._decide_actions(grid)
    self._execute_actions(actions, grid, dt_hours)
    
    # Math-heavy updates delegated to Rust batch processors
    # (Called externally on all agents)
    self._update_biology(dt_hours)
    self._check_death(grid)
    return actions

# External batch processor (called from simulation loop)
def update_agents_batch(agents, grid, dt_hours, rust_interface):
    # Extract agent data into arrays
    masses = np.array([a.mass_kg for a in agents], dtype=np.float64)
    energies = np.array([a.state.energy_kcal for a in agents], dtype=np.float64)
    lactating = np.array([a.state.is_lactating for a in agents], dtype=np.bool_)
    # ... similarly for positions, etc.
    
    # Call Rust batch functions
    rust_interface.update_agent_energies_batch(
        masses, energies, lactating, 
        grid_slopes, hours_forage, hours_loco, 
        hours_rest, hours_other, dt_hours, is_cold
    )
    
    # Apply results back to agents
    for i, agent in enumerate(agents):
        agent.state.energy_kcal = float(energies[i])
        # ... update other fields
```

### 4. Benefits

| Aspect | Rust Contribution | Python Contribution |
|--------|-------------------|---------------------|
| **Performance** | Batch numerical ops, cache efficiency, no GIL | - |
| **Flexibility** | - | Agent行为, 高级逻辑, 实验 |
| **Development Speed** | - | 快速迭代, 调试, 原型 |
| **Maintainability** | 数学内核 (stable) | 行为逻辑 (evolving) |

### 5. Immediate Next Steps

1. **Profile Current Python Version**  
   Use `cProfile` or `line_profiler` to confirm exact bottlenecks before optimizing.

2. **Create Minimal PyO3 Extension**  
   Start with a simple batch energy function to verify the build/call workflow.

3. **Implement One Batch Operation**  
   Begin with energy updates (most frequently called) and measure performance gain.

4. **Gradually Migrate Operations**  
   Move foraging, neighborhood searches, and grid updates as needed.

5. **Maintain API Compatibility**  
   Ensure the Python-facing agent interface remains unchanged for existing workflows.

## Files to Modify/Create

- `ecosystem_simulator_rs/Cargo.toml` → Add PyO3 dependencies
- `ecosystem_simulator_rs/src/lib.rs` or new `ecosystem_math.rs` → Implement batch functions
- `src/sim/agents/base.py` → Modify agent step method and add batch helpers
- `src/sim/simulation.py` → Update simulation loop to use batch processors
- `pyproject.toml` → Add build dependencies if using maturin

## Conclusion

This hybrid approach strategically uses Rust for what it does best (high-performance numerical computing) while keeping Python for what it does best (flexible, rapid development of complex behaviors). By focusing on batch operations, we minimize data transfer overhead and maximize the performance gains from Rust.

Start with the most frequently called mathematical operations (energy calculations) and iterate based on profiling results. The goal is not to rewrite everything in Rust, but to selectively accelerate the hotspots that limit simulation scale and speed.