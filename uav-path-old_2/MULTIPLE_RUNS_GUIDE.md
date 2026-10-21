# Hướng dẫn Multiple Runs - Tìm kết quả tối ưu

## 🎯 Vấn đề

Bạn có bao giờ thắc mắc tại sao mỗi lần chạy PSO, GWO, SA, GA, hoặc RRT* lại cho kết quả khác nhau?

```
Lần 1: PSO tìm được đường dài 152.3m
Lần 2: PSO tìm được đường dài 145.8m
Lần 3: PSO tìm được đường dài 138.2m ← Tốt nhất!
```

**Nguyên nhân:** Các thuật toán này sử dụng **tính ngẫu nhiên** (random) nên mỗi lần chạy cho kết quả khác nhau.

**Hệ quả:** So sánh không công bằng! PSO có thể "may mắn" hơn GWO trong 1 lần chạy, nhưng không có nghĩa PSO tốt hơn GWO.

## ✅ Giải pháp: Multiple Runs

**Chạy mỗi thuật toán N lần (ví dụ 10 lần) và chọn kết quả tốt nhất.**

```bash
python main.py --num-runs 10
```

### Quy trình hoạt động

```
Mỗi thuật toán (PSO, GWO, SA, GA, RRT*):
├─ Lần 1: 152.3m
├─ Lần 2: 145.8m
├─ Lần 3: 138.2m ← Best!
├─ Lần 4: 149.1m
├─ Lần 5: 142.7m
├─ Lần 6: 151.5m
├─ Lần 7: 140.3m
├─ Lần 8: 147.8m
├─ Lần 9: 144.2m
└─ Lần 10: 146.9m

→ Chọn Lần 3: 138.2m để so sánh với thuật toán khác
→ Lưu thống kê: Mean=144.9m, Std=±4.2m
```

## 📊 Lợi ích

### 1. Kết quả tối ưu hơn (Best Run)

So sánh single run vs multiple runs:

| Thuật toán | Single Run | Best of 10 Runs | Cải thiện |
|-----------|-----------|----------------|-----------|
| PSO | 152.3m | 138.2m | **9.2%** ↓ |
| GWO | 148.7m | 141.5m | **4.8%** ↓ |
| SA | 155.1m | 142.8m | **7.9%** ↓ |
| GA | 149.2m | 139.7m | **6.4%** ↓ |

### 2. Đánh giá độ ổn định (Stability)

Độ lệch chuẩn (std) cho biết thuật toán có ổn định không:

| Thuật toán | Mean | Std | Nhận xét |
|-----------|------|-----|----------|
| A* | 135.2m | ±0.0m | **Rất ổn định** (deterministic) |
| RRT* | 142.5m | ±6.8m | Không ổn định |
| PSO | 144.9m | ±4.2m | **Khá ổn định** |
| GWO | 146.3m | ±7.1m | Không ổn định |
| SA | 147.8m | ±5.3m | Trung bình |
| GA | 145.6m | ±4.9m | **Khá ổn định** |

**Kết luận:** PSO và GA ổn định hơn RRT* và GWO!

### 3. Tỷ lệ thành công chính xác

Với 1 lần chạy:
- PSO thành công → Success rate = 100% ❓
- PSO thất bại → Success rate = 0% ❓

Với 10 lần chạy:
- 8/10 lần thành công → Success rate = **80%** ✓ (chính xác)

### 4. So sánh công bằng

**Trước (Single Run):**
```
PSO (may mắn): 138.2m
GWO (kém may): 155.3m
→ PSO thắng? Không chắc!
```

**Sau (Multiple Runs):**
```
PSO (best of 10): 138.2m, mean=144.9m, std=±4.2m
GWO (best of 10): 141.5m, mean=146.3m, std=±7.1m
→ PSO tốt hơn GWO (cả best và mean) ✓
```

## 🚀 Cách sử dụng

### Cơ bản

```bash
# Chạy nhanh (1 lần) - Dùng để test
python main.py

# Chạy chính xác (10 lần) - KHUYẾN NGHỊ cho nghiên cứu
python main.py --num-runs 10

# Chạy rất chính xác (30 lần) - Dùng cho paper
python main.py --num-runs 30
```

### Nâng cao

```bash
# Chỉ chạy thuật toán meta-heuristic, mỗi thuật toán 20 lần
python main.py --algorithms PSO GWO SA GA --num-runs 20

# Chạy trên bản đồ phức tạp với 15 lần
python main.py --map ./maps/corridor_map.json --num-runs 15
```

### Demo chi tiết

```bash
# Xem demo với visualization
python demo_multiple_runs.py
```

## 📈 Kết quả bổ sung

Khi chạy với `--num-runs > 1`, bạn sẽ nhận được thêm:

### File: statistics.csv

```csv
algorithm,path_length_mean,path_length_std,path_length_min,path_length_max,success_rate
PSO,144.92,4.23,138.21,152.34,1.00
GWO,146.35,7.12,141.52,161.23,0.90
SA,147.81,5.28,142.78,158.91,0.80
GA,145.63,4.87,139.67,156.42,0.90
```

### File: summary.txt (bổ sung)

```
================================================================================
THỐNG KÊ 10 LẦN CHẠY
================================================================================

Thuật toán: PSO
  - Tỷ lệ thành công: 100.0% (10/10 lần)
  - Độ dài TB: 144.92 ± 4.23 m
  - Độ dài min/max: 138.21 / 152.34 m
  - Thời gian TB: 0.3421 ± 0.0234 s
  - Tỷ lệ có va chạm: 0.0%
```

## ⏱️ Thời gian chạy

| Số lần chạy | Thời gian (6 thuật toán) | Khuyến nghị |
|------------|-------------------------|-------------|
| 1 lần | ~30 giây | Test nhanh |
| 10 lần | ~5 phút | **Khuyến nghị** cho nghiên cứu thông thường |
| 20 lần | ~10 phút | Chính xác hơn |
| 30 lần | ~15 phút | Cho paper / báo cáo chính thức |

**Lưu ý:** A* tự động chỉ chạy 1 lần vì nó deterministic (không ngẫu nhiên).

## 🎓 Best Practices

### Khi nào nên dùng Multiple Runs?

✅ **NÊN dùng khi:**
- So sánh hiệu suất các thuật toán
- Viết paper / báo cáo nghiên cứu
- Đánh giá độ ổn định
- Tìm tham số tốt nhất

❌ **KHÔNG cần khi:**
- Test nhanh / debug code
- Demo / presentation (dùng 1 lần cho nhanh)
- Đã biết rõ kết quả cần tìm

### Nên chạy bao nhiêu lần?

| Mục đích | Số lần khuyến nghị |
|---------|-------------------|
| Test nhanh | 1-3 lần |
| Nghiên cứu thông thường | **10 lần** |
| Paper / Báo cáo | 20-30 lần |
| Nghiên cứu sâu | 50-100 lần |

### Phân tích kết quả

```python
import pandas as pd

# Đọc statistics
stats = pd.read_csv('./results/YYYY-MM-DD_HH-MM-SS/statistics.csv')

# 1. Thuật toán tốt nhất (best run)
print("Best algorithm (min path_length_min):")
print(stats.loc[stats['path_length_min'].idxmin()])

# 2. Thuật toán ổn định nhất (std thấp nhất)
print("\nMost stable (min std):")
print(stats.nsmallest(3, 'path_length_std')[['algorithm', 'path_length_std']])

# 3. Tỷ lệ thành công
print("\nSuccess rates:")
print(stats[['algorithm', 'success_rate']].sort_values('success_rate', ascending=False))

# 4. Tổng hợp
print("\nOverall ranking:")
# Normalize và kết hợp các chỉ số
stats['score'] = (
    stats['path_length_min'].rank() * 0.4 +  # 40% trọng số cho best
    stats['path_length_mean'].rank() * 0.3 +  # 30% cho mean
    stats['path_length_std'].rank() * 0.2 +   # 20% cho stability
    (1 - stats['success_rate']).rank() * 0.1  # 10% cho success rate
)
print(stats[['algorithm', 'score']].sort_values('score'))
```

## 💡 Tips

### Tip 1: Chạy song song để nhanh hơn

Nếu muốn nhanh hơn, có thể chạy từng thuật toán riêng:

```bash
# Terminal 1
python main.py --algorithms PSO --num-runs 30

# Terminal 2
python main.py --algorithms GWO --num-runs 30

# Terminal 3
python main.py --algorithms SA GA --num-runs 30
```

### Tip 2: Lưu seed để reproduce

Nếu cần reproduce kết quả:

```python
import numpy as np

# Đặt seed trước khi chạy
np.random.seed(42)

# Chạy thuật toán
# Kết quả sẽ giống nhau mỗi lần với cùng seed
```

### Tip 3: Tăng iterations thay vì runs

Đôi khi tăng `max_iterations` hiệu quả hơn tăng số lần chạy:

```bash
# Thay vì: 10 runs x 200 iterations = 2000 total iterations
python main.py --num-runs 10

# Có thể: 1 run x 2000 iterations (nếu chỉnh trong code)
# → Nhanh hơn nhưng không đánh giá được variance
```

## 📚 Tài liệu tham khảo

- `README.md` - Hướng dẫn tổng quan
- `demo_multiple_runs.py` - Demo trực quan
- `multiple_runs.py` - Implementation chi tiết
- `CHANGELOG.md` - Version 1.2 update notes

---

**Tóm lại:** 

🎯 **Vấn đề:** Thuật toán ngẫu nhiên → Kết quả khác nhau mỗi lần  
✅ **Giải pháp:** Chạy N lần, chọn best → So sánh công bằng  
🚀 **Cách dùng:** `python main.py --num-runs 10`  
📊 **Lợi ích:** Best run + Statistics + Fair comparison  

**KHUYẾN NGHỊ:** Luôn dùng `--num-runs 10` khi so sánh thuật toán! 🎉
