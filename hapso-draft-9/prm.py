# ============================================================
# PRM (Probabilistic Roadmap Method) Path Planning
# Thuật toán lập kế hoạch đường đi dựa trên bản đồ xác suất.
# PRM hoạt động theo 2 pha:
#   1. Learning phase: Lấy mẫu ngẫu nhiên các điểm trong không gian
#      tự do và kết nối chúng thành một roadmap (đồ thị).
#   2. Query phase:   Kết nối start/goal vào roadmap, sau đó tìm
#      đường ngắn nhất trên đồ thị bằng Dijkstra.
# ============================================================

# --- Import tham số cấu hình từ file config ---
from config.parameter import (
    MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu đến chướng ngại vật
    PRM_CONNECTION_RADIUS,  # Bán kính tối đa để kết nối 2 node với nhau
    PRM_MAX_SAMPLE_ATTEMPTS,  # Hệ số nhân giới hạn thử lấy mẫu (= n_samples * hệ số)
    PRM_N_SAMPLES,  # Số lượng điểm mẫu cần lấy để xây dựng roadmap
)

# --- Import các module nội bộ ---
from grid_map import GridMap  # Lớp quản lý bản đồ lưới (obstacle, boundary, start/goal)
from typing import Optional  # Dùng để khai báo kiểu có thể là None

# --- Import hàm tiện ích ---
from utils import euclidean_distance, min_distance_line_to_obstacle

# euclidean_distance            : Tính khoảng cách Euclidean giữa 2 điểm
# min_distance_line_to_obstacle : Tính khoảng cách ngắn nhất từ đoạn thẳng đến vật cản gần nhất

# --- Import thư viện chuẩn ---
import heapq  # Priority queue dùng cho thuật toán Dijkstra
import random  # Dùng để lấy mẫu ngẫu nhiên khi xây dựng roadmap


# ============================================================
# CLASS: PRMNode
# Đại diện cho một node trong roadmap của PRM.
# Mỗi node lưu tọa độ, ID định danh, và danh sách láng giềng
# đã được kết nối thành công (không va chạm).
# ============================================================
class PRMNode:
    def __init__(
        self,
        x: int,  # Tọa độ x của node trên lưới
        y: int,  # Tọa độ y của node trên lưới
        node_id: int,  # ID duy nhất để định danh node trong roadmap
    ) -> None:
        self.x = x  # Gán tọa độ x
        self.y = y  # Gán tọa độ y
        self.node_id = node_id  # Gán ID định danh

        # Danh sách láng giềng: mỗi phần tử là (neighbor_id, khoảng_cách)
        self.neighbors: list[tuple[int, float]] = []


# ============================================================
# CLASS: PRM
# Lớp chính thực thi thuật toán PRM.
# Nhận vào GridMap và các tham số điều chỉnh quá trình lấy mẫu,
# kết nối, và kiểm tra va chạm.
# ============================================================
class PRM:
    def __init__(
        self,
        grid_map: GridMap,  # Bản đồ lưới chứa thông tin chướng ngại vật
        n_samples: int = PRM_N_SAMPLES,  # Số điểm mẫu cần lấy để xây roadmap
        connection_radius: float = PRM_CONNECTION_RADIUS,  # Bán kính tối đa để nối 2 node
        max_sample_attempts: int = PRM_MAX_SAMPLE_ATTEMPTS,  # Hệ số giới hạn số lần thử lấy mẫu
        min_clearance: float = MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu đến vật cản
    ) -> None:
        self.grid_map = grid_map  # Lưu bản đồ lưới
        self.start = self.grid_map.start  # Lấy điểm bắt đầu từ bản đồ
        self.goal = self.grid_map.goal  # Lấy điểm đích từ bản đồ

        self.n_samples = n_samples  # Lưu số điểm mẫu mục tiêu
        self.connection_radius = connection_radius  # Lưu bán kính kết nối
        self.max_sample_attempts = max_sample_attempts  # Lưu hệ số giới hạn thử lấy mẫu
        self.min_clearance = float(min_clearance)  # Ép kiểu float để so sánh chính xác

        self.roadmap: dict[int, PRMNode] = {}  # Roadmap: ánh xạ node_id → PRMNode
        self.node_counter = 0  # Bộ đếm ID, tăng dần mỗi khi tạo node mới

    # --------------------------------------------------------
    # Hàm chính: Lập kế hoạch đường đi từ start đến goal.
    # Thực hiện đầy đủ 2 pha: xây roadmap + tìm đường trên roadmap.
    # Trả về danh sách tọa độ tạo thành đường đi, hoặc None nếu thất bại.
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

        # Pha 1 (Learning): Xây dựng roadmap bằng cách lấy mẫu và kết nối các node
        self._build_roadmap()

        # Pha 2 (Query): Kết nối start vào roadmap, trả về None nếu thất bại
        start_node = self._connect_point(start)

        # Kết nối goal vào roadmap, trả về None nếu thất bại
        goal_node = self._connect_point(goal)

        # Nếu không kết nối được start hoặc goal vào roadmap
        if start_node is None or goal_node is None:
            # Dọn dẹp các node query đã thêm trước khi trả về
            self._remove_query_nodes([start_node, goal_node])
            return None

        # Tìm đường ngắn nhất trên roadmap từ start_node đến goal_node (Dijkstra)
        path = self._search(start_node, goal_node)

        # Dọn dẹp start_node và goal_node khỏi roadmap để không ảnh hưởng lần query sau
        self._remove_query_nodes([start_node, goal_node])

        return path  # Trả về đường đi tìm được (hoặc None nếu không có đường)

    # --------------------------------------------------------
    # Xây dựng roadmap: lấy mẫu ngẫu nhiên các điểm trong không gian tự do,
    # tạo node cho mỗi điểm, rồi kết nối các node đủ gần và không va chạm.
    # --------------------------------------------------------
    def _build_roadmap(self) -> None:
        self.roadmap = {}  # Reset roadmap về rỗng trước khi xây mới
        self.node_counter = 0  # Reset bộ đếm ID node về 0

        samples: list[tuple[int, int]] = []  # Danh sách điểm mẫu hợp lệ
        attempts = 0  # Bộ đếm số lần thử lấy mẫu
        max_attempts = self.n_samples * self.max_sample_attempts  # Giới hạn thử tối đa

        # Lấy mẫu cho đến khi đủ n_samples điểm hoặc hết lượt thử
        while len(samples) < self.n_samples and attempts < max_attempts:
            attempts += 1

            # Chọn ngẫu nhiên một ô trong bản đồ
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)

            # Chỉ chấp nhận điểm nằm trong bản đồ và không phải chướng ngại vật
            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                samples.append((x, y))

        # Tạo PRMNode cho từng điểm mẫu hợp lệ và đưa vào roadmap
        for x, y in samples:
            self.roadmap[self.node_counter] = PRMNode(x, y, self.node_counter)
            self.node_counter += 1  # Tăng ID cho node tiếp theo

        # Kết nối các cặp node: nếu đủ gần và đoạn nối không bị va chạm
        for node_id, node in list(self.roadmap.items()):
            for other_id, other_node in list(self.roadmap.items()):

                # Bỏ qua khi so sánh node với chính nó
                if other_id == node_id:
                    continue

                # Tính khoảng cách giữa 2 node
                distance = euclidean_distance(
                    (node.x, node.y), (other_node.x, other_node.y)
                )

                # Kết nối nếu: trong bán kính connection_radius VÀ không bị va chạm
                if (
                    distance <= self.connection_radius
                    and not self._segment_has_collision(
                        (node.x, node.y), (other_node.x, other_node.y)
                    )
                ):
                    # Thêm other_node vào danh sách láng giềng của node (một chiều)
                    # Lưu ý: chỉ thêm 1 chiều vì vòng lặp sẽ xử lý chiều ngược lại
                    node.neighbors.append((other_id, distance))

    # --------------------------------------------------------
    # Kết nối một điểm query (start hoặc goal) vào roadmap đã xây.
    # Tìm tất cả node trong roadmap đủ gần và kết nối 2 chiều.
    # Trả về None nếu điểm không kết nối được với bất kỳ node nào.
    # --------------------------------------------------------
    def _connect_point(self, point: tuple[int, int]) -> Optional[PRMNode]:

        # Tạo node mới cho điểm query với ID tiếp theo
        new_node = PRMNode(point[0], point[1], self.node_counter)
        is_connected = False  # Cờ theo dõi xem đã kết nối được node nào chưa

        for other_id, other_node in self.roadmap.items():

            # Tính khoảng cách từ new_node đến từng node trong roadmap
            distance = euclidean_distance(
                (new_node.x, new_node.y), (other_node.x, other_node.y)
            )

            # Kết nối nếu: trong bán kính VÀ đoạn thẳng không bị va chạm
            if distance <= self.connection_radius and not self._segment_has_collision(
                (new_node.x, new_node.y), (other_node.x, other_node.y)
            ):
                # Thêm kết nối từ new_node đến other_node
                new_node.neighbors.append((other_id, distance))

                # Thêm kết nối ngược lại từ other_node đến new_node (2 chiều)
                other_node.neighbors.append((new_node.node_id, distance))

                is_connected = True  # Đánh dấu đã kết nối thành công ít nhất 1 node

        # Nếu không kết nối được với bất kỳ node nào, trả về None
        if not is_connected:
            return None

        # Thêm new_node vào roadmap và tăng bộ đếm ID
        self.roadmap[new_node.node_id] = new_node
        self.node_counter += 1

        return new_node  # Trả về node vừa được kết nối vào roadmap

    # --------------------------------------------------------
    # Dọn dẹp các node query (start/goal) khỏi roadmap sau khi tìm đường.
    # Đồng thời xóa các liên kết ngược từ láng giềng trỏ về các node này.
    # Mục đích: giữ roadmap sạch để tái sử dụng cho lần query tiếp theo.
    # --------------------------------------------------------
    def _remove_query_nodes(self, nodes: list[Optional[PRMNode]]) -> None:
        for node in nodes:

            # Bỏ qua nếu node là None (kết nối thất bại từ trước)
            if node is None:
                continue

            # Xóa node khỏi roadmap, trả về None nếu không tồn tại
            removed_node = self.roadmap.pop(node.node_id, None)

            # Nếu node không còn trong roadmap, bỏ qua
            if removed_node is None:
                continue

            # Xóa tham chiếu ngược: duyệt qua tất cả láng giềng của node bị xóa
            for neighbor_id, _ in removed_node.neighbors:
                neighbor = self.roadmap.get(neighbor_id)

                # Bỏ qua nếu láng giềng đã không còn trong roadmap
                if neighbor is None:
                    continue

                # Lọc bỏ liên kết trong danh sách láng giềng của neighbor
                # trỏ về node vừa bị xóa
                neighbor.neighbors = [
                    (existing_id, dist)
                    for existing_id, dist in neighbor.neighbors
                    if existing_id
                    != removed_node.node_id  # Giữ lại tất cả trừ node bị xóa
                ]

    # --------------------------------------------------------
    # Tìm đường ngắn nhất trên roadmap từ start_node đến goal_node.
    # Dùng thuật toán Dijkstra với priority queue (min-heap).
    # Trả về danh sách tọa độ của đường đi, hoặc None nếu không có đường.
    # --------------------------------------------------------
    def _search(
        self,
        start_node: PRMNode,  # Node bắt đầu tìm kiếm
        goal_node: PRMNode,  # Node đích cần đến
    ) -> Optional[list[tuple[int, int]]]:

        # Khởi tạo bảng khoảng cách: tất cả node đều có khoảng cách vô cực
        distances: dict[int, float] = {
            node_id: float("inf") for node_id in self.roadmap
        }

        # Bảng truy vết: came_from[node_id] = node_id của node cha trong đường đi tốt nhất
        came_from: dict[int, Optional[int]] = {
            node_id: None for node_id in self.roadmap
        }

        # Khoảng cách từ start đến chính nó bằng 0
        distances[start_node.node_id] = 0.0

        # Khởi tạo priority queue với start_node: (khoảng_cách, node_id)
        open_set: list[tuple[float, int]] = [(0.0, start_node.node_id)]

        # Vòng lặp Dijkstra: tiếp tục cho đến khi hàng đợi rỗng
        while open_set:

            # Lấy node có khoảng cách nhỏ nhất ra khỏi priority queue
            current_dist, current_id = heapq.heappop(open_set)

            # Bỏ qua nếu đây là bản ghi cũ (khoảng cách đã được cải thiện sau)
            if current_dist > distances[current_id]:
                continue

            # Nếu đã đến goal, truy vết ngược để tạo đường đi
            if current_id == goal_node.node_id:
                return self._reconstruct_path(goal_node.node_id, came_from)

            # Lấy node hiện tại từ roadmap
            current_node = self.roadmap[current_id]

            # Duyệt qua tất cả láng giềng của node hiện tại
            for neighbor_id, edge_distance in current_node.neighbors:

                # Tính khoảng cách mới đến neighbor qua current_node
                new_dist = current_dist + edge_distance

                # Nếu tìm được đường ngắn hơn đến neighbor, cập nhật
                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist  # Cập nhật khoảng cách tốt nhất
                    came_from[neighbor_id] = current_id  # Ghi lại node cha
                    heapq.heappush(
                        open_set, (new_dist, neighbor_id)
                    )  # Thêm vào hàng đợi

        # Không tìm được đường đến goal
        return None

    # --------------------------------------------------------
    # Truy vết đường đi từ goal về start thông qua bảng came_from.
    # Sau đó đảo ngược để có thứ tự start → goal.
    # --------------------------------------------------------
    def _reconstruct_path(
        self,
        goal_id: int,  # ID của node đích
        came_from: dict[int, Optional[int]],  # Bảng truy vết node cha
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []  # Danh sách điểm trên đường đi
        current_id: Optional[int] = goal_id  # Bắt đầu từ goal

        # Đi ngược qua came_from cho đến khi gặp None (tức đã về đến start)
        while current_id is not None:
            node = self.roadmap[current_id]  # Lấy node theo ID
            path.append((node.x, node.y))  # Thêm tọa độ vào đường đi
            current_id = came_from[current_id]  # Chuyển về node cha

        # Đảo ngược để đường đi có chiều từ start đến goal
        path.reverse()
        return path

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
