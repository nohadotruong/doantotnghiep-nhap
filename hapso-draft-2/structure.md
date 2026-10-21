# HAPSO - Hybrid A\* and PSO Pathfinding Simulation

## 📁 Project Structure

```
hapso-draft-2/
├── main.py                    # Entry point - Khởi động ứng dụng
├── app.py                     # Main GUI application (Pygame)
├── config.py                  # Global configuration constants
│
├── Core Algorithms/
│   ├── astar.py              # A* Search Algorithm
│   ├── pso.py                # Particle Swarm Optimization (PSO)
│   ├── apso.py               # Adaptive PSO with improvements
│   └── hapso.py              # Hybrid A* + PSO
│
├── Utilities/
│   ├── grid_map.py           # Grid map management
│   ├── metrics.py            # Path metrics calculation
│   ├── get_line_grid.py      # Line drawing algorithms
│   ├── path_optimization.py  # Path optimization utilities
│   ├── pso_improvement.py    # PSO inertia weight strategies
│   └── f4_weight_compare.py  # Weight comparison visualization
│
├── Data/
│   ├── maps/                 # Saved grid maps (JSON format)
│   │   ├── 2026-04-10_20-35-57/
│   │   │   └── map.json
│   │   └── 2026-04-13_15-54-37/
│   │       └── map.json
│   └── results/              # Algorithm results (JSON format)
│       └── 2026-04-13_20-36-16/
│           └── result.json
│
└── reference_project/        # Reference implementations
```

---

## 📋 Files Overview

### 🎯 Entry Point

#### **main.py**

```
Mục đích: Khởi động ứng dụng chính
```

- Imports: `from app import App`
- Functions:
  - `if __name__ == '__main__'`: Tạo và chạy ứng dụng GUI

---

### ⚙️ Configuration

#### **config.py**

```
Mục đích: Định nghĩa các hằng số toàn cục cho cấu hình window, giao diện, menu
```

- **Constants:**
  - Window: `WINDOW_WIDTH=1200, WINDOW_HEIGHT=680, FPS=60`
  - Colors: `COLOR_WHITE, COLOR_BLACK, COLOR_LIGHT_GRAY, COLOR_DARK_GRAY`
  - Layout: `NAV_HEIGHT=40, CONTENT_LEFT_RATIO=0.25, CONTENT_RIGHT_RATIO=0.75`
  - Grid: `GRID_SIZE=30, GRID_CELL_SIZE=20`
  - Directories: `MAP_DIR="maps", RESULTS_DIR="results"`
- **Menu Configurations:**
  - `F1_MENU_ITEMS`: Menu của chế độ Map Editor
  - `F2_MENU_ITEMS`: Menu của chế độ Pathfinding
  - `F3_MENU_ITEMS`: Menu của chế độ Line Grid
  - `F5_MENU_ITEMS`: Menu của chế độ Result Compare
  - `MENU_ITEMS`: Ánh xạ F-key đến các trang

---

### 🖥️ GUI Application

#### **app.py**

```
Mục đích: Quản lý giao diện Pygame với 5 trang chức năng (F1-F5)
```

**Class: App**

**Attributes (Trạng thái):**

```
Cửa sổ & Hiển thị:
  - screen: Pygame display surface
  - clock: Pygame clock for FPS
  - running: Bool to control app loop
  - current_page: Current F-key page (F1-F5)

F1 (Map Editor):
  - grid_map: GridMap object
  - load_map_mode: Bool for map loading mode
  - map_list: List of available maps
  - map_selected_index, map_page: Map selection state
  - selected_item: Current editor mode (Obstacle/Ecrease/Start/Goal)
  - editor_status: Status message
  - mouse_pressed, mouse_start_pos, mouse_current_pos: Mouse tracking
  - grid_area: Pygame rect of grid display area

F2 (Pathfinding):
  - f2_algorithm: Selected algorithm (A*, PSO, APSO, HAPSO)
  - f2_remove_redundant: Path optimization flag
  - f2_remove_trans_redundant: Transitive redundant removal
  - f2_avoid_corner_cutting: Corner cutting avoidance
  - f2_use_siw, f2_use_sobl: PSO improvements
  - f2_running: Bool for running state
  - f2_result: Result dictionary with path and metrics

F3 (Line Grid):
  - f3_algorithm: Selected line algorithm
  - f3_line_start, f3_line_end: Line endpoints
  - f3_result_cells: Calculated line cells
  - f3_drawing_line: Bool for drawing state

F4 (Weight Compare):
  - f4_w_min, f4_w_max: Weight range
  - f4_iteration: Number of iterations
  - f4_chart_surface: Rendered chart image
  - f4_chart_ready: Bool for chart state

F5 (Result Compare):
  - f5_status: Status message
  - f5_results: Dictionary of 4 algorithm results
  - f5_chart_surface: Rendered 2x2 dashboard chart
```

**Main Methods:**

- `__init__()`: Khởi tạo ứng dụng, Pygame, trạng thái ban đầu
- `run()`: Main event loop - xử lý sự kiện, cập nhật, vẽ
- `handle_events()`: Xử lý input từ bàn phím và chuột
- `update()`: Cập nhật trạng thái ứng dụng
- `draw()`: Vẽ tất cả nội dung lên màn hình

**Drawing Methods (F1-F5):**

- `draw_navigation()`: Vẽ navigation bar với F-key buttons
- `draw_content_area()`: Vẽ nội dung chính của trang hiện tại
- `draw_f1_menu()`: Menu cho Map Editor
- `draw_f1_info_panel()`: Thông tin grid và trang thái
- `draw_f1_grid_area()`: Vẽ lưới 30x30
- `draw_f2_menu()`: Menu cho Pathfinding
- `draw_f2_info_panel()`: Hiển thị metrics của đường đi
- `draw_f2_grid_area()`: Vẽ lưới với đường đi
- `draw_f3_menu()`: Menu cho Line Grid
- `draw_f3_info_panel()`: Hiển thị kết quả line drawing
- `draw_f3_grid_area()`: Vẽ lưới với các cell của đường thẳng
- `draw_f4_menu()`: Menu cho Weight Compare
- `draw_f4_info_panel()`: Thông tin về weight compare
- `draw_f4_compare_panel()`: Hiển thị biểu đồ inertia weight
- `draw_f5_menu()`: Menu cho Result Compare
- `draw_f5_info_panel()`: Thông tin trạng thái
- `draw_f5_compare_panel()`: Hiển thị 2x2 dashboard của 4 algorithms

**Helper Methods:**

- `_calculate_layout()`: Tính toán vị trí các panel
- `_save_map()`: Lưu grid map hiện tại
- `_open_load_map_ui()`: Mở UI để load map
- `_load_selected_map()`: Load map được chọn
- `_save_result()`: Lưu kết quả pathfinding
- `_run_simulation()`: Chạy thuật toán pathfinding
- `_run_f5_compare()`: Chạy 4 algorithms để so sánh
- `_update_f5_chart()`: Tạo 2x2 matplotlib chart
- `_run_line_grid_algorithm()`: Chạy thuật toán line drawing
- `_paint_line()`: Vẽ line trên grid (mode F1)
- `_pixel_to_grid()`: Chuyển đổi pixel coords -> grid coords
- `_truncate_status()`: Cắt ngắn chuỗi trạng thái
- `_bresenham_line()`: Thuật toán vẽ line (Bresenham)
- `_handle_f1_mouse_event()`: Xử lý chuột trong F1
- `_handle_f3_mouse_event()`: Xử lý chuột trong F3
- `_init_f4_state()`: Khởi tạo trạng thái F4

---

### 🗺️ Grid Management

#### **grid_map.py**

```
Mục đích: Quản lý lưới bản đồ, obstacles, start/goal points
Hỗ trợ save/load từ JSON
```

**Class: GridMap**

**Constants:**

```
FREE = 0       # Ô trống
OBSTACLE = 1   # Chướng ngại vật
START = 2      # Điểm bắt đầu
GOAL = 3       # Điểm đích
```

**Attributes:**

- `width, height`: Kích thước lưới
- `grid`: 2D list đại diện lưới
- `start`: Tuple (x, y) điểm bắt đầu
- `goal`: Tuple (x, y) điểm đích

**Methods:**

- `__init__(width, height)`: Khởi tạo lưới trống
- `clear_map()`: Xóa tất cả obstacles và start/goal
- `is_obstacle(x, y)`: Kiểm tra có phải obstacle
- `is_inside(x, y)`: Kiểm tra có trong lưới
- `set_start(x, y)`: Đặt điểm bắt đầu
- `set_goal(x, y)`: Đặt điểm đích
- `set_obstacle(x, y, value)`: Đặt/xóa obstacle
- `toggle_obstacle(x, y)`: Bật/tắt obstacle
- `get_obstacles()`: Lấy danh sách obstacles
- `get_obstacle_count()`: Đếm số obstacles
- `to_dict()`: Chuyển đổi sang dict for JSON
- `from_dict(data)`: Tạo GridMap từ dict
- `save_map(map_dir, screenshot_func)`: Lưu map ra file JSON
- `load_map(json_path)`: Load map từ file JSON

---

### 🔍 Pathfinding Algorithms

#### **astar.py**

```
Mục đích: Thuật toán A* - tìm đường tối ưu trên lưới
Hỗ trợ loại bỏ điểm dư thừa, tránh cắt góc
```

**Class: Node**

- `x, y`: Tọa độ
- `g`: Chi phí từ start đến node
- `h`: Heuristic cost đến goal
- `f = g + h`: Tổng chi phí
- `parent`: Node cha (để reconstruct path)

**Class: AStar**

- `DIRECTIONS`: 8 hướng di chuyển (4 trực tiếp + 4 đường chéo)
- `STRAIGHT_COST = 1.0`: Chi phí di chuyển thẳng
- `DIAGONAL_COST = 1.414`: Chi phí di chuyển đường chéo
- `remove_redundant`: Bool loại bỏ điểm collinear
- `remove_transitive`: Bool loại bỏ điểm dông giao
- `avoid_corner_cutting`: Bool tránh cắt góc

**Methods:**

- `__init__(grid, remove_redundant, remove_transitive, avoid_corner_cutting)`
- `find_path(start, goal)`: Tìm đường từ start đến goal
- `remove_redundant_points(path)`: Loại bỏ điểm collinear
- `remove_transitive_redundant_points(path)`: Loại bỏ điểm dư thừa
- `_heuristic(x, y, goal_x, goal_y)`: Heuristic Euclidean distance
- `_is_walkable(x, y)`: Kiểm tra di được
- `_can_move_diagonal(x, y, dx, dy)`: Kiểm tra đường chéo có hợp lệ
- `_get_cost(dx, dy)`: Chi phí tương ứng với direction
- `_reconstruct_path(node)`: Reconstruct path từ node

---

#### **pso.py**

```
Mục đích: Particle Swarm Optimization - tối ưu hóa đường đi
Sử dụng waypoints và activation threshold
```

**Class: PSOPlanner**

- Chứa hàm `plan()` để tìm đường PSO

**Class: PSOptimizer**

- Chứa hàm `optimize(path)` để tối ưu hóa path tìm được

**Key Attributes:**

- `n_particles`: Số particles (mặc định 20)
- `max_iter`: Số iteration tối đa (mặc định 200)
- `w, c1, c2`: PSO parameters
- `use_siw, use_sobl`: Các improvement flags
- `w_min, w_max`: Inertia weight range

**Methods:**

- `plan()`: Chạy PSO planner để tìm đường
- `optimize(path)`: Tối ưu hóa đường đã tìm
- Hỗ trợ waypoints động, barrier avoidance, collision detection

---

#### **apso.py**

```
Mục đích: Adaptive PSO - PSO cải tiến với SIW và SOBL
Sử dụng A* như seed path, sau đó PSO tối ưu hóa
```

**Class: APSO**

- Extends PSO với các cải tiến
- Sử dụng A\* để tìm đường ban đầu
- Sau đó dùng PSO để tối ưu hóa

**Attributes:**

- `siw`: SIW (Stochastic Inertia Weight) optimizer
- `sobl`: SOBL (Stochastic Optimal Bayesian Learning) optimizer
- Kế thừa các attributes từ PSO

**Methods:**

- `find_path(start, goal)`: Tìm đường hybrid A\* + PSO
- `_euclidean_distance(p1, p2)`: Tính khoảng cách Euclidean
- `_fitness(path)`: Tính fitness với penalty cho obstacles

---

#### **hapso.py**

```
Mục đích: Hybrid A* + PSO - kết hợp A* và PSO tối ưu
```

**Class: HAPSO**

**Approach:**

1. Sử dụng A\* tìm ban đầu (với remove_redundant=True, avoid_corner_cutting=True)
2. Dùng PSOptimizer để tối ưu hóa result của A\*

**Methods:**

- `__init__(grid, n_particles, max_iter, c1, c2, w_min, w_max)`
- `find_path(start, goal)`: Chạy hybrid algorithm
  - Step 1: A\* find_path()
  - Step 2: PSOptimizer.optimize(a_star_path)
  - Return: optimized path

---

### 📊 Metrics & Analysis

#### **metrics.py**

```
Mục đích: Tính toán metrics đánh giá chất lượng đường đi
Gồm: độ dài, số waypoints, góc quay, thời gian
```

**Class: PathMetrics**

**Constants:**

- `V_M = 1.0`: Vận tốc di chuyển
- `T_P = 0.2`: Thời gian per waypoint
- `V_I = π`: Vận tốc góc

**Key Metrics:**

- `min_d`: Độ dài đường đi (Path Length)
- `min_p`: Số waypoints (Path Points)
- `min_i`: Góc quay tổng (Turning Amplitude)
- `min_c`: Thời gian thuật toán (Algorithm Time)
- `min_t`: Tổng thời gian (Total Time)

**Methods:**

- `calculate_metrics(path, execution_time)`: Tính toàn bộ metrics
- `calculate_path_length(path)`: Tính độ dài (Euclidean distance)
- `calculate_path_points(path)`: Đếm waypoints
- `calculate_turning_amplitude(path)`: Tính tổng góc quay
- `format_metrics(metrics)`: Format để hiển thị đẹp
- `_calculate_angle_difference(x1, y1, x2, y2, x3, y3)`: Tính góc giữa 3 điểm

---

### 📐 Line Drawing Algorithms

#### **get_line_grid.py**

```
Mục đích: Các thuật toán vẽ line trên grid rời rạc
So sánh 4 methods khác nhau
```

**Functions:**

1. **get_line_grid_bresenham(start, end)**
   - Thuật toán Bresenham
   - Tối ưu cho integer coordinates
   - Sử dụng error accumulation

2. **get_line_grid_incremental_traversal(start, end)**
   - DDA (Digital Differential Analyzer) incremental
   - Sử dụng t_max (parameter along line)
   - Phù hợp cho float coordinates

3. **get_line_grid_parametric_discretization(start, end)**
   - Parametric discretization method
   - Sử dụng parametric line equation
   - Kiểm tra mỗi cell dọc line

4. **get_line_grid_runs_of_runs(start, end)**
   - Runs of Runs algorithm (DDA alternative)
   - Efficient run-length encoding
   - Tối ưu cho diagonal lines

5. **compare_methods(start, end)**
   - Chạy cả 4 method
   - Return: dict với results của mỗi method

---

### ⚖️ PSO Inertia Weight Strategies

#### **pso_improvement.py**

```
Mục đích: Các chiến lược inertia weight cho PSO
Giúp cân bằng giữa exploration và exploitation
```

**Base Class: InertiaWeight (ABC)**

- `w_min, w_max`: Giới hạn weight
- `compute(k, t_max, **kwargs)`: Tính w ở iteration k

**Concrete Classes:**

1. **LDIW (Linear Decreasing Inertia Weight)**
   - Giảm tuyến tính: `w = w_max - (w_max - w_min) * (k / t_max)`
   - Simple, widely used

2. **NDIW (Nonlinear Decreasing Inertia Weight)**
   - `w = exp(-exp((t_max - k) / t_max))`
   - Nonlinear decrease

3. **AIW (Adaptive Inertia Weight)**
   - Dựa vào fitness ratio
   - `w = (w_max + w_min) * fitness_ratio - w_max * (k / t_max)`
   - Adaptively adjust based on performance

4. **SIW (Stochastic Inertia Weight)**
   - Tùy biến weight với stochastic perturbation
   - `w = w_max - (w_max - w_min) * (k / t_max) * exp(rb)`
   - Giúp escape local optima

5. **SOBL (Stochastic Optimal Bayesian Learning)**
   - Bayesian-based learning strategy
   - Sử dụng `mu` và `sigma` parameters

---

### 🎨 Visualization

#### **f4_weight_compare.py**

```
Mục đích: Vẽ biểu đồ so sánh 4 inertia weight strategies
Sử dụng matplotlib với Agg backend (non-interactive)
```

**Function: plot_inertia_weights(w_min, w_max, Tmax, pkgbest, pk1gbest)**

- Tạo 4 line plots cho: LDIW, NDIW, AIW, SIW
- X-axis: Iteration (k)
- Y-axis: Inertia weight (w)
- Return: matplotlib.pyplot object để render

---

### 🛠️ Path Optimization

#### **path_optimization.py**

```
Mục đích: Các utility functions để tối ưu hóa paths
Loại bỏ điểm dư thừa, collinear points
```

**Functions:**

1. **optimize_path(path, remove_redundant, remove_transitive)**
   - Wrapper function áp dụng optimizations
   - Return: optimized path

2. **remove_redundant_points(path)**
   - Loại bỏ điểm collinear
   - Giữ lại chỉ điểm "quay" (turning points)
   - Check: `dy1/dx1 == dy2/dx2` (slope equality)

3. **remove_transitive_redundant_points(path)**
   - Advanced redundancy removal
   - Kiểm tra line-of-sight giữa các điểm
   - Loại bỏ điểm nằm giữa 2 điểm nếu có direct line

---

## 🔄 Data Flow & Interactions

### F1 (Map Editor) → F2 (Pathfinding)

```
1. F1: User tạo map (obstacles, start, goal)
2. F1 ENTER: Save map → maps/[timestamp]/map.json
3. F2: Load map từ F1
4. F2 SPACE: Run algorithm → calculate path + metrics
5. F2 ENTER: Save result → results/[timestamp]/result.json
```

### F2 Algorithms Comparison (F5)

```
1. F2: Run một algorithm
2. F5: Run 4 algorithms (A*, PSO, APSO, HAPSO)
3. Mỗi algorithm:
   - Calculate: path, metrics (min_d, min_p, min_i, min_c)
   - Store kết quả
4. Create 2x2 matplotlib dashboard:
   - Top-left: Length (min_d)
   - Top-right: Turning (min_i)
   - Bottom-left: Time (min_c)
   - Bottom-right: Waypoints (min_p)
5. Render to pygame surface → display
```

### F3 Line Drawing Algorithms

```
1. Copy start/goal từ F1
2. Select algorithm: B/V/D/S
3. SPACE: Run → calculate grid cells
4. Display cells trên grid
5. Compare: khác nhau về cells dùng (trade-off accuracy/performance)
```

### F4 Weight Comparison

```
1. Input w_min, w_max, iterations
2. SPACE: Calculate 4 weight strategies
3. Plot line chart: w vs iteration
4. Display matplotlib chart trên pygame
```

---

## 📝 JSON Format

### Map File (maps/[timestamp]/map.json)

```json
{
  "width": 30,
  "height": 30,
  "start": [0, 0],
  "goal": [29, 29],
  "grid": [
    [2, 0, 1, 0, ...],
    [0, 0, 0, 0, ...],
    ...
  ]
}
```

### Result File (results/[timestamp]/result.json)

```json
{
  "algorithm": "HAPSO",
  "start": [0, 0],
  "goal": [29, 29],
  "path": [[0,0], [1,1], [2,2], ...],
  "path_length": 42.5,
  "execution_time": 0.0234,
  "metrics": {
    "min_d": 42.5,
    "min_p": 35,
    "min_i": 12.4,
    "min_c": 0.0234,
    "min_t": 8.234
  },
  "remove_redundant": true,
  "remove_trans_redundant": true,
  "avoid_corner_cutting": true
}
```

---

## 🎯 Algorithm Comparison

| Algorithm | Input             | Output | Speed         | Quality   | Optimal         |
| --------- | ----------------- | ------ | ------------- | --------- | --------------- |
| **A\***   | Grid, Start, Goal | Path   | ⚡⚡⚡ (fast) | High      | ✅ Optimal      |
| **PSO**   | Grid, Waypoints   | Path   | ⚡ (slow)     | Medium    | ❌ Approximate  |
| **APSO**  | Grid, Start, Goal | Path   | ⚡⚡ (medium) | High      | ✅ Often good   |
| **HAPSO** | Grid, Start, Goal | Path   | ⚡⚡ (medium) | Very High | ✅ Best of both |

**Hybrid Approach thì HAPSO:**

- A\* provides: Completeness, guaranteed path
- PSO provides: Path smoothing, optimization

---

## 💾 Key Features

### Pathfinding

- ✅ A\* Search (complete, optimal)
- ✅ PSO-based (population-based)
- ✅ APSO (Adaptive PSO with improvements)
- ✅ HAPSO (Hybrid A\* + PSO)

### Path Optimization

- ✅ Remove redundant points
- ✅ Remove transitive redundant
- ✅ Avoid corner cutting
- ✅ PSO-based smoothing

### Line Drawing

- ✅ Bresenham algorithm
- ✅ Incremental traversal (DDA)
- ✅ Parametric discretization
- ✅ Runs of Runs

### Visualization

- ✅ Pygame-based GUI (5 pages)
- ✅ Matplotlib charts (non-interactive Agg backend)
- ✅ Real-time metrics display
- ✅ Comparison dashboard (F5)

### Data Management

- ✅ Save/load maps (JSON)
- ✅ Save/load results (JSON)
- ✅ Timestamped storage
- ✅ Full path + metrics logging

---

## 🚀 Usage Guide

### F1: Map Editor

```
1: Add Obstacle
2: Remove Obstacle (Ecrease)
S: Set Start point
G: Set Goal point
L: Load saved map
C: Clear all
Enter: Save map
```

### F2: Pathfinding

```
A: A* algorithm
P: PSO algorithm
S: APSO algorithm
H: HAPSO algorithm
1: Toggle Remove Redundant
2: Toggle Remove Transitive Redundant
3: Toggle Avoid Corner Cutting
4: Toggle SIW (PSO)
5: Toggle SOBL (PSO)
Space: Run algorithm
Enter: Save result
```

### F3: Line Drawing

```
B: Bresenham
V: Fast Voxel (Incremental Traversal)
D: DDA Runs (Runs of Runs)
S: Copy Start from F1
G: Copy Goal from F1
C: Clear
Space: Run algorithm
```

### F4: Weight Compare

```
Input fields for: w_min, w_max, max_iterations
Space: Calculate and display comparison chart
```

### F5: Result Compare

```
R: Compare all 4 algorithms (A*, PSO, APSO, HAPSO)
Auto-run: Automatically runs on F5 key press
Display: 2x2 dashboard with 4 metrics
```

---

## 📦 Dependencies

```
pygame>=2.1.0           # GUI framework
numpy>=2.0.0            # Numeric computations
matplotlib>=3.10.0      # Chart plotting (Agg backend)
```

---

## 🔧 Configuration Editing

Để thay đổi:

- Window size: `config.py` → `WINDOW_WIDTH, WINDOW_HEIGHT`
- Grid size: `config.py` → `GRID_SIZE`
- PSO parameters: `app.py` → `_run_simulation()` method
- Inertia weights: `config.py` or `pso_improvement.py`

---

**Created: April 14, 2026**
**Project Type: Pathfinding Simulation & Visualization**
**Main Technology: Python + Pygame + PSO/A\* Algorithms**
