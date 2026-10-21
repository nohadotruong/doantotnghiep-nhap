# HAPSO Project Structure Documentation

**Mục đích**: Tài liệu toàn diện về tất cả classes, functions, constants trong dự án path planning.

---

## Tổng Quan

HAPSO là thư viện pure Python cung cấp **6 thuật toán path planning** trên grid 2D:

- **A\***: Thuật toán tìm kiếm heuristic cổ điển
- **PSO**: Particle Swarm Optimization với Catmull-Rom splines
- **APSO**: Adaptive PSO (A\* + PSO segment optimization)
- **HAPSO**: Hybrid A\* + Adaptive PSO
- **RRT**: Rapidly-Exploring Random Tree
- **RRT\***: RRT với rewiring tối ưu

**Tech Stack**: Python 3.x · NumPy · Matplotlib

---

## Cấu Trúc Thư Mục

```
hapso-draft-8/
├── config/
│   ├── __init__.py
│   ├── algo_config.py             [60+ constants]
│   └── ui_config.py               [UI-related constants]
│
├── core/
│   ├── __init__.py
│   ├── metrics.py                 [6 functions]
│   ├── models.py                  [3 dataclasses]
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── base_planner.py        [1 class: BasePlanner]
│   │   ├── pso_optimizer.py       [1 class: PSOptimizer]
│   │   ├── apso.py                [1 class: APSO]
│   │   ├── hapso.py               [1 class: HAPSO]
│   │   ├── rrt.py                 [2 classes: RRTNode, RRT]
│   │   └── rrt_star.py            [2 classes: RRTStarNode, RRTStar]
│   └── utils/
│       ├── __init__.py
│       ├── inertia_weight.py      [6 classes: InertiaWeight, AIW, LDIW, NDIW, SIW, SOBL]
│       └── path_smoother.py       [1 class + 3 functions]
│
├── map/
│   ├── __init__.py
│   ├── grid_map.py                [1 class: GridMap]
│   ├── map_serializer.py          [1 class: MapSerializer]
│   └── map_validator.py           [1 class: MapValidator]
│
├── simulator/
│   ├── astar-simulator.py         [Interactive A* demo]
│   ├── pso-simulator.py           [Interactive PSO demo]
│   ├── apso-simulator.py          [Interactive APSO demo]
│   ├── hapso-simulator.py         [Interactive HAPSO demo]
│   ├── rrt-simulator.py           [Interactive RRT demo]
│   ├── rrt_star-simulator.py      [Interactive RRT* demo]
│   └── README.md                  [Simulator usage guide]
│
├── maps/
│   └── test_map.json              [Example test map (30×30)]
│
├── structure.md                   [This file - full API documentation]
└── requirements.txt               [numpy, matplotlib, pygame (for simulators)]
```

---

# Chi Tiết Từng Module

## 📋 config/algo_config.py

**Mục đích**: Lưu toàn bộ hyperparameter và constants của các thuật toán.

### Constants (40+ total)

#### Robot & Collision Configuration

- `ROBOT_RADIUS = 1.5` — Bán kính robot cho collision detection
- `SAFE_DIST = 3.0` — Khoảng cách an toàn cho clearance evaluation
- `COLLISION_PENALTY_WEIGHT = 1000.0` — Penalty nếu có collision
- `OBSTACLE_RADIUS = 0.5` — Bán kính obstacles

#### A\* Configuration

- `ASTAR_REMOVE_REDUNDANT = False` — Xóa điểm redundant sau tìm đường
- `ASTAR_REMOVE_TRANSITION = False` — Xóa điểm transitive (line-of-sight)
- `ASTAR_MIN_CLEARANCE = 0.0` — Khoảng cách an toàn tối thiểu cho segment check

#### PSO Configuration (General)

- `PSO_N_WAYPOINTS = 12` — Số waypoints trong PSO path
- `PSO_N_PARTICLES = 100` — Số particles trong swarm
- `PSO_MAX_ITERATIONS = 200` — Max iterations
- `PSO_INERTIA_WEIGHT = 0.5` — Inertia weight
- `PSO_COGNITIVE_COEFFICIENT = 1.8` — c1 (cognitive term)
- `PSO_SOCIAL_COEFFICIENT = 1.8` — c2 (social term)

#### PSO Segment Optimizer Configuration

- `OPTIMIZER_N_PARTICLES = 20` — Số particles cho optimization
- `OPTIMIZER_MAX_ITERATIONS = 100` — Max iterations
- `OPTIMIZER_MAX_VELOCITY = 2.0` — Max velocity cho particle motion (Công thức 19-20 từ paper)
- `OPTIMIZER_COGNITIVE_COEFFICIENT = 2.0` — c1 (cognitive term)
- `OPTIMIZER_SOCIAL_COEFFICIENT = 2.0` — c2 (social term)
- `OPTIMIZER_W_MIN = 0.4` — Min inertia weight
- `OPTIMIZER_W_MAX = 0.9` — Max inertia weight
- `OPTIMIZER_C1_INITIAL = 2.5` — Initial c1 cho TVAC
- `OPTIMIZER_C1_FINAL = 0.5` — Final c1 cho TVAC
- `OPTIMIZER_C2_INITIAL = 0.5` — Initial c2 cho TVAC
- `OPTIMIZER_C2_FINAL = 2.5` — Final c2 cho TVAC
- `OPTIMIZER_USE_TVAC = True` — Dùng Time-Varying Acceleration Coefficients (HAPSO)
- `OPTIMIZER_SOBL_MU = 0.5` — SOBL opposition vector mean
- `OPTIMIZER_SOBL_SIGMA = 0.15` — SOBL opposition vector std dev
- `OPTIMIZER_SEARCH_MARGIN = 3` — Search margin khi tính bounds

#### RRT Configuration

- `RRT_MAX_ITERATIONS = 1500` — Max RRT iterations
- `RRT_STEP_SIZE = 3` — Step size khi expand tree
- `RRT_GOAL_SAMPLE_RATE = 0.1` — Xác suất sample goal (10%)

#### RRT\* Configuration

- `RRT_STAR_MAX_ITERATIONS = 2000` — Max RRT\* iterations
- `RRT_STAR_NEIGHBOR_RADIUS = 6.0` — Radius cho rewiring neighbors

---

## 📊 core/models.py

**Mục đích**: Data models (dataclasses) cho lưu trữ kết quả và metadata.

### PathResult (Dataclass)

```
Fields:
  - algorithm: str            — Tên thuật toán
  - path: list[tuple[int, int]] — Danh sách waypoints
  - metrics: dict             — {path_length, waypoints, turning_angle, min_clearance}
  - execution_time: float     — Thời gian chạy (giây)
  - success: bool             — Có tìm được path không
  - error_message: str        — Error nếu không tìm được
```

**Mục đích**: Lưu kết quả path planning + metrics cho một thuật toán.

**Post-Init Hook**: `__post_init__` — Validate metrics dict

### SimulationResult (Dataclass)

```
Fields:
  - algorithm: str            — Tên thuật toán
  - path_result: PathResult   — Kết quả path
  - timestamp: datetime       — Khi nào tạo
```

**Mục đích**: Lưu kết quả + metadata (thời gian, v.v.)

### ComparisonMetrics (Dataclass)

```
Fields:
  - results: dict[str, PathResult] — Map algorithm_name → PathResult

Methods:
  - add_result(algorithm: str, result: PathResult)
      → Thêm kết quả cho một thuật toán

  - get_algorithms() → list[str]
      → List tên thuật toán đã chạy

  - get_result(algorithm: str) → PathResult
      → Lấy kết quả của thuật toán nào đó
```

**Mục đích**: Tập hợp kết quả từ nhiều thuật toán để so sánh.

---

## 📈 core/metrics.py

**Mục đích**: Tính toán 5 chỉ số đánh giá path planning.

### Functions

#### `calculate_path_length(path: list[tuple[float, float]]) -> float`

- **Logic**: Tính tổng Euclidean distance giữa tất cả waypoints liên tiếp
- **Công thức**: $\sum_{i=0}^{n-1} \sqrt{(x_{i+1}-x_i)^2 + (y_{i+1}-y_i)^2}$
- **Mục đích**: Đánh giá độ dài path (càng ngắn càng tốt)

#### `calculate_waypoint_count(path: list[tuple]) -> int`

- **Logic**: Trả về `len(path)`
- **Mục đích**: Đánh giá độ phức tạp path (ít waypoints = đơn giản hơn)

#### `calculate_turning_angle(path: list[tuple[float, float]]) -> float`

- **Logic**:
  - Tính vector từ waypoint i-1 → i và i → i+1
  - Tính góc giữa 2 vectors dùng `atan2`
  - Tổng tất cả góc quay
- **Mục đích**: Đánh giá tính "mượt" của path (ít quay = mượt hơn)

#### `calculate_minimum_clearance(path: list[tuple[float, float]], grid_map: GridMap) -> float`

- **Logic**:
  - Với mỗi segment của path, tính min distance đến tất cả obstacles
  - Return min distance tìm được
- **Mục đích**: Đánh giá margin an toàn (càng xa obstacles càng tốt)
- **Phụ thuộc**: `_min_distance_segment_to_obstacles()`

#### `_min_distance_segment_to_obstacles(p1, p2, obstacles) -> float`

- **Logic** (Private Helper):
  - Project từ mỗi obstacle center tới line segment
  - Tính distance từ obstacle center tới point trên segment gần nhất
  - Return min distance
- **Mục đích**: Hỗ trợ clearance calculation

#### `compute_all_metrics(path, grid_map, execution_time) -> dict`

- **Logic**: Gọi tất cả 4 metric functions + add `execution_time`
- **Return**:
  ```python
  {
    "path_length": float,
    "waypoints": int,
    "turning_angle": float,
    "min_clearance": float,
    "execution_time": float
  }
  ```
- **Mục đích**: Tính toán 1 lần thay vì gọi từng hàm

---

## 🗺️ map/grid_map.py

**Mục đích**: Model đại diện grid 2D với obstacles, start, goal.

### GridMap (Class)

#### `__init__(width: int, height: int)`

- **Logic**: Khởi tạo grid 2D (list[list[int]])
  - `0` = ô trống (walkable)
  - `1` = obstacle
  - `2` = start
  - `3` = goal
- **State**:
  ```python
  self.grid: list[list[int]]
  self.start: tuple[int, int]
  self.goal: tuple[int, int]
  ```

#### `is_inside(x: int, y: int) -> bool`

- **Logic**: Kiểm tra `0 <= x < width` và `0 <= y < height`
- **Mục đích**: Boundary checking

#### `is_obstacle(x: int, y: int) -> bool`

- **Logic**: Kiểm tra `grid[y][x] == 1`
- **Mục đích**: Kiểm tra collision

#### `set_obstacle(x: int, y: int)`

- **Logic**: `grid[y][x] = 1`
- **Mục đích**: Thêm obstacle

#### `toggle_obstacle(x: int, y: int)`

- **Logic**: `grid[y][x] = 1 - grid[y][x]` (bật/tắt)
- **Mục đích**: Toggle obstacle khi edit map

#### `set_start(x: int, y: int)` / `set_goal(x: int, y: int)`

- **Logic**: Lưu toạ độ start/goal
- **Mục đích**: Set điểm bắt đầu và đích

#### `get_obstacles() -> list[tuple[int, int]]`

- **Logic**: Trả về danh sách toạ độ obstacles (cell có `grid[y][x] == 1`)
- **Mục đích**: Query tất cả obstacles

#### `get_obstacles_as_centers() -> list[tuple[float, float]]`

- **Logic**: Tương tự, nhưng trả về (x + 0.5, y + 0.5) — tâm ô
- **Mục đích**: Dùng cho collision checking với obstacles như hình tròn

#### `get_obstacle_count() -> int`

- **Logic**: Đếm số `1` trong grid
- **Mục đích**: Thống kê

#### `to_dict() -> dict` / `from_dict(data: dict)`

- **Logic**: Convert grid ↔ dictionary format
- **Mục đích**: Serialization (save/load)

#### `clear_map()`

- **Logic**: Reset tất cả ô về `0`
- **Mục đích**: Clear map để tái sử dụng

---

## 💾 map/map_serializer.py

**Mục đích**: Load/save GridMap từ/vào file JSON.

### MapSerializer (Class - Static Methods Only)

#### `@staticmethod load(path: str) -> GridMap`

- **Logic**:
  1. Đọc JSON file
  2. Parse `width`, `height`, `grid`, `start`, `goal`
  3. Tạo GridMap và restore state
- **Return**: GridMap object
- **Lỗi**: Print "[MAP_SERIALIZER]: Error" nếu file không tìm được

#### `@staticmethod save(grid_map: GridMap, path: str)`

- **Logic**:
  1. Convert GridMap → dict
  2. Ghi vào JSON file
- **Mục đích**: Persist map để dùng lại sau

---

## ✔️ map/map_validator.py

**Mục đích**: Validate GridMap trước khi chạy planner.

### MapValidator (Class - Static Methods)

#### `@staticmethod validate(grid_map: GridMap) -> bool`

- **Logic**:
  - Kiểm tra `start` và `goal` có hợp lệ không
  - Kiểm tra không có obstacle tại `start` hoặc `goal`
  - In warning nếu có lỗi
- **Return**: True nếu hợp lệ, False nếu không
- **Mục đích**: Fail-fast trước khi tốn thời gian tính toán

---

## 🎯 core/algorithms/base_planner.py

**Mục đích**: Abstract base class (ABC) định nghĩa interface chung cho tất cả planners.

### BasePlanner (ABC)

#### `@abstractmethod find_path(start: tuple[int, int], goal: tuple[int, int]) -> Optional[list[tuple[int, int]]]`

- **Logic**: Được override bởi mỗi planner (A\*, PSO, RRT, v.v.)
- **Return**: Path nếu tìm được, None nếu không

#### `set_distance_method(method: str)`

- **Logic**: Set `self.distance_method` ("euclidean" hoặc "manhattan")
- **Mục đích**: Cho phép thay đổi metric distance

#### `_validate_inputs(start: tuple, goal: tuple) -> bool`

- **Logic**:
  - Kiểm tra `start` và `goal` có trong bounds không
  - Kiểm tra không phải obstacles
  - Kiểm tra không bằng nhau
- **Return**: True nếu valid

#### `_euclidean_distance(p1: tuple, p2: tuple) -> float`

- **Logic**: $\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$
- **Mục đích**: Heuristic cho A\* và distance metrics

#### `_segment_has_collision(p1: tuple, p2: tuple) -> bool`

- **Logic**:
  1. Dùng Fast Voxel Traversal để lấy tất cả cell segment đi qua
  2. Check nếu có cell nào ra ngoài lưới hoặc là obstacle
  3. Check thêm clearance với obstacle centers bằng `_min_distance_segment_to_obstacles()`
- **Mục đích**: Validate nếu line segment từ p1 → p2 có pass obstacle hoặc quá gần obstacle

#### `_fast_voxel_traversal(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]`

- **Logic**:
  - Khởi tạo `step_x`, `step_y`, `t_max_x`, `t_max_y`, `t_delta_x`, `t_delta_y`
  - Mỗi vòng lặp chọn trục có `t_max` nhỏ hơn để tiến sang ô kế tiếp
  - Nếu `t_max_x == t_max_y` thì bước chéo đồng thời trên cả hai trục
- **Mục đích**: Shared voxel traversal cho collision checking giữa BasePlanner, Astar và PathSmoother

#### `_bresenham_line(p1: tuple[int, int], p2: tuple[int, int]) -> list[tuple[int, int]]`

- **Logic**: Implement Bresenham line algorithm
  - Tính từng pixel trên line từ p1 → p2
  - Return list tất cả cells
- **Mục đích**: Legacy helper giữ lại cho các chỗ cần raster line kiểu cũ

#### `_min_distance_segment_to_obstacles(p1: tuple[float, float], p2: tuple[float, float]) -> float`

- **Logic**:
  - Project từng obstacle center tới line segment
  - Return min distance tìm được
- **Mục đích**: Clearance calculation (dùng chung cho tất cả planners)

---

## ⭐ core/algorithms/astar.py

**Mục đích**: Implement A\* pathfinding algorithm.

### Astar (Class)

#### `__init__(grid: GridMap, remove_redundant: bool = False, remove_transition: bool = False, min_clearance: float = 0.0)`

- **Config**:
  ```python
  self.grid = grid
  self.remove_redundant = remove_redundant
  self.remove_transition = remove_transition
  self.min_clearance = min_clearance
  ```

#### `find_path(start: tuple, goal: tuple) -> Optional[list[tuple]]`

- **Logic**:
  1. Gán `start`/`goal` vào `grid`
  2. Initialize OPEN set (priority queue) với tuple `(f, h, g, node)`
  3. Loop:
     - Pop node có `f` nhỏ nhất, nếu tie thì ưu tiên `h` nhỏ hơn
     - Nếu == goal → reconstruct path
     - Else: expand neighbors → update `g`, `h`, `f` → thêm vào OPEN
  4. Post-process path nếu `remove_redundant` hoặc `remove_transition`
- **Return**: List waypoints hoặc None

#### `_heuristic(pos: tuple[int, int]) -> float`

- **Logic**: Euclidean distance đến `self.goal`
- **Mục đích**: Guide search về goal

#### `_movement_cost(from_pos: tuple[int, int], to_pos: tuple[int, int]) -> float`

- **Logic**: Euclidean distance giữa hai ô kề nhau
- **Mục đích**: Accumulate `g_score`

#### `_reconstruct_path(current: tuple[int, int]) -> list[tuple[int, int]]`

- **Logic**: Backtrack từ goal về start bằng `came_from`
- **Mục đích**: Rebuild path

#### `_post_process_path(path: list[tuple[int, int]]) -> list[tuple[int, int]]`

- **Logic**:
  - Nếu `remove_redundant=True` → gọi `_remove_collinear()`
  - Nếu `remove_transition=True` → gọi `_remove_transitive()`
- **Mục đích**: Tối giản path sau khi A\* hoàn tất

---

## 🔧 core/algorithms/pso_optimizer.py

**Mục đích**: PSO segment optimizer cho refinement waypoint.

### PSOptimizer (Class)

#### `__init__(grid_map: GridMap, n_particles: int = 20, max_iterations: int = 100, use_tvac: bool = True)`

- **Config**: Tương tự PSOPlanner nhưng với ít particles hơn

#### `find_path(start: tuple, goal: tuple) -> Optional[list]`

- **Logic**: Wrapper để tương thích interface BasePlanner
  - Optimize segment từ start → goal
  - Return kết quả

#### `optimize_segment(waypoints: list) -> list`

- **Logic**:
  1. Lấy mỗi cặp waypoint liên tiếp
  2. Optimize điểm giữa của segment
  3. Return optimized waypoints
- **Mục đích**: Refine path mà không thay đổi start/goal

#### `_fitness(waypoints: list) -> float`

- **Logic**: Tương tự PSOPlanner
  - Path length + collision penalty

#### `_apply_sobl(particle: list) -> list`

- **Logic**: Generate opposite solution và pick cái tốt hơn
- **Mục đích**: Escape local optimum

#### `_compute_tvac_coefficients(k: int) -> tuple[float, float]`

- **Logic**:
  - Tính dynamic c1, c2 dựa vào iteration k
  - Thường: c1 giảm, c2 tăng
- **Mục đích**: Time-Varying Acceleration Coefficients (TVAC)

---

## 🎪 core/algorithms/apso.py

**Mục đích**: Adaptive PSO = A\* + PSO segment optimization với fitness đơn giản theo paper.

### APSO (Class)

**Note**: APSO tích hợp PSO logic trực tiếp (không sử dụng PSOptimizer), với fitness function khác HAPSO.

#### `__init__(grid_map: GridMap)`

- Khởi tạo A\*, SIW, SOBL
- PSO parameters từ `algo_config.py` (n_particles, max_iterations, vmax, etc.)
- `use_tvac = False` (dùng hệ số cố định c1, c2)

#### `find_path(start: tuple, goal: tuple) -> Optional[list]`

- **Logic**:
  1. Run A\* để tìm initial path
  2. Loại bỏ điểm collinear (keep only key nodes)
  3. Call `_optimize_segments()` để refine từng segment bằng PSO
  4. Return optimized path

#### `_optimize_segment(start: tuple, end: tuple) -> tuple`

- **Logic**: Tối ưu một segment từ start → end bằng PSO
  1. Khởi tạo particles: `pos = start + (end - start) * r` (Công thức 17-18 từ paper)
  2. Khởi tạo velocities: `vel = vmax * r` (Công thức 19-20 từ paper)
  3. Loop max_iterations:
     - Update velocities: `v = w*v + c1*r1*(pbest-pos) + c2*r2*(gbest-pos)`
     - Update positions với boundary checking
     - Evaluate fitness
     - Update pbest, gbest
     - Apply SOBL (Opposition-Based Learning)
  4. Round gbest → candidate positions
  5. Chọn candidate tốt nhất (collision-free + fitness cao)

#### `_fitness(start, mid, end) -> float`

- **Công thức** (theo APSO paper):
  - Nếu collision: `f = 0`
  - Nếu không collision: `f = 1 / (1 + d)`
    - Với `d = distance(start→mid) + distance(mid→end)`
  - **Mục đích**: Minimize path length (PSO maximize f)
- **Khác HAPSO**: HAPSO dùng fitness phức tạp (length + angle + clearance)

#### `_optimize_segments(path: list) -> list`

- **Logic**: Rolling optimization
  - Loop qua từng segment (path[i] → path[i+2])
  - Optimize vị trí path[i+1] bằng `_optimize_segment()`
  - Check clearance: nếu tốt hơn → giữ, nếu không → revert

---

## 🏆 core/algorithms/hapso.py

**Mục đích**: HAPSO = Hybrid A\* + PSO với fitness phức tạp + TVAC.

### HAPSO (Class)

**Note**: HAPSO sử dụng PSOptimizer (không tích hợp PSO logic trực tiếp).

#### `__init__(grid_map: GridMap)`

- Khởi tạo A\*, PSOptimizer(use_tvac=True)
- PSO parameters từ `algo_config.py`

#### `find_path(start: tuple, goal: tuple) -> Optional[list]`

- **Logic**:
  1. Run A\* → initial path
  2. Loại bỏ điểm collinear
  3. Call `_optimize_segments()` với PSOptimizer(use_tvac=True)
  4. Return optimized path
- **Khác APSO**: Dùng Time-Varying Acceleration Coefficients + fitness phức tạp

#### `_optimize_segments(path: list) -> list`

- **Logic**: Tương tự APSO nhưng dùng PSOptimizer với fitness phức tạp (length + angle + clearance)

---

## 🔧 core/algorithms/pso_optimizer.py

**Mục đích**: PSO optimization engine dùng bởi HAPSO (fitness phức tạp, support TVAC).

### PSOptimizer (Class)

**Note**: PSOptimizer dùng cho HAPSO. APSO có PSO logic riêng với fitness đơn giản.

#### `__init__(grid_map: GridMap, use_tvac: bool = False)`

- `use_tvac`: Nếu True → dùng Time-Varying Acceleration Coefficients
- PSO parameters: n_particles, max_iterations, c1, c2, w_min, w_max, vmax, etc.

#### `optimize_segment(start: tuple, end: tuple) -> tuple`

- **Logic**: Tối ưu một segment, tương tự APSO nhưng:
  - Khởi tạo particles: `pos = start + (end - start) * r`
  - Khởi tạo velocities: `vel = vmax * r` (Công thức 19-20)
  - Loop max_iterations:
    - Update velocities với TVAC nếu use_tvac=True
    - Update positions
    - Evaluate fitness (phức tạp: length + angle + clearance)
    - Update pbest, gbest, clearance tracking
    - Apply SOBL

#### `_fitness(start, mid, end) -> float`

- **Công thức** (HAPSO fitness - phức tạp):
  - Nếu collision: `f = 0`
  - Nếu không collision:
    - Normalize path length: `length_norm = length / straight_distance`
    - Tính angle smoothness: `angle_norm = total_angle / π`
    - Tính clearance penalty: `clearance_norm` (normalized distance to obstacles)
    - **Combine**: `cost = 0.1 * length_norm + 0.2 * angle_norm + 0.7 * clearance_norm`
    - `f = 1 / (1 + cost)`
  - **Mục đích**: Optimize length + smoothness + safety (PSO maximize f)

---

## 🌳 core/algorithms/rrt.py

**Mục đích**: Rapidly-Exploring Random Tree planner.

### RRTNode (Dataclass)

```python
position: tuple[float, float]
parent: Optional[RRTNode]
cost: float
```

### RRT (Class)

#### `__init__(grid_map: GridMap, max_iterations: int = 1500, step_size: float = 3, goal_sample_rate: float = 0.1)`

#### `find_path(start: tuple, goal: tuple) -> Optional[list]`

- **Logic**:
  1. Initialize tree với start node
  2. Loop `max_iterations`:
     - Sample random point (hoặc goal với 10% xác suất)
     - Tìm nearest node trong tree
     - Steer từ nearest → sample point
     - Nếu không collision → thêm node vào tree
     - Nếu gần goal → reconstruct path
  3. Return path nếu tìm được
- **Return**: List waypoints hoặc None

#### `_sample_point() -> tuple[float, float]`

- **Logic**: Random (x, y) trong grid
- **Mục đích**: Exploration

#### `_nearest_node(point: tuple) -> RRTNode`

- **Logic**: Tìm node trong tree gần point nhất (Euclidean distance)

#### `_steer(from_node: RRTNode, to_point: tuple) -> tuple`

- **Logic**:
  - Di chuyển từ `from_node` hướng `to_point` bước `step_size`
  - Nếu `distance < step_size` → return `to_point`
  - Else: return điểm trên đường nối cách `step_size`

#### `_is_goal_reached(point: tuple) -> bool`

- **Logic**: Check nếu point gần goal (within step_size)

#### `_reconstruct_path(node: RRTNode) -> list`

- **Logic**: Backtrack từ node → start

---

## 🌲 core/algorithms/rrt_star.py

**Mục đích**: RRT\* = RRT + rewiring để tối ưu cost.

### RRTStar (Class)

#### `find_path(start: tuple, goal: tuple) -> Optional[list]`

- **Logic**: Tương tự RRT + thêm rewiring:
  1. Tìm nearest node + steer (như RRT)
  2. Tìm neighbors trong radius (method `_near_nodes`)
  3. Choose best parent (method `_choose_parent`)
  4. Add node
  5. Rewire neighbors (method `_rewire`)

#### `_near_nodes(point: tuple, radius: float) -> list[RRTNode]`

- **Logic**: Tìm tất cả node trong radius từ point
- **Optimization**: Radius giảm theo $\text{radius} = r \times (\log(n) / n)^{1/d}$ (dynamic)

#### `_choose_parent(neighbors: list[RRTNode], new_point: tuple) -> RRTNode`

- **Logic**:
  - Tìm neighbor có tổng cost (neighbor.cost + distance) nhỏ nhất
  - Check collision-free
  - Return best parent
- **Mục đích**: Minimize tree cost từ start

#### `_rewire(new_node: RRTNode, neighbors: list[RRTNode])`

- **Logic**:
  - Với mỗi neighbor:
    - Nếu `new_node.cost + distance < neighbor.cost` → update parent
    - Check collision-free trước
- **Mục đích**: Optimize existing tree paths

---

## ⚙️ core/utils/inertia_weight.py

**Mục đích**: PSO inertia weight strategies và Opposition-Based Learning.

### InertiaWeight (ABC)

#### `__init__(w_min: float = 0.4, w_max: float = 0.9, max_iterations: int = 200)`

#### `@abstractmethod compute(k: int) -> float`

- **Parameters**:
  - `k` = current iteration
- **Return**: Inertia weight cho iteration k
- **Mục đích**: Strategy pattern cho weight decay

---

### AIW (Adaptive Inertia Weight)

#### `compute(k: int) -> float`

- **Logic**:
  - Tính improvement ratio
  - Nếu success → `w = w_min`
  - Else → `w = w_max`
- **Mục đích**: Adaptive based on fitness improvement

---

### LDIW (Linearly Decreasing Inertia Weight)

#### `compute(k: int) -> float`

- **Logic**: $w = w_{max} - (w_{max} - w_{min}) × \frac{k}{k_{max}}$
- **Mục đích**: Smooth decay từ exploration → exploitation

---

### NDIW (Nonlinearly Decreasing Inertia Weight)

#### `compute(k: int) -> float`

- **Logic**: $w = (w_{max} - w_{min}) × e^{-2k/k_{max}} + w_{min}$
- **Mục đích**: Faster decay (exponential)

---

### SIW (Stochastic Inertia Weight)

#### `compute(k: int) -> float`

- **Logic**:
  - Base linear decay
  - Thêm Gaussian noise: $w = \text{linear} + \sigma × N(0, 1)$
- **Mục đích**: Stochastic perturbation

---

### SOBL (Stochastic Opposition-Based Learning)

#### `__init__(n_dims: int, bounds: list[tuple[float, float]], n_samples: int = 10)`

- **Config**:
  ```python
  self.n_dims = n_dims                     — Dimensionality
  self.bounds = bounds                     — Search space bounds
  self.n_samples = n_samples               — Số samples opposition-based
  ```

#### `opposite_scalar(x: float, x_min: float, x_max: float) -> float`

- **Logic**: $x_{opp} = x_{min} + x_{max} - x$
- **Mục đích**: Generate opposite scalar

#### `opposite_vector(x: list[float]) -> list[float]`

- **Logic**: Apply `opposite_scalar` cho mỗi dimension
- **Mục đích**: Generate opposite solution

#### `_sample_r() -> float`

- **Logic**: Sample từ Gaussian distribution
- **Mục đích**: Stochastic sampling

---

## 🛠️ core/utils/path_smoother.py

**Mục đích**: Path optimization bằng removing redundant points.

### PathSmoother (Class)

#### `smooth(path: list[tuple], remove_redundant: bool = True, remove_transitive: bool = True) -> list`

- **Logic**:
  1. Nếu `remove_redundant=True` → call `_remove_collinear`
  2. Nếu `remove_transitive=True` → call `_remove_transitive`
  3. Return smoothed path

#### `_remove_collinear(path: list) -> list`

- **Logic**:
  - Loop qua từng point
  - Check nếu 3 điểm liên tiếp thẳng hàng (collinear)
  - Nếu yes → bỏ middle point
  - Return list shorter
- **Mục đích**: Remove collinear points

#### `_remove_transitive(path: list) -> list`

- **Logic**:
  - Loop qua từng point (forward)
  - Thử kết nối `optimized_path[-1]` → `path[i+1]`
  - Dùng shared Fast Voxel Traversal để kiểm tra collision
  - Nếu không collision → bỏ point trung gian
- **Mục đích**: Remove unnecessary intermediate points (line-of-sight)

---

### Functions (Wrappers)

#### `optimize_path(path: list, **options) -> list`

- **Logic**: Wrapper call `PathSmoother.smooth()`

#### `remove_redundant_points(path: list) -> list`

- **Logic**: Call `smooth(remove_redundant=True, remove_transitive=False)`

#### `remove_transitive_redundant_points(path: list) -> list`

- **Logic**: Call `smooth(remove_redundant=True, remove_transitive=True)`

---

# Mối Quan Hệ Giữa Các Module

## Import Flow

```
algorithms → base_planner → (shared utilities)
       ↓
algorithms → (each other for hybrid methods)
       ↓
utils → inertia_weight, path_smoother
       ↓
map → grid_map, map_serializer, map_validator
       ↓
config → (constants)
```

## Algorithm Dependencies

```
A*              : BasePlanner + grid_map + metrics
PSO             : BasePlanner + inertia_weight + path_smoother + metrics
PSO Optimizer   : PSO variant cho segment refinement
APSO            : A* + PSO Optimizer
HAPSO           : A* + PSO Optimizer (với TVAC)
RRT             : BasePlanner + grid_map + metrics
RRT*            : RRT + rewiring logic
```

---

# Quy Tắc Design

✅ **Default Parameters in `__init__`**

- Mọi hyperparameter được define trong `__init__` với default values
- Khi instantiate: `planner = HAPSO(grid_map)` (không truyền args)

✅ **Class Layout (Execution Order)**

1. `__init__`
2. Public entry point (`find_path`)
3. Internal methods (call order)
4. Private helpers (leaf functions)

✅ **Naming Conventions**

- Classes: `PascalCase`
- Functions/Methods: `snake_case`
- Private helpers: `_leading_underscore`
- Constants: `UPPER_SNAKE_CASE`

✅ **No Try/Except/Raise**

- Error handling: `print("[TAG]: message")`
- Validation: Return `None` hoặc `False`

✅ **Import Direction** (No Circular Imports)

```
algorithms → map, config
utils → config
map → config
config → (nothing)
```

---

# 🎮 Simulator Files

## Purpose

**6 interactive simulator files** để test và visualize từng thuật toán. Mỗi file chạy độc lập.

## Files

| File                    | Purpose                | Features                                                      |
| ----------------------- | ---------------------- | ------------------------------------------------------------- |
| `astar-simulator.py`    | A\* interactive demo   | Configurable: diagonal movement, redundant/transitive removal |
| `pso-simulator.py`      | PSO interactive demo   | Configurable: n_particles, n_waypoints, iterations, c1/c2     |
| `apso-simulator.py`     | APSO interactive demo  | Configurable: optimizer particles/iterations, c1/c2           |
| `hapso-simulator.py`    | HAPSO interactive demo | Configurable: optimizer params + TVAC support                 |
| `rrt-simulator.py`      | RRT interactive demo   | Configurable: max_iterations, step_size, goal_sample_rate     |
| `rrt_star-simulator.py` | RRT\* interactive demo | Configurable: all RRT params + neighbor_radius                |

## Usage

```bash
# Run from root folder
python simulator/astar-simulator.py      # A*
python simulator/pso-simulator.py        # PSO
python simulator/apso-simulator.py       # APSO
python simulator/hapso-simulator.py      # HAPSO
python simulator/rrt-simulator.py        # RRT
python simulator/rrt_star-simulator.py   # RRT*
```

## Features

### Terminal Output

```
══════════════════════════════════════
  {ALGORITHM} SIMULATOR
══════════════════════════════════════
Map        : 30×30 | Obstacles: 15
Start      : (1, 1)  →  Goal: (28, 28)
──────────────────────────────────────
Status     : SUCCESS / FAILED
──────────────────────────────────────
Path Length    : 42.15
Waypoints      : 18
Turning Angle  : 12.50 rad
Min Clearance  : 2.50
Execution Time : 0.0234s
══════════════════════════════════════
```

### Pygame Visualization

- **Background**: White (free space)
- **Obstacles**: Black cells
- **Start**: Green cell
- **Goal**: Red cell
- **Path**: Blue line connecting waypoints
- **Waypoints**: Small blue dots on path
- **No Path**: Red text "NO PATH FOUND" center of screen

**Controls**:

- ESC: Exit
- Close window: Exit

## Config Section

Mỗi simulator file có "Config" section ở đầu với parameters có thể chỉnh:

```python
# Example (pso-simulator.py)
N_PARTICLES = PSO_N_PARTICLES                    # Default từ algo_config.py
N_WAYPOINTS = PSO_N_WAYPOINTS
MAX_ITERATIONS = PSO_MAX_ITERATIONS
INERTIA_WEIGHT = PSO_INERTIA_WEIGHT
COGNITIVE_COEFFICIENT = PSO_COGNITIVE_COEFFICIENT
SOCIAL_COEFFICIENT = PSO_SOCIAL_COEFFICIENT

MAP_PATH = "maps/test_map.json"                 # Map to load
WINDOW_WIDTH = 600                              # Pygame window size
WINDOW_HEIGHT = 600
```

Thay đổi giá trị trước khi chạy.

## Map Format

Tất cả simulators expect map ở dạng JSON:

```json
{
  "width": 30,
  "height": 30,
  "start": [1, 1],
  "goal": [28, 28],
  "grid": [
    [0, 0, 0, ..., 0],
    [0, 1, 1, ..., 0],
    ...
  ]
}
```

- `0` = Walkable cell
- `1` = Obstacle cell

## Metrics Reported

Mỗi simulator tính 5 metrics:

1. **Path Length** — Total Euclidean distance of path
2. **Waypoints** — Number of path waypoints
3. **Turning Angle** — Sum of all turning angles (rad)
4. **Min Clearance** — Minimum safety distance to obstacles
5. **Execution Time** — Algorithm runtime (seconds)

## Requirements

```bash
pip install pygame
```

Pygame cần cài để visualization. Nếu không có, simulators vẫn chạy nhưng sẽ bỏ visualization.

---

# Summary

| File                        | Classes | Functions         | Purpose           |
| --------------------------- | ------- | ----------------- | ----------------- |
| config/algo_config.py       | 0       | 0 (60+ constants) | Hyperparameters   |
| core/models.py              | 3       | 0                 | Data models       |
| core/metrics.py             | 0       | 6                 | Path evaluation   |
| map/grid_map.py             | 1       | 0                 | Grid model        |
| map/map_serializer.py       | 1       | 0                 | JSON load/save    |
| map/map_validator.py        | 1       | 0                 | Validation        |
| algorithms/base_planner.py  | 1       | 0 (8 methods)     | Abstract base     |
| algorithms/astar.py         | 1       | 0                 | A\* pathfinding   |
| algorithms/pso_optimizer.py | 1       | 0                 | Segment optimizer |
| algorithms/apso.py          | 1       | 0                 | Adaptive PSO      |
| algorithms/hapso.py         | 1       | 0                 | Hybrid A\*+PSO    |
| algorithms/rrt.py           | 2       | 0                 | RRT planner       |
| algorithms/rrt_star.py      | 2       | 0                 | RRT\* planner     |
| utils/inertia_weight.py     | 6       | 0                 | PSO strategies    |
| utils/path_smoother.py      | 1       | 3                 | Path optimization |
| **TOTAL Core**              | **22**  | **9**             | **6 algorithms**  |
|                             |         |                   |                   |
| **Simulators (6)**          | **N/A** | **N/A**           | Interactive demos |

---

**Last Updated**: 2026-05-04  
**Status**: ✅ Production Ready  
**Algorithms Implemented**: A*, PSO (via APSO), APSO, HAPSO, RRT, RRT*  
**Simulators**: ✅ 6/6 with Pygame visualization
