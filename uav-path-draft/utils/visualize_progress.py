"""
Module for visualization of algorithm progress - showing step-by-step execution
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from typing import List, Dict


def visualize_algorithm_progress(env, algorithm, algorithm_name, num_snapshots=5):
    """
    Visualize algorithm progress with multiple snapshots during execution
    
    Args:
        env: UAV Environment
        algorithm: Algorithm instance with tracking enabled
        algorithm_name: Name of algorithm (A*, PSO, SA, GWO, GA)
        num_snapshots: Number of progress snapshots to show
    """
    
    # Run algorithm while tracking history
    algorithm.track_history = True
    success = algorithm.find_path()
    
    if not hasattr(algorithm, 'position_history') or len(algorithm.position_history) == 0:
        print(f"[Warning] No history tracking for {algorithm_name}")
        return None
    
    history = algorithm.position_history
    total_steps = len(history)
    
    # Select snapshots at regular intervals
    if total_steps <= num_snapshots:
        snapshot_indices = list(range(total_steps))
    else:
        snapshot_indices = [int(i * (total_steps - 1) / (num_snapshots - 1)) 
                           for i in range(num_snapshots)]
    
    # Add final result
    if snapshot_indices[-1] != total_steps - 1:
        snapshot_indices.append(total_steps - 1)
    
    num_plots = len(snapshot_indices)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, (num_plots + 1) // 2, figsize=(5 * ((num_plots + 1) // 2), 10))
    if num_plots == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Draw each snapshot
    for plot_idx, hist_idx in enumerate(snapshot_indices):
        ax = axes[plot_idx]
        snapshot = history[hist_idx]
        
        # Setup map
        ax.set_xlim(0, env.width)
        ax.set_ylim(0, env.height)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Draw obstacles
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
        
        # Draw start and goal
        ax.plot(env.start[0], env.start[1], 'go', markersize=12, label='Start', zorder=5)
        ax.plot(env.goal[0], env.goal[1], 'b*', markersize=18, label='Goal', zorder=5)
        
        # Algorithm-specific visualization
        if algorithm_name == "PSO":
            _visualize_pso_snapshot(ax, snapshot, algorithm_name)
        elif algorithm_name == "A*":
            _visualize_astar_snapshot(ax, snapshot, algorithm_name)
        elif algorithm_name == "SA":
            _visualize_sa_snapshot(ax, snapshot, algorithm_name)
        elif algorithm_name == "GWO":
            _visualize_gwo_snapshot(ax, snapshot, algorithm_name)
        elif algorithm_name == "GA":
            _visualize_ga_snapshot(ax, snapshot, algorithm_name)
        
        # Set title with iteration info
        iteration = snapshot.get('iteration', 0)
        score = snapshot.get('best_score', 0)
        ax.set_title(f"{algorithm_name} - Iteration {iteration}\nBest Score: {score:.2f}", fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    # Hide unused subplots
    for i in range(len(snapshot_indices), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig


def _visualize_pso_snapshot(ax, snapshot, name):
    """Visualize PSO particles at current iteration"""
    
    particles = snapshot.get('particles', [])
    pbest = snapshot.get('pbest_positions', [])
    gbest = snapshot.get('gbest_position', None)
    
    # Draw particles (current positions)
    if len(particles) > 0:
        particles = np.array(particles)
        ax.scatter(particles[:, 0], particles[:, 1], c='cyan', s=50, 
                  alpha=0.6, label='Particles', edgecolors='blue', linewidth=0.5)
    
    # Draw personal bests
    if len(pbest) > 0:
        pbest = np.array(pbest)
        ax.scatter(pbest[:, 0], pbest[:, 1], c='lightgreen', s=30, 
                  alpha=0.4, label='Personal Best', marker='^', edgecolors='green')
    
    # Draw global best
    if gbest is not None:
        ax.scatter(gbest[0], gbest[1], c='yellow', s=200, 
                  alpha=0.9, label='Global Best', marker='*', edgecolors='orange', linewidth=2)
    
    # Draw velocity vectors for first 5 particles
    if len(particles) > 0 and 'velocities' in snapshot:
        velocities = snapshot.get('velocities', [])
        for i in range(min(5, len(particles))):
            if i < len(velocities):
                vel = velocities[i]
                ax.arrow(particles[i][0], particles[i][1], vel[0], vel[1],
                        head_width=1, head_length=0.5, fc='lightblue', ec='blue', alpha=0.3)


def _visualize_astar_snapshot(ax, snapshot, name):
    """Visualize A* explored nodes"""
    
    # Draw closed set (already explored)
    closed_set = snapshot.get('closed_set', [])
    if len(closed_set) > 0:
        closed_set = np.array(closed_set)
        ax.scatter(closed_set[:, 0], closed_set[:, 1], c='lightpink', s=20,
                  alpha=0.4, label='Explored', edgecolors='red')
    
    # Draw open set (frontier)
    open_set = snapshot.get('open_set', [])
    if len(open_set) > 0:
        open_set = np.array(open_set)
        ax.scatter(open_set[:, 0], open_set[:, 1], c='yellow', s=30,
                  alpha=0.6, label='Frontier', edgecolors='orange')
    
    # Draw current path
    current_path = snapshot.get('current_path', [])
    if len(current_path) > 0:
        current_path = np.array(current_path)
        ax.plot(current_path[:, 0], current_path[:, 1], 'g--', linewidth=1.5, alpha=0.7)


def _visualize_sa_snapshot(ax, snapshot, name):
    """Visualize SA current solution and neighborhood"""
    
    current = snapshot.get('current', None)
    best = snapshot.get('best', None)
    temperature = snapshot.get('temperature', 0)
    
    # Draw current solution
    if current is not None and len(current) > 1:
        current = np.array(current)
        ax.plot(current[:, 0], current[:, 1], 'r-', linewidth=1.5, alpha=0.7, label='Current')
        ax.scatter(current[0, 0], current[0, 1], c='red', s=100, marker='o', alpha=0.7)
    
    # Draw best solution
    if best is not None and len(best) > 1:
        best = np.array(best)
        ax.plot(best[:, 0], best[:, 1], 'g-', linewidth=2, alpha=0.8, label='Best')
    
    # Draw temperature info
    temp_text = f"Temp: {temperature:.2f}"
    ax.text(0.02, 0.98, temp_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


def _visualize_gwo_snapshot(ax, snapshot, name):
    """Visualize GWO wolves (alpha, beta, delta, omega)"""
    
    alpha = snapshot.get('alpha_position', None)
    beta = snapshot.get('beta_position', None)
    delta = snapshot.get('delta_position', None)
    omega_positions = snapshot.get('omega_positions', [])
    
    # Draw Omega wolves (swarm)
    if len(omega_positions) > 0:
        omega_positions = np.array(omega_positions)
        ax.scatter(omega_positions[:, 0], omega_positions[:, 1], c='lightblue', s=40,
                  alpha=0.5, label='Omega Wolves', edgecolors='blue')
    
    # Draw Delta (third best)
    if delta is not None:
        ax.scatter(delta[0], delta[1], c='orange', s=150, marker='D',
                  alpha=0.8, label='Delta', edgecolors='darkorange', linewidth=2)
    
    # Draw Beta (second best)
    if beta is not None:
        ax.scatter(beta[0], beta[1], c='purple', s=180, marker='s',
                  alpha=0.8, label='Beta', edgecolors='darkviolet', linewidth=2)
    
    # Draw Alpha (best)
    if alpha is not None:
        ax.scatter(alpha[0], alpha[1], c='red', s=250, marker='*',
                  alpha=0.9, label='Alpha', edgecolors='darkred', linewidth=2)
    
    # Draw path from best wolves
    if alpha is not None and beta is not None and delta is not None:
        best_path = np.array([alpha, beta, delta])
        ax.plot(best_path[:, 0], best_path[:, 1], 'r--', linewidth=1, alpha=0.5)


def _visualize_ga_snapshot(ax, snapshot, name):
    """Visualize GA population and best solution"""
    
    population = snapshot.get('population', [])
    best_solution = snapshot.get('best_solution', None)
    generation = snapshot.get('generation', 0)
    
    # Draw population individuals
    if len(population) > 0:
        population = np.array(population)
        for i, individual in enumerate(population):
            if len(individual) > 1:
                ax.plot(individual[:, 0], individual[:, 1], 'c-', linewidth=0.5, alpha=0.2)
            ax.scatter(individual[0, 0], individual[0, 1], c='cyan', s=20, alpha=0.3)
    
    # Draw best solution
    if best_solution is not None and len(best_solution) > 1:
        best_solution = np.array(best_solution)
        ax.plot(best_solution[:, 0], best_solution[:, 1], 'g-', linewidth=2.5, alpha=0.9, label='Best')
        ax.scatter(best_solution[:, 0], best_solution[:, 1], c='green', s=50, alpha=0.6, edgecolors='darkgreen')
    
    # Draw generation info
    gen_text = f"Gen: {generation}"
    ax.text(0.02, 0.98, gen_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))


def visualize_algorithm_comparison_detailed(env, algorithms, num_snapshots=4):
    """
    Visualize multiple algorithms in comparison with progress snapshots
    
    Args:
        env: UAV Environment
        algorithms: Dict of {name: algorithm_instance}
        num_snapshots: Number of progress snapshots to show per algorithm
    """
    
    results = {}
    for name, algo in algorithms.items():
        print(f"Tracking {name}...")
        algo.track_history = True
        success = algo.find_path()
        results[name] = {
            'algorithm': algo,
            'success': success,
            'history': getattr(algo, 'position_history', [])
        }
    
    # Create detailed comparison figure
    num_algorithms = len(algorithms)
    fig, axes = plt.subplots(num_algorithms, num_snapshots, 
                             figsize=(4*num_snapshots, 5*num_algorithms))
    
    if num_algorithms == 1:
        axes = axes.reshape(1, -1)
    
    for algo_idx, (name, result) in enumerate(results.items()):
        history = result['history']
        
        if len(history) == 0:
            continue
        
        # Select snapshots
        total_steps = len(history)
        if total_steps <= num_snapshots:
            snapshot_indices = list(range(total_steps))
        else:
            snapshot_indices = [int(i * (total_steps - 1) / (num_snapshots - 1)) 
                               for i in range(num_snapshots)]
        
        for snap_idx, hist_idx in enumerate(snapshot_indices):
            ax = axes[algo_idx, snap_idx]
            snapshot = history[hist_idx]
            
            # Setup map
            ax.set_xlim(0, env.width)
            ax.set_ylim(0, env.height)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2)
            
            # Draw obstacles
            for obstacle in env.obstacles:
                if obstacle['type'] == 'rectangle':
                    rect = Rectangle(
                        (obstacle['x'], obstacle['y']),
                        obstacle['width'],
                        obstacle['height'],
                        fill=True, facecolor='red', edgecolor='darkred',
                        alpha=0.7, linewidth=1.5
                    )
                    ax.add_patch(rect)
                elif obstacle['type'] == 'circle':
                    circle = Circle(
                        (obstacle['x'], obstacle['y']),
                        obstacle['radius'],
                        fill=True, facecolor='red', edgecolor='darkred',
                        alpha=0.7, linewidth=1.5
                    )
                    ax.add_patch(circle)
            
            # Draw start and goal
            ax.plot(env.start[0], env.start[1], 'go', markersize=10, zorder=5)
            ax.plot(env.goal[0], env.goal[1], 'b*', markersize=15, zorder=5)
            
            # Visualize specific algorithm
            if name == "PSO":
                _visualize_pso_snapshot(ax, snapshot, name)
            elif name == "A*":
                _visualize_astar_snapshot(ax, snapshot, name)
            elif name == "SA":
                _visualize_sa_snapshot(ax, snapshot, name)
            elif name == "GWO":
                _visualize_gwo_snapshot(ax, snapshot, name)
            elif name == "GA":
                _visualize_ga_snapshot(ax, snapshot, name)
            
            iteration = snapshot.get('iteration', 0)
            ax.set_title(f"{name} - Step {iteration}", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
    
    plt.tight_layout()
    return fig
