# HAPSO Path Planning Studio - Codebase Overview

## Project Summary

HAPSO (Hybrid A* Particle Swarm Optimizer) is a path planning application that combines multiple algorithms (A*, PSO, APSO, HAPSO) to find optimal paths on grid-based maps. The application features a comprehensive UI built with Pygame allowing users to edit maps, run simulations, and compare algorithm performance.

**Technology Stack:**

- Python 3.9+
- Pygame (UI/graphics)
- NumPy (numerical computing)
- SciPy (scientific computing)
- Matplotlib (visualization/charting)

---

## Directory Structure

```
hapso-draft/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── app_io/                    # I/O layer for applications
├── evaluation/                # Path evaluation metrics
├── io/                        # Alternative I/O layer (legacy)
├── utils/                     # Utility functions
├── ui/                        # User interface screens
├── planners/                  # Path planning algorithms
├── data/                      # Map and result storage
└── other_project/             # Separate related project
```

---

# DETAILED FILE DOCUMENTATION

## Entry Point

### [main.py](main.py)

**Purpose:** Application bootstrap and main event loop using Pygame.

**Key Classes:**

- `AppState` (dataclass)
  - Manages global application state including window dimensions, grid size, and map data
  - Properties: `window_width`, `window_height`, `grid_width`, `grid_height`, `cell_size`, `grid`, `start`, `goal`, `path`
- `App` (main application controller)
  - Initializes Pygame and manages screen switching between 4 main UI screens
  - Handles keyboard shortcuts for screen navigation (F1-F4)
  - Maintains 60 FPS game loop

**Key Functions:**

- `create_empty_grid(width: int, height: int) -> list[list[int]]` - Creates a blank grid

**Screens Managed:**

- `editor` - MapEditorScreen (F1)
- `sim` - SimulationScreen (F2)
- `weight` - CompareWeightScreen (F3)
- `result` - CompareResultScreen (F4)

---

## I/O Layer (app_io/)

### [app_io/**init**.py](app_io/__init__.py)

- Module docstring declaring map and experiment I/O helpers

### [app_io/map_io.py](app_io/map_io.py)

**Purpose:** Save/load grid maps in JSON and PNG formats, manage map directories.

**Key Functions:**

- `save_map_json(path, grid, start, goal)` - Saves map as JSON with start/goal positions
- `load_map_json(path) -> tuple[Grid, Point | None, Point | None]` - Loads map from JSON
- `save_map_png(path, grid, cell_size=20)` - Renders and saves map as PNG image
- `save_map_bundle(grid, start, goal, cell_size=20, base_dir) -> Path` - Saves complete map package (JSON + PNG) with timestamp
- `list_saved_maps(base_dir) -> list[Path]` - Lists all saved maps sorted by recency
- `load_map_from_dir(map_dir) -> tuple[Grid, Point | None, Point | None]` - Loads map from directory

---

### [app_io/result_io.py](app_io/result_io.py)

**Purpose:** Save and visualize path planning results.

**Key Functions:**

- `_render_result_surface(grid, path, start, goal, cell_size) -> pygame.Surface` - Renders path visualization with obstacles, path, start/goal points
- `save_result_bundle(grid, path, start, goal, algorithm, metrics, settings, cell_size=20, base_dir) -> Path` - Saves complete result package including:
  - Algorithm name
  - Start/goal positions and full path
  - Performance metrics (length, smoothness, node count, objective value)
  - Settings used
  - Rendered visualization (PNG)
  - Timestamp-based directory

---

### [app_io/experiment_runner.py](app_io/experiment_runner.py)

**Purpose:** Execute multi-algorithm experiments and compare performance.

**Key Classes:**

- `ExperimentResult` (dataclass)
  - Fields: `name`, `length`, `smoothness`, `nodes`, `objective_value`
  - Stores metrics from a single algorithm run

**Key Functions:**

- `build_default_algorithms(config: dict | None) -> dict[str, object]` - Creates algorithm instances:
  - **A\***: Standard A\* pathfinder with 8-directional movement
  - **PSO**: Pure Particle Swarm Optimization planner
  - **APSO**: A\* planner + PSO optimizer
  - **HAPSO**: Enhanced A\* (with corner collision check) + PSO optimizer

  Configuration parameters:
  - `planner_particles` (default: 30)
  - `planner_iterations` (default: 60)
  - `planner_waypoints` (default: 6)
  - `optimizer_particles` (default: 24)
  - `optimizer_iterations` (default: 40)

- `run_experiments(grid, start, goal, config) -> list[ExperimentResult]` - Runs all algorithms and collects metrics

---

## Evaluation Module (evaluation/)

### [evaluation/metrics.py](evaluation/metrics.py)

**Purpose:** Path quality evaluation and validation functions.

**Key Functions:**

- `path_length(path: list[Point]) -> float` - Calculates total Euclidean distance
- `node_count(path: list[Point]) -> int` - Returns number of waypoints
- `total_rotation(path: list[Point]) -> float` - Calculates accumulated direction changes in radians using dot product
- `path_smoothness(path: list[Point]) -> float` - Alias for `total_rotation()`
- `is_path_valid(path: list[Point], grid: Grid) -> bool` - Validates that:
  - No waypoints are in obstacles
  - Line-of-sight exists between consecutive waypoints
- `objective(path, grid, alpha=0.7, beta=0.3) -> float` - Combined fitness function:
  - Formula: `alpha * path_length + beta * path_smoothness + invalid_penalty`
  - Adds large penalty (1e6) if path is invalid
  - Default weights favor length (70%) over smoothness (30%)

---

## Utility Modules (utils/)

### [utils/grid_utils.py](utils/grid_utils.py)

**Purpose:** Type definitions and grid navigation utilities.

**Type Aliases:**

- `Grid = list[list[int]]` - 2D grid where 0 = free, 1 = obstacle
- `Point = tuple[int, int]` - Grid coordinates (x, y)

**Key Functions:**

- `is_valid(x, y, grid) -> bool` - Checks if coordinates are within bounds
- `is_obstacle(x, y, grid) -> bool` - Returns True if cell is blocked or out of bounds
- `get_neighbors(x, y, grid, diagonal=True, avoid_corner_cutting=False, check_corner_collision=None) -> Iterable[Point]` - Yields valid neighboring cells:
  - 4-connected (cardinal) or 8-connected (with diagonals)
  - Optional corner collision checking for diagonal moves
  - Integrates with geometry module for collision detection

---

### [utils/geometry.py](utils/geometry.py)

**Purpose:** Geometric calculations and line-of-sight detection.

**Key Functions:**

- `euclidean_distance(p1, p2) -> float` - Calculates Euclidean distance
- `_bresenham_cells(p1, p2) -> list[Point]` - Rasterizes line between two points using DDA algorithm
  - More robust than Bresenham for diagonal collision detection
  - Handles horizontal, vertical, diagonal, and general cases
- `has_line_of_sight(p1, p2, grid, avoid_corner_cutting=False) -> bool` - Checks if straight line path is obstacle-free:
  - Uses DDA rasterization
  - Optional diagonal corner clipping detection
- `check_corner_collision(p1, p2, grid) -> bool` - Detects corner clipping on diagonal moves:
  - When moving diagonally, checks both adjacent corner cells
  - Returns True if either corner is blocked (diagonal move is blocked)
  - Prevents artificial path shortcuts through corner gaps

---

### [utils/path_utils.py](utils/path_utils.py)

**Purpose:** Particle-path encoding/decoding for PSO algorithms.

**Type Definition:**

- `Particle = np.ndarray` - Flat array of waypoint coordinates

**Key Functions:**

- `encode_particle(path: list[Point], n_waypoints: int) -> Particle` - Converts path to flat representation:
  - Extracts internal waypoints (excluding start/goal)
  - Pads or truncates to exact `n_waypoints`
  - Returns flattened 1D array of coordinates
- `decode_particle(particle, start, goal, grid) -> list[Point]` - Reconstructs path from particle:
  - Reshapes flat array to waypoint pairs
  - Rounds and clips coordinates to valid grid bounds
  - Adds start and goal endpoints
- `clip_to_bounds(particle, grid) -> Particle` - Constrains particle values to grid dimensions
- `initialize_swarm(n_particles, n_waypoints, grid, seed_path=None) -> list[Particle]` - Creates initial PSO population:
  - If `seed_path` provided: population initialized around seed with Gaussian noise
  - Otherwise: random uniform initialization across grid
  - All particles clipped to valid bounds

---

## User Interface (ui/)

### [ui/common.py](ui/common.py)

**Purpose:** Shared UI components and styling.

**Constants:**

- `FONT_SMALL`, `FONT_NORMAL`, `FONT_LARGE` = 24 (all same for consistency)
- `PALETTE` - Centralized color scheme:
  - `bg` (white), `panel` (white), `ink` (black)
  - `start` (green), `goal` (red), `path` (blue)
  - `obstacle` (black), `grid` (gray)

**Key Classes:**

- `Button` - Clickable UI button with rounded corners and text
  - Properties: `rect`, `text`, `key_hint`
  - Methods: `draw(surface, font)`
- `TextInput` - Text input field with active state
  - Properties: `rect`, `label`, `text`, `active`
  - Methods: `handle_event(event)`, `draw(surface, font)`, `get_int(fallback)`, `get_float(fallback)`
  - Accepts only numeric input (0-9, ., -)

**Key Functions:**

- `draw_title(surface, title, subtitle, start_y=60)` - Renders large title and subtitle text

---

### [ui/map_editor_screen.py](ui/map_editor_screen.py)

**Purpose:** Grid editing interface for creating/modifying maps.

**Key Class:**

- `MapEditorScreen`
  - Modes: "Obstacle", "Erase", "Start", "Goal"
  - Layout: 3-4-3 ratio (left panel for controls, center for grid, right for info)
  - Controls (accessed via keyboard or buttons):
    - `1` - Obstacle mode (draw obstacles)
    - `2` - Erase mode (remove obstacles)
    - `S` - Set start position
    - `G` - Set goal position
    - `C` - Clear entire map
    - `M` - Save map to disk
    - `L` - Load previously saved map
  - Features:
    - Drag-to-draw lines of obstacles
    - Load menu with pagination (5 maps per page)
    - Real-time status messages

**Key Methods:**

- `handle_event(event)` - Process mouse/keyboard input
- `draw(surface)` - Render editor UI and map grid
- `_to_grid(mouse_pos)` - Convert screen pixels to grid coordinates
- `_paint_line(start_cell, end_cell)` - Draw line of obstacles
- `_clear_map()` - Reset grid to blank
- `_open_load_menu()` / `_handle_load_menu_event()` - Map loading UI

---

### [ui/simulation_screen.py](ui/simulation_screen.py)

**Purpose:** Algorithm execution and visualization interface.

**Key Class:**

- `SimulationScreen`
  - Algorithm selection: A\*, PSO, APSO, HAPSO
  - Layout: 3-4-3 ratio
  - Controls:
    - `A` - Select A\* algorithm
    - `P` - Select PSO
    - `O` - Select APSO
    - `H` - Select HAPSO
    - `SPACE` - Run selected algorithm
    - `K` - Save result
    - `1` - Toggle redundant point removal (A\* post-processing)
    - `2` - Toggle redundant waypoint removal (A\* path pruning)
    - `3` - Toggle diagonal corner cutting avoidance
  - Features:
    - Real-time path visualization
    - Path metrics display (length, nodes, rotation, objective)
    - Algorithm-specific settings display
    - Coordinate system visualization

**Key Methods:**

- `_run_planner()` - Execute selected algorithm
- `_save_result()` - Export path and metrics
- `_draw_path()` - Render path visualization
- `_draw_path_info()` - Display calculated metrics

---

### [ui/compare_result_screen.py](ui/compare_result_screen.py)

**Purpose:** Multi-algorithm benchmarking and comparison.

**Key Class:**

- `CompareResultScreen`
  - Runs all algorithms (A\*, PSO, APSO, HAPSO) simultaneously
  - Generates comparative bar charts
  - Layout: 3-7 ratio (left panel for controls, right for charts)

**Chart Display:**

1. Path length (lower is better)
2. Node count (lower is better)
3. Total rotation/smoothness (lower is better)
4. Objective value (lower is better)
5. Aggregate score (weighted average of all metrics)

**Key Methods:**

- `_run_and_draw()` - Execute experiments and generate charts
- Data sanitization: Replaces infinite values with capped estimates
- Normalization: Scales all metrics to [0, 1] range for fair comparison

---

### [ui/compare_weight_screen.py](ui/compare_weight_screen.py)

**Purpose:** Visualize and compare PSO inertia weight strategies.

**Key Class:**

- `CompareWeightScreen`
  - Compares 4 inertia weight formulas: LDIW, NDIW, AIW, SIW
  - Configurable parameters:
    - Iterations: Number of PSO iterations to simulate
    - w_min: Minimum inertia weight (default 0.4)
    - w_max: Maximum inertia weight (default 0.9)
  - Control: `R` - Recompute and display weight schedules

**Key Methods:**

- `_build_chart()` - Generate line chart showing weight evolution

---

## Path Planning Algorithms (planners/)

### [planners/base.py](planners/base.py)

**Purpose:** Abstract base class for all planners.

**Key Class:**

- `BasePlanner` (ABC)
  - Abstract method: `plan(grid, start, goal) -> list[Point]`
  - Implemented by: AStarPlanner, PSOPlanner, HybridPlanner

---

### [planners/astar.py](planners/astar.py)

**Purpose:** A\* pathfinding algorithm with optional post-processing optimizations.

**Key Class:**

- `AStarPlanner(BasePlanner)`
  - Options:
    - `remove_redundant_points`: Eliminate collinear waypoints
    - `remove_redundant_waypoints`: Visibility-graph path pruning
    - `corner_collision_check`: Diagonal move validation
  - Algorithm:
    - Uses heap-based open set (priority queue by f-cost)
    - Heuristic: Euclidean distance to goal
    - 8-directional movement (including diagonals)

**Key Methods:**

- `plan()` - Main A\* algorithm
- `_reconstruct()` - Backtrace from goal to start
- `_post_process(path, grid)` - Apply optimization passes
- `remove_redundant_points()` - Prune collinear waypoints using cross product test
- `remove_redundant_waypoints()` - Visibility pruning (connect non-adjacent waypoints if line-of-sight exists)

---

### [planners/pso_planner.py](planners/pso_planner.py)

**Purpose:** Pure PSO-based path planning.

**Key Class:**

- `PSOPlanner(BasePlanner)`
  - Parameters:
    - `n_particles`: Swarm size (default: 30)
    - `n_iterations`: PSO iterations (default: 60)
    - `n_waypoints`: Number of internal waypoints (default: 6)
    - `c1`, `c2`: Cognitive/social coefficients (default: 1.6 each)
    - `inertia`: InertiaWeight strategy (default: SIW)
  - Algorithm:
    - Encodes paths as particle coordinates
    - Iterative velocity and position updates
    - Tracks personal best (pbest) and global best (gbest)
    - Inertia weight adaptation enables exploration→exploitation transition

**Key Methods:**

- `plan()` - Execute PSO algorithm
- `_fitness()` - Objective function evaluation

---

### [planners/pso_optimizer.py](planners/pso_optimizer.py)

**Purpose:** PSO-based path refinement optimizer.

**Key Class:**

- `PSOOptimizer`
  - Parameters:
    - `n_particles`: Swarm size (default: 24)
    - `n_iterations`: PSO iterations (default: 40)
    - `c1`, `c2`: Coefficients (default: 1.5, 1.7)
  - Initialization:
    - Encodes input path as seed particle
    - Replaces worst particle in initial swarm with seed
    - Ensures optimizer improves rather than abandons initial solution

**Key Methods:**

- `optimize(path, grid)` - Refine provided path
- `_fitness()` - Objective with different alpha/beta weights (75/25 vs planner's 85/15)

---

### [planners/hybrid.py](planners/hybrid.py)

**Purpose:** Composition wrapper for planner + optimizer combinations.

**Key Class:**

- `HybridPlanner(BasePlanner)`
  - Combines two-stage planning:
    1. First stage: Generate initial path using planner
    2. Second stage: Refine path using optimizer

**Supported Combinations:**

- **PSO** = PSOPlanner + PSOOptimizer
- **APSO** = AStarPlanner + PSOOptimizer (A\* planning, PSO refinement)
- **HAPSO** = AStarPlanner(corner_check=True) + PSOOptimizer (Enhanced A\* with PSO refinement)

---

### [planners/inertia_weight.py](planners/inertia_weight.py)

**Purpose:** Inertia weight strategies for PSO convergence control.

**Key Classes:**

- `InertiaWeight` (ABC)
  - Abstract: `compute(k, t_max, **kwargs) -> float`
  - Parameters: `w_min` (default 0.4), `w_max` (default 0.9)

- `LDIW` - Linear Decreasing Inertia Weight
  - Formula: `w_max - (w_max - w_min) * (k / t_max)`
  - Simple linear decay from w_max to w_min
- `NDIW` - Nonlinear Decreasing Inertia Weight
  - Formula: `exp(-exp((t_max - k) / t_max))`
  - Exponential decay with accelerated convergence at end
- `AIW` - Adaptive Inertia Weight
  - Formula: `(w_max + w_min) * (pk_gbest / pk1_gbest) - w_max * (k / t_max)`
  - Adapts based on fitness improvement ratio
  - Less improvement → more exploitation
- `SIW` - Stochastic Inertia Weight
  - Formula: `w_max - (w_max - w_min) * (k / t_max) * exp(random_noise)`
  - Introduces randomness for exploration flexibility

---

## Legacy I/O Module (io/) - Duplicate Implementation

**Note:** This directory contains duplicated versions of `map_io.py` and `experiment_runner.py` from the `app_io/` directory. The versions differ slightly:

- `io/map_io.py`: Simpler version without PNG export
- `io/experiment_runner.py`: Simpler version with fixed algorithm configurations

**Status:** Appears to be legacy code; recommend using `app_io/` versions instead.

---

## Data Organization

### Saved Maps

Location: `data/maps/{timestamp}/`
Files:

- `map.json` - Grid data, start/goal positions
- `map.png` - Visual representation

### Saved Results

Location: `data/results/{timestamp}/`
Files:

- `result.json` - Complete result data (algorithm, path, metrics)
- `result.png` - Path visualization

### Pre-built Test Maps

Location: `data/maps/` includes:

- `paper-figure-*` - Maps from research papers
- `custom-*` - User-created test cases
- Timestamped maps from experiments

---

## Data Types and Constants

### Type Aliases (from utils/grid_utils.py)

```python
Grid = list[list[int]]      # 2D list where 0=free, 1=obstacle
Point = tuple[int, int]     # (x, y) coordinates
```

### Color Palette (from ui/common.py)

```python
PALETTE = {
    "bg": (255, 255, 255),           # White background
    "obstacle": (0, 0, 0),           # Black obstacles
    "start": (39, 163, 108),         # Green start
    "goal": (216, 73, 60),           # Red goal
    "path": (53, 112, 201),          # Blue path
    "grid": (185, 185, 185),         # Gray grid lines
}
```

### Grid Representation

- Value `0`: Free/walkable cell
- Value `1`: Obstacle/blocked cell
- Coordinate system: (x, y) where x is column, y is row

---

## Algorithm Comparison Summary

| Algorithm | Type            | Key Features                     | Use Case                           |
| --------- | --------------- | -------------------------------- | ---------------------------------- |
| **A\***   | Deterministic   | Fast, exhaustive, optimal        | Baseline, fine-grained control     |
| **PSO**   | Evolutionary    | Global search, natural obstacles | Exploration, waypoint optimization |
| **APSO**  | Hybrid          | A\* init + PSO refinement        | Balance speed and quality          |
| **HAPSO** | Hybrid Enhanced | A\* with corner check + PSO      | Best quality with safety checks    |

---

## Dependencies

From `requirements.txt`:

- `numpy>=1.21.0` - Numerical arrays and operations
- `pygame>=2.1.0` - Graphics and user interface
- `scipy>=1.7.0` - Scientific computing utilities
- `matplotlib>=3.5.0` - Chart generation and visualization

---

## Key Design Patterns

### 1. **Strategy Pattern**

- `BasePlanner` ABC with multiple implementations (A\*, PSO, Hybrid)
- `InertiaWeight` ABC with multiple weight strategies (LDIW, NDIW, AIW, SIW)
- Allows easy algorithm swapping at runtime

### 2. **Decorator/Wrapper Pattern**

- `HybridPlanner` wraps planner + optimizer
- Single interface (`plan()`) for complex compositions

### 3. **Factory Pattern**

- `build_default_algorithms()` creates algorithm instances with predefined configs
- Centralizes configuration management

### 4. **Data Container Pattern**

- Type aliases (`Grid`, `Point`) for semantic clarity
- Dataclasses (`AppState`, `ExperimentResult`) for structured data

### 5. **State Management Pattern**

- `AppState` holds global application state
- Update flow: Event → Handler → State → Render

---

## Workflow: Path Planning Execution

1. **User starts on MapEditorScreen (F1)**
   - Creates/loads grid map
   - Sets start and goal positions
   - Saves map to `data/maps/{timestamp}/`

2. **User switches to SimulationScreen (F2)**
   - Selects algorithm (A\*, PSO, APSO, or HAPSO)
   - Configures options (post-processing, corner checks)
   - Presses SPACE to execute planning
   - Path displayed with metrics

3. **Optional: Compare Results (F4)**
   - All algorithms run on same map
   - Metrics calculated and normalized
   - Bar charts compare performance

4. **Optional: Compare Weights (F3)**
   - Visualize PSO inertia weight evolution
   - Test different w_min/w_max parameters

---

## Known Issues & Improvements

### Current Limitations

1. **Duplicate code** in `io/` directory (legacy)
2. **Grid limited to small sizes** (testing with ~20x20 maps)
3. **No parameter tuning UI** for PSO hyperparameters
4. **No animation** during algorithm execution
5. **Limited error handling** for invalid map configurations

### Potential Enhancements

1. Remove legacy `io/` module and consolidate to `app_io/`
2. Add real-time algorithm visualization/animation
3. Implement configuration profiles for different scenario types
4. Add path export (DXF, SVG formats)
5. Multi-threading for algorithm execution
6. Batch experiment runner with statistical analysis

---

## Module Dependency Graph

```
main.py
├── ui/ (all screens)
│   ├── common.py (UI components)
│   ├── map_editor_screen.py
│   │   └── app_io/map_io.py
│   ├── simulation_screen.py
│   │   ├── app_io/result_io.py
│   │   ├── evaluation/metrics.py
│   │   └── planners/*
│   ├── compare_result_screen.py
│   │   ├── app_io/experiment_runner.py
│   │   └── evaluation/metrics.py
│   └── compare_weight_screen.py
│       └── planners/inertia_weight.py
│
├── planners/
│   ├── base.py (abstract base)
│   ├── astar.py
│   ├── pso_planner.py
│   ├── pso_optimizer.py
│   ├── hybrid.py
│   └── inertia_weight.py
│
├── utils/
│   ├── grid_utils.py (types & grid utilities)
│   ├── geometry.py (line-of-sight & collision)
│   └── path_utils.py (particle encoding/decoding)
│
├── evaluation/
│   └── metrics.py (path quality evaluation)
│
└── app_io/
    ├── map_io.py
    ├── result_io.py
    └── experiment_runner.py
```

---

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py

# Keyboard shortcuts
F1  - Map Editor
F2  - Simulation
F3  - Weight Compare
F4  - Result Compare
ESC - Exit
```

---

_Last Updated: April 9, 2026_
_Documentation Version: 1.0_
