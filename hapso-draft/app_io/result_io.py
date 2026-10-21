from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pygame

from utils.grid_utils import Grid, Point


def _render_result_surface(
    grid: Grid,
    path: list[Point],
    start: Point | None,
    goal: Point | None,
    cell_size: int,
) -> pygame.Surface:
    height = len(grid)
    width = len(grid[0])
    surface = pygame.Surface((width * cell_size, height * cell_size))
    surface.fill((255, 255, 255))

    for y in range(height):
        for x in range(width):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            color = (0, 0, 0) if grid[y][x] == 1 else (255, 255, 255)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (190, 190, 190), rect, 1)

    if len(path) >= 2:
        points = [
            (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
            for x, y in path
        ]
        pygame.draw.lines(surface, (53, 112, 201), False, points, 3)

    if start:
        sx, sy = start
        pygame.draw.circle(
            surface,
            (39, 163, 108),
            (sx * cell_size + cell_size // 2, sy * cell_size + cell_size // 2),
            max(4, cell_size // 2 - 2),
        )

    if goal:
        gx, gy = goal
        pygame.draw.circle(
            surface,
            (216, 73, 60),
            (gx * cell_size + cell_size // 2, gy * cell_size + cell_size // 2),
            max(4, cell_size // 2 - 2),
        )

    return surface


def save_result_bundle(
    grid: Grid,
    path: list[Point],
    start: Point | None,
    goal: Point | None,
    algorithm: str,
    metrics: dict[str, float | int] | None,
    settings: dict[str, bool] | None,
    cell_size: int = 20,
    base_dir: str | Path = "data/results",
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = Path(base_dir) / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "algorithm": algorithm,
        "start": list(start) if start else None,
        "goal": list(goal) if goal else None,
        "path": [list(p) for p in path],
        "metrics": metrics,
        "settings": settings,
        "map": {"grid": grid},
    }
    (target_dir / "result.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    image = _render_result_surface(grid, path, start, goal, cell_size)
    pygame.image.save(image, str(target_dir / "result.png"))
    return target_dir
