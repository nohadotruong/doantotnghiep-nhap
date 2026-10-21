"""
Simulated Annealing (SA) để tối ưu hóa đường đi.

Ghi chú:
- Mỗi giải pháp là một mảng `num_waypoints` các điểm.
- SA sinh neighbor bằng cách thêm nhiễu Gaussian cho một waypoint.
- Nếu neighbor tốt hơn thì chấp nhận; nếu tệ hơn vẫn có xác suất chấp nhận phụ thuộc vào
    nhiệt độ hiện tại (cho phép vượt qua cực tiểu cục bộ).
"""

import numpy as np
import math
from typing import List, Tuple, Dict
from generate_map import Map2D
from object_function import ObjectiveFunction


class SA:
    """Lớp thực hiện thuật toán SA."""
    
    def __init__(self, map_obj: Map2D, initial_temperature: float = 100,
                 cooling_rate: float = 0.95, max_iterations: int = 1000, 
                 num_waypoints: int = 5):
        """
        Khởi tạo SA.
        
        Args:
            map_obj: Đối tượng Map2D
            initial_temperature: Nhiệt độ ban đầu
            cooling_rate: Tỷ lệ giảm nhiệt độ
            max_iterations: Số lần lặp tối đa
            num_waypoints: Số điểm dừng
        """
        self.map = map_obj
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
        self.num_waypoints = num_waypoints
        
        self.current_solution = None
        self.current_cost = float('inf')
        self.best_solution = None
        self.best_cost = float('inf')
        
        self.objective_function = ObjectiveFunction(map_obj)

        # Computation time optional
        self.computation_time = 0
    
    def initialize_solution(self) -> np.ndarray:
        """
        Khởi tạo giải pháp ban đầu.
        
        Returns:
            Mảng tọa độ ban đầu
        """
        # Sinh ngẫu nhiên một giải pháp ban đầu (mỗi waypoint nằm trong bản đồ)
        solution = np.random.uniform(
            0,
            [self.map.width, self.map.height],
            size=(self.num_waypoints, 2)
        )

        return solution
    
    def solution_to_path(self, solution: np.ndarray) -> List[Tuple[float, float]]:
        """
        Chuyển đổi giải pháp thành đường đi.
        
        Args:
            solution: Ma trận tọa độ
            
        Returns:
            Danh sách các điểm trong đường đi
        """
        # Chuyển giải pháp (mảng waypoint) -> danh sách điểm path
        path = [self.map.start]

        for waypoint in solution:
            x = np.clip(waypoint[0], 0, self.map.width)
            y = np.clip(waypoint[1], 0, self.map.height)
            path.append((x, y))

        path.append(self.map.goal)
        return path
    
    def evaluate_solution(self, solution: np.ndarray) -> float:
        """
        Đánh giá chi phí của một giải pháp.
        
        Args:
            solution: Giải pháp cần đánh giá
            
        Returns:
            Chi phí (fitness score)
        """
        # Trả về cost (fitness) cho giải pháp - dùng trong so sánh
        path = self.solution_to_path(solution)
        cost, _ = self.objective_function.evaluate_path(path)
        return cost
    
    def generate_neighbor(self, solution: np.ndarray) -> np.ndarray:
        """
        Tạo một giải pháp lân cận.
        
        Args:
            solution: Giải pháp hiện tại
            
        Returns:
            Giải pháp lân cận
        """
        # Tạo neighbor bằng cách perturb một waypoint ngẫu nhiên bằng Gaussian noise
        neighbor = solution.copy()

        waypoint_idx = np.random.randint(0, self.num_waypoints)
        neighbor[waypoint_idx] += np.random.normal(0, 1, 2)

        # Clamp tọa độ vào trong bản đồ
        neighbor = np.clip(
            neighbor,
            [0, 0],
            [self.map.width, self.map.height]
        )

        return neighbor
    
    def acceptance_probability(self, current_cost: float, 
                              neighbor_cost: float, temperature: float) -> float:
        """
        Tính xác suất chấp nhận giải pháp mới.
        
        Args:
            current_cost: Chi phí giải pháp hiện tại
            neighbor_cost: Chi phí giải pháp lân cận
            temperature: Nhiệt độ hiện tại
            
        Returns:
            Xác suất chấp nhận
        """
        # Nếu giải pháp mới tốt hơn, luôn chấp nhận
        # Luật chấp nhận: luôn chấp nhận nếu tốt hơn; nếu không, chấp nhận với xác suất e^{-delta/T}
        if neighbor_cost < current_cost:
            return 1.0

        if temperature > 0:
            delta = neighbor_cost - current_cost
            return np.exp(-delta / temperature)

        return 0.0
    
    def find_path(self) -> List[Tuple[float, float]]:
        """
        Tìm đường đi sử dụng SA.
        
        Returns:
            Đường đi tốt nhất tìm được
        """
        # Nếu thiếu điểm start/goal -> không chạy
        if not self.map.start or not self.map.goal:
            return []

        # Khởi tạo current và best solution
        self.current_solution = self.initialize_solution()
        self.current_cost = self.evaluate_solution(self.current_solution)

        self.best_solution = self.current_solution.copy()
        self.best_cost = self.current_cost

        temperature = self.initial_temperature

        # Vòng lặp chính: sinh neighbor, chấp nhận theo xác suất, cập nhật best
        for iteration in range(self.max_iterations):
            neighbor_solution = self.generate_neighbor(self.current_solution)
            neighbor_cost = self.evaluate_solution(neighbor_solution)

            if self.acceptance_probability(self.current_cost, neighbor_cost, temperature) > np.random.random():
                # Chấp nhận neighbor làm current
                self.current_solution = neighbor_solution
                self.current_cost = neighbor_cost

            # Cập nhật best nếu cần
            if self.current_cost < self.best_cost:
                self.best_solution = self.current_solution.copy()
                self.best_cost = self.current_cost

            # Giảm nhiệt độ theo cooling_rate
            temperature *= self.cooling_rate

        # Trả về đường từ best_solution
        path = self.solution_to_path(self.best_solution)
        return path


def sa_path_planning(map_obj: Map2D, initial_temperature: float = 100,
                    cooling_rate: float = 0.95, max_iterations: int = 1000,
                    num_waypoints: int = 5) -> List[Tuple[float, float]]:
    """
    Hàm tiện ích để chạy SA.
    
    Args:
        map_obj: Đối tượng Map2D
        initial_temperature: Nhiệt độ ban đầu
        cooling_rate: Tỷ lệ giảm nhiệt độ
        max_iterations: Số lần lặp tối đa
        num_waypoints: Số điểm dừng
        
    Returns:
        Đường đi tìm được
    """
    sa = SA(map_obj, initial_temperature, cooling_rate, max_iterations, num_waypoints)
    return sa.find_path()


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    path = sa_path_planning(map_obj, initial_temperature=100, max_iterations=500)
    
    if path:
        print(f"Tìm thấy đường đi với {len(path)} điểm")
        print(f"Độ dài: {sum(np.linalg.norm(np.array(path[i+1]) - np.array(path[i])) for i in range(len(path)-1)):.2f}")
        map_obj.visualize(path, filename='results/sa_example.png')
    else:
        print("Không tìm thấy đường đi")
