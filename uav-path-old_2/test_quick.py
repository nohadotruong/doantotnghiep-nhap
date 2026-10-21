"""
test_quick.py - Script test nhanh hệ thống
"""
import os
import sys
from datetime import datetime

# Tạo thư mục cần thiết
os.makedirs('./maps', exist_ok=True)
os.makedirs('./results', exist_ok=True)

print("="*80)
print("TEST NHANH HỆ THỐNG TÌM ĐƯỜNG CHO UAV")
print("="*80)
print(f"\nLưu ý: Kết quả sẽ được lưu vào ./results/YYYY-MM-DD_HH-MM-SS/")

# Bước 1: Tạo bản đồ đơn giản
print("\n1. Tạo bản đồ test...")
from generate_map import Map2D, Obstacle

simple_map = Map2D(100, 100)
simple_map.add_obstacle(Obstacle(30, 30, 20, 20))
simple_map.add_obstacle(Obstacle(60, 60, 15, 15))
simple_map.set_start(10, 10)
simple_map.set_goal(90, 90)
simple_map.save('./maps/test_map.json')
print("✓ Đã tạo bản đồ: ./maps/test_map.json")

# Bước 2: Test từng thuật toán
print("\n2. Test các thuật toán...")

from astar import AStar
from rrt_star import RRTStar
from pso import PSO
from gwo import GWO
from sa import SA
from ga import GA
from evaluate import PathEvaluator

evaluator = PathEvaluator(simple_map)

# Test A*
print("\n--- Test A* ---")
try:
    astar = AStar(simple_map, grid_resolution=1.0)
    path = astar.find_path()
    if path:
        print(f"✓ A* thành công: {astar.get_path_length():.2f}m, {astar.computation_time:.4f}s")
    else:
        print("✗ A* không tìm thấy đường")
except Exception as e:
    print(f"✗ A* lỗi: {e}")

# Test RRT*
print("\n--- Test RRT* ---")
try:
    rrt = RRTStar(simple_map, max_iterations=1000, step_size=2.0)
    path = rrt.find_path()
    if path:
        print(f"✓ RRT* thành công: {rrt.get_path_length():.2f}m, {rrt.computation_time:.4f}s")
    else:
        print("✗ RRT* không tìm thấy đường")
except Exception as e:
    print(f"✗ RRT* lỗi: {e}")

# Test PSO
print("\n--- Test PSO ---")
try:
    pso = PSO(simple_map, num_particles=30, num_waypoints=10, max_iterations=100)
    path = pso.find_path()
    if path:
        print(f"✓ PSO thành công: {pso.get_path_length():.2f}m, {pso.computation_time:.4f}s")
    else:
        print("✗ PSO không tìm thấy đường")
except Exception as e:
    print(f"✗ PSO lỗi: {e}")

# Test GWO
print("\n--- Test GWO ---")
try:
    gwo = GWO(simple_map, num_wolves=20, num_waypoints=10, max_iterations=100)
    path = gwo.find_path()
    if path:
        print(f"✓ GWO thành công: {gwo.get_path_length():.2f}m, {gwo.computation_time:.4f}s")
    else:
        print("✗ GWO không tìm thấy đường")
except Exception as e:
    print(f"✗ GWO lỗi: {e}")

# Test SA
print("\n--- Test SA ---")
try:
    sa = SA(simple_map, num_waypoints=10, max_iterations=50)
    path = sa.find_path()
    if path:
        print(f"✓ SA thành công: {sa.get_path_length():.2f}m, {sa.computation_time:.4f}s")
    else:
        print("✗ SA không tìm thấy đường")
except Exception as e:
    print(f"✗ SA lỗi: {e}")

# Test GA
print("\n--- Test GA ---")
try:
    ga = GA(simple_map, population_size=30, num_waypoints=10, max_generations=100)
    path = ga.find_path()
    if path:
        print(f"✓ GA thành công: {ga.get_path_length():.2f}m, {ga.computation_time:.4f}s")
    else:
        print("✗ GA không tìm thấy đường")
except Exception as e:
    print(f"✗ GA lỗi: {e}")

print("\n" + "="*80)
print("✓ TEST HOÀN THÀNH!")
print("="*80)
print("\nBạn có thể chạy so sánh đầy đủ với lệnh:")
print("  python main.py")
print("\nHoặc với bản đồ cụ thể:")
print("  python main.py --map ./maps/test_map.json")
