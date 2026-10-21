import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from generate_map import Map2D
from astar import AStar

def main():
    """Chương trình chính"""
    
    print("=" * 70)
    print("UAV PATH PLANNING - A* ALGORITHM")
    print("=" * 70)
    
    # 1. Tạo bản đồ
    print("\n[1] Tạo bản đồ...")
    map_2d = Map2D(width=100, height=100)
    map_2d.generate_random_obstacles(num_obstacles=50, seed=None)
    print(f"    ✓ Đã tạo bản đồ {map_2d.width}x{map_2d.height}m")
    print(f"    ✓ Số vật cản: {len(map_2d.obstacles)}")
    
    # 2. Định nghĩa start và goal
    print("\n[2] Định nghĩa điểm start và goal...")
    start = (10, 10)
    goal = (90, 90)
    print(f"    ✓ Start: {start}")
    print(f"    ✓ Goal: {goal}")
    
    # Kiểm tra va chạm
    if map_2d.is_collision(*start):
        print("    ! Warning: Start point có va chạm!")
    if map_2d.is_collision(*goal):
        print("    ! Warning: Goal point có va chạm!")
    
    # 3. Chạy A*
    print("\n[3] Chạy thuật toán A*...")
    astar = AStar(map_2d, resolution=1.0)
    path = astar.find_path(start, goal)
    
    if path:
        path_length = astar.get_path_length(path)
        print(f"    ✓ Tìm được đường đi!")
        print(f"    ✓ Số waypoints: {len(path)}")
        print(f"    ✓ Độ dài đường đi: {path_length:.2f}m")
        
        # Khoảng cách Euclidean
        euclidean = np.sqrt((goal[0] - start[0])**2 + (goal[1] - start[1])**2)
        print(f"    ✓ Khoảng cách Euclidean: {euclidean:.2f}m")
        print(f"    ✓ Tỷ lệ: {path_length/euclidean:.2f}x")
    else:
        print("    ✗ Không tìm được đường đi!")
    
    # 4. Visualization
    print("\n[4] Tạo visualization...")
    fig, ax = map_2d.visualize(start=start, goal=goal, path=path,
                               title="UAV Path Planning - A* Algorithm")
    
    # Thêm thông tin
    if path:
        info_text = f"Obstacles: {len(map_2d.obstacles)}\n"
        info_text += f"Waypoints: {len(path)}\n"
        info_text += f"Path Length: {path_length:.2f}m"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # Lưu hình
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    filename = f"{timestamp}.png"
    output_file = f'output/{filename}'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"    ✓ Đã lưu: {filename}")
    
    # 5. Thống kê
    print("\n" + "=" * 70)
    print("THỐNG KÊ")
    print("=" * 70)
    print(f"Kích thước bản đồ: {map_2d.width} × {map_2d.height} m")
    print(f"Số vật cản: {len(map_2d.obstacles)}")
    print(f"Độ phân giải grid: {astar.resolution} m/cell")
    print(f"Kích thước grid: {astar.grid_width} × {astar.grid_height}")
    
    if path:
        print(f"\nĐường đi:")
        print(f"  - Số waypoints: {len(path)}")
        print(f"  - Độ dài: {path_length:.2f} m")
        print(f"  - Khoảng cách thẳng: {euclidean:.2f} m")
        print(f"  - Tỷ lệ: {path_length/euclidean:.2f}x")
    
    print("=" * 70)
    print("✓ HOÀN THÀNH!")
    print("=" * 70)
    
    plt.show()
    
    return map_2d, astar, path


if __name__ == "__main__":
    map_obj, astar_obj, path = main()