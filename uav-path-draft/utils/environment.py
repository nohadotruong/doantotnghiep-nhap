# ===== IMPORT CÁC THƯ VIỆN CẦN THIẾT =====
import numpy as np                          # Thư viện làm việc với mảng và tính toán số học
import matplotlib.pyplot as plt             # Thư viện vẽ đồ thị và visualization
from matplotlib.patches import Rectangle, Circle  # Thư viện vẽ hình chữ nhật và hình tròn
from typing import Tuple                     # Thư viện type hints - giúp code dễ đọc hơn
import json                                  # Thư viện làm việc với JSON
import os                                    # Thư viện làm việc với hệ thống file
from datetime import datetime                # Thư viện làm việc với thời gian


class UAVEnvironment:
    """Lớp đại diện cho môi trường 2D với các chướng ngại vật
    
    Lớp này chứa:
    - Bản đồ (grid): khu vực hoạt động của UAV
    - Vị trí start (điểm xuất phát)
    - Vị trí goal (điểm đích)
    - Các chướng ngại vật (obstacles): hình chữ nhật và hình tròn
    
    Tính năng:
    - Tạo bản đồ ngẫu nhiên
    - Kiểm tra va chạm (collision detection)
    - Visualization (vẽ bản đồ)
    """
    
    def __init__(self, width=100, height=100, grid_size=1, num_obstacles=0):
        """Hàm khởi tạo (Constructor) môi trường
        
        Args:
            width (int): Chiều rộng của bản đồ (mặc định 100)
            height (int): Chiều cao của bản đồ (mặc định 100)
            grid_size (int): Kích thước mỗi ô trong grid (mặc định 1, hiện không sử dụng)
            num_obstacles (int): Số lượng chướng ngại vật tạo ngẫu nhiên (mặc định 0)
        """
        self.width = width                      # Lưu trữ chiều rộng bản đồ
        self.height = height                    # Lưu trữ chiều cao bản đồ
        self.grid_size = grid_size              # Lưu trữ kích thước grid (dự phòng)
        self.start = None                       # Vị trí xuất phát (None nếu chưa đặt)
        self.goal = None                        # Vị trí đích (None nếu chưa đặt)
        self.obstacles = []                     # Danh sách các chướng ngại vật

        # Nếu num_obstacles > 0, tự động tạo bản đồ với các chướng ngại vật ngẫu nhiên
        if num_obstacles > 0:
            self.simple_map(num_obstacles=num_obstacles)

    def add_rectangular_obstacle(self, x, y, width, height):
        """Thêm một chướng ngại vật hình chữ nhật vào bản đồ
        
        Args:
            x (float): Tọa độ x của góc dưới-trái của hình chữ nhật
            y (float): Tọa độ y của góc dưới-trái của hình chữ nhật
            width (float): Chiều rộng của hình chữ nhật
            height (float): Chiều cao của hình chữ nhật
        """
        self.obstacles.append(
            {"type": "rectangle", "x": x, "y": y, "width": width, "height": height}
        )

    def add_circular_obstacle(self, x, y, radius):
        """Thêm một chướng ngại vật hình tròn vào bản đồ
        
        Args:
            x (float): Tọa độ x của tâm hình tròn
            y (float): Tọa độ y của tâm hình tròn
            radius (float): Bán kính của hình tròn
        """
        self.obstacles.append(
            {
                "type": "circle",
                "x": x,
                "y": y,
                "radius": radius,
            }
        )

    def set_start_goal(self, start: Tuple[float, float], goal: Tuple[float, float]):
        """Đặt vị trí điểm xuất phát và điểm đích cho bản đồ
        
        Args:
            start (Tuple[float, float]): Tọa độ [x, y] của điểm xuất phát
            goal (Tuple[float, float]): Tọa độ [x, y] của điểm đích
        """
        # Chuyển từ tuple thành numpy array để dễ tính toán
        self.start = np.array(start)
        self.goal = np.array(goal)

    def simple_map(self, num_obstacles=5, seed=None):
        """Tạo bản đồ ngẫu nhiên với các chướng ngại vật
        
        Bản đồ được tạo bằng cách:
        1. Tạo ngẫu nhiên num_obstacles chướng ngại vật
        2. Mỗi chướng ngại vật là hình chữ nhật (60% xác suất) hoặc hình tròn (40% xác suất)
        3. Vị trí chắc chắn nằm trong khu vực an toàn (tránh sát cạnh bản đồ)
        
        Args:
            num_obstacles (int): Số lượng chướng ngại vật cần tạo (mặc định 5)
            seed (int): Seed cho random (nếu None, kết quả sẽ khác mỗi lần chạy)
                        Nếu set seed, kết quả sẽ lặp lại
        """
        # Nếu seed được chỉ định, đặt seed để có kết quả tái lập được
        if seed is not None:
            np.random.seed(seed)

        # Xóa các chướng ngại vật cũ (nếu có) để tạo bản đồ mới
        self.obstacles = []

        # Lặp num_obstacles lần để tạo mỗi chướng ngại vật
        for i in range(num_obstacles):
            # Chọn ngẫu nhiên kiểu chướng ngại vật:
            # - 60% xác suất: hình chữ nhật ("rectangle")
            # - 40% xác suất: hình tròn ("circle")
            obstacle_type = np.random.choice(["rectangle", "circle"], p=[0.6, 0.4])

            # Nếu là hình chữ nhật
            if obstacle_type == "rectangle":
                # Tọa độ x: ngẫu nhiên từ 10 đến 70% chiều rộng (tránh sát cạnh)
                x = np.random.uniform(10, self.width * 0.7)
                # Tọa độ y: ngẫu nhiên từ 10 đến 70% chiều cao (tránh sát cạnh)
                y = np.random.uniform(10, self.height * 0.7)
                # Chiều rộng: ngẫu nhiên từ 10 đến 25 đơn vị
                w = np.random.uniform(10, 25)
                # Chiều cao: ngẫu nhiên từ 8 đến 20 đơn vị
                h = np.random.uniform(8, 20)

                # Thêm chướng ngại vật hình chữ nhật
                self.add_rectangular_obstacle(x, y, w, h)

            # Nếu là hình tròn
            elif obstacle_type == "circle":
                # Tọa độ x của tâm: ngẫu nhiên từ 15 đến 70% chiều rộng
                x = np.random.uniform(15, self.width * 0.7)
                # Tọa độ y của tâm: ngẫu nhiên từ 15 đến 70% chiều cao
                y = np.random.uniform(15, self.height * 0.7)
                # Bán kính: ngẫu nhiên từ 5 đến 12 đơn vị
                r = np.random.uniform(5, 12)

                # Thêm chướng ngại vật hình tròn
                self.add_circular_obstacle(x, y, r)

    def is_collision(self, point: np.ndarray, safety_radius=1.0) -> bool:
        """Kiểm tra xem một điểm có va chạm với chướng ngại vật hay không
        
        Hàm kiểm tra:
        1. Điểm có nằm ngoài biên bản đồ không
        2. Điểm có va chạm với hình chữ nhật nào không
        3. Điểm có va chạm với hình tròn nào không
        
        Args:
            point (np.ndarray): Tọa độ [x, y] của điểm cần kiểm tra
            safety_radius (float): Bán kính an toàn (mặc định 1.0)
                                  UAV cần cách chướng ngại vật ít nhất safety_radius
        
        Returns:
            bool: True nếu có va chạm, False nếu không va chạm
        """
        # Lấy tọa độ x và y từ điểm
        x, y = point[0], point[1]

        # ===== KIỂM TRA BIÊN BẢN ĐỒ =====
        # Nếu điểm nằm ngoài bản đồ, coi như va chạm
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return True

        # ===== KIỂM TRA VA CHẠM VỚI CÁC CHƯỚNG NGẠI VẬT =====
        # Lặp qua tất cả các chướng ngại vật
        for obstacle in self.obstacles:
            # Nếu là chướng ngại vật hình chữ nhật
            if obstacle["type"] == "rectangle":
                # Lấy thông tin hình chữ nhật
                rect_x = obstacle["x"]          # Tọa độ x của góc dưới-trái
                rect_y = obstacle["y"]          # Tọa độ y của góc dưới-trái
                rect_w = obstacle["width"]      # Chiều rộng
                rect_h = obstacle["height"]     # Chiều cao

                # Tìm điểm gần nhất trên hình chữ nhật so với điểm đang kiểm tra
                # np.clip: giới hạn giá trị trong khoảng [min, max]
                # Nếu x nằm trong [rect_x, rect_x + rect_w], closest_x = x
                # Nếu x < rect_x, closest_x = rect_x (cạnh trái)
                # Nếu x > rect_x + rect_w, closest_x = rect_x + rect_w (cạnh phải)
                closest_x = np.clip(x, rect_x, rect_x + rect_w)
                closest_y = np.clip(y, rect_y, rect_y + rect_h)

                # Tính khoảng cách từ điểm đến điểm gần nhất trên hình chữ nhật
                # Công thức: distance = sqrt((x2-x1)^2 + (y2-y1)^2)
                distance = np.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)
                
                # Nếu khoảng cách < safety_radius, có va chạm
                if distance < safety_radius:
                    return True

            # Nếu là chướng ngại vật hình tròn
            elif obstacle["type"] == "circle":
                # Lấy tâm của hình tròn
                center = np.array([obstacle["x"], obstacle["y"]])
                
                # Tính khoảng cách từ điểm đến tâm hình tròn
                distance = np.linalg.norm(point - center)
                
                # Nếu khoảng cách < bán kính + safety_radius, có va chạm
                if distance < obstacle["radius"] + safety_radius:
                    return True

        # Nếu kiểm tra qua tất cả chướng ngại vật không có va chạm, trả về False
        return False

    def line_collision(
        self, point1: np.ndarray, point2: np.ndarray, num_checks=20, safety_radius=1.0
    ) -> bool:
        """Kiểm tra xem đường thẳng từ point1 đến point2 có va chạm với chướng ngại vật không
        
        Cách kiểm tra:
        1. Chia đường thẳng thành num_checks điểm trung gian
        2. Kiểm tra từng điểm xem có va chạm không
        3. Nếu có điểm nào va chạm, trả về True
        
        Args:
            point1 (np.ndarray): Tọa độ điểm bắt đầu [x, y]
            point2 (np.ndarray): Tọa độ điểm kết thúc [x, y]
            num_checks (int): Số điểm cần kiểm tra trên đường thẳng (mặc định 20)
                             Càng nhiều càng chính xác nhưng mất thời gian hơn
            safety_radius (float): Bán kính an toàn (mặc định 1.0)
        
        Returns:
            bool: True nếu đường thẳng va chạm, False nếu không
        """
        # Chia đường thẳng thành num_checks điểm (từ 0 đến 1)
        # t=0: point1, t=1: point2, các giá trị giữa: điểm trung gian
        for t in np.linspace(0, 1, num_checks):
            # Công thức nội suy tuyến tính: điểm = point1*(1-t) + point2*t
            # Điều này tạo ra một điểm nằm giữa point1 và point2
            point = point1 * (1 - t) + point2 * t
            
            # Kiểm tra xem điểm này có va chạm không
            if self.is_collision(point, safety_radius):
                return True  # Có va chạm, trả về True ngay

        # Nếu kiểm tra tất cả các điểm không có va chạm, trả về False
        return False

    def get_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """Tính khoảng cách Euclidean giữa hai điểm
        
        Công thức: distance = sqrt((x2-x1)^2 + (y2-y1)^2)
        
        Args:
            point1 (np.ndarray): Tọa độ điểm thứ nhất [x, y]
            point2 (np.ndarray): Tọa độ điểm thứ hai [x, y]
        
        Returns:
            float: Khoảng cách giữa hai điểm
        """
        # np.linalg.norm: tính độ dài của vector (point2 - point1)
        return np.linalg.norm(point2 - point1)

    def visualize(self, path=None, title="UAV Environment"):
        """Vẽ bản đồ với các chướng ngại vật, điểm start, goal, và đường đi (nếu có)
        
        Visualization:
        - Đỏ: Chướng ngại vật (hình chữ nhật và hình tròn)
        - Xanh lá: Điểm xuất phát (Start) - hình tròn
        - Xanh dương sao: Điểm đích (Goal) - hình sao
        - Xanh dương: Đường đi (Path) - nếu được cung cấp
        
        Args:
            path (List[np.ndarray], optional): Danh sách các điểm tạo thành đường đi.
                                              Nếu None, không vẽ đường đi
            title (str): Tiêu đề của biểu đồ (mặc định "UAV Environment")
        
        Returns:
            tuple: (fig, ax) - figure và axes matplotlib để có thể tiếp tục vẽ thêm
        """
        # Tạo figure và axes với kích thước 10x10 inch
        fig, ax = plt.subplots(figsize=(10, 10))

        # ===== CẤU HÌNH AXES =====
        ax.set_xlim(0, self.width)              # Giới hạn trục x từ 0 đến width
        ax.set_ylim(0, self.height)             # Giới hạn trục y từ 0 đến height
        ax.set_aspect("equal")                  # Tỷ lệ x:y = 1:1 (không bóp méo)
        ax.grid(True, alpha=0.3)                # Hiển thị lưới với độ trong suốt 0.3
        ax.set_xlabel("X")                      # Nhãn trục x
        ax.set_ylabel("Y")                      # Nhãn trục y
        ax.set_title(title)                     # Tiêu đề biểu đồ

        # ===== VẼ CÁC CHƯỚNG NGẠI VẬT =====
        for obstacle in self.obstacles:
            # Nếu là chướng ngại vật hình chữ nhật
            if obstacle["type"] == "rectangle":
                # Tạo đối tượng Rectangle
                rect = Rectangle(
                    (obstacle["x"], obstacle["y"]),  # Tọa độ góc dưới-trái
                    obstacle["width"],               # Chiều rộng
                    obstacle["height"],              # Chiều cao
                    fill=True,                       # Tô đầy màu
                    facecolor="red",                 # Màu tô: đỏ
                    edgecolor="darkred",             # Màu viền: đỏ đậm
                    alpha=0.7,                       # Độ trong suốt: 0.7
                    linewidth=2,                     # Độ dày viền: 2
                )
                ax.add_patch(rect)  # Thêm hình chữ nhật vào axes

            # Nếu là chướng ngại vật hình tròn
            elif obstacle["type"] == "circle":
                # Tạo đối tượng Circle
                circle = Circle(
                    (obstacle["x"], obstacle["y"]),   # Tạo độ tâm (x, y)
                    obstacle["radius"],              # Bán kính
                    fill=True,                       # Tô đầy màu
                    facecolor="red",                 # Màu tô: đỏ
                    edgecolor="darkred",             # Màu viền: đỏ đậm
                    alpha=0.7,                       # Độ trong suốt: 0.7
                    linewidth=2,                     # Độ dày viền: 2
                )
                ax.add_patch(circle)  # Thêm hình tròn vào axes

        # ===== VẼ ĐIỂM XUẤT PHÁT (START) =====
        if self.start is not None:
            ax.plot(
                self.start[0],
                self.start[1],
                "go",                   # Màu xanh lá, hình tròn (o)
                markersize=15,          # Kích thước marker: 15
                label="Start",          # Nhãn trong legend
                zorder=5,               # Vẽ lên trên các đối tượng khác
            )

        # ===== VẼ ĐIỂM ĐÍch (GOAL) =====
        if self.goal is not None:
            ax.plot(
                self.goal[0],
                self.goal[1],
                "b*",                   # Màu xanh dương, hình sao (*)
                markersize=20,          # Kích thước marker: 20
                label="Goal",           # Nhãn trong legend
                zorder=5,               # Vẽ lên trên các đối tượng khác
            )

        # ===== VẼ ĐƯỜNG ĐI (PATH) =====
        if path is not None and len(path) > 0:
            # Chuyển danh sách đường đi thành numpy array để dễ xử lý
            path = np.array(path)
            
            # Vẽ đường thẳng nối các điểm trong đường đi
            ax.plot(
                path[:, 0],             # Tọa độ x của tất cả các điểm
                path[:, 1],             # Tọa độ y của tất cả các điểm
                "b-",                   # Màu xanh dương, kiểu đường thẳng (-)
                linewidth=2,            # Độ dày đường: 2
                label="Path",           # Nhãn trong legend
                alpha=0.7,              # Độ trong suốt: 0.7
            )
            
            # Vẽ các điểm riêng lẻ trên đường đi (để dễ thấy)
            ax.plot(
                path[:, 0],             # Tọa độ x của tất cả các điểm
                path[:, 1],             # Tọa độ y của tất cả các điểm
                "bo",                   # Màu xanh dương, hình tròn (o)
                markersize=4,           # Kích thước marker: 4 (nhỏ)
                alpha=0.5,              # Độ trong suốt: 0.5
            )

        # ===== THÊM LEGEND (CHÚ THÍCH) =====
        ax.legend(loc="best")           # Thêm chú thích ở vị trí tốt nhất
        
        return fig, ax                  # Trả về figure và axes để có thể tiếp tục sử dụng

    def save_map(self, filename: str = None, folder: str = "maps"):
        """Lưu bản đồ vào file JSON và ảnh trong thư mục maps/<timestamp>
        
        Hàm này sẽ lưu:
        1. File JSON: chứa thông tin bản đồ (kích thước, start, goal, chướng ngại vật)
        2. File PNG: hình ảnh visualization của bản đồ
        
        Thư mục lưu sẽ có tên: maps/<timestamp> (ví dụ: maps/2026-02-28_14-30-45)
        
        Args:
            filename (str, optional): Tên file lưu (không bao gồm extension)
                                     Nếu None, sẽ dùng "map_<timestamp>"
            folder (str): Thư mục gốc (mặc định "maps")
        
        Returns:
            dict: Chứa đường dẫn của hai file đã lưu:
                  {"json": path_to_json_file, "image": path_to_image_file}
        """
        # Tạo timestamp hiện tại (format: YYYY-MM-DD_HH-MM-SS)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Nếu không cung cấp tên file, dùng "map_<timestamp>"
        if filename is None:
            filename = f"map_{timestamp}"
        
        # Tạo thư mục maps/<timestamp> nếu chưa tồn tại
        map_folder = os.path.join(folder, timestamp)
        if not os.path.exists(map_folder):
            os.makedirs(map_folder)
        
        # Tạo đường dẫn cho file JSON
        json_filepath = os.path.join(map_folder, f"{filename}.json")
        
        # Chuẩn bị dữ liệu để lưu
        map_data = {
            "width": self.width,
            "height": self.height,
            "start": self.start.tolist() if self.start is not None else None,
            "goal": self.goal.tolist() if self.goal is not None else None,
            "obstacles": self.obstacles
        }
        
        # Lưu dữ liệu vào file JSON
        with open(json_filepath, 'w') as f:
            json.dump(map_data, f, indent=4)
        
        print(f"File JSON đã được lưu tại: {json_filepath}")
        
        # Tạo đường dẫn cho file ảnh
        image_filepath = os.path.join(map_folder, f"{filename}.png")
        
        # Vẽ bản đồ và lưu ảnh
        fig, ax = self.visualize(title=f"Map - {timestamp}")
        fig.savefig(image_filepath, dpi=100, bbox_inches='tight')
        plt.close(fig)  # Đóng figure để tiết kiệm bộ nhớ
        
        print(f"File ảnh đã được lưu tại: {image_filepath}")
        
        # Trả về đường dẫn của cả hai file
        return {"json": json_filepath, "image": image_filepath}

    def load_map(self, filepath: str):
        """Tải bản đồ từ file JSON
        
        Hàm này sẽ đọc file JSON và khôi phục tất cả thông tin bản đồ:
        - Kích thước (width, height)
        - Vị trí start và goal
        - Danh sách tất cả chướng ngại vật
        
        Args:
            filepath (str): Đường dẫn đầy đủ đến file JSON
                           (ví dụ: "maps/my_map.json")
        
        Returns:
            bool: True nếu tải thành công, False nếu file không tồn tại
        """
        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(filepath):
            print(f"Lỗi: File không tồn tại - {filepath}")
            return False
        
        try:
            # Đọc dữ liệu từ file JSON
            with open(filepath, 'r') as f:
                map_data = json.load(f)
            
            # Khôi phục thông tin bản đồ
            self.width = map_data["width"]
            self.height = map_data["height"]
            self.start = np.array(map_data["start"]) if map_data["start"] is not None else None
            self.goal = np.array(map_data["goal"]) if map_data["goal"] is not None else None
            self.obstacles = map_data["obstacles"]
            
            print(f"Bản đồ đã được tải thành công từ: {filepath}")
            return True
            
        except json.JSONDecodeError:
            print(f"Lỗi: File JSON không hợp lệ - {filepath}")
            return False
        except KeyError as e:
            print(f"Lỗi: Thiếu dữ liệu trong file - {e}")
            return False

# ===== CHƯƠNG TRÌNH CHÍNH KIỂM TRA =====
if __name__ == "__main__":
    # Tạo môi trường mới với kích thước 100x100
    env = UAVEnvironment(width=100, height=100)

    # Tạo bản đồ ngẫu nhiên với 9 chướng ngại vật
    # seed=42 để kết quả lặp lại mỗi lần chạy
    env.simple_map(num_obstacles=9, seed=42)
    
    # Đặt điểm xuất phát ở (5, 5) và điểm đích ở (95, 95)
    env.set_start_goal((5, 5), (95, 95))

    # Tạo một đường đi thẳng từ start đến goal (chỉ để demo visualization)
    path = [(5, 5), (95, 95)]

    # Vẽ bản đồ với đường đi
    env.visualize(path, title="Simple Map")
    
    # Hiển thị biểu đồ
    plt.show()
