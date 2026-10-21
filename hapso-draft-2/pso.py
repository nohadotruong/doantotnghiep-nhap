from typing import Callable, List, Optional, Tuple
import math
import random
import numpy as np
from get_line_grid import get_line_grid_incremental_traversal
from pso_improvement import SIW, SOBL


class PSOPlanner:
    def __init__(
        self,
        grid,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        n_waypoints: int = 3,
        n_particles: int = 20,
        w: float = 0.7,
        c1: float = 2.0,
        c2: float = 2.0,
        max_iter: int = 200,
        use_siw: bool = False,
        w_min: float = 0.4,
        w_max: float = 0.9,
        use_sobl: bool = True,
        sobl_mu: float = 0.5,
        sobl_sigma: float = 0.15,
        retry_until_success: bool = True,
        max_restarts: Optional[int] = 30,
    ):
        if hasattr(grid, "grid") and hasattr(grid, "width") and hasattr(grid, "height"):
            self.grid = grid.grid
            self.width = grid.width
            self.height = grid.height
        else:
            self.grid = grid
            self.height = len(grid)
            self.width = len(grid[0]) if self.height > 0 else 0
        self.start = start
        self.goal = goal
        self.n_waypoints = n_waypoints
        self.n_particles = n_particles
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.max_iter = max_iter
        self.use_siw = use_siw
        self.w_min = w_min
        self.w_max = w_max
        self.use_sobl = use_sobl
        self.sobl_mu = sobl_mu
        self.sobl_sigma = sobl_sigma
        self.retry_until_success = retry_until_success
        self.max_restarts = max_restarts
        total_cells = max(1, self.width * self.height)
        obstacle_cells = sum((1 for row in self.grid for cell in row if cell == 1))
        self.obstacle_ratio = obstacle_cells / total_cells
        (sx, sy) = self.start
        (gx, gy) = self.goal
        sg_dist = math.sqrt((gx - sx) * (gx - sx) + (gy - sy) * (gy - sy))
        auto_max = int(
            max(4, min(20, round(3 + self.obstacle_ratio * 12 + sg_dist / 10)))
        )
        self.max_waypoints = max(int(n_waypoints), auto_max)
        self.min_waypoints = 1 if self.max_waypoints <= 2 else 2
        self.activation_threshold = 0.5

    def plan(self) -> List[Tuple[int, int]]:
        self._validate_inputs()
        attempts = 0
        while True:
            (initial_positions, bounds, fitness_fn) = self._build_problem()
            gbest_pos = self._run_pso_optimization(
                initial_positions, bounds, fitness_fn
            )
            path = self._post_process(gbest_pos)
            if path:
                return path
            attempts += 1
            if not self.retry_until_success:
                return []
            if self.max_restarts is not None and attempts >= self.max_restarts:
                return []

    def _build_problem(
        self,
    ) -> Tuple[List[np.ndarray], List[Tuple[float, float]], Callable]:
        initial_positions = []
        (sx, sy) = self.start
        (gx, gy) = self.goal
        base_dx = gx - sx
        base_dy = gy - sy
        norm = math.sqrt(base_dx * base_dx + base_dy * base_dy)
        if norm > 0:
            nx = -base_dy / norm
            ny = base_dx / norm
        else:
            nx = 0.0
            ny = 0.0
        lateral_scale = max(self.width, self.height) * 0.15
        for _ in range(self.n_particles):
            waypoints = []
            active_k = random.randint(self.min_waypoints, self.max_waypoints)
            for i in range(self.max_waypoints):
                t_center = (i + 1) / (self.max_waypoints + 1)
                t = max(0.05, min(0.95, t_center + random.uniform(-0.15, 0.15)))
                base_x = sx + t * base_dx
                base_y = sy + t * base_dy
                offset = random.uniform(-lateral_scale, lateral_scale)
                x = int(round(base_x + nx * offset + random.uniform(-1.0, 1.0)))
                y = int(round(base_y + ny * offset + random.uniform(-1.0, 1.0)))
                x = max(0, min(x, self.width - 1))
                y = max(0, min(y, self.height - 1))
                if i < active_k:
                    a = random.uniform(0.7, 1.0)
                else:
                    a = random.uniform(0.0, 0.3)
                waypoints.append((x, y, a))
            flat_pos = np.array(
                [coord for triple in waypoints for coord in triple], dtype=float
            )
            initial_positions.append(flat_pos)
        bounds = []
        for _ in range(self.max_waypoints):
            bounds.append([0, self.width - 1])
            bounds.append([0, self.height - 1])
            bounds.append([0.0, 1.0])

        def fitness_fn(pos: np.ndarray) -> float:
            waypoints = self._decode_particle_waypoints(pos)
            path = [self.start] + waypoints + [self.goal]
            (cost_dc, _, _) = self._path_cost_dc(path)
            return -cost_dc

        return (initial_positions, bounds, fitness_fn)

    def _decode_particle_waypoints(self, pos: np.ndarray) -> List[Tuple[int, int]]:
        candidates = []
        for i in range(self.max_waypoints):
            base = i * 3
            x = int(round(pos[base]))
            y = int(round(pos[base + 1]))
            a = float(max(0.0, min(1.0, pos[base + 2])))
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            if self.grid[y][x] == 1:
                continue
            candidates.append((x, y, a))
        active = [(x, y) for (x, y, a) in candidates if a >= self.activation_threshold]
        if len(active) < self.min_waypoints and candidates:
            top = sorted(candidates, key=lambda item: item[2], reverse=True)
            needed = self.min_waypoints - len(active)
            for x, y, _ in top:
                if (x, y) not in active:
                    active.append((x, y))
                    needed -= 1
                    if needed <= 0:
                        break
        active = list(dict.fromkeys(active))
        active = self._sort_waypoints_sg(active)
        active = self._shrink_waypoints(active)
        return active

    def _path_cost_dc(self, path: List[Tuple[int, int]]) -> Tuple[float, int, float]:
        d = 0.0
        collision_cells = 0
        for i in range(len(path) - 1):
            (x1, y1) = path[i]
            (x2, y2) = path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            d += math.sqrt(dx * dx + dy * dy)
            collision_cells += self._segment_collision_count(path[i], path[i + 1])
        c = 1.0 + float(collision_cells)
        return (d * c, collision_cells, d)

    def _post_process(self, gbest_pos: np.ndarray) -> List[Tuple[int, int]]:
        waypoints = self._decode_particle_waypoints(gbest_pos)
        for _ in range(2):
            waypoints = self._shrink_waypoints(waypoints)
        path = [self.start] + waypoints + [self.goal]
        (_, collision_cells, _) = self._path_cost_dc(path)
        if collision_cells > 0:
            return []
        return path

    def _run_pso_optimization(
        self,
        initial_positions: List[np.ndarray],
        bounds: List[Tuple[float, float]],
        fitness_fn: Callable[[np.ndarray], float],
    ) -> np.ndarray:
        positions = np.array(initial_positions[: self.n_particles], dtype=float)
        velocities = np.zeros_like(positions)
        n_dims = len(bounds)
        fitness = np.array([fitness_fn(pos) for pos in positions])
        pbest_pos = positions.copy()
        pbest_fitness = fitness.copy()
        gbest_idx = np.argmax(pbest_fitness)
        gbest_pos = pbest_pos[gbest_idx].copy()
        gbest_fitness = pbest_fitness[gbest_idx]
        siw = None
        if self.use_siw:
            siw = SIW(w_min=self.w_min, w_max=self.w_max)
        sobl = None
        if self.use_sobl:
            sobl = SOBL(mu=self.sobl_mu, sigma=self.sobl_sigma)
        for iteration in range(self.max_iter):
            if self.use_siw:
                k = iteration + 1
                w_current = siw.compute(k, self.max_iter)
            else:
                w_current = self.w
            for i in range(self.n_particles):
                r1 = np.random.random(n_dims)
                r2 = np.random.random(n_dims)
                velocities[i] = (
                    w_current * velocities[i]
                    + self.c1 * r1 * (pbest_pos[i] - positions[i])
                    + self.c2 * r2 * (gbest_pos - positions[i])
                )
                positions[i] = positions[i] + velocities[i]
                for d in range(n_dims):
                    positions[i, d] = np.clip(
                        positions[i, d], bounds[d][0], bounds[d][1]
                    )
                fitness[i] = fitness_fn(positions[i])
                if fitness[i] > pbest_fitness[i]:
                    pbest_fitness[i] = fitness[i]
                    pbest_pos[i] = positions[i].copy()
                    if pbest_fitness[i] > gbest_fitness:
                        gbest_fitness = pbest_fitness[i]
                        gbest_pos = pbest_pos[i].copy()
            if self.use_sobl and sobl:
                for i in range(self.n_particles):
                    opposite_pbest = np.array(
                        sobl.opposite_vector(pbest_pos[i], bounds), dtype=float
                    )
                    opposite_fit = fitness_fn(opposite_pbest)
                    if opposite_fit > pbest_fitness[i]:
                        pbest_pos[i] = opposite_pbest
                        pbest_fitness[i] = opposite_fit
                        if opposite_fit > gbest_fitness:
                            gbest_fitness = opposite_fit
                            gbest_pos = opposite_pbest.copy()
                opposite_gbest = np.array(
                    sobl.opposite_vector(gbest_pos, bounds), dtype=float
                )
                opposite_gbest_fit = fitness_fn(opposite_gbest)
                if opposite_gbest_fit > gbest_fitness:
                    gbest_fitness = opposite_gbest_fit
                    gbest_pos = opposite_gbest.copy()
        return gbest_pos

    def _segment_collision_count(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        collisions = 0
        cells = get_line_grid_incremental_traversal(a, b)
        for x, y in cells:
            if (x, y) == self.start or (x, y) == self.goal:
                continue
            if x < 0 or x >= self.width or y < 0 or (y >= self.height):
                collisions += 1
                continue
            if self.grid[y][x] == 1:
                collisions += 1
        return collisions

    def _shrink_waypoints(
        self, waypoints: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        if not waypoints:
            return []
        points = [self.start] + waypoints + [self.goal]
        kept = [points[0]]
        i = 1
        while i < len(points) - 1:
            prev_pt = kept[-1]
            next_pt = points[i + 1]
            if self._segment_collision_count(prev_pt, next_pt) == 0:
                i += 1
                continue
            kept.append(points[i])
            i += 1
        kept.append(points[-1])
        return kept[1:-1]

    def _sort_waypoints_sg(
        self, waypoints: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        (sx, sy) = self.start
        (gx, gy) = self.goal
        dx = gx - sx
        dy = gy - sy
        line_len_sq = dx * dx + dy * dy
        if line_len_sq == 0:
            return waypoints[:]
        return sorted(
            waypoints,
            key=lambda wp: ((wp[0] - sx) * dx + (wp[1] - sy) * dy) / line_len_sq,
        )

    def _validate_inputs(self) -> None:
        if not (0 <= self.start[0] < self.width and 0 <= self.start[1] < self.height):
            raise ValueError(f"Start {self.start} is out of grid bounds")
        if not (0 <= self.goal[0] < self.width and 0 <= self.goal[1] < self.height):
            raise ValueError(f"Goal {self.goal} is out of grid bounds")
        if self.grid[self.start[1]][self.start[0]] == 1:
            raise ValueError(f"Start {self.start} is an obstacle")
        if self.grid[self.goal[1]][self.goal[0]] == 1:
            raise ValueError(f"Goal {self.goal} is an obstacle")


class PSOptimizer:
    def __init__(
        self,
        grid,
        n_particles: int = 20,
        max_iter: int = 50,
        c1: float = 1.5,
        c2: float = 1.5,
        w_min: float = 0.4,
        w_max: float = 0.9,
    ):
        self.grid = grid
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.c1 = c1
        self.c2 = c2
        self.w_min = w_min
        self.w_max = w_max
        self.siw = SIW(w_min=w_min, w_max=w_max)
        self.sobl = SOBL(mu=0.5, sigma=0.15)

    def optimize(self, initial_path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(initial_path) <= 2:
            return initial_path
        optimized_path = [initial_path[0]]
        for i in range(1, len(initial_path) - 1):
            prev_point = optimized_path[-1]
            next_point = initial_path[i + 1]
            optimal_wp = self._optimize_segment(prev_point, next_point)
            if optimal_wp:
                optimized_path.append(optimal_wp)
            else:
                optimized_path.append(initial_path[i])
        optimized_path.append(initial_path[-1])
        return optimized_path

    def _euclidean_distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)

    def _fitness_segment(
        self, start: Tuple[int, int], mid: Tuple[int, int], end: Tuple[int, int]
    ) -> float:
        if not self._is_walkable(mid[0], mid[1]):
            return 0.0
        collisions_1 = self._segment_collision_count(start, mid)
        if collisions_1 > 0:
            return 0.0
        collisions_2 = self._segment_collision_count(mid, end)
        if collisions_2 > 0:
            return 0.0
        d = self._euclidean_distance(start, mid) + self._euclidean_distance(mid, end)
        return d

    def _initialize_segment_particles(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        particles = []
        (sx, sy) = (float(start[0]), float(start[1]))
        (ex, ey) = (float(end[0]), float(end[1]))
        for i in range(self.n_particles):
            t = random.random()
            base_x = sx + (ex - sx) * t
            base_y = sy + (ey - sy) * t
            dx = ex - sx
            dy = ey - sy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1e-06:
                nx = -dy / dist
                ny = dx / dist
            else:
                (nx, ny) = (0, 0)
            offset = random.uniform(-dist * 0.3, dist * 0.3)
            x = int(round(base_x + nx * offset))
            y = int(round(base_y + ny * offset))
            x = max(0, min(x, self.grid.width - 1))
            y = max(0, min(y, self.grid.height - 1))
            particles.append((x, y))
        return particles

    def _is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.grid.width or y < 0 or (y >= self.grid.height):
            return False
        return not self.grid.is_obstacle(x, y)

    def _optimize_segment(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Tuple[int, int]:
        particles = self._initialize_segment_particles(start, end)
        fitness = [self._fitness_segment(start, p, end) for p in particles]
        pbest_pos = particles[:]
        pbest_fitness = fitness[:]
        gbest_idx = np.argmin(pbest_fitness) if min(pbest_fitness) > 0 else 0
        gbest_pos = pbest_pos[gbest_idx]
        gbest_fitness = pbest_fitness[gbest_idx]
        v_max = max(self.grid.width, self.grid.height) * 0.1
        [
            (random.uniform(-v_max, v_max), random.uniform(-v_max, v_max))
            for _ in range(self.n_particles)
        ]
        for iteration in range(self.max_iter):
            k = iteration + 1
            w_current = self.siw.compute(k, self.max_iter)
            for i in range(self.n_particles):
                mutation_prob = 0.6 * w_current
                if random.random() < mutation_prob:
                    new_x = random.randint(0, self.grid.width - 1)
                    new_y = random.randint(0, self.grid.height - 1)
                    particles[i] = (new_x, new_y)
                elif random.random() < 0.5:
                    particles[i] = pbest_pos[i]
                else:
                    particles[i] = gbest_pos
                fitness[i] = self._fitness_segment(start, particles[i], end)
                if fitness[i] > 0 and fitness[i] < pbest_fitness[i]:
                    pbest_fitness[i] = fitness[i]
                    pbest_pos[i] = particles[i]
                    if fitness[i] < gbest_fitness:
                        gbest_fitness = fitness[i]
                        gbest_pos = pbest_pos[i]
            for i in range(self.n_particles):
                if pbest_fitness[i] > 0:
                    bounds = [[0, self.grid.width - 1], [0, self.grid.height - 1]]
                    opposite_pos_array = self.sobl.opposite_vector(pbest_pos[i], bounds)
                    opposite_pos = tuple([int(round(x)) for x in opposite_pos_array])
                    opposite_pos = (
                        max(0, min(opposite_pos[0], self.grid.width - 1)),
                        max(0, min(opposite_pos[1], self.grid.height - 1)),
                    )
                    opposite_fitness = self._fitness_segment(start, opposite_pos, end)
                    if opposite_fitness > 0 and opposite_fitness < pbest_fitness[i]:
                        pbest_fitness[i] = opposite_fitness
                        pbest_pos[i] = opposite_pos
                        if opposite_fitness < gbest_fitness:
                            gbest_fitness = opposite_fitness
                            gbest_pos = opposite_pos
            if gbest_fitness > 0:
                bounds = [[0, self.grid.width - 1], [0, self.grid.height - 1]]
                opposite_gbest_array = self.sobl.opposite_vector(gbest_pos, bounds)
                opposite_gbest = tuple([int(round(x)) for x in opposite_gbest_array])
                opposite_gbest = (
                    max(0, min(opposite_gbest[0], self.grid.width - 1)),
                    max(0, min(opposite_gbest[1], self.grid.height - 1)),
                )
                opposite_gbest_fitness = self._fitness_segment(
                    start, opposite_gbest, end
                )
                if (
                    opposite_gbest_fitness > 0
                    and opposite_gbest_fitness < gbest_fitness
                ):
                    gbest_fitness = opposite_gbest_fitness
                    gbest_pos = opposite_gbest
        return gbest_pos if gbest_fitness > 0 else None

    def _segment_collision_count(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        collisions = 0
        cells = get_line_grid_incremental_traversal(a, b)
        for x, y in cells:
            if x < 0 or x >= self.grid.width or y < 0 or (y >= self.grid.height):
                collisions += 1
                continue
            if self.grid.is_obstacle(x, y):
                collisions += 1
        return collisions
