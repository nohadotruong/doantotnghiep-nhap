# Import thuật toán A* để tạo đường đi ban đầu
from astar import Astar

# Import tất cả hằng số cấu hình cho thuật toán PSO và các tham số liên quan
from config.parameter import (
    MIN_CLEARANCE,  # Khoảng cách an toàn tối thiểu tới chướng ngại vật
    COLLISION_PENALTY,  # Giá trị phạt khi đường đi va chạm
    PSO_PATIENCE,  # Số vòng lặp không cải thiện tối đa trước khi dừng sớm
    PSO_N_PARTICLES,  # Số lượng hạt (particles) trong đàn PSO
    PSO_MAX_INIT_ATTEMPTS,  # Số lần thử tối đa khi khởi tạo vị trí hạt hợp lệ
    PSO_MAX_ITER,  # Số vòng lặp tối đa của PSO
    PSO_WEIGHT,  # Trọng số quán tính cố định (dùng khi không bật SIW)
    PSO_COGNITIVE_COEFF,  # Hệ số nhận thức cá nhân c1 (kéo hạt về best cá nhân)
    PSO_SOCIAL_COEFF,  # Hệ số xã hội c2 (kéo hạt về best toàn cục)
    PSO_VMAX_K,  # Hệ số nhân để tính vận tốc tối đa của hạt
    PSO_USE_SIW,  # Bật/tắt Stochastic Inertia Weight (trọng số quán tính ngẫu nhiên)
    PSO_W_MAX,  # Trọng số quán tính tối đa (dùng với SIW)
    PSO_W_MIN,  # Trọng số quán tính tối thiểu (dùng với SIW)
    PSO_USE_TVAC,  # Bật/tắt Time-Varying Acceleration Coefficients
    PSO_COG_INIT,  # Hệ số nhận thức ban đầu (dùng với TVAC)
    PSO_COG_FINAL,  # Hệ số nhận thức cuối (dùng với TVAC)
    PSO_SOC_INIT,  # Hệ số xã hội ban đầu (dùng với TVAC)
    PSO_SOC_FINAL,  # Hệ số xã hội cuối (dùng với TVAC)
    PSO_USE_SOBL,  # Bật/tắt Stochastic Opposition-Based Learning
    PSO_SOBL_MARGIN,  # Biên mở rộng vùng không gian tìm kiếm SOBL
    PSO_SOBL_MU,  # Giá trị trung bình phân phối Gauss trong SOBL
    PSO_SOBL_SIGMA,  # Độ lệch chuẩn phân phối Gauss trong SOBL
    PSO_USE_BEZIER,  # Bật/tắt làm mượt đường đi bằng đường cong Bezier
    PSO_BEZIER_THRESHOLD,  # Ngưỡng góc quay (độ) để áp dụng Bezier tại góc cua
    PSO_BEZIER_BLEND_RATIO,  # Tỷ lệ pha trộn điểm vào/ra của đường cong Bezier
    PSO_BEZIER_N_POINTS,  # Số điểm nội suy trên đường cong Bezier
)

from grid_map import GridMap  # Import lớp lưới bản đồ
from math import exp, sqrt  # exp dùng cho SIW, sqrt dùng tính vmax
from random import gauss, uniform  # gauss cho SOBL, uniform cho PSO ngẫu nhiên
from typing import Optional  # Kiểu trả về có thể là None
from utils import (
    compute_fitness,  # Tính hàm đánh giá (fitness) của một đường đi
    euclidean_distance,  # Tính khoảng cách Euclid giữa 2 điểm
    min_distance_line_to_obstacle,  # Tính khoảng cách nhỏ nhất từ đoạn thẳng tới chướng ngại vật
    round_pos,  # Làm tròn tọa độ điểm
    turning_angle,  # Tính góc quay tại một điểm trên đường đi
)


class HAPSO:
    """
    HAPSO - Hybrid A* Particle Swarm Optimizer:
    Thuật toán lai ghép A* (tìm đường ban đầu) với PSO (tối ưu hóa đường đi).
    Quy trình: A* → tối ưu PSO từng đoạn → làm mượt Bezier.
    """

    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
        collision_penalty: float = COLLISION_PENALTY,
        patience: int = PSO_PATIENCE,
        n_particles: int = PSO_N_PARTICLES,
        max_init_attempts: int = PSO_MAX_INIT_ATTEMPTS,
        max_iter: int = PSO_MAX_ITER,
        weight: float = PSO_WEIGHT,
        cognitive_coeff: float = PSO_COGNITIVE_COEFF,
        social_coeff: float = PSO_SOCIAL_COEFF,
        vmax_k: float = PSO_VMAX_K,
        use_siw: bool = PSO_USE_SIW,
        w_min: float = PSO_W_MIN,
        w_max: float = PSO_W_MAX,
        use_tvac: bool = PSO_USE_TVAC,
        cog_init: float = PSO_COG_INIT,
        cog_final: float = PSO_COG_FINAL,
        soc_init: float = PSO_SOC_INIT,
        soc_final: float = PSO_SOC_FINAL,
        use_sobl: bool = PSO_USE_SOBL,
        sobl_margin: float = PSO_SOBL_MARGIN,
        sobl_mu: float = PSO_SOBL_MU,
        sobl_sigma: float = PSO_SOBL_SIGMA,
        use_bezier: bool = PSO_USE_BEZIER,
        bezier_threshold: float = PSO_BEZIER_THRESHOLD,
        bezier_blend_ratio: float = PSO_BEZIER_BLEND_RATIO,
        bezier_n_points: int = PSO_BEZIER_N_POINTS,
    ) -> None:
        self.grid_map = grid_map  # Lưu tham chiếu đến bản đồ lưới
        self.start = self.grid_map.start  # Lấy tọa độ điểm xuất phát từ bản đồ
        self.goal = self.grid_map.goal  # Lấy tọa độ điểm đích từ bản đồ

        self.min_clearance = float(
            min_clearance
        )  # Khoảng cách an toàn tối thiểu (ép kiểu float)
        self.collision_penalty = collision_penalty  # Giá trị phạt khi va chạm

        # --- Tham số điều khiển vòng lặp PSO ---
        self.patience = patience  # Số vòng chờ không cải thiện trước khi dừng
        self.n_particles = n_particles  # Số hạt trong đàn
        self.max_init_attempts = max_init_attempts  # Số lần thử khởi tạo vị trí hợp lệ
        self.max_iter = max_iter  # Giới hạn vòng lặp tối đa
        self.weight = weight  # Trọng số quán tính cố định
        self.cognitive_coeff = cognitive_coeff  # Hệ số kéo về best cá nhân (c1)
        self.social_coeff = social_coeff  # Hệ số kéo về best toàn cục (c2)
        self.vmax_k = vmax_k  # Hệ số giới hạn vận tốc tối đa

        # --- Tham số SIW (Stochastic Inertia Weight) ---
        self.use_siw = use_siw  # True: dùng trọng số quán tính giảm dần có nhiễu
        self.w_min = w_min  # Giới hạn dưới của trọng số quán tính
        self.w_max = w_max  # Giới hạn trên của trọng số quán tính

        # --- Tham số TVAC (Time-Varying Acceleration Coefficients) ---
        self.use_tvac = use_tvac  # True: hệ số c1, c2 thay đổi theo thời gian
        self.cog_init = cog_init  # c1 ban đầu (khám phá nhiều)
        self.cog_final = cog_final  # c1 cuối (khám phá ít)
        self.soc_init = soc_init  # c2 ban đầu (hội tụ ít)
        self.soc_final = soc_final  # c2 cuối (hội tụ nhiều)

        # --- Tham số SOBL (Stochastic Opposition-Based Learning) ---
        self.use_sobl = use_sobl  # True: sinh điểm đối lập để tăng đa dạng
        self.sobl_margin = sobl_margin  # Biên mở rộng vùng tìm kiếm đối lập
        self.sobl_mu = sobl_mu  # Trung bình Gauss cho hệ số đối lập r
        self.sobl_sigma = sobl_sigma  # Độ lệch chuẩn Gauss cho hệ số đối lập r

        # --- Tham số Bezier smoothing ---
        self.use_bezier = use_bezier  # True: làm mượt góc cua bằng Bezier
        self.bezier_threshold = bezier_threshold  # Ngưỡng góc (độ) mới áp dụng Bezier
        self.bezier_blend_ratio = (
            bezier_blend_ratio  # Tỷ lệ lùi điểm vào/ra so với góc cua
        )
        self.bezier_n_points = bezier_n_points  # Số điểm trên đường cong Bezier

    def plan(self) -> Optional[list[tuple[float, float]]]:
        """
        Hàm lập kế hoạch đường đi chính.
        Trả về danh sách tọa độ đường đi, hoặc None nếu không tìm được.
        """
        start = self.start
        goal = self.goal

        # Kiểm tra điểm Start hợp lệ (trong bản đồ và không phải chướng ngại vật)
        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        # Kiểm tra điểm Goal hợp lệ
        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        # Nếu start trùng goal, trả về đường đi chỉ gồm 2 điểm giống nhau
        if start == goal:
            return [start, goal]

        # Bước 1: Chạy A* để có đường đi ban đầu
        initial_path = self._run_astar()
        if initial_path is None:
            return None  # A* không tìm được đường → thất bại hoàn toàn

        # Bước 2: Tối ưu đường đi bằng PSO
        pso_path = self._pso_optimize_path(initial_path)

        # Bước 3: Làm mượt đường đi (Bezier nếu được bật)
        smooth_path = self._smooth_path(pso_path)

        # Thêm điểm Goal vào cuối (PSO không xử lý điểm cuối)
        smooth_path.append(goal)

        return smooth_path

    def _run_astar(self) -> Optional[list[tuple[float, float]]]:
        """Chạy thuật toán A* trên bản đồ hiện tại, trả về đường đi thô."""
        return Astar(grid_map=self.grid_map).plan()

    def _pso_optimize_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """
        Tối ưu hóa từng điểm trung gian trên đường đi bằng PSO.
        Đường đi được xử lý theo từng đoạn 3 điểm: prev → current → next.
        """
        if len(path) <= 2:
            return path  # Đường đi chỉ có 2 điểm, không cần tối ưu

        optimized = [path[0]]  # Giữ nguyên điểm Start

        # Duyệt qua từng điểm trung gian (bỏ qua điểm đầu và điểm cuối)
        for i in range(1, len(path) - 1):
            prev_point = optimized[-1]  # Điểm trước (đã được tối ưu)
            next_point = path[i + 1]  # Điểm tiếp theo trong đường A*

            # Khởi tạo đàn hạt PSO cho đoạn này
            particles = self._init_particles(prev_point, next_point)

            # Chạy PSO để tìm vị trí tốt nhất cho điểm trung gian thứ i
            best_pos = self._run_pso_segment(particles, prev_point, next_point)

            # Thêm điểm tốt nhất (đã làm tròn) vào đường đi tối ưu
            optimized.append(round_pos(best_pos))

        return optimized

    def _init_particles(
        self, prev_point: tuple[float, float], next_point: tuple[float, float]
    ) -> list[dict]:
        """
        Khởi tạo đàn hạt PSO cho một đoạn đường.
        Mỗi hạt có: vị trí, vận tốc, best cá nhân, và giá trị fitness.
        """
        particles = []

        # Tính vận tốc tối đa theo tỷ lệ với độ dài đoạn prev→next
        max_vel = self.vmax_k * sqrt(
            (next_point[0] - prev_point[0]) ** 2 + (next_point[1] - prev_point[1]) ** 2
        )

        for _ in range(self.n_particles):
            # Lấy mẫu vị trí hợp lệ (không trùng chướng ngại vật, đủ khoảng hở)
            px, py = self._sample_valid_position(prev_point, next_point)

            # Khởi tạo vận tốc ngẫu nhiên trong khoảng [-vmax, vmax]
            vel_x = uniform(-max_vel, max_vel)
            vel_y = uniform(-max_vel, max_vel)

            # Tính fitness ban đầu của hạt
            fitness = self._eval_fitness((px, py), prev_point, next_point)

            # Lưu thông tin hạt dưới dạng dict
            particles.append(
                {
                    "pos": (px, py),  # Vị trí hiện tại
                    "vel": (vel_x, vel_y),  # Vận tốc hiện tại
                    "best_pos": (px, py),  # Vị trí tốt nhất cá nhân (pbest)
                    "best_fitness": fitness,  # Fitness tốt nhất cá nhân
                    "fitness": fitness,  # Fitness hiện tại
                }
            )

        return particles

    def _sample_valid_position(
        self, prev_point: tuple[float, float], next_point: tuple[float, float]
    ) -> tuple[float, float]:
        """
        Lấy mẫu ngẫu nhiên một vị trí hợp lệ nằm trên đoạn prev→next.
        Vị trí hợp lệ: trong bản đồ, không phải chướng ngại vật, đủ khoảng hở.
        """
        for _ in range(self.max_init_attempts):
            # Nội suy tuyến tính với t ngẫu nhiên trong [0, 1]
            t = uniform(0.0, 1.0)
            px = prev_point[0] + (next_point[0] - prev_point[0]) * t
            py = prev_point[1] + (next_point[1] - prev_point[1]) * t
            pos = round_pos((px, py))

            # Bỏ qua nếu ngoài bản đồ
            if not self.grid_map.is_inside(px, py):
                continue

            # Bỏ qua nếu là ô chướng ngại vật
            if self.grid_map.is_obstacle(int(px), int(py)):
                continue

            # Bỏ qua nếu khoảng cách tới chướng ngại vật nhỏ hơn ngưỡng an toàn
            if (
                min_distance_line_to_obstacle(pos, pos, self.grid_map)
                < self.min_clearance
            ):
                continue

            return (px, py)  # Vị trí hợp lệ, trả về

        # Không tìm được vị trí hợp lệ → dùng điểm giữa của đoạn làm dự phòng
        return (
            round((prev_point[0] + next_point[0]) / 2.0, 2),
            round((prev_point[1] + next_point[1]) / 2.0, 2),
        )

    def _run_pso_segment(
        self,
        particles: list[dict],
        prev_point: tuple[float, float],
        next_point: tuple[float, float],
    ) -> tuple[float, float]:
        """
        Chạy vòng lặp PSO để tối ưu vị trí của một điểm trung gian.
        Trả về vị trí tốt nhất toàn cục (gbest) sau khi hội tụ.
        """
        # Khởi tạo gbest từ hạt có fitness tốt nhất trong đàn ban đầu
        gbest = min(particles, key=lambda p: p["best_fitness"])
        gbest_pos = gbest["best_pos"]
        gbest_fitness = gbest["best_fitness"]

        # Tính biên không gian tìm kiếm cho SOBL (nếu được bật)
        if self.use_sobl:
            lb_x = min(prev_point[0], next_point[0]) - self.sobl_margin
            ub_x = max(prev_point[0], next_point[0]) + self.sobl_margin
            lb_y = min(prev_point[1], next_point[1]) - self.sobl_margin
            ub_y = max(prev_point[1], next_point[1]) + self.sobl_margin

        stagnation_count = 0  # Đếm số vòng lặp không cải thiện liên tiếp

        for it in range(self.max_iter):
            prev_gbest_fitness = gbest_fitness  # Lưu fitness gbest của vòng trước

            # Tính trọng số quán tính cho vòng lặp này
            w = self._inertia_weight(it)

            # Tính hệ số nhận thức và xã hội cho vòng lặp này
            cog_t, soc_t = self._acceleration_coeffs(it)

            for p in particles:
                vel_x, vel_y = p["vel"]  # Vận tốc hiện tại
                pos_x, pos_y = p["pos"]  # Vị trí hiện tại
                pb_x, pb_y = p["best_pos"]  # Best cá nhân (pbest)

                # --- Cập nhật vận tốc theo công thức PSO tiêu chuẩn ---
                # Thành phần quán tính + nhận thức (kéo về pbest) + xã hội (kéo về gbest)
                new_vel_x = (
                    w * vel_x
                    + cog_t * uniform(0.0, 1.0) * (pb_x - pos_x)
                    + soc_t * uniform(0.0, 1.0) * (gbest_pos[0] - pos_x)
                )
                new_vel_y = (
                    w * vel_y
                    + cog_t * uniform(0.0, 1.0) * (pb_y - pos_y)
                    + soc_t * uniform(0.0, 1.0) * (gbest_pos[1] - pos_y)
                )

                # Cập nhật vị trí mới (làm tròn)
                new_pos = round_pos((pos_x + new_vel_x, pos_y + new_vel_y))

                if self.use_sobl:
                    # Tạo hệ số r ngẫu nhiên theo phân phối Gauss
                    r = gauss(self.sobl_mu, self.sobl_sigma)

                    # Tính vị trí đối lập (opposite position) và clamp trong biên
                    opp_x = max(lb_x, min(ub_x, round(lb_x + ub_x - new_pos[0] * r, 2)))
                    opp_y = max(lb_y, min(ub_y, round(lb_y + ub_y - new_pos[1] * r, 2)))

                    # So sánh fitness điểm mới và điểm đối lập
                    fit_new = self._eval_fitness(new_pos, prev_point, next_point)
                    fit_opp = self._eval_fitness((opp_x, opp_y), prev_point, next_point)

                    # Chọn điểm có fitness tốt hơn
                    if fit_opp < fit_new:
                        p["pos"] = (opp_x, opp_y)
                        p["fitness"] = fit_opp
                    else:
                        p["pos"] = new_pos
                        p["fitness"] = fit_new

                else:
                    # Không dùng SOBL: cập nhật vị trí và tính fitness bình thường
                    p["pos"] = new_pos
                    p["fitness"] = self._eval_fitness(new_pos, prev_point, next_point)

                # Cập nhật vận tốc mới
                p["vel"] = (new_vel_x, new_vel_y)

                # Cập nhật pbest nếu fitness hiện tại tốt hơn
                if p["fitness"] < p["best_fitness"]:
                    p["best_fitness"] = p["fitness"]
                    p["best_pos"] = p["pos"]

                # Cập nhật gbest nếu có hạt nào vượt qua fitness tốt nhất hiện tại
                candidate = min(particles, key=lambda p: p["best_fitness"])
                if candidate["best_fitness"] < gbest_fitness:
                    gbest_fitness = candidate["best_fitness"]
                    gbest_pos = candidate["best_pos"]

            # Kiểm tra điều kiện dừng sớm (early stopping)
            if gbest_fitness < prev_gbest_fitness - 1e-6:
                stagnation_count = 0  # Có cải thiện → reset đếm
            else:
                stagnation_count += 1
                if stagnation_count >= self.patience:
                    break  # Không cải thiện đủ lâu → dừng sớm

        return gbest_pos  # Trả về vị trí tốt nhất tìm được

    def _eval_fitness(
        self,
        particle_pos: tuple[float, float],
        prev_point: tuple[float, float],
        next_point: tuple[float, float],
    ) -> float:
        """
        Tính fitness của một hạt tại vị trí particle_pos,
        xét trong ngữ cảnh đoạn đường [prev_point → particle_pos → next_point].
        """
        return compute_fitness(
            [prev_point, particle_pos, next_point],
            self.grid_map,
            self.min_clearance,
            self.collision_penalty,
        )

    def _inertia_weight(self, it: int) -> float:
        """
        Tính trọng số quán tính w cho vòng lặp thứ `it`.
        - SIW bật: w giảm tuyến tính từ w_max → w_min có thêm nhiễu Gaussian nhỏ.
        - SIW tắt: trả về hằng số weight cố định.
        """
        if self.use_siw:
            # Giảm tuyến tính + nhiễu ngẫu nhiên nhỏ trong [-0.1, 0.1]
            return self.w_max - (self.w_max - self.w_min) * (it / self.max_iter) * exp(
                uniform(-0.1, 0.1)
            )

        return self.weight

    def _acceleration_coeffs(self, it: int) -> tuple[float, float]:
        """
        Tính hệ số nhận thức (c1) và xã hội (c2) cho vòng lặp thứ `it`.
        - TVAC bật: c1 giảm, c2 tăng dần theo thời gian (tăng hội tụ cuối quá trình).
        - TVAC tắt: trả về hằng số cố định.
        """
        if self.use_tvac:
            t = it / self.max_iter  # Tỷ lệ tiến trình [0, 1]

            # Nội suy tuyến tính từ giá trị ban đầu → cuối
            cog_t = (self.cog_final - self.cog_init) * t + self.cog_init
            soc_t = (self.soc_final - self.soc_init) * t + self.soc_init

            return cog_t, soc_t

        return self.cognitive_coeff, self.social_coeff

    def _smooth_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """
        Làm mượt đường đi sau khi PSO tối ưu.
        Nếu use_bezier=True và đường đi có hơn 2 điểm, áp dụng Bezier tại các góc cua.
        """
        curr_path = path

        if self.use_bezier and len(curr_path) > 2:
            curr_path = self._bezier_corner_smooth(curr_path)

        return curr_path

    def _bezier_corner_smooth(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """
        Làm mượt các góc cua trong đường đi bằng đường cong Bezier bậc 2.
        Chỉ áp dụng tại những góc vượt ngưỡng bezier_threshold.
        """
        smoothed = [path[0]]  # Giữ nguyên điểm đầu

        for i in range(1, len(path) - 1):
            prev_point = smoothed[-1]  # Điểm trước trong đường đã làm mượt
            curr_point = path[i]  # Điểm góc cua hiện tại
            next_point = path[i + 1]  # Điểm tiếp theo

            # Tính góc quay tại curr_point
            angle = turning_angle(prev_point, curr_point, next_point)

            # Góc nhỏ hơn ngưỡng → không cần làm mượt, giữ nguyên điểm
            if angle < self.bezier_threshold:
                smoothed.append(curr_point)
                continue

            # Tính khoảng cách 2 đoạn kề góc
            d_prev = euclidean_distance(prev_point, curr_point)
            d_next = euclidean_distance(curr_point, next_point)

            # Nếu một trong hai đoạn quá ngắn → bỏ qua làm mượt
            if d_prev < 1e-6 or d_next < 1e-6:
                smoothed.append(curr_point)
                continue

            # Đảm bảo tỷ lệ blend không vượt quá 0.5 (tránh điểm vượt ra ngoài đoạn)
            blend = min(self.bezier_blend_ratio, 0.5)

            # Tính điểm vào (entry): lùi lại từ curr_point về phía prev_point
            entry = (
                curr_point[0] + blend * (prev_point[0] - curr_point[0]),
                curr_point[1] + blend * (prev_point[1] - curr_point[1]),
            )
            # Tính điểm ra (exit): tiến về phía next_point từ curr_point
            exit_ = (
                curr_point[0] + blend * (next_point[0] - curr_point[0]),
                curr_point[1] + blend * (next_point[1] - curr_point[1]),
            )

            # Nội suy đường cong Bezier bậc 2: entry → curr_point (điểm kiểm soát) → exit_
            bezier_pts = []
            for k in range(self.bezier_n_points + 1):
                t = k / self.bezier_n_points  # Tham số t ∈ [0, 1]

                # Công thức Bezier bậc 2: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
                bx = (
                    (1 - t) ** 2 * entry[0]
                    + 2 * (1 - t) * t * curr_point[0]
                    + t**2 * exit_[0]
                )
                by = (
                    (1 - t) ** 2 * entry[1]
                    + 2 * (1 - t) * t * curr_point[1]
                    + t**2 * exit_[1]
                )
                bezier_pts.append(round_pos((bx, by)))

            # Kiểm tra an toàn: đoạn từ điểm cuối smoothed tới điểm đầu bezier có đủ khoảng hở không
            is_safe = (
                min_distance_line_to_obstacle(
                    smoothed[-1], bezier_pts[0], self.grid_map
                )
                > self.min_clearance
            )

            # Kiểm tra thêm toàn bộ các đoạn liên tiếp trong bezier_pts
            if is_safe:
                for k in range(len(bezier_pts) - 1):
                    if not (
                        min_distance_line_to_obstacle(
                            smoothed[-1], bezier_pts[0], self.grid_map
                        )
                        > self.min_clearance
                    ):
                        is_safe = False
                        break

            if is_safe:
                # An toàn → thêm toàn bộ điểm Bezier vào đường đi
                smoothed.extend(bezier_pts)
            else:
                # Không an toàn → giữ nguyên điểm góc cua gốc
                smoothed.append(curr_point)

        smoothed.append(path[-1])  # Thêm điểm cuối đường đi gốc
        return smoothed
