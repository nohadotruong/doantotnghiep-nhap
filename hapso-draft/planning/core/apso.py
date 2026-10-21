"""
APSO (Adaptive PSO) path planner - A* + PSO optimization without corner guards.

For production use, refactor algorithms from other_project/algorithms/apso.py
"""

from typing import List, Tuple, Optional

import planning.api as plan_api
from planning.core.base import BasePlanner
from planning.core.astar import AStarPlanner
from planning.core.pso import PSOPlanner


class APSOPlanner(BasePlanner):
    """Adaptive PSO - A* with segment-wise PSO optimization (no corner guard)."""

    def __init__(
        self,
        grid: plan_api.Grid,
        start: plan_api.Point,
        goal: plan_api.Point,
        astar_prune_collinear: bool = True,
        astar_prune_transitions: bool = True,
        astar_avoid_corner_cutting: bool = False,
        pso_particles: int = 50,
        pso_iterations: int = 120,
        pso_cognitive_coeff: float = 1.4,
        pso_social_coeff: float = 1.6,
    ):
        """Initialize APSO planner."""
        super().__init__(grid, start, goal)
        self.astar_prune_collinear = astar_prune_collinear
        self.astar_prune_transitions = astar_prune_transitions
        self.astar_avoid_corner_cutting = astar_avoid_corner_cutting
        self.pso_particles = pso_particles
        self.pso_iterations = pso_iterations
        self.pso_cognitive_coeff = pso_cognitive_coeff
        self.pso_social_coeff = pso_social_coeff

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        """
        Execute APSO algorithm.

        Pipeline:
        1. Get coarse path from A*
        2. Prune collinear waypoints
        3. Smooth via line-of-sight
        4. Segment-wise PSO optimization (future enhancement)
        5. Return optimized path

        Returns:
            List of waypoints or None if no path found
        """
        # Step 1: Get A* path
        astar = AStarPlanner(
            self.grid,
            self.start,
            self.goal,
            prune_collinear=self.astar_prune_collinear,
            prune_transitions=self.astar_prune_transitions,
            avoid_corner_cutting=self.astar_avoid_corner_cutting,
        )
        path = astar.plan()

        if not path:
            return None

        # For now, return A* result
        # TODO: Add PSO segment optimization
        return path


__all__ = ["APSOPlanner"]
