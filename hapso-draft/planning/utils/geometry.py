"""
Geometry utilities for path planning.

Provides distance calculations, line-of-sight checks, and collision detection.
"""

from typing import List, Tuple
import math

import planning.api as plan_api


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def manhattan_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Manhattan distance between two points."""
    return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])


def has_line_of_sight(
    grid: plan_api.Grid, p1: Tuple[int, int], p2: Tuple[int, int]
) -> bool:
    """
    Check if there's line-of-sight between two points (no obstacles blocking).

    Uses Bresenham's line algorithm for efficient traversal.
    """
    x0, y0 = p1
    x1, y1 = p2

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1

    if dx > dy:
        err = dx / 2.0
        y = y0
        for x in range(x0, x1 + sx, sx):
            if grid.is_obstacle(x, y):
                return False
            err -= dy
            if err < 0:
                y += sy
                err += dx
    else:
        err = dy / 2.0
        x = x0
        for y in range(y0, y1 + sy, sy):
            if grid.is_obstacle(x, y):
                return False
            err -= dx
            if err < 0:
                x += sx
                err += dy

    return True


def check_corner_collision(
    grid: plan_api.Grid, p1: Tuple[int, int], p2: Tuple[int, int]
) -> bool:
    """
    Check if diagonal movement from p1 to p2 cuts corners (steps on obstacles).

    For diagonal moves like (x, y) -> (x+1, y+1), check if cells (x+1, y) or (x, y+1) are obstacles.

    Returns:
        True if corner collision detected, False if movement is safe
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    # Only check diagonal moves
    if abs(dx) != 1 or abs(dy) != 1:
        return False

    # Check the two adjacent cells
    is_blocked = grid.is_obstacle(p1[0] + dx, p1[1]) or grid.is_obstacle(
        p1[0], p1[1] + dy
    )

    return is_blocked


def path_length(path: List[Tuple[float, float]]) -> float:
    """Calculate total Euclidean path length."""
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        total += euclidean_distance(path[i], path[i + 1])

    return total


def path_smoothness(path: List[Tuple[float, float]]) -> float:
    """
    Calculate total rotation (sum of turning angles).

    Lower values indicate smoother paths.
    """
    if len(path) < 3:
        return 0.0

    total_rotation = 0.0

    for i in range(1, len(path) - 1):
        # Vector from i-1 to i
        v1_x = path[i][0] - path[i - 1][0]
        v1_y = path[i][1] - path[i - 1][1]
        len1 = math.sqrt(v1_x * v1_x + v1_y * v1_y)

        # Vector from i to i+1
        v2_x = path[i + 1][0] - path[i][0]
        v2_y = path[i + 1][1] - path[i][1]
        len2 = math.sqrt(v2_x * v2_x + v2_y * v2_y)

        if len1 > 0 and len2 > 0:
            # Dot product and cross product for angle
            dot = v1_x * v2_x + v1_y * v2_y
            cross = v1_x * v2_y - v1_y * v2_x

            angle = abs(math.atan2(cross, dot))
            total_rotation += angle

    return total_rotation


__all__ = [
    "euclidean_distance",
    "manhattan_distance",
    "has_line_of_sight",
    "check_corner_collision",
    "path_length",
    "path_smoothness",
]
