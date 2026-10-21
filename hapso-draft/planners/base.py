"""Stub planner base class after refactoring.

Note: All algorithm implementations have been removed.
This module provides only the abstract base interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from utils.grid_utils import Grid, Point


class BasePlanner(ABC):
    """Abstract base class for path planning algorithms.

    After refactoring, all subclasses return empty paths.
    This class is retained for interface compatibility.
    """

    @abstractmethod
    def plan(self, grid: Grid, start: Point, goal: Point) -> list[Point]:
        """Plan a path from start to goal on the grid.

        Args:
            grid: 2D grid where 0=free, 1=obstacle
            start: Starting position (x, y)
            goal: Goal position (x, y)

        Returns:
            List of waypoints from start to goal
            After refactoring: returns empty list []
        """
        return []
