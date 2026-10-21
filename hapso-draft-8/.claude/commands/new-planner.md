# /new-planner

Tạo một planner class mới kế thừa BasePlanner, đúng chuẩn HAPSO.

## Đầu vào

Cung cấp tên planner khi gọi lệnh. Ví dụ: `/new-planner DijkstraPlanner`

## Quy trình

1. Tạo file mới theo tên class: `snake_case.py` trong thư mục `algorithms/`.
2. Kế thừa `BasePlanner`, import đúng thứ tự theo `rules/code-style.md`.
3. Xây dựng class theo `rules/class-design.md`:
   - `__init__` với tất cả tham số có **default value** — không để trống.
   - `find_path(self, start, goal)` là entry point duy nhất.
   - Các method nội bộ theo đúng thứ tự call từ `find_path`.
4. Annotate type hints cho toàn bộ public methods.
5. Không có comment, không có docstring.
6. In terminal output đúng format: `print("[TÊN_CLASS]: message")`

## Output

- File `.py` hoàn chỉnh, sẵn sàng dùng.
- Tóm tắt: danh sách methods đã tạo và thứ tự của chúng.
