from astar import Astar  # Import thuật toán A*
from config.colors import (
    BLACK,
    MEDIUM,
    LIGHT,
    WHITE,  # Màu trắng/đen/xám (nền, lưới, viền)
    RED,
    ORANGE,
    YELLOW,  # Màu nóng cho path và UI
    GREEN,
    BLUE,
    INDIGO,
    VIOLET,  # Màu lạnh cho path và UI
)
from config.ui import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,  # Kích thước cửa sổ ứng dụng
    NAV_HEIGHT,
    NAV_WIDTH,  # Kích thước panel menu bên trái
    NAV_MENU,  # Danh sách các mục menu hiển thị
    NAV_OFFSET_X,
    NAV_OFFSET_Y,  # Vị trí bắt đầu vẽ menu
    MODE_HEIGHT,
    MODE_OFFSET_X,
    MODE_OFFSET_Y,  # Thanh trạng thái (mode + thuật toán)
    GRID_CELL_SIZE,  # Kích thước mỗi ô lưới (pixel)
    TEXT_FONT,  # Font chữ dùng trong pygame
    SMALL_TEXT_SIZE,
    NORMAL_TEXT_SIZE,
    LARGE_TEXT_SIZE,  # Cỡ chữ
    TKINTER_ALGOR_WINDOW_SIZE,  # Kích thước cửa sổ chọn thuật toán (Tkinter)
    TKINTER_BATCH_WINDOW_SIZE,  # Kích thước cửa sổ batch test (Tkinter)
    TKINTER_TEXT_FONT,
    TKINTER_TEXT_SIZE,  # Font và cỡ chữ trong Tkinter
)
from config.parameter import (
    GRID_MAP_HEIGHT,
    GRID_MAP_WIDTH,  # Kích thước mặc định bản đồ lưới
    MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu
    COLLISION_PENALTY,  # Giá trị phạt khi va chạm
)
from datetime import datetime  # Lấy thời gian thực để ghi log
from grid_map import GridMap  # Lớp bản đồ lưới
from hapso import HAPSO  # Thuật toán HAPSO
from openpyxl import Workbook  # Tạo file Excel
from pathlib import Path  # Làm việc với đường dẫn file
from prm import PRM  # Thuật toán PRM
from rrt_star import RRTStar  # Thuật toán RRT*
from tkinter import filedialog, messagebox, Tk  # Hộp thoại file, thông báo
from utils import (
    compute_path_metrics,  # Tính các chỉ số đánh giá đường đi
    print_all_path_metrics,  # In bảng so sánh tất cả thuật toán
    print_batch_header,  # In tiêu đề batch test
    print_batch_summary_report,  # In báo cáo tổng kết batch test
    print_path_metrics,  # In metrics một thuật toán
    save_run_results,  # Lưu kết quả ra file
)

import json  # Đọc/ghi file JSON (bản đồ)
import pygame  # Thư viện giao diện đồ họa
import time  # Đo thời gian chạy thuật toán
import tkinter as tk  # Giao diện hộp thoại (dialog)

# ─────────────────────────────────────────────
#  LỚP Text: Hiển thị chữ lên màn hình pygame
# ─────────────────────────────────────────────


class Text:
    def __init__(
        self,
        screen: pygame.Surface,  # Bề mặt pygame để vẽ lên
        x: int,  # Tọa độ x (pixel)
        y: int,  # Tọa độ y (pixel)
        color: tuple[int, int, int],  # Màu sắc (R, G, B)
        text: str,  # Nội dung chữ
        font_name: str = TEXT_FONT,  # Tên font
        size: int = NORMAL_TEXT_SIZE,  # Cỡ chữ
    ) -> None:
        self.screen = screen
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.font_name = font_name
        self.size = size

        self.font = pygame.font.SysFont(self.font_name, self.size)  # Tạo đối tượng font

    def draw_text(self) -> None:
        """Render và vẽ chữ lên màn hình pygame."""
        text_surface = self.font.render(
            self.text, True, self.color
        )  # Render chữ thành Surface
        self.screen.blit(text_surface, (self.x, self.y))  # Vẽ lên màn hình


# ─────────────────────────────────────────────
#  HỘP THOẠI CHỌN THUẬT TOÁN (Tkinter)
# ─────────────────────────────────────────────


class AlgorithmSelectDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, current_idx: int, options: list[str]) -> None:
        super().__init__(parent)

        self.title("Select Algorithm")  # Tiêu đề cửa sổ
        self.geometry(TKINTER_ALGOR_WINDOW_SIZE)  # Kích thước cửa sổ
        self.result = None  # Lưu kết quả người dùng chọn
        self.lift()  # Đưa cửa sổ lên trên cùng
        self.focus_force()  # Bắt focus về cửa sổ này
        self.grab_set()  # Chặn tương tác với cửa sổ khác (modal)

        tk.Label(
            self, text="Choose Solver:", font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE)
        ).pack(pady=10)

        self.selected_algo_var = tk.IntVar(
            value=current_idx
        )  # Biến lưu index thuật toán được chọn

        # Tạo RadioButton cho mỗi thuật toán
        for i, name in enumerate(options):
            tk.Radiobutton(
                self,
                text=name,
                variable=self.selected_algo_var,
                value=i,
                font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
            ).pack(anchor="w", padx=40)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        # Nút "Select" xác nhận chọn
        tk.Button(
            btn_frame,
            text="Select",
            command=self.on_select,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)

        # Nút "Cancel" đóng cửa sổ không lưu gì
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)

        self._center_window()  # Căn giữa cửa sổ trên màn hình

    def on_select(self) -> None:
        """Lưu kết quả lựa chọn và đóng cửa sổ."""
        self.result = self.selected_algo_var.get()
        self.destroy()

    def _center_window(self) -> None:
        """Căn giữa cửa sổ Tkinter trên màn hình."""
        self.update_idletasks()  # Cập nhật layout trước khi lấy kích thước thực

        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")  # Đặt lại vị trí cửa sổ


# ─────────────────────────────────────────────
#  HỘP THOẠI CẤU HÌNH BATCH TEST
# ─────────────────────────────────────────────


class BatchTestDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)

        self.title("Batch Test Configuration")
        self.geometry(TKINTER_BATCH_WINDOW_SIZE)
        self.result = None  # Số lần chạy do người dùng nhập
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(
            self,
            text="Number of Test Runs (1-100):",
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(pady=10)

        self.run_count_var = tk.IntVar(value=10)  # Giá trị mặc định: 10 lần chạy
        tk.Entry(
            self,
            textvariable=self.run_count_var,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Start Testing",
            command=self.on_start,
            width=15,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)

        self._center_window()

    def on_start(self) -> None:
        """Validate số lần chạy và lưu kết quả nếu hợp lệ."""
        try:
            runs = self.run_count_var.get()  # Đọc giá trị từ ô nhập

        except tk.TclError:
            messagebox.showerror("Error", "Invalid number.")
            return

        # Kiểm tra kiểu int và phạm vi [1, 100]
        if not isinstance(runs, int) or not (1 <= runs <= 100):
            messagebox.showerror("Error", "Enter 1-100.")
            return

        self.result = runs  # Lưu số lần chạy hợp lệ
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────────────────────────
#  HỘP THOẠI CÀI ĐẶT BẢN ĐỒ
# ─────────────────────────────────────────────


class SettingsDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        current_width: int,
        current_height: int,
        current_cell_size: int,
    ) -> None:
        super().__init__(parent)

        self.title("Map Settings")
        self.geometry("300x250")
        self.result = None  # Lưu (width, height, cell_size) sau khi xác nhận
        self.lift()
        self.focus_force()
        self.grab_set()

        # Ô nhập chiều rộng bản đồ
        tk.Label(self, text="Width (5-100):").pack(pady=(10, 0))
        self.width_var = tk.IntVar(value=current_width)
        tk.Entry(self, textvariable=self.width_var).pack()

        # Ô nhập chiều cao bản đồ
        tk.Label(self, text="Height (5-100):").pack(pady=(10, 0))
        self.height_var = tk.IntVar(value=current_height)
        tk.Entry(self, textvariable=self.height_var).pack()

        # Ô nhập kích thước ô lưới (pixel)
        tk.Label(self, text="Cell Size (5-50 px):").pack(pady=(10, 0))
        self.cell_size_var = tk.IntVar(value=current_cell_size)
        tk.Entry(self, textvariable=self.cell_size_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Apply", command=self.on_apply, width=10).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(
            side=tk.LEFT, padx=5
        )

        self._center_window()

    def on_apply(self) -> None:
        """Validate đầu vào và lưu kết quả cài đặt bản đồ."""
        try:
            width = self.width_var.get()
            height = self.height_var.get()
            cell_size = self.cell_size_var.get()

        except tk.TclError:
            messagebox.showerror("Error", "Invalid input.")
            return

        # Kiểm tra phạm vi hợp lệ cho tất cả tham số
        if not (5 <= width <= 100 and 5 <= height <= 100 and 5 <= cell_size <= 50):
            messagebox.showerror("Error", "Values out of range.")
            return

        self.result = (width, height, cell_size)  # Lưu kết quả
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────────────────────────
#  LỚP App: ỨNG DỤNG CHÍNH
# ─────────────────────────────────────────────


class App:
    def __init__(self) -> None:
        print("=" * 60)
        print("HAPSO: Hybrid A-Star Particle Swarm Optimizer")
        print("=" * 60)
        print("[INIT] Initializing application...")

        pygame.init()  # Khởi tạo pygame

        # Tạo cửa sổ pygame với kích thước cố định
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("HAPSO: Simulator Application")

        # Tạo cửa sổ Tkinter ẩn (dùng làm parent cho các dialog)
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Ẩn cửa sổ Tkinter chính

        self.clock = pygame.time.Clock()  # Đồng hồ kiểm soát FPS
        self.font = pygame.font.SysFont(TEXT_FONT, NORMAL_TEXT_SIZE)  # Font chữ pygame

        # Kích thước bản đồ và ô lưới
        self.height = GRID_MAP_HEIGHT
        self.width = GRID_MAP_WIDTH
        self.cell_size = GRID_CELL_SIZE

        self.grid_map = GridMap(
            width=self.width, height=self.height
        )  # Khởi tạo bản đồ lưới

        self.min_clearance = MIN_CLEARANCE  # Khoảng cách an toàn tối thiểu
        self.collision_penalty = COLLISION_PENALTY  # Giá trị phạt va chạm

        # Trạng thái ứng dụng
        self.running = True  # Vòng lặp chính còn chạy không
        self.mode = "Free"  # Chế độ tương tác hiện tại (Free/Obstacle/Erase/Start/Goal)
        self.selected_algorithm = "A-Star"  # Thuật toán đang được chọn

        # Trạng thái kéo chuột (vẽ chướng ngại vật)
        self.is_dragging = False
        self.drag_start: tuple[float, float] | None = None  # Điểm bắt đầu kéo
        self.drag_end: tuple[float, float] | None = None  # Điểm kết thúc kéo

        self.current_path: list[tuple[float, float]] | None = (
            None  # Đường đi hiện tại (kết quả thuật toán)
        )

        self.map_name: str = "N/A"  # Tên bản đồ (lấy từ tên file khi import)

        # Danh sách tên các thuật toán hỗ trợ
        self.algorithm_names = [
            "RRT-Star",
            "PRM",
            "A-Star",
            "HAPSO",
            "All",  # Chạy tất cả thuật toán cùng lúc
        ]

        # Gán màu cho từng thuật toán (trừ "All")
        colors_for_algos = [BLUE, ORANGE, GREEN, VIOLET, INDIGO, YELLOW, RED]
        self.algorithm_colors: dict[str, tuple[int, int, int]] = {
            name: colors_for_algos[i % len(colors_for_algos)]
            for i, name in enumerate(self.algorithm_names)
            if name != "All"
        }

        self.all_paths: dict[str, list[tuple[float, float]]] = (
            {}
        )  # Lưu đường đi khi chạy chế độ "All"

        self._recalc_layout()  # Tính lại vị trí lưới trên màn hình

        print(
            f"[INIT] Grid initialized: {self.width}x{self.height} (cell size: {self.cell_size}px)"
        )
        print(f"[INIT] Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"[INIT] Ready. Press [?] or check menu for commands.\n")

    @staticmethod
    def _now_str() -> str:
        """Trả về chuỗi thời gian hiện tại theo định dạng YYYY-MM-DD HH:MM:SS."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ─────────────────────────────────────────────
    #  VÒNG LẶP CHÍNH
    # ─────────────────────────────────────────────

    def run(self) -> None:
        """Vòng lặp chính của ứng dụng: xử lý sự kiện → vẽ UI → lặp lại (60 FPS)."""
        while self.running:
            self._handle_events()  # Xử lý tất cả sự kiện pygame
            self._draw_ui()  # Vẽ toàn bộ giao diện
            self.clock.tick(60)  # Giới hạn 60 FPS

        print("\n[EXIT] Shutting down application...")
        pygame.quit()  # Dọn dẹp pygame
        self.tk_root.destroy()  # Đóng Tkinter
        print("[EXIT] Application closed.")

    # ─────────────────────────────────────────────
    #  XỬ LÝ SỰ KIỆN
    # ─────────────────────────────────────────────

    def _handle_events(self) -> None:
        """Phân phối tất cả sự kiện pygame đến các handler tương ứng."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  # Nhấn nút đóng cửa sổ → thoát

            elif event.type == pygame.MOUSEMOTION:
                self._on_mouse_motion(event)  # Di chuyển chuột

            elif event.type == pygame.MOUSEBUTTONUP:
                self._on_mouse_up(event)  # Nhả chuột

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_down(event)  # Nhấn chuột

            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event)  # Nhấn phím

    def _on_mouse_motion(self, event: pygame.event.Event) -> None:
        """Cập nhật điểm kết thúc kéo khi di chuyển chuột trong chế độ kéo."""
        if not self.is_dragging:
            return

        grid_pos = self._screen_to_grid(event.pos)  # Chuyển tọa độ pixel → ô lưới
        if grid_pos is not None:
            self.drag_end = grid_pos  # Cập nhật điểm cuối kéo

    def _on_mouse_up(self, event: pygame.event.Event) -> None:
        """Khi nhả chuột trái: áp dụng đường kéo (vẽ/xóa chướng ngại vật)."""
        if event.button != 1:  # Chỉ xử lý chuột trái
            return

        if (
            self.is_dragging
            and self.drag_start is not None
            and self.drag_end is not None
        ):
            # Tính các ô trên đường thẳng từ drag_start → drag_end (Bresenham)
            pts = self._bresenham_line(self.drag_start, self.drag_end)
            self._apply_line(pts)  # Áp dụng thay đổi lên bản đồ

        # Reset trạng thái kéo
        self.is_dragging = False
        self.drag_start = None
        self.drag_end = None

    def _on_mouse_down(self, event: pygame.event.Event) -> None:
        """Khi nhấn chuột trái: xử lý theo chế độ hiện tại."""
        if event.button != 1:
            return

        grid_pos = self._screen_to_grid(event.pos)  # Tọa độ ô lưới được click
        if grid_pos is None:
            return  # Click ngoài vùng lưới → bỏ qua

        if self.mode == "Free":
            pass  # Chế độ tự do: không làm gì

        elif self.mode in ("Obstacle", "Erase"):
            # Bắt đầu kéo để vẽ/xóa chướng ngại vật
            self.is_dragging = True
            self.drag_start = grid_pos
            self.drag_end = grid_pos

        elif self.mode == "Start":
            # Đặt điểm Start tại vị trí click
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None  # Xóa đường đi cũ
                self._stop_simulation()

        elif self.mode == "Goal":
            # Đặt điểm Goal tại vị trí click
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None
                self._stop_simulation()

    def _on_keydown(self, event: pygame.event.Event) -> None:
        """Xử lý phím tắt bàn phím."""
        if event.key == pygame.K_ESCAPE:
            self.running = False  # ESC → thoát ứng dụng

        elif event.key == pygame.K_0:
            self.mode = "Free"  # 0 → chế độ tự do

        elif event.key == pygame.K_1:
            self.mode = "Obstacle"  # 1 → vẽ chướng ngại vật

        elif event.key == pygame.K_2:
            self.mode = "Erase"  # 2 → xóa chướng ngại vật

        elif event.key == pygame.K_s:
            self.mode = "Start"  # S → đặt điểm Start

        elif event.key == pygame.K_g:
            self.mode = "Goal"  # G → đặt điểm Goal

        elif event.key == pygame.K_c:
            self._clear_map()  # C → xóa toàn bộ bản đồ

        elif event.key == pygame.K_i:
            self._import_map()  # I → nhập bản đồ từ file JSON

        elif event.key == pygame.K_e:
            self._export_map()  # E → xuất bản đồ ra file JSON

        elif event.key == pygame.K_a:
            self._open_algo_dialog()  # A → mở hộp thoại chọn thuật toán

        elif event.key == pygame.K_SPACE:
            # SPACE → chạy thuật toán đã chọn
            result = self._run_selected_algorithm()

            if result is not None:
                algo_elapsed, metrics = result

                try:
                    # Lưu kết quả ra file sau khi chạy
                    run_dir = save_run_results(
                        algorithm_name=self.selected_algorithm,
                        path=self.current_path or [],
                        metrics=metrics,
                        map_name=self.map_name,
                    )
                    print(f"[SAVE] Results saved → {run_dir}")

                except Exception as exc:
                    print(f"[SAVE] WARNING – could not save results: {exc}")

        elif event.key == pygame.K_r:
            self._reset_result()  # R → xóa kết quả đường đi

        elif event.key == pygame.K_b:
            self._open_batch_test_dialog()  # B → mở hộp thoại batch test

        elif event.key == pygame.K_p:
            self._open_settings_dialog()  # P → mở cài đặt bản đồ

    # ─────────────────────────────────────────────
    #  CHUYỂN ĐỔI TỌA ĐỘ VÀ VẼ ĐƯỜNG
    # ─────────────────────────────────────────────

    def _screen_to_grid(
        self, screen_pos: tuple[float, float]
    ) -> tuple[float, float] | None:
        """
        Chuyển tọa độ pixel (màn hình) sang tọa độ ô lưới.
        Trả về None nếu click ngoài vùng lưới.
        """
        sx, sy = screen_pos
        grid_w = self.grid_map.width * self.cell_size  # Chiều rộng vùng lưới (pixel)
        grid_h = self.grid_map.height * self.cell_size  # Chiều cao vùng lưới (pixel)

        # Kiểm tra có nằm trong vùng lưới không
        if (
            sx < self.grid_offset_x
            or sy < self.grid_offset_y
            or sx >= self.grid_offset_x + grid_w
            or sy >= self.grid_offset_y + grid_h
        ):
            return None

        # Tính chỉ số ô lưới từ tọa độ pixel
        grid_x = (sx - self.grid_offset_x) // self.cell_size
        grid_y = (sy - self.grid_offset_y) // self.cell_size

        return (grid_x, grid_y)

    def _bresenham_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> list[tuple[float, float]]:
        """
        Thuật toán Bresenham để tính tập hợp các ô lưới nằm trên đường thẳng
        từ `start` đến `end`. Dùng để vẽ chướng ngại vật khi kéo chuột.
        """
        x0, y0 = start
        x1, y1 = end
        points = []

        dx = abs(x1 - x0)  # Hiệu tuyệt đối theo x
        dy = abs(y1 - y0)  # Hiệu tuyệt đối theo y
        err = dx - dy  # Sai số ban đầu

        step_x = 1 if x0 < x1 else -1  # Hướng di chuyển theo x
        step_y = 1 if y0 < y1 else -1  # Hướng di chuyển theo y

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break  # Đã đến điểm cuối

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += step_x  # Bước theo x

            if e2 < dx:
                err += dx
                y += step_y  # Bước theo y

        return points

    def _apply_line(self, points: list[tuple[float, float]]) -> None:
        """
        Áp dụng thay đổi (thêm/xóa chướng ngại vật) lên các ô trong danh sách points.
        Xóa đường đi hiện tại nếu có thay đổi.
        """
        if self.mode == "Free":
            return  # Chế độ tự do không làm gì

        changed = False
        for x, y in points:
            if self.mode == "Obstacle":
                changed = (
                    self.grid_map.set_obstacle(x, y, True) or changed
                )  # Đặt chướng ngại vật

            elif self.mode == "Erase":
                changed = (
                    self.grid_map.set_obstacle(x, y, False) or changed
                )  # Xóa chướng ngại vật

        if changed:
            self.current_path = None  # Bản đồ thay đổi → đường đi cũ không còn hợp lệ

    # ─────────────────────────────────────────────
    #  THAO TÁC BẢN ĐỒ
    # ─────────────────────────────────────────────

    def _clear_map(self) -> None:
        """Xóa toàn bộ bản đồ: lưới, start, goal, chướng ngại vật, đường đi."""
        self.grid_map.grid = [
            [GridMap.FREE for _ in range(self.grid_map.width)]
            for _ in range(self.grid_map.height)
        ]
        self.grid_map.rebuild_obstacle_set()  # Xây dựng lại obstacle set (rỗng)
        self.grid_map.start = None
        self.grid_map.goal = None
        self.current_path = None
        self.map_name = "N/A"

        self._stop_simulation()
        print("[MAP] Map cleared")

    def _reset_result(self) -> None:
        """Xóa đường đi hiện tại nhưng giữ nguyên bản đồ."""
        self.current_path = None
        self._stop_simulation()
        print("[RUN] Result reset")

    def _import_map(self) -> None:
        """Nhập bản đồ từ file JSON do người dùng chọn."""
        path = self._ask_open_path()
        if not path:
            print("[IMPORT] Cancelled")
            return

        file_path = Path(path)
        if not file_path.exists():
            print(f"[IMPORT] ERROR - File not found: {path}")
            return

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)  # Đọc và parse JSON

            loaded = self._dict_to_grid_map(data)  # Chuyển dict → GridMap
            if loaded is None:
                print("[IMPORT] ERROR - Invalid map data")
                return

            # Cập nhật bản đồ mới
            self.grid_map = loaded
            self.map_name = file_path.stem  # Lấy tên file (không có phần mở rộng)
            self.current_path = None
            self.all_paths = {}
            self._stop_simulation()
            self._recalc_layout()  # Tính lại vị trí lưới trên màn hình

            print(
                f"[IMPORT] SUCCESS - Map loaded: {self.grid_map.width}x{self.grid_map.height}"
            )

            if self.grid_map.start:
                print(f"[IMPORT] Start position: {self.grid_map.start}")
            if self.grid_map.goal:
                print(f"[IMPORT] Goal position: {self.grid_map.goal}")

            obstacle_count = self.grid_map.get_obstacle_count()
            total_cells = self.grid_map.width * self.grid_map.height
            obstacle_ratio = round(obstacle_count / total_cells * 100)
            print(
                f"[IMPORT] Obstacle count: {obstacle_count} / {total_cells} ({obstacle_ratio}%)"
            )

        except Exception as e:
            print(f"[IMPORT] ERROR - {str(e)}")

    def _export_map(self) -> None:
        """Xuất bản đồ hiện tại ra file JSON (yêu cầu đã đặt cả Start và Goal)."""
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[EXPORT] ERROR - Start and goal positions must be set")
            return

        try:
            base_dir = Path("data/maps")
            base_dir.mkdir(parents=True, exist_ok=True)  # Tạo thư mục nếu chưa có

            filename = self._ask_save_path(str(base_dir))  # Mở hộp thoại lưu file
            if not filename:
                print("[EXPORT] Cancelled")
                return

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self._grid_map_to_dict(self.grid_map), f, indent=2)

            self.map_name = Path(filename).stem
            print(f"[EXPORT] SUCCESS - Map saved to: {filename}")
            print(f"[EXPORT] Map size: {self.grid_map.width}x{self.grid_map.height}")

        except Exception as e:
            print(f"[EXPORT] ERROR - {str(e)}")

    def _ask_open_path(self) -> str:
        """Mở hộp thoại chọn file JSON để nhập bản đồ."""
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)  # Đảm bảo hộp thoại hiện lên trên cùng
        try:
            return filedialog.askopenfilename(
                parent=root,
                title="Import map JSON",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            )
        finally:
            root.destroy()  # Luôn đóng cửa sổ Tkinter tạm

    def _ask_save_path(self, initial_dir: str = "") -> str:
        """Mở hộp thoại lưu file JSON để xuất bản đồ."""
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return filedialog.asksaveasfilename(
                parent=root,
                title="Export map JSON",
                initialdir=initial_dir,
                defaultextension=".json",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            )
        finally:
            root.destroy()

    def _dict_to_grid_map(self, data: dict) -> GridMap | None:
        """
        Chuyển dict (đọc từ JSON) thành đối tượng GridMap.
        Trả về None nếu dữ liệu không hợp lệ.
        """
        if not isinstance(data, dict):
            return None

        # Kiểm tra các trường bắt buộc
        if "width" not in data or "height" not in data or "grid" not in data:
            return None

        try:
            gm = GridMap(
                data["width"], data["height"]
            )  # Tạo GridMap với kích thước từ file
            gm.grid = data["grid"]  # Gán lưới từ file
            gm.rebuild_obstacle_set()  # Xây dựng lại obstacle set từ lưới
            gm.start = (
                tuple(data["start"]) if data.get("start") else None
            )  # Khôi phục Start
            gm.goal = (
                tuple(data["goal"]) if data.get("goal") else None
            )  # Khôi phục Goal
            return gm

        except (TypeError, ValueError):
            return None

    def _grid_map_to_dict(self, grid_map: GridMap) -> dict:
        """Chuyển đối tượng GridMap thành dict để lưu ra file JSON."""
        return {
            "width": grid_map.width,
            "height": grid_map.height,
            "grid": grid_map.grid,
            "start": grid_map.start,
            "goal": grid_map.goal,
        }

    # ─────────────────────────────────────────────
    #  CHẠY THUẬT TOÁN
    # ─────────────────────────────────────────────

    def _open_algo_dialog(self) -> None:
        """Mở hộp thoại chọn thuật toán và cập nhật lựa chọn."""
        dialog = AlgorithmSelectDialog(
            self.tk_root,
            self.algorithm_names.index(
                self.selected_algorithm
            ),  # Index thuật toán hiện tại
            self.algorithm_names,
        )

        self.tk_root.wait_window(dialog)  # Chờ người dùng đóng hộp thoại
        if dialog.result is not None:
            self.selected_algorithm = self.algorithm_names[dialog.result]
            print(f"[MENU] Algorithm selected: {self.selected_algorithm}")

    def _run_selected_algorithm(self) -> tuple[float, dict] | None:
        """
        Chạy thuật toán đang được chọn và trả về (thời gian chạy, metrics).
        Trả về None nếu chạy chế độ "All" hoặc có lỗi.
        """
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[ALGORITHM] ERROR - Start and goal positions must be set")
            return

        run_start_time = self._now_str()  # Ghi thời điểm bắt đầu

        if self.selected_algorithm != "All":
            self.all_paths = {}  # Reset all_paths nếu chỉ chạy 1 thuật toán

        match self.selected_algorithm:
            case "RRT-Star":
                planner = RRTStar(self.grid_map)

                algo_t0 = time.perf_counter()  # Bắt đầu đo thời gian
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0  # Thời gian chạy (giây)

                self._stop_simulation()

            case "PRM":
                planner = PRM(self.grid_map)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "A-Star":
                planner = Astar(
                    self.grid_map, min_clearance=0.0
                )  # A* không cần khoảng hở

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "HAPSO":
                planner = HAPSO(self.grid_map)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "All":
                # Chạy tất cả thuật toán, lưu kết quả riêng từng cái
                self.all_paths = {}
                self.all_path_metrics = {}
                algo_start_times: dict[str, str] = {}
                algo_end_times: dict[str, str] = {}

                for name in self.algorithm_names:
                    if name == "All":
                        continue  # Bỏ qua "All" trong danh sách

                    # Khởi tạo planner tương ứng
                    if name == "RRT-Star":
                        planner = RRTStar(self.grid_map)
                    elif name == "PRM":
                        planner = PRM(self.grid_map)
                    elif name == "A-Star":
                        planner = Astar(self.grid_map, min_clearance=0.0)
                    elif name == "HAPSO":
                        planner = HAPSO(self.grid_map)
                    else:
                        self.all_paths[name] = []
                        continue

                    # Ghi thời gian và chạy
                    algo_start_times[name] = self._now_str()
                    algo_t_start = time.perf_counter()
                    path = planner.plan()
                    algo_elapsed = time.perf_counter() - algo_t_start
                    algo_end_times[name] = self._now_str()

                    # Lưu đường đi và metrics
                    self.all_paths[name] = path or []
                    self.all_path_metrics[name] = {
                        **compute_path_metrics(
                            path=path or [],
                            algorithm_name=name,
                            grid_map=self.grid_map,
                        )[name],
                        "Execution time": algo_elapsed,
                    }

                    # Lưu kết quả ra file
                    try:
                        run_dir = save_run_results(
                            algorithm_name=name,
                            path=path or [],
                            metrics=self.all_path_metrics[name],
                            map_name=self.map_name,
                            start_time=algo_start_times[name],
                            end_time=algo_end_times[name],
                        )
                        print(f"[SAVE] {name} results saved → {run_dir}")
                    except Exception as exc:
                        print(f"[SAVE] WARNING – could not save {name} results: {exc}")

                self.current_path = None  # Không hiển thị đường đi đơn lẻ
                self._stop_simulation()

        run_end_time = self._now_str()

        # Nếu chế độ "All": in bảng so sánh tất cả thuật toán rồi return None
        if self.selected_algorithm == "All":
            print_all_path_metrics(
                self.all_path_metrics,
                self.all_paths,
                map_name=self.map_name,
                start_time=run_start_time,
                end_time=run_end_time,
                algo_start_times=algo_start_times,
                algo_end_times=algo_end_times,
            )
            return None

        # Tính metrics và in báo cáo cho thuật toán đơn lẻ
        metrics = compute_path_metrics(
            path=self.current_path or [],
            algorithm_name=self.selected_algorithm,
            grid_map=self.grid_map,
        )[self.selected_algorithm]
        metrics["Execution time"] = algo_elapsed

        print_path_metrics(
            {self.selected_algorithm: metrics},
            map_name=self.map_name,
            start_time=run_start_time,
            end_time=run_end_time,
            path=self.current_path,
        )

        return algo_elapsed, metrics

    # ─────────────────────────────────────────────
    #  BATCH TEST
    # ─────────────────────────────────────────────

    def _open_batch_test_dialog(self) -> None:
        """Mở hộp thoại batch test và chạy nếu người dùng xác nhận."""
        dialog = BatchTestDialog(self.tk_root)
        self.tk_root.wait_window(dialog)
        if dialog.result is not None:
            self._batch_test(dialog.result)

    def _batch_test(self, run_count: int = 10) -> None:
        """
        Chạy thuật toán đang chọn nhiều lần liên tiếp (batch test).
        Thu thập thống kê, lưu kết quả từng lần, xuất Excel tổng kết.
        """
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[BATCH] ERROR - Start and goal positions must be set")
            messagebox.showwarning("Batch Test", "Please set start and goal first.")
            return

        if self.selected_algorithm == "All":
            messagebox.showwarning(
                "Batch Test",
                "Please select a single algorithm before running batch test.",
            )
            return

        if run_count < 1:
            return

        batch_start_time = self._now_str()
        print_batch_header(
            self.selected_algorithm,
            self.map_name,
            batch_start_time,
            run_count,
        )

        # Khởi tạo các biến thống kê
        successful_runs = 0  # Số lần chạy thành công
        total_time = 0.0  # Tổng thời gian tất cả các lần
        path_lengths = []  # Độ dài đường đi của các lần thành công
        fitness_values = []  # Fitness của các lần thành công
        run_records: list[dict] = []  # Bản ghi chi tiết từng lần chạy
        best_success_run = None  # Lần chạy thành công tốt nhất
        best_failed_run = (
            None  # Lần chạy thất bại tốt nhất (nếu không có lần nào thành công)
        )

        # Tạo thư mục lưu kết quả batch
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_algo = "".join(
            c if (c.isalnum() or c in " _") else "_" for c in self.selected_algorithm
        ).replace(" ", "_")
        batch_root = (
            Path(__file__).resolve().parent
            / "data"
            / "results"
            / "batch_tests"
            / f"{safe_algo}_{timestamp}_batch"
        )
        batch_root.mkdir(parents=True, exist_ok=True)

        output_dir = batch_root

        for run_idx in range(run_count):
            # Xử lý sự kiện pygame trong vòng lặp batch (tránh treo ứng dụng)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested during batch test. Stopping.")
                    self.running = False
                    break

                elif ev.type == pygame.KEYDOWN:
                    try:
                        self._on_keydown(ev)
                    except Exception:
                        pass

            if not self.running:
                break

            print(f"[BATCH] ALGORITHM REPORT ({run_idx + 1}/{run_count})")

            run_start_time = self._now_str()
            result = self._run_selected_algorithm()  # Chạy thuật toán
            run_end_time = self._now_str()

            if result is None:
                continue

            run_time, metrics = result
            total_time += run_time

            curr_path = list(self.current_path) if self.current_path else []
            is_success = metrics["Result"]

            if is_success:
                successful_runs += 1
                path_len = len(curr_path)
                path_lengths.append(path_len)

                fitness = metrics["TOTAL FITNESS"]
                if fitness is not None:
                    fitness_values.append(fitness)

                # Bản ghi chi tiết lần chạy thành công
                record = {
                    "Run_ID": run_idx + 1,
                    "Found_Path": bool(curr_path),
                    "Success": is_success,
                    "Path_Length": path_len,
                    "Total_Distance": metrics["Total distance"],
                    "Total_Waypoint": metrics["Total waypoint"],
                    "Total_Angle": metrics["Total angle"],
                    "Min_Angle": metrics["Min angle"],
                    "Max_Angle": metrics["Max angle"],
                    "Average_Angle": metrics["Average angle"],
                    "Min_Clearance": metrics["Min clearance"],
                    "TOTAL_FITNESS": fitness,
                    "Execution_Time_s": run_time,
                    "Path": json.dumps(curr_path),
                    "_start": run_start_time,
                    "_end": run_end_time,
                }

                # Cập nhật best_success_run: ưu tiên fitness thấp → path ngắn → thời gian ít
                if (
                    best_success_run is None
                    or fitness < best_success_run["TOTAL_FITNESS"]
                    or (
                        fitness == best_success_run["TOTAL_FITNESS"]
                        and path_len < best_success_run["Path_Length"]
                    )
                    or (
                        fitness == best_success_run["TOTAL_FITNESS"]
                        and path_len == best_success_run["Path_Length"]
                        and run_time < best_success_run["Execution_Time_s"]
                    )
                ):
                    best_success_run = {**record, "path": curr_path}

            else:
                # Bản ghi lần chạy thất bại
                record = {
                    "Run_ID": run_idx + 1,
                    "Found_Path": bool(curr_path),
                    "Success": False,
                    "Path_Length": len(curr_path),
                    "Total_Distance": metrics["Total distance"],
                    "Total_Waypoint": metrics["Total waypoint"],
                    "Total_Angle": metrics["Total angle"],
                    "Min_Angle": metrics["Min angle"],
                    "Max_Angle": metrics["Max angle"],
                    "Average_Angle": metrics["Average angle"],
                    "Min_Clearance": metrics["Min clearance"],
                    "TOTAL_FITNESS": metrics["TOTAL FITNESS"],
                    "Execution_Time_s": run_time,
                    "Path": json.dumps(curr_path),
                    "_start": run_start_time,
                    "_end": run_end_time,
                }

                # Cập nhật best_failed_run: ưu tiên khoảng hở lớn nhất → path ngắn nhất
                if curr_path:
                    curr_clearance = metrics["Min clearance"] or 0

                    if (
                        best_failed_run is None
                        or curr_clearance > (best_failed_run["Min_Clearance"] or 0)
                        or (
                            curr_clearance == (best_failed_run["Min_Clearance"] or 0)
                            and len(curr_path) < best_failed_run["Path_Length"]
                        )
                    ):
                        best_failed_run = {**record, "path": curr_path}

            run_records.append(record)

            # Lưu kết quả từng lần chạy ra thư mục riêng
            try:
                run_dir = save_run_results(
                    algorithm_name=self.selected_algorithm,
                    path=curr_path,
                    metrics=metrics,
                    map_name=self.map_name,
                    start_time=run_start_time,
                    end_time=run_end_time,
                    base_dir=str(batch_root / f"run_{run_idx + 1:03d}"),
                )
                print(f"[SAVE] Run {run_idx + 1} saved → {run_dir}")

            except Exception as exc:
                print(f"[SAVE] WARNING – run {run_idx + 1} save failed: {exc}")

            # Xử lý sự kiện sau mỗi lần chạy
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested after run. Stopping.")
                    self.running = False
                    break
                elif ev.type == pygame.KEYDOWN:
                    try:
                        self._on_keydown(ev)
                    except Exception:
                        pass

            if not self.running:
                break

        # Lấy run tốt nhất để hiển thị: ưu tiên thành công, không có thì lấy thất bại tốt nhất
        best_run = best_success_run if best_success_run is not None else best_failed_run

        # Tính các thống kê tổng hợp
        avg_len = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
        actual_runs = len(run_records)
        avg_time = total_time / actual_runs if actual_runs > 0 else 0.0
        avg_fitness = (
            sum(fitness_values) / len(fitness_values) if fitness_values else 0.0
        )

        # Hiển thị đường đi tốt nhất trên màn hình
        self.current_path = list(best_run["path"]) if best_run else None

        # ─── Tạo file Excel tổng kết batch ───
        wb = Workbook()
        ws_results = wb.active
        ws_results.title = "Results"

        # Cột dữ liệu cần xuất
        result_cols = [
            "Run_ID",
            "Success",
            "Path_Length",
            "Total_Distance",
            "Total_Waypoint",
            "Total_Angle",
            "Min_Angle",
            "Max_Angle",
            "Average_Angle",
            "Min_Clearance",
            "TOTAL_FITNESS",
            "Execution_Time_s",
            "Path",
        ]
        ws_results.append(result_cols)  # Hàng header

        for rec in run_records:
            ws_results.append(
                [rec.get(col) for col in result_cols]
            )  # Từng hàng dữ liệu

        # Sheet tổng kết
        ws_summary = wb.create_sheet("Summary")
        ws_summary.append(["Metric", "Value"])
        for row in [
            ("Algorithm", self.selected_algorithm),
            ("Total runs", run_count),
            ("Successful runs", successful_runs),
            ("Success rate", successful_runs / run_count if run_count else 0.0),
            ("Average path length", avg_len),
            ("Average fitness", avg_fitness),
            ("Average time (s)", avg_time),
            ("Total time (s)", total_time),
            ("Best run", best_run["Run_ID"] if best_run else "N/A"),
            ("Best fitness", best_run["TOTAL_FITNESS"] if best_run else "N/A"),
            ("Best path length", best_run["Path_Length"] if best_run else "N/A"),
        ]:
            ws_summary.append(list(row))

        # Đặt tên file Excel và lưu
        algo_safe = "".join(
            c if (c.isalnum() or c in " _") else "_" for c in self.selected_algorithm
        ).replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = output_dir / f"{timestamp}_{algo_safe}.xlsx"
        wb.save(out_file)

        batch_end_time = self._now_str()

        # In báo cáo tổng kết batch ra console
        print_batch_summary_report(
            algo_name=self.selected_algorithm,
            map_name=self.map_name,
            batch_start_time=batch_start_time,
            batch_end_time=batch_end_time,
            run_count=run_count,
            successful_runs=successful_runs,
            total_time=total_time,
            excel_path=str(out_file),
            best_run=best_run,
            run_records=run_records,
        )

        # Hiển thị hộp thoại tóm tắt kết quả batch
        if successful_runs > 0:
            msg = (
                f"Runs: {run_count}\n"
                f"Success: {successful_runs}/{run_count}\n"
                f"Avg path length: {avg_len:.2f}\n"
                f"Avg fitness: {avg_fitness:.4f}\n"
                f"Avg time: {avg_time:.4f} s\n"
                f"Best run: {best_run['Run_ID']}\n"
                f"Excel: {out_file}"
            )
        else:
            msg = (
                f"Runs: {run_count}\n"
                f"Success: 0/{run_count}\n"
                f"No successful path was found.\n"
                f"Displaying the best failed path.\n"
                f"Best run: {best_run['Run_ID'] if best_run else 'N/A'}\n"
                f"Excel: {out_file}"
            )

        messagebox.showinfo("Batch Test", msg)

        # Xử lý sự kiện sau khi hộp thoại đóng
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                try:
                    self._on_keydown(ev)
                except Exception:
                    pass

    def _stop_simulation(self) -> None:
        """Hook dừng simulation (hiện tại không làm gì, dành cho mở rộng sau)."""
        return

    def _open_settings_dialog(self) -> None:
        """Mở hộp thoại cài đặt kích thước bản đồ và ô lưới."""
        dialog = SettingsDialog(
            self.tk_root, GRID_MAP_WIDTH, GRID_MAP_HEIGHT, GRID_CELL_SIZE
        )

        self.tk_root.wait_window(dialog)
        if dialog.result:
            width, height, cell_size = dialog.result
            self._resize_grid(width, height, cell_size)

    # ─────────────────────────────────────────────
    #  TÍNH LAYOUT VÀ RESIZE
    # ─────────────────────────────────────────────

    def _recalc_layout(self) -> None:
        """
        Tính lại vị trí offset của lưới trên màn hình.
        Căn giữa lưới trong vùng hiển thị (trừ panel menu và thanh mode).
        """
        map_w = self.grid_map.width * self.cell_size
        map_h = self.grid_map.height * self.cell_size

        avail_w = WINDOW_WIDTH - NAV_WIDTH  # Chiều rộng vùng hiển thị khả dụng
        avail_h = WINDOW_HEIGHT - MODE_HEIGHT  # Chiều cao vùng hiển thị khả dụng

        axis_label_w, axis_label_h = (
            self._axis_label_margins()
        )  # Biên cho nhãn trục tọa độ
        gap = 8  # Khoảng cách giữa nhãn trục và lưới

        content_w = map_w + axis_label_w + gap  # Tổng chiều rộng nội dung
        content_h = map_h + axis_label_h + gap  # Tổng chiều cao nội dung

        # Tính origin (góc trên trái) sao cho nội dung căn giữa
        origin_x = NAV_WIDTH + max(0, (avail_w - content_w) // 2)
        origin_y = MODE_HEIGHT + max(0, (avail_h - content_h) // 2)

        # Tính vị trí thực sự của góc trên trái lưới (sau nhãn trục)
        self.grid_offset_x = origin_x + axis_label_w + gap
        self.grid_offset_y = origin_y + axis_label_h + gap

    def _resize_grid(self, width: int, height: int, cell_size: int) -> None:
        """Thay đổi kích thước lưới và cập nhật lại toàn bộ layout."""
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_map.resize(width=self.width, height=self.height)  # Reset bản đồ
        self.current_path = None
        self.all_paths = {}
        self._stop_simulation()
        self._recalc_layout()  # Tính lại vị trí lưới

    # ─────────────────────────────────────────────
    #  VẼ GIAO DIỆN
    # ─────────────────────────────────────────────

    def _draw_ui(self) -> None:
        """Vẽ toàn bộ giao diện: nền, panel menu, thanh trạng thái, lưới."""
        self.screen.fill(WHITE)  # Tô nền trắng
        self._draw_nav_panel()  # Vẽ panel menu bên trái
        self._draw_status_bar()  # Vẽ thanh trạng thái trên cùng
        self._draw_grid()  # Vẽ lưới bản đồ và đường đi
        pygame.display.flip()  # Cập nhật màn hình (double buffering)

    def _draw_nav_panel(self) -> None:
        """Vẽ panel menu bên trái: tiêu đề MENU và các phím tắt."""
        pygame.draw.rect(self.screen, WHITE, (0, 0, NAV_WIDTH, NAV_HEIGHT))  # Nền trắng
        pygame.draw.line(
            self.screen, BLACK, (NAV_WIDTH, 0), (NAV_WIDTH, NAV_HEIGHT), 2
        )  # Đường kẻ phân cách

        Text(
            self.screen, NAV_OFFSET_X, NAV_OFFSET_Y, BLACK, "MENU", size=LARGE_TEXT_SIZE
        ).draw_text()

        y = NAV_OFFSET_Y + 40
        for item in NAV_MENU:
            Text(self.screen, NAV_OFFSET_X, y, BLACK, item).draw_text()
            y += 30  # Cách nhau 30px theo chiều dọc

    def _draw_status_bar(self) -> None:
        """Vẽ thanh trạng thái: chế độ hiện tại, thuật toán, và chú thích màu."""
        Text(
            self.screen,
            MODE_OFFSET_X,
            MODE_OFFSET_Y,
            BLACK,
            f"Mode: {self.mode} | Alg: {self.selected_algorithm}",
        ).draw_text()

        # Đường kẻ phân cách thanh trạng thái và vùng lưới
        pygame.draw.line(
            self.screen,
            BLACK,
            (NAV_WIDTH, MODE_HEIGHT),
            (WINDOW_WIDTH, MODE_HEIGHT),
            2,
        )

        try:
            # Vẽ chú thích màu (legend) cho từng thuật toán ở góc trên phải
            legend_items = [
                (name, self.algorithm_colors[name])
                for name in self.algorithm_names
                if name in self.algorithm_colors
            ]
            if not legend_items:
                return

            pad = 4
            lgd_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)
            box_sz = SMALL_TEXT_SIZE - 4  # Kích thước ô màu trong legend

            # Tính tổng chiều rộng legend
            total_w = pad
            for name, _ in legend_items:
                total_w += box_sz + 4 + lgd_font.size(name)[0] + pad

            lgd_h = box_sz + pad * 2
            lgd_top = (
                MODE_HEIGHT - lgd_h
            ) // 2  # Căn giữa theo chiều dọc trong thanh mode
            lgd_left = WINDOW_WIDTH - total_w - 10  # Căn phải

            # Vẽ nền bán trong suốt cho legend
            surf = pygame.Surface((total_w, lgd_h), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 180))
            self.screen.blit(surf, (lgd_left, lgd_top))

            cx = lgd_left + pad
            cy = lgd_top + pad
            for name, color in legend_items:
                pygame.draw.rect(self.screen, color, (cx, cy, box_sz, box_sz))  # Ô màu
                label = lgd_font.render(name, True, BLACK)
                self.screen.blit(label, (cx + box_sz + 4, cy))  # Tên thuật toán
                cx += box_sz + 4 + lgd_font.size(name)[0] + pad

        except Exception:
            pass  # Bỏ qua lỗi khi vẽ legend

    def _draw_grid(self) -> None:
        """Vẽ toàn bộ lưới: ô, đường đi, preview kéo chuột, và trục tọa độ."""
        # Vẽ từng ô lưới
        for row in range(self.grid_map.height):
            for col in range(self.grid_map.width):
                rect = (
                    self.grid_offset_x + col * self.cell_size,
                    self.grid_offset_y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                val = self.grid_map.grid[row][
                    col
                ]  # Giá trị ô: FREE/OBSTACLE/START/GOAL

                # Tô màu ô theo loại
                if val == GridMap.OBSTACLE:
                    pygame.draw.rect(self.screen, BLACK, rect)  # Chướng ngại vật: đen
                elif val == GridMap.START:
                    pygame.draw.rect(self.screen, GREEN, rect)  # Điểm Start: xanh lá
                elif val == GridMap.GOAL:
                    pygame.draw.rect(self.screen, RED, rect)  # Điểm Goal: đỏ
                else:
                    pygame.draw.rect(self.screen, WHITE, rect)  # Ô tự do: trắng

                # Hiển thị giá trị số tại tâm ô — chỉ khi cell đủ lớn
                if self.cell_size >= 12:
                    # Màu chữ tương phản với nền của từng loại cell
                    _TEXT_COLOR = {
                        GridMap.FREE: BLACK,
                        GridMap.OBSTACLE: WHITE,
                        GridMap.START: BLACK,
                        GridMap.GOAL: BLACK,
                    }
                    text_color = _TEXT_COLOR.get(val, MEDIUM)
                    label = pygame.font.SysFont("Sans-serif", 20).render(
                        str(val), True, text_color
                    )
                    lw, lh = label.get_size()
                    lx = rect[0] + (self.cell_size - lw) // 2
                    ly = rect[1] + (self.cell_size - lh) // 2
                    self.screen.blit(label, (lx, ly))

                pygame.draw.rect(self.screen, LIGHT, rect, 1)  # Viền ô: xám nhạt

        # Vẽ đường đi (1 thuật toán hoặc tất cả)
        if self.selected_algorithm == "All" and self.all_paths:
            for name, pts in self.all_paths.items():
                if not pts or len(pts) <= 1:
                    continue
                color = self.algorithm_colors.get(name, BLUE)
                self._draw_path_lines(pts, color)

        else:
            pts = self.current_path or []
            if pts and len(pts) > 1:
                self._draw_path_lines(pts, BLUE)

        # Vẽ preview các ô đang kéo chuột (viền xám đậm)
        if (
            self.is_dragging
            and self.drag_start is not None
            and self.drag_end is not None
        ):
            for x, y in self._bresenham_line(self.drag_start, self.drag_end):
                pygame.draw.rect(
                    self.screen,
                    MEDIUM,
                    (
                        self.grid_offset_x + x * self.cell_size,
                        self.grid_offset_y + y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                    2,
                )

        self._draw_axes()  # Vẽ trục tọa độ và nhãn số

    def _draw_path_lines(
        self,
        pts: list[tuple[float, float]],
        color: tuple[int, int, int],
    ) -> None:
        """Vẽ đường đi dưới dạng đoạn thẳng nối các điểm liên tiếp."""
        for i in range(len(pts) - 1):
            # Tính tọa độ pixel tâm ô cho điểm đầu và điểm cuối đoạn
            sx = self.grid_offset_x + pts[i][0] * self.cell_size + self.cell_size // 2
            sy = self.grid_offset_y + pts[i][1] * self.cell_size + self.cell_size // 2
            ex = (
                self.grid_offset_x
                + pts[i + 1][0] * self.cell_size
                + self.cell_size // 2
            )
            ey = (
                self.grid_offset_y
                + pts[i + 1][1] * self.cell_size
                + self.cell_size // 2
            )

            pygame.draw.line(self.screen, color, (sx, sy), (ex, ey), 2)

    def _draw_path_nodes(
        self,
        pts: list[tuple[float, float]],
        color: tuple[int, int, int],
    ) -> None:
        """Vẽ các điểm nút (waypoint) trên đường đi dưới dạng hình tròn."""
        r = max(3, self.cell_size // 6)  # Bán kính tỷ lệ với kích thước ô

        for x, y in pts:
            cx = self.grid_offset_x + x * self.cell_size + self.cell_size // 2
            cy = self.grid_offset_y + y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, color, (cx, cy), r)  # Vòng ngoài màu đường
            pygame.draw.circle(
                self.screen, WHITE, (cx, cy), max(1, r - 2)
            )  # Vòng trong trắng (viền)

    def _draw_axes(self) -> None:
        """Vẽ trục tọa độ X (trên) và Y (trái) với các tick và nhãn số (bước 5)."""
        map_w = self.grid_map.width * self.cell_size
        map_h = self.grid_map.height * self.cell_size
        axis_label_w, _ = self._axis_label_margins()
        tick_len = 6  # Chiều dài tick mark (pixel)
        label_gap = 6  # Khoảng cách từ tick tới nhãn số
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        # Các điểm mốc của lưới
        gx = self.grid_offset_x  # Cạnh trái lưới
        gy = self.grid_offset_y  # Cạnh trên lưới
        gr = gx + map_w  # Cạnh phải lưới
        gb = gy + map_h  # Cạnh dưới lưới

        # Vẽ 2 đường trục chính
        pygame.draw.line(
            self.screen, BLACK, (gx, gy), (gx, gb), 2
        )  # Trục Y (dọc, bên trái)
        pygame.draw.line(
            self.screen, BLACK, (gx, gy), (gr, gy), 2
        )  # Trục X (ngang, trên cùng)

        # Vẽ tick và nhãn trục X (theo cột, bước 5)
        max_x_tick = self.grid_map.width - (self.grid_map.width % 5)
        for coord in range(0, max_x_tick + 1, 5):
            tick_x = gx + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (tick_x, gy - tick_len),
                (tick_x, gy),
                1,
            )
            lbl = label_font.render(str(coord), True, BLACK)
            self.screen.blit(
                lbl,
                (
                    tick_x - lbl.get_width() // 2,
                    gy - tick_len - label_gap - lbl.get_height(),
                ),
            )

        # Vẽ tick và nhãn trục Y (theo hàng, bước 5)
        max_y_tick = self.grid_map.height - (self.grid_map.height % 5)
        for coord in range(0, max_y_tick + 1, 5):
            tick_y = gy + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (gx - tick_len, tick_y),
                (gx, tick_y),
                1,
            )
            lbl = label_font.render(str(coord), True, BLACK)
            self.screen.blit(
                lbl,
                (
                    gx - axis_label_w + tick_len + label_gap - 10,
                    tick_y - lbl.get_height() // 2,
                ),
            )

    def _axis_label_margins(self) -> tuple[float, float]:
        """
        Tính biên (margin) cần thiết cho nhãn số trên trục X và Y.
        Trả về (margin_w, margin_h) tính theo pixel.
        """
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        # Nhãn lớn nhất có thể xuất hiện trên mỗi trục
        max_x_label = self.grid_map.width - (self.grid_map.width % 5)
        max_y_label = self.grid_map.height - (self.grid_map.height % 5)

        # Lấy chiều rộng lớn nhất của nhãn số
        max_lbl_w = max(
            label_font.size(str(max_x_label))[0],
            label_font.size(str(max_y_label))[0],
        )

        tick_len = 6
        label_gap = 6
        margin_w = max_lbl_w + tick_len + label_gap + 2  # Biên trục Y
        margin_h = label_font.get_height() + tick_len + label_gap  # Biên trục X

        return margin_w, margin_h


if __name__ == "__main__":
    app = App()
    app.run()
