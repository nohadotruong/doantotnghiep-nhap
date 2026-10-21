"""
Script chạy thử các thuật toán với bản đồ có sẵn
"""
import sys
import io
import os
import json
import time
from datetime import datetime
from generate_map import Map2D

# Hỗ trợ UTF-8 trên Windows
if sys.stdout.encoding != 'utf-8':
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import các thuật toán
try:
    from algorithms.a_star import a_star_path_planning
    from algorithms.rrt_star import rrt_star_path_planning
    HAS_ALGORITHMS = True
except ImportError as e:
    print(f"⚠️  Cảnh báo: Không thể import thuật toán - {e}")
    HAS_ALGORITHMS = False


def run_algorithm_on_map(map_obj: Map2D, algorithm_name: str, algorithm_func):
    """
    Chạy một thuật toán trên bản đồ
    
    Args:
        map_obj: Đối tượng Map2D
        algorithm_name: Tên thuật toán
        algorithm_func: Hàm thuật toán
        
    Returns:
        (path, length, time_taken)
    """
    start_time = time.time()
    
    try:
        print(f"\n  🔄 Chạy {algorithm_name}...", end=" ")
        
        # Gọi thuật toán
        path = algorithm_func(map_obj)
        
        elapsed = time.time() - start_time
        
        if path:
            # Tính độ dài đường đi
            length = sum(
                ((path[i][0] - path[i+1][0])**2 + (path[i][1] - path[i+1][1])**2)**0.5
                for i in range(len(path) - 1)
            )
            
            print(f"✅ Hoàn thành trong {elapsed:.2f}s")
            print(f"      - Độ dài đường đi: {length:.2f} m")
            print(f"      - Số waypoint: {len(path)}")
            
            return path, length, elapsed
        else:
            print(f"⚠️  Không tìm thấy đường đi")
            return None, float('inf'), elapsed
    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Lỗi: {e}")
        return None, float('inf'), elapsed


def test_map_with_algorithms(map_file: str, output_dir: str = None):
    """
    Test bản đồ với các thuật toán có sẵn
    
    Args:
        map_file: Đường dẫn file bản đồ JSON
        output_dir: Thư mục lưu kết quả (tùy chọn)
    """
    if not os.path.exists(map_file):
        print(f"❌ Không tìm thấy file: {map_file}")
        return False
    
    print(f"\n{'='*70}")
    print(f"🗺️  Kiểm tra bản đồ: {os.path.basename(map_file)}")
    print(f"{'='*70}")
    
    # Tải bản đồ
    try:
        map_obj = Map2D.load(map_file)
        print(f"✓ Kích thước: {map_obj.width} x {map_obj.height} m")
        print(f"✓ Số chướng ngại vật: {len(map_obj.obstacles)}")
        print(f"✓ Start: {map_obj.start}, Goal: {map_obj.goal}")
    except Exception as e:
        print(f"❌ Lỗi khi tải bản đồ: {e}")
        return False
    
    # Kiểm tra start/goal hợp lệ
    start_valid = not map_obj.is_collision(map_obj.start[0], map_obj.start[1])
    goal_valid = not map_obj.is_collision(map_obj.goal[0], map_obj.goal[1])
    
    if not start_valid or not goal_valid:
        print(f"⚠️  Cảnh báo: Start hoặc Goal không hợp lệ")
        if not start_valid:
            print(f"   - Start [{map_obj.start[0]}, {map_obj.start[1]}] va chạm trực tiếp với chướng ngại vật")
        if not goal_valid:
            print(f"   - Goal [{map_obj.goal[0]}, {map_obj.goal[1]}] va chạm trực tiếp với chướng ngại vật")
    
    if not HAS_ALGORITHMS:
        print(f"\n⚠️  Không thể chạy thuật toán - các module không khả dụng")
        return False
    
    # Chạy các thuật toán
    print(f"\n🚀 Chạy các thuật toán:")
    results = {}
    
    # Test A*
    try:
        path, length, elapsed = run_algorithm_on_map(map_obj, "A*", a_star_path_planning)
        results['A*'] = {'path': path, 'length': length, 'time': elapsed}
    except Exception as e:
        print(f"❌ A* lỗi: {e}")
    
    # Test RRT*
    try:
        path, length, elapsed = run_algorithm_on_map(map_obj, "RRT*", rrt_star_path_planning)
        results['RRT*'] = {'path': path, 'length': length, 'time': elapsed}
    except Exception as e:
        print(f"❌ RRT* lỗi: {e}")
    
    # Hiển thị tóm tắt
    print(f"\n📊 Tóm tắt kết quả:")
    print(f"{'Thuật toán':<15} {'Độ dài':<15} {'Thời gian':<15} {'Trạng thái':<15}")
    print("-" * 60)
    
    best_length = float('inf')
    best_algo = None
    
    for algo_name, result in sorted(results.items()):
        status = "✅ Thành công" if result['path'] else "❌ Thất bại"
        length_str = f"{result['length']:.2f} m" if result['path'] else "N/A"
        time_str = f"{result['time']:.2f} s"
        
        print(f"{algo_name:<15} {length_str:<15} {time_str:<15} {status:<15}")
        
        if result['path'] and result['length'] < best_length:
            best_length = result['length']
            best_algo = algo_name
    
    if best_algo:
        print(f"\n🏆 Thuật toán tốt nhất: {best_algo} ({best_length:.2f} m)")
    
    # Lưu kết quả nếu được yêu cầu
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Lưu JSON
        result_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(map_file))[0]}_results.json")
        
        results_data = {}
        for algo_name, result in results.items():
            results_data[algo_name] = {
                'length': float(result['length']) if result['path'] else None,
                'time': float(result['time']),
                'status': 'success' if result['path'] else 'failed',
                'waypoints': len(result['path']) if result['path'] else 0
            }
        
        with open(result_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n✅ Kết quả lưu tại: {result_file}")
    
    return True


def main():
    """Hàm chính"""
    maps_dir = './maps'
    results_dir = './results/test_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not os.path.exists(maps_dir):
        print(f"❌ Thư mục không tồn tại: {maps_dir}")
        return
    
    # Danh sách bản đồ để test
    map_files = [
        os.path.join(maps_dir, 'random_map_1.json'),
        os.path.join(maps_dir, 'corridor_map_1.json'),
        # os.path.join(maps_dir, 'maze_map_1.json'),  # Bỏ qua maze vì start va chạm
    ]
    
    print("\n" + "🧪 CHẠY THỬ CÁC THUẬT TOÁN VỚI BẢN ĐỒ CÓ SẴN".center(70))
    
    successful = 0
    for map_file in map_files:
        if test_map_with_algorithms(map_file, output_dir=results_dir):
            successful += 1
    
    print(f"\n{'='*70}")
    print(f"✅ HOÀN THÀNH: {successful}/{len(map_files)} bản đồ test thành công")
    print(f"📁 Kết quả lưu tại: {os.path.abspath(results_dir)}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
