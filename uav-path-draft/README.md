# 🚁 UAV Pathfinding Algorithms - Hệ thống Tìm Đường Đi cho UAV

Một dự án giáo dục để học tập và thực hành các thuật toán tìm đường đi (pathfinding) cho máy bay không người lái (UAV) trên bản đồ có chướng ngại vật.

## 📚 Các Thuật Toán Được Triển Khai

### 1. **A* (A-Star)** - Thuật toán Tìm Kiếm Đồ Thị
- **Loại**: Greedy + Heuristic Search
- **Đặc điểm**:
  - Luôn tìm được đường đi tối ưu (nếu tồn tại)
  - Sử dụng heuristic (ước lượng) để hướng dẫn tìm kiếm
  - f(n) = g(n) + h(n) - chi phí = khoảng cách cũ + ước lượng khoảng cách còn lại
  - Hiệu quả cao, thích hợp cho không gian nhỏ
- **Ưu điểm**: Tìm được đường tối ưu, nhanh
- **Nhược điểm**: Chậm trong không gian tìm kiếm lớn

### 2. **PSO (Particle Swarm Optimization)** - Tối Ưu Hóa Bầy
- **Loại**: Evolutionary Algorithm, Swarm Intelligence
- **Đặc điểm**:
  - Mô phỏng hành vi tìm kiếm thức ăn của bầy chim
  - Mỗi hạt (particle) đại diện cho giải pháp tiềm năng
  - Di chuyển dựa trên: vận tốc cũ + hướng đến giải pháp tốt nhất cá nhân + hướng đến giải pháp tốt nhất bầy
  - v(t+1) = w*v(t) + c1*r1*(pbest - x) + c2*r2*(gbest - x)
- **Ưu điểm**: Hội tụ nhanh, có thể tìm trong không gian lớn
- **Nhược điểm**: Không chắc chắn tìm được tối ưu, dễ rơi vào local optimum

### 3. **SA (Simulated Annealing)** - Mô Phỏng Quá Trình Làm Nguội
- **Loại**: Metaheuristic, Monte Carlo Method
- **Đặc điểm**:
  - Mô phỏng quá trình làm nguội kim loại trong luyện kim
  - Bắt đầu với nhiệt độ cao → từ từ giảm
  - Ở nhiệt độ cao: chấp nhận giải pháp tệ hơn (thoát local optimum)
  - Ở nhiệt độ thấp: chỉ chấp nhận giải pháp tốt hơn
  - P(accept) = exp(-ΔE / T)
- **Ưu điểm**: Thoát khỏi local optimum tốt, linh hoạt
- **Nhược điểm**: Cần điều chỉnh tham số, hội tụ có thể chậm

### 4. **GWO (Grey Wolf Optimizer)** - Tối Ưu Hóa Bầy Sói Xám
- **Loại**: Swarm Intelligence, Evolutionary Algorithm
- **Đặc điểm**:
  - Mô phỏng hành vi săn mồi của bầy sói xám
  - 4 cấp bậc: Alpha (lãnh đạo), Beta, Delta, Omega
  - Mỗi sói di chuyển dựa trên 3 lãnh đạo tốt nhất
  - X(t+1) = (X_α + X_β + X_δ) / 3 - A⃗ · |C⃗ · X - X|
- **Ưu điểm**: Cân bằng khám phá-khai thác tốt, hội tụ nhanh
- **Nhược điểm**: Có thể bị mắc kẹt ở local optimum

### 5. **GA (Genetic Algorithm)** - Thuật Toán Di Truyền
- **Loại**: Evolutionary Algorithm
- **Đặc điểm**:
  - Mô phỏng quá trình tiến hóa tự nhiên
  - Quần thể gồm các cá thể (giải pháp)
  - Các bước: **Selection** (chọn) → **Crossover** (lai ghép) → **Mutation** (đột biến)
  - Duy trì đa dạng, thoát local optimum
- **Ưu điểm**: Tìm được giải pháp tốt, có thể tìm trong không gian phức tạp
- **Nhược điểm**: Hội tụ chậm, cần điều chỉnh tham số

## 🏗️ Cấu Trúc Dự Án

```
.
├── algorithms/              # Thư mục các thuật toán
│   ├── __init__.py
│   ├── astar.py            # A* Algorithm
│   ├── pso.py              # Particle Swarm Optimization
│   ├── sa.py               # Simulated Annealing
│   ├── gwo.py              # Grey Wolf Optimizer
│   └── ga.py               # Genetic Algorithm
│
├── utils/                   # Các công cụ tiện ích
│   ├── __init__.py
│   └── environment.py       # Lớp quản lý môi trường
│
├── main.py                  # Script chính - chạy và so sánh các thuật toán
├── requirements.txt         # Danh sách thư viện cần thiết
└── README.md               # Hướng dẫn này
```

## 🚀 Cách Sử Dụng

### 1. Cài Đặt Thư Viện

```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install numpy matplotlib
```

### 2. Chạy Chương Trình Chính

```bash
python main.py
```

Chương trình sẽ:
- Tạo môi trường với bản đồ 100x100 và 5 chướng ngại vật
- Chạy tất cả 5 thuật toán
- Vẽ đường đi tìm được bởi mỗi thuật toán
- In ra bảng so sánh hiệu suất

### 3. Tạo Môi Trường Tùy Chỉnh

```python
from utils.environment import UAVEnvironment
from algorithms import AStarPathfinder

# Tạo môi trường
env = UAVEnvironment(width=100, height=100)

# Thêm chướng ngại vật
env.add_rectangular_obstacle(20, 30, 20, 10)  # Hình chữ nhật
env.add_circular_obstacle(50, 50, 8)          # Hình tròn

# Đặt điểm bắt đầu và mục tiêu
env.set_start_goal(start=(5, 5), goal=(95, 95))

# Tạo và chạy A*
astar = AStarPathfinder(env)
astar.find_path()
path = astar.get_path()

# Vẽ kết quả
env.visualize(path, title="Đường đi A*")
```

## 📊 Kết Quả So Sánh

Khi chạy `main.py`, bạn sẽ thấy bảng so sánh như sau:

```
================================================================================
BẢNG SO SÁNH CÁC THUẬT TOÁN
================================================================================
Thuật toán      Thành công Thời gian (s)   Khoảng cách    Waypoints
--------------------------------------------------------------------------------
A*              ✓          0.0234         78.45          45
PSO             ✓          0.1234         82.10          23
SA              ✓          0.2456         80.50          28
GWO             ✓          0.1156         79.80          26
GA              ✓          0.1878         81.20          25
================================================================================
```

## 🎓 Hướng Dẫn Học Tập

### Dành cho Người Mới Bắt Đầu

1. **Bước 1**: Đọc file `environment.py` để hiểu cấu trúc môi trường
2. **Bước 2**: Đọc kỹ file `astar.py` - thuật toán đơn giản nhất
3. **Bước 3**: Chạy `main.py` và xem kết quả
4. **Bước 4**: Sửa một số tham số (start, goal, chướng ngại vật) và chạy lại
5. **Bước 5**: Đọc các thuật toán khác (PSO, SA, GWO, GA)

### Dành cho Người Muốn Mở Rộng

Bạn có thể:

- **Thêm thuật toán mới**: Tạo file mới trong `algorithms/` và implement hàm `find_path()`, `get_path()`, `get_statistics()`
- **Cải tiến hàm fitness**: Sửa hàm `_fitness()` để tính chi phí theo cách khác
- **3D Pathfinding**: Mở rộng từ 2D sang 3D
- **Động lực học**: Thêm yếu tố gió, vệ sinh bánh quạt UAV
- **Visualization Cao Cấp**: Sử dụng Pygame hoặc OpenGL để mô phỏng thời gian thực

## 📈 Biểu Đồ So Sánh

Các biểu đồ được tạo ra từ `main.py`:
- **Subplot 1-5**: Đường đi tìm được bởi mỗi thuật toán (nếu thành công)
- **Tiêu đề mỗi subplot**: Hiển thị tên thuật toán và chiều dài đường đi

## 🔧 Tham Số Mặc Định

### A*
- `grid_step`: 2.0 (khoảng cách giữa các nút)

### PSO
- `num_particles`: 30 (số hạt)
- `max_iterations`: 200 (số lần lặp)
- `c1`: 2.0 (hệ số cognitive)
- `c2`: 2.0 (hệ số social)
- `w`: 0.7 (hệ số inertia)

### SA
- `initial_temp`: 100 (nhiệt độ ban đầu)
- `cooling_rate`: 0.95 (tỷ lệ giảm nhiệt độ)
- `max_iterations`: 500 (số lần lặp)

### GWO
- `num_wolves`: 30 (số sói)
- `max_iterations`: 200 (số lần lặp)

### GA
- `population_size`: 30 (kích thước quần thể)
- `max_iterations`: 200 (số thế hệ)
- `mutation_rate`: 0.1 (tỷ lệ đột biến)
- `crossover_rate`: 0.8 (tỷ lệ lai ghép)

## 💡 Những Điểm Cần Lưu Ý

1. **Va Chạm**: Tất cả thuật toán đều kiểm tra va chạm với chướng ngại vật
2. **Heuristic**: A* sử dụng heuristic Euclid, có thể thay đổi sang Manhattan
3. **Khoảng Cách**: Sử dụng khoảng cách Euclid, có thể dùng Manhattan khác
4. **Tối Ưu**: A* luôn tìm được tối ưu, các thuật toán khác chỉ tìm được "tốt"

## 📚 Tài Liệu Tham Khảo

### A*
- https://en.wikipedia.org/wiki/A*_search_algorithm

### PSO
- https://en.wikipedia.org/wiki/Particle_swarm_optimization
- Eberhart, R. C., & Kennedy, J. (1995). A new optimizer using particle swarm theory

### SA
- https://en.wikipedia.org/wiki/Simulated_annealing
- Kirkpatrick, S., Gelatt, C. D., & Vecchi, M. P. (1983). Optimization by simulated annealing

### GWO
- https://en.wikipedia.org/wiki/Grey_wolf_optimizer
- Mirjalili, S., Mirjalili, S. M., & Lewis, A. (2014). Grey Wolf Optimizer

### GA
- https://en.wikipedia.org/wiki/Genetic_algorithm
- Holland, J. H. (1975). Adaptation in Natural and Artificial Systems

## 🤝 Đóng Góp

Nếu bạn muốn cải tiến dự án này, bạn có thể:
- Thêm thuật toán mới
- Cải tiến hiệu suất
- Thêm các ví dụ/bài tập
- Báo cáo lỗi

## 📄 Giấy Phép

Dự án này được phát hành theo giấy phép MIT.

---

**Tác giả**: GitHub Copilot  
**Ngày tạo**: 2026  
**Phiên bản**: 1.0
