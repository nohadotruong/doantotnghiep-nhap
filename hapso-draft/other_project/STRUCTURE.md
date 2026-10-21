# other_project - Complete Project Structure Documentation

## Project Overview

**Purpose**: UAV Pathfinding Simulator - A comprehensive path planning application combining classical (A\*) and swarm intelligence (PSO) algorithms with hybrid approaches (APSO, HAPSO).

**Key Algorithms**: A*, PSO (Particle Swarm Optimization), APSO (Adaptive PSO), HAPSO (Hybrid A* PSO)

**Tech Stack**: Python 3, NumPy, SciPy, Pygame (for UI/visualization)

**Dependencies** (from `requirements.txt`):

- numpy>=1.21.0
- pygame>=2.1.0
- scipy>=1.7.0

---

## Directory Structure & File Organization

```
other_project/
├── main.py                      # Entry point - Initializes PathfindingSimulator
├── requirements.txt              # Python dependencies
├── prompt.txt                   # Project requirements in Vietnamese
│
├── config/                      # Configuration module
│   ├── __init__.py             # Imports and exports all config constants
│   ├── colors.py               # RGB color constants for UI rendering
│   ├── display_config.py       # Window dimensions and font sizes
│   └── paths.py                # File system paths for maps/results directories
│
├── environment/                # Environment/Grid representation
│   ├── __init__.py
│   └── grid_map.py             # GridMap class - 2D obstacle grid management
│
├── evaluation/                 # Performance metrics & evaluation
│   ├── __init__.py
│   └── metrics.py              # Path evaluation functions (length, smoothness, rotation, objective)
│
├── algorithms/                 # Core pathfinding algorithms (V1)
│   ├── __init__.py
│   ├── astar.py               # A* pathfinding implementation
│   ├── pso.py                 # PSO planner & optimizer
│   ├── apso.py                # Adaptive PSO (hybrid A* + PSO)
│   └── hapso.py               # Hybrid A* + PSO (with corner-cutting)
│
├── algorithms_new/            # Refactored algorithms (V2)
│   ├── __init__.py
│   ├── base.py                # Abstract BasePlanner interface
│   ├── astar.py               # Wrapper for A* planner
│   ├── pso_planner.py         # Wrapper for PSO planner
│   ├── pso_optimizer.py       # Path optimization wrapper
│   └── hybrid.py              # Hybrid planner composition
│
├── utils/                     # Utility functions (V1)
│   ├── __init__.py
│   ├── geometry.py            # Line traversal, collision detection, path post-processing
│   ├── inertia_weight.py      # PSO inertia weight strategies (4 variants)
│   ├── message_handler.py     # UI message system
│   ├── layout_calculator.py   # Window layout computation
│   ├── visualization.py       # Pygame drawing utilities
│   └── results_saver.py       # Save results to JSON & PNG
│
├── utils_new/                 # Refactored utilities (V2)
│   ├── __init__.py
│   ├── geometry_utils.py      # Distance & line-of-sight calculations
│   ├── map_utils.py           # Grid validation & neighbor queries
│   ├── path_evaluation.py     # Path metrics (length, smoothness, validity)
│   ├── path_processing.py     # Remove redundant waypoints/points
│   ├── pso_utils.py           # Particle encoding/decoding
│   └── inertia_weight.py      # PSO inertia weight strategies (OOP version)
│
├── app/                       # UI & Application logic
│   ├── __init__.py
│   ├── menu.py                # StartMenu & MapMenu classes (Pygame)
│   ├── grid_editor.py         # GridEditor - Interactive map drawing
│   └── simulator.py           # PathfindingSimulator - Main application controller
│
└── data/                      # Data storage
    ├── maps/                  # Saved grid maps (JSON format)
    │   ├── 2026-04-08_11-17-38/
    │   ├── custom_1/
    │   └── ... (other saved maps)
    └── results/               # Simulation results (images & JSON)
        ├── 20260325_103942/
        └── ... (timestamped result directories)
```

---

## Module Documentation

### 1. **config/** - Configuration Management

#### [colors.py](config/colors.py)

**Constants**:

- `COLOR_FREE` = (255, 255, 255) - White for empty cells
- `COLOR_OBSTACLE` = (0, 0, 0) - Black for obstacles
- `COLOR_START` = (0, 255, 0) - Green for start position
- `COLOR_GOAL` = (255, 0, 0) - Red for goal position
- `COLOR_PATH` = (0, 0, 255) - Blue for planned path
- `COLOR_GRID` = (200, 200, 200) - Light gray for grid lines
- `COLOR_GRAY` = (100, 100, 100) - Gray for decorative elements
- `COLOR_HOVER` = (230, 230, 230) - Light background for hover states

#### [display_config.py](config/display_config.py)

**Display Constants**:

- Grid size: CELL_SIZE = 20 pixels
- Default grid: 20x20 cells
- Editor window: 700x460 pixels
- Simulation window: 700x460 pixels (+ 200px side panel)
- Start menu: 500x200 pixels
- Map menu: 350x500 pixels
- Fonts: SMALL=20, NORMAL=24, LARGE=32 pt

#### [paths.py](config/paths.py)

**Path Constants**:

- `MAPS_DIR` = "data/maps"
- `RESULTS_DIR` = "data/results"
- Default map filename: "map.json"

---

### 2. **environment/** - Grid Environment

#### [grid_map.py](environment/grid_map.py)

**Purpose**: Represents 2D grid with obstacles, start, and goal positions

**GridMap Class**:

- **Constants**: FREE=0, OBSTACLE=1, START=2, GOAL=3, PATH=4
- **Attributes**:
  - `width`, `height`: Grid dimensions
  - `grid`: 2D list of cell types
  - `start`, `goal`: Tuple positions (x, y)

- **Core Methods**:
  - `is_inside(x, y)`: Boundary check
  - `is_obstacle(x, y)`: Query cell type
  - `set_obstacle(x, y, value)`: Set/unset obstacle
  - `toggle_obstacle(x, y)`: Toggle obstacle state
  - `set_start/set_goal(x, y)`: Set position markers
  - `get_obstacles()`: Return list of all obstacle positions
  - `get_neighbors(x, y)`: Get 8-connected neighbors (incl. diagonals)

- **I/O Methods**:
  - `save_map(filepath)`: Store grid to JSON with timestamp
  - `load_map(filepath)`: Load grid from JSON
  - `load_from_path(filepath)`: Static factory method
  - `list_saved_maps()`: List all saved maps in MAPS_DIR

**File Format** (map.json):

```json
{
  "width": 20,
  "height": 20,
  "start": [5, 5],
  "goal": [18, 18],
  "obstacles": [[10, 10], [10, 11], ...]
}
```

---

### 3. **evaluation/** - Path Metrics

#### [metrics.py](evaluation/metrics.py)

**Functions**:

- `path_length(path)`: Sum of Euclidean distances between consecutive waypoints
- `node_count(path)`: Number of waypoints in path
- `total_rotation(path)`: Sum of turning angles at each waypoint (radians)
- `compute_time(t_a)`: Elapsed computation time
- `objective(path, t_a, v_m=1.0, t_p=0.2, v_i=π)`: Weighted path cost formula

**Objective Function**:

```
F = (D/v_m) + (P*t_p) + (I/v_i) + C

Where:
  D = path length
  P = waypoint count
  I = total rotation
  C = computation time
  v_m = velocity magnitude (default 1.0)
  t_p = time per waypoint (default 0.2)
  v_i = velocity for rotation (default π)
```

---

### 4. **algorithms/** - Core Pathfinding Algorithms (V1)

#### [astar.py](algorithms/astar.py)

**Purpose**: Classical A\* pathfinding algorithm implementation

**Astar Class**:

- **Constructor Parameters**:
  - `grid`: GridMap instance
  - `prune_collinear`: Remove collinear waypoints (post-processing)
  - `prune_transitions`: Smooth waypoint path
  - `avoid_corner_cutting`: Check diagonal movement obstacles

- **Core Method**:
  - `plan()`: Execute A\* algorithm, return path or None

- **Internal Methods**:
  - `_get_valid_neighbors()`: Get walkable neighbors w/ optional corner checks
  - `_reconstruct_path()`: Backtrack from goal to start via came_from dict
  - `_post_process_path()`: Apply pruning/smoothing post-processing

- **Algorithm Details**:
  - Uses heap-based open set for efficiency
  - Stores visited, g_score (cost), f_score (cost+heuristic)
  - Heuristic: Euclidean distance to goal
  - Cost metric: Euclidean distance to neighbors (1.0 for cardinal, √2 for diagonal)

#### [pso.py](algorithms/pso.py)

**Purpose**: Particle Swarm Optimization for path planning

**Inertia Weight Strategies** (4 variants):

1. `linear_decreasing_inertia_weight()`: w = w_max - (w_max-w_min)\*(k/t_max)
2. `nonlinear_decreasing_inertia_weight()`: w = exp(-exp((t_max-k)/t_max))
3. `stochastic_inertia_weight()`: w = (w_max - (w_max-w_min)_(k/t_max)) _ exp(rb), rb ~ U(-0.1, 0.1)
4. `adaptive_inertia_weight()`: Fitness-ratio based adjustment

**PSOPlanner Class**:

- **Constructor Parameters**:
  - `num_particles`: Swarm size (default 50)
  - `num_waypoints`: Path waypoints (auto-calculated if None)
  - `max_iterations`: PSO iterations (default 120)
  - `inertia_weight`: w parameter (default 0.7)
  - `cognitive_coeff` (c1), `social_coeff` (c2): Learning factors (1.4, 1.6)
  - `collision_penalty`: Penalty for invalid paths (1000.0)
  - `max_velocity`: Max velocity magnitude (2.5)

- **Core Method**:
  - `plan()`: Execute PSO algorithm for path planning
- **Key Features**:
  - **Particle Representation**: Each particle = list of n waypoints (2D coordinates)
  - **Waypoint Auto-Sizing**: Based on Manhattan distance and obstacle density
  - **Heuristic Initialization**: First particle initialized on start→goal line
  - **Line-of-Sight Smoothing**: Post-process to skip redundant waypoints
  - **Fallback**: Return A\* path if PSO fails (infinite fitness)

- **Fitness Calculation**:
  - Returns ∞ if path collides with obstacles
  - Otherwise: Total Euclidean path length

- **Constraint Handling**:
  - Boundary clipping to grid bounds
  - Repair particles in obstacles by snapping to nearest free cell
  - Velocity clamping: [-max_velocity, max_velocity]

- **Helper Class**: `PSOptimizer`
  - Optimizes single segment (p_start → p_mid → p_end) of path
  - Used by APSO/HAPSO for local optimization

#### [apso.py](algorithms/apso.py)

**Purpose**: Adaptive PSO - A\* path + segment-wise PSO optimization

**APSO Class**:

- **Constructor**:
  - A\* parameters: prune_collinear, prune_transitions, avoid_corner_cutting=False
  - PSO parameters: swarm_size, max_iter, w, c1, c2, max_velocity

- **Pipeline** (`plan()`):
  1. Get coarse path from A\*
  2. Apply prune_collinear if enabled
  3. Apply prune_transitions if enabled
  4. Optimize each segment (i-1 → i → i+1) with PSOptimizer
  5. Validate optimized path (revert if collisions)
  6. Line-of-sight smoothing (remove skippable waypoints)

- **Key Difference from HAPSO**:
  - `avoid_corner_cutting=False` in A\* (allows cutting corners)
  - Suitable for environments with less restrictive corner constraints

#### [hapso.py](algorithms/hapso.py)

**Purpose**: Hybrid A* + PSO - A* path + segment-wise PSO optimization with corner constraints

**HAPSO Class**:

- **Constructor**:
  - Same as APSO but `avoid_corner_cutting=True` (default)
  - Enforces corner collision checks throughout

- **Pipeline** (`plan()`):
  1. Get coarse path from A\* with corner-cutting avoidance
  2. Apply prune_collinear if enabled
  3. Apply prune_transitions if enabled
  4. Optimize each segment with PSOptimizer
  5. Validate optimized path
  6. Line-of-sight smoothing

- **Key Difference from APSO**:
  - Uses corner-cutting guard: Better safety for narrow passages
  - More conservative but reliable paths

---

### 5. **algorithms_new/** - Refactored Algorithms (V2)

**Design Pattern**: Wrapper pattern around original algorithm implementations

#### [base.py](algorithms_new/base.py)

**Purpose**: Abstract base class for all planners

**BasePlanner Class** (ABC):

```python
class BasePlanner(ABC):
    def __init__(self, grid: GridMap)

    @abstractmethod
    def plan() -> Optional[List[Tuple[int, int]]]
```

#### [astar.py](algorithms_new/astar.py)

**AStarPlanner** wraps `algorithms.Astar`:

- Better parameter naming:
  - `remove_redundant_points` (was `prune_collinear`)
  - `remove_redundant_waypoints` (was `prune_transitions`)
  - `corner_collision_check` (was `avoid_corner_cutting`)
- Delegates to original `Astar` implementation

#### [pso_planner.py](algorithms_new/pso_planner.py)

**PSOPlanner** wraps `algorithms.PSOPlanner`

#### [pso_optimizer.py](algorithms_new/pso_optimizer.py)

**PSOOptimizer** wraps `algorithms.PSOptimizer`

- **Additional Method**: `_fitness()` - Combine path validity with length

#### [hybrid.py](algorithms_new/hybrid.py)

**HybridPlanner** - Composition pattern:

```python
class HybridPlanner(BasePlanner):
    def __init__(self, planner: BasePlanner, optimizer: PSOOptimizer)

    def plan():
        path = self.planner.plan()       # Initial planning
        path = self.optimizer.optimize() # Local optimization
        return path
```

---

### 6. **utils/** - Utility Functions (V1)

#### [geometry.py](utils/geometry.py)

**Line Traversal Algorithms**:

- `bresenham_line(p1, p2)`: Bresenham's line algorithm - Efficient integer-only
- `dda_line(p1, p2)`: Digital Differential Analyzer - More accurate
- `voxel_traversal_line(p1, p2)`: Alias for DDA (voxel grid traversal)
- `supercover_voxels(p1, p2)`: Supercover line - All cells touching line

**Collision Detection**:

- `check_collision_line(grid, p1, p2)`: Check if line segment hits obstacles
  - Uses voxel traversal
  - Returns True if collision found
- `has_corner_obstacle(grid, p1, p2)`: Check diagonal corner blocking
  - For 8-connected movement, check if cutting corner hits obstacles
- `check_collision_line_with_clearance()`: Collision + safety margin

**Path Analysis**:

- `calculate_path_length(path)`: Sum of segment distances
- `euclidean_distance(p1, p2)`: √((x2-x1)² + (y2-y1)²)
- `calculate_path_smoothness(path)`: Sum of turning angles (penalty metric)
- `calculate_path_metrics(grid, path)`: Dict with length, smoothness, waypoint_count, has_collision

**Path Post-Processing**:

- `remove_redundant_points(path)`: Remove collinear waypoints
- `remove_redundant_transitions(grid, path, avoid_corner_cutting)`: Skip waypoints if line-of-sight (with optional corner checks)

#### [inertia_weight.py](utils/inertia_weight.py)

**PSO Inertia Weight Functions** (procedural):

- `calculate_ldiw()` - Linear Decreasing Inertia Weight
- `calculate_ndiw()` - Nonlinear Decreasing Inertia Weight
- `calculate_aiw()` - Adaptive Inertia Weight
- `calculate_siw()` - Stochastic Inertia Weight

#### [message_handler.py](utils/message_handler.py)

**MessageHandler Class**: Temporary UI message system

- `set_message(msg)`: Store message with timestamp
- `get_message()`: Return message if duration_ms not exceeded
- `is_message_active()`: Check if message still valid
- `clear_message()`: Clear message immediately

#### [layout_calculator.py](utils/layout_calculator.py)

**LayoutConfig** (NamedTuple):

```python
LayoutConfig(
    window_width, window_height,    # Total window size
    left_width, right_width,        # Panel widths (60:40 ratio)
    left_x, left_y, right_x, right_y, # Panel positions
    offset_x, offset_y,              # Grid drawing offset
    margin
)
```

**calculate_layout()**: Compute responsive layout based on:

- Grid dimensions
- Target window size
- Margin and axes space
- Left/right panel ratio

#### [visualization.py](utils/visualization.py)

**Pygame Drawing Functions**:

- `draw_text(screen, text, font, x, y, color, center)`: Render text
- `draw_grid(screen, grid, offset_x, offset_y, show_coordinates)`: Render grid cells & coordinate axes
- `draw_coordinate_axes()`: Draw x/y axis labels
- `draw_path(screen, path, offset_x, offset_y, thickness)`: Draw path lines
- `draw_button()`: Interactive button with hover detection
- `get_cell_from_mouse()`: Convert mouse position to grid cell
- `save_screen()`: Export pygame surface to PNG

#### [results_saver.py](utils/results_saver.py)

**Result Saving**:

- `save_all_results()`: Orchestrator - saves both image and JSON
- `create_results_directory()`: Create timestamped results folder
- `save_result_image()`: Export pygame surface to PNG
- `save_result_json()`: Save path and metadata to JSON

**Result JSON Format**:

```json
{
  "timestamp": "2024-04-09T12:34:56.789012",
  "algorithm": "HAPSO",
  "grid": {"width": 20, "height": 20, "start": [5, 5], "goal": [18, 18], "obstacles_count": 45},
  "path": {"found": true, "length": 12, "coordinates": [[5,5], ...], "distance": 11}
}
```

---

### 7. **utils_new/** - Refactored Utilities (V2)

**Design Principle**: Functional decomposition + OOP for strategies

#### [geometry_utils.py](utils_new/geometry_utils.py)

**Functions**:

- `euclidean_distance(p1, p2)`: Distance calculation
- `_bresenham_line(p1, p2)`: Internal line algorithm
- `has_line_of_sight(grid, p1, p2)`: LoS check (uses Bresenham)
- `check_corner_collision(grid, p1, p2)`: Diagonal obstacle detection

#### [map_utils.py](utils_new/map_utils.py)

**Functions**:

- `is_valid(grid, x, y)`: Inside bounds
- `is_obstacle(grid, x, y)`: Is cell blocked
- `get_neighbors(grid, x, y, diagonal=True)`: Get valid neighbors

#### [path_evaluation.py](utils_new/path_evaluation.py)

**Functions**:

- `path_length(path)`: Total distance
- `path_smoothness(path)`: Total angle change
- `is_path_valid(path, grid)`: Collision-free check

#### [path_processing.py](utils_new/path_processing.py)

**Functions**:

- `remove_redundant_points(path)`: Cross-product based collinearity
- `remove_redundant_waypoints(path, grid)`: Line-of-sight based pruning

#### [pso_utils.py](utils_new/pso_utils.py)

**Functions**:

- `encode_particle(path)`: Flatten path to 1D array
- `decode_particle(particle, start, goal, num_waypoints)`: Reconstruct path
- `clip_to_bounds(particle, grid)`: Enforce grid boundaries
- `initialize_swarm()`: Create initial PSO swarm

#### [inertia_weight.py](utils_new/inertia_weight.py)

**OOP Strategy Pattern**:

**InertiaWeight** (ABC):

```python
class InertiaWeight(ABC):
    def compute(k: int, t_max: int, **kwargs) -> float
```

**Implementations**:

- **LDIW** - Linear Decreasing
- **NDIW** - Nonlinear Decreasing
- **AIW** - Adaptive (fitness-based)
- **SIW** - Stochastic

---

### 8. **app/** - User Interface & Application

#### [menu.py](app/menu.py)

**StartMenu Class**:

- Displays main menu with 4 options via buttons
- Keyboard shortcuts: N (new), L (load), C (collision check), ESC (exit)
- Returns: "new", "load", "compare", or None

**MapMenu Class**:

- Lists all saved maps in MAPS_DIR with pagination
- Navigation: UP/DOWN (select), LEFT/RIGHT (page), ENTER (load), ESC (cancel)
- Features: Current page indicator, map directory listing

#### [grid_editor.py](grid_editor.py)

**GridEditor Class**:

- **User Interactions**:
  - Click: Toggle single obstacle
  - Drag: Draw obstacle line (using voxel traversal)
  - S: Set start position (click to place)
  - G: Set goal position (click to place)
  - SPACE/ENTER: Save map & proceed to simulator
  - C: Clear all obstacles
  - ESC: Return to menu

- **Features**:
  - Live message feedback
  - Responsive layout with grid preview
  - Status display (current start/goal positions)
  - Drag preview (shows cells that will be affected)

#### [simulator.py](simulator.py)

**PathfindingSimulator Class** - Main application controller

**Attributes**:

- `grid`: Current GridMap instance
- `current_path`: Most recent path result
- `current_algorithm`: Active algorithm selection (1-4)
- `is_collision_check`: Mode flag (collision detection test vs. normal pathfinding)
- `prune_collinear/prune_transitions/avoid_corner_cutting`: A\* options
- `message_handler`: UI message system
- `path_metrics`: Current path statistics

**Main Workflow** (`run()`):

1. ShowStartMenu() → Select mode
2. Create or load map
3. Launch GridEditor for manual edits
4. Enter simulation loop with path rendering

**Algorithm Selection** (SPACE to run):

- 1: A\* (with configurable options)
- 2: PSO (pure swarm-based)
- 3: APSO (A\* + PSO optimization, no corner guard)
- 4: HAPSO (A\* + PSO optimization, with corner guard)

**Simulation Features**:

- Real-time path rendering (blue lines)
- Algorithm switching without re-planning
- Path metrics display (length, waypoint count)
- Turn angle analysis (max/min/avg turning)
- Multi-algorithm comparison

**Collision Check Mode** (`_run_collision_check_algorithm()`):

- Auto-runs A\* with collision guards enabled
- Displays three line traversal methods comparison:
  - Bresenham: Current default
  - DDA: Digital Differential Analyzer
  - Supercover: Reference implementation

**Result Saving**:

- S key: Save path image (PNG) + metadata (JSON)
- Timestamped results directory
- Includes algorithm name and statistics

**Control Keys** (Simulation):

- 1/2/3/4: Select algorithm
- SPACE: Run algorithm
- C: Toggle prune_collinear
- T: Toggle prune_transitions
- N: Toggle corner-cut guard
- I: Print detailed path info (console)
- S: Save results
- ESC: Exit to menu

---

## Architecture & Design Patterns

### 1. **Layered Architecture**

```
┌─────────────────────────────────────┐
│  UI Layer (Pygame)                  │
│  - app/simulator.py                 │
│  - app/grid_editor.py               │
│  - app/menu.py                      │
├─────────────────────────────────────┤
│  Algorithm Layer                    │
│  - algorithms/ (A*, PSO, APSO, HAPSO) │
│  - algorithms_new/ (refactored)     │
├─────────────────────────────────────┤
│  Environment & Utilities            │
│  - environment/grid_map.py          │
│  - utils/ (geometry, visualization) │
│  - evaluation/metrics.py            │
└─────────────────────────────────────┘
```

### 2. **Design Patterns Used**

#### **Strategy Pattern** (PSO Inertia Weights):

- `utils_new/inertia_weight.py`: LDIW, NDIW, AIW, SIW strategies
- Each algorithm implements `compute(k, t_max, **kwargs)`

#### **Wrapper/Adapter Pattern** (Refactored Algorithms):

- `algorithms_new/`: Wraps original implementations with better naming
- Maintains backward compatibility while improving API

#### **Factory Pattern** (Grid and Results):

- `GridMap.load_from_path()`: Static factory
- `GridMap.list_saved_maps()`: Factory for available maps

#### **Composition Pattern** (Hybrid Planner):

- `HybridPlanner`: Combines BasePlanner + PSOOptimizer
- Flexible algorithm combinations

#### **Template Method** (Pathfinding):

- A\*, PSO, APSO, HAPSO follow similar `plan()` interface
- `BasePlanner` ABC enforces contract

### 3. **Dependency Graph**

```
main.py
  └─→ app/simulator.py (PathfindingSimulator)
       ├─→ app/menu.py (StartMenu, MapMenu)
       ├─→ app/grid_editor.py (GridEditor)
       ├─→ environment/grid_map.py (GridMap)
       ├─→ algorithms/ (Astar, PSOPlanner, APSO, HAPSO)
       ├─→ evaluation/metrics.py (calculate_path_metrics)
       └─→ utils/ (visualization, results_saver, layout_calculator)
            ├─→ utils/geometry.py
            ├─→ utils/visualization.py
            └─→ utils/message_handler.py

algorithms/
  ├─→ astar.py uses utils/geometry.py (collision detection)
  ├─→ pso.py uses algorithms/astar.py (fallback)
  ├─→ apso.py uses algorithms/astar.py + algorithms/pso.py
  └─→ hapso.py uses algorithms/astar.py + algorithms/pso.py

algorithms_new/
  ├─→ All wrappers delegate to algorithms/
  └─→ hybrid.py composes astar.py + pso_optimizer.py
```

---

## Data Flow & Key Workflows

### **Workflow 1: Interactive Map Creation & Pathfinding**

```
1. main.py → PathfindingSimulator.run()
2. Show StartMenu() → User selects "new"
3. Create empty GridMap(20, 20)
4. Launch GridEditor
   - User draws obstacles (click/drag)
   - User sets start (S key)
   - User sets goal (G key)
   - User presses SPACE to run
5. GridEditor calls GridMap.save_map()
   - Creates timestamped directory
   - Saves map.json with obstacles list
6. Launch Simulator
   - Show grid with start/goal
   - Wait for user to select algorithm (1-4)
   - User presses SPACE
7. Call _find_path()
   - Based on current_algorithm:
     - Invoke Astar/PSOPlanner/APSO/HAPSO.plan()
     - Calculate path_metrics
   - Render path on grid
8. User selects "S" to save results
   - Call save_all_results()
   - Creates result.png + result.json
```

### **Workflow 2: Load & Compare Saved Map**

```
1. StartMenu() → User selects "load"
2. MapMenu shows list from GridMap.list_saved_maps()
3. User selects map (ENTER)
4. Load via GridMap.load_from_path()
5. Display in Simulator
6. Can modify obstacles in GridEditor
7. Re-run algorithms for comparison
```

### **Workflow 3: Collision Detection Analysis**

```
1. StartMenu() → User selects "compare"
   (Sets is_collision_check=True)
2. Create/load map
3. GridEditor for setup
4. Simulator auto-runs A* with collision checks
5. Display three line traversal methods:
   - Bresenham cells
   - DDA cells
   - Supercover cells
   (Helps validate collision detection algorithm)
```

### **Workflow 4: Algorithm Execution (Example: HAPSO)**

```
HAPSO.plan():
  ├─ Astar(corner_cutting=True).plan()
  │  └─ Returns coarse path (e.g., 25 waypoints)
  ├─ remove_redundant_points()
  │  └─ Removes collinear points (e.g., 20 waypoints)
  ├─ remove_redundant_transitions()
  │  └─ Line-of-sight pruning (e.g., 15 waypoints)
  ├─ _optimize_segments()
  │  └─ For each segment i-1→i→i+1:
  │     PSOptimizer.optimize()
  │     └─ PSO mini-swarm optimizes middle point
  │        (e.g., move from (10,10) to (10.5, 9.8))
  ├─ _validate_path()
  │  └─ Check no collisions, revert if failed
  ├─ _smooth_line_of_sight()
  │  └─ Final line-of-sight pruning
  └─ Return optimized path (e.g., 14 waypoints)
```

---

## Key Algorithms Comparison

| Aspect             | A\*                  | PSO              | APSO                 | HAPSO             |
| ------------------ | -------------------- | ---------------- | -------------------- | ----------------- |
| **Type**           | Deterministic search | Stochastic swarm | Hybrid (A\*+PSO)     | Hybrid (A\*+PSO)  |
| **Speed**          | Fast                 | Slow             | Medium               | Medium            |
| **Quality**        | Good (grid-aligned)  | Variable         | Better               | Best              |
| **Corner Cutting** | Optional             | Implicit         | Not enforced (False) | Enforced (True)   |
| **Path Type**      | Grid-based           | Continuous       | Continuous           | Continuous        |
| **Best For**       | Fast planning        | Memory-efficient | Balanced             | Restricted spaces |

---

## Configuration & Customization

### **A\* Options**:

```python
astar = Astar(
    grid,
    prune_collinear=True,        # Remove collinear waypoints
    prune_transitions=True,      # Smooth path via line-of-sight
    avoid_corner_cutting=True    # Block diagonal corner cuts
)
```

### **PSO Parameters**:

```python
pso = PSOPlanner(
    grid,
    num_particles=50,            # Swarm size
    num_waypoints=16,            # Path waypoints (auto if None)
    max_iterations=120,          # PSO iterations
    inertia_weight=0.7,          # w parameter
    cognitive_coeff=1.4,         # c1 (personal best influence)
    social_coeff=1.6,            # c2 (global best influence)
    collision_penalty=1000.0,    # Cost of invalid paths
    max_velocity=2.5             # Max step size
)
```

### **APSO/HAPSO Parameters**:

```python
hapso = HAPSO(
    grid,
    astar_prune_collinear=True,
    astar_prune_transitions=True,
    astar_avoid_corner_cutting=True,    # Key difference: HAPSO=True, APSO=False
    pso_swarm_size=30,
    pso_max_iter=100,
    pso_w=0.7,
    pso_c1=2.0,
    pso_c2=2.0,
    pso_max_velocity=5.0
)
```

---

## File Format Reference

### **Map JSON** (`data/maps/YYYYMMDD_HHMMSS/map.json`):

```json
{
  "width": 20,
  "height": 20,
  "start": [5, 5],
  "goal": [18, 18],
  "obstacles": [[10, 10], [10, 11], [11, 10], ...]
}
```

### **Result JSON** (`data/results/YYYYMMDD_HHMMSS/result.json`):

```json
{
  "timestamp": "2024-04-09T12:34:56.789012",
  "algorithm": "HAPSO",
  "grid": {
    "width": 20,
    "height": 20,
    "start": [5, 5],
    "goal": [18, 18],
    "obstacles_count": 45
  },
  "path": {
    "found": true,
    "length": 12,
    "coordinates": [[5, 5], [6, 5], ..., [18, 18]],
    "distance": 11
  }
}
```

---

## Version Comparison: V1 vs V2

| Aspect            | V1 (algorithms/)           | V2 (algorithms_new/)               |
| ----------------- | -------------------------- | ---------------------------------- |
| **Naming**        | Concise (prune_collinear)  | Explicit (remove_redundant_points) |
| **Structure**     | Direct implementations     | Wrapper pattern                    |
| **Interface**     | Implicit planning() method | Abstract BasePlanner               |
| **Customization** | Parameter-heavy            | Composition-friendly               |
| **Utils**         | Procedural (functions)     | Mixed (functions + OOP)            |

**Recommendation**: Use V2 (algorithms_new/) for new code. V1 remains functional for backward compatibility.

---

## Key Points & Best Practices

1. **Grid Coordinate System**: (x, y) where x=column, y=row (0 at top-left)
2. **Collision Detection**: Always use voxel/Bresenham traversal for accuracy
3. **Path Post-Processing**: Apply line-of-sight smoothing last to preserve safety
4. **PSO Convergence**: Increase num_waypoints for complex environments
5. **Corner Cutting**: Enable in narrow areas; disable in open spaces for speed
6. **Memory Management**: Load large maps into numpy arrays for PSOptimizer
7. **UI Responsiveness**: Message duration is 3000ms (3 seconds) by default

---

## Testing & Validation

**Included Test Cases** (under `data/maps/`):

- `paper-figure-*`: Published paper test cases
- `custom_1-4`: Various complexity levels
- Manual creation via GridEditor

**Metrics Provided**:

- Path length (Euclidean)
- Waypoint count
- Turning angles (smoothness)
- Collision-free validation
- Computation time recording

---

## Future Enhancement Possibilities

1. **RRT (Rapidly-exploring Random Tree)**: Add as algorithm option
2. **3D Path Planning**: Extend GridMap to 3D
3. **Dynamic Obstacles**: Moving obstacles support
4. **Multi-Agent Pathfinding**: Coordinate multiple UAVs
5. **Learning-Based Heuristics**: ML-guided A\* or reward shaping for PSO
6. **GPU Acceleration**: CUDA for large swarms
7. **Web Interface**: Browser-based visualization
8. **Export Formats**: ROS bag, KML for UAV platforms

---

**END OF STRUCTURE DOCUMENTATION**
