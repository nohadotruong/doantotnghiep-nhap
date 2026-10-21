# Quick Start Guide

## 🚀 Khởi Động Nhanh - Quick Start

### 1. Cài Đặt (Installation)

```bash
# Vào thư mục project
cd d:\DEV\_Projects\TLU\DoAn\tsp-optimization-draft

# Activate virtual environment
venv\Scripts\activate

# Cài đặt dependencies (lần đầu)
pip install -r requirements.txt
```

### 2. Chạy Demo (Run Demo)

```bash
# Chạy demo đơn giản
python demo.py

# Chạy so sánh đầy đủ
python main_comparison.py
```

### 3. Công Dụng Các Files (File Purposes)

| File                                   | Công dụng                                              |
| -------------------------------------- | ------------------------------------------------------ |
| `demo.py`                              | 3 ví dụ đơn giản - Simple demonstrations               |
| `main_comparison.py`                   | So sánh toàn bộ - Full comparison study                |
| `src/environment/obstacles.py`         | Môi trường & chướng ngại vật - Environment & obstacles |
| `src/algorithms/rrt_star.py`           | Thuật toán RRT\*                                       |
| `src/algorithms/pso.py`                | Thuật toán PSO                                         |
| `src/algorithms/multipoint_planner.py` | Planner chính - Main planner                           |
| `src/utils/visualization.py`           | Visualize kết quả - Visualization                      |

---

## 💡 Ví Dụ Sử Dụng (Usage Examples)

### Ví dụ 1: Path Planning Cơ Bản

```python
import numpy as np
from src.environment import Environment
from src.algorithms import MultiPointPlanner

# Tạo môi trường
env = Environment(bounds=(0, 100, 0, 100))
env.add_circle_obstacle([30, 30], radius=8)
env.add_circle_obstacle([70, 70], radius=8)

# Định nghĩa waypoints
start = np.array([5, 5])
goal = np.array([95, 95])
waypoints = [
    np.array([30, 70]),
    np.array([60, 30]),
]

# Plan đường
planner = MultiPointPlanner(env)
path, cost, info = planner.plan(start, waypoints, goal, optimizer='combined')

print(f"Path cost: {cost:.4f}")
```

### Ví dụ 2: Visualize Kết Quả

```python
from src.utils import PathVisualizer

visualizer = PathVisualizer()
visualizer.plot(env, path, waypoints,
               title="My Result",
               save_path="results/my_path.png")
```

### Ví dụ 3: So Sánh Các Phương Pháp

```python
# Thử tất cả phương pháp
methods = ['greedy', 'pso', '2opt', 'combined']
results = {}

for method in methods:
    path, cost, _ = planner.plan(start, waypoints, goal, optimizer=method)
    results[method] = cost
    print(f"{method}: {cost:.4f}")

# Visualize comparison
visualizer.compare_paths(env,
                        {m: planner.plan(start, waypoints, goal, m)[0]
                         for m in methods},
                        waypoints)
```

---

## 📊 Kết Quả Dự Kiến (Expected Results)

Các phương pháp sẽ được so sánh:

| Phương pháp     | Tốc độ     | Chất lượng  | Ghi chú                |
| --------------- | ---------- | ----------- | ---------------------- |
| **Greedy**      | ⭐⭐⭐⭐⭐ | ⭐⭐        | Nhanh nhất, kém tối ưu |
| **PSO**         | ⭐⭐       | ⭐⭐⭐⭐    | Tốt, chậm hơn          |
| **2-Opt**       | ⭐⭐⭐     | ⭐⭐⭐      | Bình thường            |
| **PSO+2Opt** ⭐ | ⭐⭐⭐⭐⭐ | ✨ **BEST** | Phương pháp đề xuất    |

- ⭐ = Tương đối chậm nhưng cho kết quả tốt nhất

---

## 🎯 Các Thuộc Tính Chính (Key Parameters)

### RRT\* Parameters

```python
rrt = RRTStar(
    environment=env,
    max_iter=5000,      # Số lần lặp
    step_size=0.5,      # Kích thước mỗi bước
    goal_radius=0.3,    # Bán kính thành công
    search_radius=2.0   # Bán kính tìm kiếm neighbors
)
```

### PSO Parameters

```python
pso = PSO(
    num_particles=30,       # Số particles
    max_iterations=100,     # Số lần lặp
    w=0.7,                 # Inertia weight
    c1=1.5,                # Cognitive parameter
    c2=1.5                 # Social parameter
)
```

### Multi-Point Planner

```python
path, cost, info = planner.plan(
    start,
    waypoints,
    goal,
    optimizer='combined',    # 'greedy', 'pso', '2opt', 'combined'
    rrt_iterations=3000      # Số lần lặp RRT*
)
```

---

## 📈 Thống Kê & Metrics

### Tính Metrics

```python
from src.utils import PerformanceMetrics

# Độ dài đường
length = PerformanceMetrics.path_length(path)

# Độ mịn đường
smoothness = PerformanceMetrics.path_smoothness(path)

# Cải thiện %
improvement = PerformanceMetrics.improvement_percentage(greedy_cost, pso_cost)

# Tất cả metrics
all_metrics = PerformanceMetrics.compute_all_metrics(path, waypoints, cost)
```

### Lưu Kết Quả

```python
from src.utils import ResultsRecorder

recorder = ResultsRecorder()
key = recorder.record_result("test_1", result_data)
recorder.save_results(key)
```

---

## 🔧 Troubleshooting

### Vấn đề: "No path found"

**Giải pháp:**

- Tăng `rrt_iterations` (5000 hoặc 10000)
- Giảm `step_size`
- Kiểm tra waypoints không qua chướng ngại vật

### Vấn đề: Chương trình chạy chậm

**Giải pháp:**

- Giảm `max_iterations` trong PSO (50 thay vì 100)
- Giảm `rrt_iterations` (2000 thay vì 3000)
- Giảm số lượng waypoints để test

### Vấn đề: Visualization không hiển thị

```python
# Cập nhật cách hiển thị:
import matplotlib.pyplot as plt
visualizer.plot(env, path, waypoints)
plt.show()  # Hoặc lưu file
```

---

## 📁 Cấu Trúc Thư Mục (Directory Structure)

```
tsp-optimization-draft/
├── src/
│   ├── environment/       # Môi trường & obstacles
│   ├── algorithms/        # RRT*, PSO, Multi-point planner
│   └── utils/            # Utilities & visualization
├── results/              # Simpan kết quả
├── demo.py              # Demo đơn giản
├── main_comparison.py   # So sánh đầy đủ
├── requirements.txt     # Dependencies
└── README.md            # Documentation đầy đủ
```

---

## 🎓 Cho Đề Tài (For Thesis)

### Các Hình Cần Thiết (Figures to Include)

1. **So sánh đường** - `results/comparison_*.png`
2. **So sánh chi phí** - `results/cost_comparison_*.png`
3. **Tránh chướng ngại vật** - Visualizations
4. **Biểu đồ RRT tree** - RRT structure visualization

### Metric Để Báo Cáo

- Path cost (chi phí đường)
- Computation time (thời gian tính toán)
- Path smoothness (độ mịn)
- Improvement percentage (phần trăm cải thiện)

---

## 🎯 Mục Tiêu Đề Tài (Thesis Objectives)

✅ **Mục tiêu 1:** Xây dựng môi trường mô phỏng

- Đã implement: Circular & rectangular obstacles
- Collision detection

✅ **Mục tiêu 2:** Phương pháp kết hợp RRT\* + PSO

- RRT\* cho paths
- PSO cho ordering
- Combined optimizer

✅ **Mục tiêu 3:** So sánh & đánh giá

- Greedy baseline
- PSO method
- 2-Opt improvement
- Combined approach

---

## 💻 Chạy Thử Nhanh (Quick Test)

```bash
# Từ terminal
cd d:\DEV\_Projects\TLU\DoAn\tsp-optimization-draft
venv\Scripts\activate

# Chạy demo
python demo.py

# Hoặc chạy so sánh
python main_comparison.py
```

Kết quả sẽ lưu trong thư mục `results/`

---

**Good luck with your thesis! 🚀**

Nếu có vấn đề, kiểm tra:

1. Dependencies đã cài đặt chưa? → `pip install -r requirements.txt`
2. Virtual environment đã activate? → `venv\Scripts\activate`
3. Path đúng chưa? → Check `sys.path`
