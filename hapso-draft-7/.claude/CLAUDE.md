# HAPSO — Claude Context

## Dự án là gì

Framework mô phỏng và so sánh thuật toán path planning trên grid 2D.
4 thuật toán: A*, PSO, APSO, HAPSO (Hybrid A* + Adaptive PSO).

**Tech stack**: Python 3.x · Pygame · NumPy · Matplotlib

---

## Cấu trúc thư mục

```
hapso-draft-6/
├── main.py                        # Entry point
├── simulation.py                  # Chạy đơn lẻ 1 thuật toán
├── comparison.py                  # So sánh nhiều thuật toán
├── map_editor.py                  # Standalone map editor
│
├── config/
│   ├── ui_config.py               # Window, colors, fonts, FPS, layout
│   └── algo_config.py             # Hyperparameters PSO, A*, HAPSO
│
├── core/
│   ├── models.py                  # PathResult, ComparisonMetrics
│   ├── metrics.py                 # compute_all_metrics()
│   └── algorithms/
│       ├── base_planner.py        # BasePlanner (ABC)
│       ├── astar.py
│       ├── pso_planner.py
│       ├── pso_optimizer.py
│       ├── apso.py
│       └── hapso.py
│
├── gui/
│   ├── app.py                     # Main Pygame loop
│   ├── event_handler.py
│   ├── renderer.py
│   └── pages/
│       ├── f1_editor.py           # Map Editor
│       ├── f2_simulation.py       # Simulation
│       └── f3_comparison.py       # Metrics Comparison
│
├── state/
│   └── app_state.py               # AppState singleton
│
├── map/
│   ├── grid_map.py
│   ├── map_serializer.py
│   └── map_validator.py
│
└── data/
    ├── maps/                      # Saved maps (by timestamp)
    └── results/                   # Simulation results (by timestamp)
```

---

## Kiến trúc quan trọng

**Config**: Mọi constant đều nằm trong `config/`. Không hardcode bất kỳ giá trị nào inline.

**Algorithms**: Tất cả kế thừa `BasePlanner`. Entry point duy nhất là `find_path(start, goal)`.

**State**: Mọi thay đổi map và result đi qua `AppState.instance()` — không đọc/ghi trực tiếp.

**GUI**: Rendering chỉ nằm trong `renderer.py` và `pages/`. Không vẽ Pygame trong algorithms.

**Import direction** (chỉ được import theo chiều này):

```
gui → core, state, map, config
core/algorithms → map, config
state → core, map
map → config
config → (không import gì trong project)
```

---

## Quy tắc

Đọc từng file trong `.claude/rules/` trước khi viết code:

- `.claude/rules/code-style.md` — naming, imports, type hints
- `.claude/rules/class-design.md` — class layout, method order, default params
- `.claude/rules/error-handling.md` — print format, không dùng try/except/raise
- `.claude/rules/project-structure.md` — one responsibility, no circular imports

---

## Hard constraints

- KHÔNG dùng `try/except`, `raise`, `hasattr()`.
- KHÔNG docstrings, KHÔNG comments.
- KHÔNG hardcode constant — dùng `config/`.
- KHÔNG truyền tham số khi khởi tạo class bên ngoài — mọi default nằm trong `__init__`.
- KHÔNG import `*`.
- KHÔNG vẽ Pygame trong `core/algorithms/`.
- KHÔNG sửa map/result trực tiếp — đi qua `AppState`.
- Dùng `start`/`goal`, không dùng `start`/`end`.
- Dùng `grid_map`, không dùng `grid`.

---

## Workflows thường dùng

**Thêm thuật toán mới** → đọc `.claude/skills/add-new-algorithm.md`

**Debug PSO** → đọc `.claude/skills/debug-pso.md`

**Benchmark** → đọc `.claude/skills/benchmark-algorithms.md`

**Slash commands có sẵn**: `/review` · `/fix` · `/refactor` · `/new-planner`

---

## Trạng thái dự án

Refactoring hoàn tất: 2026-04-27
Sẵn sàng phát triển feature mới.
