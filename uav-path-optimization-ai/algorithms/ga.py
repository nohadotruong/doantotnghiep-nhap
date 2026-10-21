"""
Genetic Algorithm (GA) để tối ưu hóa đường đi.

Ý tưởng chính:
- Mỗi individual là một 'chromosome' (ma trận waypoint).
- Khởi tạo quần thể, đánh giá fitness, áp dụng selection/crossover/mutation,
  dùng elitism giữ cá thể tốt nhất.
- Sau `max_generations` trả về `best_individual`.
"""

import numpy as np
from typing import List, Tuple, Dict
from generate_map import Map2D
from object_function import ObjectiveFunction


class Individual:
    """Một cá thể trong quần thể GA."""
    
    def __init__(self, chromosome: np.ndarray):
        self.chromosome = chromosome.copy()
        self.fitness = float('inf')


class GA:
    """Lớp thực hiện thuật toán GA."""
    
    def __init__(self, map_obj: Map2D, population_size: int = 30, 
                 max_generations: int = 100, num_waypoints: int = 5,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        """
        Khởi tạo GA.
        
        Args:
            map_obj: Đối tượng Map2D
            population_size: Kích thước quần thể
            max_generations: Số thế hệ tối đa
            num_waypoints: Số điểm dừng
            mutation_rate: Tỷ lệ đột biến
            crossover_rate: Tỷ lệ lai ghép
        """
        self.map = map_obj
        self.population_size = population_size
        self.max_generations = max_generations
        self.num_waypoints = num_waypoints
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        self.population = []
        self.best_individual = None
        self.best_fitness = float('inf')
        
        self.objective_function = ObjectiveFunction(map_obj)

        # Computation time optional
        self.computation_time = 0
    
    def initialize_population(self):
        """Khởi tạo quần thể ban đầu."""
        self.population = []
        
        for _ in range(self.population_size):
            # Mỗi chromosome là ma trận (num_waypoints, 2)
            chromosome = np.random.uniform(
                0,
                [self.map.width, self.map.height],
                size=(self.num_waypoints, 2)
            )

            individual = Individual(chromosome)

            # Đánh giá bằng hàm objective
            path = self.chromosome_to_path(chromosome)
            individual.fitness, _ = self.objective_function.evaluate_path(path)

            # Cập nhật best individual ban đầu
            if individual.fitness < self.best_fitness:
                self.best_fitness = individual.fitness
                self.best_individual = Individual(chromosome)
                self.best_individual.fitness = individual.fitness

            self.population.append(individual)
    
    def chromosome_to_path(self, chromosome: np.ndarray) -> List[Tuple[float, float]]:
        """
        Chuyển đổi chromosome thành đường đi.
        
        Args:
            chromosome: Ma trận tọa độ
            
        Returns:
            Danh sách các điểm trong đường đi
        """
        # Chuyển chromosome -> danh sách điểm path (start, waypoints..., goal)
        path = [self.map.start]

        for waypoint in chromosome:
            x = np.clip(waypoint[0], 0, self.map.width)
            y = np.clip(waypoint[1], 0, self.map.height)
            path.append((x, y))

        path.append(self.map.goal)
        return path
    
    def evaluate_fitness(self, individual: Individual):
        """
        Đánh giá fitness của một cá thể.
        
        Args:
            individual: Cá thể cần đánh giá
        """
        path = self.chromosome_to_path(individual.chromosome)
        individual.fitness, _ = self.objective_function.evaluate_path(path)
    
    def selection(self) -> List[Individual]:
        """
        Chọn lọc bằng tournament selection.
        
        Returns:
            Danh sách các cá thể được chọn
        """
        # Tournament selection (kích thước 3) - chọn cá thể tốt nhất trong mỗi tournament
        selected = []

        for _ in range(self.population_size):
            tournament = np.random.choice(self.population, size=3, replace=False)
            winner = min(tournament, key=lambda x: x.fitness)
            selected.append(winner)

        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Lai ghép hai cá thể cha.
        
        Args:
            parent1: Cha thứ nhất
            parent2: Cha thứ hai
            
        Returns:
            Hai cá thể con
        """
        # Nếu không thực hiện crossover, trả về bản sao cha
        if np.random.random() > self.crossover_rate:
            return Individual(parent1.chromosome), Individual(parent2.chromosome)

        # Uniform crossover: với xác suất 0.5 hoán đổi từng gene (waypoint)
        child1_chromosome = parent1.chromosome.copy()
        child2_chromosome = parent2.chromosome.copy()

        for i in range(self.num_waypoints):
            if np.random.random() < 0.5:
                child1_chromosome[i] = parent2.chromosome[i]
                child2_chromosome[i] = parent1.chromosome[i]

        child1 = Individual(child1_chromosome)
        child2 = Individual(child2_chromosome)

        return child1, child2
    
    def mutate(self, individual: Individual):
        """
        Đột biến một cá thể.
        
        Args:
            individual: Cá thể cần đột biến
        """
        # Với xác suất mutation_rate áp gaussian noise cho gene
        for i in range(self.num_waypoints):
            if np.random.random() < self.mutation_rate:
                individual.chromosome[i] += np.random.normal(0, 2, 2)

                # Đảm bảo tọa độ vẫn nằm trong giới hạn bản đồ
                individual.chromosome[i] = np.clip(
                    individual.chromosome[i],
                    [0, 0],
                    [self.map.width, self.map.height]
                )
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Tìm đường đi sử dụng GA.
        
        Returns:
            Đường đi tốt nhất tìm được
        """
        # Nếu thiếu start/goal -> không chạy
        if not self.map.start or not self.map.goal:
            return []

        # Khởi tạo quần thể ban đầu
        self.initialize_population()

        # Vòng lặp tiến hoá
        for generation in range(self.max_generations):
            # Chọn lọc (tournament)
            selected = self.selection()

            # Tạo quần thể mới, bắt đầu với elitism (giữ một cá thể tốt nhất)
            new_population = []
            new_population.append(Individual(self.best_individual.chromosome))

            # Lai ghép, đột biến và đánh giá cho đến khi đủ population
            while len(new_population) < self.population_size:
                parent1 = np.random.choice(selected)
                parent2 = np.random.choice(selected)

                child1, child2 = self.crossover(parent1, parent2)

                self.mutate(child1)
                self.mutate(child2)

                self.evaluate_fitness(child1)
                self.evaluate_fitness(child2)

                # Cập nhật best nếu tìm thấy con tốt hơn
                if child1.fitness < self.best_fitness:
                    self.best_fitness = child1.fitness
                    self.best_individual = Individual(child1.chromosome)

                new_population.append(child1)

                if len(new_population) < self.population_size:
                    if child2.fitness < self.best_fitness:
                        self.best_fitness = child2.fitness
                        self.best_individual = Individual(child2.chromosome)

                    new_population.append(child2)

            self.population = new_population[:self.population_size]

        # Trả về đường đi xây từ best individual
        path = self.chromosome_to_path(self.best_individual.chromosome)
        return path


def ga_path_planning(map_obj: Map2D, population_size: int = 30, 
                    max_generations: int = 100, 
                    num_waypoints: int = 5) -> List[Tuple[float, float]]:
    """
    Hàm tiện ility để chạy GA.
    
    Args:
        map_obj: Đối tượng Map2D
        population_size: Kích thước quần thể
        max_generations: Số thế hệ tối đa
        num_waypoints: Số điểm dừng
        
    Returns:
        Đường đi tìm được
    """
    ga = GA(map_obj, population_size, max_generations, num_waypoints)
    return ga.find_path()


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    path = ga_path_planning(map_obj, population_size=30, max_generations=50)
    
    if path:
        print(f"Tìm thấy đường đi với {len(path)} điểm")
        print(f"Độ dài: {sum(np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) for i in range(len(path)-1)):.2f}")
        map_obj.visualize(path, filename='results/ga_example.png')
    else:
        print("Không tìm thấy đường đi")
