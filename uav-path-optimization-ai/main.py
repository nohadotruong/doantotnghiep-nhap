"""
Module chính - Cấu hình và chạy toàn bộ thí nghiệm.
"""

import os
import sys
import json
import io
import numpy as np
from datetime import datetime
from generate_map import generate_random_map, generate_corridor_map, generate_maze_map, Map2D
from optimizer_runner import run_optimization_experiment
from compare_algorithm import AlgorithmComparator

# Hỗ trợ UTF-8 trên Windows
if sys.stdout.encoding != 'utf-8':
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder để xử lý numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def create_experiment_config() -> dict:
    """
    Tạo cấu hình cho thí nghiệm.
    
    Returns:
        Dictionary chứa cấu hình thí nghiệm
    """
    # Cấu hình mặc định cho thí nghiệm. Người dùng có thể sửa các tham số này
    # trước khi gọi `run_experiment` hoặc ghi ra file cấu hình.
    config = {
        # Cấu hình bản đồ
        'map_config': {
            'type': 'random',  # 'random', 'corridor', 'maze'
            'width': 50,
            'height': 50,
            'num_obstacles': 5,
            'obstacle_size_range': (2, 8)
        },
        
        # Cấu hình thí nghiệm
        'experiment_config': {
            'runs_per_algorithm': 5,  # Số lần chạy mỗi thuật toán
            'output_directory': 'results',
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
        },
        
        # Cấu hình cho các thuật toán meta-heuristic
        'algorithm_config': {
            'PSO': {
                'num_particles': 30,
                'max_iterations': 100,
                'num_waypoints': 5
            },
            'GWO': {
                'num_wolves': 30,
                'max_iterations': 100,
                'num_waypoints': 5
            },
            'GA': {
                'population_size': 30,
                'max_generations': 100,
                'num_waypoints': 5,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8
            },
            'SA': {
                'initial_temperature': 100,
                'cooling_rate': 0.95,
                'max_iterations': 500,
                'num_waypoints': 5
            },
            'RRT*': {
                'max_iter': 5000,
                'step_size': 2.0
            },
            'A*': {
                'step_size': 1.0
            }
        }
    }
    
    return config


def generate_map_from_config(config: dict) -> Map2D:
    """
    Tạo bản đồ dựa trên cấu hình.
    
    Args:
        config: Cấu hình thí nghiệm
        
    Returns:
        Đối tượng Map2D
    """
    # Lấy phần cấu hình bản đồ từ cấu hình tổng
    map_config = config['map_config']
    
    # Tạo Map2D tùy theo loại được chỉ định
    if map_config['type'] == 'random':
        # Bản đồ ngẫu nhiên với các chướng ngại vật được phân bố trong vùng
        map_obj = generate_random_map(
            map_config['width'],
            map_config['height'],
            map_config['num_obstacles'],
            map_config['obstacle_size_range']
        )
    elif map_config['type'] == 'corridor':
        map_obj = generate_corridor_map(
            map_config['width'],
            map_config['height'],
            num_corridors=3
        )
    elif map_config['type'] == 'maze':
        map_obj = generate_maze_map(
            map_config['width'],
            map_config['height'],
            maze_complexity=5
        )
    else:
        raise ValueError(f"Loại bản đồ không được hỗ trợ: {map_config['type']}")
    
    return map_obj


def print_config(config: dict):
    """
    In cấu hình thí nghiệm.
    
    Args:
        config: Cấu hình thí nghiệm
    """
    # In thông tin cấu hình để người dùng kiểm tra trước khi chạy
    print("="*80)
    print("CẤU HÌNH THÍ NGHIỆM TỐI ƯU HÓA ĐƯỜNG ĐI UAV")
    print("="*80)
    
    print("\n📍 Cấu hình bản đồ:")
    print(f"   Loại: {config['map_config']['type']}")
    print(f"   Kích thước: {config['map_config']['width']} x {config['map_config']['height']} m")
    print(f"   Số chướng ngại vật: {config['map_config']['num_obstacles']}")
    
    print("\n⚙️  Cấu hình thí nghiệm:")
    print(f"   Số lần chạy mỗi thuật toán: {config['experiment_config']['runs_per_algorithm']}")
    print(f"   Thư mục output: {config['experiment_config']['output_directory']}")
    print(f"   Thời gian bắt đầu: {config['experiment_config']['timestamp']}")
    
    print("\n" + "="*80)


def run_experiment(config: dict):
    """
    Chạy toàn bộ thí nghiệm.
    
    Args:
        config: Cấu hình thí nghiệm
    """
    # In cấu hình để biết các tham số đang được sử dụng
    print_config(config)
    
    # Tạo thư mục output (mỗi lần chạy có timestamp riêng)
    base_dir = config['experiment_config']['output_directory']
    timestamp = config['experiment_config']['timestamp']
    output_dir = os.path.join(base_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📁 Thư mục output: {os.path.abspath(output_dir)}")
    
    # Lưu cấu hình dưới dạng JSON (dễ tái sử dụng và ghi nhận tham số)
    config_file = os.path.join(output_dir, 'experiment_config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2, cls=NumpyEncoder)
    print(f"✅ Lưu cấu hình: {config_file}")
    
    # Tạo bản đồ theo cấu hình đã định
    print("\n🗺️  Tạo bản đồ...")
    map_obj = generate_map_from_config(config)
    
    # Lưu bản đồ
    map_file = os.path.join(output_dir, 'experiment_map.json')
    map_obj.save(map_file)
    
    # Vẽ và lưu ảnh bản đồ để người dùng có thể xem trực quan cấu trúc chướng ngại vật
    map_image = os.path.join(output_dir, 'experiment_map.png')
    map_obj.visualize(filename=map_image)
    print(f"✅ Bản đồ đã tạo: {map_image}")
    
    # Chạy các thuật toán: số lần chạy lấy từ cấu hình
    print("\n🚀 Chạy các thuật toán tối ưu hóa...")
    runs = config['experiment_config']['runs_per_algorithm']
    # Gọi hàm chạy thí nghiệm chính (chạy từng thuật toán nhiều lần)
    runner = run_optimization_experiment(map_obj, runs=runs, output_dir=output_dir)
    
    # So sánh kết quả
    print("\n📊 Tạo biểu đồ và bảng so sánh...")
    comparator = AlgorithmComparator(runner)
    comparator.plot_all_comparisons(output_dir)
    
    # In tóm tắt
    runner.print_summary()
    
    # Hiển thị và lưu hình ảnh đường đi tốt nhất của từng thuật toán
    print("\n" + "="*80)
    print("ĐƯỜNG ĐI TỐT NHẤT CỦA MỖI THUẬT TOÁN")
    print("="*80)
    
    for algorithm_name in runner.algorithms.keys():
        path, length = runner.get_best_path(algorithm_name)
        
        if path:
            filename = os.path.join(output_dir, f'best_path_{algorithm_name.lower().replace("*", "star")}.png')
            map_obj.visualize(path, filename=filename)
            print(f"{algorithm_name:10s}: Độ dài = {length:8.2f} m")
        else:
            print(f"{algorithm_name:10s}: Không tìm thấy đường đi")
    
    print("\n" + "="*80)
    print("✅ HOÀN THÀNH THÍ NGHIỆM!")
    print(f"📁 Kết quả lưu tại: {os.path.abspath(output_dir)}")
    print("="*80)


def main():
    """Hàm chính - Điểm vào chương trình."""
    # Tạo cấu hình
    config = create_experiment_config()
    
    # Có thể sửa đổi cấu hình tại đây
    # config['map_config']['type'] = 'corridor'
    # config['experiment_config']['runs_per_algorithm'] = 3
    
    # Chạy thí nghiệm
    try:
        run_experiment(config)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
