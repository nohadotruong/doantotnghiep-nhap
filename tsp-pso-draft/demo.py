"""
Demo script - Various use cases and examples for TSP-PSO solver
"""

import numpy as np
from tsp_pso import TSPProblem, PSO, generate_cities, plot_solution, plot_convergence
from config import get_preset, list_presets, create_pso_with_preset
import matplotlib.pyplot as plt


def demo_1_basic_usage():
    """Demo 1: Basic usage - solve a simple TSP"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage - Simple 20-City TSP")
    print("="*70)
    
    # Generate cities
    cities = generate_cities(n_cities=20, seed=42)
    problem = TSPProblem(cities)
    
    print(f"Problem: {len(cities)} cities in 2D space")
    print(f"Search space: [0, 100] x [0, 100]")
    
    # Create PSO solver
    pso = PSO(problem, n_particles=30, max_iterations=500)
    
    # Solve
    print("\nSolving...")
    best_tour, best_distance, history = pso.solve()
    
    print(f"\nResults:")
    print(f"  Best tour: {best_tour}")
    print(f"  Best distance: {best_distance:.2f}")
    print(f"  Initial distance: {history[0]:.2f}")
    print(f"  Improvement: {history[0] - best_distance:.2f} ({100*(history[0]-best_distance)/history[0]:.1f}%)")
    
    # Visualize
    try:
        plot_solution(problem, best_tour, f"Demo 1: Basic TSP (Distance: {best_distance:.2f})")
        plot_convergence(history)
    except:
        print("  (Visualization skipped - matplotlib display not available)")


def demo_2_different_sizes():
    """Demo 2: Solve TSPs of different sizes"""
    print("\n" + "="*70)
    print("DEMO 2: Different Problem Sizes")
    print("="*70)
    
    sizes = [10, 20, 30, 40]
    results = {}
    
    for size in sizes:
        print(f"\nSolving TSP with {size} cities...")
        cities = generate_cities(size, seed=42)
        problem = TSPProblem(cities)
        
        pso = PSO(problem, n_particles=30, max_iterations=500)
        _, best_distance, _ = pso.solve()
        
        results[size] = best_distance
        print(f"  Distance: {best_distance:.2f}")
    
    # Plot results
    try:
        plt.figure(figsize=(10, 6))
        sizes_list = list(results.keys())
        distances_list = list(results.values())
        plt.plot(sizes_list, distances_list, 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Number of Cities')
        plt.ylabel('Best Distance Found')
        plt.title('TSP Solution Quality vs Problem Size')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    except:
        print("  (Plot skipped - matplotlib display not available)")


def demo_3_presets():
    """Demo 3: Using configuration presets"""
    print("\n" + "="*70)
    print("DEMO 3: Using Configuration Presets")
    print("="*70)
    
    # List all presets
    list_presets()
    
    # Solve same problem with different presets
    cities = generate_cities(n_cities=15, seed=42)
    problem = TSPProblem(cities)
    
    preset_names = ['quick', 'balanced', 'thorough']
    results = {}
    
    for preset_name in preset_names:
        print(f"\nSolving with '{preset_name}' preset...")
        pso = create_pso_with_preset(problem, preset_name)
        _, best_distance, history = pso.solve()
        results[preset_name] = {
            'distance': best_distance,
            'history': history
        }
        print(f"  Best distance: {best_distance:.2f}")
    
    # Compare presets
    print(f"\n{'Preset':<15} {'Distance':<12} {'Time Complexity':<15}")
    print("-" * 42)
    for preset_name in preset_names:
        result = results[preset_name]
        config = get_preset(preset_name)
        complexity = config.n_particles * config.max_iterations
        print(f"{preset_name:<15} {result['distance']:<12.2f} {complexity:<15,}")


def demo_4_compare_parameters():
    """Demo 4: Compare different parameters"""
    print("\n" + "="*70)
    print("DEMO 4: Parameter Sensitivity Analysis")
    print("="*70)
    
    cities = generate_cities(n_cities=12, seed=42)
    problem = TSPProblem(cities)
    
    # Test different particle counts
    print("\n1. Effect of particle count:")
    print("-" * 50)
    n_particles_list = [10, 20, 30, 50, 80]
    results_particles = {}
    
    for n_particles in n_particles_list:
        print(f"  Testing {n_particles} particles...", end=' ')
        pso = PSO(problem, n_particles=n_particles, max_iterations=300)
        _, distance, _ = pso.solve()
        results_particles[n_particles] = distance
        print(f"Distance: {distance:.2f}")
    
    # Test different iterations
    print("\n2. Effect of iteration count:")
    print("-" * 50)
    iterations_list = [100, 200, 500, 1000]
    results_iterations = {}
    
    for max_iter in iterations_list:
        print(f"  Testing {max_iter} iterations...", end=' ')
        pso = PSO(problem, n_particles=30, max_iterations=max_iter)
        _, distance, _ = pso.solve()
        results_iterations[max_iter] = distance
        print(f"Distance: {distance:.2f}")
    
    # Summary
    print("\n3. Summary:")
    print("-" * 50)
    print(f"  Best with particles: {min(results_particles, key=results_particles.get)} " +
          f"({results_particles[min(results_particles, key=results_particles.get)]:.2f})")
    print(f"  Best with iterations: {min(results_iterations, key=results_iterations.get)} " +
          f"({results_iterations[min(results_iterations, key=results_iterations.get)]:.2f})")


def demo_5_convergence_analysis():
    """Demo 5: Analyze convergence behavior"""
    print("\n" + "="*70)
    print("DEMO 5: Convergence Analysis")
    print("="*70)
    
    cities = generate_cities(n_cities=20, seed=42)
    problem = TSPProblem(cities)
    
    # Run with different w (inertia) values
    w_values = [0.4, 0.7, 0.9]
    results = {}
    
    for w in w_values:
        print(f"\nSolving with w={w} (inertia weight)...")
        pso = PSO(problem, n_particles=30, max_iterations=500, w=w)
        _, distance, history = pso.solve()
        results[w] = {
            'distance': distance,
            'history': history
        }
        print(f"  Final distance: {distance:.2f}")
    
    # Plot convergence curves
    try:
        plt.figure(figsize=(12, 6))
        for w, result in results.items():
            plt.plot(result['history'], label=f'w={w}', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Best Distance')
        plt.title('Effect of Inertia Weight on Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    except:
        print("  (Plot skipped - matplotlib display not available)")


def demo_6_statistical_analysis():
    """Demo 6: Run multiple trials and analyze statistics"""
    print("\n" + "="*70)
    print("DEMO 6: Statistical Analysis - Multiple Runs")
    print("="*70)
    
    cities = generate_cities(n_cities=15, seed=42)
    problem = TSPProblem(cities)
    
    n_trials = 10
    results = []
    
    print(f"\nRunning {n_trials} trials with same problem...")
    for trial in range(n_trials):
        pso = PSO(problem, n_particles=30, max_iterations=500)
        _, distance, _ = pso.solve()
        results.append(distance)
        print(f"  Trial {trial+1:2d}: {distance:7.2f}")
    
    # Statistics
    results = np.array(results)
    print(f"\n{'Statistics':^50}")
    print("-" * 50)
    print(f"  Best result:      {results.min():.2f}")
    print(f"  Worst result:     {results.max():.2f}")
    print(f"  Mean:             {results.mean():.2f}")
    print(f"  Std deviation:    {results.std():.2f}")
    print(f"  Range:            {results.max() - results.min():.2f}")
    print(f"  Coefficient of variation: {results.std()/results.mean():.2%}")


def demo_7_algorithm_comparison():
    """Demo 7: Compare PSO with other heuristics (e.g., random, greedy nearest neighbor)"""
    print("\n" + "="*70)
    print("DEMO 7: Benchmark - PSO vs Other Heuristics")
    print("="*70)
    
    cities = generate_cities(n_cities=20, seed=42)
    problem = TSPProblem(cities)
    
    # Random solution
    print("\n1. Random solution:")
    random_tour = np.random.permutation(len(cities)).tolist()
    random_distance = problem.calculate_tour_distance(random_tour)
    print(f"  Distance: {random_distance:.2f}")
    
    # Simple nearest neighbor
    print("\n2. Nearest Neighbor (greedy):")
    nn_tour = nearest_neighbor(cities)
    nn_distance = problem.calculate_tour_distance(nn_tour)
    print(f"  Distance: {nn_distance:.2f}")
    
    # PSO solution
    print("\n3. Particle Swarm Optimization:")
    pso = PSO(problem, n_particles=30, max_iterations=500)
    pso_tour, pso_distance, _ = pso.solve()
    print(f"  Distance: {pso_distance:.2f}")
    
    # Comparison
    print(f"\n{'Comparison':^50}")
    print("-" * 50)
    print(f"  Random:        {random_distance:7.2f} (baseline)")
    print(f"  Nearest Neigh: {nn_distance:7.2f}" +
          f" ({100*(nn_distance-random_distance)/random_distance:+.1f}%)")
    print(f"  PSO:           {pso_distance:7.2f}" +
          f" ({100*(pso_distance-random_distance)/random_distance:+.1f}%)")
    
    improvement = (nn_distance - pso_distance) / nn_distance * 100
    print(f"\n  PSO improvement over NN: {improvement:.1f}%")


def nearest_neighbor(cities: np.ndarray) -> list:
    """Simple nearest neighbor heuristic"""
    n = len(cities)
    unvisited = set(range(n))
    current = 0
    tour = [current]
    unvisited.remove(current)
    
    while unvisited:
        nearest = min(unvisited, 
                     key=lambda city: np.linalg.norm(cities[current] - cities[city]))
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("TSP-PSO Solver - Comprehensive Demo Suite")
    print("="*70)
    
    demos = [
        ("Basic Usage", demo_1_basic_usage),
        ("Different Sizes", demo_2_different_sizes),
        ("Configuration Presets", demo_3_presets),
        ("Parameter Analysis", demo_4_compare_parameters),
        ("Convergence Analysis", demo_5_convergence_analysis),
        ("Statistical Analysis", demo_6_statistical_analysis),
        ("Algorithm Comparison", demo_7_algorithm_comparison),
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all demos...\n")
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n  Error in {name}: {e}")
    
    print("\n" + "="*70)
    print("Demo Suite Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
