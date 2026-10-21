import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class MapVisualizer:
    
    @staticmethod
    def visualize_map(map_info: Dict, route_indices: List[int] = None, 
                      paths: Dict = None, save_path: str = None):
        fig, ax = plt.subplots(figsize=(10, 10))
        
        width = map_info['width']
        height = map_info['height']
        grid = map_info['grid']
        start = map_info['start']
        targets = map_info['targets']
        
        ax.set_xlim(-0.5, width - 0.5)
        ax.set_ylim(-0.5, height - 0.5)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        
        for y in range(height):
            for x in range(width):
                if grid[y, x] == 1:
                    rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, 
                                             linewidth=0, facecolor='black')
                    ax.add_patch(rect)
        
        if paths and route_indices:
            for i in range(len(route_indices) - 1):
                from_idx = route_indices[i]
                to_idx = route_indices[i + 1]
                key = (from_idx, to_idx)
                
                if key in paths and paths[key] is not None:
                    path = paths[key]
                    x_coords = [p[0] for p in path]
                    y_coords = [p[1] for p in path]
                    ax.plot(x_coords, y_coords, 'b-', alpha=0.5, linewidth=1)
        
        ax.plot(start[0], start[1], 'go', markersize=15, label='Điểm bắt đầu', zorder=5)
        
        for i, target in enumerate(targets):
            ax.plot(target[0], target[1], 'r*', markersize=20, zorder=4)
            ax.text(target[0] + 0.3, target[1] - 0.3, str(i), fontsize=8)
        
        if route_indices:
            route_coords = [targets[i] if i < len(targets) else start for i in route_indices]
            for idx, point_idx in enumerate(route_indices[:-1]):
                if point_idx < len(targets):
                    target = targets[point_idx]
                    ax.text(target[0] - 0.5, target[1] + 0.5, f"{idx}", 
                           fontsize=10, fontweight='bold', color='blue')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Bản đồ TSP với Lộ trình Tối ưu')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Hình ảnh đã lưu tại: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def print_map_ascii(map_info: Dict):
        width = map_info['width']
        height = map_info['height']
        grid = map_info['grid']
        start = map_info['start']
        targets = map_info['targets']
        
        print("\n=== BẢN ĐỒ ASCII ===")
        
        for y in range(height):
            for x in range(width):
                if (x, y) == start:
                    print('S', end=' ')
                elif (x, y) in targets:
                    print('*', end=' ')
                elif grid[y, x] == 1:
                    print('█', end=' ')
                else:
                    print('.', end=' ')
            print()
        
        print(f"\nS = Điểm bắt đầu {start}")
        print(f"* = Điểm đích")
        print(f"█ = Chướng ngại vật")
        print(f". = Ô trống")


class MetricsCalculator:
    
    @staticmethod
    def calculate_metrics(cost_matrix: np.ndarray, route: List[int], 
                         total_cost: float) -> Dict:
        n = len(cost_matrix)
        
        avg_cost = total_cost / (len(route) - 1) if len(route) > 1 else 0
        
        min_per_node = []
        for i in range(n):
            row = [cost_matrix[i, j] for j in range(n) if i != j]
            if row:
                min_per_node.append(min(row))
        theoretical_lower_bound = sum(min_per_node) / 2 if min_per_node else 0
        
        if theoretical_lower_bound > 0:
            deviation = ((total_cost - theoretical_lower_bound) / theoretical_lower_bound) * 100
        else:
            deviation = 0
        
        visited_count = len(set(route[:-1]))
        
        metrics = {
            'total_cost': total_cost,
            'average_segment_cost': avg_cost,
            'theoretical_lower_bound': theoretical_lower_bound,
            'deviation_from_lower_bound_%': deviation,
            'number_of_points': n,
            'visited_points': visited_count,
            'number_of_segments': len(route) - 1
        }
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: Dict):
        print("\n=== CÁC CHỈ SỐ ĐÁNH GIÁ LỘNG TRÌNH ===")
        print(f"Tổng chi phí:                  {metrics['total_cost']:.2f}")
        print(f"Chi phí trung bình trên segment: {metrics['average_segment_cost']:.2f}")
        print(f"Số điểm cần ghé thăm:          {metrics['number_of_points']}")
        print(f"Số điểm đã ghé thăm:           {metrics['visited_points']}")
        print(f"Số segment:                    {metrics['number_of_segments']}")
        print(f"Giới hạn dưới lý thuyết:       {metrics['theoretical_lower_bound']:.2f}")
        print(f"Độ lệch từ giới hạn dưới:      {metrics['deviation_from_lower_bound_%']:.2f}%")
