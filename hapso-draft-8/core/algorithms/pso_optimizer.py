from config.algo_config import (
    OBSTACLE_RADIUS,
    OPTIMIZER_C1_FINAL,
    OPTIMIZER_C1_INITIAL,
    OPTIMIZER_C2_FINAL,
    OPTIMIZER_C2_INITIAL,
    OPTIMIZER_COGNITIVE_COEFFICIENT,
    OPTIMIZER_MAX_ITERATIONS,
    OPTIMIZER_MAX_VELOCITY,
    OPTIMIZER_N_PARTICLES,
    OPTIMIZER_SEARCH_MARGIN,
    OPTIMIZER_SOBL_MU,
    OPTIMIZER_SOBL_SIGMA,
    OPTIMIZER_SOCIAL_COEFFICIENT,
    OPTIMIZER_USE_TVAC,
    OPTIMIZER_W_MAX,
    OPTIMIZER_W_MIN,
    ROBOT_RADIUS,
    SAFE_DIST,
)
from core.algorithms.base_planner import BasePlanner
from core.utils.inertia_weight import SOBL, siw
from map.grid_map import GridMap

import math
import numpy as np
import random


class PSOptimizer(BasePlanner):
    def __init__(self, grid_map: GridMap, use_tvac: bool = False) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles: np.ndarray = np.array([])

        self.width: int = grid_map.width
        self.height: int = grid_map.height

        self.n_particles: int = OPTIMIZER_N_PARTICLES
        self.max_iter: int = OPTIMIZER_MAX_ITERATIONS
        self.cognitive_coeff: float = OPTIMIZER_COGNITIVE_COEFFICIENT
        self.social_coeff: float = OPTIMIZER_SOCIAL_COEFFICIENT
        self.w_min: float = OPTIMIZER_W_MIN
        self.w_max: float = OPTIMIZER_W_MAX
        self.max_velocity: float = OPTIMIZER_MAX_VELOCITY
        self.search_margin: int = OPTIMIZER_SEARCH_MARGIN

        self.use_tvac: bool = use_tvac
        self.c1_init: float = OPTIMIZER_C1_INITIAL
        self.c1_final: float = OPTIMIZER_C1_FINAL
        self.c2_init: float = OPTIMIZER_C2_INITIAL
        self.c2_final: float = OPTIMIZER_C2_FINAL

        self.sobl: SOBL = SOBL(mu=OPTIMIZER_SOBL_MU, sigma=OPTIMIZER_SOBL_SIGMA)

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        print(
            "[PSO_OPTIMIZER]: find_path() not available - use optimize_segment() instead"
        )
        return None

    def optimize_segment(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> tuple[int, int]:
        self.start = start
        self.goal = end
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        particles = self._init_particles(start, end)
        velocities = self._init_velocities(start, end)

        pbests = [p[:] for p in particles]
        pbest_fits = [self._fitness(start, p, end) for p in particles]

        gbest = max(pbests, key=lambda p: self._fitness(start, p, end))
        gbest_fit = self._fitness(start, gbest, end)

        best_clearance = BasePlanner._min_distance_segment_to_obstacles(
            start, gbest, self.obstacles
        )

        bounds = self._get_bounds(start, end)

        for k in range(self.max_iter):
            w = siw(k, self.max_iter, w_min=self.w_min, w_max=self.w_max)

            for idx in range(self.n_particles):
                velocities[idx] = self._update_velocity(
                    velocities[idx], particles[idx], pbests[idx], gbest, w, k
                )
                particles[idx] = self._update_position(
                    particles[idx], velocities[idx], bounds
                )

                fit = self._fitness(start, particles[idx], end)

                if fit > pbest_fits[idx]:
                    pbests[idx] = particles[idx][:]
                    pbest_fits[idx] = fit

                    if fit > gbest_fit:
                        gbest = particles[idx][:]
                        gbest_fit = fit
                        best_clearance = BasePlanner._min_distance_segment_to_obstacles(
                            start, particles[idx], self.obstacles
                        )
                    elif fit == gbest_fit:
                        curr_clearance = BasePlanner._min_distance_segment_to_obstacles(
                            start, particles[idx], self.obstacles
                        )
                        if curr_clearance > best_clearance:
                            gbest = particles[idx][:]
                            best_clearance = curr_clearance

            gbest, gbest_fit = self._apply_sobl(gbest, gbest_fit, start, end, bounds)
            for idx in range(self.n_particles):
                pbests[idx], pbest_fits[idx] = self._apply_sobl(
                    pbests[idx], pbest_fits[idx], start, end, bounds
                )

        raw_x, raw_y = gbest[0], gbest[1]
        candidates = [
            (round(raw_x), round(raw_y)),
            (math.floor(raw_x), round(raw_y)),
            (math.ceil(raw_x), round(raw_y)),
            (round(raw_x), math.floor(raw_y)),
            (round(raw_x), math.ceil(raw_y)),
        ]

        best_mid = None
        best_cand_clearance = -1.0

        for cx, cy in candidates:
            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue
            if self.grid_map.is_obstacle(cx, cy):
                continue
            if self._segment_has_collision(start, (cx, cy)):
                continue
            if self._segment_has_collision((cx, cy), end):
                continue

            cand_clearance = min(
                BasePlanner._min_distance_segment_to_obstacles(
                    start, (cx, cy), self.obstacles
                ),
                BasePlanner._min_distance_segment_to_obstacles(
                    (cx, cy), end, self.obstacles
                ),
            )

            if cand_clearance > best_cand_clearance:
                best_cand_clearance = cand_clearance
                best_mid = (cx, cy)

        if best_mid is None:
            fallback_mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)

            if (
                not self.grid_map.is_obstacle(fallback_mid[0], fallback_mid[1])
                and not self._segment_has_collision(start, fallback_mid)
                and not self._segment_has_collision(fallback_mid, end)
            ):
                best_mid = fallback_mid
            else:
                best_mid = start

        return best_mid

    def _init_particles(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[list[float]]:
        return [
            [
                start[0] + ((end[0] - start[0]) * random.random()),
                start[1] + ((end[1] - start[1]) * random.random()),
            ]
            for _ in range(self.n_particles)
        ]

    def _get_bounds(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[float, float]]:
        x_min = min(start[0], end[0]) - self.search_margin
        x_max = max(start[0], end[0]) + self.search_margin
        y_min = min(start[1], end[1]) - self.search_margin
        y_max = max(start[1], end[1]) + self.search_margin

        x_min = max(0, x_min)
        x_max = min(self.width - 1, x_max)
        y_min = max(0, y_min)
        y_max = min(self.height - 1, y_max)

        if x_min >= x_max:
            x_max = x_min + 1
        if y_min >= y_max:
            y_max = y_min + 1

        return [(x_min, x_max), (y_min, y_max)]

    def _init_velocities(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[list[float]]:
        return [
            [self.max_velocity * random.random(), self.max_velocity * random.random()]
            for _ in range(self.n_particles)
        ]

    def _update_velocity(
        self,
        vel: list[float],
        pos: list[float],
        pbest: list[float],
        gbest: list[float],
        w: float,
        k: int = 0,
    ) -> list[float]:
        r1, r2 = random.random(), random.random()
        c1, c2 = self._compute_tvac_coefficients(k)

        return [
            w * vel[0] + c1 * r1 * (pbest[0] - pos[0]) + c2 * r2 * (gbest[0] - pos[0]),
            w * vel[1] + c1 * r1 * (pbest[1] - pos[1]) + c2 * r2 * (gbest[1] - pos[1]),
        ]

    def _compute_tvac_coefficients(self, k: int) -> tuple[float, float]:
        if not self.use_tvac:
            return self.cognitive_coeff, self.social_coeff

        t_ratio = k / max(self.max_iter, 1)
        c1_tvac = self.c1_init - (self.c1_init - self.c1_final) * t_ratio
        c2_tvac = self.c2_init + (self.c2_final - self.c2_init) * t_ratio

        return c1_tvac, c2_tvac

    def _update_position(
        self,
        pos: list[float],
        vel: list[float],
        bounds: list[tuple[float, float]],
    ) -> list[float]:
        return [
            max(bounds[0][0], min(bounds[0][1], pos[0] + vel[0])),
            max(bounds[1][0], min(bounds[1][1], pos[1] + vel[1])),
        ]

    def _fitness(
        self, start: tuple[int, int], mid: list[float], end: tuple[int, int]
    ) -> float:
        mid_cell = (round(mid[0]), round(mid[1]))
        path_cells = [start, mid_cell, end]

        for i in range(len(path_cells) - 1):
            if self._segment_has_collision(path_cells[i], path_cells[i + 1]):
                return 0.0

        path_continuous = [
            (float(start[0]), float(start[1])),
            (mid[0], mid[1]),
            (float(end[0]), float(end[1])),
        ]

        start_end_dist = self._euclidean_distance(start, end)

        length = sum(
            self._euclidean_distance(path_continuous[i], path_continuous[i + 1])
            for i in range(len(path_continuous) - 1)
        )
        length_norm = length / max(start_end_dist, 1.0)

        ax = path_continuous[1][0] - path_continuous[0][0]
        ay = path_continuous[1][1] - path_continuous[0][1]
        bx = path_continuous[2][0] - path_continuous[1][0]
        by = path_continuous[2][1] - path_continuous[1][1]

        mag_a = math.sqrt(ax**2 + ay**2)
        mag_b = math.sqrt(bx**2 + by**2)

        if mag_a < 1e-9 or mag_b < 1e-9:
            angle_norm = 0.0
        else:
            cos_angle = max(-1.0, min(1.0, (ax * bx + ay * by) / (mag_a * mag_b)))
            angle_norm = math.acos(cos_angle) / math.pi

        clearance_penalties = []
        min_safe_dist = OBSTACLE_RADIUS + ROBOT_RADIUS

        for i in range(len(path_continuous) - 1):
            dist = BasePlanner._min_distance_segment_to_obstacles(
                path_continuous[i], path_continuous[i + 1], self.obstacles
            )

            if dist < min_safe_dist:
                return 0.0

            if dist < SAFE_DIST:
                penalty_dist = max(dist - OBSTACLE_RADIUS, 1e-9)
                clearance_penalties.append(1.0 / penalty_dist)
            else:
                clearance_penalties.append(0.0)

        if clearance_penalties:
            clearance_sum = sum(clearance_penalties)
            clearance_norm = min(
                clearance_sum
                / len(clearance_penalties)
                / (SAFE_DIST - OBSTACLE_RADIUS),
                1.0,
            )
        else:
            clearance_norm = 0.0

        cost = 0.1 * length_norm + 0.2 * angle_norm + 0.7 * clearance_norm
        return 1.0 / (1.0 + cost)

    def _apply_sobl(
        self,
        pos: list[float],
        fit: float,
        start: tuple[int, int],
        end: tuple[int, int],
        bounds: list[tuple[float, float]],
    ) -> tuple[list[float], float]:
        opp = self.sobl.opposite_vector(pos, bounds)
        opp_fit = self._fitness(start, opp, end)

        if opp_fit > fit:
            return opp, opp_fit

        return pos, fit
