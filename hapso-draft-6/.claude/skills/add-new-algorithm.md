# Skill: Add New Algorithm

## Kích hoạt khi
Nhận thấy yêu cầu thêm thuật toán path planning mới vào dự án.
Ví dụ: "thêm Dijkstra", "implement RRT", "viết BFS planner".

## Quy trình

### Bước 1 — Xác định thông tin
- Tên thuật toán → suy ra tên class (PascalCase) và tên file (snake_case).
- Loại thuật toán: graph-based (A*, Dijkstra) hay metaheuristic (PSO, GA)?

### Bước 2 — Tạo file planner
- Tạo `algorithms/<tên_file>.py`.
- Kế thừa `BasePlanner`.
- Import theo thứ tự trong `rules/code-style.md`.
- Toàn bộ tham số có default value trong `__init__` — không để trống.

### Bước 3 — Xây dựng class
Theo đúng `rules/class-design.md` — planner layout:
```
__init__
find_path          ← entry point, type annotated, trả về Optional[list[tuple[int,int]]]
[methods theo thứ tự gọi trong find_path]
[leaf helpers cuối cùng]
```

### Bước 4 — Kiểm tra edge cases
Trong `find_path`, xử lý trước khi chạy thuật toán:
```python
if start == goal:
    print("[TÊN_CLASS]: Warning — start equals goal.")
    return [start]
```

### Bước 5 — Kiểm tra import rules
- Không tạo circular import (xem `rules/project-structure.md`).
- `algorithms/` chỉ được import từ `map/`.

### Bước 6 — Output
- File `.py` hoàn chỉnh.
- Tóm tắt: tên class, tên file, danh sách methods và thứ tự.
