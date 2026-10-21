# Skill: Benchmark Algorithms

## Kích hoạt khi
Nhận thấy yêu cầu so sánh hiệu năng giữa các thuật toán.
Ví dụ: "so sánh A* và HAPSO", "benchmark path length", "thuật toán nào nhanh hơn".

## Quy trình

### Bước 1 — Xác định metrics cần đo
Hỏi hoặc suy ra từ context:
- **Path length** — tổng độ dài đường đi.
- **Execution time** — thời gian chạy (ms).
- **Iterations** — số vòng lặp đến khi hội tụ (chỉ áp dụng PSO-based).
- **Success rate** — tỉ lệ tìm được path trên nhiều map.

### Bước 2 — Xác định điều kiện test
- Cùng map, cùng start/goal cho tất cả thuật toán.
- Nếu có random (PSO): chạy nhiều lần, lấy trung bình.
- Ghi rõ: grid size, obstacle density, số lần chạy.

### Bước 3 — Viết benchmark script
- File: `benchmark.py` ở root hoặc `analytics/`.
- Không sửa code của các planner — chỉ gọi `find_path()`.
- Dùng `time.perf_counter()` cho execution time.
- Kết quả lưu vào dict, in ra terminal theo format chuẩn:
```python
print("[BENCHMARK]: A* | length=42.3 | time=1.2ms")
print("[BENCHMARK]: HAPSO | length=39.1 | time=84.5ms | iter=120")
```

### Bước 4 — Output
- Bảng so sánh rõ ràng các metrics.
- Nhận xét ngắn: thuật toán nào tốt hơn ở metric nào và trong điều kiện nào.
- Không kết luận "thuật toán X tốt hơn" nếu chưa đủ dữ liệu.
