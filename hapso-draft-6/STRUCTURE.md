# HAPSO Project Structure - Refactoring Complete (2026-04-27)

## Overview

**HAPSO** (Hybrid Adaptive Particle Swarm Optimization) - Pathfinding simulation framework implementing A\*, PSO, APSO, HAPSO algorithms with GUI.

**Refactoring Status**: ✅ **COMPLETE (6/6 Steps)**

**Completed Steps**:

1. ✅ **Bước 1**: Xóa & dọn dẹp (Deleted config.py, algorithms/, analytics/)
2. ✅ **Bước 2**: Update main.py (New architecture with AppState init)
3. ✅ **Bước 3**: Connect GUI to AppState (gui/event_handler.py, gui/app.py refactored)
4. ✅ **Bước 4**: Connect renderer to AppState (gui/renderer.py refactored, F4-F5 pages removed)
5. ✅ **Bước 5**: Import audit (Zero deprecated imports in active code)
6. ✅ **Bước 6**: Smoke test (All imports chain successfully, ready to run)

**Architecture Completed**:

- ✅ Config separated into UI & algorithm layers (config/)
- ✅ Core models created (PathResult, ComparisonMetrics in core/models.py)
- ✅ Algorithms refactored with type hints & config-driven parameters (core/algorithms/)
- ✅ AppState singleton for state management (state/app_state.py)
- ✅ GUI simplified from 5 pages to 3 pages (F1, F2, F3 only)
- ✅ Legacy code archived in `/old` folder
- ✅ No active code imports from deprecated modules

---

## Directory Structure

### 📦 Root Level

```
hapso-draft-5/
├── main.py                      ✅ REFACTORED - New architecture
├── requirements.txt
├── STRUCTURE.md                 (This file - UPDATED 2026-04-27)
├── code_rule.md
│
├── test_*.py                    (Test files - keep for reference, old imports OK)
├── playground_dont_delete.py    (Development playground)
│
├── [REFACTORED PRODUCTION CODE] ✅
├── config/                      ✨ Configuration layer (UI & algorithms)
├── core/                        ✨ Core algorithms & models with type hints
├── state/                       ✨ Global state (AppState singleton)
├── gui/                         ✅ REFACTORED - Connected to AppState
├── map/                         ✓ Map management & serialization
├── optimization/                ✓ Algorithm utilities
├── data/                        ✓ Maps & results storage
│
└── old/                         📁 ARCHIVED - Legacy code backup
```

**Deprecated (Removed)**:

- ❌ `config.py` - Split into config/ui_config.py + config/algo_config.py
- ❌ `algorithms/` - Moved to old/algorithms/ or refactored to core/algorithms/
- ❌ `analytics/` - Moved to old/analytics/ (functionality moved to AppState/models)

---

## 🟢 NEW REFACTORED CODE

### 1. `config/` - Configuration Layer

**Separation of Concerns**: UI config ≠ Algorithm config

```
config/
├── __init__.py                  (Re-exports both configs)
├── ui_config.py                 (Window, colors, layout, fonts, FPS, menus)
└── algo_config.py               (All algorithm hyperparameters)
```

#### `config/ui_config.py` - UI Settings

- Window dimensions, colors, fonts
- Grid settings (cell size, size)
- Layout ratios (navigation, content left/right)
- FPS, menu items, fonts

#### `config/algo_config.py` - Algorithm Tuning

- A\* parameters
- PSO parameters (waypoints, particles, iterations, inertia, coefficients)
- Optimizer parameters (for APSO/HAPSO segment optimization)
- Robot parameters (ROBOT_RADIUS, OBSTACLE_RADIUS, SAFE_DIST)

### 2. `core/` - Core Algorithms & Models

```
core/
├── __init__.py
├── models.py                    ✨ NEW - Data models
│
└── algorithms/                  ✨ NEW - Refactored algorithms
    ├── __init__.py
    ├── base_planner.py          (Abstract Planner class)
    ├── astar.py                 (A* algorithm)
    ├── pso_planner.py           (PSO waypoint optimization)
    ├── pso_optimizer.py         (PSOptimizer - segment refinement)
    ├── apso.py                  (APSO = A* + segment optimization)
    └── hapso.py                 (HAPSO = A* + segment optimization with TVAC)
```

#### `core/models.py` - Data Models

Three main dataclasses:

1. **PathResult** - Standard result for single algorithm run

   ```python
   @dataclass
   class PathResult:
       algorithm: str              # "A*", "PSO", "APSO", "HAPSO"
       path: Optional[list]        # Waypoints or None if failed
       metrics: dict               # Path metrics (length, turns, etc.)
       execution_time: float       # Runtime in seconds
       success: bool               # Whether path was found
       error_message: str          # Error details if failed
   ```

2. **SimulationResult** - Wrapper for single run + timestamp

   ```python
   @dataclass
   class SimulationResult:
       algorithm: str
       path_result: PathResult
       timestamp: str
   ```

3. **ComparisonMetrics** - Container for multiple algorithm results
   ```python
   @dataclass
   class ComparisonMetrics:
       algorithm_results: dict[str, PathResult]  # Multiple algorithms
       get_result(algo_name) -> PathResult       # Lookup by name
       get_algorithms() -> list[str]             # All algorithm names
       add_result(name, result) -> None          # Add result
   ```

#### `core/algorithms/` - Algorithm Implementations

**Key Refactoring Changes**:

- ✅ **Type Hints**: All functions use modern Python 3.10+ type syntax
- ✅ **Config-Driven**: Constructor takes ONLY boolean flags, loads numbers from `config.algo_config`
- ✅ **Docstrings**: Comprehensive documentation for all classes/methods
- ✅ **Standard Return**: All return `Optional[list[tuple[int, int]]]` (path or None)

##### `base_planner.py` - Abstract Base Class

- `find_path(start, goal) -> Optional[list[tuple[int, int]]]` (abstract)
- Collision detection methods
- Distance calculation methods (vector_projection or algebraic)
- Imports from `config.algo_config`

##### `astar.py` - A\* Pathfinding

- 8-directional movement
- Euclidean heuristic
- Diagonal validation (prevents corner-cutting)
- Optional path smoothing via PathSmoother

##### `pso_planner.py` - PSO Algorithm

- Catmull-Rom spline waypoints
- Arc-length resampling
- Collision repair (BFS detours)
- Parameters: N_WAYPOINTS, N_PARTICLES, MAX_ITERATIONS, INERTIA_WEIGHT, COGNITIVE/SOCIAL_COEFFICIENT, etc.
- Boolean constructor: `use_siw`, `use_sobl` (all else from config)

##### `pso_optimizer.py` - PSOptimizer Class

- PSO-based segment optimizer (used by APSO/HAPSO)
- Optimizes individual segments between A\* waypoints
- Returns single best waypoint per segment
- Parameters: N_PARTICLES, MAX_ITERATIONS, SEARCH_MARGIN, etc.
- Boolean constructor: `use_tvac` (TVAC = Time-Varying Acceleration Coefficients)

##### `apso.py` - Adaptive PSO

- Pipeline: A\* → remove collinear points → optimize each segment → return path
- Fixed A\* policy: `remove_redundant=True, remove_transitive=True, avoid_corner_cutting=False`
- Segment optimizer: `use_tvac=False` (fixed PSO strategy)
- No constructor parameters (creates internal AStar + PSOptimizer)

##### `hapso.py` - Hybrid APSO (with TVAC)

- Similar to APSO but segment optimizer has `use_tvac=True`
- TVAC: c1 decreases (exploitation), c2 increases (exploration) over iterations
- More adaptive exploration-exploitation balance
- No constructor parameters (creates internal AStar + PSOptimizer)

### 3. `state/` - Global Application State

```
state/
├── __init__.py                  (Exports public API)
└── app_state.py                 ✨ NEW - AppState singleton
```

#### `state/app_state.py` - AppState Singleton

Single source of truth for entire app:

```python
@dataclass
class AppState:
    current_map: Optional[GridMap]              # Currently loaded map
    current_page: str                           # "F1", "F2", "F3"
    f2_results: dict[str, PathResult]           # F2 simulation results
    f3_comparison_results: Optional[ComparisonMetrics]  # F3 comparison

    # Helper methods
    add_f2_result(algorithm_name, result)
    get_f2_result(algorithm_name) -> PathResult
    has_f2_results() -> bool
    set_f3_comparison(comparison)
    get_f3_comparison() -> ComparisonMetrics
    has_f3_comparison() -> bool
    reset()
```

**Singleton Pattern**:

- `get_app_state()` - Get global instance
- `reset_app_state()` - Reset to defaults

---

## 🔄 UPDATED CODE

### 4. `gui/` - GUI with 3 Pages (F1, F2, F3 only)

**Status**: ✅ **REFACTORED & CONNECTED TO APPSTATE**

**Simplified from 5 pages (F1-F5) to 3 pages (F1-F3)**

```
gui/
├── __init__.py
├── app.py                       ✅ REFACTORED - Connected to AppState
│                                   - Imports from core/, config.ui_config, state.app_state
│                                   - _run_all_algorithms() saves to AppState.f3_comparison_results
│                                   - _run_simulation() saves to AppState.f2_results
│                                   - Auto-switch to F3 when running "All"
│
├── event_handler.py             ✅ REFACTORED - Connected to AppState
│                                   - Imports from config.ui_config, state.app_state
│                                   - Dispatches events to update AppState
│
├── renderer.py                  ✅ REFACTORED - Draws from AppState
│                                   - Imports from config.ui_config, state.app_state
│                                   - Loads only 3 pages (F1, F2, F3)
│                                   - Draws grid based on AppState.current_map
│
└── pages/                       ✅ NEW PAGES - AppState-aware
    ├── __init__.py
    ├── f1_editor.py             (Map design & editing)
    ├── f2_simulation.py         (Single algorithm pathfinding)
    └── f3_comparison.py         (Multi-algorithm comparison)
```

#### Key Changes in app.py

**Before (Old)**:

- Imported algorithms from `algorithms/`, analytics from `analytics/`
- Old imports: `from config import ...`
- Results stored in `self.f2_result` dict, `self.f3_results` list
- PageNo F4/F5 logic present

**After (Refactored)**:

- Imports from `core/algorithms/`, `config.ui_config`, `state.app_state`
- Imports models: `PathResult`, `ComparisonMetrics`
- Results stored in `AppState.f2_results`, `AppState.f3_comparison_results`
- Only F1, F2, F3 logic; F4, F5 removed
- Methods `_run_f5_compare()`, `_update_f5_chart()`, `_update_f4_chart()` commented out

**New Algorithm Call Pattern**:

```python
# Import new way
from core.algorithms.pso_planner import PSOPlanner
from core.models import PathResult
from state.app_state import get_app_state

# Run algorithm
pso = PSOPlanner(self.grid_map, use_siw=True, use_sobl=False)
path = pso.find_path(self.grid_map.start, self.grid_map.goal)

# Save to AppState
result = PathResult(
    algorithm="PSO",
    path=path,
    metrics={"waypoints": len(path) if path else 0},
    execution_time=execution_time,
    success=path is not None,
    error_message="" if path else "No path found"
)
state = get_app_state()
state.add_f2_result("PSO", result)
```

#### F1: Editor Page

- Draw/clear obstacles
- Set start/goal points
- Load/save maps
- Display map info (obstacles count, start/goal)
- Reads/writes to `AppState.current_map`

#### F2: Simulation Page

- Select algorithm (A\*, PSO, APSO, HAPSO)
- Run single pathfinding
- View execution time & path length
- Display metrics
- Saves results to `AppState.f2_results`

#### F3: Comparison Page

- Run comparison across all 4 algorithms
- View results table (Time, Path Length, Status)
- Display comparison chart
- Results stored in `AppState.f3_comparison_results`
- Auto-triggered when user selects "Run All" in F2

### 5. `map/` - Map Management

```
map/
├── __init__.py
├── grid_map.py                  (GridMap class - collision detection, obstacles)
├── map_serializer.py            (Save/load maps)
├── map_validator.py             (Validate map data)
└── result_serializer.py         (Save/load results)
```

### 6. `optimization/` - Algorithm Utilities

```
optimization/
├── __init__.py
├── path_smoother.py             (Collinear point removal, smoothing)
├── inertia_weight.py            (SIW, SOBL strategies)
├── line_drawing.py              (Bresenham's algorithm)
└── adaptive_coefficient.py      (Coefficient adaptation)
```

### 7. `data/` - Map & Result Storage

```
data/
├── maps/                        (Saved maps by timestamp)
│   ├── 2026-04-13_15-54-37/
│   ├── 2026-04-19_09-31-58/
│   ├── 2026-04-19_10-39-26/
│   ├── 2026-04-21_09-42-59/
│   └── 2026-04-23_19-53-07/
│
└── results/                     (Simulation results by timestamp)
    ├── 2026-04-13_20-36-16/
    ├── 2026-04-15_09-31-44/
    ├── 2026-04-19_10-50-45/
    └── 2026-04-24_10-37-11/
```

---

## 🔴 DEPRECATED / OLD CODE

### 8. `old/` - Legacy Code Archive

Complete backup of old implementation before refactoring.

```
old/
├── __init__.py
│
├── algorithms/                  (Old algorithm implementations)
│   ├── __init__.py
│   ├── base_planner.py          (Old - now in core/algorithms/base_planner.py)
│   ├── astar.py                 (Old - now in core/algorithms/astar.py)
│   ├── pso.py                   (Old - split into pso_planner.py + pso_optimizer.py)
│   ├── apso.py                  (Old - now in core/algorithms/apso.py)
│   └── hapso.py                 (Old - now in core/algorithms/hapso.py)
│
├── analytics/                   (Old analysis utilities)
│   ├── __init__.py
│   ├── chart_builder.py         (Old chart generation)
│   ├── comparison_runner.py     (Old comparison logic)
│   └── metrics.py               (Old metrics calculation)
│
└── gui/                         (Old GUI pages)
    ├── __init__.py
    └── pages/
        ├── __init__.py
        ├── f1_editor.py         (Old - now in gui/pages/f1_editor.py)
        ├── f2_pathfinding.py    (Old - now in gui/pages/f2_simulation.py)
        ├── f3_linegrid.py       (Old - deprecated, merged into F3)
        ├── f4_weight.py         (Old - deprecated, merged into F3)
        └── f5_compare.py        (Old - now in gui/pages/f3_comparison.py)
```

**When to Use Old Code**:

- Reference implementation for debugging
- Fallback if new code has issues
- Understanding original algorithm versions
- Comparing with new refactored versions

---

## ⚠️ FILES TO CLEANUP / MIGRATE

These can be moved to `/old` or removed:

```
❌ config.py                     (Use config/ folder instead)
❌ algorithms/                   (Empty - old code moved to old/algorithms/)
❌ analytics/                    (Empty - old code moved to old/analytics/)
```

---

## ✅ REFACTORING COMPLETION SUMMARY (Bước 1-6)

### Bước 1: Xóa & Dọn Dẹp

- ✅ Deleted deprecated `config.py`
- ✅ Deleted empty `algorithms/` folder (moved to old/algorithms/)
- ✅ Deleted empty `analytics/` folder (moved to old/analytics/)
- ✅ Fixed import in `gui/renderer.py` from `config` → `config.ui_config`

### Bước 2: Update main.py

- ✅ Refactored to use new architecture
- ✅ AppState singleton initialized before GUI startup
- ✅ Imports: `config.ui_config`, `state.app_state`, `gui.app`
- ✅ No imports from deprecated modules

### Bước 3: Connect gui/event_handler.py & gui/app.py

- ✅ Updated event_handler.py imports: `config` → `config.ui_config`
- ✅ Added AppState import: `from state.app_state import get_app_state`
- ✅ Updated app.py imports to core modules
- ✅ Refactored `_run_all_algorithms()`:
  - Saves to `AppState.f3_comparison_results` as `ComparisonMetrics`
  - Auto-switches to F3 page after completion
- ✅ Refactored `_run_simulation()`:
  - Saves to `AppState.f2_results` as `PathResult` objects
  - Fixed algorithm call signatures (e.g., `pso.find_path(start, goal)`)
- ✅ Commented out deprecated methods: `_run_f5_compare()`, `_update_f5_chart()`, `_update_f4_chart()`

### Bước 4: Connect gui/renderer.py

- ✅ Removed old pages: F3LineGridPage, F4WeightPage, F5ComparePage
- ✅ Added new pages: F1EditorPage, F2SimulationPage, F3ComparisonPage
- ✅ Updated page loading to import from `gui.pages`
- ✅ Simplified draw logic: only F1, F2, F3 pages rendered

### Bước 5: Import Audit

- ✅ Scanned entire codebase for deprecated imports
- ✅ **Result**: Zero deprecated imports in active code
- ✅ Deprecated imports only found in:
  - Test files (test\_\*.py) - acceptable per constraints
  - Documentation (STRUCTURE.md, code_rule.md) - examples only
  - old/ folder - archived code

### Bước 6: Smoke Test

- ✅ All imports chain successfully
- ✅ No syntax errors in any module
- ✅ No runtime import errors
- ✅ Fixed: MAP_DIR, RESULTS_DIR import (moved to config.ui_config)
- ✅ App ready to run!

---

## 🚀 Next Steps / Enhancement Ideas

### Immediate (Can do now)

- [ ] GUI test: Start app → F1 draw map → F2 run algorithm → check AppState updates
- [ ] Visual test: Verify F3 shows comparison results when running "All"
- [ ] Test persistence: Save/load maps and verify state preserved

### Medium Priority (Future)

- [ ] Add unit tests for refactored algorithms
- [ ] Performance benchmarking (old vs new refactored code)
- [ ] Migration guide from old to new code
- [ ] Optimize grid drawing (current implementation acceptable but can cache)
- [ ] Add statistics/analytics dashboard (currently F5 deprecated)

### Low Priority (Nice-to-have)

- [ ] Dark theme GUI option
- [ ] Algorithm animation/step-through mode
- [ ] Export results to CSV/JSON
- [ ] Real-time algorithm comparison (run multiple simultaneously)
- [ ] 3D visualization of pathfinding

---

## 🔍 Code Migration Reference (Updated for Completed Refactoring)

### Import Migration

```python
# OLD (DEPRECATED) ❌
from config import GRID_SIZE, PSO_N_PARTICLES
# Result: ImportError - config.py was deleted

# NEW (CORRECT) ✅
from config.ui_config import GRID_SIZE
from config.algo_config import PSO_N_PARTICLES
```

```python
# OLD (DEPRECATED) ❌
from algorithms.pso import PSOPlanner
planner = PSOPlanner(grid_map, n_particles=30, max_iterations=100)
# Result: ModuleNotFoundError - algorithms/ folder removed

# NEW (CORRECT) ✅
from core.algorithms.pso_planner import PSOPlanner
planner = PSOPlanner(grid_map, use_siw=True, use_sobl=False)
# All numeric params loaded from config.algo_config automatically
```

```python
# OLD (DEPRECATED) ❌
from analytics.metrics import PathMetrics
metrics = PathMetrics.calculate_metrics(path, grid_map, time)
# Result: ModuleNotFoundError - analytics/ folder removed

# NEW (CORRECT) ✅
from core.models import PathResult
result = PathResult(
    algorithm="A*",
    path=path,
    metrics={"waypoints": len(path)},
    execution_time=time,
    success=True,
    error_message=""
)
```

### State Management

```python
# OLD (DEPRECATED) ❌
# State scattered across app.py instance variables
class App:
    def __init__(self):
        self.f2_result = {}
        self.f3_results = []
        # Inconsistent state management

# NEW (CORRECT) ✅
from state.app_state import get_app_state
from core.models import PathResult

state = get_app_state()  # Singleton

# Add F2 simulation result
result = PathResult(...)
state.add_f2_result("PSO", result)

# Get F3 comparison results
comparison = state.get_f3_comparison()
for algo_name, result in comparison.algorithm_results.items():
    print(f"{algo_name}: {result.execution_time}s")
```

---

## 📊 Project Summary

| Layer      | Status      | Location                     | Purpose                          |
| ---------- | ----------- | ---------------------------- | -------------------------------- |
| **Config** | ✅ Done     | `config/ui_config.py`        | UI parameters                    |
| **Config** | ✅ Done     | `config/algo_config.py`      | Algorithm tuning constants       |
| **Core**   | ✅ Done     | `core/algorithms/`           | Type-hinted algorithm impl       |
| **Models** | ✅ Done     | `core/models.py`             | PathResult, ComparisonMetrics    |
| **State**  | ✅ Done     | `state/app_state.py`         | AppState singleton               |
| **GUI**    | ✅ Done     | `gui/app.py`                 | Main window + event loop         |
| **GUI**    | ✅ Done     | `gui/event_handler.py`       | Input handling + AppState update |
| **GUI**    | ✅ Done     | `gui/renderer.py`            | Drawing from AppState            |
| **Pages**  | ✅ Done     | `gui/pages/f1_editor.py`     | F1: Map editing                  |
| **Pages**  | ✅ Done     | `gui/pages/f2_simulation.py` | F2: Single algorithm run         |
| **Pages**  | ✅ Done     | `gui/pages/f3_comparison.py` | F3: Multi-algorithm compare      |
| **Map**    | ✅ Done     | `map/`                       | Grid & serialization             |
| **Utils**  | ✅ Done     | `optimization/`              | Algorithm utilities              |
| **Data**   | ✅ Done     | `data/`                      | Maps & results storage           |
| **Legacy** | ✅ Archived | `old/`                       | Old implementation               |

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer (gui/)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Pages (F1: Editor | F2: Simulation | F3: Compare)   │
│  │  event_handler.py → EventHandler (dispatches input)  │
│  │  renderer.py → Renderer (draws from AppState)        │
│  └──────────────────────────────────────────────────┘   │
│                           ↕                              │
├─────────────────────────────────────────────────────────┤
│              State Management (state/)                   │
│         AppState Singleton (get_app_state())            │
│  - current_map: GridMap                                  │
│  - f2_results: dict[str, PathResult]                     │
│  - f3_comparison_results: ComparisonMetrics              │
├─────────────────────────────────────────────────────────┤
│                   Core Layer (core/)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Algorithms (A*, PSO, APSO, HAPSO)               │   │
│  │  - All with type hints                           │   │
│  │  - Config-driven parameters                      │   │
│  │  - Standard return type: Optional[list[tuple]]  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Models (PathResult, ComparisonMetrics)          │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│              Configuration (config/)                     │
│  - ui_config.py (window, colors, layout)                │
│  - algo_config.py (hyperparameters, constants)          │
├─────────────────────────────────────────────────────────┤
│               Utilities (map/, optimization/)            │
│  - GridMap, MapSerializer, ResultSerializer             │
│  - PathSmoother, LineDrawing, InertiaWeight             │
├─────────────────────────────────────────────────────────┤
│                 Legacy Archive (old/)                    │
│         Old implementation for reference                │
└─────────────────────────────────────────────────────────┘
```

---

**Last Updated**: 2026-04-27  
**Refactoring Status**: ✅ **COMPLETE - All 6 Steps Done**
**Ready for**: GUI Testing & Feature Validation
**Next Action**: Run app with `python main.py`

**Classes**: `PSOPlanner(Planner)`, `PSOptimizer`

**PSOPlanner Class** (Main PSO Implementation):

**Constructor Parameters**:

- `n_waypoints`: Number of intermediate waypoints (default 12)
- `n_particles`: Number of particles in swarm (default 100)
- `w, c1, c2`: PSO cognitive/social coefficients
- `max_iter`: Maximum iterations (default 200)
- `use_siw`: Enable Stochastic Inertia Weight
- `use_sobl`: Enable Self-Opposite Based Learning
- `max_speed`: Maximum velocity magnitude (default 12.0)
- `smooth_alpha`: Path smoothing factor (default 0.12)
- `patience`: Early stopping threshold

**Key Methods**:

- `_init_spline_particle()`: Initializes particle using Catmull-Rom spline interpolation
  - Creates control points from start to goal with random perturbation
  - Applies Catmull-Rom curve fitting for smooth initial paths
- `_catmull_rom_chain(ctrl, samples_per_seg)`: Generates smooth curve through control points
  - Uses Catmull-Rom curve formula for interpolation
  - Produces dense point sampling between control points

- `_resample_by_arclength(path, n)`: Resamples path to have uniform arc-length distribution
  - Calculates cumulative arc length
  - Redistributes n points evenly along the path

- `_smooth_path(path, alpha, rounds)`: Applies iterative smoothing filter
  - Moves internal points toward midpoint between neighbors
  - Preserves start/goal endpoints

- `_repair_continuous(path)`: Clamps path coordinates to valid grid bounds

- `_repair_path_list(path, max_attempts)`: Repairs collision-free path constraints
  - Identifies segments with collisions
  - Inserts midpoints or uses BFS local pathfinding to bypass obstacles
  - Iterates until path is collision-free or max attempts exceeded

- `_cost(path)`: Comprehensive path quality evaluation
  - **Length Component** (0.1 weight): Normalized total path distance
  - **Angle Component** (0.1 weight): Sum of turning angles normalized
  - **Clearance Component** (0.1 weight): Distance to obstacles
  - **Collision Component** (0.7 weight): Exponential penalty for collisions
  - **Combined Score**: Weighted sum of all components

- `_run_pso()`: Main PSO optimization loop
  - Initializes particles with spline-based random paths
  - Updates velocities: v = w*v + c1*r1*(pbest-pos) + c2*r2\*(gbest-pos)
  - Applies velocity clamping to prevent unbounded motion
  - Tracks personal best (pbest) and global best (gbest) positions
  - Implements early stopping on fitness plateau

**PSOptimizer Class**:

- Wrapper class providing `optimize(keypoints)` method
- Optimizes path connecting key waypoints from A\* using PSO particles

---

### `apso.py` - Adaptive PSO (Hybrid A\* + PSO)

**Class**: `APSO(Planner)`

**Purpose**: Combines A\* initial path with PSO optimization

**Algorithm Flow**:

1. Runs A\* with path smoothing to get initial path
2. Extracts key nodes (collinear point removal)
3. Uses PSO to optimize the path connecting these key nodes

**Key Methods**:

- `find_path(start, goal)`: Main APSO algorithm
  - Returns A\* path if no optimization possible
  - Falls back to A\* if PSO optimization fails

**Key Attributes**:

- `astar`: A\* instance for initial path generation
- `optimizer`: PSO instance for path optimization

---

### `hapso.py` - Hybrid Adaptive PSO (Advanced A\* + PSO)

**Class**: `HAPSO(Planner)`

**Purpose**: Advanced hybrid combining A\* with adaptive PSO using Time-Varying Acceleration Coefficients (TVAC)

**Key Parameters** (beyond APSO):

- `use_tvac`: Enable Time-Varying Acceleration Coefficients
- `c1_init, c1_final`: Initial and final cognitive coefficients
- `c2_init, c2_final`: Initial and final social coefficients

**Algorithm Enhancement**:

- PSO coefficients adapt during iterations (c1 decreases, c2 increases)
- Encourages exploration early, exploitation late
- Uses `avoid_corner_cutting=False` for more flexible paths

**Key Methods**:

- `find_path(start, goal)`: Main HAPSO algorithm (similar to APSO but with adaptive coefficients)

---

## Map Module (`map/`)

### `grid_map.py` - Grid Map Data Structure

**Class**: `GridMap`

**Cell Values**:

- `FREE = 0`: Walkable cell
- `OBSTACLE = 1`: Obstacle cell
- `START = 2`: Start position
- `GOAL = 3`: Goal position

**Key Methods**:

- `clear_map()`: Resets all cells to FREE, clears start/goal
- `from_dict(data)`: Static method to deserialize from dict
- `to_dict()`: Serializes to dict (width, height, grid, start, goal)
- `get_obstacle_count()`: Returns number of obstacles
- `get_obstacles()`: Returns list of obstacle coordinates
- `get_obstacles_as_centers()`: Returns numpy array of obstacle centers (x+0.5, y+0.5)
- `is_inside(x, y)`: Checks if coordinates are within grid bounds
- `is_obstacle(x, y)`: Checks if cell is obstacle
- `set_start(x, y)`: Sets start position, updates grid
- `set_goal(x, y)`: Sets goal position, updates grid
- `set_obstacle(x, y, value)`: Adds/removes obstacle
- `toggle_obstacle(x, y)`: Toggles obstacle at position

**Key Attributes**:

- `width, height`: Grid dimensions
- `grid`: 2D list of cell values
- `start, goal`: Tuple coordinates

---

### `map_serializer.py` - Map Load/Save

**Class**: `MapSerializer`

**Key Methods**:

- `load(path)`: Loads map from JSON file, returns GridMap object
- `save(grid_map, map_dir, screenshot_func)`: Saves map to JSON + PNG screenshot
  - Creates timestamp-based directory structure
  - Generates visual preview of map
  - Returns (json_path, image_path) tuple

- `_default_screenshot(grid_map, map_path)`: Generates PIL-based preview image
  - Renders obstacles (black), start (green), goal (red), free (white)
  - 30px cell size with grid lines

---

### `map_validator.py` - Map Validation

**Class**: `MapValidator`

**Key Methods**:

- `validate(grid_map)`: Checks map validity
  - Returns (bool, str) tuple with status and message
  - Validates: start exists, goal exists, start is not obstacle, goal is not obstacle

---

### `result_serializer.py` - Results Load/Save

**Class**: `ResultSerializer`

**Key Methods**:

- `load(path)`: Loads result JSON
- `save(result_data, results_dir)`: Saves result data to JSON with timestamp directory

---

## Analytics Module (`analytics/`)

### `metrics.py` - Path Quality Metrics

**Class**: `PathMetrics`

**Constants**:

- `V_M = 1.0`: Base movement velocity
- `T_P = 0.2`: Time per waypoint decision
- `V_I = π`: Angular velocity (radians/unit)

**Key Methods**:

- `calculate_metrics(path, grid_map, execution_time)`: Main metrics calculator
  - **Returns dict** with keys:
    - `length`: Total path distance
    - `waypoint`: Number of waypoints
    - `tuning`: Total turning angle (radians)
    - `time`: Algorithm execution time
    - `min_dis_to_obs`: Minimum distance to obstacles
    - `total`: Composite time score
    - `time_movement`: Movement time component
    - `time_decision`: Waypoint decision time
    - `time_turning`: Turning time component
    - `time_algorithm`: Algorithm execution time

- `calculate_path_length(path)`: Sums Euclidean distances between consecutive waypoints

- `calculate_path_points(path)`: Returns number of waypoints in path

- `calculate_turning_amplitude(path)`: Sums absolute angle differences at each waypoint
  - Uses angle calculation between consecutive segments
  - Handles slope edge cases (vertical/horizontal lines)

- `_calculate_angle_difference(x1, y1, x2, y2, x3, y3)`: Calculates angle between two vectors
  - Converts to slopes, then to angles
  - Normalizes angle difference to [-π, π] range
  - Returns absolute value

- `calculate_min_distance_to_obstacles(path, grid_map)`: Minimum clearance to obstacles
  - For each path segment, calculates distance to nearest obstacle
  - Subtracts obstacle radius to get actual clearance
  - Returns -1.0 if no valid calculation

- `format_metrics(metrics)`: Formats metrics as readable string list for display

---

### `comparison_runner.py` - Algorithm Comparison

**Class**: `ComparisonRunner`

**Key Methods**:

- `run_all(grid_map)`: Runs all 4 algorithms and compares results
  - Returns dict with algorithm names as keys
  - Each entry contains: algorithm, path, path_length, execution_time, metrics

- `run_one(algorithm, grid_map)`: Runs single algorithm
  - **Algorithms**: "A\*", "PSO", "APSO", "HAPSO"
  - Measures execution time
  - Calculates path metrics
  - Returns standardized result dict

---

### `chart_builder.py` - Chart Visualization

**Class**: `ChartBuilder`

**Key Methods**:

- `build_comparison_chart(results)`: Creates 2x2 subplot chart
  - Displays: Length, Turning, Time, Waypoint metrics for all algorithms
  - Uses matplotlib bar charts with different colors per algorithm
  - Returns pygame Surface for display

- `build_weight_chart(w_min, w_max, t_max)`: Visualizes inertia weight strategies
  - Compares 4 formulas: LDIW, NDIW, AIW, SIW
  - Plots weight value vs iteration
  - Shows how different strategies adjust inertia over time

---

## Optimization Module (`optimization/`)

### `path_smoother.py` - Path Optimization

**Class**: `PathSmoother`

**Key Methods**:

- `smooth(path, grid_map, remove_redundant, remove_transitive)`: Main smoother
  - Applies collinear point removal if enabled
  - Applies transitive point removal iteratively if enabled

- `_remove_collinear(path)`: Removes points on straight lines
  - Uses cross product to detect collinearity
  - Preserves start/goal
  - Logic: if cross_product ≈ 0, points are collinear

- `_remove_transitive(path, grid_map)`: Removes points that can be shortcut
  - For each point i, checks if direct line from i-1 to i+1 is collision-free
  - If yes, removes i; otherwise keeps i
  - Iterates to remove multiple redundant points

---

### `line_drawing.py` - Line Rasterization Algorithms

**Class**: `LineDrawer`

**Purpose**: Implements 4 different line drawing algorithms for grid-based rasterization

**Key Methods**:

- `bresenham(start, goal)`: Bresenham line algorithm
  - Efficient integer-based algorithm
  - Uses error accumulation to determine pixel/cell inclusion
  - Minimizes rasterization error
  - Best for performance

- `incremental(start, goal)`: Fast Voxel Traversal (Incremental traversal)
  - Uses parametric time (t) stepping
  - Calculates t_max for each axis
  - Steps through cells when t_max thresholds crossed
  - Good for true rasterization accuracy

- `parametric(start, goal)`: Supercover/Parametric line algorithm
  - Calculates all axis crossings
  - Uses floating-point midpoints to determine cell inclusion
  - Most accurate coverage of line
  - Ensures supercover property (line doesn't escape grid)

- `runs_of_runs(start, goal)`: DDA-like runs algorithm
  - Optimizes step direction based on major/minor axes
  - Uses run-length encoding for efficiency
  - Balances accuracy and performance

- `compare_all(start, goal)`: Compares all 4 algorithms, returns dict with results

---

### `inertia_weight.py` - PSO Inertia Weight Strategies

**Base Class**: `InertiaWeight(ABC)`

- Abstract base with `compute(k, t_max, **kwargs)` method

**LDIW** (Linear Decreasing Inertia Weight):

- Formula: w = w_max - (w_max - w_min) \* (k / t_max)
- Linearly decreases from w_max to w_min
- Simple, predictable convergence

**NDIW** (Non-Linear Decreasing Inertia Weight):

- Formula: w = exp(-exp((t_max - k) / t_max))
- Exponential decay, faster initially
- More aggressive convergence

**AIW** (Adaptive Inertia Weight):

- Adjusts based on fitness ratio of consecutive iterations
- Formula: w = (w*max + w_min) * fitness*ratio - w_max * (k / t_max)
- Adapts to algorithm progress
- Dynamic behavior based on performance

**SIW** (Stochastic Inertia Weight):

- Adds random perturbation to LDIW
- Formula: w = (w*max - (w_max - w_min) * (k / t*max)) * exp(rb)
- Where rb ~ Uniform(-0.1, 0.1)
- Adds exploration variability

**SOBL** (Self-Opposite Based Learning):

- Generates opposite/complementary solutions
- `opposite_scalar(x, lb, ub)`: Maps value to opposite side of bounds
- Samples r from Gaussian(mu, sigma)
- Formula: x_tilde = lb + ub - x \* r
- Encourages diversity in search

---

### `adaptive_coefficient.py` - Adaptive PSO Coefficients

**Base Class**: `AccelerationCoefficient(ABC)`

**TVAC** (Time Varying Acceleration Coefficients):

- Adapts c1 and c2 linearly over iterations
- Formula:
  - c1(iter) = (c1_final - c1_init) \* (iter / t_max) + c1_init
  - c2(iter) = (c2_final - c2_init) \* (iter / t_max) + c2_init
- Typical: c1 decreases (2.5→0.5), c2 increases (0.5→2.5)
- Behavior: Encourages exploration early, exploitation late

**FuzzyCoefficient** (Interval Type-2 Fuzzy):

- Uses IT2FIS (Interval Type-2 Fuzzy Inference System)
- Adjusts c1, c2 based on:
  - Swarm diversity (mean distance from best)
  - Iteration percentage
- Fuzzy rules balance exploration vs exploitation
- More complex adaptive behavior

---

## GUI Module (`gui/`)

### `app.py` - Main Application Window

**Class**: `App`

**Key Initialization**:

- Pygame window setup (centered, configurable fullscreen)
- Clock for FPS control (60 FPS)
- Grid map creation (30x30 cells)
- State management for 5 pages (F1-F5)

**Page States**:

- **F1 (Editor)**: Map creation and editing
- **F2 (Pathfinding)**: Algorithm selection and execution
- **F3 (Line Grid)**: Line drawing algorithm testing
- **F4 (Weight)**: Inertia weight visualization
- **F5 (Compare)**: All algorithms comparison

**Key Methods**:

- `draw_content_area()`: Delegates rendering to Renderer
- `draw_f1_menu()`: Displays F1 menu and status
- `draw_f2_menu()`: Displays F2 menu and algorithm info
- `draw_f2_metrics()`: Shows path metrics after algorithm runs
- `draw_f3_menu()`: Displays F3 line drawing menu
- `draw_f4_panel()`: Displays weight parameter input UI
- `draw_f5_results()`: Shows algorithm comparison results and chart

**Key Attributes**:

- `grid_map`: Active GridMap instance
- `current_page`: Active page (F1-F5)
- `editor_status`: Current editing mode status string
- `f2_algorithm`: Selected algorithm for pathfinding
- `f3_algorithm`: Selected line drawing algorithm
- `f4_*`: Weight visualization parameters
- `f5_results`: Comparison results cache

---

### `renderer.py` - Rendering Engine

**Class**: `Renderer`

**Purpose**: Handles all visual rendering for all 5 pages

**Key Methods**:

- `draw_content_area(app)`: Main render dispatcher
  - Draws left panel (white) with menu/info
  - Draws vertical separator
  - Draws right panel (white) with grid or content
  - Delegates to appropriate page renderer

- `draw_grid(app)`: Renders the 30x30 grid
  - Draws cells with colors based on type (obstacle/start/goal/free)
  - Draws grid lines
  - **Page-specific overlays**:
    - **F2**: Draws computed path lines in blue
    - **F2 All**: Draws all algorithm results in different colors
    - **F3**: Draws line drawing result cells and start/end markers
  - Shows axis labels

- **Page Instances**: f1_page, f2_page, f3_page, f4_page, f5_page
  - Each page has `draw(app)` method

---

### `event_handler.py` - Event Processing

**Class**: `EventHandler`

**Key Methods**:

- `handle_events(app)`: Main event loop processor
  - Handles pygame events (QUIT, KEYDOWN, MOUSEBUTTONDOWN, etc.)
  - Dispatches to page-specific handlers

**Keyboard Handlers**:

- `_handle_f1_keyboard()`: Map editor
  - `1`: Obstacle mode
  - `2`: Erase mode
  - `S`: Set Start
  - `G`: Set Goal
  - `ENTER`: Save map
  - `L`: Load map
  - `C`: Clear grid

- `_handle_f2_keyboard()`: Pathfinding
  - `1-6`: Select algorithm (A*, A* improved, PSO, PSO improved, APSO, HAPSO)
  - `A`: Run all algorithms
  - `SPACE`: Run selected algorithm
  - `ENTER`: Save result

- `_handle_f3_keyboard()`: Line drawing
  - `B`: Bresenham
  - `V`: Incremental (Voxel)
  - `D`: Runs of Runs (DDA)
  - `S`: Supercover (Parametric)
  - `SPACE`: Execute algorithm

- `_handle_f4_keyboard()`: Weight visualization
  - `I`: Input w_min
  - `A`: Input w_max
  - `T`: Input iteration count
  - `SPACE`: Refresh chart

- `_handle_f5_keyboard()`: Comparison
  - `R`: Run/refresh comparison

**Mouse Handlers**:

- `_handle_f1_mouse_event()`: Place/erase obstacles with mouse drag
- `_handle_f3_mouse_event()`: Set line start/end points with clicks

---

### `pages/f1_editor.py` - Map Editor Page

**Class**: `F1EditorPage`

**Rendering**:

- Menu with editing modes
- Info panel showing: start, goal, obstacle count

---

### `pages/f2_pathfinding.py` - Pathfinding Page

**Class**: `F2PathfindingPage`

**Rendering**:

- Menu with algorithm selection
- Info panel with selected algorithm
- Metrics panel showing path quality metrics
- All results view (if running all algorithms)

---

### `pages/f3_linegrid.py` - Line Drawing Test Page

**Class**: `F3LineGridPage`

**Rendering**:

- Menu with line algorithm selection
- Info panel showing start/end points and result cells

---

### `pages/f4_weight.py` - Inertia Weight Visualization

**Class**: `F4WeightPage`

**Rendering**:

- Input fields for w_min, w_max, iteration count
- Chart displaying 4 inertia weight strategies

---

### `pages/f5_compare.py` - Algorithm Comparison

**Class**: `F5ComparePage`

**Rendering**:

- Comparison chart (2x2: Length, Turning, Time, Waypoint)
- Results list showing total time for each algorithm

---

## Data Flow Architecture

### Pathfinding Execution Flow (F2):

```
EventHandler → App._run_simulation()
  ↓
MapValidator.validate()
  ↓
Selected Algorithm (A*/PSO/APSO/HAPSO)
  ↓
find_path(start, goal) → path
  ↓
PathMetrics.calculate_metrics()
  ↓
Result display in F2PathfindingPage
```

### Comparison Flow (F5):

```
ComparisonRunner.run_all(grid_map)
  ↓
For each algorithm: run_one()
  ↓
Collect all results
  ↓
ChartBuilder.build_comparison_chart()
  ↓
Results display + chart in F5ComparePage
```

---

## Performance Characteristics

### Algorithm Complexity:

- **A\***: O(b^d) time, O(b^d) space
- **PSO**: O(n*particles * max*iter * waypoints) time, O(n_particles \* waypoints) space
- **APSO**: O(A\* + PSO optimization)
- **HAPSO**: O(A\* + PSO optimization) with adaptive coefficients

### Grid Operations:

- Collision check: O(path_length)
- Distance calculation: O(obstacles) per segment
- Map serialization: O(grid_width \* grid_height)

---

## Key Design Patterns

1. **Strategy Pattern**: Multiple algorithms (A\*, PSO, APSO, HAPSO) with common interface
2. **Template Method**: Planner base class defines algorithm structure
3. **Factory Pattern**: MapSerializer.load/save for object creation
4. **Observer Pattern**: App updates UI based on algorithm results
5. **Decorator Pattern**: Path smoothing decorates algorithm results

---

## Configuration & Tuning

### PSO Parameters:

- `n_particles`: Population size (typically 50-200)
- `n_waypoints`: Path resolution (typically 8-20)
- `max_iter`: Convergence iterations (typically 100-500)
- `w, c1, c2`: Inertia and cognitive/social coefficients

### Algorithm Enhancement:

- `remove_redundant`: Enables collinear point removal
- `remove_transitive`: Enables transitive point removal
- `use_siw`: Stochastic inertia weight
- `use_sobl`: Self-opposite based learning

### Visualization:

- `GRID_CELL_SIZE`: Cell rendering size (20px)
- `GRID_SIZE`: Grid dimension (30x30)
- Color schemes for different cell types

---

## File Statistics

- **Total Python Files**: 38
- **Modules**: 6 (algorithms, analytics, gui, map, optimization, + root)
- **Test Files**: 4
- **Data Directories**: maps/ (5 samples), results/ (4 samples)

---

_Documentation generated on April 27, 2026_
_Project: HAPSO Draft 4 - Hybrid Adaptive Particle Swarm Optimization_
