import numpy as np
from numba import njit
from heapq import heappush, heappop

from sim.grid import TerrainGrid


@njit(cache=True)
def _heuristic(ax: int, ay: int, bx: int, by: int) -> float:
    dx = ax - bx
    dy = ay - by
    return np.sqrt(float(dx * dx + dy * dy))


@njit(cache=True)
def _neighbors_numba(
    x: int,
    y: int,
    width: int,
    height: int,
    cost_arr: np.ndarray,
) -> list[tuple[int, int, float]]:
    result = []
    for dx, dy in [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            move_cost = cost_arr[ny, nx]
            if dx != 0 and dy != 0:
                move_cost *= 1.414
            result.append((nx, ny, move_cost))
    return result


def a_star(
    grid: TerrainGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
    max_steps: int = 5000,
) -> list[tuple[int, int]] | None:
    cost_arr = grid.get_cost_array()
    height, width = cost_arr.shape
    return _a_star_numba(
        start[0],
        start[1],
        goal[0],
        goal[1],
        width,
        height,
        cost_arr,
        max_steps,
    )


@njit(cache=True)
def _a_star_numba(
    sx: int,
    sy: int,
    gx: int,
    gy: int,
    width: int,
    height: int,
    cost_arr: np.ndarray,
    max_steps: int,
) -> list[tuple[int, int]] | None:
    open_set = [(0.0, sx, sy)]
    came_from = np.full((height, width, 2), -1, dtype=np.int32)
    g_score = np.full((height, width), 1e18, dtype=np.float64)
    f_score = np.full((height, width), 1e18, dtype=np.float64)
    in_open = np.zeros((height, width), dtype=np.int8)

    g_score[sy, sx] = 0.0
    f_score[sy, sx] = _heuristic(sx, sy, gx, gy)
    in_open[sy, sx] = 1

    steps = 0
    while open_set and steps < max_steps:
        _, cx, cy = heappop(open_set)
        in_open[cy, cx] = 0
        steps += 1

        if cx == gx and cy == gy:
            path = [(gx, gy)]
            px, py = gx, gy
            while not (px == sx and py == sy):
                px, py = came_from[py, px]
                path.append((px, py))
            path.reverse()
            return path

        for nx, ny, move_cost in _neighbors_numba(cx, cy, width, height, cost_arr):
            tentative = g_score[cy, cx] + move_cost
            if tentative < g_score[ny, nx]:
                came_from[ny, nx, 0] = cx
                came_from[ny, nx, 1] = cy
                g_score[ny, nx] = tentative
                f = tentative + _heuristic(nx, ny, gx, gy)
                f_score[ny, nx] = f
                if not in_open[ny, nx]:
                    heappush(open_set, (f, nx, ny))
                    in_open[ny, nx] = 1

    return None


def compute_path_cost(
    grid: TerrainGrid,
    path: list[tuple[int, int]],
) -> float:
    total = 0.0
    for x, y in path:
        total += grid.cells[y][x].cost_a_star
    return total


def astar_batch(
    grid: TerrainGrid,
    starts: list[tuple[int, int]],
    goals: list[tuple[int, int]],
) -> list[list[tuple[int, int]] | None]:
    return [a_star(grid, s, g) for s, g in zip(starts, goals)]
