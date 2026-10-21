from typing import List, Tuple
from astar import AStar
from pso import PSOptimizer

class HAPSO:

    def __init__(self, grid, n_particles: int=20, max_iter: int=200, c1: float=2.0, c2: float=2.0, w_min: float=0.4, w_max: float=0.9):
        self.grid = grid
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.c1 = c1
        self.c2 = c2
        self.w_min = w_min
        self.w_max = w_max

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        try:
            astar = AStar(self.grid, remove_redundant=True, remove_transitive=True, avoid_corner_cutting=True)
            path = astar.find_path(start, goal)
            if not path:
                print('[HAPSO]  A did not find a path')
                return []
            print(f'[HAPSO]  A found path with {len(path)} waypoints (corner-cutting avoided)')
            pso_opt = PSOptimizer(grid=self.grid, n_particles=self.n_particles, max_iter=self.max_iter, c1=self.c1, c2=self.c2, w_min=self.w_min, w_max=self.w_max)
            optimized_path = pso_opt.optimize(path)
            if not optimized_path:
                print('[HAPSO]  PSO optimization failed')
                return []
            print(f'[HAPSO]  PSO optimized to {len(optimized_path)} waypoints')
            return optimized_path
        except Exception as e:
            print(f'[HAPSO]  Error: {e}')
            import traceback
            traceback.print_exc()
            return []
