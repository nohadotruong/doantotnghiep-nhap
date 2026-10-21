from environment.grid_map import GridMap
from typing import Dict, List, Optional, Tuple
from utils.geometry import (
    calculate_path_metrics,
    check_collision_line,
    check_collision_line_with_clearance,
    euclidean_distance,
)

import heapq


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
        return euclidean_distance((pos[0], pos[1]), (self.goal[0], self.goal[1]))

    def _movement_cost(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> float:
        return euclidean_distance(from_pos, to_pos)

    def _reconstruct_path(self, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def validate_path(self, path: List[Tuple[int, int]]) -> bool:
        for i in range(len(path) - 1):
            if check_collision_line(self.grid, path[i], path[i + 1]):
                return False
        return True


class AstarNoCornercutting:
    """
    A* algorithm with clearance margin to prevent corner cutting.

    This version ensures that paths maintain a safe distance from obstacles,
    preventing diagonal cutting through obstacle corners.
    """

    def __init__(self, grid: GridMap, clearance: float = 0.5):
        """
        Initialize A* with corner cutting prevention.

        Args:
            grid: The grid map
            clearance: Minimum safe distance from obstacles (default 1.5)
        """
        self.grid = grid
        self.goal = None
        self.clearance = clearance
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

                # Check collision with clearance
                if check_collision_line_with_clearance(
                    self.grid, current, neighbor, self.clearance
                ):
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
        return euclidean_distance((pos[0], pos[1]), (self.goal[0], self.goal[1]))

    def _movement_cost(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> float:
        return euclidean_distance(from_pos, to_pos)

    def _reconstruct_path(self, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def validate_path(self, path: List[Tuple[int, int]]) -> bool:
        for i in range(len(path) - 1):
            if check_collision_line_with_clearance(
                self.grid, path[i], path[i + 1], self.clearance
            ):
                return False
        return True

    def get_path_metrics(self, path: List[Tuple[int, int]]) -> dict:
        return calculate_path_metrics(self.grid, path)
