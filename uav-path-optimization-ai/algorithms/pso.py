"""
PSO (Particle Swarm Optimization) để tối ưu hóa đường đi.

Mô tả:
- Mỗi particle đại diện cho một dãy `num_waypoints` (mảng (N,2)).
- Particle có velocity, best_position cá nhân và global_best.
- Qua mỗi vòng lặp, cập nhật velocity dựa trên inertia, cognitive và social
    rồi cập nhật vị trí, đánh giá fitness (sử dụng `ObjectiveFunction`).
- Cuối cùng trả về đường đi xây từ `global_best_position`.
"""

import numpy as np
from typing import List, Tuple, Dict, Callable
from generate_map import Map2D
from object_function import ObjectiveFunction


class Particle:
    """Một hạt trong PSO."""
    
    def __init__(self, position: np.ndarray):
        self.position = position.copy()
        self.velocity = np.random.uniform(-1, 1, size=position.shape)
        self.best_position = position.copy()
        self.best_fitness = float('inf')
        self.fitness = float('inf')


class PSO:
    """Lớp thực hiện thuật toán PSO."""
    
    def __init__(self, map_obj: Map2D, num_particles: int = 30, 
                 max_iterations: int = 100, num_waypoints: int = 5):
        """
        Khởi tạo PSO.
        
        Args:
            map_obj: Đối tượng Map2D
            num_particles: Số lượng hạt
            max_iterations: Số lần lặp tối đa
            num_waypoints: Số điểm dừng trong đường đi
        """
        self.map = map_obj
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.num_waypoints = num_waypoints
        
        # Tham số PSO
        self.w = 0.7          # Hệ số quán tính
        self.c1 = 1.5         # Hệ số cognitie
        self.c2 = 1.5         # Hệ số social
        
        self.particles = []
        self.global_best_position = None
        self.global_best_fitness = float('inf')
        
        self.objective_function = ObjectiveFunction(map_obj)

        # computation_time có thể được ghi lại nếu muốn đo thời gian chạy
        self.computation_time = 0
    
    def initialize_particles(self):
        """Khởi tạo bầy hạt."""
        self.particles = []
        
        for _ in range(self.num_particles):
            # Mỗi hạt chứa tọa độ của các waypoint (num_waypoints x 2)
            position = np.random.uniform(
                0,
                [self.map.width, self.map.height],
                size=(self.num_waypoints, 2)
            )

            particle = Particle(position)

            # Đánh giá fitness ban đầu theo hàm objective
            path = self.position_to_path(position)
            particle.fitness, _ = self.objective_function.evaluate_path(path)
            particle.best_fitness = particle.fitness

            # Cập nhật global best nếu cần
            if particle.fitness < self.global_best_fitness:
                self.global_best_fitness = particle.fitness
                self.global_best_position = position.copy()

            self.particles.append(particle)
    
    def position_to_path(self, position: np.ndarray) -> List[Tuple[float, float]]:
        """
        Chuyển đổi vị trí hạt thành đường đi đầy đủ.
        
        Args:
            position: Ma trận tọa độ (num_waypoints, 2)
            
        Returns:
            Danh sách các điểm trong đường đi
        """
        # Chuyển ma trận waypoint thành danh sách điểm full path: start + waypoints + goal
        path = [self.map.start]

        for waypoint in position:
            x = np.clip(waypoint[0], 0, self.map.width)
            y = np.clip(waypoint[1], 0, self.map.height)
            path.append((x, y))

        path.append(self.map.goal)
        return path
    
    def smooth_path(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Làm mịn đường đi bằng cách loại bỏ các điểm không cần thiết.
        
        Args:
            path: Đường đi ban đầu
            
        Returns:
            Đường đi làm mịn
        """
        # Loại bỏ các waypoint không cần thiết nếu đoạn thẳng giữa hai waypoint liền kề không va chạm
        if len(path) <= 2:
            return path

        smoothed = [path[0]]

        for i in range(1, len(path) - 1):
            # Nếu điểm hiện tại không nằm trong vùng va chạm, kiểm tra xem có thể bỏ qua
            if not self.map.is_collision(path[i][0], path[i][1], radius=0.3):
                can_skip = True

                # Kiểm tra đoạn thẳng từ p1 đến p3 có va chạm không
                p1 = path[i - 1]
                p3 = path[i + 1]

                for t in np.linspace(0, 1, 20):
                    x = p1[0] + (p3[0] - p1[0]) * t
                    y = p1[1] + (p3[1] - p1[1]) * t

                    if self.map.is_collision(x, y, radius=0.3):
                        can_skip = False
                        break

                if not can_skip:
                    smoothed.append(path[i])
            else:
                smoothed.append(path[i])

        smoothed.append(path[-1])
        return smoothed
    
    def update_velocity_and_position(self):
        """Cập nhật vận tốc và vị trí của các hạt."""
        for particle in self.particles:
            # Cập nhật vận tốc
            cognitive = (self.c1 * np.random.random() * 
                        (particle.best_position - particle.position))
            social = (self.c2 * np.random.random() * 
                     (self.global_best_position - particle.position))
            
            # Velocity = inertia * v + cognitive_component + social_component
            particle.velocity = (self.w * particle.velocity +
                                cognitive + social)
            
            # Cập nhật vị trí
            # Cập nhật vị trí và clamp vào trong giới hạn bản đồ
            particle.position = particle.position + particle.velocity
            particle.position = np.clip(
                particle.position,
                [0, 0],
                [self.map.width, self.map.height]
            )
            
            # Đánh giá hạt
            path = self.position_to_path(particle.position)
            particle.fitness, _ = self.objective_function.evaluate_path(path)
            
            # Cập nhật best của hạt
            if particle.fitness < particle.best_fitness:
                particle.best_fitness = particle.fitness
                particle.best_position = particle.position.copy()
            
            # Cập nhật global best
            if particle.fitness < self.global_best_fitness:
                self.global_best_fitness = particle.fitness
                self.global_best_position = particle.position.copy()
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Tìm đường đi sử dụng PSO.
        
        Returns:
            Đường đi tốt nhất tìm được
        """
        # Nếu thiếu điểm start/goal thì không chạy
        if not self.map.start or not self.map.goal:
            return []

        # Khởi tạo các particle
        self.initialize_particles()

        # Vòng lặp chính cập nhật particle
        for iteration in range(self.max_iterations):
            self.update_velocity_and_position()

        # Lấy đường tốt nhất từ global best position và làm mịn
        path = self.position_to_path(self.global_best_position)
        path = self.smooth_path(path)

        return path


def pso_path_planning(map_obj: Map2D, num_particles: int = 30, 
                     max_iterations: int = 100, 
                     num_waypoints: int = 5) -> List[Tuple[float, float]]:
    """
    Hàm tiện ích để chạy PSO.
    
    Args:
        map_obj: Đối tượng Map2D
        num_particles: Số lượng hạt
        max_iterations: Số lần lặp tối đa
        num_waypoints: Số điểm dừng
        
    Returns:
        Đường đi tìm được
    """
    pso = PSO(map_obj, num_particles, max_iterations, num_waypoints)
    return pso.find_path()


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    path = pso_path_planning(map_obj, num_particles=30, max_iterations=50)
    
    if path:
        print(f"Tìm thấy đường đi với {len(path)} điểm")
        print(f"Độ dài: {sum(np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) for i in range(len(path)-1)):.2f}")
        map_obj.visualize(path, filename='results/pso_example.png')
    else:
        print("Không tìm thấy đường đi")
