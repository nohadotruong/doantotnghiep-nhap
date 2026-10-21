"""
gwo.py - Thuật toán GWO (Grey Wolf Optimizer) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
from generate_map import Map2D
import time


class GWO:
    """Thuật toán GWO để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D,
                 num_wolves: int = 30,
                 num_waypoints: int = 15,
                 max_iterations: int = 200):
        """
        Args:
            map_obj: Bản đồ
            num_wolves: Số lượng sói (search agents)
            num_waypoints: Số điểm waypoint trên đường đi
            max_iterations: Số lần lặp tối đa
        """
        self.map = map_obj
        self.num_wolves = num_wolves
        self.num_waypoints = num_waypoints
        self.max_iterations = max_iterations
        
        self.path = []
        self.computation_time = 0
        
        # Khởi tạo bầy sói
        self.wolves = []
        self.alpha = None  # Sói tốt nhất
        self.beta = None   # Sói tốt thứ 2
        self.delta = None  # Sói tốt thứ 3
        
        self.alpha_fitness = float('inf')
        self.beta_fitness = float('inf')
        self.delta_fitness = float('inf')
    
    def initialize_wolves(self):
        """Khởi tạo vị trí cho các sói"""
        for _ in range(self.num_wolves):
            # Tạo wolf (đường đi) với waypoints ngẫu nhiên
            wolf = []
            
            for i in range(self.num_waypoints):
                # Nội suy tuyến tính từ start đến goal
                ratio = (i + 1) / (self.num_waypoints + 1)
                
                # Thêm nhiễu ngẫu nhiên
                base_x = self.map.start[0] + ratio * (self.map.goal[0] - self.map.start[0])
                base_y = self.map.start[1] + ratio * (self.map.goal[1] - self.map.start[1])
                
                # Thêm nhiễu
                noise_x = np.random.uniform(-15, 15)
                noise_y = np.random.uniform(-15, 15)
                
                x = np.clip(base_x + noise_x, 0, self.map.width)
                y = np.clip(base_y + noise_y, 0, self.map.height)
                
                wolf.append([x, y])
            
            self.wolves.append(np.array(wolf))
    
    def calculate_fitness(self, wolf: np.ndarray) -> float:
        """
        Tính fitness cho wolf (đường đi)
        Fitness thấp = tốt hơn
        """
        # Tạo đường đi đầy đủ: start -> waypoints -> goal
        full_path = [self.map.start] + wolf.tolist() + [self.map.goal]
        
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
        for point in wolf:
            if not self.map.is_valid_point(point[0], point[1]):
                obstacle_penalty += 500
        
        # 4. Penalty cho điểm nằm ngoài bản đồ
        out_of_bounds_penalty = 0
        for point in wolf:
            if point[0] < 0 or point[0] > self.map.width or point[1] < 0 or point[1] > self.map.height:
                out_of_bounds_penalty += 500
        
        fitness = length + collision_penalty + obstacle_penalty + out_of_bounds_penalty
        return fitness
    
    def update_wolves(self, iteration: int):
        """Cập nhật vị trí của các sói dựa trên alpha, beta, delta"""
        a = 2 - iteration * (2.0 / self.max_iterations)  # Giảm từ 2 về 0
        
        for i in range(self.num_wolves):
            for j in range(self.num_waypoints):
                # Cập nhật theo alpha
                r1 = np.random.random(2)
                r2 = np.random.random(2)
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                D_alpha = np.abs(C1 * self.alpha[j] - self.wolves[i][j])
                X1 = self.alpha[j] - A1 * D_alpha
                
                # Cập nhật theo beta
                r1 = np.random.random(2)
                r2 = np.random.random(2)
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                D_beta = np.abs(C2 * self.beta[j] - self.wolves[i][j])
                X2 = self.beta[j] - A2 * D_beta
                
                # Cập nhật theo delta
                r1 = np.random.random(2)
                r2 = np.random.random(2)
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                D_delta = np.abs(C3 * self.delta[j] - self.wolves[i][j])
                X3 = self.delta[j] - A3 * D_delta
                
                # Vị trí mới là trung bình của 3 vị trí
                self.wolves[i][j] = (X1 + X2 + X3) / 3.0
                
                # Giới hạn trong bản đồ
                self.wolves[i][j][0] = np.clip(self.wolves[i][j][0], 0, self.map.width)
                self.wolves[i][j][1] = np.clip(self.wolves[i][j][1], 0, self.map.height)
    
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
        
        # Khởi tạo bầy sói
        self.initialize_wolves()
        
        # Tính fitness ban đầu và tìm alpha, beta, delta
        for i in range(self.num_wolves):
            fitness = self.calculate_fitness(self.wolves[i])
            
            if fitness < self.alpha_fitness:
                self.delta_fitness = self.beta_fitness
                self.delta = np.copy(self.beta) if self.beta is not None else None
                
                self.beta_fitness = self.alpha_fitness
                self.beta = np.copy(self.alpha) if self.alpha is not None else None
                
                self.alpha_fitness = fitness
                self.alpha = np.copy(self.wolves[i])
                
            elif fitness < self.beta_fitness:
                self.delta_fitness = self.beta_fitness
                self.delta = np.copy(self.beta) if self.beta is not None else None
                
                self.beta_fitness = fitness
                self.beta = np.copy(self.wolves[i])
                
            elif fitness < self.delta_fitness:
                self.delta_fitness = fitness
                self.delta = np.copy(self.wolves[i])
        
        # Vòng lặp chính
        for iteration in range(self.max_iterations):
            # Cập nhật vị trí của các sói
            self.update_wolves(iteration)
            
            # Đánh giá fitness và cập nhật alpha, beta, delta
            for i in range(self.num_wolves):
                fitness = self.calculate_fitness(self.wolves[i])
                
                if fitness < self.alpha_fitness:
                    self.delta_fitness = self.beta_fitness
                    self.delta = np.copy(self.beta)
                    
                    self.beta_fitness = self.alpha_fitness
                    self.beta = np.copy(self.alpha)
                    
                    self.alpha_fitness = fitness
                    self.alpha = np.copy(self.wolves[i])
                    
                elif fitness < self.beta_fitness:
                    self.delta_fitness = self.beta_fitness
                    self.delta = np.copy(self.beta)
                    
                    self.beta_fitness = fitness
                    self.beta = np.copy(self.wolves[i])
                    
                elif fitness < self.delta_fitness:
                    self.delta_fitness = fitness
                    self.delta = np.copy(self.wolves[i])
        
        self.computation_time = time.time() - start_time
        
        # Tạo đường đi cuối cùng
        if self.alpha is not None:
            self.path = [self.map.start] + self.alpha.tolist() + [self.map.goal]
            
            # Kiểm tra có collision không
            if self.alpha_fitness < 10000:
                return self.path
            else:
                print("GWO: Không tìm thấy đường đi hợp lệ (có collision)!")
                return self.path
        
        print("GWO: Không tìm thấy đường đi!")
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
    # Test thuật toán GWO
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy GWO
    print("Chạy thuật toán GWO...")
    gwo = GWO(map_obj, num_wolves=30, num_waypoints=15, max_iterations=200)
    path = gwo.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {gwo.get_path_length():.2f} m")
        print(f"  - Thời gian: {gwo.computation_time:.4f} s")
        print(f"  - Alpha fitness: {gwo.alpha_fitness:.2f}")
        
        # Vẽ kết quả
        map_obj.visualize()
        
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, marker='o', 
                    markersize=4, label='GWO Path')
            plt.legend()
        
        plt.title(f'GWO - Độ dài: {gwo.get_path_length():.2f}m, Thời gian: {gwo.computation_time:.4f}s')
        plt.show()
