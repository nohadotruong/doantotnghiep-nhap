"""
PSO (Particle Swarm Optimization) path planner.

For production use, refactor algorithms from other_project/algorithms/pso.py
"""

from typing import List, Tuple, Optional
import random
import math

import planning.api as plan_api
from planning.core.base import BasePlanner
from planning.core.astar import AStarPlanner


class PSOPlanner(BasePlanner):
    """PSO-based path planning algorithm."""

    def __init__(
        self,
        grid: plan_api.Grid,
        start: plan_api.Point,
        goal: plan_api.Point,
        num_particles: int = 50,
        max_iterations: int = 120,
        cognitive_coeff: float = 1.4,
        social_coeff: float = 1.6,
        max_velocity: float = 2.5,
        inertia_weight: float = 0.7,
    ):
        """Initialize PSO planner."""
        super().__init__(grid, start, goal)
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.cognitive_coeff = cognitive_coeff
        self.social_coeff = social_coeff
        self.max_velocity = max_velocity
        self.inertia_weight = inertia_weight

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        """
        Execute PSO algorithm for path planning.

        Returns:
            List of waypoints or None if no path found
        """
        # Fallback to A* for now
        astar = AStarPlanner(self.grid, self.start, self.goal)
        return astar.plan()


__all__ = ["PSOPlanner"]
