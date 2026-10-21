from collections import deque
from config.algo_config import (
    COLLISION_PENALTY_WEIGHT,
    OBSTACLE_RADIUS,
    OPTIMIZER_C1_FINAL,
    OPTIMIZER_C1_INITIAL,
    OPTIMIZER_C2_FINAL,
    OPTIMIZER_C2_INITIAL,
    OPTIMIZER_COGNITIVE_COEFFICIENT,
    OPTIMIZER_MAX_ITERATIONS,
    OPTIMIZER_N_PARTICLES,
    OPTIMIZER_SEARCH_MARGIN,
    OPTIMIZER_SOBL_MU,
    OPTIMIZER_SOBL_SIGMA,
    OPTIMIZER_SOCIAL_COEFFICIENT,
    OPTIMIZER_USE_TVAC,
    OPTIMIZER_W_MAX,
    OPTIMIZER_W_MIN,
    PSO_COGNITIVE_COEFFICIENT,
    PSO_INERTIA_WEIGHT,
    PSO_JITTER,
    PSO_MAX_ITERATIONS,
    PSO_MAX_RESTARTS,
    PSO_MAX_SPEED,
    PSO_N_CONTROL_POINTS,
    PSO_N_PARTICLES,
    PSO_N_WAYPOINTS,
    PSO_PATIENCE,
    PSO_PATIENCE_TOLERANCE,
    PSO_RETRY_UNTIL_SUCCESS,
    PSO_SMOOTH_ALPHA,
    PSO_SMOOTH_ROUNDS,
    PSO_SOBL_MU,
    PSO_SOBL_SIGMA,
    PSO_SOCIAL_COEFFICIENT,
    PSO_W_MAX,
    PSO_W_MIN,
    ROBOT_RADIUS,
    SAFE_DIST,
)
from core.algorithms.base_planner import Planner
from core.utils.inertia_weight import SIW, SOBL
from map.grid_map import GridMap

import math
import numpy as np
import random


class PSOPlanner(Planner):
    def __init__(
        self, grid_map: GridMap, use_siw: bool = False, use_sobl: bool = False
    ) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles: np.ndarray = np.array([])

        self.width: int = grid_map.width
        self.height: int = grid_map.height

        self.n_waypoints: int = PSO_N_WAYPOINTS
        self.n_particles: int = PSO_N_PARTICLES
        self.max_iter: int = PSO_MAX_ITERATIONS
        self.inertia_weight_base: float = PSO_INERTIA_WEIGHT
        self.cognitive_coeff: float = PSO_COGNITIVE_COEFFICIENT
        self.social_coeff: float = PSO_SOCIAL_COEFFICIENT
        self.w_max: float = PSO_W_MAX
        self.w_min: float = PSO_W_MIN
        self.max_speed: float = PSO_MAX_SPEED
        self.patience: int = PSO_PATIENCE
        self.patience_tolerance: float = PSO_PATIENCE_TOLERANCE
        self.max_restarts: int | None = PSO_MAX_RESTARTS
        self.retry_until_success: bool = PSO_RETRY_UNTIL_SUCCESS

        self.n_ctrl_points: int = PSO_N_CONTROL_POINTS
        self.jitter: float = PSO_JITTER
        self.smooth_alpha: float = PSO_SMOOTH_ALPHA
        self.smooth_rounds: int = PSO_SMOOTH_ROUNDS

        self.use_siw: bool = use_siw
        self.use_sobl: bool = use_sobl

        if use_siw:
            self.inertia_weight: SIW | None = SIW(w_min=self.w_min, w_max=self.w_max)
        else:
            self.inertia_weight = None

        if use_sobl:
            self.sobl: SOBL | None = SOBL(mu=PSO_SOBL_MU, sigma=PSO_SOBL_SIGMA)
        else:
            self.sobl = None

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        if not self._validate_inputs():
            return None

        attempts = 0
        while True:
            gbest_path = self._run_pso()
            path = self._postprocess(gbest_path)

            if path:
                return path

            attempts += 1
            if not self.retry_until_success:
                return None
            if self.max_restarts is not None and attempts >= self.max_restarts:
                return None

    def _run_pso(self) -> np.ndarray:
        M = self.n_waypoints
        start_arr = np.array(self.start, dtype=float)
        goal_arr = np.array(self.goal, dtype=float)

        positions = np.array(
            [self._init_spline_particle() for _ in range(self.n_particles)],
            dtype=float,
        )
        velocities = np.zeros_like(positions)
        costs = np.array([self._cost(p) for p in positions])
        pbest_pos = positions.copy()
        pbest_cost = costs.copy()

        gbest_idx = np.argmin(pbest_cost)
        gbest_pos = pbest_pos[gbest_idx].copy()
        gbest_cost = pbest_cost[gbest_idx]

        best_cost_prev = float("inf")
        no_improve = 0

        for iteration in range(self.max_iter):
            if self.inertia_weight is not None:
                w = self.inertia_weight.compute(iteration, self.max_iter)
            else:
                w = self.inertia_weight_base

            for i in range(self.n_particles):
                r1 = np.random.rand(M, 2)
                r2 = np.random.rand(M, 2)

                cognitive = self.cognitive_coeff * r1 * (pbest_pos[i] - positions[i])
                social = self.social_coeff * r2 * (gbest_pos - positions[i])
                velocities[i] = w * velocities[i] + cognitive + social

                speed = np.linalg.norm(velocities[i], axis=1, keepdims=True)
                scale = np.minimum(1.0, self.max_speed / (speed + 1e-9))
                velocities[i] *= scale

                positions[i] += velocities[i]
                positions[i] = self._repair_continuous(positions[i])
                positions[i] = self._smooth_path(
                    positions[i],
                    alpha=self.smooth_alpha,
                    rounds=self.smooth_rounds,
                )
                positions[i][0] = start_arr
                positions[i][-1] = goal_arr

                if self.sobl is not None:
                    flat = positions[i].flatten()
                    bounds_flat = [[0, self.width - 1], [0, self.height - 1]] * M
                    opp_flat = np.array(
                        self.sobl.opposite_vector(flat, bounds_flat), dtype=float
                    )
                    opp = opp_flat.reshape(M, 2)
                    opp = np.clip(opp, [0, 0], [self.width - 1, self.height - 1])
                    opp[0] = start_arr
                    opp[-1] = goal_arr
                    opp_cost = self._cost(opp)
                    c = self._cost(positions[i])
                    if opp_cost < c:
                        positions[i] = opp
                        c = opp_cost
                else:
                    c = self._cost(positions[i])

                if c < pbest_cost[i]:
                    pbest_cost[i] = c
                    pbest_pos[i] = positions[i].copy()
                    if c < gbest_cost:
                        gbest_cost = c
                        gbest_pos = positions[i].copy()

            if gbest_cost < best_cost_prev - self.patience_tolerance:
                best_cost_prev = gbest_cost
                no_improve = 0
            else:
                no_improve += 1

            if no_improve >= self.patience:
                break

        return gbest_pos

    def _postprocess(self, gbest: np.ndarray) -> list[tuple[int, int]] | None:
        pts: list[tuple[int, int]] = [
            (
                int(np.clip(round(gbest[i, 0]), 0, self.width - 1)),
                int(np.clip(round(gbest[i, 1]), 0, self.height - 1)),
            )
            for i in range(len(gbest))
        ]

        unique: list[tuple[int, int]] = []
        for pt in pts:
            if not unique or pt != unique[-1]:
                unique.append(pt)

        if not unique or unique[0] != self.start:
            unique = [self.start] + unique
        if unique[-1] != self.goal:
            unique.append(self.goal)

        waypoints = unique[1:-1]
        waypoints = self._shrink_waypoints(waypoints)
        path = [self.start] + waypoints + [self.goal]

        path = self._repair_path_list(path)

        for i in range(len(path) - 1):
            if self._segment_has_collision(path[i], path[i + 1]):
                return None

        return path

    def _shrink_waypoints(
        self, waypoints: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        if not waypoints:
            return []

        points = [self.start] + waypoints + [self.goal]
        kept = [points[0]]

        for i in range(1, len(points) - 1):
            if self._segment_has_collision(
                kept[-1], points[i + 1]
            ) or self._segment_has_collision(kept[-1], points[i]):
                kept.append(points[i])

        kept.append(points[-1])
        return kept[1:-1]

    def _repair_path_list(
        self, path: list[tuple[int, int]], max_attempts: int = 5
    ) -> list[tuple[int, int]]:
        repaired = list(path)

        for _ in range(max_attempts):
            changed = False
            new_path = [repaired[0]]

            for i in range(len(repaired) - 1):
                a, b = repaired[i], repaired[i + 1]

                if self._segment_has_collision(a, b):
                    mid = self._find_clear_midpoint(a, b)
                    if mid is not None:
                        new_path.extend([mid, b])
                        changed = True
                    else:
                        detour = self._bfs_local_path(a, b)
                        if detour:
                            new_path.extend(detour + [b])
                            changed = True
                        else:
                            new_path.append(b)
                else:
                    new_path.append(b)

            repaired = new_path
            if not changed:
                break

        return repaired

    def _bfs_local_path(
        self, a: tuple[int, int], b: tuple[int, int]
    ) -> list[tuple[int, int | None]]:
        obstacle_set = {(int(round(ox)), int(round(oy))) for ox, oy in self.obstacles}
        ia = (int(round(a[0])), int(round(a[1])))
        ib = (int(round(b[0])), int(round(b[1])))

        if ia == ib:
            return []

        budget = self.width * self.height
        queue: deque = deque([(ia, [])])
        visited = {ia}

        while queue:
            cur, path_to_cur = queue.popleft()

            if cur == ib:
                return path_to_cur

            if len(path_to_cur) >= budget:
                continue

            cx, cy = cur
            neighbors = [
                (cx - 1, cy),
                (cx + 1, cy),
                (cx, cy - 1),
                (cx, cy + 1),
                (cx - 1, cy - 1),
                (cx - 1, cy + 1),
                (cx + 1, cy - 1),
                (cx + 1, cy + 1),
            ]

            for nx, ny in neighbors:
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                nb = (nx, ny)
                if nb in obstacle_set or nb in visited:
                    continue
                visited.add(nb)
                queue.append((nb, path_to_cur + [nb]))

        return None

    def _find_clear_midpoint(
        self,
        a: tuple[int, int],
        b: tuple[int, int],
        n_candidates: int = 12,
    ) -> tuple[int, int | None]:
        mid_x = (a[0] + b[0]) / 2.0
        mid_y = (a[1] + b[1]) / 2.0

        perp_x = -(b[1] - a[1])
        perp_y = b[0] - a[0]
        length = math.sqrt(perp_x**2 + perp_y**2)

        if length < 1e-9:
            return None

        perp_x /= length
        perp_y /= length

        search_radius = max(5, int(self._euclidean_distance(a, b) * 0.6))

        for k in range(1, n_candidates + 1):
            sign = 1 if k % 2 == 0 else -1
            offset = sign * (k // 2 + 1) * (search_radius / (n_candidates // 2))
            cx = int(np.clip(round(mid_x + perp_x * offset), 0, self.width - 1))
            cy = int(np.clip(round(mid_y + perp_y * offset), 0, self.height - 1))
            candidate = (cx, cy)

            if not self._segment_has_collision(
                a, candidate
            ) and not self._segment_has_collision(candidate, b):
                return candidate

        return None

    def _cost(self, path: np.ndarray) -> float:
        pts = [(float(p[0]), float(p[1])) for p in path]
        n = len(pts)

        if n < 2:
            return float("inf")

        start_goal_dist = self._euclidean_distance(self.start, self.goal)

        length = sum(self._euclidean_distance(pts[i], pts[i + 1]) for i in range(n - 1))
        length_norm = length / max(start_goal_dist, 1.0)

        angle_total = 0.0
        for i in range(1, n - 1):
            ax = pts[i][0] - pts[i - 1][0]
            ay = pts[i][1] - pts[i - 1][1]
            bx = pts[i + 1][0] - pts[i][0]
            by = pts[i + 1][1] - pts[i][1]
            ma = math.sqrt(ax**2 + ay**2)
            mb = math.sqrt(bx**2 + by**2)
            if ma < 1e-9 or mb < 1e-9:
                continue
            cos_a = max(-1.0, min(1.0, (ax * bx + ay * by) / (ma * mb)))
            angle_total += math.acos(cos_a)

        angle_norm = angle_total / max((n - 2) * math.pi, 1e-9)

        collision_count = 0
        clearance_sum = 0.0

        for i in range(n - 1):
            dist = self._min_dist_to_obstacles(pts[i], pts[i + 1])
            if dist < ROBOT_RADIUS:
                collision_count += 1
                clearance_sum += COLLISION_PENALTY_WEIGHT
            elif dist < SAFE_DIST:
                clearance_sum += 1.0 / dist

        collision_rate = collision_count / max(n - 1, 1)
        clearance_norm = clearance_sum / max(n - 1, 1)

        ALPHA = 10.0
        collision_penalty = (math.exp(ALPHA * collision_rate) - 1.0) / (
            math.exp(ALPHA) - 1.0
        )

        return (
            0.1 * length_norm
            + 0.1 * angle_norm
            + 0.1 * clearance_norm
            + 0.7 * collision_penalty
        )

    def _init_spline_particle(self) -> np.ndarray:
        K = self.n_ctrl_points
        M = self.n_waypoints

        start_arr = np.array(self.start, dtype=float)
        goal_arr = np.array(self.goal, dtype=float)

        t = np.linspace(0, 1, K).reshape(-1, 1)
        ctrl = (1 - t) * start_arr + t * goal_arr

        d = goal_arr - start_arr
        dn = d / (np.linalg.norm(d) + 1e-9)
        perp = np.array([-dn[1], dn[0]])

        noise_perp = np.random.randn(K, 1) * self.jitter
        noise_along = np.random.randn(K, 1) * (0.25 * self.jitter)
        ctrl = ctrl + noise_perp * perp + noise_along * dn

        ctrl[:, 0] = np.clip(ctrl[:, 0], 0, self.width - 1)
        ctrl[:, 1] = np.clip(ctrl[:, 1], 0, self.height - 1)
        ctrl[0] = start_arr
        ctrl[-1] = goal_arr

        dense = self._catmull_rom_chain(ctrl, samples_per_seg=30)
        path = self._resample_by_arclength(dense, M)

        path[:, 0] = np.clip(path[:, 0], 0, self.width - 1)
        path[:, 1] = np.clip(path[:, 1], 0, self.height - 1)
        path = self._smooth_path(
            path, alpha=self.smooth_alpha, rounds=self.smooth_rounds
        )

        path[0] = start_arr
        path[-1] = goal_arr

        return path

    def _catmull_rom_chain(
        self, ctrl: np.ndarray, samples_per_seg: int = 30
    ) -> np.ndarray:
        p = np.vstack([2 * ctrl[0] - ctrl[1], ctrl, 2 * ctrl[-1] - ctrl[-2]])
        points = []

        for i in range(1, len(p) - 2):
            p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]

            for t in np.linspace(0, 1, samples_per_seg, endpoint=False):
                t2, t3 = t * t, t * t * t
                pt = 0.5 * (
                    2 * p1
                    + (-p0 + p2) * t
                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                    + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
                )
                points.append(pt)

        points.append(ctrl[-1])
        return np.array(points)

    def _resample_by_arclength(self, path: np.ndarray, n: int) -> np.ndarray:
        diffs = np.diff(path, axis=0)
        seg_lens = np.linalg.norm(diffs, axis=1)
        cum = np.concatenate([[0.0], np.cumsum(seg_lens)])
        total = cum[-1]

        if total < 1e-9:
            return np.tile(path[0], (n, 1))

        targets = np.linspace(0, total, n)
        resampled = np.zeros((n, 2))

        for i, s in enumerate(targets):
            idx = np.searchsorted(cum, s, side="right") - 1
            idx = min(idx, len(path) - 2)
            rem = s - cum[idx]
            seg = seg_lens[idx] if seg_lens[idx] > 1e-9 else 1e-9
            resampled[i] = path[idx] + (rem / seg) * diffs[idx]

        return resampled

    def _smooth_path(
        self, path: np.ndarray, alpha: float = 0.12, rounds: int = 1
    ) -> np.ndarray:
        p = path.copy()

        for _ in range(rounds):
            for i in range(1, len(p) - 1):
                mid = (p[i - 1] + p[i + 1]) / 2.0
                p[i] = p[i] + alpha * (mid - p[i])

            p[0] = path[0]
            p[-1] = path[-1]

        return p

    def _repair_continuous(self, path: np.ndarray) -> np.ndarray:
        path = path.copy()
        path[:, 0] = np.clip(path[:, 0], 0, self.width - 1)
        path[:, 1] = np.clip(path[:, 1], 0, self.height - 1)
        return path

    def _min_dist_to_obstacles(
        self, a: tuple[float, float], b: tuple[float, float]
    ) -> float:
        if len(self.obstacles) == 0:
            return float("inf")

        return Planner._min_distance_segment_to_obstacles(a, b, self.obstacles)
