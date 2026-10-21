# /fix

Sửa bug hoặc lỗi được chỉ định, tuân thủ đúng rules của dự án.

## Đầu vào

Mô tả bug sau lệnh. Ví dụ: `/fix path trả về None khi start == goal`

## Quy trình

1. Xác định file và method liên quan.
2. Đọc `rules/error-handling.md` — không dùng try/except, không raise, chỉ dùng print().
3. Đọc `rules/class-design.md` — không thay đổi default params trong __init__.
4. Chỉ sửa đúng phần gây ra bug — không refactor code xung quanh.
5. Nếu cần in thông báo lỗi: đúng format `print("[CLASS]: Warning/Error — mô tả")`.

## Output

- Hiển thị diff trước / sau của từng đoạn thay đổi.
- Giải thích ngắn: nguyên nhân bug và cách fix.
- Nếu fix có thể gây ảnh hưởng chỗ khác → cảnh báo rõ.
