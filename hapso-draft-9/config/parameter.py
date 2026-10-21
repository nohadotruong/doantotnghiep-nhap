# ─── Cấu hình bản đồ lưới ─────────────────────────────────────────────────────
GRID_MAP_HEIGHT: int = 30  # Chiều cao bản đồ (số ô theo trục Y)
GRID_MAP_WIDTH: int = 30  # Chiều rộng bản đồ (số ô theo trục X)

# ─── Tham số an toàn & va chạm ────────────────────────────────────────────────
DANGER_CLEARANCE: float = (
    0.7071  # Khoảng cách tối thiểu đến vật cản để xếp loại "nguy hiểm"
)
# (= √2/2, bằng khoảng cách đường chéo 1 ô)
MIN_CLEARANCE: float = (
    1.0  # Khoảng cách tối thiểu bắt buộc để ô được coi là an toàn (đơn vị ô)
)
SAFETY_PENALTY: float = 5.0  # Phạt chi phí khi đi qua vùng nguy hiểm (gần vật cản)
COLLISION_PENALTY: float = (
    10.0  # Phạt chi phí khi đường đi đi vào vật cản (va chạm thực sự)
)

# ─── Tham số hiển thị & xuất kết quả ──────────────────────────────────────────
MARGIN_CELL: int = (
    3  # Vùng đệm (số ô) quanh cạnh bản đồ, không đặt điểm bắt đầu/kết thúc
)
ROUND_NUM: int = 2  # Số chữ số thập phân khi làm tròn tọa độ in ra

# ─── Cấu hình PSO (Particle Swarm Optimization) – tổng quát ───────────────────
PSO_N_WAYPOINTS: int = 5  # Số điểm trung gian (waypoint) mà mỗi hạt biểu diễn

PSO_PATIENCE: int = (
    15  # Số vòng lặp không cải thiện trước khi dừng sớm (early stopping)
)
PSO_N_PARTICLES: int = 20  # Số lượng hạt trong bầy
PSO_MAX_INIT_ATTEMPTS: int = (
    20  # Số lần thử tối đa để khởi tạo hạt hợp lệ (tránh vật cản)
)
PSO_MAX_ITER: int = 50  # Số vòng lặp tối đa của thuật toán PSO
PSO_WEIGHT: float = 0.7  # Trọng số quán tính (w) – điều khiển mức độ giữ vận tốc cũ
PSO_COGNITIVE_COEFF: float = (
    1.0  # Hệ số nhận thức (c1) – lực kéo hạt về vị trí tốt nhất của chính nó
)
PSO_SOCIAL_COEFF: float = (
    1.0  # Hệ số xã hội (c2) – lực kéo hạt về vị trí tốt nhất của cả bầy
)
PSO_VMAX_K: float = (
    0.1  # Tỉ lệ giới hạn vận tốc tối đa so với kích thước không gian tìm kiếm
)

# ─── PSO: Trọng số quán tính giảm dần theo thời gian (SIW) ────────────────────
PSO_USE_SIW: bool = True  # Bật/tắt chiến lược giảm trọng số quán tính theo vòng lặp
PSO_W_MIN: float = 0.4  # Giá trị trọng số quán tính nhỏ nhất (cuối quá trình)
PSO_W_MAX: float = 0.9  # Giá trị trọng số quán tính lớn nhất (đầu quá trình)

# ─── PSO: Hệ số gia tốc thay đổi theo thời gian (TVAC) ────────────────────────
PSO_USE_TVAC: bool = True  # Bật/tắt chiến lược thay đổi c1/c2 theo vòng lặp
PSO_COG_INIT: float = (
    2.5  # Hệ số nhận thức ban đầu (cao → hạt khám phá cục bộ nhiều hơn)
)
PSO_COG_FINAL: float = (
    0.5  # Hệ số nhận thức cuối (thấp → giảm ảnh hưởng tìm kiếm cá nhân)
)
PSO_SOC_INIT: float = 0.5  # Hệ số xã hội ban đầu (thấp → ít bị kéo về tâm bầy lúc đầu)
PSO_SOC_FINAL: float = (
    2.5  # Hệ số xã hội cuối (cao → hội tụ về nghiệm tốt nhất toàn cục)
)

# ─── PSO: Học đối xứng dựa trên đối lập (SOBL) ────────────────────────────────
PSO_USE_SOBL: bool = (
    True  # Bật/tắt khởi tạo dựa trên điểm đối xứng (tăng đa dạng ban đầu)
)
PSO_SOBL_MARGIN: float = (
    3.0  # Biên mở rộng không gian khi tính điểm đối xứng (đơn vị ô)
)
PSO_SOBL_MU: float = (
    1.0  # Tỉ lệ nhân khoảng cách khi tạo điểm đối xứng (1.0 = đối xứng đều)
)
PSO_SOBL_SIGMA: float = 0.1  # Độ lệch chuẩn nhiễu Gaussian thêm vào điểm đối xứng

# ─── PSO: Làm mượt đường đi bằng đường cong Bézier ───────────────────────────
PSO_USE_BEZIER: bool = True  # Bật/tắt hậu xử lý làm mượt đường đi bằng Bézier
PSO_BEZIER_THRESHOLD: float = (
    30.0  # Ngưỡng tổng góc lệch (độ): vượt qua mới áp dụng làm mượt
)
PSO_BEZIER_BLEND_RATIO: float = (
    0.65  # Tỉ lệ pha trộn giữa đường gốc và đường Bézier (0=gốc, 1=Bézier)
)
PSO_BEZIER_N_POINTS: int = 7  # Số điểm nội suy trên đường cong Bézier

# ─── RRT* (Rapidly-exploring Random Tree Star) ────────────────────────────────
RRT_STAR_MAX_ITER: int = 2000  # Số vòng lặp tối đa của RRT*
RRT_STAR_STEP_SIZE: int = 3  # Độ dài mỗi bước mở rộng cây (đơn vị ô)
RRT_STAR_GOAL_SAMPLE_RATE: float = (
    0.1  # Xác suất lấy mẫu trực tiếp tại đích (thay vì ngẫu nhiên)
)
RRT_STAR_MAX_SAMPLE_ATTEMPTS: int = (
    30  # Số lần thử lấy mẫu hợp lệ (tránh vật cản) mỗi vòng
)
RRT_STAR_NEIGHBOR_RADIUS: float = (
    6.0  # Bán kính tìm kiếm láng giềng để tối ưu lại cây (rewire)
)

# ─── PRM (Probabilistic Roadmap Method) ───────────────────────────────────────
PRM_N_SAMPLES: int = 300  # Số điểm ngẫu nhiên xây dựng bản đồ đường đi
PRM_CONNECTION_RADIUS: float = (
    15.0  # Bán kính kết nối tối đa giữa hai điểm trong bản đồ
)
PRM_MAX_SAMPLE_ATTEMPTS: int = 50  # Số lần thử lấy mẫu tối đa để đặt một điểm hợp lệ
