"""
evaluate.py - Đánh giá hiệu suất các thuật toán tìm đường cho UAV
"""
import numpy as np
from typing import List, Tuple, Dict
from generate_map import Map2D
import matplotlib.pyplot as plt
import pandas as pd


class PathEvaluator:
    """Lớp đánh giá hiệu suất thuật toán tìm đường"""
    
    def __init__(self, map_obj: Map2D):
        self.map = map_obj
    
    def calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính độ dài đường đi
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            Độ dài đường đi (m)
        """
        if not path or len(path) < 2:
            return 0
        
        length = 0
        for i in range(len(path) - 1):
            dist = np.sqrt((path[i+1][0] - path[i][0])**2 + 
                          (path[i+1][1] - path[i][1])**2)
            length += dist
        
        return length
    
    def calculate_smoothness(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính độ mượt của đường đi (dựa trên tổng góc quay)
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            Tổng góc quay (độ) - càng nhỏ càng mượt
        """
        if not path or len(path) < 3:
            return 0
        
        total_angle = 0
        
        for i in range(1, len(path) - 1):
            # Tính vector từ i-1 đến i
            v1 = np.array([path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]])
            # Tính vector từ i đến i+1
            v2 = np.array([path[i+1][0] - path[i][0], path[i+1][1] - path[i][1]])
            
            # Tính góc giữa 2 vector
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)  # Tránh lỗi số học
                angle = np.arccos(cos_angle)
                total_angle += np.degrees(angle)
        
        return total_angle
    
    def calculate_curvature(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính độ cong trung bình của đường đi
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            Độ cong trung bình
        """
        if not path or len(path) < 3:
            return 0
        
        curvatures = []
        
        for i in range(1, len(path) - 1):
            p1 = np.array(path[i-1])
            p2 = np.array(path[i])
            p3 = np.array(path[i+1])
            
            # Tính bán kính đường tròn đi qua 3 điểm
            a = np.linalg.norm(p2 - p1)
            b = np.linalg.norm(p3 - p2)
            c = np.linalg.norm(p3 - p1)
            
            # Công thức Menger curvature
            if a > 0 and b > 0 and c > 0:
                s = (a + b + c) / 2
                area = np.sqrt(max(0, s * (s - a) * (s - b) * (s - c)))
                if area > 0:
                    curvature = 4 * area / (a * b * c)
                    curvatures.append(curvature)
        
        return np.mean(curvatures) if curvatures else 0
    
    def check_collision(self, path: List[Tuple[float, float]]) -> Tuple[bool, int]:
        """
        Kiểm tra va chạm trên đường đi
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            (has_collision, num_collisions)
        """
        if not path or len(path) < 2:
            return False, 0
        
        collision_count = 0
        
        for i in range(len(path) - 1):
            if not self.map.is_valid_path(path[i], path[i+1]):
                collision_count += 1
        
        return collision_count > 0, collision_count
    
    def calculate_clearance(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính khoảng cách trung bình đến chướng ngại vật gần nhất
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            Khoảng cách trung bình (m)
        """
        if not path:
            return 0
        
        clearances = []
        
        for point in path:
            min_dist = float('inf')
            
            for obstacle in self.map.obstacles:
                # Tính khoảng cách đến các cạnh của chướng ngại vật
                distances = [
                    abs(point[0] - obstacle.x),
                    abs(point[0] - (obstacle.x + obstacle.width)),
                    abs(point[1] - obstacle.y),
                    abs(point[1] - (obstacle.y + obstacle.height))
                ]
                
                # Khoảng cách gần nhất
                dist = min(distances)
                min_dist = min(min_dist, dist)
            
            clearances.append(min_dist)
        
        return np.mean(clearances) if clearances else 0
    
    def calculate_optimality(self, path: List[Tuple[float, float]]) -> float:
        """
        Tính tỷ lệ tối ưu (so với đường thẳng)
        
        Args:
            path: Danh sách các điểm trên đường đi
            
        Returns:
            Tỷ lệ độ dài đường đi / khoảng cách thẳng
        """
        if not path or len(path) < 2:
            return float('inf')
        
        # Khoảng cách thẳng từ start đến goal
        straight_dist = np.sqrt(
            (self.map.goal[0] - self.map.start[0])**2 + 
            (self.map.goal[1] - self.map.start[1])**2
        )
        
        # Độ dài đường đi thực tế
        path_length = self.calculate_path_length(path)
        
        return path_length / straight_dist if straight_dist > 0 else float('inf')
    
    def evaluate(self, path: List[Tuple[float, float]], 
                computation_time: float,
                algorithm_name: str = "") -> Dict:
        """
        Đánh giá toàn diện một đường đi
        
        Args:
            path: Danh sách các điểm trên đường đi
            computation_time: Thời gian tính toán (s)
            algorithm_name: Tên thuật toán
            
        Returns:
            Dictionary chứa các chỉ số đánh giá
        """
        has_collision, num_collisions = self.check_collision(path)
        
        metrics = {
            'algorithm': algorithm_name,
            'path_length': self.calculate_path_length(path),
            'num_waypoints': len(path),
            'computation_time': computation_time,
            'smoothness': self.calculate_smoothness(path),
            'curvature': self.calculate_curvature(path),
            'has_collision': has_collision,
            'num_collisions': num_collisions,
            'clearance': self.calculate_clearance(path),
            'optimality_ratio': self.calculate_optimality(path),
            'success': not has_collision
        }
        
        return metrics
    
    def print_metrics(self, metrics: Dict):
        """In các chỉ số đánh giá"""
        print(f"\n{'='*60}")
        print(f"Thuật toán: {metrics['algorithm']}")
        print(f"{'='*60}")
        print(f"Thành công: {'✓ Có' if metrics['success'] else '✗ Không'}")
        print(f"Độ dài đường đi: {metrics['path_length']:.2f} m")
        print(f"Số điểm waypoint: {metrics['num_waypoints']}")
        print(f"Thời gian tính toán: {metrics['computation_time']:.4f} s")
        print(f"Độ mượt (góc quay): {metrics['smoothness']:.2f}°")
        print(f"Độ cong trung bình: {metrics['curvature']:.6f}")
        print(f"Khoảng cách an toàn TB: {metrics['clearance']:.2f} m")
        print(f"Tỷ lệ tối ưu: {metrics['optimality_ratio']:.2f}x")
        print(f"Va chạm: {metrics['num_collisions']} điểm")
        print(f"{'='*60}\n")


def compare_algorithms(results: List[Dict], save_path: str = None):
    """
    So sánh các thuật toán
    
    Args:
        results: Danh sách các kết quả đánh giá
        save_path: Đường dẫn lưu biểu đồ
    """
    df = pd.DataFrame(results)
    
    # In bảng so sánh
    print("\n" + "="*80)
    print("BẢNG SO SÁNH CÁC THUẬT TOÁN")
    print("="*80)
    
    # Chọn các cột quan trọng
    cols = ['algorithm', 'success', 'path_length', 'computation_time', 
            'smoothness', 'optimality_ratio', 'clearance']
    print(df[cols].to_string(index=False))
    print("="*80 + "\n")
    
    # Vẽ biểu đồ so sánh
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # 1. Độ dài đường đi
    ax = axes[0, 0]
    df.plot(x='algorithm', y='path_length', kind='bar', ax=ax, legend=False, color='skyblue')
    ax.set_title('Độ dài đường đi', fontsize=12, fontweight='bold')
    ax.set_ylabel('Độ dài (m)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    
    # 2. Thời gian tính toán
    ax = axes[0, 1]
    df.plot(x='algorithm', y='computation_time', kind='bar', ax=ax, legend=False, color='lightcoral')
    ax.set_title('Thời gian tính toán', fontsize=12, fontweight='bold')
    ax.set_ylabel('Thời gian (s)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    
    # 3. Độ mượt
    ax = axes[0, 2]
    df.plot(x='algorithm', y='smoothness', kind='bar', ax=ax, legend=False, color='lightgreen')
    ax.set_title('Độ mượt (Góc quay)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tổng góc quay (°)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    
    # 4. Tỷ lệ tối ưu
    ax = axes[1, 0]
    df.plot(x='algorithm', y='optimality_ratio', kind='bar', ax=ax, legend=False, color='gold')
    ax.set_title('Tỷ lệ tối ưu', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tỷ lệ vs đường thẳng')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=1, color='r', linestyle='--', label='Optimal')
    
    # 5. Khoảng cách an toàn
    ax = axes[1, 1]
    df.plot(x='algorithm', y='clearance', kind='bar', ax=ax, legend=False, color='orchid')
    ax.set_title('Khoảng cách an toàn TB', fontsize=12, fontweight='bold')
    ax.set_ylabel('Khoảng cách (m)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    
    # 6. Tỷ lệ thành công
    ax = axes[1, 2]
    success_rate = df.groupby('algorithm')['success'].mean() * 100
    success_rate.plot(kind='bar', ax=ax, color='mediumseagreen')
    ax.set_title('Tỷ lệ thành công', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tỷ lệ (%)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim([0, 105])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()


def rank_algorithms(results: List[Dict]) -> pd.DataFrame:
    """
    Xếp hạng các thuật toán dựa trên nhiều tiêu chí
    
    Args:
        results: Danh sách các kết quả đánh giá
        
    Returns:
        DataFrame chứa điểm số và xếp hạng
    """
    df = pd.DataFrame(results)
    
    # Tính điểm cho từng tiêu chí (chuẩn hóa 0-100)
    scores = pd.DataFrame()
    scores['algorithm'] = df['algorithm']
    
    # Độ dài đường đi (ngắn hơn = tốt hơn)
    if df['path_length'].max() > 0:
        scores['length_score'] = 100 * (1 - (df['path_length'] - df['path_length'].min()) / 
                                        (df['path_length'].max() - df['path_length'].min() + 1e-6))
    else:
        scores['length_score'] = 50
    
    # Thời gian (nhanh hơn = tốt hơn)
    if df['computation_time'].max() > 0:
        scores['time_score'] = 100 * (1 - (df['computation_time'] - df['computation_time'].min()) / 
                                      (df['computation_time'].max() - df['computation_time'].min() + 1e-6))
    else:
        scores['time_score'] = 50
    
    # Độ mượt (mượt hơn = tốt hơn)
    if df['smoothness'].max() > 0:
        scores['smooth_score'] = 100 * (1 - (df['smoothness'] - df['smoothness'].min()) / 
                                        (df['smoothness'].max() - df['smoothness'].min() + 1e-6))
    else:
        scores['smooth_score'] = 50
    
    # Thành công
    scores['success_score'] = df['success'].astype(int) * 100
    
    # Tổng điểm (có trọng số)
    weights = {
        'success_score': 0.4,
        'length_score': 0.3,
        'time_score': 0.15,
        'smooth_score': 0.15
    }
    
    scores['total_score'] = (
        scores['success_score'] * weights['success_score'] +
        scores['length_score'] * weights['length_score'] +
        scores['time_score'] * weights['time_score'] +
        scores['smooth_score'] * weights['smooth_score']
    )
    
    # Xếp hạng
    scores = scores.sort_values('total_score', ascending=False)
    scores['rank'] = range(1, len(scores) + 1)
    
    return scores


if __name__ == "__main__":
    # Test đánh giá
    from generate_map import Map2D
    
    # Load bản đồ
    map_obj = Map2D.load('./maps/simple_map.json')
    
    # Tạo evaluator
    evaluator = PathEvaluator(map_obj)
    
    # Đường đi test
    test_path = [
        (10, 10),
        (30, 20),
        (50, 40),
        (70, 70),
        (90, 90)
    ]
    
    # Đánh giá
    metrics = evaluator.evaluate(test_path, computation_time=0.5, algorithm_name="Test")
    evaluator.print_metrics(metrics)
