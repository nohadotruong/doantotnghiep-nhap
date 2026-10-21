"""
Module: RRT* Algorithm
Purpose: Rapidly-exploring Random Tree with asymptotic optimality
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from ..environment import Environment


@dataclass
class Node:
    """Node in RRT tree"""

    position: np.ndarray
    parent: Optional["Node"] = None
    cost: float = 0.0  # Cost from start node

    def __hash__(self):
        return id(self)


class RRTStar:
    """RRT* path planning algorithm"""

    def __init__(
        self,
        environment: Environment,
        max_iter: int = 5000,
        step_size: float = 0.5,
        goal_radius: float = 0.3,
        search_radius: float = 2.0,
        clearance: float = 0.1,
    ):
        """
        Initialize RRT*

        Args:
            environment: Planning environment
            max_iter: Maximum iterations
            step_size: Distance for each step
            goal_radius: Success threshold to goal
            search_radius: Radius for rewiring neighbors (should be large)
            clearance: Minimum clearance from obstacles
        """
        self.env = environment
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_radius = goal_radius
        self.search_radius = search_radius
        self.clearance = clearance
        self.nodes: List[Node] = []
        self.goal_node: Optional[Node] = None

    def plan(self, start: np.ndarray, goal: np.ndarray) -> Optional[List[np.ndarray]]:
        """
        Plan path from start to goal

        Args:
            start: Start position
            goal: Goal position

        Returns:
            Path as list of positions, or None if no path found
        """
        # Initialize
        self.nodes = []
        start_node = Node(position=np.array(start, dtype=float), cost=0.0)
        self.nodes.append(start_node)
        self.goal_node = None

        goal = np.array(goal, dtype=float)

        # Main loop
        for iteration in range(self.max_iter):
            # Sample random point
            if np.random.rand() < 0.1:  # 10% goal biasing
                random_point = goal.copy()
            else:
                random_point = np.array(
                    [
                        np.random.uniform(self.env.x_min, self.env.x_max),
                        np.random.uniform(self.env.y_min, self.env.y_max),
                    ]
                )

            # Find nearest node
            nearest_node = self._nearest_node(random_point)
            if nearest_node is None:
                continue

            # Steer towards random point
            new_position = self._steer(nearest_node.position, random_point)

            # Check collision
            if not self.env.is_path_collision_free(
                nearest_node.position, new_position, self.clearance
            ):
                continue

            # Create new node with cost
            new_cost = nearest_node.cost + np.linalg.norm(
                new_position - nearest_node.position
            )
            new_node = Node(position=new_position, parent=nearest_node, cost=new_cost)

            # Find neighbors for rewiring
            neighbors = self._find_neighbors(new_node)

            # Find best parent
            best_parent = nearest_node
            best_cost = new_cost

            for neighbor in neighbors:
                if self.env.is_path_collision_free(
                    neighbor.position, new_position, self.clearance
                ):
                    neighbor_cost = neighbor.cost + np.linalg.norm(
                        new_position - neighbor.position
                    )
                    if neighbor_cost < best_cost:
                        best_cost = neighbor_cost
                        best_parent = neighbor

            new_node.parent = best_parent
            new_node.cost = best_cost
            self.nodes.append(new_node)

            # Rewire neighbors
            for neighbor in neighbors:
                if self.env.is_path_collision_free(
                    new_node.position, neighbor.position, self.clearance
                ):
                    new_neighbor_cost = new_node.cost + np.linalg.norm(
                        neighbor.position - new_node.position
                    )
                    if new_neighbor_cost < neighbor.cost:
                        neighbor.parent = new_node
                        neighbor.cost = new_neighbor_cost

            # Check if goal reached
            if np.linalg.norm(new_position - goal) < self.goal_radius:
                goal_node = Node(
                    position=goal.copy(),
                    parent=new_node,
                    cost=new_cost + np.linalg.norm(goal - new_position),
                )
                self.nodes.append(goal_node)
                self.goal_node = goal_node

        # Extract path
        if self.goal_node is None:
            return None

        path = []
        node = self.goal_node
        while node is not None:
            path.append(node.position.copy())
            node = node.parent

        path.reverse()
        return path

    def _nearest_node(self, point: np.ndarray) -> Optional[Node]:
        """Find nearest node to point"""
        if not self.nodes:
            return None

        min_dist = float("inf")
        nearest = None

        for node in self.nodes:
            dist = np.linalg.norm(node.position - point)
            if dist < min_dist:
                min_dist = dist
                nearest = node

        return nearest

    def _steer(self, from_pos: np.ndarray, to_pos: np.ndarray) -> np.ndarray:
        """Steer from one position towards another"""
        direction = to_pos - from_pos
        dist = np.linalg.norm(direction)

        if dist == 0:
            return from_pos.copy()

        # Move step_size in direction, or to goal if closer
        if dist < self.step_size:
            return to_pos.copy()
        else:
            return from_pos + (direction / dist) * self.step_size

    def _find_neighbors(self, node: Node) -> List[Node]:
        """Find neighbors within search radius"""
        neighbors = []
        for other in self.nodes:
            dist = np.linalg.norm(node.position - other.position)
            if 0 < dist < self.search_radius:
                neighbors.append(other)
        return neighbors

    def get_path_cost(self, path: List[np.ndarray]) -> float:
        """Calculate total path cost"""
        cost = 0.0
        for i in range(len(path) - 1):
            cost += np.linalg.norm(path[i + 1] - path[i])
        return cost
