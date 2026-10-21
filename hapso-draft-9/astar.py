# Import hằng số MIN_CLEARANCE (khoảng cách an toàn tối thiểu) từ file cấu hình
from config.parameter import (
    MIN_CLEARANCE,
)

# Import class GridMap đại diện cho bản đồ lưới (chứa vật cản, điểm đầu, điểm cuối)
from grid_map import GridMap

# Import Optional để khai báo kiểu trả về có thể là None (khi không tìm được đường)
from typing import Optional

# Import hàm tính khoảng cách Euclid và hàm kiểm tra khoảng cách từ đoạn thẳng đến vật cản
from utils import euclidean_distance, min_distance_line_to_obstacle

# Import module heapq để sử dụng hàng đợi ưu tiên (min-heap) — cốt lõi của A*
import heapq


class Astar:
    def __init__(
        self,
        grid_map: GridMap,  # Bản đồ lưới chứa thông tin vật cản
        min_clearance: float = MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu đến vật cản
    ) -> None:
        self.grid_map = grid_map  # Lưu tham chiếu đến bản đồ lưới
        self.start = self.grid_map.start  # Lấy tọa độ điểm bắt đầu từ bản đồ
        self.goal = self.grid_map.goal  # Lấy tọa độ điểm đích từ bản đồ

        self.min_clearance = float(
            min_clearance
        )  # Ép kiểu về float để đảm bảo tính toán chính xác

        # g_score[pos]: chi phí thực tế tích lũy từ start đến pos
        self.g_score: dict[tuple[float, float], float] = {}
        # f_score[pos]: tổng ước tính chi phí = g_score + heuristic (khoảng cách đến goal)
        self.f_score: dict[tuple[float, float], float] = {}

        # came_from[pos]: ô cha của pos — dùng để truy vết lại đường đi sau khi tìm xong
        self.came_from: dict[tuple[float, float], tuple[float, float]] = {}
        # visited: tập các ô đã được xử lý hoàn toàn (đã "đóng"), không xét lại
        self.visited: set[tuple[float, float]] = set()

        # open_set: hàng đợi ưu tiên chứa các ô đang chờ xét
        # Mỗi phần tử có dạng (f_score, h_score, g_score, pos)
        # Sắp xếp theo f_score tăng dần → ô có chi phí ước tính nhỏ nhất được xét trước
        self.open_set: list[tuple[float, float, float, tuple[float, float]]] = []

    def plan(self) -> Optional[list[tuple[float, float]]]:
        """Thực hiện tìm đường từ start đến goal. Trả về danh sách tọa độ đường đi, hoặc None nếu thất bại."""
        start = self.start
        goal = self.goal

        # Kiểm tra tính hợp lệ của điểm bắt đầu: phải nằm trong bản đồ và không phải vật cản
        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        # Kiểm tra tính hợp lệ của điểm đích: phải nằm trong bản đồ và không phải vật cản
        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        # Trường hợp đặc biệt: start và goal trùng nhau → đường đi chỉ gồm 1 điểm
        if start == goal:
            return [start, goal]

        # ── Khởi tạo lại trạng thái tìm kiếm ──────────────────────────────────
        self.came_from = {}  # Xóa bảng truy vết đường đi cũ
        self.g_score = {start: 0}  # Chi phí từ start đến start = 0
        start_h = euclidean_distance(
            start, goal
        )  # Heuristic h(start): ước tính khoảng cách đến goal
        self.f_score = {start: start_h}  # f(start) = g(start) + h(start) = 0 + h(start)
        self.visited = set()  # Tập ô đã xét (ban đầu rỗng)
        # Đưa start vào hàng đợi: (f, h, g, vị_trí)
        self.open_set = [(start_h, start_h, 0, start)]

        # ── Vòng lặp chính của A* ───────────────────────────────────────────────
        while self.open_set:
            # Lấy ra ô có f_score nhỏ nhất từ heap (ô tiềm năng nhất)
            _, _, g_curr, curr = heapq.heappop(self.open_set)

            # Bỏ qua nếu ô này đã được xử lý rồi
            # (có thể bị đẩy vào heap nhiều lần với g_score khác nhau)
            if curr in self.visited:
                continue

            # Đánh dấu ô hiện tại là đã xử lý
            self.visited.add(curr)

            # Nếu đến được đích → truy vết và trả về đường đi
            if curr == goal:
                return self._reconstruct_path(curr)

            # Duyệt qua tất cả các ô hàng xóm hợp lệ (8 hướng)
            for neighbor in self._get_neighbors(curr):
                # Bỏ qua ô đã xử lý
                if neighbor in self.visited:
                    continue

                # Kiểm tra khoảng cách an toàn: bước di chuyển curr→neighbor
                # phải không đi quá gần vật cản (nếu có bật tính năng này)
                if self.min_clearance > 0.0:
                    if (
                        min_distance_line_to_obstacle(curr, neighbor, self.grid_map)
                        <= self.min_clearance  # Đoạn thẳng vi phạm vùng an toàn → bỏ qua
                    ):
                        continue

                # Chi phí di chuyển từ curr sang neighbor (khoảng cách Euclid)
                # = 1.0 cho bước ngang/dọc, ≈1.414 cho bước chéo
                move_cost = euclidean_distance(curr, neighbor)

                # g tạm thời: chi phí thực tế nếu đi qua curr đến neighbor
                tentative_g = g_curr + move_cost

                # Cập nhật nếu đây là con đường tốt hơn đến neighbor
                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    # Ghi nhận curr là cha của neighbor trong đường đi tối ưu hiện tại
                    self.came_from[neighbor] = curr
                    # Cập nhật chi phí thực tế đến neighbor
                    self.g_score[neighbor] = tentative_g

                    # Tính heuristic: khoảng cách thẳng từ neighbor đến goal
                    neighbor_h = euclidean_distance(neighbor, goal)
                    # f(neighbor) = g(neighbor) + h(neighbor)
                    self.f_score[neighbor] = tentative_g + neighbor_h

                    # Đẩy neighbor vào hàng đợi để xét sau
                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], neighbor_h, tentative_g, neighbor),
                    )

        # Duyệt hết open_set mà không tìm được đích → không có đường đi
        return None

    def _get_neighbors(self, pos: tuple[float, float]) -> list[tuple[float, float]]:
        """Trả về danh sách các ô lân cận hợp lệ (8 hướng: ngang, dọc, chéo)."""
        # 8 hướng di chuyển: trái, phải, lên, xuống và 4 góc chéo
        directions = [
            (0, -1),  # Lên
            (0, 1),  # Xuống
            (-1, 0),  # Trái
            (1, 0),  # Phải
            (-1, -1),  # Chéo trên-trái
            (-1, 1),  # Chéo dưới-trái
            (1, -1),  # Chéo trên-phải
            (1, 1),  # Chéo dưới-phải
        ]

        px, py = pos  # Tọa độ ô hiện tại
        neighbors = []

        for dx, dy in directions:
            nx, ny = px + dx, py + dy  # Tọa độ ô lân cận theo hướng (dx, dy)

            # Chỉ thêm vào danh sách nếu ô nằm trong bản đồ VÀ không phải vật cản
            if self.grid_map.is_inside(nx, ny) and not self.grid_map.is_obstacle(
                nx, ny
            ):
                neighbors.append((nx, ny))

        return neighbors

    def _reconstruct_path(self, curr: tuple[float, float]) -> list[tuple[float, float]]:
        """Truy ngược từ goal về start qua bảng came_from để tái tạo đường đi."""
        path = [curr]  # Bắt đầu từ ô hiện tại (goal)

        # Theo chuỗi cha: curr → cha của curr → cha của cha → ... → start
        while curr in self.came_from:
            curr = self.came_from[curr]  # Lùi về ô cha
            path.append(curr)  # Thêm vào đường đi

        # Đảo ngược vì đang truy từ goal về start → cần thứ tự start → goal
        path.reverse()
        return path
