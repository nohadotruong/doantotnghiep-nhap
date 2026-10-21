# Random Obstacle Map Generation - `simple_map()`

## 🎯 Tính Năng Mới

Environment class hiện đã hỗ trợ **tạo map ngẫu nhiên** với chướng ngại vật tự động được sinh.

---

## 📝 Cách Sử Dụng

### **Cách 1: Tạo map khi init**
```python
from utils.environment import UAVEnvironment

# Tạo environment với 5 chướng ngại vật ngẫu nhiên
env = UAVEnvironment(width=100, height=100, num_obstacles=5)

# Set start và goal
env.set_start_goal((5, 5), (95, 95))
```

### **Cách 2: Tạo map sau init (khuyến nghị)**
```python
# Tạo environment trống
env = UAVEnvironment(width=100, height=100)

# Tạo 5 chướng ngại vật ngẫu nhiên
env.simple_map(num_obstacles=5, seed=42)

# Set start và goal
env.set_start_goal((5, 5), (95, 95))
```

### **Cách 3: Tạo lại map mới**
```python
# Xóa obstacles cũ, tạo 7 chướng ngại vật mới
env.simple_map(num_obstacles=7)
```

---

## 🔧 Tham Số

### `simple_map(num_obstacles=5, seed=None)`

| Tham số | Kiểu | Mặc định | Mô Tả |
|--------|------|---------|-------|
| `num_obstacles` | int | 5 | Số lượng chướng ngại vật |
| `seed` | int/None | None | Random seed (cho kết quả lặp lại) |

---

## 🎲 Cơ Chế Tạo Obstacles

Obstacles được tạo **hoàn toàn ngẫu nhiên**:

### **Loại Obstacles** (60% hình chữ nhật, 40% hình tròn)
```python
# 60% chính là hình chữ nhật
rectangle: 
  - Position: random trong vùng (10, height*0.7) × (10, width*0.7)
  - Size: width = [10-25], height = [8-20]

# 40% chính là hình tròn
circle:
  - Position: random trong vùng (15, height*0.7) × (15, width*0.7)
  - Radius: [5-12]
```

---

## 📊 Ví Dụ Thực Tế

### Ví dụ 1: Map giống nhau (dùng seed)
```python
# Run 1
env1 = UAVEnvironment(width=100, height=100)
env1.simple_map(num_obstacles=5, seed=42)
# → Obstacles như nhau với run 2

# Run 2
env2 = UAVEnvironment(width=100, height=100)
env2.simple_map(num_obstacles=5, seed=42)
# → Obstacles như nhau với run 1
```

### Ví dụ 2: Map khác nhau (không seed)
```python
env = UAVEnvironment(width=100, height=100)
env.simple_map(num_obstacles=5)  # Khác nhau mỗi lần chạy
```

### Ví dụ 3: Sử dụng trong main.py
```python
def create_environment():
    """Create UAV environment with random obstacles"""
    env = UAVEnvironment(width=100, height=100)
    
    # Generate 5 random obstacles (reproducible)
    env.simple_map(num_obstacles=5, seed=42)
    
    env.set_start_goal(
        start=(5, 5),
        goal=(95, 95)
    )
    
    return env
```

---

## 🔄 Thay Đổi Từ Cũ → Mới

### **Trước (Manual)**
```python
env = UAVEnvironment(width=100, height=100)
env.add_rectangular_obstacle(20, 30, 20, 10)
env.add_rectangular_obstacle(50, 50, 15, 25)
env.add_circular_obstacle(35, 70, 8)
env.set_start_goal((5, 5), (95, 95))
```

### **Sau (Simple Map)**
```python
env = UAVEnvironment(width=100, height=100)
env.simple_map(num_obstacles=5, seed=42)  # ← Một dòng!
env.set_start_goal((5, 5), (95, 95))
```

---

## 💡 Lợi Ích

✅ **Đơn giản**: Một dòng code thay vì nhiều dòng add_obstacle
✅ **Linh hoạt**: Dễ dàng điều chỉnh số lượng obstacles
✅ **Tái lập**: Seed cho kết quả giống nhau
✅ **Đa dạng**: Obstacles phân bố ngẫu nhiên trên map
✅ **Tối ưu**: Obstacles không ở gần start/goal (margins)

---

## 📁 Files Được Cập Nhật

- ✅ `utils/environment.py` - Thêm simple_map()
- ✅ `main.py` - Sử dụng simple_map()
- ✅ `examples_detailed.py` - Sử dụng simple_map()
- ✅ `quickstart_visualization.py` - Sử dụng simple_map()
- ✅ `test_fixes.py` - Sử dụng simple_map()

---

## 🚀 Sử Dụng Ngay

```bash
# Chạy test
python test_fixes.py

# Hoặc chạy main với map ngẫu nhiên
python main.py
```

Mỗi lần chạy sẽ tạo **5 chướng ngại vật ngẫu nhiên** trên map! 🎲✨
