# /review

Review toàn bộ code hiện tại theo rules của dự án HAPSO.

## Quy trình

1. Đọc toàn bộ file hoặc diff được chỉ định.
2. Kiểm tra lần lượt theo từng rule file:
   - `rules/code-style.md` — naming, imports, type hints
   - `rules/class-design.md` — class layout, method order, default params
   - `rules/error-handling.md` — print format, no try/except/raise
   - `rules/project-structure.md` — one responsibility, no circular imports

## Output

Liệt kê issues theo 3 mức, không bỏ qua bất kỳ vi phạm nào:

### 🔴 Critical
Vi phạm trực tiếp rule — phải sửa trước khi merge.

### 🟡 Warning
Không theo convention nhưng không gây lỗi runtime.

### 🟢 Suggestion
Có thể cải thiện để nhất quán hơn với codebase.

Nếu không có issue ở một mức → bỏ qua mức đó.
Cuối cùng: tổng số issues mỗi mức.
