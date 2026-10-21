"""
=============================================================================
Traveling Salesman Problem (TSP) Solver using Particle Swarm Optimization
=============================================================================

BÀI TOÁN TSP (Traveling Salesman Problem):
- Cho n thành phố với tọa độ [x, y] xác định
- Tìm hành trình đi qua tất cả thành phố đúng 1 lần rồi quay lại điểm xuất phát
- Mục tiêu: Tối thiểu hóa tổng khoảng cách = NP-hard problem

GIAI PHÁP: Particle Swarm Optimization (PSO)
- Thuật toán meta-heuristic lấy cảm hứng từ hành vi bầy chim/đàn cá
- Mỗi "hạt" (particle) đại diện cho một giải pháp (tour)
- Hạt di chuyển trong không gian tìm kiếm để tìm giải pháp tốt nhất
- Dựa trên kinh nghiệm cá nhân + kinh nghiệm của bầy đàn

CÔNG THỨC CẬP NHẬT VẬN TỐC PSO:
v(t+1) = w*v(t) + c1*r1*(pbest - x(t)) + c2*r2*(gbest - x(t))
Trong đó:
  - w: Inertia weight (quán tính) - cân bằng giữa khám phá & khai thác
  - c1: Cognitive parameter - hệ số tu nhân (lấy kinh nghiệm riêng)
  - c2: Social parameter - hệ số xã hội (lấy kinh nghiệm bầy đàn)
  - r1, r2: Số ngẫu nhiên trong [0,1]
  - pbest: Vị trí tốt nhất cá nhân từng tìm thấy
  - gbest: Vị trí tốt nhất toàn bộ bầy đã tìm thấy

=============================================================================
"""

import numpy as np
# Tuple, List để type hint cho hàm (giúp VS Code auto-complete tốt hơn)
from typing import Tuple, List
# matplotlib để vẽ biểu đồ kết quả và curve hội tụ
import matplotlib.pyplot as plt


class TSPProblem:
    """
    Lớp quản lý bài toán TSP - tính toán khoảng cách giữa các thành phố
    
    Các thành phố được biểu diễn bằng tọa độ [x, y] trong không gian 2D.
    Khoảng cách được tính bằng khoảng cách Euclid giữa hai điểm.
    """
    
    def __init__(self, cities: np.ndarray):
        """
        Khởi tạo bài toán TSP với tọa độ các thành phố
        
        Args:
            cities (np.ndarray): Mảng numpy hình dạng (n_cities, 2) chứa [x, y]
                                 tọa độ của mỗi thành phố
                                 Ví dụ: [[0, 0], [10, 15], [20, 5], ...]
        """
        # Lưu danh sách tọa độ các thành phố
        self.cities = cities
        # Tính số lượng thành phố
        self.n_cities = len(cities)
        # Khởi tạo ma trận khoảng cách = None (sẽ tính lần đầu tiên sử dụng)
        # Điều này gọi là "lazy loading" - chỉ tính khi cần
        self._distance_matrix = None
    
    @property
    def distance_matrix(self) -> np.ndarray:
        """
        Tính và lưu trữ ma trận khoảng cách Euclid giữa các thành phố
        
        Sử dụng @property giúp sử dụng như một thuộc tính (không cần gọi như hàm)
        Ví dụ: problem.distance_matrix (thay vì problem.distance_matrix())
        
        Returns:
            np.ndarray: Ma trận n x n với distance_matrix[i][j] = khoảng cách từ i đến j
        """
        # Kiểm tra xem ma trận đã tính chưa (lazy loading)
        if self._distance_matrix is None:
            n = self.n_cities
            # Tạo ma trận zeros kích thước n x n để lưu khoảng cách
            self._distance_matrix = np.zeros((n, n))
            
            # Tính khoảng cách giữa mỗi cặp thành phố
            for i in range(n):
                # Chỉ tính nửa trên của ma trận (vì ma trận đối xứng: d(i,j) = d(j,i))
                for j in range(i + 1, n):
                    # Công thức Euclid: sqrt((x1-x2)^2 + (y1-y2)^2)
                    dist = np.linalg.norm(self.cities[i] - self.cities[j])
                    # Lưu vào cả hai vị trí (đối xứng)
                    self._distance_matrix[i][j] = dist
                    self._distance_matrix[j][i] = dist
        
        return self._distance_matrix
    
    def calculate_tour_distance(self, tour: List[int]) -> float:
        """
        Tính tổng khoảng cách của một hành trình hoàn chỉnh
        
        Hành trình là: thành phố tour[0] -> tour[1] -> ... -> tour[-1] -> tour[0]
        
        Args:
            tour (List[int]): Danh sách chỉ số thành phố theo thứ tự visit
                             Ví dụ: [0, 3, 1, 2] = thứ tự đi: 0 -> 3 -> 1 -> 2 -> 0
            
        Returns:
            float: Tổng khoảng cách của hành trình (độ dài tour)
        """
        # Khởi tạo tổng khoảng cách = 0
        distance = 0
        
        # Lặp qua mỗi thành phố trong hành trình
        for i in range(len(tour)):
            # Thành phố hiện tại
            from_city = tour[i]
            # Thành phố tiếp theo (dùng % để quay lại thành phố đầu khi hết)
            # Ví dụ: nếu i = len(tour)-1, thì (i+1) % len(tour) = 0
            to_city = tour[(i + 1) % len(tour)]
            
            # Cộng khoảng cách từ thành phố hiện tại đến thành phố tiếp theo
            distance += self.distance_matrix[from_city][to_city]
        
        return distance


class Particle:
    """
    Lớp đại diện cho một "hạt" (particle) trong bầy PSO
    
    Mỗi hạt đại diện cho:
    - position: một hành trình TSP (tour) đi qua tất cả các thành phố
    - velocity: "vận tốc" - hướng di chuyển để cải thiện tour
    - best_position: hành trình tốt nhất mà hạt từng tìm thấy
    """
    
    def __init__(self, n_cities: int, problem: TSPProblem):
        """
        Khởi tạo một hạt với hành trình ngẫu nhiên
        
        Args:
            n_cities (int): Số lượng thành phố
            problem (TSPProblem): Đối tượng bài toán TSP
        """
        # POSITION: Hành trình hiện tại của hạt
        # np.random.permutation(n) tạo một hoán vị ngẫu nhiên của [0, 1, ..., n-1]
        # Ví dụ: [2, 0, 3, 1] = tour: 2 -> 0 -> 3 -> 1 -> 2
        self.position = np.random.permutation(n_cities)
        
        # VELOCITY: Vận tốc PSO - biểu diễn xu hướng di chuyển
        # Bắt đầu bằng 0 (chưa di chuyển gì)
        self.velocity = np.zeros_like(self.position, dtype=float)
        
        # Lưu reference đến bài toán (để tính khoảng cách)
        self.problem = problem
        
        # BEST_POSITION: Hành trình tốt nhất mà hạt từng tìm thấy
        # Bắt đầu = position hiện tại
        self.best_position = self.position.copy()  # .copy() để tạo copy, không share memory
        
        # BEST_DISTANCE: Khoảng cách của best_position
        self.best_distance = problem.calculate_tour_distance(list(self.best_position))
        
        # CURRENT_DISTANCE: Khoảng cách của position hiện tại
        self.current_distance = self.best_distance
    
    def update_velocity(self, global_best: np.ndarray, w: float, c1: float, c2: float):
        """
        Cập nhật vận tốc sử dụng công thức PSO chuẩn
        
        Công thức:
        v(t+1) = w*v(t) + c1*r1*(pbest - x(t)) + c2*r2*(gbest - x(t))
        
        Args:
            global_best (np.ndarray): Hành trình tốt nhất của toàn bộ bầy
            w (float): Trọng số quán tính (inertia weight) - cân bằng khám phá/khai thác
                      - w gần 1: khám phá nhiều hơn (exploration)
                      - w nhỏ: khai thác nhiều hơn (exploitation)
            c1 (float): Tham số nhận thức (cognitive) - độ mạnh lực hút về best của riêng mình
                       Thường = 1.5 hoặc 2.0
            c2 (float): Tham số xã hội (social) - độ mạnh lực hút về best toàn bộ bầy
                       Thường = 1.5 hoặc 2.0
        """
        # Sinh hai số ngẫu nhiên trong khoảng [0, 1]
        # Để tránh hạt luôn di chuyển theo cùng hướng
        r1, r2 = np.random.random(2)
        
        # CẬP NHẬT VẬN TỐC theo công thức PSO:
        # v_new = w*v_old + c1*r1*(pbest - x) + c2*r2*(gbest - x)
        # 
        # Giải thích từng thành phần:
        # 1. w * self.velocity: Giữ lại vận tốc cũ (quán tính)
        # 2. c1*r1*(best_position - position): Kéo về best cá nhân
        #    - Là chênh lệch giữa best position và current position
        #    - Nhân với r1 để randomize, c1 để điều chỉnh độ mạnh
        # 3. c2*r2*(global_best - position): Kéo về best toàn bộ bầy
        #    - Là chênh lệch giữa global best và current position
        #    - Nhân với r2 để randomize, c2 để điều chỉnh độ mạnh
        self.velocity = (w * self.velocity +
                        c1 * r1 * (self.best_position - self.position) +
                        c2 * r2 * (global_best - self.position))
    
    def update_position(self, problem: TSPProblem):
        """
        Cập nhật vị trí (position) của hạt dựa trên vận tốc vừa tính
        
        Vì đây là bài toán TSP (permutation problem), không thể cộng vận tốc 
        vào position như trong continuous optimization.
        Thay vào đó, ta sử dụng độ lớn của velocity để quyết định xác suất swap.
        
        Phương pháp: 2-opt style moves
        - 2-opt: Chọn 2 thành phố và đảo ngược phần tour giữa chúng
        - Tạo nhiều tour mới từ tour hiện tại
        """
        # Chuẩn hóa velocity thành xác suất di chuyển (trong [0, 1])
        # - Velocity lớn = xác suất swap lớn
        # - Velocity nhỏ = xác suất swap nhỏ
        # Công thức: (v - min) / (max - min) chuẩn hóa vào [0, 1]
        # Thêm 1e-10 để tránh chia cho 0
        movement_probability = (self.velocity - self.velocity.min()) / (self.velocity.max() - self.velocity.min() + 1e-10)
        
        # Tạo tour mới bằng cách copy tour hiện tại
        new_position = self.position.copy()
        
        # ÁP DỤNG 2-OPT SWAP:
        # 2-opt: Chọn hai thành phố và đảo ngược phần tour giữa chúng
        # Ví dụ tour [0, 3, 1, 2]:
        # - Swap giữa index 1 và 3: đảo [3, 1] thành [1, 3] -> [0, 1, 3, 2]
        # Điều này giúp cải thiện tour (nếu có crossing edges, 2-opt loại bỏ chúng)
        for i in range(len(new_position)):
            # Xác suất 10% để thực hiện swap từ vị trí i
            # Có thể điều chỉnh: 0.1 = 10% (thêm hay bớt swap)
            if np.random.random() < 0.1:
                # Chọn ngẫu nhiên một vị trí khác để swap
                j = np.random.randint(0, len(new_position))
                # Đảo hai thành phố tại index i và j
                new_position[i], new_position[j] = new_position[j], new_position[i]
        
        # Cập nhật position của hạt thành tour mới
        self.position = new_position
        
        # Tính khoảng cách của tour mới
        self.current_distance = problem.calculate_tour_distance(list(self.position))
        
        # CẬP NHẬT BEST_POSITION (nếu tìm được tour tốt hơn)
        # Điều này là "memory" của hạt - nó nhớ tour tốt nhất từng tìm
        if self.current_distance < self.best_distance:
            self.best_distance = self.current_distance
            self.best_position = self.position.copy()


class PSO:
    """
    Lớp Particle Swarm Optimization (Öt "theng" PSO) - giải pháp chính cho TSP
    
    Cập NHẬT CHI TIẾT THUẬT TOÁN:
    1. Khởi tạo: Tạo n_particles hạt với tour ngẫu nhiên
    2. Lặp lại max_iterations lần:
       a) Mỗi hạt cập nhật vận tốc dựa trên:
          - Quán tính (inertia weight)
          - Đã tìm thấy tốt của riêng họ (cognitive)
          - Đã tìm thấy tốt của bầy (social)
       b) Mỗi hạt cập nhật vị trí (tour) dựa trên vận tỐ
       c) Cập nhật global best nếu tÌm thấy tốt hơn
       d) Giảm inertia weight (w *= 0.99) để tăng độ không định seeded
    3) Trả về best tour và lịch sử hội tụ
    
    Lưu Ý: Có thể điều chỉnh các tham số để thỉ với các bài toán khác nhau
    """
    
    def __init__(self, problem: TSPProblem, n_particles: int = 30, 
                 max_iterations: int = 500, w: float = 0.7, 
                 c1: float = 1.5, c2: float = 1.5):
        """
        Khởi tạo PSO solver
        
        Args:
            problem (TSPProblem): Đối tượng bài toán TSP
            n_particles (int): Số hạt trong bầy
                            - Mùi nhau = khím phá tốt hơn (slower)
                            - ít = nhanh hơn (nhưng có thể bỏ lỡ local minima)
                            - Mắc định: 30
            max_iterations (int): Số lần lặp tối đa
                                 - Nhiều lấp = hỉ vọng tốt hơn (slower)
                                 - ít lấp = nhanh hơn (nhưng có thể chưa hội tụ)
                                 - Mắc định: 500
            w (float): Trọng số quán tính (inertia weight)
                      - Giá trị cao (gần 1.0): Bạo tơn vận tỐ cũ -> khám phá nhiều
                      - Giá trị thấp (gần 0.4): Giảm vận tỐ -> khai thác nhiều
                      - Mị: 0.7 (cân bằng giữa khám phá và khai thác)
            c1 (float): Tham số nhẫn thức (cognitive parameter)
                       - Nền có giá trị > 0, thường 1.5 đến 2.5
                       - Càng cao, hạt càng "tự quý" (tập trung vào best của mình)
            c2 (float): Tham số xã hội (social parameter)
                       - Nền có giá trị > 0, thường 1.5 đến 2.5
                       - Càng cao, hạt càng "theo cập nã" (tập trung vào best của bầy)
        """
        # Lưu tham số bài toán
        self.problem = problem
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.w = w  # Sẽ thay đổi qua các lầp
        self.c1 = c1
        self.c2 = c2
        
        # KHỚI TẠO BẨY PSO:
        # Tạo n_particles hạt với tour ngẫu nhiên
        self.particles = [Particle(problem.n_cities, problem) for _ in range(n_particles)]
        
        # TÌM GLOBAL BEST BAN ĐẦU:
        # Tìm hạt có best_distance nhỏ nhất
        best_particle = min(self.particles, key=lambda p: p.best_distance)
        # Lưu global best position và distance
        self.global_best_position = best_particle.best_position.copy()
        self.global_best_distance = best_particle.best_distance
        
        # LỊCH Sậ: Lưu trữ global best distance qua các lầp
        # Dùng để vẽ biểu đồ hội tụ (convergence curve)
        self.best_distance_history = [self.global_best_distance]
    
    def solve(self) -> Tuple[List[int], float, List[float]]:
        """
        Giải TSP sử dụng PSO algorithm
        
        Quá trình:
        1. Trong mỗi iteration:
           - Mỗi hạt cập nhật vận tốc (bị kéo bởi best cá nhân + best toàn bộ)
           - Mỗi hạt cập nhật vị trí (tour) dựa trên vận tốc mới
           - Cập nhật best cá nhân nếu tìm thấy tour tốt hơn
           - Cập nhật best toàn bộ bầy nếu một hạt tìm thấy tour tốt hơn cả bầy
        2. Giảm inertia weight (w *= 0.99) qua các iteration
           - Lúc đầu: w cao = khám phá nhiều (exploration)
           - Lúc sau: w thấp = khai thác (exploitation)
        3. Lưu lịch sử best distance để vẽ convergence curve
        
        Returns:
            Tuple gồm:
            - best_tour (List[int]): Hành trình tốt nhất tìm thấy
            - best_distance (float): Độ dài của hành trình tốt nhất
            - best_distance_history (List[float]): Lịch sử thay đổi best distance
        """
        # VÒNG LẶP CHÍNH: Thực hiện max_iterations lần
        for iteration in range(self.max_iterations):
            # Cập nhật mỗi hạt trong bầy
            for particle in self.particles:
                # 1. CẬP NHẬT VẬN TỐC
                # Hạt bị kéo bởi:
                # - Best cá nhân (bước đi tốt nhất của riêng nó)
                # - Best toàn bộ (bước đi tốt nhất của cả bầy)
                particle.update_velocity(self.global_best_position, 
                                        self.w, self.c1, self.c2)
                
                # 2. CẬP NHẬT VỊ TRÍ (TOUR)
                # Dùng 2-opt moves để tạo tour mới dựa trên vận tốc
                particle.update_position(self.problem)
                
                # 3. CẬP NHẬT GLOBAL BEST
                # Nếu hạt này tìm thấy best_distance tốt hơn cả bầy
                if particle.best_distance < self.global_best_distance:
                    # Cập nhật global best
                    self.global_best_distance = particle.best_distance
                    self.global_best_position = particle.best_position.copy()
            
            # 4. GIẢM INERTIA WEIGHT (w)
            # Công thức giản đơn: w = w * 0.99
            # - Lúc đầu: w = 0.7 -> khám phá nhiều
            # - Lúc sau: w = 0.7 * 0.99^500 ≈ 0.006 -> khai thác nhiều
            # Cách khác: w = w_initial - (w_initial - w_final) * iteration / max_iterations
            self.w *= 0.99
            
            # 5. LƯU LỊCH SỬ BEST DISTANCE
            # Dùng để theo dõi quá trình hội tụ
            self.best_distance_history.append(self.global_best_distance)
            
            # 6. IN KẾT QUẢ TRUNG GIAN (mỗi 50 iteration)
            # Giúp biết thuật toán đang chạy và tiến độ như thế nào
            if (iteration + 1) % 50 == 0:
                print(f"Iteration {iteration + 1}: Best distance = {self.global_best_distance:.2f}")
        
        # TRẢ VỀ KẾT QUẢ CUỐI CÙNG
        return (list(self.global_best_position),           # Best tour tìm thấy
                self.global_best_distance,                  # Độ dài tốt nhất
                self.best_distance_history)                 # Lịch sử hội tụ


def generate_cities(n_cities: int, seed: int = None) -> np.ndarray:
    """
    Tạo ngẫu nhiên các thành phố trong không gian 2D
    
    Args:
        n_cities (int): Số lượng thành phố muốn tạo
        seed (int, optional): Random seed để có kết quả lặp lại
                             - None: Mỗi lần chạy sẽ tạo thành phố khác nhau
                             - Số nào đó (VD: 42): Mỗi lần chạy sẽ tạo thành phố giống nhau
                             Dùng seed để test lặp lại mà không thay đổi dữ liệu
    
    Returns:
        np.ndarray: Mảng shape (n_cities, 2) chứa [x, y] của mỗi thành phố
                   Tọa độ nằm trong khoảng [0, 100]
    """
    # Thiết lập random seed nếu có
    if seed is not None:
        np.random.seed(seed)
    
    # Tạo mảng random n_cities hàng x 2 cột
    # np.random.uniform(0, 100, size=(n_cities, 2)):
    # - Tạo số ngẫu nhiên trong [0, 100]
    # - Shape: (n_cities, 2) -> (số lượng thành phố, x và y)
    return np.random.uniform(0, 100, size=(n_cities, 2))


def plot_solution(problem: TSPProblem, tour: List[int], title: str = "TSP Solution"):
    """
    Vẽ biểu đồ giải pháp TSP - hiển thị thành phố và hành trình
    
    Args:
        problem (TSPProblem): Đối tượng bài toán TSP
        tour (List[int]): Danh sách chỉ số thành phố theo thứ tự visit
                         Ví dụ: [0, 3, 1, 2] = tour: 0 -> 3 -> 1 -> 2 -> 0
        title (str, optional): Tiêu đề của biểu đồ. Mặc định: "TSP Solution"
    
    Hiển thị:
    - Các thành phố dưới dạng các điểm đỏ
    - Số thứ tự của mỗi thành phố
    - Hành trình tốt nhất dưới dạng các đường xanh nối các thành phố
    """
    # Tạo figure với kích thước 10 inch ngang x 8 inch cao
    plt.figure(figsize=(10, 8))
    
    # VẼ CÁC THÀNH PHỐ:
    # - c='red': màu đỏ
    # - s=100: kích thước điểm
    # - zorder=3: lớp vẽ (3 = lên trên)
    plt.scatter(problem.cities[:, 0], problem.cities[:, 1], c='red', s=100, zorder=3)
    
    # ĐẶT TÊN THÀNH PHỐ:
    # Ghi số thứ tự (0, 1, 2, ...) lên mỗi thành phố
    for i, (x, y) in enumerate(problem.cities):
        # (x, y): vị trí thành phố
        # xytext=(5, 5): offset text 5 pixel về phải và lên trên
        plt.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points')
    
    # VẼ HÀNH TRÌNH:
    # tour_extended = tour + [tour[0]] để quay lại thành phố đầu tiên
    # Ví dụ: tour = [0, 3, 1, 2] -> tour_extended = [0, 3, 1, 2, 0]
    tour_extended = tour + [tour[0]]
    
    # Lấy tọa độ các thành phố trong hành trình
    # problem.cities[tour_extended] trả về mảng shape (len(tour_extended), 2)
    tour_coords = problem.cities[tour_extended]
    
    # Vẽ đường biểu diễn hành trình
    # 'b-': blue color, solid line
    # zorder=2: lớp vẽ (2 = dưới điểm thành phố)
    # linewidth=1.5: độ dày đường
    plt.plot(tour_coords[:, 0], tour_coords[:, 1], 'b-', zorder=2, linewidth=1.5)
    
    # Thiết lập labels và tiêu đề
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    
    # Hiển thị lưới để dễ đọc tọa độ
    plt.grid(True, alpha=0.3)  # alpha=0.3: độ trong suốt
    
    # Auto fit layout
    plt.tight_layout()
    
    # Hiển thị biểu đồ
    plt.show()


def plot_convergence(distance_history: List[float]):
    """
    Vẽ biểu đồ hội tụ - thể hiện cách best distance thay đổi qua các iteration
    
    Args:
        distance_history (List[float]): Danh sách best distance tại mỗi iteration
    
    Giải thích:
    - X-axis: Số iteration (0, 1, 2, ...)
    - Y-axis: Best distance tìm thấy tại iteration đó
    - Ngoài mong đợi, đường sẽ xuống (distance giảm = tour tốt hơn)
    - Khi đường bằng phẳng = algorithm đã hội tụ (không tìm thấy cải thiện)
    """
    # Tạo figure
    plt.figure(figsize=(10, 6))
    
    # Vẽ đường biểu diễn
    # linewidth=2: độ dày đường
    plt.plot(distance_history, linewidth=2)
    
    # Thiết lập labels
    plt.xlabel('Iteration')  # X-axis: số iteration
    plt.ylabel('Best Tour Distance')  # Y-axis: best distance
    plt.title('PSO Convergence for TSP')  # Tiêu đề
    
    # Hiển thị lưới
    plt.grid(True, alpha=0.3)
    
    # Auto fit layout
    plt.tight_layout()
    
    # Hiển thị biểu đồ
    plt.show()


if __name__ == "__main__":
    # CHƯƠNG TRÌNH CHÍNH: Giải TSP với 20 thành phố
    
    # In header
    print("=" * 60)
    print("TSP Solver using Particle Swarm Optimization (PSO)")
    print("=" * 60)
    
    # BƯỚC 1: TẠO DỮ LIỆU
    # Số lượng thành phố
    n_cities = 20
    # Tạo 20 thành phố ngẫu nhiên trong [0, 100] x [0, 100]
    # seed=42 để mỗi lần chạy tạo cùng một bộ thành phố (reproducable)
    cities = generate_cities(n_cities, seed=42)
    
    # BƯỚC 2: TẠO ĐỐI TƯỢNG BÀI TOÁN
    problem = TSPProblem(cities)
    print(f"\nProblem: {n_cities} cities")
    print(f"Search space: [0, 100] x [0, 100]")
    
    # BƯỚC 3: GIẢI BÀI TOÁN BẰNG PSO
    print("\nRunning PSO solver...")
    # Tạo PSO solver với:
    # - 30 hạt
    # - 500 iteration
    # - w=0.7 (inertia weight)
    # - c1=1.5 (cognitive)
    # - c2=1.5 (social)
    pso = PSO(problem, n_particles=30, max_iterations=500)
    
    # Chạy solver - trả về best_tour, best_distance, history
    best_tour, best_distance, history = pso.solve()
    
    # BƯỚC 4: ĐỀU KẾT QUẢ
    print(f"\n{'=' * 60}")
    print(f"Best tour found: {best_tour}")
    print(f"Best distance: {best_distance:.2f}")
    print(f"{'=' * 60}")
    
    # BƯỚC 5: HIỂN THỊ KẾT QUẢ
    print("\nGenerating visualizations...")
    # Vẽ hành trình tốt nhất
    plot_solution(problem, best_tour, f"TSP Solution (Distance: {best_distance:.2f})")
    # Vẽ đường cong hội tụ
    plot_convergence(history)
