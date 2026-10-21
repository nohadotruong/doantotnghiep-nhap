from typing import List, Tuple
import math
import numpy as np


def path_length(path: List[Tuple[float, float]]) -> float:
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        dx = path[i + 1][0] - path[i][0]
        dy = path[i + 1][1] - path[i][1]
        total += math.hypot(dx, dy)

    return total


def node_count(path: List[Tuple[float, float]]) -> int:
    return len(path)


def total_rotation(path: List[Tuple[float, float]]) -> float:
    if len(path) < 3:
        return 0.0

    total_angle = 0.0

    for i in range(1, len(path) - 1):
        p_prev = path[i - 1]
        p_curr = path[i]
        p_next = path[i + 1]

        v1 = np.array(
            [
                p_curr[0] - p_prev[0],
                p_curr[1] - p_prev[1],
            ],
            dtype=np.float32,
        )
        v2 = np.array(
            [
                p_next[0] - p_curr[0],
                p_next[1] - p_curr[1],
            ],
            dtype=np.float32,
        )

        len_v1 = np.linalg.norm(v1)
        len_v2 = np.linalg.norm(v2)

        if len_v1 > 1e-9 and len_v2 > 1e-9:
            cos_angle = np.dot(v1, v2) / (len_v1 * len_v2)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = math.acos(cos_angle)
            total_angle += angle

    return total_angle


def compute_time(t_a: float) -> float:
    return t_a


def objective(
    path: List[Tuple[float, float]],
    t_a: float,
    v_m: float = 1.0,
    t_p: float = 0.2,
    v_i: float = math.pi,
) -> float:
    D = path_length(path)
    P = node_count(path)
    I = total_rotation(path)
    C = compute_time(t_a)

    return D / v_m + P * t_p + I / v_i + C
