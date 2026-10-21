"""
Examples - Usage examples for each algorithm

These examples help you understand how to use each algorithm separately
"""

import numpy as np
import matplotlib.pyplot as plt
from utils.environment import UAVEnvironment
from algorithms import (
    AStarPathfinder,
    PSOPathfinder,
    SAPathfinder,
    GWOPathfinder,
    GAPathfinder
)


def example1_astar():
    """
    Example 1: Using A* to find path
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: A* Algorithm")
    print("="*60)
    
    env = UAVEnvironment(width=50, height=50)
    env.add_rectangular_obstacle(15, 15, 10, 20)
    env.set_start_goal(start=(5, 5), goal=(45, 45))
    
    print("Running A*...")
    astar = AStarPathfinder(env, grid_step=2.0)
    success = astar.find_path()
    
    if success:
        stats = astar.get_statistics()
        print(f"Success! Distance: {stats['distance']:.2f}")
        path = astar.get_path()
        env.visualize(path, title="A* Pathfinding")
    
    return env, astar


def example2_pso():
    """
    Example 2: Using PSO to find path
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Particle Swarm Optimization (PSO)")
    print("="*60)
    
    env = UAVEnvironment(width=80, height=80)
    env.add_rectangular_obstacle(20, 20, 15, 25)
    env.add_circular_obstacle(60, 40, 8)
    env.set_start_goal(start=(5, 5), goal=(75, 75))
    
    print("Running PSO...")
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    success = pso.find_path()
    
    if success:
        stats = pso.get_statistics()
        print(f"Success! Distance: {stats['distance']:.2f}")
        path = pso.get_path()
        env.visualize(path, title="PSO Pathfinding")
    
    return env, pso


def example3_compare():
    """
    Example 3: Compare two algorithms
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Compare PSO vs GWO")
    print("="*60)
    
    env = UAVEnvironment(width=100, height=100)
    env.add_rectangular_obstacle(30, 40, 20, 15)
    env.add_rectangular_obstacle(60, 20, 15, 30)
    env.set_start_goal(start=(5, 5), goal=(95, 95))
    
    print("Running PSO...")
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    pso.find_path()
    pso_stats = pso.get_statistics()
    print(f"PSO: {pso_stats['distance']:.2f}")
    
    print("Running GWO...")
    gwo = GWOPathfinder(env, num_wolves=30, max_iterations=200)
    gwo.find_path()
    gwo_stats = gwo.get_statistics()
    print(f"GWO: {gwo_stats['distance']:.2f}")


def example4_all():
    """
    Example 4: Run all algorithms
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Run All Algorithms")
    print("="*60)
    
    env = UAVEnvironment(width=100, height=100)
    env.add_rectangular_obstacle(20, 30, 20, 10)
    env.add_rectangular_obstacle(50, 50, 15, 25)
    env.add_rectangular_obstacle(70, 20, 15, 15)
    env.add_circular_obstacle(35, 70, 8)
    env.add_circular_obstacle(60, 10, 10)
    env.set_start_goal(start=(5, 5), goal=(95, 95))
    
    algorithms = [
        ("A*", AStarPathfinder(env, grid_step=2.0)),
        ("PSO", PSOPathfinder(env, num_particles=30, max_iterations=200)),
        ("SA", SAPathfinder(env, initial_temp=100, cooling_rate=0.95)),
        ("GWO", GWOPathfinder(env, num_wolves=30, max_iterations=200)),
        ("GA", GAPathfinder(env, population_size=30, max_iterations=200))
    ]
    
    for name, algo in algorithms:
        print(f"Running {name}...")
        algo.find_path()
        stats = algo.get_statistics()
        print(f"  Distance: {stats['distance']:.2f}")


def main():
    """
    Run examples
    """
    print("\n" + "#"*60)
    print("# EXAMPLES - ALGORITHM PATHFINDING USAGE EXAMPLES")
    print("#"*60)
    
    # Uncomment lines below to run corresponding example
    example1_astar()
    # example2_pso()
    # example3_compare()
    # example4_all()
    
    print("\n" + "="*60)
    print("Completed!")
    print("="*60 + "\n")
    
    plt.show()


if __name__ == "__main__":
    main()
