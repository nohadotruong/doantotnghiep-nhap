# Project Structure

## One Responsibility Per File

A file has **one reason to change**.
If you write "and" when describing what a file does → split it.

```
# Good
map/grid_map.py         ← "manages the grid model"
map/map_serializer.py   ← "saves and loads grid maps"

# Bad
map/grid_map.py         ← "manages the grid AND saves/loads maps"
```

---

## Private Helpers Stay Close to Their Caller

Do not move a helper to a shared module until **two or more** unrelated callers need it.

```python
# _segment_collision_count is only used by PSO fitness
# → keep it in pso.py, not in a shared utils module
```

---

## Cập nhật CLAUDE.md

Cập nhật `CLAUDE.md` ngay sau khi có thay đổi thuộc các loại sau:

| Thay đổi                               | Phần cần cập nhật trong CLAUDE.md |
| -------------------------------------- | --------------------------------- |
| Thêm / xóa / đổi tên file hoặc thư mục | Sơ đồ cấu trúc thư mục            |
| Thêm thuật toán mới                    | Sơ đồ + mô tả Key Modules nếu có  |
| Đổi entry point của class              | Hard constraints                  |
| Thêm / xóa dependency quan trọng       | Tech stack                        |
| Thay đổi import direction              | Phần Kiến trúc quan trọng         |
| Thêm workflow hoặc command mới         | Phần Workflows                    |

Không cập nhật `CLAUDE.md` nếu thay đổi chỉ là logic nội bộ trong file — cấu trúc bên ngoài không đổi thì không cần chỉnh.

---

## No Circular Imports

Allowed import directions (top → bottom only):

```
gui         →  algorithms, optimization, map, analytics
algorithms  →  map
analytics   →  algorithms, map
optimization →  (nothing from this project)
map         →  (nothing from this project)
```
