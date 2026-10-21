# Simple TSP Solver

## Giới thiệu
Giải pháp đơn giản cho bài toán Traveling Salesman Problem (TSP) sử dụng:
- **A* Algorithm**: Tìm đường đi tối ưu giữa các điểm trên bản đồ có chướng ngại vật
- **Cost Matrix Builder**: Xây dựng ma trận chi phí dựa trên khoảng cách thực tế
- **Greedy Algorithm**: Giải bài toán TSP bằng phương pháp tham lam

## Cấu trúc Dự án

```
simple-tsp-draft/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── map_builder.py           # Khởi tạo bản đồ
│   ├── astar.py                 # Thuật toán A* pathfinding
│   ├── cost_matrix.py           # Xây dựng ma trận chi phí
│   ├── greedy_tsp.py            # Thuật toán Greedy TSP
│   ├── utils.py                 # Visualization & metrics
│   └── main.py                  # Main script
├── tsp_route.png                # Hình ảnh kết quả (được tạo sau khi chạy)
└── README.md                    # Tài liệu này
```

## Các Module

### 1. MapBuilder (map_builder.py)
Tạo bản đồ với chướng ngại vật và điểm đến:
- `add_obstacles()`: Thêm chướng ngại vật ngẫu nhiên
- `add_targets()`: Thêm 5 điểm đích
- `set_start_position()`: Đặt vị trí bắt đầu

### 2. AStarPathfinder (astar.py)
Tìm đường đi ngắn nhất giữa hai điểm:
- Hỗ trợ 8 hướng di chuyển (ngang, dọc, chéo)
- Sử dụng Euclidean distance làm heuristic
- Tính chi phí: di chuyển ngang/dọc = 1, chéo = √2

### 3. CostMatrixBuilder (cost_matrix.py)
Xây dựng ma trận chi phí n×n:
- Tính chi phí từ mỗi điểm đến mỗi điểm khác
- Lưu lại các đường đi chi tiết
- Hiển thị ma trận dưới dạng bảng

### 4. GreedyTSP (greedy_tsp.py)
Giải bài toán TSP bằng chiến lược tham lam:
- Tại mỗi bước, chọn điểm chưa thăm gần nhất
- Trả về lộ trình và chi phí tổng
- Cung cấp mô tả chi tiết của lộ trình

### 5. MapVisualizer & MetricsCalculator (utils.py)
Hiển thị và đánh giá kết quả:
- `MapVisualizer`: Vẽ bản đồ, chướng ngại vật, và lộ trình
- `MetricsCalculator`: Tính các chỉ số đánh giá

## Các Chỉ Số Đánh Giá

| Chỉ Số | Ý Nghĩa |
|--------|---------|
| **Tổng chi phí** | Tổng khoảng cách của lộ trình |
| **Chi phí trung bình** | Trung bình chi phí trên mỗi segment |
| **Số điểm ghé thăm** | Bao nhiêu điểm trong lộ trình |
| **Số segment** | Số đoạn đường trong lộ trình |
| **Giới hạn dưới** | Chi phí tối thiểu lý thuyết |
| **Độ lệch %** | Sai lệch so với giới hạn dưới |

## Cách Chạy

### Yêu cầu
- Python 3.7+
- numpy
- matplotlib

### Cài đặt

```bash
# Clone hoặc tải project
cd simple-tsp-draft

# Tạo virtual environment (tùy chọn)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/Mac

# Cài đặt dependencies
pip install numpy matplotlib
```

### Chạy chương trình

```bash
python src/main.py
```

## Output

Chương trình sẽ in ra:

1. **Bản đồ ASCII**: Hiển thị bản đồ, chướng ngại vật, điểm bắt đầu (S), điểm đích (*)

2. **Ma trận chi phí**: Bảng chi phí giữa tất cả các điểm

3. **Lộ trình tối ưu**: Thứ tự ghé thăm các điểm

4. **Các chỉ số đánh giá**:
   - Tổng chi phí
   - Chi phí trung bình
   - Giới hạn dưới lý thuyết
   - Độ lệch từ giới hạn dưới

5. **Hình ảnh visualization**: Lưu tại `tsp_route.png`

## Ví dụ Output

```
============================================================
GIẢI BÀI TOÁN TRAVELING SALESMAN PROBLEM (TSP)
============================================================

[BƯỚC 1] Khởi tạo bản đồ...
  - Kích thước bản đồ: 30x30
  - Điểm bắt đầu: (3, 11)
  - Số điểm đích: 5
  - Số chướng ngại vật: 80

[BƯỚC 2] Áp dụng thuật toán A* để tìm đường đi...

[BƯỚC 3] Áp dụng thuật toán Greedy...
  - Lộ trình tìm được: [0, 1, 2, 3, 5, 4, 0]
  - Tổng chi phí: 51.11

[BƯỚC 4] Hiển thị kết quả và chỉ số đánh giá...
  - Tạo hình ảnh visualization...

Lộ trình tối ưu:
Điểm bắt đầu: (3, 11)
→ (2, 12) (chi phí: 1.41)
→ (5, 22) (chi phí: 11.24)
→ (6, 24) (chi phí: 2.41)
→ (13, 10) (chi phí: 16.90)
→ (10, 3) (chi phí: 8.24)
→ (3, 11) (Quay về, chi phí: 10.90)

=== CÁC CHỈ SỐ ĐÁNH GIÁ ===
Tổng chi phí:                  51.11
Chi phí trung bình trên segment: 8.52
Số điểm cần ghé thăm:          6
Số điểm đã ghé thăm:           6
Số segment:                    6
Giới hạn dưới lý thuyết:       12.07
Độ lệch từ giới hạn dưới:      323.43%
```

## Pipeline Xử lý

```
┌─────────────────────────────────────────────┐
│ 1. Khởi tạo bản đồ (MapBuilder)             │
│    - Tạo lưới 30x30                        │
│    - Thêm 20 chướng ngại vật                │
│    - Thêm 5 điểm đích                      │
│    - Đặt vị trí bắt đầu                    │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 2. Xây dựng ma trận chi phí (A* + Builder) │
│    - Dùng A* tìm đường giữa các điểm       │
│    - Tính chi phí thực tế                  │
│    - Xây dựng ma trận n×n                  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 3. Giải TSP (GreedyTSP)                    │
│    - Chọn điểm gần nhất chưa thăm          │
│    - Lặp cho đến khi ghé hết               │
│    - Quay về điểm bắt đầu                  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 4. Hiển thị kết quả (Visualizer)           │
│    - In bảng chi phí                       │
│    - Vẽ hình ảnh lộ trình                  │
│    - Tính các chỉ số đánh giá              │
└─────────────────────────────────────────────┘
```

## Tùy chỉnh

Để thay đổi thông số, chỉnh sửa trong `main.py`:

```python
# Thay đổi kích thước bản đồ
map_builder = MapBuilder(width=50, height=50)  # Thay vì 30x30

# Thay đổi số lượng chướng ngại vật
map_builder.add_obstacles(num_obstacles=30, obstacle_size=2)  # Thay vì 20

# Thay đổi số điểm đích
map_builder.add_targets(num_targets=10)  # Thay vì 5
```

## Ghi chú

- **A* Heuristic**: Sử dụng Euclidean distance, có thể đổi sang Manhattan distance nếu cần
- **Greedy Algorithm**: Phương pháp tham lam, tìm được giải pháp nhanh nhưng không đảm bảo tối ưu toàn cục
- **Movement**: Hỗ trợ 8 hướng di chuyển (bao gồm đường chéo)

## Cải tiến Có Thể

1. Implement các thuật toán TSP khác (2-opt, Simulated Annealing, Genetic Algorithm)
2. Hỗ trợ các heuristic khác cho A*
3. Thêm giao diện tương tác
4. Lưu/tải bản đồ từ file
5. So sánh hiệu suất giữa các thuật toán

## Tác giả

Simple TSP Solver - Dự án để giải quyết bài toán TSP đơn giản
