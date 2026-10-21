"""
Planning API - Single contract between app layer and planning layer.

This module defines the complete interface that the app layer uses to interact
with the path planning algorithms. All types are concrete dataclasses with 100%
explicit type hints (zero 'type Any').

Key Design Principles:
- planning/api.py is the ONLY entry point from app to planning
- All request/response types are concrete dataclasses
- No pygame imports (planning layer is independent)
- Factory pattern handles all 4 algorithms (A*, PSO, APSO, HAPSO)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
import time


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


@dataclass
class Point:
    """2D coordinate with unpacking support."""

    x: float
    y: float

    def __iter__(self):
        """Allow unpacking: x, y = point"""
        return iter((self.x, self.y))


@dataclass
class Grid:
    """Environment grid definition with obstacles."""

    width: int
    height: int
    obstacles: List[Tuple[int, int]] = field(default_factory=list)

    def is_obstacle(self, x: int, y: int) -> bool:
        """Check if cell is obstacle."""
        return (x, y) in self.obstacles

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Check if cell is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height


@dataclass
class Metrics:
    """Path evaluation metrics."""

    path_length: float
    waypoint_count: int
    total_rotation: float
    computation_time: float
    path_valid: bool
    objective_value: float
    turn_angles: List[float] = field(default_factory=list)


@dataclass
class PlanRequest:
    """Request to plan a single path."""

    # Grid and positions
    grid: Grid
    start: Point
    goal: Point

    # Algorithm type
    algorithm: "AlgorithmType"

    # A* options
    astar_prune_collinear: bool = True
    astar_prune_transitions: bool = True
    astar_avoid_corner_cutting: bool = False

    # PSO options
    pso_particles: int = 50
    pso_iterations: int = 120
    pso_inertia_strategy: "InertiaWeightStrategy" = "InertiaWeightStrategy.LDIW"
    pso_cognitive_coeff: float = 1.4
    pso_social_coeff: float = 1.6
    pso_max_velocity: float = 2.5


@dataclass
class PlanResult:
    """Result of a single path planning attempt."""

    success: bool
    path: List[Point] = field(default_factory=list)
    metrics: Optional[Metrics] = None
    error_message: str = ""


@dataclass
class ExperimentConfig:
    """Configuration for multi-algorithm experiment."""

    grid: Grid
    start: Point
    goal: Point

    # Which algorithms to run
    run_astar: bool = True
    run_pso: bool = True
    run_apso: bool = True
    run_hapso: bool = True

    # Algorithm parameters (same for all)
    astar_prune_collinear: bool = True
    astar_prune_transitions: bool = True
    astar_avoid_corner_cutting: bool = False

    pso_particles: int = 50
    pso_iterations: int = 120
    pso_inertia_strategy: "InertiaWeightStrategy" = "InertiaWeightStrategy.LDIW"


@dataclass
class ExperimentResult:
    """Results from multi-algorithm experiment."""

    results: dict[str, PlanResult] = field(
        default_factory=dict
    )  # algorithm_name -> PlanResult
    best_algorithm: Optional[str] = None
    best_path_length: Optional[float] = None


# ============================================================================
# ENUMS
# ============================================================================


class AlgorithmType(Enum):
    """Available pathfinding algorithms."""

    ASTAR = "astar"
    PSO = "pso"
    APSO = "apso"
    HAPSO = "hapso"


class InertiaWeightStrategy(Enum):
    """PSO inertia weight strategies."""

    LDIW = "ldiw"  # Linear Decreasing Inertia Weight
    NDIW = "ndiw"  # Nonlinear Decreasing Inertia Weight
    AIW = "aiw"  # Adaptive Inertia Weight
    SIW = "siw"  # Stochastic Inertia Weight


# ============================================================================
# PUBLIC API
# ============================================================================


def run_plan(request: PlanRequest) -> PlanResult:
    """
    Execute single path planning with specified algorithm.

    Args:
        request: PlanRequest with grid, start/goal, algorithm type, and parameters

    Returns:
        PlanResult with success status, path (if found), metrics, and error message

    Example:
        >>> grid = Grid(width=20, height=20, obstacles=[(10, 10), (10, 11)])
        >>> start = Point(x=2, y=2)
        >>> goal = Point(x=18, y=18)
        >>> request = PlanRequest(
        ...     grid=grid,
        ...     start=start,
        ...     goal=goal,
        ...     algorithm=AlgorithmType.HAPSO,
        ...     astar_avoid_corner_cutting=True,
        ...     pso_particles=50
        ... )
        >>> result = run_plan(request)
        >>> if result.success:
        ...     print(f"Path found: {len(result.path)} waypoints")
        ...     print(f"Length: {result.metrics.path_length:.2f}")
    """
    # Validate request
    _validate_request(request)

    t_start = time.time()

    try:
        # Create appropriate planner
        planner = _create_planner(request)

        # Execute planning
        path_coords = planner.plan()

        t_end = time.time()
        computation_time = t_end - t_start

        if path_coords is None:
            return PlanResult(
                success=False,
                error_message=f"Failed to find path with {request.algorithm.value}",
            )

        # Convert to Point objects
        path: List[Point] = [Point(x=x, y=y) for x, y in path_coords]

        # Calculate metrics
        metrics = get_metrics(path, request.grid, computation_time)

        return PlanResult(success=True, path=path, metrics=metrics)

    except Exception as e:
        t_end = time.time()
        return PlanResult(success=False, error_message=f"Planning error: {str(e)}")


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    """
    Run all configured algorithms and return comparative results.

    Args:
        config: ExperimentConfig specifying which algorithms to run and parameters

    Returns:
        ExperimentResult with results dict (algorithm_name -> PlanResult)
        and best_algorithm/best_path_length

    Example:
        >>> config = ExperimentConfig(
        ...     grid=grid,
        ...     start=start,
        ...     goal=goal,
        ...     run_astar=True,
        ...     run_pso=True,
        ...     run_apso=True,
        ...     run_hapso=True
        ... )
        >>> result = run_experiment(config)
        >>> for algo_name, plan_result in result.results.items():
        ...     if plan_result.success:
        ...         print(f"{algo_name}: {plan_result.metrics.path_length:.2f}")
    """
    results: dict[str, PlanResult] = {}
    best_length = float("inf")
    best_algo = None

    # Run A*
    if config.run_astar:
        request = PlanRequest(
            grid=config.grid,
            start=config.start,
            goal=config.goal,
            algorithm=AlgorithmType.ASTAR,
            astar_prune_collinear=config.astar_prune_collinear,
            astar_prune_transitions=config.astar_prune_transitions,
            astar_avoid_corner_cutting=config.astar_avoid_corner_cutting,
        )
        result = run_plan(request)
        results["A*"] = result
        if result.success and result.metrics.path_length < best_length:
            best_length = result.metrics.path_length
            best_algo = "A*"

    # Run PSO
    if config.run_pso:
        request = PlanRequest(
            grid=config.grid,
            start=config.start,
            goal=config.goal,
            algorithm=AlgorithmType.PSO,
            pso_particles=config.pso_particles,
            pso_iterations=config.pso_iterations,
            pso_inertia_strategy=config.pso_inertia_strategy,
        )
        result = run_plan(request)
        results["PSO"] = result
        if result.success and result.metrics.path_length < best_length:
            best_length = result.metrics.path_length
            best_algo = "PSO"

    # Run APSO
    if config.run_apso:
        request = PlanRequest(
            grid=config.grid,
            start=config.start,
            goal=config.goal,
            algorithm=AlgorithmType.APSO,
            astar_prune_collinear=config.astar_prune_collinear,
            astar_prune_transitions=config.astar_prune_transitions,
            astar_avoid_corner_cutting=False,  # APSO: no corner cutting guard
            pso_particles=config.pso_particles,
            pso_iterations=config.pso_iterations,
        )
        result = run_plan(request)
        results["APSO"] = result
        if result.success and result.metrics.path_length < best_length:
            best_length = result.metrics.path_length
            best_algo = "APSO"

    # Run HAPSO
    if config.run_hapso:
        request = PlanRequest(
            grid=config.grid,
            start=config.start,
            goal=config.goal,
            algorithm=AlgorithmType.HAPSO,
            astar_prune_collinear=config.astar_prune_collinear,
            astar_prune_transitions=config.astar_prune_transitions,
            astar_avoid_corner_cutting=True,  # HAPSO: enforced corner cutting guard
            pso_particles=config.pso_particles,
            pso_iterations=config.pso_iterations,
        )
        result = run_plan(request)
        results["HAPSO"] = result
        if result.success and result.metrics.path_length < best_length:
            best_length = result.metrics.path_length
            best_algo = "HAPSO"

    return ExperimentResult(
        results=results,
        best_algorithm=best_algo,
        best_path_length=best_length if best_algo else None,
    )


def get_metrics(path: List[Point], grid: Grid, computation_time: float) -> Metrics:
    """
    Calculate evaluation metrics for a path.

    Args:
        path: List of waypoints
        grid: Grid environment
        computation_time: Time taken to compute path (seconds)

    Returns:
        Metrics dataclass with all evaluation metrics
    """
    if not path or len(path) < 2:
        return Metrics(
            path_length=0,
            waypoint_count=len(path),
            total_rotation=0,
            computation_time=computation_time,
            path_valid=False,
            objective_value=float("inf"),
            turn_angles=[],
        )

    # Calculate path length
    path_length = 0.0
    for i in range(len(path) - 1):
        dx = path[i + 1].x - path[i].x
        dy = path[i + 1].y - path[i].y
        path_length += (dx**2 + dy**2) ** 0.5

    # Calculate turn angles
    turn_angles: List[float] = []
    total_rotation = 0.0

    for i in range(1, len(path) - 1):
        # Vector from i-1 to i
        v1_x = path[i].x - path[i - 1].x
        v1_y = path[i].y - path[i - 1].y
        len1 = (v1_x**2 + v1_y**2) ** 0.5

        # Vector from i to i+1
        v2_x = path[i + 1].x - path[i].x
        v2_y = path[i + 1].y - path[i].y
        len2 = (v2_x**2 + v2_y**2) ** 0.5

        if len1 > 0 and len2 > 0:
            # Dot product for angle
            dot = v1_x * v2_x + v1_y * v2_y
            det = v1_x * v2_y - v1_y * v2_x
            angle = abs(__import__("math").atan2(det, dot))
            turn_angles.append(angle)
            total_rotation += angle

    # Check path validity (no collisions)
    path_valid = _is_path_valid(path, grid)

    # Objective value: weighted combination
    objective_value = path_length + len(path) * 0.2 + total_rotation + computation_time

    return Metrics(
        path_length=path_length,
        waypoint_count=len(path),
        total_rotation=total_rotation,
        computation_time=computation_time,
        path_valid=path_valid,
        objective_value=objective_value,
        turn_angles=turn_angles,
    )


# ============================================================================
# INTERNAL HELPERS
# ============================================================================


def _validate_request(request: PlanRequest) -> None:
    """Validate PlanRequest before processing."""
    if not isinstance(request.grid, Grid):
        raise ValueError("request.grid must be Grid instance")

    if not isinstance(request.start, Point):
        raise ValueError("request.start must be Point instance")

    if not isinstance(request.goal, Point):
        raise ValueError("request.goal must be Point instance")

    if not isinstance(request.algorithm, AlgorithmType):
        raise ValueError("request.algorithm must be AlgorithmType enum")

    # Check start/goal in bounds
    if not request.grid.is_in_bounds(int(request.start.x), int(request.start.y)):
        raise ValueError("Start position out of grid bounds")

    if not request.grid.is_in_bounds(int(request.goal.x), int(request.goal.y)):
        raise ValueError("Goal position out of grid bounds")

    # Check start/goal not on obstacles
    if request.grid.is_obstacle(int(request.start.x), int(request.start.y)):
        raise ValueError("Start position on obstacle")

    if request.grid.is_obstacle(int(request.goal.x), int(request.goal.y)):
        raise ValueError("Goal position on obstacle")


def _create_planner(request: PlanRequest):
    """
    Factory: Create appropriate planner based on algorithm type.

    Returns planner instance with plan() method.
    """
    # This is a placeholder - actual implementation will import planners
    # from planning.core with lazy imports to avoid circular dependencies

    if request.algorithm == AlgorithmType.ASTAR:
        from planning.core.astar import AStarPlanner

        return AStarPlanner(
            grid=request.grid,
            start=request.start,
            goal=request.goal,
            prune_collinear=request.astar_prune_collinear,
            prune_transitions=request.astar_prune_transitions,
            avoid_corner_cutting=request.astar_avoid_corner_cutting,
        )

    elif request.algorithm == AlgorithmType.PSO:
        from planning.core.pso import PSOPlanner

        return PSOPlanner(
            grid=request.grid,
            start=request.start,
            goal=request.goal,
            num_particles=request.pso_particles,
            max_iterations=request.pso_iterations,
        )

    elif request.algorithm == AlgorithmType.APSO:
        from planning.core.apso import APSOPlanner

        return APSOPlanner(
            grid=request.grid,
            start=request.start,
            goal=request.goal,
            astar_prune_collinear=request.astar_prune_collinear,
            astar_prune_transitions=request.astar_prune_transitions,
            astar_avoid_corner_cutting=False,
            pso_particles=request.pso_particles,
            pso_iterations=request.pso_iterations,
        )

    elif request.algorithm == AlgorithmType.HAPSO:
        from planning.core.hapso import HAPSOPlanner

        return HAPSOPlanner(
            grid=request.grid,
            start=request.start,
            goal=request.goal,
            astar_prune_collinear=request.astar_prune_collinear,
            astar_prune_transitions=request.astar_prune_transitions,
            astar_avoid_corner_cutting=True,
            pso_particles=request.pso_particles,
            pso_iterations=request.pso_iterations,
        )

    else:
        raise ValueError(f"Unknown algorithm: {request.algorithm}")


def _is_path_valid(path: List[Point], grid: Grid) -> bool:
    """Check if path collides with any obstacles."""
    if not path:
        return False

    for point in path:
        if grid.is_obstacle(int(point.x), int(point.y)):
            return False

    return True


__all__ = [
    # Types
    "Point",
    "Grid",
    "Metrics",
    "PlanRequest",
    "PlanResult",
    "ExperimentConfig",
    "ExperimentResult",
    # Enums
    "AlgorithmType",
    "InertiaWeightStrategy",
    # Public API
    "run_plan",
    "run_experiment",
    "get_metrics",
]
