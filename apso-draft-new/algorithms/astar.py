from environment.grid_map import GridMap
from typing import Dict, List, Optional, Tuple

import heapq
import math


class Astar:
    def __init__(self, grid: GridMap):
        self.grid = grid
        self.goal = None
        self.came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.g_score: Dict[Tuple[int, int], float] = {}
        self.f_score: Dict[Tuple[int, int], float] = {}
        self.visited = set()
        self.open_set = []

    def plan(self) -> Optional[List[Tuple[int, int]]]:
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
        self.f_score = {start: self._heuristic(start)}
        self.visited = set()
        self.open_set = [(self._heuristic(start), 0, start)]

        while self.open_set:
            _, current_g, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)

            if current == goal:
                return self._reconstruct_path(current)

            for neighbor in self.grid.get_neighbors(current[0], current[1]):
                if neighbor in self.visited:
                    continue

                cost = self._movement_cost(current, neighbor)

                tentative_g = current_g + cost

                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g

                    self.f_score[neighbor] = tentative_g + self._heuristic(neighbor)

                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], tentative_g, neighbor),
                    )

        return None

    def _heuristic(self, pos: Tuple[int, int]) -> float:
        dx = pos[0] - self.goal[0]
        dy = pos[1] - self.goal[1]
        return math.sqrt(dx * dx + dy * dy)

    def _movement_cost(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> float:

        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        return math.sqrt(2) if (dx == 1 and dy == 1) else 1.0

    def _reconstruct_path(self, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path
