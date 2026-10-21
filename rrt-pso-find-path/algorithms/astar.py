import heapq
import math


class AStarPlanner:
    def __init__(
        self,
        environment,
        start,
        goal,
        grid_resolution=2.0,
        heuristic="euclidean",
        allow_diagonal=True,
    ):
        self.environment = environment
        self.start = start
        self.goal = goal
        self.grid_resolution = grid_resolution
        self.heuristic_type = heuristic
        self.allow_diagonal = allow_diagonal

        if environment.is_inside_obstacle(start[0], start[1]):
            raise ValueError(f"Start position {start} is inside obstacle")
        if environment.is_inside_obstacle(goal[0], goal[1]):
            raise ValueError(f"Goal position {goal} is inside obstacle")

        self.cols = int(math.ceil(environment.width / grid_resolution))
        self.rows = int(math.ceil(environment.height / grid_resolution))

        self.start_grid = self._world_to_grid(start)
        self.goal_grid = self._world_to_grid(goal)

    def _world_to_grid(self, world_pos):
        grid_x = int(world_pos[0] / self.grid_resolution)
        grid_y = int(world_pos[1] / self.grid_resolution)

        grid_x = max(0, min(grid_x, self.cols - 1))
        grid_y = max(0, min(grid_y, self.rows - 1))

        return (grid_x, grid_y)

    def _grid_to_world(self, grid_pos):
        world_x = grid_pos[0] * self.grid_resolution + self.grid_resolution / 2
        world_y = grid_pos[1] * self.grid_resolution + self.grid_resolution / 2

        return (world_x, world_y)

    def _is_walkable(self, grid_pos):
        world_pos = self._grid_to_world(grid_pos)
        return not self.environment.is_inside_obstacle(world_pos[0], world_pos[1])

    def _get_neighbors(self, grid_pos):
        x, y = grid_pos
        neighbors = []

        directions_4 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        directions_diagonal = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        directions = directions_4
        if self.allow_diagonal:
            directions = directions_4 + directions_diagonal

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                if self._is_walkable((nx, ny)):
                    neighbors.append((nx, ny))

        return neighbors

    def _heuristic(self, grid_pos1, grid_pos2):
        dx = abs(grid_pos1[0] - grid_pos2[0])
        dy = abs(grid_pos1[1] - grid_pos2[1])

        if self.heuristic_type == "manhattan":
            return dx + dy
        else:
            return math.sqrt(dx * dx + dy * dy)

    def _get_cost(self, grid_pos1, grid_pos2):
        dx = abs(grid_pos1[0] - grid_pos2[0])
        dy = abs(grid_pos1[1] - grid_pos2[1])

        if dx == 1 and dy == 1:
            return math.sqrt(2)
        else:
            return 1.0

    def plan(self):
        counter = 0
        open_set = [(0, counter, self.start_grid)]

        closed_set = set()

        g_score = {self.start_grid: 0}
        f_score = {self.start_grid: self._heuristic(self.start_grid, self.goal_grid)}

        parent = {self.start_grid: None}

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            closed_set.add(current)

            if current == self.goal_grid:
                path = self._reconstruct_path(parent, current)
                return path

            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + self._get_cost(current, neighbor)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = self._heuristic(neighbor, self.goal_grid)
                    f_score[neighbor] = tentative_g + h

                    counter += 1
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))

        return None

    def _reconstruct_path(self, parent, current):
        path = [self._grid_to_world(current)]

        while parent[current] is not None:
            current = parent[current]
            path.append(self._grid_to_world(current))

        path.reverse()

        return path


if __name__ == "__main__":
    from environment.environment import UAVEnvironment

    uav_map = UAVEnvironment.load_map(
        r"D:\DEV\_Projects\TLU\DoAn\rrt-pso-find-path\maps\map_20260302_164324\config.json"
    )
    astar_planner = AStarPlanner(uav_map, (0, 0), (100, 100))
    astar_path = astar_planner.plan()
    uav_map.visualize(astar_path)
