"""
Script test - Chạy thử với các bản đồ có sẵn trong thư mục maps
"""
import sys
import io
import os
import json
from generate_map import Map2D

# Hỗ trợ UTF-8 trên Windows
if sys.stdout.encoding != 'utf-8':
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_and_test_map(map_file: str):
    """Tải và kiểm tra bản đồ từ file JSON"""
    if not os.path.exists(map_file):
        print(f"❌ Không tìm thấy file: {map_file}")
        return False
    
    try:
        print(f"\n{'='*70}")
        print(f"📍 Kiểm tra bản đồ: {os.path.basename(map_file)}")
        print(f"{'='*70}")
        
        # Tải bản đồ từ file JSON
        with open(map_file, 'r') as f:
            map_data = json.load(f)
        
        print(f"✓ Kích thước bản đồ: {map_data['width']} x {map_data['height']} m")
        print(f"✓ Số chướng ngại vật: {len(map_data['obstacles'])}")
        print(f"✓ Điểm bắt đầu: {map_data['start']}")
        print(f"✓ Điểm đích: {map_data['goal']}")
        
        # Tạo đối tượng Map2D từ dữ liệu
        map_obj = Map2D.load(map_file)
        
        # Kiểm tra điểm hợp lệ
        start_valid = not map_obj.is_collision(map_obj.start[0], map_obj.start[1])
        goal_valid = not map_obj.is_collision(map_obj.goal[0], map_obj.goal[1])
        
        print(f"✓ Điểm bắt đầu hợp lệ: {'✅' if start_valid else '❌'}")
        print(f"✓ Điểm đích hợp lệ: {'✅' if goal_valid else '❌'}")
        
        # Kiểm tra khoảng cách tới các chướng ngại vật
        start_distance = map_obj.get_distance_to_obstacle(map_obj.start[0], map_obj.start[1])
        goal_distance = map_obj.get_distance_to_obstacle(map_obj.goal[0], map_obj.goal[1])
        
        print(f"✓ Khoảng cách từ start tới chướng ngại vật gần nhất: {start_distance:.2f} m")
        print(f"✓ Khoảng cách từ goal tới chướng ngại vật gần nhất: {goal_distance:.2f} m")
        
        # Hiển thị chi tiết các chướng ngại vật
        print(f"\n📦 Chi tiết các chướng ngại vật:")
        for i, obs in enumerate(map_data['obstacles'], 1):
            print(f"  {i}. Vị trí: ({obs['x']:.1f}, {obs['y']:.1f}), "
                  f"Kích thước: {obs['width']:.1f} x {obs['height']:.1f}")
        
        return True
    
    except Exception as e:
        print(f"❌ Lỗi khi tải bản đồ: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Hàm chính"""
    maps_dir = './maps'
    
    if not os.path.exists(maps_dir):
        print(f"❌ Thư mục không tồn tại: {maps_dir}")
        return
    
    # Danh sách các bản đồ để test
    map_files = [
        os.path.join(maps_dir, 'random_map_1.json'),
        os.path.join(maps_dir, 'corridor_map_1.json'),
        os.path.join(maps_dir, 'maze_map_1.json'),
    ]
    
    print("\n" + "🧪 BẮT ĐẦU TEST CÁC BẢN ĐỒ CÓ SẴN".center(70))
    
    successful = 0
    for map_file in map_files:
        if load_and_test_map(map_file):
            successful += 1
    
    print(f"\n{'='*70}")
    print(f"✅ HOÀN THÀNH TEST: {successful}/{len(map_files)} bản đồ hợp lệ")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
