"""
examples.py - Các ví dụ sử dụng hệ thống tìm đường cho UAV
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Tạo thư mục
os.makedirs('./maps', exist_ok=True)
os.makedirs('./results', exist_ok=True)

# Tạo thư mục con theo datetime cho session này
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
results_dir = os.path.join('./results', f'examples_{timestamp}')
os.makedirs(results_dir, exist_ok=True)

print(f"\n{'='*80}")
print(f"Kết quả ví dụ sẽ được lưu vào: {results_dir}")
print(f"{'='*80}\n")


def example_1_create_map():
    """Ví dụ 1: Tạo bản đồ đơn giản"""
    print("\n" + "="*60)
    print("VÍ DỤ 1: TẠO BẢN ĐỒ")
    print("="*60)
    
    from generate_map import Map2D, Obstacle
    
    # Tạo bản đồ 100x100m
    map_obj = Map2D(width=100, height=100)
    
    # Thêm chướng ngại vật (x, y, width, height)
    map_obj.add_obstacle(Obstacle(30, 30, 20, 20))
    map_obj.add_obstacle(Obstacle(60, 60, 15, 15))
    map_obj.add_obstacle(Obstacle(20, 70, 10, 10))
    
    # Đặt điểm start và goal
    map_obj.set_start(10, 10)
    map_obj.set_goal(90, 90)
    
    # Lưu bản đồ
    map_obj.save('./maps/example_map.json')
    print("✓ Đã tạo và lưu bản đồ: ./maps/example_map.json")
    
    # Vẽ bản đồ
    map_obj.visualize(os.path.join(results_dir, 'example_map.png'))
    
    return map_obj


def example_2_run_astar(map_obj):
    """Ví dụ 2: Chạy thuật toán A*"""
    print("\n" + "="*60)
    print("VÍ DỤ 2: CHẠY THUẬT TOÁN A*")
    print("="*60)
    
    from astar import AStar
    
    # Khởi tạo A* với độ phân giải lưới 0.5m
    astar = AStar(map_obj, grid_resolution=0.5)
    
    # Tìm đường đi
    print("Đang tìm đường...")
    path = astar.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {astar.get_path_length():.2f} m")
        print(f"  - Thời gian: {astar.computation_time:.4f} s")
        print(f"  - Nodes explored: {astar.nodes_explored}")
        
        # Vẽ kết quả
        plt.figure(figsize=(10, 10))
        map_obj.visualize()
        path_array = np.array(path)
        plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, label='A* Path')
        plt.legend()
        plt.title(f'A* Path - Length: {astar.get_path_length():.2f}m')
        plt.savefig(os.path.join(results_dir, 'example_astar.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Đã lưu kết quả: {os.path.join(results_dir, 'example_astar.png')}")
    
    return path


def example_3_run_rrt_star(map_obj):
    """Ví dụ 3: Chạy thuật toán RRT*"""
    print("\n" + "="*60)
    print("VÍ DỤ 3: CHẠY THUẬT TOÁN RRT*")
    print("="*60)
    
    from rrt_star import RRTStar
    
    # Khởi tạo RRT*
    rrt = RRTStar(
        map_obj,
        max_iterations=2000,  # Số lần lặp
        step_size=2.0,        # Kích thước bước
        search_radius=8.0     # Bán kính tìm kiếm
    )
    
    # Tìm đường đi
    print("Đang tìm đường...")
    path = rrt.find_path()
    
    if path:
        print(f"✓ Tìm thấy đường đi!")
        print(f"  - Số điểm: {len(path)}")
        print(f"  - Độ dài: {rrt.get_path_length():.2f} m")
        print(f"  - Thời gian: {rrt.computation_time:.4f} s")
        print(f"  - Nodes trong cây: {len(rrt.nodes)}")
        
        # Vẽ kết quả với cây RRT
        plt.figure(figsize=(10, 10))
        
        # Vẽ các nhánh cây (mờ ở background)
        for node in rrt.nodes[::5]:  # Chỉ vẽ 1/5 để giảm clutter
            if node.parent:
                plt.plot([node.position[0], node.parent.position[0]],
                        [node.position[1], node.parent.position[1]],
                        'c-', alpha=0.2, linewidth=0.5)
        
        # Vẽ bản đồ và đường đi
        map_obj.visualize()
        if path:
            path_array = np.array(path)
            plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2, 
                    marker='o', markersize=4, label='RRT* Path')
        plt.legend()
        plt.title(f'RRT* Path - Length: {rrt.get_path_length():.2f}m')
        plt.savefig(os.path.join(results_dir, 'example_rrt_star.png'), dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Đã lưu kết quả: {os.path.join(results_dir, 'example_rrt_star.png')}")
    
    return path


def example_4_compare_algorithms(map_obj):
    """Ví dụ 4: So sánh các thuật toán"""
    print("\n" + "="*60)
    print("VÍ DỤ 4: SO SÁNH CÁC THUẬT TOÁN")
    print("="*60)
    
    from astar import AStar
    from rrt_star import RRTStar
    from pso import PSO
    from evaluate import PathEvaluator, compare_algorithms
    
    evaluator = PathEvaluator(map_obj)
    results = []
    
    # Chạy A*
    print("\n1. Chạy A*...")
    astar = AStar(map_obj, grid_resolution=1.0)
    path_astar = astar.find_path()
    if path_astar:
        metrics = evaluator.evaluate(path_astar, astar.computation_time, "A*")
        results.append(metrics)
        print(f"   ✓ Độ dài: {metrics['path_length']:.2f}m")
    
    # Chạy RRT*
    print("\n2. Chạy RRT*...")
    rrt = RRTStar(map_obj, max_iterations=1000)
    path_rrt = rrt.find_path()
    if path_rrt:
        metrics = evaluator.evaluate(path_rrt, rrt.computation_time, "RRT*")
        results.append(metrics)
        print(f"   ✓ Độ dài: {metrics['path_length']:.2f}m")
    
    # Chạy PSO
    print("\n3. Chạy PSO...")
    pso = PSO(map_obj, num_particles=30, num_waypoints=10, max_iterations=100)
    path_pso = pso.find_path()
    if path_pso:
        metrics = evaluator.evaluate(path_pso, pso.computation_time, "PSO")
        results.append(metrics)
        print(f"   ✓ Độ dài: {metrics['path_length']:.2f}m")
    
    # So sánh
    if len(results) > 0:
        print("\n4. So sánh kết quả...")
        compare_algorithms(results, save_path=os.path.join(results_dir, 'example_comparison.png'))
        print(f"✓ Đã lưu biểu đồ so sánh: {os.path.join(results_dir, 'example_comparison.png')}")


def example_5_evaluate_path(map_obj):
    """Ví dụ 5: Đánh giá chi tiết một đường đi"""
    print("\n" + "="*60)
    print("VÍ DỤ 5: ĐÁNH GIÁ CHI TIẾT ĐƯỜNG ĐI")
    print("="*60)
    
    from astar import AStar
    from evaluate import PathEvaluator
    
    # Tìm đường với A*
    astar = AStar(map_obj, grid_resolution=0.5)
    path = astar.find_path()
    
    if path:
        # Đánh giá
        evaluator = PathEvaluator(map_obj)
        metrics = evaluator.evaluate(path, astar.computation_time, "A*")
        
        # In chi tiết
        evaluator.print_metrics(metrics)
        
        print("\nGiải thích các chỉ số:")
        print("- Độ dài đường đi: Tổng khoảng cách từ start đến goal")
        print("- Độ mượt (góc quay): Tổng góc quay, càng nhỏ càng mượt")
        print("- Độ cong: Độ cong trung bình, càng nhỏ càng thẳng")
        print("- Khoảng cách an toàn: Khoảng cách TB đến chướng ngại vật")
        print("- Tỷ lệ tối ưu: So với đường thẳng (1.0 = tối ưu)")


def example_6_custom_map():
    """Ví dụ 6: Tạo bản đồ tùy chỉnh"""
    print("\n" + "="*60)
    print("VÍ DỤ 6: TẠO BẢN ĐỒ TÙY CHỈNH")
    print("="*60)
    
    from generate_map import Map2D, Obstacle, generate_random_map
    
    # Tạo bản đồ ngẫu nhiên
    print("\n1. Bản đồ ngẫu nhiên...")
    random_map = generate_random_map(
        width=100, 
        height=100, 
        num_obstacles=15,
        min_size=5,
        max_size=15
    )
    random_map.save('./maps/example_random.json')
    print("✓ Đã lưu: ./maps/example_random.json")
    
    # Tạo bản đồ maze-like
    print("\n2. Bản đồ maze...")
    maze_map = Map2D(100, 100)
    
    # Tạo các tường dọc
    for i in range(5):
        x = 20 + i * 15
        maze_map.add_obstacle(Obstacle(x, 10, 3, 30))
        maze_map.add_obstacle(Obstacle(x, 60, 3, 30))
    
    maze_map.set_start(5, 50)
    maze_map.set_goal(95, 50)
    maze_map.save('./maps/example_maze.json')
    print("✓ Đã lưu: ./maps/example_maze.json")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CÁC VÍ DỤ SỬ DỤNG HỆ THỐNG TÌM ĐƯỜNG CHO UAV")
    print("="*80)
    
    # Chạy các ví dụ
    map_obj = example_1_create_map()
    example_2_run_astar(map_obj)
    example_3_run_rrt_star(map_obj)
    example_4_compare_algorithms(map_obj)
    example_5_evaluate_path(map_obj)
    example_6_custom_map()
    
    print("\n" + "="*80)
    print("✓ HOÀN THÀNH TẤT CẢ VÍ DỤ!")
    print("="*80)
    print(f"\nCác file kết quả đã được lưu trong thư mục: {results_dir}")
    print("\nBạn có thể:")
    print("  1. Chạy test nhanh: python test_quick.py")
    print("  2. Chạy so sánh đầy đủ: python main.py")
    print("  3. Xem các ví dụ: python examples.py")
