from algorithms.base_planner import Planner
from config import COLLISION_PENALTY_WEIGHT, ROBOT_RADIUS, SAFE_DIST, OBSTACLE_RADIUS
from map import GridMap
from optimization.inertia_weight import SIW, SOBL
from typing import List, Optional, Tuple

import math
import numpy as np
import random


class PSOptimizer(Planner):
    def __init__(
        self,
        grid_map: GridMap,
        n_particles: int = 20,
        max_iter: int = 100,
        c1: float = 2.0,
        c2: float = 2.0,
        w_min: float = 0.4,
        w_max: float = 0.9,
        mu: float = 0.5,
        sigma: float = 0.15,
        use_tvac: bool = True,
        c1_init: float = 2.5,
        c1_final: float = 0.5,
        c2_init: float = 0.5,
        c2_final: float = 2.5,
    ) -> None:
        self.grid_map = grid_map
        self.width = grid_map.width
        self.height = grid_map.height
        self.start = grid_map.start
        self.goal = grid_map.goal
        self.obstacles = grid_map.get_obstacles_as_centers()

        self.n_particles = n_particles
        self.max_iter = max_iter

        self.c1 = c1
        self.c2 = c2
        self.w_min = w_min
        self.w_max = w_max
        self.mu = mu
        self.sigma = sigma

        self.use_tvac = use_tvac
        self.c1_init = c1_init
        self.c1_final = c1_final
        self.c2_init = c2_init
        self.c2_final = c2_final

        self.inertia_weight = SIW(w_min=w_min, w_max=w_max)
        self.sobl = SOBL(mu=self.mu, sigma=self.sigma)

    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        raise NotImplementedError(
            "PSOptimizer is an optimizer, not a planner. Use optimize() method."
        )

    def optimize(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if len(path) < 3:
            return path

        optimized = [path[0]]

        for i in range(0, len(path) - 2):
            anchor_start = optimized[-1]
            anchor_end = path[i + 2]
            original_waypoint = path[i + 1]

            best_mid = self._optimize_segment(anchor_start, anchor_end)

            # Check for collision
            collision_detected = self._segment_has_collision(
                anchor_start, best_mid
            ) or self._segment_has_collision(best_mid, anchor_end)

            if not collision_detected:
                # BUG FIX 2: Also check clearance — reject if worse than original
                best_clearance = min(
                    Planner._min_distance_segment_to_obstacles(
                        anchor_start, best_mid, self.obstacles
                    ),
                    Planner._min_distance_segment_to_obstacles(
                        best_mid, anchor_end, self.obstacles
                    ),
                )
                orig_clearance = min(
                    Planner._min_distance_segment_to_obstacles(
                        anchor_start, original_waypoint, self.obstacles
                    ),
                    Planner._min_distance_segment_to_obstacles(
                        original_waypoint, anchor_end, self.obstacles
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
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Tuple[int, int]:
        particles = self._init_particles(start, end)
        velocities = self._init_velocities(start, end)

        pbests = [p[:] for p in particles]
        pbest_fits = [self._fitness(start, p, end) for p in particles]

        gbest = max(pbests, key=lambda p: self._fitness(start, p, end))
        gbest_fit = self._fitness(start, gbest, end)

        best_clearance = Planner._min_distance_segment_to_obstacles(
            start, gbest, self.obstacles
        )

        bounds = self._get_bounds(start, end)

        for k in range(self.max_iter):
            w = self.inertia_weight.compute(k, self.max_iter)

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
                        best_clearance = Planner._min_distance_segment_to_obstacles(
                            start, particles[idx], self.obstacles
                        )
                    elif fit == gbest_fit:
                        # Tiebreaker: if same fitness, prefer higher clearance
                        curr_clearance = Planner._min_distance_segment_to_obstacles(
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

        # BUG FIX 3: Try multiple rounded candidates around gbest
        # and choose the one with best clearance (not just simple rounding)
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
            # Check bounds
            if not (0 <= cx < self.width and 0 <= cy < self.height):
                continue

            # Check if obstacle
            if self.grid_map.is_obstacle(cx, cy):
                continue

            # Check if collision on segments
            if self._segment_has_collision(start, (cx, cy)):
                continue
            if self._segment_has_collision((cx, cy), end):
                continue

            # Calculate clearance for this candidate
            cand_clearance = min(
                Planner._min_distance_segment_to_obstacles(
                    start, (cx, cy), self.obstacles
                ),
                Planner._min_distance_segment_to_obstacles(
                    (cx, cy), end, self.obstacles
                ),
            )

            # Keep candidate with best clearance
            if cand_clearance > best_cand_clearance:
                best_cand_clearance = cand_clearance
                best_mid = (cx, cy)

        # Fallback if no valid candidate found
        if best_mid is None:
            fallback_mid = (
                (start[0] + end[0]) // 2,
                (start[1] + end[1]) // 2,
            )

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
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[List[float]]:
        bounds = self._get_bounds(start, end)
        return [
            [
                random.uniform(bounds[0][0], bounds[0][1]),
                random.uniform(bounds[1][0], bounds[1][1]),
            ]
            for _ in range(self.n_particles)
        ]

    def _get_bounds(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[float, float]]:
        MARGIN = 3

        x_min = min(start[0], end[0]) - MARGIN
        x_max = max(start[0], end[0]) + MARGIN
        y_min = min(start[1], end[1]) - MARGIN
        y_max = max(start[1], end[1]) + MARGIN

        x_min = max(0, x_min)
        x_max = min(self.width - 1, x_max)
        y_min = max(0, y_min)
        y_max = min(self.height - 1, y_max)

        if x_min >= x_max:
            x_max = x_min + 1
        if y_min >= y_max:
            y_max = y_min + 1

        return [
            (x_min, x_max),
            (y_min, y_max),
        ]

    def _init_velocities(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[List[float]]:
        dx = abs(end[0] - start[0]) or 1
        dy = abs(end[1] - start[1]) or 1

        return [
            [random.uniform(-dx, dx), random.uniform(-dy, dy)]
            for _ in range(self.n_particles)
        ]

    def _update_velocity(
        self,
        vel: List[float],
        pos: List[float],
        pbest: List[float],
        gbest: List[float],
        w: float,
        k: int = 0,
    ) -> List[float]:
        r1, r2 = random.random(), random.random()
        c1, c2 = self._compute_tvac_coefficients(k)

        return [
            w * vel[0] + c1 * r1 * (pbest[0] - pos[0]) + c2 * r2 * (gbest[0] - pos[0]),
            w * vel[1] + c1 * r1 * (pbest[1] - pos[1]) + c2 * r2 * (gbest[1] - pos[1]),
        ]

    def _compute_tvac_coefficients(self, k: int):
        if not self.use_tvac:
            return self.c1, self.c2

        t_ratio = k / max(self.max_iter, 1)
        c1_tvac = self.c1_init - (self.c1_init - self.c1_final) * t_ratio
        c2_tvac = self.c2_init + (self.c2_final - self.c2_init) * t_ratio

        return c1_tvac, c2_tvac

    def _update_position(
        self,
        pos: List[float],
        vel: List[float],
        bounds: List[Tuple[float, float]],
    ) -> List[float]:
        return [
            max(bounds[0][0], min(bounds[0][1], pos[0] + vel[0])),
            max(bounds[1][0], min(bounds[1][1], pos[1] + vel[1])),
        ]

    def _fitness(
        self, start: Tuple[int, int], mid: List[float], end: Tuple[int, int]
    ) -> float:
        mid_cell = (round(mid[0]), round(mid[1]))
        path_cells = [start, mid_cell, end]

        # Collision check on grid cells (discrete raster check)
        for i in range(len(path_cells) - 1):
            if self._segment_has_collision(path_cells[i], path_cells[i + 1]):
                return 0.0

        # ─────────────────────────────────────────────────────────────────
        # Fitness evaluation on CONTINUOUS path (using continuous mid)
        # This gives PSO gradient to optimize within each grid cell
        # ─────────────────────────────────────────────────────────────────
        path_continuous = [
            (float(start[0]), float(start[1])),
            (mid[0], mid[1]),  # continuous float coordinates
            (float(end[0]), float(end[1])),
        ]

        start_goal_distance = self._euclidean_distance(start, end)
        length = sum(
            self._euclidean_distance(path_continuous[i], path_continuous[i + 1])
            for i in range(len(path_continuous) - 1)
        )
        length_norm = length / max(start_goal_distance, 1.0)

        # Angle calculation on continuous path
        angle_total = 0.0
        for i in range(1, len(path_continuous) - 1):
            ax = path_continuous[i][0] - path_continuous[i - 1][0]
            ay = path_continuous[i][1] - path_continuous[i - 1][1]
            bx = path_continuous[i + 1][0] - path_continuous[i][0]
            by = path_continuous[i + 1][1] - path_continuous[i][1]

            mag_a = math.sqrt(ax**2 + ay**2)
            mag_b = math.sqrt(bx**2 + by**2)

            if mag_a < 1e-9 or mag_b < 1e-9:
                continue

            cos_angle = max(-1.0, min(1.0, (ax * bx + ay * by) / (mag_a * mag_b)))
            angle_total += math.acos(cos_angle)

        angle_norm = angle_total / max((len(path_continuous) - 2) * math.pi, 1e-9)

        # Clearance calculation on continuous path (NOW PSO HAS REAL GRADIENT)
        clearance_penalties = []
        min_safe_dist = OBSTACLE_RADIUS + ROBOT_RADIUS

        for i in range(len(path_continuous) - 1):
            dist = Planner._min_distance_segment_to_obstacles(
                path_continuous[i], path_continuous[i + 1], self.obstacles
            )

            # Hard cutoff: too close to obstacle
            if dist < min_safe_dist:
                return 0.0

            # Gradient penalty for unsafe distances (continuous)
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
        pos: List[float],
        fit: float,
        start: Tuple[int, int],
        end: Tuple[int, int],
        bounds: List[Tuple[float, float]],
    ) -> Tuple[List[float], float]:
        opp = self.sobl.opposite_vector(pos, bounds)
        opp_fit = self._fitness(start, opp, end)

        if opp_fit > fit:
            return opp, opp_fit

        return pos, fit


class GridMap:
    def get_obstacles_as_centers(self) -> np.ndarray:
        return np.array(
            [
                [c + 0.5, r + 0.5]
                for r in range(self.height)
                for c in range(self.width)
                if self.grid[r][c] == self.OBSTACLE
            ],
            dtype=float,
        )


class Planner:
    def _segment_has_collision(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        cells = LineDrawer.incremental(a, b)
        for cx, cy in cells:
            if not self.grid_map.is_inside(cx, cy) or self.grid_map.is_obstacle(cx, cy):
                return True

        min_distance = Planner._min_distance_segment_to_obstacles(a, b, self.obstacles)

        # BUG FIX: Obstacles stored as centers (c+0.5, r+0.5)
        # Distance to center must subtract OBSTACLE_RADIUS to get distance to edge
        return min_distance < (OBSTACLE_RADIUS + ROBOT_RADIUS)

    @staticmethod
    def _min_distance_segment_to_obstacles(
        a: Tuple[int, int], b: Tuple[int, int], obstacles: np.ndarray
    ) -> float:
        if len(obstacles) == 0:
            return 1980.0

        p1 = np.array([float(a[0]), float(a[1])])
        p2 = np.array([float(b[0]), float(b[1])])
        segment_vector = p2 - p1
        vector_norm_sq = np.dot(segment_vector, segment_vector)

        if vector_norm_sq < 1e-9:
            distances = np.linalg.norm(obstacles - p1, axis=1)
        else:
            projection_param = np.clip(
                np.dot(obstacles - p1, segment_vector) / vector_norm_sq, 0.0, 1.0
            )
            proj = p1 + projection_param[:, np.newaxis] * segment_vector
            distances = np.linalg.norm(obstacles - proj, axis=1)

        return float(np.min(distances))


class LineDrawer:
    @staticmethod
    def incremental(
        start: Tuple[int, int], goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        x1, y1 = start
        x2, y2 = goal
        cells = []
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return [start]
        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
        step_y = 1 if dy > 0 else -1 if dy < 0 else 0
        dx = abs(dx)
        dy = abs(dy)
        if dx != 0:
            t_delta_x = 1.0 / dx
            if step_x > 0:
                t_max_x = (math.ceil(x1) - x1) * t_delta_x
                if abs(t_max_x) < 1e-10:
                    t_max_x = t_delta_x
            else:
                t_max_x = (x1 - math.floor(x1)) * t_delta_x
                if abs(t_max_x) < 1e-10:
                    t_max_x = t_delta_x
        else:
            t_delta_x = float("inf")
            t_max_x = float("inf")
        if dy != 0:
            t_delta_y = 1.0 / dy
            if step_y > 0:
                t_max_y = (math.ceil(y1) - y1) * t_delta_y
                if abs(t_max_y) < 1e-10:
                    t_max_y = t_delta_y
            else:
                t_max_y = (y1 - math.floor(y1)) * t_delta_y
                if abs(t_max_y) < 1e-10:
                    t_max_y = t_delta_y
        else:
            t_delta_y = float("inf")
            t_max_y = float("inf")
        x, y = x1, y1
        cells.append((x, y))
        while x != x2 or y != y2:
            if abs(t_max_x - t_max_y) < 1e-10:
                cells.append((x + step_x, y))
                cells.append((x, y + step_y))
                t_max_x += t_delta_x
                t_max_y += t_delta_y
                x += step_x
                y += step_y
            elif t_max_x < t_max_y:
                t_max_x += t_delta_x
                x += step_x
            else:
                t_max_y += t_delta_y
                y += step_y
            cells.append((x, y))
        return cells
