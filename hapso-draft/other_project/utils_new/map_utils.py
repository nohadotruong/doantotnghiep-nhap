from environment.grid_map import GridMap
from typing import List, Tuple


def is_obstacle(grid: GridMap, x: int, y: int) -> bool:
    if not is_valid(grid, x, y):
        return True
    return grid.is_obstacle(x, y)


def is_valid(grid: GridMap, x: int, y: int) -> bool:
    return grid.is_inside(x, y)


def get_neighbors(
    grid: GridMap,
    x: int,
    y: int,
    diagonal: bool = True,
) -> List[Tuple[int, int]]:
    neighbors = []

    cardinal_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    directions = cardinal_directions
    if diagonal:
        directions = cardinal_directions + diagonal_directions

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_valid(grid, nx, ny) and not is_obstacle(grid, nx, ny):
            neighbors.append((nx, ny))

    return neighbors
