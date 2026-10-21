# Hướng dẫn khắc phục lỗi

## Lỗi thường gặp và cách sửa

### 1. ImportError: No module named ...

**Lỗi:**
```
ImportError: No module named 'numpy'
ImportError: No module named 'matplotlib'
ImportError: No module named 'pandas'
```

**Giải pháp:**
```bash
pip install -r requirements.txt
```

Hoặc cài từng thư viện:
```bash
pip install numpy matplotlib pandas
```

---

### 2. TypeError: Rectangle.__init__() missing arguments

**Lỗi:**
```
TypeError: Rectangle.__init__() missing 2 required positional arguments
```

**Nguyên nhân:** Đã được sửa trong phiên bản mới

**Giải pháp:** Download lại file `main.py` mới nhất hoặc sửa thủ công:

```python
# SAI
from matplotlib.patches import Rectangle
simple_map.add_obstacle(Rectangle((30, 30, 20, 20)))

# ĐÚNG
from generate_map import Obstacle
simple_map.add_obstacle(Obstacle(30, 30, 20, 20))
```

---

### 3. FileNotFoundError: No such file or directory: './maps/...'

**Lỗi:**
```
FileNotFoundError: [Errno 2] No such file or directory: './maps/simple_map.json'
```

**Giải pháp:**

Tạo thư mục và bản đồ:
```bash
python generate_map.py
```

Hoặc tạo thư mục thủ công:
```python
import os
os.makedirs('./maps', exist_ok=True)
os.makedirs('./results', exist_ok=True)
```

---

### 4. Thuật toán không tìm thấy đường đi

**Triệu chứng:**
```
RRT*: Không tìm thấy đường đi!
PSO: Không tìm thấy đường đi hợp lệ (có collision)!
```

**Nguyên nhân:**
- Bản đồ quá phức tạp
- Tham số không phù hợp
- Start/Goal bị chướng ngại vật bao quanh

**Giải pháp:**

1. **Tăng số lần lặp:**
```python
# RRT*
rrt = RRTStar(map_obj, max_iterations=5000)  # Tăng từ 2000 lên 5000

# PSO
pso = PSO(map_obj, max_iterations=300)  # Tăng từ 200 lên 300
```

2. **Điều chỉnh tham số:**
```python
# RRT* - tăng search radius
rrt = RRTStar(map_obj, search_radius=10.0)  # Tăng từ 5.0 lên 10.0

# PSO - tăng số particles
pso = PSO(map_obj, num_particles=100)  # Tăng từ 50 lên 100
```

3. **Kiểm tra bản đồ:**
```python
from generate_map import Map2D

map_obj = Map2D.load('./maps/your_map.json')

# Kiểm tra start và goal có hợp lệ không
print(f"Start valid: {map_obj.is_valid_point(*map_obj.start)}")
print(f"Goal valid: {map_obj.is_valid_point(*map_obj.goal)}")
```

---

### 5. Chương trình chạy quá chậm

**Triệu chứng:**
- A* mất nhiều phút
- RRT* không kết thúc

**Giải pháp:**

1. **Giảm độ phân giải (A*):**
```python
# Thay vì 0.5m, dùng 1.0m hoặc 2.0m
astar = AStar(map_obj, grid_resolution=2.0)
```

2. **Giảm số lần lặp:**
```python
rrt = RRTStar(map_obj, max_iterations=1000)  # Giảm từ 3000
pso = PSO(map_obj, max_iterations=100)  # Giảm từ 200
```

3. **Giảm số waypoints (thuật toán meta-heuristic):**
```python
pso = PSO(map_obj, num_waypoints=10)  # Giảm từ 15
gwo = GWO(map_obj, num_waypoints=10)  # Giảm từ 15
```

---

### 6. Matplotlib không hiển thị hình

**Lỗi:**
Không có cửa sổ hiển thị khi chạy

**Giải pháp:**

1. **Kiểm tra backend:**
```python
import matplotlib
print(matplotlib.get_backend())
```

2. **Thay đổi backend nếu cần:**
```python
import matplotlib
matplotlib.use('TkAgg')  # Hoặc 'Qt5Agg'
import matplotlib.pyplot as plt
```

3. **Lưu thay vì hiển thị:**
```python
# Thêm save_path để lưu thay vì hiển thị
map_obj.visualize(save_path='./results/map.png')
```

---

### 7. Memory Error / Out of Memory

**Lỗi:**
```
MemoryError: Unable to allocate array
```

**Nguyên nhân:**
- Bản đồ quá lớn với A*
- Grid resolution quá nhỏ

**Giải pháp:**

1. **Tăng grid resolution:**
```python
astar = AStar(map_obj, grid_resolution=2.0)  # Thay vì 0.5
```

2. **Dùng thuật toán khác:**
```python
# Thay A* bằng RRT* cho bản đồ lớn
rrt = RRTStar(map_obj)
```

---

### 8. Đường đi không mượt / có góc nhọn

**Triệu chứng:**
- Đường đi gấp khúc
- Góc quay lớn

**Giải pháp:**

1. **Dùng thuật toán cho đường mượt hơn:**
```python
# A* với grid nhỏ hơn
astar = AStar(map_obj, grid_resolution=0.3)

# Hoặc dùng PSO/GA với nhiều waypoints
pso = PSO(map_obj, num_waypoints=20)
```

2. **Path smoothing sau khi tìm được đường:**
```python
def smooth_path(path, iterations=10):
    """Làm mượt đường đi"""
    smoothed = path.copy()
    for _ in range(iterations):
        for i in range(1, len(smoothed) - 1):
            # Trung bình 3 điểm
            x = (smoothed[i-1][0] + smoothed[i][0] + smoothed[i+1][0]) / 3
            y = (smoothed[i-1][1] + smoothed[i][1] + smoothed[i+1][1]) / 3
            smoothed[i] = (x, y)
    return smoothed

# Sử dụng
smoothed_path = smooth_path(path)
```

---

### 9. Collision vẫn xảy ra dù thuật toán báo thành công

**Nguyên nhân:**
- Thuật toán meta-heuristic có thể cho kết quả gần đúng
- Fitness function cho phép một số collision

**Giải pháp:**

1. **Kiểm tra collision:**
```python
from evaluate import PathEvaluator

evaluator = PathEvaluator(map_obj)
has_collision, num_collisions = evaluator.check_collision(path)
print(f"Có collision: {has_collision}, Số điểm: {num_collisions}")
```

2. **Tăng penalty cho collision:**
```python
# Trong file pso.py, gwo.py, etc.
# Tìm dòng collision_penalty và tăng giá trị
collision_penalty += 2000  # Thay vì 1000
```

3. **Chỉ dùng A* hoặc RRT* cho đường đi đảm bảo không collision:**
```python
# A* và RRT* luôn đảm bảo không collision
astar = AStar(map_obj)
path = astar.find_path()
```

---

## Gợi ý chung

### Test từng bước

1. **Test tạo bản đồ:**
```bash
python generate_map.py
```

2. **Test từng thuật toán:**
```bash
python test_quick.py
```

3. **Chạy full comparison:**
```bash
python main.py
```

### Tham số khuyến nghị

| Bản đồ | A* grid | RRT* iter | PSO particles | Waypoints |
|--------|---------|-----------|---------------|-----------|
| Nhỏ (50x50) | 0.5 | 1000 | 30 | 10 |
| Trung (100x100) | 1.0 | 2000 | 50 | 15 |
| Lớn (200x200) | 2.0 | 5000 | 100 | 20 |

### Liên hệ / Báo lỗi

Nếu gặp lỗi khác, vui lòng:
1. Kiểm tra lại version Python (>= 3.8)
2. Kiểm tra lại thư viện đã cài đúng version
3. Xem log chi tiết và tìm dòng lỗi
4. Thử chạy ví dụ đơn giản nhất trước (test_quick.py)
