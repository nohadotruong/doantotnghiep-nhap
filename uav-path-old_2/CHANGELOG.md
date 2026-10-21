# Nhật ký thay đổi (Changelog)

## [Version 1.2] - 2024-02-14

### ✨ Tính năng mới: Multiple Runs - Chạy nhiều lần để tìm kết quả tối ưu

#### 🎯 Vấn đề được giải quyết
Các thuật toán meta-heuristic (PSO, GWO, SA, GA) và RRT* có tính ngẫu nhiên nên mỗi lần chạy cho kết quả khác nhau. Điều này gây khó khăn trong việc so sánh công bằng giữa các thuật toán.

#### ✅ Giải pháp
**Chạy mỗi thuật toán nhiều lần (N lần) và chọn kết quả tốt nhất (best run)** để so sánh.

#### 📦 Files mới
1. **multiple_runs.py** (MỚI!) - Module chạy thuật toán nhiều lần
   - Class `MultipleRunsOptimizer`: Chạy 1 thuật toán N lần
   - Function `run_all_algorithms_optimized()`: Chạy tất cả thuật toán với multiple runs
   - Tự động chọn run tốt nhất (không collision, độ dài ngắn nhất)
   - Tính statistics: mean, std, min, max, median

2. **demo_multiple_runs.py** (MỚI!) - Demo tính năng
   - Demo 1: Chạy PSO 10 lần và xem sự khác biệt
   - Demo 2: So sánh PSO vs GWO (mỗi thuật toán 10 lần)
   - Demo 3: Vẽ biểu đồ phân bố kết quả
   - Demo 4: Chạy tất cả thuật toán với multiple runs

#### 🔧 Cập nhật main.py
- Thêm parameter `--num-runs` (default: 1)
- Tích hợp `MultipleRunsOptimizer` khi `num_runs > 1`
- Lưu thêm file `statistics.csv` với thống kê N lần chạy
- Cập nhật `summary.txt` với thông tin variance

#### 📊 Kết quả bổ sung

**File statistics.csv bao gồm:**
- `path_length_mean` - Độ dài trung bình
- `path_length_std` - Độ lệch chuẩn
- `path_length_min/max` - Độ dài min/max
- `computation_time_mean/std` - Thời gian TB và độ lệch
- `success_rate` - Tỷ lệ thành công
- `collision_rate` - Tỷ lệ có va chạm

#### 💡 Cách sử dụng

**Chạy nhanh (single run):**
```bash
python main.py  # Mỗi thuật toán chạy 1 lần
```

**Chạy chính xác (multiple runs - KHUYẾN NGHỊ):**
```bash
python main.py --num-runs 10  # Mỗi thuật toán chạy 10 lần
```

**Chạy rất chính xác:**
```bash
python main.py --num-runs 30  # Mỗi thuật toán chạy 30 lần
```

**Xem demo:**
```bash
python demo_multiple_runs.py
```

#### 📈 Lợi ích

✅ **Kết quả tối ưu hơn**: Chọn best run trong N lần  
✅ **Đánh giá độ ổn định**: Biết được variance của thuật toán  
✅ **So sánh công bằng**: Tất cả thuật toán đều được chạy N lần  
✅ **Tỷ lệ thành công chính xác**: Dựa trên N lần thử  

#### 🎓 Lưu ý
- **A* là deterministic** nên chỉ cần chạy 1 lần (tự động)
- **RRT*, PSO, GWO, SA, GA** nên chạy ≥10 lần để kết quả ổn định
- Thời gian chạy tăng tỷ lệ thuận với `num_runs`
- Khuyến nghị: `num_runs=10` cho nghiên cứu thông thường

---

## [Version 1.1] - 2024-02-14

### ✨ Tính năng mới

#### Tự động tạo thư mục kết quả theo datetime
- **Mô tả**: Kết quả giờ được lưu vào thư mục con có tên theo thời gian chạy
- **Format**: `./results/YYYY-MM-DD_HH-MM-SS/`
- **Ví dụ**: `./results/2024-02-14_13-45-30/`
- **Lợi ích**: 
  - Không ghi đè kết quả cũ
  - Dễ dàng theo dõi và so sánh các lần chạy khác nhau
  - Tự động sắp xếp theo thứ tự thời gian

#### Files mới được lưu trong mỗi session
1. **comparison.png** - Biểu đồ so sánh các thuật toán
2. **all_paths.png** - Tất cả đường đi trên cùng bản đồ
3. **rankings.csv** - Bảng xếp hạng dạng CSV
4. **metrics_detail.csv** - Chi tiết tất cả các chỉ số
5. **summary.txt** - Tổng kết chi tiết (MỚI!)

#### File summary.txt bao gồm:
- Thời gian chạy
- Thông tin bản đồ
- Bảng xếp hạng
- Chi tiết từng thuật toán

### 🔧 Cải tiến

#### main.py
- Thêm `from datetime import datetime`
- Tự động tạo thư mục con theo timestamp
- Lưu thêm `rankings.csv`, `metrics_detail.csv`, `summary.txt`
- Hiển thị đường dẫn thư mục kết quả trước khi chạy

#### test_quick.py
- Thêm thông báo về cấu trúc thư mục mới

#### examples.py
- Sử dụng timestamp riêng cho mỗi session: `examples_YYYY-MM-DD_HH-MM-SS`
- Tất cả kết quả ví dụ được lưu trong thư mục có timestamp

### 📁 Cấu trúc thư mục mới

```
./results/
├── 2024-02-14_13-45-30/        # Session 1
│   ├── comparison.png
│   ├── all_paths.png
│   ├── rankings.csv
│   ├── metrics_detail.csv
│   └── summary.txt
├── 2024-02-14_14-20-15/        # Session 2
│   ├── comparison.png
│   ├── all_paths.png
│   ├── rankings.csv
│   ├── metrics_detail.csv
│   └── summary.txt
└── examples_2024-02-14_15-00-00/  # Examples session
    ├── example_map.png
    ├── example_astar.png
    ├── example_rrt_star.png
    └── example_comparison.png
```

### 📝 Ví dụ sử dụng

#### Chạy so sánh:
```bash
python main.py
# Kết quả sẽ tự động lưu vào: ./results/2024-02-14_13-45-30/
```

#### Chạy nhiều lần:
```bash
python main.py --map ./maps/urban_map.json
# Lần 1: ./results/2024-02-14_13-45-30/

python main.py --map ./maps/corridor_map.json  
# Lần 2: ./results/2024-02-14_13-50-15/
# → Kết quả không bị ghi đè!
```

### 🐛 Bug fixes
- Sửa lỗi `TypeError: Rectangle.__init__()` trong main.py
- Đảm bảo tất cả thư mục được tạo đúng cách

---

## [Version 1.0] - 2024-02-14

### 🎉 Phát hành ban đầu

#### Tính năng chính
- 6 thuật toán tìm đường: A*, RRT*, PSO, GWO, SA, GA
- Tạo bản đồ 2D với chướng ngại vật
- 8 chỉ số đánh giá hiệu suất
- So sánh và xếp hạng thuật toán
- Biểu đồ trực quan

#### Files
- generate_map.py
- astar.py, rrt_star.py, pso.py, gwo.py, sa.py, ga.py
- evaluate.py
- main.py
- test_quick.py
- examples.py
- README.md
- TROUBLESHOOTING.md
- requirements.txt
