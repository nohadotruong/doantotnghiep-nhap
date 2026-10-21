"""
main.py - Chương trình chính để so sánh các thuật toán tìm đường cho UAV
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import argparse
import os
from datetime import datetime

from generate_map import Map2D, generate_random_map, generate_urban_map, generate_corridor_map
from astar import AStar
from rrt_star import RRTStar
from pso import PSO
from gwo import GWO
from sa import SA
from ga import GA
from evaluate import PathEvaluator, compare_algorithms, rank_algorithms


def visualize_all_paths(map_obj: Map2D, results: dict, save_path: str = None):
    """
    Vẽ tất cả các đường đi trên cùng một bản đồ
    
    Args:
        map_obj: Bản đồ
        results: Dictionary chứa kết quả của các thuật toán
        save_path: Đường dẫn lưu hình
    """
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Vẽ các chướng ngại vật
    for obstacle in map_obj.obstacles:
        rect = Rectangle(
            (obstacle.x, obstacle.y), 
            obstacle.width, 
            obstacle.height,
            linewidth=1, 
            edgecolor='black', 
            facecolor='gray',
            alpha=0.7
        )
        ax.add_patch(rect)
    
    # Vẽ điểm start và goal
    if map_obj.start:
        ax.plot(map_obj.start[0], map_obj.start[1], 'go', markersize=15, 
                label='Start', zorder=100)
    if map_obj.goal:
        ax.plot(map_obj.goal[0], map_obj.goal[1], 'r*', markersize=20, 
                label='Goal', zorder=100)
    
    # Màu sắc cho các thuật toán
    colors = {
        'A*': 'blue',
        'RRT*': 'green',
        'PSO': 'red',
        'GWO': 'purple',
        'SA': 'orange',
        'GA': 'cyan'
    }
    
    # Vẽ các đường đi
    for algo_name, result in results.items():
        if result['path'] is not None and len(result['path']) > 0:
            path_array = np.array(result['path'])
            ax.plot(path_array[:, 0], path_array[:, 1], 
                   color=colors.get(algo_name, 'black'),
                   linewidth=2, 
                   alpha=0.7,
                   label=f"{algo_name} ({result['metrics']['path_length']:.1f}m)",
                   marker='o',
                   markersize=3)
    
    ax.set_xlim(0, map_obj.width)
    ax.set_ylim(0, map_obj.height)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)
    ax.set_title('So sánh các thuật toán tìm đường cho UAV', fontsize=14, fontweight='bold')
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.show()


def run_single_algorithm(algo_name: str, map_obj: Map2D, evaluator: PathEvaluator):
    """
    Chạy một thuật toán
    
    Args:
        algo_name: Tên thuật toán
        map_obj: Bản đồ
        evaluator: Đối tượng đánh giá
        
    Returns:
        Dictionary chứa path và metrics
    """
    print(f"\n{'='*60}")
    print(f"Đang chạy {algo_name}...")
    print(f"{'='*60}")
    
    path = None
    computation_time = 0
    
    try:
        if algo_name == "A*":
            algorithm = AStar(map_obj, grid_resolution=0.5)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
            
        elif algo_name == "RRT*":
            algorithm = RRTStar(map_obj, max_iterations=2000, step_size=2.0, search_radius=8.0)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
            
        elif algo_name == "PSO":
            algorithm = PSO(map_obj, num_particles=50, num_waypoints=15, max_iterations=200)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
            
        elif algo_name == "GWO":
            algorithm = GWO(map_obj, num_wolves=30, num_waypoints=15, max_iterations=200)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
            
        elif algo_name == "SA":
            algorithm = SA(map_obj, num_waypoints=15, initial_temp=100.0, 
                         cooling_rate=0.95, max_iterations=100)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
            
        elif algo_name == "GA":
            algorithm = GA(map_obj, population_size=50, num_waypoints=15, 
                         max_generations=200, mutation_rate=0.1)
            path = algorithm.find_path()
            computation_time = algorithm.computation_time
        
        # Đánh giá
        if path:
            metrics = evaluator.evaluate(path, computation_time, algo_name)
            evaluator.print_metrics(metrics)
            return {'path': path, 'metrics': metrics}
        else:
            print(f"✗ {algo_name} không tìm thấy đường đi!")
            return {'path': None, 'metrics': None}
            
    except Exception as e:
        print(f"✗ Lỗi khi chạy {algo_name}: {str(e)}")
        return {'path': None, 'metrics': None}


def run_comparison(map_path: str, algorithms: list = None, output_dir: str = './results', 
                  num_runs: int = 1):
    """
    Chạy so sánh các thuật toán
    
    Args:
        map_path: Đường dẫn đến file bản đồ
        algorithms: Danh sách các thuật toán cần so sánh (None = tất cả)
        output_dir: Thư mục lưu kết quả
        num_runs: Số lần chạy mỗi thuật toán để tìm kết quả tối ưu (mặc định: 1)
    """
    # Tạo thư mục output với datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(output_dir, timestamp)
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Kết quả sẽ được lưu vào: {output_path}")
    
    if num_runs > 1:
        print(f"Chế độ: Mỗi thuật toán sẽ chạy {num_runs} lần và chọn kết quả tốt nhất")
    
    # Load bản đồ
    print(f"\nĐang load bản đồ từ {map_path}...")
    map_obj = Map2D.load(map_path)
    print(f"✓ Đã load bản đồ: {map_obj.width}x{map_obj.height}m, "
          f"{len(map_obj.obstacles)} chướng ngại vật")
    
    # Tạo evaluator
    evaluator = PathEvaluator(map_obj)
    
    # Danh sách thuật toán
    if algorithms is None:
        algorithms = ["A*", "RRT*", "PSO", "GWO", "SA", "GA"]
    
    print(f"\nSẽ chạy {len(algorithms)} thuật toán: {', '.join(algorithms)}")
    
    # Chạy từng thuật toán
    results = {}
    all_metrics = []
    all_statistics = []  # Lưu thống kê nếu chạy nhiều lần
    
    if num_runs > 1:
        # Sử dụng MultipleRunsOptimizer
        from multiple_runs import run_all_algorithms_optimized
        
        optimized_results = run_all_algorithms_optimized(
            map_obj, 
            num_runs=num_runs,
            algorithms=algorithms
        )
        
        for algo_name, opt_result in optimized_results.items():
            if opt_result['best_metrics'] is not None:
                results[algo_name] = {
                    'path': opt_result['best_path'],
                    'metrics': opt_result['best_metrics'],
                    'statistics': opt_result['statistics'],
                    'success_rate': opt_result['success_rate'],
                    'total_runs': opt_result['total_runs']
                }
                all_metrics.append(opt_result['best_metrics'])
                all_statistics.append({
                    'algorithm': algo_name,
                    **opt_result['statistics'],
                    'success_rate': opt_result['success_rate'],
                    'total_runs': opt_result['total_runs']
                })
            else:
                results[algo_name] = {
                    'path': None,
                    'metrics': None,
                    'statistics': None
                }
    else:
        # Chạy single run như cũ
        for algo_name in algorithms:
            result = run_single_algorithm(algo_name, map_obj, evaluator)
            results[algo_name] = result
            
            if result['metrics'] is not None:
                all_metrics.append(result['metrics'])
    
    # So sánh kết quả
    if len(all_metrics) > 0:
        print("\n" + "="*80)
        print("SO SÁNH KẾT QUẢ")
        print("="*80)
        
        # Vẽ biểu đồ so sánh
        compare_algorithms(all_metrics, 
                          save_path=os.path.join(output_path, 'comparison.png'))
        
        # Xếp hạng
        rankings = rank_algorithms(all_metrics)
        print("\nXẾP HẠNG THUẬT TOÁN:")
        print(rankings[['rank', 'algorithm', 'total_score']].to_string(index=False))
        
        # Lưu bảng xếp hạng ra file CSV
        rankings.to_csv(os.path.join(output_path, 'rankings.csv'), index=False)
        print(f"✓ Đã lưu bảng xếp hạng: {os.path.join(output_path, 'rankings.csv')}")
        
        # Vẽ tất cả đường đi
        visualize_all_paths(map_obj, results, 
                           save_path=os.path.join(output_path, 'all_paths.png'))
        
        # Lưu thông tin chi tiết về các metrics ra file CSV
        import pandas as pd
        metrics_df = pd.DataFrame(all_metrics)
        metrics_df.to_csv(os.path.join(output_path, 'metrics_detail.csv'), index=False)
        print(f"✓ Đã lưu metrics chi tiết: {os.path.join(output_path, 'metrics_detail.csv')}")
        
        # Nếu có statistics (multiple runs), lưu ra file
        if num_runs > 1 and all_statistics:
            stats_df = pd.DataFrame(all_statistics)
            stats_df.to_csv(os.path.join(output_path, 'statistics.csv'), index=False)
            print(f"✓ Đã lưu thống kê {num_runs} lần chạy: {os.path.join(output_path, 'statistics.csv')}")
        
        # Tạo file summary
        with open(os.path.join(output_path, 'summary.txt'), 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("KẾT QUẢ SO SÁNH THUẬT TOÁN TÌM ĐƯỜNG CHO UAV\n")
            f.write("="*80 + "\n\n")
            f.write(f"Thời gian chạy: {timestamp}\n")
            f.write(f"Bản đồ: {map_path}\n")
            f.write(f"Kích thước: {map_obj.width}x{map_obj.height}m\n")
            f.write(f"Số chướng ngại vật: {len(map_obj.obstacles)}\n")
            f.write(f"Start: {map_obj.start}\n")
            f.write(f"Goal: {map_obj.goal}\n")
            if num_runs > 1:
                f.write(f"Số lần chạy mỗi thuật toán: {num_runs}\n")
                f.write(f"Chế độ: Chọn kết quả tốt nhất trong {num_runs} lần chạy\n")
            f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("BẢNG XẾP HẠNG\n")
            f.write("="*80 + "\n")
            f.write(rankings[['rank', 'algorithm', 'total_score']].to_string(index=False))
            f.write("\n\n")
            
            f.write("="*80 + "\n")
            f.write("CHI TIẾT TỪNG THUẬT TOÁN\n")
            f.write("="*80 + "\n\n")
            for metric in all_metrics:
                f.write(f"Thuật toán: {metric['algorithm']}\n")
                f.write(f"  - Độ dài đường đi: {metric['path_length']:.2f} m\n")
                f.write(f"  - Thời gian: {metric['computation_time']:.4f} s\n")
                f.write(f"  - Thành công: {'Có' if metric['success'] else 'Không'}\n")
                f.write(f"  - Độ mượt: {metric['smoothness']:.2f}°\n")
                f.write(f"  - Tỷ lệ tối ưu: {metric['optimality_ratio']:.2f}x\n")
                f.write(f"  - Va chạm: {metric['num_collisions']}\n")
                f.write("\n")
            
            # Thêm statistics nếu có
            if num_runs > 1 and all_statistics:
                f.write("="*80 + "\n")
                f.write(f"THỐNG KÊ {num_runs} LẦN CHẠY\n")
                f.write("="*80 + "\n\n")
                for stat in all_statistics:
                    f.write(f"Thuật toán: {stat['algorithm']}\n")
                    f.write(f"  - Tỷ lệ thành công: {stat['success_rate']*100:.1f}% "
                           f"({int(stat['success_rate']*stat['total_runs'])}/{stat['total_runs']} lần)\n")
                    f.write(f"  - Độ dài TB: {stat['path_length_mean']:.2f} ± {stat['path_length_std']:.2f} m\n")
                    f.write(f"  - Độ dài min/max: {stat['path_length_min']:.2f} / {stat['path_length_max']:.2f} m\n")
                    f.write(f"  - Thời gian TB: {stat['computation_time_mean']:.4f} ± {stat['computation_time_std']:.4f} s\n")
                    f.write(f"  - Tỷ lệ có va chạm: {stat['collision_rate']*100:.1f}%\n")
                    f.write("\n")
        
        print(f"✓ Đã lưu file tổng kết: {os.path.join(output_path, 'summary.txt')}")
        
        print(f"\n✓ Đã lưu tất cả kết quả vào thư mục: {output_path}")
    else:
        print("\n✗ Không có thuật toán nào tìm được đường đi!")


def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(description='So sánh các thuật toán tìm đường cho UAV')
    
    parser.add_argument('--map', type=str, default='./maps/simple_map.json',
                       help='Đường dẫn đến file bản đồ')
    parser.add_argument('--algorithms', type=str, nargs='+', 
                       choices=['A*', 'RRT*', 'PSO', 'GWO', 'SA', 'GA'],
                       help='Danh sách thuật toán cần chạy (mặc định: tất cả)')
    parser.add_argument('--output', type=str, default='./results',
                       help='Thư mục lưu kết quả')
    parser.add_argument('--num-runs', type=int, default=1,
                       help='Số lần chạy mỗi thuật toán để tìm kết quả tối ưu (mặc định: 1, khuyến nghị: 10-30)')
    parser.add_argument('--generate-maps', action='store_true',
                       help='Tạo các bản đồ mẫu trước khi chạy')
    
    args = parser.parse_args()
    
    # Tạo bản đồ nếu cần
    if args.generate_maps:
        print("\n" + "="*80)
        print("TẠO BẢN ĐỒ MẪU")
        print("="*80)
        
        os.makedirs('./maps', exist_ok=True)
        
        # Bản đồ ngẫu nhiên
        print("\n1. Tạo bản đồ ngẫu nhiên...")
        random_map = generate_random_map(width=100, height=100, num_obstacles=20)
        random_map.save('./maps/random_map.json')
        print("✓ Đã lưu: ./maps/random_map.json")
        
        # Bản đồ đô thị
        print("\n2. Tạo bản đồ đô thị...")
        urban_map = generate_urban_map()
        urban_map.save('./maps/urban_map.json')
        print("✓ Đã lưu: ./maps/urban_map.json")
        
        # Bản đồ hành lang
        print("\n3. Tạo bản đồ hành lang...")
        corridor_map = generate_corridor_map()
        corridor_map.save('./maps/corridor_map.json')
        print("✓ Đã lưu: ./maps/corridor_map.json")
        
        print("\n✓ Đã tạo xong các bản đồ mẫu!")
    
    # Chạy so sánh
    print("\n" + "="*80)
    print("BẮT ĐẦU SO SÁNH CÁC THUẬT TOÁN")
    print("="*80)
    
    run_comparison(args.map, args.algorithms, args.output, args.num_runs)
    
    print("\n" + "="*80)
    print("HOÀN THÀNH!")
    print("="*80)


if __name__ == "__main__":
    # Ví dụ sử dụng trực tiếp (không qua command line)
    
    # Tạo bản đồ mẫu
    os.makedirs('./maps', exist_ok=True)
    os.makedirs('./results', exist_ok=True)
    
    print("\n" + "="*80)
    print("HỆ THỐNG TÌM ĐƯỜNG CHO UAV")
    print("="*80)
    
    # Tạo bản đồ đơn giản
    print("\nTạo bản đồ test...")
    from generate_map import Obstacle
    simple_map = Map2D(100, 100)
    simple_map.add_obstacle(Obstacle(30, 30, 20, 20))
    simple_map.add_obstacle(Obstacle(60, 60, 15, 15))
    simple_map.set_start(10, 10)
    simple_map.set_goal(90, 90)
    simple_map.save('./maps/test_map.json')
    
    # Chạy so sánh với tất cả thuật toán
    # Kết quả sẽ được lưu vào ./results/YYYY-MM-DD_HH-MM-SS/
    # num_runs=1: Chạy mỗi thuật toán 1 lần (nhanh)
    # num_runs=10: Chạy mỗi thuật toán 10 lần và chọn kết quả tốt nhất (chính xác hơn)
    run_comparison('./maps/test_map.json', output_dir='./results', num_runs=1)
