# Hệ thống tìm đường cho UAV (Unmanned Aerial Vehicle)

Hệ thống so sánh 6 thuật toán tìm đường tối ưu cho UAV trong môi trường 2D với các chướng ngại vật.

## 📋 Mô tả

Dự án này triển khai và so sánh 6 thuật toán tìm đường phổ biến cho UAV:

1. **A\*** - Thuật toán tìm kiếm heuristic
2. **RRT\*** - Rapidly-exploring Random Tree Star
3. **PSO** - Particle Swarm Optimization
4. **GWO** - Grey Wolf Optimizer
5. **SA** - Simulated Annealing
6. **GA** - Genetic Algorithm

## 🚀 Cài đặt

### Yêu cầu

```bash
Python 3.8+
numpy
matplotlib
pandas
```

### Cài đặt thư viện

```bash
pip install numpy matplotlib pandas
```

## 📁 Cấu trúc dự án

```
.
├── generate_map.py      # Tạo và quản lý bản đồ 2D
├── astar.py            # Thuật toán A*
├── rrt_star.py         # Thuật toán RRT*
├── pso.py              # Thuật toán PSO
├── gwo.py              # Thuật toán GWO
├── sa.py               # Thuật toán SA
├── ga.py               # Thuật toán GA
├── evaluate.py         # Đánh giá và so sánh thuật toán
├── main.py             # Chương trình chính
├── test_quick.py       # Test nhanh tất cả thuật toán (BẮT ĐẦU TỪ ĐÂY!)
├── examples.py         # 6 ví dụ sử dụng chi tiết
├── requirements.txt    # Thư viện cần thiết
├── CHANGELOG.md        # Nhật ký thay đổi
├── maps/               # Thư mục chứa các bản đồ
└── results/            # Thư mục chứa kết quả
    ├── 2024-02-14_13-45-30/    # Kết quả session 1
    │   ├── comparison.png
    │   ├── all_paths.png
    │   ├── rankings.csv
    │   ├── metrics_detail.csv
    │   └── summary.txt
    └── 2024-02-14_14-20-15/    # Kết quả session 2
        └── ...
```

### 💡 Tính năng tự động tạo thư mục theo thời gian

Mỗi lần chạy, kết quả sẽ được lưu vào thư mục con riêng biệt theo format:
- **Format**: `./results/YYYY-MM-DD_HH-MM-SS/`
- **Ví dụ**: `./results/2024-02-14_13-45-30/`
- **Lợi ích**: Không ghi đè kết quả cũ, dễ so sánh các lần chạy

**Các file được tạo trong mỗi session:**
1. `comparison.png` - Biểu đồ so sánh 6 thuật toán
2. `all_paths.png` - Tất cả đường đi trên cùng bản đồ
3. `rankings.csv` - Bảng xếp hạng (có thể mở bằng Excel)
4. `metrics_detail.csv` - Chi tiết tất cả chỉ số
5. `summary.txt` - Tổng kết toàn bộ kết quả

## 💻 Sử dụng

### 0. Test nhanh (Khuyến nghị bắt đầu từ đây!)

```bash
# Test tất cả thuật toán nhanh chóng
python test_quick.py

# Xem các ví dụ chi tiết
python examples.py
```

### 1. Tạo bản đồ

```bash
python generate_map.py
```

Hoặc sử dụng trong code:

```python
from generate_map import generate_random_map, generate_urban_map, Map2D

# Tạo bản đồ ngẫu nhiên
random_map = generate_random_map(width=100, height=100, num_obstacles=20)
random_map.save('./maps/my_map.json')

# Tạo bản đồ đô thị
urban_map = generate_urban_map()
urban_map.save('./maps/urban_map.json')
```

### 2. Chạy một thuật toán riêng lẻ

```python
from generate_map import Map2D
from astar import AStar

# Load bản đồ
map_obj = Map2D.load('./maps/simple_map.json')

# Chạy A*
astar = AStar(map_obj, grid_resolution=0.5)
path = astar.find_path()

if path:
    print(f"Độ dài đường đi: {astar.get_path_length():.2f} m")
    print(f"Thời gian: {astar.computation_time:.4f} s")
```

### 3. So sánh tất cả thuật toán

```bash
# Chạy nhanh - Mỗi thuật toán 1 lần
python main.py

# Chạy với bản đồ cụ thể
python main.py --map ./maps/urban_map.json

# Chạy với một số thuật toán
python main.py --algorithms A* RRT* PSO

# ⭐ MỚI: Chạy nhiều lần để tìm kết quả tối ưu (KHUYẾN NGHỊ!)
# Mỗi thuật toán chạy 10 lần và chọn kết quả tốt nhất
python main.py --num-runs 10

# Chạy rất chính xác (30 lần mỗi thuật toán)
python main.py --num-runs 30 --map ./maps/urban_map.json

# Tạo bản đồ mẫu trước khi chạy
python main.py --generate-maps
```

### 4. Demo tính năng Multiple Runs

```bash
# Xem demo chi tiết về tính năng chạy nhiều lần
python demo_multiple_runs.py
```

### 4. Đánh giá kết quả

```python
from evaluate import PathEvaluator

# Tạo evaluator
evaluator = PathEvaluator(map_obj)

# Đánh giá một đường đi
metrics = evaluator.evaluate(path, computation_time=0.5, algorithm_name="A*")
evaluator.print_metrics(metrics)
```

## 📊 Các chỉ số đánh giá

Hệ thống đánh giá các thuật toán dựa trên:

1. **Độ dài đường đi** - Tổng khoảng cách từ start đến goal
2. **Thời gian tính toán** - Thời gian để tìm ra đường đi
3. **Độ mượt** - Tổng góc quay (càng nhỏ càng mượt)
4. **Độ cong** - Độ cong trung bình của đường đi
5. **Khoảng cách an toàn** - Khoảng cách trung bình đến chướng ngại vật
6. **Tỷ lệ tối ưu** - Tỷ lệ so với đường thẳng
7. **Va chạm** - Số điểm va chạm với chướng ngại vật
8. **Tỷ lệ thành công** - Tìm được đường đi hay không

## 📂 Quản lý kết quả

### Cấu trúc thư mục kết quả

Mỗi lần chạy tạo một thư mục riêng:
```
./results/
├── 2024-02-14_13-45-30/        # Chạy lần 1
├── 2024-02-14_14-20-15/        # Chạy lần 2
└── 2024-02-14_15-00-00/        # Chạy lần 3
```

### So sánh kết quả giữa các lần chạy

**Cách 1: Xem file summary.txt**
```bash
# Xem tổng kết
cat ./results/2024-02-14_13-45-30/summary.txt
```

**Cách 2: So sánh CSV bằng Excel/LibreOffice**
```bash
# Mở file rankings.csv
excel ./results/2024-02-14_13-45-30/rankings.csv
```

**Cách 3: So sánh bằng pandas**
```python
import pandas as pd

# Đọc 2 lần chạy
df1 = pd.read_csv('./results/2024-02-14_13-45-30/metrics_detail.csv')
df2 = pd.read_csv('./results/2024-02-14_14-20-15/metrics_detail.csv')

# So sánh A*
print(df1[df1['algorithm'] == 'A*'][['path_length', 'computation_time']])
print(df2[df2['algorithm'] == 'A*'][['path_length', 'computation_time']])
```

### Dọn dẹp kết quả cũ

```bash
# Xóa kết quả cũ hơn 7 ngày (Linux/Mac)
find ./results -type d -mtime +7 -exec rm -rf {} +

# Hoặc xóa thủ công
rm -rf ./results/2024-02-14_13-45-30/
```

## 🎯 Ví dụ

### ⚠️ Vấn đề: Tính ngẫu nhiên trong thuật toán

Các thuật toán meta-heuristic (PSO, GWO, SA, GA) và RRT* có tính ngẫu nhiên, nên **mỗi lần chạy cho kết quả khác nhau**:

```python
# Lần 1: Độ dài = 145.23m
# Lần 2: Độ dài = 152.67m  
# Lần 3: Độ dài = 138.91m  ← Tốt nhất!
```

### ✅ Giải pháp: Chạy nhiều lần và chọn kết quả tốt nhất

```bash
# Chạy mỗi thuật toán 10 lần, chọn kết quả tối ưu nhất
python main.py --num-runs 10
```

**Lợi ích:**
- ✅ Tìm được đường đi tối ưu hơn (best run)
- ✅ Đánh giá độ ổn định của thuật toán (std deviation)
- ✅ Tỷ lệ thành công chính xác hơn
- ✅ So sánh công bằng giữa các thuật toán

**Kết quả bổ sung:**
- `statistics.csv` - Thống kê mean/std/min/max của 10 lần chạy
- File `summary.txt` bao gồm phân tích variance

### Ví dụ 1: Tạo bản đồ và chạy A*

```python
from generate_map import Map2D, Obstacle
from astar import AStar
import matplotlib.pyplot as plt

# Tạo bản đồ
map_obj = Map2D(100, 100)
map_obj.add_obstacle(Obstacle(30, 30, 20, 20))
map_obj.add_obstacle(Obstacle(60, 60, 15, 15))
map_obj.set_start(10, 10)
map_obj.set_goal(90, 90)

# Chạy A*
astar = AStar(map_obj, grid_resolution=0.5)
path = astar.find_path()

# Vẽ kết quả
map_obj.visualize()
if path:
    import numpy as np
    path_array = np.array(path)
    plt.plot(path_array[:, 0], path_array[:, 1], 'b-', linewidth=2)
    plt.show()
```

### Ví dụ 2: So sánh nhiều thuật toán

```python
from main import run_comparison

# So sánh tất cả thuật toán trên bản đồ urban
run_comparison('./maps/urban_map.json', output_dir='./results')

# Kết quả sẽ được lưu trong ./results/2024-02-14_13-45-30/:
# - comparison.png: Biểu đồ so sánh
# - all_paths.png: Tất cả đường đi trên cùng bản đồ
# - rankings.csv: Bảng xếp hạng
# - metrics_detail.csv: Chi tiết các chỉ số
# - summary.txt: Tổng kết toàn bộ
```

## ⚙️ Tùy chỉnh tham số

### A*
```python
AStar(map_obj, grid_resolution=0.5)  # Độ phân giải lưới
```

### RRT*
```python
RRTStar(map_obj, 
        max_iterations=3000,    # Số lần lặp
        step_size=2.0,          # Kích thước bước
        search_radius=5.0)      # Bán kính tìm kiếm
```

### PSO
```python
PSO(map_obj,
    num_particles=50,      # Số particles
    num_waypoints=15,      # Số waypoints
    max_iterations=200,    # Số thế hệ
    w=0.7,                 # Trọng số quán tính
    c1=1.5,                # Hệ số học cá nhân
    c2=1.5)                # Hệ số học xã hội
```

### GWO
```python
GWO(map_obj,
    num_wolves=30,         # Số sói
    num_waypoints=15,      # Số waypoints
    max_iterations=200)    # Số thế hệ
```

### SA
```python
SA(map_obj,
   num_waypoints=15,       # Số waypoints
   initial_temp=100.0,     # Nhiệt độ ban đầu
   final_temp=0.1,         # Nhiệt độ cuối
   cooling_rate=0.95,      # Tốc độ làm lạnh
   max_iterations=1000)    # Số lần lặp mỗi nhiệt độ
```

### GA
```python
GA(map_obj,
   population_size=50,     # Kích thước quần thể
   num_waypoints=15,       # Số waypoints
   max_generations=200,    # Số thế hệ
   mutation_rate=0.1,      # Tỷ lệ đột biến
   crossover_rate=0.8)     # Tỷ lệ lai ghép
```

## 📈 Kết quả mong đợi

Sau khi chạy, bạn sẽ có:

1. **Biểu đồ so sánh** - So sánh các chỉ số của các thuật toán
2. **Bản đồ đường đi** - Hiển thị tất cả đường đi trên cùng một bản đồ
3. **Bảng xếp hạng** - Xếp hạng các thuật toán dựa trên điểm tổng hợp
4. **Thống kê chi tiết** - Các chỉ số cho từng thuật toán

## 🔬 Phân tích thuật toán

### Ưu điểm và nhược điểm

| Thuật toán | Ưu điểm | Nhược điểm |
|-----------|---------|------------|
| **A\*** | Tối ưu, nhanh với bản đồ nhỏ | Chậm với bản đồ lớn, cần nhiều bộ nhớ |
| **RRT\*** | Tốt với không gian phức tạp | Đường đi không mượt, cần hậu xử lý |
| **PSO** | Nhanh, dễ triển khai | Có thể bị local optimum |
| **GWO** | Tốt với bài toán tối ưu phức tạp | Tốc độ hội tụ chậm |
| **SA** | Tránh local optimum tốt | Cần tune nhiều tham số |
| **GA** | Linh hoạt, song song hóa dễ | Chậm, cần quần thể lớn |

## 📝 Ghi chú

- Các thuật toán meta-heuristic (PSO, GWO, SA, GA) có thể không đảm bảo tìm được đường đi tối ưu
- A* cho kết quả tối ưu nhưng chậm hơn trên bản đồ lớn
- RRT* phù hợp với môi trường động và không gian phức tạp
- Tham số của các thuật toán cần được điều chỉnh tùy theo bài toán cụ thể

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc pull request.

## 📄 License

MIT License

## 👨‍💻 Tác giả

Hệ thống tìm đường cho UAV
