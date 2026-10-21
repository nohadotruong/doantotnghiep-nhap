# Tối Ưu Hóa Đường Đi Cho UAV (Unmanned Aerial Vehicle)

## 📋 Giới Thiệu

Dự án này tập trung vào phát triển và so sánh các thuật toán tối ưu hóa để tìm đường đi tối ưu cho máy bay không người lái (UAV) trên bản đồ 2D có chứa chướng ngại vật.

### Các Thuật Toán Được Triển Khai:

1. **A\*** - Tìm kiếm heuristic
2. **RRT\*** - Rapidly-exploring Random Tree Star
3. **PSO** - Particle Swarm Optimization (Tối ưu hóa bầy đàn)
4. **GWO** - Grey Wolf Optimizer (Tối ưu hóa bầy sói xám)
5. **GA** - Genetic Algorithm (Thuật toán di truyền)
6. **SA** - Simulated Annealing (Luyện tôi mô phỏng)

## 📁 Cấu Trúc Dự Án

```
uav-path-optimization/
├── generate_map.py              # Tạo bản đồ có chướng ngại vật
├── object_function.py           # Hàm mục tiêu đánh giá chất lượng đường đi
├── metrics.py                   # Tính các chỉ số hiệu suất
├── optimizer_runner.py          # Chạy các thuật toán nhiều lần
├── compare_algorithm.py         # So sánh và tạo biểu đồ
├── main.py                      # Điểm vào chính của chương trình
├── requirements.txt             # Danh sách thư viện cần thiết
├── README.md                    # Tài liệu hướng dẫn
│
├── algorithms/                  # Thư mục chứa các thuật toán
│   ├── a_star.py               # Thuật toán A*
│   ├── rrt_star.py             # Thuật toán RRT*
│   ├── pso.py                  # Thuật toán PSO
│   ├── gwo.py                  # Thuật toán GWO
│   ├── ga.py                   # Thuật toán GA
│   └── sa.py                   # Thuật toán SA
│
├── maps/                        # Thư mục lưu bản đồ
│   └── (các file bản đồ JSON)
│
└── results/                     # Thư mục lưu kết quả
    ├── optimization_results.json
    ├── experiment_config.json
    ├── experiment_map.json
    ├── experiment_map.png
    ├── comparison_table.csv
    ├── path_length_comparison.png
    ├── execution_time_comparison.png
    ├── smoothness_comparison.png
    ├── safety_comparison.png
    ├── radar_comparison.png
    └── best_path_*.png
```

## 🚀 Hướng Dẫn Cài Đặt

### 1. Yêu Cầu

- Python 3.8+
- pip (Python package manager)

### 2. Cài Đặt Thư Viện

```bash
pip install -r requirements.txt
```

### Các thư viện chính:

- **numpy** - Tính toán số học
- **matplotlib** - Vẽ biểu đồ và bản đồ
- **pandas** - Xử lý dữ liệu và tạo bảng
- **scipy** - Các hàm tính toán khoa học

## 📖 Hướng Dẫn Sử Dụng

### 1. Chạy Toàn Bộ Thí Nghiệm

```bash
python main.py
```

Lệnh này sẽ:
- Tạo một bản đồ ngẫu nhiên
- Chạy tất cả 6 thuật toán 5 lần (mặc định)
- So sánh kết quả và tạo biểu đồ
- Lưu tất cả dữ liệu vào thư mục `results/`

### 2. Tạo Bản Đồ

```python
from generate_map import generate_random_map, Map2D

# Tạo bản đồ ngẫu nhiên
map_obj = generate_random_map(width=50, height=50, num_obstacles=5)

# Lưu bản đồ
map_obj.save('maps/my_map.json')

# Hiển thị bản đồ
map_obj.visualize(filename='maps/my_map.png')
```

### 3. Chạy Một Thuật Toán Cụ Thể

```python
from generate_map import generate_random_map
from algorithms.a_star import a_star_path_planning
from metrics import Metrics

# Tạo bản đồ
map_obj = generate_random_map(50, 50, 5)

# Chạy thuật toán A*
path = a_star_path_planning(map_obj, step_size=1.0)

# Tính các chỉ số
metrics = Metrics.compute_all_metrics(path, map_obj)

print(f"Độ dài đường đi: {metrics['path_length']:.2f}")
print(f"Số điểm dừng: {metrics['waypoints_count']}")
```

### 4. So Sánh Các Thuật Toán

```python
from generate_map import generate_random_map
from optimizer_runner import run_optimization_experiment
from compare_algorithm import AlgorithmComparator

# Tạo bản đồ
map_obj = generate_random_map(50, 50, 5)

# Chạy thí nghiệm
runner = run_optimization_experiment(map_obj, runs=5, output_dir='results')

# So sánh
comparator = AlgorithmComparator(runner)
comparator.plot_all_comparisons('results')
```

## 📊 Các Chỉ Số Đánh Giá

### 1. **Độ Dài Đường Đi (Path Length)**
- Tổng khoảng cách của đường đi
- **Mục tiêu**: Càng ngắn càng tốt

### 2. **Độ Mượt (Smoothness)**
- Tổng góc quay dọc theo đường đi
- **Mục tiêu**: Càng nhỏ càng tốt (đường thẳng hơn)

### 3. **Độ An Toàn (Safety Margin)**
- Khoảng cách tối thiểu đến chướng ngại vật
- **Mục tiêu**: Càng lớn càng tốt

### 4. **Hiệu Suất Đường Đi (Path Efficiency)**
- Tỷ số giữa khoảng cách Euclidean và độ dài thực tế
- **Mục tiêu**: Gần 1 càng tốt

### 5. **Thời Gian Thực Thi (Execution Time)**
- Thời gian chạy thuật toán
- **Mục tiêu**: Càng nhanh càng tốt

### 6. **Tỷ Lệ An Toàn (Clearance Ratio)**
- Phần trăm điểm có khoảng cách an toàn
- **Mục tiêu**: Cao nhất có thể (0-1)

## 🔧 Cấu Hình Thuật Toán

### Trong File `main.py`:

```python
config = {
    'map_config': {
        'type': 'random',           # 'random', 'corridor', 'maze'
        'width': 50,
        'height': 50,
        'num_obstacles': 5
    },
    'experiment_config': {
        'runs_per_algorithm': 5,     # Số lần chạy mỗi thuật toán
    },
    'algorithm_config': {
        'PSO': {
            'num_particles': 30,
            'max_iterations': 100,
            'num_waypoints': 5
        },
        # ... cấu hình cho các thuật toán khác
    }
}
```

## 📈 Giải Thích Biểu Đồ Kết Quả

### 1. **Biểu Đồ So Sánh Độ Dài Đường Đi**
- Hiển thị độ dài trung bình và độ lệch chuẩn
- Càng thấp càng tốt

### 2. **Biểu Đồ So Sánh Thời Gian Thực Thi**
- Thể hiện khả năng tính toán của mỗi thuật toán
- Thuật toán classic (A*, RRT*) thường nhanh hơn

### 3. **Biểu Đồ Radar**
- So sánh toàn diện các khía cạnh khác nhau
- Giúp dễ dàng nhận biết ưu điểm/nhược điểm của mỗi thuật toán

## 🤖 Chi Tiết Từng Thuật Toán

### A* (A-Star)
- **Loại**: Tìm kiếm heuristic
- **Ưu điểm**: Tìm đường đi tối ưu, nhanh chóng
- **Nhược điểm**: Cần rời rạc hóa không gian, không xử lý tốt không gian liên tục lớn

### RRT*
- **Loại**: Lấy mẫu ngẫu nhiên
- **Ưu điểm**: Tìm được đường đi trong không gian phức tạp
- **Nhược điểm**: Thời gian tính toán có thể lâu

### PSO
- **Loại**: Tối ưu hóa meta-heuristic
- **Ưu điểm**: Tìm được lời giải tốt, hội tụ nhanh
- **Nhược điểm**: Có thể bị lọc trong cực tiểu địa phương

### GWO
- **Loại**: Tối ưu hóa meta-heuristic (tinh thể độc lập)
- **Ưu điểm**: Cân bằng tốt giữa khai thác và khám phá
- **Nhược điểm**: Tham số cần tinh chỉnh

### GA
- **Loại**: Thuật toán di truyền
- **Ưu điểm**: Đa dạng lời giải, song song hóa tốt
- **Nhược điểm**: Có thể hội tụ chậm

### SA
- **Loại**: Tối ưu hóa ngẫu nhiên
- **Ưu điểm**: Đơn giản, thoát khỏi cực tiểu địa phương
- **Nhược điểm**: Cần cân chỉnh tham số nhiệt độ

## 💡 Mẹo và Trickys

### Tối Ưu Hóa Hiệu Suất

1. **Giảm Số Lần Chạy**: Thay đổi `runs_per_algorithm = 3` để chạy nhanh hơn
2. **Giảm Số Lần Lặp**: Giảm `max_iterations` trong cấu hình thuật toán
3. **Bản Đồ Nhỏ Hơn**: Giảm kích thước bản đồ từ 50x50 xuống 30x30

### Cải Thiện Chất Lượng Lời Giải

1. **Tăng Số Lần Lặp**: Tăng `max_iterations` cho thuật toán meta-heuristic
2. **Điều Chỉnh Tham Số**: 
   - PSO: Tăng `num_particles`
   - GA: Giảm `mutation_rate` để ít đột biến hơn
   - SA: Giảm `cooling_rate` để giảm nhanh hơn

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi: "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi: "Không tìm thấy đường đi"
- Kiểm tra xem điểm bắt đầu/kết thúc có bị chặn không
- Giảm bán kính VA chạm của UAV

### Biểu Đồ Không Hiển Thị
- Đảm bảo thư mục `results/` tồn tại
- Kiểm tra quyền ghi file

## 📝 Ví Dụ Sử Dụng Nâng Cao

### Chạy Thí Nghiệm Tùy Chỉnh

```python
from generate_map import Map2D
from optimizer_runner import OptimizerRunner

# Tạo bản đồ tùy chỉnh
map_obj = Map2D(width=60, height=60)
map_obj.set_start_goal((3, 3), (57, 57))
map_obj.add_obstacle(20, 20, 15, 5)
map_obj.add_obstacle(35, 35, 8, 12)

# Chạy tối ưu hóa
runner = OptimizerRunner(map_obj)
results = runner.run_all_algorithms(runs=3)

# In kết quả
runner.print_summary()
```

### Phân Tích Chi Tiết Kết Quả

```python
from compare_algorithm import AlgorithmComparator

comparator = AlgorithmComparator(runner)
df = comparator.create_comparison_dataframe()

# Sắp xếp theo độ dài đường đi
best_algorithms = df.nsmallest(3, 'Độ dài TB (m)')
print(best_algorithms)
```

## 📄 Tĩnh Năng Tương Lai

- [ ] Hỗ trợ bản đồ 3D
- [ ] Tối ưu hóa đa mục tiêu (độ dài + an toàn + thời gian)
- [ ] Giao diện GUI
- [ ] Xuất kết quả dưới dạng báo cáo HTML
- [ ] Hỗ trợ thêm thuật toán (Ant Colony Optimization, Bat Algorithm, v.v.)

## 🤝 Đóng Góp

Mọi đóng góp, gợi ý, và báo cáo bug đều được hoan nghênh.

## 📧 Liên Hệ

Nếu có bất kỳ câu hỏi hoặc cần hỗ trợ, vui lòng liên hệ.

## 📚 Tài Liệu Tham Khảo

1. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths
2. LaValle, S. M. (2006). Planning Algorithms
3. Kennedy, J., & Eberhart, R. (1995). Particle swarm optimization
4. Mirjalili, S., Mirjalili, S. M., & Lewis, A. (2014). Grey wolf optimizer

## 📄 Giấy Phép

MIT License

---

**Phiên bản**: 1.0  
**Cập nhật lần cuối**: 2026-02-17
