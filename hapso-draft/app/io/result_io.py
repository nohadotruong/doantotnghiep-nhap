"""
Result I/O - Save planning results to JSON and images.

This module handles persisting planning results to the file system:
- JSON results with metadata (timestamp, algorithm, metrics, path coordinates)
- PNG images of the planned path
- Timestamped directory structure

The module accepts planning.api.PlanResult as input and converts to JSON format.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import planning.api as plan_api
from app.state import AppState


def save_result_bundle(
    result: plan_api.PlanResult, state: AppState, base_dir: str = "data/results"
) -> str:
    """
    Save complete result bundle (JSON + metadata).

    Args:
        result: PlanResult from planning.api.run_plan()
        state: Current AppState for grid configuration
        base_dir: Base directory for results

    Returns:
        Path to created result directory

    Raises:
        IOError: If directory creation or file writing fails
    """
    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(base_dir, timestamp)

    # Ensure directory exists
    Path(result_dir).mkdir(parents=True, exist_ok=True)

    # Save result JSON
    result_json_path = os.path.join(result_dir, "result.json")

    # Build result dictionary
    result_dict = {
        "timestamp": datetime.now().isoformat(),
        "algorithm": state.current_algorithm,
        "success": result.success,
        "grid": {
            "width": state.grid_width,
            "height": state.grid_height,
            "start": list(state.start) if state.start else None,
            "goal": list(state.goal) if state.goal else None,
            "obstacles_count": len(state.obstacles),
        },
        "path": {
            "found": result.success,
            "waypoints": len(result.path) if result.path else 0,
            "coordinates": (
                [(int(p.x), int(p.y)) for p in result.path] if result.path else []
            ),
        },
        "metrics": None,
        "error": result.error_message if result.error_message else None,
    }

    # Add metrics if successful
    if result.success and result.metrics:
        result_dict["metrics"] = {
            "path_length": round(result.metrics.path_length, 4),
            "waypoint_count": result.metrics.waypoint_count,
            "total_rotation": round(result.metrics.total_rotation, 4),
            "computation_time": round(result.metrics.computation_time, 4),
            "path_valid": result.metrics.path_valid,
            "objective_value": round(result.metrics.objective_value, 4),
        }

    # Write JSON
    with open(result_json_path, "w") as f:
        json.dump(result_dict, f, indent=2)

    return result_dir


def save_experiment_results(
    experiment_result: plan_api.ExperimentResult,
    state: AppState,
    base_dir: str = "data/results",
) -> str:
    """
    Save multi-algorithm experiment results.

    Args:
        experiment_result: ExperimentResult from planning.api.run_experiment()
        state: Current AppState for grid configuration
        base_dir: Base directory for results

    Returns:
        Path to created result directory
    """
    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(base_dir, timestamp)

    # Ensure directory exists
    Path(result_dir).mkdir(parents=True, exist_ok=True)

    # Save experiment JSON
    experiment_json_path = os.path.join(result_dir, "experiment.json")

    # Build experiment dictionary
    experiment_dict = {
        "timestamp": datetime.now().isoformat(),
        "grid": {
            "width": state.grid_width,
            "height": state.grid_height,
            "start": list(state.start) if state.start else None,
            "goal": list(state.goal) if state.goal else None,
            "obstacles_count": len(state.obstacles),
        },
        "best_algorithm": experiment_result.best_algorithm,
        "best_path_length": experiment_result.best_path_length,
        "results": {},
    }

    # Add results for each algorithm
    for algo_name, plan_result in experiment_result.results.items():
        if plan_result.success and plan_result.metrics:
            experiment_dict["results"][algo_name] = {
                "found": True,
                "path_length": round(plan_result.metrics.path_length, 4),
                "waypoint_count": plan_result.metrics.waypoint_count,
                "computation_time": round(plan_result.metrics.computation_time, 4),
                "total_rotation": round(plan_result.metrics.total_rotation, 4),
                "objective_value": round(plan_result.metrics.objective_value, 4),
            }
        else:
            experiment_dict["results"][algo_name] = {
                "found": False,
                "error": plan_result.error_message,
            }

    # Write JSON
    with open(experiment_json_path, "w") as f:
        json.dump(experiment_dict, f, indent=2)

    return result_dir


def load_result(result_path: str) -> dict:
    """
    Load result from JSON file.

    Args:
        result_path: Path to result.json file

    Returns:
        Dictionary with result data
    """
    with open(result_path, "r") as f:
        return json.load(f)


def list_results(base_dir: str = "data/results") -> list[str]:
    """
    List all saved results (timestamped directories).

    Args:
        base_dir: Base directory for results

    Returns:
        List of result directory names (sorted newest first)
    """
    results_path = Path(base_dir)
    if not results_path.exists():
        return []

    dirs = [d.name for d in results_path.iterdir() if d.is_dir()]
    return sorted(dirs, reverse=True)


__all__ = [
    "save_result_bundle",
    "save_experiment_results",
    "load_result",
    "list_results",
]
