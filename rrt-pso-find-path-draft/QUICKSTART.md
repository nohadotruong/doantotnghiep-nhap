# RRT-PSO UAV Path Planning System - Hướng dẫn hoàn tất

## 📋 Tóm tắt hệ thống

Một hệ thống **tối ưu đường đi cho UAV** trong môi trường 2D có vật cản sử dụng:
- **Goal-biased RRT** để tìm đường khả thi
- **PSO (Particle Swarm Optimization)** để tối ưu hóa đường

## 📁 Cấu trúc dự án hoàn chỉnh

```
rrt-pso-find-path-draft/
│
├── .venv/                          # Virtual environment
│
├── environment/
│   ├── __init__.py
│   └── environment.py              # Class UAVEnvironment
│
├── node/
│   ├── __init__.py
│   └── node.py                     # Class Node
│
├── algorithms/
│   ├── __init__.py
│   ├── rrt.py                      # Class RRTPlanner
│   └── pso.py                      # Class PSOOptimizer
│
├── utils/
│   ├── __init__.py
│   └── collision.py                # Hàm kiểm tra va chạm
│
├── main.py                         # Chương trình chính
├── examples.py                     # Các ví dụ nâng cao
├── tests.py                        # Unit tests
├── README.md                       # Hướng dẫn chi tiết
└── QUICKSTART.md                   # File này
```

## 🚀 Bắt đầu nhanh

### 1. Cài đặt

```bash
cd rrt-pso-find-path-draft

# (Tuỳ chọn) Tạo virtual environment
python -m venv venv
venv\Scripts\activate

# Cài đặt dependencies
pip install numpy matplotlib
```

### 2. Chạy chương trình chính

```bash
python main.py
```

**Kết quả:**
- Tìm đường từ (10, 10) đến (90, 90)
- RRT: 139.40 (29 waypoints)
- PSO: 131.07 (cải thiện 5.97%)
- Hiển thị biểu đồ so sánh

### 3. Chạy các ví dụ khác

```bash
python examples.py
```

Sửa file `examples.py`, bỏ comment các ví dụ bạn muốn chạy:
- Ví dụ 1: Dense obstacles (nhiều vật cản)
- Ví dụ 2: Narrow corridor (hẻo hẹp)
- Ví dụ 3: Large obstacles (vài vật cản lớn)
- Ví dụ 4: So sánh tham số

### 4. Chạy Unit Tests

```bash
python tests.py
```

Xác minh tất cả các thành phần hoạt động đúng:
- ✓ Node class
- ✓ Collision detection
- ✓ Environment
- ✓ RRT Planner
- ✓ PSO Optimizer
- ✓ Full integration

## 📖 Hướng dẫn sử dụng

### Sử dụng cơ bản

```python
from environment.environment import UAVEnvironment
from algorithms.rrt import RRTPlanner
from algorithms.pso import PSOOptimizer
from utils.collision import path_length

# 1. Tạo environment
env = UAVEnvironment(100, 100, [
    (20, 20, 10, 40),
    (50, 10, 10, 50),
    (70, 60, 20, 10)
])

# 2. Chạy RRT
planner = RRTPlanner(
    env,
    start=(10, 10),
    goal=(90, 90),
    step_size=5.0,
    max_iter=5000,
    goal_sample_rate=0.2
)
rrt_path = planner.plan()

# 3. Tối ưu bằng PSO
optimizer = PSOOptimizer(
    env,
    rrt_path,
    num_particles=30,
    iterations=100
)
pso_path = optimizer.optimize()

# 4. Visualize
rrt_length = path_length(rrt_path)
pso_length = path_length(pso_path)

print(f"RRT: {rrt_length:.2f}")
print(f"PSO: {pso_length:.2f}")
print(f"Cải thiện: {(rrt_length-pso_length)/rrt_length*100:.2f}%")

env.visualize_multiple_paths({
    'RRT': rrt_path,
    'RRT-PSO': pso_path
})
```

### Tùy chỉnh tham số

#### RRT Parameters

```python
RRTPlanner(
    environment,
    start,
    goal,
    step_size=5.0,          # Khoảng cách mỗi bước (nhỏ hơn = chi tiết hơn)
    max_iter=5000,          # Số lần lặp tối đa
    goal_sample_rate=0.2    # Xác suất chọn goal (0-1)
)
```

**Điều chỉnh cho tình huống khác nhau:**

| Tình huống | step_size | max_iter | goal_rate |
|-----------|-----------|----------|-----------|
| Hẻo hẹp   | 2.0-3.0   | 10000    | 0.15-0.2  |
| Mở rộng   | 5.0-10.0  | 3000     | 0.3-0.5   |
| Chi tiết  | 1.0-2.0   | 15000    | 0.1-0.15  |

#### PSO Parameters

```python
PSOOptimizer(
    environment,
    original_path,
    num_particles=30,       # Số particles (nhiều hơn = tối ưu tốt hơn)
    iterations=100,         # Số iteration (nhiều hơn = tối ưu tốt hơn)
    w=0.7,                 # Inertia weight (0.4-0.9)
    c1=1.5,                # Cognitive parameter (1.0-2.0)
    c2=1.5                 # Social parameter (1.0-2.0)
)
```

**Điều chỉnh cho kết quả tốt hơn:**

| Mục tiêu | num_particles | iterations | w | c1 | c2 |
|---------|----------|------------|-----|-----|-----|
| Nhanh   | 10-20    | 50         | 0.8 | 1.5 | 1.5 |
| Cân bằng| 30-50    | 100-150    | 0.7 | 1.5 | 1.5 |
| Chất lượng| 50-100 | 200-300    | 0.6 | 2.0 | 2.0 |

## 🔧 Các thành phần chính

### 1. Node Class (node.py)

```python
from node.node import Node

node1 = Node(10, 20)
node2 = Node(30, 40)

distance = node1.distance_to(node2)
```

**Phương thức:**
- `distance_to(other)`: Tính khoảng cách Euclid

### 2. Environment Class (environment.py)

```python
from environment.environment import UAVEnvironment

env = UAVEnvironment(width=100, height=100, obstacles=[...])

# Kiểm tra điểm
if env.is_inside_obstacle(50, 50):
    print("Điểm nằm trong vật cản")

# Kiểm tra đoạn thẳng
if env.is_collision((10,10), (90,90)):
    print("Va chạm!")

# Vẽ
env.visualize(path=my_path, title="My Path")
env.visualize_multiple_paths({'RRT': rrt, 'PSO': pso})
```

**Phương thức:**
- `is_inside_obstacle(x, y)`: Kiểm tra điểm
- `is_collision(p1, p2)`: Kiểm tra đoạn thẳng
- `visualize(path, title, show_goal)`: Vẽ path
- `visualize_multiple_paths(paths_dict, title)`: Vẽ nhiều paths

### 3. RRT Planner (algorithms/rrt.py)

```python
from algorithms.rrt import RRTPlanner

planner = RRTPlanner(env, start, goal)
path = planner.plan()  # Trả về [(x1,y1), (x2,y2), ...] hoặc None
```

**Phương thức:**
- `sample()`: Lấy điểm ngẫu nhiên
- `nearest(point)`: Tìm node gần nhất
- `steer(from_node, to_point)`: Di chuyển một bước
- `plan()`: Chạy thuật toán

### 4. PSO Optimizer (algorithms/pso.py)

```python
from algorithms.pso import PSOOptimizer

optimizer = PSOOptimizer(env, rrt_path)
optimized = optimizer.optimize()
```

**Fitness Function:**
```
fitness = path_length 
        + 1000 * collision_penalty 
        + 0.1 * smoothness_penalty
```

### 5. Collision Tools (utils/collision.py)

```python
from utils.collision import (
    point_in_rectangle,
    line_rectangle_collision,
    path_length,
    smoothness_penalty
)
```

## 📊 Kết quả mong đợi

### Ví dụ 1: Standard Case (100x100, 3 obstacles)

```
[SETUP] Tạo môi trường...
  - Kích thước map: 100 x 100
  - Số vật cản: 3
  - Start: (10, 10)
  - Goal: (90, 90)

[RRT] Chạy thuật toán RRT...
[RRT] Tìm đường thành công sau 72 iterations
  - Số điểm waypoint: 29
  - Độ dài đường: 139.40

[PSO] Chạy thuật toán PSO tối ưu hóa...
[PSO] Bắt đầu tối ưu hóa...
[PSO] Fitness ban đầu: 1196.95
[PSO] Iteration 20/100: Best Fitness = 151.34
[PSO] Iteration 40/100: Best Fitness = 140.33
[PSO] Iteration 60/100: Best Fitness = 136.63
[PSO] Iteration 80/100: Best Fitness = 132.93
[PSO] Iteration 100/100: Best Fitness = 131.59
[PSO] Hoàn thành. Fitness cuối cùng: 131.59
  - Số điểm waypoint: 29
  - Độ dài đường: 131.07

============================================================
KẾT QUẢ SO SÁNH
============================================================

RRT:
  - Độ dài: 139.40
  - Waypoints: 29

PSO (Optimized):
  - Độ dài: 131.07
  - Waypoints: 29

Cải thiện:
  - Độ dài giảm: 8.32 (5.97%)
```

## 🐛 Troubleshooting

### Problem: Python không tìm được modules

**Giải pháp:**
- Chắc chắn bạn đang chạy từ thư mục gốc `rrt-pso-find-path-draft/`
- Kiểm tra các file `__init__.py` tồn tại trong các thư mục

### Problem: Matplotlib không hiển thị window

**Giải pháp:**
- Thêm `plt.show()` sau khi vẽ
- Hoặc export thành file PNG (xem mã chi tiết)

### Problem: RRT không tìm được đường

**Giải pháp:**
- Tăng `max_iter`
- Giảm `step_size` để tìm kiếm chi tiết hơn
- Kiểm tra start/goal không nằm trong vật cản

### Problem: PSO không tối ưu hóa được

**Giải pháp:**
- Tăng `num_particles` và `iterations`
- Điều chỉnh `w`, `c1`, `c2`
- Kiếm tra fitness function

## 📚 Tài liệu tham khảo

### RRT (Rapidly-exploring Random Trees)
- Paper: "Rapidly-exploring random trees: A new tool for path planning" (LaValle, 1998)
- Thuật toán tìm đường xác suất, hiệu quả cho không gian cao chiều

### PSO (Particle Swarm Optimization)
- Paper: "Particle Swarm Optimization" (Kennedy & Eberhart, 1995)
- Tối ưu hóa dựa trên hành vi giàn cá

### Path Planning
- RRT* - Optimal RRT
- Informed RRT* - Tối ưu hơn
- BiRRT - Hai chiều

## 💡 Ghi chú quan trọng

1. **Hẻo hẹp:** Nếu UAV cần đi qua hẻo hẹp, giảm `step_size` của RRT
2. **Tối ưu hóa:** PSO có thể mất thời gian, start với `iterations=50-100`
3. **Collision:** Kiểm tra va chạm sử dụng line-rectangle collision
4. **Smoothness:** Phạt độ uốn giúp đường đi mượt hơn, an toàn hơn cho UAV
5. **Real-time:** Nếu cần thời gian thực, giảm `max_iter` của RRT

## 🎯 Các bước tiếp theo

### Nâng cao hệ thống:

1. **3D Path Planning:**
   - Mở rộng từ 2D sang 3D
   - Thêm height/altitude

2. **Dynamics:**
   - Thêm vận tốc, gia tốc
   - Kiểm tra constraint UAV

3. **Real-time:**
   - RRT* (optimal)
   - Informed RRT*
   - Anytime algorithms

4. **Multi-UAV:**
   - Tìm đường cho nhiều UAV
   - Tránh collision giữa UAV

5. **Learning:**
   - Học từ kinh nghiệm (reinforcement learning)
   - Neural network cho planning

## 📞 Hỗ trợ

Xem file `README.md` để biết thêm chi tiết.

---

**Hệ thống sẵn sàng sử dụng! Chúc bạn thành công!** 🚀

**Phiên bản:** 1.0  
**Cập nhật:** 2026-02-28
