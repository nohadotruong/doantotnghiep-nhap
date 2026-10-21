"""
Base planner abstract class.

All path planning algorithms inherit from BasePlanner and implement the plan() method.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

import planning.api as plan_api


class BasePlanner(ABC):
    """Abstract base class for all path planners."""

    def __init__(
        self, grid: plan_api.Grid, start: plan_api.Point, goal: plan_api.Point
    ):
        """
        Initialize planner.

        Args:
            grid: Grid environment with obstacles
            start: Starting position
            goal: Goal position
        """
        self.grid = grid
        self.start = start
        self.goal = goal

    @abstractmethod
    def plan(self) -> Optional[List[Tuple[int, int]]]:
        """
        Execute path planning algorithm.

        Returns:
            List of (x, y) coordinates forming the path, or None if no path found
        """
        pass


__all__ = ["BasePlanner"]
