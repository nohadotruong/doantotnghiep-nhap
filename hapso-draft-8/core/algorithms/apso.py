from config.algo_config import (
    OPTIMIZER_COGNITIVE_COEFFICIENT,
    OPTIMIZER_MAX_ITERATIONS,
    OPTIMIZER_MAX_VELOCITY,
    OPTIMIZER_N_PARTICLES,
    OPTIMIZER_SEARCH_MARGIN,
    OPTIMIZER_SOBL_MU,
    OPTIMIZER_SOBL_SIGMA,
    OPTIMIZER_SOCIAL_COEFFICIENT,
    OPTIMIZER_W_MAX,
    OPTIMIZER_W_MIN,
)
from core.algorithms.astar import Astar
from core.algorithms.base_planner import BasePlanner
from core.utils.inertia_weight import SOBL, siw
from core.utils.path_smoother import PathSmoother
from map.grid_map import GridMap

import math
import numpy as np
import random


class APSO(BasePlanner):
    def __init__(self, grid_map: GridMap) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles: np.ndarray = np.array([])

        self.width: int = grid_map.width
        self.height: int = grid_map.height

        self.astar = Astar(grid_map)

        self.n_particles: int = OPTIMIZER_N_PARTICLES
        self.max_iter: int = OPTIMIZER_MAX_ITERATIONS
        self.cognitive_coeff: float = OPTIMIZER_COGNITIVE_COEFFICIENT
        self.social_coeff: float = OPTIMIZER_SOCIAL_COEFFICIENT
        self.w_min: float = OPTIMIZER_W_MIN
        self.w_max: float = OPTIMIZER_W_MAX
        self.max_velocity: float = OPTIMIZER_MAX_VELOCITY
        self.search_margin: int = OPTIMIZER_SEARCH_MARGIN

        self.sobl: SOBL = SOBL(mu=OPTIMIZER_SOBL_MU, sigma=OPTIMIZER_SOBL_SIGMA)

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal

        a_star_path = self.astar.plan()

        if not a_star_path:
            return None

        key_nodes = PathSmoother._remove_collinear(a_star_path)

        if len(key_nodes) < 2:
            return a_star_path

        optimized_path = self._optimize_segments(key_nodes)

        return optimized_path if optimized_path else a_star_path

    def _optimize_segments(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(path) < 3:
            return path

        optimized = [path[0]]

        for i in range(0, len(path) - 2):
            anchor_start = optimized[-1]
            anchor_end = path[i + 2]
            original_waypoint = path[i + 1]

            best_mid = self._optimize_segment(anchor_start, anchor_end)

            collision_detected = self._segment_has_collision(
                anchor_start, best_mid
            ) or self._segment_has_collision(best_mid, anchor_end)

            if not collision_detected:
                best_clearance = min(
                    BasePlanner._min_distance_segment_to_obstacles(
                        anchor_start, best_mid, self.grid_map.get_obstacles_as_centers()
                    ),
                    BasePlanner._min_distance_segment_to_obstacles(
                        best_mid, anchor_end, self.grid_map.get_obstacles_as_centers()
                    ),
                )
                orig_clearance = min(
                    BasePlanner._min_distance_segment_to_obstacles(
                        anchor_start,
                        original_waypoint,
                        self.grid_map.get_obstacles_as_centers(),
                    ),
                    BasePlanner._min_distance_segment_to_obstacles(
                        original_waypoint,
                        anchor_end,
                        self.grid_map.get_obstacles_as_centers(),
                    ),
                )

                if best_clearance < orig_clearance:
                    best_mid = original_waypoint
            else:
                best_mid = original_waypoint

            optimized.append(best_mid)

        optimized.append(path[-1])

        return optimized

    def _optimize_segment(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> tuple[int, int]:
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        particles = self._init_particles(start, end)
        velocities = self._init_velocities(start, end)

        pbests = [p[:] for p in particles]
        pbest_fits = [self._fitness(start, p, end) for p in particles]

        gbest = max(pbests, key=lambda p: self._fitness(start, p, end))
        gbest_fit = self._fitness(start, gbest, end)

        bounds = self._get_bounds(start, end)

        for k in range(self.max_iter):
            w = siw(k, self.max_iter, w_min=self.w_min, w_max=self.w_max)

            for idx in range(self.n_particles):
                velocities[idx] = self._update_velocity(
                    velocities[idx], particles[idx], pbests[idx], gbest, w
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
        best_fit = -float("inf")

        for cx, cy in candidates:
            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue
            if self.grid_map.is_obstacle(cx, cy):
                continue
            if self._segment_has_collision(start, (cx, cy)):
                continue
            if self._segment_has_collision((cx, cy), end):
                continue

            cand_fit = self._fitness(start, [cx, cy], end)
            if cand_fit > best_fit:
                best_fit = cand_fit
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
    ) -> list[float]:
        r1, r2 = random.random(), random.random()
        c1, c2 = self.cognitive_coeff, self.social_coeff

        return [
            w * vel[0] + c1 * r1 * (pbest[0] - pos[0]) + c2 * r2 * (gbest[0] - pos[0]),
            w * vel[1] + c1 * r1 * (pbest[1] - pos[1]) + c2 * r2 * (gbest[1] - pos[1]),
        ]

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

        d = sum(
            self._euclidean_distance(path_continuous[i], path_continuous[i + 1])
            for i in range(len(path_continuous) - 1)
        )

        return 1.0 / (1.0 + d)

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
