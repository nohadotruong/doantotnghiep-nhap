from core.algorithms.base_planner import Planner
from core.utils.path_smoother import PathSmoother
from map.grid_map import GridMap
from typing import Optional

import heapq


class Node:
    def __init__(self, x: int, y: int, g: float, h: float) -> None:
        self.x: int = x
        self.y: int = y
        self.g: float = g
        self.h: float = h
        self.f: float = g + h
        self.parent: Optional["Node"] = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __lt__(self, other: "Node") -> bool:
        return self.f < other.f


class AStar(Planner):
    DIRECTIONS: list[tuple[int, int]] = [
        (0, -1),
        (1, 0),
        (0, 1),
        (-1, 0),
        (1, -1),
        (1, 1),
        (-1, 1),
        (-1, -1),
    ]
    STRAIGHT_COST: float = 1.0
    DIAGONAL_COST: float = 1.414213562

    def __init__(
        self,
        grid_map: GridMap,
        remove_redundant: bool = False,
        remove_transitive: bool = False,
        avoid_corner_cutting: bool = False,
    ) -> None:
        self.grid_map: GridMap = grid_map
        self.start: Optional[tuple[int, int]] = None
        self.goal: Optional[tuple[int, int]] = None
        self.obstacles: list[tuple[int, int]] = []

        self.remove_redundant: bool = remove_redundant
        self.remove_transitive: bool = remove_transitive
        self.avoid_corner_cutting: bool = avoid_corner_cutting

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> Optional[list[tuple[int, int]]]:
        self.start = start
        self.goal = goal
        self.obstacles = self.grid_map.get_obstacles()

        start_x, start_y = start
        goal_x, goal_y = goal

        if not self._is_valid(start_x, start_y):
            return None
        if not self._is_valid(goal_x, goal_y):
            return None

        open_set: list[Node] = []
        closed_set: set[tuple[int, int]] = set()
        open_dict: dict[tuple[int, int], Node] = {}

        start_node = Node(
            start_x, start_y, 0, self._heuristic(start_x, start_y, goal_x, goal_y)
        )
        heapq.heappush(open_set, start_node)
        open_dict[(start_x, start_y)] = start_node

        while open_set:
            current = heapq.heappop(open_set)
            current_pos = (current.x, current.y)

            if current_pos in open_dict:
                del open_dict[current_pos]

            if current_pos in closed_set:
                continue

            if current.x == goal_x and current.y == goal_y:
                path = self._reconstruct_path(current)
                # Apply optional smoothing
                path = PathSmoother.smooth(
                    path,
                    grid_map=self.grid_map,
                    remove_redundant=self.remove_redundant,
                    remove_transitive=self.remove_transitive,
                )
                return path

            closed_set.add(current_pos)

            # Explore neighbors
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
                g_cost = current.g + move_cost
                h_cost = self._heuristic(neighbor_x, neighbor_y, goal_x, goal_y)

                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]

                    if g_cost < neighbor_node.g:
                        neighbor_node.g = g_cost
                        neighbor_node.f = g_cost + h_cost
                        neighbor_node.parent = current
                        heapq.heappush(open_set, neighbor_node)
                else:
                    neighbor_node = Node(neighbor_x, neighbor_y, g_cost, h_cost)
                    neighbor_node.parent = current
                    heapq.heappush(open_set, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        # No path found
        return None

    def _can_move_diagonal(self, x: int, y: int, dx: int, dy: int) -> bool:
        if abs(dx) != 1 or abs(dy) != 1:
            return True

        # Both adjacent cells must be free for diagonal move
        obs1 = not self._is_valid(x + dx, y)
        obs2 = not self._is_valid(x, y + dy)

        if obs1 and obs2:
            return False

        # Additional: avoid corner cutting through narrow spaces
        if self.avoid_corner_cutting:
            left = not self._is_valid(x - 1, y)
            right = not self._is_valid(x + 1, y)
            up = not self._is_valid(x, y - 1)
            down = not self._is_valid(x, y + 1)

            # If any cardinal neighbor is blocked, no diagonals
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

    def _reconstruct_path(self, node: Node) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current: Optional[Node] = node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        path.reverse()
        return path
