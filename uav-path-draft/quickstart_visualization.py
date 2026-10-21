"""
Quick start example - Showing detailed algorithm visualization
Simple script to visualize one algorithm step-by-step
"""

import matplotlib.pyplot as plt
from utils.environment import UAVEnvironment
from utils.visualize_progress import visualize_algorithm_progress
from algorithms import PSOPathfinder


def main():
    """
    Simple example: Visualize PSO algorithm progress
    Shows 5 snapshots of how particles move toward the goal
    """
    
    print("Creating environment...")
    env = UAVEnvironment(width=100, height=100)
    
    # Generate 5 random obstacles
    env.simple_map(num_obstacles=5, seed=42)
    
    env.set_start_goal((5, 5), (95, 95))
    
    print("Creating PSO with tracking enabled...")
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    
    print("Generating detailed progress visualization...")
    fig = visualize_algorithm_progress(env, pso, "PSO", num_snapshots=5)
    
    if fig:
        fig.suptitle("PSO Algorithm Progress: How Particles Find the Path", 
                    fontsize=14, fontweight='bold')
        print("Visualizing...")
        plt.show()
    else:
        print("Error: Could not generate visualization")


if __name__ == "__main__":
    main()
