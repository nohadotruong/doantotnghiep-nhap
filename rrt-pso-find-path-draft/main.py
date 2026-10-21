"""
Main script for RRT-PSO Path Planning System
Chạy toàn bộ hệ thống tìm đường bằng RRT và tối ưu bằng PSO
"""

import time
import sys
import numpy as np
from environment.environment import UAVEnvironment
from algorithms.rrt import RRTPlanner
from algorithms.pso import PSOOptimizer
from utils.core import path_length
from utils.evaluation import report_metrics


def main():
    """Hàm chính"""
    
    print("="*60)
    print("RRT-PSO PATH PLANNING SYSTEM")
    print("="*60)
    
    # ============= PHẦN 1: TẠO ENVIRONMENT =============
    print("\n[SETUP] Tạo môi trường...")
    
    # Kích thước map
    WIDTH = 100
    HEIGHT = 100
    
    # Danh sách vật cản: (x, y, w, h)
    obstacles = [
        (20, 20, 10, 40),   # Vật cản 1
        (50, 10, 10, 50),   # Vật cản 2
        (70, 60, 20, 10)    # Vật cản 3
    ]
    
    # Tạo environment
    env = UAVEnvironment(WIDTH, HEIGHT, obstacles)
    
    # Điểm start và goal
    start = (10, 10)
    goal = (90, 90)
    
    print(f"  - Kích thước map: {WIDTH} x {HEIGHT}")
    print(f"  - Số vật cản: {len(obstacles)}")
    print(f"  - Start: {start}")
    print(f"  - Goal: {goal}")
    
    # ============= PHẦN 2: CHẠY RRT =============
    print("\n[RRT] Chạy thuật toán RRT...")
    
    rrt_planner = RRTPlanner(
        environment=env,
        start=start,
        goal=goal,
        step_size=5.0,
        max_iter=5000,
        goal_sample_rate=0.2
    )
    
    # Đo thời gian RRT
    rrt_start_time = time.time()
    rrt_path = rrt_planner.plan()
    rrt_end_time = time.time()
    rrt_time = rrt_end_time - rrt_start_time
    
    if rrt_path is None:
        print("[ERROR] RRT không tìm được đường!")
        return
    
    rrt_length = path_length(rrt_path)
    rrt_waypoints = len(rrt_path)
    
    print(f"  - Số điểm waypoint: {rrt_waypoints}")
    print(f"  - Độ dài đường: {rrt_length:.2f}")
    print(f"  - Thời gian: {rrt_time:.4f} seconds")
    
    # ============= PHẦN 3: CHẠY PSO =============
    print("\n[PSO] Chạy thuật toán PSO tối ưu hóa...")
    
    # Nếu RRT tìm được quá ít waypoint, không cần PSO
    if rrt_waypoints <= 2:
        print("  (Đường quá ngắn, bỏ qua tối ưu hóa)")
        pso_path = rrt_path
        pso_length = rrt_length
        pso_time = 0
    else:
        pso_optimizer = PSOOptimizer(
            environment=env,
            original_path=rrt_path,
            num_particles=30,
            iterations=100,
            w=0.7,
            c1=1.5,
            c2=1.5,
            w_length=0.25,           # 25% độ dài
            w_curvature=0.25,        # 25% độ uốn
            w_straightness=0.25,     # 25% tính thẳng
            w_safety=0.25            # 25% độ an toàn
        )
        
        # Đo thời gian PSO
        pso_start_time = time.time()
        pso_path = pso_optimizer.optimize()
        pso_end_time = time.time()
        pso_time = pso_end_time - pso_start_time
        
        pso_length = path_length(pso_path)
    
    pso_waypoints = len(pso_path)
    
    print(f"  - Số điểm waypoint: {pso_waypoints}")
    print(f"  - Độ dài đường: {pso_length:.2f}")
    print(f"  - Thời gian: {pso_time:.4f} seconds")
    
    # ============= PHẦN 4: BÁNG CÁO ĐÁNH GIÁ CHI TIẾT =============
    print("\n[EVALUATION] Đánh giá chi tiết...")
    
    # Sử dụng hàm report_metrics mới với đánh giá toàn diện
    evaluation_results = report_metrics(
        rrt_path=rrt_path,
        pso_path=pso_path,
        environment=env,
        rrt_time=rrt_time,
        pso_time=pso_time
    )
    
    # ============= PHẦN 5: SO SÁNH NHANH =============
    print("\n" + "="*60)
    print("QUICK SUMMARY")
    print("="*60)
    
    improvement = (rrt_length - pso_length) / rrt_length * 100
    
    print(f"\nPath Length Comparison:")
    print(f"  - RRT:         {rrt_length:.2f} units")
    print(f"  - RRT-PSO:     {pso_length:.2f} units")
    print(f"  - Improvement: {improvement:+.2f}%")
    
    print(f"\nExecution Time:")
    print(f"  - RRT:     {rrt_time:.4f} seconds")
    print(f"  - PSO:     {pso_time:.4f} seconds")
    print(f"  - Total:   {rrt_time + pso_time:.4f} seconds")
    
    # ============= PHẦN 6: VISUALIZE =============
    print("\n[VISUALIZATION] Vẽ kết quả...")
    
    env.visualize_multiple_paths(
        {
            'RRT': rrt_path,
            'RRT-PSO': pso_path
        },
        title="RRT-PSO Path Planning Result"
    )
    
    print("\n" + "="*60)
    print("Hoàn thành!")
    print("="*60)


if __name__ == "__main__":
    main()
