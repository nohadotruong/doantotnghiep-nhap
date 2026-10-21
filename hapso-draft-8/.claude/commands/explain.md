# /explain

Phân tích và mô tả toàn bộ hệ thống — thành phần, chức năng, luồng hoạt động.
Mục đích: giúp hiểu rõ hệ thống đang làm gì trước khi thêm feature hoặc sau khi lạc hướng.

Có thể gọi toàn bộ hoặc chỉ định phạm vi:

- `/explain` — toàn bộ hệ thống
- `/explain core/algorithms/` — chỉ một thư mục
- `/explain hapso.py` — chỉ một file
- `/explain flow: chạy thuật toán` — chỉ một luồng cụ thể

---

## Quy trình

### Bước 1 — Đọc context

Đọc `CLAUDE.md` để nắm kiến trúc tổng thể trước khi đọc code.

### Bước 2 — Duyệt code thực tế

Đọc từng file trong phạm vi được chỉ định.
Không đoán — chỉ mô tả những gì thực sự có trong code.

### Bước 3 — Tổng hợp theo 4 góc nhìn

**Thành phần**: Hệ thống gồm những module nào, mỗi module chứa gì.

**Chức năng**: Mỗi class/module làm được gì — mô tả theo hành vi, không theo code.

**Luồng hoạt động**: Dữ liệu đi từ đâu đến đâu khi người dùng thực hiện một tác vụ cụ thể.
Ví dụ: người dùng nhấn Run → AppState → Planner → PathResult → Renderer.

**Điểm kết nối**: Các module phụ thuộc nhau như thế nào, dependency quan trọng nào cần biết khi sửa.

---

## Output

Viết bằng văn xuôi, rõ ràng, không dùng jargon kỹ thuật thừa.
Độ dài tùy phạm vi — đủ để người đọc hiểu mà không cần mở code.

Kết thúc bằng:
**Điểm cần lưu ý khi thay đổi** — những chỗ dễ gây ảnh hưởng ngoài ý muốn nếu sửa.
