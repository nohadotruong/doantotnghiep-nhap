# Skill: File Safety

## Kích hoạt khi
Nhận thấy yêu cầu xóa file, thay thế file, hoặc thay đổi lớn trên nhiều file cùng lúc.
Ví dụ: "xóa file này", "viết lại toàn bộ", "remove class cũ", "dọn dẹp thư mục".

---

## Quy tắc bắt buộc

### Trước khi sửa file
- Hook `PreToolUse` tự động backup — không cần làm thủ công.
- Backup lưu tại: `.claude/backups/YYYY-MM-DD/HH-MM-SS_<tên_file>`

### Khi cần xóa file
- **Không dùng `rm`** — hook sẽ chặn và chuyển vào trash tự động.
- File xóa lưu tại: `.claude/trash/YYYY-MM-DD/HH-MM-SS_<tên_file>`
- Nếu cần thông báo: `print("[FILE_SAFETY]: Moved <file> to trash.")`

### Khi thay đổi lớn (refactor toàn file, đổi tên class)
Trước khi bắt đầu, thông báo rõ:
```
[FILE_SAFETY]: Chuẩn bị thay đổi lớn trên <file>.
Backup sẽ được lưu tự động trước mỗi lần ghi.
```

---

## Cấu trúc lưu trữ

```
.claude/
├── backups/
│   └── 2025-01-15/
│       ├── 14-32-01_src__algorithms__hapso.py   ← bản gốc trước khi sửa
│       └── 15-10-44_src__map__grid_map.py
└── trash/
    └── 2025-01-15/
        └── 09-05-22_src__utils__old_helper.py   ← file đã "xóa"
```

---

## Khôi phục file

Khi cần khôi phục, tìm trong `.claude/backups/` hoặc `.claude/trash/` theo ngày và giờ.
Tên file đã được flatten: `__` tương đương `/` trong path gốc.

Ví dụ: `14-32-01_src__algorithms__hapso.py` → file gốc là `src/algorithms/hapso.py` lúc 14:32:01.
