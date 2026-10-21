# Hướng dẫn nhanh (Quick Start)

## 🚀 Bắt đầu trong 3 bước

### Bước 1: Cài đặt (30 giây)

```bash
# Clone hoặc download dự án
# Sau đó cài đặt thư viện:
pip install -r requirements.txt
```

### Bước 2: Test nhanh (1-2 phút)

```bash
python test_quick.py
```

Chương trình sẽ:
- ✅ Tạo bản đồ test tự động
- ✅ Chạy tất cả 6 thuật toán
- ✅ Hiển thị kết quả ngắn gọn

### Bước 3: Chạy so sánh đầy đủ (3-5 phút)

**Chạy nhanh (1 lần/thuật toán):**
```bash
python main.py
```

**⭐ Chạy chính xác - KHUYẾN NGHỊ (10 lần/thuật toán):**
```bash
python main.py --num-runs 10
```

**Tại sao nên dùng `--num-runs 10`?**
- ✅ Các thuật toán PSO, GWO, SA, GA, RRT* có tính ngẫu nhiên
- ✅ Mỗi lần chạy cho kết quả khác nhau (±5-15%)
- ✅ Chạy 10 lần và chọn kết quả tốt nhất → So sánh công bằng hơn

Kết quả sẽ được lưu tự động vào:
```
./results/2024-02-14_13-45-30/
├── comparison.png          # Biểu đồ so sánh
├── all_paths.png          # Tất cả đường đi
├── rankings.csv           # Bảng xếp hạng
├── metrics_detail.csv     # Chi tiết các chỉ số
└── summary.txt            # Tổng kết
```

---

## 📋 Các lệnh thường dùng

### Tạo bản đồ mẫu

```bash
python generate_map.py
```

Hoặc với code:
```python
from generate_map import generate_random_map, generate_urban_map

# Bản đồ ngẫu nhiên
map1 = generate_random_map(width=100, height=100, num_obstacles=20)
map1.save('./maps/my_random_map.json')

# Bản đồ đô thị
map2 = generate_urban_map()
map2.save('./maps/my_urban_map.json')
```

### Chạy với bản đồ cụ thể

```bash
# Tạo bản đồ mẫu trước
python main.py --generate-maps

# Chạy nhanh (1 lần)
python main.py --map ./maps/urban_map.json

# Chạy chính xác (10 lần - KHUYẾN NGHỊ)
python main.py --map ./maps/urban_map.json --num-runs 10

# Kết quả: ./results/2024-02-14_13-45-30/
```

### Chỉ chạy một số thuật toán

```bash
# Chỉ chạy A* và RRT*
python main.py --algorithms A* RRT*

# Chỉ meta-heuristic, mỗi thuật toán 10 lần
python main.py --algorithms PSO GWO SA GA --num-runs 10
```

### Demo tính năng Multiple Runs

```bash
# Xem demo chi tiết về lợi ích của multiple runs
python demo_multiple_runs.py
```

### Chạy nhiều lần không lo ghi đè

```bash
# Lần 1
python main.py --map ./maps/urban_map.json
# → Lưu vào: ./results/2024-02-14_13-45-30/

# Lần 2  
python main.py --map ./maps/corridor_map.json
# → Lưu vào: ./results/2024-02-14_13-46-15/

# Kết quả cả 2 lần đều được giữ nguyên!
```

---

## 🎯 Các kịch bản sử dụng

### Kịch bản 1: Nghiên cứu so sánh thuật toán

**Mục tiêu**: So sánh hiệu suất 6 thuật toán trên nhiều bản đồ khác nhau

```bash
# Tạo các bản đồ test
python main.py --generate-maps

# Chạy trên bản đồ đơn giản
python main.py --map ./maps/simple_map.json
# → ./results/2024-02-14_10-00-00/

# Chạy trên bản đồ đô thị
python main.py --map ./maps/urban_map.json
# → ./results/2024-02-14_10-05-30/

# Chạy trên bản đồ hành lang
python main.py --map ./maps/corridor_map.json
# → ./results/2024-02-14_10-10-45/

# So sánh kết quả
cat ./results/*/summary.txt
```

### Kịch bản 2: Tìm thuật toán tốt nhất cho bài toán cụ thể

**Mục tiêu**: Tìm thuật toán phù hợp nhất cho môi trường đô thị

```bash
# Chạy tất cả thuật toán trên bản đồ urban
python main.py --map ./maps/urban_map.json

# Xem kết quả
cat ./results/YYYY-MM-DD_HH-MM-SS/summary.txt

# Hoặc mở file rankings.csv bằng Excel
```

### Kịch bản 3: Điều chỉnh tham số và so sánh

**Mục tiêu**: Tìm tham số tốt nhất cho thuật toán

```python
from generate_map import Map2D
from astar import AStar

map_obj = Map2D.load('./maps/urban_map.json')

# Test với grid resolution khác nhau
for grid_res in [0.5, 1.0, 2.0]:
    astar = AStar(map_obj, grid_resolution=grid_res)
    path = astar.find_path()
    print(f"Grid {grid_res}: Length={astar.get_path_length():.2f}m, "
          f"Time={astar.computation_time:.4f}s")
```

### Kịch bản 4: So sánh single run vs multiple runs

**Mục tiêu**: Xem sự khác biệt giữa chạy 1 lần và chạy nhiều lần

```bash
# Lần 1: Chạy single run
python main.py --map ./maps/urban_map.json
# → Lưu vào: ./results/2024-02-14_10-00-00/
# → PSO: 152.3m

# Lần 2: Chạy 10 lần và chọn best
python main.py --map ./maps/urban_map.json --num-runs 10
# → Lưu vào: ./results/2024-02-14_10-05-30/
# → PSO: 138.7m (tốt hơn 13.6m = 9%!)

# So sánh 2 file summary.txt
diff ./results/2024-02-14_10-00-00/summary.txt \
     ./results/2024-02-14_10-05-30/summary.txt
```

### Kịch bản 5: Nghiên cứu variance của thuật toán

**Mục tiêu**: Đánh giá độ ổn định (stability) của các thuật toán

```bash
# Chạy 30 lần để có thống kê tốt
python main.py --num-runs 30

# Xem file statistics.csv
# → Thuật toán nào có path_length_std nhỏ nhất = ổn định nhất
```

**Phân tích kết quả:**
```python
import pandas as pd

stats = pd.read_csv('./results/YYYY-MM-DD_HH-MM-SS/statistics.csv')

print("Độ ổn định (std càng nhỏ càng tốt):")
print(stats[['algorithm', 'path_length_std']].sort_values('path_length_std'))

print("\nTỷ lệ thành công:")
print(stats[['algorithm', 'success_rate']].sort_values('success_rate', ascending=False))
```

### Kịch bản 6: Xem ví dụ chi tiết

```bash
# Chạy 6 ví dụ từng bước
python examples.py

# Kết quả trong: ./results/examples_YYYY-MM-DD_HH-MM-SS/
```

---

## 📊 Hiểu kết quả

### File comparison.png

![Comparison](docs/comparison_example.png)

Biểu đồ so sánh 6 thuật toán theo:
- Độ dài đường đi
- Thời gian tính toán
- Độ mượt
- Tỷ lệ tối ưu
- Khoảng cách an toàn
- Tỷ lệ thành công

### File all_paths.png

![All Paths](docs/all_paths_example.png)

Hiển thị tất cả đường đi trên cùng bản đồ:
- **Xanh lá (Start)**: Điểm xuất phát
- **Sao đỏ (Goal)**: Điểm đích
- **Các màu khác nhau**: Đường đi của từng thuật toán

### File summary.txt

```
================================================================================
KẾT QUẢ SO SÁNH THUẬT TOÁN TÌM ĐƯỜNG CHO UAV
================================================================================

Thời gian chạy: 2024-02-14_13-45-30
Bản đồ: ./maps/urban_map.json
Kích thước: 100x100m
Số chướng ngại vật: 9
Start: (5, 5)
Goal: (95, 95)

================================================================================
BẢNG XẾP HẠNG
================================================================================
rank algorithm  total_score
   1       A*        85.50
   2     RRT*        78.30
   3      PSO        72.10
   ...

================================================================================
CHI TIẾT TỪNG THUẬT TOÁN
================================================================================

Thuật toán: A*
  - Độ dài đường đi: 145.23 m
  - Thời gian: 0.5432 s
  - Thành công: Có
  - Độ mượt: 234.56°
  - Tỷ lệ tối ưu: 1.15x
  - Va chạm: 0
...
```

---

## ⚡ Tips & Tricks

### Tip 1: Chạy nhanh hơn

```python
# Giảm độ phân giải
astar = AStar(map_obj, grid_resolution=2.0)  # Thay vì 0.5

# Giảm số lần lặp
rrt = RRTStar(map_obj, max_iterations=1000)  # Thay vì 3000
pso = PSO(map_obj, max_iterations=100)  # Thay vì 200
```

### Tip 2: Kết quả chính xác hơn

```python
# Tăng độ phân giải
astar = AStar(map_obj, grid_resolution=0.3)

# Tăng số lần lặp
rrt = RRTStar(map_obj, max_iterations=5000)
```

### Tip 3: Đường đi mượt hơn

```python
# Tăng số waypoints
pso = PSO(map_obj, num_waypoints=20)  # Thay vì 15
gwo = GWO(map_obj, num_waypoints=20)
```

### Tip 4: So sánh nhanh 2 lần chạy

```bash
# Dùng diff để so sánh summary
diff ./results/2024-02-14_13-45-30/summary.txt \
     ./results/2024-02-14_14-20-15/summary.txt
```

---

## 🆘 Gặp vấn đề?

### Lỗi "No module named..."
```bash
pip install -r requirements.txt
```

### Thuật toán không tìm thấy đường
- Tăng số lần lặp (max_iterations)
- Thử thuật toán khác (A* hoặc RRT*)
- Kiểm tra bản đồ có hợp lệ không

### Chương trình chạy quá chậm
- Giảm grid_resolution (cho A*)
- Giảm max_iterations
- Chạy ít thuật toán hơn: `--algorithms A* RRT*`

### Xem thêm
- **Chi tiết**: Xem file `TROUBLESHOOTING.md`
- **Tất cả tính năng**: Xem file `README.md`

---

## 📚 Tài liệu thêm

- `README.md` - Hướng dẫn đầy đủ
- `TROUBLESHOOTING.md` - Khắc phục lỗi
- `CHANGELOG.md` - Nhật ký thay đổi

---

**Chúc bạn thành công! 🎉**

Nếu có câu hỏi, hãy tham khảo README.md hoặc TROUBLESHOOTING.md
