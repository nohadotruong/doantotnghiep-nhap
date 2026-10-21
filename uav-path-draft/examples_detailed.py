"""
Detailed visualization examples of each algorithm
Shows step-by-step progress of how algorithms find paths
"""

import numpy as np
import matplotlib.pyplot as plt
from utils.environment import UAVEnvironment
from utils.visualize_progress import (
    visualize_algorithm_progress,
    visualize_algorithm_comparison_detailed
)
from algorithms import (
    AStarPathfinder,
    PSOPathfinder,
    SAPathfinder,
    GWOPathfinder,
    GAPathfinder
)


def create_environment():
    """Create UAV environment with obstacles"""
    env = UAVEnvironment(width=100, height=100)
    
    # Generate 5 random obstacles
    env.simple_map(num_obstacles=5, seed=42)
    
    env.set_start_goal(
        start=(5, 5),
        goal=(95, 95)
    )
    
    return env


def example_1_individual_algorithm_progress():
    """
    Example 1: Visualize progress of each algorithm individually
    Shows 5 snapshots of how algorithm executes step by step
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Individual Algorithm Progress (Step-by-step)")
    print("="*60)
    
    env = create_environment()
    
    # PSO Example
    print("\n[1] Visualizing PSO (Particle Swarm Optimization)...")
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    fig_pso = visualize_algorithm_progress(env, pso, "PSO", num_snapshots=5)
    if fig_pso:
        fig_pso.suptitle("PSO Progress: Particles moving toward goal", fontsize=14, fontweight='bold')
    
    # A* Example
    print("[2] Visualizing A* (A-Star Pathfinding)...")
    astar = AStarPathfinder(env, grid_step=2.0)
    fig_astar = visualize_algorithm_progress(env, astar, "A*", num_snapshots=5)
    if fig_astar:
        fig_astar.suptitle("A* Progress: Exploring frontier toward goal", fontsize=14, fontweight='bold')
    
    # SA Example
    print("[3] Visualizing SA (Simulated Annealing)...")
    sa = SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500)
    fig_sa = visualize_algorithm_progress(env, sa, "SA", num_snapshots=5)
    if fig_sa:
        fig_sa.suptitle("SA Progress: Temperature cooling down", fontsize=14, fontweight='bold')
    
    # GWO Example
    print("[4] Visualizing GWO (Grey Wolf Optimizer)...")
    gwo = GWOPathfinder(env, num_wolves=30, max_iterations=200)
    fig_gwo = visualize_algorithm_progress(env, gwo, "GWO", num_snapshots=5)
    if fig_gwo:
        fig_gwo.suptitle("GWO Progress: Pack hunting (Alpha/Beta/Delta hierarchy)", fontsize=14, fontweight='bold')
    
    # GA Example
    print("[5] Visualizing GA (Genetic Algorithm)...")
    ga = GAPathfinder(env, population_size=30, max_iterations=200)
    fig_ga = visualize_algorithm_progress(env, ga, "GA", num_snapshots=5)
    if fig_ga:
        fig_ga.suptitle("GA Progress: Population evolution", fontsize=14, fontweight='bold')
    
    plt.show()


def example_2_algorithm_comparison():
    """
    Example 2: Comparison of all algorithms in progress
    Each row = one algorithm, columns = different iterations
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: All Algorithms Comparison (Side-by-side)")
    print("="*60)
    
    env = create_environment()
    
    algorithms = {
        "A*": AStarPathfinder(env, grid_step=2.0),
        "PSO": PSOPathfinder(env, num_particles=30, max_iterations=200),
        "SA": SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500),
        "GWO": GWOPathfinder(env, num_wolves=30, max_iterations=200),
        "GA": GAPathfinder(env, population_size=30, max_iterations=200)
    }
    
    fig = visualize_algorithm_comparison_detailed(env, algorithms, num_snapshots=4)
    fig.suptitle("Algorithm Evolution Comparison: From Iteration 0 to Final Result", 
                fontsize=14, fontweight='bold')
    
    plt.show()


def example_3_detailed_learning():
    """
    Example 3: Learn how one specific algorithm works
    Focus on PSO with detailed explanation
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Detailed Learning - Let's understand PSO")
    print("="*60)
    
    env = create_environment()
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    
    # Enable tracking
    pso.track_history = True
    success = pso.find_path()
    
    if hasattr(pso, 'position_history') and len(pso.position_history) > 0:
        print(f"\nPSO found {'a good solution!' if success else 'no solution'}")
        print(f"Total iterations: {len(pso.position_history)}")
        print(f"Final best score: {pso.gbest_score:.2f}")
        
        # Show detailed analysis of specific iterations
        history = pso.position_history
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle("PSO Detailed Analysis: Understanding Particle Movement", 
                    fontsize=14, fontweight='bold')
        
        # Select key iterations
        key_iterations = [
            (0, "Iteration 1: Swarm initialized at random positions"),
            (len(history)//4, f"Iteration {len(history)//4}: Early exploration phase"),
            (len(history)//2, f"Iteration {len(history)//2}: Mid-process convergence"),
            (3*len(history)//4, f"Iteration {3*len(history)//4}: Approaching goal"),
            (len(history)-1, f"Final iteration: Converged solution"),
        ]
        
        axes = axes.flatten()
        for plot_idx, (hist_idx, title) in enumerate(key_iterations):
            if plot_idx >= len(axes):
                break
            
            ax = axes[plot_idx]
            snapshot = history[hist_idx]
            
            # Draw environment
            ax.set_xlim(0, env.width)
            ax.set_ylim(0, env.height)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2)
            
            # Draw obstacles
            from matplotlib.patches import Rectangle, Circle
            for obstacle in env.obstacles:
                if obstacle['type'] == 'rectangle':
                    rect = Rectangle((obstacle['x'], obstacle['y']), 
                                   obstacle['width'], obstacle['height'],
                                   fill=True, facecolor='red', edgecolor='darkred',
                                   alpha=0.7, linewidth=2)
                    ax.add_patch(rect)
                elif obstacle['type'] == 'circle':
                    circle = Circle((obstacle['x'], obstacle['y']), 
                                  obstacle['radius'],
                                  fill=True, facecolor='red', edgecolor='darkred',
                                  alpha=0.7, linewidth=2)
                    ax.add_patch(circle)
            
            # Draw start and goal
            ax.plot(env.start[0], env.start[1], 'go', markersize=12, label='Start', zorder=5)
            ax.plot(env.goal[0], env.goal[1], 'b*', markersize=18, label='Goal', zorder=5)
            
            # Draw particles
            particles = np.array(snapshot.get('particles', []))
            gbest = snapshot.get('gbest_position', None)
            
            if len(particles) > 0:
                ax.scatter(particles[:, 0], particles[:, 1], c='cyan', s=60,
                          alpha=0.7, label='Particles', edgecolors='blue', linewidth=0.5)
            
            if gbest is not None:
                ax.scatter(gbest[0], gbest[1], c='yellow', s=200, marker='*',
                          alpha=0.9, label='Global Best', edgecolors='orange', linewidth=2)
            
            ax.set_title(title, fontsize=10)
            ax.legend(loc='upper right', fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
        
        # Hide extra subplots
        for i in range(5, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
    
    plt.show()


def example_4_convergence_analysis():
    """
    Example 4: Analyze convergence behavior of each algorithm
    Show how quickly each algorithm improves over iterations
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Convergence Analysis")
    print("="*60)
    
    env = create_environment()
    
    algorithms = {
        "A*": AStarPathfinder(env, grid_step=2.0),
        "PSO": PSOPathfinder(env, num_particles=30, max_iterations=200),
        "SA": SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500),
        "GWO": GWOPathfinder(env, num_wolves=30, max_iterations=200),
        "GA": GAPathfinder(env, population_size=30, max_iterations=200)
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Algorithm Convergence: Best Score Over Iterations", 
                fontsize=14, fontweight='bold')
    axes = axes.flatten()
    
    for idx, (name, algo) in enumerate(algorithms.items()):
        ax = axes[idx]
        
        print(f"Running {name} with history tracking...")
        algo.track_history = True
        success = algo.find_path()
        
        # Extract convergence data
        if hasattr(algo, 'position_history') and len(algo.position_history) > 0:
            history = algo.position_history
            iterations = [h.get('iteration', i) for i, h in enumerate(history)]
            scores = [h.get('best_score', float('inf')) for h in history]
            
            ax.plot(iterations, scores, 'b-', linewidth=2, label='Best Score')
            ax.scatter(iterations, scores, c='blue', s=20, alpha=0.6)
            
            # Add threshold line (close to goal)
            ax.axhline(y=5, color='green', linestyle='--', linewidth=2, label='Goal threshold (5)')
            
            ax.set_xlabel('Iteration', fontsize=10)
            ax.set_ylabel('Best Score (Distance to Goal)', fontsize=10)
            ax.set_title(f"{name}: Convergence\nFinal: {scores[-1]:.2f}", fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_ylim(bottom=0)
        else:
            ax.text(0.5, 0.5, f"No history\nfor {name}", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(name)
    
    # Hide extra subplot
    axes[-1].set_visible(False)
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    """
    Run visualization examples
    Choose which example to run by uncommenting
    """
    
    # Run example 1: Individual algorithm progress
    example_1_individual_algorithm_progress()
    
    # Run example 2: Algorithm comparison
    example_2_algorithm_comparison()
    
    # Run example 3: Detailed learning (PSO)
    example_3_detailed_learning()
    
    # Run example 4: Convergence analysis
    example_4_convergence_analysis()
    
    print("\n" + "="*60)
    print("All visualization examples completed!")
    print("="*60)
