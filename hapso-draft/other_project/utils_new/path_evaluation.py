from environment.grid_map import GridMap
from typing import List, Tuple
import math


def path_length(path: List[Tuple[float, float]]) -> float:
    if len(path) < 2:
        return 0.0

    total_length = 0.0
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        total_length += math.sqrt(dx * dx + dy * dy)

    return total_length


def path_smoothness(path: List[Tuple[float, float]]) -> float:
    if len(path) < 3:
        return 0.0

    total_angle_change = 0.0

    for i in range(1, len(path) - 1):
        p_prev = path[i - 1]
        p_curr = path[i]
        p_next = path[i + 1]

        v1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
        v2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])

        len_v1 = math.sqrt(v1[0] * v1[0] + v1[1] * v1[1])
        len_v2 = math.sqrt(v2[0] * v2[0] + v2[1] * v2[1])

        if len_v1 > 0 and len_v2 > 0:
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            cos_angle = dot_product / (len_v1 * len_v2)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle_change = math.acos(cos_angle)
            total_angle_change += angle_change

    return total_angle_change


def is_path_valid(
    path: List[Tuple[float, float]],
    grid: GridMap,
) -> bool:
    from utils_new.geometry_utils import has_line_of_sight

    if len(path) < 2:
        return True

    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]

        if not has_line_of_sight(grid, p1, p2):
            return False

    return True
