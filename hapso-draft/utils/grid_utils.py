from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.geometry import check_corner_collision

Grid = list[list[int]]
Point = tuple[int, int]


def is_valid(x: int, y: int, grid: Grid) -> bool:
    """Return True when (x, y) is inside the grid bounds."""
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def is_obstacle(x: int, y: int, grid: Grid) -> bool:
    """Return True when the cell is blocked or out of bounds."""
    return not is_valid(x, y, grid) or grid[y][x] == 1


def get_neighbors(
    x: int,
    y: int,
    grid: Grid,
    diagonal: bool = True,
    avoid_corner_cutting: bool = False,
    check_corner_collision: callable = None,
) -> Iterable[Point]:
    """Yield free neighboring cells in 4- or 8-connected mode.

    Args:
        x, y: Current position
        grid: Grid map
        diagonal: Include diagonal neighbors (8-connected=True, 4-connected=False)
        avoid_corner_cutting: If True, check for corner collisions in diagonal moves
        check_corner_collision: Function to check corner collision (optional)
    """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if not is_valid(nx, ny, grid) or is_obstacle(nx, ny, grid):
            continue

        # Check corner collision for diagonal moves
        if avoid_corner_cutting and check_corner_collision is not None:
            if abs(dx) == 1 and abs(dy) == 1:  # Diagonal move
                if check_corner_collision((x, y), (nx, ny), grid):
                    continue

        yield nx, ny
