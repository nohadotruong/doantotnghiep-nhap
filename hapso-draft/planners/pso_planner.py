"""Stub PSO planner after refactoring.

Algorithm implementation has been removed.
"""

from __future__ import annotations

from planners.base import BasePlanner
from planners.inertia_weight import InertiaWeight, SIW
from utils.grid_utils import Grid, Point


class PSOPlanner(BasePlanner):
    """Stub PSO path planner.

    After refactoring, the PSO algorithm implementation has been removed.
    This class is retained for interface compatibility.

    Parameters:
        n_particles: Swarm size (default: 30)
        n_iterations: Number of iterations (default: 60)
        n_waypoints: Number of waypoints (default: 6)
        c1: Cognitive coefficient (default: 1.6)
        c2: Social coefficient (default: 1.6)
        inertia: Inertia weight strategy (default: SIW)
    """

    def __init__(
        self,
        n_particles: int = 30,
        n_iterations: int = 60,
        n_waypoints: int = 6,
        c1: float = 1.6,
        c2: float = 1.6,
        inertia: InertiaWeight | None = None,
    ) -> None:
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.n_waypoints = n_waypoints
        self.c1 = c1
        self.c2 = c2
        self.inertia = inertia or SIW()

    def plan(self, grid: Grid, start: Point, goal: Point) -> list[Point]:
        """Plan a path using PSO algorithm (stubbed).

        Args:
            grid: 2D grid where 0=free, 1=obstacle
            start: Starting position
            goal: Goal position

        Returns:
            Empty list after refactoring
        """
        # After refactoring: return empty path
        return []
