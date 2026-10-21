"""
sa.py - Thuật toán SA (Simulated Annealing) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
from generate_map import Map2D
import time
import copy


class SA:
    """Thuật toán SA để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D,
                 num_waypoints: int = 15,
                 initial_temp: float = 100.0,
                 final_temp: float = 0.1,
                 cooling_rate: float = 0.95,
                 max_iterations: int = 1000):
        """
        Args:
            map_obj: Bản đồ
            num_waypoints: Số điểm waypoint trên đường đi
            initial_temp: Nhiệt độ ban đầu
            final_temp: Nhiệt độ cuối cùng
            cooling_rate: Tốc độ làm lạnh
            max_iterations: Số lần lặp tối đa ở mỗi nhiệt độ
        """
        self.map = map_obj
        self.num_waypoints = num_waypoints
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
        
        self.path = []
        self.computation_time = 0
        self.current_solution = None
        self.best_solution = None
        self.best_fitness = float('inf')
    
    def generate_initial_solution(self) -> np.ndarray:
        """Tạo nghiệm ban đầu (đường đi ngẫu nhiên)"""
        solution = []
        
        for i in range(self.num_waypoints):
            # Nội suy tuyến tính từ start đến goal
            ratio = (i + 1) / (self.num_waypoints + 1)
            
            base_x = self.map.start[0] + ratio * (self.map.goal[0] - self.map.start[0])
            base_y = self.map.start[1] + ratio * (self.map.goal[1] - self.map.start[1])
            
            # Thêm nhiễu
            noise_x = np.random.uniform(-10, 10)
            noise_y = np.random.uniform(-10, 10)
            
            x = np.clip(base_x + noise_x, 0, self.map.width)
            y = np.clip(base_y + noise_y, 0, self.map.height)
            
            solution.append([x, y])
        
        return np.array(solution)
    
    def calculate_fitness(self, solution: np.ndarray) -> float:
        """
        Tính fitness cho nghiệm (đường đi)
        Fitness thấp = tốt hơn
        """
        # Tạo đường đi đầy đủ: start -> waypoints -> goal
        full_path = [self.map.start] + solution.tolist() + [self.map.goal]
        
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
        for point in solution:
            if not self.map.is_valid_point(point[0], point[1]):
                obstacle_penalty += 500
        
        # 4. Penalty cho điểm nằm ngoài bản đồ
        out_of_bounds_penalty = 0
        for point in solution:
            if point[0] < 0 or point[0] > self.map.width or point[1] < 0 or point[1] > self.map.height:
                out_of_bounds_penalty += 500
        
        fitness = length + collision_penalty + obstacle_penalty + out_of_bounds_penalty
        return fitness
    
    def get_neighbor(self, solution: np.ndarray, temperature: float) -> np.ndarray:
        """
        Tạo nghiệm láng giềng bằng cách thay đổi ngẫu nhiên vị trí các waypoint
        """
        new_solution = np.copy(solution)
        
        # Chọn ngẫu nhiên một số waypoints để thay đổi
        num_points_to_change = np.random.randint(1, max(2, self.num_waypoints // 3))
        indices = np.random.choice(self.num_waypoints, num_points_to_change, replace=False)
        
        # Độ lớn nhiễu phụ thuộc vào nhiệt độ
        noise_scale = 5.0 * (temperature / self.initial_temp)
        
        for idx in indices:
            # Thêm nhiễu
            new_solution[idx][0] += np.random.uniform(-noise_scale, noise_scale)
            new_solution[idx][1] += np.random.uniform(-noise_scale, noise_scale)
            
            # Giới hạn trong bản đồ
            new_solution[idx][0] = np.clip(new_solution[idx][0], 0, self.map.width)
            new_solution[idx][1] = np.clip(new_solution[idx][1], 0, self.map.height)
        
        return new_solution
    
    def acceptance_probability(self, current_fitness: float, new_fitness: float, 
                              temperature: float) -> float:
        """
        Tính xác suất chấp nhận nghiệm mới
        """
        if new_fitness < current_fitness:
            return 1.0
        else:
            return np.exp(-(new_fitness - current_fitness) / temperature)
    
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
        
        # Khởi tạo nghiệm ban đầu
        self.current_solution = self.generate_initial_solution()
        current_fitness = self.calculate_fitness(self.current_solution)
        
        self.best_solution = np.copy(self.current_solution)
        self.best_fitness = current_fitness
        
        temperature = self.initial_temp
        iteration_count = 0
        
        # Vòng lặp chính
        while temperature > self.final_temp:
            for _ in range(self.max_iterations):
                iteration_count += 1
                
                # Tạo nghiệm láng giềng
                new_solution = self.get_neighbor(self.current_solution, temperature)
                new_fitness = self.calculate_fitness(new_solution)
                
                # Quyết định chấp nhận nghiệm mới
                if self.acceptance_probability(current_fitness, new_fitness, temperature) > np.random.random():
                    self.current_solution = new_solution
                    current_fitness = new_fitness
                    
                    # Cập nhật best solution
                    if current_fitness < self.best_fitness:
                        self.best_solution = np.copy(self.current_solution)
                        self.best_fitness = current_fitness
            
            # Làm lạnh
            temperature *= self.cooling_rate
        
        self.computation_time = time.time() - start_time
        
        # Tạo đường đi cuối cùng
        if self.best_solution is not None:
            self.path = [self.map.start] + self.best_solution.tolist() + [self.map.goal]
            
            if self.best_fitness < 10000:
                return self.path
            else:
                print("SA: Không tìm thấy đường đi hợp lệ (có collision)!")
                return self.path
        
        print("SA: Không tìm thấy đường đi!")
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
    # Test thuật toán SA
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy SA
    print("Chạy thuật toán SA...")
    sa = SA(map_obj, num_waypoints=15, initial_temp=100.0, 
            cooling_rate=0.95, max_iterations=100)
    path = sa.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {sa.get_path_length():.2f} m")
        print(f"  - Thời gian: {sa.computation_time:.4f} s")
        print(f"  - Best fitness: {sa.best_fitness:.2f}")
        
        # Vẽ kết quả
        map_obj.visualize()
        
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, marker='o', 
                    markersize=4, label='SA Path')
            plt.legend()
        
        plt.title(f'SA - Độ dài: {sa.get_path_length():.2f}m, Thời gian: {sa.computation_time:.4f}s')
        plt.show()
