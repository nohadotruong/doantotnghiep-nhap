# Promblem solved

Dưới đây là phân tích vấn đề và đề xuất cấu trúc mới được tổ chức theo **Clean Architecture** với separation of concerns rõ ràng.---

## Vấn đề của cấu trúc cũ

Cấu trúc hiện tại có 3 vấn đề chính: `app.py` đang gánh **toàn bộ** logic (vẽ, xử lý sự kiện, chạy thuật toán, lưu file — gần 1000+ dòng), các file utility nằm lộn xộn cùng cấp với core algorithms, và không có ranh giới rõ ràng giữa các tầng.

---

## Cấu trúc mới — 5 package theo tầng trách nhiệm

**`gui/`** — Presentation layer, chỉ biết vẽ và nhận input. Tách `app.py` hiện tại thành 4 file nhỏ: `app.py` chỉ giữ main loop, `renderer.py` chứa toàn bộ các `draw_*` method, `event_handler.py` xử lý keyboard/mouse, `state.py` lưu trạng thái UI của từng page F1–F5. Thêm thư mục `pages/` với mỗi page F1–F5 là một class riêng.

**`algorithms/`** — Pure logic, zero dependency vào Pygame. Thêm `base_planner.py` là abstract base class với interface `find_path(start, goal) -> list`, tất cả 4 thuật toán đều implement. Giúp `comparison_runner.py` có thể gọi đồng nhất mà không cần `if/elif`.

**`optimization/`** — Gộp `path_optimization.py` + `pso_improvement.py` + `get_line_grid.py` vào đây. Đổi tên thành `path_smoother.py`, `inertia_weight.py`, `line_drawing.py` — tên rõ nghĩa hơn.

**`map/`** — Domain model thuần túy. Tách `grid_map.py` ra: giữ `grid_map.py` là model, tách save/load thành `map_serializer.py` và `result_serializer.py` (Single Responsibility). Thêm `map_validator.py` để validate start/goal trước khi chạy.

**`analytics/`** — Gộp `metrics.py` + `f4_weight_compare.py` + logic F5 vào đây. `chart_builder.py` đảm nhiệm toàn bộ matplotlib → pygame surface, `comparison_runner.py` chạy 4 thuật toán song song và trả về dict kết quả.

---

## Quy tắc dependency

```
gui  →  algorithms / optimization / map / analytics
algorithms  →  map (đọc grid)
optimization  →  (không phụ thuộc gì)
analytics  →  algorithms / map
map  →  (không phụ thuộc gì — domain thuần)
```

Chiều mũi tên chỉ đi **một chiều xuống dưới**. `algorithms` không bao giờ import từ `gui`, `map` không bao giờ import từ `analytics`. Khi cần thêm tính năng hay viết test, bạn chỉ cần quan tâm đúng một package.

Tôi sẽ làm một bảng mapping tương tác — click vào từng package để xem chi tiết từng class/function đi đâu.
Click vào từng tab để xem mapping chi tiết. Dưới đây là 4 điểm quan trọng nhất cần chú ý khi refactor:

**Logic trùng lặp cần gộp lại.** `remove_redundant_points` và `remove_transitive_redundant_points` hiện tồn tại ở cả `astar.py` lẫn `path_optimization.py` — đây là bug tiềm ẩn vì nếu sửa một chỗ bạn dễ quên chỗ kia. Gộp cả hai về `optimization/path_smoother.py`, xóa bản trong `astar.py`.

**`App` class cần được "xả tải" triệt để.** Hiện tại `App` có khoảng 40 instance variable (`f1_*`, `f2_*`, `f3_*`...) và hàng chục method. Mục tiêu sau refactor: `App.__init__` chỉ còn khởi tạo Pygame, tạo `AppState`, tạo `Renderer` và `EventHandler` — khoảng 20 dòng.

**`_bresenham_line` trong `app.py` là code thừa.** Đã có `get_line_grid_bresenham` trong `get_line_grid.py` làm đúng việc đó. Khi chuyển sang `optimization/line_drawing.py` thì `event_handler.py` chỉ cần gọi `LineDrawer.bresenham()`, xóa bản duplicate trong `app.py`.

**Thứ tự refactor an toàn nhất** là từ dưới lên: bắt đầu với `map/` (không dependency nào) → `optimization/` → `algorithms/` → `analytics/` → `gui/` cuối cùng. Mỗi bước test lại trước khi chuyển tầng tiếp theo.

map/grid_map.py
move
GridMap (class)
grid_map.py — giữ nguyên
→
GridMap
Giữ toàn bộ, chỉ xóa save/load ra
FREE, OBSTACLE, START, GOAL
→
Constants giữ trong class
is_obstacle, is_inside, set_start, set_goal
→
Giữ nguyên
set_obstacle, toggle_obstacle, get_obstacles
→
Giữ nguyên
to_dict, from_dict
→
Giữ trong GridMap (pure conversion)
map/map_serializer.py
split
GridMap.save_map()
grid_map.py
→
MapSerializer.save(grid_map, path)
Tách I/O ra khỏi domain model
GridMap.load_map()
grid_map.py
→
MapSerializer.load(path) → GridMap
GridMap không còn biết mình được lưu thế nào — đúng Single Responsibility
map/result_serializer.py
split
App.\_save_result()
app.py
→
ResultSerializer.save(result_dict, path)
(không có load)
app.py — F5 chỉ run lại
→
ResultSerializer.load(path) → dict
Thêm mới để F5 có thể load kết quả cũ
map/map_validator.py
new
(logic rải rác trong app.py)
check start/goal trước khi run
→
MapValidator.validate(grid_map) → bool, str
Trả về (is_valid, error_message)

algorithms/base_planner.py
new
(không tồn tại)
→
BasePlanner (ABC)
Abstract: find_path(start, goal) → list
Giúp comparison_runner.py gọi tất cả planner qua interface chung, không cần if/elif
algorithms/astar.py
move
Node (class)
astar.py
→
Node — giữ nguyên
AStar (class)
→
AStar(BasePlanner) — kế thừa base
find_path, \_heuristic, \_is_walkable
→
Giữ nguyên
remove_redundant_points, remove_transitive_redundant_points
→
Xóa khỏi đây → chuyển sang optimization/path_smoother.py
\_can_move_diagonal, \_get_cost, \_reconstruct_path
→
Giữ nguyên (private helpers)
algorithms/pso.py
move
PSOPlanner (class)
pso.py — chứa plan()
→
PSOPlanner(BasePlanner)
PSOptimizer (class)
pso.py — chứa optimize(path)
→
Giữ trong pso.py — dùng nội bộ bởi HAPSO
plan(), optimize()
→
find_path() wrap plan() để đồng nhất interface
algorithms/apso.py
move
APSO (class)
apso.py
→
APSO(BasePlanner)
find_path, \_euclidean_distance, \_fitness
→
Giữ nguyên
siw, sobl attributes
import từ pso_improvement.py
→
Import từ optimization/inertia_weight.py
algorithms/hapso.py
move
HAPSO (class)
hapso.py
→
HAPSO(BasePlanner)
find_path() — gọi AStar rồi PSOptimizer
→
Giữ nguyên logic

optimization/path_smoother.py
rename
optimize_path()
path_optimization.py
→
PathSmoother.smooth(path, \*\*options) → list
remove_redundant_points()
path_optimization.py + astar.py (trùng lặp!)
→
PathSmoother.\_remove_collinear(path)
Gộp 2 bản trùng thành 1
remove_transitive_redundant_points()
path_optimization.py + astar.py (trùng lặp!)
→
PathSmoother.\_remove_transitive(path)
Gộp 2 bản trùng thành 1
Hiện tại logic này tồn tại ở 2 nơi (astar.py và path_optimization.py) — gộp về 1 class duy nhất
optimization/inertia_weight.py
rename
InertiaWeight (ABC)
pso_improvement.py
→
InertiaWeight (ABC) — giữ nguyên
LDIW, NDIW, AIW, SIW, SOBL
pso_improvement.py
→
Giữ nguyên 5 class, đổi tên file thôi
optimization/line_drawing.py
rename
get_line_grid_bresenham()
get_line_grid.py
→
LineDrawer.bresenham(start, end)
get_line_grid_incremental_traversal()
get_line_grid.py
→
LineDrawer.incremental(start, end)
get_line_grid_parametric_discretization()
get_line_grid.py
→
LineDrawer.parametric(start, end)
get_line_grid_runs_of_runs()
get_line_grid.py
→
LineDrawer.runs_of_runs(start, end)
compare_methods()
get_line_grid.py
→
LineDrawer.compare_all(start, end) → dict
Bọc 4 free functions thành static methods trong 1 class — dễ import, dễ test hơn

analytics/metrics.py
move
PathMetrics (class)
metrics.py — giữ nguyên hoàn toàn
→
PathMetrics — giữ nguyên
calculate_metrics, calculate_path_length
→
Giữ nguyên
calculate_path_points, calculate_turning_amplitude
→
Giữ nguyên
format_metrics, \_calculate_angle_difference
→
Giữ nguyên
analytics/chart_builder.py
rename
plot_inertia_weights()
f4_weight_compare.py — trả về plt object
→
ChartBuilder.build_weight_chart(w_min, w_max, tmax) → Surface
App.\_update_f5_chart()
app.py — tạo 2x2 matplotlib chart
→
ChartBuilder.build_comparison_chart(results) → Surface
Gộp 2 nơi tạo chart (app.py + f4_weight_compare.py) vào 1 class. App chỉ nhận Surface về render.
analytics/comparison_runner.py
split
App.\_run_f5_compare()
app.py — chạy 4 algo, collect kết quả
→
ComparisonRunner.run_all(grid_map) → dict
App.\_run_simulation()
app.py — chạy 1 algo cụ thể
→
ComparisonRunner.run_one(planner, grid_map) → dict
Dùng BasePlanner interface

gui/app.py
split
App.**init**, run()
app.py — giữ lại
→
App — chỉ còn main loop + khởi tạo
App.handle*events()
app.py
→
→ gui/event_handler.py
App.draw(), draw_navigation(), draw_content_area()
→
→ gui/renderer.py
App.draw_f1*_, draw*f2*_, draw*f3*_, draw*f4*_, draw*f5*_
→
→ gui/pages/f1*editor.py … f5_compare.py
gui/renderer.py
split
draw_navigation()
app.py
→
Renderer.draw_nav(screen, current_page)
draw_content_area()
app.py — dispatch sang F1-F5
→
Renderer.draw(screen, state) — gọi page tương ứng
draw_f1_grid_area(), draw_f2_grid_area(), draw_f3_grid_area()
→
GridRenderer.draw(screen, grid_map, path, highlights)
gui/event_handler.py
split
App.\_handle_f1_mouse_event()
app.py
→
EventHandler.on_f1_mouse(event, state)
App.\_handle_f3_mouse_event()
app.py
→
EventHandler.on_f3_mouse(event, state)
App.\_pixel_to_grid()
app.py
→
EventHandler.\_pixel_to_grid() — private helper
App.\_bresenham_line(), App.\_paint_line()
app.py — dùng trong F1 paint
→
Xóa — dùng LineDrawer từ optimization/
gui/state.py
split
Tất cả f1*_, f2*\*, f3*\_, f4\_\_, f5\_\* attributes
App class — ~40 instance variables
→
AppState dataclass
F1State, F2State, F3State, F4State, F5State
Tách state ra dataclass riêng → App.**init** gọn lại, dễ reset từng page độc lập
gui/pages/ (5 files)
split
draw_f1_menu, draw_f1_info_panel, draw_f1_grid_area
→
pages/f1_editor.py — F1EditorPage
draw_f2_menu, draw_f2_info_panel, draw_f2_grid_area
→
pages/f2_pathfinding.py — F2PathfindingPage
draw_f3_menu, draw_f3_info_panel, draw_f3_grid_area
→
pages/f3_linegrid.py — F3LineGridPage
draw_f4_menu, draw_f4_info_panel, draw_f4_compare_panel
→
pages/f4_weight.py — F4WeightPage
draw_f5_menu, draw_f5_info_panel, draw_f5_compare_panel
→
pages/f5_compare.py — F5ComparePage
Xóa khỏi app.py (đã chuyển hết)
rename
\_calculate_layout()
app.py
→
config.py — hằng số layout tính sẵn
\_save_map(), \_open_load_map_ui(), \_load_selected_map()
→
pages/f1_editor.py + map/map_serializer.py
\_truncate_status()
app.py — utility nhỏ
→
gui/utils.py — truncate_text()
\_init_f4_state()
→
F4State.**init**() trong gui/state.py
