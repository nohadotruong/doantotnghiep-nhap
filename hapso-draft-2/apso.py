from typing import List, Tuple
import math
import random
from astar import AStar
from pso import PSOptimizer
from pso_improvement import SIW, SOBL

class APSO:

    def __init__(self, grid, n_particles: int=20, max_iter: int=200, c1: float=2.0, c2: float=2.0, w_min: float=0.4, w_max: float=0.9):
        self.grid = grid
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.c1 = c1
        self.c2 = c2
        self.w_min = w_min
        self.w_max = w_max
        self.siw = SIW(w_min=w_min, w_max=w_max)
        self.sobl = SOBL(mu=0.5, sigma=0.15)

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        try:
            astar = AStar(self.grid, remove_redundant=True, remove_transitive=True, avoid_corner_cutting=False)
            path = astar.find_path(start, goal)
            if not path:
                print('[APSO]  A did not find a path')
                return []
            print(f'[APSO]  A found path with {len(path)} waypoints')
            pso_opt = PSOptimizer(grid=self.grid, n_particles=self.n_particles, max_iter=self.max_iter, c1=self.c1, c2=self.c2, w_min=self.w_min, w_max=self.w_max)
            optimized_path = pso_opt.optimize(path)
            if not optimized_path:
                print('[APSO]  PSO optimization failed')
                return []
            print(f'[APSO]  PSO optimized to {len(optimized_path)} waypoints')
            return optimized_path
        except Exception as e:
            print(f'[APSO]  Error: {e}')
            return []

    def _euclidean_distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)

    def _fitness(self, path: List[Tuple[int, int]]) -> float:
        if len(path) < 2:
            return float('inf')
        length = self._path_length(path)
        penalty = self._obstacle_penalty(path)
        return length + penalty * 100.0

    def _generate_opposite_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(path) <= 2:
            return path[:]
        opposite_path = [path[0]]
        for i in range(1, len(path) - 1):
            (x, y) = path[i]
            if random.random() < 0.5:
                new_x = random.randint(0, self.grid.width - 1)
                new_y = random.randint(0, self.grid.height - 1)
                if self._is_walkable(new_x, new_y):
                    opposite_path.append((new_x, new_y))
                else:
                    opposite_path.append((x, y))
            else:
                opposite_path.append((x, y))
        opposite_path.append(path[-1])
        return opposite_path

    def _insert_waypoint(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(path) < 2:
            return path[:]
        new_path = [path[0]]
        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]
            candidates = []
            for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                (nx, ny) = (prev[0] + dx, prev[1] + dy)
                if self._is_walkable(nx, ny):
                    dist = self._euclidean_distance((nx, ny), curr)
                    candidates.append(((nx, ny), dist))
            if candidates and random.random() < 0.2:
                waypoint = min(candidates, key=lambda x: x[1])[0]
                new_path.append(waypoint)
            new_path.append(curr)
        return new_path

    def _is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.grid.width or y < 0 or (y >= self.grid.height):
            return False
        return not self.grid.is_obstacle(x, y)

    def _obstacle_penalty(self, path: List[Tuple[int, int]]) -> int:
        penalty = 0
        for (x, y) in path:
            if not self._is_walkable(x, y):
                penalty += 1
        return penalty

    def _optimize_pso(self, initial_path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(initial_path) < 2:
            return initial_path
        particles = []
        best_fitness = [float('inf')] * self.n_particles
        best_position = [None] * self.n_particles
        global_best_fitness = self._fitness(initial_path)
        global_best_position = initial_path[:]
        for i in range(self.n_particles):
            if i == 0:
                path = initial_path[:]
            elif random.random() < 0.5:
                path = self._shorten_path(initial_path)
            else:
                path = self._insert_waypoint(initial_path)
            particles.append(path)
            fitness = self._fitness(path)
            best_fitness[i] = fitness
            best_position[i] = path[:]
            if fitness < global_best_fitness:
                global_best_fitness = fitness
                global_best_position = path[:]
        for iteration in range(self.max_iter):
            k = iteration + 1
            w_current = self.siw.compute(k, self.max_iter)
            for i in range(self.n_particles):
                current_path = particles[i]
                current_fitness = self._fitness(current_path)
                if current_fitness < best_fitness[i]:
                    best_fitness[i] = current_fitness
                    best_position[i] = current_path[:]
                if current_fitness < global_best_fitness:
                    global_best_fitness = current_fitness
                    global_best_position = current_path[:]
                mutation_prob = 0.3 * w_current
                if random.random() < mutation_prob:
                    if random.random() < 0.5:
                        particles[i] = self._shorten_path(current_path)
                    else:
                        particles[i] = self._insert_waypoint(current_path)
            for i in range(self.n_particles):
                best_path = best_position[i]
                if best_path:
                    opposite_path = self._generate_opposite_path(best_path)
                    opposite_fitness = self._fitness(opposite_path)
                    if opposite_fitness < best_fitness[i]:
                        best_fitness[i] = opposite_fitness
                        best_position[i] = opposite_path[:]
                        if opposite_fitness < global_best_fitness:
                            global_best_fitness = opposite_fitness
                            global_best_position = opposite_path[:]
            gbest_opposite = self._generate_opposite_path(global_best_position)
            gbest_opposite_fitness = self._fitness(gbest_opposite)
            if gbest_opposite_fitness < global_best_fitness:
                global_best_fitness = gbest_opposite_fitness
                global_best_position = gbest_opposite[:]
        return global_best_position

    def _path_length(self, path: List[Tuple[int, int]]) -> float:
        if len(path) < 2:
            return 0.0
        total = 0.0
        for i in range(len(path) - 1):
            total += self._euclidean_distance(path[i], path[i + 1])
        return total

    def _shorten_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(path) <= 2:
            return path[:]
        optimized = [path[0]]
        for i in range(1, len(path) - 1):
            prev = optimized[-1]
            curr = path[i]
            next_point = path[i + 1]
            can_skip = True
            dx = next_point[0] - prev[0]
            dy = next_point[1] - prev[1]
            steps = max(abs(dx), abs(dy))
            if steps > 0:
                for step in range(1, steps):
                    x = int(prev[0] + dx * step / steps)
                    y = int(prev[1] + dy * step / steps)
                    if not self._is_walkable(x, y):
                        can_skip = False
                        break
            if not can_skip:
                optimized.append(curr)
        optimized.append(path[-1])
        return optimized
