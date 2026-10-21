# HAPSO Path Planning Studio - Cấu Trúc Toàn Bộ Dự Án

**Cập nhật:** 09/04/2026  
**Phiên bản:** 2.0 (AFTER REFACTORING)

> ⚠️ **REFACTORED**: Tất cả logic thuật toán và tìm đường đã bị loại bỏ.
> Chỉ giữ lại UI, I/O, và stub interface. Các thuật toán trả về đường đi trống `[]`.

---

## 📋 MỤC LỤC

1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
3. [Các Tệp Tin Chi Tiết](#các-tệp-tin-chi-tiết)
4. [Các Lớp (Classes) và Hàm (Functions)](#các-lớp-và-hàm)
5. [Bảng Tóm Tắt Thuật Toán](#bảng-tóm-tắt-thuật-toán)
6. [Quy Trình Làm Việc](#quy-trình-làm-việc)
7. [Biểu Đồ Phụ Thuộc Module](#biểu-đồ-phụ-thuộc-module)

---

## 🎯 Tổng Quan Dự Án

**HAPSO Path Planning Studio** (Phiên bản Refactored) là ứng dụng UI + I/O layer sau khi xóa tất cả logic lập kế hoạch đường đi.

**Status:**

- ✅ UI Screens (F1-F4) - Hoạt động bình thường
- ✅ I/O Layer (map_io, result_io) - Hoạt động bình thường
- ✅ Grid Utilities - Hoạt động bình thường
- ❌ Planners (A\*, PSO, APSO, HAPSO) - Stubbed (trả về [])
- ❌ Geometry/Path Utils - Stubbed (không tính toán)
- ❌ Metrics - Stubbed (trả về 0/False)

**Ngôn Ngữ & Công Nghệ:**

- Python 3.9+
- Pygame (UI/Đồ Họa)
- NumPy (Tối thiểu usage)
- SciPy (Không dùng)
- Matplotlib (Không dùng)

---

## 📁 Cấu Trúc Thư Mục (Sau Refactor)

```
hapso-draft/
├── main.py                          # ✅ Giữ lại - Entry point
├── requirements.txt                 # ✅ Cập nhật - Bỏ scipy, matplotlib
├── structure.md                     # Tài liệu này
│
├── app_io/                          # ✅ Giữ lại - Module I/O chính
│   ├── __init__.py
│   ├── map_io.py                   # ✅ Lưu/tải bản đồ
│   ├── result_io.py                # ✅ Lưu kết quả
│   └── experiment_runner.py        # 🔶 Stubbed - Trả về inf
│
├── evaluation/                      # 🔶 Stubbed
│   ├── __init__.py
│   └── metrics.py                  # 🔶 Tất cả hàm trả về 0/False
│
├── utils/                          # ✅ Partial - Giữ grid_utils, stub geometry/path
│   ├── __init__.py
│   ├── grid_utils.py               # ✅ Giữ lại - Kiểu Grid, Point
│   ├── geometry.py                 # 🔶 Stubbed - Trả về 0/True/False
│   └── path_utils.py               # 🔶 Stubbed - Trả về []
│
├── ui/                             # ✅ Giữ lại - Giao diện hoàn toàn
│   ├── __init__.py
│   ├── common.py                   # ✅ Components & colors
│   ├── map_editor_screen.py        # ✅ F1 - Chỉnh sửa bản đồ
│   ├── simulation_screen.py        # ✅ F2 - Chạy thuật toán (trả về [])
│   ├── compare_weight_screen.py    # ✅ F3 - So sánh trọng số
│   └── compare_result_screen.py    # ✅ F4 - So sánh kết quả
│
├── planners/                       # 🔶 Stubbed - Tất cả return []
│   ├── __init__.py
│   ├── base.py                     # 🔶 BasePlanner - plan() return []
│   ├── astar.py                    # 🔶 AStarPlanner - plan() return []
│   ├── pso_planner.py              # 🔶 PSOPlanner - plan() return []
│   ├── pso_optimizer.py            # 🔶 PSOOptimizer - optimize() return path
│   ├── hybrid.py                   # 🔶 HybridPlanner - plan() return []
│   └── inertia_weight.py           # 🔶 Strategies - compute() vẫn hoạt động
│
├── data/                           # ✅ Giữ - Dữ liệu bản đồ
│   ├── maps/                       # Thư mục bản đồ
│   └── results/                    # Thư mục kết quả
│
├── io/                             # ❌ XÓA - Legacy
├── other_project/                  # ❌ XÓA - Không liên quan
└── venv/                           # ❌ XÓA - Virtual env

Legend: ✅ = Giữ lại | 🔶 = Stubbed | ❌ = Xóa
```

---

## 📄 Các Tệp Tin Chi Tiết

### 🚀 Điểm Vào Ứng Dụng

#### **main.py**

**Ý Nghĩa:** Khởi động ứng dụng và quản lý vòng lặp chính (game loop).

**Các Lớp Chính:**

| Lớp        | Ý Nghĩa                      | Thuộc Tính Quan Trọng                                                                                      |
| ---------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `AppState` | Quản lý trạng thái toàn cục  | `window_width`, `window_height`, `grid_width`, `grid_height`, `cell_size`, `grid`, `start`, `goal`, `path` |
| `App`      | Bộ điều khiển ứng dụng chính | Quản lý 4 màn hình, xử lý sự kiện bàn phím, duy trì 60 FPS                                                 |

**Hàm Quan Trọng:**

| Hàm                   | Ý Nghĩa        | Thông Số          |
| --------------------- | -------------- | ----------------- |
| `create_empty_grid()` | Tạo lưới trống | `width`, `height` |

**Các Màn Hình (Screens):**

| Phím | Màn Hình            | Ý Nghĩa                        |
| ---- | ------------------- | ------------------------------ |
| F1   | MapEditorScreen     | Chỉnh sửa bản đồ               |
| F2   | SimulationScreen    | Chạy mô phỏng thuật toán       |
| F3   | CompareWeightScreen | So sánh trọng số quán tính     |
| F4   | CompareResultScreen | So sánh kết quả các thuật toán |

---

### 💾 Module I/O (app_io/)

#### **app_io/map_io.py**

**Ý Nghĩa:** Lưu và tải bản đồ từ tệp.

**Hàm Quan Trọng:**

| Hàm                   | Ý Nghĩa                       | Thông Số                                         | Trả Về                 |
| --------------------- | ----------------------------- | ------------------------------------------------ | ---------------------- |
| `save_map_json()`     | Lưu bản đồ dạng JSON          | `path`, `grid`, `start`, `goal`                  | None                   |
| `load_map_json()`     | Tải bản đồ từ JSON            | `path`                                           | `(Grid, Point, Point)` |
| `save_map_png()`      | Lưu bản đồ dạng PNG           | `path`, `grid`, `cell_size`                      | None                   |
| `save_map_bundle()`   | Lưu trọn bộ bản đồ (JSON+PNG) | `grid`, `start`, `goal`, `cell_size`, `base_dir` | `Path`                 |
| `list_saved_maps()`   | Liệt kê tất cả bản đồ đã lưu  | `base_dir`                                       | `list[Path]`           |
| `load_map_from_dir()` | Tải bản đồ từ thư mục         | `map_dir`                                        | `(Grid, Point, Point)` |

---

#### **app_io/result_io.py**

**Ý Nghĩa:** Lưu và hiển thị kết quả lập kế hoạch đường đi.

**Hàm Quan Trọng:**

| Hàm                        | Ý Nghĩa             | Thông Số                                                                                     | Trả Về           |
| -------------------------- | ------------------- | -------------------------------------------------------------------------------------------- | ---------------- |
| `_render_result_surface()` | Vẽ kết quả đường đi | `grid`, `path`, `start`, `goal`, `cell_size`                                                 | `pygame.Surface` |
| `save_result_bundle()`     | Lưu kết quả toàn bộ | `grid`, `path`, `start`, `goal`, `algorithm`, `metrics`, `settings`, `cell_size`, `base_dir` | `Path`           |

**Dữ Liệu Được Lưu:**

- Tên thuật toán
- Tọa độ bắt đầu/kết thúc và toàn bộ đường đi
- Các chỉ số hiệu năng (độ dài, độ trơn, số nút, giá trị mục tiêu)
- Cài đặt được sử dụng
- Hình ảnh hiển thị (PNG)

---

#### **app_io/experiment_runner.py**

**Ý Nghĩa:** Chạy thí nghiệm so sánh nhiều thuật toán.

**Các Lớp:**

| Lớp                | Ý Nghĩa                            | Thuộc Tính                                                 |
| ------------------ | ---------------------------------- | ---------------------------------------------------------- |
| `ExperimentResult` | Kết quả từ một lần chạy thuật toán | `name`, `length`, `smoothness`, `nodes`, `objective_value` |

**Hàm Quan Trọng:**

| Hàm                          | Ý Nghĩa                     | Thông Số                          | Trả Về                   |
| ---------------------------- | --------------------------- | --------------------------------- | ------------------------ |
| `build_default_algorithms()` | Tạo các instance thuật toán | `config`                          | `dict[str, object]`      |
| `run_experiments()`          | Chạy tất cả thuật toán      | `grid`, `start`, `goal`, `config` | `list[ExperimentResult]` |

**Các Thuật Toán Được Tạo:**

1. **A\***: Tìm đường tất định, tối ưu
2. **PSO**: Tối ưu hóa bầy hạt
3. **APSO**: Kết hợp A\* + PSO
4. **HAPSO**: A\* nâng cao + PSO

**Cấu Hình Mặc Định:**

- `planner_particles`: 30
- `planner_iterations`: 60
- `planner_waypoints`: 6
- `optimizer_particles`: 24
- `optimizer_iterations`: 40

---

### 📊 Module Đánh Giá (evaluation/)

#### **evaluation/metrics.py**

**Ý Nghĩa:** Tính toán chất lượng và tính hợp lệ của đường đi.

**Hàm Quan Trọng:**

| Hàm                 | Ý Nghĩa                      | Thông Số                                | Trả Về           |
| ------------------- | ---------------------------- | --------------------------------------- | ---------------- |
| `path_length()`     | Tính tổng khoảng cách Euclid | `path`                                  | `float`          |
| `node_count()`      | Đếm số nút trong đường đi    | `path`                                  | `int`            |
| `total_rotation()`  | Tính tổng góc quay           | `path`                                  | `float` (radian) |
| `path_smoothness()` | = `total_rotation()`         | `path`                                  | `float`          |
| `is_path_valid()`   | Kiểm tra đường đi hợp lệ     | `path`, `grid`                          | `bool`           |
| `objective()`       | Hàm fitness kết hợp          | `path`, `grid`, `alpha=0.7`, `beta=0.3` | `float`          |

**Công Thức Objective:**

```
objective = alpha * path_length + beta * path_smoothness + penalty
```

- `alpha = 0.7` (trọng số độ dài)
- `beta = 0.3` (trọng số độ trơn)
- `penalty = 1e6` (nếu đường đi không hợp lệ)

---

### 🛠️ Các Module Tiện Ích (utils/)

#### **utils/grid_utils.py**

**Ý Nghĩa:** Định nghĩa kiểu dữ liệu và tiện ích lưới.

**Định Nghĩa Kiểu:**

| Kiểu    | Ý Nghĩa | Giá Trị                                   |
| ------- | ------- | ----------------------------------------- |
| `Grid`  | Lưới 2D | `list[list[int]]` (0=rỗng, 1=chướng ngại) |
| `Point` | Tọa độ  | `tuple[int, int]` (x, y)                  |

**Hàm Quan Trọng:**

| Hàm               | Ý Nghĩa                       | Thông Số                                                                       | Trả Về            |
| ----------------- | ----------------------------- | ------------------------------------------------------------------------------ | ----------------- |
| `is_valid()`      | Kiểm tra tọa độ trong phạm vi | `x`, `y`, `grid`                                                               | `bool`            |
| `is_obstacle()`   | Kiểm tra ô chứa chướng ngại   | `x`, `y`, `grid`                                                               | `bool`            |
| `get_neighbors()` | Lấy các ô lân cận hợp lệ      | `x`, `y`, `grid`, `diagonal`, `avoid_corner_cutting`, `check_corner_collision` | `Iterable[Point]` |

---

#### **utils/geometry.py**

**Ý Nghĩa:** Tính toán hình học và phát hiện line-of-sight.

**Hàm Quan Trọng:**

| Hàm                        | Ý Nghĩa                     | Thông Số                                   | Trả Về        |
| -------------------------- | --------------------------- | ------------------------------------------ | ------------- |
| `euclidean_distance()`     | Tính khoảng cách Euclid     | `p1`, `p2`                                 | `float`       |
| `_bresenham_cells()`       | Rasterize đường thẳng (DDA) | `p1`, `p2`                                 | `list[Point]` |
| `has_line_of_sight()`      | Kiểm tra tầm nhìn thẳng     | `p1`, `p2`, `grid`, `avoid_corner_cutting` | `bool`        |
| `check_corner_collision()` | Phát hiện va chạm góc cắt   | `p1`, `p2`, `grid`                         | `bool`        |

**Tác Dụng `check_corner_collision()`:**

- Khi di chuyển chéo, kiểm tra cả 2 ô góc kề
- Nếu góc bị chắn, không cho phép di chuyển chéo
- Tránh "cắt góc" qua khoảng trống hẹp

---

#### **utils/path_utils.py**

**Ý Nghĩa:** Mã hóa/giải mã đường đi cho PSO.

**Định Nghĩa Kiểu:**

| Kiểu       | Ý Nghĩa                                    |
| ---------- | ------------------------------------------ |
| `Particle` | `np.ndarray` - Mảng phẳng tọa độ điểm dừng |

**Hàm Quan Trọng:**

| Hàm                  | Ý Nghĩa                      | Thông Số                                          | Trả Về           |
| -------------------- | ---------------------------- | ------------------------------------------------- | ---------------- |
| `encode_particle()`  | Chuyển đường đi → mảng phẳng | `path`, `n_waypoints`                             | `Particle`       |
| `decode_particle()`  | Chuyển mảng phẳng → đường đi | `particle`, `start`, `goal`, `grid`               | `list[Point]`    |
| `clip_to_bounds()`   | Cắt giá trị vào phạm vi lưới | `particle`, `grid`                                | `Particle`       |
| `initialize_swarm()` | Tạo bầy PSO ban đầu          | `n_particles`, `n_waypoints`, `grid`, `seed_path` | `list[Particle]` |

**Khởi Tạo Bầy:**

- Nếu có `seed_path`: Tạo bầy xung quanh seed với nhiễu Gaussian
- Nếu không: Khởi tạo ngẫu nhiên đều trên lưới

---

### 🎨 Giao Diện (ui/)

#### **ui/common.py**

**Ý Nghĩa:** Các thành phần UI và styling chung.

**Hằng Số:**

| Hằng                                      | Ý Nghĩa      | Giá Trị |
| ----------------------------------------- | ------------ | ------- |
| `FONT_SMALL`, `FONT_NORMAL`, `FONT_LARGE` | Kích cỡ font | 24      |

**Bảng Màu (PALETTE):**

| Màu        | RGB             | Ý Nghĩa             |
| ---------- | --------------- | ------------------- |
| `bg`       | (255, 255, 255) | Nền trắng           |
| `obstacle` | (0, 0, 0)       | Chướng ngại đen     |
| `start`    | (39, 163, 108)  | Điểm bắt đầu xanh   |
| `goal`     | (216, 73, 60)   | Điểm kết thúc đỏ    |
| `path`     | (53, 112, 201)  | Đường đi xanh dương |
| `grid`     | (185, 185, 185) | Lưới xám            |

**Các Lớp:**

| Lớp         | Ý Nghĩa        | Phương Thức Chính                                                        |
| ----------- | -------------- | ------------------------------------------------------------------------ |
| `Button`    | Nút bấm UI     | `draw(surface, font)`                                                    |
| `TextInput` | Ô nhập văn bản | `handle_event(event)`, `draw(surface, font)`, `get_int()`, `get_float()` |

**Hàm:**

| Hàm            | Ý Nghĩa        | Thông Số                                  |
| -------------- | -------------- | ----------------------------------------- |
| `draw_title()` | Vẽ tiêu đề lớn | `surface`, `title`, `subtitle`, `start_y` |

---

#### **ui/map_editor_screen.py**

**Ý Nghĩa:** Giao diện chỉnh sửa bản đồ (F1).

**Các Lớp:**

| Lớp               | Ý Nghĩa           |
| ----------------- | ----------------- |
| `MapEditorScreen` | Bộ soạn thảo lưới |

**Chế Độ (Modes):**

| Phím | Chế Độ   | Ý Nghĩa            |
| ---- | -------- | ------------------ |
| `1`  | Obstacle | Vẽ chướng ngại     |
| `2`  | Erase    | Xóa chướng ngại    |
| `S`  | Start    | Đặt điểm bắt đầu   |
| `G`  | Goal     | Đặt điểm kết thúc  |
| `C`  | Clear    | Xóa toàn bộ bản đồ |
| `M`  | Save     | Lưu bản đồ         |
| `L`  | Load     | Tải bản đồ         |

**Phương Thức Quan Trọng:**

| Phương Thức      | Ý Nghĩa                      | Thông Số                 |
| ---------------- | ---------------------------- | ------------------------ |
| `handle_event()` | Xử lý sự kiện mouse/keyboard | `event`                  |
| `draw()`         | Vẽ giao diện                 | `surface`                |
| `_to_grid()`     | Chuyển pixel → tọa độ lưới   | `mouse_pos`              |
| `_paint_line()`  | Vẽ dòng chướng ngại          | `start_cell`, `end_cell` |
| `_clear_map()`   | Reset bản đồ                 | -                        |

---

#### **ui/simulation_screen.py**

**Ý Nghĩa:** Giao diện chạy mô phỏng (F2).

**Lựa Chọn Thuật Toán:**

| Phím | Thuật Toán | Ý Nghĩa            |
| ---- | ---------- | ------------------ |
| `A`  | A\*        | Tìm đường chuẩn    |
| `P`  | PSO        | Bầy hạt thuần      |
| `O`  | APSO       | A\* + PSO          |
| `H`  | HAPSO      | A\* nâng cao + PSO |

**Lựa Chọn & Thiết Lập:**

| Phím    | Chức Năng | Ý Nghĩa               |
| ------- | --------- | --------------------- |
| `SPACE` | Run       | Chạy thuật toán       |
| `K`     | Save      | Lưu kết quả           |
| `1`     | Toggle    | Loại bỏ điểm thừa     |
| `2`     | Toggle    | Loại bỏ waypoint thừa |
| `3`     | Toggle    | Tránh cắt góc         |

**Hiển Thị Thông Tin:**

- Độ dài đường đi
- Số nút
- Tổng góc quay
- Giá trị mục tiêu

---

#### **ui/compare_result_screen.py**

**Ý Nghĩa:** So sánh kết quả của tất cả 4 thuật toán (F4).

**Lớp:**

| Lớp                   | Ý Nghĩa              |
| --------------------- | -------------------- |
| `CompareResultScreen` | Bảng so sánh kết quả |

**Biểu Đồ Hiển Thị:**

| Biểu Đồ 1 | Biểu Đồ 2 | Biểu Đồ 3 | Biểu Đồ 4        | Biểu Đồ 5     |
| --------- | --------- | --------- | ---------------- | ------------- |
| Độ dài    | Số nút    | Độ quay   | Giá trị mục tiêu | Điểm tổng hợp |

**Phương Thức:**

| Phương Thức       | Ý Nghĩa                      | Thông Số |
| ----------------- | ---------------------------- | -------- |
| `_run_and_draw()` | Chạy thí nghiệm & vẽ biểu đồ | -        |

---

#### **ui/compare_weight_screen.py**

**Ý Nghĩa:** So sánh các chiến lược trọng số quán tính (F3).

**Lớp:**

| Lớp                   | Ý Nghĩa                           |
| --------------------- | --------------------------------- |
| `CompareWeightScreen` | So sánh chiến lược inertia weight |

**Các Chiến Lược:**

| Chiến Lược           | Viết Tắt | Ý Nghĩa         |
| -------------------- | -------- | --------------- |
| Linear Decreasing    | LDIW     | Giảm tuyến tính |
| Nonlinear Decreasing | NDIW     | Giảm phi tuyến  |
| Adaptive             | AIW      | Thích ứng       |
| Stochastic           | SIW      | Ngẫu nhiên      |

**Tham Số Cấu Hình:**

- `Iterations`: Số lần lặp PSO
- `w_min`: Trọng số tối thiểu (mặc định 0.4)
- `w_max`: Trọng số tối đa (mặc định 0.9)
- `R` - Tính toán lại và hiển thị

---

### 🤖 Các Thuật Toán (planners/)

#### **planners/base.py**

**Ý Nghĩa:** Lớp cơ sở trừu tượng cho tất cả các planner.

**Lớp:**

| Lớp                 | Ý Nghĩa   | Phương Thức                              |
| ------------------- | --------- | ---------------------------------------- |
| `BasePlanner` (ABC) | Lớp cơ sở | `plan(grid, start, goal) -> list[Point]` |

---

#### **planners/astar.py**

**Ý Nghĩa:** Thuật toán A\* với tùy chọn hậu xử lý.

**Lớp:**

| Lớp                         | Ý Nghĩa             |
| --------------------------- | ------------------- |
| `AStarPlanner(BasePlanner)` | Bộ lập kế hoạch A\* |

**Tùy Chọn:**

| Tùy Chọn                     | Ý Nghĩa                                    | Mặc Định |
| ---------------------------- | ------------------------------------------ | -------- |
| `remove_redundant_points`    | Loại bỏ điểm thẳng hàng                    | False    |
| `remove_redundant_waypoints` | Loại bỏ waypoint thừa (visibility pruning) | False    |
| `corner_collision_check`     | Kiểm tra va chạm góc                       | False    |

**Phương Thức Quan Trọng:**

| Phương Thức                    | Ý Nghĩa                  | Thông Số                |
| ------------------------------ | ------------------------ | ----------------------- |
| `plan()`                       | Chạy A\*                 | `grid`, `start`, `goal` |
| `_reconstruct()`               | Dò ngược từ goal → start | -                       |
| `_post_process()`              | Áp dụng tối ưu hóa       | `path`, `grid`          |
| `remove_redundant_points()`    | Loại bỏ điểm thẳng hàng  | -                       |
| `remove_redundant_waypoints()` | Visibility pruning       | -                       |

**Thuật Toán:**

- Sử dụng heap-based open set
- Heuristic: Khoảng cách Euclid đến goal
- Di chuyển 8 hướng (kể cả chéo)

---

#### **planners/pso_planner.py**

**Ý Nghĩa:** Thuật toán PSO thuần để lập kế hoạch đường đi.

**Lớp:**

| Lớp                       | Ý Nghĩa             |
| ------------------------- | ------------------- |
| `PSOPlanner(BasePlanner)` | Bộ lập kế hoạch PSO |

**Tham Số:**

| Tham Số        | Ý Nghĩa             | Mặc Định |
| -------------- | ------------------- | -------- |
| `n_particles`  | Kích cỡ bầy         | 30       |
| `n_iterations` | Số lần lặp          | 60       |
| `n_waypoints`  | Số điểm dừng        | 6        |
| `c1`           | Hệ số Cognitive     | 1.6      |
| `c2`           | Hệ số Social        | 1.6      |
| `inertia`      | Chiến lược trọng số | SIW      |

**Phương Thức:**

| Phương Thức  | Ý Nghĩa              |
| ------------ | -------------------- |
| `plan()`     | Chạy PSO             |
| `_fitness()` | Tính giá trị fitness |

**Thuật Toán:**

- Mã hóa đường đi thành tọa độ hạt
- Cập nhật vận tốc và vị trí lặp đi lặp lại
- Theo dõi pbest (tốt nhất cá nhân) và gbest (tốt nhất toàn cục)
- Trọng số quán tính thích ứng: khám phá → khai thác

---

#### **planners/pso_optimizer.py**

**Ý Nghĩa:** Bộ tối ưu hóa PSO để tinh chỉnh đường đi.

**Lớp:**

| Lớp            | Ý Nghĩa       |
| -------------- | ------------- |
| `PSOOptimizer` | Bộ tối ưu PSO |

**Tham Số:**

| Tham Số        | Ý Nghĩa         | Mặc Định |
| -------------- | --------------- | -------- |
| `n_particles`  | Kích cỡ bầy     | 24       |
| `n_iterations` | Số lần lặp      | 40       |
| `c1`           | Hệ số Cognitive | 1.5      |
| `c2`           | Hệ số Social    | 1.7      |

**Phương Thức:**

| Phương Thức  | Ý Nghĩa             | Thông Số       |
| ------------ | ------------------- | -------------- |
| `optimize()` | Tinh chỉnh đường đi | `path`, `grid` |
| `_fitness()` | Tính fitness        | -              |

**Khặc Độc Đáo:**

- Mã hóa đường đi đầu vào thành hạt "seed"
- Thay hạt tệ nhất bằng seed
- Đảm bảo cải thiện hơn là loại bỏ giải pháp ban đầu

---

#### **planners/hybrid.py**

**Ý Nghĩa:** Kết hợp Planner + Optimizer thành 2 giai đoạn.

**Lớp:**

| Lớp                          | Ý Nghĩa    |
| ---------------------------- | ---------- |
| `HybridPlanner(BasePlanner)` | Bộ kết hợp |

**Kết Hợp Được Hỗ Trợ:**

| Tên       | Tác Dụng            | Kết Hợp                                        |
| --------- | ------------------- | ---------------------------------------------- |
| **PSO**   | PSO + PSO Optimizer | PSOPlanner + PSOOptimizer                      |
| **APSO**  | A\* + PSO Optimizer | AStarPlanner + PSOOptimizer                    |
| **HAPSO** | A\* nâng cao + PSO  | AStarPlanner(corner_check=True) + PSOOptimizer |

**Quy Trình:**

1. Giai đoạn 1: Tạo đường đi ban đầu bằng Planner
2. Giai đoạn 2: Tinh chỉnh bằng Optimizer

---

#### **planners/inertia_weight.py**

**Ý Nghĩa:** Các chiến lược trọng số quán tính để kiểm soát hội tụ PSO.

**Lớp Cơ Sở:**

| Lớp                   | Ý Nghĩa   | Phương Thức                            |
| --------------------- | --------- | -------------------------------------- |
| `InertiaWeight` (ABC) | Lớp cơ sở | `compute(k, t_max, **kwargs) -> float` |

**Các Chiến Lược Cụ Thể:**

| Chiến Lược           | Viết Tắt | Công Thức                               | Ý Nghĩa                                |
| -------------------- | -------- | --------------------------------------- | -------------------------------------- |
| Linear Decreasing    | LDIW     | `w_max - (w_max - w_min) * (k / t_max)` | Giảm tuyến tính                        |
| Nonlinear Decreasing | NDIW     | `exp(-exp((t_max - k) / t_max))`        | Giảm phi tuyến với hội tụ nhanh ở cuối |
| Adaptive             | AIW      | Dựa vào tỉ lệ cải thiện fitness         | Giảm theo tiến độ                      |
| Stochastic           | SIW      | LDIW + nhiễu ngẫu nhiên                 | LDIW với tính linh hoạt                |

**Tham Số:**

- `w_min`: Trọng số tối thiểu (mặc định 0.4)
- `w_max`: Trọng số tối đa (mặc định 0.9)

---

## 📊 Bảng Tóm Tắt Thuật Toán

| Thuật Toán | Loại         | Đặc Điểm                      | Trường Hợp Sử Dụng                       |
| ---------- | ------------ | ----------------------------- | ---------------------------------------- |
| **A\***    | Tất định     | Nhanh, đầy đủ, tối ưu         | Baseline, kiểm soát chi tiết             |
| **PSO**    | Tiến hóa     | Tìm kiếm toàn cục, tự nhiên   | Khám phá, tối ưu waypoint                |
| **APSO**   | Lai          | A\* khởi tạo + PSO tinh chỉnh | Cân bằng tốc độ và chất lượng            |
| **HAPSO**  | Lai nâng cao | A\* (kiểm tra góc) + PSO      | Chất lượng tốt nhất với kiểm tra an toàn |

---

## 🔄 Quy Trình Làm Việc

### Bước 1: Chỉnh Sửa Bản Đồ (F1)

```
MapEditorScreen
├── Chọn chế độ (Obstacle/Erase/Start/Goal)
├── Vẽ chướng ngại bằng cách kéo mouse
├── Đặt điểm bắt đầu (S) và kết thúc (G)
└── Lưu bản đồ (M) → data/maps/{timestamp}/
```

### Bước 2: Chạy Mô Phỏng (F2)

```
SimulationScreen
├── Chọn thuật toán (A/P/O/H)
├── Cấu hình tùy chọn (1/2/3)
├── SPACE → Chạy thuật toán
├── Hiển thị kết quả và chỉ số
└── K → Lưu kết quả → data/results/{timestamp}/
```

### Bước 3: So Sánh Kết Quả (F4)

```
CompareResultScreen
├── Chạy tất cả 4 thuật toán
├── Tính toán chỉ số cho mỗi thuật toán
├── Chuẩn hóa kết quả
└── Hiển thị 5 biểu đồ so sánh
```

### Bước 4: So Sánh Trọng Số (F3)

```
CompareWeightScreen
├── Cấu hình Iterations, w_min, w_max
├── R → Tính toán lại
└── Hiển thị đồ thị tiến hóa của 4 chiến lược
```

---

## 📐 Biểu Đồ Phụ Thuộc Module

```
main.py
│
├── ui/ (Các giao diện)
│   ├── common.py (Thành phần chung)
│   │
│   ├── map_editor_screen.py
│   │   └── app_io/map_io.py
│   │
│   ├── simulation_screen.py
│   │   ├── app_io/result_io.py
│   │   ├── evaluation/metrics.py
│   │   └── planners/*
│   │
│   ├── compare_result_screen.py
│   │   ├── app_io/experiment_runner.py
│   │   └── evaluation/metrics.py
│   │
│   └── compare_weight_screen.py
│       └── planners/inertia_weight.py
│
├── planners/ (Các thuật toán)
│   ├── base.py (Lớp cơ sở)
│   ├── astar.py
│   ├── pso_planner.py
│   ├── pso_optimizer.py
│   ├── hybrid.py
│   └── inertia_weight.py
│
├── utils/ (Tiện ích)
│   ├── grid_utils.py (Kiểu + tiện ích)
│   ├── geometry.py (Hình học)
│   └── path_utils.py (Mã hóa đường đi)
│
├── evaluation/
│   └── metrics.py (Tính toán chất lượng)
│
└── app_io/ (I/O)
    ├── map_io.py
    ├── result_io.py
    └── experiment_runner.py
```

---

## 📦 Các Phụ Thuộc (Dependencies)

| Thư Viện   | Phiên Bản | Ý Nghĩa            |
| ---------- | --------- | ------------------ |
| numpy      | >=1.21.0  | Mảng số học        |
| pygame     | >=2.1.0   | Đồ họa & UI        |
| scipy      | >=1.7.0   | Tính toán khoa học |
| matplotlib | >=3.5.0   | Biểu đồ & hiển thị |

---

## 🏗️ Các Mẫu Thiết Kế (Design Patterns)

### 1. **Strategy Pattern**

- `BasePlanner` ABC + các implementation (A\*, PSO, Hybrid)
- `InertiaWeight` ABC + các strategy (LDIW, NDIW, AIW, SIW)
- Cho phép thay đổi thuật toán tại runtime

### 2. **Decorator/Wrapper Pattern**

- `HybridPlanner` bao bọc Planner + Optimizer
- Single interface (`plan()`) cho các kết hợp phức tạp

### 3. **Factory Pattern**

- `build_default_algorithms()` tạo các instance với cấu hình mặc định
- Tập trung quản lý cấu hình

### 4. **Data Container Pattern**

- Type aliases (`Grid`, `Point`) cho clarity
- Dataclasses (`AppState`, `ExperimentResult`) cho dữ liệu cấu trúc

### 5. **State Management Pattern**

- `AppState` giữ trạng thái toàn bộ ứng dụng
- Flow: Event → Handler → State → Render

---

## 🚀 Cách Chạy Ứng Dụng

```bash
# Cài đặt phụ thuộc
pip install -r requirements.txt

# Chạy ứng dụng chính
python main.py
```

**Phím Tắt Chính:**

| Phím | Chức Năng        |
| ---- | ---------------- |
| F1   | Chỉnh sửa bản đồ |
| F2   | Chạy mô phỏng    |
| F3   | So sánh trọng số |
| F4   | So sánh kết quả  |
| ESC  | Thoát            |

---

## ⚙️ Cấu Hình & Cải Thiện

### Những Hạn Chế Hiện Tại:

1. Mã trùng lặp trong thư mục `io/` (legacy)
2. Lưới giới hạn kích cỡ nhỏ (~20x20)
3. Không có UI cấu hình tham số PSO
4. Không có animation trong quá trình chạy thuật toán
5. Xử lý lỗi hạn chế

### Các Cải Thiện Đề Xuất:

1. Xóa module `io/` legacy và hợp nhất vào `app_io/`
2. Thêm visualization/animation real-time
3. Cấu hình profile cho các kịch bản khác nhau
4. Export đường đi (DXF, SVG)
5. Multi-threading cho chạy thuật toán
6. Batch experiment runner với phân tích thống kê

---

## 📝 Ghi Chú

- **Hệ Tọa Độ**: (x, y) với x = cột, y = hàng
- **Giá Trị Lưới**: 0 = rỗng, 1 = chướng ngại
- **Hàm Objective**: Kết hợp độ dài (70%) + độ trơn (30%)
- **PSO Mặc Định**: LDIW + 4 hệ số mặc định tối ưu

---

**Tài Liệu này được cập nhật lần cuối: 09/04/2026**  
**Tác Giả: Hệ Thống Tư Vấn AI**  
**Phiên Bản: 1.0**
