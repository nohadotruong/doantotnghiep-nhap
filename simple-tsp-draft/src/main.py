import sys
import os
import random
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_builder import MapBuilder
from astar import AStarPathfinder
from cost_matrix import CostMatrixBuilder
from greedy_tsp import GreedyTSP
from utils import MapVisualizer, MetricsCalculator


def run_tsp_pipeline():
    print("="*60)
    print("GIẢI BÀI TOÁN TRAVELING SALESMAN PROBLEM (TSP)")
    print("="*60)
    
    print("\n[BƯỚC 1] Khởi tạo bản đồ...")
    map_builder = MapBuilder(width=30, height=30)
    map_builder.add_obstacles(num_obstacles=20, obstacle_size=2)
    map_builder.add_targets(num_targets=5)
    map_builder.set_start_position()
    
    map_info = map_builder.get_map_info()
    
    print(f"  - Kích thước bản đồ: {map_info['width']}x{map_info['height']}")
    print(f"  - Điểm bắt đầu: {map_info['start']}")
    print(f"  - Số điểm đích: {len(map_info['targets'])}")
    print(f"  - Số chướng ngại vật: {len(map_info['obstacles'])}")
    
    MapVisualizer.print_map_ascii(map_info)
    
    print("\n[BƯỚC 2] Áp dụng thuật toán A* để tìm đường đi...")
    
    pathfinder = AStarPathfinder(
        grid=map_info['grid'],
        width=map_info['width'],
        height=map_info['height']
    )
    
    points = [map_info['start']] + map_info['targets']
    
    cost_builder = CostMatrixBuilder(pathfinder)
    cost_matrix = cost_builder.build_cost_matrix(points)
    
    print(f"  - Tính chi phí giữa {len(points)} điểm...")
    cost_builder.display_cost_matrix(points)
    
    print("\n[BƯỚC 3] Áp dụng thuật toán Greedy...")
    
    tsp_solver = GreedyTSP(cost_matrix)
    route, total_cost = tsp_solver.solve(start=0)
    
    print(f"  - Lộ trình tìm được: {route}")
    print(f"  - Tổng chi phí: {total_cost:.2f}")
    print("\n" + tsp_solver.get_route_description(points))
    
    print("\n[BƯỚC 4] Hiển thị kết quả và chỉ số đánh giá...")
    
    metrics = MetricsCalculator.calculate_metrics(cost_matrix, route, total_cost)
    MetricsCalculator.print_metrics(metrics)
    
    detailed_route = tsp_solver.get_detailed_route(points)
    
    route_indices = route
    
    print("\n  - Tạo hình ảnh visualization...")
    output_image = os.path.join(os.path.dirname(__file__), '..', 'tsp_route.png')
    os.makedirs(os.path.dirname(output_image), exist_ok=True)
    
    paths_viz = {}
    for (i, j), path in cost_builder.paths.items():
        if path is not None:
            paths_viz[(i, j)] = path
    
    MapVisualizer.visualize_map(map_info, route_indices, paths_viz, save_path=output_image)
    
    print("\n" + "="*60)
    print("TÓM TẮT KẾT QUẢ")
    print("="*60)
    print(f"Tổng chi phí lộ trình: {total_cost:.2f}")
    print(f"Số điểm đã ghé thăm: {metrics['visited_points']}/{metrics['number_of_points']}")
    print(f"Độ lệch từ giới hạn dưới: {metrics['deviation_from_lower_bound_%']:.2f}%")
    print(f"\nFile hình ảnh: {output_image}")
    print("="*60)


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    
    run_tsp_pipeline()