"""
Ví dụ sử dụng các module riêng lẻ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from map_builder import MapBuilder
from astar import AStarPathfinder
from cost_matrix import CostMatrixBuilder
from greedy_tsp import GreedyTSP
from utils import MapVisualizer, MetricsCalculator


def example_1_basic_pathfinding():
    """Ví dụ 1: Tìm đường đi cơ bản giữa hai điểm"""
    print("\n" + "="*60)
    print("VÍ DỤ 1: Tìm đường đi cơ bản")
    print("="*60)
    
    map_builder = MapBuilder(width=20, height=20)
    map_builder.add_obstacles(num_obstacles=10)
    map_builder.set_start_position(2, 2)
    
    map_info = map_builder.get_map_info()
    
    pathfinder = AStarPathfinder(
        grid=map_info['grid'],
        width=map_info['width'],
        height=map_info['height']
    )
    
    start = (2, 2)
    goal = (18, 18)
    
    path, cost = pathfinder.find_path(start, goal)
    
    if path:
        print(f"Tìm được đường đi từ {start} tới {goal}")
        print(f"Độ dài đường đi: {cost:.2f}")
        print(f"Số bước: {len(path)}")
    else:
        print(f"Không tìm được đường đi từ {start} tới {goal}")


def example_2_cost_matrix():
    """Ví dụ 2: Xây dựng ma trận chi phí"""
    print("\n" + "="*60)
    print("VÍ DỤ 2: Xây dựng ma trận chi phí")
    print("="*60)
    
    map_builder = MapBuilder(width=25, height=25)
    map_builder.add_obstacles(num_obstacles=15)
    map_builder.add_targets(num_targets=4)
    map_builder.set_start_position()
    
    map_info = map_builder.get_map_info()
    
    pathfinder = AStarPathfinder(
        grid=map_info['grid'],
        width=map_info['width'],
        height=map_info['height']
    )
    
    points = [map_info['start']] + map_info['targets']
    
    cost_builder = CostMatrixBuilder(pathfinder)
    cost_matrix = cost_builder.build_cost_matrix(points)
    
    cost_builder.display_cost_matrix(points)


def example_3_compare_algorithms():
    """Ví dụ 3: So sánh kết quả"""
    print("\n" + "="*60)
    print("VÍ DỤ 3: So sánh kết quả từ các thuật toán")
    print("="*60)
    
    map_builder = MapBuilder(width=30, height=30)
    map_builder.add_obstacles(num_obstacles=20)
    map_builder.add_targets(num_targets=5)
    map_builder.set_start_position()
    
    map_info = map_builder.get_map_info()
    
    pathfinder = AStarPathfinder(
        grid=map_info['grid'],
        width=map_info['width'],
        height=map_info['height']
    )
    
    points = [map_info['start']] + map_info['targets']
    
    cost_builder = CostMatrixBuilder(pathfinder)
    cost_matrix = cost_builder.build_cost_matrix(points)
    
    # Chạy Greedy từ các điểm bắt đầu khác nhau
    print("\nSo sánh Greedy từ các điểm bắt đầu:")
    print("-" * 40)
    
    results = []
    for start_point in range(len(points)):
        tsp_solver = GreedyTSP(cost_matrix)
        route, total_cost = tsp_solver.solve(start=start_point)
        results.append((start_point, route, total_cost))
        print(f"Bắt đầu từ điểm {start_point}: Chi phí = {total_cost:.2f}")
    
    # Tìm kết quả tốt nhất
    best = min(results, key=lambda x: x[2])
    print(f"\nKết quả tốt nhất: Bắt đầu từ điểm {best[0]}, Chi phí = {best[2]:.2f}")


def example_4_detailed_metrics():
    """Ví dụ 4: Tính toán các chỉ số chi tiết"""
    print("\n" + "="*60)
    print("VÍ DỤ 4: Các chỉ số đánh giá chi tiết")
    print("="*60)
    
    map_builder = MapBuilder(width=30, height=30)
    map_builder.add_obstacles(num_obstacles=20)
    map_builder.add_targets(num_targets=5)
    map_builder.set_start_position()
    
    map_info = map_builder.get_map_info()
    
    pathfinder = AStarPathfinder(
        grid=map_info['grid'],
        width=map_info['width'],
        height=map_info['height']
    )
    
    points = [map_info['start']] + map_info['targets']
    
    cost_builder = CostMatrixBuilder(pathfinder)
    cost_matrix = cost_builder.build_cost_matrix(points)
    
    tsp_solver = GreedyTSP(cost_matrix)
    route, total_cost = tsp_solver.solve(start=0)
    
    metrics = MetricsCalculator.calculate_metrics(cost_matrix, route, total_cost)
    
    print("\nChi tiết từng segment:")
    print("-" * 60)
    
    detailed = tsp_solver.get_detailed_route(points)
    for i, segment in enumerate(detailed['segments']):
        print(f"Segment {i}: {segment['from_coord']} → {segment['to_coord']}")
        print(f"  Chi phí: {segment['cost']:.2f}")
    
    print("\nTóm tắt chỉ số:")
    MetricsCalculator.print_metrics(metrics)


if __name__ == "__main__":
    print("CÁC VÍ DỤ SỬ DỤNG MODULE TSP SOLVER")
    
    # Chạy các ví dụ
    example_1_basic_pathfinding()
    example_2_cost_matrix()
    example_3_compare_algorithms()
    example_4_detailed_metrics()
    
    print("\n" + "="*60)
    print("Các ví dụ đã hoàn thành!")
    print("="*60)
