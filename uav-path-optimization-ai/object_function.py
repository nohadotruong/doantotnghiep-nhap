"""
Module tính hàm mục tiêu (objective function) để đánh giá chất lượng đường đi.
Tiêu chí: độ dài đường đi, góc quay, và độ an toàn (khoảng cách với chướng ngại vật).
"""

import numpy as np
from typing import List, Tuple, Dict
from generate_map import Map2D


class ObjectiveFunction:
    """Lớp tính hàm mục tiêu đa tính chất."""
    
    def __init__(self, map_obj: Map2D):
        """
        Khởi tạo hàm mục tiêu.
        
        Args:
            map_obj: Đối tượng Map2D
        """
        self.map = map_obj
        self.weights = {
            'length': 1.0,      # Trọng số cho độ dài đường đi
            'smoothness': 0.5,  # Trọng số cho độ mượt (góc quay)
            'safety': 0.3       # Trọng số cho độ an toàn
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """
        Cập nhật trọng số.
        
        Args:
            weights: Dictionary chứa các trọng số
        """
        self.weights.update(weights)
    
    def calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính độ dài đường đi.
        
        Args:
            path: Danh sách các điểm trong đường đi
            
        Returns:
            Độ dài tổng cộng
        """
        # Nếu ít hơn 2 điểm thì không có đoạn để tính
        if len(path) < 2:
            return 0

        total_length = 0
        # Cộng dồn khoảng cách Euclid giữa các cặp điểm liên tiếp
        for i in range(len(path) - 1):
            p1 = np.array(path[i])
            p2 = np.array(path[i + 1])
            total_length += np.linalg.norm(p2 - p1)

        return total_length
    
    def calculate_turning_angle(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính tổng góc quay (độ không mượt).
        
        Args:
            path: Danh sách các điểm trong đường đi
            
        Returns:
            Tổng góc quay (độ)
        """
        # Tổng góc quay (độ) giữa các đoạn liên tiếp => càng nhỏ càng mượt
        if len(path) < 3:
            return 0

        total_angle = 0

        for i in range(1, len(path) - 1):
            p1 = np.array(path[i - 1])
            p2 = np.array(path[i])
            p3 = np.array(path[i + 1])

            # Vector từ p1->p2 và p2->p3
            v1 = p2 - p1
            v2 = p3 - p2

            # Nếu hai vector có độ dài > 0, tính góc giữa chúng
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                # Clamp để tránh giá trị ngoài [-1,1] do lỗi số học
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                # Cộng góc chuyển sang độ
                total_angle += np.degrees(angle)

        return total_angle
    
    def calculate_safety_cost(self, path: List[Tuple[float, float]], 
                             min_distance: float = 1.0) -> float:
        """
        Tính chi phí về an toàn dựa trên khoảng cách đến chướng ngại vật.
        
        Args:
            path: Danh sách các điểm trong đường đi
            min_distance: Khoảng cách tối thiểu an toàn
            
        Returns:
            Chi phí an toàn (càng nhỏ càng tốt)
        """
        # Chi phí an toàn: penalize nếu quá gần chướng ngại vật, ưu tiên giữ khoảng cách
        safety_cost = 0

        for point in path:
            distance = self.map.get_distance_to_obstacle(point[0], point[1])

            if distance < min_distance:
                # Nếu quá gần, hình phạt tăng theo bình phương khoảng cách thiếu hụt
                safety_cost += (min_distance - distance) ** 2
            else:
                # Nếu an toàn, vẫn cộng một khoản nhỏ khuyến khích giữ khoảng cách
                safety_cost += 1.0 / (1.0 + distance)

        return safety_cost
    
    def calculate_collision_penalty(self, path: List[Tuple[float, float]], 
                                   collision_penalty: float = 1000) -> float:
        """
        Tính hình phạt va chạm.
        
        Args:
            path: Danh sách các điểm trong đường đi
            collision_penalty: Giá trị hình phạt cho va chạm
            
        Returns:
            Hình phạt va chạm (0 nếu không va chạm)
        """
        # Hình phạt lớn cho các điểm nằm trong vùng va chạm
        penalty = 0

        for point in path:
            if self.map.is_collision(point[0], point[1], radius=0.5):
                penalty += collision_penalty

        return penalty
    
    def evaluate_path(self, path: List[Tuple[float, float]], 
                     include_collision: bool = True) -> Tuple[float, Dict]:
        """
        Đánh giá tổng thể chất lượng đường đi.
        
        Args:
            path: Danh sách các điểm trong đường đi
            include_collision: Có tính hình phạt va chạm không
            
        Returns:
            Tuple (điểm số tổng, dictionary chi tiết các thành phần)
        """
        # Tính các thành phần cấu thành điểm số
        length = self.calculate_path_length(path)
        turning_angle = self.calculate_turning_angle(path)
        safety_cost = self.calculate_safety_cost(path)
        collision_penalty = self.calculate_collision_penalty(path) if include_collision else 0

        # Chuẩn hóa về thang đo tương đối để kết hợp bằng trọng số
        normalized_length = length / max(self.map.width, self.map.height)
        normalized_angle = turning_angle / 360.0
        normalized_safety = safety_cost / len(path) if len(path) > 0 else 0

        # Tổng điểm là tổng trọng số của các thành phần + hình phạt va chạm
        total_score = (
            self.weights['length'] * normalized_length +
            self.weights['smoothness'] * normalized_angle +
            self.weights['safety'] * normalized_safety +
            collision_penalty
        )

        details = {
            'total_score': total_score,
            'path_length': length,
            'turning_angle': turning_angle,
            'safety_cost': safety_cost,
            'collision_penalty': collision_penalty,
            'normalized_length': normalized_length,
            'normalized_angle': normalized_angle,
            'normalized_safety': normalized_safety
        }

        return total_score, details
    
    def compare_paths(self, paths: List[List[Tuple[float, float]]]) -> List[Dict]:
        """
        So sánh nhiều đường đi.
        
        Args:
            paths: Danh sách các đường đi
            
        Returns:
            Danh sách các dictionary chứa thông tin đánh giá
        """
        results = []
        
        for i, path in enumerate(paths):
            score, details = self.evaluate_path(path)
            details['path_index'] = i
            results.append(details)
        
        # Sắp xếp theo điểm số
        results.sort(key=lambda x: x['total_score'])
        
        return results


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Chuẩn hóa giá trị vào khoảng [0, 1].
    
    Args:
        value: Giá trị cần chuẩn hóa
        min_val: Giá trị tối thiểu
        max_val: Giá trị tối đa
        
    Returns:
        Giá trị chuẩn hóa
    """
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def weighted_sum_evaluation(metrics: Dict[str, float], 
                           weights: Dict[str, float]) -> float:
    """
    Tính toán đánh giá dựa trên tổng trọng số.
    
    Args:
        metrics: Dictionary chứa các chỉ số
        weights: Dictionary chứa các trọng số
        
    Returns:
        Điểm số tổng
    """
    total_score = 0
    
    for metric_name, metric_value in metrics.items():
        if metric_name in weights:
            total_score += weights[metric_name] * metric_value
    
    return total_score


if __name__ == "__main__":
    # Ví dụ sử dụng
    from generate_map import generate_random_map
    
    # Tạo bản đồ và hàm mục tiêu
    map_obj = generate_random_map(50, 50, 5)
    obj_func = ObjectiveFunction(map_obj)
    
    # Ví dụ đường đi
    path1 = [
        (2, 2),
        (15, 15),
        (30, 30),
        (48, 48)
    ]
    
    path2 = [
        (2, 2),
        (10, 25),
        (35, 35),
        (48, 48)
    ]
    
    # Đánh giá đường đi
    score1, details1 = obj_func.evaluate_path(path1)
    score2, details2 = obj_func.evaluate_path(path2)
    
    print("Đường đi 1:")
    print(f"  Điểm số: {score1:.4f}")
    print(f"  Độ dài: {details1['path_length']:.2f}")
    print(f"  Góc quay: {details1['turning_angle']:.2f}°")
    
    print("\nĐường đi 2:")
    print(f"  Điểm số: {score2:.4f}")
    print(f"  Độ dài: {details2['path_length']:.2f}")
    print(f"  Góc quay: {details2['turning_angle']:.2f}°")
