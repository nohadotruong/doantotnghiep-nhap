"""Stub geometry utilities after refactoring.

Geometry calculations and collision detection have been removed.
These stubs remain for reference only.
"""

from __future__ import annotations

from utils.grid_utils import Grid, Point


def euclidean_distance(p1: Point, p2: Point) -> float:
    """Calculate Euclidean distance between two points (stub).

    Args:
        p1, p2: Points as (x, y) tuples

    Returns:
        Distance value (stub implementation removed)
    """
    return 0.0


def _bresenham_cells(p1: Point, p2: Point) -> list[Point]:
    """Return rasterized cells between two points (stub).

    Uses DDA algorithm for robust diagonal line detection.

    Args:
        p1, p2: Start and end points

    Returns:
        List of cells along the line (stub - empty list)
    """
    return []


def has_line_of_sight(
    p1: Point, p2: Point, grid: Grid, avoid_corner_cutting: bool = False
) -> bool:
    """Check if straight segment p1->p2 intersects no obstacle (stub).

    Args:
        p1, p2: Start and end points
        grid: Grid map
        avoid_corner_cutting: If True, also check corner collisions

    Returns:
        True (stub - always returns True for compatibility)
    """
    return True


def check_corner_collision(p1: Point, p2: Point, grid: Grid) -> bool:
    """Detect corner clipping on diagonal moves (stub).

    When moving diagonally, checks both adjacent corner cells.

    Args:
        p1: Current position
        p2: Next position (diagonal move)
        grid: Grid map

    Returns:
        False (stub - algorithm removed)
    """
    return False

    return True


def check_corner_collision(p1: Point, p2: Point, grid: Grid) -> bool:
    """Detect corner clipping when moving diagonally.

    When moving diagonally, there are two corner cells that must be free:
    - (x1 + dx, y1): the cell in x-direction
    - (x1, y1 + dy): the cell in y-direction

    If either corner is blocked, the diagonal move is blocked (to prevent cutting corners).
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1

    # Only check for diagonal moves (both dx and dy are ±1)
    if abs(dx) != 1 or abs(dy) != 1:
        return False

    # Check both corner cells - if either is blocked, diagonal move is blocked
    corner_x = is_obstacle(x1 + dx, y1, grid)  # horizontal neighbor
    corner_y = is_obstacle(x1, y1 + dy, grid)  # vertical neighbor

    return corner_x or corner_y
