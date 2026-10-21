from algorithms.astar import Astar
from environment.grid_map import GridMap
from typing import List, Optional, Tuple
from utils.geometry import calculate_path_length, check_collision_line
import math
import numpy as np
import random

from utils.geometry import calculate_path_length, check_collision_line
from algorithms.astar import Astar

def stochastic_inertia_weight(
    k: int,
    t_max: int,
    w_min: float = 0.4,
    w_max: float = 0.9,
    rb_range: Tuple[float, float] = (-0.1, 0.1),
) -> float:
    if t_max <= 0:
        raise ValueError("t_max must be positive")

    rb = random.uniform(*rb_range)
    return w_max - (w_max - w_min) * (k / t_max) * math.exp(rb)

def adaptive_inertia_weight(
    k: int,
    t_max: int,
    gbest_score_k: float,
    gbest_score_k_minus_1: float,
    w_min: float = 0.4,
    w_max: float = 0.9,
) -> float:
    if gbest_score_k_minus_1 == 0:
        ratio = 1.0
    else:
        ratio = gbest_score_k / gbest_score_k_minus_1

    return (w_max + w_min) * ratio - w_max * (k / t_max)

def nonlinear_decreasing_inertia_weight(
    k: int,
    t_max: int,
) -> float:
    exponent = (t_max - k) / t_max
    return math.exp(-math.exp(exponent))

def linear_decreasing_inertia_weight(
    k: int,
    t_max: int,
    w_min: float = 0.4,
    w_max: float = 0.9,
) -> float:
    return w_max - (w_max - w_min) * (k / t_max)

def sobl_try(
    pos: np.ndarray,
    fitness_fn,
    lb: np.ndarray,
    ub: np.ndarray,
    rng=None,
) -> Tuple[np.ndarray, float]:
    rng = rng or np.random

    r = rng.normal(loc=0.0, scale=1.0, size=pos.shape)
    r = np.clip(r, 0.0, 1.0)

    opp = lb + ub - r * pos
    opp = np.clip(opp, lb, ub)

    f_cur = fitness_fn(pos)
    f_opp = fitness_fn(opp)

    if f_opp <= f_cur:
        return opp, f_opp
    return pos, f_cur

class PSOPlanner:

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
        self.grid = grid
        self.num_particles = num_particles
        self.num_waypoints = num_waypoints
        self.max_iterations = max_iterations
        self.w = inertia_weight
        self.c1 = cognitive_coeff
        self.c2 = social_coeff
        self.collision_penalty = collision_penalty
        self.max_velocity = max_velocity

        self.valid_nodes: List[Tuple[int, int]] = []

        if num_waypoints is None:
            self.num_waypoints = self._auto_num_waypoints()
        else:
            self.num_waypoints = max(4, num_waypoints)

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        start = self.grid.start
        goal = self.grid.goal

        if start is None or goal is None:
            return None

        if not self._is_valid_endpoint(start) or not self._is_valid_endpoint(goal):
            return None

        if start == goal:
            return [start, goal]

        if not check_collision_line(self.grid, start, goal):

            return [start, goal]

        self.valid_nodes = self._collect_valid_nodes()
        if not self.valid_nodes:
            return None

        particles = []

        heuristic_particle = self._create_heuristic_particle(start, goal)
        particles.append(heuristic_particle)

        for _ in range(self.num_particles - 1):
            particles.append(self._init_particle())

        velocities = [np.zeros_like(p) for p in particles]

        pbest_positions = [p.copy() for p in particles]
        pbest_scores = [self._evaluate_fitness(p, start, goal) for p in particles]

        gbest_idx = int(np.argmin(pbest_scores))
        gbest_position = pbest_positions[gbest_idx].copy()
        gbest_score = pbest_scores[gbest_idx]

        for _ in range(self.max_iterations):
            for i in range(self.num_particles):
                r1 = np.random.rand(self.num_waypoints, 2)
                r2 = np.random.rand(self.num_waypoints, 2)

                cognitive = self.c1 * r1 * (pbest_positions[i] - particles[i])
                social = self.c2 * r2 * (gbest_position - particles[i])

                velocities[i] = self.w * velocities[i] + cognitive + social
                velocities[i] = np.clip(
                    velocities[i], -self.max_velocity, self.max_velocity
                )

                particles[i] = particles[i] + velocities[i]
                particles[i] = self._handle_constraints(particles[i])

                fitness = self._evaluate_fitness(particles[i], start, goal)
                if fitness < pbest_scores[i]:
                    pbest_scores[i] = fitness
                    pbest_positions[i] = particles[i].copy()

                    if fitness < gbest_score:
                        gbest_score = fitness
                        gbest_position = particles[i].copy()

        if np.isinf(gbest_score):

            astar = Astar(
                self.grid,
                prune_collinear=True,
                prune_transitions=True,
                avoid_corner_cutting=False,
            )
            astar_path = astar.plan()
            return astar_path

        best_path = self._build_path(gbest_position, start, goal)
        smoothed = self._smooth_line_of_sight(best_path)
        return smoothed

    def _auto_num_waypoints(self) -> int:
        start, goal = self.grid.start, self.grid.goal
        if start is None or goal is None:
            return 8

        manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        area = max(1, self.grid.width * self.grid.height)
        obstacle_count = len(self.grid.get_obstacles())
        free_ratio = 1.0 - obstacle_count / area

        if not check_collision_line(self.grid, start, goal):
            return 4

        base = round(manhattan / 6) + 2

        if free_ratio < 0.7:
            base += 2
        if free_ratio < 0.5:
            base += 2

        auto = int(max(4, min(base, 20)))
        return auto

    def _collect_valid_nodes(self) -> List[Tuple[int, int]]:
        nodes: List[Tuple[int, int]] = []
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if not self.grid.is_obstacle(x, y):
                    nodes.append((x, y))
        return nodes

    def _create_heuristic_particle(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> np.ndarray:
        waypoints: List[np.ndarray] = []

        for i in range(self.num_waypoints):

            t = (i + 1) / (self.num_waypoints + 1)

            x = start[0] + t * (goal[0] - start[0])
            y = start[1] + t * (goal[1] - start[1])

            waypoint = np.array([x, y], dtype=float)

            waypoint = self._project_to_bounds(waypoint)
            waypoint = self._repair_if_obstacle(waypoint)

            waypoints.append(waypoint)

        return np.array(waypoints, dtype=float)

    def _init_particle(self) -> np.ndarray:
        waypoints: List[np.ndarray] = []

        for _ in range(self.num_waypoints):
            vx, vy = self.valid_nodes[np.random.randint(0, len(self.valid_nodes))]
            candidate = np.array([vx, vy], dtype=float)
            waypoints.append(candidate)

        return np.array(waypoints, dtype=float)

    def _project_to_bounds(self, point: np.ndarray) -> np.ndarray:
        x = float(np.clip(point[0], 0, self.grid.width - 1))
        y = float(np.clip(point[1], 0, self.grid.height - 1))
        return np.array([x, y], dtype=float)

    def _repair_if_obstacle(self, point: np.ndarray) -> np.ndarray:
        gx, gy = int(round(point[0])), int(round(point[1]))
        if not self.grid.is_obstacle(gx, gy):
            return point

        nearest = self._find_nearest_valid((point[0], point[1]))
        return np.array(nearest, dtype=float)

    def _handle_constraints(self, waypoints: np.ndarray) -> np.ndarray:
        repaired = []
        for wp in waypoints:
            projected = self._project_to_bounds(wp)
            repaired.append(self._repair_if_obstacle(projected))
        return np.array(repaired, dtype=float)

    def _find_nearest_valid(self, point: Tuple[float, float]) -> Tuple[int, int]:
        px, py = point
        best = self.valid_nodes[0]
        best_dist = math.inf

        for vx, vy in self.valid_nodes:
            dist = (vx - px) ** 2 + (vy - py) ** 2
            if dist < best_dist:
                best_dist = dist
                best = (vx, vy)

        return best

    def _build_path(
        self, waypoints: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        path: List[Tuple[int, int]] = [start]
        for wp in waypoints:
            node = (int(round(wp[0])), int(round(wp[1])))
            if node != path[-1]:
                path.append(node)
        if goal != path[-1]:
            path.append(goal)
        return path

    def _count_collisions(self, path: List[Tuple[int, int]]) -> int:
        collisions = 0
        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):
                collisions += 1
        return collisions

    def _evaluate_fitness(
        self, waypoints: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> float:
        path = self._build_path(waypoints, start, goal)

        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):

                return np.inf

        length = calculate_path_length(path)
        return length

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

    def _is_valid_endpoint(self, point: Tuple[int, int]) -> bool:
        x, y = point
        return self.grid.is_inside(x, y) and not self.grid.is_obstacle(x, y)

class PSOptimizer:

    def __init__(
        self,
        grid: np.ndarray,
        swarm_size: int = 30,
        max_iter: int = 100,
        w: float = 0.7,
        c1: float = 2.0,
        c2: float = 2.0,
        max_velocity: float = 5.0,
    ) -> None:
        self.grid = grid
        self.height, self.width = grid.shape
        self.swarm_size = swarm_size
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.max_velocity = max_velocity

    def optimize(
        self,
        p_start: Tuple[int, int],
        p_mid: Tuple[int, int],
        p_end: Tuple[int, int],
    ) -> Tuple[int, int]:

        particles = self._initialize_particles(p_start, p_mid, p_end)
        velocities = np.random.uniform(
            -self.max_velocity, self.max_velocity, size=particles.shape
        )

        pbest_positions = particles.copy()
        pbest_fitness = np.array(
            [self.fitness(tuple(p), p_start, p_end) for p in particles]
        )

        gbest_idx = np.argmin(pbest_fitness)
        gbest_position = particles[gbest_idx].copy()
        gbest_fitness = pbest_fitness[gbest_idx]

        for iteration in range(self.max_iter):
            for i in range(self.swarm_size):

                r1 = np.random.rand(2)
                r2 = np.random.rand(2)

                cognitive = self.c1 * r1 * (pbest_positions[i] - particles[i])
                social = self.c2 * r2 * (gbest_position - particles[i])

                velocities[i] = self.w * velocities[i] + cognitive + social

                velocities[i] = np.clip(
                    velocities[i], -self.max_velocity, self.max_velocity
                )

                particles[i] = particles[i] + velocities[i]

                particles[i] = np.clip(
                    particles[i], [0, 0], [self.width - 1, self.height - 1]
                )

                fitness = self.fitness(tuple(particles[i]), p_start, p_end)

                if fitness < pbest_fitness[i]:
                    pbest_fitness[i] = fitness
                    pbest_positions[i] = particles[i].copy()

                    if fitness < gbest_fitness:
                        gbest_fitness = fitness
                        gbest_position = particles[i].copy()

        optimal_point = (int(round(gbest_position[0])), int(round(gbest_position[1])))

        return optimal_point

    def fitness(
        self,
        point: Tuple[float, float],
        p_start: Tuple[int, int],
        p_end: Tuple[int, int],
    ) -> float:

        if self._is_collision(p_start, point) or self._is_collision(point, p_end):
            return np.inf

        dist1 = self._distance(p_start, point)
        dist2 = self._distance(point, p_end)

        return dist1 + dist2

    def _is_collision(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
    ) -> bool:
        from utils.geometry import voxel_traversal_line

        cells = voxel_traversal_line(p1, p2)

        for x, y in cells:

            if not (0 <= x < self.width and 0 <= y < self.height):
                return True

            if self.grid[y, x] == 1:
                return True

        return False

    def _initialize_particles(
        self,
        p_start: Tuple[int, int],
        p_mid: Tuple[int, int],
        p_end: Tuple[int, int],
    ) -> np.ndarray:
        particles = np.zeros((self.swarm_size, 2))

        for i in range(self.swarm_size):
            if i < self.swarm_size // 2:

                perturbation = np.random.uniform(-3.0, 3.0, size=2)
                particles[i] = (
                    np.array([p_mid[0], p_mid[1]], dtype=float) + perturbation
                )
            else:

                t = np.random.rand()
                x = p_start[0] + t * (p_end[0] - p_start[0])
                y = p_start[1] + t * (p_end[1] - p_start[1])
                perturbation = np.random.uniform(-3.0, 3.0, size=2)
                particles[i] = np.array([x, y], dtype=float) + perturbation

        particles = np.clip(particles, [0, 0], [self.width - 1, self.height - 1])

        return particles

    def _distance(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
    ) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)