# RRT-PSO Path Planning System for UAV

Hệ thống tối ưu đường đi cho UAV trong môi trường 2D có vật cản sử dụng Goal-biased RRT và PSO.

## Cấu trúc dự án

```
project/
│
├── environment/
│   ├── __init__.py
│   └── environment.py          # Lớp UAVEnvironment
│
├── node/
│   ├── __init__.py
│   └── node.py                 # Lớp Node
│
├── algorithms/
│   ├── __init__.py
│   ├── rrt.py                  # Goal-biased RRT Planner
│   └── pso.py                  # PSO Optimizer
│
├── utils/
│   ├── __init__.py
│   └── collision.py            # Hàm kiểm tra va chạm
│
├── main.py                     # Chương trình chính
└── README.md                   # File này
```

## Yêu cầu

- Python 3.7+
- numpy
- matplotlib

## Cài đặt

1. Tạo virtual environment (tuỳ chọn):
```bash
python -m venv venv
venv\Scripts\activate
```

2. Cài đặt dependencies:
```bash
pip install numpy matplotlib
```

## Chạy chương trình

Chạy từ thư mục gốc:
```bash
python main.py
```

## Kết quả

Chương trình sẽ:
1. Tạo environment với 3 vật cản
2. Chạy RRT để tìm đường từ (10,10) đến (90,90)
3. Tối ưu hóa đường bằng PSO
4. Hiển thị kết quả trực quan hóa

**Ví dụ kết quả:**
- RRT path length: ~139.40
- PSO optimized path length: ~131.07
- Improvement: ~5.97%

## Các thành phần chính

### 1. Environment (environment.py)

Lớp `UAVEnvironment` đại diện môi trường:

```python
env = UAVEnvironment(width=100, height=100, obstacles=[...])

# Kiểm tra điểm nằm trong vật cản
env.is_inside_obstacle(x, y)

# Kiểm tra đoạn thẳng va chạm
env.is_collision(p1, p2)

# Vẽ bản đồ
env.visualize(path=rrt_path)
env.visualize_multiple_paths({
    'RRT': rrt_path,
    'RRT-PSO': pso_path
})
```

### 2. Node (node.py)

Lớp `Node` đại diện một điểm trong không gian:

```python
node = Node(x, y, parent=None)
distance = node.distance_to(other_node)
```

### 3. RRT Planner (algorithms/rrt.py)

Thuật toán Goal-biased RRT:

```python
planner = RRTPlanner(
    environment=env,
    start=(10, 10),
    goal=(90, 90),
    step_size=5.0,
    max_iter=5000,
    goal_sample_rate=0.2
)

path = planner.plan()
# Returns: [(x1,y1), (x2,y2), ...] hoặc None
```

**Tham số:**
- `step_size`: Khoảng cách di chuyển mỗi bước (default: 5.0)
- `max_iter`: Số lần lặp tối đa (default: 5000)
- `goal_sample_rate`: Xác suất chọn goal (default: 0.2)

### 4. PSO Optimizer (algorithms/pso.py)

Thuật toán PSO tối ưu hóa:

```python
optimizer = PSOOptimizer(
    environment=env,
    original_path=rrt_path,
    num_particles=30,
    iterations=100,
    w=0.7,
    c1=1.5,
    c2=1.5
)

optimized_path = optimizer.optimize()
```

**Tham số:**
- `num_particles`: Số lượng particles (default: 30)
- `iterations`: Số lần lặp (default: 100)
- `w`: Inertia weight (default: 0.7)
- `c1`: Cognitive parameter (default: 1.5)
- `c2`: Social parameter (default: 1.5)

**Fitness function:**
```
fitness = path_length + 1000 * collision_penalty + 0.1 * smoothness_penalty
```

### 5. Collision Detection (utils/collision.py)

Các hàm kiểm tra va chạm:
- `point_in_rectangle()`: Kiểm tra điểm trong hình chữ nhật
- `line_rectangle_collision()`: Kiểm tra đoạn thẳng cắt hình chữ nhật
- `path_length()`: Tính độ dài đường đi
- `smoothness_penalty()`: Tính phạt độ uốn

## Ví dụ tùy chỉnh

Tạo file `custom_example.py`:

```python
from environment.environment import UAVEnvironment
from algorithms.rrt import RRTPlanner
from algorithms.pso import PSOOptimizer

# Tạo environment tùy chỉnh
env = UAVEnvironment(200, 200, [
    (50, 50, 30, 40),
    (100, 100, 20, 30),
    (150, 50, 25, 25)
])

# Chạy RRT
planner = RRTPlanner(env, (20, 20), (180, 180))
path_rrt = planner.plan()

# Tối ưu hóa
if path_rrt:
    optimizer = PSOOptimizer(env, path_rrt, num_particles=50, iterations=200)
    path_optimized = optimizer.optimize()
    
    env.visualize_multiple_paths({
        'Original RRT': path_rrt,
        'Optimized PSO': path_optimized
    })
```

## Giải thích thuật toán

### Goal-biased RRT

1. Khởi tạo cây với start node
2. Lặp max_iter lần:
   - Sample: Chọn goal với xác suất goal_sample_rate, ngược lại chọn random
   - Tìm node gần nhất trong tree
   - Steer: Di chuyển step_size về phía sample
   - Kiểm tra va chạm, nếu OK thêm vào tree
   - Nếu gần goal, kết thúc

### PSO Optimization

1. Khởi tạo quần thể particles (mỗi particle là một đường đi)
2. Lặp iterations lần:
   - Cập nhật velocity = w * velocity + c1 * personal_best + c2 * global_best
   - Cập nhật position = position + velocity
   - Tính fitness
   - Cập nhật best position cá nhân và global best

## Điều chỉnh thông số

**Để tìm đường nhanh hơn:**
- Tăng `goal_sample_rate` của RRT (0.3-0.5)
- Giảm `step_size` để chi tiết hơn

**Để tối ưu hóa tốt hơn:**
- Tăng `num_particles` (50, 100)
- Tăng `iterations` (200, 300)

**Để tránh va chạm:**
- Giảm `step_size` của RRT
- Tăng `collision_penalty` trong PSO fitness function

## Ghi chú

- Hàm va chạm sử dụng line-rectangle collision detection
- PSO chỉ tối ưu các waypoint trung gian, giữ nguyên start và goal
- Độ uốn được tính dựa trên góc giữa các đoạn thẳng liên tiếp

## Tài liệu tham khảo

- RRT: Rapidly-exploring Random Trees
- PSO: Particle Swarm Optimization
- Path Planning for Autonomous Vehicles

## Liên hệ / Hỗ trợ

Cho câu hỏi hoặc đề xuất, vui lòng tạo issue hoặc liên hệ.

---

**Phiên bản:** 1.0  
**Cập nhật cuối:** 2026-02-28
