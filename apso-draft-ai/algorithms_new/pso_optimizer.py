from algorithms.pso import PSOOptimizer as OriginalPSOOptimizer
from environment.grid_map import GridMap
from typing import List, Optional, Tuple
from utils_new import (
    is_path_valid,
    path_length,
)


class PSOOptimizer:
    def __init__(
        self,
        grid: GridMap,
        num_particles: int = 50,
        max_iterations: int = 100,
        inertia_weight: float = 0.7,
        cognitive_coeff: float = 1.4,
        social_coeff: float = 1.6,
        collision_penalty: float = 1000.0,
        smoothing_strength: float = 0.5,
    ) -> None:
        self.grid = grid
        self.optimizer = OriginalPSOOptimizer(
            grid,
            num_particles=num_particles,
            max_iterations=max_iterations,
            inertia_weight=inertia_weight,
            cognitive_coeff=cognitive_coeff,
            social_coeff=social_coeff,
            collision_penalty=collision_penalty,
            smoothing_strength=smoothing_strength,
        )

    def optimize(self, path: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        return self.optimizer.optimize(path)

    def _fitness(self, path: List[Tuple[float, float]]) -> float:
        c = 1.0 if is_path_valid(path, self.grid) else 0.0
        d = path_length(path)
        return d * c
