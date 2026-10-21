# Quick Start Guide - Hướng Dẫn Bắt Đầu Nhanh

## Khởi Động Nhanh

```bash
# 1. Vào thư mục dự án
cd simple-tsp-draft

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Chạy giải pháp TSP
python src/main.py

# 4. (Tùy chọn) Xem các ví dụ
python examples.py
```

## Kết Quả

Sau khi chạy `python src/main.py`, bạn sẽ nhìn thấy:

1. **Bản đồ ASCII** - Hiển thị bản đồ 30x30 với:
   - `S` = Điểm bắt đầu
   - `*` = Điểm đích (5 điểm)
   - `█` = Chướng ngại vật
   - `.` = Ô trống

2. **Ma trận chi phí** - Bảng chi phí giữa tất cả các cặp điểm

3. **Lộ trình tối ưu** - Thứ tự ghé thăm các điểm và chi phí từng segment

4. **Chỉ số đánh giá**:
   - Tổng chi phí lộ trình
   - Chi phí trung bình
   - Độ lệch từ giới hạn dưới lý thuyết

5. **Hình ảnh** - `tsp_route.png` visualize lộ trình trên bản đồ

## Cấu Trúc Thư Mục

```
simple-tsp-draft/
├── src/
│   ├── __init__.py           # Package
│   ├── map_builder.py        # Khởi tạo bản đồ
│   ├── astar.py              # A* pathfinding
│   ├── cost_matrix.py        # Xây dựng ma trận chi phí
│   ├── greedy_tsp.py         # Giải TSP (Greedy)
│   ├── utils.py              # Visualization & metrics
│   └── main.py               # Main script
├── examples.py               # Các ví dụ sử dụng
├── requirements.txt          # Dependencies
├── README.md                 # Tài liệu đầy đủ
├── QUICK_START.md           # File này
└── tsp_route.png            # Output hình ảnh (sau khi chạy)
```

## Pipeline

```
MapBuilder (khởi tạo bản đồ)
    ↓
AStarPathfinder (tìm đường giữa các điểm)
    ↓
CostMatrixBuilder (xây dựng ma trận chi phí)
    ↓
GreedyTSP (giải bài toán TSP)
    ↓
Visualizer & MetricsCalculator (hiển thị kết quả)
```

## Các Module Chính

### [MapBuilder](src/map_builder.py)
Tạo bản đồ với chướng ngại vật:
```python
from map_builder import MapBuilder
map = MapBuilder(width=30, height=30)
map.add_obstacles(num_obstacles=20)
map.add_targets(num_targets=5)
map.set_start_position()
```

### [AStarPathfinder](src/astar.py)
Tìm đường đi tối ưu:
```python
from astar import AStarPathfinder
pathfinder = AStarPathfinder(grid, width, height)
path, cost = pathfinder.find_path(start, goal)
```

### [CostMatrixBuilder](src/cost_matrix.py)
Xây dựng ma trận chi phí:
```python
from cost_matrix import CostMatrixBuilder
builder = CostMatrixBuilder(pathfinder)
cost_matrix = builder.build_cost_matrix(points)
```

### [GreedyTSP](src/greedy_tsp.py)
Giải TSP bằng Greedy:
```python
from greedy_tsp import GreedyTSP
solver = GreedyTSP(cost_matrix)
route, total_cost = solver.solve(start=0)
```

### [Visualization & Metrics](src/utils.py)
Hiển thị kết quả:
```python
from utils import MapVisualizer, MetricsCalculator
MapVisualizer.visualize_map(map_info, route, paths)
metrics = MetricsCalculator.calculate_metrics(cost_matrix, route, cost)
```

## Ví Dụ Sử Dụng

### Ví dụ 1: Tìm đường đi cơ bản
```python
from src.map_builder import MapBuilder
from src.astar import AStarPathfinder

map = MapBuilder(20, 20)
map.add_obstacles(10)
map.set_start_position(2, 2)

pathfinder = AStarPathfinder(map.grid, 20, 20)
path, cost = pathfinder.find_path((2, 2), (18, 18))
print(f"Costs: {cost:.2f}, Steps: {len(path)}")
```

### Ví dụ 2: Giải TSP đầy đủ
```python
from src.main import run_tsp_pipeline
run_tsp_pipeline()
```

### Ví dụ 3: Xem các ví dụ khác
```bash
python examples.py
```

## Thông Số Mặc Định

| Thông số | Giá trị |
|----------|--------|
| Kích thước bản đồ | 30x30 |
| Số chướng ngại vật | 20 |
| Kích thước chướng ngại vật | 2x2 |
| Số điểm đích | 5 |
| Thuật toán pathfinding | A* |
| Thuật toán TSP | Greedy |

## Tùy chỉnh Thông Số

Chỉnh sửa `src/main.py`:

```python
# Thay đổi kích thước bản đồ (mặc định: 30x30)
map_builder = MapBuilder(width=50, height=50)

# Thay đổi số chướng ngại vật (mặc định: 20)
map_builder.add_obstacles(num_obstacles=30, obstacle_size=2)

# Thay đổi số điểm đích (mặc định: 5)
map_builder.add_targets(num_targets=10)
```

## Ghi Chú

- **A* Heuristic**: Euclidean distance
- **Movement**: 8 hướng (ngang, dọc, chéo)
- **Greedy Strategy**: Chọn điểm gần nhất chưa thăm
- **Output**: Text output + file hình ảnh PNG

## Troubleshooting

### Lỗi: Module not found
```bash
# Chạy lại setup
pip install -r requirements.txt
```

### Lỗi: Matplotlib
```bash
# Cài đặt matplotlib
pip install --upgrade matplotlib
```

### Hình ảnh không lưu
Kiểm tra quyền ghi file trong thư mục dự án

## Các Chỉ Số Đánh Giá

- **Tổng chi phí**: Tổng khoảng cách của lộ trình
- **Chi phí trung bình**: Chi phí / số segment
- **Giới hạn dưới lý thuyết**: Giới hạn chi phí tối thiểu
- **Độ lệch**: Sai lệch so với giới hạn (%)

## Cải Tiến

Có thể thêm:
- Các thuật toán TSP khác (2-opt, Simulated Annealing)
- Giao diện GUI
- Export/import bản đồ
- So sánh hiệu suất

## Cần Giúp?

Xem [README.md](README.md) để tài liệu đầy đủ.

---
**Chúc bạn sử dụng vui vẻ!** 🚀
