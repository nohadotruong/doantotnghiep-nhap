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


class APSO:

    def __init__(
        self,
        grid: GridMap,
        astar_prune_collinear: bool = True,
        astar_prune_transitions: bool = True,
        astar_avoid_corner_cutting: bool = False,
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

        print(f"[APSO] A* path: {len(coarse_path)} waypoints")

        if self.astar_prune_collinear:
            coarse_path = remove_redundant_points(coarse_path)
            print(f"[APSO] After prune collinear: {len(coarse_path)} waypoints")

        if self.astar_prune_transitions:
            coarse_path = remove_redundant_transitions(self.grid, coarse_path)
            print(f"[APSO] After prune transitions: {len(coarse_path)} waypoints")

        optimized_path = self._optimize_segments(coarse_path)
        print(f"[APSO] After PSO optimization: {len(optimized_path)} waypoints")

        if not self._validate_path(optimized_path):
            print(
                f"[APSO] Warning: PSO optimization created collisions, reverting to coarse path"
            )
            optimized_path = coarse_path

        smoothed_path = self._smooth_line_of_sight(optimized_path)
        print(f"[APSO] After smoothing: {len(smoothed_path)} waypoints")

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


if __name__ == "__main__":
    from environment.grid_map import GridMap

    print("=" * 70)
    print("APSO Path Planning Example")
    print("=" * 70)

    grid = GridMap(width=50, height=50)

    for x in range(20, 30):
        grid.set_obstacle(x, 25, True)
    for y in range(10, 40):
        grid.set_obstacle(25, y, True)

    grid.set_start(5, 5)
    grid.set_goal(45, 45)

    print(f"\nGrid: {grid.width}x{grid.height}")
    print(f"Start: {grid.start}, Goal: {grid.goal}")

    apso = APSO(
        grid=grid,
        astar_prune_collinear=True,
        astar_prune_transitions=True,
        pso_swarm_size=30,
        pso_max_iter=80,
    )

    print("\n" + "-" * 70)
    print("Running APSO...")
    print("-" * 70 + "\n")

    path = apso.plan()

    print("\n" + "-" * 70)
    print("Result:")
    print("-" * 70)

    if path:
        print(f"\nPath found with {len(path)} waypoints")
        print(f"Waypoints: {path}")

        total_length = 0
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            distance = (dx**2 + dy**2) ** 0.5
            total_length += distance

        print(f"Total path length: {total_length:.2f}")
    else:
        print("No path found!")
