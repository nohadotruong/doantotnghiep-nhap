"""
PSO (Particle Swarm Optimization) for Path Optimization

Optimizes RRT paths by adjusting intermediate waypoints.
Optimizes 4 metrics: Length, Curvature, Straightness, Safety
"""

import numpy as np
import math
from geometry import path_length, path_curvature, path_straightness


class PSOOptimizer:
    """
    PSO-based path optimizer.
    
    Each particle represents a path with adjustable waypoints.
    Start and goal positions are fixed.
    """
    
    def __init__(self, environment, original_path,
                 num_particles=30, iterations=100,
                 w=0.7, c1=1.5, c2=1.5,
                 w_length=0.25, w_curvature=0.25, 
                 w_straightness=0.25, w_safety=0.25):
        """
        Initialize PSO optimizer.
        
        Args:
            environment: UAVEnvironment with obstacles
            original_path: Initial path [(x1,y1), ..., (xn,yn)]
            num_particles (int): number of particles, default 30
            iterations (int): optimization iterations, default 100
            w (float): inertia weight, default 0.7
            c1 (float): cognitive parameter, default 1.5
            c2 (float): social parameter, default 1.5
            w_length (float): weight for path length optimization, default 0.25
            w_curvature (float): weight for curvature optimization, default 0.25
            w_straightness (float): weight for straightness optimization, default 0.25
            w_safety (float): weight for safety optimization, default 0.25
        """
        self.environment = environment
        self.original_path = original_path
        self.num_particles = num_particles
        self.iterations = iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        # Normalize weights
        self.w_length = w_length
        self.w_curvature = w_curvature
        self.w_straightness = w_straightness
        self.w_safety = w_safety
        total = w_length + w_curvature + w_straightness + w_safety
        if not np.isclose(total, 1.0):
            self.w_length /= total
            self.w_curvature /= total
            self.w_straightness /= total
            self.w_safety /= total
        
        # Path info
        self.start = original_path[0]
        self.goal = original_path[-1]
        self.straight_line_dist = math.sqrt(
            (self.goal[0] - self.start[0])**2 + 
            (self.goal[1] - self.start[1])**2
        )
        
        # Particle swarm state
        self.particles = []
        self.velocities = []
        self.best_positions = []
        self.best_fitness = []
        self.global_best_position = None
        self.global_best_fitness = float('inf')
        
        self._init_particles()
    
    def _init_particles(self):
        """Initialize particle swarm from original path."""
        x_min, x_max = 0, self.environment.width
        y_min, y_max = 0, self.environment.height
        
        for _ in range(self.num_particles):
            # Convert path to particle (waypoints only, no start/goal)
            particle = self._path_to_particle(self.original_path)
            
            # Add small random noise
            for i in range(len(particle)):
                if i % 2 == 0:  # x coordinate
                    particle[i] += np.random.uniform(-5, 5)
                    particle[i] = np.clip(particle[i], x_min, x_max)
                else:  # y coordinate
                    particle[i] += np.random.uniform(-5, 5)
                    particle[i] = np.clip(particle[i], y_min, y_max)
            
            self.particles.append(particle)
            self.velocities.append(np.random.uniform(-1, 1, len(particle)))
            self.best_positions.append(particle.copy())
            
            fitness = self._fitness(particle)
            self.best_fitness.append(fitness)
        
        # Find global best
        best_idx = np.argmin(self.best_fitness)
        self.global_best_position = self.best_positions[best_idx].copy()
        self.global_best_fitness = self.best_fitness[best_idx]
    
    def _path_to_particle(self, path):
        """Convert path to particle representation (waypoints only)."""
        particle = []
        for i in range(1, len(path) - 1):
            particle.append(path[i][0])
            particle.append(path[i][1])
        return np.array(particle, dtype=float)
    
    def _particle_to_path(self, particle):
        """Convert particle back to path."""
        path = [self.start]
        for i in range(0, len(particle), 2):
            path.append((particle[i], particle[i + 1]))
        path.append(self.goal)
        return path
    
    def _fitness(self, particle):
        """
        Calculate fitness (weighted combination of 4 metrics).
        
        Lower fitness = better path.
        """
        path = self._particle_to_path(particle)
        
        # 1. Length (shorter is better)
        length = path_length(path)
        length_norm = min(1.0, self.straight_line_dist / length) if length > 0 else 0
        
        # 2. Curvature (less curved is better)
        curvature = path_curvature(path)
        curvature_norm = 1.0 / (1.0 + curvature)
        
        # 3. Straightness (more straight is better)
        straightness = path_straightness(path)
        straightness_norm = 1.0 / (1.0 + straightness)
        
        # 4. Safety (no collisions is better)
        collision_count = sum(1 for i in range(len(path) - 1)
                            if self.environment.is_collision(path[i], path[i + 1]))
        
        if collision_count > 0:
            safety_norm = 0
        else:
            min_dist = self._min_distance_to_obstacles(path)
            safety_norm = min(1.0, min_dist / 10.0)
        
        # Combine metrics
        fitness = (
            self.w_length * (1 - length_norm) +
            self.w_curvature * (1 - curvature_norm) +
            self.w_straightness * (1 - straightness_norm) +
            self.w_safety * (1 - safety_norm)
        )
        
        return fitness
    
    def _min_distance_to_obstacles(self, path):
        """Calculate minimum distance from any path point to obstacles."""
        if not self.environment.obstacles:
            return float('inf')
        
        min_dist = float('inf')
        
        for x, y in path:
            for ox, oy, ow, oh in self.environment.obstacles:
                # Distance from point to rectangle
                dist_x = max(ox - x, 0, x - (ox + ow))
                dist_y = max(oy - y, 0, y - (oy + oh))
                dist = math.sqrt(dist_x**2 + dist_y**2)
                min_dist = min(min_dist, dist)
        
        return min_dist
    
    def _clip_position(self, position):
        """Keep particle within map bounds."""
        for i in range(len(position)):
            if i % 2 == 0:  # x
                position[i] = np.clip(position[i], 0, self.environment.width)
            else:  # y
                position[i] = np.clip(position[i], 0, self.environment.height)
        return position
    
    def optimize(self):
        """
        Run PSO optimization.
        
        Returns:
            list: optimized path [(x1,y1), ..., (xn,yn)]
        """
        print(f"[PSO] Starting optimization ({self.iterations} iterations)...")
        print(f"[PSO] Weights: L={self.w_length*100:.0f}%, C={self.w_curvature*100:.0f}%, "
              f"S={self.w_straightness*100:.0f}%, Sf={self.w_safety*100:.0f}%")
        print(f"[PSO] Initial fitness: {self.global_best_fitness:.4f}")
        
        for iteration in range(self.iterations):
            for i in range(self.num_particles):
                # Update velocity
                r1 = np.random.random(len(self.particles[i]))
                r2 = np.random.random(len(self.particles[i]))
                
                cognitive = self.c1 * r1 * (self.best_positions[i] - self.particles[i])
                social = self.c2 * r2 * (self.global_best_position - self.particles[i])
                
                self.velocities[i] = (self.w * self.velocities[i] + 
                                     cognitive + social)
                
                # Update position
                self.particles[i] = self.particles[i] + self.velocities[i]
                self.particles[i] = self._clip_position(self.particles[i])
                
                # Evaluate fitness
                fitness = self._fitness(self.particles[i])
                
                # Update personal best
                if fitness < self.best_fitness[i]:
                    self.best_fitness[i] = fitness
                    self.best_positions[i] = self.particles[i].copy()
                    
                    # Update global best
                    if fitness < self.global_best_fitness:
                        self.global_best_fitness = fitness
                        self.global_best_position = self.particles[i].copy()
            
            # Progress report
            if (iteration + 1) % max(1, self.iterations // 5) == 0:
                print(f"[PSO] Iteration {iteration + 1}/{self.iterations}: "
                      f"Fitness = {self.global_best_fitness:.4f}")
        
        print(f"[PSO] Completed. Final fitness: {self.global_best_fitness:.4f}")
        return self._particle_to_path(self.global_best_position)
