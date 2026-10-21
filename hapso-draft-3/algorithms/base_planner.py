from abc import ABC, abstractmethod
from map.grid_map import GridMap
from optimization import LineDrawer
from typing import List, Optional, Tuple

import math


class BasePlanner(ABC):
    def __init__(self, grid_map: Optional["GridMap"]):
        self.grid_map = grid_map

    @abstractmethod
    def find_path(self) -> List[Tuple[int, int]]:
        start = self.grid_map.start
        goal = self.grid_map.goal

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def validate_input(self) -> bool:
        start = self.grid_map.start
        goal = self.grid_map.goal

        if start is None or goal is None:
            print("[BASE_PLANNER]: Start or Goal is None")
            return False

        return True

    def _normalize_path(self, path) -> List[Tuple[int, int]]:
        return [(int(x), int(y)) for x, y in path]

    def _is_valid(self, x: int, y: int) -> bool:
        return self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y)

    def _euclidean(self, point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def _segment_collision_count(
        self, segment_start: Tuple[int, int], segment_end: Tuple[int, int]
    ) -> int:
        collisions = 0
        cells = LineDrawer.voxel_traversal(segment_start, segment_end)

        for x, y in cells:
            if self.grid_map.is_inside(x, y):
                collisions += 1
                continue

            if self.grid_map.is_obstacle(x, y):
                collisions += 1

        return collisions
