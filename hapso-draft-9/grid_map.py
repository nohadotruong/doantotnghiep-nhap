# Import các hằng số chiều rộng và chiều cao mặc định từ file cấu hình
from config.parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH

import numpy as np  # Import thư viện numpy để xử lý mảng số học


class GridMap:
    # --- Các hằng số đại diện cho trạng thái của từng ô trong lưới ---
    FREE = 0  # Ô trống, có thể đi qua
    OBSTACLE = 1  # Ô chướng ngại vật, không thể đi qua
    START = 2  # Ô điểm xuất phát
    GOAL = 3  # Ô điểm đích

    def __init__(
        self, width: int = GRID_MAP_WIDTH, height: int = GRID_MAP_HEIGHT
    ) -> None:
        self.width = width  # Lưu chiều rộng lưới (số cột)
        self.height = height  # Lưu chiều cao lưới (số hàng)

        # Khởi tạo lưới 2D (height hàng × width cột), tất cả ô đều FREE (= 0)
        # grid[y][x] — trục y là hàng (dọc), trục x là cột (ngang)
        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]

        self.start: tuple[int, int] | None = (
            None  # Tọa độ (x, y) điểm Start, ban đầu chưa đặt
        )
        self.goal: tuple[int, int] | None = (
            None  # Tọa độ (x, y) điểm Goal, ban đầu chưa đặt
        )

        # Tập hợp (set) lưu tọa độ các ô chướng ngại vật — dùng set để tra cứu O(1)
        self._obstacle_set: set[tuple[int, int]] = set()

    def rebuild_obstacle_set(self) -> None:
        """Xây dựng lại _obstacle_set bằng cách quét toàn bộ lưới.
        Dùng khi lưới bị chỉnh sửa trực tiếp mà không qua set_obstacle()."""
        self._obstacle_set = set()  # Xóa set cũ

        # Duyệt từng ô trong lưới
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    self._obstacle_set.add((x, y))  # Thêm ô có chướng ngại vật vào set

    def get_obstacles(self) -> list[tuple[int, int]]:
        """Trả về danh sách (list) tọa độ tất cả các ô chướng ngại vật."""
        return list(self._obstacle_set)

    def get_obstacle_set(self) -> set[tuple[int, int]]:
        """Trả về bản sao của set chướng ngại vật (tránh bên ngoài sửa trực tiếp)."""
        return set(self._obstacle_set)

    def get_obstacle_count(self) -> int:
        """Trả về tổng số ô chướng ngại vật hiện có."""
        return len(self.get_obstacles())

    def get_obstacles_as_centers(self) -> np.ndarray:
        """Trả về tọa độ tâm của từng ô chướng ngại vật dưới dạng mảng numpy.
        Mỗi ô có kích thước 1×1, nên tâm ô (x, y) là (x + 0.5, y + 0.5)."""
        return np.array([[x + 0.5, y + 0.5] for x, y in self.get_obstacles()])

    def is_inside(self, x: int, y: int) -> bool:
        """Kiểm tra tọa độ (x, y) có nằm trong giới hạn của lưới không."""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        """Kiểm tra ô (x, y) có phải chướng ngại vật không.
        Ô nằm ngoài lưới cũng được coi là chướng ngại vật (không thể đi qua)."""
        if not self.is_inside(x, y):
            return True  # Ngoài biên → coi như chướng ngại vật

        return (x, y) in self._obstacle_set  # Tra cứu O(1) trong set

    def set_start(self, x: int, y: int) -> bool:
        """Đặt điểm Start tại (x, y).
        Trả về False nếu tọa độ không hợp lệ (ngoài biên hoặc là chướng ngại vật)."""
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False  # Vị trí không hợp lệ

        if self.start is not None:
            old_x, old_y = self.start  # Lấy tọa độ Start cũ

            # Xóa trạng thái START của ô cũ, trả về FREE
            if self.grid[old_y][old_x] == self.START:
                self.grid[old_y][old_x] = self.FREE

        self.start = (x, y)  # Cập nhật tọa độ Start mới
        self.grid[y][x] = self.START  # Đánh dấu ô mới trên lưới

        return True

    def set_goal(self, x: int, y: int) -> bool:
        """Đặt điểm Goal tại (x, y).
        Trả về False nếu tọa độ không hợp lệ (ngoài biên hoặc là chướng ngại vật)."""
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False  # Vị trí không hợp lệ

        if self.goal is not None:
            old_x, old_y = self.goal  # Lấy tọa độ Goal cũ

            # Xóa trạng thái GOAL của ô cũ, trả về FREE
            if self.grid[old_y][old_x] == self.GOAL:
                self.grid[old_y][old_x] = self.FREE

        self.goal = (x, y)  # Cập nhật tọa độ Goal mới
        self.grid[y][x] = self.GOAL  # Đánh dấu ô mới trên lưới

        return True

    def set_obstacle(self, x: int, y: int, value: bool | None = None) -> bool:
        """Đặt hoặc xóa chướng ngại vật tại (x, y).
        - value=True  → đặt chướng ngại vật
        - value=False → xóa chướng ngại vật
        - value=None  → đảo trạng thái (toggle)
        Trả về False nếu tọa độ không hợp lệ hoặc là ô Start/Goal."""
        if not self.is_inside(x, y):
            return False  # Ngoài biên

        # Không cho phép đặt chướng ngại vật đè lên Start hoặc Goal
        if (x, y) == self.start or (x, y) == self.goal:
            return False

        if value is None:
            # Toggle: nếu đang là OBSTACLE thì xóa, ngược lại thì đặt
            currently = self.grid[y][x] == self.OBSTACLE
            value = not currently

        if value:
            # Đặt chướng ngại vật
            self.grid[y][x] = self.OBSTACLE
            self._obstacle_set.add((x, y))
        else:
            # Xóa chướng ngại vật
            self.grid[y][x] = self.FREE
            self._obstacle_set.discard(
                (x, y)
            )  # discard không báo lỗi nếu key không tồn tại

        return True

    def resize(self, width: int, height: int) -> None:
        """Thay đổi kích thước lưới. Toàn bộ dữ liệu cũ (lưới, Start, Goal, chướng ngại vật) bị xóa sạch."""
        self.width = width  # Cập nhật chiều rộng mới
        self.height = height  # Cập nhật chiều cao mới

        # Tạo lại lưới mới hoàn toàn trống
        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]

        self.start = None  # Xóa điểm Start
        self.goal = None  # Xóa điểm Goal

        self._obstacle_set = set()  # Xóa toàn bộ chướng ngại vật
