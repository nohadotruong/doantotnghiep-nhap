from abc import ABC, abstractmethod
from config.algo_config import OBSTACLE_RADIUS, ROBOT_RADIUS

import math
import numpy as np


class BasePlanner(ABC):
    distance_method: str = "vector_projection"

    @classmethod
    def set_distance_method(cls, method: str) -> None:
        if method in ["vector_projection", "algebraic"]:
            cls.distance_method = method
            print(f"[BASE_PLANNER]: Distance calculation method changed to {method}")
        else:
            print(
                f"[BASE_PLANNER]: Invalid method '{method}'. Use 'vector_projection' or 'algebraic'"
            )

    @abstractmethod
    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        pass

    def _validate_inputs(self) -> bool:
        if self.start is None or self.goal is None:
            print("[BASE_PLANNER]: Start and goal are required")
            return False

        start_x, start_y = self.start
        goal_x, goal_y = self.goal

        if not self._is_valid(start_x, start_y):
            print(
                f"[BASE_PLANNER]: Start {self.start} is invalid (out of bounds or obstacle)"
            )
            return False
        if not self._is_valid(goal_x, goal_y):
            print(
                f"[BASE_PLANNER]: Goal {self.goal} is invalid (out of bounds or obstacle)"
            )
            return False
        return True

    def _is_valid(self, x: int, y: int) -> bool:
        return self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y)

    def _euclidean_distance(self, p1: tuple[int, int], p2: tuple[int, int]) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return (dx * dx + dy * dy) ** 0.5

    def _segment_has_collision(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        points = BasePlanner._fast_voxel_traversal(a[0], a[1], b[0], b[1])

        for cx, cy in points:
            if not self.grid_map.is_inside(cx, cy) or self.grid_map.is_obstacle(cx, cy):
                return True

        min_distance = BasePlanner._min_distance_segment_to_obstacles(
            a, b, self.obstacles
        )

        return min_distance < (OBSTACLE_RADIUS + ROBOT_RADIUS)

    @staticmethod
    def _fast_voxel_traversal(
        x0: int, y0: int, x1: int, y1: int
    ) -> list[tuple[int, int]]:
        points = []

        dx = x1 - x0
        dy = y1 - y0

        step_x = 1 if dx > 0 else -1 if dx < 0 else 0
        step_y = 1 if dy > 0 else -1 if dy < 0 else 0

        current_x = x0
        current_y = y0

        if dx == 0 and dy == 0:
            return [(x0, y0)]

        if dx == 0:
            t_max_x = float("inf")
            t_delta_x = float("inf")
        else:
            t_delta_x = 1.0 / abs(dx)
            t_max_x = 0.5 * t_delta_x

        if dy == 0:
            t_max_y = float("inf")
            t_delta_y = float("inf")
        else:
            t_delta_y = 1.0 / abs(dy)
            t_max_y = 0.5 * t_delta_y

        points.append((current_x, current_y))

        while current_x != x1 or current_y != y1:
            if t_max_x < t_max_y:
                current_x += step_x
                t_max_x += t_delta_x
            elif t_max_y < t_max_x:
                current_y += step_y
                t_max_y += t_delta_y
            else:
                current_x += step_x
                current_y += step_y
                t_max_x += t_delta_x
                t_max_y += t_delta_y

            points.append((current_x, current_y))

        return points

    @staticmethod
    def _bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points

    @staticmethod
    def _min_distance_segment_to_obstacles(
        a: tuple[int, int], b: tuple[int, int], obstacles: np.ndarray
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
