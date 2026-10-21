"""
HAPSO (Hybrid A* PSO) path planner - A* + PSO optimization with corner guards.

For production use, refactor algorithms from other_project/algorithms/hapso.py
"""

from typing import List, Tuple, Optional

import planning.api as plan_api
from planning.core.base import BasePlanner
from planning.core.astar import AStarPlanner


class HAPSOPlanner(BasePlanner):
    """Hybrid A* PSO - A* with segment-wise PSO optimization (with corner guard)."""

    def __init__(
        self,
        grid: plan_api.Grid,
        start: plan_api.Point,
        goal: plan_api.Point,
        astar_prune_collinear: bool = True,
        astar_prune_transitions: bool = True,
        astar_avoid_corner_cutting: bool = True,
        pso_particles: int = 50,
        pso_iterations: int = 120,
        pso_cognitive_coeff: float = 1.4,
        pso_social_coeff: float = 1.6,
    ):
        """Initialize HAPSO planner."""
        super().__init__(grid, start, goal)
        self.astar_prune_collinear = astar_prune_collinear
        self.astar_prune_transitions = astar_prune_transitions
        self.astar_avoid_corner_cutting = (
            astar_avoid_corner_cutting  # HAPSO: True by default
        )
        self.pso_particles = pso_particles
        self.pso_iterations = pso_iterations
        self.pso_cognitive_coeff = pso_cognitive_coeff
        self.pso_social_coeff = pso_social_coeff

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        """
        Execute HAPSO algorithm.

        Pipeline:
        1. Get coarse path from A* (with corner guide enabled)
        2. Prune collinear waypoints
        3. Smooth via line-of-sight (with corner checks)
        4. Segment-wise PSO optimization (future enhancement)
        5. Return optimized path

        Returns:
            List of waypoints or None if no path found
        """
        # Step 1: Get A* path with corner guard enabled
        astar = AStarPlanner(
            self.grid,
            self.start,
            self.goal,
            prune_collinear=self.astar_prune_collinear,
            prune_transitions=self.astar_prune_transitions,
            avoid_corner_cutting=True,  # HAPSO: Always enable corner guard
        )
        path = astar.plan()

        if not path:
            return None

        # For now, return A* result
        # TODO: Add PSO segment optimization with corner constraints
        return path


__all__ = ["HAPSOPlanner"]
