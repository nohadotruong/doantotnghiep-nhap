# ✅ Các Lỗi Được Sửa Chữa

## 1. Lỗi JSON Serialization (int32)
**Vấn đề:** `TypeError: Object of type int32 is not JSON serializable`

**Nguyên nhân:** NumPy trả về các kiểu dữ liệu như `int32`, `float64` không được hỗ trợ natively bởi `json.dump()`.

**Giải pháp:** 
- Tạo custom JSON encoder `NumpyEncoder` trong cả `main.py` và `optimizer_runner.py`
- Encoder tự động chuyển đổi numpy types sang Python native types:
  - `np.integer` → `int`
  - `np.floating` → `float`
  - `np.ndarray` → `list`

```python
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
```

---

## 2. Cấu Trúc Thư Mục Lưu Kết Quả
**Yêu Cầu:** Kết quả lưu vào `results/<datetime>/`, bản đồ ngẫu nhiên cũng lưu vào cùng thư mục

**Thay Đổi:**
- **main.py:** 
  - Tạo output directory theo cấu trúc: `results/<timestamp>/`
  - Timestamp format: `YYYYMMDD_HHMMSS` (ví dụ: `20260217_135526`)
  - Tất cả các file (config, map, results) đều lưu vào thư mục này

```python
base_dir = config['experiment_config']['output_directory']
timestamp = config['experiment_config']['timestamp']
output_dir = os.path.join(base_dir, timestamp)
```

**Kết Quả Cấu Trúc:**
```
results/
└── 20260217_135526/
    ├── experiment_config.json        # Cấu hình thí nghiệm
    ├── experiment_map.json           # Dữ liệu bản đồ
    ├── experiment_map.png            # Hình ảnh bản đồ
    ├── optimization_results.json     # Kết quả tối ưu (FIX JSON)
    ├── best_path_astar.png          # Đường đi tốt nhất A*
    ├── best_path_pso.png            # Đường đi tốt nhất PSO
    ├── best_path_ga.png             # Đường đi tốt nhất GA
    ├── best_path_gwo.png            # Đường đi tốt nhất GWO
    ├── best_path_sa.png             # Đường đi tốt nhất SA
    ├── best_path_rrtstar.png        # Đường đi tốt nhất RRT*
    ├── path_length_comparison.png    # Biểu đồ so sánh độ dài
    ├── execution_time_comparison.png # Biểu đồ so sánh thời gian
    ├── safety_comparison.png         # Biểu đồ so sánh an toàn
    ├── smoothness_comparison.png     # Biểu đồ so sánh độ mượt
    └── radar_comparison.png          # Biểu đồ Radar
```

---

## 3. Hỗ Trợ UTF-8 Trên Windows
**Vấn đề:** Unicode characters (emoji, Vietnamese) bị lỗi trên Windows PowerShell

**Giải pháp:**
- Thêm code tự động enable UTF-8 encoding trong main.py:

```python
import io

# Hỗ trợ UTF-8 trên Windows
if sys.stdout.encoding != 'utf-8':
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

**Kết Quả:** Không cần phải chạy `$env:PYTHONIOENCODING='utf-8'` trước khi chạy script

---

## 🎯 Tệp Được Sửa Chữa
1. ✅ **main.py**
   - Thêm NumpyEncoder
   - Thêm UTF-8 encoding support
   - Cập nhật logic tạo output directory

2. ✅ **optimizer_runner.py**
   - Thêm NumpyEncoder
   - Cập nhật save_results() để sử dụng NumpyEncoder
   - Thêm import numpy

---

## ✅ Kiểm Tra
- ✅ JSON file được lưu mà không có lỗi serialization
- ✅ Các file được lưu vào `results/<timestamp>/`
- ✅ UTF-8 characters hiển thị đúng trên Windows
- ✅ Tất cả kết quả và bản đồ trong cùng một folder

---

## 📝 Cách Sử Dụng
```bash
cd uav-path-optimization
python main.py
```

Kết quả sẽ được lưu vào folder: `results/YYYYMMDD_HHMMSS/`
