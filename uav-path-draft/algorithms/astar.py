# ===== IMPORT CÁC THƯ VIỆN CẦN THIẾT =====
import numpy as np       # Thư viện làm việc với mảng và toán học
import heapq            # Thư viện cấu trúc dữ liệu hàng đợi ưu tiên (Priority Queue)
import time             # Thư viện đo thời gian thực hiện thuật toán
from typing import List, Optional  # Thư viện type hints giúp code dễ đọc hơn
from utils.enviroment import UAVEnvironment  # Import module cung cấp môi trường (bản đồ, chướng ngại vật)
import matplotlib.pyplot as plt  # Thư viện vẽ đồ thị để visualization


# ===== GIẢI THÍCH VỀ THUẬT TOÁN A* =====
# A* (A-Star) là một thuật toán tìm đường đi ngắn nhất giữa hai điểm trong bản đồ có chướng ngại vật
# Cách hoạt động:
#   1. Bắt đầu từ vị trí xuất phát (start)
#   2. Khám phá các điểm lân cận (neighbors) theo 8 hướng (4 hướng chính + 4 hướng chéo)
#   3. Tính điểm F = G + H:
#      - G: khoảng cách thực từ start đến điểm hiện tại
#      - H: ước lượng khoảng cách từ điểm hiện tại đến goal (heuristic)
#   4. Ưu tiên khám phá các điểm có F nhỏ nhất trước
#   5. Lặp lại cho đến khi tìm được đường đi hoặc không còn điểm nào để khám phá

class AStarPathfinder:
    """Lớp thực hiện thuật toán A* để tìm đường đi"""
    
    def __init__(self, environment: UAVEnvironment, grid_step=2.0):
        """
        Hàm khởi tạo (Constructor)
        
        Args:
            environment (UAVEnvironment): Đối tượng môi trường chứa bản đồ, vị trí start, goal, chướng ngại vật
            grid_step (float): Kích thước bước nhảy khi tìm đường (mặc định 2.0)
        """
        self.env = environment              # Lưu trữ môi trường (bản đồ)
        self.grid_step = grid_step          # Khoảng cách giữa các điểm lân cận
        self.path = None                    # Danh sách các điểm trong đường đi (mới tạo là None - chưa tìm)
        self.visited_nodes = []             # Danh sách các điểm đã được khám phá (closed_set)
        self.track_history = True           # Cờ để lưu lại lịch sử quá trình tìm đường (dùng để animation)
        self.position_history = []          # Danh sách lưu lịch sử từng bước tìm kiếm
        self.search_time = 0                # Thời gian thực hiện thuật toán (tính bằng giây)

    def heuristic(self, point: np.ndarray) -> float:
        """
        Hàm ước lượng khoảng cách từ một điểm đến goal (điểm đích)
        
        Sử dụng công thức Euclidean distance (khoảng cách thẳng được):
        khoảng_cách = sqrt((x2-x1)^2 + (y2-y1)^2)
        
        Args:
            point (np.ndarray): Tọa độ điểm cần ước lượng [x, y]
            
        Returns:
            float: Khoảng cách ước lượng từ điểm đến goal
        """
        return np.linalg.norm(self.env.goal - point)

    def get_neighbors(self, point: np.ndarray, max_turns=8) -> List[np.ndarray]:
        """
        Hàm tìm tất cả các điểm lân cận (điểm có thể đi tới từ điểm hiện tại)
        
        Từ một điểm, có thể di chuyển theo 8 hướng:
        - 4 hướng chính: Lên, Xuống, Phải, Trái
        - 4 hướng chéo: Chéo lên phải, Chéo lên trái, Chéo xuống phải, Chéo xuống trái
        
        Args:
            point (np.ndarray): Tọa độ điểm hiện tại [x, y]
            max_turns (int): Số hướng tối đa (không sử dụng trong code này, giữ cho compatibilty)
            
        Returns:
            List[np.ndarray]: Danh sách các điểm lân cận hợp lệ (không va chạm, không bị chặn)
        """
        neighbors = []  # Danh sách lưu các điểm lân cận
        
        # Định nghĩa 8 hướng di chuyển: (dx, dy)
        # grid_step là khoảng cách di chuyển, mặc định là 2.0
        directions = [
            (self.grid_step, 0),             # Di chuyển phải
            (-self.grid_step, 0),            # Di chuyển trái
            (0, self.grid_step),             # Di chuyển lên
            (0, -self.grid_step),            # Di chuyển xuống
            (self.grid_step, self.grid_step),     # Di chuyển chéo lên phải
            (self.grid_step, -self.grid_step),    # Di chuyển chéo xuống phải
            (-self.grid_step, self.grid_step),    # Di chuyển chéo lên trái
            (-self.grid_step, -self.grid_step),   # Di chuyển chéo xuống trái
        ]

        # Lặp qua từng hướng để tìm điểm lân cận
        for dx, dy in directions:
            # Tính tọa độ điểm lân cận mới
            new_point = point + np.array([dx, dy])

            # Kiểm tra xem điểm mới có hợp lệ không:
            # - is_collision: Điểm không chạm chướng ngại vật
            # - line_collision: Đường đi từ điểm hiện tại đến điểm mới không bị chặn
            if not self.env.is_collision(new_point) and not self.env.line_collision(
                point, new_point
            ):
                neighbors.append(new_point)  # Thêm vào danh sách nếu hợp lệ

        return neighbors  # Trả về danh sách các điểm lân cận hợp lệ

    def find_path(self) -> bool:
        """
        Hàm chính thực hiện thuật toán A* để tìm đường đi từ start đến goal
        
        Returns:
            bool: True nếu tìm được đường đi, False nếu không tìm được
        
        Giải thích chi tiết quá trình:
        1. Khởi tạo open_set (các điểm chưa được khám phá) với điểm start
        2. Lặp cho đến khi open_set rỗng hoặc tìm được goal:
           - Lấy điểm có F score nhỏ nhất từ open_set (ưu tiên cao nhất)
           - Nếu là goal: thêm các điểm trung gian để hoàn thành đường đi, trả về True
           - Nếu không: coi như đã khám phá điểm này, thêm vào closed_set
           - Tìm tất cả điểm lân cận của điểm hiện tại
           - Cập nhật điểm lân cận: tính G score mới, so sánh với G score cũ
           - Nếu G score mới tốt hơn: thêm vào open_set
        """
        # Ghi lại thời gian bắt đầu để tính thời gian chạy
        start_time = time.time()
        
        # Copy tọa độ start và goal để tránh thay đổi giá trị gốc
        start = self.env.start.copy()
        goal = self.env.goal.copy()

        # counter: biến đếm để đảm bảo thứ tự xử lý khi F score bằng nhau
        counter = 0
        
        # open_set: hàng đợi ưu tiên lưu các điểm chưa được khám phá
        # Mỗi phần tử: (f_score, counter, tọa_độ_tuple, đường_đi)
        # f_score: giá trị F = G + H (dùng để ưu tiên phần tử)
        # counter: thứ tự chèn (để break tie khi F score bằng nhau)
        # tọa_độ_tuple: tọa độ điểm dưới dạng tuple (để có thể dùng làm key trong dict)
        # đường_đi: danh sách các điểm từ start đến điểm hiện tại
        open_set = [(0, counter, tuple(start), [start.copy()])]
        
        # closed_set: tập hợp các điểm đã được khám phá (để tránh khám phá lại)
        closed_set = set()
        
        # g_scores: từ điển lưu G score (khoảng cách thực từ start) của mỗi điểm
        # Key: tọa độ điểm (dưới dạng tuple)
        # Value: G score của điểm đó
        g_scores = {tuple(start): 0}

        # ===== VÒ MỤC WHILE CHÍNH CỦA THUẬT TOÁN A* =====
        while open_set:  # Lặp cho đến khi open_set rỗng
            # Lấy phần tử có f_score nhỏ nhất từ open_set (điểm ưu tiên nhất)
            f_score, _, current_tuple, path = heapq.heappop(open_set)
            
            # Chuyển tọa độ từ tuple về numpy array để tính toán
            current = np.array(current_tuple)

            # Nếu điểm này đã được khám phá rồi, bỏ qua
            if tuple(current) in closed_set:
                continue

            # Kiểm tra xem điểm hiện tại có gần goal không
            # Nếu khoảng cách < 1.5 * grid_step thì coi như đã đến goal
            if np.linalg.norm(current - goal) < self.grid_step * 1.5:
                # ===== XỬ LÝ KHI GẦN ĐẾN GOAL =====
                last_point = np.array(path[-1])  # Lấy điểm cuối cùng trong đường đi hiện tại

                # Kiểm tra xem có thể đi thẳng từ điểm cuối cùng đến goal không
                if self.env.line_collision(last_point, goal):
                    # Nếu có chướng ngại vật chắn đường, coi điểm này chưa hoàn thành
                    if tuple(current) not in closed_set:
                        closed_set.add(tuple(current))
                        continue  # Tiếp tục tìm kiếm

                # ===== HOÀN THÀNH ĐƯỜNG ĐI =====
                final_path = path.copy()  # Copy đường đi hiện tại
                
                # Tính khoảng cách từ điểm cuối cùng đến goal
                distance = self.env.get_distance(last_point, goal)
                
                # Tính số điểm trung gian cần thêm vào (để đường đi mượt mà)
                # grid_step / 2: độ chi tiết cao hơn so với bước chính
                num_steps = max(2, int(distance / (self.grid_step / 2)))

                # Nội suy tuyến tính: tính các điểm trung gian từ last_point đến goal
                # np.linspace(0, 1, num_steps) tạo các giá trị từ 0 đến 1
                # t=[0,1]: t=0 là last_point, t=1 là goal
                # [1:] bỏ qua t=0 vì last_point đã có trong path rồi
                for t in np.linspace(0, 1, num_steps)[1:]:
                    # Công thức nội suy: điểm = điểm_cũ * (1-t) + điểm_mới * t
                    intermediate = last_point * (1 - t) + goal * t
                    final_path.append(intermediate.copy())

                # Lưu kết quả tìm được
                self.path = final_path  # Đường đi hoàn thành
                self.visited_nodes = list(closed_set)  # Các điểm đã khám phá
                self.search_time = time.time() - start_time  # Thời gian thực hiện
                return True  # Trả về True: tìm được đường đi

            # Thêm điểm hiện tại vào closed_set (đã khám phá xong)
            closed_set.add(tuple(current))

            # Lưu lịch sử từng bước tìm kiếm (dùng để animation)
            if self.track_history:
                self.position_history.append(
                    {
                        "iteration": len(self.position_history),  # Số bước hiện tại
                        "closed_set": [np.array(c) for c in closed_set],  # Các điểm đã khám phá
                        "open_set": [np.array(o[2]) for o in open_set],  # Các điểm chưa khám phá
                        "current_path": path,  # Đường đi hiện tại
                        "best_score": len(path),  # Số điểm trong đường đi
                        "current": current.copy(),  # Điểm đang xử lý
                    }
                )

            # ===== KHÁM PHÁ CÁC ĐIỂM LÂN CẬN =====
            # Lặp qua tất cả điểm lân cận của điểm hiện tại
            for neighbor in self.get_neighbors(current):
                # Nếu điểm lân cận đã được khám phá rồi, bỏ qua
                if tuple(neighbor) in closed_set:
                    continue

                # Tính G score mới: G của current + khoảng cách từ current đến neighbor
                new_g = g_scores[tuple(current)] + self.env.get_distance(
                    current, neighbor
                )

                # Kiểm tra xem điểm này là lần đầu gặp hay là đã gặp rồi nhưng có con đường tốt hơn
                if tuple(neighbor) not in g_scores or new_g < g_scores[tuple(neighbor)]:
                    # Cập nhật G score
                    g_scores[tuple(neighbor)] = new_g

                    # Tính H score: ước lượng khoảng cách từ neighbor đến goal
                    h = self.heuristic(neighbor)

                    # Tính F score: F = G + H
                    # F là tổng của:
                    # - G: khoảng cách thực từ start đến neighbor
                    # - H: ước lượng khoảng cách từ neighbor đến goal
                    f = new_g + h

                    # Tăng counter để đảm bảo thứ tự xử lý
                    counter += 1
                    
                    # Thêm điểm neighbor vào open_set với F score
                    # heappush: thêm phần tử vào heap (hàng đợi ưu tiên)
                    # Phần tử được sắp xếp theo f_score (nhỏ nhất ở trước)
                    heapq.heappush(
                        open_set,
                        (f, counter, tuple(neighbor), path + [neighbor.copy()]),
                    )

        # ===== KẾT THÚC: KHÔNG TÌM ĐƯỢC ĐƯỜNG ĐI =====
        # Nếu vòng while kết thúc mà không tìm được đường, lưu thông tin
        self.visited_nodes = list(closed_set)  # Danh sách các điểm đã khám phá
        self.search_time = time.time() - start_time  # Thời gian thực hiện
        return False  # Trả về False: không tìm được đường đi

    def get_path(self) -> Optional[List[np.ndarray]]:
        """Hàm trả về đường đi đã tìm được (hoặc None nếu không tìm được)"""
        return self.path

    def animate_history(self):
        """Hàm tạo animation hiển thị quá trình tìm đường A* theo từng bước
        
        Visualization:
        - Xanh dương: Các điểm đã khám phá (closed_set)
        - Xanh lamy: Các điểm chưa khám phá (open_set)
        - Đỏ: Điểm đang xử lý
        - Xanh lá: Đường đi hiện tại
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        for step in self.position_history:
            self.env.visualize(ax=ax, title="A* Track History")

            if len(step["closed_set"]) > 0:
                closed = np.array(step["closed_set"])
                ax.plot(closed[:, 0], closed[:, 1], "bo", markersize=3)

            if len(step["open_set"]) > 0:
                open_nodes = np.array(step["open_set"])
                ax.plot(open_nodes[:, 0], open_nodes[:, 1], "yo", markersize=3)

            c = step["current"]
            ax.plot(c[0], c[1], "ro", markersize=6)

            p = np.array(step["current_path"])
            ax.plot(p[:, 0], p[:, 1], "g-")

            plt.pause(0.03)

        plt.show()

    def get_statistics(self) -> dict:
        """Hàm trả về thống kê về kết quả tìm đường
        
        Returns:
            dict: Từ điển chứa:
                - path_length: Số điểm trong đường đi
                - num_waypoints: Số điểm waypoint (giống path_length)
                - distance: Tổng khoảng cách của đường đi
                - visited_nodes: Số điểm đã khám phá
                - search_time: Thời gian thực hiện tìm kiếm (giây)
        """
        # Nếu không tìm được đường đi, trả về thống kê mặc định
        if self.path is None:
            return {
                "path_length": None,
                "num_waypoints": 0,
                "distance": 0,
                "visited_nodes": 0,
                "search_time": 0,
            }

        # Chuyển đường đi thành numpy array để tính toán
        path = np.array(self.path)
        
        # Tính tổng khoảng cách: cộng khoảng cách giữa các điểm liên tiếp
        # range(len(path) - 1): lặp qua từng cặp điểm adjacent
        # np.linalg.norm: tính khoảng cách Euclidean giữa 2 điểm
        distance = float(
            sum(np.linalg.norm(path[i + 1] - path[i]) for i in range(len(path) - 1))
        )

        return {
            "path_length": len(self.path),     # Số điểm trong đường đi
            "num_waypoints": len(self.path),   # Số điểm waypoint
            "distance": round(distance, 2),    # Tổng khoảng cách (làm tròn 2 chữ số)
            "visited_nodes": len(self.visited_nodes),  # Số điểm đã khám phá
            "search_time": round(self.search_time, 2),  # Thời gian thực hiện (làm tròn 2 chữ số)
        }


# ===== CHƯƠNG TRÌNH CHÍNH TEST THUẬT TOÁN A* =====
if __name__ == "__main__":
    # Tạo môi trường mới
    env = UAVEnvironment()
    
    # Tạo bản đồ đơn giản với 8 chướng ngại vật (seed=42 để kết quả lặp lại)
    env.simple_map(num_obstacles=8, seed=42)
    
    # Đặt vị trí start (10, 10) và goal (90, 90)
    env.set_start_goal((10, 10), (90, 90))

    # Tạo pathfinder với grid_step=2
    astar = AStarPathfinder(env, grid_step=2)
    
    # Chạy thuật toán A*
    found = astar.find_path()

    # Có thể bỏ comment dòng dưới để xem animation quá trình tìm đường
    # astar.animate_history()

    # In kết quả
    print("Tìm được đường:", found)
    if found:
        print(astar.get_statistics())  # In thống kê
        env.visualize(path=astar.get_path(), title="A* Result")  # Vẽ bản đồ với đường đi
        plt.show()
