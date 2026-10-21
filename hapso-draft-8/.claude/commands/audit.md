# /audit

Review tổng thể toàn bộ dự án — code, kiến trúc, chức năng, tính nhất quán.
Mục đích: cung cấp đủ thông tin để đưa ra quyết định điều chỉnh hệ thống.

---

## Quy trình

### Bước 1 — Đọc context

Đọc `CLAUDE.md` và toàn bộ `.claude/rules/` trước khi bắt đầu.

### Bước 2 — Quét cấu trúc

Duyệt toàn bộ thư mục dự án. Với mỗi file:

- Đúng vị trí theo kiến trúc trong `CLAUDE.md` không?
- Tên file đúng `snake_case` và phản ánh đúng nội dung không?
- Có file nào thừa, trùng lặp, hoặc không rõ vai trò không?

### Bước 3 — Review từng module

Với mỗi thư mục (`config/`, `core/`, `gui/`, `state/`, `map/`):

**Kiến trúc**

- Import direction có đúng không?
- Có circular import không?
- Có class nào nằm sai module không?

**Code conventions** (theo `rules/code-style.md`)

- Naming: variables, functions, classes, files
- Import sorting
- Type hints trên public methods

**Class design** (theo `rules/class-design.md`)

- Method order đúng layout không?
- Default params có nằm trong `__init__` không?
- Có nơi nào khởi tạo class với tham số bên ngoài không?

**Error handling** (theo `rules/error-handling.md`)

- Có `try/except`, `raise`, `hasattr()` không?
- Print format có đúng `[CLASS]: message` không?

**Hard constraints** (theo `CLAUDE.md`)

- Có hardcode constant không?
- Có docstring hoặc comment thừa không?
- GUI có lọt vào `core/algorithms/` không?

### Bước 4 — Kiểm tra tính nhất quán chức năng

- Mỗi thuật toán có đúng entry point `find_path(start, goal)` không?
- `AppState` có được dùng đúng chỗ không — không đọc/ghi state trực tiếp?
- `config/` có thực sự chứa toàn bộ constants không?

### Bước 5 — Kiểm tra CLAUDE.md

- Sơ đồ thư mục trong `CLAUDE.md` có khớp với thực tế không?
- Có gì thay đổi mà chưa cập nhật `CLAUDE.md` không?

---

## Output

Trình bày theo thứ tự ưu tiên xử lý:

### 🔴 Critical — Phá vỡ kiến trúc hoặc hard constraints

Mô tả cụ thể: file nào, dòng nào, vi phạm rule nào.

### 🟡 Warning — Không nhất quán, tiềm ẩn vấn đề

Mô tả cụ thể: file nào, dòng nào, nên sửa thành gì.

### 🟢 Suggestion — Cải thiện chất lượng

Có thể bỏ qua nếu không ảnh hưởng đến hoạt động.

### 📋 Tổng kết

- Số issues mỗi mức.
- Danh sách file cần xử lý ngay (Critical + Warning).
- Đề xuất thứ tự refactor nếu có nhiều file.
