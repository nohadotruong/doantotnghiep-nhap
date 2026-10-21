from .astar import Astar
from .pso import PSOptimizer
from environment.grid_map import GridMap
from typing import List, Optional, Tuple
from utils.geometry import (
    check_collision_line,
    remove_redundant_points,
    remove_redundant_transitions,
)

import numpy as np


class HAPSO:

    def __init__(
        self,
        grid: GridMap,
        astar_prune_collinear: bool = True,
        astar_prune_transitions: bool = True,
        astar_avoid_corner_cutting: bool = True,
        pso_swarm_size: int = 30,
        pso_max_iter: int = 100,
        pso_w: float = 0.7,
        pso_c1: float = 2.0,
        pso_c2: float = 2.0,
        pso_max_velocity: float = 5.0,
    ) -> None:
        self.grid = grid
        self.astar_prune_collinear = astar_prune_collinear
        self.astar_prune_transitions = astar_prune_transitions
        self.astar_avoid_corner_cutting = astar_avoid_corner_cutting

        self.pso_swarm_size = pso_swarm_size
        self.pso_max_iter = pso_max_iter
        self.pso_w = pso_w
        self.pso_c1 = pso_c1
        self.pso_c2 = pso_c2
        self.pso_max_velocity = pso_max_velocity

    def plan(self) -> Optional[List[Tuple[int, int]]]:

        astar = Astar(
            self.grid,
            prune_collinear=self.astar_prune_collinear,
            prune_transitions=self.astar_prune_transitions,
            avoid_corner_cutting=self.astar_avoid_corner_cutting,
        )
        coarse_path = astar.plan()

        if coarse_path is None or len(coarse_path) < 3:
            return coarse_path

        print(
            f"[HAPSO] A* path (corner cutting={'avoided' if self.astar_avoid_corner_cutting else 'allowed'}): {len(coarse_path)} waypoints"
        )

        if self.astar_prune_collinear:
            coarse_path = remove_redundant_points(coarse_path)
            print(f"[HAPSO] After prune collinear: {len(coarse_path)} waypoints")

        if self.astar_prune_transitions:
            coarse_path = remove_redundant_transitions(self.grid, coarse_path)
            print(f"[HAPSO] After prune transitions: {len(coarse_path)} waypoints")

        optimized_path = self._optimize_segments(coarse_path)
        print(f"[HAPSO] After PSO optimization: {len(optimized_path)} waypoints")

        if not self._validate_path(optimized_path):
            print(
                f"[HAPSO] Warning: PSO optimization created collisions, reverting to coarse path"
            )
            optimized_path = coarse_path

        smoothed_path = self._smooth_line_of_sight(optimized_path)
        print(f"[HAPSO] After smoothing: {len(smoothed_path)} waypoints")

        return smoothed_path

    def _optimize_segments(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(path) <= 2:
            return path

        optimized = [path[0]]

        grid_array = self._grid_to_numpy_array()

        for i in range(1, len(path) - 1):
            p_start = path[i - 1]
            p_mid = path[i]
            p_end = path[i + 1]

            optimizer = PSOptimizer(
                grid=grid_array,
                swarm_size=self.pso_swarm_size,
                max_iter=self.pso_max_iter,
                w=self.pso_w,
                c1=self.pso_c1,
                c2=self.pso_c2,
                max_velocity=self.pso_max_velocity,
            )

            p_optimized = optimizer.optimize(p_start, p_mid, p_end)
            optimized.append(p_optimized)

        optimized.append(path[-1])

        return optimized

    def _grid_to_numpy_array(self) -> np.ndarray:
        grid_array = np.zeros((self.grid.height, self.grid.width), dtype=np.uint8)

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.is_obstacle(x, y):
                    grid_array[y, x] = 1

        return grid_array

    def _smooth_line_of_sight(
        self, path: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current = 0

        while current < len(path) - 1:

            next_idx = current + 1
            for j in range(len(path) - 1, current, -1):
                if not check_collision_line(self.grid, path[current], path[j]):
                    next_idx = j
                    break

            smoothed.append(path[next_idx])
            current = next_idx

        return smoothed

    def _validate_path(self, path: List[Tuple[int, int]]) -> bool:
        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):
                return False
        return True
