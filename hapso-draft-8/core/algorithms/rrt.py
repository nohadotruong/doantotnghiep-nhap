from config.algo_config import (
    RRT_GOAL_SAMPLE_RATE,
    RRT_MAX_ITERATIONS,
    RRT_MAX_SAMPLE_ATTEMPTS,
    RRT_STEP_SIZE,
)
from core.algorithms.base_planner import BasePlanner
from map.grid_map import GridMap

import math
import random


class RRTNode:
    def __init__(
        self,
        x: int,
        y: int,
        parent: "RRTNode | None" = None,
        cost: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.parent = parent
        self.cost = cost


class RRT(BasePlanner):
    def __init__(
        self,
        grid_map: GridMap,
        max_iter: int = RRT_MAX_ITERATIONS,
        step_size: int = RRT_STEP_SIZE,
        goal_sample_rate: float = RRT_GOAL_SAMPLE_RATE,
        max_sample_attempts: int = RRT_MAX_SAMPLE_ATTEMPTS,
    ) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.max_sample_attempts = max_sample_attempts

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        if not self._validate_inputs():
            return None

        start_node = RRTNode(start[0], start[1])
        nodes = [start_node]

        for _ in range(self.max_iter):
            sample = self._sample_point()
            nearest = self._nearest_node(nodes, sample)
            new_point = self._steer(nearest, sample)
            if new_point is None:
                continue
            if self._segment_has_collision((nearest.x, nearest.y), new_point):
                continue

            new_cost = nearest.cost + self._euclidean_distance(
                (nearest.x, nearest.y), new_point
            )
            new_node = RRTNode(new_point[0], new_point[1], nearest, new_cost)
            nodes.append(new_node)

            if self._is_goal_reached(new_node):
                if not self._segment_has_collision((new_node.x, new_node.y), goal):
                    goal_cost = new_node.cost + self._euclidean_distance(
                        (new_node.x, new_node.y), goal
                    )
                    goal_node = RRTNode(goal[0], goal[1], new_node, goal_cost)
                    return self._reconstruct_path(goal_node)

        return None

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

    def _nearest_node(self, nodes: list[RRTNode], point: tuple[int, int]) -> RRTNode:
        return min(
            nodes,
            key=lambda n: self._euclidean_distance((n.x, n.y), point),
        )

    def _steer(
        self, from_node: RRTNode, to_point: tuple[int, int]
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

    def _is_goal_reached(self, node: RRTNode) -> bool:
        if self.goal is None:
            return False
        return self._euclidean_distance((node.x, node.y), self.goal) <= self.step_size

    def _reconstruct_path(self, node: RRTNode) -> list[tuple[int, int]]:
        path = []
        current = node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        path.reverse()
        return path
