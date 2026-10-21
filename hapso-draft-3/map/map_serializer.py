from datetime import datetime
from .grid_map import GridMap
from typing import Optional, Tuple

import json
import os


class MapSerializer:
    @staticmethod
    def save_map(map_dir: str = "data/maps") -> Optional[Tuple[str, Optional[str]]]:
        try:
            if not os.path.exists(map_dir):
                os.makedirs(map_dir)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            map_path = os.path.join(map_dir, timestamp)
            os.makedirs(map_path, exist_ok=True)

            json_path = os.path.join(map_path, "map.json")
            with open(json_path, "w") as f:
                json.dump(GridMap.to_dict(), f, indent=2)

        except Exception as e:
            print("[MAP_SERIALIZER]: Error saving map:", e)
            return None

    @staticmethod
    def load_map(json_path: str) -> Optional["GridMap"]:
        try:
            with open(json_path, "r") as f:
                data = json.load(f)

            return GridMap.from_dict(data)
        except Exception as e:
            print("[MAP_SERIALIZER]: Error loading map:", e)
            return None
