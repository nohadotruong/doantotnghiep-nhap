from __future__ import annotations

import json
from datetime import datetime
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


def save_map_bundle(
    grid: Grid,
    start: Point | None,
    goal: Point | None,
    cell_size: int = 20,
    base_dir: str | Path = "data/maps",
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = Path(base_dir) / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)

    save_map_json(target_dir / "map.json", grid, start, goal)
    save_map_png(target_dir / "map.png", grid, cell_size)
    return target_dir


def list_saved_maps(base_dir: str | Path = "data/maps") -> list[Path]:
    root = Path(base_dir)
    if not root.exists():
        return []

    candidates = [p for p in root.iterdir() if p.is_dir() and (p / "map.json").exists()]
    candidates.sort(key=lambda p: p.name, reverse=True)
    return candidates


def load_map_from_dir(map_dir: str | Path) -> tuple[Grid, Point | None, Point | None]:
    return load_map_json(Path(map_dir) / "map.json")
