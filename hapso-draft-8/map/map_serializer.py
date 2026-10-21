from datetime import datetime
from map.grid_map import GridMap

import json
import os


class MapSerializer:
    @staticmethod
    def load(path: str) -> GridMap | None:
        if not os.path.exists(path):
            print(f"[MAP_SERIALIZER]: File not found - {path}")
            return None
        with open(path, "r") as file:
            data = json.load(file)
        return GridMap.from_dict(data)

    @staticmethod
    def save(grid_map: GridMap, map_dir: str = "data/maps") -> str | None:
        if not os.path.exists(map_dir):
            os.makedirs(map_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        map_path = os.path.join(map_dir, timestamp)
        os.makedirs(map_path, exist_ok=True)
        json_path = os.path.join(map_path, "map.json")
        with open(json_path, "w") as file:
            json.dump(grid_map.to_dict(), file, indent=2)
        return json_path
