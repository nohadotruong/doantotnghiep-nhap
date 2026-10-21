import numpy as np


class GridMap:
    FREE = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None

    def clear_map(self) -> None:
        self.grid = [[self.FREE for _ in range(self.width)] for _ in range(self.height)]
        self.start = None
        self.goal = None

    @staticmethod
    def from_dict(data: dict) -> "GridMap":
        grid_map = GridMap(data["width"], data["height"])
        grid_map.grid = data["grid"]
        grid_map.start = tuple(data["start"]) if data["start"] else None
        grid_map.goal = tuple(data["goal"]) if data["goal"] else None
        return grid_map

    def get_obstacle_count(self) -> int:
        return len(self.get_obstacles())

    def get_obstacles(self) -> list[tuple[int, int]]:
        obstacles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    obstacles.append((x, y))
        return obstacles

    def get_obstacles_as_centers(self) -> np.ndarray:
        return np.array(
            [
                [c + 0.5, r + 0.5]
                for r in range(self.height)
                for c in range(self.width)
                if self.grid[r][c] == self.OBSTACLE
            ],
            dtype=float,
        )

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True
        return self.grid[y][x] == self.OBSTACLE

    def set_goal(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False
        if self.goal is not None:
            old_x, old_y = self.goal
            if self.grid[old_y][old_x] == self.GOAL:
                self.grid[old_y][old_x] = self.FREE
        self.goal = (x, y)
        self.grid[y][x] = self.GOAL
        return True

    def set_obstacle(self, x: int, y: int, value: bool) -> bool:
        if not self.is_inside(x, y):
            return False
        if (x, y) == self.start or (x, y) == self.goal:
            return False
        if value:
            self.grid[y][x] = self.OBSTACLE
        else:
            self.grid[y][x] = self.FREE
        return True

    def set_start(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False
        if self.start is not None:
            old_x, old_y = self.start
            if self.grid[old_y][old_x] == self.START:
                self.grid[old_y][old_x] = self.FREE
        self.start = (x, y)
        self.grid[y][x] = self.START
        return True

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid,
            "start": self.start,
            "goal": self.goal,
        }

    def toggle_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return False
        if (x, y) == self.start or (x, y) == self.goal:
            return False
        if self.grid[y][x] == self.OBSTACLE:
            self.grid[y][x] = self.FREE
        else:
            self.grid[y][x] = self.OBSTACLE
        return True
