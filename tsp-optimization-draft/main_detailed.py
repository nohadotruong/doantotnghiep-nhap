"""
Chương Trình Chi Tiết - Tối Ưu Hóa Đường Bay Đa Điểm
Detailed Program - Multi-Point Path Optimization

Trình tự:
1. Tạo map và các điểm đến
2. Tính ma trận chi phí và trực quan hóa
3. Chạy Greedy và PSO, so sánh chi tiết
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.environment import Environment
from src.algorithms import MultiPointPlanner, TSPSolver
from src.utils import PerformanceMetrics, PathVisualizer


def print_section(title):
    """In tiêu đề phần"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def visualize_distance_matrix(distance_matrix, save_path=None):
    """Trực quan hóa ma trận chi phí dưới dạng heatmap"""
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(distance_matrix, cmap="YlOrRd", aspect="auto")

    # Hiển thị giá trị trong ma trận
    for i in range(len(distance_matrix)):
        for j in range(len(distance_matrix)):
            text = ax.text(
                j,
                i,
                f"{distance_matrix[i, j]:.1f}",
                ha="center",
                va="center",
                color="black",
                fontsize=8,
            )

    ax.set_xticks(np.arange(len(distance_matrix)))
    ax.set_yticks(np.arange(len(distance_matrix)))
    ax.set_xticklabels([f"P{i}" for i in range(len(distance_matrix))])
    ax.set_yticklabels([f"P{i}" for i in range(len(distance_matrix))])

    plt.colorbar(im, ax=ax, label="Chi phí (Cost)")
    ax.set_title(
        "Ma Trận Chi Phí Đường Đi\nDistance Matrix", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("Điểm đích (To)", fontsize=12)
    ax.set_ylabel("Điểm xuất phát (From)", fontsize=12)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"✓ Đã lưu ma trận: {save_path}")

    return fig, ax


def main():
    """Chương trình chính"""

    print_section("BƯỚC 1: TẠO BẢN ĐỒ VÀ CÁC ĐIỂM ĐẾN")
    print("Creating environment and waypoints...")
    print("-" * 80)

    # Tạo bản đồ
    env = Environment(bounds=(0, 100, 0, 100))

    # Thêm chướng ngại vật
    env.add_circle_obstacle([30, 30], radius=8)
    env.add_circle_obstacle([70, 70], radius=8)
    env.add_rectangle_obstacle(40, 60, 40, 50)

    # Định nghĩa các điểm
    start = np.array([5.0, 5.0])
    goal = np.array([95.0, 95.0])
    waypoints = [
        np.array([25.0, 75.0]),  # P1
        np.array([50.0, 50.0]),  # P2
        np.array([75.0, 25.0]),  # P3
        np.array([75.0, 75.0]),  # P4
    ]

    all_points = np.array([start] + waypoints + [goal])

    print(f"📍 Điểm xuất phát (Start):    {start}")
    print(f"📍 Điểm đích (Goal):         {goal}")
    print(f"📍 Các điểm trung gian:      {len(waypoints)} điểm")
    for i, wp in enumerate(waypoints):
        print(f"   P{i+1}: {wp}")
    print(f"\n🚧 Chướng ngại vật:          {len(env.obstacles)} chướng ngại vật")
    print(f"📏 Kích thước bản đồ:        100 x 100")

    # Visualize bản đồ ban đầu
    print("\n📊 Vẽ bản đồ...")
    visualizer = PathVisualizer()
    visualizer.plot(
        env,
        path=[start, goal],
        waypoints=waypoints,
        title="Bản Đồ Ban Đầu - Initial Map",
        save_path="results/step1_environment.png",
    )
    print("✓ Đã lưu: results/step1_environment.png")

    # ========================================================================
    print_section("BƯỚC 2: TÍNH MA TRẬN CHI PHÍ ĐƯỜNG ĐI")
    print("Computing distance matrix using RRT*...")
    print("-" * 80)

    planner = MultiPointPlanner(env)

    print(f"\n⏳ Đang tính khoảng cách giữa {len(all_points)} điểm...")
    print("(Với RRT* iterations=2000 cho mỗi cặp điểm)\n")

    distance_matrix = planner._compute_distance_matrix(all_points, rrt_iterations=2000)

    # In ma trận chi phí
    print("💾 Ma Trận Chi Phí (Distance Matrix):")
    print("-" * 80)
    print("    ", end="")
    for j in range(len(all_points)):
        if j == 0:
            print("  Start  ", end="")
        elif j == len(all_points) - 1:
            print("  Goal   ", end="")
        else:
            print(f"   P{j}   ", end="")
    print()

    for i in range(len(distance_matrix)):
        if i == 0:
            print("Start", end="")
        elif i == len(all_points) - 1:
            print("Goal ", end="")
        else:
            print(f" P{i}  ", end="")

        for j in range(len(distance_matrix)):
            cost = distance_matrix[i, j]
            if cost == float("inf"):
                print(f"   ∞   ", end="")
            else:
                print(f" {cost:6.2f}", end="")
        print()

    # Trực quan hóa ma trận
    print("\n📈 Trực quan hóa ma trận chi phí...")
    visualize_distance_matrix(
        distance_matrix, save_path="results/step2_distance_matrix.png"
    )

    # Thống kê ma trận
    valid_distances = distance_matrix[distance_matrix != float("inf")]
    print(f"\n📊 Thống kê ma trận:")
    print(
        f"   Min: {valid_distances.min():.2f},  Max: {valid_distances.max():.2f},  Mean: {valid_distances.mean():.2f}"
    )

    # ========================================================================
    print_section("BƯỚC 3: CHẠY GREEDY - TÌM KIẾM HÀNG XÓM GẦN NHẤT")
    print("Running Greedy Nearest Neighbor algorithm...")
    print("-" * 80)

    tsp_solver = TSPSolver(all_points, distance_matrix)
    greedy_order, greedy_cost = tsp_solver.solve_greedy(start_idx=0)

    print(f"\n✓ Thuật toán Greedy hoàn thành!")
    print(f"Thứ tự thăm điểm (Order): {greedy_order}")
    print(f"\nChi tiết thứ tự:")
    for idx, point_id in enumerate(greedy_order):
        if point_id == 0:
            print(f"  {idx+1}. Start (điểm xuất phát)")
        elif point_id == len(all_points) - 1:
            print(f"  {idx+1}. Goal (điểm đích)")
        else:
            print(f"  {idx+1}. P{point_id} (điểm trung gian)")

    print(f"\n💰 Chi phí tổng cộng Greedy: {greedy_cost:.4f}")

    # Xây dựng đường đi Greedy
    print(f"\n🛣️  Xây dựng đường đi từ thứ tự Greedy...")
    greedy_path = planner._construct_path(all_points, greedy_order)
    print(f"✓ Đường đi Greedy có {len(greedy_path)} điểm")

    # Visualize Greedy
    print(f"\n📊 Vẽ đường đi Greedy...")
    visualizer.plot(
        env,
        greedy_path,
        waypoints,
        title="Greedy - Tìm Kiếm Hàng Xóm Gần Nhất",
        save_path="results/step3a_greedy_path.png",
    )
    print("✓ Đã lưu: results/step3a_greedy_path.png")

    greedy_actual_cost = PerformanceMetrics.path_length(greedy_path)
    greedy_smoothness = PerformanceMetrics.path_smoothness(greedy_path)

    print(f"\n📈 Chỉ số Greedy:")
    print(f"   Chi phí TSP: {greedy_cost:.4f}")
    print(f"   Chi phí thực tế: {greedy_actual_cost:.4f}")
    print(f"   Độ mượt mà: {greedy_smoothness:.4f}")

    # ========================================================================
    print_section("BƯỚC 4: CHẠY PSO - TỐI ƯU HÓA BẦY HẠTC")
    print("Running PSO (Particle Swarm Optimization)...")
    print("-" * 80)

    pso_order, pso_cost = tsp_solver.solve_pso(num_particles=50, max_iterations=150)

    print(f"\n✓ Thuật toán PSO hoàn thành!")
    print(f"Thứ tự thăm điểm (Order): {pso_order}")
    print(f"\nChi tiết thứ tự:")
    for idx, point_id in enumerate(pso_order):
        if point_id == 0:
            print(f"  {idx+1}. Start (điểm xuất phát)")
        elif point_id == len(all_points) - 1:
            print(f"  {idx+1}. Goal (điểm đích)")
        else:
            print(f"  {idx+1}. P{point_id} (điểm trung gian)")

    print(f"\n💰 Chi phí tổng cộng PSO: {pso_cost:.4f}")

    # Xây dựng đường đi PSO
    print(f"\n🛣️  Xây dựng đường đi từ thứ tự PSO...")
    pso_path = planner._construct_path(all_points, pso_order)
    print(f"✓ Đường đi PSO có {len(pso_path)} điểm")

    # Visualize PSO
    print(f"\n📊 Vẽ đường đi PSO...")
    visualizer.plot(
        env,
        pso_path,
        waypoints,
        title="PSO - Tối Ưu Hóa Bầy Hạt",
        save_path="results/step4a_pso_path.png",
    )
    print("✓ Đã lưu: results/step4a_pso_path.png")

    pso_actual_cost = PerformanceMetrics.path_length(pso_path)
    pso_smoothness = PerformanceMetrics.path_smoothness(pso_path)

    print(f"\n📈 Chỉ số PSO:")
    print(f"   Chi phí TSP: {pso_cost:.4f}")
    print(f"   Chi phí thực tế: {pso_actual_cost:.4f}")
    print(f"   Độ mượt mà: {pso_smoothness:.4f}")

    # ========================================================================
    print_section("BƯỚC 5: SO SÁNH GREEDY VÀ PSO")
    print("Comparison Analysis...")
    print("-" * 80)

    improvement = PerformanceMetrics.improvement_percentage(greedy_cost, pso_cost)
    actual_improvement = PerformanceMetrics.improvement_percentage(
        greedy_actual_cost, pso_actual_cost
    )

    print("\n📊 BẢNG SO SÁNH CHI TIẾT")
    print("=" * 80)
    print(f"{'Chỉ số':30} {'Greedy':20} {'PSO':20} {'Cải thiện':15}")
    print("-" * 80)

    print(f"{'Chi phí TSP':30} {greedy_cost:20.4f} {pso_cost:20.4f}", end="")
    print(f" {improvement:14.2f}%")

    print(
        f"{'Chi phí thực tế':30} {greedy_actual_cost:20.4f} {pso_actual_cost:20.4f}",
        end="",
    )
    print(f" {actual_improvement:14.2f}%")

    print(f"{'Độ mượt mà':30} {greedy_smoothness:20.4f} {pso_smoothness:20.4f}", end="")
    smoothness_improvement = PerformanceMetrics.improvement_percentage(
        greedy_smoothness, pso_smoothness
    )
    print(f" {smoothness_improvement:14.2f}%")

    print(f"{'Số điểm trên đường':30} {len(greedy_path):20} {len(pso_path):20}")
    print("=" * 80)

    # So sánh đường dẫn
    print("\n🏆 KẾT QUẢ:")
    if pso_cost < greedy_cost:
        print(f"✅ PSO TỐT HƠN Greedy")
        print(f"   → PSO tiết kiệm {improvement:.2f}% chi phí so với Greedy")
    elif greedy_cost < pso_cost:
        print(f"⚠️  Greedy TỐT HƠN PSO (có thể PSO chưa hội tụ)")
        print(f"   → Tăng PSO iterations để cải thiện")
    else:
        print(f"🤝 Cả hai có chi phí bằng nhau")

    # Vẽ so sánh
    print(f"\n📊 Vẽ so sánh 2 đường đi...")
    visualizer.compare_paths(
        env,
        {"Greedy": greedy_path, "PSO": pso_path},
        waypoints,
        title="So Sánh Greedy vs PSO",
        save_path="results/step5_comparison.png",
    )
    print("✓ Đã lưu: results/step5_comparison.png")

    # Vẽ biểu đồ chi phí
    print(f"\n📊 Vẽ biểu đồ chi phí...")
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = ["Greedy", "PSO"]
    costs = [greedy_cost, pso_cost]
    colors = ["#FF6B6B", "#4ECDC4"]

    bars = ax.bar(
        methods, costs, color=colors, alpha=0.7, edgecolor="black", linewidth=2
    )

    # Thêm giá trị trên cột
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{cost:.2f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    # Thêm đường tối ưu
    min_cost = min(costs)
    ax.axhline(y=min_cost, color="green", linestyle="--", linewidth=2, label="Tối ưu")

    ax.set_ylabel("Chi Phí (Cost)", fontsize=12, fontweight="bold")
    ax.set_title(
        "So Sánh Chi Phí: Greedy vs PSO\nCost Comparison: Greedy vs PSO",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend()

    plt.tight_layout()
    plt.savefig("results/step5_cost_comparison.png", dpi=150, bbox_inches="tight")
    print("✓ Đã lưu: results/step5_cost_comparison.png")

    # ========================================================================
    print_section("TÓM TẮT KẾT QUẢ")

    print("📁 Các file đã lưu:")
    print("   1. results/step1_environment.png       - Bản đồ ban đầu")
    print("   2. results/step2_distance_matrix.png   - Ma trận chi phí")
    print("   3. results/step3a_greedy_path.png      - Đường đi Greedy")
    print("   4. results/step4a_pso_path.png         - Đường đi PSO")
    print("   5. results/step5_comparison.png        - So sánh 2 đường")
    print("   6. results/step5_cost_comparison.png   - Biểu đồ chi phí")

    print(f"\n📊 Kết quả cuối cùng:")
    print(f"   Greedy: {greedy_cost:.4f} (Baseline)")
    print(f"   PSO:    {pso_cost:.4f}")
    if improvement > 0:
        print(f"   → PSO cải thiện {improvement:.2f}% ✅")
    else:
        print(f"   → Greedy tốt hơn {-improvement:.2f}% (PSO cần lặp lại)")

    print("\n" + "=" * 80)
    print("✓ HOÀN THÀNH - PROGRAM COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    main()
