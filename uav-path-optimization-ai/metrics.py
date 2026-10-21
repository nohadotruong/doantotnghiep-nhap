"""
Module tính các chỉ số để đánh giá hiệu suất các thuật toán.
"""

import numpy as np
from typing import List, Tuple, Dict
from object_function import ObjectiveFunction
from generate_map import Map2D


class Metrics:
    """Lớp tính các chỉ số hiệu suất."""
    
    @staticmethod
    def calculate_path_length(path: List[Tuple[float, float]]) -> float:
        """Tính độ dài đường đi (tổng khoảng cách giữa các waypoint).

        Trả về 0 nếu không có đoạn nào.
        """
        if len(path) < 2:
            return 0
        
        length = 0
        for i in range(len(path) - 1):
            length += np.sqrt((path[i+1][0] - path[i][0])**2 + 
                            (path[i+1][1] - path[i][1])**2)
        return length
    
    @staticmethod
    def calculate_smoothness(path: List[Tuple[float, float]]) -> float:
        """Tính độ mượt: tổng góc quay giữa các đoạn liên tiếp (độ).

        Giá trị càng nhỏ => đường càng mượt.
        """
        if len(path) < 3:
            return 0
        
        total_angle = 0
        for i in range(1, len(path) - 1):
            v1 = np.array(path[i]) - np.array(path[i-1])
            v2 = np.array(path[i+1]) - np.array(path[i])
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                total_angle += np.degrees(angle)
        
        return total_angle
    
    @staticmethod
    def calculate_safety_margin(path: List[Tuple[float, float]], 
                                map_obj: Map2D) -> float:
        """Khoảng cách nhỏ nhất từ bất kỳ waypoint nào tới chướng ngại vật gần nhất.

        Nếu không có chướng ngại vật trả về 0.
        """
        if not path:
            return 0
        
        min_distance = float('inf')
        
        for point in path:
            distance = map_obj.get_distance_to_obstacle(point[0], point[1])
            min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 0
    
    @staticmethod
    def calculate_average_safety_margin(path: List[Tuple[float, float]],
                                       map_obj: Map2D) -> float:
        """Khoảng cách trung bình từ các waypoint đến chướng ngại vật.

        Dùng để đánh giá mức an toàn trung bình của đường đi.
        """
        if not path:
            return 0
        
        total_distance = 0
        
        for point in path:
            distance = map_obj.get_distance_to_obstacle(point[0], point[1])
            total_distance += distance
        
        return total_distance / len(path)
    
    @staticmethod
    def calculate_path_efficiency(path: List[Tuple[float, float]],
                                 map_obj: Map2D) -> float:
        """
        Tính hiệu suất đường đi.
        Hiệu suất = khoảng cách đường thẳng / độ dài đường đi thực tế
        """
        if not path or len(path) < 2:
            return 0
        
        straight_distance = np.sqrt(
            (map_obj.goal[0] - map_obj.start[0])**2 +
            (map_obj.goal[1] - map_obj.start[1])**2
        )
        
        actual_length = Metrics.calculate_path_length(path)
        
        if actual_length == 0:
            return 0
        
        return straight_distance / actual_length
    
    @staticmethod
    def calculate_waypoints_count(path: List[Tuple[float, float]]) -> int:
        """Trả về số waypoint trong đường đi (bao gồm start và goal)."""
        return len(path)
    
    @staticmethod
    def calculate_execution_time_metric(execution_time: float) -> float:
        """Trả về thời gian thực thi; hiện tại không có chuẩn hóa thêm."""
        return execution_time
    
    @staticmethod
    def calculate_clearance_ratio(path: List[Tuple[float, float]],
                                 map_obj: Map2D, min_safe_distance: float = 2.0) -> float:
        """
        Tính tỷ lệ điểm dừng có khoảng cách an toàn.
        
        Args:
            path: Đường đi
            map_obj: Bản đồ
            min_safe_distance: Khoảng cách an toàn tối thiểu
            
        Returns:
            Tỷ lệ (0-1)
        """
        if not path:
            return 0
        
        safe_count = 0
        
        for point in path:
            distance = map_obj.get_distance_to_obstacle(point[0], point[1])
            if distance >= min_safe_distance:
                safe_count += 1
        
        return safe_count / len(path)
    
    @staticmethod
    def calculate_curvature(path: List[Tuple[float, float]]) -> float:
        """Ước lượng độ cong trung bình dùng cross-product giữa vector liên tiếp.

        Trả về 0 nếu không đủ điểm để tính.
        """
        if len(path) < 3:
            return 0
        
        total_curvature = 0
        count = 0
        
        for i in range(1, len(path) - 1):
            # Vector từ điểm i-1 đến i
            v1 = np.array(path[i]) - np.array(path[i-1])
            # Vector từ điểm i đến i+1
            v2 = np.array(path[i+1]) - np.array(path[i])
            
            # Tính độ cong (cross product / distance^2)
            len1 = np.linalg.norm(v1)
            len2 = np.linalg.norm(v2)
            
            if len1 > 0 and len2 > 0:
                cross = abs(v1[0] * v2[1] - v1[1] * v2[0])
                curvature = cross / (len1 * len2)
                total_curvature += curvature
                count += 1
        
        return total_curvature / count if count > 0 else 0
    
    @staticmethod
    def compute_all_metrics(path: List[Tuple[float, float]], 
                           map_obj: Map2D,
                           execution_time: float = 0) -> Dict:
        """
        Tính tất cả các chỉ số.
        
        Args:
            path: Đường đi
            map_obj: Bản đồ
            execution_time: Thời gian thực thi (giây)
            
        Returns:
            Dictionary chứa tất cả các chỉ số
        """
        # Thu thập toàn bộ metrics cần thiết cho so sánh và phân tích
        metrics = {
            'path_length': Metrics.calculate_path_length(path),
            'smoothness': Metrics.calculate_smoothness(path),
            'safety_margin': Metrics.calculate_safety_margin(path, map_obj),
            'average_safety_margin': Metrics.calculate_average_safety_margin(path, map_obj),
            'path_efficiency': Metrics.calculate_path_efficiency(path, map_obj),
            'waypoints_count': Metrics.calculate_waypoints_count(path),
            'execution_time': execution_time,
            'clearance_ratio': Metrics.calculate_clearance_ratio(path, map_obj),
            'curvature': Metrics.calculate_curvature(path)
        }
        
        return metrics


def normalize_metrics(results: List[Dict]) -> List[Dict]:
    """
    Chuẩn hóa các chỉ số để so sánh công bằng.
    
    Args:
        results: Danh sách kết quả từ các thuật toán
        
    Returns:
        Danh sách kết quả đã chuẩn hóa
    """
    # Lấy các giá trị min/max cho mỗi chỉ số
    metrics_keys = ['path_length', 'smoothness', 'execution_time', 'curvature']
    
    for key in metrics_keys:
        values = [r[key] for r in results if key in r]
        
        if values:
            min_val = min(values)
            max_val = max(values)
            
            for result in results:
                if key in result:
                    if max_val == min_val:
                        result[f'{key}_normalized'] = 0.5
                    else:
                        result[f'{key}_normalized'] = (result[key] - min_val) / (max_val - min_val)
    
    # Các chỉ số tốt hơn khi cao hơn
    metrics_higher_is_better = ['path_efficiency', 'clearance_ratio', 'average_safety_margin', 'safety_margin']
    
    for key in metrics_higher_is_better:
        values = [r[key] for r in results if key in r]
        
        if values:
            min_val = min(values)
            max_val = max(values)
            
            for result in results:
                if key in result:
                    if max_val == min_val:
                        result[f'{key}_normalized'] = 0.5
                    else:
                        result[f'{key}_normalized'] = (result[key] - min_val) / (max_val - min_val) if key not in ['path_efficiency', 'clearance_ratio', 'average_safety_margin', 'safety_margin'] else 1 - (result[key] - min_val) / (max_val - min_val)
    
    return results


if __name__ == "__main__":
    from generate_map import generate_random_map
    
    map_obj = generate_random_map(50, 50, 5)
    
    # Ví dụ đường đi
    path = [
        (2, 2),
        (15, 15),
        (30, 30),
        (48, 48)
    ]
    
    metrics = Metrics.compute_all_metrics(path, map_obj, execution_time=0.5)
    
    print("Các chỉ số:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
