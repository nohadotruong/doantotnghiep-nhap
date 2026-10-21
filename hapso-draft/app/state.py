"""
Application State - Unified app state storage (pure dataclass).

This module defines AppState - a pure dataclass that holds all application state
without importing anything from the planning layer. It acts as a bridge between
the UI and the planning/api.py contract.

Key Design:
- NO imports from planning layer
- Pure data holder (no business logic)
- Converts between UI types and planning API types at boundaries
- Compatible with pygame, JSON serialization, etc.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class AppState:
    """Unified application state."""

    # ========================================================================
    # Window & Display Configuration
    # ========================================================================
    window_width: int = 900
    window_height: int = 600
    cell_size: int = 20

    # ========================================================================
    # Grid Configuration
    # ========================================================================
    grid_width: int = 20
    grid_height: int = 20

    # Current grid state: 2D list (row, col)
    # 0 = free, 1 = obstacle, 2 = start, 3 = goal
    grid: List[List[int]] = field(default_factory=lambda: [[0] * 20 for _ in range(20)])

    obstacles: List[Tuple[int, int]] = field(default_factory=list)
    start: Optional[Tuple[int, int]] = None
    goal: Optional[Tuple[int, int]] = None

    # Most recent planned path
    path: List[Tuple[int, int]] = field(default_factory=list)

    # ========================================================================
    # Algorithm Configuration
    # ========================================================================
    current_algorithm: str = "HAPSO"  # "ASTAR", "PSO", "APSO", "HAPSO"

    # A* options
    astar_prune_collinear: bool = True
    astar_prune_transitions: bool = True
    astar_avoid_corner_cutting: bool = False

    # PSO options
    pso_particles: int = 50
    pso_iterations: int = 120
    pso_inertia_strategy: str = "LDIW"  # "LDIW", "NDIW", "AIW", "SIW"
    pso_cognitive_coeff: float = 1.4
    pso_social_coeff: float = 1.6
    pso_max_velocity: float = 2.5

    # ========================================================================
    # UI State
    # ========================================================================
    current_screen: str = "MENU"  # "MENU", "EDITOR", "SIMULATOR", "COMPARE"
    is_collision_check_mode: bool = False
    last_message: str = ""
    message_timestamp: float = 0.0

    # ========================================================================
    # Last Run Metrics
    # ========================================================================
    last_path_length: Optional[float] = None
    last_waypoint_count: Optional[int] = None
    last_computation_time: Optional[float] = None
    last_total_rotation: Optional[float] = None
    last_error: Optional[str] = None

    # ========================================================================
    # Experiment Results (from running all algorithms)
    # ========================================================================
    experiment_results: dict[str, dict] = field(default_factory=dict)
    # Format: {
    #   "A*": {"path_length": 12.5, "waypoints": 15, "found": True},
    #   "PSO": {"path_length": 13.1, "waypoints": 18, "found": True},
    #   ...
    # }

    def reset_grid(self) -> None:
        """Reset grid to all free cells."""
        self.grid = [[0] * self.grid_width for _ in range(self.grid_height)]
        self.obstacles = []
        self.start = None
        self.goal = None
        self.path = []

    def reset_metrics(self) -> None:
        """Clear last run metrics."""
        self.last_path_length = None
        self.last_waypoint_count = None
        self.last_computation_time = None
        self.last_total_rotation = None
        self.last_error = None

    def set_message(self, message: str, timestamp: float) -> None:
        """Set temporary message."""
        self.last_message = message
        self.message_timestamp = timestamp

    def get_message(self) -> Optional[str]:
        """Get message if still active (within 3 seconds)."""
        import time

        if self.last_message and (time.time() - self.message_timestamp) < 3.0:
            return self.last_message
        return None


__all__ = ["AppState"]
