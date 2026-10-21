from datetime import datetime
from typing import Optional, Tuple

import json
import os


class ResultSerializer:
    @staticmethod
    def save_result(
        result, grid_map, result_dir="data/results"
    ) -> Optional[Tuple[str, Optional[str]]]:
        try:
            if not result:
                return None

            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            result_path = os.path.join(result_dir, timestamp)
            os.makedirs(result_path, exist_ok=True)

            result_with_metadata = {
                **result,
                "timestamp": datetime.now().isoformat(),
                "grid": {
                    "width": grid_map.width,
                    "height": grid_map.height,
                    "start": grid_map.start,
                    "goal": grid_map.goal,
                },
            }

            json_path = os.path.join(result_path, "result.json")
            with open(json_path, "w") as f:
                json.dump(result_with_metadata, f, indent=2)

            image_path = None

            return (json_path, image_path)

        except Exception as e:
            print("[RESULT_SERIALIZER]: Error saving result:", e)
            return None
