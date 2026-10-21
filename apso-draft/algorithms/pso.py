from algorithms.astar import Astar, AstarNoCornercutting
from typing import List, Optional, Set, Tuple
from utils.geometry import (
    calculate_path_length,
    calculate_path_metrics,
    calculate_path_smoothness,
    check_collision_line,
    check_collision_line_with_clearance,
    euclidean_distance,
)

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
            if check_collision_line(self.grid, path[i], path[i + 1]):
                collision_count += 1

        length = calculate_path_length(path)

        smoothness = calculate_path_smoothness(path)

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
            self.valid_nodes,
            key=lambda node: euclidean_distance((node[0], node[1]), (px, py)),
        )

        return (float(nearest[0]), float(nearest[1]))

    def _repair_path(
        self, path: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        if len(path) < 2:
            return path
        repaired = [path[0]]
        i = 0
        while i < len(path) - 1:
            a, b = path[i], path[i + 1]
            if check_collision_line(self.grid, a, b):
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
                if not check_collision_line(
                    self.grid, path[current_idx], path[next_idx]
                ):
                    farthest = next_idx
                else:
                    break

            smoothed.append(path[farthest])
            current_idx = farthest

        if smoothed[-1] != path[-1]:
            smoothed[-1] = path[-1]

        return smoothed

    def validate_path(self, path: List[Tuple[float, float]]) -> bool:
        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):
                return False
        return True

    def get_path_metrics(self, path: List[Tuple[float, float]]) -> dict:
        return calculate_path_metrics(self.grid, path)


class PSONew:
    """
    Standalone PSO-based path planner for continuous 2D space.

    Features:
    - Pure PSO optimization without A* dependency
    - Continuous waypoint coordinates
    - Multi-objective fitness: path length + smoothness + safety
    - Obstacle inflation for safety margin
    - Random initialization (no guideline paths)
    """

    def __init__(
        self,
        grid: List[List[int]],
        num_particles: int = 30,
        num_waypoints: int = 5,
        max_iterations: int = 100,
        inertia_weight: float = 0.7,
        cognitive_coeff: float = 1.5,
        social_coeff: float = 1.5,
        w_length: float = 1.0,
        w_smoothness: float = 0.5,
        w_safety: float = 2.0,
        safety_radius: int = 1,
        collision_penalty: float = 1000.0,
        patience: int = 20,
        fitness_threshold: float = None,
    ):
        """
        Initialize PSONew planner.

        Args:
            grid: 2D list (0=free, 1=obstacle)
            num_particles: Number of particles
            num_waypoints: Number of waypoints per path
            max_iterations: Maximum iterations
            inertia_weight: PSO inertia weight
            cognitive_coeff: Cognitive coefficient (c1)
            social_coeff: Social coefficient (c2)
            w_length: Weight for path length in fitness
            w_smoothness: Weight for smoothness in fitness
            w_safety: Weight for safety penalty in fitness
            safety_radius: Obstacle inflation radius (cells)
            collision_penalty: Large penalty for collisions
            patience: Early stopping patience
            fitness_threshold: Target fitness threshold
        """
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0

        self.num_particles = num_particles
        self.num_waypoints = num_waypoints
        self.max_iterations = max_iterations
        self.w = inertia_weight
        self.c1 = cognitive_coeff
        self.c2 = social_coeff

        self.w_length = w_length
        self.w_smoothness = w_smoothness
        self.w_safety = w_safety
        self.safety_radius = safety_radius
        self.collision_penalty = collision_penalty

        self.patience = patience
        self.fitness_threshold = fitness_threshold

        self.particles: List[dict] = []
        self.gbest_position: Optional[np.ndarray] = None
        self.gbest_fitness: float = float("inf")

        # Precompute inflated grid
        self._distance_field = None
        self._precompute_distance_field()

    def plan(
        self, start: Tuple[float, float], goal: Tuple[float, float]
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Find optimal path from start to goal using PSO.

        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)

        Returns:
            List of waypoints (x, y) or None if no valid path found
        """
        self.start = np.array(start, dtype=float)
        self.goal = np.array(goal, dtype=float)

        # Validate start and goal
        if not self._is_valid_position(self.start) or self._is_collision(self.start):
            return None
        if not self._is_valid_position(self.goal) or self._is_collision(self.goal):
            return None

        # Initialize particles randomly
        self._initialize_particles()

        # Evaluate initial population
        for particle in self.particles:
            fitness = self._fitness(particle)
            particle["pbest_fitness"] = fitness
            particle["pbest_position"] = particle["position"].copy()
            if fitness < self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = particle["position"].copy()

        # PSO iterations
        no_improvement_count = 0
        previous_best_fitness = self.gbest_fitness

        for iteration in range(self.max_iterations):
            # Update personal and global best
            self._update_pbest_gbest()

            # Update velocity and position
            self._update_particles()

            # Handle constraints
            self._handle_constraints()

            # Check for improvement
            if self.gbest_fitness < previous_best_fitness:
                no_improvement_count = 0
                previous_best_fitness = self.gbest_fitness
            else:
                no_improvement_count += 1

            # Early stopping
            if no_improvement_count >= self.patience:
                print(
                    f"Early stopping at iteration {iteration + 1}/{self.max_iterations}"
                )
                break

            if (
                self.fitness_threshold is not None
                and self.gbest_fitness <= self.fitness_threshold
            ):
                print(
                    f"Fitness threshold reached at iteration {iteration + 1}/{self.max_iterations}"
                )
                break

        if self.gbest_position is None:
            return None

        # Construct final path
        path = self._construct_path(self.gbest_position)
        return path

    def _precompute_distance_field(self) -> None:
        """Compute distance transform for obstacle safety checking."""
        # Simple distance field: distance from each cell to nearest obstacle
        self._distance_field = np.zeros((self.height, self.width), dtype=float)

        # Find all free cells
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0:  # Free cell
                    # Find minimum distance to any obstacle
                    min_dist = float("inf")
                    for dy in range(max(0, y - 10), min(self.height, y + 11)):
                        for dx in range(max(0, x - 10), min(self.width, x + 11)):
                            if self.grid[dy][dx] == 1:  # Obstacle
                                dist = ((dx - x) ** 2 + (dy - y) ** 2) ** 0.5
                                min_dist = min(min_dist, dist)
                    self._distance_field[y][x] = (
                        min_dist if min_dist != float("inf") else 10.0
                    )
                else:
                    self._distance_field[y][x] = 0.0

    def _get_distance_to_obstacle(self, pos: Tuple[float, float]) -> float:
        """Get distance from position to nearest obstacle."""
        x, y = pos
        if not self._is_valid_position(pos):
            return -1.0

        xi = int(round(x))
        yi = int(round(y))

        if not self._is_valid_position((xi, yi)):
            return -1.0

        if self.grid[yi][xi] == 1:
            return 0.0

        return float(self._distance_field[yi][xi])

    def _initialize_particles(self) -> None:
        """Initialize particles with random waypoints in free space."""
        self.particles = []

        for _ in range(self.num_particles):
            # Generate random waypoints in free space
            waypoints = []
            for _ in range(self.num_waypoints):
                # Random position in grid bounds
                valid_pos = False
                while not valid_pos:
                    x = np.random.uniform(0, self.width - 1)
                    y = np.random.uniform(0, self.height - 1)
                    if not self._is_collision((x, y)):
                        waypoints.append([x, y])
                        valid_pos = True

            position = np.array(waypoints, dtype=float)
            velocity = np.random.uniform(-1, 1, size=position.shape)

            particle = {
                "position": position,
                "velocity": velocity,
                "pbest_position": position.copy(),
                "pbest_fitness": float("inf"),
            }
            self.particles.append(particle)

    def _fitness(self, particle: dict) -> float:
        """
        Compute multi-objective fitness.

        F = w_length * path_length + w_smoothness * smoothness + w_safety * safety_penalty
        """
        waypoints = particle["position"]

        # Construct full path: start -> waypoints -> goal
        path = self._construct_path(waypoints)

        # 1. Path length
        path_length = self._calculate_path_length(path)

        # 2. Smoothness (sum of turning angles)
        smoothness = self._calculate_smoothness(path)

        # 3. Collision penalty and safety
        collision_penalty = 0.0
        safety_penalty = 0.0

        for i in range(len(path) - 1):
            # Check for collision
            if self._segment_collides(path[i], path[i + 1]):
                collision_penalty += self.collision_penalty

            # Safety penalty (distance to obstacles)
            mid_point = (
                (path[i][0] + path[i + 1][0]) / 2,
                (path[i][1] + path[i + 1][1]) / 2,
            )
            dist_to_obs = self._get_distance_to_obstacle(mid_point)
            if dist_to_obs < self.safety_radius:
                safety_penalty += (self.safety_radius - dist_to_obs) ** 2

        fitness = (
            self.w_length * path_length
            + self.w_smoothness * smoothness
            + self.w_safety * safety_penalty
            + collision_penalty
        )

        return fitness

    def _construct_path(self, waypoints: np.ndarray) -> List[Tuple[float, float]]:
        """Construct full path: start -> waypoints -> goal."""
        path = [tuple(self.start)]

        for waypoint in waypoints:
            path.append(tuple(waypoint))

        path.append(tuple(self.goal))

        return path

    def _calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        """Calculate total path length."""
        length = 0.0
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            length += (dx * dx + dy * dy) ** 0.5
        return length

    def _calculate_smoothness(self, path: List[Tuple[float, float]]) -> float:
        """Calculate smoothness as sum of turning angles."""
        if len(path) < 3:
            return 0.0

        smoothness = 0.0

        for i in range(1, len(path) - 1):
            p1 = np.array(path[i - 1], dtype=float)
            p2 = np.array(path[i], dtype=float)
            p3 = np.array(path[i + 1], dtype=float)

            v1 = p2 - p1
            v2 = p3 - p2

            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 > 1e-6 and norm2 > 1e-6:
                v1 /= norm1
                v2 /= norm2

                # Clamp dot product to [-1, 1]
                dot = np.clip(np.dot(v1, v2), -1, 1)
                angle = np.arccos(dot)
                smoothness += angle

        return smoothness

    def _segment_collides(
        self, p1: Tuple[float, float], p2: Tuple[float, float]
    ) -> bool:
        """Check if line segment collides with obstacles using Bresenham."""
        cells = self._bresenham_line(p1, p2)

        for x, y in cells:
            if self._is_collision((x, y)):
                return True

        return False

    def _bresenham_line(
        self, p1: Tuple[float, float], p2: Tuple[float, float]
    ) -> List[Tuple[int, int]]:
        """Generate cells along line using Bresenham algorithm."""
        x0 = int(round(p1[0]))
        y0 = int(round(p1[1]))
        x1 = int(round(p2[0]))
        y1 = int(round(p2[1]))

        cells = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        if dx > dy:
            err = dx / 2.0
            y = y0
            for x in range(x0, x1 + sx, sx):
                if self._is_valid_position((x, y)):
                    cells.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
        else:
            err = dy / 2.0
            x = x0
            for y in range(y0, y1 + sy, sy):
                if self._is_valid_position((x, y)):
                    cells.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy

        return cells

    def _update_pbest_gbest(self) -> None:
        """Update personal best and global best."""
        for particle in self.particles:
            fitness = self._fitness(particle)

            if fitness < particle["pbest_fitness"]:
                particle["pbest_fitness"] = fitness
                particle["pbest_position"] = particle["position"].copy()

            if fitness < self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = particle["position"].copy()

    def _update_particles(self) -> None:
        """Update particle velocities and positions using PSO."""
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

            particle["position"] = particle["position"] + particle["velocity"]

    def _handle_constraints(self) -> None:
        """Enforce constraints on positions and velocities."""
        for particle in self.particles:
            # Clamp to grid bounds
            particle["position"][:, 0] = np.clip(
                particle["position"][:, 0], 0, self.width - 1
            )
            particle["position"][:, 1] = np.clip(
                particle["position"][:, 1], 0, self.height - 1
            )

            # Move colliding waypoints to nearest free space
            for i in range(len(particle["position"])):
                pos = tuple(particle["position"][i])
                if self._is_collision(pos):
                    safe_pos = self._find_nearest_free_space(pos)
                    particle["position"][i] = np.array(safe_pos, dtype=float)

            # Limit velocity
            max_velocity = np.array([2.0, 2.0])
            particle["velocity"] = np.clip(
                particle["velocity"], -max_velocity, max_velocity
            )

    def _find_nearest_free_space(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Find nearest free space within search radius."""
        x, y = pos
        search_radius = 3

        for radius in range(1, search_radius + 1):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx = int(round(x)) + dx
                    ny = int(round(y)) + dy

                    if self._is_valid_position((nx, ny)) and not self._is_collision(
                        (nx, ny)
                    ):
                        return (float(nx), float(ny))

        # Fallback to position as is
        return pos

    def _is_valid_position(self, pos: Tuple[float, float]) -> bool:
        """Check if position is within grid bounds."""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def _is_collision(self, pos: Tuple[float, float]) -> bool:
        """Check if position collides with obstacle."""
        x, y = pos
        if not self._is_valid_position(pos):
            return True

        xi = int(round(x))
        yi = int(round(y))

        return self.grid[yi][xi] == 1


class PSPlannerNoCornercutting:
    """
    PSO-based path planner with clearance margin to prevent corner cutting.

    This version uses check_collision_line_with_clearance to ensure paths
    maintain a safe distance from obstacles.
    """

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
        clearance: float = 1.5,
    ):
        """
        Initialize PSO planner with corner cutting prevention.

        Args:
            grid: The grid map
            num_particles: Number of particles in PSO swarm
            num_waypoints: Number of intermediate waypoints
            max_iterations: Maximum iterations for PSO
            inertia_weight: PSO inertia weight
            cognitive_coeff: PSO cognitive coefficient
            social_coeff: PSO social coefficient
            collision_penalty: Penalty for collision
            smoothness_weight: Weight for smoothness in fitness
            patience: Early stopping patience
            fitness_threshold: Fitness threshold for early stopping
            clearance: Minimum safe distance from obstacles
        """
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
        self.clearance = clearance

        self.patience = patience
        self.fitness_threshold = fitness_threshold
        self.particles: List[dict] = []

        self.gbest_position: Optional[np.ndarray] = None
        self.gbest_fitness: float = float("inf")

        self.valid_nodes: Set[Tuple[int, int]] = set()

        self._generate_valid_nodes()

    def plan(self) -> Optional[List[Tuple[float, float]]]:
        """Plan path using PSO with clearance constraint."""
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
        """Generate all valid (non-obstacle) nodes."""
        self.valid_nodes = set()
        for x in range(self.width):
            for y in range(self.height):
                if not self.grid.is_obstacle(x, y):
                    self.valid_nodes.add((x, y))

    def _initialize_particles(self) -> None:
        """Initialize PSO particles around guide line."""
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
        """Evaluate particle fitness with clearance constraint."""
        waypoints = particle["position"]
        path = self._construct_full_path(waypoints)

        collision_count = 0
        clearance_violations = 0

        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):
                collision_count += 1
            if check_collision_line_with_clearance(
                self.grid, path[i], path[i + 1], self.clearance
            ):
                clearance_violations += 1

        length = calculate_path_length(path)
        smoothness = calculate_path_smoothness(path)

        fitness = (
            length
            + collision_count * self.collision_penalty
            + clearance_violations * (self.collision_penalty * 0.5)
            + self.smoothness_weight * smoothness
        )

        return fitness

    def _construct_full_path(self, waypoints: np.ndarray) -> List[Tuple[float, float]]:
        """Construct full path from start through waypoints to goal."""
        path = [self.start]
        for waypoint in waypoints:
            path.append(tuple(waypoint))
        path.append(self.goal)
        return path

    def _update_pbest_gbest(self) -> None:
        """Update personal best and global best positions."""
        for particle in self.particles:
            fitness = self._evaluate(particle)

            if fitness < particle["pbest_fitness"]:
                particle["pbest_fitness"] = fitness
                particle["pbest_position"] = particle["position"].copy()

            if fitness < self.gbest_fitness:
                self.gbest_fitness = fitness
                self.gbest_position = particle["position"].copy()

    def _update_particles(self) -> None:
        """Update particle velocities and positions."""
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
        """Handle position and velocity constraints."""
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
        """Find nearest valid (non-obstacle) node."""
        if not self.valid_nodes:
            return position

        px, py = position
        nearest = min(
            self.valid_nodes,
            key=lambda node: euclidean_distance((node[0], node[1]), (px, py)),
        )

        return (float(nearest[0]), float(nearest[1]))

    def _repair_path(
        self, path: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Repair path by inserting intermediate waypoints for colliding segments."""
        if len(path) < 2:
            return path

        repaired = [path[0]]
        i = 0

        while i < len(path) - 1:
            a, b = path[i], path[i + 1]
            if check_collision_line(self.grid, a, b):
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
        """Use A* to find local path between two points."""
        start_int = (int(round(start[0])), int(round(start[1])))
        goal_int = (int(round(goal[0])), int(round(goal[1])))

        if self.grid.is_obstacle(start_int[0], start_int[1]):
            return None
        if self.grid.is_obstacle(goal_int[0], goal_int[1]):
            return None

        # Use A* with clearance
        astar = AstarNoCornercutting(self.grid, self.clearance)
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
        """Smooth path by connecting non-colliding waypoints."""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_idx = 0

        while current_idx < len(path) - 1:
            farthest = current_idx + 1

            for next_idx in range(current_idx + 2, len(path)):
                if not check_collision_line_with_clearance(
                    self.grid, path[current_idx], path[next_idx], self.clearance
                ):
                    farthest = next_idx
                else:
                    break

            smoothed.append(path[farthest])
            current_idx = farthest

        if smoothed[-1] != path[-1]:
            smoothed[-1] = path[-1]

        return smoothed

    def validate_path(self, path: List[Tuple[float, float]]) -> bool:
        """Validate that path respects clearance constraint."""
        for i in range(len(path) - 1):
            if check_collision_line_with_clearance(
                self.grid, path[i], path[i + 1], self.clearance
            ):
                return False
        return True

    def get_path_metrics(self, path: List[Tuple[float, float]]) -> dict:
        """Get metrics for path."""
        return calculate_path_metrics(self.grid, path)
