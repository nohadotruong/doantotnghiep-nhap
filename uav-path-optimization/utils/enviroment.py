import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from typing import Tuple


class UAVEnvironment:
    def __init__(self, width=100, height=100, grid_size=1, num_obstacles=0):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.start = None
        self.goal = None
        self.obstacles = []

        if num_obstacles > 0:
            self.simple_map(num_obstacles=num_obstacles)

    def add_rectangular_obstacle(self, x, y, width, height):
        self.obstacles.append(
            {"type": "rectangle", "x": x, "y": y, "width": width, "height": height}
        )

    def add_circular_obstacle(self, x, y, radius):
        self.obstacles.append(
            {
                "type": "circle",
                "x": x,
                "y": y,
                "radius": radius,
            }
        )

    def set_start_goal(self, start: Tuple[float, float], goal: Tuple[float, float]):
        self.start = np.array(start)
        self.goal = np.array(goal)

    def simple_map(self, num_obstacles=5, seed=None):
        if seed is not None:
            np.random.seed(seed)

        self.obstacles = []

        for i in range(num_obstacles):
            obstacle_type = np.random.choice(["rectangle", "circle"], p=[0.6, 0.4])

            if obstacle_type == "rectangle":
                x = np.random.uniform(10, self.width * 0.7)
                y = np.random.uniform(10, self.height * 0.7)
                w = np.random.uniform(10, 25)
                h = np.random.uniform(8, 20)

                self.add_rectangular_obstacle(x, y, w, h)

            elif obstacle_type == "circle":
                x = np.random.uniform(15, self.width * 0.7)
                y = np.random.uniform(15, self.height * 0.7)
                r = np.random.uniform(5, 12)

                self.add_circular_obstacle(x, y, r)

    def is_collision(self, point: np.ndarray, safety_radius=1.0) -> bool:
        x, y = point[0], point[1]

        if x < 0 or x > self.width or y < 0 or y > self.height:
            return True

        for obstacle in self.obstacles:
            if obstacle["type"] == "rectangle":
                rect_x = obstacle["x"]
                rect_y = obstacle["y"]
                rect_w = obstacle["width"]
                rect_h = obstacle["height"]

                closest_x = np.clip(x, rect_x, rect_x + rect_w)
                closest_y = np.clip(y, rect_y, rect_y + rect_h)

                distance = np.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)
                if distance < safety_radius:
                    return True

            elif obstacle["type"] == "circle":
                center = np.array([obstacle["x"], obstacle["y"]])
                distance = np.linalg.norm(point - center)
                if distance < obstacle["radius"] + safety_radius:
                    return True

        return False

    def line_collision(
        self, point1: np.ndarray, point2: np.ndarray, num_checks=20, safety_radius=1.0
    ) -> bool:
        for t in np.linspace(0, 1, num_checks):
            point = point1 * (1 - t) + point2 * t
            if self.is_collision(point, safety_radius):
                return True

        return False

    def get_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        return np.linalg.norm(point2 - point1)

    def visualize(self, path=None, title="UAV Environment", ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.figure

        ax.clear()

        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(title)

        for obstacle in self.obstacles:
            if obstacle["type"] == "rectangle":
                rect = Rectangle(
                    (obstacle["x"], obstacle["y"]),
                    obstacle["width"],
                    obstacle["height"],
                    fill=True,
                    facecolor="red",
                    edgecolor="darkred",
                    alpha=0.7,
                    linewidth=2,
                )
                ax.add_patch(rect)

            elif obstacle["type"] == "circle":
                circle = Circle(
                    (obstacle["x"], obstacle["y"]),
                    obstacle["radius"],
                    fill=True,
                    facecolor="red",
                    edgecolor="darkred",
                    alpha=0.7,
                    linewidth=2,
                )
                ax.add_patch(circle)

        if self.start is not None:
            ax.plot(
                self.start[0],
                self.start[1],
                "go",
                markersize=15,
                label="Start",
                zorder=5,
            )

        if self.goal is not None:
            ax.plot(
                self.goal[0], self.goal[1], "b*", markersize=20, label="Goal", zorder=5
            )

        if path is not None and len(path) > 0:
            path = np.array(path)
            ax.plot(path[:, 0], path[:, 1], "b-", linewidth=2, label="Path", alpha=0.7)
            ax.plot(path[:, 0], path[:, 1], "bo", markersize=4, alpha=0.5)

        ax.legend(loc="best")
        return fig, ax


if __name__ == "__main__":
    env = UAVEnvironment(width=100, height=100)

    env.simple_map(num_obstacles=9, seed=42)
    env.set_start_goal((5, 5), (95, 95))

    path = [(5, 5), (95, 95)]

    env.visualize(path, title="Simple Map")
    plt.show()
