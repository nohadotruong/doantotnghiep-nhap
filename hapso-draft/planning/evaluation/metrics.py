"""
Path evaluation metrics.

Calculate path quality metrics for comparison and validation.
"""

from typing import List, Tuple
import math

import planning.api as plan_api
from planning.utils.geometry import euclidean_distance, path_smoothness


def calculate_metrics(
    path: List[Tuple[float, float]], grid: plan_api.Grid, computation_time: float
) -> plan_api.Metrics:
    """
    Calculate all evaluation metrics for a path.

    Args:
        path: List of (x, y) waypoints
        grid: Grid environment
        computation_time: Time taken to compute path (seconds)

    Returns:
        Metrics dataclass with all metrics
    """
    if not path or len(path) < 2:
        return plan_api.Metrics(
            path_length=0,
            waypoint_count=len(path),
            total_rotation=0,
            computation_time=computation_time,
            path_valid=False,
            objective_value=float("inf"),
            turn_angles=[],
        )

    # Path length
    path_len = 0.0
    for i in range(len(path) - 1):
        path_len += euclidean_distance(path[i], path[i + 1])

    # Turn angles
    turn_angles: List[float] = []
    total_rotation = 0.0

    for i in range(1, len(path) - 1):
        # Vector from i-1 to i
        v1_x = path[i][0] - path[i - 1][0]
        v1_y = path[i][1] - path[i - 1][1]
        len1 = math.sqrt(v1_x * v1_x + v1_y * v1_y)

        # Vector from i to i+1
        v2_x = path[i + 1][0] - path[i][0]
        v2_y = path[i + 1][1] - path[i][1]
        len2 = math.sqrt(v2_x * v2_x + v2_y * v2_y)

        if len1 > 0 and len2 > 0:
            # Dot and cross product
            dot = v1_x * v2_x + v1_y * v2_y
            cross = v1_x * v2_y - v1_y * v2_x

            angle = abs(math.atan2(cross, dot))
            turn_angles.append(angle)
            total_rotation += angle

    # Path validity check
    path_valid = is_path_valid(path, grid)

    # Objective function: weighted combination of metrics
    objective = (
        path_len  # Distance cost
        + len(path) * 0.2  # Waypoint count cost
        + total_rotation  # Rotation cost
        + computation_time * 0.5  # Time cost
    )

    return plan_api.Metrics(
        path_length=path_len,
        waypoint_count=len(path),
        total_rotation=total_rotation,
        computation_time=computation_time,
        path_valid=path_valid,
        objective_value=objective,
        turn_angles=turn_angles,
    )


def is_path_valid(path: List[Tuple[float, float]], grid: plan_api.Grid) -> bool:
    """
    Check if path is collision-free.

    Args:
        path: List of waypoints
        grid: Grid environment

    Returns:
        True if path has no collisions, False otherwise
    """
    if not path:
        return False

    for point in path:
        x, y = int(point[0]), int(point[1])
        if not grid.is_in_bounds(x, y) or grid.is_obstacle(x, y):
            return False

    return True


__all__ = [
    "calculate_metrics",
    "is_path_valid",
]
