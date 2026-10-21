from typing import List, Tuple

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

    # Check cells within search_radius only (much faster)
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

    # Check if it's a diagonal move (both dx and dy are 1)
    if dx == 1 and dy == 1:
        # Check the two corner positions
        corner1 = (x1, y2)  # (x, y+1) or (x, y-1)
        corner2 = (x2, y1)  # (x+1, y) or (x-1, y)

        # If both corners are obstacles, diagonal move is blocked
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
    # Get all cells along the line
    cells = bresenham_line(p1, p2)

    # Check for direct collision
    for x, y in cells:
        if grid.is_obstacle(x, y):
            return True

    # Check for clearance violation (with optimized search radius)
    for x, y in cells:
        min_dist = min_distance_to_obstacle(grid, (x, y), search_radius=2)
        if min_dist < clearance:
            return True

    # Check for diagonal corner cutting
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
