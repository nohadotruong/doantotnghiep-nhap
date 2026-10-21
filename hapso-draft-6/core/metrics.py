from config.algo_config import OBSTACLE_RADIUS, ROBOT_RADIUS
from map.grid_map import GridMap

import math
import numpy as np


def calculate_path_length(path: list[tuple[int, int]]) -> float:
    if not path or len(path) < 2:
        return 0.0

    total_length = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        dx = x2 - x1
        dy = y2 - y1
        total_length += math.sqrt(dx * dx + dy * dy)

    return total_length


def calculate_waypoint_count(path: list[tuple[int, int]]) -> int:
    return len(path) if path else 0


def calculate_turning_angle(path: list[tuple[int, int]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    total_angle = 0.0

    for i in range(1, len(path) - 1):
        v1_x = path[i][0] - path[i - 1][0]
        v1_y = path[i][1] - path[i - 1][1]

        v2_x = path[i + 1][0] - path[i][0]
        v2_y = path[i + 1][1] - path[i][1]

        dot_product = v1_x * v2_x + v1_y * v2_y
        cross_product = v1_x * v2_y - v1_y * v2_x

        angle = math.atan2(cross_product, dot_product)

        total_angle += abs(angle)

    return total_angle


def calculate_minimum_clearance(
    path: list[tuple[int, int]], grid_map: GridMap
) -> float:
    if not path:
        return float("inf")

    obstacles = grid_map.get_obstacles_as_centers()
    if len(obstacles) == 0:
        return float("inf")

    min_clearance = float("inf")

    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]

        segment_clearance = _min_distance_segment_to_obstacles(a, b, obstacles)
        min_clearance = min(min_clearance, segment_clearance)

    actual_clearance = min_clearance - (ROBOT_RADIUS + OBSTACLE_RADIUS)

    return actual_clearance


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


def compute_all_metrics(
    path: list[tuple[int, int]],
    grid_map: GridMap,
    execution_time: float = 0.0,
) -> dict[str, float]:
    if not path:
        return {
            "path_length": 0.0,
            "waypoints": 0,
            "turning_angle": 0.0,
            "execution_time": execution_time,
            "min_clearance": 0.0,
        }

    return {
        "path_length": calculate_path_length(path),
        "waypoints": calculate_waypoint_count(path),
        "turning_angle": calculate_turning_angle(path),
        "execution_time": execution_time,
        "min_clearance": calculate_minimum_clearance(path, grid_map),
    }
