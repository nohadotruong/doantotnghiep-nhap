from .base_planner import BasePlanner
from map.grid_map import GridMap
from optimization.path_smoother import PathSmoother
from typing import List, Optional, Tuple

import heapq


class Node:
    def __init__(self, x: int, y: int, g_cost: float, h_cost: float):
        self.x = x
        self.y = y
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = None

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):
        return self.f_cost < other.f_cost


class Astar(BasePlanner):
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    STRAIGHT_COST = 1.0
    DIAGONAL_COST = 1.414213562

    def __init__(
        self,
        grid_map: Optional["GridMap"],
        remove_redundant: bool = False,
        remove_transitive: bool = False,
        avoid_corner_cutting: bool = False,
    ):
        super().__init__(grid_map)

        self.grid_map = grid_map
        self.remove_redundant = remove_redundant
        self.remove_transitive = remove_transitive
        self.avoid_corner_cutting = avoid_corner_cutting

    def find_path(self) -> Optional[List[Tuple[int, int]]]:
        if not self.validate_input():
            return None

        start = self.grid_map.start
        goal = self.grid_map.goal

        (start_x, start_y) = start
        (goal_x, goal_y) = goal

        if not self._is_valid(start_x, start_y):
            return None

        if not self._is_valid(goal_x, goal_y):
            return None

        open_set = []
        closed_set = set()
        open_dict = {}

        start_node = Node(
            start_x, start_y, 0, self._heuristic(start_x, start_y, goal_x, goal_y)
        )
        heapq.heappush(open_set, start_node)
        open_dict[start_x, start_y] = start_node

        while open_set:
            current = heapq.heappop(open_set)
            current_pos = (current.x, current.y)

            open_dict.pop(current_pos, None)

            if current_pos in closed_set:
                continue

            if current.x == goal_x and current.y == goal_y:
                path = self._reconstruct_path(current)

                if self.remove_redundant or self.remove_transitive:
                    path = PathSmoother.smooth(
                        path=path,
                        remove_redundant=self.remove_redundant,
                        remove_transitive=self.remove_transitive,
                    )

                return path

            closed_set.add(current_pos)

            for dx, dy in self.DIRECTIONS:
                neighbor_x = current.x + dx
                neighbor_y = current.y + dy
                if not self._is_valid(neighbor_x, neighbor_y):
                    continue

                if not self._can_move_diagonal(current.x, current.y, dx, dy):
                    continue

                neighbor_pos = (neighbor_x, neighbor_y)
                if neighbor_pos in closed_set:
                    continue

                move_cost = self._get_cost(dx, dy)
                g_cost = current.g_cost + move_cost
                h_cost = self._heuristic(neighbor_x, neighbor_y, goal_x, goal_y)

                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]

                    if g_cost < neighbor_node.g_cost:
                        neighbor_node.g_cost = g_cost
                        neighbor_node.f_cost = g_cost + h_cost

                        neighbor_node.parent = current
                        heapq.heappush(open_set, neighbor_node)
                else:
                    neighbor_node = Node(neighbor_x, neighbor_y, g_cost, h_cost)
                    neighbor_node.parent = current

                    heapq.heappush(open_set, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        return None

    def _can_move_diagonal(
        self, current_x: int, current_y: int, delta_x: int, delta_y: int
    ) -> bool:
        if abs(delta_x) != 1 or abs(delta_y) != 1:
            return True

        x_adjacent_blocked = not self._is_valid(current_x + delta_x, current_y)
        y_adjacent_blocked = not self._is_valid(current_x, current_y + delta_y)

        if x_adjacent_blocked and y_adjacent_blocked:
            return False

        if self.avoid_corner_cutting:
            left = not self._is_valid(current_x - 1, current_y)
            right = not self._is_valid(current_x + 1, current_y)
            up = not self._is_valid(current_x, current_y - 1)
            down = not self._is_valid(current_x, current_y + 1)

            if left or right or up or down:
                return False

        return True

    def _get_cost(self, dx: int, dy: int) -> float:
        if abs(dx) == 1 and abs(dy) == 1:
            return self.DIAGONAL_COST
        return self.STRAIGHT_COST

    def _heuristic(self, x: int, y: int, goal_x: int, goal_y: int) -> float:
        dx = goal_x - x
        dy = goal_y - y
        return (dx * dx + dy * dy) ** 0.5

    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        path = []
        current = node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        path.reverse()
        return path
