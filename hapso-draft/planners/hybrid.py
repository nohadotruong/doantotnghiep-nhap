"""Stub hybrid planner after refactoring.

Algorithm implementation has been removed.
"""

from __future__ import annotations

from planners.base import BasePlanner
from utils.grid_utils import Grid, Point


class HybridPlanner(BasePlanner):
    """Stub hybrid planner combining planner + optimizer (stubbed).

    Composes a planner (e.g., A* or PSO) and an optimizer (e.g., PSO) into
    a two-stage path planning system. After refactoring, both return empty
    paths, so this returns empty as well.

    Parameters:
        planner: BasePlanner instance for initial path generation
        optimizer: Optimizer with optimize(path, grid) method
    """

    def __init__(self, planner: BasePlanner, optimizer: object) -> None:
        self.planner = planner
        self.optimizer = optimizer

    def plan(self, grid: Grid, start: Point, goal: Point) -> list[Point]:
        """Execute two-stage planning: planner then optimizer (both stubbed).

        Args:
            grid: 2D grid where 0=free, 1=obstacle
            start: Starting position
            goal: Goal position

        Returns:
            Empty list after refactoring
        """
        path = self.planner.plan(grid, start, goal)
        if not path:
            return []
        if hasattr(self.optimizer, "optimize"):
            return self.optimizer.optimize(path, grid)
        return path
