"""
demo_multiple_runs.py - Demo tính năng chạy nhiều lần để tìm kết quả tối ưu
"""
import os
from generate_map import Map2D, generate_urban_map
from multiple_runs import MultipleRunsOptimizer, run_all_algorithms_optimized
from pso import PSO
from gwo import GWO
import matplotlib.pyplot as plt
import numpy as np

# Tạo thư mục
os.makedirs('./maps', exist_ok=True)
os.makedirs('./results', exist_ok=True)

print("="*80)
print("DEMO: CHẠY NHIỀU LẦN ĐỂ TÌM KẾT QUẢ TỐI ƯU")
print("="*80)

# Tạo bản đồ
print("\n1. Tạo bản đồ đô thị...")
map_obj = generate_urban_map()
map_obj.save('./maps/demo_urban.json')
print("✓ Đã tạo bản đồ")

# Demo 1: Chạy PSO 10 lần
print("\n" + "="*80)
print("DEMO 1: Chạy PSO 10 lần và xem sự khác biệt")
print("="*80)

optimizer = MultipleRunsOptimizer(map_obj, num_runs=10)
pso_result = optimizer.run_algorithm_multiple_times(
    algorithm_class=PSO,
    algorithm_name="PSO",
    num_particles=50,
    num_waypoints=15,
    max_iterations=200
)

if pso_result['statistics']:
    print("\n📊 Phân tích kết quả PSO:")
    stats = pso_result['statistics']
    print(f"  - Độ dài tốt nhất: {stats['path_length_min']:.2f}m")
    print(f"  - Độ dài tệ nhất: {stats['path_length_max']:.2f}m")
    print(f"  - Độ chênh lệch: {stats['path_length_max'] - stats['path_length_min']:.2f}m "
          f"({(stats['path_length_max'] - stats['path_length_min'])/stats['path_length_min']*100:.1f}%)")
    print(f"  - Độ lệch chuẩn: ±{stats['path_length_std']:.2f}m")
    print(f"\n💡 Kết luận: Chạy nhiều lần giúp tìm được đường đi tốt hơn "
          f"{(stats['path_length_max'] - stats['path_length_min'])/stats['path_length_min']*100:.1f}%!")

# Demo 2: So sánh PSO với GWO (mỗi thuật toán chạy 10 lần)
print("\n" + "="*80)
print("DEMO 2: So sánh PSO vs GWO (mỗi thuật toán chạy 10 lần)")
print("="*80)

print("\nChạy PSO 10 lần...")
pso_result = optimizer.run_algorithm_multiple_times(
    algorithm_class=PSO,
    algorithm_name="PSO",
    num_particles=50,
    num_waypoints=15,
    max_iterations=200
)

print("\nChạy GWO 10 lần...")
gwo_result = optimizer.run_algorithm_multiple_times(
    algorithm_class=GWO,
    algorithm_name="GWO",
    num_wolves=30,
    num_waypoints=15,
    max_iterations=200
)

# So sánh
print("\n" + "="*80)
print("KẾT QUẢ SO SÁNH")
print("="*80)

if pso_result['best_metrics'] and gwo_result['best_metrics']:
    print("\n📊 Kết quả tốt nhất:")
    print(f"  PSO: {pso_result['best_metrics']['path_length']:.2f}m")
    print(f"  GWO: {gwo_result['best_metrics']['path_length']:.2f}m")
    
    if pso_result['best_metrics']['path_length'] < gwo_result['best_metrics']['path_length']:
        diff = gwo_result['best_metrics']['path_length'] - pso_result['best_metrics']['path_length']
        print(f"  🏆 PSO tốt hơn {diff:.2f}m ({diff/gwo_result['best_metrics']['path_length']*100:.1f}%)")
    else:
        diff = pso_result['best_metrics']['path_length'] - gwo_result['best_metrics']['path_length']
        print(f"  🏆 GWO tốt hơn {diff:.2f}m ({diff/pso_result['best_metrics']['path_length']*100:.1f}%)")
    
    print("\n📊 Độ ổn định (Độ lệch chuẩn):")
    print(f"  PSO: ±{pso_result['statistics']['path_length_std']:.2f}m")
    print(f"  GWO: ±{gwo_result['statistics']['path_length_std']:.2f}m")
    
    if pso_result['statistics']['path_length_std'] < gwo_result['statistics']['path_length_std']:
        print(f"  🎯 PSO ổn định hơn")
    else:
        print(f"  🎯 GWO ổn định hơn")

# Demo 3: Vẽ biểu đồ phân bố
print("\n" + "="*80)
print("DEMO 3: Vẽ biểu đồ phân bố kết quả")
print("="*80)

if pso_result['all_metrics'] and gwo_result['all_metrics']:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # PSO distribution
    ax = axes[0]
    pso_lengths = [m['path_length'] for m in pso_result['all_metrics']]
    ax.hist(pso_lengths, bins=10, alpha=0.7, color='blue', edgecolor='black')
    ax.axvline(pso_result['best_metrics']['path_length'], color='red', 
               linestyle='--', linewidth=2, label=f"Best: {pso_result['best_metrics']['path_length']:.2f}m")
    ax.axvline(np.mean(pso_lengths), color='green', 
               linestyle='--', linewidth=2, label=f"Mean: {np.mean(pso_lengths):.2f}m")
    ax.set_xlabel('Độ dài đường đi (m)')
    ax.set_ylabel('Số lần')
    ax.set_title('PSO - Phân bố độ dài (10 lần chạy)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # GWO distribution
    ax = axes[1]
    gwo_lengths = [m['path_length'] for m in gwo_result['all_metrics']]
    ax.hist(gwo_lengths, bins=10, alpha=0.7, color='purple', edgecolor='black')
    ax.axvline(gwo_result['best_metrics']['path_length'], color='red', 
               linestyle='--', linewidth=2, label=f"Best: {gwo_result['best_metrics']['path_length']:.2f}m")
    ax.axvline(np.mean(gwo_lengths), color='green', 
               linestyle='--', linewidth=2, label=f"Mean: {np.mean(gwo_lengths):.2f}m")
    ax.set_xlabel('Độ dài đường đi (m)')
    ax.set_ylabel('Số lần')
    ax.set_title('GWO - Phân bố độ dài (10 lần chạy)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('./results/demo_distribution.png', dpi=150, bbox_inches='tight')
    print("✓ Đã lưu biểu đồ: ./results/demo_distribution.png")
    plt.show()

# Demo 4: Chạy tất cả thuật toán với multiple runs
print("\n" + "="*80)
print("DEMO 4: Chạy tất cả 6 thuật toán (mỗi thuật toán 10 lần)")
print("="*80)

print("\n⏰ Lưu ý: Việc này sẽ mất vài phút...")
print("Bạn có thể dùng lệnh sau để chạy:")
print("  python main.py --map ./maps/demo_urban.json --num-runs 10")
print("\nHoặc chạy code:")

choice = input("\nBạn có muốn chạy demo này không? (y/n): ")

if choice.lower() == 'y':
    results = run_all_algorithms_optimized(map_obj, num_runs=10)
    
    print("\n" + "="*80)
    print("TỔNG KẾT")
    print("="*80)
    
    # Tạo bảng so sánh
    print(f"\n{'Thuật toán':<10} {'Best (m)':<12} {'Mean (m)':<12} {'Std (m)':<10} {'Success %':<10}")
    print("-" * 70)
    
    for algo_name, result in results.items():
        if result['best_metrics']:
            stats = result['statistics']
            print(f"{algo_name:<10} "
                  f"{result['best_metrics']['path_length']:<12.2f} "
                  f"{stats['path_length_mean']:<12.2f} "
                  f"{stats['path_length_std']:<10.2f} "
                  f"{result['success_rate']*100:<10.1f}")

print("\n" + "="*80)
print("✓ HOÀN THÀNH DEMO!")
print("="*80)
print("\n💡 Hướng dẫn sử dụng:")
print("  1. Chạy nhanh (1 lần/thuật toán):")
print("     python main.py")
print("\n  2. Chạy chính xác (10 lần/thuật toán):")
print("     python main.py --num-runs 10")
print("\n  3. Chạy rất chính xác (30 lần/thuật toán):")
print("     python main.py --num-runs 30")
print("\n  4. Chỉ chạy thuật toán meta-heuristic:")
print("     python main.py --num-runs 10 --algorithms PSO GWO SA GA")
