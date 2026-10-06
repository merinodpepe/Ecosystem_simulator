use std::cmp::Reverse;
use std::collections::BinaryHeap;

use ordered_float::OrderedFloat;

use super::grid::TerrainGrid;

fn heuristic(ax: i32, ay: i32, bx: i32, by: i32) -> f64 {
    let dx = (ax - bx) as f64;
    let dy = (ay - by) as f64;
    (dx * dx + dy * dy).sqrt()
}

fn neighbors_numba(
    x: i32,
    y: i32,
    width: i32,
    height: i32,
    cost_arr: &[f64],
) -> [(i32, i32, f64); 8] {
    let mut result: [(i32, i32, f64); 8] = [(0, 0, 0.0); 8];
    let mut count = 0;
    let offsets: [(i32, i32); 8] = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ];
    for (dx, dy) in offsets {
        let nx = x + dx;
        let ny = y + dy;
        if nx >= 0 && nx < width && ny >= 0 && ny < height {
            let idx = (ny * width + nx) as usize;
            let mut move_cost = cost_arr[idx];
            if dx != 0 && dy != 0 {
                move_cost *= 1.414;
            }
            result[count] = (nx, ny, move_cost);
            count += 1;
        }
    }
    for i in count..8 {
        result[i] = (-1, -1, f64::INFINITY);
    }
    result
}

pub fn a_star_path(
    grid: &TerrainGrid,
    start: (i32, i32),
    goal: (i32, i32),
    max_steps: u32,
) -> Option<Vec<(i32, i32)>> {
    let width = grid.width as i32;
    let height = grid.height as i32;
    let size = (width * height) as usize;

    let cost_arr = grid.cost_array();

    let (sx, sy) = start;
    let (gx, gy) = goal;

    let start_idx = (sy * width + sx) as usize;
    let goal_idx = (gy * width + gx) as usize;

    let mut open_set: BinaryHeap<Reverse<(OrderedFloat<f64>, u32)>> = BinaryHeap::new();
    let mut came_from = vec![-1i32; size];
    let mut g_score = vec![f64::INFINITY; size];
    let mut f_score = vec![f64::INFINITY; size];
    let mut in_open = vec![false; size];

    g_score[start_idx] = 0.0;
    f_score[start_idx] = heuristic(sx, sy, gx, gy);
    open_set.push(Reverse((OrderedFloat(f_score[start_idx]), start_idx as u32)));
    in_open[start_idx] = true;

    let mut steps = 0u32;

    while let Some(Reverse((_f, idx))) = open_set.pop() {
        let idx = idx as usize;
        let cx = (idx % width as usize) as i32;
        let cy = (idx / width as usize) as i32;

        if steps >= max_steps {
            return None;
        }
        steps += 1;

        if cx == gx && cy == gy {
            let mut path = Vec::new();
            let mut current = goal_idx;
            path.push((gx, gy));
            while current != start_idx {
                let parent = came_from[current] as usize;
                let px = (parent % width as usize) as i32;
                let py = (parent / width as usize) as i32;
                path.push((px, py));
                current = parent;
            }
            path.reverse();
            return Some(path);
        }

        let neighbors = neighbors_numba(cx, cy, width, height, &cost_arr);
        for (nx, ny, move_cost) in neighbors {
            if nx == -1 {
                break;
            }
            let nidx = (ny * width + nx) as usize;
            let tentative = g_score[idx] + move_cost;
            if tentative < g_score[nidx] {
                came_from[nidx] = idx as i32;
                g_score[nidx] = tentative;
                let f = tentative + heuristic(nx, ny, gx, gy);
                f_score[nidx] = f;
                if !in_open[nidx] {
                    open_set.push(Reverse((OrderedFloat(f), nidx as u32)));
                    in_open[nidx] = true;
                }
            }
        }
    }

    None
}

pub fn compute_path_cost(grid: &TerrainGrid, path: &[(i32, i32)]) -> f64 {
    let mut total = 0.0;
    for (x, y) in path {
        total += grid.cell(*x as u32, *y as u32).cost_a_star;
    }
    total
}
