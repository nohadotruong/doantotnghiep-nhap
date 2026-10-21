
from core.algorithms.astar import AStar
from core.algorithms.base_planner import Planner
from core.algorithms.pso_optimizer import PSOptimizer
from core.utils.path_smoother import PathSmoother
from map.grid_map import GridMap
from typing import Optional


class HAPSO(Planner):

    def __init__(self, grid_map: GridMap) -> None:
        self.grid_map: GridMap = grid_map
        self.start: Optional[tuple[int, int]] = None
        self.goal: Optional[tuple[int, int]] = None
        self.obstacles: list[tuple[int, int]] = []

        # A* with fixed smoothing policy from config
        self.astar = AStar(
            grid_map,
            remove_redundant=True,
            remove_transitive=True,
            avoid_corner_cutting=False,
        )

        # Segment optimizer with TVAC enabled
        self.optimizer = PSOptimizer(grid_map, use_tvac=True)

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> Optional[list[tuple[int, int]]]:
        self.start = start
        self.goal = goal
        self.obstacles = self.grid_map.get_obstacles()

        # Get A* path
        a_star_path = self.astar.find_path(start, goal)

        if not a_star_path:
            return None

        # Remove collinear waypoints
        key_nodes = PathSmoother._remove_collinear(a_star_path)

        if len(key_nodes) < 2:
            return a_star_path

        # Optimize each segment with TVAC
        optimized_path = self._optimize_segments(key_nodes)

        return optimized_path if optimized_path else a_star_path

    def _optimize_segments(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(path) < 3:
            return path

        optimized = [path[0]]

        for i in range(0, len(path) - 2):
            anchor_start = optimized[-1]
            anchor_end = path[i + 2]
            original_waypoint = path[i + 1]

            # Optimize segment (TVAC enabled)
            best_mid = self.optimizer.optimize_segment(anchor_start, anchor_end)

            # Check collision on optimized waypoint
            collision_detected = self._segment_has_collision(
                anchor_start, best_mid
            ) or self._segment_has_collision(best_mid, anchor_end)

            if not collision_detected:
                # Check clearance vs original
                best_clearance = min(
                    Planner._min_distance_segment_to_obstacles(
                        anchor_start, best_mid, self.grid_map.get_obstacles_as_centers()
                    ),
                    Planner._min_distance_segment_to_obstacles(
                        best_mid, anchor_end, self.grid_map.get_obstacles_as_centers()
                    ),
                )
                orig_clearance = min(
                    Planner._min_distance_segment_to_obstacles(
                        anchor_start,
                        original_waypoint,
                        self.grid_map.get_obstacles_as_centers(),
                    ),
                    Planner._min_distance_segment_to_obstacles(
                        original_waypoint,
                        anchor_end,
                        self.grid_map.get_obstacles_as_centers(),
                    ),
                )

                # Reject if worse clearance
                if best_clearance < orig_clearance:
                    best_mid = original_waypoint
            else:
                # Collision detected, keep original
                best_mid = original_waypoint

            optimized.append(best_mid)

        optimized.append(path[-1])

        return optimized
