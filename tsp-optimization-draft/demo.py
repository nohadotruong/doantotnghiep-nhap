"""
Simple Demo of Multi-Point Path Optimization
Shows how to use the system in a straightforward way
"""

import sys
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.environment import Environment
from src.algorithms import MultiPointPlanner
from src.utils import PathVisualizer, PerformanceMetrics


def demo_simple():
    """Simple demonstration with a basic environment"""
    print("=" * 80)
    print("DEMO 1: Simple Multi-Point Path Planning")
    print("=" * 80)

    # Create environment
    env = Environment(bounds=(0, 100, 0, 100))

    # Add some obstacles
    env.add_circle_obstacle([30, 30], radius=8)
    env.add_circle_obstacle([70, 70], radius=8)
    env.add_rectangle_obstacle(40, 60, 40, 50)

    # Define waypoints
    start = np.array([5, 5])
    goal = np.array([95, 95])
    waypoints = [
        np.array([30, 70]),
        np.array([60, 30]),
        np.array([70, 60]),
    ]

    print(f"\nEnvironment: 100x100")
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print(f"Waypoints: {len(waypoints)}")
    print(f"Obstacles: {len(env.obstacles)}")

    # Plan path using proposed method (PSO + 2-Opt)
    print("\nPlanning path using PSO + 2-Opt...")

    planner = MultiPointPlanner(env)
    path, cost, info = planner.plan(
        start, waypoints, goal, optimizer="combined", rrt_iterations=3000
    )

    print(f"✓ Path found!")
    print(f"  - Total cost: {cost:.4f}")
    print(f"  - Path length: {PerformanceMetrics.path_length(path):.4f}")
    print(f"  - Path smoothness: {PerformanceMetrics.path_smoothness(path):.4f}")
    print(f"  - Number of waypoints: {len(path)}")

    # Visualize
    print("\nGenerating visualization...")
    visualizer = PathVisualizer()
    visualizer.plot(
        env,
        path,
        waypoints,
        title="Demo 1: Multi-Point Path Planning",
        save_path="results/demo_simple.png",
    )

    return path


def demo_comparison():
    """Compare different optimization methods"""
    print("\n" + "=" * 80)
    print("DEMO 2: Compare Optimization Methods")
    print("=" * 80)

    # Create environment
    env = Environment(bounds=(0, 100, 0, 100))

    # Add obstacles to create more interesting problem
    env.add_circle_obstacle([30, 50], radius=8)
    env.add_circle_obstacle([50, 30], radius=8)
    env.add_circle_obstacle([70, 70], radius=8)
    env.add_rectangle_obstacle(45, 55, 45, 55)

    # Define waypoints
    start = np.array([5, 5])
    goal = np.array([95, 95])
    waypoints = [
        np.array([25, 75]),
        np.array([50, 50]),
        np.array([75, 25]),
    ]

    print(f"\nEnvironment: 100x100")
    print(f"Waypoints: {len(waypoints)}")
    print(f"Obstacles: {len(env.obstacles)}\n")

    results = {}
    paths = {}

    # Test different methods
    methods = ["greedy", "pso", "combined"]

    for method in methods:
        print(f"Testing {method}...", end=" ")

        planner = MultiPointPlanner(env)
        path, cost, info = planner.plan(
            start, waypoints, goal, optimizer=method, rrt_iterations=2000
        )

        results[method] = {
            "cost": cost,
            "smoothness": PerformanceMetrics.path_smoothness(path),
            "length": PerformanceMetrics.path_length(path),
        }
        paths[method] = path

        print(f"✓ Cost: {cost:.4f}")

    # Print comparison
    print("\n" + "-" * 60)
    print("COMPARISON:")
    print("-" * 60)
    print(f"{'Method':15} {'Cost':15} {'Length':15} {'Smoothness':15}")
    print("-" * 60)
    for method, res in results.items():
        print(
            f"{method:15} {res['cost']:15.4f} {res['length']:15.4f} {res['smoothness']:15.4f}"
        )

    # Find best
    best_method = min(results.items(), key=lambda x: x[1]["cost"])[0]
    best_cost = results[best_method]["cost"]

    print("-" * 60)
    print(f"Best method: {best_method} (Cost: {best_cost:.4f})")
    print("-" * 60)

    # Visualize comparison
    print("\nGenerating comparison visualization...")
    visualizer = PathVisualizer()
    visualizer.compare_paths(
        env,
        paths,
        waypoints,
        title="Demo 2: Method Comparison",
        save_path="results/demo_comparison.png",
    )

    return results, paths


def demo_obstacle_avoidance():
    """Demonstrate obstacle avoidance capability"""
    print("\n" + "=" * 80)
    print("DEMO 3: Complex Obstacle Avoidance")
    print("=" * 80)

    # Create challenging environment with narrow passages
    env = Environment(bounds=(0, 100, 0, 100))

    # Create maze-like environment
    env.add_rectangle_obstacle(20, 30, 0, 70)
    env.add_rectangle_obstacle(50, 60, 30, 100)
    env.add_circle_obstacle([40, 40], radius=10)
    env.add_circle_obstacle([70, 70], radius=8)

    start = np.array([5, 50])
    goal = np.array([95, 50])
    waypoints = [
        np.array([35, 80]),
        np.array([65, 20]),
        np.array([85, 80]),
    ]

    print(f"\nEnvironment: 100x100 with complex obstacles")
    print(f"Waypoints: {len(waypoints)}")
    print(f"Obstacles: {len(env.obstacles)}\n")

    # Plan using proposed method
    print("Planning with PSO + 2-Opt...")

    planner = MultiPointPlanner(env)
    path, cost, info = planner.plan(
        start, waypoints, goal, optimizer="combined", rrt_iterations=4000
    )

    print(f"✓ Path found!")
    print(f"  - Cost: {cost:.4f}")
    print(f"  - Path points: {len(path)}")
    print(f"  - Smoothness: {PerformanceMetrics.path_smoothness(path):.4f}")

    # Visualize
    print("\nGenerating visualization...")
    visualizer = PathVisualizer()
    visualizer.plot(
        env,
        path,
        waypoints,
        title="Demo 3: Complex Obstacle Avoidance",
        save_path="results/demo_obstacles.png",
    )

    return path


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("UAV MULTI-POINT PATH OPTIMIZATION - DEMO")
    print("=" * 80)

    # Create results directory
    Path("results").mkdir(exist_ok=True)

    # Run demos
    path1 = demo_simple()
    results2, paths2 = demo_comparison()
    path3 = demo_obstacle_avoidance()

    print("\n" + "=" * 80)
    print("DEMOS COMPLETED - Check results/ folder for visualizations")
    print("=" * 80 + "\n")
