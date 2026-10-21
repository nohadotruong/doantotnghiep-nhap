"""
GA Algorithm (Genetic Algorithm) - Evolutionary Algorithm

Principles:
- Simulates natural evolution process
- Population consists of individuals (chromosomes)
  * Each individual represents a solution (in this case, a waypoint)
Steps:
  1. Initialize random population
  2. Evaluate fitness for each individual
  3. Selection: Pick the best individuals
  4. Crossover: Create new individuals from 2 good ones
  5. Mutation: Random change to maintain diversity
  6. Repeat from step 2
"""

import numpy as np
from typing import List, Tuple
from utils.environment import UAVEnvironment


class GAPathfinder:
    """
    Class implementing Genetic Algorithm for pathfinding
    """
    
    def __init__(self, environment: UAVEnvironment, population_size=30, 
                 max_iterations=200, mutation_rate=0.1, crossover_rate=0.8):
        """
        Initialize GA
        Args:
            environment: UAV environment
            population_size: Size of population
            max_iterations: Maximum number of generations
            mutation_rate: Mutation probability (0-1)
            crossover_rate: Crossover probability (0-1)
        """
        self.env = environment
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        self.population = []  # Population
        self.fitness_values = []  # Fitness values
        
        self.best_individual = None
        self.best_fitness = float('inf')
        
        self.path = None
        self.best_fitness_history = []
        self.track_history = False
        self.position_history = []
        
    def _create_individual(self) -> np.ndarray:
        """
        Create an individual (solution) - a random available point
        """
        while True:
            individual = np.random.uniform(0, [self.env.width, self.env.height], 2)
            if not self.env.is_collision(individual):
                return individual
    
    def _fitness(self, individual: np.ndarray) -> float:
        """
        Fitness function - Distance to goal
        Low fitness = good solution
        """
        distance = self.env.get_distance(individual, self.env.goal)
        return distance
    
    def _initialize_population(self):
        """Initialize population with random individuals"""
        self.population = []
        self.fitness_values = []
        
        for _ in range(self.population_size):
            individual = self._create_individual()
            self.population.append(individual)
            fitness = self._fitness(individual)
            self.fitness_values.append(fitness)
        
        # Find best individual
        self._update_best_individual()
    
    def _update_best_individual(self):
        """Update the best individual in population"""
        best_idx = np.argmin(self.fitness_values)
        
        if self.fitness_values[best_idx] < self.best_fitness:
            self.best_fitness = self.fitness_values[best_idx]
            self.best_individual = self.population[best_idx].copy()
    
    def _selection(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Selection (Tournament Selection)
        Select 2 individuals for crossover
        """
        # Select each individual via tournament selection
        def tournament_select():
            tournament_size = 3
            tournament_indices = np.random.choice(self.population_size, 
                                                 tournament_size, replace=False)
            tournament_fitness = [self.fitness_values[i] 
                                 for i in tournament_indices]
            winner_idx = tournament_indices[np.argmin(tournament_fitness)]
            return self.population[winner_idx].copy()
        
        parent1 = tournament_select()
        parent2 = tournament_select()
        
        return parent1, parent2
    
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """
        Crossover - create child from 2 parents
        Uses: Blend crossover
        """
        if np.random.random() > self.crossover_rate:
            return parent1.copy() if np.random.random() > 0.5 else parent2.copy()
        
        # Blend crossover: trung gian giữa hai cha mẹ
        alpha = np.random.random(2)
        child = alpha * parent1 + (1 - alpha) * parent2
        
        # Kiểm tra biên
        child = np.clip(child, 0, [self.env.width, self.env.height])
        
        return child
    
    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """
        Mutation - random change to individual
        """
        if np.random.random() > self.mutation_rate:
            return individual.copy()
        
        # Change one or both coordinates
        max_change = max(self.env.width, self.env.height) / 10
        mutation = np.random.uniform(-max_change, max_change, 2)
        
        mutated = individual + mutation
        
        # Check boundaries
        mutated = np.clip(mutated, 0, [self.env.width, self.env.height])
        
        # Check collision
        if not self.env.is_collision(mutated):
            return mutated
        
        return individual.copy()
    
    def _evolve_generation(self):
        """Evolve one generation"""
        new_population = []
        new_fitness_values = []
        
        # Calculate relative fitness
        min_fitness = min(self.fitness_values)
        max_fitness = max(self.fitness_values)
        
        # Keep best individual (Elitism)
        elite_idx = np.argmin(self.fitness_values)
        new_population.append(self.population[elite_idx].copy())
        new_fitness_values.append(self.fitness_values[elite_idx])
        
        # Create new individuals
        while len(new_population) < self.population_size:
            # Selection
            parent1, parent2 = self._selection()
            
            # Crossover
            child = self._crossover(parent1, parent2)
            
            # Mutation
            child = self._mutate(child)
            
            new_population.append(child)
            new_fitness_values.append(self._fitness(child))
        
        self.population = new_population
        self.fitness_values = new_fitness_values
        self._update_best_individual()
    
    def find_path(self) -> bool:
        """
        Find path using Genetic Algorithm
        
        NATURAL EVOLUTION PROCESS:
        ==========================
        GA simulates natural evolution process
        
        POPULATION:
        ===========
        - Each individual (individual) = one solution (one coordinate point)
        - Each individual has fitness = distance to goal
        - Initial population: 30 random individuals
        
        EACH GENERATION:
        ===============
        Contains 3 steps:
        
        1. SELECTION (Tournament Selection):
           - Pick 3 random individuals -> pick the best
           - Repeat 2 times => pick 2 parents for crossover
           - This product has high survival ability
        
        2. CROSSOVER (Blend Crossover):
           - Take coordinates of 2 parents:
             parent1 = [30, 40], parent2 = [80, 80]
           - Create child = alpha*parent1 + (1-alpha)*parent2
             alpha = [0.3, 0.7] (random)
             child = [0.3*30 + 0.7*80, 0.7*40 + 0.3*80]
                   = [65, 52]
           - Child is between 2 parents => inherits traits from both
           - If no crossover: randomly pick 1 parent
        
        3. MUTATION (Gaussian Mutation):
           - Make small changes [±0.1, ±0.2] (random)
           - Maintain diversity in population (prevent all identical)
           - Only happens with mutation_rate = 0.1 (10%) probability
           - If collision => reject mutation
        
        ELITISM:
        ========
        - Keep best individual from old generation into new generation
        - Ensures: evolution doesn't go backward (solution doesn't worse)
        
        CONVERGENCE:
        ============
        - Stop early if best_fitness < 5 (close to goal)
        - Otherwise: run full max_iterations = 200 generations
        
        BUILD PATH:
        ===========
        - Use best_individual (best individual)
        - From start -> best_individual -> goal
        
        EVOLUTION DETAILS:
        ==================
        Generation 0: 
          - Random population
          - Best fitness = ~80
        
        Generation 1-10:
          - Selection: best individuals survive
          - Crossover: learn from each other's strengths
          - Mutation: explore
          - Best fitness = ~70
        
        Generation 10-50:
          - Population concentrates around good solutions
          - Best fitness = ~40
        
        Generation 50-100:
          - Population converges around best solution
          - Best fitness = ~20
        
        Generation 100-200:
          - Detailed search around goal
          - Best fitness = ~10 -> < 5
        
        Returns:
        --------
        bool : True if valid solution found (best_fitness < inf)
        """
        # ---------- STEP 1: INITIALIZE POPULATION ----------
        self._initialize_population()
        self.best_fitness_history = []
        
        # ---------- STEP 2: MAIN EVOLUTION LOOP ----------
        for generation in range(self.max_iterations):
            # Evolve 1 generation
            self._evolve_generation()
            
            # Record progress
            self.best_fitness_history.append(self.best_fitness)
            
            # Track history if enabled
            if self.track_history:
                self.position_history.append({
                    'generation': generation,
                    'population': [p.copy() for p in self.population],
                    'best_solution': self.best_individual.copy() if self.best_individual is not None else None,
                    'best_fitness': self.best_fitness,
                    'best_score': self.best_fitness,
                    'iteration': generation
                })
            
            # Print progress
            if generation % 50 == 0:
                pass  # print(f"GA Generation {generation}: {self.best_fitness:.2f}")
            
            # ---------- CHECK CONVERGENCE ----------
            if self.best_fitness < 5:  # Close to goal
                break
        
        # ---------- BUILD PATH ----------
        self.path = self._construct_path()
        
        return self.best_fitness < float('inf')
    
    def _construct_path(self) -> List[np.ndarray]:
        """
        Build path from start through best_individual to goal with collision checking
        """
        path = [self.env.start.copy()]
        
        # Interpolate from start to best_individual with collision checking
        if self.best_individual is not None:
            dist = self.env.get_distance(self.env.start, self.best_individual)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.env.start * (1 - t) + self.best_individual * t
                # Only add if no collision
                if not self.env.is_collision(point):
                    if len(path) == 0 or not np.allclose(path[-1], point):
                        path.append(point.copy())
        
        # Interpolate from best_individual to goal with collision checking
        if self.best_individual is not None:
            dist = self.env.get_distance(self.best_individual, self.env.goal)
            num_points = max(10, int(dist / 1.0))  # More points for safety
            
            for t in np.linspace(0, 1, num_points):
                point = self.best_individual * (1 - t) + self.env.goal * t
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
                'best_fitness': self.best_fitness,
                'distance': 0,
                'convergence_generation': self.max_iterations
            }
        
        path = np.array(self.path)
        distance = float(sum(np.linalg.norm(path[i+1] - path[i]) 
                      for i in range(len(path)-1)))
        
        # Find convergence generation
        convergence_gen = self.max_iterations
        if len(self.best_fitness_history) > 10:
            for i in range(10, len(self.best_fitness_history)):
                if i > 10 and np.std(self.best_fitness_history[i-10:i]) < 0.1:
                    convergence_gen = i
                    break
        
        return {
            'best_fitness': self.best_fitness,
            'distance': distance,
            'convergence_generation': convergence_gen,
            'num_waypoints': len(self.path)
        }
