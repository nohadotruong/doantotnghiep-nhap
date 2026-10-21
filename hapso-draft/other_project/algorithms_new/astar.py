from algorithms.astar import Astar
from algorithms_new.base import BasePlanner
from environment.grid_map import GridMap
from typing import List, Optional, Tuple


class AStarPlanner(BasePlanner):
    def __init__(
        self,
        grid: GridMap,
        remove_redundant_points: bool = False,
        remove_redundant_waypoints: bool = False,
        corner_collision_check: bool = False,
    ) -> None:
        super().__init__(grid)
        self.remove_redundant_points = remove_redundant_points
        self.remove_redundant_waypoints = remove_redundant_waypoints
        self.corner_collision_check = corner_collision_check
        self.astar = Astar(
            grid,
            prune_collinear=remove_redundant_points,
            prune_transitions=remove_redundant_waypoints,
            avoid_corner_cutting=corner_collision_check,
        )

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        return self.astar.plan()
