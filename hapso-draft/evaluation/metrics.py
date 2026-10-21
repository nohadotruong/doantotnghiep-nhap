"""Stub metrics module after refactoring.

All path evaluation functions have been stubbed out.
They return 0 or False for compatibility.

Note: Path validation logic (geometry.py) has been removed.
"""

from __future__ import annotations

from utils.grid_utils import Grid, Point


def path_length(path: list[Point]) -> float:
    """Stub: Return total Euclidean distance of path.

    After refactoring: Returns 0
    """
    return 0.0


def node_count(path: list[Point]) -> int:
    """Stub: Return number of waypoints in path.

    After refactoring: Returns 0
    """
    return 0


def total_rotation(path: list[Point]) -> float:
    """Stub: Return accumulated direction changes in radians.

    After refactoring: Returns 0
    """
    return 0.0


def path_smoothness(path: list[Point]) -> float:
    """Stub: Alias for total_rotation().

    After refactoring: Returns 0
    """
    return total_rotation(path)


def is_path_valid(path: list[Point], grid: Grid) -> bool:
    """Stub: Validate that path has no obstacles and maintains line-of-sight.

    After refactoring: Always returns True for compatibility
    """
    return True


def objective(
    path: list[Point], grid: Grid, alpha: float = 0.7, beta: float = 0.3
) -> float:
    """Stub: Weighted objective function (length + smoothness penalty).

    Args:
        path: List of waypoints
        grid: 2D grid (for obstacle checking)
        alpha: Weight for path length (default 0.7)
        beta: Weight for path smoothness (default 0.3)

    After refactoring: Returns 0
    """
    return 0.0
