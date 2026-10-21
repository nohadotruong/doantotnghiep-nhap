# /refactor

Tái cấu trúc một class hoặc file để đúng chuẩn HAPSO, không thay đổi behavior.

## Đầu vào

Chỉ định file hoặc class cần refactor. Ví dụ: `/refactor path_smoother.py`

## Quy trình

1. Đọc toàn bộ file chỉ định.
2. Áp dụng `rules/class-design.md`:
   - Sắp xếp lại thứ tự methods đúng layout.
   - Đưa tất cả tham số về `__init__` với default values.
3. Áp dụng `rules/code-style.md`:
   - Sửa naming nếu sai convention.
   - Sắp xếp lại imports.
   - Bổ sung type hints cho public methods nếu thiếu.
4. Áp dụng `rules/error-handling.md`:
   - Thay thế try/except bằng print() + early return.
   - Thay thế raise bằng print() + return None.
5. Xóa toàn bộ comments và docstrings.
6. Không thay đổi logic — output phải giống hệt trước refactor.

## Output

- File đã refactor hoàn chỉnh.
- Danh sách thay đổi theo từng rule đã áp dụng.
