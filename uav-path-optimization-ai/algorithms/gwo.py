"""
GWO (Grey Wolf Optimizer) để tối ưu hóa đường đi.

Mô tả:
- Mỗi con sói đại diện cho 1 giải pháp (mảng waypoint).
- Alpha, Beta, Delta là 3 cá thể tốt nhất hiện tại dùng làm tham chiếu.
- Các sói khác cập nhật vị trí theo alpha/beta/delta với hệ số ngẫu nhiên.
"""

import numpy as np
from typing import List, Tuple, Dict, Tuple as TupleType
from generate_map import Map2D
from object_function import ObjectiveFunction


class Wolf:
    """Một con sói trong GWO."""
    
    def __init__(self, position: np.ndarray):
        self.position = position.copy()
        self.fitness = float('inf')


class GWO:
    """Lớp thực hiện thuật toán GWO."""
    
    def __init__(self, map_obj: Map2D, num_wolves: int = 30, 
                 max_iterations: int = 100, num_waypoints: int = 5):
        """
        Khởi tạo GWO.
        
        Args:
            map_obj: Đối tượng Map2D
            num_wolves: Số lượng sói
            max_iterations: Số lần lặp tối đa
            num_waypoints: Số điểm dừng trong đường đi
        """
        self.map = map_obj
        self.num_wolves = num_wolves
        self.max_iterations = max_iterations
        self.num_waypoints = num_waypoints
        
        self.wolves = []
        self.alpha = None  # Sói alpha (tốt nhất)
        self.beta = None   # Sói beta (thứ 2)
        self.delta = None  # Sói delta (thứ 3)
        
        self.objective_function = ObjectiveFunction(map_obj)

        # Có thể lưu computation_time nếu cần
        self.computation_time = 0
    
    def initialize_wolves(self):
        """Khởi tạo bầy sói."""
        self.wolves = []
        
        for _ in range(self.num_wolves):
            # Mỗi wolf là ma trận (num_waypoints, 2)
            position = np.random.uniform(
                0,
                [self.map.width, self.map.height],
                size=(self.num_waypoints, 2)
            )

            wolf = Wolf(position)

            # Đánh giá fitness ban đầu
            path = self.position_to_path(position)
            wolf.fitness, _ = self.objective_function.evaluate_path(path)

            self.wolves.append(wolf)
        
        # Sắp xếp và chọn alpha, beta, delta
        self.wolves.sort(key=lambda w: w.fitness)
        self.alpha = Wolf(self.wolves[0].position.copy())
        self.alpha.fitness = self.wolves[0].fitness
        
        self.beta = Wolf(self.wolves[1].position.copy() if len(self.wolves) > 1 
                        else self.wolves[0].position.copy())
        self.beta.fitness = self.wolves[1].fitness if len(self.wolves) > 1 else self.wolves[0].fitness
        
        self.delta = Wolf(self.wolves[2].position.copy() if len(self.wolves) > 2 
                         else self.wolves[0].position.copy())
        self.delta.fitness = self.wolves[2].fitness if len(self.wolves) > 2 else self.wolves[0].fitness
    
    def position_to_path(self, position: np.ndarray) -> List[Tuple[float, float]]:
        """
        Chuyển đổi vị trí sói thành đường đi đầy đủ.
        
        Args:
            position: Ma trận tọa độ (num_waypoints, 2)
            
        Returns:
            Danh sách các điểm trong đường đi
        """
        # Chuyển ma trận waypoint thành danh sách các điểm (start + waypoints + goal)
        path = [self.map.start]

        for waypoint in position:
            x = np.clip(waypoint[0], 0, self.map.width)
            y = np.clip(waypoint[1], 0, self.map.height)
            path.append((x, y))

        path.append(self.map.goal)
        return path
    
    def update_position(self, current_wolf: Wolf, a: float, iteration: int):
        """
        Cập nhật vị trí của một con sói.
        
        Args:
            current_wolf: Con sói cần cập nhật
            a: Tham số giảm dần
            iteration: Lần lặp hiện tại
        """
        # Cập nhật từng waypoint của current_wolf dựa trên alpha/beta/delta
        for i in range(self.num_waypoints):
            # Hệ số A và C là ngẫu nhiên phụ thuộc vào a (a giảm dần theo iteration)
            A1 = 2 * a * np.random.random() - a
            C1 = 2 * np.random.random()

            A2 = 2 * a * np.random.random() - a
            C2 = 2 * np.random.random()

            A3 = 2 * a * np.random.random() - a
            C3 = 2 * np.random.random()

            # Công thức cập nhật vị trí theo alpha/beta/delta
            X_alpha = self.alpha.position[i] - A1 * np.abs(C1 * self.alpha.position[i] - current_wolf.position[i])
            X_beta = self.beta.position[i] - A2 * np.abs(C2 * self.beta.position[i] - current_wolf.position[i])
            X_delta = self.delta.position[i] - A3 * np.abs(C3 * self.delta.position[i] - current_wolf.position[i])

            current_wolf.position[i] = (X_alpha + X_beta + X_delta) / 3

            # Giữ trong giới hạn bản đồ
            current_wolf.position[i] = np.clip(
                current_wolf.position[i],
                [0, 0],
                [self.map.width, self.map.height]
            )
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Tìm đường đi sử dụng GWO.
        
        Returns:
            Đường đi tốt nhất tìm được
        """
        # Nếu thiếu start/goal -> không chạy
        if not self.map.start or not self.map.goal:
            return []

        # Khởi tạo và đánh giá ban đầu
        self.initialize_wolves()

        # Vòng lặp chính cập nhật vị trí sói
        for iteration in range(self.max_iterations):
            # a giảm dần từ 2 -> 0 theo số iteration
            a = 2 - 2 * (iteration / self.max_iterations)

            # Cập nhật vị trí và đánh giá fitness từng con
            for wolf in self.wolves:
                self.update_position(wolf, a, iteration)

                path = self.position_to_path(wolf.position)
                wolf.fitness, _ = self.objective_function.evaluate_path(path)

            # Sắp xếp theo fitness và cập nhật alpha/beta/delta
            self.wolves.sort(key=lambda w: w.fitness)

            if self.wolves[0].fitness < self.alpha.fitness:
                self.alpha = Wolf(self.wolves[0].position.copy())
                self.alpha.fitness = self.wolves[0].fitness

            if len(self.wolves) > 1 and self.wolves[1].fitness < self.beta.fitness:
                self.beta = Wolf(self.wolves[1].position.copy())
                self.beta.fitness = self.wolves[1].fitness

            if len(self.wolves) > 2 and self.wolves[2].fitness < self.delta.fitness:
                self.delta = Wolf(self.wolves[2].position.copy())
                self.delta.fitness = self.wolves[2].fitness

        # Trả về đường đi xây từ alpha (giải pháp tốt nhất tìm thấy)
        path = self.position_to_path(self.alpha.position)
        return path


def gwo_path_planning(map_obj: Map2D, num_wolves: int = 30, 
                     max_iterations: int = 100, 
                     num_waypoints: int = 5) -> List[Tuple[float, float]]:
    """
    Hàm tiện ích để chạy GWO.
    
    Args:
        map_obj: Đối tượng Map2D
        num_wolves: Số lượng sói
        max_iterations: Số lần lặp tối đa
        num_waypoints: Số điểm dừng
        
    Returns:
        Đường đi tìm được
    """
    gwo = GWO(map_obj, num_wolves, max_iterations, num_waypoints)
    return gwo.find_path()


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    path = gwo_path_planning(map_obj, num_wolves=30, max_iterations=50)
    
    if path:
        print(f"Tìm thấy đường đi với {len(path)} điểm")
        print(f"Độ dài: {sum(np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) for i in range(len(path)-1)):.2f}")
        map_obj.visualize(path, filename='results/gwo_example.png')
    else:
        print("Không tìm thấy đường đi")
