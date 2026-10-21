from typing import List, Optional, Tuple

import math
import numpy as np


def bresenham_line(
    p1: Tuple[float, float], p2: Tuple[float, float]
) -> List[Tuple[int, int]]:
    x0, y0 = int(round(p1[0])), int(round(p1[1]))
    x1, y1 = int(round(p2[0])), int(round(p2[1]))

    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    if dx > dy:
        err = dx / 2.0
        y = y0
        for x in range(x0, x1 + sx, sx):
            cells.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:
        err = dy / 2.0
        x = x0
        for y in range(y0, y1 + sy, sy):
            cells.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy

    return cells


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
    cells = bresenham_line(p1, p2)

    for x, y in cells:
        if grid.is_obstacle(x, y):
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


def min_distance_to_obstacle(
    grid, point: Tuple[float, float], search_radius: int = 5
) -> float:
    """
    Calculate minimum distance from a point to the nearest obstacle within search radius.
    OPTIMIZED: Only checks nearby cells instead of entire grid.

    Args:
        grid: The grid map
        point: The point (x, y)
        search_radius: Search radius around point (default 5)

    Returns:
        Minimum distance to obstacle
    """
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
    """
    Check if a diagonal move would cut through obstacle corners.

    For diagonal moves like (x, y) -> (x+1, y+1), check corners at (x, y+1) and (x+1, y).
    This prevents corner cutting when moving diagonally.

    Args:
        grid: The grid map
        p1: Start point
        p2: End point

    Returns:
        True if corner collision detected
    """
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
    """
    Check if a line segment collides with obstacles or violates clearance margin.
    Also checks for diagonal corner cutting.

    Args:
        grid: The grid map
        p1: Start point
        p2: End point
        clearance: Minimum safe distance from obstacles

    Returns:
        True if collision, clearance violation, or corner cutting detected
    """

    cells = bresenham_line(p1, p2)

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
    """Remove collinear waypoints that keep the same heading."""
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


def remove_redundant_transitions(grid, path: List[Tuple[float, float]]):
    """Drop intermediate waypoints when straight-line travel is obstacle-free."""
    if len(path) <= 2:
        return path

    cleaned = [path[0]]
    i = 1

    while i < len(path) - 1:
        if check_collision_line(grid, cleaned[-1], path[i + 1]):
            cleaned.append(path[i])
            i += 1
            continue

        i += 1

    cleaned.append(path[-1])
    return cleaned


def calculate_angle_metrics(path: List[Tuple[float, float]]) -> dict:
    """Calculate turning angles between consecutive path segments."""
    metrics = {
        "max_angle": 0.0,
        "avg_angle": 0.0,
        "total_angle": 0.0,
    }

    if len(path) < 3:
        return metrics

    angles = []

    for i in range(1, len(path) - 1):
        # Vectors from point i-1 to i, and from i to i+1
        v1_x = path[i][0] - path[i - 1][0]
        v1_y = path[i][1] - path[i - 1][1]

        v2_x = path[i + 1][0] - path[i][0]
        v2_y = path[i + 1][1] - path[i][1]

        # Calculate magnitudes
        mag1 = math.hypot(v1_x, v1_y)
        mag2 = math.hypot(v2_x, v2_y)

        if mag1 < 1e-9 or mag2 < 1e-9:
            continue  # Skip if segment is too small

        # Calculate dot product and cross product
        dot = v1_x * v2_x + v1_y * v2_y
        cross = v1_x * v2_y - v1_y * v2_x

        # Calculate angle in degrees
        angle_rad = math.atan2(cross, dot)
        angle_deg = abs(math.degrees(angle_rad))

        angles.append(angle_deg)

    if angles:
        metrics["max_angle"] = max(angles)
        metrics["avg_angle"] = sum(angles) / len(angles)
        metrics["total_angle"] = sum(angles)

    return metrics
