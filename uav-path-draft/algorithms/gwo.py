"""
GWO Algorithm (Grey Wolf Optimizer) - Gray Wolf Swarm Optimization

Principles:
- Simulates hunting behavior of gray wolf packs
- Pack consists of 4 ranks: Alpha (α), Beta (β), Delta (δ), Omega (ω)
  * Alpha: Leader, best solution
  * Beta: Deputy, second best solution
  * Delta: Scout, third best solution
  * Omega: Followers, rest of the pack, follow alpha/beta/delta
- Each wolf updates position based on positions of alpha, beta, delta
- Update formula:
  X(t+1) = (X_α + X_β + X_δ) / 3 - A⃗ · |C⃗ · X - X|
"""

import numpy as np
from typing import List
from utils.environment import UAVEnvironment


class GWOPathfinder:
    """
    Class implementing Grey Wolf Optimizer algorithm for pathfinding
    """
    
    def __init__(self, environment: UAVEnvironment, num_wolves=30, 
                 max_iterations=200):
        """
        Initialize GWO
        Args:
            environment: UAV environment
            num_wolves: Number of wolves in pack
            max_iterations: Maximum number of iterations
        """
        self.env = environment
        self.num_wolves = num_wolves
        self.max_iterations = max_iterations
        
        self.wolves = []  # Positions of wolves
        self.fitness_values = []  # Fitness values of each wolf
        
        self.alpha = None  # Leader
        self.beta = None
        self.delta = None
        
        self.alpha_score = float('inf')
        self.beta_score = float('inf')
        self.delta_score = float('inf')
        
        self.path = None
        self.best_scores_history = []
        self.track_history = False
        self.position_history = []
        
    def _fitness(self, position: np.ndarray) -> float:
        """
        Fitness function - Distance to goal
        Low fitness = good solution
        """
        if self.env.is_collision(position):
            return float('inf')
        
        distance = self.env.get_distance(position, self.env.goal)
        return distance
    
    def _initialize_wolves(self):
        """Initialize wolf pack with random positions"""
        self.wolves = []
        self.fitness_values = []
        
        for _ in range(self.num_wolves):
            # Create wolf at random available position
            while True:
                wolf = np.random.uniform(0, [self.env.width, self.env.height], 2)
                if not self.env.is_collision(wolf):
                    break
            
            self.wolves.append(wolf)
            fitness = self._fitness(wolf)
            self.fitness_values.append(fitness)
        
        # Find alpha, beta, delta
        self._update_leaders()
    
    def _update_leaders(self):
        """Update three leaders: alpha, beta, delta"""
        # Sort by fitness
        sorted_indices = np.argsort(self.fitness_values)
        
        # Alpha: best
        self.alpha = self.wolves[sorted_indices[0]].copy()
        self.alpha_score = self.fitness_values[sorted_indices[0]]
        
        # Beta: second best
        self.beta = self.wolves[sorted_indices[1]].copy()
        self.beta_score = self.fitness_values[sorted_indices[1]]
        
        # Delta: third best
        self.delta = self.wolves[sorted_indices[2]].copy()
        self.delta_score = self.fitness_values[sorted_indices[2]]
    
    def _update_position(self, wolf_index: int, iteration: int):
        """
        Update position of one wolf
        Formula: X = (X_α + X_β + X_δ) / 3 - A⃗ · |C⃗ · X - X|
        """
        current_wolf = self.wolves[wolf_index]
        
        # a decreases from 2 to 0
        a = 2 - 2 * (iteration / self.max_iterations)
        
        # Update according to alpha
        A1 = 2 * a * np.random.random(2) - a
        C1 = 2 * np.random.random(2)
        X1 = self.alpha - A1 * np.abs(C1 * self.alpha - current_wolf)
        
        # Update according to beta
        A2 = 2 * a * np.random.random(2) - a
        C2 = 2 * np.random.random(2)
        X2 = self.beta - A2 * np.abs(C2 * self.beta - current_wolf)
        
        # Update according to delta
        A3 = 2 * a * np.random.random(2) - a
        C3 = 2 * np.random.random(2)
        X3 = self.delta - A3 * np.abs(C3 * self.delta - current_wolf)
        
        # New position is average
        new_position = (X1 + X2 + X3) / 3
        
        # Check boundaries
        new_position = np.clip(new_position, 0, 
                              [self.env.width, self.env.height])
        
        # Check collision
        if not self.env.is_collision(new_position):
            self.wolves[wolf_index] = new_position
        
        # Evaluate fitness again
        new_fitness = self._fitness(self.wolves[wolf_index])
        self.fitness_values[wolf_index] = new_fitness
    
    def find_path(self) -> bool:
        """
        Find path using Grey Wolf Optimizer
        
        GRAY WOLF HUNTING AND HIERARCHY:
        ================================
        GWO simulates hunting behavior of gray wolf packs
        
        WOLF PACK HAS 4 RANKS:
        ====================
        1. ALPHA (α): Leader, commands hunting
           - Has best solution (best fitness)
           - Commands other wolves
        
        2. BETA (β): Deputy, assists alpha
           - Has second best solution
           - Assists alpha and commands omega
        
        3. DELTA (δ): Scout, protects the pack
           - Has third best solution
           - Protects children and reports threats
        
        4. OMEGA (ω): Followers, hunted by pack
           - Worst solution (worst fitness)           
           - Follows all three: X_new = (X_a + X_b + X_d) / 3
        
        DETAILED PROCEDURE:
        ===================
        1. INITIALIZATION:
           - Create pack of 30 wolves at random positions
           - Set alpha, beta, delta = 3 best wolves
        
        2. MAIN LOOP (maximum 200 iterations):
           a. UPDATE ALL WOLVES:
              - Alpha hunts: X_a(t+1) = X_a(t) - A*|C*X_a - X|
              - Beta hunts: X_b(t+1) = X_b(t) - B*|C*X_b - X|
              - Delta hunts: X_d(t+1) = X_d(t) - D*|C*X_d - X|
              - Omega follow: X(t+1) = (X_a + X_b + X_d) / 3
           
           b. COEFFICIENTS A AND C:
              - a = 2 - 2*(iteration/max_iterations)
                * Iteration 0: a = 2 (broad search, exploration)
                * Iteration 200: a = 0 (detailed search, exploitation)
              - A = 2*a*rand - a (range [-a, a])
              - C = 2*rand (range [0, 2])
           
           c. SEARCH BEHAVIOR SWITCH:
              - If |C*X_best - X| > 1 => Broad search
              - If |C*X_best - X| < 1 => Exploit around best
           
           d. UPDATE PACK LEADERS:
              - Repeat step 2: find 3 best wolves
        
        3. CONVERGENCE: Stop early if alpha_score < 5
        
        4. BUILD PATH: From start -> alpha -> goal
        
        PHASES VISUALIZATION:
        ====================
        Iteration 0-50 (a=2->1.5):    Pack broad exploration
        Iteration 50-100 (a=1.5->1):  Pack starts concentrating
        Iteration 100-150 (a=1->0.5): Pack converges around goal
        Iteration 150-200 (a=0.5->0): Pack exploits details near goal
        
        Returns:
        --------
        bool : True if valid solution found (alpha_score < inf)
        """
        # ---------- STEP 1: INITIALIZE WOLF PACK ----------
        self._initialize_wolves()
        self.best_scores_history = []
        
        # ---------- STEP 2: MAIN LOOP ----------
        for iteration in range(self.max_iterations):
            # ---------- 2a: UPDATE ALL WOLVES ----------
            for wolf_idx in range(self.num_wolves):
                self._update_position(wolf_idx, iteration)
            
            # ---------- 2d: UPDATE PACK LEADERS ----------
            # Find 3 best wolves: alpha, beta, delta
            self._update_leaders()
            
            # Record progress
            self.best_scores_history.append(self.alpha_score)
            
            # Track history if enabled
            if self.track_history:
                self.position_history.append({
                    'iteration': iteration,
                    'alpha_position': self.alpha.copy() if self.alpha is not None else None,
                    'beta_position': self.beta.copy() if self.beta is not None else None,
                    'delta_position': self.delta.copy() if self.delta is not None else None,
                    'omega_positions': [w.copy() for w in self.wolves],
                    'best_score': self.alpha_score
                })
            
            # Print progress
            if iteration % 50 == 0:
                pass  # print(f"GWO Iteration {iteration}: {self.alpha_score:.2f}")
            
            # ---------- STEP 3: CONVERGENCE ----------
            if self.alpha_score < 5:  # Close to goal
                break
        
        # ---------- STEP 4: BUILD PATH ----------
        self.path = self._construct_path()
        
        return self.alpha_score < float('inf')
    
    def _construct_path(self) -> List[np.ndarray]:
        """
        Build path from start through alpha to goal with collision checking
        """
        path = [self.env.start.copy()]
        
        # Interpolate from start to alpha with collision checking
        if self.alpha is not None:
            dist = self.env.get_distance(self.env.start, self.alpha)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.env.start * (1 - t) + self.alpha * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Interpolate from alpha to goal with collision checking
        if self.alpha is not None:
            dist = self.env.get_distance(self.alpha, self.env.goal)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.alpha * (1 - t) + self.env.goal * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Ensure goal is added if valid
        if not self.env.is_collision(self.env.goal):
            if len(path) == 0 or not np.allclose(path[-1], self.env.goal):
                path.append(self.env.goal.copy())
        
        return path
    
    def get_path(self) -> List[np.ndarray]:
        """Get the found path"""
        return self.path
    
    def get_statistics(self) -> dict:
        """Get statistics about search process"""
        if self.path is None:
            return {
                'best_score': self.alpha_score,
                'distance': 0,
                'convergence_iteration': self.max_iterations
            }
        
        path = np.array(self.path)
        distance = float(sum(np.linalg.norm(path[i+1] - path[i]) 
                      for i in range(len(path)-1)))
        
        # Find convergence iteration
        convergence_iter = self.max_iterations
        if len(self.best_scores_history) > 10:
            for i in range(10, len(self.best_scores_history)):
                if i > 10 and np.std(self.best_scores_history[i-10:i]) < 0.1:
                    convergence_iter = i
                    break
        
        return {
            'best_score': self.alpha_score,
            'distance': distance,
            'convergence_iteration': convergence_iter,
            'num_waypoints': len(self.path)
        }
