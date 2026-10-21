from environment.grid_map import GridMap
from typing import Tuple
import math


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def _bresenham_line(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
) -> list[Tuple[int, int]]:
    x0, y0 = int(round(p1[0])), int(round(p1[1]))
    x1, y1 = int(round(p2[0])), int(round(p2[1]))

    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1

    if dx > dy:
        err = dx / 2
        y = y0
        for x in range(x0, x1 + sx, sx):
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:
        err = dy / 2
        x = x0
        for y in range(y0, y1 + sy, sy):
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy

    return points


def has_line_of_sight(
    grid: GridMap,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
) -> bool:
    from utils_new.map_utils import is_obstacle

    line_cells = _bresenham_line(p1, p2)

    for x, y in line_cells:
        if is_obstacle(grid, x, y):
            return False

    return True


def check_corner_collision(
    grid: GridMap,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
) -> bool:
    from utils_new.map_utils import is_obstacle

    x0, y0 = int(round(p1[0])), int(round(p1[1]))
    x1, y1 = int(round(p2[0])), int(round(p2[1]))

    dx = x1 - x0
    dy = y1 - y0

    if dx == 0 or dy == 0:
        return False

    diagonal_cells = [(x0 + dx, y0), (x0, y0 + dy)]

    for cell in diagonal_cells:
        if is_obstacle(grid, cell[0], cell[1]):
            return True

    return False
