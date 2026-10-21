from datetime import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import random
from utils import point_in_rectangle, line_rectangle_collision, path_length


class UAVEnvironment:
    def __init__(self, width, height, obstacles=None):
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles else []

    def is_inside_obstacle(self, x, y):
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return True

        for ox, oy, ow, oh in self.obstacles:
            if point_in_rectangle(x, y, ox, oy, ow, oh):
                return True

        return False

    def is_collision(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        if self.is_inside_obstacle(x1, y1) or self.is_inside_obstacle(x2, y2):
            return True

        for ox, oy, ow, oh in self.obstacles:
            if line_rectangle_collision(x1, y1, x2, y2, ox, oy, ow, oh):
                return True

        return False

    @staticmethod
    def generate_random_obstacles(
        width, height, num_obstacles=5, min_size=5, max_size=20, seed=None
    ):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        obstacles = []
        for _ in range(num_obstacles):
            x = random.uniform(0, max(0, width - min_size))
            y = random.uniform(0, max(0, height - min_size))

            w = random.uniform(min_size, max_size)
            h = random.uniform(min_size, max_size)

            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = min(w, width - x)
            h = min(h, height - y)

            obstacles.append((x, y, w, h))

        return obstacles

    def visualize(self, path=None, title="Map", show_goal=None):
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(title)

        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle(
                (ox, oy),
                ow,
                oh,
                linewidth=2,
                edgecolor="red",
                facecolor="red",
                alpha=0.5,
            )
            ax.add_patch(rect)

        if path is not None and len(path) > 0:
            path = np.array(path)

            ax.plot(path[:, 0], path[:, 1], "b-", linewidth=2, label="Path")
            ax.plot(path[0, 0], path[0, 1], "go", markersize=10, label="Start")
            ax.plot(path[-1, 0], path[-1, 1], "r*", markersize=15, label="Goal")
            ax.legend()
        elif show_goal is not None:
            ax.plot(show_goal[0], show_goal[1], "r*", markersize=15, label="Goal")
            ax.legend()

        plt.tight_layout()
        plt.show()

    def visualize_multiple_paths(self, paths_dict, title="Map"):
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(title)

        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle(
                (ox, oy),
                ow,
                oh,
                linewidth=2,
                edgecolor="red",
                facecolor="red",
                alpha=0.5,
            )
            ax.add_patch(rect)

        colors = ["blue", "green", "orange", "purple", "brown"]

        for idx, (name, path) in enumerate(paths_dict.items()):
            if path is not None and len(path) > 0:
                path = np.array(path)
                color = colors[idx % len(colors)]
                length = path_length(path)
                ax.plot(
                    path[:, 0],
                    path[:, 1],
                    color=color,
                    linewidth=2,
                    label=f"{name} (L={length:.2f})",
                )

                if idx == 0:
                    ax.plot(path[0, 0], path[0, 1], "go", markersize=10, label="Start")

        last_path = list(paths_dict.values())[-1]
        if last_path is not None and len(last_path) > 0:
            last_path = np.array(last_path)
            ax.plot(
                last_path[-1, 0], last_path[-1, 1], "r*", markersize=15, label="Goal"
            )

        ax.legend()
        plt.tight_layout()
        plt.show()

    def save_map(self, map_name="map"):
        maps_dir = "maps"
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join(maps_dir, f"{map_name}_{timestamp}")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        config = {
            "name": map_name,
            "timestamp": timestamp,
            "width": self.width,
            "height": self.height,
            "obstacles": self.obstacles,
        }

        json_path = os.path.join(save_dir, "config.json")
        with open(json_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"[SAVE] JSON config: {json_path}")

        fig, ax = plt.subplots(figsize=(10, 10))

        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Map: {map_name}")

        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle(
                (ox, oy),
                ow,
                oh,
                linewidth=2,
                edgecolor="red",
                facecolor="red",
                alpha=0.5,
            )
            ax.add_patch(rect)

        ax.plot(0, 0, "go", markersize=10, label="Origin")
        ax.legend()
        plt.tight_layout()

        image_path = os.path.join(save_dir, "map.png")
        fig.savefig(image_path, dpi=100, bbox_inches="tight")
        plt.close(fig)

        print(f"[SAVE] Map image: {image_path}")
        print(f"[SAVE] Map saved to: {save_dir}")

        return save_dir

    @staticmethod
    def load_map(map_path):
        if map_path.endswith("config.json"):
            json_path = map_path
            map_dir = os.path.dirname(map_path)
        else:
            map_dir = map_path
            json_path = os.path.join(map_dir, "config.json")

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Config file not found: {json_path}")

        with open(json_path, "r") as f:
            config = json.load(f)

        width = config.get("width")
        height = config.get("height")
        obstacles = config.get("obstacles", [])

        obstacles = [tuple(obs) for obs in obstacles]

        env = UAVEnvironment(width, height, obstacles)

        print(f"[LOAD] Map loaded from: {map_dir}")
        print(f"[LOAD] Width: {width}, Height: {height}")
        print(f"[LOAD] Obstacles: {len(obstacles)}")

        return env

    def get_map_info(self):
        return {
            "width": self.width,
            "height": self.height,
            "num_obstacles": len(self.obstacles),
            "obstacle_details": self.obstacles,
        }


if __name__ == "__main__":
    # obstacles = UAVEnvironment.generate_random_obstacles(
    #     width=100, height=100, num_obstacles=10
    # )
    # new_map = UAVEnvironment(100, 100, obstacles)
    # new_map.save_map()

    loaded_map = UAVEnvironment.load_map(
        r"D:\DEV\_Projects\TLU\DoAn\rrt-pso-find-path\maps\map_20260302_162124\config.json"
    )
    print(loaded_map.obstacles)
    # loaded_map.visualize()
