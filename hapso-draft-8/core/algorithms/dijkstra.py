from core.algorithms.base_planner import BasePlanner
from map.grid_map import GridMap

import heapq


class Dijkstra(BasePlanner):
    def __init__(self, grid_map: GridMap) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles = self.grid_map.get_obstacles_as_centers()

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal

        if not self._validate_inputs():
            return None

        distances: dict[tuple[int, int], float] = {}
        parent: dict[tuple[int, int], tuple[int, int] | None] = {}
        visited: set[tuple[int, int]] = set()

        distances[start] = 0
        parent[start] = None

        pq: list[tuple[float, tuple[int, int]]] = [(0, start)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            if current == goal:
                return self._reconstruct_path(start, goal, parent)

            neighbors = self._get_neighbors(current)

            for neighbor in neighbors:
                if neighbor in visited:
                    continue

                if self._segment_has_collision(current, neighbor):
                    continue

                new_dist = current_dist + self._euclidean_distance(current, neighbor)

                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    parent[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))

        return None

    def _get_neighbors(self, point: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = point
        neighbors: list[tuple[int, int]] = []

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                nx = x + dx
                ny = y + dy

                if self._is_valid(nx, ny):
                    neighbors.append((nx, ny))

        return neighbors

    def _reconstruct_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        parent: dict[tuple[int, int], tuple[int, int] | None],
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current = goal

        while current is not None:
            path.append(current)
            current = parent.get(current)

        path.reverse()
        return path
