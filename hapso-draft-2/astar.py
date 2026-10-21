from typing import List, Optional, Tuple
import heapq
from get_line_grid import get_line_grid_incremental_traversal

class Node:

    def __init__(self, x: int, y: int, g: float, h: float):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):
        return self.f < other.f

class AStar:
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
    STRAIGHT_COST = 1.0
    DIAGONAL_COST = 1.414213562

    def __init__(self, grid, remove_redundant: bool=False, remove_transitive: bool=False, avoid_corner_cutting: bool=False):
        self.grid = grid
        self.remove_redundant = remove_redundant
        self.remove_transitive = remove_transitive
        self.avoid_corner_cutting = avoid_corner_cutting

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        (start_x, start_y) = start
        (goal_x, goal_y) = goal
        if not self._is_walkable(start_x, start_y):
            return None
        if not self._is_walkable(goal_x, goal_y):
            return None
        open_set = []
        closed_set = set()
        open_dict = {}
        start_node = Node(start_x, start_y, 0, self._heuristic(start_x, start_y, goal_x, goal_y))
        heapq.heappush(open_set, start_node)
        open_dict[start_x, start_y] = start_node
        while open_set:
            current = heapq.heappop(open_set)
            current_pos = (current.x, current.y)
            if current_pos in open_dict:
                del open_dict[current_pos]
            if current_pos in closed_set:
                continue
            if current.x == goal_x and current.y == goal_y:
                path = self._reconstruct_path(current)
                if self.remove_redundant:
                    path = self.remove_redundant_points(path)
                if self.remove_transitive:
                    path = self.remove_transitive_redundant_points(path)
                return path
            closed_set.add(current_pos)
            for (dx, dy) in self.DIRECTIONS:
                neighbor_x = current.x + dx
                neighbor_y = current.y + dy
                if not self._is_walkable(neighbor_x, neighbor_y):
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
        return None

    def remove_redundant_points(self, path):
        if len(path) <= 2:
            return path
        optimized_path = [path[0]]
        i = 1
        while i < len(path) - 1:
            prev_point = optimized_path[-1]
            curr_point = path[i]
            next_point = path[i + 1]
            (x_prev, y_prev) = prev_point
            (x_curr, y_curr) = curr_point
            (x_next, y_next) = next_point
            v1_x = x_curr - x_prev
            v1_y = y_curr - y_prev
            v2_x = x_next - x_prev
            v2_y = y_next - y_prev
            cross_product = v1_x * v2_y - v1_y * v2_x
            is_collinear = abs(cross_product) < 1e-09
            if not is_collinear:
                optimized_path.append(curr_point)
            i += 1
        optimized_path.append(path[-1])
        return optimized_path

    def remove_transitive_redundant_points(self, path):
        if len(path) <= 2:
            return path
        optimized_path = [path[0]]
        i = 1
        while i < len(path) - 1:
            prev_point = optimized_path[-1]
            curr_point = path[i]
            next_point = path[i + 1]
            (x_prev, y_prev) = prev_point
            (x_next, y_next) = next_point
            line_cells = get_line_grid_incremental_traversal((x_prev, y_prev), (x_next, y_next))
            has_obstacle_on_direct_path = False
            for (cell_x, cell_y) in line_cells:
                if self.grid.is_obstacle(cell_x, cell_y):
                    has_obstacle_on_direct_path = True
                    break
            if has_obstacle_on_direct_path:
                line_to_curr = get_line_grid_incremental_traversal((x_prev, y_prev), (curr_point[0], curr_point[1]))
                prev_to_curr_clear = all((not self.grid.is_obstacle(cx, cy) for (cx, cy) in line_to_curr))
                if prev_to_curr_clear:
                    optimized_path.append(curr_point)
                else:
                    optimized_path.append(path[i - 1])
                    optimized_path.append(curr_point)
            i += 1
        optimized_path.append(path[-1])
        return optimized_path

    def _can_move_diagonal(self, x: int, y: int, dx: int, dy: int) -> bool:
        if abs(dx) != 1 or abs(dy) != 1:
            return True
        obs1 = not self._is_walkable(x + dx, y)
        obs2 = not self._is_walkable(x, y + dy)
        if obs1 and obs2:
            return False
        if self.avoid_corner_cutting:
            left = not self._is_walkable(x - 1, y)
            right = not self._is_walkable(x + 1, y)
            up = not self._is_walkable(x, y - 1)
            down = not self._is_walkable(x, y + 1)
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

    def _is_walkable(self, x: int, y: int) -> bool:
        if hasattr(self.grid, 'height') and hasattr(self.grid, 'width'):
            if x < 0 or x >= self.grid.width or y < 0 or (y >= self.grid.height):
                return False
            return not self.grid.is_obstacle(x, y)
        else:
            height = len(self.grid)
            width = len(self.grid[0]) if height > 0 else 0
            if x < 0 or x >= width or y < 0 or (y >= height):
                return False
            return self.grid[y][x] == 0

    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        path = []
        current = node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        path.reverse()
        return path
