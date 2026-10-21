"""
Main Comparison Program
Compare different optimization methods for multi-point path planning
"""

import sys
import numpy as np
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.environment import Environment
from src.algorithms import MultiPointPlanner, TSPSolver
from src.utils import (
    ResultsRecorder,
    PerformanceMetrics,
    PathVisualizer,
    create_test_environment,
    print_results_table,
)


def run_comparison_single_environment(
    test_type: str = "simple", num_waypoints: int = None
):
    """
    Run comparison on single environment

    Args:
        test_type: Type of test environment
        num_waypoints: Number of waypoints (if None, use default)
    """
    print(f"\n{'='*80}")
    print(f"TEST: {test_type.upper()} ENVIRONMENT")
    print(f"{'='*80}\n")

    # Create environment
    env, start, goal, waypoints = create_test_environment(test_type)

    if num_waypoints:
        waypoints = waypoints[:num_waypoints]

    print(
        f"Environment bounds: ({env.x_min}, {env.x_max}) x ({env.y_min}, {env.y_max})"
    )
    print(f"Number of obstacles: {len(env.obstacles)}")
    print(f"Number of waypoints: {len(waypoints)}")
    print(f"Start: {start}")
    print(f"Goal: {goal}\n")

    # Dictionary to store results
    results = {}
    all_paths = {}

    # ========== Method 1: Greedy Nearest Neighbor ==========
    print("Computing Greedy Nearest Neighbor...")
    start_time = time.time()

    try:
        planner = MultiPointPlanner(env)
        path, cost, info = planner.plan(
            start, waypoints, goal, optimizer="greedy", rrt_iterations=3000
        )
        elapsed = time.time() - start_time

        all_paths["Greedy"] = path
        results["Greedy"] = {
            "cost": cost,
            "time": elapsed,
            "smoothness": PerformanceMetrics.path_smoothness(path),
            "path_length": PerformanceMetrics.path_length(path),
        }
        print(f"  ✓ Cost: {cost:.4f}, Time: {elapsed:.4f}s")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        results["Greedy"] = {"cost": float("inf"), "time": -1}

    # ========== Method 2: 2-Opt Improvement ==========
    print("Computing 2-Opt...")
    start_time = time.time()

    try:
        planner = MultiPointPlanner(env)
        path, cost, info = planner.plan(
            start, waypoints, goal, optimizer="2opt", rrt_iterations=3000
        )
        elapsed = time.time() - start_time

        all_paths["2-Opt"] = path
        results["2-Opt"] = {
            "cost": cost,
            "time": elapsed,
            "smoothness": PerformanceMetrics.path_smoothness(path),
            "path_length": PerformanceMetrics.path_length(path),
        }
        print(f"  ✓ Cost: {cost:.4f}, Time: {elapsed:.4f}s")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        results["2-Opt"] = {"cost": float("inf"), "time": -1}

    # ========== Method 3: PSO ==========
    print("Computing PSO...")
    start_time = time.time()

    try:
        planner = MultiPointPlanner(env)
        path, cost, info = planner.plan(
            start, waypoints, goal, optimizer="pso", rrt_iterations=3000
        )
        elapsed = time.time() - start_time

        all_paths["PSO"] = path
        results["PSO"] = {
            "cost": cost,
            "time": elapsed,
            "smoothness": PerformanceMetrics.path_smoothness(path),
            "path_length": PerformanceMetrics.path_length(path),
        }
        print(f"  ✓ Cost: {cost:.4f}, Time: {elapsed:.4f}s")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        results["PSO"] = {"cost": float("inf"), "time": -1}

    # ========== Method 4: Combined PSO + 2-Opt (PROPOSED) ==========
    print("Computing PSO + 2-Opt (PROPOSED)...")
    start_time = time.time()

    try:
        planner = MultiPointPlanner(env)
        path, cost, info = planner.plan(
            start, waypoints, goal, optimizer="combined", rrt_iterations=3000
        )
        elapsed = time.time() - start_time

        all_paths["PSO+2Opt"] = path
        results["PSO+2Opt"] = {
            "cost": cost,
            "time": elapsed,
            "smoothness": PerformanceMetrics.path_smoothness(path),
            "path_length": PerformanceMetrics.path_length(path),
        }
        print(f"  ✓ Cost: {cost:.4f}, Time: {elapsed:.4f}s")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        results["PSO+2Opt"] = {"cost": float("inf"), "time": -1}

    # ========== Analysis ==========
    print("\n" + "=" * 80)
    print("RESULTS ANALYSIS")
    print("=" * 80)

    # Find best method
    best_method = min(results.items(), key=lambda x: x[1]["cost"])[0]
    best_cost = results[best_method]["cost"]

    print(f"\nBest method: {best_method}")
    print(f"Best cost: {best_cost:.4f}\n")

    # Calculate improvements
    for method, result in results.items():
        if method != best_method and result["cost"] != float("inf"):
            improvement = PerformanceMetrics.improvement_percentage(
                result["cost"], best_cost
            )
            print(
                f"{method:15} → Cost improvement vs. {best_method}: {improvement:.2f}%"
            )

    # Print full results table
    print_results_table(results)

    # ========== Visualization ==========
    try:
        visualizer = PathVisualizer()

        # Plot comparison
        visualizer.compare_paths(
            env,
            all_paths,
            waypoints,
            title=f"Multi-Point Path Comparison ({test_type})",
            save_path=f"results/comparison_{test_type}.png",
        )

        # Plot cost comparison
        cost_results = {name: results[name]["cost"] for name in results}
        PathVisualizer.plot_cost_comparison(
            cost_results,
            title=f"Cost Comparison ({test_type})",
            save_path=f"results/cost_comparison_{test_type}.png",
        )

        print("\nPlots saved to results/")
    except Exception as e:
        print(f"\nVisualization error: {str(e)}")

    return results, all_paths, env, waypoints


def run_scalability_test():
    """Test scalability with different numbers of waypoints"""
    print(f"\n{'='*80}")
    print("SCALABILITY TEST")
    print(f"{'='*80}\n")

    env, start, goal, waypoints = create_test_environment("simple")

    scalability_results = {}

    for num_wp in [2, 3, 4, 5]:
        print(f"\nTesting with {num_wp} waypoints...")

        current_waypoints = waypoints[:num_wp]

        # Create simplified test with fewer RRT iterations for speed
        planner = MultiPointPlanner(env)

        times = {}
        costs = {}

        for optimizer in ["greedy", "pso", "combined"]:
            print(f"  {optimizer}...", end=" ")

            start_time = time.time()
            try:
                path, cost, info = planner.plan(
                    start,
                    current_waypoints,
                    goal,
                    optimizer=optimizer,
                    rrt_iterations=2000,
                )
                elapsed = time.time() - start_time
                times[optimizer] = elapsed
                costs[optimizer] = cost
                print(f"✓ ({elapsed:.2f}s)")
            except Exception as e:
                print(f"✗ ({str(e)})")
                times[optimizer] = -1
                costs[optimizer] = float("inf")

        scalability_results[num_wp] = {"times": times, "costs": costs}

    # Print scalability results
    print("\n" + "=" * 80)
    print("SCALABILITY RESULTS")
    print("=" * 80)
    print("\nComputation Time (seconds):")
    print(f"{'Waypoints':15} {'Greedy':15} {'PSO':15} {'PSO+2Opt':15}")
    print("-" * 60)
    for num_wp in sorted(scalability_results.keys()):
        row = f"{num_wp:15}"
        for opt in ["greedy", "pso", "combined"]:
            t = scalability_results[num_wp]["times"].get(opt, -1)
            row += f"{t:15.4f}" if t > 0 else f"{'N/A':15}"
        print(row)

    return scalability_results


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("UAV MULTI-POINT PATH OPTIMIZATION")
    print(
        "Thesis: Tối ưu hóa đường bay đa điểm cho UAV trong môi trường có chướng ngại vật"
    )
    print("=" * 80)

    # Create results directory
    Path("results").mkdir(exist_ok=True)

    # Run comparisons on different environments
    all_results = {}

    for test_type in ["simple", "complex"]:
        results, paths, env, waypoints = run_comparison_single_environment(test_type)
        all_results[test_type] = results

    # Run scalability test
    scalability = run_scalability_test()

    # Save results
    recorder = ResultsRecorder()
    recorder.record_result("comparison_results", all_results)
    recorder.record_result("scalability_results", scalability)
    recorder.save_all_results("uav")

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETED")
    print("Results saved to results/ directory")
    print("=" * 80 + "\n")
