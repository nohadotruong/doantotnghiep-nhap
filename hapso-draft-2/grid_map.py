from datetime import datetime
from typing import List, Optional, Tuple
import json
import os
from PIL import Image, ImageDraw


class GridMap:
    FREE = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]
        self.start: Optional[Tuple[int, int]] = None
        self.goal: Optional[Tuple[int, int]] = None

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

    def get_obstacles(self) -> List[Tuple[int, int]]:
        obstacles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    obstacles.append((x, y))
        return obstacles

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True
        return self.grid[y][x] == self.OBSTACLE

    @staticmethod
    def load_map(json_path: str) -> Optional["GridMap"]:
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            return GridMap.from_dict(data)
        except Exception as e:
            print(f"Error loading map: {e}")
            return None

    def _default_screenshot(self, map_path: str) -> Optional[str]:
        """Tạo ảnh preview của bản đồ sử dụng PIL"""
        try:
            cell_size = 30
            padding = 20
            img_width = self.width * cell_size + padding * 2
            img_height = self.height * cell_size + padding * 2
            img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            for y in range(self.height):
                for x in range(self.width):
                    x1 = padding + x * cell_size
                    y1 = padding + (self.height - 1 - y) * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size

                    cell_value = self.grid[y][x]
                    if cell_value == self.OBSTACLE:
                        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
                    elif cell_value == self.START:
                        draw.rectangle([x1, y1, x2, y2], fill=(0, 255, 0))
                    elif cell_value == self.GOAL:
                        draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0))
                    else:
                        draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255))

                    draw.rectangle([x1, y1, x2, y2], outline=(200, 200, 200), width=1)

            image_path = os.path.join(map_path, "preview.png")
            img.save(image_path)
            return image_path
        except Exception as e:
            print(f"Error creating screenshot: {e}")
            return None

    def save_map(
        self, map_dir: str = "maps", screenshot_func=None
    ) -> Optional[Tuple[str, Optional[str]]]:
        try:
            if not os.path.exists(map_dir):
                os.makedirs(map_dir)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            map_path = os.path.join(map_dir, timestamp)
            os.makedirs(map_path, exist_ok=True)
            json_path = os.path.join(map_path, "map.json")
            with open(json_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            if screenshot_func is None:
                screenshot_func = self._default_screenshot
            image_path = screenshot_func(map_path)
            return (json_path, image_path)
        except Exception as e:
            print(f"Error saving map: {e}")
            return None

    def set_goal(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False
        if self.goal is not None:
            (old_x, old_y) = self.goal
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
            (old_x, old_y) = self.start
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
