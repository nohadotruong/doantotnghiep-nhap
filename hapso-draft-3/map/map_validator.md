Hãy tưởng tượng `GridMap` là một tấm bản đồ, `MapSerializer` là người lưu nó vào tủ hồ sơ 📁…
còn `MapValidator` chính là **anh bảo vệ đứng cửa** 🛂:

> “Map này hợp lệ mới được đi vào thuật toán. Không thì quay đầu!”

---

# 🎯 `MapValidator` dùng để làm gì?

👉 **Kiểm tra tính hợp lệ của map trước khi chạy thuật toán**

---

# 💥 Nếu KHÔNG có validator thì sao?

Bạn sẽ gặp những thứ kiểu:

- ❌ Không có `start` hoặc `goal`
- ❌ `start` nằm trong obstacle
- ❌ `goal` bị block kín
- ❌ Map full obstacle (không có đường đi)
- ❌ Start = Goal (có thể hợp lệ, có thể không tùy rule)

👉 Và kết quả là:

- A\* chạy lỗi hoặc trả path rỗng
- PSO “bay loạn” không hội tụ
- GUI hiển thị… không biết chuyện gì đang xảy ra 😵

---

# 🧠 Vai trò đúng của `MapValidator`

- ✅ Check logic map (domain rule)
- ✅ Trả về lỗi rõ ràng cho UI
- ❌ Không sửa map
- ❌ Không chạy thuật toán

---

# 🧱 Cấu trúc chuẩn

```python
class MapValidator:
    @staticmethod
    def validate(grid_map) -> tuple[bool, str]:
        ...
```

---

# 🔍 Những gì nên kiểm tra

## 🥇 1. Start & Goal tồn tại

```python
if grid_map.start is None:
    return False, "Start point chưa được đặt"

if grid_map.goal is None:
    return False, "Goal point chưa được đặt"
```

---

## 🥈 2. Start/Goal không nằm trên obstacle

```python
sx, sy = grid_map.start
gx, gy = grid_map.goal

if grid_map.is_obstacle(sx, sy):
    return False, "Start nằm trên obstacle"

if grid_map.is_obstacle(gx, gy):
    return False, "Goal nằm trên obstacle"
```

---

## 🥉 3. Map có ô trống

```python
if grid_map.get_obstacle_count() == grid_map.width * grid_map.height:
    return False, "Map toàn obstacle"
```

---

## 🔥 4. (Optional nhưng rất mạnh) Có đường đi không?

👉 Dùng BFS nhẹ để check

```python
@staticmethod
def _has_path(grid_map) -> bool:
    from collections import deque

    visited = set()
    queue = deque([grid_map.start])

    while queue:
        x, y = queue.popleft()

        if (x, y) == grid_map.goal:
            return True

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy

            if not grid_map.is_inside(nx, ny):
                continue
            if grid_map.is_obstacle(nx, ny):
                continue
            if (nx, ny) in visited:
                continue

            visited.add((nx, ny))
            queue.append((nx, ny))

    return False
```

---

```python
if not MapValidator._has_path(grid_map):
    return False, "Không tồn tại đường đi từ Start đến Goal"
```

---

# 🧩 Full version gọn gàng

```python
class MapValidator:
    @staticmethod
    def validate(grid_map) -> tuple[bool, str]:
        if grid_map.start is None:
            return False, "Chưa đặt Start"

        if grid_map.goal is None:
            return False, "Chưa đặt Goal"

        sx, sy = grid_map.start
        gx, gy = grid_map.goal

        if grid_map.is_obstacle(sx, sy):
            return False, "Start nằm trên obstacle"

        if grid_map.is_obstacle(gx, gy):
            return False, "Goal nằm trên obstacle"

        if grid_map.get_obstacle_count() == grid_map.width * grid_map.height:
            return False, "Map toàn obstacle"

        if not MapValidator._has_path(grid_map):
            return False, "Không có đường đi"

        return True, "Valid map"
```

---

# 🔄 Dùng ở đâu?

👉 Trong GUI trước khi chạy thuật toán:

```python
is_valid, msg = MapValidator.validate(grid_map)

if not is_valid:
    self.status = msg
    return
```

---

# 🎯 Insight cực quan trọng

> 📌 Validator giúp bạn **fail sớm, fail rõ ràng**

Thay vì:

- chạy A\* → fail
- debug 30 phút

→ bạn fail ngay với message:

> “Goal nằm trên obstacle”

---

# ⚡ Bonus nâng cấp (pro hơn)

Bạn có thể tách ra:

```python
validate_basic()
validate_connectivity()
validate_for_algorithm(algo_type)
```

👉 Ví dụ:

- PSO có thể không cần strict như A\*
- A\* cần connectivity chắc chắn

---

# 🧩 Kết luận

- `MapValidator` = **bộ lọc trước khi chạy thuật toán**
- Giúp:
  - tránh crash
  - debug dễ
  - UX tốt hơn
