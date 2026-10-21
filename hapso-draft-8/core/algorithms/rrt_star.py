from config.algo_config import (
    RRT_GOAL_SAMPLE_RATE,
    RRT_MAX_SAMPLE_ATTEMPTS,
    RRT_STAR_MAX_ITERATIONS,
    RRT_STAR_NEIGHBOR_RADIUS,
    RRT_STEP_SIZE,
)
from core.algorithms.base_planner import BasePlanner
from map.grid_map import GridMap

import math
import random


class RRTStarNode:
    def __init__(
        self,
        x: int,
        y: int,
        parent: "RRTStarNode | None" = None,
        cost: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.parent = parent
        self.cost = cost


class RRTStar(BasePlanner):
    def __init__(
        self,
        grid_map: GridMap,
        max_iter: int = RRT_STAR_MAX_ITERATIONS,
        step_size: int = RRT_STEP_SIZE,
        goal_sample_rate: float = RRT_GOAL_SAMPLE_RATE,
        max_sample_attempts: int = RRT_MAX_SAMPLE_ATTEMPTS,
        neighbor_radius: float = RRT_STAR_NEIGHBOR_RADIUS,
    ) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.max_sample_attempts = max_sample_attempts
        self.neighbor_radius = neighbor_radius

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        if not self._validate_inputs():
            return None

        start_node = RRTStarNode(start[0], start[1])
        nodes = [start_node]
        best_goal_node: RRTStarNode | None = None

        for _ in range(self.max_iter):
            sample = self._sample_point()
            nearest = self._nearest_node(nodes, sample)
            new_point = self._steer(nearest, sample)
            if new_point is None:
                continue

            neighbors = self._near_nodes(nodes, new_point)
            parent = self._choose_parent(neighbors, nearest, new_point)
            if parent is None:
                continue

            if self._segment_has_collision((parent.x, parent.y), new_point):
                continue

            new_cost = parent.cost + self._euclidean_distance(
                (parent.x, parent.y), new_point
            )
            new_node = RRTStarNode(new_point[0], new_point[1], parent, new_cost)
            nodes.append(new_node)

            self._rewire(neighbors, new_node, nodes)

            if self._is_goal_reached(new_node):
                goal_cost = new_node.cost + self._euclidean_distance(
                    (new_node.x, new_node.y), goal
                )
                if best_goal_node is None or goal_cost < best_goal_node.cost:
                    if not self._segment_has_collision((new_node.x, new_node.y), goal):
                        best_goal_node = RRTStarNode(
                            goal[0], goal[1], new_node, goal_cost
                        )

        if best_goal_node is None:
            return None

        return self._reconstruct_path(best_goal_node)

    def _sample_point(self) -> tuple[int, int]:
        if self.goal is None:
            return (0, 0)

        if random.random() < self.goal_sample_rate:
            return self.goal

        for _ in range(self.max_sample_attempts):
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)
            if self._is_valid(x, y):
                return (x, y)

        return self.goal

    def _nearest_node(
        self, nodes: list[RRTStarNode], point: tuple[int, int]
    ) -> RRTStarNode:
        return min(
            nodes,
            key=lambda n: self._euclidean_distance((n.x, n.y), point),
        )

    def _steer(
        self, from_node: RRTStarNode, to_point: tuple[int, int]
    ) -> tuple[int, int] | None:
        dx = to_point[0] - from_node.x
        dy = to_point[1] - from_node.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 1e-9:
            return None

        if distance <= self.step_size:
            new_x, new_y = to_point
        else:
            ratio = self.step_size / distance
            new_x = int(round(from_node.x + dx * ratio))
            new_y = int(round(from_node.y + dy * ratio))

        if not self._is_valid(new_x, new_y):
            return None
        if new_x == from_node.x and new_y == from_node.y:
            return None
        return (new_x, new_y)

    def _near_nodes(
        self, nodes: list[RRTStarNode], point: tuple[int, int]
    ) -> list[RRTStarNode]:
        node_count = len(nodes)
        if node_count <= 1:
            radius = self.neighbor_radius
        else:
            adaptive_radius = 10.0 * math.sqrt(
                math.log(node_count + 1) / (node_count + 1)
            )
            radius = min(adaptive_radius, self.step_size * 3)
        near_nodes = []
        for node in nodes:
            if self._euclidean_distance((node.x, node.y), point) <= radius:
                near_nodes.append(node)
        return near_nodes

    def _choose_parent(
        self,
        neighbors: list[RRTStarNode],
        nearest: RRTStarNode,
        point: tuple[int, int],
    ) -> RRTStarNode | None:
        candidates = neighbors if neighbors else [nearest]
        best_node = None
        best_cost = float("inf")
        for node in candidates:
            if self._segment_has_collision((node.x, node.y), point):
                continue
            cost = node.cost + self._euclidean_distance((node.x, node.y), point)
            if cost < best_cost:
                best_cost = cost
                best_node = node
        return best_node

    def _rewire(
        self,
        neighbors: list[RRTStarNode],
        new_node: RRTStarNode,
        nodes: list[RRTStarNode],
    ) -> None:
        for node in neighbors:
            if node is new_node.parent:
                continue
            if self._segment_has_collision((new_node.x, new_node.y), (node.x, node.y)):
                continue

            new_cost = new_node.cost + self._euclidean_distance(
                (new_node.x, new_node.y), (node.x, node.y)
            )
            if new_cost < node.cost:
                node.parent = new_node
                node.cost = new_cost
                self._propagate_cost(node, nodes)

    def _propagate_cost(self, node: RRTStarNode, nodes: list[RRTStarNode]) -> None:
        for child in nodes:
            if child.parent is node:
                child.cost = node.cost + self._euclidean_distance(
                    (node.x, node.y), (child.x, child.y)
                )
                self._propagate_cost(child, nodes)

    def _is_goal_reached(self, node: RRTStarNode) -> bool:
        if self.goal is None:
            return False
        return self._euclidean_distance((node.x, node.y), self.goal) <= self.step_size

    def _reconstruct_path(self, node: RRTStarNode) -> list[tuple[int, int]]:
        path = []
        current = node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        path.reverse()
        return path
