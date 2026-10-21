from core.algorithms.base_planner import BasePlanner
from core.utils.path_smoother import PathSmoother
from map.grid_map import GridMap
from math import sqrt
from typing import Optional
from config.algo_config import (
    ASTAR_REMOVE_REDUNDANT,
    ASTAR_REMOVE_TRANSITION,
    ASTAR_MIN_CLEARANCE,
)

import heapq


class Astar(BasePlanner):
    def __init__(
        self,
        grid: GridMap,
        remove_redundant: bool = ASTAR_REMOVE_REDUNDANT,
        remove_transition: bool = ASTAR_REMOVE_TRANSITION,
        min_clearance: float = ASTAR_MIN_CLEARANCE,
    ) -> None:
        super().__init__()
        self.grid = grid
        self.goal: tuple[int, int] | None = None
        self.remove_redundant = remove_redundant
        self.remove_transition = remove_transition
        self.min_clearance = float(min_clearance)
        self.came_from: dict[tuple[int, int], tuple[int, int]] = {}
        self.g_score: dict[tuple[int, int], float] = {}
        self.f_score: dict[tuple[int, int], float] = {}
        self.visited: set[tuple[int, int]] = set()
        self.open_set: list[tuple[float, float, float, tuple[int, int]]] = []

    def plan(self) -> Optional[list[tuple[int, int]]]:
        start = self.grid.start
        goal = self.grid.goal

        if not self.grid.is_inside(start[0], start[1]) or self.grid.is_obstacle(
            start[0], start[1]
        ):
            return None
        if not self.grid.is_inside(goal[0], goal[1]) or self.grid.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        if start == goal:
            return [start, goal]

        self.goal = goal
        self.came_from = {}
        self.g_score = {start: 0}
        start_h = self._heuristic(start)
        self.f_score = {start: start_h}
        self.visited = set()
        self.open_set = [(start_h, start_h, 0, start)]

        while self.open_set:
            _, _, current_g, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)

            if current == goal:
                path = self._reconstruct_path(current)
                return self._post_process_path(path)

            cx, cy = current

            for neighbor in self.grid.get_neighbors(cx, cy):
                if neighbor in self.visited:
                    continue

                if self.min_clearance > 0.0:
                    if not self._check_clearance(current, neighbor, self.min_clearance):
                        continue

                cost = self._movement_cost(current, neighbor)

                tentative_g = current_g + cost

                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g

                    neighbor_h = self._heuristic(neighbor)
                    self.f_score[neighbor] = tentative_g + neighbor_h

                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], neighbor_h, tentative_g, neighbor),
                    )

        return None

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        prev_start = self.grid.start
        prev_goal = self.grid.goal
        try:
            self.grid.start = start
            self.grid.goal = goal
            return self.plan()
        finally:
            self.grid.start = prev_start
            self.grid.goal = prev_goal

    def _heuristic(self, pos: tuple[int, int]) -> float:
        dx = self.goal[0] - pos[0]
        dy = self.goal[1] - pos[1]
        return sqrt(dx * dx + dy * dy)

    def _movement_cost(
        self, from_pos: tuple[int, int], to_pos: tuple[int, int]
    ) -> float:
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        return sqrt(dx * dx + dy * dy)

    def _reconstruct_path(self, current: tuple[int, int]) -> list[tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def _post_process_path(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        return PathSmoother.smooth(
            path,
            grid_map=self.grid,
            remove_redundant=self.remove_redundant,
            transition=self.remove_transition,
            min_clearance=self.min_clearance,
        )

    def _check_clearance(
        self, a: tuple[int, int], b: tuple[int, int], min_clearance: float
    ) -> bool:
        obstacles = self.grid.get_obstacles_as_centers()
        if obstacles is None or len(obstacles) == 0:
            return True
        a_center = (float(a[0]) + 0.5, float(a[1]) + 0.5)
        b_center = (float(b[0]) + 0.5, float(b[1]) + 0.5)
        min_dist = BasePlanner._min_distance_segment_to_obstacles(
            a_center, b_center, obstacles
        )
        return min_dist >= min_clearance
