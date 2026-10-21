"""
pso.py - Thuật toán PSO (Particle Swarm Optimization) cho UAV
"""
import numpy as np
from typing import List, Tuple, Optional
from generate_map import Map2D
import time


class PSO:
    """Thuật toán PSO để tìm đường đi cho UAV"""
    
    def __init__(self, map_obj: Map2D,
                 num_particles: int = 50,
                 num_waypoints: int = 15,
                 max_iterations: int = 200,
                 w: float = 0.7,
                 c1: float = 1.5,
                 c2: float = 1.5):
        """
        Args:
            map_obj: Bản đồ
            num_particles: Số lượng particles
            num_waypoints: Số điểm waypoint trên đường đi
            max_iterations: Số lần lặp tối đa
            w: Trọng số quán tính
            c1: Hệ số học cá nhân
            c2: Hệ số học xã hội
        """
        self.map = map_obj
        self.num_particles = num_particles
        self.num_waypoints = num_waypoints
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.path = []
        self.computation_time = 0
        
        # Khởi tạo particles
        self.particles = []
        self.velocities = []
        self.personal_best = []
        self.personal_best_fitness = []
        self.global_best = None
        self.global_best_fitness = float('inf')
    
    def initialize_particles(self):
        """Khởi tạo vị trí và vận tốc cho các particles"""
        for _ in range(self.num_particles):
            # Tạo particle (đường đi) với waypoints ngẫu nhiên
            particle = []
            
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
                
                particle.append([x, y])
            
            self.particles.append(np.array(particle))
            
            # Khởi tạo vận tốc
            velocity = np.random.uniform(-2, 2, (self.num_waypoints, 2))
            self.velocities.append(velocity)
            
            # Khởi tạo personal best
            self.personal_best.append(np.copy(self.particles[-1]))
            self.personal_best_fitness.append(float('inf'))
    
    def calculate_fitness(self, particle: np.ndarray) -> float:
        """
        Tính fitness cho particle (đường đi)
        Fitness thấp = tốt hơn
        """
        # Tạo đường đi đầy đủ: start -> waypoints -> goal
        full_path = [self.map.start] + particle.tolist() + [self.map.goal]
        
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
                collision_penalty += 1000  # Penalty lớn cho va chạm
        
        # 3. Penalty cho điểm nằm trong chướng ngại vật
        obstacle_penalty = 0
        for point in particle:
            if not self.map.is_valid_point(point[0], point[1]):
                obstacle_penalty += 500
        
        # 4. Penalty cho điểm nằm ngoài bản đồ
        out_of_bounds_penalty = 0
        for point in particle:
            if point[0] < 0 or point[0] > self.map.width or point[1] < 0 or point[1] > self.map.height:
                out_of_bounds_penalty += 500
        
        fitness = length + collision_penalty + obstacle_penalty + out_of_bounds_penalty
        return fitness
    
    def update_particles(self):
        """Cập nhật vị trí và vận tốc của particles"""
        for i in range(self.num_particles):
            # Cập nhật vận tốc
            r1 = np.random.random((self.num_waypoints, 2))
            r2 = np.random.random((self.num_waypoints, 2))
            
            cognitive = self.c1 * r1 * (self.personal_best[i] - self.particles[i])
            social = self.c2 * r2 * (self.global_best - self.particles[i])
            
            self.velocities[i] = self.w * self.velocities[i] + cognitive + social
            
            # Giới hạn vận tốc
            max_velocity = 5.0
            self.velocities[i] = np.clip(self.velocities[i], -max_velocity, max_velocity)
            
            # Cập nhật vị trí
            self.particles[i] += self.velocities[i]
            
            # Giới hạn vị trí trong bản đồ
            self.particles[i][:, 0] = np.clip(self.particles[i][:, 0], 0, self.map.width)
            self.particles[i][:, 1] = np.clip(self.particles[i][:, 1], 0, self.map.height)
    
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
        
        # Khởi tạo particles
        self.initialize_particles()
        
        # Tính fitness ban đầu
        for i in range(self.num_particles):
            fitness = self.calculate_fitness(self.particles[i])
            self.personal_best_fitness[i] = fitness
            
            if fitness < self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best = np.copy(self.particles[i])
        
        # Vòng lặp chính
        for iteration in range(self.max_iterations):
            # Cập nhật particles
            self.update_particles()
            
            # Đánh giá fitness
            for i in range(self.num_particles):
                fitness = self.calculate_fitness(self.particles[i])
                
                # Cập nhật personal best
                if fitness < self.personal_best_fitness[i]:
                    self.personal_best_fitness[i] = fitness
                    self.personal_best[i] = np.copy(self.particles[i])
                
                # Cập nhật global best
                if fitness < self.global_best_fitness:
                    self.global_best_fitness = fitness
                    self.global_best = np.copy(self.particles[i])
            
            # Giảm w theo thời gian (linearly decreasing inertia weight)
            self.w = 0.9 - (0.9 - 0.4) * iteration / self.max_iterations
        
        self.computation_time = time.time() - start_time
        
        # Tạo đường đi cuối cùng
        if self.global_best is not None:
            self.path = [self.map.start] + self.global_best.tolist() + [self.map.goal]
            
            # Kiểm tra có collision không
            if self.global_best_fitness < 10000:  # Ngưỡng chấp nhận được
                return self.path
            else:
                print("PSO: Không tìm thấy đường đi hợp lệ (có collision)!")
                return self.path  # Trả về dù có collision để visualize
        
        print("PSO: Không tìm thấy đường đi!")
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
    # Test thuật toán PSO
    from generate_map import Map2D
    import matplotlib.pyplot as plt
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Chạy PSO
    print("Chạy thuật toán PSO...")
    pso = PSO(map_obj, num_particles=50, num_waypoints=15, max_iterations=200)
    path = pso.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {pso.get_path_length():.2f} m")
        print(f"  - Thời gian: {pso.computation_time:.4f} s")
        print(f"  - Best fitness: {pso.global_best_fitness:.2f}")
        
        # Vẽ kết quả
        map_obj.visualize()
        
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, marker='o', 
                    markersize=4, label='PSO Path')
            plt.legend()
        
        plt.title(f'PSO - Độ dài: {pso.get_path_length():.2f}m, Thời gian: {pso.computation_time:.4f}s')
        plt.show()
