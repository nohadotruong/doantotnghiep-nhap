"""
PSO Algorithm (Particle Swarm Optimization) - Swarm Intelligence

Principles:
- Simulates behavior of bird flocks or fish schools searching for food
- Each particle represents a potential solution
- Each particle moves based on:
  * Its current velocity (inertia)
  * Direction to its personal best solution (cognitive)
  * Direction to the swarm's best solution (social)
- Velocity update formula:
  v(t+1) = w*v(t) + c1*r1*(pbest - x(t)) + c2*r2*(gbest - x(t))
"""

import numpy as np
from typing import List, Tuple
from utils.environment import UAVEnvironment


class PSOPathfinder:
    """
    Class implementing PSO algorithm for pathfinding
    """
    
    def __init__(self, environment: UAVEnvironment, num_particles=30, 
                 max_iterations=200, c1=2.0, c2=2.0, w=0.7):
        """
        Initialize PSO
        Args:
            environment: UAV environment
            num_particles: Number of particles
            max_iterations: Maximum number of iterations
            c1: Cognitive coefficient (attraction to personal best)
            c2: Social coefficient (attraction to global best)
            w: Inertia weight (momentum of old velocity)
        """
        self.env = environment
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.c1 = c1
        self.c2 = c2
        self.w = w
        
        self.particles = []
        self.velocities = []
        self.pbest_positions = []  # Best position of each particle
        self.pbest_scores = []      # Best score of each particle
        self.gbest_position = None  # Best position of entire swarm
        self.gbest_score = float('inf')
        
        self.path = None
        self.iteration_best_scores = []
        self.track_history = False
        self.position_history = []
        
    def _initialize_swarm(self):
        """Initialize swarm with random particles"""
        self.particles = []
        self.velocities = []
        self.pbest_positions = []
        self.pbest_scores = []
        
        for _ in range(self.num_particles):
            # Create random particle in available space
            while True:
                particle = np.random.uniform(0, [self.env.width, self.env.height], 2)
                if not self.env.is_collision(particle):
                    break
            
            self.particles.append(particle)
            self.velocities.append(np.random.uniform(-1, 1, 2))
            self.pbest_positions.append(particle.copy())
            
            # Evaluate initial score
            score = self._fitness(particle)
            self.pbest_scores.append(score)
            
            if score < self.gbest_score:
                self.gbest_score = score
                self.gbest_position = particle.copy()
    
    def _fitness(self, position: np.ndarray) -> float:
        """
        Fitness function - Distance to goal
        Closer particle = lower score (better)
        """
        # Penalty for collision
        if self.env.is_collision(position):
            return float('inf')
        
        distance_to_goal = self.env.get_distance(position, self.env.goal)
        return distance_to_goal
    
    def _update_particles(self):
        """
        Update positions and velocities of all particles
        
        DETAILED PROCEDURE:
        ===================
        PSO simulates bird flock behavior searching for food
        
        EACH PARTICLE MUST UPDATE:
        ==========================
        
        STEP 1: CALCULATE FORMULA COMPONENTS
        v_new = w*v_old + c1*r1*(pbest - x) + c2*r2*(gbest - x)
        
        Where:
        - v: velocity (direction and speed of movement)
        - w: inertia weight (0.7) - momentum from old velocity
        - c1: cognitive coefficient (2.0) - attraction to personal best
        - c2: social coefficient (2.0) - attraction to global best
        - r1, r2: random numbers (0-1) - provide randomness
        - pbest: personal best position of this particle
        - x: current position of particle
        
        STEP 2: CALCULATE COMPONENTS
        - Inertia = w * v_old
          (maintain momentum of movement - avoid sudden changes)
        
        - Cognitive = c1 * r1 * (pbest - x)
          * (pbest - x): direction toward personal best
          * c1 * r1: magnitude is random (0 - 2*c1)
          * If pbest ~ x: component = 0 (already at best)
          * If pbest >> x: component is large (need to go to pbest)
        
        - Social = c2 * r2 * (gbest - x)
          * (gbest - x): direction toward global best
          * c2 * r2: magnitude is random (0 - 2*c2)
          * Creates attractive force following good solutions
        
        STEP 3: NEW VELOCITY = SUM OF 3 COMPONENTS
        v = inertia + cognitive + social
        
        STEP 4: LIMIT VELOCITY
        v = max(min(v, max_v), -max_v)
        (Prevent particle from moving too fast and losing control)
        
        STEP 5: UPDATE POSITION
        x_new = x_old + v
        
        STEP 6: CHECK COLLISION
        - If x_new collides => keep x = x_old
        - If x_new valid => update x = x_new
        
        STEP 7: EVALUATE NEW SCORE
        - Calculate distance from x_new to goal
        - If better than pbest => update pbest
        - If better than gbest => update gbest
        
        EXAMPLE ILLUSTRATION:
        =====================
        Particle 1: x=[30, 30], v=[2, 3], pbest=[30, 20], gbest=[80, 80]
        
        r1=[0.5, 0.5], r2=[0.5, 0.5], w=0.7, c1=2, c2=2
        
        Inertia = 0.7 * [2, 3] = [1.4, 2.1]
        Cognitive = 2 * 0.5 * ([30,20] - [30,30]) = 1 * [0, -10] = [0, -10]
        Social = 2 * 0.5 * ([80,80] - [30,30]) = 1 * [50, 50] = [50, 50]
        
        v_new = [1.4, 2.1] + [0, -10] + [50, 50] = [51.4, 42.1]
        v_max = 20 (from map size)
        v_new = [20, 20] (after limiting)
        
        x_new = [30, 30] + [20, 20] = [50, 50]
        => Particle moves to position [50, 50]
        """
        for i in range(self.num_particles):
            # ---------- STEP 1 + 2 + 3: CALCULATE NEW VELOCITY ----------
            r1 = np.random.random(2)  # Random numbers (0-1)
            r2 = np.random.random(2)
            
            # Cognitive component: attraction to personal best
            cognitive = self.c1 * r1 * (self.pbest_positions[i] - self.particles[i])
            
            # Social component: attraction to global best
            social = self.c2 * r2 * (self.gbest_position - self.particles[i])
            
            # ---------- STEP 3: NEW VELOCITY = SUM OF 3 COMPONENTS ----------
            self.velocities[i] = (self.w * self.velocities[i] + 
                                 cognitive + social)
            
            # ---------- STEP 4: LIMIT VELOCITY ----------
            max_velocity = max(self.env.width, self.env.height) / 10
            self.velocities[i] = np.clip(self.velocities[i], 
                                        -max_velocity, max_velocity)
            
            # ---------- STEP 5: UPDATE POSITION ----------
            new_position = self.particles[i] + self.velocities[i]
            
            # ---------- STEP 6: CHECK COLLISION ----------
            if not self.env.is_collision(new_position):
                self.particles[i] = new_position
            
            # ---------- STEP 7: EVALUATE NEW SCORE ----------
            score = self._fitness(self.particles[i])
            
            if score < self.pbest_scores[i]:
                self.pbest_scores[i] = score
                self.pbest_positions[i] = self.particles[i].copy()
                
                if score < self.gbest_score:
                    self.gbest_score = score
                    self.gbest_position = self.particles[i].copy()
    
    def find_path(self) -> bool:
        """
        Find path using PSO
        
        HIGH-LEVEL PROCEDURE:
        ====================
        1. INITIALIZE: Create random swarm and track best position
        2. LOOP: For each iteration, update particles
        3. UPDATE: Each particle moves according to PSO formula
        4. CONVERGENCE: When swarm converges near goal => stop early
        5. BUILD: Construct path from start -> gbest -> goal
        
        LOOP DETAILS:
        =============
        - Max iteration: 200 (maximum number of iterations)
        - Each iteration: update all particles (see _update_particles)
        - Track: best score after this iteration (gbest_score)
        - Check convergence: if gbest_score < 5 => stop early (close to goal)
        
        CONVERGENCE:
        ============
        - Swarm converges when all particles circle around gbest (best found)
        - Convergence speed depends on:
          * c1, c2: coefficients (high => fast convergence but risk local optimum)
          * w: inertia weight (high => explore broadly, low => exploit)
          * num_particles: more particles => better exploration
        
        Returns:
        --------
        bool : True if good solution found (gbest_score < inf)
        """
        # ---------- STEP 1: INITIALIZE SWARM ----------
        self._initialize_swarm()
        self.iteration_best_scores = []
        
        # ---------- STEP 2: MAIN LOOP ----------
        for iteration in range(self.max_iterations):
            # Update all particles in this iteration
            self._update_particles()
            
            # Track progress: best score after this iteration
            self.iteration_best_scores.append(self.gbest_score)
            
            # Track history if enabled
            if self.track_history:
                self.position_history.append({
                    'iteration': iteration,
                    'particles': [p.copy() for p in self.particles],
                    'velocities': [v.copy() for v in self.velocities],
                    'pbest_positions': [pb.copy() for pb in self.pbest_positions],
                    'pbest_scores': self.pbest_scores.copy(),
                    'gbest_position': self.gbest_position.copy() if self.gbest_position is not None else None,
                    'gbest_score': self.gbest_score,
                    'best_score': self.gbest_score
                })
            
            # Print progress (optional)
            if iteration % 50 == 0:
                pass  # print(f"PSO Iteration {iteration}: {self.gbest_score:.2f}")
            
            # ---------- STEP 4: CHECK CONVERGENCE ----------
            # If close to goal, stop early to save time
            if self.gbest_score < 5:
                break
        
        # ---------- STEP 5: BUILD PATH ----------
        self.path = self._construct_path()
        
        return self.gbest_score < float('inf')
    
    def _construct_path(self) -> List[np.ndarray]:
        """
        Build path from start through gbest to goal with collision checking
        """
        path = [self.env.start.copy()]
        
        # Interpolate from start to gbest with collision checking
        if self.gbest_position is not None:
            dist = self.env.get_distance(self.env.start, self.gbest_position)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.env.start * (1 - t) + self.gbest_position * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Interpolate from gbest to goal with collision checking
        if self.gbest_position is not None:
            dist = self.env.get_distance(self.gbest_position, self.env.goal)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.gbest_position * (1 - t) + self.env.goal * t
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
                'best_score': self.gbest_score,
                'distance': 0,
                'convergence_iteration': self.max_iterations
            }
        
        path = np.array(self.path)
        distance = float(sum(np.linalg.norm(path[i+1] - path[i]) 
                      for i in range(len(path)-1)))
        
        # Find convergence iteration (when score stops changing)
        convergence_iter = self.max_iterations
        if len(self.iteration_best_scores) > 0:
            for i in range(1, len(self.iteration_best_scores)):
                if i > 10 and np.std(self.iteration_best_scores[i-10:i]) < 0.1:
                    convergence_iter = i
                    break
        
        return {
            'best_score': self.gbest_score,
            'distance': distance,
            'convergence_iteration': convergence_iter,
            'num_waypoints': len(self.path)
        }
