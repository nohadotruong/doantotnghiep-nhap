"""
SA Algorithm (Simulated Annealing) - Thermal Process Simulation

Principles:
- Simulates slow cooling process of metal in metalworking
- Starts at high temperature, gradually reduces temperature
- At high temperature: High probability to accept worse solutions
  (to escape local optimum)
- At low temperature: Only accept better solutions
- Acceptance probability: P = exp(-ΔE / T)
  * ΔE: Energy difference (score difference)
  * T: Current temperature
"""

import numpy as np
from typing import List
from utils.environment import UAVEnvironment


class SAPathfinder:
    """
    Class implementing Simulated Annealing algorithm for pathfinding
    """
    
    def __init__(self, environment: UAVEnvironment, 
                 initial_temp=100, cooling_rate=0.95, 
                 max_iterations=500, step_size=2.0):
        """
        Initialize SA
        Args:
            environment: UAV environment
            initial_temp: Initial temperature
            cooling_rate: Temperature decrease rate (0 < rate < 1)
            max_iterations: Maximum number of iterations
            step_size: Size of movement step
        """
        self.env = environment
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
        self.step_size = step_size
        
        self.current_solution = None
        self.current_energy = float('inf')
        self.best_solution = None
        self.best_energy = float('inf')
        
        self.path = None
        self.temperature_history = []
        self.energy_history = []
        self.track_history = False
        self.position_history = []
        
    def _energy(self, position: np.ndarray) -> float:
        """
        Energy function - Distance to goal
        Low energy = good solution
        """
        if self.env.is_collision(position):
            return float('inf')
        
        distance = self.env.get_distance(position, self.env.goal)
        return distance
    
    def _perturb(self, solution: np.ndarray) -> np.ndarray:
        """
        Create new solution by making small change to current solution
        """
        max_attempts = 10
        for _ in range(max_attempts):
            # Random perturbation
            perturbation = np.random.uniform(-self.step_size, self.step_size, 2)
            new_solution = solution + perturbation
            
            # Check boundaries
            new_solution = np.clip(new_solution, 0, 
                                  [self.env.width, self.env.height])
            
            # Check collision
            if not self.env.is_collision(new_solution):
                return new_solution
        
        # If can't find valid solution, return old solution
        return solution.copy()
    
    def _acceptance_probability(self, current_energy: float, 
                               new_energy: float, temperature: float) -> float:
        """
        Calculate probability of accepting new solution
        """
        if new_energy < current_energy:
            return 1.0  # Always accept if better
        
        if temperature == 0:
            return 0.0
        
        # Accept worse solution with probability based on temperature
        return np.exp(-(new_energy - current_energy) / temperature)
    
    def find_path(self) -> bool:
        """
        Find path using Simulated Annealing
        
        METALLURGICAL ANNEALING PROCESS:
        ================================
        SA simulates the slow cooling process of metal during metalworking:
        - Initially: High TEMPERATURE => can accept WORSE solutions
          (to escape local optimum)
        - Gradually: TEMPERATURE DECREASES => only accept BETTER solutions
        
        DETAILED PROCEDURE:
        ===================
        1. INITIALIZATION: 
           - Initial solution: random in available space
           - Initial temperature: 100
           - Temperature decrease rate: 0.95
        
        2. MAIN LOOP (maximum 500 iterations):
           a. CREATE NEW SOLUTION: perturb() makes small change (±2 distance)
           b. CALCULATE NEW ENERGY: distance to goal (high energy = far from goal)
           c. DECIDE TO ACCEPT:
              - If new solution better => ACCEPT 100%
              - If new solution WORSE => accept with probability P = exp(-ΔE/T)
                * ΔE = energy_new - energy_old (always positive)
                * T = current temperature (high T => high probability)
                * High T => can accept worse solution (escape local)
                * Low T => rarely accept worse solution (exploit)
           d. RECORD BEST: if better than best => update best_solution
           e. COOL DOWN: T = T * cooling_rate
        
        3. TEMPERATURE PROGRESSION:
        Iteration:  1   10   50  100  200  300  400  500
        Temp:     100   65   15    6    1   0.5  0.1  0.03
        Accept %:  95%  85%  50%  20%  10%   5%   2%   1%
        (Probability of accepting worse solution decreases with temperature)
        
        4. CONVERGENCE: Stop early if best_energy < 5 (close to goal)
        
        5. BUILD PATH: From start -> best_solution -> goal
        
        WORKING EXAMPLE:
        ===============
        Iteration 1: T=100, worse solution -> accept (P=0.95)
        Iteration 50: T=15, worse solution -> may accept (P=0.30)
        Iteration 100: T=6, worse solution -> rarely accept (P=0.05)
        Iteration 200: T=1, worse solution -> almost never accept
        
        Returns:
        --------
        bool : True if valid solution found (best_energy < inf)
        """
        # ---------- STEP 1: INITIALIZE INITIAL SOLUTION ----------
        while True:
            self.current_solution = np.random.uniform(0, 
                                                      [self.env.width, self.env.height], 2)
            if not self.env.is_collision(self.current_solution):
                break
        
        self.current_energy = self._energy(self.current_solution)
        self.best_solution = self.current_solution.copy()
        self.best_energy = self.current_energy
        
        temperature = self.initial_temp
        self.temperature_history = []
        self.energy_history = []
        
        # ---------- STEP 2: MAIN LOOP ----------
        for iteration in range(self.max_iterations):
            # a. CREATE NEW SOLUTION
            new_solution = self._perturb(self.current_solution)
            new_energy = self._energy(new_solution)
            
            # c. DECIDE TO ACCEPT
            if self._acceptance_probability(self.current_energy, new_energy, 
                                           temperature) > np.random.random():
                # Accept new solution
                self.current_solution = new_solution
                self.current_energy = new_energy
            
            # d. RECORD BEST
            if self.current_energy < self.best_energy:
                self.best_energy = self.current_energy
                self.best_solution = self.current_solution.copy()
            
            # Record history for plotting
            self.temperature_history.append(temperature)
            self.energy_history.append(self.best_energy)
            
            # Track history if enabled
            if self.track_history:
                self.position_history.append({
                    'iteration': iteration,
                    'current': self.current_solution.copy(),
                    'best': self.best_solution.copy(),
                    'temperature': temperature,
                    'current_energy': self.current_energy,
                    'best_energy': self.best_energy,
                    'best_score': self.best_energy
                })
            
            # e. COOL DOWN
            temperature *= self.cooling_rate
            
            # Print progress
            if iteration % 100 == 0:
                pass  # print(f"SA Iteration {iteration}: T={temperature:.4f}, E={self.best_energy:.2f}")
            
            # ---------- STEP 4: CONVERGENCE ----------
            if self.best_energy < 5:  # Close to goal, stop early
                break
        
        # ---------- STEP 5: BUILD PATH ----------
        self.path = self._construct_path()
        
        return self.best_energy < float('inf')
    
    def _construct_path(self) -> List[np.ndarray]:
        """
        Build path from start through best_solution to goal with collision checking
        """
        path = [self.env.start.copy()]
        
        # Interpolate from start to best_solution with collision checking
        if self.best_solution is not None:
            dist = self.env.get_distance(self.env.start, self.best_solution)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.env.start * (1 - t) + self.best_solution * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Interpolate from best_solution to goal with collision checking
        if self.best_solution is not None:
            dist = self.env.get_distance(self.best_solution, self.env.goal)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.best_solution * (1 - t) + self.env.goal * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Ensure goal is added if valid
        if not self.env.is_collision(self.env.goal):
            if len(path) == 0 or not np.allclose(path[-1], self.env.goal):
                path.append(self.env.goal.copy())
        
        return path
        return path
    
    def get_path(self) -> List[np.ndarray]:
        """Get the found path"""
        return self.path
    
    def get_statistics(self) -> dict:
        """Get statistics about search process"""
        if self.path is None:
            return {
                'best_energy': self.best_energy,
                'distance': 0,
                'final_temperature': 0
            }
        
        path = np.array(self.path)
        distance = float(sum(np.linalg.norm(path[i+1] - path[i]) 
                      for i in range(len(path)-1)))
        
        return {
            'best_energy': self.best_energy,
            'distance': distance,
            'final_temperature': self.temperature_history[-1] if self.temperature_history else 0,
            'num_waypoints': len(self.path)
        }
