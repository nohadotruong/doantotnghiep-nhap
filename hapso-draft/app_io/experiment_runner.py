"""Stub experiment runner after refactoring.

Algorithm implementations have been removed.
"""

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
    """Result from running a single path planning algorithm.

    Attributes:
        name: Algorithm name
        length: Total path length
        smoothness: Path smoothness (total rotation)
        nodes: Number of waypoints
        objective_value: Combined fitness score
    """

    name: str
    length: float
    smoothness: float
    nodes: int
    objective_value: float


def build_default_algorithms(
    config: dict[str, float | int] | None = None,
) -> dict[str, object]:
    """Build default algorithm instances with configuration.

    After refactoring: All planners return empty paths.

    Args:
        config: Configuration dict with keys like 'planner_particles', etc.

    Returns:
        Dictionary mapping algorithm names to planner instances
    """
    cfg = config or {}
    planner_particles = int(cfg.get("planner_particles", 30))
    planner_iterations = int(cfg.get("planner_iterations", 60))
    planner_waypoints = int(cfg.get("planner_waypoints", 6))
    optimizer_particles = int(cfg.get("optimizer_particles", 24))
    optimizer_iterations = int(cfg.get("optimizer_iterations", 40))

    return {
        "A*": AStarPlanner(True, True, False),
        "PSO": HybridPlanner(
            PSOPlanner(
                n_particles=planner_particles,
                n_iterations=planner_iterations,
                n_waypoints=planner_waypoints,
            ),
            PSOOptimizer(
                n_particles=optimizer_particles,
                n_iterations=optimizer_iterations,
            ),
        ),
        "APSO": HybridPlanner(
            AStarPlanner(True, True, False),
            PSOOptimizer(
                n_particles=optimizer_particles,
                n_iterations=optimizer_iterations,
            ),
        ),
        "HAPSO": HybridPlanner(
            AStarPlanner(True, True, True),
            PSOOptimizer(
                n_particles=optimizer_particles,
                n_iterations=optimizer_iterations,
            ),
        ),
    }


def run_experiments(
    grid: Grid,
    start: Point,
    goal: Point,
    config: dict[str, float | int] | None = None,
) -> list[ExperimentResult]:
    """Run all algorithms and collect results.

    After refactoring: All algorithms return empty paths and default results.

    Args:
        grid: 2D grid
        start: Starting position
        goal: Goal position
        config: Configuration dict

    Returns:
        List of ExperimentResult for each algorithm
    """
    results: list[ExperimentResult] = []
    for name, planner in build_default_algorithms(config).items():
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
