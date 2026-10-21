import random
import math
from node.node import Node


class RRTPlanner:
    def __init__(
        self,
        environment,
        start,
        goal,
        step_size=5.0,
        max_iter=5000,
        goal_sample_rate=0.2,
    ):
        self.environment = environment
        self.start = Node(start[0], start[1])
        self.goal = Node(goal[0], goal[1])
        self.step_size = step_size
        self.max_iter = max_iter
        self.goal_sample_rate = goal_sample_rate
        self.tree = [self.start]

    def sample(self):
        if random.random() < self.goal_sample_rate:
            return self.goal

        x = random.uniform(0, self.environment.width)
        y = random.uniform(0, self.environment.height)

        return Node(x, y)

    def nearest(self, point):
        if not isinstance(point, Node):
            point = Node(point[0], point[1])

        nearest_node = self.tree[0]
        min_distance = nearest_node.distance_to(point)

        for node in self.tree[1:]:
            distance = node.distance_to(point)

            if distance < min_distance:
                min_distance = distance
                nearest_node = node

        return nearest_node

    def steer(self, from_node, to_point):
        if not isinstance(to_point, Node):
            to_point = Node(to_point[0], to_point[1])

        distance = from_node.distance_to(to_point)

        if distance < self.step_size:
            return Node(to_point.x, to_point.y, parent=from_node)

        dx = to_point.x - from_node.x
        dy = to_point.y - from_node.y

        length = (dx**2 + dy**2) ** 0.5
        dx = dx / length * self.step_size
        dy = dy / length * self.step_size

        new_x = from_node.x + dx
        new_y = from_node.y + dy

        return Node(new_x, new_y, parent=from_node)

    def plan(self):
        for iteration in range(self.max_iter):
            random_point = self.sample()
            nearest_node = self.nearest(random_point)
            new_node = self.steer(nearest_node, random_point)

            if not self.environment.is_collision(
                (nearest_node.x, nearest_node.y), (new_node.x, new_node.y)
            ):
                self.tree.append(new_node)

                if new_node.distance_to(self.goal) < self.step_size:
                    goal_node = Node(self.goal.x, self.goal.y, parent=new_node)

                    if not self.environment.is_collision(
                        (new_node.x, new_node.y), (goal_node.x, goal_node.y)
                    ):
                        self.tree.append(goal_node)

                        path = self._extract_path(goal_node)
                        print(
                            f"[RRT] Finding path successfully after {iteration + 1} iterations"
                        )
                        return path

        print(f"[RRT] Finding path failed after {self.max_iter} iterations")
        return None

    def _extract_path(self, node):
        path = []
        current = node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        path.reverse()
        return path


if __name__ == "__main__":
    from environment.environment import UAVEnvironment

    # obstacles = UAVEnvironment.generate_random_obstacles(
    #     width=100, height=100, num_obstacles=20
    # )
    # new_map = UAVEnvironment(100, 100, obstacles)
    # new_map.visualize()
    # new_map.save_map()

    uav_map = UAVEnvironment.load_map(
        r"D:\DEV\_Projects\TLU\DoAn\rrt-pso-find-path\maps\map_20260302_164324\config.json"
    )
    rrt_planner = RRTPlanner(uav_map, (0, 0), (100, 100))
    rrt_path = rrt_planner.plan()

    uav_map.visualize(rrt_path)
