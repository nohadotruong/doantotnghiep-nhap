"""
A* pathfinding algorithm implementation.

This is a minimal A* implementation for grid-based pathfinding.
For production use, refactor algorithms from other_project/algorithms/astar.py
"""

from typing import List, Tuple, Optional
import heapq
import math

import planning.api as plan_api
from planning.core.base import BasePlanner


class AStarPlanner(BasePlanner):
    """A* pathfinding algorithm."""

    def __init__(
        self,
        grid: plan_api.Grid,
        start: plan_api.Point,
        goal: plan_api.Point,
        prune_collinear: bool = True,
        prune_transitions: bool = True,
        avoid_corner_cutting: bool = False,
    ):
        """Initialize A* planner."""
        super().__init__(grid, start, goal)
        self.prune_collinear = prune_collinear
        self.prune_transitions = prune_transitions
        self.avoid_corner_cutting = avoid_corner_cutting

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        """
        Execute A* algorithm.

        Returns:
            List of waypoints (x, y) from start to goal, or None if no path found
        """
        start_tuple = (int(self.start.x), int(self.start.y))
        goal_tuple = (int(self.goal.x), int(self.goal.y))

        if start_tuple == goal_tuple:
            return [start_tuple]

        # Open set: priority queue of (f_score, counter, position)
        open_set = []
        counter = 0
        heapq.heappush(open_set, (0, counter, start_tuple))
        counter += 1

        # Track visited nodes
        visited = set()
        came_from = {}
        g_score = {start_tuple: 0}

        neighbors_4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors_8 = neighbors_4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        neighbors = neighbors_8

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            if current == goal_tuple:
                # Reconstruct path
                path = []
                node = current
                while node in came_from:
                    path.append(node)
                    node = came_from[node]
                path.append(start_tuple)
                path.reverse()

                # Post-processing
                if self.prune_collinear:
                    path = self._remove_collinear(path)
                if self.prune_transitions:
                    path = self._smooth_path(path)

                return path

            # Explore neighbors
            for dx, dy in neighbors:
                nx, ny = current[0] + dx, current[1] + dy
                neighbor = (nx, ny)

                # Check bounds
                if not self.grid.is_in_bounds(nx, ny):
                    continue

                # Check obstacle
                if self.grid.is_obstacle(nx, ny):
                    continue

                # Check diagonal corner cutting
                if (
                    self.avoid_corner_cutting
                    and max(abs(dx), abs(dy)) == 1
                    and min(abs(dx), abs(dy)) == 1
                ):
                    # Diagonal move - check corner
                    if self.grid.is_obstacle(
                        current[0] + dx, current[1]
                    ) or self.grid.is_obstacle(current[0], current[1] + dy):
                        continue

                # Calculate new g_score
                cost = math.sqrt(dx * dx + dy * dy)
                tentative_g = g_score[current] + cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal_tuple)

                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    counter += 1

                    came_from[neighbor] = current

        return None  # No path found

    def _heuristic(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Euclidean distance heuristic."""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        return math.sqrt(dx * dx + dy * dy)

    def _remove_collinear(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Remove collinear waypoints."""
        if len(path) <= 2:
            return path

        result = [path[0]]

        for i in range(1, len(path) - 1):
            p1 = path[i - 1]
            p2 = path[i]
            p3 = path[i + 1]

            # Cross product to check collinearity
            cross = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (
                p3[0] - p1[0]
            )

            if cross != 0:  # Not collinear
                result.append(p2)

        result.append(path[-1])
        return result

    def _smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Line-of-sight smoothing."""
        if len(path) <= 2:
            return path

        result = [path[0]]
        i = 0

        while i < len(path) - 1:
            # Try to reach as far as possible
            j = len(path) - 1
            while j > i + 1:
                if self._has_line_of_sight(path[i], path[j]):
                    result.append(path[j])
                    i = j
                    break
                j -= 1
            else:
                # Could not reach further, go to next
                result.append(path[i + 1])
                i += 1

        return result

    def _has_line_of_sight(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        """Check if there's line-of-sight between two points."""
        x0, y0 = p1
        x1, y1 = p2

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1

        if dx > dy:
            err = dx / 2.0
            y = y0
            for x in range(x0, x1 + sx, sx):
                if self.grid.is_obstacle(x, y):
                    return False
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
        else:
            err = dy / 2.0
            x = x0
            for y in range(y0, y1 + sy, sy):
                if self.grid.is_obstacle(x, y):
                    return False
                err -= dx
                if err < 0:
                    x += sx
                    err += dy

        return True


__all__ = ["AStarPlanner"]
