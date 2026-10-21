from environment.grid_map import GridMap
from typing import Dict, List, Optional, Tuple
from utils.geometry import (

    check_collision_line,
    has_corner_obstacle,
    euclidean_distance,
    remove_redundant_points,
    remove_redundant_transitions,
)

import heapq

class Astar:
    def __init__(
        self,
        grid: GridMap,
        prune_collinear: bool = False,
        prune_transitions: bool = False,
        avoid_corner_cutting: bool = False,
    ):
        self.grid = grid
        self.goal = None
        self.prune_collinear = prune_collinear
        self.prune_transitions = prune_transitions
        self.avoid_corner_cutting = avoid_corner_cutting
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
        self.f_score = {start: euclidean_distance(start, goal)}
        self.visited = set()
        self.open_set = [(euclidean_distance(start, goal), 0, start)]

        while self.open_set:
            _, current_g, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)

            if current == goal:
                path = self._reconstruct_path(current)
                processed_path = self._post_process_path(path)

                if self.avoid_corner_cutting or self.prune_transitions:
                    for i in range(len(processed_path) - 1):
                        p1 = (float(processed_path[i][0]), float(processed_path[i][1]))
                        p2 = (
                            float(processed_path[i + 1][0]),
                            float(processed_path[i + 1][1]),
                        )
                        if check_collision_line(self.grid, p1, p2):
                            print(
                                f"[A* DEBUG]  COLLISION in segment {i}: {processed_path[i]}  {processed_path[i+1]}"
                            )

                return processed_path

            cx, cy = current

            for neighbor in self._get_valid_neighbors(current):
                cost = euclidean_distance(current, neighbor)

                tentative_g = current_g + cost

                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g

                    self.f_score[neighbor] = tentative_g + euclidean_distance(
                        neighbor, goal
                    )

                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], tentative_g, neighbor),
                    )

        return None

    def _get_valid_neighbors(self, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        valid = []

        for neighbor in self.grid.get_neighbors(current[0], current[1]):
            if neighbor in self.visited:
                continue

            if self.grid.is_obstacle(neighbor[0], neighbor[1]):
                continue

            if self.avoid_corner_cutting and has_corner_obstacle(
                self.grid, current, neighbor
            ):
                continue

            valid.append(neighbor)

        return valid

    def _reconstruct_path(self, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def _post_process_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        if self.prune_collinear:
            path = remove_redundant_points(path)
        if self.prune_transitions:

            path = remove_redundant_transitions(
                self.grid, path, self.avoid_corner_cutting
            )
        return path