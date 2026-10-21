from algorithms_new.base import BasePlanner
from algorithms_new.pso_optimizer import PSOOptimizer
from environment.grid_map import GridMap
from typing import List, Optional, Tuple


class HybridPlanner(BasePlanner):
    def __init__(
        self,
        planner: BasePlanner,
        optimizer: PSOOptimizer,
    ) -> None:
        super().__init__(planner.grid)
        self.planner = planner
        self.optimizer = optimizer

    def plan(self) -> Optional[List[Tuple[int, int]]]:
        path = self.planner.plan()

        if path is None or len(path) < 2:
            return path

        optimized_path = self.optimizer.optimize(path)

        return optimized_path if optimized_path is not None else path
