from config.algo_config import (
    PRM_CONNECTION_RADIUS,
    PRM_MAX_CONNECTION_ATTEMPTS,
    PRM_N_SAMPLES,
)
from core.algorithms.base_planner import BasePlanner
from map.grid_map import GridMap

import heapq
import random


class PRMNode:
    def __init__(self, x: int, y: int, node_id: int) -> None:
        self.x = x
        self.y = y
        self.node_id = node_id
        self.neighbors: list[tuple[int, float]] = []

    def __lt__(self, other: "PRMNode") -> bool:
        return self.node_id < other.node_id


class PRM(BasePlanner):
    def __init__(
        self,
        grid_map: GridMap,
        n_samples: int = PRM_N_SAMPLES,
        connection_radius: float = PRM_CONNECTION_RADIUS,
        max_connection_attempts: int = PRM_MAX_CONNECTION_ATTEMPTS,
    ) -> None:
        self.grid_map: GridMap = grid_map
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None
        self.obstacles = self.grid_map.get_obstacles_as_centers()

        self.n_samples = n_samples
        self.connection_radius = connection_radius
        self.max_connection_attempts = max_connection_attempts

        self.roadmap: dict[int, PRMNode] = {}
        self.node_counter = 0
        self._roadmap_built = False

    def build_roadmap(self) -> None:
        if self._roadmap_built:
            return

        print(f"[PRM]: Building roadmap with {self.n_samples} samples...")
        self._build_roadmap()
        self._roadmap_built = True

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        self.start = start
        self.goal = goal

        if not self._validate_inputs():
            return None

        if start == goal:
            return [start]

        self.build_roadmap()

        print("[PRM]: Connecting start and goal to roadmap...")
        start_node = self._connect_point_to_roadmap(start)
        goal_node = self._connect_point_to_roadmap(goal)

        if start_node is None or goal_node is None:
            self._cleanup_query_nodes([start_node, goal_node])
            print("[PRM]: Failed to connect start or goal to roadmap")
            return None

        print("[PRM]: Searching for path...")
        path = self._dijkstra_search(start_node, goal_node)

        self._cleanup_query_nodes([start_node, goal_node])

        if path is None:
            print("[PRM]: No path found")
            return None

        print(f"[PRM]: Path found with {len(path)} waypoints")
        return path

    def _build_roadmap(self) -> None:
        self.roadmap.clear()
        self.node_counter = 0

        samples = self._generate_samples()

        for x, y in samples:
            node_id = self.node_counter
            self.roadmap[node_id] = PRMNode(x, y, node_id)
            self.node_counter += 1

        self._connect_roadmap_nodes()

    def _generate_samples(self) -> list[tuple[int, int]]:
        samples: list[tuple[int, int]] = []
        width = self.grid_map.width
        height = self.grid_map.height
        attempts = 0
        max_attempts = self.n_samples * self.max_connection_attempts

        while len(samples) < self.n_samples and attempts < max_attempts:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            attempts += 1

            if self._is_valid(x, y):
                samples.append((x, y))

        print(f"[PRM]: Generated {len(samples)} valid samples")
        return samples

    def _connect_roadmap_nodes(self) -> None:
        node_ids = list(self.roadmap.keys())

        for node_id in node_ids:
            node = self.roadmap[node_id]
            nearest_ids = self._find_nearest_nodes(node_id, self.connection_radius)

            for nearest_id in nearest_ids:
                if nearest_id != node_id:
                    nearest_node = self.roadmap[nearest_id]
                    if not self._segment_has_collision(
                        (node.x, node.y), (nearest_node.x, nearest_node.y)
                    ):
                        distance = self._euclidean_distance(
                            (node.x, node.y), (nearest_node.x, nearest_node.y)
                        )
                        node.neighbors.append((nearest_id, distance))

        edges = sum(len(node.neighbors) for node in self.roadmap.values())
        print(f"[PRM]: Connected roadmap with {edges} edges")

    def _find_nearest_nodes(self, node_id: int, radius: float) -> list[int]:
        node = self.roadmap[node_id]
        nearest_ids: list[int] = []

        for other_id, other_node in self.roadmap.items():
            if other_id != node_id:
                distance = self._euclidean_distance(
                    (node.x, node.y), (other_node.x, other_node.y)
                )
                if distance <= radius:
                    nearest_ids.append(other_id)

        return nearest_ids

    def _connect_point_to_roadmap(self, point: tuple[int, int]) -> PRMNode | None:
        node_id = self.node_counter
        new_node = PRMNode(point[0], point[1], node_id)

        connected = False
        for existing_id, existing_node in self.roadmap.items():
            distance = self._euclidean_distance(
                (new_node.x, new_node.y), (existing_node.x, existing_node.y)
            )

            if distance <= self.connection_radius:
                if not self._segment_has_collision(
                    (new_node.x, new_node.y), (existing_node.x, existing_node.y)
                ):
                    new_node.neighbors.append((existing_id, distance))
                    existing_node.neighbors.append((node_id, distance))
                    connected = True

        if not connected:
            return None

        self.roadmap[node_id] = new_node
        self.node_counter += 1
        return new_node

    def _cleanup_query_nodes(self, nodes: list[PRMNode | None]) -> None:
        for node in nodes:
            if node is None:
                continue

            current_node = self.roadmap.pop(node.node_id, None)
            if current_node is None:
                continue

            for neighbor_id, _ in current_node.neighbors:
                neighbor = self.roadmap.get(neighbor_id)
                if neighbor is None:
                    continue

                neighbor.neighbors = [
                    (existing_neighbor_id, distance)
                    for existing_neighbor_id, distance in neighbor.neighbors
                    if existing_neighbor_id != current_node.node_id
                ]

    def _dijkstra_search(
        self, start_node: PRMNode, goal_node: PRMNode
    ) -> list[tuple[int, int]] | None:
        if start_node.node_id == goal_node.node_id:
            return [(start_node.x, start_node.y)]

        distances: dict[int, float] = {
            node_id: float("inf") for node_id in self.roadmap
        }
        distances[start_node.node_id] = 0
        parent: dict[int, int | None] = {node_id: None for node_id in self.roadmap}

        pq: list[tuple[float, int]] = [(0, start_node.node_id)]

        while pq:
            current_dist, current_id = heapq.heappop(pq)

            if current_dist > distances[current_id]:
                continue

            if current_id == goal_node.node_id:
                return self._reconstruct_path(
                    start_node.node_id, goal_node.node_id, parent
                )

            current_node = self.roadmap[current_id]

            for neighbor_id, edge_distance in current_node.neighbors:
                new_dist = distances[current_id] + edge_distance

                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    parent[neighbor_id] = current_id
                    heapq.heappush(pq, (new_dist, neighbor_id))

        return None

    def _reconstruct_path(
        self, start_id: int, goal_id: int, parent: dict[int, int | None]
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current_id = goal_id

        while current_id is not None:
            node = self.roadmap[current_id]
            path.append((node.x, node.y))
            current_id = parent[current_id]

        path.reverse()
        return path
