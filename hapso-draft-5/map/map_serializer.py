from datetime import datetime
from map.grid_map import GridMap
from PIL import Image, ImageDraw
from typing import Callable, Optional, Tuple

import json
import os


class MapSerializer:
    @staticmethod
    def load(path: str) -> Optional[GridMap]:
        try:
            with open(path, "r") as file:
                data = json.load(file)
            return GridMap.from_dict(data)
        except Exception as error:
            print(f"[MAP_SERIALIZER]: Error - {error}")
            return None

    @staticmethod
    def save(
        grid_map: GridMap,
        map_dir: str = "data/maps",
        screenshot_func: Optional[Callable[[str], Optional[str]]] = None,
    ) -> Optional[Tuple[str, Optional[str]]]:
        try:
            if not os.path.exists(map_dir):
                os.makedirs(map_dir)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            map_path = os.path.join(map_dir, timestamp)
            os.makedirs(map_path, exist_ok=True)
            json_path = os.path.join(map_path, "map.json")
            with open(json_path, "w") as file:
                json.dump(grid_map.to_dict(), file, indent=2)
            if screenshot_func is None:
                screenshot_func = lambda p: MapSerializer._default_screenshot(
                    grid_map, p
                )
            image_path = screenshot_func(map_path)
            return json_path, image_path
        except Exception as error:
            print(f"[MAP_SERIALIZER]: Error - {error}")
            return None

    @staticmethod
    def _default_screenshot(grid_map: GridMap, map_path: str) -> Optional[str]:
        try:
            cell_size = 30
            padding = 20
            img_width = grid_map.width * cell_size + padding * 2
            img_height = grid_map.height * cell_size + padding * 2
            img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            for y in range(grid_map.height):
                for x in range(grid_map.width):
                    x1 = padding + x * cell_size
                    y1 = padding + (grid_map.height - 1 - y) * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    cell_value = grid_map.grid[y][x]
                    if cell_value == grid_map.OBSTACLE:
                        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
                    elif cell_value == grid_map.START:
                        draw.rectangle([x1, y1, x2, y2], fill=(0, 255, 0))
                    elif cell_value == grid_map.GOAL:
                        draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0))
                    else:
                        draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255))
                    draw.rectangle([x1, y1, x2, y2], outline=(200, 200, 200), width=1)
            image_path = os.path.join(map_path, "preview.png")
            img.save(image_path)
            return image_path
        except Exception as error:
            print(f"[MAP_SERIALIZER]: Error - {error}")
            return None
