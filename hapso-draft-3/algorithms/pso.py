from .base_planner import BasePlanner
from map.grid_map import GridMap
from optimization import InertiaWeight, SOBL
from typing import List, Optional, Tuple

import math
import numpy as np
import random


class PSOPlanner(BasePlanner):
    V_MAX_MULTIPLIER = 0.1
    EPSILON = 1e-9
    VELOCITY_OFFSET_RANGE = 0.2
    COLLISION_PENALTY_MULTIPLIER = 1000

    def __init__(
        self,
        grid_map: "GridMap",
        optimizer: Optional["PSOOptimizer"] = None,
        n_waypoints: int = 5,
        n_particles: int = 30,
        max_iter: int = 200,
        w: float = 0.7,
        c1: float = 2.0,
        c2: float = 2.0,
    ) -> None:
        super().__init__(grid_map)

        self.optimizer = optimizer

        self.n_waypoints = n_waypoints
        self.n_particles = n_particles
        self.max_iter = max_iter

        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.grid = grid_map.grid
        self.width = grid_map.width
        self.height = grid_map.height

    def find_path(self) -> List[Tuple[int, int]]:
        if not self.validate_input():
            return []

        start = self.grid_map.start
        goal = self.grid_map.goal

        raw_path = self._run_pso(start, goal)

        if not raw_path:
            return []

        if self.optimizer:
            refined = self.optimizer.optimize(raw_path)
        else:
            refined = raw_path

        final_path = self._post_process(refined)

        return self._normalize_path(final_path)

    def _run_pso(self, start, goal):

        particles = [self._init_particle(start, goal) for _ in range(self.n_particles)]

        positions = np.array(particles, dtype=float)
        velocities = np.zeros_like(positions)

        pbest_pos = positions.copy()
        pbest_fit = np.array([self._fitness(p, start, goal) for p in positions])

        gbest_idx = np.argmin(pbest_fit)
        gbest_pos = pbest_pos[gbest_idx].copy()
        gbest_fit = pbest_fit[gbest_idx]

        for iter_i in range(self.max_iter):

            for i in range(self.n_particles):

                random_vec_1 = np.random.random(len(positions[i]))
                random_vec_2 = np.random.random(len(positions[i]))

                w_current = InertiaWeight.siw()

                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * random_vec_1 * (pbest_pos[i] - positions[i])
                    + self.c2 * random_vec_2 * (gbest_pos - positions[i])
                )

                v_max = max(self.width, self.height) * self.V_MAX_MULTIPLIER
                velocities[i] = np.clip(velocities[i], -v_max, v_max)

                positions[i] = positions[i] + velocities[i]
                self._clamp_position(positions[i])

                positions[i] = self._repair_particle(positions[i], start, goal)
                positions[i] = self._smooth_particle(positions[i], start, goal)

                fitness_value = self._fitness(positions[i], start, goal)

                if fitness_value < pbest_fit[i]:
                    pbest_fit[i] = fitness_value
                    pbest_pos[i] = positions[i].copy()

                    if fitness_value < gbest_fit:
                        gbest_fit = fitness_value
                        gbest_pos = positions[i].copy()

        return self._decode_path(gbest_pos, start, goal)

    def _init_particle(self, start, goal):
        (start_x, start_y) = start
        (goal_x, goal_y) = goal

        dx = goal_x - start_x
        dy = goal_y - start_y
        norm = math.sqrt(dx * dx + dy * dy) + self.EPSILON

        perp_x = -dy / norm
        perp_y = dx / norm

        waypoints = []

        for i in range(self.n_waypoints):
            ratio = (i + 1) / (self.n_waypoints + 1)

            base_x = start_x + ratio * dx
            base_y = start_y + ratio * dy

            offset = random.uniform(
                -self.VELOCITY_OFFSET_RANGE, self.VELOCITY_OFFSET_RANGE
            ) * max(self.width, self.height)

            waypoint_x = base_x + perp_x * offset
            waypoint_y = base_y + perp_y * offset

            waypoints.extend([waypoint_x, waypoint_y])

        return waypoints

    def _clamp_position(self, pos):

        for i in range(self.n_waypoints):
            pos[2 * i] = np.clip(pos[2 * i], 0, self.width - 1)
            pos[2 * i + 1] = np.clip(pos[2 * i + 1], 0, self.height - 1)

    def _decode_path(self, pos, start, goal):

        waypoints = []

        for i in range(self.n_waypoints):
            decoded_x = int(round(pos[2 * i]))
            decoded_y = int(round(pos[2 * i + 1]))

            decoded_x = max(0, min(decoded_x, self.width - 1))
            decoded_y = max(0, min(decoded_y, self.height - 1))

            waypoints.append((decoded_x, decoded_y))

        return [start] + waypoints + [goal]

    def _fitness(self, pos, start, goal):

        path = self._decode_path(pos, start, goal)

        total = 0
        penalty = 0

        for i in range(len(path) - 1):

            current_point = path[i]
            next_point = path[i + 1]

            total += self._euclidean(current_point, next_point)
            penalty += (
                self._segment_collision_count(current_point, next_point)
                * self.COLLISION_PENALTY_MULTIPLIER
            )

        return total + penalty

    def _repair_particle(self, pos, start, goal):

        path = self._decode_path(pos, start, goal)

        for i in range(len(path) - 1):
            if self._segment_collision_count(path[i], path[i + 1]) > 0:

                if i > 0 and i < len(path) - 1:
                    mid = (
                        (path[i][0] + path[i + 1][0]) // 2,
                        (path[i][1] + path[i + 1][1]) // 2,
                    )

                    idx = (i - 1) * 2
                    pos[idx] = mid[0]
                    pos[idx + 1] = mid[1]

        return pos

    def _smooth_particle(self, pos, start, goal):

        path = self._decode_path(pos, start, goal)

        new_path = [path[0]]

        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_p = path[i + 1]

            smoothed_x = int((prev[0] + curr[0] + next_p[0]) / 3)
            smoothed_y = int((prev[1] + curr[1] + next_p[1]) / 3)

            new_path.append((smoothed_x, smoothed_y))

        new_path.append(path[-1])

        new_pos = []
        for p in new_path[1:-1]:
            new_pos.extend([p[0], p[1]])

        return np.array(new_pos, dtype=float)


class PSOOptimizer:
    EPSILON = 1e-9
    COLLISION_PENALTY_MULTIPLIER = 1000
    VELOCITY_OFFSET_RANGE = 0.2
    VELOCITY_INIT_RANGE = 1.0
    V_MAX_CLIPPING = 5
    MUTATION_PROBABILITY_SCALE = 0.3
    MUTATION_RANGE = 5
    OFFSET_SCALE = 0.3
    SOBL_MU = 0.5
    SOBL_SIGMA = 0.15

    def __init__(
        self,
        planner: BasePlanner,
        grid_map: Optional["GridMap"],
        n_particles: int = 50,
        max_iter: int = 200,
        c1: float = 1.5,
        c2: float = 1.5,
        w_min: float = 0.4,
        w_max: float = 0.9,
    ):
        self.planner = planner
        self.grid_map = grid_map
        self.n_particles = n_particles
        self.max_iter = max_iter

        self.c1 = c1
        self.c2 = c2

        self.w_min = w_min
        self.w_max = w_max
        self.sobl = SOBL(mu=self.SOBL_MU, sigma=self.SOBL_SIGMA)

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

    def _optimize_segment(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
    ) -> Optional[Tuple[int, int]]:
        particles = self._initialize_segment_particles(start, end)

        velocities = [
            [
                random.uniform(-self.VELOCITY_INIT_RANGE, self.VELOCITY_INIT_RANGE),
                random.uniform(-self.VELOCITY_INIT_RANGE, self.VELOCITY_INIT_RANGE),
            ]
            for _ in range(self.n_particles)
        ]

        fitness = [self._fitness_segment(start, p, end) for p in particles]

        pbest_pos = particles[:]
        pbest_fitness = fitness[:]

        valid_indices = [i for i, f in enumerate(fitness) if f > 0]
        if not valid_indices:
            return None

        gbest_idx = min(valid_indices, key=lambda i: fitness[i])
        gbest_pos = particles[gbest_idx]
        gbest_fitness = fitness[gbest_idx]

        for iteration in range(self.max_iter):

            w_current = InertiaWeight.siw(
                iteration + 1, self.max_iter, w_min=self.w_min, w_max=self.w_max
            )

            for i in range(self.n_particles):

                particle_x, particle_y = particles[i]
                velocity_x, velocity_y = velocities[i]

                random_coeff_1 = random.random()
                random_coeff_2 = random.random()

                pbest_x, pbest_y = pbest_pos[i]
                gbest_x, gbest_y = gbest_pos

                mutation_prob = self.MUTATION_PROBABILITY_SCALE * w_current

                if random.random() < mutation_prob:
                    mutation_delta_x = random.randint(
                        -self.MUTATION_RANGE, self.MUTATION_RANGE
                    )
                    mutation_delta_y = random.randint(
                        -self.MUTATION_RANGE, self.MUTATION_RANGE
                    )

                    particle_x += mutation_delta_x
                    particle_y += mutation_delta_y
                else:
                    velocity_x = (
                        w_current * velocity_x
                        + self.c1 * random_coeff_1 * (pbest_x - particle_x)
                        + self.c2 * random_coeff_2 * (gbest_x - particle_x)
                    )
                    velocity_y = (
                        w_current * velocity_y
                        + self.c1 * random_coeff_1 * (pbest_y - particle_y)
                        + self.c2 * random_coeff_2 * (gbest_y - particle_y)
                    )

                    velocity_max = self.V_MAX_CLIPPING
                    velocity_x = max(-velocity_max, min(velocity_x, velocity_max))
                    velocity_y = max(-velocity_max, min(velocity_y, velocity_max))

                    particle_x += velocity_x
                    particle_y += velocity_y

                particle_x = int(
                    round(max(0, min(particle_x, self.grid_map.width - 1)))
                )
                particle_y = int(
                    round(max(0, min(particle_y, self.grid_map.height - 1)))
                )

                particles[i] = (particle_x, particle_y)
                velocities[i] = [velocity_x, velocity_y]

                fitness_segment = self._fitness_segment(start, particles[i], end)

                if fitness_segment > 0:
                    if pbest_fitness[i] == 0 or fitness_segment < pbest_fitness[i]:
                        pbest_fitness[i] = fitness_segment
                        pbest_pos[i] = particles[i]

                        if fitness_segment < gbest_fitness:
                            gbest_fitness = fitness_segment
                            gbest_pos = particles[i]

            for i in range(self.n_particles):
                if pbest_fitness[i] > 0:

                    bounds = [
                        [0, self.grid_map.width - 1],
                        [0, self.grid_map.height - 1],
                    ]

                    opposite = self.sobl.opposite_vector(pbest_pos[i], bounds)
                    opposite = tuple(int(round(coord)) for coord in opposite)

                    opposite = (
                        max(0, min(opposite[0], self.grid_map.width - 1)),
                        max(0, min(opposite[1], self.grid_map.height - 1)),
                    )

                    f_op = self._fitness_segment(start, opposite, end)

                    if f_op > 0 and f_op < pbest_fitness[i]:
                        pbest_pos[i] = opposite
                        pbest_fitness[i] = f_op

                        if f_op < gbest_fitness:
                            gbest_fitness = f_op
                            gbest_pos = opposite

        return gbest_pos if gbest_fitness > 0 else None

    def _initialize_segment_particles(self, start, end):
        particles = []

        (start_x, start_y) = start
        (end_x, end_y) = end

        delta_x = end_x - start_x
        delta_y = end_y - start_y
        dist = math.sqrt(delta_x * delta_x + delta_y * delta_y) + 1e-9

        normal_x = -delta_y / dist
        normal_y = delta_x / dist

        for _ in range(self.n_particles):

            segment_param = random.random()

            base_x = start_x + delta_x * segment_param
            base_y = start_y + delta_y * segment_param

            offset = random.uniform(-dist * self.OFFSET_SCALE, dist * self.OFFSET_SCALE)

            particle_x = int(round(base_x + normal_x * offset))
            particle_y = int(round(base_y + normal_y * offset))

            particle_x = max(0, min(particle_x, self.grid_map.width - 1))
            particle_y = max(0, min(particle_y, self.grid_map.height - 1))

            particles.append((particle_x, particle_y))

        return particles

    def _fitness_segment(self, start, mid, end):
        if not self.planner._is_valid(mid[0], mid[1]):
            return 0.0

        if self.planner._segment_collision_count(start, mid) > 0:
            return 0.0

        if self.planner._segment_collision_count(mid, end) > 0:
            return 0.0

        return self.planner._euclidean(start, mid) + self.planner._euclidean(mid, end)

    def _post_process(self, path):
        if len(path) <= 2:
            return path

        optimized = [path[0]]
        i = 1

        while i < len(path) - 1:
            prev = optimized[-1]
            next_p = path[i + 1]

            if self._segment_collision_count(prev, next_p) == 0:
                i += 1
                continue

            optimized.append(path[i])
            i += 1

        optimized.append(path[-1])

        return optimized
