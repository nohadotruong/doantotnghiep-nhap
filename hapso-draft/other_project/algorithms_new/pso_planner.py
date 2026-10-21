from algorithms.pso import PSOPlanner as OriginalPSOPlanner
from algorithms_new.base import BasePlanner
from environment.grid_map import GridMap
from typing import List, Optional, Tuple


class PSOPlanner(BasePlanner):
    def __init__(
        self,
        grid: GridMap,
        num_particles: int = 50,
        num_waypoints: Optional[int] = None,
        max_iterations: int = 120,
        inertia_weight: float = 0.7,
        cognitive_coeff: float = 1.4,
        social_coeff: float = 1.6,
        collision_penalty: float = 1000.0,
        max_velocity: float = 2.5,
    ) -> None:
        super().__init__(grid)
        self.pso = OriginalPSOPlanner(
            grid,
            num_particles=num_particles,
            num_waypoints=num_waypoints,
            max_iterations=max_iterations,
            inertia_weight=inertia_weight,
            cognitive_coeff=cognitive_coeff,
            social_coeff=social_coeff,
            collision_penalty=collision_penalty,
            max_velocity=max_velocity,
        )

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        return self.pso.plan()
