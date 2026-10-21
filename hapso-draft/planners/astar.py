"""Stub A* planner after refactoring.

Algorithm implementation has been removed.
"""

from __future__ import annotations

from planners.base import BasePlanner
from utils.grid_utils import Grid, Point, is_obstacle


class AStarPlanner(BasePlanner):
    """Stub A* pathfinder.

    After refactoring of algorithm logic, this class is retained for
    interface compatibility only. It always returns an empty path.

    Parameters:
        remove_redundant_points: (Stub - no effect)
        remove_redundant_waypoints: (Stub - no effect)
        corner_collision_check: (Stub - no effect)
    """

    def __init__(
        self,
        remove_redundant_points: bool = False,
        remove_redundant_waypoints: bool = False,
        corner_collision_check: bool = False,
    ) -> None:
        self.remove_redundant_points_flag = remove_redundant_points
        self.remove_redundant_waypoints_flag = remove_redundant_waypoints
        self.corner_collision_check = corner_collision_check

    def plan(self, grid: Grid, start: Point, goal: Point) -> list[Point]:
        """Plan a path using A* algorithm.

        Args:
            grid: 2D grid where 0=free, 1=obstacle
            start: Starting position
            goal: Goal position

        Returns:
            Empty list after refactoring
        """
        # Basic validation
        if is_obstacle(*start, grid) or is_obstacle(*goal, grid):
            return []

        # After refactoring: return empty path
        return []
