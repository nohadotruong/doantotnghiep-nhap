from __future__ import (
    annotations,
)  # Cho phép dùng kiểu annotation như str trước khi định nghĩa

# Import các hằng số cấu hình liên quan đến đánh giá đường đi
from config.parameter import (
    COLLISION_PENALTY,  # Giá trị phạt tối đa khi đường đi xuyên qua chướng ngại vật
    DANGER_CLEARANCE,  # Khoảng cách nguy hiểm: nhỏ hơn mức này bị phạt collision
    MARGIN_CELL,  # Số ô mở rộng khi tìm chướng ngại vật gần đoạn thẳng
    MIN_CLEARANCE,  # Khoảng cách an toàn: nhỏ hơn mức này bị phạt safety
    ROUND_NUM,  # Số chữ số thập phân khi làm tròn tọa độ
    SAFETY_PENALTY,  # Giá trị phạt khi đường đi quá gần chướng ngại vật
)
from datetime import datetime  # Lấy thời gian hiện tại khi lưu kết quả
from grid_map import GridMap  # Lớp bản đồ lưới
from math import atan2, ceil, degrees, floor, sqrt  # Các hàm toán học cần thiết
from openpyxl import Workbook  # Tạo và lưu file Excel (.xlsx)
from pathlib import Path  # Làm việc với đường dẫn file hệ thống
from statistics import median, stdev  # Tính trung vị và độ lệch chuẩn
from typing import Optional  # Kiểu dữ liệu có thể là None

import json  # Đọc/ghi file JSON
import matplotlib  # Thư viện vẽ đồ thị

matplotlib.use("Agg")  # Dùng backend Agg (không cần màn hình GUI) để render ảnh
import matplotlib.pyplot as plt  # Giao diện vẽ đồ thị

# ─────────────────────────────────────────────
#  NHÓM 1: CÁC HÀM TOÁN HỌC CƠ BẢN
# ─────────────────────────────────────────────


def round_pos(
    point: tuple[float, float], round_num: int = ROUND_NUM
) -> tuple[float, float]:
    """Làm tròn tọa độ điểm (x, y) đến `round_num` chữ số thập phân."""
    return (round(point[0], round_num), round(point[1], round_num))


def euclidean_distance(
    start_point: tuple[float, float], end_point: tuple[float, float]
) -> float:
    """Tính khoảng cách Euclid giữa hai điểm 2D."""
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]

    return sqrt(dx * dx + dy * dy)


def count_waypoints(path: list[tuple[float, float]]) -> int:
    """Đếm số lượng waypoint trong đường đi. Trả về 0 nếu đường đi rỗng."""
    return len(path) if path else 0


def turning_angle(
    prev_point: tuple[float, float],
    curr_point: tuple[float, float],
    next_point: tuple[float, float],
) -> float:
    """
    Tính góc quay (độ) tại điểm curr_point khi đi từ prev_point → curr_point → next_point.
    Sử dụng tích có hướng (cross product) và tích vô hướng (dot product) của 2 vector kề nhau.
    Trả về góc tuyệt đối trong khoảng [0°, 180°].
    """
    v1 = (
        curr_point[0] - prev_point[0],
        curr_point[1] - prev_point[1],
    )  # Vector đoạn trước
    v2 = (
        next_point[0] - curr_point[0],
        next_point[1] - curr_point[1],
    )  # Vector đoạn sau

    dot = v1[0] * v2[0] + v1[1] * v2[1]  # Tích vô hướng
    cross = v1[0] * v2[1] - v1[1] * v2[0]  # Tích có hướng (độ lớn)

    return abs(degrees(atan2(cross, dot)))  # Góc giữa 2 vector (độ tuyệt đối)


# ─────────────────────────────────────────────
#  NHÓM 2: KHOẢNG CÁCH TỪ ĐOẠN THẲNG ĐẾN CHƯỚNG NGẠI VẬT
# ─────────────────────────────────────────────


def distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle: tuple[float, float],
) -> float:
    """
    Tính khoảng cách nhỏ nhất từ một điểm obstacle đến đoạn thẳng [start_point, end_point].
    Tọa độ được dịch chuyển +0.5 để lấy tâm ô thay vì góc ô.
    """
    # Lấy tọa độ tâm của các ô (cộng 0.5 vì mỗi ô có kích thước 1×1)
    sx, sy = start_point[0] + 0.5, start_point[1] + 0.5
    ex, ey = end_point[0] + 0.5, end_point[1] + 0.5
    ox, oy = obstacle[0] + 0.5, obstacle[1] + 0.5

    dx = ex - sx  # Hiệu x của đoạn thẳng
    dy = ey - sy  # Hiệu y của đoạn thẳng

    # Nếu đoạn thẳng suy biến thành điểm → tính khoảng cách điểm-điểm
    if dx == 0 and dy == 0:
        return euclidean_distance((ox, oy), (sx, sy))

    # Tính tham số t là vị trí hình chiếu của obstacle lên đoạn thẳng (clamped [0, 1])
    t = ((ox - sx) * dx + (oy - sy) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    # Tính điểm gần nhất trên đoạn thẳng
    nearest_x = sx + t * dx
    nearest_y = sy + t * dy

    return euclidean_distance((ox, oy), (nearest_x, nearest_y))


def get_nearby_obstacles(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle_set: set[tuple[int, int]],
    margin_cells: int = MARGIN_CELL,
) -> list[tuple[float, float]]:
    """
    Lấy danh sách chướng ngại vật nằm gần đoạn thẳng [start_point, end_point].
    Tạo bounding box xung quanh đoạn thẳng với biên mở rộng `margin_cells`,
    rồi lọc các ô trong obstacle_set nằm trong bounding box đó.
    Giúp tránh duyệt toàn bộ bản đồ khi tính khoảng cách.
    """
    # Dịch tọa độ về tâm ô
    sx, sy = start_point[0] + 0.5, start_point[1] + 0.5
    ex, ey = end_point[0] + 0.5, end_point[1] + 0.5

    # Tính bounding box có mở rộng margin_cells về mỗi phía
    min_x = ceil(min(sx, ex) - margin_cells)
    max_x = floor(max(sx, ex) + margin_cells)
    min_y = ceil(min(sy, ey) - margin_cells)
    max_y = floor(max(sy, ey) + margin_cells)

    # Trả về các ô chướng ngại vật nằm trong bounding box
    return [
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) in obstacle_set
    ]


def min_distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    grid_map: GridMap,
) -> float:
    """
    Tính khoảng cách nhỏ nhất từ đoạn thẳng [start_point, end_point]
    đến bất kỳ chướng ngại vật nào trên bản đồ.
    Dùng get_nearby_obstacles để chỉ xét các ô gần đoạn thẳng (tối ưu hiệu suất).
    """
    nearby = get_nearby_obstacles(start_point, end_point, grid_map.get_obstacle_set())

    # Khởi tạo min_dist = kích thước bản đồ (giá trị rất lớn)
    min_dist = float(grid_map.height * grid_map.width)

    for obs in nearby:
        d = distance_line_to_obstacle(start_point, end_point, obs)
        if d < min_dist:
            min_dist = d

    return min_dist


def min_distance_path_to_obstacle(
    path: list[tuple[float, float]], grid_map: GridMap
) -> float:
    """
    Tính khoảng cách nhỏ nhất từ toàn bộ đường đi đến chướng ngại vật.
    Xét từng đoạn liên tiếp trong đường đi và lấy min của tất cả.
    """
    if not path or len(path) < 2:
        return 10000.0  # Đường đi không đủ điểm → trả về giá trị rất lớn (an toàn)

    return min(
        min_distance_line_to_obstacle(path[i], path[i + 1], grid_map)
        for i in range(len(path) - 1)
    )


# ─────────────────────────────────────────────
#  NHÓM 3: TÍNH ĐỘ DÀI VÀ GÓC QUAY ĐƯỜNG ĐI
# ─────────────────────────────────────────────


def compute_path_length(path: list[tuple[float, float]]) -> float:
    """Tính tổng độ dài đường đi (tổng khoảng cách Euclid các đoạn liên tiếp)."""
    if not path or len(path) < 2:
        return 0.0

    return sum(euclidean_distance(path[i], path[i + 1]) for i in range(len(path) - 1))


def compute_total_angle(path: list[tuple[float, float]]) -> float:
    """Tính tổng góc quay của toàn bộ đường đi (tổng góc tại tất cả điểm trung gian)."""
    if not path or len(path) < 3:
        return 0.0

    return sum(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_min_angle(path: list[tuple[float, float]]) -> float:
    """Tính góc quay nhỏ nhất trong đường đi."""
    if not path or len(path) < 3:
        return 0.0

    return min(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_max_angle(path: list[tuple[float, float]]) -> float:
    """Tính góc quay lớn nhất trong đường đi."""
    if not path or len(path) < 3:
        return 0.0

    return max(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_avg_angle(path: list[tuple[float, float]]) -> float:
    """Tính góc quay trung bình tại các điểm trung gian của đường đi."""
    if not path or len(path) < 3:
        return 0.0

    return compute_total_angle(path) / (len(path) - 2)


# ─────────────────────────────────────────────
#  NHÓM 4: HÀM FITNESS (ĐÁNH GIÁ ĐƯỜNG ĐI)
# ─────────────────────────────────────────────


def compute_fitness(
    path: list[tuple[float, float]],
    grid_map: GridMap,
    danger_clearance: float = DANGER_CLEARANCE,
    min_clearance: float = MIN_CLEARANCE,
    collision_penalty: float = COLLISION_PENALTY,
    safety_penalty: float = SAFETY_PENALTY,
    reference_metrics: dict | None = None,
) -> float:
    """
    Tính giá trị hàm đánh giá (fitness) của một đường đi.
    Fitness càng thấp → đường đi càng tốt.

    Các thành phần đánh giá:
    - Nếu khoảng cách tới chướng ngại vật < danger_clearance → trả về collision_penalty (tệ nhất)
    - Nếu khoảng cách < min_clearance → trả về safety_penalty (không an toàn)
    - Ngược lại: tính tổ hợp có trọng số của: độ dài, góc trung bình, góc lớn nhất, khoảng hở

    Trọng số mặc định: 30% độ dài + 30% góc TB + 10% góc max + 30% khoảng hở
    """
    total_dist = compute_path_length(path)  # Độ dài tổng
    avg_angle = compute_avg_angle(path)  # Góc quay trung bình
    max_angle = compute_max_angle(path)  # Góc quay lớn nhất
    min_dist = min_distance_path_to_obstacle(
        path, grid_map
    )  # Khoảng cách tối thiểu tới chướng ngại vật

    # Phạt va chạm: đường đi quá gần hoặc xuyên qua chướng ngại vật
    if min_dist < danger_clearance:
        return collision_penalty

    # Phạt an toàn: đường đi gần chướng ngại vật hơn ngưỡng tối thiểu cho phép
    elif min_dist < min_clearance:
        return safety_penalty

    if reference_metrics is not None:
        # Chuẩn hóa theo metrics tham chiếu (từ đường đi A* hoặc đường chuẩn)
        norm_dist = total_dist / (reference_metrics.get("distance", 1.0) + 1e-6)
        norm_avg_angle = avg_angle / (reference_metrics.get("avg_angle", 1.0) + 1e-6)
        norm_max_angle = max_angle / (reference_metrics.get("max_angle", 1.0) + 1e-6)
        norm_clearance = (1.0 / (min_dist + 1e-6)) / (
            reference_metrics.get("clearance", 1.0) + 1e-6
        )
    else:
        # Chuẩn hóa theo kích thước bản đồ (không có tham chiếu)
        grid_diag = euclidean_distance(
            (0, 0), (grid_map.width, grid_map.height)
        )  # Đường chéo bản đồ
        norm_dist = total_dist / (grid_diag + 1e-6)  # Chuẩn hóa độ dài
        norm_avg_angle = avg_angle / 180.0  # Chuẩn hóa về [0, 1]
        norm_max_angle = max_angle / 180.0  # Chuẩn hóa về [0, 1]
        norm_clearance = (
            1.0 / (min_dist + 1e-6)
        ) * min_clearance  # Nghịch đảo khoảng hở

    # Tổ hợp có trọng số: 30% độ dài + 30% góc TB + 10% góc max + 30% khoảng hở
    return (
        0.3 * norm_dist
        + 0.3 * norm_avg_angle
        + 0.1 * norm_max_angle
        + 0.3 * norm_clearance
    )


def total_fitness(
    path: list[tuple[float, float]],
    grid_map: GridMap,
    reference_metrics: dict | None = None,
) -> float:
    """Alias của compute_fitness — dùng để gọi từ nơi khác với tên rõ ràng hơn."""
    return compute_fitness(
        path=path, grid_map=grid_map, reference_metrics=reference_metrics
    )


# ─────────────────────────────────────────────
#  NHÓM 5: CÁC HÀM ALIAS (tên rõ nghĩa hơn)
# ─────────────────────────────────────────────


def get_nearby_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle_set: set[tuple[int, int]],
    margin_cells: int = MARGIN_CELL,
) -> list[tuple[float, float]]:
    """Alias của get_nearby_obstacles (tên số ít, dùng tương đương)."""
    return get_nearby_obstacles(start_point, end_point, obstacle_set, margin_cells)


def total_path_length(path: list[tuple[float, float]]) -> float:
    """Alias của compute_path_length."""
    return compute_path_length(path)


def total_turning_angle(path: list[tuple[float, float]]) -> float:
    """Alias của compute_total_angle."""
    return compute_total_angle(path)


def min_turning_angle(path: list[tuple[float, float]]) -> float:
    """Alias của compute_min_angle."""
    return compute_min_angle(path)


def max_turning_angle(path: list[tuple[float, float]]) -> float:
    """Alias của compute_max_angle."""
    return compute_max_angle(path)


def average_turning_angle(path: list[tuple[float, float]]) -> float:
    """Alias của compute_avg_angle."""
    return compute_avg_angle(path)


def waypoint_count(path: list[tuple[float, float]]) -> int:
    """Alias của count_waypoints."""
    return count_waypoints(path)


# ─────────────────────────────────────────────
#  NHÓM 6: TÍNH VÀ IN METRICS ĐƯỜNG ĐI
# ─────────────────────────────────────────────


def compute_path_metrics(
    path: list[tuple[float, float]],
    algorithm_name: str,
    grid_map: GridMap,
    danger_clearance: float = DANGER_CLEARANCE,
    reference_metrics: dict | None = None,
) -> dict:
    """
    Tính đầy đủ các chỉ số đánh giá đường đi, trả về dict với key là tên thuật toán.
    Nếu đường đi không hợp lệ (rỗng hoặc không an toàn), trả về dict toàn None.
    """
    min_dist = min_distance_path_to_obstacle(path, grid_map)

    # Đường đi hợp lệ khi: không rỗng và khoảng cách tới chướng ngại vật > danger_clearance
    is_successful = bool(path) and min_dist > danger_clearance

    if not is_successful:
        # Trả về dict với tất cả giá trị None
        return {
            algorithm_name: {
                "Result": False,
                "Total distance": None,
                "Total waypoint": None,
                "Total angle": None,
                "Min angle": None,
                "Max angle": None,
                "Average angle": None,
                "Min clearance": None,
                "TOTAL FITNESS": None,
            }
        }

    # Trả về dict với đầy đủ chỉ số
    return {
        algorithm_name: {
            "Result": True,
            "Total distance": compute_path_length(path),
            "Total waypoint": len(path),
            "Total angle": compute_total_angle(path),
            "Min angle": compute_min_angle(path),
            "Max angle": compute_max_angle(path),
            "Average angle": compute_avg_angle(path),
            "Min clearance": min_dist,
            "TOTAL FITNESS": compute_fitness(
                path=path,
                grid_map=grid_map,
                reference_metrics=reference_metrics,
            ),
        }
    }


def _fmt(val):
    """
    Hàm định dạng giá trị để in ra console:
    - None → 'N/A'
    - bool → 'SUCCESS' hoặc 'FAILED'
    - float → 4 chữ số thập phân
    - Khác → chuỗi thông thường
    """
    if val is None:
        return "N/A"

    if isinstance(val, bool):
        return "SUCCESS" if val else "FAILED"

    if isinstance(val, float):
        return f"{val:.4f}"

    return str(val)


def print_path_metrics(
    path_metrics: dict,
    *,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    path: list[tuple[float, float]] | None = None,
) -> None:
    """In báo cáo metrics đường đi của một thuật toán ra console."""
    algo = next(iter(path_metrics))  # Lấy tên thuật toán (key đầu tiên)
    metrics = path_metrics[algo]  # Lấy dict metrics tương ứng

    print("=" * 120)
    print("[ALGORITHM] ALGORITHM REPORT")
    print("=" * 120)
    print(f"{'Algorithm':<16}: {algo}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {start_time}")
    print(f"{'End time':<16}: {end_time}")
    print(f"{'Result':<16}: {metrics.get('Result')}")
    print("-" * 120)
    print("FITNESS / PATH METRICS:")

    # In từng chỉ số quan trọng
    _print_metric_row("Result", metrics.get("Result"))
    _print_metric_row("Total distance", metrics.get("Total distance"))
    _print_metric_row("Average angle", metrics.get("Average angle"))
    _print_metric_row("Min clearance", metrics.get("Min clearance"))
    _print_metric_row("Execution time", metrics.get("Execution time"))
    _print_metric_row("TOTAL FITNESS", metrics.get("TOTAL FITNESS"))

    print("=" * 120)


def _print_metric_row(key: str, val) -> None:
    """In một dòng metric theo định dạng cố định: key (16 ký tự) : giá trị."""
    print(f"{key:<16}: {_fmt(val)}")


def print_all_path_metrics(
    all_path_metrics: dict,
    all_paths: dict,
    *,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    algo_start_times: dict | None = None,
    algo_end_times: dict | None = None,
) -> None:
    """
    In bảng so sánh metrics của nhiều thuật toán cùng lúc (dạng bảng ngang).
    Mỗi cột là một thuật toán, mỗi hàng là một chỉ số.
    """
    algos = list(all_path_metrics.keys())  # Danh sách tên các thuật toán
    algo_start_times = algo_start_times or {}
    algo_end_times = algo_end_times or {}

    col = 14  # Độ rộng mỗi cột thuật toán

    def row(key: str, getter) -> None:
        """In một hàng trong bảng: key + giá trị của từng thuật toán."""
        line = f"{key:<{16}}"

        for a in algos:
            val = getter(a)
            line += f"| {_fmt(val):<{col}}"

        print(line)

    print("=" * 120)
    print("[ALGORITHM ALL] ALL ALGORITHM REPORT")
    print("=" * 120)
    print(f"{'Algorithms':<16}: {', '.join(algos)}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {start_time}")
    print(f"{'End time':<16}: {end_time}")
    print("-" * 120)
    print("[ALGORITHM ALL] FITNESS / PATH METRICS:")

    # In header bảng
    header = f"{'Metrics':<{16}}"
    for a in algos:
        header += f"| {a:<{col}}"
    print(header)
    print("-" * 120)

    # In các hàng metrics chính
    for metric_key in ("Result", "Total distance", "Average angle", "Min clearance"):
        row(metric_key, lambda a, k=metric_key: all_path_metrics[a].get(k))

    # In thời gian bắt đầu/kết thúc (chỉ lấy phần giờ HH:MM:SS)
    row("Start time", lambda a: algo_start_times.get(a, "N/A").split()[1])
    row("End time", lambda a: algo_end_times.get(a, "N/A").split()[1])
    row("Execution time", lambda a: all_path_metrics[a].get("Execution time"))
    row("TOTAL FITNESS", lambda a: all_path_metrics[a].get("TOTAL FITNESS"))

    print("=" * 120)


def print_batch_summary_report(
    algo_name: str,
    map_name: str,
    batch_start_time: str,
    batch_end_time: str,
    run_count: int,
    successful_runs: int,
    total_time: float,
    excel_path: str,
    best_run: dict | None,
    run_records: list[dict],
) -> None:
    """
    In báo cáo tổng kết sau khi chạy batch test.
    Hiển thị thống kê (best, worst, mean, median, std dev) cho từng chỉ số.
    """

    def _series(key):
        """Lấy danh sách giá trị của một chỉ số từ tất cả run thành công."""
        return [
            r[key]
            for r in run_records
            if r.get("Found_Path") and r.get(key) is not None
        ]

    # Thu thập chuỗi dữ liệu cho từng chỉ số
    dist_vals = _series("Total_Distance")
    angle_vals = _series("Average_Angle")
    clear_vals = _series("Min_Clearance")
    time_vals = _series("Execution_Time_s")
    fit_vals = _series("TOTAL_FITNESS")

    def _stats(vals: list[float], higher_is_better: bool = False) -> tuple:
        """
        Tính thống kê (best, worst, mean, median, std dev) từ danh sách giá trị.
        higher_is_better=True: giá trị lớn hơn là tốt hơn (ví dụ: khoảng hở an toàn).
        """
        if not vals:
            return ("-", "-", "-", "-", "-")

        best_v = max(vals) if higher_is_better else min(vals)  # Giá trị tốt nhất
        worst_v = min(vals) if higher_is_better else max(vals)  # Giá trị tệ nhất
        mean_v = sum(vals) / len(vals)  # Trung bình
        med_v = median(vals)  # Trung vị
        std_v = stdev(vals) if len(vals) > 1 else 0.0  # Độ lệch chuẩn

        return (best_v, worst_v, mean_v, med_v, std_v)

    failed_runs = run_count - successful_runs  # Số lần thất bại

    # Hàng thống kê cho chỉ số Result (thành công/thất bại)
    result_stats = (
        f"{successful_runs} OK",
        f"{failed_runs} FAIL",
        "-",
        "-",
        "-",
    )

    col = 14  # Độ rộng cột

    def _stat_row(key: str, stats: tuple) -> None:
        """In một hàng thống kê (best, worst, mean, median, std) cho một chỉ số."""
        best_v, worst_v, mean_v, med_v, std_v = stats
        line = f"{key:<{16}}"

        for v in (best_v, worst_v, mean_v, med_v, std_v):
            line += f"| {_fmt(v):<{col}}"
        print(line)

    print("=" * 120)
    print("[BATCH] RESULTS:")
    print(f"[BATCH] Algorithm   : {algo_name}")
    print(f"[BATCH] Map         : {map_name}")
    print(f"[BATCH] Total runs  : {run_count}")
    print(f"[BATCH] Successful  : {successful_runs}/{run_count}")
    print(f"[BATCH] Start time  : {batch_start_time}")
    print(f"[BATCH] End time    : {batch_end_time}")
    print(f"[BATCH] Total time  : {total_time:.4f}s")
    print(f"[BATCH] Excel       : {excel_path}")

    if best_run:
        fitness = _fmt(best_run["TOTAL_FITNESS"])
        print(f"[BATCH] Best run    : {best_run['Run_ID']} | Fitness = {fitness}")

    print("-" * 120)

    # In header bảng thống kê
    header = f"{'Metrics':<{16}}"
    for col_name in ("Best", "Worst", "Mean", "Median", "Std Dev"):
        header += f"| {col_name:<{col}}"
    print(header)
    print("-" * 120)

    # In từng hàng thống kê
    _stat_row("Result", result_stats)
    _stat_row("Total distance", _stats(dist_vals))
    _stat_row("Average angle", _stats(angle_vals))
    _stat_row("Min clearance", _stats(clear_vals, higher_is_better=True))
    _stat_row("Execution time", _stats(time_vals))
    _stat_row("TOTAL FITNESS", _stats(fit_vals))

    print("=" * 120)


def print_batch_header(
    algo_name: str,
    map_name: str,
    batch_start_time: str,
    run_count: int,
) -> None:
    """In header (tiêu đề) trước khi bắt đầu batch test."""
    print("=" * 120)
    print("[BATCH] ALGORITHM BATCH TEST REPORT")
    print("=" * 120)
    print(f"{'Algorithm':<16}: {algo_name}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {batch_start_time}")
    print(f"{'Total runs':<16}: {run_count}")
    print("=" * 120)


# ─────────────────────────────────────────────
#  NHÓM 7: LƯU KẾT QUẢ RA FILE
# ─────────────────────────────────────────────


def save_run_results(
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    base_dir: str = "data/results/simulation",
) -> Path:
    """
    Lưu kết quả một lần chạy thuật toán vào thư mục riêng.
    Tạo thư mục theo format: base_dir/<algo_name>_<timestamp>/
    Lưu 2 file: path.json (đường đi) và metrics.xlsx (bảng chỉ số).
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Timestamp để đặt tên thư mục
    safe_name = _safe(algorithm_name)  # Tên thuật toán (đã lọc ký tự đặc biệt)

    run_dir = Path(base_dir) / f"{safe_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)  # Tạo thư mục (kể cả thư mục cha)

    # Lưu đường đi và metrics ra file JSON
    _save_path_json(
        run_dir, algorithm_name, path, metrics, map_name, start_time, end_time
    )
    # Lưu metrics ra file Excel
    _save_metrics_xlsx(
        run_dir, algorithm_name, path, metrics, map_name, start_time, end_time
    )

    return run_dir  # Trả về đường dẫn thư mục đã lưu


def _safe(name: str) -> str:
    """Chuyển tên thành chuỗi an toàn cho tên file: chỉ giữ chữ số, chữ cái, dấu gạch dưới."""
    return "".join(c if (c.isalnum() or c == "_") else "_" for c in name)


def _save_path_json(
    run_dir: Path,
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    map_name: str,
    start_time: str,
    end_time: str,
) -> None:
    """Lưu thông tin đường đi và metrics ra file path.json trong thư mục run_dir."""
    payload = {
        "algorithm": algorithm_name,
        "map": map_name,
        "start_time": start_time,
        "end_time": end_time,
        "success": metrics["Result"],  # Kết quả: thành công hay thất bại
        "waypoint_count": len(path) if path else 0,  # Số waypoint
        "path": [list(p) for p in path] if path else [],  # Đường đi (list of [x, y])
        "metrics": {
            # Làm tròn float đến 4 chữ số, giữ nguyên các kiểu khác
            k: (v if not isinstance(v, float) else round(v, 4))
            for k, v in metrics.items()
        },
    }

    out = run_dir / "path.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _save_metrics_xlsx(
    run_dir: Path,
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    map_name: str,
    start_time: str,
    end_time: str,
) -> None:
    """Lưu metrics ra file Excel metrics.xlsx trong thư mục run_dir."""
    wb = Workbook()  # Tạo workbook mới

    ws_sum = wb.active  # Lấy sheet đầu tiên (mặc định)
    ws_sum.title = "Summary"  # Đặt tên sheet
    ws_sum.append(["Field", "Value"])  # Hàng header

    # Ghi thông tin cơ bản
    for row in [
        ("Algorithm", algorithm_name),
        ("Map", map_name),
        ("Start time", start_time),
        ("End time", end_time),
        ("Result", "SUCCESS" if path else "FAILED"),
        ("Waypoint count", len(path) if path else 0),
    ]:
        ws_sum.append(list(row))

    ws_sum.append([])  # Dòng trống ngăn cách

    ws_sum.append(["Metric", "Value"])  # Header cho phần metrics

    # Ghi từng chỉ số metrics (làm tròn float)
    for k, v in metrics.items():
        ws_sum.append([k, round(v, 4) if isinstance(v, float) else v])

    wb.save(run_dir / "metrics.xlsx")  # Lưu file Excel
