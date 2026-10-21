"""
visualization.py
Vẽ các biểu đồ phục vụ luận văn / báo cáo về thuật toán HAPSO trong bài toán lập kế hoạch
đường đi robot. Mỗi hàm tạo ra một file ảnh (.png) và lưu vào thư mục tương ứng.
"""

from __future__ import (
    annotations,
)  # Cho phép dùng kiểu chú thích dạng chuỗi (Python ≥ 3.7)

# ── Import các hằng màu sắc / họa tiết dùng cho biểu đồ ────────────────────────
from config.colors import (
    CHART_COLORS,  # Danh sách màu lần lượt cho từng cột/thuật toán
    CHART_HATCHES,  # Danh sách họa tiết (gạch chéo, chấm, ...) cho từng cột
    DARK_GRAY,  # Màu xám đậm — dùng cho điểm đặc biệt
    CHART_BLUE,  # Màu xanh dương
    CHART_ORANGE,  # Màu cam
    CHART_GREEN,  # Màu xanh lá
    CHART_DARK_GREEN,  # Màu xanh lá đậm
    CHART_MAGENTA,  # Màu hồng tím
    CHART_PURPLE,  # Màu tím
    CHART_GOLD,  # Màu vàng gold
    HEX_MEDIUM,  # Màu trung tính (dùng cho đường viền vùng SOBL)
)
from typing import Dict, List, Optional, Tuple  # Kiểu dữ liệu tường minh cho type hints

import datetime  # Lấy thời gian hiện tại để đặt tên thư mục đầu ra
import matplotlib.pyplot as plt  # Thư viện vẽ biểu đồ chính
import matplotlib.patches as mpatches  # Vẽ các hình hộp, mũi tên, ... tuỳ chỉnh
import numpy as np  # Tính toán mảng số học
import os  # Thao tác hệ thống tệp (tạo thư mục, ghép đường dẫn)

# Đặt font chữ mặc định cho tất cả biểu đồ; ưu tiên DejaVu Sans, fallback về sans-serif
plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]

# ── Tên bản đồ đang chạy (dùng để đặt tên thư mục lưu kết quả) ─────────────────
MAP_NAME = "KB03-OD"

# ── Bảng số liệu so sánh 4 thuật toán (dạng TSV — tab-separated values) ─────────
# Mỗi hàng là một chỉ số đánh giá; mỗi cột (sau cột đầu) là một thuật toán.
# Giá trị "–" biểu thị thuật toán không tìm được đường đi (không hợp lệ).
COMPARISON_TABLE = """Thuật toán	RRT*	PRM	A*	HAPSO
Tỷ lệ thành công	100.0	10.0	100.0	100.0
Độ dài đường đi	53.1532	48.8074	49.3137	50.123
Góc quay trung bình	14.9267	42.3634	9	4.3502
Khoảng cách an toàn 	1.3097	0.7071	0.7071	1.1729
Thời gian tính toán	0.2157	0.2009	0.0021	1.1606
Hàm đánh giá	0.6695	5	5	0.634
"""

# ── Ánh xạ tên chỉ số (tiếng Việt) → tên file ảnh (tiếng Anh, không dấu) ────────
# Dùng để đặt tên file PNG khi lưu từng biểu đồ chỉ số riêng lẻ.
METRIC_FILENAME_MAP: Dict[str, str] = {
    "Tỷ lệ thành công": "success_rate",
    "Độ dài đường đi": "path_length",
    "Góc quay trung bình": "average_turning_angle",
    "Khoảng cách an toàn": "safety_clearance",
    "Thời gian tính toán": "computation_time",
    "Hàm đánh giá": "evaluation_function",
}


# ── Hàm tiện ích: lưu figure và đóng để giải phóng bộ nhớ ───────────────────────
def _save_fig(fig: plt.Figure, out_path: str) -> None:
    """Tạo thư mục nếu chưa có, lưu figure vào out_path, rồi đóng figure."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)  # Tạo thư mục cha nếu thiếu
    fig.savefig(out_path, bbox_inches="tight")  # Lưu, cắt sát nội dung
    plt.close(fig)  # Đóng figure tránh rò bộ nhớ


# ════════════════════════════════════════════════════════════════════════════════
# 1. Biểu đồ Trọng số Quán tính Ngẫu nhiên (Stochastic Inertia Weight — SIW)
# ════════════════════════════════════════════════════════════════════════════════
def plot_stochastic_inertia_weight(
    max_iterations: int = 50,  # Tổng số vòng lặp PSO
    weight_max: float = 0.9,  # Trọng số quán tính lớn nhất (đầu quá trình)
    weight_min: float = 0.4,  # Trọng số quán tính nhỏ nhất (cuối quá trình)
    noise_scale: float = 0.1,  # Biên độ nhiễu ngẫu nhiên ±5 % của linear_weight
    seed: int = 42,  # Seed để kết quả tái lập được
    out_path: str = "data/results/improved/stochastic_inertia.png",
    figsize: Tuple[float, float] = (8.0, 4.5),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    # Tạo mảng chỉ số vòng lặp 0, 1, 2, ..., max_iterations-1
    iterations = np.arange(max_iterations)

    # Giảm tuyến tính từ weight_max → weight_min theo số vòng lặp
    linear_weight = weight_max - (weight_max - weight_min) * iterations / max_iterations

    # Khởi tạo bộ sinh số ngẫu nhiên với seed cố định
    rng = np.random.default_rng(seed)

    # Thêm nhiễu ngẫu nhiên vào đường tuyến tính:
    #   rng.random() sinh giá trị [0, 1) → trừ 0.5 → phạm vi [-0.5, 0.5)
    #   nhân noise_scale → nhiễu nhỏ quanh 0
    stochastic_weight = linear_weight * (
        1 + noise_scale * (rng.random(max_iterations) - 0.5)
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(iterations, stochastic_weight, "b-", label="Giá trị trọng số quán tính")
    ax.set_xlabel("Vòng lặp (t)", fontsize=12)
    ax.set_ylabel("Trọng số quán tính (w)", fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, linestyle=grid_style)
    fig.tight_layout()  # Tự điều chỉnh lề cho vừa khít
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] SIW saved to '{out_path}'")


# ════════════════════════════════════════════════════════════════════════════════
# 2. Biểu đồ TVAC — Time-Varying Acceleration Coefficients
#    Minh hoạ sự thay đổi hành vi đàn cá thể: khám phá (đầu) → khai thác (cuối)
# ════════════════════════════════════════════════════════════════════════════════
def plot_tvac(
    particle_count: int = 40,  # Số cá thể trong đàn
    space_min_value: float = 0.0,  # Giới hạn dưới không gian tìm kiếm
    space_max_value: float = 100.0,  # Giới hạn trên không gian tìm kiếm
    global_best: Tuple[float, float] = (50.0, 50.0),  # Vị trí tối ưu toàn cục (Gbest)
    seed: int = 10,
    out_path: str = "data/results/improved/tvac.png",
    figsize: Tuple[float, float] = (11.0, 4.8),
    dpi: int = 150,
) -> None:
    rng = np.random.default_rng(seed)
    gbx, gby = global_best  # Tọa độ Gbest

    # Giai đoạn đầu: cá thể phân tán rộng (khám phá toàn cục)
    early_x = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)
    early_y = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)

    # Giai đoạn cuối: cá thể tập trung quanh Gbest (khai thác cục bộ)
    late_x = rng.normal(gbx, 4, particle_count)  # Phân phối chuẩn xung quanh gbx
    late_y = rng.normal(gby, 4, particle_count)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)

    # ── Subplot trái: giai đoạn đầu ──────────────────────────────────────────
    ax1.quiver(
        early_x,
        early_y,  # Gốc mũi tên
        rng.uniform(-15, 15, particle_count),  # Thành phần vận tốc X (ngẫu nhiên)
        rng.uniform(-15, 15, particle_count),  # Thành phần vận tốc Y (ngẫu nhiên)
        color=CHART_GREEN,
        alpha=0.7,
    )
    ax1.scatter(early_x, early_y, color=CHART_DARK_GREEN, s=100, label="Cá thể")
    ax1.set_title("Giai đoạn đầu", fontsize=18)

    # ── Subplot phải: giai đoạn cuối ─────────────────────────────────────────
    ax2.quiver(
        late_x,
        late_y,
        # Vận tốc hướng về Gbest + nhiễu nhỏ → mô phỏng lực hút của hệ số gia tốc cao
        (gbx - late_x) * 0.5 + rng.normal(0, 0.5, particle_count),
        (gby - late_y) * 0.5 + rng.normal(0, 0.5, particle_count),
        color=CHART_MAGENTA,
        alpha=0.7,
    )
    ax2.scatter(late_x, late_y, color=CHART_PURPLE, s=30)
    ax2.scatter(
        gbx,
        gby,
        color=CHART_GOLD,
        marker="*",
        s=200,
        edgecolors="black",
        label="Tối ưu toàn cục (Gbest)",
    )
    ax2.set_title("Giai đoạn cuối", fontsize=18)

    # Áp dụng cài đặt chung cho cả 2 subplot
    for _ax in (ax1, ax2):
        _ax.set_xlim(space_min_value, space_max_value)
        _ax.set_ylim(space_min_value, space_max_value)
        _ax.set_xlabel("Không gian X₁", fontsize=16)
        _ax.set_ylabel("Không gian X₂", fontsize=16)
        _ax.grid(True, linestyle=":")
        _ax.legend(fontsize=14)

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] TVAC saved to '{out_path}'")


# ════════════════════════════════════════════════════════════════════════════════
# 3. Biểu đồ SOBL — Stochastic Opposition-Based Learning
#    So sánh phân bố cá thể KHI và KHÔNG áp dụng học đối lập ngẫu nhiên
# ════════════════════════════════════════════════════════════════════════════════
def plot_sobl(
    n_particles: int = 20,  # Số cá thể minh hoạ
    seed: int = 42,
    out_path: str = "data/results/improved/sobl.png",
    figsize: Tuple[float, float] = (11.0, 4.8),
    dpi: int = 150,
) -> None:
    rng = np.random.default_rng(seed)

    focus = np.array([0.50, 0.50])  # Điểm trung tâm (điểm đang xét trên quỹ đạo)
    lb, ub = focus - 0.30, focus + 0.30  # Vùng lân cận [0.20, 0.80] × [0.20, 0.80]

    # Cá thể gốc: phân phối chuẩn quanh focus, cắt tại [0.06, 0.94]
    raw = np.clip(rng.normal(focus, 0.13, (n_particles, 2)), 0.06, 0.94)

    # Điểm đối lập: lb + ub - raw (phản chiếu qua vùng lb..ub) + nhiễu nhỏ
    opp = np.clip(
        lb + ub - raw * rng.normal(1.0, 0.15, n_particles)[:, None], 0.06, 0.94
    )

    # Quỹ đạo mẫu đi qua điểm focus (minh hoạ đường đi robot)
    path_pts = np.array(
        [
            [0.08, 0.88],
            [0.22, 0.72],
            [0.40, 0.58],
            [0.50, 0.50],  # ← focus
            [0.62, 0.38],
            [0.78, 0.24],
            [0.92, 0.10],
        ]
    )

    fig, (ax_without, ax_with) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)

    for ax, show_sobl in [(ax_without, False), (ax_with, True)]:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.set_xlabel("Không gian X₁", fontsize=16)
        ax.set_ylabel("Không gian X₂", fontsize=16)
        ax.grid(True, linestyle=":")

        # Vẽ quỹ đạo đường đi
        ax.plot(
            path_pts[:, 0],
            path_pts[:, 1],
            color=CHART_GREEN,
            lw=2.0,
            linestyle=(0, (6, 4)),
            label="Quỹ đạo",
            zorder=2,
        )
        # Đánh dấu điểm đang xét
        ax.scatter(
            [focus[0]],
            [focus[1]],
            marker="D",
            s=80,
            color=DARK_GRAY,
            zorder=6,
            label="Điểm đang xét",
        )

        if show_sobl:
            # Vẽ hình chữ nhật vùng lân cận (minh hoạ không gian áp dụng SOBL)
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (lb[0], lb[1]),
                    ub[0] - lb[0],
                    ub[1] - lb[1],
                    boxstyle="square,pad=0",
                    linewidth=0.9,
                    edgecolor=HEX_MEDIUM,
                    facecolor="none",
                    linestyle=(0, (4, 3)),
                    alpha=0.6,
                )
            )
            # Đường nối cá thể gốc ↔ điểm đối lập
            for i in range(n_particles):
                ax.plot(
                    [raw[i, 0], opp[i, 0]],
                    [raw[i, 1], opp[i, 1]],
                    color=CHART_ORANGE,
                    lw=0.7,
                    alpha=0.3,
                    linestyle=(0, (2, 3)),
                )
            # Vẽ điểm đối lập (tam giác cam)
            ax.scatter(
                opp[:, 0],
                opp[:, 1],
                s=40,
                color=CHART_ORANGE,
                marker="^",
                alpha=0.75,
                zorder=4,
                label="Điểm đối lập",
            )

        # Vẽ cá thể gốc (tròn xanh) — luôn hiển thị ở cả 2 subplot
        ax.scatter(
            raw[:, 0],
            raw[:, 1],
            s=55,
            color=CHART_BLUE,
            alpha=0.85,
            zorder=5,
            label="Cá thể gốc",
        )
        ax.set_title("Áp dụng SOBL" if show_sobl else "Không áp dụng SOBL", fontsize=18)
        ax.legend(fontsize=12, loc="upper right")

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] SOBL saved to '{out_path}'")


# ════════════════════════════════════════════════════════════════════════════════
# 4. Biểu đồ làm mượt góc quay bằng đường cong Bézier bậc 2
# ════════════════════════════════════════════════════════════════════════════════
def plot_bezier_corner_smoothing(
    blend_ratio: float = 0.3,  # Tỉ lệ kéo điểm vào/ra so với đoạn trước/sau
    out_path: str = "data/results/improved/bezier_corner_smoothing.png",
    figsize: Tuple[float, float] = (7.2, 4.5),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    # Ba điểm kiểm soát của góc gãy ban đầu
    prev_point = np.array([2.0, 2.0])  # Điểm trước đỉnh
    corner_point = np.array([6.0, 8.0])  # Đỉnh góc gãy (điểm hiện tại P_curr)
    next_point = np.array([10.0, 3.0])  # Điểm sau đỉnh

    # Nội suy điểm vào (P_in) và điểm ra (P_out) theo blend_ratio
    # P_in  = corner + ratio * (prev - corner)  →  lùi về phía prev 30 %
    entry_point = corner_point + blend_ratio * (prev_point - corner_point)
    # P_out = corner + ratio * (next - corner)  →  tiến về phía next 30 %
    exit_point = corner_point + blend_ratio * (next_point - corner_point)

    # Tham số t ∈ [0, 1] để vẽ đường cong Bézier bậc 2
    t = np.linspace(0.0, 1.0, 100)

    # Công thức Bézier bậc 2: B(t) = (1-t)²·P_in + 2(1-t)t·P_curr + t²·P_out
    bezier_points = (
        np.outer((1 - t) ** 2, entry_point)  # Đóng góp của điểm vào
        + np.outer(2 * (1 - t) * t, corner_point)  # Đóng góp của đỉnh (điểm kiểm soát)
        + np.outer(t**2, exit_point)  # Đóng góp của điểm ra
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_aspect("equal", adjustable="box")  # Giữ tỉ lệ X:Y = 1:1
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.set_xticks(np.arange(0, 13, 1))
    ax.set_yticks(np.arange(0, 11, 1))
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.7)

    # Vẽ quỹ đạo gốc (đường gãy góc)
    ax.plot(
        [prev_point[0], corner_point[0], next_point[0]],
        [prev_point[1], corner_point[1], next_point[1]],
        "r--o",
        label="Quỹ đạo gốc",
    )
    # Vẽ đường cong Bézier nội suy
    ax.plot(
        bezier_points[:, 0],
        bezier_points[:, 1],
        "b-",
        linewidth=2.5,
        label="Đường cong Bezier nội suy",
    )
    # Đánh dấu P_in và P_out
    ax.scatter(
        [entry_point[0], exit_point[0]],
        [entry_point[1], exit_point[1]],
        color=CHART_MAGENTA,
        s=80,
        zorder=5,
    )
    # Nhãn điểm dùng ký hiệu LaTeX
    ax.text(entry_point[0] - 0.8, entry_point[1] + 0.2, "$P_{in}$", fontsize=16)
    ax.text(exit_point[0] + 0.3, exit_point[1] + 0.2, "$P_{out}$", fontsize=16)
    ax.text(corner_point[0] - 0.5, corner_point[1] + 0.3, "$P_{curr}$", fontsize=16)

    ax.set_xlabel("Trục X", fontsize=14)
    ax.set_ylabel("Trục Y", fontsize=14)
    ax.legend(fontsize=14)
    ax.grid(True, linestyle=grid_style)
    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] Bezier saved to '{out_path}'")


# ════════════════════════════════════════════════════════════════════════════════
# 5. Hàm phân tích bảng số liệu TSV
# ════════════════════════════════════════════════════════════════════════════════
def _parse_comparison_table(
    raw: str,
) -> Tuple[List[str], Dict[str, List[Optional[float]]]]:
    """
    Đọc bảng TSV dạng chuỗi, trả về:
      - algorithms : danh sách tên thuật toán (cột tiêu đề)
      - data       : dict {tên_chỉ_số → [giá_trị hoặc None nếu không hợp lệ]}
    """
    # Xoá khoảng trắng đầu/cuối dòng và bỏ dòng trống
    lines = [ln.rstrip() for ln in raw.strip().splitlines() if ln.strip()]

    header_idx, algorithms = 0, []
    for i, line in enumerate(lines):
        parts = line.split("\t")  # Tách theo tab
        if len(parts) >= 3:  # Tìm dòng tiêu đề (≥ 3 cột)
            algorithms = [p.strip() for p in parts[1:] if p.strip()]  # Bỏ cột chỉ số
            header_idx = i
            break

    data: Dict[str, List[Optional[float]]] = {}
    for line in lines[header_idx + 1 :]:  # Duyệt từng dòng dữ liệu
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        metric = parts[0].strip()  # Tên chỉ số (cột đầu tiên)
        # Chuyển chuỗi → float; giá trị rỗng / "-" / "–" → None
        values = [None if v.strip() in ("", "-", "–") else float(v) for v in parts[1:]]
        # Chỉ lưu nếu số cột khớp với số thuật toán
        if metric and len(values) == len(algorithms):
            data[metric] = values

    return algorithms, data


# ════════════════════════════════════════════════════════════════════════════════
# 6. Biểu đồ so sánh thuật toán (cột + đường tỉ lệ thành công)
# ════════════════════════════════════════════════════════════════════════════════
def plot_algorithm_comparison(
    raw_table: str = COMPARISON_TABLE,
    map_name: str = MAP_NAME,
    out_base_dir: str = "data/results/charts",
    figsize: Tuple[float, float] = (7.0, 5.0),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    """
    Với mỗi chỉ số (trừ Tỷ lệ thành công), tạo một biểu đồ cột đôi trục:
      - Trục Y trái : giá trị chỉ số của từng thuật toán (cột)
      - Trục Y phải: Tỷ lệ thành công (đường đỏ với marker tròn)
    """
    if not map_name:
        print("[VISUALIZATION] MAP_NAME is not defined — skipping.")
        return

    algorithms, data = _parse_comparison_table(raw_table)
    if not algorithms or not data:
        print("[VISUALIZATION] Failed to parse data from the table.")
        return

    # Tạo tên thư mục theo MAP_NAME + timestamp để tránh ghi đè
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(out_base_dir, f"{map_name}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    x = np.arange(len(algorithms))  # Vị trí cột trên trục X: 0, 1, 2, 3
    # Chiều rộng cột: điều chỉnh theo số thuật toán, tối đa 0.65
    bar_width = min(0.55 / max(len(algorithms) - 1, 1) * len(algorithms), 0.65)
    colors = CHART_COLORS[: len(algorithms)]  # Màu cho từng thuật toán
    hatches = CHART_HATCHES[: len(algorithms)]  # Họa tiết cho từng thuật toán
    success_rates = data["Tỷ lệ thành công"]  # Giữ sẵn để vẽ trục phụ

    for metric, values in data.items():
        if metric == "Tỷ lệ thành công":
            continue  # Chỉ số này được vẽ trên trục phụ, không cần cột riêng

        fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)
        ax2 = ax1.twinx()  # Trục Y thứ hai dùng chung trục X với ax1

        # Lọc bỏ các giá trị None (thuật toán không hợp lệ)
        valid = [
            (x[i], v, colors[i], hatches[i])
            for i, v in enumerate(values)
            if v is not None
        ]
        valid_x, valid_values, valid_colors, valid_hatches = zip(*valid)

        # Vẽ cột — màu và họa tiết khác nhau cho từng thuật toán
        bars = ax1.bar(
            valid_x,
            valid_values,
            width=bar_width,
            color=valid_colors,
            edgecolor="black",
            linewidth=0.8,
        )
        # Áp họa tiết cho từng cột
        for bar, hatch in zip(bars, valid_hatches):
            bar.set_hatch(hatch)

        # Ghi giá trị số lên đỉnh mỗi cột
        max_val = max(valid_values)
        for bar, val in zip(bars, valid_values):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,  # Canh giữa cột theo X
                bar.get_height() + max_val * 0.015,  # Đẩy lên thêm 1.5 % chiều cao
                f"{val:.4g}",  # Định dạng 4 chữ số có nghĩa
                ha="center",
                va="bottom",
                fontsize=16,
            )

        # Vẽ đường Tỷ lệ thành công trên trục Y phải
        ax2.plot(
            x,
            success_rates,
            marker="o",
            linewidth=2.5,
            color="red",
            label="Tỷ lệ thành công",
        )

        # Cài đặt nhãn và scale
        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms, fontsize=20)
        ax1.set_ylabel(metric, fontsize=20)
        ax2.set_ylabel("Tỷ lệ thành công (%)", fontsize=20)
        ax1.set_ylim(
            0, max_val * 1.18
        )  # Thêm 18 % không gian phía trên để có chỗ ghi số
        ax2.set_ylim(0, 105)  # Tỷ lệ % tối đa 100, thêm lề 5
        ax1.tick_params(axis="y", labelsize=18)
        ax2.tick_params(axis="y", labelsize=18)
        ax1.grid(True, axis="y", linestyle=grid_style, alpha=0.6)
        ax1.set_axisbelow(True)  # Đường lưới nằm sau cột (không che cột)
        fig.tight_layout()

        # Lấy tên file từ map; nếu không có thì dùng tên chỉ số viết thường, thay dấu cách bằng _
        file_stem = METRIC_FILENAME_MAP.get(metric, metric.lower().replace(" ", "_"))
        _save_fig(fig, os.path.join(out_dir, f"{file_stem}.png"))

    print(f"[VISUALIZATION] Completed — {len(data)} charts saved to '{out_dir}'")


# ════════════════════════════════════════════════════════════════════════════════
# Điểm vào chính — chọn hàm cần chạy bằng cách bỏ comment
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    # plot_stochastic_inertia_weight()  # Biểu đồ trọng số quán tính ngẫu nhiên
    # plot_tvac()                       # Biểu đồ TVAC (giai đoạn đầu vs cuối)
    # plot_sobl()                       # Biểu đồ học đối lập ngẫu nhiên
    plot_bezier_corner_smoothing()  # Biểu đồ làm mượt góc bằng Bézier
    # plot_algorithm_comparison()       # Biểu đồ so sánh 4 thuật toán

    pass  # Giữ lại để tránh lỗi cú pháp khi tất cả dòng bị comment
