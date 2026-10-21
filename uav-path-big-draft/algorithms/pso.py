# ============================================================================
# MODULE PSO - PARTICLE SWARM OPTIMIZATION
# ============================================================================
# File này chứa các class và hàm implementations của thuật toán PSO
# ============================================================================

import numpy as np  # Thư viện xử lý mảng
import random  # Thư viện phát sinh số ngẫu nhiên
from math import sqrt  # Hàm tính căn bậc hai
from utils.core import path_length  # Nhập hàm path_length từ utils


# ============================================================================
# CLASS PSOTSP - PSO ÁP DỤNG CHO BÀI TOÁN TSP (Traveling Salesman Problem)
# ============================================================================
class PSOTSP:
    """
    Lớp PSOTSP áp dụng thuật toán PSO để giải bài toán TSP.
    
    Bài toán TSP (Traveling Salesman Problem):
    - Tìm đường đi ngắn nhất đi qua tất cả các điểm đã cho
    - Bắt đầu từ một điểm cho trước
    - Kết thúc tại cùng điểm bắt đầu
    
    Thuật toán PSO (Particle Swarm Optimization):
    - Mô phỏng hành động tập thể của những con chim tìm kiếm thức ăn
    - Mỗi "particle" (hạt) đại diện cho một giải pháp (thứ tự đi qua các điểm)
    - Mỗi particle có:
      * Position: thứ tự hiện tại của các điểm
      * Velocity: một tập hợp các phép swap (hoán đổi) để áp dụng
      * Best position (pbest): thứ tự tốt nhất mà particle từng tìm được
      * Fitness: đánh giá độ tốt của position hiện tại
    - Swarm (đàn): tập hợp của nhiều particles cùng tìm kiếm
    
    Ứng dụng trong dự án:
    - Tìm đường đi tối ưu cho máy bay không người lái
    - Có thể so sánh kết quả với các thuật toán khác (RRT, RRT*, v.v.)
    
    Tệp này giúp giải các bài toán:
    - Lập kế hoạch đường đi tối ưu
    - Tối ưu hóa tổng độ dài đường đi
    - Đáp ứng ràng buộc về điểm bắt đầu và kết thúc
    """

    # ========================================================================
    # PHƯƠNG THỨC __init__ - KHỞI TẠO PSOTSP
    # ========================================================================
    def __init__(self, points, start_point, num_particles=20, max_iterations=100):
        """
        Khởi tạo một instance của PSOTSP.
        
        Tham số:
            points (list): Danh sách các điểm cần đi qua dưới dạng [(x1, y1), (x2, y2), ...]
            start_point (tuple): Điểm bắt đầu dưới dạng (x, y) - phải là một trong các points
            num_particles (int): Số lượng particles trong swarm (mặc định: 20)
            max_iterations (int): Số lượng iterations (vòng lặp) để chạy (mặc định: 100)
        """
        # Lưu danh sách các điểm
        self.points = points
        # Lưu điểm bắt đầu
        self.start_point = start_point
        # Số lượng particles
        self.num_particles = num_particles
        # Số lượng iterations (vòng lặp)
        self.max_iterations = max_iterations
        
        # Tính số lượng điểm (không bao gồm điểm bắt đầu vì nó sẽ lặp lại ở cuối)
        self.num_points = len(points)
        
        # Tìm index của điểm bắt đầu
        self.start_idx = points.index(start_point)
        
        # ===== CÁC THAM SỐ CỦA THUẬT TOÁN PSO =====
        self.w = 0.7  # Inertia weight - trọng số quán tính (kiểm soát ảnh hưởng của vận tốc cũ)
        self.c1 = 1.5  # Cognitive parameter - hệ số cá nhân (ảnh hưởng tới best position của particle)
        self.c2 = 1.5  # Social parameter - hệ số xã hội (ảnh hưởng tới best position của cả swarm)
        
        # ===== KHỞI TẠO CÁC DANH SÁCH LƯU TRỮ =====
        # Vị trí hiện tại của tất cả particles
        self.positions = []
        # Vận tốc (swap list) của tất cả particles
        self.velocities = []
        # Best position riêng của từng particle
        self.pbest_positions = []
        # Fitness của best position của từng particle
        self.pbest_fitness = []
        # Fitness hiện tại của từng particle
        self.fitness = []
        
        # Best position toàn cầu (tốt nhất trong toàn swarm)
        self.gbest_position = None
        # Fitness của best position toàn cầu
        self.gbest_fitness = float('inf')  # Bắt đầu với vô cực (vì tìm min)
        
        # ===== KHỞI TẠO SWARM =====
        self._initialize_swarm()

    # ========================================================================
    # PHƯƠNG THỨC _initialize_swarm - KHỞI TẠO SWARM
    # ========================================================================
    def _initialize_swarm(self):
        """
        Khởi tạo toàn bộ swarm với positions, velocities ngẫu nhiên.
        
        Phương pháp:
        1. Tạo một danh sách các điểm lần lượt từ điểm bắt đầu
        2. Hoán đổi (shuffle) ngẫu nhiên các điểm (trừ điểm bắt đầu)
        3. Mỗi particle được khởi tạo với một permutation ngẫu nhiên
        4. Tính fitness ban đầu cho mỗi particle
        5. Cập nhật global best (gbest)
        """
        # Lặp để tạo num_particles particles
        for i in range(self.num_particles):
            # ===== Khởi tạo position =====
            # Tạo danh sách các điểm bắt đầu từ các points
            position = list(self.points)
            # Hoán đổi ngẫu nhiên các điểm để tạo permutation ngẫu nhiên
            random.shuffle(position)
            # Thêm position vào danh sách
            self.positions.append(position)
            
            # ===== Khởi tạo velocity =====
            # Velocity ban đầu là danh sách rỗng (không có swap)
            velocity = []
            # Thêm velocity vào danh sách
            self.velocities.append(velocity)
            
            # ===== Tính fitness =====
            # Tính độ dài đường đi cho particle này
            fit = self._calculate_path_length(position)
            # Thêm fitness vào danh sách
            self.fitness.append(fit)
            
            # ===== Khởi tạo pbest =====
            # pbest position ban đầu = position hiện tại
            self.pbest_positions.append(position[:])  # Sao chép danh sách
            # pbest fitness ban đầu = fitness hiện tại
            self.pbest_fitness.append(fit)
            
            # ===== Cập nhật gbest =====
            # Nếu fitness này tốt hơn gbest thì cập nhật gbest
            if fit < self.gbest_fitness:
                self.gbest_fitness = fit
                # Sao chép position để lưu gbest
                self.gbest_position = position[:]

    # ========================================================================
    # PHƯƠNG THỨC _calculate_path_length - TÍNH ĐỘ DÀI ĐƯỜNG ĐI (TSP - khép kín)
    # ========================================================================
    def _calculate_path_length(self, path):
        """
        Tính tổng độ dài của đường đi TSP (khép kín).
        
        Phương pháp:
        - Sử dụng hàm path_length() từ utils.core
        - Thêm điểm đầu vào cuối path để tạo vòng lặp (TSP)
        - path_length() sẽ tính từ điểm đầu → ... → điểm cuối → quay lại điểm đầu
        
        Tham số:
            path (list): Danh sách các điểm [(x1,y1), (x2,y2), ...]
        
        Trả về:
            float: Tổng độ dài của đường đi khép kín
        """
        # Thêm điểm đầu vào cuối để tạo vòng lặp (quay lại điểm bắt đầu)
        tsp_path = path + [path[0]]
        # Gọi hàm path_length từ utils.core để tính độ dài
        return path_length(tsp_path)

    # ========================================================================
    # PHƯƠNG THỨC _apply_swaps - ÁP DỤNG CÁC PHÉP SWAP
    # ========================================================================
    def _apply_swaps(self, position, swaps):
        """
        Áp dụng một danh sách các phép hoán đổi (swap) vào một position.
        
        Phương pháp:
        1. Sao chép position để không thay đổi bản gốc
        2. Lặp qua từng swap
        3. Thực hiện hoán đổi giữa index i và j
        
        Tham số:
            position (list): Position (danh sách điểm) gốc
            swaps (list): Danh sách các phép swap dưới dạng [(i, j), ...]
        
        Trả về:
            list: Position mới sau khi áp dụng tất cả swaps
        """
        # Sao chép position để tránh thay đổi bản gốc
        new_position = position[:]
        
        # Lặp qua từng swap
        for i, j in swaps:
            # Hoán đổi phần tử ở index i với phần tử ở index j
            new_position[i], new_position[j] = new_position[j], new_position[i]
        
        # Trả về position mới
        return new_position

    # ========================================================================
    # PHƯƠNG THỨC _update_velocity - CẬP NHẬT VELOCITY
    # ========================================================================
    def _update_velocity(self, particle_idx):
        """
        Cập nhật velocity (danh sách swap) của một particle.
        
        Phương pháp PSO:
        1. Tạo ngẫu nhiên các swaps từ position hiện tại tới pbest
        2. Tạo ngẫu nhiên các swaps từ position hiện tại tới gbest
        3. Kết hợp chúng với các peso (c1 và c2)
        
        Tham số:
            particle_idx (int): Index của particle cần cập nhật
        """
        # Lấy position hiện tại
        current_pos = self.positions[particle_idx]
        # Lấy pbest position
        pbest_pos = self.pbest_positions[particle_idx]
        # Lấy gbest position
        gbest_pos = self.gbest_position
        
        # ===== Tính toán swaps cần thiết =====
        # Tìm các sự khác nhau giữa current position và pbest
        pbest_swaps = self._find_swaps(current_pos, pbest_pos)
        # Tìm các sự khác nhau giữa current position và gbest
        gbest_swaps = self._find_swaps(current_pos, gbest_pos)
        
        # ===== Tạo velocity mới =====
        new_velocity = []
        
        # Thêm các swaps từ pbest với xác suất c1/10
        if random.random() < self.c1 / 10:
            # Chọn một swap ngẫu nhiên từ pbest_swaps
            if pbest_swaps:
                num_swaps = random.randint(1, len(pbest_swaps))
                new_velocity.extend(random.sample(pbest_swaps, num_swaps))
        
        # Thêm các swaps từ gbest với xác suất c2/10
        if random.random() < self.c2 / 10:
            # Chọn một swap ngẫu nhiên từ gbest_swaps
            if gbest_swaps:
                num_swaps = random.randint(1, len(gbest_swaps))
                new_velocity.extend(random.sample(gbest_swaps, num_swaps))
        
        # Cập nhật velocity
        self.velocities[particle_idx] = new_velocity

    # ========================================================================
    # PHƯƠNG THỨC _find_swaps - TÌM CÁC PHÉP SWAP CẦN THIẾT
    # ========================================================================
    def _find_swaps(self, current_pos, target_pos):
        """
        Tìm các phép swap cần thiết để đi từ current_pos tới target_pos.
        
        Phương pháp:
        1. Tạo một danh sách sao chép từ current position
        2. Lặp qua từng vị trí
        3. Nếu phần tử không khớp với target, tìm và swap nó
        4. Ghi lại các swap này
        
        Tham số:
            current_pos (list): Position hiện tại
            target_pos (list): Position đích
        
        Trả về:
            list: Danh sách các swap dưới dạng [(i, j), ...]
        """
        # Sao chép current position để làm việc trên nó
        temp_pos = current_pos[:]
        # Danh sách để lưu các swap
        swaps = []
        
        # Lặp qua từng vị trí
        for i in range(len(temp_pos)):
            # Nếu phần tử ở vị trí i không giống với target
            if temp_pos[i] != target_pos[i]:
                # Tìm vị trí j của target_pos[i] trong temp_pos
                j = temp_pos.index(target_pos[i])
                # Thêm swap này vào danh sách
                swaps.append((i, j))
                # Thực hiện swap
                temp_pos[i], temp_pos[j] = temp_pos[j], temp_pos[i]
        
        # Trả về danh sách swaps
        return swaps

    # ========================================================================
    # PHƯƠNG THỨC _update_position - CẬP NHẬT POSITION
    # ========================================================================
    def _update_position(self, particle_idx):
        """
        Cập nhật position của một particle bằng cách áp dụng velocity.
        
        Phương pháp:
        1. Lấy position hiện tại
        2. Lấy velocity (danh sách swaps)
        3. Áp dụng các swaps vào position
        4. Tính fitness mới
        5. Cập nhật pbest nếu cần
        """
        # Lấy position hiện tại
        current_pos = self.positions[particle_idx]
        # Lấy velocity (danh sách swaps)
        velocity = self.velocities[particle_idx]
        
        # Áp dụng các swaps vào position
        new_pos = self._apply_swaps(current_pos, velocity)
        
        # Cập nhật position
        self.positions[particle_idx] = new_pos
        
        # ===== Tính fitness mới =====
        new_fitness = self._calculate_path_length(new_pos)
        # Cập nhật fitness
        self.fitness[particle_idx] = new_fitness
        
        # ===== Cập nhật pbest =====
        # Nếu fitness mới tốt hơn pbest fitness
        if new_fitness < self.pbest_fitness[particle_idx]:
            self.pbest_fitness[particle_idx] = new_fitness
            self.pbest_positions[particle_idx] = new_pos[:]
        
        # ===== Cập nhật gbest =====
        # Nếu fitness mới tốt hơn gbest fitness
        if new_fitness < self.gbest_fitness:
            self.gbest_fitness = new_fitness
            self.gbest_position = new_pos[:]

    # ========================================================================
    # PHƯƠNG THỨC optimize - CHẠY THUẬT TOÁN PSO
    # ========================================================================
    def optimize(self):
        """
        Chạy thuật toán PSO để tìm đường đi tối ưu.
        
        Phương pháp:
        1. Lặp qua max_iterations iterations (vòng lặp)
        2. Trong mỗi iteration:
           - Cập nhật velocity cho tất cả particles
           - Cập nhật position cho tất cả particles
           - Theo dõi best fitness
        3. Trả về kết quả tốt nhất
        
        Trả về:
            tuple: (best_path, best_fitness)
                - best_path: Đường đi tối ưu tìm được [(x1,y1), (x2,y2), ...]
                - best_fitness: Độ dài của đường đi tối ưu
        """
        print(f"[PSO-TSP] Bắt đầu tối ưu hóa với {self.num_particles} particles")
        print(f"[PSO-TSP] Số iterations: {self.max_iterations}")
        
        # Lặp qua các iterations
        for iteration in range(self.max_iterations):
            # ===== Cập nhật velocity và position cho tất cả particles trong iteration này =====
            for particle_idx in range(self.num_particles):
                # Cập nhật velocity
                self._update_velocity(particle_idx)
                # Cập nhật position
                self._update_position(particle_idx)
            
            # ===== In thông tin định kỳ =====
            if (iteration + 1) % 10 == 0 or iteration == 0:
                print(f"[PSO-TSP] Iteration {iteration + 1}/{self.max_iterations} - Best fitness: {self.gbest_fitness:.4f}")
        
        print(f"[PSO-TSP] Hoàn thành! Best fitness: {self.gbest_fitness:.4f}")
        
        # Trả về kết quả tốt nhất
        return self.gbest_position, self.gbest_fitness

    # ========================================================================
    # PHƯƠNG THỨC get_best_path - LẤY ĐƯỜNG ĐI TỐT NHẤT
    # ========================================================================
    def get_best_path(self):
        """
        Lấy đường đi tối ưu tìm được.
        
        Trả về:
            list: Danh sách các điểm của đường đi tối ưu
        """
        return self.gbest_position

    # ========================================================================
    # PHƯƠNG THỨC get_best_fitness - LẤY ĐIỂM AN TOÀN TỐT NHẤT
    # ========================================================================
    def get_best_fitness(self):
        """
        Lấy fitness (độ dài đường đi) tốt nhất tìm được.
        
        Trả về:
            float: Độ dài đường đi tối ưu
        """
        return self.gbest_fitness


# ============================================================================
# HÀM DEMO - KIỂM TRA CLASS PSOTSP
# ============================================================================
if __name__ == "__main__":
    # Tạo danh sách các điểm ngẫu nhiên cho bài toán TSP
    num_points = 10
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_points)]
    
    # Điểm bắt đầu là điểm đầu tiên
    start_point = points[0]
    
    print("=" * 70)
    print("DEMO - PSOTSP (PSO cho Traveling Salesman Problem)")
    print("=" * 70)
    print(f"Số điểm: {num_points}")
    print(f"Điểm bắt đầu: {start_point}")
    print()
    
    # Tạo instance của PSOTSP
    pso_tsp = PSOTSP(points, start_point, num_particles=20, max_iterations=50)
    
    # Chạy thuật toán
    best_path, best_fitness = pso_tsp.optimize()
    
    print()
    print("=" * 70)
    print("KẾT QUẢ")
    print("=" * 70)
    print(f"Đường đi tốt nhất: {best_path}")
    print(f"Độ dài đường đi tốt nhất: {best_fitness:.4f}")
    print()
