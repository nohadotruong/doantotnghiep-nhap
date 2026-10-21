"""
Advanced examples and utilities for TSP-PSO solver
"""

import numpy as np
from tsp_pso import TSPProblem, PSO, generate_cities, plot_solution, plot_convergence
import json


def run_multiple_trials(n_cities: int = 30, n_trials: int = 5, 
                       n_particles: int = 50, max_iterations: int = 500) -> dict:
    """
    Run PSO multiple times to get statistics
    
    Args:
        n_cities: Number of cities
        n_trials: Number of trials
        n_particles: Number of particles per trial
        max_iterations: Maximum iterations per trial
        
    Returns:
        Dictionary with statistics
    """
    results = []
    
    for trial in range(n_trials):
        print(f"\n{'='*60}")
        print(f"Trial {trial + 1}/{n_trials}")
        print(f"{'='*60}")
        
        cities = generate_cities(n_cities, seed=trial)
        problem = TSPProblem(cities)
        
        pso = PSO(problem, n_particles=n_particles, max_iterations=max_iterations)
        best_tour, best_distance, _ = pso.solve()
        
        results.append({
            'trial': trial + 1,
            'best_distance': best_distance,
            'tour': best_tour
        })
        
        print(f"Best distance: {best_distance:.2f}")
    
    # Statistics
    distances = [r['best_distance'] for r in results]
    stats = {
        'n_cities': n_cities,
        'n_trials': n_trials,
        'n_particles': n_particles,
        'max_iterations': max_iterations,
        'min_distance': min(distances),
        'max_distance': max(distances),
        'mean_distance': np.mean(distances),
        'std_distance': np.std(distances),
        'results': results
    }
    
    return stats


def solve_custom_cities(cities_file: str = None) -> tuple:
    """
    Solve TSP from a custom cities file
    
    File format: JSON with array of [x, y] coordinates
    Example:
    [[0, 0], [10, 10], [20, 5], ...]
    
    Args:
        cities_file: Path to JSON file with cities
        
    Returns:
        Tuple of (best_tour, best_distance)
    """
    if cities_file is None:
        # Create example file
        example_cities = np.random.uniform(0, 100, size=(15, 2)).tolist()
        cities_file = 'cities.json'
        with open(cities_file, 'w') as f:
            json.dump(example_cities, f, indent=2)
        print(f"Created example cities file: {cities_file}")
    else:
        with open(cities_file, 'r') as f:
            example_cities = json.load(f)
    
    cities = np.array(example_cities)
    print(f"\nLoaded {len(cities)} cities from {cities_file}")
    
    problem = TSPProblem(cities)
    pso = PSO(problem, n_particles=40, max_iterations=500)
    best_tour, best_distance, _ = pso.solve()
    
    print(f"Best distance: {best_distance:.2f}")
    print(f"Best tour: {best_tour}")
    
    return best_tour, best_distance


def compare_parameters(n_cities: int = 20, n_particles_list: list = None, 
                      max_iterations: int = 500):
    """
    Compare PSO performance with different particle counts
    
    Args:
        n_cities: Number of cities
        n_particles_list: List of particle counts to test
        max_iterations: Maximum iterations
    """
    if n_particles_list is None:
        n_particles_list = [10, 20, 30, 50]
    
    cities = generate_cities(n_cities, seed=42)
    problem = TSPProblem(cities)
    
    results = {}
    
    for n_particles in n_particles_list:
        print(f"\nTesting with {n_particles} particles...")
        pso = PSO(problem, n_particles=n_particles, max_iterations=max_iterations)
        _, best_distance, _ = pso.solve()
        results[n_particles] = best_distance
        print(f"Result: {best_distance:.2f}")
    
    print(f"\n{'='*60}")
    print("Summary:")
    for n_particles, distance in sorted(results.items()):
        print(f"  {n_particles} particles: {distance:.2f}")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    # Example 1: Multiple trials
    print("\n" + "="*60)
    print("EXAMPLE 1: Multiple Trials with Statistics")
    print("="*60)
    stats = run_multiple_trials(n_cities=20, n_trials=3, n_particles=30)
    print(f"\nStatistics:")
    print(f"  Min distance: {stats['min_distance']:.2f}")
    print(f"  Max distance: {stats['max_distance']:.2f}")
    print(f"  Mean distance: {stats['mean_distance']:.2f}")
    print(f"  Std deviation: {stats['std_distance']:.2f}")
    
    # Example 2: Parameter comparison
    print("\n" + "="*60)
    print("EXAMPLE 2: Parameter Comparison")
    print("="*60)
    compare_parameters(n_cities=15, n_particles_list=[10, 20, 30, 40])
    
    # Example 3: Custom cities
    print("\n" + "="*60)
    print("EXAMPLE 3: Solving with Custom Cities")
    print("="*60)
    solve_custom_cities()
