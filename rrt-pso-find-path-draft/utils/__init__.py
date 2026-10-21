"""
Utils Package - Core utilities, Evaluation metrics, Optimization tools

Structure:
  core.py: Collision detection & path utilities (foundation)
  evaluation.py: Path metrics & evaluation (depends on core)
  optimization.py: Benchmarking, tuning, algorithm optimization (depends on core + evaluation)
"""

# Import core utilities
from utils.core import (
    point_in_rectangle,
    line_rectangle_collision,
    line_rectangle_collision_by_points,
    line_segment_intersection,
    path_length,
    smoothness_penalty,
    calculate_min_distance_to_obstacle
)

# Import evaluation metrics
from utils.evaluation import (
    PathMetrics,
    SafetyMetrics,
    SmoothnessMetrics,
    ExecutionMetrics,
    ComprehensiveEvaluation,
    PerformanceMetrics,
    ComparisonMetrics,
    report_metrics
)

# Note: optimization.py imports environment.environment to avoid circular imports
# Import optimization tools only when needed
# from utils.optimization import (
#     BenchmarkConfig,
#     RRTBenchmark,
#     PSOBenchmark,
#     BenchmarkReport,
#     run_full_benchmark,
#     ParameterTuner,
#     PSOParameterTuner
# )

__all__ = [
    # Core
    'point_in_rectangle',
    'line_rectangle_collision',
    'line_rectangle_collision_by_points',
    'line_segment_intersection',
    'path_length',
    'smoothness_penalty',
    'calculate_min_distance_to_obstacle',
    
    # Evaluation
    'PathMetrics',
    'SafetyMetrics',
    'SmoothnessMetrics',
    'ExecutionMetrics',
    'ComprehensiveEvaluation',
    'PerformanceMetrics',
    'ComparisonMetrics',
    'report_metrics'
    
    # Optimization imports removed to avoid circular dependencies
    # Import from utils.optimization directly when needed
]
