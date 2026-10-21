"""
ga.py - Thuật toán GA (Genetic Algorithm) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
from generate_map import Map2D
import time


class GA:
    """Thuật toán GA để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D,
                 population_size: int = 50,
                 num_waypoints: int = 15,
                 max_generations: int = 200,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_size: int = 5):
        """
        Args:
            map_obj: Bản đồ
            population_size: Kích thước quần thể
            num_waypoints: Số điểm waypoint trên đường đi
            max_generations: Số thế hệ tối đa
            mutation_rate: Tỷ lệ đột biến
            crossover_rate: Tỷ lệ lai ghép
            elite_size: Số cá thể ưu tú được giữ lại
        """
        self.map = map_obj
        self.population_size = population_size
        self.num_waypoints = num_waypoints
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        self.path = []
        self.computation_time = 0
        self.population = []
        self.best_individual = None
        self.best_fitness = float('inf')
    
    def create_individual(self) -> np.ndarray:
        """Tạo một cá thể (đường đi) ngẫu nhiên"""
        individual = []
        
        for i in range(self.num_waypoints):
            # Nội suy tuyến tính từ start đến goal
            ratio = (i + 1) / (self.num_waypoints + 1)
            
            base_x = self.map.start[0] + ratio * (self.map.goal[0] - self.map.start[0])
            base_y = self.map.start[1] + ratio * (self.map.goal[1] - self.map.start[1])
            
            # Thêm nhiễu
            noise_x = np.random.uniform(-15, 15)
            noise_y = np.random.uniform(-15, 15)
            
            x = np.clip(base_x + noise_x, 0, self.map.width)
            y = np.clip(base_y + noise_y, 0, self.map.height)
            
            individual.append([x, y])
        
        return np.array(individual)
    
    def initialize_population(self):
        """Khởi tạo quần thể ban đầu"""
        self.population = []
        for _ in range(self.population_size):
            self.population.append(self.create_individual())
    
    def calculate_fitness(self, individual: np.ndarray) -> float:
        """
        Tính fitness cho cá thể (đường đi)
        Fitness thấp = tốt hơn
        """
        # Tạo đường đi đầy đủ: start -> waypoints -> goal
        full_path = [self.map.start] + individual.tolist() + [self.map.goal]
        
        # 1. Tính độ dài đường đi
        length = 0
        for i in range(len(full_path) - 1):
            dist = np.sqrt((full_path[i+1][0] - full_path[i][0])**2 + 
                          (full_path[i+1][1] - full_path[i][1])**2)
            length += dist
        
        # 2. Penalty cho va chạm
        collision_penalty = 0
        for i in range(len(full_path) - 1):
            if not self.map.is_valid_path(tuple(full_path[i]), tuple(full_path[i+1])):
                collision_penalty += 1000
        
        # 3. Penalty cho điểm nằm trong chướng ngại vật
        obstacle_penalty = 0
        for point in individual:
            if not self.map.is_valid_point(point[0], point[1]):
                obstacle_penalty += 500
        
        # 4. Penalty cho điểm nằm ngoài bản đồ
        out_of_bounds_penalty = 0
        for point in individual:
            if point[0] < 0 or point[0] > self.map.width or point[1] < 0 or point[1] > self.map.height:
                out_of_bounds_penalty += 500
        
        fitness = length + collision_penalty + obstacle_penalty + out_of_bounds_penalty
        return fitness
    
    def selection(self, fitnesses: List[float]) -> List[int]:
        """
        Chọn lọc dựa trên Tournament Selection
        Trả về indices của các cá thể được chọn
        """
        selected_indices = []
        
        # Giữ lại elite
        sorted_indices = np.argsort(fitnesses)
        for i in range(self.elite_size):
            selected_indices.append(sorted_indices[i])
        
        # Tournament selection cho phần còn lại
        tournament_size = 3
        while len(selected_indices) < self.population_size:
            # Chọn ngẫu nhiên tournament_size cá thể
            tournament_indices = np.random.choice(self.population_size, tournament_size, replace=False)
            tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
            
            # Chọn cá thể tốt nhất trong tournament
            winner_idx = tournament_indices[np.argmin(tournament_fitnesses)]
            selected_indices.append(winner_idx)
        
        return selected_indices
    
    def crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Lai ghép 2 cá thể cha mẹ để tạo 2 con
        Sử dụng uniform crossover
        """
        if np.random.random() > self.crossover_rate:
            return np.copy(parent1), np.copy(parent2)
        
        child1 = np.copy(parent1)
        child2 = np.copy(parent2)
        
        # Uniform crossover
        for i in range(self.num_waypoints):
            if np.random.random() < 0.5:
                child1[i] = parent2[i]
                child2[i] = parent1[i]
        
        return child1, child2
    
    def mutate(self, individual: np.ndarray) -> np.ndarray:
        """
        Đột biến cá thể
        """
        mutated = np.copy(individual)
        
        for i in range(self.num_waypoints):
            if np.random.random() < self.mutation_rate:
                # Thêm nhiễu ngẫu nhiên
                mutated[i][0] += np.random.uniform(-5, 5)
                mutated[i][1] += np.random.uniform(-5, 5)
                
                # Giới hạn trong bản đồ
                mutated[i][0] = np.clip(mutated[i][0], 0, self.map.width)
                mutated[i][1] = np.clip(mutated[i][1], 0, self.map.height)
        
        return mutated
    
    def find_path(self) -> Optional[List[Tuple[float, float]]]:
        """
        Tìm đường đi từ start đến goal
        
        Returns:
            Danh sách các điểm trên đường đi, hoặc None nếu không tìm thấy
        """
        start_time = time.time()
        
        if not self.map.start or not self.map.goal:
            print("Lỗi: Chưa đặt điểm start hoặc goal!")
            return None
        
        # Khởi tạo quần thể
        self.initialize_population()
        
        # Vòng lặp tiến hóa
        for generation in range(self.max_generations):
            # Tính fitness cho tất cả cá thể
            fitnesses = [self.calculate_fitness(ind) for ind in self.population]
            
            # Cập nhật best individual
            min_fitness_idx = np.argmin(fitnesses)
            if fitnesses[min_fitness_idx] < self.best_fitness:
                self.best_fitness = fitnesses[min_fitness_idx]
                self.best_individual = np.copy(self.population[min_fitness_idx])
            
            # Chọn lọc
            selected_indices = self.selection(fitnesses)
            selected_population = [self.population[i] for i in selected_indices]
            
            # Tạo thế hệ mới
            new_population = []
            
            # Giữ lại elite
            for i in range(self.elite_size):
                new_population.append(np.copy(selected_population[i]))
            
            # Lai ghép và đột biến
            while len(new_population) < self.population_size:
                # Chọn 2 cha mẹ
                parent1 = selected_population[np.random.randint(0, len(selected_population))]
                parent2 = selected_population[np.random.randint(0, len(selected_population))]
                
                # Lai ghép
                child1, child2 = self.crossover(parent1, parent2)
                
                # Đột biến
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            self.population = new_population
        
        self.computation_time = time.time() - start_time
        
        # Tạo đường đi cuối cùng
        if self.best_individual is not None:
            self.path = [self.map.start] + self.best_individual.tolist() + [self.map.goal]
            
            if self.best_fitness < 10000:
                return self.path
            else:
                print("GA: Không tìm thấy đường đi hợp lệ (có collision)!")
                return self.path
        
        print("GA: Không tìm thấy đường đi!")
        return None
    
    def get_path_length(self) -> float:
        """Tính độ dài đường đi"""
        if not self.path or len(self.path) < 2:
            return 0
        
        length = 0
        for i in range(len(self.path) - 1):
            length += np.sqrt((self.path[i+1][0] - self.path[i][0])**2 + 
                            (self.path[i+1][1] - self.path[i][1])**2)
        
        return length


if __name__ == "__main__":
    # Test thuật toán GA
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy GA
    print("Chạy thuật toán GA...")
    ga = GA(map_obj, population_size=50, num_waypoints=15, 
            max_generations=200, mutation_rate=0.1)
    path = ga.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {ga.get_path_length():.2f} m")
        print(f"  - Thời gian: {ga.computation_time:.4f} s")
        print(f"  - Best fitness: {ga.best_fitness:.2f}")
        
        # Vẽ kết quả
        map_obj.visualize()
        
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, marker='o', 
                    markersize=4, label='GA Path')
            plt.legend()
        
        plt.title(f'GA - Độ dài: {ga.get_path_length():.2f}m, Thời gian: {ga.computation_time:.4f}s')
        plt.show()
