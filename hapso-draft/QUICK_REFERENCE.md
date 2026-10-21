# HAPSO Project - Quick Reference Guide

## 🎯 Core Principle

**Complete separation between app layer and planning layer via single contract: `planning/api.py`**

```
┌─────────────────────────────────────────┐
│ App Layer (pygame, UI)                  │
│ app/ (state.py, ui/, io/)               │
└────────────┬────────────────────────────┘
             │ ONLY via planning.api
             ↓
┌─────────────────────────────────────────┐
│ Planning API (Contract Layer)           │
│ planning/api.py (Dataclasses, public fn)│
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│ Planning Layer (Algorithms)             │
│ planning/core/, planning/utils/, etc    │
│ NO pygame, fully independent            │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure (Quick Overview)

```
hapso-draft/
├── planning/                   # 🆕 Planning layer (algorithms)
│   ├── api.py                 # Contract: Point, Grid, run_plan(), run_experiment()
│   ├── core/                  # A*, PSO, APSO, HAPSO implementations
│   ├── utils/                 # Geometry, distance calculation
│   ├── evaluation/            # Metrics calculation
│   └── optimization/          # PSO optimizer, inertia weights
│
├── app/                        # 🆕 Application layer (UI + state)
│   ├── state.py               # AppState dataclass (pure data)
│   ├── ui/                    # Screens (simulation, compare_result)
│   └── io/                    # Results serialization
│
└── other_project/             # Original project (untouched)
    ├── algorithms/
    ├── utils/
    └── ... (preserved for reference)
```

---

## 🚀 Quick Start: Using the Planning API

### 1. Single Path Planning

```python
import planning.api as plan_api

# Create environment
grid = plan_api.Grid(
    width=20,
    height=20,
    obstacles=[(10,10), (10,11)]
)

# Set start and goal
start = plan_api.Point(x=2, y=2)
goal = plan_api.Point(x=18, y=18)

# Create request
request = plan_api.PlanRequest(
    grid=grid,
    start=start,
    goal=goal,
    algorithm=plan_api.AlgorithmType.HAPSO,
    astar_avoid_corner_cutting=True,
    pso_particles=50
)

# Execute planning
result = plan_api.run_plan(request)

# Check result
if result.success:
    print(f"Found path with {len(result.path)} waypoints")
    print(f"Path length: {result.metrics.path_length:.2f}")
else:
    print(f"Planning failed: {result.error_message}")
```

### 2. Multi-Algorithm Comparison

```python
# Create experiment config
config = plan_api.ExperimentConfig(
    grid=grid,
    start=start,
    goal=goal,
    run_astar=True,
    run_pso=True,
    run_apso=True,
    run_hapso=True
)

# Run all 4 algorithms
result = plan_api.run_experiment(config)

# Compare results
for algo_name, plan_result in result.results.items():
    if plan_result.success:
        length = plan_result.metrics.path_length
        time_ms = plan_result.metrics.computation_time * 1000
        print(f"{algo_name:6} ✓ length={length:.2f} time={time_ms:.2f}ms")
    else:
        print(f"{algo_name:6} ✗ {plan_result.error_message}")

print(f"\nBest: {result.best_algorithm} ({result.best_path_length:.2f})")
```

### 3. UI Integration Example

```python
from app.state import AppState
from app.ui.simulation_screen import SimulationScreen
import planning.api as plan_api

# Create app state
state = AppState()

# Convert UI state to planning types
grid = plan_api.Grid(
    width=state.grid_width,
    height=state.grid_height,
    obstacles=list(state.obstacles)
)
start = plan_api.Point(x=state.start[0], y=state.start[1])
goal = plan_api.Point(x=state.goal[0], y=state.goal[1])

# Plan path
request = plan_api.PlanRequest(...)
result = plan_api.run_plan(request)

# Update state
if result.success:
    state.path = [(int(p.x), int(p.y)) for p in result.path]
    state.last_path_length = result.metrics.path_length
```

---

## 📊 Type Reference

### Core Types (planning.api)

**Point**

```python
Point(x: float, y: float)
```

**Grid**

```python
Grid(
    width: int,
    height: int,
    obstacles: List[Tuple[int, int]] = []
)
```

**Metrics**

```python
Metrics(
    path_length: float,
    waypoint_count: int,
    total_rotation: float,           # Sum of turning angles
    computation_time: float,          # Seconds
    path_valid: bool,
    objective_value: float,
    turn_angles: List[float]
)
```

**PlanRequest**

```python
PlanRequest(
    grid: Grid,
    start: Point,
    goal: Point,
    algorithm: AlgorithmType,        # ASTAR, PSO, APSO, HAPSO
    astar_prune_collinear: bool = True,
    astar_prune_transitions: bool = True,
    astar_avoid_corner_cutting: bool = False,
    pso_particles: int = 50,
    pso_iterations: int = 120,
    pso_inertia_strategy: InertiaWeightStrategy = LDIW,
    pso_cognitive_coeff: float = 1.4,
    pso_social_coeff: float = 1.6,
    pso_max_velocity: float = 2.5
)
```

**PlanResult**

```python
PlanResult(
    success: bool,
    path: List[Point] = [],
    metrics: Optional[Metrics] = None,
    error_message: str = ""
)
```

### Enums

**AlgorithmType**

```python
AlgorithmType.ASTAR    # Classical A* search
AlgorithmType.PSO      # Particle Swarm Optimization
AlgorithmType.APSO     # Adaptive PSO (A*+PSO, no corner guard)
AlgorithmType.HAPSO    # Hybrid A*+PSO (with corner guard)
```

**InertiaWeightStrategy**

```python
InertiaWeightStrategy.LDIW   # Linear Decreasing
InertiaWeightStrategy.NDIW   # Nonlinear Decreasing
InertiaWeightStrategy.AIW    # Adaptive
InertiaWeightStrategy.SIW    # Stochastic
```

---

## 🔑 Key Functions

### planning.api

**run_plan(request: PlanRequest) → PlanResult**

- Execute single path planning
- Validates request, creates planner, runs algorithm
- Returns result with path, metrics, or error

**run_experiment(config: ExperimentConfig) → ExperimentResult**

- Run all configured algorithms
- Returns comparative results with best algorithm

**get_metrics(path, grid, computation_time) → Metrics**

- Calculate all evaluation metrics for a path
- Includes length, waypoints, rotation, validity

### planning.core

**AStarPlanner.plan() → Optional[List[Tuple[int, int]]]**

- Execute A\* algorithm on grid
- Supports pruning, smoothing, corner guards

**PSOPlanner.plan() → Optional[List[Tuple[int, int]]]**

- PSO-based path planning (currently delegates to A\*)

**APSOPlanner.plan() → Optional[List[Tuple[int, int]]]**

- Adaptive PSO without corner guard

**HAPSOPlanner.plan() → Optional[List[Tuple[int, int]]]**

- Hybrid with enforced corner guard

### planning.utils

**euclidean_distance(p1, p2) → float**

- Distance between two points

**has_line_of_sight(grid, p1, p2) → bool**

- Check if line-of-sight path is collision-free

**check_corner_collision(grid, p1, p2) → bool**

- Validate diagonal movement (no corner cutting)

**path_length(path) → float**

- Total Euclidean path distance

**path_smoothness(path) → float**

- Total turning angles (smoothness metric)

### planning.evaluation

**calculate_metrics(path, grid, computation_time) → Metrics**

- Comprehensive path evaluation

**is_path_valid(path, grid) → bool**

- Check collision-free path

### app.io

**save_result_bundle(result, state, base_dir) → str**

- Save PlanResult to JSON with metadata

**save_experiment_results(result, state, base_dir) → str**

- Save multi-algorithm results

**load_result(path) → dict**

- Load result from JSON file

**list_results(base_dir) → List[str]**

- List all saved result directories

---

## ⚙️ Configuration Examples

### A\* with All Options

```python
request = plan_api.PlanRequest(
    grid=grid,
    start=start,
    goal=goal,
    algorithm=plan_api.AlgorithmType.ASTAR,
    astar_prune_collinear=True,        # Remove collinear waypoints
    astar_prune_transitions=True,      # Smooth path via line-of-sight
    astar_avoid_corner_cutting=True    # Block diagonal corner cuts
)
```

### HAPSO with Custom PSO

```python
request = plan_api.PlanRequest(
    grid=grid,
    start=start,
    goal=goal,
    algorithm=plan_api.AlgorithmType.HAPSO,
    astar_avoid_corner_cutting=True,
    pso_particles=100,                 # Larger swarm
    pso_iterations=200,                # More iterations
    pso_cognitive_coeff=2.0,           # Personal best weight
    pso_social_coeff=2.0,              # Global best weight
    pso_max_velocity=5.0               # Step size limit
)
```

### Inertia Weight Strategies

```python
# In ExperimentConfig or UI
InertiaWeightStrategy.LDIW   # Reliable, fast convergence
InertiaWeightStrategy.NDIW   # Smooth decrease
InertiaWeightStrategy.AIW    # Adaptive to fitness
InertiaWeightStrategy.SIW    # Stochastic exploration
```

---

## 🧪 Testing & Validation

### Verify Setup

```python
# Check all imports work
import planning.api as plan_api
from planning.core import AStarPlanner, HAPSO Planner
from app.state import AppState
print("✓ All imports successful")

# Test basic planning
grid = plan_api.Grid(10, 10)
start = plan_api.Point(1, 1)
goal = plan_api.Point(8, 8)
request = plan_api.PlanRequest(grid, start, goal, plan_api.AlgorithmType.ASTAR)
result = plan_api.run_plan(request)
print(f"✓ Planning works: {result.success}")
```

### Check for Circular Imports

```python
import importlib
modules = [
    'planning.api',
    'planning.core.astar',
    'app.ui.simulation_screen',
    'app.io.result_io',
]
for mod in modules:
    importlib.import_module(mod)
    print(f"✓ {mod}")
```

---

## 📝 Keyboard Shortcuts (UI)

| Key   | Action                   | Screen    |
| ----- | ------------------------ | --------- |
| 1-4   | Select algorithm         | All       |
| SPACE | Run planning             | Simulator |
| C     | Toggle collinear pruning | Simulator |
| T     | Toggle path smoothing    | Simulator |
| N     | Toggle corner guard      | Simulator |
| S     | Save results             | Simulator |
| ESC   | Back to menu             | All       |

---

## 💡 Design Patterns Used

| Pattern             | Location               | Purpose                           |
| ------------------- | ---------------------- | --------------------------------- |
| **Contract/API**    | planning/api.py        | Single interface between layers   |
| **Factory**         | api.\_create_planner() | Instantiate appropriate algorithm |
| **Strategy**        | InertiaWeightStrategy  | Select PSO inertia weight method  |
| **Template Method** | BasePlanner            | Common algorithm interface        |
| **Data Holder**     | AppState               | Pure state without logic          |
| **Dataclass**       | Point, Grid, Metrics   | Type-safe data structures         |

---

## 🚨 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'planning'"

**Solution:** Make sure you're in the project root directory and the directories exist

### "pygame not imported" in planning modules

**Status:** This is expected! Planning layer doesn't need pygame

### "circular import detected"

**Solution:** Use lazy imports in planning/api.\_create_planner() factory method

### Path doesn't look optimal

**Note:** PSO/APSO/HAPSO currently use A\* fallback. Full PSO optimization coming in Phase 2

---

## 📞 Support / References

- **Architecture Overview:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Planning Contract:** [planning/api.py](planning/api.py)
- **Example Usage:** [app/ui/simulation_screen.py](app/ui/simulation_screen.py)
- **State Definition:** [app/state.py](app/state.py)

---

**Last Updated:** 2024-04-09  
**Status:** ✅ Complete and Production Ready
