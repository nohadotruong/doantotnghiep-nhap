import numpy as np
import matplotlib.pyplot as plt
import time
from utils.environment import UAVEnvironment
from utils.visualize_progress import visualize_algorithm_progress
from algorithms import (
    AStarPathfinder,
    PSOPathfinder,
    SAPathfinder,
    GWOPathfinder,
    GAPathfinder
)


def create_environment():
    """Create UAV environment with random obstacles"""
    env = UAVEnvironment(width=100, height=100)
    
    # Generate 5 random obstacles
    env.simple_map(num_obstacles=5, seed=42)
    
    env.set_start_goal(
        start=(5, 5),
        goal=(95, 95)
    )
    
    return env


def run_algorithm(algorithm_name, algorithm, env):
    """Run one algorithm and measure execution time"""
    print(f"\n{'='*50}")
    print(f"Running algorithm: {algorithm_name}")
    print(f"{'='*50}")
    
    start_time = time.time()
    success = algorithm.find_path()
    elapsed_time = time.time() - start_time
    
    if success:
        stats = algorithm.get_statistics()
        path = algorithm.get_path()
        
        print(f"[OK] Path found")
        print(f"  - Time: {elapsed_time:.4f} seconds")
        print(f"  - Distance: {stats.get('distance', 0):.2f}")
        print(f"  - Waypoints: {stats.get('num_waypoints', 0)}")
        
        if 'best_score' in stats:
            print(f"  - Best score: {stats['best_score']:.2f}")
        if 'convergence_iteration' in stats:
            print(f"  - Convergence at iteration: {stats['convergence_iteration']}")
        if 'convergence_generation' in stats:
            print(f"  - Convergence at generation: {stats['convergence_generation']}")
        
        return {
            'algorithm': algorithm_name,
            'success': True,
            'time': elapsed_time,
            'distance': stats.get('distance', 0),
            'num_waypoints': stats.get('num_waypoints', 0),
            'path': path,
            'stats': stats
        }
    else:
        print(f"[FAIL] No path found")
        return {
            'algorithm': algorithm_name,
            'success': False,
            'time': elapsed_time,
            'distance': float('inf'),
            'num_waypoints': 0,
            'path': None
        }


def visualize_results(env, results):
    """Visualize results of all algorithms"""
    successful_results = [r for r in results if r['success']]
    num_plots = min(len(successful_results), 6)
    
    if num_plots == 0:
        print("\nNo successful algorithms!")
        return
    
    if num_plots <= 3:
        rows, cols = 1, num_plots
    else:
        rows = 2
        cols = (num_plots + 1) // 2
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
    if num_plots == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    from matplotlib.patches import Rectangle, Circle
    
    for i, result in enumerate(successful_results[:num_plots]):
        ax = axes[i]
        
        ax.set_xlim(0, env.width)
        ax.set_ylim(0, env.height)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{result['algorithm']}\nDistance: {result['distance']:.2f}")
        
        for obstacle in env.obstacles:
            if obstacle['type'] == 'rectangle':
                rect = Rectangle(
                    (obstacle['x'], obstacle['y']),
                    obstacle['width'],
                    obstacle['height'],
                    fill=True, facecolor='red', edgecolor='darkred',
                    alpha=0.7, linewidth=2
                )
                ax.add_patch(rect)
            elif obstacle['type'] == 'circle':
                circle = Circle(
                    (obstacle['x'], obstacle['y']),
                    obstacle['radius'],
                    fill=True, facecolor='red', edgecolor='darkred',
                    alpha=0.7, linewidth=2
                )
                ax.add_patch(circle)
        
        ax.plot(env.start[0], env.start[1], 'go', markersize=12, label='Start')
        ax.plot(env.goal[0], env.goal[1], 'b*', markersize=18, label='Goal')
        
        if result['path']:
            path = np.array(result['path'])
            ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, alpha=0.7)
            ax.plot(path[:, 0], path[:, 1], 'bo', markersize=3, alpha=0.5)
        
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    for i in range(num_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig


def print_comparison_table(results):
    """Print algorithm comparison table"""
    print(f"\n\n{'='*80}")
    print("ALGORITHM COMPARISON TABLE")
    print(f"{'='*80}")
    
    print(f"{'Algorithm':<15} {'Success':<10} {'Time (s)':<15} {'Distance':<15} {'Waypoints':<10}")
    print(f"{'-'*80}")
    
    for result in results:
        distance_str = f"{result['distance']:.2f}" if result['distance'] != float('inf') else "N/A"
        waypoints_str = str(result['num_waypoints']) if result['num_waypoints'] > 0 else "N/A"
        success = "OK" if result['success'] else "FAIL"
        
        print(f"{result['algorithm']:<15} {success:<10} {result['time']:<15.4f} {distance_str:<15} {waypoints_str:<10}")
    
    print(f"{'='*80}\n")


def main():
    """Main function"""
    print("\n" + "="*80)
    print("UAV PATHFINDING - ALGORITHM COMPARISON")
    print("="*80)
    
    print("\n[1] Creating environment...")
    env = create_environment()
    print("    [OK] Created 100x100 map with 5 obstacles")
    
    print("\n[2] Running algorithms...")
    results = []
    
    astar = AStarPathfinder(env, grid_step=2.0)
    results.append(run_algorithm("A*", astar, env))
    
    pso = PSOPathfinder(env, num_particles=30, max_iterations=200)
    results.append(run_algorithm("PSO", pso, env))
    
    sa = SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500)
    results.append(run_algorithm("SA", sa, env))
    
    gwo = GWOPathfinder(env, num_wolves=30, max_iterations=200)
    results.append(run_algorithm("GWO", gwo, env))
    
    ga = GAPathfinder(env, population_size=30, max_iterations=200)
    results.append(run_algorithm("GA", ga, env))
    
    print_comparison_table(results)
    
    print("[3] Visualizing results...")
    fig = visualize_results(env, results)
    
    env_fig, _ = env.visualize(title="Environment Map")
    
    plt.show()
    
    print("\n[OK] Completed!")
    
    # Optional: Show detailed progress of one algorithm
    print("\n\n" + "="*80)
    print("BONUS: Detailed Algorithm Progress Visualization")
    print("="*80)
    print("\nGenerating detailed progress visualization of one algorithm...")
    print("This shows 5 snapshots of how the algorithm explores the space\n")
    
    # Choose one algorithm to visualize in detail (PSO in this example)
    choice = input("Which algorithm to visualize in detail? (pso/astar/sa/gwo/ga) [default: pso]: ").strip().lower()
    
    if choice == "astar":
        algo_detail = AStarPathfinder(env, grid_step=2.0)
        algo_name = "A*"
    elif choice == "sa":
        algo_detail = SAPathfinder(env, initial_temp=100, cooling_rate=0.95, max_iterations=500)
        algo_name = "SA"
    elif choice == "gwo":
        algo_detail = GWOPathfinder(env, num_wolves=30, max_iterations=200)
        algo_name = "GWO"
    elif choice == "ga":
        algo_detail = GAPathfinder(env, population_size=30, max_iterations=200)
        algo_name = "GA"
    else:  # Default to PSO
        algo_detail = PSOPathfinder(env, num_particles=30, max_iterations=200)
        algo_name = "PSO"
    
    print(f"\nGenerating {algo_name} progress visualization (this may take a moment)...")
    fig_detail = visualize_algorithm_progress(env, algo_detail, algo_name, num_snapshots=6)
    
    if fig_detail:
        fig_detail.suptitle(f"{algo_name} Algorithm Progress: Step-by-step Pathfinding", 
                           fontsize=14, fontweight='bold')
        print(f"[OK] {algo_name} detailed visualization generated!")
        print("\nVisualization shows how the algorithm searches for the path:")
        print("- Left to right: Progress from iteration 0 to final result")
        print("- Colors represent different algorithm states")
        print("\nShowing visualization...")
        plt.show()
    else:
        print(f"Could not generate visualization for {algo_name}")


if __name__ == "__main__":
    main()
