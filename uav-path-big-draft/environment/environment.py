# ============================================================================
# NHẬP CÁC THƯ VIỆN CẦN THIẾT
# ============================================================================
from datetime import datetime  # Để xử lý và lưu trữ thời gian
import json  # Để chuyển đổi dữ liệu thành JSON và ngược lại
import matplotlib.pyplot as plt  # Để vẽ đồ thị và biểu đồ
import matplotlib.patches as patches  # Để vẽ các hình dạng hình học như hình chữ nhật
import numpy as np  # Để xử lý mảng nhiều chiều và các phép toán đại số tuyến tính
import os  # Để làm việc với đường dẫn tệp và các hệ điều hành
import random  # Để phát sinh các số ngẫu nhiên
from utils import point_in_rectangle, line_rectangle_collision, path_length  # Nhập các hàm tiện ích từ file utils


# ============================================================================
# ĐỊNH NGHĨA LỚP UAVEnvironment - QUẢN LÝ MÔI TRƯỜNG BAY CỦA MÁY BAY KHÔNG NGƯỜI LÁI
# ============================================================================
class UAVEnvironment:
    """
    Lớp UAVEnvironment đại diện cho toàn bộ môi trường bay của UAV (máy bay không người lái).
    Cung cấp các phương thức để:
    - Khởi tạo môi trường với kích thước và chướng ngại vật
    - Kiểm tra va chạm 
    - Tạo chướng ngại vật ngẫu nhiên
    - Hiển thị bản đồ
    """
    
    # ========================================================================
    # PHƯƠNG THỨC __init__ - KHỞI TẠO MÔI TRƯỜNG
    # ========================================================================
    def __init__(self, width, height, obstacles=None):
        """
        Khởi tạo một môi trường bay mới.
        
        Tham số:
            width (float): Chiều rộng kiểm soát không gian bay (trục X)
            height (float): Chiều cao của không gian bay (trục Y)
            obstacles (list): Danh sách các chướng ngại vật dưới dạng tuple (x, y, w, h)
                            nếu None thì sẽ khởi tạo danh sách rỗng
        """
        self.width = width  # Lưu chiều rộng của môi trường
        self.height = height  # Lưu chiều cao của môi trường
        # Nếu không truyền vào danh sách chướng ngại vật thì khởi tạo danh sách rỗng
        # Nếu truyền vào thì sử dụng chính danh sách đó
        self.obstacles = obstacles if obstacles else []

    # ========================================================================
    # PHƯƠNG THỨC is_inside_obstacle - KIỂM TRA ĐIỂM CÓ TRONG CHƯỚNG NGẠI VẬT
    # ========================================================================
    def is_inside_obstacle(self, x, y):
        """
        Kiểm tra xem một điểm (x, y) có nằm bên trong bất kỳ chướng ngại vật nào không.
        
        Phương pháp:
        1. Trước hết kiểm tra xem điểm có nằm ngoài ranh giới môi trường không
        2. Nếu nằm trong ranh giới, lặp qua từng chướng ngại vật
        3. Dùng hàm point_in_rectangle để kiểm tra
        
        Tham số:
            x (float): Tọa độ X của điểm cần kiểm tra
            y (float): Tọa độ Y của điểm cần kiểm tra
        
        Trả về:
            bool: True nếu điểm nằm trong chướng ngại vật hoặc ngoài ranh giới
                  False nếu điểm nằm trong vùng an toàn
        """
        # Kiểm tra nếu điểm nằm ngoài ranh giới của môi trường
        # x < 0 hoặc x > width hoặc y < 0 hoặc y > height đều là điểm ngoài ranh giới
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return True  # Coi điểm ngoài ranh giới như va chạm

        # Lặp qua từng chướng ngại vật trong danh sách để kiểm tra
        for ox, oy, ow, oh in self.obstacles:
            # ox, oy là tọa độ góc trái dưới của hình chữ nhật chướng ngại vật
            # ow, oh là chiều rộng và chiều cao của chướng ngại vật
            # Dùng hàm point_in_rectangle để kiểm tra điểm có trong hình chữ nhật không
            if point_in_rectangle(x, y, ox, oy, ow, oh):
                return True  # Tìm thấy điểm nằm trong một chướng ngại vật

        return False  # Nếu không nằm trong bất kỳ chướng ngại vật nào, trả về False

    # ========================================================================
    # PHƯƠNG THỨC is_collision - KIỂM TRA VA CHẠM ĐƯỜNG THẲNG
    # ========================================================================
    def is_collision(self, p1, p2):
        """
        Kiểm tra xem đoạn thẳng từ p1 đến p2 có va chạm với chướng ngại vật không.
        
        Phương pháp kiểm tra:
        1. Kiểm tra xem hai điểm đầu mút có nằm trong chướng ngại vật không
        2. Kiểm tra xem đoạn thẳng có giao với bất kỳ chướng ngại vật nào không
        
        Tham số:
            p1 (tuple): Tọa độ (x1, y1) của điểm bắt đầu
            p2 (tuple): Tọa độ (x2, y2) của điểm kết thúc
        
        Trả về:
            bool: True nếu có va chạm, False nếu an toàn
        """
        x1, y1 = p1  # Tách tọa độ điểm bắt đầu thành x1 và y1
        x2, y2 = p2  # Tách tọa độ điểm kết thúc thành x2 và y2

        # Kiểm tra nếu cả hai điểm đầu mút có nằm trong chướng ngại vật
        # Nếu một trong hai điểm ở trong chướng ngại vật thì coi như đoạn thẳng va chạm
        if self.is_inside_obstacle(x1, y1) or self.is_inside_obstacle(x2, y2):
            return True  # Phát hiện va chạm

        # Lặp qua từng chướng ngại vật để kiểm tra xem đoạn thẳng có cắt nó không
        for ox, oy, ow, oh in self.obstacles:
            # Dùng hàm line_rectangle_collision để kiểm tra xem đoạn thẳng
            # từ (x1, y1) đến (x2, y2) có giao với hình chữ nhật (ox, oy, ow, oh) không
            if line_rectangle_collision(x1, y1, x2, y2, ox, oy, ow, oh):
                return True  # Phát hiện va chạm

        return False  # Nếu không va chạm với bất kỳ chướng ngại vật nào

    # ========================================================================
    # PHƯƠNG THỨC TĨN (STATIC) generate_random_obstacles - TẠO CHƯỚNG NGẠI VẬT NGẪU NHIÊN
    # ========================================================================
    @staticmethod
    def generate_random_obstacles(
        width, height, num_obstacles=5, min_size=5, max_size=20, seed=None
    ):
        """
        Tạo một danh sách các chướng ngại vật ngẫu nhiên cho môi trường.
        
        Phương pháp:
        1. Nếu có seed, thiết lập để đảm bảo kết quả có thể lặp lại
        2. Lặp n lần để tạo n chướng ngại vật với tọa độ và kích thước ngẫu nhiên
        3. Điều chỉnh vị trí và kích thước để chắc chắn nằm trong môi trường
        
        Tham số:
            width (float): Chiều rộng của môi trường
            height (float): Chiều cao của môi trường
            num_obstacles (int): Số lượng chướng ngại vật cần tạo (mặc định: 5)
            min_size (float): Kích thước tối thiểu của chướng ngại vật (mặc định: 5)
            max_size (float): Kích thước tối đa của chướng ngại vật (mặc định: 20)
            seed (int): Hạt ngẫu nhiên để tạo ra kết quả lặp lại được (mặc định: None)
        
        Trả về:
            list: Danh sách các chướng ngại vật dưới dạng tuple (x, y, w, h)
        """
        # Nếu seed được cung cấp, thiết lập seed cho cả random và numpy
        # Điều này đảm bảo kết quả ngẫu nhiên có thể tái tạo lại được
        if seed is not None:
            random.seed(seed)  # Thiết lập seed cho module random của Python
            np.random.seed(seed)  # Thiết lập seed cho module numpy

        obstacles = []  # Khởi tạo danh sách rỗng để lưu các chướng ngại vật

        # Lặp num_obstacles lần để tạo mỗi chướng ngại vật
        for _ in range(num_obstacles):
            # Tạo ngẫu nhiên tọa độ x từ 0 đến (width - min_size)
            # max(0, width - min_size) đảm bảo không tạo ra số âm
            x = random.uniform(0, max(0, width - min_size))
            # Tạo ngẫu nhiên tọa độ y từ 0 đến (height - min_size)
            y = random.uniform(0, max(0, height - min_size))

            # Tạo ngẫu nhiên chiều rộng từ min_size đến max_size
            w = random.uniform(min_size, max_size)
            # Tạo ngẫu nhiên chiều cao từ min_size đến max_size
            h = random.uniform(min_size, max_size)

            # Điều chỉnh tọa độ x để nằm trong khoảng [0, width]
            # max(0, ...) đảm bảo x không âm
            # min(..., width) đảm bảo x không vượt quá width
            x = max(0, min(x, width))
            # Điều chỉnh tọa độ y để nằm trong khoảng [0, height]
            y = max(0, min(y, height))
            # Điều chỉnh chiều rộng để đảm bảo chướng ngại vật không vượt quá ranh giới bên phải
            w = min(w, width - x)
            # Điều chỉnh chiều cao để đảm bảo chướng ngại vật không vượt quá ranh giới phía trên
            h = min(h, height - y)

            # Thêm một bộ 4 giá trị (x, y, w, h) vào danh sách chướng ngại vật
            obstacles.append((x, y, w, h))

        return obstacles  # Trả về danh sách đầy đủ các chướng ngại vật

    # ========================================================================
    # PHƯƠNG THỨC visualize - HIỂN THỊ BẢN ĐỒ MÔI TRƯỜNG
    # ========================================================================
    def visualize(self, path=None, title="Map", show_goal=None):
        """
        Hiển thị hình ảnh bản đồ môi trường với các chướng ngại vật, đường đi và mục tiêu.
        
        Các yếu tố hiển thị:
        - Chướng ngại vật: Hình chữ nhật màu đỏ
        - Đường đi: Đường thẳng màu xanh dương
        - Điểm bắt đầu: Vòng tròn màu xanh lục
        - Điểm kết thúc: Sao màu đỏ
        
        Tham số:
            path (list): Danh sách các điểm tạo thành đường đi (mặc định: None)
            title (str): Tiêu đề của biểu đồ (mặc định: "Map")
            show_goal (tuple): Tọa độ (x, y) của mục tiêu nếu không có đường đi (mặc định: None)
        """
        # Tạo một hình vẽ (figure) mới với kích thước 10 inch × 10 inch
        fig, ax = plt.subplots(figsize=(10, 10))

        # Thiết lập giới hạn của trục X từ -5 đến width + 5
        # Phần -5 đến 0 và width đến width+5 tạo không gian trống để dễ nhìn
        ax.set_xlim(-5, self.width + 5)
        # Thiết lập giới hạn của trục Y từ -5 đến height + 5
        ax.set_ylim(-5, self.height + 5)
        # Thiết lập tỷ lệ khung hình bằng 1:1 để tránh méo dạng hình vẽ
        ax.set_aspect("equal")
        # Hiển thị lưới nền với độ trong suốt (alpha) = 0.3 (nhẹ)
        ax.grid(True, alpha=0.3)
        # Thiết lập nhãn cho trục X
        ax.set_xlabel("X")
        # Thiết lập nhãn cho trục Y
        ax.set_ylabel("Y")
        # Thiết lập tiêu đề cho biểu đồ
        ax.set_title(title)

        # Lặp qua từng chướng ngại vật để vẽ nó
        for ox, oy, ow, oh in self.obstacles:
            # Tạo một đối tượng hình chữ nhật tại vị trí (ox, oy) với chiều rộng ow và chiều cao oh
            rect = patches.Rectangle(
                (ox, oy),  # Tọa độ góc trái dưới của hình chữ nhật
                ow,  # Chiều rộng của hình chữ nhật
                oh,  # Chiều cao của hình chữ nhật
                linewidth=2,  # Độ dày của đường viền (2 điểm)
                edgecolor="red",  # Màu của đường viền - đỏ
                facecolor="red",  # Màu nền của hình chữ nhật - đỏ
                alpha=0.5,  # Độ trong suốt (0.5 = 50% trong suốt)
            )
            # Thêm hình chữ nhật vào trục (ax)
            ax.add_patch(rect)

        # Kiểm tra nếu có đường đi và danh sách đường đi không rỗng
        if path is not None and len(path) > 0:
            path = np.array(path)  # Chuyển danh sách đường đi thành mảng numpy để dễ xử lý

            # Vẽ đường đi dưới dạng một đường thẳng liên tục màu xanh dương
            # path[:, 0] là tất cả tọa độ X, path[:, 1] là tất cả tọa độ Y
            ax.plot(path[:, 0], path[:, 1], "b-", linewidth=2, label="Path")
            # Vẽ điểm bắt đầu (phần tử đầu tiên) dưới dạng vòng tròn màu xanh lục
            # "go" = green circle
            ax.plot(path[0, 0], path[0, 1], "go", markersize=10, label="Start")
            # Vẽ điểm kết thúc (phần tử cuối cùng) dưới dạng sao màu đỏ
            # "r*" = red star
            ax.plot(path[-1, 0], path[-1, 1], "r*", markersize=15, label="Goal")
            # Thêm chú giải (legend) để hiển thị các nhãn Path, Start, Goal
            ax.legend()
        # Nếu không có đường đi nhưng có mục tiêu để hiển thị
        elif show_goal is not None:
            # Vẽ điểm mục tiêu dưới dạng sao màu đỏ
            ax.plot(show_goal[0], show_goal[1], "r*", markersize=15, label="Goal")
            # Thêm chú giải
            ax.legend()

        # Tự động điều chỉnh khoảng cách giữa các yếu tố trong hình vẽ để tránh bị cắt xén
        plt.tight_layout()
        # Hiển thị biểu đồ lên màn hình
        plt.show()

    # ========================================================================
    # PHƯƠNG THỨC visualize_multiple_paths - HIỂN THỊ NHIỀU ĐƯỜNG ĐI
    # ========================================================================
    def visualize_multiple_paths(self, paths_dict, title="Map"):
        """
        Hiển thị nhiều đường đi cùng lúc trên một bản đồ để so sánh.
        
        Ứng dụng:
        - So sánh các đường đi tìm được bằng các thuật toán khác nhau
        - Hiển thị độ dài của từng đường đi
        - Dễ dàng nhận biết đường đi tốt nhất
        
        Phương pháp:
        1. Vẽ tất cả chướng ngại vật
        2. Vẽ từng đường đi với màu sắc khác nhau
        3. Tính và hiển thị độ dài của mỗi đường đi
        4. Hiển thị điểm bắt đầu và kết thúc duy nhất
        
        Tham số:
            paths_dict (dict): Dictionary với định dạng {"tên_đường_đi": [điểm1, điểm2, ...]}
                             Ví dụ: {"RRT": [(0,0), (10,10), ...], "PSO": [...]}
            title (str): Tiêu đề của biểu đồ (mặc định: "Map")
        """
        # Tạo một hình vẽ mới với kích thước 10x10 inch
        fig, ax = plt.subplots(figsize=(10, 10))

        # Thiết lập giới hạn trục X
        ax.set_xlim(-5, self.width + 5)
        # Thiết lập giới hạn trục Y
        ax.set_ylim(-5, self.height + 5)
        # Tỷ lệ khung hình 1:1
        ax.set_aspect("equal")
        # Hiển thị lưới nền
        ax.grid(True, alpha=0.3)
        # Nhãn trục X
        ax.set_xlabel("X")
        # Nhãn trục Y
        ax.set_ylabel("Y")
        # Tiêu đề biểu đồ
        ax.set_title(title)

        # Vẽ tất cả chướng ngại vật
        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle(
                (ox, oy),
                ow,
                oh,
                linewidth=2,
                edgecolor="red",
                facecolor="red",
                alpha=0.5,
            )
            ax.add_patch(rect)

        # Danh sách màu sắc để phân biệt các đường đi khác nhau
        # Nếu có nhiều hơn 5 đường thì sẽ lặp lại các màu
        colors = ["blue", "green", "orange", "purple", "brown"]

        # Lặp qua từng đường đi trong dictionary
        for idx, (name, path) in enumerate(paths_dict.items()):
            # Kiểm tra nếu đường đi tồn tại và không rỗng
            if path is not None and len(path) > 0:
                path = np.array(path)  # Chuyển thành mảng numpy
                # Chọn màu từ danh sách (nếu vượt quá sẽ lặp lại)
                color = colors[idx % len(colors)]
                # Tính độ dài của đường đi
                length = path_length(path)
                # Vẽ đường đi với nhãn hiển thị tên và độ dài
                # Nhãn format: "RRT (L=50.25)" - chữ L viết tắt cho Length
                ax.plot(
                    path[:, 0],
                    path[:, 1],
                    color=color,
                    linewidth=2,
                    label=f"{name} (L={length:.2f})",  # .2f = 2 chữ số sau dấu phẩy
                )

                # Chỉ vẽ điểm bắt đầu một lần (cho đường đi đầu tiên)
                if idx == 0:
                    ax.plot(path[0, 0], path[0, 1], "go", markersize=10, label="Start")

        # Lấy đường đi cuối cùng từ dictionary
        last_path = list(paths_dict.values())[-1]
        # Kiểm tra và vẽ điểm kết thúc (từ đường đi cuối cùng)
        if last_path is not None and len(last_path) > 0:
            last_path = np.array(last_path)
            # Vẽ điểm cuối cùng của đường đi cuối cùng
            ax.plot(
                last_path[-1, 0], last_path[-1, 1], "r*", markersize=15, label="Goal"
            )

        # Thêm chú giải để hiển thị tất cả các nhãn
        ax.legend()
        # Tự động điều chỉnh bố cục
        plt.tight_layout()
        # Hiển thị
        plt.show()

    # ========================================================================
    # PHƯƠNG THỨC save_map - LƯU BẢN ĐỒ VÀO TỆP
    # ========================================================================
    def save_map(self, map_name="map"):
        """
        Lưu bản đồ vào thư mục với hai dạng:
        1. File JSON chứa thông tin cấu hình bản đồ (kích thước, chướng ngại vật)
        2. File PNG chứa hình ảnh trực quan của bản đồ
        
        Cấu trúc thư mục được tạo:
            maps/
            └── map_name_YYYYMMDD_HHMMSS/
                ├── config.json    (thông tin cấu hình)
                └── map.png        (hình ảnh PNG)
        
        Phương pháp:
        1. Tạo thư mục "maps" nếu chưa tồn tại
        2. Tạo thư mục con với tên bản đồ + timestamp
        3. Lưu thông tin cấu hình vào file JSON
        4. Vẽ và lưu hình ảnh bản đồ thành PNG
        
        Tham số:
            map_name (str): Tên của bản đồ (mặc định: "map")
        
        Trả về:
            str: Đường dẫn thư mục chứa bản đồ đã lưu
        """
        # Đặt tên thư mục chính để lưu trữ tất cả bản đồ
        maps_dir = "maps"
        # Kiểm tra nếu thư mục "maps" chưa tồn tại thì tạo mới
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)

        # Tạo timestamp hiện tại dưới dạng: 20260310_143025
        # Format: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Tạo đường dẫn thư mục con: maps/map_20260310_143025
        save_dir = os.path.join(maps_dir, f"{map_name}_{timestamp}")

        # Kiểm tra và tạo thư mục con nếu chưa tồn tại
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Tạo dictionary chứa tất cả thông tin cấu hình bản đồ
        config = {
            "name": map_name,  # Tên bản đồ
            "timestamp": timestamp,  # Thời gian lưu
            "width": self.width,  # Chiều rộng môi trường
            "height": self.height,  # Chiều cao môi trường
            "obstacles": self.obstacles,  # Danh sách chướng ngại vật
        }

        # Tạo đường dẫn file JSON
        json_path = os.path.join(save_dir, "config.json")
        # Mở file để ghi
        with open(json_path, "w") as f:
            # Lưu dictionary thành JSON với indentation = 2 để dễ đọc
            json.dump(config, f, indent=2)

        # In thông báo lưu thành công
        print(f"[SAVE] JSON config: {json_path}")

        # Vẽ bản đồ để lưu thành hình ảnh
        fig, ax = plt.subplots(figsize=(10, 10))

        # Thiết lập trục
        ax.set_xlim(-5, self.width + 5)
        ax.set_ylim(-5, self.height + 5)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(f"Map: {map_name}")

        # Vẽ tất cả chướng ngại vật
        for ox, oy, ow, oh in self.obstacles:
            rect = patches.Rectangle(
                (ox, oy),
                ow,
                oh,
                linewidth=2,
                edgecolor="red",
                facecolor="red",
                alpha=0.5,
            )
            ax.add_patch(rect)

        # Vẽ điểm gốc (origin) tại (0, 0)
        ax.plot(0, 0, "go", markersize=10, label="Origin")
        # Thêm chú giải
        ax.legend()
        # Tự động điều chỉnh bố cục
        plt.tight_layout()

        # Tạo đường dẫn file PNG
        image_path = os.path.join(save_dir, "map.png")
        # Lưu hình vẽ thành file PNG với độ phân giải 100 DPI
        # bbox_inches="tight" để loại bỏ khoảng trắng thừa xung quanh
        fig.savefig(image_path, dpi=100, bbox_inches="tight")
        # Đóng hình vẽ để giải phóng bộ nhớ
        plt.close(fig)

        # In thông báo lưu thành công
        print(f"[SAVE] Map image: {image_path}")
        print(f"[SAVE] Map saved to: {save_dir}")

        # Trả về đường dẫn thư mục đã lưu
        return save_dir

    # ========================================================================
    # PHƯƠNG THỨC TĨN (STATIC) load_map - TẢI BẢN ĐỒ TỪ TỆP
    # ========================================================================
    @staticmethod
    def load_map(map_path):
        """
        Tải bản đồ từ file JSON được lưu trước đó.
        
        Phương pháp:
        1. Xác định đường dẫn đến file config.json
        2. Đọc file JSON để lấy thông tin cấu hình
        3. Tạo một object UAVEnvironment mới với thông tin đã đọc
        4. In thông điệp xác nhận
        
        Tham số:
            map_path (str): Đường dẫn tới:
                          - File config.json trực tiếp, hoặc
                          - Thư mục chứa file config.json
                          Ví dụ: "maps/map_20260310_143025/config.json"
                         hoặc: "maps/map_20260310_143025"
        
        Trả về:
            UAVEnvironment: Một object UAVEnvironment được tải lại với thông tin cũ
        
        Raise:
            FileNotFoundError: Nếu file config.json không tìm thấy
        """
        # Kiểm tra nếu map_path kết thúc bằng "config.json"
        if map_path.endswith("config.json"):
            # Nếu là file JSON thì lấy trực tiếp
            json_path = map_path
            # Lấy thư mục chứa file JSON
            map_dir = os.path.dirname(map_path)
        else:
            # Nếu là đường dẫn thư mục thì tạo đường dẫn đến config.json
            map_dir = map_path
            json_path = os.path.join(map_dir, "config.json")

        # Kiểm tra xem file JSON có tồn tại không
        if not os.path.exists(json_path):
            # Nếu không tồn tại thì ném ra lỗi
            raise FileNotFoundError(f"Config file not found: {json_path}")

        # Mở file JSON để đọc
        with open(json_path, "r") as f:
            # Chuyển dữ liệu JSON thành dictionary
            config = json.load(f)

        # Lấy thông tin từ dictionary
        width = config.get("width")  # Lấy chiều rộng
        height = config.get("height")  # Lấy chiều cao
        obstacles = config.get("obstacles", [])  # Lấy danh sách chướng ngại vật (nếu không có thì [])

        # Chuyển danh sách obstacles thành tuples
        # Vì JSON lưu danh sách dưới dạng list, nên cần chuyển lại thành tuple
        obstacles = [tuple(obs) for obs in obstacles]

        # Tạo một object UAVEnvironment mới với thông tin đã tải
        env = UAVEnvironment(width, height, obstacles)

        # In thông báo thành công
        print(f"[LOAD] Map loaded from: {map_dir}")
        print(f"[LOAD] Width: {width}, Height: {height}")
        print(f"[LOAD] Obstacles: {len(obstacles)}")

        # Trả về object UAVEnvironment
        return env

    # ========================================================================
    # PHƯƠNG THỨC get_map_info - LẤY THÔNG TIN BẢN ĐỒ
    # ========================================================================
    def get_map_info(self):
        """
        Lấy tossn bộ thông tin về bản đồ hiện tại dưới dạng dictionary.
        
        Ứng dụng:
        - Lấy thông tin nhanh về bản đồ
        - In ra thông tin bản đồ để kiểm tra
        - Dùng cho logging hoặc debugging
        
        Trả về:
            dict: Dictionary chứa các thông tin:
                - "width": Chiều rộng môi trường
                - "height": Chiều cao môi trường
                - "num_obstacles": Số lượng chướng ngại vật
                - "obstacle_details": Chi tiết từng chướng ngại vật [(x, y, w, h), ...]
        """
        return {
            "width": self.width,  # Chiều rộng
            "height": self.height,  # Chiều cao
            "num_obstacles": len(self.obstacles),  # Số lượng chướng ngại vật
            "obstacle_details": self.obstacles,  # Chi tiết các chướng ngại vật
        }


# ============================================================================
# PHẦN TEST - CHẠY KHI TỆP ĐƯỢC CHẠY TRỰC TIẾP
# ============================================================================
if __name__ == "__main__":
    # Phần này chỉ chạy khi file được chạy trực tiếp, không chạy khi được import
    
    # ===== CÁCH 1: TẠO BẢN ĐỒ MỚI VÀ LƯU ĐI =====
    # Bỏ comment để sử dụng
    # obstacles = UAVEnvironment.generate_random_obstacles(
    #     width=100, height=100, num_obstacles=10
    # )
    # new_map = UAVEnvironment(100, 100, obstacles)
    # new_map.save_map()

    # ===== CÁCH 2: TẢI BẢN ĐỒ TỪ TỆP LƯU TRỮ =====
    loaded_map = UAVEnvironment.load_map(
        r"D:\DEV\_Projects\TLU\DoAn\rrt-pso-find-path\maps\map_20260302_162124\config.json"
    )
    # In ra danh sách chướng ngại vật của bản đồ đã tải
    print(loaded_map.obstacles)
    # Bỏ comment để hiển thị bản đồ
    # loaded_map.visualize()
