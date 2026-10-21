import numpy as np
import heapq
import time
from typing import List, Optional
from utils.enviroment import UAVEnvironment
import matplotlib.pyplot as plt


class AStarPathfinder:
    def __init__(self, environment: UAVEnvironment, grid_step=2.0):
        self.env = environment
        self.grid_step = grid_step
        self.path = None
        self.visited_nodes = []
        self.track_history = True
        self.position_history = []
        self.search_time = 0

    def heuristic(self, point: np.ndarray) -> float:
        return np.linalg.norm(self.env.goal - point)

    def get_neighbors(self, point: np.ndarray, max_turns=8) -> List[np.ndarray]:
        neighbors = []
        directions = [
            (self.grid_step, 0),
            (-self.grid_step, 0),
            (0, self.grid_step),
            (0, -self.grid_step),
            (self.grid_step, self.grid_step),
            (self.grid_step, -self.grid_step),
            (-self.grid_step, self.grid_step),
            (-self.grid_step, -self.grid_step),
        ]

        for dx, dy in directions:
            new_point = point + np.array([dx, dy])

            if not self.env.is_collision(new_point) and not self.env.line_collision(
                point, new_point
            ):
                neighbors.append(new_point)

            # if self.env.is_collision(new_point):
            #     print("Va chạm tại:", new_point)
            #     continue

            # if self.env.line_collision(point, new_point):
            #     print("Đường đi bị chặn:", point, "->", new_point)
            #     continue

        return neighbors

    def find_path(self) -> bool:
        start_time = time.time()
        start = self.env.start.copy()
        goal = self.env.goal.copy()

        counter = 0
        open_set = [(0, counter, tuple(start), [start.copy()])]
        closed_set = set()
        g_scores = {tuple(start): 0}

        while open_set:
            f_score, _, current_tuple, path = heapq.heappop(open_set)
            current = np.array(current_tuple)

            if tuple(current) in closed_set:
                continue

            if np.linalg.norm(current - goal) < self.grid_step * 1.5:
                last_point = np.array(path[-1])

                if self.env.line_collision(last_point, goal):
                    if tuple(current) not in closed_set:
                        closed_set.add(tuple(current))
                        continue

                final_path = path.copy()
                distance = self.env.get_distance(last_point, goal)
                num_steps = max(2, int(distance / (self.grid_step / 2)))

                for t in np.linspace(0, 1, num_steps)[1:]:
                    intermediate = last_point * (1 - t) + goal * t
                    final_path.append(intermediate.copy())

                self.path = final_path
                self.visited_nodes = list(closed_set)
                self.search_time = time.time() - start_time
                return True

            closed_set.add(tuple(current))

            if self.track_history:
                self.position_history.append(
                    {
                        "iteration": len(self.position_history),
                        "closed_set": [np.array(c) for c in closed_set],
                        "open_set": [np.array(o[2]) for o in open_set],
                        "current_path": path,
                        "best_score": len(path),
                        "current": current.copy(),
                    }
                )

            for neighbor in self.get_neighbors(current):
                if tuple(neighbor) in closed_set:
                    continue

                new_g = g_scores[tuple(current)] + self.env.get_distance(
                    current, neighbor
                )

                if tuple(neighbor) not in g_scores or new_g < g_scores[tuple(neighbor)]:
                    g_scores[tuple(neighbor)] = new_g

                    h = self.heuristic(neighbor)

                    f = new_g + h

                    counter += 1
                    heapq.heappush(
                        open_set,
                        (f, counter, tuple(neighbor), path + [neighbor.copy()]),
                    )

        self.visited_nodes = list(closed_set)
        self.search_time = time.time() - start_time
        return False

    def get_path(self) -> Optional[List[np.ndarray]]:
        return self.path

    def animate_history(self):
        """Animate the search history step by step"""
        fig, ax = plt.subplots(figsize=(10, 10))

        for step in self.position_history:
            self.env.visualize(ax=ax, title="A* Track History")

            if len(step["closed_set"]) > 0:
                closed = np.array(step["closed_set"])
                ax.plot(closed[:, 0], closed[:, 1], "bo", markersize=3)

            if len(step["open_set"]) > 0:
                open_nodes = np.array(step["open_set"])
                ax.plot(open_nodes[:, 0], open_nodes[:, 1], "yo", markersize=3)

            c = step["current"]
            ax.plot(c[0], c[1], "ro", markersize=6)

            p = np.array(step["current_path"])
            ax.plot(p[:, 0], p[:, 1], "g-")

            plt.pause(0.03)

        plt.show()

    def get_statistics(self) -> dict:
        if self.path is None:
            return {
                "path_length": None,
                "num_waypoints": 0,
                "distance": 0,
                "visited_nodes": 0,
                "search_time": 0,
            }

        path = np.array(self.path)
        distance = float(
            sum(np.linalg.norm(path[i + 1] - path[i]) for i in range(len(path) - 1))
        )

        return {
            # "path": path,
            "path_length": len(self.path),
            "num_waypoints": len(self.path),
            "distance": round(distance, 2),
            "visited_nodes": len(self.visited_nodes),
            "search_time": round(self.search_time, 2),
        }


if __name__ == "__main__":
    env = UAVEnvironment()
    env.simple_map(num_obstacles=8, seed=42)
    env.set_start_goal((10, 10), (90, 90))

    astar = AStarPathfinder(env, grid_step=2)
    found = astar.find_path()

    # Animate search history
    # astar.animate_history()

    print("Tìm được đường:", found)
    if found:
        print(astar.get_statistics())
        # env.visualize(path=astar.get_path(), title="A* Result")
        # plt.show()
