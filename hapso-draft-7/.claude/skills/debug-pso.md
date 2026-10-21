# Skill: Debug PSO

## Kích hoạt khi
Nhận thấy vấn đề liên quan đến PSO không hoạt động đúng.
Ví dụ: "PSO không hội tụ", "path ra toàn None", "particle bị kẹt", "kết quả tệ hơn A*".

## Quy trình

### Bước 1 — Phân loại triệu chứng

| Triệu chứng | Nghi vấn đầu tiên |
|-------------|-------------------|
| Luôn trả về `None` | Fitness function hoặc collision check sai |
| Path có collision | `_segment_collision_count` không đúng |
| Không cải thiện sau nhiều iter | Inertia weight quá cao hoặc `c1`/`c2` mất cân bằng |
| Path dài hơn A* nhiều | Fitness function chưa penalize độ dài đúng |
| Chạy cực chậm | Vòng lặp O(n²) không cần thiết trong fitness |

### Bước 2 — Kiểm tra có hệ thống
Theo thứ tự từ ngoài vào trong:

1. `find_path()` — có xử lý edge case start == goal không?
2. `_run_optimizer()` — vòng lặp có đúng `range(t_max)` không?
3. `_fitness()` — công thức có phản ánh đúng mục tiêu không?
4. `_segment_collision_count()` — có đếm đúng số collision không?

### Bước 3 — Thêm print debug tạm thời
Thêm print theo format chuẩn, ghi rõ iteration và giá trị:
```python
print("[PSO]: iter", k, "best_fitness=", best_fitness)
print("[PSO]: particle", i, "path_len=", len(path), "collisions=", col)
```
Xóa toàn bộ print debug sau khi fix xong.

### Bước 4 — Fix
- Chỉ sửa đúng phần gây lỗi.
- Không thay đổi default params trong `__init__`.
- Không dùng try/except — xử lý bằng điều kiện if.

### Bước 5 — Output
- Mô tả rõ: nguyên nhân gốc rễ là gì.
- Diff trước/sau của phần được sửa.
- Cách xác nhận đã fix: chạy case nào để kiểm tra.
