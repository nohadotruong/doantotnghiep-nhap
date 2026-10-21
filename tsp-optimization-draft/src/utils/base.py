"""
Module: Utilities
Purpose: Common utility functions
"""

import numpy as np
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path


class ResultsRecorder:
    """Record and save planning results"""

    def __init__(self, save_dir: str = "results"):
        """Initialize recorder"""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.results = {}

    def record_result(self, experiment_name: str, result_data: Dict[str, Any]):
        """Record experiment result"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{experiment_name}_{timestamp}"
        self.results[key] = result_data
        return key

    def save_results(self, key: str, filename_prefix: str = ""):
        """Save results to JSON file"""
        if key not in self.results:
            raise ValueError(f"Result '{key}' not found")

        data = self.results[key]

        # Convert numpy arrays to lists for JSON serialization
        data_serializable = self._make_serializable(data)

        filename = f"{filename_prefix}_{key}.json" if filename_prefix else f"{key}.json"
        filepath = self.save_dir / filename

        with open(filepath, "w") as f:
            json.dump(data_serializable, f, indent=2)

        return filepath

    def save_all_results(self, filename_prefix: str = ""):
        """Save all results"""
        filepaths = []
        for key in self.results:
            filepath = self.save_results(key, filename_prefix)
            filepaths.append(filepath)
        return filepaths

    @staticmethod
    def _make_serializable(obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: ResultsRecorder._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ResultsRecorder._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return obj


class PerformanceMetrics:
    """Calculate performance metrics"""

    @staticmethod
    def path_length(path: List[np.ndarray]) -> float:
        """Calculate total path length"""
        total = 0.0
        for i in range(len(path) - 1):
            total += np.linalg.norm(path[i + 1] - path[i])
        return total

    @staticmethod
    def path_smoothness(path: List[np.ndarray]) -> float:
        """
        Calculate path smoothness using curvature
        Lower is smoother
        """
        if len(path) < 3:
            return 0.0

        curvature_sum = 0.0
        for i in range(1, len(path) - 1):
            p1 = np.array(path[i - 1])
            p2 = np.array(path[i])
            p3 = np.array(path[i + 1])

            # Vectors
            v1 = p2 - p1
            v2 = p3 - p2

            # Angle between vectors
            l1 = np.linalg.norm(v1)
            l2 = np.linalg.norm(v2)

            if l1 > 0 and l2 > 0:
                cos_angle = np.dot(v1, v2) / (l1 * l2)
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle = np.arccos(cos_angle)
                curvature_sum += angle

        return curvature_sum

    @staticmethod
    def waypoint_visit_order(
        path: List[np.ndarray], waypoints: List[np.ndarray]
    ) -> List[int]:
        """Determine order waypoints are visited in path"""
        order = []
        visited = set()

        for wp_idx, waypoint in enumerate(waypoints):
            # Find closest point in path to this waypoint
            min_dist = float("inf")
            closest_path_idx = -1

            for path_idx, path_point in enumerate(path):
                dist = np.linalg.norm(path_point - waypoint)
                if dist < min_dist:
                    min_dist = dist
                    closest_path_idx = path_idx

            if closest_path_idx not in visited:
                order.append(wp_idx)
                visited.add(closest_path_idx)

        return order

    @staticmethod
    def improvement_percentage(original: float, improved: float) -> float:
        """Calculate improvement percentage"""
        if original == 0:
            return 0.0
        return ((original - improved) / original) * 100

    @staticmethod
    def compute_all_metrics(
        path: List[np.ndarray], waypoints: List[np.ndarray], cost: float
    ) -> Dict[str, Any]:
        """Compute all metrics for a path"""
        return {
            "path_length": PerformanceMetrics.path_length(path),
            "path_smoothness": PerformanceMetrics.path_smoothness(path),
            "optimal_cost": cost,
            "waypoint_count": len(waypoints),
            "path_point_count": len(path),
        }


def create_test_environment(test_type: str = "simple") -> Tuple:
    """
    Create test environments with obstacles

    Args:
        test_type: Type of test environment

    Returns:
        Tuple: (environment, start, goal, waypoints)
    """
    from ..environment import Environment

    if test_type == "simple":
        # Simple environment with few obstacles
        env = Environment(bounds=(0, 100, 0, 100))

        # Add some obstacles
        env.add_circle_obstacle(center=[30, 30], radius=8)
        env.add_circle_obstacle(center=[70, 70], radius=8)

        start = np.array([5, 5])
        goal = np.array([95, 95])
        waypoints = [
            np.array([30, 60]),
            np.array([60, 30]),
            np.array([40, 80]),
        ]

    elif test_type == "complex":
        # Complex environment with many obstacles
        env = Environment(bounds=(0, 100, 0, 100))

        # Add circular obstacles
        for x in range(20, 100, 30):
            for y in range(20, 100, 30):
                if np.random.rand() > 0.3:
                    env.add_circle_obstacle(center=[x, y], radius=5)

        # Add rectangular obstacles
        env.add_rectangle_obstacle(40, 50, 30, 40)
        env.add_rectangle_obstacle(60, 70, 50, 60)

        start = np.array([5, 5])
        goal = np.array([95, 95])
        waypoints = [
            np.array([25, 75]),
            np.array([50, 50]),
            np.array([75, 25]),
            np.array([75, 75]),
        ]

    elif test_type == "narrow":
        # Environment with narrow passages
        env = Environment(bounds=(0, 100, 0, 100))

        # Create narrow corridor
        env.add_rectangle_obstacle(0, 40, 40, 60)
        env.add_rectangle_obstacle(60, 100, 40, 60)

        env.add_circle_obstacle(center=[20, 80], radius=8)
        env.add_circle_obstacle(center=[80, 20], radius=8)

        start = np.array([5, 50])
        goal = np.array([95, 50])
        waypoints = [
            np.array([50, 80]),
            np.array([50, 20]),
        ]

    else:
        raise ValueError(f"Unknown test type: {test_type}")

    return env, start, goal, waypoints


def print_results_table(results: Dict[str, Dict[str, float]]):
    """Print results in formatted table"""
    print("\n" + "=" * 80)
    print("PLANNING RESULTS COMPARISON")
    print("=" * 80)

    # Get all metric names
    metrics = set()
    for method_results in results.values():
        metrics.update(method_results.keys())
    metrics = sorted(metrics)

    # Print header
    header = "Method".ljust(20)
    for metric in metrics:
        header += metric.ljust(20)
    print(header)
    print("-" * 80)

    # Print rows
    for method, method_results in results.items():
        row = method.ljust(20)
        for metric in metrics:
            value = method_results.get(metric, 0.0)
            if isinstance(value, float):
                row += f"{value:.4f}".ljust(20)
            else:
                row += str(value).ljust(20)
        print(row)

    print("=" * 80 + "\n")
