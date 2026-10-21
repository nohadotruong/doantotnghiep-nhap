# ============================================================
# RRT* (Rapidly-exploring Random Tree Star) Path Planning
# Thuật toán lập kế hoạch đường đi tối ưu dựa trên cây ngẫu nhiên.
# RRT* mở rộng RRT thông thường bằng cách thêm bước rewire để
# liên tục cải thiện chi phí của các node đã có trong cây,
# đảm bảo hội tụ về đường đi tối ưu khi số iteration đủ lớn.
# ============================================================

# --- Import tham số cấu hình từ file config ---
from config.parameter import (
    MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu đến chướng ngại vật
    RRT_STAR_GOAL_SAMPLE_RATE,  # Xác suất lấy mẫu thẳng vào điểm đích
    RRT_STAR_MAX_ITER,  # Số vòng lặp tối đa của thuật toán
    RRT_STAR_MAX_SAMPLE_ATTEMPTS,  # Số lần thử tối đa để lấy một điểm mẫu hợp lệ
    RRT_STAR_NEIGHBOR_RADIUS,  # Bán kính tìm kiếm láng giềng mặc định
    RRT_STAR_STEP_SIZE,  # Độ dài bước di chuyển tối đa mỗi lần mở rộng cây
)

# --- Import các module nội bộ ---
from grid_map import GridMap  # Lớp quản lý bản đồ lưới (obstacle, boundary, start/goal)
from typing import Optional  # Dùng để khai báo kiểu trả về có thể là None

# --- Import hàm tiện ích ---
from utils import euclidean_distance, min_distance_line_to_obstacle

# euclidean_distance         : Tính khoảng cách Euclidean giữa 2 điểm
# min_distance_line_to_obstacle : Tính khoảng cách ngắn nhất từ đoạn thẳng đến chướng ngại vật gần nhất

# --- Import thư viện chuẩn ---
import math  # Dùng cho sqrt, log trong tính toán hình học
import random  # Dùng cho lấy mẫu ngẫu nhiên trong không gian


# ============================================================
# CLASS: RRTStarNode
# Đại diện cho một node (nút) trong cây RRT*.
# Mỗi node lưu tọa độ, node cha, và tổng chi phí từ điểm start.
# ============================================================
class RRTStarNode:
    def __init__(
        self,
        x: int,  # Tọa độ x của node trên lưới
        y: int,  # Tọa độ y của node trên lưới
        came_from: Optional[
            "RRTStarNode"
        ] = None,  # Node cha trong cây (None nếu là root)
        cost: float = 0.0,  # Tổng chi phí đường đi từ start đến node này
    ) -> None:
        self.x = x  # Gán tọa độ x
        self.y = y  # Gán tọa độ y
        self.came_from = came_from  # Gán node cha (dùng để truy vết đường đi)
        self.cost = cost  # Gán chi phí tích lũy từ start


# ============================================================
# CLASS: RRTStar
# Lớp chính thực thi thuật toán RRT*.
# Nhận vào GridMap và các tham số điều chỉnh hành vi thuật toán.
# ============================================================
class RRTStar:
    def __init__(
        self,
        grid_map: GridMap,  # Bản đồ lưới chứa thông tin chướng ngại vật, start, goal
        max_iter: int = RRT_STAR_MAX_ITER,  # Số vòng lặp tối đa
        step_size: int = RRT_STAR_STEP_SIZE,  # Bước mở rộng tối đa mỗi lần steer
        goal_sample_rate: float = RRT_STAR_GOAL_SAMPLE_RATE,  # Xác suất lấy mẫu vào goal
        max_sample_attempts: int = RRT_STAR_MAX_SAMPLE_ATTEMPTS,  # Giới hạn thử lấy mẫu
        neighbor_radius: float = RRT_STAR_NEIGHBOR_RADIUS,  # Bán kính tìm láng giềng ban đầu
        min_clearance: float = MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu đến vật cản
    ) -> None:
        self.grid_map = grid_map  # Lưu bản đồ lưới
        self.start = self.grid_map.start  # Lấy điểm bắt đầu từ bản đồ
        self.goal = self.grid_map.goal  # Lấy điểm đích từ bản đồ

        self.max_iter = max_iter  # Lưu số vòng lặp tối đa
        self.step_size = step_size  # Lưu kích thước bước steer
        self.goal_sample_rate = goal_sample_rate  # Lưu xác suất lấy mẫu goal
        self.max_sample_attempts = max_sample_attempts  # Lưu giới hạn thử lấy mẫu
        self.neighbor_radius = neighbor_radius  # Lưu bán kính tìm láng giềng
        self.min_clearance = float(
            min_clearance
        )  # Ép kiểu float để đảm bảo so sánh chính xác

    # --------------------------------------------------------
    # Hàm chính: Lập kế hoạch đường đi từ start đến goal.
    # Trả về danh sách các điểm tọa độ tạo thành đường đi,
    # hoặc None nếu không tìm được đường.
    # --------------------------------------------------------
    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.grid_map.start  # Lấy tọa độ điểm start
        goal = self.grid_map.goal  # Lấy tọa độ điểm goal

        # Kiểm tra start hoặc goal chưa được thiết lập
        if start is None or goal is None:
            return None

        # Kiểm tra start có nằm trong bản đồ và không trùng chướng ngại vật
        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        # Kiểm tra goal có nằm trong bản đồ và không trùng chướng ngại vật
        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        # Trường hợp đặc biệt: start và goal trùng nhau
        if start == goal:
            return [start, goal]

        # Khởi tạo cây với node gốc tại vị trí start (cost = 0)
        nodes = [RRTStarNode(start[0], start[1])]

        # Biến lưu node goal tốt nhất tìm được (chi phí thấp nhất)
        best_goal_node: Optional[RRTStarNode] = None

        # Vòng lặp chính của RRT*: lặp tối đa max_iter lần
        for _ in range(self.max_iter):

            # Bước 1: Lấy mẫu ngẫu nhiên một điểm trong không gian
            sample_point = self._sample_point(goal)

            # Bước 2: Tìm node trong cây gần nhất với điểm mẫu
            nearest_node = self._nearest_node(nodes, sample_point)

            # Bước 3: Steer — di chuyển từ nearest_node về hướng sample_point với step_size
            new_point = self._steer(nearest_node, sample_point)

            # Bỏ qua nếu steer không tạo ra điểm hợp lệ (ra ngoài bản đồ, trùng vật cản...)
            if new_point is None:
                continue

            # Bước 4: Tìm tất cả node trong cây nằm trong bán kính láng giềng của new_point
            neighbors = self._near_nodes(nodes, new_point)

            # Bước 5: Chọn node cha tối ưu (chi phí thấp nhất, không va chạm)
            parent_node = self._choose_parent(neighbors, nearest_node, new_point)

            # Bỏ qua nếu không có node cha hợp lệ
            if parent_node is None:
                continue

            # Kiểm tra đoạn từ parent đến new_point có va chạm không (lần kiểm tra cuối)
            if self._segment_has_collision((parent_node.x, parent_node.y), new_point):
                continue

            # Tính chi phí của new_node = chi phí parent + khoảng cách từ parent đến new_point
            new_cost = parent_node.cost + euclidean_distance(
                (parent_node.x, parent_node.y), new_point
            )

            # Tạo node mới và thêm vào cây
            new_node = RRTStarNode(new_point[0], new_point[1], parent_node, new_cost)
            nodes.append(new_node)

            # Bước 6: Rewire — kiểm tra các láng giềng có thể đi qua new_node với chi phí thấp hơn
            self._rewire(neighbors, new_node, nodes)

            # Bước 7: Kiểm tra xem new_node có đủ gần goal để kết nối không
            if self._is_goal_reached(new_node, goal):

                # Tính tổng chi phí nếu kết nối new_node với goal
                goal_cost = new_node.cost + euclidean_distance(
                    (new_node.x, new_node.y), goal
                )

                # Cập nhật best_goal_node nếu đây là đường đến goal tốt hơn
                if best_goal_node is None or goal_cost < best_goal_node.cost:

                    # Chỉ chấp nhận nếu đoạn cuối (new_node → goal) không có va chạm
                    if not self._segment_has_collision((new_node.x, new_node.y), goal):
                        best_goal_node = RRTStarNode(
                            goal[0], goal[1], new_node, goal_cost
                        )

        # Không tìm thấy đường đi nào đến goal sau tất cả các iteration
        if best_goal_node is None:
            return None

        # Truy vết ngược từ goal về start để tạo đường đi hoàn chỉnh
        return self._reconstruct_path(best_goal_node)

    # --------------------------------------------------------
    # Lấy mẫu một điểm trong không gian.
    # Có xác suất goal_sample_rate lấy thẳng điểm goal (định hướng cây về đích).
    # Ngược lại, lấy mẫu ngẫu nhiên một điểm không phải chướng ngại vật.
    # --------------------------------------------------------
    def _sample_point(self, goal: tuple[int, int]) -> tuple[int, int]:

        # Với xác suất goal_sample_rate, lấy mẫu thẳng tại goal để kéo cây về đích
        if random.random() < self.goal_sample_rate:
            return goal

        # Thử lấy mẫu ngẫu nhiên tối đa max_sample_attempts lần
        for _ in range(self.max_sample_attempts):
            x = random.randint(0, self.grid_map.width - 1)  # x ngẫu nhiên trong bản đồ
            y = random.randint(0, self.grid_map.height - 1)  # y ngẫu nhiên trong bản đồ

            # Chấp nhận điểm nếu nằm trong bản đồ và không phải chướng ngại vật
            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                return (x, y)

        # Fallback: nếu không lấy được điểm hợp lệ, trả về goal
        return goal

    # --------------------------------------------------------
    # Tìm node trong cây gần nhất với điểm cho trước.
    # Dùng hàm min với key là khoảng cách Euclidean.
    # --------------------------------------------------------
    def _nearest_node(
        self,
        nodes: list[RRTStarNode],  # Danh sách tất cả node trong cây
        point: tuple[int, int],  # Điểm cần tìm node gần nhất
    ) -> RRTStarNode:
        # Duyệt toàn bộ cây, trả về node có khoảng cách nhỏ nhất đến point
        return min(nodes, key=lambda node: euclidean_distance((node.x, node.y), point))

    # --------------------------------------------------------
    # Steer: Di chuyển từ from_node về hướng to_point một khoảng step_size.
    # Nếu khoảng cách đã nhỏ hơn step_size, đi thẳng đến to_point.
    # Trả về None nếu điểm mới không hợp lệ.
    # --------------------------------------------------------
    def _steer(
        self,
        from_node: RRTStarNode,  # Node xuất phát
        to_point: tuple[int, int],  # Điểm đích cần steer tới
    ) -> Optional[tuple[int, int]]:

        # Tính vector hướng từ from_node đến to_point
        delta_x = to_point[0] - from_node.x
        delta_y = to_point[1] - from_node.y

        # Tính khoảng cách thực tế giữa 2 điểm
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        # Nếu 2 điểm quá gần nhau (gần như trùng), bỏ qua để tránh chia cho 0
        if distance < 1e-9:
            return None

        # Nếu khoảng cách nhỏ hơn step_size, lấy thẳng to_point làm điểm mới
        if distance <= self.step_size:
            new_x, new_y = to_point

        else:
            # Tính tỉ lệ để đi đúng step_size theo hướng to_point
            ratio = self.step_size / distance

            # Tính tọa độ điểm mới sau khi di chuyển step_size
            new_x = int(round(from_node.x + delta_x * ratio))
            new_y = int(round(from_node.y + delta_y * ratio))

        # Loại bỏ nếu điểm mới nằm ngoài biên bản đồ
        if not self.grid_map.is_inside(new_x, new_y):
            return None

        # Loại bỏ nếu điểm mới trùng với chướng ngại vật
        if self.grid_map.is_obstacle(new_x, new_y):
            return None

        # Loại bỏ nếu điểm mới trùng với vị trí hiện tại (không tiến được)
        if new_x == from_node.x and new_y == from_node.y:
            return None

        return (new_x, new_y)  # Trả về điểm mới hợp lệ

    # --------------------------------------------------------
    # Tìm tất cả node trong cây nằm trong bán kính láng giềng của point.
    # Bán kính được tính adaptive theo lý thuyết RRT* để đảm bảo tính tối ưu,
    # nhưng được giới hạn không vượt quá step_size * 3.
    # --------------------------------------------------------
    def _near_nodes(
        self,
        nodes: list[RRTStarNode],  # Danh sách tất cả node trong cây
        point: tuple[int, int],  # Điểm trung tâm cần tìm láng giềng xung quanh
    ) -> list[RRTStarNode]:

        node_count = len(nodes)  # Số lượng node hiện có trong cây

        if node_count <= 1:
            # Nếu cây chỉ có 1 node, dùng bán kính mặc định từ config
            radius = self.neighbor_radius

        else:
            # Công thức adaptive radius của RRT*:
            # r = gamma * sqrt(log(n+1) / (n+1))
            # Đảm bảo vùng tìm kiếm thu hẹp dần khi cây dày đặc hơn
            adaptive_radius = 10.0 * math.sqrt(
                math.log(node_count + 1) / (node_count + 1)
            )

            # Giới hạn trên: không quá 3 lần step_size để tránh quét quá rộng
            radius = min(adaptive_radius, self.step_size * 3)

        # Trả về danh sách các node nằm trong bán kính radius quanh point
        return [
            node
            for node in nodes
            if euclidean_distance((node.x, node.y), point) <= radius
        ]

    # --------------------------------------------------------
    # Chọn node cha tối ưu cho new_point từ danh sách láng giềng.
    # Ưu tiên node có tổng chi phí (cost + khoảng cách đến new_point) nhỏ nhất
    # và đoạn nối không bị va chạm.
    # --------------------------------------------------------
    def _choose_parent(
        self,
        neighbors: list[RRTStarNode],  # Danh sách node láng giềng ứng viên
        nearest_node: RRTStarNode,  # Node gần nhất (fallback nếu neighbors rỗng)
        point: tuple[int, int],  # Điểm mới cần chọn cha
    ) -> Optional[RRTStarNode]:

        # Nếu không có láng giềng nào, dùng nearest_node làm ứng viên duy nhất
        candidates = neighbors if neighbors else [nearest_node]

        best_node = None  # Node cha tốt nhất tìm được
        best_cost = float("inf")  # Chi phí tốt nhất (khởi tạo vô cực)

        for node in candidates:

            # Bỏ qua node nếu đoạn thẳng nối đến point có va chạm
            if self._segment_has_collision((node.x, node.y), point):
                continue

            # Tính tổng chi phí: chi phí của node + khoảng cách từ node đến point
            cost = node.cost + euclidean_distance((node.x, node.y), point)

            # Cập nhật node cha tốt nhất nếu tìm được chi phí nhỏ hơn
            if cost < best_cost:
                best_cost = cost
                best_node = node

        return (
            best_node  # Trả về node cha tối ưu (hoặc None nếu không có ứng viên hợp lệ)
        )

    # --------------------------------------------------------
    # Rewire: Cải thiện cây bằng cách kiểm tra các node láng giềng.
    # Nếu đi qua new_node sẽ rẻ hơn đường hiện tại của neighbor,
    # cập nhật node cha của neighbor thành new_node.
    # --------------------------------------------------------
    def _rewire(
        self,
        neighbors: list[RRTStarNode],  # Các node láng giềng cần kiểm tra rewire
        new_node: RRTStarNode,  # Node mới vừa được thêm vào cây
        nodes: list[RRTStarNode],  # Toàn bộ cây (để propagate cost)
    ) -> None:
        for node in neighbors:

            # Bỏ qua nếu node đang là node cha của new_node (tránh vòng lặp)
            if node is new_node.came_from:
                continue

            # Bỏ qua nếu đoạn nối new_node → node bị va chạm
            if self._segment_has_collision((new_node.x, new_node.y), (node.x, node.y)):
                continue

            # Tính chi phí mới nếu node đi qua new_node
            new_cost = new_node.cost + euclidean_distance(
                (new_node.x, new_node.y), (node.x, node.y)
            )

            # Nếu đường qua new_node rẻ hơn, cập nhật cha và chi phí của node
            if new_cost < node.cost:
                node.came_from = new_node  # Đổi cha của node thành new_node
                node.cost = new_cost  # Cập nhật chi phí mới của node

                # Lan truyền chi phí mới xuống tất cả các node con phía sau
                self._propagate_cost(node, nodes)

    # --------------------------------------------------------
    # Lan truyền chi phí cập nhật từ node xuống toàn bộ cây con.
    # Được gọi sau khi rewire để đảm bảo mọi node con phản ánh chi phí mới.
    # --------------------------------------------------------
    def _propagate_cost(
        self,
        node: RRTStarNode,  # Node vừa được cập nhật chi phí
        nodes: list[RRTStarNode],  # Toàn bộ cây để tìm các node con
    ) -> None:
        for child in nodes:

            # Nếu child có node cha là node hiện tại, cập nhật chi phí của child
            if child.came_from is node:
                child.cost = node.cost + euclidean_distance(
                    (node.x, node.y), (child.x, child.y)
                )
                # Đệ quy: tiếp tục lan truyền xuống các node con của child
                self._propagate_cost(child, nodes)

    # --------------------------------------------------------
    # Kiểm tra xem node có đủ gần goal để kết nối trực tiếp không.
    # Điều kiện: khoảng cách đến goal ≤ step_size.
    # --------------------------------------------------------
    def _is_goal_reached(
        self,
        node: RRTStarNode,  # Node cần kiểm tra
        goal: tuple[int, int],  # Tọa độ điểm đích
    ) -> bool:
        # Trả về True nếu node nằm trong vùng step_size xung quanh goal
        return euclidean_distance((node.x, node.y), goal) <= self.step_size

    # --------------------------------------------------------
    # Kiểm tra đoạn thẳng giữa 2 điểm có vi phạm clearance không.
    # Dùng min_distance_line_to_obstacle từ utils để tính khoảng cách
    # từ đoạn thẳng đến chướng ngại vật gần nhất, rồi so sánh với min_clearance.
    # --------------------------------------------------------
    def _segment_has_collision(
        self,
        point_a: tuple[float, float],  # Điểm đầu của đoạn thẳng
        point_b: tuple[float, float],  # Điểm cuối của đoạn thẳng
    ) -> bool:
        # Nếu khoảng cách nhỏ hơn hoặc bằng min_clearance → coi là có va chạm
        if (
            min_distance_line_to_obstacle(point_a, point_b, self.grid_map)
            <= self.min_clearance
        ):
            return True

        return False  # Đoạn thẳng an toàn, không có va chạm

    # --------------------------------------------------------
    # Truy vết đường đi từ goal node về start bằng cách đi ngược qua came_from.
    # Sau đó đảo ngược danh sách để có thứ tự start → goal.
    # --------------------------------------------------------
    def _reconstruct_path(
        self,
        node: RRTStarNode,  # Node đích (goal node) để bắt đầu truy vết ngược
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []  # Danh sách điểm trên đường đi
        current: Optional[RRTStarNode] = node  # Bắt đầu từ goal node

        # Đi ngược qua chuỗi came_from cho đến khi đến root (came_from = None)
        while current is not None:
            path.append((current.x, current.y))  # Thêm tọa độ node hiện tại vào path
            current = current.came_from  # Nhảy lên node cha

        # Đảo ngược để path đi từ start đến goal
        path.reverse()
        return path
