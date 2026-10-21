from typing import List, Optional, Tuple
import math
import numpy as np

import numpy as np

def bresenham_line(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> List[Tuple[int, int]]:
    x0, y0 = int(p1[0]), int(p1[1])
    x1, y1 = int(p2[0]), int(p2[1])

    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:

        err = dx / 2
        y = y0
        for x in range(x0, x1 + sx, sx):
            cells.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:

        err = dy / 2
        x = x0
        for y in range(y0, y1 + sy, sy):
            cells.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy

    return cells

def dda_line(p1: Tuple[float, float], p2: Tuple[float, float]) -> List[Tuple[int, int]]:
    x0, y0 = int(p1[0]), int(p1[1])
    x1, y1 = int(p2[0]), int(p2[1])

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1

    cells = []

    if dx == 0 and dy == 0:
        return [(x0, y0)]

    if dx == 0:

        for y in range(y0, y1 + sy, sy):
            cells.append((x0, y))
        return cells

    if dy == 0:

        for x in range(x0, x1 + sx, sx):
            cells.append((x, y0))
        return cells

    if dx >= dy:

        y = y0
        err = dx / 2.0
        for x in range(x0, x1 + sx, sx):
            cells.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx

                if (x + sx, y - sy) != (x, y):
                    cells.append((x + sx, y - sy))
    else:

        x = x0
        err = dy / 2.0
        for y in range(y0, y1 + sy, sy):
            cells.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy

                if (x - sx, y + sy) != (x, y):
                    cells.append((x - sx, y + sy))

    seen = set()
    result = []
    for cell in cells:
        if cell not in seen:
            seen.add(cell)
            result.append(cell)

    return result

def voxel_traversal_line(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> List[Tuple[int, int]]:
    return dda_line(p1, p2)

def supercover_voxels(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> List[Tuple[int, int]]:
    x0, y0 = int(p1[0]), int(p1[1])
    x1, y1 = int(p2[0]), int(p2[1])

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    if x0 < x1:
        sx = 1
    else:
        sx = -1

    if y0 < y1:
        sy = 1
    else:
        sy = -1

    cells = set()

    if dx == 0:

        for y in range(y0, y1 + sy, sy):
            cells.add((x0, y))
    elif dy == 0:

        for x in range(x0, x1 + sx, sx):
            cells.add((x, y0))
    elif dx == dy:

        x, y = x0, y0
        while True:
            cells.add((x, y))
            if x == x1:
                break
            x += sx
            y += sy
    else:

        cells.add((x0, y0))
        cells.add((x1, y1))

        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                if x0 == x1:
                    if x == x0 and min(y0, y1) <= y <= max(y0, y1):
                        cells.add((x, y))
                elif y0 == y1:
                    if y == y0 and min(x0, x1) <= x <= max(x0, x1):
                        cells.add((x, y))
                else:

                    for t in [0, 0.25, 0.5, 0.75, 1.0]:
                        px = x0 + t * (x1 - x0)
                        py = y0 + t * (y1 - y0)
                        if x <= px < x + 1 and y <= py < y + 1:
                            cells.add((x, y))
                            break

    return sorted(list(cells))

def calculate_path_length(path: List[Tuple[float, float]]) -> float:
    length = 0.0
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]
        length += euclidean_distance(p1, p2)

    return length

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)

def calculate_path_smoothness(path: List[Tuple[float, float]]) -> float:
    if len(path) < 3:
        return 0.0

    penalty = 0.0

    for i in range(1, len(path) - 1):
        p1 = np.array(path[i - 1], dtype=float)
        p2 = np.array(path[i], dtype=float)
        p3 = np.array(path[i + 1], dtype=float)

        v1 = p1 - p2
        v2 = p3 - p2

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 > 1e-6 and norm2 > 1e-6:
            v1 /= norm1
            v2 /= norm2

            dot_product = np.clip(np.dot(v1, v2), -1, 1)
            angle = math.acos(dot_product)
            penalty += angle

    return penalty

def check_collision_line(
    grid, p1: Tuple[float, float], p2: Tuple[float, float]
) -> bool:
    cells = voxel_traversal_line(p1, p2)

    for x, y in cells:

        if 0 <= x < grid.width and 0 <= y < grid.height:
            if grid.is_obstacle(x, y):
                return True
        else:

            return True

    return False

def has_corner_obstacle(grid, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
    x1, y1 = int(round(p1[0])), int(round(p1[1]))
    x2, y2 = int(round(p2[0])), int(round(p2[1]))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dx == 1 and dy == 1:

        if grid.is_obstacle(x1, y2) or grid.is_obstacle(x2, y1):
            return True

    return False

def min_distance_to_obstacle(
    grid, point: Tuple[float, float], search_radius: int = 5
) -> float:
    px, py = int(round(point[0])), int(round(point[1]))
    min_dist = float("inf")

    for x in range(max(0, px - search_radius), min(grid.width, px + search_radius + 1)):
        for y in range(
            max(0, py - search_radius), min(grid.height, py + search_radius + 1)
        ):
            if grid.is_obstacle(x, y):
                dist = euclidean_distance(point, (x, y))
                min_dist = min(min_dist, dist)

    return min_dist

def _check_diagonal_corner_collision(
    grid, p1: Tuple[float, float], p2: Tuple[float, float]
) -> bool:
    x1, y1 = int(round(p1[0])), int(round(p1[1]))
    x2, y2 = int(round(p2[0])), int(round(p2[1]))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dx == 1 and dy == 1:

        corner1 = (x1, y2)
        corner2 = (x2, y1)

        if grid.is_obstacle(corner1[0], corner1[1]) and grid.is_obstacle(
            corner2[0], corner2[1]
        ):
            return True

    return False

def check_collision_line_with_clearance(
    grid, p1: Tuple[float, float], p2: Tuple[float, float], clearance: float = 1.0
) -> bool:

    cells = voxel_traversal_line(p1, p2)

    for x, y in cells:
        if grid.is_obstacle(x, y):
            return True

    for x, y in cells:
        min_dist = min_distance_to_obstacle(grid, (x, y), search_radius=2)
        if min_dist < clearance:
            return True

    if _check_diagonal_corner_collision(grid, p1, p2):
        return True

    return False

def calculate_path_metrics(grid, path: List[Tuple[float, float]]) -> dict:
    metrics = {
        "length": calculate_path_length(path),
        "smoothness": calculate_path_smoothness(path),
        "waypoint_count": len(path),
        "has_collision": False,
    }

    for i in range(len(path) - 1):
        if check_collision_line(grid, path[i], path[i + 1]):
            metrics["has_collision"] = True
            break

    return metrics

def remove_redundant_points(
    path: List[Tuple[float, float]], direction_tolerance: float = 1e-4
) -> List[Tuple[float, float]]:
    if len(path) <= 2:
        return path

    cleaned: List[Tuple[float, float]] = [path[0]]
    prev_dir: Optional[Tuple[float, float]] = None

    for i in range(1, len(path)):
        dx = path[i][0] - cleaned[-1][0]
        dy = path[i][1] - cleaned[-1][1]
        norm = math.hypot(dx, dy)

        if norm < 1e-9:
            continue

        curr_dir = (dx / norm, dy / norm)

        if prev_dir is not None:
            dot = prev_dir[0] * curr_dir[0] + prev_dir[1] * curr_dir[1]
            if dot > 1 - direction_tolerance:
                cleaned[-1] = path[i]
                prev_dir = curr_dir
                continue

        cleaned.append(path[i])
        prev_dir = curr_dir

    return cleaned

def remove_redundant_transitions(
    grid, path: List[Tuple[float, float]], avoid_corner_cutting: bool = False
):
    if len(path) <= 2:
        return path

    cleaned = [path[0]]
    i = 1

    while i < len(path) - 1:

        has_collision = check_collision_line(grid, cleaned[-1], path[i + 1])

        skip_waypoint = not has_collision

        if skip_waypoint and avoid_corner_cutting:

            has_corner = has_corner_obstacle(grid, cleaned[-1], path[i + 1])
            skip_waypoint = not has_corner

        if not skip_waypoint:
            cleaned.append(path[i])

        i += 1

    cleaned.append(path[-1])
    return cleaned