"""
Module: PSO Algorithm
Purpose: Particle Swarm Optimization for multi-point path ordering
"""

import numpy as np
from typing import List, Callable, Tuple
import itertools


class PSO:
    """Particle Swarm Optimization for discrete optimization"""

    def __init__(
        self,
        num_particles: int = 30,
        max_iterations: int = 100,
        w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
    ):
        """
        Initialize PSO

        Args:
            num_particles: Number of particles in swarm
            max_iterations: Maximum iterations
            w: Inertia weight
            c1: Cognitive parameter
            c2: Social parameter
        """
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.particles: List[np.ndarray] = []
        self.velocities: List[np.ndarray] = []
        self.best_positions: List[np.ndarray] = []
        self.best_costs: List[float] = []
        self.global_best_position: np.ndarray = None
        self.global_best_cost: float = float("inf")

    def optimize(
        self, cost_function: Callable[[np.ndarray], float], num_points: int
    ) -> Tuple[np.ndarray, float]:
        """
        Optimize order of points using PSO

        Args:
            cost_function: Function to minimize (takes order as input)
            num_points: Number of points to order

        Returns:
            Best order and its cost
        """
        # Initialize particles (random permutations)
        self.particles = []
        self.velocities = []
        self.best_positions = []
        self.best_costs = []

        for i in range(self.num_particles):
            # Random permutation
            perm = np.random.permutation(num_points)
            self.particles.append(perm.copy())
            self.best_positions.append(perm.copy())

            cost = cost_function(perm)
            self.best_costs.append(cost)

            if cost < self.global_best_cost:
                self.global_best_cost = cost
                self.global_best_position = perm.copy()

            # Initialize velocity as random position
            self.velocities.append(np.random.permutation(num_points))

        # Ensure global_best_position is set (fallback to first particle if all costs are inf)
        if self.global_best_position is None:
            self.global_best_position = self.best_positions[0].copy()
            self.global_best_cost = self.best_costs[0]

        # Main optimization loop
        for iteration in range(self.max_iterations):
            for i in range(self.num_particles):
                # Update velocity and position
                new_position = self._update_particle(i, num_points)

                # Evaluate
                cost = cost_function(new_position)

                # Update personal best
                if cost < self.best_costs[i]:
                    self.best_costs[i] = cost
                    self.best_positions[i] = new_position.copy()

                    # Update global best
                    if cost < self.global_best_cost:
                        self.global_best_cost = cost
                        self.global_best_position = new_position.copy()

        return self.global_best_position, self.global_best_cost

    def _update_particle(self, idx: int, num_points: int) -> np.ndarray:
        """Update position of a particle"""
        # For discrete optimization, use order-based update
        current = self.particles[idx]
        best_personal = self.best_positions[idx]
        best_global = self.global_best_position

        # Create new position by mixing current, personal best, and global best
        new_position = current.copy()

        # Apply inertia
        if np.random.rand() < self.w:
            # Keep some of current position
            pass

        # Apply cognitive component (follow personal best)
        if np.random.rand() < self.c1 / 2.0:
            new_position = self._order_crossover(new_position, best_personal)

        # Apply social component (follow global best) - only if global best exists
        if best_global is not None and np.random.rand() < self.c2 / 2.0:
            new_position = self._order_crossover(new_position, best_global)

        # Add some mutation
        if np.random.rand() < 0.1:
            new_position = self._random_swap(new_position)

        self.particles[idx] = new_position
        return new_position

    @staticmethod
    def _order_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Order crossover between two permutations"""
        if parent2 is None:
            return parent1.copy()

        n = len(parent1)

        # Random segments
        start = np.random.randint(0, n)
        end = np.random.randint(start, n)

        # Create offspring
        child = np.full(n, -1, dtype=int)
        child[start:end] = parent1[start:end]

        # Fill remaining positions with parent2 order
        pointer = 0
        for i in range(n):
            if child[i] == -1:
                # Find next value from parent2 not in child
                while pointer < n and parent2[pointer] in child:
                    pointer += 1

                # If we found a valid position, use it
                if pointer < n:
                    child[i] = parent2[pointer]
                    pointer += 1
                else:
                    # Fallback: find any missing value
                    for val in range(n):
                        if val not in child:
                            child[i] = val
                            break

        return child

    @staticmethod
    def _random_swap(perm: np.ndarray) -> np.ndarray:
        """Apply random swap mutation"""
        child = perm.copy()
        i, j = np.random.choice(len(perm), 2, replace=False)
        child[i], child[j] = child[j], child[i]
        return child


class TSPSolver:
    """Solve Traveling Salesman Problem with PSO"""

    def __init__(self, points: np.ndarray, distance_matrix: np.ndarray = None):
        """
        Initialize TSP solver

        Args:
            points: Array of point coordinates
            distance_matrix: Pre-computed distance matrix (optional)
        """
        self.points = np.array(points)
        self.num_points = len(points)

        if distance_matrix is None:
            self._compute_distance_matrix()
        else:
            self.distance_matrix = distance_matrix

    def _compute_distance_matrix(self):
        """Compute pairwise distances"""
        n = self.num_points
        self.distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(self.points[i] - self.points[j])
                self.distance_matrix[i, j] = dist
                self.distance_matrix[j, i] = dist

    def cost_function(self, order: np.ndarray) -> float:
        """Calculate tour cost for given order"""
        cost = 0.0
        for i in range(len(order)):
            curr = order[i]
            next_idx = order[(i + 1) % len(order)]
            cost += self.distance_matrix[int(curr), int(next_idx)]
        return cost

    def solve_pso(
        self, num_particles: int = 30, max_iterations: int = 100
    ) -> Tuple[np.ndarray, float]:
        """Solve TSP using PSO"""
        pso = PSO(num_particles=num_particles, max_iterations=max_iterations)

        best_order, best_cost = pso.optimize(self.cost_function, self.num_points)

        return best_order, best_cost

    def solve_greedy(self, start_idx: int = 0) -> Tuple[np.ndarray, float]:
        """Solve TSP using greedy nearest neighbor"""
        unvisited = set(range(self.num_points))
        current = start_idx
        tour = [current]
        unvisited.remove(current)
        total_cost = 0.0

        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current, x])
            total_cost += self.distance_matrix[current, nearest]
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        # Close tour
        total_cost += self.distance_matrix[current, start_idx]

        return np.array(tour), total_cost

    def solve_2opt(
        self, initial_tour: np.ndarray = None, max_iterations: int = 1000
    ) -> Tuple[np.ndarray, float]:
        """Improve tour using 2-opt local search"""
        if initial_tour is None:
            tour, _ = self.solve_greedy()
        else:
            tour = initial_tour.copy()

        improved = True
        iterations = 0

        while improved and iterations < max_iterations:
            improved = False
            for i in range(1, self.num_points - 2):
                for j in range(i + 1, self.num_points):
                    # Calculate cost change
                    a, b = tour[i - 1], tour[i]
                    c, d = tour[j], tour[(j + 1) % self.num_points]

                    old_cost = (
                        self.distance_matrix[int(a), int(b)]
                        + self.distance_matrix[int(c), int(d)]
                    )
                    new_cost = (
                        self.distance_matrix[int(a), int(c)]
                        + self.distance_matrix[int(b), int(d)]
                    )

                    if new_cost < old_cost:
                        # Reverse segment
                        tour[i : j + 1] = tour[i : j + 1][::-1]
                        improved = True

            iterations += 1

        cost = self.cost_function(tour)
        return tour, cost
