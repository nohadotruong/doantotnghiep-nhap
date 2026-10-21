from __future__ import annotations

from dataclasses import dataclass

from evaluation.metrics import node_count, objective, path_length, path_smoothness
from planners.astar import AStarPlanner
from planners.hybrid import HybridPlanner
from planners.pso_optimizer import PSOOptimizer
from planners.pso_planner import PSOPlanner
from utils.grid_utils import Grid, Point


@dataclass
class ExperimentResult:
    name: str
    length: float
    smoothness: float
    nodes: int
    objective_value: float


def build_default_algorithms() -> dict[str, object]:
    return {
        "A*": AStarPlanner(True, True, False),
        "PSO": HybridPlanner(PSOPlanner(), PSOOptimizer()),
        "APSO": HybridPlanner(AStarPlanner(True, True, False), PSOOptimizer()),
        "HAPSO": HybridPlanner(AStarPlanner(True, True, True), PSOOptimizer()),
    }


def run_experiments(grid: Grid, start: Point, goal: Point) -> list[ExperimentResult]:
    results: list[ExperimentResult] = []
    for name, planner in build_default_algorithms().items():
        path = planner.plan(grid, start, goal)
        if not path:
            results.append(
                ExperimentResult(name, float("inf"), float("inf"), 0, float("inf"))
            )
            continue

        results.append(
            ExperimentResult(
                name=name,
                length=path_length(path),
                smoothness=path_smoothness(path),
                nodes=node_count(path),
                objective_value=objective(path, grid),
            )
        )
    return results
