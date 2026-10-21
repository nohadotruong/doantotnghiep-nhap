from typing import List, Tuple
import math


def compare_methods(start: Tuple[int, int], end: Tuple[int, int]) -> dict:
    return {
        "incremental_traversal": get_line_grid_incremental_traversal(start, end),
        "parametric_discretization": get_line_grid_parametric_discretization(
            start, end
        ),
        "bresenham": get_line_grid_bresenham(start, end),
        "runs_of_runs": get_line_grid_runs_of_runs(start, end),
    }


def get_line_grid_bresenham(
    start: Tuple[int, int], end: Tuple[int, int]
) -> List[Tuple[int, int]]:
    (x1, y1) = (int(start[0]), int(start[1]))
    (x2, y2) = (int(end[0]), int(end[1]))
    cells = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    step_x = 1 if x2 > x1 else -1
    step_y = 1 if y2 > y1 else -1
    if dx > dy:
        error = dy - dx
        y = y1
        for x in range(x1, x2 + step_x, step_x):
            cells.append((x, y))
            if error >= 0:
                y += step_y
                error -= dx
            error += dy
    else:
        error = dx - dy
        x = x1
        for y in range(y1, y2 + step_y, step_y):
            cells.append((x, y))
            if error >= 0:
                x += step_x
                error -= dy
            error += dx
    return cells


def get_line_grid_incremental_traversal(
    start: Tuple[int, int], end: Tuple[int, int]
) -> List[Tuple[int, int]]:
    (x1, y1) = start
    (x2, y2) = end
    cells = []
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return [start]
    step_x = 1 if dx > 0 else -1 if dx < 0 else 0
    step_y = 1 if dy > 0 else -1 if dy < 0 else 0
    dx = abs(dx)
    dy = abs(dy)
    if dx != 0:
        t_delta_x = 1.0 / dx
        if step_x > 0:
            t_max_x = (math.ceil(x1) - x1) * t_delta_x
            if abs(t_max_x) < 1e-10:
                t_max_x = t_delta_x
        else:
            t_max_x = (x1 - math.floor(x1)) * t_delta_x
            if abs(t_max_x) < 1e-10:
                t_max_x = t_delta_x
    else:
        t_delta_x = float("inf")
        t_max_x = float("inf")
    if dy != 0:
        t_delta_y = 1.0 / dy
        if step_y > 0:
            t_max_y = (math.ceil(y1) - y1) * t_delta_y
            if abs(t_max_y) < 1e-10:
                t_max_y = t_delta_y
        else:
            t_max_y = (y1 - math.floor(y1)) * t_delta_y
            if abs(t_max_y) < 1e-10:
                t_max_y = t_delta_y
    else:
        t_delta_y = float("inf")
        t_max_y = float("inf")
    (x, y) = (x1, y1)
    cells.append((x, y))
    while x != x2 or y != y2:
        if abs(t_max_x - t_max_y) < 1e-10:
            cells.append((x + step_x, y))
            cells.append((x, y + step_y))
            t_max_x += t_delta_x
            t_max_y += t_delta_y
            x += step_x
            y += step_y
        elif t_max_x < t_max_y:
            t_max_x += t_delta_x
            x += step_x
        else:
            t_max_y += t_delta_y
            y += step_y
        cells.append((x, y))
    return cells


def get_line_grid_parametric_discretization(
    start: Tuple[float, float], end: Tuple[float, float]
) -> List[Tuple[int, int]]:
    (x1, y1) = start
    (x2, y2) = end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return [(int(x1), int(y1))]
    t_values = [0.0, 1.0]
    if dx != 0:
        for k in range(int(min(x1, x2)), int(max(x1, x2)) + 2):
            t = (k + (0.5 if dx > 0 else -0.5) - x1) / dx
            if 0 <= t <= 1:
                t_values.append(t)
    if dy != 0:
        for k in range(int(min(y1, y2)), int(max(y1, y2)) + 2):
            t = (k + (0.5 if dy > 0 else -0.5) - y1) / dy
            if 0 <= t <= 1:
                t_values.append(t)
    t_values = sorted(set(t_values))
    cells = []
    for i in range(len(t_values) - 1):
        t_mid = (t_values[i] + t_values[i + 1]) / 2.0
        x = x1 + dx * t_mid
        y = y1 + dy * t_mid
        cell = (math.floor(x), math.floor(y))
        if not cells or cells[-1] != cell:
            cells.append(cell)
    endpoint = (math.floor(x2), math.floor(y2))
    if not cells or cells[-1] != endpoint:
        cells.append(endpoint)
    return cells


def get_line_grid_runs_of_runs(
    start: Tuple[int, int], end: Tuple[int, int]
) -> List[Tuple[int, int]]:
    (x1, y1) = (int(start[0]), int(start[1]))
    (x2, y2) = (int(end[0]), int(end[1]))
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return [(x1, y1)]
    if dx == 0:
        cells = []
        step = 1 if dy > 0 else -1
        for y in range(y1, y2 + step, step):
            cells.append((x1, y))
        return cells
    if dy == 0:
        cells = []
        step = 1 if dx > 0 else -1
        for x in range(x1, x2 + step, step):
            cells.append((x, y1))
        return cells
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    step_x = 1 if dx > 0 else -1
    step_y = 1 if dy > 0 else -1
    (x, y) = (x1, y1)
    cells = [(x, y)]
    if abs_dx >= abs_dy:
        major_len = abs_dx
        minor_len = abs_dy
        alpha = minor_len / major_len
        r = int(1.0 / alpha) if alpha > 0 else major_len
        psi = 1.0 - alpha * r
        nu = alpha * (r + 1) - 1.0
        beta = 0.0
        steps_major = 0
        while steps_major < major_len:
            if beta >= psi:
                run_len = r
                beta -= psi
            else:
                run_len = r + 1
                beta += nu
            run_len = min(run_len, major_len - steps_major)
            for _ in range(run_len):
                x += step_x
                cells.append((x, y))
            if steps_major + run_len < major_len:
                y += step_y
            steps_major += run_len
    else:
        major_len = abs_dy
        minor_len = abs_dx
        alpha = minor_len / major_len
        r = int(1.0 / alpha) if alpha > 0 else major_len
        psi = 1.0 - alpha * r
        nu = alpha * (r + 1) - 1.0
        beta = 0.0
        steps_major = 0
        while steps_major < major_len:
            if beta >= psi:
                run_len = r
                beta -= psi
            else:
                run_len = r + 1
                beta += nu
            run_len = min(run_len, major_len - steps_major)
            for _ in range(run_len):
                y += step_y
                cells.append((x, y))
            if steps_major + run_len < major_len:
                x += step_x
            steps_major += run_len
    if (x, y) != (x2, y2):
        cells.append((x2, y2))
    return cells
