from algorithms.astar import Astar
from typing import List, Optional, Set, Tuple
from utils.geometry import bresenham_line

import math
import numpy as np


class PSOPlanner:
    def __init__(
        self,
        grid,
        num_particles: int = 30,
        num_waypoints: int = 5,
        max_iterations: int = 100,
        inertia_weight: float = 0.7,
        cognitive_coeff: float = 1.5,
        social_coeff: float = 1.5,
        collision_penalty: float = 1000.0,
        smoothness_weight: float = 1.0,
        patience: int = 20,
        fitness_threshold: float = None,
    ):
        self.grid = grid
        self.start = grid.start
        self.goal = grid.goal
        self.width = grid.width
        self.height = grid.height

        self.num_particles = num_particles
        self.num_waypoints = num_waypoints
        self.max_iterations = max_iterations
        self.w = inertia_weight
        self.c1 = cognitive_coeff
        self.c2 = social_coeff

        self.collision_penalty = collision_penalty
        self.smoothness_weight = smoothness_weight

        self.patience = patience
        self.fitness_threshold = fitness_threshold
        self.particles: List[dict] = []

        self.gbest_position: Optional[np.ndarray] = None
        self.gbest_fitness: float = float("inf")

        self.valid_nodes: Set[Tuple[int, int]] = set()

        self._generate_valid_nodes()

    def plan(self) -> Optional[List[Tuple[float, float]]]:
        """
        Execute PSO-based path planning.
        Uses start and goal from self.grid.
        """
        self.start = self.grid.start
        self.goal = self.grid.goal
        self._initialize_particles()

        for particle in self.particles:
            fitness = self._evaluate(particle)
            particle["pbest_fitness"] = fitness
            particle["pbest_position"] = particle["position"].copy()
            if fitness < self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = particle["position"].copy()

        no_improvement_count = 0
        previous_best_fitness = self.gbest_fitness

        for iteration in range(self.max_iterations):
            self._update_pbest_gbest()

            self._update_particles()

            self._handle_constraints()

            if self.gbest_fitness < previous_best_fitness:
                no_improvement_count = 0
                previous_best_fitness = self.gbest_fitness
            else:
                no_improvement_count += 1

            if no_improvement_count >= self.patience:
                print(
                    f"Early stopping: no improvement for {self.patience} iterations (iteration {iteration + 1}/{self.max_iterations})"
                )
                break

            if (
                self.fitness_threshold is not None
                and self.gbest_fitness <= self.fitness_threshold
            ):
                print(
                    f"Early stopping: fitness threshold reached ({self.gbest_fitness:.4f} <= {self.fitness_threshold:.4f}) at iteration {iteration + 1}/{self.max_iterations}"
                )
                break

        if self.gbest_position is None:
            return None

        best_path = self._construct_full_path(self.gbest_position)
        repaired_path = self._repair_path(best_path)
        smoothed_path = self._smooth_path(repaired_path)

        return smoothed_path

    def _generate_valid_nodes(self) -> None:
        self.valid_nodes = set()

        for x in range(self.width):
            for y in range(self.height):
                if not self.grid.is_obstacle(x, y):
                    self.valid_nodes.add((x, y))

    def _initialize_particles(self) -> None:
        self.particles = []

        guide_line = np.linspace(self.start, self.goal, self.num_waypoints + 2)[1:-1]
        guide_line = np.round(guide_line).astype(int)

        for _ in range(self.num_particles):
            position = guide_line.copy().astype(float)
            position = position + np.random.randint(-2, 3, size=position.shape)
            position[:, 0] = np.clip(position[:, 0], 0, self.width - 1)
            position[:, 1] = np.clip(position[:, 1], 0, self.height - 1)
            position = np.round(position).astype(int)
            velocity = np.random.randint(-2, 3, size=position.shape)

            particle = {
                "position": position,
                "velocity": velocity,
                "pbest_position": position.copy(),
                "pbest_fitness": float("inf"),
            }

            self.particles.append(particle)

    def _evaluate(self, particle: dict) -> float:
        waypoints = particle["position"]

        path = self._construct_full_path(waypoints)

        collision_count = 0
        for i in range(len(path) - 1):
            if self._check_collision_line(path[i], path[i + 1]):
                collision_count += 1

        length = self._path_length(path)

        smoothness = self._calculate_smoothness_penalty(waypoints)

        fitness = (
            length
            + collision_count * self.collision_penalty
            + self.smoothness_weight * smoothness
        )

        return fitness

    def _construct_full_path(self, waypoints: np.ndarray) -> List[Tuple[float, float]]:
        path = [self.start]

        for waypoint in waypoints:
            path.append(tuple(waypoint))

        path.append(self.goal)

        return path

    def _check_collision_line(
        self, p1: Tuple[float, float], p2: Tuple[float, float]
    ) -> bool:
        cells = bresenham_line(p1, p2)

        for x, y in cells:
            if self.grid.is_obstacle(x, y):
                return True

        return False

    def _path_length(self, path: List[Tuple[float, float]]) -> float:
        length = 0.0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            length += math.sqrt((x2 - x1) ** 2 + (x2 - x1) ** 2)

        return length

    def _calculate_smoothness_penalty(self, waypoints: np.ndarray) -> float:
        if len(waypoints) < 2:
            return 0.0

        penalty = 0.0

        full_path = self._construct_full_path(waypoints)

        for i in range(1, len(full_path) - 1):
            p1 = np.array(full_path[i - 1], dtype=float)
            p2 = np.array(full_path[i], dtype=float)
            p3 = np.array(full_path[i + 1], dtype=float)

            v1 = p1 - p2
            v2 = p3 - p2

            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 > 1e-6 and norm2 > 1e-6:
                v1 /= norm1
                v2 /= norm2

                dot_product = np.clip(np.dot(v1, v2), -1, 1)
                angle = math.acos(dot_product)
                penalty += angle

        return penalty

    def _update_pbest_gbest(self) -> None:
        for particle in self.particles:
            fitness = self._evaluate(particle)

            if fitness < particle["pbest_fitness"]:
                particle["pbest_fitness"] = fitness
                particle["pbest_position"] = particle["position"].copy()

            if fitness < self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = particle["position"].copy()

    def _update_particles(self) -> None:
        for particle in self.particles:
            r1 = np.random.rand(*particle["position"].shape)
            r2 = np.random.rand(*particle["position"].shape)

            cognitive = (
                self.c1
                * r1
                * (
                    particle["pbest_position"].astype(float)
                    - particle["position"].astype(float)
                )
            )
            social = (
                self.c2
                * r2
                * (
                    self.gbest_position.astype(float)
                    - particle["position"].astype(float)
                )
            )
            particle["velocity"] = self.w * particle["velocity"] + cognitive + social
            particle["velocity"] = np.round(particle["velocity"]).astype(int)
            particle["position"] = particle["position"] + particle["velocity"]

    def _handle_constraints(self) -> None:
        for particle in self.particles:
            particle["position"][:, 0] = np.clip(
                particle["position"][:, 0], 0, self.width - 1
            )
            particle["position"][:, 1] = np.clip(
                particle["position"][:, 1], 0, self.height - 1
            )
            particle["position"] = particle["position"].astype(int)
            for i in range(len(particle["position"])):
                x, y = int(particle["position"][i, 0]), int(particle["position"][i, 1])
                if self.grid.is_obstacle(x, y):
                    safe_pos = self._find_nearest_valid_node((float(x), float(y)))
                    particle["position"][i] = np.array(safe_pos, dtype=int)
            max_velocity = np.array([3, 3])
            particle["velocity"] = np.clip(
                particle["velocity"],
                -max_velocity,
                max_velocity,
            )
            particle["velocity"] = particle["velocity"].astype(int)

    def _find_nearest_valid_node(
        self, position: Tuple[float, float]
    ) -> Tuple[float, float]:
        if not self.valid_nodes:
            return position

        px, py = position
        nearest = min(
            self.valid_nodes, key=lambda node: (node[0] - px) ** 2 + (node[1] - py) ** 2
        )

        return (float(nearest[0]), float(nearest[1]))

    def _repair_path(
        self, path: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Repair path by fixing collision segments using local A*."""
        if len(path) < 2:
            return path
        repaired = [path[0]]
        i = 0
        while i < len(path) - 1:
            a, b = path[i], path[i + 1]
            if self._check_collision_line(a, b):
                local_path = self._local_astar(a, b)
                if local_path and len(local_path) > 0:
                    local_path_float = [(float(x), float(y)) for x, y in local_path]
                    repaired.extend(local_path_float[1:])
                else:
                    repaired.append(b)
            else:
                repaired.append(b)
            i += 1
        return repaired

    def _local_astar(
        self, start: Tuple[float, float], goal: Tuple[float, float]
    ) -> Optional[List[Tuple[float, float]]]:
        """Local A* pathfinding between start and goal."""
        start_int = (int(round(start[0])), int(round(start[1])))
        goal_int = (int(round(goal[0])), int(round(goal[1])))
        if self.grid.is_obstacle(start_int[0], start_int[1]):
            return None
        if self.grid.is_obstacle(goal_int[0], goal_int[1]):
            return None
        astar = Astar(self.grid)
        original_start = self.grid.start
        original_goal = self.grid.goal
        self.grid.start = start_int
        self.grid.goal = goal_int
        try:
            path = astar.plan()
            return path
        finally:
            self.grid.start = original_start
            self.grid.goal = original_goal

    def _smooth_path(
        self, path: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_idx = 0

        while current_idx < len(path) - 1:
            farthest = current_idx + 1

            for next_idx in range(current_idx + 2, len(path)):
                if not self._check_collision_line(path[current_idx], path[next_idx]):
                    farthest = next_idx
                else:
                    break

            smoothed.append(path[farthest])
            current_idx = farthest

        if smoothed[-1] != path[-1]:
            smoothed[-1] = path[-1]

        return smoothed
