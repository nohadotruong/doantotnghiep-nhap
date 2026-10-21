"""
Module: Multi-point Path Planner
Purpose: Combine RRT* and PSO for multi-point path optimization
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from .rrt_star import RRTStar
from .pso import TSPSolver
from ..environment import Environment


@dataclass
class PathSegment:
    """Represents a path segment between two waypoints"""

    path: List[np.ndarray]
    cost: float
    start: np.ndarray
    end: np.ndarray


class MultiPointPlanner:
    """Plan optimal multi-point path in obstacle environment"""

    def __init__(self, environment: Environment, cache_paths: bool = True):
        """
        Initialize multi-point planner

        Args:
            environment: Planning environment
            cache_paths: Cache computed paths between points
        """
        self.env = environment
        self.cache_paths = cache_paths
        self.path_cache: Dict[Tuple, PathSegment] = {}
        self.rrt_star = RRTStar(environment)

    def plan(
        self,
        start: np.ndarray,
        waypoints: List[np.ndarray],
        goal: np.ndarray,
        optimizer: str = "pso",
        rrt_iterations: int = 5000,
    ) -> Tuple[List[np.ndarray], float, Dict]:
        """
        Plan multi-point path

        Args:
            start: Start position
            waypoints: List of waypoints to visit
            goal: Goal position
            optimizer: 'pso', 'greedy', '2opt', or 'combined'
            rrt_iterations: RRT* iterations per path segment

        Returns:
            Tuple: (complete_path, total_cost, info_dict)
        """
        # Include start and goal in points for ordering
        all_points = np.array([start] + waypoints + [goal])
        num_points = len(all_points)

        # Compute distance matrix using RRT* for realistic distances
        distance_matrix = self._compute_distance_matrix(all_points, rrt_iterations)

        # Find optimal order of waypoints
        if optimizer == "pso":
            best_order, order_cost = self._optimize_pso(all_points, distance_matrix)
        elif optimizer == "greedy":
            best_order, order_cost = self._optimize_greedy(all_points, distance_matrix)
        elif optimizer == "2opt":
            best_order, order_cost = self._optimize_2opt(all_points, distance_matrix)
        elif optimizer == "combined":
            best_order, order_cost = self._optimize_combined(
                all_points, distance_matrix
            )
        else:
            raise ValueError(f"Unknown optimizer: {optimizer}")

        # Construct complete path following best order
        complete_path = self._construct_path(all_points, best_order)

        # Calculate actual path cost
        actual_cost = self._calculate_path_cost(complete_path)

        # Prepare info
        info = {
            "best_order": best_order,
            "order_cost": order_cost,
            "actual_cost": actual_cost,
            "optimizer": optimizer,
            "path_segments": len(complete_path) - 1,
            "distance_matrix": distance_matrix,
        }

        return complete_path, actual_cost, info

    def _compute_distance_matrix(
        self, points: np.ndarray, rrt_iterations: int
    ) -> np.ndarray:
        """Compute realistic distance matrix using RRT*"""
        n = len(points)
        distance_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i + 1, n):
                # Check if direct path is collision-free
                if self.env.is_path_collision_free(points[i], points[j]):
                    dist = np.linalg.norm(points[j] - points[i])
                else:
                    # Use RRT* to find path
                    self.rrt_star.max_iter = rrt_iterations
                    path = self.rrt_star.plan(points[i], points[j])
                    if path is None:
                        # No path found, use large cost
                        dist = float("inf")
                    else:
                        dist = self.rrt_star.get_path_cost(path)

                distance_matrix[i, j] = dist
                distance_matrix[j, i] = dist

        return distance_matrix

    def _optimize_pso(
        self, points: np.ndarray, distance_matrix: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Optimize using PSO"""
        tsp_solver = TSPSolver(points, distance_matrix)
        return tsp_solver.solve_pso()

    def _optimize_greedy(
        self, points: np.ndarray, distance_matrix: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Optimize using greedy nearest neighbor"""
        tsp_solver = TSPSolver(points, distance_matrix)
        return tsp_solver.solve_greedy()

    def _optimize_2opt(
        self, points: np.ndarray, distance_matrix: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Optimize using 2-opt"""
        tsp_solver = TSPSolver(points, distance_matrix)
        return tsp_solver.solve_2opt()

    def _optimize_combined(
        self, points: np.ndarray, distance_matrix: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Optimize using PSO followed by 2-opt"""
        tsp_solver = TSPSolver(points, distance_matrix)

        # First PSO
        order_pso, cost_pso = tsp_solver.solve_pso()

        # Then 2-opt improvement
        order_2opt, cost_2opt = tsp_solver.solve_2opt(order_pso)

        return order_2opt, cost_2opt

    def _construct_path(
        self, all_points: np.ndarray, order: np.ndarray
    ) -> List[np.ndarray]:
        """Construct complete path following given order"""
        complete_path = []

        for i in range(len(order)):
            curr_idx = int(order[i])
            next_idx = int(order[(i + 1) % len(order)])

            curr_point = all_points[curr_idx]
            next_point = all_points[next_idx]

            # Check if direct path is collision-free
            if self.env.is_path_collision_free(curr_point, next_point):
                # Direct path
                if i == 0:
                    complete_path.append(curr_point.copy())
                complete_path.append(next_point.copy())
            else:
                # Use RRT* to find path
                segment_path = self.rrt_star.plan(curr_point, next_point)

                if segment_path is None:
                    # Fallback to straight line if RRT* fails
                    if i == 0:
                        complete_path.append(curr_point.copy())
                    complete_path.append(next_point.copy())
                else:
                    # Add segment path
                    if i == 0:
                        complete_path.extend(segment_path)
                    else:
                        complete_path.extend(
                            segment_path[1:]
                        )  # Skip duplicate start point

        # Remove last point if it's duplicate of first (closed path)
        if np.allclose(complete_path[0], complete_path[-1]):
            complete_path = complete_path[:-1]

        return complete_path

    def _calculate_path_cost(self, path: List[np.ndarray]) -> float:
        """Calculate total path cost"""
        cost = 0.0
        for i in range(len(path) - 1):
            cost += np.linalg.norm(path[i + 1] - path[i])
        return cost

    def clear_cache(self):
        """Clear path cache"""
        self.path_cache.clear()
