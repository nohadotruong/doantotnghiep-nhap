# HAPSO Claude Context

## Project

Pure Python path planning library for 2D grid maps.
Algorithms: A*, Dijkstra, APSO, HAPSO, RRT, RRT*, PRM.

Shared utilities: inertia weight strategies and path smoothing helpers.

Tech stack: Python 3.x, NumPy, Matplotlib, Pygame.

---

## Structure

```
hapso-draft-8/
├── config/
│   ├── __init__.py
│   ├── algo_config.py
│   └── ui_config.py
├── core/
│   ├── __init__.py
│   ├── metrics.py
│   ├── models.py
│   └── algorithms/
│       ├── __init__.py
│       ├── base_planner.py
│       ├── astar.py
│       ├── pso_optimizer.py
│       ├── apso.py
│       ├── hapso.py
│       ├── prm.py
│       ├── rrt.py
│       └── rrt_star.py
│   └── utils/
│       ├── __init__.py
│       ├── inertia_weight.py
│       └── path_smoother.py
├── map/
│   ├── __init__.py
│   ├── grid_map.py
│   ├── map_serializer.py
│   └── map_validator.py
├── data/
│   ├── maps/
│   │   ├── 2026-05-08_11-05-40/
│   │   ├── figure-1/
│   │   ├── figure-2-3-5/
│   │   └── ...
│   └── results/
│       └── (timestamped result folders)
├── reference_project/
│   ├── project_1/
│   └── project_2/
├── simulator/
│   └── README.md
├── map_editor.py
├── single-simulator.py
├── multi-simulator.py
├── weight_compare.py
├── min_clearance_astar_summary.md
├── structure.md
├── README.md
└── requirements.txt
```

---

## Rules

- Use start and goal.
- Use grid_map for map objects.
- Keep constants in config/algo_config.py.
- Shared collision helpers live in BasePlanner and are reused by PathSmoother.
- No try/except, raise, or hasattr().
- No docstrings or comments in production code.
- No wildcard imports.
- Public planners use find_path(start, goal).

---

## Import Direction

Allowed:

```
algorithms -> map, config
utils -> algorithms, map, config
map -> config
config -> nothing in project
```

---

## Workflows

- Run single simulator: python single-simulator.py
- Run multi simulator: python multi-simulator.py
- Run editor: python map_editor.py
- Run A\* simulator: python simulator/astar-simulator.py

---

## Notes

- **Fitness Functions**: APSO uses simple distance-based fitness `f = 1/(1+d)` per paper. HAPSO uses PSOptimizer with complex fitness (length + angle + clearance).
- **APSO PSO**: PSO logic integrated directly in APSO class (not shared with HAPSO via PSOptimizer).
- **Parameters**:
  - APSO: `use_tvac = False` (constant c1, c2)
  - HAPSO: `use_tvac = True` (time-varying c1, c2)
  - `OPTIMIZER_MAX_VELOCITY = 2.0` (fixed vmax per paper)
- Update CLAUDE.md when files/folders are added, removed, or renamed, or when workflows/import directions change.
