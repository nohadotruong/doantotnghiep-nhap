from environment.grid_map import GridMap
from typing import List, Tuple


def remove_redundant_points(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if len(path) <= 2:
        return path

    filtered_path = [path[0]]

    for i in range(1, len(path) - 1):
        p_prev = path[i - 1]
        p_curr = path[i]
        p_next = path[i + 1]

        cross_product = (p_curr[0] - p_prev[0]) * (p_next[1] - p_prev[1]) - (
            p_curr[1] - p_prev[1]
        ) * (p_next[0] - p_prev[0])

        if cross_product != 0:
            filtered_path.append(p_curr)

    filtered_path.append(path[-1])

    return filtered_path


def remove_redundant_waypoints(
    path: List[Tuple[int, int]],
    grid: GridMap,
) -> List[Tuple[int, int]]:
    from utils_new.geometry_utils import has_line_of_sight

    if len(path) <= 2:
        return path

    filtered_path = [path[0]]

    i = 0
    while i < len(path) - 1:
        j = len(path) - 1

        while j > i + 1:
            p1 = (float(path[i][0]), float(path[i][1]))
            p2 = (float(path[j][0]), float(path[j][1]))

            if has_line_of_sight(grid, p1, p2):
                break

            j -= 1

        filtered_path.append(path[j])
        i = j

    return filtered_path
