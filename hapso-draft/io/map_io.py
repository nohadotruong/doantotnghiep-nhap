from __future__ import annotations

import json
from pathlib import Path

import pygame

from utils.grid_utils import Grid, Point


def save_map_json(
    path: str | Path, grid: Grid, start: Point | None, goal: Point | None
) -> None:
    payload = {
        "grid": grid,
        "start": list(start) if start else None,
        "goal": list(goal) if goal else None,
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_map_json(path: str | Path) -> tuple[Grid, Point | None, Point | None]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    start = tuple(data["start"]) if data.get("start") else None
    goal = tuple(data["goal"]) if data.get("goal") else None
    return data["grid"], start, goal


def save_map_png(path: str | Path, grid: Grid, cell_size: int = 20) -> None:
    height = len(grid)
    width = len(grid[0])
    surface = pygame.Surface((width * cell_size, height * cell_size))
    surface.fill((245, 246, 248))

    for y in range(height):
        for x in range(width):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            color = (35, 36, 45) if grid[y][x] == 1 else (245, 246, 248)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (220, 224, 230), rect, 1)

    pygame.image.save(surface, str(path))
